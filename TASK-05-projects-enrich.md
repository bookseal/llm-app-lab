# TASK-05 · Enrich the three Module-5 project pages (5B / 5C / 5D)

Instruction file for Opus worker agents. **Task 0 is the shared foundation and must
land first** (done by the orchestrator). Tasks 1–3 are per-page enrichment briefs
that can run **in parallel** — each agent edits **exactly one file** and nothing else.

## Why

5B (261 lines), 5C (384), 5D (143) are thin next to the reference-quality 4B (907).
A reader must be able to travel the full arc **concept → code scaffold → runtime
flow → the code itself**. The flow is taught with *function-name-level* mermaid
diagrams animated by a shared anime.js layer — every animation must **encode
meaning**, never decorate: motion = data flow · repetition = loop · contrast =
frozen/trained · disruption = mismatch.

## Ground truth (read these before writing a single line)

| Page | Project source (READ IT — all excerpts must come from here) |
|---|---|
| 5B `docs/05B-finetune.html` | `/private/tmp/claude-501/-Users-chan-workspace-llm-app-lab/f0e12884-3011-4e12-85d8-86521a517dd8/scratchpad/finetune/` — `common.py`(129) · `stage0_zeroshot.py`(34) · `stage1_fewshot.py`(46) · `stage2_finetune.py`(75) · `evaluate.py`(92) · `data/` · `README.md` |
| 5C `docs/05C-vla.html` | `/private/tmp/claude-501/-Users-chan-workspace-llm-app-lab/9a9f2808-d591-446f-9700-ebd93d19a64e/scratchpad/robot/` — `run_demo.py`(206) · `check_setup.py`(100) · `README.md` |
| 5D `docs/05D-agent.html` | `/private/tmp/claude-501/-Users-chan-workspace-llm-app-lab/f0e12884-3011-4e12-85d8-86521a517dd8/scratchpad/agent-app/` — `agent.py`(116) · `tools.py`(106) · `build_db.py`(181) · `README.md` |

Reference page for depth/quality/tone: `docs/04B-rag.html`.
Shared systems (USE, never re-implement): `docs/mermaid-fx.js`, `docs/flow-anim.js`
(built by Task 0), `docs/style.css`, `docs/nav.js`, `docs/run.js`.

## Hard rules (all tasks)

1. **Edit only your assigned page file.** Never touch `nav.js`, `style.css`,
   `mermaid-fx.js`, `flow-anim.js`, other pages, or git (no commits — the
   orchestrator reviews and commits).
2. **Mermaid diagram content is English** (memory rule). Body prose is Korean,
   같은 톤 유지: 친근한 해요체, `<strong>`로 핵심어 강조, 4B/기존 5C 문체.
3. **No inline mermaid/anime initialization.** The page `<head>` already loads
   `mermaid-fx.js` and `flow-anim.js`; you only write `<div class="mermaid">`
   blocks and `data-flow` attributes.
4. **No autoplay.** Step-through effects advance on user click only
   (learning-pace rule: 천천히, 한 개념씩).
5. Keep every existing section **id** (anchors are linked from nav.js and other
   pages). You may add new sections with new ids; update the page's own `<nav
   class="toc">` to match. Renumber section headings coherently (5X.1 … 5X.n).
6. Code excerpts must be **verbatim from the ground-truth source** (trim
   uninteresting middles with `# …`), never invented. Keep each excerpt ≤ 25 lines.
7. Every quiz targets one named misconception (listed per brief). Use the
   existing `.quiz` markup + the page's existing quiz `<script>` (keep it at the
   bottom; it already handles all `.quiz` blocks).
8. Mermaid node IDs must be **distinct, ≥3 chars, UPPERCASE** (e.g. `ASK`,
   `DISPATCH`) — `flow-anim.js` finds nodes by `[id*="-<ID>-"]`.
9. Loop-back edges in flow diagrams are **dotted** (`-.->`) — visual convention
   for feedback, and what `pulse-path` rides on when no `data-cycle` is given.
