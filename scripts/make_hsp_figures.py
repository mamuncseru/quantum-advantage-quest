"""Figures for autopsy 05 — the hidden subgroup problem and its graveyard.

Four light/dark pairs, every number computed by the modules in
`predecessors/05-hsp-graveyard/`:

  fig-continent  one quantum step, three algorithms — the abelian win
  fig-wall       S_n: the involution you get is the one you cannot see
  fig-dihedral   D_N: the label says one bit, the phase says the rest
  fig-baseline   what colour refinement was already doing to graph isomorphism

Run from repo root:  .venv/bin/python scripts/make_hsp_figures.py
"""

import sys
from math import factorial
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "predecessors/05-hsp-graveyard"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from abelian_hsp import (bv_instance, order_instance,  # noqa: E402
                         sample_distribution, simon_instance)
from gi_baseline import (color_refine, random_pair_stats,  # noqa: E402
                         rooks_graph, shrikhande_graph)
from nonabelian_wall import (Dihedral, dihedral_label_distribution,  # noqa: E402
                             dihedral_phase, fixed_point_free_type,
                             samples_needed, sieve_optimal_block,
                             total_variation, transposition_type)

INK = {
    "light": dict(primary="#0b0b0b", secondary="#52514e", muted="#898781",
                  grid="#e1e0d9", axis="#c3c2b7"),
    "dark": dict(primary="#ffffff", secondary="#c3c2b7", muted="#898781",
                 grid="#2c2c2a", axis="#383835"),
}
SERIES = {
    "light": ["#2a78d6", "#eda100", "#1baf7a", "#e34948", "#8a63d2"],
    "dark": ["#6da7ec", "#f0b429", "#199e70", "#e66767", "#a586ff"],
}


def new_ax(ax, ink):
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


def legend(ax, ink, **kw):
    leg = ax.legend(frameon=False, fontsize=8, **kw)
    for t in leg.get_texts():
        t.set_color(ink["secondary"])
    return leg


def save(fig, name, mode):
    suffix = "-dark" if mode == "dark" else ""
    out = ROOT / OUT / f"{name}{suffix}.svg"
    fig.savefig(out, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"  {out.relative_to(ROOT)}")


# ---------------------------------------------------------- 1 · continent ---

def fig_continent(mode):
    ink, cols = INK[mode], SERIES[mode]
    rng = np.random.default_rng(3)

    g_bv, f_bv, H_bv = bv_instance(4, (1, 0, 1, 1))
    g_si, f_si, H_si = simon_instance(4, (1, 1, 0, 1), rng)
    g_or, f_or, H_or, r = order_instance(16, 7, 15)

    panels = [
        (g_bv, f_bv, H_bv, "Bernstein–Vazirani",
         "G = ℤ₂⁴,  H = the hyperplane s·x = 0",
         "one nonzero label IS the secret"),
        (g_si, f_si, H_si, "Simon",
         "G = ℤ₂⁴,  H = {0, s}",
         "n−1 labels → solve over GF(2)"),
        (g_or, f_or, H_or, "Shor, order-finding",
         f"G = ℤ₁₆,  H = rℤ with r = {r}",
         "gcd of the labels → r"),
    ]

    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.5))
    fig.patch.set_alpha(0.0)
    for ax, (g, f, H, title, sub, post) in zip(axes, panels):
        new_ax(ax, ink)
        p = sample_distribution(f, g)
        ann = {g.encode(k) for k in g.annihilator(H)}
        colours = [cols[0] if i in ann else cols[3] for i in range(g.order)]
        ax.bar(np.arange(g.order), p, width=0.78, color=colours, zorder=3)
        ax.set_ylim(0, max(p) * 1.45)
        ax.set_xlabel("measured label")
        ax.set_title(title, loc="left")
        ax.text(0.02, 0.90, sub, transform=ax.transAxes, fontsize=8.4,
                color=ink["secondary"])
        ax.text(0.02, 0.78, f"support = H⊥, |H⊥| = {len(ann)}",
                transform=ax.transAxes, fontsize=8.2, color=ink["muted"],
                fontfamily="monospace")
        ax.text(0.5, -0.30, post, transform=ax.transAxes, ha="center",
                va="top", fontsize=9, color=cols[0], style="italic")
    axes[0].set_ylabel("probability")

    fig.suptitle("One quantum step, three algorithms: the samples always land "
                 "exactly on H⊥ — only the last line of classical work differs",
                 color=ink["secondary"], fontsize=10.5, y=1.03)
    fig.tight_layout()
    save(fig, "fig-continent", mode)


# --------------------------------------------------------------- 2 · wall ---

