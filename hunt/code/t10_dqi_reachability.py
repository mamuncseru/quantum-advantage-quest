"""T10 first numerics: is the DQI payoff variationally reachable?

Setting: random sparse max-XORSAT (the Hamming-DQI home turf; A2's CRT
twin shares the payoff theory). n = 12 bits, m = 24 weight-3 parity
constraints, mu = 1/2. Exact enumeration (4096 states) gives:
  - the DQI ell-shell payoff curve: top eigenvalue of the (ell+1)
    Jacobi pencil in the elementary-symmetric basis of standardized
    constraint signs (the same machinery validated in J1);
  - the trained-QAOA payoff: statevector QAOA-p (phase separator
    e^{-i gamma f} diagonal, transverse mixer), trained GENEROUSLY
    (multi-start gradient ascent) so any shortfall is not an optimizer
    artifact;
  - the ground-T tie-in: Pauli-budget N* of the trained QAOA circuits
    (f's terms are Z-strings; mixers are X rotations — the T4 engine
    applies unchanged).

PRE-REGISTERED (before running at scale):
  K1 (reachability) fires if best QAOA-p<=6 matches the ell=3 shell
  payoff (within 0.01 of <f>/m): DQI's edge would be constructive
  convenience, not necessity.
  T10's separation outcome: QAOA plateaus below the ell>=2 payoff
  while its own N* stays small — "variational training neither reaches
  the DQI payoff nor escapes its own surrogate."

Run: .venv/bin/python hunt/code/t10_dqi_reachability.py   (~10 min)
"""

import sys
from math import comb
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from t4_adaptive_growth import anticommute, pmult  # noqa: E402

N = 12
M_CONS = 24
DIM = 2 ** N
RNG = np.random.default_rng(20260718)


def instance():
    rows, vs = [], []
    for _ in range(M_CONS):
        sites = RNG.choice(N, 3, replace=False)
        mask = 0
        for s in sites:
            mask |= 1 << int(s)
        rows.append(mask)
        vs.append(int(RNG.integers(0, 2)))
    return rows, vs


ROWS, VS = instance()
b = np.arange(DIM)
G = np.stack([(1 - 2 * ((np.bitwise_count(b & r).astype(np.int64)
                         + v) & 1)).astype(float)
              for r, v in zip(ROWS, VS)])          # g_i(x) = +-1
FVAL = ((G + 1) / 2).sum(axis=0)                    # satisfied count
FMAX = float(FVAL.max())


# ------------------------------------------- DQI shell payoff curve ----

def dqi_curve(lmax=4):
    """Top eigenvalue of the Jacobi pencil per shell degree ell."""
    e = [np.ones(DIM)]
    p_sums = [None] + [(G ** k).sum(axis=0) for k in range(1, lmax + 1)]
    for k in range(1, lmax + 1):                    # Newton's identities
        acc = np.zeros(DIM)
        for i in range(1, k + 1):
            acc += ((-1) ** (i - 1)) * e[k - i] * p_sums[i]
        e.append(acc / k)
    out = {}
    for ell in range(1, lmax + 1):
        Phi = np.stack([e[k] / np.sqrt(comb(M_CONS, k))
                        for k in range(ell + 1)])
        A = np.einsum('ap,bp,p->ab', Phi, Phi, FVAL) / DIM
        B = np.einsum('ap,bp->ab', Phi, Phi) / DIM
        evals = np.linalg.eigvals(np.linalg.solve(B, A))
        out[ell] = float(np.real(evals).max()) / M_CONS
    return out


# ------------------------------------------------------- QAOA arm ----

def qaoa_state(params):
    p = len(params) // 2
    v = np.full(DIM, 1 / np.sqrt(DIM), dtype=complex)
    for l in range(p):
        v = np.exp(-1j * params[2 * l] * FVAL) * v
        beta = params[2 * l + 1]
        for q in range(N):
            v = v.reshape(2 ** (N - 1 - q), 2, 2 ** q)
            a0, a1 = v[:, 0].copy(), v[:, 1].copy()
            v[:, 0] = np.cos(beta) * a0 - 1j * np.sin(beta) * a1
            v[:, 1] = np.cos(beta) * a1 - 1j * np.sin(beta) * a0
            v = v.reshape(-1)
    return v


