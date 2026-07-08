import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from lll_decode import lll, lll_recover, plant


def _norm2(v):
    return sum(x * x for x in v)


def test_lll_reduces_known_lattice():
    # classic textbook example: LLL should shorten this basis
    B = [[1, 1, 1], [-1, 0, 2], [3, 5, 6]]
    red = lll(B)
    # first reduced vector is short and the basis stays integral
    assert all(all(isinstance(x, int) for x in row) for row in red)
    assert _norm2(red[0]) <= _norm2(B[0])
    # LLL guarantees b1 is within 2^((n-1)/2) of the shortest; here b1 nonzero
    assert _norm2(red[0]) > 0


def test_lll_finds_short_vector_orthogonal_case():
    B = [[10, 0], [0, 10]]
    red = lll(B)
    assert sorted(_norm2(r) for r in red) == [100, 100]


def test_naive_lattice_fails_on_sparse_recovery():
    """Documents the finding (note section 8): the natural embedding lattice
    does NOT recover the planted sparse combination, because the modular
    kernel {p_i * e_i} supplies weight-1 vectors of L2-norm p_i that LLL
    prefers over the planted coefficient. L2-shortness != L0-sparsity."""
    misses = 0
    for seed in range(6):
        moduli, M, a, t = plant(m=12, ell=1, seed=seed)
        if lll_recover(moduli, M, t) != a:
            misses += 1
    assert misses >= 5          # the attack essentially always fails
