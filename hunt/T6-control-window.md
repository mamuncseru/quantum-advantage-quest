# T6 — The control window: evaluation hardness with a trainable landscape

**Final status (2026-07-18, after three same-day self-attacks): CLOSED
as a variational candidate.** K4 killed the 1D instance (bond-32 MPO);
the 2D form hardened (whole surrogate ladder fails — real, and kept as
an oracle-cost measurement); then **K6 dissolved the variational
identity: random search at matched oracle budget beats gradient
training 0.79 to 0.60** — the landscape is not load-bearing, only the
(already-known-hard) simulation oracle is. The briefly-claimed "first
live window of ground T" is retracted in §K6 below; what survives is a
boundary note and the sharpest form of the ground's meta-lesson.

**Pre-registered and opened 2026-07-18**, ground T, sixth candidate —
**and the ground's first survivor of first contact.** The order
objective closed like every face before it; the heating objective met
the pre-registered survival condition on both cost proxies *and* the
operational check: budget-limited surrogate-driven optimizers fail —
non-monotonically in budget — to follow the exact-driven ascent.
**No advantage is claimed.** Survival means: the pre-registered
follow-up attacks are now owed, and they are listed below.

## Why this formulation (dodging the concentration trap)

Naive "evaluation-hardness" losses die instantly: circuits with
classically-hard expectation values usually have exponentially
*concentrated* values, so the constant-0 surrogate passes
additive-error evaluation. The honest instance is **quantum optimal
control**: few parameters ($K = 6$ — barren plateaus cannot apply),
loss = a physical response after real-time dynamics (O(1) values —
concentration cannot apply), and the evaluation oracle is Hamiltonian
dynamics — the one task whose classical-hardness pedigree is
BQP-completeness. Graveyard-compliant: no classical-data QML anywhere;
the mechanism is the field's most solid.

> **Q(T6).** Does gradient-following on physical control objectives
> steer the dynamics *into* the classically expensive region (cost
> proxies growing above the random-control baseline while gradients
> stay O(1)) — or do optimizers avoid scrambling here as they did in
> every previous face?

## Instrument

$n=10$ chain, $H$ = TFIM($g{=}1$)+$0.4ZZ'$, staggered-$Z$ drive in
$K=6$ piecewise-constant segments, Trotterized ($3\times$ dt $=0.1$
per segment; the Trotter circuit *is* the model); start state = ground
state of $H$. Three arms cross-validated to machine precision before
any experiment (statevector, truncated backward propagation, dense
Heisenberg conjugation) — after two caught ordering bugs (Trotter
gate-order and conjugation direction; both found by the exactness
checks, both pinned by tests). Proxies: $N^*$ (Pauli budget, ladder
capped 8192) and $S_{\rm op}$ (operator entanglement of the evolved
objective at the middle cut). Code:
[`code/t6_control_window.py`](code/t6_control_window.py), 5
[tests](code/test_t6_control_window.py); CSV:
[`t6-control-scan.csv`](../hunt/t6-control-scan.csv).

## Results (gradient ascent, 30 steps; baselines = 8 random-θ draws)

**Objective A — restore order (maximize staggered magnetization):
closes.** $N^*$ pinned at the baseline (8192 throughout); $S_{\rm op}$
*decreases* along training (3.33 → 3.18, baseline 3.28). Ordering
objectives steer toward classically-visible dynamics — face-consistent.

**Objective B — heating (maximize $\langle H\rangle$ from the ground
state): survives.**

| t | $\langle H\rangle$ | $\lvert\nabla\rvert$ | $N^*$ | $S_{\rm op}$ |
|---:|---:|---:|---:|---:|
| 0 | −11.63 | 0.77 | 128 | 1.36 |
| 10 | +3.56 | 1.52 | 2048 | 2.84 |
| 30 | **+7.06** | 0.85 | **>8192 (saturated)** | 2.86 |
| *baseline* | — | — | *median 2048* | *median 1.57, max 1.94* |

Training pumps ~19 energy units with healthy gradients while both
proxies exceed the entire baseline range — the optimizer is *choosing*
the classically expensive dynamics because the objective rewards it.

**K3 — the operational check (the decisive one):** identical
gradient-ascent policy, loss oracle swapped for the budgeted surrogate;
scored by the TRUE $\langle H\rangle$ of the parameters found:

| driver | true $\langle H\rangle_{\rm final}$ |
|---|---:|
| exact oracle | **+7.06** |
| surrogate, N=512 | +0.75 |
| surrogate, N=2048 | −1.48 |
| surrogate, N=8192 | **−1.13** |

