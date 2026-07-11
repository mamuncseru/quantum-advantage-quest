# L10 — The QUALM gap on physical dynamics: temporal coherence as the resource

**Pre-registered 2026-07-11**, ground L.
[Aharonov–Cotler–Qi](https://arxiv.org/abs/2101.04634) (Nat. Comm. 2022)
proved fully **coherent** experimental access to dynamics is exponentially
stronger than adaptive **incoherent** access — for adversarial unitary
ensembles (their tasks: time-independence testing, symmetry-class
determination). The ground-L question, one more time: what survives on
*physical* dynamics (local, learnable generators)? The collapse pressure
is strong (short-time Hamiltonian learning parameterizes closed
dynamics); the residue must live where the generator is **not**
learnable: open/non-Markovian evolution — which is where L2's suspect 1
already produced a signal.

## First numerics (this session — doubles as L2's pre-registered T-scan)

[`code/qualm_scaling.py`](code/qualm_scaling.py): the non-Markovian dyad
at $T = 2, 3, 4$ steps. Coherent-access Fisher information grows as
$F_B = T^2/2$ (temporal Heisenberg compounding) while the best
measure-and-reprepare protocol grows sublinearly:

| $T$ | best incoherent FI | coherent FI | ratio |
|---|---|---|---|
| 2 | 0.500 | 2.0 | 4.0 |
| 3 | 0.750 | 4.5 | 6.0 |
| 4 | 1.018 | 8.0 | **7.9** |

**The ratio grows** — L2's kill-2 question ("does the edge saturate?")
answers *no* at these sizes. Honest reading: $T^2$ growth is
metrology-grade (quadratic), not yet QUALM-grade (exponential); the
exponential regime needs bath *structure* that incoherent probes cannot
resolve at any polynomial order — that construction is the candidate.

## Pre-registration

- **Deliverable:** either a physically-motivated process family
  (structured bath, $\mathrm{poly}(n)$ description) with superpolynomial
  coherent/incoherent separation — the QUALM mechanism made physical —
  or the collapse theorem for efficiently-parameterized process tensors
  (the L-pattern negative, certifying incoherent process tomography).
- **Kills:** (1) comb-SDP shows the dyad family's edge is capped at
  $T^2$ for all baths of bounded dimension (then the candidate needs
  growing baths — reassess scope); (2) the replica-hierarchy line
  ([2111.05874](https://arxiv.org/pdf/2111.05874)) or QUALM follow-ups
  already treat structured ensembles — deep lit pass; (3) merge with L2:
  if the only live residue is non-Markovian noise learning, L10 *is*
  L2's suspect 1 — fuse after the review.
- **First actions:** comb-SDP bound for the dyad (rigorous protocol-free
  comparison); bath-dimension scan; deep lit pass.
