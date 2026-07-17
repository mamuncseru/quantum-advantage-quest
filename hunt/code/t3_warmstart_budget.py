"""T3 first numerics: the warm-start face of the dichotomy.

T2's theorem covers the deep/Haar regime of poly-DLA circuits. The known
escape from barren plateaus that lives OUTSIDE both assumptions is the
warm start: hardware-efficient ansatz (exponential DLA), parameters
initialized at scale eps near identity, trained by gradient descent. The
matching classical surrogate is truncated Pauli propagation, whose cost
is the number of Pauli terms retained. T3's question, trajectory-
resolved: along trajectories that actually make progress, does the
surrogate term budget stay polynomial (the dichotomy's third face), or
does the trajectory outrun every truncation while still descending?

Protocol (n = 8, RY+CZ-ring hardware-efficient ansatz, 6 layers, 48
params; H = open-chain TFIM at g=1 plus 0.4 * sum Z_i Z_{i+2} to break
integrability — at these sizes everything is classically simulable by
other means; as everywhere in this program, the numerics measure the
MECHANISM's scaling indicators, not hardness):

  E1  engine validation: untruncated Pauli propagation == statevector.
  E2  trajectories: gradient descent from init scales eps in
      {0.01, 0.1, 0.3} and uniform (BP control). Along each: loss,
      gradient norm, and at checkpoints the minimal term budget N* for
      surrogate error <= 0.1.
  E3  the operational kill probe: a CLASSICAL optimizer driven entirely
      by the budget-N surrogate (finite-diff on truncated propagation).
      If it reaches the quantum trajectory's loss at moderate fixed N
      for every eps, the warm-start face closes at this size.

Pre-registered (T3 brief): K1 fires if surrogate-driven descent matches
quantum descent at fixed poly-ish N for all warm eps; K3 (owed next) is
the n-scaling of N* at matched progress.

Run: .venv/bin/python hunt/code/t3_warmstart_budget.py   (~minutes)
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

N = 8
DIM = 2 ** N
LAYERS = 6
NPARAM = LAYERS * N
RNG = np.random.default_rng(20260717)

PAULI = {0: np.eye(2, dtype=complex),
         1: np.array([[0, 1], [1, 0]], dtype=complex),
         2: np.array([[0, -1j], [1j, 0]], dtype=complex),
         3: np.array([[1, 0], [0, -1]], dtype=complex)}
CZ4 = np.diag([1, 1, 1, -1]).astype(complex)


# ------------------- conjugation tables, derived numerically ----------

def _decompose2(M):
    """Unique Pauli x Pauli component of a 2-qubit Pauli conjugate."""
    for a in range(4):
        for b in range(4):
            P = np.kron(PAULI[a], PAULI[b])
            c = np.trace(P.conj().T @ M) / 4
            if abs(c) > 1e-9:
                assert abs(abs(c) - 1) < 1e-9
                return a, b, float(np.real(c))
    raise AssertionError


CZ_TABLE = {}
for a in range(4):
    for b in range(4):
        M = CZ4.conj().T @ np.kron(PAULI[a], PAULI[b]) @ CZ4
        CZ_TABLE[(a, b)] = _decompose2(M)

# RY: U(th)^dag P U(th) = cos(th) P + sin(th) * partner (P in {X, Z})
RY_PARTNER = {}
for p in (1, 3):
    U = np.cos(np.pi / 4) * PAULI[0] - 1j * np.sin(np.pi / 4) * PAULI[2]
    M = U.conj().T @ PAULI[p] @ U            # theta = pi/2: pure partner
    for q in range(1, 4):
        c = np.trace(PAULI[q].conj().T @ M) / 2
        if abs(c) > 1e-9:
            RY_PARTNER[p] = (q, float(np.real(c)))


# --------------------------------------------- circuit definition ----

def circuit():
    gates = []
    k = 0
    for _ in range(LAYERS):
        for q in range(N):
            gates.append(("ry", q, k))
            k += 1
        for q in range(0, N - 1, 2):
            gates.append(("cz", q, q + 1))
        for q in range(1, N - 1, 2):
            gates.append(("cz", q, q + 1))
    return gates


GATES = circuit()


def hamiltonian_terms():
    terms = {}
    for i in range(N - 1):                       # ZZ nearest
        x, z = 0, (1 << i) | (1 << (i + 1))
        terms[(x, z)] = 1.0
    for i in range(N):                           # X field
        terms[((1 << i), 0)] = 1.0
    for i in range(N - 2):                       # ZZ next-next
        terms[(0, (1 << i) | (1 << (i + 2)))] = \
            terms.get((0, (1 << i) | (1 << (i + 2))), 0.0) + 0.4
    return terms


HTERMS = hamiltonian_terms()


def pauli_dense(x, z):
    M = np.array([[1]], dtype=complex)
    for q in range(N):
        a = ((x >> q) & 1) + 2 * ((z >> q) & 1)
        a = {0: 0, 1: 1, 2: 3, 3: 2}[a]          # x,z bits -> pauli id
        M = np.kron(PAULI[a], M)
    return M


HDENSE = sum(c * pauli_dense(x, z) for (x, z), c in HTERMS.items())
EMIN = float(np.linalg.eigvalsh(HDENSE)[0])


# ------------------------------------------------ statevector side ----

def apply_ry(v, q, th):
    v = v.reshape(2 ** (N - 1 - q), 2, 2 ** q)
    a, b = v[:, 0].copy(), v[:, 1].copy()
    v[:, 0] = np.cos(th / 2) * a - np.sin(th / 2) * b
    v[:, 1] = np.sin(th / 2) * a + np.cos(th / 2) * b
    return v.reshape(-1)


def state(params):
    v = np.zeros(DIM, dtype=complex)
    v[0] = 1.0
    for g in GATES:
        if g[0] == "ry":
            v = apply_ry(v, g[1], params[g[2]])
        else:
            i, j = g[1], g[2]
            idx = np.arange(DIM)
            mask = ((idx >> i) & 1) & ((idx >> j) & 1)
            v = v * (1 - 2 * mask)
    return v


def exact_loss(params):
    v = state(params)
    return float(np.real(v.conj() @ (HDENSE @ v)))


def exact_grad(params, h=1e-5):
    g = np.zeros(NPARAM)
    for k in range(NPARAM):
        p1, p2 = params.copy(), params.copy()
        p1[k] += h
        p2[k] -= h
        g[k] = (exact_loss(p1) - exact_loss(p2)) / (2 * h)
    return g


# --------------------------------------- Pauli propagation engine ----

def pid(x, z, q):
    return ((x >> q) & 1) + 2 * ((z >> q) & 1)   # 0 I, 1 X, 2 Z, 3 Y


def setp(x, z, q, a):
    x &= ~(1 << q)
    z &= ~(1 << q)
    if a in (1, 3):
        x |= 1 << q
    if a in (2, 3):
        z |= 1 << q
    return x, z


ID2XZ = {0: 0, 1: 1, 3: 2, 2: 3}                 # pauli id -> (xbit,zbit) id


def surrogate_loss(params, budget):
    """<0| U^dag H U |0> by backward conjugation with term truncation."""
    terms = dict(HTERMS)
    for g in reversed(GATES):
        if g[0] == "cz":
            i, j = g[1], g[2]
            new = {}
            for (x, z), c in terms.items():
                ai = {0: 0, 1: 1, 2: 3, 3: 2}[pid(x, z, i)]
                aj = {0: 0, 1: 1, 2: 3, 3: 2}[pid(x, z, j)]
                bi, bj, s = CZ_TABLE[(ai, aj)]
                x2, z2 = setp(x, z, i, ID2XZ[bi])
                x2, z2 = setp(x2, z2, j, ID2XZ[bj])
                new[(x2, z2)] = new.get((x2, z2), 0.0) + s * c
            terms = new
        else:
            q, th = g[1], params[g[2]]
            co, si = np.cos(th), np.sin(th)
            new = {}
            for (x, z), c in terms.items():
                a = {0: 0, 1: 1, 2: 3, 3: 2}[pid(x, z, q)]
                if a in (0, 2):                   # I or Y: unchanged
                    new[(x, z)] = new.get((x, z), 0.0) + c
                else:
                    partner, s = RY_PARTNER[a]
                    new[(x, z)] = new.get((x, z), 0.0) + co * c
                    x2, z2 = setp(x, z, q, ID2XZ[partner])
                    key = (x2, z2)
                    new[key] = new.get(key, 0.0) + s * si * c
            if budget and len(new) > budget:
                keep = sorted(new, key=lambda k: -abs(new[k]))[:budget]
                new = {k: new[k] for k in keep}
            terms = new
    return float(sum(c for (x, z), c in terms.items() if x == 0))


def budget_needed(params, tol=0.1,
                  ladder=(32, 128, 512, 2048, 8192, 32768)):
    ex = exact_loss(params)
    for Nb in ladder:
        if abs(surrogate_loss(params, Nb) - ex) <= tol:
            return Nb
    return None


# ------------------------------------------------------ trajectories ----

def descend(loss_fn, theta0, steps, lr=0.05, h=1e-4):
    th = theta0.copy()
    traj = [th.copy()]
    for _ in range(steps):
        g = np.zeros(NPARAM)
        for k in range(NPARAM):
            p1, p2 = th.copy(), th.copy()
            p1[k] += h
            p2[k] -= h
            g[k] = (loss_fn(p1) - loss_fn(p2)) / (2 * h)
        th = th - lr * g
        traj.append(th.copy())
    return traj


def descend_spsa(loss_fn, theta0, steps, seed, a=0.15, A=20.0, c=0.1):
    """SPSA with the standard decaying gain schedule (Spall):
    a_k = a/(k+1+A)^0.602, c_k = c/(k+1)^0.101. Two loss evals per
    step; the shared seed makes the quantum-vs-surrogate comparison use
    identical perturbation sequences. (A first version used a fixed
    learning rate; the exact loss's sharper landscape made it bounce
    while the smoother truncated loss descended — an optimizer
    artifact, documented in the brief, fixed here.)"""
    rng = np.random.default_rng(seed)
    th = theta0.copy()
    for k in range(steps):
        ak = a / (k + 1 + A) ** 0.602
        ck = c / (k + 1) ** 0.101
        d = rng.choice((-1.0, 1.0), NPARAM)
        g = (loss_fn(th + ck * d) - loss_fn(th - ck * d)) / (2 * ck)
        th = th - ak * g * d
    return th


if __name__ == "__main__":
    print(f"n = {N}, HEA {LAYERS} layers, {NPARAM} params, "
          f"E_min = {EMIN:.4f}\n")

    print("E1. engine validation (no truncation) vs statevector")
    worst = 0.0
    for _ in range(5):
        p = RNG.uniform(-0.4, 0.4, NPARAM)
        worst = max(worst, abs(surrogate_loss(p, None) - exact_loss(p)))
    print(f"    worst |propagation - exact| over 5 random points: "
          f"{worst:.2e}\n")

    print("E2. trajectories: budget N* (err<=0.1) at checkpoints")
    checkpoints = (0, 10, 30, 60)
    inits = {"0.01": 0.01 * RNG.normal(size=NPARAM),
             "0.10": 0.10 * RNG.normal(size=NPARAM),
             "0.30": 0.30 * RNG.normal(size=NPARAM),
             "unif": RNG.uniform(-np.pi, np.pi, NPARAM)}
    trajs = {}
    print(f"    {'init':>6} {'t':>4} {'loss':>9} {'gap%':>6} "
          f"{'|grad|':>8} {'N*':>7}")
    for name, th0 in inits.items():
        traj = descend(exact_loss, th0, steps=max(checkpoints))
        trajs[name] = traj
        for t in checkpoints:
            th = traj[t]
            lo = exact_loss(th)
            gap = (lo - EMIN) / abs(EMIN) * 100
            gn = float(np.linalg.norm(exact_grad(th)))
            nb = budget_needed(th)
            print(f"    {name:>6} {t:>4} {lo:>9.4f} {gap:>6.1f} "
                  f"{gn:>8.3f} {str(nb):>7}")

    print("\nE3. shared-seed SPSA, 200 steps: quantum vs surrogate-driven")
    print("    (identical perturbation sequences; final TRUE loss of the")
    print("    parameters each optimizer found)")
    for name in ("0.10", "0.30"):
        th0 = inits[name]
        thq = descend_spsa(exact_loss, th0, 200, seed=42)
        for Nb in (512, 2048):
            ths = descend_spsa(lambda p: surrogate_loss(p, Nb), th0,
                               200, seed=42)
            print(f"    eps={name} N={Nb:>5}: quantum {exact_loss(thq):.4f}"
                  f"  surrogate-driven {exact_loss(ths):.4f}"
                  f"  (diff {abs(exact_loss(thq)-exact_loss(ths)):.4f})")
    print("\nReading: if N* stays on the ladder wherever descent makes")
    print("progress and E3 matches, the warm-start face closes at n=8;")
    print("K3 (n-scaling at matched progress) is the owed decisive scan.")
