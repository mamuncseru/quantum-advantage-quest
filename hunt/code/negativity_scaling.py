"""C1 follow-up: does field-induced entanglement survive as n grows, and
does the disorder ordering (random > quasiperiodic > uniform) persist under
disorder averaging? Gibbs-state log-negativity only (no Lindbladian here —
the 4^n superoperator is the expensive part; state negativity is 2^n).

Run from repo root: .venv/bin/python hunt/code/negativity_scaling.py
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

ALPHA = (np.sqrt(5) - 1) / 2
BETA, H = 2.0, 1.5          # the structure-rich point from the first atlas
SEEDS = 12


def hamiltonian(n, profile, seed):
    rng = np.random.default_rng(seed)
    if profile == "uniform":
        field = np.ones(n)
    elif profile == "quasiperiodic":
        field = np.cos(2 * np.pi * ALPHA * np.arange(n) + 0.3)
    else:
        field = rng.uniform(-1, 1, size=n)
    H0 = np.zeros((2 ** n, 2 ** n), dtype=complex)
    for i in range(n - 1):
        for P in (X, Y, Z):
            H0 += davies.site_op(P, i, n) @ davies.site_op(P, i + 1, n)
    for i in range(n):
        H0 += H * field[i] * davies.site_op(Z, i, n)
    return H0


def log_negativity(rho, n):
    cut = n // 2
    dA, dB = 2 ** cut, 2 ** (n - cut)
    r = rho.reshape(dA, dB, dA, dB).transpose(2, 1, 0, 3).reshape(dA * dB,
                                                                  dA * dB)
    return float(np.log2(np.abs(np.linalg.svd(r, compute_uv=False)).sum()))


def run():
    profiles = ("uniform", "quasiperiodic", "random")
    ns = range(3, 9)
    results = {p: [] for p in profiles}
    for p in profiles:
        for n in ns:
            vals = []
            reps = SEEDS if p == "random" else 1
            for s in range(reps):
                rho = davies.gibbs_state(hamiltonian(n, p, s), BETA)
                vals.append(log_negativity(rho, n))
            results[p].append((n, float(np.mean(vals)), float(np.std(vals))))
            print(f"{p:14s} n={n} logneg={np.mean(vals):.4f} "
                  f"+/-{np.std(vals):.4f}", flush=True)
    return list(ns), results


INK = {"light": dict(sec="#52514e", mut="#898781", grid="#e1e0d9", ax="#c3c2b7"),
       "dark": dict(sec="#c3c2b7", mut="#898781", grid="#2c2c2a", ax="#383835")}
SER = {"light": ["#eda100", "#1baf7a", "#2a78d6"],
       "dark": ["#c98500", "#199e70", "#3987e5"]}


def figure(ns, results):
    order = ["uniform", "quasiperiodic", "random"]
    for mode in ("light", "dark"):
        ink, c = INK[mode], SER[mode]
        fig, ax = plt.subplots(figsize=(7.0, 3.8))
        fig.patch.set_alpha(0.0)
        ax.set_facecolor("none")
        for s in ("top", "right"):
            ax.spines[s].set_visible(False)
        for s in ("left", "bottom"):
            ax.spines[s].set_color(ink["ax"])
        ax.tick_params(colors=ink["mut"], labelsize=9)
        ax.grid(True, color=ink["grid"], lw=0.6)
        ax.set_axisbelow(True)
        for i, p in enumerate(order):
            xs = [r[0] for r in results[p]]
            ys = [r[1] for r in results[p]]
            es = [r[2] for r in results[p]]
            ax.errorbar(xs, ys, yerr=es, color=c[i], lw=2, marker="o", ms=5,
                        capsize=3, zorder=3, label=p)
        leg = ax.legend(frameon=False, fontsize=9)
        for t in leg.get_texts():
            t.set_color(ink["sec"])
        ax.set_xlabel(f"chain length n   (β = {BETA}, h = {H}, half-chain cut)",
                      color=ink["sec"], fontsize=10)
        ax.set_ylabel("log-negativity", color=ink["sec"], fontsize=10)
        ax.set_title("Field-induced Gibbs entanglement vs system size "
                     "(random: 12-seed average)", color=ink["sec"], fontsize=10)
        out = ROOT / "hunt" / f"fig-negscale{'-dark' if mode == 'dark' else ''}.svg"
        fig.savefig(out, transparent=True, bbox_inches="tight")
        plt.close(fig)
        print(out, flush=True)


if __name__ == "__main__":
    ns, results = run()
    with open(ROOT / "hunt" / "negscale-results.csv", "w") as fh:
        fh.write("profile,n,logneg_mean,logneg_std\n")
        for p in results:
            for n, mean, std in results[p]:
                fh.write(f"{p},{n},{mean:.6f},{std:.6f}\n")
    figure(ns, results)
    print("negscale done")
