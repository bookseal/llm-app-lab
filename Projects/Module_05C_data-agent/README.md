# Architecture & Agents — Data-analyst agent

A tiny agent that answers plain-English questions about a SQLite database.
It's the agent loop from the lecture (ask Claude → run the tools it requests
→ feed results back → repeat) wired to three read-only tools over a sample
e-commerce dataset. It runs as an interactive, multi-turn session — like the
Claude Code prompt — so follow-up questions keep the context.

```
$ python agent.py
Data-analyst agent. Ask about the store's customers, products, and orders.
Commands:  exit / quit  ·  reset (clear the conversation)

you › Which single product had the highest revenue in the most recent quarter?
  → list_tables()
  → describe_table(table=order_items)
  → run_query(sql=SELECT p.name, SUM(oi.quantity*oi.unit_price) AS rev ...)

Robot Vacuum — $46,307 in revenue (Mar 3 – May 31, 2026, completed orders).

you › What about the quarter before that?       ← follow-up: uses the history
  → run_query(sql=WITH product_revenue AS (...) ...)

Robot Vacuum again — $29,637 the prior quarter, so revenue jumped ~56%.
```

## What's in it

```
agent-app/
├── agent.py          the ~20-line agent loop + a CLI wrapper
├── tools.py          list_tables / describe_table / run_query (read-only)
├── build_db.py       deterministic seed → writes data.db
├── data.db           the sample database (ships prebuilt; rebuild any time)
├── .env.example      template for your ANTHROPIC_API_KEY
└── requirements.txt  anthropic, python-dotenv
```

## The database

A small online store, generated with a fixed random seed so everyone has the
same data (~60 products, ~500 customers, ~3,000 orders, ~8,000 line items over
about 18 months):

```
customers(id, name, email, country, signup_date)
products(id, name, category, price, cost)
orders(id, customer_id, order_date, status)        -- completed | cancelled | refunded
order_items(id, order_id, product_id, quantity, unit_price)
```

It has real-world seams on purpose — cancelled/refunded orders, a few missing
`country` values — so the agent has to look before it leaps. Time-relative
questions ("last quarter") are answered from the most recent `order_date` in
the data, not today's date, so the dataset never goes stale.

## Run

```bash
# from this directory:
python3.11 -m venv .venv
source .venv/bin/activate      # Windows: .venv\Scripts\Activate.ps1
pip install -r requirements.txt

# uses the shared ~/gsia-lab/.env, or copy the template here:
cp .env.example .env           # then put your real ANTHROPIC_API_KEY in

python agent.py                # interactive session (type 'exit' to quit)
# or one-shot, for scripts:
python agent.py "How many orders completed last month?"
```

The prebuilt `data.db` is already here. To regenerate (or change the data):

```bash
python build_db.py
```

## How it works

`agent.py` is the loop:

1. Send the question + the three tool definitions to Claude.
2. If the reply contains `tool_use` blocks, run each one (`dispatch` in
   `tools.py`), append the results, and loop.
3. When Claude stops requesting tools, its text is the answer.

**Multi-turn** is almost free: the interactive loop keeps a single `messages`
list and appends each question (and the tool calls/results) to it, so every
turn sees the full history. That's why "what about the quarter before that?"
works without repeating yourself. (`reset` clears it.)

Two safety details worth noticing:

- **Read-only by construction.** `run_query` opens the database with
  `mode=ro`, so SQLite rejects any write even if the model tries one.
- **A hard step budget.** `MAX_STEPS` caps the loop so a confused agent
  can't spin forever (the "10,000 small failures" from the Safety slide).

## Your job

Pick at least two and present them:

1. **Add a tool.** Ideas: `top_n(metric, table, n)`, `monthly_trend(metric)`,
   or `save_report(text)` that writes findings to a file. Add the function,
   register it in `TOOLS`, and wire it into `dispatch`.
2. **Probe the limits.** Find a question the agent gets *wrong* or answers
   inefficiently (e.g., counts refunded orders as revenue, or runs five
   queries where one would do). Show the transcript and explain what happened.
3. **Tighten the loop.** Make it stream progress, add loop detection (bail on
   repeated identical queries), or have it show the final SQL it settled on.
4. **Swap the data.** Point `build_db.py` at a different schema (a SaaS
   subscriptions DB, your own CSV) and confirm the same agent works unchanged.

## What to present

- One question that works cleanly — show the tool calls and the answer.
- One question that exposes a weakness, and your read on why.
- Whatever you added (a tool, a guardrail) and what it changed.
