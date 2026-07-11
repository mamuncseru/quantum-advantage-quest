# L5 — Noise robustness of memory advantages: is physical data the shield?

**Pre-registered 2026-07-11**, ground L, fifth candidate — and the
ground's own quality control: every L-candidate assumes clean quantum
memory; L5 asks what survives on hardware.

## The map as published (lit-checked first)

[Noisy Quantum Learning Theory (arXiv 2512.10929)](https://arxiv.org/abs/2512.10929)
(Dec 2025): the exponential two-copy advantage for purity testing
**collapses under local depolarizing memory noise** for worst-case
states; a superpolynomial NISQ-vs-fault-tolerant gap remains; one
AdS/CFT-motivated structure restores noise resilience. So the naive L5
question is answered. The seam is ours:

> **The L5 conjecture.** *Physical* structure restores noise robustness:
> for Gibbs states of local Hamiltonians the two-copy purity advantage
> survives **constant** storage noise, because thermal Pauli spectra are
> weight-concentrated and per-qubit depolarizing damages weight-$w$
> sectors by $(1-\gamma)^{2w}$. If true, L1's conditional advantage is
> NISQ-tolerant *because its data is physical* — the same locality that
> collapsed the sample separation (AAKS) is what shields the
> computational one from noise. One structure, both effects.

## First numerics (this session, exact)

Critical storage noise $\gamma^*(n)$ where the swap-test bias reaches
$\varepsilon = 0.05$, from exact Pauli weight spectra
([`code/noise_threshold.py`](code/noise_threshold.py)):

| ensemble | $\gamma^*$ log-log slope vs $n$ | mean Pauli weight at $n=7$ |
|---|---|---|
| Haar states | **−1.30** (the published collapse, reproduced) | 5.24 |
| Gibbs ($\beta = 1$, disordered Heisenberg) | **−0.42** | 4.31 |

Thermal structure already buys a factor-three flatter exponent at toy
sizes. Honest caveats: $n \le 7$; $\beta = 1$ is mildly entangled (the
conjecture predicts flatter still at higher $T$... and *steeper* at very
low $T$ — the robustness window and L1's advantage window may compete —
that tension is the scientifically interesting part).

## Pre-registration

- **Deliverable currency:** a theorem tying $\gamma^*$ to the weight
  concentration of the state family (cluster-expansion regime: constant
  $\gamma^*$ at high $T$ — likely provable), plus the map of the
  tension: L1 wants slow mixing (low $T$), L5-robustness wants weight
  concentration (high $T$) — **does a regime satisfy both?** That
  question is falsifiable and is the candidate.
- **Kill criteria:**
    1. Deep lit pass: 2512.10929's framework or follow-ups may already
       cover thermal ensembles — verify.
    2. The tension closes the window: if every slow-mixing family has
       Haar-like weight spectra (robustness dies exactly where the
       advantage lives) → merge into L1 as its NISQ-feasibility boundary,
       an honest negative.
    3. Mitigation trivializes it: if known-$\gamma$ rescaling restores
       any state family at poly cost, the threshold question is moot —
       check first (cheapest kill: the estimator-inversion is
       weight-resolved, and weight sectors are not separately observable
       from one swap statistic; but richer two-copy measurements may
       resolve them — verify before claiming).
- **First actions:** kill 3 check (weight-resolved mitigation); scan
  $\gamma^*$ vs $\beta$ at fixed $n$ (the tension curve); deep lit pass.
