# A2 working note — the CRT-OPI transplant, first derivation

!!! warning "Epistemic status"

    Derived by the AI in a single session (2026-07-06), unverified by human.
    Every step is elementary Fourier analysis on $\mathbb{Z}_M$ except the
    two flagged as **open**. The self-attack section applies. Nothing here is
    a claim; it is a map of where the claim would live.

## 1. Setup and dictionary

Moduli $p_1 < \dots < p_m$ pairwise coprime, $M = \prod_i p_i$. Residue map
$R(x) = (x \bmod p_1, \dots, x \bmod p_m)$; CRT makes $R$ a ring isomorphism
$\mathbb{Z}_M \to \prod_i \mathbb{Z}_{p_i}$. Sets $F_i \subset \mathbb{Z}_{p_i}$,
objective $f(x) = \sum_i \mathbb{1}[x \bmod p_i \in F_i]$.

**CRT-OPI$(X)$:** maximize $f$ over $x \in [0, X)$, where
$\kappa := \log X / \log M < 1$.

| RS-OPI (DQI paper) | CRT-OPI (this note) |
|---|---|
| polynomial $Q$, $\deg < n$ | integer $x < X$ |
| evaluation points $y \in \mathbb{F}_p^\times$ | moduli $p_i$ |
| agreement sets $F_y \subset \mathbb{F}_p$ | residue sets $F_i \subset \mathbb{Z}_{p_i}$ |
| rate $n/m$ | rate $\kappa = \log X/\log M$ |
| Reed–Solomon code | CRT code $\{R(x) : x < X\}$ |
| Berlekamp–Massey decoder | Goldreich–Ron–Sudan / Boneh decoder |

Sanity anchor: at $X = M$ the problem is trivial both classically
(CRT-combine any $a_i \in F_i$) and, as shown below, quantumly. Hardness
lives entirely in $\kappa < 1$.

## 2. Fourier structure (exact)

Characters of $\mathbb{Z}_M$: $\chi_t(x) = \omega_M^{tx}$. Since
$\mathbb{1}[x \equiv a \ (p_i)] = \frac{1}{p_i}\sum_{k \in \mathbb{Z}_{p_i}}
\omega_M^{(M/p_i)k\,x}\,\omega_{p_i}^{-ka}$, each constraint's Fourier
support is the order-$p_i$ subgroup $T_i = (M/p_i)\mathbb{Z}_{p_i}$, and any
$t \in \mathbb{Z}_M$ decomposes **uniquely** as
$t = \sum_i (M/p_i) k_i \bmod M$ with $k_i = t \cdot (M/p_i)^{-1} \bmod p_i$.
Define the **CRT weight** $w(t) = \#\{i : t \not\equiv 0 \bmod p_i\}$. Then a
degree-$\ell$ polynomial $P(f)$ has Fourier support exactly in
$\{t : w(t) \le \ell\}$ — the precise analogue of DQI's low-Hamming-weight
support.

## 3. Finding 1 — over the full ring, "decoding" is trivial

Run the DQI recipe on $\mathbb{Z}_M$: superpose sparse residue patterns
$(S, \{k_i\}_{i \in S})$ with $|S| \le \ell$ and per-coordinate amplitudes
$\hat g_i(k_i)$; compute $t = \sum_{i\in S}(M/p_i)k_i$; **uncompute the
pattern from $t$ by plain modular reduction** ($k_i = t(M/p_i)^{-1} \bmod
p_i$ — a bijection, no decoder needed); inverse QFT over $\mathbb{Z}_M$.
Output: $\sum_{x \in \mathbb{Z}_M} P(f(x))\,|x\rangle$ *exactly*, in
polynomial time.

This is correct and consistent: the unrestricted problem is classically
trivial, so both sides collapse together. **Interpretation:** in RS-DQI the
map $\mathbf y \mapsto B^T\mathbf y$ is compressive and inverting it inside
the weight ball is syndrome decoding — the expensive ingredient. Over
$\mathbb{Z}$, CRT makes the same map a bijection. *The entire difficulty of
CRT-OPI therefore relocates into the window constraint $x < X$.*

## 4. Finding 2 — the mountain, located precisely

Options for imposing $x < X$:

- **(a) Postselection** after measuring: success mass $\approx X/M =
  M^{\kappa - 1}$ — exponentially small. Dead.
