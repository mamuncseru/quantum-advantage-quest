"""L3 first numerics: does the 'memory-measurable loss' escape route from
trainability => surrogatability actually open a window?

Candidate escape: variational losses that REQUIRE quantum memory to
measure - e.g. L_k(theta) = Tr[rho_A(theta)^2], the purity of a k-qubit
marginal of the trial state. Two copies + local swap test measure it with
O(1/eps^2) shots for ANY k; single-copy shadows pay ~2^k; so if such a
loss were trainable, no shadow surrogate could follow the optimizer.

The self-attack this file runs: the SAME parameter k that makes the loss
expensive for shadows may also kill its gradients (purity of a large
subsystem concentrates - a global-cost barren plateau in disguise). We
measure both exponentials on the same instances:

    training side:   Var_theta[dL_k/dtheta] vs k  (shallow HEA, random init)
    surrogate side:  shadow samples-to-eps for L_k vs k

If the gradient decays at base >= the shadow-cost growth base, the escape
self-kills: shots-to-train outruns shots-to-surrogate and no
trainable-but-hard window exists from this mechanism.

Run: .venv/bin/python hunt/code/swap_loss_bp.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))
from memory_purity import ShadowSampler, shadow_purity  # noqa: E402

DEPTH = 2
BUFFER = 3          # n = k + BUFFER


def ansatz_state(n, theta):
    """Depth-DEPTH hardware-efficient ansatz: RY layer + CZ ring."""
    psi = np.zeros(2 ** n)
    psi[0] = 1.0
    idx = 0
    for _ in range(DEPTH):
        for q in range(n):
            psi = _ry(psi, n, q, theta[idx])
            idx += 1
        for q in range(n):
            psi = _cz(psi, n, q, (q + 1) % n)
    return psi


def _ry(psi, n, q, angle):
    psi = psi.reshape(2 ** q, 2, -1)
    c, s = np.cos(angle / 2), np.sin(angle / 2)
    out = np.empty_like(psi)
    out[:, 0, :] = c * psi[:, 0, :] - s * psi[:, 1, :]
    out[:, 1, :] = s * psi[:, 0, :] + c * psi[:, 1, :]
    return out.reshape(-1)


def _cz(psi, n, a, b):
    a, b = min(a, b), max(a, b)
    psi = psi.reshape(2 ** a, 2, 2 ** (b - a - 1), 2, -1)
    psi = psi.copy()
    psi[:, 1, :, 1, :] *= -1
    return psi.reshape(-1)


def marginal(psi, n, k):
    """rho_A for the first k qubits."""
    m = psi.reshape(2 ** k, -1)
    return m @ m.conj().T


def loss(theta, n, k):
    rho = marginal(ansatz_state(n, theta), n, k)
    return float(np.real(np.trace(rho @ rho)))


def gradient_variance(n, k, samples=150, seed=0):
    rng = np.random.default_rng(seed)
    nparams = DEPTH * n
    grads = []
    for _ in range(samples):
        theta = rng.uniform(0, 2 * np.pi, size=nparams)
        d = 1e-4
        tp, tm = theta.copy(), theta.copy()
        tp[0] += d
        tm[0] -= d
        grads.append((loss(tp, n, k) - loss(tm, n, k)) / (2 * d))
    return float(np.var(grads))


def shadow_cost_of_loss(n, k, eps=0.05, N=400, reps=15, seed=0):
    """Empirical shadow samples-to-eps for Tr[rho_A^2], averaged over a
    few random theta."""
    rng = np.random.default_rng(seed)
    costs = []
    for _ in range(3):
        theta = rng.uniform(0, 2 * np.pi, size=DEPTH * n)
        rho = marginal(ansatz_state(n, theta), n, k)
        sampler = ShadowSampler(rho, rng)
        vals = [shadow_purity(*sampler.snapshots(N)) for _ in range(reps)]
        costs.append(N * (np.std(vals) / eps) ** 2)
    return float(np.mean(costs))


if __name__ == "__main__":
    print("Memory-measurable loss L_k = Tr[rho_A^2], shallow HEA "
          f"(depth {DEPTH}), n = k + {BUFFER}\n")
    print(f"{'k':>3} {'n':>3} {'Var[grad]':>11} {'shots-to-train':>15} "
          f"{'shadow N':>10} {'swap N':>7}")
    gv, sc, ks = [], [], []
    for k in range(1, 6):
        n = k + BUFFER
        v = gradient_variance(n, k)
        cost = shadow_cost_of_loss(n, k)
        ks.append(k)
        gv.append(v)
        sc.append(cost)
        # shots-to-train ~ 1/Var[grad] (resolve the gradient signal);
        # swap N is k-independent by construction
        print(f"{k:>3} {n:>3} {v:>11.2e} {1/v:>15.0f} {cost:>10.0f} "
              f"{'~400':>7}")

    ks = np.array(ks, dtype=float)
    a = np.polyfit(ks, np.log2(1 / np.array(gv)), 1)[0]
    b = np.polyfit(ks, np.log2(sc), 1)[0]
    print(f"\ntraining-cost growth:  {a:.2f} bits per k")
    print(f"surrogate-cost growth: {b:.2f} bits per k")
    print("escape window exists only if training grows strictly slower")
    print("than surrogation; matched or faster => the mechanism self-kills.")
