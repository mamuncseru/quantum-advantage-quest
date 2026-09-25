# T4 — The adaptive face: can the feedback loop outrun the surrogate?

**RESOLVED 2026-07-17, same day: no — K1 fired at its maximum.** The
truncated-propagation surrogate replicates the **entire** ADAPT
construction: selection match **1.00** at every size, both
Hamiltonians, budgets down to N = 512; final true energies agree to
$\le 5\times10^{-4}$ against a tolerance of $0.075$–$0.125$. See
§Resolution.

**Pre-registered and opened 2026-07-17**, ground T, fourth candidate —
the last trainability mechanism no earlier face covers: **adaptive
circuit growth** (qubit-ADAPT). The circuit is built by a greedy
feedback loop through the device — largest pool gradient wins each
round — so it is data-dependent: no fixed ensemble (T2's Haar), no
fixed warm region (T3), no fixed DLA (T1). The hypothesis under test
was ground T's own prediction:

> The selection criterion *is* gradient magnitude, and by T1–T3 large
> gradients live in classically visible sectors — so the surrogate
> should replicate the construction itself, selections and all.

Access symmetry as always: the surrogate arm runs the *same policy*
(greedy selection + Rotosolve angle updates + periodic sweeps), with
every quantity — pool gradients included — computed from budget-N
truncated Pauli propagation instead of the device.

## Protocol

Qubit-ADAPT: pool $\{Y_q\} \cup \{Y_qZ_{q+1}, Z_qY_{q+1}, Y_qX_{q+1},
X_qY_{q+1}\}$, 24 rounds, Rotosolve for each new angle (the loss is
exactly sinusoidal in one rotation angle), full sweep every 5 rounds.
Hamiltonians: $H_A$ = TFIM+$0.4ZZ'$ (T3 continuity) and $H_B$ = random
2-local chain (XX/YY/ZZ + fields, fixed seed). $n \in \{6, 8, 10\}$.
Instrument: generalized Pauli engine (arbitrary Pauli rotations;
product/anticommutation tables derived numerically at import with
dense self-checks — engine and pool gradients validated against
statevector to $3\times10^{-15}$ before any experiment ran). Code:
[`code/t4_adaptive_growth.py`](code/t4_adaptive_growth.py), 5
[tests](code/test_t4_adaptive_growth.py); CSV:
[`t4-adaptive-scan.csv`](../hunt/t4-adaptive-scan.csv).

## Resolution: K1 fired at its maximum

| | exact-ADAPT gap closed | audit $N^*$ | selection match (N=512) | $\lvert\Delta E\rvert$ |
|---|---:|---:|---:|---:|
| $H_A$, n=6/8/10 | 100/99/99% | 128–512 | **1.00** | ≤ 0.0005 |
| $H_B$, n=6/8/10 | 100/98/99% | 128 | **1.00** | 0.0000 |

The pre-registered fire condition (match ≥ 0.8, $|\Delta E| \le
0.0125n$, audits on the ladder) is not just met — the surrogate is
**indistinguishable from the device** at every decision the algorithm
makes. Two readings, both structural:

1. **The selection oracle is itself a surrogatable functional.** Pool
   gradients $i\langle[G,H]\rangle$ at the current state are linear
   losses of exactly the kind T1–T3 showed the truncation tracks —
   greedily maximizing them selects, by construction, directions the
   classical tracker sees best.
2. **Greed keeps the construction shallow and sparse.** ADAPT's
   24-gate circuits have audit budgets (128) *below* the fixed
   warm-start ansatz's (512): the feedback loop, optimizing for
   gradient signal, actively steers *into* the classically cheap
   region. Adaptivity doesn't escape the dichotomy — it deepens it.

**Stated limits:** $n \le 10$; 2-local neighbor pool (chemistry-style
fermionic pools untested); 24 rounds; quasi-local chain Hamiltonians.
The mechanism statement is structural, but these are the corners a
skeptic should push on.

## Ground T after four faces

| face | mechanism | why the surrogate rides along |
|---|---|---|
| T1 | poly-DLA (no BP) | module mass feeds gradient and tracker alike |
| T2 | any poly-DLA, theorem | irrep dimension controls both; multiplicity contracts |
| T3 | warm starts | the optimizer stays where Heisenberg is sparse |
| T4 | adaptive growth | the selection criterion is a surrogatable functional |

**Four unrelated trainability mechanisms; four structural reasons; one
conclusion: for linear losses, the trainable signal is the surrogatable
signal.** The doors still standing are now exactly the pre-named ones:
nonlinear losses ([L3](L3-trainability-surrogates.md), live), noise-
shaped landscapes (a T-slot), and loss-evaluation hardness (T6-slot,
L9 kinship). This convergence is the ground's meta-lesson and is
paper-shaped — **gated on the human passes now owed** (T2's lemmas,
four kill reviews).

## Ledger discipline

Opened and closed same day — third same-day resolution in the ground.
Instrument validated to machine precision before the experiment;
verdict thresholds pre-registered in the code header.
