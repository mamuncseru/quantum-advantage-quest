# Autopsy 12 — Decoded Quantum Interferometry (Jordan–Shutty et al. 2024)

*Hunting ground A. The newest genuine algorithmic idea in a decade.*

!!! info "Read with the frontier file open"

    The 2026 state of this ground — what got killed, what stands — lives in
    [the literature sweep](../../frontier/lit-sweep-2026H1.md). Primary
    source: arXiv 2408.08292. Per our rules nothing enters the hunt
    unverified, so the mechanism on this page is **computed** rather than
    quoted: [`dqi_spectrum.py`](dqi_spectrum.py) and
    [`prange_baseline.py`](prange_baseline.py), pinned by 28 tests.

    The sentence to carry, and it is the reason this ground is worth
    hunting on:

    > **DQI's fate is decided in coding theory, not in quantum mechanics.**
    > The decoder sets the degree, the degree sets the objective, and the
    > quantum machine only supplies the interference.

---

## 1. The problem

**max-LinSAT**: satisfy as many linear constraints over a finite field as
possible. Two key cases:

- **max-XORSAT**: equations $a_i \cdot x = b_i$ over $\mathbb{F}_2$;
- **OPI (Optimal Polynomial Intersection)**: find a degree $< k$ polynomial
  $Q$ over $\mathbb{F}_p$ maximising the number of points $i$ where $Q(y_i)$
  lands in a prescribed set $F_i$. Equivalently *noisy polynomial
  reconstruction* — a problem with a real cryptographic pedigree
  (Reed–Solomon list decoding, Naor–Pinkas oblivious polynomial evaluation).

---

## 2. The reduction: optimisation becomes decoding

<div class="qq-anim" data-anim="dqichain"></div>

Four links, and only the third is quantum. Take max-XORSAT and write the
objective as a sign function:

$$
s(x) \;=\; 2f(x) - m \;=\; \sum_{i=1}^{m} (-1)^{\,b_i + a_i \cdot x} .
$$

That is a sum of $m$ characters, so **the objective is already
Fourier-sparse**, supported on the constraint vectors themselves
(`test_the_objective_is_fourier_sparse`). Raise it to a power and the
characters multiply: a degree-$\ell$ polynomial of $s$ has all its Fourier
weight on XOR-combinations of at most $\ell$ constraint vectors — the
**low-weight words of the code the constraints generate**.

