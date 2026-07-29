# Execution Plan — AI Coding Agent (ConversAllabs Assignment)

## Goal
Build a Python-based AI agent that:
1. Explores an existing codebase (`node-easy-notes-app`)
2. Understands a plain-English product request
3. Creates a short execution plan
4. Modifies the codebase to implement it
5. Summarizes what it changed

The agent must be **generic** — it should work for ANY reasonable product request on this repo, not just "organize and search notes". It will be tested live with a new, unseen request in the follow-up interview.

---

## Phase 0: Setup
- [ ] Clone `https://github.com/callicoder/node-easy-notes-app` into `./target-repo/`
- [ ] Create a new folder `./agent/` for our agent code (separate from target repo)
- [ ] Set up `.env` file with `GEMINI_API_KEY` and fallback API key (e.g. `OPENROUTER_API_KEY` or Claude key)
- [ ] Create `requirements.txt` with minimal deps only (e.g. `google-generativeai`, `python-dotenv`, `requests`)

---

## Phase 1: Tools Layer (`agent/tools.py`)
Build simple, isolated functions the agent (LLM) can call:

- `list_files(root_path: str) -> list[str]`
  Recursively lists files in the target repo (skip `node_modules`, `.git`, build folders).

- `read_file(path: str) -> str`
  Reads and returns file content (with basic size guard, e.g. skip files >50kb).

- `search_code(keyword: str, root_path: str) -> list[dict]`
  Simple grep-like search across files, returns matching file + line number.

- `write_file(path: str, content: str) -> str`
  Writes/overwrites a file. Should create parent dirs if needed. Return confirmation string.

Each tool should:
- Have a clear docstring (used to generate the tool schema for the LLM)
- Return plain strings/lists — no complex objects
- Fail gracefully (return an error message string, don't crash the whole agent)

---

## Phase 2: LLM Client Layer (`agent/llm_client.py`)
- Single function: `call_llm(messages, tools) -> response`
- Primary: Gemini free tier (function calling / tool use API)
- Fallback: second free cloud model (e.g. OpenRouter free tier or Claude) — if Gemini call fails or rate-limits, automatically retry with fallback
- Keep the interface identical regardless of provider, so `agent_loop.py` doesn't care which one answered

---

## Phase 3: Agent Loop (`agent/agent_loop.py`)
This is the core "brain":

1. Build a system prompt explaining:
   - The agent's role (autonomous coding agent)
   - The available tools
   - The target repo path
   - Instruction to first explore, then plan, then implement, then summarize
2. Loop:
   - Send conversation + tool definitions to LLM
   - If LLM requests a tool call → run it, append result to conversation, continue loop
   - If LLM says it's done → break and return final summary
3. Add a max iteration limit (e.g. 15) to avoid infinite loops
4. Log every step to console (which tool, what args, what result) — this makes the demo recording easy and shows "reasoning" transparently

---

## Phase 4: Entry Point (`agent/main.py`)
- Accepts a request via CLI argument or hardcoded string, e.g.:
  `python main.py --request "Improve the app so users can better organise and search their notes." --repo ./target-repo`
- Calls `agent_loop.py`
- Prints final summary of changes made

---

## Phase 5: Test Run
- [ ] Run the agent with the actual assignment request
- [ ] Verify it produces a reasonable implementation (e.g. tags/categories + search filter)
- [ ] Verify existing notes app functionality still works (manually check add/edit/delete notes still work)
- [ ] Fix any bugs in tool execution or loop logic

---

## Phase 6: Documentation
- [ ] Write final `README.md` for the agent repo covering:
  - Architecture overview (with the file structure above)
  - Agent workflow (explore → plan → implement → summarize)
  - How repo exploration works
  - Assumptions and trade-offs made
  - How to run it
- [ ] Record a 2–3 min screen recording: show the command being run, the agent's step-by-step reasoning/tool calls in the console, and the final code change in the notes app
- [ ] Push agent code to a new public GitHub repo
- [ ] Upload recording to Google Drive, get shareable link

---

## Important Constraints (keep in mind throughout)
- Do NOT hardcode logic specific to "tags" or "search" anywhere in the agent loop — the LLM must decide the implementation approach dynamically based on the request text and repo contents.
- Do NOT rewrite the target repo in Python — it stays Node.js/JS, the agent only edits/adds files within it.
- Keep total build time within 2–3 hours — favor simple, working code over polished abstractions.
