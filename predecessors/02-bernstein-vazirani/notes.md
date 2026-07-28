# Autopsy 02 — Bernstein–Vazirani (1993)

*Same circuit, different problem — the lesson of the whole course in one page.*

!!! tip "How to read this page"

    The main line assumes only [autopsy 01](../01-deutsch-jozsa/notes.md).
    Boxes marked **▸ deeper** hold algebra and complexity theory you can
    skip on a first pass. The implementation in the exercises is *your*
    homework — nothing on this page does it for you.

---

## 0. Twenty questions, but every answer is one bit

I am thinking of a secret ten-bit string — say `1011010010`. You may ask me
questions, but only questions of one very restricted kind:

> Name any subset of the ten positions. I will tell you whether the number
> of **1s** among those positions is **even or odd**.

That is all. Not "what is bit 4" — you get a parity, a single bit, every
time.

How many questions do you need to pin down all ten bits?

You can get it in ten: ask about position 1 alone (the parity of a single
bit *is* that bit), then position 2 alone, and so on. Ten questions, ten
bits, done.

Can you do better? Each answer is one bit; the secret contains ten bits.
Ten answers carry ten bits. **You cannot beat ten, and no amount of
cleverness or luck changes that** — a claim we will make precise in §2, and
which you will prove yourself in the exercises.

A quantum computer needs **one** question.

Here is what makes this page different from the last one. In
Deutsch–Jozsa, the classical wall turned out to be soft: allow a little
randomness and it collapsed from exponential to $O(1)$. **This wall does
not collapse.** One query versus $n$ is a smaller claim than DJ's, and
unlike DJ's, it is *true against every classical strategy*.

And the circuit that does it is the one you already built.

---

## 1. What the box actually computes

The oracle here computes

$$
f(x) \;=\; s \cdot x \bmod 2
$$

which reads: **AND the two strings bit by bit, then take the parity of what
survives.** The secret $s$ acts as a mask deciding which of *your* bits get
looked at; everything else you set is thrown away. Then the surviving 1s
are counted, and you are told only *even* or *odd*.

<div class="qq-anim" data-anim="bvmask"></div>

Two things worth noticing while you play with it:

- Flip a bit of $x$ where $s$ has a **0** and the answer never changes. That
  position of the secret is invisible to that question.
- Flip a bit of $x$ where $s$ has a **1** and the answer *always* flips.
  That is the only handle you have.

So the box does hold all $n$ bits of $s$ — but every question you ask
squeezes them through a one-bit funnel.

??? note "▸ deeper — this is a linear function, and that will matter"

    Parity is addition mod 2, so $f$ is **linear**:
    $f(x \oplus y) = f(x) \oplus f(y)$ for all $x, y$. Every linear
    Boolean function is $s\cdot x$ for exactly one $s$ — so "find $s$" and
    "identify which linear function this is" are the same task. §4 shows
    that linearity is precisely what makes the quantum spectrum a single
    spike.

---

## 2. The $n$-question grind, and why luck does not help

The classical algorithm is the obvious one. Ask about position $i$ alone —
in vector terms, query $x = e_i$, the string with a single 1 in position
$i$. Since only bit $i$ survives the mask,

$$
f(e_i) \;=\; s_i
$$

Do that for $i = 1 \dots n$ and you have read the secret. **$n$ queries,
always, guaranteed.**

Now the lower bound, in words (you will make it rigorous in the exercises).
Before you ask anything, the secret could be any of $2^n$ strings. Each
answer is a single bit, so it can at best split the surviving candidates
into two groups. After $k$ answers, at least $2^n / 2^k$ candidates remain
consistent with everything you have heard. To be left with exactly one, you
need $k \ge n$.

