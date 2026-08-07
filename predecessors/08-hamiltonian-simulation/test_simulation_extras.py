"""Tests for the classical wall and the cost comparison.

The two that carry the page: `test_only_the_quench_is_exponential` pins the
three-regime picture that makes the frontier instance-wise, and
`test_the_ratio_moves_the_crossover` pins the claim that alpha over the
commutator norm — not the word "chemistry" — is what decides Trotter versus
qubitization.
"""

import sys
from math import log2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pytest

from entanglement_wall import (bond_dimension_needed, classical_memory_bytes,
                               entanglement_entropy, ground_state_entropy,
                               ground_state_scaling, growth_rate,
                               product_state, quench, tfim_sparse)
from simulation_cost import (SUZUKI_STAGES, best_trotter, bound_looseness,
                             crossover_epsilon, long_range_profile,
                             mean_looseness, qubitization_cost, tfim_profile,
                             trotter_cost, winner)


# ============================================ the classical wall ===========

def test_a_product_state_has_no_entanglement():
    assert entanglement_entropy(product_state(8), 8) == pytest.approx(
        0.0, abs=1e-12)
    assert bond_dimension_needed(product_state(8), 8) == 1


def test_entropy_grows_linearly_under_a_quench():
    """The mechanism of the tensor-network wall: S ~ t, so the bond
    dimension is 2^S and the classical cost is exponential in *time*."""
    n = 12
    times = np.array([0.5, 1.0, 1.5, 2.0, 2.5, 3.0, 3.5, 4.0])
    rows = quench(n, times)
    ss = np.array([r[1] for r in rows])
    assert np.all(np.diff(ss) > 0)                     # monotone
    slope, _ = np.polyfit(times, ss, 1)
    assert 0.5 < slope < 1.5                           # measured ~0.94
    resid = ss - np.polyval(np.polyfit(times, ss, 1), times)
    assert np.max(np.abs(resid)) < 0.15                # genuinely linear


def test_bond_dimension_tracks_two_to_the_entropy():
    n = 12
    rows = quench(n, np.array([1.0, 2.0, 3.0, 4.0]))
    for _, s, chi in rows:
        assert 1 <= chi <= 2 ** (s + 2) + 2
    chis = [r[2] for r in rows]
    assert chis == sorted(chis)


@pytest.mark.parametrize("g", [0.5, 2.0])
def test_gapped_ground_states_obey_an_area_law(g):
    """Flat in n: constant bond dimension, which is why DMRG has eaten these
    since 1992. Two thirds of 'classical methods fail' is not true."""
    assert abs(ground_state_scaling(g, ns=(6, 8, 10, 12, 14))) < 0.05


def test_the_critical_point_is_logarithmic_and_matches_the_cft():
    """At g = 1 the chain is critical: S ~ (c/6) log2 n with c = 1/2 for the
    Ising universality class. Still only polynomial cost — harder, not hard."""
    slope = ground_state_scaling(1.0, ns=(6, 8, 10, 12, 14, 16))
    assert slope == pytest.approx(1 / 12, abs=0.04)
    assert slope > ground_state_scaling(2.0, ns=(6, 8, 10, 12, 14, 16))


def test_only_the_quench_is_exponential():
    """The three regimes, compared fairly: how much entropy does *doubling
    the resource* buy? For the quench the resource is time (t: 2 -> 4); for a
    ground state it is system size (n: 6 -> 12). Only the quench accumulates
    enough to put 2^S out of reach."""
    rows = quench(12, np.array([2.0, 4.0]))
    quench_gain = rows[1][1] - rows[0][1]
    critical_gain = (ground_state_entropy(12, g=1.0)
                     - ground_state_entropy(6, g=1.0))
    gapped_gain = abs(ground_state_entropy(12, g=2.0)
                      - ground_state_entropy(6, g=2.0))
    assert quench_gain > 10 * critical_gain
    assert critical_gain > gapped_gain
    assert gapped_gain < 0.01                      # flat: the area law


def test_memory_model_is_quadratic_in_bond_dimension():
    assert classical_memory_bytes(200, 50) == pytest.approx(
        4 * classical_memory_bytes(100, 50))


def test_hamiltonian_is_hermitian():
    H = tfim_sparse(6).toarray()
    assert np.abs(H - H.conj().T).max() < 1e-12


