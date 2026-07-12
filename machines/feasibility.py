"""Will it run? — feasibility of a circuit profile on every cataloged machine.

Give it what your algorithm needs — qubits, two-qubit gates, interaction
pattern, capabilities — and it answers, per machine in data.yml: expected
zero-fault probability after routing overhead, and a verdict. This is the
instrument the Hunt uses to turn "runs on near-term hardware" from a
hand-wave into a number.

Model (all constants stated; every one is OPTIMISTIC for the hardware):
- Routing: a "nonlocal" circuit on limited connectivity pays SWAP overhead.
  Mean qubit distance is ~(2/3)sqrt(n) on a square lattice (standard grid
  arithmetic), ~1.5x that on heavy-hex, ~n/3 on a chain; each SWAP costs 3
  native 2Q gates. All-to-all and shuttling/reconfigurable machines pay 0.
  "local" circuits (nearest-neighbor by design) pay 0 everywhere.
- Fidelity: zero-fault probability (1-e2)^G2_eff (1-e1)^g1 (1-ro)^n with
  the catalog's published errors; e1 defaults to e2/10 and readout to 1%
  where unpublished (same defaults as qsim.noise).
- Ignored (because unpublished): idle errors, crosstalk, drift, leakage,
  correlated bursts. Real machines do worse — see machines/gap.md.

CLI:  .venv/bin/python machines/feasibility.py --qubits 50 --g2 1225 \
          --pattern nonlocal --needs mid_circuit_meas
"""

import argparse
import math
from pathlib import Path

import yaml

HERE = Path(__file__).resolve().parent
DATA = yaml.safe_load((HERE / "data.yml").read_text())

SWAP_COST = 3          # native 2Q gates per SWAP
DEFAULT_1Q_FRACTION = 0.1
DEFAULT_READOUT = 1e-2

VERDICTS = ("RUNS", "HEROIC", "NO", "TOO SMALL", "BLOCKED")


def connectivity_kind(machine):
    """Classify a machine's connectivity string for routing purposes."""
    c = (machine.get("connectivity") or "").lower()
    if "all-to-all" in c or "reconfigurable" in c:
        return "all-to-all"
    if "heavy-hex" in c:
        return "heavy-hex"
    if "square" in c or "lattice" in c:
        return "square"
    if "linear" in c:
        return "linear"
    return "unknown"


def route_multiplier(kind, n, pattern):
    """Factor multiplying the 2Q gate count after SWAP routing."""
    if pattern == "local" or kind == "all-to-all":
        return 1.0
    if kind == "square":
        dist = (2 / 3) * math.sqrt(n)
    elif kind == "heavy-hex":
        dist = 1.5 * (2 / 3) * math.sqrt(n)
    elif kind == "linear":
        dist = n / 3
    else:  # unknown connectivity: charge square-lattice routing
        dist = (2 / 3) * math.sqrt(n)
    return 1.0 + SWAP_COST * max(0.0, dist - 1.0)


class Profile:
    """What the algorithm needs from a machine."""

    def __init__(self, qubits, g2, g1=0, pattern="nonlocal", needs=()):
        if pattern not in ("local", "nonlocal"):
            raise ValueError("pattern must be 'local' or 'nonlocal'")
        self.qubits, self.g2, self.g1 = qubits, g2, g1
        self.pattern, self.needs = pattern, tuple(needs)


def assess_machine(profile, m):
    """One machine's verdict for a profile; None if not assessable."""
    if not m["gate_based"] or m.get("qubits") is None:
        return None
    caps = m.get("caps", {})
    missing = [k for k in profile.needs if caps.get(k) is not True]
    if m["qubits"] < profile.qubits:
        return dict(machine=m["name"], verdict="TOO SMALL",
                    fidelity=0.0, g2_eff=None, missing=missing)
    if missing:
        return dict(machine=m["name"], verdict="BLOCKED",
                    fidelity=0.0, g2_eff=None, missing=missing)
    if m.get("err_2q") is None:
        return None  # nothing honest to compute
    e2 = m["err_2q"]
    e1 = m.get("err_1q") or e2 * DEFAULT_1Q_FRACTION
    ro = m.get("spam_err") or DEFAULT_READOUT
    mult = route_multiplier(connectivity_kind(m), profile.qubits,
                            profile.pattern)
    g2_eff = profile.g2 * mult
    fid = ((1 - e2) ** g2_eff * (1 - e1) ** profile.g1
           * (1 - ro) ** profile.qubits)
    verdict = "RUNS" if fid >= 0.5 else "HEROIC" if fid >= 0.01 else "NO"
    return dict(machine=m["name"], verdict=verdict, fidelity=fid,
                g2_eff=g2_eff, missing=[])


def assess(profile):
    """Verdicts for every assessable machine, best fidelity first."""
    rows = [r for m in DATA["machines"]
            if (r := assess_machine(profile, m)) is not None]
    return sorted(rows, key=lambda r: -r["fidelity"])


def render(profile, rows):
    lines = [f"profile: {profile.qubits} qubits, {profile.g2:,} 2Q gates "
             f"({profile.pattern}), needs={list(profile.needs) or '—'}",
             f"{'machine':34} {'verdict':9} {'P(zero faults)':>14} "
             f"{'2Q after routing':>17}"]
    for r in rows:
        fid = f"{r['fidelity']:.2e}" if r["g2_eff"] is not None else "—"
        g2 = f"{r['g2_eff']:,.0f}" if r["g2_eff"] is not None else "—"
        note = f"  (missing: {', '.join(r['missing'])})" if r["missing"] else ""
        lines.append(f"{r['machine']:34} {r['verdict']:9} {fid:>14} "
                     f"{g2:>17}{note}")
    return "\n".join(lines)


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--qubits", type=int, required=True)
    ap.add_argument("--g2", type=int, required=True,
                    help="two-qubit gate count")
    ap.add_argument("--g1", type=int, default=0)
    ap.add_argument("--pattern", choices=("local", "nonlocal"),
                    default="nonlocal")
    ap.add_argument("--needs", nargs="*", default=(),
                    help="required caps, e.g. mid_circuit_meas feed_forward")
    args = ap.parse_args(argv)
    profile = Profile(args.qubits, args.g2, args.g1, args.pattern,
                      args.needs)
    print(render(profile, assess(profile)))


if __name__ == "__main__":
    main()
