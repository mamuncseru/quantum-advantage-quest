"""Figures for deep dive 01 — the Fourier thread.

Five light/dark pairs, every one computed from
`study-deep-dive/01-fourier-thread/fourier_lab.py` rather than sketched:

  fig-characters  orthogonality as vectors that cancel + the whole Gram matrix
  fig-spectra     four functions, four spectra, one circuit
  fig-readout     how spread a spectrum is, and what that costs to read
  fig-comb        the QFT comb: exact when r | N, Dirichlet leakage when not
  fig-fragility   what corrupting the structure does to the spike

Run from repo root:  .venv/bin/python scripts/make_fourier_figures.py
"""

import sys
from math import gcd, pi
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "study-deep-dive/01-fourier-thread"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from fourier_lab import (character, collision_entropy,  # noqa: E402
                         corrupted_linear, gram, peak_mass, period_readout,
                         popcount, samples_to_span, shor_success_rate,
                         spectrum, spike_height)

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
HEAT = {"light": "Purples", "dark": "magma"}


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


def save(fig, name, mode):
    suffix = "-dark" if mode == "dark" else ""
    out = ROOT / OUT / f"{name}{suffix}.svg"
    fig.savefig(out, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"  {out.relative_to(ROOT)}")


def legend(ax, ink, **kw):
    leg = ax.legend(frameon=False, fontsize=8, **kw)
    for t in leg.get_texts():
        t.set_color(ink["secondary"])
    return leg


# ------------------------------------------------------- 1 · orthogonality ---

