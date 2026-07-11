# The superconducting field — Rigetti, IQM, OQC, Fujitsu & co.

*Machine autopsies, condensed. Specs as of 2026-07, sourced in
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*

Behind [IBM](ibm.md), [Google](google.md), and [USTC](zuchongzhi.md) runs a
second tier of superconducting programs. The physics is the same transmon
([level diagram](ibm.md#2--the-qubit)); what differs is the business model —
and one full *nine* of two-qubit fidelity, which per
[the nines plot](metrics.md#0-the-one-plot-to-internalize) is a 10× depth
deficit. Each entry here is a different strategy for surviving that gap.

## Rigetti — the chiplet bet

Founded 2013 (Chad Rigetti, ex-IBM), Berkeley; runs **Fab-1**, the only
dedicated quantum foundry among the startups.

- **Ankaa-3** (Dec 2024): 84 tunable transmons, square lattice, tunable
  couplers. Median **fSim 99.5%** / iSWAP 99.0%, gates 56–72 ns — a
  ~200-gate depth budget, one nine behind the leaders.
- **The bet:** stop scaling dies, start tiling them. **Cepheus-1-36Q**
  (2025) stitches four 9-qubit chiplets; a 100+ qubit chiplet system is the
  declared 2026 step. If inter-chiplet gates hold fidelity, this sidesteps
  the yield wall every monolithic chip faces.
- **Skeptic's note:** the number that decides the bet — *inter-chiplet*
  2Q fidelity at scale — is exactly the number not yet published.

## IQM — Europe's on-prem workhorse

Espoo, Finland (Aalto/VTT spin-out, 2018). The quiet volume leader: more
systems physically delivered to customers (LRZ, VTT, and installations
across Europe and Asia) than anyone else in the tier.

- Product ladder: **Spark** (5q, education) → **Radiance 54** (flagship,
  2025) → 150-qubit class declared next.
- Numbers: vendor materials cite ~99.5% median 2Q on delivered systems and
  a 99.91% single-pair record on the 20-qubit Crystal — but third-party
  aggregators contradict each other on IQM specs, so `data.yml` carries
  **null** until an operator report pins them.
- **Skeptic's note:** on-prem machines create a verification asymmetry —
  the buyer sees the calibration data, the field sees the press release.

## OQC — the 3D shortcut

Oxford Quantum Circuits. Its **coaxmon** puts control and readout wiring
*above* the qubit plane on a coaxial stack rather than beside it —
trading planar fab simplicity for wiring density. **Toshiko** (32q, 2023)
went into commercial data centers (Equinix). Public fleet fidelities:
sparse, which for the purposes of this catalog is itself a datum.

## Fujitsu / RIKEN — the HPC-integration play

The RIKEN RQC–Fujitsu center shipped a 64q machine (2023), then **256q
(Apr 2025)** with 3D packaging, targeting ~1,000 qubits in 2026. The
strategy is not to win the fidelity race but to sit next to Fugaku-class
supercomputers as a hybrid accelerator. No published fleet-wide fidelities —
count without quality until proven otherwise
([primer, §1](metrics.md#1-qubit-count--the-vanity-metric)).

## Also in the field (one line each, all superconducting-adjacent)

- **Alice & Bob** (Paris) — **cat qubits**: bosonic states in a cavity whose
  bit-flips are exponentially suppressed by design (bit-flip lifetimes now
  quoted in *hours*); only phase-flips need correcting, collapsing the code
  overhead by one dimension. Watch this one.
- **AWS** — entered hardware with **Ocelot** (Feb 2025, Nature): cat-qubit
  memory with transmon ancillas; claims ~90% resource reduction for QEC.
- **SeeQC** — single-flux-quantum classical control *on the qubit chip*:
  attacks the wiring wall rather than the fidelity wall.
- **Quantum Circuits Inc.** (Yale lineage) — dual-rail transmon qubits with
  built-in erasure detection: errors become *flagged* losses, which codes
  handle far more cheaply.

!!! danger "⚔ The skeptic's box (for the whole tier)"

    - **The tier's defining fact is the missing nine.** ~99.5% median 2Q
      versus ~99.9%+ for the leaders is not a 0.4% gap — it is 10× less
      circuit depth, per the exponential
      ([nines plot](metrics.md#0-the-one-plot-to-internalize)).
    - **Every strategy above is a way to change the axis of competition** —
      chiplets (yield), on-prem delivery (distribution), 3D wiring
      (density), HPC integration (workflow), cat/dual-rail qubits (error
      *structure*). Legitimate — but none of them repeals the depth budget.
    - **Beware deployment-count marketing.** "Systems delivered" measures
      sales, not physics; a delivered 99.5% machine runs the same shallow
      circuits wherever it is installed.

## Sources

- [Rigetti Ankaa-3 launch](https://investors.rigetti.com/news-releases/news-release-details/rigetti-computing-launches-84-qubit-ankaatm-3-system-achieves)
- [IQM](https://www.meetiqm.com/) · [OQC](https://oqc.tech/) ·
  [Fujitsu 256q release](https://www.fujitsu.com/global/about/resources/news/press-releases/2025/0422-01.html)
- [AWS Ocelot (Nature 2025)](https://www.nature.com/articles/s41586-025-08642-7)
