"""Generate the machines-catalog figures from machines/data.yml.

Single source of truth: every number plotted here is read from data.yml,
never hand-copied. Each figure renders twice (light/dark) as transparent
SVGs saved into machines/, following the same ink/series conventions as
scripts/make_figures.py. Categorical colors are assigned to hardware
modalities in a fixed slot order (data.yml `modalities.*.slot`), never
cycled; every mark carries a direct label.

Run from repo root:  .venv/bin/python scripts/make_machine_figures.py
"""

from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.ticker import NullFormatter
import yaml

ROOT = Path(__file__).resolve().parent.parent
OUT = "machines"

INK = {
    "light": dict(primary="#0b0b0b", secondary="#52514e", muted="#898781",
                  grid="#e1e0d9", axis="#c3c2b7"),
    "dark": dict(primary="#ffffff", secondary="#c3c2b7", muted="#898781",
                 grid="#2c2c2a", axis="#383835"),
}
# Categorical slots 1..7 (reference palette order — fixed, never cycled).
SERIES = {
    "light": ["#2a78d6", "#1baf7a", "#eda100", "#008300",
              "#4a3aa7", "#e34948", "#e87ba4"],
    "dark": ["#3987e5", "#199e70", "#c98500", "#008300",
             "#9085e9", "#e66767", "#d55181"],
}
# Ordinal single-hue ramp (blue), light->dark, for ordered magnitudes.
ORDINAL = {
    "light": ["#86b6ef", "#3987e5", "#1c5cab", "#0d366b"],
    "dark": ["#9ec5f4", "#6da7ec", "#2a78d6", "#184f95"],
}
# Assumed page surface, used only as a thin separation ring on markers.
SURFACE = {"light": "#fcfcfb", "dark": "#1a1a19"}

DATA = yaml.safe_load((ROOT / "machines" / "data.yml").read_text())
SLOT = {m: v["slot"] - 1 for m, v in DATA["modalities"].items()}
LABEL = {m: v["label"] for m, v in DATA["modalities"].items()}


def color(mode, modality):
    return SERIES[mode][SLOT[modality]]


def new_fig(mode, figsize=(7.0, 3.6)):
    ink = INK[mode]
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_alpha(0.0)
    ax.set_facecolor("none")
    for side in ("top", "right"):
        ax.spines[side].set_visible(False)
    for side in ("left", "bottom"):
        ax.spines[side].set_color(ink["axis"])
        ax.spines[side].set_linewidth(0.8)
    ax.tick_params(colors=ink["muted"], labelsize=9, width=0.8)
    ax.grid(True, color=ink["grid"], linewidth=0.6, alpha=0.9)
    ax.set_axisbelow(True)
    for lbl in (ax.xaxis.label, ax.yaxis.label, ax.title):
        lbl.set_color(ink["secondary"])
        lbl.set_fontsize(10)
    return fig, ax


def save(fig, stem, mode):
    suffix = "-dark" if mode == "dark" else ""
    out = ROOT / OUT / f"{stem}{suffix}.svg"
    fig.savefig(out, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"  {out.relative_to(ROOT)}")


def legend(ax, mode, modalities, loc="upper right"):
    ink = INK[mode]
    handles = [plt.Line2D([], [], marker="o", linestyle="", markersize=7,
                          color=color(mode, m), label=LABEL[m])
               for m in sorted(modalities, key=lambda m: SLOT[m])]
    leg = ax.legend(handles=handles, loc=loc, frameon=False, fontsize=8.5,
                    handletextpad=0.2, borderaxespad=0.2)
    for t in leg.get_texts():
        t.set_color(ink["secondary"])
    return leg


def scatter_points():
    """Gate-based machines with both a qubit count and a sourced 2Q error."""
    pts = []
    for m in DATA["machines"]:
        if not m["gate_based"] or m["err_2q"] is None or m["qubits"] is None:
            continue
        spec = "design spec" in (m.get("err_2q_note") or "")
        pts.append(dict(name=m["name"], q=m["qubits"], e=m["err_2q"],
                        mod=m["modality"], spec=spec))
    return pts


# ------------------------------------------------------------- landscape --

