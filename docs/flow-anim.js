// Shared flow-animation layer for the docs diagrams (pairs with mermaid-fx.js).
// Every effect ENCODES MEANING, never decorates:
//   motion = data flow · repetition = loop · contrast = frozen/trained ·
//   disruption = mismatch.
// Declarative use — pages only add attributes, never init code:
//   <div class="mermaid" data-flow="steps pulse-path"
//        data-steps='[{"node":"ASK","cap":"…","lines":"3-9"}]'
//        data-cycle="OBS,VLA,ACT,SIM" data-code="#code-loop">…</div>
//   <div class="fx-morph" data-text="My card was charged twice" data-dims="8"></div>
//   <div class="fx-mismatch" data-model="16" data-sim="14"></div>
// anime.js is progressive juice: if the CDN import fails, everything still
// works via CSS classes + rAF. No autoplay of step-throughs — user-paced.
// The matching CSS lives in style.css (.flowsteps/.flowcap/.fnode-*/.fx-*).

let anime = null;
try {
  anime = await import("https://cdn.jsdelivr.net/npm/animejs@4/lib/anime.esm.min.js");
  if (typeof anime.animate !== "function") anime = null;
} catch (e) { anime = null; }

const REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;

// ── mermaid node/edge lookup (contract: distinct UPPERCASE ids ≥3 chars) ──
const findNode = (svg, id) =>
  svg.querySelector(`g.node[id*="-${id}-"]`) ||
  svg.querySelector(`g.node[id$="-${id}"]`) ||
  svg.querySelector(`g.node[id*="${id}"]`);
const findEdge = (svg, a, b) =>
  svg.querySelector(`path[id^="L_${a}_${b}"]`) ||
  svg.querySelector(`path[id*="${a}_${b}"]`);

function pulseNode(el) { // spring pop on the hot node (anime if present, CSS otherwise)
  if (REDUCED) return;
  el.style.transformBox = "fill-box";
  el.style.transformOrigin = "center";
  if (anime) {
    anime.animate(el, { scale: [1, 1.14, 1], duration: 550, ease: "outElastic(1, .6)" });
  } else {
    el.classList.remove("fnode-pop"); void el.getBoundingClientRect();
    el.classList.add("fnode-pop");
  }
}

// ── steps: functions firing in call order, user-paced ⏮ ▶ controls ──
function initSteps(box, svg) {
  let steps;
  try { steps = JSON.parse(box.dataset.steps || "[]"); } catch (e) { steps = []; }
  if (!steps.length) return;
  const nodes = steps.map((s) => findNode(svg, s.node));
  if (nodes.some((n) => !n)) {
    console.warn("flow-anim steps: missing node", steps.filter((s, i) => !nodes[i]).map((s) => s.node));
  }

  // optional codewalk target: split the excerpt into line spans once
  let codeLines = null;
  if (box.dataset.code) {
    const pre = document.querySelector(box.dataset.code);
    const code = pre && pre.querySelector("code");
    if (code && !code.dataset.cwSplit) {
      const lines = code.textContent.split("\n");
      code.textContent = "";
      codeLines = lines.map((t) => {
        const span = document.createElement("span");
        span.className = "cw-line";
        span.textContent = t + "\n";
        code.appendChild(span);
        return span;
      });
      code.dataset.cwSplit = "1";
      code.__cwLines = codeLines;
    } else if (code) {
      codeLines = code.__cwLines || null;
    }
  }

  const bar = document.createElement("div");
  bar.className = "flowsteps";
  const prev = document.createElement("button"); prev.textContent = "⏮";
  const next = document.createElement("button"); next.textContent = "▶ 다음";
  const reset = document.createElement("button"); reset.textContent = "⟲";
  const count = document.createElement("span"); count.className = "flowcount";
  const cap = document.createElement("div"); cap.className = "flowcap";
  bar.append(prev, next, reset, count);
  box.after(bar); bar.after(cap);

  let idx = -1;
  function render(pop) {
    nodes.forEach((n, i) => {
      if (!n) return;
      n.classList.toggle("fnode-hot", i === idx);
      n.classList.toggle("fnode-dim", idx >= 0 && i !== idx);
    });
    if (idx >= 0 && nodes[idx] && pop) pulseNode(nodes[idx]);
    cap.textContent = idx >= 0 ? steps[idx].cap || "" : "";
    cap.classList.toggle("on", idx >= 0);
    count.textContent = idx >= 0 ? `${idx + 1} / ${steps.length}` : `${steps.length} steps`;
    if (codeLines) {
      codeLines.forEach((l) => l.classList.remove("hot-line"));
      const r = idx >= 0 && steps[idx].lines;
      if (r) {
        const [a, b] = String(r).split("-").map(Number);
        for (let i = (a || 1) - 1; i <= ((b || a) - 1) && i < codeLines.length; i++)
          codeLines[i].classList.add("hot-line");
        const first = codeLines[(a || 1) - 1];
        if (first) first.scrollIntoView({ block: "nearest", behavior: REDUCED ? "auto" : "smooth" });
      }
    }
  }
  next.addEventListener("click", () => { if (idx < steps.length - 1) { idx++; render(true); } });
  prev.addEventListener("click", () => { if (idx > -1) { idx--; render(true); } });
  reset.addEventListener("click", () => { idx = -1; render(false); });
  render(false);
}

