from typing_extensions import TypedDict
from openai import AzureOpenAI
import openai
from dotenv import load_dotenv
import os
from typing import Literal, Optional, Dict, Any
from langgraph.graph import StateGraph, START, END
import time
from pydantic import BaseModel
import neatlogs
import random
import logging
from dataclasses import dataclass

load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ✅ Initialize neatlogs (as required) — but we won't use it anywhere else
neatlogs.init(api_key=os.getenv('NEATLOGS_API_KEY'))

# Azure OpenAI setup with error handling
def create_azure_client():
    """Create Azure OpenAI client with proper error handling"""
    try:
        return AzureOpenAI(
            api_key=os.getenv("AZURE_OPENAI_API_KEY"),
            api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
            azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
            azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
        )
    except Exception as e:
        logger.error(f"Failed to create Azure OpenAI client: {e}")
        return None

client = create_azure_client()

# Enhanced Pydantic models with better context
class DetectCallResponse(BaseModel):
    is_question_ai: bool
    confidence_score: Optional[float] = None
    reasoning: Optional[str] = None

class AiResponse(BaseModel):
    ai_message: str
    response_type: Optional[str] = None
    confidence: Optional[float] = None
    
class ErrorResponse(BaseModel):
    error_message: str
    error_type: str
    suggestions: Optional[list[str]] = None
    fallback_response: Optional[str] = None

# Enhanced State with error handling fields
class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool
    error_context: Optional[Dict[str, Any]]
    retry_count: Optional[int]
    response_metadata: Optional[Dict[str, Any]]

# Enhanced error handling class
@dataclass
class ErrorHandler:
    max_retries: int = 3
    fallback_enabled: bool = True
    
    def handle_api_error(self, error: Exception, context: str) -> ErrorResponse:
        """Enhanced error handling with contextual responses"""
        error_type = type(error).__name__
        
        if "Connection" in str(error) or "ConnectionError" in error_type:
            return ErrorResponse(
                error_message="Unable to connect to AI service",
                error_type="ConnectionError",
                suggestions=[
                    "Check your internet connection",
                    "Verify API credentials are correct",
                    "Try again in a few moments"
                ],
                fallback_response=self._get_fallback_response(context)
            )
        elif "Authentication" in str(error) or "401" in str(error):
            return ErrorResponse(
                error_message="Authentication failed",
                error_type="AuthenticationError", 
                suggestions=[
                    "Check your API key is valid",
                    "Verify API permissions",
                    "Contact administrator for access"
                ],
                fallback_response=self._get_fallback_response(context)
            )
        else:
            return ErrorResponse(
                error_message=f"Unexpected error in {context}",
                error_type=error_type,
                suggestions=["Try rephrasing your question", "Contact support if the issue persists"],
                fallback_response=self._get_fallback_response(context)
            )
    
    def _get_fallback_response(self, context: str) -> str:
        """Provide contextual fallback responses"""
        if "pydantic" in context.lower():
            return self._get_pydantic_fallback()
        elif "coding" in context.lower():
            return "I'm currently unable to provide detailed coding assistance, but I recommend checking the official documentation for your programming language or framework."
        else:
            return "I'm currently experiencing technical difficulties. Please try your question again or rephrase it differently."
    
    def _get_pydantic_fallback(self) -> str:
        """Rich fallback response for Pydantic questions"""
        return """
# Pydantic Overview

Pydantic is a Python library that provides data validation and settings management using Python type annotations.

## Key Features:
- **Data Validation**: Automatic validation of data types
- **Type Safety**: Leverages Python type hints
- **JSON Schema**: Auto-generation of JSON schemas
- **Performance**: Fast validation using Rust under the hood

## Basic Example:
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str

# Usage
user = User(name="John", age=30, email="john@example.com")
print(user.name)  # John
```

## Common Use Cases:
1. **API Development**: Validate request/response data
2. **Configuration Management**: Type-safe settings
3. **Data Processing**: Clean and validate incoming data
4. **ORM Integration**: Work with databases safely

## Best Practices:
- Use descriptive field names
- Add validation constraints where needed
- Leverage Field() for complex validation
- Use validators for custom logic
- Handle validation errors gracefully

For more detailed information, visit: https://docs.pydantic.dev/
"""

# Global error handler instance
error_handler = ErrorHandler()

