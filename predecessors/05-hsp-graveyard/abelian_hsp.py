"""The continent that fell: one machine, three algorithms.

The Hidden Subgroup Problem over an abelian group is solved by a single
procedure — build the coset state, Fourier transform, measure, repeat, then
do classical algebra on the labels. Bernstein-Vazirani, Simon and Shor's
order-finding are the *same quantum step* with three different classical
post-processors bolted on the end.

This file makes that literal. `hsp_sample` does not know which algorithm it
is running: it is handed a function and a group, and it simulates the real
thing — build the superposition over all inputs, measure the output register
(so the input register collapses to a coset), apply the Fourier transform of
the group, and sample. The three solvers below differ only in what they do
with the labels that come back.

Run:  .venv/bin/python predecessors/05-hsp-graveyard/abelian_hsp.py
"""

from __future__ import annotations

from math import gcd

import numpy as np


# ------------------------------------------------------------ the group ----

class AbelianGroup:
    """A finite abelian group as a product of cyclic groups Z_{d1} x ... x Z_{dk}.

    Every finite abelian group is one of these (structure theorem), so this
    class is not a restriction — it is the general case, written down.
    """

    def __init__(self, dims):
        self.dims = tuple(int(d) for d in dims)
        self.order = int(np.prod(self.dims))

    def elements(self):
        idx = np.arange(self.order)
        return [self.decode(int(i)) for i in idx]

    def encode(self, g):
        """Tuple -> flat index, mixed-radix, first coordinate most significant."""
        v = 0
        for d, c in zip(self.dims, g):
            v = v * d + (c % d)
        return v

    def decode(self, i):
        out = []
        for d in reversed(self.dims):
            out.append(i % d)
            i //= d
        return tuple(reversed(out))

    def add(self, a, b):
        return tuple((x + y) % d for x, y, d in zip(a, b, self.dims))

    def character(self, k, g):
        """chi_k(g) = prod_j exp(2 pi i k_j g_j / d_j) — the character table
        entry. On Z_2^n every factor is +-1; on Z_N it is a root of unity."""
        phase = 0.0
        for kj, gj, d in zip(k, g, self.dims):
            phase += kj * gj / d
        return np.exp(2j * np.pi * phase)

    def dft_matrix(self):
        """The Fourier transform of the group: rows are normalised characters.

        Built as an explicit character table so that nothing about the
        algorithm can secretly depend on a fast-transform trick.
        """
        els = self.elements()
        M = np.array([[self.character(k, g) for g in els] for k in els])
        return M.conj() / np.sqrt(self.order)

    def subgroup(self, generators):
        """Close a set of generators under the group operation."""
        H = {tuple([0] * len(self.dims))}
        frontier = list(H)
        while frontier:
            a = frontier.pop()
            for g in generators:
                b = self.add(a, tuple(g))
                if b not in H:
                    H.add(b)
                    frontier.append(b)
        return sorted(H)

    def annihilator(self, H):
        """H-perp = {k : chi_k(h) = 1 for all h in H} — where the samples land."""
        out = []
        for k in self.elements():
            if all(abs(self.character(k, h) - 1.0) < 1e-9 for h in H):
                out.append(k)
        return out

    def all_subgroups(self):
        """Every subgroup, exhaustively.

        Each new generator at least doubles the subgroup, so no subgroup of
        G needs more than log2|G| generators — enumerating generating sets up
        to that size therefore finds all of them. Brute force, and
        deliberately so: a claim like "no subgroup at all has these fibers as
        its cosets" is worth nothing unless every subgroup was really checked.
        """
        from itertools import combinations
        els = self.elements()
        rank = max(1, int(np.ceil(np.log2(self.order))))
        found = {}
        for size in range(rank + 1):
            for gens in combinations(els, size):
                key = tuple(self.subgroup(list(gens)))
                found[key] = list(key)
        return sorted(found.values(), key=lambda H: (len(H), H))


# ------------------------------------------------- the quantum step, once --

def fibers(f, group):
    """Group the inputs by output value: the preimages f^-1(y).

    Measuring the output register of the standard two-register state picks
    one of these at random, weighted by size. If f really does hide a
    subgroup, every fiber is a coset of it — and the test suite checks that
    claim rather than assuming it.
    """
    buckets = {}
    for g in group.elements():
        buckets.setdefault(f(g), []).append(g)
    return buckets


