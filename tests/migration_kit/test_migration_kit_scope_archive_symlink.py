"""C32 R12: lexical kit root, shared link refusals and portable seeded content."""
import json
import shutil

import pytest

from test_migration_kit_scope_archive_root import fleet, gate, record_launch
from test_migration_kit_scope_archive import A, REC, AGET, OLD, LAUNCH, RETIRE
from test_migration_kit_batch_authority import SID, packet, records


SYMLINK_REMEDY = ("replace the symlink with the real file/directory; "
                   "the ledger and archive must live in the kit's data directory")


@pytest.mark.parametrize("mode", ["production", "test"])
@pytest.mark.parametrize("route", ["records", "ledger", "root", "archive"])
def test_active_symlink_refuses_gate_and_all_recorder_writes(fleet, tmp_path, monkeypatch, capsys, mode, route):
    root, old, active, projects = fleet
    assert REC.main(["--archive-ledger", str(old)], records=active) == 0
    if mode == "test":
        monkeypatch.setenv("AGET_MIGRATION_TEST_MODE", "1")
    archive = root / "scope_archive.jsonl"
    before_archive = archive.read_bytes()
    before_old = old.read_bytes()
    # S1 relocates to a fresh file nested in the active ledger; S2 relocates outside data.
    if route == "records":
        target = active.parent / "x" / "records.json"
        target.parent.mkdir()
        target.write_text("{}")
        active.rename(active.with_name("records.aside.json"))
        active.symlink_to("x/records.json")
    elif route == "ledger":
        target = tmp_path / "outside" / "current_ledger"
        target.mkdir(parents=True)
        (target / "records.json").write_text("{}")
        active.parent.rename(root / "current.aside")
        active.parent.symlink_to(target, target_is_directory=True)
    elif route == "root":
        target = tmp_path / "data.aside"
        root.rename(target)
        root.symlink_to(target, target_is_directory=True)
    else:
        target = tmp_path / "archive.aside.jsonl"
        archive.rename(target)
        archive.symlink_to(target)
    before_active = active.read_bytes()
    for line in (OLD, LAUNCH):
        ok, why = gate(active, projects, line)
        assert not ok, why
        assert "symlink" in why and SYMLINK_REMEDY in why, why
        assert record_launch(active, projects, line) == 1
    p = packet(tmp_path, AGET, tmp_path)
    commands = [
        ["--archive-ledger", str(old)], ["--anchor-archive"],
        ["--session", SID, "--key", "12", "--line", LAUNCH],
        ["--session", SID, "--retire-scope", AGET, "--principal-line", RETIRE],
        ["--session", SID, "--key", "12", "--line", OLD, "--packet", str(p),
         "--scope-override", f"{AGET}=docs/"],
    ]
    for argv in commands:
        for dry_run in ([], ["--dry-run"]):
            capsys.readouterr()
            assert REC.main([*argv, *dry_run], records=active, projects_dir=projects) == 1
            assert SYMLINK_REMEDY in capsys.readouterr().out
    assert active.read_bytes() == before_active
    assert archive.read_bytes() == before_archive
    assert old.read_bytes() == before_old


@pytest.mark.parametrize("route", ["outside-dir", "alias-dir", "empty-dir", "records", "broken-records"])
def test_symlinked_sibling_refuses_even_aliases_and_empty_directories(fleet, tmp_path, route):
    root, old, active, projects = fleet
    assert REC.main(["--archive-ledger", str(old)], records=active) == 0
    sibling = root / "linked_ledger"
    if route.endswith("dir"):
        target = active.parent if route == "alias-dir" else tmp_path / "outside"
        target.mkdir(exist_ok=True)
        if route == "outside-dir":
            (target / "records.json").write_text("{}")
        sibling.symlink_to(target, target_is_directory=True)
    else:
        sibling.mkdir()
        (sibling / "records.json").symlink_to(old if route == "records" else tmp_path / "missing.json")
    ok, why = gate(active, projects)
    assert not ok and str(sibling) in why and SYMLINK_REMEDY in why, why
    assert record_launch(active, projects) == 1
    assert REC.main(["--anchor-archive"], records=active) == 1


