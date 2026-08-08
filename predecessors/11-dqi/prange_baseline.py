"""The classical baseline DQI has to beat, implemented and measured.

The autopsy's ledger says Prange achieves "satisfied fraction ~ 1/2 + o(1)"
and that random sparse instances fell to classical algorithms while
Reed-Solomon structure survived. Both statements are checkable, and checking
them turns the ledger from a table of verdicts into a table of numbers.

**Prange / information-set decoding**, for max-XORSAT: choose n of the m
constraints at random, solve those exactly by Gaussian elimination over
F_2, and let the rest fall where they may. The chosen ones are all
satisfied; the others are satisfied at chance. So

    fraction  =  n/m + (1/2)(1 - n/m)  =  1/2 + n/(2m)

with a small bonus from repeating the draw and keeping the best. That is
the line DQI's semicircle has to clear, and where it clears it is the whole
question.

Run:  .venv/bin/python predecessors/11-dqi/prange_baseline.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).parent))

from dqi_spectrum import (random_instance, satisfied_count,  # noqa: E402
                          satisfied_fraction, semicircle_prediction)


# ----------------------------------------------------- GF(2) linear algebra

def solve_gf2(rows, rhs, n):
    """Solve a linear system over F_2. Returns a solution int, or None.

    Written out rather than imported: the whole baseline is this routine
    plus a random choice, and a reader should be able to see there is no
    cleverness hiding in it.
    """
    aug = [(r, b) for r, b in zip(rows, rhs)]
    pivots = {}
    for col in range(n - 1, -1, -1):
        pick = None
        for k, (r, b) in enumerate(aug):
            if k not in pivots.values() and (r >> col) & 1:
                pick = k
                break
        if pick is None:
            continue
        pr, pb = aug[pick]
        for k, (r, b) in enumerate(aug):
            if k != pick and (r >> col) & 1:
                aug[k] = (r ^ pr, b ^ pb)
        pivots[col] = pick
    x = 0
    for col, k in pivots.items():
        if aug[k][1]:
            x |= 1 << col
    for r, b in aug:
        if r == 0 and b == 1:
            return None
    return x


# ------------------------------------------------------------- Prange -----

def prange_once(A, b, n, rng):
    """One information-set attempt: solve a random n-subset exactly."""
    m = len(A)
    idx = rng.choice(m, size=min(n, m), replace=False)
    x = solve_gf2([A[i] for i in idx], [b[i] for i in idx], n)
    if x is None:
        return None
    return satisfied_count(A, b, x)


def prange_best(A, b, n, rng, tries=40):
    """Best of `tries` information sets — the honest classical baseline.

    Repeating and keeping the best is free and is what any real attacker
    does, so the comparison uses it. Reporting single-shot Prange would be
    the same weak-baseline mistake autopsy 01 is about.
    """
    best = 0
    for _ in range(tries):
        got = prange_once(A, b, n, rng)
        if got is not None:
            best = max(best, got)
    return best


def prange_fraction(n, m, trials=12, tries=40, seed=0):
    """Measured satisfied fraction, averaged over instances."""
    rng = np.random.default_rng(seed)
    out = []
    for _ in range(trials):
        A, b = random_instance(n, m, rng)
        out.append(prange_best(A, b, n, rng, tries=tries) / m)
    return float(np.mean(out))


def prange_prediction(n, m):
    """1/2 + n/(2m): the exact constraints, plus chance on the rest.

    This is the *single-draw* expectation. Repeating and keeping the best
    adds a finite-size bonus of order sqrt(log(tries)/m), which is large at
    the sizes this file can simulate and vanishes as m grows —
    `prange_finite_size_bonus` measures exactly that, because an asymptotic
    claim defended only at m = 32 is not defended.
    """
    return 0.5 + n / (2 * m)


def prange_finite_size_bonus(ratio=0.25, ms=(32, 64, 128, 256), tries=30,
                             trials=6, seed=1):
    """Measured minus predicted, as m grows at fixed n/m.

    Should shrink like 1/sqrt(m). If it did not, the formula would be wrong
    rather than asymptotic.
    """
    out = []
    for m in ms:
        n = max(2, int(round(ratio * m)))
        meas = prange_fraction(n, m, trials=trials, tries=tries, seed=seed)
        out.append((m, meas, prange_prediction(n, m), meas -
                    prange_prediction(n, m)))
    return out


# ------------------------------------------------- the head-to-head -------

def dqi_fraction(m, ell):
    """DQI's achievable fraction at decoding radius ell."""
    return satisfied_fraction(m, ell)


