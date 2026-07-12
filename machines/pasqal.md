# Pasqal — analog atoms for Europe

*Machine autopsy. Specs as of 2026-07, sourced in
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*

## 1 · Who & lineage

Pasqal (Massy, France, 2019) is the Institut d'Optique spin-out — Antoine
Browaeys' and Thierry Lahaye's tweezer-array program, with Nobel laureate
Alain Aspect as co-founder. It is Europe's flagship neutral-atom company
and the continent's counterweight to [QuEra](quera.md): same physics,
different strategy — **sell analog machines to HPC centers now**, digitize
later.

## 2 · The qubit

**⁸⁷Rb in optical tweezers** — identical physics to QuEra
([qubit & blockade figure](quera.md#2--the-qubit)): hyperfine storage,
Rydberg interactions, room-temperature vacuum system drawing ~3 kW total.
Over 1,000 atoms trapped in a single lab processor (2024); ~100-atom
machines are what ships.

## 3 · How gates happen — mostly, they don't

The delivered product is **analog**: atom geometry encodes the problem
graph, global pulses drive the Rydberg Hamiltonian, and the machine
produces samples from its evolution. Native workloads: quantum simulation
of magnetism, and graph problems (MIS-type) embedded in atom positions.
A digital gate-based mode is on the roadmap, not in the field.

## 4 · System architecture

Orion-class QPUs are deliberately boring in the best sense: rack-mounted,
room-temperature, datacenter-compatible units delivered **on-premises** to
Jülich (JUPITER integration), GENCI/CEA in France, and further European and
international HPC sites. Pasqal's real moat is procedural — it is the
neutral-atom vendor European supercomputing centers can actually buy,
integrate, and schedule jobs on.

## 5 · The numbers

| Metric | Value | Source quality |
|---|---|---|
| Atoms per delivered QPU | ~100 | vendor/operator |
| Atoms trapped (lab) | >1,000 | published |
| Gate fidelities | — (analog mode) | n/a |
| Next declared step | 250-qubit QPU, 2026 | vendor |

The dashes are the point: an analog machine has no gate fidelity to report,
which makes cross-platform comparison tables featuring Pasqal qubit counts
structurally misleading ([primer §1](metrics.md#1-qubit-count--the-vanity-metric)).

## 6 · Error correction status

None — error correction is a digital-mode concept. The relevant quality
figures for analog operation (state-preparation fidelity, detection
fidelity, Hamiltonian calibration accuracy) are published per-experiment
rather than as system specs.

!!! danger "⚔ The skeptic's box"

    - **Analog quantum simulation at 100 atoms lives inside tensor-network
      range** for most practically accessed regimes; 2D Rydberg dynamics
      claims need — and rarely get — an adversarial classical baseline.
    - **The digital transition is the entire long-run bet**, and every
      neutral-atom digital milestone so far (blockade-gate fidelity, zoned
      logical operation) has come from the QuEra–Harvard axis, not from
      Pasqal. The 250-qubit machine's mode (analog vs digital) is the tell
      to watch.
    - **"Delivered to HPC centers" measures procurement, not physics** —
      the same caveat as [IQM](superconducting-field.md#iqm--europes-on-prem-workhorse).

## 7 · Roadmap & sources

Watch for: the 250-qubit QPU's mode, first digital-gate fidelities, and
independent operator reports from Jülich/GENCI workloads.

- [Pasqal newsroom](https://www.pasqal.com/newsroom/)
- [Browaeys–Lahaye review of tweezer-array physics](https://www.nature.com/articles/s41567-019-0733-z)