// ── pulse-path: a dot forever touring the loop (rAF — dependency-free) ──
function initPulsePath(box, svg) {
  if (REDUCED) return;
  let segs = [];
  const cycle = (box.dataset.cycle || "").split(",").map((s) => s.trim()).filter(Boolean);
  if (cycle.length >= 2) {
    for (let i = 0; i < cycle.length; i++) {
      const p = findEdge(svg, cycle[i], cycle[(i + 1) % cycle.length]);
      if (p) segs.push(p);
    }
  }
  if (!segs.length) { // fallback: ride each dotted (feedback) edge
    segs = [...svg.querySelectorAll('path.edge-pattern-dotted, path[class*="dotted"]')];
  }
  if (!segs.length) return;

  const chains = cycle.length >= 2 ? [segs] : segs.map((p) => [p]); // tour vs per-edge
  const dots = chains.map((chain) => {
    const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
    dot.setAttribute("r", "4.5");
    dot.setAttribute("class", "flowdot");
    chain[0].parentNode.appendChild(dot);
    const lens = chain.map((p) => { try { return p.getTotalLength(); } catch (e) { return 0; } });
    return { chain, lens, total: lens.reduce((a, b) => a + b, 0), dot };
  });

  let running = false, raf = 0, t0 = 0;
  const PERIOD = 2600 * (cycle.length >= 2 ? Math.max(1, chains[0].length / 2) : 1);
  function tick(ts) {
    if (!t0) t0 = ts;
    const t = ((ts - t0) % PERIOD) / PERIOD;
    for (const d of dots) {
      if (!d.total) continue;
      let at = t * d.total, i = 0;
      while (i < d.lens.length - 1 && at > d.lens[i]) { at -= d.lens[i]; i++; }
      const pt = d.chain[i].getPointAtLength(Math.min(at, d.lens[i]));
      d.dot.setAttribute("cx", pt.x); d.dot.setAttribute("cy", pt.y);
    }
    if (running) raf = requestAnimationFrame(tick);
  }
  const io = new IntersectionObserver((es) => { // only spend CPU while visible
    es.forEach((e) => {
      if (e.isIntersecting && !running) { running = true; raf = requestAnimationFrame(tick); }
      else if (!e.isIntersecting && running) { running = false; cancelAnimationFrame(raf); }
    });
  }, { threshold: 0.1 });
  io.observe(box);
}

// ── freeze-train: frozen node still & desaturated, trained node breathes ──
function initFreezeTrain(box, svg) {
  const setup = (id, cls) => {
    const n = id && findNode(svg, id);
    if (!n) return;
    n.style.transformBox = "fill-box"; n.style.transformOrigin = "center";
    n.classList.add(cls);
  };
  setup(box.dataset.frozen, "fnode-frozen");
  setup(box.dataset.trained, "fnode-breathe");
}

// ── fx-morph widget: a text string collapses into a bar vector ──
function initMorph(el) {
  const text = el.dataset.text || "hello";
  const dims = Math.max(4, Math.min(16, Number(el.dataset.dims) || 8));
  el.innerHTML = "";
  const t = document.createElement("div"); t.className = "fx-morph-text"; t.textContent = `"${text}"`;
  const arrow = document.createElement("div"); arrow.className = "fx-morph-arrow"; arrow.textContent = "→ embed() →";
  const bars = document.createElement("div"); bars.className = "fx-morph-bars";
  const hs = [];
  for (let i = 0; i < dims; i++) { // deterministic heights from the text itself
    const h = 18 + ((text.charCodeAt(i % text.length) * (i + 3)) % 42);
    hs.push(h);
    const b = document.createElement("div"); b.className = "fx-bar"; b.style.height = "0px";
    bars.appendChild(b);
  }
  const lab = document.createElement("div"); lab.className = "fx-label";
  lab.textContent = `${dims} numbers (실제로는 384차원)`;
  el.append(t, arrow, bars, lab);

  let played = false;
  function play() {
    const els = [...bars.children];
    els.forEach((b) => (b.style.height = "0px"));
    t.style.opacity = "1"; t.style.transform = "none";
    if (REDUCED) { els.forEach((b, i) => (b.style.height = hs[i] + "px")); return; }
    if (anime) {
      anime.animate(t, { opacity: [1, 0.35], scale: [1, 0.92], duration: 500, ease: "outQuad" });
      anime.animate(els, {
        height: (b, i) => hs[i] + "px",
        delay: anime.stagger ? anime.stagger(60, { start: 250 }) : 250,
        duration: 480, ease: "outBack(1.4)",
      });
    } else {
      els.forEach((b, i) => setTimeout(() => { b.style.height = hs[i] + "px"; }, 250 + i * 60));
      t.style.opacity = "0.35";
    }
  }
  addReplay(el, play);
  const io = new IntersectionObserver((es) => {
    es.forEach((e) => { if (e.isIntersecting && !played) { played = true; play(); io.unobserve(el); } });
  }, { threshold: 0.4 });
  io.observe(el);
}