def fig_landscape():
    pts = scatter_points()
    # hand-tuned label offsets (points); keyed by machine name
    off = {
        "IBM Heron r2": (8, -3), "Google Willow": (-8, 6),
        "USTC Zuchongzhi 3.0": (8, 2), "Rigetti Ankaa-3": (-8, 7),
        "Quantinuum H2": (8, -3), "Quantinuum Helios": (8, -3),
        "IonQ Forte": (8, -3), "IonQ Tempo": (8, 4),
        "QuEra-Harvard logical processor": (-8, 7),
    }
    short = {"USTC Zuchongzhi 3.0": "Zuchongzhi 3",
             "QuEra-Harvard logical processor": "QuEra–Harvard (phys. CZ)",
             "IonQ Tempo": "Tempo (spec)"}
    for mode in ("light", "dark"):
        ink = INK[mode]
        fig, ax = new_fig(mode, (7.0, 4.4))
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlim(25, 700)
        ax.set_ylim(4e-4, 2.5e-2)
        ax.axhspan(1e-2, 2.5e-2, color=ink["grid"], alpha=0.55, zorder=0)
        ax.text(600, 1.35e-2, "above surface-code threshold (~1%)",
                ha="right", color=ink["muted"], fontsize=8, style="italic")
        for p in pts:
            c = color(mode, p["mod"])
            face = SURFACE[mode] if p["spec"] else c
            ax.scatter(p["q"], p["e"], s=64, facecolors=face, edgecolors=c,
                       linewidths=1.6, zorder=3)
            dx, dy = off.get(p["name"], (8, -3))
            ax.annotate(short.get(p["name"], p["name"]), (p["q"], p["e"]),
                        xytext=(dx, dy), textcoords="offset points",
                        ha="left" if dx > 0 else "right",
                        color=ink["secondary"], fontsize=8.5)
        ax.annotate("toward fault tolerance", xy=(430, 5.6e-4),
                    xytext=(120, 5.6e-4), color=ink["muted"], fontsize=8.5,
                    arrowprops=dict(arrowstyle="->", color=ink["muted"], lw=0.9))
        ax.set_xticks([30, 50, 100, 200, 400], ["30", "50", "100", "200", "400"])
        ax.set_yticks([1e-3, 1e-2], ["0.1%", "1%"])
        ax.xaxis.set_minor_formatter(NullFormatter())
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_xlabel("physical qubits (log)")
        ax.set_ylabel("two-qubit gate error (log, lower is better)")
        ax.set_title("The landscape: every machine is one point — size × quality")
        legend(ax, mode, {p["mod"] for p in pts}, loc="lower left")
        save(fig, "fig-landscape", mode)


# -------------------------------------------------------------- timeline --

def fig_timeline():
    hist = DATA["history"]
    # label offsets: (dx, dy, ha); x-jitter separates coincident points only
    off = {
        "Sycamore": (0, 8, "center"), "Zuchongzhi 2": (0, -14, "center"),
        "IBM Eagle": (0, 8, "center"), "H1": (0, -14, "center"),
        "Aquila": (0, -14, "center"), "IBM Osprey": (0, 8, "center"),
        "Forte": (0, -14, "center"), "IBM Condor": (-4, 9, "right"),
        "Atom gen-2": (6, -12, "left"), "H2": (0, -14, "center"),
        "Willow": (-8, -3, "right"), "Heron r2": (0, 9, "center"),
        "Helios": (0, -14, "center"), "Zuchongzhi 3": (8, -3, "left"),
        "Nighthawk": (-2, 9, "center"), "QuEra logical": (0, 9, "center"),
    }
    jit = {"IBM Condor": -0.07, "Atom gen-2": 0.07,
           "Helios": -0.08, "Zuchongzhi 3": 0.08}
    for mode in ("light", "dark"):
        ink = INK[mode]
        fig, ax = new_fig(mode, (7.0, 4.0))
        ax.set_yscale("log")
        ax.set_ylim(12, 3200)
        ax.set_xlim(2018.4, 2026.8)
        for h in hist:
            c = color(mode, h["modality"])
            x = h["year"] + jit.get(h["label"], 0.0)
            ax.scatter(x, h["qubits"], s=56, color=c, zorder=3,
                       edgecolors=SURFACE[mode], linewidths=1.2)
            dx, dy, ha = off.get(h["label"], (0, 8, "center"))
            ax.annotate(h["label"], (x, h["qubits"]),
                        xytext=(dx, dy), textcoords="offset points",
                        ha=ha, color=ink["secondary"], fontsize=8)
        ax.set_yticks([16, 64, 256, 1024], ["16", "64", "256", "1024"])
        ax.yaxis.set_minor_formatter(NullFormatter())
        ax.set_xticks(range(2019, 2027))
        ax.set_xlabel("year")
        ax.set_ylabel("physical qubits (log)")
        ax.set_title("Flagships by year — after Condor, the leaders traded count for quality")
        legend(ax, mode, {h["modality"] for h in hist}, loc="upper left")
        save(fig, "fig-timeline", mode)


