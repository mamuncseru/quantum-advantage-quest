"""Bernstein-Vazirani as a real machine would run it — notes.md section 6.

!!! SPOILER for the section-9 exercise: this file builds the BV circuit
out of H and CNOT gates. If you want to implement bernstein_vazirani()
on the simulator unaided, do that first. (The same circuit is already
shown publicly in autopsy 01 section 7, so nothing here is secret — but
you may prefer to derive it yourself.)

The circuit is GATE-FOR-GATE the Deutsch-Jozsa circuit of
predecessors/01-deutsch-jozsa/dj_on_hardware.py. Nothing about the
hardware changes. What changes is how much you demand of the output:

    Deutsch-Jozsa   asks one yes/no question  ->  1 bit out
    Bernstein-Vazirani reads the whole string ->  n bits out

and that difference alone decides how the two algorithms die under noise.
Single-shot BV needs all n measured bits correct at once, so its success
falls like (1-eps)^n. But readout errors hit each qubit INDEPENDENTLY,
so majority-voting each bit across shots repairs them one at a time --
which is what a real experiment does, and why n bits of output is not
n times more fragile in practice.

Run:  .venv/bin/python predecessors/02-bernstein-vazirani/bv_on_hardware.py
"""

import sys
from collections import Counter
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from qsim import CNOT, H, X, apply, sample, zero_state  # noqa: E402
from qsim.noise import MachineNoise, noisy_apply, noisy_sample  # noqa: E402

MACHINES = ["quantinuum-helios", "ibm-heron-r2", "rigetti-ankaa-3"]


def _one_run(n, s_mask, noise, rng):
    """One trajectory of the BV circuit on n+1 qubits."""
    anc = n
    psi = zero_state(n + 1)

    def gate(psi, U, qubits):
        if noise is None:
            return apply(psi, U, qubits)
        return noisy_apply(psi, U, qubits, noise, rng)

    psi = gate(psi, X, [anc])
    psi = gate(psi, H, [anc])                 # ancilla -> |->
    for q in range(n):
        psi = gate(psi, H, [q])
    for q in range(n):                        # the oracle: CNOT per set bit
        if (s_mask >> q) & 1:
            psi = gate(psi, CNOT, [q, anc])
    for q in range(n):
        psi = gate(psi, H, [q])
    return psi


def measure_shots(n, s_mask, noise=None, shots=200, seed=0):
    """Return `shots` measured bitstrings of the n input qubits.

    Noisy runs use one fresh trajectory per shot: a real machine draws a
    new error pattern every repetition.
    """
    rng = np.random.default_rng(seed)
    inputs = list(range(n))
    if noise is None:
        psi = _one_run(n, s_mask, None, rng)
        return sample(psi, shots=shots, qubits=inputs,
                      seed=int(rng.integers(2 ** 31)))
    out = []
    for _ in range(shots):
        psi = _one_run(n, s_mask, noise, rng)
        out.append(noisy_sample(psi, noise, shots=1, qubits=inputs,
                                seed=int(rng.integers(2 ** 31)))[0])
    return out


def target_string(n, s_mask):
    """The bitstring the circuit should produce (qsim is big-endian:
    qubit 0 is the leading character)."""
    return "".join(str((s_mask >> q) & 1) for q in range(n))


def exact_rate(shots_list, target):
    """Fraction of single shots that got the WHOLE string right."""
    return sum(1 for b in shots_list if b == target) / len(shots_list)


def majority_vote(shots_list):
    """Per-bit majority across shots — the standard experimental repair."""
    n = len(shots_list[0])
    return "".join(
        Counter(b[i] for b in shots_list).most_common(1)[0][0]
        for i in range(n))


def per_bit_rate(shots_list, target):
    """Fraction of individual bits (not strings) read correctly."""
    tot = ok = 0
    for b in shots_list:
        for i, ch in enumerate(b):
            ok += (ch == target[i])
            tot += 1
    return ok / tot


if __name__ == "__main__":
    n, shots = 8, 400
    s_mask = 0b10110101 & ((1 << n) - 1)
    target = target_string(n, s_mask)
    print(f"Bernstein-Vazirani, n = {n} (+1 ancilla), secret = {target}")
    print(f"oracle = {bin(s_mask).count('1')} CNOTs; "
          f"{2 * n + 2} single-qubit gates; {shots} shots each\n")
    print(f"{'machine':<24}{'exact string':>14}{'per-bit':>10}"
          f"{'majority vote':>15}")

    rows = [("ideal (no noise)", None)]
    rows += [(m, MachineNoise.from_catalog(m)) for m in MACHINES]
    for label, noise in rows:
        sh = measure_shots(n, s_mask, noise, shots=shots, seed=7)
        name = noise.label if noise else label
        mv = majority_vote(sh)
        print(f"{name:<24}{exact_rate(sh, target):>14.3f}"
              f"{per_bit_rate(sh, target):>10.3f}"
              f"{('OK  ' + mv) if mv == target else ('WRONG ' + mv):>15}")

    print("\nThe exact-string column is what single-shot BV delivers; it "
          "decays like\n(1-eps)^n because every one of the n bits has to "
          "survive at once. The\nper-bit column barely moves — and "
          "majority-voting those independent\nbits recovers the secret "
          "exactly. n bits of output cost shots, not fidelity.")
