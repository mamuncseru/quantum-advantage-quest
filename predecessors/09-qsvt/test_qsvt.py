import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from qsvt_demo import (chebyshev_of_matrix, random_hermitian, top_left_block,
                       walk_operator)


def test_walk_operator_is_unitary():
    A = random_hermitian(6, seed=3)
    W = walk_operator(A)
    assert np.allclose(W @ W.conj().T, np.eye(12))


def test_powers_give_chebyshev_polynomials():
    A = random_hermitian(6, seed=4)
    W = walk_operator(A)
    Wd = np.eye(12)
    for d in range(1, 8):
        Wd = Wd @ W
        assert np.allclose(top_left_block(Wd, 6), chebyshev_of_matrix(A, d),
                           atol=1e-10)
