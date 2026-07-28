/* qq-anim.js — interactive figures for the autopsies.
 *
 * No dependencies (house rule: nothing loads from a CDN). Every widget is
 * built from inline SVG, styled entirely through CSS custom properties so
 * light/dark themes come for free, and degrades to a readable static state
 * when JS is off or prefers-reduced-motion is set.
 *
 * Usage in markdown:  <div class="qq-anim" data-anim="sandwich"></div>
 */

(function () {
  "use strict";

  var NS = "http://www.w3.org/2000/svg";

  function reduced() {
    return window.matchMedia &&
      window.matchMedia("(prefers-reduced-motion: reduce)").matches;
  }

  function s(tag, attrs, parent) {
    var e = document.createElementNS(NS, tag);
    for (var k in attrs || {}) e.setAttribute(k, attrs[k]);
    if (parent) parent.appendChild(e);
    return e;
  }

  function h(tag, cls, parent, text) {
    var e = document.createElement(tag);
    if (cls) e.className = cls;
    if (text !== undefined && text !== null) e.textContent = text;
    if (parent) parent.appendChild(e);
    return e;
  }

  function frame(root, title, caption) {
    root.innerHTML = "";
    var wrap = h("div", "qq-fig", root);
    if (title) h("div", "qq-fig-title", wrap, title);
    var body = h("div", "qq-fig-body", wrap);
    var foot = null;
    if (caption) foot = h("div", "qq-fig-note", wrap, caption);
    return { wrap: wrap, body: body, foot: foot };
  }

  function btn(parent, label, onClick, cls) {
    var b = h("button", "qq-btn" + (cls ? " " + cls : ""), parent, label);
    b.type = "button";
    b.addEventListener("click", onClick);
    return b;
  }

  /* ---- math ------------------------------------------------------- */

  // H^(x)n applied in place: the Walsh-Hadamard butterfly, 1/sqrt2 a level.
  function walsh(a) {
    var n = a.length, len, i, j, u, v;
    for (len = 1; len < n; len <<= 1) {
      for (i = 0; i < n; i += len << 1) {
        for (j = i; j < i + len; j++) {
          u = a[j]; v = a[j + len];
          a[j] = (u + v) / Math.SQRT2;
          a[j + len] = (u - v) / Math.SQRT2;
        }
      }
    }
    return a;
  }

  function popcount(x) {
    var c = 0;
    while (x) { x &= x - 1; c++; }
    return c;
  }

  /* =================================================================
   * A · the oracle box: reversibility you can click
   * ================================================================= */

  function animOracle(root) {
    var f = frame(root, "The box you are allowed to ask, but not open",
      "f here is “top bit is 1”. Flip the input bits and watch the " +
      "target. Apply the box twice and you are exactly back where you " +
      "started — that is what reversible means, and it is why the box " +
      "must XOR rather than overwrite.");

    var st = { x: [0, 1, 1], y: 0, applied: 0 };
    var fx = function (x) { return x[0]; };            // "top bit is 1"

    var svg = s("svg", { viewBox: "0 0 460 200", class: "qq-svg" }, f.body);

    // static scaffolding
    s("rect", { x: 175, y: 38, width: 110, height: 124, rx: 10,
      class: "qq-box" }, svg);
    var boxLabel = s("text", { x: 230, y: 92, class: "qq-t-mid qq-ink" }, svg);
    boxLabel.textContent = "U_f";
    var boxSub = s("text", { x: 230, y: 114, class: "qq-t-mid qq-muted qq-sm" },
      svg);
    boxSub.textContent = "sealed";

    var rows = [
      { y: 58, label: "x₀" }, { y: 84, label: "x₁" },
      { y: 110, label: "x₂" }, { y: 148, label: "y" }
    ];
    var bits = [];
    rows.forEach(function (r, i) {
      s("line", { x1: 60, y1: r.y, x2: 175, y2: r.y, class: "qq-wire" }, svg);
      s("line", { x1: 285, y1: r.y, x2: 400, y2: r.y, class: "qq-wire" }, svg);
      var lab = s("text", { x: 30, y: r.y + 4, class: "qq-t qq-muted" }, svg);
      lab.textContent = r.label;
      var g = s("g", { class: "qq-bitcell" }, svg);
      var rect = s("rect", { x: 40, y: r.y - 12, width: 24, height: 24, rx: 5,
        class: "qq-bit qq-bit-in" }, g);
      var txt = s("text", { x: 52, y: r.y + 5, class: "qq-t-mid qq-bit-t" }, g);
      var out = s("text", { x: 412, y: r.y + 5, class: "qq-t qq-bit-o" }, svg);
      bits.push({ rect: rect, txt: txt, out: out, i: i, g: g });
      if (i < 3) {
        g.style.cursor = "pointer";
        g.addEventListener("click", function () {
          st.x[i] = st.x[i] ? 0 : 1; st.applied = 0; draw();
        });
      }
    });

    var eq = s("text", { x: 230, y: 186, class: "qq-t-mid qq-muted qq-sm" },
      svg);

    var ctr = h("div", "qq-ctrl", f.body);
    btn(ctr, "apply the box", function () {
      st.applied = (st.applied + 1) % 3; draw();
    });
    btn(ctr, "reset", function () { st.applied = 0; draw(); }, "qq-btn-ghost");
    var tally = h("span", "qq-readout", ctr, "");

    function draw() {
      var val = fx(st.x);
      var y = st.applied % 2 === 1 ? (st.y ^ val) : st.y;
      bits.forEach(function (b) {
        var v = b.i < 3 ? st.x[b.i] : y;
        b.txt.textContent = v;
        b.rect.setAttribute("class",
          "qq-bit " + (b.i < 3 ? "qq-bit-in" : "qq-bit-tgt") +
          (v ? " qq-bit-on" : ""));
        b.out.textContent = b.i < 3 ? "→ " + st.x[b.i]
          : "→ " + y;
        b.out.setAttribute("class", "qq-t qq-bit-o" +
          (b.i === 3 && y !== st.y ? " qq-hot" : ""));
      });
      eq.textContent = "|x⟩|y⟩  ↦  |x⟩|y ⊕ f(x)⟩" +
        "   —   f(" + st.x.join("") + ") = " + val;
      boxSub.textContent = st.applied === 0 ? "sealed" :
        (st.applied === 1 ? "applied once" : "applied twice");
      tally.textContent = st.applied === 2
        ? "back to the start — nothing was erased"
        : (st.applied === 1 ? "target flipped by f(x) = " + val : "");
    }
    draw();
  }

  /* =================================================================
   * B · superposition alone computes nothing (the myth killer)
   * ================================================================= */

  function animCollapse(root) {
    var N = 64;
    var f = frame(root, "What one measurement actually gives you",
      "Sixty-four inputs, all present at once, all equally likely. Press " +
      "measure: the machine hands back a single random input. Do that all " +
      "day and you have learned 64 values the slow way — no better " +
      "than checking by hand.");

    var W = 620, Hh = 150, pad = 26;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var bw = (W - 2 * pad) / N;
    var bars = [];
    for (var i = 0; i < N; i++) {
      bars.push(s("rect", { x: pad + i * bw + 0.6, width: bw - 1.2,
        class: "qq-bar qq-pos" }, svg));
    }
    s("line", { x1: pad, y1: Hh - 26, x2: W - pad, y2: Hh - 26,
      class: "qq-axis" }, svg);
    var note = s("text", { x: W / 2, y: Hh - 8,
      class: "qq-t-mid qq-muted qq-sm" }, svg);

    var st = { collapsed: -1, seen: {}, shots: 0 };

    function draw() {
      var top = 18, hMax = Hh - 26 - top;
      for (var i = 0; i < N; i++) {
        var live = st.collapsed < 0 || st.collapsed === i;
        var hgt = st.collapsed < 0 ? hMax * 0.34 : (live ? hMax : 0);
        bars[i].setAttribute("y", Hh - 26 - hgt);
        bars[i].setAttribute("height", Math.max(hgt, 0));
        bars[i].setAttribute("class", "qq-bar " +
          (st.collapsed === i ? "qq-hotbar" : "qq-pos"));
      }
      note.textContent = st.collapsed < 0
        ? "all 64 inputs in play — nothing measured yet"
        : "collapsed to x = " + st.collapsed + "  —  you learned f at " +
          "one input, chosen for you at random";
      readout.textContent = st.shots
        ? st.shots + " shots → " + Object.keys(st.seen).length +
          " distinct inputs seen of 64"
        : "";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    btn(ctr, "measure", function () {
      st.collapsed = Math.floor(Math.random() * N);
      st.seen[st.collapsed] = 1; st.shots++; draw();
    });
    btn(ctr, "re-prepare", function () { st.collapsed = -1; draw(); },
      "qq-btn-ghost");
    btn(ctr, "×100 shots", function () {
      for (var k = 0; k < 100; k++) {
        st.seen[Math.floor(Math.random() * N)] = 1; st.shots++;
      }
      st.collapsed = Math.floor(Math.random() * N); draw();
    }, "qq-btn-ghost");
    var readout = h("span", "qq-readout", ctr, "");
    draw();
  }

  /* =================================================================
   * C · phase kickback
   * ================================================================= */

  function animKickback(root) {
    var f = frame(root, "Phase kickback: the minus sign bounces back",
      "The target register starts in |−⟩ = (|0⟩ − " +
      "|1⟩)/√2. XOR-ing a 1 into it swaps its two halves, which " +
      "is the same state again wearing a minus sign. The target comes out " +
      "unchanged; the sign lands on the input.");

    var svg = s("svg", { viewBox: "0 0 620 210", class: "qq-svg" }, f.body);
    var st = { fx: 1, t: 0 };

    s("rect", { x: 250, y: 34, width: 110, height: 128, rx: 10,
      class: "qq-box" }, svg);
    var bl = s("text", { x: 305, y: 96, class: "qq-t-mid qq-ink" }, svg);
    bl.textContent = "U_f";
    var bs = s("text", { x: 305, y: 118, class: "qq-t-mid qq-muted qq-sm" },
      svg);
    bs.textContent = "XOR into target";

    s("line", { x1: 120, y1: 66, x2: 250, y2: 66, class: "qq-wire" }, svg);
    s("line", { x1: 360, y1: 66, x2: 505, y2: 66, class: "qq-wire" }, svg);
    s("line", { x1: 120, y1: 130, x2: 250, y2: 130, class: "qq-wire" }, svg);
    s("line", { x1: 360, y1: 130, x2: 505, y2: 130, class: "qq-wire" }, svg);

    var inTop = s("text", { x: 112, y: 71, class: "qq-t-end qq-ink" }, svg);
    inTop.textContent = "|x⟩";
    var inBot = s("text", { x: 112, y: 135, class: "qq-t-end qq-ink" }, svg);
    inBot.textContent = "|−⟩";
    var outTop = s("text", { x: 513, y: 71, class: "qq-t qq-ink" }, svg);
    var outBot = s("text", { x: 513, y: 135, class: "qq-t qq-ink" }, svg);

    s("text", { x: 60, y: 26, class: "qq-t qq-muted qq-sm" }, svg)
      .textContent = "input register";
    s("text", { x: 60, y: 174, class: "qq-t qq-muted qq-sm" }, svg)
      .textContent = "target register";

    // the travelling minus sign
    var spark = s("text", { x: 305, y: 130, class: "qq-t-mid qq-spark" }, svg);
    spark.textContent = "−";
    spark.setAttribute("opacity", "0");

    var expl = s("text", { x: 305, y: 196, class: "qq-t-mid qq-muted qq-sm" },
      svg);

    function draw() {
      var neg = st.fx === 1;
      outTop.textContent = (neg ? "−" : "+") + "|x⟩";
      outTop.setAttribute("class", "qq-t qq-ink" + (neg ? " qq-hot" : ""));
      outBot.textContent = "|−⟩";
      expl.textContent = neg
        ? "(|1⟩ − |0⟩)/√2  =  −(|0⟩ − " +
          "|1⟩)/√2  —  same state, minus sign freed"
        : "f(x) = 0: nothing flips, no sign";
      spark.setAttribute("opacity", "0");
      if (neg && !reduced()) {
        spark.setAttribute("opacity", "1");
        spark.setAttribute("x", "305"); spark.setAttribute("y", "130");
        var t0 = null;
        var step = function (ts) {
          if (t0 === null) t0 = ts;
          var u = Math.min((ts - t0) / 900, 1);
          spark.setAttribute("y", 130 - 64 * u);
          spark.setAttribute("x", 305 + 150 * u);
          spark.setAttribute("opacity", u < 0.85 ? 1 : (1 - u) / 0.15);
          if (u < 1) requestAnimationFrame(step);
        };
        requestAnimationFrame(step);
      }
    }

    var ctr = h("div", "qq-ctrl", f.body);
    btn(ctr, "f(x) = 1  (flip)", function () { st.fx = 1; draw(); });
    btn(ctr, "f(x) = 0  (no flip)", function () { st.fx = 0; draw(); },
      "qq-btn-ghost");
    draw();
  }

  /* =================================================================
   * D · the sandwich, three acts (centrepiece)
   * ================================================================= */

  function animSandwich(root) {
    var n = 6, N = 1 << n;
    var f = frame(root, "The sandwich, one layer at a time", null);

    var FS = {
      "constant  f(x) = 0": function () { return 0; },
      "constant  f(x) = 1": function () { return 1; },
      "balanced  f(x) = parity(x)": function (x) { return popcount(x) & 1; },
      "balanced  f(x) = top bit": function (x) { return (x >> (n - 1)) & 1; },
      "NOT in the promise  f = AND(top 2)":
        function (x) { return ((x >> (n - 1)) & (x >> (n - 2))) & 1; }
    };
    var names = Object.keys(FS);
    var st = { fname: names[2], act: 0 };

    // header band (y < 48) is reserved for the act label and the readout,
    // so full-height bars in acts 1-2 can never sit under the text
    var W = 640, Hh = 212, pad = 24, top = 56, base = 168;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var bw = (W - 2 * pad) / N;
    var bars = [];
    for (var i = 0; i < N; i++) {
      bars.push(s("rect", { x: pad + i * bw + 0.7, width: bw - 1.4,
        class: "qq-bar qq-pos" }, svg));
    }
    s("line", { x1: pad, y1: base, x2: W - pad, y2: base, class: "qq-axis" },
      svg);
    // the |0...0> readout marker
    var mark = s("rect", { x: pad - 1, y: top - 6, width: bw + 2,
      height: base - top + 12, class: "qq-mark" }, svg);
    var markLbl = s("text", { x: pad + bw / 2, y: top - 12,
      class: "qq-t-mid qq-muted qq-sm" }, svg);
    markLbl.textContent = "|0…0⟩";
    var actLbl = s("text", { x: W - pad, y: 22, class: "qq-t-end qq-ink" },
      svg);
    var meter = s("text", { x: W - pad, y: 41, class: "qq-t-end qq-muted qq-sm" },
      svg);
    var story = s("text", { x: pad, y: Hh - 10, class: "qq-t qq-muted qq-sm" },
      svg);

    function amps() {
      var a = new Float64Array(N), i;
      if (st.act === 0) { a[0] = 1; return a; }
      var fn = FS[st.fname];
      for (i = 0; i < N; i++) a[i] = 1 / Math.sqrt(N);
      if (st.act === 1) return a;
      for (i = 0; i < N; i++) a[i] *= (fn(i) & 1) ? -1 : 1;
      if (st.act === 2) return a;
      return walsh(a);
    }

    var ACTS = [
      ["start", "|0…0⟩ — one certainty, everything else empty"],
      ["act 1 · spread (H⊗ⁿ)",
        "every input now carries the same small amplitude"],
      ["act 2 · stamp (one oracle call)",
        "heights unchanged — only signs moved"],
      ["act 3 · refocus (H⊗ⁿ)",
        "the signs decide whether you come home"]
    ];

    function draw() {
      var a = amps(), i, m = 0;
      for (i = 0; i < N; i++) m = Math.max(m, Math.abs(a[i]));
      var scale = (base - top) / (m > 1e-9 ? m : 1);
      for (i = 0; i < N; i++) {
        var v = a[i], hgt = Math.abs(v) * scale;
        bars[i].setAttribute("y", base - hgt);
        bars[i].setAttribute("height", Math.max(hgt, 0.6));
        bars[i].setAttribute("class", "qq-bar " + (v < -1e-12 ? "qq-neg"
          : "qq-pos"));
      }
      var p0 = a[0] * a[0];
      actLbl.textContent = ACTS[st.act][0];
      story.textContent = ACTS[st.act][1];
      meter.textContent = st.act === 3
        ? "P(|0…0⟩) = " + p0.toFixed(3) + "  →  " +
          (p0 > 0.99 ? "CONSTANT" : (p0 < 0.01 ? "BALANCED" : "—"))
        : "";
      mark.setAttribute("opacity", st.act === 3 ? "1" : "0.25");
      slider.value = st.act;
    }

    var ctr = h("div", "qq-ctrl", f.body);
    var sel = h("select", "qq-sel", ctr);
    names.forEach(function (nm) {
      var o = h("option", null, sel, nm); o.value = nm;
    });
    sel.value = st.fname;
    sel.addEventListener("change", function () {
      st.fname = sel.value; draw();
    });
    var slider = h("input", "qq-range", ctr);
    slider.type = "range"; slider.min = 0; slider.max = 3; slider.step = 1;
    slider.value = 0;
    slider.addEventListener("input", function () {
      st.act = +slider.value; draw();
    });
    btn(ctr, "step ▸", function () {
      st.act = (st.act + 1) % 4; draw();
    });

    h("div", "qq-fig-note", f.wrap,
      "Sixty-four amplitudes (n = 6). Blue is positive, amber negative. " +
      "Watch act 3: for a constant f every sign agrees and the whole " +
      "distribution snaps back onto |0…0⟩; for a balanced f the " +
      "signs cancel there exactly and the amplitude you are testing is " +
      "zero. The last option obeys no promise — the readout lands " +
      "between the two answers and means nothing.");
    draw();
  }

  /* =================================================================
   * E · the interferometer
   * ================================================================= */

  function animInterferometer(root) {
    var f = frame(root, "The same physics as a two-path light experiment",
      "Drag the phase. With both paths in step the light leaves by the " +
      "bright port every time; half a wavelength out of step it leaves by " +
      "the other one. Deutsch–Jozsa is this device with 2ⁿ arms, " +
      "and “did it come out of the bright port?” is the whole " +
      "question the algorithm asks.");

    var W = 620, Hh = 200;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var st = { phi: 0 };

    // beam paths
    s("line", { x1: 40, y1: 100, x2: 150, y2: 100, class: "qq-beam" }, svg);
    s("path", { d: "M150 100 L 260 52 L 370 52 L 470 100",
      class: "qq-beam" }, svg);
    s("path", { d: "M150 100 L 260 148 L 370 148 L 470 100",
      class: "qq-beam" }, svg);
    [[150, 100], [470, 100]].forEach(function (p) {
      s("rect", { x: p[0] - 9, y: p[1] - 9, width: 18, height: 18, rx: 3,
        class: "qq-bs", transform: "rotate(45 " + p[0] + " " + p[1] + ")" },
        svg);
    });
    s("text", { x: 150, y: 128, class: "qq-t-mid qq-muted qq-sm" }, svg)
      .textContent = "split (H)";
    s("text", { x: 470, y: 128, class: "qq-t-mid qq-muted qq-sm" }, svg)
      .textContent = "recombine (H)";
    s("text", { x: 20, y: 104, class: "qq-t-end qq-muted qq-sm" }, svg)
      .textContent = "in";

    // phase shifter on the upper arm
    s("rect", { x: 300, y: 40, width: 26, height: 24, rx: 4,
      class: "qq-phase" }, svg);
    var phLbl = s("text", { x: 313, y: 32, class: "qq-t-mid qq-muted qq-sm" },
      svg);

    // output ports
    var portA = s("circle", { cx: 540, cy: 70, r: 15, class: "qq-port" }, svg);
    var portB = s("circle", { cx: 540, cy: 132, r: 15, class: "qq-port" }, svg);
    s("line", { x1: 470, y1: 100, x2: 525, y2: 74, class: "qq-beam" }, svg);
    s("line", { x1: 470, y1: 100, x2: 525, y2: 128, class: "qq-beam" }, svg);
    var la = s("text", { x: 566, y: 74, class: "qq-t qq-muted qq-sm" }, svg);
    var lb = s("text", { x: 566, y: 136, class: "qq-t qq-muted qq-sm" }, svg);
    s("text", { x: 566, y: 58, class: "qq-t qq-muted qq-sm" }, svg)
      .textContent = "“constant” port";
    s("text", { x: 566, y: 120, class: "qq-t qq-muted qq-sm" }, svg)
      .textContent = "“balanced” port";

    function draw() {
      var phi = st.phi * Math.PI;
      var pa = Math.cos(phi / 2) * Math.cos(phi / 2);
      portA.setAttribute("opacity", (0.12 + 0.88 * pa).toFixed(3));
      portB.setAttribute("opacity", (0.12 + 0.88 * (1 - pa)).toFixed(3));
      la.textContent = (100 * pa).toFixed(0) + "%";
      lb.textContent = (100 * (1 - pa)).toFixed(0) + "%";
      phLbl.textContent = "phase " + (st.phi).toFixed(2) + "π";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    var r = h("input", "qq-range", ctr);
    r.type = "range"; r.min = 0; r.max = 2; r.step = 0.01; r.value = 0;
    r.addEventListener("input", function () { st.phi = +r.value; draw(); });
    btn(ctr, "in step (constant)", function () {
      st.phi = 0; r.value = 0; draw();
    });
    btn(ctr, "out of step (balanced)", function () {
      st.phi = 1; r.value = 1; draw();
    }, "qq-btn-ghost");
    draw();
  }

  /* ---- registry + hydration --------------------------------------- */

  var ANIMS = {
    oracle: animOracle,
    collapse: animCollapse,
    kickback: animKickback,
    sandwich: animSandwich,
    interferometer: animInterferometer
  };

  function hydrate(scope) {
    var nodes = (scope || document).querySelectorAll(".qq-anim");
    Array.prototype.forEach.call(nodes, function (node) {
      if (node.getAttribute("data-qq-ready") === "1") return;
      var fn = ANIMS[node.getAttribute("data-anim")];
      if (!fn) return;
      try {
        fn(node);
        node.setAttribute("data-qq-ready", "1");
      } catch (err) {
        node.setAttribute("data-qq-ready", "1");
        if (window.console) console.error("qq-anim", err);
      }
    });
  }

  if (window.document$ && typeof window.document$.subscribe === "function") {
    window.document$.subscribe(function () { hydrate(document); });
  } else if (document.readyState !== "loading") {
    hydrate(document);
  } else {
    document.addEventListener("DOMContentLoaded", function () {
      hydrate(document);
    });
  }
})();
