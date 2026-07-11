# L7 — Symmetry-class learning on physical data: does the advantage survive?

**Pre-registered 2026-07-11**, ground L. Symmetry-class determination is
a flagship provable separation: exponential single-copy vs poly two-copy
for testing time-reversal classes (HCP Science 2022;
[QUALM](https://arxiv.org/abs/2101.04634) proved the coherent-access
version for dynamics). All proofs use adversarial (Haar-twirled)
ensembles. L7 asks the ground-L question: **does any of it survive on
physical data** — quench states of local Hamiltonians, the tenfold-way
classification of real materials?

## The collapse conjecture (pre-registered as the likely outcome)

For *local* $H$, symmetry breaking leaks into **low-weight observables**:
the time-averaged quench state of a real (T-symmetric) $H$ is a real
matrix, so every odd-$Y$ Pauli expectation vanishes; a complex $H$
generically lights them up at $\Omega(1)$. Single-copy shadows then
decide the class in poly time — collapse. The identifiability literature
adds pressure: local $H$ is often determined by
[a single eigenstate](https://quantum-journal.org/papers/q-2019-07-08-159/).

**First numerics** ([`code/symmetry_leakage.py`](code/symmetry_leakage.py)):
time-averaged quench states, $n = 6$, real vs complex local $H$ — the
low-weight odd-$Y$ leakage statistic separates the classes exactly as
conjectured (real class → finite-grid residue only; complex class →
$\Omega(1)$).

## Pre-registration

- **Deliverable:** the leakage *theorem* (local $H$ ⇒ symmetry class
  decidable from $O(\mathrm{poly})$ low-weight observables of the
  time-averaged ensemble) — an honest collapse result delimiting HCP-type
  symmetry advantages to non-local or globally-hidden breaking; plus the
  residue map (breaking hidden from all local probes ⇒ L6's shield —
  the two candidates likely **merge** at the residue).
- **Kills:** (1) the leakage theorem fails for some local class
  (interesting on its own — that class is the candidate); (2) residue
  empty after merge with L6 → close both into one; (3) lit: the
  collapse may be known folklore in the random-matrix/thermalization
  community — check.
- **First actions:** prove the infinite-time-average leakage lemma
  (elementary: eigenvector reality); scan symmetry classes beyond T
  (the tenfold way — which classes leak locally?); lit pass.
