"""The ceiling, computed — notes.md sections 3-5.

Grover is the one algorithm in this curriculum whose optimality was proved
*before* the algorithm existed. This file makes the three parts of that
statement checkable rather than quotable:

  1. the rotation formula, verified against the real circuit;
  2. Zalka's tight ceiling — no T-query algorithm beats sin^2((2T+1)theta),
     and Grover attains it exactly, so the quadratic is a wall on both
     sides;
  3. the BBBV hybrid argument run on the actual state vector: the total
     query attention is exactly T, so some item receives at most T/N of it,
     and marking that item barely moves the output.

Plus the two facts that decide whether Grover is usable: what happens when
you do not know how many solutions there are, and what parallel machines
buy you (much less than you would expect).

Run:  .venv/bin/python predecessors/06-grover/grover_limits.py
"""

from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(Path(__file__).parent))

from qsim import H, amplitudes, apply, phase_oracle, zero_state  # noqa: E402

from grover import diffusion  # noqa: E402


# ------------------------------------------------------ the rotation -------

def theta(N, M=1):
    """Half the rotation angle: sin(theta) = sqrt(M/N).

    The whole algorithm lives in the two-dimensional plane spanned by "the
    marked items" and "everything else", and one iteration turns the state
    by 2*theta. That is the entire mechanism.
    """
    return np.arcsin(np.sqrt(M / N))


def success_probability(N, M, t):
    """sin^2((2t+1) theta) — exact, for any number of iterations."""
    return float(np.sin((2 * t + 1) * theta(N, M)) ** 2)


def optimal_iterations(N, M=1):
    """The t that maximises the success probability.

    Solve (2t+1) theta = pi/2 for t: the state should land exactly on the
    marked axis, so t = pi/(4 theta) - 1/2, rounded. For large N this is the
    familiar (pi/4)sqrt(N/M), but the exact form is what the tests check —
    `test_optimal_iterations_are_the_first_peak` brute-forces every t and
    compares, because a factor of two hidden in this line silently halves
    every success probability on the page.

    Valid when M << N, which is the only regime anyone runs Grover in. Once
    M/N approaches 1/2 the very first rotation overshoots and the rounding
    stops being reliable (N = 16, M = 7 is a concrete counterexample) — but
    there random guessing already succeeds 44% of the time, so the question
    does not arise.
    """
    return int(round(np.pi / (4 * theta(N, M)) - 0.5))


def simulate(n, marked, iterations):
    """Run the real circuit and return the full state, not just the answer."""
    oracle = phase_oracle(lambda x: x in marked, n)
    D = diffusion(n)
    qubits = list(range(n))
    psi = zero_state(n)
    for q in qubits:
        psi = apply(psi, H, [q])
    for _ in range(iterations):
        psi = apply(psi, oracle, qubits)
        psi = apply(psi, D, qubits)
    return psi


def simulated_success(n, marked, iterations):
    amps = amplitudes(simulate(n, marked, iterations))
    return float(sum(abs(amps[m]) ** 2 for m in marked))


# ------------------------------------------------- the souffle problem -----

def overshoot_curve(N, M, t_max):
    """Success probability for t = 0..t_max. It oscillates; it does not settle.

    Grover is not a "keep going until it works" algorithm. Run it twice as
    long as you should and the state sails past the target and back out
    again — which is why every application needs to know N and M in advance,
    or pay for the search in the next function.
    """
    return [success_probability(N, M, t) for t in range(t_max + 1)]


def bbht_expected_queries(N, M, rng, trials=400, lam=6 / 5):
    """Boyer-Brassard-Hoyer-Tapp: searching when you do NOT know M.

    Pick a random iteration count below a bound m, run, check the answer
    classically, and grow m by 6/5 on failure. Simulated with the exact
    success formula rather than a state vector, so large N is affordable.
    The expected cost stays O(sqrt(N/M)) — but the constant is worse, and
    the "check the answer classically" step is the part that quietly
    requires the oracle to be a *computed predicate* rather than a database.
    """
    total = 0
    for _ in range(trials):
        m, queries = 1.0, 0
        while True:
            t = int(rng.integers(0, max(1, int(m))))
            queries += t + 1                     # +1 for the classical check
            if rng.random() < success_probability(N, M, t):
                break
            m = min(lam * m, np.sqrt(N))
            if queries > 200 * np.sqrt(N / M):
                break
        total += queries
    return total / trials


