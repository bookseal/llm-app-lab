"""Architecture & Agents starter — a data-analyst agent.

Ask plain-English questions about the bundled e-commerce database; the
agent inspects the schema, writes read-only SQL, and answers.

Interactive (multi-turn — it remembers the conversation):

    python agent.py
    you › Which 3 products had the highest revenue last quarter?
    you › What about the quarter before that?      ← follow-up uses the history

One-shot (handy for scripts / quick checks):

    python agent.py "How many orders completed last month?"

The core is the agent loop from the lecture: ask Claude, run any tools it
requests, feed the results back, repeat until it stops calling tools.
Multi-turn is just keeping one `messages` list across questions.
"""
import sys

from anthropic import Anthropic
from dotenv import load_dotenv

from tools import TOOLS, dispatch

load_dotenv()          # loads ANTHROPIC_API_KEY from .env (walks up to ~/gsia-lab/.env)
client = Anthropic()

MODEL = "claude-sonnet-4-6"
MAX_STEPS = 12         # per question: cap the tool-loop so it can't run away

SYSTEM = """You are a data analyst. You answer questions about a SQLite database \
by inspecting its schema and running read-only SQL queries.

Always start by checking what's there: call list_tables, then describe_table on \
the tables you need, before writing any query. Use SQLite syntax. The data spans \
about 18 months; when a question is time-relative ("last quarter", "recent month"), \
work it out from the most recent order_date in the data, not today's date. Unless \
asked otherwise, treat only 'completed' orders as revenue.

This is a conversation — later questions may refer back to earlier ones. When you \
have the answer, state it plainly, with the key numbers."""


def answer_turn(messages: list) -> str:
    """Run the agent loop for one user turn, mutating `messages` in place.

    `messages` carries the whole conversation so far, so follow-up questions
    have full context. Returns the assistant's final text for this turn.
    """
    for _ in range(MAX_STEPS):
        resp = client.messages.create(
            model=MODEL, max_tokens=2048, system=SYSTEM,
            messages=messages, tools=TOOLS,
        )
        messages.append({"role": "assistant", "content": resp.content})

        tool_calls = [b for b in resp.content if b.type == "tool_use"]
        if not tool_calls:                       # no tools requested → done
            return "".join(b.text for b in resp.content if b.type == "text").strip()

        results = []
        for call in tool_calls:
            print(f"  → {call.name}({_fmt(call.input)})")
            output = dispatch(call.name, call.input)
            results.append({
                "type": "tool_result",
                "tool_use_id": call.id,
                "content": output,
            })
        messages.append({"role": "user", "content": results})

    return "(stopped: hit the step budget without finishing)"


def _fmt(tool_input: dict) -> str:
    """Compact one-line view of a tool's input for the progress log."""
    parts = []
    for k, v in tool_input.items():
        s = str(v).replace("\n", " ")
        parts.append(f"{k}={s[:57] + '...' if len(s) > 60 else s}")
    return ", ".join(parts)


def repl() -> None:
    """Interactive multi-turn session."""
    print("Data-analyst agent. Ask about the store's customers, products, and orders.")
    print("Commands:  exit / quit  ·  reset (clear the conversation)\n")
    messages: list = []
    while True:
        try:
            question = input("you › ").strip()
        except (EOFError, KeyboardInterrupt):
            print()
            break
        if not question:
            continue
        if question.lower() in {"exit", "quit", ":q"}:
            break
        if question.lower() in {"reset", "clear", "new"}:
            messages.clear()
            print("(conversation reset)\n")
            continue
        messages.append({"role": "user", "content": question})
        answer = answer_turn(messages)
        print(f"\n{answer}\n")


if __name__ == "__main__":
    if len(sys.argv) > 1:                         # one-shot mode
        question = " ".join(sys.argv[1:])
        print(f"Q: {question}\n")
        print(answer_turn([{"role": "user", "content": question}]))
    else:                                         # interactive mode
        repl()
