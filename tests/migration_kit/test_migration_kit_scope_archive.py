"""C32 / v337prep:R9: retirement and later ledgers cannot untaint a scope quote."""
import builtins
import hashlib
import json
import os
from pathlib import Path

import pytest

from test_migration_kit_batch_authority import A, REC, SID, entry, packet, prompt, records, transcript

AGET = "example-core-aget"
OLD = "GO supervisor - batch 12 for example-core: docs may be written"
NEW = "GO supervisor - batch 12t for example-core: docs under reviewed terms"
LAUNCH = "GO supervisor - launch batch 12 for example-core as prepared"
RETIRE = "GO supervisor - the old scope override for example-core-aget no longer applies"


def archive_path():
    return Path(os.environ["AGET_MIGRATION_SCOPE_ARCHIVE"])


def seed_ledger(tmp_path, *, current=False, ov=None):
    f = records(tmp_path, {"12": entry(OLD)})
    if ov is None:
        ov = {"batches": ["12"], "source": f'principal: "{OLD}"'}
        if current:
            ov["history"] = [{"line": OLD, "batches_added": ["12"]}]
    doc = json.loads(f.read_text())
    doc["scope_overrides"] = {AGET: ov}
    f.write_text(json.dumps(doc))
    d = transcript(tmp_path, [prompt(f"t{i}", "typed", text)
                              for i, text in enumerate((OLD, NEW, LAUNCH, RETIRE), 1)])
    return f, d


def retire(f, d, line=RETIRE, extra=()):
    return REC.main(["--session", SID, "--retire-scope", AGET, "--principal-line", line, *extra],
                    records=f, projects_dir=d)


@pytest.mark.parametrize("variant", ["A", "B", "C", "D"])
@pytest.mark.parametrize("current", [False, True], ids=["legacy", "current"])
def test_c32_seventh_review_high_and_variants_stay_tainted(tmp_path, variant, current):
    f, d = seed_ledger(tmp_path, current=current)
    assert retire(f, d) == 0
    assert AGET not in json.loads(f.read_text())["scope_overrides"]
    if variant == "A":
        p = packet(tmp_path, AGET, tmp_path)
        assert REC.main(["--session", SID, "--key", "12", "--line", OLD, "--packet", str(p),
                         "--scope-override", f"{AGET}=docs/"], records=f, projects_dir=d) == 1
    elif variant == "B":
        p = packet(tmp_path, AGET, tmp_path)
        assert REC.main(["--session", SID, "--key", "12t", "--line", NEW, "--packet", str(p),
                         "--scope-override", f"{AGET}=docs/"], records=f, projects_dir=d) == 0
    else:
        if variant == "C":
            f.rename(f.with_name("records.aside.json"))
            f.write_text("{}")
            assert REC.main(["--anchor-archive"], records=f) == 0
        assert REC.main(["--session", SID, "--key", "12", "--act", "launch", "--line", OLD],
                        records=f, projects_dir=d) == 1
    ok, why = A.check("12", records=f, projects_dir=d, act="launch", entry=("12", entry(OLD)))
    assert not ok and "archive" in why, why
    # A separate principal launch prompt still works after retirement.
    assert REC.main(["--session", SID, "--key", "12", "--act", "launch", "--line", LAUNCH],
                    records=f, projects_dir=d) == 0
    assert A.check("12", records=f, projects_dir=d, act="launch")[0]


@pytest.mark.parametrize("current", [False, True])
@pytest.mark.parametrize("removal", ["entry", "ledger", "directory"])
def test_c32_seeded_archive_survives_hand_removal_and_ledger_move(tmp_path, monkeypatch, current, removal):
    monkeypatch.delenv("AGET_MIGRATION_SCOPE_ARCHIVE")
    ledger = tmp_path / "release-one"
    ledger.mkdir()
    f, d = seed_ledger(ledger, current=current)
    assert REC.main(["--archive-ledger", str(f)], records=f) == 0
    A.check("12", records=f, projects_dir=d, act="launch")
    archive = tmp_path / "scope_archive.jsonl"
    assert archive.exists()
    before = archive.read_bytes()
    if removal == "entry":
        doc = json.loads(f.read_text())
        del doc["scope_overrides"][AGET]
        f.write_text(json.dumps(doc))
    elif removal == "ledger":
        f.rename(f.with_name("records.aside.json"))
        f.write_text("{}")
    else:
        ledger.rename(tmp_path / "release-aside")
        d = tmp_path / "release-aside" / "projects"
        ledger = tmp_path / "release-two"
        ledger.mkdir()
        f = ledger / "records.json"
        f.write_text("{}")
    if removal in ("ledger", "directory"):
        assert REC.main(["--anchor-archive"], records=f) == 0
    for batch in ("12", "99"):
        why = A.scope_launch_refusal(OLD, batch, records=f, projects_dir=d)
        assert why and "archive" in why
    assert archive.read_bytes() == before


