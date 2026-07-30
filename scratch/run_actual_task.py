import sys
import os

# Add workspace directory to path
WORKSPACE_DIR = r"f:\Scoutr"
sys.path.insert(0, WORKSPACE_DIR)

from agent.agent_loop import run_agent

def run():
    print("=== RUNNING ACTUAL ASSIGNMENT TASK ===")
    request = "Improve the application so users can better organise and search their notes."
    try:
        final_summary = run_agent(request)
        print("\n=== TASK COMPLETED ===")
        print("Final Agent Summary:")
        print(final_summary)
    except Exception as e:
        print(f"\nError running task: {e}")

if __name__ == "__main__":
    run()
