"""What Grover actually costs — notes.md sections 6-7.

Shor's cost is dominated by circuit *size*. Grover's is dominated by circuit
*depth*, and that difference decides everything: the (pi/4)sqrt(N)
iterations are strictly sequential. Iteration t+1 cannot begin until
iteration t has finished, no matter how many qubits you own.

So the headline number on this page needs no assumption about how expensive
the oracle is:

    a 128-bit key search needs 2^64 sequential iterations.

At the logical clock rate this repository already established in
machines/gap.md — a distance-25 logical operation takes ~25 microseconds on
superconducting hardware, a ~40 kHz logical clock — that is
14 million years even if each entire iteration were a single logical
operation, which it is not.

MODEL (stated so it can be argued with):
    iterations        = (pi/4) * 2^(k/2)          for a k-bit key
    logical ops/iter  = 2 * (oracle depth) + diffusion, in logical operations
    logical op time   = 25 us   (d=25 surface code, machines/gap.md)
    classical op time = 0.3 ns  (one core, ~3 GHz)
Published AES oracle estimates are quoted where they change the conclusion,
and they do not: the sequential depth alone settles it.

Run:  .venv/bin/python predecessors/06-grover/grover_resources.py
"""

from __future__ import annotations

import sys
from math import ceil, log2, pi, sqrt
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "machines"))
sys.path.insert(0, str(Path(__file__).parent))

from feasibility import Profile, assess  # noqa: E402

# --- the two clocks, both sourced -------------------------------------------
LOGICAL_OP_S = 25e-6      # d=25 surface code, ~25 syndrome rounds (gap.md)
PHYSICAL_2Q_S = 6.8e-8    # IBM Heron r2, machines/data.yml (no error correction)
CLASSICAL_OP_S = 0.3e-9   # one classical core at ~3 GHz
SECONDS_PER_YEAR = 365.25 * 24 * 3600


def iterations(key_bits, solutions=1):
    """(pi/4) sqrt(N/M) — and every one of them is sequential."""
    return (pi / 4) * sqrt(2 ** key_bits / solutions)


def sequential_time(key_bits, ops_per_iteration=1, op_s=LOGICAL_OP_S,
                    solutions=1):
    """Wall-clock seconds. No amount of hardware reduces this — see
    `parallel_time` for what buying more machines actually buys."""
    return iterations(key_bits, solutions) * ops_per_iteration * op_s


def parallel_time(key_bits, machines, ops_per_iteration=1, op_s=LOGICAL_OP_S):
    """k machines split the space and each searches its slice: sqrt(k) only.

    This is the asymmetry that decides the whole question. Classical brute
    force divides by k; Grover divides by sqrt(k).
    """
    return sequential_time(key_bits, ops_per_iteration, op_s) / sqrt(machines)


def classical_time(key_bits, cores=1, op_s=CLASSICAL_OP_S):
    """Brute force: 2^(k-1) expected trials, perfectly parallel."""
    return 2 ** (key_bits - 1) * op_s / cores


def years(seconds):
    return seconds / SECONDS_PER_YEAR


def crossover_N(quantum_op_s=LOGICAL_OP_S, classical_op_s=CLASSICAL_OP_S):
    """Smallest N where Grover's sqrt(N) beats brute force's N/2.

    Grover: sqrt(N) * quantum_op_s. Classical: (N/2) * classical_op_s.
    They cross at sqrt(N) = 2 * quantum_op_s / classical_op_s, so

        N_cross = (2 * ratio)^2 .

    Below that the constant factor wins and the asymptotically slower
    algorithm is the faster program — which is the whole content of
    "quadratic speedups need enormous instances before they mean anything".
    """
    ratio = quantum_op_s / classical_op_s
    return (2 * ratio) ** 2


def crossover_with_parallel_classical(cores, quantum_op_s=LOGICAL_OP_S,
                                      classical_op_s=CLASSICAL_OP_S):
    """The same crossover once the classical attacker owns a cluster.

    k cores divide the classical time per trial by k, which *raises* the
    crossover: every core the defender-side attacker buys pushes the size at
    which quantum starts winning further out of reach. (Grover gains only
    sqrt(k) from the same purchase — `parallel_time`.)
    """
    return crossover_N(quantum_op_s, classical_op_s / cores)


# ------------------------------------------- a toy Grover on real hardware --

def circuit_cost(n, iters=None):
    """Gate counts for our own n-qubit Grover circuit, compiled honestly.

    An n-controlled Z with ancillas costs about 2(n-2) Toffoli; the oracle
    is one and the diffusion operator contains another, so one iteration is
    ~4(n-2) Toffoli, and a Toffoli is 6 CNOT.
    """
    iters = iters or int(round(pi / 4 * sqrt(2 ** n) - 0.5))
    toffoli_per_iter = 4 * max(n - 2, 1)
    toffoli = toffoli_per_iter * iters
    return dict(n=n, iterations=iters, toffoli=toffoli, cnot=6 * toffoli,
                qubits=n + max(n - 2, 1),          # + ancillas
                depth_sequential=iters)


