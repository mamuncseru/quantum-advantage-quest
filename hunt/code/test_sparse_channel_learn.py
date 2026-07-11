import random
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from sparse_channel_learn import (LambdaOracle, max_param_error,
                                  plant_sparse_channel, prefix_learn)


def test_planted_channel_is_distribution():
    p = plant_sparse_channel(16, 9, seed=1)
    assert abs(sum(p.values()) - 1) < 1e-12
    assert 0 in p and len(p) == 9


def test_low_weight_planting():
    p = plant_sparse_channel(24, 9, seed=2, low_weight=True)
    assert all(bin(a).count('1') <= 2 for a in p)


def test_noiseless_oracle_gives_exact_eigenvalues():
    p = {0: 0.7, 5: 0.3}
    oracle = LambdaOracle(p, shots=1, rng=np.random.default_rng(0))
    # b with <a,b> = 0 for both support points: lambda = 1 exactly
    assert abs(oracle.query(0) - 1.0) < 1e-12


def test_recovers_planted_sparse_channel():
    m, s = 16, 6
    p = plant_sparse_channel(m, s, seed=7)
    oracle = LambdaOracle(p, shots=4000, rng=np.random.default_rng(7))
    est = prefix_learn(oracle, m, s, eps=0.05, rand=random.Random(7))
    heavy = {a for a, w in p.items() if w >= 0.05}
    assert heavy <= set(est)
    assert max_param_error(p, est) < 0.05


def test_query_count_is_polynomial_in_m():
    counts = []
    for m in (8, 32):
        p = plant_sparse_channel(m, 5, seed=m)
        oracle = LambdaOracle(p, shots=2000, rng=np.random.default_rng(m))
        prefix_learn(oracle, m, 5, eps=0.05, rand=random.Random(m))
        counts.append(oracle.queries)
    # 4x the register size costs well under 16x the queries (linear-ish)
    assert counts[1] < 8 * counts[0]
