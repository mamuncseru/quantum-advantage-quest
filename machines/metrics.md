# How to read a spec sheet

**The metrics vendors publish, what they actually measure, and how each one
gets gamed.** Read this before any machine page — the pages assume it.

*Specs discussed here are as of 2026-07 and sourced in
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*

## 0. The one plot to internalize

A quantum circuit with $m$ two-qubit gates succeeds (to first order) with
probability $(1-\varepsilon)^m$, where $\varepsilon$ is the two-qubit error
rate. This exponential is the entire economics of the field:

![Circuit success probability vs depth for different gate fidelities](fig-nines.svg#only-light)
![Circuit success probability vs depth for different gate fidelities](fig-nines-dark.svg#only-dark)

Each added *nine* of fidelity multiplies your usable circuit depth by ten.
No number of additional qubits does that. When a vendor announces "twice the
qubits" and is silent about fidelity, this plot is what they are hoping you
won't consult.

## 1. Qubit count — the vanity metric

The number in every headline, and the least informative one on the sheet.
Three separate inflations to watch:

- **Analog counts are not gate counts.** D-Wave's 4,400 annealer qubits,
  Aquila's 256 Rydberg atoms, and Jiuzhang's 1,024 photonic modes live in
  restricted computational models. Comparing them to 98 gate-model qubits is
  a category error (the catalog table marks these †).
- **Trapped ≠ computing.** "1,180 atoms in an array" means 1,180 trapped
  atoms — the published entangling fidelity *at that scale* is the number
  that decides whether they compute.
- **Physical ≠ logical.** 448 physical atoms recently made 96 logical
  qubits; 105 physical transmons made 1. The exchange rate between the two
  columns is the entire fault-tolerance story.

## 2. Coherence — T1 and T2

- **T1** (relaxation): time for an excited qubit to decay. Sets the hard
  ceiling on everything.
- **T2** (dephasing): time until phase information is scrambled — this is
  the one algorithms feel, and T2 ≤ 2·T1 always.
- **T2\* vs T2 (echo):** T2\* is measured raw; T2-echo is measured while
  actively refocusing slow noise. Vendors quote the echo number. It is
  legitimate — but it is the *best case*.

Raw coherence spans six orders of magnitude across modalities (transmons
~100 µs, hyperfine ions and nuclear-spin atoms ~seconds to minutes). That is
**not** a six-order-of-magnitude advantage: what matters is the ratio
**coherence ÷ gate time**, and gates span the same six orders in the same
direction (transmon CZ ~50 ns, ion gates ~100 µs). Never compare coherence
across modalities without dividing by the clock.

## 3. Gate fidelity — where the bodies are buried

The headline number is almost always **two-qubit gate fidelity from
randomized benchmarking (RB)**. Questions to ask, in order of how often the
answer is disappointing:

1. **Median or mean? Best pair or fleet?** "Above 99.9% for >50% of pairs"
   (a real vendor sentence) means the median is somewhere *below* 99.9% and
   the tail is unspoken. The tail qubits are still on your chip and your
   compiler must route around them.
2. **Isolated or parallel?** Gates benchmarked one-at-a-time dodge crosstalk.
   Parallel benchmarking (all gates firing, as in a real circuit) is the
   honest number — credit to USTC for reporting Zuchongzhi 3.0 this way
   (99.62% parallel), and discount isolated numbers accordingly.
3. **RB or interleaved RB on the gate you'll actually use?** Plain RB
   averages over a gate set; a native-gate interleaved number is cleaner.
4. **Is SPAM excluded?** RB deliberately factors out state-preparation and
   measurement error — fair for gates, but your algorithm pays SPAM on every
   shot. A machine with 99.9% gates and 1% readout error is a 99% machine
   for shallow circuits.
5. **Spec or measurement?** "Designed to achieve 99.9%" is a sentence about
   intentions. The catalog marks design specs with hollow markers.

## 4. The depth budget — 1/ε

The most useful derived number: expected two-qubit gates before the first
error ≈ 1/ε. It converts fidelity into the unit you actually spend —
operations. The [landscape page](index.md) charts it for every machine with
a sourced ε. Two caveats: it ignores idling errors and crosstalk (real
budgets are smaller), and it assumes errors don't conspire (correlated error
bursts — cosmic rays on superconducting chips are a real example — break the
arithmetic entirely).

## 5. Holistic benchmarks — QV, CLOPS, EPLG, #AQ

Composite metrics exist because single numbers hide tails. Each solves one
problem and introduces another:

- **Quantum Volume (QV)** — largest square (depth = width) random circuit
  the machine passes. Honest about tails, but reported as $2^n$: "QV
  1,048,576" is a *20-qubit-deep* circuit wearing a seven-digit number.
  Trapped ions post huge QV partly because all-to-all connectivity flatters
  square circuits.
- **EPLG / layer fidelity (IBM)** — error per layered gate across a
  100-qubit chain; the honest fleet-scale successor to cherry-picked pair
  fidelities. Watch that the chain length matches the chip you're promised.
- **CLOPS (IBM)** — circuit layer operations per second: the *clock* metric.
  This is where superconductors dominate and QCCD ion machines pay for their
  fidelity: the gap is 3–4 orders of magnitude in wall-clock throughput.
  Any fidelity comparison that omits CLOPS-like numbers is half a comparison.
- **#AQ (IonQ)** — "algorithmic qubits": largest n for which a suite of
  n-qubit benchmark circuits passes, *with error mitigation allowed*. It is
  a vendor-defined metric, scored by the vendor, on benchmarks chosen by the
  vendor. Treat as an internal progress bar, not a cross-vendor unit.

## 6. Logical qubits — the new number, and its new games

"Logical qubit" now carries the hype that "qubit count" carried in 2019, so
the definitional games have started. When a vendor says *N logical qubits*,
ask:

1. **Created, entangled, or computed with?** Preparing N logical qubits in
   parallel, entangling them, and running an algorithm on them are three
   different milestones (roughly: Atom 2024, then Microsoft+Quantinuum,
   then the QuEra–Harvard 2026 demos).
2. **Error-detecting or error-correcting?** Detecting an error and
   post-selecting the shot away is far cheaper than correcting it live.
   Post-selected "logical" results quietly discard most of the data.
3. **Below threshold, or just encoded?** The Google Willow result matters
   because making the code *bigger* made errors *smaller* (Λ = 2.14 per
   distance step). An encoded qubit above threshold is worse than a bare one.
4. **What's the code rate?** A distance-7 surface code buys 1 logical qubit
   with ~100 physical; the QuEra [[16,6,4]]-family codes buy 6 per 16. Rate
   is why 448 atoms → 96 logical while 105 transmons → 1. The surface code
   pays its terrible rate back in threshold and locality — high-rate codes
   pay theirs back only if the hardware can do non-local gates, which is
   exactly what movable atoms can and fixed chips cannot.
5. **Logical clock and logical error rate?** The two numbers that will
   decide everything and are quoted the least.

## 7. Advantage claims — the special rules

When a machine page says *"claimed 10¹⁵× beyond classical"*, this repository
applies its own [verification protocol](../hunt/00-verification-log.md)
reflexes:

- **Sampling claims decay.** Sycamore 2019 (10,000 years → ~seconds after
  tensor-network spoofing), Jiuzhang 1/2 (loss-exploiting samplers),
  Borealis (partially matched), IBM Eagle "utility" (matched in weeks).
  The half-life of an unattacked supremacy claim has historically been
  about two years.
- **Verifiability is the moat.** Random-circuit and boson-sampling outputs
  can't be checked at scale — the claim rests on extrapolated fidelity.
  Claims with efficient verification (or classical-hardness reductions,
  the entire program of this repo) are a different species.
- **The baseline is a moving target.** Every claim on these pages is dated,
  because "beyond classical" is a statement about *today's* classical
  algorithms, and the [kill/keep ledger](../hunt/ledger.md) shows how fast
  those move when motivated.

The full scoreboard — every claim since 2019 against the classical attack
that answered it — lives in [the claim ledger](gap.md#6--the-claim-ledger).

## The checklist

When a spec sheet lands on your desk, in order:

1. Gate-based or analog? (If analog, stop comparing qubit counts.)
2. Two-qubit error: median, parallel, fleet-wide, measurement not spec?
3. Depth budget 1/ε — can it even run the circuit you care about?
4. SPAM error and readout — what do shallow circuits really cost?
5. Clock: gates/sec or CLOPS — divide all fidelity brags by wall-clock.
6. Connectivity: what does SWAP overhead do to your circuit on their graph?
7. Logical claims: created/entangled/computed? detecting/correcting?
   below threshold? what rate? what logical clock?
8. Advantage claims: verifiable? dated? has anyone competent attacked it yet?

Eight questions. Most spec sheets survive three.
