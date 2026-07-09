import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from product_schemes import (cartesian, clebsch, complete_graph, cycle,
                             distances, distinct_eigs, doob, hamming_array,
                             intersection_array, is_distance_regular,
                             shrikhande)


def test_hamming_product_sanity():
    A = cartesian(complete_graph(4), complete_graph(4))
    dr, _ = is_distance_regular(A)
    assert dr
    assert intersection_array(A) == hamming_array(2, 4)


def test_shrikhande_has_rook_array_but_is_not_rook():
    # same intersection array as H(2,4), non-isomorphic: the neighbourhood
    # of a vertex is a 6-cycle (connected) vs two triangles in the rook.
    S, R = shrikhande(), cartesian(complete_graph(4), complete_graph(4))
    assert intersection_array(S) == intersection_array(R) == hamming_array(2, 4)

    def nbhd_connected(A):
        nz = np.nonzero(A[0])[0]
        sub = A[np.ix_(nz, nz)]
        reach = np.linalg.matrix_power(np.eye(len(nz)) + sub, len(nz))
        return bool((reach > 0).all())

    assert nbhd_connected(S) and not nbhd_connected(R)


def test_doob_family_is_dr_with_hamming_arrays():
    # the unique non-Hamming survivors: D(m,n) has H(2m+n, 4)'s array
    for m, n in [(1, 1), (2, 0)]:
        A = doob(m, n)
        dr, _ = is_distance_regular(A)
        assert dr
        assert intersection_array(A) == hamming_array(2 * m + n, 4)


def test_clebsch_is_srg_but_square_is_not_dr():
    C = clebsch()
    dr, _ = is_distance_regular(C)
    assert dr                                   # a fine graph on its own...
    dr2, wit = is_distance_regular(cartesian(C, C))
    assert dr2 is False                         # ...but its square dies
    j, k, lo, hi = wit
    assert (j, k) == (2, 2) and lo == 0.0 and hi == 3.0
    # mechanism: a_2 = k - mu = 3 for within-block distance-2 pairs but
    # 2*lambda = 0 for split (1,1) pairs — a_2 = 2*a_1 fails


def test_clebsch_k4_mix_fails_at_lambda():
    dr, wit = is_distance_regular(cartesian(clebsch(), complete_graph(4)))
    assert dr is False
    assert wit[:2] == (1, 1)      # p_11^1 = lambda differs across blocks


def test_lee_kill_is_the_c2_special_case():
    # C5 [] C5 = Lee metric on Z_5^2; cycles have c_2 = 1, split pairs give 2
    dr, wit = is_distance_regular(cartesian(cycle(5), cycle(5)))
    assert dr is False
    assert wit == (1, 2, 1.0, 2.0)


def test_ap_eigenvalues_are_not_sufficient():
    # all three blocks have AP eigenvalues with common difference 4, yet
    # only Shrikhande and K4 survive the product test — the intersection
    # axiom, not the spectrum, is the binding constraint
    for A in (shrikhande(), complete_graph(4), clebsch()):
        e = distinct_eigs(A)
        gaps = {round(e[i] - e[i + 1], 6) for i in range(len(e) - 1)}
        assert gaps == {4.0}
