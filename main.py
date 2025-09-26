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

# Pydantic models
class DetectCallResponse(BaseModel):
    is_question_ai: bool

class AiResponse(BaseModel):
    ai_message: str

# State
class State(TypedDict):
    user_message: str
    ai_message: str
    is_coding_question: bool

# 🎯 Global counter to track runs (crash limit removed)
CALL_COUNTER = 0

# Node: Detect if query is coding-related
def detect_query(state: State):
    global CALL_COUNTER
    CALL_COUNTER += 1

    user_message = state.get("user_message")
    SYSTEM_PROMPT = """You are a query classifier for a technical AI assistant. 
    Analyze the user's query and determine if it's a coding/programming-related question.

    Coding-related questions include:
    - Questions about programming languages, libraries, frameworks (e.g., Python, Pydantic, FastAPI)
    - Technical implementation questions
    - Code examples, syntax, or usage questions
    - Software development concepts and tools
    - Programming best practices and patterns

    Non-coding questions include:
    - General knowledge questions
    - Personal advice
    - Non-technical topics
    - Casual conversation

    Classify accurately to ensure the user gets the most appropriate response."""

    try:
        result = client.beta.chat.completions.parse(
            model="gpt-4o-mini",
            response_format=DetectCallResponse,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": user_message},
            ],
        )
        state["is_coding_question"] = result.choices[0].message.parsed.is_question_ai
    except Exception as e:
        raise Exception(f"Error in detect_query: {str(e)}")

    return state

# Edge router
def route_edge(state: State) -> Literal["solve_coding_question", "solve_simple_question"]:
    is_coding_question = state.get("is_coding_question")
    if is_coding_question:
        return "solve_coding_question"
    else:
        return "solve_simple_question"

# Node: Solve coding question with enhanced context awareness
def solve_coding_question(state: State):
    user_message = state.get("user_message")

    # Enhanced system prompt with comprehensive context for coding questions
    SYSTEM_PROMPT = """You are an expert programming assistant specializing in providing comprehensive, contextually rich responses to coding questions.

    When answering coding/programming questions, always provide:

    1. **Clear Overview**: Start with a concise explanation of what the topic/technology is and its primary purpose
    2. **Key Features & Capabilities**: List the main features and what makes it useful
    3. **Practical Code Examples**: Always include working code examples with proper syntax
    4. **Common Use Cases**: Explain real-world scenarios where it's commonly used
    5. **Benefits & Advantages**: Highlight why developers choose this technology
    6. **Best Practices**: Include relevant tips, considerations, or common patterns
    7. **Integration Context**: If applicable, mention how it works with other popular tools/frameworks

    For Python libraries specifically:
    - Show installation commands when relevant
    - Demonstrate basic usage patterns with complete code snippets
    - Include proper imports and setup
    - Explain configuration options when applicable
    - Mention integration with popular frameworks like FastAPI, Django, Flask, etc.

    Make your response comprehensive yet accessible, providing sufficient context for developers at various skill levels to understand and apply the information effectively."""
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
        raise Exception(f"Error in solve_coding_question: {str(e)}")

    return state

# Node: Solve simple question
def solve_simple_question(state: State):
    user_message = state.get("user_message")
    SYSTEM_PROMPT = """You are a helpful assistant that provides clear, accurate, and informative responses to general questions.

    Guidelines for responding:
    - Provide factual, well-structured answers
    - Use examples when helpful to illustrate concepts
    - Be concise but comprehensive
    - If the question seems technical despite classification, provide a basic explanation
    - Maintain a friendly and professional tone
    - Structure your response logically with clear sections when appropriate

    Ensure your response directly addresses the user's question with sufficient detail and context."""

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

# Function to run graph with error handling and multiple test queries
def call_graph(query: str = "Explain me about Pydantic in Python"):
    state = {
        "user_message": query,
        "ai_message": "",
        "is_coding_question": False
    }

    try:
        print(f"🚀 Processing query: {query}")
        result = graph.invoke(state)
        print("✅ Success! Response preview:", result["ai_message"][:150] + "...")
        return result
    except Exception as e:
        print("❌ ERROR CAUGHT:", str(e))
        return None

# Test with multiple diverse queries to validate fixes
if __name__ == "__main__":
    test_queries = [
        "Explain me about Pydantic in Python",
        "How do I validate data with Pydantic models?",
        "What's the weather like today?",
        "How to use FastAPI with Pydantic?",
        "What are Python decorators?",
        "Can you recommend a good restaurant?",
        "Explain type hints in Python",
        "What's your favorite color?"
    ]
    
    for i, query in enumerate(test_queries, 1):
        print(f"\n{'='*60}")
        print(f"        TEST #{i} - Query Type Check")
        print('='*60)
        result = call_graph(query)
        if result:
            print(f"✓ Classification: {'Coding' if result['is_coding_question'] else 'Simple'} question")
        time.sleep(1)  # Brief pause between tests