The budget-512 optimizer achieves a tenth of the pumping; **larger
budgets do *worse* than 512** — across a 16× budget range the
truncated landscape is not a noisy copy of the true one but a
*different* landscape with different optima. This is the first
operational separation in ground T, and it is robust across the entire
ladder that closed all five previous faces.

## K4-t6 delivered (2026-07-18, same day): the MPO attack LANDS at n=10

The pre-registered "most dangerous" attack was built
([`code/t6_mpo_attack.py`](code/t6_mpo_attack.py), hand-rolled MPO
machinery validated to $2\times10^{-14}$ at the $n=6$ exactness point,
5 [tests](code/test_t6_mpo_attack.py); two construction bugs — an FSA
boundary gate and 0-based leg arithmetic — caught by the dense
cross-checks before any attack number was produced) and run along the
exact heating trajectory:

| t | exact $\langle H\rangle$ | MPO error at $\chi$ = 4 / 8 / 16 / **32** / 64 |
|---:|---:|---|
| 0 | −11.63 | 0.26 / 0.11 / 0.04 / **0.012** / 0.000 |
| 10 | +3.56 | 0.49 / 0.58 / 0.06 / **0.043** / 0.007 |
| 30 | +7.06 | 0.34 / 1.30 / 0.26 / **0.008** / 0.006 |

