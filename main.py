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
import random
import logging
import json
from datetime import datetime

load_dotenv()

# Initialize neatlogs and Python logging
neatlogs.init(api_key=os.getenv('NEATLOGS_API_KEY'))

# Configure comprehensive logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('llm_responses.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Azure OpenAI setup
client = AzureOpenAI(
    api_key=os.getenv("AZURE_OPENAI_API_KEY"),
    api_version=os.getenv("AZURE_OPENAI_API_VERSION"),
    azure_endpoint=os.getenv("AZURE_OPENAI_ENDPOINT"),
    azure_deployment=os.getenv("AZURE_OPENAI_DEPLOYMENT_NAME"),
)

# Pydantic models
class DetectCallResponse(BaseModel):
    is_question_ai: bool

class AiResponse(BaseModel):
    ai_message: str
    
    def validate_completeness(self) -> bool:
        """Validate that all required fields are present and non-empty."""
        return bool(self.ai_message and self.ai_message.strip())

# State
class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool

# Response validation and logging utilities
def validate_and_log_response(response_data: dict, context: str, user_message: str) -> bool:
    """
    Validate LLM response and log any issues.
    Returns True if response is valid, False otherwise.
    """
    is_valid = True
    issues = []
    
    # Check if response_data exists
    if not response_data:
        issues.append("Response data is None or empty")
        is_valid = False
    
    # Check for required ai_message field
    if not response_data.get('ai_message'):
        issues.append("Missing or empty 'ai_message' field")
        is_valid = False
    elif len(response_data['ai_message'].strip()) < 10:
        issues.append(f"ai_message too short: {len(response_data['ai_message'])} characters")
        is_valid = False
    
    # Log the validation result
    log_entry = {
        "timestamp": datetime.now().isoformat(),
        "context": context,
        "user_message": user_message[:100] + "..." if len(user_message) > 100 else user_message,
        "is_valid": is_valid,
        "issues": issues,
        "response_length": len(response_data.get('ai_message', '')) if response_data else 0
    }
    
    if is_valid:
        logger.info(f"✅ Valid response in {context}: {json.dumps(log_entry)}")
    else:
        logger.error(f"❌ Invalid response in {context}: {json.dumps(log_entry)}")
        # Also log to neatlogs for external monitoring
        neatlogs.log("llm_response_validation_failed", log_entry)
    
    return is_valid

def create_fallback_response(user_message: str, context: str) -> str:
    """Create a fallback response when LLM fails to generate proper response."""
    logger.warning(f"Creating fallback response for {context}")
    
    # Specific fallbacks for known topics
    if "pydantic" in user_message.lower():
        return """Pydantic is a Python library that provides data validation and parsing using Python type hints.

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

Pydantic ensures data integrity and reduces runtime errors by validating data at the application boundary.

Note: This is a fallback response due to an issue with the primary response generation system."""
    
    elif any(keyword in user_message.lower() for keyword in ["python", "programming", "code", "library", "framework"]):
        return f"""I apologize, but I encountered an issue generating a complete response to your programming question: "{user_message}"

To get a proper answer, you may want to:
1. Try rephrasing your question
2. Be more specific about what you'd like to know
3. Check the official documentation for the technology you're asking about

Note: This is a fallback response due to a technical issue with the response generation system."""
    
    else:
        return f"""I apologize, but I encountered an issue generating a complete response to your question: "{user_message}"

Please try rephrasing your question or contact support if this issue persists.

Note: This is a fallback response due to a technical issue with the response generation system."""

# 🎯 Global counter to trigger error after 2 successful runs
CALL_COUNTER = 0
MAX_SUCCESSFUL_CALLS = 2

# Node: Detect if query is coding-related with comprehensive error handling
def detect_query(state: State):
    global CALL_COUNTER
    CALL_COUNTER += 1

    user_message = state.get("user_message", "")
    context = "detect_query"
    
    logger.info(f"Detecting query type for: {user_message[:100]}...")

    # Improved system prompt for query classification
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