- **(b) Amplitude amplification:** $\sqrt{M/X}$ rounds — exponential. Dead.
- **(c) Window built in from the start:** prepare
  $\sum_x W(x) P(f(x))\,|x\rangle$ with $W$ supported near $[0, X)$. In
  Fourier this convolves the clean sparse support with $\widehat W$. A sharp
  interval gives a Dirichlet kernel ($1/|t|$ tails — unusable). A
  **Gaussian-tapered window** (the Regev / Chen–Liu–Zhandry move) gives
  near-Gaussian localization of width $\sim M/X$ around each sparse
  frequency. The uncomputation step then receives $t' = t + \delta$,
  $|\delta| \lesssim (M/X)\,\mathrm{polylog}$, and must recover the sparse
  pattern — which is no longer trivial. It is a *new decoding problem*:

!!! question "Q(A2.1) — the open problem this note reduces A2 to"

    Given $t' \in \mathbb{Z}_M$ with the promise that there exists $t$ with
    $w(t) \le \ell$ and $|t - t'| \le \Delta$ (say $\Delta \approx
    M^{1-\kappa+o(1)}$): recover $t$ in $\mathrm{poly}(m, \log M)$ time —
    "**closest CRT-sparse integer**." Equivalently: decode sparse residue
    patterns under *archimedean* (size) noise rather than Hamming noise.

    Also open (flagged): the amplitude bookkeeping — that Gaussian tails
    through the nonlinear step degrade the semicircle payoff by only $o(1)$.
    The April-2024 LWE-algorithm bug lived in exactly this kind of
    Gaussian-window domain step; maximum suspicion applies.

If Q(A2.1) has an efficient algorithm at radius $\ell$, CRT-DQI follows;
with balanced moduli the GRS-type decoding radius gives $\ell/m \approx
(1-\kappa)/2$ — **numerically the same semicircle payoff curve as RS-OPI**
with $\kappa$ in place of $n/p$ (`hunt/code/advantage_window.py` applies
as-is). If Q(A2.1) is hard in the relevant regime, that is a boundary
theorem: *DQI's architecture requires windows that are linear-algebraic
(subspaces/degree bounds), and $\mathbb{Z}$ has none* — a publishable
insight about where the magic lives.

## 5. Finding 3 — the classical baseline (CRT-Prange), derived

Sort moduli ascending; take $S$ greedily with $\prod_{i \in S} p_i \le X$,
so $|S| \approx \kappa m$ for balanced moduli. Pick any $a_i \in F_i$ for
$i \in S$, CRT-combine: $x < X$ satisfies all of $S$; each remaining
constraint is satisfied at rate $\mu_i = |F_i|/p_i$ heuristically. Expected
fraction:

$$
\frac{\langle s\rangle}{m} \;\approx\; \kappa + \mu\,(1 - \kappa)
$$

— identical in form to OPI's Prange baseline ($n/m + \mu(1 - n/m)$), so the
**DQI-vs-Prange window, if Q(A2.1) resolves positively, is the same
+0.21-at-$\kappa\!\approx\!0.29$ window** we mapped for OPI. Enhancements to
inventory before any claim: Bleichenbacher–Nguyen-style lattice attacks on
noisy CRT (expected to work only at small error counts — the analogue of the
list-decoding regime — but this must be checked, not assumed; novelty-check
agent tasked).

## 6. Self-attack ledger (standing)

1. **Lattice attacks** may solve noisy CRT at constant agreement — would
   close the window classically. Status: inventory pending.
2. **Is CRT-OPI natural/hard?** Same epistemic tier as OPI (no
   complexity-theoretic hardness in regime; pedigree = cryptographic use of
   noisy CRT). Any claim inherits DQI's own honesty note verbatim.
3. **Unbalanced moduli** make both the weight metric and the decoding radius
   lopsided; balanced-moduli assumption must be surfaced in any statement.
4. **The window step** is the known graveyard of integer-QFT algorithms.
   Q(A2.1) plus bookkeeping is where this candidate lives or dies — no
   enthusiasm shortcuts.

## 7. First attack on Q(A2.1) — three results (same session)

**(i) The geometry of CRT-sparse integers.** For fixed support $S$, the set
$\{t : w(t)\text{-support} \subseteq S\}$ is exactly the subgroup of
multiples of $M/P_S$, $P_S = \prod_{i \in S} p_i$. So CRT-sparse integers
are a union of $\binom{m}{\le\ell}$ arithmetic progressions, with spacing
$M/P_S$ inside each.

**(ii) Constant $\ell$: enumeration finds the planted pattern — but
uniqueness taught us two lessons.** Enumeration over supports with
nearest-multiple rounding runs in $O(m^\ell)$ and recovers the planted $t$
(verified, `code/crt_sparse_decode.py`, 5/5 seeds). Uniqueness, however,
fell twice to our own tests:

