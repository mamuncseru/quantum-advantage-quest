# Autopsy 13 — Quantum Gibbs sampling: Metropolis → Davies → CKG

*Hunting ground C. Classical MCMC's quantum sibling, forty years late.*

!!! info "Read with the frontier file open"

    2026 state: [the literature sweep](../../frontier/lit-sweep-2026H1.md).
    Verify at proof level: Chen–Kastoryano–Gilyén (arXiv 2311.09207, lineage
    published Nature 646, 561), Rajakumar–Watson (2408.01516, Quantum 2026),
    Bakshi–Tan (per sweep).

    This page's three headline quantities — the gap, the sign problem, the
    thermal entanglement — are computed by [`gibbs_gap.py`](gibbs_gap.py),
    and the ground's template result is **executed** in
    [`dequantizer_window.py`](dequantizer_window.py). 26 tests.

    One of those computations corrects a reading almost everyone carries,
    including the earlier version of this page: **non-commuting does not
    mean signful**, and the Hamiltonian our own demo uses turns out not to
    be hard for Monte Carlo at all. §3.

---

## 1. The problem

Prepare (sample from) the Gibbs state

$$
\rho_\beta = \frac{e^{-\beta H}}{\mathrm{Tr}\, e^{-\beta H}}
$$

of a local quantum Hamiltonian. The customer: all of equilibrium physics and
chemistry, plus Gibbs states as the engine of optimisation and of ML
(Boltzmann machines). Classical MCMC is arguably the most-used algorithm
family in science — this ground hunts its quantum counterpart.

---

## 2. The primitive — three generations, and why it took forty years

<div class="qq-anim" data-anim="detbalance"></div>

Classical Metropolis needs only detailed balance and ergodicity. Both are
easy when a state is a list of numbers you may inspect — and *inspecting* is
exactly what quantum mechanics charges for.

**1 · Davies generator** (1970s, weak-coupling limit). Split each coupling
$A$ into Bohr-frequency components

$$
A(\omega) = \sum_{E_k - E_j = \omega} |j\rangle\langle j|\, A\, |k\rangle\langle k| ,
$$

give each the Glauber rate $\gamma(\omega) = (1 + e^{-\beta\omega})^{-1}$,
which satisfies the KMS condition $\gamma(\omega) = e^{\beta\omega}\gamma(-\omega)$,
and form the Lindbladian

$$
\mathcal{L}(\rho) = \sum_\omega \gamma(\omega)
\Big( A(\omega)\,\rho\, A(\omega)^\dagger
- \tfrac12\big\{ A(\omega)^\dagger A(\omega),\, \rho \big\} \Big).
$$

It fixes $\rho_\beta$ **exactly**. [`davies.py`](davies.py) verifies
stationarity to $10^{-16}$:

<figure markdown="span">
  ![Convergence of the Davies sampler](fig-convergence.svg#only-light)
  ![Convergence of the Davies sampler](fig-convergence-dark.svg#only-dark)
  <figcaption>Three very different initial states, one destination: the
  Davies Lindbladian pulls everything to e^(−βH)/Z at a rate set by its
  spectral gap.</figcaption>
</figure>

Its fatal flaw at scale: $A(\omega)$ requires *exactly* resolving all Bohr
frequencies — an oracle, not an algorithm.

**2 · Quantum Metropolis** (Temme et al. 2011). Phase-estimate energies,
accept/reject. Obstruction: measuring energy destroys the coherences, and
rewinding rejected moves is awkward and approximate.

**3 · CKG samplers** (2023 →). Gaussian-filtered jump operators — finite
energy resolution, implementable at Hamiltonian-simulation cost — **plus an
explicitly constructed coherent correction term** that restores exact
quantum detailed balance for arbitrary non-commuting $H$. Efficient
Lindbladian, exact fixed point. Mixing time: **not guaranteed** — and that
is precisely where the science now lives.

---

## 3. The two classical walls, priced

The autopsy's claim is that the sign problem blocks Monte Carlo and
entanglement blocks tensor networks. Both are measurable, and one of them
produces a surprise.

<div class="qq-anim" data-anim="signcost"></div>

<figure markdown="span">
  ![The gap and the two classical walls](fig-walls.svg#only-light)
  ![The gap and the two classical walls](fig-walls-dark.svg#only-dark)
  <figcaption>Left: the quantum cost. Middle: the average sign
  ⟨s⟩ = Z/Z_abs, whose square inverse is Monte Carlo's overhead. Right: the
  thermal mutual information a tensor network must carry.</figcaption>
</figure>

!!! danger "The correction: non-commuting does not mean signful"

    Monte Carlo's overhead is $1/\langle s\rangle^2$ where
    $\langle s \rangle = Z/Z_{\text{abs}}$, and it is computable exactly at
    these sizes. The measurement:

    | model | ⟨s⟩ at β = 1 | at β = 2 | at β = 4 |
    |---|---|---|---|
    | transverse Ising (stoquastic) | 1.00000 | 1.00000 | 1.00000 |
    | **Heisenberg chain + fields** | **1.00000** | **1.00000** | **1.00000** |
    | triangle AFM (frustrated) | 0.26991 | 0.03663 | 0.00067 |
    | all-pairs AFM, n = 4 | 0.03821 | 0.00067 | ~0 |

    The second row is the Hamiltonian [`davies.py`](davies.py) demonstrates
    on. It is thoroughly non-commuting, it is *not* stoquastic in the
    computational basis — and its average sign is exactly 1, because a chain
    is **bipartite** and the Marshall sign rule gauges the problem away
    (`test_a_bipartite_chain_has_no_sign_problem`).

    So our own demo instance is a witness for the **mechanism** and not for
    the **hardness**: Monte Carlo handles it comfortably. What creates a
    sign problem is *frustration* — close the chain into an odd cycle and
    the sign decays exponentially, reaching a $2\times10^6$ overhead by
    $\beta = 4$ (`test_frustration_is_what_creates_the_sign_problem`).

    Worth carrying into the hunt: "non-commuting" is not a hardness
    argument, and a demo Hamiltonian is not an instance family.

The second wall is gentler than it sounds too. The thermal mutual
information is near zero at high temperature — which is exactly why the
provably-easy atlas covers that regime — and grows as the state cools. The
advantage has to live in between: **cold enough that correlations are real,
warm enough that the Lindbladian still mixes.**

---

## 4. The gap is the cost, and cooling is what costs

The quantum side's runtime is $1/\text{gap}$, so the frontier question is
not "is there a gap" — [`davies.py`](davies.py) already shows one — but how
it behaves. Measured on the 3-site chain: gap $1.71 \to 1.00$ as $\beta$
goes $0.25 \to 4$, i.e. the sampler slows as it cools, the same story
classical MCMC tells (`test_cooling_costs_mixing_time`).

!!! warning "And that is all exact diagonalisation can say"

    Three sites is not an asymptotic statement. **Proving the gap stays open
    for large $n$ is the entire remaining frontier of this ground**, and
    nothing on this page substitutes for that theorem. Everything computed
    here characterises the *shape* of the question, not its answer.

---

## 5. The recipe, executed

The sweep calls Bakshi–Tan "the template result … executed exactly once in
the literature. Repeatable by construction." A template nobody has re-run is
a claim, so [`dequantizer_window.py`](dequantizer_window.py) re-runs one.

<div class="qq-anim" data-anim="gibbswin"></div>

The recipe as a procedure: take a family with a knob, measure what the
classical methods pay as it turns, measure whether the Lindbladian still
mixes, and look for a window where the first blows up and the second does
not. The knob used here is **frustration** — the smallest honest one, since
it moves the sign structure while leaving locality and norm alone.

| λ | ‖H‖ | ⟨sign⟩ | QMC overhead | Davies gap | mixing time |
|---|---|---|---|---|---|
| 0.00 | 4.03 | 1.00000 | ×1 | 1.0001 | 6.91 |
| 0.50 | 3.53 | 0.08279 | ×146 | 1.0037 | 6.88 |
| 1.00 | 3.22 | 0.00500 | **×39,939** | **1.1800** | **5.85** |

<figure markdown="span">
  ![The window: classical cost up, mixing time flat](fig-window.svg#only-light)
  ![The window: classical cost up, mixing time flat](fig-window-dark.svg#only-dark)
  <figcaption>The classical cost climbs four orders of magnitude across the
  knob while the mixing time does not degrade — it slightly improves. Right:
  the window in (λ, β).</figcaption>
</figure>

!!! success "Both halves, and neither alone"

    The classical cost rises **40,000×** while the mixing time *falls* and
    the operator norm barely moves
    (`test_the_knob_breaks_the_dequantizer_and_keeps_the_mixer`). That is
    the conjunction, and it is what "break the dequantizer, keep the mixer"
    means operationally.

    Neither condition alone is worth anything, and the code enforces that:
    a hard instance where the sampler also stalls is just a hard instance,
    and a fast sampler on an easy instance is a demo
    (`test_both_axes_matter`).

    **What this does not establish**: three sites is not asymptotics, the
    QMC overhead is a proxy for one classical method rather than all of
    them, and at $n = 3$ the gap never closes — so the window's boundary
    here is set entirely by the classical side. The useful output is the
    **shape**: a candidate for this ground must move a classical cost by
    orders of magnitude while leaving the mixing time flat, and *both*
    halves must be measured before either is claimed.

---

## 6. The hardness evidence — the 2026 ledger

- Constant-$T$ sampling hardness for $O(1)$-local $H$: Rajakumar–Watson —
  the ground's anchor theorem (conditional, standard assumptions).
- **Bakshi–Tan (Apr 2026), the template result:** strong on-site fields
  break the best classical dequantizer (the high-temperature
  counting-to-sampling method) while the quantum Lindbladian still mixes
  rapidly. §5 re-runs the *shape* of that argument on a computable family.
- No unconditional quantum-vs-classical mixing-time separation yet. Open.

!!! tip "Structural immunity worth pinning"

    The input here is a **Hamiltonian**, not a data matrix — there is no
    $\ell^2$-sampling access model to hide behind, so Tang-style
    dequantisation ([autopsy 11](../10-hhl-tang/notes.md)) cannot even be
    *formulated*. Advantage claims on this ground die or survive on physics,
    not on access-model bookkeeping.

    That is the same quantum-native-input property
    [autopsy 09 §7](../08-hamiltonian-simulation/notes.md) identifies, and
    across thirteen autopsies it is the most durable structural asset any
    ground has.

---

## 7. The lesson — YOUR TURN

!!! abstract "Write this section yourself"

    Argue with the draft, then replace it.

    <div class="qq-lesson" markdown>

    **The quantum obstruction was measurement.** Classical Metropolis
    inspects a state and decides; quantum mechanically that inspection
    destroys the object being sampled. Davies avoided it by working in the
    exact energy eigenbasis — an oracle. Quantum Metropolis paid for it with
    approximate rewinding. CKG paid for it with a **coherent correction
    term**, buying exact detailed balance at finite energy resolution: an
    efficient generator with an exact fixed point, and no mixing-time
    guarantee at all. Forty years to arrive at "the fixed point is right,
    the rate is open".

    "Prove the gap" is the entire remaining frontier because everything else
    is settled: the generator is efficient, the fixed point is exact, the
    input is quantum-native and so immune to access-model attacks. The one
    unknown is the rate — and §4 shows even a 3-site chain slows as it
    cools.

    Bakshi–Tan as a recipe: (1) pick a family with a knob that moves the
    classical cost, (2) verify the knob does not change locality or norm,
    (3) measure the classical proxy *and* the mixing time across it, (4)
    claim only the conjunction. §5 is that recipe executed with frustration
    as the knob. The knob I would turn next is a **weak non-commuting
    perturbation of a classically-hard commuting model** — it inherits the
    hardness from the commuting limit while the perturbation is small enough
    that a mixing-time proof might still be reachable, which is the pairing
    every other knob fails.

    </div>

Questions worth answering in your own words:

- Which quantum obstruction made "just do Metropolis" take forty years, and
  what did CKG actually pay to fix it?
- §3 shows our own demo Hamiltonian has no sign problem. What *is* the
  smallest instance family that is simultaneously frustrated, local, and
  large enough to matter?
- Name the knob you would turn next, with a mechanism argument — and say in
  advance which of §5's two halves you expect to be the hard one.

---

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/12-gibbs-lindblad/metropolis.py
    .venv/bin/python predecessors/12-gibbs-lindblad/davies.py
    .venv/bin/python predecessors/12-gibbs-lindblad/gibbs_gap.py           # §3-§4
    .venv/bin/python predecessors/12-gibbs-lindblad/dequantizer_window.py  # §5
    .venv/bin/pytest predecessors/12-gibbs-lindblad -q                     # 26 tests
    ```

- [ ] Verify the KMS ratio for the Glauber choice — two lines of algebra.
- [ ] Prove Gibbs stationarity of the Davies generator: show each
      $\omega$-term of $\mathcal{L}$ annihilates $\rho_\beta$, using
      $A(\omega)\,\rho_\beta = e^{\beta\omega}\rho_\beta\, A(\omega)$
      (~10 lines; the code verifies it numerically — your proof explains why).
- [ ] Classical side: what is the known mixing time of 1D Ising Metropolis at
      $\beta = 0.7$ (order of magnitude, with citation)?
- [ ] **The hunt-phase question** (one page): write the Bakshi–Tan recipe as
      a checklist — dequantizer to break, mixer to preserve, hardness to
      inherit — then propose ONE candidate knob with a mechanism argument.
      Hold it against §5's table.
- [ ] **New.** §3 found the Heisenberg chain sign-free by the Marshall rule.
      Work out *which* basis change does it, and then determine whether the
      random $z$-fields in `heisenberg_with_fields` preserve the property.
      (The measurement says yes — your job is to say why.)
- [ ] **The uncomfortable one.** §5's window is bounded entirely by the
      classical side because the gap never closes at $n = 3$. Push
      `dequantizer_window.py` to $n = 4$ and $n = 5$ and see whether that
      remains true. If the gap starts closing with $n$, the window is a
      finite-size artefact — and you will have learned more from breaking
      the result than from quoting it.
