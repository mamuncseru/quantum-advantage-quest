# Autopsy 13 — Quantum Gibbs sampling: Metropolis → Davies → CKG

**Hunting ground C.** Companion: `frontier/lit-sweep-2026H1.md` (2026 state).
Primary sources to verify at proof level: Chen–Kastoryano–Gilyén
(arXiv 2311.09207, "exact noncommutative Gibbs sampler"; lineage published
Nature 646, 561), Rajakumar–Watson (2408.01516, Quantum 2026),
Bakshi–Tan (2604.08408, per sweep).

## 1. The problem

Prepare (sample from) the Gibbs state ρ_β ∝ e^{−βH} of a local quantum
Hamiltonian. The customer: all of equilibrium physics and chemistry, plus
Gibbs states as the engine of optimization (classical MCMC's quantum
sibling) and of ML (Boltzmann machines). Classical MCMC is arguably the
most-used algorithm family in science — this ground hunts its quantum
counterpart.

## 2. The classical wall

- Generic: quantum Gibbs states of non-commuting H have no efficient
  classical description at intermediate β (sign problem blocks QMC;
  entanglement blocks tensor networks in ≥2D).
- **But the provably-easy atlas is expanding** (this is the 2026 squeeze,
  see sweep): 1D all temperatures, high temperature generally, weak
  coupling. The advantage region is the *intermediate* regime — and
  crucially, hardness there has anchors: Rajakumar–Watson prove (under
  PH-non-collapse-style sampling assumptions) that constant-temperature
  Gibbs sampling of O(1)-local Hamiltonians is classically hard.

## 3. The primitive — three generations

1. **Davies generator** (1970s, weak-coupling limit): jump operators = Bohr-
   frequency components A(ω) of couplings, rates with the KMS ratio
   γ(ω) = e^{βω}γ(−ω). Fixes Gibbs exactly, ergodic ⇒ gap ⇒ convergence.
   **You have it in code** (`davies.py`): stationarity 1e−16, gap 0.20 at
   3 qubits. Its fatal flaw at scale: A(ω) needs exact Bohr frequencies —
   an oracle, not an algorithm (resolving them costs exponential time).
2. **Quantum Metropolis** (Temme et al. 2011): phase-estimate energies,
   accept/reject. The obstruction it hit: measurement destroys coherence;
   rewinding rejected moves is awkward and approximate.
3. **CKG samplers** (2023→, the modern engine): Gaussian-filtered jump
   operators (finite energy resolution, so implementable — cost ~ Hamiltonian
   simulation time) PLUS an explicitly constructed coherent correction term
   B that restores **exact** quantum detailed balance. Efficiently
   implementable Lindbladian, exact Gibbs fixed point, arbitrary
   non-commuting H. Mixing time: NOT guaranteed — and that is precisely
   where the science now lives.

## 4. The hardness evidence — the 2026 ledger (from the sweep; verify)

- Sampling hardness at constant T for O(1)-local H: Rajakumar–Watson
  (conditional, standard assumptions) — the ground's anchor theorem.
- **Bakshi–Tan (Apr 2026), the template result:** strong on-site fields
  break the best classical dequantizer (the Bakshi–Liu–Moitra–Tang
  high-temperature counting method) while the quantum Lindbladian still
  mixes rapidly — "break the dequantizer, keep the mixer." Executed ONCE
  in the literature. Repeatable by construction.
- No unconditional quantum-vs-classical mixing-time separation yet. Open.
- Structural immunity worth pinning: the input is a HAMILTONIAN, not a
  data matrix — there is no ℓ²-sampling access model to hide behind, so
  Tang-style dequantization cannot even be formulated. (Contrast autopsy 11.)

## 5. The lesson — YOUR TURN

*(Own words. Prompts: classical Metropolis needed only detailed balance +
ergodicity — which quantum obstruction made "just do Metropolis" take 40
years to fix, and what did CKG actually pay (Gaussian filter width, the
coherent term) to fix it? Why is "prove the gap" the entire remaining
frontier? Sketch the Bakshi–Tan mechanism as a recipe: which knob would YOU
turn next — quasi-periodic fields? weak non-commuting perturbation of a
classically-hard commuting model?)*

## Exercises

- [ ] Run both demos. In `davies.py`, verify the KMS ratio claim for the
      Glauber choice γ(ω) = 1/(1+e^{−βω}) — 2 lines of algebra.
- [ ] Prove Gibbs stationarity of the Davies generator: show each ω-term of
      L annihilates ρ_β using A(ω)ρ_β = e^{βω} ρ_β A(ω) (operator algebra,
      ~10 lines; then check your steps against what the code verifies
      numerically).
- [ ] Classical side: for the 1D Ising Metropolis chain, what is the known
      mixing time at β = 0.7 (order of magnitude, cite)? Why does the same
      question for `davies.py`'s 3-qubit chain have no classical analogue?
- [ ] The hunt-phase question, one page: write the Bakshi–Tan recipe as a
      checklist (dequantizer to break, mixer to preserve, hardness to
      inherit), then propose ONE candidate knob with a mechanism argument.