# --------------------------------------------------------------- logical --

def fig_logical():
    ms = DATA["logical_milestones"]
    off = {
        "Harvard-QuEra, 280 atoms": (0, 8, "center"),
        "Microsoft+Quantinuum (800x)": (0, -14, "center"),
        "Microsoft+Quantinuum, H2": (-9, -3, "right"),
        "Microsoft+Atom, entangled": (9, 2, "left"),
        "Google d=7 below threshold": (9, -3, "left"),
        "Helios launch demo (vendor)": (0, -14, "center"),
        "QuEra [[16,6,4]] codes": (-9, 2, "right"),
    }
    for mode in ("light", "dark"):
        ink = INK[mode]
        fig, ax = new_fig(mode, (7.0, 3.8))
        # running-max staircase in muted ink, under the points
        pts = sorted(ms, key=lambda m: m["date"])
        xs, ys, best = [], [], 0
        for p in pts:
            xs += [p["date"]]
            best = max(best, p["logical"])
            ys += [best]
        ax.step(xs, ys, where="post", color=ink["muted"], linewidth=1.2,
                alpha=0.7, zorder=2)
        for p in pts:
            c = color(mode, p["modality"])
            ax.scatter(p["date"], p["logical"], s=56, color=c, zorder=3,
                       edgecolors=SURFACE[mode], linewidths=1.2)
            dx, dy, ha = off.get(p["label"], (0, 8, "center"))
            ax.annotate(p["label"], (p["date"], p["logical"]),
                        xytext=(dx, dy), textcoords="offset points",
                        ha=ha, color=ink["secondary"], fontsize=8)
        ax.set_xlim(2023.6, 2026.5)
        ax.set_ylim(-6, 112)
        ax.set_xticks([2024, 2025, 2026])
        ax.set_xlabel("year")
        ax.set_ylabel("logical qubits demonstrated")
        ax.set_title("The number that matters now — logical qubits, by demonstration")
        legend(ax, mode, {p["modality"] for p in ms}, loc="upper left")
        save(fig, "fig-logical", mode)


# ----------------------------------------------------------------- depth --

def fig_depth():
    pts = sorted(scatter_points(), key=lambda p: 1 / p["e"])
    short = {"USTC Zuchongzhi 3.0": "Zuchongzhi 3",
             "QuEra-Harvard logical processor": "QuEra–Harvard (phys. CZ)",
             "IonQ Tempo": "IonQ Tempo (spec)"}
    for mode in ("light", "dark"):
        ink = INK[mode]
        fig, ax = new_fig(mode, (7.0, 3.8))
        ax.grid(True, axis="x", color=INK[mode]["grid"], linewidth=0.6)
        ax.grid(False, axis="y")
        for i, p in enumerate(pts):
            depth = 1 / p["e"]
            c = color(mode, p["mod"])
            fill = "none" if p["spec"] else c
            ax.barh(i, depth, height=0.62, color=fill, edgecolor=c,
                    linewidth=1.4, zorder=3)
            ax.text(depth + 18, i, f"{depth:,.0f}", va="center",
                    color=ink["secondary"], fontsize=8.5)
        ax.set_yticks(range(len(pts)),
                      [short.get(p["name"], p["name"]) for p in pts],
                      fontsize=8.5)
        ax.set_xlim(0, 1480)
        ax.set_xlabel("expected two-qubit gates before the first error  (= 1 / error)")
        ax.set_title("The depth budget — how deep a circuit each machine can afford")
        legend(ax, mode, {p["mod"] for p in pts}, loc="lower right")
        save(fig, "fig-depth", mode)


# ----------------------------------------------------------------- nines --

