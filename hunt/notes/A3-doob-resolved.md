# A3 — Doob-DQI resolved: new geometry, no new advantage (K3 fires)

!!! success "Resolution, 2026-07-08 — the last coordinate-decomposable door closes"

    The Doob scheme is the unique non-Hamming coordinate-decomposable
    P-polynomial translation scheme ([product theorem](A3-product-theorem.md)).
    We now show its DQI instance offers **no advantage beyond Hamming**. The
    coordinate-decomposable DQI-beyond-Hamming branch is therefore
    **completely closed: Hamming is the unique advantage home.**

## The argument (two rigorous legs + one empirical)

Computed exactly on the 16-element Shrikhande scheme,
[`code/shrikhande_dqi.py`](../code/shrikhande_dqi.py)
([tests](../code/test_shrikhande_dqi.py) green).

### Leg 1 — Doob-DQI's payoff is a *subset* of the Hamming family's

The DQI semicircle (Eq 6 of 2408.08292, verified) is

$$
\frac{\langle s\rangle}{m} = \Big(\sqrt{\tfrac{\ell}{m}(1-\mu)}
+ \sqrt{\mu(1-\tfrac{\ell}{m})}\Big)^2 ,
$$

which **has no alphabet parameter** — it depends only on the density $\mu$
and decoder radius $\ell/m$. Doob $D(m,n)$ has the *same intersection array /
Jacobi matrix* as $H(2m{+}n,4)$, so its radial DQI dynamics are identical.
Every density Doob's pair predicates reach
($\mu' \in \{1,6,7,9,10,15\}/16$), plus the sweet spot $8/16$ available
through $D(m,n)$'s $K_4$ single-form blocks, is reached by an ordinary
$H(N,16)$ single-form target set of the same size. Hence

> **anything Doob-DQI achieves at $(\mu,\ell/m)$, $H(N,16)$-DQI achieves at
> the same $(\mu,\ell/m)$.** Doob's payoff set $\subseteq$ Hamming family's.

The only conceivable escape is the decoder gate (K2): a Doob decoder reaching
larger $\ell/m$ than any Hamming decoder. No Doob-code decoder exists in the
literature at all, and nothing suggests it would beat Hamming's — this is
A2's open gate, not a Doob advantage.

### Leg 2 — the objective hands the classical attacker a strictly stronger lever

Shrikhande-radial *pair* predicates leak **form-aligned conditional bias**
that single forms do not. For $g = \mathbf{1}_{B_1}$ ($\mu' = 7/16$),
pinning one form to $0$ raises the block satisfaction to $3/4$ (verified
exactly). Spending budget one-form-per-block therefore beats the
array-matched two-form Prange at every budget:

| classical strategy | marginal per unit |
|---|---|
| array-matched Prange (pin both forms) | $9/32$ |
| **predicate-aware (pin one form, exploit $3/4$ bias)** | $\mathbf{10/32}$ |

So the classical baseline on Doob is *strictly stronger* than the single-form
baseline at the same $\mu$. DQI's side is unchanged (Leg 1); the classical
side only improves. The window can only shrink.

### Leg 3 (empirical corroboration) — random instances are classically easy

Brute-forced max-Shrikhande-LinSAT optimum vs a strong poly-time classical
opponent (random restart + greedy $\mathbb{Z}_4$ local search), overconstrained
regime:

| $n$ | $m'$ | true optimum | strong classical | gap |
|---|---|---|---|---|
| 7 | 40 | 0.760 | 0.750 | 0.010 |
| 7 | 60 | 0.683 | 0.670 | 0.013 |
| 8 | 60 | 0.710 | 0.697 | 0.013 |

Greedy local search tracks the optimum to ~1%. Small-scale and random-regime
(not the structured OPI-like regime), so *suggestive not decisive* — but fully
consistent with Legs 1–2: no advantage room on random Doob instances.

## Verdict

**K3 fires.** Doob-DQI replicates Hamming's payoff at best and faces a
strictly stronger classical baseline; it is a genuine new *geometry* (the only
non-Hamming coordinate-decomposable P-polynomial translation scheme) but **not
a new source of quantum advantage.** Together with the product theorem:

> **Among all coordinate-decomposable metrics, Hamming is the unique DQI
> advantage home.** Lee ($q\ge5$) is not a scheme; every other product is
> Hamming or Doob; Doob adds geometry but no advantage.

This is a clean negative boundary for shape #10 — publishable as *"the limits
of DQI-beyond-Hamming for coordinate-decomposable metrics."*

## What stays open (honestly)

- **Non-product P-polynomial translation schemes.** No completeness theorem
  exists for unbounded-diameter ones; the forms schemes (rank etc.) are
  non-product and hit the covering-radius obstruction (A1). Whether some
  *other* non-product family escapes both obstructions is not settled — but
  it is outside the coordinate-decomposable world this branch closed.
- **A2 (CRT-OPI)** is unaffected: it never relied on a metric scheme; its gate
  remains the algebraic $\mathbb{Z}/M$ decoder or list-decoding-through-
  uncomputation.
