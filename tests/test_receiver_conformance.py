"""C-34-08 — receiver conformance rows a receiver can actually clear, except the one it may not.

gh#2429: a receiver that had adopted a release byte-for-byte reported four INCOMPLETE rows and
three were structurally unreachable. The fourth was correct. These tests hold that line in both
directions: the three become clearable, and the fourth stays blocking.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]


def _load(name, rel):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


crc = _load("crconf", "scripts/check_receiver_conformance.py")
canon = _load("canonroot", "scripts/canonical_root.py")

COMPLETE, INCOMPLETE, UNVERIFIABLE = crc.COMPLETE, crc.INCOMPLETE, crc.UNVERIFIABLE


@pytest.mark.parametrize("entries", [[], [None], ["bad"], [{"sha256": "abc"}]])
def test_invalid_ordered_entries_cannot_certify_integrity(tmp_path, entries):
    assert crc.check_integrity(entries, tmp_path)["state"] == UNVERIFIABLE


@pytest.mark.parametrize("entries", [[], [None], ["bad"], [{"path": "a.py"}, None]])
def test_manifest_reader_does_not_silently_drop_entries(entries):
    with pytest.raises(crc.InputError):
        crc.manifest_entries({"files": entries})


def test_json_manifest_requires_mapping(tmp_path):
    source = tmp_path / "manifest.json"
    source.write_text("[]")
    with pytest.raises(crc.InputError):
        crc.load_manifest(source)


@pytest.mark.parametrize("detection", [
    [{"name": "check", "exit": 1}, {"name": "check", "exit": 0}],
    [{"name": "check"}], [{"name": "check", "exit": False}], [None],
])
def test_detection_population_cannot_discard_or_invent_results(tmp_path, detection):
    manifest, repo = payload(tmp_path)
    with pytest.raises(crc.InputError):
        crc.assess(manifest, repo, accept(tmp_path, "ACCEPTED"), detection)


def test_acceptance_prose_and_conflicting_terminals_cannot_pass(tmp_path):
    folder = tmp_path / "records"
    folder.mkdir()
    record = folder / "receipt.md"
    record.write_text("The acceptance was NOT ACCEPTED\n")
    assert crc.check_acceptance(folder)["state"] == INCOMPLETE
    record.write_text("**Acceptance terminal**: ACCEPTED\n")
    assert crc.check_acceptance(folder)["state"] == COMPLETE
    (folder / "other.md").write_text("Acceptance terminal: REJECTED\n")
    result = crc.check_acceptance(folder)
    assert result["state"] == INCOMPLETE
    assert result["terminal"] == "CONFLICT"
    assert len(result["evidence"]) == 2


def test_unreadable_acceptance_record_prevents_complete_population(tmp_path):
    folder = accept(tmp_path, "ACCEPTED")
    record = folder / "unreadable.md"
    record.write_text("Acceptance terminal: REJECTED\n")
    record.chmod(0)
    try:
        result = crc.check_acceptance(folder)
        assert result["state"] == UNVERIFIABLE
        assert result["read_failures"]
    finally:
        record.chmod(0o600)


def payload(tmp: Path, *, with_digests=True, corrupt=False):
    repo = tmp / "recv"
    (repo / "scripts").mkdir(parents=True)
    files = {}
    for n in ("a.py", "b.py"):
        p = repo / "scripts" / n
        p.write_text(f"# {n}\n")
        files[f"scripts/{n}"] = hashlib.sha256(p.read_bytes()).hexdigest()
    entries = []
    for rel, dig in files.items():
        e = {"path": rel, "change": "modified", "item": "CD-1"}
        if with_digests:
            e["sha256"] = ("0" * 64) if corrupt else dig
        entries.append(e)
    m = tmp / "DELIVERED.json"
    m.write_text(json.dumps({"files": entries}))
    return m, repo


def accept(tmp: Path, terminal: str):
    d = tmp / "acceptance"
    d.mkdir()
    (d / "record.md").write_text(f"**Acceptance terminal**: {terminal}\n")
    return d


# --- the three that must become reachable -------------------------------------------

def test_a_manifest_carrying_digests_verifies(tmp_path):
    m, repo = payload(tmp_path)
    res = crc.assess(m, repo, accept(tmp_path, "ACCEPTED"), None)
    assert res["rows"]["integrity"]["state"] == COMPLETE
    assert res["rows"]["integrity"]["digest_fields"] == 2


def test_a_manifest_without_digests_is_UNVERIFIABLE_not_verified(tmp_path):
    """The spec said 'verify every ordered manifest digest'; the manifest carried none."""
    m, repo = payload(tmp_path, with_digests=False)
    row = crc.assess(m, repo, accept(tmp_path, "ACCEPTED"), None)["rows"]["integrity"]
    assert row["state"] == UNVERIFIABLE
    assert row["digest_fields"] == 0
    assert "cannot be satisfied by this manifest" in row["why"]


def test_a_mismatched_payload_digest_is_incomplete(tmp_path):
    m, repo = payload(tmp_path, corrupt=True)
    assert crc.assess(m, repo, accept(tmp_path, "ACCEPTED"), None)[
        "rows"]["integrity"]["state"] == INCOMPLETE


def test_a_skipped_detection_row_is_unverified_never_passed(tmp_path):
    m, repo = payload(tmp_path)
    det = [{"name": "CD-01", "exit": 0, "skipped": 1,
            "skip_reasons": "canonical ../aget not present"}]
    row = crc.assess(m, repo, accept(tmp_path, "ACCEPTED"), det)["rows"]["detection:CD-01"]
    assert row["state"] == INCOMPLETE
    assert "never a pass" in row["why"]
    assert "canonical ../aget not present" in row["why"]


def test_a_clean_detection_row_completes(tmp_path):
    m, repo = payload(tmp_path)
    det = [{"name": "CD-01", "exit": 0, "skipped": 0}]
    res = crc.assess(m, repo, accept(tmp_path, "ACCEPTED"), det)
    assert res["rows"]["detection:CD-01"]["state"] == COMPLETE
    assert res["overall"] == COMPLETE and crc.exit_code(res) == 0


# --- the one that must NOT become clearable -------------------------------------------

def test_pending_acceptance_keeps_the_aggregate_incomplete(tmp_path):
    """'exit 2 must never become green because three of its four causes were repaired.'"""
    m, repo = payload(tmp_path)
    det = [{"name": "CD-01", "exit": 0, "skipped": 0}, {"name": "CD-02", "exit": 0, "skipped": 0}]
    res = crc.assess(m, repo, accept(tmp_path, "PENDING"), det)
    assert res["rows"]["detection:CD-01"]["state"] == COMPLETE
    assert res["rows"]["detection:CD-02"]["state"] == COMPLETE
    assert res["rows"]["integrity"]["state"] == COMPLETE
    assert res["rows"]["acceptance_terminal"]["state"] == INCOMPLETE
    assert res["overall"] == INCOMPLETE
    assert crc.exit_code(res) == 2, "three repairs must not turn exit 2 green"


def test_an_absent_acceptance_record_is_not_an_implied_acceptance(tmp_path):
    m, repo = payload(tmp_path)
    res = crc.assess(m, repo, None, None)
    assert res["rows"]["acceptance_terminal"]["state"] == INCOMPLETE
    assert res["rows"]["acceptance_terminal"]["terminal"] == "UNREAD"


@pytest.mark.parametrize("word", ["PENDING", "REJECTED"])
def test_a_non_accepted_terminal_is_reported_verbatim_and_blocks(tmp_path, word):
    m, repo = payload(tmp_path)
    holder = tmp_path / word
    holder.mkdir()
    res = crc.assess(m, repo, accept(holder, word), None)
    assert res["rows"]["acceptance_terminal"]["terminal"] == word
    assert res["rows"]["acceptance_terminal"]["state"] == INCOMPLETE


# --- the canonical resolver, both polarities -------------------------------------------

def test_a_declared_but_unresolvable_canonical_raises_rather_than_skipping(monkeypatch):
    """Skipping there hides a misconfiguration behind a green run."""
    monkeypatch.setenv("AGET_CANONICAL_ROOT", "/definitely/not/here")
    with pytest.raises(canon.CanonicalDeclaredButUnresolvable):
        canon.resolve(REPO)


def test_a_declared_fleet_root_without_aget_raises(monkeypatch, tmp_path):
    monkeypatch.delenv("AGET_CANONICAL_ROOT", raising=False)
    monkeypatch.setenv("AGET_FLEET_ROOT", str(tmp_path))
    with pytest.raises(canon.CanonicalDeclaredButUnresolvable):
        canon.resolve(REPO)


def test_an_absent_canonical_with_nothing_declared_is_None(monkeypatch, tmp_path):
    """Genuinely absent is a portability skip, and must stay distinguishable."""
    monkeypatch.delenv("AGET_CANONICAL_ROOT", raising=False)
    monkeypatch.delenv("AGET_FLEET_ROOT", raising=False)
    lonely = tmp_path / "seat"
    lonely.mkdir()
    assert canon.resolve(lonely) is None


def test_an_explicit_canonical_root_resolves(monkeypatch, tmp_path):
    c = tmp_path / "aget"
    (c / ".git").mkdir(parents=True)
    monkeypatch.setenv("AGET_CANONICAL_ROOT", str(c))
    assert canon.resolve(None) == c


def test_a_fleet_root_resolves_its_aget(monkeypatch, tmp_path):
    monkeypatch.delenv("AGET_CANONICAL_ROOT", raising=False)
    (tmp_path / "aget" / ".git").mkdir(parents=True)
    monkeypatch.setenv("AGET_FLEET_ROOT", str(tmp_path))
    assert canon.resolve(None) == tmp_path / "aget"


def test_the_resolver_matches_the_harnesses_own_order(monkeypatch, tmp_path):
    """AGET_CANONICAL_ROOT wins over AGET_FLEET_ROOT, as check_template_conformance.sh does."""
    a = tmp_path / "explicit"
    (a / ".git").mkdir(parents=True)
    (tmp_path / "fleet" / "aget" / ".git").mkdir(parents=True)
    monkeypatch.setenv("AGET_CANONICAL_ROOT", str(a))
    monkeypatch.setenv("AGET_FLEET_ROOT", str(tmp_path / "fleet"))
    assert canon.resolve(None) == a


# --- input hygiene ---------------------------------------------------------------------

def test_a_manifest_with_no_ordered_list_is_an_input_error(tmp_path):
    m = tmp_path / "m.json"
    m.write_text(json.dumps({"nope": 1}))
    with pytest.raises(crc.InputError):
        crc.assess(m, tmp_path, None, None)


def test_an_unparseable_manifest_is_an_input_error(tmp_path):
    m = tmp_path / "m.json"
    m.write_text("{[bad")
    with pytest.raises(crc.InputError):
        crc.assess(m, tmp_path, None, None)
