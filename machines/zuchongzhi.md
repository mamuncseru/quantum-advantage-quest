# USTC Zuchongzhi — the other superconducting frontier

*Machine autopsy. Specs as of 2026-07, sourced in
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*

## 1 · Who & lineage

The University of Science and Technology of China (Hefei), under Jian-Wei
Pan's quantum program with Xiao-Bo Zhu leading the superconducting line. The
same institution runs the [Jiuzhang photonic samplers](jiuzhang.md) — one
lab, two independent shots at beyond-classical claims. The machine is named
for Zu Chongzhi, the 5th-century mathematician who pinned π to seven digits.

| Chip | Year | Qubits | The lesson it taught |
|---|---|---:|---|
| Zuchongzhi 1 | 2021 | 62 | first 2D walk demos at scale |
| Zuchongzhi 2.0/2.1 | 2021 | 66 | RCS supremacy claim #2 — and its decay |
| Zuchongzhi 3.0 | 2025 | 105 | Willow-class hardware, parallel-benchmarked |

This is a *prototype* line — no cloud access, results arrive as papers. The
strategic read: USTC deliberately mirrors Google's architecture choices and
publishes the comparison, making it the only independent replication of the
Willow design point anywhere.

## 2 · The qubit

A **frequency-tunable transmon** — Google's choice, not IBM's: SQUID loop,
flux-bias line per qubit, tunable coupler per edge
([the trade-off table on the Google page](google.md#2--the-qubit) applies
verbatim). Flip-chip packaging: qubits on one die, wiring on another, bonded
face-to-face — how you route 105 flux lines plus 182 couplers without
routing them *through* the qubit plane.

## 3 · How gates happen

Flux-pulsed CZ via the |11⟩↔|02⟩ avoided crossing, microwave 1Q gates,
dispersive readout — the Google recipe. The distinguishing habit is
*how they benchmark*: all reported fidelities are **parallel** — measured
with the whole chip firing, crosstalk included:

- 1Q: 99.90% (parallel)
- 2Q: 99.62% (parallel)
- readout: 99.13% (parallel)

Parallel numbers are the honest ones
([primer, question 2](metrics.md#3-gate-fidelity--where-the-bodies-are-buried)) —
credit where due, and a standing rebuke to isolated-pair marketing.

## 4 · System architecture

Square lattice, degree 4, 105 qubits + 182 couplers
([lattice figure](ibm.md#4--system-architecture)) — a surface-code floor
plan, same as Willow. T1 ≈ 72 µs against Willow's ~100 µs: the replication
lag is in materials/coherence, roughly one hardware generation, and closing.

## 5 · The numbers

| Metric | Zuchongzhi 3.0 | Source quality |
|---|---|---|
| Physical qubits | 105 (182 couplers) | published |
| 2Q error, **parallel** | 3.8×10⁻³ | PRL 2025 |
| 1Q error, **parallel** | 1.0×10⁻³ | PRL 2025 |
| Readout error, parallel | 8.7×10⁻³ | PRL 2025 |
| T1 | 72 µs | PRL 2025 |
| Depth budget (1/ε) | ~260 gates | derived |

## 6 · Error correction status

No logical qubits on Zuchongzhi 3.0 yet. The group has run surface-code
experiments on the 2.x generation (distance-3 era) and states error
correction as the 3.0 follow-up program; a below-threshold replication on
this chip would be the first independent confirmation of the Willow result —
worth more to the field than another sampling record.

**Distance to theory:** at 3.8×10⁻³ parallel 2Q error, one 10⁻¹²-grade
logical qubit costs distance-53 ≈ **5,600 physical qubits — 53× the chip**.
Logical qubits on board today: zero.
[The gap, computed →](gap.md#2--the-gap-computed)

!!! danger "⚔ The skeptic's box"

    - **The headline is an RCS claim: 83 qubits × 32 cycles, "10¹⁵× beyond
      Frontier" (PRL cover, Mar 2025).** Zuchongzhi 2.1's 2021 claim was
      substantially reclaimed by the same tensor-network methods that killed
      Sycamore's margin — the authors know this, which is why 3.0's circuits
      are deeper. The margin is real *today*; its half-life is the question
      ([claim-decay rules](metrics.md#7-advantage-claims--the-special-rules)).
    - **Unverifiable at size, by construction** — the fidelity behind the
      claim is XEB-extrapolated, exactly like Google's.
    - **"10¹⁵× faster than the best classical"** compares against published
      classical algorithms as of submission. The two prior entries in this
      exact series (Sycamore, Zuchongzhi 2) both lost ≥10 orders of
      magnitude of margin post-publication. Priced accordingly.

## 7 · Roadmap & sources

Watch for: a surface-code result on 105-qubit-class hardware (the
independent Willow check), coherence closing the ~72→100 µs gap, and
whether the RCS margin survives 2026's tensor-network literature.

- [Zuchongzhi 3.0 (Phys. Rev. Lett. 134, 090601, 2025)](https://link.aps.org/doi/10.1103/PhysRevLett.134.090601)
- [arXiv:2412.11924](https://arxiv.org/abs/2412.11924)
- [CAS announcement](https://english.cas.cn/head/202503/t20250305_903086.shtml)
