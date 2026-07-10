import sys
from fractions import Fraction
from itertools import islice
from pathlib import Path

import sympy

sys.path.insert(0, str(Path(__file__).parent))

from cf_decode import (balanced_moduli, cf_decode, convergents, factor_over,
                       noisy, plant)


def test_convergents_of_pi_approx():
    # classical sanity: convergents of 355/113 include 22/7 and itself
    cs = convergents(Fraction(355, 113))
    assert (22, 7) in cs and (355, 113) in cs


def test_factor_over_rejects_squarefull_and_foreign():
    moduli = [3, 5, 7]
    assert factor_over(moduli, 15) == [0, 1]
    assert factor_over(moduli, 9) is None       # 3^2: squarefull
    assert factor_over(moduli, 33) is None      # 11 is foreign


def test_noise_free_recovery_where_lll_failed():
    # lll_decode.py: 12-38% on these; CF must be exact
    for m in (12, 16):
        moduli = [int(p) for p in islice(sympy.primerange(3, 10 ** 7), m)]
        for ell in (1, 2, 3):
            for seed in range(4):
                a, theta = plant(moduli, ell, seed + 100 * m)
                assert cf_decode(moduli, ell, theta, Fraction(0)) == a


def test_window_threshold_two_sides():
    # kappa = 0.3: ell/m = 0.1 decodes, ell/m = 0.2 hits the d_min wall
    m = 20
    moduli = balanced_moduli(m, 1000)
    M = 1
    for p in moduli:
        M *= p
    eta = Fraction(1, sympy.integer_nthroot(M ** 3, 10)[0])
    ok_low = ok_high = 0
    for seed in range(6):
        a, theta = plant(moduli, 2, 500 + seed)
        ok_low += (cf_decode(moduli, 2, noisy(theta, eta, seed), eta) == a)
        a, theta = plant(moduli, 4, 600 + seed)
        ok_high += (cf_decode(moduli, 4, noisy(theta, eta, seed), eta) == a)
    assert ok_low == 6           # strictly inside the window: always
    assert ok_high <= 2          # beyond kappa/2: information-theoretic wall


def test_linear_sparsity_is_fast():
    # ell = m/10 at m = 80: enumeration is ~80^8; CF is instant
    m = 80
    moduli = balanced_moduli(m, 1000)
    M = 1
    for p in moduli:
        M *= p
    eta = Fraction(1, sympy.integer_nthroot(M ** 3, 10)[0])
    for seed in range(3):
        a, theta = plant(moduli, 8, 900 + seed)
        assert cf_decode(moduli, 8, noisy(theta, eta, seed), eta) == a


def test_recovered_pattern_reconstructs_theta():
    # end-to-end consistency: decoded coefficients re-sum to within eta
    m = 24
    moduli = balanced_moduli(m, 1000)
    M = 1
    for p in moduli:
        M *= p
    eta = Fraction(1, sympy.integer_nthroot(M ** 3, 10)[0])
    a, theta = plant(moduli, 3, 42)
    tn = noisy(theta, eta, 42)
    got = cf_decode(moduli, 3, tn, eta)
    resum = sum(Fraction(got[i], moduli[i]) for i in range(m) if got[i]) % 1
    d = abs(tn - resum)
    assert min(d, 1 - d) <= eta
