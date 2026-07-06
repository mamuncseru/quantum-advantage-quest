---
title: Home
hide:
  - navigation
  - toc
---

<div class="qq-hero" markdown>

# Quantum Advantage Quest

<p class="qq-tag">A problem-first expedition toward genuine quantum advantage — run fully in the open.</p>

<blockquote class="qq-quote">
"Almost no named quantum algorithm came from a new primitive.<br>
It came from a new problem."
<span class="attrib">— the thesis this program tests</span>
</blockquote>

[Start the curriculum :octicons-arrow-right-24:](curriculum/00-curriculum.md){ .md-button .md-button--primary }
[Read the roadmap](ROADMAP.md){ .md-button }
[:fontawesome-brands-github: Source](https://github.com/mamuncseru/quantum-advantage-quest){ .md-button }

</div>

<div class="qq-stats" markdown>
  <div class="qq-stat"><span class="num">13</span><span class="lbl">autopsies</span></div>
  <div class="qq-stat"><span class="num">32</span><span class="lbl">passing tests</span></div>
  <div class="qq-stat"><span class="num">19</span><span class="lbl">qubits, Shor demo</span></div>
  <div class="qq-stat"><span class="num">6</span><span class="lbl">month clock</span></div>
  <div class="qq-stat"><span class="num">2</span><span class="lbl">hunting grounds</span></div>
</div>

<figure markdown="span">
  ![Order finding interference spectrum](predecessors/04-shor/fig-spectrum.svg#only-light)
  ![Order finding interference spectrum](predecessors/04-shor/fig-spectrum-dark.svg#only-dark)
  <figcaption>Not a stock photo — real output of this repo's hand-built simulator: Shor's
  algorithm factoring 15, with the order r = 4 written into the interference
  peaks of a 9-qubit counting register. Every figure on this site is generated
  by the code you can read here.</figcaption>
</figure>

## What this is

Most published "quantum advantage" claims die the same death: someone takes the
classical baseline seriously. This site is a live, open research program built
on the opposite reflex — **attack your own results first** — with one goal:
design a quantum algorithm with theoretically validated advantage, at the
currency Shor's algorithm trades in (a rigorous algorithm **plus** classical
hardness under a well-studied assumption).

The journey is shared as it happens: the study of every named quantum algorithm
(*The Predecessors*), the distilled pattern-book (*the Problem-Shape Catalog*),
the literature frontier, and — soon — the hunt itself, including the failures.

<div class="grid cards" markdown>

-   :material-dna:{ .lg .middle } **The Predecessors**

    ---

    Thirteen algorithm autopsies, Deutsch–Jozsa → Shor → QSVT → DQI, each
    answering the same five questions: what problem, what wall, what
    primitive, what hardness, what lesson.

    [:octicons-arrow-right-24: Autopsy 01](predecessors/01-deutsch-jozsa/notes.md)

-   :material-flask-outline:{ .lg .middle } **Everything runs**

    ---

    A ~100-line hand-built statevector simulator, no framework black boxes.
    Shor factors 35 on 19 qubits; a Davies Lindbladian provably converges to
    its Gibbs state; Tang's dequantization kills an "advantage" before your
    eyes. `pytest` proves all of it.

    [:octicons-arrow-right-24: The simulator](qsim/__init__.py)

-   :material-map-search:{ .lg .middle } **The Problem-Shape Catalog**

    ---

    The hunting weapon: 12 problem shapes that map to quantum mechanisms,
    5 graveyards that eat research programs, and the meta-patterns behind
    every named algorithm.

    [:octicons-arrow-right-24: Read the catalog](frontier/problem-shapes.md)

-   :material-sword-cross:{ .lg .middle } **Rules of engagement**

    ---

    Symmetric effort for classical baselines. Hardness needs a mechanism.
    Kill criteria pre-registered. Negative results are deliverables. Every
    proof gets attacked before it gets believed.

    [:octicons-arrow-right-24: The roadmap & rules](ROADMAP.md)

</div>

## How a lesson works

Every algorithm gets the same **autopsy**, because the goal isn't to admire the
circuit — it's to learn how algorithms get *found*:

1. **The problem** — who cared about it *before* quantum computing?
2. **The classical wall** — which structural feature blocked classical progress?
3. **The primitive** — how exactly does interference extract the answer?
4. **The hardness evidence** — and what happened when classical algorithms fought back?
5. **The lesson** — what *shape* of problem does this mechanism want?

Question 4 is the one this field keeps skipping. Here it never is: the same
curriculum that builds Shor also builds the Tang dequantization and the BBBV
lower bound — the anti-hype toolkit — because an advantage you haven't tried
to kill is not yet a result.

## The six-month arc

| Phase | Weeks | What happens |
|---|---|---|
| **ARM** | 1–5 | The Predecessors: 13 autopsies, from-scratch code, proof drafts |
| **HUNT** | 6–13 | Problem-first search on two grounds: optimization-as-decoding (DQI) and quantum Gibbs sampling |
| **STRIKE** | 14–20 | Everything on the best surviving candidate — proof attempt and self-attack in parallel |
| **WRITE** | 21–26 | The result — positive or a precise boundary — written with full care |

*Sibling project: [HilbertBench](https://github.com/mamuncseru/hilbertbench) —
diagnostics for quantum ML experiments. The Bench diagnoses; the Quest hunts.*
