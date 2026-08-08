"""Figures for autopsy 11 — HHL and Tang.

Two light/dark pairs (fig-dequantized is older and still current), computed
by `predecessors/10-hhl-tang/`:

  fig-tolls     the output toll, the kappa toll, and the matched comparison
  fig-boundary  where dequantisation works, and where it stops

Run from repo root:  .venv/bin/python scripts/make_hhl_figures.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "predecessors/10-hhl-tang"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from dequantize import (make_matrix, rows_needed_median,  # noqa: E402
                        solve_quality, stable_rank)
from hhl_tolls import (classical_cg_runtime, condition_number,  # noqa: E402
                       hhl_runtime, hhl_with_readout_runtime, readout_penalty,
                       samples_to_read_one_amplitude,
                       samples_to_read_the_whole_vector, sparse_spd)

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


# -------------------------------------------------------------- 1 · tolls ---

def fig_tolls(mode):
    ink, cols = INK[mode], SERIES[mode]
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.5))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    dims = np.logspace(2, 9, 30)
    ax.loglog(dims, [samples_to_read_one_amplitude(0.01)] * len(dims),
              color=cols[2], lw=2.0, label="one amplitude  (dimension-free)")
    ax.loglog(dims, [samples_to_read_the_whole_vector(int(d), 0.01)
                     for d in dims], color=cols[3], lw=2.0,
              label="the whole vector x")
    ax.set_xlabel("dimension")
    ax.set_ylabel("state preparations needed")
    ax.set_title("toll 3: the output is a state", loc="left")
    ax.text(0.05, 0.55, "the algorithm runs in polylog(dim)\n"
                        "and hands you an object that\ncosts dim to read",
            transform=ax.transAxes, fontsize=8.2, color=ink["secondary"])
    legend(ax, ink, loc="lower right")

    ax = axes[1]
    new_ax(ax, ink)
    dims = [16, 32, 64, 128, 256]
    ks = [condition_number(sparse_spd(d)) for d in dims]
    ax.loglog(dims, ks, "-o", color=cols[3], lw=1.9, ms=5,
              label="discrete Laplacian")
    ax.loglog(dims, [k * 0 + 0.05 * d ** 2 for k, d in zip(ks, dims)],
              ls="--", color=ink["muted"], lw=1.4, label="∝ dim²")
    ax.set_xticks(dims)
    ax.set_xticklabels([str(d) for d in dims])
    ax.minorticks_off()
    ax.set_xlabel("dimension")
    ax.set_ylabel("condition number κ")
    ax.set_title("toll 2: κ is not a constant", loc="left")
    legend(ax, ink, loc="upper left")

    ax = axes[2]
    new_ax(ax, ink)
    dims = np.logspace(2, 9, 30)
    kappa = 100
    ax.loglog(dims, [classical_cg_runtime(d, kappa, 1e-3) for d in dims],
              color=cols[2], lw=2.0, label="conjugate gradients → x")
    ax.loglog(dims, [hhl_runtime(d, kappa, 1e-3) for d in dims],
              color=cols[0], lw=2.0, ls="--",
              label="HHL → a state (the quoted claim)")
    ax.loglog(dims, [hhl_with_readout_runtime(d, kappa, 1e-3) for d in dims],
              color=cols[3], lw=2.0, label="HHL → x  (matched output)")
    ax.set_xlabel("dimension")
    ax.set_ylabel("cost")
    ax.set_title("the comparison, both ways", loc="left")
    legend(ax, ink, loc="upper left")

    fig.suptitle("HHL's polylog is the price of preparing a state — and the "
                 "state is not the answer",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-tolls", mode)


# ----------------------------------------------------------- 2 · boundary ---

def fig_boundary(mode):
    ink, cols = INK[mode], SERIES[mode]
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.5))
    fig.patch.set_alpha(0.0)

    m = n = 400
    ax = axes[0]
    new_ax(ax, ink)
    rs = [8, 16, 32, 64, 128]
    for i, rank in enumerate((5, 20, 80)):
        errs = [solve_quality(m, n, rank, rank, r, seed=3)[0] for r in rs]
        ax.semilogy(rs, errs, "-o", color=cols[i], lw=1.8, ms=5,
                    label=f"rank {rank}")
    ax.axhline(0.1, color=ink["muted"], lw=1.2, ls=":")
    ax.text(9, 0.115, "10% error", color=ink["muted"], fontsize=8.2,
            style="italic")
    ax.set_xlabel(f"rows sampled  (out of {m})")
    ax.set_ylabel("relative error of the solve")
    ax.set_title("solving from samples alone", loc="left")
    legend(ax, ink, loc="upper right")

    ax = axes[1]
    new_ax(ax, ink)
    ranks = [5, 10, 20, 40, 80]
    needs = [rows_needed_median(m, n, r, target=0.1, seeds=5) for r in ranks]
    ax.plot(ranks, needs, "-o", color=cols[0], lw=1.9, ms=6,
            label="rows needed for 10% error")
    ax.plot(ranks, [m] * len(ranks), ls="--", color=cols[3], lw=1.5,
            label=f"the whole matrix ({m} rows)")
    ax.fill_between(ranks, needs, [m] * len(ranks), color=cols[0], alpha=0.10,
                    lw=0)
    ax.set_ylim(0, m * 1.05)
    ax.set_xlabel("rank of the data")
    ax.set_ylabel("rows the classical algorithm reads")
    ax.set_title("the shaded gap is Tang's result", loc="left")
    legend(ax, ink, loc="center left")

    ax = axes[2]
    new_ax(ax, ink)
    ranks_all = [2, 5, 10, 20, 40, 80]
    srs = [stable_rank(make_matrix(m, n, r, seed=0)) for r in ranks_all]
    needs_all = [rows_needed_median(m, n, r, target=0.1, seeds=5)
                 for r in ranks_all]
    ax.scatter(srs[1:], needs_all[1:], s=60, color=cols[0], zorder=4,
               label="rank ≥ 5")
    ax.scatter(srs[:1], needs_all[:1], s=80, color=cols[3], zorder=5,
               marker="D", label="rank 2 — the anomaly")
    for sr, nd, rk in zip(srs, needs_all, ranks_all):
        ax.annotate(f"{rk}", xy=(sr, nd), xytext=(4, 5),
                    textcoords="offset points", fontsize=7.6,
                    color=ink["muted"])
    ax.set_xscale("log")
    ax.set_ylim(0, 150)
    ax.set_xlabel("stable rank  ‖A‖_F² / ‖A‖₂²")
    ax.set_ylabel("rows needed")
    ax.set_title("what sampling actually responds to", loc="left")
    ax.text(0.26, 0.60, "nominal rank counts directions;\n"
                        "stable rank weighs them",
            transform=ax.transAxes, fontsize=8.2, color=ink["secondary"])
    legend(ax, ink, loc="lower right")

    fig.suptitle("Dequantisation costs scale with the rank, not the "
                 "dimension — and stop working when the rank is large",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-boundary", mode)


def main():
    for mode in ("light", "dark"):
        fig_tolls(mode)
        fig_boundary(mode)


if __name__ == "__main__":
    print("Autopsy 11 — HHL and Tang figures:")
    main()
