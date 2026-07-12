# The Machines

**A field guide to every working quantum computer in the world — who builds
it, what the qubit physically is, how the architecture works, and what the
classical attack said about its headline claims.**

> You cannot hunt hardware-realizable advantage without knowing the hardware
> cold. This catalog exists so that "runs on near-term devices" is never a
> hand-wave in this repository — it is a specific machine, with a specific
> error rate, a specific connectivity, and a specific clock.

This is a side track of the [main roadmap](../ROADMAP.md), held to the same
rules as everything else here: **every number has a source**, vendor claims
are labeled as vendor claims, and every flagship result is paired with what
the strongest classical baseline did to it. All specs live in one data file —
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml)
— and every table and figure on these pages is generated from it by
[`scripts/make_machine_figures.py`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/scripts/make_machine_figures.py).
Nothing is hand-copied, so nothing can silently drift.

## The landscape in one picture

Two numbers locate a gate-based machine: how many qubits it has, and how
badly its two-qubit gates fail. Everything else — coherence, connectivity,
clock speed — matters through these two.

![The machine landscape: qubits vs two-qubit error](fig-landscape.svg#only-light)
![The machine landscape: qubits vs two-qubit error](fig-landscape-dark.svg#only-dark)

Read it like a map:

- **The gray band is death.** Above ~1% two-qubit error, surface-code error
  correction makes things *worse*, not better. Everything interesting happens
  below it.
- **Trapped ions own the bottom** (quality), **superconductors own the
  middle-right** (scale × speed), and the **neutral-atom point is deceptive** —
  its 0.5% is the *physical* Rydberg CZ, but its 448 atoms encode 96 *logical*
  qubits, a different game entirely.
- The hollow marker is a **design spec, not a measurement** — a distinction
  vendor slide decks like to blur.

## The depth budget

A better single number than qubit count: **how many two-qubit gates can run
before the first error is expected** — simply 1/ε. This is the machine's
entire circuit budget, to be spent on your algorithm *and* on any error
correction overhead.

![Depth budget per machine](fig-depth.svg#only-light)
![Depth budget per machine](fig-depth-dark.svg#only-dark)

This is why nobody serious brags about raw qubit count anymore: a 1,000-qubit
machine with a 200-gate budget cannot even entangle all of its own qubits
once.

## How we got here — and where the race turned

![Flagship machines by year](fig-timeline.svg#only-light)
![Flagship machines by year](fig-timeline-dark.svg#only-dark)

The visible knee in 2023 is the field's most important strategic event: IBM
shipped the 1,121-qubit Condor, learned what it needed to, and then **shipped
smaller chips** (Heron 156, Nighthawk 120). The race stopped being about
count and became about the depth budget above — and about this:

![Logical qubits demonstrated by year](fig-logical.svg#only-light)
![Logical qubits demonstrated by year](fig-logical-dark.svg#only-dark)

Logical qubits — error-corrected qubits that outlive their own components —
are the number to watch from here on. Note who leads it: **neutral atoms**,
the platform that was an academic curiosity five years ago.

## The catalog

--8<-- "machines/_table.md"

Each machine page follows a fixed autopsy template, same discipline as the
[algorithm autopsies](../curriculum/00-curriculum.md): **who & lineage → the
qubit → how gates happen → system architecture → the numbers → error
correction status → ⚔ the skeptic's box → roadmap & sources**. The skeptic's
box is the section no vendor page will give you: what happened when the
strongest classical methods attacked the machine's flagship claim.

Before reading any machine page, read **[how to read a spec sheet](metrics.md)**
— it is the difference between memorizing vendor numbers and being able to
smell what they omit. Then read **[the gap](gap.md)** — the page that asks
whether *any* of these is yet a quantum computer in the theoretical sense,
and answers with arithmetic: the census of algorithm-grade logical qubits
across the entire industry is currently **zero**, and every advantage claim
since 2019 is scored there against the classical attack that followed it.

## Status vocabulary

| Status | Meaning |
|---|---|
| `deployed` | commercially accessible (cloud or on-prem), running user workloads |
| `prototype` | operational in the lab; results published; not generally accessible |
| `research` | a physics testbed, not a computer — no system-level algorithm demos |
| `contested` | central claims disputed in the peer-reviewed literature |
| `announced` | does not exist yet; treat all numbers as marketing |
| `retired` | no longer operating; kept for the historical record |

## Freshness

This field moves monthly. Every page carries the `data.yml` stamp
(**specs as of 2026-07**) and each spec was verified against
primary sources on the date of the page's last commit. If a number looks
stale, it probably is — check the source links and the git history.
