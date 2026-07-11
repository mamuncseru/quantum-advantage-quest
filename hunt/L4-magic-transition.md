# L4 — The magic transition in state learning

**Pre-registered 2026-07-11**, ground L, fourth candidate.

## The map as published (lit-checked first)

- $t = O(\log n)$ T-gates: Clifford+T states are learnable in poly time —
  with two-copy Bell-difference sampling
  ([GIKL, STOC 2024](https://arxiv.org/pdf/2304.13915)) *and* with
  [single-copy protocols](https://quantum-journal.org/papers/q-2024-02-12-1250/)
  — so at small $t$ there is no memory question left.
- $t = \Theta(n)$: necessary for computational pseudorandomness (GIKL,
  tight if linear-time quantum-secure PRFs exist) — above this wall,
  learning is cryptographically hard.
- GIKL's stabilizer-fidelity witness runs in poly *samples* but
  $\exp(O(n/\tau^4))$ *time* — sample-easy, compute-hard, already at
  moderate stabilizer fidelity.

> **The candidate question: the open middle strip.** For
> $\omega(\log n) \le t \le o(n)$, learning $t$-doped states is
> sample-efficient and not pseudorandom — **where in the strip does
> computational learnability actually die**, and does quantum memory
> shift the boundary (Bell-difference methods are inherently two-copy)?

Graveyard compliance: quantum data (the states), provable currency
(upper bounds constructive, lower bounds cryptographic), no classical-data
speedup claims anywhere.

## First numerics (this session)

The cost of every Bell-difference learner is governed by the collision
mass $2^n\sum_a p_\psi(a)^2 = 2^{-M_2}$ of the characteristic
distribution ($M_2$ = stabilizer 2-Rényi entropy). Computed exactly
($n = 6$, all $4^n$ Weyl expectations, 16 circuits/point,
[`code/magic_transition.py`](code/magic_transition.py)): the mass decays
at a measured per-T-gate rate (~0.1 bits/T with random placement —
random T's partially cancel since $T^2 = S$; the ideal-placement rate is
higher), making the cost curve $\text{poly} \cdot 2^{\Theta(t)}$
concrete: polynomial at $t = O(\log n)$, superpolynomial in the strip.

## Pre-registration

- **Advantage/deliverable currency:** locate the transition — either a
  poly learner beyond $O(\log n)$ T-gates (would be a major algorithmic
  result), or hardness evidence pushing the wall down from $\Theta(n)$
  (low-degree/statistical-query lower bounds in the strip), or a proven
  memory separation *inside* the strip. Any of the three redraws the map.
- **Kill criteria:**
    1. Deep lit pass: the strip may already be closing (2025–26 wave:
       qudit Bell sampling [2510.06848](https://arxiv.org/pdf/2510.06848),
       STOC 2026 stabilizer-structure learning) — verify before investing.
    2. If single-copy and two-copy provably match throughout the strip
       (no memory axis) *and* the computational boundary is
       crypto-blocked from both sides → park as "well-posed, not ours."
    3. Two reviews without a new foothold → park.
- **First actions:** deep lit pass; formulate the strip's simplest
  concrete instance ($t = n^{1/2}$, say) as a target; check whether the
  L2 unknown-frame suspect reduces to it (frame-finding *is* stabilizer
  structure learning — the candidates may merge).
