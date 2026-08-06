# Autopsy 06 — Grover (1996), amplitude amplification, and the BBBV ceiling

*The quadratic workhorse — and the theorem that fences the whole hunt.*

!!! tip "How to read this page"

    Everything before this autopsy was about finding *structure* to
    exploit. This one is about what happens when there is none — and it is
    the only page in the curriculum where the field knew the answer before
    it had the algorithm.

    Sections 0–2 are the algorithm and need nothing but the picture of a
    rotating arrow. Section 3 is the ceiling, run on a real state vector
    rather than quoted. Sections 4–6 are the part that decides whether any
    of it matters, and they are arithmetic anyone can check.

    Two sentences to carry:

    > **The ceiling was proved before the algorithm existed.** Bennett,
    > Bernstein, Brassard and Vazirani showed $\Omega(\sqrt N)$ queries are
    > necessary *before* Grover showed $O(\sqrt N)$ are sufficient.
    >
    > **Grover is a magnificent subroutine and a terrible flagship.**

---

## 0. The problem with nothing in it

$N$ boxes. Exactly one contains the prize. You may ask "is it in box $x$?"
as often as you like. Find it.

Classically this costs $\Theta(N)$ questions, and the triviality of that
statement is the entire point of this autopsy: **there is nothing to
exploit.** No period, no hidden subgroup, no algebraic shadow — the boxes
are unrelated to one another by construction. Every previous algorithm in
this curriculum ran on structure. This one has none, so it is the cleanest
possible test of what interference alone is worth.

The answer is: a square root. Not more, and — this is the surprising half —
not less either.

---

## 1. The whole algorithm is one rotation

Start in the uniform superposition over all $N$ boxes. Two operations:

- **the oracle**, which flips the sign of the marked item's amplitude;
- **the diffusion operator**, which flips every amplitude about the average.

Each is a *reflection*. And two reflections make a **rotation** — that is a
fact about geometry, not about quantum mechanics. So the state turns by a
fixed angle each iteration, in the two-dimensional plane spanned by "the
marked item" and "everything else". Nothing ever leaves that plane.

<div class="qq-anim" data-anim="groverspin"></div>

With $M$ marked items out of $N$, write $\sin\theta = \sqrt{M/N}$. After $t$
iterations the state has turned to angle $(2t+1)\theta$, so

$$
P(\text{success}) \;=\; \sin^2\!\big((2t+1)\,\theta\big),
$$

and it reaches 1 when $(2t+1)\theta \approx \pi/2$, i.e. after about
$\frac{\pi}{4}\sqrt{N/M}$ iterations. Our simulator agrees with that formula
to $10^{-10}$ at every step, for every $t$
(`test_formula_matches_the_circuit_at_every_step`) — the rotation picture is
not an approximation, it is exact.

