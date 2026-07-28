"""Deutsch-Jozsa as a real machine would run it — section 7 of notes.md.

The textbook version hands you a dense 2^n "oracle matrix". No machine has
one. This file compiles DJ into the gates a device actually executes and
runs it under the published error rates of real machines
(machines/data.yml, via qsim.noise).

The circuit, on n+1 qubits (n inputs + 1 ancilla):

    ancilla:  X ─ H ────────●────●─────────────────── (discarded)
    input i:      H ────────┼────┼──── H ── measure
                            │    │
    the oracle IS those CNOTs: for f(x) = x·s (mod 2), one CNOT from every
    input qubit in the support of s onto the ancilla. With the ancilla in
    |-> each CNOT kicks a (-1)^{x_i} back onto the input — phase kickback,
    made of hardware.

So the honest gate budget of DJ is:  2n + 2 single-qubit gates, |s|
two-qubit gates, n measurements. Balanced parity (s = all ones) is the
worst case; a constant function needs no CNOT at all.

Run:  .venv/bin/python predecessors/01-deutsch-jozsa/dj_on_hardware.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from qsim import CNOT, H, X, apply, sample, zero_state  # noqa: E402
from qsim.noise import MachineNoise, noisy_apply, noisy_sample  # noqa: E402

MACHINES = ["quantinuum-helios", "quantinuum-h2", "ibm-heron-r2",
            "google-willow", "rigetti-ankaa-3"]


def _one_run(n, s_mask, noise, rng):
    """Build the circuit once. With noise this is ONE trajectory: the
    faults drawn here are a single error pattern, so a shot may only be
    drawn from it once (see run_dj)."""
    anc = n                                   # ancilla is the last qubit
    psi = zero_state(n + 1)

    def gate(psi, U, qubits):
        if noise is None:
            return apply(psi, U, qubits)
        return noisy_apply(psi, U, qubits, noise, rng)

    psi = gate(psi, X, [anc])                 # |0> -> |1>
    psi = gate(psi, H, [anc])                 # |1> -> |->
    for q in range(n):
        psi = gate(psi, H, [q])
    for q in range(n):                        # the oracle, in hardware
        if (s_mask >> q) & 1:
            psi = gate(psi, CNOT, [q, anc])
    for q in range(n):
        psi = gate(psi, H, [q])
    return psi


def run_dj(n, s_mask, noise=None, shots=2000, seed=0):
    """Return P(all n input qubits read 0) — the DJ decision statistic.

    s_mask = 0 is a constant f (ideal answer 1.0); s_mask with k bits set
    is a balanced f (ideal answer 0.0) costing k CNOTs.

    Noisy runs draw ONE shot per trajectory: a fresh error pattern for
    every shot, which is what a real machine does. (Drawing many shots
    from a single trajectory would report the statistics of one lucky or
    unlucky error pattern.)
    """
    rng = np.random.default_rng(seed)
    inputs, target = list(range(n)), "0" * n
    if noise is None:
        psi = _one_run(n, s_mask, None, rng)
        bits = sample(psi, shots=shots, qubits=inputs,
                      seed=int(rng.integers(2 ** 31)))
        return sum(1 for b in bits if b == target) / shots
    zeros = 0
    for _ in range(shots):
        psi = _one_run(n, s_mask, noise, rng)
        bit = noisy_sample(psi, noise, shots=1, qubits=inputs,
                           seed=int(rng.integers(2 ** 31)))[0]
        zeros += (bit == target)
    return zeros / shots


def gate_counts(n, s_mask):
    return dict(one_qubit=2 * n + 2, two_qubit=bin(s_mask).count("1"),
                qubits=n + 1)


def survey(n=10, shots=2000, seed=1):
    """P(0...0) for a constant and a balanced f, ideal and per machine."""
    const, bal = 0, (1 << n) - 1              # balanced = full parity
    rows = [dict(machine="ideal (no noise)", err_2q=None,
                 const=run_dj(n, const, None, shots, seed),
                 bal=run_dj(n, bal, None, shots, seed + 1))]
    for mid in MACHINES:
        noise = MachineNoise.from_catalog(mid)
        rows.append(dict(
            machine=noise.label, err_2q=noise.err_2q, readout=noise.readout,
            const=run_dj(n, const, noise, shots, seed + 2),
            bal=run_dj(n, bal, noise, shots, seed + 3)))
    return rows


if __name__ == "__main__":
    n, shots = 10, 4000
    gc = gate_counts(n, (1 << n) - 1)
    print(f"Deutsch-Jozsa, n = {n} inputs (+1 ancilla = {gc['qubits']} "
          f"qubits), balanced case")
    print(f"gate budget: {gc['one_qubit']} single-qubit, "
          f"{gc['two_qubit']} two-qubit, {n} measurements\n")
    print(f"{'machine':<26}{'P(0…0) constant':>17}{'P(0…0) balanced':>17}"
          f"{'margin':>9}")
    for r in survey(n, shots):
        margin = r["const"] - r["bal"]
        print(f"{r['machine']:<26}{r['const']:>17.3f}{r['bal']:>17.3f}"
              f"{margin:>9.3f}")
    print("\nDecision rule: P(0…0) > 0.5 ⇒ constant. The margin is what "
          "noise eats.\nReadout error dominates here — the circuit is "
          "shallow, but every one of\nthe 10 measured qubits can lie.")
