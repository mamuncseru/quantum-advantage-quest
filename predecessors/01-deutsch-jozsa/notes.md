# Autopsy 01 — Deutsch–Jozsa (1992)

*Interference works — and the field's first weak-baseline incident.*

!!! tip "How to read this page"

    The main line is written for someone who has never seen a quantum
    algorithm. Every symbol is built before it is used. Boxes marked
    **▸ deeper** hold the algebra and can be skipped entirely on a first
    pass without losing the thread — come back to them when you want the
    proof rather than the picture.

---

## 0. The locked box

Here is a sealed box. On its front are ten switches; on its top, one lamp.
Setting the switches to some pattern makes the lamp show black or white.
Ten switches means **1024** different patterns.

Someone you trust hands you the box and swears it is one of two kinds:

- **constant** — the lamp shows the same colour for all 1024 patterns; or
- **balanced** — the lamp shows white for exactly 512 patterns and black
  for the other 512.

You may set switches and look at the lamp as often as you like. **How many
looks do you need to say which kind of box you hold?**

Think it through before reading on. If you check 100 patterns and every one
is white, you still cannot be sure: a balanced box has 512 white patterns,
and you may have hit 100 of them. You cannot be *certain* until you have
seen **513** patterns — one more than half — because only then is "all the
same so far" impossible for a balanced box.

Deutsch and Jozsa's claim, in 1992, was that a quantum machine settles this
with **one** look.

Not 513. Not ten. One.

That claim sounds like cheating, and the interesting thing is *exactly
where* it is honest and *exactly where* it is thin. Both halves of that
answer are in this page. Let us build the machine that does it, one piece
at a time, and then take it apart.

---

## 1. What an "oracle" actually is

The box is what the field calls an **oracle**. The word makes it sound
mystical; it is not. Three things to understand about it, in order.

### It is a thing you may use, not a thing you may read

An oracle is a device that computes some function $f$ for you. You are
allowed to *ask* it — put in $x$, get out $f(x)$ — but you are not allowed
to open it up and study how it decides. In the model, we count **only** how
many times you ask. That counting is the entire currency of this subject:
"one query" versus "513 queries" is the claim.

### It cannot overwrite — physics forbids it

Here is the part that always gets skipped, and it is the reason the
notation looks strange. Quantum evolution is **reversible**: every
operation a quantum computer performs can be run backwards. A box that
took $|x\rangle$ and simply *replaced* it with $|f(x)\rangle$ would destroy
information — if $f$ maps many inputs to the same output, you could never
run it backwards, because you would not know which input you came from.
Such a box cannot exist as a quantum operation.

So the box is built to *add* its answer to a spare register instead of
overwriting anything:

$$
|x\rangle\,|y\rangle \;\longmapsto\; |x\rangle\,|y \oplus f(x)\rangle
$$

where $\oplus$ is XOR (addition mod 2: $0\oplus0=0$, $1\oplus0=1$,
$0\oplus1=1$, $1\oplus1=0$). The input $x$ survives untouched. The answer
lands on the spare bit $y$. Nothing is erased, so the whole thing can be
undone — and indeed applying it **twice** returns you exactly to where you
started, since $y \oplus f(x) \oplus f(x) = y$.

Play with it:

<div class="qq-anim" data-anim="oracle"></div>

That is the whole content of the notation $U_f$. It is a box that XORs its
answer onto a register you supply, because reversibility leaves it no other
choice.

### The fine print that the field routinely forgets

!!! warning "The query model charges for asking, not for building"

    The model charges one unit per call and **nothing at all** for the
    box's existence. That is a modelling choice, and it is load-bearing in
    a way that has embarrassed this field repeatedly.

    A query separation becomes a real-world separation only when the
    oracle can be **instantiated** — built as an efficient circuit — for a
    problem someone actually has. Shor's algorithm instantiates (its
    "oracle" is modular exponentiation, real arithmetic on real numbers).
    Most oracle results never do.

    Look at our own code: [`qsim/__init__.py`](../../qsim/__init__.py)
    builds `phase_oracle` as a dense $2^n \times 2^n$ matrix. Constructing
    it costs exponential classical work — and the model counts that as
    **free**. Feel that, because it is the crack through which a great
    deal of over-claiming has entered.

---

## 2. The lie you have already been told

Almost everyone arrives with this sentence in their head:

> *"A quantum computer tries all the inputs at once."*

