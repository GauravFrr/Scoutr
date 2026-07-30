import sys
import os

# Add workspace directory to path
WORKSPACE_DIR = r"f:\Scoutr"
sys.path.insert(0, WORKSPACE_DIR)

from agent.agent_loop import run_agent

def run_tests():
    print("=== Testing Agent Loop ===")
    request = "List all files in target-repo, then read package.json, and summarize the name field of the project."
    
    try:
        final_summary = run_agent(request)
        print("\n=== AGENT LOOP COMPLETED SUCCESSFULLY ===")
        print("Final summary produced by agent:")
        print(final_summary)
    except Exception as e:
        print(f"\nFAIL: Agent loop failed with error: {e}")

if __name__ == "__main__":
    run_tests()
