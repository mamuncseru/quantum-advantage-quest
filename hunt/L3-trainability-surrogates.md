# L3 — Trainability vs surrogatability on quantum data

**Pre-registered 2026-07-11**, ground L, third candidate. The
barren-plateau question, access-model-symmetrized — the author's home
field (HilbertBench diagnoses exactly these landscapes).

## The frontier as published

[Cerezo et al., Nat. Comm. 16, 7907 (2025)](https://arxiv.org/abs/2312.09121):
case-by-case evidence that provably BP-free landscapes admit classical
surrogates after a poly data-acquisition phase — because known
trainability mechanisms confine dynamics to poly-sized subspaces
(poly-DLA ⇒ $\mathfrak{g}$-sim; shallow + local cost ⇒ lightcones). The
paper's own caveat list (smart initializations, models outside the
assumptions) is the open boundary. Graveyard compliance: we do **not**
hunt variational speedups on classical data; the seam is **quantum input
data** with access-model symmetry — the classical surrogate gets
single-copy (shadow) access to the same input states, never less.

## The mechanism under test: memory-measurable losses

Losses that *require quantum memory to estimate*:
$L_k(\theta) = \mathrm{Tr}[\rho_A(\theta)^2]$, the purity of a $k$-qubit
marginal of the trial state — measurable with two copies and a local swap
test at $O(1/\varepsilon^2)$ shots for any $k$, while single-copy shadow
estimation pays $\sim 2^{\Theta(k)}$. If such a loss is *trainable*, a
shadow-bound surrogate cannot follow the optimizer.

**First numerics** ([`code/swap_loss_bp.py`](code/swap_loss_bp.py),
tests; shallow depth-2 HEA, $n = k+3$, $k \le 5$):

| measured rate | bits per unit $k$ |
|---|---|
| training cost $1/\mathrm{Var}[\partial_\theta L_k]$ | **0.36** |
| naive shadow surrogate cost | **1.65** |
| two-copy loss estimation | 0 (flat) |

Gradients do *not* decay at the shadow rate — at face value the window is
open. **Self-attack finding (same session, load-bearing):** at this depth
with a *known* input, the trial state is a bond-dimension-4 MPS, so the
true best surrogate is polynomial — the naive-shadow column is a strawman
for that setting. The honest live formulation is therefore:

> **The L3 question.** For variational tasks on **unknown quantum input
> data** (where any surrogate must reconstruct $(k{+}O(1))$-qubit
> marginals from single-copy access — genuinely $2^{\Theta(k)}$), with
> mesoscopic memory-measurable losses ($k \sim \omega(\log n)$): does the
> measured rate gap (0.36 vs 1.65 bits/$k$) persist, giving a **trainable
> but non-surrogatable** region — the first rigorous escape from the
> trainability ⇒ simulability implication? Or do the rates merge as
> $k, n$ grow (the implication wins again)?

Note the L1 kinship: the surrogate's bottleneck is single-copy purity
estimation — L1's exponential-vs-flat table is literally the surrogate's
lower-bound evidence.

## Pre-registration

- **Advantage currency:** a provable trainable-not-surrogatable family
  (conditional lower bounds acceptable if standard), or the sharpened
  implication theorem covering memory-measurable losses — either extends
  the Cerezo et al. map, on the quantum-data side they flag as open.
- **Kill criteria:**
    1. **Rate merge:** gradient variance at fixed relative $k/n$, deeper
       ansätze, decays at $\ge$ the surrogate rate (the 0.36 was a
       shallow-depth finite-size artifact) → implication wins, write the
       boundary note.
    2. **Smarter surrogate:** a single-copy protocol estimating
       $\mathrm{Tr}[\rho_A^2]$-type losses at poly cost for the relevant
       ensembles (would also bite L1 — shared kill).
    3. **Lit pass:** the escape already constructed or refuted in the
       2025–26 wave around the Cerezo conjecture → fold.
- **Access honesty:** surrogate always gets shadows of the same quantum
  inputs plus full classical compute; quantum learner's memory advantage
  must be the *only* asymmetry.

## Kill-1 first data (2026-07-11, same day)

Rate-persistence scan in the proportional regime $n = 2k$
([`code/rate_persistence.py`](code/rate_persistence.py)): the training
rate **rises with depth** — 0.13 / 0.28 / 0.36 bits per $k$ at depths
2 / 4 / 6 — trending toward the surrogate rate (1.65) but still $4.5\times$
below it at depth 6. Kill 1 has not fired; the narrowing trend is the
honest headline. The window, if real, lives at *shallow-to-moderate*
depth — which is also where ansätze are expressive enough to be useful,
so the tension is genuine and undecided. Next: deeper + larger $n$ on a
compute node, and gradient *signal* (not just variance) along optimization
trajectories.

## First actions

1. Rate-persistence scan: depth and $k/n$ scaling of
   $\mathrm{Var}[\partial L_k]$ — first pass done (above); extend to
   $n \le 14$ and optimization trajectories on a compute node.
2. Formalize the surrogate lower bound via the L1 machinery
   (single-copy purity estimation on the induced ensemble).
3. Deep lit pass on post-2025 counterexample attempts.