def qaoa_payoff(params):
    v = qaoa_state(params)
    return float((np.abs(v) ** 2 @ FVAL))


def train_qaoa(p, starts=12, steps=300, lr=0.05, h=1e-4):
    best = -1e9
    for s in range(starts):
        rng = np.random.default_rng(1000 + s)
        th = rng.uniform(0, 0.6, 2 * p)
        for _ in range(steps):
            g = np.zeros(2 * p)
            for k in range(2 * p):
                p1, p2 = th.copy(), th.copy()
                p1[k] += h
                p2[k] -= h
                g[k] = (qaoa_payoff(p1) - qaoa_payoff(p2)) / (2 * h)
            th = th + lr * g
        best = max(best, qaoa_payoff(th))
        if s == 0:
            best_th = th.copy()
        elif qaoa_payoff(th) >= best - 1e-12:
            best_th = th.copy()
    return best / M_CONS, best_th


# --------------------------------- ground-T tie-in: Pauli budget ----

def qaoa_budget(params, tol=0.1, ladder=(128, 512, 2048, 8192)):
    """N* for the QAOA circuit: conjugate f's Z-string terms backward
    through the mixer/phase layers (T4 rules), evaluate on |+>^n."""
    p = len(params) // 2
    gates = []
    for l in range(p):
        for r_, v_ in zip(ROWS, VS):
            gates.append((0, r_, params[2 * l] * 0.5 * (-1) ** v_))
        for q in range(N):
            gates.append(((1 << q), 0, params[2 * l + 1]))
    # f = m/2 + (1/2) sum_i (-1)^{v_i} Z-string(r_i)
    ex = qaoa_payoff(params)
    for Nb in ladder:
        terms = {}
        for r_, v_ in zip(ROWS, VS):
            key = (0, r_)
            terms[key] = terms.get(key, 0.0) + 0.5 * ((-1.0) ** v_)
        for (gx, gz, th) in reversed(gates):
            co, si = np.cos(2 * th), np.sin(2 * th)
            new = {}
            for (x, z), c in terms.items():
                if not anticommute(gx, gz, x, z):
                    new[(x, z)] = new.get((x, z), 0.0) + c
                else:
                    new[(x, z)] = new.get((x, z), 0.0) + co * c
                    x3, z3, ph = pmult(gx, gz, x, z)
                    w = 1j * ph
                    new[(x3, z3)] = new.get((x3, z3), 0.0) + si * w.real * c
            if len(new) > Nb:
                keep = sorted(new, key=lambda kk: -abs(new[kk]))[:Nb]
                new = {kk: new[kk] for kk in keep}
            terms = new
        # <+|P|+> = 1 iff z-mask == 0 (X-strings give 1, Z's give 0)
        val = M_CONS / 2 + sum(c for (x, z), c in terms.items() if z == 0)
        if abs(val - ex) <= tol:
            return Nb
    return None


if __name__ == "__main__":
    print(f"max-XORSAT: n = {N}, m = {M_CONS} weight-3 rows, "
          f"f_max = {FMAX:.0f} ({FMAX / M_CONS:.3f} of m), "
          f"random guess = 0.500\n")
    curve = dqi_curve()
    print("DQI shell payoffs <f>/m (ideal ell-shell, exact pencil):")
    for ell, val in curve.items():
        print(f"  ell = {ell}: {val:.4f}")
    print("\ntrained QAOA (12 starts x 300 steps, generous):")
    for p in (1, 2, 3, 4, 6):
        val, th = train_qaoa(p)
        nb = qaoa_budget(th)
        print(f"  p = {p}: <f>/m = {val:.4f}   N*(trained circuit) = {nb}",
              flush=True)
    print("\nPre-registered: K1 (reachable) fires if best QAOA matches "
          "ell=3\nwithin 0.01; separation outcome otherwise.")
