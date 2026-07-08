# A1∩A2 working note — Lee-metric DQI, the shared spine

!!! failure "SUPERSEDED 2026-07-08 — this direction was killed"

    The conjecture below was tested and **failed at its first gate**: the Lee
    metric on $\mathbb{Z}_q^n$ is not even an association scheme for $q\ge5$,
    so DQI's shell/Jacobi machinery has no foothold. See
    **[AC-lee-metric-KILLED.md](AC-lee-metric-KILLED.md)** for the
    computation, the concrete witness, and the redirection to candidate A3.
    This note is kept for the reasoning trail — it shows *why* Lee looked
    right (coordinate-decomposable, counting objective) and what we missed
    (the scheme axiom precedes the decoder question).

!!! warning "Original epistemic status (2026-07-07)"

    Framing note, AI-drafted, unverified. Connects two threads (A1's
    objective-type obstruction, A2's decoder obstruction) into one target.

## Why the two candidates converged here

- **A1** (from reading 2606.04843): DQI's covering-radius obstruction is a
  property of **distance-minimization** objectives; it vanishes for
  **counting** objectives (max-LinSAT), which exist only in
  *coordinate-decomposable* metrics. Hamming has them; rank does not.
- **A2** (from the LLL attack, section 8 of the CRT note): sparse recovery
  under **archimedean (size) noise** blocks the naive lattice, because
  size-distance is not the Hamming weight the DQI machinery decodes.

Both point at the same missing object: **a non-Hamming metric that is still
coordinate-decomposable, with a counting objective and an efficient
bounded-distance decoder.** The **Lee metric** over $\mathbb{Z}_q$ is the
canonical candidate.

## The Lee metric, and why it fits

Lee weight $w_L(x) = \sum_i \min(x_i, q - x_i)$ on $\mathbb{Z}_q^n$: a
cyclic, coordinate-decomposable distance interpolating Hamming ($q \le 3$)
and archimedean ($q$ large, single coordinate $\approx |{\cdot}|$). The
checklist DQI needs, against the Lee scheme:

| DQI ingredient | Lee-metric status |
|---|---|
| P-polynomial translation scheme | ✅ the Lee scheme on $\mathbb{Z}_q$ is P-polynomial (known; radial operator = a known Jacobi matrix) |
| shell Dicke states, radial subspace | ✅ inherited from the 2606.04843 framework |
| counting objective (max-LinSAT) | ✅ **exists** — Lee distance decomposes per coordinate, unlike rank |
| efficient bounded-distance decoder | ⚠️ **the open question** — Lee-metric BCH / negacyclic codes have algebraic decoders (Roth–Siegel, Berlekamp); radius vs the DQI need is unverified |
| Fourier phases over $\mathbb{Z}_q$ | ✅ standard |

The one ⚠️ is the whole game — same as always, the decoder decides.

## The bridge to A2, made precise

A2's window noise is *archimedean* on $\mathbb{Z}_M$. Embed a coarse-grained
version into the Lee metric: a shift $|\delta| \le \Delta$ has small Lee
weight in a mixed-radix $\mathbb{Z}_{p_1}\times\cdots$ representation *only
if* the carry structure is controlled. **Conjecture to test:** CRT-OPI with
the window becomes Lee-metric decoding on the product scheme, and the
"kernel pollution" that killed the naive lattice (section 8) is exactly the
statement that the Lee ball is not aligned with the CRT sublattices unless
the metric is chosen Lee-not-Euclidean. If true, Lee-metric DQI would
*subsume* CRT-OPI and dodge its decoder obstruction — the escape route (i)
of section 8, made structural.

## Why this might still fail (pre-registered kills)

1. Lee-BCH decoding radius may be too small — same covering-radius
   obstruction as rank, just at a different constant. Check first: compare
   Lee packing radius vs the semicircle-useful $\ell$.
2. The scheme's Jacobi matrix may give a *worse* semicircle law than
   Hamming (the radial eigenvalues are $q$-analogues; their spread sets the
   payoff). Compute it.
3. Lee-metric optimization may just be classically easy (dynamic
   programming over $\mathbb{Z}_q$ per coordinate?) — the Tang test for this
   ground. **Run this check first**; it is the cheapest kill.

## First actions

1. Kill-check 3: is max-Lee-LinSAT classically easy? (per-coordinate DP /
   transfer matrix — if yes, done, negative result.)
2. If it survives: compute the Lee-scheme Jacobi matrix radial eigenvalues
   ($q$-Krawtchouk-like) and the resulting semicircle payoff.
3. Inventory Lee-metric decoders (Roth–Siegel, Byrne–Greferath) and their
   radii vs the DQI need.
