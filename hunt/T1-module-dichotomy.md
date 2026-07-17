# T1 — The module dichotomy: is trainable always surrogatable?

**RESOLVED 2026-07-17, same day: yes, at the free-fermion point, in every
access model tested — K1, K2 and K4 all fired.** T1 closes as a boundary
result (an honest negative with a mechanism); see §Resolution at the end.

**Pre-registered 2026-07-17. Opens ground T** — trainable/parametric
quantum circuits, hunted under the graveyard rule: **no QML-speedup
claims on classical data, ever** ([ROADMAP](../ROADMAP.md)). Every
T-candidate is anchored on quantum data/dynamics or on mechanism-level
boundary results where a negative is a deliverable. The field's corpses
are all buried in this ground; that is exactly why a kill-criteria-first
sweep of it is worth ten candidates.

## Ground T — the provisional map (doors open doors; this list will change)

T1 (this brief) · the module dichotomy + the interleaved-dynamics window.
T2 · noise–trainability–simulability phase diagram (NIBP vs Pauli-path
simulability: is there a mid-noise window?). T3 · adaptive/warm-start
ansätze: does data-dependent circuit growth escape the dichotomy? T4 ·
training-cost economics when the trained model is classically
extractable. T5 · variational inversion of unknown dynamics vs
process-tomography lower bounds. T6 · loss-evaluation hardness with
benign landscapes (L9 kinship). T7 · the overparametrization transition
as a computational boundary. T8 · Born-machine training on
quantum-experiment distributions. T9 · equivariant PQCs vs classical
learners of the same symmetry class (kill-fast expected). T10 ·
variational reachability of DQI payoffs (landscape obstruction as a
theorem target; A2 kinship).

## The frontier

The Cerezo implication — *provable trainability ⇒ classical
surrogatability* — is the boulder blocking this entire ground
([L3](L3-trainability-surrogates.md) hit it from the nonlinear-loss
side). Its proven core: known no-BP mechanisms confine Heisenberg
dynamics to poly-dimensional invariant subspaces (poly-DLA ⇒
$\mathfrak{g}$-sim). Its open flanks, which T1 attacks with the access
model symmetrized (the surrogate gets single-copy access to the same
unknown inputs and query access to the same unknown box — never less):

> **Q(T1.1).** For linear losses on *unknown quantum inputs*, does
> trainability imply a surrogate at one-time poly measurement cost?
> **Q(T1.2).** Does the implication survive an *unknown black-box
> dynamics $U$ interleaved inside the trainable circuit* — the physical
> setting (device with untrusted internals, material sample in the
> loop) that no surrogate theorem covers?

## First numerics (exact, $n=6$, free-fermion/TFIM-DLA ansatz, module dim 66)

[`code/t1_module_dichotomy.py`](code/t1_module_dichotomy.py) — the ansatz
generators $\sum_i X_iX_{i+1}, \sum_i Z_i$ are Majorana quadratics; the
operator space splits into ad-invariant Majorana-degree sectors of
dimension $\binom{2n}{2k}$. (A first draft used $\sum X_i, \sum Z_iZ_{i+1}$
— *not* quadratic — and every check failed; the checks did their job.)

**A — Q(T1.1) resolved negative at the free-fermion point (kill K1
fired).** For a module observable on an unknown input, the
$\mathfrak{g}$-sim surrogate built from the 66 single-copy moments
$\langle i c_a c_b\rangle$ reproduces the on-device loss to
$1.6\times10^{-14}$, worst case over random $(\psi,\theta)$ — and the
moments are measured **once**, then reused for every $\theta$. The
surrogate is strictly *cheaper* than on-device training (which pays
shots per step). For first-order module losses on quantum data, the
Cerezo implication **extends**: honest negative, recorded.

**B — the variance law with fixed inputs.** Gradient variance per
degree sector next to the input's sector mass. Two exact structures
surfaced: (i) the degree-$2n$ sector (fermion parity) is an ad-invariant
singlet — its gradient is *identically zero* ($\sim10^{-22}$) while its
loss is a *constant*, i.e. perfectly surrogatable: the dichotomy in its
purest form; (ii) parity-conjugate sectors ($2k \leftrightarrow 2n-2k$)
show mirrored variances on a parity eigenstate input — measured, e.g.
$0.56/0.52$ (deg 2/10) and $0.20/0.29$ (4/8) on $|0^n\rangle$. At $n=6$
non-invariant sectors are all alive; the at-scale suppression is a
scaling question (owed, K4).

**C/D — Q(T1.2): the interleaved box.** Loss
$\langle\psi|V_1^\dagger U^\dagger V_2^\dagger O V_2 U V_1|\psi\rangle$
with $U$ a fixed unknown scrambler, input $|0^n\rangle$, $O = Z_1$:

| box | depth | module mass | 95% budget (of 4096) | Var $\partial\theta$ | block-surrogate err / loss scale |
|---|---:|---:|---:|---:|---:|
| local | 0 | 1.000 | 67 | 0.54 | exact ($10^{-14}$) |
| local | 2 | 0.42 | 562 | 0.27 | 0.10 / 0.12 |
| local | 6 | 0.19 | 1,981 | 0.20 | 0.13 / 0.15 |
| **nonlocal** | **1** | **0.33** | **1,486** | **0.13** | **0.12 / 0.15** |
| nonlocal | 2 | 0.23 | 1,981 | 0.21 | 0.10 / 0.14 |
| nonlocal | 4 | 0.04 | 2,047 | 0.22 | 0.11 / 0.11 |

Wherever gradients are alive past depth 0, the poly surrogate that
learns the $66\times66$ module block of $\mathrm{Ad}_U$ mis-tracks the
loss at the loss's own scale. **One nonlocal layer already collapses
the module.**

