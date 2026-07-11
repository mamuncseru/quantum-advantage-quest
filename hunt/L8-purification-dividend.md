# L8 — The purification dividend: entropy tasks and the access hierarchy

**Pre-registered 2026-07-11**, ground L. The converse sandwich to
[[L1|L1-memory-vs-mixing.md]]: L1 says *slow* mixing makes nature's
copies precious (memory advantage); L8 says *fast* mixing makes the
**preparer** strictly stronger than any copy-consumer — because
preparation upgrades the access class.

## The mechanism

Entropy and free energy need $\log Z$. From copies at one fixed
$\beta$ — all nature ever provides — even unlimited quantum memory faces
the known exponential sample bounds for spectrum-dependent quantities.
A learner who can *prepare* (fast mixing, or learned $\hat H$ + a rapid
sampler) manufactures copies along a temperature **schedule** and
telescopes

$$\frac{Z(\beta_{i+1})}{Z(\beta_i)} = \mathbb{E}_{\rho_{\beta_i}}
\big[e^{-(\beta_{i+1}-\beta_i)H}\big],$$

turning free-energy/entropy estimation into $K$ bounded-variance
measurements. Exact numerics
([`code/ratio_telescope.py`](code/ratio_telescope.py), $n=5$,
$\beta = 2$): the single-jump estimator has relative variance 21; a
32-step schedule brings the *total* to 0.49 — every factor tame. The
dividend belongs to whoever can re-prepare at intermediate temperatures;
fixed-$\beta$ copies cannot telescope.

## The candidate

> **The mixing-time sandwich.** On thermal data, the resource landscape
> is controlled by one dial: preparation cost. Slow mixing ⇒ two-copy
> memory advantage on nature's copies (L1). Fast mixing ⇒ preparer's
> access-upgrade advantage for spectrum tasks (this brief). Formalize
> both directions into a single theorem: *for every task in a natural
> class, the optimal protocol's structure is determined by the mixing
> time* — the first complete resource map for learning from thermal
> equilibrium.

## Pre-registration

- **Kills:** (1) fixed-$\beta$ copies secretly suffice for entropy under
  the Gibbs promise at subexponential cost (would break the sandwich's
  right side — check the copy-complexity literature for
  promise-restricted bounds, cheapest kill); (2) the sandwich statement
  is already assembled somewhere (deep lit pass); (3) two reviews
  without theorem progress → fold into L1 as its converse annex.
- **First actions:** promise-restricted entropy copy-bound literature
  check; write the sandwich as two lemmas with explicit task classes;
  the $\beta$-schedule length vs mixing-gap tradeoff (ties to C1's gap
  data directly).
