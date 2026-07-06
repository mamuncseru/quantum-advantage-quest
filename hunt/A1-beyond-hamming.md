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

## Pre-registration

- **Two competing hypotheses, both worked simultaneously:**
    - (H1) Obstruction theorem: for translation schemes whose covering radius
      grows faster than the decoding radius payoff, no DQI additive guarantee
      exists. Attempt: formalize the covering-radius vs semicircle tradeoff
      as an inequality over association-scheme parameters.
    - (H2) Circumvention: find a scheme (sum-rank? skew metrics? subspace
      metric?) where covering and decoding radii align well enough for a
      guarantee.
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
