# Autopsy 11 — HHL (2009) and Tang (2018): how an advantage dies

## 1. The problem

HHL (Harrow–Hassidim–Lloyd): "solve" Ax = b — more precisely, prepare a
quantum state ∝ A⁻¹|b⟩ — in time polylog(dim) for well-conditioned sparse A.
It launched a decade of quantum machine learning: recommendation systems,
PCA, clustering, SVMs, all claiming exponential speedups.

## 2. The classical wall (as it appeared)

Classical linear algebra is poly(dim). Exponential speedup for the most
common computation in the world — if true, the biggest result since Shor.

## 3. The primitive

QSVT with p(x) ≈ 1/x (historically: phase estimation + controlled rotation).
Legitimate, and BQP-complete in the right regime — the primitive is not the
problem. The problem is the fine print (Aaronson 2015, "Read the fine
print"), four separate tolls at the door:

1. Preparing |b⟩ from classical data: needs QRAM / state preparation — the
   input toll.
2. Condition number κ and sparsity enter polynomially.
3. Output is a *state*, not the solution vector: reading x costs dim samples
   — the output toll.
4. If A is low-rank (as in all the ML applications), see below.

## 4. The hardness evidence — collapsed

**Tang 2018** (then a 22-year-old student; recommendation systems, followed
by the full "quantum-inspired" program of Tang, Gilyén, Chia, Lin, Wang...):
if the quantum algorithm assumes state-preparation access to the data, the
honest classical comparison is **ℓ²-sampling access** — and with it,
classical algorithms match every low-rank QML speedup up to polynomial
factors. `fkv.py` makes you feel it: 200 sampled rows of a 1500×1500
low-rank matrix reconstruct the optimal projection to within 2%.

The autopsy verdict, precisely: **the exponential advantage never lived in
the quantum processing; it lived in an unfair comparison of access models.**
What survives of HHL: the BQP-complete regime — sparse, well-conditioned,
*high-rank* A with |b⟩ produced by a quantum process rather than loaded
from data. Survivors are quantum-native; casualties were classical data
wearing a quantum costume.

## 5. The lesson — YOUR TURN

*(Own words — this one is the red-team charter. Prompts: state the "access
model symmetry" rule for any future claim we make: whatever preparation
power we grant the quantum algorithm, the classical baseline gets its
sampling analogue. Which of our two hunting grounds is structurally immune
to this attack, and why? Write the checklist you would run against a new
QML-advantage paper — then keep it; it goes in the Problem-Shape Catalog.)*

## Exercises

- [ ] Run `python predecessors/10-hhl-tang/fkv.py`.
- [ ] Prove E[SᵀS] = AᵀA for the FKV rescaled row sample (3 lines) — this
      identity IS the dequantization.
- [ ] One paragraph: why does ℓ²-sampling access to a *Gibbs state of a
      non-commuting Hamiltonian* not exist classically? (This is why ground
      C survives Tang-style attacks — be precise about where the analogy
      breaks.)
