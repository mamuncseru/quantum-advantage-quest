# QuEra — Aquila and the logical-qubit machines

*Machine autopsy. Specs as of 2026-07, sourced in
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*

## 1 · Who & lineage

QuEra Computing (Boston, 2018) commercializes the Harvard–MIT neutral-atom
program — above all Mikhail Lukin's group, which has quietly produced more
of the last three years' landmark error-correction results than any
corporate lab. The company operates in an unusual dual mode: **Aquila**, a
256-atom analog machine public on AWS Braket since 2022, and a line of
gate-based logical-qubit machines built jointly with the academic lab.

| Machine | Year | Atoms | The lesson it taught |
|---|---|---:|---|
| Aquila | 2022 | 256 | analog Rydberg simulation at scale, publicly |
| Harvard logical demo | 2023 | 280 | 48 logical qubits — the field's wake-up call |
| Logical processor | 2026 | 448 | 96 logical, below threshold, high-rate codes |

## 2 · The qubit

**⁸⁷Rb hyperfine ground states** held in optical tweezers — individually
trapped neutral atoms, identical by nature, with seconds-class coherence.
The computational trick is the **Rydberg state**: promote an atom to a huge
principal quantum number and it acquires a micron-ranged interaction that
ground-state atoms completely lack. Qubits are stored where nothing
interacts and entangled only when deliberately excited.

![Rydberg blockade gate and movable-tweezer architecture](fig-tweezers.svg#only-light)
![Rydberg blockade gate and movable-tweezer architecture](fig-tweezers-dark.svg#only-dark)

## 3 · How gates happen

- **Analog (Aquila):** no gates. You program atom positions (the
  interaction graph) and global laser sweeps, and the machine evolves under
  its native Rydberg Hamiltonian.
- **Digital (logical line):** the **Rydberg-blockade CZ** — within the
  blockade radius only one atom of a pair can reach the Rydberg state, and
  that conditionality is the entangling gate. Physical fidelity 99.5%
  (Evered et al., Nature 2023), executed in ~hundreds of nanoseconds by
  *global* beams on many pairs in parallel.

## 4 · System architecture

The architecture is the moving of atoms (right panel above): tweezers drag
qubits between **storage, entangling, and readout zones**, so connectivity
is a compiler decision. This is precisely the capability high-rate qLDPC
codes need — non-local check operators are just another move — and it is
why this platform, not superconductors, holds the logical-qubit records
([the code-rate argument](metrics.md#6-logical-qubits--the-new-number-and-its-new-games)).
Room-temperature vacuum cell, no dilution refrigerator; the 2025
continuous-reload arrays (3,000+ atoms at Harvard) attack the platform's
oldest weakness, atom loss.

## 5 · The numbers

| Metric | Value | Source quality |
|---|---|---|
| Aquila atoms (analog) | 256 | published |
| Logical processor atoms | 448 | Nature 2026 |
| **Logical qubits** | **96** (37 operational at AIST) | Nature 2026 |
| Physical CZ error | 5×10⁻³ | Nature 2023 |
| Coherence (hyperfine) | ~seconds | literature |
| Logical clock | ~kHz-class cycles | the honest denominator |

## 6 · Error correction status

The platform leader, and it isn't close: 48 logical qubits in 2023
(surface-code-era, transversal circuits), then **96 logical from 448 atoms
using [[16,6,4]]-family high-rate codes, below threshold** (Nature,
Jan 2026), then a 2:1 physical-to-logical qLDPC demonstration (Apr 2026).
For calibration: the best superconducting result is *one* below-threshold
logical qubit. The open questions are operational — logical *algorithms*,
not logical memories, and the wall-clock cost of all that atom traffic.

**Distance to theory:** by surface-code arithmetic at the 5×10⁻³ physical
CZ, one 10⁻¹²-grade logical qubit would cost ≈ **10,700 physical atoms** —
which is precisely why this platform bets on high-rate codes and transport
instead. The 96 logical qubits are *memories* at ~10⁻³-class logical error,
not 10⁻¹² compute qubits; the code-rate advantage must survive nine more
orders of magnitude of suppression to cash out.
[The gap, computed →](gap.md#2--the-gap-computed)

!!! danger "⚔ The skeptic's box"

    - **Aquila's analog results keep getting matched.** The 2023 quantum
      speedup claim for maximum independent set on unit-disk graphs was
      answered by better classical heuristics within months; phase-diagram
      results at 256 atoms sit within tensor-network reach. Analog
      "advantage" on graph problems has not survived contact with motivated
      classical baselines — a pattern this repo's
      [kill/keep ledger](../hunt/ledger.md) would recognize.
    - **The logical-qubit numbers are real but the denominators are quiet:**
      logical cycle rates (limited by atom transport and imaging at ~ms
      scale), atom loss between cycles, and the post-selection fraction in
      some demos. 96 logical qubits at kHz-class cycles is a different
      machine from 96 logical qubits at MHz — check which one a claim needs
      ([checklist item 7](metrics.md#the-checklist)).
    - **Two-machine ambiguity in marketing:** capabilities of the
      Harvard-lab demonstrators and the commercially deployed systems
      (Aquila; the AIST machine) are routinely quoted side by side. Ask
      which box the number came from.

## 7 · Roadmap & sources

Watch for: a logical-qubit *algorithm* demo (not memory), published loss
and cycle-rate budgets, and the declared 10,000-atom-class machine.

- [96 logical qubits coverage (Jan 2026)](https://www.businesswire.com/news/home/20260112950379/en/)
- [Evered et al., 99.5% Rydberg CZ (Nature 2023)](https://www.nature.com/articles/s41586-023-06481-y)
- [Bluvstein et al., 48 logical qubits (Nature 2024)](https://www.nature.com/articles/s41586-023-06927-3)
- [Aquila on AWS Braket](https://aws.amazon.com/braket/quantum-computers/quera/)