def fig_nines():
    import numpy as np
    ms = np.logspace(0, 5, 300)
    errs = [(1e-2, "99%"), (5e-3, "99.5%"), (1e-3, "99.9%"), (1e-4, "99.99%")]
    for mode in ("light", "dark"):
        ink = INK[mode]
        fig, ax = new_fig(mode, (7.0, 3.4))
        ax.set_xscale("log")
        stagger = [(-6, 10), (8, -16), (0, 10), (0, 10)]
        for (e, lab), c, (dx, dy) in zip(errs, ORDINAL[mode], stagger):
            p = (1 - e) ** ms
            ax.plot(ms, p, color=c, linewidth=2.0, zorder=3)
            m_half = np.log(0.5) / np.log(1 - e)
            ax.annotate(lab, (m_half, 0.5), xytext=(dx, dy),
                        textcoords="offset points", ha="center",
                        color=ink["secondary"], fontsize=8.5)
        ax.axhline(0.5, color=ink["muted"], linewidth=0.9, linestyle=":",
                   alpha=0.8)
        ax.text(1.3, 0.53, "coin-flip line", color=ink["muted"], fontsize=8)
        ax.set_xlim(1, 1e5)
        ax.set_ylim(0, 1.04)
        ax.set_xlabel("two-qubit gates in the circuit (log)")
        ax.set_ylabel("P(zero errors) = (1 − ε)^m")
        ax.set_title("Why the next nine is worth more than the next hundred qubits")
        save(fig, "fig-nines", mode)


# -------------------------------------------------------------- transmon --

def fig_transmon():
    import numpy as np
    phi = np.linspace(-1.35 * np.pi, 1.35 * np.pi, 400)
    ucos = -np.cos(phi)
    uharm = -1 + phi ** 2 / 2
    levels = [-0.85, -0.58, -0.36]          # anharmonic: 0.27, 0.22
    ghosts = [-0.85, -0.58, -0.31]          # harmonic:   0.27, 0.27
    names = ["|0⟩", "|1⟩", "|2⟩"]
    for mode in ("light", "dark"):
        ink = INK[mode]
        blue = SERIES[mode][0]
        fig, ax = new_fig(mode, (7.0, 3.9))
        ax.plot(phi, ucos, color=blue, linewidth=2.0, zorder=3)
        ax.plot(phi, uharm, color=ink["muted"], linewidth=1.4,
                linestyle="--", alpha=0.85, zorder=2)
        for e, g, nm in zip(levels, ghosts, names):
            half = np.arccos(min(1.0, -e))
            ax.plot([-half, half], [e, e], color=ink["primary"],
                    linewidth=1.6, zorder=4)
            ax.text(half + 0.12, e, nm, va="center",
                    color=ink["primary"], fontsize=10)
            hhalf = np.sqrt(2 * (g + 1))
            ax.plot([-hhalf, hhalf], [g, g], color=ink["muted"],
                    linewidth=1.1, linestyle="--", alpha=0.85, zorder=2)
        arr = dict(arrowstyle="<->", color=ink["secondary"], lw=1.1)
        ax.annotate("", (-0.62, levels[0]), (-0.62, levels[1]),
                    arrowprops=arr)
        ax.text(-0.74, -0.715, "ω₀₁", ha="right",
                color=ink["secondary"], fontsize=9)
        ax.annotate("", (-1.02, levels[1]), (-1.02, levels[2]),
                    arrowprops=arr)
        ax.text(-1.14, -0.475, "ω₁₂", ha="right",
                color=ink["secondary"], fontsize=9)
        ax.text(0, 0.32, "harmonic oscillator: equal steps,\nno way to "
                "address one transition", ha="center",
                color=ink["muted"], fontsize=8.5, style="italic")
        ax.text(0, -1.22, "Josephson cosine well: ω₁₂ < ω₀₁ — drive ω₀₁ "
                "and the rest of the ladder stays dark",
                ha="center", color=ink["secondary"], fontsize=8.5)
        ax.set_xlim(-4.6, 4.6)
        ax.set_ylim(-1.38, 0.62)
        ax.set_xticks([])
        ax.set_yticks([])
        ax.grid(False)
        ax.set_xlabel("superconducting phase φ")
        ax.set_ylabel("energy  (units of $E_J$)")
        ax.set_title("The transmon: an oscillator with unequal steps — "
                     "that inequality IS the qubit")
        save(fig, "fig-transmon", mode)


# -------------------------------------------------------------- lattices --