<figure markdown="span">
  ![Grover is a rotation](fig-rotation.svg#only-light)
  ![Grover is a rotation](fig-rotation-dark.svg#only-dark)
  <figcaption>Real output of <code>grover.py</code> (n = 8, N = 256). At the
  optimal k = 12 the success probability is 0.9999; run twice as long and it
  falls to 0.006 — the rotation sails straight past the target.</figcaption>
</figure>

??? note "▸ deeper — why two reflections are a rotation, and why the plane is closed"

    Let $|w\rangle$ be the marked state and $|r\rangle$ the normalised
    uniform superposition over everything else. The starting state
    $|s\rangle$ lies in $\mathrm{span}\{|w\rangle, |r\rangle\}$, and both
    operators map that plane to itself: the oracle is a reflection about
    $|r\rangle$, and the diffusion operator is a reflection about
    $|s\rangle$. In a plane, reflecting about one line and then about
    another at angle $\alpha$ to it is a rotation by $2\alpha$ — a fact from
    school geometry.

    That is the whole mechanism, and it explains the limitation as well as
    the power. The dynamics are confined to **two dimensions** no matter how
    large $N$ is, and a rotation in two dimensions has one parameter. There
    is nowhere for the algorithm to hide extra structure, which is exactly
    why it cannot do better than a rotation's worth of work — see §3.

---

## 2. The soufflé: more queries can be worse

A rotation does not stop when it arrives. Keep iterating and the state
sails past the marked item and out the other side. At $N = 4096$ the optimal
50 iterations give $p = 0.9999$; running 100 gives $p = 0.0000$
(`test_the_souffle_running_twice_as_long_is_much_worse`).

This is unlike any classical search. You cannot run Grover "until it works",
because the algorithm has no notion of having arrived — and checking would
require a measurement, which destroys the superposition you have been
building.

So Grover needs to know $N$ **and $M$** before it starts. And $M$ matters
more than you would expect:

<figure markdown="span">
  ![The stopping point moves with M, and the cost of not knowing it](fig-souffle.svg#only-light)
  ![The stopping point moves with M, and the cost of not knowing it](fig-souffle-dark.svg#only-dark)
  <figcaption>Left: success probability over (iterations, number of
  solutions) — the white ridge is where you must stop, and it moves sharply
  with M. Right: the measured cost of not knowing M, via the BBHT
  exponential-search schedule.</figcaption>
</figure>

Not knowing $M$ costs a constant factor, not an asymptotic one — the
Boyer–Brassard–Høyer–Tapp schedule guesses an iteration count, checks the
answer, and grows the guess by $6/5$ on failure. Measured here at about
$1.5\sqrt{N/M}$ (`test_bbht_stays_within_a_constant_of_knowing_M`).

!!! question "Stop and think"

    BBHT has to *check the answer classically* after each attempt. What does
    that quietly assume about the oracle — and which "Grover speeds up
    database search" claims does it kill?

    ??? success "One answer"

        It assumes you can **evaluate the predicate yourself**, cheaply, on
        a candidate. That is true for a computed predicate — "is this the
        AES key?", "does this assignment satisfy the formula?" — and false
        for an actual database, where the only way to know what is in box
        $x$ is to look in box $x$.

        And that is the deeper problem with "Grover searches a database of
        $N$ items in $\sqrt N$ steps": to search a database in
        superposition you must first *load* it into the machine, which costs
        $\Omega(N)$ before the first iteration. The quadratic advantage is
        spent before the algorithm starts. Grover helps for **computed**
        haystacks, never for stored ones — the same instantiation fine print
        as [autopsy 01 §1](../01-deutsch-jozsa/notes.md).

---

## 3. The ceiling, run rather than quoted

Here is the healthiest event in this whole curriculum. Bennett, Bernstein,
Brassard and Vazirani proved that **no** quantum algorithm can search $N$
unstructured items with fewer than $\Omega(\sqrt N)$ queries — and they did
it *before* Grover's algorithm appeared.

The argument is short enough to run on a computer, so we did.

<div class="qq-anim" data-anim="attention"></div>

Run any algorithm on an oracle that marks *nothing*, and record how much
amplitude sits on each item at each query. Call the total for item $x$ its
**query attention** $q_x$. Then:

1. **The sum rule.** $\sum_x q_x = T$ exactly, where $T$ is the number of
   queries — whatever the algorithm does in between
   (`test_query_attention_sums_to_exactly_T`, verified on the real state
   vector at $n = 4, 6, 8, 10$).
2. **The pigeonhole.** $T$ units spread over $N$ items means some item
   receives at most $T/N$ (`test_some_item_is_almost_ignored`).
3. **Cauchy–Schwarz.** Marking *that* item perturbs the final state by at
   most $2\sqrt{T q_x} \le 2T/\sqrt N$.
4. **Therefore** telling the marked run from the empty one requires
   $2T/\sqrt N$ to be a constant, i.e. $T = \Omega(\sqrt N)$
   (`test_the_bound_forces_a_square_root`).

<figure markdown="span">
  ![The hybrid argument and the ceiling it implies](fig-ceiling.svg#only-light)
  ![The hybrid argument and the ceiling it implies](fig-ceiling-dark.svg#only-dark)
  <figcaption>Left: two very different strategies, both spending exactly T
  units of attention — the pigeonhole applies to either. Right: the ceiling
  is monotone in T (an algorithm may always stop early), and Grover touches
  it at the optimum. The gap afterwards is not slack in the bound; it is the
  soufflé.</figcaption>
</figure>

**Zalka (1999) closed the constant**: the bound is not merely
$\Omega(\sqrt N)$, it is exactly the Grover curve. Grover is optimal, not
just asymptotically optimal. There is no cleverer schedule, no better
diffusion operator, and no room left at all.

!!! warning "The theorem that draws the map for this whole repository"

    The generalisation (the Aaronson–Ambainis line) is the one to remember:
    for problems **invariant under permuting the inputs**, quantum speedup is
    at most polynomial. No structure, no exponential advantage — ever, by
    theorem.

    That is why the Quest hunts exclusively in structured territory. The
    fence is not a matter of taste or of present-day cleverness; it is
    proved. Every "quantum computers try all possibilities at once" claim
    collides with it, and the collision is fatal.

---

## 4. Where the speedup actually goes: depth

Now the part that decides whether any of this is useful, and it needs no
assumption about how the oracle is built.

**Grover's iterations are strictly sequential.** Iteration $t+1$ cannot
begin until iteration $t$ has finished, however many qubits you own. So the
cost is *depth*, and a 128-bit key search needs

$$
\tfrac{\pi}{4}\,2^{64} \;\approx\; 1.45 \times 10^{19} \ \text{sequential iterations.}
$$

This repository already established the relevant clock in
[machines/gap.md](../../machines/gap.md): a distance-25 logical operation
takes about 25 µs on superconducting hardware — a ~40 kHz logical clock.
Charging **one logical operation for an entire Grover iteration**, which is
absurdly generous:

| target | sequential iterations | wall clock, at 1 op per iteration |
|---|---|---|
| AES-128 key search | $1.45\times10^{19}$ | **11.5 million years** |
| AES-192 key search | $6.22\times10^{28}$ | $4.9\times10^{16}$ years |
| AES-256 key search | $2.67\times10^{38}$ | $2.1\times10^{26}$ years |

With a realistic oracle (a few thousand logical operations per AES
evaluation) the AES-128 figure becomes $\approx 10^{11}$ years — for scale,
the universe is $1.4\times10^{10}$ years old.

<figure markdown="span">
  ![Depth, parallelism, and the crossover](fig-cost.svg#only-light)
  ![Depth, parallelism, and the crossover](fig-cost-dark.svg#only-dark)
  <figcaption>Computed by <code>grover_resources.py</code> against this
  repository's own logical-clock figure. The model is stated in the module
  docstring so it can be argued with.</figcaption>
</figure>

---

## 5. The asymmetry that settles it

There is one more fact, and it is the one that turns "expensive" into
"structurally losing".

**Classical search is embarrassingly parallel: $k$ machines give a speedup
of $k$. Grover is not: $k$ machines give $\sqrt k$.** Each quantum machine
searches its own $N/k$ slice in $\sqrt{N/k}$ steps, and Zalka proved you
cannot do better.

<div class="qq-anim" data-anim="groverwall"></div>

So every purchase of hardware favours the classical side, and the size at
which the quadratic finally pays runs away as the other side buys cores:

| classical hardware | Grover wins only above |
|---|---|
| one core | $N > 2^{35}$ |
| $10^3$ cores | $N > 2^{55}$ |
| $10^6$ cores | $N > 2^{75}$ |
| $10^9$ cores | $N > 2^{94}$ |

Charging the oracle honestly on both sides — reversible and error-corrected
on the quantum side — pushes the single-core figure from $2^{35}$ to
$2^{41}$.

!!! success "The honest window, because it does exist"

    It would be over-claiming in the other direction to say Grover never
    wins. Set the widget above to $N = 2^{64}$ with $2^{13}$ logical
    operations per iteration and one classical core: quantum takes about 22
    years, classical about 88. Quantum wins, by a factor of four.

    That window is real, and it is also the whole story: it needs a
    **fault-tolerant machine at a 40 kHz logical clock**, a search space of
    $2^{64}$, a **computed** predicate, and an opponent who never buys a
    second core. Move any one of those and the window shuts. That is what a
    quadratic speedup is actually worth — and it is why the field's
    attention moved to problems where the exponent itself changes.

Our own toy circuit is a useful humility check: $N = 4096$ — a search space
a laptop finishes instantly — already scores **NO** on every machine in the
catalog (`test_no_existing_machine_runs_grover_on_twelve_qubits`).

---

## 6. What survives

Quite a lot, as long as it is not asked to be the headline:

- **Amplitude amplification** (Brassard–Høyer–Mosca–Tapp 2000) is the real
  export. Any algorithm with success probability $p$ can be boosted with
  $O(1/\sqrt p)$ repetitions instead of $O(1/p)$ — a subroutine that appears
  inside almost everything else.
- **Amplitude estimation** turns that rotation into a phase and estimates
  $M/N$ with quadratically fewer samples than classical Monte Carlo. This is
  the engine inside most claimed "quadratic speedup" applications, including
  the planted-inference results at the modern frontier.
- **As an inner loop**, where the *outer* algorithm supplies the structure —
  which is exactly the shape [DQI](../11-dqi/notes.md) has, and the shape
  our own [strike](../../strike/crt-dqi-theorem.md) work aims at.

The verdict is not that Grover is bad. It is that a quadratic speedup is a
**component**, and the field spent a decade treating it as a product.

---

## 7. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    Argue with the draft, then replace it.

    <div class="qq-lesson" markdown>

    **The ceiling was proved before the algorithm existed, and that is the
    healthiest event in this curriculum.** Everywhere else the field found a
    result and then spent years discovering what it was worth; here the
    limit came first, so nobody could over-claim about unstructured search
    without contradicting a published theorem. Compare autopsy 01, where the
    absence of a baseline let a non-result stand for thirty years.

    The 2-D rotation picture says where the power comes from and why it
    cannot compound: the entire dynamics live in a **two-dimensional plane**,
    however large $N$ is. One rotation angle, one parameter, one square
    root. There is no room in two dimensions for the kind of structure that
    turns polynomial into exponential — which is precisely why
    Aaronson–Ambainis can prove the fence.

    And the practical verdict is a resource statement, not an opinion:
    Grover's cost is **depth**, depth is sequential, and sequential time is
    the one resource that cannot be bought in parallel. Every other
    algorithm in this curriculum trades qubits for time; this one cannot.

    </div>

Questions worth answering in your own words:

- Why does "no structure ⇒ at most polynomial" make §3 a *map* rather than a
  disappointment? What does it tell you to stop reading?
- Amplitude estimation is a genuine quadratic win over Monte Carlo. Under
  what conditions does that survive §4 and §5 — and is any real application
  in that regime?
- If a claim crosses your desk saying "quadratic speedup for X", what are the
  three numbers you now ask for before reading the abstract?

---

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/06-grover/grover.py            # the circuit
    .venv/bin/python predecessors/06-grover/grover_limits.py     # §1–§3
    .venv/bin/python predecessors/06-grover/grover_resources.py  # §4–§5
    .venv/bin/pytest predecessors/06-grover -q                   # 50 tests
    ```

- [ ] **Proof draft #3:** the BBBV bound via the hybrid argument. Draft it
      before reading §3, then check your version against the four numbered
      steps — and against `query_magnitudes`, which computes step 1 on the
      real state vector.
- [ ] Explain the overshoot exactly: for $n = 8$, compute
      $(2 \cdot 24 + 1)\theta$ in radians and show why the answer is
      $p = 0.006$ rather than something small but respectable.
- [ ] In `grover_limits.py`, replace the uniform starting state with a
      biased one and re-run `query_magnitudes`. Does the sum rule still
      hold? (It must — say why in one sentence.) Does the *minimum* still
      fall below $T/N$?
- [ ] Amplitude estimation in one paragraph: how does phase estimation on
      the Grover rotation turn $M/N$ into a readable phase, and where does
      the quadratic saving actually appear?
- [ ] **The pricing exercise.** Pick any published "quadratic speedup"
      application you find plausible. Using `grover_resources.py`, work out
      the search-space size at which it would beat a single classical core,
      then a thousand. Write down whether the application's real instances
      are anywhere near that size — before looking up what the authors
      claim.
