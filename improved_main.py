from typing_extensions import TypedDict
from openai import AzureOpenAI
import openai
from dotenv import load_dotenv
import os
from typing import Literal
from langgraph.graph import StateGraph, START, END
import time
from pydantic import BaseModel
import neatlogs
import logging
from datetime import datetime
import random

load_dotenv()

# Initialize neatlogs and logging
neatlogs.init(api_key=os.getenv('NEATLOGS_API_KEY'))

# Setup logging for error tracking
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def log_llm_error(error_type: str, user_message: str, error_details: str):
    """Log LLM response errors for analysis"""
    timestamp = datetime.now().isoformat()
    error_info = {
        "timestamp": timestamp,
        "error_type": error_type,
        "user_message": user_message[:100] + "..." if len(user_message) > 100 else user_message,
        "error_details": str(error_details),
        "component": "langgraph.node.solve_coding_question"
    }
    
    logger.error(f"LLM Response Error: {error_info}")
    print(f"🔍 Logged LLM error: {error_type} - {error_details[:50]}...")
    
    # You could also send this to an external monitoring service
    try:
        neatlogs.info(f"LLM Response Processing Error", error_info)
    except Exception as e:
        logger.warning(f"Failed to send error to neatlogs: {e}")

# Azure OpenAI setup
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

# Improved Pydantic models
class QueryClassificationResponse(BaseModel):
    is_coding_question: bool
    confidence_score: float
    reasoning: str

class AiResponse(BaseModel):
    ai_message: str
    response_type: str = "general"
    includes_code_examples: bool = False
    
    def __init__(self, **data):
        # Ensure ai_message is not empty
        if not data.get('ai_message') or not data['ai_message'].strip():
            raise ValueError("ai_message field cannot be empty or None")
        super().__init__(**data)

# State
class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool
    query_classification: dict

# Enhanced fallback response generator
def generate_enhanced_fallback_response(user_message: str, response_type: str) -> str:
    """Generate a comprehensive fallback response when LLM fails to provide ai_message field"""
    
    # Programming topics with enhanced responses
    programming_topics = {
        "pydantic": """Pydantic is a Python library that provides data validation and parsing using Python type hints.

Key Features:
- Data validation using type annotations
- Automatic data parsing and conversion
- JSON schema generation
- Integration with FastAPI and other frameworks

Basic Example:
```python
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None

# Usage
user_data = {"id": "123", "name": "John Doe"}
user = User(**user_data)  # Automatically converts id to int
print(user.name)  # Output: John Doe
```

Common Use Cases:
- API request/response validation
- Configuration management
- Data pipeline validation
- FastAPI integration

Pydantic ensures data integrity and reduces runtime errors by validating data at the application boundary.""",
        
        "fastapi": """FastAPI is a modern, fast web framework for building APIs with Python 3.7+ based on standard Python type hints.

Key Features:
- Automatic API documentation
- Built-in data validation with Pydantic
- High performance (comparable to NodeJS and Go)
- Easy to use and learn

Basic Example:
```python
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()

class Item(BaseModel):
    name: str
    price: float
    is_offer: bool = False

@app.post("/items/")
async def create_item(item: Item):
    return item
```

Benefits:
- Automatic request/response validation
- Interactive API documentation
- Type safety and IDE support
- Production-ready performance""",
        
        "python": """Python is a high-level, interpreted programming language known for its simplicity and readability.

Key Features:
- Clean, readable syntax
- Extensive standard library
- Large ecosystem of third-party packages
- Cross-platform compatibility
- Strong community support

Common Use Cases:
- Web development (Django, Flask, FastAPI)
- Data science and analytics
- Machine learning and AI
- Automation and scripting
- Scientific computing"""
    }
    
    # Check for specific programming topics
    for topic, response in programming_topics.items():
        if topic in user_message.lower():
            return response
    
    # General programming question
    if response_type == "coding" or any(keyword in user_message.lower() for keyword in ["programming", "code", "library", "framework", "api", "function", "class"]):
        return f"""I understand you're asking about a programming topic: '{user_message}'. 

Unfortunately, I encountered an issue generating a complete response. This could be due to:
- Temporary service issues
- Complex query requirements
- Model processing limitations

Please try:
1. Rephrasing your question more specifically
2. Breaking complex questions into smaller parts
3. Checking your internet connection
4. Contacting support if this issue persists

I apologize for the inconvenience and appreciate your patience."""
    
    # General non-programming question
    else:
        return f"""I apologize, but I encountered an issue processing your request: '{user_message}'. 

This could be due to:
- Temporary service issues
- Unexpected query format
- Model processing limitations

Please try:
1. Rephrasing your question
2. Being more specific about what you need
3. Contacting support if this problem continues

Thank you for your understanding."""

