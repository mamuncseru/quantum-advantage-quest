# A3 — The product branch is closed: only Hamming and Doob

!!! success "Result, 2026-07-08 — one branch of the DQI-beyond-Hamming map is now a theorem"

    **A Cartesian product of two or more connected graphs is distance-regular
    if and only if it is a Hamming graph $H(N,q)$ or a Doob graph $D(m,n)$.**
    Consequently every *coordinate-decomposable* DQI geometry — any metric
    that is a sum of per-block weights — is Hamming or Doob. The Lee kill
    was the tip of this iceberg. One genuinely non-Hamming door survives,
    and it is unique: the **Doob scheme**, $q=4$, Shrikhande blocks.

    Status of the mathematics: the graph classification turns out to be
    **known** (Song 1986 + Egawa 1981; assembled in Stevanović 2004 — found
    by lit-check *after* we derived and computationally verified it
    independently). The DQI corollary and the Doob-DQI analysis below are,
    to our knowledge, new — DQI postdates all three papers by two decades.

## The theorem

> **Theorem (product branch).** Let $G_1,\dots,G_r$ ($r\ge 2$) be connected
> graphs, each with at least one edge, and let $P = G_1 \square \cdots
> \square G_r$ be their Cartesian product. Then $P$ is distance-regular iff
> every factor has the intersection array of a Hamming graph $H(d_i, q)$
> with one **common** $q$. By Egawa's characterization this makes $P$ a
> Hamming graph $H(N,q)$, or (exactly when $q=4$) a Doob graph
> $D(m,n) = \text{Shrikhande}^{\square m}\,\square\,K_4^{\square n}$.