def feasibility(n):
    """Would any machine in the catalog survive even a toy Grover?"""
    c = circuit_cost(n)
    prof = Profile(qubits=c["qubits"], g2=c["cnot"], g1=2 * n * c["iterations"],
                   pattern="nonlocal")
    return c, prof, assess(prof)


# --------------------------------------------------------------- targets ---

TARGETS = [
    # label, key bits, published oracle depth in logical ops per iteration
    ("AES-128 key search", 128, 2 ** 13),
    ("AES-192 key search", 192, 2 ** 14),
    ("AES-256 key search", 256, 2 ** 14),
    ("SHA-256 preimage", 256, 2 ** 15),
]


def _demo():
    print("1 · THE NUMBER THAT NEEDS NO ORACLE MODEL\n")
    print("   Grover's iterations are strictly sequential, so even if an")
    print("   entire iteration were ONE logical operation:\n")
    print(f"   {'target':22} {'iterations':>12} {'wall clock':>18}")
    for label, bits, _ in TARGETS:
        t = sequential_time(bits, ops_per_iteration=1)
        print(f"   {label:22} {iterations(bits):>12.2e} "
              f"{years(t):>15.2e} yr")
    print(f"\n   (logical op = {LOGICAL_OP_S * 1e6:.0f} us, the d=25 surface-code")
    print("    clock this repository already derived in machines/gap.md)")

    print("\n2 · WITH A REALISTIC ORACLE\n")
    print(f"   {'target':22} {'ops/iter':>10} {'wall clock':>20}")
    for label, bits, depth in TARGETS:
        t = sequential_time(bits, ops_per_iteration=depth)
        print(f"   {label:22} {depth:>10,} {years(t):>17.2e} yr")
    print("\n   For scale: the universe is 1.4e10 years old.")

    print("\n3 · BUYING MORE QUANTUM COMPUTERS DOES NOT HELP MUCH\n")
    bits, depth = 128, 2 ** 13
    print(f"   AES-128, {depth:,} logical ops per iteration:\n")
    print(f"   {'machines':>14} {'quantum (sqrt k)':>22} "
          f"{'classical cores (k)':>22}")
    for k in (1, 10 ** 3, 10 ** 6, 10 ** 9):
        q = years(parallel_time(bits, k, depth))
        c = years(classical_time(bits, cores=k))
        print(f"   {k:>14,} {q:>19.2e} yr {c:>19.2e} yr")
    print("\n   both are hopeless for AES-128 — which is the point: the key")
    print("   size was chosen so that neither works. What matters is that")
    print("   the quantum column falls as sqrt(k) and the classical column")
    print("   falls as k, so more hardware always favours the classical side.")

    print("\n4 · WHERE THE QUADRATIC ACTUALLY STARTS PAYING\n")
    n_cross = crossover_N()
    print(f"   {'classical hardware':>22}   {'Grover wins only above':>24}")
    print(f"   {'one core':>22}   N > {n_cross:.2e}  "
          f"(2^{log2(n_cross):.0f})")
    for cores in (10 ** 3, 10 ** 6, 10 ** 9):
        nc = crossover_with_parallel_classical(cores)
        t_win = years(sqrt(nc) * LOGICAL_OP_S)
        print(f"   {cores:>13,} cores   N > {nc:.2e}  "
              f"(2^{log2(nc):.0f})   and searching it takes "
              f"{t_win:.1e} yr")
    print("\n   Those rows are the most generous possible reading: one")
    print("   operation per trial on BOTH sides. A real predicate costs")
    print("   gates on both sides, and the quantum copy must be reversible")
    print("   and error-corrected. Charge it honestly:\n")
    print(f"   {'oracle: quantum / classical ops':>34}   "
          f"{'Grover wins only above':>22}")
    for gq, gc in ((2 ** 13, 2 ** 10), (2 ** 15, 2 ** 12)):
        nc = crossover_N(LOGICAL_OP_S * gq, CLASSICAL_OP_S * gc)
        print(f"   {gq:>15,} / {gc:<16,}   N > {nc:.2e}  "
              f"(2^{log2(nc):.0f})")
    print("\n   Below those sizes the asymptotically slower algorithm is the")
    print("   faster program. A quadratic speedup buys nothing until the")
    print("   search space is astronomically large — and if the space is")
    print("   that large, sqrt of it is still astronomically large.")

    print("\n5 · AND OUR OWN TOY CIRCUIT, ON REAL MACHINES\n")
    for n in (8, 12):
        c, prof, rows = feasibility(n)
        print(f"   n = {n} (N = {2**n}): {c['iterations']} iterations, "
              f"{c['cnot']:,} CNOT on {c['qubits']} qubits")
        for r in rows[:3]:
            print(f"      {r['machine']:<30}{r['verdict']:>9}"
                  f"{r['fidelity']:>12.2e}")
    print("\n   Grover is a magnificent subroutine and a terrible flagship.")


if __name__ == "__main__":
    _demo()
