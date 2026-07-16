"""Adversarial pass 1, exhibit A: the uniqueness step of Theorem 4.4 is
false as written — and why the decoder survives it anyway.

The theorem's proof claims the accepted continued-fraction candidate is
UNIQUE, via "two accepted candidates give weight-<=2l integers within
2*eta*M <= d_min(2l)", resting on the inequality P_S * P_S' <= P_max(2l).
Both steps fail:

  (a) P_S * P_S' <= P_max(2l) is false whenever the supports overlap
      (take S = S' = the l largest moduli: P_max(l)^2 > P_max(2l));
  (b) eta < 1/(2 P_S^2) does NOT imply 2*eta*M <= d_min(2l) when the true
      support sits on SMALL moduli — and then a second, spurious candidate
      really is accepted (exhibit E1 below: theta = 43/323 has BOTH 2/15
      and 43/323 within a legal eta, both smooth, both weight 2).

What saves the algorithm: convergents arrive in increasing denominator
order, and NO spurious candidate with denominator <= P_S can be within eta
(distance >= 1/(P_S q') > 2*eta). So the FIRST accepted convergent is the
true one — cf_decode returns it before ever seeing the spurious accept.
Correctness holds; the written uniqueness argument does not. The repaired
proof is in strike/crt-dqi-theorem.md section 4.4.

Exhibit E2 shows the flip side, which matters for the COHERENT use (state
uncomputation runs one global eta across all branches): with eta legal for
a small support but the truth planted on a LARGE support, the decoder
returns the wrong pattern. Hence the uncomputation constant must be the
worst case over branches: eta < 1/(2 P_max(l)^2). E4 validates that
corrected global constant exhaustively.

Run: .venv/bin/python hunt/code/attack_cf_uniqueness.py
"""

import sys
from fractions import Fraction
from itertools import combinations
from math import prod
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from cf_decode import cf_decode, convergents, factor_over  # noqa: E402

PRIMES = [3, 5, 7, 11, 13, 17, 19]
M = prod(PRIMES)


def cf_accepts(moduli, ell, theta, eta):
    """ALL convergents the acceptance rule of Theorem 4.4 admits —
    the same test as cf_decode, without the first-accept early return."""
    out = []
    for h, k in convergents(theta):
        if k == 1:
            continue
        d = abs(theta - Fraction(h, k))
        d = min(d, 1 - d)
        if d > eta:
            continue
        support = factor_over(moduli, k)
        if support is None or len(support) > ell:
            continue
        out.append((h, k))
    return out


