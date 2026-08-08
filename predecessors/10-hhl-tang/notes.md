# Autopsy 11 — HHL (2009) and Tang (2018): how an advantage dies

*The red-team chapter. Watch an exponential speedup evaporate.*

!!! tip "How to read this page"

    This is the autopsy where the curriculum's method gets used on a real
    corpse, so the discipline is to price every caveat rather than list it.
    "There is a caveat" and "the caveat costs $10^{10}$ state preparations"
    are different sentences, and only the second one settles an argument.

    Everything here is computed by [`hhl_tolls.py`](hhl_tolls.py) and
    [`dequantize.py`](dequantize.py), pinned by 23 tests — including an
    **audit** that the dequantised solver never reads the rows it did not
    sample, because a dequantisation demo that quietly touches the whole
    matrix proves nothing.

    Two sentences to carry:

    > **HHL's polylog is the cost of preparing a state, and the state is not
    > the answer.**
    >
    > **Whatever preparation power the quantum side is granted, the
    > classical side gets its sampling analogue** — and then the comparison
    > is fair.

---

## 1. The problem

HHL (Harrow–Hassidim–Lloyd): "solve" $Ax = b$ — more precisely, prepare a
quantum state $\propto A^{-1}|b\rangle$ — in time
$\mathrm{polylog}(\dim)$ for well-conditioned sparse $A$. It launched a
decade of quantum machine learning: recommendation systems, PCA, clustering,
SVMs, all claiming exponential speedups.

The primitive is legitimate — it is QSVT with $p(x) \approx 1/x$
([autopsy 10 §4](../09-qsvt/notes.md) measures that polynomial's degree as
$\propto \kappa$) and it is BQP-complete in the right regime. **The
primitive is not the problem.** The problem is four tolls at the door
(Aaronson 2015, *"Read the fine print"*), and this page charges each of
them.

---

## 2. Toll 3 first: the output is a state

Take the tolls out of order, because this one decides the most and is
argued about the least.

<div class="qq-anim" data-anim="readout"></div>

| what you want | cost | verdict |
|---|---|---|
| one amplitude $x_i$ | $O(1/\varepsilon^2)$ | cheap — dimension-free |
| an expectation $\langle x|M|x\rangle$ | $O(1/\varepsilon^2)$ | cheap, if $M$ is simple |
| the whole vector $x$ | $O(\dim/\varepsilon^2)$ | **the toll** |

At $\dim = 10^6$ and $\varepsilon = 10^{-2}$: one amplitude costs about
$1.8\times10^4$ repetitions regardless of dimension, and the whole vector
costs $8.8\times10^{10}$ (`test_reading_the_vector_costs_the_dimension`).

The algorithm runs in $\mathrm{polylog}(\dim)$ and hands you an object that
costs $\dim$ to look at. Every honest application therefore has to end in
**one number** — which is a real claim, and a far narrower one than "quantum
computers solve linear systems".

---

## 3. Toll 2: κ is an assumption, not a fact

$\kappa$ enters the runtime linearly (QSVT-era; quadratically in the
original). So "well-conditioned" is load-bearing — and on the textbook
sparse system it is false:

| dimension | condition number | growth |
|---|---|---|
| 16 | 116 | — |
| 64 | 1712 | ×3.88 |
| 256 | 26768 | ×3.97 |

The discrete Laplacian's $\kappa$ grows like $\dim^2$
(`test_the_laplacian_condition_number_grows_quadratically`, fitted exponent
$2.0$). A $\kappa$ that grows polynomially in the dimension eats a
$\log(\dim)$ advantage outright.

---

## 4. The comparison nobody runs

Now put the tolls together against the *right* classical baseline. For a
sparse symmetric system that baseline is not Gaussian elimination, it is
**conjugate gradients** — and CG needs $O(\sqrt{\kappa}\log(1/\varepsilon))$
iterations. Note the square root, which the quantum algorithm does not have.

