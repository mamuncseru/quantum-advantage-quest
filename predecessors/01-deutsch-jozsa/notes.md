# Autopsy 01 — Deutsch–Jozsa (1992)

*Interference works — and the field's first weak-baseline incident.*

## 1. The problem

A promise problem. Oracle access to $f:\{0,1\}^n \to \{0,1\}$, **promised** to
be either *constant* (same value everywhere) or *balanced* (each value on
exactly half the inputs). Decide which, minimizing oracle queries.

Who cared about this problem before quantum computing? **Nobody.** It was
reverse-engineered to fit the mechanism: Deutsch (1985) asked *"can
interference compute something with provably fewer queries, even in
principle?"* — and the problem was constructed as a showcase. DJ is a solution
in search of a problem. Knowing that is part of the lesson, not a dismissal.

## 2. The classical wall

- Deterministic, exact: $2^{n-1}+1$ queries in the worst case — you can see
  half the inputs agree and still not know.
- **Randomized:** $O(1)$ queries for bounded error. Sample $k$ random inputs;
  any disagreement $\Rightarrow$ balanced; all equal $\Rightarrow$ constant,
  wrong with probability $\le 2^{-(k-1)}$ under the promise.

So the "exponential separation" holds only against deterministic *exact*
computation. The wall is real, but thin.

## 3. The primitive

The whole algorithm is a Hadamard sandwich around one phase-oracle call:

```text
|0…0⟩ ──H⊗ⁿ──►  uniform  ──O_f──►  Σₓ (−1)^f(x) |x⟩ / 2^(n/2)  ──H⊗ⁿ──►  measure
```

The amplitude left on $|0\dots0\rangle$ at the end is

$$
\frac{1}{2^n}\sum_{x\in\{0,1\}^n} (-1)^{f(x)}
\;=\;
\text{the \emph{mean} of } (-1)^f .
$$

Constant $f \Rightarrow \pm 1$ (measured with certainty). Balanced
$f \Rightarrow$ exactly $0$ (never observed). One query computed a **global
property** of $f$ — something no single classical evaluation can see.

<figure markdown="span">
  ![Deutsch–Jozsa interference readout](fig-interference.svg#only-light)
  ![Deutsch–Jozsa interference readout](fig-interference-dark.svg#only-dark)
  <figcaption>Real output of <code>deutsch_jozsa.py</code> on our simulator
  (n = 10). Constant functions land on 1, balanced on 0 — and the yellow bar
  is a function <em>outside</em> the promise, where the answer (0.25) means
  nothing. The promise is load-bearing.</figcaption>
</figure>

Two ideas here outlive the algorithm:

- **Phase kickback** moves data into phases, where interference can act:
  $|x\rangle|-\rangle \;\mapsto\; (-1)^{f(x)}|x\rangle|-\rangle$.
  (Proved equivalent to the phase oracle in
  `qsim/test_qsim.py::test_phase_kickback_ties_the_two_oracle_forms`.)
- $H^{\otimes n}$ is the **Fourier transform over $\mathbb{Z}_2^n$**, so the
  $|0\dots0\rangle$ amplitude is the Fourier coefficient of $(-1)^f$ at
  frequency $0$. Superposition alone computes nothing readable; *interference
  concentrating a global property onto a measurable state is the whole game.*

!!! question "Stop and think"

    Before you read section 2 again: why does randomness collapse this
    particular wall, and what would a problem need so that randomness *doesn't*
    help?

    ??? success "One answer"

        A random classical sample already estimates the *mean* of $(-1)^f$
        cheaply — DJ's global property is statistically easy. Randomness stops
        helping when each query carries almost no information about the answer
        until an exponentially rare event occurs. That design principle is
        Simon's problem (Autopsy 03).

## 4. The hardness evidence

Only versus deterministic exact classical computation; the randomized baseline
collapses the gap to $O(1)$ vs $1$. **This is the field's founding
weak-baseline incident (1992)** — the first named quantum algorithm's
advantage dies against the right classical baseline. What genuinely survives:
the exact/deterministic separation, and — much more importantly — the
mechanism.

!!! warning "The fine print of the query model — pinned here, once and for all"

    The model charges one unit per oracle call and *nothing* for having the
    oracle. A query separation becomes a real-world separation only when the
    oracle can be **instantiated** by an efficient circuit for a problem
    someone cares about. Shor instantiated; most oracle results never do. Our
    own `phase_oracle` builds a dense $2^n$ matrix — exponential classical
    work the model doesn't count. Feel that.

## 5. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    One paragraph, your own words: what *shape* of problem does this mechanism
    want? What died against the randomized baseline, and what survived? This
    paragraph becomes a Problem-Shape Catalog entry in week 5.

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/01-deutsch-jozsa/deutsch_jozsa.py
    .venv/bin/pytest predecessors/01-deutsch-jozsa -q
    ```

- [ ] Read [`deutsch_jozsa.py`](deutsch_jozsa.py) against §3 until every line
      is obvious.
- [ ] The demo includes an $f$ outside the promise (AND of two bits,
      $p_0 = 1/4$). In one sentence: why is the promise load-bearing for the
      interference pattern, not just for interpreting the output?
- [ ] Write §5.
