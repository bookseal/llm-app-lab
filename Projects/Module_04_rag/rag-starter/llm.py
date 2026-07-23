"""Provider adapter — swap the generation LLM without touching any call site.

WHY this exists: streamlit_app.py and backend/app.py speak *Anthropic message
shapes* everywhere — `resp.content[0].text`, `b.type == "tool_use"`, `b.input`,
`resp.stop_reason`, `stream.get_final_message()`, and even feeding raw content
blocks back in via `messages.append({"role": "assistant", "content": resp.content})`.
Rewriting all of that per provider would be a rewrite, not a swap.

So the Anthropic shape is the LINGUA FRANCA. Two families of provider:

  kind="anthropic"  DeepSeek / GLM / Kimi ship an Anthropic-COMPATIBLE endpoint.
                    We hand the real `anthropic` SDK a different base_url and
                    api_key. Zero translation — streaming, tools, usage all work.

  kind="openai"     Gemini / Groq / OpenRouter / Ollama speak OpenAI chat
                    completions. `_OpenAIShim` below translates both directions
                    so the caller still sees Anthropic-shaped objects.

Usage:
    from llm import get_client, MODEL, price_for
    client = get_client()                    # honours $LLM_PROVIDER
    client.messages.create(model=MODEL, ...) # exactly as before

Select with a single env var in .env:
    LLM_PROVIDER=gemini
    GEMINI_API_KEY=...

NOTE: base_urls, model ids and prices below are a starting point — providers move
fast. Verify against the provider's own docs before trusting the cost badge.
"""
import json
import os
from dataclasses import dataclass, field
from pathlib import Path

from dotenv import load_dotenv

# Load .env HERE, not in the caller: PROVIDER/MODEL are read at import time, and
# an importer that calls load_dotenv() after `import llm` would be too late.
load_dotenv(Path(__file__).parent / ".env")

# ── Provider registry ────────────────────────────────────────────────────────
# price = (USD per 1M input tokens, USD per 1M output tokens). (0, 0) = free tier.
PROVIDERS = {
    "anthropic": dict(
        kind="anthropic", base_url=None, key_env="ANTHROPIC_API_KEY",
        model="claude-sonnet-4-6", price=(3.0, 15.0),
    ),
    # ── Chinese providers: cheap, Anthropic-compatible endpoints ──
    # NOTE: deepseek-chat / deepseek-reasoner are DEPRECATED as of 2026-07-24 —
    # v4-flash is the replacement (v4-pro is the bigger, ~3x pricier sibling).
    # DeepSeek's Anthropic layer fully supports tool_use + tool_result, so the
    # agentic loop and the gap-aware report_answer tool both work unchanged.
    "deepseek": dict(
        kind="anthropic", base_url="https://api.deepseek.com/anthropic",
        key_env="DEEPSEEK_API_KEY", model="deepseek-v4-flash", price=(0.14, 0.28),
    ),
    "glm": dict(  # Zhipu 智谱 / Z.AI — the -Flash tiers are genuinely $0
        kind="anthropic", base_url="https://api.z.ai/api/anthropic",
        key_env="ZAI_API_KEY", model="glm-4.7-flash", price=(0.0, 0.0),
    ),
    "kimi": dict(  # Moonshot. Endpoint verified; model id NOT — check their docs.
        kind="anthropic", base_url="https://api.moonshot.ai/anthropic",
        key_env="MOONSHOT_API_KEY", model="kimi-k2-turbo-preview", price=(0.6, 2.5),
    ),
    # ── OpenAI-compatible: need the translation shim ──
    # Gemini 3 is a THINKING model and its thinking tokens come out of the same
    # max_tokens budget as the answer — but they're invisible in usage
    # (completion_tokens counts text only). Passing max_tokens=400 straight
    # through yields a 12-token answer with finish_reason="length": the request
    # looks like it succeeded and the answer is just silently cut off mid-word.
    # Measured at reasoning_effort="low": ~1.3k tokens of thinking. So we pad.
    "gemini": dict(
        kind="openai",
        base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
        key_env="GEMINI_API_KEY", model="gemini-3.5-flash", price=(1.5, 9.0),
        # Gemini's free tier is a property of the PROJECT (no billing linked),
        # not of the key or the model — the same model id costs $0 on an unbilled
        # project and the rates below on a billed one. We quote the PAID rates so
        # the cost badge never under-reports; on a free project it just reads high.
        model_prices={"gemini-3.5-flash": (1.5, 9.0),
                      "gemini-3.5-flash-lite": (0.5, 3.0),
                      "gemini-3.1-pro-preview": (2.0, 12.0),
                      "gemini-2.5-flash": (0.3, 2.5)},
        extra={"reasoning_effort": "low"}, thinking_pad=1536,
    ),
    "groq": dict(
        kind="openai", base_url="https://api.groq.com/openai/v1",
        key_env="GROQ_API_KEY", model="llama-3.3-70b-versatile", price=(0.0, 0.0),
    ),
    # OpenRouter's free roster rotates — re-check with:
    #   curl -s https://openrouter.ai/api/v1/models | jq -r \
    #     '.data[] | select(.id|endswith(":free")) | select(.supported_parameters|index("tools")) | .id'
    # `tools` support is non-negotiable here: agentic + gap-aware modes need it.
    "openrouter": dict(
        kind="openai", base_url="https://openrouter.ai/api/v1",
        key_env="OPENROUTER_API_KEY",
        model="openai/gpt-oss-20b:free", price=(0.0, 0.0),
    ),
    "ollama": dict(  # fully local — no key, no network. Model = whatever you pulled.
        kind="openai", base_url="http://localhost:11434/v1",
        key_env=None, model="qwen3:8b", price=(0.0, 0.0),
    ),
}