# ------------------------------------------- the hybrid argument, run ------

def query_magnitudes(n, iterations):
    """Total "query attention" each item receives, from the real circuit.

    Run the algorithm on the *unmarked* oracle and record, at every query,
    how much amplitude sits on each item:

        q_x = sum over queries t of |alpha_{x,t}|^2 ,   sum_x q_x = T .

    That sum rule is the whole of BBBV. T units of attention spread over N
    items means some item gets at most T/N, and an oracle that marks *that*
    item perturbs the run by very little — so the algorithm cannot tell it
    apart from the empty oracle unless T is large.
    """
    D = diffusion(n)
    qubits = list(range(n))
    psi = zero_state(n)
    for q in qubits:
        psi = apply(psi, H, [q])
    mags = np.zeros(1 << n)
    for _ in range(iterations):
        mags += np.abs(amplitudes(psi)) ** 2      # attention at this query
        psi = apply(psi, D, qubits)               # empty oracle = identity
    return mags


def bbbv_bound(N, T):
    """How far marking the least-attended item can move the final state.

    Cauchy-Schwarz on the hybrid argument: the deviation is at most
    2*sqrt(T*q_x) <= 2T/sqrt(N) for the item with the least attention.
    Telling two states apart with constant probability needs that to be a
    constant, so T = Omega(sqrt(N)). The bound is drawn against the real
    circuit in the figures.
    """
    return 2.0 * T / np.sqrt(N)


def queries_for_constant_distinguishability(N, deviation=1.0):
    """The T at which BBBV stops forbidding success: T >= deviation*sqrt(N)/2."""
    return deviation * np.sqrt(N) / 2.0


def zalka_ceiling(N, M, T):
    """The best success probability ANY algorithm with T queries can reach.

    Zalka (1999) closed the constant: the bound is the Grover curve, so
    Grover is not merely asymptotically optimal, it is optimal — no cleverer
    schedule, no better diffusion operator, no room left.

    One subtlety worth getting right: the ceiling is *monotone* in T, while
    the Grover curve is not. An algorithm allowed T queries may always use
    fewer, so once t_opt is affordable the bound stays at its maximum. The
    ceiling is therefore the running maximum, and the gap that opens between
    it and the Grover curve past t_opt is not slack in the bound — it is the
    souffle, i.e. Grover failing to stop.
    """
    best = max(success_probability(N, M, t) for t in range(int(T) + 1))
    return best


def strategy_attention_classical(N, T):
    """Attention profile of a plain classical checker: T items, one unit each.

    Included for contrast with `query_magnitudes`. Both profiles sum to T —
    that is the sum rule — but this one leaves N - T items with *zero*
    attention, so marking any of them is perfectly invisible. Grover instead
    spreads T/N everywhere, which is the extremal way to satisfy the same
    constraint. Either way the pigeonhole bites: some item gets at most T/N.
    """
    prof = np.zeros(N)
    prof[:min(T, N)] = 1.0
    return prof


# ------------------------------------------------------- parallelism -------

def parallel_speedup_quantum(k):
    """k independent quantum searchers give only sqrt(k), not k.

    Each machine searches its own N/k slice in sqrt(N/k) queries, so the
    wall-clock improvement over one machine is sqrt(k). Zalka proved this is
    optimal for parallel quantum search too.
    """
    return np.sqrt(k)


def parallel_speedup_classical(k):
    """k independent classical searchers give exactly k. Embarrassingly
    parallel, and this asymmetry is what erases the quadratic advantage
    whenever hardware can be bought in bulk."""
    return float(k)


