"""Generate every documentation figure from the actual implementations.

Each figure renders twice (light/dark) as transparent SVGs, saved next to
the autopsy that embeds it. Colors follow a validated categorical palette;
marks are thin, grids hairline, text in ink tones.

Run from repo root:  .venv/bin/python scripts/make_figures.py
"""

import importlib.util
import sys
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from qsim import H, amplitudes, apply, phase_oracle, sample, zero_state  # noqa: E402

INK = {
    "light": dict(primary="#0b0b0b", secondary="#52514e", muted="#898781",
                  grid="#e1e0d9", axis="#c3c2b7"),
    "dark": dict(primary="#ffffff", secondary="#c3c2b7", muted="#898781",
                 grid="#2c2c2a", axis="#383835"),
}
SERIES = {
    "light": ["#2a78d6", "#1baf7a", "#eda100", "#008300"],
    "dark": ["#3987e5", "#199e70", "#c98500", "#008300"],
}


def load(relpath, name):
    spec = importlib.util.spec_from_file_location(name, ROOT / relpath)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def new_fig(mode, figsize=(7.0, 3.6)):
    ink = INK[mode]
    fig, ax = plt.subplots(figsize=figsize)
    fig.patch.set_alpha(0.0)
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
    return fig, ax


def save(fig, directory, stem, mode):
    suffix = "-dark" if mode == "dark" else ""
    out = ROOT / directory / f"{stem}{suffix}.svg"
    fig.savefig(out, transparent=True, bbox_inches="tight")
    plt.close(fig)
    print(f"  {out.relative_to(ROOT)}")


# ------------------------------------------------------------------ 01 DJ --

def fig_dj():
    dj = load("predecessors/01-deutsch-jozsa/deutsch_jozsa.py", "dj")
    n = 10
    cases = [
        ("f = 0", lambda x: 0), ("f = 1", lambda x: 1),
        ("parity", lambda x: bin(x).count("1") & 1),
        ("top bit", lambda x: (x >> (n - 1)) & 1),
        ("AND\n(no promise)", lambda x: ((x >> (n - 1)) & (x >> (n - 2))) & 1),
    ]
    vals = [dj.dj_p0(phase_oracle(f, n), n) for _, f in cases]
    for mode in ("light", "dark"):
        ink, c = INK[mode], SERIES[mode]
        fig, ax = new_fig(mode, (6.4, 3.3))
        colors = [c[0]] * 4 + [c[2]]
        bars = ax.bar(range(5), vals, width=0.55, color=colors, zorder=3)
        for b, v in zip(bars, vals):
            ax.text(b.get_x() + b.get_width() / 2, v + 0.03, f"{v:.2f}",
                    ha="center", color=ink["secondary"], fontsize=9)
        ax.set_xticks(range(5), [c0 for c0, _ in cases])
        ax.set_ylim(0, 1.12)
        ax.set_ylabel("P(measure |0…0⟩)")
        ax.set_title("One query, one global property — constant f ⇒ 1, balanced f ⇒ 0")
        save(fig, "predecessors/01-deutsch-jozsa", "fig-interference", mode)


# ------------------------------------------------------------------ 02 BV --

def fig_bv():
    n, s = 4, 0b1011
    f = lambda x: bin(x & s).count("1") & 1
    psi = zero_state(n)
    for q in range(n):
        psi = apply(psi, H, [q])
    psi = apply(psi, phase_oracle(f, n), list(range(n)))
    for q in range(n):
        psi = apply(psi, H, [q])
    p = np.abs(amplitudes(psi)) ** 2
    for mode in ("light", "dark"):
        ink, c = INK[mode], SERIES[mode]
        fig, ax = new_fig(mode, (6.4, 3.0))
        ax.bar(range(16), p, width=0.55, color=c[0], zorder=3)
        ax.set_xticks(range(16), [f"{i:04b}" for i in range(16)],
                      rotation=60, fontsize=7.5)
        ax.set_ylabel("probability")
        ax.set_title("After one query, ALL amplitude sits on the secret s = 1011")
        ax.annotate("s", (11, p[11]), xytext=(11, p[11] - 0.15),
                    ha="center", color=ink["primary"], fontsize=11)
        save(fig, "predecessors/02-bernstein-vazirani", "fig-delta", mode)


