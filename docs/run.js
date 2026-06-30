// "Run it live" button for the project pages.
//
// Each project page drops a placeholder:
//   <div class="runbox" data-app="extractor" data-local="#local"></div>
// and this script renders a button that asks the LAUNCHER service to spin up a
// throwaway container, polls until it's ready, then links to the live URL.
//
// The launcher is an on-demand spawner you run on YOUR server (see docs/infra
// or the launcher design). Until you set LAUNCHER_BASE, the button stays in
// "local only" mode: clicking it just reveals the page's "Run it locally"
// section so the page is never a dead end.
(function () {
  // ── configure this once the launcher is deployed, e.g.:
  //    const LAUNCHER_BASE = "https://launch.bit-habit.com";
  const LAUNCHER_BASE = ""; // empty → local-only mode
  const POLL_MS = 2500;
  const POLL_MAX = 48; // ~2 min before giving up

  const boxes = document.querySelectorAll(".runbox");
  if (!boxes.length) return;

  for (const box of boxes) {
    const app = box.dataset.app;
    const localSel = box.dataset.local || "#local";

    const btn = document.createElement("button");
    btn.className = "runbtn";
    const state = document.createElement("span");
    state.className = "runstate";
    box.append(btn, state);

    if (!LAUNCHER_BASE) {
      btn.textContent = "▶ Run it live";
      btn.title = "Live run needs the launcher service; this opens local-run steps for now";
      state.innerHTML =
        'Live run is not wired up yet — <a href="' + localSel + '">run it locally ↓</a>.';
      btn.addEventListener("click", () => {
        const t = document.querySelector(localSel);
        if (t) t.scrollIntoView({ behavior: "smooth", block: "start" });
      });
      continue;
    }

    btn.textContent = "▶ Run it live";
    let polls = 0;
    const fail = (msg) => {
      state.innerHTML = "⚠️ " + msg + ' — <a href="' + localSel + '">run it locally ↓</a>.';
      btn.disabled = false;
      btn.textContent = "▶ Try again";
    };
    const ready = (url) => {
      state.innerHTML = '✅ Ready — <a href="' + url + '" target="_blank" rel="noopener">open the app ↗</a> (it shuts down when idle).';
      btn.disabled = false;
      btn.textContent = "▶ Run again";
    };
    const poll = (id) => {
      if (polls++ > POLL_MAX) return fail("took too long to start");
      fetch(LAUNCHER_BASE + "/status/" + encodeURIComponent(id))
        .then((r) => r.json())
        .then((d) => {
          if (d.state === "ready" && d.url) return ready(d.url);
          if (d.state === "error") return fail(d.message || "launch failed");
          state.textContent = "⏳ Starting… (" + (d.state || "pending") + ")";
          setTimeout(() => poll(id), POLL_MS);
        })
        .catch(() => fail("could not reach the launcher"));
    };
    btn.addEventListener("click", () => {
      btn.disabled = true;
      btn.textContent = "⏳ Starting…";
      state.textContent = "⏳ Asking the server to start a container…";
      polls = 0;
      fetch(LAUNCHER_BASE + "/launch", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ app }),
      })
        .then((r) => r.json())
        .then((d) => {
          if (d.url && d.state === "ready") return ready(d.url);
          if (d.id) return poll(d.id);
          fail(d.message || "launch failed");
        })
        .catch(() => fail("could not reach the launcher"));
    });
  }
})();
