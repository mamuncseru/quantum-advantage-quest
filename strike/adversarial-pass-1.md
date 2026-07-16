# Adversarial pass 1 — the owed attack, delivered

**Target:** [`crt-dqi-theorem.md`](crt-dqi-theorem.md) as merged 2026-07-11
(master condition, J1/J2 joints, finite-size payoff). **Date:** 2026-07-12.
**Verdict up front: the candidate survives, with two repairs.** One proof
step of Theorem 4.4 is false as written (explicit counterexample below) and
is repaired without weakening the theorem; the coherent-use constant in §5
step 4 must be tightened to a worst-case-branch bound, with the advantage
window unchanged. The owed KOW verdict (§8 row 4) is delivered: **the
dequantization mechanism does not transfer.** Exhibits are executable:
[`attack_cf_uniqueness.py`](../hunt/code/attack_cf_uniqueness.py), pinned
by [tests](../hunt/code/test_attack_cf_uniqueness.py).

---

## Finding 1 — Theorem 4.4's uniqueness step is false; the theorem survives

**The defect.** The proof asserts uniqueness of the accepted candidate via
two claims, both wrong:

1. *"$P_S P_{S'} \le P_{\max}(2\ell)$"* — false whenever supports overlap:
   $S = S' = \{17,19\}$ gives $P_S P_{S'} = 323^2 = 104{,}329 >
   P_{\max}(4) = 46{,}189$ on the validation primes.
2. *"two weight-$\le\ell$ integers within $2\eta M \le d_{\min}(2\ell)$"* —
   the hypothesis $\eta < 1/(2P_S^2)$ does **not** imply
   $2\eta M \le d_{\min}(2\ell)$ when the true support sits on *small*
   moduli ($P_S^2 \ll P_{\max}(2\ell)$).

**The counterexample (E1, executable).** $m=7$, primes $3\ldots19$,
$\ell=2$: $\theta = 43/323$, $\eta = 1/500$ — legal for the true pattern
$2/15$ (support $\{3,5\}$, $\eta < 1/(2\cdot15^2) = 1/450$), since
$|43/323 - 2/15| = 1/4845 \le \eta$. The acceptance rule of step 2 admits
**both** $2/15$ and $43/323$: two accepted candidates, distinct patterns.
Uniqueness, as claimed, is false.

**Why the algorithm survives.** Convergents arrive in increasing
denominator order, and *no spurious candidate with denominator $\le P_S$
can be accepted*: an accepted $h'/q'$ with $q' \le P_S$,
$h'/q' \ne K/P_S$, would satisfy
$1/(P_S q') \le |K/P_S - h'/q'| \le 2\eta < 1/P_S^2 \le 1/(P_S q')$ —
contradiction. The first accepted convergent is therefore the true one,
which is exactly what `cf_decode` returns. **Repaired proof = the
two-line exclusion above + first-accept ordering.** Verified exhaustively:
all 1,940 weight-$\le2$ patterns at boundary noise, 0/5,820 failures (E3);
the no-spurious-accept-below-$P_S$ step checked exhaustively as its own
test.

*Character of the finding:* the theorem's conclusion, the algorithm, and
Corollary 4.5 all stand; the written proof did not. Third instance of this
program's pattern: the code was right, the prose was wrong.

## Finding 2 — the coherent use needs the worst-case constant (and the master condition a companion)

**The hazard (E2, executable).** §5 step 4 runs the decoder *coherently*
with a single $\eta$ across every branch of the superposition. Theorem
4.4's per-instance condition $\eta < 1/(2P_S^2)$ is deceptive there:
with $\eta = 1/500$ (legal for support $\{3,5\}$) a branch carrying the
pattern $43/323$ (support $\{17,19\}$) under noise $|\delta| = 1/4845$
decodes to the **wrong pattern** — the uncomputation would silently
corrupt exactly the large-support branches. Executable: planted
$(0,0,0,0,0,13,7)$, decoded $(1,4,0,0,0,0,0)$.

**The repair.** The uncomputation constant is the worst case over
branches:

$$\eta \;<\; \frac{1}{2\,P_{\max}(\ell)^2}.$$

