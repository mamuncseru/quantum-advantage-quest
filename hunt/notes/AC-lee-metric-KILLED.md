# A1∩A2 — Lee-metric DQI is structurally dead for q ≥ 5

!!! danger "Kill, 2026-07-08 — with a mechanism and a concrete witness"

    The cheapest pre-registered kill-check fired, harder than expected. The
    Lee metric on $\mathbb{Z}_q^n$ does **not form a P-polynomial translation
    association scheme** for $q \ge 5$ — in fact it is **not an association
    scheme at all**. DQI's entire analytical machinery (shell Dicke states,
    radial subspace, tridiagonal Jacobi operator, semicircle law) is built on
    that structure, so it has no foothold. Computed, not assumed:
    [`code/lee_scheme.py`](../code/lee_scheme.py), tests green.

## The computation

| $q$ | $n$ | association scheme? | #eig$(A_1)$ | $D{+}1$ | P-polynomial? |
|---|---|---|---|---|---|
| 3 | 2 | ✅ | 3 | 3 | ✅ (Hamming — sanity) |
| 3 | 3 | ✅ | 4 | 4 | ✅ |
| 4 | 2 | ✅ | 5 | 5 | ✅ (the $\mathbb{Z}_4$ special case) |
| 4 | 3 | ✅ | 7 | 7 | ✅ |
| **5** | **2** | ❌ | 6 | 5 | ❌ |
| **5** | **3** | ❌ | 10 | 7 | ❌ |
| **6** | **2** | ❌ | 9 | 7 | ❌ |
| **7** | **2** | ❌ | 10 | 7 | ❌ |

## The concrete witness (q = 5, n = 2)

The intersection number $p_{11}^{2}$ — how many common Lee-distance-1
neighbours two Lee-distance-2 points share — takes **both values 1 and 2**
depending on the pair. Two points at Lee distance 2 can differ by one
coordinate changing by $2$, or two coordinates each by $1$; these are
geometrically different, so the "distance-2 shell" is not homogeneous. Integer
path counts, not roundoff. One inhomogeneous intersection number is enough to
break the association-scheme axiom.

## The mechanism (crisp, and it predicts the boundary)

A translation scheme's distance-$k$ operators are simultaneously diagonalised
by the group characters; P-polynomiality needs $A_1$ to have exactly $D+1$
distinct eigenvalues. The single-coordinate cycle $\mathbb{Z}_q$ has
eigenvalues $2\cos(2\pi t/q)$, and the $n$-fold sums collapse to
$n\lfloor q/2\rfloor+1$ values **iff the base values form an arithmetic
progression**:

| $q$ | base eigenvalues $2\cos(2\pi t/q)$ | AP? |
|---|---|---|
| 3 | $\{-1, 2\}$ | ✅ |
| 4 | $\{-2, 0, 2\}$ | ✅ |
| 5 | $\{-1.618, 0.618, 2\}$ | ❌ |
| 6 | $\{-2, -1, 1, 2\}$ | ❌ |
| 7 | $\{-1.802, -0.445, 1.247, 2\}$ | ❌ |

$2\cos(2\pi t/q)$ is an arithmetic progression only for $q \le 4$. So the
$\mathbb{Z}_4$ case (Kerdock–Preparata's home) is the *last* Lee metric with
DQI-compatible structure, and it coincides with essentially Hamming-type
structure — nothing new over Hamming DQI.

## What this kills, and what it teaches

- **A1's hypothesis H2′** (circumvent the covering-radius obstruction via a
  coordinate-decomposable non-Hamming metric): the canonical candidate is
  dead. Lee doesn't provide the structure.
- **A2's escape route (i)** (reduce CRT window-decoding to Lee decoding):
  dead in this form — there is no Lee scheme to decode in the DQI sense.
- **Catalog-level insight (the real prize):** *DQI-beyond-Hamming is gated on
  the existence of a **P-polynomial translation scheme**, and these are rare.*
  Among natural metrics: Hamming ✅, rank ✅ (bilinear-forms scheme), Lee ❌
  for $q\ge5$. The "new metric ⇒ new DQI advantage" program is far more
  constrained than it looks — the scheme axiom, not the decoder, is the first
  gate. This belongs in the Problem-Shape Catalog as a sharpening of shape #10.

## Where the two candidates go now

- **A1 → H1′ only.** The obstruction looks intrinsic; the remaining move is to
  *prove* it (covering radius > efficient decoding radius forces no additive
  guarantee for distance-minimization objectives in any scheme). That is a
  clean theorem target, not a new-advantage target — an honest negative
  contribution.
- **A2 → escape route (ii) only.** List-decoding pushed through DQI's
  uncomputation as a superposition. This changes the amplitude analysis and
  may be fatal; it is now A2's single remaining path to asymptotic advantage.
- **Redirection (new):** the right question is no longer "which metric" but
  **"which P-polynomial translation schemes exist beyond Hamming and rank,
  and do any carry a natural, classically-hard optimization objective?"** The
  classification of distance-regular Cayley graphs is the relevant math. New
  candidate seed A3, logged.
