"""The tools the data-analyst agent can call — all strictly read-only.

The real safety gate is the connection: we open `data.db` with
`mode=ro`, so SQLite itself rejects any write. The `SELECT`/`WITH`
check on top just returns a friendly message instead of an error.
"""
import os
import sqlite3

DB_PATH = os.path.join(os.path.dirname(__file__), "data.db")


def _connect():
    # Read-only connection — any attempted write raises sqlite3.OperationalError.
    return sqlite3.connect(f"file:{DB_PATH}?mode=ro", uri=True)


def _tables(conn):
    return {r[0] for r in conn.execute(
        "SELECT name FROM sqlite_master WHERE type='table'")}


def list_tables() -> str:
    """Return the names of every table in the database."""
    with _connect() as conn:
        return "\n".join(sorted(_tables(conn)))


def describe_table(table: str) -> str:
    """Return columns (name + type) and a few sample rows for one table."""
    with _connect() as conn:
        if table not in _tables(conn):
            return f"No such table: {table!r}."
        cols = conn.execute(f"PRAGMA table_info({table})").fetchall()
        sample = conn.execute(f"SELECT * FROM {table} LIMIT 3").fetchall()
    names = [c[1] for c in cols]
    lines = [f"Table {table}:"]
    lines += [f"  {c[1]} ({c[2]})" for c in cols]
    lines.append("Sample rows:")
    lines.append("  " + " | ".join(names))
    for row in sample:
        lines.append("  " + " | ".join("NULL" if v is None else str(v) for v in row))
    return "\n".join(lines)


def run_query(sql: str) -> str:
    """Run a read-only SQL SELECT and return up to 100 rows."""
    head = sql.strip().lstrip("(").lower()
    if not (head.startswith("select") or head.startswith("with")):
        return "Rejected: only read-only SELECT queries are allowed."
    try:
        with _connect() as conn:
            cur = conn.execute(sql)        # runs a single statement only
            cols = [d[0] for d in cur.description] if cur.description else []
            rows = cur.fetchmany(100)
    except (sqlite3.Error, sqlite3.Warning) as e:
        return f"SQL error: {e}"
    if not rows:
        return "(no rows)"
    out = [" | ".join(cols)]
    out += [" | ".join("NULL" if v is None else str(v) for v in r) for r in rows]
    if len(rows) == 100:
        out.append("… (truncated at 100 rows)")
    return "\n".join(out)


# ── Tool definitions sent to the Claude API ──────────────────────────────
TOOLS = [
    {
        "name": "list_tables",
        "description": "List the names of all tables in the database.",
        "input_schema": {"type": "object", "properties": {}},
    },
    {
        "name": "describe_table",
        "description": "Show the columns (name + type) and a few sample rows "
                       "for one table. Call this before writing a query.",
        "input_schema": {
            "type": "object",
            "properties": {"table": {"type": "string", "description": "Table name"}},
            "required": ["table"],
        },
    },
    {
        "name": "run_query",
        "description": "Run a single read-only SQL SELECT against the SQLite "
                       "database and return the rows. Use SQLite syntax. Any "
                       "write (INSERT/UPDATE/DELETE/…) is rejected.",
        "input_schema": {
            "type": "object",
            "properties": {"sql": {"type": "string", "description": "A single SELECT statement"}},
            "required": ["sql"],
        },
    },
]


def dispatch(name: str, tool_input: dict) -> str:
    """Route a tool_use block to the matching function."""
    if name == "list_tables":
        return list_tables()
    if name == "describe_table":
        return describe_table(tool_input["table"])
    if name == "run_query":
        return run_query(tool_input["sql"])
    return f"Unknown tool: {name}"
