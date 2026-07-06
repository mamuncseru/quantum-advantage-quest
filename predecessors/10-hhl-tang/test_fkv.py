import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from fkv import make_low_rank, reconstruction_ratio


def test_few_samples_match_optimal_projection():
    A = make_low_rank(1000, 1000, k=5)
    assert reconstruction_ratio(A, k=5, r=200) < 1.05


def test_more_samples_help():
    A = make_low_rank(800, 800, k=4, seed=2)
    r_small = reconstruction_ratio(A, k=4, r=20, seed=1)
    r_large = reconstruction_ratio(A, k=4, r=300, seed=1)
    assert r_large <= r_small