# Improved detection function with better prompt
def detect_query(state: State):
    user_message = state.get("user_message")
    
    # Significantly improved system prompt for query classification
    SYSTEM_PROMPT = """You are a query classifier for a technical AI assistant. 
    Analyze the user's query and determine if it's a coding/programming-related question.

    Coding-related questions include:
    - Questions about programming languages, libraries, frameworks
    - Technical implementation questions
    - Code examples, syntax, or usage questions
    - Software development concepts
    - Programming tools and technologies

    Non-coding questions include:
    - General knowledge questions
    - Personal advice
    - Non-technical topics
    - Casual conversation

    Provide your classification with confidence score (0.0-1.0) and brief reasoning."""

    try:
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=QueryClassificationResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        classification = result.choices[0].message.parsed
        state["is_coding_question"] = classification.is_coding_question
        state["query_classification"] = {
            "confidence": classification.confidence_score,
            "reasoning": classification.reasoning
        }
    except Exception as e:
        # Fallback classification for technical terms
        technical_keywords = ["python", "pydantic", "programming", "code", "library", "framework", "api"]
        is_likely_coding = any(keyword.lower() in user_message.lower() for keyword in technical_keywords)
        state["is_coding_question"] = is_likely_coding
        state["query_classification"] = {
            "confidence": 0.7 if is_likely_coding else 0.3,
            "reasoning": f"Fallback classification based on keywords. Error: {str(e)}"
        }
        print(f"Warning: Classification failed, using fallback. Error: {str(e)}")

    return state

# Edge router
def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"]:
    is_coding_question = state.get("is_coding_question")
    return "solve_coding_question" if is_coding_question else "solve_simple_question"

# Dramatically improved coding question handler
def solve_coding_question(state: State):
    user_message = state.get("user_message")

    # Comprehensive system prompt for technical/coding questions
    SYSTEM_PROMPT = """You are a knowledgeable programming assistant specializing in Python and related technologies.

    CRITICAL: Always provide a complete response in the 'ai_message' field. Never return partial or incomplete responses.

    When explaining programming topics, libraries, or frameworks:

    1. **Overview**: Start with a clear, concise explanation of what it is and its primary purpose
    2. **Key Features**: List the main features and capabilities
    3. **Code Examples**: Always provide practical, working code examples
    4. **Use Cases**: Explain common scenarios where it's used
    5. **Benefits**: Highlight advantages and why developers choose it
    6. **Best Practices**: Include relevant tips or considerations

    For Python libraries specifically:
    - Show installation instructions when relevant
    - Demonstrate basic usage patterns
    - Include imports and complete code snippets
    - Explain integration with popular frameworks when applicable

    Make your response comprehensive yet accessible, suitable for developers at various skill levels.
    Ensure your entire response is properly formatted and complete before submitting."""

    try:
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=AiResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        
        # Validate LLM response and check for ai_message field
        if not result or not hasattr(result, 'choices') or not result.choices:
            raise Exception("Failed to process model response: Empty or invalid response from LLM")
        
        parsed_response = result.choices[0].message.parsed
        if not parsed_response:
            raise Exception("Failed to process model response: LLM response could not be parsed")
            
        if not hasattr(parsed_response, 'ai_message') or not parsed_response.ai_message:
            error_msg = "LLM response missing required field 'ai_message'. Model may have returned partial output."
            log_llm_error("MISSING_AI_MESSAGE", user_message, error_msg)
            print(f"⚠️ Warning: {error_msg}")
            # Provide a fallback response based on the user query
            fallback_response = generate_enhanced_fallback_response(user_message, "coding")
            state["ai_message"] = fallback_response
        else:
            state["ai_message"] = parsed_response.ai_message
            
    except Exception as e:
        log_llm_error("GENERAL_ERROR", user_message, str(e))
        print(f"⚠️ Error in solve_coding_question: {str(e)}")
        # Provide a fallback response for Pydantic specifically or general coding questions
        if "pydantic" in user_message.lower():
            fallback_response = """Pydantic is a Python library that provides data validation and parsing using Python type hints.

Key Features:
- Data validation using type annotations
- Automatic data parsing and conversion
- JSON schema generation
- Integration with FastAPI and other frameworks

Basic Example:
```python
from pydantic import BaseModel
from typing import Optional

class User(BaseModel):
    id: int
    name: str
    email: Optional[str] = None

# Usage
user_data = {"id": "123", "name": "John Doe"}
user = User(**user_data)  # Automatically converts id to int
print(user.name)  # Output: John Doe
```

Common Use Cases:
- API request/response validation
- Configuration management
- Data pipeline validation
- FastAPI integration

Pydantic ensures data integrity and reduces runtime errors by validating data at the application boundary."""
            state["ai_message"] = fallback_response
        else:
            fallback_response = generate_enhanced_fallback_response(user_message, "coding")
            state["ai_message"] = fallback_response

    return state