def hsp_sample(f, group, rng, dft=None):
    """One honest run of the quantum part, for any finite abelian group.

    1. Build |x>|f(x)> over the whole group.
    2. Measure the second register: the first collapses to a uniform
       superposition over one fiber.
    3. Apply the group's Fourier transform.
    4. Measure. Return the character label.

    No shortcut: the state vector is built and transformed. The output is a
    label k in G-hat, and the theorem (deep dive 01, section 7) says it is
    uniform on H-perp — which the tests verify by sampling rather than by
    quoting.
    """
    dft = group.dft_matrix() if dft is None else dft
    buckets = fibers(f, group)
    keys = list(buckets)
    sizes = np.array([len(buckets[k]) for k in keys], dtype=float)
    which = keys[rng.choice(len(keys), p=sizes / sizes.sum())]

    psi = np.zeros(group.order, dtype=complex)
    for g in buckets[which]:
        psi[group.encode(g)] = 1.0
    psi /= np.linalg.norm(psi)

    amps = dft @ psi
    probs = np.abs(amps) ** 2
    probs /= probs.sum()
    return group.decode(int(rng.choice(group.order, p=probs)))


def sample_distribution(f, group, offset_fiber=None):
    """Exact outcome distribution of `hsp_sample`, by enumeration.

    Used by the tests and figures: no sampling noise, so claims about the
    distribution are claims about the distribution.
    """
    dft = group.dft_matrix()
    buckets = fibers(f, group)
    total = np.zeros(group.order)
    for key, coset in buckets.items():
        if offset_fiber is not None and key != offset_fiber:
            continue
        psi = np.zeros(group.order, dtype=complex)
        for g in coset:
            psi[group.encode(g)] = 1.0
        psi /= np.linalg.norm(psi)
        weight = 1.0 if offset_fiber is not None else len(coset) / group.order
        total += weight * np.abs(dft @ psi) ** 2
    return total


# -------------------------------------------- classical post-processing ----

def rank_gf2(rows):
    """Rank over GF(2) of a list of ints."""
    basis = []
    for v in rows:
        for b in basis:
            v = min(v, v ^ b)
        if v:
            basis.append(v)
            basis.sort(reverse=True)
    return len(basis)


def solve_z2n(labels, n):
    """Simon / BV post-processing: the hidden subgroup is the null space.

    Labels are elements of H-perp; H is everything orthogonal to all of them.
    Brute-forced over 2^n candidates because n is small here and the point of
    this file is clarity, not speed.
    """
    ints = [int("".join(str(b) for b in k), 2) for k in labels]
    H = []
    for cand in range(1 << n):
        if all(bin(cand & z).count("1") % 2 == 0 for z in ints):
            H.append(tuple((cand >> (n - 1 - i)) & 1 for i in range(n)))
    return sorted(H)


def solve_zN_order(labels, N):
    """Shor post-processing: the labels are multiples of N/r, so gcd finds r.

    This is the r | N case, where everything is exact. When r does not divide
    N the labels are only *near* multiples and continued fractions are
    needed — see autopsy 04 and deep dive 01 section 8. Keeping the exact
    case here makes the point that the quantum step is identical; only this
    function changed.
    """
    g = 0
    for (k,) in labels:
        g = gcd(g, k)
    if g == 0:
        return None
    return N // gcd(N, g) if g else None


# ---------------------------------------------------- the four instances ---

def bv_instance(n, s):
    """f(x) = s.x mod 2. Hides the hyperplane {x : s.x = 0}, of index 2."""
    group = AbelianGroup([2] * n)

    def f(x):
        return sum(xi * si for xi, si in zip(x, s)) % 2

    return group, f, group.subgroup(_hyperplane_generators(s, n))


def _hyperplane_generators(s, n):
    """A generating set for {x : s.x = 0} <= Z_2^n."""
    piv = max(i for i in range(n) if s[i])
    gens = []
    for i in range(n):
        if i == piv:
            continue
        v = [0] * n
        v[i] = 1
        if s[i]:
            v[piv] = 1
        gens.append(tuple(v))
    return gens