!!! success "Why this wall does not crumble the way DJ's did"

    In [Deutsch–Jozsa](../01-deutsch-jozsa/notes.md#8-the-classical-wall-and-the-crack-in-it),
    the answer was **one bit** ("constant or balanced?") hiding in a
    statistical property — the mean. Random sampling estimates a mean
    cheaply, so a randomized classical algorithm got there in $O(1)$
    queries and the exponential separation evaporated.

    Here the answer is **$n$ bits**, and information does not care how
    lucky you are: $n$ bits cannot arrive through fewer than $n$ one-bit
    answers. The bound is **information-theoretic**, so it holds for
    deterministic algorithms, randomized ones, and any strategy anyone
    will ever invent.

    That upgrade — from "beats a baseline nobody would use" to "beats every
    possible classical algorithm" — is the real content of this autopsy.

The honest ledger for the course so far:

| | separation | robust to randomness? |
|---|---|---|
| Deutsch–Jozsa | exponential | :material-close: dies at $O(1)$ |
| Bernstein–Vazirani | $n$ vs $1$ — polynomial | :material-check: information-theoretic |
| Simon (next) | **exponential** | :material-check: **robust** |

Notice the trade. DJ's claim was **big but fragile**; BV's is **small but
solid**. Getting big *and* solid at the same time is
[Simon's problem](../03-simon/notes.md), and that combination is what
provoked Shor.

---

## 3. The reveal: it is the same circuit

Here is the punchline of the entire autopsy, and it is worth pausing on.

**The Bernstein–Vazirani circuit is gate-for-gate identical to
Deutsch–Jozsa's.** Hadamards on every wire, one phase-oracle call,
Hadamards on every wire, measure. Not "similar to". Identical. If you built
DJ in autopsy 01, you have already built BV and did not know it.

Nothing about the machine changed. **Only the promise on $f$ changed** —
and the algorithm went from answering one yes/no question to handing you
$n$ bits.

So where did the power come from? Watch. The circuit below is frozen; you
change only the problem:

<div class="qq-anim" data-anim="spectrum"></div>

What you are looking at is the **Fourier spectrum** of the sign function
$(-1)^{f(x)}$ — the thing the final Hadamard layer computes
([autopsy 01 §5](../01-deutsch-jozsa/notes.md#5-why-the-hadamard-layer-is-really-a-fourier-transform)).
Each promise writes its answer somewhere different in that picture:

- **Constant $f$** — all the mass piles onto frequency $0$. DJ's question
  ("did we come home?") is answered yes.
- **Linear $f = s\cdot x$** — all the mass moves to a **single spike
  standing on $s$**. Read the label off the bar and you have the secret,
  every bit of it, from one measurement.
- **Balanced but not linear** — frequency 0 is empty (so DJ still correctly
  says "balanced"), but the mass is *spread* across many frequencies.
  There is no single answer to read.
- **No promise at all** — the spectrum is a mess and both questions become
  meaningless.

!!! question "Stop and think"

    If the gates are identical to DJ's, where exactly does the extra power
    come from?

    ??? success "The point of this entire autopsy"

        From the **problem structure**. The promise "$f$ is a character"
        makes the Fourier spectrum a delta; the promise "$f$ is
        constant-or-balanced" only makes the zero-frequency coefficient
        informative. Same transform, different spectra.

        **The algorithm content lives in the problem, not in the circuit.**
        Which is why this whole research program is problem-first: hunting
        for new *circuits* is hunting in the wrong place.

---

## 4. Characters, demystified — and why the spike is exact

The word in the literature is that $(-1)^{s\cdot x}$ is a **character** of
the group $\mathbb{Z}_2^n$. That sounds like a barrier; it is a one-line
idea.

A character is simply a function that **turns the group's operation into
multiplication**. Our group operation is XOR, so a character satisfies

$$
\chi(x \oplus y) \;=\; \chi(x)\,\chi(y)
$$

Check that $\chi_s(x) = (-1)^{s\cdot x}$ does exactly this:
$s\cdot(x\oplus y) = (s\cdot x) \oplus (s\cdot y)$, and $(-1)$ raised to a
sum is the product of the powers. That is the whole definition. Characters
are the functions that "respect" XOR — the $\mathbb{Z}_2^n$ version of
$e^{2\pi i k x/N}$, which respects addition the same way.

Now, why does the transform of a character land *entirely* on one spike,
with nothing left over anywhere else? Because of **orthogonality**, and you
can watch it happen term by term:

<div class="qq-anim" data-anim="orthogonality"></div>

Set the test frequency $y$ equal to the secret $s$: every term is $+1$ and
they pile up to $2^n$. Now flip a single bit of $y$ so it misses: the terms
split into **exactly** half $+1$ and half $-1$, and the total is **exactly
zero**. Not small — zero.

That exactness is why Bernstein–Vazirani never fails, never needs
repeating, and has no error term. Every wrong answer is annihilated by
perfect cancellation, and all the amplitude has nowhere to go but the right
one.

<figure markdown="span">
  ![All amplitude on the secret](fig-delta.svg#only-light)
  ![All amplitude on the secret](fig-delta-dark.svg#only-dark)
  <figcaption>Our simulator, n = 4, s = 1011: the post-circuit distribution
  is a perfect delta on the secret. Not approximately — exactly.</figcaption>
</figure>

??? note "▸ deeper — the two lines"

    After the oracle the state is
    $2^{-n/2}\sum_x (-1)^{s\cdot x}|x\rangle$. Apply $H^{\otimes n}$ using
    $H^{\otimes n}|x\rangle = 2^{-n/2}\sum_y (-1)^{x\cdot y}|y\rangle$ and
    collect the coefficient of $|y\rangle$:

    $$
    \frac{1}{2^n}\sum_x (-1)^{s\cdot x}(-1)^{x\cdot y}
    = \frac{1}{2^n}\sum_x (-1)^{(s\oplus y)\cdot x}
    = \begin{cases} 1 & y = s \\ 0 & y \ne s\end{cases}
    $$

    The last step is the widget above: summing $(-1)^{d\cdot x}$ over all
    $x$ gives $2^n$ when $d = 0$ and $0$ otherwise, because a non-zero $d$
    makes $d\cdot x$ even for exactly half the inputs. Hence
    $H^{\otimes n}$ maps the state to $|s\rangle$ exactly.

---

## 5. Fourier sampling — the primitive being born

Step back and name what the machine actually does, because this is the
piece that outlives the problem.

!!! abstract "Fourier sampling"

    Prepare a uniform superposition, call the oracle once to write $f$ into
    the phases, apply $H^{\otimes n}$, and measure. The outcome $y$ arrives
    with probability $|\hat g(y)|^2$, where $g(x) = (-1)^{f(x)}$.

    **One query buys one sample from the Fourier spectrum of $f$** — a
    spectrum that classically can cost exponentially many evaluations to
    probe.

Every algorithm in this curriculum's first half is this primitive pointed
at a different structure:

| algorithm | what the spectrum looks like | what you read |
|---|---|---|
| Deutsch–Jozsa | mass at frequency 0, or not | one bit: is it there? |
| Bernstein–Vazirani | a single delta at $s$ | the whole location |
| [Simon](../03-simon/notes.md) | mass only on frequencies ⟂ the hidden period | a random constraint; repeat, solve a linear system |
| [Shor](../04-shor/notes.md) | mass on multiples of $N/r$ over $\mathbb{Z}_N$ | a period, via continued fractions |

So the design question for a quantum algorithm becomes concrete:
**is my problem's answer written in the location of Fourier mass?** If yes,
this machinery applies. If no, this machinery has nothing to offer, no
matter how many qubits you have. That question is the seed of the
[Problem-Shape Catalog](../../frontier/problem-shapes.md).

---

## 6. On real hardware — n bits out is a different demand

The circuit is the same as DJ's, so the *hardware* story ought to be the
same. It is not, and the reason is instructive.

In [autopsy 01 §7](../01-deutsch-jozsa/notes.md#7-what-a-real-machine-gives-you)
we compiled this circuit honestly: the oracle for $s\cdot x$ is literally
**one CNOT per set bit of $s$**, firing into an ancilla held in
$|-\rangle$. That is phase kickback made of hardware, and it is exactly
what BV needs. Same gates, same qubits, same noise.

What differs is **how much you demand of the output**:

- Deutsch–Jozsa asks a **yes/no question** and decides from a *statistic*
  over many shots. Individual bad shots wash out.
- Bernstein–Vazirani wants the **whole $n$-bit string**, and a single
  misread bit gives you the wrong secret.

Run it ([`bv_on_hardware.py`](bv_on_hardware.py), $n=8$, secret
`10101101`, one fresh noise trajectory per shot):

| machine | exact string, one shot | per-bit correct | majority vote (400 shots) |
|---|---:|---:|---|
| ideal | 1.000 | 1.000 | ✓ `10101101` |
| Quantinuum Helios | 0.998 | 1.000 | ✓ `10101101` |
| IBM Heron r2 | 0.920 | 0.987 | ✓ `10101101` |
| Rigetti Ankaa-3 | 0.912 | 0.988 | ✓ `10101101` |

Look at the middle column against the first. Each *bit* is read correctly
about 98.7% of the time — but demanding all eight at once costs
$0.987^8 \approx 0.90$, and at $n = 60$ it would cost
$0.987^{60} \approx 0.45$: worse than a coin flip.

!!! info "The repair, and why it is cheap"

    Readout errors hit each qubit **independently**. So you do not need any
    single shot to be perfect — you run the circuit a few dozen times and
    take a **majority vote on each bit separately**. Each bit is repaired
    on its own, and the probability that a majority of shots misreads the
    same bit is astronomically small.

    **$n$ bits of output cost you *shots*, not *fidelity*.** That is real
    experimental practice, not a trick, and it is part of why BV is a
    standard hardware smoke-test today.

<figure markdown="span">
  ![BV under real machine noise](fig-readout.svg#only-light)
  ![BV under real machine noise](fig-readout-dark.svg#only-dark)
  <figcaption>Left: single-shot success (whole string at once) falls away
  while the per-bit read rate barely moves. Right: extrapolated — one-shot
  BV drops through the coin-flip line, while a 25-shot majority vote holds
  the secret essentially forever. Generated by
  <code>scripts/make_bv_figures.py</code> from the error rates in
  <code>machines/data.yml</code>.</figcaption>
</figure>

---

## 7. The honest accounting

Three deductions, in increasing order of severity.

**One: the separation is polynomial, and that is a ceiling, not an
accident.** $n$ queries versus 1. Counting bits can never do better than a
factor of $n$ — if the answer is $n$ bits and each classical query returns
one bit, the very best story you can tell is "$n$ versus 1". To get an
*exponential* separation, the answer must hide so that each classical query
reveals **almost nothing**, rather than merely little. That is precisely
Simon's move, and it is why autopsy 03 is the escalation.

**Two: the win is in queries only — not in gates.** The quantum circuit
uses $2n$ Hadamards and $|s|$ CNOTs. It is not doing less *work* than the
classical algorithm; it is asking fewer *questions*. Those are different
metrics, and only the second one is being compared.

**Three — the sharpest: instantiate the oracle and the advantage
disappears entirely.** This is the same fine print as
[DJ's](../01-deutsch-jozsa/notes.md#1-what-an-oracle-actually-is), but it
bites harder here. Suppose the oracle is not a magic box but an actual
circuit someone hands you, as it must be in any real application. Then it
is a circuit computing $s\cdot x$ — and you can recover $s$ by **looking at
which input wires are connected to the output**. No queries at all. The
$n$-versus-1 separation exists only while the box stays sealed, and BV's
box is the easiest possible box to read once opened.

!!! danger "What this means, and does not mean"

    BV is not a useful algorithm and never was. Nobody has a
    hidden-linear-function problem where the function is genuinely opaque.

    What it *is*: a proof of principle with a clean, unconditional lower
    bound, built to serve complexity theory rather than applications. Its
    descendants matter enormously; it does not. Judge it as evidence, not
    as software — the same standard the
    [claim ledger](../../machines/gap.md) applies to modern results.

### What genuinely survived

- **BQP itself.** This is the paper (Bernstein & Vazirani, STOC 1993;
  SIAM J. Comput. 1997) that defined the class of problems a quantum
  computer can solve efficiently, and built the universal quantum Turing
  machine that makes the definition meaningful. Every "is X in BQP?"
  question descends from here.
- **Recursive Fourier Sampling.** Nesting this problem inside itself gave
  the **first superpolynomial separation** between quantum and classical
  computation relative to an oracle — the strongest evidence available in
  1993 that BQP might exceed BPP, and the direct provocation for Simon and
  then Shor.
- **Fourier sampling as a reusable primitive** (§5), which is the actual
  inheritance.

??? note "▸ deeper — what BQP, BPP and P actually mean"

    Complexity classes are just buckets of problems sorted by what
    resources solve them.

    - **P** — solvable by an ordinary computer in polynomial time. The
      informal meaning of "efficient".
    - **BPP** — *Bounded-error Probabilistic Polynomial time*: solvable in
      polynomial time by a computer allowed to flip coins, getting the
      right answer at least 2/3 of the time. (Repeat and take a majority to
      push the error as low as you like.) This is the honest definition of
      "efficiently solvable in practice" — and note it is the baseline that
      demolished Deutsch–Jozsa.
    - **BQP** — the same, with a quantum computer: polynomial time,
      bounded error. Defined in this paper.

    We know $\text{P} \subseteq \text{BPP} \subseteq \text{BQP}$: a quantum
    computer can do anything the others can. The billion-dollar question is
    whether any of those containments is **strict** — in particular whether
    BQP is genuinely bigger than BPP. **Nobody has proved it**, and a proof
    would separate P from PSPACE, which is far beyond current mathematics.

    This is why oracle results exist. Relative to a black box, we *can*
    prove separations (BV does; Simon does more dramatically). Whether such
    separations survive when the box becomes a real circuit is exactly the
    open question — and exactly the fine print in deduction three above.

---

## 8. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    One paragraph, own words. React to: where exactly did the power come
    from, given identical gates? What problem-shape wants "answer =
    location of Fourier mass"? $\mathbb{Z}_2^n$ is the baby group — what
    changes when the group becomes $\mathbb{Z}_N$? (That question is
    Week 2.)

---

## Exercises

### Code (make the tests green)

!!! warning "Spoiler note"

    [`bv_on_hardware.py`](bv_on_hardware.py) (used in §6) builds this
    circuit explicitly from H and CNOT gates. If you want to derive the
    implementation unaided, write your version **before** reading that
    file. The circuit is already shown in
    [autopsy 01 §7](../01-deutsch-jozsa/notes.md#7-what-a-real-machine-gives-you),
    so nothing is truly hidden — but the derivation is worth doing
    yourself.

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

??? note "▸ deeper — what Yao's principle is, and why you would reach for it"

    *This explains the tool, not the answer — the proof above is yours.*

    Proving a lower bound against a **randomized** algorithm is awkward:
    the algorithm gets to flip coins, so it has infinitely many possible
    behaviours and you cannot argue against them one at a time.

    **Yao's principle** converts that problem into an easier one. It says:
    to show every randomized algorithm needs many queries in the worst
    case, it is enough to

    1. **pick a probability distribution over inputs** yourself (you choose
       the hard distribution — this is where the creativity lives), and
    2. show that every **deterministic** algorithm makes many queries *on
       average* against that distribution.

    Since a randomized algorithm is just a probability distribution over
    deterministic ones, it cannot do better on average than the best
    deterministic algorithm does. Worst case over randomness $\ge$ average
    case over inputs.

    So the shape of your proof for (b) is: choose a distribution on
    secrets $s$ (the uniform one is the natural first guess here), then
    bound how much a deterministic questioner can learn per query against
    it. An information-theoretic accounting — how many bits about $s$ can
    $k$ answers carry? — is the standard way to finish.

### Proof draft (yours)

*(write here)*
