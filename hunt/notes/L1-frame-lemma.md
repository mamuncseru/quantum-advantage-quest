# L1 — the (⇒) direction: fast preparation collapses the memory advantage

**2026-07-11.** The L1 conjecture is an equivalence: *memory advantage on
Gibbs data ⟺ preparation hardness*. This note proves the easy half —
**(⇒): efficient preparation ⇒ no memory advantage** — modulo one clearly
stated caveat. The hard half (⇐) stays open. Proving (⇒) turns L1 from a
slogan into a theorem with one side done.

## Statement

**Lemma (preparation kills the memory advantage).** Fix a family of
Gibbs states $\rho_\beta = e^{-\beta H}/Z$ of geometrically-local
Hamiltonians on $n$ qubits. Suppose:

- **(Learnable)** single-copy measurements on $\mathrm{poly}(n)$ copies
  of $\rho_\beta$ output $\hat H$ with $\|\hat H - H\| \le \delta$
  (Anshu–Arunachalam–Kuwahara–Soleimanifar; Chen–Anshu–Nguyen for the
  local-and-efficient version);
- **(Preparable)** there is a $\mathrm{poly}(n, 1/\varepsilon)$-time
  quantum procedure preparing $\hat\rho_\beta$ with
  $\|\hat\rho_\beta - \rho_{\beta}(\hat H)\|_1 \le \varepsilon$ (e.g. a
  Gibbs sampler whose mixing time is $\mathrm{poly}(n)$ — the
  fast-mixing regime).

Then for any $k$-copy learning task $T$ (estimate a functional
$\Phi(\rho_\beta)$ to accuracy $\alpha$) that a $k$-copy protocol solves
with $N$ copies of the *true* $\rho_\beta$, a **single-copy** learner
solves $T$ to accuracy $\alpha + O(k(\delta' + \varepsilon))$ using
$\mathrm{poly}(n) + N\cdot k$ *self-prepared* copies and no access to
nature beyond the learning phase — where $\delta'$ is the Lipschitz
transfer of the $\hat H$ error onto $\rho_\beta$.

*In words:* once you can learn the Hamiltonian and prepare the state, you
manufacture your own copies and run the $k$-copy protocol on them. The
"quantum memory advantage" evaporates because the single-copy learner
reconstructs the resource that the $k$-copy learner got from nature.

## Proof

1. **Learn.** Spend $\mathrm{poly}(n)$ single-copy measurements to get
   $\hat H$, $\|\hat H - H\| \le \delta$ (Learnable).
2. **Transfer the error to the state.** Gibbs states are Lipschitz in the
   Hamiltonian at fixed $\beta$: $\|\rho_\beta(\hat H) -
   \rho_\beta(H)\|_1 \le \delta' := c(\beta, \text{locality})\,\delta$
   (strong convexity of the log-partition function — the same AAKS
   ingredient, run forward). At high temperature $c$ is a constant; at
   low temperature $c$ can grow, which is where the caveat below bites.
3. **Prepare.** Produce $M' = Nk$ copies of $\hat\rho_\beta$, each
   $\varepsilon$-close in trace distance (Preparable).
4. **Simulate the protocol.** Run the given $k$-copy protocol on batches
   of $k$ self-prepared copies. Each $k$-tuple differs from a true
   $k$-tuple by $\le k(\delta' + \varepsilon)$ in trace distance
   (triangle + subadditivity over the tensor factors), so any measurement
   statistic shifts by $\le k(\delta' + \varepsilon)$; the estimate of
   $\Phi$ shifts by the same up to $\Phi$'s Lipschitz constant. $\square$

## The caveat, stated honestly

The reduction's error is $k(\delta' + \varepsilon)$, and **$\delta'$ can
be large at low temperature**: near a phase transition or in a glassy
regime, a small Hamiltonian error moves the Gibbs state by $\Omega(1)$
(susceptibility diverges). So (⇒) is clean in the **fast-mixing /
high-temperature regime** — exactly where Preparable holds with a benign
constant — and *degrades precisely where the (⇐) direction expects the
advantage to appear.* This is not a bug in the lemma; it is the
equivalence showing its seam. The two directions meet at the mixing
transition:

| regime | preparation | $\delta'$ transfer | verdict |
|---|---|---|---|
| high $T$ / fast mixing | poly (Preparable ✓) | $O(1)$ constant | **(⇒) bites: no advantage** |
| low $T$ / slow mixing | superpoly (Preparable ✗) | can diverge | (⇒) vacuous; (⇐) territory |

## What this buys the candidate

- L1's equivalence now has a **proven forward direction** with an
  explicit regime of validity — publishable as-is as "quantum memory
  gives no asymptotic advantage for learning functionals of
  fast-mixing Gibbs states."
- It sharpens the target for (⇐): the hard direction must exhibit a
  family where preparation is *provably* hard (Rajakumar–Watson tier)
  AND the functional is memory-estimable but single-copy-hard — and the
  caveat says to look at the low-temperature side of a mixing transition,
  which is exactly [[L5|L5-noise-threshold.md]]'s tension regime. **L1
  and L5 now point at the same regime from opposite motivations** —
  strong evidence it is the right place to dig.

## Next

- Make step 2's $\delta'(\beta)$ explicit for the disordered Heisenberg
  chain (susceptibility bound) — numerically first, then the
  cluster-expansion statement at high $T$.
- State (⇐) as a formal conjecture with the Rajakumar–Watson hardness
  plugged in; identify the functional (Rényi-2 is the working example).