**E — the smartest classical counter, measured.** A training-orbit
surrogate needs only the smallest ad-invariant subspace containing
$\mathrm{Ad}_U(\text{module})$. Measured: 66 at depth 0; **>1,900 of
the 2,048-dim even-parity space at depth 1**, local and nonlocal alike.
Structure (exact): ad-invariant subspaces are precisely the degree
sectors, so the closure is the sum of touched sectors — which yields
the scaling analysis for free:

- **local box, constant depth:** lightcone ⇒ leaked degrees are
  constant ⇒ closure $\sum_k^{O(1)}\binom{2n}{2k}$ = **poly.
  Kill K2 fires by argument**: constant-depth local boxes are
  surrogatable at scale.
- **nonlocal box, depth $\Theta(\log n)$:** leaked degree reaches
  $\Theta(n)$ ⇒ closure hits $\binom{2n}{\Theta(n)}$ = **exponential**.
  No sector-truncation or invariant-subspace surrogate exists there.

## The surviving window (the T1 candidate proper)

> Trainable sandwiches around **nonlocal, log-depth unknown dynamics**:
> the on-device loss is measurable at poly shots; every
> moment/sector/invariant-subspace surrogate pays
> $\binom{2n}{\Theta(n)}$. The question that decides everything —
> pre-registered as **K4**: does $\mathrm{Var}_\theta[\partial\text{loss}]$
> through a nonlocal box of depth $c\log n$ decay exponentially in $n$
> (BP through the box ⇒ dichotomy restored ⇒ T1 dies), or
> polynomially (⇒ first trainable-not-surrogatable candidate)?
> Statevector scan $n = 4..10$ is feasible and owed next.

Kinship: the surviving window is **L10's QUALM gap with a variational
payload** — coherent sandwich access vs incoherent (measure-and-
reprepare) access to the same box; L10's machinery is the lower-bound
route if K4 doesn't fire. L2 supplies the box realism (non-Markovian
noise as the unknown dynamics); L3 owns the nonlinear-loss flank.

## Pre-registration

- **Advantage currency:** query/sample separation for loss estimation
  along the training trajectory, access-model symmetric. No hardness
  pedigree claimed; conditional lower bounds via L10 reductions
  acceptable.
- **K1** (surrogate-from-moments, linear module losses): **FIRED**
  2026-07-17 at the free-fermion point — exhibit A. Boundary recorded.
- **K2** (lightcone kill, constant-depth local boxes): **FIRED** by the
  sector-closure argument + measured leakage structure.
- **K3** (ad-closure shortcut): **fails to kill** — closure explodes at
  depth 1 (measured); survives only through K2's lightcone at scale,
  which nonlocal boxes evade.
- **K4** (the decisive scaling kill): **FIRED 2026-07-17** — see
  §Resolution.
- **K5** (smarter-surrogate sweep): **moot** — T1 resolved negative; a
  smarter surrogate can only strengthen the kill.

## Resolution (2026-07-17): the dichotomy is access-robust

The refined K4 scan ([`code/t1_k4_scan.py`](code/t1_k4_scan.py),
thresholds pre-registered in the file header before running; CSV:
[`t1-k4-scan.csv`](t1-k4-scan.csv)) splits the training gradient into
the part a poly adversary tracks (the module block of
$\mathrm{Ad}_{U_{\rm box}}$) and the **residual** it cannot see, and
scales $n = 4..9$:

| box depth | Var total | Var block | Var **residual** |
|---|---:|---:|---:|
| $\lceil\log_2 n\rceil$ (c=1) | −0.42 bits/qubit (R² .85) | noisy | **−0.65 bits/qubit (R² .94)** |
| $\lceil 2\log_2 n\rceil$ (c=2) | −0.67 (R² .98) | −0.86 | **−0.68 (R² .99)** |
| $2n$ (deep control) | −0.80 | −1.97 | −0.77 |

The pre-registered fire condition (residual ≥ 0.5 bits/qubit, R² > 0.9,
total strictly slower) is met at $c=1$; at $c=2$ trainability itself
collapses at the residual's rate (no window, trivially). Caveats stated:
slope separation at $c=1$ is ~2σ with $n \le 9$ and two box seeds — the
qualitative structure (residual decaying strictly faster than total,
converging to the deep-control rate) is unambiguous.

**The mechanism, which is the real deliverable:** barren plateaus and
classical surrogatability are not merely correlated — *they have the
same cause*. Both are controlled by module mass: an operator component
that leaves the poly module simultaneously (i) becomes invisible to the
$\mathfrak{g}$-sim tracker and (ii) has its gradient signal spread over
exponentially large invariant sectors where the input's per-direction
moments cannot sustain it. The trainable signal is asymptotically the
surrogatable signal because they are the *same* signal. Structured boxes
cannot escape either horn: by the sector-closure structure (exhibit E),
any leak is a sum of degree sectors — poly-degree leaks are trackable,
spread leaks are BP-dead.

**What T1's closure leaves open, for the record:** (i) losses nonlinear
in $\rho$ — [L3](L3-trainability-surrogates.md)'s flank, unaffected;
(ii) non-free-fermion poly-DLAs — the dichotomy mechanism should
generalize (module → isotypic decomposition), and *proving* that is a
theorem target worth a T-slot; (iii) nothing else within linear losses:
inputs (K1), local boxes (K2), nonlocal boxes (K4) are all closed.

## Ledger discipline

Closed same-day with three kills fired and a mechanism extracted — the
fastest full resolution in the program so far. 11 pinning tests across
[`code/test_t1_module_dichotomy.py`](code/test_t1_module_dichotomy.py)
and [`code/test_t1_k4_scan.py`](code/test_t1_k4_scan.py).