**At the point where Pauli truncation saturated its whole ladder
(>8192 terms), a bond-32 MPO — 3% of the exact bond 1024 — evaluates
the loss to 0.008.** The K3 separation was real but
Pauli-truncation-specific: the evolved-Hamiltonian objective has a flat
Pauli coefficient spectrum (magnitude truncation's worst case) and low
operator entanglement (the MPO's best case). The intermediate
entanglement barrier did not materialize at this size.

**Verdict: the 1D instance at $n \le 10$ is closed.** T6 survives only
in its pre-registered narrowed form (written in this brief *before* the
attack ran): **≥2D or long-range dynamics**, where bond dimension must
grow with the cut and tensor-network surrogates lose their guarantee —
which is exactly where the field's Hamiltonian-simulation advantage
consensus lives. The candidate's fate now matches the field's own map:
1D dynamics is classical (TN); the window, if it exists, is
higher-dimensional. Building the 2D instrument (4×4, 4×5 statevector)
is the continuation gate.

## The 2D continuation (2026-07-18, same day): the hardening condition FIRES

The narrowed form was tested immediately: same protocol on a **4×4
lattice** ($g = 3$, near the 2D critical point; snake-ordered MPO with
vertical bonds as long-range couplings — the machinery ports because
the P-sandwich uses only single-site multiplications; gate: exact at
2×3 to $1.6\times10^{-13}$). Code:
[`code/t6_2d_scan.py`](code/t6_2d_scan.py), 4
[tests](code/test_t6_2d_scan.py).

| t | $\langle H\rangle$ (frac of span) | $\lvert\nabla\rvert$ | Pauli $N^*$ | MPO err @ χ=32 / 64 / **128** |
|---:|---:|---:|---:|---|
| 0 | −47.5 (0.03) | 4.8 | 2048 | 0.77 / 0.47 / 0.58 |
| 10 | +8.9 (0.59) | 5.4 | **saturated** | 0.28 / 0.30 / 0.33 |
| 30 | +9.7 (0.60) | **21.0** | **saturated** | 1.75 / 0.66 / **0.32** |

**$\chi^*(t{=}30) > 128$ — the pre-registered hardening threshold
(≥128) fires with the whole ladder failing**, robustly under both
tolerance readings (0.2 = the 0.0125n convention; even at a relaxed
0.5, $\chi^* = 128$ exactly). The bond-32 surrogate that demolished 1D
misses by 1.75. Meanwhile the 6-parameter landscape is not merely
trainable but *steep* ($|\nabla| = 21$ at the heated endpoint).

**The honest nuance the data adds:** $t=0$ is *also* beyond the ladder
— in 2D at $T = 1.8$ near criticality there are no classically cheap
regions on this trajectory, trained or not. The "optimizer steers into
hardness" framing (the 1D question) gives way to the sharper true
shape of T6: **the evaluation oracle is dynamics-intrinsically hard
(the BQP pedigree, now visible in the proxies), and the control
structure contributes what no other T-candidate had — a few-parameter,
BP-free, non-concentrated, steep landscape sitting on top of that hard
oracle.**

*(Superseded the same day: this window was retracted by the K6 attack —
see [K6-t6](#k6-t6-delivered-2026-07-18-same-day-the-variational-identity-dissolves).
The status below is kept as it was recorded.)*

**Status: T6-2D stands — the first live window of ground T.** Owed
before the word "advantage" is ever used: the width scan (4×5, 4×6 —
$\chi^*$ growth with the cut is the real scaling statement); a
dedicated high-χ/PEPS attack session (128 is 0.2% of the exact 2D
bond — the ladder is nowhere near exhausted); the random-θ 2D baseline
(to quantify dynamics-intrinsic vs training-steered hardness); K6 task
sharpening; and the human gate over everything.

## K6-t6 delivered (2026-07-18, same day): the variational identity dissolves

The task-sharpening attack asked whether the *trained landscape* is
load-bearing, at matched oracle budget (390 calls) on the 4×4 instance:

| strategy | oracle calls | final $\langle H\rangle$ | frac of span |
|---|---:|---:|---:|
| gradient descent (the T6 protocol) | 390 | +9.66 | 0.60 |
| best periodic drive (grid of 40) | 40 | +12.93 | 0.63 |
| **random search** | **390** | **+28.81** | **0.79** |

**Random search at the same query budget beats gradient training by a
wide margin.** The landscape is not what earns the pumping — *any*
oracle-driven strategy does as well or better; gradients are neither
necessary nor even competitive here. What remains load-bearing is
exactly one thing: the **evaluation oracle** (2D real-time dynamics,
whose classical cost the K4/width instruments quantify).

**Verdict: T6's specifically-variational content is dead.** A
classically-hard simulation oracle inside a classical outer search loop
is the field's *standard* known advantage shape (quantum simulation as
subroutine), not a trainability result — and ground T is about
trainability. What survives of T6 is a boundary note, not a window:
control-type objectives place their oracles in the classically-hard
regime (measured: whole surrogate ladders fail in 2D), but nothing
about *training* is special once you're there. The "first live window
of ground T" framing is **retracted**; the window belongs to
Hamiltonian simulation, where the field already keeps it.

**What this means for ground T** — the meta-lesson reaches its final
shape: across six candidates, *every* mechanism either collapsed into
its own classical surrogate (T1–T5) or collapsed into the underlying
non-variational oracle (T6). For linear losses, we found no
specifically-variational advantage anywhere. The surviving carve-out
in the whole ground remains [L3](L3-trainability-surrogates.md)'s
nonlinear-loss window — now genuinely the last door standing.

*(The running width scan retains value as oracle-cost quantification —
its verdict will be recorded as such, not as a window claim.)*

## ⚔ Standing attacks — owed before this means anything

1. **The MPO attack (most dangerous, most urgent).** $S_{\rm op}
   \approx 2.9$ bits = effective operator Schmidt rank ~8: a
   tensor-network surrogate with bond dimension ~tens likely tracks
   this at $n=10$. The Pauli-magnitude truncation may simply be the
   *wrong* classical algorithm for evolved Hamiltonians (flat
   coefficient spectra). Survival requires the *bond-dimension budget
   at matched pumping fraction to grow with $n$* — 1D at these sizes
   is MPS-country; the honest scaling question may need 2D or
   long-range models. Pre-registered as **K4-t6**.
2. **n-scaling** of both proxies at matched pumping fraction (the K3-t3
   analogue). Pre-registered as **K5-t6**.
3. **Control-specific classical methods** (Krylov/Magnus expansions,
   adiabatic/counterdiabatic shortcuts that reach the same
   $\langle H\rangle$ without following the landscape). The classical
   competitor need not imitate the optimizer — it needs only the
   *answer* (a heating protocol). Heating to mid-spectrum is easy
   classically (any resonant drive); heating to $\langle H\rangle =
   +7$ of $E_{\max}$ — pumping *coherently past* infinite temperature —
   is the part that needs the landscape. The task definition must be
   sharpened to "reach $\ge f\cdot E_{\max}$" with $f$ where naive
   protocols fail. Pre-registered as **K6-t6**.
4. **Trotter-model dependence** — the circuit is the model here;
   continuum-limit robustness unchecked.

## Kinships

The evaluation oracle is Hamiltonian simulation — the advantage
pedigree of the entire field ([machines/gap](../machines/gap.md) §
resource estimates; the natural hardware demonstrator is a
[feasibility-checked](../machines/toolkit.md) control experiment).
Response-function objectives are Quantum-Echoes-adjacent — the one
external advantage claim that has so far survived classical attack.
Access-model formalization would go through L10's QUALM frame. The
five closed faces are what make this survival *informative*: the same
instrument that killed five mechanisms did not kill this one.

## Pre-registration summary

- K1 (both objectives close): **did not fire** — A closed, B survived.
- K3 (operational): **separation found** — non-monotone in budget.
- Owed: K4-t6 (MPO attack), K5-t6 (n-scaling), K6-t6 (task
  sharpening vs classical control theory), plus the standing human
  gate over the whole ground.

## Ledger discipline

First survivor of ground T. Nothing is claimed; three pre-registered
attacks and one human gate stand between this and the word "window."
