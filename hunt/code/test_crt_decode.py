import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from crt_sparse_decode import (crt_sparse, crt_weight_pattern, decode,
                               planted_instance)


def test_pattern_roundtrip():
    moduli = [3, 5, 7, 11, 13]
    t = crt_sparse(moduli, [1, 3], [2, 10])
    assert crt_weight_pattern(t, moduli) == {1: 2, 3: 10}


def test_planted_recovery_constant_ell():
    # UNIQUE decoding below d_min(2*ell)/2 = M/(2 P_max(2*ell)) — the exact
    # radius from the minimum-distance theorem (note section 7).
    for seed in range(6):
        moduli, t, t_prime, delta = planted_instance(m=18, ell=2, seed=seed)
        hits = decode(t_prime, moduli, ell=2, delta=delta)
        assert t in hits
        assert len(hits) == 1


def test_zero_noise_is_trivial_readout():
    moduli, t, _, _ = planted_instance(m=18, ell=3, seed=1, noise_frac=0.0)
    # noiseless: support readable by plain modular reduction, no enumeration
    assert len(crt_weight_pattern(t, moduli)) <= 3
