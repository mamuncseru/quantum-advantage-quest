# IonQ — Forte and Tempo

*Machine autopsy. Specs as of 2026-07, sourced in
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*

## 1 · Who & lineage

Founded 2015 by Chris Monroe (Maryland) and Jungsang Kim (Duke) — the
academic ion-trap lineage on the *other* side of the QCCD family tree from
[Quantinuum](quantinuum.md). First pure-play quantum company to go public
(2021), and the sector's most aggressive acquirer since: **Oxford Ionics**
(2025, the important one — chip traps with electronic gate control),
Lightsynq (photonic interconnects), ID Quantique, Capella (satellite QKD).
IonQ is now as much a quantum-*networking* conglomerate as a computer maker.

| Machine | Year | Qubits | The lesson it taught |
|---|---|---:|---|
| Harmony | 2019 | 11 | first ion machine on a public cloud |
| Aria | 2022 | 25 | the #AQ metric era begins |
| Forte | 2023 | 36 | AOD beam steering; software-defined chains |
| Tempo | 2026 | ~100 | datacenter form factor; first deliveries |

## 2 · The qubit

**¹⁷¹Yb⁺ hyperfine clock states** — same atom, same physics as Quantinuum's
H-series ([qubit figure](quantinuum.md#2--the-qubit)); identical qubits,
seconds-class coherence, error budget in the control system.

## 3 · How gates happen

The architectural contrast with QCCD is the whole story (right panel of
[the ion figure](fig-ions.svg)): IonQ keeps a **single static chain** of
ions in a linear Paul trap and *steers laser beams* instead of moving ions —
acousto-optic deflectors pick out any ion pair for a Raman-driven
Mølmer–Sørensen gate. All-to-all connectivity within the chain, no
transport overhead — but every gate on the shared motional bus, so gates
are slow (hundreds of µs) and crosstalk grows with chain length. The
practical ceiling of one chain is a few dozen ions, which is exactly why
Tempo's ~100 qubits and the declared 256-qubit successor lean on the
Oxford Ionics trap-chip technology and, further out, photonic links
between chains.

## 4 · System architecture

Room-temperature vacuum package (no dilution refrigerator), rack-scale
optics; Forte Enterprise and Tempo are explicitly datacenter-form-factor.
The forward architecture — Oxford Ionics' electrode-controlled gates
(*no lasers in the gate path*) plus Lightsynq-style photonic interconnects —
is a genuinely different bet from Quantinuum's monolithic QCCD: many
smaller chips, networked, rather than one big trap.

## 5 · The numbers

| Metric | Forte | Tempo | Source quality |
|---|---|---|---|
| Physical qubits | 36 | ~100 | vendor |
| 2Q error, typical | 4×10⁻³ | 1×10⁻³ | vendor / **design spec** |
| 1Q error, typical | 2×10⁻⁴ | 1×10⁻⁴ | vendor / design spec |
| Connectivity | all-to-all (chain) | all-to-all | architectural |
| #AQ | 36 | 64 target | vendor metric — see below |

The R&D headline: Oxford Ionics prototype pairs past **99.99%** 2Q fidelity
— the first four-nines gate anywhere. It is a lab record on a prototype
pair, not a system median; on [the landscape](index.md#the-landscape-in-one-picture)
Tempo therefore appears as a hollow marker (spec, not measurement).

## 6 · Error correction status

No logical-qubit demonstrations published. IonQ's stated position has long
been that high physical fidelity defers the need for heavy encoding — true
exactly up to the depth budget argument
([primer §4](metrics.md#4-the-depth-budget--1%CE%B5)), and quietly revised
as the four-nines gates arrive: at 10⁻⁴ physical error, small codes start
buying real logical depth. Watch whether the 256-qubit system ships with
an encoding story.

**Distance to theory:** at Forte's measured 4×10⁻³, one 10⁻¹²-grade
logical qubit needs ≈ **6,000 physical qubits — 168× the machine**; even at
Tempo's spec-sheet 10⁻³ it is ≈ 880, nine times Tempo's size. Zero
algorithm-grade logical qubits, here as everywhere.
[The gap, computed →](gap.md#2--the-gap-computed)

!!! danger "⚔ The skeptic's box"

    - **#AQ is the catalog's canonical vendor-defined metric** — benchmark
      suite chosen by IonQ, scored by IonQ, *with error mitigation allowed*
      ([primer §5](metrics.md#5-holistic-benchmarks--qv-clops-eplg-aq)).
      It is not comparable to anyone else's numbers and has been criticized
      on exactly those grounds.
    - **Spec-sheet culture:** Tempo's 99.9% was published before systems
      shipped; the four-nines number is a prototype-pair record marketed
      with system-level language. Hollow markers until measured medians land.
    - **The chain ceiling is physics, not engineering caution** — motional
      crosstalk and spectral crowding grow with ion number. The multi-chip
      photonic path inherits a new denominator: remote-entanglement rate
      and fidelity, numbers currently published by nobody at system scale.
    - Wall-clock: like all ion machines, gates run ~1,000× slower than
      superconducting — the [CLOPS caveat](metrics.md#5-holistic-benchmarks--qv-clops-eplg-aq)
      applies in full.

## 7 · Roadmap & sources

Watch for: measured Tempo medians vs the spec, the first Oxford-Ionics-trap
production system (256q declared for 2026), and any published
remote-entanglement numbers.

- [IonQ systems comparison](https://www.ionq.com/quantum-systems/compare)
- [Forte](https://www.ionq.com/quantum-systems/forte)
- [Four-nines announcement](https://www.ionq.com/news/ionq-achieves-landmark-result-setting-new-world-record-in-quantum-computing)
- [Oxford Ionics](https://www.oxionics.com/)
