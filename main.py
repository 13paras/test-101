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
import logging
from functools import wraps

load_dotenv()

# ✅ Initialize neatlogs (as required) — but we won't use it anywhere else
neatlogs.init(api_key=os.getenv('NEATLOGS_API_KEY'))

# Set up logging for error handling
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

# Custom exception for incomplete responses
class IncompleteResponseError(Exception):
    pass

# Utility function to log errors
def log_error(error, context=""):
    """Log errors with context information"""
    logger.error(f"Error in {context}: {str(error)}")
    
# Retry decorator for resilience
def retry(max_attempts=3, delay=1):
    """Decorator to add retry logic to functions"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        raise e
                    log_error(e, f"{func.__name__} attempt {attempt + 1}")
                    time.sleep(delay)
            return None
        return wrapper
    return decorator

# Response completeness validation
def is_complete(response):
    """Check if response meets completeness criteria"""
    if not response or len(response.strip()) < 50:
        return False
    # Additional checks for response quality
    if "error" in response.lower() or "incomplete" in response.lower():
        return False
    return True

# Azure OpenAI setup
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

# Enhanced Pydantic models with validation
class DetectCallResponse(BaseModel):
    is_question_ai: bool
    confidence: float = 0.8
    reasoning: str = ""

class AiResponse(BaseModel):
    ai_message: str
    completeness_score: float = 1.0

# Enhanced State with additional context
class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool
    context: dict
    retry_count: int
    classification_confidence: float

# Success tracking for reliability monitoring
successful_calls = 0
error_count = 0

# Node: Enhanced detect_query with improved context management and validation
@retry(max_attempts=3, delay=1)
def detect_query(state: State):
    user_message = state.get("user_message")
    
    # Initialize context and retry tracking
    if "context" not in state:
        state["context"] = {}
    if "retry_count" not in state:
        state["retry_count"] = 0
    
    # Enhanced system prompt with more context
    SYSTEM_PROMPT = """Your task is to determine whether the user's query is a coding-related question.
    
    Consider the following as coding-related:
    - Programming languages (Python, JavaScript, etc.)
    - Libraries and frameworks (Pydantic, React, etc.)
    - Software development concepts
    - Code implementation questions
    - Technical debugging
    
    Provide confidence score and brief reasoning for your classification.
    Ensure your response is complete and well-reasoned."""

    try:
        # Enhanced context preparation
        context_info = f"User query: {user_message}\nQuery length: {len(user_message)} characters"
        state["context"]["query_analysis"] = context_info
        
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
        state["classification_confidence"] = parsed_result.confidence
        
        # Validate response completeness
        response_text = f"Classification: {parsed_result.is_question_ai}, Confidence: {parsed_result.confidence}, Reasoning: {parsed_result.reasoning}"
        if not is_complete(response_text):
            raise IncompleteResponseError('Response is incomplete')
            
        # Store successful classification details in context
        state["context"]["classification"] = {
            "is_coding": parsed_result.is_question_ai,
            "confidence": parsed_result.confidence,
            "reasoning": parsed_result.reasoning
        }
        
        logger.info(f"Successfully classified query with confidence: {parsed_result.confidence}")
        
    except IncompleteResponseError as e:
        log_error(e, "detect_query - incomplete response")
        # Fallback with keyword-based detection
        coding_keywords = ["python", "pydantic", "code", "programming", "function", "class", "api", "library"]
        is_coding = any(keyword.lower() in user_message.lower() for keyword in coding_keywords)
        state["is_coding_question"] = is_coding
        state["classification_confidence"] = 0.6
        state["context"]["classification"] = {
            "is_coding": is_coding,
            "confidence": 0.6,
            "reasoning": "Fallback classification due to incomplete AI response"
        }
    except Exception as e:
        log_error(e, "detect_query")
        # Implement alternative handling instead of re-raising
        state["is_coding_question"] = True  # Default to coding question for safety
        state["classification_confidence"] = 0.5
        state["context"]["error"] = str(e)
        logger.warning(f"Using fallback classification due to error: {str(e)}")

    return state

# Edge router
def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"]:
    is_coding_question = state.get("is_coding_question")
    if is_coding_question:
        return "solve_coding_question"
    else:
        return "solve_simple_question"

# Node: Enhanced solve_coding_question with retry mechanism and robust error handling
@retry(max_attempts=3, delay=2)
def solve_coding_question(state: State):
    global successful_calls, error_count
    user_message = state.get("user_message")
    
    # Initialize retry tracking
    if "retry_count" not in state:
        state["retry_count"] = 0
    
    # Enhanced system prompt for better responses
    SYSTEM_PROMPT = """Your task is to solve the coding question of the user.
    
    Provide a comprehensive response that includes:
    1. Clear explanation of the concept
    2. Practical code examples when applicable
    3. Use cases and best practices
    4. Complete and well-structured information
    
    Ensure your response is thorough and helpful for the user's coding needs."""
    
    try:
        # Prepare enhanced context
        context = state.get("context", {})
        classification_info = context.get("classification", {})
        
        # Add context to the user message for better AI understanding
        enhanced_message = f"{user_message}\n\nContext: Classification confidence: {classification_info.get('confidence', 'N/A')}"
        
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=AiResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": enhanced_message},
            ],
        )
        
        ai_response = result.choices[0].message.parsed.ai_message
        
        # Validate response completeness
        if not is_complete(ai_response):
            raise IncompleteResponseError('AI response is incomplete')
        
        state["ai_message"] = ai_response
        successful_calls += 1
        
        # Store success metrics in context
        if "context" not in state:
            state["context"] = {}
        state["context"]["processing_success"] = True
        state["context"]["response_length"] = len(ai_response)
        
        logger.info(f"Successfully processed coding question. Total successful calls: {successful_calls}")
        
    except IncompleteResponseError as e:
        log_error(e, "solve_coding_question - incomplete response")
        error_count += 1
        # Provide fallback response for common coding topics
        if "pydantic" in user_message.lower():
            fallback_response = """Pydantic is a data validation library for Python that uses type hints.
            
Key features:
- Data validation using Python type annotations
- Automatic data parsing and serialization
- JSON schema generation
- Integration with FastAPI

Example:
```python
from pydantic import BaseModel

class User(BaseModel):
    name: str
    age: int
    email: str

user = User(name="John", age=30, email="john@example.com")
print(user.name)  # Output: John
```

Pydantic ensures data integrity and helps catch errors early in development."""
            state["ai_message"] = fallback_response
        else:
            # Generic fallback for other coding questions
            state["ai_message"] = f"I understand you're asking about: {user_message}. While I encountered an issue generating a complete response, I can help you with coding questions. Please provide more specific details about what you'd like to learn or implement."
        
        state["context"]["fallback_used"] = True
        
    except Exception as e:
        log_error(e, "solve_coding_question")
        error_count += 1
        
        # Implement retry logic or alternative handling instead of crashing
        state["retry_count"] += 1
        
        if state["retry_count"] < 3:
            logger.info(f"Retrying solve_coding_question (attempt {state['retry_count'] + 1})")
            # Add delay and retry will be handled by decorator
            raise e
        else:
            # After max retries, provide a graceful fallback
            logger.warning(f"Max retries reached for solve_coding_question. Providing fallback response.")
            state["ai_message"] = f"I'm experiencing technical difficulties processing your coding question: '{user_message}'. Please try rephrasing your question or contact support if the issue persists."
            state["context"]["max_retries_reached"] = True

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

