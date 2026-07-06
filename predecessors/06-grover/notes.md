# Autopsy 06 — Grover (1996), amplitude amplification, and the BBBV ceiling

*The quadratic workhorse — and the theorem that fences our whole hunt.*

## 1. The problem

Find the marked item among $N$ with oracle access. Real pedigree
(search / SAT as generic problems), but note what's missing: **structure**.
That absence is the theme of this autopsy.

## 2. The classical wall

$\Theta(N)$ queries, trivially — and that triviality is the point. Nothing to
exploit means nothing for interference to grab.

## 3. The primitive

**Amplitude amplification** — the algorithm's real content
(Brassard–Høyer–Mosca–Tapp 2000). The state never leaves the 2D plane spanned
by $|w\rangle$ (marked) and $|{\rm rest}\rangle$; oracle + diffusion compose
into a rotation by $2\theta$ with $\theta = \arcsin\sqrt{k/N}$, so after $j$
iterations

$$
P(\text{success}) = \sin^2\!\big((2j+1)\,\theta\big).
$$

After $\sim \frac{\pi}{4}\sqrt{N/k}$ steps the state points at the marked
item. Not a "keep trying" method — a precisely timed one:

<figure markdown="span">
  ![Grover is a rotation](fig-rotation.svg#only-light)
  ![Grover is a rotation](fig-rotation-dark.svg#only-dark)
  <figcaption>Our circuit (n = 8) matches the rotation formula to 1e−10. At
  the optimal k = 12 the success probability is 0.9999; run twice as long and
  it falls to 0.58 — the rotation sails past the target. More queries can be
  worse.</figcaption>
</figure>

The other export: **amplitude estimation** — phase-estimate the rotation to
learn $k/N$ with quadratically fewer samples than classical Monte Carlo. This
is the engine inside most claimed "quadratic speedup" applications, including
the Kikuchi-method planted-inference results at the modern frontier.

## 4. The hardness evidence — and the ceiling

**BBBV (1997), proved *before* Grover was discovered:** any quantum algorithm
needs $\Omega(\sqrt N)$ queries for unstructured search. Quadratic is
*optimal* — a ceiling, not a floor.

Proof shape (hybrid argument — draft it; skeleton in
`curriculum/solutions.md`): run the algorithm on the empty oracle and let
$q_x = \sum_t |\alpha_{x,t}|^2$ be the total query attention on item $x$.
Some $x$ gets $q_x \le T/N$; marking it changes the final state by at most
$2\sum_t |\alpha_{x,t}| \le 2\sqrt{T\,q_x} \le 2T/\sqrt N$ (Cauchy–Schwarz).
Distinguishing needs constant trace distance $\Rightarrow T = \Omega(\sqrt N)$.

!!! warning "The theorem that draws our map"

    The generalization (Aaronson–Ambainis line): for problems invariant under
    permuting inputs, quantum speedup is at most polynomial. **No structure
    ⇒ no exponential advantage.** This is why the Quest hunts exclusively in
    structured territory — the fence is a theorem, not a taste.

Practical fine print for the honest ledger: on hardware, quadratic speedups
are expected to be eaten by fault-tolerance overhead at any feasible size.
Grover is a magnificent subroutine and a terrible flagship.

## 5. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    Why is "the ceiling was proved before the algorithm existed" the
    healthiest event in this whole curriculum? What does the 2D-rotation
    picture say about where Grover's power comes from — and why that power
    cannot compound?

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/06-grover/grover.py
    .venv/bin/pytest predecessors/06-grover -q
    ```

- [ ] **Proof draft #3:** the BBBV bound via the hybrid argument. Draft
      before reading the sketch.
- [ ] Explain the overshoot number: for $n=6$, $2k_{\rm opt}=12$ iterations
      gives $p \approx{}$? Compute $(2\cdot 12 + 1)\,\theta$ and see.
- [ ] Amplitude estimation in one paragraph: how does phase estimation on the
      Grover rotation turn $k/N$ into a readable phase?
