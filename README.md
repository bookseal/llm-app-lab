# llm-app-lab

> **A live, interactive course on building with LLMs — that I built *while learning it*.**
> Not a folder of exercises: a hosted teaching site with animated concept notes, instant
> quizzes, and apps you can boot from inside the page on demand.

### ▶ See it live

| | |
|---|---|
| 🎓 **The course** | **<https://llm-app-lab.bit-habit.com/>** — concept notes, animated diagrams, per-module quizzes |
| 🖥️ **Run a real app in the browser** | [Module 5 · data-analyst agent](https://llm-app-lab.bit-habit.com/05D-agent.html) → press **▶ Run it live** and a real agent boots and answers, embedded in the page |
| ⚙️ **How that works** | [launcher.html](https://llm-app-lab.bit-habit.com/launcher.html) — a static page that spins up Kubernetes pods on demand |
| 🧾 **The receipts** | [auto-generated change log](https://llm-app-lab.bit-habit.com/history.html) straight from `git log` |

I'm going through the **KSEPT Summer Program — Building with LLMs** (single API call →
tools → RAG → agents). Instead of taking notes into a drawer, I turned the whole thing
into a **product**: a teaching site I'd actually want to learn from, and the
infrastructure to let anyone *run* the examples without installing anything. This repo
is both the coursework and the platform.

🧱 Stack: **Flask · React + Vite · Anthropic SDK (`claude-sonnet-4-6`)** · **Mermaid + anime.js** for the visuals · **k3s (Kubernetes) + Traefik + cert-manager** for hosting and on-demand app instances.

---

## What I sweated over (the portfolio bits)

The code is the easy part. These are the things I actually spent design thought on —
and what I'd want a fellow educator or engineer to look at first.

### 1 · Teaching as a craft, not a dump of notes

The [learning site](https://llm-app-lab.bit-habit.com/) is written the way I wish
courses were: **Korean, analogy-first prose** for intuition, **English diagrams** for
precision, and an **instantly-graded quiz** at the end of every section so a reader
finds out immediately whether the idea landed. 96 diagrams across the site, each one
built to make *one* concept click.

Every diagram is **colored by shape, not by hand** — the shared renderer infers a
node's role from its geometry (a cylinder is a store, a rhombus is a decision) and
colors it, so the whole site stays visually consistent and an author only has to pick
the right shape. Details in the [Visualization stack](#visualization-stack) appendix.

### 2 · Animations that *encode meaning*, never decorate

I built a small animation layer (`anime.js`) on top of Mermaid where every motion
carries information, and **nothing auto-plays a walkthrough** (I want the reader to set
the pace):

- a **green ball tours the common path** of a flow forever, and turns **yellow** when
  it takes a special-case branch — so "the loop is the engine" is something you *watch*,
  not just read ([agent loop](https://llm-app-lab.bit-habit.com/05D-agent.html));
- a **frozen node sits still and desaturated while a trained node breathes** — the
  "only the small head learns" idea, made visual ([fine-tuning](https://llm-app-lab.bit-habit.com/05B-finetune.html));
- a **dimension-mismatch widget** shakes and truncates bars to show why a robot policy
  trained on the wrong body produces meaningless motion ([VLA](https://llm-app-lab.bit-habit.com/05C-vla.html)).

### 3 · Run real apps from a static page — ephemeral, on demand

A documentation page can't start a server. So I built a **launcher**: a ~120-line
service that scales a **Kubernetes deployment 0 → 1 on demand**, waits until it's
ready, and the page **embeds the running app in an iframe right where you're reading**.
Idle apps are **scaled back to zero automatically** after 20 minutes — the same
"ephemeral, spin-up-for-a-test, tear-down-after" idea as a throwaway preview deploy,
but self-hosted on my own k3s cluster.

The agent app has no web UI of its own (it's a terminal REPL), so its container serves
the **real terminal over the web** via `ttyd` — the browser gets the exact session a
student would get locally. Security mirrors the lesson it teaches: the launcher's
Kubernetes role can *only* scale that one deployment — it can't read secrets or create
pods (same "don't hand out the dangerous capability" principle as the read-only SQL
agent). → [`infra/`](infra/) · [how-it-works page](https://llm-app-lab.bit-habit.com/launcher.html)

### 4 · Learning by breaking, with the `git log` as the journal

Every starter app ships with **intentional bugs**. I don't just make them go away — I
reproduce the failure, explain the *mechanism*, fix it, and read the diff before
accepting it. One commit per fix, so `git log` is a walkable learning journal and
`git show <hash>` narrates any single fix.

---

## The hands-on builds

Each build isolates *one* LLM concept — small enough to fully understand, real enough
to break. They're the evidence behind the concept notes above.

| Build | What it is | The concept it nails |
|---|---|---|
| **[Module_02_chat-app](Projects/Module_02_chat-app/)** | Minimal Claude chat over `/api/chat` | Stateless single-turn — and the gaps to production |
| **[Module_03_extractor/starter](Projects/Module_03_extractor/starter/)** | Single-turn structured extraction template | Forced tool call **+ Pydantic validation** as a safety layer |
| **[Module_03_extractor/webapp](Projects/Module_03_extractor/webapp/)** ⭐ | Messy job post → structured fields + auto follow-up email | Forced `tool_use` **vs.** free-text generation |
| **[Module_04_rag](Projects/Module_04_rag/)** | Cited answers over a 14 CFR (FAA) corpus | Chunking · embeddings · vector store · citations |
| **[Module_04_embedding-similarity](Projects/Module_04_embedding-similarity/)** | Two phrases → cosine similarity (local, no API) | What embeddings *measure* (cross-lingual) |
| **[Module_05B_finetune](Projects/Module_05B_finetune/)** | Route support tickets to 6 teams, three ways | Zero-shot → few-shot → **distilled classifier** (F1 compared) |
| **[Module_05C_data-agent](Projects/Module_05C_data-agent/)** | Ask a SQLite DB in English; it writes read-only SQL | The ~20-line **agent loop** + read-only-by-construction safety |

### ⭐ Module_03_extractor/webapp — one model, two opposite jobs on one screen

Paste an instructor job post (copied from email or KakaoTalk). Claude extracts five
structured fields, flags blanks as **⚠️ missing**, copies everything as a TSV row for a
spreadsheet, then *drafts a polite follow-up email asking only for the missing fields*.

![instructor-extractor demo](docs/assets/instructor-extractor.png)

The lesson I built an app to *feel*: **the output format decides whether you force a tool.**

- **Extraction = text → data.** Machine-readable, so I *force* the shape with
  `tool_choice={"type": "tool", "name": "record_posting"}`; every field is nullable and
  the prompt says *"return null rather than guess."*
- **Email = data → text.** For a human, so I drop the tool and let Claude write prose.

&nbsp; → run it: [Projects/Module_03_extractor/webapp/README.md](Projects/Module_03_extractor/webapp/README.md)

### 🔎 Module_04_rag — single-shot vs. agentic, side by side

Ask one question about 14 CFR (FAA regs) and it answers *twice*: **single-shot**
retrieves once (gaps show up as honest "Not specified" cells); **agentic** keeps
searching until it has every part, then fills the same table with §-cited sources. The
lesson isn't chunking — it's **one retrieval vs. a retrieval loop, and the recall you
buy with more tokens.** Showing both columns *is* the point.

![Module_04 RAG — single-shot leaves Class B/C blank; the agentic loop runs 3 more searches and fills every cell with §-cited sources, at a visible token/cost trade-off](docs/assets/module-04-rag.png)

&nbsp; → run it: [Projects/Module_04_rag/rag-starter/README.md](Projects/Module_04_rag/rag-starter/README.md)

### 🧭 Module_04_embedding-similarity — intuition for vectors

A tiny REPL: type two phrases, get cosine similarity on a −1…1 scale, using a **local
multilingual model** (`paraphrase-multilingual-MiniLM-L12-v2`) — so `"cat"` and
`"고양이"` score *high* across languages, and `"I love this"` vs `"I hate this"` is
**not** near −1 (same topic, opposite sentiment). No API key, no cost.

![Module_04 embedding-similarity — cat↔고양이 0.989 (cross-lingual), love↔hate 0.530 (same topic), stock-market↔photosynthesis −0.115 (unrelated)](docs/assets/module-04-embedding.png)

### 💬 Module_02_chat-app — the smallest thing that talks to Claude

React + Flask, one endpoint, one `client.messages.create` call. Deliberately bare: run
it, read it, and name what production still needs (memory, streaming, error handling).

![Module_02 chat-app — a live Claude reply rendered over /api/chat](docs/assets/module-02-chat.png)

---

## The curriculum path

I take the course one module at a time — **concept note → original slides → build the
starter → mini quiz** — and each module's project page lives on the site.

| # | Module | What I take from it |
|---|------|------|
| 1 | Setup | Six tools + one shared `.env` for the API key |
| 2 | Foundations | First API call, a chat app, **fixing built-in bugs**, SSE streaming |
| 3 | Tools & Structure | Structured output, 4 levels: parseable → schema → tool-loop → MCP |
| 4 | Context | Indexing pipeline + RAG (chunking, embeddings, vector store, citations) |
| 5 | Architecture & Agents | A ~20-line agent loop; 3 project deep-dives: fine-tuning, VLA, data-agent |
| 6 | Production | Eval ladder, prompt-injection defense, observability |
| 7 | Workshop | Build something small enough to actually finish |

Full curriculum reference: [TUTORIAL.md](TUTORIAL.md).

---

## Repo layout & running locally

```
.
├── Projects/                          one folder per build (each has its own README)
│   ├── Module_02_chat-app/            minimal Claude chat (/api/chat)
│   ├── Module_03_extractor/           forced tool_use + Pydantic → web app
│   ├── Module_04_rag/                 RAG over a 14 CFR corpus (starter + eval harness)
│   ├── Module_04_embedding-similarity/ embeddings playground — cosine similarity
│   ├── Module_05B_finetune/           distill Claude → a tiny local ticket classifier
│   └── Module_05C_data-agent/         ~20-line agent loop over a read-only SQLite DB
├── docs/                              the teaching site (Mermaid + anime.js + quizzes)
├── infra/                             the "Run it live" launcher (Flask + k8s manifests)
└── TUTORIAL.md                        full curriculum reference
```

Each build is self-contained. The general shape (Python projects):

```bash
cd Projects/<Module_..>          # e.g. Projects/Module_05B_finetune
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt  # then follow that project's README
```

The API key comes from one shared `.env` (`ANTHROPIC_API_KEY`). React-frontend projects
(`Module_02_chat-app`, `Module_04_rag`) run the backend and `npm run dev` in two
terminals — see their READMEs. Or skip setup entirely and press **▶ Run it live** on the
project's page.

---

## Visualization stack

*How the diagrams are drawn and animated — the technical appendix to
["What I sweated over"](#what-i-sweated-over-the-portfolio-bits).*

Two libraries, both loaded as ES modules straight from the jsDelivr CDN (no build step,
no `node_modules`). A page never touches them directly — it only writes
`<div class="mermaid">` blocks and a few `data-*` attributes, and loads **four shared
scripts** that do the work in one place:

| File | Library | Responsibility |
|---|---|---|
| [`docs/mermaid-fx.js`](docs/mermaid-fx.js) | `mermaid@11` (ESM) | Renders every `.mermaid` block; dark theme; **shape-based auto-coloring**; the reveal animation; the `core` glow; a `▶` replay button. Fires a `mermaid-fx:done` event when SVGs exist. |
| [`docs/flow-anim.js`](docs/flow-anim.js) | `animejs@4` (ESM) | Waits for `mermaid-fx:done`, then adds the meaning-encoding motion (below). Degrades gracefully if the CDN import fails; honors `prefers-reduced-motion`. |
| [`docs/style.css`](docs/style.css) | — | Every class the two scripts use (`.mermaid`, `.flowdot`, `.fnode-*`, `.fx-*`, …) lives here once. |
| [`docs/nav.js`](docs/nav.js) | — | The two-part sidebar rail (modules 1–7 + indented projects on top, current page's sections with scroll-spy below). |

**Colored by *shape*, not by hand:**

| Mermaid shape | Role | Color |
|---|---|---|
| `["…"]` plain box | a step (io) | blue |
| `{"…"}` rhombus | a choice / decision | purple |
| `[("…")]` cylinder | a store (data) | amber |
| `(["…"])` stadium / circle | start or end | green |

A node tagged `class X core;` gets a pulsing green glow to mark the key node.

**Animations (declared with `data-*`, no per-page JS):**

| Effect | Attribute | What it shows | Used in |
|---|---|---|---|
| Touring ball | `data-flow="pulse-path" data-cycle="A,B,C"` (+ optional `data-alt="B,X"`) | A **green** dot tours the common path; turns **yellow** on a special-case branch, then back to green | 5B, 5C, 5D, launcher |
| Freeze / train | `data-flow="freeze-train" data-frozen="EMB" data-trained="HEAD"` | Frozen node desaturated & still, trained node breathing | 5B (MiniLM vs LR head) |
| Text → vector | `<div class="fx-morph" data-text="…" data-dims="8">` | A string collapses into a bar-vector — embedding intuition | 5B |
| Dim mismatch | `<div class="fx-mismatch" data-model="6" data-sim="14">` | Model outputs N bars vs sim's M slots; extras shake red & get cut, gaps zero-pad | 5C |

The full authoring contract (node-ID rules, attribute reference) lives in
[`TASK-05-projects-enrich.md`](TASK-05-projects-enrich.md); the change log is
auto-generated from `git log` on every push to `main`
([scripts/gen_history.py](scripts/gen_history.py)).
