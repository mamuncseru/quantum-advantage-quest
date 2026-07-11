"""Consistency checks for the machines catalog.

The catalog's discipline is mechanical, so it is enforced mechanically:
data.yml is the single source of truth, every number is typed and in a sane
range, every machine maps to a page, and the generated master table on disk
matches what the data would generate today.
"""

import importlib.util
import re
from pathlib import Path

import pytest
import yaml

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent

DATA = yaml.safe_load((HERE / "data.yml").read_text())
MACHINES = DATA["machines"]
STATUSES = {"deployed", "prototype", "research", "contested", "announced",
            "retired"}
NON_MACHINE_PAGES = {"index.md", "metrics.md", "_table.md"}


def _load_figures_module():
    spec = importlib.util.spec_from_file_location(
        "make_machine_figures", ROOT / "scripts" / "make_machine_figures.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


# ------------------------------------------------------------- structure --

def test_required_fields_present():
    required = {"id", "name", "org", "page", "modality", "status",
                "gate_based", "year", "qubits", "qubit", "claim", "skeptic",
                "sources"}
    for m in MACHINES:
        missing = required - set(m)
        assert not missing, f"{m.get('id', '?')} missing {missing}"


def test_ids_unique():
    ids = [m["id"] for m in MACHINES]
    assert len(ids) == len(set(ids))


def test_modalities_and_statuses_valid():
    slots = [v["slot"] for v in DATA["modalities"].values()]
    assert sorted(slots) == list(range(1, len(slots) + 1))
    for m in MACHINES:
        assert m["modality"] in DATA["modalities"], m["id"]
        assert m["status"] in STATUSES, f"{m['id']}: {m['status']}"


def test_as_of_stamp_format_and_presence():
    assert re.fullmatch(r"20\d\d-\d\d", DATA["as_of"])
    # the index page must carry the same stamp it promises
    assert f"specs as of {DATA['as_of']}" in (HERE / "index.md").read_text()


# ----------------------------------------------------------- sane values --

def test_numbers_are_numbers_not_strings():
    # PyYAML parses "1e-3" as a string; the 1.0e-3 form as a float.
    # A silent string here would corrupt every figure.
    for m in MACHINES:
        for key in ("err_2q", "err_1q", "spam_err", "t1_s", "t2_s",
                    "gate_2q_s"):
            v = m.get(key)
            assert v is None or isinstance(v, (int, float)), \
                f"{m['id']}.{key} = {v!r} parsed as {type(v).__name__}"


def test_values_in_sane_ranges():
    for m in MACHINES:
        assert 2019 <= m["year"] <= 2027, m["id"]
        if m["qubits"] is not None:
            assert 1 <= m["qubits"] <= 10_000, m["id"]
        for key in ("err_2q", "err_1q", "spam_err"):
            v = m.get(key)
            if v is not None:
                assert 1e-6 < v < 0.1, f"{m['id']}.{key} = {v}"
        for key in ("t1_s", "t2_s"):
            v = m.get(key)
            if v is not None:
                assert 1e-6 < v < 1e3, f"{m['id']}.{key} = {v}"
        if m.get("gate_2q_s") is not None:
            assert 1e-9 < m["gate_2q_s"] < 1e-2, m["id"]
        lg = m.get("logical")
        if lg is not None:
            assert 1 <= lg <= (m["qubits"] or 10_000), m["id"]


def test_every_machine_has_sources():
    for m in MACHINES:
        assert m["sources"], m["id"]
        for url in m["sources"]:
            assert url.startswith("https://"), f"{m['id']}: {url}"


def test_physics_bounds():
    # t2 <= 2*t1 whenever both are given
    for m in MACHINES:
        if m.get("t1_s") is not None and m.get("t2_s") is not None:
            assert m["t2_s"] <= 2 * m["t1_s"] + 1e-12, m["id"]


# ------------------------------------------------------- pages <-> data --

def test_pages_are_plain_markdown_names():
    for m in MACHINES:
        assert re.fullmatch(r"[a-z0-9-]+\.md", m["page"]), m["id"]


def test_every_existing_machine_page_is_referenced():
    referenced = {m["page"] for m in MACHINES}
    for page in HERE.glob("*.md"):
        if page.name in NON_MACHINE_PAGES:
            continue
        assert page.name in referenced, \
            f"{page.name} exists but no machine in data.yml points to it"


def test_existing_machine_pages_carry_the_stamp():
    for m in MACHINES:
        page = HERE / m["page"]
        if page.exists():
            assert DATA["as_of"] in page.read_text(), \
                f"{m['page']} missing 'as of {DATA['as_of']}' stamp"


# --------------------------------------------------- generated artifacts --

def test_master_table_matches_data():
    mod = _load_figures_module()
    before = (HERE / "_table.md").read_text()
    mod.emit_table()
    after = (HERE / "_table.md").read_text()
    assert before == after, \
        "_table.md is stale — run scripts/make_machine_figures.py"


def test_scatter_points_exclude_analog_and_unsourced():
    mod = _load_figures_module()
    pts = mod.scatter_points()
    assert len(pts) >= 8
    by_id = {m["name"]: m for m in MACHINES}
    for p in pts:
        m = by_id[p["name"]]
        assert m["gate_based"], p["name"]
        assert m["err_2q"] is not None and m["qubits"] is not None


def test_figures_exist_for_both_modes():
    for stem in ("fig-landscape", "fig-timeline", "fig-logical",
                 "fig-depth", "fig-nines", "fig-transmon", "fig-lattices"):
        assert (HERE / f"{stem}.svg").exists(), stem
        assert (HERE / f"{stem}-dark.svg").exists(), stem


def test_history_and_milestones_typed():
    for h in DATA["history"]:
        assert isinstance(h["year"], int) and 2018 <= h["year"] <= 2027
        assert isinstance(h["qubits"], int) and h["qubits"] > 0
        assert h["modality"] in DATA["modalities"]
    dates = [m["date"] for m in DATA["logical_milestones"]]
    assert dates == sorted(dates), "milestones must be chronological"
    for m in DATA["logical_milestones"]:
        assert isinstance(m["logical"], int) and 1 <= m["logical"] <= 1000
        assert m["modality"] in DATA["modalities"]
