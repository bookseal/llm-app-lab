// Shared mermaid visual system for every docs page.
// One place for: dark theme, shape-based auto-coloring, the reveal animation
// (nodes fade in, then edges draw themselves), the "core" glow, and a ▶ replay
// button. Pages just load this instead of their own inline mermaid.initialize.
// The matching CSS lives once in style.css (.mermaid / .mreveal / .core / .mreplay).
import mermaid from "https://cdn.jsdelivr.net/npm/mermaid@11/dist/mermaid.esm.min.mjs";

mermaid.initialize({
  startOnLoad: false,
  theme: "dark",
  themeVariables: {
    background: "#161b22", primaryColor: "#161b22", primaryTextColor: "#e6edf3",
    primaryBorderColor: "#30363d", lineColor: "#8b949e",
    fontFamily: "-apple-system, system-ui, sans-serif", fontSize: "15px",
  },
  flowchart: { curve: "basis", nodeSpacing: 45, rankSpacing: 55 },
});
await mermaid.run();

// ── Role palette (one place). [fill, stroke] on the dark canvas. ──
const ROLE = {
  decision: ["#241a2e", "#a371f7"], // rhombus  → a choice
  data:     ["#2a2410", "#d29322"], // cylinder → a store
  startend: ["#11271a", "#3fb950"], // stadium/circle → start or end
  io:       ["#0d1f33", "#58a6ff"], // plain box → a step
};
// Auto-color nodes by SHAPE, but only nodes mermaid marks `.default` (i.e. NO
// classDef) — so any node given an explicit classDef (04B, 05A, …) keeps its
// hand color, because mermaid names it `node <classdef>` instead of `default`.
function autoColor(svg) {
  svg.querySelectorAll("g.node.default").forEach((node) => {
    const shapes = [...node.querySelectorAll("rect, polygon, circle, ellipse, path")];
    const first = shapes[0];
    if (!first) return;

    const tag = first.tagName.toLowerCase();
    let role = "io";
    if (tag === "polygon") role = "decision";
    else if (tag === "circle" || tag === "ellipse") role = "startend";
    else if (tag === "path") role = "data";
    else if (tag === "rect") {
      let rx = parseFloat(first.getAttribute("rx") || "0");
      let h = 1; try { h = first.getBBox().height || 1; } catch (e) {}
      role = rx > h * 0.35 ? "startend" : "io"; // stadium vs plain box
    }
    const [fill, stroke] = ROLE[role];
    shapes.forEach((s) => { s.style.fill = fill; s.style.stroke = stroke; });
  });
}

// ── Reveal: nodes fade in staggered, then edges draw themselves. ──
function reveal(svg) {
  if (!svg) return;
  const nodes = [...svg.querySelectorAll(
    ".node, .cluster, .actor, .labelText, .messageText, .note, .loopText")];
  nodes.forEach((el, i) => {
    el.classList.remove("reveal"); void el.getBoundingClientRect();
    el.style.animationDelay = (i * 60) + "ms"; el.classList.add("reveal");
  });
  const edges = [...svg.querySelectorAll(
    ".edgePaths path, path.flowchart-link, .flowchart-link, path.messageLine0, path.messageLine1")];
  const base = nodes.length * 60;
  edges.forEach((p, i) => {
    let len = 0; try { len = p.getTotalLength(); } catch (e) {}
    if (!len) return;
    p.style.transition = "none";
    p.style.strokeDasharray = len; p.style.strokeDashoffset = len;
    void p.getBoundingClientRect();
    const d = base + i * 65;
    p.style.transition = "stroke-dashoffset .45s ease " + d + "ms";
    p.style.strokeDashoffset = "0";
    setTimeout(() => { // restore so dotted edges look normal again
      p.style.transition = ""; p.style.strokeDasharray = ""; p.style.strokeDashoffset = "";
    }, d + 700);
  });
}

// ── Wire every diagram: auto-color now, play on first scroll-in, ▶ to replay. ──
const io = new IntersectionObserver((entries) => {
  entries.forEach((e) => {
    if (!e.isIntersecting) return;
    reveal(e.target.querySelector("svg"));
    io.unobserve(e.target);
  });
}, { threshold: 0.15 });

document.querySelectorAll(".mermaid").forEach((box) => {
  const svg = box.querySelector("svg");
  if (!svg) return;
  autoColor(svg);
  io.observe(box);
  const btn = document.createElement("button");
  btn.className = "mreplay";
  btn.textContent = "▶";
  btn.title = "애니메이션 다시 재생";
  btn.addEventListener("click", () => reveal(box.querySelector("svg")));
  box.appendChild(btn);
});

// signal downstream layers (flow-anim.js) that every SVG is rendered & wired
window.__mermaidFxDone = true;
document.dispatchEvent(new Event("mermaid-fx:done"));
