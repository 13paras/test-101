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

# 🎯 Global counter to trigger error after 2 successful runs
CALL_COUNTER = 0
MAX_SUCCESSFUL_CALLS = 2

# Node: Detect if query is coding-related
def detect_query(state: State):
    global CALL_COUNTER
    CALL_COUNTER += 1

    user_message = state.get("user_message")
    SYSTEM_PROMPT = "Your task is to determine whether the user's query is a coding-related question."

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

# Node: Solve coding question — will force error after MAX_SUCCESSFUL_CALLS
def solve_coding_question(state: State):
    user_message = state.get("user_message")

    # 🚨 FORCE ERROR after MAX_SUCCESSFUL_CALLS
    if CALL_COUNTER > MAX_SUCCESSFUL_CALLS:
        raise Exception(f"🚨 Simulated crash after {MAX_SUCCESSFUL_CALLS} successful runs!")

    SYSTEM_PROMPT = "Your task is to solve the coding question of the user."
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

# Function to run graph with error handling
def call_graph():
    state = {
        "user_message": "Explain me about Pydantic in Python",
        "ai_message": "",
        "is_coding_question": False
    }

    try:
        print("🚀 Running graph...")
        result = graph.invoke(state)
        print("✅ Success:", result["ai_message"][:100] + "...")
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