# L6 — The topological shield: distributed comparison of locally hidden sectors

**Pre-registered 2026-07-11**, ground L. Cross-platform verification —
"do our two labs hold the same state?" — is provably hard in the worst
case: [Anshu–Landau–Liu, STOC 2022](https://arxiv.org/abs/2111.03273)
show $\Theta(\sqrt{d}) = 2^{\Theta(n)}$ copies are needed with local
operations + classical communication (via a cloning reduction);
follow-ups map [limited quantum communication](https://arxiv.org/html/2410.12684v1).
But the L1 collapse applies to physical data: marginal-parameterized
states (Gibbs) are compared by learning $\hat H$ on each side and
comparing classically. **The shield must be states that are locally
identical by theorem** — sector pairs of topological order, minimally
the GHZ pair.

## First numerics ([`code/ghz_shield.py`](code/ghz_shield.py))

Exact, $n = 8$: (1) all $(n{-}1)$-qubit marginals of $|GHZ^\pm\rangle$
identical to machine precision — marginal learners carry *zero* signal;
(2) **but** a frame-known global product measurement ($X$-string parity)
separates the sectors in one shot — marginal-blindness ≠
single-copy-blindness; (3) under a hidden product frame the
distinguishing string becomes one unknown weight-$n$ Pauli among
$\sim 4^n$, while the frame-free two-copy overlap test is untouched.

> **The candidate question.** For hidden-frame sector pairs (random-frame
> GHZ, toric-code sectors under unknown code deformation): prove the
> single-copy / classical-communication lower bound (the distinguishing
> observable is global *and* cryptographically hidden — the ALL cloning
> argument should localize here), giving the first *physical* family
> where distributed memory advantage survives the collapse.

## Pre-registration

- **Kills:** (1) frame-finding turns out single-copy-easy (it is
  stabilizer-structure learning — if L4's strip resolves toward easy,
  L6 dies with it: **shared fate with L4, flagged**); (2) the physical
  instantiation is unnatural (no lab hands out random-frame sectors) —
  the topological version must be argued from actual anyonic memories;
  (3) lit: the ALL line may already cover promise-restricted ensembles.
- **First actions:** toric-code version of the demo (3×3 torus, 18
  qubits); reduction map L6 ↔ L4 (frame-finding ≡ strip instance);
  deep lit pass on cross-platform verification with promises.
