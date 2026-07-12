# The toolkit — will it run?

**The catalog as an instrument: a capability matrix, per-machine noise
models for `qsim`, and a feasibility calculator that turns "runs on
near-term hardware" into a number.** *As of 2026-07; parameters from
[`data.yml`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/data.yml).*

The [landscape](index.md) says what exists; [the gap](gap.md) says what's
missing. This page is for the working question in between: *given an
algorithm this program cares about, what would actually happen if we tried
to run it?* Three instruments, all reading the same data file, all tested.

## 1 · The capability matrix

Fidelity decides how *well* a machine runs a circuit; **features decide
whether it can run it at all.** Whole algorithm classes are gated on
booleans no landscape plot shows: the repo's
[Gibbs sampler](../predecessors/12-gibbs-lindblad/notes.md) needs
mid-circuit measurement *and* feed-forward; teleportation-based anything
needs feed-forward; qubit-reuse tricks halve the width of many circuits.

--8<-- "machines/_caps.md"

Three fine-print items worth the price of the table:

- **IBM's arbitrary-angle gates and dynamic circuits are currently
  mutually exclusive** — you may have fractional RZZ *or* feed-forward,
  not both in one job. No headline says this; the compiler flag does.
- **Pulse-level access is nearly extinct** — IBM retired it in Feb 2025;
  Rigetti is the last major vendor exposing it. If your research needs
  pulse control (error-mitigation research, custom gates), your machine
  list has one entry.
- **IonQ's mid-circuit measurement is a roadmap item**, not a Forte
  feature — a capability gap #AQ benchmarks never encounter.

## 2 · Machine noise models for `qsim`

[`qsim/noise.py`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/qsim/noise.py)
lets any circuit in this repository run "as if" on a cataloged machine —
stochastic Pauli trajectories at the machine's published error rates, plus
readout flips:

```python
from qsim import zero_state, H, CNOT
from qsim.noise import MachineNoise, noisy_apply, noisy_sample
import numpy as np

noise = MachineNoise.from_catalog("quantinuum-helios")
rng = np.random.default_rng(0)

psi = zero_state(2)
psi = noisy_apply(psi, H, [0], noise, rng)
psi = noisy_apply(psi, CNOT, [0, 1], noise, rng)
print(noisy_sample(psi, noise, shots=5, seed=1))
```

The model is stated in the module docstring and it is deliberately
**an upper bound on the hardware**: published RB error as total Pauli-fault
probability, independent faults, no crosstalk, no drift, no leakage, no
correlated bursts ([the gap, §3](gap.md#3--the-noise-the-theorem-doesnt-cover)).
If an experiment fails *in this simulation*, it fails on the machine;
passing here proves nothing about the machine. That asymmetry is the
honest use of noise models, and it is exactly the right tool for the
L-ground candidates ([L2](../hunt/L2-physical-noise-learning.md),
[L5](../hunt/L5-noise-threshold.md)) that ask how advantages die under
physical noise. `MachineNoise.from_catalog` refuses machines with no
published error — no number, no simulation.

## 3 · The feasibility calculator

[`machines/feasibility.py`](https://github.com/mamuncseru/quantum-advantage-quest/blob/main/machines/feasibility.py)
scores a circuit profile against every machine: SWAP-routing overhead from
the machine's topology (all constants stated in the module, all optimistic
for the hardware), then zero-fault probability, then a verdict —
`RUNS` (≥ 0.5) / `HEROIC` (≥ 0.01, error-mitigation territory) / `NO` /
`TOO SMALL` / `BLOCKED` (missing capability).

```text
$ python machines/feasibility.py --qubits 50 --g2 1225 --pattern nonlocal
Quantinuum Helios    HEROIC   3.7e-01    1,225
IonQ Tempo           HEROIC   1.8e-01    1,225   (spec numbers)
Quantinuum H2        HEROIC   1.2e-01    1,225
Google Willow        NO       2.7e-22   14,874
IBM Heron r2         NO       1.2e-31   23,536
```

### Worked example 1 — connectivity is destiny

The profile above (50 qubits, 1,225 nonlocal 2Q gates — a QV-style square
circuit) is the clearest demonstration in the catalog of a fact vendor
tables hide: **routing is a multiplier on error**. The same 1,225 gates
stay 1,225 on Quantinuum's all-to-all QCCD but become 14,874 on Willow's
grid and 23,536 on heavy-hex. The ion machines' fidelity lead is real, but
on nonlocal circuits their *effective* lead is ~30× bigger than the
spec-sheet ratio — this, not raw fidelity, is why they own quantum-volume
benchmarks.

### Worked example 2 — this repo's own Shor cannot run anywhere

Our [`qsim` Shor implementation](../predecessors/04-shor/notes.md) factors
35 with 19 qubits and order-10⁴ two-qubit gates. Verdict, on the best
machine ever built: **NO — zero-fault probability ≈ 5×10⁻¹¹** (Helios);
every other machine is worse by orders of magnitude. The smallest
textbook-interesting instance of the most famous quantum algorithm is
out of reach of every computer on Earth, bare. That single number is the
entire case for fault tolerance — and for this program's insistence that
near-term advantage must come from somewhere other than deep circuits.

### Worked example 3 — capabilities cut before fidelity does

A Gibbs-sampler-shaped profile (30 qubits, 2,000 nonlocal 2Q gates,
**needs** mid-circuit measurement + feed-forward):

```text
Quantinuum Helios    HEROIC   2.0e-01    2,000
Quantinuum H2        HEROIC   5.5e-02    2,000
Google Willow        NO       1.5e-26   17,909
Zuchongzhi 3.0       BLOCKED  (missing: mid_circuit_meas, feed_forward)
Rigetti Ankaa-3      BLOCKED  (missing: feed_forward)
```

The field for this algorithm class is **one vendor deep**. If a Hunt
candidate needs measure-and-condition, its hardware story begins and ends
in Broomfield, Colorado — a concentration risk worth knowing before
investing proof effort.

## Honest limits

These instruments inherit the catalog's discipline and its blind spots:
published numbers only, first-order error arithmetic, no idle noise, no
drift. They will tell you a circuit is *infeasible* with confidence; they
can never certify one *feasible*. For that there is only the queue, the
invoice, and the machine.

*Longitudinal honesty: `machines/snapshots/` keeps dated copies of
`data.yml` (quarterly) so that, in a year, extrapolation claims can be
tested against what the numbers actually did.*
