"""The wall, computed: where Fourier sampling stops carrying information.

Three experiments, none of which needs to be taken on faith:

1. **Symmetric group.** Build the character table of S_n from the
   Murnaghan-Nakayama rule, then compute exactly how distinguishable a
   hidden involution is from no hidden subgroup at all under weak Fourier
   sampling. The answer separates sharply: a *transposition* is easy to see,
   a *fixed-point-free involution* — the one graph isomorphism actually
   hands you — is invisible.

2. **Dihedral group.** Build the D_N Fourier transform from its irreducible
   representations, transform a real coset state, and measure. The
   distribution over representation labels turns out to be identical for
   every hidden reflection, so the label carries exactly zero bits. All the
   information sits in a relative phase inside a two-dimensional block.

3. **Kuperberg's sieve, in shape.** Copies carry phases; combining two
   copies produces the sum or difference of their labels. Cancel low bits,
   repeat. This is why the dihedral case is subexponential rather than
   polynomial or exponential.

Run:  .venv/bin/python predecessors/05-hsp-graveyard/nonabelian_wall.py
"""

from __future__ import annotations

from functools import lru_cache
from math import factorial

import numpy as np


# ============================================================ partitions ====

def partitions(n, maxpart=None):
    """All partitions of n, as weakly decreasing tuples — the labels of both
    the conjugacy classes and the irreducible representations of S_n."""
    if maxpart is None:
        maxpart = n
    if n == 0:
        yield ()
        return
    for first in range(min(n, maxpart), 0, -1):
        for rest in partitions(n - first, first):
            yield (first,) + rest


def class_size(rho, n):
    """How many permutations have cycle type rho: n! / (prod k^m_k m_k!)."""
    counts = {}
    for part in rho:
        counts[part] = counts.get(part, 0) + 1
    denom = 1
    for k, m in counts.items():
        denom *= (k ** m) * factorial(m)
    return factorial(n) // denom


# =============================================== characters of S_n (M-N) ====

def beta_set(lam):
    """First-column hook lengths: strictly decreasing beta_i = lam_i + m-1-i.

    Removing a border strip of length k is exactly "subtract k from one beta
    and keep them distinct", which is why this encoding makes the
    Murnaghan-Nakayama rule a two-line loop instead of a picture.
    """
    m = len(lam)
    return tuple(lam[i] + m - 1 - i for i in range(m))


def from_beta(betas):
    betas = tuple(sorted(betas, reverse=True))
    m = len(betas)
    lam = tuple(betas[i] - (m - 1 - i) for i in range(m))
    return tuple(p for p in lam if p > 0)


@lru_cache(maxsize=None)
def character(lam, rho):
    """chi_lambda(rho) by the Murnaghan-Nakayama recursion.

    Peel one cycle of length rho[0] off as a border strip in every legal
    way; each removal contributes (-1)^(height of the strip). The height is
    the number of beta values strictly between the old and new one.
    """
    if not rho:
        return 1 if not lam else 0
    k, rest = rho[0], rho[1:]
    betas = beta_set(lam)
    total = 0
    for i, b in enumerate(betas):
        nb = b - k
        if nb < 0 or nb in betas:
            continue
        height = sum(1 for x in betas if nb < x < b)
        newlam = from_beta(betas[:i] + (nb,) + betas[i + 1:])
        total += (-1) ** height * character(newlam, rest)
    return total


def dimension(lam):
    """d_lambda = chi_lambda(1,1,...,1) — the size of the representation."""
    n = sum(lam)
    return character(lam, tuple([1] * n))


def hook_length_dimension(lam):
    """The same number by the hook length formula — an independent check."""
    n = sum(lam)
    conj = [sum(1 for p in lam if p > j) for j in range(lam[0])] if lam else []
    prod = 1
    for i, row in enumerate(lam):
        for j in range(row):
            prod *= (row - j) + (conj[j] - i) - 1
    return factorial(n) // prod


def character_table(n):
    """{(lambda, rho): chi} for every irrep and every cycle type."""
    parts = list(partitions(n))
    return {(lam, rho): character(lam, rho) for lam in parts for rho in parts}


# ================================== weak Fourier sampling over S_n ==========

def weak_sampling_distribution(n, subgroup_cycle_types):
    """P(lambda) = (d_lambda / |G|) * sum over h in H of chi_lambda(h).

    `subgroup_cycle_types` lists the cycle type of every element of H,
    including the identity. For H = {e} this is the Plancherel distribution
    d^2/|G|; for a hidden involution it is that, tilted by the character of
    the involution — and the whole question is how big the tilt is.
    """
    G = factorial(n)
    out = {}
    for lam in partitions(n):
        d = dimension(lam)
        out[lam] = (d / G) * sum(character(lam, rho)
                                 for rho in subgroup_cycle_types)
    return out


