# Autopsy 03 — Simon (1994)

*The first big-and-robust separation — and the paper that triggered Shor.*

!!! tip "How to read this page"

    This is the biggest conceptual jump in the curriculum so far. Three new
    things arrive at once: a second register that **stays entangled**, an
    answer the machine **refuses to hand you directly**, and a classical
    algorithm doing half the work. Boxes marked **▸ deeper** hold the
    algebra and can be skipped on a first pass.

---

## 0. The stamping machine

A machine stamps documents. Feed it any 10-bit document number, it prints a
stamp. You are told two things about it:

- **Exactly two documents share each stamp.** Never one, never three.
- **The pairing is always the same hidden step.** If documents $x$ and $y$
  share a stamp, then $y = x \oplus s$ for one fixed secret mask $s$ — the
  same $s$ for every pair in the machine.

**Find $s$.**

Notice what you cannot do. Looking at a single stamp tells you nothing:
stamps are arbitrary labels, and knowing document `0110101101` prints stamp
`#41` says nothing about which *other* document also prints `#41`. The
secret is not in any value. It is in **which inputs are glued to which** —
and you only ever see one side of a glue joint at a time.

So the classical strategy is forced: **hunt for a collision**. Feed in
documents until two of them come back with the same stamp; the XOR of that
pair is $s$, immediately. With $2^{10}$ documents, how long does that take?

That question has a famous answer, and it is the reason this page exists.

---

## 1. The promise, made concrete

Formally: an oracle $f:\{0,1\}^n \to \{0,1\}^n$, promised **2-to-1** with a
hidden XOR mask,

$$
f(x) = f(y) \iff y = x \oplus s
$$

The inputs come glued into couples, every couple separated by the same step:

<div class="qq-anim" data-anim="coset"></div>

Those couples $\{x,\, x\oplus s\}$ have a name: they are the **cosets** of
the subgroup $\{0, s\}$. "Coset" sounds like a barrier and means something
simple — take a subgroup, shift the whole thing by some element, and you get
one of the parallel slices it cuts the space into. Here the subgroup has two
elements, so the slices are the 8 couples in the widget.

!!! info "Why the secret hides so well"

    Compare with [Bernstein–Vazirani](../02-bernstein-vazirani/notes.md).
    There, every query returned $s\cdot x$ — a real, if thin, fact about
    $s$. Here $f(x)$ is an **arbitrary label**. It carries no information
    about $s$ whatsoever until you happen to see the *same* label twice.

    That is the design upgrade: not "each query gives few bits" but
    **"each query gives no bits at all, until an exponentially rare
    coincidence"**.

---

## 2. The classical wall — the birthday bound

Any classical algorithm, randomized included, needs $\Omega(2^{n/2})$
queries.

Why $2^{n/2}$ and not $2^n$? Because collisions come from **pairs**, not
from draws. After $k$ queries you hold $k$ values, and any of the
$\binom{k}{2} \approx k^2/2$ pairs among them could collide. Each pair
collides with probability about $2^{-n}$, so you expect a hit once
$k^2/2 \approx 2^n$ — that is $k \approx 2^{n/2}$. Same arithmetic as the
birthday paradox: 23 people, not 183, for a shared birthday.

Until that collision lands, **every query is consistent with almost every
candidate secret**. You are not slowly narrowing the field, as in BV. You
are learning nothing at all, repeatedly, until you get lucky.

