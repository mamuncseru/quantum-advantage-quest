# Autopsy 10 — QSP / Qubitization / QSVT: the grand unification

## 1. The problem

Not one problem — a *language*. Gilyén–Su–Low–Wiebe 2019 (arXiv 1806.01838):
given a matrix A block-encoded in a unitary, apply an (almost) arbitrary
bounded polynomial p(A) to its singular values, using deg(p) applications of
the unitary and ONE extra qubit. Nearly every earlier algorithm is a choice
of polynomial:

| polynomial | algorithm |
|---|---|
| sign(x) | search / amplitude amplification |
| e^{-ixt} (poly approx) | Hamiltonian simulation |
| 1/x (poly approx on [1/κ, 1]) | HHL / linear systems |
| threshold/step | phase estimation, ground states |
| e^{-βx} approximants | Gibbs states (ground C speaks this language) |

## 2. The classical wall

Inherited from whichever problem you instantiate — QSVT is a compiler, not
an advantage claim. (The dequantization mirror exists and is instructive:
"quantum-inspired" classical algorithms do low-degree polynomial transforms
on *sampled* sketches — QSVT's advantage survives only when the
block-encoding is something classical sampling can't imitate, e.g. a sparse
Hamiltonian's structure rather than low-rank data. Next autopsy.)

## 3. The primitive

Two nested ideas, demoed exactly in `qsvt_demo.py`:

1. **Qubitization:** block-encode Hermitian A (‖A‖<1) as
   W = [[A, B], [−B, A]], B = √(I−A²). W is unitary; on each eigenvector of
   A with λ = cos θ, W rotates a 2D invariant subspace by θ. All spectral
   information becomes *rotation angles* — a matrix has been turned into a
   collection of independent single-qubit problems. Then
   (W^d)_top-left = T_d(A): **d applications of one unitary = degree-d
   Chebyshev polynomial of the matrix.** Verified to 1e−10 in the tests.
2. **QSP phases:** interleave W with single-qubit z-rotations
   e^{iφ_k Z} in that 2D subspace; the achievable top-left entries sweep out
   essentially all bounded polynomials of parity d mod 2 (quantum signal
   processing, Low–Chuang). Choosing φ's = choosing your algorithm.

## 4. The hardness evidence

None of its own (see §2) — but a *completeness* fact worth pinning: any
BQP computation can be phrased as a QSVT of a sparse block-encoding, so
"which polynomials of which block-encodings are classically feasible" is a
complete language for the advantage question. When we evaluate a candidate
in the hunt phase, translating it into QSVT form is a fast way to see what
resource is actually being consumed (degree × block-encoding cost).

## 5. The lesson — YOUR TURN

*(Own words. Prompts: if all algorithms are polynomials, then advantage =
(a) a block-encoding classical algorithms can't sample-imitate, times (b) a
polynomial degree classically unaffordable — which factor did Tang attack?
Which factor does Hamiltonian simulation win on? Where would a DQI-style
decoding step sit in this decomposition?)*

## Exercises

- [ ] Verify by hand the 2×2 rotation claim: for eigenvalue λ = cos θ of A,
      write W's action on span{|v⟩⊗e₁, |v⟩⊗e₂-ish blocks} and get the
      rotation matrix. (This is the entire theorem; 10 lines.)
- [ ] Grover from QSVT: which A, which polynomial, and where does the √N
      come from as a *degree*? One paragraph.
- [ ] Run the demo. Then modify it (locally, throwaway) to check d = 20 —
      where does numerical error creep in, and why?
