# Autopsy 11 — HHL (2009) and Tang (2018): how an advantage dies

*The red-team chapter. Watch an exponential speedup evaporate.*

## 1. The problem

HHL (Harrow–Hassidim–Lloyd): "solve" $Ax = b$ — more precisely, prepare a
quantum state $\propto A^{-1}|b\rangle$ — in time $\mathrm{polylog}(\dim)$
for well-conditioned sparse $A$. It launched a decade of quantum machine
learning: recommendation systems, PCA, clustering, SVMs, all claiming
exponential speedups.

## 2. The classical wall (as it appeared)

Classical linear algebra is $\mathrm{poly}(\dim)$. An exponential speedup on
the most common computation in the world — if true, the biggest result since
Shor.

## 3. The primitive

QSVT with $p(x) \approx 1/x$ (historically: phase estimation + a controlled
rotation). Legitimate, and BQP-complete in the right regime — **the primitive
is not the problem.** The problem is the fine print (Aaronson 2015, *"Read
the fine print"*), four separate tolls at the door:

1. Preparing $|b\rangle$ from classical data needs QRAM / state-preparation —
   the *input toll*.
2. Condition number $\kappa$ and sparsity enter polynomially.
3. The output is a *state*, not a vector: reading all of $x$ costs
   $\dim$ samples — the *output toll*.
4. If $A$ is **low-rank** — as in all the ML applications — see below.

## 4. The hardness evidence — collapsed

**Tang 2018** (then a 22-year-old student), followed by the full
"quantum-inspired" program (Tang, Gilyén, Chia, Lin, Wang, …): if the quantum
algorithm assumes state-preparation access to the data, the honest classical
comparison is **$\ell^2$-sampling access** — and with it, classical
algorithms match every low-rank QML speedup up to polynomial factors.

The core identity is three lines: sampling rows with
$p_i \propto \|A_i\|^2$ and rescaling by $1/\sqrt{r\,p_i}$ gives a small
sketch $S$ with

$$
\mathbb{E}\big[S^\top S\big] = A^\top A ,
$$

so $S$'s right singular vectors approximate $A$'s — *which is exactly the
thing quantum state preparation was secretly doing for free.*

<figure markdown="span">
  ![Dequantization in one picture](fig-dequantized.svg#only-light)
  ![Dequantization in one picture](fig-dequantized-dark.svg#only-dark)
  <figcaption>Our implementation of the FKV sketch: 200 ℓ²-sampled rows of an
  800×800 low-rank matrix reconstruct the optimal rank-5 projection to within
  ~2%. The "exponential" advantage never lived in the quantum processing — it
  lived in an unfair comparison of access models.</figcaption>
</figure>

What survives of HHL: the BQP-complete regime — sparse, well-conditioned,
**high-rank** $A$, with $|b\rangle$ produced by a *quantum process* rather
than loaded from data. Survivors are quantum-native; the casualties were
classical data wearing a quantum costume.

!!! danger "Access-model symmetry — a law of nature for the Quest"

    Whatever preparation power we grant a quantum algorithm, the classical
    baseline gets its sampling analogue. We apply this to OUR OWN claims
    first. Any future result that dies under this rule was never a result.

## 5. The lesson — YOUR TURN

!!! abstract "Write this section yourself — it is the red-team charter"

    State the access-model symmetry rule in your own words. Which of our two
    hunting grounds is structurally immune to this attack, and why, exactly?
    Then write the checklist you would run against a new QML-advantage paper
    — and keep it; it goes in the Problem-Shape Catalog.

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/10-hhl-tang/fkv.py
    .venv/bin/pytest predecessors/10-hhl-tang -q
    ```

- [ ] Prove $\mathbb{E}[S^\top S] = A^\top A$ for the rescaled row sample
      (three lines). This identity IS the dequantization.
- [ ] One paragraph: why does $\ell^2$-sampling access to a *Gibbs state of a
      non-commuting Hamiltonian* not exist classically? Be precise about
      where the analogy breaks — this is why hunting ground C survives
      Tang-style attacks.