10. Target size ~600–900 lines per page. Depth over padding: every added block
    must teach something the page didn't already say.

## The animation vocabulary (`flow-anim.js` — usage API)

Attach via attributes on the `.mermaid` box (effects compose, space-separated):

```html
<div class="mermaid" data-flow="steps pulse-path"
     data-steps='[{"node":"ASK","cap":"모델에 messages+tools를 보낸다","lines":"31-42"},
                  {"node":"DISPATCH","cap":"tool_use 이름을 실제 함수로 연결"}]'
     data-cycle="OBS,VLA,ACT,SIM"
     data-code="#code-agent-loop">
flowchart LR
    ASK["messages.create()"] --> ...
</div>
```

| Effect | What it teaches | How to use |
|---|---|---|
| `steps` | Functions firing **in call order** — one node lights (spring+glow), others dim; a Korean caption line syncs below; ⏮ ▶ ⏭ controls | `data-steps` JSON: `node` (mermaid node ID), `cap` (Korean, one line), optional `lines` ("12-18") to co-highlight code |
| `pulse-path` | "The loop is the engine" — a dot travels the cycle forever | `data-cycle="A,B,C,D"` (node IDs in tour order) or omit → dot rides each dotted edge |
| `freeze-train` | Frozen vs trained contrast — frozen node desaturated & still, trained node breathes | `data-frozen="EMB" data-trained="HEAD"` |
| `codewalk` | Diagram node ↔ actual code line, 1:1 | `data-code="#<id of a pre>"` on the same `steps` box; give the `<pre>` that id. Lines are 1-indexed within the excerpt |
| `fx-morph` | text → vector intuition (embedding) | standalone widget: `<div class="fx-morph" data-text="My card was charged twice" data-dims="8"></div>` |
| `fx-mismatch` | Embodiment force-fit: model outputs N bars, sim expects M slots; extras shake red and get cut, gaps zero-pad in gray | standalone widget: `<div class="fx-mismatch" data-model="16" data-sim="14"></div>` |

Rules of thumb: exactly **one** big `steps` diagram per page (the 흐름 section);
`pulse-path` wherever the concept literally is a loop; widgets (`fx-*`) once each
where the concept appears, not more. If an effect doesn't add meaning, don't use it.

## Common section skeleton (개념 → scaffold → 흐름 → 코드)