The first half is nearly true and the second half ruins it. Yes — you can
put a register into a **superposition** of all 1024 patterns, and yes, one
call to the box then involves all of them. Here is what you get for it:

$$
\frac{1}{\sqrt{1024}}\sum_{x} |x\rangle\,|f(x)\rangle
$$

Every input, paired with its answer, all present. It looks like you have
computed 1024 things.

Now you have to **measure**, because measurement is the only way to get a
number out of a quantum machine. And measurement hands you back
**one** pair $(x, f(x))$, chosen at random, and destroys the rest.

<div class="qq-anim" data-anim="collapse"></div>

Read that widget until it stings. You did an elaborate thing involving all
1024 inputs and you learned the value of $f$ at *one input you did not even
get to choose*. That is strictly worse than just checking a pattern
yourself.

!!! danger "The correct sentence"

    **Superposition alone computes nothing.** A quantum computer is not a
    parallel classical computer with 2ⁿ processors and an unlucky output
    port. Everything real comes from what happens *between* the
    superposition and the measurement — from **interference**, which is
    the subject of the rest of this page.

### So what is a "global property"?

That widget also gives us the definition we need, by contrast.

- A **local** question is: *what is $f(0110101101)$?* One input, one
  answer. Measurement is happy to answer local questions — one at a time,
  at random, which is why it is useless here.
- A **global** question is: *is the lamp always the same colour?* This is
  a property of **all 1024 values at once**. No single value of $f$
  contains any part of the answer.

Constant-versus-balanced is exactly a global question. And it has a
particularly clean numerical form. Write the lamp's colour as $\pm 1$
instead of $0/1$ — define $s(x) = (-1)^{f(x)}$, so white is $+1$ and black
is $-1$. Then:

- $f$ constant $\Rightarrow$ every $s(x)$ is the same $\Rightarrow$ their
  **average** is $+1$ or $-1$.
- $f$ balanced $\Rightarrow$ half are $+1$, half are $-1$
  $\Rightarrow$ their average is **exactly 0**.

So the question "constant or balanced?" is the question **"is the average
of $s$ zero, or not?"** Hold onto that: our machine is going to compute an
average of 1024 numbers using one query, and the reason it can is that
averaging is exactly what interference does.

---

## 3. Phase kickback: how data gets into signs

We have a box that XORs onto a spare register. We want signs — numbers like
$+1$ and $-1$ that can *cancel*. Here is the trick that converts one into
the other, and it is the single most reused idea in quantum algorithms.

### The minus-sign spring

Prepare the spare register not in $|0\rangle$ or $|1\rangle$, but in the
state

$$
|-\rangle \;=\; \frac{|0\rangle - |1\rangle}{\sqrt{2}}
$$

which is a perfectly ordinary state: "equal parts 0 and 1, with a minus
sign on the 1". Now ask what XOR does to it.

- If $f(x) = 0$, XOR-ing 0 changes nothing. The register stays $|-\rangle$.
- If $f(x) = 1$, XOR-ing 1 **swaps** the roles of $|0\rangle$ and
  $|1\rangle$. The state becomes $\frac{|1\rangle - |0\rangle}{\sqrt 2}$.

Look hard at that second one. It is the same state as $|-\rangle$ with
every term negated:

$$
\frac{|1\rangle - |0\rangle}{\sqrt{2}}
\;=\; -\,\frac{|0\rangle - |1\rangle}{\sqrt{2}}
\;=\; -\,|-\rangle
$$

The spare register **came back unchanged** — and spat out a minus sign,
which has nowhere to live except in front of the whole expression, which is
to say: **on the input register**.

<div class="qq-anim" data-anim="kickback"></div>

Put together, for an input in superposition:

$$
\sum_x |x\rangle\,|-\rangle
\;\xrightarrow{\;U_f\;}\;
\sum_x (-1)^{f(x)}\,|x\rangle\,|-\rangle
$$

The spare register is now dead weight — it is in exactly the state it
started in, unentangled, and we can forget it forever. What we have gained
is that **every input amplitude now carries the sign of $f$ at that
input**. This is called **phase kickback**: the answer was "kicked back"
from the target register onto the phases of the input.

??? note "▸ deeper — why this is the same as a 'phase oracle'"

    Because the target register factors out, the whole operation is
    equivalent to a simpler object that acts on the input register alone:

    $$O_f : |x\rangle \mapsto (-1)^{f(x)}|x\rangle$$

    a diagonal matrix of $\pm 1$. That is what our simulator's
    `phase_oracle` builds, and the equivalence is not assumed — it is
    checked in [`qsim/test_qsim.py`](../../qsim/test_qsim.py), in
    `test_phase_kickback_ties_the_two_oracle_forms`.

