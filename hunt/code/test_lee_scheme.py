import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lee_scheme import (distance_matrices, distinct_eigs_of_A1,
                        is_association_scheme)


def test_hamming_cases_are_p_polynomial():
    # q <= 3: Lee == Hamming, must be a P-polynomial scheme (sanity)
    for q, n in [(3, 2), (3, 3)]:
        A, D = distance_matrices(q, n)
        sched, _ = is_association_scheme(A, D)
        assert sched
        assert distinct_eigs_of_A1(A) == D + 1


def test_z4_is_p_polynomial():
    # the special Z_4 case (Kerdock/Preparata): base eigenvalues {-2,0,2} AP
    A, D = distance_matrices(4, 2)
    sched, _ = is_association_scheme(A, D)
    assert sched and distinct_eigs_of_A1(A) == D + 1


def test_lee_q5_is_not_even_a_scheme():
    # the kill: Lee on Z_5^2 fails the association-scheme axiom outright
    A, D = distance_matrices(5, 2)
    sched, witness = is_association_scheme(A, D)
    assert sched is False
    assert witness is not None            # a concrete (i,j,k) witness exists


def test_lee_q567_all_fail():
    for q, n in [(5, 2), (6, 2), (7, 2)]:
        A, D = distance_matrices(q, n)
        sched, _ = is_association_scheme(A, D)
        assert sched is False
