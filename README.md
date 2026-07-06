# Quantum Advantage Quest

**A problem-first expedition toward genuine quantum advantage — run fully in
the open.**

> Almost no named quantum algorithm came from a new primitive.
> It came from a new problem.

This repository is a live research program, not a finished textbook. The goal
is stated plainly: design a quantum algorithm with theoretically validated
advantage — Shor-tier currency: a rigorous algorithm plus classical hardness
under a well-studied assumption — and document every step, including the
failures, so anyone can learn from the journey.

**Website:** https://mamuncseru.github.io/quantum-advantage-quest/
**Sibling project:** [HilbertBench](https://github.com/mamuncseru/hilbertbench) —
diagnostics for quantum ML experiments. The Bench diagnoses; the Quest hunts.

## Why this exists

Most published "quantum advantage" claims die the same death: someone takes
the classical baseline seriously. This program is built on the opposite
reflex — attack your own results before anyone else can:

1. **Symmetric effort.** Every claimed quantum advantage gets attacked with
   the strongest classical tools we can build, before anyone else sees it.
2. **Hardness needs a mechanism.** Only problems whose classical difficulty
   has structural evidence (algebraic, spectral, coding-theoretic) — never
   "we couldn't simulate it."
3. **Pre-registered criteria.** Advantage type and kill criterion are written
   down before an investigation starts.
4. **Negative results are deliverables.** A precise boundary and why the
   advantage dies there is a result, written up with full care.
5. **Every proof gets attacked before it gets believed.**

## What's inside

- **[The Predecessors curriculum](curriculum/00-curriculum.md)** — every
  named quantum algorithm studied as a case study in *problem-finding*, via
  a fixed five-question "autopsy" template. Thirteen autopsies from
  Deutsch–Jozsa to Decoded Quantum Interferometry and quantum Gibbs sampling.
- **[Working code](qsim/__init__.py)** — a hand-built statevector simulator
  (no framework black boxes) and from-scratch, tested implementations:
  Shor factoring 35 on 19 simulated qubits, the glued-trees exponential walk
  separation, a Davies-generator Gibbs sampler, Tang-style dequantization,
  QSVT's Chebyshev identity, and more. `pytest` runs them all.
- **[Solutions & self-attack checklists](curriculum/solutions.md)** — proof
  sketches with the "common holes" that break naive drafts.
- **[The Problem-Shape Catalog](frontier/problem-shapes.md)** — the
  distillation: which problem structures map to which quantum mechanisms,
  what kills each one, and where the live frontier is.
- **[Roadmap](ROADMAP.md)** — the six-month arc: ARM → HUNT → STRIKE → WRITE,
  with hard phase gates.

## Quickstart

```bash
git clone https://github.com/mamuncseru/quantum-advantage-quest
cd quantum-advantage-quest
python3 -m venv .venv && source .venv/bin/activate
pip install numpy scipy sympy matplotlib pytest
pytest --ignore=predecessors/02-bernstein-vazirani   # 02 is your exercise
```

Then start reading at [the curriculum](curriculum/00-curriculum.md), or follow
the [self-study guide](curriculum/self-study-guide.md).

## Status

Phase 1 (ARM) in progress — curriculum complete, gate review due early
August 2026. The hunt directives for Phase 2 live at the bottom of the
[Problem-Shape Catalog](frontier/problem-shapes.md).

## License

[MIT](LICENSE). Use everything; cite kindly.