- *Correction 1:* the per-support bound $\Delta < M/(2 P_S)$ is wrong —
  finer progressions (the $\ell$ largest moduli) admit spurious candidates.
  Empirically ~1500 of them.
- *Correction 2 (the real law):* two weight-$\le\ell$ integers differ by a
  weight-$\le 2\ell$ integer, so the exact uniqueness radius is
  $d_{\min}/2$ with

$$
d_{\min}(2\ell) \;=\; \min\{\, |t| \;:\; 0 \ne t \in \mathbb{Z}_M,\;
w(t) \le 2\ell \,\}
$$

  — how close a sparse combination $\sum_{i} k_i/p_i$ can sneak to an
  integer, scaled by $M$. For arbitrary prime sets this can be small
  (empirically ~200 candidates survive even the corrected radius); the
  decoder is honestly a **list decoder** at generic moduli. DQI's
  uncomputation needs uniqueness per branch, so:

!!! success "Q(A2.2) — RESOLVED (2026-07-07): the minimum-distance theorem"

    **Theorem (elementary; verified numerically 4/4 configurations, then
    5/5 planted-decoding seeds).** For any coprime moduli,

    $$
    d_{\min}(w) \;=\; \frac{M}{P_{\max}(w)},
    \qquad P_{\max}(w) = \text{product of the } w \text{ largest moduli.}
    $$

    *Lower bound:* a support-$S$ integer is a multiple of $M/P_S \ge
    M/P_{\max}(|S|)$. *Upper bound:* the map $(k_i) \mapsto \sum_i k_i
    (P_S/p_i) \bmod P_S$ hits **every** residue (CRT), in particular $1$ —
    so some weight-$\le|S|$ integer equals exactly $M/P_S$. $\blacksquare$

    **Consequences.** (1) Unique decoding radius is exactly
    $M/(2P_{\max}(2\ell))$ — implemented, and planted recovery is now
    unique, 5/5 seeds. (2) The "modulus design" freedom **evaporates**:
    $d_{\min}$ depends only on modulus *sizes*. Every balanced modulus set
    is automatically extremal — the number-theoretic twin of "Reed–Solomon
    is MDS," with CRT playing Vandermonde's role. No design can beat it;
    none is needed.

!!! abstract "The open-window statement (the candidate's viability, made precise)"

    With balanced moduli ($p_i \approx \bar p$), combine the three
    constraints — window noise $\Delta \approx M/X = M^{1-\kappa}$,
    uniqueness $\Delta < M/(2P_{\max}(2\ell))$, and the Prange-beating
    margin — at $\mu = 1/2$:

    $$
    \underbrace{\frac{\kappa^2}{4}}_{\text{beat Prange}}
    \;<\; \frac{\ell}{m} \;<\;
    \underbrace{\frac{\kappa}{2}}_{\text{unique decoding}}
    $$

    **The window is nonempty for every rate $0 < \kappa < 2$** — e.g.
    $\kappa = 0.1$: $0.0025 < \ell/m < 0.05$. Information-theoretically,
    CRT-DQI has room to live. Everything now rides on ONE question: an
    *efficient* decoder at sparsity $\ell = \varepsilon m$ within the
    theorem radius (Q(A2.1) at linear sparsity), plus the Gaussian-window
    amplitude bookkeeping. Enumeration ($O(m^\ell)$) certifies the
    constant-$\ell$ fragment only.

A positive fragment thus survives, now on solid ground: at constant
$\ell$, CRT-DQI state preparation is poly-time with provably unique
uncomputation. But…

**(iii) The margin computation forces linear $\ell$.** Setting the
semicircle payoff equal to CRT-Prange: beating
$\kappa + \mu(1-\kappa)$ at fixed $\kappa$ requires
$\ell/m \ge c(\kappa, \mu) > 0$ — e.g. at $\mu = \tfrac12$,
$\kappa = 0.1$: $\ell/m \gtrsim 0.0025$. Tiny constant, but a constant:
**asymptotic advantage needs decoding at sparsity linear in $m$**, where
enumeration is exponential. Exactly parallel to RS-DQI, where
Berlekamp–Massey's algebraic magic — not sparsity alone — delivers linear
radius.

**(iv) The dualization.** Divide by $M$: with $\theta = t'/M$,

$$
\Big|\, \theta - \sum_{i \in S} \frac{k_i}{p_i} \Big| \;\le\; \frac{\Delta}{M}
\approx M^{-\kappa},
\qquad |S| \le \ell
$$

