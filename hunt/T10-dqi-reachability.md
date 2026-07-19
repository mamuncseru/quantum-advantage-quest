# T10 — Variational reachability of DQI payoffs

**Opened and resolved 2026-07-18** (ground T, taken out of map order as
the last substantive slot — the one connecting this ground to
[A2/STRIKE](../strike/crt-dqi-theorem.md)). **Verdict: K1 fires at toy
scale — no separation is decidable there — and the question hands off
to theory at DQI's true parameter regime.** Along the way, the ground's
recurring lesson fired a third time: schedules beat training.

## The question

DQI reaches its semicircle payoff by a closed-form interference
construction. Can *variational* circuits find the same payoff by
training — or is the construction necessary? A clean separation
("trained QAOA provably plateaus below the shell curve") would be a
strong structural statement for A2; clean reachability would say DQI's
edge is constructive convenience.

## Instrument and results (n = 12, m = 24 random weight-3 max-XORSAT)

Exact by enumeration: the ideal $\ell$-shell payoff curve (Jacobi
pencil, the J1-validated machinery) — 0.602 / 0.674 / 0.726 / 0.762
for $\ell = 1..4$ ($f_{\max}/m = 0.833$, random = 0.5). Code:
[`code/t10_dqi_reachability.py`](code/t10_dqi_reachability.py), 5
[tests](code/test_t10_dqi_reachability.py).

| strategy | best $\langle f\rangle/m$ |
|---|---:|
| trained QAOA, $p \le 6$, 12 starts × 300 steps | 0.656 (p=4; **glassy**: p=2,3,6 landed *below* p=1) |
| layer-wise warm-started chain, $p \le 8$ | 0.578 (a bad seed poisoned the chain) |
| **linear-ramp schedule, 2 parameters, no training** | **0.695 (p=4) → 0.732 (p=8) → 0.753 (p=12)** |

The annealing-inspired ramp — a two-hyperparameter family requiring no
gradients and no landscape — **exceeds the ideal $\ell=3$ shell payoff**
that seventeen gradient-trained starts never approached. The trained-
QAOA shortfall was optimizer glass, not expressivity (the depth-
nonmonotonicity was the tell, and the instrument's own history — the
T3 SPSA artifact — mandated the schedule baseline before any claim).

## Verdict

1. **K1 fires at toy scale:** the DQI shell curve is reachable (and
   exceeded) by digitized-annealing QAOA at trivial depth on instances
   this size. **No variational-reachability separation exists at
   $n=12$ random 3-XORSAT** — the toy is simply too easy: SAT-adjacent
   instances are exactly annealing's home turf, and the decodable-$\ell$
   regime of a random weight-3 code is tiny anyway.
2. **The real question is out of toy reach and becomes a theory
   target:** DQI's advantage regime (OPI/CRT at rate $\kappa$, the
   semicircle-vs-Prange gap of [A2](A2-objective-code-reductions.md))
   is where the DQI paper itself reports QAOA falling short. Whether
   annealing-schedule families also plateau *there* is a landscape-
   theory question about spectral gaps along the anneal path on
   planted-code objectives — logged as a **STRIKE-side follow-up**
   (it strengthens or contextualizes A2's write-up), not a T-slot.
3. **The ground's lesson, third firing:** T6's random search beat
   gradients; T10's fixed schedules beat gradients. Across ground T,
   whenever a quantum resource was real, the *variational* layer on
   top of it was never the load-bearing part.

## Ledger discipline

Same-day open-and-resolve; the instrument survives (pencil curve +
QAOA arms + budget tie-in, all exact-checked); the question's hard core
is re-filed where it belongs (A2 theory), and ground T's substantive
slate is complete.
