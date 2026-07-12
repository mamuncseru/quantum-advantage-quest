# Atom Computing — a thousand nuclear spins

*Machine autopsy. Specs as of 2026-07, sourced in
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*

## 1 · Who & lineage

Atom Computing (Berkeley, 2018) took the neutral-atom platform in a
different atomic direction from the rubidium camp
([QuEra](quera.md), [Pasqal](pasqal.md)): alkaline-earth-like atoms whose
qubit is a **nuclear spin**. Gen-1 "Phoenix" (2021) used strontium; gen-2
(Oct 2023) moved to ytterbium and became **the first gate-based platform
past 1,000 physical qubits** — 1,180 atoms in a 1,225-site array. Since
2024 the company is effectively Microsoft's neutral-atom hardware arm.

## 2 · The qubit

The nuclear spin of **¹⁷¹Yb** (I = ½) in an optical tweezer. The nucleus
barely talks to the world — no electronic magnetic moment in the ground
state to first order — which buys coherence times quoted at **~40 seconds**
(vendor-reported). Rydberg blockade provides two-qubit gates exactly as in
the rubidium machines ([blockade figure](quera.md#2--the-qubit)); the
nuclear spin adds convenient mid-circuit tricks (measure the electron
cloud without destroying the nuclear qubit).

## 3–4 · Gates & architecture

Rydberg CZ for entanglement, tweezer transport for connectivity, zoned
operation — architecturally the QuEra playbook with a different atom. The
distinguishing engineering feat is *array scale with repetitive
measurement*: demonstrating repeated mid-circuit readout across a
thousand-site array without evicting the atoms.

## 5 · The numbers

| Metric | Value | Source quality |
|---|---|---|
| Physical qubits (sites) | 1,180 (1,225) | published |
| Nuclear-spin coherence | ~40 s | vendor |
| 2Q fidelity at array scale | **not published** | — |
| Logical qubits | 24 entangled (with Microsoft, Nov 2024) | vendor+MSFT |
| Next machine | "Magne": 50 logical (QuNorth, Denmark) | announced |

That empty third row is the page's most important cell
([primer §1: trapped ≠ computing](metrics.md#1-qubit-count--the-vanity-metric)).

## 6 · Error correction status

Through the Microsoft partnership: 24 entangled logical qubits and
28 prepared (Nov 2024) via Microsoft's qubit-virtualization stack — at the
time the largest entangled logical register anywhere, since overtaken by
[QuEra–Harvard's 96](quera.md#6--error-correction-status). The commercial
bet is **Magne** (with Microsoft): ~50 logical qubits from ~1,200 physical,
sold to Denmark's QuNorth initiative, operational target 2026–27 — the
first attempt to *sell* a logical-qubit machine rather than demonstrate one.

!!! danger "⚔ The skeptic's box"

    - **1,180 trapped atoms made the headlines; the entangling fidelity at
      that scale was never published.** The logical-qubit demos ran on far
      smaller active registers. The gap between "sites in the array" and
      "qubits doing verified two-qubit gates" is this vendor's version of
      the count-vs-quality trap.
    - **The 40-second coherence is a memory number** — it does not survive
      Rydberg gates, transport, or imaging; the effective coherence during
      computation is orders shorter.
    - **Microsoft dependency cuts both ways:** the virtualization stack
      supplied the logical-qubit results, and Microsoft's platform strategy
      (it also partners with [Quantinuum](quantinuum.md) and runs its own
      [topological program](microsoft.md)) does not need this particular
      hardware to win. Magne's delivery is the falsifiable milestone.

## 7 · Roadmap & sources

Watch for: published 2Q fidelities at ≥100-qubit active scale, and Magne
commissioning at QuNorth with operator-side numbers.

- [1,180-atom announcement](https://atom-computing.com/quantum-startup-atom-computing-first-to-exceed-1000-qubits/)
- [Microsoft + Atom logical qubits (Nov 2024)](https://blogs.microsoft.com/blog/2024/11/19/microsoft-and-atom-computing-offer-a-commercial-quantum-machine-with-the-largest-number-of-entangled-qubits/)
- [Yb-171 nuclear-spin qubit literature (arXiv:2112.06732)](https://arxiv.org/abs/2112.06732)
