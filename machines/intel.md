# Intel Tunnel Falls — the transistor argument

*Machine autopsy. Specs as of 2026-07, sourced in
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*

## 1 · Who & the bet

Intel's quantum program (Oregon, with QuTech/Delft heritage) makes a single
argument with total conviction: **the winning qubit will be the one you can
manufacture like a transistor.** No cloud service, no qubit-count races —
research chips distributed to national labs and universities like foundry
samples: LPS/Maryland, Sandia, Rochester, Wisconsin, and an Argonne testbed
deployment in January 2026.

## 2 · The qubit

A **single electron's spin** in a silicon/silicon-germanium quantum dot —
gate electrodes corral one electron, and |0⟩/|1⟩ are spin states in an
applied field. It is the smallest qubit on any platform (~100 nm pitch,
about a million times smaller in area than a transmon's footprint), runs at
~1 K rather than millikelvin, and is made of the semiconductor industry's
best-understood material.

## 3 · How gates happen

1Q: microwave spin resonance (ESR/EDSR). 2Q: the **exchange interaction** —
lower the electrostatic barrier between neighboring dots and the two
electrons' spins couple (√SWAP-class gates). Fast, nanosecond-scale, but
exquisitely sensitive to sub-nanometer electrostatics — which is exactly
why Intel insists fab uniformity is the whole problem.

## 4 · System architecture

**Tunnel Falls** (2023): 12 quantum dots in a linear array, fabricated with
EUV lithography on Intel's 300 mm D1 line — **~95% device yield, >24,000
multi-qubit devices per wafer**, threshold-voltage uniformity approaching
CMOS norms. Control via **Horse Ridge II**, Intel's cryo-CMOS controller
operating at 4 K — attacking the wiring bottleneck that every
dilution-fridge platform hits ([IBM's wiring wall](ibm.md#4--system-architecture)).

## 5 · The numbers

| Metric | Value | Source quality |
|---|---|---|
| Qubits | 12 (linear) | published |
| Yield / devices per wafer | ~95% / >24,000 | published |
| System 2Q fidelity | **not published** | — |
| Field-best Si-spin 2Q (other groups) | ~99.5% | Delft/RIKEN literature |

## 6 · Error correction status

None demonstrated on Intel hardware. The field-wide silicon-spin story is
credible at small scale (two-qubit fidelities above 99.5% in academic
devices, natural compatibility with dense 2D arrays) but no silicon
platform anywhere has run a multi-qubit code.

!!! danger "⚔ The skeptic's box"

    - **A fab story, not a computing story — yet.** Yield and uniformity
      are necessary, not sufficient; no system-level algorithm demo exists
      on any Intel chip, and the 12-qubit scale is where superconductors
      were in ~2012.
    - **Crossing the valley:** valley splitting, charge noise, and
      addressability at scale are silicon-specific physics risks that
      transistor manufacturing prowess does not automatically retire.
    - **The strategic risk is patience** — Intel's own corporate turbulence
      makes a decade-horizon research program institutionally fragile; the
      program's quiet 2024–26 cadence is worth reading in that light.

## 7 · Sources

- [Tunnel Falls announcement](https://newsroom.intel.com/new-technologies/quantum-computing-chip-to-advance-research)
- [Argonne deployment (Jan 2026)](https://quantumcomputingreport.com/argonne-national-laboratory-and-intel-deploy-12-qubit-silicon-quantum-dot-processor/)
- [12-spin-qubit 300 mm fab paper (Nano Letters)](https://pubs.acs.org/doi/10.1021/acs.nanolett.4c05205)