<figure markdown="span">
  ![The spectrum lands on low-weight codewords](fig-reduction.svg#only-light)
  ![The spectrum lands on low-weight codewords](fig-reduction-dark.svg#only-dark)
  <figcaption>Every nonzero Fourier coefficient of s^ℓ sits on a reachable
  frequency — <strong>zero</strong> outside, verified by direct transform on
  a 10-variable instance rather than re-derived.</figcaption>
</figure>

So DQI prepares $\sum_x P(f(x))|x\rangle$ by building the state on the
Fourier side — a superposition of weight-$\le\ell$ error patterns — and
uncomputing the pattern from its syndrome. That uncomputation *is* syndrome
decoding.

!!! abstract "The architecture, for the catalog"

    **optimisation → coding theory → borrow the decoder.**

    Where Shor turned factoring into Fourier sampling, DQI turns
    optimisation into decoding, and a sixty-year-old classical toolbox
    becomes a quantum resource. **Decoding radius $\ell$ buys polynomial
    degree $\ell$** — that exchange rate is the whole algorithm.

---

## 3. What the radius buys, exactly

Restrict the state to error patterns of weight $\le \ell$ and the expected
objective becomes a quadratic form in the amplitudes $w_k$. Because $s$
moves weight by exactly one, the form is **tridiagonal** with couplings
$\sqrt{(k+1)(m-k)}$ — so the best achievable objective is an eigenvalue, and
no asymptotics are needed to compute it
(`test_the_form_is_tridiagonal_with_the_stated_couplings`).

<div class="qq-anim" data-anim="semicircle"></div>

That eigenvalue converges to the paper's **semicircle law**:

$$
\text{satisfied fraction} \;\longrightarrow\; \tfrac12 + \sqrt{d(1-d)},
\qquad d = \ell/m .
$$

Checked the only honest way — the gap must *shrink with $m$*, and it does:
$0.062 \to 0.036 \to 0.016 \to 0.006$ for $m = 50, 100, 400, 1600$ at
$d = 0.25$ (`test_the_semicircle_is_the_large_m_limit`).

!!! warning "Where the model stops being about anything"

    The tridiagonal reduction treats the weight-$k$ subspaces as
    orthogonal, which holds below the code's distance. Push $d$ past $1/2$
    and its eigenvalue drifts toward $m$, which would say "unlimited
    decoding radius solves the problem exactly". It does not — that is the
    model leaving its regime, and `test_the_model_is_only_trusted_below_half`
    pins the boundary so nobody quotes the number beyond it.

    Everything below stays at $d \le 1/2$, where the semicircle peaks.

---

## 4. The baseline it has to beat

The classical attack is **Prange's information-set decoding**: pick $n$ of
the $m$ constraints, solve them exactly over $\mathbb{F}_2$, and take the
rest at chance. That gives $\tfrac12 + n/2m$, and repeating it and keeping
the best adds a finite-size bonus that vanishes like $1/\sqrt m$
(measured: $0.083 \to 0.044$ as $m$ goes $32 \to 256$,
`test_the_finite_size_bonus_shrinks_with_m`).

Now the head-to-head, which is the only number that matters:

| classical attacker | Prange fraction | radius $\ell$ DQI needs | $d = \ell/m$ |
|---|---|---|---|
| $n = 10$, $m = 100$ | 0.550 | 2 | 0.020 |
| $n = 40$, $m = 100$ | 0.700 | 7 | 0.070 |
| $n = 60$, $m = 100$ | 0.800 | 14 | 0.140 |
| $n = 80$, $m = 100$ | 0.900 | 26 | 0.260 |

!!! success "Read the third column as a specification"

    DQI's advantage is **not** "quantum beats classical". It is *"a decoder
    that reaches radius $\ell$ beats an attacker who solves $n$ equations
    exactly"* — and as the attacker gets stronger the required decoder gets
    deeper (`test_harder_baselines_demand_bigger_radii`).

    If no efficient decoder reaches that radius, there is no advantage,
    whatever the quantum machine does. The quantum contribution is real but
    it is *interference*; the decoder decides whether there is anything to
    interfere toward.

    (These radii are lower bounds: they use the asymptotic Prange line, and
    finite-size Prange is stronger.)

---

## 5. The 2026 ledger — and why it reads the way it does

<div class="qq-anim" data-anim="codereach"></div>

| Regime | Status (July 2026) |
|---|---|
| random / sparse max-k-XORSAT | :material-close: **killed** — OGP/AMP obstructions; tight inapproximability; enhanced Prange matched even genuinely quantum LDPC decoders (the DQI team's own negative result, Apr 2026) |
| **OPI over $\mathbb{F}_p$ (Reed–Solomon)** | :material-check: **standing** — explicit searches found no classical attack; best classical remains Prange-type |
| Hermitian / AG-code OPI | :material-check: standing, younger, less attacked |
| rank-metric (Gabidulin) variants | :material-check: standing — classical side un-stress-tested (June 2026) |
| HDQI: Gibbs sampling via decoding | :material-help: open — the bridge to ground C |

<figure markdown="span">
  ![The law, the baseline, and which codes reach far enough](fig-semicircle.svg#only-light)
  ![The law, the baseline, and which codes reach far enough](fig-semicircle-dark.svg#only-dark)
  <figcaption>Left: the exact eigenvalue converging to the semicircle.
  Middle: the radius each classical baseline forces. Right: which codes have
  a decoder that gets there.</figcaption>
</figure>

!!! danger "The mechanism behind “structure survived, randomness fell”"

    It is one line of coding theory, and §4 turns it into arithmetic.

    - **Reed–Solomon** has efficient decoders reaching a *constant fraction*
      of the constraints — $(m-k)/2$ for unique decoding, $m - \sqrt{mk}$
      for Guruswami–Sudan list decoding. At $m = 200$, $k = 50$ that is
      $d = 0.5$, far past the radius any of §4's baselines demands
      (`test_reed_solomon_radius_beats_what_prange_needs`).
    - **A random linear code** has no known efficient decoder beyond the
      information-set regime — which is *the attacker's own algorithm*. So
      on random sparse instances DQI is asking Prange to beat Prange, and
      the advantage cancels identically.

    **No DQI advantage without algebraic structure**, and now with a
    mechanism rather than a slogan: *structure is what an efficient decoder
    needs in order to exist*. Connect it to
    [autopsy 05](../05-hsp-graveyard/notes.md) — abelian structure was what
    made the shadow readable there, algebraic structure is what makes the
    decoder exist here. Same shape, twice.

Plus Sun–Wootters: DQI's semicircle law is *not optimal* on worst-case OPI —
headroom exists, for either side.

---

## 6. The lesson — YOUR TURN

!!! abstract "Write this section yourself — this is the ground you'll hunt on"

    Argue with the draft, then replace it.

    <div class="qq-lesson" markdown>

    **The quantum–classical asymmetry enters at exactly one place: the
    decoder has to run coherently on a superposition of syndromes.** That is
    cheap when the decoder is a fixed algebraic procedure — Berlekamp–Massey,
    Guruswami–Sudan — and expensive or impossible when it is a search. So
    the hunt's shopping list is not "codes with good distance"; it is
    **codes whose decoder is a straight-line algebraic computation**.

    Why structure survived and randomness fell is then immediate: an
    efficient decoder is a piece of *structure*, and a random code has none
    to offer. Reed–Solomon's decoder reaches $d = 0.5$; a random code's
    reaches the Prange line, which is where the attacker already is.

    Where a new problem family plugs in — four axes, and §5's table says
    which are under-attacked:

    1. **new code** (AG / Hermitian — standing, younger),
    2. **new metric** (rank-metric / Gabidulin — standing, un-stress-tested),
    3. **new decoder** (anything reaching further than list decoding),
    4. **new objective-to-code reduction** — the least explored, and the
       one that does not need a coding-theory breakthrough to pay off.

    Our own [CRT construction](../../strike/crt-dqi-theorem.md) is axis 4
    with a continued-fraction decoder, which is why the numbers on this page
    are the ones to hold it against.

    </div>

Questions worth answering in your own words:

- Where exactly does the quantum–classical asymmetry enter, and when is
  coherent decoding cheap?
- §4 turns the advantage into a required decoding radius. What radius does
  *our* construction need, and does its decoder reach it?
- Sun–Wootters say the semicircle is not optimal on worst-case OPI. Is that
  headroom for us or for the classical side — and what would settle it?

---

## Exercises

!!! example "Run it"

    ```bash
    .venv/bin/python predecessors/11-dqi/dqi_spectrum.py     # §2-§3
    .venv/bin/python predecessors/11-dqi/prange_baseline.py  # §4-§5
    .venv/bin/pytest predecessors/11-dqi -q                  # 28 tests
    ```

- [ ] Read 2408.08292 §1–3 at proof level; re-derive the Fourier-support
      claim for max-XORSAT yourself — it is Parseval plus the binomial
      expansion of $P(f)$. Then check your derivation against
      `test_the_spectrum_lives_on_low_weight_codewords`, which verifies it
      by transform.
- [ ] From the sweep: list the three 2026 negative results for sparse
      instances with a one-sentence mechanism each.
- [ ] **The hunt-phase question** (one page): what does a problem need to be
      "OPI-like enough" to inherit the advantage, yet different enough to be
      a new result? Use §6's four axes.
- [ ] **New.** `dqi_spectrum.py` implements max-XORSAT over $\mathbb{F}_2$.
      Extend `objective_sign` to $\mathbb{F}_p$ and check that the support
      claim still holds — the characters become $p$-th roots of unity and
      the "XOR of $\le \ell$ rows" becomes a $\mathbb{F}_p$-combination.
      This is the step from max-XORSAT to OPI.
- [ ] **New.** §3's tridiagonal form assumes the weight-$k$ subspaces are
      orthogonal. Find the $\ell$ at which that fails for a concrete small
      code (hint: its minimum distance), and compare with the $d = 1/2$
      boundary the module uses.
- [ ] **The uncomfortable one.** §4's radii are lower bounds because they
      use the asymptotic Prange line. Re-run the head-to-head using
      *measured* Prange at the same $m$, and report how much the required
      radius moves. If it moves a lot, every margin quoted for a DQI variant
      — including ours — needs re-checking at finite size.
