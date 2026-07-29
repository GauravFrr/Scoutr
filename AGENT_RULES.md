# Coding Rules for This Project

These rules apply to ALL code generated for this project. Follow them strictly — do not deviate for the sake of "best practices" if it adds unnecessary complexity.

## Core Principle
Keep everything as SIMPLE as possible. This is a 2-3 hour assignment, not a production system.
If something can be done with plain Python (loops, if/else, functions, dicts), do that.
Do NOT reach for advanced patterns, design patterns, extra abstraction layers, or "enterprise" structure unless there is a clear, concrete reason.

## Specific Rules

1. **No heavy frameworks.**
   - No LangChain, LangGraph, CrewAI, AutoGen, or similar.
   - Use direct API calls to Gemini / Claude via their official SDKs or plain `requests`.
   - No smolagents unless explicitly asked for.

2. **No unnecessary object-oriented complexity.**
   - Prefer plain functions over classes unless state genuinely needs to be held (e.g. a small `Agent` class holding conversation history is fine — but don't create separate classes for every tool, every message type, etc.)

3. **File and folder naming**
   - Python files: `snake_case.py`
   - Functions: `snake_case`
   - Constants: `UPPER_SNAKE_CASE`
   - No cryptic abbreviations — full words (`read_file` not `rf`, `max_iterations` not `max_it`)

4. **Code formatting**
   - Standard PEP8 formatting.
   - Every function should have a one-line docstring explaining what it does — this docstring will also be used to describe the tool to the LLM, so make it clear and specific.
   - Keep functions short (under ~30 lines where possible). If a function is doing too much, split it.

5. **No premature error handling / logging frameworks.**
   - Simple `try/except` with a clear printed message is enough.
   - No custom logging classes, no config-driven log levels — plain `print()` statements are fine and preferred for this project (makes the demo recording easy to follow too).

6. **Comments**
   - Add short comments only where the "why" isn't obvious from the code itself.
   - Do not comment obvious lines (e.g. don't write `# increment counter` above `count += 1`).

7. **No unnecessary config files, env abstractions, or plugin systems.**
   - One `.env` file for API keys, loaded with `python-dotenv`. That's it.
   - One `config.py` with plain constants (model name, repo path, max iterations) — not a class-based settings system.

8. **Dependencies**
   - Only add a dependency if it is clearly necessary.
   - Preferred libraries: `google-generativeai` (Gemini), `python-dotenv`, `requests`. Avoid adding anything beyond this unless truly required.

9. **When in doubt, choose the more readable/obvious solution over the more "clever" one.**
   - The goal is that someone reading this code for the first time (e.g. an interviewer) understands it in under 2 minutes.

## What NOT to do
- Do not add retry-with-exponential-backoff decorators, custom exception hierarchies, dependency injection, or abstract base classes.
- Do not build a plugin/tool-registry system with decorators — a simple dict mapping tool name → function is enough.
- Do not add unit test frameworks/mocking setups unless explicitly asked — a single manual test run is enough for this assignment.
