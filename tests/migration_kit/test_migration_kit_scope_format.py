"""C32 / v337prep:R8: old scope records cannot be converted; push is unaffected."""
import hashlib
import json

import pytest

from test_migration_kit_batch_authority import A, REC, SID, NEUTRAL_SCOPE, OVERRIDE12, LAUNCH12
from test_migration_kit_batch_authority import entry, packet, prompt, records, transcript, anchor_ledger


OLD_FORMAT_SCOPES = [
    pytest.param({"batches": ["12"]}, id="no-history"),
    pytest.param({"batches": ["12"], "history": []}, id="empty-history"),
    pytest.param({"batches": ["12"], "history": [{"scope": "docs/"}]}, id="missing-line"),
    pytest.param({"batches": ["12"], "history": [{"line": ""}]}, id="empty-line"),
    pytest.param({"batches": ["12"], "history": [{"line": "  "}]}, id="blank-line"),
    pytest.param({"batches": ["12"], "history": [{"line": 42}]}, id="non-string-line"),
    pytest.param({"batches": ["12"], "history": [None]}, id="non-dict-item"),
    pytest.param({"batches": ["12"], "history": "broken"}, id="non-list-history"),
    pytest.param({"batches": ["12"], "history": [{"line": "reviewed terms"}, {}]}, id="mixed-history"),
    pytest.param(None, id="non-dict-entry"),
    pytest.param({}, id="no-batches-or-history"),
    pytest.param({"history": [{"line": "reviewed terms", "batches_added": ["12"]}]}, id="no-batches"),
    pytest.param({"batches": "12", "history": [{"line": "reviewed terms", "batches_added": ["12"]}]},
                 id="non-list-batches"),
    pytest.param({"batches": ["12"], "history": [{"line": "reviewed terms"}]}, id="no-line-batches"),
    pytest.param({"batches": ["12"], "history": [{"line": "reviewed terms", "batches_added": "12"}]},
                 id="non-list-line-batches"),
    pytest.param({"batches": ["12", "13"],
                  "history": [{"line": "reviewed terms", "batches_added": ["13"]}]}, id="partial-coverage"),
]


def old_format_ledger(tmp_path, ov, mixed):
    f = records(tmp_path)
    doc = json.loads(f.read_text())
    ovs = {}
    if mixed:
        ovs["example-current-aget"] = {"batches": ["5"],
                                       "history": [{"line": "current reviewed terms", "batches_added": ["5"]}]}
    ovs["example-old-aget"] = ov
    if mixed:
        ovs["example-second-old-aget"] = {"batches": ["6"]}
    doc["scope_overrides"] = ovs
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    return f


def assert_removal_reason(why, f, mixed=False):
    assert "example-old-aget" in why, why
    if mixed:
        assert "example-second-old-aget" in why, why
        assert "example-current-aget" not in why, why
    assert "ask the principal to confirm the old scope override no longer applies" in why, why
    assert "--retire-scope example-old-aget" in why, why
    assert '--principal-line "GO supervisor - the old scope override for example-old-aget no longer applies"' in why, why
    assert "archive" in why, why
    assert "move the ledger aside" not in why, why


@pytest.mark.parametrize("ov", OLD_FORMAT_SCOPES)
@pytest.mark.parametrize("mixed", [False, True], ids=["old-only", "mixed-ledger"])
@pytest.mark.parametrize("batch", ["12", "13", "99"], ids=["governed", "not-governed", "unrelated"])
@pytest.mark.parametrize("generic", [False, True], ids=["act-key", "generic-key"])
def test_c32_old_format_anywhere_refuses_gate_and_recorder_with_same_remedy(tmp_path, capsys, ov, mixed,
                                                                          batch, generic):
    line = f"GO supervisor - launch batch {batch} for example-core as prepared"
    d = transcript(tmp_path, [prompt("t1", "typed", line)])
    f = old_format_ledger(tmp_path, ov, mixed)
    doc = json.loads(f.read_text())
    key = batch if generic else f"{batch}:launch"
    doc["batch_authority"][key] = entry(line)
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    ok, why = A.check(batch, records=f, projects_dir=d, act="launch")
    assert not ok, why
    assert_removal_reason(why, f, mixed)
    shared_reason = A.scope_launch_refusal(line, batch, records=f, projects_dir=d)
    assert shared_reason in why
    doc["batch_authority"] = {}  # duplicate-key protection must not mask the format refusal
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    before = f.read_bytes()
    assert REC.main(["--session", SID, "--key", batch, "--act", "launch", "--line", line],
                    records=f, projects_dir=d) == 1
    assert shared_reason in capsys.readouterr().out
    assert f.read_bytes() == before


