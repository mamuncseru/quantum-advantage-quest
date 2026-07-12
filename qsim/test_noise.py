"""Tests for qsim.noise — the machine-noise trajectory model."""

import numpy as np
import pytest

from qsim import CNOT, H, amplitudes, apply, zero_state
from qsim.noise import (MachineNoise, noisy_apply, noisy_sample,
                        success_probability)


def bell_pair(noise=None, rng=None):
    psi = zero_state(2)
    if noise is None:
        psi = apply(psi, H, [0])
        return apply(psi, CNOT, [0, 1])
    psi = noisy_apply(psi, H, [0], noise, rng)
    return noisy_apply(psi, CNOT, [0, 1], noise, rng)


def test_zero_noise_is_exact():
    noise = MachineNoise(err_2q=0.0, err_1q=0.0, readout=0.0)
    rng = np.random.default_rng(0)
    assert np.allclose(amplitudes(bell_pair(noise, rng)),
                       amplitudes(bell_pair()))
    assert set(noisy_sample(bell_pair(), noise, shots=200, seed=1)) \
        <= {"00", "11"}


def test_fault_injection_rate():
    # On |00>, a noisy 2Q identity leaves the state unchanged unless a
    # Pauli with an X/Y component fires: 12 of the 15 non-identity Paulis.
    noise = MachineNoise(err_2q=0.3, err_1q=0.0, readout=0.0)
    rng = np.random.default_rng(7)
    eye4 = np.eye(4, dtype=complex)
    trials, flipped = 4000, 0
    base = amplitudes(zero_state(2))
    for _ in range(trials):
        psi = noisy_apply(zero_state(2), eye4, [0, 1], noise, rng)
        if abs(abs(np.vdot(base, amplitudes(psi))) - 1) > 1e-9:
            flipped += 1
    expect = 0.3 * 12 / 15
    assert abs(flipped / trials - expect) < 0.02


def test_readout_flip_rate():
    noise = MachineNoise(err_2q=0.0, err_1q=0.0, readout=0.25)
    bits = noisy_sample(zero_state(4), noise, shots=2000, seed=3)
    ones = sum(b.count("1") for b in bits) / (2000 * 4)
    assert abs(ones - 0.25) < 0.02


def test_monte_carlo_matches_analytic():
    # GHZ-3: two 2Q gates, one 1Q gate, 3 readouts. The zero-fault
    # frequency of ideal outcomes should approach the analytic estimate
    # (faults can accidentally still yield 000/111, so MC >= analytic).
    noise = MachineNoise(err_2q=0.05, err_1q=0.005, readout=0.01)
    rng = np.random.default_rng(11)
    shots, good = 3000, 0
    for _ in range(shots):
        psi = zero_state(3)
        psi = noisy_apply(psi, H, [0], noise, rng)
        psi = noisy_apply(psi, CNOT, [0, 1], noise, rng)
        psi = noisy_apply(psi, CNOT, [1, 2], noise, rng)
        good += noisy_sample(psi, noise, shots=1,
                             seed=rng.integers(2**31))[0] in ("000", "111")
    analytic = success_probability(3, g2=2, g1=1, noise=noise)
    mc = good / shots
    assert analytic - 0.02 <= mc <= analytic + 0.12


def test_from_catalog_reads_helios():
    noise = MachineNoise.from_catalog("quantinuum-helios")
    assert noise.err_2q == pytest.approx(7.9e-4)
    assert noise.err_1q == pytest.approx(2.5e-5)
    assert noise.readout == pytest.approx(4.8e-4)


def test_from_catalog_refuses_unsourced():
    with pytest.raises(ValueError):
        MachineNoise.from_catalog("ibm-nighthawk")  # err_2q is null
    with pytest.raises(KeyError):
        MachineNoise.from_catalog("no-such-machine")
