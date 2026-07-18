# T6 — The control window: evaluation hardness with a trainable landscape

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
