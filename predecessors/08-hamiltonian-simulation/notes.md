# Autopsy 09 — Hamiltonian simulation: Trotter → LCU → qubitization

*Feynman's original problem — the reason quantum computing exists, and the
only autopsy in this curriculum whose subject is winning.*

!!! tip "How to read this page"

    Every autopsy so far has hunted for the weak baseline. This one cannot:
    the hardness has a mechanism, the customers are real, and the classical
    attack has been tried hard and mostly failed. So the discipline runs the
    other way round. Instead of asking *is this advantage real?*, the useful
    questions are **which instances**, and **which method** — because on this
    page the over-claiming takes the form of "quantum computers will do
    chemistry", not "quantum beats a strawman".

    Both questions are answered with numbers here, from
    [`entanglement_wall.py`](entanglement_wall.py) and
    [`simulation_cost.py`](simulation_cost.py), pinned by 23 tests. One of
    the answers contradicts the folklore, including the folklore in the
    earlier version of this page.

    Two sentences to carry:

    > **The classical wall is a wall for dynamics, and only for dynamics.**
    > Two thirds of "classical methods fail" is false.
    >
    > **Asymptotically optimal is not the same as cheaper**, and the number
    > that decides it is α over the commutator norm.

---

## 1. The problem, and the customer

Given a local Hamiltonian $H$ and a time $t$, apply $e^{-iHt}$. Feynman
proposed it in 1982 as the founding use case, and unlike every other problem
in this curriculum it arrived with a customer base already in place:
chemistry, materials, nuclear and lattice physics.

It also has the strongest hardness footing available: simulating
local-Hamiltonian dynamics to $1/\mathrm{poly}$ precision is
**BQP-complete**. A generic dequantisation would collapse BQP to BPP, so
there is no Tang-style result waiting to happen (compare
[autopsy 11](../10-hhl-tang/notes.md)).

---

## 2. The classical wall — and exactly where it is not

The stub version of this page listed three classical methods and the
mechanism by which each fails. That table is correct but it invites a wrong
conclusion, so here is the measurement.

<div class="qq-anim" data-anim="entwall"></div>

A matrix-product state stores a wavefunction in **bond dimension** $\chi$,
and it needs $\chi \approx 2^{S}$ where $S$ is the entanglement entropy
across a cut. So the classical cost is decided entirely by how $S$ behaves —
and it behaves in three completely different ways:

<figure markdown="span">
  ![Three regimes: area law, critical, and the quench](fig-wall.svg#only-light)
  ![Three regimes: area law, critical, and the quench](fig-wall-dark.svg#only-dark)
  <figcaption>Measured on a transverse-field Ising chain by
  <code>entanglement_wall.py</code> — exact diagonalisation, entropy from the
  Schmidt values, no approximation.</figcaption>
</figure>

| regime | how $S$ grows | bond dimension | classically |
|---|---|---|---|
| **gapped ground state** | flat in $n$ — the *area law* | constant | easy; DMRG since 1992 |
| **critical ground state** | $\sim \tfrac{c}{6}\log_2 n$ | polynomial | harder, not hard |
| **quench dynamics** | **linear in $t$** | $2^{\Theta(t)}$ | **the wall** |

The measured numbers: the gapped chain's entropy is flat to $4\times10^{-4}$
per doubling; the critical chain fits a slope of $0.097$ against the Ising
CFT's $c/6 = 0.083$; and the quench accumulates $0.94$ bits per unit time
(`test_gapped_ground_states_obey_an_area_law`,
`test_the_critical_point_is_logarithmic_and_matches_the_cft`,
`test_entropy_grows_linearly_under_a_quench`).

!!! danger "The honest form of “classical methods fail”"

    Only the third row is a wall — and it is a magnificent one: **doubling
    the simulated time squares the memory.** But a claim of quantum
    advantage in simulation that does not say which of those three regimes
    its instances live in has not begun to make an argument.

    "Quantum computers are needed for chemistry" is, as usually stated,
    false for a large fraction of chemistry. The advantage lives in
    **dynamics** and in **strongly correlated** ground states, not in the
    word chemistry.

---

## 3. Trotter: the error is a commutator

Slice time; the error is commutator-sized:

$$
\Big\| e^{-i(A+B)t} - \big(e^{-iAt/r}\,e^{-iBt/r}\big)^r \Big\|
\;\le\; \frac{t^2\,\|[A,B]\|}{2r} ,
$$

and the symmetric (Strang) splitting cancels the first commutator term,
giving $O(t^3/r^2)$.

<div class="qq-anim" data-anim="trotterslice"></div>

<figure markdown="span">
  ![Measured Trotter error slopes](fig-slopes.svg#only-light)
  ![Measured Trotter error slopes](fig-slopes-dark.svg#only-dark)
  <figcaption>Measured on a 6-qubit transverse-field Ising chain: fitted
  slopes −1.0 and −2.0, exactly the commutator bounds.</figcaption>
</figure>

Two measurements that decide how good Trotter really is, both from
`simulation_cost.py`:

- **The commutator is the right quantity, and it is much smaller.** The
  textbook charges $\|A\|\,\|B\|$, which grows as $n^{2.2}$ on this chain;
  the real $\|[A,B]\|$ grows as $n^{1.0}$, because a local chain's
  commutator is a sum of local pieces
  (`test_the_two_bounds_scale_differently`). This is the Childs–Su insight
  that changed the picture.
- **And Trotter beats even that bound**, by a factor of $3.1$ that is stable
  across step counts and system sizes
  (`test_trotter_beats_its_own_bound_by_a_stable_factor`) — so every
  crossover below moves in Trotter's favour by $3.1^{1/2k}$.

---

## 4. LCU and qubitization, in a paragraph each

**LCU** (Berry–Childs–Cleve–Kothari–Somma). Write the evolution as a Linear
Combination of Unitaries and implement it with ancillas plus amplitude
amplification — the first exponential improvement in the $1/\varepsilon$
dependence.

**Qubitization** (Low–Chuang). Block-encode $H/\alpha$ in a unitary; the walk
operator rotates each eigenspace by $\arccos(\lambda)$ — the same $\arccos$
that appeared in [Szegedy's walks](../07-quantum-walks/notes.md) — achieving
the optimal $O\big(\alpha t + \log(1/\varepsilon)\big)$.

Note what $\alpha$ is: the sum of the absolute values of $H$'s coefficients,
i.e. how much of the block-encoding's budget $H$ occupies. It is paid
**linearly**, it grows with the system, and the optimality theorem says
nothing about it.

---

## 5. So which one is actually cheaper?

This is the live fight in applied work, and the received answer — *Trotter
wins at chemically relevant precision on local Hamiltonians* — does not
survive being computed.

<div class="qq-anim" data-anim="simcost"></div>

<figure markdown="span">
  ![Trotter against qubitization, and the knob between them](fig-crossover.svg#only-light)
  ![Trotter against qubitization, and the knob between them](fig-crossover-dark.svg#only-dark)
  <figcaption>Both costs in term-applications, with the qubitization side
  charged generously. The model is written out in the module docstring so it
  can be argued with.</figcaption>
</figure>

!!! warning "What the computation says, including against the earlier draft of this page"

    On a plain nearest-neighbour Ising chain, **qubitization wins at every
    precision finer than $\varepsilon \approx 4\times10^{-2}$** — including
    every precision anyone would call chemically relevant
    (`test_the_folklore_fails_on_a_plain_local_chain`). The folklore is
    wrong here, and the reason is that this Hamiltonian has a *small* α.

    The knob that actually decides it is
    $\alpha / \|[A,B]\|$ — how much of the Hamiltonian's weight sits in a
    block that commutes with itself. Qubitization pays α linearly; Trotter
    pays only a $2k$-th root of the commutator. Tune them apart and the
    winner flips:

    | Hamiltonian | $\alpha/\|[A,B]\|$ | crossover $\varepsilon$ |
    |---|---|---|
    | nearest-neighbour Ising | 0.79 | $4.5\times10^{-2}$ |
    | long-range Ising, $g=1$ | 0.75 | $1.5\times10^{-2}$ |
    | long-range Ising, $g=0.01$ | 47.7 | $7.7\times10^{-4}$ |

    Within the long-range family, a 64-fold rise in the ratio widens
    Trotter's window by a factor of 19
    (`test_the_ratio_moves_the_crossover`). Real chemistry Hamiltonians
    *are* that shape — a large commuting Coulomb part plus a smaller kinetic
    one — which is why the folklore exists. **But the shape is the reason,
    not the word "chemistry"**, and the shape is a number you can compute
    before choosing a method.

    Also measured: the best *order* rises as precision tightens
    (`test_the_best_order_rises_as_precision_tightens`). Comparing
    second-order Trotter against qubitization, as many papers do, is
    comparing the wrong product formula.

!!! abstract "The rule this yields"

    A simulation resource estimate that does not report **α** and the
    **commutator norm** has not made an argument — it has picked a method
    and priced it. Both numbers are cheap to compute for any Hamiltonian you
    can write down, and together they predict the winner without running
    anything.

---

## 6. The hardness evidence, and its fine print

BQP-completeness is the strongest footing in this curriculum. It is also
**worst-case**, and that gap is where the whole argument lives:

!!! warning "Worst-case hardness, instance-wise reality"

    The instances chemists care about may still be classically easy — and
    tensor-network people keep proving that some are. §2 is the same point
    from the other side: two of the three regimes are comfortably classical.

    The advantage frontier in simulation is therefore **instance-wise**,
    which is exactly the situation in which baseline discipline decides
    everything. Per this repository's 2026
    [frontier sweep](../../frontier/lit-sweep-2026H1.md), simulation is the
    only bucket of *empirical* advantage claims that survived contact with
    classical algorithms at all — and the survivors are specific instances,
    not a field.

---

## 7. What makes this autopsy different

Every other mechanism in this curriculum can be attacked at its input. The
Fourier family needs an oracle that can be instantiated; HHL needs a state
you can prepare; Grover needs a haystack you can compute. Tang's technique
([autopsy 11](../10-hhl-tang/notes.md)) works precisely by giving the
classical algorithm the same access the quantum one assumed.

Hamiltonian simulation has **quantum-native input**. The problem is *about* a
quantum object: you are handed a Hamiltonian — a short classical description
— and asked for a property of its evolution. There is no access model to
level, so no dequantisation of that shape can even be formulated.

That immunity is real, and it is the single most valuable structural
property on this page. But be precise about what it buys: it protects the
*model*, not the *instances*. §2 and §5 are both about instances, and both
found the honest answer to be narrower than the slogan.

---

## 8. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    Argue with the draft, then replace it.

    <div class="qq-lesson" markdown>

    **Quantum-native input is the most durable structural property in this
    curriculum.** When the problem is about a quantum object, the
    access-model attack that killed HHL cannot be posed. Any hunting ground
    that inherits this — anything whose input is a Hamiltonian, a channel or
    a state rather than a data set — starts with that immunity, and it is
    worth more than any speedup exponent.

    But immunity at the input does not settle the instance question, and §2
    shows the instance question has a computable answer: **entanglement
    growth is the discriminator**. Flat means classical, logarithmic means
    classical-with-effort, linear-in-time means quantum. That is a test
    anyone can run on a candidate before writing a proposal.

    And §5 is the methodological lesson: *asymptotically optimal* is a
    statement about limits, not about your instance. The optimal algorithm
    lost here whenever the Hamiltonian's weight sat in a commuting block —
    a property invisible to the complexity statement and obvious to a
    two-line computation.

    </div>

Questions worth answering in your own words:

- Which of our hunting grounds inherits the quantum-native-input immunity,
  and which only appear to?
- §5 gives a two-number test (α, commutator norm) for choosing a method.
  What is the equivalent two-number test for deciding whether an *instance*
  is worth a quantum computer at all?
- The sign problem kills quantum Monte Carlo. Why does it have no analogue
  for a quantum computer running the same instance — and what *is* the
  quantum computer's version of the same difficulty?

---

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/08-hamiltonian-simulation/trotter.py            # §3
    .venv/bin/python predecessors/08-hamiltonian-simulation/entanglement_wall.py  # §2
    .venv/bin/python predecessors/08-hamiltonian-simulation/simulation_cost.py    # §5
    .venv/bin/pytest predecessors/08-hamiltonian-simulation -q                    # 23 tests
    ```

- [ ] Prove the first-order bound above (BCH truncation + telescoping;
      sketch in `curriculum/solutions.md`).
- [ ] The Strang splitting kills which BCH term, exactly?
- [ ] One paragraph: why does the sign problem (QMC's killer) have no
      analogue for a quantum computer running the same instance?
- [ ] **New.** §2 measures entanglement growth at the critical point
      ($g = 1$). Run `quench` at $g = 0.5$ and $g = 3$. Does the growth rate
      change? Predict the direction *before* running it, from what the gap
      does to the propagation velocity.
- [ ] **New.** §3 finds the commutator bound loose by a stable $3.1\times$.
      Is that constant universal, or a property of this Hamiltonian? Measure
      it for the long-range model in `simulation_cost.py` and say what would
      have to be true for it to be universal.
- [ ] **The uncomfortable one.** §5 contradicts a widely repeated claim.
      Before believing this page, reconstruct the cost model yourself from
      the docstring, pick your own Hamiltonian, and check whether the
      crossover lands where we say. If it does not, the disagreement is
      worth more than the agreement — write down which assumption differs.