!!! quote "Why signs are the whole game"

    A list of *values* can only be looked at one at a time. A list of
    *signed amplitudes* can **cancel**: put $+a$ and $-a$ on the same
    outcome and that outcome becomes impossible. Classical probabilities
    are non-negative and can never cancel — they only pile up.
    Cancellation is the one genuinely non-classical resource in this
    entire subject, and phase kickback is how you load your problem into
    it.

---

## 4. The sandwich, one layer at a time

Now the algorithm. It is three steps: a layer of Hadamard gates, one oracle
call, another layer of Hadamard gates. The traditional presentation writes
that as a diagram and moves on, which explains nothing. Let us do it
slowly.

### The Hadamard gate

On one qubit, $H$ turns a definite state into an even mixture:

$$
H|0\rangle = \frac{|0\rangle + |1\rangle}{\sqrt2},
\qquad
H|1\rangle = \frac{|0\rangle - |1\rangle}{\sqrt2} \;=\; |-\rangle
$$

Two facts matter. First, applied to all $n$ qubits at once
($H^{\otimes n}$, "an $H$ on every wire"), it turns the single state
$|0\dots0\rangle$ into an equal superposition of **all** $2^n$ patterns —
that is our "spread all inputs" step. Second, and this is the one people
miss:

$$
H \cdot H = I
$$

**$H$ is its own inverse.** Apply it twice and you are exactly back where
you began.

### The reframing that makes the algorithm obvious

That second fact hands us the whole design. Suppose we ran the circuit with
**no oracle in the middle** — just $H^{\otimes n}$ twice in a row. Then by
$H\cdot H = I$ we would land back on $|0\dots0\rangle$ with **certainty**.

So put the oracle in the middle and ask a single question:

!!! success "Deutsch–Jozsa in one sentence"

    $H^{\otimes n}$ spreads out, the oracle stamps signs, and
    $H^{\otimes n}$ tries to gather everything back onto
    $|0\dots0\rangle$. **The only thing that can spoil the return home is
    the oracle's pattern of signs.** So: *did we come home?*

    - All signs agree (**constant** $f$) — nothing was disturbed, the
      gathering succeeds perfectly, and you measure $|0\dots0\rangle$ with
      probability **1**.
    - Half the signs are flipped (**balanced** $f$) — the contributions to
      $|0\dots0\rangle$ cancel *exactly*, and you measure it with
      probability **0**.

    One measurement distinguishes probability 1 from probability 0 with
    certainty. That is the algorithm.

Watch it happen. Step through the three acts, and switch $f$ to compare a
constant function against a balanced one:

<div class="qq-anim" data-anim="sandwich"></div>

Three things to notice while you play:

1. **Act 2 changes no heights.** The oracle never makes any outcome more or
   less likely on its own — it only paints signs. If you measured right
   after the oracle you would learn nothing at all (that is §2 again).
2. **Act 3 is where physics does the work.** All the signed amplitudes are
   added together, and the sum lands on $|0\dots0\rangle$. Agreement
   builds; disagreement annihilates.
3. **Try the last option** — the function that is *neither* constant nor
   balanced. The readout comes out between the two answers, and the
   algorithm's output is meaningless. **The promise is load-bearing**: it
   is not a convenience for interpreting the result, it is a precondition
   for the interference pattern being one of only two possible shapes.

??? note "▸ deeper — the two lines of algebra"

    Start in $|0\rangle^{\otimes n}$, apply $H^{\otimes n}$:

    $$\frac{1}{\sqrt{2^n}}\sum_{x} |x\rangle$$

    Apply the oracle (phase kickback, §3):

    $$\frac{1}{\sqrt{2^n}}\sum_{x} (-1)^{f(x)} |x\rangle$$

    Apply $H^{\otimes n}$ again. The general rule is
    $H^{\otimes n}|x\rangle = 2^{-n/2}\sum_z (-1)^{x\cdot z}|z\rangle$
    where $x \cdot z$ is the bitwise dot product mod 2. Collecting the
    coefficient of $|z = 0\dots0\rangle$ (where $x\cdot z = 0$ always):

    $$
    \text{amplitude of } |0\dots0\rangle
    \;=\; \frac{1}{2^n}\sum_{x\in\{0,1\}^n} (-1)^{f(x)}
    $$

    which is precisely **the average of $s(x) = (-1)^{f(x)}$** — the global
    property from §2. Constant $f$ gives $\pm1$ (probability
    $|\pm1|^2 = 1$); balanced $f$ gives $0$.

