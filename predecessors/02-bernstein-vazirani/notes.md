# Autopsy 02 — Bernstein–Vazirani (1993)

*Same circuit, different problem — the lesson of the whole course in one page.*

## 1. The problem

Oracle access to $f(x) = s\cdot x \bmod 2$ for a hidden $s \in \{0,1\}^n$.
**Find $s$.** That is $n$ bits of information hidden inside a linear structure.

Who cared: this comes from *"Quantum Complexity Theory"* (Bernstein & Vazirani,
STOC 1993) — the paper that **defined BQP**. They needed evidence separating
BQP from BPP; this problem is the building block, and its recursive version
(Recursive Fourier Sampling) gave the first superpolynomial oracle separation.
The problem served complexity theory rather than applications — but this time
the separation *survives randomness*.

## 2. The classical wall

Each classical query returns ONE bit; $s$ contains $n$ bits. So $n$ queries
are necessary — and $n$ suffice: query the unit vectors,
$f(e_i) = s_i$. Unlike Deutsch–Jozsa, **randomization does not help**: the
bound is information-theoretic, $\Omega(n)$ even for bounded-error algorithms.

The honest ledger so far:

| | separation | robust to randomness? |
|---|---|---|
| Deutsch–Jozsa | exponential | :material-close: dies at $O(1)$ |
| Bernstein–Vazirani | $n$ vs $1$ — polynomial | :material-check: information-theoretic |
| Simon (next) | **exponential** | :material-check: **robust** |

Big *and* robust at once is Simon's problem — the escalation that provoked Shor.

## 3. The primitive

**The circuit is gate-for-gate identical to Deutsch–Jozsa.** Same Hadamard
sandwich, same single phase-oracle call. Only the promise changed.

Why it works: $(-1)^{s\cdot x}$ is a *character* of the group
$\mathbb{Z}_2^n$, and $H^{\otimes n}$ is the Fourier transform over
$\mathbb{Z}_2^n$. The Fourier transform of a character is a delta function:

$$
H^{\otimes n}\left[\frac{1}{2^{n/2}}\sum_x (-1)^{s\cdot x}\,|x\rangle\right]
= |s\rangle .
$$

After the sandwich, *all* amplitude sits on $|s\rangle$: one measurement, all
$n$ bits.

<figure markdown="span">
  ![All amplitude on the secret](fig-delta.svg#only-light)
  ![All amplitude on the secret](fig-delta-dark.svg#only-dark)
  <figcaption>Our simulator, n = 4, s = 1011: the post-circuit distribution is
  a perfect delta on the secret. Not approximately — exactly.</figcaption>
</figure>

The general mechanism, named: **Fourier sampling.** Measuring after
$H^{\otimes n}$ samples $y$ with probability $|\hat g(y)|^2$, where
$g(x) = (-1)^{f(x)}$ — one query buys one sample from the *Fourier spectrum*
of $f$, which classically can cost exponentially many evaluations. Problems
whose answer is written in the **location of Fourier mass** are quantum-native.

!!! question "Stop and think"

    If the gates are identical to DJ's, where exactly does the extra power
    come from?

    ??? success "The point of this entire autopsy"

        From the *problem structure*. The promise "f is a character" makes the
        Fourier spectrum a delta; the promise "f is constant-or-balanced" only
        makes the zero-frequency coefficient informative. Same transform,
        different spectra. The algorithm content lives in the problem, not in
        the circuit — which is why our hunt is problem-first.

## 4. The hardness evidence

Information-theoretic, unconditional, robust to randomness — the cleanest kind
of lower bound we will ever meet. And also the reason it caps at $n$ vs $1$:
counting bits can never give more than a factor-$n$ separation. To beat it,
the answer must hide so that each classical query reveals *almost nothing* —
not merely few bits. That is Simon's move (Autopsy 03).

## 5. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    One paragraph, own words. React to: where exactly did the power come from,
    given identical gates? What problem-shape wants "answer = location of
    Fourier mass"? $\mathbb{Z}_2^n$ is the baby group — what changes when the
    group becomes $\mathbb{Z}_N$? (That question is Week 2.)

## Exercises

### Code (make the tests green)

- [ ] Implement `bernstein_vazirani(oracle, n)` in
      [`bernstein_vazirani.py`](bernstein_vazirani.py) —
      `pytest predecessors/02-bernstein-vazirani` must pass.
      Honor system: exactly ONE `apply` of the oracle.

### Proof draft #0 *(graded against `curriculum/solutions.md` — draft first!)*

- [ ] Prove: **(a)** any deterministic algorithm needs $\ge n$ queries;
      **(b)** any randomized algorithm with success probability $\ge 2/3$
      needs $\Omega(n)$ queries. Make (b) rigorous — "each query gives one
      bit" is intuition, not a proof. (Routes: counting over the $2^n$
      candidate secrets, an adversary argument; Yao's principle is your
      friend for (b).)

### Proof draft (yours)

*(write here)*
