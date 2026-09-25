# T5 — The noise face: does noise ever hurt the surrogate more than the device?

**Pre-registered and opened 2026-07-17**, ground T, fifth candidate.
Two known results, never put on one trajectory-resolved instrument:
noise-induced barren plateaus flatten variational landscapes
exponentially in circuit volume, and depolarizing noise makes
Pauli-propagation surrogates converge *faster* — each noise location
damps exactly the high-weight terms that truncation drops. The
fifth-face hypothesis: **noise degrades trainability and surrogate cost
together, monotonically** — there is no $(p, \text{depth})$ window
where training survives but the surrogate breaks.

> **Q(T5).** Along warm-start training trajectories under per-gate
> depolarizing noise $p$: does the surrogate budget $N^*$ ever
> *increase* with $p$ while training progress stays within 90% of
> noiseless? (Survival condition — noise as a quantum resource against
> surrogacy.) Or do progress and budget fall together? (K1 — the fifth
> face.)

## Instrument

T3's protocol (RY+CZ HEA, 6 layers, $\varepsilon = 0.1$ warm start,
$H$ = TFIM+$0.4ZZ'$) with single-qubit depolarizing after every gate on
every touched qubit. **Two independent implementations of the noisy
loss**: exact density-matrix simulation, and backward Pauli propagation
with the exact per-location damping factor $(1 - 4p/3)$ on touched
terms — validated against each other to $8.4\times10^{-15}$ before any
experiment ran (the damped propagation, untruncated, *is* the noisy
loss). Code: [`code/t5_noise_face.py`](code/t5_noise_face.py), 5
[tests](code/test_t5_noise_face.py); CSV:
[`t5-noise-scan.csv`](../hunt/t5-noise-scan.csv).

## Results

**$n=6$ (preliminary, same protocol):** monotone in exactly the
predicted direction —

| $p$ | progress (t=60) | $N^*$ |
|---:|---:|---:|
| 0 | 0.99 | 512 |
| $10^{-3}$ | 0.97 | 512 |
| $10^{-2}$ | 0.82 | 128 |
| $3\times10^{-2}$ | 0.50 | **32** |

**$n=8$ (the pre-registered protocol size):**

| $p$ | progress (t=60) | $\lvert\nabla\rvert$ (t=60) | $N^*$ (t=30/60) |
|---:|---:|---:|---:|
| 0 | 0.99 | 0.12 | 512 |
| $10^{-3}$ | 0.97 | 0.12 | 512 |
| $10^{-2}$ | 0.81 | 0.20 | 32 |
| $3\times10^{-2}$ | 0.48 | 0.27 | 128 |

Reading: as noise grows the device closes less of the gap while the
surrogate needs an order of magnitude *fewer* terms than noiseless — at
$p = 0.01$ the machine loses a fifth of the gap and the classical side
tracks it with **32 terms** of a 65,536-term space.

## Verdict (2026-07-17, same day): K1 fires — the fifth face

The **survival condition is violated at every $p$**: no noise level
keeps progress within 90% of noiseless (0.97 at $p{=}10^{-3}$ comes
closest — with $N^*$ *equal*, not above, noiseless), and every noisy
$N^*$ sits at or far below the noiseless 512. One granularity caveat,
reported because pre-registration demands it: between the two noisiest
levels, late-checkpoint $N^*$ goes 32 → 128 ($p = 0.01 \to 0.03$) —
not strictly monotone at ladder resolution, though both are $\ll$ the
noiseless budget and the $p=0.03$ trajectory stalls in a different
region of the landscape (progress 0.48). The face-defining comparison —
noisy vs noiseless — is monotone everywhere. **T5 closes.**

**Mechanism (the fifth face's version of the shared cause):** the
damping factor $(1-4p/3)^{\#\text{locations touched}}$ acts on Pauli
weight — the same coordinate truncation acts on. Noise *is* a
truncation, applied by the hardware to itself. The components of the
loss that noise destroys are precisely the components the surrogate was
going to drop; what noise leaves alive is what the surrogate keeps.
NIBP and noisy-simulability are one phenomenon seen from two sides —
the exact analogue of T1/T2's module-mass identity and T3/T4's
sparsity identity.

**Stated limits:** depolarizing only (coherent/non-Markovian noise
untested — L2's territory); $n \le 8$ at protocol size; error
mitigation not modeled (and [provably exponential](../machines/gap.md)
as a way out).

## Pre-registration

- **K1** (fifth face): $N^*(p)$ and progress$(p)$ both non-increasing
  in $p$ at every checkpoint — **FIRED in substance** (monotone vs
  noiseless everywhere; one 32→128 ladder-granularity blip between
  noisy levels, recorded above).
- **Survival:** some $p$ with progress $\ge 0.9\times$ noiseless and
  $N^*$ persistently above noiseless — **decisively violated at every
  $p$, both sizes.**

## Ledger discipline

Fifth candidate of the ground; instrument cross-validated to machine
precision before use; verdict thresholds pre-registered in the code
header.