<figure markdown="span">
  ![The tolls, priced](fig-tolls.svg#only-light)
  ![The tolls, priced](fig-tolls-dark.svg#only-dark)
  <figcaption>Left: the output toll. Middle: κ for the textbook sparse
  system. Right: the same comparison run twice — once as it is usually
  quoted, once with both sides returning the same object.</figcaption>
</figure>

!!! danger "Two comparisons, and only one of them is fair"

    **(a) As usually quoted.** HHL prepares a *state*; CG returns the
    *vector*. Even here the story is not an exponential: CG pays
    $\sqrt\kappa$ and the quantum algorithm pays $\kappa$, so the crossover
    dimension moves **right** as the problem gets harder
    (`test_the_unfair_crossover_moves_right_as_kappa_grows`) — the opposite
    of what an exponential speedup should do.

    **(b) With matched outputs.** Ask both sides for $x$. Then the quantum
    route costs its state preparation *times* the readout, and it loses by
    $10^8$ at $\dim = 10^3$ and by $10^{10}$ at $\dim = 10^6$
    (`test_readout_makes_hhl_strictly_worse_than_cg`). **There is no
    crossover to find.**

    The polylog is real. It is the price of preparing a state, and the state
    is not the answer.

---

## 5. Toll 4: Tang, and the access model

The fourth toll is the famous one. **Tang 2018** (then a 22-year-old
student), followed by the full quantum-inspired programme (Tang, Gilyén,
Chia, Lin, Wang, …): if the quantum algorithm assumes state-preparation
access to the data, the honest classical comparison is
**$\ell^2$-sampling access** — and with it, classical algorithms match every
low-rank QML speedup up to polynomial factors.

<div class="qq-anim" data-anim="sqsample"></div>

The identity is three lines. Sample rows with $p_i \propto \|A_i\|^2$,
rescale by $1/\sqrt{r p_i}$, and the sketch $S$ satisfies

$$
\mathbb{E}\big[S^\top S\big] = A^\top A ,
$$

so $S$'s right singular vectors approximate $A$'s — *which is exactly what
quantum state preparation was quietly doing for free*
(`test_the_sketch_is_unbiased` checks it by sampling, not by algebra).

<figure markdown="span">
  ![Dequantization in one picture](fig-dequantized.svg#only-light)
  ![Dequantization in one picture](fig-dequantized-dark.svg#only-dark)
  <figcaption>The FKV sketch: 200 ℓ²-sampled rows of an 800×800 low-rank
  matrix reconstruct the optimal rank-5 projection to within ~2%. The
  "exponential" advantage never lived in the quantum processing — it lived
  in an unfair comparison of access models.</figcaption>
</figure>

`dequantize.py` goes further and implements the access model as a data
structure with a **query counter**, writing the solver against that
interface and nothing else. On a $600\times600$ rank-5 problem:

| rows sampled | % of A | median relative error |
|---|---|---|
| 8 | 1.3% | 0.220 |
| 32 | 5.3% | 0.084 |
| 128 | 21.3% | 0.044 |

and `test_the_solve_never_reads_the_whole_matrix` asserts the counter stayed
below 10% of the entries. The classical algorithm returns **the vector**,
which is the object HHL does not give you.

---

## 6. Where dequantisation stops — the useful half

The famous result is negative. The useful content is the boundary, because
it marks out where an advantage could still live:

<figure markdown="span">
  ![Where dequantisation works and where it stops](fig-boundary.svg#only-light)
  ![Where dequantisation works and where it stops](fig-boundary-dark.svg#only-dark)
  <figcaption>Rows the classical algorithm must read, against the rank of
  the data. The shaded gap is Tang's result; the right-hand panel is the
  variable sampling actually responds to.</figcaption>
</figure>

The sample count tracks the **rank**, not the dimension
(`test_sample_cost_tracks_rank_not_dimension`): a $400\times400$ problem
falls to a few dozen rows whenever the rank is small, and a bigger matrix of
the same rank costs no more. As the rank climbs, the sketch has to read more
and more of $A$ until the shortcut is gone.

!!! success "An anomaly worth keeping"

    Nominal rank 2 needs *more* rows than rank 10. That is not noise: its
    **stable rank** $\|A\|_F^2/\|A\|_2^2$ is only 1.1, so 96% of the weight
    sits in a single direction — and length-squared sampling sees directions
    in proportion to their weight
    (`test_stable_rank_is_the_variable_sampling_responds_to`).

    **Nominal rank counts directions; stable rank weighs them, and sampling
    responds to the second.** Worth knowing before repeating "low rank means
    dequantisable" — the true condition is about how the weight is
    distributed, and it is computable in one line for any candidate.

!!! warning "And the nuance both camps skip"

    The dequantised algorithms match the quantum ones **up to polynomial
    factors**, and those polynomials are enormous — early versions carried
    $\mathrm{rank}^6$ and $\kappa^6$. So the honest verdict has two halves:
    the *exponential* claim is dead, **and** a large polynomial gap can
    still be real. Quantum partisans quote the second half; dequantisation
    partisans quote the first.

What survives of HHL: the BQP-complete regime — sparse, well-conditioned,
**high-rank** $A$, with $|b\rangle$ produced by a *quantum process* rather
than loaded from data, and an answer that is one expectation value.
Survivors are quantum-native; the casualties were classical data wearing a
quantum costume.

---

## 7. The rule this autopsy leaves behind

<div class="qq-anim" data-anim="accessrule"></div>

!!! danger "Access-model symmetry — a law for the Quest"

    Whatever preparation power we grant a quantum algorithm, the classical
    baseline gets its sampling analogue. We apply this to **our own** claims
    first. Any future result that dies under this rule was never a result.

    Note precisely which of our hunting grounds are immune and why: not
    because they are cleverer, but because **there is no data set to
    sample**. A Hamiltonian is a description, not a matrix of measurements;
    a Gibbs state of a non-commuting Hamiltonian has no classical
    $\ell^2$-sampling access to be granted. That is the same
    quantum-native-input immunity
    [autopsy 09 §7](../08-hamiltonian-simulation/notes.md) identifies, and
    it is the most durable structural property in this curriculum.

---

## 8. The lesson — YOUR TURN

!!! abstract "Write this section yourself — it is the red-team charter"

    Argue with the draft, then replace it.

    <div class="qq-lesson" markdown>

    **An advantage claim is a claim about two access models, not about one
    algorithm.** HHL's exponential lived entirely in the asymmetry: the
    quantum side was handed state-preparation access to classical data and
    the classical side was not given its analogue. Restore the symmetry and
    the exponential disappears — while leaving a polynomial gap that is real
    and rarely quoted.

    The checklist that follows, and that belongs in the Problem-Shape
    Catalog:

    1. **Where does the input come from?** If it is classical data, grant
       the classical side $\ell^2$-sampling and re-run the comparison.
    2. **What is the output?** If it is a vector rather than one number,
       add the readout toll — §4 shows it is decisive.
    3. **What is $\kappa$, really?** Measure it on the actual instances;
       "well-conditioned" is an assumption.
    4. **What is the *stable* rank?** Not the nominal rank — §6 shows they
       disagree, and sampling responds to the stable one.
    5. **Is the classical baseline the best known algorithm?** For sparse
       systems that is conjugate gradients, and it pays only $\sqrt\kappa$.

    </div>

Questions worth answering in your own words:

- State the access-model symmetry rule in your own words. Which of our
  hunting grounds is structurally immune, and why exactly?
- §6 shows dequantisation leaves a large polynomial gap. Under what
  conditions would that gap be worth a fault-tolerant quantum computer?
  (Use [autopsy 06's](../06-grover/notes.md) pricing.)
- Which of the five checklist items would have killed the 2016
  recommendation-systems claim on the day it was posted?

---

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/10-hhl-tang/fkv.py          # the sketch
    .venv/bin/python predecessors/10-hhl-tang/hhl_tolls.py    # §2-§4
    .venv/bin/python predecessors/10-hhl-tang/dequantize.py   # §5-§6
    .venv/bin/pytest predecessors/10-hhl-tang -q              # 23 tests
    ```

- [ ] Prove $\mathbb{E}[S^\top S] = A^\top A$ for the rescaled row sample
      (three lines). This identity IS the dequantisation.
- [ ] One paragraph: why does $\ell^2$-sampling access to a *Gibbs state of a
      non-commuting Hamiltonian* not exist classically? Be precise about
      where the analogy breaks — this is why hunting ground C survives
      Tang-style attacks.
- [ ] **New.** §6's anomaly: construct a matrix of nominal rank 50 whose
      stable rank is under 3, and predict — before running it — how many
      rows `rows_needed` will ask for. Then run it.
- [ ] **New.** `sq_solve` currently reads whole rows. Tang's algorithms
      subsample *within* rows too, so the cost becomes independent of the
      dimension. Add column subsampling and measure what it costs in
      accuracy. (This is the step that turns "reads 5% of A" into "reads
      polylog of A".)
- [ ] **The uncomfortable one.** Take the most recent quantum-machine-
      learning speedup you find persuasive and run all five checklist items
      against it, writing your answers down before searching for whether
      someone has already dequantised it.
