# Autopsies 07–08 — Quantum walks: glued trees and Szegedy

*The only exponential speedup in this course that owes nothing to the Fourier
transform.*

## 1. The problem(s)

Traversal and search on graphs. Two exemplars:

- **Glued trees** (Childs–Cleve–Deutsch–Farhi–Gutmann–Spielman 2003): two full
  binary trees of depth $d$, leaves joined by a random cycle. Enter at the
  left root; **find the right root**. Oracle = adjacency access.
- **Markov-chain search** (Szegedy 2004; Magniez–Nayak–Roland–Santha): find
  marked states of a reversible chain faster than its mixing time.

## 2. The classical wall

A classical walker drifts INTO the exponentially fat middle — from each side,
2 of 3 edges point inward — and provably needs $2^{\Omega(d)}$ steps; the
random cycle prevents even clever algorithms from learning where they are.

## 3. The primitive

**Interference against the drift.** By symmetry both walks live in the
$(2d+2)$-dimensional *column space* (which is how our code simulates a
$\sim 2^{d+2}$-vertex graph exactly). There the reduced Hamiltonian is a
near-uniform path — hopping $\sqrt 2$, with weight $2$ at the glue — and a
wave packet crosses **ballistically**: the path graph's dispersion relation
gives a linear light cone where the diffusive classical walker moves as
$\sqrt t$ and is pushed back by the drift.

<figure markdown="span">
  ![Quantum vs classical exit probability](fig-separation.svg#only-light)
  ![Quantum vs classical exit probability](fig-separation-dark.svg#only-dark)
  <figcaption>Our simulation: the quantum walk (time ≈ 0.8·d) holds a ~0.4
  exit probability while the classical walk — given a d³ step budget — decays
  exponentially. At d = 20 the ratio is 638 and doubling every few
  levels.</figcaption>
</figure>

Szegedy's discretization makes the mechanism systematic: quantize any
reversible chain $P$ into a walk whose eigenphases are $\arccos$ of $P$'s
eigenvalues — a classical spectral gap $\delta$ becomes a quantum phase gap
$\sqrt\delta$. Hence hitting/search in $\sim 1/\sqrt\delta$ where classical
needs $\sim 1/\delta$ (the MNRS framework behind element distinctness,
triangle finding, and friends).

!!! tip "Bridge to hunting ground C"

    Quantum Gibbs samplers (Autopsy 13) hunt exactly this $\sqrt{}$-vs-linear
    gap structure — but in *open-system* dynamics, where the target is a
    thermal state rather than a marked vertex. Same spectral instinct, harder
    detailed-balance constraints.

## 4. The hardness evidence

Glued trees: an **unconditional exponential query separation** — the
classical lower bound is a theorem, no assumptions. The eternal catch: it is
an oracle result, and twenty years have produced no compelling instantiation.
*Exponential speedup, no customer.* Szegedy walks: mostly quadratic, honest,
and — like amplitude amplification — overhead-prone in practice.

## 5. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    The glued-trees speedup needed a graph *engineered* so classical drift
    fails while quantum dispersion sails — what does that teach about where
    walk advantages live "in nature"? Why does $\sqrt{\text{gap}}$ cap most
    walk speedups at quadratic, and what structural extras does an
    exponential walk advantage seem to require?

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/07-quantum-walks/glued_trees.py
    .venv/bin/pytest predecessors/07-quantum-walks -q
    ```

- [ ] Derive the reduced path weights ($\sqrt 2$ inside the trees, $2$ at the
      glue) from the column-state normalization
      $|{\rm col}_j\rangle = \frac{1}{\sqrt{N_j}}\sum_{v \in {\rm col}_j}|v\rangle$
      — five lines.
- [ ] Explain the classical column chain's $2/3$-vs-$1/3$ bias from vertex
      degrees, and why making the exit absorbing only *helps* the classical
      side (so our comparison is fair).
- [ ] One paragraph: why is the glued-trees oracle hard to instantiate? What
      would a real function have to hide — and compare with $a^x \bmod N$.
