"""Tests for batch 1's launch packet (prepare_launch.py) and launcher (launch_batch.py). No launch happens here."""
import hashlib
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "scripts/migration_kit"


def load(name):
    spec = importlib.util.spec_from_file_location(name, BATCH / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


PL = load("prepare_launch")
LB = load("launch_batch")

R = {"aget": "example-x-aget", "template": "template-x-aget", "head": "a" * 40,
     "pins": {"core": "c" * 40, "template-x-aget": "t" * 40},
     "items": [{"path": "scripts/a.py", "op": "write", "staged": "/stage/a.py", "sha256": "1" * 64, "pre": "0" * 64,
                "command": "cp /stage/a.py scripts/a.py", "hash_command": "git hash-object scripts/a.py"},
               {"path": "tests/fixtures/f.json", "op": "write", "staged": "/stage/f.json", "sha256": "2" * 64,
                "pre": "absent", "command": "cp /stage/f.json tests/fixtures/f.json",
                "mkdir": "mkdir -p tests/fixtures", "closure": True, "why": "import closure",
                "hash_command": "git hash-object tests/fixtures/f.json"},
               {"path": "scripts/b.py", "op": "hold", "kind": "authored", "authored_lines": 3, "staged": "/stage/b.py",
                "authored_ids": ["1" * 64, "2" * 64, "3" * 64]},
               {"path": "scripts/c.py", "op": "noop"}],
     "pre_dirty": [".aget/state/s.json"], "untracked_protected": [".claude/skills/u/SKILL.md"],
     "commit_protected": ["AGENTS.md"]}


def test_prompt_never_pushes_and_names_the_protected_commit():
    """Asserts the prompt TEXT says "Do NOT push"; whether the session can push is not tested here."""
    p = PL.prompt(R, "att-1", ["AGENTS.md", ".claude/skills/u/SKILL.md"])
    assert "Do NOT push" in p
    assert "AGENTS.md (stage them; never edit them)" in p
    assert "Do not use the Skill, Agent, Task or Monitor tools" in p


def test_prompt_records_the_packets_route_and_tolerates_carriers_already_at_target(monkeypatch):
    """Batch 8 V3.7 (framework Aget's finding): the prompt wrote route "a1 … batch 1" into version.json and the receipt
    while the packet's route was "a2 … batch 8"; main() ignored --route for the prompt."""
    import inspect
    monkeypatch.setattr(PL, "ROUTE", "a2 + b1 route-b-restricted-hooks (detective), batch 8")
    p = PL.prompt(R, "att-1", [])
    assert "route 'a2 + b1 route-b-restricted-hooks (detective), batch 8'" in p and "batch 1'" not in p
    assert "leave it if it already reads 3.35.0" in p and "from 3.34.0 to 3.35.0" not in p
    assert "a string if they are strings" in p
    assert "ROUTE = a.route" in inspect.getsource(PL.main)     # --route reaches the prompt, not only the packet


def test_prompt_protects_pre_existing_work_and_records_untracked_files():
    p = PL.prompt(R, "att-1", [])
    assert ".aget/state/s.json. Do not stage, commit, edit or discard them." in p
    assert "does not track these protected files: .claude/skills/u/SKILL.md" in p


def test_prompt_places_writes_by_exact_copy_and_lists_merges_but_not_noops():
    p = PL.prompt(R, "att-1", [])
    assert "Run: cp /stage/a.py scripts/a.py" in p and "Run: mkdir -p tests/fixtures" in p
    assert "WRITE scripts/a.py" not in p  # batch 1: a re-typed WRITE lost trailing whitespace
    assert "MERGE scripts/b.py" in p and "3 line(s) of your own" in p
    assert "scripts/c.py" not in p


def test_write_set_allowlist_and_exact_commands_agree():
    ws = PL.write_set(R)
    assert "scripts/a.py" in ws and "scripts/b.py" in ws and "scripts/c.py" not in ws
    rules = PL.allowlist(R)
    assert "Bash(cp /stage/a.py scripts/a.py)" in rules and "Bash(mkdir -p tests/fixtures)" in rules
    assert "Edit(scripts/a.py)" not in rules and "Edit(scripts/b.py)" in rules
    assert all(f"Bash({c})" in rules for c in PL.VALIDATION)
    assert not any("push" in x or x.startswith("Bash(gh") for x in rules)
    assert PL.exact_commands(R)[:3] == ["cp /stage/a.py scripts/a.py", "mkdir -p tests/fixtures",
                                        "cp /stage/f.json tests/fixtures/f.json"]


def test_correction_row_4_is_sourced_from_core_even_when_the_template_ships_it(monkeypatch):
    monkeypatch.setattr(PL.P, "tag_bytes", lambda repo, tag, path: b"x")
    tpl, core = Path("/fw/template-x-aget"), Path("/fw/aget")
    for p in PL.W.CORRECTION_ROW_4:
        assert PL.source_repo(p, tpl, core) == core
    assert PL.source_repo("scripts/other.py", tpl, core) == tpl


def test_references_find_joined_paths_quoted_paths_and_imports():
    text = ('FIXTURE = REPO / "tests" / "fixtures" / "l980_session_2026_05_21_action_batch.json"\n'
            'REG = "SCRIPT_REGISTRY.yaml"\nimport health_logger\nfrom propagation_audit import x\n')
    refs = PL.references("tests/test_propose_actions_step_2_7.py", text)
    assert "tests/fixtures/l980_session_2026_05_21_action_batch.json" in refs
    assert "SCRIPT_REGISTRY.yaml" in refs
    assert "scripts/health_logger.py" in refs and "scripts/propagation_audit.py" in refs


def test_closure_adds_only_release_files_missing_from_the_payload_transitively(monkeypatch):
    tree = {"tests/test_t.py": b'F = ROOT / "tests" / "fixtures" / "f.json"\nimport helper\n"AGENTS.md"\n',
            "tests/fixtures/f.json": b"{}", "scripts/helper.py": b"import deeper\n", "scripts/deeper.py": b"",
            "scripts/in_payload.py": b"", "AGENTS.md": b"x"}
    monkeypatch.setattr(PL.P, "tag_bytes", lambda repo, tag, path: tree.get(path))
    got = PL.closure({"tests/test_t.py", "scripts/in_payload.py"}, Path("/fw/t"), Path("/fw/aget"))
    assert set(got) == {"tests/fixtures/f.json", "scripts/helper.py", "scripts/deeper.py"}  # AGENTS.md never


def test_repair_prompt_places_only_differing_files_and_never_pushes():
    """Asserts the repair prompt TEXT says "Do NOT push"; whether the session can push is not tested here."""
    r = {**R, "items": [*R["items"][:2], {"path": "scripts/v.py", "op": "verify", "sha256": "3" * 64},
                        {"path": "scripts/study_topic.py", "op": "merged", "kind": "authored",   # R3: a recorded kind
                         "authored_lines": 1}]}
    p = PL.repair_prompt(r, "att-2", "att-1")
    assert "Run: cp /stage/a.py scripts/a.py" in p and "Run: cp /stage/f.json tests/fixtures/f.json" in p
    assert "scripts/v.py" not in p and "MERGE" not in p
    assert "merge of scripts/study_topic.py" in p and "Do NOT push" in p and "REPAIR" in p
    ws = PL.write_set(r, repair=True)
    assert ".aget/version.json" not in ws and "scripts/a.py" in ws and "scripts/v.py" not in ws
    assert "Bash(git rm:*)" not in PL.allowlist(r, repair=True)


def test_placing_uses_the_sealed_placer_and_declares_the_blob_id_command(tmp_path):
    # V3.7 (2026-09-27): `git hash-object` was refused under --restricted until declared. R1 (kit design pass, R1-T19):
    # the placer in the packet's sealed stage replaces `cp -f` and `mkdir -p` (which followed links and truncated a
    # hard-linked file in place, J-5); it makes missing folders itself, so no `mkdir` command is issued.
    i = PL.placing_commands({"path": "tests/fixtures/f.json", "op": "write", "staged": "/s/f.json",
                             "sha256": "d" * 64}, str(tmp_path))
    assert i["command"] == f"python3 {PL.placer_path()} {tmp_path} tests/fixtures/f.json /s/f.json {'d' * 64}"
    assert i["hash_command"] == "git hash-object tests/fixtures/f.json" and "mkdir" not in i
    assert "command" not in PL.placing_commands({"path": "x", "op": "noop"}, str(tmp_path))
    r = {**R, "items": [dict(R["items"][0], hash_command="git hash-object scripts/a.py")]}
    assert "git hash-object scripts/a.py" in PL.exact_commands(r)
    assert "Bash(git hash-object scripts/a.py)" in PL.allowlist(r, repair=True)
    assert not any(x.startswith("Bash(git hash-object:") for x in PL.allowlist(r, repair=True))  # no -w by prefix


def test_an_own_row_amendment_is_stated_exactly_and_scoped_to_one_file():
    amend = {"path": "handoffs/C.json", "row": "CI-1", "artifact": "scripts/study_topic.py", "ruling": "rule-x",
             "sha256": "e" * 64, "note": "re-pinned."}
    r = {**R, "items": [], "amendments": [amend]}
    p = PL.repair_prompt(r, "att-2", "att-1")
    assert "AMEND your own contract row CI-1 in handoffs/C.json (principal ruling rule-x)" in p
    assert "set sha256_current to " + "e" * 64 in p and "leave every other sha256_at_* field unchanged" in p
    assert "handoffs/C.json" in PL.write_set(r, repair=True)
    assert "Edit(handoffs/C.json)" in PL.allowlist(r, repair=True)
    assert "git hash-object scripts/study_topic.py" in PL.exact_commands(r)


def test_placed_by_apply_gives_no_copy_command_and_keeps_placed_files_out_of_the_write_set():
    # F5 ruling `F5-apply-script` (2026-09-28): the harness refused an exactly-allowlisted `cp -f` (V3.7 rerun)
    items = [dict(R["items"][0], placed_by="principal apply_protected.py"), dict(R["items"][1], placed_by="x")]
    for i in items:
        i.pop("command"), i.pop("mkdir", None)
    r = {**R, "items": items, "placed_by_apply": True}
    p = PL.repair_prompt(r, "att-2", "att-1")
    assert "has ALREADY placed these files" in p and "cp " not in p
    assert "run git hash-object scripts/a.py" in p
    assert "scripts/a.py" not in PL.write_set(r, repair=True)
    assert not any(x.startswith("Bash(cp") or x.startswith("Bash(mkdir") for x in PL.allowlist(r, repair=True))


def test_history_names_only_this_receivers_defects():
    only_guard = {**R, "items": [{"path": "scripts/close_authorization_guard.py", "op": "write", "sha256": "1"}]}
    h = PL.history(only_guard)
    assert "close_authorization_guard.py" in h and "omitted" not in h and "re-typed" not in h
    assert "omitted tests/fixtures/f.json" in PL.history(R) and "re-typed" in PL.history(R)


def test_apply_list_matches_the_reviewed_apply_scripts_contract(tmp_path):
    pkt = {"batch": "1-repair", "receivers": [{"aget": "a", "location": "/r/a", "items": [
        {"path": "scripts/g.py", "op": "write", "pre": "p" * 64, "sha256": "s" * 64, "source": "aget@v3.35.0:scripts/g.py",
         "placed_by": "x"}, {"path": "scripts/v.py", "op": "verify", "sha256": "v" * 64}]}]}
    doc = PL.apply_list(pkt, {"a": "/copy/a"})
    assert doc["apply_script_sha256"] == PL.P.sha_bytes((BATCH / "apply_protected.py").read_bytes())
    (op,) = doc["agets"][0]["ops"]
    assert op == {"path": "scripts/g.py", "op": "write", "pre": "p" * 64, "post": "s" * 64,
                  "source": "aget@v3.35.0:scripts/g.py", "source_sha256": "s" * 64}
    assert doc["agets"][0]["location"] == "/copy/a"


def test_push_session_is_restricted_and_allows_only_the_exact_push():
    PB = load("push_batch")
    r = {"settings": {"path": "/stage/settings/x.json"}}
    cmd = PB.push_command(r, "git push origin abc:refs/heads/main", "main", "P", "sid")
    assert "--restricted" in cmd and cmd[cmd.index("--settings") + 1] == "/stage/settings/x.json"
    a = cmd.index("--allowedTools")
    assert cmd[a + 1:a + 3] == ["Bash(git push origin abc:refs/heads/main)", "Bash(git ls-remote origin refs/heads/main)"]
    assert cmd[cmd.index("--tools") + 1] == "Bash" and cmd[-1] == "P"


def test_a2_migration_prompt_reads_the_recorded_baseline_and_lists_placed_files():
    items = [dict(R["items"][0], placed_by="approved list"), R["items"][2]]
    r = {**R, "items": items, "placed_by_apply": True}
    p = PL.prompt(r, "att", [])
    assert PL.baseline_path(r) in p and "2. Run: python3 -m pytest" not in p
    assert "scripts/a.py: placed; run git hash-object scripts/a.py" in p and "cp " not in p
    assert "MERGE scripts/b.py" in p


def test_track_skills_session_stages_each_path_and_probes_the_rule():
    r = {**R, "track_paths": [".gitignore", ".claude/skills/a/SKILL.md", ".claude/skills/b/SKILL.md"]}
    cmds = PL.track_commands(r)
    assert cmds[0] == "git check-ignore --no-index .claude/skills/a/SKILL.md"
    assert cmds[1:] == ["git add .gitignore", "git add .claude/skills/a/SKILL.md", "git add .claude/skills/b/SKILL.md"]
    p = PL.track_skills_prompt(r, "att")
    assert "It must exit 1" in p and "Do NOT push" in p and "Do not edit .gitignore" in p


def _kit_report():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_kit_report", Path(__file__).parent / "_kit_report.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_baseline_is_parsed_from_the_one_allowed_call_only(tmp_path):
    cmd = PL.BASELINE_CMD
    # B180 finding 1 (changed, labelled): pytest's short summary header added, as pytest prints it
    out = ("..F.\n=== short test summary info ===\nFAILED tests/test_a.py::test_x - boom\n"
           "ERROR tests/test_b.py::test_y\n1 failed, 3 passed, 1 error in 2.1s")
    # C2a7 (B185 finding 1, changed, labelled): the run carries its kit report, which the ids are read from
    rpt, tok, (out,) = _kit_report().reported(tmp_path / "r.jsonl", [(out, [
        "tests/test_a.py::test_x", ("tests/test_b.py::test_y", "setup")])])
    stream = "\n".join(__import__("json").dumps(e) for e in [
        {"sessionId": "S", "message": {"content": [{"type": "tool_use", "id": "1", "name": "Bash", "input": {"command": cmd}}]}},
        {"sessionId": "S", "message": {"content": [{"type": "tool_result", "tool_use_id": "1", "content": out}]}},
        {"sessionId": "S", "message": {"content": [{"type": "tool_use", "id": "2", "name": "Bash", "input": {"command": "echo x"}}]}},
        {"sessionId": "S", "message": {"content": [{"type": "tool_result", "tool_use_id": "2", "content": "FAILED fake::id"}]}}])
    got = LB.parse_baseline(stream, cmd, rpt, tok)
    assert got["summary"] == "1 failed, 3 passed, 1 error"
    assert got["failures"] == ["tests/test_a.py::test_x", "tests/test_b.py::test_y"]
    assert LB.parse_baseline("", cmd)["complete"] is False  # changed at C2a10 (labelled, B192 finding 2): a refusal is a record that is not complete


def test_a_receipt_can_move_out_of_docs_and_the_write_set_follows():
    # batch 4, principal: one receiver's own write_scope forbids docs/, so its receipt goes under .aget/
    r = {**R, "items": [], "receipt_path": ".aget/receipts/V335_RECEIVER_RECEIPT_example-x-aget.md"}
    assert PL.receipt_path(r) == ".aget/receipts/V335_RECEIVER_RECEIPT_example-x-aget.md"
    assert PL.receipt_path(R) == "docs/V335_RECEIVER_RECEIPT_example-x-aget.md"
    assert ".aget/receipts/V335_RECEIVER_RECEIPT_example-x-aget.md" in PL.write_set(r, repair=True)
    assert "Edit(.aget/receipts/V335_RECEIVER_RECEIPT_example-x-aget.md)" in PL.allowlist(r, repair=True)


def test_an_override_note_is_quoted_only_for_the_batches_it_names(monkeypatch, tmp_path):
    rec = tmp_path / "data" / "v335_ledger" / "records.json"
    rec.parent.mkdir(parents=True)
    rec.write_text(__import__("json").dumps({"scope_overrides": {"a": {"batches": ["4"], "source": "principal, typed X"}}}))
    monkeypatch.setattr(PL, "REPO", tmp_path)
    assert "principal, typed X" in PL.override_note("a", "4") and "this batch only" in PL.override_note("a", "4")
    assert PL.override_note("a", "5") is None and PL.override_note("b", "4") is None
    r = {**R, "override_note": PL.override_note("a", "4")}
    assert PL.prompt(r, "att", []).find("principal, typed X") != -1


def test_launch_command_is_restricted_with_hooks_file_and_push_denied():
    """Asserts the command's arguments carry the deny entries; what the harness then refuses is not tested here."""
    r = {**R, "allowlist": ["Read"], "prompt": "P", "settings": {"path": "/stage/settings/x.json"}}
    cmd = LB.command(r, "/stage", "sid", tools="Bash,Read", deny=["Bash(git push:*)", "Bash(gh:*)"])
    for flag, value in (("--permission-mode", "dontAsk"), ("--permission-prompts", "none"), ("--add-dir", "/stage"),
                        ("--tools", "Bash,Read"), ("--settings", "/stage/settings/x.json")):
        assert cmd[cmd.index(flag) + 1] == value
    assert "--restricted" in cmd and "--setting-sources" not in cmd
    d = cmd.index("--disallowedTools")
    assert cmd[d + 1:d + 3] == ["Bash(git push:*)", "Bash(gh:*)"]
    assert cmd[0:2] == ["claude", "-p"] and cmd[-1] == "P"


def test_untracked_skill_paths_reports_the_on_disk_spelling(tmp_path):
    """G3.6 row 2: a lowercase skill.md was reported as SKILL.md on a case-insensitive filesystem, so its git add
    staged nothing. The path must be the file's own name, whatever the filesystem's case rules."""
    import subprocess
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    for d, f in (("a", "SKILL.md"), ("b", "skill.md")):
        (tmp_path / ".claude" / "skills" / d).mkdir(parents=True)
        (tmp_path / ".claude" / "skills" / d / f).write_text("x\n")
    (tmp_path / ".claude" / "skills" / "c").mkdir()
    (tmp_path / ".claude" / "skills" / "c" / "notes.md").write_text("not a skill file\n")
    assert PL.untracked_skill_paths(str(tmp_path)) == [".claude/skills/a/SKILL.md", ".claude/skills/b/skill.md"]


def _v37():
    s = importlib.util.spec_from_file_location("rehearse_v37", BATCH / "rehearse_v37.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def _rb2():
    s = importlib.util.spec_from_file_location("rehearse_batch2", BATCH / "rehearse_batch2.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def test_rehearsal_bumps_a_receiver_specific_third_carrier(tmp_path):
    """G3.6 row 8: one receiver's pre-commit hook needs data/fleet/CANONICAL_AGET_VERSION.yaml bumped with version.json."""
    RB = _rb2()
    (tmp_path / ".aget").mkdir()
    (tmp_path / ".aget" / "version.json").write_text('{"aget_version": "3.34.0"}\n')
    (tmp_path / "data" / "fleet").mkdir(parents=True)
    c = tmp_path / "data" / "fleet" / "CANONICAL_AGET_VERSION.yaml"
    c.write_text("# prose mentioning 3.34.0 stays\ncanonical_version: 3.34.0\nsource: tag v3.34.0\nstamped: 2026-09-18\n")
    RB.bump_carriers(tmp_path, {"extra_carriers": ["data/fleet/CANONICAL_AGET_VERSION.yaml"]}, today="2026-09-28")
    assert c.read_text() == ("# prose mentioning 3.34.0 stays\ncanonical_version: 3.35.0\nsource: tag v3.34.0\n"
                             "stamped: 2026-09-28\n")
    assert '"3.35.0"' in (tmp_path / ".aget" / "version.json").read_text()
    RB.bump_carriers(tmp_path, {}, today="2026-09-29")   # no extra carrier named: untouched
    assert "stamped: 2026-09-28" in c.read_text()


def test_known_missing_emulation_drops_resolved_entries_and_adds_only_the_ruled_ones(tmp_path):
    RB = _rb2()
    (tmp_path / "tests").mkdir()
    t = tmp_path / "tests" / "test_ratchet.py"
    t.write_text('X = 1\nKNOWN_MISSING = {\n    ("a", "scripts/gone.py"),\n    ("b", "scripts/still.py"),\n}\n\n'
                 'def test_x():\n    pass\n')
    aud = tmp_path / "audit.py"
    aud.write_text('print("b  ->  scripts/still.py")\nprint("c  ->  scripts/ruled.py")\nprint("d  ->  scripts/new.py")\n')
    r = {"known_missing_ruling": {"file": "tests/test_ratchet.py", "auditor": "audit.py",
                                  "entries": [["c", "scripts/ruled.py"]]}}
    removed, added = RB.emulate_known_missing(tmp_path, r)
    assert removed == [("a", "scripts/gone.py")] and added == [("c", "scripts/ruled.py")]
    body = t.read_text()
    assert '("b", "scripts/still.py")' in body and '("c", "scripts/ruled.py")' in body
    assert "scripts/new.py" not in body and "def test_x" in body   # an unruled new miss must still fail the ratchet


def _load(folder, name):
    s = importlib.util.spec_from_file_location(name, BATCH / f"{name}.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


def test_a_dropped_member_is_marked_blocked_in_the_list():
    """G3.6 row 10 (a): a member dropped after the list is built must be `blocked`, so a bare apply cannot write it.
    The launcher never reads the list: a dropped member still in the packet is launched (not tested here)."""
    PW = _load("batch2", "prepare_write_list")
    doc = {"agets": [{"aget": "a", "ops": []}, {"aget": "b", "ops": []}]}
    PW.mark_dropped(doc, {"b": "V3.6 FAIL"})
    assert "blocked" not in doc["agets"][0] and doc["agets"][1]["blocked"].endswith("V3.6 FAIL")
    import pytest as _pt
    with _pt.raises(ValueError):
        PW.mark_dropped(doc, {"zzz": "not a member"})


ATTEMPT = "att-1"
RECEIPT_ACCEPTED = f"# Receipt\n\n## Attempt {ATTEMPT}\n\ndone\n\nTerminal: ACCEPTED\n"


def _phase1(ev, r, head, verdict="PASS", session="s-1"):
    """Phase-1 evidence as the launch now leaves it (R2): a launch record naming the session, and an after-run verdict
    that is the current run of the check for that file, bound to the member, the session and the commit judged. The
    receiver record gains the packet's attempt."""
    import subprocess as _sp
    RBND = _load("batch2", "result_binding")
    r["attempt"] = ATTEMPT
    r["push_url"] = _sp.run(["git", "-C", r["location"], "remote", "get-url", "--push", "--all", "origin"],
                            capture_output=True, text=True).stdout.split()             # recorded at B1 (R1)
    (ev / "launch_record.json").write_text(json.dumps({"head_after": head, "session_id": session}))
    run_id = RBND.start_run("after_run_check", ev / "after_run_check.json", recorded_by="invoker")
    RBND.write_result("after_run_check", ev / "after_run_check.json", {"verdict": verdict}, run_id,
                      binding={"aget": r["aget"], "session_id": session, "subject": head})


def _b8a(ev, doc):
    """Write the B8a record as suite_at_commit.py now does (R2-T16 (c)): its run recorded first, the record bound to it."""
    RB = _load("batch2", "result_binding")
    rid = RB.start_run("suite_at_commit", ev / "suite_at_commit.json", aget=doc.get("aget"))
    RB.write_result("suite_at_commit", ev / "suite_at_commit.json", doc, rid,
                    binding={"aget": doc.get("aget"), "subject": doc.get("sha")})


def _launch_names_snapshot(ev):
    """What launch_batch.run_one records (R2-T10): the launch record names the sha256 of its pre-session snapshot."""
    import hashlib
    rec = json.loads((ev / "launch_record.json").read_text())
    rec["snapshot_sha256"] = hashlib.sha256((ev / "settings_snapshot_pre.json").read_bytes()).hexdigest()
    (ev / "launch_record.json").write_text(json.dumps(rec))


def _repo_with_ignored_skill(tmp_path):
    import subprocess
    remote, loc = tmp_path / "remote.git", tmp_path / "aget"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(loc)], check=True)
    def g(*a):
        return subprocess.run(["git", "-C", str(loc), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                              check=True, capture_output=True, text=True).stdout.strip()
    (loc / ".gitignore").write_text(".claude/\n")
    (loc / "scripts").mkdir()
    (loc / "scripts" / "a.py").write_text("old\n")
    g("add", ".gitignore", "scripts/a.py")
    g("commit", "-q", "-m", "base")
    g("remote", "add", "origin", str(remote))
    g("push", "-q", "origin", "main")
    base = g("rev-parse", "HEAD")
    (loc / "scripts" / "a.py").write_text("release\n")
    (loc / ".claude" / "skills" / "x").mkdir(parents=True)
    (loc / ".claude" / "skills" / "x" / "SKILL.md").write_text("release skill\n")   # written, but git-ignored
    (loc / "docs").mkdir()
    (loc / "docs" / "V335_RECEIVER_RECEIPT_a.md").write_text(RECEIPT_ACCEPTED)       # R2: the receiver's terminal
    g("add", "scripts/a.py", "docs/V335_RECEIVER_RECEIPT_a.md")
    g("commit", "-q", "-m", "migration")
    return loc, base, g("rev-parse", "HEAD"), g


def test_push_gate_refuses_a_write_the_commit_does_not_carry(tmp_path):
    """G3.6 row 10 (b): batch 7's three pushes carried everything but their git-ignored protected skills."""
    PB = _load("batch1", "push_batch")
    loc, base, head, g = _repo_with_ignored_skill(tmp_path)
    r = {"aget": "a", "location": str(loc), "head": base, "branch": "main", "pre_dirty": [],
         "items": [{"path": "scripts/a.py", "op": "write"}]}
    ev = tmp_path / "ev" / "a"
    ev.mkdir(parents=True)
    _phase1(ev, r, head)
    _b8a(ev, {"sha": head, "verdict": "PASS", "aget": "a", "tree_check": "enforced"})   # B8a
    skill = ".claude/skills/x/SKILL.md"
    assert PB.untracked_writes(r, head, [skill]) == [skill]
    ok, why = PB.gate(r, tmp_path / "ev", [skill])
    assert ok is None and "not in the commit" in why and skill in why
    ok, why = PB.gate(r, tmp_path / "ev", None)                      # a migrating member needs the apply receipt
    assert ok is None and "--apply-receipt" in why
    ok, why = PB.gate(r, tmp_path / "ev", [])                        # nothing protected written: passes
    assert ok and ok["head"] == head


def test_push_gate_passes_once_the_skill_is_tracked(tmp_path):
    PB = _load("batch1", "push_batch")
    loc, base, _, g = _repo_with_ignored_skill(tmp_path)
    (loc / ".gitignore").write_text(".claude/*\n!.claude/skills/\n")
    g("add", ".gitignore", ".claude/skills/x/SKILL.md")
    g("commit", "-q", "-m", "track skills")
    head = g("rev-parse", "HEAD")
    r = {"aget": "a", "location": str(loc), "head": base, "branch": "main", "pre_dirty": [], "mode": "track-skills",
         "items": [], "track_paths": [".gitignore", ".claude/skills/x/SKILL.md"]}
    ev = tmp_path / "ev" / "a"
    ev.mkdir(parents=True)
    _phase1(ev, r, head)
    _b8a(ev, {"sha": head, "verdict": "PASS", "aget": "a", "tree_check": "enforced"})   # B8a
    ok, why = PB.gate(r, tmp_path / "ev", None)                      # track-skills: its own paths are checked
    assert ok and not why


def _produced(path, doc, step):
    """Write a rehearsal result the way its tool now does (R2): a run recorded in runs.jsonl beside it, the result
    with its binding, and the FINISHED row naming its bytes."""
    RBND = _load("batch2", "result_binding")
    run_id = RBND.start_run(step, path)
    RBND.write_result(step, path, doc, run_id)


def test_a_list_with_an_unblocked_v36_failure_is_not_approvable(tmp_path):
    """G3.6 row 10 (a), structural (framework-lane review of 6e82854e): the approval step refuses such a list."""
    CA = _load("batch2", "check_list_approvable")
    v36 = {"results": [{"aget": "a", "verdict": "PASS", "blind_spots": []}, {"aget": "b", "verdict": "FAIL"}]}
    lst = {"agets": [{"aget": "a"}, {"aget": "b"}]}
    assert CA.problems(lst, v36) and "b:" in CA.problems(lst, v36)[0]      # batch 7's case: one receiver FAIL, still ok
    lst["agets"][1]["blocked"] = "dropped after the list was built: V3.6 FAIL"
    assert CA.problems(lst, v36) == []
    assert CA.problems({"agets": [{"aget": "c"}]}, v36)                     # no V3.6 result at all: refused too
    L, V, V7 = tmp_path / "l.json", tmp_path / "v.json", tmp_path / "v7.json"

    def bind(list_doc, v37_verdict="PASS"):                       # results that name the list they rehearsed
        L.write_text(json.dumps(list_doc))
        sha = hashlib.sha256(L.read_bytes()).hexdigest()
        _produced(V, {**v36, "list_sha256": sha}, "rehearse_batch2")
        _produced(V7, {"verdict": v37_verdict, "list_sha256": sha}, "rehearse_v37")

    bind({"agets": [{"aget": "a"}, {"aget": "b"}]})
    assert CA.main(["--list", str(L), "--v36", str(V), "--v37", str(V7)]) == 1
    bind({"agets": [{"aget": "a"}]})
    assert CA.main(["--list", str(L), "--v36", str(V), "--v37", str(V7)]) == 0
    bind({"agets": [{"aget": "a"}]}, "INCONCLUSIVE")             # the framework Aget's finding: V3.7 must pass too
    assert CA.main(["--list", str(L), "--v36", str(V), "--v37", str(V7)]) == 1


def test_each_result_must_name_the_list_being_approved(tmp_path):
    """supervisor:L843: batch 8's V3.7 result for list 5040d231 would have passed list a06ecb52. Each stale or
    unnamed result is refused on its own, with every other condition met."""
    CA = _load("batch2", "check_list_approvable")
    L, V, V7 = tmp_path / "l.json", tmp_path / "v.json", tmp_path / "v7.json"
    L.write_text(json.dumps({"agets": [{"aget": "a"}]}))
    sha, other = hashlib.sha256(L.read_bytes()).hexdigest(), "f" * 64
    def run():
        return CA.main(["--list", str(L), "--v36", str(V), "--v37", str(V7)])
    v36 = {"results": [{"aget": "a", "verdict": "PASS", "blind_spots": []}]}

    _produced(V, {**v36, "list_sha256": sha}, "rehearse_batch2")
    _produced(V7, {"verdict": "PASS", "list": f"WRITE_LIST sha256 {sha} (location rewritten)"}, "rehearse_v37")
    assert run() == 1          # R2 (S-184): a digest found in free text is no longer read; only `list_sha256` binds
    _produced(V7, {"verdict": "PASS", "list_sha256": sha}, "rehearse_v37")
    assert run() == 0
    _produced(V7, {"verdict": "PASS", "list_sha256": other}, "rehearse_v37")
    assert run() == 1                                             # stale V3.7 alone
    _produced(V7, {"verdict": "PASS"}, "rehearse_v37")
    assert run() == 1                                             # V3.7 naming no list alone
    _produced(V7, {"verdict": "PASS", "list_sha256": sha}, "rehearse_v37")
    _produced(V, {**v36, "list_sha256": other}, "rehearse_batch2")
    assert run() == 1                                             # stale V3.6 alone (was only a NOTE before)
    _produced(V, v36, "rehearse_batch2")
    assert run() == 1                                             # V3.6 naming no list alone


# R3 (kit design pass): list ops are classified items (the approval check reads their meaning row), not bare values
W1, W2, W9 = ({"path": f"scripts/{n}.py", "op": "write"} for n in ("one", "two", "nine"))


def test_a_drop_relist_is_approvable_only_against_the_rehearsed_list(tmp_path):
    """--drop after V3.6 changes the digest; --relisted-from names the rehearsed list, and only newly blocked members
    (not the V3.7 member) may differ."""
    CA = _load("batch2", "check_list_approvable")
    OLD, L, V, V7 = (tmp_path / n for n in ("old.json", "l.json", "v.json", "v7.json"))
    old = {"prepared_at": "t0", "agets": [{"aget": "a", "ops": [W1]}, {"aget": "b", "ops": [W2]}]}
    OLD.write_text(json.dumps(old))
    osha = hashlib.sha256(OLD.read_bytes()).hexdigest()
    _produced(V, {"list_sha256": osha, "results": [{"aget": "a", "verdict": "PASS", "blind_spots": []},
                                                    {"aget": "b", "verdict": "FAIL"}]}, "rehearse_batch2")
    _produced(V7, {"verdict": "PASS", "list_sha256": osha, "members": {"a": {"verdict": "PASS"}}}, "rehearse_v37")
    def run(*x):
        return CA.main(["--list", str(L), "--v36", str(V), "--v37", str(V7), *x])

    new = {"prepared_at": "t1", "agets": [{"aget": "a", "ops": [W1]}, {"aget": "b", "ops": [W2], "blocked": "V3.6 FAIL"}]}
    L.write_text(json.dumps(new))
    assert run() == 1                                             # without the flag: the digests do not match
    assert run("--relisted-from", str(OLD)) == 0
    new["agets"][0]["ops"] = [W9]
    L.write_text(json.dumps(new))
    assert run("--relisted-from", str(OLD)) == 1                  # any other change: refused
    new["agets"][0]["ops"] = [W1]
    _produced(V7, {"verdict": "PASS", "list_sha256": osha, "members": {"b": {"verdict": "PASS"}}}, "rehearse_v37")
    L.write_text(json.dumps(new))
    assert run("--relisted-from", str(OLD)) == 1                  # the V3.7 member itself dropped: refused


def test_receiver_authored_bytes_become_listed_writes_with_their_digest(tmp_path):
    """G3.6 row 11: the framework Aget's own merge resolutions are placed by the list, each marked and digested."""
    PW = _load("batch2", "prepare_write_list")
    (tmp_path / "scripts").mkdir()
    (tmp_path / "scripts" / "m.py").write_text("mine\n")
    doc = {"agets": [{"aget": "f", "location": str(tmp_path), "ops": [
        {"path": "scripts/m.py", "op": "hold", "kind": "authored", "authored_lines": 1},   # B151 #4: a classified row
        {"path": "scripts/other.py", "op": "write", "post": "x"}]}]}
    src = "framework-aget@abc123:planning/kr0/scripts__m.py.resolved"
    PW.apply_resolved(doc, {"f": {"scripts/m.py": src}}, read=lambda s: b"resolved\n" if s == src else None)
    ops = {o["path"]: o for o in doc["agets"][0]["ops"]}
    m = ops["scripts/m.py"]
    assert m["op"] == "write" and m["receiver_authored"] and m["source"] == src
    assert m["post"] == m["source_sha256"] == PW.sha(b"resolved\n") and m["pre"] == PW.sha(b"mine\n")
    assert ops["scripts/other.py"]["post"] == "x"                          # other ops untouched
    import pytest as _pt
    with _pt.raises(ValueError):                                            # an unreadable source refuses, never skips
        PW.apply_resolved(doc, {"f": {"scripts/m.py": "repo@nope:x"}}, read=lambda s: None)


def test_prompt_names_receiver_authored_files_and_the_extra_step():
    r = {"aget": "f", "head": "abc", "template": "t", "pins": {"core": "c", "t": "p"}, "placed_by_apply": True,
         "items": [{"path": "scripts/m.py", "op": "write", "placed_by": "x", "hash_command": "git hash-object scripts/m.py",
                    "receiver_authored": True, "source": "repo@abc:k/m.resolved"}],
         "extra_steps": ["In scripts/a.py, change `close_gate_lifecycle_ext` imports to `close_gate_lifecycle`."]}
    p = PL.prompt(r, "att", [])
    assert "4c. In scripts/a.py" in p and "YOUR OWN resolutions" in p and "repo@abc:k/m.resolved" in p


def test_an_excluded_path_leaves_the_packet_with_its_reason():
    """G3.6 row 11: a machine-local, git-ignored path (framework's .aget/config.json) is excluded, recorded, never silent."""
    r = {"items": [{"path": ".aget/config.json", "op": "hold"}, {"path": "scripts/x.py", "op": "write"}]}
    PL.exclude_items(r, {".aget/config.json": "machine-local; git-ignored and untracked"})
    assert [i["path"] for i in r["items"]] == ["scripts/x.py"]
    assert r["excluded"] == [{"path": ".aget/config.json", "reason": "machine-local; git-ignored and untracked"}]
    import pytest as _pt
    with _pt.raises(ValueError):
        PL.exclude_items(r, {"not/there": "typo"})


def test_parallel_suite_runner_aggregates_discloses_and_parses(tmp_path):
    """Principal ruling `framework suite-command parallel-runner, CI deselection disclosed` (2026-09-28)."""
    import subprocess
    import sys
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text("def test_ok():\n    pass\n\ndef test_known_bad():\n    assert False\n")
    (tmp_path / "tests" / "test_b.py").write_text("def test_fails():\n    assert 1 == 2\n\ndef test_ok2():\n    pass\n")
    (tmp_path / "tests" / "ci_known_failures.txt").write_text("# CI deselection\ntests/test_a.py::test_known_bad\n")
    runner = BATCH / "run_suite_parallel.py"
    p = subprocess.run([sys.executable, str(runner), "--deselect-file", "tests/ci_known_failures.txt"], cwd=tmp_path,
                       capture_output=True, text=True)
    out = p.stdout
    assert p.returncode == 1, out
    assert "FAILED tests/test_b.py::test_fails" in out and "test_known_bad" not in out.split("DESELECTED")[0]
    assert "DESELECTED (disclosed" in out and "tests/test_a.py::test_known_bad" in out
    RR = _load("batch1", "rehearse_repair")
    summ = next((m.group(1) for ln in reversed(out.splitlines()) if (m := RR.SUMMARY.search(ln))), None)
    assert summ and summ.startswith("1 failed, 2 passed") and "1 deselected" in summ, out
    LB = _load("batch1", "launch_batch")
    assert any(LB.SUMMARY.search(ln) for ln in out.splitlines())
    # B180 finding 1 (changed, labelled): the ids are read by the kit's one reader, not rehearse_repair's own pattern
    assert RR.RBND.failing_ids(out) == (["tests/test_b.py::test_fails"], None), out


def test_parallel_suite_runner_reports_a_broken_file_as_error(tmp_path):
    import subprocess
    import sys
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_ok.py").write_text("def test_ok():\n    pass\n")
    (tmp_path / "tests" / "test_broken.py").write_text("import nonexistent_module_xyz\n\ndef test_x():\n    pass\n")
    p = subprocess.run([sys.executable, str(BATCH / "run_suite_parallel.py")], cwd=tmp_path,
                       capture_output=True, text=True)
    assert p.returncode == 1 and ("ERROR tests/test_broken.py" in p.stdout), p.stdout


def test_parallel_suite_runner_reports_exit_1_with_no_failure_counted_as_error(tmp_path):
    """The framework Aget's review (2026-09-29): a session-level failure prints 'N passed' and exits 1; that file read
    green. It must be an ERROR line and a non-zero exit."""
    import subprocess
    import sys
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_ok.py").write_text("def test_ok():\n    pass\n")
    (tmp_path / "tests" / "conftest.py").write_text(
        "def pytest_sessionfinish(session, exitstatus):\n    session.exitstatus = 1\n")
    p = subprocess.run([sys.executable, str(BATCH / "run_suite_parallel.py")], cwd=tmp_path,
                       capture_output=True, text=True)
    # changed at C2a5 (B182 finding 1, labelled): a line the runner makes is marked IDS-UNKNOWN, never an ERROR id
    assert p.returncode == 1 and "IDS-UNKNOWN tests/test_ok.py (pytest exit 1 with no failed or error counted" in p.stdout, \
        p.stdout


def test_a_ruled_suite_command_reaches_baseline_steps_and_declared_commands():
    cmd = "python3 /x/run_suite_parallel.py --deselect-file tests/ci_known_failures.txt"
    r = {"aget": "f", "head": "abc", "template": "t", "pins": {"core": "c", "t": "p"}, "items": [], "suite_cmd": cmd}
    assert cmd in PL.baseline_prompt(r)
    p = PL.prompt(r, "att", [])
    assert f"2. Run: {cmd}" in p and f"5. Validate. Run: {cmd}" in p
    assert cmd in PL.exact_commands(r)
    r.pop("suite_cmd")
    assert "python3 -m pytest -q -rfE" in PL.baseline_prompt(r) and cmd not in PL.exact_commands(r)


def test_push_gate_allows_paths_dirty_at_launch_and_refuses_later_ones(tmp_path):
    """Row 11: files that appear between preparation and launch are in the launch snapshot; later ones still refuse."""
    PB = _load("batch1", "push_batch")
    loc, base, head, g = _repo_with_ignored_skill(tmp_path)
    r = {"aget": "a", "location": str(loc), "head": base, "branch": "main", "pre_dirty": [],
         "items": [{"path": "scripts/a.py", "op": "write"}]}
    ev = tmp_path / "ev" / "a"
    ev.mkdir(parents=True)
    _phase1(ev, r, head)
    _b8a(ev, {"sha": head, "verdict": "PASS", "aget": "a", "tree_check": "enforced"})   # B8a
    (loc / "sessions" / "markers").mkdir(parents=True)
    (loc / "sessions" / "markers" / "late.json").write_text("{}")         # appeared after prep, before launch
    (ev / "settings_snapshot_pre.json").write_text(json.dumps({"dirty": {"sessions/markers/late.json": "x"}}))
    _launch_names_snapshot(ev)                                             # R2-T10: the launch recorded its digest
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok, why
    (loc / "sessions" / "after_launch.md").write_text("x")                 # appeared after the launch snapshot
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and "sessions/after_launch.md" in why


def test_import_renames_are_data_the_prompt_states_and_v36_applies(tmp_path):
    """Row 11: step 4c as prose hid a regression from V3.6; as data, V3.6 applies exactly what the prompt states."""
    RB = _rb2()
    (tmp_path / "scripts").mkdir()
    f = tmp_path / "scripts" / "g.py"
    f.write_text("from close_gate_lifecycle_ext import x\nimport close_gate_lifecycle_ext_other\n")
    r = {"renames": [{"old": "close_gate_lifecycle_ext", "new": "close_gate_lifecycle", "path": "scripts/g.py"}]}
    assert RB.emulate_renames(tmp_path, r) == [("scripts/g.py", 1)]
    assert f.read_text() == "from close_gate_lifecycle import x\nimport close_gate_lifecycle_ext_other\n"
    p = PL.prompt({"aget": "f", "head": "a", "template": "t", "pins": {"core": "c", "t": "p"}, "items": [], **r}, "att", [])
    assert "4d. Rename imports" in p and "in scripts/g.py, close_gate_lifecycle_ext -> close_gate_lifecycle" in p


def test_an_omitted_hook_event_is_left_out_and_disclosed(tmp_path, monkeypatch):
    """Principal ruling `batch8 omit SessionEnd hook for framework`: only the named event is dropped, and disclosed."""
    import subprocess
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / ".claude").mkdir()
    (tmp_path / ".claude" / "settings.json").write_text(json.dumps({"hooks": {
        "SessionEnd": [{"hooks": [{"type": "command", "command": "python3 wind_down.py"}]}],
        "PreToolUse": [{"hooks": [{"type": "command", "command": "guard.sh"}]}]},
        "permissions": {"allow": ["Bash(ls)"]}}))
    monkeypatch.setattr(PL, "STAGE", tmp_path / "stage")
    s = PL.settings_file({"aget": "f", "location": str(tmp_path), "omit_hooks": ["SessionEnd"]})
    body = json.loads(Path(s["path"]).read_text())
    assert list(body["hooks"]) == ["PreToolUse"] and s["hook_events_omitted"] == ["SessionEnd"]
    assert "permissions" not in body
    import pytest as _pt
    with _pt.raises(ValueError):
        PL.settings_file({"aget": "f", "location": str(tmp_path), "omit_hooks": ["NoSuchEvent"]})


def test_v36_copies_declared_sibling_folders_beside_the_copy(tmp_path):
    """G3.6 row 12, B2: batch 8 V3.6 copied the framework Aget without ../aget, so its identifier test already failed
    in S0 and the real regression could not show as new. A declared sibling is copied to the same relative place."""
    RB = _load("batch2", "rehearse_batch2")
    import subprocess
    home = tmp_path / "home"
    (home / "sib" / "specs").mkdir(parents=True)
    (home / "sib" / "specs" / "S.md").write_text("canonical\n")
    seat = home / "seat"
    seat.mkdir()
    (seat / "a.txt").write_text("x\n")
    subprocess.run(["git", "init", "-q", str(seat)], check=True)
    r = {"aget": "seat", "location": str(seat)}
    scratch = tmp_path / "scr"
    scratch.mkdir()
    dest = RB.copy_of(r, scratch, ["../sib"])
    assert dest.name == "seat" and (dest / "a.txt").read_text() == "x\n"
    assert (dest.parent / "sib" / "specs" / "S.md").read_text() == "canonical\n"
    plain = RB.copy_of(r, scratch)                                       # no declaration: as before
    assert plain == scratch / "seat" and not (scratch / "sib").exists()


def test_v36_refuses_a_sibling_that_is_missing_or_escapes_the_copy_root(tmp_path):
    RB = _load("batch2", "rehearse_batch2")
    import subprocess
    seat = tmp_path / "home" / "seat"
    seat.mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(seat)], check=True)
    r = {"aget": "seat", "location": str(seat)}
    scratch = tmp_path / "scr"
    scratch.mkdir()
    for bad in (["../missing"], ["../../.."]):
        with pytest.raises(ValueError):
            RB.copy_of(r, scratch, bad)


