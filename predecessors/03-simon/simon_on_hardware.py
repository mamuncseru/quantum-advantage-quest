"""Simon on real error rates — notes.md section 5, the fragility ladder.

Three autopsies, three demands on the output, three ways to break:

    Deutsch-Jozsa   1 bit, read as a statistic   -> bad shots wash out
    Bernstein-Vazirani  n independent bits       -> majority-vote each bit
    Simon           n-1 equations of n bits,
                    all correct AND independent  -> one bad equation and
                                                    the nullspace is wrong

Simon is the first algorithm here whose classical post-processing can
turn a small measurement error into a completely wrong answer: Gaussian
elimination has no notion of "mostly right". This file measures how
often that happens on published error rates, and shows the repair that
real experiments use -- oversample, then keep the candidate that the
majority of samples agree with, and verify it against the oracle.

The circuit uses the LINEAR oracle f(x) = x XOR (x_p . s), which is pure
CNOT and is what any hardware demonstration would run. See
simon_classical_attack.py for why that same choice destroys the
separation being demonstrated.

Run:  .venv/bin/python predecessors/03-simon/simon_on_hardware.py
"""

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))

from qsim import CNOT, H, apply, sample, zero_state  # noqa: E402
from qsim.noise import MachineNoise, noisy_apply, noisy_sample  # noqa: E402

MACHINES = ["quantinuum-helios", "ibm-heron-r2", "rigetti-ankaa-3"]


def dot(a, b):
    return bin(a & b).count("1") & 1


def oracle_cnots(s_bits, n):
    """The linear oracle as CNOT pairs (control, target) on 2n qubits.

    Input register is qubits 0..n-1, output register n..2n-1.
    f(x) = x XOR (x_p . s): copy x across, then fan x_p into every
    position where s has a 1.
    """
    pairs = [(i, n + i) for i in range(n)]          # copy
    p = next(i for i in range(n) if s_bits[i])      # any set bit of s
    pairs += [(p, n + j) for j in range(n) if s_bits[j]]
    return pairs


def _one_run(n, pairs, noise, rng):
    psi = zero_state(2 * n)

    def gate(psi, U, qubits):
        if noise is None:
            return apply(psi, U, qubits)
        return noisy_apply(psi, U, qubits, noise, rng)

    for q in range(n):
        psi = gate(psi, H, [q])
    for (c, t) in pairs:
        psi = gate(psi, CNOT, [c, t])
    for q in range(n):
        psi = gate(psi, H, [q])
    return psi


def collect_samples(n, s_bits, noise=None, shots=200, seed=0):
    """`shots` measured y values from the input register."""
    rng = np.random.default_rng(seed)
    pairs = oracle_cnots(s_bits, n)
    inputs = list(range(n))
    if noise is None:
        psi = _one_run(n, pairs, None, rng)
        bits = sample(psi, shots=shots, qubits=inputs,
                      seed=int(rng.integers(2 ** 31)))
    else:
        bits = []
        for _ in range(shots):
            psi = _one_run(n, pairs, noise, rng)
            bits.append(noisy_sample(psi, noise, shots=1, qubits=inputs,
                                     seed=int(rng.integers(2 ** 31)))[0])
    return [int(b, 2) for b in bits]


def s_int(s_bits, n):
    """The secret as an integer in the same bit order the samples use
    (qubit 0 is the most significant bit)."""
    v = 0
    for i in range(n):
        v |= s_bits[i] << (n - 1 - i)
    return v


def clean_fraction(ys, s):
    return sum(1 for y in ys if dot(y, s) == 0) / len(ys)


def naive_solve(ys, n):
    """Take the first n-1 independent samples and solve — what the
    textbook algorithm does, with no tolerance for a bad equation."""
    basis, rows = [], []
    for y in ys:
        z = y
        for b in basis:
            z = min(z, z ^ b)
        if z:
            basis.append(z)
            rows.append(y)
        if len(rows) == n - 1:
            break
    if len(rows) < n - 1:
        return None
    for cand in range(1, 2 ** n):                  # tiny n: just search
        if all(dot(y, cand) == 0 for y in rows):
            return cand
    return None


def majority_solve(ys, n):
    """The repair: keep the candidate that the most samples agree with.

    Brute force over candidates is fine at the sizes we can simulate; at
    scale you would instead solve many random subsets and vote, or use
    the oracle itself to verify a shortlist.
    """
    best, best_score = None, -1
    for cand in range(1, 2 ** n):
        score = sum(1 for y in ys if dot(y, cand) == 0)
        if score > best_score:
            best, best_score = cand, score
    return best


if __name__ == "__main__":
    n = 5
    s_bits = [1, 0, 1, 1, 0]
    s = s_int(s_bits, n)
    pairs = oracle_cnots(s_bits, n)
    print(f"Simon, n = {n} (+{n} output qubits = {2 * n} total), "
          f"secret = {s:0{n}b}")
    print(f"circuit: {2 * n} Hadamards, {len(pairs)} CNOTs, "
          f"{n} measured qubits")
    print(f"needs {n - 1} equations, all correct and independent\n")
    print(f"{'machine':<24}{'clean y':>9}{'all eqs clean':>15}"
          f"{'naive solve':>13}{'majority (60)':>15}")

    rows = [("ideal (no noise)", None)]
    rows += [(m, MachineNoise.from_catalog(m)) for m in MACHINES]
    for label, noise in rows:
        ys = collect_samples(n, s_bits, noise, shots=240, seed=4)
        cf = clean_fraction(ys, s)
        name = noise.label if noise else label
        trials, naive_ok = 24, 0
        for t in range(trials):
            block = collect_samples(n, s_bits, noise, shots=12,
                                    seed=500 + 7 * t)
            naive_ok += (naive_solve(block, n) == s)
        maj = majority_solve(
            collect_samples(n, s_bits, noise, shots=60, seed=77), n)
        print(f"{name:<24}{cf:>9.3f}{cf ** (n - 1):>15.3f}"
              f"{naive_ok / trials:>13.2f}"
              f"{('OK' if maj == s else 'WRONG'):>15}")

    print("\n'clean y' is the fraction of single runs whose equation is "
          "actually true.\nRaise it to the power n-1 and you have the "
          "chance that a textbook solve\nsucceeds — which is why Simon "
          "degrades faster than Bernstein-Vazirani,\nand why the majority "
          "repair (last column) is not optional on real hardware.")
