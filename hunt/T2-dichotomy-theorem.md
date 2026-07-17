# T2 — The dichotomy theorem: trainable ⇒ surrogatable, for every poly-DLA

**Pre-registered and opened 2026-07-17**, ground T, second candidate —
the door [T1](T1-module-dichotomy.md) opened: turn T1's measured
mechanism into a proved boundary for *arbitrary* polynomial-DLA
ansätze, linear losses, unknown quantum inputs. This is a
theorem-target hunt: the deliverable is a proof (or its counterexample),
and either is a keep.

**Status: theorem stated and proved at AI rigor below; validated on two
maximally different DLAs; human verification and deep novelty pass
owed.** The variance *engine* is known —
[Ragone et al., Nat. Comm. 2024 (2309.09342)](https://arxiv.org/abs/2309.09342)
and Fontana et al.'s adjoint formalism — and is cited, not claimed. The
contribution here is the **multiplicity-contraction lemma** (Lemma B),
the access-symmetrized corollaries (unknown inputs; interleaved unknown
dynamics = T1's K4 as a special case), and the quantitative
trainable-⇒-surrogatable partition they assemble into.

## Setting

Ansatz $V(\theta)=\prod_l e^{-i\theta_l H_l}$, $H_l \in \mathfrak{g}$
(the DLA), $\dim\mathfrak{g} = \mathrm{poly}(n)$, $G = e^{\mathfrak{g}}$
compact. The operator space $\mathcal{B}(\mathcal{H})$ with HS inner
product decomposes under $\mathrm{Ad}_G$ into isotypic components
$\bigoplus_\lambda \mathbb{C}^{k_\lambda}\!\otimes V_\lambda$
($d_\lambda = \dim V_\lambda$, multiplicity $k_\lambda$). Linear loss
$L(\theta) = \mathrm{Tr}[\rho\, V^\dagger O V]$: $\rho$ **unknown**
(single-copy access only), $O$ known with polynomially many
nonvanishing isotypic components, each admitting a bounded-∞-norm
operator basis (the standard measurable class; see Remarks). Deep-circuit
idealization: $\theta$-averages = Haar over $G$ (Ragone et al.'s
regime; finite depth is approximate — measured below).

## Lemma A (per-irrep variance; engine known)

For a nontrivial $\lambda$ of real type,
$\mathbb{E}_g[L_\lambda] = 0$ and

$$\mathrm{Var}_g[L_\lambda] \;=\; \frac{\|M_\lambda\|_F^2}{d_\lambda},
\qquad
\mathrm{Var}_g[\partial_{\theta_l} L_\lambda] \;\le\;
\frac{4\|H_l\|_\infty^2\,\|M_\lambda\|_F^2}{d_\lambda},$$

with $c_\lambda \le 2$ replacing the equality for complex/quaternionic
type, and $\|M_\lambda\|_F \le \|P_\lambda\rho\|_{HS}\|P_\lambda
O\|_{HS}$. Trivial $\lambda$: $L_\lambda$ is a $\theta$-independent
constant (zero gradient, perfectly surrogatable — T1's parity sector and
the $\ell=0$ Casimir sector below are instances). *Proof:* Schur
orthogonality for the real orthogonal representation $R_\lambda$;
the gradient inserts $\mathrm{ad}_{iH_l}$, which preserves
$V_\lambda$ with $\|[iH_l,X]\|_{HS} \le 2\|H_l\|_\infty\|X\|_{HS}$;
one-sided Haar suffices. $\square$

## Lemma B (multiplicity contraction — the new content)

Because $\mathrm{Ad}_G$ acts as $\mathbb{1}_{k_\lambda}\!\otimes
R_\lambda$ — the dynamics never touches the multiplicity index —

$$L_\lambda(\theta) \;=\; \mathrm{Tr}\big[R_\lambda(\theta)\,
M_\lambda\big],\qquad
M_\lambda[m,m'] \;=\; \sum_{a=1}^{k_\lambda} o^{(a)}_m\,
\overline{\mu^{(a)}_{m'}},$$

and each entry of $M_\lambda$ is the expectation of a **single known
observable** $W_{\lambda,m,m'} = \sum_a o^{(a)}_m T^{(a)}_{m'}$ on
$\rho$. The surrogate therefore pays $\sum_\lambda d_\lambda^2$
one-time single-copy measurements — **independent of the
multiplicities**, which may be exponential. $\square$

This closes the one structural escape T1's analysis left conceivable:
exponential multiplicity of a poly-dim irrep makes the *isotypic
component* exponentially large while leaving gradients unsuppressed —
but the contraction shows the surrogate never needed the component,
only its $d_\lambda^2$ contracted cross-moments. The escape hatch was
attempted as a kill of the theorem and closed constructively.

## Theorem (the linear-loss dichotomy)

Fix a cutoff $D$. Split $O = O_{\mathrm{track}} + O_{\mathrm{blind}}$
by $d_\lambda \le D$ vs $d_\lambda > D$. Then:

1. **(Surrogate)** $L_{\mathrm{track}}(\theta)$ is classically
   computable for every $\theta$ from
   $\sum_{\lambda \in \mathrm{supp}(O),\, d_\lambda\le D} d_\lambda^2$
   one-time single-copy measurements plus
   $\mathrm{poly}$ propagation through the $d_\lambda$-dim blocks.
2. **(Barren plateau)** $\mathrm{Var}_\theta[L_{\mathrm{blind}}]$ and
   $\mathrm{Var}_\theta[\partial L_{\mathrm{blind}}]
   \;\le\; \dfrac{8\,\|H\|_\infty^2\,\mathrm{Tr}(\rho^2)\,
   \|O\|_{HS}^2}{D}.$

*Proof of 2:* sum Lemma A over blind components;
$\sum_\lambda \|P_\lambda\rho\|^2\|P_\lambda O\|^2 \le
\|O\|_{HS}^2\,\mathrm{Tr}\rho^2$ by Cauchy–Schwarz. $\square$

**Reading: every part of the loss the polynomial surrogate cannot see
has gradients vanishing as $1/D$ — the trainable signal *is* the
surrogatable signal, for any poly-DLA, with unknown quantum inputs
included at one-time measurement cost.** T1's measured 0.65-bits/qubit
residual decay is clause 2 in action at the free-fermion point.

**Corollary (interleaved unknown dynamics — T1's K4, generalized).**
With a fixed unknown $U$ inside the sandwich, the effective observable
is $\mathrm{Ad}_U(\mathrm{Ad}_{V_2}O)$; the surrogate additionally
learns the transfer blocks $P_{\lambda'}\mathrm{Ad}_U P_\lambda$
between tracked components (poly queries when the tracked bases have
bounded ∞-norm, by preparing $(\mathbb{1}+T)/2^n$ ensembles and
measuring), and clause 2 covers everything $U$ scatters into blind
components. The dichotomy is access-robust.

## Validation on two maximally different DLAs

| | T1: free fermions ($\mathfrak{so}(2n)$, dim 66 at $n{=}6$) | T2: collective spin ($\mathfrak{su}(2)$, dim 3, $n{=}5$) |
|---|---|---|
| module structure | multiplicity-free degree sectors, dims to $\binom{2n}{n}$ | dims $\le 2n{+}1$, multiplicities to 90 (exp in $n$) |
| side of dichotomy exhibited | BP side: blind residual dies at 0.65 bits/qubit | surrogate side: everything tracked by **286 numbers** of a 1024-dim space |
| Lemma B check | — | contraction surrogate = exact to $3.0\times10^{-15}$, unknown input |
| Lemma A check | variance law qualitative ([T1 §B](T1-module-dichotomy.md)) | Var vs $\|M\|^2/d$: **within 5% ($\ell{=}1$), 0.3% ($\ell{=}2$)** at 4 layers |
| invariant sectors | parity: Var $\sim10^{-22}$ | Casimir $\ell{=}0$: Var $\sim10^{-32}$ |

Code: [`code/t2_dichotomy_su2.py`](code/t2_dichotomy_su2.py), 5 pinning
[tests](code/test_t2_dichotomy_su2.py).

## Remarks and honest scope

- **The Haar idealization** is the standard deep-circuit regime; finite
  shallow circuits obey the law approximately (measured: 5% at 4
  layers). Warm starts and adaptive ansätze live outside it — that
  boundary is [T3-territory](T1-module-dichotomy.md#ground-t--the-provisional-map-doors-open-doors).
- **supp(O) assumption:** an $O$ with exponentially many small-dim
  components (possible for abelian DLAs) evades clause 1's cost bound —
  but diagonal observables under diagonal DLAs sit in trivial modules
  (constant loss), and generic HS-normalized exponential-support
  observables have $2^{-\Theta(n)}$ signal, unmeasurable on the device
  too. The access-symmetric formulation absorbs the corner; a sharper
  characterization is listed as follow-up.
- **What the theorem does NOT cover, by design:** losses nonlinear in
  $\rho$ ([L3](L3-trainability-surrogates.md)'s live flank — this
  theorem is exactly why L3's window is the only linear-adjacent one
  left) and non-DLA circuit families (adaptive, measurement-based).

## Pre-registration

- **Deliverable:** the theorem above as a boundary result (write-up
  quality), or a counterexample.
- **K1** (counterexample via multiplicity): attempted first, **closed
  constructively** — became Lemma B.
- **K2** (numerics contradict a lemma on a second DLA): **did not fire**
  — su(2) validation at machine precision / 5%.
- **K3** (novelty): the variance engine is Ragone/Fontana's; if the
  deep pass finds Lemma B + the access-robust corollaries already
  stated, T2 collapses to a citation note. **Deep novelty pass owed
  before any write-up.**
- **K4** (human verification): owed, as for everything in this program.

## Ledger discipline

Opened with the theorem delivered at AI rigor same-day; remains open
pending K3 (novelty) and K4 (human batch) — a theorem is not closed by
the day it is typed.