// ── fx-mismatch widget: model outputs N bars, the sim expects M slots ──
function initMismatch(el) {
  const N = Number(el.dataset.model) || 16;
  const M = Number(el.dataset.sim) || 14;
  el.innerHTML = "";
  const mk = (n, cls, label) => {
    const wrap = document.createElement("div"); wrap.className = "fx-row";
    const lab = document.createElement("div"); lab.className = "fx-label"; lab.textContent = label;
    const row = document.createElement("div"); row.className = "fx-bars " + cls;
    for (let i = 0; i < n; i++) {
      const b = document.createElement("div");
      b.className = "fx-bar"; b.style.height = 14 + ((i * 37) % 30) + "px";
      row.appendChild(b);
    }
    wrap.append(lab, row); el.appendChild(wrap);
    return row;
  };
  const model = mk(N, "model", `model output · action dim = ${N}`);
  const sim = mk(M, "sim", `sim expects · action dim = ${M}`);
  const verdict = document.createElement("div"); verdict.className = "fx-verdict"; el.appendChild(verdict);

  let played = false;
  function play() {
    const mBars = [...model.children], sBars = [...sim.children];
    mBars.forEach((b) => { b.classList.remove("cut", "shake"); b.style.opacity = "1"; });
    sBars.forEach((b) => b.classList.remove("pad"));
    verdict.textContent = "";
    const extras = mBars.slice(M);              // truncated
    const gaps = sBars.slice(N);                // zero-padded
    const finish = () => {
      verdict.textContent = extras.length
        ? `⚠️ force-fit: ${extras.length}개 잘림(truncate) — 루프는 돌지만 이 몸에 맞는 동작이 아님`
        : gaps.length
          ? `⚠️ force-fit: ${gaps.length}개 zero-pad — 루프는 돌지만 이 몸에 맞는 동작이 아님`
          : "✓ dims match";
    };
    if (REDUCED) { extras.forEach((b) => b.classList.add("cut")); gaps.forEach((b) => b.classList.add("pad")); finish(); return; }
    extras.forEach((b, i) => setTimeout(() => b.classList.add("shake"), 200 + i * 90));
    setTimeout(() => {
      extras.forEach((b, i) => setTimeout(() => b.classList.add("cut"), i * 90));
      gaps.forEach((b, i) => setTimeout(() => b.classList.add("pad"), i * 90));
      setTimeout(finish, extras.length * 90 + 350);
    }, 200 + extras.length * 90 + 500);
  }
  addReplay(el, play);
  const io = new IntersectionObserver((es) => {
    es.forEach((e) => { if (e.isIntersecting && !played) { played = true; play(); io.unobserve(el); } });
  }, { threshold: 0.4 });
  io.observe(el);
}

function addReplay(el, play) { // same affordance as mermaid-fx's ▶
  const btn = document.createElement("button");
  btn.className = "mreplay"; btn.textContent = "▶"; btn.title = "애니메이션 다시 재생";
  btn.addEventListener("click", play);
  el.style.position = "relative";
  el.appendChild(btn);
}

// ── boot: diagrams need mermaid's SVGs; widgets can go immediately ──
function wireDiagrams() {
  document.querySelectorAll(".mermaid[data-flow]").forEach((box) => {
    const svg = box.querySelector("svg");
    if (!svg) return;
    const fx = (box.dataset.flow || "").split(/\s+/);
    if (fx.includes("steps")) initSteps(box, svg);
    if (fx.includes("pulse-path")) initPulsePath(box, svg);
    if (fx.includes("freeze-train")) initFreezeTrain(box, svg);
  });
}
document.querySelectorAll(".fx-morph").forEach(initMorph);
document.querySelectorAll(".fx-mismatch").forEach(initMismatch);

if (window.__mermaidFxDone) wireDiagrams();
else {
  document.addEventListener("mermaid-fx:done", wireDiagrams, { once: true });
  setTimeout(() => { if (!window.__mermaidFxDone) wireDiagrams(); }, 3500); // belt & suspenders
}
