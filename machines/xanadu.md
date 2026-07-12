# Xanadu — Borealis and Aurora

*Machine autopsy. Specs as of 2026-07, sourced in
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*

## 1 · Who & lineage

Xanadu (Toronto, 2016) is the photonic company that ships: hardware on a
public cloud, and PennyLane — the field's most-used QML library — as the
software beachhead. Two machines mark two different theses:

| Machine | Year | Scale | The thesis |
|---|---|---|---|
| Borealis | 2022 | 216 squeezed modes | beat classical at sampling, publicly |
| Aurora | 2025 | 12 qubits / 35 chips / 4 racks | prove the *datacenter* architecture |

## 2 · The qubit

Photonics has no transmon-style two-level object sitting in a trap. Borealis
used **squeezed states of light in time-multiplexed fiber loops** — modes,
not qubits ([why that distinction matters](metrics.md#1-qubit-count--the-vanity-metric)).
Aurora moves to genuine qubits: **GKP bosonic-code states** — grid states in
a photonic mode whose redundancy makes small displacement errors
*measurable and correctable*. GKP states are the photonic bet in one object:
error correction is baked into the qubit itself, because photons offer no
second chances (loss is irreversible).

## 3 · How gates happen

Measurement-based: entangle a large cluster state, then compute by
*measuring* — gate choice becomes measurement-basis choice, executed in
room-temperature silicon-nitride photonics at telecom wavelengths.
Homodyne/PNR detection plus feed-forward replaces pulsed control entirely.

![Gaussian boson sampling pipeline](fig-gbs.svg#only-light)
![Gaussian boson sampling pipeline](fig-gbs-dark.svg#only-dark)

*Borealis' pipeline (above) is sampling-only. Aurora replaces the fixed mesh
with cluster-state generation and adaptive measurements — same components,
universal machine.*

## 4 · System architecture

Aurora's claim to history: **first modular, networked photonic quantum
computer** — 35 photonic chips across 4 server racks, linked by 13 km of
fiber, running error-correction primitives in real time at room
temperature (Nature, Jan 2025; 12 GKP qubits with real-time decoding
reported 2026). Networking is native — the qubits *are* light in fiber —
which is the scaling story every matter-based platform still has to buy
separately.

## 5 · The numbers

| Metric | Borealis | Aurora | Source quality |
|---|---|---|---|
| Scale | 216 modes | 12 GKP qubits | published |
| Advantage claim | 36 µs vs "9,000 years" | — | Nature 2022 |
| Status | retired | prototype | — |
| Loss budget to FT | — | orders of magnitude short | paper, candidly |

## 6 · Error correction status

GKP + real-time decoding on Aurora is real and architecturally important —
but the Nature paper itself is unusually candid that **component losses sit
orders of magnitude above fault-tolerance budgets**. Aurora demonstrates
the *shape* of a fault-tolerant photonic machine, not its performance.

!!! danger "⚔ The skeptic's box"

    - **Borealis is a completed claim-decay case study.** "9,000 years
      classically" (2022) fell to loss-exploiting classical samplers
      (Oh et al., 2023-class tensor methods) that matched or beat parts of
      the task. The machine is retired; the lesson —
      [sampling claims decay](metrics.md#7-advantage-claims--the-special-rules) —
      is permanent.
    - **Aurora's "12 qubits" and "86 billion modes/s" describe different
      layers** — marketing swaps freely between physical qubits, chips, and
      time-bin throughput. Insist on the qubit number.
    - **Loss is the whole game.** Squeezing quality, chip insertion loss,
      detector efficiency — each must improve several-fold *simultaneously*.
      Modularity solved the topology problem; it does not touch the loss
      problem.

## 7 · Roadmap & sources

Watch for: published loss budgets closing generation-over-generation, GKP
logical error rates, and whether the next machine grows qubits (not just
modes).

- [Aurora (Nature 2025)](https://www.nature.com/articles/s41586-024-08406-9)
- [Borealis advantage (Nature 2022)](https://www.nature.com/articles/s41586-022-04725-x)
- [Classical spoofing of GBS (Oh et al.)](https://arxiv.org/abs/2306.03709)