# ============================================== the cost comparison ========

def test_commutator_is_tighter_than_the_product_of_norms():
    for n in (4, 6, 8):
        p = tfim_profile(n)
        assert p["comm"] < p["naive"]


def test_the_two_bounds_scale_differently():
    """||[A,B]|| ~ n for a chain, ||A||·||B|| ~ n^2. That difference is the
    whole reason the modern Trotter analysis changed the picture."""
    ns = np.array([4, 5, 6, 7, 8], dtype=float)
    comm = np.array([tfim_profile(int(x))["comm"] for x in ns])
    naive = np.array([tfim_profile(int(x))["naive"] for x in ns])
    a_comm = np.polyfit(np.log(ns), np.log(comm), 1)[0]
    a_naive = np.polyfit(np.log(ns), np.log(naive), 1)[0]
    assert 0.8 < a_comm < 1.3
    assert 1.8 < a_naive < 2.4       # n(n-1) fits slightly above 2 at small n


def test_trotter_beats_its_own_bound_by_a_stable_factor():
    """~3.2x, and stable across step counts — so it is a real constant, not
    one lucky data point."""
    rows = bound_looseness(n=6)
    ratios = [r[3] for r in rows]
    assert all(x > 1.0 for x in ratios)
    assert max(ratios) - min(ratios) < 0.3
    assert 2.5 < mean_looseness() < 4.5


def test_qubitization_is_linear_in_time():
    """alpha*t + log(1/eps): doubling t does not double the cost, because of
    the constant log term — so linearity is the statement that equal steps in
    t give equal increments in cost."""
    p = tfim_profile(6)
    c = [qubitization_cost(p, t, 1e-6) for t in (10.0, 20.0, 30.0, 40.0)]
    steps = np.diff(c)
    assert np.allclose(steps, steps[0], rtol=1e-9)


@pytest.mark.parametrize("order", [2, 4, 6])
def test_higher_orders_scale_better_in_precision(order):
    p = tfim_profile(6)
    coarse = trotter_cost(p, 10.0, 1e-3, order)
    fine = trotter_cost(p, 10.0, 1e-9, order)
    k = order // 2
    assert fine / coarse == pytest.approx(1000 ** (1.0 / k), rel=0.15)


def test_the_best_order_rises_as_precision_tightens():
    p = tfim_profile(8)
    orders = [best_trotter(p, 10.0, e)[0] for e in (1e-2, 1e-6, 1e-12)]
    assert orders == sorted(orders)


def test_the_ratio_moves_the_crossover():
    """The finding. alpha/||[A,B]|| is the knob: a Hamiltonian whose weight
    sits in a commuting block gives Trotter a far wider window, and the
    crossover moves with the ratio rather than with the word 'chemistry'."""
    L = mean_looseness()
    tight = long_range_profile(8, g=1.0)      # ratio ~0.8
    loose = long_range_profile(8, g=0.01)     # ratio ~48
    assert loose["alpha"] / loose["comm"] > 10 * tight["alpha"] / tight["comm"]
    x_tight = crossover_epsilon(tight, 10.0, L)
    x_loose = crossover_epsilon(loose, 10.0, L)
    assert x_loose < x_tight        # smaller eps = Trotter wins further down


def test_trotter_wins_only_in_its_window():
    """Concretely: at eps = 1e-2 the commuting-dominated Hamiltonian goes to
    Trotter and the balanced one does not."""
    L = mean_looseness()
    assert winner(long_range_profile(8, g=0.01), 10.0, 1e-2, L)[0] == "Trotter"
    assert winner(long_range_profile(8, g=1.0), 10.0, 1e-2, L)[0] == \
        "qubitization"


def test_the_folklore_fails_on_a_plain_local_chain():
    """'Trotter wins at chemically relevant precision on local Hamiltonians'
    does not survive contact with the nearest-neighbour Ising chain."""
    L = mean_looseness()
    assert winner(tfim_profile(8), 10.0, 1e-4, L)[0] == "qubitization"


def test_suzuki_stage_counts_are_declared():
    assert SUZUKI_STAGES[2] < SUZUKI_STAGES[4] < SUZUKI_STAGES[6]