# Enhanced counter system with better tracking
class CallTracker:
    def __init__(self):
        self.call_count = 0
        self.max_calls_before_simulated_error = 2
        self.enable_simulated_errors = False  # Set to False to disable intentional crashes
        
    def increment(self):
        self.call_count += 1
        
    def should_simulate_error(self) -> bool:
        return (self.enable_simulated_errors and 
                self.call_count > self.max_calls_before_simulated_error)
        
    def reset(self):
        self.call_count = 0

call_tracker = CallTracker()

# Enhanced node functions with robust error handling

def detect_query(state: State):
    """Enhanced detect_query with comprehensive error handling"""
    global call_tracker
    call_tracker.increment()
    
    user_message = state.get("user_message", "")
    state["retry_count"] = state.get("retry_count", 0)
    
    # Enhanced system prompt for better classification
    SYSTEM_PROMPT = """
    Analyze the user's query and determine if it's a coding-related question.
    
    Consider these as coding-related:
    - Programming concepts, languages, frameworks
    - Code debugging, optimization, or review
    - Software development practices
    - API usage, libraries, or tools
    - Data structures, algorithms
    - Technical implementation questions
    
    Provide your reasoning and confidence level.
    """
    
    try:
        if not client:
            raise Exception("Azure OpenAI client not initialized")
            
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=DetectCallResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        
        parsed_result = result.choices[0].message.parsed
        state["is_coding_question"] = parsed_result.is_question_ai
        state["response_metadata"] = {
            "confidence": parsed_result.confidence_score,
            "reasoning": parsed_result.reasoning
        }
        
    except Exception as e:
        logger.error(f"Error in detect_query: {e}")
        error_response = error_handler.handle_api_error(e, "query detection")
        
        # Fallback logic - assume coding question if contains programming keywords
        coding_keywords = ["python", "pydantic", "code", "function", "class", "import", "error", "debug"]
        is_coding = any(keyword in user_message.lower() for keyword in coding_keywords)
        
        state["is_coding_question"] = is_coding
        state["error_context"] = {
            "error_message": error_response.error_message,
            "error_type": error_response.error_type,
            "suggestions": error_response.suggestions,
            "fallback_used": True
        }
    
    return state

def solve_coding_question(state: State):
    """Enhanced coding question solver with rich context"""
    user_message = state.get("user_message", "")
    
    # Check for simulated error (disabled by default)
    if call_tracker.should_simulate_error():
        logger.warning("Simulated error triggered - but continuing with fallback")
        # Instead of crashing, use fallback
        state["ai_message"] = error_handler._get_fallback_response("coding " + user_message)
        return state
    
    # Enhanced system prompt with rich context, especially for Pydantic
    SYSTEM_PROMPT = """
    You are an expert programming assistant with deep knowledge across multiple domains.
    
    **For Pydantic questions, provide comprehensive context including:**
    1. Clear explanation of concepts
    2. Working code examples with comments
    3. Common patterns and best practices  
    4. Error handling approaches
    5. Performance considerations
    6. Integration examples (FastAPI, SQLAlchemy, etc.)
    7. Migration guides for version differences
    8. Troubleshooting common issues
    
    **For general coding questions:**
    - Provide complete, runnable examples
    - Explain the reasoning behind solutions
    - Mention alternative approaches
    - Include error handling where relevant
    - Suggest testing strategies
    
    **Always consider:**
    - Code readability and maintainability
    - Security implications
    - Performance impact
    - Compatibility with different versions
    - Real-world usage scenarios
    
    Be thorough but concise. Use markdown formatting for better readability.
    """
    
    try:
        if not client:
            raise Exception("Azure OpenAI client not initialized")
            
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=AiResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        
        parsed_result = result.choices[0].message.parsed
        state["ai_message"] = parsed_result.ai_message
        state["response_metadata"] = {
            "response_type": parsed_result.response_type,
            "confidence": parsed_result.confidence
        }
        
    except Exception as e:
        logger.error(f"Error in solve_coding_question: {e}")
        error_response = error_handler.handle_api_error(e, "coding " + user_message)
        
        if error_response.fallback_response:
            state["ai_message"] = error_response.fallback_response
        else:
            state["ai_message"] = "I apologize, but I'm currently unable to process your coding question. Please try again later."
            
        state["error_context"] = {
            "error_message": error_response.error_message,
            "error_type": error_response.error_type,
            "suggestions": error_response.suggestions
        }
    
    return state