def fig_lattices():
    import numpy as np

    def hex_edges():
        centers = [(0.0, 0.0), (np.sqrt(3), 0.0),
                   (np.sqrt(3) / 2, 1.5)]
        edges, seen = [], set()
        for cx, cy in centers:
            vs = [(cx + np.cos(a), cy + np.sin(a))
                  for a in np.deg2rad([30, 90, 150, 210, 270, 330])]
            for i in range(6):
                a, b = vs[i], vs[(i + 1) % 6]
                key = tuple(sorted((tuple(np.round(a, 3)),
                                    tuple(np.round(b, 3)))))
                if key not in seen:
                    seen.add(key)
                    edges.append((a, b))
        return edges

    for mode in ("light", "dark"):
        ink = INK[mode]
        blue = SERIES[mode][0]
        fig, axes = plt.subplots(1, 2, figsize=(7.0, 3.3))
        fig.patch.set_alpha(0.0)
        for ax in axes:
            ax.set_facecolor("none")
            ax.set_aspect("equal")
            ax.axis("off")

        # left: heavy-hex — qubits on corners AND edge midpoints
        ax = axes[0]
        corners, mids = set(), []
        for a, b in hex_edges():
            m = ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
            ax.plot([a[0], b[0]], [a[1], b[1]], color=ink["axis"],
                    linewidth=1.2, zorder=1)
            corners.add(tuple(np.round(a, 3)))
            corners.add(tuple(np.round(b, 3)))
            mids.append(m)
        cs = np.array(sorted(corners))
        ms = np.array(mids)
        ax.scatter(cs[:, 0], cs[:, 1], s=52, color=blue, zorder=3,
                   edgecolors=SURFACE[mode], linewidths=1.0)
        ax.scatter(ms[:, 0], ms[:, 1], s=52, color=blue, zorder=3,
                   edgecolors=SURFACE[mode], linewidths=1.0)
        ax.text(0.5, -0.06, "heavy-hex (IBM Heron) — degree ≤ 3",
                transform=ax.transAxes, ha="center",
                color=ink["secondary"], fontsize=9.5)

        # right: square lattice with a coupler on every edge
        ax = axes[1]
        n, mgap = 4, 5
        for i in range(mgap):
            for j in range(n):
                if i < mgap - 1:
                    ax.plot([i, i + 1], [j, j], color=ink["axis"],
                            linewidth=1.2, zorder=1)
                if j < n - 1:
                    ax.plot([i, i], [j, j + 1], color=ink["axis"],
                            linewidth=1.2, zorder=1)
        xs, ys = np.meshgrid(range(mgap), range(n))
        ax.scatter(xs.ravel(), ys.ravel(), s=52, color=blue, zorder=3,
                   edgecolors=SURFACE[mode], linewidths=1.0)
        ax.text(0.5, -0.06, "square (Willow, Zuchongzhi 3, Nighthawk) — degree 4",
                transform=ax.transAxes, ha="center",
                color=ink["secondary"], fontsize=9.5)

        fig.suptitle("Two answers to frequency crowding: fewer neighbors, "
                     "or tunable everything", color=ink["secondary"],
                     fontsize=10, y=0.98)
        save(fig, "fig-lattices", mode)


# ------------------------------------------------------------------ ions --

