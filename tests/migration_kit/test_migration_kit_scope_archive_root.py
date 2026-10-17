"""C32 R11: fixed production archive and completeness across release ledgers."""
import json

import pytest

from test_migration_kit_scope_archive import A, REC, AGET, OLD, LAUNCH, RETIRE, seed_ledger
from test_migration_kit_batch_authority import SID, entry, packet, prompt, records, transcript


@pytest.fixture
def fleet(tmp_path, monkeypatch):
    monkeypatch.delenv("AGET_MIGRATION_TEST_MODE", raising=False)
    monkeypatch.delenv("AGET_MIGRATION_SCOPE_ARCHIVE", raising=False)
    root = tmp_path / "data"
    for module in (A, REC.batch_authority):
        monkeypatch.setattr(module, "HERE", tmp_path / "scripts" / "migration_kit")
    old_dir, active_dir = root / "previous_ledger", root / "current_ledger"
    old_dir.mkdir(parents=True)
    active_dir.mkdir()
    old, _ = seed_ledger(old_dir, current=True)
    active = records(active_dir)
    projects = transcript(tmp_path, [prompt("t1", "typed", OLD), prompt("t2", "typed", LAUNCH),
                                     prompt("t3", "typed", RETIRE)])
    return root, old, active, projects


def gate(active, projects, line=LAUNCH):
    return A.check("12", records=active, projects_dir=projects, act="launch",
                   entry=("12:launch", entry(line)))


def record_launch(active, projects, line=LAUNCH, extra=()):
    return REC.main(["--session", SID, "--key", "12", "--act", "launch", "--line", line, *extra],
                    records=active, projects_dir=projects)


@pytest.mark.parametrize("target", ["blank.jsonl", "../unrelated.jsonl"])
def test_ledger_only_anchor_redirect_refuses_gate_and_recorder(fleet, target, capsys):
    root, old, active, projects = fleet
    assert REC.main(["--archive-ledger", str(old)], records=active) == 0
    assert REC.main(["--anchor-archive"], records=old) == 0
    # Normal post-retirement state: no live scope entry remains to detect this attack.
    assert REC.main(["--session", SID, "--retire-scope", AGET, "--principal-line", RETIRE],
                    records=old, projects_dir=projects) == 0
    archive = root / "scope_archive.jsonl"
    before = archive.read_bytes()
    (active.parent / target).write_text("")
    doc = json.loads(active.read_text())
    doc["scope_archive_anchor"] = {"path": target, "rows": 0, "chain": ""}
    active.write_text(json.dumps(doc))
    ok, why = gate(active, projects, OLD)
    assert not ok, why
    assert "anchor path is not the ledger root's archive; restore the anchor" in why
    assert record_launch(active, projects, OLD) == 1
    assert "anchor path is not the ledger root's archive" in capsys.readouterr().out
    assert REC.main(["--archive-ledger", str(old)], records=active) == 1
    assert archive.read_bytes() == before


@pytest.mark.parametrize("ov", [None, OLD, [OLD], {"source": OLD},
                               {"batches": ["12"], "history": [{"line": OLD, "batches_added": ["12"]}]}])
@pytest.mark.parametrize("empty_archive", [False, True])
def test_fresh_ledger_requires_seed_for_any_raw_entry_then_launches(fleet, ov, empty_archive, capsys):
    root, old, active, projects = fleet
    doc = json.loads(old.read_text())
    doc["scope_overrides"][AGET] = ov
    old.write_text(json.dumps(doc))
    archive = root / "scope_archive.jsonl"
    if empty_archive:
        archive.write_text("")
    before = active.read_bytes(), old.read_bytes()
    ok, why = gate(active, projects, OLD)
    assert not ok, why
    remedy = f"record_authority.py --archive-ledger {old}"
    assert remedy in why, why
    assert record_launch(active, projects, OLD, ["--dry-run"]) == 1
    assert remedy in capsys.readouterr().out
    assert (active.read_bytes(), old.read_bytes()) == before
    assert archive.exists() == empty_archive
    assert REC.main(["--archive-ledger", str(old)], records=active) == 0
    assert gate(active, projects)[0]
    assert record_launch(active, projects) == 0
    # Raw entries without OLD have no taint to retain; all other formats do.
    if ov is not None:
        ok, why = gate(active, projects, OLD)
        assert not ok and "archive" in why, why


