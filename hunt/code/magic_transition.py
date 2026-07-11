"""L4 first numerics: the learnability signal of Clifford+T states decays
at a measurable per-T-gate rate.

Bell-difference-sampling learners (GIKL, STOC 2024) draw from the
characteristic distribution p_psi(a) = |<psi|W_a|psi>|^2 / 2^n over the
4^n Weyl operators. Their sample AND time costs are controlled by the
collision mass 2^n sum_a p(a)^2 = exp2(-M_2), with M_2 the stabilizer
2-Renyi entropy (Leone-Oliviero-Hamma): stabilizer states have collision
mass 1; each T gate multiplies it by a roughly constant factor. Measuring
that factor quantifies the transition: cost ~ (1/factor)^t is polynomial
at t = O(log n), superpolynomial in the open middle strip, and the
pseudorandomness wall sits at t = Theta(n).

Exact computation (no sampling): all 4^n Weyl expectations, n <= 6.

Run: .venv/bin/python hunt/code/magic_transition.py
"""

import numpy as np

RNG = np.random.default_rng(11)

_H = np.array([[1, 1], [1, -1]]) / np.sqrt(2)
_S = np.diag([1.0, 1.0j])
_T = np.diag([1.0, np.exp(1j * np.pi / 4)])


def _apply_1q(psi, n, q, gate):
    psi = psi.reshape(2 ** q, 2, -1)
    return np.einsum('ab,ibj->iaj', gate, psi).reshape(-1)


def _apply_cx(psi, n, c, t):
    psi = psi.reshape([2] * n)
    idx = [slice(None)] * n
    idx[c] = 1
    sub = psi[tuple(idx)]
    psi[tuple(idx)] = np.flip(sub, axis=t if t < c else t - 1)
    return psi.reshape(-1)


def random_clifford_t_state(n, t_count, rng, depth=60):
    """Random {H,S,CX} circuit with t_count T gates spliced in."""
    psi = np.zeros(2 ** n, dtype=complex)
    psi[0] = 1.0
    t_slots = set(rng.choice(depth, size=t_count, replace=False)) \
        if t_count else set()
    for step in range(depth):
        kind = rng.integers(0, 3)
        if kind == 0:
            psi = _apply_1q(psi, n, int(rng.integers(n)), _H)
        elif kind == 1:
            psi = _apply_1q(psi, n, int(rng.integers(n)), _S)
        else:
            c, t = rng.choice(n, size=2, replace=False)
            psi = _apply_cx(psi, n, int(c), int(t))
        if step in t_slots:
            psi = _apply_1q(psi, n, int(rng.integers(n)), _T)
    return psi


def weyl_expectations(psi, n):
    """|<psi|W_a|psi>|^2 for all 4^n Paulis, via factored Pauli action."""
    vals = np.empty(4 ** n)
    for a in range(4 ** n):
        phi = psi
        aa = a
        for q in range(n):
            p = aa % 4
            aa //= 4
            if p == 1:                                     # X
                phi = _apply_1q(phi, n, q, np.array([[0, 1], [1, 0]],
                                                    dtype=complex))
            elif p == 2:                                   # Y
                phi = _apply_1q(phi, n, q, np.array([[0, -1j], [1j, 0]]))
            elif p == 3:                                   # Z
                phi = _apply_1q(phi, n, q, np.diag([1.0, -1.0]).astype(
                    complex))
        vals[a] = abs(np.vdot(psi, phi)) ** 2
    return vals


def collision_mass(psi, n):
    """2^n sum_a p(a)^2 with p the characteristic distribution; equals 1
    exactly for stabilizer states, exp2(-M_2) in general."""
    w = weyl_expectations(psi, n)
    p = w / w.sum()
    return float(2 ** n * (p ** 2).sum())


if __name__ == "__main__":
    n, reps = 6, 16
    print(f"Collision mass of the Bell-difference distribution, n={n}, "
          f"{reps} random circuits per point\n")
    print(f"{'t':>3} {'collision mass':>15} {'M_2 (bits)':>11} "
          f"{'cost proxy 1/cm':>16}")
    masses = []
    for t in range(0, 13, 2):
        cms = [collision_mass(random_clifford_t_state(n, t, RNG), n)
               for _ in range(reps)]
        cm = float(np.mean(cms))
        masses.append((t, cm))
        print(f"{t:>3} {cm:>15.4f} {-np.log2(cm):>11.3f} {1/cm:>16.1f}")

    ts = np.array([m[0] for m in masses if m[0] > 0], dtype=float)
    per_t = np.polyfit(ts, np.log2([m[1] for m in masses if m[0] > 0]),
                       1)[0]
    print(f"\nper-T-gate decay: {per_t:.3f} bits => Bell-sampling cost "
          f"grows ~{2**-per_t:.2f}x per T gate.")
    print("t = O(log n): poly cost (matches known learners). The open")
    print("strip is omega(log n) < t < o(n): sample-easy everywhere,")
    print("pseudorandom only at t = Theta(n) (GIKL) - where in between")
    print("does computational learnability actually die?")