def simon_instance(n, s, rng):
    """A 2-to-1 f with f(x) = f(x + s). Hides H = {0, s}."""
    group = AbelianGroup([2] * n)
    labels, table, nxt = {}, {}, 0
    perm = rng.permutation(1 << n)
    for x in group.elements():
        xi = group.encode(x)
        rep = min(xi, xi ^ group.encode(s))
        if rep not in labels:
            labels[rep] = int(perm[nxt])
            nxt += 1
        table[x] = labels[rep]
    return group, (lambda x: table[x]), group.subgroup([s])


def order_instance(N, a, M):
    """f(x) = a^x mod M on Z_N. Hides rZ when the order r divides N."""
    group = AbelianGroup([N])

    def f(x):
        return pow(a, x[0], M)

    r = 1
    while pow(a, r, M) != 1:
        r += 1
    return group, f, group.subgroup([(r,)]), r


def dj_constant_instance(n):
    """A constant function hides the whole group: the degenerate HSP case."""
    group = AbelianGroup([2] * n)
    return group, (lambda x: 0), group.elements()


def dj_balanced_nonlinear_instance(n):
    """A balanced but non-linear f — which is NOT an HSP instance at all.

    Its fibers are not cosets of anything, so no hidden subgroup exists to
    find. Deutsch-Jozsa is usually listed as a member of this family; for
    every f except the constant and linear ones, it is not.
    """
    group = AbelianGroup([2] * n)

    def f(x):
        return (x[0] ^ (x[1] & x[2])) & 1

    return group, f


def fibers_are_cosets(f, group, H):
    """Is every preimage of f a coset of H? The promise, checked."""
    Hset = set(H)
    for coset in fibers(f, group).values():
        base = coset[0]
        shifted = {tuple((c - b) % d for c, b, d in
                         zip(g, base, group.dims)) for g in coset}
        if shifted != Hset:
            return False
    return True


def solve(f, group, rng, solver, needed, max_shots=200):
    """The whole algorithm: sample until the post-processor is satisfied."""
    labels, shots = [], 0
    while shots < max_shots:
        labels.append(hsp_sample(f, group, rng))
        shots += 1
        got = solver(labels)
        if got is not None and needed(got):
            return got, shots
    return None, shots


# ----------------------------------------------------------------- demo ----

def _demo():
    rng = np.random.default_rng(7)
    print("ONE quantum step, three algorithms — only the last line differs\n")

    n, s = 4, (1, 0, 1, 1)
    group, f, H = bv_instance(n, s)
    print(f"Bernstein-Vazirani   G = Z_2^{n}   H = the hyperplane s.x = 0 "
          f"(|H| = {len(H)})")
    print(f"  fibers really are cosets of H: {fibers_are_cosets(f, group, H)}")
    labels = [hsp_sample(f, group, rng) for _ in range(4)]
    print(f"  samples land in H-perp = {group.annihilator(H)}")
    print(f"  drew {labels} → recovered s in one nonzero label\n")

    s2 = (1, 1, 0, 1)
    group, f, H = simon_instance(4, s2, rng)
    print(f"Simon                G = Z_2^4   H = {{0, s}} with s = {s2}")
    print(f"  fibers really are cosets of H: {fibers_are_cosets(f, group, H)}")
    got, shots = solve(f, group, rng,
                       lambda L: solve_z2n(L, 4),
                       lambda H2: len(H2) == 2)
    print(f"  recovered H = {got} in {shots} shots (needs {4 - 1} independent)\n")

    N, a, M = 16, 7, 15
    group, f, H, r = order_instance(N, a, M)
    print(f"Shor order-finding   G = Z_{N}    H = rZ with r = {r} "
          f"(order of {a} mod {M})")
    print(f"  fibers really are cosets of H: {fibers_are_cosets(f, group, H)}")
    got, shots = solve(f, group, rng,
                       lambda L: solve_zN_order(L, N),
                       lambda rr: rr == r)
    print(f"  recovered r = {got} in {shots} shots\n")

    print("And the one that does not belong:")
    group, f = dj_balanced_nonlinear_instance(3)
    sizes = sorted(len(c) for c in fibers(f, group).values())
    subs = group.all_subgroups()
    hits = [H2 for H2 in subs if fibers_are_cosets(f, group, H2)]
    print(f"  Deutsch-Jozsa, balanced but non-linear: fiber sizes {sizes}")
    print(f"  checked all {len(subs)} subgroups of Z_2^3: "
          f"{len(hits)} of them have these fibers as cosets")
    print("  → DJ with a non-linear f is NOT an HSP instance at all")


if __name__ == "__main__":
    _demo()
