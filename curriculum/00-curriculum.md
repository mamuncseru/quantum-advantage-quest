# The Predecessors — a 5-week study of every named quantum algorithm

> **2026-07-06 update:** all session material (autopsies 01–13, tested
> implementations, solution sketches, the Problem-Shape Catalog draft) was
> delivered up front because AI access becomes limited after July 7.
> The session plan below remains the study ORDER; the delivery is complete.
> Start from `curriculum/self-study-guide.md`.

Not a course. A training program in **problem-finding**, taught through autopsies
of the algorithms that made it. Format per session: AI teaches interactively
(derivations, history, context) → human works the exercises (proof drafts,
implementations) → AI attacks the drafts. Read the *original* papers, not surveys;
the AI guides through them.

Cadence: ~3 teaching sessions/week; the rest of full-time goes to exercises,
implementations, and original papers. **Hard stop end of week 5** — studying is
comfortable, hunting is not; the gate forces the jump.

---

## The Autopsy Template (applied to every algorithm)

1. **The problem** — what is it, and who cared about it *before* quantum computing?
2. **The classical wall** — what was the classical state of the art, and what
   structural feature blocked further progress?
3. **The primitive** — which quantum mechanism exploits that structure, and how
   exactly does interference/measurement extract the answer?
4. **The hardness evidence** — why do we believe no classical algorithm matches it?
   What happened when classical algorithms fought back (dequantizations, caveats)?
5. **The lesson** — what *shape* of problem does this pattern want? (Feeds the
   Problem-Shape Catalog.)

Autopsies live in `predecessors/<nn>-<name>/notes.md`; implementations beside them.

---

## Week 1 — Interference and the birth of structure

**Session 1.** Rules of the game at speed (states, unitaries, measurement, oracles —
refresher, you know this). Then Deutsch–Jozsa (1992) and Bernstein–Vazirani (1993):
the toys that proved interference computes global properties.
*Code:* build our own numpy statevector simulator (~100 lines). Everything later
runs on it — no framework black boxes during the curriculum.
*Autopsies 1–2.*

**Session 2.** Simon (1994): hidden XOR-mask, the first exponential separation,
and the direct provocation for Shor.
*Exercise (attack #1):* you draft the classical query lower bound (birthday-style
argument); I attack the draft.
*Autopsy 3.*

*(Parallel, AI: literature sweep Jan–Jul 2026 for grounds A & C → `frontier/`.)*

## Week 2 — Shor week: the masterclass in problem-first thinking

**Session 3.** The reduction, no quantum anywhere: factoring → order finding.
Pure number theory. *Exercise:* you draft the reduction proof; I attack.

**Session 4.** QFT, phase estimation, continued fractions.
*Code:* full Shor on our simulator; factor 15, 21, 35. Watch where the exponential
cost actually goes (modular exponentiation), not where folklore says it goes.

**Session 5.** The lineage forward and the first graveyard: abelian HSP solved in
general; nonabelian HSP (graph iso; dihedral → lattices) resisted 30 years,
Kuperberg's subexponential sieve as best-known. **Lesson: where structure ends,
speedup ends.**
*Autopsies 4–5.*

## Week 3 — The workhorses: amplification and walks

**Session 6.** Grover (1996) → amplitude amplification → amplitude estimation
(BHMT). Then the ceiling: BBBV lower bound — *why* unstructured search caps at
quadratic (Aaronson–Ambainis: no structure ⇒ no superpolynomial speedup; this is
why our hunt lives in structured territory only).
*Exercise (attack #2):* you draft the hybrid-argument lower bound; I attack.
*Autopsy 6.*

**Session 7.** Quantum walks: glued trees (exponential hitting-time separation —
the *only* exponential speedup not based on the QFT), Szegedy walks and the
√(spectral gap) rule. Bridge to ground C.
*Code:* glued-trees walk on the simulator; reproduce the exponential separation
numerically.
*Autopsies 7–8.*

## Week 4 — The modern engine room

**Session 8.** Hamiltonian simulation: Trotter (Lloyd 1996) → LCU → qubitization.
The physics-native lineage and why it resists dequantization.
*Autopsy 9.*

**Session 9.** QSVT (Gilyén–Su–Low–Wiebe 2019): the grand unification.
*Exercise:* recover Grover and phase estimation as QSVT special cases.
*Autopsy 10.*

**Session 10.** The cautionary lineage: HHL (2009), Aaronson's fine print, and
Tang 2018.
*Code (attack #3):* implement Tang-style ℓ²-sampling dequantization of low-rank
recommendation — feel, in code, exactly how an advantage dies when the problem's
structure is secretly classical too. Red-team training.
*Autopsy 11.*

## Week 5 — Our hunting grounds, at proof level

*Required companion reading for this week: `frontier/lit-sweep-2026H1.md` —
the Jan–Jul 2026 state of both grounds. Sessions 11–12 teach the anchor papers;
the sweep tells you what happened to them this year.*

**Session 11.** DQI (Jordan et al. 2024) deep dive: max-LinSAT → decoding,
Optimal Polynomial Intersection, which regimes classical algorithms reclaimed and
why. *Exercise:* you re-derive the core reduction; I attack.
*Autopsy 12.*

**Session 12.** Classical MCMC refresher (Metropolis, spectral gaps, mixing times —
must be solid) → quantum Metropolis (Temme et al. 2011) → Davies generators →
Lindbladian samplers (Chen–Kastoryano–Gilyén line). Where mixing-time advantage
could provably live.
*Autopsy 13.*

**Session 13 — Synthesis & gate review.** Write `frontier/problem-shapes.md`
together: the distilled catalog (hidden periodicity → QFT; spectral gap → walks;
decoding structure → DQI; local Hamiltonian / Gibbs → dissipative; low-rank +
sampling access → classically dead; unstructured → quadratic ceiling; …).
Check the Phase-1 gate. **GO for the hunt.**

---

## Side quest (30 min/week, weeks 3–5)

The advantage bestiary beyond time complexity: shallow-circuit separations (BGK),
learning with quantum memory (Chen–Cotler–Huang–Li), communication complexity.
Advantage has more than one currency — sample, space, depth, communication all
count, and "Abdullah's algorithm" may be denominated in any of them.