This implies the per-branch Legendre condition for every support
($P_S \le P_{\max}(\ell)$) *and* branch-pair separation
($2\eta M < M/P_{\max}(\ell)^2 \le M/(P_S P_{S'})$ — which also quietly
replaces the broken $P_{\max}(2\ell)$ claim of Finding 1 in the coherent
setting). Validated exhaustively: 0/3,880 failures at the corrected global
constant (E4). **Window cost: none asymptotically** — for balanced moduli
$P_{\max}(\ell)^2 = M^{2\ell/m}\,e^{O(\ell/\log \bar p)\cdot\log \bar p}$,
so the condition still reads $\ell/m < \kappa/2 - O(\ell \log(c_2/c_1)/(m\log\bar p))$:
the same boundary, with an honest constant-factor edge shift that vanishes
only as $\bar p \to \infty$. The advantage window $(\kappa^2/4, \kappa/2)$
remains nonempty for every $\kappa$ regardless (the shift multiplies the
upper edge by $1-\Theta(1/\log\bar p) > 1/2$ for any sane balancedness).

**Companion inequality for Lemma 6.1.** The boxed master condition
($4\sigma_f R$-term $\le d_{\min}(2\ell+1)$) does *not by itself* imply
the corrected decoder constant: it does iff
$P_{\max}(\ell)^2 \le 2\,P_{\max}(2\ell+1)$, i.e.
$(c_2/c_1)^{\ell} = O(\bar p)$. For tightly-balanced moduli (prime windows
$[\bar p, (1+o(1))\bar p]$) this is automatic; for loosely-balanced sets at
linear sparsity it can fail. **Repair: state the master condition as the
minimum of two inequalities** —
$\sigma_f\sqrt{2\ln(8mN_\ell/\varepsilon)} \le
\min\!\big(d_{\min}(2\ell{+}1)/4,\; M/(2P_{\max}(\ell)^2)\big)$ — or
strengthen "balanced" to $(c_2/c_1)^\ell = O(\bar p)$. Either way the
asymptotic window is unchanged; the boxed form alone was not
self-contained.

## Finding 3 — the KOW verdict (§8 row 4, owed since 2026-07-11): does not transfer

Kothari–O'Donnell–Wu (2510.07515) dequantized CLZ's SIS$_\infty$/CIS
speedups. Mechanism, from the paper: **zero-sum linear algebra plus a
coefficient-halving trick, with inductive dimension reduction** — find
nontrivial zero-sums among $\ge \ell + r$ vectors in an
$\ell$-dimensional space, then iteratively re-express solutions with
halved coefficient ranges ($\pm\lfloor q/2\rfloor \to \pm\lfloor q/4\rfloor
\to \cdots$), projecting and recursing. Three structural requirements, and
CRT-OPI fails each:

1. **Solutions form (a coset of) a linear space.** SIS$_\infty$ asks for
   *any* point of a random lattice inside an $\ell_\infty$ box; solutions
   combine linearly. CRT-OPI's feasible set
   $\{x < X : x \bmod p_i \in F_i \text{ for many } i\}$ has no linear
   structure — sums and differences of good $x$'s are not good.
2. **Feasibility is preserved by coefficient arithmetic.** The halving
   trick lives on the interval structure of the $\ell_\infty$ ball
   (closed under averaging/halving). Dense arbitrary target sets
   $F_i \subset \mathbb{Z}_{p_i}$ ($\mu = 1/2$) are closed under *no*
   arithmetic — halving a residue lands outside $F_i$ half the time by
   construction.
3. **The target is feasibility, not a margin.** KOW needed to *hit the
   box once*. CRT-DQI's claim is a payoff **curve** — semicircle vs
   information-set baseline — an average-case optimization margin. A
   KOW-style dequantization of CRT-OPI would have to *beat CRT-Prange*,
   i.e., solve large-list list-recovery of CRT codes above the
   information-set bound, for which (§8 row 2) no classical literature
   exists.

**Verdict: row 4 is passed for this pass.** The window step's
"neighborhood" worry also resolves: KOW dequantized the CLZ *problems*,
not Gaussian-state preparation in general — window states are commodity
components (standard since Regev), and the load-bearing quantum step in
CRT-DQI is the $\ell$-shell interference it shares with mainline DQI.
**The honest residual is family-coupling, not KOW:** if RS-OPI's
semicircle margin ever falls classically, CRT-OPI falls the same day by
the dictionary — the candidate's fate is tied to the flagship's, which is
precisely why row 3 ("CF empowers the classical attacker too") remains
the attack to keep hammering. Nothing in this pass advanced row 3 in
either direction.

## What this pass did *not* do

- **J1 (shell-state preparation) is untouched** — still the one genuine
  hole, still a sketch.
- **J2's Poisson bookkeeping** was not re-derived line-by-line (human
  batch item); the exhibits here only stress the decoder face.
- **No hardness progress** — row 5 unchanged, as it must be until the
  Hunt's reduction program says otherwise.

## Ledger disposition

**Keep, repaired.** Two textual repairs applied to the theorem document
(§4.4 proof, §5/§6 constants); no kill criterion fired; the advantage
window survives both repairs unchanged. The candidate remains gated on J1
and the human verification batch — unchanged from 2026-07-11, now with
one fewer unexamined attack surface.
