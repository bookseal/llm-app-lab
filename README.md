# llm-app-lab

> Learning to **build with LLMs** the hands-on way — one small, working app at a time.

This is my working repo for the **KSEPT Summer Program — Building with LLMs**. I'm
going from a single API call all the way to tools, RAG, and agents, and I learn each
idea by *shipping a tiny app that proves I understand it* — not by copying answers.

Every starter app in this course ships with **intentional bugs**. The fun part isn't
making them go away; it's reproducing the failure, explaining *why* it happens, fixing
it, and reading the diff before I accept it. My `git log` is the receipt.

📚 **Learning site (my concept notes):** <https://bookseal.github.io/llm-app-lab/>
&nbsp;·&nbsp; 📑 **Full curriculum:** [TUTORIAL.md](TUTORIAL.md)
&nbsp;·&nbsp; 🧱 Stack: **Flask · React + Vite · Anthropic SDK (`claude-sonnet-4-6`)**

---

## 🔬 The hands-on builds

The stuff I actually built and broke and fixed. Each one isolates *one* LLM concept.

| Build | What it is | The concept it nails |
|---|---|---|
| **[instructor-extractor](instructor-extractor/)** | Paste a messy job post → structured fields + auto follow-up email | Forced `tool_use` **vs.** free-text generation |
| **[extract-starter](extract-starter/)** | Single-turn structured extraction template | Forced tool call **+ Pydantic validation** as a safety layer |
| **[embedding-similarity](embedding-similarity/)** | Console playground: two phrases → cosine similarity | What embeddings *measure* (cross-lingual, no API) |
| **[chat-app](chat-app/)** | Minimal Claude chat over `/api/chat` | Stateless single-turn — and the 5 gaps to production |
| **[backend](backend/) + [frontend](frontend/)** | Full-stack `Hello from Flask` | Two servers, a dev proxy, `fetch` on mount |

### ⭐ instructor-extractor — the one I extended into a real web app

Paste an instructor job post (copied from email or KakaoTalk). Claude extracts five
structured fields, flags the blanks as **⚠️ missing**, copies everything as a TSV row
for a spreadsheet, and then *drafts a polite follow-up email asking only for the
fields that are missing*.

![instructor-extractor demo](docs/assets/instructor-extractor.png)

What I find genuinely cool about it — **the same model, used two opposite ways on one
screen**:

- **Extraction = text → data.** The output is machine-readable, so I *force* the shape
  with `tool_choice={"type": "tool", "name": "record_posting"}`. Every field is
  nullable, and the system prompt says *"return null rather than guess."*
- **Email = data → text.** The output is for a human, so I drop the tool entirely and
  let Claude write free-form prose.

That contrast — *the output format decides whether you force a tool* — is the whole
lesson, and I built an app to feel it instead of just reading it.
&nbsp; → run it: [instructor-extractor/README.md](instructor-extractor/README.md)

### 🧭 embedding-similarity — building intuition for vectors

A tiny REPL: type two phrases, get their cosine similarity on a −1…1 scale. It runs a
**local multilingual model** (`paraphrase-multilingual-MiniLM-L12-v2`), so `"cat"` and
`"고양이"` score *high* across languages — no API key, no cost. Great for feeling why
`"I love this"` vs `"I hate this"` is **not** near −1 (same topic, opposite sentiment).

---

## 🗺️ The path I'm walking

I take the course's [concept map](https://bookseal.github.io/llm-app-lab/) one module
at a time: **concept note → original slides → build the starter → mini quiz.**

| # | Module | What I take from it |
|---|------|------|
| 1 | Setup | Six tools + one shared `.env` for the API key |
| 2 | Foundations | First API call, a chat app, **fixing 5 built-in bugs**, SSE streaming |
| 3 | Tools & Structure | Structured output, 4 levels: parseable → schema → tool-loop → MCP |
| 4 | Context | Indexing pipeline + RAG (chunking, embeddings, vector store, citations) |
| 5 | Architecture & Agents | A ~20-line agent loop, subagents, memory scope, multi-model |
| 6 | Production | Eval ladder, prompt-injection defense, observability |
| 7 | Workshop | Build something small enough to actually finish |

### My learning loop (why the `git log` is the point)

Each starter is **broken on purpose**. For every fix I run the same loop:

1. **Reproduce** — see the bug myself (e.g. the bot forgets the previous turn).
2. **Diagnose** — dig until I can explain the *mechanism*, not just the symptom.
3. **Fix** — tell Claude Code the *behavior I want*, ask for a plan first.
4. **Read the diff** — understand every change before accepting it.
5. **Verify** — re-run the original failure to confirm it's gone.
6. **Commit** — one commit per fix: `git commit -am "fix: <bug>"`.

→ So `git log` becomes my learning journal, and I can `git show <hash>` to walk anyone
through each fix, one diff at a time.

---

## ▶️ Run the full-stack hello-world

Two servers, so you need **two terminals**.

```bash
# Terminal 1 — backend
python -m venv .venv          # first time only
source .venv/bin/activate     # Windows: .venv\Scripts\activate
pip install -r backend/requirements.txt
python backend/app.py         # → http://localhost:5001
```

```bash
# Terminal 2 — frontend
cd frontend
npm install                   # first time only
npm run dev                   # → http://localhost:5173
```

Open **http://localhost:5173** — the page calls `/api/hello` (proxied to Flask) and
shows `Hello from Flask`. Details: [backend/README.md](backend/README.md) ·
[frontend/README.md](frontend/README.md). Each build has its own README to run it.

---

## 📒 About the learning site

The [`docs/`](docs/) folder is served at <https://bookseal.github.io/llm-app-lab/>. It's
my own **concept notes** — written in Korean (analogy-first), with English Mermaid
diagrams and instantly-graded mini quizzes for each module. The
[change log](https://bookseal.github.io/llm-app-lab/history.html) is auto-generated
from `git log` on every push to `main`
([scripts/gen_history.py](scripts/gen_history.py)).

```
.
├── instructor-extractor/  ⭐ extended web app — extract + follow-up email
├── extract-starter/          Module 3 starter — forced tool_use + Pydantic
├── embedding-similarity/     embeddings playground — cosine similarity
├── chat-app/                 minimal Claude chat
├── backend/ + frontend/      full-stack hello-world (Flask + React/Vite)
├── docs/                     my concept notes (GitHub Pages)
└── TUTORIAL.md               full curriculum reference
```
