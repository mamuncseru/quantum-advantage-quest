"""Tests for the ceiling and the cost — notes.md sections 3-7.

Two of these earn their keep more than the rest:
`test_query_attention_sums_to_exactly_T` is the BBBV hybrid argument
checked on a real state vector, and
`test_more_classical_cores_push_the_crossover_further_out` pins a sign that
is easy to get backwards and that flips the conclusion when you do.
"""

import sys
from math import log2, pi, sqrt
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pytest

from grover import grover
from grover_limits import (bbbv_bound, bbht_expected_queries,
                           optimal_iterations, overshoot_curve,
                           parallel_speedup_classical,
                           parallel_speedup_quantum,
                           queries_for_constant_distinguishability,
                           query_magnitudes, simulated_success,
                           success_probability, theta, zalka_ceiling)
from grover_resources import (CLASSICAL_OP_S, LOGICAL_OP_S, circuit_cost,
                              classical_time, crossover_N,
                              crossover_with_parallel_classical, feasibility,
                              iterations, parallel_time, sequential_time,
                              years)


# ================================================== the rotation ===========

@pytest.mark.parametrize("n", [3, 4, 5, 6])
def test_formula_matches_the_circuit_at_every_step(n):
    """The 2-D rotation picture is not an approximation: it is exact, at
    every iteration count, for the real circuit."""
    N = 1 << n
    for t in range(0, 2 * optimal_iterations(N, 1) + 2):
        assert simulated_success(n, (1,), t) == pytest.approx(
            success_probability(N, 1, t), abs=1e-10)


@pytest.mark.parametrize("n,M", [(6, 1), (6, 2), (7, 1), (8, 1), (8, 4)])
def test_optimal_iterations_are_the_first_peak(n, M):
    """No iteration count up to 2t does better than t. (The claim is about
    the first arch: sin^2 is periodic, so later peaks exist and cost more
    queries — nobody wants those.)"""
    N = 1 << n
    t = optimal_iterations(N, M)
    best = max(range(0, 2 * t + 2), key=lambda u: success_probability(N, M, u))
    assert success_probability(N, M, best) <= \
        success_probability(N, M, t) + 1e-12


@pytest.mark.parametrize("n", [6, 8, 10, 12])
def test_optimal_iterations_nearly_certain(n):
    N = 1 << n
    assert success_probability(N, 1, optimal_iterations(N, 1)) > 0.99


@pytest.mark.parametrize("n", [6, 8, 10, 12])
def test_the_souffle_running_twice_as_long_is_much_worse(n):
    """More queries can be worse — the property that separates Grover from
    every classical "keep trying" search, and the reason you must know N and
    M before you start."""
    N = 1 << n
    t = optimal_iterations(N, 1)
    assert success_probability(N, 1, 2 * t) < 0.01
    assert success_probability(N, 1, t) > 0.99


def test_the_curve_oscillates_rather_than_settling():
    N = 1 << 10
    curve = overshoot_curve(N, 1, 4 * optimal_iterations(N, 1))
    assert max(curve) > 0.99
    assert min(curve) < 0.01
    peaks = [i for i in range(1, len(curve) - 1)
             if curve[i] > curve[i - 1] and curve[i] > curve[i + 1]]
    assert len(peaks) >= 2                     # it comes back around


# ====================================== BBBV, run on the state vector ======

@pytest.mark.parametrize("n,T", [(4, 3), (6, 6), (8, 12), (10, 25)])
def test_query_attention_sums_to_exactly_T(n, T):
    """The sum rule that IS the hybrid argument: T queries deposit exactly T
    units of attention across the items, no matter what the algorithm does
    in between."""
    assert query_magnitudes(n, T).sum() == pytest.approx(T, abs=1e-9)


@pytest.mark.parametrize("n", [4, 6, 8, 10])
def test_some_item_is_almost_ignored(n):
    """Consequence: with T units spread over N items, the least-attended one
    receives at most T/N — and marking that item is what the algorithm
    cannot notice."""
    N = 1 << n
    T = optimal_iterations(N, 1)
    mags = query_magnitudes(n, T)
    assert mags.min() <= T / N + 1e-12


def test_the_bound_forces_a_square_root():
    """2T/sqrt(N) must reach a constant before the marked and unmarked runs
    can be told apart, so T grows like sqrt(N). Checked as a statement about
    the numbers rather than a paraphrase of the proof."""
    for n in (10, 14, 18, 20):
        N = 1 << n
        T_needed = queries_for_constant_distinguishability(N, deviation=1.0)
        assert bbbv_bound(N, T_needed) == pytest.approx(1.0)
        assert bbbv_bound(N, T_needed / 2) < 1.0        # too few: forbidden
    small, large = (queries_for_constant_distinguishability(1 << k)
                    for k in (10, 20))
    assert large / small == pytest.approx(2 ** 5, rel=1e-9)   # sqrt scaling


