# Autopsy 13 — Quantum Gibbs sampling: Metropolis → Davies → CKG

*Hunting ground C. Classical MCMC's quantum sibling, forty years late.*

!!! info "Read with the frontier file open"

    2026 state: [the literature sweep](../../frontier/lit-sweep-2026H1.md).
    Verify at proof level: Chen–Kastoryano–Gilyén (arXiv 2311.09207, lineage
    published Nature 646, 561), Rajakumar–Watson (2408.01516, Quantum 2026),
    Bakshi–Tan (per sweep).

## 1. The problem

Prepare (sample from) the Gibbs state

$$
\rho_\beta = \frac{e^{-\beta H}}{\mathrm{Tr}\, e^{-\beta H}}
$$

of a local quantum Hamiltonian. The customer: all of equilibrium physics and
chemistry, plus Gibbs states as the engine of optimization and of ML
(Boltzmann machines). Classical MCMC is arguably the most-used algorithm
family in science — this ground hunts its quantum counterpart.

## 2. The classical wall

Generic quantum Gibbs states of non-commuting $H$ at intermediate $\beta$
have no efficient classical description: the sign problem blocks QMC,
entanglement blocks tensor networks in $\ge 2$D. **But the provably-easy
atlas is expanding** — 1D at all temperatures, high temperature generally,
weak coupling — squeezing the advantage into the *intermediate regime*. The
anchor there: **Rajakumar–Watson** prove (under PH-non-collapse-style
sampling assumptions) that constant-temperature Gibbs sampling of
$O(1)$-local Hamiltonians is classically hard.

## 3. The primitive — three generations

**1 · Davies generator** (1970s, weak-coupling limit). Split each coupling
$A$ into Bohr-frequency components

$$
A(\omega) = \sum_{E_k - E_j = \omega} |j\rangle\langle j|\, A\, |k\rangle\langle k| ,
$$

give each the Glauber rate $\gamma(\omega) = \big(1 + e^{-\beta\omega}\big)^{-1}$,
which satisfies the KMS / detailed-balance condition
$\gamma(\omega) = e^{\beta\omega}\,\gamma(-\omega)$, and form the Lindbladian

$$
\mathcal{L}(\rho) = \sum_\omega \gamma(\omega)
\Big( A(\omega)\,\rho\, A(\omega)^\dagger
- \tfrac12\big\{ A(\omega)^\dagger A(\omega),\, \rho \big\} \Big).
$$

It fixes $\rho_\beta$ **exactly**, and ergodic couplings give a spectral gap.
You have this in code — [`davies.py`](davies.py) verifies stationarity to
$10^{-16}$ and measures gap $0.20$ on a 3-qubit chain:

<figure markdown="span">
  ![Convergence of the Davies sampler](fig-convergence.svg#only-light)
  ![Convergence of the Davies sampler](fig-convergence-dark.svg#only-dark)
  <figcaption>Three very different initial states, one destination: the
  Davies Lindbladian pulls everything to e^(−βH)/Z at a rate set by its
  spectral gap. "Prove the gap" is the entire remaining frontier of this
  ground.</figcaption>
</figure>

Its fatal flaw at scale: $A(\omega)$ requires *exactly* resolving all Bohr
frequencies — an oracle, not an algorithm.

**2 · Quantum Metropolis** (Temme et al. 2011). Phase-estimate energies,
accept/reject. Obstruction: measuring energy destroys the coherences;
rewinding rejected moves is awkward and approximate.

**3 · CKG samplers** (2023 →, the modern engine). Gaussian-filtered jump
operators — finite energy resolution, implementable at Hamiltonian-simulation
cost — **plus an explicitly constructed coherent correction term** that
restores *exact* quantum detailed balance for arbitrary non-commuting $H$.
Efficient Lindbladian, exact fixed point. Mixing time: **not guaranteed** —
and that is precisely where the science now lives.

## 4. The hardness evidence — the 2026 ledger

- Constant-$T$ sampling hardness for $O(1)$-local $H$: Rajakumar–Watson —
  the ground's anchor theorem (conditional, standard assumptions).
- **Bakshi–Tan (Apr 2026), the template result:** strong on-site fields
  *break the best classical dequantizer* (the high-temperature
  counting-to-sampling method) *while the quantum Lindbladian still mixes
  rapidly*. "Break the dequantizer, keep the mixer" — executed exactly once
  in the literature. Repeatable by construction.
- No unconditional quantum-vs-classical mixing-time separation yet. Open.

!!! tip "Structural immunity worth pinning"

    The input here is a **Hamiltonian**, not a data matrix — there is no
    $\ell^2$-sampling access model to hide behind, so Tang-style
    dequantization (Autopsy 11) cannot even be *formulated*. Advantage
    claims on this ground die or survive on physics, not on access-model
    bookkeeping.

## 5. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    Classical Metropolis needed only detailed balance + ergodicity. Which
    quantum obstruction made "just do Metropolis" take forty years, and what
    did CKG actually pay to fix it? Why is "prove the gap" the entire
    remaining frontier? Then sketch the Bakshi–Tan mechanism as a *recipe* —
    and name the knob YOU would turn next (quasi-periodic fields? weak
    non-commuting perturbation of a classically-hard commuting model?).

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/12-gibbs-lindblad/metropolis.py
    .venv/bin/python predecessors/12-gibbs-lindblad/davies.py
    .venv/bin/pytest predecessors/12-gibbs-lindblad -q
    ```

- [ ] Verify the KMS ratio for the Glauber choice — two lines of algebra.
- [ ] Prove Gibbs stationarity of the Davies generator: show each
      $\omega$-term of $\mathcal{L}$ annihilates $\rho_\beta$, using
      $A(\omega)\,\rho_\beta = e^{\beta\omega}\rho_\beta\, A(\omega)$
      (~10 lines; the code verifies it numerically — your proof explains why).
- [ ] Classical side: what is the known mixing time of 1D Ising Metropolis at
      $\beta = 0.7$ (order of magnitude, with citation)? Why does the same
      question for the 3-qubit Davies chain have no classical analogue?
- [ ] **The hunt-phase question** (one page): write the Bakshi–Tan recipe as
      a checklist — dequantizer to break, mixer to preserve, hardness to
      inherit — then propose ONE candidate knob with a mechanism argument.
