import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from bernstein_vazirani import bernstein_vazirani
from qsim import phase_oracle


def make_oracle(s):
    n = len(s)
    si = int(s, 2)
    return phase_oracle(lambda x: bin(x & si).count("1") & 1, n), n


def test_recovers_hidden_string():
    for s in ("1", "101", "0000000001", "11011011011"):
        oracle, n = make_oracle(s)
        assert bernstein_vazirani(oracle, n) == s


def test_all_zero_secret():
    oracle, n = make_oracle("0000")
    assert bernstein_vazirani(oracle, n) == "0000"
