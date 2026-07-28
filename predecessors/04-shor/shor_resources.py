"""What Shor actually costs — notes.md section 7.

The circuit in shor.py is honest about structure and dishonest about
cost: mod_mult_unitary() builds a dense 2^m x 2^m permutation matrix,
which is fine for simulating and impossible on hardware. A real machine
has to do the modular arithmetic REVERSIBLY, out of adders, and that is
where every qubit-second of Shor's algorithm goes.

This file prices the real thing:

  1. the circuit structure our simulator runs (exact, counted);
  2. a stated schoolbook model for the reversible arithmetic;
  3. the resulting two-qubit gate count fed through the machine catalog
     (machines/feasibility.py, machines/data.yml) -- i.e. would any
     machine that exists survive the circuit;
  4. the same model extrapolated to RSA-2048, next to the best published
     optimisation, so the gap between "schoolbook" and "state of the art"
     is visible rather than hidden.

ARITHMETIC MODEL (schoolbook, stated so it can be argued with):
    modular exponentiation = 2t controlled modular multiplications
    modular multiplication = n modular additions
    modular addition       ~ 4n Toffoli   (adder + comparison + fixup)
  =>  Toffoli ~ 8 t n^2  with t = 2n+1,  i.e. ~16 n^3
    1 Toffoli ~ 6 CNOT
This is deliberately unoptimised. Windowed arithmetic (Gidney-Ekera 2019)
does far better, and the comparison is printed below.

Run:  .venv/bin/python predecessors/04-shor/shor_resources.py
"""

import sys
from math import ceil, log2
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "machines"))

from feasibility import Profile, assess  # noqa: E402

TOFFOLI_TO_CNOT = 6


def circuit_shape(N):
    """The structure our simulator actually runs (see shor.py)."""
    m = ceil(log2(N + 1))          # work qubits
    t = 2 * m + 1                  # counting qubits
    return dict(
        N=N, work=m, counting=t, qubits=t + m,
        hadamards=t,
        controlled_mults=t,                       # the U^(2^j) cascade
        qft_phase_gates=t * (t - 1) // 2,         # inverse QFT
    )


def arithmetic_cost(N=None, bits=None):
    """Schoolbook reversible-arithmetic cost of the same circuit.

    Pass `bits` directly for moduli too large to hold as an integer.
    """
    n = bits if bits is not None else ceil(log2(N + 1))
    t = 2 * n + 1
    toffoli = 8 * t * n * n
    return dict(n=n, toffoli=toffoli, cnot=toffoli * TOFFOLI_TO_CNOT)


def feasibility(N):
    """Ask the machine catalog whether this circuit survives."""
    shape, cost = circuit_shape(N), arithmetic_cost(N)
    prof = Profile(qubits=shape["qubits"], g2=cost["cnot"],
                   g1=shape["hadamards"], pattern="nonlocal")
    return prof, assess(prof)


if __name__ == "__main__":
    print("1. the circuit our simulator runs\n")
    print(f"   {'N':>5}{'work':>6}{'counting':>10}{'qubits':>8}"
          f"{'ctrl-mults':>12}{'QFT phases':>12}")
    for N in (15, 21, 35, 2047, 10 ** 6 + 3):
        s = circuit_shape(N)
        print(f"   {s['N']:>5}{s['work']:>6}{s['counting']:>10}"
              f"{s['qubits']:>8}{s['controlled_mults']:>12}"
              f"{s['qft_phase_gates']:>12}")

    print("\n2. what the modular arithmetic really costs "
          "(schoolbook model)\n")
    print(f"   {'N':>8}{'bits n':>8}{'Toffoli':>14}{'2-qubit gates':>16}")
    for N in (15, 21, 35, 2047):
        c = arithmetic_cost(N)
        print(f"   {N:>8}{c['n']:>8}{c['toffoli']:>14,}{c['cnot']:>16,}")

    print("\n3. can any machine that exists run Shor on N = 15?\n")
    prof, rows = feasibility(15)
    print(f"   profile: {prof.qubits} qubits, {prof.g2:,} two-qubit gates\n")
    print(f"   {'machine':<34}{'verdict':>11}{'P(no error)':>14}")
    for r in rows:
        print(f"   {r['machine']:<34}{r['verdict']:>11}"
              f"{r['fidelity']:>14.2e}")

    print("\n4. RSA-2048, the thing everyone means\n")
    c = arithmetic_cost(bits=2048)
    print(f"   schoolbook model here:      {c['toffoli']:.2e} Toffoli")
    print(f"   Gidney-Ekera 2019 (windowed): 2.7e+09 Toffoli, "
          f"~2e7 physical qubits")
    print(f"   ratio (how much optimisation buys): "
          f"{c['toffoli'] / 2.7e9:.0f}x")
    print("\n   Either way the conclusion is the same one the machines")
    print("   catalog reaches independently: this needs fault tolerance,")
    print("   not better NISQ hardware. See machines/gap.md.")