PROVIDER = os.environ.get("LLM_PROVIDER", "anthropic").strip().lower()
if PROVIDER not in PROVIDERS:
    raise SystemExit(
        f"LLM_PROVIDER={PROVIDER!r} is unknown. Pick one of: {', '.join(PROVIDERS)}"
    )
CONFIG = PROVIDERS[PROVIDER]

# $LLM_MODEL overrides the provider's default model (e.g. a different :free model
# on OpenRouter) without editing this file.
MODEL = os.environ.get("LLM_MODEL") or CONFIG["model"]


def price_for(model: str) -> tuple[float, float]:
    """(input, output) USD per million tokens for `model`.

    Looked up WITHIN the active provider, never from a global model→price table:
    the same model id is billed differently on OpenRouter vs. its home provider.
    An unrecognised model falls back to the provider's default price, so the badge
    degrades to an estimate instead of silently reading $0.
    """
    return tuple((CONFIG.get("model_prices") or {}).get(model) or CONFIG["price"])


# ── Anthropic-shaped response objects (what every call site already expects) ──
@dataclass
class TextBlock:
    text: str
    type: str = "text"


@dataclass
class ToolUseBlock:
    id: str
    name: str
    input: dict
    type: str = "tool_use"
    # The provider's ORIGINAL tool_call, replayed verbatim on the next turn.
    # Gemini 3 attaches a `thought_signature` under extra_content.google and
    # rejects the follow-up turn with 400 if it doesn't come back — reconstructing
    # the call from (id, name, input) silently drops it. Callers never touch this;
    # it exists so a round trip through our Anthropic shape is lossless.
    raw: dict | None = None


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0


@dataclass
class Message:
    model: str
    content: list = field(default_factory=list)
    stop_reason: str = "end_turn"
    usage: Usage = field(default_factory=Usage)


# ── OpenAI ⇄ Anthropic translation ───────────────────────────────────────────
def _to_openai_messages(system, messages):
    """Anthropic `system` + `messages` → a flat OpenAI message list.

    Three shapes have to survive the trip, because the agentic loop produces all
    three: plain string content, an assistant turn carrying our ToolUseBlocks,
    and a user turn that is really a list of tool_result dicts.
    """
    out = []
    if system:
        out.append({"role": "system", "content": system})
    for m in messages:
        role, content = m["role"], m["content"]
        if isinstance(content, str):
            out.append({"role": role, "content": content})
            continue
        # Assistant turn replayed from a previous response's content blocks.
        if role == "assistant":
            text = "".join(b.text for b in content if getattr(b, "type", "") == "text")
            calls = [
                # Replay the provider's own tool_call when we have it (keeps
                # Gemini's thought_signature intact); rebuild only as a fallback.
                b.raw or {"id": b.id, "type": "function",
                          "function": {"name": b.name, "arguments": json.dumps(b.input)}}
                for b in content if getattr(b, "type", "") == "tool_use"
            ]
            msg = {"role": "assistant", "content": text or None}
            if calls:
                msg["tool_calls"] = calls
            out.append(msg)
            continue
        # User turn that is actually tool results — OpenAI wants one "tool"
        # message per result, not a list bundled into a user turn.
        for b in content:
            if isinstance(b, dict) and b.get("type") == "tool_result":
                out.append({"role": "tool", "tool_call_id": b["tool_use_id"],
                            "content": b["content"]})
            elif isinstance(b, dict) and b.get("type") == "text":
                out.append({"role": role, "content": b["text"]})
    return out


def _to_openai_tools(tools):
    return [{"type": "function",
             "function": {"name": t["name"], "description": t.get("description", ""),
                          "parameters": t["input_schema"]}}
            for t in tools]


