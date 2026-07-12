# CRT-DQI: the construction, stated as a theorem

**Phase 3 (STRIKE) opened 2026-07-11.** This document is the load-bearing
statement of candidate A2 — every claim with explicit constants, every
gap named. It supersedes nothing (the [derivation
note](../hunt/notes/A2-crt-opi-derivation.md) keeps the history and the
failed attacks) but it is the thing to attack, verify, and eventually
publish.

!!! danger "Epistemic status — read before citing anything here"

    Derived and computationally validated by the AI; **not yet verified by
    a human at proof level** (deferred batch, per program directive).
    §4 and §6 are complete proofs; **§5 (state preparation) is a
    construction sketch, not a proof** — it is the largest remaining hole.
    A dedicated adversarial pass is running in parallel. Any statement
    below inherits DQI's own honesty note (§8): there is no
    complexity-theoretic hardness theorem for the underlying optimization
    problem, and "advantage" always means *versus the best classical
    algorithm we and the literature could find*.

## 1. The problem

**Definition (CRT-OPI).** Fix pairwise-coprime moduli
$p_1 < \dots < p_m$, all within a constant factor of a scale $\bar p$
(*balanced*), $M = \prod_i p_i$. Fix target sets
$F_i \subseteq \mathbb{Z}_{p_i}$ with densities
$\mu_i = |F_i|/p_i$, and a rate $\kappa \in (0,1)$ with $X = M^\kappa$.
Maximize

$$
f(x) \;=\; \sum_{i=1}^{m} \mathbb{1}\big[\,x \bmod p_i \in F_i\,\big],
\qquad x \in [0, X).
$$

Write $\mu$ for the common density (take $\mu = 1/2$ throughout; the
general case only changes constants).

**Why this problem.** It is the Chinese-remainder twin of the *Optimal
Polynomial Intersection* problem — the one DQI regime that remains
unbroken as of the 2026 literature sweep. The dictionary: evaluation
points $\to$ moduli, polynomials of degree $< n$ $\to$ integers $< X$,
Reed–Solomon codes $\to$ CRT codes, rate $n/m \to \kappa$. Under this
dictionary CRT-OPI is the natural "over $\mathbb{Z}$, without field
structure" member of the family, and the novelty check
([note](../hunt/notes/A2-novelty-check.md)) found the point unclaimed.

## 2. The classical baseline (CRT-Prange)

**Proposition 2.1.** The greedy information-set algorithm — take
$S$ with $\prod_{i \in S} p_i \le X$ (so $|S| \approx \kappa m$ for
balanced moduli), pick any $a_i \in F_i$ for $i \in S$, CRT-combine to
get $x < X$ — achieves expected

$$
\frac{\langle f \rangle}{m} \;=\; \kappa + \mu\,(1 - \kappa)
\;=\; \tfrac{1}{2}(1 + \kappa) \quad \text{at } \mu = \tfrac12 .
$$

*Proof.* The $|S|$ chosen constraints are satisfied exactly; the CRT
combination is $< \prod_{i\in S} p_i \le X$; the remaining $m - |S|$
residues are equidistributed over the freedom left, each landing in
$F_i$ with probability $\mu_i$. $\square$

This is the exact analogue of OPI's Prange baseline, and it is the
number to beat. Enhanced-Prange and lattice attacks are inventoried in
§8; none currently beats it in this regime.

## 3. Fourier structure

Characters of $\mathbb{Z}_M$: $\chi_t(x) = \omega_M^{tx}$. Each
constraint indicator has Fourier support in the order-$p_i$ subgroup
$T_i = (M/p_i)\,\mathbb{Z}_{p_i}$, and every $t \in \mathbb{Z}_M$
decomposes **uniquely** as

$$
t \;=\; \sum_{i=1}^m \frac{M}{p_i} k_i \bmod M,
\qquad k_i = t\,(M/p_i)^{-1} \bmod p_i .
$$

Define the **CRT weight** $w(t) = \#\{i : k_i \ne 0\}$. Then any
degree-$\ell$ polynomial in the constraint indicators has Fourier support
exactly in $\{t : w(t) \le \ell\}$ — the precise analogue of DQI's
low-Hamming-weight support, with CRT weight replacing Hamming weight.

## 4. The two structure theorems

**Theorem 4.1 (minimum distance).** For any coprime moduli and any
$1 \le w \le m$,

