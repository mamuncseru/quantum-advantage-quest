import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from grover import grover, success_curve


def test_optimal_iterations_succeed():
    p, k = grover(8, marked=137)
    assert p > 0.99
    assert k == int(np.floor(np.pi / 4 * np.sqrt(256)))


def test_overshoot_hurts():
    p_opt, k = grover(6, marked=17)
    p_over, _ = grover(6, marked=17, iterations=2 * k)
    assert p_over < 0.5 < p_opt


def test_circuit_matches_rotation_picture():
    n, marked = 5, 9
    curve = success_curve(n, marked, 4)
    for k in range(5):
        p, _ = grover(n, marked, iterations=k)
        assert np.isclose(p, curve[k], atol=1e-10)
