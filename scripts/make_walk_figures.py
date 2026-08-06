"""Figures for autopsies 07-08 — quantum walks.

Three light/dark pairs (fig-separation is older and still current), all
computed by `predecessors/07-quantum-walks/`:

  fig-transport  the mechanism: a ballistic front against a diffusive blob
  fig-disorder   the fragility: polynomial decay becomes exponential
  fig-szegedy    the ceiling: phase gap = Theta(sqrt(spectral gap))

Run from repo root:  .venv/bin/python scripts/make_walk_figures.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "predecessors/07-quantum-walks"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from szegedy import (barbell_chain, complete_chain, cycle_chain,  # noqa: E402
                     lazy, path_chain, phase_gap, spectral_gap, szegedy_walk)
from walk_transport import (classical_spread, clean_decay_exponent,  # noqa: E402
                            disordered_exit, fit_exponent, localisation_length,
                            quantum_spread)

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


# ---------------------------------------------------------- 1 · transport ---

def _packet(L, t):
    A = np.zeros((L, L))
    for j in range(L - 1):
        A[j, j + 1] = A[j + 1, j] = 1.0
    lam, V = np.linalg.eigh(A)
    start = np.zeros(L)
    start[L // 2] = 1.0
    psi = V @ (np.exp(-1j * lam * t) * (V.T @ start))
    return np.abs(psi) ** 2


def _classical(L, steps):
    P = np.zeros((L, L))
    for j in range(L):
        nb = [k for k in (j - 1, j + 1) if 0 <= k < L]
        for k in nb:
            P[j, k] = 1.0 / len(nb)
    d = np.zeros(L)
    d[L // 2] = 1.0
    for _ in range(steps):
        d = d @ P
    return d


def fig_transport(mode):
    ink, cols = INK[mode], SERIES[mode]
    L = 301
    xs = np.arange(L) - L // 2

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.7))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    for i, t in enumerate((20, 40, 60)):
        ax.plot(xs, _packet(L, t), color=cols[i], lw=1.5,
                label=f"quantum, t = {t}")
        ax.plot(xs, _classical(L, 2 * t), color=cols[i], lw=1.2, ls=":",
                alpha=0.85)
    ax.set_xlim(-140, 140)
    ax.set_xlabel("position")
    ax.set_ylabel("probability")
    ax.set_title("solid: quantum fronts.  dotted: classical blobs", loc="left")
    ax.text(0.02, 0.72, "the quantum walk puts its\nweight at the FRONT and\n"
                        "keeps moving; the classical\nwalk piles up where it "
                        "started",
            transform=ax.transAxes, fontsize=8.2, color=ink["secondary"])
    legend(ax, ink, loc="upper right")

    ax = axes[1]
    new_ax(ax, ink)
    times = np.array([2, 4, 8, 16, 32, 64], dtype=float)
    q = quantum_spread(401, times)
    c = classical_spread(401, times)
    ax.loglog(times, q, "-o", color=cols[0], lw=1.8, ms=5,
              label=f"quantum: slope {fit_exponent(times, q):.2f}")
    ax.loglog(times, c, "-s", color=cols[3], lw=1.8, ms=5,
              label=f"classical: slope {fit_exponent(times, c):.2f}")
    ax.set_xticks([2, 4, 8, 16, 32, 64])
    ax.set_xticklabels(["2", "4", "8", "16", "32", "64"])
    ax.minorticks_off()
    ax.set_xlabel("time t")
    ax.set_ylabel("⟨x²⟩")
    ax.set_title("ballistic (t²) against diffusive (t)", loc="left")
    legend(ax, ink, loc="upper left")

    fig.suptitle("The entire speedup is one exponent: the quantum walk "
                 "spreads as t, the classical walk as √t",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-transport", mode)


# ----------------------------------------------------------- 2 · disorder ---

def fig_disorder(mode):
    ink, cols = INK[mode], SERIES[mode]
    depths = [8, 16, 30, 50, 80, 120, 150]
    Ws = [0.0, 0.5, 1.0, 2.0, 3.0]

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.7))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    for i, W in enumerate(Ws):
        ps = [disordered_exit(d, W, trials=10, seed=3) for d in depths]
        ax.semilogy(depths, np.maximum(ps, 1e-8), "-o", ms=4, lw=1.7,
                    color=cols[i % 5],
                    label=("clean (W = 0)" if W == 0 else f"W = {W}"))
    ax.set_ylim(1e-6, 1.4)
    ax.set_xlabel("tree depth d   (graph has ~2^(d+2) vertices)")
    ax.set_ylabel("exit probability")
    ax.set_title(f"clean: p ~ d^-{clean_decay_exponent():.2f}.  "
                 f"disordered: exponential", loc="left")
    legend(ax, ink, loc="lower left", ncol=2)

    ax = axes[1]
    new_ax(ax, ink)
    strengths = np.array([0.5, 0.75, 1.0, 1.5, 2.0, 3.0, 4.0])
    xis = np.array([localisation_length(float(W), length=800, trials=4)
                    for W in strengths])
    ax.loglog(strengths, xis, "-o", color=cols[0], lw=1.8, ms=5,
              label="localisation length ξ")
    ax.loglog(strengths, (xis[2] - 2) / 2 * (strengths / 1.0) ** 0 * 0 +
              (xis - 2) / 2, "-s", color=cols[2], lw=1.8, ms=5,
              label="largest usable depth d")
    slope = np.polyfit(np.log(strengths), np.log(xis), 1)[0]
    ax.text(0.05, 0.12, f"fitted ξ ~ W^{slope:.2f}", transform=ax.transAxes,
            fontsize=9, color=ink["secondary"])
    ax.set_xticks([0.5, 1, 2, 4])
    ax.set_xticklabels(["0.5", "1", "2", "4"])
    ax.minorticks_off()
    ax.set_xlabel("disorder strength W")
    ax.set_ylabel("sites")
    ax.set_title("how much imperfection the graph can absorb", loc="left")
    legend(ax, ink, loc="upper right")

    fig.suptitle("The exponential advantage needs a chain that is clean over "
                 "its whole length — and the length is the problem size",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-disorder", mode)


# ------------------------------------------------------------ 3 · szegedy ---

def fig_szegedy(mode):
    ink, cols = INK[mode], SERIES[mode]
    chains = [("cycle", lazy(cycle_chain(n))) for n in (6, 8, 10, 14, 20)]
    chains += [("path", lazy(path_chain(n))) for n in (6, 10, 14)]
    chains += [("barbell", lazy(barbell_chain(n))) for n in (4, 5, 6, 8)]
    chains += [("complete", lazy(complete_chain(n))) for n in (6, 10)]

    kinds = {}
    for name, P in chains:
        kinds.setdefault(name, []).append(
            (spectral_gap(P), phase_gap(szegedy_walk(P))))

    fig, axes = plt.subplots(1, 2, figsize=(9.8, 3.7))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    for i, (name, pts) in enumerate(sorted(kinds.items())):
        d = np.array([p[0] for p in pts])
        g = np.array([p[1] for p in pts])
        ax.loglog(d, g, "o", ms=7, color=cols[i % 5], label=name)
    grid = np.logspace(-2.2, 0, 50)
    ax.loglog(grid, 2 * np.sqrt(2) * np.sqrt(grid), color=ink["muted"],
              lw=1.4, ls="--", label="2√2 · √δ")
    ax.set_xlabel("classical spectral gap δ")
    ax.set_ylabel("quantum phase gap")
    ax.set_title("one law, four families of chain", loc="left")
    legend(ax, ink, loc="upper left")

    ax = axes[1]
    new_ax(ax, ink)
    deltas = np.logspace(-6, -0.5, 60)
    ax.loglog(deltas, 1 / deltas, color=cols[3], lw=2.0, label="classical ~ 1/δ")
    ax.loglog(deltas, 1 / np.sqrt(deltas), color=cols[0], lw=2.0,
              label="quantum ~ 1/√δ")
    ax.fill_between(deltas, 1 / np.sqrt(deltas), 1 / deltas, color=cols[0],
                    alpha=0.12, lw=0)
    for name, pts in sorted(kinds.items()):
        d = np.array([p[0] for p in pts])
        ax.scatter(d, 1 / d, s=22, color=ink["muted"], zorder=5)
    ax.set_xlabel("classical spectral gap δ")
    ax.set_ylabel("hitting-time scale")
    ax.set_title("the shaded band is the entire prize: a square root",
                 loc="left")
    legend(ax, ink, loc="upper right")

    fig.suptitle("Szegedy's construction is systematic — and systematically "
                 "quadratic",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-szegedy", mode)


def main():
    for mode in ("light", "dark"):
        fig_transport(mode)
        fig_disorder(mode)
        fig_szegedy(mode)


if __name__ == "__main__":
    print("Autopsies 07–08 — quantum walk figures:")
    main()