FREE_TEXT = [
    ("source", "principal typed: '{line}'"),
    ("source", '2026-10-01T12:00:00Z principal: "{line}"'),
    ("source", 'principal adopted pasted block: <pasted_content id="example">{line}</pasted_content>'),
    ("source_7t", 'principal extension: "{line}"'),
    ("reason", "reason: the principal confirmed '{line}'"),
]


@pytest.mark.parametrize("field,style", FREE_TEXT)
@pytest.mark.parametrize("history", [False, True], ids=["entry-field", "history-field"])
@pytest.mark.parametrize("current", [False, True])
def test_c32_reverse_containment_retains_real_free_text_styles(tmp_path, field, style, history, current):
    raw = style.format(line=OLD.replace(" ", "  "))
    ov = {"batches": ["12"]}
    if current or history:
        ov["history"] = [{"line": NEW, "batches_added": ["12"]}] if current else [{}]
    (ov["history"][0] if history else ov)[field] = raw
    f, d = seed_ledger(tmp_path, ov=ov)
    assert retire(f, d) == 0
    for batch in ("12", "99"):
        why = A.scope_launch_refusal(OLD, batch, records=f, projects_dir=d)
        assert why and "archive" in why, why
    before = f.read_bytes()
    assert REC.main(["--session", SID, "--key", "12", "--act", "launch", "--line", OLD],
                    records=f, projects_dir=d) == 1
    assert f.read_bytes() == before


def test_c32_archive_history_containment_and_reverse_guard(tmp_path):
    quote = "GO supervisor - batch 12 for example-core: reviewed terms"
    ov = {"batches": ["12"], "source": "prefix " + "x" * 24 + " suffix",
          "history": [{"line": quote, "batches_added": ["12"]}]}
    f, d = seed_ledger(tmp_path, ov=ov)
    assert retire(f, d) == 0
    assert A.scope_launch_refusal("before " + quote + " after", "99", records=f)
    assert A.scope_launch_refusal("x" * 24, "99", records=f)
    assert A.scope_launch_refusal("x" * 23, "99", records=f) is None
    # Reverse containment uses the FULL prompt, not a recorded substring of it.
    assert A.scope_launch_refusal("unquoted prefix " + "x" * 24, "99", records=f) is None
    assert A.scope_launch_refusal(quote.lower(), "99", records=f) is None


@pytest.mark.parametrize("bad", ["GO supervisor - the example-core override is retired but this was never typed",
                                  RETIRE + " extra words", "yes"])
def test_c32_retirement_requires_whole_typed_principal_confirmation(tmp_path, bad):
    f, d = seed_ledger(tmp_path)
    before = f.read_bytes()
    assert retire(f, d, bad) == 1
    assert f.read_bytes() == before
    assert not archive_path().exists()


def test_c32_retirement_rejects_substring_of_typed_prompt(tmp_path):
    f, d = seed_ledger(tmp_path)
    transcript(tmp_path, [prompt("t1", "typed", RETIRE + "; wait for the review")])
    assert retire(f, d) == 1
    assert AGET in json.loads(f.read_text())["scope_overrides"]