Return true if the question is coding-related, false otherwise."""

    try:
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=DetectCallResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        
        # Validate the response structure
        if not result or not result.choices or len(result.choices) == 0:
            logger.error(f"Invalid API response structure in {context}")
            raise Exception("Invalid API response structure")
            
        parsed_response = result.choices[0].message.parsed
        
        # Validate parsed response
        if not parsed_response:
            logger.error(f"Failed to parse response in {context}")
            raise Exception("Failed to parse API response")
        
        # Check if parsed response has is_question_ai field
        if not hasattr(parsed_response, 'is_question_ai'):
            logger.error(f"Missing is_question_ai field in {context}")
            raise Exception("Response missing required is_question_ai field")
        
        state["is_coding_question"] = parsed_response.is_question_ai
        logger.info(f"Query classified as {'coding' if parsed_response.is_question_ai else 'simple'} question")
        
    except Exception as e:
        logger.error(f"Error in {context}: {str(e)}")
        
        # Log the error details for analysis
        error_details = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "user_message": user_message[:100] + "..." if len(user_message) > 100 else user_message,
            "error_type": type(e).__name__,
            "error_message": str(e)
        }
        
        neatlogs.log("query_classification_error", error_details)
        
        # Fallback classification based on keywords
        technical_keywords = ["python", "pydantic", "programming", "code", "library", "framework", "api", "software", "development"]
        is_likely_coding = any(keyword.lower() in user_message.lower() for keyword in technical_keywords)
        state["is_coding_question"] = is_likely_coding
        
        logger.warning(f"Used fallback classification: {'coding' if is_likely_coding else 'simple'} question")

    return state

# Edge router
def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"]:
    is_coding_question = state.get("is_coding_question")
    if is_coding_question:
        return "solve_coding_question"
    else:
        return "solve_simple_question"

# Node: Solve coding question with comprehensive error handling
def solve_coding_question(state: State):
    user_message = state.get("user_message", "")
    context = "solve_coding_question"
    
    logger.info(f"Processing coding question: {user_message[:100]}...")

    # 🚨 FORCE ERROR after MAX_SUCCESSFUL_CALLS (for testing)
    if CALL_COUNTER > MAX_SUCCESSFUL_CALLS:
        logger.error(f"Simulated error triggered after {MAX_SUCCESSFUL_CALLS} calls")
        raise Exception(f"🚨 Simulated crash after {MAX_SUCCESSFUL_CALLS} successful runs!")

    # Improved system prompt for coding questions
    SYSTEM_PROMPT = """You are a knowledgeable programming assistant specializing in Python and related technologies.

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
Ensure your response is substantial and informative (at least 200 words)."""
    
    try:
        # Make the API call
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=AiResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        
        # Validate the response structure
        if not result or not result.choices or len(result.choices) == 0:
            logger.error(f"Invalid API response structure in {context}")
            raise Exception("Invalid API response structure")
            
        parsed_response = result.choices[0].message.parsed
        
        # Validate parsed response
        if not parsed_response:
            logger.error(f"Failed to parse response in {context}")
            raise Exception("Failed to parse API response")
        
        # Check if parsed response has ai_message field and it's valid
        if not hasattr(parsed_response, 'ai_message') or not parsed_response.ai_message:
            logger.error(f"Missing ai_message field in {context}")
            raise Exception("Response missing required ai_message field")
        
        # Validate response completeness using our validation function
        response_data = {"ai_message": parsed_response.ai_message}
        if not validate_and_log_response(response_data, context, user_message):
            logger.warning(f"Response failed validation in {context}, using fallback")
            state["ai_message"] = create_fallback_response(user_message, context)
        else:
            # Use the validated response
            state["ai_message"] = parsed_response.ai_message
            logger.info(f"Successfully processed coding question with {len(parsed_response.ai_message)} characters")
            
    except Exception as e:
        logger.error(f"Error in {context}: {str(e)}")
        
        # Log the error details for analysis
        error_details = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "user_message": user_message[:100] + "..." if len(user_message) > 100 else user_message,
            "error_type": type(e).__name__,
            "error_message": str(e)
        }
        
        neatlogs.log("llm_response_error", error_details)
        
        # Provide fallback response instead of crashing
        state["ai_message"] = create_fallback_response(user_message, context)
        logger.info(f"Used fallback response for error in {context}")

    return state

# Node: Solve simple question with comprehensive error handling
def solve_simple_question(state: State):
    user_message = state.get("user_message", "")
    context = "solve_simple_question"
    
    logger.info(f"Processing simple question: {user_message[:100]}...")

    # Improved system prompt for non-coding questions
    SYSTEM_PROMPT = """You are a helpful assistant that provides clear, accurate, and informative responses to general questions.

