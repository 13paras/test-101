from typing_extensions import TypedDict
from openai import AzureOpenAI
import openai
from dotenv import load_dotenv
import os
from typing import Literal
from langgraph.graph import StateGraph, START, END
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

# Enhanced Pydantic models for better context passing
class DetectCallResponse(BaseModel):
    is_question_ai: bool
    confidence_score: float
    reasoning: str
    query_complexity: str  # simple, moderate, complex
    key_topics: list[str]  # extracted key topics/concepts

class AiResponse(BaseModel):
    ai_message: str

# Enhanced State with comprehensive context preservation
class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool
    # Rich context dictionary to preserve all classification details
    query_context: dict  # stores classification reasoning, confidence, complexity, topics, etc.
    processing_metadata: dict  # stores processing steps and decisions

# 🎯 Global counter to trigger error after 2 successful runs
CALL_COUNTER = 0
MAX_SUCCESSFUL_CALLS = 2

# Enhanced Node: Detect query with comprehensive context preservation
def detect_query(state: State):
    global CALL_COUNTER
    CALL_COUNTER += 1

    user_message = state.get("user_message")
    
    # Enhanced system prompt for comprehensive query analysis
    SYSTEM_PROMPT = """You are an advanced query classifier for a technical AI assistant.
    
    Analyze the user's query comprehensively and provide:
    1. Classification (coding vs non-coding)
    2. Confidence score (0.0-1.0)
    3. Detailed reasoning for your classification
    4. Query complexity assessment (simple, moderate, complex)
    5. Key topics/concepts mentioned in the query
    
    Coding-related queries include:
    - Programming languages, libraries, frameworks (Python, Pydantic, FastAPI, etc.)
    - Technical implementation questions
    - Code examples, syntax, debugging
    - Software development concepts
    - API usage and integration
    
    Provide thorough analysis to help downstream processing."""

    try:
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=DetectCallResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        
        classification = result.choices[0].message.parsed
        
        # Store classification result
        state["is_coding_question"] = classification.is_question_ai
        
        # Preserve ALL context in a comprehensive dictionary
        state["query_context"] = {
            "original_query": user_message,
            "classification": "coding" if classification.is_question_ai else "general",
            "confidence_score": classification.confidence_score,
            "reasoning": classification.reasoning,
            "complexity": classification.query_complexity,
            "key_topics": classification.key_topics,
            "timestamp": time.time(),
            "analysis_details": {
                "has_technical_terms": any(term.lower() in user_message.lower() 
                                         for term in ["python", "pydantic", "code", "api", "library", "framework"]),
                "query_length": len(user_message.split()),
                "contains_question_words": any(word in user_message.lower() 
                                              for word in ["how", "what", "why", "when", "where", "explain"])
            }
        }
        
        # Track processing metadata
        state["processing_metadata"] = {
            "detect_query_completed": True,
            "classification_method": "llm_analysis",
            "processing_step": "detection_complete"
        }
        
    except Exception as e:
        # Enhanced fallback with keyword analysis
        technical_keywords = ["python", "pydantic", "programming", "code", "library", "framework", "api", "debug"]
        is_likely_coding = any(keyword.lower() in user_message.lower() for keyword in technical_keywords)
        
        state["is_coding_question"] = is_likely_coding
        
        # Preserve context even in fallback scenario
        state["query_context"] = {
            "original_query": user_message,
            "classification": "coding" if is_likely_coding else "general", 
            "confidence_score": 0.7 if is_likely_coding else 0.3,
            "reasoning": f"Fallback keyword-based classification. Keywords found: {[k for k in technical_keywords if k.lower() in user_message.lower()]}",
            "complexity": "moderate",  # default assumption
            "key_topics": [k for k in technical_keywords if k.lower() in user_message.lower()],
            "timestamp": time.time(),
            "analysis_details": {
                "has_technical_terms": is_likely_coding,
                "query_length": len(user_message.split()),
                "contains_question_words": any(word in user_message.lower() 
                                              for word in ["how", "what", "why", "when", "where", "explain"])
            }
        }
        
        state["processing_metadata"] = {
            "detect_query_completed": True,
            "classification_method": "fallback_keywords",
            "processing_step": "detection_complete_with_fallback",
            "error_encountered": str(e)
        }
        
        print(f"Warning: LLM classification failed, using keyword fallback. Error: {str(e)}")

    return state

