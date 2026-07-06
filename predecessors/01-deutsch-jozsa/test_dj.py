import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from deutsch_jozsa import deutsch_jozsa, dj_p0
from qsim import phase_oracle


def test_constant_functions():
    n = 6
    for c in (0, 1):
        assert deutsch_jozsa(phase_oracle(lambda x: c, n), n) == "constant"


def test_balanced_functions():
    n = 6
    rng = np.random.default_rng(5)
    balanced = [
        lambda x: bin(x).count("1") & 1,          # parity
        lambda x: (x >> (n - 1)) & 1,             # top bit
    ]
    for _ in range(3):                            # random s . x, s != 0
        s = int(rng.integers(1, 2 ** n))
        balanced.append(lambda x, s=s: bin(x & s).count("1") & 1)
    for f in balanced:
        assert deutsch_jozsa(phase_oracle(f, n), n) == "balanced"


def test_p0_is_exact():
    n = 5
    assert np.isclose(dj_p0(phase_oracle(lambda x: 1, n), n), 1.0)
    parity = lambda x: bin(x).count("1") & 1
    assert np.isclose(dj_p0(phase_oracle(parity, n), n), 0.0)
