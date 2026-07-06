# Autopsy 03 — Simon (1994)

*The first big-and-robust separation — and the paper that triggered Shor.*

## 1. The problem

Oracle $f:\{0,1\}^n \to \{0,1\}^n$, promised 2-to-1 with a hidden XOR mask:

$$
f(x) = f(y) \iff y = x \oplus s .
$$

**Find $s$.**

Who cared: nobody, yet — like Deutsch–Jozsa it is a designed problem. But this
one was designed to fix DJ's fatal flaw: an exponential separation that
*survives randomness*. Simon's paper was initially rejected; one of its
referees was Peter Shor, who saw what it implied. Within months Shor had
replaced the group $\mathbb{Z}_2^n$ with $\mathbb{Z}_N$ — and factoring fell.
**Simon's is the most consequential "useless" problem in the history of
computing.**

## 2. The classical wall

Any classical algorithm — randomized included — needs $\Omega(2^{n/2})$
queries. Values of $f$ at distinct points look uniformly random until you hit
a *collision* $f(x) = f(x\oplus s)$, and by the birthday bound that takes
$\sim 2^{n/2}$ samples. Until a collision appears, everything seen is
consistent with exponentially many candidate secrets: each query eliminates
almost nothing.

!!! tip "The design principle DJ lacked"

    Not *"each query gives few bits"* (BV's wall — capped at a factor $n$) but
    *"each query gives almost zero information about the answer until an
    exponentially rare event occurs."* Every exponential separation we will
    meet has a version of this property.

## 3. The primitive

Same Hadamard sandwich, one new register:

```text
|0⟩|0⟩ ──H⊗ⁿ (reg 1)──►  Σₓ|x⟩|0⟩  ──O_f──►  Σₓ|x⟩|f(x)⟩  ──H⊗ⁿ (reg 1)──►  measure reg 1 → y
```

The second register entangles each $|x\rangle$ with its $f$-value. Since $f$
is constant exactly on the cosets $\{x,\, x\oplus s\}$, interference happens
*within cosets*: the amplitude at $y$ picks up

$$
(-1)^{x\cdot y} + (-1)^{(x\oplus s)\cdot y}
= (-1)^{x\cdot y}\big(1 + (-1)^{s\cdot y}\big),
$$

which **vanishes unless $s\cdot y = 0$**. Each run returns a uniform sample
from the subspace orthogonal to $s$; $n-1$ independent samples plus Gaussian
elimination over $\mathbb{F}_2$ recover $s$.

<figure markdown="span">
  ![Samples land only in the orthogonal subspace](fig-subspace.svg#only-light)
  ![Samples land only in the orthogonal subspace](fig-subspace-dark.svg#only-dark)
  <figcaption>4000 runs on our simulator (n = 4, s = 1011): every observed y
  satisfies y·s = 0 (blue, uniform at 1/8); the complementary half of the
  space (yellow positions) never appears. The answer hides in the geometry of
  the support.</figcaption>
</figure>

Note the escalation from BV: there, the Fourier transform put all mass **on**
the answer; here it puts mass on a random element of a subspace *determined
by* the answer, and classical post-processing finishes the job.

!!! tip "Remember this architecture"

    **Quantum samples + classical algebra.** Simon: Fourier samples + Gaussian
    elimination. Shor: Fourier samples + continued fractions. DQI: Fourier
    state + a classical *decoder*. The classical toolbox is a quantum
    resource — this hybrid shape is a generator of algorithms.

## 4. The hardness evidence

Unconditional in the query model: $\Omega(2^{n/2})$ vs $O(n)$ — exponential
AND robust. The catch, as always: it is an *oracle* separation. To make it
real you must instantiate a function that provably hides a coset structure
and is efficiently computable. Nobody has done that usefully over
$\mathbb{Z}_2^n$ — but doing it over $\mathbb{Z}_N$ is literally Shor's
algorithm: $f(j) = a^j \bmod N$ hides the subgroup $r\mathbb{Z}$. The oracle
result was the blueprint; the instantiation was the revolution.

## 5. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    What property of the PROBLEM made each query nearly worthless classically
    but a full subspace-sample quantumly? Why did hiding the structure in a
    promise about $f$ — rather than in $f$'s values — matter?

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/03-simon/simon.py
    .venv/bin/pytest predecessors/03-simon -q
    ```

- [ ] Read [`simon.py`](simon.py) — especially `rref_nullspace` — against §3
      until the coset-interference step is obvious.
- [ ] **Proof draft #1 (the real one):** prove the classical
      $\Omega(2^{n/2})$ lower bound. Draft completely BEFORE reading the
      sketch in `curriculum/solutions.md`, then grade yourself against its
      "common holes" list.
- [ ] One paragraph: the algorithm needs $n-1$ *independent* samples. Why does
      that cost only $O(n)$ expected runs, not more?
- [ ] Write §5.