def test_c32_seed_archives_raw_entries_without_changing_previous_ledger(tmp_path, monkeypatch):
    f, _ = seed_ledger(tmp_path)
    doc = json.loads(f.read_text())
    doc["scope_overrides"]["example-extra-aget"] = {
        "batches": ["7t"], "reason": "raw\n  reason with Unicode: café",
        "history": [{"line": NEW, "source_7t": "raw history", "scope": "docs/"}],
        "nested": {"text": "raw nested text"}}
    f.write_text(json.dumps(doc))
    before = f.read_bytes()
    # Seed needs no transcript or session, and the environment may place the archive outside the ledger tree.
    monkeypatch.setenv("AGET_MIGRATION_SCOPE_ARCHIVE", str(tmp_path / "shared" / "scope_archive.jsonl"))
    active_dir = tmp_path / "current"
    active_dir.mkdir()
    active = records(active_dir)
    assert REC.main(["--archive-ledger", str(f)], records=active) == 0
    assert f.read_bytes() == before
    rows = [json.loads(line) for line in archive_path().read_text().splitlines()]
    assert len(rows) == 2
    for row in rows:
        assert row["recorded_at"]
        assert row["ledger"] == str(f.resolve())
        ov = doc["scope_overrides"][row["aget"]]
        assert row["entry"] == ov
        assert row["batches"] == ov["batches"]
        digest = row.pop("sha256")
        canonical = json.dumps(row, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
        assert hashlib.sha256(canonical.encode()).hexdigest() == digest
    values = set(rows[1]["fields"].values())
    assert {"raw\n  reason with Unicode: café", NEW, "raw history", "docs/", "raw nested text"} <= values
    archived = archive_path().read_bytes()
    assert REC.main(["--archive-ledger", str(f)], records=active) == 0
    assert archive_path().read_bytes() == archived


def test_c32_recorder_archives_before_every_scope_mutation_and_retirement(tmp_path, monkeypatch):
    d = transcript(tmp_path, [prompt("t1", "typed", OLD), prompt("t2", "typed", NEW),
                              prompt("t3", "typed", RETIRE)])
    f = records(tmp_path)
    p = packet(tmp_path, AGET, tmp_path)
    original_write = REC.batch_authority.write_scope_records
    snapshots = []

    def checked_write(path, doc):
        if path == f:
            rows = [json.loads(line) for line in archive_path().read_text().splitlines()]
            old = json.loads(f.read_text()).get("scope_overrides", {}).get(AGET)
            new = doc.get("scope_overrides", {}).get(AGET)
            for ov in (old, new):
                if ov is not None:
                    assert any(row["entry"] == ov for row in rows)
            snapshots.append(archive_path().read_bytes())
        return original_write(path, doc)

    monkeypatch.setattr(REC.batch_authority, "write_scope_records", checked_write)
    for key, line in (("12", OLD), ("12t", NEW)):
        assert REC.main(["--session", SID, "--key", key, "--line", line, "--packet", str(p),
                         "--scope-override", f"{AGET}=docs/"], records=f, projects_dir=d) == 0
    assert retire(f, d) == 0
    assert len(snapshots) == 3
    assert all(later.startswith(earlier) for earlier, later in zip(snapshots, snapshots[1:]))


def test_c32_archive_only_opened_for_append_by_all_tool_paths(tmp_path, monkeypatch):
    f, d = seed_ledger(tmp_path)
    archive = archive_path()
    original_open, original_path_open, original_os_open = builtins.open, Path.open, os.open
    writes = []

    def check_mode(path, mode):
        if not isinstance(path, int) and Path(path) == archive and any(c in mode for c in "wax+"):
            assert mode in ("a", "ab", "a+", "a+b"), mode
            writes.append(mode)

    def checked_open(path, mode="r", *args, **kwargs):
        check_mode(path, mode)
        return original_open(path, mode, *args, **kwargs)

    def checked_path_open(path, mode="r", *args, **kwargs):
        check_mode(path, mode)
        return original_path_open(path, mode, *args, **kwargs)

    def checked_os_open(path, flags, *args, **kwargs):
        if Path(path) == archive and flags & (os.O_WRONLY | os.O_RDWR):
            assert flags & os.O_APPEND and not flags & os.O_TRUNC
            writes.append(flags)
        return original_os_open(path, flags, *args, **kwargs)

    monkeypatch.setattr(builtins, "open", checked_open)
    monkeypatch.setattr(Path, "open", checked_path_open)
    monkeypatch.setattr(os, "open", checked_os_open)
    assert REC.main(["--archive-ledger", str(f)], records=f) == 0
    prefix = archive.read_bytes()
    A.check("12", records=f, projects_dir=d, act="launch")
    assert archive.read_bytes() == prefix
    assert retire(f, d) == 0
    p = packet(tmp_path, AGET, tmp_path)
    assert REC.main(["--session", SID, "--key", "12t", "--line", NEW, "--packet", str(p),
                     "--scope-override", f"{AGET}=docs/"], records=f, projects_dir=d) == 0
    assert archive.read_bytes().startswith(prefix)
    assert writes


@pytest.mark.parametrize("operation", ["retire", "scope", "launch"])
def test_c32_archive_failure_preserves_ledger(tmp_path, operation):
    f, d = seed_ledger(tmp_path, current=True)
    archive_path().mkdir()  # Cannot read or append a JSONL file here.
    before = f.read_bytes()
    if operation == "retire":
        rc = retire(f, d)
    elif operation == "scope":
        p = packet(tmp_path, AGET, tmp_path)
        rc = REC.main(["--session", SID, "--key", "12t", "--line", NEW, "--packet", str(p),
                       "--scope-override", f"{AGET}=docs/"], records=f, projects_dir=d)
    else:
        rc = REC.main(["--session", SID, "--key", "12", "--act", "launch", "--line", LAUNCH],
                       records=f, projects_dir=d)
    assert rc == 1
    assert f.read_bytes() == before


def test_c32_push_ignores_archive_and_leaves_it_untouched(tmp_path):
    f, d = seed_ledger(tmp_path)
    archive_path().write_text("not JSON\n")
    line = "GO supervisor - push the commits of batch 12"
    transcript(tmp_path, [prompt("t1", "typed", line)])
    p = packet(tmp_path, AGET, tmp_path)
    before = archive_path().read_bytes()
    assert REC.main(["--session", SID, "--key", "12", "--act", "push", "--line", line,
                     "--packet", str(p)], records=f, projects_dir=d) == 0
    assert A.push_authority("12", hashlib.sha256(p.read_bytes()).hexdigest(), records=f, projects_dir=d)[0]
    assert archive_path().read_bytes() == before