def pattern_of(h, q, moduli):
    a = [0] * len(moduli)
    for i, p in enumerate(moduli):
        if q % p == 0:
            a[i] = h * pow(q // p, -1, p) % p
    return a


def all_patterns(moduli, ell):
    """Every CRT-weight-<=ell pattern (support, (k_i)) as (theta, a)."""
    for r in range(1, ell + 1):
        for S in combinations(range(len(moduli)), r):
            ks = [1] * r
            while True:
                a = [0] * len(moduli)
                theta = Fraction(0)
                for j, i in enumerate(S):
                    a[i] = ks[j]
                    theta += Fraction(ks[j], moduli[i])
                yield theta % 1, a
                for j in range(r - 1, -1, -1):
                    ks[j] += 1
                    if ks[j] < moduli[S[j]]:
                        break
                    ks[j] = 1
                else:
                    break


# ---------------------------------------------------------------- E1 ----

def e1_double_accept():
    """theta = 43/323: both 2/15 and 43/323 accepted at a legal eta —
    the proof's uniqueness claim is false; first-accept still returns the
    hypothesis pattern (support {3,5}, P_S = 15, eta < 1/(2*15^2))."""
    theta = Fraction(43, 323)
    eta = Fraction(1, 500)                     # legal: < 1/450
    gap = abs(theta - Fraction(2, 15))
    assert gap == Fraction(1, 4845) <= eta
    accepts = cf_accepts(PRIMES, 2, theta, eta)
    assert (2, 15) in accepts and (43, 323) in accepts, accepts
    got = cf_decode(PRIMES, 2, theta, eta)
    assert got == pattern_of(2, 15, PRIMES)    # first accept = truth
    return accepts


# ---------------------------------------------------------------- E2 ----

def e2_large_support_needs_global_eta():
    """Truth planted on {17,19} (P_S = 323); noise |delta| = 1/4845 pushes
    theta onto 2/15 exactly. With eta = 1/500 (legal only for SMALL
    supports) the decoder returns the WRONG pattern — so the coherent
    uncomputation, which runs one eta for every branch, must use the
    worst-case constant eta < 1/(2 P_max(l)^2)."""
    truth = pattern_of(43, 323, PRIMES)
    theta = Fraction(2, 15)                    # = 43/323 - 1/4845
    got = cf_decode(PRIMES, 2, theta, Fraction(1, 500))
    assert got is not None and got != truth
    # with the corrected global eta the offending noise is excluded:
    eta_g = Fraction(1, 2 * 323 * 323)
    assert Fraction(1, 4845) > eta_g
    return got, truth


# ------------------------------------------------------------- E3, E4 ----

def sweep(ell, eta_of_ps, delta_of_eta, moduli=PRIMES):
    """Exhaustive decode over every weight-<=ell pattern with worst-case
    noise; returns (failures, trials)."""
    fails = trials = 0
    for theta, a in all_patterns(moduli, ell):
        P_S = prod(moduli[i] for i in range(len(moduli)) if a[i])
        eta = eta_of_ps(P_S)
        if eta is None:
            continue
        for delta in delta_of_eta(eta):
            trials += 1
            got = cf_decode(moduli, ell, (theta + delta) % 1, eta)
            fails += (got != a)
    return fails, trials


def e3_per_instance_eta(ell=2):
    """Theorem 4.4 as repaired: eta just under 1/(2 P_S^2), noise at the
    boundary — must decode every pattern."""
    return sweep(
        ell,
        eta_of_ps=lambda ps: Fraction(1, 2 * ps * ps)
        - Fraction(1, 10 ** 12),
        delta_of_eta=lambda eta: (eta, -eta, eta / 2),
    )


def e4_global_eta(ell=2):
    """The corrected uncomputation constant: one global
    eta < 1/(2 P_max(l)^2) for every branch."""
    pmax = prod(sorted(PRIMES)[-ell:])
    eta_g = Fraction(1, 2 * pmax * pmax) - Fraction(1, 10 ** 12)
    return sweep(ell, eta_of_ps=lambda ps: eta_g,
                 delta_of_eta=lambda eta: (eta, -eta))


if __name__ == "__main__":
    print("=== (a) the written inequality P_S*P_S' <= P_max(2l) is false ===")
    pmax_l, pmax_2l = 17 * 19, 19 * 17 * 13 * 11
    print(f"  P_max(l)^2 = {pmax_l**2:,} > P_max(2l) = {pmax_2l:,}  "
          f"(S = S' = {{17,19}})")

    print("\n=== E1: double accept at legal eta (uniqueness claim false) ===")
    accepts = e1_double_accept()
    print(f"  theta = 43/323, eta = 1/500 < 1/(2*15^2)")
    print(f"  accepted candidates: {[f'{h}/{k}' for h, k in accepts]}")
    print("  first accept = pattern of 2/15 = the hypothesis t  [correct]")

    print("\n=== E2: same configuration kills a large-support branch ===")
    got, truth = e2_large_support_needs_global_eta()
    print(f"  planted {truth} (supp {{17,19}}), decoded {got} (supp {{3,5}})")
    print("  => coherent uncomputation must use eta < 1/(2 P_max(l)^2)")

    print("\n=== E3: exhaustive, per-instance eta at the boundary ===")
    fails, trials = e3_per_instance_eta()
    print(f"  failures: {fails}/{trials} over every weight-<=2 pattern")

    print("\n=== E4: exhaustive, corrected global eta ===")
    fails, trials = e4_global_eta()
    print(f"  failures: {fails}/{trials} over every weight-<=2 pattern")

    print("\nReading: the theorem's conclusion and algorithm survive; the")
    print("uniqueness step of its written proof does not. Repaired proof =")
    print("first-accept ordering + no-spurious-accept below P_S. The")
    print("coherent-use constant is eta < 1/(2 P_max(l)^2), same window.")