— Q(A2.1) is **sparse rational approximation**: decompose a real number
into at most $\ell$ fractions with denominators from the given set. For
$\ell = 1$ this is continued fractions. And it is precisely the **Fourier
dual of Goldreich–Ron–Sudan decoding**: GRS recovers an integer *small in
value* from residues *corrupted on few moduli*; Q(A2.1) recovers an integer
*sparse in residues* from a value *corrupted by a small shift*. The two
problems swap "small" and "sparse" across the CRT transform — the same
relationship a code bears to its dual.

**The question this leaves (the candidate's new center of mass):** GRS/Boneh
decoding at linear radius exists because $[0, X)$ has lattice structure the
algorithms exploit. Does the dual side admit the same — and here is the
algorithm designer's freedom — **for moduli sets WE design**? RS-DQI works
because Vandermonde structure gives BM decoding; the CRT analogue would be a
modulus design (primes in arithmetic structure? prime powers of one prime?
smooth-plus-structured sets?) making sparse rational approximation
poly-time at $\ell = \varepsilon m$. One suggestive special case to try
first: $p_i$ = powers of distinct small primes vs $p_i = $ consecutive
primes (where density of $\sum k_i/p_i$ values differs sharply).
NP-hardness for *arbitrary* moduli is plausible and worth attempting as the
complementary result (it would mirror "syndrome decoding is NP-hard, RS
decoding is easy" exactly).

## 8. Self-attack (2026-07-07): the natural lattice decoder FAILS

The crux subroutine — the decoder DQI runs coherently to uncompute — is
Q(A2.1) at *linear* sparsity. The RS analogue (Berlekamp–Massey) is
efficient because syndrome decoding of RS duals reduces to it. Does the CRT
analogue reduce to lattice reduction? **We built the natural Kannan-embedding
lattice and ran exact LLL on it** ([`code/lll_decode.py`](../code/lll_decode.py)).
It fails at every sparsity (recovery rate 12–38%, i.e. chance):

| $m$ | $\ell$ | LLL recovery rate |
|---|---|---|
| 12 | 1 | 0.25 |
| 12 | 2 | 0.38 |
| 16 | 1–3 | 0.12 |

**Why — a clean structural obstruction.** A weight-1 integer is
$t = a\,(M/p_j)$. But $p_i\,(M/p_i) = M \equiv 0$, so each
$p_i \cdot e_i$ is a **weight-1 lattice vector of $\ell^2$-norm $p_i$** in
coefficient space — a *non-solution* that LLL prefers whenever
$p_i < |a|$. The modular kernel $\{p_i e_i\}$ is always shorter than the
planted coefficient at the small primes. **$\ell^2$-shortness $\ne$
$\ell^0$-sparsity**, and the kernel pollutes the lattice with short junk.

This is the CRT-side echo of a classical fact: minimum-*Hamming*-weight
decoding is NP-hard in general (Berlekamp–McEliece–van Tilborg) while
minimum-*Euclidean* (lattice) is LLL-able. RS escapes via algebraic
(Berlekamp–Massey) structure, not lattice geometry. CRT has no Vandermonde;
the naive lattice route is blocked.

!!! danger "Consequence for A2 — honest downgrade"

    The crux decoder does **not** come for free from lattice reduction. A2's
    viability now rests entirely on whether an *algebraic* dual-CRT decoder
    exists at linear radius — a genuinely open, possibly hard, question. The
    **constant-$\ell$ fragment stands** (enumeration + the $d_{\min}$
    uniqueness theorem give provably-correct poly-time preparation), but the
    margin computation says constant $\ell$ does **not** beat Prange
    asymptotically. So: A2 is not dead, but it is **gated on one hard
    subroutine**, and the probability I assign to a clean efficient decoder
    existing dropped materially after this attack. Recorded as such.

    *Two escape routes not yet tried, in priority order:* (i) an algebraic
    decoder using the multiplicative structure of $(\mathbb{Z}/M)^\times$
    (the CRT analogue of BM's LFSR-synthesis — does a "rational function
    reconstruction over $\mathbb{Z}$" exist?); (ii) accept list decoding and
    push the list through DQI's uncomputation as a superposition (changes
    the amplitude analysis — may be fatal, may be fine).

## 9. Next actions

1. Await novelty-check agent (kill criterion 3).
2. Attack Q(A2.1): try (i) reduce to known CRT list decoding by re-encoding
   size-noise as residue-noise on auxiliary moduli; (ii) LLL on the lattice
   of $w \le \ell$ patterns near $t'$ for constant $\ell$; (iii) look for an
   NP-hardness reduction at general $\ell$.
3. Human (deferred batch): verify §2–§4 derivations; then DQI §5 at proof
   level side-by-side.
