"""Tests for the will-it-run feasibility calculator."""

import pytest

from machines.feasibility import (Profile, assess, connectivity_kind,
                                  route_multiplier)


def by_name(rows, name):
    return next(r for r in rows if name in r["machine"])


def test_tiny_circuit_runs_on_helios():
    rows = assess(Profile(qubits=2, g2=10, pattern="local"))
    r = by_name(rows, "Helios")
    assert r["verdict"] == "RUNS" and r["fidelity"] > 0.98


def test_more_gates_never_help():
    small = by_name(assess(Profile(20, 100)), "Heron")
    big = by_name(assess(Profile(20, 10_000)), "Heron")
    assert big["fidelity"] < small["fidelity"]


def test_routing_order():
    # For nonlocal circuits: all-to-all pays nothing; grids pay; heavy-hex
    # pays more than square; a chain pays most.
    n = 100
    a2a = route_multiplier("all-to-all", n, "nonlocal")
    sq = route_multiplier("square", n, "nonlocal")
    hh = route_multiplier("heavy-hex", n, "nonlocal")
    lin = route_multiplier("linear", n, "nonlocal")
    assert a2a == 1.0 < sq < hh < lin
    # local circuits pay nothing anywhere
    assert route_multiplier("heavy-hex", n, "local") == 1.0


def test_connectivity_classification():
    assert connectivity_kind({"connectivity": "heavy-hex lattice"}) == "heavy-hex"
    assert connectivity_kind({"connectivity": "square lattice (degree 4)"}) == "square"
    assert connectivity_kind({"connectivity": "all-to-all (QCCD)"}) == "all-to-all"
    assert connectivity_kind(
        {"connectivity": "reconfigurable (atom shuttling)"}) == "all-to-all"


def test_caps_block_and_too_small():
    rows = assess(Profile(qubits=30, g2=100, needs=("mid_circuit_meas",)))
    assert by_name(rows, "Forte")["verdict"] == "BLOCKED"
    assert "mid_circuit_meas" in by_name(rows, "Forte")["missing"]
    assert by_name(rows, "Helios")["verdict"] != "BLOCKED"
    rows = assess(Profile(qubits=200, g2=100))
    assert by_name(rows, "Helios")["verdict"] == "TOO SMALL"


def test_analog_and_unsourced_machines_excluded():
    names = " ".join(r["machine"] for r in assess(Profile(2, 1)))
    assert "D-Wave" not in names and "Aquila" not in names
    assert "Jiuzhang" not in names


def test_ion_all_to_all_beats_grid_on_nonlocal():
    # Same profile, nonlocal: Helios pays no routing, Heron does. The
    # routed 2Q count must reflect that.
    rows = assess(Profile(qubits=50, g2=1000, pattern="nonlocal"))
    assert by_name(rows, "Helios")["g2_eff"] == 1000
    assert by_name(rows, "Heron")["g2_eff"] > 10_000


def test_bad_profile_rejected():
    with pytest.raises(ValueError):
        Profile(2, 1, pattern="diagonal")