# --------------------------------------------------------------- 03 Simon --

def fig_simon():
    simon = load("predecessors/03-simon/simon.py", "simon_mod")
    rng = np.random.default_rng(1)
    n, s = 4, 0b1011
    f = simon.make_simon_function(s, n, rng)
    oracle = simon.function_oracle(f, n, n)
    psi = zero_state(2 * n)
    for q in range(n):
        psi = apply(psi, H, [q])
    psi = apply(psi, oracle, list(range(2 * n)))
    for q in range(n):
        psi = apply(psi, H, [q])
    shots = sample(psi, shots=4000, qubits=range(n), seed=5)
    freq = np.zeros(16)
    for b in shots:
        freq[int(b, 2)] += 1
    freq /= freq.sum()
    ortho = [y for y in range(16) if bin(y & s).count("1") % 2 == 0]
    for mode in ("light", "dark"):
        ink, c = INK[mode], SERIES[mode]
        fig, ax = new_fig(mode, (6.4, 3.0))
        colors = [c[0] if y in ortho else c[2] for y in range(16)]
        ax.bar(range(16), freq, width=0.55, color=colors, zorder=3)
        ax.axhline(1 / 8, color=ink["muted"], lw=1, ls=(0, (4, 3)))
        ax.text(15.4, 1 / 8, "1/8", va="center", color=ink["muted"], fontsize=8)
        ax.set_xticks(range(16), [f"{i:04b}" for i in range(16)],
                      rotation=60, fontsize=7.5)
        ax.set_ylabel("frequency (4000 runs)")
        ax.set_title("Every sample obeys y·s = 0 — the answer hides in a subspace")
        save(fig, "predecessors/03-simon", "fig-subspace", mode)


# ---------------------------------------------------------------- 04 Shor --

def fig_shor():
    shor = load("predecessors/04-shor/shor.py", "shor_mod")
    psi, t = shor.order_finding_state(7, 15)
    m = psi.ndim - t
    p = (np.abs(amplitudes(psi)) ** 2).reshape(2 ** t, 2 ** m).sum(axis=1)
    for mode in ("light", "dark"):
        ink, c = INK[mode], SERIES[mode]
        fig, ax = new_fig(mode, (7.2, 3.4))
        ax.plot(range(2 ** t), p, color=c[0], lw=1.6, zorder=3)
        ax.set_ylim(0, 0.33)
        for k in range(4):
            ck = k * 2 ** t // 4
            ax.annotate(f"k/r = {k}/4", (ck, 0.255), xytext=(ck + 7, 0.27),
                        color=ink["secondary"], fontsize=9)
        ax.set_xlabel("counting-register outcome c   (t = 9 qubits, N = 15, a = 7)")
        ax.set_ylabel("probability")
        ax.set_title("The order r = 4 appears as interference peaks at c ≈ k·2ᵗ/r")
        save(fig, "predecessors/04-shor", "fig-spectrum", mode)


# -------------------------------------------------------------- 06 Grover --

def fig_grover():
    grover = load("predecessors/06-grover/grover.py", "grover_mod")
    n, kmax = 8, 30
    curve = grover.success_curve(n, 0, kmax)
    kopt = int(np.floor(np.pi / 4 * np.sqrt(2 ** n)))
    for mode in ("light", "dark"):
        ink, c = INK[mode], SERIES[mode]
        fig, ax = new_fig(mode)
        ax.plot(range(kmax + 1), curve, color=c[0], lw=2, zorder=3)
        ax.plot([kopt], [curve[kopt]], "o", ms=8, color=c[1], zorder=4)
        ax.annotate(f"optimal k = {kopt}\np = {curve[kopt]:.3f}",
                    (kopt, curve[kopt]), xytext=(kopt + 1.2, 0.86),
                    color=ink["secondary"], fontsize=9)
        ax.plot([2 * kopt], [curve[2 * kopt]], "o", ms=8, color=c[2], zorder=4)
        ax.annotate(f"2k = {2*kopt}: overshoot\np = {curve[2*kopt]:.2f}",
                    (2 * kopt, curve[2 * kopt]),
                    xytext=(2 * kopt - 8.5, 0.18),
                    color=ink["secondary"], fontsize=9)
        ax.set_xlabel("Grover iterations k   (n = 8, N = 256)")
        ax.set_ylabel("success probability")
        ax.set_title("A rotation, not a ratchet: sin²((2k+1)θ) — more queries can be worse")
        save(fig, "predecessors/06-grover", "fig-rotation", mode)


