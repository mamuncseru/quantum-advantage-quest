"""Figures for autopsy 06 — Grover, amplitude amplification, the BBBV ceiling.

Three light/dark pairs (fig-rotation is older and still current), all
computed by `predecessors/06-grover/`:

  fig-souffle  more queries can be worse, and you must know when to stop
  fig-ceiling  the hybrid argument on a real state vector, and the wall it implies
  fig-cost     sequential depth, the parallelism asymmetry, and the crossover

Run from repo root:  .venv/bin/python scripts/make_grover_figures.py
"""

import sys
from math import log2, sqrt
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "predecessors/06-grover"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from grover_limits import (bbht_expected_queries, optimal_iterations,  # noqa: E402
                           overshoot_curve, query_magnitudes,
                           strategy_attention_classical,
                           success_probability, zalka_ceiling)
from grover_resources import (CLASSICAL_OP_S, LOGICAL_OP_S,  # noqa: E402
                              classical_time, crossover_N,
                              crossover_with_parallel_classical, iterations,
                              parallel_time, sequential_time, years)

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


# ------------------------------------------------------------ 1 · souffle ---

def fig_souffle(mode):
    ink, cols = INK[mode], SERIES[mode]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.7))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    ax.grid(False)
    N = 4096
    Ms = np.arange(1, 17)
    ts = np.arange(0, 90)
    grid = np.array([[success_probability(N, int(M), int(t)) for t in ts]
                     for M in Ms])
    im = ax.imshow(grid, aspect="auto", origin="lower", cmap="magma",
                   extent=[ts[0], ts[-1], Ms[0] - 0.5, Ms[-1] + 0.5],
                   vmin=0, vmax=1)
    ridge = [optimal_iterations(N, int(M)) for M in Ms]
    ax.plot(ridge, Ms, "o-", color="#ffffff", lw=1.6, ms=4,
            label="where you must stop")
    ax.set_xlabel("Grover iterations t")
    ax.set_ylabel("number of solutions M")
    ax.set_title(f"N = {N}: the stopping point moves with M", loc="left")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=ink["muted"], labelsize=8)
    leg = ax.legend(frameon=False, fontsize=8, loc="upper right")
    for t in leg.get_texts():
        t.set_color("#ffffff")

    ax = axes[1]
    new_ax(ax, ink)
    rng = np.random.default_rng(0)
    Ns = [256, 1024, 4096, 16384, 65536]
    known = [sqrt(N) for N in Ns]
    unknown = [bbht_expected_queries(N, 1, rng, trials=200) for N in Ns]
    ax.plot(Ns, known, "-o", color=cols[0], lw=1.8, ms=5,
            label="knowing M: √N queries")
    ax.plot(Ns, unknown, "-s", color=cols[1], lw=1.8, ms=5,
            label="not knowing M: BBHT, measured")
    ax.plot(Ns, [N / 2 for N in Ns], ls=":", color=ink["muted"], lw=1.4,
            label="classical: N/2")
    ax.set_xscale("log", base=2)
    ax.set_yscale("log")
    ax.set_xlabel("search space N")
    ax.set_ylabel("expected queries")
    ax.set_title("not knowing when to stop costs a constant", loc="left")
    legend(ax, ink, loc="upper left")

    fig.suptitle("Grover is a precisely timed rotation, not a “keep trying” "
                 "search — and the timing needs N and M in advance",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-souffle", mode)


# ------------------------------------------------------------ 2 · ceiling ---

def fig_ceiling(mode):
    ink, cols = INK[mode], SERIES[mode]
    fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.7))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    n = 10
    N = 1 << n
    T = optimal_iterations(N, 1)
    grover_prof = np.sort(query_magnitudes(n, T))[::-1]
    classical_prof = np.sort(strategy_attention_classical(N, T))[::-1]
    ax.plot(np.arange(N), classical_prof, color=cols[1], lw=1.8,
            label=f"a classical checker: T = {T} items, 1 unit each")
    ax.plot(np.arange(N), grover_prof, color=cols[0], lw=1.8,
            label="Grover: T/N everywhere")
    ax.axhline(T / N, color=cols[3], lw=1.3, ls="--",
               label=f"T/N = {T / N:.3f}")
    ax.set_yscale("symlog", linthresh=1e-3)
    ax.set_ylim(0, 2.0)
    ax.set_xlabel(f"items, sorted by attention (N = {N})")
    ax.set_ylabel("total query attention  qₓ")
    ax.set_title("both profiles sum to exactly T", loc="left")
    ax.text(0.30, 0.42,
            f"Σ qₓ = {grover_prof.sum():.2f} = T   (Grover)\n"
            f"Σ qₓ = {classical_prof.sum():.2f} = T   (classical)\n"
            "→ some item always gets ≤ T/N",
            transform=ax.transAxes, fontsize=8.2, color=ink["secondary"],
            fontfamily="monospace")
    legend(ax, ink, loc="upper right")

    ax = axes[1]
    new_ax(ax, ink)
    N = 1 << 14
    t_opt = optimal_iterations(N, 1)
    ts = np.arange(0, 2 * t_opt)
    # the ceiling is MONOTONE: an algorithm given T queries may use fewer,
    # so once t_opt is affordable the bound stays at its maximum.
    ceiling = np.maximum.accumulate(
        [success_probability(N, 1, int(t)) for t in ts])
    grover = [success_probability(N, 1, int(t)) for t in ts]
    ax.fill_between(ts, ceiling, 1.02, color=cols[3], alpha=0.16, lw=0)
    ax.plot(ts, ceiling, color=cols[3], lw=2.0, ls="--",
            label="the ceiling: no algorithm beats this")
    ax.plot(ts, grover, color=cols[0], lw=2.0, label="Grover, run to t")
    ax.text(0.06, 0.86, "no quantum algorithm\nreaches this region",
            transform=ax.transAxes, fontsize=9, color=cols[3])
    ax.annotate("the gap is the soufflé:\nGrover failing to stop",
                xy=(int(1.7 * t_opt), grover[int(1.7 * t_opt)]),
                xytext=(1.15 * t_opt, 0.44), fontsize=8.4,
                color=ink["secondary"],
                arrowprops=dict(arrowstyle="-|>", color=ink["muted"], lw=1.0))
    ax.set_ylim(0, 1.06)
    ax.set_xlabel("queries T")
    ax.set_ylabel("success probability")
    ax.set_title(f"N = {N}: Grover touches the bound at t = {t_opt}",
                 loc="left")
    legend(ax, ink, loc="lower right")

    fig.suptitle("BBBV was proved before the algorithm existed: the quadratic "
                 "is a ceiling, and Grover touches it",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-ceiling", mode)


# --------------------------------------------------------------- 3 · cost ---

def fig_cost(mode):
    ink, cols = INK[mode], SERIES[mode]
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 3.6))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    bits = np.arange(32, 145, 8)
    ax.plot(bits, [years(sequential_time(int(b), 1)) for b in bits],
            "-o", color=cols[0], lw=1.8, ms=4,
            label="1 logical op per iteration")
    ax.plot(bits, [years(sequential_time(int(b), 2 ** 13)) for b in bits],
            "-s", color=cols[3], lw=1.8, ms=4,
            label="2¹³ logical ops per iteration")
    ax.axhline(1.4e10, color=ink["muted"], lw=1.2, ls=":")
    ax.text(34, 3e10, "age of the universe", color=ink["muted"], fontsize=8.2,
            style="italic")
    ax.axhline(1, color=cols[2], lw=1.2, ls="--")
    ax.text(34, 1.6, "one year", color=cols[2], fontsize=8.2, style="italic")
    ax.set_yscale("log")
    ax.set_xlabel("key size, bits")
    ax.set_ylabel("wall-clock years (sequential)")
    ax.set_title("depth cannot be bought away", loc="left")
    legend(ax, ink, loc="lower right")

    ax = axes[1]
    new_ax(ax, ink)
    ks = np.logspace(0, 12, 40)
    ax.plot(ks, np.sqrt(ks), color=cols[0], lw=2.0, label="quantum: √k")
    ax.plot(ks, ks, color=cols[3], lw=2.0, label="classical: k")
    ax.fill_between(ks, np.sqrt(ks), ks, color=cols[3], alpha=0.12, lw=0)
    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xlabel("machines / cores bought, k")
    ax.set_ylabel("speedup")
    ax.set_title("every purchase favours classical", loc="left")
    legend(ax, ink, loc="upper left")

    ax = axes[2]
    new_ax(ax, ink)
    cores = [1, 10 ** 3, 10 ** 6, 10 ** 9]
    xs = np.arange(len(cores))
    vals = [log2(crossover_N() if c == 1
                 else crossover_with_parallel_classical(c)) for c in cores]
    ax.bar(xs, vals, width=0.6, color=cols[0], zorder=3)
    for x, v in zip(xs, vals):
        ax.text(x, v + 1.6, f"2^{v:.0f}", ha="center", fontsize=8.6,
                color=ink["secondary"])
    ax.set_xticks(xs)
    ax.set_xticklabels(["1 core", "10³", "10⁶", "10⁹"], fontsize=8.5)
    ax.set_ylim(0, max(vals) * 1.25)
    ax.set_xlabel("classical cores the other side owns")
    ax.set_ylabel("crossover N  (log₂)")
    ax.set_title("the crossover runs away", loc="left")

    fig.suptitle("Grover's cost is depth, and depth is the one resource "
                 "money cannot parallelise away",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-cost", mode)


def main():
    for mode in ("light", "dark"):
        fig_souffle(mode)
        fig_ceiling(mode)
        fig_cost(mode)


if __name__ == "__main__":
    print("Autopsy 06 — Grover figures:")
    main()
