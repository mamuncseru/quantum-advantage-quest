"""Tests pinning adversarial pass 1's exhibits (attack_cf_uniqueness.py).

These are regression pins on a *finding*: if a later edit to cf_decode or
to Theorem 4.4's constants makes any exhibit silently change character,
the pass's conclusions must be re-derived.
"""

import sys
from fractions import Fraction
from math import prod
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from attack_cf_uniqueness import (PRIMES, cf_accepts, e1_double_accept,
                                  e2_large_support_needs_global_eta,
                                  e3_per_instance_eta, e4_global_eta,
                                  pattern_of)
from cf_decode import cf_decode


def test_written_inequality_is_false():
    # P_S * P_S' <= P_max(2l) fails for overlapping supports
    assert (17 * 19) ** 2 > 19 * 17 * 13 * 11


def test_e1_two_candidates_accepted():
    accepts = e1_double_accept()  # asserts internally too
    assert (2, 15) in accepts and (43, 323) in accepts
    assert len(accepts) >= 2


def test_e1_first_accept_is_hypothesis_pattern():
    got = cf_decode(PRIMES, 2, Fraction(43, 323), Fraction(1, 500))
    assert got == pattern_of(2, 15, PRIMES)


def test_e2_wrong_pattern_without_global_eta():
    got, truth = e2_large_support_needs_global_eta()
    assert got != truth
    # and the corrected global constant excludes the offending noise
    assert Fraction(1, 4845) > Fraction(1, 2 * 323 * 323)


def test_e3_exhaustive_per_instance_eta_clean():
    fails, trials = e3_per_instance_eta(ell=2)
    assert fails == 0 and trials == 5820


def test_e4_exhaustive_global_eta_clean():
    fails, trials = e4_global_eta(ell=2)
    assert fails == 0 and trials == 3880


def test_no_spurious_accept_at_or_below_true_denominator():
    # The repaired proof's load-bearing step, checked exhaustively at l=2:
    # every accepted candidate with denominator <= P_S is the truth itself.
    from attack_cf_uniqueness import all_patterns
    for theta, a in all_patterns(PRIMES, 2):
        P_S = prod(PRIMES[i] for i in range(len(PRIMES)) if a[i])
        eta = Fraction(1, 2 * P_S * P_S) - Fraction(1, 10 ** 12)
        for h, k in cf_accepts(PRIMES, 2, (theta + eta) % 1, eta):
            if k <= P_S:
                assert Fraction(h, k) == theta, (h, k, a)
