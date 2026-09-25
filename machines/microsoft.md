# Microsoft Majorana — the contested qubit

*Machine autopsy. Specs as of 2026-07, sourced in
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*
**Status: contested** — *the only entry in this catalog whose central claims
are disputed in the peer-reviewed literature.*

## 1 · Who & the bet

Microsoft's Station Q program (since ~2005, Santa Barbara/Copenhagen/Delft)
pursues the **topological qubit**: encode quantum information non-locally
in **Majorana zero modes** so that local noise physically *cannot* touch it
— error correction by physics instead of by code. The prize justifies the
patience: a working topological qubit would collapse the overheads every
other page in this catalog is fighting. The history counsels caution: the
program's 2018 Nature paper claiming Majorana signatures was **retracted**
(2021) after data-analysis problems.

## 2 · The claimed qubit

**Majorana 1** (Feb 2025): a "topoconductor" chip — InAs/Al nanowire
devices claimed to host Majorana zero modes at each end, arranged into
**tetrons** (four Majoranas = one qubit), with **8 qubits** on the
announced chip. Operations are measurement-based: instead of pulsing
fields, you measure joint parities in sequences. **Majorana 2** (Jun 2026)
claims >1,000× stability improvement and quantum-state lifetimes beyond
20 seconds. Note the systematic absence in both announcements: no published
demonstration of coherent *qubit operation* — no Rabi oscillations between
the computational states, no gate, no algorithm.

## 5 · The numbers

| Metric | Value | Source quality |
|---|---|---|
| Claimed qubits (Majorana 1) | 8 | vendor |
| Claimed state lifetime (Majorana 2) | >20 s | vendor, unpublished |
| Independently verified qubit operations | **0** | — |
| Retracted papers in program lineage | 1 (Nature, 2021) | record |

## 6 · Error correction status

The roadmap (with DARPA US2QC involvement) projects scaling tetron arrays
toward fault tolerance by ~2029 — but the unit being scaled has not been
publicly demonstrated *as a qubit*.

!!! danger "⚔ The skeptic's box — here, the main text"

    This is what [`status: contested`](index.md#status-vocabulary) looks
    like in detail:

    - **Henry Legg's Nature "Matters Arising" (2026)** argues the
      topological-gap protocol (TGP) — the measurement underpinning the
      Majorana claim — involves data selection: analysis code highlighting
      the largest purportedly topological region while omitting other
      regions that also passed tune-up, plus inconsistencies against the
      underlying transport data.
    - **Sergey Frolov (Pittsburgh)** — a central figure in exposing the
      2018 retraction — publicly assesses the 2025 paper as having "no
      scientific value." Not a fringe voice: the referee reports published
      alongside the Nature paper themselves flagged that the paper does
      not demonstrate a topological qubit.
    - **The epistemic structure is the problem:** the topological gap is
      *inferred through a protocol that presupposes it*, rather than shown
      directly. Until an independent, protocol-free demonstration exists —
      or simple coherent qubit operation data is published — the claim
      floats. Microsoft says such data exists, unpublished; in this
      repository's [rules](../ROADMAP.md), unpublished evidence is not
      evidence.
    - **Score the asymmetry honestly:** if right, this program leapfrogs
      the entire catalog. If wrong, it will have consumed two decades on a
      quasiparticle that keeps being mistaken for disorder. Both remain
      live possibilities in 2026-07.

## 7 · Sources

- [Scientific American on Legg's critique](https://www.scientificamerican.com/article/top-quantum-computer-expert-claims-microsofts-topological-qubit-doesnt-hold-up/)
- [Science: "Doubling down on controversial claims"](https://www.science.org/content/article/doubling-down-controversial-claims-microsoft-accelerates-quantum-computing-plans)
- [Majorana 2 coverage (Jun 2026)](https://thequantuminsider.com/2026/06/02/microsoft-reports-advances-in-majorana-2-following-debate-over-last-years-topological-claims/)
- Microsoft's side: [Majorana 1 announcement](https://news.microsoft.com/source/features/innovation/microsofts-majorana-1-chip-carves-new-path-for-quantum-computing/)
