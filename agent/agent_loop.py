import json
import time
from agent import config
from agent.llm_client import call_llm
from agent.tools import list_files, read_file, search_code, write_file

# Dict mapping tool name -> function
TOOL_FUNCTIONS = {
    "list_files": list_files,
    "read_file": read_file,
    "search_code": search_code,
    "write_file": write_file
}

# OpenAI-compatible tool definitions
TOOL_SCHEMAS = [
    {
        "type": "function",
        "function": {
            "name": "list_files",
            "description": "Recursively list all files under the given root path, returning their relative paths.",
            "parameters": {
                "type": "object",
                "properties": {
                    "root_path": {
                        "type": "string",
                        "description": "The root directory to recursively list files in (usually config.TARGET_REPO_PATH)."
                    }
                },
                "required": ["root_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "read_file",
            "description": "Read and return the contents of the file at the given path, with a 50KB size limit.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to read (must not contain the target-repo/ prefix)."
                    }
                },
                "required": ["path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "search_code",
            "description": "Search for a keyword in files under root_path, returning matches with relative paths and line numbers.",
            "parameters": {
                "type": "object",
                "properties": {
                    "keyword": {
                        "type": "string",
                        "description": "The case-insensitive keyword or substring to search for."
                    },
                    "root_path": {
                        "type": "string",
                        "description": "The root directory to search under (usually config.TARGET_REPO_PATH)."
                    }
                },
                "required": ["keyword", "root_path"]
            }
        }
    },
    {
        "type": "function",
        "function": {
            "name": "write_file",
            "description": "Write or overwrite content to a file, creating parent directories if necessary.",
            "parameters": {
                "type": "object",
                "properties": {
                    "path": {
                        "type": "string",
                        "description": "The path to the file to write to (must not contain the target-repo/ prefix)."
                    },
                    "content": {
                        "type": "string",
                        "description": "The text content to write into the file."
                    }
                },
                "required": ["path", "content"]
            }
        }
    }
]

SYSTEM_PROMPT = f"""You are an autonomous coding agent working on a codebase located in the folder '{config.TARGET_REPO_PATH}'.
Your goal is to solve the user's request by following these steps:
1. Explore the repository first to locate relevant files.
2. Formulate a short execution plan.
3. Implement the required changes by adding/modifying files.
4. Verify the changes (if needed) and summarize what you did.

You have access to the following 4 tools:
- list_files: Lists files in the repository.
- read_file: Reads a file's content.
- search_code: Searches for a keyword in the codebase.
- write_file: Writes/overwrites a file.

Strict Constraints:
- For 'list_files' and 'search_code', you MUST always use '{config.TARGET_REPO_PATH}' as the 'root_path'.
- For 'read_file' and 'write_file', you MUST pass the file paths WITHOUT any '{config.TARGET_REPO_PATH}/' prefix. They are resolved relative to the target repository automatically.
- Do not make assumptions about codebase contents without checking; read files to understand their structure before writing changes to them.
- You MUST NOT ask the user for clarification, questions, or additional instructions. You must be completely autonomous, proactive, and independent.
- If a request is broad or open-ended, make reasonable design decisions, inspect the existing files to see how the app works, and implement a complete, end-to-end enhancement.
- Start immediately on Iteration 1 by listing all files in the repository to locate where to work.
- You MUST use the native tool calling mechanism to invoke tools. Do not output raw XML tags (like <function>...</function>) or pseudo-code function calls in your conversational response.
- Crucial: When writing JavaScript/Node.js code, you MUST use traditional function syntax (e.g., 'function(req, res) { ... }' and '.then(function(data) { ... })') and strictly avoid using ES6 arrow functions (do not write '=>'). This is required to prevent API parser issues.
- The examples below show the parameter keys and values for each tool, but you must pass them via the API's native tool-calling parameter structure.
- When you are fully done and have implemented all requested changes, respond with a final plain-text summary of your changes. Do not call any more tools in your final turn.

Tool Call Parameter Examples:
1. list_files: {{"root_path": "{config.TARGET_REPO_PATH}"}}
2. search_code: {{"keyword": "mongoose", "root_path": "{config.TARGET_REPO_PATH}"}}
3. read_file: {{"path": "app/controllers/note.controller.js"}}
4. write_file: {{"path": "app/routes/note.routes.js", "content": "const notes = require..."}}
"""

def _execute_tool(tool_call: dict, iteration: int) -> dict:
    """Execute a single tool call requested by the LLM and return the tool message."""
    tool_id = tool_call.get("id")
    func_data = tool_call.get("function", {})
    tool_name = func_data.get("name")
    args_str = func_data.get("arguments", "{}")
    
    try:
        args = json.loads(args_str)
    except Exception as e:
        args = {}
        print(f"Error parsing arguments JSON: {e}")

    print(f"  Step {iteration}: calling {tool_name}({args})")
    
    if tool_name in TOOL_FUNCTIONS:
        try:
            result = TOOL_FUNCTIONS[tool_name](**args)
        except Exception as e:
            result = f"Error executing tool {tool_name}: {e}"
    else:
        result = f"Error: Tool '{tool_name}' is not recognized."

    content_str = json.dumps(result) if isinstance(result, (list, dict)) else str(result)
    return {
        "role": "tool",
        "tool_call_id": tool_id,
        "name": tool_name,
        "content": content_str
    }

def run_agent(request: str) -> str:
    """Run the autonomous agent loop to fulfill the user's codebase request."""
    print("Initializing agent loop...")
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": request}
    ]

    for iteration in range(1, config.MAX_ITERATIONS + 1):
        print(f"\n--- Iteration {iteration} / {config.MAX_ITERATIONS} ---")
        response = call_llm(messages, tools=TOOL_SCHEMAS)
        messages.append(response)
        
        tool_calls = response.get("tool_calls")
        if not tool_calls:
            print("No tool calls requested. Final summary received.")
            return response.get("content", "")
            
        print(f"Agent requested {len(tool_calls)} tool call(s):")
        for tool_call in tool_calls:
            tool_msg = _execute_tool(tool_call, iteration)
            messages.append(tool_msg)

    print(f"Reached maximum iterations ({config.MAX_ITERATIONS}). Stopping.")
    return messages[-1].get("content", "Agent stopped due to iteration limit.")
