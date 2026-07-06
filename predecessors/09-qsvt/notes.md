# Autopsy 10 — QSP / Qubitization / QSVT: the grand unification

*Not one problem — a language every algorithm turns out to speak.*

## 1. The problem

Gilyén–Su–Low–Wiebe 2019 (arXiv 1806.01838): given a matrix $A$ block-encoded
in a unitary, apply an (almost) arbitrary bounded polynomial $p(A)$ to its
singular values, using $\deg(p)$ applications of the unitary and ONE extra
qubit. Nearly every earlier algorithm is a choice of polynomial:

| Polynomial | Algorithm |
|---|---|
| $\mathrm{sign}(x)$ | search / amplitude amplification |
| approx. of $e^{-ixt}$ | Hamiltonian simulation |
| approx. of $1/x$ on $[1/\kappa, 1]$ | HHL / linear systems |
| threshold / step | phase estimation, ground states |
| approx. of $e^{-\beta x}$ | Gibbs states — hunting ground C speaks QSVT |

## 2. The classical wall

Inherited from whichever problem you instantiate — QSVT is a **compiler, not
an advantage claim**. Its dequantization mirror exists and is instructive:
"quantum-inspired" classical algorithms do low-degree polynomial transforms
on *sampled sketches*. QSVT's advantage survives only when the block-encoding
is something classical sampling cannot imitate — a sparse Hamiltonian's
structure, not low-rank data (next autopsy).

## 3. The primitive

Two nested ideas, both live in [`qsvt_demo.py`](qsvt_demo.py):

**1 · Qubitization.** Block-encode Hermitian $A$ ($\|A\| < 1$) in the walk
operator

$$
W = \begin{pmatrix} A & B \\ -B & A \end{pmatrix},
\qquad B = \sqrt{I - A^2}.
$$

$W$ is unitary, and on each eigenvector of $A$ with $\lambda = \cos\theta$ it
rotates a 2D invariant subspace by $\theta$ — the whole matrix becomes a
stack of independent single-qubit rotations. Consequently

$$
\big(W^d\big)_{\text{top-left}} = T_d(A)
$$

— **$d$ applications of one unitary implement the degree-$d$ Chebyshev
polynomial of the encoded matrix** (verified to $10^{-10}$ in our tests).

<figure markdown="span">
  ![Chebyshev polynomials from walk-operator powers](fig-chebyshev.svg#only-light)
  ![Chebyshev polynomials from walk-operator powers](fig-chebyshev-dark.svg#only-dark)
  <figcaption>What the top-left block of W^d does to each eigenvalue of A:
  Chebyshev curves T₁…T₄. QSP phases interpolate between such polynomials —
  choosing phases is choosing your algorithm.</figcaption>
</figure>

**2 · QSP phases.** Interleave $W$ with single-qubit rotations
$e^{i\phi_k Z}$ in that 2D subspace; the achievable top-left entries sweep
out essentially all bounded polynomials of parity $d \bmod 2$ (Low–Chuang
quantum signal processing). Choosing $\phi_1,\dots,\phi_d$ *is* choosing your
algorithm.

## 4. The hardness evidence

None of its own (see §2) — but a completeness fact worth pinning: any BQP
computation can be phrased as a QSVT of a sparse block-encoding, so *"which
polynomials of which block-encodings are classically feasible"* is a complete
language for the advantage question.

!!! tip "How the Quest uses this"

    When we evaluate a hunt-phase candidate, translating it into QSVT form —
    degree × block-encoding cost — is the fastest way to see which resource
    is actually being consumed, and which factor (encoding or degree) the
    classical attack will target.

## 5. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    If all algorithms are polynomials, advantage $=$ (a) a block-encoding
    classical algorithms can't sample-imitate $\times$ (b) a polynomial
    degree classically unaffordable. Which factor did Tang attack? Which does
    Hamiltonian simulation win on? Where would a DQI-style decoding step sit?

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/09-qsvt/qsvt_demo.py
    .venv/bin/pytest predecessors/09-qsvt -q
    ```

- [ ] Verify the 2×2 rotation claim by hand: for eigenvalue
      $\lambda = \cos\theta$, write $W$'s action on the invariant plane and
      obtain the rotation matrix. This IS the theorem; ten lines.
- [ ] Grover from QSVT: which $A$, which polynomial, and where does
      $\sqrt N$ appear as a *degree*? One paragraph.
- [ ] Modify the demo (throwaway) to $d = 20$: where does numerical error
      creep in, and why?