@pytest.mark.parametrize("line", [NEUTRAL_SCOPE, OVERRIDE12, LAUNCH12, "bad"])
def test_c32_old_format_remedy_precedes_wording_or_missing_launch_evidence(tmp_path, capsys, line):
    d = transcript(tmp_path, [])
    f = old_format_ledger(tmp_path, {"batches": ["5"]}, False)
    assert_removal_reason(A.scope_launch_refusal(line, "99", records=f, projects_dir=d), f)
    ok, why = A.check("99", records=f, projects_dir=d, act="launch")
    assert not ok
    assert_removal_reason(why, f)
    assert REC.main(["--session", SID, "--key", "99", "--act", "launch", "--line", line],
                    records=f, projects_dir=d) == 1
    assert_removal_reason(capsys.readouterr().out, f)


def test_c32_old_format_scope_does_not_affect_fixed_form_push_authority(tmp_path):
    # R7 explicitly leaves --act push (recorder and gate) unaffected by old-format scope entries.
    line = "GO supervisor - push the commits of batch 99"
    d = transcript(tmp_path, [prompt("t1", "typed", line)])
    f = old_format_ledger(tmp_path, {"batches": ["99"]}, True)
    p = packet(tmp_path, "example-core-aget", tmp_path)
    assert REC.main(["--session", SID, "--key", "99", "--act", "push", "--line", line, "--packet", str(p)],
                    records=f, projects_dir=d) == 0
    ok, why = A.check("99", records=f, projects_dir=d, act="push")
    assert ok, why
    digest = hashlib.sha256(p.read_bytes()).hexdigest()
    assert A.push_authority("99", digest, records=f, projects_dir=d)[0]


@pytest.mark.parametrize("ov", OLD_FORMAT_SCOPES)
@pytest.mark.parametrize("dry_run", [False, True])
def test_c32_recorder_refuses_old_scope_shapes_without_conversion_or_traceback(tmp_path, capsys, ov, dry_run):
    line = "GO supervisor - batch 12t for example-old: docs under reviewed terms"
    d = transcript(tmp_path, [prompt("t1", "typed", line)])
    f = old_format_ledger(tmp_path, ov, False)
    p = packet(tmp_path, "example-old-aget", tmp_path)
    before = f.read_bytes()
    args = ["--session", SID, "--key", "12t", "--line", line, "--packet", str(p),
            "--scope-override", "example-old-aget=docs/"] + (["--dry-run"] if dry_run else [])
    assert REC.main(args, records=f, projects_dir=d) == 1
    out = capsys.readouterr().out
    assert "REFUSED, nothing written" in out
    assert_removal_reason(out, f)
    assert A.scope_launch_refusal(None, "99", records=f) in out
    assert f.read_bytes() == before


def test_c32_sixth_review_old_quote_cannot_be_lost_by_rerecording(tmp_path, capsys):
    old = "GO supervisor - batch 12 for example-core: docs may be written"
    new = "GO supervisor - batch 12t for example-core: docs under reviewed terms"
    d = transcript(tmp_path, [prompt("t1", "typed", old), prompt("t2", "typed", new)])
    f = records(tmp_path)
    doc = json.loads(f.read_text())
    doc["scope_overrides"] = {"example-core-aget": {"batches": ["12"],
                              "source": f'principal, typed, session {SID}: "{old}"'}}
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    p = packet(tmp_path, "example-core-aget", tmp_path)
    before = f.read_bytes()
    launch = ["--session", SID, "--key", "12", "--act", "launch", "--line", old]
    assert REC.main(launch, records=f, projects_dir=d) == 1
    assert REC.main(["--session", SID, "--key", "12t", "--line", new, "--packet", str(p),
                     "--scope-override", "example-core-aget=docs/"], records=f, projects_dir=d) == 1
    assert REC.main(launch, records=f, projects_dir=d) == 1
    assert "old-format" in capsys.readouterr().out
    assert f.read_bytes() == before
    ok, why = A.check("12", records=f, projects_dir=d, act="launch", entry=("12:launch", entry(old)))
    assert not ok and "old-format" in why, why


