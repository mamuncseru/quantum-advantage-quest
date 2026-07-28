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

  /* ---- shared: a row of bit toggles -------------------------------- */

  function bitToggles(parent, label, bits, onChange) {
    var wrap = h("span", "qq-bits", parent);
    h("span", "qq-bits-l", wrap, label);
    var btns = [];
    bits.forEach(function (_, i) {
      var b = h("button", "qq-chip", wrap, String(bits[i]));
      b.type = "button";
      b.addEventListener("click", function () {
        bits[i] = bits[i] ? 0 : 1;
        b.textContent = String(bits[i]);
        b.className = "qq-chip" + (bits[i] ? " qq-chip-on" : "");
        onChange();
      });
      if (bits[i]) b.className = "qq-chip qq-chip-on";
      btns.push(b);
    });
    return { btns: btns, sync: function () {
      btns.forEach(function (b, i) {
        b.textContent = String(bits[i]);
        b.className = "qq-chip" + (bits[i] ? " qq-chip-on" : "");
      });
    } };
  }

  function bitsToInt(bits) {          // bits[0] is the most significant
    var v = 0, i;
    for (i = 0; i < bits.length; i++) v = (v << 1) | bits[i];
    return v;
  }

  function intToStr(v, n) {
    var out = "", i;
    for (i = n - 1; i >= 0; i--) out += (v >> i) & 1;
    return out;
  }

  /* =================================================================
   * F · what the Bernstein-Vazirani box computes: s . x mod 2
   * ================================================================= */

  function animBvMask(root) {
    var n = 5;
    var f = frame(root, "What the box computes: pick, then count",
      "The secret s selects which of your bits are looked at. Everything " +
      "else you set is ignored. The box adds up the surviving bits and " +
      "hands back one bit: even or odd. That single bit is the entire " +
      "answer to your question — which is why you have to ask n times.");

    var sbits = [1, 0, 1, 1, 0], xbits = [1, 1, 0, 0, 1];
    var W = 580, Hh = 226;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var cx = [], i;
    for (i = 0; i < n; i++) cx.push(140 + i * 62);

    function rowLabel(y, txt) {
      var t = s("text", { x: 126, y: y + 5, class: "qq-t-end qq-muted qq-sm" },
        svg);
      t.textContent = txt;
    }
    rowLabel(46, "secret  s");
    rowLabel(108, "your input  x");
    rowLabel(170, "s AND x");

    var cellS = [], cellX = [], cellP = [];
    for (i = 0; i < n; i++) {
      (function (i) {
        var g1 = s("g", {}, svg);
        cellS.push({
          r: s("rect", { x: cx[i] - 16, y: 30, width: 32, height: 32, rx: 6,
            class: "qq-bit" }, g1),
          t: s("text", { x: cx[i], y: 52, class: "qq-t-mid qq-bit-t" }, g1)
        });
        var g2 = s("g", { class: "qq-bitcell" }, svg);
        g2.style.cursor = "pointer";
        cellX.push({
          r: s("rect", { x: cx[i] - 16, y: 92, width: 32, height: 32, rx: 6,
            class: "qq-bit qq-bit-in" }, g2),
          t: s("text", { x: cx[i], y: 114, class: "qq-t-mid qq-bit-t" }, g2)
        });
        g2.addEventListener("click", function () {
          xbits[i] = xbits[i] ? 0 : 1; draw();
        });
        var g3 = s("g", {}, svg);
        cellP.push({
          r: s("rect", { x: cx[i] - 16, y: 154, width: 32, height: 32, rx: 6,
            class: "qq-bit" }, g3),
          t: s("text", { x: cx[i], y: 176, class: "qq-t-mid qq-bit-t" }, g3)
        });
      })(i);
    }
    var outT = s("text", { x: W - 20, y: 176, class: "qq-t-end qq-ink" }, svg);
    var noteT = s("text", { x: 140, y: 212, class: "qq-t qq-muted qq-sm" },
      svg);

    function draw() {
      var kept = 0, ignored = 0;
      for (var i = 0; i < n; i++) {
        var p = sbits[i] & xbits[i];
        cellS[i].t.textContent = sbits[i];
        cellS[i].r.setAttribute("class",
          "qq-bit" + (sbits[i] ? " qq-bit-on" : ""));
        cellX[i].t.textContent = xbits[i];
        cellX[i].r.setAttribute("class",
          "qq-bit qq-bit-in" + (xbits[i] ? " qq-bit-on" : ""));
        cellP[i].t.textContent = p;
        cellP[i].r.setAttribute("class",
          "qq-bit" + (p ? " qq-bit-on" : ""));
        cellP[i].r.setAttribute("opacity", sbits[i] ? "1" : "0.28");
        cellX[i].r.setAttribute("opacity", sbits[i] ? "1" : "0.45");
        kept += p;
        if (!sbits[i] && xbits[i]) ignored++;
      }
      outT.textContent = "f(x) = " + (kept & 1);
      outT.setAttribute("class", "qq-t-end " + ((kept & 1) ? "qq-hot"
        : "qq-ink"));
      noteT.textContent = kept + " surviving 1s → " +
        ((kept & 1) ? "odd → 1" : "even → 0") +
        (ignored ? "   (" + ignored + " of your bits ignored entirely)" : "");
    }

    var ctr = h("div", "qq-ctrl", f.body);
    var tog = bitToggles(ctr, "secret s =", sbits, function () { draw(); });
    btn(ctr, "new secret", function () {
      for (var i = 0; i < n; i++) sbits[i] = Math.random() < 0.5 ? 0 : 1;
      tog.sync(); draw();
    }, "qq-btn-ghost");
    draw();
  }

  /* =================================================================
   * G · same circuit, different problem — the spectrum switcher
   * ================================================================= */

  function animSpectrum(root) {
    var n = 5, N = 1 << n;
    var f = frame(root, "One circuit, three problems, three spectra", null);

    var sbits = [1, 0, 1, 1, 0];
    var PROBS = ["constant   f(x) = 0",
                 "linear (BV)   f(x) = s·x",
                 "balanced, not linear",
                 "no promise at all   f = AND"];
    var st = { prob: PROBS[1] };

    var W = 640, Hh = 214, pad = 24, top = 58, base = 170;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var bw = (W - 2 * pad) / N, bars = [], i;
    for (i = 0; i < N; i++) {
      bars.push(s("rect", { x: pad + i * bw + 1.2, width: bw - 2.4,
        class: "qq-bar qq-pos" }, svg));
    }
    s("line", { x1: pad, y1: base, x2: W - pad, y2: base, class: "qq-axis" },
      svg);
    var headline = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, svg);
    var sub = s("text", { x: pad, y: 43, class: "qq-t qq-muted qq-sm" }, svg);
    var tick = s("text", { x: 0, y: base + 18, class: "qq-t-mid qq-hot qq-sm" },
      svg);

    function fval(x) {
      if (st.prob === PROBS[0]) return 0;
      if (st.prob === PROBS[1]) {
        var v = 0, sv = bitsToInt(sbits);
        for (var k = 0; k < n; k++) v ^= ((x >> k) & 1) & ((sv >> k) & 1);
        return v;
      }
      if (st.prob === PROBS[2]) {              // x0 XOR (x1 AND x2)
        return (((x >> (n - 1)) & 1) ^
          (((x >> (n - 2)) & 1) & ((x >> (n - 3)) & 1))) & 1;
      }
      return (((x >> (n - 1)) & 1) & ((x >> (n - 2)) & 1)) & 1;
    }

    function draw() {
      var a = new Float64Array(N), i, m = 0;
      for (i = 0; i < N; i++) a[i] = (fval(i) & 1 ? -1 : 1) / Math.sqrt(N);
      walsh(a);
      for (i = 0; i < N; i++) m = Math.max(m, Math.abs(a[i]));
      var scale = (base - top) / (m > 1e-9 ? m : 1), peak = 0;
      for (i = 0; i < N; i++) {
        var hgt = Math.abs(a[i]) * scale;
        bars[i].setAttribute("y", base - hgt);
        bars[i].setAttribute("height", Math.max(hgt, 0.8));
        bars[i].setAttribute("class", "qq-bar " +
          (a[i] < -1e-12 ? "qq-neg" : "qq-pos"));
        if (Math.abs(a[i]) > Math.abs(a[peak])) peak = i;
      }
      var spike = a[peak] * a[peak] > 0.999;
      tick.setAttribute("x", pad + peak * bw + bw / 2);
      tick.textContent = spike ? intToStr(peak, n) : "";
      if (st.prob === PROBS[0]) {
        headline.textContent = "all the mass sits at frequency 0";
        sub.textContent = "the DJ readout: “did we come home?” — yes, " +
          "with certainty";
      } else if (st.prob === PROBS[1]) {
        headline.textContent = "a single spike, standing exactly on s = " +
          intToStr(bitsToInt(sbits), n);
        sub.textContent = "one measurement returns all " + n +
          " bits of the secret — read the label off the bar";
      } else if (st.prob === PROBS[2]) {
        headline.textContent = "balanced, but the mass is spread";
        sub.textContent = "nothing at frequency 0 (so DJ still says " +
          "“balanced”) — but no single answer to read off";
      } else {
        headline.textContent = "no promise: the spectrum is a mess";
        sub.textContent = "frequency 0 is non-zero and so is everything " +
          "else — both questions become meaningless";
      }
    }

    var ctr = h("div", "qq-ctrl", f.body);
    var sel = h("select", "qq-sel", ctr);
    PROBS.forEach(function (p) { var o = h("option", null, sel, p);
      o.value = p; });
    sel.value = st.prob;
    sel.addEventListener("change", function () { st.prob = sel.value; draw(); });
    bitToggles(ctr, "s =", sbits, function () { draw(); });

    h("div", "qq-fig-note", f.wrap,
      "The gates never change — this is the identical Hadamard sandwich " +
      "from autopsy 01, with one oracle call. Only the promise on f " +
      "changes. What you are looking at is the Fourier spectrum of " +
      "(−1)^f, and each problem writes its answer in a different " +
      "place: Deutsch–Jozsa asks only whether the leftmost bar " +
      "survived; Bernstein–Vazirani reads the position of the spike. " +
      "The power was never in the circuit.");
    draw();
  }

  /* =================================================================
   * H · why a character's transform is a delta: orthogonality
   * ================================================================= */

  function animOrthogonality(root) {
    var n = 4, N = 1 << n;
    var f = frame(root, "Why the spike is exact: 16 terms that cancel",
      "The amplitude landing on frequency y is the sum of (−1) raised " +
      "to (s ⊕ y)·x over every input x. Match y to s and every " +
      "term is +1, so they pile up. Miss by even one bit and the terms " +
      "split exactly half and half, cancelling to zero. No approximation " +
      "anywhere — this is why Bernstein–Vazirani never fails.");

    var sb = [1, 0, 1, 1], yb = [1, 0, 1, 1];
    var W = 620, Hh = 132;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var tw = 30, x0 = 26, tiles = [];
    for (var i = 0; i < N; i++) {
      var g = s("g", {}, svg);
      tiles.push({
        r: s("rect", { x: x0 + i * (tw + 6), y: 34, width: tw, height: tw,
          rx: 5, class: "qq-bit" }, g),
        t: s("text", { x: x0 + i * (tw + 6) + tw / 2, y: 54,
          class: "qq-t-mid qq-bit-t" }, g)
      });
    }
    s("text", { x: 26, y: 24, class: "qq-t qq-muted qq-sm" }, svg)
      .textContent = "one term per input x  →  (−1)^((s⊕y)·x)";
    var totalT = s("text", { x: 26, y: 104, class: "qq-t qq-ink" }, svg);
    var verdictT = s("text", { x: W - 26, y: 104, class: "qq-t-end qq-muted" },
      svg);

    function draw() {
      var d = bitsToInt(sb) ^ bitsToInt(yb), sum = 0;
      for (var x = 0; x < N; x++) {
        var par = 0;
        for (var k = 0; k < n; k++) par ^= ((d >> k) & 1) & ((x >> k) & 1);
        var v = par ? -1 : 1;
        sum += v;
        tiles[x].t.textContent = par ? "−" : "+";
        tiles[x].r.setAttribute("class",
          "qq-bit " + (par ? "qq-tile-neg" : "qq-tile-pos"));
      }
      totalT.textContent = "sum = " + sum + "   →   amplitude = " +
        (sum / N).toFixed(2);
      var match = d === 0;
      verdictT.textContent = match
        ? "y = s : every term agrees"
        : "y ≠ s : exactly 8 plus, 8 minus";
      verdictT.setAttribute("class", "qq-t-end " +
        (match ? "qq-hot" : "qq-muted"));
    }

    var ctr = h("div", "qq-ctrl", f.body);
    bitToggles(ctr, "secret s =", sb, function () { draw(); });
    bitToggles(ctr, "test freq y =", yb, function () { draw(); });
    draw();
  }

  /* =================================================================
   * I · Simon's promise: inputs are glued into pairs
   * ================================================================= */

  function animCoset(root) {
    var n = 4, N = 1 << n;
    var f = frame(root, "Every input has exactly one partner",
      "f gives the same answer on x and on x ⊕ s, and on no other " +
      "pair. So the 16 inputs are glued into 8 couples, and every couple " +
      "is separated by the same hidden step s. Click any input to see its " +
      "partner; change s and the whole pairing rewires at once.");

    var sb = [1, 0, 1, 1];
    var W = 620, Hh = 178, cw = 34, x0 = 28;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var arcs = s("g", {}, svg), cells = [];
    for (var i = 0; i < N; i++) {
      (function (i) {
        var g = s("g", { class: "qq-bitcell" }, svg);
        g.style.cursor = "pointer";
        var r = s("rect", { x: x0 + i * cw, y: 26, width: cw - 6, height: 26,
          rx: 5, class: "qq-bit" }, g);
        var t = s("text", { x: x0 + i * cw + (cw - 6) / 2, y: 44,
          class: "qq-t-mid qq-bit-t qq-sm" }, g);
        t.textContent = intToStr(i, n);
        t.setAttribute("font-size", "9.5");
        cells.push({ r: r, t: t });
        g.addEventListener("click", function () { st.sel = i; draw(); });
      })(i);
    }
    var info = s("text", { x: 28, y: 166, class: "qq-t qq-muted qq-sm" }, svg);
    var st = { sel: 0 };

    function draw() {
      var sv = bitsToInt(sb), i;
      while (arcs.firstChild) arcs.removeChild(arcs.firstChild);
      if (sv === 0) {
        info.textContent = "s = 0000 is not allowed: every input would be " +
          "its own partner and f would be one-to-one.";
        for (i = 0; i < N; i++) {
          cells[i].r.setAttribute("class", "qq-bit");
          cells[i].r.setAttribute("opacity", "0.4");
        }
        return;
      }
      var partner = st.sel ^ sv;
      for (i = 0; i < N; i++) {
        var j = i ^ sv, on = (i === st.sel || i === partner);
        cells[i].r.setAttribute("opacity", "1");
        cells[i].r.setAttribute("class", "qq-bit" + (on ? " qq-bit-on" : ""));
        if (i < j) {                              // one arc per couple
          var xa = x0 + i * cw + (cw - 6) / 2,
              xb = x0 + j * cw + (cw - 6) / 2,
              dep = 26 + Math.min(58, Math.abs(j - i) * 5);
          s("path", { d: "M" + xa + " 56 Q " + (xa + xb) / 2 + " " +
            (56 + dep) + " " + xb + " 56",
            class: "qq-arc" + (on ? " qq-arc-on" : "") }, arcs);
        }
      }
      info.textContent = "s = " + intToStr(sv, n) + "   ·   " +
        intToStr(st.sel, n) + " ⊕ " + intToStr(sv, n) + " = " +
        intToStr(partner, n) + "   ·   8 couples, one hidden step";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    bitToggles(ctr, "hidden s =", sb, function () { draw(); });
    draw();
  }

  /* =================================================================
   * J · the centrepiece: measure register 2, then interfere
   * ================================================================= */

  function animSimonComb(root) {
    var n = 4, N = 1 << n;
    var f = frame(root, "Measure the second register first — then it is obvious",
      null);

    var sb = [1, 0, 1, 1];
    var st = { act: 0, x0: 6 };
    var W = 640, Hh = 224, pad = 26, top = 62, base = 178;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var bw = (W - 2 * pad) / N, bars = [], labels = [];
    for (var i = 0; i < N; i++) {
      bars.push(s("rect", { x: pad + i * bw + 2.5, width: bw - 5,
        class: "qq-bar qq-pos" }, svg));
      var t = s("text", { x: pad + i * bw + bw / 2, y: base + 15,
        class: "qq-t-mid qq-muted" }, svg);
      t.setAttribute("font-size", "9");
      t.textContent = intToStr(i, n);
      labels.push(t);
    }
    s("line", { x1: pad, y1: base, x2: W - pad, y2: base, class: "qq-axis" },
      svg);
    var head = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, svg);
    var sub = s("text", { x: pad, y: 44, class: "qq-t qq-muted qq-sm" }, svg);
    var foot = s("text", { x: pad, y: Hh - 8, class: "qq-t qq-muted qq-sm" },
      svg);

    function amps() {
      var sv = bitsToInt(sb) || 1, a = new Float64Array(N), i;
      if (st.act === 0) {
        for (i = 0; i < N; i++) a[i] = 1 / Math.sqrt(N);
      } else if (st.act === 1) {
        for (i = 0; i < N; i++) a[i] = 1 / Math.sqrt(N);
      } else if (st.act === 2) {
        a[st.x0] = 1 / Math.SQRT2;
        a[st.x0 ^ sv] = 1 / Math.SQRT2;
      } else {
        a[st.x0] = 1 / Math.SQRT2;
        a[st.x0 ^ sv] = 1 / Math.SQRT2;
        walsh(a);
      }
      return a;
    }

    function draw() {
      var sv = bitsToInt(sb) || 1, a = amps(), i, m = 0;
      for (i = 0; i < N; i++) m = Math.max(m, Math.abs(a[i]));
      var scale = (base - top) / (m > 1e-9 ? m : 1);
      for (i = 0; i < N; i++) {
        var hgt = Math.abs(a[i]) * scale;
        bars[i].setAttribute("y", base - hgt);
        bars[i].setAttribute("height", Math.max(hgt, 0.7));
        var par = popcount(i & sv) & 1;             // y . s
        var cls = a[i] < -1e-12 ? "qq-neg" : "qq-pos";
        if (st.act === 3) cls = par ? "qq-neg" : "qq-pos";
        bars[i].setAttribute("class", "qq-bar " + cls);
        bars[i].setAttribute("opacity",
          st.act === 3 && Math.abs(a[i]) < 1e-9 ? "0.18" : "1");
        labels[i].setAttribute("class", "qq-t-mid " +
          (st.act === 3 && !par ? "qq-hot" : "qq-muted"));
      }
      var texts = [
        ["register 1: every input at once",
         "register 2 is still empty; nothing has been asked yet"],
        ["one oracle call — the registers are now entangled",
         "each |x⟩ is tied to its answer |f(x)⟩; the second " +
         "register no longer factors out, unlike autopsies 01 and 02"],
        ["measure register 2 — you may, and it makes the rest obvious",
         "seeing one f-value leaves register 1 on exactly the two " +
         "inputs that share it: x₀ = " + intToStr(st.x0, n) +
         " and x₀ ⊕ s = " + intToStr(st.x0 ^ sv, n)],
        ["apply H⊗ⁿ to those two spikes",
         "the two paths cancel wherever y·s = 1, and reinforce " +
         "wherever y·s = 0 — every surviving bar is one free equation"]
      ];
      head.textContent = texts[st.act][0];
      sub.textContent = texts[st.act][1];
      foot.textContent = st.act === 3
        ? "highlighted labels are the y you can measure — all satisfy " +
          "y·s = 0.  Half the space is gone, exactly."
        : "s = " + intToStr(sv, n);
      slider.value = st.act;
    }

    var ctr = h("div", "qq-ctrl", f.body);
    var slider = h("input", "qq-range", ctr);
    slider.type = "range"; slider.min = 0; slider.max = 3; slider.step = 1;
    slider.value = 0;
    slider.addEventListener("input", function () {
      st.act = +slider.value; draw();
    });
    btn(ctr, "step ▸", function () { st.act = (st.act + 1) % 4; draw(); });
    btn(ctr, "different collapse", function () {
      st.x0 = Math.floor(Math.random() * N); draw();
    }, "qq-btn-ghost");
    bitToggles(ctr, "s =", sb, function () { draw(); });

    h("div", "qq-fig-note", f.wrap,
      "You never actually have to measure register 2 — the maths is the " +
      "same either way. But you are allowed to, and pretending you did " +
      "turns a page of algebra into a picture: two spikes, one " +
      "interference pattern, half the outcomes annihilated. Each run " +
      "hands you a random y from the surviving half, which is one linear " +
      "equation about s.");
    draw();
  }

  /* =================================================================
   * K · quantum samples + classical algebra
   * ================================================================= */

  function animConstraints(root) {
    var n = 4, N = 1 << n;
    var f = frame(root, "Each run halves the list of suspects",
      "The machine never tells you s. It hands you a random y with " +
      "y·s = 0, which rules out every candidate that disagrees. " +
      "Three good equations are enough to go from fifteen suspects to " +
      "one — and this is why the algorithm is quantum sampling plus " +
      "ordinary linear algebra.");

    var sTrue = 0b1011, st = { alive: [], ys: [] };
    function reset() {
      st.alive = [];
      for (var c = 1; c < N; c++) st.alive.push(c);
      st.ys = [];
      draw();
    }

    var W = 620, Hh = 150;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var chips = [], cw = 38, x0 = 26;
    for (var c = 1; c < N; c++) {
      (function (c) {
        var g = s("g", {}, svg);
        var r = s("rect", { x: x0 + (c - 1) * cw, y: 30, width: cw - 6,
          height: 24, rx: 5, class: "qq-bit" }, g);
        var t = s("text", { x: x0 + (c - 1) * cw + (cw - 6) / 2, y: 46,
          class: "qq-t-mid qq-bit-t" }, g);
        t.setAttribute("font-size", "9");
        t.textContent = intToStr(c, n);
        chips[c] = { r: r, t: t };
      })(c);
    }
    var eqT = s("text", { x: 26, y: 82, class: "qq-t qq-muted qq-sm" }, svg);
    var statT = s("text", { x: 26, y: 108, class: "qq-t qq-ink" }, svg);
    var doneT = s("text", { x: 26, y: 132, class: "qq-t qq-hot qq-sm" }, svg);

    function draw() {
      for (var c = 1; c < N; c++) {
        var live = st.alive.indexOf(c) >= 0;
        chips[c].r.setAttribute("class", "qq-bit" +
          (live ? (c === sTrue && st.alive.length === 1 ? " qq-bit-on" : "")
            : ""));
        chips[c].r.setAttribute("opacity", live ? "1" : "0.16");
        chips[c].t.setAttribute("opacity", live ? "1" : "0.25");
      }
      eqT.textContent = st.ys.length
        ? "equations so far:  " + st.ys.map(function (y) {
            return intToStr(y, n) + "·s = 0"; }).join("    ")
        : "no equations yet — every non-zero string is still a suspect";
      statT.textContent = st.alive.length + " candidate" +
        (st.alive.length === 1 ? "" : "s") + " left";
      doneT.textContent = st.alive.length === 1
        ? "solved: s = " + intToStr(st.alive[0], n) +
          "   (" + st.ys.length + " runs, " + st.ys.length + " queries)"
        : "";
    }

    function runOnce() {
      if (st.alive.length <= 1) return;
      var pool = [];                       // the y with y . sTrue = 0
      for (var y = 1; y < N; y++) if (!(popcount(y & sTrue) & 1)) pool.push(y);
      var y2 = pool[Math.floor(Math.random() * pool.length)];
      st.ys.push(y2);
      st.alive = st.alive.filter(function (c) {
        return !(popcount(y2 & c) & 1);
      });
      draw();
    }

    var ctr = h("div", "qq-ctrl", f.body);
    btn(ctr, "run the circuit once", runOnce);
    btn(ctr, "start over", reset, "qq-btn-ghost");
    reset();
  }

  /* ---- shared number theory + DFT ---------------------------------- */

  function gcd(a, b) { while (b) { var t = a % b; a = b; b = t; } return a; }

  function modpow(a, e, m) {
    var r = 1;
    a %= m;
    while (e > 0) {
      if (e & 1) r = (r * a) % m;
      a = (a * a) % m;
      e >>= 1;
    }
    return r;
  }

  function orderOf(a, N) {
    var v = a % N, k = 1;
    while (v !== 1 && k <= N) { v = (v * a) % N; k++; }
    return v === 1 ? k : null;
  }

  function dftProbs(re, im) {
    /* |sum_j psi_j e^{-2pi i jc/M}|^2 / M  — the QFT readout. */
    var M = re.length, out = new Float64Array(M), c, j;
    for (c = 0; c < M; c++) {
      var sr = 0, si = 0;
      for (j = 0; j < M; j++) {
        if (re[j] === 0 && im[j] === 0) continue;
        var ang = -2 * Math.PI * j * c / M,
            co = Math.cos(ang), sn = Math.sin(ang);
        sr += re[j] * co - im[j] * sn;
        si += re[j] * sn + im[j] * co;
      }
      out[c] = (sr * sr + si * si) / M;
    }
    return out;
  }

  function convergents(num, den, limit) {
    /* continued-fraction convergents of num/den */
    var out = [], a = num, b = den,
        h0 = 0, h1 = 1, k0 = 1, k1 = 0;
    while (b && out.length < (limit || 12)) {
      var q = Math.floor(a / b), t;
      t = a - q * b; a = b; b = t;
      t = q * h1 + h0; h0 = h1; h1 = t;
      t = q * k1 + k0; k0 = k1; k1 = t;
      out.push({ q: q, num: h1, den: k1 });
    }
    return out;
  }

  /* =================================================================
   * L · the clock that comes home: order finding, and the reduction
   * ================================================================= */

  function animModOrder(root) {
    var f = frame(root, "Multiply, over and over, until you get back to 1",
      null);

    var st = { N: 15, a: 7 };
    var W = 660, Hh = 230;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var chain = s("g", {}, svg);
    var head = s("text", { x: 24, y: 26, class: "qq-t qq-ink" }, svg);
    var lineR = s("text", { x: 24, y: 132, class: "qq-t qq-ink" }, svg);
    var step1 = s("text", { x: 24, y: 158, class: "qq-t qq-muted qq-sm" }, svg);
    var step2 = s("text", { x: 24, y: 180, class: "qq-t qq-muted qq-sm" }, svg);
    var verdict = s("text", { x: 24, y: 210, class: "qq-t qq-hot" }, svg);

    function draw() {
      while (chain.firstChild) chain.removeChild(chain.firstChild);
      var N = st.N, a = st.a, r = orderOf(a, N);
      head.textContent = "N = " + N + ",  a = " + a +
        "   —   keep multiplying by " + a + ", mod " + N + ":";

      var vals = [1], v = 1, i;
      for (i = 0; i < (r || 1); i++) { v = (v * a) % N; vals.push(v); }
      var bw = Math.min(50, (W - 60) / vals.length);
      for (i = 0; i < vals.length; i++) {
        var last = i === vals.length - 1;
        s("rect", { x: 24 + i * bw, y: 48, width: bw - 8, height: 34, rx: 6,
          class: "qq-bit" + ((i === 0 || last) ? " qq-bit-on" : "") }, chain);
        var t = s("text", { x: 24 + i * bw + (bw - 8) / 2, y: 70,
          class: "qq-t-mid qq-bit-t" }, chain);
        t.textContent = vals[i];
        var lab = s("text", { x: 24 + i * bw + (bw - 8) / 2, y: 98,
          class: "qq-t-mid qq-muted" }, chain);
        lab.setAttribute("font-size", "9.5");
        lab.textContent = a + "^" + i;
        if (i < vals.length - 1) {
          var ar = s("text", { x: 24 + i * bw + bw - 6, y: 70,
            class: "qq-t-mid qq-muted" }, chain);
          ar.setAttribute("font-size", "11");
          ar.textContent = "›";
        }
      }
      lineR.textContent = "it comes home after r = " + r + " steps   " +
        "(the ORDER of " + a + " mod " + N + ")";

      if (r % 2 === 1) {
        step1.textContent = "r is odd, so a^(r/2) is not a whole number.";
        step2.textContent = "";
        verdict.textContent = "no factor from this a — pick another " +
          "(about half of them work)";
        return;
      }
      var x = modpow(a, r / 2, N);
      step1.textContent = "r is even, so x = " + a + "^" + (r / 2) +
        " mod " + N + " = " + x + "   — and x² = " +
        ((x * x) % N) + " mod " + N + ", a square root of 1";
      if (x === N - 1) {
        step2.textContent = "but x = N − 1 = −1, which is the boring " +
          "square root of 1.";
        verdict.textContent = "no factor from this a — pick another";
        return;
      }
      var g1 = gcd(x - 1, N), g2 = gcd(x + 1, N);
      step2.textContent = "gcd(" + (x - 1) + ", " + N + ") = " + g1 +
        "    gcd(" + (x + 1) + ", " + N + ") = " + g2;
      var good = (g1 > 1 && g1 < N) ? g1 : ((g2 > 1 && g2 < N) ? g2 : null);
      verdict.textContent = good
        ? "FACTORED:  " + N + " = " + good + " × " + (N / good)
        : "no factor from this a — pick another";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", ctr, "N =");
    [15, 21, 33, 35].forEach(function (N) {
      btn(ctr, String(N), function () {
        st.N = N;
        var a = 2;
        while (gcd(a, N) !== 1) a++;
        st.a = a;
        draw();
      }, "qq-btn-ghost");
    });
    btn(ctr, "try another a", function () {
      var a = st.a;
      do { a = a + 1 > st.N - 1 ? 2 : a + 1; } while (gcd(a, st.N) !== 1);
      st.a = a;
      draw();
    });
    h("div", "qq-fig-note", f.wrap,
      "Nothing on this page so far is quantum. Finding r by hand means " +
      "walking the chain, and the chain can be astronomically long — for " +
      "an RSA modulus it has more steps than there are atoms in the " +
      "observable universe. Everything else Shor did is exactly the " +
      "arithmetic above: get r, halve it, take two gcds, read off the " +
      "factors.");
    draw();
  }

  /* =================================================================
   * M · Simon, one group over: the comb and its transform
   * ================================================================= */

  function animShorComb(root) {
    var t = 6, M = 1 << t;
    var f = frame(root, "Measure the second register — the first one " +
      "becomes a comb", null);

    var st = { r: 4, act: 0, j0: 2 };
    var W = 660, Hh = 228, pad = 26, top = 62, base = 176;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var bw = (W - 2 * pad) / M, bars = [];
    for (var i = 0; i < M; i++) {
      bars.push(s("rect", { x: pad + i * bw + 1, width: bw - 2,
        class: "qq-bar qq-pos" }, svg));
    }
    s("line", { x1: pad, y1: base, x2: W - pad, y2: base, class: "qq-axis" },
      svg);
    var head = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, svg);
    var sub = s("text", { x: pad, y: 44, class: "qq-t qq-muted qq-sm" }, svg);
    var foot = s("text", { x: pad, y: base + 20,
      class: "qq-t qq-muted qq-sm" }, svg);
    var foot2 = s("text", { x: pad, y: base + 40,
      class: "qq-t qq-muted qq-sm" }, svg);

    function probs() {
      var p = new Float64Array(M), i, k;
      if (st.act === 0 || st.act === 1) {
        for (i = 0; i < M; i++) p[i] = 1 / M;
        return p;
      }
      var idx = [];
      for (i = st.j0 % st.r; i < M; i += st.r) idx.push(i);
      if (st.act === 2) {
        for (k = 0; k < idx.length; k++) p[idx[k]] = 1 / idx.length;
        return p;
      }
      var re = new Float64Array(M), im = new Float64Array(M);
      for (k = 0; k < idx.length; k++) re[idx[k]] = 1 / Math.sqrt(idx.length);
      return dftProbs(re, im);
    }

    function draw() {
      var p = probs(), i, m = 0;
      for (i = 0; i < M; i++) m = Math.max(m, p[i]);
      var scale = (base - top) / (m > 1e-12 ? m : 1);
      for (i = 0; i < M; i++) {
        var hgt = p[i] * scale;
        bars[i].setAttribute("y", base - hgt);
        bars[i].setAttribute("height", Math.max(hgt, 0.6));
        bars[i].setAttribute("class", "qq-bar " +
          (st.act === 3 && p[i] > 0.4 * m ? "qq-hotbar" : "qq-pos"));
      }
      var peaks = [];
      for (i = 0; i < st.r; i++) peaks.push(Math.round(i * M / st.r));
      var texts = [
        ["counting register: every exponent j at once",
         "the work register still holds |1⟩; nothing has been asked"],
        ["compute a^j mod N into the work register",
         "the two registers are now entangled — exactly Simon's step, " +
         "one group over"],
        ["measure the work register",
         "you see one value of a^j. The exponents that could have " +
         "produced it are j₀, j₀+r, j₀+2r, … — an evenly spaced COMB " +
         "of spacing r = " + st.r],
        ["apply the QFT to the comb",
         "a comb of spacing r transforms into a comb of spacing " +
         (M / st.r).toFixed(2) + " = 2^t / r — the peaks sit at " +
         "multiples of 2^t/r"]
      ];
      head.textContent = texts[st.act][0];
      sub.textContent = texts[st.act][1];
      foot.textContent = st.act === 3
        ? "peaks at c ≈ " + peaks.join(", ") +
          "   —   measure any one, and c/2^t ≈ k/r"
        : (st.act === 2 ? "spacing r = " + st.r +
           ", offset j₀ = " + (st.j0 % st.r) + " (random, and harmless)"
           : "");
      foot2.textContent = st.act === 3 && (M % st.r)
        ? "note: r = " + st.r + " does not divide 2^t = " + M +
          ", so the peaks are smeared rather than razor-sharp — " +
          "this is why you need spare precision (§5)."
        : "";
      slider.value = st.act;
    }

    var ctr = h("div", "qq-ctrl", f.body);
    var slider = h("input", "qq-range", ctr);
    slider.type = "range"; slider.min = 0; slider.max = 3; slider.step = 1;
    slider.value = 0;
    slider.addEventListener("input", function () {
      st.act = +slider.value; draw();
    });
    btn(ctr, "step ▸", function () { st.act = (st.act + 1) % 4; draw(); });
    h("span", "qq-bits-l", ctr, "order r =");
    [2, 3, 4, 5, 6, 8].forEach(function (r) {
      btn(ctr, String(r), function () {
        st.r = r; st.j0 = Math.floor(Math.random() * r); draw();
      }, "qq-btn-ghost");
    });

    h("div", "qq-fig-note", f.wrap,
      "Compare autopsy 03. Simon's measurement collapsed register 1 onto " +
      "a coset {x₀, x₀⊕s} and H⊗ⁿ turned it into the " +
      "subspace orthogonal to s. Here the collapse gives an arithmetic " +
      "progression {j₀, j₀+r, …} and the QFT turns it into " +
      "multiples of 2^t/r. Same machine; XOR has become addition, and a " +
      "hidden mask has become a hidden period.");
    draw();
  }

  /* =================================================================
   * N · why 2m+1 counting qubits
   * ================================================================= */

  function animPrecision(root) {
    var f = frame(root, "How much precision do you actually need?",
      "The measured c is useless unless c/2^t is close enough to k/r " +
      "that continued fractions can only land on r. Too few counting " +
      "qubits and neighbouring fractions blur together; enough, and the " +
      "recovery becomes essentially certain. That threshold is where " +
      "the recipe t = 2m+1 comes from.");

    var st = { r: 6, t: 5 };
    var W = 660, Hh = 190, pad = 26, top = 40, base = 150;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var barsG = s("g", {}, svg);
    s("line", { x1: pad, y1: base, x2: W - pad, y2: base, class: "qq-axis" },
      svg);
    var head = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, svg);
    var foot = s("text", { x: pad, y: base + 24,
      class: "qq-t qq-muted qq-sm" }, svg);

    function draw() {
      while (barsG.firstChild) barsG.removeChild(barsG.firstChild);
      var M = 1 << st.t, r = st.r, i, k;
      var re = new Float64Array(M), im = new Float64Array(M);
      var idx = [];
      for (i = 0; i < M; i += r) idx.push(i);
      for (k = 0; k < idx.length; k++) re[idx[k]] = 1 / Math.sqrt(idx.length);
      var p = dftProbs(re, im), m = 0, good = 0;
      for (i = 0; i < M; i++) m = Math.max(m, p[i]);
      var bw = (W - 2 * pad) / M;
      for (i = 0; i < M; i++) {
        var hgt = p[i] / (m || 1) * (base - top);
        // does continued fractions on c/2^t recover r?
        var cs = convergents(i, M), den = 0;
        for (k = 0; k < cs.length; k++) if (cs[k].den <= r) den = cs[k].den;
        var ok = den === r;
        if (ok) good += p[i];
        s("rect", { x: pad + i * bw + 0.6, y: base - hgt,
          width: Math.max(bw - 1.2, 0.8), height: Math.max(hgt, 0.5),
          class: "qq-bar " + (ok ? "qq-pos" : "qq-neg") }, barsG);
      }
      head.textContent = "true order r = " + r + ",  t = " + st.t +
        " counting qubits (2^t = " + M + ")";
      foot.textContent = "blue outcomes recover r by continued " +
        "fractions, amber ones do not  —  success probability ≈ " +
        good.toFixed(3);
    }

    var ctr = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", ctr, "counting qubits t");
    var sl = h("input", "qq-range", ctr);
    sl.type = "range"; sl.min = 3; sl.max = 8; sl.step = 1; sl.value = 5;
    sl.addEventListener("input", function () { st.t = +sl.value; draw(); });
    h("span", "qq-bits-l", ctr, "order r =");
    [3, 5, 6, 7].forEach(function (r) {
      btn(ctr, String(r), function () { st.r = r; draw(); }, "qq-btn-ghost");
    });
    draw();
  }

  /* =================================================================
   * O · continued fractions: the classical finish
   * ================================================================= */

  function animContFrac(root) {
    var f = frame(root, "Turning a measured number back into the order",
      "The machine hands you c. You know 2^t. The order is hiding in " +
      "c/2^t as the denominator of a nearby simple fraction, and " +
      "continued fractions find it by building better and better " +
      "approximations until the denominator would get too large to be " +
      "an order mod N.");

    var st = { c: 21, t: 6, N: 15 };
    var W = 660, Hh = 170;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var head = s("text", { x: 24, y: 26, class: "qq-t qq-ink" }, svg);
    var rowsG = s("g", {}, svg);
    var verdict = s("text", { x: 24, y: 150, class: "qq-t qq-hot" }, svg);

    function draw() {
      while (rowsG.firstChild) rowsG.removeChild(rowsG.firstChild);
      var M = 1 << st.t;
      head.textContent = "measured c = " + st.c + ",  c / 2^t = " +
        st.c + "/" + M + " = " + (st.c / M).toFixed(6);
      var cs = convergents(st.c, M), i, best = null;
      var hdr = s("text", { x: 24, y: 52, class: "qq-t qq-muted qq-sm" },
        rowsG);
      hdr.textContent = "convergents (each one a better simple fraction):";
      for (i = 0; i < cs.length && i < 6; i++) {
        var x = 24 + i * 104;
        var okDen = cs[i].den <= st.N;
        s("rect", { x: x, y: 66, width: 94, height: 40, rx: 6,
          class: "qq-bit" + (okDen ? "" : "") }, rowsG);
        var tx = s("text", { x: x + 47, y: 84, class: "qq-t-mid qq-bit-t" },
          rowsG);
        tx.textContent = cs[i].num + " / " + cs[i].den;
        var tv = s("text", { x: x + 47, y: 99, class: "qq-t-mid qq-muted" },
          rowsG);
        tv.setAttribute("font-size", "9.5");
        tv.textContent = (cs[i].num / cs[i].den).toFixed(5);
        if (okDen) best = cs[i];
      }
      verdict.textContent = best
        ? "largest denominator below N: r = " + best.den +
          "   —   now check a^" + best.den + " mod N = 1"
        : "no usable convergent";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", ctr, "measured c =");
    [0, 16, 21, 32, 43, 48].forEach(function (c) {
      btn(ctr, String(c), function () { st.c = c; draw(); }, "qq-btn-ghost");
    });
    draw();
  }

  /* ---- registry + hydration --------------------------------------- */

  var ANIMS = {
    oracle: animOracle,
    modorder: animModOrder,
    shorcomb: animShorComb,
    precision: animPrecision,
    contfrac: animContFrac,
    collapse: animCollapse,
    kickback: animKickback,
    sandwich: animSandwich,
    interferometer: animInterferometer,
    bvmask: animBvMask,
    spectrum: animSpectrum,
    orthogonality: animOrthogonality,
    coset: animCoset,
    simoncomb: animSimonComb,
    constraints: animConstraints
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
