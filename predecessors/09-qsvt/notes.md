# Autopsy 10 — QSP / Qubitization / QSVT: the grand unification

*Not one problem — a language every algorithm turns out to speak.*

!!! tip "How to read this page"

    This autopsy has no advantage claim of its own to attack. QSVT is a
    **compiler**: it takes a matrix you can block-encode and applies a
    polynomial to its singular values. Every algorithm in this curriculum is
    a choice of polynomial, and that is worth knowing for exactly one
    reason —

    > **It makes the advantage question factor.**
    >
    > advantage = (an encoding classical sampling cannot imitate)
    > × (a degree classical computers cannot afford)

    Both factors are computed here rather than described, by
    [`qsp_phases.py`](qsp_phases.py) and
    [`polynomial_cost.py`](polynomial_cost.py), pinned by 39 tests. The
    payoff is §4, where Grover's $\sqrt N$, HHL's $\kappa$ and simulation's
    $t$ turn out to be the same number.

---

## 1. The problem

Gilyén–Su–Low–Wiebe 2019 (arXiv 1806.01838): given a matrix $A$
block-encoded in a unitary, apply an (almost) arbitrary bounded polynomial
$p(A)$ to its singular values, using $\deg(p)$ applications of the unitary
and **one** extra qubit. Nearly every earlier algorithm is a choice of
polynomial:

| polynomial | algorithm |
|---|---|
| $\mathrm{sign}(x)$ | search / amplitude amplification |
| approx. of $e^{-ixt}$ | Hamiltonian simulation |
| approx. of $1/x$ on $[1/\kappa, 1]$ | HHL / linear systems |
| threshold / step | phase estimation, ground states |
| approx. of $e^{-\beta x}$ | Gibbs states — hunting ground C speaks QSVT |

§4 replaces the right-hand column of that table with numbers.

---

## 2. Qubitization: one unitary, all the Chebyshevs

Block-encode Hermitian $A$ (with $\|A\| < 1$) in the walk operator

$$
W = \begin{pmatrix} A & B \\ -B & A \end{pmatrix},
\qquad B = \sqrt{I - A^2}.
$$

$W$ is unitary, and on each eigenvector of $A$ with $\lambda = \cos\theta$ it
rotates a two-dimensional invariant subspace by $\theta$ — the whole matrix
becomes a stack of independent single-qubit rotations. Consequently

$$
\big(W^d\big)_{\text{top-left}} = T_d(A),
$$

**$d$ applications of one unitary implement the degree-$d$ Chebyshev
polynomial of the encoded matrix** (verified to $10^{-10}$ in
[`test_qsvt.py`](test_qsvt.py)).

