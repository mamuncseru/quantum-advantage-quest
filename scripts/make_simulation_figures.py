"""Figures for autopsy 09 — Hamiltonian simulation.

Two light/dark pairs (fig-slopes is older and still current), computed by
`predecessors/08-hamiltonian-simulation/`:

  fig-wall       three regimes: area law, critical log, and the quench cliff
  fig-crossover  Trotter against qubitization, and the knob that decides it

Run from repo root:  .venv/bin/python scripts/make_simulation_figures.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "predecessors/08-hamiltonian-simulation"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from entanglement_wall import (ground_state_entropy,  # noqa: E402
                               ground_state_scaling, growth_rate, quench)
from simulation_cost import (best_trotter, crossover_epsilon,  # noqa: E402
                             long_range_profile, mean_looseness,
                             qubitization_cost, tfim_profile)

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


# --------------------------------------------------------------- 1 · wall ---

def fig_wall(mode):
    ink, cols = INK[mode], SERIES[mode]
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.5),
                             gridspec_kw=dict(width_ratios=[1.1, 1, 1]))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    times = np.array([0.0, 0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
    rows = quench(14, times)
    ss = [r[1] for r in rows]
    ax.plot(times, ss, "-o", color=cols[3], lw=1.9, ms=5,
            label=f"quench: S ≈ {growth_rate(14, times):.2f}·t")
    ns = np.array([6, 8, 10, 12, 14, 16])
    ax.plot(np.log2(ns), [ground_state_entropy(int(n), g=1.0) for n in ns],
            "-s", color=cols[1], lw=1.9, ms=5, label="critical ground state")
    ax.plot(np.log2(ns), [ground_state_entropy(int(n), g=2.0) for n in ns],
            "-^", color=cols[2], lw=1.9, ms=5, label="gapped ground state")
    ax.set_xlabel("time t   /   log₂ n  (ground states)")
    ax.set_ylabel("entanglement entropy (bits)")
    ax.set_title("three regimes, one axis", loc="left")
    legend(ax, ink, loc="upper left")

    ax = axes[1]
    new_ax(ax, ink)
    chis = [r[2] for r in rows]
    ax.semilogy(times, chis, "-o", color=cols[3], lw=1.9, ms=5,
                label="measured, n = 14")
    ax.semilogy(times, 2.0 ** np.array(ss), ls="--", color=ink["muted"],
                lw=1.4, label="2^S")
    ax.set_xlabel("time t")
    ax.set_ylabel("bond dimension for 99% of the weight")
    ax.set_title("what a tensor network must store", loc="left")
    legend(ax, ink, loc="upper left")

    ax = axes[2]
    new_ax(ax, ink)
    rate = growth_rate(14, times)
    ts = np.arange(0, 33)
    mem = 50 * (2.0 ** (rate * ts)) ** 2 * 32
    ax.semilogy(ts, mem, color=cols[3], lw=2.0)
    for label, size, colour in (("a laptop", 1.6e10, cols[0]),
                                ("a big cluster", 1e15, cols[2]),
                                ("every byte ever made", 1e23, cols[1])):
        ax.axhline(size, color=colour, lw=1.2, ls=":")
        ax.text(0.4, size * 2.2, label, color=colour, fontsize=8.2,
                style="italic")
    ax.set_ylim(1e2, 1e30)
    ax.set_xlabel("simulated time t")
    ax.set_ylabel("MPS memory, bytes (extrapolated)")
    ax.set_title("doubling the time squares the memory", loc="left")

    fig.suptitle("The classical wall is a wall for dynamics — and only for "
                 "dynamics",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-wall", mode)


# ---------------------------------------------------------- 2 · crossover ---

def fig_crossover(mode):
    ink, cols = INK[mode], SERIES[mode]
    L = mean_looseness()
    t = 10.0
    fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.7))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    eps = np.logspace(-1, -10, 40)
    profiles = [(tfim_profile(8), "nearest-neighbour Ising", cols[0]),
                (long_range_profile(8, g=1.0), "long-range, g = 1", cols[2]),
                (long_range_profile(8, g=0.01), "long-range, g = 0.01",
                 cols[1])]
    for prof, label, colour in profiles:
        ax.loglog(eps, [best_trotter(prof, t, e, L)[1] for e in eps],
                  color=colour, lw=1.9, label=f"Trotter · {label}")
        ax.loglog(eps, [qubitization_cost(prof, t, e) for e in eps],
                  color=colour, lw=1.4, ls="--")
    ax.set_xlim(1e-1, 1e-10)
    ax.set_xlabel("target error ε")
    ax.set_ylabel("term applications")
    ax.set_title("solid: best product formula.  dashed: qubitization",
                 loc="left")
    legend(ax, ink, loc="upper left")

    ax = axes[1]
    new_ax(ax, ink)
    gs = np.array([1.0, 0.5, 0.2, 0.1, 0.05, 0.02, 0.01])
    ratios, crossings = [], []
    for g in gs:
        prof = long_range_profile(8, g=float(g))
        ratios.append(prof["alpha"] / prof["comm"])
        x = crossover_epsilon(prof, t, L)
        crossings.append(x if x is not None else 1.0)
    ax.loglog(ratios, crossings, "-o", color=cols[0], lw=1.9, ms=6)
    for r, c, g in zip(ratios, crossings, gs):
        if g in (1.0, 0.1, 0.01):
            ax.annotate(f"g = {g}", xy=(r, c), xytext=(r * 0.42, c * 1.35),
                        fontsize=8.2, color=ink["secondary"])
    ax.set_xlabel("α / ‖[A,B]‖   (how much of H commutes with itself)")
    ax.set_ylabel("ε below which qubitization wins")
    ax.set_title("the knob that actually decides it", loc="left")
    ax.text(0.03, 0.08, "Trotter's window widens\nas the commuting block grows",
            transform=ax.transAxes, fontsize=8.4, color=ink["secondary"])

    fig.suptitle("Asymptotic optimality is not a verdict: α against the "
                 "commutator norm decides who is cheaper",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-crossover", mode)


def main():
    for mode in ("light", "dark"):
        fig_wall(mode)
        fig_crossover(mode)


if __name__ == "__main__":
    print("Autopsy 09 — Hamiltonian simulation figures:")
    main()
