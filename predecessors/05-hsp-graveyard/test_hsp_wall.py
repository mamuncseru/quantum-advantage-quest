"""Tests for the wall: the symmetric group, the dihedral group, and the
classical baseline that graph isomorphism was always being measured against.

Every number quoted in `notes.md` sections 4-7 is computed here.
"""

import sys
from math import factorial
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import pytest

from gi_baseline import (automorphism_count, color_refine, discrete_colouring,
                         is_strongly_regular, isomorphic_pairs_are_never_separated,
                         neighbourhood_signature, permute, random_graph,
                         random_pair_stats, rooks_graph, shrikhande_graph,
                         wl1_distinguishes, _complete, _cycle, _path)
from nonabelian_wall import (Dihedral, character, character_table,
                             class_size, dihedral_label_distribution,
                             dihedral_label_drift, dihedral_phase, dimension,
                             fixed_point_free_type, hook_length_dimension,
                             identity_type, partitions, samples_needed,
                             sieve_round, sieve_run, total_variation,
                             transposition_type, weak_sampling_distribution)


# ================================================= characters of S_n ========

@pytest.mark.parametrize("n,count", [(1, 1), (2, 2), (3, 3), (4, 5), (5, 7),
                                     (6, 11), (7, 15), (8, 22), (9, 30),
                                     (10, 42)])
def test_partition_counts(n, count):
    assert len(list(partitions(n))) == count


@pytest.mark.parametrize("n", [4, 5, 6, 7])
def test_dimensions_agree_with_the_hook_length_formula(n):
    """Murnaghan-Nakayama and the hook length formula are independent routes
    to the same number. Two implementations, one answer."""
    for lam in partitions(n):
        assert dimension(lam) == hook_length_dimension(lam)


@pytest.mark.parametrize("n", [3, 4, 5, 6, 7, 8])
def test_sum_of_squared_dimensions_is_the_group_order(n):
    assert sum(dimension(lam) ** 2 for lam in partitions(n)) == factorial(n)


@pytest.mark.parametrize("n", [4, 5, 6])
def test_character_table_is_orthogonal(n):
    """The first orthogonality relation, over conjugacy classes weighted by
    their sizes. If this passes, the table is right."""
    parts = list(partitions(n))
    tab = character_table(n)
    G = factorial(n)
    for lam in parts:
        for mu in parts:
            total = sum(class_size(rho, n) * tab[(lam, rho)] * tab[(mu, rho)]
                        for rho in parts)
            assert total == (G if lam == mu else 0)


@pytest.mark.parametrize("n", [4, 5, 6])
def test_known_characters(n):
    """The trivial representation is all ones; the sign representation is the
    sign of the permutation."""
    triv = (n,)
    sign = tuple([1] * n)
    for rho in partitions(n):
        assert character(triv, rho) == 1
        parity = (-1) ** sum(p - 1 for p in rho)
        assert character(sign, rho) == parity


@pytest.mark.parametrize("n", [4, 6, 8])
def test_weak_sampling_distributions_are_normalised(n):
    for H in ([identity_type(n)],
              [identity_type(n), transposition_type(n)],
              [identity_type(n), fixed_point_free_type(n)]):
        p = weak_sampling_distribution(n, H)
        assert sum(p.values()) == pytest.approx(1.0)
        assert min(p.values()) > -1e-12


# ==================================================== the S_n wall ==========

def test_a_transposition_stays_visible():
    """TV falls only like 1/n, so polynomially many copies still see it.
    The wall is not "non-abelian is hard" — it is specific."""
    tvs = [total_variation(n, transposition_type(n)) for n in (8, 16, 24)]
    assert tvs[0] > tvs[1] > tvs[2] > 0.02
    assert tvs[0] / tvs[2] < 4                      # slow decay, not a cliff


@pytest.mark.parametrize("n,want", [(8, 3.562e-2), (16, 1.979e-4),
                                    (24, 4.341e-7)])
def test_fixed_point_free_involution_numbers_quoted_in_the_notes(n, want):
    assert total_variation(n, fixed_point_free_type(n)) == pytest.approx(
        want, rel=1e-3)


def test_the_gi_relevant_involution_falls_off_a_cliff():
    """A perfect matching is the involution graph isomorphism actually hands
    you, and weak Fourier sampling cannot see it: each step of 2 in n costs
    at least a factor of 3, so the copies needed explode."""
    tvs = [total_variation(n, fixed_point_free_type(n))
           for n in range(8, 25, 2)]
    for a, b in zip(tvs, tvs[1:]):
        assert b < a / 3
    assert samples_needed(tvs[-1]) > 1e12


def test_transposition_and_matching_separate():
    """At n = 24 the easy involution is five orders of magnitude more visible
    than the hard one — same group, same measurement, different subgroup."""
    easy = total_variation(24, transposition_type(24))
    hard = total_variation(24, fixed_point_free_type(24))
    assert easy / hard > 1e4


# ================================================== the dihedral wall =======

@pytest.mark.parametrize("N", [5, 6, 7, 8])
def test_dihedral_fourier_is_unitary(N):
    F, labels = Dihedral(N).fourier_matrix()
    assert F.shape[0] == 2 * N == len(labels)
    assert np.abs(F.conj().T @ F - np.eye(2 * N)).max() < 1e-10


