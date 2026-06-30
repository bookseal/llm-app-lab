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
    { href: "index.html", num: "·", label: "개념 지도", sections: [] },
    { href: "setup.html", num: "1", label: "Setup", sections: [
      { t: "Install VSCode" }, { t: "Install Git" }, { t: "Install Node.js (LTS)" },
      { t: "Install Python 3.11" }, { t: "Create your project folder and venv" },
      { t: "Install the Claude Code CLI" }, { t: "Get an Anthropic API key" },
    ] },
    { href: "foundations.html", num: "2-1", label: "Foundations", sections: [
      { t: "전체 그림", id: "overview" }, { t: "Flask", id: "flask" },
      { t: "엔드포인트 (endpoint)", id: "endpoint" }, { t: "CORS", id: "cors" },
      { t: "React", id: "react" }, { t: "Vite", id: "vite" }, { t: "JSX", id: "jsx" },
      { t: "Mount (마운트)", id: "mount" }, { t: "Stateless", id: "stateless" },
      { t: "스스로 점검 (코드 읽기)", id: "selfcheck" },
    ] },
    { href: "chat-app.html", num: "2-2", label: "chat-app", sections: [
      { t: "전체 그림 — 서버가 셋", id: "llm" }, { t: "메모리 (stateless)", id: "memory" },
      { t: "비동기 & 로딩", id: "async" }, { t: "네트워크 실패", id: "network" },
      { t: "API 에러", id: "apierror" }, { t: "입력 검증 & 그 외", id: "missing" },
      { t: "결함 5가지 찾기", id: "selfcheck" },
    ] },
    { href: "tools.html", num: "3", label: "Tools & Structure", sections: [
      { t: "Live demo (BigQuery SQL)", id: "demo" }, { t: "4 Levels", id: "levels" },
      { t: "L1 · Parseable output", id: "level1" }, { t: "L2 · Structured output", id: "level2" },
      { t: "L3 · Tool use (agent loop)", id: "level3" }, { t: "L4 · MCP", id: "level4" },
      { t: "Project · structured extractor", id: "project" },
    ] },
    { href: "context.html", num: "4", label: "Context / RAG", sections: [
      { t: "4.1 · Why not giant context", id: "why" },
      { t: "4.2 · Indexing pipeline", id: "pipeline" },
      { t: "4.3 · Embeddings", id: "embed" },
      { t: "4.4 · Chunking", id: "chunk" },
      { t: "4.5 · Vector stores · ANN/HNSW", id: "store" },
      { t: "4.6 · RAG in 30 lines", id: "rag" },
      { t: "4.7 · Citations", id: "cite" },
      { t: "4.8 · Memory", id: "memory" },
      { t: "4.9 · Project", id: "project" },
    ] },
    { href: "agents.html", num: "5", label: "Agents", sections: [
      { t: "The agent loop — the engine" }, { t: "What is Claude Code, actually?" },
      { t: "Subagents — recursion for agents" }, { t: "Memory — what persists, where" },
      { t: "Patterns: routing · caching · async · progress" },
      { t: "Computer use & Safety" }, { t: "Project: build a data-analyst agent" },
    ] },
    { href: "production.html", num: "6", label: "Production", sections: [
      { t: "Three questions before you ship" },
      { t: "Eval & Testing — does it work, and stay working?" },
      { t: "Guardrails & Security" }, { t: "Observability & Latency" },
      { t: "Wrap-up & topics we didn't cover" },
    ] },
    { href: "workshop.html", num: "7", label: "Workshop", sections: [
      { t: "How the workshop works" }, { t: "Suggestions, in case you want them" },
      { t: "Final Quiz" },
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
  handle.setAttribute("aria-label", "사이드바 접기/펼치기");
  const setCollapsed = (c) => {
    document.body.classList.toggle("rail-collapsed", c);
    handle.textContent = c ? "☰ 목차" : "‹ 접기";
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