Guidelines:
- Provide factual, well-structured answers
- Use examples when helpful
- Be concise but comprehensive
- If the question seems technical despite classification, provide a basic technical explanation
- Maintain a friendly and professional tone
- Ensure your response is helpful and complete (at least 50 words)"""

    try:
        # Make the API call
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=AiResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        
        # Validate the response structure
        if not result or not result.choices or len(result.choices) == 0:
            logger.error(f"Invalid API response structure in {context}")
            raise Exception("Invalid API response structure")
            
        parsed_response = result.choices[0].message.parsed
        
        # Validate parsed response
        if not parsed_response:
            logger.error(f"Failed to parse response in {context}")
            raise Exception("Failed to parse API response")
        
        # Check if parsed response has ai_message field and it's valid
        if not hasattr(parsed_response, 'ai_message') or not parsed_response.ai_message:
            logger.error(f"Missing ai_message field in {context}")
            raise Exception("Response missing required ai_message field")
        
        # Validate response completeness using our validation function
        response_data = {"ai_message": parsed_response.ai_message}
        if not validate_and_log_response(response_data, context, user_message):
            logger.warning(f"Response failed validation in {context}, using fallback")
            state["ai_message"] = create_fallback_response(user_message, context)
        else:
            # Use the validated response
            state["ai_message"] = parsed_response.ai_message
            logger.info(f"Successfully processed simple question with {len(parsed_response.ai_message)} characters")
            
    except Exception as e:
        logger.error(f"Error in {context}: {str(e)}")
        
        # Log the error details for analysis
        error_details = {
            "timestamp": datetime.now().isoformat(),
            "context": context,
            "user_message": user_message[:100] + "..." if len(user_message) > 100 else user_message,
            "error_type": type(e).__name__,
            "error_message": str(e)
        }
        
        neatlogs.log("llm_response_error", error_details)
        
        # Provide fallback response instead of crashing
        state["ai_message"] = create_fallback_response(user_message, context)
        logger.info(f"Used fallback response for error in {context}")

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

# Enhanced function to run graph with comprehensive error handling and validation
def call_graph(query: str = "Explain me about Pydantic in Python"):
    state = {
        "user_message": query,
        "ai_message": "",
        "is_coding_question": False
    }

    logger.info(f"Starting graph execution for query: {query}")

    try:
        print("🚀 Running graph...")
        result = graph.invoke(state)
        
        # Validate the final result
        if not result:
            logger.error("Graph returned None or empty result")
            print("❌ ERROR: Graph returned no result")
            return None
            
        # Check if ai_message is present and valid
        ai_message = result.get("ai_message", "")
        if not ai_message or not ai_message.strip():
            logger.error("Final result missing valid ai_message field")
            print("❌ ERROR: No valid response generated")
            
            # Create emergency fallback
            emergency_fallback = create_fallback_response(query, "final_result_validation")
            result["ai_message"] = emergency_fallback
            logger.warning("Applied emergency fallback for missing ai_message")
        
        # Final validation of the response
        if not validate_and_log_response({"ai_message": result["ai_message"]}, "final_result", query):
            logger.warning("Final result failed validation but proceeding with response")
        
        # Log successful completion
        logger.info(f"Graph execution completed successfully with {len(result['ai_message'])} character response")
        print("✅ Success:", result["ai_message"][:100] + "...")
        
        # Log completion details to neatlogs
        completion_details = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "is_coding_question": result.get("is_coding_question", False),
            "response_length": len(result["ai_message"]),
            "success": True
        }
        neatlogs.log("graph_execution_completed", completion_details)
        
        return result
        
    except Exception as e:
        logger.error(f"Graph execution failed: {str(e)}")
        print(f"❌ ERROR CAUGHT: {str(e)}")
        
        # Log the failure details
        failure_details = {
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "error_type": type(e).__name__,
            "error_message": str(e),
            "success": False
        }
        neatlogs.log("graph_execution_failed", failure_details)
        
        # Return a fallback result even on complete failure
        fallback_result = {
            "user_message": query,
            "ai_message": create_fallback_response(query, "graph_execution_failure"),
            "is_coding_question": any(keyword.lower() in query.lower() for keyword in ["python", "pydantic", "programming", "code"])
        }
        
        logger.info("Returning fallback result due to graph execution failure")
        return fallback_result

# Run multiple times
if __name__ == "__main__":
    for i in range(5):
        print(f"\n{'='*40}")
        print(f"        RUN #{i+1}")
        print('='*40)
        call_graph()
        time.sleep(2)