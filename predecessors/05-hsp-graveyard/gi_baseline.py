"""The baseline the graph-isomorphism prize was actually competing against.

Thirty years of dihedral- and symmetric-group HSP work was motivated partly
by graph isomorphism. This file measures what a classical algorithm from
1968 already does to that problem, because "what would the classical
baseline have said" is the question this repository asks first.

Colour refinement (1-dimensional Weisfeiler-Leman): colour every vertex by
its degree, then repeatedly recolour by the multiset of neighbouring
colours until nothing changes. Two graphs with different colour multisets
are certainly not isomorphic. It is a few lines long, runs in near-linear
time, and settles essentially every graph anyone draws at random.

Where it fails is a thin, adversarial family — and even there, a second
cheap invariant walks straight through.

Run:  .venv/bin/python predecessors/05-hsp-graveyard/gi_baseline.py
"""

from __future__ import annotations

from itertools import permutations

import numpy as np


# -------------------------------------------------------- colour refinement --

def color_refine(adj, max_rounds=None):
    """Stable 1-WL colouring. adj is a symmetric 0/1 numpy array."""
    n = adj.shape[0]
    colors = np.zeros(n, dtype=int)
    max_rounds = max_rounds or n
    for _ in range(max_rounds):
        sigs = []
        for v in range(n):
            neigh = sorted(int(colors[u]) for u in np.flatnonzero(adj[v]))
            sigs.append((int(colors[v]), tuple(neigh)))
        order = {sig: i for i, sig in enumerate(sorted(set(sigs)))}
        new = np.array([order[s] for s in sigs], dtype=int)
        if len(set(new.tolist())) == len(set(colors.tolist())):
            return new
        colors = new
    return colors


def color_signature(adj):
    """The multiset of stable colour-class sizes.

    Useful as a summary, but NOT sufficient to compare two graphs: two
    graphs that both refine to all-singleton classes have the identical
    signature (1,1,1,...) whether or not they are isomorphic. Comparing
    graphs needs `wl1_distinguishes` below.
    """
    c = color_refine(adj)
    counts = {}
    for x in c.tolist():
        counts[x] = counts.get(x, 0) + 1
    return tuple(sorted(counts.values()))


def wl1_distinguishes(a, b):
    """Does 1-WL prove these two graphs non-isomorphic?

    Refine the *disjoint union*, so that a colour means the same thing on
    both sides, then compare the colour multiset of each half. Running the
    refinement separately and comparing class sizes is a classic mistake: it
    reports "cannot distinguish" for every pair of graphs that refine to
    singletons, which is almost all of them.
    """
    n1, n2 = a.shape[0], b.shape[0]
    if n1 != n2 or int(a.sum()) != int(b.sum()):
        return True
    union = np.zeros((n1 + n2, n1 + n2), dtype=int)
    union[:n1, :n1] = a
    union[n1:, n1:] = b
    c = color_refine(union)
    return sorted(c[:n1].tolist()) != sorted(c[n1:].tolist())


def discrete_colouring(adj):
    """True when every vertex ends up its own colour — the graph is then
    settled outright: the colouring *is* a canonical labelling."""
    return len(set(color_refine(adj).tolist())) == adj.shape[0]


# ----------------------------------------------------- random instances -----

def random_graph(n, p, rng):
    a = (rng.random((n, n)) < p).astype(int)
    a = np.triu(a, 1)
    return a + a.T


def permute(adj, perm):
    return adj[np.ix_(perm, perm)]


def random_pair_stats(n, trials, rng, p=0.5):
    """On random graphs, how often does 1-WL settle the question?

    Two measurements: how often a random *non-isomorphic* pair is separated,
    and how often a single random graph is refined all the way to a discrete
    colouring (which means the isomorphism question for it is already over).
    """
    separated = discrete = 0
    for _ in range(trials):
        a = random_graph(n, p, rng)
        b = random_graph(n, p, rng)
        if wl1_distinguishes(a, b):
            separated += 1
        if discrete_colouring(a):
            discrete += 1
    return separated / trials, discrete / trials


def isomorphic_pairs_are_never_separated(n, trials, rng, p=0.5):
    """Sanity: 1-WL must never 'separate' a graph from a relabelling of itself.

    A one-sided test is only useful if it has no false positives, and this
    checks that rather than assuming it.
    """
    for _ in range(trials):
        a = random_graph(n, p, rng)
        perm = rng.permutation(n)
        if wl1_distinguishes(a, permute(a, perm)):
            return False
    return True


# ------------------------------------------- the family where it breaks -----

def rooks_graph():
    """4x4 rook's graph: vertices of a grid, joined along rows and columns.

    Strongly regular with parameters (16, 6, 2, 2).
    """
    n = 16
    a = np.zeros((n, n), dtype=int)
    for i in range(4):
        for j in range(4):
            for k in range(4):
                for l in range(4):
                    if (i, j) == (k, l):
                        continue
                    if i == k or j == l:
                        a[4 * i + j, 4 * k + l] = 1
    return a


def shrikhande_graph():
    """The Shrikhande graph: same parameters (16, 6, 2, 2), different graph.

    Vertices Z_4 x Z_4, joined when the difference is +-(0,1), +-(1,0) or
    +-(1,1). It and the rook's graph are the standard smallest example of two
    non-isomorphic graphs that colour refinement cannot tell apart.
    """
    n = 16
    diffs = {(0, 1), (0, 3), (1, 0), (3, 0), (1, 1), (3, 3)}
    a = np.zeros((n, n), dtype=int)
    for i in range(4):
        for j in range(4):
            for k in range(4):
                for l in range(4):
                    if ((k - i) % 4, (l - j) % 4) in diffs:
                        a[4 * i + j, 4 * k + l] = 1
    return a