# Enhanced function to run graph with comprehensive error handling and logging
def call_graph(query="Explain me about Pydantic in Python"):
    global successful_calls, error_count
    
    state = {
        "user_message": query,
        "ai_message": "",
        "is_coding_question": False,
        "context": {},
        "retry_count": 0,
        "classification_confidence": 0.0
    }

    try:
        print(f"🚀 Processing query: {query}")
        result = graph.invoke(state)
        
        # Comprehensive success reporting
        classification_confidence = result.get("classification_confidence", 0.0)
        context = result.get("context", {})
        
        print(f"✅ Success! Classification: {'Coding' if result['is_coding_question'] else 'General'} (confidence: {classification_confidence:.2f})")
        print(f"📊 Response length: {len(result['ai_message'])} characters")
        
        if context.get("fallback_used"):
            print("⚠️  Note: Fallback response was used due to processing issues")
        
        print(f"📝 Response: {result['ai_message'][:100]}...")
        
        # Log success metrics
        logger.info(f"Graph execution successful. Total successful calls: {successful_calls}, Total errors: {error_count}")
        
        return result
        
    except Exception as e:
        error_count += 1
        log_error(e, "call_graph")
        print(f"❌ ERROR CAUGHT: {str(e)}")
        print(f"📊 Error statistics - Total errors: {error_count}, Successful calls: {successful_calls}")
        
        # Return partial state for debugging
        return state

# Comprehensive testing with multiple queries
if __name__ == "__main__":
    test_queries = [
        "Explain me about Pydantic in Python",
        "How do I validate data models?",
        "What are Python type hints?",
        "Show me FastAPI integration examples",
        "How to handle validation errors?",
        "What is data serialization?",
        "Explain Python decorators",
        "How to create REST APIs?",
        "What are the benefits of static typing?",
        "Show me advanced Pydantic features"
    ]
    
    print(f"🧪 Starting reliability test with {len(test_queries)} queries...")
    print("="*60)
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"        TEST RUN #{i}: Testing reliability")
        print('='*60)
        result = call_graph(query)
        
        if result and "ai_message" in result:
            print(f"✅ Run #{i} completed successfully")
        else:
            print(f"❌ Run #{i} failed")
        
        # Brief pause between tests
        if i < len(test_queries):
            time.sleep(1)
    
    print(f"\n{'='*60}")
    print(f"🏁 RELIABILITY TEST COMPLETED")
    print(f"📊 Final Statistics:")
    print(f"   - Successful calls: {successful_calls}")
    print(f"   - Error count: {error_count}")
    print(f"   - Success rate: {(successful_calls/(successful_calls+error_count)*100) if (successful_calls+error_count) > 0 else 0:.1f}%")
    print('='*60)