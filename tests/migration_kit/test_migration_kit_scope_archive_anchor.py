"""C32 R10: complete archive bound to active ledger; the launch gate only reads."""
import hashlib
import json
import os
from pathlib import Path

import pytest
from test_migration_kit_scope_archive import A, REC, AGET, OLD, LAUNCH, seed_ledger, archive_path
from test_migration_kit_batch_authority import SID, entry, prompt, records, transcript

CONFIRM = f"GO supervisor - the old scope override for {AGET} no longer applies"


def anchored(tmp_path):
    f, d = seed_ledger(tmp_path, current=True)
    doc = json.loads(f.read_text())
    doc["scope_overrides"]["example-extra-aget"] = {"batches": ["99"], "source": "older terms"}
    f.write_text(json.dumps(doc))
    transcript(tmp_path, [prompt("t1", "typed", OLD), prompt("t2", "typed", LAUNCH),
                          prompt("t3", "typed", CONFIRM)])
    assert REC.main(["--archive-ledger", str(f)], records=f) == 0
    assert REC.main(["--session", SID, "--retire-scope", AGET, "--principal-line", CONFIRM],
                    records=f, projects_dir=d) == 0
    doc = json.loads(f.read_text())
    doc["scope_overrides"] = {}
    f.write_text(json.dumps(doc))
    return f, d


def gate(f, d, batch="12"):
    return A.check(batch, records=f, projects_dir=d, act="launch", entry=(batch, entry(LAUNCH)))


@pytest.mark.parametrize("damage", ["delete", "empty", "first-row", "last-row", "swap", "replace"])
@pytest.mark.parametrize("batch", ["12", "99"])
def test_loss_and_mismatch_refuse_every_batch_without_recreation(tmp_path, damage, batch):
    f, d = anchored(tmp_path)
    arc = archive_path()
    rows = arc.read_text().splitlines(keepends=True)
    if damage == "delete":
        arc.unlink()
    else:
        arc.write_text({"empty": "", "first-row": "".join(rows[1:]), "last-row": "".join(rows[:-1]),
                        "swap": "".join(reversed(rows)), "replace": rows[1] * len(rows)}[damage])
    before = (f.read_bytes(), arc.read_bytes() if arc.exists() else None)
    ok, why = gate(f, d, batch)
    assert not ok, why
    assert "restore" in why and "archive" in why, why
    assert (f.read_bytes(), arc.read_bytes() if arc.exists() else None) == before
    assert REC.main(["--anchor-archive"], records=f) == 1


def test_unanchored_scope_history_refuses_without_gate_write(tmp_path):
    f, d = seed_ledger(tmp_path, current=True)
    before = f.read_bytes()
    ok, why = gate(f, d)
    assert not ok and "--archive-ledger" in why, why
    assert not archive_path().exists()
    assert f.read_bytes() == before


def test_anchor_format_and_read_only_gate(tmp_path, monkeypatch):
    monkeypatch.delenv("AGET_MIGRATION_SCOPE_ARCHIVE")
    ledger = tmp_path / "data" / "current"
    ledger.mkdir(parents=True)
    f, d = anchored(ledger)
    arc = A.scope_archive_path(f)
    rows = [json.loads(line) for line in arc.read_text().splitlines()]
    chain = ""
    for row in rows:
        chain = hashlib.sha256((chain + row["sha256"]).encode("ascii")).hexdigest()
    assert json.loads(f.read_text())["scope_archive_anchor"] == {
        "path": "../scope_archive.jsonl", "rows": len(rows), "chain": chain}
    before = (f.read_bytes(), arc.read_bytes())
    assert gate(f, d)[0]
    assert (f.read_bytes(), arc.read_bytes()) == before


def test_extra_rows_require_explicit_reanchor(tmp_path):
    f, d = anchored(tmp_path)
    arc = archive_path()
    arc.write_bytes(arc.read_bytes() + arc.read_bytes().splitlines(keepends=True)[0])
    ok, why = gate(f, d)
    assert not ok and "re-anchor" in why and "--anchor-archive" in why, why
    assert REC.main(["--anchor-archive"], records=f) == 0
    assert gate(f, d)[0]


@pytest.mark.parametrize("damage", [None, "invalid", "torn"])
def test_migrate_previous_round_archive_after_verifying_every_row(tmp_path, damage):
    f, d = anchored(tmp_path)
    doc = json.loads(f.read_text())
    del doc["scope_archive_anchor"]
    f.write_text(json.dumps(doc))
    if damage:
        with archive_path().open("a") as stream:
            stream.write("{broken\n" if damage == "invalid" else "{torn")
    before = (f.read_bytes(), archive_path().read_bytes())
    ok, why = gate(f, d)
    assert not ok and "--anchor-archive" in why, why
    assert REC.main(["--anchor-archive", "--dry-run"], records=f) == (1 if damage else 0)
    assert (f.read_bytes(), archive_path().read_bytes()) == before
    assert REC.main(["--anchor-archive"], records=f) == (1 if damage else 0)
    assert archive_path().read_bytes() == before[1]
    if not damage:
        assert gate(f, d)[0]


