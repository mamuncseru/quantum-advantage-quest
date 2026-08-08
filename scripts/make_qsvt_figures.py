"""Figures for autopsy 10 — QSP / qubitization / QSVT.

Two light/dark pairs (fig-chebyshev is older and still current), computed by
`predecessors/09-qsvt/`:

  fig-polynomials  what QSP can reach, and the four algorithms as curves
  fig-degrees      every cost is a degree — and the two-factor test

Run from repo root:  .venv/bin/python scripts/make_qsvt_figures.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "predecessors/09-qsvt"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from polynomial_cost import (chebyshev_basis, degree_for_evolution,  # noqa: E402
                             degree_for_inverse, degree_for_sign,
                             low_rank_imitability, low_rank_matrix,
                             sparse_local_matrix)
from qsp_phases import chebyshev, qsp_response, solve_phases  # noqa: E402

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


def legend(ax, ink, fontsize=8, **kw):
    leg = ax.legend(frameon=False, fontsize=fontsize, **kw)
    for t in leg.get_texts():
        t.set_color(ink["secondary"])
    return leg


def save(fig, name, mode):
    suffix = "-dark" if mode == "dark" else ""
    out = ROOT / OUT / f"{name}{suffix}.svg"
    fig.savefig(out, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"  {out.relative_to(ROOT)}")


def _best_poly(target, xs, d, parity):
    B = chebyshev_basis(d, xs, parity)
    c, *_ = np.linalg.lstsq(B, target(xs), rcond=None)
    return B @ c


# --------------------------------------------------------- 1 · polynomials --

def fig_polynomials(mode):
    ink, cols = INK[mode], SERIES[mode]
    xs = np.linspace(-1, 1, 800)
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.4))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    for i, d in enumerate((3, 5, 7)):
        ax.plot(xs, qsp_response(np.zeros(d + 1), xs), color=cols[i], lw=1.7,
                label=f"phases all zero, d = {d}")
    rng = np.random.default_rng(2)
    for i in range(3):
        ph = rng.uniform(-1.2, 1.2, 8)
        ax.plot(xs, qsp_response(ph, xs), color=ink["muted"], lw=1.1,
                alpha=0.8, ls="--")
    ax.set_ylim(-1.5, 1.75)
    ax.set_xlabel("x  (an eigenvalue of the encoded matrix)")
    ax.set_ylabel("Re⟨0|U(x)|0⟩")
    ax.set_title("choosing phases is choosing a polynomial", loc="left")
    ax.text(0.5, 0.02, "dashed: three random phase choices, d = 7",
            transform=ax.transAxes, ha="center", fontsize=7.6,
            color=ink["muted"])
    legend(ax, ink, loc="upper center", ncol=1, fontsize=7.4)

    ax = axes[1]
    new_ax(ax, ink)
    delta = 0.2
    dom = np.concatenate([np.linspace(-1, -delta, 300),
                          np.linspace(delta, 1, 300)])
    ax.axvspan(-delta, delta, color=ink["muted"], alpha=0.16, lw=0)
    ax.plot(dom, np.sign(dom), color=ink["muted"], lw=1.4, ls=":",
            label="sign(x)")
    for i, d in enumerate((5, 11, 21)):
        ax.plot(dom, _best_poly(np.sign, dom, d, "odd"), color=cols[i],
                lw=1.6, label=f"degree {d}")
    ax.set_ylim(-1.4, 1.4)
    ax.set_xlabel("x")
    ax.set_title("search = approximating sign(x)", loc="left")
    ax.text(0.5, 0.06, "shaded: the gap δ", transform=ax.transAxes,
            ha="center", fontsize=8, color=ink["secondary"], style="italic")
    legend(ax, ink, loc="upper left")

    ax = axes[2]
    new_ax(ax, ink)
    t = 12.0
    ax.plot(xs, np.cos(t * xs), color=ink["muted"], lw=1.4, ls=":",
            label=f"cos({t:.0f}x)")
    for i, d in enumerate((8, 14, 20)):
        ax.plot(xs, _best_poly(lambda z: np.cos(t * z), xs, d, "even"),
                color=cols[i], lw=1.5, label=f"degree {d}")
    ax.set_ylim(-1.5, 1.5)
    ax.set_xlabel("x")
    ax.set_title("simulation = approximating cos(tx)", loc="left")
    legend(ax, ink, loc="lower center", ncol=2)

    fig.suptitle("One circuit shape, one knob: every algorithm in this "
                 "curriculum is a choice of polynomial",
                 color=ink["secondary"], fontsize=10.5, y=1.03)
    fig.tight_layout()
    save(fig, "fig-polynomials", mode)


# ------------------------------------------------------------ 2 · degrees ---

def fig_degrees(mode):
    ink, cols = INK[mode], SERIES[mode]
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.5))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    deltas = np.array([0.25, 0.125, 0.0625, 0.03125])
    ax.loglog(1 / deltas, [degree_for_sign(float(d)) for d in deltas], "-o",
              color=cols[0], lw=1.8, ms=5, label="search: sign(x), 1/δ = √N")
    kappas = np.array([4, 8, 16, 32])
    ax.loglog(kappas, [degree_for_inverse(int(k)) for k in kappas], "-s",
              color=cols[3], lw=1.8, ms=5, label="linear systems: 1/x, κ")
    ts = np.array([4, 8, 16, 32, 64, 128])
    ax.loglog(ts, [degree_for_evolution(int(t)) for t in ts], "-^",
              color=cols[2], lw=1.8, ms=5, label="simulation: cos(tx), t")
    ax.set_xlabel("the algorithm's own parameter  (√N, κ, or t)")
    ax.set_ylabel("polynomial degree")
    ax.set_title("three parameters, one axis", loc="left")
    legend(ax, ink, loc="lower right")

    ax = axes[1]
    new_ax(ax, ink)
    eps = [1e-1, 1e-2, 1e-3, 1e-4]
    xs = -np.log10(eps)
    ax.plot(xs, [degree_for_sign(0.125, e) for e in eps], "-o", color=cols[0],
            lw=1.8, ms=5, label="sign, δ = 1/8")
    ax.plot(xs, [degree_for_inverse(8, e) for e in eps], "-s", color=cols[3],
            lw=1.8, ms=5, label="1/x, κ = 8")
    ax.plot(xs, [degree_for_evolution(8, e) for e in eps], "-^", color=cols[2],
            lw=1.8, ms=5, label="cos(8x)")
    ax.set_xlabel("digits of precision demanded,  −log₁₀ ε")
    ax.set_ylabel("polynomial degree")
    ax.set_title("who pays for precision", loc="left")
    ax.text(0.28, 0.20, "simulation's degree barely moves:\n"
                        "additive in log(1/ε), not multiplicative",
            transform=ax.transAxes, fontsize=8.2, color=cols[2])
    legend(ax, ink, loc="upper left")

    ax = axes[2]
    new_ax(ax, ink)
    ranks = [1, 2, 4, 8, 16, 32, 64]
    for i, (name, maker) in enumerate((
            ("low-rank data (rank 8)", lambda: low_rank_matrix(128, 8)),
            ("low-rank data (rank 32)", lambda: low_rank_matrix(128, 32)),
            ("sparse Hamiltonian", lambda: sparse_local_matrix(128)))):
        A = maker()
        ax.semilogy(ranks, [max(low_rank_imitability(A, r), 1e-17)
                            for r in ranks], "-o", color=cols[i], lw=1.8,
                    ms=5, label=name)
    ax.set_ylim(1e-17, 3e3)
    ax.set_xlabel("rank of the classical sketch")
    ax.set_ylabel("error of the sketch")
    ax.set_title("can the encoding be imitated?", loc="left")
    legend(ax, ink, loc="upper right")

    fig.suptitle("Advantage = an encoding sampling cannot imitate × a degree "
                 "classical computers cannot afford",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-degrees", mode)


def main():
    for mode in ("light", "dark"):
        fig_polynomials(mode)
        fig_degrees(mode)


if __name__ == "__main__":
    print("Autopsy 10 — QSVT figures:")
    main()
