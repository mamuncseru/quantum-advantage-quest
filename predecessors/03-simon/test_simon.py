import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

import numpy as np

from simon import make_simon_function, rref_nullspace, simon


def test_recovers_hidden_string():
    rng = np.random.default_rng(3)
    for n, s_true in ((3, 0b101), (4, 0b1001), (5, 0b11111)):
        f = make_simon_function(s_true, n, rng)
        s, used = simon(f, n, seed=11)
        assert s == s_true
        assert used <= 20 * n


def test_nullspace_solver():
    # y's orthogonal to s = 1101 (n=4): e.g. 0110, 1010, 0001... check a set
    s = 0b1101
    rows = [0b0010, 0b1100, 0b1011]
    for y in rows:
        assert bin(y & s).count("1") % 2 == 0
    assert rref_nullspace(rows, 4) == s
