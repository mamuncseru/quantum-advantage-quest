# L1 — Quantum memory on physical data: learning advantage ⟺ preparation hardness?

**Pre-registered 2026-07-11.** New ground **L** (learning with quantum
data) — opened on request, with the graveyard sign read aloud first:

!!! warning "Graveyard compliance"

    This is **not** QML-on-classical-data (banned: Tang's mirror). The
    data here is *quantum states handed over by nature* — Gibbs states of
    a lab system — and the comparison is single-copy vs multi-copy
    measurements, the one arena with unconditional exponential
    separations (Huang–Chen–Preskill). Access-model symmetry enforced:
    the single-copy side gets a full quantum computer.

## The observation that seeds the candidate

HCP-type sample-complexity separations (purity, shadow tomography of all
Paulis) are proven over **adversarial ensembles** — Haar-random states,
random Pauli channels. Physical data is not adversarial:

> **Collapse lemma (assembled from known results).** For Gibbs states of
> spatially local Hamiltonians, single-copy measurements learn the full
> parameter vector with polynomially many samples
> ([Anshu–Arunachalam–Kuwahara–Soleimanifar, Nature Physics 2021](https://arxiv.org/abs/2004.07266):
> strong convexity of the log-partition function;
> [Chen–Anshu–Nguyen, FOCS 2025](https://anuraganshu.seas.harvard.edu/publications/quantum-many-body-systems)
> make it local and efficient). The Hamiltonian determines every
> functional of the state. Hence **no sample-complexity separation
> survives on Gibbs data** — anything two-copy measurements estimate,
> a single-copy learner can *in principle* compute from
> $(\hat H, \beta)$.

"In principle" is doing loud work: computing $\mathrm{Tr}\,\rho_\beta^2$
from $\hat H$ means evaluating partition-function-type quantities —
classically hard in general. The single-copy learner's honest escape is
to **rebuild** $\rho_\beta$ on its quantum computer and swap-test its own
copies — and rebuilding is Gibbs preparation, whose cost is the mixing
time (ground C!). Meanwhile the two-copy learner gets nature's copies for
free. So on physical data:

> **The L1 conjecture.** Quantum-memory advantage for learning
> functionals of Gibbs states is *equivalent to* Gibbs-preparation
> hardness of the family: (⇐) slow mixing + free natural copies ⇒
> two-copy wins computationally; (⇒) fast preparation ⇒ rebuild-and-swap
> matches any multi-copy protocol up to poly overhead. **"Nature as the
> Gibbs sampler" is the resource being measured.**

The separation, where it exists, is **computational, not
sample-theoretic** — the exact opposite of the HCP regime, and a bridge
that gives C1's mixing-time atlas a second payoff channel: every
slow-mixing family C1 maps is a candidate memory-advantage family for L1.

## Task instance (concrete)

Estimate $\mathrm{Tr}\,\rho_\beta^2$ (Rényi-2 entropy) of a lab system in
thermal equilibrium to constant relative error.

- **Two-copy protocol:** swap test on pairs of natural copies —
  $O(1/\varepsilon^2)$ samples, $O(n)$ gates, *independent of n*. (This
  is not hypothetical; it is how cold-atom experiments measure Rényi-2.)
- **Single-copy protocols:** (i) classical shadows — variance
  exponential in $n$ for generic states; (ii) AAKS: poly samples, then a
  partition-function computation — classically hard at low $T$; (iii)
  learn $\hat H$, prepare $\rho_\beta$ quantumly, swap-test — cost =
  mixing time of the preparation algorithm.

## The advantage window (three walls, each falsifiable)

The family must simultaneously be:

1. **Slow-mixing** (else rebuild-and-swap, conjecture direction ⇒):
   kills fast-mixing families — 1D at all T
   ([arXiv 2510.08533](https://arxiv.org/pdf/2510.08533)), anything at
   high T, C1's strong-disordered-field regime (our own gap data shows
   the Davies gap open there — that regime is *dead for L1*).
2. **Not single-copy tomographable** (else learn the state directly):
   kills 1D area-law states (MPS tomography), stabilizer-ish and
   Gaussian-ish families.
3. **Not classically computable from $\hat H$** (else AAKS + classical
   evaluation): kills high-T (cluster expansions for
   $\mathrm{Tr}\rho^2$), sign-problem-free models (QMC).

Window = **low-temperature, ≥2D or long-range, glassy/slow-mixing** —
precisely where Rajakumar–Watson-type conditional hardness for Gibbs
sampling lives. The conjecture inherits its assumptions; nothing here is
unconditional, and the brief says so.

## Pre-registration

- **Advantage currency:** computational separation for a natural learning
  task with natural quantum data access, conditional on Gibbs-preparation
  hardness (Rajakumar–Watson tier) — plus the (⇒) direction as an
  unconditional *equivalence theorem* target.
- **Kill criteria:**
    1. **Lit check (cheapest, first):** the equivalence framing published
       anywhere ⇒ fold into study notes, close as candidate. First pass
       (2026-07-11) found the pieces (AAKS; HCP; Rajakumar–Watson;
       [cloning≡learning for stabilizers](https://arxiv.org/pdf/2604.15269)
       is adjacent in spirit) but not the composite. Deep pass owed.
    2. **The (⇒) direction fails:** a multi-copy protocol on Gibbs data
       that beats rebuild-and-swap *without* preparation hardness — would
       break the equivalence (and be interesting on its own).
    3. **The window is empty:** every slow-mixing family in reach is also
       single-copy-computable (wall 2 or 3 closes whenever wall 1 opens).
       Two consecutive reviews with no family clearing all three walls ⇒
       park.
- **Classical/access honesty:** the single-copy side always gets full BQP
  compute; "advantage" never means "we forbade the baseline a tool."

## First numerics (2026-07-11, same session)

[`code/memory_purity.py`](code/memory_purity.py) (4 tests): Rényi-2 to
$\varepsilon = 0.05$ on disordered-Heisenberg Gibbs states ($\beta = 1$).
Two-copy swap cost stays at ~330 samples for every $n$; the single-copy
shadow cost doubles at **2.2 bits per qubit** — ratio $\approx 2.2\times
10^4$ already at $n = 8$ (heavy-tail caveat: the U-statistic's mean
deviations at large $n$ sit within one standard error; it is exactly
unbiased). This is the raw memory gap the collapse lemma says must be
*rerouted through computation* on physical data — AAKS gets the samples
down to poly, and then the cost reappears as Gibbs
preparation/partition-function work. The frame in one table, on our own
stack.

## First actions
2. Draft the (⇒) direction as a lemma: fast preparation ⇒ single-copy
   simulates multi-copy learning with poly overhead (should be a
   clean simulation argument; the subtlety is sample reuse vs fresh
   copies).
3. Find one family clearing all three walls (start: 2D disordered
   models at low T; C1's knobs transplanted off the chain).
4. Deep novelty pass (kill 1).