$$
d_{\min}(w) \;:=\; \min\{\,|t| : 0 \ne t \in \mathbb{Z}_M,\ w(t) \le w\,\}
\;=\; \frac{M}{P_{\max}(w)},
$$

where $P_{\max}(w)$ is the product of the $w$ largest moduli (and $|t|$
means the representative in $(-M/2, M/2]$).

*Proof.* **Lower bound:** if $\mathrm{supp}(t) = S$ then $p_i \mid t$ for
all $i \notin S$, so $t$ is a nonzero multiple of $M/P_S$ where
$P_S = \prod_{i\in S} p_i$; hence $|t| \ge M/P_S \ge M/P_{\max}(|S|)$.
**Upper bound:** fix $S$ = the $w$ largest moduli. The map
$(k_i)_{i\in S} \mapsto \sum_{i \in S} k_i (P_S/p_i) \bmod P_S$ is onto
$\mathbb{Z}_{P_S}$ (CRT), so some choice hits $1$; the corresponding
$t = (M/P_S)\cdot 1$ has weight $\le w$ and $|t| = M/P_{\max}(w)$.
$\square$

**Corollary 4.2 (unique decoding radius).** Two CRT-weight-$\le\ell$
integers differ by a weight-$\le 2\ell$ integer, so patterns are uniquely
determined by any $t'$ within $d_{\min}(2\ell)/2 = M/(2 P_{\max}(2\ell))$
of them.

**Corollary 4.3 (no modulus design is possible or needed).**
$d_{\min}$ depends only on the modulus *sizes*, so every balanced modulus
set is automatically extremal. This is the number-theoretic twin of
"Reed–Solomon is MDS", with CRT playing Vandermonde's role — and it means
the algorithm designer has *no* freedom to exploit here (a negative
result that saves work).

**Theorem 4.4 (the decoder — the crux).** Let $\theta \in [0,1)$ satisfy
$|\theta - t/M| \le \eta \pmod 1$ for some $t$ with $w(t) \le \ell$ and
support $S$, $P_S = \prod_{i \in S} p_i$. If

$$
\eta \;<\; \frac{1}{2 P_S^{2}},
$$

then the following runs in time $O(\mathrm{poly}(m, \log M))$ and outputs
the pattern $(k_i)_{i \in S}$ exactly:

1. expand $\theta$ in continued fractions (exact rational arithmetic);
2. for each convergent $h/q$: accept iff $q$ factors squarefree over
   $\{p_i\}$ with support size $\le \ell$ and the circular distance
   $|\theta - h/q| \le \eta$;
3. output $k_i = h\,(q/p_i)^{-1} \bmod p_i$ for $i$ in that support.