def test_production_ignores_env_override(tmp_path, monkeypatch):
    monkeypatch.delenv("AGET_MIGRATION_TEST_MODE", raising=False)
    for module in (A, REC.batch_authority):
        monkeypatch.setattr(module, "HERE", tmp_path / "scripts" / "migration_kit")
    ledger = tmp_path / "data" / "current_ledger"
    ledger.mkdir(parents=True)
    f, d = seed_ledger(ledger, current=True)
    monkeypatch.setenv("AGET_MIGRATION_SCOPE_ARCHIVE", "/dev/null")
    assert REC.main(["--archive-ledger", str(f)], records=f) == 0
    assert A.scope_archive_path(f) == ledger.parent / "scope_archive.jsonl"
    assert json.loads(f.read_text())["scope_archive_anchor"]["path"] == "../scope_archive.jsonl"
    monkeypatch.setenv("AGET_MIGRATION_SCOPE_ARCHIVE", "elsewhere.jsonl")
    assert A.scope_launch_refusal(LAUNCH, "12", f, projects_dir=d) is None


def test_relative_override_resolves_from_ledger_directory(tmp_path, monkeypatch):
    monkeypatch.setenv("AGET_MIGRATION_SCOPE_ARCHIVE", "archive/scope.jsonl")
    f, d = seed_ledger(tmp_path, current=True)
    assert REC.main(["--archive-ledger", str(f)], records=f) == 0
    assert (tmp_path / "archive" / "scope.jsonl").is_file()
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    monkeypatch.chdir(elsewhere)
    assert A.scope_launch_refusal(LAUNCH, "12", f, projects_dir=d) is None
    assert json.loads(f.read_text())["scope_archive_anchor"]["path"] == "archive/scope.jsonl"


def test_changed_override_refuses_without_recreation(tmp_path, monkeypatch):
    f, d = anchored(tmp_path)
    other = tmp_path / "other.jsonl"
    monkeypatch.setenv("AGET_MIGRATION_SCOPE_ARCHIVE", str(other))
    ok, why = gate(f, d)
    assert not ok and "path" in why and "override" in why, why
    assert not other.exists()
    assert REC.main(["--archive-ledger", str(f)], records=f) == 1
    assert not other.exists()


@pytest.mark.parametrize("kind", ["devnull", "directory", "fifo", "same-ledger"])
def test_non_regular_or_ledger_archive_refused(tmp_path, monkeypatch, kind):
    f, d = seed_ledger(tmp_path, current=True)
    target = tmp_path / "bad"
    if kind == "devnull":
        target = Path("/dev/null")
    elif kind == "directory":
        target.mkdir()
    elif kind == "fifo":
        os.mkfifo(target)
    else:
        target = f
    monkeypatch.setenv("AGET_MIGRATION_SCOPE_ARCHIVE", str(target))
    before = f.read_bytes()
    assert REC.main(["--archive-ledger", str(f)], records=f) == 1
    assert not gate(f, d)[0]
    assert f.read_bytes() == before


def test_foreign_seed_requires_flag_and_updates_active_archive_only(tmp_path, monkeypatch, capsys):
    monkeypatch.delenv("AGET_MIGRATION_SCOPE_ARCHIVE")
    active_dir = tmp_path / "active" / "data" / "current"
    active_dir.mkdir(parents=True)
    active = records(active_dir)
    foreign = tmp_path / "foreign"
    foreign.mkdir()
    old, _ = seed_ledger(foreign)
    before = (active.read_bytes(), old.read_bytes())
    assert REC.main(["--archive-ledger", str(old)], records=active) == 1
    assert "--allow-foreign-ledger" in capsys.readouterr().out
    assert (active.read_bytes(), old.read_bytes()) == before
    arc = active_dir.parent / "scope_archive.jsonl"
    assert not arc.exists()
    args = ["--archive-ledger", str(old), "--allow-foreign-ledger"]
    assert REC.main(args, records=active) == 0
    assert "archived 1" in capsys.readouterr().out
    row = json.loads(arc.read_text())
    assert row["ledger"] == str(old.resolve())
    assert json.loads(active.read_text())["scope_archive_anchor"]["rows"] == 1
    assert old.read_bytes() == before[1]
    assert REC.main(args, records=active) == 0
    assert "archived 0" in capsys.readouterr().out


def test_retirement_cannot_reuse_old_scope_grant(tmp_path):
    f, d = seed_ledger(tmp_path, current=True)
    before = f.read_bytes()
    assert REC.main(["--session", SID, "--retire-scope", AGET, "--principal-line", OLD],
                    records=f, projects_dir=d) == 1
    assert f.read_bytes() == before
    assert not archive_path().exists()


@pytest.mark.parametrize("operation", ["launch", "retire", "seed"])
def test_dry_run_never_writes_archive_or_ledger(tmp_path, operation):
    f, d = seed_ledger(tmp_path, current=True)
    transcript(tmp_path, [prompt("t1", "typed", LAUNCH), prompt("t2", "typed", CONFIRM)])
    before = f.read_bytes()
    args = {"launch": ["--session", SID, "--key", "12", "--act", "launch", "--line", LAUNCH],
            "retire": ["--session", SID, "--retire-scope", AGET, "--principal-line", CONFIRM],
            "seed": ["--archive-ledger", str(f)]}[operation]
    REC.main([*args, "--dry-run"], records=f, projects_dir=d)
    assert f.read_bytes() == before
    assert not archive_path().exists()