def required_radius(n, m, margin=0.0):
    """Smallest decoding radius at which DQI beats Prange by `margin`.

    This is the number the whole architecture turns on. DQI's advantage is
    not "quantum beats classical"; it is "a decoder that reaches radius l
    beats an attacker who solves n equations exactly". If no decoder reaches
    that radius, there is no advantage — whatever the quantum machine does.
    """
    target = prange_prediction(n, m) + margin
    for ell in range(1, m // 2 + 1):
        if dqi_fraction(m, ell) > target:
            return ell
    return None


def advantage_window(n, m):
    """(radius needed, DQI fraction there, Prange fraction) — or None."""
    ell = required_radius(n, m)
    if ell is None:
        return None
    return ell, dqi_fraction(m, ell), prange_prediction(n, m)


# --------------------------------------------- structure versus randomness

def reed_solomon_radius(m, k, list_decoding=True):
    """How far a Reed-Solomon decoder reaches, as a fraction of m.

    Unique decoding reaches (m-k)/2 errors; Guruswami-Sudan list decoding
    reaches m - sqrt(m k). Both are *efficient and known*, which is exactly
    what a random code does not offer — and it is the whole of the
    "structure survived, randomness fell" lesson.
    """
    if list_decoding:
        return m - int(np.floor(np.sqrt(m * k)))
    return (m - k) // 2


def random_code_radius(m, n):
    """What an efficient decoder reaches for a random code: essentially the
    Prange line and no further.

    There is no known efficient decoder for a random linear code beyond the
    information-set regime — that is the assumption all of code-based
    cryptography rests on. So the radius available to DQI is the same one
    the classical attacker already has, and the advantage cancels.
    """
    return None


# ----------------------------------------------------------------- demo ----

def _demo():
    print("1 · PRANGE, MEASURED AGAINST ITS OWN FORMULA\n")
    print(f"   {'n':>5} {'m':>6} {'measured':>11} {'1/2 + n/2m':>12} "
          f"{'difference':>12}")
    for n, m in ((6, 24), (8, 32), (10, 40), (10, 80), (12, 96)):
        meas = prange_fraction(n, m, trials=8, tries=30, seed=1)
        pred = prange_prediction(n, m)
        print(f"   {n:>5} {m:>6} {meas:>11.4f} {pred:>12.4f} "
              f"{meas - pred:>12.4f}")
    print("\n   The measured fraction sits WELL above the single-draw")
    print("   formula. That is the best-of-many-draws bonus, and at these")
    print("   sizes it is worth more than 0.1 — so the baseline has to be")
    print("   the repeated version, not a single shot. The bonus is a")
    print("   finite-size effect and shrinks like 1/sqrt(m):\n")
    print(f"   {'m':>6} {'measured':>11} {'formula':>10} {'bonus':>9}")
    for m4, meas, pred, bonus in prange_finite_size_bonus():
        print(f"   {m4:>6} {meas:>11.4f} {pred:>10.4f} {bonus:>9.4f}")
    print("\n   So the asymptotic line is right and the finite-size Prange is")
    print("   stronger than it — which means the radii in the next section")
    print("   are LOWER BOUNDS on what a decoder must reach.\n")

    print("2 · THE HEAD-TO-HEAD: WHAT RADIUS DOES DQI NEED?\n")
    print(f"   {'n':>5} {'m':>6} {'Prange':>9} {'radius ℓ needed':>17} "
          f"{'d = ℓ/m':>9} {'DQI there':>11}")
    for n, m in ((10, 100), (20, 100), (40, 100), (60, 100), (80, 100)):
        win = advantage_window(n, m)
        if win is None:
            print(f"   {n:>5} {m:>6} {prange_prediction(n, m):>9.4f} "
                  f"{'unreachable':>17} {'—':>9} {'—':>11}")
            continue
        ell, dqi, pr = win
        print(f"   {n:>5} {m:>6} {pr:>9.4f} {ell:>17} {ell / m:>9.3f} "
              f"{dqi:>11.4f}")
    print("\n   Read the middle column as the specification handed to coding")
    print("   theory. DQI's advantage is NOT 'quantum beats classical' — it")
    print("   is 'a decoder reaching radius ℓ beats an attacker who solves n")
    print("   equations'. The quantum machine contributes the interference;")
    print("   the DECODER decides whether there is anything to interfere")
    print("   toward.\n")

    print("3 · WHY STRUCTURE SURVIVED AND RANDOMNESS FELL\n")
    m = 200
    print(f"   m = {m} constraints\n")
    print(f"   {'code':>28} {'radius reached':>16} {'d':>8} "
          f"{'DQI fraction':>14}")
    for k in (20, 50, 100):
        r = reed_solomon_radius(m, k)
        d = r / m
        lab = f"Reed-Solomon, k = {k}"
        print(f"   {lab:>28} {r:>16} {d:>8.3f} "
              f"{dqi_fraction(m, min(r, m // 2)):>14.4f}")
    print(f"   {'random linear code':>28} {'none known':>16} {'—':>8} "
          f"{'— (Prange line)':>14}")
    print("\n   Reed-Solomon has an efficient decoder that reaches far;")
    print("   a random code has none beyond information-set decoding — which")
    print("   is the classical attacker's own algorithm. So on random sparse")
    print("   instances DQI is asking a decoder to beat Prange using Prange,")
    print("   and the advantage cancels. **No DQI advantage without")
    print("   algebraic structure**, and now with a mechanism rather than a")
    print("   slogan: structure is what an efficient decoder needs to exist.")


if __name__ == "__main__":
    _demo()