def _from_openai(resp, model):
    """OpenAI ChatCompletion → an Anthropic-shaped Message."""
    choice = resp.choices[0]
    blocks = []
    if choice.message.content:
        blocks.append(TextBlock(text=choice.message.content))
    for call in (choice.message.tool_calls or []):
        try:
            args = json.loads(call.function.arguments or "{}")
        except json.JSONDecodeError:
            args = {}
        raw = call.model_dump(exclude_none=True) if hasattr(call, "model_dump") else None
        blocks.append(ToolUseBlock(id=call.id, name=call.function.name, input=args,
                                   raw=raw))
    if not blocks:
        blocks.append(TextBlock(text=""))
    stop = "tool_use" if choice.finish_reason == "tool_calls" else "end_turn"
    u = getattr(resp, "usage", None)
    usage = Usage(getattr(u, "prompt_tokens", 0) or 0,
                  getattr(u, "completion_tokens", 0) or 0)
    return Message(model=getattr(resp, "model", model) or model,
                   content=blocks, stop_reason=stop, usage=usage)


class _OpenAIStream:
    """Context manager mimicking `anthropic`'s `messages.stream(...)`.

    Same contract the UI was built around (①): text arrives incrementally via
    `.text_stream`, and usage/meta only becomes available at the END via
    `.get_final_message()`.
    """

    def __init__(self, client, model, kwargs):
        self._client, self._model, self._kwargs = client, model, kwargs
        self._final = None
        self._text = ""

    def __enter__(self):
        return self

    def __exit__(self, *exc):
        return False

    @property
    def text_stream(self):
        usage = Usage()
        stream = self._client.chat.completions.create(
            stream=True, stream_options={"include_usage": True}, **self._kwargs)
        for chunk in stream:
            if getattr(chunk, "usage", None):
                usage = Usage(chunk.usage.prompt_tokens or 0,
                              chunk.usage.completion_tokens or 0)
            if not chunk.choices:
                continue
            piece = chunk.choices[0].delta.content
            if piece:
                self._text += piece
                yield piece
        # Some OpenAI-compatible servers never send a usage chunk; ~4 chars per
        # token keeps the cost badge in the right order of magnitude.
        if not usage.input_tokens and not usage.output_tokens:
            usage = Usage(0, len(self._text) // 4)
        self._final = Message(model=self._model, content=[TextBlock(text=self._text)],
                              usage=usage)

    def get_final_message(self):
        if self._final is None:  # caller never drained text_stream
            self._final = Message(model=self._model,
                                  content=[TextBlock(text=self._text)])
        return self._final


class _Messages:
    def __init__(self, client, default_model):
        self._client, self._default_model = client, default_model

    def _kwargs(self, model, max_tokens, system, messages, tools=None, tool_choice=None):
        kw = {"model": model or self._default_model,
              # Pad so a thinking model's hidden reasoning doesn't eat the answer.
              "max_tokens": max_tokens + CONFIG.get("thinking_pad", 0),
              "messages": _to_openai_messages(system, messages)}
        kw.update(CONFIG.get("extra") or {})
        if tools:
            kw["tools"] = _to_openai_tools(tools)
        if tool_choice and tool_choice.get("type") == "tool":
            kw["tool_choice"] = {"type": "function",
                                 "function": {"name": tool_choice["name"]}}
        elif tool_choice:
            kw["tool_choice"] = "auto"
        return kw

    def create(self, *, model=None, max_tokens=1024, system=None, messages,
               tools=None, tool_choice=None, **_):
        kw = self._kwargs(model, max_tokens, system, messages, tools, tool_choice)
        return _from_openai(self._client.chat.completions.create(**kw), kw["model"])

    def stream(self, *, model=None, max_tokens=1024, system=None, messages,
               tools=None, tool_choice=None, **_):
        kw = self._kwargs(model, max_tokens, system, messages, tools, tool_choice)
        return _OpenAIStream(self._client, kw["model"], kw)


class _OpenAIShim:
    """Quacks like `anthropic.Anthropic` — exposes only `.messages`."""

    def __init__(self, base_url, api_key, default_model):
        from openai import OpenAI  # imported lazily: unused on the anthropic path
        self._client = OpenAI(base_url=base_url, api_key=api_key or "not-needed")
        self.messages = _Messages(self._client, default_model)


def get_client():
    """The active provider's client, Anthropic-shaped either way."""
    key = os.environ.get(CONFIG["key_env"]) if CONFIG["key_env"] else None
    if CONFIG["key_env"] and not key:
        raise SystemExit(
            f"LLM_PROVIDER={PROVIDER} needs {CONFIG['key_env']} in your environment "
            f"or rag-starter/.env"
        )
    if CONFIG["kind"] == "anthropic":
        from anthropic import Anthropic
        kw = {"api_key": key} if key else {}
        if CONFIG["base_url"]:
            kw["base_url"] = CONFIG["base_url"]
        return Anthropic(**kw)
    return _OpenAIShim(CONFIG["base_url"], key, MODEL)
