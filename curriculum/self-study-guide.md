# Self-study guide — running the curriculum without the AI

Written 2026-07-06, when it became clear AI access would be limited after
July 7. Everything needed for Phase 1 (ARM) is in this repo and tested.
The 6-month clock and the ROADMAP gates are unchanged.

## Daily protocol

1. **One autopsy at a time**, in numbered order. Read `notes.md` with the
   original paper open (references are in each file). Sections 1–4 are
   teaching; section 5 is YOURS — write it, always, in your own words.
2. **Run and read the code.** Every implementation is deliberately short
   and framework-free; read until every line is obvious, run the demos,
   run `pytest` on the directory. Break something on purpose; predict the
   failure before running.
3. **Proof drafts before solutions.** Draft completely on paper, then grade
   yourself against `curriculum/solutions.md` including the "common holes."
   The six-point self-attack checklist at the bottom of that file applies
   to every proof you ever write in this program — including the hunt phase,
   where it is the difference between a result and an embarrassment.
4. After each autopsy: add/edit the corresponding row of
   `frontier/problem-shapes.md`. The catalog must end up in YOUR voice.

## Pacing (full-time, gate = 2026-08-06, hard)

- Days 1–3: 01–02 (DJ, BV) + Simon (03). The three proof drafts (#0, #1).
- Days 4–8: Shor (04) — the centerpiece; give it real time — then HSP
  graveyard (05). Proof draft #2. Skim Kuperberg.
- Days 9–12: Grover (06) + walks (07). Proof draft #3 (BBBV).
- Days 13–17: Hamiltonian simulation (08) + QSVT (09) + HHL/Tang (10).
- Days 18–24: the hunting grounds (11, 12) at proof level, with
  `frontier/lit-sweep-2026H1.md` and the primary papers side by side.
  These two autopsies are the transition into Phase 2 — their "hunt-phase
  question" exercises are the first hunt documents.
- Days 25–30: rewrite `frontier/problem-shapes.md` end to end; check the
  ROADMAP Phase-1 gate boxes honestly; write a one-page gate review.

## Verification duties (things the AI could not verify from its cutoff)

The DQI and Gibbs autopsies cite 2026 papers found by a search agent —
sound methodology, but per our rules nothing enters the hunt unverified:

- [ ] Confirm the arXiv IDs and claims in `frontier/lit-sweep-2026H1.md`
      for every paper you'll build on (especially the items flagged
      "snippet-level").
- [ ] Verify at proof level: DQI 2408.08292 (semicircle law + OPI regime),
      CKG 2311.09207 (detailed balance construction), Rajakumar–Watson
      2408.01516, Bakshi–Tan (ID per sweep).

## When you have AI access again (any model, including cheaper ones)

- This repo is self-describing: README → ROADMAP → curriculum → autopsies.
  Point the model at those, in that order.
- Use the model as attacker, not oracle: "here is my proof draft, break it"
  extracts far more value per token than "explain X to me."

## Working environment

`source .venv/bin/activate`; run everything from the repo root.
`pytest --ignore=predecessors/02-bernstein-vazirani` is green (your BV
homework is the one red suite until you make it pass).
GPU/big-CPU nodes are NOT needed for Phase 1; they enter in Phase 2
(scaling numerics) — budget them then.