# --------------------------------------------------------------- 07 walks --

def fig_walks():
    gt = load("predecessors/07-quantum-walks/glued_trees.py", "gt")
    ds = list(range(4, 25, 2))
    pq = [gt.quantum_exit_prob(d)[0] for d in ds]
    pc = [gt.classical_exit_prob(d, d ** 3) for d in ds]
    for mode in ("light", "dark"):
        ink, c = INK[mode], SERIES[mode]
        fig, ax = new_fig(mode)
        ax.semilogy(ds, pq, color=c[0], lw=2, marker="o", ms=5, zorder=3)
        ax.semilogy(ds, pc, color=c[2], lw=2, marker="o", ms=5, zorder=3)
        ax.text(ds[-1] + 0.4, pq[-1], "quantum walk\n(time ≈ 0.8·d)",
                color=ink["secondary"], fontsize=9, va="center")
        ax.text(ds[-1] + 0.4, pc[-1], "classical walk\n(d³ steps allowed)",
                color=ink["secondary"], fontsize=9, va="center")
        ax.set_xlim(3, 33)
        ax.set_xlabel("tree depth d   (graph has ~2^(d+2) vertices)")
        ax.set_ylabel("P(reach exit)")
        ax.set_title("Ballistic beats diffusive: the separation grows exponentially")
        save(fig, "predecessors/07-quantum-walks", "fig-separation", mode)


# ------------------------------------------------------------- 08 Trotter --

def fig_trotter():
    tr = load("predecessors/08-hamiltonian-simulation/trotter.py", "tr")
    steps = (4, 8, 16, 32, 64)
    A, B = tr.tfim(6)
    e1 = [tr.trotter_error(A, B, 1.0, n, 1) for n in steps]
    e2 = [tr.trotter_error(A, B, 1.0, n, 2) for n in steps]
    for mode in ("light", "dark"):
        ink, c = INK[mode], SERIES[mode]
        fig, ax = new_fig(mode)
        ax.loglog(steps, e1, color=c[0], lw=2, marker="o", ms=5, zorder=3)
        ax.loglog(steps, e2, color=c[1], lw=2, marker="o", ms=5, zorder=3)
        ax.text(steps[-1] * 1.15, e1[-1], "1st order ~ n⁻¹",
                color=ink["secondary"], fontsize=9, va="center")
        ax.text(steps[-1] * 1.15, e2[-1], "2nd order ~ n⁻²",
                color=ink["secondary"], fontsize=9, va="center")
        ax.set_xlim(3, 260)
        ax.set_xlabel("Trotter steps n   (TFIM, 6 qubits, t = 1)")
        ax.set_ylabel("‖U_trotter − U_exact‖₂")
        ax.set_title("Measured error slopes match the commutator bounds")
        save(fig, "predecessors/08-hamiltonian-simulation", "fig-slopes", mode)


# ---------------------------------------------------------------- 09 QSVT --

def fig_qsvt():
    x = np.linspace(-1, 1, 400)
    for mode in ("light", "dark"):
        ink, c = INK[mode], SERIES[mode]
        fig, ax = new_fig(mode)
        for d in range(1, 5):
            ax.plot(x, np.cos(d * np.arccos(x)), color=c[d - 1], lw=2, zorder=3)
            xl = {1: 0.62, 2: 0.05, 3: -0.52, 4: -0.80}[d]
            yv = np.cos(d * np.arccos(xl))
            ax.annotate(f"T{d}", (xl, yv), xytext=(xl, yv + 0.13),
                        ha="center", color=ink["secondary"], fontsize=10)
        ax.set_xlabel("eigenvalue λ of the block-encoded A")
        ax.set_ylabel("top-left block of Wᵈ")
        ax.set_title("d applications of one unitary = Chebyshev T_d(A); phases unlock the rest")
        save(fig, "predecessors/09-qsvt", "fig-chebyshev", mode)