def parallel_crossover(k_max=1 << 40):
    """Where a classical cluster of k machines matches one quantum machine.

    Quantum: sqrt(N) queries. Classical with k cores: N/k. They tie at
    k = sqrt(N) — so an attacker with sqrt(N) classical cores has already
    matched the quantum machine, before any constant factors are counted.
    """
    return "k = sqrt(N)"


# ----------------------------------------------------------------- demo ----

def _demo():
    print("1 · THE ROTATION, CHECKED AGAINST THE CIRCUIT\n")
    n, marked = 8, (137,)
    N = 1 << n
    t_opt = optimal_iterations(N, 1)
    print(f"   n = {n} (N = {N}), optimal t = {t_opt}")
    print(f"   {'t':>4} {'formula':>10} {'circuit':>10} {'|diff|':>10}")
    for t in (0, 1, t_opt // 2, t_opt, 2 * t_opt):
        f = success_probability(N, 1, t)
        c = simulated_success(n, marked, t)
        print(f"   {t:>4} {f:>10.6f} {c:>10.6f} {abs(f - c):>10.1e}")
    print("\n   the souffle: twice the optimal number of queries is WORSE "
          f"({success_probability(N, 1, 2 * t_opt):.3f} vs "
          f"{success_probability(N, 1, t_opt):.3f})")

    print("\n2 · THE HYBRID ARGUMENT, RUN ON THE REAL STATE VECTOR\n")
    for n in (6, 8, 10):
        N = 1 << n
        T = optimal_iterations(N, 1)
        mags = query_magnitudes(n, T)
        print(f"   n = {n:2d}  T = {T:3d}   sum of attention = {mags.sum():.6f}"
              f" (= T)   min per item = {mags.min():.2e}  (T/N = {T / N:.2e})")
    print("\n   spread T units of attention over N items and something gets"
          "\n   almost none. Marking that item moves the answer by at most"
          "\n   2T/sqrt(N) — so T must grow like sqrt(N). That is the whole"
          "\n   proof, and it was published before Grover's algorithm.")

    print("\n3 · GROVER SITS EXACTLY ON THE CEILING\n")
    N = 4096
    print(f"   N = {N}: no T-query algorithm can beat the Grover curve")
    print(f"   {'T':>5} {'Grover':>10} {'ceiling':>10} {'gap':>8}")
    for T in (1, 5, 10, 25, 50):
        print(f"   {T:>5} {success_probability(N, 1, T):>10.6f} "
              f"{zalka_ceiling(N, 1, T):>10.6f} "
              f"{abs(success_probability(N, 1, T) - zalka_ceiling(N, 1, T)):>8.0e}")

    print("\n4 · WHEN YOU DO NOT KNOW HOW MANY SOLUTIONS THERE ARE\n")
    rng = np.random.default_rng(0)
    print(f"   {'N':>8} {'M':>4} {'sqrt(N/M)':>11} {'BBHT measured':>15}")
    for N, M in ((4096, 1), (4096, 4), (65536, 1), (65536, 16)):
        exp = bbht_expected_queries(N, M, rng)
        print(f"   {N:>8} {M:>4} {np.sqrt(N / M):>11.1f} {exp:>15.1f}")

    print("\n5 · PARALLELISM — THE ASYMMETRY THAT DECIDES IT\n")
    print(f"   {'machines k':>12} {'classical':>12} {'quantum':>10}")
    for k in (1, 10, 1000, 10 ** 6, 10 ** 9):
        print(f"   {k:>12,} {parallel_speedup_classical(k):>12,.0f}x "
              f"{parallel_speedup_quantum(k):>9,.0f}x")
    print("\n   classical search is embarrassingly parallel; quantum search")
    print("   is not. A cluster of sqrt(N) classical cores already matches")
    print("   one quantum machine — before a single constant factor is")
    print("   counted. See grover_resources.py for those constants.")


if __name__ == "__main__":
    _demo()
