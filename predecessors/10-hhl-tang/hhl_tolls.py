"""The four tolls at HHL's door, each with a number attached.

Aaronson's "Read the fine print" lists four caveats. The autopsy repeats
them; this file prices them, because the difference between "there is a
caveat" and "the caveat costs 10^6 samples" is the whole argument.

  1. INPUT   — |b> has to come from somewhere.
  2. KAPPA   — the condition number enters polynomially, and real matrices
               have bad ones.
  3. OUTPUT  — you get a *state*, not a vector. Reading x costs dim samples;
               reading one number out of it costs 1/eps^2.
  4. RANK    — if A is low-rank, the classical side gets the same access
               (that is `dequantize.py`).

The honest summary the accounting produces: HHL's polylog(dim) is the cost
of *preparing a state proportional to the answer*, and every use of that
state that a person would call "solving Ax = b" reintroduces a factor the
polylog was supposed to remove.

Run:  .venv/bin/python predecessors/10-hhl-tang/hhl_tolls.py
"""

from __future__ import annotations

import numpy as np


# ------------------------------------------------------------ the matrix ---

def random_spd(dim, kappa, seed=0):
    """A symmetric positive-definite matrix with a prescribed condition number."""
    rng = np.random.default_rng(seed)
    Q = np.linalg.qr(rng.normal(size=(dim, dim)))[0]
    lam = np.geomspace(1.0, 1.0 / kappa, dim)
    return (Q * lam) @ Q.T


def sparse_spd(dim, kappa=None, seed=0):
    """A tridiagonal system — the sparse, structured case HHL is aimed at.

    Its condition number is not chosen but *emerges*, and it emerges bad:
    the discrete Laplacian's kappa grows like dim^2, which is measured below.
    """
    A = np.zeros((dim, dim))
    i = np.arange(dim)
    A[i, i] = 2.0
    A[i[:-1], i[:-1] + 1] = -1.0
    A[i[:-1] + 1, i[:-1]] = -1.0
    return A


def condition_number(A):
    s = np.linalg.svd(A, compute_uv=False)
    return float(s[0] / s[-1])


# --------------------------------------------------------- toll 3: output --

def samples_to_read_one_amplitude(eps, delta=0.05):
    """Measuring one component of |x> to additive error eps.

    Each shot is a Bernoulli draw, so Hoeffding needs ~log(2/delta)/(2 eps^2)
    of them. Independent of dimension — this is the case HHL is genuinely
    good at, and it is also the case where the answer is a single number.
    """
    return int(np.ceil(np.log(2 / delta) / (2 * eps ** 2)))


def samples_to_read_the_whole_vector(dim, eps, delta=0.05):
    """Reading all `dim` components to accuracy eps each.

    Union bound over dim components, so log(dim) enters — but the leading
    factor is dim itself, because every component needs its own statistics.
    THIS is the toll: the algorithm that runs in polylog(dim) hands you an
    object that costs dim to look at.
    """
    return int(np.ceil(dim * np.log(2 * dim / delta) / (2 * eps ** 2)))


def useful_outputs():
    """What you *can* extract cheaply, and what you cannot."""
    return [
        ("one amplitude x_i", "O(1/eps^2)", "cheap — dimension-free"),
        ("an expectation <x|M|x>", "O(1/eps^2)", "cheap, if M is simple"),
        ("the location of the largest x_i", "O(dim) in general", "expensive"),
        ("the whole vector x", "O(dim/eps^2)", "expensive — the toll"),
    ]


# ---------------------------------------------------------- toll 2: kappa --

def hhl_runtime(dim, kappa, eps, sparsity=4, qsvt=True):
    """A stated cost model, in block-encoding applications.

    QSVT-era: O(s * kappa * log(1/eps) * log(dim)). The original HHL had
    kappa^2/eps. Either way kappa is multiplicative and log(dim) is the only
    place the promised exponential lives.
    """
    k = kappa if qsvt else kappa ** 2 / eps
    return sparsity * k * (np.log(1 / eps) if qsvt else 1.0) * np.log2(dim)


def classical_cg_runtime(dim, kappa, eps, sparsity=4):
    """Conjugate gradients on the same sparse system: O(s*dim*sqrt(kappa)*log(1/eps)).

    The honest classical baseline for a sparse SPD system is not Gaussian
    elimination. CG costs one sparse mat-vec per iteration and needs
    O(sqrt(kappa) log(1/eps)) of them — note the SQUARE ROOT, which quantum
    does not have.
    """
    return sparsity * dim * np.sqrt(kappa) * np.log(1 / eps)


def hhl_with_readout_runtime(dim, kappa, eps, sparsity=4):
    """HHL's cost when it is asked to return the same object CG returns.

    One state preparation costs `hhl_runtime`; reading the whole vector out
    needs `samples_to_read_the_whole_vector` independent preparations. This
    is the only comparison in which both sides deliver x, and it is the one
    that never appears on a slide.
    """
    return hhl_runtime(dim, kappa, eps, sparsity) * \
        samples_to_read_the_whole_vector(dim, eps)


