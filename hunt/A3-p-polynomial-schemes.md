# A3 — Which P-polynomial translation schemes carry a hard objective?

**Seeded 2026-07-08**, the redirection forced by the Lee kill
([note](notes/AC-lee-metric-KILLED.md)). Status: **first branch closed the
same day** — see below.

!!! success "Update 2026-07-08 (second session) — the product branch is a theorem"

    The enumeration question is *answered* for all Cartesian-product
    schemes: **a product of connected graphs is distance-regular iff it is
    Hamming or Doob** (independently derived and computationally verified;
    lit-check then found the classification is known — Song 1986 + Egawa
    1981). Coordinate-decomposable DQI therefore lives on exactly two
    geometries, and only **Doob $D(m,n)$** is non-Hamming: a counting
    objective over Shrikhande-radial *pair* predicates, self-dual scheme,
    array identical to $H(2m+n,4)$; gates = Doob decoder + hardness
    separation, kills pre-registered. Full proof, witnesses (the Clebsch
    near-miss shows AP-eigenvalues are not sufficient), and the updated
    scheme×objective×decoder map:
    [notes/A3-product-theorem.md](notes/A3-product-theorem.md). Doob first
    action 1 below is done; the halved/folded-cube quotient rows are the
    remaining enumeration work.

## The question, corrected

The Lee kill taught us the real gate for DQI-beyond-Hamming is not the
decoder but the **association scheme** itself: DQI needs a P-polynomial
translation scheme so the radial dynamics are tridiagonal. So the search
reorders:

> Enumerate the P-polynomial translation schemes (equivalently: the
> distance-regular Cayley graphs on abelian groups). For each, ask: (a) is
> there a natural max-LinSAT-type counting objective? (b) is its dual code
> efficiently *algebraically* decodable (not just lattice-decodable — the
> 07-07 finding)? (c) is the optimization classically hard?

Only schemes clearing (a)+(b)+(c) can host a new DQI advantage. Hamming and
rank (bilinear forms) are the two known winners; the question is whether the
list is longer.

## Known P-polynomial translation schemes to work through

- **Hamming** $H(n,q)$ — DQI's home. Taken.
- **Bilinear/alternating/Hermitian forms** (rank metric) — 2606.04843.
  Taken, and hit the covering-radius obstruction for distance objectives.
- **Johnson scheme** — not a *translation* scheme (no abelian group), so the
  finite-field Fourier step needs rethinking; likely out.
- **Halved/folded cubes, Doob schemes** ($\mathbb{Z}_4$-based mix of Hamming
  and Shrikhande) — P-polynomial, translation. **Doob is the interesting
  one:** it is a genuine non-Hamming P-polynomial translation scheme built
  from $\mathbb{Z}_4$ / Shrikhande factors. Does it carry a hard objective?
- **Bilinear forms over rings, skew-symmetric forms** — younger, less mapped.

The classification of distance-regular Cayley graphs (van Dam–Koolen–Tanaka
survey territory) is the reference map; the P-polynomial translation ones are
a short, studied list — which is exactly why this is finite, checkable work
rather than an open-ended hunt.

## Pre-registration

- **Advantage currency:** as A2 — superpoly vs best-known, DQI honesty note.
- **First kill (cheapest):** for each candidate scheme, the $2\cos$-type
  arithmetic-progression / distinct-eigenvalue test (`code/lee_scheme.py`
  generalizes) — rules out non-P-polynomial pretenders in minutes.
- **Second kill:** semicircle-payoff-vs-classical-baseline for the survivors.
- **Deliverable either way:** a table "P-polynomial translation schemes ×
  (objective? decoder? hard?)" — the map of where DQI-beyond-Hamming *can*
  live. Even if empty beyond Hamming+rank, that is a publishable boundary:
  *DQI advantage is essentially confined to the Hamming and forms schemes.*

## First actions

1. Build the Doob scheme; run the P-polynomial test; if it passes, find its
   natural objective and dual code.
2. Tabulate the known P-polynomial translation schemes with their parameters.
3. For each, the arithmetic-progression eigenvalue check.