def test_v37_writes_its_own_result_naming_the_list_digest_and_the_approval_check_reads_it(tmp_path):
    """G3.6 row 12, B3 (supervisor:L843): batch 8's V3.7 results were hand-composed; a stale digest survived in one and a
    FAIL had to be transcribed. The rehearsal now writes its own result from its own records."""
    import hashlib
    RV = _load("batch2", "rehearse_v37")
    CA = _load("batch2", "check_list_approvable")
    lst, pk = tmp_path / "WRITE_LIST.json", tmp_path / "PACKET.json"
    lst.write_text(json.dumps({"agets": [{"aget": "a"}]}))
    pk.write_text("{}")
    ev = tmp_path / "evidence"
    (ev / "a").mkdir(parents=True)
    (ev / "a" / "after_run_check.json").write_text(json.dumps({"verdict": "PASS", "F": []}))
    (ev / "a" / "launch_record.json").write_text(json.dumps({"head_after": "abc"}))
    getattr(RV, "LAUNCHED", set()).add("a")      # changed at C2e (D-8, S-198/S-323, labelled): records are embedded for a launched member
    doc = RV.result_doc("9", pk, lst, ev, {"a": "PASS"}, "t0")
    sha = hashlib.sha256(lst.read_bytes()).hexdigest()
    assert doc["list_sha256"] == sha and doc["verdict"] == "PASS" and doc["members"]["a"]["launch_record"]["head_after"]
    assert RV.result_doc("9", pk, lst, ev, {"a": "FAIL"}, "t0")["verdict"] == "FAIL"
    assert RV.result_doc("9", pk, lst, ev, {}, "t0")["verdict"] == "FAIL"          # nothing rehearsed is not a PASS
    v36, v37 = tmp_path / "v36.json", tmp_path / "v37.json"
    _produced(v36, {"list_sha256": sha, "results": [{"aget": "a", "verdict": "PASS", "blind_spots": []}]},
              "rehearse_batch2")
    _produced(v37, doc, "rehearse_v37")
    assert CA.main(["--list", str(lst), "--v36", str(v36), "--v37", str(v37)]) == 0
    lst.write_text(json.dumps({"agets": [{"aget": "a"}, {"aget": "b", "blocked": "x"}]}))   # list changed after it
    assert CA.main(["--list", str(lst), "--v36", str(v36), "--v37", str(v37)]) == 1


