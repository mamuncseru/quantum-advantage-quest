# L9 — The certification gap: learning is easy, certifying is the memory task

**Pre-registered 2026-07-11**, ground L. The HilbertBench candidate:
diagnostics = certification, and certification is where ground-L's
collapses *stop*.

## The construction (exact, this session)

[`code/certification_gap.py`](code/certification_gap.py):
$\rho_{\text{bad}} = \rho_{\text{Gibbs}} + c\,Y^{\otimes n}$ ($n = 6$,
$c$ at the positivity edge). Every marginal on $< n$ qubits is
**identical** to the honest Gibbs state's (a full-weight Pauli has zero
partial trace), so every marginal-based learner — including the AAKS
max-entropy fit — outputs the same model for both and reports *zero
misfit*, while the true trace distance is a macroscopic **0.03**. The
model class is right, the fit converges, and the certificate lies.

The frame anatomy (shared with [L6](L6-topological-shield.md)): if the
auditor *knows* the deviation direction, $\langle Y^{\otimes n}\rangle$
is a cheap product measurement. Unknown frame: a single-copy auditor
searches $\sim 4^n$ global Paulis; a two-copy auditor Bell-difference
samples the Pauli spectrum *as a distribution* and flags the deviation's
support directly.

## The candidate

> **Certified agnostic tomography.** Formalize: given copies of ρ and a
> physical model class $\mathcal{F}$ (Gibbs of local $H$; sparse
> Pauli–Lindblad), output a model *and a certified bound on
> $d(\rho, \mathcal{F})$*. Conjecture: the learning half is single-copy
> poly (known, ground-L collapses); the certification half has a
> single-copy exponential lower bound (hidden-frame deviations) and a
> two-copy poly upper bound (Bell-difference deviation detection).
> Deliverable either way: the theorem, or the single-copy certifier that
> refutes it — both directly actionable for device diagnostics.

Lit anchors: the agnostic-tomography wave
([stabilizer bootstrapping, STOC'25](https://dl.acm.org/doi/10.1145/3717823.3718191);
[stabilizer product states](https://arxiv.org/abs/2404.03813); agnostic
process tomography, PRX Quantum 12/2025) does the *learning* half; the
*certification-against-hidden-deviation* half appears open.

## Pre-registration

- **Kills:** (1) tolerant-testing literature already gives single-copy
  certification for these classes (check
  [tolerant stabilizer testing](https://arxiv.org/pdf/2410.22220) line
  first); (2) the two-copy upper bound fails at small deviation scales
  (Bell-sampling signal $\propto c^2 2^n$ vs shot noise — quantify
  before claiming); (3) merge: the hidden-frame core may be the same
  theorem as L6's — if so, fuse.
- **First actions:** quantify the two-copy detection threshold exactly;
  tolerant-testing lit pass; the Gibbs-class version of the lower-bound
  construction (deviations orthogonal to all low-weight Paulis, scaled
  families).
