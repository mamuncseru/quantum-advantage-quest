# Autopsies 07–08 — Quantum walks: glued trees and Szegedy

## 1. The problem(s)

Traversal/search on graphs. Two exemplars:
- **Glued trees** (Childs–Cleve–Deutsch–Farhi–Gutmann–Spielman 2003): two
  binary trees of depth d joined leaves-to-leaves by a random cycle; enter at
  the left root, find the right root. Oracle = adjacency access.
- **Markov-chain search** (Szegedy 2004; Magniez–Nayak–Roland–Santha):
  find marked states of a reversible Markov chain faster than its mixing.

## 2. The classical wall

Glued trees: a classical walker drifts INTO the exponentially fat middle
(2 of 3 edges point inward from each side) and provably needs 2^Ω(d) steps —
in fact any classical algorithm needs exponentially many queries; the
random cycle prevents even clever algorithms from knowing where they are.
Run `glued_trees.py`: at d = 20, classical with a d³ budget: 6×10⁻⁴;
quantum at time 0.8d: 0.40.

## 3. The primitive

**Interference against the drift.** By symmetry the quantum walk lives in the
(2d+2)-dim "column space," where the reduced Hamiltonian is a near-uniform
path — a wave packet crosses *ballistically* (dispersion relation of the
path graph), sailing through the middle that traps the diffusive classical
walker. This is the **only exponential speedup in our curriculum that does
not come from the Fourier transform over a group.** Its mechanism is
spectral: the walk operator's eigenvalues e^{±i·arccos(λ)} give quantum
dynamics a *linear* light cone where classical chains move as √t.

Szegedy's discretization makes this systematic: quantize any reversible
chain P into a walk with eigenphases arccos of P's eigenvalues — so a
classical spectral gap δ becomes a quantum phase gap √δ. Hence hitting/
search in ~1/√δ where classical needs ~1/δ. (MNRS: search cost
~ S + (1/√δ)(1/√ε)(U + C) — the framework behind element distinctness,
triangle finding, etc.) **Bridge to ground C:** quantum Gibbs samplers hunt
the same √-vs-linear gap structure in *open-system* dynamics.

## 4. The hardness evidence

Glued trees: unconditional exponential *query* separation (classical lower
bound is a theorem, no assumptions). The eternal catch: an oracle result —
20+ years without a compelling instantiation; "exponential speedup, no
customer." Szegedy walks: mostly quadratic, honest, and — like amplitude
amplification — overhead-prone in practice.

## 5. The lesson — YOUR TURN

*(Own words. Prompts: the glued-trees speedup needed a graph engineered so
that classical drift fails while quantum dispersion sails — what does that
teach about where walk advantages live "in nature"? Why does √(spectral gap)
cap most walk speedups at quadratic, and what structural extras (symmetry,
spectral concentration) does an exponential walk advantage seem to require?)*

## Exercises

- [ ] Run the demo; then derive the reduced path weights (√2 inside trees,
      2 at the glue) from the column-state normalization yourself — 5 lines.
- [ ] Explain the classical column chain's bias 2/3-vs-1/3 from vertex
      degrees, and why making the exit absorbing only *helps* the classical
      side (so our comparison is fair).
- [ ] One paragraph: why is the glued-trees oracle hard to instantiate?
      (What would a real function have to hide? Compare with a^x mod N.)