**Attribution.** The two-factor classification is due to
[S.Y. Song, *Products of distance-regular graphs*, Util. Math. 29 (1986)](https://www.semanticscholar.org/search?q=Song%20products%20of%20distance-regular%20graphs),
summarized with the other three NEPS compositions in
[Stevanović, *Distance regularity of compositions of graphs*, AML 17 (2004)](https://draganstevanovic.wordpress.com/wp-content/uploads/2012/09/drcg.pdf)
(his Main Theorem (i): $G+H$ DR iff both factors have
$\mathrm{Ham}(D,\,a_1+2)$ parameters). The classification input is
[Egawa, *Characterization of $H(n,q)$ by the parameters*, JCTA 31 (1981)](https://www.sciencedirect.com/science/article/pii/S0095895685710465):
a DRG with $H(d,q)$'s array is $H(d,q)$ unless $q=4$, where the Doob
graphs are the only exceptions (diameter 2: Shrikhande 1959). We keep our
independent proof below because it is short, self-contained, and its
intermediate conditions are exactly the kill-witnesses the computation
finds.

## The proof

Write $c_j, a_j, b_j$ for intersection numbers. Distances in $P$ add over
blocks; a neighbour of $x$ differs from $x$ in exactly one block.

**Step 1 — every factor is DR, with shared $c_j, a_j$.** Take $x,y$
differing only in block $i$ at distance $j$. Any $z \sim x$ differing in
block $i' \ne i$ has $d(z,y) = j+1$. So the counts of $z\sim x$ at distance
$j-1$ (resp. $j$) from $y$ are *within-block* counts, and DR of $P$ forces
them constant: each $G_i$ is DR with $c_j(G_i) = c_j(P)$ and
$a_j(G_i) = a_j(P)$ for all $j \le \operatorname{diam} G_i$ — the same
sequences for every factor.

**Step 2 — $c_2 = 2$.** A pair split across two blocks ($d_i = d_{i'} = 1$)
has exactly two common neighbours, $(\dots y_i \dots x_{i'} \dots)$ and
$(\dots x_i \dots y_{i'} \dots)$. A within-block pair at distance 2 has
$c_2(G_i)$ of them. Equality forces $c_2 = 2$. *(Cycles $C_q$, $q\ge5$,
have $c_2 = 1$ — the entire Lee kill is this line.)*

**Step 3 — $a_2 = 2a_1$.** For the split pair, $z \sim x$ with $d(z,y)=2$
must move block $i$ (or $i'$) to a common neighbour of the adjacent pair
$x_i, y_i$: that is $a_1$ choices each, $2a_1$ total. The within-block
count is $a_2$. *(Clebsch: $a_2 = k-c_2 = 3 \ne 0 = 2a_1$ — see below.)*

**Step 4 — induction, $c_{j+1} = j+1$ and $a_{j+1} = (j+1)\,a_1$.** For a
pair of type $(j, 1)$ across blocks $(i, i')$: $z \sim x$ lowering the
distance either lowers block $i$ ($c_j = j$ ways, induction) or closes
block $i'$ ($1$ way): $c_{j+1} = j+1$. Keeping the distance: $a_j = j a_1$
ways in block $i$, $a_1$ in block $i'$: $a_{j+1} = (j+1) a_1$.

**Step 5 — that is Hamming's array.** For each factor: $c_j = j$,
$a_j = j\,a_1$, $b_j = k_i - j(a_1+1)$, and $b_{d_i} = 0$ forces
$k_i = d_i(a_1+1)$ — precisely the array of $H(d_i, q)$ with
$q = a_1 + 2$, common across factors. Egawa (plus Shrikhande for $d=2$)
converts arrays into graphs: $K_q$/Hamming pieces for $q \ne 4$; for
$q = 4$ also Shrikhande blocks, i.e. Doob. Sufficiency is classical:
$H(N,q)$ and $D(m,n)$ are DR. $\blacksquare$

## Computed, not assumed

[`code/product_schemes.py`](../code/product_schemes.py) checks
distance-regularity exhaustively and extracts witnesses
([tests](../code/test_product_schemes.py), 7 green):

| product | $N$ | DR? | array | witness $(j,k,\min,\max)$ |
|---|---|---|---|---|
| $K_4 \square K_4$ | 16 | ✅ | $H(2,4)$ | |
| Shrikhande | 16 | ✅ | $H(2,4)$ | (same array, **not** $H(2,4)$: its vertex-neighbourhoods are 6-cycles, the rook's are $2K_3$) |
| $D(1,1),\ D(2,0),\ D(2,1)$ | 64–1024 | ✅ | $H(3,4), H(4,4), H(5,4)$ | |
| Clebsch alone | 16 | ✅ | *not Hamming* | |
| Clebsch $\square$ Clebsch | 256 | ❌ | | $(2,2,0,3)$ — Step 3 |
| Clebsch $\square$ $K_4$ | 64 | ❌ | | $(1,1,0,2)$ — $a_1$ clash |
| $C_5 \square C_5$ (Lee $q{=}5$) | 25 | ❌ | | $(1,2,1,2)$ — Step 2 |

**The Clebsch near-miss is the instructive one.** Clebsch = folded 5-cube
= $\mathrm{Cayley}(\mathbb{Z}_2^4,\ \{e_1,e_2,e_3,e_4,\mathbf{1}\})$, a
translation SRG with eigenvalues $\{5,1,-3\}$ — an arithmetic progression
with common difference 4, same as Shrikhande's $\{6,2,-2\}$ and $K_4$'s
$\{3,-1\}$. The 07-08 Lee note's AP-eigenvalue condition (necessary for
the right eigenvalue *count*) is satisfied — yet the square is not even
distance-regular. **The spectral condition is necessary but not
sufficient; the intersection axiom $a_2 = 2a_1$ is the binding gate**, and
Clebsch fails it because it is triangle-free ($a_1 = 0$) with $a_2 = 3$.

## Corollary for the hunt

**Coordinate-decomposable DQI is exactly $\{$Hamming, Doob$\}$.** DQI's
machinery (2606.04843 framework) needs a P-polynomial translation scheme;
if the weight is a sum of per-block weights, the weight-1 graph is a
Cartesian product and its distance classes must form the scheme — the
theorem then leaves Hamming and Doob, full stop. This upgrades the Lee
kill from "the canonical candidate is dead" to **"the entire H2′ search
space contains exactly one non-Hamming point."** A1's remaining target
H1′ (the obstruction theorem) is untouched but its complement is now
maximally sharp.

## The one live door: Doob-DQI

$D(m,n)$ is a translation scheme on $\mathbb{Z}_4^{2m} \times
\mathbb{Z}_4^{n}$ with the **same intersection array as $H(2m+n, 4)$** —
so the Jacobi matrix, the shell dynamics, and the semicircle payoff curve
of a Doob-DQI are *identical* to Hamming DQI at $q=4$. Three structural
facts make it a genuine (not cosmetic) new instance:

1. **Self-duality (computed).** The dual partition of the Shrikhande
   scheme — characters $\chi_{(a,b)}$ of $\mathbb{Z}_4^2$ grouped by
   eigenvalue $2\cos\frac{\pi a}{2} + 2\cos\frac{\pi b}{2} +
   2\cos\frac{\pi(a+b)}{2} \in \{6, 2, -2\}$ — has eigenvalue-2 class
   $\{\pm(1,0), \pm(0,1), \pm(1,3)\}$, which is a Shrikhande connection
   set again (image under $(x,y) \mapsto (x,-y)$). Like Hamming, Doob is
   formally self-dual: MacWilliams/Fourier duality keeps Doob weight on
   both sides, so DQI's uncomputation step is structurally unchanged.

2. **A strictly larger objective language.** Hamming DQI scores
   *single* affine forms: $f_i(\langle b_i, x\rangle)$. Doob-DQI scores
   **pairs of $\mathbb{Z}_4$-forms through Shrikhande-radial predicates**
   $g(u,v)$, constant on Shrikhande shells of $(u,v)$. These are not
   single-form functions — the radius-1 ball has $|B_1| = 7$ elements,
   while any function of one affine form has level sets of size divisible
   by 4. And because the metric is still coordinate-decomposable, the
   objective **counts satisfied blocks** — the covering-radius obstruction
   that forced the rank-metric authors' disclaimer (A1) never enters.
   Doob is the unique scheme combining "non-Hamming" with "counting
   objective."

3. **Incomparable weights, so decoders do not transfer.** On a block,
   $\mathrm{wt}_{Sh}(2,0) = 2$ but Hamming-$\mathbb{Z}_4^2$ weight 1;
   $\mathrm{wt}_{Sh}(1,1) = 1$ but Hamming weight 2. Neither metric
   dominates the other: a Doob decoder is not a repackaged Hamming
   decoder in either direction.

Honesty ledger, before anyone gets excited:

- **Payoff menu is a wash.** Per-block densities $\mu' = r'/16$,
  $r' \in \{1, 6, 7, 9, 10, 15\}$, include new values vs $q=4$'s
  $\{4,8,12\}/16$ — but $\mu = 1/2$ (the semicircle sweet spot) is in
  both menus, and $H(N', 16)$ reaches every $r'/16$ with arbitrary
  predicates. The advantage, if any, is **not** in the payoff formula.
- **The real question:** the triple (group $\mathbb{Z}_4$-additive,
  Doob metric, Shrikhande-radial predicates) sits strictly between
  $H(N,4)$ and $H(N/2,16)$. Does it contain a **classically-hard
  objective whose dual code is efficiently Doob-decodable to linear
  radius**? Nothing in the Doob-code literature answers this: known
  results are radius-1 perfect codes
  ([existence iff $6m+3n+1$ is a power of 2 — Krotov et al.](https://arxiv.org/abs/1407.6329),
  [arXiv:1810.03772](https://arxiv.org/pdf/1810.03772)), additive/linear
  perfect-code characterizations, and
  [MDS classifications](https://arxiv.org/pdf/1510.01429). **No
  linear-radius decoder for any Doob code family is known** — the same
  gate A2 is stuck at, in a different geometry.

### Pre-registered kills (Doob-DQI)

1. **K1 — disguise kill.** If Shrikhande-radial pair predicates admit a
   payoff-preserving gadget reduction to single-form $q=4$ (or $q=16$)
   LinSAT at matched $(m, \ell)$, Doob-DQI is Hamming-DQI in disguise:
   kill. First check: compare best gadget emulation payoff against the
   block payoff at equal constraint budget.
2. **K2 — decoder gate.** No $\mathbb{Z}_4$-additive family with linear
   minimum Doob distance and an efficient decoder within 8 weeks of
   focused search → park (this is A2's condition transplanted; do not
   run two open-decoder hunts in parallel — whichever falls first
   revives the other).
3. **K3 — hardness gate.** If max-Shrikhande-LinSAT with random pairs is
   classically approximable beyond the DQI curve (Prange-analog over
   block information sets, or an SDP beating $\mu' + $ semicircle
   uplift), kill. Cheapest first: compute the block-Prange baseline —
   it is array-determined and may already close the window.

    **K3 first check (done 2026-07-08, red flag).** Radial predicates
    have *form-aligned conditional bias*: for $g = 1_{B_1}$
    ($\mu' = 7/16$), pinning one form to $u=0$ satisfies the block with
    probability $3/4$ (the surviving elements are $(0,0),(0,\pm1)$). A
    budget of $N$ pinned forms is therefore better spent one-per-block
    (marginal $3/4 - 7/16 = 5/16$) than two-per-block (marginal $1/4$):
    with $\tau = N/m'$, the predicate-aware baseline achieves
    $\frac{7}{16} + \frac{10}{32}\tau$ versus the array-matched Prange's
    $\frac{7}{16} + \frac{9}{32}\tau$ — **strictly stronger, at every
    budget**. The DQI side is array-determined; the classical side is
    not. Unless the general-scheme payoff formula for pair predicates
    delivers an uplift beyond Hamming's (no reason to expect it — the
    Jacobi data are identical), the Doob window is *at most* Hamming's
    and likely narrower. Next action: derive the exact Doob-DQI payoff
    for radial pair predicates and quantify; if it clears nothing beyond
    Hamming, K3 fires and the door closes honestly.

### Where this leaves the A3 map

| P-polynomial translation scheme | objective type | decoder | status |
|---|---|---|---|
| Hamming $H(N,q)$ | counting ✅ | classical families ✅ | taken (DQI) |
| forms schemes (bilinear/alternating/Hermitian) | distance-min only | Gabidulin etc. | obstruction — disclaimed (A1) |
| **products beyond these** | — | — | **closed by this theorem** |
| **Doob $D(m,n)$** | **counting ✅ (pair predicates)** | **open** | **the unique live door (K3-flagged)** |
| halved cube $\tfrac12 H(d,2)$ | Hamming-radial subclass | even subcodes | **reduces to Hamming DQI** |
| folded cube | complement-symmetric Hamming-radial | codes $\ni \mathbf{1}$ | **reduces to Hamming DQI** |

**The quotient rows close by inspection.** The halved cube is the Hamming
scheme *restricted to the even-weight subgroup* (its distance is
$\mathrm{wt}/2$ — a rescaled Hamming weight), and the folded cube is
Hamming *on the quotient* $\mathbb{Z}_2^d/\langle\mathbf{1}\rangle$ (its
distance is $\min(\mathrm{wt}, d-\mathrm{wt})$). Their Bose–Mesner
algebras are restrictions/fusions of Hamming's; their radial functions
are subclasses of Hamming-radial functions; a DQI instance on either is a
Hamming-DQI instance whose dual code carries a side condition (even
weight, resp. contains $\mathbf{1}$). New geometry: none.

**Two boundary caveats, so this map is not oversold.** (1) Bounded-diameter
schemes are DQI-irrelevant regardless of structure: every connected
translation SRG (Paley graphs, …) is trivially P-polynomial with diameter
2, but the semicircle payoff needs the shell count to scale with the
instance — only *unbounded-diameter* families matter. (2) There is **no
completeness theorem** for unbounded-diameter P-polynomial translation
schemes (that classification is open); this map covers the known
families — Hamming and its quotients, Doob, and the forms schemes — not
all conceivable ones. Within the coordinate-decomposable branch, however,
the closure is a theorem, not a survey.
