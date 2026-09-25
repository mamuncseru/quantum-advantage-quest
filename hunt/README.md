# The Hunt — Phase 2

*Opened 2026-07-06. Candidate generation on ground A (optimization-as-decoding)
and ground C (quantum Gibbs sampling); ground L (learning with quantum data)
was added on 2026-07-11 and ground T (trainable circuits) on 2026-07-17.
Phase 1 study continued in parallel — the phases were deliberately overlapped
to front-load AI-assisted groundwork.*

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

Every candidate opened so far, with its latest decision. The dated reasons
are in the [kill/keep ledger](ledger.md); this table only summarizes them.

### Ground A — optimization as decoding

A2 is the program's lead candidate and moved to Phase 3
([Strike](../strike/crt-dqi-theorem.md)) on 2026-07-11.

| ID | Candidate | Standing | Last decision |
|---|---|---|---|
| [A2](A2-objective-code-reductions.md) | New objective→code reductions (CRT-OPI) | **In Strike.** Construction complete; survived adversarial pass 1 with two repairs; human proof check owed | 2026-07-12 |
| [A1](A1-beyond-hamming.md) | DQI beyond Hamming: the covering-radius obstruction | Narrowed to H1′ (the obstruction theorem); the Lee-metric circumvention is closed | 2026-07-08 |
| [A3](A3-p-polynomial-schemes.md) | Which P-polynomial schemes carry a hard objective? | **Closed (theorem):** among coordinate-decomposable metrics, Hamming is the only home for a DQI advantage | 2026-07-08 |
| A1∩A2 | The Lee-metric spine | **Killed:** the Lee metric is not an association scheme for $q\ge5$ ([note](notes/AC-lee-metric-KILLED.md)) | 2026-07-08 |

### Ground C — quantum Gibbs sampling

| ID | Candidate | Standing | Last decision |
|---|---|---|---|
| [C1](C1-fields-and-mixers.md) | Field-induced hardness with rapid quantum mixing | Active. The mixer gap stays open in the strong disordered-field regime ($n\le5$); the atlas doubles as L1's map | 2026-07-08 |
| [A∩C](AC-hdqi-boundary.md) | The HDQI vs classical-dynamics boundary | Watch, not active | 2026-07-06 |

### Ground L — learning with quantum data

Standings are from the first ground-L review (2026-07-11), updated where a
later entry exists.

| ID | Candidate | Standing | Last decision |
|---|---|---|---|
| [L1](L1-memory-vs-mixing.md) | Memory vs mixing | Keep (anchor). The (⇒) direction is proved | 2026-07-11 |
| [L2](L2-physical-noise-learning.md) | Physical noise learning | Keep, narrowed to static structured noise; the temporal suspect moved to L10 | 2026-07-11 |
| [L3](L3-trainability-surrogates.md) | Trainability vs surrogates | Keep, compute-gated. After ground T, its nonlinear-loss window is the last door standing | 2026-07-11 |
| [L4](L4-magic-transition.md) | The magic transition | Keep | 2026-07-11 |
| [L5](L5-noise-threshold.md) | Noise threshold of memory advantages | Kill 2 partially fired; now L1's NISQ-feasibility boundary | 2026-07-11 |
| [L6](L6-topological-shield.md) | Topological shield | Keep; absorbs L9 | 2026-07-11 |
| [L7](L7-symmetry-class-learning.md) | Symmetry-class learning | Probation | 2026-07-11 |
| [L8](L8-purification-dividend.md) | Purification dividend | Probation | 2026-07-11 |
| [L9](L9-certification-gap.md) | Certification gap | Merged into L6 | 2026-07-11 |
| [L10](L10-qualm-gap.md) | QUALM gap | Keep; absorbs L2's temporal suspect | 2026-07-11 |

### Ground T — trainable circuits

Every trainability mechanism tested carried its own classical surrogate
(T1–T5) or collapsed into the non-variational oracle underneath it (T6).
For linear losses, no specifically-variational advantage was found.

| ID | Candidate | Standing | Last decision |
|---|---|---|---|
| [T1](T1-module-dichotomy.md) | Module dichotomy | **Closed (K4):** barren plateaus and surrogatability share one cause | 2026-07-17 |
| [T2](T2-dichotomy-theorem.md) | The dichotomy theorem | Theorem at AI rigor; novelty pass and human verification owed | 2026-07-17 |
| [T3](T3-warmstart-face.md) | The warm-start face | **Closed (K3)** | 2026-07-17 |
| [T4](T4-adaptive-face.md) | The adaptive face | **Closed (K1)** | 2026-07-17 |
| [T5](T5-noise-face.md) | The noise face | **Closed (K1)** | 2026-07-17 |
| [T6](T6-control-window.md) | The control window | **Closed (K6);** the window claimed earlier that day was retracted | 2026-07-18 |
| [T10](T10-dqi-reachability.md) | DQI reachability | Resolved: K1 at toy scale; the open question passes to A2's write-up | 2026-07-18 |

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

## Why the first four candidates (2026-07-06, honest priors)

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
