# The gap — is any of this a quantum computer?

**The critical analysis the catalog's descriptive pages point toward: what
the machines actually are, measured against the theoretical object they are
marketed as, with the arithmetic shown.** *As of 2026-07; every number
sourced in [`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml)
or derived in [`make_machine_figures.py`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/scripts/make_machine_figures.py).*

Companies underreport what follows because it prices their stock; academic
groups underreport it because "we are 10⁴ away from the goal" doesn't renew
grants. This repository has neither problem. What follows is not cynicism —
several results below are genuinely great physics, and we say so — it is
the ledger a buyer of the *future* would demand.

---

## 1 · The theoretical object, and the census

"Quantum computer," in the sense every marketing claim borrows its meaning
from, is a precise theoretical object: a machine executing a **universal
gate set** on qubits whose errors are (i) below the fault-tolerance
threshold and (ii) shaped like the threshold theorem assumes — local,
uncorrelated, Markovian — so that logical error can be suppressed to any
target at **polylogarithmic overhead**. That machine runs Shor. That
machine is what "quantum computers will break RSA" refers to.

Score today's platforms against that object, criterion by criterion:

| Criterion | Supercond. | Trapped ion | Neutral atom | Photonic | Analog (D-Wave, GBS, Rydberg-sim) |
|---|:-:|:-:|:-:|:-:|:-:|
| Universal *physical* gate set | ✓ | ✓ | ✓ | ✓ (MBQC) | **✗ — by design** |
| Init & measurement (incl. mid-circuit) | ✓ | ✓ | ~ | ~ | ✓/n.a. |
| Coherence ≫ gate time | ~ (10³–10⁴) | ✓ (10⁴⁺) | ~ | ✓/✗ (loss) | n.a. |
| Below-threshold error correction shown | ✓ (1 memory) | ~ (codes + post-selection) | ✓ (memories) | ✗ | ✗ |
| **Universal *fault-tolerant* gate set shown** | **✗** | **✗** | **✗** | **✗** | **✗** |
| Noise matches threshold-theorem assumptions | ✗ (bursts, drift) | ~ | ~ (loss ≈ erasure, favorable) | ~ (loss heralded) | n.a. |
| Scaling demonstrated *while holding error* | ✗ (count went **down**) | ✗ | ~ (count up, fidelity unpublished) | ✗ | ✗ |

The fifth row is the verdict row, and it is unanimous. **By the definition
the marketing implies, the number of quantum computers on Earth in 2026-07
is zero.** What exists: superb physics experiments converging on prototypes
(the gate-based platforms), one genuinely historic below-threshold memory
([Willow](google.md)), logical-qubit *memories* accumulating fast
([QuEra–Harvard](quera.md)), and a family of analog machines that are not
on the path to the theoretical object at all and should never be counted
in the same column.

Honesty cuts the other way too: **zero is not the interesting number — the
derivative is.** Two-qubit error fell ~100× in fifteen years; Willow's
Λ = 2.14 means bigger codes now help instead of hurt; 96 logical memories
exist where zero did three years ago. The gap below is closing. It is also
still a *gap*, and its size is never printed on a slide.

## 2 · The gap, computed

Take each machine's own published two-qubit error, apply standard surface-code
arithmetic (the same scaling every vendor roadmap privately uses), and ask:
**how many logical qubits good enough for a useful algorithm (10⁻¹² per
operation) does this machine contain right now?**

--8<-- "machines/_gap.md"

Every row says **0**, including the best machine ever built. And the
right-hand column of the same arithmetic — what RSA-2048 needs — is ~10⁶
physical qubits *at* 10⁻³ error. Plotted:

![The computed gap between today's machines and useful fault tolerance](fig-gap.svg#only-light)
![The computed gap between today's machines and useful fault tolerance](fig-gap-dark.svg#only-dark)

Read the distances: the cluster marked "every quantum computer on Earth"
must travel **~4 orders of magnitude in qubit count while simultaneously
holding or improving error rates** — and count-vs-quality has so far been a
trade-off, not a conjunction: the only vendor that built a 1,000-qubit chip
([Condor](ibm.md)) shelved it, and the machines that hold the best error
rates are the *smallest*. No platform has yet demonstrated the conjunction,
and the conjunction is the whole game.

Two more honest annotations on that figure:

- **The frontier is optimistic.** It counts no magic-state factories, no
  routing overhead, no correlated-noise penalty (§3). Real machines will
  need to land *deeper* inside the shaded region than drawn.
- **Extrapolation is not well-defined.** "Qubits double every N months"
  died in 2023 when the leaders deliberately stopped scaling count.
  There is no Moore's law here; there is a hard co-optimization problem
  with unknown rate.

## 3 · The noise the theorem doesn't cover

The threshold theorem — the entire justification for "errors are fine,
we'll correct them" — assumes noise that is local, independent, and
stationary. Real machines violate all three, and this is the fine print
with the highest stakes:

- **Correlated bursts.** Cosmic-ray muons and ambient radioactivity create
  quasiparticle bursts on superconducting chips that collapse T1 across
  large regions **simultaneously** — measured at roughly one event every
  ~10 seconds on Sycamore-class devices (McEwen et al., *Nature Physics*
  2022). A distance-*d* surface code protects against *d*-qubit accidents;
  a chip-wide burst is not an accident the code can price. Gap engineering
  reduces the rate; nobody has demonstrated it dead at scale. Every
  superconducting fault-tolerance roadmap carries this asterisk silently.
- **Drift.** Two-level-system defects migrate hourly; the fidelity in the
  paper is the fidelity *at calibration time*. Fleet medians sit below
  paper numbers as a rule, which is why this catalog prefers fleet data and
  flags hero numbers ([primer §3](metrics.md#3-gate-fidelity--where-the-bodies-are-buried)).
- **Leakage.** Transmons leak to |2⟩, atoms leave the trap, ions heat.
  Leakage is outside the code space — the code doesn't see it — and the
  machinery to flush it (reset, reload, re-cool) costs the cycles that
  wall-clock numbers quietly omit. The favorable exception: platforms where
  loss is *heralded* (photonic dual-rail, atom imaging) convert their worst
  error into their cheapest one — a genuine structural advantage.
- **Consequence:** the ~1% "threshold" is a theorem about textbook noise.
  Against real noise the effective threshold is lower and partly unknown —
  Λ = 2.14 measured at d ≤ 7 is *evidence*, not *proof*, that Λ > 1 holds
  at d = 25. That extrapolation is load-bearing for every 2029 roadmap and
  is tested nowhere.

## 4 · Error mitigation is a loan, not income

Everything impressive done on today's NISQ hardware at depth — IBM's
utility experiments above all — runs on **error mitigation** (zero-noise
extrapolation, probabilistic error cancellation). The part rarely said out
loud: mitigation's sampling cost grows **exponentially** in circuit volume.
This is not an engineering gripe but a theorem — exponential lower bounds
on mitigation overhead are proven (Quek, França, Khatri, Meyer, Eisert,
*Nature Physics* 2024, and the surrounding no-go literature).

Translation: mitigation buys a *fixed, small* circuit-volume window just
past the bare-hardware budget, at exponential classical cost. It is
legitimate near-term science inside that window and **a mathematical dead
end as a scaling strategy**. When a roadmap presents mitigated results as
progress toward quantum advantage, it is mixing two currencies with
different exchange rates — check which one a claim is denominated in.

## 5 · The missing gate

"Below threshold" — the field's proudest 2024 result — is a statement about
a quantum **memory** running **Clifford** operations. The theoretical
machine needs one more thing, and it is the thing nobody has shown:

- **A fault-tolerant non-Clifford gate** (the T gate) — via magic-state
  distillation or cultivation. Status across all platforms, 2026-07:
  theory strong, small demos only. **No platform has executed a single
  fault-tolerant universal logical operation end-to-end.** Every logical
  demo in the [milestones chart](index.md#how-we-got-here--and-where-the-race-turned)
  is Clifford circuits, error-*detecting* codes, or post-selected.
- **Logical clock arithmetic** vendors never print: a distance-25 logical
  operation needs ~25 syndrome rounds ≈ 25 µs on superconducting hardware —
  a ~40 kHz logical clock, before distillation multiplies it. Ion and atom
  platforms divide by another 10³–10⁴. "Logical qubits" without a logical
  clock rate is half a spec.
- **Decoding bandwidth:** a 10⁶-qubit machine emits syndrome data at
  ~TB/s that must be decoded in real time, forever. Willow's real-time
  d = 7 decoder is the state of the art; the requirement is four orders
  beyond it.
- **Post-selection fine print:** several celebrated logical demos discard
  a large fraction of shots ("error-detected" ≠ "error-corrected"), with
  the discard fraction in the supplement. Any logical claim without its
  discard rate is an advertisement
  ([primer §6](metrics.md#6-logical-qubits--the-new-number-and-its-new-games)).

## 6 · The claim ledger

Every headline "beyond classical" claim since 2019, scored against the best
classical answer today. This table is the single strongest argument for
this repository's entire methodology:

--8<-- "machines/_claims.md"

The patterns are mechanical:

1. **Unverifiable claims decay.** Median half-life of an attacked sampling
   claim: ~2 years. The classical baseline is a moving target that moves
   *fastest exactly where a headline paints it*.
2. **The survivor is instructive.** The one claim that has beaten back a
   serious attack ([Quantum Echoes](google.md)) is the one built around a
   *checkable* quantity. Verifiability isn't a nicety — it is the moat.
3. **Nothing on this list is useful.** Twelve claims, zero applications.
   Every task was chosen because the machine could do it, not because
   anyone needed it — benchmarks *defined as* what the hardware does.
   The claim that matters — advantage on a problem someone already wanted
   solved, with hardness that has a mechanism — has never been made by any
   vendor. (Making one is [this repository's actual program](../hunt/README.md).)

## 7 · The incentive audit

None of this is conspiracy; all of it is incentives. Knowing *which*
numbers each party is paid to hide tells you exactly where to look:

**What companies systematically omit** — calibration-day fidelities quoted
as steady-state; fleet medians hidden behind hero pairs; wall-clock and
shots-per-second (the number that makes ion fidelity records and
superconducting speed records incomparable); analog counts placed next to
gate-model counts; design specs typeset like measurements; roadmap
slippage (PsiQuantum 2025→2027-8; IBM's old 4,000-qubit-by-2025 chart,
quietly replaced — to their credit — by the quality pivot; a decade of
Majorana timelines). The tell is always the same: **the denominator is
missing.**

**What researchers systematically omit** — baselines tuned to lose
(the [Aquila MIS speedup](quera.md) died against *properly tuned* simulated
annealing, not against new physics); benchmarks chosen after the machine
exists (RCS is, definitionally, the thing the chip does); post-selection
fractions in supplements; the file drawer of runs that showed nothing; and
a replication vacuum — hardware claims are almost never independently
re-run because access is gatekept by the claimant. Peer review checks the
analysis, not the machine.

**The shared game** is milestone inflation: "supremacy" (2019) became
"utility" (2023) became "verifiable advantage" (2025) — each term coined
at the moment the previous one was classically matched. Track the object,
not the noun.

## 8 · What real progress would look like

Falsifiable milestones, resistant to the games above. When one of these
lands, the gap is actually closing; until then, it's engineering progress
inside the gap:

1. **Λ ≥ 2 sustained at d ≥ 15** with leakage handling and burst events
   included, no post-selection — on *any* platform.
2. **A fault-tolerant T gate** with logical error below physical, discard
   fraction printed in the abstract.
3. **Two logical qubits, entangled, running an algorithm end-to-end** at a
   stated logical clock ≥ kHz and logical error ≤ 10⁻⁶.
4. **An advantage claim with efficient verification or a hardness
   reduction** — [the standard this repo demands of itself](../hunt/README.md) —
   surviving 24 months of motivated classical attack.
5. **Continuous public calibration telemetry** (drift included) and
   pre-registered benchmarks against *adversarially tuned* classical
   baselines at matched wall-clock and watts.
6. A vendor roadmap that lists its **missed** milestones next to its
   future ones.

Nothing on this list is unreasonable; nothing on this list has happened.
That sentence is the state of the field in 2026-07 — and the reason the
[Hunt](../hunt/README.md) attacks the problem from the theory side rather
than waiting for the hardware to arrive.
