"""Machine-noise channels for qsim — run any circuit "as if" on a cataloged
machine (curriculum rule: no black boxes, so the model is spelled out).

Model (stated plainly, honest about its limits)
-----------------------------------------------
Stochastic Pauli trajectories on the statevector: after each gate, with
probability equal to the machine's published average gate error, a uniformly
random non-identity Pauli is applied to the gate's qubits; measured bits are
flipped independently with the readout error. This treats the published
randomized-benchmarking error as a total Pauli-fault probability — the
standard depolarizing approximation. What it deliberately does NOT model,
because no vendor publishes the numbers: coherent errors, crosstalk,
leakage, drift, and correlated bursts (machines/gap.md section 3). Real
hardware is therefore WORSE than this simulation — treat results as an
upper bound on machine performance.

Machine parameters come from machines/data.yml (the catalog's single source
of truth); unknown fields fall back to stated defaults.

>>> from qsim.noise import MachineNoise, noisy_apply, noisy_sample
>>> noise = MachineNoise.from_catalog("quantinuum-helios")
"""

from pathlib import Path

import numpy as np
import yaml

from . import I2, X, Y, Z, apply

_ROOT = Path(__file__).resolve().parent.parent
_PAULIS = (I2, X, Y, Z)

# Stated defaults where the catalog has null (documented, deliberately
# pessimistic-but-plausible): 1Q error = 2Q error / 10, readout error 1%.
DEFAULT_1Q_FRACTION = 0.1
DEFAULT_READOUT = 1e-2


class MachineNoise:
    """Noise parameters of one machine: 2Q, 1Q, and readout error."""

    def __init__(self, err_2q, err_1q=None, readout=None, label=""):
        if not 0 <= err_2q < 1:
            raise ValueError(f"err_2q out of range: {err_2q}")
        self.err_2q = float(err_2q)
        self.err_1q = float(err_1q if err_1q is not None
                            else err_2q * DEFAULT_1Q_FRACTION)
        self.readout = float(readout if readout is not None else DEFAULT_READOUT)
        self.label = label

    @classmethod
    def from_catalog(cls, machine_id):
        data = yaml.safe_load((_ROOT / "machines" / "data.yml").read_text())
        for m in data["machines"]:
            if m["id"] == machine_id:
                if m.get("err_2q") is None:
                    raise ValueError(
                        f"{machine_id} has no published 2Q error in the "
                        "catalog — nothing honest to simulate")
                return cls(m["err_2q"], m.get("err_1q"), m.get("spam_err"),
                           label=m["name"])
        raise KeyError(f"unknown machine id: {machine_id}")

    def __repr__(self):
        return (f"MachineNoise({self.label or '?'}: 2Q={self.err_2q:.1e}, "
                f"1Q={self.err_1q:.1e}, readout={self.readout:.1e})")


def _random_pauli_fault(psi, qubits, rng):
    """Apply a uniform non-identity Pauli string on `qubits`."""
    k = len(qubits)
    while True:
        picks = rng.integers(0, 4, size=k)
        if picks.any():
            break
    for q, p in zip(qubits, picks):
        if p:
            psi = apply(psi, _PAULIS[p], [q])
    return psi


def noisy_apply(psi, U, qubits, noise, rng):
    """`apply`, then a stochastic Pauli fault at the machine's gate error."""
    psi = apply(psi, U, qubits)
    err = noise.err_2q if len(qubits) >= 2 else noise.err_1q
    if rng.random() < err:
        psi = _random_pauli_fault(psi, qubits, rng)
    return psi


def noisy_sample(psi, noise, shots=1, qubits=None, seed=None):
    """Measure like qsim.sample, then flip each bit at the readout error."""
    from . import sample
    rng = np.random.default_rng(seed)
    raw = sample(psi, shots=shots, qubits=qubits, seed=rng.integers(2**31))
    out = []
    for bits in raw:
        flips = rng.random(len(bits)) < noise.readout
        out.append("".join(str(int(b) ^ int(f))
                           for b, f in zip(bits, flips)))
    return out


def success_probability(n_qubits, g2, noise, g1=0):
    """Analytic zero-fault probability: (1-e2)^g2 (1-e1)^g1 (1-r)^n.

    First-order circuit-success estimate — the same arithmetic as the
    catalog's depth-budget figure, with readout included.
    """
    return ((1 - noise.err_2q) ** g2 * (1 - noise.err_1q) ** g1
            * (1 - noise.readout) ** n_qubits)
