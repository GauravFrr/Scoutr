import argparse
import sys
import os

# Add parent directory to path so imports work correctly
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from agent import config
from agent.agent_loop import run_agent

def main():
    parser = argparse.ArgumentParser(description="Run the Scoutr autonomous coding agent.")
    parser.add_argument("--request", type=str, required=True, help="The prompt or request for the agent to complete.")
    parser.add_argument("--repo", type=str, default="./target-repo", help="Path to the target repository codebase.")
    
    args = parser.parse_args()
    
    # Configure TARGET_REPO_PATH in config module
    config.TARGET_REPO_PATH = args.repo
    
    print(f"Starting agent on repository: {config.TARGET_REPO_PATH}")
    print(f"Request: {args.request}")
    
    try:
        final_summary = run_agent(args.request)
        print("\n=== AGENT LOOP COMPLETED ===")
        print(final_summary)
    except Exception as e:
        print(f"Error running agent loop: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