*Proof.* Reduce $t/M$ mod 1: with $S$ the support,
$t/M \equiv \sum_{i\in S} k_i/p_i = K/P_S \pmod 1$ where
$K = \sum_{i \in S} k_i (P_S/p_i)$. **The fraction is automatically in
lowest terms:** for $j \in S$, $K \equiv k_j (P_S/p_j) \pmod{p_j}$ and
neither factor vanishes mod $p_j$, so $p_j \nmid K$; hence
$\gcd(K, P_S) = 1$. By Legendre's theorem, $|\theta - K/P_S| < 1/(2P_S^2)$
with $\gcd(K,P_S)=1$ forces $K/P_S$ to be a convergent of $\theta$, so
step 2 sees it. Uniqueness of the accepted candidate: another accepted
$K'/P_{S'}$ within $\eta$ would give two weight-$\le\ell$ integers within
$2\eta M \le M/P_{\max}(2\ell) = d_{\min}(2\ell)$ of each other,
contradicting Corollary 4.2 (using $P_S P_{S'} \le P_{\max}(2\ell)$).
Step 3 inverts the CRT map on the support. Each step is polynomial:
CF has $O(\log M)$ convergents, trial division is $O(m)$ per convergent.
$\square$

**Corollary 4.5 (the decoder covers the whole information-theoretic
window).** With balanced moduli, $P_S \approx M^{\ell/m}$ and the
condition $\eta < 1/(2P_S^2)$ with $\eta \approx M^{-\kappa}$ reads
$\ell/m < \kappa/2 + o(1)$ — **exactly** Corollary 4.2's uniqueness
radius. There is no algorithmic gap to close: wherever uncomputation is
well-defined, continued fractions decode.

**Remark (why lattices fail and Euclid succeeds).** The natural
coefficient-space lattice attack (Kannan embedding, LLL) *fails at every
sparsity* (measured: 12–38% recovery, i.e. chance) because the modular
kernel $\{p_i e_i\}$ supplies short $\ell^2$-vectors that are $\ell^0$-dense
non-solutions: **$\ell^2$-shortness $\ne$ $\ell^0$-sparsity**. The
CRT-sparse structure is *multiplicative* — a smooth denominator — which
the 2-dimensional lattice reduction that *is* continued fractions sees
directly. The dictionary completes: Berlekamp–Massey is Euclid in
$\mathbb{F}_q[x]$; continued fractions are Euclid in $\mathbb{Z}$.

## 5. The algorithm (construction sketch — the remaining hole)

Given the target degree $\ell = \varepsilon m$ and weights
$(w_k)_{k \le \ell}$ from DQI's optimal-polynomial prescription:

1. **Shell superposition.** Prepare
   $\sum_{|S| \le \ell} \sum_{(k_i)_{i \in S}} \big(\prod_{i\in S}
   \hat g_i(k_i)\big) |S, (k_i)\rangle$ — the CRT analogue of DQI's Dicke
   state over error patterns, with per-coordinate amplitudes
   $\hat g_i$ the Fourier coefficients of $\mathbb{1}[\cdot \in F_i]$.
2. **Frequency computation.** Compute
   $t = \sum_{i \in S} (M/p_i) k_i \bmod M$ into a fresh register.
3. **Window.** Convolve with a discrete Gaussian of frequency width
   $\sigma_f$ (equivalently: prepare the Gaussian in the $x$-basis of
   width $\sigma_x = M/(2\pi\sigma_f)$), giving $t' = t + \delta$ with
   $|\delta| \lesssim \sigma_f\sqrt{\log(1/\varepsilon')}$.
4. **Uncompute.** Run the decoder of Theorem 4.4 coherently on
   $\theta = t'/M$ and erase $|S,(k_i)\rangle$.
5. **Inverse QFT** over $\mathbb{Z}_M$; measure $x$.

**What is proven:** steps 2–4 (Theorems 4.1–4.4 and §6). **What is
sketched:** step 1 at general $\ell$ — DQI's Dicke-state machinery
transplants coordinate-wise and the amplitudes are the same combinatorial
objects, but the *proof* that the CRT shell state is preparable in
$\mathrm{poly}(m)$ with the right normalization is written nowhere in
this repo. **This is the largest open item in the construction.** It is
believed routine (it is the part of DQI that is *not* problem-specific),
but "believed routine" is exactly the phrase that preceded the
April-2024 LWE bug, and it must be written out.

## 6. The window lemma (amplitude bookkeeping)

**Lemma 6.1.** Let the Gaussian window have frequency width $\sigma_f$,
truncated at $C\sigma_f\sqrt{\log(m/\varepsilon)}$. If

$$
C\,\sigma_f\,\sqrt{\log(m/\varepsilon)} \;\le\; d_{\min}(2\ell + 1),
$$

then (i) the prepared state is $\varepsilon$-close to the ideal windowed
state, (ii) the decoder is correct on all but $\varepsilon$ of the
Gaussian mass, and (iii) the expected objective satisfies
$\big|\mathbb{E}[f]_W - \mathbb{E}[f]\big| \le m\varepsilon'$ with
$\varepsilon'$ superpolynomially small in the truncation parameter.

*Proof idea.* By Poisson summation every window-induced correction is a
Fourier coefficient of $W^2$ evaluated at a *nonzero difference of sparse
frequencies*: norm/coherence terms at $\ge d_{\min}(2\ell)$, payoff
cross-terms (the objective's own frequencies have weight 1) at
$\ge d_{\min}(2\ell+1)$, decoder collisions at $\ge d_{\min}(2\ell)/2$.
A Gaussian of width $\sigma_f$ suppresses all of them by
$\exp(-\Omega((d_{\min}(2\ell+1)/\sigma_f)^2))$. $\square$

**Corollary 6.2 (the bookkeeping adds no constraint).** The smallest
window the lemma supports has
$X \approx \sigma_x \,\mathrm{polylog} = M\,\mathrm{polylog}/(2\pi\sigma_f)
\gtrsim M/d_{\min}(2\ell+1) = P_{\max}(2\ell+1)$, i.e.
$\kappa \gtrsim 2\ell/m$ — *the same* $\ell/m \lesssim \kappa/2$ boundary
already imposed by unique decoding.

**Validation (exact, not sampled).** At $\ell = 1$ and $\ell = 2$ on
$m = 7$ (primes 3…19, $M = 4{,}849{,}845$), the windowed and unwindowed
objective agree to $3.3\times10^{-16}$ and $1.4\times10^{-11}$
respectively, with zero decoder failure mass; both stress directions
break **exactly** at the predicted thresholds ($3\sigma_f \approx
d_{\min}(2\ell{+}1)$ on the state side; cut $\approx d_{\min}(2\ell)/2$ on
the decoder side) — measured, not fitted. Code:
[`windowed_payoff.py`](../hunt/code/windowed_payoff.py),
[`windowed_payoff_l2.py`](../hunt/code/windowed_payoff_l2.py).

## 7. The payoff, and the advantage window

**Claim 7.1 (conditional on §5).** CRT-DQI achieves the DQI semicircle
payoff with $\kappa$ in the role of the code rate:

$$
\frac{\langle f \rangle}{m} \;=\;
\Big(\sqrt{\tfrac{\ell}{m}(1-\mu)} + \sqrt{\mu\,(1 - \tfrac{\ell}{m})}\Big)^{2}
\qquad (\mu \le 1 - \ell/m),
$$

for any $\ell/m < \kappa/2$ (Theorem 4.4 + Lemma 6.1). Comparing with
Proposition 2.1 at $\mu = 1/2$, CRT-DQI beats CRT-Prange iff

$$
\boxed{\;\frac{\kappa^2}{4} \;<\; \frac{\ell}{m} \;<\; \frac{\kappa}{2}\;}
$$

— **nonempty for every $\kappa \in (0,1)$**. Example ($\kappa = 0.1$):
any $\ell/m \in (0.0025,\, 0.05)$. The maximum gap over the family,
computed from the verified semicircle tool
([`advantage_window.py`](../hunt/code/advantage_window.py), unit-tested
against the DQI paper's own numbers): **+0.207 at $\kappa \approx 0.29$**
— i.e. the quantum algorithm satisfies ~21% more constraints than the
information-set baseline, the same margin DQI reports for RS-OPI.

## 8. Standing self-attacks (the honest ledger)

| # | Attack | Status |
|---|---|---|
| 1 | Coefficient-space lattice decoder (LLL/Kannan) | **Tried, fails** — and that failure is *explained* (§4 remark), not merely observed |
| 2 | Noisy-CRT lattice attacks (Bleichenbacher–Nguyen, Shparlinski–Steinfeld) | Solve list-*decoding* (one residue per modulus); CRT-OPI at $\mu\approx1/2$ is large-list list-*recovery* ($\ell_{\rm in} \sim p/2$), where GS-type methods are vacuous and **no classical literature exists** |
| 3 | "CF empowers the classical attacker too" | CF solves the *Fourier-side* problem given $\theta$; no classical route is known to the high-payoff $\theta$'s without the quantum interference that concentrates amplitude on them. **This is the attack to keep hammering.** |
| 4 | KOW dequantization of CLZ's SIS$_\infty$ (2510.07515) | The one prior "over $\mathbb{Z}$" claim in this family fell classically. Our window step lives in that neighbourhood — an independent adversarial pass is running specifically on this |
| 5 | Hardness pedigree | **None claimed.** Same epistemic tier as OPI: no complexity-theoretic hardness in-regime; pedigree = the absence of attacks in 25 years of noisy-CRT literature |
| 6 | Human proof-level verification | **Owed.** §4, §6 and this document's §5 gap |

## 9. What must happen before this is a paper

1. **§5 written as a proof** (shell-state preparation at general $\ell$)
   — the one genuine hole.
2. **Human verification batch** — §4 (both theorems), §6, §7.
3. **The adversarial pass** now running must fail to kill it.
4. Deep novelty pass on Theorem 4.4 as a standalone statement (the
   ingredients are textbook; the composite appears unclaimed).

Only then does the phrase "a new quantum algorithm with a plausible
advantage" get used — and even then, with DQI's honesty note attached.