def fig_wall(mode):
    ink, cols = INK[mode], SERIES[mode]
    ns = list(range(4, 25, 2))
    tv_t = [total_variation(n, transposition_type(n)) for n in ns]
    tv_f = [total_variation(n, fixed_point_free_type(n)) for n in ns]

    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.8))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    ax.plot(ns, tv_t, "-o", color=cols[0], lw=1.8, ms=4.5,
            label="a transposition (visible)")
    ax.plot(ns, tv_f, "-s", color=cols[3], lw=1.8, ms=4.5,
            label="a perfect matching (the GI case)")
    ax.plot(ns, [2 / n for n in ns], ls=":", color=cols[0], lw=1.2,
            label="2/n reference")
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("total variation from “no hidden subgroup”")
    ax.set_title("how visible the hidden involution is", loc="left")
    legend(ax, ink, loc="lower left")

    ax = axes[1]
    new_ax(ax, ink)
    ax.plot(ns, [samples_needed(t) for t in tv_t], "-o", color=cols[0],
            lw=1.8, ms=4.5, label="a transposition")
    ax.plot(ns, [samples_needed(t) for t in tv_f], "-s", color=cols[3],
            lw=1.8, ms=4.5, label="a perfect matching")
    ax.axhline(1e12, color=ink["muted"], lw=1.0, ls=":")
    ax.text(12.6, 1.9e12, "a trillion copies", color=ink["muted"],
            fontsize=8.4, style="italic")
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("copies needed to notice, ≈ 1/TV²")
    ax.set_title("what that costs", loc="left")
    legend(ax, ink, loc="upper left")

    fig.suptitle("Weak Fourier sampling over Sₙ: the wall is not “non-abelian”"
                 " — it is this particular subgroup",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-wall", mode)


# ----------------------------------------------------------- 3 · dihedral ---

def fig_dihedral(mode):
    ink, cols = INK[mode], SERIES[mode]
    N = 8
    D = Dihedral(N)

    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.5),
                             gridspec_kw=dict(width_ratios=[1.25, 1, 1]))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    # every even d gives the identical distribution, and so does every odd d —
    # verified across all offsets by dihedral_label_drift, so two bars suffice.
    even = dihedral_label_distribution(D, 0)
    odd = dihedral_label_distribution(D, 1)
    names = sorted(even)
    xs = np.arange(len(names))
    ax.bar(xs - 0.19, [even[nm] for nm in names], width=0.36, color=cols[0],
           label="d even", zorder=3)
    ax.bar(xs + 0.19, [odd[nm] for nm in names], width=0.36, color=cols[1],
           label="d odd", zorder=3)
    ax.set_xticks(xs)
    ax.set_xticklabels(names, rotation=45, ha="right", fontsize=7.5)
    ax.set_ylim(0, 0.40)
    ax.set_ylabel("probability")
    ax.set_title("the label you measure", loc="left")
    ax.text(0.34, 0.95, "ρ labels (2-dim): identical for every d",
            transform=ax.transAxes, fontsize=8, color=ink["secondary"],
            va="top")
    ax.text(0.34, 0.85, "alt labels (1-dim): flip with the parity of d",
            transform=ax.transAxes, fontsize=8, color=cols[3], va="top")
    legend(ax, ink, loc="upper left", ncol=1)

    ax = axes[1]
    new_ax(ax, ink)
    ds = list(range(N))
    for i, k in enumerate((1, 2, 3)):
        meas = [dihedral_phase(D, d, k) % (2 * np.pi) / (2 * np.pi)
                for d in ds]
        ax.plot(ds, [(k * d / N) % 1.0 for d in ds], ls=":", lw=1.2,
                color=cols[i])
        ax.plot(ds, meas, "o", ms=5, color=cols[i], label=f"block ρ_{k}")
    ax.set_ylim(-0.08, 1.52)
    ax.set_xlabel("hidden reflection offset d")
    ax.set_ylabel("phase inside the block, in turns")
    ax.set_title("where the secret actually is", loc="left")
    ax.text(0.02, 0.80, "dots: measured    dotted: k·d/N mod 1",
            transform=ax.transAxes, fontsize=7.8, color=ink["muted"])
    legend(ax, ink, loc="upper center", ncol=3)

    ax = axes[2]
    new_ax(ax, ink)
    for i, n_bits in enumerate((32, 64, 128)):
        best, cost, curve = sieve_optimal_block(n_bits)
        ts = sorted(curve)
        ax.plot(ts, [curve[t] for t in ts], lw=1.7, color=cols[i],
                label=f"log₂N = {n_bits}")
        ax.scatter([best], [cost], s=48, color=cols[i], zorder=5,
                   edgecolor="none")
    ax.set_yscale("log")
    ax.set_xlim(0, 40)
    ax.set_ylim(1e2, 1e14)
    ax.set_xlabel("bits cleared per round")
    ax.set_ylabel("copies you must start with")
    ax.set_title("Kuperberg: the trade that gives √", loc="left")
    ax.text(0.03, 0.06, "dots: the optimum, at ≈ √(log N)",
            transform=ax.transAxes, ha="left", fontsize=7.8,
            color=ink["secondary"], style="italic")
    legend(ax, ink, loc="lower right")

    fig.suptitle("The dihedral group is barely non-abelian, and that is "
                 "exactly how much it costs",
                 color=ink["secondary"], fontsize=10.5, y=1.03)
    fig.tight_layout()
    save(fig, "fig-dihedral", mode)


