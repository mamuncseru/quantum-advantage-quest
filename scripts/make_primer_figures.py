"""Figures for the prerequisite page — Fourier from scratch.

Five light/dark pairs, all computed by
`study-deep-dive/00-fourier-primer/primer_lab.py`:

  fig-recipe       a signal is a sum of waves; the spectrum is the recipe
  fig-correlation  the one measurement: multiply, average, sweep
  fig-square       Fourier series of a square wave, and Gibbs' 9%
  fig-sampling     N samples, N frequencies: aliasing and leakage
  fig-bridge       the same algebra on Z_2^n, where a wave is a sign pattern

Run from repo root:  .venv/bin/python scripts/make_primer_figures.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "study-deep-dive/00-fourier-primer"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from primer_lab import (amount_of_frequency, complex_wave,  # noqa: E402
                        cosine, gibbs_fraction, leakage_profile,
                        orthogonality_table, peak_share, power_spectrum,
                        sample_times, square_series, square_wave,
                        walsh_pattern)

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


# ------------------------------------------------------------- 1 · recipe ---

def fig_recipe(mode):
    ink, cols = INK[mode], SERIES[mode]
    N = 256
    t = sample_times(N)
    parts = [(3, 1.0), (7, 0.5), (12, 0.25)]
    sig = sum(a * cosine(N, k) for k, a in parts) + 0.4

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.5),
                             gridspec_kw=dict(width_ratios=[1.35, 1]))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    for i, (k, a) in enumerate(parts):
        ax.plot(t, a * cosine(N, k), color=cols[i], lw=1.1, alpha=0.55,
                label=f"{a} × cos({k} cycles)")
    ax.plot(t, sig, color=ink["primary"], lw=2.0, label="their sum + 0.4",
            zorder=5)
    ax.set_xlabel("time, as a fraction of the window")
    ax.set_ylabel("value")
    ax.set_title("three waves and the lumpy signal they add up to", loc="left")
    legend(ax, ink, loc="lower center", ncol=2)
    ax.set_ylim(-2.6, 3.1)

    ax = axes[1]
    new_ax(ax, ink)
    # amplitude of the cosine at frequency k: a real cosine splits its
    # energy between +k and -k, so the coefficient is half the amplitude.
    mags = np.array([abs(amount_of_frequency(sig, k)) * (1 if k == 0 else 2)
                     for k in range(20)])
    ax.bar(np.arange(20), mags, width=0.72, color=cols[0], zorder=3)
    for k, a in parts:
        ax.annotate(f"{a}", xy=(k, mags[k]), xytext=(k, mags[k] + 0.05),
                    ha="center", fontsize=8.5, color=ink["secondary"])
    ax.annotate("the constant\n(frequency 0)", xy=(0.35, mags[0]),
                xytext=(4.6, 0.62), fontsize=8.2, color=ink["secondary"],
                arrowprops=dict(arrowstyle="-|>", color=ink["muted"], lw=1.0))
    ax.set_xlabel("frequency k, in cycles per window")
    ax.set_ylabel("amplitude of that wave")
    ax.set_title("the recipe, read straight off", loc="left")
    ax.set_ylim(0, 1.24)

    fig.suptitle("A spectrum is a recipe: which waves, and how much of each",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-recipe", mode)


# -------------------------------------------------------- 2 · correlation ---

def fig_correlation(mode):
    ink, cols = INK[mode], SERIES[mode]
    N = 512
    t = sample_times(N)
    sig = cosine(N, 5) + 0.6 * cosine(N, 11)

    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.3),
                             gridspec_kw=dict(width_ratios=[1, 1, 1.06]))
    fig.patch.set_alpha(0.0)

    for ax, probe, tag in [(axes[0], 5, "matched: k = 5"),
                           (axes[1], 6, "mismatched: k = 6")]:
        new_ax(ax, ink)
        prod = sig * cosine(N, probe)
        ax.fill_between(t, 0, prod, where=prod >= 0, color=cols[0], alpha=0.55,
                        lw=0)
        ax.fill_between(t, 0, prod, where=prod < 0, color=cols[1], alpha=0.55,
                        lw=0)
        ax.plot(t, sig, color=ink["muted"], lw=0.9, alpha=0.8)
        ax.plot(t, cosine(N, probe), color=cols[3], lw=1.1, ls="--")
        ax.axhline(0, color=ink["axis"], lw=0.8)
        ax.set_title(tag, loc="left")
        ax.set_xlabel("time")
        ax.text(0.5, -0.34, f"average of the product = {np.mean(prod):+.3f}",
                transform=ax.transAxes, ha="center", va="top", fontsize=9,
                color=ink["secondary"])
        ax.set_ylim(-2.1, 2.1)
    axes[0].set_ylabel("signal × probe")

    ax = axes[2]
    new_ax(ax, ink)
    ks = np.arange(0, 20)
    vals = np.array([2 * abs(amount_of_frequency(sig, k)) for k in ks])
    ax.bar(ks, vals, width=0.72, color=cols[0], zorder=3)
    ax.set_xlabel("probe frequency k")
    ax.set_ylabel("|average of the product|")
    ax.set_title("sweep all probes → the spectrum", loc="left")

    fig.suptitle("The only measurement in Fourier analysis: multiply by a "
                 "probe wave, average, repeat",
                 color=ink["secondary"], fontsize=10.5, y=1.04)
    fig.tight_layout()
    save(fig, "fig-correlation", mode)


# ------------------------------------------------------------- 3 · square ---

def fig_square(mode):
    ink, cols = INK[mode], SERIES[mode]
    N = 2000
    t = sample_times(N)

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.5))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    ax.plot(t, square_wave(N), color=ink["muted"], lw=1.4, ls=":",
            label="the square wave")
    for i, terms in enumerate([1, 3, 9, 49]):
        ax.plot(t, square_series(N, terms), color=cols[i], lw=1.3,
                label=f"{terms} harmonic" + ("s" if terms > 1 else ""))
    ax.set_xlim(0, 0.62)
    ax.set_ylim(-1.45, 1.65)
    ax.set_xlabel("time")
    ax.set_title("adding odd harmonics, one at a time", loc="left")
    legend(ax, ink, loc="lower left", ncol=2)

    ax = axes[1]
    new_ax(ax, ink)
    terms = [1, 2, 3, 5, 9, 17, 33, 65, 129, 257, 513]
    frac = [gibbs_fraction(m) for m in terms]
    ax.plot(terms, frac, "-o", color=cols[0], lw=1.7, ms=4)
    ax.axhline(0.0894898, color=cols[3], lw=1.4, ls="--",
               label="Wilbraham–Gibbs constant 0.08949")
    ax.set_xscale("log")
    ax.set_xlabel("harmonics used (log)")
    ax.set_ylabel("overshoot, as a fraction of the jump")
    ax.set_ylim(0.07, 0.15)
    ax.set_title("the 9% that never goes away", loc="left")
    legend(ax, ink, loc="upper right")

    fig.suptitle("A finite recipe cannot make a sharp edge — it can only "
                 "make the ringing narrower",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-square", mode)


# ----------------------------------------------------------- 4 · sampling ---

def fig_sampling(mode):
    ink, cols = INK[mode], SERIES[mode]

    fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.6))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    N, fine = 16, 800
    tf = np.linspace(0, 1, fine)
    ax.plot(tf, np.cos(2 * np.pi * 1 * tf), color=cols[0], lw=1.6,
            label="1 cycle per window")
    ax.plot(tf, np.cos(2 * np.pi * 17 * tf), color=cols[3], lw=1.0, alpha=0.75,
            label="17 cycles per window")
    ax.scatter(sample_times(N), cosine(N, 1), s=42, color=ink["primary"],
               zorder=5, label="the 16 samples (identical for both)")
    ax.set_xlabel("time")
    ax.set_title("aliasing: 16 samples cannot tell 1 from 17", loc="left")
    ax.set_ylim(-1.5, 1.9)
    legend(ax, ink, loc="upper center", ncol=1)

    ax = axes[1]
    new_ax(ax, ink)
    N = 64
    for i, freq in enumerate([8.0, 8.25, 8.5]):
        p = leakage_profile(N, freq)[:N // 2 + 1]
        ax.plot(np.arange(len(p)), np.maximum(p / p.max(), 1e-17), "-o",
                ms=3.4, lw=1.4, color=cols[i],
                label=f"{freq} cycles — top two bins hold "
                      f"{peak_share(N, freq):.2f}")
    ax.set_yscale("log")
    ax.set_ylim(1e-6, 400)
    ax.set_xlim(0, 20)
    ax.set_xlabel("frequency bin k")
    ax.set_ylabel("relative power (log)")
    ax.set_title("leakage: a tone that does not fit spreads out", loc="left")
    ax.text(0.5, 0.04, "8.0 has nothing outside its bin — the rest is below "
                       "1e-6", transform=ax.transAxes, ha="center",
            fontsize=8, color=ink["muted"], style="italic")
    legend(ax, ink, loc="upper left")

    fig.suptitle("Two facts that follow from having finitely many samples — "
                 "and both come back in Shor's algorithm",
                 color=ink["secondary"], fontsize=10.5, y=1.02)
    fig.tight_layout()
    save(fig, "fig-sampling", mode)


# ------------------------------------------------------------- 5 · bridge ---

def fig_bridge(mode):
    ink, cols = INK[mode], SERIES[mode]
    N, n = 8, 3

    fig, axes = plt.subplots(1, 3, figsize=(10.2, 3.4),
                             gridspec_kw=dict(width_ratios=[1.1, 1.1, 1]))
    fig.patch.set_alpha(0.0)

    ax = axes[0]
    new_ax(ax, ink)
    tf = np.linspace(0, 1, 400)
    for i, k in enumerate([1, 2, 3]):
        ax.plot(tf, np.cos(2 * np.pi * k * tf) - 2.6 * i, color=cols[i], lw=1.4)
        ax.scatter(sample_times(N), cosine(N, k) - 2.6 * i, s=26,
                   color=cols[i], zorder=4)
        ax.text(1.01, -2.6 * i, f"k = {k}", fontsize=8.5,
                color=ink["secondary"], va="center")
    ax.set_yticks([])
    ax.set_xlabel("x / N")
    ax.set_title("on ℤ₈: waves take many values", loc="left")

    ax = axes[1]
    new_ax(ax, ink)
    ax.grid(False)
    for i, z in enumerate([1, 2, 3]):
        w = walsh_pattern(n, z)
        ax.bar(np.arange(N), w, bottom=-2.6 * i, width=0.75,
               color=[cols[i] if v > 0 else ink["muted"] for v in w],
               zorder=3)
        ax.axhline(-2.6 * i, color=ink["axis"], lw=0.7)
        ax.text(N - 0.2, -2.6 * i, f"z = {z:03b}", fontsize=8.5,
                color=ink["secondary"], va="center")
    ax.set_yticks([])
    ax.set_xlabel("x")
    ax.set_title("on ℤ₂³: the same waves, ±1 only", loc="left")

    ax = axes[2]
    new_ax(ax, ink)
    ax.grid(False)
    G = np.abs(orthogonality_table([walsh_pattern(n, z) for z in range(N)]))
    im = ax.imshow(G, cmap=HEAT[mode], vmin=0, vmax=1, origin="lower")
    ax.set_xticks(range(N))
    ax.set_yticks(range(N))
    ax.set_xlabel("z′")
    ax.set_ylabel("z")
    ax.set_title("and they still cancel exactly", loc="left")
    cb = fig.colorbar(im, ax=ax, fraction=0.046, pad=0.03)
    cb.outline.set_visible(False)
    cb.ax.tick_params(colors=ink["muted"], labelsize=8)

    fig.suptitle("The bridge: a group where every element is its own inverse "
                 "leaves the waves only two values, ±1",
                 color=ink["secondary"], fontsize=10.5, y=1.03)
    fig.tight_layout()
    save(fig, "fig-bridge", mode)


def main():
    for mode in ("light", "dark"):
        fig_recipe(mode)
        fig_correlation(mode)
        fig_square(mode)
        fig_sampling(mode)
        fig_bridge(mode)


if __name__ == "__main__":
    print("Prerequisite — Fourier primer figures:")
    main()
