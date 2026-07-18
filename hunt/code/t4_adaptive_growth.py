"""T4 first numerics: adaptive circuit growth (ADAPT-style) — can the
feedback loop through the device outrun the surrogate?

The mechanism no earlier face covers: the ansatz is BUILT by greedy
selection (largest pool gradient at the current state), so the circuit
is data-dependent — no fixed ensemble (T2's Haar), no fixed warm region
(T3), no fixed DLA (T1). The ground-T hypothesis under test:

    The selection criterion is gradient magnitude, and large gradients
    live in classically visible sectors — so a truncated-propagation
    surrogate should replicate the ENTIRE adaptive construction:
    selections, angles, and final energy.

Protocol: qubit-ADAPT with pool {Y_q} + neighbor {YZ, ZY, YX, XY};
each round: select argmax |dL/dtheta at 0|, set the new angle by
Rotosolve (the loss in one rotation angle is exactly sinusoidal), full
Rotosolve sweep every 5 rounds; 24 rounds. Two Hamiltonians: H_A =
TFIM(g=1)+0.4 ZZ' (T3 continuity) and H_B = random 2-local chain
(XX/YY/ZZ + X/Z fields, fixed seed). Two arms with the same policy:
  exact arm      — all quantities from the statevector;
  surrogate arm  — ALL quantities (pool gradients, Rotosolve evals)
                   from budget-N truncated Pauli propagation.
Scored by: selection-match fraction, TRUE final energies of both arms'
circuits, and the T3-style audit budget N* along the exact arm.

PRE-REGISTERED (before running at scale):
  K1 fires (the fourth face closes at tested sizes) if, at N <= 2048,
  selection match >= 0.8 AND |E_true(surrogate-built) -
  E_true(exact-built)| <= 0.0125 n for both Hamiltonians and all n
  tested, with audit budgets staying on the T3 ladder (<= 2048).
  T4 survives if selections diverge AND the exact-built circuit beats
  every budgeted surrogate-built circuit by a margin growing with n.

Run: .venv/bin/python hunt/code/t4_adaptive_growth.py   (~15 min)
"""

import csv
import sys
from pathlib import Path

import numpy as np
from scipy.sparse.linalg import LinearOperator, eigsh

sys.path.insert(0, str(Path(__file__).parent))

HERE = Path(__file__).resolve().parent
CSV = HERE.parent / "t4-adaptive-scan.csv"
ROUNDS = 24
LADDER = (128, 512, 2048, 8192, 32768)

# ---------------- per-qubit Pauli product table, derived numerically ----

_P2 = {0: np.eye(2, dtype=complex),
       1: np.array([[0, 1], [1, 0]], dtype=complex),
       2: np.array([[0, -1j], [1j, 0]], dtype=complex),
       3: np.array([[1, 0], [0, -1]], dtype=complex)}
PROD = {}
for a in range(4):
    for b in range(4):
        M = _P2[a] @ _P2[b]
        for c in range(4):
            ph = np.trace(_P2[c].conj().T @ M) / 2
            if abs(ph) > 1e-9:
                PROD[(a, b)] = (c, complex(np.round(ph.real)
                                           + 1j * np.round(ph.imag)))
                break

XZ2ID = {0: 0, 1: 1, 2: 3, 3: 2}
ID2XZ = {0: (0, 0), 1: (1, 0), 3: (0, 1), 2: (1, 1)}


def pmult(x1, z1, x2, z2):
    """Product of Hermitian Pauli strings: returns (x3, z3, phase)."""
    x3, z3, phase = x1 ^ x2, z1 ^ z2, 1 + 0j
    act = x1 | z1 | x2 | z2
    q = 0
    while act >> q:
        if (act >> q) & 1:
            a = XZ2ID[((x1 >> q) & 1) + 2 * ((z1 >> q) & 1)]
            b = XZ2ID[((x2 >> q) & 1) + 2 * ((z2 >> q) & 1)]
            phase *= PROD[(a, b)][1]
        q += 1
    return x3, z3, phase


def anticommute(x1, z1, x2, z2):
    return (int(x1 & z2).bit_count() + int(z1 & x2).bit_count()) & 1


