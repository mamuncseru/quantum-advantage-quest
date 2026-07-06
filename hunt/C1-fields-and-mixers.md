# C1 — Field-induced hardness with rapid quantum mixing

**Pre-registered 2026-07-06.** Built on the *verified* Bakshi–Tan result
(arXiv 2604.08408): (i) on-site fields induce entanglement in high-temperature
Gibbs states past $h \approx \beta^{-1}\log(1/\beta)$; (ii) a quasi-local
Lindbladian mixes in $O(\log(n/\varepsilon))$ under arbitrary on-site fields;
(iii) classical hardness of computational-basis sampling for $\beta < 1$ with
sufficiently large fields.

## The question

Their mechanism lives at **high temperature** ($\beta < 1$) — the same regime
where, without fields, everything is provably classically easy. The seam:

> **Which other physically natural knobs induce classical hardness while
> preserving provable quantum rapid mixing — and can any push the mechanism
> into the intermediate-$\beta$ regime where no easiness results wait to
> squeeze it?**

Candidate knobs, in priority order:

1. **Quasi-periodic fields** (Aubry–André-type) — breaks translation
   invariance in a structured way; classical cluster expansions and
   transfer-matrix methods degrade differently than under random fields.
2. **Weak non-commuting perturbation of a classically hard commuting model**
   — start where classical hardness is known (commuting case) and ask how
   much non-commutativity the quantum mixer tolerates before its gap closes.
3. **Field gradients / boundary-driven profiles** — hardness from
   inhomogeneity rather than strength.

## What we can compute (and nobody has published)

Small-system exact numerics as *conjecture-formers*, on the 96-core node:

- Davies/CKG-style generator spectral gap vs $(h, \beta)$ for each knob at
  $n \le 7$ (superoperator $4^n{\times}4^n$ exact diagonalization — our
  `predecessors/12` machinery scales to this).
- The classical side: convergence radius of the high-temperature cluster
  expansion vs the same knobs — locating where the classical certificate
  *fails* (necessary-but-not-sufficient signal for hardness).
- The map of (quantum gap open) ∧ (classical certificate broken) — the
  candidate advantage region, to be attacked by proof afterwards.

## Pre-registration

- **Advantage currency:** conditional sampling hardness (PH-style, matching
  Rajakumar–Watson / Bakshi–Tan tier) + provable quantum mixing for a *named
  family*.
- **Hardness mechanism:** inherited from the commuting/large-field hardness
  results — never "we couldn't simulate it"; numerics only *locate*
  candidates, proofs decide.
- **Named classical baselines:** high-temperature cluster expansion
  (Bakshi–Liu–Moitra–Tang line), tensor-network contraction at small $\beta$,
  and — access-model symmetry — any classical sampler given the same explicit
  Hamiltonian description.
- **Kill criteria:**
    1. For every knob: quantum gap closes wherever the classical certificate
       breaks (numerics at $n \le 7$, then perturbative argument) → kill knob.
    2. All three knobs killed → kill candidate; deliverable = the numerical
       atlas of gap-vs-certificate, which is a useful negative result.
    3. Deadline for the numerical atlas: 4 weeks of compute time.
- **Honesty constraint:** small-$n$ numerics never headline; they select the
  one family that gets the proof effort.

## First actions

1. Human: proof-level pass through Bakshi–Tan's Lindbladian construction and
   the hardness argument (which step needs $\beta < 1$? that step is the wall
   we probe).
2. Extend `predecessors/12-gibbs-lindblad/davies.py` to sweep $(h,\beta)$
   for knob 1 at $n = 4,5,6$; produce the first gap map.
3. Implement the cluster-expansion convergence check (classical certificate).