def readout_penalty(dim, kappa, eps=1e-3, sparsity=4):
    """How much worse HHL is than CG once both return the vector.

    Always greater than one, and growing: the quantum side pays kappa where
    CG pays sqrt(kappa), and then pays dim/eps^2 on top to look at its own
    answer. There is no crossover to find.
    """
    return (hhl_with_readout_runtime(dim, kappa, eps, sparsity)
            / classical_cg_runtime(dim, kappa, eps, sparsity))


def crossover_dimension(kappa, eps=1e-6, sparsity=4):
    """Dimension above which HHL's state *preparation* beats CG's full solve.

    Deliberately the unfair comparison — CG returns the vector, HHL returns
    a state — because it is the one quoted in talks. `readout_penalty` is
    the fair version, and it has no crossover at all.
    """
    lo, hi = 4, 2 ** 60
    while lo < hi:
        mid = (lo + hi) // 2
        if hhl_runtime(mid, kappa, eps, sparsity) < \
                classical_cg_runtime(mid, kappa, eps, sparsity):
            hi = mid
        else:
            lo = mid + 1
    return lo


# ----------------------------------------------------------------- demo ----

def _demo():
    print("1 · TOLL 3, THE OUTPUT: YOU GET A STATE, NOT A VECTOR\n")
    print(f"   {'what you want':>34} {'cost':>22} {'verdict':>26}")
    for what, cost, verdict in useful_outputs():
        print(f"   {what:>34} {cost:>22} {verdict:>26}")
    print()
    print(f"   {'dimension':>12} {'read one amplitude':>20} "
          f"{'read the whole vector':>24}")
    for dim in (10 ** 3, 10 ** 6, 10 ** 9):
        print(f"   {dim:>12,} {samples_to_read_one_amplitude(0.01):>20,} "
              f"{samples_to_read_the_whole_vector(dim, 0.01):>24.2e}")
    print("\n   The algorithm runs in polylog(dim) and produces an object")
    print("   that costs dim to look at. Every honest application therefore")
    print("   has to end in ONE number — which is a real but much narrower")
    print("   claim than 'quantum computers solve linear systems'.\n")

    print("2 · TOLL 2, KAPPA: IT IS NOT A CONSTANT\n")
    print("   the discrete Laplacian — the textbook sparse system:\n")
    print(f"   {'dimension':>12} {'condition number':>18} "
          f"{'grows like':>14}")
    prev = None
    for dim in (16, 32, 64, 128, 256):
        k = condition_number(sparse_spd(dim))
        ratio = f"{k / prev:.2f}x" if prev else "—"
        prev = k
        print(f"   {dim:>12} {k:>18.1f} {ratio:>14}")
    print("\n   kappa roughly quadruples when the dimension doubles: kappa ~")
    print("   dim^2. So for this system 'kappa is polylog' is false, and the")
    print("   kappa factor eats the log(dim) advantage outright.\n")

    print("3 · AGAINST CONJUGATE GRADIENTS — TWICE, FAIRLY AND UNFAIRLY\n")
    print("   (a) the comparison usually quoted: HHL prepares a STATE,")
    print("   conjugate gradients returns the VECTOR.\n")
    print(f"   {'kappa':>10} {'crossover dimension':>22}")
    for kappa in (10, 100, 10 ** 4, 10 ** 6):
        print(f"   {kappa:>10,} {crossover_dimension(kappa):>22.3e}")
    print("\n   Even here the story is not 'exponential': CG needs")
    print("   sqrt(kappa) iterations and the quantum algorithm needs kappa,")
    print("   so the crossover moves RIGHT as the problem gets harder.\n")
    print("   (b) the comparison where both sides return x:\n")
    print(f"   {'dimension':>12} {'kappa':>10} "
          f"{'HHL+readout / CG':>20}")
    for dim, kappa in ((10 ** 3, 10), (10 ** 6, 10), (10 ** 6, 10 ** 4),
                       (10 ** 9, 10 ** 4)):
        print(f"   {dim:>12,} {kappa:>10,} "
              f"{readout_penalty(dim, kappa):>20.2e}")
    print("\n   Always worse, by a growing margin. There is no crossover to")
    print("   find, because the quantum side pays kappa where CG pays its")
    print("   square root and then pays dim/eps^2 to read its own answer.")
    print("   The polylog is real; it is the cost of preparing a state, and")
    print("   the state is not the answer.")

    print("\n4 · WHAT IS LEFT WHEN ALL FOUR TOLLS ARE PAID\n")
    print("   sparse, high-rank, well-conditioned A;  |b> from a quantum")
    print("   process rather than loaded from data;  and an answer that is")
    print("   ONE expectation value rather than the vector. That regime is")
    print("   real and BQP-complete — and it is not linear algebra as any")
    print("   user of linear algebra means the phrase.")


if __name__ == "__main__":
    _demo()
