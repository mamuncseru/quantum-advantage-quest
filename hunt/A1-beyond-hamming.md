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

- **Two competing hypotheses, both worked simultaneously:**
    - (H1′) Obstruction theorem: for ANY distance-minimization objective in a
      scheme where efficient decoding radius < typical target-to-code
      distance, no DQI additive guarantee exists. (Likely provable at
      scheme-parameter generality; would subsume their appendix as the
      special case.)
    - (H2′) Circumvention by objective type: pick **coordinate-decomposable
      non-Hamming metrics** — Lee metric over $\mathbb{Z}_q$ first, block
      sum-rank second — where counting objectives (max-LinSAT with target
      sets) exist and the semicircle-type guarantee is absolute. Needs:
      P-polynomiality of the Lee scheme (classical, known), Lee-metric codes
      with efficient decoders (exist — negacyclic/BCH-type constructions),
      and the Jacobi analysis transplanted.
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