And here is the same thing measured on our own simulator, at $n = 10$:

<figure markdown="span">
  ![Deutsch–Jozsa interference readout](fig-interference.svg#only-light)
  ![Deutsch–Jozsa interference readout](fig-interference-dark.svg#only-dark)
  <figcaption>Real output of <code>deutsch_jozsa.py</code> (n = 10).
  Constant functions land on 1, balanced on 0 — and the yellow bar is a
  function <em>outside</em> the promise, where the answer (0.25) means
  nothing at all.</figcaption>
</figure>

---

## 5. Why the Hadamard layer is really a Fourier transform

??? note "▸ deeper — optional, but it is the thread through the next twelve autopsies"

    $H^{\otimes n}$ is exactly the **Fourier transform over the group
    $\mathbb{Z}_2^n$**. Its matrix entries are $2^{-n/2}(-1)^{x\cdot z}$ —
    the characters of that group, the $\mathbb{Z}_2^n$ analogue of
    $e^{2\pi i k x/N}$.

    That reframes everything above. The final $H^{\otimes n}$ does not
    compute *one* number; it computes **all $2^n$ Fourier coefficients of
    the sign function $(-1)^{f}$ simultaneously**, one per basis state.
    Measuring $|0\dots0\rangle$ reads the coefficient at **frequency
    zero** — and the zero-frequency Fourier coefficient of any function is
    its mean. Hence §4's answer.

    This is the seed of everything that follows in this curriculum:

    - **Deutsch–Jozsa** reads the frequency-0 coefficient (the mean).
    - **[Bernstein–Vazirani](../02-bernstein-vazirani/notes.md)** hides a
      string $s$ so that *all* the amplitude lands on the single frequency
      $s$ — read it off in one shot.
    - **[Simon](../03-simon/notes.md)** uses a function with a hidden XOR
      period, so the surviving frequencies are exactly those orthogonal to
      the period; sample a few, solve a linear system.
    - **[Shor](../04-shor/notes.md)** replaces $\mathbb{Z}_2^n$ with
      $\mathbb{Z}_N$ and the Hadamard layer with the full quantum Fourier
      transform, so the surviving frequencies reveal a *period* over the
      integers — which is factoring.

    Same skeleton every time: **put a function into phases, Fourier
    transform, and read off which frequencies survived.** What changes from
    algorithm to algorithm is the group and the structure hidden in $f$ —
    never the mechanism. Learn this once and twelve autopsies become
    variations.

    **Want this properly?**
    [Deep dive 01 — the Fourier thread](../../study-deep-dive/01-fourier-thread/notes.md)
    is this box taken seriously: why the Fourier basis is the eigenbasis of
    *shift*, why $H$ is literally a character table, which spectral shapes
    are readable and which are not, where exactness dies when the group
    changes, and the classical theorem (Kushilevitz–Mansour) that stands
    exactly where you hoped to plant a flag. With live widgets and code you
    can run.

---

## 6. What actually happens in a laboratory

Everything above is arithmetic. Here is the physical machine, because
"interference" should mean something you can picture.

### The gates are pulses

There is no little box labelled $H$. On a superconducting machine, a qubit
is a tiny circuit whose two lowest energy levels are $|0\rangle$ and
$|1\rangle$, cooled to about 15 millikelvin — colder than deep space. A
Hadamard is a **microwave pulse of a precise duration and phase**, roughly
20–30 nanoseconds long, delivered by a wire into the chip. On a trapped-ion
machine, the qubit is a single atom held in an electric trap and the gate
is a **laser pulse** lasting microseconds. "Applying $H$" means: fire the
pulse, correctly shaped, at the right moment.

A **phase flip** — that $-1$ we have been moving around — is not a spooky
label. It is a change in *when* the qubit's internal rotation arrives: the
same oscillation, shifted half a cycle. Two waves half a cycle apart cancel
when added. That is all a minus sign has ever meant.

### It is an interferometer

If you have seen the two-slit experiment or a Mach–Zehnder interferometer,
you already know the physics. Split a beam into two paths, let one path
travel a slightly different distance, then recombine them. Whether the
light comes out of the "bright" port or the "dark" port depends only on
whether the two paths arrive **in step** or **out of step**.

<div class="qq-anim" data-anim="interferometer"></div>

Deutsch–Jozsa is that device with $2^n$ arms instead of two.

- The first $H^{\otimes n}$ is the beam splitter: one path becomes 1024.
- The oracle is a phase plate in each arm: it delays some arms by half a
  cycle ($f(x)=1$) and leaves others alone ($f(x)=0$).
- The second $H^{\otimes n}$ is the recombiner.
- Measuring $|0\dots0\rangle$ is **looking at the bright port**.

Constant $f$: every arm arrives in step, and all 1024 add up at the bright
port — the lamp is on, guaranteed. Balanced $f$: 512 arms arrive exactly
out of step with the other 512, and the bright port is **perfectly dark**.
Not dim: dark. That total darkness is the "probability 0" from §4, and it
is the same effect as the dark fringes in a two-slit pattern.

### How you would actually sense it

You never see an amplitude. You get one bitstring per run. So you run the
circuit a few thousand times and build a histogram:

- **Constant $f$**: essentially every shot reads `0000000000`.
- **Balanced $f$**: essentially no shot does.

You are not measuring a subtle number; you are checking whether a
particular outcome shows up at all. Which is why this is such a robust
little algorithm — and why it is a poor test of hardware, as the next
section shows.

---

## 7. What a real machine gives you

Time to stop hand-waving about hardware and compute it, using this repo's
own machine-noise models and the published error rates from the
[Machines catalog](../../machines/index.md).

First, the circuit has to become real gates. The dense $2^n$ oracle matrix
does not exist on any device — but for the balanced function
$f(x) = x\cdot s$ (parity of a subset of bits), **the oracle is literally
just CNOT gates**: one CNOT from each input qubit in $s$ onto the ancilla.
With the ancilla in $|-\rangle$, each CNOT kicks back a sign exactly as in
§3. Phase kickback, made of hardware.

So the honest budget for Deutsch–Jozsa on $n$ inputs is:

| resource | count |
|---|---|
| qubits | $n + 1$ (inputs + one ancilla) |
| single-qubit gates | $2n + 2$ |
| two-qubit gates (CNOT) | number of bits in $s$ — at most $n$; **zero** for a constant $f$ |
| measurements | $n$ |

For $n=10$ that is 22 single-qubit gates, 10 CNOTs, 11 qubits. Now run it
under real error rates ([`dj_on_hardware.py`](dj_on_hardware.py), one fresh
noise trajectory per shot):

| machine | P(0…0), constant | P(0…0), balanced | decision margin |
|---|---:|---:|---:|
| ideal | 1.000 | 0.000 | 1.000 |
| Quantinuum Helios | 0.991 | 0.000 | 0.991 |
| IBM Heron r2 | 0.916 | 0.000 | 0.916 |
| Google Willow | 0.911 | 0.000 | 0.911 |
| Rigetti Ankaa-3 | 0.906 | 0.000 | 0.906 |

Every machine gets the answer right, comfortably. But look *where* the loss
comes from — it is not where beginners expect:

!!! info "The margin is eaten by readout, not by gates"

    The superconducting machines all land near 0.91, and they land there
    *together*, despite two-qubit error rates differing by 60% between
    them. The reason: this circuit is only 10 CNOTs deep, so gate error
    contributes about 3%, while **measuring 10 qubits at roughly 1%
    readout error each costs about 10%**. Readout dominates completely.

    Quantinuum Helios pulls ahead not because its gates are better (they
    are) but because its *measurement* is: a published SPAM error of
    4.8×10⁻⁴ against the ~1% we must assume for machines that do not
    publish theirs. Which is itself a lesson about the catalog — see
    [how to read a spec sheet](../../machines/metrics.md).

Push $n$ up and the picture becomes a scaling statement:

<figure markdown="span">
  ![Deutsch–Jozsa under real machine noise](fig-hardware.svg#only-light)
  ![Deutsch–Jozsa under real machine noise](fig-hardware-dark.svg#only-dark)
  <figcaption>Left: simulated noisy runs (dots) against the analytic error
  model (lines). Right: the same model extrapolated — the decision margin
  falls below 0.5 at roughly n ≈ 65 for today's superconducting readout,
  and near n ≈ 1300 for Helios-class measurement. Generated by
  <code>scripts/make_dj_figures.py</code> from the error rates in
  <code>machines/data.yml</code>.</figcaption>
</figure>

So Deutsch–Jozsa would survive on real hardware out to something like
**65 qubits** today. That sounds impressive until you remember the next
section: a classical computer settles the same question in three
coin-flips' worth of work. **DJ is the cheapest possible quantum circuit
and still proves nothing** — which is precisely why "we ran algorithm X on
N qubits" is never by itself a result. What matters is whether the task was
hard, and this one is not.

---

## 8. The classical wall — and the crack in it

Back to the honest accounting.

- **Deterministic and exact:** $2^{n-1}+1$ queries in the worst case, as we
  worked out in §0. Against this baseline, one query versus 513 is a real
  and provable separation.
- **Randomized, allowing a tiny error probability:** $O(1)$ queries. Pick a
  few patterns at random. If you ever see two different colours, the box is
  balanced, certainly. If you see $k$ patterns all the same colour, call it
  constant — and you are wrong with probability at most $2^{-(k-1)}$ under
  the promise, because a balanced box would have had to hand you $k$
  matching colours by luck.

Ten random looks make you wrong less than once in five hundred runs.
Twenty looks, less than once in five hundred thousand.

!!! danger "The field's founding weak-baseline incident (1992)"

    The exponential separation is **only** against deterministic exact
    computation. Allow the classical algorithm the same tiny error
    probability that every real quantum device has anyway — remember §7,
    where our "certain" answer arrived at 0.91 — and the gap collapses
    from exponential to $O(1)$ versus $1$.

    This is the first named quantum algorithm, and its advantage dies
    against the right classical baseline. That pattern — a claim that
    stands only against a baseline nobody would actually use — has
    repeated for thirty years and is the reason this repository takes
    classical attacks as seriously as it does. See the
    [claim ledger](../../machines/gap.md) for the modern instances of the
    same story.

**What survives:** the exact-versus-exact separation is real mathematics
and still stands. And far more importantly, **the mechanism survives** —
kickback into phases, Fourier transform, read a coefficient — and goes on
to carry Simon, and then Shor, where the problem *is* hard and the baseline
*does* hold.

### Who cared about this problem?

**Nobody.** Not before, and not after. The problem was reverse-engineered
to showcase a mechanism: Deutsch (1985) asked whether interference could
provably compute something with fewer queries, and the
constant-versus-balanced puzzle was built to be the thing it could do. DJ
is a solution in search of a problem.

That is not a dismissal — it is the single most important strategic lesson
in this autopsy, and it is why this curriculum exists. The mechanism was
right and the problem was fake. The next thirty years of the field have
largely been a search for **real problems with the shape this mechanism
wants**. Finding one is the whole job.

!!! question "Stop and think"

    Why does randomness collapse *this* particular wall, and what would a
    problem need so that randomness *doesn't* help?

    ??? success "One answer"

        A random classical sample already estimates the **mean** of
        $(-1)^f$ cheaply — and DJ's global property *is* that mean, so it
        was statistically easy all along. Randomness stops helping when
        each query carries almost no information about the answer until an
        exponentially rare coincidence occurs. Build a function where two
        random inputs almost never collide, but the *pattern* of collisions
        is the answer, and sampling learns nothing. That is
        [Simon's problem](../03-simon/notes.md) — and it is what a real
        exponential separation looks like.

---

## 9. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    One paragraph, your own words: what *shape* of problem does this
    mechanism want? What died against the randomized baseline, and what
    survived? This paragraph becomes a Problem-Shape Catalog entry in
    week 5.

---

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/01-deutsch-jozsa/deutsch_jozsa.py
    .venv/bin/python predecessors/01-deutsch-jozsa/dj_on_hardware.py
    .venv/bin/pytest predecessors/01-deutsch-jozsa -q
    ```

- [ ] Read [`deutsch_jozsa.py`](deutsch_jozsa.py) against §4 until every
      line is obvious.
- [ ] The demo includes an $f$ outside the promise (AND of two bits,
      $p_0 = 1/4$). In one sentence: why is the promise load-bearing for
      the interference pattern, not just for interpreting the output?
- [ ] In [`dj_on_hardware.py`](dj_on_hardware.py), change the balanced
      function's mask $s$ so that only **two** bits are set. The CNOT count
      drops from 10 to 2. Predict what happens to the decision margin
      before you run it — then run it. Does gate error or readout error
      dominate? (§7 tells you the answer; make yourself derive it.)
- [ ] Write §9.