def fig_characters(mode):
    """Left: the N terms of an inner product, laid head to tail. Right: all
    N^2 inner products at once."""
    ink, cols = INK[mode], SERIES[mode]
    N = 8
    fig, axes = plt.subplots(1, 2, figsize=(9.2, 3.9))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    ax.grid(False)
    ax.set_aspect("equal")
    for i, (d, lab) in enumerate([(0, r"$k = \ell$  (same character)"),
                                  (1, r"$k - \ell = 1$"),
                                  (3, r"$k - \ell = 3$")]):
        terms = character(N, d)                       # χ_k(x)·conj(χ_ℓ(x))
        path = np.concatenate([[0], np.cumsum(terms)])
        ax.plot(path.real, path.imag, "-o", color=cols[i], lw=1.6, ms=3.4,
                label=lab, zorder=3 - i * 0.1)
        ax.annotate("", xy=(path.real[-1], path.imag[-1]),
                    xytext=(path.real[-2], path.imag[-2]),
                    arrowprops=dict(arrowstyle="-|>", color=cols[i], lw=1.4))
    ax.scatter([0], [0], s=70, facecolor="none", edgecolor=ink["muted"],
               lw=1.1, zorder=4)
    ax.text(0.28, -0.92, "back to zero", color=ink["muted"], fontsize=8.5,
            style="italic")
    ax.text(7.9, 0.34, "sums to N", color=cols[0], fontsize=8.5,
            style="italic", ha="right")
    ax.axhline(0, color=ink["axis"], lw=0.7)
    ax.axvline(0, color=ink["axis"], lw=0.7)
    ax.set_xlim(-1.6, 8.7)
    ax.set_ylim(-1.5, 3.1)
    ax.set_xlabel("real part")
    ax.set_ylabel("imaginary part")
    ax.set_title(r"$\sum_x \chi_k(x)\,\overline{\chi_\ell(x)}$ — eight unit "
                 "vectors, head to tail")
    legend(ax, ink, loc="lower right")

    ax = axes[1]
    new_ax(ax, ink)
    ax.grid(False)
    G = np.abs(gram([character(N, k) for k in range(N)]))
    im = ax.imshow(G, cmap=HEAT[mode], vmin=0, vmax=1, origin="lower")
    ax.set_xticks(range(N))
    ax.set_yticks(range(N))
    ax.set_xlabel(r"$\ell$")
    ax.set_ylabel(r"$k$")
    ax.set_title(r"$|\langle \chi_k, \chi_\ell\rangle| / N$ — the identity "
                 "matrix, exactly")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=ink["muted"], labelsize=8)
    ax.text(0.5, 6.4, f"max off-diagonal\n{np.abs(G - np.eye(N)).max():.1e}",
            color=ink["secondary"], fontsize=8.5)

    fig.suptitle("Orthogonality is the whole engine: mismatched frequencies "
                 "cancel to zero, matched ones pile up",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-characters", mode)


# --------------------------------------------------------- 2 · four spectra --

def fig_spectra(mode):
    ink, cols = INK[mode], SERIES[mode]
    n, N = 6, 64
    s = 0b101101
    rng = np.random.default_rng(11)
    bits = rng.integers(0, 2, size=N)
    xs = rng.permutation(N)
    half = set(int(v) for v in xs[:N // 2])

    panels = [
        ("constant   f(x) = 0", lambda x: 0,
         "all the mass at frequency 0"),
        ("linear   f(x) = s·x,  s = 101101", lambda x: int(popcount(x & s)) & 1,
         "one spike, standing on s"),
        ("balanced, not linear", lambda x: int(x in half),
         "frequency 0 empty, the rest spread"),
        ("no promise   (random f)", lambda x: int(bits[x]),
         "nothing to read"),
    ]

    fig, axes = plt.subplots(2, 2, figsize=(9.4, 5.0), sharex=True)
    fig.patch.set_alpha(0.0)
    for ax, (title, f, verdict) in zip(axes.ravel(), panels):
        new_ax(ax, ink)
        F = spectrum(f, n)
        p = F ** 2
        ax.bar(np.arange(N), F, width=0.82,
               color=[cols[0] if v >= 0 else cols[1] for v in F], zorder=3)
        ax.axhline(0, color=ink["axis"], lw=0.8)
        ax.set_ylim(-1.15, 1.15)
        ax.set_title(title, loc="left")
        ax.text(0.985, 0.05,
                f"support {int(np.sum(np.abs(F) > 1e-12)):d}/{N}   "
                f"max p {p.max():.3f}   {collision_entropy(p):.2f} bits",
                transform=ax.transAxes, ha="right", fontsize=8,
                color=ink["muted"], fontfamily="monospace")
        ax.text(0.015, 0.16, verdict, transform=ax.transAxes, ha="left",
                fontsize=9, color=ink["secondary"], style="italic")
    for ax in axes[1]:
        ax.set_xlabel("frequency z  (0 … 63)")
    for ax in axes[:, 0]:
        ax.set_ylabel("Fourier coefficient  F̂(z)")

    fig.suptitle("One circuit, four promises: the Hadamard sandwich always "
                 "returns the spectrum of (−1)^f",
                 color=ink["secondary"], fontsize=10.5, y=1.0)
    fig.tight_layout()
    save(fig, "fig-spectra", mode)


# ------------------------------------------------------ 3 · readout budget ---

def fig_readout(mode):
    ink, cols = INK[mode], SERIES[mode]
    ns = np.arange(4, 13)

    ent_flat, ent_simon = [], []
    rng = np.random.default_rng(4)
    for n in ns:
        bits = rng.integers(0, 2, size=1 << n)
        p = spectrum(lambda x: int(bits[x]), n) ** 2
        ent_flat.append(collision_entropy(p))
        ent_simon.append(n - 1.0)               # uniform on H⊥, |H⊥| = 2^(n−1)
    simon_cost = [samples_to_span(int(n), trials=200, seed=int(n)) for n in ns]

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.8))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    ax.plot(ns, ent_flat, "-o", color=cols[3], lw=1.7, ms=4,
            label="no structure (random f)")
    ax.plot(ns, ent_simon, "-s", color=cols[2], lw=1.7, ms=4,
            label="Simon: uniform on H⊥")
    ax.plot(ns, np.zeros_like(ns, dtype=float), "-^", color=cols[0], lw=1.7,
            ms=4, label="DJ / BV: a single outcome")
    ax.annotate("Simon's spectrum is as spread as noise —\n"
                "and still readable, because its outcomes\n"
                "are a subgroup rather than a mess",
                xy=(ns[-2], ent_simon[-2] + 0.15), xytext=(4.15, 9.1),
                fontsize=8.2, color=ink["secondary"],
                arrowprops=dict(arrowstyle="-|>", color=ink["muted"], lw=1.0,
                                connectionstyle="arc3,rad=-0.25"))
    ax.set_ylim(-2.4, 12.4)
    ax.set_xlabel("n")
    ax.set_ylabel("collision entropy of the spectrum (bits)")
    ax.set_title("how spread the spectrum is")
    legend(ax, ink, loc="lower right")

    ax = axes[1]
    new_ax(ax, ink)
    ax.plot(ns, 2.0 ** ns, "-o", color=cols[3], lw=1.7, ms=4,
            label="no structure: Ω(2ⁿ) — no algorithm")
    ax.plot(ns, simon_cost, "-s", color=cols[2], lw=1.7, ms=4,
            label="Simon: n − 1 equations (+1.6 waste)")
    ax.plot(ns, np.ones_like(ns, dtype=float), "-^", color=cols[0], lw=1.7,
            ms=4, label="DJ / BV: one query")
    ax.axhline(43, color=cols[1], lw=1.6, ls="--",
               label="classical DJ baseline: 43 samples, any n")
    ax.set_yscale("log")
    ax.set_xlabel("n")
    ax.set_ylabel("samples to reach the answer")
    ax.set_title("what that costs to read")
    legend(ax, ink, loc="upper left")

    fig.suptitle("A quantum Fourier transform hands you one sample of |F̂|² — "
                 "so only concentrated spectra are readable",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-readout", mode)


# --------------------------------------------------------------- 4 · comb ----

def fig_comb(mode):
    ink, cols = INK[mode], SERIES[mode]
    N = 256
    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.5),
                             gridspec_kw=dict(width_ratios=[1, 1, 0.72]))
    fig.patch.set_alpha(0.0)

    for ax, r in zip(axes[:2], (16, 11)):
        new_ax(ax, ink)
        p = period_readout(N, r)
        ax.bar(np.arange(N), p, width=1.0, color=cols[0], zorder=3)
        for j in range(r):
            ax.axvline(j * N / r, color=cols[1], lw=0.9, ls=":", zorder=1,
                       alpha=0.75)
        ax.set_xlim(-2, N + 2)
        ax.set_ylim(0, p.max() * 1.42)
        ax.set_xlabel("measured c")
        ax.set_ylabel("probability")
        div = "divides" if N % r == 0 else "does not divide"
        ax.set_title(f"r = {r}  ({div} N = {N})", loc="left")
        ax.text(0.98, 0.95,
                f"peak mass {peak_mass(N, r):.3f}\n"
                f"one-shot recovery {shor_success_rate(N, r):.3f}",
                transform=ax.transAxes, ha="right", va="top", fontsize=8.2,
                color=ink["secondary"], fontfamily="monospace")

    ax = axes[2]
    new_ax(ax, ink)
    r = 11
    p = period_readout(N, r)
    centre = 3 * N / r
    lo, hi = int(centre) - 6, int(centre) + 7
    ax.bar(np.arange(lo, hi), p[lo:hi], width=0.85, color=cols[0], zorder=3)
    ax.axvspan(centre - 0.5, centre + 0.5, color=cols[2], alpha=0.20, zorder=1)
    ax.axvline(centre, color=cols[1], lw=1.2, ls=":", zorder=2)
    # exact envelope: the geometric sum |(1/sqrt(mN)) sum_j w^{c j r}|^2,
    # evaluated at real c. Not a fitted curve — the same formula the bars are.
    m = len(range(0, N, r))
    grid = np.linspace(lo - 0.5, hi - 0.5, 800)
    num = np.sin(pi * grid * r * m / N) ** 2
    den = np.sin(pi * grid * r / N) ** 2
    env = np.where(den > 1e-14, num / np.maximum(den, 1e-14), m ** 2) / (m * N)
    ax.plot(grid, env, color=cols[3], lw=1.3, zorder=4)
    ax.set_xlabel("measured c")
    ax.set_title(f"one peak, r = {r}", loc="left")
    ax.text(0.5, -0.36, "shaded: the ±½ bin Legendre needs;\n"
                        "red: the exact Dirichlet envelope",
            transform=ax.transAxes, ha="center", va="top", fontsize=8.2,
            color=ink["muted"], style="italic")

    fig.suptitle("Change the group from ℤ₂ⁿ to ℤ_N and exactness is the first "
                 "casualty — the comb leaks, and continued fractions clean up",
                 color=ink["secondary"], fontsize=10.5, y=1.03)
    fig.tight_layout()
    save(fig, "fig-comb", mode)