def fig_ions():
    import numpy as np
    for mode in ("light", "dark"):
        ink = INK[mode]
        aqua = SERIES[mode][1]
        fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4),
                                 gridspec_kw={"width_ratios": [1, 1.35]})
        fig.patch.set_alpha(0.0)
        for ax in axes:
            ax.set_facecolor("none")
            ax.axis("off")

        # left: hyperfine clock qubit levels
        ax = axes[0]
        ax.set_xlim(0, 10)
        ax.set_ylim(0, 10)
        # ground manifold
        ax.plot([1.5, 5.0], [1.6, 1.6], color=ink["primary"], lw=1.8)
        ax.plot([1.5, 5.0], [3.4, 3.4], color=ink["primary"], lw=1.8)
        ax.text(5.3, 1.5, "|0⟩  F=0", color=ink["primary"], fontsize=9)
        ax.text(5.3, 3.3, "|1⟩  F=1", color=ink["primary"], fontsize=9)
        ax.annotate("", (1.9, 3.4), (1.9, 1.6),
                    arrowprops=dict(arrowstyle="<->", color=ink["secondary"],
                                    lw=1.0))
        ax.text(2.2, 2.4, "12.6 GHz\n(hyperfine)", color=ink["secondary"],
                fontsize=7.5, va="center")
        # excited manifold + Raman
        ax.plot([2.2, 4.4], [8.6, 8.6], color=ink["muted"], lw=1.4)
        ax.text(4.7, 8.5, "²P₁⁄₂", color=ink["muted"], fontsize=9)
        ax.plot([3.0, 3.0], [1.6, 8.0], color=aqua, lw=1.6, zorder=2)
        ax.plot([3.6, 3.6], [8.0, 3.4], color=aqua, lw=1.6, zorder=2)
        ax.plot([2.6, 4.0], [8.0, 8.0], color=ink["muted"], lw=1.0,
                linestyle=":")
        ax.text(3.3, 9.3, "two Raman beams,\ndetuned from ²P₁⁄₂",
                ha="center", color=ink["secondary"], fontsize=7.5)
        ax.text(3.25, 0.3, "clock states: first-order\nB-field insensitive",
                ha="center", color=ink["muted"], fontsize=7.5,
                style="italic")
        ax.set_title("the qubit: ¹⁷¹Yb⁺ / ¹³⁷Ba⁺ hyperfine",
                     color=ink["secondary"], fontsize=9.5)

        # right: QCCD shuttling vs static chain
        ax = axes[1]
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 10)
        # QCCD rail (top)
        ax.add_patch(plt.Rectangle((0.5, 6.4), 13.0, 1.6, fill=False,
                                   edgecolor=ink["axis"], lw=1.2))
        for x0, w, lab in [(0.5, 4.0, "storage"), (4.5, 3.5, "gate zone"),
                           (8.0, 3.0, "junction"), (11.0, 2.5, "storage")]:
            ax.plot([x0 + w, x0 + w], [6.4, 8.0], color=ink["axis"], lw=0.8,
                    linestyle=":")
            ax.text(x0 + w / 2, 8.4, lab, ha="center",
                    color=ink["muted"], fontsize=7.5)
        for x in (1.3, 2.2, 3.1, 11.8, 12.7):
            ax.scatter(x, 7.2, s=42, color=aqua, zorder=3,
                       edgecolors=SURFACE[mode], linewidths=1.0)
        for x in (5.8, 6.6):
            ax.scatter(x, 7.2, s=42, color=aqua, zorder=3,
                       edgecolors=SURFACE[mode], linewidths=1.0)
        ax.annotate("", (5.4, 6.0), (2.6, 6.0),
                    arrowprops=dict(arrowstyle="->", color=ink["secondary"],
                                    lw=1.0))
        ax.text(4.0, 5.4, "shuttle any pair together → all-to-all",
                color=ink["secondary"], fontsize=7.5)
        ax.text(0.5, 9.4, "QCCD (Quantinuum): ions move",
                color=ink["secondary"], fontsize=8.5)

        # static chain (bottom)
        for i, x in enumerate(np.linspace(2.5, 11.5, 9)):
            ax.scatter(x, 1.8, s=42, color=aqua, zorder=3,
                       edgecolors=SURFACE[mode], linewidths=1.0)
        for x in (4.75, 9.25):
            ax.annotate("", (x, 2.0), (x, 3.6),
                        arrowprops=dict(arrowstyle="->", color=ink["muted"],
                                        lw=1.4))
        ax.text(7.0, 3.9, "steered beam pair", ha="center",
                color=ink["muted"], fontsize=7.5)
        ax.text(0.5, 0.3, "static chain (IonQ): beams move",
                color=ink["secondary"], fontsize=8.5)
        ax.set_title("the architecture: transport vs addressing",
                     color=ink["secondary"], fontsize=9.5)

        fig.suptitle("Trapped ions: perfect identical qubits — the "
                     "engineering is in who talks to whom",
                     color=ink["secondary"], fontsize=10, y=1.04)
        save(fig, "fig-ions", mode)


# -------------------------------------------------------------- tweezers --

