import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from shrikhande_dqi import (conditional_bias, density, dqi_semicircle,
                            prange_slopes, radial_predicate, shells)


def test_shell_sizes():
    s = shells()
    assert [len(s[d]) for d in (0, 1, 2)] == [1, 6, 9]


def test_radius1_ball_density():
    supp = radial_predicate(1, 1, 0)      # shells 0 and 1
    assert len(supp) == 7
    assert density(supp) == 7 / 16


def test_conditional_bias_is_three_quarters():
    supp = radial_predicate(1, 1, 0)
    bias, desc = conditional_bias(supp)
    assert bias == 0.75                    # pin one form -> 3/4 satisfaction


def test_predicate_aware_beats_array_matched():
    supp = radial_predicate(1, 1, 0)
    mu, array_slope, aware_slope = prange_slopes(supp)
    assert np.isclose(array_slope, 9 / 32)
    assert np.isclose(aware_slope, 10 / 32)
    assert aware_slope > array_slope       # the K3 red flag, exact


def test_semicircle_is_alphabet_independent():
    # Eq 6 depends only on (mu, l/m): Doob at mu=7/16 == any scheme at mu=7/16
    for lm in (0.05, 0.1, 0.2):
        v = dqi_semicircle(7 / 16, lm)
        # matches the closed form with no q anywhere
        assert np.isclose(v, (np.sqrt(lm * 9 / 16)
                              + np.sqrt(7 / 16 * (1 - lm))) ** 2)