# import-time self-check of the phase formula against dense (n = 2)
def _pauli_dense(x, z, n):
    M = np.array([[1]], dtype=complex)
    for q in range(n):
        a = XZ2ID[((x >> q) & 1) + 2 * ((z >> q) & 1)]
        M = np.kron(_P2[a], M)
    return M


for _ in range(1):
    rng = np.random.default_rng(0)
    for _k in range(20):
        x1, z1, x2, z2 = rng.integers(0, 4, 4)
        x3, z3, ph = pmult(x1, z1, x2, z2)
        ref = _pauli_dense(x1, z1, 2) @ _pauli_dense(x2, z2, 2)
        assert np.abs(ph * _pauli_dense(x3, z3, 2) - ref).max() < 1e-9


# ------------------------------------------------------- the instance ----

class Inst:
    def __init__(self, n, ham="A", seed=7):
        self.n, self.dim = n, 2 ** n
        self.terms = {}
        if ham == "A":
            for i in range(n - 1):
                self.terms[(0, (1 << i) | (1 << (i + 1)))] = 1.0
            for i in range(n):
                self.terms[((1 << i), 0)] = 1.0
            for i in range(n - 2):
                key = (0, (1 << i) | (1 << (i + 2)))
                self.terms[key] = self.terms.get(key, 0.0) + 0.4
        else:                                    # random 2-local chain
            rng = np.random.default_rng(seed)
            for i in range(n - 1):
                m = (1 << i) | (1 << (i + 1))
                self.terms[(m, 0)] = 0.7 * rng.normal()      # XX
                self.terms[(m, m)] = 0.7 * rng.normal()      # YY
                self.terms[(0, m)] = 0.7 * rng.normal()      # ZZ
            for i in range(n):
                self.terms[((1 << i), 0)] = \
                    self.terms.get(((1 << i), 0), 0.0) + 0.5 * rng.normal()
                self.terms[(0, (1 << i))] = 0.5 * rng.normal()
        self._pc = {}
        op = LinearOperator((self.dim, self.dim),
                            matvec=lambda v: self.hv(v.astype(complex)),
                            dtype=complex)
        self.emin = float(np.real(eigsh(op, k=1, which="SA")[0][0]))
        # pool: Y_q singles + neighbor YZ, ZY, YX, XY
        self.pool = []
        for q in range(n):
            self.pool.append(((1 << q), (1 << q)))
        for i in range(n - 1):
            a, b = 1 << i, 1 << (i + 1)
            self.pool += [((a, a | b)), ((b, a | b)),
                          ((a | b, a)), ((a | b, b))]

    def phases(self, x, z):
        if (x, z) not in self._pc:
            b = np.arange(self.dim)
            odd = np.bitwise_count(b & z).astype(np.int64) & 1
            ny = int(x & z).bit_count()
            self._pc[(x, z)] = (1j) ** ny * (1 - 2 * odd)
        return self._pc[(x, z)]

    def papply(self, v, x, z):
        out = np.empty_like(v)
        out[np.arange(self.dim) ^ x] = self.phases(x, z) * v
        return out

    def hv(self, v):
        out = np.zeros_like(v)
        for (x, z), c in self.terms.items():
            out += c * self.papply(v, x, z)
        return out

    def state(self, gates):
        v = np.zeros(self.dim, dtype=complex)
        v[0] = 1.0
        for (x, z, th) in gates:
            v = np.cos(th) * v - 1j * np.sin(th) * self.papply(v, x, z)
        return v

    def exact_loss(self, gates):
        v = self.state(gates)
        return float(np.real(v.conj() @ self.hv(v)))

    def exact_pool_grads(self, gates):
        v = self.state(gates)
        hv = self.hv(v)
        return [-2.0 * float(np.imag(v.conj() @ self.papply(hv, x, z)))
                for (x, z) in self.pool]

    # ------------------------- truncated-propagation surrogate side ----
    def surrogate_eval(self, terms, gates, budget):
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
                    assert abs(w.imag) < 1e-9
                    key = (x3, z3)
                    new[key] = new.get(key, 0.0) + si * w.real * c
            if budget and len(new) > budget:
                keep = sorted(new, key=lambda k: -abs(new[k]))[:budget]
                new = {k: new[k] for k in keep}
            terms = new
        return float(sum(c for (x, z), c in terms.items() if x == 0))

    def surrogate_loss(self, gates, budget):
        return self.surrogate_eval(dict(self.terms), gates, budget)

    def surrogate_pool_grads(self, gates, budget):
        out = []
        for (gx, gz) in self.pool:
            d = {}
            for (x, z), c in self.terms.items():
                if anticommute(gx, gz, x, z):
                    x3, z3, ph = pmult(gx, gz, x, z)
                    w = 2j * ph
                    d[(x3, z3)] = d.get((x3, z3), 0.0) + w.real * c
            out.append(self.surrogate_eval(d, gates, budget)
                       if d else 0.0)
        return out


