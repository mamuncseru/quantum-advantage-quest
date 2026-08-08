"""Tests for the gap, the two classical walls, and the recipe.

Two carry the page: `test_a_bipartite_chain_has_no_sign_problem` is a
correction to the obvious reading (non-commuting does not mean signful, and
the repo's own demo Hamiltonian is not a hard instance), and
`test_the_knob_breaks_the_dequantizer_and_keeps_the_mixer` is the Bakshi-Tan
template, executed.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pytest

from davies import gibbs_state, heisenberg_with_fields
from dequantizer_window import (find_window, frustration_family,
                                gap_cost_ratio, is_window, knob_sweep,
                                profile, window_scan)
from gibbs_gap import (average_sign, davies_gap, frustrated_afm,
                       gap_scaling_in_beta, is_stoquastic, mixing_time,
                       qmc_overhead, stoquasticised,
                       thermal_mutual_information, transverse_ising)


# ==================================================== the gap =============

@pytest.mark.parametrize("beta", [0.25, 1.0, 4.0])
def test_the_gap_is_open(beta):
    assert davies_gap(heisenberg_with_fields(3), beta) > 0.1


def test_cooling_costs_mixing_time():
    """The gap shrinks as the sampler cools — the same story classical MCMC
    tells, and the reason 'prove the gap' is the frontier."""
    H = heisenberg_with_fields(3)
    gaps = [davies_gap(H, b) for b in (0.25, 0.5, 1.0, 2.0)]
    assert gaps == sorted(gaps, reverse=True)
    assert gap_scaling_in_beta(H) > 0


def test_mixing_time_is_the_inverse_gap():
    H = heisenberg_with_fields(3)
    g = davies_gap(H, 1.0)
    assert mixing_time(H, 1.0) == pytest.approx(np.log(1000.0) / g)


# ============================================== wall 1: the sign ==========

def test_a_stoquastic_model_has_no_sign_problem():
    H = transverse_ising(3)
    assert is_stoquastic(H)
    for beta in (1.0, 4.0):
        assert average_sign(H, beta) == pytest.approx(1.0, abs=1e-9)
        assert qmc_overhead(H, beta) == pytest.approx(1.0, abs=1e-8)


def test_a_bipartite_chain_has_no_sign_problem():
    """The correction. A Heisenberg chain is thoroughly non-commuting and
    NOT stoquastic in this basis, yet its average sign is exactly 1 — it is
    bipartite, so the Marshall sign rule removes the problem. The chain
    `davies.py` demonstrates on is a witness for the mechanism, not for the
    hardness."""
    H = heisenberg_with_fields(3)
    assert not is_stoquastic(H)
    for beta in (1.0, 2.0, 4.0):
        assert average_sign(H, beta) == pytest.approx(1.0, abs=1e-9)


def test_frustration_is_what_creates_the_sign_problem():
    """Close the chain into an odd cycle and the sign collapses
    exponentially in beta."""
    H = frustrated_afm(3)
    signs = [average_sign(H, b) for b in (1.0, 2.0, 4.0)]
    assert signs == sorted(signs, reverse=True)
    assert signs[0] < 0.5
    assert signs[-1] < 0.01
    assert qmc_overhead(H, 4.0) > 1e5


def test_the_sign_problem_worsens_with_size():
    assert average_sign(frustrated_afm(4), 2.0) < \
        average_sign(frustrated_afm(3), 2.0)


def test_stoquasticised_is_stoquastic():
    for H in (heisenberg_with_fields(3), frustrated_afm(3)):
        assert is_stoquastic(stoquasticised(H))


def test_average_sign_never_exceeds_one():
    for H in (heisenberg_with_fields(3), frustrated_afm(3),
              transverse_ising(3)):
        for beta in (0.5, 2.0):
            assert average_sign(H, beta) <= 1.0 + 1e-12


# ======================================= wall 2: the entanglement =========

def test_hot_thermal_states_are_nearly_product():
    """High temperature is classically easy, which is why the provably-easy
    atlas covers it and the advantage has to live at intermediate beta."""
    H = heisenberg_with_fields(4)
    assert thermal_mutual_information(H, 0.05) < 0.05


def test_correlation_grows_as_the_state_cools():
    H = heisenberg_with_fields(4)
    mis = [thermal_mutual_information(H, b) for b in (0.1, 0.5, 1.0, 2.0)]
    assert mis == sorted(mis)


def test_mutual_information_is_non_negative():
    H = heisenberg_with_fields(3)
    for beta in (0.1, 1.0, 5.0):
        assert thermal_mutual_information(H, beta) >= -1e-9


def test_gibbs_state_is_a_state():
    rho = gibbs_state(heisenberg_with_fields(3), 1.5)
    assert np.trace(rho).real == pytest.approx(1.0)
    assert np.linalg.eigvalsh(rho).min() > -1e-12


# ============================================ the recipe ==================

def test_the_knob_moves_the_classical_cost_by_orders_of_magnitude():
    rows = knob_sweep(n=3, beta=3.0)
    assert rows[0]["qmc"] == pytest.approx(1.0, abs=1e-6)     # λ = 0: free
    assert rows[-1]["qmc"] > 1e4                              # λ = 1: not


def test_the_knob_barely_moves_the_hamiltonian():
    """The knob has to be honest: if it changed the norm or the locality,
    the comparison would be between two different problems."""
    rows = knob_sweep(n=3, beta=3.0)
    norms = [r["norm"] for r in rows]
    assert max(norms) / min(norms) < 1.35


def test_the_knob_breaks_the_dequantizer_and_keeps_the_mixer():
    """The Bakshi-Tan template, executed: classical cost up by four orders
    of magnitude while the quantum mixing time does not degrade at all."""
    rows = knob_sweep(n=3, beta=3.0)
    lo, hi = rows[0], rows[-1]
    assert hi["qmc"] / max(lo["qmc"], 1.0) > 1e4      # dequantizer broken
    assert hi["gap"] >= lo["gap"] * 0.9               # mixer kept
    assert hi["mixing"] <= lo["mixing"] * 1.1


def test_the_window_is_non_empty_and_needs_both_conditions():
    hits = find_window(n=3)
    assert len(hits) >= 3
    for row in hits:
        assert row["qmc"] >= 100.0 and row["gap"] >= 0.25
    easy = profile(3, 0.0, 1.0)                       # no frustration
    assert not is_window(easy)                        # classical is fine


def test_both_axes_matter():
    """Neither knob alone puts you in the window: frustration at high
    temperature is cheap, and cold without frustration is sign-free."""
    assert not is_window(profile(3, 1.0, 0.5))        # hot
    assert not is_window(profile(3, 0.0, 4.0))        # unfrustrated


def test_the_scan_has_the_shape_it_claims():
    scan = window_scan(n=3, lams=(0.0, 0.5, 1.0), betas=(0.5, 1.0, 2.0, 4.0))
    for row in scan:                                  # colder is costlier
        assert [r["qmc"] for r in row] == sorted([r["qmc"] for r in row])
    coldest = [rows[-1]["qmc"] for rows in scan]      # more frustration too
    assert coldest == sorted(coldest)


def test_the_ratio_moves_the_right_way():
    lo = gap_cost_ratio(profile(3, 0.0, 3.0))
    hi = gap_cost_ratio(profile(3, 1.0, 3.0))
    assert hi > 1e3 * lo


def test_frustration_family_reduces_to_the_open_chain():
    H0 = frustration_family(3, 0.0)
    assert average_sign(H0, 3.0) == pytest.approx(1.0, abs=1e-9)