<figure markdown="span">
  ![Chebyshev polynomials from walk-operator powers](fig-chebyshev.svg#only-light)
  ![Chebyshev polynomials from walk-operator powers](fig-chebyshev-dark.svg#only-dark)
  <figcaption>What the top-left block of W^d does to each eigenvalue of A:
  Chebyshev curves T₁…T₄.</figcaption>
</figure>

Notice the same $\arccos$ that ran
[Szegedy's walks](../07-quantum-walks/notes.md): a matrix's spectrum becomes
a set of rotation angles, and powers of the operator add them. That
recurrence is the one mechanical idea underneath this whole page.

---

## 3. QSP: the phases, and what is actually hard about them

Chebyshev polynomials alone would not be a unification — they are one
family. The generalisation is to interleave the walk operator with
single-qubit rotations $e^{i\phi_k Z}$:

$$
U(x) \;=\; e^{i\phi_0 Z}\prod_{k=1}^{d}\Big[\,W(x)\,e^{i\phi_k Z}\Big],
\qquad
\mathrm{Re}\,\langle 0|U(x)|0\rangle \;=\; P(x)
$$

and the reachable $P$ are essentially **all** bounded polynomials of degree
$\le d$ and parity $d \bmod 2$. Turn the dials:

<div class="qq-anim" data-anim="qspdial"></div>

<figure markdown="span">
  ![What QSP can reach, and three algorithms as curves](fig-polynomials.svg#only-light)
  ![What QSP can reach, and three algorithms as curves](fig-polynomials-dark.svg#only-dark)
  <figcaption>Left: zero phases give Chebyshev; other phases give other
  polynomials, all bounded by 1 because they are entries of a unitary.
  Middle and right: search and simulation, as approximation problems.</figcaption>
</figure>

Two structural facts, both verified rather than assumed: the response is
always a polynomial of **exactly** degree $d$
(`test_the_response_really_is_a_polynomial_of_that_degree`), and its
**parity is forced** (`test_parity_is_forced_by_the_degree`). Parity is not
a technicality — a degree budget spent on the wrong parity buys nothing, and
`test_parity_costs_you_when_it_is_wrong` shows an even basis failing
completely on an odd target.

!!! warning "“Choosing phases is choosing your algorithm” hides a real cost"

    The phrase makes phase-finding sound free. It is not, and the usual
    explanation of why — *the map is horribly ill-conditioned* — turns out
    to be wrong when you measure it.

    `phase_map_spectrum` computes the Jacobian of response-with-respect-to-
    phases at an exact solution and takes its singular values. Two findings:

    - **Exactly one singular value is zero, at every degree tested**
      (`test_the_phase_map_has_exactly_one_gauge_direction`). That is a real
      gauge freedom of the construction, and any phase-finding routine has
      to quotient it out.
    - **Modulo that direction the conditioning is mild**, and it grows
      *sub-linearly* in $d$ — a factor under 10 across an eightfold rise in
      degree (`test_conditioning_modulo_gauge_grows_slowly`). So the local
      geometry is not the obstacle.

    What is the obstacle, then? The **search**. Phase-finding is a
    non-convex fit, and a generic solve from a random start becomes
    expensive well below the degrees §4 says real algorithms need. That is
    why dedicated phase-finding algorithms are a research area of their own
    — a cost of doing business that the slogan conceals entirely.

---

## 4. Every algorithm's parameter is a polynomial degree

This is the payoff, and it is best met as a table of measured numbers.
`polynomial_cost.py` *constructs* each approximation and reports the
smallest degree that reaches a target error:

<div class="qq-anim" data-anim="degreecost"></div>

| algorithm | polynomial | measured degree |
|---|---|---|
| search | $\mathrm{sign}(x)$ outside a gap $\delta$ | $\propto 1/\delta$ — and $\delta = 1/\sqrt N$ gives **$\sqrt N$** |
| linear systems | $1/x$ on $[1/\kappa, 1]$ | $\propto \kappa$ |
| simulation | $\cos(tx)$ | $t + O(\log 1/\varepsilon)$ |
| Gibbs states | $e^{-\beta x}$ | grows with $\beta$ |

!!! success "Grover's √N is a polynomial degree"

    Fitted exponent $-0.99$ against $\delta$, with $\text{degree} \times
    \delta$ constant to within $0.5$ across a factor of eight
    (`test_grovers_root_n_is_a_polynomial_degree`). The "iterations" of
    [autopsy 06](../06-grover/notes.md) were always the degree of an
    approximation to $\mathrm{sign}$ — and HHL's condition number is the
    same thing (fitted exponent $+0.99$ in $\kappa$).

    Three algorithms, three famous cost parameters, one quantity.

<figure markdown="span">
  ![Every cost is a degree, and the two-factor test](fig-degrees.svg#only-light)
  ![Every cost is a degree, and the two-factor test](fig-degrees-dark.svg#only-dark)
  <figcaption>Left: three parameters on one axis. Middle: who pays when you
  demand precision. Right: whether a classical sketch can reproduce the
  encoding.</figcaption>
</figure>

And now the middle panel, which is the most useful thing on this page.
Tighten $\varepsilon$ from $10^{-1}$ to $10^{-4}$ and:

- $\mathrm{sign}$'s degree goes $21 \to 73$ — **multiplicative**;
- $1/x$'s goes $27 \to 85$ — multiplicative;
- $\cos(8x)$'s goes $10 \to 16$ — **additive**
  (`test_simulation_degree_is_additive_in_precision`).

That additive-versus-multiplicative split is exactly the
$\alpha t + \log(1/\varepsilon)$ of
[autopsy 09](../08-hamiltonian-simulation/notes.md), arrived at from the
polynomial side and with nothing quantum in the derivation. It is also the
single best structural reason simulation is the healthiest application in
this curriculum.

??? note "▸ deeper — a fitting trap worth meeting once"

    Fit a power law to simulation's degree against $t$ and you get
    $t^{0.78}$ — an apparently *sublinear* cost, which would be a
    remarkable result if it were true. It is not: the correct statement is
    $\text{degree} = t + c(\varepsilon)$, and the measured $\text{degree}-t$
    is $6, 6, 8, 10, 12, 16$ across $t = 4 \dots 128$ — nearly constant.

    The additive offset dominates at small $t$ and drags the log-log slope
    below 1. `test_simulation_degree_is_linear_in_time_with_an_additive_offset`
    pins the additive form *and* the misleading exponent, because a fit that
    turns an additive law into a fake sublinear one is exactly the sort of
    thing that gets into abstracts.

---

## 5. The two-factor test

QSVT inherits its classical wall from whichever problem you instantiate — it
is a compiler, not an advantage claim. But because the compiler is uniform,
the advantage question factors cleanly, and each factor can be checked
separately:

<div class="qq-anim" data-anim="twofactor"></div>

**Factor one — is the block-encoding imitable?** Quantum-inspired classical
algorithms work by replacing the encoded matrix with a sampled low-rank
sketch. So the test is whether a sketch reproduces it:

| matrix | stable rank | error of a rank-8 sketch |
|---|---|---|
| low-rank data (rank 8) | 3.3 | $< 10^{-15}$ |
| low-rank data (rank 32) | 8.3 | 0.63 |
| sparse local Hamiltonian | 49.1 | 0.93 |

A rank-8 sketch reproduces the low-rank matrix **exactly** and the sparse
Hamiltonian **not at all** (`test_a_low_rank_encoding_is_imitable`,
`test_a_sparse_hamiltonian_is_not_imitable`). That is the difference between
an advantage [Tang can dequantise](../10-hhl-tang/notes.md) and one nobody
can — and it is decided by the *encoding*, before any polynomial is chosen.

**Factor two — is the degree unaffordable?** §4 gives it.

!!! abstract "The checklist"

    | claim | encoding | degree | verdict |
    |---|---|---|---|
    | Grover / search | not imitable | $\sqrt N$ — only quadratic | fails on degree |
    | HHL on low-rank data | **imitable** | $\kappa$ | fails on encoding |
    | HHL on sparse systems | not imitable | $\kappa$ | depends on $\kappa$ |
    | Hamiltonian simulation | not imitable | $\alpha t + \log(1/\varepsilon)$ | **passes both** |
    | Gibbs sampling | not imitable | $\beta$, spectral gap | live |

    An advantage claim has to win **both** columns. Almost every dequantised
    result in this curriculum lost the first; almost every disappointing
    speedup lost the second. The two are attacked by different communities —
    dequantisation goes after the encoding, lower bounds after the degree —
    which is why a claim can look healthy right up until the other side
    arrives.

---

## 6. The hardness evidence

None of its own, by construction (§5). But a completeness fact worth
pinning: any BQP computation can be phrased as a QSVT of a sparse
block-encoding, so *"which polynomials of which block-encodings are
classically feasible"* is a **complete language** for the advantage
question. That is what makes the two-factor test more than a mnemonic — it
is not a heuristic decomposition, it is the whole space.

!!! tip "How the Quest uses this"

    When we evaluate a hunt-phase candidate, translating it into QSVT form —
    degree × block-encoding cost — is the fastest way to see which resource
    is actually being consumed, and which factor the classical attack will
    target. §5's table is the form that translation should take.

---

## 7. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    Argue with the draft, then replace it.

    <div class="qq-lesson" markdown>

    **If all algorithms are polynomials, then advantage has exactly two
    ingredients and they can be attacked independently.** Tang attacked the
    encoding: low-rank data can be sketched, so no degree saves it.
    Hamiltonian simulation wins on the encoding (sparse, no sketch
    reproduces it) *and* is cheap in the degree (additive in
    $\log 1/\varepsilon$). Grover wins the encoding and loses the degree —
    $\sqrt N$ is a real degree, and a quadratic one is not enough to pay for
    a fault-tolerant machine.

    The strategic reading for the hunt: **we are shopping for block-encodings
    that resist sketching, attached to polynomials whose degree is large for
    a structural reason.** A DQI-style decoding step sits in the second
    factor — it is a way of making a high-degree readout affordable that
    does not go through a longer circuit.

    And the methodological reading: when a new speedup crosses your desk,
    translate it into (encoding, degree) before reading the abstract. If
    either factor is missing, the rest of the paper cannot supply it.

    </div>

Questions worth answering in your own words:

- Which factor did Tang attack? Which does Hamiltonian simulation win on?
  Where would a DQI-style decoding step sit?
- §3 found the phase map only mildly ill-conditioned. What *else* would you
  measure before believing that high-degree QSVT is practical?
- §4 shows an additive-in-precision cost is the rare and valuable one. Which
  other algorithm in this curriculum has that property, and why?

---

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/09-qsvt/qsvt_demo.py        # §2
    .venv/bin/python predecessors/09-qsvt/qsp_phases.py       # §3
    .venv/bin/python predecessors/09-qsvt/polynomial_cost.py  # §4-§5
    .venv/bin/pytest predecessors/09-qsvt -q                  # 39 tests
    ```

- [ ] Verify the 2×2 rotation claim by hand: for eigenvalue
      $\lambda = \cos\theta$, write $W$'s action on the invariant plane and
      obtain the rotation matrix. This IS the theorem; ten lines.
- [ ] Grover from QSVT: which $A$, which polynomial, and where does
      $\sqrt N$ appear as a *degree*? Check your answer against §4's first
      table row, which measures it.
- [ ] Modify `qsvt_demo.py` (throwaway) to $d = 20$: where does numerical
      error creep in, and why?
- [ ] **New.** §3 measures exactly one gauge direction in the phase map.
      Identify it analytically — which change to the phases leaves
      $\mathrm{Re}\langle 0|U|0\rangle$ untouched? (One line, once you see
      it.)
- [ ] **New.** `degree_for_gibbs` is in `polynomial_cost.py` but does not
      appear in §4's fitted table. Work out its scaling in $\beta$, and say
      what that predicts for hunting ground C's cost at low temperature.
- [ ] **The uncomfortable one.** §5 claims the two-factor test is complete,
      not heuristic. Try to construct a quantum advantage that passes
      neither box yet is still real — or convince yourself why you cannot,
      and write down the argument.
