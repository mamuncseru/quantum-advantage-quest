"""Figures for autopsy 02 (Bernstein-Vazirani), section 6.

Left panel: single-shot success — the whole n-bit string correct at once —
falls off exponentially, while the per-bit read rate barely moves.
Right panel: majority-voting those independent bits across a handful of
shots recovers the secret where single-shot BV has already collapsed.

Run from repo root:  .venv/bin/python scripts/make_bv_figures.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "predecessors/02-bernstein-vazirani"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from bv_on_hardware import (exact_rate, majority_vote,  # noqa: E402
                            measure_shots, per_bit_rate, target_string)
from qsim.noise import MachineNoise  # noqa: E402

INK = {
    "light": dict(primary="#0b0b0b", secondary="#52514e", muted="#898781",
                  grid="#e1e0d9", axis="#c3c2b7"),
    "dark": dict(primary="#ffffff", secondary="#c3c2b7", muted="#898781",
                 grid="#2c2c2a", axis="#383835"),
}
SERIES = {
    "light": ["#2a78d6", "#1baf7a", "#eda100"],
    "dark": ["#3987e5", "#199e70", "#c98500"],
}
SHOWN = ["quantinuum-helios", "ibm-heron-r2", "rigetti-ankaa-3"]
NS = [4, 6, 8, 10, 12]
VOTE_SHOTS = 25


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


def vote_fail(p_bit, m):
    """P(majority of m independent reads of one bit is wrong).

    Exact binomial tail — the bit is lost only if more than half the
    shots misread it, which is why a handful of repetitions is enough.
    """
    from math import comb
    need = m // 2 + 1
    return sum(comb(m, k) * p_bit ** k * (1 - p_bit) ** (m - k)
               for k in range(need, m + 1))


def secret_for(n):
    return int("10110101"[:n] or "1", 2) & ((1 << n) - 1) or 1


def collect():
    data = {}
    for mid in SHOWN:
        nz = MachineNoise.from_catalog(mid)
        exact, perbit, vote = [], [], []
        for n in NS:
            s = secret_for(n)
            tgt = target_string(n, s)
            sh = measure_shots(n, s, nz, shots=240, seed=11 + n)
            exact.append(exact_rate(sh, tgt))
            perbit.append(per_bit_rate(sh, tgt))
            wins = 0
            trials = 12
            for t in range(trials):
                block = measure_shots(n, s, nz, shots=VOTE_SHOTS,
                                      seed=900 + 31 * n + t)
                wins += (majority_vote(block) == tgt)
            vote.append(wins / trials)
        data[nz.label] = dict(noise=nz, exact=exact, perbit=perbit,
                              vote=vote)
        print(f"  {nz.label}: exact={[round(v,2) for v in exact]} "
              f"vote={[round(v,2) for v in vote]}")
    return data


def main():
    data = collect()
    for mode in ("light", "dark"):
        ink, cols = INK[mode], SERIES[mode]
        fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.7))
        fig.patch.set_alpha(0.0)
        for ax in axes:
            new_ax(ax, ink)

        ax = axes[0]
        grid = np.linspace(3, 13, 60)
        for i, (label, d) in enumerate(data.items()):
            nz = d["noise"]
            model = ((1 - nz.readout) ** grid *
                     (1 - nz.err_1q) ** (2 * grid + 2))
            ax.plot(grid, model, color=cols[i], lw=1.5, zorder=2)
            ax.scatter(NS, d["exact"], s=34, color=cols[i], zorder=3,
                       label=label)
            ax.plot(NS, d["perbit"], color=cols[i], lw=1.2, ls=":",
                    zorder=2)
        ax.set_ylim(0.5, 1.02)
        ax.set_xlabel("secret length n")
        ax.set_ylabel("success rate")
        ax.set_title("solid/dots: whole string at once    dotted: per bit")
        leg = ax.legend(frameon=False, fontsize=8, loc="lower left")
        for t in leg.get_texts():
            t.set_color(ink["secondary"])

        ax = axes[1]
        big = np.arange(2, 201)
        for i, (label, d) in enumerate(data.items()):
            p_bit = 1.0 - float(np.mean(d["perbit"]))     # measured
            ax.plot(big, (1 - p_bit) ** big, color=cols[i], lw=1.4,
                    ls="--", alpha=0.75, zorder=2)
            q = vote_fail(p_bit, VOTE_SHOTS)
            ax.plot(big, (1 - q) ** big, color=cols[i], lw=2.2, zorder=3)
            ax.scatter(NS, d["exact"], s=22, color=cols[i], alpha=0.7,
                       zorder=4)
            ax.scatter(NS, d["vote"], s=30, marker="s", color=cols[i],
                       zorder=4)
        ax.axhline(0.5, color=ink["muted"], lw=1.0, ls=":")
        ax.text(3, 0.53, "coin flip", color=ink["muted"], fontsize=8.5,
                style="italic")
        ax.set_xscale("log")
        ax.set_xlim(2, 200)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel("secret length n (log)")
        ax.set_ylabel("probability the secret is recovered")
        ax.set_title(f"dashed: one shot     solid: majority vote "
                     f"({VOTE_SHOTS} shots)")

        fig.suptitle("Bernstein–Vazirani wants n bits out — which costs "
                     "shots, not fidelity",
                     color=ink["secondary"], fontsize=10.5, y=1.02)
        fig.tight_layout()
        suffix = "-dark" if mode == "dark" else ""
        out = ROOT / OUT / f"fig-readout{suffix}.svg"
        fig.savefig(out, transparent=True, bbox_inches="tight")
        plt.close(fig)
        print(f"  {out.relative_to(ROOT)}")


if __name__ == "__main__":
    print("BV readout figures:")
    main()
