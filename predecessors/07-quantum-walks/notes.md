# Autopsies 07–08 — Quantum walks: glued trees and Szegedy

*The only exponential speedup in this course that owes nothing to the Fourier
transform — and the one whose fragility is easiest to measure.*

!!! tip "How to read this page"

    Every other exponential separation in this curriculum came from
    [the Fourier thread](../../study-deep-dive/01-fourier-thread/notes.md):
    hide a subgroup, transform, read the surviving frequencies. This one does
    not. It comes from a difference in how fast two kinds of walker spread,
    and that makes it the cleanest available test of whether a *mechanism*
    other than Fourier sampling can carry an exponential.

    Sections 0–3 are the mechanism and the win. Sections 4–5 are what it
    costs to keep, and both are computed here rather than cited —
    [`walk_transport.py`](walk_transport.py) and [`szegedy.py`](szegedy.py),
    pinned by 34 tests.

    Three sentences to carry:

    > **The whole speedup is one exponent**: a quantum walker spreads as
    > $t$, a classical one as $\sqrt t$.
    >
    > **The separation is unconditional** — the classical lower bound is a
    > theorem, not a hardness assumption.
    >
    > **And it is the most fragile advantage in the curriculum**: the
    > imperfection it tolerates *shrinks* as the problem grows.

---

## 0. Two problems, one primitive

- **Glued trees** (Childs–Cleve–Deutsch–Farhi–Gutmann–Spielman 2003): two
  full binary trees of depth $d$, their leaves joined by a random cycle.
  Enter at the left root; **find the right root.** You get adjacency access
  and nothing else.
- **Markov-chain search** (Szegedy 2004; Magniez–Nayak–Roland–Santha): find
  the marked states of a reversible chain faster than its mixing time.

The first is a one-off with an exponential payoff. The second is the
systematic construction that works on *any* chain — and, as §5 measures,
comes with a systematic ceiling.

---

## 1. The classical wall

A classical walker on the glued trees is not merely slow; it is pushed the
wrong way. From any vertex inside a tree, **two of three edges point toward
the middle and one points out**, so the walk drifts into the exponentially
fat centre and stays there. Reaching the far root takes $2^{\Omega(d)}$
steps, and the random cycle in the middle prevents any cleverer classical
strategy from working out where it is.

That lower bound is a **theorem**, not a conjecture — which makes this the
only unconditional exponential separation in the curriculum.

---

## 2. The mechanism: a front, not a blob

Here is the whole idea, and it is a statement about spreading.

A classical random walker's position is a sum of independent steps, so its
spread grows like $\sqrt t$ — the familiar diffusion. A quantum walker on a
line is a *wave*, and waves have a group velocity: the amplitude runs out in
two fronts that keep moving, so the spread grows like $t$.

<div class="qq-anim" data-anim="walkrace"></div>

Measured rather than asserted: fitting $\langle x^2\rangle \sim t^{\alpha}$
gives **2.00 for the quantum walk and 1.00 for the classical one**
(`test_the_exponents_are_two_and_one`), and essentially no quantum amplitude
is found outside the light cone $|x| \le 2t$
(`test_quantum_packet_stays_inside_its_light_cone`).

