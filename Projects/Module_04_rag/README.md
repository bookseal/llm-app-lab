# RAG over the U.S. Federal Aviation Regulations (14 CFR)

> A citation-grounded RAG chat over **~1,297 pages of U.S. federal aviation law**, built for an
> in-course RAG tournament — **graded 9/10 by the instructor, the top score in the class**
> (Larry Arnstein — CTO @ Clause; ex-Apple, Impinj, Xnor.ai; former UW faculty).
> Every retrieval choice was picked by **measurement, not vibes**: a 45-config overnight grid
> search, a blind holdout set, and a token budget treated as a first-class metric.

**Live demo:** press ▶ Run it live on the [course page](https://llm-app-lab.bit-habit.com/04B-rag.html) ·
**Results:** [experiments/leaderboard.md](experiments/leaderboard.md) · [experiments/prompt_leaderboard.md](experiments/prompt_leaderboard.md)

---

## Why this corpus is hard

14 CFR is not a friendly wiki dump. Six government PDFs (Parts 1–59, 61, 67, 71, 73, 91) full of:

- **Cross-references** — Class B airspace *operating* rules live in §91.131, not in Part 71
  where the airspace is *designated*. A question that looks like "one lookup" often needs
  passages from two Parts.
- **§-structure that punishes naive chunking** — a fixed 1000-char chunker slices clauses
  mid-sentence; the answer to a practice question sat in clause (a)(1)(iv), *late* in its
  section, where front-truncation silently drops it.
- **Tables and GPO running headers** that wreck PDF text extraction.
- **A domain where hallucination is dangerous** — an invented fuel-reserve minimum is not a
  cosmetic bug.

## Architecture (the deployed champion)

```
6 CFR PDFs ──PyMuPDF + §-tagging──► documents/*.md   (<!-- §91.151 | part91 --> markers,
     │                                                canary gate: build fails if part91
     │                                                tags < 50 sections)
     ▼
one chunk per §-section ──bge-large-en-v1.5 (local)──► index.pkl (+ model-stamp sidecar)
     ▼
dense vector search, K=5
     ▼
select_context(): oversized § hits split into ~500-char windows,
re-ranked against the query, kept under a fixed char budget
     ▼
claude-sonnet-4-6 · max_tokens=700 · grounding prompt ──► answer with §-cited sources
```

Every box above beat its alternatives on the leaderboard — none of it was assumed:

| Decision | Beat | Evidence |
|---|---|---|
| §-boundary chunking | fixed 1000-char chunks | coverage ~0.86 vs ~0.41 — the single biggest win |
| `bge-large-en-v1.5` (local, $0) | MiniLM / e5-large / gte-large | best MRR at equal recall |
| plain vector, K=5 | hybrid (BM25+vector), K=8 | 0.045 less coverage, **~38% cheaper**, better MRR (0.718) |
| window re-rank over front-truncation | keep-the-front-N | worst question: **15,482 → 2,256 input tokens** with the right clause surviving |

Deployed config: `section / bge / vector / K5` — **recall 0.909 · coverage 0.818 · MRR 0.718**
on the blind holdout. The tie-break rule that picked it: *when quality is within noise, take
the cheaper, simpler config.*

## The evaluation harness (the actual weapon)

Most contest entries were tuned by eyeballing 5 practice questions. This one was tuned by a
harness ([`harness/`](harness/)) that ran **45 retrieval configs overnight** — chunking ×
embedding model × retrieval method × K — against a **14-question blind holdout**
([`holdout.jsonl`](holdout.jsonl)) with `tune`/`final` splits, cross-Part questions,
out-of-scope questions, and a prompt-injection probe where *refusing* is the correct answer.

Three graders, ordered by cost:

1. **Code, free** — coverage (set-based: found §s ÷ expected §s), recall@K, and MRR, so
   multi-answer questions can't score full marks on half an answer.
2. **Code, free** — program citation verification: does the cited § actually appear in the
   cited chunk? Fabricated citations get caught mechanically, no LLM involved.
3. **LLM judge, last** — rubric scoring (1–5) with the judge model deliberately separated
   from the generation model to avoid self-grading bias. Only the finalists get this far.

The orchestrator ([`harness/orchestrate.py`](harness/orchestrate.py)) nests its loops so the
expensive work stays outer: each index (chunking × embedding) is built once, then every
retrieval method × K combination sweeps it in memory for free. Runs append to JSONL — crash-tolerant, resumable, and the
leaderboards are regenerated from it, never hand-edited. Three configs died overnight to
memory pressure; the leaderboard says so — *"never scored, never faked."*

## Tokens as a first-class metric

The contest rubric put 15/100 points on cost management, so cost was measured, not estimated:

- **91–96% of per-answer cost is input tokens** (K × passage size) — so K and context
  selection, not output length, are the real levers.
- The K=5 champion spends **10,802 tokens** per holdout sweep vs 17,284 for K=8 — that's the
  "~38% cheaper" above, bought for 0.045 coverage.
- The system prompt itself was A/B/C tested ([`prompt_leaderboard.md`](experiments/prompt_leaderboard.md)):
  the balanced variant won 4.93/5; the "warm" variant *lost* points because verbosity hit the
  `max_tokens` ceiling and truncated answers.

## The agentic loop that didn't ship — on purpose

[`harness/agent_rag.py`](harness/agent_rag.py) gives the model a `search_cfr` tool and lets
*it* drive retrieval — and on broad multi-Part questions it recovers passages single-shot
retrieval misses. Measured cost of that quality:

| Variant | Tokens (broad question) |
|---|---|
| Agentic, unbounded | **81,320** (13 searches — history grows ~quadratically) |
| Agentic, hard-capped at 3 searches | 15,954 |
| Agentic, specific question | 4,282 |
| **Single-shot (deployed)** | **~2,256** |

Single-shot already answered the hard holdout questions correctly, so it shipped; the agentic
loop stays here as a documented experiment. Two portable lessons from building it:

- **The cap is the design.** `MAX_SEARCHES = 3` is the cost lever, not a footnote — each
  search is re-sent in the conversation history, so unbounded search cost grows quadratically.
- **Don't withdraw the tool mid-loop.** Removing the tool once the budget was spent made the
  model return empty turns. Keeping the tool and answering further calls with a
  *"budget reached — answer now"* `tool_result` is what actually works.

## Map of this folder

| Path | What it is |
|---|---|
| [`CONTEST.md`](CONTEST.md) | The official contest spec: corpus, rubric (100 pts), tournament format *(Korean)* |
| [`STRATEGY.md`](STRATEGY.md) | The battle plan written the night before: rubric analysis → architecture → overnight experiment design *(Korean)* |
| [`EXPERIMENTS.md`](EXPERIMENTS.md) | The experiments runbook: why free axes get a wide grid and paid axes get greedy search *(Korean)* |
| [`DESIGN.md`](DESIGN.md) | Chat-UI design system — sectional-chart palette, terracotta reserved for § citations *(Korean)* |
| [`holdout.jsonl`](holdout.jsonl) | The 14-question blind eval set (tune/final split, adversarial + out-of-scope included) |
| [`harness/`](harness/) | Extraction, retrieval, orchestrator, scorers, agentic experiment — with tests |
| [`experiments/`](experiments/) | Auto-generated leaderboards (retrieval + prompt) |
| [`rag-starter/`](rag-starter/) | The running app: Flask backend, React frontend, Streamlit variant, indexer |
| [`todo/`](todo/) | Dated build logs — the decisions above, recorded as they happened |

## Run it

```bash
cd rag-starter
python3.11 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt          # needs ANTHROPIC_API_KEY in ../.env
python indexer.py                        # builds index.pkl with the champion config
python backend/app.py                    # Flask API — then `npm run dev` in frontend/
# or the one-process variant:
streamlit run streamlit_app.py
```

Or skip setup: the [course page](https://llm-app-lab.bit-habit.com/04B-rag.html) boots the
Streamlit app on demand (k3s scale-to-zero) and embeds it in the page.
