// Injects ONE sticky left sidebar that lists the WHOLE lab — every module
// (1 → 7) with its detailed section titles — so you can scroll the entire
// outline and jump anywhere. A handle at the top collapses/expands the rail
// (state remembered in localStorage). The current page's sections get
// scroll-spy highlighting.
//
// Loaded with <script src="./nav.js" defer></script> in each page's <head>.
(function () {
  // mirror each page's own slugging so cross-page "#anchor" links land
  const slug = (t) =>
    t.toLowerCase().trim().replace(/[^0-9a-z가-힣]+/g, "-")
      .replace(/^-+|-+$/g, "").slice(0, 40) || "sec";

  // ── single source of truth: the full lab outline ──
  // Pages with explicit <section id> → {t: <label>, id: <id>}.
  // Pages whose sections have NO id → {t: <EXACT h2 text>}; we slug it the same
  // way the page does at runtime, so the anchor still resolves.
  const OUTLINE = [
    { href: "index.html", num: "★", label: "Start here", sections: [] },
    { href: "01-setup.html", num: "1", label: "Setup", sections: [
      { t: "1.1 · Install VSCode", id: "vscode" },
      { t: "1.2 · Install Git", id: "git" },
      { t: "1.3 · Install Node.js (LTS)", id: "node" },
      { t: "1.4 · Install Python 3.11", id: "python" },
      { t: "1.5 · Project folder & venv", id: "venv" },
      { t: "1.6 · Claude Code CLI", id: "cli" },
      { t: "1.7 · Anthropic API key", id: "apikey" },
    ] },
    { href: "02-1-foundations.html", num: "2A", label: "Foundations", sections: [
      { t: "2A.1 · Big picture", id: "overview" }, { t: "2A.2 · Flask", id: "flask" },
      { t: "2A.3 · Endpoints", id: "endpoint" }, { t: "2A.4 · CORS", id: "cors" },
      { t: "2A.5 · React", id: "react" }, { t: "2A.6 · Vite", id: "vite" }, { t: "2A.7 · JSX", id: "jsx" },
      { t: "2A.8 · Mount", id: "mount" }, { t: "2A.9 · Stateless", id: "stateless" },
      { t: "2A.10 · Self-check", id: "selfcheck" },
    ] },
    { href: "02-2-chat-app.html", num: "2B", label: "Project: chat-app", sections: [
      { t: "2B.1 · Big picture — three servers", id: "llm" }, { t: "2B.2 · Memory (stateless)", id: "memory" },
      { t: "2B.3 · Async & loading", id: "async" }, { t: "2B.4 · Network failure", id: "network" },
      { t: "2B.5 · API errors", id: "apierror" }, { t: "2B.6 · Input validation & more", id: "missing" },
      { t: "2B.7 · Find the 5 bugs", id: "selfcheck" },
    ] },
    { href: "03A-tools.html", num: "3A", label: "Tools & Structure", sections: [
      { t: "3A.1 · Live demo (BigQuery SQL)", id: "demo" }, { t: "3A.2 · 4 Levels", id: "levels" },
      { t: "3A.3 · L1 · Parseable output", id: "level1" }, { t: "3A.4 · L2 · Structured output", id: "level2" },
      { t: "3A.5 · L3 · Tool use (agent loop)", id: "level3" }, { t: "3A.6 · L4 · MCP", id: "level4" },
      { t: "3A.7 · Project: job-post extractor", id: "project" },
    ] },
    { href: "03B-extractor.html", num: "3B", label: "Project: extractor", sections: [
      { t: "3B.1 · What it builds", id: "what" },
      { t: "3B.2 · How it works", id: "how" },
      { t: "3B.3 · Run it live", id: "run" },
      { t: "3B.4 · Run it locally", id: "local" },
      { t: "3B.5 · The key idea", id: "key" },
    ] },
    { href: "04A-context.html", num: "4A", label: "Context / RAG", sections: [
      { t: "4A.1 · Why not giant context", id: "why" },
      { t: "4A.2 · Embeddings", id: "embed" },
      { t: "4A.3 · Indexing pipeline", id: "pipeline" },
      { t: "4A.4 · Chunking", id: "chunk" },
      { t: "4A.5 · Vector stores · ANN/HNSW", id: "store" },
      { t: "4A.6 · RAG in 30 lines", id: "rag" },
      { t: "4A.7 · Citations", id: "cite" },
      { t: "4A.8 · Memory", id: "memory" },
      { t: "4A.9 · Project: RAG over a corpus", id: "project" },
    ] },
    { href: "04B-rag.html", num: "4B", label: "Project: RAG", sections: [
      { t: "4B.1 · 60-second version", id: "sixty" },
      { t: "4B.2 · 5-minute version", id: "five" },
      { t: "4B.3 · 10-minute version", id: "ten" },
      { t: "4B.4 · 20-minute version", id: "twenty" },
      { t: "4B.5 · The whole picture", id: "whole" },
      { t: "4B.6 · Why it's built this way", id: "why" },
      { t: "4B.7 · File map", id: "files" },
    ] },
    { href: "05A-agents.html", num: "5A", label: "Agents", sections: [
      { t: "5A.1 · The agent loop", id: "loop" },
      { t: "5A.2 · What is Claude Code", id: "claude-code" },
      { t: "5A.3 · Subagents", id: "subagents" },
      { t: "5A.4 · Memory scopes", id: "memory" },
      { t: "5A.5 · Patterns (routing·caching·async)", id: "patterns" },
      { t: "5A.6 · Computer use & Safety", id: "safety" },
      { t: "5A.7 · Project: data-analyst agent", id: "project" },
    ] },
    { href: "05B-finetune.html", num: "5B", label: "Special Topics: fine-tuning · VLA", sections: [
      { t: "5B.1 · What it builds", id: "what" },
      { t: "5B.2 · 왜 어려운가 — 숨은 하우스룰", id: "hard" },
      { t: "5B.3 · 신경망이 분류하는 법", id: "primer" },
      { t: "5B.4 · 세 가지 방법", id: "stages" },
      { t: "5B.5 · Frozen embedder + trained head", id: "hood" },
      { t: "5B.6 · Build & run locally", id: "local" },
      { t: "5B.7 · The key idea", id: "key" },
      { t: "5B.8 · VLA — LLM을 물리 세계로", id: "vla" },
      { t: "5B.9 · See it move", id: "vla-see" },
      { t: "5B.10 · Anatomy of a VLA", id: "vla-hood" },
    ] },
    { href: "05C-agent.html", num: "5C", label: "Project: data agent", sections: [
      { t: "5C.1 · What it builds", id: "what" },
      { t: "5C.2 · How it works", id: "how" },
      { t: "5C.3 · Run it live", id: "run" },
      { t: "5C.4 · Build & run locally", id: "local" },
      { t: "5C.5 · The key idea", id: "key" },
    ] },
    { href: "06-production.html", num: "6", label: "Production", sections: [
      { t: "6.1 · Three questions before you ship", id: "three-questions" },
      { t: "6.2 · Eval & Testing", id: "eval" },
      { t: "6.3 · Guardrails & Security", id: "security" },
      { t: "6.4 · Observability & Latency", id: "observability" },
      { t: "6.5 · Wrap-up", id: "wrapup" },
    ] },
    { href: "07-workshop.html", num: "7", label: "Workshop", sections: [
      { t: "7.1 · How the workshop works", id: "how" },
      { t: "7.2 · Project options", id: "options" },
      { t: "7.3 · What you've built so far", id: "recap" },
      { t: "7.4 · Final Quiz", id: "final-quiz" },
    ] },
  ];

  const here = location.pathname.split("/").pop() || "index.html";
  const wrap = document.querySelector(".wrap");
  if (!wrap) return;

  // ── make sure THIS page's sections have ids (for anchors + scroll-spy) ──
  const used = {};
  const pageSections = []; // { id, el }
  for (const sec of wrap.querySelectorAll("section")) {
    const h = sec.querySelector("h2");
    if (!h) continue;
    if (!sec.id) {
      // label = <h2> text WITHOUT the trailing "슬라이드 N" link
      const label = Array.from(h.childNodes)
        .filter((n) => !(n.nodeType === 1 && n.classList.contains("slide")))
        .map((n) => n.textContent).join("").trim();
      let s = slug(label);
      while (used[s]) s += "-x";
      used[s] = true;
      sec.id = s;
    } else {
      used[sec.id] = true;
    }
    pageSections.push({ id: sec.id, el: sec });
  }

  // ── build the single continuous outline ──
  const nav = document.createElement("nav");
  nav.className = "rail-outline";
  const linkBySectionId = new Map(); // current-page section id → its <a> (scroll-spy)

  for (const mod of OUTLINE) {
    const modA = document.createElement("a");
    modA.className = "rail-mod";
    modA.href = "./" + mod.href;
    const numSpan = document.createElement("span");
    numSpan.className = "rail-num";
    numSpan.textContent = mod.num;
    modA.append(numSpan, document.createTextNode(mod.label));
    if (mod.href === here) modA.classList.add("current-mod");
    nav.appendChild(modA);

    if (mod.sections.length) {
      const sub = document.createElement("div");
      sub.className = "rail-subs";
      for (const s of mod.sections) {
        const id = s.id || slug(s.t);
        const a = document.createElement("a");
        a.className = "rail-sub";
        a.href = "./" + mod.href + "#" + id;
        a.textContent = s.t;
        sub.appendChild(a);
        if (mod.href === here) linkBySectionId.set(id, a);
      }
      nav.appendChild(sub);
    }
  }

  // ── collapse/expand handle ──
  const rail = document.createElement("aside");
  rail.className = "rail";
  const handle = document.createElement("button");
  handle.className = "rail-handle";
  handle.setAttribute("aria-label", "Toggle sidebar");
  const setCollapsed = (c) => {
    document.body.classList.toggle("rail-collapsed", c);
    handle.textContent = c ? "☰ Menu" : "‹ Hide";
    try { localStorage.setItem("railCollapsed", c ? "1" : "0"); } catch (e) {}
  };
  handle.addEventListener("click", () =>
    setCollapsed(!document.body.classList.contains("rail-collapsed")));
  rail.append(handle, nav);

  // restructure: body > .layout > (rail, .wrap)
  const layout = document.createElement("div");
  layout.className = "layout";
  wrap.parentNode.insertBefore(layout, wrap);
  layout.append(rail, wrap);

  let initCollapsed = false;
  try { initCollapsed = localStorage.getItem("railCollapsed") === "1"; } catch (e) {}
  setCollapsed(initCollapsed);

  // bring the current module into view inside the (scrollable) rail
  const cur = nav.querySelector(".current-mod");
  if (cur) cur.scrollIntoView({ block: "center" });

  // ── scroll-spy: highlight the current page's section being read ──
  if (linkBySectionId.size && "IntersectionObserver" in window) {
    const visible = new Set();
    let activeId = null;
    const setActive = (id) => {
      if (id === activeId) return;
      if (activeId && linkBySectionId.has(activeId)) linkBySectionId.get(activeId).classList.remove("active");
      activeId = id;
      if (id && linkBySectionId.has(id)) {
        const el = linkBySectionId.get(id);
        el.classList.add("active");
        el.scrollIntoView({ block: "nearest" });
      }
    };
    const io = new IntersectionObserver(
      (entries) => {
        for (const e of entries) {
          if (e.isIntersecting) visible.add(e.target.id);
          else visible.delete(e.target.id);
        }
        let best = null, bestTop = Infinity;
        for (const id of visible) {
          const top = document.getElementById(id).getBoundingClientRect().top;
          if (top < bestTop) { bestTop = top; best = id; }
        }
        if (best) setActive(best);
      },
      { rootMargin: "0px 0px -65% 0px", threshold: 0 }
    );
    for (const ps of pageSections) io.observe(ps.el);
  }
})();
