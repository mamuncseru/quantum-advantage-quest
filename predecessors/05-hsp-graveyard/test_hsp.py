"""Tests for the abelian side: one machine, three algorithms.

The claim this file exists to pin is structural, not numeric — that
`hsp_sample` is *the same function* for Bernstein-Vazirani, Simon and
order-finding, and that only the classical post-processor changes.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pytest

from abelian_hsp import (AbelianGroup, bv_instance, dj_balanced_nonlinear_instance,
                         dj_constant_instance, fibers, fibers_are_cosets,
                         hsp_sample, order_instance, sample_distribution,
                         simon_instance, solve, solve_z2n, solve_zN_order)


# ----------------------------------------------------------- the group -----

@pytest.mark.parametrize("dims", [(2, 2, 2), (4,), (2, 4), (6,), (3, 3)])
def test_encode_decode_round_trip(dims):
    G = AbelianGroup(dims)
    for i in range(G.order):
        assert G.encode(G.decode(i)) == i


@pytest.mark.parametrize("dims", [(2, 2), (2, 2, 2), (4,), (6,), (2, 4)])
def test_group_fourier_transform_is_unitary(dims):
    F = AbelianGroup(dims).dft_matrix()
    assert np.abs(F.conj().T @ F - np.eye(F.shape[0])).max() < 1e-10


@pytest.mark.parametrize("dims,gens", [
    ((2, 2, 2), [(1, 0, 1)]),
    ((2, 2, 2), [(1, 1, 0), (0, 0, 1)]),
    ((4,), [(2,)]),
    ((2, 4), [(1, 2)]),
    ((6,), [(2,)]),
])
def test_annihilator_has_the_complementary_size(dims, gens):
    """|H| |H-perp| = |G|, for every subgroup of every group here."""
    G = AbelianGroup(dims)
    H = G.subgroup(gens)
    assert len(H) * len(G.annihilator(H)) == G.order


@pytest.mark.parametrize("dims,count", [((2, 2), 5), ((2, 2, 2), 16),
                                        ((4,), 3), ((6,), 4), ((3, 3), 6)])
def test_all_subgroups_is_exhaustive(dims, count):
    """Subspace counts for F_2^n and divisor counts for cyclic groups —
    the enumeration must find exactly the known number."""
    assert len(AbelianGroup(dims).all_subgroups()) == count


# ------------------------------------------- the promise, actually checked --

def test_bv_fibers_are_cosets_of_a_hyperplane():
    group, f, H = bv_instance(4, (1, 0, 1, 1))
    assert len(H) == 8
    assert fibers_are_cosets(f, group, H)


def test_simon_fibers_are_cosets_of_the_period():
    rng = np.random.default_rng(2)
    group, f, H = simon_instance(4, (1, 1, 0, 1), rng)
    assert H == [(0, 0, 0, 0), (1, 1, 0, 1)]
    assert fibers_are_cosets(f, group, H)


def test_order_finding_fibers_are_cosets_of_rZ():
    group, f, H, r = order_instance(16, 7, 15)
    assert r == 4
    assert len(H) == 16 // r
    assert fibers_are_cosets(f, group, H)


def test_constant_f_hides_the_whole_group():
    group, f, H = dj_constant_instance(3)
    assert len(H) == group.order
    assert fibers_are_cosets(f, group, H)


def test_deutsch_jozsa_is_not_an_hsp_instance():
    """A balanced, non-linear f hides nothing: checked against *every*
    subgroup of Z_2^3, not a sample of them. Deutsch-Jozsa is routinely
    listed as a member of this family; for any f that is neither constant
    nor linear, it is not one."""
    group, f = dj_balanced_nonlinear_instance(3)
    subs = group.all_subgroups()
    assert len(subs) == 16
    assert not any(fibers_are_cosets(f, group, H) for H in subs)


# ------------------------------------------------- the quantum step, once ---

@pytest.mark.parametrize("seed", [0, 1, 2])
def test_samples_always_land_in_the_annihilator(seed):
    """The annihilator theorem, verified by running the simulator rather
    than by quoting it: 200 real samples, none outside H-perp."""
    rng = np.random.default_rng(seed)
    group, f, H = simon_instance(4, (1, 0, 1, 1), rng)
    allowed = set(group.annihilator(H))
    for _ in range(200):
        assert hsp_sample(f, group, rng) in allowed


def test_sample_distribution_is_uniform_on_the_annihilator():
    group, f, H = bv_instance(4, (1, 1, 0, 1))
    p = sample_distribution(f, group)
    ann = {group.encode(k) for k in group.annihilator(H)}
    for i in range(group.order):
        assert p[i] == pytest.approx(1 / len(ann) if i in ann else 0.0,
                                     abs=1e-12)


def test_order_finding_samples_are_multiples_of_N_over_r():
    group, f, H, r = order_instance(16, 7, 15)
    p = sample_distribution(f, group)
    hits = np.flatnonzero(p > 1e-12)
    assert sorted(hits.tolist()) == [j * (16 // r) for j in range(r)]


# ---------------------------------------- one machine, three post-processors

def test_bernstein_vazirani_solved():
    rng = np.random.default_rng(4)
    group, f, H = bv_instance(5, (1, 0, 1, 1, 0))
    labels = [hsp_sample(f, group, rng) for _ in range(20)]
    nonzero = {k for k in labels if any(k)}
    assert nonzero == {(1, 0, 1, 1, 0)}          # the secret, read directly


def test_simon_solved():
    rng = np.random.default_rng(5)
    s = (1, 1, 0, 1)
    group, f, H = simon_instance(4, s, rng)
    got, shots = solve(f, group, rng, lambda L: solve_z2n(L, 4),
                       lambda H2: len(H2) == 2)
    assert got == [(0, 0, 0, 0), s]
    assert shots <= 20


def test_order_finding_solved():
    rng = np.random.default_rng(6)
    group, f, H, r = order_instance(16, 7, 15)
    got, shots = solve(f, group, rng, lambda L: solve_zN_order(L, 16),
                       lambda rr: rr == r)
    assert got == r
    assert shots <= 20


def test_the_quantum_step_is_literally_shared():
    """The three algorithms differ only after the sampling. This test runs
    all three through the same `solve` with the same `hsp_sample` and only
    swaps the callable that reads the labels."""
    rng = np.random.default_rng(7)
    runs = []
    g1, f1, H1 = bv_instance(4, (1, 0, 1, 1))
    runs.append(solve(f1, g1, rng, lambda L: solve_z2n(L, 4),
                      lambda H2: len(H2) == 8)[0] is not None)
    g2, f2, H2 = simon_instance(4, (1, 1, 0, 1), rng)
    runs.append(solve(f2, g2, rng, lambda L: solve_z2n(L, 4),
                      lambda H3: len(H3) == 2)[0] is not None)
    g3, f3, H3, r = order_instance(16, 7, 15)
    runs.append(solve(f3, g3, rng, lambda L: solve_zN_order(L, 16),
                      lambda rr: rr == r)[0] is not None)
    assert all(runs)


def test_fibers_partition_the_group():
    rng = np.random.default_rng(8)
    group, f, H = simon_instance(4, (0, 1, 1, 0), rng)
    parts = fibers(f, group)
    assert sum(len(v) for v in parts.values()) == group.order
    assert all(len(v) == len(H) for v in parts.values())
