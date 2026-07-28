"""Figures for autopsy 01 (Deutsch-Jozsa), section 7: what a real machine
gives you.

Generates machines-catalog-style light/dark SVG pairs next to the autopsy
from ACTUAL noisy runs of the compiled circuit (predecessors/01-.../
dj_on_hardware.py) at published error rates (machines/data.yml).

Run from repo root:  .venv/bin/python scripts/make_dj_figures.py
"""

import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
OUT = "predecessors/01-deutsch-jozsa"
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / OUT))

from dj_on_hardware import run_dj  # noqa: E402
from qsim.noise import MachineNoise  # noqa: E402

INK = {
    "light": dict(primary="#0b0b0b", secondary="#52514e", muted="#898781",
                  grid="#e1e0d9", axis="#c3c2b7"),
    "dark": dict(primary="#ffffff", secondary="#c3c2b7", muted="#898781",
                 grid="#2c2c2a", axis="#383835"),
}
SERIES = {
    "light": ["#2a78d6", "#1baf7a", "#eda100", "#e34948"],
    "dark": ["#3987e5", "#199e70", "#c98500", "#e66767"],
}

SHOWN = ["quantinuum-helios", "ibm-heron-r2", "rigetti-ankaa-3"]


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


def margin_model(noise, n):
    """Analytic decision margin: the constant branch keeps its 2n+2
    single-qubit gates and n readouts; the balanced branch contributes
    nothing to P(0...0) (its output is the deterministic string |s>)."""
    return ((1 - noise.err_1q) ** (2 * n + 2)) * ((1 - noise.readout) ** n)


def crossing(noise):
    n = np.arange(1, 5000)
    m = margin_model(noise, n)
    idx = np.argmax(m < 0.5)
    return int(n[idx]) if idx else None


def measure(noise, ns, shots):
    return [run_dj(n, 0, noise, shots=shots, seed=100 + n) -
            run_dj(n, (1 << n) - 1, noise, shots=shots, seed=200 + n)
            for n in ns]


def main():
    ns = [2, 4, 6, 8, 10, 12]
    shots = 400
    noises = [MachineNoise.from_catalog(m) for m in SHOWN]
    measured = {}
    for nz in noises:
        measured[nz.label] = measure(nz, ns, shots)
        print(f"  measured {nz.label}: "
              f"{[round(v, 3) for v in measured[nz.label]]}")

    for mode in ("light", "dark"):
        ink, cols = INK[mode], SERIES[mode]
        fig, axes = plt.subplots(1, 2, figsize=(9.4, 3.7))
        fig.patch.set_alpha(0.0)
        for ax in axes:
            new_ax(ax, ink)

        ax = axes[0]
        grid = np.linspace(2, 13, 60)
        for i, nz in enumerate(noises):
            ax.plot(grid, margin_model(nz, grid), color=cols[i], lw=1.6,
                    zorder=2)
            ax.scatter(ns, measured[nz.label], s=34, color=cols[i],
                       zorder=3, label=nz.label)
        ax.set_ylim(0.55, 1.02)
        ax.set_xlabel("input qubits n")
        ax.set_ylabel("decision margin")
        ax.set_title("simulated runs vs the error model")
        leg = ax.legend(frameon=False, fontsize=8, loc="lower left")
        for t in leg.get_texts():
            t.set_color(ink["secondary"])

        ax = axes[1]
        grid = np.arange(1, 3000)
        for i, nz in enumerate(noises):
            ax.plot(grid, margin_model(nz, grid), color=cols[i], lw=1.6,
                    zorder=2)
            x = crossing(nz)
            if x:
                ax.scatter([x], [0.5], s=40, marker="v", color=cols[i],
                           zorder=4)
                far = x > 500
                ax.annotate(f"{nz.label.split()[0]}  n≈{x}", (x, 0.5),
                            xytext=(-9, 14) if far else (0, -16 - 12 * i),
                            textcoords="offset points",
                            ha="right" if far else "center",
                            color=cols[i], fontsize=8.5)
        ax.axhline(0.5, color=ink["muted"], lw=1.0, ls=":")
        ax.text(1.3, 0.53, "decision breaks", color=ink["muted"],
                fontsize=8.5, style="italic")
        ax.set_xscale("log")
        ax.set_xlim(1, 3000)
        ax.set_ylim(0, 1.05)
        ax.set_xlabel("input qubits n (log)")
        ax.set_ylabel("decision margin")
        ax.set_title("extrapolated: where the answer stops being readable")

        fig.suptitle("Deutsch–Jozsa on real error rates — the margin is "
                     "eaten by readout, not by gates",
                     color=ink["secondary"], fontsize=10.5, y=1.02)
        fig.tight_layout()
        suffix = "-dark" if mode == "dark" else ""
        out = ROOT / OUT / f"fig-hardware{suffix}.svg"
        fig.savefig(out, transparent=True, bbox_inches="tight")
        plt.close(fig)
        print(f"  {out.relative_to(ROOT)}")


if __name__ == "__main__":
    print("DJ hardware figures:")
    main()
