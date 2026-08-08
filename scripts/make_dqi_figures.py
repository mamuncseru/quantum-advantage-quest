"""Figures for autopsy 12 — Decoded Quantum Interferometry.

Two light/dark pairs, computed by `predecessors/11-dqi/`:

  fig-reduction  the objective's spectrum lands on low-weight codewords
  fig-semicircle the law, the baseline, and the radius a decoder must reach

Run from repo root:  .venv/bin/python scripts/make_dqi_figures.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "predecessors/11-dqi"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from dqi_spectrum import (objective_sign, optimal_weights,  # noqa: E402
                          polynomial_of_objective, random_instance,
                          reachable_frequencies, satisfied_fraction,
                          semicircle_convergence, semicircle_prediction,
                          walsh)
from prange_baseline import (prange_prediction, reed_solomon_radius,  # noqa: E402
                             required_radius)

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


# ---------------------------------------------------------- 1 · reduction ---

def fig_reduction(mode):
    ink, cols = INK[mode], SERIES[mode]
    rng = np.random.default_rng(4)
    n, m = 10, 6
    A, b = random_instance(n, m, rng)
    s = objective_sign(A, b, n)
    N = 1 << n

    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.4))
    fig.patch.set_alpha(0.0)

    for ax, ell in zip(axes[:2], (1, 3)):
        new_ax(ax, ink)
        P = polynomial_of_objective(s, [0] * ell + [1])
        spec = np.abs(walsh(P))
        spec = spec / spec.max()
        reach = sorted(reachable_frequencies(A, ell))
        nz = np.flatnonzero(spec > 1e-9)
        outside = [int(z) for z in nz if int(z) not in set(reach)]
        # stems, not 1024 bars: at this density bars overlap and the picture
        # stops being readable.
        for z in reach:
            ax.plot([z, z], [0, 1.08], color=ink["muted"], lw=0.8,
                    alpha=0.45, zorder=1)
        ax.vlines(nz, 0, spec[nz], color=cols[0], lw=1.6, zorder=3)
        ax.scatter(nz, spec[nz], s=16, color=cols[0], zorder=4,
                   label="nonzero Fourier coefficient")
        ax.plot([], [], color=ink["muted"], lw=0.8, alpha=0.45,
                label=f"reachable: XOR of ≤ {ell} constraints")
        ax.set_ylim(0, 1.62)
        ax.set_xlim(-20, N + 20)
        ax.set_xlabel("frequency z")
        ax.set_title(f"spectrum of s^{ell}", loc="left")
        ax.text(0.5, 0.70, f"{len(nz)} nonzero · {len(reach)} reachable · "
                           f"{len(outside)} outside",
                transform=ax.transAxes, ha="center", fontsize=8.2,
                color=cols[3] if outside else ink["secondary"])
        legend(ax, ink, loc="upper left", fontsize=7.2)
    axes[0].set_ylabel("|Fourier coefficient| (normalised)")

    ax = axes[2]
    new_ax(ax, ink)
    ells = [1, 2, 3, 4]
    reach = [len(reachable_frequencies(A, l)) for l in ells]
    ax.plot(ells, reach, "-o", color=cols[0], lw=1.9, ms=6,
            label="frequencies a degree-ℓ polynomial can reach")
    ax.axhline(N, ls="--", color=ink["muted"], lw=1.3,
               label=f"all {N} frequencies")
    ax.set_yscale("log")
    ax.set_xticks(ells)
    ax.set_xlabel("polynomial degree ℓ  =  decoding radius")
    ax.set_ylabel("reachable frequencies")
    ax.set_title("degree buys reach", loc="left")
    legend(ax, ink, loc="lower right")

    fig.suptitle("The objective's spectrum lives on low-weight codewords — "
                 "so optimisation becomes decoding",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-reduction", mode)


# --------------------------------------------------------- 2 · semicircle ---

def fig_semicircle(mode):
    ink, cols = INK[mode], SERIES[mode]
    fig, axes = plt.subplots(1, 3, figsize=(10.8, 3.5))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    ds = np.linspace(0.005, 0.5, 60)
    ax.plot(ds, [semicircle_prediction(d) for d in ds], color=ink["muted"],
            lw=1.6, ls="--", label="semicircle law (m → ∞)")
    for i, m in enumerate((50, 200, 1600)):
        xs = [l / m for l in range(1, m // 2 + 1, max(1, m // 40))]
        ax.plot(xs, [satisfied_fraction(m, int(round(d * m))) for d in xs],
                color=cols[i], lw=1.7, label=f"exact, m = {m}")
    ax.set_xlabel("d = ℓ / m   (decoding radius, as a fraction)")
    ax.set_ylabel("satisfied fraction")
    ax.set_title("better decoder, better optimiser", loc="left")
    legend(ax, ink, loc="lower right")

    ax = axes[1]
    new_ax(ax, ink)
    m = 100
    ds = np.linspace(0.005, 0.5, 80)
    ax.plot(ds, [satisfied_fraction(m, max(1, int(round(d * m)))) for d in ds],
            color=cols[0], lw=2.0, label="DQI at radius ℓ")
    for i, n in enumerate((20, 40, 60, 80)):
        pr = prange_prediction(n, m)
        ax.axhline(pr, color=cols[3], lw=1.0, ls=":", alpha=0.8)
        need = required_radius(n, m)
        if need:
            ax.scatter([need / m], [pr], s=45, color=cols[3], zorder=5)
            ax.annotate(f"n = {n}", xy=(need / m, pr), xytext=(6, -11),
                        textcoords="offset points", fontsize=7.8,
                        color=ink["secondary"])
    ax.plot([], [], color=cols[3], ls=":", label="Prange, for several n")
    ax.set_xlabel("d = ℓ / m")
    ax.set_ylabel("satisfied fraction")
    ax.set_title(f"the radius needed (m = {m})", loc="left")
    legend(ax, ink, loc="lower right")

    ax = axes[2]
    new_ax(ax, ink)
    m = 200
    ks = [10, 20, 40, 80, 120, 160]
    ax.plot(ks, [reed_solomon_radius(m, k) / m for k in ks], "-o",
            color=cols[2], lw=1.9, ms=5, label="Reed–Solomon (list decoding)")
    ax.plot(ks, [reed_solomon_radius(m, k, False) / m for k in ks], "-s",
            color=cols[1], lw=1.7, ms=5, label="Reed–Solomon (unique)")
    ax.axhspan(0, 0.02, color=cols[3], alpha=0.18, lw=0)
    ax.text(85, 0.045, "random code: no efficient decoder\nbeyond Prange —"
                       " the attacker's own algorithm",
            fontsize=8, color=cols[3])
    ax.set_ylim(0, 0.85)
    ax.set_xlabel("code dimension k")
    ax.set_ylabel("decoding radius reached, as d")
    ax.set_title("structure vs randomness", loc="left")
    legend(ax, ink, loc="upper right")

    fig.suptitle("DQI's fate is decided in coding theory: the decoder sets "
                 "the degree, and the degree sets the objective",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-semicircle", mode)


def main():
    for mode in ("light", "dark"):
        fig_reduction(mode)
        fig_semicircle(mode)


if __name__ == "__main__":
    print("Autopsy 12 — DQI figures:")
    main()
