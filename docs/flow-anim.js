// Shared flow-animation layer for the docs diagrams (pairs with mermaid-fx.js).
// Every effect ENCODES MEANING, never decorates:
//   the green ball = the COMMON path through the flow, touring forever ·
//   it turns YELLOW when it takes a special-case branch, then goes green again ·
//   contrast = frozen/trained · disruption = mismatch.
// Declarative use — pages only add attributes, never init code:
//   <div class="mermaid" data-flow="pulse-path"
//        data-cycle="CREATE,STOPQ,DISPATCH,APPEND"   ← the common (green) tour
//        data-alt="STOPQ,DONE">…</div>               ← the special-case (yellow) branch
//   <div class="mermaid" data-flow="freeze-train" data-frozen="EMB" data-trained="HEAD">
//   <div class="fx-morph" data-text="My card was charged twice" data-dims="8"></div>
//   <div class="fx-mismatch" data-model="6" data-sim="14"></div>
// anime.js is progressive juice: if the CDN import fails, everything still
// works via CSS + rAF. Honors prefers-reduced-motion.
// The matching CSS lives in style.css (.flowdot/.fnode-*/.fx-*).

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

// ── pulse-path: the ball tours the common path in green; every third lap it
//    takes the special-case branch in yellow, then goes back to green. ──
function initPulsePath(box, svg) {
  if (REDUCED) return;
  const main = (box.dataset.cycle || "").split(",").map((s) => s.trim()).filter(Boolean);
  const alt = (box.dataset.alt || "").split(",").map((s) => s.trim()).filter(Boolean);

  // edges(a→b→c, wrap): consecutive pairs; silently skip pairs with no edge
  // (the ball just jumps — e.g. a linear pipeline restarting at the top).
  const edgesOf = (ids, wrap) => {
    const out = [];
    const last = wrap ? ids.length : ids.length - 1;
    for (let i = 0; i < last; i++) {
      const p = findEdge(svg, ids[i], ids[(i + 1) % ids.length]);
      if (p) out.push(p);
    }
    return out;
  };

  let schedule = []; // [{paths, alt:bool}] — one entry per lap segment-group
  if (main.length >= 2) {
    const mainLap = edgesOf(main, true);
    if (!mainLap.length) return;
    if (alt.length >= 2 && main.includes(alt[0])) {
      // green up to the branch node, then yellow along the special case
      const upto = main.slice(0, main.indexOf(alt[0]) + 1);
      const greenHead = edgesOf(upto, false);
      const yellowTail = edgesOf(alt, false);
      schedule = [
        { paths: mainLap, alt: false },
        { paths: mainLap, alt: false },
        { paths: greenHead, alt: false },
        { paths: yellowTail, alt: true },
      ];
    } else {
      schedule = [{ paths: mainLap, alt: false }];
    }
  } else {
    // no cycle given: ride each dotted (feedback) edge with its own green ball
    const dotted = [...svg.querySelectorAll('path.edge-pattern-dotted, path[class*="dotted"]')];
    if (!dotted.length) return;
    return dotted.forEach((p) => runBall(box, svg, [{ paths: [p], alt: false }]));
  }
  runBall(box, svg, schedule);
}

function runBall(box, svg, schedule) {
  const groups = schedule.map((g) => {
    const lens = g.paths.map((p) => { try { return p.getTotalLength(); } catch (e) { return 0; } });
    return { ...g, lens, total: lens.reduce((a, b) => a + b, 0) };
  }).filter((g) => g.total > 0);
  if (!groups.length) return;

  const dot = document.createElementNS("http://www.w3.org/2000/svg", "circle");
  dot.setAttribute("r", "4.5");
  dot.setAttribute("class", "flowdot");
  groups[0].paths[0].parentNode.appendChild(dot);

  const SPEED = 190; // px per second — same feel regardless of diagram size
  let gi = 0, dist = 0, lastTs = 0, running = false, raf = 0;
  function tick(ts) {
    if (!lastTs) lastTs = ts;
    dist += ((ts - lastTs) / 1000) * SPEED;
    lastTs = ts;
    let g = groups[gi];
    while (dist >= g.total) { // advance to the next lap segment-group
      dist -= g.total;
      gi = (gi + 1) % groups.length;
      g = groups[gi];
      dot.setAttribute("class", g.alt ? "flowdot alt" : "flowdot");
    }
    let at = dist, i = 0;
    while (i < g.lens.length - 1 && at > g.lens[i]) { at -= g.lens[i]; i++; }
    const pt = g.paths[i].getPointAtLength(Math.min(at, g.lens[i]));
    dot.setAttribute("cx", pt.x); dot.setAttribute("cy", pt.y);
    if (running) raf = requestAnimationFrame(tick);
  }
  const io = new IntersectionObserver((es) => { // only spend CPU while visible
    es.forEach((e) => {
      if (e.isIntersecting && !running) { running = true; lastTs = 0; raf = requestAnimationFrame(tick); }
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