# --------------------------------------------------- the ADAPT policy ----

def rotosolve(lossf, gates, k):
    """Closed-form angle update for gate k (loss is sinusoidal in it)."""
    def at(th):
        g = list(gates)
        g[k] = (g[k][0], g[k][1], th)
        return lossf(g)
    l0, lp, lm = at(0.0), at(np.pi / 4), at(-np.pi / 4)
    a = (lp + lm) / 2
    b, c = l0 - a, (lp - lm) / 2
    th = 0.5 * np.arctan2(-c, -b)
    gates[k] = (gates[k][0], gates[k][1], th)


def adapt_run(inst, budget=None, rounds=ROUNDS):
    """One ADAPT run; budget=None -> exact arm."""
    if budget is None:
        lossf = inst.exact_loss
        gradf = lambda g: inst.exact_pool_grads(g)
    else:
        lossf = lambda g: inst.surrogate_loss(g, budget)
        gradf = lambda g: inst.surrogate_pool_grads(g, budget)
    gates, sel = [], []
    for r in range(rounds):
        grads = gradf(gates)
        k = int(np.argmax(np.abs(grads)))
        sel.append(k)
        gates.append((inst.pool[k][0], inst.pool[k][1], 0.0))
        rotosolve(lossf, gates, len(gates) - 1)
        if (r + 1) % 5 == 0:
            for j in range(len(gates)):
                rotosolve(lossf, gates, j)
    return gates, sel


def audit_budget(inst, gates, tol):
    ex = inst.exact_loss(gates)
    for Nb in LADDER:
        if abs(inst.surrogate_loss(gates, Nb) - ex) <= tol:
            return Nb
    return None


if __name__ == "__main__":
    rows = []
    for ham in ("A", "B"):
        for n in (6, 8, 10):
            inst = Inst(n, ham)
            gq, sq = adapt_run(inst)
            eq = inst.exact_loss(gq)
            aud = audit_budget(inst, gq, tol=0.0125 * n)
            print(f"H_{ham} n={n:>2}: exact-ADAPT E = {eq:.4f} "
                  f"(E_min {inst.emin:.4f}, gap closed "
                  f"{(1 - (eq - inst.emin) / abs(inst.emin)) * 100:.0f}%), "
                  f"audit N* = {aud}", flush=True)
            for Nb in (512, 2048):
                gs, ss = adapt_run(inst, budget=Nb)
                es = inst.exact_loss(gs)          # TRUE energy of its circuit
                match = float(np.mean([a == b for a, b in zip(sq, ss)]))
                rows.append(dict(ham=ham, n=n, budget=Nb, match=match,
                                 e_exact=eq, e_surr=es, audit=aud))
                print(f"        N={Nb:>5}: selection match {match:.2f}, "
                      f"surrogate-built TRUE E = {es:.4f} "
                      f"(diff {abs(es - eq):.4f}, tol {0.0125 * n:.3f})",
                      flush=True)
    new = not CSV.exists()
    with open(CSV, "a", newline="") as f:
        w = csv.DictWriter(f, fieldnames=list(rows[0]))
        if new:
            w.writeheader()
        w.writerows(rows)
    print(f"\nappended {len(rows)} rows to {CSV.name}")
    print("\nPre-registered: K1 fires if match >= 0.8 and |dE| <= 0.0125n")
    print("at N <= 2048 for both H and all n, audits on the ladder.")