def fig_tweezers():
    import numpy as np
    for mode in ("light", "dark"):
        ink = INK[mode]
        yellow = SERIES[mode][2]
        fig, axes = plt.subplots(1, 2, figsize=(7.2, 3.4))
        fig.patch.set_alpha(0.0)
        for ax in axes:
            ax.set_facecolor("none")
            ax.axis("off")
            ax.set_xlim(0, 10)
            ax.set_ylim(0, 10)

        # left: Rydberg blockade level picture
        ax = axes[0]
        lv = dict(color=ink["primary"], lw=1.8)
        ax.plot([1.0, 4.0], [1.2, 1.2], **lv)
        ax.text(4.3, 1.1, "|gg⟩", color=ink["primary"], fontsize=9)
        ax.plot([1.0, 4.0], [5.0, 5.0], **lv)
        ax.text(4.3, 4.9, "|gr⟩, |rg⟩", color=ink["primary"], fontsize=9)
        ax.plot([1.0, 4.0], [8.8, 8.8], color=ink["muted"], lw=1.4,
                linestyle="--")
        ax.plot([1.0, 4.0], [7.6, 7.6], **lv)
        ax.annotate("", (2.0, 8.75), (2.0, 7.7),
                    arrowprops=dict(arrowstyle="<->", color=ink["secondary"],
                                    lw=1.0))
        ax.text(2.3, 8.15, "blockade shift V", color=ink["secondary"],
                fontsize=7.5)
        ax.text(4.3, 7.5, "|rr⟩ pushed away", color=ink["primary"],
                fontsize=9)
        ax.annotate("", (1.6, 4.9), (1.6, 1.3),
                    arrowprops=dict(arrowstyle="->", color=yellow, lw=1.6))
        ax.annotate("", (3.4, 8.7), (3.4, 5.1),
                    arrowprops=dict(arrowstyle="->", color=yellow, lw=1.6,
                                    linestyle=(0, (4, 3))))
        ax.text(3.7, 6.3, "second excitation\nblocked", color=ink["muted"],
                fontsize=7.5, style="italic")
        ax.text(2.5, 0.15, "within ~5 µm, only ONE atom can reach the\n"
                "Rydberg state — that conditionality is the CZ gate",
                ha="center", color=ink["secondary"], fontsize=7.5)
        ax.set_title("the gate: Rydberg blockade",
                     color=ink["secondary"], fontsize=9.5)

        # right: movable tweezers, zoned layout
        ax = axes[1]
        for x0, w, lab in [(0.3, 4.2, "storage zone"),
                           (5.0, 2.8, "entangling\nzone"),
                           (8.2, 1.6, "readout")]:
            ax.add_patch(plt.Rectangle((x0, 2.2), w, 6.0, fill=False,
                                       edgecolor=ink["axis"], lw=1.0,
                                       linestyle=":"))
            ax.text(x0 + w / 2, 8.7, lab, ha="center",
                    color=ink["muted"], fontsize=7.5)
        rng = np.random.default_rng(4)
        for x, y in zip(rng.uniform(0.7, 4.1, 14),
                        rng.uniform(2.7, 7.7, 14)):
            ax.scatter(x, y, s=40, color=yellow, zorder=3,
                       edgecolors=SURFACE[mode], linewidths=1.0)
        for y in (4.0, 6.0):
            ax.scatter(6.0, y, s=40, color=yellow, zorder=3,
                       edgecolors=SURFACE[mode], linewidths=1.0)
            ax.scatter(6.8, y, s=40, color=yellow, zorder=3,
                       edgecolors=SURFACE[mode], linewidths=1.0)
        ax.scatter(9.0, 5.0, s=40, color=yellow, zorder=3,
                   edgecolors=SURFACE[mode], linewidths=1.0)
        ax.annotate("", (5.8, 4.05), (3.4, 3.4),
                    arrowprops=dict(arrowstyle="->", color=ink["secondary"],
                                    lw=1.1))
        ax.annotate("", (8.9, 5.0), (7.0, 6.0),
                    arrowprops=dict(arrowstyle="->", color=ink["secondary"],
                                    lw=1.1))
        ax.text(5.0, 1.2, "optical tweezers MOVE atoms between zones:\n"
                "connectivity is a compiler decision, not a chip layout",
                ha="center", color=ink["secondary"], fontsize=7.5)
        ax.set_title("the architecture: atoms in motion",
                     color=ink["secondary"], fontsize=9.5)

        fig.suptitle("Neutral atoms: identical qubits, reconfigurable "
                     "wiring — the platform logical qubits like best",
                     color=ink["secondary"], fontsize=10, y=1.04)
        save(fig, "fig-tweezers", mode)


# ------------------------------------------------------------------- gbs --