@pytest.mark.parametrize("route", ["outside", "nested", "wrong-name", "parent-traversal"])
def test_production_active_path_must_match_configured_data_layout(fleet, tmp_path, route, capsys):
    root, old, active, projects = fleet
    assert REC.main(["--archive-ledger", str(old)], records=active) == 0
    if route == "parent-traversal":
        alternate = active.parent / ".." / active.parent.name / "records.json"
    else:
        directory = {"outside": tmp_path / "outside" / "current_ledger",
                     "nested": root / "nested" / "current_ledger",
                     "wrong-name": root / "current"}[route]
        directory.mkdir(parents=True)
        alternate = records(directory)
    ok, why = gate(alternate, projects)
    assert not ok and "kit's data directory" in why, why
    assert record_launch(alternate, projects) == 1
    assert REC.main(["--archive-ledger", str(old)], records=alternate) == 1
    assert "kit's data directory" in capsys.readouterr().out


@pytest.mark.parametrize("operation", ["clone", "move"])
def test_relative_content_hash_keeps_relocated_fleet_seeded(fleet, tmp_path, monkeypatch, operation):
    root, old, active, projects = fleet
    assert REC.main(["--archive-ledger", str(old)], records=active) == 0
    archive = root / "scope_archive.jsonl"
    before = archive.read_bytes()
    relocated = tmp_path / "relocated"
    relocated.mkdir()
    if operation == "clone":
        shutil.copytree(root, relocated / "data")
    else:
        shutil.move(str(root), relocated / "data")
    for module in (A, REC.batch_authority):
        monkeypatch.setattr(module, "HERE", relocated / "scripts" / "migration_kit")
    new_active = relocated / "data" / active.relative_to(root)
    new_old = relocated / "data" / old.relative_to(root)
    assert gate(new_active, projects)[0]
    ok, why = gate(new_active, projects, OLD)
    assert not ok and "scope archive" in why, why
    assert REC.main(["--archive-ledger", str(new_old)], records=new_active) == 0
    assert (relocated / "data" / "scope_archive.jsonl").read_bytes() == before
    row = json.loads(before.decode().splitlines()[0])
    # Absolute source provenance may be retained, but cannot participate in the content hash.
    expected = {"ledger": str(old.relative_to(root)), "aget": row["aget"], "entry": row["entry"]}
    assert row["content_sha256"] == A.archive_hash(expected)


@pytest.mark.parametrize("corruption", ["{bad json", "[]", ""])
def test_corrupt_sibling_names_file_and_actionable_repair(fleet, corruption):
    root, old, active, projects = fleet
    assert REC.main(["--archive-ledger", str(old)], records=active) == 0
    directory = root / "notes_ledger"
    directory.mkdir()
    bad = directory / "records.json"
    bad.write_text(corruption)
    ok, why = gate(active, projects)
    assert not ok and str(bad) in why, why
    assert "repair or move it out of the data folder" in why, why


def test_legacy_archive_stays_seeded_at_original_root(fleet):
    root, old, active, projects = fleet
    assert REC.main(["--archive-ledger", str(old)], records=active) == 0
    archive = root / "scope_archive.jsonl"
    row = json.loads(archive.read_text())
    row.pop("ledger_relative", None)
    row["content_sha256"] = A.archive_hash({k: row[k] for k in ("ledger", "aget", "entry")})
    del row["sha256"]
    row["sha256"] = A.archive_hash(row)
    archive.write_text(A.archive_json(row) + "\n")
    doc = json.loads(active.read_text())
    doc["scope_archive_anchor"]["chain"] = A.archive_chain([row])
    active.write_text(json.dumps(doc))
    ok, why = gate(active, projects)
    assert ok, why
    ok, why = gate(active, projects, OLD)
    assert not ok and "scope archive" in why, why
    # Explicit seeding adds the portable identity without rewriting the old row or losing taint.
    before = archive.read_bytes()
    assert REC.main(["--archive-ledger", str(old)], records=active) == 0
    assert archive.read_bytes().startswith(before)
    assert len(archive.read_text().splitlines()) == 2
    assert gate(active, projects)[0]
    assert not gate(active, projects, OLD)[0]