def solve_simple_question(state: State):
    """Enhanced simple question solver"""
    user_message = state.get("user_message", "")
    
    # Enhanced system prompt for non-coding questions
    SYSTEM_PROMPT = """
    You are a helpful assistant providing clear, informative responses to general questions.
    
    **Guidelines:**
    - Provide accurate, well-structured information
    - Use examples where helpful
    - Be concise but comprehensive
    - If the question touches on technical topics, provide appropriate context
    - Include relevant resources or next steps when applicable
    
    Format your response clearly with proper structure and markdown when helpful.
    """
    
    try:
        if not client:
            raise Exception("Azure OpenAI client not initialized")
            
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=AiResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        
        parsed_result = result.choices[0].message.parsed
        state["ai_message"] = parsed_result.ai_message
        
    except Exception as e:
        logger.error(f"Error in solve_simple_question: {e}")
        error_response = error_handler.handle_api_error(e, "simple question")
        
        state["ai_message"] = (error_response.fallback_response or 
                             "I apologize, but I'm currently unable to process your question. Please try again later.")
        state["error_context"] = {
            "error_message": error_response.error_message,
            "error_type": error_response.error_type,
            "suggestions": error_response.suggestions
        }
    
    return state

# Enhanced edge router (same as before but included for completeness)
def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"]:
    is_coding_question = state.get("is_coding_question")
    if is_coding_question:
        return "solve_coding_question"
    else:
        return "solve_simple_question"

# Build enhanced graph
graph_builder = StateGraph(State)
graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_question", solve_simple_question)

graph_builder.add_edge(START, "detect_query")
graph_builder.add_conditional_edges("detect_query", route_edge)
graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_simple_question", END)

graph = graph_builder.compile()

# Enhanced function to run graph with comprehensive error handling and reporting
def call_graph_enhanced():
    """Enhanced graph caller with better error handling and reporting"""
    state = {
        "user_message": "Explain me about Pydantic in Python with examples and best practices",
        "ai_message": "",
        "is_coding_question": False,
        "error_context": None,
        "retry_count": 0,
        "response_metadata": None
    }
    
    try:
        logger.info("🚀 Running enhanced graph...")
        result = graph.invoke(state)
        
        # Enhanced result reporting
        if result.get("error_context"):
            logger.warning("⚠️  Completed with fallback response")
            logger.info(f"Error type: {result['error_context']['error_type']}")
            logger.info(f"Suggestions: {result['error_context'].get('suggestions', [])}")
        else:
            logger.info("✅ Completed successfully")
            
        logger.info(f"Response preview: {result['ai_message'][:200]}...")
        
        if result.get("response_metadata"):
            logger.info(f"Metadata: {result['response_metadata']}")
            
        return result
        
    except Exception as e:
        logger.error(f"❌ Critical error in graph execution: {e}")
        return {
            "ai_message": error_handler._get_fallback_response("pydantic"),
            "error_context": {
                "error_message": str(e),
                "error_type": "CriticalError",
                "suggestions": ["Contact system administrator", "Try again later"]
            }
        }

# Demo with multiple test cases
def run_comprehensive_demo():
    """Run comprehensive demo with various scenarios"""
    test_cases = [
        "Explain me about Pydantic in Python with examples and best practices",
        "How do I validate data with Pydantic models?",
        "What are the differences between Pydantic v1 and v2?",
        "How do I handle validation errors in Pydantic?",
        "Show me Pydantic integration with FastAPI"
    ]
    
    for i, test_case in enumerate(test_cases, 1):
        logger.info(f"\n{'='*60}")
        logger.info(f"        TEST CASE #{i}")
        logger.info(f"        Query: {test_case}")
        logger.info('='*60)
        
        # Update the state for each test case
        state = {
            "user_message": test_case,
            "ai_message": "",
            "is_coding_question": False,
            "error_context": None,
            "retry_count": 0,
            "response_metadata": None
        }
        
        try:
            result = graph.invoke(state)
            
            if result.get("error_context"):
                logger.warning("⚠️  Completed with fallback response")
                print(f"Fallback Response:\n{result['ai_message']}")
            else:
                logger.info("✅ Completed successfully")
                print(f"AI Response:\n{result['ai_message'][:500]}...")
                
        except Exception as e:
            logger.error(f"❌ Error in test case {i}: {e}")
            print(f"Fallback: {error_handler._get_fallback_response('pydantic')}")
        
        time.sleep(1)  # Brief pause between test cases

# Run the demo
if __name__ == "__main__":
    run_comprehensive_demo()