def fig_gbs():
    import numpy as np
    for mode in ("light", "dark"):
        ink = INK[mode]
        green = SERIES[mode][3]
        fig, ax = new_fig(mode, (7.0, 3.2))
        ax.axis("off")
        ax.set_xlim(0, 14)
        ax.set_ylim(0, 9.0)
        n = 6
        ys = np.linspace(1.2, 6.8, n)
        for y in ys:
            ax.plot([1.6, 11.6], [y, y], color=ink["axis"], lw=1.1,
                    zorder=1)
            ax.scatter(1.2, y, s=60, marker="s", color=green, zorder=3,
                       edgecolors=SURFACE[mode], linewidths=1.0)
        for li, x in enumerate(np.linspace(4.2, 9.2, 6)):
            start = 0 if li % 2 == 0 else 1
            for a in range(start, n - 1, 2):
                ax.plot([x, x + 0.9], [ys[a], ys[a + 1]], color=ink["axis"],
                        lw=1.1, zorder=2)
                ax.plot([x, x + 0.9], [ys[a + 1], ys[a]], color=ink["axis"],
                        lw=1.1, zorder=2)
        clicks = [2, 0, 1, 0, 3, 1]
        for y, c in zip(ys, clicks):
            ax.scatter(12.2, y, s=64, marker=">", color=green, zorder=3,
                       edgecolors=SURFACE[mode], linewidths=1.0)
            ax.text(13.0, y, str(c), va="center", color=ink["primary"],
                    fontsize=9)
        ax.text(0.7, 8.1, "squeezed-light\nsources", color=ink["secondary"],
                fontsize=8)
        ax.text(7.2, 8.1, "interferometer (beamsplitter mesh)",
                ha="center", color=ink["secondary"], fontsize=8.5)
        ax.text(12.6, 8.1, "photon\ncounts", ha="center",
                color=ink["secondary"], fontsize=8)
        ax.text(7.0, 0.1, "output distribution ∝ |Hafnian|² — #P-hard to "
                "sample classically, and equally hard to VERIFY",
                ha="center", color=ink["muted"], fontsize=8, style="italic")
        ax.set_title("Gaussian boson sampling: the machine is the "
                     "distribution", color=ink["secondary"], fontsize=10)
        save(fig, "fig-gbs", mode)


# ----------------------------------------------------------------- table --

def fmt_err(e):
    if e is None:
        return "—"
    exp = 0
    while e < 1:
        e *= 10
        exp += 1
    sup = str(-exp).translate(str.maketrans("-0123456789", "⁻⁰¹²³⁴⁵⁶⁷⁸⁹"))
    return f"{e:.1f}×10{sup}"


def emit_table():
    """Write machines/_table.md — the master table included by index.md.

    Generated from data.yml so the table cannot drift from the data. A page
    is linked once its file exists; until then the cell reads "soon".
    """
    order = {m["id"]: (SLOT[m["modality"]], -(m["qubits"] or 0))
             for m in DATA["machines"]}
    rows = sorted(DATA["machines"], key=lambda m: order[m["id"]])
    lines = [
        "<!-- GENERATED by scripts/make_machine_figures.py from data.yml — do not edit. -->",
        "",
        "| Machine | Modality | Qubits | 2Q error | Status | Page |",
        "|---|---|---:|---:|---|---|",
    ]
    analog = False
    for m in rows:
        q = "—" if m["qubits"] is None else f"{m['qubits']:,}"
        if not m["gate_based"] and m["qubits"] is not None:
            q += "†"
            analog = True
        page = m["page"]
        cell = f"[{m['org']}]({page})" if (ROOT / OUT / page).exists() else "soon"
        lines.append(
            f"| {m['name']} | {LABEL[m['modality']]} | {q} | "
            f"{fmt_err(m['err_2q'])} | {m['status']} | {cell} |")
    lines.append("")
    if analog:
        lines.append("† analog device — atom, mode, or annealer counts are "
                     "**not** gate-model qubits and must not be compared to them.")
    lines.append("")
    lines.append(f"*Specs as of {DATA['as_of']}; every number is sourced in "
                 f"[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*")
    out = ROOT / OUT / "_table.md"
    out.write_text("\n".join(lines) + "\n")
    print(f"  {out.relative_to(ROOT)}")


if __name__ == "__main__":
    print("machines figures:")
    fig_landscape()
    fig_timeline()
    fig_logical()
    fig_depth()
    fig_nines()
    fig_transmon()
    fig_lattices()
    fig_ions()
    fig_tweezers()
    fig_gbs()
    emit_table()