# Improved simple question handler
def solve_simple_question(state: State):
    user_message = state.get("user_message")
    
    # Better system prompt for non-coding questions
    SYSTEM_PROMPT = """You are a helpful assistant that provides clear, accurate, and informative responses to general questions.

    CRITICAL: Always provide a complete response in the 'ai_message' field. Never return partial or incomplete responses.

    Guidelines:
    - Provide factual, well-structured answers
    - Use examples when helpful
    - Be concise but comprehensive
    - If the question seems technical despite classification, provide a basic technical explanation
    - Maintain a friendly and professional tone
    - Ensure your entire response is properly formatted and complete before submitting"""

    try:
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=AiResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        
        # Validate LLM response and check for ai_message field
        if not result or not hasattr(result, 'choices') or not result.choices:
            raise Exception("Failed to process model response: Empty or invalid response from LLM")
        
        parsed_response = result.choices[0].message.parsed
        if not parsed_response:
            raise Exception("Failed to process model response: LLM response could not be parsed")
            
        if not hasattr(parsed_response, 'ai_message') or not parsed_response.ai_message:
            error_msg = "LLM response missing required field 'ai_message'. Model may have returned partial output."
            log_llm_error("MISSING_AI_MESSAGE", user_message, error_msg)
            print(f"⚠️ Warning: {error_msg}")
            # Provide a fallback response based on the user query
            fallback_response = generate_enhanced_fallback_response(user_message, "simple")
            state["ai_message"] = fallback_response
        else:
            state["ai_message"] = parsed_response.ai_message
            
    except Exception as e:
        log_llm_error("GENERAL_ERROR", user_message, str(e))
        print(f"⚠️ Error in solve_simple_question: {str(e)}")
        # Provide a fallback response to ensure graceful handling
        fallback_response = generate_enhanced_fallback_response(user_message, "simple")
        state["ai_message"] = fallback_response

    return state

# Build improved graph
graph_builder = StateGraph(State)
graph_builder.add_node("detect_query", detect_query)
graph_builder.add_node("solve_coding_question", solve_coding_question)
graph_builder.add_node("solve_simple_question", solve_simple_question)

graph_builder.add_edge(START, "detect_query")
graph_builder.add_conditional_edges("detect_query", route_edge)
graph_builder.add_edge("solve_coding_question", END)
graph_builder.add_edge("solve_simple_question", END)

graph = graph_builder.compile()

# Enhanced function to run graph with better error handling and logging
def call_graph(query: str = "Explain me about Pydantic in Python"):
    state = {
        "user_message": query,
        "ai_message": "",
        "is_coding_question": False,
        "query_classification": {}
    }

    try:
        print(f"🚀 Processing query: {query}")
        result = graph.invoke(state)
        
        # Enhanced output with classification info
        classification = result.get("query_classification", {})
        print(f"📊 Classification: {'Coding' if result['is_coding_question'] else 'Simple'} "
              f"(Confidence: {classification.get('confidence', 'N/A')})")
        print(f"🧠 Reasoning: {classification.get('reasoning', 'N/A')}")
        print(f"✅ Response:\n{result['ai_message']}")
        
        return result
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return None

# Test with various queries
if __name__ == "__main__":
    test_queries = [
        "Explain me about Pydantic in Python",
        "How do I validate data with Pydantic?",
        "What's the weather like today?",
        "How to use FastAPI with Pydantic models?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"        TEST #{i}")
        print('='*60)
        call_graph(query)
        if i < len(test_queries):
            time.sleep(1)  # Brief pause between tests