# ---------------------------------------------------------- 5 · fragility ----

def fig_fragility(mode):
    ink, cols = INK[mode], SERIES[mode]
    n, s = 10, 0b1011010110
    eps = np.linspace(0.0, 0.35, 15)
    measured = [spike_height(n, s, float(e), seed=7) for e in eps]

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.7))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    ax.plot(eps, (1 - 2 * eps) ** 2, color=cols[1], lw=1.6, ls="--",
            label="theory  (1 − 2ε)²")
    ax.plot(eps, np.array(measured) ** 2, "-o", color=cols[0], lw=1.7, ms=4,
            label="measured single-shot success")
    ax.axhline(2 ** -n, color=ink["muted"], lw=1.0, ls=":")
    ax.text(0.20, 2 ** -n * 1.5, "random guessing", color=ink["muted"],
            fontsize=8.5, style="italic")
    ax.set_yscale("log")
    ax.set_xlabel("fraction ε of the oracle's answers corrupted")
    ax.set_ylabel("P(read the whole secret in one shot)")
    ax.set_title("the spike is second-order fragile", loc="left")
    legend(ax, ink, loc="upper right")

    ax = axes[1]
    new_ax(ax, ink)
    F = spectrum(corrupted_linear(n, s, 0.1, seed=7), n)
    p = F ** 2
    leaked = 1.0 - p[s]
    ax.bar(np.arange(1 << n), np.maximum(p, 1e-9), width=1.0, color=cols[3],
           zorder=3)
    ax.bar([s], [p[s]], width=7.0, color=cols[0], zorder=4)
    ax.axhline(leaked / ((1 << n) - 1), color=ink["secondary"], lw=1.1,
               ls="--", zorder=5)
    ax.set_yscale("log")
    ax.set_ylim(1e-8, 3.0)
    ax.annotate(f"s survives at {p[s]:.2f}", xy=(s, p[s]),
                xytext=(40, 1.3), color=ink["secondary"], fontsize=8.6,
                arrowprops=dict(arrowstyle="-|>", color=ink["muted"], lw=1.0))
    ax.text(1 << n, leaked / ((1 << n) - 1) * 9.0,
            f"leaked mass ÷ 2ⁿ = {leaked / ((1 << n) - 1):.1e}",
            ha="right", fontsize=8.2, color=ink["secondary"])
    ax.set_xlabel("frequency z")
    ax.set_ylabel("probability (log)")
    ax.set_title("ε = 0.10: the rest of the mass is now everywhere",
                 loc="left")

    fig.suptitle("The mechanism needs exact algebra: 10% corruption costs a "
                 "third of the answer, and no circuit repairs it",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-fragility", mode)


def main():
    for mode in ("light", "dark"):
        fig_characters(mode)
        fig_spectra(mode)
        fig_readout(mode)
        fig_comb(mode)
        fig_fragility(mode)


if __name__ == "__main__":
    print("Deep dive 01 — Fourier figures:")
    main()
    N, r = 256, 11
    print(f"\nsanity: peak mass(N={N}, r={r}) = {peak_mass(N, r):.4f}  "
          f"floor 4/pi^2 = {4 / pi ** 2:.4f}  "
          f"phi(r)/r = {sum(1 for j in range(r) if gcd(j, r) == 1) / r:.4f}")