def is_strongly_regular(adj):
    """Check (n, k, lambda, mu) regularity — returns the parameters or None."""
    n = adj.shape[0]
    degs = adj.sum(axis=1)
    if len(set(degs.tolist())) != 1:
        return None
    k = int(degs[0])
    lam = mu = None
    for u in range(n):
        for v in range(n):
            if u == v:
                continue
            common = int(adj[u] @ adj[v])
            if adj[u, v]:
                if lam is None:
                    lam = common
                elif lam != common:
                    return None
            else:
                if mu is None:
                    mu = common
                elif mu != common:
                    return None
    return (n, k, lam, mu)


def neighbourhood_signature(adj):
    """For each vertex, the shape of the graph induced on its neighbours.

    The two-line invariant that walks past the hard case: in the rook's
    graph every neighbourhood is two disjoint triangles; in the Shrikhande
    graph every neighbourhood is a single 6-cycle. Both are 6 vertices and 6
    edges, so no counting argument sees it — but the *connectivity* does.
    """
    sigs = []
    for v in range(adj.shape[0]):
        nb = np.flatnonzero(adj[v])
        sub = adj[np.ix_(nb, nb)]
        sigs.append(tuple(sorted(_component_sizes(sub))))
    return tuple(sorted(set(sigs)))


def _component_sizes(adj):
    n = adj.shape[0]
    seen, out = set(), []
    for v in range(n):
        if v in seen:
            continue
        stack, size = [v], 0
        seen.add(v)
        while stack:
            u = stack.pop()
            size += 1
            for w in np.flatnonzero(adj[u]):
                if w not in seen:
                    seen.add(int(w))
                    stack.append(int(w))
        out.append(size)
    return out


def brute_force_isomorphic(a, b, limit=9):
    """Exhaustive check, for graphs small enough to justify it."""
    n = a.shape[0]
    assert n <= limit, "exponential; only for tiny graphs"
    for perm in permutations(range(n)):
        if np.array_equal(permute(a, np.array(perm)), b):
            return True
    return False


def automorphism_count(adj, limit=8):
    """|Aut(G)| by brute force — the object the HSP reduction hides."""
    n = adj.shape[0]
    assert n <= limit
    return sum(1 for p in permutations(range(n))
               if np.array_equal(permute(adj, np.array(p)), adj))


# ----------------------------------------------------------------- demo -----

def _demo():
    rng = np.random.default_rng(11)
    print("COLOUR REFINEMENT (1-WL, 1968) on random graphs\n")
    print(f"  {'n':>4} {'non-isomorphic pairs separated':>32} "
          f"{'graphs settled outright':>26}")
    for n in (8, 12, 20, 40, 80):
        sep, disc = random_pair_stats(n, 60, rng)
        print(f"  {n:>4} {sep:>31.1%} {disc:>25.1%}")
    print("\n  no false positives (a graph is never separated from a "
          "relabelling of itself):",
          isomorphic_pairs_are_never_separated(20, 40, rng))

    print("\n" + "-" * 68)
    print("WHERE IT FAILS — and how thin that family is\n")
    rook, shri = rooks_graph(), shrikhande_graph()
    print(f"  rook's graph      strongly regular {is_strongly_regular(rook)}")
    print(f"  Shrikhande graph  strongly regular {is_strongly_regular(shri)}")
    print(f"  1-WL separates them?  {wl1_distinguishes(rook, shri)}  "
          f"→ colour refinement is blind here")
    print(f"  every vertex gets the same colour: "
          f"{len(set(color_refine(rook).tolist())) == 1}")
    print("\n  but one more cheap invariant separates them instantly:")
    print(f"    rook's neighbourhoods      {neighbourhood_signature(rook)} "
          f"→ two disjoint triangles")
    print(f"    Shrikhande neighbourhoods  {neighbourhood_signature(shri)} "
          f"→ one 6-cycle")
    print(f"    distinguished: "
          f"{neighbourhood_signature(rook) != neighbourhood_signature(shri)}")

    print("\n" + "-" * 68)
    print("WHAT THE HSP REDUCTION WAS HIDING\n")
    for name, g in [("path on 6", _path(6)), ("cycle on 6", _cycle(6)),
                    ("complete on 6", _complete(6))]:
        print(f"  |Aut({name})| = {automorphism_count(g)}")
    print("\n  graph isomorphism reduces to finding the automorphism group,")
    print("  which is a hidden subgroup of S_n. That reduction is correct —")
    print("  and it aims a thirty-year quantum programme at a problem whose")
    print("  random instances a 1968 heuristic finishes in near-linear time.")


def _path(n):
    a = np.zeros((n, n), dtype=int)
    for i in range(n - 1):
        a[i, i + 1] = a[i + 1, i] = 1
    return a


def _cycle(n):
    a = _path(n)
    a[0, n - 1] = a[n - 1, 0] = 1
    return a


def _complete(n):
    return np.ones((n, n), dtype=int) - np.eye(n, dtype=int)


if __name__ == "__main__":
    _demo()
