"""Figures for autopsy 04 (Shor).

fig-cost  : the famous algorithm priced against the machines that exist.
            Shor on N = 15 needs more two-qubit gates than any machine's
            entire error budget allows -- on 13 qubits.
fig-cheat : why every demonstration factors 15. The controlled-U cascade
            collapses exactly when the order is a power of two, and for
            N = 15 that is true for every choice of a.

Run from repo root:  .venv/bin/python scripts/make_shor_figures.py
"""

import sys
from math import gcd
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "predecessors/04-shor"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from shor_compiled_cheat import (is_power_of_two, order,  # noqa: E402
                                 nontrivial_gates, survey, units)
from shor_resources import arithmetic_cost, circuit_shape  # noqa: E402
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
MACHINES = ["quantinuum-helios", "quantinuum-h2", "ionq-forte",
            "google-willow", "ustc-zuchongzhi-3", "ibm-heron-r2",
            "rigetti-ankaa-3"]


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


def fig_cost():
    budgets = []
    for mid in MACHINES:
        nz = MachineNoise.from_catalog(mid)
        budgets.append((nz.label, 1.0 / nz.err_2q))
    budgets.sort(key=lambda p: p[1])
    need15 = arithmetic_cost(15)["cnot"]

    for mode in ("light", "dark"):
        ink, cols = INK[mode], SERIES[mode]
        fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.9))
        fig.patch.set_alpha(0.0)
        for ax in axes:
            new_ax(ax, ink)

        ax = axes[0]
        names = [b[0] for b in budgets]
        vals = [b[1] for b in budgets]
        ax.barh(range(len(vals)), vals, height=0.62, color=cols[0],
                zorder=3)
        ax.axvline(need15, color=cols[3], lw=2.0, zorder=4)
        ax.text(need15 * 1.15, 0.2, f"Shor on N = 15\nneeds {need15:,}",
                color=cols[3], fontsize=8.5, va="bottom")
        ax.set_yticks(range(len(names)), names, fontsize=8)
        ax.set_xscale("log")
        ax.set_xlim(50, 3e4)
        ax.set_xlabel("two-qubit gates before the first error  (1/ε)")
        ax.set_title("every machine's entire error budget, vs one job")

        ax = axes[1]
        bits = np.array([4, 6, 8, 11, 16, 32, 64, 128, 256, 512, 1024, 2048])
        need = [arithmetic_cost(bits=int(b))["cnot"] for b in bits]
        ax.plot(bits, need, color=cols[0], lw=2.0, marker="o", ms=4,
                zorder=3, label="schoolbook model (this repo)")
        ax.scatter([2048], [2.7e9 * 6], s=60, marker="*", color=cols[2],
                   zorder=4, label="Gidney–Ekerå 2019 (windowed)")
        best = max(v for _, v in budgets)
        ax.axhline(best, color=cols[3], lw=1.6, ls="--", zorder=2)
        ax.text(5, best * 1.5, "best machine budget today",
                color=cols[3], fontsize=8.5)
        ax.set_xscale("log")
        ax.set_yscale("log")
        ax.set_xlabel("modulus size (bits, log)")
        ax.set_ylabel("two-qubit gates required (log)")
        ax.set_title("the gap does not close by being patient")
        leg = ax.legend(frameon=False, fontsize=8, loc="upper left")
        for t in leg.get_texts():
            t.set_color(ink["secondary"])

        fig.suptitle("Shor's algorithm, priced against the machines that "
                     "exist", color=ink["secondary"], fontsize=10.5,
                     y=1.03)
        fig.tight_layout()
        suffix = "-dark" if mode == "dark" else ""
        out = ROOT / OUT / f"fig-cost{suffix}.svg"
        fig.savefig(out, transparent=True, bbox_inches="tight")
        plt.close(fig)
        print(f"  {out.relative_to(ROOT)}")


def collapse_fraction(N):
    us = units(N)
    if not us:
        return 0.0
    return sum(1 for a in us if is_power_of_two(order(a, N))) / len(us)


FERMAT = {3, 5, 17, 257, 65537}


def is_fermat_product(N):
    """N a product of DISTINCT Fermat primes <=> lambda(N) is a power of
    two <=> every base has power-of-two order <=> every cascade
    collapses. 15 = 3x5 is merely the smallest such semiprime."""
    m, fs = N, set()
    for p in sorted(FERMAT):
        if m % p == 0:
            m //= p
            fs.add(p)
    return m == 1 and len(fs) >= 2


def fig_cheat():
    Ns = [15, 21, 33, 35, 39, 51, 55, 57, 65, 77, 85, 91, 95, 115, 119]
    fracs = [collapse_fraction(N) for N in Ns]
    for mode in ("light", "dark"):
        ink, cols = INK[mode], SERIES[mode]
        fig, axes = plt.subplots(1, 2, figsize=(9.6, 3.8))
        fig.patch.set_alpha(0.0)
        for ax in axes:
            new_ax(ax, ink)

        ax = axes[0]
        for i, N in enumerate((15, 21, 35)):
            t, rows = survey(N)
            xs = [r["a"] for r in rows]
            ys = [r["gates"] for r in rows]
            colr = [cols[2] if r["collapses"] else cols[1] for r in rows]
            ax.scatter([i + 0.06 * (k - len(xs) / 2) for k in range(len(xs))],
                       ys, s=34, c=colr, zorder=3)
            ax.plot([i - 0.45, i + 0.45], [t, t], color=ink["muted"],
                    lw=1.2, ls=":", zorder=2)
            ax.text(i, t + 0.6, f"honest: {t}", ha="center",
                    color=ink["muted"], fontsize=8)
        ax.set_xticks([0, 1, 2], ["N = 15", "N = 21", "N = 35"])
        ax.set_ylim(0, 16)
        ax.set_ylabel("non-trivial controlled-U gates")
        ax.set_title("green = cascade collapses (order is a power of 2)")

        ax = axes[1]
        colr = [cols[3] if is_fermat_product(N) else cols[0] for N in Ns]
        ax.bar(range(len(Ns)), [100 * f for f in fracs], color=colr,
               zorder=3, width=0.66)
        labels = [f"{n}*" if is_fermat_product(n) else str(n) for n in Ns]
        ax.set_xticks(range(len(Ns)), labels, fontsize=7.6, rotation=45)
        ax.set_ylim(0, 118)
        ax.set_xlabel("N (odd semiprimes)   * = product of Fermat primes")
        ax.set_ylabel("% of bases a whose cascade collapses")
        ax.set_title("100% exactly when N = product of Fermat primes")
        ax.annotate("15 = 3×5, 51 = 3×17, 85 = 5×17\n"
                    "— every base is easy here,\nand 15 is the smallest",
                    (0, 100), xytext=(3.0, 52), color=cols[3],
                    fontsize=8.2,
                    arrowprops=dict(arrowstyle="->", color=cols[3], lw=1.0))

        fig.suptitle("Compiled demonstrations: the circuit shrinks exactly "
                     "when you already know the order",
                     color=ink["secondary"], fontsize=10.5, y=1.03)
        fig.tight_layout()
        suffix = "-dark" if mode == "dark" else ""
        out = ROOT / OUT / f"fig-cheat{suffix}.svg"
        fig.savefig(out, transparent=True, bbox_inches="tight")
        plt.close(fig)
        print(f"  {out.relative_to(ROOT)}")


if __name__ == "__main__":
    print("Shor figures:")
    fig_cost()
    fig_cheat()
