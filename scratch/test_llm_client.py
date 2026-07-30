import sys
import os

# Add workspace directory to path
WORKSPACE_DIR = r"f:\Scoutr"
sys.path.insert(0, WORKSPACE_DIR)

from agent.llm_client import call_llm
from agent import config

# Dummy tool schema for testing tool-calling support
DUMMY_WEATHER_TOOL = {
    "type": "function",
    "function": {
        "name": "get_weather",
        "description": "Get the current weather for a location",
        "parameters": {
            "type": "object",
            "properties": {
                "location": {
                    "type": "string",
                    "description": "The city and state, e.g. London, UK"
                }
            },
            "required": ["location"]
        }
    }
}


def run_tests():
    print("=== TEST 1: Primary call via Groq ===")
    messages = [{"role": "user", "content": "Respond with exactly the word 'Apple'."}]
    try:
        response = call_llm(messages)
        print(f"Response: {response}")
        if "apple" in response.get("content", "").lower():
            print("PASS: Primary call via Groq succeeded.")
        else:
            print("FAIL: Response did not contain 'Apple'.")
    except Exception as e:
        print(f"FAIL: Primary call encountered an error: {e}")

    print("\n=== TEST 2: Tool-calling via Groq ===")
    messages = [{"role": "user", "content": "What is the weather like in London, UK?"}]
    try:
        response = call_llm(messages, tools=[DUMMY_WEATHER_TOOL])
        print(f"Tool Call Response: {response}")
        if "tool_calls" in response and response["tool_calls"]:
            tool_call = response["tool_calls"][0]
            func = tool_call.get("function", {})
            print(f"Tool call name: {func.get('name')}, arguments: {func.get('arguments')}")
            if func.get("name") == "get_weather":
                print("PASS: Tool calling via Groq succeeded.")
            else:
                print("FAIL: Expected tool 'get_weather', but got something else.")
        else:
            print("FAIL: Model did not trigger a tool call.")
    except Exception as e:
        print(f"FAIL: Tool call via Groq encountered an error: {e}")

    print("\n=== TEST 3: Fallback from Groq to Gemini ===")
    # Save original Groq config
    orig_key = config.GROQ_API_KEY
    # Force Groq to fail by setting invalid key
    config.GROQ_API_KEY = "gsk_invalid_key_for_testing"
    
    messages = [{"role": "user", "content": "Respond with exactly the word 'Banana'."}]
    try:
        response = call_llm(messages)
        print(f"Response: {response}")
        if "banana" in response.get("content", "").lower():
            print("PASS: Fallback from Groq to Gemini succeeded.")
        else:
            print("FAIL: Response did not contain 'Banana'.")
    except Exception as e:
        print(f"FAIL: Fallback encountered an error: {e}")
    finally:
        # Restore Groq config
        config.GROQ_API_KEY = orig_key

    print("\n=== All Tests Completed ===")


if __name__ == "__main__":
    run_tests()