# ----------------------------------------------------------------- 10 FKV --

def fig_fkv():
    fkv = load("predecessors/10-hhl-tang/fkv.py", "fkv_mod")
    A = fkv.make_low_rank(800, 800, k=5)
    rs = [15, 25, 50, 100, 200, 400]
    ratios = [fkv.reconstruction_ratio(A, 5, r) for r in rs]
    for mode in ("light", "dark"):
        ink, c = INK[mode], SERIES[mode]
        fig, ax = new_fig(mode)
        ax.plot(rs, ratios, color=c[0], lw=2, marker="o", ms=6, zorder=3)
        ax.axhline(1.0, color=ink["muted"], lw=1, ls=(0, (4, 3)))
        ax.text(rs[-1], 1.005, "optimal rank-5 projection", ha="right",
                color=ink["muted"], fontsize=8.5)
        ax.set_xscale("log")
        ax.set_xticks(rs, [str(r) for r in rs])
        ax.set_xlabel("sampled rows r   (A is 800 × 800, rank ≈ 5)")
        ax.set_ylabel("error vs optimal (1.0 = perfect)")
        ax.set_title("ℓ²-sampling a few rows matches the 'quantum' result — the advantage was the access model")
        save(fig, "predecessors/10-hhl-tang", "fig-dequantized", mode)


# --------------------------------------------------------------- 12 Gibbs --

def fig_gibbs():
    from scipy.linalg import expm
    dv = load("predecessors/12-gibbs-lindblad/davies.py", "dv")
    from qsim import X, Y
    n, beta = 3, 1.0
    Hm = dv.heisenberg_with_fields(n)
    coup = [dv.site_op(X, i, n) for i in range(n)] + \
           [dv.site_op(Y, i, n) for i in range(n)]
    L = dv.davies_superoperator(Hm, coup, beta)
    rho_b = dv.gibbs_state(Hm, beta)
    rng = np.random.default_rng(4)
    v = rng.normal(size=8) + 1j * rng.normal(size=8)
    v /= np.linalg.norm(v)
    starts = [("maximally mixed", np.eye(8) / 8),
              ("pure |000⟩", np.diag([1.0] + [0] * 7).astype(complex)),
              ("random pure", np.outer(v, v.conj()))]
    ts = np.linspace(0, 40, 60)
    props = [expm(L * t) for t in ts]
    for mode in ("light", "dark"):
        ink, c = INK[mode], SERIES[mode]
        fig, ax = new_fig(mode)
        for i, (label, rho0) in enumerate(starts):
            d = [0.5 * np.abs(np.linalg.eigvalsh(
                (P @ rho0.reshape(-1)).reshape(8, 8) - rho_b)).sum()
                 for P in props]
            ax.semilogy(ts, np.maximum(d, 1e-9), color=c[i], lw=2, zorder=3,
                        label=label)
        leg = ax.legend(frameon=False, fontsize=9, loc="upper right")
        for txt in leg.get_texts():
            txt.set_color(ink["secondary"])
        ax.set_xlabel("time t   (3-qubit Heisenberg + fields, β = 1)")
        ax.set_ylabel("trace distance to Gibbs")
        ax.set_title("The Davies Lindbladian pulls every state to e^{−βH}/Z at rate ≈ its gap")
        save(fig, "predecessors/12-gibbs-lindblad", "fig-convergence", mode)


if __name__ == "__main__":
    for f in (fig_dj, fig_bv, fig_simon, fig_shor, fig_grover, fig_walks,
              fig_trotter, fig_qsvt, fig_fkv, fig_gibbs):
        print(f.__name__)
        f()
    print("done")