@pytest.mark.parametrize("use_extension", [False, True])
def test_c32_sixth_review_partial_batch_coverage_is_old_format(tmp_path, capsys, use_extension):
    old = "GO supervisor - batch 10: example-core writes .gitignore and docs/ as reviewed"
    extension = "GO supervisor - batch 10 also covers the AGENTS.md version line for example-core"
    new = "GO supervisor - batch 13: example-core as batch 12 with its held commits"
    d = transcript(tmp_path, [prompt("t1", "typed", old), prompt("t2", "typed", extension),
                              prompt("t3", "typed", new)])
    line = extension if use_extension else old
    f = records(tmp_path, {"10:launch": entry(line)})
    doc = json.loads(f.read_text())
    doc["scope_overrides"] = {"example-core-aget": {
        "batches": ["10", "13"], "source": f'principal: "{new}"', "reason": f'principal: "{old}"',
        "extension": f'Extended by the principal line "{extension}"',
        "history": [{"batches_added": ["13"], "line": new}]}}
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    for batch in ("10", "13", "99"):
        ok, why = A.check(batch, records=f, projects_dir=d, act="launch")
        assert not ok and "old-format" in why, why
    doc["batch_authority"] = {}
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    before = f.read_bytes()
    assert REC.main(["--session", SID, "--key", "10", "--act", "launch", "--line", line],
                    records=f, projects_dir=d) == 1
    assert "old-format" in capsys.readouterr().out
    assert f.read_bytes() == before


@pytest.mark.parametrize("ovs", [None, [], "broken"])
def test_c32_recorder_refuses_malformed_scope_mapping(tmp_path, capsys, ovs):
    line = "GO supervisor - batch 12 for example-core: docs under reviewed terms"
    d = transcript(tmp_path, [prompt("t1", "typed", line)])
    f = records(tmp_path)
    doc = json.loads(f.read_text())
    doc["scope_overrides"] = ovs
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    p = packet(tmp_path, "example-core-aget", tmp_path)
    before = f.read_bytes()
    assert REC.main(["--session", SID, "--key", "12", "--line", line, "--packet", str(p),
                     "--scope-override", "example-core-aget=docs/"], records=f, projects_dir=d) == 1
    assert "scope_overrides is not a mapping" in capsys.readouterr().out
    assert f.read_bytes() == before


def test_c32_current_history_can_extend_with_union_coverage_and_no_new_batches(tmp_path):
    first = "GO supervisor - batch 12T for example-core: docs under reviewed terms"
    second = "GO supervisor - batch 13 for example-core: docs under reviewed terms"
    third = "GO supervisor - batches 12t and 13 for example-core: docs under reviewed terms"
    launch = "GO supervisor - launch batches 12t and 13 for example-core as prepared"
    d = transcript(tmp_path, [prompt(f"t{i}", "typed", line)
                              for i, line in enumerate((first, second, third, launch), 1)])
    f = records(tmp_path)
    p = packet(tmp_path, "example-core-aget", tmp_path)
    for key, line in (("12T", first), ("13", second), ("12t+13", third)):
        assert REC.main(["--session", SID, "--key", key, "--line", line, "--packet", str(p),
                         "--scope-override", "example-core-aget=docs/"], records=f, projects_dir=d) == 0
        assert A.scope_launch_refusal(None, "99", records=f) is None
    ov = json.loads(f.read_text())["scope_overrides"]["example-core-aget"]
    assert [h["batches_added"] for h in ov["history"]] == [["12t"], ["13"], []]
    # Existing batch normalization also applies to coverage in imported current history.
    doc = json.loads(f.read_text())
    doc["scope_overrides"]["example-core-aget"]["history"][0]["batches_added"] = ["12T"]
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    assert REC.main(["--session", SID, "--key", "12t+13", "--act", "launch", "--line", launch],
                    records=f, projects_dir=d) == 0
    for batch in ("12t", "13"):
        ok, why = A.check(batch, records=f, projects_dir=d, act="launch")
        assert ok, why


def test_c32_fully_covered_history_may_include_a_line_without_added_batches(tmp_path):
    scope = "GO supervisor - batch 12 for example-core: docs under reviewed terms"
    note = "GO supervisor - batch 12 for example-core: reviewed terms still apply"
    launch = "GO supervisor - launch batch 12 for example-core as prepared"
    d = transcript(tmp_path, [prompt("t1", "typed", scope), prompt("t2", "typed", note),
                              prompt("t3", "typed", launch)])
    f = records(tmp_path, {"12:launch": entry(launch)})
    doc = json.loads(f.read_text())
    doc["scope_overrides"] = {"example-core-aget": {"batches": ["12"], "history": [
        {"line": scope, "batches_added": ["12"]}, {"line": note}]}}
    f.write_text(json.dumps(doc))
    anchor_ledger(f)
    doc = json.loads(f.read_text())
    ok, why = A.check("12", records=f, projects_dir=d, act="launch")
    assert ok, why
