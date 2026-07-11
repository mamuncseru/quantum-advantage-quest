import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from swap_loss_bp import ansatz_state, gradient_variance, loss, marginal


def test_ansatz_state_is_normalized():
    psi = ansatz_state(5, np.linspace(0, 3, 10))
    assert abs(np.linalg.norm(psi) - 1) < 1e-10


def test_marginal_is_a_state():
    psi = ansatz_state(6, np.linspace(0.1, 2, 12))
    rho = marginal(psi, 6, 3)
    assert abs(np.trace(rho) - 1) < 1e-10
    assert np.all(np.linalg.eigvalsh(rho) > -1e-12)


def test_loss_bounds():
    theta = np.linspace(0.2, 2.5, 8)
    val = loss(theta, 4, 2)
    assert 0.25 - 1e-9 <= val <= 1 + 1e-9    # purity in [1/2^k, 1]


def test_gradients_not_flat_at_small_k():
    v = gradient_variance(4, 1, samples=40, seed=1)
    assert v > 1e-4        # shallow local-ish loss: trainable signal exists
