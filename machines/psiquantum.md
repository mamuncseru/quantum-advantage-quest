# PsiQuantum — the machine that doesn't exist yet

*Machine autopsy — of a blueprint. Specs as of 2026-07, sourced in
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*

## 1 · Who & the bet

PsiQuantum (Palo Alto, 2016; Jeremy O'Brien, Terry Rudolph et al. —
UK photonics academia transplanted to Silicon Valley money) holds the
field's most extreme position: **NISQ is a dead end, so build nothing until
you can build a fault-tolerant million-qubit machine.** No cloud offering,
no benchmark demos, no intermediate machines — a decade of silence
punctuated by manufacturing papers. It is either the most disciplined
program in the field or the most expensive way to be wrong, with billions
in private and government capital (Australia, Illinois) riding on which.

## 2 · The qubit

**Dual-rail photonic qubits**: one photon across two waveguides. Photons
don't decohere sitting still and don't feel their neighbors — the inverse
of every matter platform's problem profile. The catch: photons vanish
(loss), and two photons interact only through measurement — so every
entangling operation is probabilistic.

## 3 · How gates happen — fusion

The architecture is **fusion-based quantum computing (FBQC)**: generate
small entangled photon clusters ("resource states"), then join them by
**fusion measurements** — destructive two-photon measurements that either
link the clusters or herald a failure that the code absorbs as a known
erasure. Computation = a lattice of fusions in spacetime; the error
correction *is* the architecture, not a layer on top.

## 4 · System architecture

The real thesis is **manufacturing**: the **Omega** chipset (Nature 2025)
runs on GlobalFoundries' standard 300 mm silicon-photonics line — waveguides,
single-photon detectors, and switches in a commercial fab, at wafer scale.
Two million-qubit-class sites are under construction (Brisbane; Chicago's
Illinois Quantum Park), designed around **cryogenic plant at ~4 K**
(photon detectors' requirement — far cheaper than millikelvin dilution
fridges) and networking-native photonics throughout.

## 5 · The numbers

| Metric | Value | Source quality |
|---|---|---|
| Operational qubits, any site, today | **0** | — |
| Chipset | Omega, GF 300 mm | Nature 2025 |
| Declared target | ~10⁶ physical qubits, FT | vendor |
| Timeline | "operational ~2027–28" | vendor, has slipped before |

## 6 · Error correction status

On paper, arguably the most complete FT architecture published (FBQC +
interleaved photonic memory). In hardware: component demonstrations only —
no logical qubit, no system.

!!! danger "⚔ The skeptic's box"

    - **Zero machines after a decade and billions** is itself a datum. The
      skip-NISQ argument is intellectually respectable — this repository
      shares the skepticism of near-term advantage — but it also
      conveniently defers every falsifiable milestone to the far end.
    - **The published loss numbers still don't close.** FBQC tolerates
      percent-level loss budgets end-to-end; demonstrated
      source-switch-detector chains remain above that. The gap must close
      in *manufactured* components, not hero devices.
    - **Government-scale funding creates schedule truth-bending pressure** —
      dates have already moved right (2025 → 2027-28). Treat all timelines
      as soft until a logical qubit exists.
    - The falsifiable near-term milestone to hold them to: **a logical
      qubit from fab-line chips, with published loss budgets.**

## 7 · Sources

- [Omega chipset (Nature 2025)](https://www.nature.com/articles/s41586-025-08820-7)
- [PsiQuantum news](https://www.psiquantum.com/news)
- [FBQC architecture paper (arXiv:2101.09310)](https://arxiv.org/abs/2101.09310)