# ----------------------------------------------------------- 4 · baseline ---

def _neighbourhood_layout(adj, v):
    """Positions for the graph induced on v's neighbours, component by
    component, so two triangles read as two triangles."""
    nb = list(np.flatnonzero(adj[v]))
    sub = adj[np.ix_(nb, nb)]
    n = len(nb)
    seen, comps = set(), []
    for i in range(n):
        if i in seen:
            continue
        stack, comp = [i], []
        seen.add(i)
        while stack:
            u = stack.pop()
            comp.append(u)
            for w in np.flatnonzero(sub[u]):
                if int(w) not in seen:
                    seen.add(int(w))
                    stack.append(int(w))
        comps.append(comp)
    pos = {}
    for ci, comp in enumerate(comps):
        cx = (ci - (len(comps) - 1) / 2) * 2.6
        for j, u in enumerate(comp):
            ang = 2 * np.pi * j / len(comp) + np.pi / 2
            pos[u] = (cx + np.cos(ang), np.sin(ang))
    return sub, pos


def fig_baseline(mode):
    ink, cols = INK[mode], SERIES[mode]
    rng = np.random.default_rng(11)
    ns = [8, 12, 16, 20, 30, 40]
    stats = [random_pair_stats(n, 40, rng) for n in ns]

    fig, axes = plt.subplots(1, 3, figsize=(10.4, 3.4),
                            gridspec_kw=dict(width_ratios=[1.2, 1, 1]))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    ax.plot(ns, [s[0] for s in stats], "-o", color=cols[0], lw=1.8, ms=5,
            label="non-isomorphic pairs separated")
    ax.plot(ns, [s[1] for s in stats], "-s", color=cols[2], lw=1.8, ms=5,
            label="graphs canonically labelled outright")
    ax.set_ylim(-0.05, 1.12)
    ax.set_xlabel("vertices n")
    ax.set_ylabel("fraction of random instances")
    ax.set_title("colour refinement, 1968", loc="left")
    legend(ax, ink, loc="lower right")

    for ax, (g, name, verdict) in zip(axes[1:], [
            (rooks_graph(), "4×4 rook's graph", "two disjoint triangles"),
            (shrikhande_graph(), "Shrikhande graph", "one 6-cycle")]):
        new_ax(ax, ink)
        ax.grid(False)
        ax.set_aspect("equal")
        sub, pos = _neighbourhood_layout(g, 0)
        for i in range(sub.shape[0]):
            for j in range(i + 1, sub.shape[0]):
                if sub[i, j]:
                    ax.plot([pos[i][0], pos[j][0]], [pos[i][1], pos[j][1]],
                            color=ink["muted"], lw=1.4, zorder=1)
        xs = [pos[i][0] for i in pos]
        ys = [pos[i][1] for i in pos]
        ax.scatter(xs, ys, s=110, color=cols[0], zorder=3, edgecolor="none")
        ax.set_xticks([])
        ax.set_yticks([])
        for side in ("left", "bottom"):
            ax.spines[side].set_visible(False)
        ax.set_xlim(-4.2, 4.2)
        ax.set_ylim(-1.9, 1.9)
        ax.set_title(name, loc="left")
        ax.text(0.5, -0.10, f"every neighbourhood: {verdict}",
                transform=ax.transAxes, ha="center", va="top", fontsize=8.6,
                color=ink["secondary"], style="italic")

    fig.suptitle("Both graphs are strongly regular (16, 6, 2, 2), so refinement"
                 " is blind — and one more invariant sees straight through",
                 color=ink["secondary"], fontsize=10.5, y=1.03)
    fig.tight_layout()
    save(fig, "fig-baseline", mode)


def main():
    for mode in ("light", "dark"):
        fig_continent(mode)
        fig_wall(mode)
        fig_dihedral(mode)
        fig_baseline(mode)


if __name__ == "__main__":
    print("Autopsy 05 — HSP figures:")
    main()
