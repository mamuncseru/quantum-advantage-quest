# T6 — The control window: evaluation hardness with a trainable landscape

**Status after the same-day K4 self-attack: the 1D instance is closed
by the MPO surrogate (bond 32 suffices at $n=10$); T6 persists only in
its pre-registered ≥2D/long-range form.** See §K4-t6 below.

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

| t | $\langle H\rangle$ | $|\nabla|$ | $N^*$ | $S_{\rm op}$ |
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