def test_push_gate_accepts_exactly_one_named_bounded_commit_above_the_checked_head(tmp_path):
    """Batch 8 (`predicatefix`, 2026-09-29): 76f19247 plus exactly one framework commit touching only the checker and
    its test. Each refusal is tested with the other conditions met. The commit and its paths reach the gate as
    arguments (--extra-commit and --extra-paths on the command line). This tests gate() alone; main() separately
    requires a live push's extra commit to match the recorded push line. Paths have no typed-line comparison."""
    PB = _load("batch1", "push_batch")
    loc, base, checked, g = _repo_with_ignored_skill(tmp_path)
    r = {"aget": "a", "location": str(loc), "head": base, "branch": "main", "pre_dirty": [],
         "items": [{"path": "scripts/a.py", "op": "write"}]}
    ev = tmp_path / "ev" / "a"
    ev.mkdir(parents=True)
    _phase1(ev, r, checked)
    (loc / "scripts" / "chk.py").write_text("fix\n")
    (loc / "tests").mkdir()
    (loc / "tests" / "t.py").write_text("t\n")
    g("add", "scripts/chk.py", "tests/t.py")
    g("commit", "-q", "-m", "fix")
    fix = g("rev-parse", "HEAD")
    paths = ["scripts/chk.py", "tests/t.py"]
    _b8a(ev, {"sha": fix, "verdict": "PASS", "aget": "a", "tree_check": "enforced"})   # B8a
    ok, why = PB.gate(r, tmp_path / "ev", [], (fix, paths))
    assert ok and ok["head"] == fix, why
    ok, why = PB.gate(r, tmp_path / "ev", [])                              # not named: refused as before
    assert ok is None and "HEAD moved" in why
    ok, why = PB.gate(r, tmp_path / "ev", [], (fix, ["scripts/chk.py"]))   # touches a path beyond the bound
    assert ok is None and "beyond the named paths" in why
    ok, why = PB.gate(r, tmp_path / "ev", [], (checked, paths))            # names the wrong commit
    assert ok is None and "not the named extra commit" in why
    (loc / "tests" / "t.py").write_text("t2\n")
    g("commit", "-q", "-am", "second")                                     # a second commit above the checked HEAD
    ok, why = PB.gate(r, tmp_path / "ev", [], (g("rev-parse", "HEAD"), paths))
    assert ok is None and "parents" in why
    g("reset", "-q", "--hard", checked)
    (loc / "scripts" / "a.py").write_text("tamper\n")
    g("commit", "-q", "-am", "touches a batch-written path")
    t = g("rev-parse", "HEAD")
    ok, why = PB.gate(r, tmp_path / "ev", [], (t, ["scripts/a.py"]))
    assert ok is None and "paths the batch wrote" in why


