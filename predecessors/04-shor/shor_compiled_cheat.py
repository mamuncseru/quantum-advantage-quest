"""Why every published "Shor factorization" is compiled — notes.md §8.

Smolin, Smith and Vargo (Nature 499, 163, 2013; "Oversimplifying quantum
factoring") pointed out that experimental factorizations of 15, 21, 143
and friends all used circuits simplified with prior knowledge of the
answer. This file makes that concrete on our own implementation, and
turns the critique into a number you can compute.

THE MECHANISM. Shor's cascade applies controlled-U^(2^j) for
j = 0..t-1, where U is multiplication by a mod N. That gate is the
IDENTITY exactly when a^(2^j) = 1 mod N, i.e. when the order r divides
2^j. So:

    r a power of two  ->  the cascade collapses to log2(r) real gates
    r with any odd factor  ->  every one of the t gates is non-trivial

A demonstration therefore wants an a whose order is a small power of
two. With r = 2 the whole quantum cascade is ONE controlled operation,
and the "factorization" is a toy circuit.

THE CATCH. To choose such an a you must know its order -- which is the
problem the algorithm is supposed to solve. Picking the convenient a is
using the answer to compute the answer.

AND THE PUNCHLINE. For N = 15 every unit has order 1, 2 or 4 -- all
powers of two -- so the collapse happens no matter which a you pick.
The exact criterion (measured, then proved): every base collapses iff
lambda(N) is a power of two, which for odd squarefree N happens iff N is
a product of DISTINCT FERMAT PRIMES (3, 5, 17, 257, 65537). So 15 = 3x5,
51 = 3x17, 85 = 5x17 and 255 = 3x5x17 are all "free" -- and 15 is simply
the smallest. That is why 15 is the number in every demonstration, and
why factoring 15 on hardware demonstrates approximately nothing.

Run:  .venv/bin/python predecessors/04-shor/shor_compiled_cheat.py
"""

import sys
from math import ceil, gcd, log2
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[2]))


def order(a, N):
    v, k = a % N, 1
    while v != 1:
        v = (v * a) % N
        k += 1
        if k > N:
            return None
    return k


def units(N):
    return [a for a in range(2, N) if gcd(a, N) == 1]


def nontrivial_gates(a, N, t=None):
    """How many of the t controlled-U^(2^j) are NOT the identity."""
    m = ceil(log2(N + 1))
    t = t or 2 * m + 1
    return sum(1 for j in range(t) if pow(a, 2 ** j, N) != 1)


def is_power_of_two(x):
    return x is not None and x > 0 and (x & (x - 1)) == 0


def useful(a, N):
    """Does this a actually yield a factor? (r even, a^(r/2) != -1)"""
    r = order(a, N)
    if r is None or r % 2:
        return False
    x = pow(a, r // 2, N)
    if x == N - 1:
        return False
    return any(1 < gcd(x + d, N) < N for d in (-1, 1))


def survey(N):
    m = ceil(log2(N + 1))
    t = 2 * m + 1
    rows = []
    for a in units(N):
        r = order(a, N)
        rows.append(dict(a=a, r=r, gates=nontrivial_gates(a, N, t),
                         collapses=is_power_of_two(r), useful=useful(a, N)))
    return t, rows


if __name__ == "__main__":
    for N in (15, 21, 35):
        t, rows = survey(N)
        coll = [r for r in rows if r["collapses"]]
        print(f"N = {N}   ({t} counting qubits, so {t} controlled "
              f"multiplications in an honest circuit)")
        print(f"   {'a':>4}{'order r':>9}{'non-trivial gates':>20}"
              f"{'collapses?':>13}{'gives a factor?':>17}")
        for r in rows:
            print(f"   {r['a']:>4}{str(r['r']):>9}{r['gates']:>20}"
                  f"{('YES' if r['collapses'] else '-'):>13}"
                  f"{('yes' if r['useful'] else 'no'):>17}")
        frac = len(coll) / len(rows)
        print(f"   -> {len(coll)}/{len(rows)} choices of a "
              f"({frac:.0%}) collapse the cascade")
        best = min(rows, key=lambda r: r["gates"])
        print(f"   -> cheapest demo: a = {best['a']} needs "
              f"{best['gates']} of {t} gates "
              f"({100 * (1 - best['gates'] / t):.0f}% of the circuit "
              f"disappears)\n")

    print("Reading:")
    print("  For N = 15 EVERY a collapses — which is why 15 is the number")
    print("  in every demonstration. For N = 21 and 35 only a minority do,")
    print("  and identifying them requires knowing the order first.")
    print("  A compiled demo is therefore a circuit built from the answer;")
    print("  it shows the hardware can execute gates, and nothing about")
    print("  factoring. See notes.md section 8.")
