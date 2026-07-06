import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from glued_trees import classical_exit_prob, quantum_exit_prob


def test_quantum_crosses_in_linear_time():
    pq, tstar = quantum_exit_prob(16)
    assert pq > 0.4                     # calibrated: 0.445 at d=16
    assert tstar < 16                   # ballistic: crossing time ~ 0.8 d


def test_classical_is_exponentially_suppressed():
    # classical gets a d^3 step budget and still collapses exponentially in d
    p12 = classical_exit_prob(12, 12 ** 3)
    p16 = classical_exit_prob(16, 16 ** 3)
    p20 = classical_exit_prob(20, 20 ** 3)
    assert p16 < p12 / 3 and p20 < p16 / 3
    assert p20 < 1e-3


def test_separation_grows():
    ratios = []
    for d in (12, 16, 20):
        pq, _ = quantum_exit_prob(d)
        ratios.append(pq / classical_exit_prob(d, d ** 3))
    assert ratios[0] < ratios[1] < ratios[2]
    assert ratios[2] > 500
