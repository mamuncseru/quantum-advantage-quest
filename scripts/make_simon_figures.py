"""Figures for autopsy 03 (Simon).

fig-attack   : the separation appears and disappears with the ORACLE.
               A linear oracle (what hardware demos build) falls to a
               classical attacker in n queries; a genuinely random 2-to-1
               table costs the birthday bound. Both measured.
fig-fragility: why Simon breaks differently. Its answer needs n-1
               equations of n bits each, so success decays with n^2 while
               Deutsch-Jozsa and Bernstein-Vazirani decay with n.

Run from repo root:  .venv/bin/python scripts/make_simon_figures.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "predecessors/03-simon"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from simon import make_simon_function  # noqa: E402
from simon_classical_attack import (birthday_hunt, break_linear,  # noqa: E402
                                    linear_simon_oracle)
from simon_on_hardware import (clean_fraction, collect_samples,  # noqa: E402
                               naive_solve, s_int)
from qsim.noise import MachineNoise  # noqa: E402

INK = {
    "light": dict(secondary="#52514e", muted="#898781", grid="#e1e0d9",
                  axis="#c3c2b7"),
    "dark": dict(secondary="#c3c2b7", muted="#898781", grid="#2c2c2a",
                 axis="#383835"),
}
SERIES = {
    "light": ["#2a78d6", "#eda100", "#1baf7a", "#e34948"],
    "dark": ["#3987e5", "#c98500", "#199e70", "#e66767"],
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


# ------------------------------------------------------------- attack ----

def attack_data():
    lin_ns = [4, 6, 8, 10, 12, 14, 16, 18, 20]
    lin_q = []
    for n in lin_ns:
        s_true = (1 << (n - 1)) | 0b1011
        _, q = break_linear(linear_simon_oracle(s_true, n), n)
        lin_q.append(q)
    rnd_ns = [4, 6, 8, 10, 12, 14]
    rnd_q = []
    rng = np.random.default_rng(3)
    for n in rnd_ns:
        qs = []
        for t in range(25):
            f = make_simon_function(int(rng.integers(1, 2 ** n)), n,
                                    np.random.default_rng(100 + t))
            _, q = birthday_hunt(f, n, rng)
            qs.append(q)
        rnd_q.append(float(np.median(qs)))
        print(f"  random table n={n}: median {rnd_q[-1]:.0f} queries")
    return lin_ns, lin_q, rnd_ns, rnd_q


def fig_attack(data):
    lin_ns, lin_q, rnd_ns, rnd_q = data
    for mode in ("light", "dark"):
        ink, cols = INK[mode], SERIES[mode]
        fig, ax = plt.subplots(figsize=(6.6, 3.9))
        fig.patch.set_alpha(0.0)
        new_ax(ax, ink)
        grid = np.arange(4, 41)
        ax.plot(grid, 2 ** (grid / 2), color=cols[1], lw=1.5, ls="--",
                zorder=2)
        ax.scatter(rnd_ns, rnd_q, s=40, color=cols[1], zorder=4,
                   label="random 2-to-1 table (the real promise)")
        ax.plot(grid, grid, color=cols[0], lw=1.5, ls="--", zorder=2)
        ax.scatter(lin_ns, lin_q, s=40, color=cols[0], zorder=4,
                   label="linear oracle (what demos build)")
        ax.plot(grid, 4 * grid, color=cols[2], lw=1.8, zorder=3,
                label="quantum, either oracle  ~O(n)")
        ax.set_yscale("log")
        ax.set_xlim(4, 40)
        ax.set_ylim(1, 1e6)
        ax.set_xlabel("secret length n")
        ax.set_ylabel("queries to recover s (log)")
        ax.set_title("The separation lives in the oracle, not the circuit")
        ax.annotate("no separation\nleft here", (20, 20),
                    xytext=(23, 3), color=cols[0], fontsize=8.5,
                    arrowprops=dict(arrowstyle="->", color=cols[0], lw=0.9))
        leg = ax.legend(frameon=False, fontsize=8, loc="upper left")
        for t in leg.get_texts():
            t.set_color(ink["secondary"])
        fig.tight_layout()
        suffix = "-dark" if mode == "dark" else ""
        out = ROOT / OUT / f"fig-attack{suffix}.svg"
        fig.savefig(out, transparent=True, bbox_inches="tight")
        plt.close(fig)
        print(f"  {out.relative_to(ROOT)}")


# ---------------------------------------------------------- fragility ----

def fragility_data():
    ns = [3, 4, 5, 6]
    out = {}
    for mid in ("ibm-heron-r2", "rigetti-ankaa-3"):
        nz = MachineNoise.from_catalog(mid)
        clean, solved = [], []
        for n in ns:
            s_bits = [1] + [(i % 2) for i in range(n - 1)]
            s = s_int(s_bits, n)
            ys = collect_samples(n, s_bits, nz, shots=160, seed=21 + n)
            clean.append(clean_fraction(ys, s))
            trials, ok = 20, 0
            for t in range(trials):
                blk = collect_samples(n, s_bits, nz, shots=4 * n,
                                      seed=700 + 13 * n + t)
                ok += (naive_solve(blk, n) == s)
            solved.append(ok / trials)
        out[nz.label] = dict(noise=nz, clean=clean, solved=solved)
        print(f"  {nz.label}: clean={[round(c,3) for c in clean]} "
              f"solved={[round(v,2) for v in solved]}")
    return ns, out


def fig_fragility(data):
    ns, out = data
    for mode in ("light", "dark"):
        ink, cols = INK[mode], SERIES[mode]
        fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.7))
        fig.patch.set_alpha(0.0)
        for ax in axes:
            new_ax(ax, ink)

        ax = axes[0]
        for i, (label, d) in enumerate(out.items()):
            ax.scatter(ns, d["clean"], s=34, color=cols[i], zorder=3,
                       label=label)
            ax.plot(ns, [c ** (n - 1) for c, n in zip(d["clean"], ns)],
                    color=cols[i], lw=1.8, marker="s", ms=4, zorder=3)
            ax.scatter(ns, d["solved"], s=30, marker="^", color=cols[i],
                       alpha=0.65, zorder=3)
        ax.set_ylim(0.4, 1.03)
        ax.set_xticks(ns)
        ax.set_xlabel("secret length n")
        ax.set_ylabel("probability")
        ax.set_title("● one clean equation   ■ all n−1 clean   "
                     "▲ textbook solve")
        leg = ax.legend(frameon=False, fontsize=8, loc="lower left")
        for t in leg.get_texts():
            t.set_color(ink["secondary"])

        ax = axes[1]
        nz = list(out.values())[0]["noise"]
        e1, ro = nz.err_1q, nz.readout
        g = np.arange(2, 60)
        one_shot = (1 - ro) ** g * (1 - e1) ** (2 * g + 2)
        p_clean = 1 - (1 - (1 - ro) ** g) / 2
        simon = p_clean ** (g - 1)
        ax.plot(g, np.ones_like(g) * 1.0, color=cols[2], lw=2.0,
                label="Deutsch–Jozsa: 1 bit, as a statistic")
        ax.plot(g, one_shot, color=cols[0], lw=2.0,
                label="Bernstein–Vazirani: n bits, one shot")
        ax.plot(g, simon, color=cols[3], lw=2.2,
                label="Simon: n−1 equations, all clean")
        ax.axhline(0.5, color=ink["muted"], lw=1.0, ls=":")
        ax.text(3, 0.53, "coin flip", color=ink["muted"], fontsize=8.5,
                style="italic")
        ax.set_xlim(2, 58)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel("problem size n")
        ax.set_ylabel("probability the answer is right")
        ax.set_title(f"the fragility ladder ({nz.label} error rates)")
        leg = ax.legend(frameon=False, fontsize=7.6, loc="lower right")
        for t in leg.get_texts():
            t.set_color(ink["secondary"])

        fig.suptitle("Simon asks for n² bits of structured output — and "
                     "linear algebra has no notion of “mostly right”",
                     color=ink["secondary"], fontsize=10.5, y=1.03)
        fig.tight_layout()
        suffix = "-dark" if mode == "dark" else ""
        o = ROOT / OUT / f"fig-fragility{suffix}.svg"
        fig.savefig(o, transparent=True, bbox_inches="tight")
        plt.close(fig)
        print(f"  {o.relative_to(ROOT)}")


if __name__ == "__main__":
    print("Simon figures:")
    fig_attack(attack_data())
    fig_fragility(fragility_data())