def identity_type(n):
    return tuple([1] * n)


def transposition_type(n):
    """One swap, n-2 fixed points: the *easy* involution."""
    return tuple([2] + [1] * (n - 2))


def fixed_point_free_type(n):
    """n/2 disjoint swaps: the involution graph isomorphism actually gives
    you, and the one Moore-Russell-Schulman proved is invisible."""
    assert n % 2 == 0
    return tuple([2] * (n // 2))


def total_variation(n, involution_type):
    """How well one weak Fourier sample separates {e, tau} from {e}.

    TV = 1/2 sum_lambda (d_lambda / |G|) |chi_lambda(tau)|. Distinguishing
    two distributions this close needs on the order of 1/TV^2 samples, so a
    TV that decays exponentially in n is a wall, not a slow patch.
    """
    G = factorial(n)
    return 0.5 * sum(dimension(lam) * abs(character(lam, involution_type)) / G
                     for lam in partitions(n))


def samples_needed(tv):
    """Order-of-magnitude copies to tell the two cases apart: ~1/TV^2."""
    return float("inf") if tv <= 0 else 1.0 / tv ** 2


# ============================================ dihedral group D_N ============

class Dihedral:
    """D_N = {r^a s^b}, order 2N. Elements are pairs (a, b).

    Multiplication: (a1,b1)(a2,b2) = (a1 + (-1)^b1 a2, b1 xor b2). This is
    the smallest group that is "barely non-abelian", and it is where lattice
    cryptography's fate sits.
    """

    def __init__(self, N):
        self.N = N
        self.order = 2 * N

    def elements(self):
        return [(a, b) for b in (0, 1) for a in range(self.N)]

    def index(self, g):
        a, b = g
        return b * self.N + (a % self.N)

    def multiply(self, g1, g2):
        a1, b1 = g1
        a2, b2 = g2
        return ((a1 + (a2 if b1 == 0 else -a2)) % self.N, b1 ^ b2)

    def irreps(self):
        """Every irreducible representation, as a list of (name, dim, matrices).

        Two one-dimensional ones (four when N is even) and the
        two-dimensional rho_k. The two-dimensional ones are the entire
        problem: on an abelian group every irrep is 1x1, a coset state's
        transform is a set of labels, and you read the answer off. Here the
        answer is a *matrix element*, and a measurement returns one sample
        from a block instead.
        """
        N = self.N
        reps = []

        def one_dim(sign_r, sign_s, name):
            def rep(g):
                a, b = g
                return np.array([[(sign_r ** a) * (sign_s ** b)]], dtype=complex)
            reps.append((name, 1, rep))

        one_dim(1, 1, "trivial")
        one_dim(1, -1, "sign")
        if N % 2 == 0:
            one_dim(-1, 1, "alt")
            one_dim(-1, -1, "alt-sign")

        top = (N - 1) // 2 if N % 2 else N // 2 - 1
        for k in range(1, top + 1):
            def rep(g, k=k):
                a, b = g
                w = np.exp(2j * np.pi * k * a / N)
                rot = np.array([[w, 0], [0, np.conj(w)]], dtype=complex)
                flip = np.array([[0, 1], [1, 0]], dtype=complex)
                return rot @ flip if b else rot
            reps.append((f"rho_{k}", 2, rep))
        return reps

    def fourier_matrix(self):
        """The Fourier transform of D_N: rows indexed by (irrep, i, j).

        F|g> = sum over irreps of sqrt(d/|G|) * rho(g)_ij |rho,i,j>. Unitary,
        and `test_dihedral_fourier_is_unitary` checks it rather than trusting
        the formula.
        """
        rows, labels = [], []
        els = self.elements()
        for name, d, rep in self.irreps():
            mats = [rep(g) for g in els]
            for i in range(d):
                for j in range(d):
                    rows.append([np.sqrt(d / self.order) * m[i, j]
                                 for m in mats])
                    labels.append((name, i, j))
        return np.array(rows, dtype=complex).conj(), labels

    def reflection_subgroup(self, d):
        """H_d = {identity, the reflection s r^d} — the hidden subgroup."""
        return [(0, 0), (d % self.N, 1)]

    def coset_state(self, x, d):
        """The state a real dihedral HSP run leaves in the first register."""
        v = np.zeros(self.order, dtype=complex)
        for h in self.reflection_subgroup(d):
            v[self.index(self.multiply(x, h))] = 1.0
        return v / np.linalg.norm(v)


def dihedral_label_distribution(D, d, average_over_cosets=True):
    """P(irrep label) for a hidden reflection at offset d.

    Measured, and the measurement corrects the usual slogan. The
    *two-dimensional* labels are exactly uniform and exactly independent of
    d — they carry zero information, for every N. The one-dimensional labels
    are not quite silent: when N is even they reveal the **parity of d**, and
    nothing else. One bit out of log N.

    That single bit is the whole reason the dihedral case sits where it does.
    Weak sampling is not useless (so the problem is not maximally hard) and
    not enough (so the problem is not easy), and everything past that bit
    lives in phases that only Kuperberg-style recombination can reach.
    """
    F, labels = D.fourier_matrix()
    names = sorted({lab[0] for lab in labels})
    starts = [x for x in (D.elements() if average_over_cosets else [(0, 0)])]
    acc = {nm: 0.0 for nm in names}
    for x in starts:
        amps = F @ D.coset_state(x, d)
        p = np.abs(amps) ** 2
        for (nm, _, _), pi in zip(labels, p):
            acc[nm] += pi / len(starts)
    total = sum(acc.values())
    return {nm: v / total for nm, v in acc.items()}


def dihedral_label_drift(D):
    """How much the label distribution moves when the secret moves.

    Returns (drift over all labels, drift over the 2-dimensional labels
    only), maximised over every hidden reflection. The second number is zero
    to machine precision for every N — that is the wall. The first is zero
    for odd N and 1/8 for even N, which is the parity bit leaking out of the
    one-dimensional representations.
    """
    base = dihedral_label_distribution(D, 0)
    allmax = twomax = 0.0
    for d in range(D.N):
        p = dihedral_label_distribution(D, d)
        allmax = max(allmax, max(abs(p[k] - base[k]) for k in p))
        twomax = max(twomax, max((abs(p[k] - base[k])
                                  for k in p if k.startswith("rho_")),
                                 default=0.0))
    return allmax, twomax


def dihedral_phase(D, d, k):
    """The relative phase inside block rho_k: exp(2 pi i k d / N).

    Extracted from the transformed state, not asserted. One copy gives you
    one sample of a qubit whose phase is this — worth less than one bit.
    """
    F, labels = D.fourier_matrix()
    amps = F @ D.coset_state((0, 0), d)
    rows = [i for i, lab in enumerate(labels) if lab[0] == f"rho_{k}"]
    block = np.array([amps[i] for i in rows]).reshape(2, 2)
    col = block[:, 0] if abs(block[:, 0]).sum() > 1e-12 else block[:, 1]
    return np.angle(col[1] / col[0]) if abs(col[0]) > 1e-12 else np.nan


# ================================= Kuperberg's sieve, in shape ==============

def sieve_round(labels, low_bits, rng):
    """Pair up labels agreeing on their low bits; keep the differences.

    That is Kuperberg's move: combining two copies gives a copy labelled by
    the sum or the difference, so matching low bits and subtracting clears
    them. Half the pairs are lost to the coin flip, which is where the cost
    comes from.
    """
    mask = (1 << low_bits) - 1
    buckets = {}
    for k in labels:
        buckets.setdefault(k & mask, []).append(k)
    out = []
    for group in buckets.values():
        rng.shuffle(group)
        for i in range(0, len(group) - 1, 2):
            a, b = group[i], group[i + 1]
            if rng.random() < 0.5:          # the sum branch is discarded
                continue
            diff = abs(a - b)
            if diff:
                out.append(diff)
    return out


def sieve_decay_factor(history):
    """Measured population ratio per round — the constant the cost model uses."""
    ratios = [a / b for a, b in zip(history, history[1:]) if b]
    return float(np.mean(ratios)) if ratios else float("nan")


def sieve_starting_copies(n_bits, block, decay=4.0):
    """How many copies you must start with to still have one at the end.

    Backwards recursion, calibrated against the simulation above: each round
    pairs copies inside 2^block buckets and throws away the branch that adds
    instead of subtracting, so the population falls by a constant factor and
    the bucket count is a floor on how many you need.

        need(0) = 1,  need(r) = decay * need(r-1) + 2^block

    Clearing n bits takes ceil(n/block) rounds, so a big block finishes in
    few rounds but pays 2^block per round, and a small block pays few copies
    but needs many rounds. The two costs cross at block ~ sqrt(n), and the
    minimum is 2^O(sqrt(n)) — which, with n = log N, is Kuperberg's
    2^O(sqrt(log N)). The exponent is not quoted here; it is the shape of
    this curve.
    """
    rounds = int(np.ceil(n_bits / block))
    need = 1.0
    for _ in range(rounds):
        need = decay * need + 2 ** block
    return need


def sieve_optimal_block(n_bits, decay=4.0):
    """The block size that minimises the starting population, and its cost."""
    costs = {t: sieve_starting_copies(n_bits, t, decay)
             for t in range(1, n_bits + 1)}
    best = min(costs, key=costs.get)
    return best, costs[best], costs


def sieve_run(n_bits, start_copies, rng, rounds=None):
    """Run the sieve until a label equals 2^(n-1) (which reveals one bit of d).

    Reports how many copies survive each round. Not the optimised algorithm —
    the *shape* of it, which is what explains 2^O(sqrt(log N)): each round
    clears a block of bits and costs a constant factor of the population, so
    the parameters trade block size against round count.
    """
    N = 1 << n_bits
    labels = [int(rng.integers(1, N)) for _ in range(start_copies)]
    rounds = rounds or max(1, int(np.sqrt(n_bits)))
    block = max(1, n_bits // rounds)
    history = [len(labels)]
    for _ in range(rounds):
        labels = sieve_round(labels, block, rng)
        history.append(len(labels))
        if not labels:
            break
    hit = any(k == N // 2 for k in labels)
    return dict(history=history, survivors=len(labels), found=hit,
                block=block, rounds=rounds)


# ================================================================ demo ======

def _demo():
    print("=" * 68)
    print("1 · SYMMETRIC GROUP — how visible is a hidden involution?")
    print("=" * 68)
    print("  weak Fourier sampling: P(lambda) = (d_lambda/|G|) sum_h "
          "chi_lambda(h)\n")
    print(f"  {'n':>3} {'|S_n|':>12} {'irreps':>7} "
          f"{'TV: transposition':>19} {'TV: perfect matching':>22}")
    for n in range(4, 25, 2):
        tv_t = total_variation(n, transposition_type(n))
        tv_f = total_variation(n, fixed_point_free_type(n))
        print(f"  {n:>3} {factorial(n):>12} {len(list(partitions(n))):>7} "
              f"{tv_t:>19.6f} {tv_f:>22.3e}")
    print("\n  a transposition stays visible (TV falls like 1/n, so poly(n)")
    print("  copies suffice). The fixed-point-free involution — the one graph")
    print("  isomorphism actually hands you — falls off a cliff:")
    for n in (10, 16, 24):
        tv = total_variation(n, fixed_point_free_type(n))
        print(f"    n = {n:2d}:  TV = {tv:.3e}  →  ~{samples_needed(tv):,.0f} "
              f"copies to notice the difference")

    print()
    print("=" * 68)
    print("2 · DIHEDRAL GROUP — the label carries one bit, and only one")
    print("=" * 68)
    D = Dihedral(8)
    print("  P(irrep) for each hidden reflection offset d:")
    for d in range(3):
        p = dihedral_label_distribution(D, d)
        print(f"    d = {d}: " +
              "  ".join(f"{k}={v:.3f}" for k, v in sorted(p.items())))
    for N in (7, 8, 9, 12):
        allmax, twomax = dihedral_label_drift(Dihedral(N))
        print(f"    N = {N:2d}: drift over all labels {allmax:.2e}   "
              f"over 2-dim labels only {twomax:.2e}")
    print("  → the 2-dimensional labels are EXACTLY independent of the secret.")
    print("    The 1-dimensional ones leak the parity of d when N is even —")
    print("    one bit out of log N, and then the trail goes cold.")
    print("  everything else is a phase inside the 2-dimensional block:")
    for d in (1, 2, 3):
        got = dihedral_phase(D, d, k=1)
        want = 2 * np.pi * 1 * d / D.N
        print(f"    d = {d}: measured phase {got:+.4f} rad, "
              f"2*pi*k*d/N = {want:+.4f}")

    print()
    print("=" * 68)
    print("3 · KUPERBERG'S SIEVE — trading copies for progress")
    print("=" * 68)
    rng = np.random.default_rng(3)
    for n_bits in (8, 12, 16):
        res = sieve_run(n_bits, 4000, rng)
        print(f"  N = 2^{n_bits:<3} block {res['block']} bits x "
              f"{res['rounds']} rounds:  population "
              f"{' -> '.join(str(h) for h in res['history'])}")
    print("  each round clears a block of bits and costs a constant factor of")
    print("  the population — balance the two and you get 2^O(sqrt(log N)):")
    print("  neither polynomial (a revolution) nor exponential (harmless).")


if __name__ == "__main__":
    _demo()