def _git_repo(loc, files):
    import subprocess
    loc.mkdir(parents=True)
    for p, s in files.items():
        (loc / p).parent.mkdir(parents=True, exist_ok=True)
        (loc / p).write_text(s)
    def g(*a):
        return subprocess.run(["git", "-C", str(loc), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                              check=True, capture_output=True, text=True).stdout.strip()
    g("init", "-q")
    g("add", "-A")
    g("commit", "-q", "-m", "c")
    return g


def test_v36_blind_spots_are_copy_only_failures_against_a_clean_clone_reference(tmp_path):
    """Plan G3.6 row 13 (b), supervisor:L816: batch 8's copy had 153 failures where the real Aget had 0, and nothing
    compared them. A test failing on the copy but not in a clean clone of the Aget's commit is a blind spot."""
    import sys as _sys
    RB = _load("batch2", "rehearse_batch2")
    RB.SAC.WORK = tmp_path / "w"
    loc = tmp_path / "home" / "seat"
    g = _git_repo(loc, {"tests/test_x.py": "def test_a():\n    assert True\n\ndef test_real():\n    assert False\n"})
    r = {"aget": "seat", "location": str(loc), "head": g("rev-parse", "HEAD"),
         "suite_cmd": f"{_sys.executable} -m pytest -q -p no:cacheprovider"}
    s0 = {"failures": ["tests/test_x.py::test_a", "tests/test_x.py::test_real"]}      # test_a fails only on the copy
    rep = RB.blind_spot_report(r, s0, tmp_path / "scr")
    assert rep["blind_spots"] == ["tests/test_x.py::test_a"] and rep["reference"]["verdict"] == "FAIL"
    rep = RB.blind_spot_report({**r, "head": "0" * 40}, s0, tmp_path / "scr")
    assert rep["blind_spots"] is None and "INCONCLUSIVE" in rep["blind_spots_why"]      # unknown is not empty
    # supervisor:L816 (row 13 proof): when CI passed the commit, a failure shared by copy and reference is local, so
    # the rehearsal is blind there too.
    # changed at C2e (D-8, S-193/S-325, labelled): CI is read as the ledger reads it; PASS = every committed workflow
    RB.ci_on_commit = lambda loc, sha: {"state": "PASS", "why": "1 run(s)"}
    rep = RB.blind_spot_report(r, s0, tmp_path / "scr")
    assert rep["blind_spots"] == ["tests/test_x.py::test_a", "tests/test_x.py::test_real"]
    assert rep["reference_disagrees_with_ci"] == ["tests/test_x.py::test_real"]


def test_approval_prints_blind_spots_and_refuses_one_covering_a_written_file_unless_accepted(tmp_path, capsys):
    CA = _load("batch2", "check_list_approvable")
    loc = tmp_path / "seat"
    (loc / "tests").mkdir(parents=True)
    (loc / "tests" / "test_a.py").write_text("import close_gate_lifecycle\n")
    (loc / "tests" / "test_b.py").write_text("def test_b(): pass\n")
    lst = {"agets": [{"aget": "a", "location": str(loc),
                      "ops": [{"path": "scripts/close_gate_lifecycle.py", "op": "write"}]}]}
    v36 = {"results": [{"aget": "a", "verdict": "PASS",
                        "blind_spots": ["tests/test_a.py::t", "tests/test_b.py::test_b"]}]}
    out = CA.blind_spot_problems(lst, v36)
    assert len(out) == 1 and "tests/test_a.py::t" in out[0]              # imports a written module: covers it
    assert "BLIND SPOTS a: 2 test(s)" in capsys.readouterr().out
    assert CA.blind_spot_problems(lst, v36, {"tests/test_a.py::t"}) == []
    v36["results"][0]["blind_spots"] = None
    assert CA.blind_spot_problems(lst, v36) and "no V3.6 blind-spot report" in CA.blind_spot_problems(lst, v36)[0]


def test_v36_commits_the_applied_files_in_the_copy_before_s2_leaving_pre_existing_changes(tmp_path):
    """Plan G3.6 row 13 (c): batch 8's clean-tree test read 'new' in V3.6 only because the copy never committed."""
    RB = _load("batch2", "rehearse_batch2")
    loc = tmp_path / "copy"
    g = _git_repo(loc, {"a.py": "old\n", "notes.md": "mine\n"})
    (loc / "notes.md").write_text("mine, edited before the batch\n")      # pre-existing change
    (loc / "a.py").write_text("release\n")                                 # applied write
    (loc / "new.py").write_text("new\n")                                   # applied new file
    assert RB.CI.isolate(loc, "remove", member=True, run=loc.parent) is None   # E2f2: as the rehearsal does
    paths = RB.commit_applied(loc, {"pre_dirty": ["notes.md"]})
    assert paths == ["a.py", "new.py"]
    assert g("status", "--porcelain") == "M notes.md"
    assert g("show", "HEAD:a.py") == "release"


def test_push_gate_allows_only_the_exact_dirty_paths_named(tmp_path):
    """Batch 9 (2026-09-29): one receiver's own hook wrote its friction ledger after launch. A path given to the gate
    (--allow-dirty on the command line; no typed line is compared) passes; any other new uncommitted path still refuses."""
    PB = _load("batch1", "push_batch")
    loc, base, head, g = _repo_with_ignored_skill(tmp_path)
    r = {"aget": "a", "location": str(loc), "head": base, "branch": "main", "pre_dirty": [],
         "items": [{"path": "scripts/a.py", "op": "write"}]}
    ev = tmp_path / "ev" / "a"
    ev.mkdir(parents=True)
    _phase1(ev, r, head)
    _b8a(ev, {"sha": head, "verdict": "PASS", "aget": "a", "tree_check": "enforced"})
    (loc / "ledger.md").write_text("receiver's note\n")
    g("add", "ledger.md")
    g("commit", "-q", "-m", "ledger")
    g("reset", "-q", "--soft", "HEAD~1")
    g("reset", "-q", "HEAD")                                               # ledger.md now untracked dirt
    head2 = g("rev-parse", "HEAD")
    assert head2 == head
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and "ledger.md" in why
    ok, why = PB.gate(r, tmp_path / "ev", [], None, {"ledger.md": "receiver's own friction hook"})
    assert ok, why
    (loc / "other.md").write_text("x\n")
    ok, why = PB.gate(r, tmp_path / "ev", [], None, {"ledger.md": "receiver's own friction hook"})
    assert ok is None and "other.md" in why


def test_push_gate_for_a_track_skills_pass_checks_what_it_wrote_not_the_migration_payload(tmp_path):
    """Batch 9t (2026-09-29): skill tracking before the migration. The gate counted the packet's release items as
    written and refused; it must require its own track paths and receipt files, and still refuse a missing one."""
    PB = _load("batch1", "push_batch")
    loc = tmp_path / "seat"
    g = _git_repo(loc, {".gitignore": ".claude/*\n!.claude/skills/\n", ".claude/skills/x/SKILL.md": "s\n"})
    head = g("rev-parse", "HEAD")
    r = {"aget": "a", "location": str(loc), "mode": "track-skills",
         "items": [{"path": "scripts/release_only.py", "op": "write"}],
         "track_paths": [".gitignore", ".claude/skills/x/SKILL.md"]}
    assert PB.untracked_writes(r, head, [".gitignore"]) == []
    r["track_paths"].append(".claude/skills/missing/SKILL.md")
    assert PB.untracked_writes(r, head, [".gitignore"]) == [".claude/skills/missing/SKILL.md"]
    r["mode"] = "migrate"                                                  # a migration still counts its items
    assert "scripts/release_only.py" in PB.untracked_writes(r, head, [])


def test_push_gate_requires_a_b8a_pass_record_for_the_exact_commit_to_be_pushed(tmp_path):
    """Plan G3.6 row 13 (a); supervisor:L844: no push without a suite_at_commit.json that names that exact commit with
    verdict PASS. The gate reads the file's fields; this test writes the file by hand, and the gate does not verify
    that a suite run produced it. Each refusal with every other condition met."""
    PB = _load("batch1", "push_batch")
    loc, base, head, g = _repo_with_ignored_skill(tmp_path)
    r = {"aget": "a", "location": str(loc), "head": base, "branch": "main", "pre_dirty": [],
         "items": [{"path": "scripts/a.py", "op": "write"}]}
    ev = tmp_path / "ev" / "a"
    ev.mkdir(parents=True)
    _phase1(ev, r, head)
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and "no B8a record" in why
    _b8a(ev, {"sha": base, "verdict": "PASS", "aget": "a", "tree_check": "enforced"})
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and "not the commit to be pushed" in why
    _b8a(ev, {"sha": head, "verdict": "FAIL", "aget": "a", "tree_check": "enforced", "failures": ["t::x"]})
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and "B8a FAIL" in why
    _b8a(ev, {"sha": head, "verdict": "PASS", "aget": "a", "tree_check": "enforced"})
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok and ok["head"] == head, why


def sealed_packet_root(tmp_path, names):
    """A packet root as prepare_launch now makes one (R1 lifecycle): a sealed stage with its manifest, and one open
    baseline slot per receiver. Returns the packet fields that name it."""
    import hashlib as _h
    import os as _os
    pr = tmp_path / "packet_root"
    (pr / "stage" / "kit").mkdir(parents=True)
    (pr / "stage" / "kit" / "place_file.py").write_text("# placer\n")
    for n in names:
        (pr / "baselines" / n).mkdir(parents=True)
    manifest = {"kit/": "folder", "kit/place_file.py": _h.sha256(b"# placer\n").hexdigest()}
    for p in (pr / "stage" / "kit" / "place_file.py", pr / "stage" / "kit", pr / "stage"):   # sealed: a-w
        _os.chmod(p, _os.stat(p).st_mode & ~0o222)
    return {"packet_root": str(pr), "stage": str(pr / "stage"), "stage_manifest": manifest}


def _copy_root_fixture(tmp_path, monkeypatch):
    """F-4 fixture: a member repository with no remote, and a packet file naming it at its HEAD. `claude --version`
    answers the packet's version, and a started session or baseline fails the test: nothing is launched here."""
    import subprocess
    member = tmp_path / "home" / "m-aget"
    g = _git_repo(member, {"a.txt": "x\n", "sub/b.txt": "y\n"})
    settings = tmp_path / "settings.json"
    settings.write_text("{}\n")
    pk = tmp_path / "PACKET.json"
    pk.write_text(json.dumps({
        "batch": "99", "claude_version": "stub 1.0", **sealed_packet_root(tmp_path, ["m-aget"]), "tools": "Bash",
        "deny": ["Bash(gh:*)"],
        "receivers": [{"aget": "m-aget", "location": str(member), "head": g("rev-parse", "HEAD"), "prompt": "p",
                       "baseline_prompt": "b", "allowlist": ["Bash(python3 -m pytest:*)"], "write_set": ["a.txt"],
                       "allow_bash": [], "attempt": "a1",   # as every prepared packet carries (B148 #3's C1 check)
                       "settings": {"path": str(settings),
                                    "sha256": hashlib.sha256(settings.read_bytes()).hexdigest()}}]}))
    real = subprocess.run

    def fake(cmd, *a, **k):
        if [str(c) for c in cmd[:2]] == ["claude", "--version"]:
            return subprocess.CompletedProcess(cmd, 0, "stub 1.0\n", "")
        return real(cmd, *a, **k)

    def launched(*a, **k):
        raise AssertionError("a session was started")

    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setattr(LB, "run_one", launched)
    monkeypatch.setattr(LB, "run_baseline", launched)
    return member, pk


def _write_marker(folder, packet_bytes, aget):
    (folder / ".git" / LB.COPY_MARKER).write_text(json.dumps(
        {"packet_sha256": hashlib.sha256(packet_bytes).hexdigest(), "aget": aget}))


def _copy_root_run(pk, folder, launch=True):
    return LB.main(["--packet", str(pk), "--only", "m-aget", "--copy-root", str(folder)] + (["--launch"] * launch))


def test_copy_root_refuses_the_members_own_folder_and_a_folder_nested_in_it(tmp_path, monkeypatch, capsys):
    """F-4: a real member with no remote, at the packet's HEAD, entered the launch path that checks no typed line. Its
    own folder and a folder inside it are refused (exit 2) even with a marker naming this packet in its .git folder,
    so the path test alone refuses them; the folder that holds the member is refused by the same function, and so is
    a separate folder whose .git is a symbolic link to the member's."""
    member, pk = _copy_root_fixture(tmp_path, monkeypatch)
    _write_marker(member, pk.read_bytes(), "m-aget")
    for folder in (member, member / "sub"):
        assert _copy_root_run(pk, folder) == 2
        out = capsys.readouterr().out
        assert "STOPPED: --copy-root" in out and "own folder" in out
    sha = hashlib.sha256(pk.read_bytes()).hexdigest()
    assert "own folder" in LB.copy_root_refusal(member.parent, member, sha, "m-aget")
    linked = tmp_path / "linked"
    linked.mkdir()
    (linked / ".git").symlink_to(member / ".git")
    assert "shares its .git" in LB.copy_root_refusal(linked, member, sha, "m-aget")


def test_copy_root_refuses_a_remoteless_folder_without_the_custody_marker(tmp_path, monkeypatch, capsys):
    """F-4: a second checkout of the member (no remote, the packet's HEAD) that the rehearsal tool did not make."""
    import shutil
    member, pk = _copy_root_fixture(tmp_path, monkeypatch)
    other = tmp_path / "elsewhere" / "m-aget"
    shutil.copytree(member, other)
    assert _copy_root_run(pk, other) == 2
    assert "no readable custody marker" in capsys.readouterr().out
    (other / ".git" / LB.COPY_MARKER).write_text("not json")
    assert _copy_root_run(pk, other) == 2
    assert "no readable custody marker" in capsys.readouterr().out


def test_copy_root_refuses_a_marker_for_another_packet_or_receiver_and_accepts_the_right_one(tmp_path, monkeypatch,
                                                                                            capsys):
    """F-4: the marker must name the digest of the --packet bytes given and the receiver. The last step is the control
    (a dry run, so no session): with the right marker the same folder passes, so the refusals are the marker's doing.
    The marker here is written by the test, which is the stated limit: whoever can write it can forge it."""
    import shutil
    member, pk = _copy_root_fixture(tmp_path, monkeypatch)
    other = tmp_path / "elsewhere" / "m-aget"
    shutil.copytree(member, other)
    assert LB.CI.isolate(other, "remove", member=True) is None   # as rehearse_v37 does (E2g: the session ENV is checked)
    for packet_bytes, aget in ((b"another packet", "m-aget"), (pk.read_bytes(), "n-aget")):
        _write_marker(other, packet_bytes, aget)
        assert _copy_root_run(pk, other) == 2
        assert "names packet" in capsys.readouterr().out
    _write_marker(other, pk.read_bytes(), "m-aget")
    assert _copy_root_run(pk, other, launch=False) == 0
    assert f"DRY RUN m-aget: cwd {other.resolve()}" in capsys.readouterr().out


def test_a_copy_made_by_the_session_rehearsal_is_accepted_by_the_launcher(tmp_path, monkeypatch, capsys):
    """F-4: step B3 keeps working. rehearse_v37.rehearse makes the copy and writes the marker; its launcher call is run
    here in-process with the arguments it built, minus --launch (a dry run: the launcher's folder tests run, no session
    starts), and the apply is made to fail so the rehearsal stops there. The member itself gets no marker."""
    member, pk = _copy_root_fixture(tmp_path, monkeypatch)
    RV = _v37()
    seen = []

    def fake_run(*cmd):
        if Path(str(cmd[1])).name != "launch_batch.py":
            return 1
        seen.append(LB.main([str(c) for c in cmd[2:] if str(c) != "--launch"]))
        return seen[-1]

    monkeypatch.setattr(RV, "run", fake_run)
    verdict = RV.rehearse("m-aget", pk, json.loads(pk.read_text()), {"agets": [{"aget": "m-aget"}]}, tmp_path / "scr")
    copy = tmp_path / "scr" / "m-aget"
    assert verdict == "apply failed" and seen == [0]
    assert f"DRY RUN m-aget: cwd {copy.resolve()}" in capsys.readouterr().out
    marker = json.loads((copy / ".git" / RV.COPY_MARKER).read_text())
    assert marker["packet_sha256"] == hashlib.sha256(pk.read_bytes()).hexdigest() and marker["aget"] == "m-aget"
    assert RV.COPY_MARKER == LB.COPY_MARKER and not (member / ".git" / LB.COPY_MARKER).exists()
    pk.write_text(pk.read_text() + "\n")                    # the packet changed after the copy was made
    assert _copy_root_run(pk, copy) == 2
    assert "names packet" in capsys.readouterr().out


def _marked_copy(tmp_path, monkeypatch):
    """A separate copy of the fixture member with its own .git folder, no remote, the packet's HEAD and the right
    marker: the folder the launcher accepted before the git identity tests (the last control below shows it still
    does when nothing redirects git)."""
    import shutil
    member, pk = _copy_root_fixture(tmp_path, monkeypatch)
    other = tmp_path / "elsewhere" / "m-aget"
    shutil.copytree(member, other)
    assert LB.CI.isolate(other, "remove", member=True) is None   # as rehearse_v37 does (E2g: the session ENV is checked)
    _write_marker(other, pk.read_bytes(), "m-aget")
    return member, pk, other


def test_copy_root_refuses_a_copy_whose_git_working_tree_is_the_member(tmp_path, monkeypatch, capsys):
    """F-4 (second review, 2026-10-02): the copy's own config sets core.worktree to the member, so git run in the copy
    acts on the member (`git checkout -- a.txt` there rewrote the member's file). The launcher refuses, as a dry run
    too, and the helper names the reason. Control: with the setting removed the same folder is accepted."""
    import subprocess
    member, pk, other = _marked_copy(tmp_path, monkeypatch)
    subprocess.run(["git", "-C", str(other), "config", "core.worktree", str(member.resolve())], check=True)
    top = subprocess.run(["git", "-C", str(other), "rev-parse", "--show-toplevel"], capture_output=True, text=True)
    assert Path(top.stdout.strip()).resolve() == member.resolve()            # the redirection is real in this git
    for launch in (True, False):
        assert _copy_root_run(pk, other, launch=launch) == 2
        assert "acts on the working tree" in capsys.readouterr().out
    assert "acts on the working tree" in LB.git_identity_refusal(other)
    subprocess.run(["git", "-C", str(other), "config", "--unset", "core.worktree"], check=True)
    assert LB.git_identity_refusal(other) is None
    assert _copy_root_run(pk, other, launch=False) == 0


def test_copy_root_refuses_a_git_folder_that_is_not_the_copys_own(tmp_path, monkeypatch, capsys):
    """F-4: a linked worktree of the member (its .git is a `gitdir:` file into the member's .git folder), and a copy
    whose .git folder is its own but whose `commondir` file names the member's .git folder."""
    import subprocess
    member, pk, other = _marked_copy(tmp_path, monkeypatch)
    linked = tmp_path / "wt" / "m-aget"
    subprocess.run(["git", "-C", str(member), "worktree", "add", "--detach", "-q", str(linked)], check=True)
    assert (linked / ".git").is_file()
    assert "not a folder of its own" in LB.git_identity_refusal(linked)
    assert _copy_root_run(pk, linked) == 2
    assert "not a folder of its own" in capsys.readouterr().out
    (other / ".git" / "commondir").write_text(str((member / ".git").resolve()) + "\n")
    why = LB.git_identity_refusal(other)
    assert why and ("uses the git folder" in why or "cannot name" in why)
    assert _copy_root_run(pk, other) == 2


@pytest.mark.parametrize("var", ["GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                                 "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES", "GIT_NAMESPACE"])
def test_copy_root_refuses_an_environment_that_tells_git_where_the_repository_is(tmp_path, monkeypatch, capsys, var):
    """F-4: a session inherits the launcher's environment, and these variables move git's repository, working tree,
    index or object store whatever folder it runs in. Refused by name, before git is asked."""
    member, pk, other = _marked_copy(tmp_path, monkeypatch)
    assert LB.git_identity_refusal(other) is None                              # control: accepted without it
    monkeypatch.setenv(var, str(member / ".git"))
    assert var in LB.git_identity_refusal(other)
    assert _copy_root_run(pk, other) == 2
    assert f"the environment holds {var}" in capsys.readouterr().out


def test_copy_root_refuses_a_bare_or_unreadable_repository(tmp_path, monkeypatch):
    import subprocess
    member, pk, other = _marked_copy(tmp_path, monkeypatch)
    subprocess.run(["git", "-C", str(other), "config", "core.bare", "true"], check=True)
    assert "cannot name a working tree" in LB.git_identity_refusal(other)
    plain = tmp_path / "plain"
    plain.mkdir()
    assert "not a folder of its own" in LB.git_identity_refusal(plain)


def _rehearsal_spy(monkeypatch):
    RV = _v37()
    calls = []
    monkeypatch.setattr(RV, "run", lambda *cmd: (calls.append([str(c) for c in cmd]), 1)[1])
    return RV, calls


def test_the_rehearsal_refuses_a_copy_that_inherits_the_members_working_tree_setting(tmp_path, monkeypatch):
    """F-4: `cp -a` copies the member's git settings. A member whose config names its own folder as core.worktree
    yields a copy in which git acts on the member. The rehearsal stops before the remote removal, the marker, the
    apply and any launch; the member's file is as it was."""
    import subprocess
    member, pk = _copy_root_fixture(tmp_path, monkeypatch)
    subprocess.run(["git", "-C", str(member), "config", "core.worktree", str(member.resolve())], check=True)
    RV, calls = _rehearsal_spy(monkeypatch)
    verdict = RV.rehearse("m-aget", pk, json.loads(pk.read_text()), {"agets": [{"aget": "m-aget"}]}, tmp_path / "scr")
    assert verdict.startswith("copy not usable, nothing applied or launched") and "acts on the working tree" in verdict
    assert calls == [] and not (tmp_path / "scr" / "m-aget" / ".git" / RV.COPY_MARKER).exists()
    assert (member / "a.txt").read_text() == "x\n"
    subprocess.run(["git", "-C", str(member), "config", "--unset", "core.worktree"], check=True)   # control
    assert RV.rehearse("m-aget", pk, json.loads(pk.read_text()), {"agets": [{"aget": "m-aget"}]},
                       tmp_path / "scr2") == "baseline not RECORDED"   # E2g: a fresh run folder; nothing is cleared
    assert len(calls) == 1 and Path(calls[0][1]).name == "launch_batch.py"


def test_the_rehearsal_removes_nothing_when_the_copy_folder_would_be_the_member(tmp_path, monkeypatch):
    """F-4: with --scratch set to the folder that holds the member, <scratch>/<name> is the member itself, and the
    cleanup before the copy removed it. With declared siblings the folder cleared is <scratch>/<name>.root; a scratch
    inside the member is refused there too. Nothing is removed, copied or launched."""
    member, pk = _copy_root_fixture(tmp_path, monkeypatch)
    RV, calls = _rehearsal_spy(monkeypatch)
    packet = json.loads(pk.read_text())
    verdict = RV.rehearse("m-aget", pk, packet, {"agets": [{"aget": "m-aget"}]}, member.parent)
    assert verdict.startswith("copy not made") and "nothing was removed" in verdict
    packet["receivers"][0]["sibling_reads"] = ["../sib"]
    verdict = RV.rehearse("m-aget", pk, packet, {"agets": [{"aget": "m-aget"}]}, member / "sub")
    assert verdict.startswith("copy not made")
    assert calls == [] and (member / "a.txt").read_text() == "x\n" and (member / "sub" / "b.txt").exists()
    assert not (member / "sub" / "m-aget.root").exists()


# ---------- one isolation routine for every copy the kit makes (second review, 2026-10-02) ----------

CI = load("copy_isolation")


def _member(tmp_path, name="seat"):
    """A member repository at tmp_path/home/<name> with one commit and a bare remote; returns (member, git, remote)."""
    import subprocess
    member = tmp_path / "home" / name
    g = _git_repo(member, {"a.txt": "x\n", "sub/b.txt": "y\n"})
    remote = tmp_path / f"{name}_remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    g("remote", "add", "origin", str(remote))
    return member, g, remote


def test_copy_isolation_place_identity_and_remotes(tmp_path):
    """The routine as functions. place_refusal: the live folder, a folder holding it and (unless inside_ok) a folder
    inside it. isolate: a plain folder is left alone; a clean copy loses its remotes or gets the push URL; a copy whose
    git acts elsewhere is refused with nothing changed."""
    import shutil
    member, g, remote = _member(tmp_path)
    assert "nothing was removed or copied" in CI.place_refusal(member, member)
    assert CI.place_refusal(member.parent, member) and CI.place_refusal(member / "sub", member)
    assert CI.place_refusal(member / "sub", member, inside_ok=True) is None
    assert CI.place_refusal(member, member, inside_ok=True) and CI.place_refusal(member.parent, member, inside_ok=True)
    assert CI.place_refusal(tmp_path / "elsewhere", member) is None
    plain = tmp_path / "plain"
    plain.mkdir()
    assert CI.isolate(plain, "remove") is None and CI.isolate(plain, "no-push") is None
    a, b = tmp_path / "a", tmp_path / "b"
    shutil.copytree(member, a, symlinks=True)
    shutil.copytree(member, b, symlinks=True)
    assert CI.isolate(a, "remove") is None and g("remote") == "origin"                 # the live remote is still there
    assert (a / ".git" / "config").read_text().count("[remote") == 0
    assert CI.isolate(b, "no-push") is None and CI.NO_PUSH_URL in (b / ".git" / "config").read_text()
    c = tmp_path / "c"
    shutil.copytree(member, c, symlinks=True)
    import subprocess
    subprocess.run(["git", "-C", str(c), "config", "core.worktree", str(member.resolve())], check=True)
    before = (c / ".git" / "config").read_text()
    assert "acts on the working tree" in CI.isolate(c, "remove") and (c / ".git" / "config").read_text() == before
    with pytest.raises(ValueError):
        CI.isolate(a, "keep")


def test_isolation_refuses_a_git_folder_that_links_outside_itself(tmp_path):
    """Reviewer session, 2026-10-02: a copy whose .git/config is a symbolic link to the member's config passes every
    identity question (working tree, git folder and common folder are the copy's own), and removing the copy's
    remotes then removed the member's. Any entry under .git that links outside it refuses, before a remote is
    touched; a link that stays inside .git is accepted."""
    import shutil
    member, g, _ = _member(tmp_path)
    copy = tmp_path / "copy"
    shutil.copytree(member, copy, symlinks=True)
    (copy / ".git" / "config").unlink()
    (copy / ".git" / "config").symlink_to(member / ".git" / "config")
    for mode in ("remove", "no-push"):
        why = CI.isolate(copy, mode)
        assert why and "symbolic link that leads outside" in why
    assert g("remote") == "origin" and CI.NO_PUSH_URL not in (member / ".git" / "config").read_text()
    inside = tmp_path / "inside"
    shutil.copytree(member, inside, symlinks=True)
    (inside / ".git" / "alias_of_head").symlink_to("HEAD")
    assert CI.outside_link(inside / ".git") is None and CI.isolate(inside, "remove") is None


def test_isolation_reads_back_the_push_url_git_would_use(tmp_path):
    """Reviewer session, 2026-10-02: with `url.<path>.insteadOf` set to the no-push URL, the stored push URL was the
    no-push one and `git push origin` still reached a writable remote. The push URL is read back from git after it is
    set; a rewritten one is a reason, not a success."""
    import shutil, subprocess
    member, g, remote = _member(tmp_path)
    copy = tmp_path / "copy"
    shutil.copytree(member, copy, symlinks=True)
    subprocess.run(["git", "-C", str(copy), "config", f"url.{remote}.insteadOf", CI.NO_PUSH_URL], check=True)
    # R1 (kit design pass, J-3): a rewrite rule copied into the copy's own config is now removed, so the copy is made
    # safe rather than refused, and the push from it fails
    assert CI.isolate(copy, "no-push") is None
    assert subprocess.run(["git", "-C", str(copy), "push", "origin", "HEAD:refs/heads/p0"], capture_output=True,
                          ).returncode != 0
    # a rule isolation cannot remove (here in the global config the environment names) is still read back: refused
    gconf = tmp_path / "global.gitconfig"
    gconf.write_text(f'[url "{remote}"]\n\tinsteadOf = {CI.NO_PUSH_URL}\n')
    env = {k: v for k, v in __import__("os").environ.items()} | {"GIT_CONFIG_GLOBAL": str(gconf)}
    other = tmp_path / "copy2"
    shutil.copytree(member, other, symlinks=True)
    why = CI.isolate(other, "no-push", env)
    assert why and "the push URL git would use for remote 'origin'" in why and str(remote) in why
    clean = tmp_path / "clean"
    shutil.copytree(member, clean, symlinks=True)
    assert CI.isolate(clean, "no-push") is None                                    # control
    pushed = subprocess.run(["git", "-C", str(clean), "push", "origin", "HEAD:refs/heads/probe"], capture_output=True)
    refs = subprocess.run(["git", "--git-dir", str(remote), "for-each-ref"], capture_output=True, text=True).stdout
    assert pushed.returncode != 0 and refs == ""


@pytest.mark.parametrize("var", ["GIT_INDEX_FILE", "GIT_DIR", "GIT_WORK_TREE"])
def test_nothing_is_removed_copied_or_cloned_while_the_environment_redirects_git(tmp_path, monkeypatch, var):
    """Reviewer session, 2026-10-02: the suite check cloned and checked out with GIT_INDEX_FILE pointing at a live
    repository's index and changed that index; the environment was tested only later, on the sibling copies. Every
    tool now asks before its first removal, copy or clone."""
    RB = _load("batch2", "rehearse_batch2")
    RR = _load("batch1", "rehearse_repair")
    SAC = load("suite_at_commit")
    member, g, _ = _member(tmp_path)
    head = g("rev-parse", "HEAD")
    index = (member / ".git" / "index").read_bytes()
    monkeypatch.setenv(var, str(member / ".git" / "index"))
    scratch = tmp_path / "scr"
    scratch.mkdir()
    r = {"aget": "seat", "location": str(member), "head": head}
    with pytest.raises(ValueError, match=var):
        RB.copy_of(r, scratch)
    assert var in RR.rehearse(r, head, scratch, tmp_path / "ev")["verdict"]
    dest, why = SAC.clean_clone(member, "seat", head, [], tmp_path / "work")
    assert dest is None and var in why and not (tmp_path / "work").exists()
    assert list(scratch.iterdir()) == [] and (member / ".git" / "index").read_bytes() == index


def test_the_packet_rehearsal_refuses_a_copy_whose_git_acts_on_the_member(tmp_path):
    """Review finding (second independent review): B2 runs before B3 and made its copy with no isolation test, then
    removed remotes, staged and committed through git in the copy. A member whose config names its own folder as
    core.worktree is refused; its remote, its files and its config are as they were."""
    import subprocess
    RB = _load("batch2", "rehearse_batch2")
    member, g, _ = _member(tmp_path)
    subprocess.run(["git", "-C", str(member), "config", "core.worktree", str(member.resolve())], check=True)
    config = (member / ".git" / "config").read_text()
    scratch = tmp_path / "scr"
    scratch.mkdir()
    with pytest.raises(ValueError, match="acts on the working tree"):
        RB.copy_of({"aget": "seat", "location": str(member)}, scratch)
    assert (member / ".git" / "config").read_text() == config and g("remote") == "origin"
    subprocess.run(["git", "-C", str(member), "config", "--unset", "core.worktree"], check=True)      # control
    scratch = tmp_path / "scr2"                      # E2g: each run has a fresh folder; nothing is cleared in one
    scratch.mkdir()
    dest = RB.copy_of({"aget": "seat", "location": str(member)}, scratch)
    assert RB.RR.git(dest, "remote").stdout.strip() == "" and g("remote") == "origin"


def test_the_packet_rehearsal_removes_nothing_when_its_copy_folder_would_be_the_member(tmp_path):
    RB = _load("batch2", "rehearse_batch2")
    member, g, _ = _member(tmp_path)
    r = {"aget": "seat", "location": str(member)}
    with pytest.raises(ValueError, match="nothing was removed or copied"):
        RB.copy_of(r, member.parent)                                  # <scratch>/seat is the member itself
    with pytest.raises(ValueError, match="nothing was removed or copied"):
        RB.copy_of(r, member / "sub", ["../sib"])                     # <scratch>/seat.root lies inside the member
    assert (member / "a.txt").read_text() == "x\n" and (member / "sub" / "b.txt").exists()


def test_the_packet_rehearsal_isolates_each_copied_sibling(tmp_path):
    """A copied sibling keeps its remotes with pushing closed; one whose .git is a file (a linked worktree, a
    submodule) is refused, because git in the copy would use the live git folder."""
    import subprocess
    RB = _load("batch2", "rehearse_batch2")
    member, g, _ = _member(tmp_path)
    sib, sg, sremote = _member(tmp_path, "sib")
    scratch = tmp_path / "scr"
    scratch.mkdir()
    r = {"aget": "seat", "location": str(member)}
    dest = RB.copy_of(r, scratch, ["../sib"])
    assert CI.NO_PUSH_URL in (dest.parent / "sib" / ".git" / "config").read_text() and sg("remote") == "origin"
    assert CI.NO_PUSH_URL not in (sib / ".git" / "config").read_text()
    linked = tmp_path / "home" / "linked"
    subprocess.run(["git", "-C", str(sib), "worktree", "add", "--detach", "-q", str(linked)], check=True)
    scratch = tmp_path / "scr2"                      # E2g: each run has a fresh folder; nothing is cleared in one
    scratch.mkdir()
    with pytest.raises(ValueError, match="sibling '../linked'.*not a folder of its own"):
        RB.copy_of(r, scratch, ["../linked"])


def test_the_repair_rehearsal_refuses_a_copy_whose_git_acts_on_the_member(tmp_path):
    import subprocess
    RR = _load("batch1", "rehearse_repair")
    member, g, _ = _member(tmp_path)
    head = g("rev-parse", "HEAD")
    r = {"aget": "seat", "location": str(member), "head": head}
    ev = tmp_path / "ev"
    res = RR.rehearse(r, head, member.parent, ev)                     # <scratch>/seat is the member itself
    assert res["verdict"].startswith("INCONCLUSIVE") and "nothing was removed or copied" in res["verdict"]
    subprocess.run(["git", "-C", str(member), "config", "core.worktree", str(member.resolve())], check=True)
    (member / "a.txt").write_text("uncommitted live work\n")
    scratch = tmp_path / "scr"
    scratch.mkdir()
    res = RR.rehearse(r, head, scratch, ev)
    assert res["verdict"].startswith("INCONCLUSIVE") and "acts on the working tree" in res["verdict"]
    assert (member / "a.txt").read_text() == "uncommitted live work\n" and g("remote") == "origin"
    assert "S0" not in res                                             # no checkout and no suite ran


def _v37_world(tmp_path, monkeypatch, launch):
    """rehearse_v37.rehearse on the fixture member with its tool calls replaced: the baseline launch and the apply
    return 0 (the apply leaves a receipt), and the session launch is `launch(evidence_folder)`, returning its exit."""
    member, pk = _copy_root_fixture(tmp_path, monkeypatch)
    RV = _v37()
    ev = tmp_path / "scr" / "evidence" / "m-aget"

    def fake_run(*cmd):
        argv = [str(c) for c in cmd]
        if Path(argv[1]).name == "apply_protected.py":
            (ev / "APPLY_RECEIPT_x.json").write_text("{}")
            return 0
        return launch(ev) if "--apply-receipt" in argv else 0

    monkeypatch.setattr(RV, "run", fake_run)
    go = lambda: RV.rehearse("m-aget", pk, json.loads(pk.read_text()), {"agets": [{"aget": "m-aget"}]}, tmp_path / "scr")
    return RV, pk, ev, go


def test_a_failed_session_rehearsal_does_not_report_an_earlier_pass(tmp_path, monkeypatch):
    """Review finding (second independent review): the evidence folder is reused, the session launch's exit code was
    not checked, and the after-run record was read as found, so an earlier PASS stood for a launch that failed before
    writing one; the approval step accepted it. Now the two records are removed before the launch, and a launch that
    does not exit 0 gives no verdict. Control: a launch that exits 0 and writes PASS is PASS."""
    CA = _load("batch2", "check_list_approvable")
    RV, pk, ev, go = _v37_world(tmp_path, monkeypatch, lambda ev: 7)
    ev.mkdir(parents=True)
    (ev / "after_run_check.json").write_text(json.dumps({"verdict": "PASS"}))
    (ev / "launch_record.json").write_text(json.dumps({"from": "an earlier run"}))
    verdict = go()
    assert verdict == "session launch failed (exit 7)"
    assert not (ev / "after_run_check.json").exists() and not (ev / "launch_record.json").exists()
    lst = tmp_path / "LIST.json"
    lst.write_text(json.dumps({"agets": [{"aget": "m-aget"}]}))
    doc = RV.result_doc("99", pk, lst, ev.parent, {"m-aget": verdict}, "t0")
    assert doc["verdict"] == "FAIL" and doc["members"]["m-aget"]["after_run_check"] is None
    v36 = {"results": [{"aget": "m-aget", "verdict": "PASS"}]}
    assert any("V3.7" in x for x in CA.problems(json.loads(lst.read_text()), v36, doc))      # the approval step refuses


def test_a_session_rehearsal_that_writes_no_record_or_a_fresh_pass(tmp_path, monkeypatch):
    RV, pk, ev, go = _v37_world(tmp_path, monkeypatch, lambda ev: 0)
    ev.mkdir(parents=True)
    (ev / "after_run_check.json").write_text(json.dumps({"verdict": "PASS"}))          # stale, and the launch writes none
    assert go() == "no after-run result"

    def writes_pass(folder):
        (folder / "after_run_check.json").write_text(json.dumps({"verdict": "PASS"}))
        return 0

    RV2, pk2, ev2, go2 = _v37_world(tmp_path / "second", monkeypatch, writes_pass)
    assert go2() == "PASS"


def test_a_rehearsal_that_stops_before_its_end_leaves_no_earlier_pass_in_its_result_file(tmp_path, monkeypatch):
    """Reviewer session, 2026-10-02: the session rehearsal wrote its result only after the receiver loop, so a copy
    that could not be made left an earlier V37 PASS in place and the approval step accepted it (the rehearsal exited 1,
    the approval 0). The packet and repair rehearsals wrote theirs the same way. Each now writes a not-finished result
    before its first copy. Here each tool's rehearse step raises; the result file left behind is not a PASS and the
    approval step refuses it."""
    CA = _load("batch2", "check_list_approvable")
    member, pk = _copy_root_fixture(tmp_path, monkeypatch)
    lst = tmp_path / "LIST.json"
    lst.write_text(json.dumps({"agets": [{"aget": "m-aget"}]}))
    digest = hashlib.sha256(lst.read_bytes()).hexdigest()

    def boom(*a, **k):
        raise RuntimeError("the copy could not be made")

    RV = _v37()
    out37 = tmp_path / "V37.json"
    out37.write_text(json.dumps({"verdict": "PASS", "list_sha256": digest, "members": {}}))      # an earlier PASS
    monkeypatch.setattr(RV, "rehearse", boom)
    # R4 (kit design pass, Gate 3): the step that raises becomes that member's REFUSED result, with no traceback, and
    # the result file is written with it; before R4 the exception escaped and NOT FINISHED was left.
    assert RV.main(["--batch", "99", "--scratch", str(tmp_path / "scr"), "--packet", str(pk), "--list", str(lst),
                    "--out", str(out37), "m-aget"]) == 1
    left = json.loads(out37.read_text())
    assert left["verdict"] == "FAIL" and left["list_sha256"] == digest
    assert left["members"]["m-aget"]["verdict"].startswith("REFUSED: RuntimeError")
    v36 = {"results": [{"aget": "m-aget", "verdict": "PASS"}], "list_sha256": digest}
    assert any("V3.7" in x for x in CA.problems(json.loads(lst.read_text()), v36, left))

    RB = _load("batch2", "rehearse_batch2")
    out36 = tmp_path / "V36.json"
    out36.write_text(json.dumps({"results": [{"aget": "m-aget", "verdict": "PASS"}], "list_sha256": digest}))
    monkeypatch.setattr(RB, "rehearse", boom)
    monkeypatch.setattr(RB.R, "require", lambda: None)
    assert RB.main(["--packet", str(pk), "--list", str(lst), "--scratch", str(tmp_path / "scr2"),
                    "--out", str(out36)]) == 1
    left = json.loads(out36.read_text())
    assert [x["verdict"].split(":")[:2] for x in left["results"]] == [["REFUSED", " RuntimeError"]]
    assert any("m-aget" in x for x in CA.problems(json.loads(lst.read_text()), left, None))


def test_a_rehearsal_that_cannot_even_start_leaves_no_earlier_pass(tmp_path, monkeypatch):
    """Reviewer session, 2026-10-02, one step earlier than the test above: a scratch folder that cannot be made (here
    its parent is a file) stopped the tool before it had touched the result file. Writing NOT FINISHED is now the
    tools' first act, before the packet is read or a folder is made."""
    member, pk = _copy_root_fixture(tmp_path, monkeypatch)
    lst = tmp_path / "LIST.json"
    lst.write_text(json.dumps({"agets": [{"aget": "m-aget"}]}))
    blocker = tmp_path / "a_file"
    blocker.write_text("x")
    RV, RB, RR = _v37(), _load("batch2", "rehearse_batch2"), _load("batch1", "rehearse_repair")
    monkeypatch.setattr(RB.R, "require", lambda: None)
    old_pass = json.dumps({"verdict": "PASS", "results": [{"aget": "m-aget", "verdict": "PASS"}]})
    runs = ((RV, ["--batch", "99", "--scratch", str(blocker / "scr"), "--packet", str(pk), "--list", str(lst),
                  "--out", str(tmp_path / "V37.json"), "m-aget"], tmp_path / "V37.json"),
            (RB, ["--packet", str(pk), "--list", str(lst), "--scratch", str(blocker / "scr"),
                  "--out", str(tmp_path / "V36.json")], tmp_path / "V36.json"),
            (RV, ["--batch", "99", "--scratch", str(tmp_path / "s"), "--packet", str(tmp_path / "no_packet.json"),
                  "--list", str(lst), "--out", str(tmp_path / "V37b.json"), "m-aget"], tmp_path / "V37b.json"))
    for tool, argv, out in runs:
        out.write_text(old_pass)
        # R4 C1 (kit design pass, Gate 3): an input or scratch folder that cannot be used refuses the run, exit 2, no
        # traceback; the earlier PASS is gone either way.
        assert tool.main(argv) == 2
        left = json.loads(out.read_text())
        assert left["verdict"] == "REFUSED" and not left.get("results") and not left.get("members")
    assert RR.NOT_FINISHED == RV.NOT_FINISHED


def test_the_packet_rehearsal_invalidates_its_result_before_refusing_a_missing_release_target(tmp_path, monkeypatch):
    """Reviewer session, 2026-10-02 (B110, B111): the packet rehearsal asked for the release target before it wrote
    NOT FINISHED, so with no target set it stopped and left an earlier V3.6 PASS that the approval step accepted. The
    target is still required before any receiver work, now after the result is invalidated."""
    RB = _load("batch2", "rehearse_batch2")
    out = tmp_path / "V36.json"
    out.write_text(json.dumps({"results": [{"aget": "m-aget", "verdict": "PASS"}]}))

    def no_target():
        raise SystemExit(1)

    monkeypatch.setattr(RB.R, "require", no_target)
    with pytest.raises(SystemExit):
        RB.main(["--packet", str(tmp_path / "P.json"), "--list", str(tmp_path / "L.json"),
                 "--scratch", str(tmp_path / "scr"), "--out", str(out)])
    assert json.loads(out.read_text()) == RB.NOT_FINISHED and not (tmp_path / "scr").exists()


def _shared_repository(tmp_path):
    """A shared repository holding two members as folders (no .git of their own); memberB has a staged change and a
    further unstaged edit, and a scratch folder sits inside the shared repository, outside both members."""
    shared = tmp_path / "home" / "shared"
    g = _git_repo(shared, {"memberA/a.txt": "a\n", "memberB/notes.txt": "v1\n"})
    (shared / "memberB" / "notes.txt").write_text("staged work of memberB\n")
    g("add", "memberB/notes.txt")
    (shared / "memberB" / "notes.txt").write_text("staged work of memberB, further edit\n")
    scratch = shared / "rehearsal_scratch"
    scratch.mkdir()

    def state():
        return (g("rev-parse", "HEAD"), g("symbolic-ref", "-q", "HEAD"), g("diff", "--cached", "--name-only"),
                (shared / "memberB" / "notes.txt").read_text())
    return shared, g, scratch, state


def test_a_member_copy_without_its_own_git_is_refused_before_any_git_command(tmp_path):
    """Supervisor round three (packet r6, H-1): a member that is a folder inside a shared repository has no .git of its
    own; isolate() admitted its copy untested, and with the scratch folder inside the shared repository the repair
    rehearsal ran `git checkout -f` in the live repository and the packet rehearsal committed on its live branch. A
    member copy with no .git of its own is now refused; a sibling copy with none is still a plain folder."""
    shared, g, scratch, state = _shared_repository(tmp_path)
    plain = tmp_path / "plain"
    plain.mkdir()
    assert "no .git of its own" in CI.isolate(plain, "remove", member=True)
    assert "no .git of its own" in CI.isolate(plain, "no-push", member=True)
    assert CI.isolate(plain, "remove") is None                              # a sibling's plain folder
    before = state()
    RB = _load("batch2", "rehearse_batch2")
    with pytest.raises(ValueError, match="no .git of its own"):
        RB.copy_of({"aget": "memberA", "location": str(shared / "memberA")}, scratch)
    assert state() == before
    RR = _load("batch1", "rehearse_repair")
    head = g("rev-parse", "HEAD")
    res = RR.rehearse({"aget": "memberA", "location": str(shared / "memberA"), "head": head}, head, scratch,
                      tmp_path / "ev")
    assert res["verdict"].startswith("INCONCLUSIVE") and "no .git of its own" in res["verdict"]
    assert "S0" not in res and state() == before                           # nothing ran; the live repository as it was


@pytest.mark.parametrize("mode", ["remove", "no-push"])
def test_isolation_deletes_remotes_defined_in_the_older_files(tmp_path, mode):
    """Supervisor round three (packet r6, H-2): a remote defined by a file under .git/remotes/ or .git/branches/ is
    not listed by `git remote`, survived isolation, and `git push <name>` from the copy reached the real remote.
    Isolation now deletes those definitions and reads back that none is left; the push by that name then fails."""
    import shutil
    import subprocess
    member, g, remote = _member(tmp_path)
    (member / ".git" / "remotes").mkdir(exist_ok=True)
    (member / ".git" / "remotes" / "legacy").write_text(f"URL: {remote}\n")
    (member / ".git" / "branches").mkdir(exist_ok=True)
    (member / ".git" / "branches" / "older").write_text(f"{remote}\n")
    assert [p.name for p in CI.legacy_remote_files(member / ".git")] == ["legacy", "older"]
    copy = tmp_path / "copy"
    shutil.copytree(member, copy, symlinks=True)
    assert CI.isolate(copy, mode) is None
    assert CI.legacy_remote_files(copy / ".git") == []
    assert (member / ".git" / "remotes" / "legacy").exists()                 # the member's own definitions stay
    for name in ("legacy", "older"):
        p = subprocess.run(["git", "-C", str(copy), "push", "-q", name, "HEAD:refs/heads/arrived"],
                           capture_output=True, text=True)
        assert p.returncode != 0
    assert subprocess.run(["git", "--git-dir", str(remote), "rev-parse", "--verify", "-q", "refs/heads/arrived"],
                          capture_output=True).returncode != 0


def test_copy_root_refuses_a_copy_with_a_remote_defined_in_the_older_files(tmp_path, monkeypatch, capsys):
    """Supervisor round three (packet r6, H-2): the launcher's own remote test used `git remote`, which does not list
    a remote defined by a file under .git/remotes/ or .git/branches/. Such a folder is now refused; removing the file
    makes the same folder pass (a dry run), so the refusal is the file's doing."""
    import shutil
    member, pk = _copy_root_fixture(tmp_path, monkeypatch)
    other = tmp_path / "elsewhere" / "m-aget"
    shutil.copytree(member, other)
    assert LB.CI.isolate(other, "remove", member=True) is None   # as rehearse_v37 does (E2g: the session ENV is checked)
    _write_marker(other, pk.read_bytes(), "m-aget")
    (other / ".git" / "branches").mkdir(exist_ok=True)
    (other / ".git" / "branches" / "older").write_text(str(tmp_path / "somewhere.git") + "\n")
    assert _copy_root_run(pk, other, launch=False) == 2
    assert "the copy has remotes" in capsys.readouterr().out
    (other / ".git" / "branches" / "older").unlink()
    assert _copy_root_run(pk, other, launch=False) == 0


def test_an_unsafe_path_gets_no_command_no_write_permission_and_no_merge(tmp_path):
    """Reviewer session, B131: a path through a symbolic link was a `hold`, and a hold gets an Edit rule, a write-set
    entry and a MERGE instruction, so the session was told and permitted to edit through the link. It is now
    `unsafe`: no command, no Edit rule, no write-set entry, and the prompt says to leave it. The ordinary hold in the
    same packet keeps its merge, rule and write-set entry (the control)."""
    loc = tmp_path / "m"
    (loc / "scripts").mkdir(parents=True)
    (tmp_path / "elsewhere.py").write_text("x\n")
    (loc / "scripts" / "linked.py").symlink_to(tmp_path / "elsewhere.py")
    item = PL.classify_path(str(loc), "scripts/linked.py", tmp_path / "no-src", tmp_path / "no-tpl")
    assert item["op"] == "unsafe" and "symbolic link" in item["why"]
    PL.placing_commands(item, str(loc))
    assert "command" not in item
    r = {**R, "items": R["items"] + [item]}
    p = PL.prompt(r, "att-1", [])
    assert "LEAVE scripts/linked.py: not migrated" in p and "MERGE scripts/linked.py" not in p
    assert "MERGE scripts/b.py" in p
    assert "scripts/linked.py" not in PL.write_set(r) and "scripts/b.py" in PL.write_set(r)
    rules = PL.allowlist(r)
    assert "Edit(scripts/linked.py)" not in rules and "Edit(scripts/b.py)" in rules
    assert not [x for x in rules if "linked.py" in x]


# --- C2a: R2-T14, a truncated baseline output is not recorded ----------------------------------------------------

def _stream(output, cmd="python3 -m pytest -q -rfE"):
    """A session stream in which the baseline command ran and returned `output`."""
    # C2a10 (B192 finding 2, changed, labelled): a Bash call, as both readers now require
    use = {"sessionId": "S", "message": {"content": [{"type": "tool_use", "id": "u1", "name": "Bash", "input": {"command": cmd}}]}}
    res = {"sessionId": "S", "message": {"content": [{"type": "tool_result", "tool_use_id": "u1", "content": output}]}}
    return json.dumps(use) + "\n" + json.dumps(res) + "\n", cmd


# C2a7 (B185 finding 1, changed, labelled): each row's run has a kit report holding `failing`; `mark` says whether the
# output still names its invocation (a cut output loses it); the last row's report holds fewer events than its count
@pytest.mark.parametrize("output,failing,mark,complete", [
    # B180 finding 1 (changed, labelled): the complete rows carry pytest's short summary header, as pytest prints it
    ("=== short test summary info ===\n"
     "FAILED tests/t.py::a - x\nFAILED tests/t.py::b - y\n==== 2 failed, 5 passed in 1.0s ====",
     ["tests/t.py::a", "tests/t.py::b"], True, True),
    ("[... 400 lines truncated ...]\nFAILED tests/t.py::b - y\n==== 2 failed, 5 passed in 1.0s ====",
     ["tests/t.py::a", "tests/t.py::b"], False, False),
    ("=== short test summary info ===\nERROR tests/t.py::c\n==== 1 error, 5 passed in 1.0s ====",
     [("tests/t.py::c", "setup")], True, True),
    ("==== 3 failed, 1 error, 5 passed in 1.0s ====", ["tests/t.py::a", "tests/t.py::b"], True, False),
])
def test_r2_t14_a_truncated_baseline_output_is_not_complete(tmp_path, output, failing, mark, complete):
    """R2-T14 (S-168). The baseline's failing ids must account for its own summary's failed and error counts; a tool
    result cut short keeps its summary but loses ids, and is not complete, so the baseline is not RECORDED. Before
    C2a the summary alone made it RECORDED with ids missing."""
    rpt, tok, (text,) = _kit_report().reported(tmp_path / "r.jsonl", [(output, failing)])
    stream, cmd = _stream(text if mark else output)
    parsed = LB.parse_baseline(stream, cmd, rpt, tok)
    assert parsed["complete"] is complete, parsed


# --- REVW9's B179 read of stage C2a: failing ids are read whole --------------------------------------------------

@pytest.mark.parametrize("output,ids,complete", [
    # B180 finding 1 (changed, labelled): pytest's short summary header added to each output
    ("=== short test summary info ===\nFAILED tests/t.py::t[case alpha] - assert 0\n==== 1 failed, 1 passed in 1.0s ====",
     ["tests/t.py::t[case alpha]"], True),
    # changed at C2a5 (B182 finding 1, labelled): a ` - ` inside the id and another before the message leave its end
    # not unique (a name through `globals()` can hold ` - ` too), so this reads not complete: an admission cost
    # changed at C2a7 (B185 finding 1, labelled): the id comes whole from the kit's report, so it is complete; the
    # admission cost is gone for the consumers
    ("=== short test summary info ===\nFAILED tests/t.py::t[a - b] - boom\n==== 1 failed, 1 passed in 1.0s ====",
     ["tests/t.py::t[a - b]"], True),
    # changed at C2a7 (labelled): the display line cut before `]` is not read; the report's id is
    ("=== short test summary info ===\nFAILED tests/t.py::t[unclosed - boom\n==== 1 failed, 1 passed in 1.0s ====",
     ["tests/t.py::t[unclosed - boom]"], True),
])
def test_b179_3_the_baseline_reads_each_failing_id_whole(tmp_path, output, ids, complete):
    """B179 finding 3 (REVW9's falsifier, producer half). A parametrized failing id holding a space is recorded whole,
    so a different failure sharing its first word is a different id; an id that cannot be delimited (an unbalanced
    `[`) makes the baseline not complete. On stage C2a ids were read with `\\S+`: `tests/t.py::t[case` was recorded and
    counted as complete."""
    rpt, tok, (text,) = _kit_report().reported(tmp_path / "r.jsonl", [(output, ids)])   # C2a7 (changed, labelled)
    stream, cmd = _stream(text)
    parsed = LB.parse_baseline(stream, cmd, rpt, tok)
    assert parsed["failures"] == ids and parsed["complete"] is complete, parsed
    assert LB.parse_baseline(_stream(output)[0], cmd, rpt, tok)["complete"] is False   # no report line: not known


def test_b180_1_the_parallel_runner_passes_on_only_each_files_summary(tmp_path):
    """B180 finding 1 (the kit's own suite runner). A test prints a `FAILED` line; the runner's output holds only the
    real failure under one `short test summary info` header, and the kit's reader reads it complete. On stage C2a2 the
    runner took every line starting `FAILED ` and printed no header."""
    import subprocess
    import sys
    (tmp_path / "tests").mkdir()
    (tmp_path / "tests" / "test_a.py").write_text(
        'def test_real():\n    print("FAILED tests/test_a.py::test_printed - fake")\n    assert False\n'
        'def test_printed():\n    pass\n')
    p = subprocess.run([sys.executable, str(BATCH / "run_suite_parallel.py")], cwd=tmp_path, capture_output=True,
                       text=True)
    out = p.stdout
    assert "test_printed" not in out and out.count("short test summary info") == 1, out
    RB = _load("b180", "result_binding")
    assert RB.failing_ids(out) == (["tests/test_a.py::test_real"], None), out


def test_c2e_d8_s351_the_blind_spot_gate_reads_the_mode_from_the_list(tmp_path, capsys):
    """D-8, S-351 (DESIGN's R2-T19): a list entry prepared as migrate, and a V3.6 result labelled `track-skills` with
    no blind-spot report: the gate skipped the member. The mode is the list's; the mismatch is a problem. Controls:
    both migrate with no report is refused for the report; both track-skills is skipped."""
    CA = _load("batch2", "check_list_approvable")
    lst = {"agets": [{"aget": "a", "location": str(tmp_path), "ops": [{"path": "scripts/x.py", "op": "write"}]}]}
    v36 = {"results": [{"aget": "a", "verdict": "PASS", "mode": "track-skills"}]}
    out = CA.blind_spot_problems(lst, v36)
    assert out and "track-skills" in out[0] and "migrate" in out[0], out
    v36["results"][0].pop("mode")
    assert "no V3.6 blind-spot report" in CA.blind_spot_problems(lst, v36)[0]
    lst["agets"][0]["mode"], v36["results"][0]["mode"] = "track-skills", "track-skills"
    assert CA.blind_spot_problems(lst, v36) == []


def test_c2e_d8_s193_s325_one_success_of_an_unrelated_workflow_does_not_widen_blind_spots(tmp_path, monkeypatch):
    """D-8, S-193/S-325 (DESIGN's new R2-T3 case): any non-empty all-success run list on the commit counted as CI
    green, so one success of an unrelated workflow widened the blind spots to every copy failure. CI now corroborates
    only when every root workflow committed at the SHA passed on it (the ledger's ci_result). Control: the committed
    workflow's own success widens them, as supervisor:L816 intends."""
    import sys as _sys
    RB = _load("batch2", "rehearse_batch2")
    FL = _load("batch2", "fleet_ledger")
    monkeypatch.setitem(_sys.modules, "v335_fleet_ledger", FL)
    RB.SAC.WORK = tmp_path / "w"
    loc = tmp_path / "home" / "seat"
    g = _git_repo(loc, {"tests/test_x.py": "def test_a():\n    assert True\n\ndef test_real():\n    assert False\n",
                        ".github/workflows/ci.yml": "name: ci\non: push\n"})
    r = {"aget": "seat", "location": str(loc), "head": g("rev-parse", "HEAD"),
         "suite_cmd": f"{_sys.executable} -m pytest -q -p no:cacheprovider"}
    s0 = {"failures": ["tests/test_x.py::test_a", "tests/test_x.py::test_real"]}
    other = {"status": "completed", "conclusion": "success", "workflowName": "other", "path": ".github/workflows/o.yml"}
    monkeypatch.setattr(FL, "_run_list", lambda root, sha: [other])
    monkeypatch.setattr(FL, "_api_run_count", lambda root, sha: 1)
    rep = RB.blind_spot_report(r, s0, tmp_path / "scr")
    assert rep["reference_ci"]["state"] == "INCOMPLETE", rep["reference_ci"]
    assert rep["blind_spots"] == ["tests/test_x.py::test_a"], rep
    mine = {**other, "workflowName": "ci", "path": ".github/workflows/ci.yml"}
    monkeypatch.setattr(FL, "_run_list", lambda root, sha: [mine])
    rep = RB.blind_spot_report(r, s0, tmp_path / "scr")
    assert rep["reference_ci"]["state"] == "PASS" and len(rep["blind_spots"]) == 2, rep


def test_c2e_d8_s198_s323_a_member_stopped_before_its_launch_embeds_no_earlier_records(tmp_path):
    """D-8, S-198/S-323 (DESIGN's new R2-T7 case): for a member that stopped before its launch (baseline or apply),
    the result embedded the evidence folder's after_run_check.json and launch_record.json, an earlier run's. Only a
    member whose launch this invocation started has its records embedded. Control: a launched member's are."""
    RV = _load("batch2", "rehearse_v37")
    lst, pk = tmp_path / "WRITE_LIST.json", tmp_path / "PACKET.json"
    lst.write_text(json.dumps({"agets": [{"aget": "a"}, {"aget": "b"}]}))
    pk.write_text("{}")
    ev = tmp_path / "evidence"
    for n in ("a", "b"):
        (ev / n).mkdir(parents=True)
        (ev / n / "after_run_check.json").write_text(json.dumps({"verdict": "PASS", "from": "an earlier run"}))
        (ev / n / "launch_record.json").write_text(json.dumps({"from": "an earlier run"}))
    getattr(RV, "LAUNCHED", set()).discard("a")
    getattr(RV, "LAUNCHED", set()).add("b")
    doc = RV.result_doc("9", pk, lst, ev, {"a": "baseline not RECORDED", "b": "PASS"}, "t0")
    assert doc["members"]["a"]["after_run_check"] is None and doc["members"]["a"]["launch_record"] is None, doc
    assert doc["members"]["b"]["after_run_check"]["verdict"] == "PASS"
    assert doc["verdict"] == "FAIL"


def test_c2e_relisted_from_is_accepted_only_with_current_results(tmp_path):
    """R2-T17 rest (DESIGN's `test_permitted_reuse_is_explicit`, third case): `--relisted-from` is accepted with
    current results (the existing drop-relist test) and refused when a result is no longer current: a later V3.6 run
    started for the same output and never finished."""
    CA = _load("batch2", "check_list_approvable")
    RBND = _load("batch2", "result_binding")
    OLD, L, V, V7 = (tmp_path / n for n in ("old.json", "l.json", "v.json", "v7.json"))
    old = {"prepared_at": "t0", "agets": [{"aget": "a", "ops": [W1]}, {"aget": "b", "ops": [W2]}]}
    OLD.write_text(json.dumps(old))
    osha = hashlib.sha256(OLD.read_bytes()).hexdigest()
    _produced(V, {"list_sha256": osha, "results": [{"aget": "a", "verdict": "PASS", "blind_spots": []},
                                                    {"aget": "b", "verdict": "FAIL"}]}, "rehearse_batch2")
    _produced(V7, {"verdict": "PASS", "list_sha256": osha, "members": {"a": {"verdict": "PASS"}}}, "rehearse_v37")
    new = {"prepared_at": "t1", "agets": [{"aget": "a", "ops": [W1]}, {"aget": "b", "ops": [W2], "blocked": "V3.6 FAIL"}]}
    L.write_text(json.dumps(new))
    def run():
        return CA.main(["--list", str(L), "--v36", str(V), "--v37", str(V7), "--relisted-from", str(OLD)])
    assert run() == 0                                                # control: current results
    RBND.start_run("rehearse_batch2", V)                             # a later V3.6 run started and never finished
    assert run() == 1


def test_d2_r3_the_launch_recomputes_the_session_rules_and_refuses_a_packet_that_differs():
    """D2 (R3, DESIGN: "launch_batch.py:44 recomputes allowlist(r) and write_set(r) from the items and refuses if
    they differ from the packet"): the launch used the packet's rules as written, so a hand-edited packet could
    widen the session. Control: rules exactly as preparation derives them pass."""
    LB, PL = _load("batch2", "launch_batch"), _load("batch2", "prepare_launch")
    r = {"aget": "a", "items": [{"path": "scripts/x.py", "op": "write"}]}
    r.update(allowlist=PL.allowlist(r, False), write_set=PL.write_set(r, False))
    assert LB.launch_rules_refusal(r, {"batch": "9"}) is None
    wider = {**r, "allowlist": r["allowlist"] + ["Edit(scripts/**)"]}
    assert "allowlist" in str(LB.launch_rules_refusal(wider, {"batch": "9"}))
    more = {**r, "write_set": r["write_set"] + ["scripts/other.py"]}
    assert "write set" in str(LB.launch_rules_refusal(more, {"batch": "9"}))
    assert "cannot be recomputed" in str(LB.launch_rules_refusal({**r, "items": [{"path": "x", "op": "??"}]}, {}))


# R55: the outcome test's producer/reader join and run-local cache defaults.
def r55_sop_packet(tmp_path, monkeypatch, packet_override=True):
    import os
    import subprocess
    import sys
    from test_migration_kit_rehearse_refusal import git_repo, MEMBER_FILES
    run = tmp_path / "run"
    batch = run / "B"
    batch.mkdir(parents=True)
    home = tmp_path / "home"
    home.mkdir()
    monkeypatch.setenv("HOME", str(home))
    monkeypatch.delenv("AGET_MIGRATION_PACKET_BASE", raising=False)
    monkeypatch.delenv("AGET_MIGRATION_WORK", raising=False)
    if packet_override:
        monkeypatch.setenv("AGET_MIGRATION_PACKET_BASE", str(run / "packets"))
    member = tmp_path / "member"
    g = git_repo(member, MEMBER_FILES)
    pl, lb = load("prepare_launch"), load("launch_batch")
    monkeypatch.setattr(pl.L, "members", lambda: [("r55-aget", str(member))])
    monkeypatch.setattr(pl.L, "usable_template", lambda *a: ("template-worker-aget", "test fixture"))
    monkeypatch.setattr(pl.L.W.V, "framework_root", lambda: str(tmp_path / "framework"))
    # Only payload discovery is stubbed. The B1 CLI builds prompts, rules, settings and sealed stage itself.
    monkeypatch.setattr(pl, "CORE_DOCS", [])
    monkeypatch.setattr(pl, "plan_receiver", lambda n, loc, **kw: {
        "aget": n, "location": loc, "template": "template-worker-aget", "head": g("rev-parse", "HEAD"),
        "items": [], "pins": {"core": "c" * 40, "template-worker-aget": "t" * 40}})
    monkeypatch.setattr(pl, "override_note", lambda *a: None)
    real_run = subprocess.run
    def command(cmd, *a, **kw):
        if cmd[:2] == ["claude", "--version"]:
            return subprocess.CompletedProcess(cmd, 0, "r55 stub CLI\n", "")
        return real_run(cmd, *a, **kw)
    monkeypatch.setattr(subprocess, "run", command)
    protected = batch / "PROTECTED_LIST.json"
    protected.write_text(json.dumps({"agets": [{"aget": "r55-aget", "ops": []}]}))
    packet = batch / "LAUNCH_PACKET.json"
    monkeypatch.setattr(sys, "argv", ["prepare_launch.py", "--batch", "55", "--protected-list", str(protected),
                                      "--placed-by-apply", "--out", str(packet), "r55-aget"])
    assert pl.main() == 0
    return pl, lb, packet, run


def test_r55_k4_sop_b1_output_is_accepted_by_b3_reader_and_baseline_but_migration_needs_receipt(
        tmp_path, monkeypatch, capsys):
    import sys
    from types import SimpleNamespace
    pl, lb, packet, _ = r55_sop_packet(tmp_path, monkeypatch)
    doc = json.loads(packet.read_text())
    assert doc["apply_receipt"] is None and doc["receivers"][0]["baseline_prompt"]
    assert lb.packet_refusal(doc, fields=False) is None  # the authority-independent structural control
    assert lb.main(["--packet", str(packet)]) == 0  # B3's actual reader, with B1's actual output
    assert "DRY RUN r55-aget" in capsys.readouterr().out
    monkeypatch.setitem(sys.modules, "batch_authority", SimpleNamespace(check=lambda *a, **kw: (True, "test")))
    monkeypatch.setattr(lb, "run_baseline", lambda r, *a, **kw: {
        "aget": r["aget"], "verdict": "RECORDED", "summary": "1 passed", "failures": []})
    args = ["--packet", str(packet), "--launch", "--evidence", str(tmp_path / "evidence")]
    assert lb.main(args + ["--baseline"]) == 0  # B6: no apply has happened yet
    assert lb.main(args) == 2  # B8: the null field must never authorize a migration
    assert "a migration launch needs `apply_receipt`" in capsys.readouterr().out
    monkeypatch.setattr(lb, "take_snapshot", lambda *a: None)
    monkeypatch.setattr(lb, "run_one", lambda r, *a, **kw: {
        "aget": r["aget"], "exit": 0, "elapsed_s": 0, "head_before": r["head"], "head_after": r["head"],
        "check_exit": 0})
    assert lb.main(args + ["--apply-receipt", str(tmp_path / "applied.json")]) == 0
    # B3 uses that same untouched B1 packet on a real isolated copy, with the rehearsal tool's marker.
    import subprocess
    copy = tmp_path / "copy-run" / "member"
    subprocess.run(["git", "clone", "--no-hardlinks", doc["receivers"][0]["location"], str(copy)],
                   check=True, capture_output=True)
    assert lb.CI.isolate(copy, "remove", member=True, run=copy) is None
    load("rehearse_v37").write_copy_marker(copy, hashlib.sha256(packet.read_bytes()).hexdigest(), "r55-aget")
    copy_args = args + ["--copy-root", str(copy)]
    assert lb.main(copy_args + ["--baseline"]) == 0
    assert lb.main(copy_args + ["--apply-receipt", str(tmp_path / "copy-applied.json")]) == 0
    assert lb.packet_refusal({**doc, "apply_receipt": 55}) is not None  # still reject malformed fields


def test_r55_p5_default_packet_and_confirmation_paths_stay_beside_sop_batch_outputs(tmp_path, monkeypatch):
    import subprocess
    from types import SimpleNamespace
    pl, lb, packet, run = r55_sop_packet(tmp_path, monkeypatch, packet_override=False)
    doc = json.loads(packet.read_text())
    assert pl.CI.work_refusal(Path(doc["packet_root"])) is None  # existing outside-repository condition
    doc.update(_path=str(packet), apply_receipt=str(run / "applied.json"))
    checks = []
    real_run = subprocess.run
    def command(cmd, *a, **kw):
        if str(lb.CHECK) in [str(x) for x in cmd]:
            checks.append(cmd)
            return subprocess.CompletedProcess(cmd, 0, "stub check", "")
        return real_run(cmd, *a, **kw)
    monkeypatch.setattr(subprocess, "run", command)
    real_popen = subprocess.Popen
    def popen(cmd, *a, **kw):
        if str(lb.WATCHER) in [str(x) for x in cmd]:
            return SimpleNamespace()
        return real_popen(cmd, *a, **kw)
    monkeypatch.setattr(subprocess, "Popen", popen)
    monkeypatch.setattr(lb, "stop_watcher", lambda *a: None)
    monkeypatch.setattr(lb.time, "sleep", lambda *a: None)
    monkeypatch.setattr(lb, "seal_baseline_slot", lambda *a: None)
    monkeypatch.setattr(lb, "run_grouped", lambda *a: subprocess.CompletedProcess([], 0, "", ""))
    lb.run_one(doc["receivers"][0], doc, run / "evidence")
    check = next(c for c in checks if "--confirm-dir" in c)
    # R62 F-5: B1's prompts and the B8 checker declare the same cache-free default.
    default = "python3 -m pytest -q -p no:cacheprovider"
    receiver = doc["receivers"][0]
    assert check[check.index("--suite-cmd") + 1] == default
    assert f"2. Run: {default}" in pl.prompt(R, "r62-default", [])
    assert f"5. Validate. Run: {default}" in receiver["prompt"]
    assert "-p no:cacheprovider" in receiver["baseline_prompt"]
    confirm = Path(check[check.index("--confirm-dir") + 1])
    paths = {"packet": doc["packet_root"], "confirmation": str(confirm)}
    assert all(Path(p).is_relative_to(run) for p in paths.values()), paths
    assert lb.CI.work_refusal(confirm) is None
    assert not list((tmp_path / "home").rglob("aget-migration-kit")), "defaults must not write in HOME"
    # Explicit overrides remain usable; the confirmation command must actually carry the override.
    override = tmp_path / "explicit-work"
    monkeypatch.setenv("AGET_MIGRATION_WORK", str(override))
    assert load("launch_batch").WORK_ROOT == override
    monkeypatch.setattr(lb, "WORK_ROOT", override)
    checks.clear()
    lb.run_one(doc["receivers"][0], doc, run / "override-evidence")
    check = next(c for c in checks if "--confirm-dir" in c)
    assert check[check.index("--confirm-dir") + 1] == str(override)
    receiver["suite_cmd"] = "python3 /fixture/run_suite_parallel.py"
    receiver["allowlist"] = pl.allowlist(receiver)
    checks.clear()
    lb.run_one(receiver, doc, run / "explicit-suite-evidence")
    check = next(c for c in checks if "--confirm-dir" in c)
    assert check[check.index("--suite-cmd") + 1] == receiver["suite_cmd"]
    monkeypatch.setenv("AGET_MIGRATION_PACKET_BASE", str(tmp_path / "explicit-packets"))
    assert load("prepare_launch").PACKET_BASE == tmp_path / "explicit-packets"


def test_r62_repair_prompt_uses_the_declared_cache_free_default_or_explicit_override():
    default = "python3 -m pytest -q -p no:cacheprovider"
    assert f"3. Run: {default}" in PL.repair_prompt(R, "r62-repair", "prior")
    override = "python3 /fixture/run_suite_parallel.py"
    assert f"3. Run: {override}" in PL.repair_prompt(dict(R, suite_cmd=override), "r62-repair", "prior")
