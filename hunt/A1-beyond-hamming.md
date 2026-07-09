# A1 — DQI beyond Hamming: the covering-radius obstruction

**Pre-registered 2026-07-06.** Recast after verification: the rank-metric DQI
authors (arXiv 2606.04843) **disclaim advantage** — their own covering-radius
obstruction means the semicircle-type bound does not translate into an
additive guarantee on the true optimum in rank metric. So the honest open
problem is not "stress-test their claim" but:

> **Is the covering-radius obstruction intrinsic to non-Hamming DQI, or a
> feature of the rank-metric instance they chose?**

## Why it matters

If the obstruction is *intrinsic*, that is a theorem about where DQI's magic
lives (Hamming-type weight distributions), and it sharpens A2's search space
for free. If it is *instance-specific*, there exists a beyond-Hamming metric
where DQI gives real guarantees — a new advantage family. Either resolution
is a result.

## Update 2026-07-06 — pages 1–6 of 2606.04843 read directly

Their framework: DQI generalizes to any **P-polynomial translation
association scheme** — shells around a basepoint, shell Dicke states, and a
tridiagonal Jacobi matrix governing the interference (rank metric: radial
eigenvalues are q-Krawtchouk polynomials). The obstruction, precisely: for
**nearest-codeword (distance-minimization) objectives**, DQI's guarantee is a
bound on a *proxy* (effective rank near $\min(m,n)-\ell$), while the true
optimum sits at typical target-to-code distance (≈ covering radius) — and
Gabidulin's efficient decoding radius can be smaller than that, so the proxy
bound implies no additive guarantee versus the optimum.

**The sharpening this forces:** the obstruction is a property of the
*objective type*, not (only) the metric. Hamming max-LinSAT never needed a
covering radius because its objective **counts satisfied constraints** — the
semicircle law bounds the objective absolutely. Rank distance is not
coordinate-decomposable, so no counting objective exists there — which is
*why* that paper had to use nearest-codeword form.

## Pre-registration (hypotheses sharpened after the read)

- **H2′ is DEAD (2026-07-08).** The Lee-metric circumvention failed at its
  first gate — Lee is not an association scheme for $q\ge5$, so the "counting
  objective in a coordinate-decomposable metric" idea has no P-polynomial
  home ([kill note](notes/AC-lee-metric-KILLED.md)). Sum-rank inherits the
  same covering-radius obstruction as rank. Only H1′ remains.
  **Upgrade (same day, second session):** the closure is now *total* — a
  Cartesian product of connected graphs is distance-regular iff Hamming or
  Doob ([product theorem](notes/A3-product-theorem.md)), so the H2′ search
  space holds exactly one non-Hamming point, the Doob scheme, which *does*
  support a counting objective and moved to A3 as a live candidate.
- **H1′ (now the whole candidate) — the obstruction theorem:** for ANY
  distance-minimization objective in a P-polynomial scheme where efficient
  decoding radius < typical target-to-code distance, no DQI additive
  guarantee exists. This is a clean, honest **negative** theorem target
  (not a new-advantage target): it would explain the rank-metric authors'
  disclaimer at full generality and delimit where shape #10 can pay off.
- **Convergence note:** A2's open problem Q(A2.1) — closest CRT-sparse
  integer under *size* noise — is itself Lee/archimedean-metric decoding.
  If H2′ produces Lee-metric DQI machinery, it feeds A2 directly. The two
  candidates now share a spine: **DQI for coordinate-decomposable non-Hamming
  geometries.**
- **Classical baseline (if H2 produces a candidate):** rank/sum-rank ISD
  (Gaborit-line algorithms) implemented at symmetric effort, plus the
  enhanced-Prange playbook from 2604.24633.
- **Kill criteria:**
    1. H1 proven → candidate *completes* (negative result, write it).
    2. Four weeks with neither an H1 proof sketch nor an H2 candidate scheme
       → park as "open, not ours," document the partial map.
- **Dependency:** human proof-level pass through 2606.04843 §(obstruction) —
  scheduled into Phase 1 week 5 reading.

## First actions

1. Human reads 2606.04843 at proof level; extract the exact form of the
   obstruction (what quantity outruns what).
2. Tabulate covering radius vs half-distance for the standard translation
   schemes (Hamming, rank, sum-rank, subspace) — where is the gap smallest?
3. Decide H1-vs-H2 emphasis from that table.