<figure markdown="span">
  ![A ballistic front against a diffusive blob](fig-transport.svg#only-light)
  ![A ballistic front against a diffusive blob](fig-transport-dark.svg#only-dark)
  <figcaption>Left: the quantum walk puts its weight at the front and keeps
  going; the classical walk piles up where it started. Right: the two
  exponents, fitted. Everything else on this page follows from
  them.</figcaption>
</figure>

On the glued-trees graph that difference is decisive: the classical drift
pulls inward at speed $\propto$ the bias, while the quantum front crosses
$2d+2$ columns in time $O(d)$ regardless.

??? note "▸ deeper — why a $2^{d+2}$-vertex graph fits in $2d+2$ dimensions"

    Both walks start in a state symmetric under permuting vertices within a
    column, and every operator here preserves that symmetry. So the dynamics
    live entirely in the **column space** spanned by

    $$
    |\mathrm{col}_j\rangle \;=\; \frac{1}{\sqrt{N_j}}\sum_{v \in \mathrm{col}_j} |v\rangle ,
    $$

    which has $2d+2$ dimensions rather than $\sim 2^{d+2}$. That is why
    `glued_trees.py` can simulate a graph with a million vertices exactly on
    a laptop.

    Working out the reduced weights is the first exercise below: hopping
    $\sqrt 2$ inside the trees, and $2$ across the glue. The reduced chain
    is therefore a **uniform path with one defect** — remember the word
    *uniform*, because §4 is about what happens when it is not.

    The classical side reduces the same way, to a biased birth–death chain
    with $2/3$ inward and $1/3$ outward — the drift, in one line.

---

## 3. The separation, measured

<figure markdown="span">
  ![Quantum vs classical exit probability](fig-separation.svg#only-light)
  ![Quantum vs classical exit probability](fig-separation-dark.svg#only-dark)
  <figcaption>Our simulation: the quantum walk (time ≈ 0.8·d) holds a ~0.4
  exit probability while the classical walk — given a generous d³ step
  budget — decays exponentially. At d = 20 the ratio is 638 and doubling
  every few levels.</figcaption>
</figure>

This is a real exponential, with no hardness assumption underneath it. It
deserves to be taken seriously, and §4 is what taking it seriously looks
like.

---

## 4. What it costs to keep: the fragility nobody quotes

The reduced chain is a *uniform* path only because the graph is engineered
to be perfectly symmetric. Any defect — an imperfect glue, an uneven tree, a
vertex of the wrong degree — makes the effective site energies non-uniform.
And one dimension is the worst possible place for that: disordered 1-D
chains **Anderson-localise**, meaning the eigenstates stop spanning the
system and transport dies.

<div class="qq-anim" data-anim="disorderwalk"></div>

So we measured it. Add on-site disorder of strength $W$ to the reduced
chain and take the median exit probability over realisations:

<figure markdown="span">
  ![Disorder turns polynomial decay into exponential](fig-disorder.svg#only-light)
  ![Disorder turns polynomial decay into exponential](fig-disorder-dark.svg#only-dark)
  <figcaption>Left: the clean walk loses amplitude only polynomially
  (p ~ d^-0.58, the packet spreading) while every disordered curve falls off
  a cliff. Right: the localisation length, and the depth it permits.</figcaption>
</figure>

!!! danger "The scaling is the problem, not the size of the effect"

    The numbers, from `walk_transport.py`:

    - **Clean:** exit probability falls as $d^{-0.58}$ — polynomial, and
      harmless. That decay is just the wave packet spreading over a longer
      chain.
    - **Disordered:** exponential. At $W = 2$, the exit probability falls
      from $0.11$ at $d = 16$ to $10^{-4}$ at $d = 150$
      (`test_disorder_turns_polynomial_decay_into_exponential`).
    - **And the criterion is predictive.** Measuring the localisation length
      $\xi$ on a *separate* long chain, then comparing it with the $2d+2$
      sites the algorithm must cross, tells you in advance where the
      advantage dies:

    | disorder $W$ | $\xi$ (sites) | largest usable depth $d$ |
    |---|---|---|
    | 0.5 | 253 | 125 |
    | 1.0 | 82 | 40 |
    | 2.0 | 24 | 11 |
    | 3.0 | 12 | 5 |

    Fitted, $\xi \sim W^{-1.7}$. Now read the table the uncomfortable way
    round: **to keep the advantage at depth $d$, the imperfection must
    satisfy roughly $W \lesssim (\text{const}/d)^{1/1.7}$.** The tolerable
    error shrinks as the problem grows — which is the opposite of what a
    robust advantage looks like, and the opposite of Shor, whose structure
    is arithmetic and cannot be perturbed at all.

!!! warning "What this model is, and is not"

    This is disorder added to the **effective chain**, which is the right
    model for "the reduced dynamics are not exactly uniform" — the situation
    any physical realisation faces. It is *not* a proof about arbitrary graph
    defects, and for a good reason worth knowing: perturbing the graph also
    **breaks the column-space reduction itself**, so a general defect does
    not even leave you with a $2d+2$-dimensional problem to analyse. The
    honest summary is that the clean case is the only one anybody can
    compute, and it is the only one that works.

---

## 5. Szegedy: the systematic version, and its systematic ceiling

Glued trees is a hand-built graph. Szegedy's construction is the general
machine: take **any** reversible Markov chain $P$ and quantise it into a
walk operator built from two reflections. What comes out is a clean theorem
about spectra.

<div class="qq-anim" data-anim="szegedygap"></div>

`szegedy.py` builds the walk operator explicitly, diagonalises it, and
measures the phase gap — no formula assumed. The result matches
$2\arccos(\lambda_2)$ to machine precision on every chain tested
(`test_phase_gap_is_arccos_of_the_classical_spectrum`), which for a small
classical gap $\delta$ is

$$
\text{phase gap} \;=\; 2\arccos(1-\delta) \;\approx\; 2\sqrt{2}\,\sqrt{\delta}.
$$

<figure markdown="span">
  ![Phase gap is the square root of the spectral gap](fig-szegedy.svg#only-light)
  ![Phase gap is the square root of the spectral gap](fig-szegedy-dark.svg#only-dark)
  <figcaption>Four families of chain — cycles, paths, barbells, complete
  graphs — with spectral gaps spanning a factor of 40, all on the same
  √δ line. The shaded band on the right is the entire prize.</figcaption>
</figure>

The constant $2\sqrt2$ is flat across chains whose gaps differ by orders of
magnitude (`test_the_square_root_law_is_flat_across_chains`), so this is a
law rather than a coincidence of one example. Hitting and search therefore
cost $\sim 1/\sqrt\delta$ where classical costs $\sim 1/\delta$ — the MNRS
framework behind element distinctness, triangle finding and friends.

!!! abstract "Which puts the systematic version under a familiar ceiling"

    A square root is a square root, so **every Szegedy walk inherits the
    pricing of [autopsy 06](../06-grover/notes.md)**: quadratic speedups are
    components, not products, and they need enormous instances before the
    constant factors stop deciding the race.

    Two conclusions worth separating:

    - The **exponential** (glued trees) is not of this family. It came from
      an engineered graph, not from quantising a chain — which is precisely
      why §4's fragility is the price of admission.
    - The **quadratic** (Szegedy/MNRS) is robust, general and real, and it
      is bounded above by the same wall Grover sits on.

    You can have generality or you can have an exponential. So far, nobody
    has had both.

!!! tip "Bridge to hunting ground C"

    Quantum Gibbs samplers ([autopsy 13](../12-gibbs-lindblad/notes.md))
    hunt exactly this $\sqrt{\ }$-versus-linear gap structure — but in
    *open-system* dynamics, where the target is a thermal state rather than
    a marked vertex. Same spectral instinct, harder detailed-balance
    constraints.

---

## 6. The hardness evidence, and the customer who never arrived

**Glued trees:** an unconditional exponential *query* separation. No
assumptions, no reliance on anyone failing to find a better algorithm. It is
the strongest form of evidence in this curriculum.

And it has produced nothing, for twenty years, because of the same fine
print that has run through every autopsy since the first:

!!! danger "Exponential speedup, no customer"

    The separation is about an **oracle**. You are handed a graph whose
    vertices have meaningless random names, and the theorem says you cannot
    find the exit by asking about names. Give the vertices *structured*
    names — anything that reveals which column you are in — and the problem
    is trivial classically.

    So the entire separation lives in the name-hiding, and instantiating it
    means finding a real function that (i) is efficiently computable, (ii)
    has the glued-trees adjacency structure, and (iii) hides the column
    index from every classical algorithm. Compare $a^x \bmod N$, which does
    all three for Shor and is the reason autopsy 04 is about factoring
    rather than about periodic oracles.

    Nobody has found one. It is the mirror image of Deutsch–Jozsa's problem
    from [autopsy 01](../01-deutsch-jozsa/notes.md): there the mechanism was
    right and the problem was fake; here the mechanism *and* the separation
    are right, and the problem is missing entirely.

---

## 7. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    Argue with the draft, then replace it.

    <div class="qq-lesson" markdown>

    The glued-trees speedup needed a graph **engineered** so that classical
    drift fails exactly where quantum dispersion sails. That is a strong hint
    about where walk advantages live "in nature": nowhere, unless something
    else is enforcing the symmetry. §4 makes the hint quantitative — the
    advantage survives only while the effective chain stays clean over its
    whole length, and the length *is* the problem size.

    Meanwhile $\sqrt{\text{gap}}$ caps everything systematic at quadratic,
    because quantising a chain can only convert eigenvalues to eigenphases,
    and $\arccos$ near 1 is a square root. An exponential walk advantage
    therefore seems to need a structural extra that no quantisation supplies:
    in the one example we have, it is a graph whose classical dynamics are
    actively **anti**-helpful while its spectrum is a clean band.

    The transferable rule: **an unconditional separation is worth more than a
    conditional one, and worth nothing without an instantiation.** Glued
    trees has the best evidence in this curriculum and the worst customer
    list.

    </div>

Questions worth answering in your own words:

- §4 says the tolerable imperfection shrinks with problem size. Which other
  advantage in this curriculum has that property, and which are immune?
- If you had to bet on one *structural extra* that could carry an exponential
  walk advantage into a real problem, what would it be — and what would you
  compute first to kill your own bet?
- Does the disorder critique apply to Szegedy walks too, or does the
  quadratic survive where the exponential does not? (Careful: what exactly is
  being perturbed in each case?)

---

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/07-quantum-walks/glued_trees.py     # §3
    .venv/bin/python predecessors/07-quantum-walks/walk_transport.py  # §2, §4
    .venv/bin/python predecessors/07-quantum-walks/szegedy.py         # §5
    .venv/bin/pytest predecessors/07-quantum-walks -q                 # 34 tests
    ```

- [ ] Derive the reduced path weights ($\sqrt 2$ inside the trees, $2$ at the
      glue) from the column-state normalisation
      $|{\rm col}_j\rangle = \frac{1}{\sqrt{N_j}}\sum_{v \in {\rm col}_j}|v\rangle$
      — five lines.
- [ ] Explain the classical column chain's $2/3$-versus-$1/3$ bias from
      vertex degrees, and why making the exit absorbing only *helps* the
      classical side (so our comparison is fair).
- [ ] One paragraph: why is the glued-trees oracle hard to instantiate? What
      would a real function have to hide — and compare with $a^x \bmod N$.
- [ ] **New.** In `walk_transport.py`, put the disorder in the *hoppings*
      rather than the site energies. Does the localisation length behave the
      same way? Which is the better model for a graph defect, and why?
- [ ] **New.** §5 shows the phase gap is $2\arccos(\lambda_2)$. Take a chain
      whose second eigenvalue is *negative* and large in magnitude — what
      does the formula give, and why does making the chain lazy fix it? (The
      `lazy()` helper exists for exactly this reason; find out what it is
      hiding.)
- [ ] **The uncomfortable one.** §6 says the separation lives entirely in the
      name-hiding. Write down the most plausible candidate instantiation you
      can think of, then spend twenty minutes trying to solve *your own*
      candidate classically. Record what broke.
