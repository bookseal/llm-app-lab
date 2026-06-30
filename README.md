# llm-app-lab

**KSEPT Summer Program — Building with LLMs** practice repo.
A hands-on lab: start from a single LLM API call, then build up through tool use,
RAG, agents, and production — learning by building real LLM apps yourself.

> 📚 **Learning site (GitHub Pages): <https://bookseal.github.io/llm-app-lab/>**
> Concept notes + Mermaid diagrams + per-module quizzes. It re-organizes the
> original slides ([ksetp.netlify.app](https://ksetp.netlify.app/)) around *how
> things actually work*.
>
> 📑 **Full curriculum in one file:** [TUTORIAL.md](TUTORIAL.md) — all 7 modules, with code.

## What's in this repo

```
.
├── backend/             Flask API (GET /api/hello)      — full-stack hello-world
├── frontend/            React + Vite app (fetch on mount) — full-stack hello-world
├── extract-starter/     Module 3 starter — structured extraction (forced tool_use + Pydantic)
├── instructor-extractor/ Module 3 extension — instructor-posting extraction web app
├── docs/                learning site source (served via GitHub Pages)
├── scripts/             docs generation scripts
├── .github/             Pages build workflow
└── TUTORIAL.md          full curriculum reference
```

The root `backend/` + `frontend/` are the Module 2 full-stack hello-world. The
per-module example apps (chat-app, rag-starter, agent-app, etc.) each come as
their own starter zip.

## A built-from-scratch example — instructor-extractor (Module 3)

This extends Module 3's (Tools & Structure) `extract-starter` into **a real web app**.
Paste an instructor job post (copied from email or chat) → it extracts structured
fields, flags **empty fields with ⚠️ missing**, and even drafts a **follow-up email**
that asks for the missing details.

![instructor-extractor demo](docs/assets/instructor-extractor.png)

- **Both directions of LLM use on one screen** — extraction (text → data, forced
  `tool_choice`) + generation (data → text, free-form).
- **Incremental development** — UI mockup first → fake data → real Claude extraction
  → add fields one at a time.
- Stack: single Flask server. See [instructor-extractor/README.md](instructor-extractor/README.md) to run it.

## How to study this

### 1. One module at a time, in order

Use the learning site's [concept map](https://bookseal.github.io/llm-app-lab/) as
your table of contents. For each module, go **concept note (docs) → original slides
→ starter-app practice → mini quiz**.

| # | Module | One line |
|---|------|------|
| 1 | Setup | Install 6 tools + save your API key once in a shared `.env` |
| 2 | Foundations | First API call, chat app, **fix 5 built-in bugs**, SSE streaming |
| 3 | Tools & Structure | 4 steps to structured output: parseable → schema → tool-loop → MCP |
| 4 | Context | Indexing pipeline + RAG (chunking, embeddings, vector store, citations) |
| 5 | Architecture & Agents | ~20-line agent loop, subagents, memory scope, multi-model |
| 6 | Production | Eval ladder, prompt-injection defense, observability |
| 7 | Workshop | Build something small enough to finish |

### 2. The "learning loop" this course teaches

Each module's starter has **intentional bugs**. The point isn't to copy the answer —
it's to run this loop:

1. **Reproduce** — see the bug with your own eyes (e.g. the bot forgets the previous turn).
2. **Diagnose** — dig until you can explain *why* it happens.
3. **Fix** — tell Claude Code the *behavior you want*, not the implementation, and ask for a plan first.
4. **Read the diff** — understand what changes before you accept it.
5. **Verify** — re-run the failure from step 1 to confirm it's fixed.
6. **Commit** — `git commit -am "fix: <bug>"`. One commit per fix.

→ Then your `git log` becomes **your learning journal**. When presenting, `git show <hash>`
lets you "walk the diff" commit by commit and explain each fix.

### 3. When you're stuck

- Concept not clicking? → Start with that module's note on the learning site (analogy-first + Mermaid).
- "The server is up but it doesn't work"? → Don't trust the startup log — **send a real
  request to the endpoint** and judge by the status code and response body (`curl -i ...`).

## Run locally (full-stack hello-world)

There are two servers, so you need **two terminals**.

### Terminal 1 — backend

```bash
python -m venv .venv          # first time only
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
python backend/app.py         # serves on http://localhost:5001
```

### Terminal 2 — frontend

```bash
cd frontend
npm install                   # first time only
npm run dev                   # serves on http://localhost:5173
```

Open **http://localhost:5173** — the page calls `/api/hello` (proxied to Flask)
and shows `Hello from Flask`.

For details, see [backend/README.md](backend/README.md) and [frontend/README.md](frontend/README.md).

## Learning site & change log (GitHub Pages)

The [`docs/`](docs/) folder is served at **<https://bookseal.github.io/llm-app-lab/>**.

- **Concept map** (`docs/index.html`): a multi-page learning site linking each
  module's note (setup · foundations · chat-app · tools · context · agents ·
  production · workshop). Korean explanations + English Mermaid diagrams +
  instantly-graded mini quizzes.
- **Change log** (`docs/history.html`): auto-generated on every push to `main` —
  GitHub Actions reads `git log` ([scripts/gen_history.py](scripts/gen_history.py),
  workflow at [.github/workflows/pages.yml](.github/workflows/pages.yml)).

To preview the history page locally:

```bash
python3 scripts/gen_history.py   # generates docs/history.html (inside a git repo)
```