!!! tip "The design principle DJ lacked"

    Not *"each query gives few bits"* (BV's wall — capped at a factor $n$)
    but *"each query gives almost zero information about the answer until
    an exponentially rare event occurs."* **Every exponential separation
    we will meet has a version of this property**, and hunting for it is
    part of what this whole research program does.

Here is the ledger now:

| | separation | robust to randomness? |
|---|---|---|
| [Deutsch–Jozsa](../01-deutsch-jozsa/notes.md) | exponential | :material-close: dies at $O(1)$ |
| [Bernstein–Vazirani](../02-bernstein-vazirani/notes.md) | $n$ vs $1$ — polynomial | :material-check: information-theoretic |
| **Simon** | **exponential** | :material-check: **robust** |

Big *and* solid, for the first time.

---

## 3. Two registers — and the trick that makes it obvious

The circuit looks like the one you already know, with one addition: a second
register that holds $f$'s output.

```text
|0⟩|0⟩ ──H⊗ⁿ on reg 1──►  Σₓ|x⟩|0⟩  ──O_f──►  Σₓ|x⟩|f(x)⟩  ──H⊗ⁿ on reg 1──►  measure reg 1
```

**This is the first algorithm in the curriculum where the second register
does not politely disappear.** In DJ and BV we put the target in
$|-\rangle$, it handed back a phase, and it factored out of the problem
entirely ([phase kickback](../01-deutsch-jozsa/notes.md#3-phase-kickback-how-data-gets-into-signs)).
Here the second register holds $f(x)$ and stays **entangled** with the
first. That entanglement is doing the work.

The algebra is short but opaque. So use the standard trick: **pretend you
measure register 2 first.**

You are allowed to. Measurement on one register commutes with the gates
acting on the other, so doing it early changes nothing about the final
statistics — it just makes the picture obvious. Suppose you see some stamp
value $v$. Which inputs could have produced it? Exactly two: some $x_0$ and
$x_0 \oplus s$. So register 1 collapses to

$$
\frac{|x_0\rangle + |x_0 \oplus s\rangle}{\sqrt2}
$$

**a two-element coset — with $x_0$ random and unknown to you.** Now apply
$H^{\otimes n}$ to *that*, and watch:

<div class="qq-anim" data-anim="simoncomb"></div>

??? note "▸ deeper — the two-line cancellation"

    Applying $H^{\otimes n}$ to the collapsed state, the amplitude landing
    on $|y\rangle$ is

    $$
    \frac{1}{\sqrt{2^{n+1}}}\Big[(-1)^{x_0\cdot y}
      + (-1)^{(x_0\oplus s)\cdot y}\Big]
    = \frac{(-1)^{x_0\cdot y}}{\sqrt{2^{n+1}}}\Big[1 + (-1)^{s\cdot y}\Big]
    $$

    The bracket is $2$ when $s\cdot y = 0$ and **exactly $0$** when
    $s\cdot y = 1$. Half of all outcomes are annihilated, and the unknown
    $x_0$ survives only as an overall sign you never observe — which is
    precisely why it does not matter that you did not know it.

So each run returns a **uniformly random $y$ from the subspace orthogonal to
$s$** — one free linear equation, $y\cdot s = 0$.

Notice the escalation from BV. There, the Fourier transform put all the mass
**on** the answer and you read it off. Here it puts mass on a random element
of a subspace *determined by* the answer. **The machine will not tell you
$s$. It will only ever tell you things that are true about $s$.**

---

## 4. Quantum samples plus classical algebra

One equation is nearly worthless: $y\cdot s = 0$ still leaves half the
candidates standing. But equations accumulate, and each independent one
halves the field:

<div class="qq-anim" data-anim="constraints"></div>

After $n-1$ independent equations exactly two vectors satisfy all of them —
$0$ and $s$ — and since $s \ne 0$ you are done. Recovering $s$ from the
equations is **Gaussian elimination over $\mathbb{F}_2$**: ordinary
row-reduction where "add" means XOR, computing the nullspace of the matrix
whose rows are your samples. That is `rref_nullspace` in
[`simon.py`](simon.py), and it is fast, classical, and boring — which is the
point.

!!! tip "Remember this architecture"

    **Quantum samples + classical algebra.** Simon: Fourier samples +
    Gaussian elimination. [Shor](../04-shor/notes.md): Fourier samples +
    continued fractions. [DQI](../11-dqi/notes.md): Fourier state + a
    classical *decoder*. The classical toolbox is a quantum resource — this
    hybrid shape is a **generator of algorithms**, and it is exactly the
    shape the [hunt](../../hunt/README.md) looks for.

??? note "▸ deeper — why $n-1$ *independent* samples cost only $O(n)$ runs"

    *(This is the tool for the third exercise, not the answer.)*

    Each run gives a uniformly random $y$ from the $(n-1)$-dimensional
    space $s^\perp$, which has $2^{n-1}$ elements. Suppose you already hold
    $k$ independent samples. Their span contains $2^k$ vectors. A fresh
    sample is *useless* only if it lands inside that span, which happens
    with probability $2^k / 2^{n-1}$.

    While $k \le n-2$, that probability is at most $1/2$ — so **each run
    has at least even odds of being useful**, no matter how far along you
    are. The rest is a short expectation argument, and it is yours to
    write.

<figure markdown="span">
  ![Samples land only in the orthogonal subspace](fig-subspace.svg#only-light)
  ![Samples land only in the orthogonal subspace](fig-subspace-dark.svg#only-dark)
  <figcaption>4000 runs on our simulator (n = 4, s = 1011): every observed y
  satisfies y·s = 0 (blue, uniform at 1/8); the complementary half of the
  space (yellow positions) never appears. The answer hides in the geometry
  of the support.</figcaption>
</figure>

---

## 5. On real hardware — the fragility ladder

Simon breaks in a way the first two algorithms do not, and the reason is
worth stating precisely.

Count what each algorithm demands of its output:

| | output demanded | what one error does |
|---|---|---|
| Deutsch–Jozsa | **1 bit**, read as a statistic over shots | washes out |
| Bernstein–Vazirani | **$n$ bits**, independent | majority-vote each bit ([02 §6](../02-bernstein-vazirani/notes.md#6-on-real-hardware-n-bits-out-is-a-different-demand)) |
| **Simon** | **$n-1$ equations of $n$ bits — all correct *and* independent** | **one bad equation ⇒ wrong nullspace ⇒ wrong secret** |

Simon needs roughly $n^2$ bits of *structured* output, and — this is the
sharp part — **Gaussian elimination has no notion of "mostly right"**. Feed
it one corrupted equation and it returns a confidently wrong $s$. There is
no averaging to hide behind.

Measured on published error rates
([`simon_on_hardware.py`](simon_on_hardware.py), $n=5$, one fresh noise
trajectory per shot):

| machine | fraction of clean equations | all $n{-}1$ clean | textbook solve | majority repair |
|---|---:|---:|---:|---|
| ideal | 1.000 | 1.000 | 1.00 | ✓ |
| Quantinuum Helios | 1.000 | 1.000 | 1.00 | ✓ |
| IBM Heron r2 | 0.963 | 0.858 | 0.92 | ✓ |
| Rigetti Ankaa-3 | 0.942 | 0.786 | 0.92 | ✓ |

96% of individual equations are fine — and yet the probability that *all
four* are fine has already fallen to 86%. Push $n$ up and that compounds
quadratically:

<figure markdown="span">
  ![Simon's fragility under real noise](fig-fragility.svg#only-light)
  ![Simon's fragility under real noise](fig-fragility-dark.svg#only-dark)
  <figcaption>Left: measured on our simulator at real error rates — single
  equations stay clean while the conjunction of all of them decays, and the
  textbook solve follows it down. Right: the ladder extrapolated on Heron
  error rates. DJ is flat, BV decays with n, Simon decays with n² and
  crosses the coin-flip line before n = 20. Generated by
  <code>scripts/make_simon_figures.py</code>.</figcaption>
</figure>

!!! info "The repair — and why it is not free"

    You cannot majority-vote an *equation* the way BV majority-votes a bit.
    What you do instead: **oversample**, then keep the candidate $s$ that
    the largest number of samples agree with, and **verify it against the
    oracle** ($f(x) \stackrel{?}{=} f(x\oplus s)$ for a few random $x$ —
    two extra queries, and the promise makes the check exact).

    That works — the last column above is unbroken — but note what it cost:
    the algorithm stopped being "run it $n$ times and solve" and became a
    statistical procedure with a verification step. **Structured output is
    a liability on noisy hardware**, and every algorithm downstream of
    Simon inherits it. Shor's continued-fraction step has exactly the same
    character.

---

## 6. The attack on the oracle everyone actually builds

Now the part that should make you suspicious of every "Simon's algorithm
demonstrated on N qubits" headline.

To run this on hardware you must build $f$ out of gates. The construction
everyone reaches for is a **linear** function

$$
f(x) = Ax \quad\text{over } \mathbb{F}_2, \qquad \ker A = \{0, s\}
$$

because a linear map over $\mathbb{F}_2$ is nothing but a **network of
CNOTs** — cheap, shallow, and exactly what a device can execute. Our own
[`simon_on_hardware.py`](simon_on_hardware.py) uses one, because anything
else is unrunnable.

But a linear $f$ is **classically trivial**. Query the $n$ unit vectors
$e_1,\dots,e_n$; each answer is a column of $A$; now compute $\ker A$ by
Gaussian elimination. That is $n$ queries, deterministic, no collisions, no
birthday bound. We wrote that attack —
[`simon_classical_attack.py`](simon_classical_attack.py) — and ran it:

| $n$ | 4 | 8 | 12 | 16 | 20 |
|---|---:|---:|---:|---:|---:|
| classical queries against the linear oracle | 4 | 8 | 12 | 16 | 20 |

Against a genuinely random 2-to-1 table, the same attacker is thrown back on
collision-hunting and the cost explodes as the birthday bound predicts —
median 155 queries at $n=14$ against $2^7 = 128$.

<figure markdown="span">
  ![The separation lives in the oracle](fig-attack.svg#only-light)
  ![The separation lives in the oracle](fig-attack-dark.svg#only-dark)
  <figcaption>Measured, both oracles. Against the linear oracle a classical
  attacker needs n queries — it is <em>below</em> the quantum cost, not
  above it. Against a random 2-to-1 table it needs 2^(n/2) and Simon's
  exponential separation is real. Same quantum circuit either way.</figcaption>
</figure>

!!! danger "What this means for hardware demonstrations"

    Look at where the blue points sit relative to the green line: against
    the oracle a real device can actually run, **the classical attacker is
    faster than the quantum algorithm.**

    A hardware "Simon demonstration" on a linear oracle proves that the
    circuit works. It demonstrates **no separation whatsoever** — the
    separation was in the promise, and building a runnable oracle threw the
    promise away. A genuinely hard Simon oracle needs a function that
    provably hides a coset structure and is *not* linear, which means an
    exponentially large lookup table or a cryptographic construction. On
    hardware, nobody has one.

    This is the [query-model fine print](../01-deutsch-jozsa/notes.md#1-what-an-oracle-actually-is)
    at its sharpest, and it is the reason the
    [claim ledger](../../machines/gap.md) exists.

---

## 7. The hardness evidence, and what survived

**Unconditional in the query model**: $\Omega(2^{n/2})$ classical versus
$O(n)$ quantum — exponential *and* robust to randomness. That lower bound is
real mathematics and still stands, untouched, thirty years on. It was the
first evidence of its kind, and §6 does not dent it: §6 is about
*instantiation*, which is a different claim.

The catch is the one every oracle result carries. To make the separation
real you must exhibit a function that provably hides a coset structure and
is efficiently computable. Nobody has done that usefully over
$\mathbb{Z}_2^n$.

**But do it over $\mathbb{Z}_N$ and you get Shor.**

!!! success "The most consequential useless problem in computing"

    Simon's paper was **initially rejected**. One of its referees was Peter
    Shor, who read it and saw what it implied. Within months Shor had
    replaced the group $\mathbb{Z}_2^n$ with $\mathbb{Z}_N$, replaced the
    hidden XOR mask with a hidden *period*, and found the instantiation
    Simon lacked: $f(j) = a^j \bmod N$ is efficiently computable, and it
    hides the subgroup $r\mathbb{Z}$ where $r$ is the order of $a$.
    Recovering $r$ factors $N$.

    Both papers appeared at FOCS 1994. **The oracle result was the
    blueprint; the instantiation was the revolution** — and the difference
    between them is the entire subject of this curriculum.

---

## 8. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    What property of the PROBLEM made each query nearly worthless
    classically but a full subspace-sample quantumly? Why did hiding the
    structure in a promise about $f$ — rather than in $f$'s values —
    matter?

---

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/03-simon/simon.py
    .venv/bin/python predecessors/03-simon/simon_classical_attack.py
    .venv/bin/python predecessors/03-simon/simon_on_hardware.py
    .venv/bin/pytest predecessors/03-simon -q
    ```

- [ ] Read [`simon.py`](simon.py) — especially `rref_nullspace` — against §3
      and §4 until the coset-interference step is obvious.
- [ ] **Proof draft #1 (the real one):** prove the classical
      $\Omega(2^{n/2})$ lower bound. Draft completely BEFORE reading the
      sketch in `curriculum/solutions.md`, then grade yourself against its
      "common holes" list.
- [ ] One paragraph: the algorithm needs $n-1$ *independent* samples. Why
      does that cost only $O(n)$ expected runs, not more? (The tool is in
      the ▸ deeper box in §4; the argument is yours.)
- [ ] Write §8.

??? note "▸ deeper — the shape of the $\Omega(2^{n/2})$ argument"

    *This is the scaffolding, not the proof — draft #1 is graded.*

    The statement to beat: no randomized algorithm making $k$ queries can
    find $s$ with probability $\ge 2/3$ unless $k = \Omega(2^{n/2})$.

    The standard route is an **adversary argument**. Do not fix $f$ in
    advance; let an adversary answer queries on the fly, always giving
    fresh random values, and keep track of which secrets remain consistent
    with the transcript so far.

    The key observation: as long as the algorithm has seen no collision,
    the transcript is consistent with a huge set of candidate secrets — and
    the adversary can keep it that way. So the algorithm can only win by
    *forcing* a collision, and the question becomes how many queries that
    takes.

    That reduces to counting: after $k$ queries there are $\binom{k}{2}$
    pairs, each of which "reveals" the secret only if it happens to be a
    colliding pair. Bound the probability that any pair collides, and you
    have the theorem. (Two standard holes to avoid: forgetting that the
    algorithm may choose queries *adaptively*, and forgetting to handle the
    algorithm that simply guesses $s$ without querying.)

### Proof draft (yours)

*(write here)*
