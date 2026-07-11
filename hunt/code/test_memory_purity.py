import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from memory_purity import (ShadowSampler, gibbs_state, shadow_purity,
                           swap_test_samples)


def test_gibbs_state_is_a_state():
    rho = gibbs_state(4, seed=4)
    assert abs(np.trace(rho) - 1) < 1e-10
    assert np.all(np.linalg.eigvalsh(rho) > -1e-12)


def test_swap_cost_is_n_independent():
    # depends only on the purity value, never on n
    assert swap_test_samples(0.5, 0.05) == swap_test_samples(0.5, 0.05)
    assert swap_test_samples(0.9, 0.05) < swap_test_samples(0.5, 0.05)


def test_shadow_estimator_unbiased_small_n():
    rho = gibbs_state(3, seed=3)
    exact = float(np.real(np.trace(rho @ rho)))
    rng = np.random.default_rng(0)
    sampler = ShadowSampler(rho, rng)
    vals = [shadow_purity(*sampler.snapshots(400)) for _ in range(12)]
    err = abs(np.mean(vals) - exact)
    assert err < 4 * np.std(vals) / np.sqrt(len(vals)) + 1e-3


def test_shadow_variance_grows_with_n():
    costs = []
    for n in (2, 5):
        rho = gibbs_state(n, seed=n)
        rng = np.random.default_rng(1)
        sampler = ShadowSampler(rho, rng)
        vals = [shadow_purity(*sampler.snapshots(300)) for _ in range(10)]
        costs.append(np.var(vals))
    assert costs[1] > 4 * costs[0]      # strongly super-constant in n
