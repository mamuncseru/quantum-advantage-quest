"""C1 atlas: Davies-generator spectral gap and Gibbs-state entanglement
across (field strength h, inverse temperature beta) for three field profiles.

Purpose (see hunt/C1-fields-and-mixers.md): locate, at small n, where
(quantum mixer keeps a gap) AND (the state develops entanglement / leaves
the easy classical regime). Conjecture-formers only — n = 5 exact numerics
headline nothing.

Profiles on a Heisenberg chain H0 = sum_i (XX + YY + ZZ):
  uniform        h * sum_i Z_i
  quasiperiodic  h * sum_i cos(2 pi alpha i + 0.3) Z_i,  alpha = golden ratio
  random         h * sum_i eps_i Z_i,  eps_i ~ U[-1, 1] (seeded)

Outputs: hunt/atlas-results.csv + hunt/fig-atlas-{gap,neg}[-dark].svg
Run from repo root: .venv/bin/python hunt/code/gibbs_atlas.py
"""

import importlib.util
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(ROOT))

from qsim import I2, X, Y, Z  # noqa: E402

spec = importlib.util.spec_from_file_location(
    "davies", ROOT / "predecessors/12-gibbs-lindblad/davies.py")
davies = importlib.util.module_from_spec(spec)
spec.loader.exec_module(davies)

N = 5
ALPHA = (np.sqrt(5) - 1) / 2
RNG = np.random.default_rng(11)
EPS = RNG.uniform(-1, 1, size=N)

PROFILES = {
    "uniform": np.ones(N),
    "quasiperiodic": np.cos(2 * np.pi * ALPHA * np.arange(N) + 0.3),
    "random": EPS,
}
BETAS = (0.25, 0.5, 1.0, 2.0)
HS = (0.0, 0.5, 1.0, 2.0, 4.0, 8.0)


def hamiltonian(profile, h):
    H = np.zeros((2 ** N, 2 ** N), dtype=complex)
    for i in range(N - 1):
        for P in (X, Y, Z):
            H += davies.site_op(P, i, N) @ davies.site_op(P, i + 1, N)
    for i in range(N):
        H += h * PROFILES[profile][i] * davies.site_op(Z, i, N)
    return H


def log_negativity(rho, cut=2):
    """log2 || rho^{T_A} ||_1 across qubits [0..cut-1] | [cut..N-1]."""
    dA, dB = 2 ** cut, 2 ** (N - cut)
    r = rho.reshape(dA, dB, dA, dB).transpose(2, 1, 0, 3).reshape(dA * dB,
                                                                  dA * dB)
    return float(np.log2(np.abs(np.linalg.svd(r, compute_uv=False)).sum()))


def atlas():
    couplings = [davies.site_op(X, i, N) for i in range(N)] + \
                [davies.site_op(Y, i, N) for i in range(N)]
    rows = []
    for profile in PROFILES:
        for beta in BETAS:
            for h in HS:
                H = hamiltonian(profile, h)
                L = davies.davies_superoperator(H, couplings, beta)
                gap = davies.spectral_gap(L)
                neg = log_negativity(davies.gibbs_state(H, beta))
                rows.append((profile, beta, h, gap, neg))
                print(f"{profile:14s} beta={beta:4.2f} h={h:4.1f} "
                      f"gap={gap:7.4f}  logneg={neg:7.4f}", flush=True)
    return rows


INK = {"light": dict(secondary="#52514e", muted="#898781", grid="#e1e0d9",
                     axis="#c3c2b7"),
       "dark": dict(secondary="#c3c2b7", muted="#898781", grid="#2c2c2a",
                    axis="#383835")}
SERIES = {"light": ["#2a78d6", "#1baf7a", "#eda100", "#008300"],
          "dark": ["#3987e5", "#199e70", "#c98500", "#008300"]}


def figure(rows, column, fname, ylabel, title, logy=False):
    data = {(p, b): [] for p in PROFILES for b in BETAS}
    for p, b, h, gap, neg in rows:
        data[(p, b)].append((h, gap if column == "gap" else neg))
    for mode in ("light", "dark"):
        ink, c = INK[mode], SERIES[mode]
        fig, axes = plt.subplots(1, 3, figsize=(10.5, 3.2), sharey=True)
        fig.patch.set_alpha(0.0)
        for ax, profile in zip(axes, PROFILES):
            ax.set_facecolor("none")
            for side in ("top", "right"):
                ax.spines[side].set_visible(False)
            for side in ("left", "bottom"):
                ax.spines[side].set_color(ink["axis"])
            ax.tick_params(colors=ink["muted"], labelsize=8)
            ax.grid(True, color=ink["grid"], linewidth=0.5)
            ax.set_axisbelow(True)
            for i, b in enumerate(BETAS):
                xy = data[(profile, b)]
                ax.plot([q[0] for q in xy], [q[1] for q in xy], color=c[i],
                        lw=1.8, marker="o", ms=4, zorder=3,
                        label=f"β = {b}")
            if logy:
                ax.set_yscale("log")
            ax.set_title(profile, fontsize=9, color=ink["secondary"])
            ax.set_xlabel("field strength h", fontsize=9,
                          color=ink["secondary"])
        axes[0].set_ylabel(ylabel, fontsize=9, color=ink["secondary"])
        leg = axes[-1].legend(frameon=False, fontsize=8)
        for t in leg.get_texts():
            t.set_color(ink["secondary"])
        fig.suptitle(title, fontsize=10, color=ink["secondary"])
        suffix = "-dark" if mode == "dark" else ""
        out = ROOT / "hunt" / f"{fname}{suffix}.svg"
        fig.savefig(out, transparent=True, bbox_inches="tight")
        plt.close(fig)
        print(out, flush=True)


if __name__ == "__main__":
    rows = atlas()
    with open(ROOT / "hunt" / "atlas-results.csv", "w") as fh:
        fh.write("profile,beta,h,davies_gap,log_negativity\n")
        for r in rows:
            fh.write(f"{r[0]},{r[1]},{r[2]},{r[3]:.6f},{r[4]:.6f}\n")
    figure(rows, "gap", "fig-atlas-gap", "Davies spectral gap",
           f"Quantum mixer gap vs field strength (n = {N} Heisenberg chain)",
           logy=True)
    figure(rows, "neg", "fig-atlas-neg", "log-negativity (2|3 cut)",
           f"Gibbs-state entanglement vs field strength (n = {N})")
    print("atlas done")
