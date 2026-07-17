# JOINT J1 closed: the shell-state preparation lemma

**The written-lemma debt of [`crt-dqi-theorem.md`](crt-dqi-theorem.md) §5.1,
paid: statement, proof, costs, and exact end-to-end validation.**
*2026-07-12. AI-proved; human verification batch still owed, as for
everything in Phase 3.*

The sketch said "believed routine." Writing it out surfaced one genuinely
hidden ingredient — a two-way normalization cancellation (Sub-lemma 2
below) that the phrase "the composition must reproduce the shell weights"
was quietly assuming. It is true, it is provable in four lines, and it is
exactly the kind of thing the April-2024 LWE episode teaches you to write
down before believing.

## 1. Statement

**Lemma J1.** Fix pairwise-coprime moduli $p_1,\dots,p_m$ with explicit
target sets $F_i \subseteq \mathbb{Z}_{p_i}$ (input size
$\Theta(\sum_i p_i)$), a degree $\ell \le m$, and a unit weight vector
$(w_0,\dots,w_\ell)$. Let
$g_i = (\mathbb{1}_{F_i} - \mu_i)/\sqrt{\mu_i(1-\mu_i)}$ and let
$|\hat h_i\rangle$ be the **unit-normalized** DFT of $g_i$
($\hat h_i \propto \widehat{g_i}$, $\|\hat h_i\| = 1$, and
$\hat h_i(0) = 0$ because $\sum_r g_i(r) = 0$). Then a circuit of

$$O\!\Big(m\ell + \sum_i p_i\Big) \text{ rotations}
\;+\; O(m\,\mathrm{poly}\log)$$

prepares, **exactly** in the ideal-gate model (and to trace distance
$\varepsilon$ with the standard $\mathrm{polylog}(1/\varepsilon)$
synthesis overhead), the state on the mixed-radix pattern register
$Y = \bigotimes_i \mathbb{Z}_{p_i}$:

$$
|\Psi_\ell\rangle \;=\; \sum_{k=0}^{\ell} w_k \binom{m}{k}^{-1/2}
\sum_{|S| = k} \;\sum_{\substack{(k_i)_{i \in S}\\ k_i \ne 0}}
\prod_{i \in S} \hat h_i(k_i)\, \big|y(S,(k_i))\big\rangle,
$$

with **no cross-normalization error**: each $(k,S)$ branch carries
amplitude exactly $w_k\binom{m}{k}^{-1/2}\prod \hat h_i(k_i)$, all
ancillas returned to $|0\rangle$ exactly. Moreover (Sub-lemma 2) the
inverse QFT over $\mathbb{Z}_M$ of the frequency embedding of
$|\Psi_\ell\rangle$ is pointwise proportional to

$$
\sum_{k=0}^{\ell} w_k \binom{m}{k}^{-1/2}
e_k\big(g_1(x),\dots,g_m(x)\big),
$$

the **unweighted** elementary-symmetric polynomial in the standardized
constraint functions — the object Claim 7.1's payoff analysis assumes.

## 2. Sub-lemma: the $\sqrt{p_i}$ cancellation (the hidden content of (iii))

With the unitary DFT convention
$\widehat{g}(k) = p^{-1/2}\sum_r g(r)\omega_p^{-kr}$:

1. $\|\widehat{g_i}\|^2 = \sum_r g_i(r)^2 = p_i$ — standardization gives
   variance 1 *per point*, hence total norm $\sqrt{p_i}$, **not** 1. So
   the prepared unit state is $\hat h_i = \widehat{g_i}/\sqrt{p_i}$.
2. The per-coordinate inverse DFT produces the inverse factor:
   $\sum_k \widehat{g_i}(k)\,\omega_{p_i}^{kx} = \sqrt{p_i}\, g_i(x)$,
   hence $\sum_k \hat h_i(k)\,\omega_{p_i}^{kx} = g_i(x)$ exactly.
3. Under the frequency embedding $t = \sum_{i\in S}(M/p_i)k_i$ the
   $\mathbb{Z}_M$-character factorizes over coordinates,
   $\omega_M^{tx} = \prod_{i\in S}\omega_{p_i}^{k_i x}$, so
   $\big(F_M^\dagger\, \Psi\big)(x) = M^{-1/2}\sum_k w_k\binom{m}{k}^{-1/2}
   \sum_{|S|=k}\prod_{i\in S} g_i(x)$. $\square$

The $1/\sqrt{p_i}$ from normalizing each coordinate state cancels the
$\sqrt{p_i}$ the inverse QFT emits per coordinate — *uniformly in $S$*.
Had one prepared $\widehat{g_i}$-proportional states with any other
normalization split, the $x$-side would carry $S$-dependent
$\prod_{i\in S}\sqrt{p_i}$ weights and the semicircle analysis (which
needs the plain $e_k$ of *standardized, independent* variables — CRT
supplies the independence) would silently break for unbalanced moduli.
This is the sentence the sketch owed.

## 3. The construction and proof

