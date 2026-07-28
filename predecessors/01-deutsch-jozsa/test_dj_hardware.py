"""Tests for the compiled-to-hardware DJ circuit (notes.md section 7),
and for the physics the page's interactive figures claim.
"""

import math
import sys
from pathlib import Path

import numpy as np
import pytest

sys.path.insert(0, str(Path(__file__).parent))

from deutsch_jozsa import dj_p0                       # noqa: E402
from dj_on_hardware import gate_counts, run_dj        # noqa: E402
from qsim import phase_oracle                         # noqa: E402
from qsim.noise import MachineNoise                   # noqa: E402


def test_noiseless_circuit_reproduces_the_ideal_answer():
    # the CNOT-compiled circuit must agree with the dense-oracle version
    n = 6
    assert run_dj(n, 0, None, shots=200, seed=1) == 1.0            # constant
    assert run_dj(n, (1 << n) - 1, None, shots=200, seed=2) == 0.0  # balanced


def test_gate_budget_matches_the_table_in_notes():
    gc = gate_counts(10, (1 << 10) - 1)
    assert gc == dict(one_qubit=22, two_qubit=10, qubits=11)
    assert gate_counts(10, 0)["two_qubit"] == 0     # constant f: no CNOTs


def test_noise_lowers_the_constant_branch_but_keeps_the_decision():
    n = 8
    noise = MachineNoise.from_catalog("ibm-heron-r2")
    p_const = run_dj(n, 0, noise, shots=300, seed=3)
    p_bal = run_dj(n, (1 << n) - 1, noise, shots=300, seed=4)
    assert 0.8 < p_const < 1.0        # degraded, but still decisive
    assert p_bal < 0.05
    assert p_const - p_bal > 0.5      # the decision rule still fires


def test_better_readout_gives_a_better_margin():
    n = 8
    helios = MachineNoise.from_catalog("quantinuum-helios")
    heron = MachineNoise.from_catalog("ibm-heron-r2")
    assert helios.readout < heron.readout          # the driver, per notes §7
    assert (run_dj(n, 0, helios, shots=300, seed=5)
            > run_dj(n, 0, heron, shots=300, seed=5))


# --- the interactive figures on the page compute their own amplitudes;
# --- this pins that math to the simulator (see notes.md section 4).

def _walsh(a):
    """Exact port of walsh() in docs/javascripts/qq-anim.js."""
    N, ln = len(a), 1
    while ln < N:
        for i in range(0, N, ln << 1):
            for j in range(i, i + ln):
                u, v = a[j], a[j + ln]
                a[j] = (u + v) / math.sqrt(2)
                a[j + ln] = (u - v) / math.sqrt(2)
        ln <<= 1
    return a


@pytest.mark.parametrize("f,label", [
    (lambda x: 0, "constant 0"),
    (lambda x: 1, "constant 1"),
    (lambda x: bin(x).count("1") & 1, "parity"),
    (lambda x: (x >> 5) & 1, "top bit"),
    (lambda x: ((x >> 5) & (x >> 4)) & 1, "AND (off-promise)"),
])
def test_widget_math_matches_the_simulator(f, label):
    n, N = 6, 64
    a = [1 / math.sqrt(N)] * N
    for i in range(N):
        if f(i) & 1:
            a[i] = -a[i]
    widget_p0 = _walsh(a)[0] ** 2
    assert np.isclose(widget_p0, dj_p0(phase_oracle(f, n), n), atol=1e-12)
