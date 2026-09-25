# Six-Month Roadmap (2026-07-02 → 2027-01-02)

## Phase 1 — ARM (weeks 1–5): The Predecessors

Study every named quantum algorithm as a **case study in problem-finding**, not as
a textbook topic. Working thesis of the whole program:

> Almost no named algorithm came from a new primitive. It came from a new problem.

Each algorithm gets an **autopsy** (template in `curriculum/00-curriculum.md`),
a from-scratch numpy implementation, and a distilled "problem-shape" lesson.
Concurrently: fresh literature sweep of grounds A & C (post-Jan-2026).

**Gate (end of week 5) — hard stop, no extension:**

- [ ] ≥ 10 completed autopsies in `predecessors/`
- [ ] Hand-built statevector simulator + Shor + quantum walk + Tang dequantization, all passing tests
- [ ] ≥ 3 attack exercises survived (human drafts proof, AI attacks)
- [ ] The **Problem-Shape Catalog** written (`frontier/problem-shapes.md`)
- [ ] Both of us fluent in the DQI paper and the Lindbladian-sampler papers at proof level

## Phase 2 — HUNT (weeks 6–13): Candidate generation

Problem-first search on ground A (primary) and C (secondary). Weekly kill/keep
review with pre-stated kill criteria. GPUs used for scaling numerics to *smell*
advantage before proving it.

**Gate:** 2–3 candidate results that survived our own classical attacks.

> **2026-07-06 — Phase 2 opened early**, overlapping Phase 1 study, to
> front-load AI-assisted groundwork before access constraints. What exists so
> far: primary-source verification of all six load-bearing frontier papers
> (two sweep-framing corrections found), four pre-registered candidates with
> kill criteria, and the advantage-window tool validated against the DQI
> paper's own numbers. See `hunt/README.md`.

## Phase 3 — STRIKE (weeks 14–20): The main proof

All effort on the best candidate. Rigorous proof attempt AND classical-attack
attempt run in parallel by design. Either outcome is progress.

> **2026-07-11 — Phase 3 opened early on candidate A2 (CRT-DQI).** A2's
> self-attack chain is complete (decoder = continued fractions; window
> bookkeeping lemma validated exactly at ℓ=1,2), so effort concentrates
> there ahead of schedule. Load-bearing statement:
> `strike/crt-dqi-theorem.md` — the construction as a theorem with all
> constants and the one remaining hole named (§5, shell-state
> preparation). Running in parallel by design: a dedicated adversarial
> cryptanalysis pass and the deferred human verification batch. Phase-2
> gate is met (A2 surviving + A3 closed as a publishable negative +
> seven live ground-L candidates), so this is a gate-passing transition,
> not a skip.

## Phase 4 — WRITE (weeks 21–26)

Full write-up of what survived — positive result or precise boundary. Harden
proofs, paper-grade numerics, reproducibility package.

## Side tracks (explicitly off the critical path)

> **2026-07-11 — The Machines catalog opened** (`machines/`): a field guide
> to every working quantum computer — fixed autopsy template, one sourced
> data file, skeptic's box per machine. Motivation: "runs on near-term
> devices" must never be a hand-wave in this program. Side track by
> declaration; it does not count toward any phase gate.

## Known graveyards (do not enter)

- Nonabelian hidden subgroup (dihedral → lattices)
- QML speedups on classical data
- Grover-type quadratic speedups as an end goal (fine as subroutines)

## Cautionary tales (pinned)

- 2024 claimed quantum LWE algorithm: survived 10 days, killed by a subtle bug.
  → every proof gets attacked before we believe it.
- IBM utility experiment vs. laptop tensor networks; DQI's max-XORSAT regime
  partially reclaimed classically. → advantage claims die at the weakest step.
