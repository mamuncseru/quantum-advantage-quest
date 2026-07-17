# T3 — The warm-start face: do trajectories outrun the surrogate?

**RESOLVED 2026-07-17, same day: no — K3 fired, and harder than
predicted.** The surrogate budget at matched training progress is
**flat** in $n$ (not merely polynomial): $N^* \le 512$ terms from
$n=6$ to $n=12$, $\alpha = -0.00$ bits/qubit ($R^2 = 1.00$) at
$p = 0.9$. See §Resolution.

**Pre-registered and opened 2026-07-17**, ground T, third candidate —
the door [T2](T2-dichotomy-theorem.md) left open by construction: its
theorem needs the deep/Haar regime and a poly DLA; **warm starts on
hardware-efficient ansätze have neither.** Trainability there comes
from initialization, not algebra; the matching classical surrogate is
truncated Pauli propagation (Angrisani/Rudolph-style), whose cost is
the number of Pauli terms retained. The question, trajectory-resolved:

> **Q(T3).** Along gradient-descent trajectories from warm starts, does
> the surrogate term budget stay polynomial wherever training makes
> progress (the dichotomy's third face — perturbative locality playing
> the role T2's module dimension played)? Or can a trajectory outrun
> every truncation while still descending?

Access symmetry as always: the classical side gets the same
initialization, the same loss oracle interface, the same step sequence.

## First numerics ($n=8$, RY+CZ hardware-efficient, 6 layers, 48 params)

Task: ground energy of TFIM($g{=}1$) + $0.4\sum Z_iZ_{i+2}$
(integrability broken; at these sizes everything is classically easy by
other means — the numerics measure the mechanism's budget, not
hardness). Engine: exact backward Pauli propagation with
magnitude-truncation; conjugation tables derived numerically at import
(no hand-derived signs); validated untruncated against statevector to
$8.9\times10^{-15}$. Code:
[`code/t3_warmstart_budget.py`](code/t3_warmstart_budget.py), 5
[tests](code/test_t3_warmstart_budget.py).

**E2 — trajectory budgets.** $N^*$ = minimal retained terms for loss
error ≤ 0.1 (of a 65,536-term Pauli space):

| init scale | best gap reached | $N^*$ along the whole trajectory |
|---|---:|---:|
| ε = 0.01 | 1.7% | ≤ 512 |
| ε = 0.10 | 1.7% | ≤ 512 |
| ε = 0.30 | 6.2% | ≤ 512 |
| uniform (BP control) | 11.7% (stalls) | ≤ 2048 |

Warm trajectories descend to ~98% of the ground energy and **never need
more than 0.8% of the Pauli space**. The BP control descends worse and
costs more — trainability and cheapness co-vary again, now via
locality rather than module dimension.

**E3 — the operational probe.** Shared-seed SPSA (identical
perturbation sequences), 300 steps, quantum-driven vs surrogate-driven,
scored by the **true** loss of the parameters each finds:

| | quantum | surrogate-driven (N=2048) | diff |
|---|---:|---:|---:|
| ε = 0.10 | −7.789 | −7.802 | 0.013 |
| ε = 0.30 | −8.347 | −8.234 | 0.113 |

(N=512 surrogate-driven reaches −8.55 / −8.55 — *better* true loss than
the quantum run, within SPSA noise.) At $n=8$, a classical optimizer
running entirely on the truncated surrogate finds parameters as good as
the quantum optimizer's, at every warm ε tested.

**Instrument note (kept, per house rules).** E3-v1 used a fixed SPSA
learning rate and produced a spurious quantum-vs-surrogate gap: the
exact loss's sharper landscape made fixed-step SPSA bounce while the
*smoother truncated* loss descended — an optimizer artifact, not an
information gap. Fixed with the standard Spall decaying gains; the
artifact is itself a caution for the literature, where
surrogate-vs-hardware comparisons with mismatched optimizer
hyperparameters can manufacture either conclusion.

## Pre-registration

- **Advantage currency (if it survives):** a warm-start trajectory
  family whose surrogate budget at matched progress grows
  superpolynomially in $n$ while gradient norms stay $1/\mathrm{poly}$
  — with the trajectory reaching loss values the budgeted surrogate
  provably cannot.
- **K1** (operational, per size): surrogate-driven descent matches
  quantum descent at fixed moderate budget for all warm ε. **FIRED at
  $n=8$** (E3 corrected). Size-limited: not yet a scaling statement.
- **K2** (BP control): uniform init must underperform warm inits —
  holds (11.7% vs 1.7% gap); the only trainable regime here is the warm
  one, so the question is warm-only. Consistent.
- **K3 (decisive, OWED):** $n$-scaling of $N^*$ at matched
  trajectory-progress (fixed fraction of ground-energy gap closed),
  $n = 6..12$, same protocol. Fires (T3 closes as the third face) if
  $N^*$ at matched progress grows ≤ polynomially; survives if the
  budget at fixed progress grows exponentially while gradients hold.
  Requires the engine's $n$-parameterization — next session's work.
- **K4** (smarter surrogates): if K3 does *not* fire, tensor-network
  and lightcone surrogates get a dedicated attack session before any
  claim.

## Kinships

T1/T2 closed the algebraic face (module dimension); T3 probes the
perturbative face (operator locality). If K3 fires, ground T will have
shown the same dichotomy emerging from two unrelated mechanisms — which
would itself be worth writing up as the ground's meta-lesson. The
remaining structurally distinct T-doors after that: nonlinear losses
(L3's, live), noise (T-slot), and adaptive circuit *growth* (data-
dependent structure — not covered by any face so far).

## Resolution (2026-07-17): K3 fired — the third face closes

The scan ([`code/t3_k3_scan.py`](code/t3_k3_scan.py), verdict
thresholds pre-registered in the header; CSV:
[`t3-k3-scan.csv`](t3-k3-scan.csv)): gradient-descent trajectories from
$\varepsilon = 0.1$ warm starts at $n = 6..12$, budget measured at
first crossings of 50%/90%/95% of the initial energy gap, tolerance
scaled extensively ($0.0125n$):

- $N^*$ at matched progress: **512 terms (occasionally 128) at every
  $n$** — of Pauli spaces growing from $4^6$ to $4^{12} = 1.7\times
  10^7$. At $n=12$ the surrogate tracks **0.003%** of the operator
  space while the trajectory closes 95% of the gap with healthy
  gradients ($|\nabla| = 1.9$).
- Fits at $p=0.9$: exponential model $\alpha = -0.00$ bits/qubit
  ($R^2 = 1.00$); the pre-registered fire condition
  ($\alpha < 0.5$, poly $\ge$ exp) is met with room to spare.

**Mechanism, stated:** warm-start trainability and truncation
surrogatability have the same cause — *the optimizer stays where the
Heisenberg representation of the loss is sparse.* The near-identity
region that keeps gradients alive is precisely the region where
backward propagation doesn't branch; descending toward a
quasi-local ground state never leaves it. Locality is doing here what
module dimension did in T1 and irrep dimension did in T2.

**Stated limits of the kill:** fixed depth (6 layers) — depth scaling
with $n$ is a named follow-up; trajectories reach 95% (not the last
stretch); $n \le 12$; plain GD (adaptive-*structure* methods are
outside — that door stays open and is the natural T4). One instrument
bug caught by cross-checks during the build: `np.bitwise_count`
returns uint8 and silently turns $-1$ into $255$ — pinned by a test as
a permanent warning.

## Ledger discipline

Opened and closed same day: K1 fired (operational, $n=8$), K2
consistent, K3 fired (flat budgets, $n \le 12$). Second same-day full
resolution in ground T; 10 pinning tests across the two instruments.