# Edge router
def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"]:
    is_coding_question = state.get("is_coding_question")
    if is_coding_question:
        return "solve_coding_question"
    else:
        return "solve_simple_question"

# Enhanced Node: Solve coding question with full context awareness
def solve_coding_question(state: State):
    user_message = state.get("user_message")
    query_context = state.get("query_context", {})
    processing_metadata = state.get("processing_metadata", {})

    # 🚨 FORCE ERROR after MAX_SUCCESSFUL_CALLS
    if CALL_COUNTER > MAX_SUCCESSFUL_CALLS:
        raise Exception(f"🚨 Simulated crash after {MAX_SUCCESSFUL_CALLS} successful runs!")

    # Context-aware system prompt that leverages classification details
    classification_info = f"""Classification Details:
    - Query Type: {query_context.get('classification', 'unknown')}
    - Confidence: {query_context.get('confidence_score', 'N/A')}
    - Complexity: {query_context.get('complexity', 'unknown')}
    - Key Topics: {', '.join(query_context.get('key_topics', []))}
    - Reasoning: {query_context.get('reasoning', 'No reasoning available')}"""
    
    # Dynamic system prompt based on context
    base_prompt = "You are an expert programming assistant specializing in comprehensive technical explanations."
    
    if query_context.get('complexity') == 'complex':
        complexity_guidance = "This is a complex query. Provide detailed, thorough explanations with multiple examples and edge cases."
    elif query_context.get('complexity') == 'simple':
        complexity_guidance = "This is a straightforward query. Provide clear, concise explanations with basic examples."
    else:
        complexity_guidance = "Provide balanced explanations appropriate for intermediate level understanding."
    
    # Topic-specific guidance
    key_topics = query_context.get('key_topics', [])
    topic_guidance = ""
    if 'pydantic' in [topic.lower() for topic in key_topics]:
        topic_guidance = """Focus on Pydantic specifics:
        - Data validation and parsing
        - Type hints and model definitions
        - Integration with FastAPI and other frameworks
        - Practical examples with real-world use cases"""
    elif any(topic.lower() in ['python', 'programming'] for topic in key_topics):
        topic_guidance = "Provide Python-focused explanations with code examples and best practices."
    
    SYSTEM_PROMPT = f"""{base_prompt}
    
    {classification_info}
    
    Based on the classification analysis above:
    
    {complexity_guidance}
    
    {topic_guidance}
    
    Guidelines:
    1. **Comprehensive Coverage**: Address all aspects mentioned in the key topics
    2. **Code Examples**: Always provide practical, working code examples
    3. **Context Awareness**: Use the classification reasoning to tailor your response depth
    4. **Progressive Explanation**: Start with overview, then dive into specifics
    5. **Real-world Applications**: Include practical use cases and scenarios
    
    Make your response thorough yet accessible, leveraging all available context."""
    
    try:
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=AiResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        state["ai_message"] = result.choices[0].message.parsed.ai_message
        
        # Update processing metadata
        state["processing_metadata"].update({
            "solve_coding_question_completed": True,
            "context_utilized": True,
            "response_tailored_to_complexity": query_context.get('complexity', 'unknown'),
            "topics_addressed": key_topics
        })
        
    except Exception as e:
        # Enhanced fallback for specific topics
        if 'pydantic' in user_message.lower():
            fallback_response = f"""Based on your query about Pydantic (Classification: {query_context.get('classification', 'coding')}, Confidence: {query_context.get('confidence_score', 'N/A')}):

Pydantic is a powerful Python library for data validation and parsing using type hints.

**Key Features:**
- Runtime data validation
- Automatic type conversion
- JSON schema generation
- Excellent FastAPI integration

**Basic Example:**
```python
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None
    age: int

# Usage with automatic validation
user_data = {{"id": "123", "name": "John", "age": "30"}}
user = User(**user_data)  # Converts strings to appropriate types
print(f"User {{user.name}} is {{user.age}} years old")
```

**Common Use Cases:**
- API request/response validation
- Configuration file parsing
- Data pipeline validation
- Database model definition

**Integration with FastAPI:**
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_available: bool = True

@app.post("/items/")
async def create_item(item: Item):
    return {{"message": f"Created {{item.name}} for ${{item.price}}"}}
```

This response was generated using available context: {query_context.get('reasoning', 'No specific reasoning available')}."""
            
            state["ai_message"] = fallback_response
            state["processing_metadata"].update({
                "solve_coding_question_completed": True,
                "fallback_used": True,
                "fallback_reason": str(e)
            })
        else:
            raise Exception(f"Error in solve_coding_question: {str(e)}")

    return state

