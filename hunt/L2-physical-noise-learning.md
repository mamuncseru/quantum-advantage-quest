# L2 — Does quantum memory ever help learn *physical* noise?

**Pre-registered 2026-07-11**, ground L, second candidate. Sibling of
[[L1|L1-memory-vs-mixing.md]] one level up the stack: L1 asks the
question for states nature hands you; L2 asks it for the *channels* a
device applies — the theory of noise profiling, HilbertBench's home turf.

## The known map (dense side)

[Chen–Zhou–Seif–Jiang](https://arxiv.org/abs/2108.08488): learning **all**
$4^n$ Pauli eigenvalues to $\pm\varepsilon$ takes $O(n/\varepsilon^2)$
channel uses with an $n$-qubit ancilla but $\Omega(2^{n/3})$ without —
an exponential memory separation, experimentally demonstrated
([Science 2025](https://www.science.org/doi/10.1126/science.adv2560)).
Resource anatomy: the ancilla *count* is fundamental, entanglement
magnitude is not ([arXiv 2507.11089](https://arxiv.org/abs/2507.11089),
Nat. Comm. 2026); logarithmic memory already restructures the task
([PRX Quantum 6, 020323](https://link.aps.org/doi/10.1103/PRXQuantum.6.020323)).

**But the dense task is adversarial.** Physical noise is *sparse*: the
Pauli–Lindblad models actually fitted to hardware carry $s =
\mathrm{poly}(n)$ generators. The separation's home is exactly where
physical noise never lives.

## First result (this session): the constructive collapse

For $s$-sparse error distributions, an **ancilla-free** learner recovers
the full channel in polynomially many uses
([`code/sparse_channel_learn.py`](code/sparse_channel_learn.py), tests):

> Eigenvalues are the Walsh transform of the error distribution,
> $\lambda_b = \sum_a p(a)(-1)^{\langle a,b\rangle}$, and each is
> measurable ancilla-free (stabilizer eigenstate in, Pauli measurement
> out). Because $p$ is a *nonnegative distribution*, the mass of any
> prefix bucket is a plain subgroup average of $\lambda$'s — no
> Goldreich–Levin squaring — so a prefix tree prunes to the $s$ heavy
> branches with $O(m\, s R)$ queries. One variance trick is load-bearing:
> center the queries by $\bar\lambda \approx p(\mathrm{id})$, since the
> identity's weight dominates every eigenvalue and otherwise swamps the
> threshold.

Computed: full support recovery and every parameter within
$\varepsilon = 0.05$ from $n = 4$ to $n = 32$ ($m = 64$), query count
growing $9{,}200 \to 24{,}600$ — polynomial, zero ancillas, including
Lindblad-like low-weight supports. **On sparse channels the exponential
separation collapses**, constructively. (The dense lower bound is
untouched; this is a boundary, not a refutation.)

## The candidate question (what remains after the collapse)

> With sample separations dead on the physical class, is there **any**
> physically-motivated noise family where quantum memory provably helps —
> or is single-copy noise profiling *optimal for all noise that actually
> occurs*?

Live suspects, in order of physical realism:

1. **Temporally correlated (non-Markovian) noise:** the process tensor
   over $T$ steps has genuinely quantum temporal correlations; a learner
   with quantum memory can interrogate them coherently across time steps,
   a single-copy learner cannot. The dense-vs-sparse question recurses
   one level up: physical baths are *structured* process tensors.
2. **Sparse in an unknown basis:** noise sparse after conjugation by an
   unknown (say Clifford) frame — prefix learning needs the frame;
   memory-assisted protocols may not.
3. **Coherent (non-Pauli) errors:** the eigenvalue picture breaks;
   process tomography with vs without entangled probes.

## Pre-registration

- **Advantage currency:** provable sample separation on a family with a
  *physical generating mechanism* (not adversarial), or the negative
  theorem: memory buys at most poly on every family in a formalized
  "physical" class (sparse + low-weight + bounded temporal depth). Both
  are results; the negative one directly certifies single-copy noise
  profiling practice.
- **Kill criteria:**
    1. **Lit check (deep pass owed):** the sparse collapse may be
       folklore or implicit in the Pauli–Lindblad fitting literature
       (van den Berg et al.); the *no-advantage theorem* and the
       non-Markovian boundary appear open — verify.
    2. **Suspect 1 collapses too:** if structured process tensors admit
       single-copy prefix-style learners, the memory advantage retreats
       to adversarial noise entirely → write the negative theorem, close.
    3. Two reviews with neither a separation candidate nor progress on
       the negative theorem → park.
- **Access honesty:** ancilla-free side gets adaptivity and arbitrary
  single-copy input states; no hobbled baselines.

## First actions

1. Deep novelty pass on the sparse collapse + no-advantage formulation.
2. Formalize suspect 1: smallest non-Markovian family (one qubit +
   one bath qubit, $T$ steps) where memory-assisted learning provably
   beats single-copy — or prove it cannot.
3. Connect to HilbertBench: the collapse result, if it holds up, is a
   correctness certificate for single-copy noise-profiling pipelines.