@pytest.mark.parametrize("n", [4, 6, 8])
def test_the_circuit_never_beats_the_ceiling(n):
    """Zalka closed the constant, so the bound is exactly the Grover curve.
    The simulated circuit is checked against it at every step — it touches
    the ceiling and never crosses it."""
    N = 1 << n
    for t in range(0, 2 * optimal_iterations(N, 1) + 2):
        assert simulated_success(n, (5,), t) <= zalka_ceiling(N, 1, t) + 1e-10


# ============================================= not knowing M ===============

@pytest.mark.parametrize("N,M", [(4096, 1), (4096, 4), (16384, 1)])
def test_bbht_stays_within_a_constant_of_knowing_M(N, M):
    """Not knowing the number of solutions costs a constant factor, not an
    asymptotic one — but it does cost, and it needs a classical check of
    every candidate, which quietly requires a computed predicate."""
    rng = np.random.default_rng(1)
    measured = bbht_expected_queries(N, M, rng, trials=250)
    ideal = sqrt(N / M)
    assert ideal <= measured <= 3 * ideal


# ================================================ parallelism ==============

@pytest.mark.parametrize("k", [4, 100, 10 ** 6])
def test_quantum_parallelism_is_only_a_square_root(k):
    assert parallel_speedup_quantum(k) == pytest.approx(sqrt(k))
    assert parallel_speedup_classical(k) == pytest.approx(k)
    assert parallel_speedup_classical(k) > parallel_speedup_quantum(k)


# ================================================ the cost =================

def test_iteration_count_for_a_128_bit_key():
    assert iterations(128) == pytest.approx(pi / 4 * 2 ** 64)
    assert iterations(128) == pytest.approx(1.45e19, rel=1e-2)


def test_the_headline_needs_no_oracle_model():
    """Even charging ONE logical operation for an entire Grover iteration —
    absurdly generous — a 128-bit key search runs for millions of years."""
    t = sequential_time(128, ops_per_iteration=1)
    assert years(t) > 1e6
    assert years(sequential_time(128, ops_per_iteration=2 ** 13)) > 1e10


def test_parallel_scaling_of_the_two_sides():
    base_q = parallel_time(128, 1)
    base_c = classical_time(128, cores=1)
    assert parallel_time(128, 10 ** 6) == pytest.approx(base_q / 10 ** 3)
    assert classical_time(128, cores=10 ** 6) == pytest.approx(base_c / 10 ** 6)


def test_crossover_formula():
    ratio = LOGICAL_OP_S / CLASSICAL_OP_S
    assert crossover_N() == pytest.approx((2 * ratio) ** 2)
    assert log2(crossover_N()) == pytest.approx(35, abs=0.5)


@pytest.mark.parametrize("cores", [10 ** 3, 10 ** 6, 10 ** 9])
def test_more_classical_cores_push_the_crossover_further_out(cores):
    """Every core the classical side buys raises the size at which Grover
    starts winning — because classical search divides by k and Grover only
    by sqrt(k). Getting this division backwards inverts the conclusion of
    the whole section, so it is pinned."""
    assert crossover_with_parallel_classical(cores) > crossover_N()
    assert crossover_with_parallel_classical(cores) == pytest.approx(
        crossover_N() * cores ** 2)


def test_a_slower_quantum_clock_makes_it_worse():
    assert crossover_N(quantum_op_s=1e-3) > crossover_N(quantum_op_s=25e-6)


# =================================== even a toy Grover, on real machines ===

def test_toy_circuit_cost():
    c = circuit_cost(8)
    assert c["iterations"] == optimal_iterations(256, 1)
    assert c["cnot"] == 6 * c["toffoli"]
    assert c["qubits"] > 8                      # ancillas are not free


def test_no_existing_machine_runs_grover_on_twelve_qubits():
    """N = 4096 is a search space a classical laptop finishes instantly, and
    it is already past every machine in the catalog."""
    _, _, rows = feasibility(12)
    assert rows, "the catalog should assess something"
    assert all(r["verdict"] in ("NO", "TOO SMALL", "BLOCKED") for r in rows)
    assert max(r["fidelity"] for r in rows) < 0.01


def test_the_toy_circuit_agrees_with_the_simulator():
    """The gate counts describe the same algorithm the simulator runs."""
    c = circuit_cost(8)
    p, k = grover(8, marked=137)
    assert k == c["iterations"]
    assert p > 0.99