# Node: Solve simple question
def solve_simple_question(state: State):
    user_message = state.get("user_message")
    SYSTEM_PROMPT = "Your task is to solve the simple question of the user."

    try:
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=AiResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        state["ai_message"] = result.choices[0].message.parsed.ai_message
    except Exception as e:
        raise Exception(f"Error in solve_simple_question: {str(e)}")

    return state

# Build graph
graph_builder = StateGraph(State)
graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_question", solve_simple_question)

graph_builder.add_edge(START, "detect_query")
graph_builder.add_conditional_edges("detect_query", route_edge)
graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_simple_question", END)

graph = graph_builder.compile()

# Enhanced function to run graph with comprehensive context tracking
def call_graph(query: str = "Explain me about Pydantic in Python"):
    state = {
        "user_message": query,
        "ai_message": "",
        "is_coding_question": False,
        "query_context": {},  # Initialize context dictionary
        "processing_metadata": {}  # Initialize processing metadata
    }

    try:
        print(f"🚀 Running graph for query: {query}")
        result = graph.invoke(state)
        
        # Display comprehensive results with context information
        query_context = result.get("query_context", {})
        processing_metadata = result.get("processing_metadata", {})
        
        print(f"\n📊 Query Analysis:")
        print(f"   Classification: {query_context.get('classification', 'unknown')}")
        print(f"   Confidence: {query_context.get('confidence_score', 'N/A')}")
        print(f"   Complexity: {query_context.get('complexity', 'unknown')}")
        print(f"   Key Topics: {', '.join(query_context.get('key_topics', []))}")
        print(f"   Reasoning: {query_context.get('reasoning', 'N/A')[:100]}...")
        
        print(f"\n🔄 Processing Info:")
        print(f"   Context Preserved: {processing_metadata.get('context_utilized', False)}")
        print(f"   Classification Method: {processing_metadata.get('classification_method', 'unknown')}")
        
        print(f"\n✅ Response (Length: {len(result['ai_message'])} chars):")
        print(result["ai_message"][:200] + "..." if len(result["ai_message"]) > 200 else result["ai_message"])
        
        return result
    except Exception as e:
        print("❌ ERROR CAUGHT:", str(e))
        return None

# Run multiple times with different queries to test context preservation
if __name__ == "__main__":
    test_queries = [
        "Explain me about Pydantic in Python",
        "How do I validate data with Pydantic models?",
        "What are the key features of Pydantic for FastAPI integration?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*50}")
        print(f"        RUN #{i}: TESTING CONTEXT PRESERVATION")
        print('='*50)
        call_graph(query)
        if i < len(test_queries):
            time.sleep(2)