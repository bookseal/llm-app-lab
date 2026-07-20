#!/usr/bin/env python3
"""Export Claude Code session transcripts (JSONL) to readable Markdown."""
import json, os, re, sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
SRC = Path.home() / ".claude" / "projects" / ("-" + str(REPO).strip("/").replace("/", "-"))
DST = REPO / "claude-sessions"

def slug(s, n=60):
    s = re.sub(r"[^\w가-힣 -]", "", s).strip().replace(" ", "-")
    return (s[:n] or "untitled")

def blocks(content):
    """Yield (kind, text) from a message content field."""
    if isinstance(content, str):
        yield ("text", content)
        return
    for b in content or []:
        if not isinstance(b, dict):
            continue
        t = b.get("type")
        if t == "text":
            yield ("text", b.get("text", ""))
        elif t == "thinking":
            yield ("thinking", b.get("thinking", ""))
        elif t == "tool_use":
            inp = json.dumps(b.get("input", {}), ensure_ascii=False)
            yield ("tool_use", f"{b.get('name')}({inp})")
        elif t == "tool_result":
            c = b.get("content")
            if isinstance(c, list):
                c = "\n".join(x.get("text", "") for x in c if isinstance(x, dict))
            yield ("tool_result", str(c or ""))

def trim(s, n):
    s = s.strip()
    return s if len(s) <= n else s[:n] + f"\n… [+{len(s)-n} chars truncated]"

def export(path, tool_chars, keep_thinking):
    title, events = None, []
    for line in path.open(encoding="utf-8", errors="replace"):
        try:
            d = json.loads(line)
        except json.JSONDecodeError:
            continue
        if d.get("type") == "ai-title":
            title = d.get("aiTitle")
        if d.get("type") not in ("user", "assistant") or d.get("isSidechain"):
            continue
        events.append(d)

    title = title or f"untitled-{path.stem[:8]}"
    ts = (events[0].get("timestamp", "")[:10] if events else "0000-00-00")
    out = [f"# {title}", "", f"- session: `{path.stem}`", f"- started: {ts}",
           f"- messages: {len(events)}", "", "---", ""]

    for d in events:
        msg = d.get("message") or {}
        role = msg.get("role")
        stamp = d.get("timestamp", "")[11:19]
        for kind, text in blocks(msg.get("content")):
            if not text.strip():
                continue
            if kind == "thinking":
                if not keep_thinking:
                    continue
                out += [f"> 🧠 *thinking* — {trim(text, 800)}", ""]
            elif kind == "text":
                who = "👤 **User**" if role == "user" else "🤖 **Claude**"
                out += [f"### {who}  <sub>{stamp}</sub>", "", text.strip(), ""]
            elif kind == "tool_use":
                out += [f"<details><summary>🔧 {trim(text, 120)}</summary>", "",
                        "```json", trim(text, tool_chars), "```", "", "</details>", ""]
            elif kind == "tool_result":
                out += [f"<details><summary>📄 result</summary>", "",
                        "```", trim(text, tool_chars), "```", "", "</details>", ""]

    name = f"{ts}__{slug(title)}__{path.stem[:8]}.md"
    (DST / name).write_text("\n".join(out), encoding="utf-8")
    return name, title, len(events), (DST / name).stat().st_size

if __name__ == "__main__":
    tool_chars = int(sys.argv[1]) if len(sys.argv) > 1 else 1500
    keep_thinking = "--thinking" in sys.argv
    DST.mkdir(parents=True, exist_ok=True)
    rows = sorted(export(p, tool_chars, keep_thinking) for p in SRC.glob("*.jsonl"))
    index = ["# llm-app-lab — Claude Code session archive", "",
             "| date | session | messages | file |", "|---|---|---|---|"]
    for name, title, n, size in rows:
        index.append(f"| {name[:10]} | {title} | {n} | [{name}](./{name}) |")
        print(f"{size/1024:8.0f} KB  {n:5d} msgs  {name}")
    (DST / "README.md").write_text("\n".join(index) + "\n", encoding="utf-8")
    print(f"\n→ {DST}")
