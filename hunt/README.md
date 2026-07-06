# The Hunt — Phase 2

*Opened 2026-07-06. Candidate generation on ground A (optimization-as-decoding)
and ground C (quantum Gibbs sampling). Phase 1 study continues in parallel —
the phases were deliberately overlapped to front-load AI-assisted groundwork.*

## Quality gates (every candidate, no exceptions)

1. **Verified footing.** No result is load-bearing until confirmed at the
   primary source. Status of every dependency: `00-verification-log.md`.
2. **Pre-registration.** Each candidate gets a brief BEFORE work starts:
   problem, advantage currency, hardness mechanism, named classical baseline,
   and a falsifiable **kill criterion** with a deadline.
3. **Symmetric effort.** The classical baseline is built and tuned with the
   same seriousness as the quantum side — Prange enhancements included.
4. **Access-model symmetry.** Whatever input access the quantum algorithm
   assumes, the classical baseline receives its sampling analogue (the Tang
   test, run against our own claims first).
5. **Kill/keep reviews** are written into `ledger.md` — a killed candidate
   gets a boundary note, not silence.

## The candidate board

| ID | Candidate | Ground | Status |
|---|---|---|---|
| [A1](A1-beyond-hamming.md) | DQI beyond Hamming: the covering-radius obstruction | A | active |
| [A2](A2-objective-code-reductions.md) | New objective→code reductions (flagship: CRT-OPI) | A | **active · primary** |
| [C1](C1-fields-and-mixers.md) | Field-induced hardness with rapid quantum mixing | C | active |
| [A∩C](AC-hdqi-boundary.md) | The HDQI vs classical-dynamics boundary | A∩C | watch |

## Tooling

- [`code/advantage_window.py`](code/advantage_window.py) — the DQI semicircle
  law (Eq. 6 of arXiv 2408.08292v5, formula verified against the paper's own
  quoted numbers *as unit tests*) and the Prange baseline; maps where the
  quantum–classical window opens as code/problem parameters vary.

<figure markdown="span">
  ![The DQI advantage window](fig-window.svg#only-light)
  ![The DQI advantage window](fig-window-dark.svg#only-dark)
  <figcaption>The gap between DQI (Berlekamp–Massey decoding) and Prange's
  algorithm on OPI, computed from the verified semicircle law. Reproduces the
  paper's numbers exactly (tests), then maps the window beyond the r/p = 1/2
  slice they plot.</figcaption>
</figure>

## Why these candidates (one paragraph each, honest priors)

**A2 is primary** because it follows the strongest meta-pattern in our catalog
— *the classical toolbox is a quantum resource* — into territory the DQI team
explicitly left open ("harvest the coding theory literature"), but aims past
the obvious harvest: not new codes for old objectives, but **new natural
problems** whose constraint structure lands on decodable codes. Flagship
candidate: transplant OPI from polynomials over $\mathbb{F}_p$ to residues
over $\mathbb{Z}/N$ (CRT codes have efficient decoders; noisy CRT is a
studied crypto primitive). **A1** was recast by our verification pass: the
rank-metric authors *disclaim* advantage due to a covering-radius obstruction
— so the open problem is the obstruction itself. **C1** builds on the
verified Bakshi–Tan result (hardness needs $\beta < 1$ + strong fields);
the seam is other knobs and the intermediate-$\beta$ regime, where we can
compute Davies/CKG gaps numerically on the 96-core node. **A∩C** (HDQI) is
verified and fascinating but one paper old — watch, verify deeper, enter
only with a sharp question.