@pytest.mark.parametrize("N", [6, 7, 8, 9, 12])
def test_two_dimensional_labels_carry_nothing(N):
    """Exactly zero drift: the 2-dimensional representation label is
    independent of the hidden reflection, to machine precision, for every N."""
    _, two_dim_drift = dihedral_label_drift(Dihedral(N))
    assert two_dim_drift < 1e-12


@pytest.mark.parametrize("N", [5, 7, 9, 11])
def test_odd_N_leaks_nothing_at_all(N):
    allmax, _ = dihedral_label_drift(Dihedral(N))
    assert allmax < 1e-12


@pytest.mark.parametrize("N", [6, 8, 10, 12])
def test_even_N_leaks_exactly_the_parity_bit(N):
    """The one-dimensional representations do move — the usual slogan that
    the label says nothing is slightly wrong. It says one bit: whether the
    hidden reflection sits at an even or an odd offset."""
    allmax, _ = dihedral_label_drift(Dihedral(N))
    assert allmax > 0.01
    D = Dihedral(N)
    evens = {round(dihedral_label_distribution(D, d)["alt"], 9)
             for d in range(0, N, 2)}
    odds = {round(dihedral_label_distribution(D, d)["alt"], 9)
            for d in range(1, N, 2)}
    assert len(evens) == 1 and len(odds) == 1     # depends only on parity
    assert evens != odds                          # and it does depend on it


@pytest.mark.parametrize("N,d,k", [(8, 1, 1), (8, 3, 1), (12, 5, 1), (8, 2, 2)])
def test_the_secret_survives_only_as_a_phase(N, d, k):
    """Where the information actually went: the relative phase inside the
    two-dimensional block is exactly 2 pi k d / N."""
    D = Dihedral(N)
    got = dihedral_phase(D, d, k)
    want = (2 * np.pi * k * d / N) % (2 * np.pi)
    assert abs((got - want + np.pi) % (2 * np.pi) - np.pi) < 1e-9


# ================================================ Kuperberg's sieve =========

def test_sieve_round_clears_low_bits():
    """The whole move: combine two labels agreeing on their low bits and the
    difference has those bits zeroed."""
    rng = np.random.default_rng(0)
    labels = [int(rng.integers(1, 1 << 12)) for _ in range(3000)]
    out = sieve_round(labels, 5, rng)
    assert out, "the round should survive with this many copies"
    assert all(k % (1 << 5) == 0 for k in out)


def test_sieve_population_decays_but_progress_is_made():
    rng = np.random.default_rng(1)
    res = sieve_run(12, 4000, rng)
    hist = res["history"]
    assert hist[0] == 4000
    assert all(b < a for a, b in zip(hist, hist[1:]))
    assert res["rounds"] * res["block"] >= 12 - res["block"]


# ============================== the classical baseline for GI ==============

def test_colour_refinement_is_relabelling_invariant():
    rng = np.random.default_rng(3)
    for _ in range(10):
        a = random_graph(12, 0.5, rng)
        perm = rng.permutation(12)
        assert sorted(color_refine(a).tolist()) == \
            sorted(color_refine(permute(a, perm)).tolist())


def test_no_false_positives():
    """A one-sided test is only worth having if it never lies in the other
    direction."""
    rng = np.random.default_rng(4)
    assert isomorphic_pairs_are_never_separated(16, 30, rng)


@pytest.mark.parametrize("n", [12, 20, 40])
def test_random_graph_pairs_are_settled_instantly(n):
    """1968 colour refinement separates every random non-isomorphic pair we
    throw at it, and canonically labels the graphs outright by n = 20."""
    rng = np.random.default_rng(n)
    sep, disc = random_pair_stats(n, 25, rng)
    assert sep == 1.0
    if n >= 20:
        assert disc == 1.0


def test_the_hard_pair_is_strongly_regular_and_invisible_to_1wl():
    rook, shri = rooks_graph(), shrikhande_graph()
    assert is_strongly_regular(rook) == (16, 6, 2, 2)
    assert is_strongly_regular(shri) == (16, 6, 2, 2)
    assert not wl1_distinguishes(rook, shri)
    assert len(set(color_refine(rook).tolist())) == 1     # one colour, total
    assert not discrete_colouring(rook)


def test_one_more_cheap_invariant_walks_past_the_hard_pair():
    """Two disjoint triangles versus one 6-cycle. Both neighbourhoods have 6
    vertices and 6 edges, so no counting sees it — connectivity does. Since
    this is an isomorphism invariant, its disagreement is a *proof* that the
    two graphs are not isomorphic."""
    rook, shri = rooks_graph(), shrikhande_graph()
    assert neighbourhood_signature(rook) == ((3, 3),)
    assert neighbourhood_signature(shri) == ((6,),)
    assert neighbourhood_signature(rook) != neighbourhood_signature(shri)


@pytest.mark.parametrize("graph,count", [(_path(6), 2), (_cycle(6), 12),
                                         (_complete(6), 720)])
def test_automorphism_counts(graph, count):
    """|Aut(G)| — the hidden subgroup of S_n the reduction is aiming at."""
    assert automorphism_count(graph) == count
