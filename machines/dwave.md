# D-Wave Advantage2 — the annealer

*Machine autopsy. Specs as of 2026-07, sourced in
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*

## 1 · Who & lineage

D-Wave (Burnaby, Canada, 1999) is the oldest quantum computing company and
the perennial outsider: it shipped "quantum computers" a decade before
anyone else by building a **different kind of machine** — an annealer, not
a gate-model computer — and has spent twenty years litigating (sometimes
literally in Science and Nature) whether its speedups are quantum at all.
Advantage (5,000+ qubits, 2020) → **Advantage2** (GA May 2025).

## 2 · The qubit

An **rf-SQUID flux qubit**: a superconducting loop where |0⟩/|1⟩ are
clockwise/counter-clockwise persistent currents. Far noisier and
shorter-lived than a transmon — deliberately so: annealing doesn't need
gate-grade coherence, it needs *many* qubits with *strong, programmable
couplings*.

## 3 · How it computes — no gates

Program an Ising problem into qubit biases and coupler strengths, start in
the ground state of a trivial Hamiltonian, and **anneal**: slowly deform
toward the problem Hamiltonian, hoping quantum tunneling keeps the system
near the ground state. The answer is read out as a spin configuration. It
is a physics-powered optimizer/sampler for one problem class — QUBO/Ising —
not a universal computer ([the analog caveat](metrics.md#1-qubit-count--the-vanity-metric), again).

## 4–5 · Architecture & numbers

| Metric | Advantage2 | Source quality |
|---|---|---|
| Flux qubits | 4,400+ | published |
| Topology | Zephyr, 20-way coupling | published |
| vs Advantage | +40% energy scale, −75% noise, 2× coherence | vendor whitepaper |
| Gate fidelity / logical qubits | not applicable | — |

Millikelvin fridge like the gate-model superconductors, but the similarity
ends there: embedding a real problem into Zephyr burns qubits fast (chains
of physical qubits per logical variable), so "4,400 qubits" translates to
hundreds-to-low-thousands of problem variables depending on graph density.

## 6 · Error correction status

None, and none possible in the gate-model sense. Notably, D-Wave itself
announced a **gate-model superconducting program** (2025-26) — read that as
the company hedging its founding thesis.

!!! danger "⚔ The skeptic's box"

    - **The Science 2025 supremacy claim met the standard fate.** D-Wave
      reported spin-glass dynamics beyond Frontier (Mar 2025); within
      months, tensor-network groups (Tindall et al. and others) reproduced
      substantial parts classically. The pattern — claim on a
      vendor-favorable instance class, classical reply on the tractable
      subregion — has now run three full cycles since 2014.
    - **Twenty years without a clean, portable advantage** on a problem
      anyone independently cares about is the base rate to reason from.
      Annealing wins appear on native-topology, vendor-selected instances
      and evaporate under embedding overhead plus tuned classical
      heuristics (simulated annealing, parallel tempering, SVMC).
    - **Commercial traction is real** (usage up 314% year-over-year, real
      deployments) — but commercial adoption measures *usefulness at
      current prices*, not quantum advantage. Those are different claims,
      and only one of them is this catalog's business.

## 7 · Sources

- [Advantage2 4,400-qubit whitepaper](https://www.dwavequantum.com/media/wakjcpsf/adv2_4400q_whitepaper-1.pdf)
- [Advantage2 GA (May 2025)](https://www.businesswire.com/news/home/20250520948155/en/)
- [Supremacy claim & rebuttal context](https://postquantum.com/industry-news/d-wave-quantum-advantage/)
