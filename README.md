# Scoutr — Autonomous AI Coding Agent

Scoutr is an autonomous coding agent that explores an unfamiliar codebase, understands a plain-English product request, forms a plan, implements the change, and summarizes what it did — with no hardcoded knowledge of the target repository or the specific feature being requested.

This submission was built for the ConversAllabs AI Coding Agent assignment. It was run against [`node-easy-notes-app`](https://github.com/callicoder/node-easy-notes-app) with the request:

> "Improve the application so users can better organise and search their notes."

---

## Architecture

```
agent/
├── main.py           # CLI entry point — accepts a request and repo path
├── config.py          # Model list, repo path, iteration limit (plain constants)
├── llm_client.py       # LLM communication layer with fallback chain
├── agent_loop.py        # The core ReAct-style reasoning loop
└── tools.py             # File-system tools the agent can call

target-repo/            # The actual application being modified (Node.js/Express)
scratch/                 # Manual test scripts used during development
```

The design intentionally avoids agent frameworks (LangChain, smolagents, etc.). With a repo this size, a small hand-written loop is easier to reason about, easier to debug, and easier to explain — all direct OpenAI-compatible API calls via `requests`.

---

## Agent Workflow

The agent follows a simple **explore → plan → implement → summarize** loop:

1. **System prompt** tells the LLM its role, the location of the target repo, and the four tools it has access to. It is explicitly instructed to decide the implementation approach itself — no feature logic is hardcoded anywhere in the agent code.
2. On each iteration, the LLM is given the running conversation plus the four tool schemas (OpenAI-compatible `function` format) and asked what to do next.
3. If the LLM requests a tool call, the agent executes the corresponding Python function, appends the result back into the conversation, and loops again.
4. Once the LLM responds with plain text and no further tool calls, that text is treated as the final summary and the loop ends.
5. A `MAX_ITERATIONS` cap (15) prevents runaway loops.

Because the loop itself contains no notes-app-specific or feature-specific logic, the same code is expected to generalize to a new, unseen request against the same repo (as will be tested in the follow-up interview).

## Repository Exploration

The agent has four tools, each a small, isolated Python function:

| Tool | Purpose |
|---|---|
| `list_files(root_path)` | Recursively lists all files in the repo (skipping `.git`, `node_modules`, build folders), returned as paths relative to the repo root |
| `read_file(path)` | Reads a file's contents, with a 50KB size guard to avoid flooding the context window |
| `search_code(keyword, root_path)` | Grep-style keyword search across the repo, returning file + line number matches |
| `write_file(path, content)` | Writes/overwrites a file, creating parent directories as needed |

In this run, the agent used `list_files` to get an overview of the repo, then `read_file` to inspect the model, controller, and route files before writing changes — mirroring how a developer would approach an unfamiliar codebase.

## LLM Provider & Reliability

Free-tier LLM APIs are unreliable under load (rate limits, temporary overloads), so `llm_client.py` implements a two-tier fallback:

1. **Primary:** a chain of Gemini models tried in order — `gemini-2.5-flash` → `gemini-2.5-flash-lite` → `gemini-2.5-pro`
2. **Secondary:** if all Gemini models fail (rate-limited or overloaded), the client automatically falls back to **Groq** (`llama-3.3-70b-versatile`), a separate provider with an independent quota

This was not a theoretical concern — during development, all three Gemini models hit rate limits mid-run, and the agent transparently completed the task via the Groq fallback without any change to the calling code. The response format is normalized across both providers so the rest of the agent has no provider-specific logic.

## What the Agent Implemented

Given the open-ended request, the agent chose a **tags + search** approach, built across two runs:

- Added a `tags: [String]` field to the Note schema (`app/models/note.model.js`)
- Updated `create` and `update` in the controller to accept and store tags
- Added a `findByTag` controller function to retrieve all notes matching a given tag
- Added a `search` controller function to find notes by keyword in the title or content (case-insensitive)
- Registered two new routes: `GET /notes/tag/:tag` and `GET /notes/search/:keyword`

This was a reasonable, minimal interpretation of "better organise and search" for a simple notes app — tags give users a lightweight way to categorize notes, tag lookup lets them retrieve everything under a category, and keyword search covers free-text lookup across titles and content.

### API Endpoints (final)

| Method | Endpoint | Description |
|---|---|---|
| `POST` | `/notes` | Create a note (`title`, `content`, optional `tags`) |
| `GET` | `/notes` | List all notes |
| `GET` | `/notes/:noteId` | Get a single note |
| `PUT` | `/notes/:noteId` | Update a note |
| `DELETE` | `/notes/:noteId` | Delete a note |
| `GET` | `/notes/tag/:tag` | Get all notes with a given tag |
| `GET` | `/notes/search/:keyword` | Search notes by keyword in title/content |

## Assumptions & Trade-offs

- **Feature choice:** tags + keyword/tag search was chosen over more complex options (e.g. full-text indexing, categories with a separate collection) to keep the change proportional to the size of the app and within the assignment's time budget.
- **Backward compatibility:** `tags` defaults to an empty array, so existing notes created without tags continue to work unchanged.
- **Route ordering:** in an earlier iteration, the agent added a single-segment search route (e.g. `/notes/search`) *after* the existing `/notes/:noteId` route, which Express incorrectly matched as a noteId lookup since it matches routes in registration order. The final `/notes/tag/:tag` route avoids this collision (it has two path segments, so it can't be mistaken for `/notes/:noteId`), but this was only confirmed by manually testing the endpoint end-to-end rather than assuming the agent's routing was correct — a good example of why verifying the agent's output matters, not just trusting it.
- **Environment fixes required to actually run the app:** the target repo is from 2018 and pins an old Mongoose version incompatible with modern MongoDB Atlas clusters (legacy `OP_QUERY` wire protocol). Mongoose was upgraded and the deprecated `useNewUrlParser` connection option was removed to get the app running end-to-end. These were pre-existing repo issues, unrelated to the agent's own changes.
- **No automated test suite:** verification was done manually via `curl` against the running server (create with/without tags, search by keyword, search by tag) rather than writing a formal test suite, to stay within the assignment's time constraints.

## How to Run

```bash
# 1. Install agent dependencies
pip install -r requirements.txt

# 2. Set up environment variables
cp .env.example .env
# Fill in GEMINI_API_KEY and GROQ_API_KEY

# 3. Run the agent against the target repo
python agent/main.py --request "Improve the application so users can better organise and search their notes." --repo ./target-repo
```

To run the target app itself afterward:
```bash
cd target-repo
npm install
npm start
```
(Requires a MongoDB connection string in `config/database.config.js` — MongoDB Atlas free tier works.)

## Demo Recording

[Watch the demo recording](https://drive.google.com/file/d/1RLXHiCk1-4Y3o-EIL5bOnMQQB4FcAxkZ/view?usp=sharing)

---

Built by Gaurav for the ConversAllabs Software Developer assignment.