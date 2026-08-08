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

  /* =================================================================
   * DEEP DIVE 01 · the Fourier thread
   *
   * Six widgets, in the order the deep dive uses them:
   *   chardial     orthogonality on Z_N — the terms that cancel
   *   shifteigen   why THIS basis: characters are the eigenvectors of shift
   *   spectrumlab  draw your own f, watch its spectrum
   *   butterfly    the H^(x)n butterfly, one level per qubit
   *   qftleak      Z_N: the comb leaks, and whose fault that is
   *   hsprank      hidden-subgroup sampling until the rank is full
   * ================================================================= */

  function clear(node) {
    while (node.firstChild) node.removeChild(node.firstChild);
  }

  function rangeCtl(parent, label, min, max, val, onInput) {
    h("span", "qq-bits-l", parent, label);
    var r = h("input", "qq-range", parent);
    r.type = "range"; r.min = min; r.max = max; r.step = 1; r.value = val;
    r.addEventListener("input", function () { onInput(+r.value); });
    return r;
  }

  /* ---- P · orthogonality on Z_N: the terms that cancel -------------- */

  function animCharDial(root) {
    var f = frame(root, "The engine: |G| unit vectors that either pile up or cancel",
      "Every entry of a Fourier transform is a sum of |G| unit vectors, " +
      "one per group element. Set the two frequencies equal and every " +
      "vector points the same way, so the sum is the group order. Make " +
      "them differ by anything at all and the vectors are the N-th roots " +
      "of unity in some order — they close a polygon and return to zero " +
      "exactly. No approximation and no large-N limit: this one fact is " +
      "why a Fourier transform can tell frequencies apart, and everything " +
      "else on this page is bookkeeping on top of it.");

    var st = { N: 8, k: 3, l: 3 };
    var W = 660, Hh = 252, ox = 232, oy = 148;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var head = s("text", { x: 24, y: 26, class: "qq-t qq-ink" }, svg);
    var sub = s("text", { x: 24, y: 46, class: "qq-t qq-muted qq-sm" }, svg);
    var val = s("text", { x: W - 24, y: 32, class: "qq-t-end qq-hot" }, svg);
    val.setAttribute("font-size", "17");
    var verdict = s("text", { x: W - 24, y: 52, class: "qq-t-end qq-muted qq-sm" },
      svg);
    var pathG = s("g", {}, svg);
    var kSl, lSl;

    function draw() {
      var N = st.N, d = ((st.k - st.l) % N + N) % N, i;
      var unit = Math.min(27, 300 / N);
      clear(pathG);
      s("line", { x1: ox - 120, y1: oy, x2: ox + 320, y2: oy,
        class: "qq-axis" }, pathG);
      s("circle", { cx: ox, cy: oy, r: 6, fill: "none",
        stroke: "currentColor", "stroke-width": 1.2,
        class: "qq-muted" }, pathG);

      var px = ox, py = oy, pts = [ox + "," + oy];
      for (i = 0; i < N; i++) {
        var ang = 2 * Math.PI * d * i / N;
        px += unit * Math.cos(ang);
        py -= unit * Math.sin(ang);
        pts.push(px.toFixed(2) + "," + py.toFixed(2));
      }
      s("polyline", { points: pts.join(" "), fill: "none",
        stroke: "currentColor", "stroke-width": 2,
        class: d === 0 ? "qq-pos" : "qq-neg",
        "stroke-linejoin": "round" }, pathG)
        .setAttribute("style", d === 0
          ? "stroke: var(--qq-pos)" : "stroke: var(--qq-neg)");
      for (i = 1; i <= N; i++) {
        var xy = pts[i].split(",");
        s("circle", { cx: xy[0], cy: xy[1], r: 2.6,
          class: d === 0 ? "qq-pos" : "qq-neg" }, pathG);
      }
      s("circle", { cx: px, cy: py, r: 7.5, fill: "none",
        "stroke-width": 2, class: "qq-hotbar",
        style: "fill:none;stroke:var(--qq-hot)" }, pathG);

      var mag = Math.hypot(px - ox, py - oy) / unit;
      head.textContent = "Σₓ χ" + st.k + "(x) · χ" + st.l + "(x)*   over " +
        "all " + N + " elements of Z" + N;
      sub.textContent = d === 0
        ? "the two frequencies match: every term is exactly +1"
        : "the frequencies differ by " + d + ": the terms are the " + N +
          "-th roots of unity, each used once";
      val.textContent = "⟨χ" + st.k + ", χ" + st.l + "⟩ / N = " +
        (mag / N).toFixed(3);
      verdict.textContent = d === 0
        ? "the walk never turns — it ends " + N + " steps out"
        : "the walk closes: distance from the origin " +
          (mag < 1e-9 ? "0, exactly" : mag.toFixed(3));
    }

    var ctr = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", ctr, "group Z_N, N =");
    [6, 8, 12, 16].forEach(function (N) {
      btn(ctr, String(N), function () {
        st.N = N;
        st.k = Math.min(st.k, N - 1); st.l = Math.min(st.l, N - 1);
        kSl.max = lSl.max = N - 1; kSl.value = st.k; lSl.value = st.l;
        draw();
      }, "qq-btn-ghost");
    });
    var ctr2 = h("div", "qq-ctrl", f.body);
    kSl = rangeCtl(ctr2, "k", 0, st.N - 1, st.k,
      function (v) { st.k = v; draw(); });
    lSl = rangeCtl(ctr2, "ℓ", 0, st.N - 1, st.l,
      function (v) { st.l = v; draw(); });
    draw();
  }

  /* ---- Q · characters are the eigenvectors of shift ----------------- */

  function animShiftEigen(root) {
    var n = 4, N = 16;
    var f = frame(root, "Why this basis and no other: shift a character and " +
      "nothing moves",
      "Shifting means relabelling x as x ⊕ a. Do it to a character and the " +
      "pattern comes back identical, or identical with every sign flipped " +
      "— one global factor χ_z(a), no change of shape. Do it to anything " +
      "else and the pattern scrambles. Characters are the eigenvectors of " +
      "shift, and that is the entire reason hidden periodicity is visible " +
      "in this basis and invisible in every other one.");

    var st = { a: 5, z: [1, 0, 1, 1], g: null };
    var W = 660, Hh = 268, tw = 30, gap = 4, x0 = 96, ytop = 60;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var rowsG = s("g", {}, svg);
    var head = s("text", { x: 24, y: 26, class: "qq-t qq-ink" }, svg);
    var verdict = s("text", { x: 24, y: 46, class: "qq-t qq-muted qq-sm" }, svg);

    function reshuffle() {
      st.g = [];
      for (var x = 0; x < N; x++) st.g.push(Math.random() < 0.5 ? 1 : -1);
    }
    reshuffle();

    function row(y, label, vals, ref) {
      var t = s("text", { x: x0 - 12, y: y + 21,
        class: "qq-t-end qq-muted qq-sm" }, rowsG);
      t.textContent = label;
      for (var x = 0; x < N; x++) {
        var cx = x0 + x * (tw + gap);
        var changed = ref && ref[x] !== vals[x];
        s("rect", { x: cx, y: y, width: tw, height: 30, rx: 5,
          class: vals[x] > 0 ? "qq-tile-pos" : "qq-tile-neg",
          opacity: changed ? 1 : 0.42 }, rowsG);
        var tx = s("text", { x: cx + tw / 2, y: y + 20,
          class: "qq-t-mid", fill: "#fff" }, rowsG);
        tx.setAttribute("font-size", "12.5");
        tx.setAttribute("font-weight", "700");
        tx.textContent = vals[x] > 0 ? "+" : "−";
        if (changed) {
          s("rect", { x: cx - 2, y: y - 2, width: tw + 4, height: 34, rx: 6,
            class: "qq-mark" }, rowsG);
        }
      }
    }

    function draw() {
      clear(rowsG);
      var z = bitsToInt(st.z), a = st.a, x, chi = [], chiS = [], gS = [];
      for (x = 0; x < N; x++) {
        chi.push(popcount(x & z) & 1 ? -1 : 1);
        chiS.push(popcount((x ^ a) & z) & 1 ? -1 : 1);
        gS.push(st.g[x ^ a]);
      }
      var moved = 0;
      for (x = 0; x < N; x++) if (gS[x] !== st.g[x]) moved++;
      var flips = 0;
      for (x = 0; x < N; x++) if (chiS[x] !== chi[x]) flips++;

      row(ytop, "any old g(x)", st.g, null);
      row(ytop + 42, "g(x ⊕ a)", gS, st.g);
      row(ytop + 104, "character χ_z(x)", chi, null);
      row(ytop + 146, "χ_z(x ⊕ a)", chiS, chi);

      head.textContent = "shift a = " + intToStr(a, n) + "   frequency z = " +
        intToStr(z, n) + "   χ_z(a) = " + (popcount(a & z) & 1 ? "−1" : "+1");
      verdict.textContent = "g had " + moved + " of 16 signs change — its " +
        "shape moved.   The character " +
        (flips === 0 ? "came back identical (χ_z(a) = +1)."
                     : "came back with all 16 signs flipped — one global " +
                       "factor χ_z(a) = −1, the same shape.");
    }

    var ctr = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr, "shift a", 0, 15, st.a, function (v) { st.a = v; draw(); });
    btn(ctr, "new g", function () { reshuffle(); draw(); }, "qq-btn-ghost");
    var ctr2 = h("div", "qq-ctrl", f.body);
    bitToggles(ctr2, "frequency z =", st.z, draw);
    draw();
  }

  /* ---- R · draw your own f and read the spectrum -------------------- */

  function animSpectrumLab(root) {
    var n = 4, N = 16;
    var f = frame(root, "Draw a function, read its spectrum",
      "The circuit is fixed — the Hadamard sandwich of autopsy 01, one " +
      "oracle call. What you are editing is the promise. Every bar is one " +
      "Fourier coefficient of (−1)^f, and one measurement returns a " +
      "single z with probability given by that bar squared. Try to build " +
      "a function you could actually learn something about from one " +
      "sample; then try the bent preset, which is designed so that you " +
      "cannot.");

    var st = { v: [], sel: "linear" };
    var W = 660, Hh = 236, pad = 26, base = 150, top = 34;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var bw = (W - 2 * pad) / N;
    var bars = [], ticks = [], i;
    for (i = 0; i < N; i++) {
      bars.push(s("rect", { x: pad + i * bw + 2.5, width: bw - 5,
        class: "qq-bar qq-pos" }, svg));
      var t = s("text", { x: pad + i * bw + bw / 2, y: base + 30,
        class: "qq-t-mid qq-muted qq-sm" }, svg);
      t.textContent = intToStr(i, n);
      t.setAttribute("font-size", "9");
      t.setAttribute("transform", "rotate(-90 " +
        (pad + i * bw + bw / 2) + " " + (base + 30) + ")");
      ticks.push(t);
    }
    s("line", { x1: pad, y1: base, x2: W - pad, y2: base, class: "qq-axis" },
      svg);
    var mark = s("rect", { y: top - 6, width: bw, height: base - top + 12,
      class: "qq-mark", rx: 4 }, svg);
    var head = s("text", { x: pad, y: 20, class: "qq-t qq-ink" }, svg);
    var stats = h("div", "qq-readout", null);

    var PRESETS = {
      "constant": function () { return 0; },
      "linear  s·x,  s = 1011": function (x) { return popcount(x & 0xB) & 1; },
      "balanced, not linear": function (x) {
        return (((x >> 3) & 1) ^ (((x >> 2) & 1) & ((x >> 1) & 1))) & 1;
      },
      "bent  x₀x₁ ⊕ x₂x₃": function (x) {
        return ((((x >> 3) & 1) & ((x >> 2) & 1)) ^
                (((x >> 1) & 1) & (x & 1))) & 1;
      },
      "AND (no promise)": function (x) { return ((x >> 3) & (x >> 2)) & 1; },
      "random": function () { return Math.random() < 0.5 ? 1 : 0; }
    };

    function load(name) {
      var g = PRESETS[name], x;
      st.v = [];
      for (x = 0; x < N; x++) st.v.push(g(x) & 1);
      st.sel = name;
    }

    function draw() {
      var a = new Float64Array(N), x, m = 0, peak = 0, sup = 0, sum2 = 0;
      for (x = 0; x < N; x++) a[x] = (st.v[x] ? -1 : 1) / 4;   // 1/sqrt(16)
      walsh(a);
      for (x = 0; x < N; x++) {
        m = Math.max(m, Math.abs(a[x]));
        if (Math.abs(a[x]) > 1e-9) sup++;
        sum2 += Math.pow(a[x] * a[x], 2);
        if (Math.abs(a[x]) > Math.abs(a[peak])) peak = x;
      }
      var scale = (base - top) / (m > 1e-9 ? m : 1);
      for (x = 0; x < N; x++) {
        var hgt = Math.abs(a[x]) * scale;
        bars[x].setAttribute("y", base - hgt);
        bars[x].setAttribute("height", Math.max(hgt, 0.9));
        bars[x].setAttribute("class", "qq-bar " +
          (x === peak ? "qq-hotbar" : (a[x] < -1e-12 ? "qq-neg" : "qq-pos")));
      }
      mark.setAttribute("x", pad);
      var ones = 0;
      for (x = 0; x < N; x++) ones += st.v[x];
      head.textContent = "F̂(0) = mean of (−1)^f = " + a[0].toFixed(3) +
        "   (f is 1 on " + ones + " of 16 inputs)";
      var pmax = a[peak] * a[peak], ent = -Math.log(sum2) / Math.LN2;
      var line1 = "support " + sup + "/16 · largest |F̂| at z = " +
        intToStr(peak, n) + " · P(that outcome) = " + pmax.toFixed(3) +
        " · " + ent.toFixed(2) + " bits of spread";
      var line2;
      if (sup === 1 && Math.abs(a[0]) > 0.99) {
        line2 = "constant: all the mass at frequency zero, and " +
          "Deutsch–Jozsa answers with certainty.";
      } else if (sup === 1) {
        line2 = "a single spike at z = " + intToStr(peak, n) +
          " — one measurement returns all 4 bits. This is " +
          "Bernstein–Vazirani, and f is linear.";
      } else if (Math.abs(a[0]) < 1e-9) {
        line2 = "balanced (F̂(0) = 0): DJ still answers in one query, but " +
          "no single outcome carries the function.";
      } else if (pmax < 0.1) {
        line2 = "flat: every outcome is nearly equally likely, so one " +
          "sample carries almost nothing. There is no algorithm here.";
      } else {
        line2 = "outside the promise: frequency zero is non-zero and so is " +
          "much else — both DJ's and BV's questions lose their meaning.";
      }
      stats.innerHTML = "";
      h("div", null, stats, line1);
      h("div", null, stats, line2);
    }

    var chipRow = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", chipRow, "f(x) for x = 0000 … 1111:");
    var chips = [];
    for (i = 0; i < N; i++) {
      (function (x) {
        var b = h("button", "qq-chip", chipRow, "0");
        b.type = "button";
        b.title = "x = " + intToStr(x, n);
        b.addEventListener("click", function () {
          st.v[x] = st.v[x] ? 0 : 1;
          syncChips();
          draw();
        });
        chips.push(b);
      })(i);
    }
    function syncChips() {
      for (var x = 0; x < N; x++) {
        chips[x].textContent = String(st.v[x]);
        chips[x].className = "qq-chip" + (st.v[x] ? " qq-chip-on" : "");
      }
    }
    var ctr = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", ctr, "presets");
    Object.keys(PRESETS).forEach(function (name) {
      btn(ctr, name, function () { load(name); syncChips(); draw(); },
        "qq-btn-ghost");
    });
    f.body.appendChild(stats);
    load("linear  s·x,  s = 1011");
    syncChips();
    draw();
  }

  /* ---- S · the butterfly: one level per qubit ----------------------- */

  function animButterfly(root) {
    var n = 3, N = 8;
    var f = frame(root, "The butterfly: one level per qubit, and that is the " +
      "whole speedup",
      "The classical fast transform sweeps log N levels over N numbers — " +
      "N log N arithmetic operations. The quantum circuit runs the very " +
      "same butterfly, but each level is one Hadamard on one qubit, " +
      "because the group Z₂ⁿ factorises and so does its transform. Three " +
      "gates here, twenty-four numeric operations there. Read the caption " +
      "below the figure before believing this is an FFT speedup — it is " +
      "not.");

    var st = { stage: 0, input: "linear" };
    var W = 660, Hh = 300;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var colX = [110, 280, 450, 610], rowY = [];
    for (var i = 0; i < N; i++) rowY.push(66 + i * 27);
    var linkG = s("g", {}, svg);
    var nodeG = s("g", {}, svg);
    var head = s("text", { x: 24, y: 26, class: "qq-t qq-ink" }, svg);
    var cost = s("text", { x: 24, y: 46, class: "qq-t qq-muted qq-sm" }, svg);

    var INPUTS = {
      "linear": function (x) { return popcount(x & 0x5) & 1; },
      "constant": function () { return 0; },
      "balanced, not linear": function (x) {
        return (((x >> 2) & 1) ^ (((x >> 1) & 1) & (x & 1))) & 1;
      }
    };

    function stages() {
      // integer butterfly, most significant qubit first: distances 4, 2, 1.
      var g = INPUTS[st.input], v = [], out = [], x;
      for (x = 0; x < N; x++) v.push(g(x) & 1 ? -1 : 1);
      out.push(v.slice());
      for (var lvl = 0; lvl < n; lvl++) {
        var dist = 1 << (n - 1 - lvl), w = v.slice();
        for (x = 0; x < N; x++) {
          if ((x & dist) === 0) {
            w[x] = v[x] + v[x + dist];
            w[x + dist] = v[x] - v[x + dist];
          }
        }
        v = w;
        out.push(v.slice());
      }
      return out;
    }

    function draw() {
      var all = stages(), i, x;
      clear(linkG);
      clear(nodeG);
      for (i = 0; i <= n; i++) {
        var t = s("text", { x: colX[i], y: 52,
          class: "qq-t-mid qq-muted qq-sm" }, nodeG);
        t.textContent = i === 0 ? "(−1)^f" : "H on qubit " + (i - 1);
        if (i > st.stage) t.setAttribute("opacity", "0.35");
      }
      for (i = 0; i < st.stage; i++) {
        var dist = 1 << (n - 1 - i);
        for (x = 0; x < N; x++) {
          if ((x & dist) === 0) {
            [[x, x], [x, x + dist], [x + dist, x], [x + dist, x + dist]]
              .forEach(function (pr) {
                s("line", { x1: colX[i] + 20, y1: rowY[pr[0]],
                  x2: colX[i + 1] - 20, y2: rowY[pr[1]],
                  class: "qq-arc" + (i === st.stage - 1 ? " qq-arc-on" : "")
                }, linkG);
              });
          }
        }
      }
      for (i = 0; i <= st.stage; i++) {
        for (x = 0; x < N; x++) {
          var v = all[i][x];
          s("rect", { x: colX[i] - 19, y: rowY[x] - 11, width: 38, height: 22,
            rx: 5, class: v > 0 ? "qq-tile-pos"
              : (v < 0 ? "qq-tile-neg" : "qq-bit"),
            opacity: v === 0 ? 0.45 : 1 }, nodeG);
          var tv = s("text", { x: colX[i], y: rowY[x] + 4,
            class: "qq-t-mid" }, nodeG);
          tv.setAttribute("font-size", "12");
          tv.setAttribute("font-weight", "700");
          tv.setAttribute("fill", v === 0 ? "var(--qq-muted)" : "#fff");
          tv.textContent = String(v);
        }
      }
      for (x = 0; x < N; x++) {
        var lab = s("text", { x: colX[0] - 30, y: rowY[x] + 4,
          class: "qq-t-end qq-muted qq-sm" }, nodeG);
        lab.textContent = intToStr(x, n);
      }
      head.textContent = st.stage === 0
        ? "the phases the oracle left behind, before any transform"
        : "level " + st.stage + " of " + n + ": pairs " +
          (1 << (n - st.stage)) + " apart have been added and subtracted";
      cost.textContent = "quantum gates spent: " + st.stage + "   ·   " +
        "classical additions and subtractions: " + (st.stage * N) +
        (st.stage === n ? "   ·   divide by 2ⁿ = 8 for the amplitudes" : "");
    }

    var ctr = h("div", "qq-ctrl", f.body);
    btn(ctr, "step", function () {
      st.stage = Math.min(n, st.stage + 1); draw();
    });
    btn(ctr, "reset", function () { st.stage = 0; draw(); }, "qq-btn-ghost");
    h("span", "qq-bits-l", ctr, "input f");
    Object.keys(INPUTS).forEach(function (k) {
      btn(ctr, k, function () { st.input = k; st.stage = 0; draw(); },
        "qq-btn-ghost");
    });
    draw();
  }

  /* ---- T · Z_N: the comb leaks, and whose fault that is ------------- */

  function cfConvergents(num, den, qmax) {
    var out = [], pp = 1, qp = 0, a, r, x = num, y = den, p, q, np, nq;
    if (y === 0) return out;
    a = Math.floor(x / y); p = a; q = 1;
    if (q <= qmax) out.push([p, q]);
    r = x - a * y;
    while (r !== 0) {
      x = y; y = r;
      a = Math.floor(x / y);
      np = a * p + pp; nq = a * q + qp;
      pp = p; qp = q; p = np; q = nq;
      if (q > qmax) break;
      out.push([p, q]);
      r = x - a * y;
    }
    return out;
  }

  function recoverPeriod(c, N, qmax) {
    var cs = cfConvergents(c, N, qmax), best = null;
    for (var i = 0; i < cs.length; i++) if (cs[i][1] > 1) best = cs[i][1];
    return best;
  }

  function animQftLeak(root) {
    var f = frame(root, "Change the group and exactness is the first casualty",
      "Over Z₂ⁿ every cancellation was exact. Over Z_N the hidden period " +
      "usually does not divide N, the comb smears into a Dirichlet " +
      "kernel, and Shor's whole analysis is the bound on that smear. Watch " +
      "which failures are approximation (mass off the peaks) and which are " +
      "plain arithmetic: an outcome sitting exactly on a peak still fails " +
      "when its index shares a factor with r, and no amount of precision " +
      "fixes that.");

    var st = { N: 64, r: 5, tries: 0, wins: 0, last: null };
    var W = 660, Hh = 232, pad = 30, base = 158, top = 44;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var barsG = s("g", {}, svg);
    var head = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, svg);
    var sub = s("text", { x: pad, y: 40, class: "qq-t qq-muted qq-sm" }, svg);
    var shot = s("text", { x: pad, y: base + 26, class: "qq-t qq-hot" }, svg);
    var tally = s("text", { x: pad, y: base + 46,
      class: "qq-t qq-muted qq-sm" }, svg);
    s("line", { x1: pad, y1: base, x2: W - pad, y2: base, class: "qq-axis" },
      svg);

    function dist() {                       // exact |QFT of the comb|^2
      var N = st.N, r = st.r, m = Math.ceil(N / r), p = [], c;
      for (c = 0; c < N; c++) {
        var s1 = Math.sin(Math.PI * c * r * m / N);
        var s2 = Math.sin(Math.PI * c * r / N);
        p.push(Math.abs(s2) < 1e-12 ? m / N
                                    : (s1 * s1) / (s2 * s2) / (m * N));
      }
      return p;
    }

    function draw() {
      var N = st.N, r = st.r, p = dist(), c, i;
      var qmax = Math.floor(Math.sqrt(N));
      var bw = (W - 2 * pad) / N, mx = 0, mass = 0, succ = 0;
      for (c = 0; c < N; c++) mx = Math.max(mx, p[c]);
      for (c = 0; c < N; c++) {
        var d = Infinity;
        for (i = 0; i < r; i++) {
          var dd = Math.abs(c - i * N / r);
          d = Math.min(d, dd, N - dd);
        }
        if (d <= 0.5 + 1e-9) mass += p[c];
        if (recoverPeriod(c, N, qmax) === r) succ += p[c];
      }
      clear(barsG);
      for (i = 0; i < r; i++) {
        var mxp = pad + (i * N / r) * bw;
        s("line", { x1: mxp, y1: top - 6, x2: mxp, y2: base,
          class: "qq-mark" }, barsG);
      }
      for (c = 0; c < N; c++) {
        var hgt = (base - top) * p[c] / (mx > 1e-12 ? mx : 1);
        var ok = recoverPeriod(c, N, qmax) === r;
        s("rect", { x: pad + c * bw, y: base - hgt,
          width: Math.max(bw - 0.6, 1), height: Math.max(hgt, 0.6),
          class: "qq-bar " + (ok ? "qq-pos" : "qq-neg"),
          opacity: st.last === c ? 1 : 0.9 }, barsG);
      }
      if (st.last !== null) {
        s("circle", { cx: pad + (st.last + 0.5) * bw, cy: top - 12, r: 5,
          class: "qq-hotbar", style: "fill:var(--qq-hot)" }, barsG);
      }
      head.textContent = "N = " + N + ",  hidden period r = " + r + "   " +
        (N % r === 0 ? "(divides N — no leakage at all)"
                     : "(does not divide N — the comb leaks)");
      sub.textContent = "peak mass " + mass.toFixed(3) +
        "   ·   recovers r (blue) " + succ.toFixed(3) +
        "   ·   arithmetic ceiling φ(r)/r = " + (phi(r) / r).toFixed(3);
      tally.textContent = "convergents bounded by ⌊√N⌋ = " + qmax +
        (st.tries ? "   ·   measured " + st.tries + " times, recovered r in " +
          st.wins : "");
    }

    function phi(m) {
      var c = 0;
      for (var j = 1; j <= m; j++) if (gcd(j, m) === 1) c++;
      return c;
    }

    function measure() {
      var p = dist(), u = Math.random(), acc = 0, c;
      for (c = 0; c < st.N; c++) {
        acc += p[c];
        if (u <= acc) break;
      }
      c = Math.min(c, st.N - 1);
      var qmax = Math.floor(Math.sqrt(st.N));
      var got = recoverPeriod(c, st.N, qmax);
      st.last = c; st.tries++;
      if (got === st.r) st.wins++;
      var cs = cfConvergents(c, st.N, qmax).map(function (pr) {
        return pr[0] + "/" + pr[1];
      }).join(", ");
      draw();
      shot.textContent = "measured c = " + c + "   →   c/N = " + c + "/" +
        st.N + "   →   convergents " + (cs || "none") + "   →   r = " +
        (got === null ? "nothing" : got) +
        (got === st.r ? "  ✓" : "  ✗");
    }

    var ctr = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", ctr, "N =");
    [32, 64, 128].forEach(function (N) {
      btn(ctr, String(N), function () {
        st.N = N; st.last = null; st.tries = 0; st.wins = 0;
        shot.textContent = ""; draw();
      }, "qq-btn-ghost");
    });
    var ctr2 = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr2, "period r", 2, 20, st.r, function (v) {
      st.r = v; st.last = null; st.tries = 0; st.wins = 0;
      shot.textContent = ""; draw();
    });
    btn(ctr2, "measure once", measure);
    draw();
  }

  /* ---- U · sampling a hidden subgroup until the rank is full -------- */

  function animHspRank(root) {
    var n = 4, N = 16;
    var f = frame(root, "One sample is one equation: the hidden-subgroup " +
      "mechanism in full",
      "The oracle hides a period s. Measuring after the transform returns " +
      "a uniformly random z from the annihilator — every z with z·s = 0, " +
      "and nothing else, ever. So each shot is one linear equation about " +
      "s, and the algorithm is finished when n − 1 of them are " +
      "independent. Notice what is *not* happening: no amplitude is being " +
      "read, no coefficient estimated. The quantum part supplies random " +
      "elements of a subgroup, and linear algebra does the rest.");

    var st = { s: [1, 0, 1, 1], rows: [], flags: [] };
    var W = 660, Hh = 256;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var head = s("text", { x: 24, y: 26, class: "qq-t qq-ink" }, svg);
    var rowsG = s("g", {}, svg);
    var verdict = s("text", { x: 24, y: 240, class: "qq-t qq-hot" }, svg);

    function rank(rows) {
      var basis = [], i, j;
      for (i = 0; i < rows.length; i++) {
        var v = rows[i];
        for (j = 0; j < basis.length; j++) {
          var hb = 31 - Math.clz32(basis[j]);
          if ((v >> hb) & 1) v ^= basis[j];
        }
        if (v) basis.push(v);
        basis.sort(function (a, b) { return b - a; });
      }
      return basis.length;
    }

    function sample() {
      var sv = bitsToInt(st.s) || 1, z = 0, b;
      var piv = 31 - Math.clz32(sv & -sv);          // lowest set bit of s
      for (b = 0; b < n; b++) {
        if (b === piv) continue;
        if (Math.random() < 0.5) {
          z ^= (1 << b) | (((sv >> b) & 1) ? (1 << piv) : 0);
        }
      }
      return z;
    }

    function solve() {
      var cands = [], v, i;
      for (v = 1; v < N; v++) {
        var ok = true;
        for (i = 0; i < st.rows.length; i++) {
          if (popcount(v & st.rows[i]) & 1) { ok = false; break; }
        }
        if (ok) cands.push(v);
      }
      return cands;
    }

    function draw() {
      clear(rowsG);
      var sv = bitsToInt(st.s) || 1, i;
      head.textContent = "hidden s = " + intToStr(sv, n) +
        "   ·   equations collected: " + st.rows.length +
        "   ·   independent: " + rank(st.rows) + " of " + (n - 1) + " needed";
      for (i = 0; i < Math.min(st.rows.length, 8); i++) {
        var y = 58 + i * 18;
        var t = s("text", { x: 30, y: y, class: "qq-t qq-ink" }, rowsG);
        t.setAttribute("font-size", "12.5");
        t.setAttribute("font-family", "ui-monospace, monospace");
        t.textContent = "z = " + intToStr(st.rows[i], n) + "   ·   z · s = 0";
        var v = s("text", { x: 230, y: y, class: "qq-t" }, rowsG);
        v.setAttribute("font-size", "12.5");
        v.setAttribute("fill", st.flags[i] ? "var(--qq-pos)" : "var(--qq-neg)");
        v.textContent = st.flags[i] ? "new information"
                                    : "already implied — wasted shot";
      }
      if (st.rows.length > 8) {
        var more = s("text", { x: 30, y: 58 + 8 * 18,
          class: "qq-t qq-muted qq-sm" }, rowsG);
        more.textContent = "… " + (st.rows.length - 8) + " more";
      }
      var cands = solve();
      if (rank(st.rows) === n - 1 && cands.length === 1) {
        verdict.textContent = "solved: the only nonzero string orthogonal to " +
          "every sample is " + intToStr(cands[0], n) +
          (cands[0] === sv ? "  ✓  that is s" : "");
      } else if (st.rows.length === 0) {
        verdict.textContent = "no samples yet — s could be any of the 15 " +
          "nonzero strings";
      } else {
        verdict.textContent = "still " + cands.length + " candidates for s: " +
          cands.slice(0, 8).map(function (v) { return intToStr(v, n); })
            .join(" ") + (cands.length > 8 ? " …" : "");
      }
    }

    function shoot(k) {
      for (var i = 0; i < k; i++) {
        var before = rank(st.rows), z = sample();
        st.rows.push(z);
        st.flags.push(rank(st.rows) > before);
      }
      draw();
    }

    var ctr = h("div", "qq-ctrl", f.body);
    btn(ctr, "measure", function () { shoot(1); });
    btn(ctr, "measure ×3", function () { shoot(3); }, "qq-btn-ghost");
    btn(ctr, "reset", function () {
      st.rows = []; st.flags = []; draw();
    }, "qq-btn-ghost");
    var ctr2 = h("div", "qq-ctrl", f.body);
    var chips = bitToggles(ctr2, "hidden s =", st.s, function () {
      if (bitsToInt(st.s) === 0) { st.s[n - 1] = 1; chips.sync(); }
      st.rows = []; st.flags = []; draw();
    });
    draw();
  }

  /* =================================================================
   * PREREQUISITE · Fourier from scratch
   *
   *   tuner      the radio dial: multiply, average, sweep
   *   harmonics  build a square wave one harmonic at a time (and Gibbs)
   *   twovalues  the bridge: a group of order 2 leaves a wave only +-1
   * ================================================================= */

  /* ---- V · the radio dial ------------------------------------------ */

  function animTuner(root) {
    var f = frame(root, "Tuning a dial: the only measurement in Fourier analysis",
      "Multiply the signal by a probe wave point by point, then average. " +
      "When the probe matches something in the signal the products stay " +
      "positive and the average is large; when it does not, the products " +
      "spend as much time below zero as above and cancel. Sweep the dial " +
      "across every frequency and the collected answers are the spectrum. " +
      "That is the whole idea — everything else is bookkeeping about which " +
      "waves you sweep.");

    var st = { k: 3, hidden: [[3, 1.0], [7, 0.55]] };
    var W = 660, Hh = 300, pad = 34;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var M = 240;                       // points used to draw the curves
    var topMid = 74, prodMid = 168, specBase = 268, specTop = 208;

    function sig(t) {
      var v = 0;
      for (var i = 0; i < st.hidden.length; i++) {
        v += st.hidden[i][1] * Math.cos(2 * Math.PI * st.hidden[i][0] * t);
      }
      return v;
    }
    function probe(t) { return Math.cos(2 * Math.PI * st.k * t); }

    function pathOf(fn, mid, amp) {
      var d = "", i, t, x, y;
      for (i = 0; i <= M; i++) {
        t = i / M;
        x = pad + t * (W - 2 * pad);
        y = mid - amp * fn(t);
        d += (i ? "L" : "M") + x.toFixed(1) + "," + y.toFixed(1);
      }
      return d;
    }

    var lblSig = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, svg);
    var lblProd = s("text", { x: pad, y: 118, class: "qq-t qq-muted qq-sm" },
      svg);
    var fillG = s("g", {}, svg);
    var sigP = s("path", { fill: "none", "stroke-width": 2,
      style: "stroke: var(--qq-ink)" }, svg);
    var probeP = s("path", { fill: "none", "stroke-width": 1.6,
      "stroke-dasharray": "5 3", style: "stroke: var(--qq-hot)" }, svg);
    var prodP = s("path", { fill: "none", "stroke-width": 1.6,
      style: "stroke: var(--qq-pos)" }, svg);
    s("line", { x1: pad, y1: topMid, x2: W - pad, y2: topMid,
      class: "qq-axis" }, svg);
    s("line", { x1: pad, y1: prodMid, x2: W - pad, y2: prodMid,
      class: "qq-axis" }, svg);
    s("line", { x1: pad, y1: specBase, x2: W - pad, y2: specBase,
      class: "qq-axis" }, svg);
    var barsG = s("g", {}, svg);
    var readout = s("text", { x: W - pad, y: 118, class: "qq-t-end qq-hot" },
      svg);

    function draw() {
      var i, t, KMAX = 14;
      sigP.setAttribute("d", pathOf(sig, topMid, 26));
      probeP.setAttribute("d", pathOf(probe, topMid, 26));
      prodP.setAttribute("d", pathOf(function (t) {
        return sig(t) * probe(t);
      }, prodMid, 20));

      // shade the product: blue above the line, amber below
      clear(fillG);
      var segs = 120, acc = 0;
      for (i = 0; i < segs; i++) {
        t = (i + 0.5) / segs;
        var v = sig(t) * probe(t);
        acc += v / segs;
        var x = pad + (i / segs) * (W - 2 * pad);
        var w = (W - 2 * pad) / segs;
        var hgt = v * 20;
        s("rect", { x: x, y: hgt >= 0 ? prodMid - hgt : prodMid,
          width: w + 0.4, height: Math.abs(hgt),
          class: hgt >= 0 ? "qq-pos" : "qq-neg", opacity: 0.42 }, fillG);
      }

      clear(barsG);
      var bw = (W - 2 * pad) / (KMAX + 1);
      for (i = 0; i <= KMAX; i++) {
        var a = 0;
        for (var j = 0; j < st.hidden.length; j++) {
          if (st.hidden[j][0] === i) a = st.hidden[j][1];
        }
        var hh = (a / 2) * (specBase - specTop) / 0.6;   // a/2 = the average
        s("rect", { x: pad + i * bw + bw * 0.18, y: specBase - hh,
          width: bw * 0.64, height: Math.max(hh, 0.8),
          class: i === st.k ? "qq-hotbar" : "qq-bar qq-pos",
          opacity: i === st.k ? 1 : 0.45 }, barsG);
        var tx = s("text", { x: pad + i * bw + bw / 2, y: specBase + 15,
          class: "qq-t-mid qq-muted qq-sm" }, barsG);
        tx.textContent = String(i);
      }

      lblSig.textContent = "the signal (solid) and your probe wave at k = " +
        st.k + " (dashed)";
      lblProd.textContent = "their product, point by point";
      readout.textContent = "average = " + acc.toFixed(3) +
        (Math.abs(acc) < 0.02 ? "   →   nothing at this frequency"
                              : "   →   found it");
      var t2 = s("text", { x: pad, y: specTop - 8,
        class: "qq-t qq-muted qq-sm" }, barsG);
      t2.textContent = "the spectrum: one bar per dial position, each the " +
        "average you would read there";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr, "probe frequency k", 0, 14, st.k,
      function (v) { st.k = v; draw(); });
    h("span", "qq-bits-l", ctr, "hidden signal");
    [["two tones", [[3, 1.0], [7, 0.55]]],
     ["one tone", [[5, 1.0]]],
     ["three tones", [[2, 0.8], [6, 0.6], [11, 0.4]]]].forEach(function (p) {
      btn(ctr, p[0], function () { st.hidden = p[1]; draw(); }, "qq-btn-ghost");
    });
    draw();
  }

  /* ---- W · building a square wave out of harmonics ------------------ */

  function animHarmonics(root) {
    var f = frame(root, "Building a shape out of waves, one harmonic at a time",
      "A square wave is the sum of odd harmonics with amplitudes 4/πk. Add " +
      "them one at a time and the sum crawls toward the shape — but look at " +
      "the corners. The overshoot settles at about 9% of the jump and never " +
      "goes away; more terms only make it narrower. A finite recipe cannot " +
      "make a sharp edge, and that same fact is why a period that does not " +
      "divide the register leaks in Shor's algorithm.");

    var st = { terms: 3 };
    var W = 660, Hh = 250, pad = 36, mid = 128, amp = 74;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var head = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, svg);
    var note = s("text", { x: pad, y: 44, class: "qq-t qq-muted qq-sm" }, svg);
    s("line", { x1: pad, y1: mid, x2: W - pad, y2: mid, class: "qq-axis" },
      svg);
    var target = s("path", { fill: "none", "stroke-width": 1.4,
      "stroke-dasharray": "4 4", style: "stroke: var(--qq-muted)" }, svg);
    var sum = s("path", { fill: "none", "stroke-width": 2.2,
      style: "stroke: var(--qq-pos)" }, svg);
    var partsG = s("g", {}, svg);
    var over = s("line", { class: "qq-mark" }, svg);

    function series(t, terms) {
      var v = 0;
      for (var j = 0; j < terms; j++) {
        var k = 2 * j + 1;
        v += (4 / (Math.PI * k)) * Math.sin(2 * Math.PI * k * t);
      }
      return v;
    }

    function pathOf(fn) {
      var d = "", i, M = 900;
      for (i = 0; i <= M; i++) {
        var t = i / M;
        var x = pad + t * (W - 2 * pad);
        var y = mid - amp * fn(t);
        d += (i ? "L" : "M") + x.toFixed(1) + "," + y.toFixed(1);
      }
      return d;
    }

    function draw() {
      target.setAttribute("d", pathOf(function (t) {
        return t < 0.5 ? 1 : -1;
      }));
      sum.setAttribute("d", pathOf(function (t) {
        return series(t, st.terms);
      }));
      clear(partsG);
      for (var j = 0; j < Math.min(st.terms, 6); j++) {
        var k = 2 * j + 1;
        s("path", { d: pathOf(function (t) {
          return (4 / (Math.PI * k)) * Math.sin(2 * Math.PI * k * t);
        }), fill: "none", "stroke-width": 1,
          style: "stroke: var(--qq-neg)", opacity: 0.4 }, partsG);
      }
      // measured peak of the partial sum, scanned near the jump
      var kmax = 2 * st.terms - 1, peak = 0;
      for (var i = 0; i <= 600; i++) {
        var t = (i / 600) * (3 / (2 * kmax));
        peak = Math.max(peak, series(t, st.terms));
      }
      over.setAttribute("x1", pad);
      over.setAttribute("x2", W - pad);
      over.setAttribute("y1", mid - amp * peak);
      over.setAttribute("y2", mid - amp * peak);
      head.textContent = st.terms + " harmonic" + (st.terms > 1 ? "s" : "") +
        "  (k = 1, 3, 5, … " + kmax + ")";
      note.textContent = "peak of the sum " + peak.toFixed(4) +
        "   ·   overshoot " + (100 * (peak - 1) / 2).toFixed(2) +
        "% of the jump   ·   the limit is 8.95%, forever";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr, "harmonics", 1, 60, st.terms,
      function (v) { st.terms = v; draw(); });
    draw();
  }

  /* ---- X · the bridge: a group of order two ------------------------ */

  function animTwoValues(root) {
    var f = frame(root, "The bridge: what a wave becomes when there are only " +
      "two positions",
      "A wave in Fourier analysis is a point running around the unit circle. " +
      "How far it steps each time depends on the group. On the integers mod " +
      "N it can stop anywhere on the circle. On bit strings under XOR, " +
      "doing anything twice returns you to the start — so the only stopping " +
      "points are +1 and −1, and a wave collapses into a pattern of signs. " +
      "Those sign patterns are exactly the rows of the Hadamard layer.");

    var st = { N: 8, k: 1 };
    var W = 660, Hh = 268;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var head = s("text", { x: 24, y: 24, class: "qq-t qq-ink" }, svg);
    var g = s("g", {}, svg);
    var note = s("text", { x: 24, y: Hh - 14, class: "qq-t qq-muted qq-sm" },
      svg);

    function draw() {
      clear(g);
      var N = st.N, k = st.k, i, cx = 128, cy = 136, R = 74;
      s("circle", { cx: cx, cy: cy, r: R, fill: "none",
        style: "stroke: var(--qq-line)", "stroke-width": 1.2 }, g);
      var prev = null;
      for (i = 0; i < N; i++) {
        var ang = 2 * Math.PI * k * i / N;
        var px = cx + R * Math.cos(ang), py = cy - R * Math.sin(ang);
        if (prev) {
          s("line", { x1: prev[0], y1: prev[1], x2: px, y2: py,
            style: "stroke: var(--qq-neg)", "stroke-width": 1.3,
            opacity: 0.75 }, g);
        }
        s("circle", { cx: px, cy: py, r: 5, class: "qq-pos" }, g);
        prev = [px, py];
      }
      var t1 = s("text", { x: cx, y: cy + R + 26, class: "qq-t-mid qq-muted qq-sm" },
        g);
      t1.textContent = N === 2 ? "only two stopping points: +1 and −1"
                               : N + " stopping points on the circle";

      // the sampled wave, drawn as bars
      var x0 = 268, bw = (W - x0 - 30) / 16, base = 136, h0 = 52;
      for (i = 0; i < 16; i++) {
        var a = 2 * Math.PI * k * i / N;
        var re = Math.cos(a);
        s("rect", { x: x0 + i * bw + 2, y: re >= 0 ? base - re * h0 : base,
          width: bw - 4, height: Math.max(Math.abs(re) * h0, 1),
          class: re >= 0 ? "qq-pos" : "qq-neg" }, g);
      }
      s("line", { x1: x0, y1: base, x2: W - 26, y2: base, class: "qq-axis" },
        g);
      var t2 = s("text", { x: x0, y: base - h0 - 16, class: "qq-t qq-muted qq-sm" },
        g);
      t2.textContent = "the wave, sampled: cos(2π·" + k + "·x / " + N + ")";
      var t3 = s("text", { x: x0, y: base + 76, class: "qq-t qq-ink" }, g);
      t3.setAttribute("font-size", "12.5");
      var vals = "";
      for (i = 0; i < 8; i++) {
        var v = Math.cos(2 * Math.PI * k * i / N);
        vals += (Math.abs(v - 1) < 1e-9 ? " +1"
          : Math.abs(v + 1) < 1e-9 ? " −1" : " " + v.toFixed(2));
      }
      t3.textContent = "values:" + vals + " …";

      head.textContent = "group ℤ" + N + ",  frequency k = " + k;
      note.textContent = N === 2
        ? "every value is ±1 — this row is exactly a row of H, and stacking "
          + "all of them for n bits gives H⊗ⁿ"
        : "values are spread around the circle; only when N = 2 does the "
          + "wave become a pure sign pattern";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", ctr, "group size N =");
    [2, 4, 8, 16].forEach(function (N) {
      btn(ctr, String(N), function () {
        st.N = N; st.k = Math.min(st.k, N - 1); draw();
      }, "qq-btn-ghost");
    });
    rangeCtl(ctr, "k", 0, 7, st.k, function (v) {
      st.k = Math.min(v, st.N - 1); draw();
    });
    draw();
  }

  /* =================================================================
   * AUTOPSY 05 · the hidden subgroup problem, and where structure ends
   *
   *   hspmachine  one quantum step, three algorithms: swap only the tail
   *   dihedral    D_N: the label says one bit, the phase says the rest
   *   colourwl    what colour refinement already does to graph isomorphism
   * ================================================================= */

  /* ---- Y · one machine, three algorithms --------------------------- */

  function animHspMachine(root) {
    var f = frame(root, "One quantum step, three algorithms",
      "The machine never changes: build the superposition, call the " +
      "function once, measure the output register so the input collapses " +
      "to a coset, Fourier transform, measure. Every sample lands on the " +
      "annihilator H⊥ and nowhere else. What changes between " +
      "Bernstein–Vazirani, Simon and Shor is only the classical line at " +
      "the end that reads the labels — which is why one theorem closed " +
      "three problems at once.");

    var n = 4, N = 16;
    var st = { mode: "simon", labels: [] };
    var W = 660, Hh = 232, pad = 30, base = 150, top = 44;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var barsG = s("g", {}, svg);
    var head = s("text", { x: pad, y: 22, class: "qq-t qq-ink" }, svg);
    var sub = s("text", { x: pad, y: 40, class: "qq-t qq-muted qq-sm" }, svg);
    var tail = s("text", { x: pad, y: base + 42, class: "qq-t qq-hot" }, svg);
    s("line", { x1: pad, y1: base, x2: W - pad, y2: base, class: "qq-axis" },
      svg);

    var MODES = {
      bv: { name: "Bernstein–Vazirani", s: 0xB,
        group: "G = ℤ₂⁴,  H = the hyperplane s·x = 0",
        tail: "classical tail: read the one nonzero label — it IS s" },
      simon: { name: "Simon", s: 0xD,
        group: "G = ℤ₂⁴,  H = {0, s}",
        tail: "classical tail: collect n−1 independent labels, solve over GF(2)" },
      shor: { name: "Shor, order-finding", r: 4,
        group: "G = ℤ₁₆,  H = rℤ",
        tail: "classical tail: gcd of the labels gives N/r, hence r" }
    };

    function support() {
      // H-perp, computed the same way the Python does it
      var out = [], z;
      if (st.mode === "bv") {
        out = [0, MODES.bv.s];                    // {0, s}
      } else if (st.mode === "simon") {
        for (z = 0; z < N; z++) {
          if (popcount(z & MODES.simon.s) % 2 === 0) out.push(z);
        }
      } else {
        for (z = 0; z < N; z++) {
          if (z % (N / MODES.shor.r) === 0) out.push(z);
        }
      }
      return out;
    }

    function draw() {
      var sup = support(), i, bw = (W - 2 * pad) / N;
      var p = 1 / sup.length, mx = p;
      clear(barsG);
      for (i = 0; i < N; i++) {
        var inSup = sup.indexOf(i) >= 0;
        var hgt = inSup ? (base - top) * p / mx : 0;
        s("rect", { x: pad + i * bw + 3, y: base - Math.max(hgt, 1),
          width: bw - 6, height: Math.max(hgt, 1),
          class: "qq-bar " + (inSup ? "qq-pos" : "qq-neg"),
          opacity: st.labels.indexOf(i) >= 0 ? 1 : 0.55 }, barsG);
        var t = s("text", { x: pad + i * bw + bw / 2, y: base + 16,
          class: "qq-t-mid qq-muted qq-sm" }, barsG);
        t.setAttribute("font-size", "8.5");
        t.textContent = st.mode === "shor" ? String(i) : intToStr(i, n);
      }
      st.labels.forEach(function (z) {
        s("circle", { cx: pad + z * bw + bw / 2, cy: top - 12, r: 4,
          style: "fill: var(--qq-hot)" }, barsG);
      });
      var m = MODES[st.mode];
      head.textContent = m.name + "   ·   " + m.group;
      sub.textContent = "the samples land on H⊥ — " + sup.length +
        " of " + N + " labels are even possible" +
        (st.labels.length ? ("   ·   drawn so far: " + st.labels.length) : "");
      tail.textContent = m.tail;
    }

    function shoot(k) {
      var sup = support();
      for (var i = 0; i < k; i++) {
        st.labels.push(sup[Math.floor(Math.random() * sup.length)]);
      }
      draw();
    }

    var ctr = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", ctr, "problem");
    [["bv", "Bernstein–Vazirani"], ["simon", "Simon"],
     ["shor", "Shor order-finding"]].forEach(function (p) {
      btn(ctr, p[1], function () {
        st.mode = p[0]; st.labels = []; draw();
      }, "qq-btn-ghost");
    });
    var ctr2 = h("div", "qq-ctrl", f.body);
    btn(ctr2, "measure", function () { shoot(1); });
    btn(ctr2, "measure ×3", function () { shoot(3); }, "qq-btn-ghost");
    btn(ctr2, "clear", function () { st.labels = []; draw(); }, "qq-btn-ghost");
    draw();
  }

  /* ---- Z · the dihedral group: one bit, then a phase --------------- */

  function animDihedral(root) {
    var f = frame(root, "Barely non-abelian, and it costs everything",
      "The dihedral group is a circle of rotations plus a flip — one step " +
      "away from abelian. Hide a reflection in it and Fourier sampling " +
      "still returns a label, but the two-dimensional labels come out with " +
      "exactly the same probabilities whatever the secret is. Only the " +
      "one-dimensional labels move, and they reveal a single bit: whether " +
      "the offset is even or odd. Everything else survives as a relative " +
      "phase inside a two-dimensional block, which one measurement cannot " +
      "read. That gap is where lattice cryptography lives.");

    var st = { N: 8, d: 3 };
    var W = 660, Hh = 264;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);
    var head = s("text", { x: 24, y: 24, class: "qq-t qq-ink" }, svg);
    var note = s("text", { x: 24, y: Hh - 12, class: "qq-t qq-muted qq-sm" },
      svg);

    function draw() {
      clear(g);
      var N = st.N, d = st.d, i;

      // left: the group as a circle of rotations plus the hidden reflection
      var cx = 118, cy = 132, R = 74;
      s("circle", { cx: cx, cy: cy, r: R, fill: "none",
        style: "stroke: var(--qq-line)", "stroke-width": 1.2 }, g);
      for (i = 0; i < N; i++) {
        var a = 2 * Math.PI * i / N;
        s("circle", { cx: cx + R * Math.cos(a), cy: cy - R * Math.sin(a),
          r: 4, class: "qq-pos" }, g);
      }
      var ad = 2 * Math.PI * d / N;
      s("line", { x1: cx - R * Math.cos(ad / 2), y1: cy + R * Math.sin(ad / 2),
        x2: cx + R * Math.cos(ad / 2), y2: cy - R * Math.sin(ad / 2),
        style: "stroke: var(--qq-hot)", "stroke-width": 2,
        "stroke-dasharray": "5 3" }, g);
      var lab = s("text", { x: cx, y: cy + R + 26,
        class: "qq-t-mid qq-muted qq-sm" }, g);
      lab.textContent = "hidden reflection at offset d = " + d;

      // right: the label distribution
      var x0 = 250, bw = 46, base = 176, hmax = 92;
      var names = ["trivial", "sign", "alt", "alt-sign", "ρ₁", "ρ₂", "ρ₃"];
      var even = d % 2 === 0;
      var vals = [0.125, 0, even ? 0.125 : 0, even ? 0 : 0.125,
                  0.25, 0.25, 0.25];
      for (i = 0; i < names.length; i++) {
        var hgt = vals[i] * hmax / 0.25 * 0.92;
        s("rect", { x: x0 + i * bw + 5, y: base - hgt, width: bw - 12,
          height: Math.max(hgt, 1.2),
          class: "qq-bar " + (i < 4 ? "qq-hotbar" : "qq-pos") }, g);
        var t = s("text", { x: x0 + i * bw + bw / 2 - 3, y: base + 16,
          class: "qq-t-mid qq-muted qq-sm" }, g);
        t.setAttribute("font-size", "9");
        t.textContent = names[i];
      }
      s("line", { x1: x0, y1: base, x2: x0 + names.length * bw, y2: base,
        class: "qq-axis" }, g);
      var t2 = s("text", { x: x0, y: 62, class: "qq-t qq-muted qq-sm" }, g);
      t2.textContent = "1-dimensional labels (amber): move with the parity";
      var t3 = s("text", { x: x0, y: 78, class: "qq-t qq-muted qq-sm" }, g);
      t3.textContent = "2-dimensional labels (blue): identical for every d";

      // the phase that holds the rest
      var px = x0, py = 216;
      var t4 = s("text", { x: px, y: py, class: "qq-t qq-ink" }, g);
      t4.setAttribute("font-size", "12.5");
      t4.textContent = "inside block ρ₁ the state is (|0⟩ + e^(2πi·" + d +
        "/" + N + ")|1⟩)/√2";

      head.textContent = "D" + N + ": " + (2 * N) + " elements, " +
        "hidden subgroup {1, s·r^" + d + "}";
      note.textContent = "the label told you d is " + (even ? "even" : "odd") +
        " — one bit out of log₂ " + N + " = " + Math.log2(N) +
        ". The remaining " + (Math.log2(N) - 1) + " bits are in that phase, " +
        "and one copy is not enough to read it.";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", ctr, "N =");
    [8, 16].forEach(function (N) {
      btn(ctr, String(N), function () {
        st.N = N; st.d = st.d % N; draw();
      }, "qq-btn-ghost");
    });
    rangeCtl(ctr, "hidden offset d", 0, 15, st.d, function (v) {
      st.d = v % st.N; draw();
    });
    draw();
  }

  /* ---- AA · colour refinement, the baseline GI was measured against - */

  function animColourWl(root) {
    var f = frame(root, "What the classical baseline was already doing",
      "Colour refinement: colour every vertex by its degree, then keep " +
      "recolouring by the multiset of neighbouring colours until nothing " +
      "changes. Two graphs whose colour multisets differ cannot be " +
      "isomorphic. On a random graph it separates every vertex within a " +
      "few rounds, which settles the isomorphism question outright — this " +
      "is the algorithm from 1968 that the thirty-year quantum programme " +
      "was implicitly racing.");

    var st = { kind: "random", round: 0, adj: null, n: 12 };
    var W = 660, Hh = 288;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);
    var head = s("text", { x: 24, y: 24, class: "qq-t qq-ink" }, svg);
    var note = s("text", { x: 24, y: Hh - 12, class: "qq-t qq-muted qq-sm" },
      svg);
    var PALETTE = ["#2a78d6", "#eda100", "#1baf7a", "#e34948", "#8a63d2",
                   "#00a3a3", "#c2185b", "#7cb342", "#5c6bc0", "#f4511e",
                   "#795548", "#00838f"];

    function makeRandom(n) {
      var a = [], i, j;
      for (i = 0; i < n; i++) { a.push([]); for (j = 0; j < n; j++) a[i].push(0); }
      for (i = 0; i < n; i++) {
        for (j = i + 1; j < n; j++) {
          var e = Math.random() < 0.35 ? 1 : 0;
          a[i][j] = a[j][i] = e;
        }
      }
      return a;
    }

    function makeRook() {           // 4x4 rook's graph: strongly regular
      var n = 16, a = [], i, j;
      for (i = 0; i < n; i++) { a.push([]); for (j = 0; j < n; j++) a[i].push(0); }
      for (i = 0; i < 16; i++) {
        for (j = 0; j < 16; j++) {
          if (i === j) continue;
          if ((i >> 2) === (j >> 2) || (i & 3) === (j & 3)) a[i][j] = 1;
        }
      }
      return a;
    }

    function refine(adj, rounds) {
      var n = adj.length, colors = [], i, r;
      for (i = 0; i < n; i++) colors.push(0);
      for (r = 0; r < rounds; r++) {
        var sigs = [];
        for (i = 0; i < n; i++) {
          var nb = [];
          for (var j = 0; j < n; j++) if (adj[i][j]) nb.push(colors[j]);
          nb.sort(function (a, b) { return a - b; });
          sigs.push(colors[i] + "|" + nb.join(","));
        }
        var uniq = sigs.slice().sort().filter(function (v, k, arr) {
          return k === 0 || v !== arr[k - 1];
        });
        var next = sigs.map(function (sig) { return uniq.indexOf(sig); });
        var before = colors.slice().sort().filter(function (v, k, arr) {
          return k === 0 || v !== arr[k - 1];
        }).length;
        colors = next;
        if (uniq.length === before) break;
      }
      return colors;
    }

    function reset() {
      st.round = 0;
      st.adj = st.kind === "random" ? makeRandom(st.n) : makeRook();
      draw();
    }

    function draw() {
      clear(g);
      var adj = st.adj, n = adj.length, i, j;
      var colors = refine(adj, st.round);
      var cx = 190, cy = 148, R = 108;
      var pos = [];
      for (i = 0; i < n; i++) {
        var a = 2 * Math.PI * i / n - Math.PI / 2;
        pos.push([cx + R * Math.cos(a), cy + R * Math.sin(a)]);
      }
      for (i = 0; i < n; i++) {
        for (j = i + 1; j < n; j++) {
          if (adj[i][j]) {
            s("line", { x1: pos[i][0], y1: pos[i][1],
              x2: pos[j][0], y2: pos[j][1],
              style: "stroke: var(--qq-line)", "stroke-width": 1,
              opacity: 0.55 }, g);
          }
        }
      }
      for (i = 0; i < n; i++) {
        s("circle", { cx: pos[i][0], cy: pos[i][1], r: 9,
          style: "fill: " + PALETTE[colors[i] % PALETTE.length] }, g);
      }
      var distinct = colors.slice().sort(function (a, b) { return a - b; })
        .filter(function (v, k, arr) { return k === 0 || v !== arr[k - 1]; })
        .length;

      // the colour histogram
      var x0 = 360, bw = 22, base = 214;
      var counts = {};
      colors.forEach(function (c) { counts[c] = (counts[c] || 0) + 1; });
      var keys = Object.keys(counts).sort(function (a, b) { return a - b; });
      for (i = 0; i < keys.length && i < 13; i++) {
        var hgt = counts[keys[i]] * 15;
        s("rect", { x: x0 + i * bw, y: base - hgt, width: bw - 5,
          height: hgt, style: "fill: " +
            PALETTE[keys[i] % PALETTE.length] }, g);
      }
      s("line", { x1: x0, y1: base, x2: W - 24, y2: base, class: "qq-axis" },
        g);
      var t = s("text", { x: x0, y: base + 20, class: "qq-t qq-muted qq-sm" },
        g);
      t.textContent = "colour classes: " + distinct + " of " + n + " vertices";

      head.textContent = "round " + st.round + "   ·   " +
        (st.kind === "random" ? "a random graph on " + n + " vertices"
                              : "the 4×4 rook's graph (strongly regular)");
      note.textContent = st.kind === "random"
        ? (distinct === n
            ? "every vertex has its own colour — the graph is canonically "
              + "labelled and isomorphism against it is now trivial"
            : "keep stepping: on a random graph this reaches all-distinct "
              + "in a handful of rounds")
        : "every vertex keeps the same colour forever. This is the thin "
          + "adversarial family where refinement is blind — and where one "
          + "more invariant (the shape of a neighbourhood) walks straight "
          + "past it.";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    btn(ctr, "step", function () { st.round++; draw(); });
    btn(ctr, "reset", reset, "qq-btn-ghost");
    h("span", "qq-bits-l", ctr, "graph");
    [["random", "random"], ["rook", "strongly regular"]].forEach(function (p) {
      btn(ctr, p[1], function () { st.kind = p[0]; reset(); }, "qq-btn-ghost");
    });
    reset();
  }

  /* =================================================================
   * AUTOPSY 06 · Grover, amplitude amplification, the BBBV ceiling
   *
   *   groverspin  the rotation, and the souffle: more can be worse
   *   attention   the hybrid argument: T units spread over N items
   *   groverwall  depth, parallelism, and where the quadratic pays
   * ================================================================= */

  /* ---- AB · the rotation, and knowing when to stop ------------------ */

  function animGroverSpin(root) {
    var f = frame(root, "A rotation you have to stop on time",
      "The state never leaves the plane spanned by “the marked item” and " +
      "“everything else”, and each iteration turns it by the same small " +
      "angle. That is the entire algorithm. Notice what it means: Grover " +
      "is not a search that improves until you stop it — run it too long " +
      "and the state sails past the target and back out again. Every " +
      "application therefore has to know the size of the haystack before " +
      "it starts.");

    var st = { n: 10, t: 0 };
    var W = 660, Hh = 300;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);
    var head = s("text", { x: 24, y: 24, class: "qq-t qq-ink" }, svg);
    var note = s("text", { x: 24, y: Hh - 12, class: "qq-t qq-muted qq-sm" },
      svg);

    function theta() { return Math.asin(Math.pow(2, -st.n / 2)); }
    function prob(t) { return Math.pow(Math.sin((2 * t + 1) * theta()), 2); }
    function topt() { return Math.round(Math.PI / (4 * theta()) - 0.5); }

    function draw() {
      clear(g);
      var cx = 150, cy = 168, R = 104, i;

      // the plane: |rest> horizontal, |marked> vertical
      s("line", { x1: cx - R - 16, y1: cy, x2: cx + R + 16, y2: cy,
        class: "qq-axis" }, g);
      s("line", { x1: cx, y1: cy + R + 16, x2: cx, y2: cy - R - 16,
        class: "qq-axis" }, g);
      s("path", { d: "M " + (cx + R) + " " + cy + " A " + R + " " + R +
        " 0 0 0 " + cx + " " + (cy - R), fill: "none",
        style: "stroke: var(--qq-line)", "stroke-width": 1.1 }, g);
      var lx = s("text", { x: cx + R + 22, y: cy + 4,
        class: "qq-t qq-muted qq-sm" }, g);
      lx.textContent = "everything else";
      var ly = s("text", { x: cx + 6, y: cy - R - 22,
        class: "qq-t qq-muted qq-sm" }, g);
      ly.textContent = "the marked item";

      // every step so far, faded; the current one solid
      for (i = 0; i <= st.t; i++) {
        var a = (2 * i + 1) * theta();
        var px = cx + R * Math.cos(a), py = cy - R * Math.sin(a);
        s("line", { x1: cx, y1: cy, x2: px, y2: py,
          style: "stroke: var(--qq-" + (i === st.t ? "hot" : "pos") + ")",
          "stroke-width": i === st.t ? 2.6 : 1.1,
          opacity: i === st.t ? 1 : 0.28 }, g);
        if (i === st.t) {
          s("circle", { cx: px, cy: py, r: 5,
            style: "fill: var(--qq-hot)" }, g);
        }
      }

      // the probability curve
      var x0 = 316, base = 250, top = 62, wid = W - x0 - 30;
      var tmax = Math.max(4 * topt(), 8);
      s("line", { x1: x0, y1: base, x2: x0 + wid, y2: base,
        class: "qq-axis" }, g);
      var d = "", k;
      for (k = 0; k <= tmax; k++) {
        var xx = x0 + (k / tmax) * wid;
        var yy = base - prob(k) * (base - top);
        d += (k ? "L" : "M") + xx.toFixed(1) + "," + yy.toFixed(1);
      }
      s("path", { d: d, fill: "none", style: "stroke: var(--qq-pos)",
        "stroke-width": 2 }, g);
      var ox = x0 + (topt() / tmax) * wid;
      s("line", { x1: ox, y1: top - 6, x2: ox, y2: base, class: "qq-mark" }, g);
      var cxp = x0 + (st.t / tmax) * wid;
      s("circle", { cx: cxp, cy: base - prob(st.t) * (base - top), r: 5,
        style: "fill: var(--qq-hot)" }, g);
      var t1 = s("text", { x: x0, y: top - 14, class: "qq-t qq-muted qq-sm" },
        g);
      t1.textContent = "success probability vs iterations (dashed = stop here)";

      head.textContent = "N = " + (1 << st.n) + "   ·   iteration t = " +
        st.t + " of the optimal " + topt() + "   ·   P(success) = " +
        prob(st.t).toFixed(4);
      note.textContent = st.t === 0
        ? "before any iteration the state is uniform: P = 1/N."
        : st.t < topt()
          ? "still climbing — each iteration turns the state by the same angle."
          : st.t === topt()
            ? "this is the stopping point. One more query makes it worse."
            : "past the target: the rotation has overshot, and P is falling. " +
              "More queries, worse answer.";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    btn(ctr, "iterate", function () {
      st.t = Math.min(st.t + 1, 4 * topt()); draw();
    });
    btn(ctr, "jump to optimum", function () { st.t = topt(); draw(); },
      "qq-btn-ghost");
    btn(ctr, "reset", function () { st.t = 0; draw(); }, "qq-btn-ghost");
    var ctr2 = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr2, "log₂ N", 4, 14, st.n, function (v) {
      st.n = v; st.t = 0; draw();
    });
    draw();
  }

  /* ---- AC · the hybrid argument: T units of attention --------------- */

  function animAttention(root) {
    var f = frame(root, "Why no algorithm can do better",
      "Run any search algorithm on an oracle that marks nothing, and " +
      "record how much amplitude sits on each item at each query. The " +
      "total across all items is exactly T, the number of queries — " +
      "whatever the algorithm does in between. Spread T units over N " +
      "items and something must receive at most T/N. Marking *that* item " +
      "barely changes the run, so the algorithm cannot notice it unless T " +
      "is large. That is the whole of BBBV, and it was proved before " +
      "Grover's algorithm existed.");

    var st = { n: 8, T: 6, strategy: "grover" };
    var W = 660, Hh = 250, pad = 34, base = 168, top = 56;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var barsG = s("g", {}, svg);
    var head = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, svg);
    var sub = s("text", { x: pad, y: 42, class: "qq-t qq-muted qq-sm" }, svg);
    var verdict = s("text", { x: pad, y: base + 40, class: "qq-t qq-hot" },
      svg);

    function profile() {
      var N = 1 << st.n, out = [], i;
      if (st.strategy === "grover") {
        for (i = 0; i < N; i++) out.push(st.T / N);      // uniform
      } else if (st.strategy === "checker") {
        for (i = 0; i < N; i++) out.push(i < st.T ? 1 : 0);
      } else {                                           // a biased mixture
        var tot = 0;
        for (i = 0; i < N; i++) { out.push(Math.exp(-i / (N / 12))); tot += out[i]; }
        for (i = 0; i < N; i++) out[i] = out[i] * st.T / tot;
      }
      return out;
    }

    function draw() {
      var N = 1 << st.n, p = profile(), i, sum = 0, mn = Infinity, mx = 0;
      for (i = 0; i < N; i++) {
        sum += p[i];
        mn = Math.min(mn, p[i]);
        mx = Math.max(mx, p[i]);
      }
      clear(barsG);
      var bw = (W - 2 * pad) / N;
      for (i = 0; i < N; i++) {
        var hgt = mx > 1e-12 ? (base - top) * p[i] / mx : 0;
        s("rect", { x: pad + i * bw, y: base - hgt,
          width: Math.max(bw - 0.5, 0.8), height: Math.max(hgt, 0.7),
          class: "qq-bar " + (p[i] <= st.T / N + 1e-12 ? "qq-neg" : "qq-pos")
        }, barsG);
      }
      var ty = base - (base - top) * (st.T / N) / (mx > 1e-12 ? mx : 1);
      s("line", { x1: pad, y1: ty, x2: W - pad, y2: ty, class: "qq-mark" },
        barsG);
      var tl = s("text", { x: W - pad, y: ty - 6,
        class: "qq-t-end qq-muted qq-sm" }, barsG);
      tl.textContent = "T/N = " + (st.T / N).toFixed(4);

      head.textContent = "N = " + N + ",  T = " + st.T + " queries   ·   " +
        "total attention = " + sum.toFixed(3) + "  (= T, always)";
      sub.textContent = "amber bars receive at most T/N — marking any one of " +
        "them is what the algorithm cannot see";
      var dev = 2 * st.T / Math.sqrt(N);
      verdict.textContent = "least-attended item gets " + mn.toFixed(5) +
        "   →   marking it moves the output by at most 2T/√N = " +
        dev.toFixed(3) +
        (dev < 1 ? "  →  too small to notice: T is not enough"
                 : "  →  finally large enough, and T ≈ √N");
    }

    var ctr = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", ctr, "how the algorithm spends its queries");
    [["grover", "Grover (uniform)"], ["checker", "check T items"],
     ["biased", "biased"]].forEach(function (p) {
      btn(ctr, p[1], function () { st.strategy = p[0]; draw(); },
        "qq-btn-ghost");
    });
    var ctr2 = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr2, "log₂ N", 5, 10, st.n, function (v) { st.n = v; draw(); });
    rangeCtl(ctr2, "queries T", 1, 40, st.T, function (v) {
      st.T = v; draw();
    });
    draw();
  }

  /* ---- AD · what the quadratic is worth in wall-clock time --------- */

  function animGroverWall(root) {
    var f = frame(root, "A quadratic speedup, priced",
      "Grover's iterations are strictly sequential: iteration t+1 cannot " +
      "start until iteration t has finished, however many qubits you own. " +
      "So the cost is depth, and depth is the one resource money cannot " +
      "parallelise away — buying k quantum machines buys √k, while buying " +
      "k classical cores buys k. Slide the search space and watch which " +
      "side the arithmetic favours.");

    var st = { bits: 64, ops: 13, cores: 0 };   // ops, cores as powers of two
    var W = 660, Hh = 230;
    var LOGICAL = 25e-6, CLASSICAL = 0.3e-9, YEAR = 365.25 * 24 * 3600;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);

    function fmtYears(y) {
      if (y < 1 / 365) return (y * 365 * 24).toFixed(1) + " hours";
      if (y < 1) return (y * 365).toFixed(1) + " days";
      if (y < 1e6) return y.toFixed(0) + " years";
      return y.toExponential(1) + " years";
    }

    function draw() {
      clear(g);
      var iters = (Math.PI / 4) * Math.pow(2, st.bits / 2);
      var qs = iters * Math.pow(2, st.ops) * LOGICAL;
      var cs = Math.pow(2, st.bits - 1) * CLASSICAL / Math.pow(2, st.cores);
      var qy = qs / YEAR, cy = cs / YEAR;

      var rows = [
        ["search space", "2^" + st.bits + " = " +
          Math.pow(2, st.bits).toExponential(1)],
        ["Grover iterations (sequential)", iters.toExponential(2)],
        ["logical ops per iteration", "2^" + st.ops],
        ["quantum wall clock", fmtYears(qy)],
        ["classical cores", "2^" + st.cores],
        ["classical wall clock", fmtYears(cy)]
      ];
      for (var i = 0; i < rows.length; i++) {
        var y = 34 + i * 24;
        var a = s("text", { x: 30, y: y, class: "qq-t qq-muted qq-sm" }, g);
        a.textContent = rows[i][0];
        var b = s("text", { x: 330, y: y, class: "qq-t qq-ink" }, g);
        b.setAttribute("font-size", "13");
        b.setAttribute("font-family", "ui-monospace, monospace");
        b.textContent = rows[i][1];
        if (i === 3 || i === 5) {
          b.setAttribute("fill", (i === 3) === (qy < cy)
            ? "var(--qq-pos)" : "var(--qq-neg)");
        }
      }
      var v = s("text", { x: 30, y: 196, class: "qq-t qq-hot" }, g);
      v.setAttribute("font-size", "13.5");
      v.textContent = qy < cy
        ? "quantum wins by " + (cy / qy).toExponential(1) + "×"
        : "classical wins by " + (qy / cy).toExponential(1) + "×";
      var w = s("text", { x: 30, y: 216, class: "qq-t qq-muted qq-sm" }, g);
      w.textContent = (qy < 1e3 || cy < 1e3)
        ? "…and at least one side finishes in a human lifetime."
        : "…but both are far past the age of the universe, so nobody wins.";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr, "log₂ N", 20, 128, st.bits, function (v) {
      st.bits = v; draw();
    });
    var ctr2 = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr2, "log₂ ops/iteration", 0, 16, st.ops, function (v) {
      st.ops = v; draw();
    });
    rangeCtl(ctr2, "log₂ classical cores", 0, 30, st.cores, function (v) {
      st.cores = v; draw();
    });
    draw();
  }

  /* =================================================================
   * AUTOPSIES 07-08 · quantum walks
   *
   *   walkrace   a ballistic front against a diffusive blob
   *   disorder   what one imperfect graph does to the exponential
   *   szegedygap phase gap = Theta(sqrt(spectral gap)), on real chains
   * ================================================================= */

  /* --- small dense-matrix helpers, enough for a tridiagonal chain --- */

  function jacobiEigh(Ain, sweeps) {
    /* Symmetric eigendecomposition by cyclic Jacobi rotations. Slow in
       general, fine for the ~60x60 chains these widgets use, and it keeps
       the file dependency-free (house rule: nothing loads from a CDN). */
    var n = Ain.length, i, j, k, p, q;
    var A = [], V = [];
    for (i = 0; i < n; i++) {
      A.push(Ain[i].slice());
      V.push([]);
      for (j = 0; j < n; j++) V[i].push(i === j ? 1 : 0);
    }
    sweeps = sweeps || 12;
    for (k = 0; k < sweeps; k++) {
      var off = 0;
      for (p = 0; p < n - 1; p++) {
        for (q = p + 1; q < n; q++) off += A[p][q] * A[p][q];
      }
      if (off < 1e-18) break;
      for (p = 0; p < n - 1; p++) {
        for (q = p + 1; q < n; q++) {
          if (Math.abs(A[p][q]) < 1e-14) continue;
          var theta = (A[q][q] - A[p][p]) / (2 * A[p][q]);
          var t = (theta >= 0 ? 1 : -1) /
            (Math.abs(theta) + Math.sqrt(theta * theta + 1));
          var c = 1 / Math.sqrt(t * t + 1), s2 = t * c;
          for (i = 0; i < n; i++) {
            var aip = A[i][p], aiq = A[i][q];
            A[i][p] = c * aip - s2 * aiq;
            A[i][q] = s2 * aip + c * aiq;
          }
          for (i = 0; i < n; i++) {
            var api = A[p][i], aqi = A[q][i];
            A[p][i] = c * api - s2 * aqi;
            A[q][i] = s2 * api + c * aqi;
          }
          for (i = 0; i < n; i++) {
            var vip = V[i][p], viq = V[i][q];
            V[i][p] = c * vip - s2 * viq;
            V[i][q] = s2 * vip + c * viq;
          }
        }
      }
    }
    var lam = [];
    for (i = 0; i < n; i++) lam.push(A[i][i]);
    return { values: lam, vectors: V };
  }

  function evolveChain(eig, start, t) {
    /* |psi(t)|^2 for exp(-iAt)|start>, given the eigendecomposition. */
    var n = start.length, i, j, coeff = [], re = [], im = [], out = [];
    for (j = 0; j < n; j++) {
      var c = 0;
      for (i = 0; i < n; i++) c += eig.vectors[i][j] * start[i];
      coeff.push(c);
    }
    for (i = 0; i < n; i++) { re.push(0); im.push(0); }
    for (j = 0; j < n; j++) {
      var ph = -eig.values[j] * t;
      var cr = Math.cos(ph) * coeff[j], ci = Math.sin(ph) * coeff[j];
      for (i = 0; i < n; i++) {
        re[i] += eig.vectors[i][j] * cr;
        im[i] += eig.vectors[i][j] * ci;
      }
    }
    for (i = 0; i < n; i++) out.push(re[i] * re[i] + im[i] * im[i]);
    return out;
  }

  /* ---- AE · ballistic against diffusive ---------------------------- */

  function animWalkRace(root) {
    var f = frame(root, "A front against a blob",
      "Both walkers start at the same place on the same line. The " +
      "classical one piles up where it began and spreads as √t; the " +
      "quantum one throws its weight into two fronts that keep moving, so " +
      "it spreads as t. That single change of exponent is the whole of " +
      "this autopsy: on the glued-trees graph the classical walker drifts " +
      "into an exponentially fat middle and never comes out, while the " +
      "quantum front sails across in time proportional to the depth.");

    var N = 61, mid = 30;
    var st = { t: 0, playing: false, timer: null };
    var W = 660, Hh = 250, pad = 34, base = 190, top = 44;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var barsG = s("g", {}, svg);
    var head = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, svg);
    var note = s("text", { x: pad, y: 42, class: "qq-t qq-muted qq-sm" }, svg);
    s("line", { x1: pad, y1: base, x2: W - pad, y2: base, class: "qq-axis" },
      svg);

    var A = [], i, j;
    for (i = 0; i < N; i++) {
      A.push([]);
      for (j = 0; j < N; j++) A[i].push(Math.abs(i - j) === 1 ? 1 : 0);
    }
    var eig = jacobiEigh(A, 14);
    var start = [];
    for (i = 0; i < N; i++) start.push(i === mid ? 1 : 0);

    function classicalDist(steps) {
      var d = [], nd, k;
      for (i = 0; i < N; i++) d.push(i === mid ? 1 : 0);
      for (k = 0; k < steps; k++) {
        nd = [];
        for (i = 0; i < N; i++) nd.push(0);
        for (i = 0; i < N; i++) {
          if (d[i] === 0) continue;
          var nb = [];
          if (i > 0) nb.push(i - 1);
          if (i < N - 1) nb.push(i + 1);
          for (j = 0; j < nb.length; j++) nd[nb[j]] += d[i] / nb.length;
        }
        d = nd;
      }
      return d;
    }

    function spread(p) {
      var m = 0;
      for (i = 0; i < N; i++) m += (i - mid) * (i - mid) * p[i];
      return m;
    }

    function draw() {
      var q = evolveChain(eig, start, st.t);
      var c = classicalDist(Math.round(st.t));
      var bw = (W - 2 * pad) / N, mx = 0;
      for (i = 0; i < N; i++) mx = Math.max(mx, q[i], c[i]);
      mx = Math.max(mx, 0.05);
      clear(barsG);
      for (i = 0; i < N; i++) {
        var hq = (base - top) * q[i] / mx, hc = (base - top) * c[i] / mx;
        s("rect", { x: pad + i * bw + 1, y: base - hq,
          width: bw - 2, height: Math.max(hq, 0.6),
          class: "qq-bar qq-pos", opacity: 0.85 }, barsG);
        s("rect", { x: pad + i * bw + bw * 0.3, y: base - hc,
          width: bw * 0.4, height: Math.max(hc, 0.6),
          class: "qq-bar qq-neg", opacity: 0.9 }, barsG);
      }
      head.textContent = "t = " + st.t.toFixed(0) +
        "   ·   quantum ⟨x²⟩ = " + spread(q).toFixed(1) +
        "   ·   classical ⟨x²⟩ = " + spread(c).toFixed(1);
      note.textContent = "blue: the quantum walk (fronts).  amber: the " +
        "classical walk (a blob that never leaves).";
    }

    function stop() {
      if (st.timer) { clearInterval(st.timer); st.timer = null; }
      st.playing = false;
    }

    var ctr = h("div", "qq-ctrl", f.body);
    btn(ctr, "play", function () {
      if (st.playing) { stop(); return; }
      st.playing = true;
      st.timer = setInterval(function () {
        st.t += 1;
        if (st.t > 26) { st.t = 0; }
        draw();
      }, reduced() ? 400 : 160);
    });
    btn(ctr, "step", function () { stop(); st.t += 1; draw(); },
      "qq-btn-ghost");
    btn(ctr, "reset", function () { stop(); st.t = 0; draw(); },
      "qq-btn-ghost");
    draw();
  }

  /* ---- AF · what disorder does to the exponential ------------------ */

  function animDisorderWalk(root) {
    var f = frame(root, "The advantage needs a perfect graph",
      "The glued-trees speedup exists because the reduced chain is exactly " +
      "uniform — the graph is engineered that way. Add a little randomness " +
      "to the site energies, as any real defect would, and one dimension " +
      "does what one dimension always does: the eigenstates localise and " +
      "transport stops. Watch the packet fail to arrive. The uncomfortable " +
      "part is the scaling: the tolerable imperfection shrinks as the " +
      "problem grows.");

    var st = { d: 12, W: 0, seed: 7 };
    var Wd = 660, Hh = 250, pad = 34, base = 186, top = 48;
    var svg = s("svg", { viewBox: "0 0 " + Wd + " " + Hh, class: "qq-svg" },
      f.body);
    var barsG = s("g", {}, svg);
    var head = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, svg);
    var note = s("text", { x: pad, y: 42, class: "qq-t qq-muted qq-sm" }, svg);
    var verdict = s("text", { x: pad, y: base + 36, class: "qq-t qq-hot" },
      svg);

    function rand(seed) {          // deterministic, so the figure is stable
      var x = Math.sin(seed) * 10000;
      return x - Math.floor(x);
    }

    function build() {
      var L = 2 * st.d + 2, A = [], i, j;
      for (i = 0; i < L; i++) {
        A.push([]);
        for (j = 0; j < L; j++) A[i].push(0);
      }
      for (j = 0; j < L - 1; j++) {
        var w = (j === st.d) ? 2 : Math.SQRT2;
        A[j][j + 1] = A[j + 1][j] = w;
      }
      for (i = 0; i < L; i++) {
        A[i][i] = st.W * (rand(st.seed + i * 7.13) - 0.5);
      }
      return A;
    }

    function draw() {
      var A = build(), L = A.length, i;
      var eig = jacobiEigh(A, 16);
      var start = [];
      for (i = 0; i < L; i++) start.push(i === 0 ? 1 : 0);
      var best = 0, bestT = 0, tt;
      for (tt = 0; tt <= 4 * st.d; tt += 0.1) {
        var p = evolveChain(eig, start, tt);
        if (p[L - 1] > best) { best = p[L - 1]; bestT = tt; }
      }
      var shown = evolveChain(eig, start, bestT);
      var bw = (Wd - 2 * pad) / L, mx = 0;
      for (i = 0; i < L; i++) mx = Math.max(mx, shown[i]);
      clear(barsG);
      for (i = 0; i < L; i++) {
        var hgt = (base - top) * shown[i] / (mx > 1e-9 ? mx : 1);
        s("rect", { x: pad + i * bw + 1, y: base - hgt,
          width: Math.max(bw - 2, 1), height: Math.max(hgt, 0.7),
          class: "qq-bar " + (i === L - 1 ? "qq-hotbar"
            : (i === 0 ? "qq-neg" : "qq-pos")) }, barsG);
      }
      s("line", { x1: pad, y1: base, x2: Wd - pad, y2: base,
        class: "qq-axis" }, barsG);
      var t1 = s("text", { x: pad, y: base + 16,
        class: "qq-t qq-muted qq-sm" }, barsG);
      t1.textContent = "entrance";
      var t2 = s("text", { x: Wd - pad, y: base + 16,
        class: "qq-t-end qq-muted qq-sm" }, barsG);
      t2.textContent = "exit";

      head.textContent = "depth d = " + st.d + "  (graph has ~2^" +
        (st.d + 2) + " vertices)   ·   disorder W = " + st.W.toFixed(2);
      note.textContent = "amplitude at the best possible measurement time, " +
        "t* = " + bestT.toFixed(1);
      verdict.textContent = "exit probability " + best.toFixed(4) +
        (st.W === 0 ? "   —   the clean, engineered graph"
          : best > 0.05 ? "   —   still crossing, but weaker"
            : "   —   the packet no longer arrives: localised");
    }

    var ctr = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr, "depth d", 6, 24, st.d, function (v) { st.d = v; draw(); });
    var ctr2 = h("div", "qq-ctrl", f.body);
    var wsl = h("input", "qq-range", ctr2);
    h("span", "qq-bits-l", ctr2, "");
    wsl.type = "range"; wsl.min = 0; wsl.max = 40; wsl.step = 1; wsl.value = 0;
    wsl.addEventListener("input", function () {
      st.W = (+wsl.value) / 10; draw();
    });
    ctr2.insertBefore(h("span", "qq-bits-l", null, "disorder W"), wsl);
    btn(ctr2, "new defects", function () {
      st.seed = 1 + Math.random() * 500; draw();
    }, "qq-btn-ghost");
    draw();
  }

  /* ---- AG · Szegedy: the square root, on real chains --------------- */

  function animSzegedyGap(root) {
    var f = frame(root, "Every systematic walk speedup is a square root",
      "Szegedy's construction turns any reversible Markov chain into a " +
      "quantum walk, and the walk's phase gap is the arccos of the chain's " +
      "spectrum — which for a small classical gap δ is about 2√2·√δ. So " +
      "hitting and search cost 1/√δ where classical costs 1/δ. Quadratic, " +
      "systematically, for every chain. The glued-trees exponential is not " +
      "of this family, and that is exactly why it needed a hand-built " +
      "graph.");

    var st = { kind: "cycle", n: 12 };
    var W = 660, Hh = 236;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);
    var head = s("text", { x: 24, y: 24, class: "qq-t qq-ink" }, svg);

    function chain() {
      var n = st.n, P = [], i, j;
      for (i = 0; i < n; i++) {
        P.push([]);
        for (j = 0; j < n; j++) P[i].push(0);
      }
      if (st.kind === "cycle") {
        for (i = 0; i < n; i++) {
          P[i][(i + 1) % n] += 0.5;
          P[i][(i + n - 1) % n] += 0.5;
        }
      } else if (st.kind === "path") {
        for (i = 0; i < n; i++) {
          var nb = [];
          if (i > 0) nb.push(i - 1);
          if (i < n - 1) nb.push(i + 1);
          for (j = 0; j < nb.length; j++) P[i][nb[j]] = 1 / nb.length;
        }
      } else if (st.kind === "complete") {
        for (i = 0; i < n; i++) {
          for (j = 0; j < n; j++) if (i !== j) P[i][j] = 1 / (n - 1);
        }
      } else {                                   // barbell
        var half = n >> 1;
        for (i = 0; i < n; i++) {
          for (j = 0; j < n; j++) {
            var same = (i < half) === (j < half);
            if (i !== j && same) P[i][j] = 1;
          }
        }
        P[half - 1][half] = 1; P[half][half - 1] = 1;
        for (i = 0; i < n; i++) {
          var tot = 0;
          for (j = 0; j < n; j++) tot += P[i][j];
          for (j = 0; j < n; j++) P[i][j] /= tot;
        }
      }
      // laziness: stay put with probability 1/2 (kills the -1 eigenvalue)
      for (i = 0; i < n; i++) {
        for (j = 0; j < n; j++) P[i][j] *= 0.5;
        P[i][i] += 0.5;
      }
      return P;
    }

    function draw() {
      clear(g);
      var P = chain(), n = P.length, i, j;
      // The discriminant D_xy = sqrt(P_xy P_yx). For a reversible chain it
      // is symmetric and has exactly the chain's spectrum — which averaging
      // (P + P^T)/2 does NOT, as soon as the vertices have unequal degrees.
      var D = [];
      for (i = 0; i < n; i++) {
        D.push([]);
        for (j = 0; j < n; j++) D[i].push(Math.sqrt(P[i][j] * P[j][i]));
      }
      var eig = jacobiEigh(D, 16);
      var vals = eig.values.slice().sort(function (a, b) {
        return Math.abs(b) - Math.abs(a);
      });
      var delta = 1 - Math.abs(vals[1]);
      var pgap = 2 * Math.acos(Math.min(1, Math.abs(vals[1])));

      // the spectrum, drawn
      var x0 = 34, wid = W - 2 * x0, base = 120;
      s("line", { x1: x0, y1: base, x2: x0 + wid, y2: base,
        class: "qq-axis" }, g);
      for (i = 0; i < n; i++) {
        var xx = x0 + (vals[i] + 1) / 2 * wid;
        s("circle", { cx: xx, cy: base, r: 5,
          class: i === 0 ? "qq-hotbar" : "qq-pos", opacity: 0.85 }, g);
      }
      var lt = s("text", { x: x0, y: base + 20, class: "qq-t qq-muted qq-sm" },
        g);
      lt.textContent = "−1";
      var rt = s("text", { x: x0 + wid, y: base + 20,
        class: "qq-t-end qq-muted qq-sm" }, g);
      rt.textContent = "+1   ← eigenvalues of the chain";

      var rows = [
        ["classical spectral gap  δ", delta.toFixed(5)],
        ["quantum phase gap  2·arccos(λ₂)", pgap.toFixed(5)],
        ["ratio to √δ", (pgap / Math.sqrt(delta)).toFixed(4) + "   (2√2 = " +
          (2 * Math.SQRT2).toFixed(4) + ")"],
        ["classical cost ~ 1/δ", (1 / delta).toFixed(1)],
        ["quantum cost ~ 1/√δ", (1 / Math.sqrt(delta)).toFixed(1)],
        ["speedup", (Math.sqrt(1 / delta)).toFixed(1) + "×"]
      ];
      for (i = 0; i < rows.length; i++) {
        var y = 152 + i * 15;
        if (y > Hh - 6) break;
        var a = s("text", { x: 34, y: y, class: "qq-t qq-muted qq-sm" }, g);
        a.textContent = rows[i][0];
        var b = s("text", { x: 330, y: y, class: "qq-t qq-ink" }, g);
        b.setAttribute("font-size", "12");
        b.setAttribute("font-family", "ui-monospace, monospace");
        b.textContent = rows[i][1];
      }
      head.textContent = st.kind + " on " + n + " vertices (lazy)";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", ctr, "chain");
    [["cycle", "cycle"], ["path", "path"], ["complete", "complete"],
     ["barbell", "barbell"]].forEach(function (p) {
      btn(ctr, p[1], function () { st.kind = p[0]; draw(); }, "qq-btn-ghost");
    });
    rangeCtl(ctr, "size", 6, 20, st.n, function (v) {
      st.n = v % 2 ? v + 1 : v; draw();
    });
    draw();
  }

  /* =================================================================
   * AUTOPSY 09 · Hamiltonian simulation
   *
   *   trotterslice  slicing time, and the commutator that survives
   *   entwall       entanglement growth and what a tensor network must store
   *   simcost       Trotter against qubitization, and the knob between them
   * ================================================================= */

  /* ---- AH · why slicing works, and what it costs -------------------- */

  function animTrotterSlice(root) {
    var f = frame(root, "Slicing time, and the commutator that will not slice",
      "e^{-i(A+B)t} is not e^{-iAt}e^{-iBt}, because A and B do not commute. " +
      "Cut the time into r slices and alternate, and the error falls — as " +
      "1/r for the naive ordering, as 1/r² if you symmetrise the slice. The " +
      "quantity that sets the size of the error is the commutator ‖[A,B]‖, " +
      "not ‖A‖‖B‖, and on a local chain that difference is the whole reason " +
      "product formulas are competitive at all.");

    var st = { r: 4, order: 2, t: 1.0 };
    var W = 660, Hh = 246, pad = 40, base = 176, top = 46;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);
    var head = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, svg);
    var note = s("text", { x: pad, y: Hh - 10, class: "qq-t qq-muted qq-sm" },
      svg);

    /* Model: error(r) = C t^(k+1) / r^k with k the order. C is fixed from
       the measured first-order constant of the 6-site chain in trotter.py,
       so the curve the widget draws is the one the module measures. */
    var C = 14.0;                       // ||[A,B]|| at n = 6, from trotter.py
    function err(r, order) {
      var k = order;
      return (C / (2 * Math.pow(3, order - 1))) *
        Math.pow(st.t, k + 1) / Math.pow(r, k);
    }

    function draw() {
      clear(g);
      var i;
      // the time axis, sliced
      var y0 = 74, x0 = pad, wid = W - 2 * pad;
      s("line", { x1: x0, y1: y0, x2: x0 + wid, y2: y0, class: "qq-axis" }, g);
      for (i = 0; i <= st.r; i++) {
        var x = x0 + (i / st.r) * wid;
        s("line", { x1: x, y1: y0 - 12, x2: x, y2: y0 + 12,
          style: "stroke: var(--qq-line)", "stroke-width": 1.2 }, g);
      }
      for (i = 0; i < st.r; i++) {
        var xa = x0 + (i / st.r) * wid, w = wid / st.r;
        if (st.order === 1) {
          s("rect", { x: xa, y: y0 - 10, width: w / 2, height: 20,
            class: "qq-tile-pos", opacity: 0.85 }, g);
          s("rect", { x: xa + w / 2, y: y0 - 10, width: w / 2, height: 20,
            class: "qq-tile-neg", opacity: 0.85 }, g);
        } else {
          s("rect", { x: xa, y: y0 - 10, width: w / 4, height: 20,
            class: "qq-tile-pos", opacity: 0.85 }, g);
          s("rect", { x: xa + w / 4, y: y0 - 10, width: w / 2, height: 20,
            class: "qq-tile-neg", opacity: 0.85 }, g);
          s("rect", { x: xa + 3 * w / 4, y: y0 - 10, width: w / 4, height: 20,
            class: "qq-tile-pos", opacity: 0.85 }, g);
        }
      }
      var lg = s("text", { x: x0, y: y0 - 22, class: "qq-t qq-muted qq-sm" }, g);
      lg.textContent = st.order === 1
        ? "each slice: e^{-iA dt} then e^{-iB dt}"
        : "each slice: half of A, all of B, half of A  (symmetric)";

      // the error curve
      var cx0 = pad, cw = W - 2 * pad;
      s("line", { x1: cx0, y1: base, x2: cx0 + cw, y2: base,
        class: "qq-axis" }, g);
      var rmax = 64, lo = Math.log(err(rmax, 2)), hi = Math.log(err(1, 1));
      function ypos(v) {
        return base - (base - top) * (Math.log(v) - lo) / (hi - lo);
      }
      [1, 2].forEach(function (ord) {
        var d = "", rr;
        for (rr = 1; rr <= rmax; rr++) {
          var x = cx0 + (Math.log(rr) / Math.log(rmax)) * cw;
          d += (rr === 1 ? "M" : "L") + x.toFixed(1) + "," +
            ypos(err(rr, ord)).toFixed(1);
        }
        s("path", { d: d, fill: "none",
          style: "stroke: var(--qq-" + (ord === st.order ? "hot" : "line") +
            ")", "stroke-width": ord === st.order ? 2.4 : 1.4 }, g);
      });
      var mx = cx0 + (Math.log(st.r) / Math.log(rmax)) * cw;
      s("circle", { cx: mx, cy: ypos(err(st.r, st.order)), r: 5,
        style: "fill: var(--qq-hot)" }, g);
      var t2 = s("text", { x: cx0, y: top - 8, class: "qq-t qq-muted qq-sm" },
        g);
      t2.textContent = "error against slice count (both axes logarithmic)";

      head.textContent = "order " + st.order + ",  r = " + st.r +
        " slices   ·   error ≈ " + err(st.r, st.order).toExponential(2);
      note.textContent = "halving the slice width divides the error by " +
        (st.order === 1 ? "2" : "4") + " — slope −" + st.order +
        " on this plot. Doubling the order is worth far more than doubling r.";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr, "slices r", 1, 64, st.r, function (v) { st.r = v; draw(); });
    h("span", "qq-bits-l", ctr, "order");
    [1, 2].forEach(function (o) {
      btn(ctr, String(o), function () { st.order = o; draw(); },
        "qq-btn-ghost");
    });
    draw();
  }

  /* ---- AI · the entanglement wall ---------------------------------- */

  function animEntWall(root) {
    var f = frame(root, "Why the classical methods die — and when they do not",
      "A matrix-product state stores a wavefunction in bond dimension χ, " +
      "and it needs χ ≈ 2^S where S is the entanglement entropy across a " +
      "cut. Under a quench, S grows linearly in time, so χ grows " +
      "exponentially in time and the classical cost explodes. Ground states " +
      "are the opposite story: gapped ones obey an area law and stay cheap " +
      "forever, critical ones grow only logarithmically. Two thirds of " +
      "“classical methods fail” is not true, and knowing which third you " +
      "are in is the whole argument.");

    var st = { regime: "quench", x: 4 };
    var W = 660, Hh = 250, pad = 40, base = 186, top = 52;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);
    var head = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, svg);
    var note = s("text", { x: pad, y: Hh - 10, class: "qq-t qq-muted qq-sm" },
      svg);

    /* Fitted from entanglement_wall.py on a 14-site critical chain:
       quench S = 0.94 t;  critical ground state S = 0.097 log2 n + 0.24;
       gapped ground state S = 0.128 (flat). */
    function entropy(x) {
      if (st.regime === "quench") return 0.94 * x;
      if (st.regime === "critical") return 0.097 * Math.log(x) / Math.LN2 + 0.24;
      return 0.128;
    }

    function draw() {
      clear(g);
      var i, xmax = 32;
      s("line", { x1: pad, y1: base, x2: W - pad, y2: base, class: "qq-axis" },
        g);
      var smax = 30;
      function ypos(v) { return base - (base - top) * Math.min(v, smax) / smax; }
      var d = "";
      for (i = 1; i <= xmax; i++) {
        var x = pad + ((i - 1) / (xmax - 1)) * (W - 2 * pad);
        d += (i === 1 ? "M" : "L") + x.toFixed(1) + "," +
          ypos(entropy(i)).toFixed(1);
      }
      s("path", { d: d, fill: "none", style: "stroke: var(--qq-hot)",
        "stroke-width": 2.4 }, g);
      var cx = pad + ((st.x - 1) / (xmax - 1)) * (W - 2 * pad);
      s("circle", { cx: cx, cy: ypos(entropy(st.x)), r: 6,
        style: "fill: var(--qq-hot)" }, g);

      var S = entropy(st.x), chi = Math.pow(2, S);
      var bytes = 50 * chi * chi * 32;
      var rows = [
        ["entanglement entropy S", S.toFixed(2) + " bits"],
        ["bond dimension χ ≈ 2^S", chi < 1e6 ? chi.toFixed(0)
          : chi.toExponential(2)],
        ["MPS memory (50 sites)", bytes < 1e9 ? (bytes / 1e6).toFixed(1) + " MB"
          : bytes < 1e15 ? (bytes / 1e9).toFixed(1) + " GB"
            : bytes.toExponential(1) + " bytes"]
      ];
      for (i = 0; i < rows.length; i++) {
        var a = s("text", { x: W - pad - 250, y: top + 4 + i * 16,
          class: "qq-t qq-muted qq-sm" }, g);
        a.textContent = rows[i][0];
        var b = s("text", { x: W - pad, y: top + 4 + i * 16,
          class: "qq-t-end qq-ink" }, g);
        b.setAttribute("font-size", "12.5");
        b.setAttribute("font-family", "ui-monospace, monospace");
        b.textContent = rows[i][1];
      }

      head.textContent = st.regime === "quench"
        ? "quench dynamics — horizontal axis is TIME t"
        : "ground state — horizontal axis is SYSTEM SIZE n";
      note.textContent = st.regime === "quench"
        ? "S grows linearly in time, so the memory doubles every ~1.1 units "
          + "of t. This is the wall, and it is a property of the dynamics."
        : st.regime === "critical"
          ? "logarithmic in n: bond dimension only polynomial. Harder than "
            + "gapped, but not a wall — DMRG still copes."
          : "flat: the area law. Constant bond dimension at any size, which "
            + "is why DMRG has eaten these since 1992.";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", ctr, "regime");
    [["quench", "quench dynamics"], ["critical", "critical ground state"],
     ["gapped", "gapped ground state"]].forEach(function (p) {
      btn(ctr, p[1], function () { st.regime = p[0]; draw(); }, "qq-btn-ghost");
    });
    var ctr2 = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr2, "t  or  n", 1, 32, st.x, function (v) { st.x = v; draw(); });
    draw();
  }

  /* ---- AJ · Trotter against qubitization --------------------------- */

  function animSimCost(root) {
    var f = frame(root, "Optimal is not the same as cheaper",
      "Qubitization is asymptotically optimal: its cost is αt + log(1/ε), " +
      "exponentially better in the precision than any product formula. But " +
      "α — the sum of the Hamiltonian's coefficients — is paid linearly and " +
      "grows with the system, while Trotter pays only a root of the " +
      "commutator norm. Slide the ratio and watch the winner change. This " +
      "is the number applied papers spend their whole effort shrinking, and " +
      "it is the one the optimality theorem does not mention.");

    var st = { ratio: 1, epsExp: 4, terms: 36, t: 10 };
    var W = 660, Hh = 236;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);
    var STAGES = { 2: 2, 4: 5, 6: 11 };

    function costs() {
      var eps = Math.pow(10, -st.epsExp);
      var alpha = 14.0;                       // fixed; the ratio moves comm
      var comm = alpha / st.ratio;
      var best = Infinity, bestOrder = 2;
      [2, 4, 6].forEach(function (o) {
        var k = o / 2;
        var r = Math.max(1, Math.ceil(Math.pow(
          comm * Math.pow(st.t, 2 * k + 1) / eps, 1 / (2 * k))));
        var c = r * st.terms * STAGES[o];
        if (c < best) { best = c; bestOrder = o; }
      });
      var q = (alpha * st.t + Math.log(1 / eps) / Math.LN2) * st.terms * 2;
      return { trotter: best, order: bestOrder, qub: q, alpha: alpha,
        comm: comm, eps: eps };
    }

    function draw() {
      clear(g);
      var c = costs(), i;
      var x0 = 40, wid = W - 2 * x0, base = 150, top = 46;
      var mx = Math.max(c.trotter, c.qub) * 1.15;
      var bars = [["best product formula (order " + c.order + ")", c.trotter,
        c.trotter < c.qub ? "qq-pos" : "qq-neg"],
      ["qubitization", c.qub, c.qub <= c.trotter ? "qq-pos" : "qq-neg"]];
      for (i = 0; i < bars.length; i++) {
        var wpx = (wid - 220) * bars[i][1] / mx;
        s("rect", { x: x0 + 220, y: top + i * 42, width: Math.max(wpx, 2),
          height: 28, class: "qq-bar " + bars[i][2] }, g);
        var lab = s("text", { x: x0 + 212, y: top + i * 42 + 19,
          class: "qq-t-end qq-muted qq-sm" }, g);
        lab.textContent = bars[i][0];
        var val = s("text", { x: x0 + 228 + Math.max(wpx, 2),
          y: top + i * 42 + 19, class: "qq-t qq-ink" }, g);
        val.setAttribute("font-size", "12");
        val.setAttribute("font-family", "ui-monospace, monospace");
        val.textContent = Math.round(bars[i][1]).toLocaleString();
      }
      s("line", { x1: x0, y1: base, x2: W - x0, y2: base, class: "qq-axis" },
        g);

      var head = s("text", { x: x0, y: 24, class: "qq-t qq-ink" }, g);
      head.textContent = "α = " + c.alpha.toFixed(1) + ",  ‖[A,B]‖ = " +
        c.comm.toFixed(2) + ",  ratio = " + st.ratio +
        ",  ε = 1e-" + st.epsExp + ",  t = " + st.t;
      var v = s("text", { x: x0, y: base + 26, class: "qq-t qq-hot" }, g);
      v.setAttribute("font-size", "13.5");
      v.textContent = c.trotter < c.qub
        ? "Trotter wins by " + (c.qub / c.trotter).toFixed(2) + "×"
        : "qubitization wins by " + (c.trotter / c.qub).toFixed(2) + "×";
      var w = s("text", { x: x0, y: base + 46, class: "qq-t qq-muted qq-sm" },
        g);
      w.textContent = st.ratio > 8
        ? "a Hamiltonian dominated by a commuting block — Trotter's home ground"
        : "α and the commutator are comparable — the optimal method is also "
          + "the cheaper one";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr, "α / ‖[A,B]‖", 1, 60, st.ratio, function (v) {
      st.ratio = v; draw();
    });
    var ctr2 = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr2, "precision 1e−", 1, 12, st.epsExp, function (v) {
      st.epsExp = v; draw();
    });
    rangeCtl(ctr2, "time t", 1, 40, st.t, function (v) { st.t = v; draw(); });
    draw();
  }

  /* =================================================================
   * AUTOPSY 10 · QSP / qubitization / QSVT
   *
   *   qspdial    turn the phases, watch the polynomial change
   *   degreecost every algorithm's parameter, as a polynomial degree
   *   twofactor  the encoding test and the degree test, side by side
   * ================================================================= */

  /* ---- AK · choosing phases is choosing a polynomial --------------- */

  function animQspDial(root) {
    var f = frame(root, "Turn the phases, change the algorithm",
      "This is the whole of quantum signal processing. Between each " +
      "application of the block-encoding you insert one single-qubit " +
      "rotation; the top-left entry of the product is then a bounded " +
      "polynomial of the encoded eigenvalue, of degree equal to the number " +
      "of applications and of parity equal to that degree. Set every phase " +
      "to zero and you get the Chebyshev polynomial — the walk-operator " +
      "picture. Turn them and you sweep out (essentially) every other " +
      "reachable polynomial. Choosing the phases IS choosing your " +
      "algorithm.");

    var st = { phases: [0, 0, 0, 0, 0, 0] };
    var W = 660, Hh = 268, pad = 44, base = 148, mid = 148, amp = 92;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);
    var head = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, svg);
    var note = s("text", { x: pad, y: Hh - 10, class: "qq-t qq-muted qq-sm" },
      svg);

    /* Re<0|U(x)|0> for the QSP product, evaluated with 2x2 complex maths
       written out by hand — same construction as qsp_phases.py. */
    function response(x) {
      var ph = st.phases;
      var sq = Math.sqrt(Math.max(0, 1 - x * x));
      // U as [[a, b], [c, d]] with complex entries stored as pairs
      var ar = Math.cos(ph[0]), ai = Math.sin(ph[0]);
      var br = 0, bi = 0, cr = 0, ci = 0;
      var dr = Math.cos(ph[0]), di = -Math.sin(ph[0]);
      for (var k = 1; k < ph.length; k++) {
        // multiply by W(x) = [[x, i s], [i s, x]]
        var nar = ar * x - bi * sq, nai = ai * x + br * sq;
        var nbr = br * x - ai * sq, nbi = bi * x + ar * sq;
        var ncr = cr * x - di * sq, nci = ci * x + dr * sq;
        var ndr = dr * x - ci * sq, ndi = di * x + cr * sq;
        ar = nar; ai = nai; br = nbr; bi = nbi;
        cr = ncr; ci = nci; dr = ndr; di = ndi;
        // multiply by diag(e^{i phi}, e^{-i phi})
        var cp = Math.cos(ph[k]), sp = Math.sin(ph[k]);
        var tr = ar * cp - ai * sp; ai = ar * sp + ai * cp; ar = tr;
        var tr2 = br * cp + bi * sp; bi = -br * sp + bi * cp; br = tr2;
        var tr3 = cr * cp - ci * sp; ci = cr * sp + ci * cp; cr = tr3;
        var tr4 = dr * cp + di * sp; di = -dr * sp + di * cp; dr = tr4;
      }
      return ar;
    }

    function draw() {
      clear(g);
      var i, M = 260, d = st.phases.length - 1;
      s("line", { x1: pad, y1: mid, x2: W - pad, y2: mid, class: "qq-axis" },
        g);
      s("line", { x1: (pad + W - pad) / 2, y1: mid - amp - 8,
        x2: (pad + W - pad) / 2, y2: mid + amp + 8, class: "qq-axis" }, g);
      // the +-1 guides: every reachable response is bounded by one
      [1, -1].forEach(function (v) {
        s("line", { x1: pad, y1: mid - amp * v, x2: W - pad, y2: mid - amp * v,
          class: "qq-mark" }, g);
      });
      var dd = "", ddc = "";
      for (i = 0; i <= M; i++) {
        var x = -1 + 2 * i / M;
        var px = pad + (i / M) * (W - 2 * pad);
        dd += (i ? "L" : "M") + px.toFixed(1) + "," +
          (mid - amp * response(x)).toFixed(1);
        ddc += (i ? "L" : "M") + px.toFixed(1) + "," +
          (mid - amp * Math.cos(d * Math.acos(Math.max(-1,
            Math.min(1, x))))).toFixed(1);
      }
      s("path", { d: ddc, fill: "none", style: "stroke: var(--qq-line)",
        "stroke-width": 1.4, "stroke-dasharray": "5 4" }, g);
      s("path", { d: dd, fill: "none", style: "stroke: var(--qq-hot)",
        "stroke-width": 2.4 }, g);

      var allzero = st.phases.every(function (p) { return Math.abs(p) < 1e-9; });
      head.textContent = "degree d = " + d + ",  parity " +
        (d % 2 ? "odd" : "even") +
        (allzero ? "   ·   every phase zero: this is T" + d : "");
      note.textContent = "dashed: the Chebyshev polynomial T" + d +
        " for comparison.   The curve never leaves ±1 — it is an entry of a " +
        "unitary, so that is a theorem, not a choice.";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    h("span", "qq-bits-l", ctr, "phases");
    st.phases.forEach(function (_, k) {
      var r = h("input", "qq-range", ctr);
      r.type = "range"; r.min = -157; r.max = 157; r.step = 1; r.value = 0;
      r.style.flex = "0 1 5.2rem";
      r.addEventListener("input", function () {
        st.phases[k] = (+r.value) / 100; draw();
      });
    });
    var ctr2 = h("div", "qq-ctrl", f.body);
    btn(ctr2, "all zero (Chebyshev)", function () {
      st.phases = st.phases.map(function () { return 0; });
      Array.prototype.forEach.call(
        f.body.querySelectorAll("input.qq-range"), function (r) {
          r.value = 0;
        });
      draw();
    }, "qq-btn-ghost");
    btn(ctr2, "randomise", function () {
      var inputs = f.body.querySelectorAll("input.qq-range");
      st.phases = st.phases.map(function () {
        return (Math.random() * 2 - 1) * 1.4;
      });
      Array.prototype.forEach.call(inputs, function (r, k) {
        r.value = Math.round(st.phases[k] * 100);
      });
      draw();
    }, "qq-btn-ghost");
    draw();
  }

  /* ---- AL · every parameter is a degree ---------------------------- */

  function animDegreeCost(root) {
    var f = frame(root, "Every algorithm's parameter is a polynomial degree",
      "Grover's √N, HHL's condition number κ and Hamiltonian simulation's " +
      "evolution time t look like three different resources. Under QSVT " +
      "they are one: the degree of the polynomial you have to build. Move " +
      "the sliders and watch which one explodes when you demand more " +
      "precision — that difference, additive against multiplicative in " +
      "log(1/ε), is why simulation is the healthiest application in this " +
      "curriculum.");

    var st = { param: 8, epsExp: 3 };
    var W = 660, Hh = 236, pad = 46;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);

    /* Calibrated against polynomial_cost.py, which measures these by
       actually building the approximations. e = -log10(eps):
         sign  ~ p * (0.5 + 2.2 e)     multiplicative in the precision
         1/x   ~ p * (0.9 + 2.5 e)     multiplicative
         cos   ~ 1.06 p + 2 e          ADDITIVE — the whole point
       Checked against the module to within about 10%. */
    function degSign(p, e) { return Math.round(p * (0.5 + 2.2 * e)); }
    function degInv(p, e) { return Math.round(p * (0.9 + 2.5 * e)); }
    function degSim(p, e) { return Math.round(1.06 * p + 2 * e); }

    function draw() {
      clear(g);
      var e = st.epsExp, p = st.param, i;
      var rows = [
        ["search — sign(x), parameter √N", degSign(p, e), "qq-pos"],
        ["linear systems — 1/x, parameter κ", degInv(p, e), "qq-neg"],
        ["simulation — cos(tx), parameter t", degSim(p, e), "qq-hotbar"]
      ];
      var mx = Math.max(rows[0][1], rows[1][1], rows[2][1]) * 1.15;
      for (i = 0; i < rows.length; i++) {
        var y = 56 + i * 46;
        var wpx = (W - pad - 250) * rows[i][1] / mx;
        s("rect", { x: 250, y: y, width: Math.max(wpx, 2), height: 26,
          class: "qq-bar " + rows[i][2] }, g);
        var lab = s("text", { x: 242, y: y + 18,
          class: "qq-t-end qq-muted qq-sm" }, g);
        lab.textContent = rows[i][0];
        var val = s("text", { x: 258 + Math.max(wpx, 2), y: y + 18,
          class: "qq-t qq-ink" }, g);
        val.setAttribute("font-size", "12.5");
        val.setAttribute("font-family", "ui-monospace, monospace");
        val.textContent = "degree " + rows[i][1];
      }
      var head = s("text", { x: pad, y: 26, class: "qq-t qq-ink" }, g);
      head.textContent = "parameter = " + p + "   ·   target error ε = 1e-" +
        e + "   ·   degree = number of block-encoding applications";
      var v = s("text", { x: pad, y: 208, class: "qq-t qq-muted qq-sm" }, g);
      v.textContent = "Raise the precision slider: the first two bars grow " +
        "with it, the third barely moves. Additive versus multiplicative in " +
        "log(1/ε) is the whole difference.";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr, "parameter (√N, κ or t)", 2, 40, st.param, function (v) {
      st.param = v; draw();
    });
    var ctr2 = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr2, "precision 1e−", 1, 10, st.epsExp, function (v) {
      st.epsExp = v; draw();
    });
    draw();
  }

  /* ---- AM · the two-factor test ------------------------------------ */

  function animTwoFactor(root) {
    var f = frame(root, "The two-factor test for any QSVT claim",
      "QSVT is a compiler, not an advantage. An advantage needs two things " +
      "at once: a block-encoding that classical sampling cannot imitate, " +
      "AND a polynomial degree classical computers cannot afford. Pick a " +
      "candidate and see which box it fails. Almost every dequantised " +
      "result in this curriculum failed the first; almost every " +
      "disappointing speedup failed the second.");

    var CASES = [
      ["Grover / unstructured search", true, false,
        "the oracle is not imitable, but √N is only a quadratic saving — " +
        "autopsy 06 prices it"],
      ["HHL on low-rank data", false, true,
        "κ is a real cost, but a rank-k sketch reproduces the encoding — " +
        "this is exactly what Tang attacked"],
      ["HHL on sparse, well-conditioned systems", true, false,
        "not imitable, but a small κ means a small degree: nothing to win"],
      ["Hamiltonian simulation", true, true,
        "sparse encoding no sketch reproduces, and degree αt — the one that " +
        "survived"],
      ["Gibbs sampling at low temperature", true, true,
        "same shape as simulation; the degree is set by β and the spectral " +
        "gap (hunting ground C)"]
    ];
    var st = { i: 3 };
    var W = 660, Hh = 232;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);

    function box(x, y, ok, label) {
      s("rect", { x: x, y: y, width: 250, height: 62, rx: 8,
        class: ok ? "qq-tile-pos" : "qq-tile-neg", opacity: 0.9 }, g);
      var t1 = s("text", { x: x + 125, y: y + 26, class: "qq-t-mid" }, g);
      t1.setAttribute("fill", "#fff");
      t1.setAttribute("font-weight", "700");
      t1.setAttribute("font-size", "13");
      t1.textContent = ok ? "PASSES" : "FAILS";
      var t2 = s("text", { x: x + 125, y: y + 46, class: "qq-t-mid" }, g);
      t2.setAttribute("fill", "#fff");
      t2.setAttribute("font-size", "11");
      t2.textContent = label;
    }

    function draw() {
      clear(g);
      var c = CASES[st.i];
      var head = s("text", { x: 30, y: 26, class: "qq-t qq-ink" }, g);
      head.setAttribute("font-size", "15");
      head.textContent = c[0];
      box(30, 46, c[1], "encoding not imitable");
      box(320, 46, c[2], "degree unaffordable");
      var mark = s("text", { x: 30, y: 140, class: "qq-t qq-hot" }, g);
      mark.setAttribute("font-size", "14");
      mark.textContent = (c[1] && c[2])
        ? "→ both boxes pass: a real advantage claim"
        : "→ one box fails, so the advantage does not survive";
      var why = s("text", { x: 30, y: 166, class: "qq-t qq-muted qq-sm" }, g);
      why.textContent = c[3];
      var w2 = s("text", { x: 30, y: 200, class: "qq-t qq-muted qq-sm" }, g);
      w2.textContent = "The two factors are attacked by different people: " +
        "dequantisation goes after the left box, complexity lower bounds " +
        "after the right.";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    CASES.forEach(function (c, i) {
      btn(ctr, c[0].split(" ")[0] + (i === 2 ? " (sparse)" : ""), function () {
        st.i = i; draw();
      }, "qq-btn-ghost");
    });
    draw();
  }

  /* =================================================================
   * AUTOPSY 11 · HHL and Tang
   *
   *   readout    the output toll: a state is not a vector
   *   sqsample   length-squared sampling, and what a sketch recovers
   *   accessrule the access-model symmetry, applied to a claim
   * ================================================================= */

  /* ---- AN · the output toll ---------------------------------------- */

  function animReadout(root) {
    var f = frame(root, "The answer is a state, and a state is not a vector",
      "HHL prepares a quantum state proportional to the solution in time " +
      "polylogarithmic in the dimension. That is true, and it is not the " +
      "same as solving the system. Reading one component costs a number of " +
      "repetitions that does not depend on the dimension — genuinely cheap. " +
      "Reading the whole vector costs one such batch per component, which " +
      "puts the dimension straight back into the bill it was supposed to " +
      "have removed.");

    var st = { dimExp: 6, epsExp: 2, want: "one" };
    var W = 660, Hh = 232, pad = 40;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);

    function fmt(x) {
      if (x < 1e4) return Math.round(x).toLocaleString();
      return x.toExponential(2);
    }

    function draw() {
      clear(g);
      var dim = Math.pow(10, st.dimExp), eps = Math.pow(10, -st.epsExp);
      var one = Math.log(2 / 0.05) / (2 * eps * eps);
      var all = dim * Math.log(2 * dim / 0.05) / (2 * eps * eps);
      // one state preparation: 4 * kappa * log(1/eps) * log2(dim), the same
      // model hhl_tolls.py uses (kappa fixed at 100 here)
      var prep = 4 * 100 * Math.log(1 / eps) * Math.log(dim) / Math.LN2;
      var rows = [
        ["dimension", dim.toExponential(0)],
        ["one state preparation (κ = 100)", fmt(prep) + " gates"],
        ["repetitions for ONE amplitude", fmt(one)],
        ["repetitions for the WHOLE vector", fmt(all)],
        ["total, for the whole vector", fmt(prep * all) + " gates"],
        ["conjugate gradients, for comparison", fmt(4 * dim * 10 * 7) +
          " gates"]
      ];
      for (var i = 0; i < rows.length; i++) {
        var y = 34 + i * 26;
        var a = s("text", { x: pad, y: y, class: "qq-t qq-muted qq-sm" }, g);
        a.textContent = rows[i][0];
        var b = s("text", { x: W - pad, y: y, class: "qq-t-end qq-ink" }, g);
        b.setAttribute("font-size", "13");
        b.setAttribute("font-family", "ui-monospace, monospace");
        b.textContent = rows[i][1];
        if (i === 4 || i === 5) {
          b.setAttribute("fill", i === 4 ? "var(--qq-neg)" : "var(--qq-pos)");
        }
      }
      var v = s("text", { x: pad, y: 208, class: "qq-t qq-hot" }, g);
      v.setAttribute("font-size", "13");
      var ratio = (prep * all) / (4 * dim * 10 * 7);
      v.textContent = "matched outputs: the quantum route costs " +
        ratio.toExponential(1) + "× more than conjugate gradients";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr, "dimension 10^", 2, 12, st.dimExp, function (v) {
      st.dimExp = v; draw();
    });
    rangeCtl(ctr, "precision 1e−", 1, 6, st.epsExp, function (v) {
      st.epsExp = v; draw();
    });
    draw();
  }

  /* ---- AO · length-squared sampling -------------------------------- */

  function animSqSample(root) {
    var f = frame(root, "What the classical side is allowed to do",
      "Tang's argument is not about algorithms, it is about what each side " +
      "is given. If the quantum algorithm may prepare a state whose " +
      "amplitudes are the data, the honest classical analogue is " +
      "length-squared sampling: draw a row with probability proportional to " +
      "its squared norm. Rows carrying more weight are drawn more often, " +
      "which is exactly the distribution a measurement of the prepared " +
      "state would give — and with it, a handful of rows reconstructs what " +
      "the quantum algorithm was going to compute.");

    var st = { rows: 12, seedShift: 0 };
    var W = 660, Hh = 252, pad = 34;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);
    var N = 40;

    /* A synthetic matrix's row norms: a few heavy rows and a long tail —
       the shape real low-rank data has. */
    function norms() {
      var out = [], i;
      for (i = 0; i < N; i++) {
        var base = Math.exp(-i / 7) + 0.05;
        var jitter = 0.6 + 0.8 * Math.abs(Math.sin(i * 12.9898 +
          st.seedShift * 7.13));
        out.push(base * jitter);
      }
      return out;
    }

    function draw() {
      clear(g);
      var nm = norms(), i, tot2 = 0;
      for (i = 0; i < N; i++) tot2 += nm[i] * nm[i];
      var p = nm.map(function (v) { return v * v / tot2; });

      // draw the rows, height = norm, opacity = sampling probability
      var bw = (W - 2 * pad) / N, base = 150, top = 40;
      var mx = Math.max.apply(null, nm);
      // deterministic "sampling": take the r largest by probability, plus a
      // couple of tail draws, so the picture is stable across redraws
      var order = p.map(function (v, k) { return [v, k]; })
        .sort(function (a, b) { return b[0] - a[0]; });
      var chosen = {};
      for (i = 0; i < Math.min(st.rows, N); i++) chosen[order[i][1]] = true;

      for (i = 0; i < N; i++) {
        var hgt = (base - top) * nm[i] / mx;
        s("rect", { x: pad + i * bw + 1, y: base - hgt,
          width: Math.max(bw - 2, 1), height: Math.max(hgt, 1),
          class: "qq-bar " + (chosen[i] ? "qq-hotbar" : "qq-pos"),
          opacity: chosen[i] ? 1 : 0.35 }, g);
      }
      s("line", { x1: pad, y1: base, x2: W - pad, y2: base, class: "qq-axis" },
        g);

      var captured = 0;
      for (i = 0; i < N; i++) if (chosen[i]) captured += p[i];
      var head = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, g);
      head.textContent = st.rows + " of " + N + " rows sampled  —  they carry "
        + (100 * captured).toFixed(1) + "% of the matrix's total weight";
      var t2 = s("text", { x: pad, y: base + 22, class: "qq-t qq-muted qq-sm" },
        g);
      t2.textContent = "bar height = row norm.  Highlighted = drawn by " +
        "length-squared sampling.";
      var t3 = s("text", { x: pad, y: base + 46, class: "qq-t qq-hot" }, g);
      t3.setAttribute("font-size", "13");
      t3.textContent = captured > 0.9
        ? "→ the sketch already sees almost all the weight: the quantum "
          + "advantage was the access model"
        : "→ still missing weight: add rows, or the sketch will be wrong";
      var t4 = s("text", { x: pad, y: base + 68,
        class: "qq-t qq-muted qq-sm" }, g);
      t4.textContent = "Note what this does NOT do: if the weight is spread " +
        "evenly over all rows — a high-rank matrix — no small sample " +
        "captures it, and the classical shortcut disappears.";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr, "rows sampled", 1, 40, st.rows, function (v) {
      st.rows = v; draw();
    });
    btn(ctr, "different matrix", function () {
      st.seedShift += 1; draw();
    }, "qq-btn-ghost");
    draw();
  }

  /* ---- AP · the access-model symmetry rule ------------------------- */

  function animAccessRule(root) {
    var f = frame(root, "The rule this autopsy leaves behind",
      "Whatever preparation power a quantum algorithm is granted, the " +
      "classical baseline gets its sampling analogue — and then the " +
      "comparison is fair. Run a claim through it. The point is not that " +
      "quantum always loses; it is that the answer is decided by where the " +
      "input comes from, and that is a question you can settle before " +
      "reading the algorithm.");

    var CASES = [
      ["Recommendation systems (2016 claim)",
        "a classical user-item matrix, loaded into QRAM",
        "ℓ²-sampling access to the same matrix", false,
        "Tang 2018: the classical algorithm matches it. Low-rank data, " +
        "classical input — the speedup was the access assumption."],
      ["Quantum PCA on classical data",
        "QRAM-loaded covariance matrix",
        "ℓ²-sampling of the same rows", false,
        "same story, same year — low rank is what sampling is good at"],
      ["Linear systems, sparse and high-rank",
        "an efficiently-computable sparse matrix",
        "sampling gives you nothing: no small sketch reproduces it", true,
        "survives — this is the BQP-complete regime HHL actually owns"],
      ["Hamiltonian simulation",
        "a Hamiltonian, given as a description",
        "there is no data set to sample", true,
        "the access-model attack cannot even be posed: the input is " +
        "quantum-native (autopsy 09)"],
      ["Gibbs state properties",
        "a state produced by a quantum process",
        "no classical sampling access exists", true,
        "hunting ground C's structural immunity — and the reason it is a " +
        "hunting ground"]
    ];
    var st = { i: 0 };
    var W = 660, Hh = 250;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);

    function wrap(text, x, y, width, cls, size) {
      var words = text.split(" "), line = "", out = [], i;
      for (i = 0; i < words.length; i++) {
        if ((line + words[i]).length * size * 0.52 > width) {
          out.push(line); line = "";
        }
        line += words[i] + " ";
      }
      out.push(line);
      out.forEach(function (ln, k) {
        var t = s("text", { x: x, y: y + k * (size + 3), class: cls }, g);
        t.setAttribute("font-size", String(size));
        t.textContent = ln;
      });
      return out.length;
    }

    function draw() {
      clear(g);
      var c = CASES[st.i];
      var head = s("text", { x: 28, y: 26, class: "qq-t qq-ink" }, g);
      head.setAttribute("font-size", "15");
      head.textContent = c[0];

      var t1 = s("text", { x: 28, y: 56, class: "qq-t qq-muted qq-sm" }, g);
      t1.textContent = "what the quantum side is given:";
      wrap(c[1], 28, 74, 290, "qq-t qq-ink", 12);
      var t2 = s("text", { x: 350, y: 56, class: "qq-t qq-muted qq-sm" }, g);
      t2.textContent = "what the classical side then gets:";
      wrap(c[2], 350, 74, 290, "qq-t qq-ink", 12);

      s("rect", { x: 28, y: 128, width: W - 56, height: 40, rx: 8,
        class: c[3] ? "qq-tile-pos" : "qq-tile-neg", opacity: 0.9 }, g);
      var v = s("text", { x: W / 2, y: 154, class: "qq-t-mid" }, g);
      v.setAttribute("fill", "#fff");
      v.setAttribute("font-weight", "700");
      v.setAttribute("font-size", "14");
      v.textContent = c[3] ? "SURVIVES the symmetry test"
                           : "DIES under the symmetry test";
      wrap(c[4], 28, 190, W - 56, "qq-t qq-muted qq-sm", 11.5);
    }

    var ctr = h("div", "qq-ctrl", f.body);
    ["recommendations", "quantum PCA", "sparse systems", "simulation",
     "Gibbs"].forEach(function (label, i) {
      btn(ctr, label, function () { st.i = i; draw(); }, "qq-btn-ghost");
    });
    draw();
  }

  /* =================================================================
   * AUTOPSY 12 · Decoded Quantum Interferometry
   *
   *   dqichain    objective -> code -> decoder -> samples
   *   semicircle  the law, and the baseline it has to clear
   *   codereach   which codes have a decoder that reaches far enough
   * ================================================================= */

  /* ---- AQ · the reduction, one link at a time ---------------------- */

  function animDqiChain(root) {
    var f = frame(root, "Optimisation becomes decoding",
      "DQI's architecture is a chain of four reductions, and only the third " +
      "is quantum. The objective's Fourier spectrum sits on low-weight " +
      "combinations of the constraint vectors — words of a code. So " +
      "preparing a polynomial of the objective means preparing low-weight " +
      "error patterns and uncomputing them from their syndrome, which is " +
      "syndrome decoding. Step through it: the decoding radius the last " +
      "step can afford is the polynomial degree the first step gets, and " +
      "that degree is the answer's quality.");

    var st = { step: 0 };
    var W = 660, Hh = 250;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);

    var STEPS = [
      ["the objective", "f(x) = how many constraints x satisfies",
        "s(x) = 2f(x) − m = Σᵢ (−1)^(bᵢ + aᵢ·x) — a sum of m characters"],
      ["its Fourier support", "a code appears, unbidden",
        "P(s) of degree ℓ has all its weight on XORs of ≤ ℓ constraint " +
        "vectors — the low-weight words of the code the aᵢ generate"],
      ["the quantum step", "prepare weight-≤ℓ error patterns",
        "build the state on the Fourier side: Σ over error patterns y with " +
        "|y| ≤ ℓ, amplitudes wₖ chosen to maximise the objective"],
      ["the decoder", "uncompute y from its syndrome",
        "this is SYNDROME DECODING of the dual code — a sixty-year-old " +
        "classical toolbox, borrowed"],
      ["measure", "samples concentrate on high-objective x",
        "satisfied fraction = ½ + √(d(1−d)) with d = ℓ/m. A better decoder " +
        "is literally a better optimiser."]
    ];

    function draw() {
      clear(g);
      var i, y0 = 34;
      for (i = 0; i < STEPS.length; i++) {
        var on = i <= st.step;
        var y = y0 + i * 40;
        s("rect", { x: 26, y: y, width: 176, height: 30, rx: 6,
          class: on ? (i === 3 ? "qq-tile-neg" : "qq-tile-pos") : "qq-bit",
          opacity: on ? 0.92 : 0.3 }, g);
        var t1 = s("text", { x: 114, y: y + 20, class: "qq-t-mid" }, g);
        t1.setAttribute("fill", on ? "#fff" : "var(--qq-muted)");
        t1.setAttribute("font-size", "12");
        t1.setAttribute("font-weight", "700");
        t1.textContent = STEPS[i][0];
        var t2 = s("text", { x: 214, y: y + 13, class: "qq-t qq-ink" }, g);
        t2.setAttribute("font-size", "11.5");
        t2.setAttribute("opacity", on ? "1" : "0.35");
        t2.textContent = STEPS[i][1];
        if (i === st.step) {
          var t3 = s("text", { x: 214, y: y + 27, class: "qq-t qq-muted" }, g);
          t3.setAttribute("font-size", "10.5");
          t3.textContent = STEPS[i][2].length > 74
            ? STEPS[i][2].slice(0, 74) + "…" : STEPS[i][2];
        }
        if (i < STEPS.length - 1) {
          s("line", { x1: 114, y1: y + 30, x2: 114, y2: y + 40,
            class: "qq-axis" }, g);
        }
      }
      var note = s("text", { x: 26, y: Hh - 12, class: "qq-t qq-hot" }, g);
      note.setAttribute("font-size", "12.5");
      note.textContent = st.step >= 3
        ? "amber = the classical decoder: the step that decides everything"
        : "step " + (st.step + 1) + " of " + STEPS.length;
    }

    var ctr = h("div", "qq-ctrl", f.body);
    btn(ctr, "next step", function () {
      st.step = (st.step + 1) % STEPS.length; draw();
    });
    btn(ctr, "reset", function () { st.step = 0; draw(); }, "qq-btn-ghost");
    draw();
  }

  /* ---- AR · the semicircle against the baseline -------------------- */

  function animSemicircle(root) {
    var f = frame(root, "The law, and the line it has to clear",
      "DQI's satisfied fraction is ½ + √(d(1−d)) where d is the decoding " +
      "radius as a fraction of the constraints. The classical baseline — " +
      "Prange's information-set decoding — solves n constraints exactly and " +
      "gets the rest at chance, for ½ + n/2m. Move the sliders and read off " +
      "the radius a decoder must reach before there is anything to claim. " +
      "That number is a specification handed to coding theory, not to " +
      "physics.");

    var st = { d: 10, ratio: 40 };        // percent
    var W = 660, Hh = 260, pad = 46, base = 190, top = 40;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);

    function frac(d) { return 0.5 + Math.sqrt(d * (1 - d)); }

    function draw() {
      clear(g);
      var i, d = st.d / 100, nOverM = st.ratio / 100;
      var prange = 0.5 + nOverM / 2;
      var ymin = 0.45, ymax = 1.05;
      function ypos(v) {
        return base - (base - top) * (v - ymin) / (ymax - ymin);
      }
      s("line", { x1: pad, y1: base, x2: W - pad, y2: base, class: "qq-axis" },
        g);
      // the semicircle
      var dd = "";
      for (i = 0; i <= 200; i++) {
        var x = 0.5 * i / 200;
        dd += (i ? "L" : "M") + (pad + (x / 0.5) * (W - 2 * pad)).toFixed(1) +
          "," + ypos(frac(x)).toFixed(1);
      }
      s("path", { d: dd, fill: "none", style: "stroke: var(--qq-pos)",
        "stroke-width": 2.4 }, g);
      // the Prange line
      s("line", { x1: pad, y1: ypos(prange), x2: W - pad, y2: ypos(prange),
        style: "stroke: var(--qq-neg)", "stroke-width": 2,
        "stroke-dasharray": "6 4" }, g);
      // the current radius
      var cx = pad + (d / 0.5) * (W - 2 * pad);
      s("line", { x1: cx, y1: top - 6, x2: cx, y2: base, class: "qq-mark" }, g);
      s("circle", { cx: cx, cy: ypos(frac(d)), r: 6,
        style: "fill: var(--qq-hot)" }, g);

      // the radius needed
      var need = null;
      for (i = 1; i <= 500; i++) {
        var dv = 0.5 * i / 500;
        if (frac(dv) > prange) { need = dv; break; }
      }
      var lab = s("text", { x: pad, y: 24, class: "qq-t qq-ink" }, g);
      lab.textContent = "d = " + d.toFixed(2) + " → DQI " +
        frac(d).toFixed(4) + "   ·   n/m = " + nOverM.toFixed(2) +
        " → Prange " + prange.toFixed(4);
      var v = s("text", { x: pad, y: base + 26, class: "qq-t qq-hot" }, g);
      v.setAttribute("font-size", "13");
      v.textContent = frac(d) > prange
        ? "DQI ahead by " + (frac(d) - prange).toFixed(4) +
          "  —  a decoder reaching d = " + d.toFixed(2) + " suffices"
        : "DQI behind: this decoder is not deep enough" +
          (need ? "  —  it needs d ≥ " + need.toFixed(3) : "");
      var w = s("text", { x: pad, y: base + 48, class: "qq-t qq-muted qq-sm" },
        g);
      w.textContent = "green: ½ + √(d(1−d)).   dashed: ½ + n/2m.   " +
        "The crossing is the whole specification.";
    }

    var ctr = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr, "decoding radius d (%)", 1, 50, st.d, function (v) {
      st.d = v; draw();
    });
    var ctr2 = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr2, "baseline n/m (%)", 5, 95, st.ratio, function (v) {
      st.ratio = v; draw();
    });
    draw();
  }

  /* ---- AS · which codes reach far enough --------------------------- */

  function animCodeReach(root) {
    var f = frame(root, "Structure survived; randomness fell",
      "The 2026 ledger says random sparse instances were killed and " +
      "Reed–Solomon ones still stand. The mechanism is one line of coding " +
      "theory: an efficient decoder that reaches a constant fraction of the " +
      "constraints exists for algebraic codes and does not exist for random " +
      "ones. On a random code, DQI would be asking a decoder to beat " +
      "Prange — using Prange. The advantage cancels, and no amount of " +
      "quantum hardware changes it.");

    var st = { k: 50, m: 200 };
    var W = 660, Hh = 240, pad = 40;
    var svg = s("svg", { viewBox: "0 0 " + W + " " + Hh, class: "qq-svg" },
      f.body);
    var g = s("g", {}, svg);

    function draw() {
      clear(g);
      var m = st.m, k = st.k, i;
      var listR = m - Math.floor(Math.sqrt(m * k));
      var uniqueR = Math.floor((m - k) / 2);
      var rows = [
        ["Reed–Solomon, list decoding", listR, "qq-tile-pos",
          "Guruswami–Sudan: m − √(mk)"],
        ["Reed–Solomon, unique decoding", uniqueR, "qq-tile-pos",
          "(m − k)/2"],
        ["random linear code", 0, "qq-tile-neg",
          "no efficient decoder known past information-set — the attacker's " +
          "own algorithm"]
      ];
      var maxR = m / 2;
      for (i = 0; i < rows.length; i++) {
        var y = 46 + i * 50;
        var d = Math.min(rows[i][1], m) / m;
        var wpx = (W - pad - 250) * Math.min(d / 0.9, 1);
        s("rect", { x: 250, y: y, width: Math.max(wpx, 3), height: 26, rx: 4,
          class: rows[i][2], opacity: 0.9 }, g);
        var a = s("text", { x: 242, y: y + 18,
          class: "qq-t-end qq-muted qq-sm" }, g);
        a.textContent = rows[i][0];
        var b2 = s("text", { x: 258 + Math.max(wpx, 3), y: y + 12,
          class: "qq-t qq-ink" }, g);
        b2.setAttribute("font-size", "12");
        b2.setAttribute("font-family", "ui-monospace, monospace");
        b2.textContent = rows[i][1] > 0 ? "d = " + d.toFixed(3) : "d = —";
        var b3 = s("text", { x: 258 + Math.max(wpx, 3), y: y + 25,
          class: "qq-t qq-muted" }, g);
        b3.setAttribute("font-size", "9.5");
        b3.textContent = rows[i][3].length > 46
          ? rows[i][3].slice(0, 46) + "…" : rows[i][3];
      }
      var head = s("text", { x: pad, y: 26, class: "qq-t qq-ink" }, g);
      head.textContent = "m = " + m + " constraints,  code dimension k = " + k;
      var v = s("text", { x: pad, y: 214, class: "qq-t qq-hot" }, g);
      v.setAttribute("font-size", "12.5");
      v.textContent = "DQI at the list-decoding radius: satisfied fraction " +
        (0.5 + Math.sqrt(Math.min(listR / m, 0.5) *
          (1 - Math.min(listR / m, 0.5)))).toFixed(4);
    }

    var ctr = h("div", "qq-ctrl", f.body);
    rangeCtl(ctr, "code dimension k", 10, 180, st.k, function (v) {
      st.k = v; draw();
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
    constraints: animConstraints,
    chardial: animCharDial,
    shifteigen: animShiftEigen,
    spectrumlab: animSpectrumLab,
    butterfly: animButterfly,
    qftleak: animQftLeak,
    hsprank: animHspRank,
    tuner: animTuner,
    harmonics: animHarmonics,
    twovalues: animTwoValues,
    hspmachine: animHspMachine,
    dihedral: animDihedral,
    colourwl: animColourWl,
    groverspin: animGroverSpin,
    attention: animAttention,
    groverwall: animGroverWall,
    walkrace: animWalkRace,
    disorderwalk: animDisorderWalk,
    szegedygap: animSzegedyGap,
    trotterslice: animTrotterSlice,
    entwall: animEntWall,
    simcost: animSimCost,
    qspdial: animQspDial,
    degreecost: animDegreeCost,
    twofactor: animTwoFactor,
    readout: animReadout,
    sqsample: animSqSample,
    accessrule: animAccessRule,
    dqichain: animDqiChain,
    semicircle: animSemicircle,
    codereach: animCodeReach
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