@pytest.mark.parametrize("damage", ["delete", "empty", "chain"])
@pytest.mark.parametrize("active_anchor", [False, True])
def test_other_ledger_anchor_blocks_archive_loss_and_reanchor(fleet, damage, active_anchor, capsys):
    root, old, active, projects = fleet
    assert REC.main(["--archive-ledger", str(old)], records=old) == 0
    assert REC.main(["--session", SID, "--retire-scope", AGET, "--principal-line", RETIRE],
                    records=old, projects_dir=projects) == 0
    if active_anchor:
        assert REC.main(["--anchor-archive"], records=active) == 0
    archive = root / "scope_archive.jsonl"
    if damage == "delete":
        archive.unlink()
    elif damage == "empty":
        archive.write_text("")
    else:
        doc = json.loads(old.read_text())
        doc["scope_archive_anchor"]["chain"] = "0" * 64
        old.write_text(json.dumps(doc))
    before = active.read_bytes(), archive.read_bytes() if archive.exists() else None
    ok, why = gate(active, projects)
    assert not ok and "restore" in why and str(old) in why, why
    assert record_launch(active, projects) == 1
    assert REC.main(["--anchor-archive"], records=active) == 1
    assert "restore" in capsys.readouterr().out
    assert REC.main(["--archive-ledger", str(old)], records=active) == 1
    assert (active.read_bytes(), archive.read_bytes() if archive.exists() else None) == before


def test_all_unseeded_ledgers_named_and_cached_scan_notices_edits(fleet):
    root, old, active, projects = fleet
    another_dir = root / "another_ledger"
    another_dir.mkdir()
    another, _ = seed_ledger(another_dir, current=True)
    ok, why = gate(active, projects)
    assert not ok, why
    for source in (old, another):
        assert f"record_authority.py --archive-ledger {source}" in why, why
        assert REC.main(["--archive-ledger", str(source)], records=active) == 0
    assert gate(active, projects)[0]
    # Same process, changed raw entry: old content hashes cannot satisfy this entry.
    doc = json.loads(old.read_text())
    doc["scope_overrides"][AGET]["source"] += " amended"
    old.write_text(json.dumps(doc))
    ok, why = gate(active, projects)
    assert not ok and f"--archive-ledger {old}" in why, why
    assert REC.main(["--archive-ledger", str(old)], records=active) == 0
    assert gate(active, projects)[0]
    new_dir = root / "new_ledger"
    new_dir.mkdir()
    new, _ = seed_ledger(new_dir, current=True)
    ok, why = gate(active, projects)
    assert not ok and f"--archive-ledger {new}" in why, why


@pytest.mark.parametrize("alias", [".././scope_archive.jsonl", "../../data/scope_archive.jsonl"])
def test_normalized_fixed_path_remains_valid(fleet, alias):
    _, old, active, projects = fleet
    assert REC.main(["--archive-ledger", str(old)], records=active) == 0
    doc = json.loads(active.read_text())
    doc["scope_archive_anchor"]["path"] = alias
    active.write_text(json.dumps(doc))
    assert gate(active, projects)[0]
    assert not gate(active, projects, OLD)[0]


def test_crash_after_archive_append_explains_possible_row_and_reanchor(tmp_path, monkeypatch, capsys):
    active = records(tmp_path)
    projects = transcript(tmp_path, [prompt("t1", "typed", OLD)])
    p = packet(tmp_path, AGET, tmp_path)
    before = active.read_bytes()
    original = REC.batch_authority.write_scope_records

    def crash(*args):
        raise OSError("simulated crash before ledger save")

    monkeypatch.setattr(REC.batch_authority, "write_scope_records", crash)
    assert REC.main(["--session", SID, "--key", "12", "--line", OLD, "--packet", str(p),
                     "--scope-override", f"{AGET}=docs/"], records=active, projects_dir=projects) == 1
    out = capsys.readouterr().out
    assert "row may have been appended" in out and "--anchor-archive" in out, out
    assert active.read_bytes() == before
    assert len(A.scope_archive_path(active).read_text().splitlines()) == 1
    monkeypatch.setattr(REC.batch_authority, "write_scope_records", original)
    assert not gate(active, projects, OLD)[0]
    assert REC.main(["--anchor-archive"], records=active) == 0
    assert not gate(active, projects, OLD)[0]


def test_old_format_remedy_gives_verbatim_fixed_retirement_form(tmp_path):
    active, projects = seed_ledger(tmp_path)
    assert REC.main(["--archive-ledger", str(active)], records=active) == 0
    ok, why = gate(active, projects)
    assert not ok and f'--principal-line "{RETIRE}"' in why, why
