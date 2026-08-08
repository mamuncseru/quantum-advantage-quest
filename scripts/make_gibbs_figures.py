"""Figures for autopsy 13 — quantum Gibbs sampling.

Two light/dark pairs (fig-convergence is older and still current), computed
by `predecessors/12-gibbs-lindblad/`:

  fig-walls   the gap, the sign problem, and the thermal entanglement
  fig-window  the recipe: break the dequantizer, keep the mixer

Run from repo root:  .venv/bin/python scripts/make_gibbs_figures.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "predecessors/12-gibbs-lindblad"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from davies import heisenberg_with_fields  # noqa: E402
from dequantizer_window import knob_sweep, profile  # noqa: E402
from gibbs_gap import (average_sign, davies_gap, frustrated_afm,  # noqa: E402
                       qmc_overhead, thermal_mutual_information,
                       transverse_ising)

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


# -------------------------------------------------------------- 1 · walls ---

def fig_walls(mode):
    ink, cols = INK[mode], SERIES[mode]
    betas = np.array([0.25, 0.5, 1.0, 2.0, 3.0, 4.0, 6.0])
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.5))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    H = heisenberg_with_fields(3)
    ax.plot(betas, [davies_gap(H, float(b)) for b in betas], "-o",
            color=cols[0], lw=1.9, ms=5, label="Davies gap")
    ax.plot(betas, [1.0 / davies_gap(H, float(b)) for b in betas], "-s",
            color=cols[3], lw=1.9, ms=5, label="mixing time ∝ 1/gap")
    ax.set_xlabel("inverse temperature β")
    ax.set_ylabel("gap  /  1 ÷ gap")
    ax.set_title("the quantum cost", loc="left")
    legend(ax, ink, loc="center right")

    ax = axes[1]
    new_ax(ax, ink)
    for i, (label, Hx) in enumerate((
            ("transverse Ising (stoquastic)", transverse_ising(3)),
            ("Heisenberg CHAIN (bipartite)", heisenberg_with_fields(3)),
            ("triangle AFM (frustrated)", frustrated_afm(3)),
            ("all-pairs AFM, n = 4", frustrated_afm(4)))):
        ax.semilogy(betas, [max(average_sign(Hx, float(b)), 1e-12)
                            for b in betas], "-o", ms=4, lw=1.7,
                    color=cols[i], label=label)
    ax.set_ylim(1e-8, 3)
    ax.set_xlabel("inverse temperature β")
    ax.set_ylabel("average sign  ⟨s⟩")
    ax.set_title("wall 1: the sign problem", loc="left")
    ax.text(0.04, 0.06, "non-commuting ≠ signful:\nthe chain sits at 1.0",
            transform=ax.transAxes, fontsize=8, color=ink["secondary"])
    legend(ax, ink, loc="lower left", fontsize=6.8)

    ax = axes[2]
    new_ax(ax, ink)
    H4 = heisenberg_with_fields(4)
    ax.plot(betas, [thermal_mutual_information(H4, float(b)) for b in betas],
            "-o", color=cols[2], lw=1.9, ms=5)
    ax.axvspan(0, 0.5, color=cols[2], alpha=0.14, lw=0)
    ax.text(0.14, 0.55, "provably\neasy", fontsize=8.4, color=cols[2],
            transform=ax.transAxes, ha="center")
    ax.set_xlabel("inverse temperature β")
    ax.set_ylabel("mutual information (bits)")
    ax.set_title("wall 2: thermal correlation", loc="left")

    fig.suptitle("An advantage needs the gap to stay open while BOTH "
                 "classical mechanisms degrade",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-walls", mode)


# ------------------------------------------------------------- 2 · window ---

def fig_window(mode):
    ink, cols = INK[mode], SERIES[mode]
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.5),
                             gridspec_kw=dict(width_ratios=[1.15, 1, 1]))
    fig.patch.set_alpha(0.0)

    lams = np.linspace(0, 1, 9)
    rows = [profile(3, float(l), 3.0) for l in lams]

    ax = axes[0]
    new_ax(ax, ink)
    ax.semilogy(lams, [r["qmc"] for r in rows], "-o", color=cols[3], lw=2.0,
                ms=5, label="classical: QMC overhead")
    ax.semilogy(lams, [r["mixing"] for r in rows], "-s", color=cols[0],
                lw=2.0, ms=5, label="quantum: mixing time")
    ax.semilogy(lams, [r["norm"] for r in rows], ls=":", color=ink["muted"],
                lw=1.5, label="‖H‖ (the knob is honest)")
    ax.set_xlabel("frustration λ  (weight of the closing bond)")
    ax.set_ylabel("cost")
    ax.set_title("break the dequantizer, keep the mixer", loc="left")
    legend(ax, ink, loc="upper left")

    ax = axes[1]
    new_ax(ax, ink)
    ax.grid(False)
    lam_grid = np.linspace(0, 1, 9)
    beta_grid = np.array([0.5, 1.0, 2.0, 3.0, 4.0, 5.0])
    Zq = np.array([[np.log10(max(profile(3, float(l), float(b))["qmc"], 1.0))
                    for b in beta_grid] for l in lam_grid])
    im = ax.imshow(Zq, origin="lower", aspect="auto", cmap="magma",
                   extent=[beta_grid[0], beta_grid[-1], 0, 1])
    ax.set_xlabel("inverse temperature β")
    ax.set_ylabel("frustration λ")
    ax.set_title("classical cost, log₁₀", loc="left")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=ink["muted"], labelsize=8)

    ax = axes[2]
    new_ax(ax, ink)
    ax.grid(False)
    Zg = np.array([[profile(3, float(l), float(b))["gap"] for b in beta_grid]
                   for l in lam_grid])
    im2 = ax.imshow(Zg, origin="lower", aspect="auto", cmap="viridis",
                    extent=[beta_grid[0], beta_grid[-1], 0, 1])
    # the window: classical expensive AND gap open
    win = (Zq >= 2.0) & (Zg >= 0.25)
    ax.contour(np.linspace(beta_grid[0], beta_grid[-1], len(beta_grid)),
               np.linspace(0, 1, len(lam_grid)), win.astype(float),
               levels=[0.5], colors="#ffffff", linewidths=2.0)
    ax.set_xlabel("inverse temperature β")
    ax.set_ylabel("frustration λ")
    ax.set_title("Davies gap, window outlined", loc="left")
    ax.text(4.0, 0.90, "window", fontsize=9, color="#ffffff",
            fontweight="bold", ha="center")
    ax.text(0.5, -0.30, "at n = 3 the gap never closes, so the boundary is "
                        "set entirely by the classical side",
            transform=ax.transAxes, ha="center", va="top", fontsize=7.8,
            color=ink["secondary"], style="italic")
    cb2 = fig.colorbar(im2, ax=ax, fraction=0.046, pad=0.03)
    cb2.outline.set_visible(False)
    cb2.ax.tick_params(colors=ink["muted"], labelsize=8)

    fig.suptitle("The recipe, executed: classical cost up 40,000× while the "
                 "mixing time does not move",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-window", mode)


def main():
    for mode in ("light", "dark"):
        fig_walls(mode)
        fig_window(mode)


if __name__ == "__main__":
    print("Autopsy 13 — Gibbs sampling figures:")
    main()