1. **개념** — why/what, one analogy, one concept diagram (plain reveal is fine)
2. **Scaffold** — file-map mermaid + role table (reuse 5C's `table.spec` pattern; 5B/5D: add the same `<style>` block pattern locally if the page lacks it — page-local widget CSS is allowed, only *mermaid/anime* styling is centralized)
3. **흐름** ★ — ONE function-name diagram with `steps` (+ `pulse-path` if loop). Captions = 그 함수가 하는 일 한 줄(한국어)
4. **코드** — per-function: mini diagram or none + verbatim excerpt + `codewalk` sync
5. **Run locally** — keep/refresh existing
6. **Key idea + quizzes**

---

## Task 0 · Shared foundation (orchestrator — already specified, listed for context)

- `docs/flow-anim.js` (new): implements the vocabulary above on top of anime.js v4
  ESM (`https://cdn.jsdelivr.net/npm/animejs@4/lib/anime.esm.min.js`); waits for
  `mermaid-fx:done` event; honors `prefers-reduced-motion`; degrades gracefully
  (steps work as instant class toggles if anime fails to load).
- `docs/mermaid-fx.js`: dispatch `mermaid-fx:done` after wiring.
- `docs/style.css`: `.rail-proj` (indented project links), `.flowsteps`, `.flowcap`,
  `.fnode-dim/.fnode-hot`, `.codewalk .hot-line`, `.fx-morph`, `.fx-mismatch`.
- `docs/nav.js`: OUTLINE becomes modules 1–7, each with optional `projects:[…]`
  (indented in the top rail); Part-2 detail lookup searches projects too.
- 5B/5C/5D `<head>`: add `<script type="module" src="./flow-anim.js?v=1"></script>`.
- Titles: h1/`<title>`/breadcrumb → `Module 5 · Project — <name>` on all three.
- Cache-bust everywhere: `nav.js?v=10`, `style.css?v=6`.

---

## Task 1 · 5B — Project: Custom Training (fine-tuning)

**File**: `docs/05B-finetune.html` (261 lines → ~700). Keep existing sections
`what/hard/primer/stages/hood/local/key` (good concept base) and DEEPEN:

New/updated sections (suggested order & ids):
- keep `what`, `hard`, `primer` (concept tier)
- NEW `scaffold` — file map: `taxonomy.json / seed_examples.jsonl / synthetic_train.jsonl / common.py / stage0·1·2 / evaluate.py`; role table. Note what `common.py` owns (Claude routing via **forced tool use**, embeddings, data IO — read it!).
- keep `stages`, upgrade its diagram to a 3-lane mermaid (`ZERO`/`FEW`/`TUNE` lanes) with `steps` walking lane by lane (captions contrast the three methods).
- NEW `flow` ★ — the stage-2 pipeline as function names from the real code:
  `LOADJ["load_jsonl()"] --> EMB["embed_texts()  · common.py"] --> FIT["LogisticRegression().fit(X, y)"] --> PRED["predict()"] --> EVAL["evaluate.py · F1 + confusion"]`
  plus dotted feedback `REROUTE["human reroutes a ticket"] -.-> TRAIN["training set"]`.
  Effects: `steps` (5 captions) + `pulse-path` on the feedback edge.
- keep/upgrade `hood` — apply `data-flow="freeze-train" data-frozen="<embedder node>" data-trained="<head node>"` to the existing frozen/trained diagram; add one `fx-morph` widget right where embedding is explained (`data-text` = a real ticket from the training data).
- NEW `code` — two codewalk excerpts: ① `common.py`'s routing function showing **tool_choice forcing** (why the model MUST answer with a team), ② `stage2_finetune.py` embed→fit→score lines. Each with `steps`+`data-code`.
- keep `local`, `key`.

Quizzes: 1 → **≥4**. Target misconceptions:
(a) "fine-tuning updates the whole model" (existing quiz — keep),
(b) "forced tool choice is about output *format* only" (it's what guarantees a
routable label every time),
(c) "few-shot and custom-trained cost the same at inference" (1 API call vs 0),
(d) "synthetic training data is as good as production data" (distribution + bias).

## Task 2 · 5C — Project: VLA on your laptop

**File**: `docs/05C-vla.html` (384 lines → ~800). The page is decent — this task
is *depth + animation*, not restructure. Keep all ids
(`what/scaffold/stack/loop/check/buildobs/rollout/embodiment/local/key`).

- `loop`: add `data-flow="pulse-path" data-cycle="OBS,VLA,ACT,SIM"` (rename the
  existing diagram's node IDs to those; keep labels).
- NEW `flow` ★ (insert after `loop`) — `main()`'s real call order:
  `LOADC["load_smolvla_class()"] --> PRET["from_pretrained()"] --> PROC["make_pre_post_processors()"] --> RESET["env.reset()"]` then the loop cluster
  `BOBS["build_observation()"] --> PRE["preprocessor()"] --> SEL["select_action()"] --> POST["postprocessor()"] --> FIT2["force-fit dims"] --> STEP["env.step()"] --> REND["env.render()"]` with `STEP -.-> BOBS`.
  Effects: `steps` (7+ captions, from the real run_demo.py) + `pulse-path`.
- `buildobs` + `rollout`: convert their code excerpts to `codewalk` (give each
  `<pre>` an id, wire `data-code`, add `lines` to the step JSON). The excerpts
  must be re-checked against `run_demo.py` verbatim.
- `embodiment`: add the `fx-mismatch` widget (`data-model` / `data-sim` — read the
  real dims: sim action dim is 14; use the checkpoint's dim as printed by
  check_setup notes, explain in caption text that numbers may drift).
- `check`: extend with a short verbatim excerpt of the four-step structure.
- Add ~2 sections' worth of prose depth where thinnest (stack rationale,
  going-further from README).

Quizzes: 5 → **≥7**. Existing five stay. Add:
(f) "the pre/post-processors are optional glue" (they're checkpoint-bound:
tokenization + normalization live there; skipping them = KeyError),
(g) "if the loop runs, the policy fits the robot" (loop running ≠ embodiment
match — force-fit hides the mismatch).

## Task 3 · 5D — Project: data-analyst agent (**biggest lift**)

**File**: `docs/05D-agent.html` (143 lines → ~700). Currently a stub. Full
skeleton build-out, keeping ids `what/how/run/local/key` and adding new ones.

- `what` (개념) — expand: what the agent does, the two pre-built safety patterns
  (structural read-only, max-steps budget), tie to 5A.1's loop. Analogy: 신입
  분석가에게 "읽기 전용 DB 계정"만 주는 회사.
- NEW `scaffold` — file map: `agent.py / tools.py / build_db.py / data.db /
  README`; role table (agent.py = the loop; tools.py = 3 read-only tools +
  SELECT guard; build_db.py = synthetic store data; data.db = SQLite).
- `how` → rename heading to 흐름 ★ and rebuild the diagram with real function
  names from `agent.py`/`tools.py`:
  `USERQ["user question"] --> CREATE["client.messages.create(tools=TOOLS)"] --> STOPQ{"stop_reason == tool_use?"}`,
  `STOPQ -->|yes| DISPATCH["dispatch(name, args)"] --> TOOLS3["list_tables() / describe_table() / run_query()"] --> APPEND["append tool_result"]`,
  `APPEND -.-> CREATE`, `STOPQ -->|no| DONE["final answer"]`, plus a `MAXS["max_steps guard"]` node.
  Effects: `steps` (6–7 captions) + `pulse-path` on `APPEND -.-> CREATE`.
- NEW `code` — three codewalk excerpts from the real files: ① the agent loop in
  `agent.py` (messages.create → tool dispatch → append), ② `run_query()`'s
  SELECT-only guard in `tools.py` (the structural-safety punchline), ③ 5 lines of
  `build_db.py` showing what data exists (so "지난달 매출 top5" questions make sense).
- NEW `schema` (optional if it earns its place) — small mermaid of the SQLite
  tables from `build_db.py` (orders/products/…, read the real schema).
- keep `run` (Run it live) and `local`; refresh `key`.

Quizzes: 1 → **≥4**. Target misconceptions:
(a) "prompt-warning the model not to write is as safe as not giving write tools"
(existing quiz — keep),
(b) "the agent decides when it's done by us checking its text" (no — `stop_reason`
semantics drive the loop),
(c) "max_steps is about cost only" (it's the halting guarantee for a loop that
otherwise has none),
(d) "the model queries the DB directly" (the model only *names* a tool + args;
`dispatch()` in OUR code touches the DB — the boundary is the whole point).

---

## Per-task verification (agent must self-check before finishing)

1. `grep -c '<section id'` matches the TOC and heading numbering is contiguous.
2. Every `data-steps` node ID exists in that diagram's mermaid source.
3. Every `data-code` target id exists; every `lines` range is within the excerpt.
4. All code excerpts diff-checked against ground-truth source (no invented code).
5. Quiz count meets target; each `.quiz` has exactly one correct `data-answer`.
6. No edits outside your one file; no inline mermaid/anime init added.
7. Report back: sections added/changed, diagram+effect inventory, quiz list
   (one line each: targeted misconception), any spec deviation + why.

## Orchestrator verification (after each task lands)

Browser (bit-habit live or local): mermaid SVG count & zero errors; `.flowsteps`
next-button actually toggles `.fnode-hot`; `fx-*` widgets render; quiz totals;
anchors ↔ TOC ↔ nav.js detail; console clean; footer chain 5A→5B→5C→5D→6 intact.
