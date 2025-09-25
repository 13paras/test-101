from typing_extensions import TypedDict
from openai import AzureOpenAI
import openai
from dotenv import load_dotenv
import os
from typing import Literal
from langgraph.graph import StateGraph, START, END
from langgraph.graph.message import add_messages
import time
from pydantic import BaseModel
import neatlogs  # ✅ imported and initialized only — no usage below
import random

load_dotenv()

# ✅ Initialize neatlogs (as required) — but we won't use it anywhere else
neatlogs.init(api_key=os.getenv('NEATLOGS_API_KEY'))

# Azure OpenAI setup
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

# Enhanced Pydantic models with comprehensive validation
from pydantic import Field, field_validator, ConfigDict
from typing import Optional, List, Literal
from datetime import datetime
from uuid import UUID, uuid4

class DetectCallResponse(BaseModel):
    """Enhanced response model for AI question detection"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    is_question_ai: bool = Field(..., description="Whether the query is AI/coding related")
    confidence_score: Optional[float] = Field(
        None, 
        ge=0.0, 
        le=1.0, 
        description="Confidence score for the classification"
    )
    detected_categories: List[str] = Field(
        default_factory=list,
        description="Categories detected in the query"
    )
    processing_time_ms: Optional[float] = Field(
        None,
        ge=0,
        description="Time taken to process the request in milliseconds"
    )
    
    @field_validator('detected_categories')
    @classmethod
    def validate_categories(cls, v: List[str]) -> List[str]:
        allowed_categories = [
            'programming', 'data_science', 'web_development', 
            'machine_learning', 'general_question', 'technical_support'
        ]
        return [cat for cat in v if cat in allowed_categories]


class AiResponse(BaseModel):
    """Enhanced AI response model with metadata"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='forbid'
    )
    
    ai_message: str = Field(..., min_length=1, max_length=5000, description="The AI response message")
    response_id: UUID = Field(default_factory=uuid4, description="Unique response identifier")
    model_used: str = Field(default="gpt-4o-mini", description="AI model used for generation")
    response_type: Literal["answer", "clarification", "error", "code_example"] = Field(
        default="answer",
        description="Type of response provided"
    )
    tokens_used: Optional[int] = Field(None, ge=0, description="Number of tokens used")
    generated_at: datetime = Field(default_factory=datetime.now, description="Timestamp when response was generated")
    has_code: bool = Field(default=False, description="Whether response contains code")
    programming_languages: List[str] = Field(
        default_factory=list,
        description="Programming languages mentioned or used in response"
    )
    
    @field_validator('ai_message')
    @classmethod
    def validate_message_content(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('AI message cannot be empty or just whitespace')
        return v.strip()
    
    @field_validator('programming_languages')
    @classmethod
    def validate_languages(cls, v: List[str]) -> List[str]:
        common_languages = [
            'python', 'javascript', 'typescript', 'java', 'c++', 'c#', 'go', 
            'rust', 'php', 'ruby', 'swift', 'kotlin', 'scala', 'r', 'sql',
            'html', 'css', 'bash', 'powershell'
        ]
        return [lang.lower() for lang in v if lang.lower() in common_languages]

# Enhanced State using Pydantic for better validation
class State(BaseModel):
    """Enhanced state model for the graph workflow"""
    model_config = ConfigDict(
        str_strip_whitespace=True,
        validate_assignment=True,
        extra='allow'  # Allow additional fields for flexibility
    )
    
    user_message: str = Field(..., min_length=1, max_length=10000, description="User's input message")
    ai_message: str = Field(default="", description="AI's response message")
    is_coding_question: bool = Field(default=False, description="Whether the question is coding-related")
    session_id: UUID = Field(default_factory=uuid4, description="Session identifier")
    conversation_history: List[Dict[str, str]] = Field(
        default_factory=list,
        description="History of the conversation"
    )
    processing_metadata: Dict[str, Any] = Field(
        default_factory=dict,
        description="Metadata about processing steps"
    )
    error_count: int = Field(default=0, ge=0, description="Number of errors encountered")
    
    @field_validator('user_message')
    @classmethod
    def validate_user_message(cls, v: str) -> str:
        if not v.strip():
            raise ValueError('User message cannot be empty')
        return v.strip()
    
    def add_to_history(self, role: str, message: str) -> None:
        """Add a message to conversation history"""
        self.conversation_history.append({
            'role': role,
            'message': message,
            'timestamp': datetime.now().isoformat()
        })
    
    def increment_error_count(self) -> None:
        """Increment error counter"""
        self.error_count += 1

# 🎯 Global counter to trigger error after 2 successful runs
CALL_COUNTER = 0
MAX_SUCCESSFUL_CALLS = 2

# Node: Detect if query is coding-related
def detect_query(state_dict: Dict[str, Any]) -> Dict[str, Any]:
    global CALL_COUNTER
    CALL_COUNTER += 1
    
    # Convert to Pydantic State for validation and easy access
    state = State(**state_dict)
    
    start_time = time.time()
    user_message = state.user_message
    SYSTEM_PROMPT = """Your task is to determine whether the user's query is a coding-related question.
    Respond with confidence score and detected categories."""

    try:
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=DetectCallResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        
        parsed_response = result.choices[0].message.parsed
        state.is_coding_question = parsed_response.is_question_ai
        
        # Add processing metadata
        processing_time = (time.time() - start_time) * 1000
        state.processing_metadata.update({
            "detect_query": {
                "confidence_score": parsed_response.confidence_score,
                "detected_categories": parsed_response.detected_categories,
                "processing_time_ms": processing_time,
                "model_used": "gpt-4o-mini"
            }
        })
        
        # Add to conversation history
        state.add_to_history("system", f"Classified as {'coding' if state.is_coding_question else 'general'} question")
        
    except Exception as e:
        state.increment_error_count()
        raise Exception(f"Error in detect_query: {str(e)}")

    return state.model_dump()

# Edge router
def route_edge(state_dict: Dict[str, Any]) -> Literal["solve_coding_question", "solve_simple_question"]:
    state = State(**state_dict)
    if state.is_coding_question:
        return "solve_coding_question"
    else:
        return "solve_simple_question"

# Node: Solve coding question — will force error after MAX_SUCCESSFUL_CALLS
def solve_coding_question(state_dict: Dict[str, Any]) -> Dict[str, Any]:
    state = State(**state_dict)
    user_message = state.user_message

    # 🚨 FORCE ERROR after MAX_SUCCESSFUL_CALLS
    if CALL_COUNTER > MAX_SUCCESSFUL_CALLS:
        raise Exception(f"🚨 Simulated crash after {MAX_SUCCESSFUL_CALLS} successful runs!")

    start_time = time.time()
    SYSTEM_PROMPT = """Your task is to solve the coding question of the user. 
    Provide comprehensive examples with Pydantic and similar Python libraries when relevant."""
    
    try:
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=AiResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        
        parsed_response = result.choices[0].message.parsed
        state.ai_message = parsed_response.ai_message
        
        # Add processing metadata
        processing_time = (time.time() - start_time) * 1000
        state.processing_metadata.update({
            "solve_coding_question": {
                "response_id": str(parsed_response.response_id),
                "model_used": parsed_response.model_used,
                "response_type": parsed_response.response_type,
                "has_code": parsed_response.has_code,
                "programming_languages": parsed_response.programming_languages,
                "processing_time_ms": processing_time,
                "tokens_used": parsed_response.tokens_used
            }
        })
        
        # Add to conversation history
        state.add_to_history("assistant", state.ai_message)
        
    except Exception as e:
        state.increment_error_count()
        raise Exception(f"Error in solve_coding_question: {str(e)}")

    return state.model_dump()

# Node: Solve simple question
def solve_simple_question(state_dict: Dict[str, Any]) -> Dict[str, Any]:
    state = State(**state_dict)
    user_message = state.user_message
    
    start_time = time.time()
    SYSTEM_PROMPT = """Your task is to solve the simple question of the user. 
    If the question involves data validation or modeling, mention Pydantic and similar Python libraries as appropriate."""

    try:
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=AiResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        
        parsed_response = result.choices[0].message.parsed
        state.ai_message = parsed_response.ai_message
        
        # Add processing metadata
        processing_time = (time.time() - start_time) * 1000
        state.processing_metadata.update({
            "solve_simple_question": {
                "response_id": str(parsed_response.response_id),
                "model_used": parsed_response.model_used,
                "response_type": parsed_response.response_type,
                "processing_time_ms": processing_time,
                "tokens_used": parsed_response.tokens_used
            }
        })
        
        # Add to conversation history
        state.add_to_history("assistant", state.ai_message)
        
    except Exception as e:
        state.increment_error_count()
        raise Exception(f"Error in solve_simple_question: {str(e)}")

    return state.model_dump()

# Build graph with Pydantic State
from typing import Dict, Any

def create_state_dict(state: State) -> Dict[str, Any]:
    """Convert Pydantic State to dict for LangGraph"""
    return state.model_dump()

def update_state_from_dict(state_dict: Dict[str, Any]) -> State:
    """Create State from dict"""
    return State(**state_dict)

graph_builder = StateGraph(Dict[str, Any])
graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_question", solve_simple_question)

graph_builder.add_edge(START, "detect_query")
graph_builder.add_conditional_edges("detect_query", route_edge)
graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_simple_question", END)

graph = graph_builder.compile()

# Function to run graph with error handling
def call_graph():
    # Create initial state using Pydantic model
    initial_state = State(
        user_message="Explain me about Pydantic in Python with comprehensive examples including validation, serialization, and advanced features"
    )
    
    state_dict = initial_state.model_dump()

    try:
        print("🚀 Running graph...")
        print(f"📝 Query: {initial_state.user_message}")
        print(f"🆔 Session ID: {initial_state.session_id}")
        
        result = graph.invoke(state_dict)
        
        # Convert result back to Pydantic State for easy access
        final_state = State(**result)
        
        print("✅ Success!")
        print(f"📊 Processing metadata: {final_state.processing_metadata}")
        print(f"💬 AI Response: {final_state.ai_message[:200]}...")
        print(f"📈 Conversation history: {len(final_state.conversation_history)} messages")
        print(f"❌ Error count: {final_state.error_count}")
        
    except Exception as e:
        print("❌ ERROR CAUGHT:", str(e))  # <-- Pure Python print, no neatlogs

# Run multiple times
if __name__ == "__main__":
    for i in range(5):
        print(f"\n{'='*40}")
        print(f"        RUN #{i+1}")
        print('='*40)
        call_graph()
        time.sleep(2)