Registers: $W$ (dimension $\ell+1$), count $C$ (dimension $\ell+1$),
mask $B$ ($m$ qubits), pattern $Y = \bigotimes_i \mathbb{Z}_{p_i}$.

- **A — weights.** Prepare $\sum_k w_k|k\rangle_W$: one
  $(\ell{+}1)$-dimensional state preparation, $O(\ell)$ rotations.
- **B — count-controlled Dicke scan.** For $i = 1..m$: rotate $B_i$ by
  the angle with $\sin^2\theta_{k,c,i} = (k-c)/(m-i+1)$, controlled on
  $(W{=}k, C{=}c)$; then $C \mathrel{+}= B_i$. By the hypergeometric
  recursion this puts, for each $k$, exactly
  $\binom{m}{k}^{-1/2}\sum_{|S|=k}|S\rangle_B$ with $C = k$ on every
  branch; uncompute $C$ against $W$. ($O(m\ell)$ controlled rotations;
  this is the standard Dicke construction, alphabet-independent as the
  sketch claimed.)
- **C — coordinates.** For each $i$: controlled on $B_i = 1$, apply
  $U_i : |0\rangle_{p_i} \to |\hat h_i\rangle$ ($O(p_i)$ rotations by
  generic state preparation; amplitudes classically precomputed by FFT in
  $O(p_i\log p_i)$). *Isometry argument:* each $U_i|0\rangle$ is a unit
  vector on a fresh register, so every $(k,S)$ branch keeps its amplitude
  $w_k\binom{m}{k}^{-1/2}$ verbatim and acquires exactly
  $\prod_{i\in S}\hat h_i(k_i)$ — this is claim (iii), and it is *purely*
  the unit-norm property plus orthogonality of distinct $(k,S)$ branches.
- **D — uncompute the crutches.** $B_i \mathrel{\oplus}= [Y_i \ne 0]$ is
  exact on every branch: for $i \in S$ the amplitude at $k_i = 0$ is
  $\hat h_i(0) = 0$ (recentring), for $i \notin S$ the register is
  $|0\rangle$. Then $W \mathrel{-}= \mathrm{wt}(Y) \bmod (\ell{+}1)$,
  exact for the same reason. All ancillas land on $|0\rangle$ with zero
  residual amplitude; the pattern register carries $|\Psi_\ell\rangle$.
  $\square$

**Costs.** Rotations: $O(\ell) + O(m\ell) + O(\sum_i p_i)$; classical
precompute $O(\sum_i p_i \log p_i)$. Everything is polynomial in the input
size $\Theta(\sum_i p_i)$ — the explicit-list input model is the one the
problem definition (§1) already uses. Precision: $N = O(m\ell + \sum p_i)$
rotations each synthesized to $\varepsilon/N$; errors add subadditively.
(For *succinctly specified* $F_i$ one would need amplitude-oracle access
in place of step C — flagged, not needed for the theorem.)

**The $k=0$ branch, for the record.** $|\Psi_\ell\rangle$ contains the
empty pattern with amplitude $w_0$; downstream, its frequency is $t = 0$
and the decoder sees $\theta \approx 0$. Under the coherent constant
$\eta < 1/(2P_{\max}(\ell)^2)$ no convergent can be accepted there (any
candidate $h/q$, $q > 1$ smooth has $|h/q| \ge 1/P_{\max}(\ell) > 2\eta$),
so the "no accept $\Rightarrow$ empty pattern" convention is sound —
validated below.

## 4. Validation (exact, not sampled)

[`j1_shell_state.py`](../hunt/code/j1_shell_state.py) simulates the actual
register-level construction (A–D as written, including the count scan and
both uncomputations) at $m=3$, primes $\{3,5,7\}$, $\ell=2$, and checks
against ground truth with no sampling; 5 pinning
[tests](../hunt/code/test_j1_shell_state.py):

| Check | Result |
|---|---|
| circuit route vs definition, max amplitude diff | $5.6\times10^{-17}$ |
| ancillas $(W, C, B)$ disentangle | zero residual (asserted) |
| state norm | $1$ to $10^{-12}$ |
| inverse QFT vs $\sum_k w_k\binom{m}{k}^{-1/2}e_k(g)$, pointwise | $5.0\times10^{-15}$ |
| payoff of prepared state at optimal $w$ vs pencil top eigenvalue | $2.2\times10^{-15}$ |
| $k=0$ convention (no accept at $\theta\approx0$, coherent $\eta$) | holds |

The payoff row is worth noting: it is Claim 7.1's finite-size
$\mathsf{SC}_{m,\ell}$ *realized by the constructed state* — the first
end-to-end check that preparation, dictionary, and payoff meet in the
middle.

## 5. Status

- §5 step 1 / JOINT J1: **closed at this program's level of rigor** —
  construction sketch upgraded to lemma + proof + exact validation.
- What it does *not* close: the human verification batch (§8 row 6) now
  owes this lemma too; and the constants here are ideal-gate — fault
  tolerance is [another catalog's](../machines/gap.md) problem.
