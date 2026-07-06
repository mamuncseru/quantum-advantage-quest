import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from trotter import measured_slope


def test_first_order_slope():
    slope, errs = measured_slope(order=1, n_qubits=4)
    assert -1.3 < slope < -0.8
    assert errs[-1] < errs[0]


def test_second_order_slope():
    slope, errs = measured_slope(order=2, n_qubits=4)
    assert -2.3 < slope < -1.7
