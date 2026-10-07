"""Tests for the route (ii) after-run detective check (batch1/after_run_check.py). Hermetic fixtures only."""
import hashlib
import importlib.util
import json
import os
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "after_run_check", ROOT / "scripts/migration_kit/after_run_check.py")
C = importlib.util.module_from_spec(spec)
spec.loader.exec_module(C)

SKILL = ".claude/skills/aget-x/SKILL.md"


def sha(text):
    return hashlib.sha256(text.encode()).hexdigest()


def tool_use(i, name, inp):
    return {"type": "assistant", "sessionId": "S", "message": {"content": [{"type": "tool_use", "id": i, "name": name, "input": inp}]}}


DENIED = "Permission to use Write has been denied because Claude Code is running in don't ask mode."


def tool_result(i, ok=True, content=None):
    block = {"type": "tool_result", "tool_use_id": i, "is_error": not ok}
    if content is not None:
        block["content"] = content
    return {"type": "user", "sessionId": "S", "permissionMode": "dontAsk", "message": {"content": [block]}}


def produce(path, step, doc):
    """Write `doc` at `path` as its producer now does (R2-T16 (c), R2-T17): a run recorded first, then the result bound
    to it (result_binding.write_result). A record written by hand names no run and is not read."""
    RB = C.RBND
    doc = {k: v for k, v in doc.items() if k != "binding"}
    rid = RB.start_run(step, path, aget=doc.get("aget"), recorded_by="invoker")
    RB.write_result(step, path, doc, rid, binding={"aget": doc.get("aget"), "subject": doc.get("head")})


def stamp(epoch):
    """An ISO timestamp as a transcript entry carries one."""
    import datetime
    return datetime.datetime.fromtimestamp(epoch, datetime.timezone.utc).isoformat().replace("+00:00", "Z")


RECEIPT_AT = {"attempt": "att-1", "receipt_path": "scripts/RECEIPT.md"}
RECEIPT_TEXT = "# Receipt\n\n## Attempt att-1\n\nall steps done\n\nTerminal: ACCEPTED\n"


@pytest.fixture
def run(tmp_path, monkeypatch):
    home = tmp_path / "home"
    (home / ".claude").mkdir(parents=True)
    monkeypatch.setenv("HOME", str(home))
    root = tmp_path / "aget"
    (root / ".claude" / "skills" / "aget-x").mkdir(parents=True)
    (root / SKILL).write_text("release\n")
    (root / ".claude" / "settings.local.json").write_text(json.dumps({"permissions": {"allow": ["Bash(git status)"]}}))
    (root / "notes.txt").write_text("pre-existing\n")
    (root / ".gitignore").write_text(".claude/hooks/\n")  # as at one receiver: hooks are git-ignored
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "base"],
                   check=True)
    (root / "notes.txt").write_text("pre-existing, modified before the launch\n")  # pre-dirty work
    packet = tmp_path / "packet.json"
    # R2 (kit design pass): the packet names the attempt, and the receipt (here under scripts/, inside the write
    # set) is committed with an authoritative section for it, which after-run check H reads at HEAD.
    packet.write_text(json.dumps({"receivers": [{"aget": "a", **RECEIPT_AT, "items": [
        {"path": "scripts/x.py", "op": "write", "sha256": sha("release x\n")},
        {"path": "scripts/m.py", "op": "hold", "kind": "no-source", "pre": "absent"}]}]}))   # R3: a KEEP item
    receipt = tmp_path / "receipt.json"
    produce(receipt, "apply_protected", {"mode": "apply", "agets": [{"aget": "a", "result": "APPLIED",   # R2-T6, T17
                                         "location": str(root), # C2d (labelled): the entry names its location (pre-read 1)
                                         "files": [{"path": SKILL, "post": sha("release\n"), "ok": True}]}]})
    snap = tmp_path / "snap.json"
    C.main(["--aget", "a", "--root", str(root), "--snapshot", str(snap)])
    watch = tmp_path / "watch.jsonl"
    watch.write_text("\n".join(json.dumps(e) for e in [
        {"event": "start", "t": 100.0, "heartbeat": 5, "interval": 0.5, "files": {}, "stat_tracked": True},
        {"event": "heartbeat", "t": 104.0}, {"event": "stop", "t": 108.0}]) + "\n")
    transcript = tmp_path / "t.jsonl"
    suite_report, suite_token, suite_texts = _kit_report().reported(tmp_path / "suite_report.jsonl",
                                                                    [("1 passed in 0.01s", [])])
    events = [tool_use("1", "Bash", {"command": "git status"}), tool_result("1"),
              tool_use("2", "Bash", {"command": "ls scripts"}), tool_result("2"),
              tool_use("3", "Write", {"file_path": str(root / "scripts" / "x.py")}), tool_result("3"),
              tool_use("4", "Bash", {"command": "git commit -m m"}), tool_result("4"),
              # R2-T11: a migration session runs its declared suite; F compares it with its bound baseline
              # C2a7 (changed, labelled): the run carries its kit report, as the plugin writes it
              tool_use("5", "Bash", {"command": "python3 -m pytest -q"}),
              tool_result("5", content=suite_texts[0])]
    for n, e in enumerate(events):              # R2-T11: the session's window, as a Claude Code transcript stamps it
        e["timestamp"] = stamp(101 + 6 * n / (len(events) - 1))
    transcript.write_text("\n".join(json.dumps(e) for e in events) + "\n")
    baseline = tmp_path / "fixture_baseline_record.json"
    produce(baseline, "baseline", {"aget": "a", "head": subprocess.run(
        ["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip(),
        "verdict": "RECORDED", "output_complete": True, "failures": [],
        "selection": _kit_report().SELECTION})        # C2c (labelled): the baseline's witness (no witness, no policy)
    (root / "scripts").mkdir()
    (root / "scripts" / "x.py").write_text("release x\n")  # the receiver's copy of the staged bytes, committed
    (root / RECEIPT_AT["receipt_path"]).write_text(RECEIPT_TEXT)
    subprocess.run(["git", "-C", str(root), "add", "scripts/x.py", RECEIPT_AT["receipt_path"]], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "mig"],
                   check=True)

    def go(extra_events=None, **over):
        if extra_events:
            with transcript.open("a") as fh:
                fh.write("\n".join(json.dumps(e) for e in extra_events) + "\n")
        args = ["--aget", "a", "--root", str(root), "--receipt", str(receipt), "--snapshot-file", str(snap),
                "--watch-log", str(over.get("watch", watch)), "--transcript", str(transcript), "--packet", str(packet),
                "--write-set", "scripts/*", "--allow-bash", "git status", "git commit", "python3 -m pytest", "--json", str(tmp_path / "o.json"),
                # R2-T11: F's inputs for a migration session (the window the watch must cover comes from the
                # transcript's timestamps, 101-107, inside the watch's 100-108)
                "--suite-cmd", "python3 -m pytest -q", "--baseline-record", str(baseline),
                "--suite-report", str(suite_report), "--suite-report-token", suite_token]
        for k in over.get("drop", ()):              # R2-T11 falsifiers: an input left out
            i = args.index(k)
            del args[i:i + 2]
        if over.get("allow_exact"):
            args += ["--allow-exact", *over["allow_exact"]]
        args += over.get("extra_args", [])
        if over.get("route"):
            args += ["--route", over["route"]]
        if over.get("settings"):
            args += ["--settings-file", str(over["settings"][0]), "--settings-sha256", over["settings"][1]]
        if over.get("packet_items"):
            packet.write_text(json.dumps({"receivers": [{"aget": "a", **RECEIPT_AT, "items": over["packet_items"]}]}))
        code = C.main(args)
        return code, json.loads((tmp_path / "o.json").read_text())
    return go, root, tmp_path


def resnapshot_baseline(tmp_path, root):
    """A test that re-takes the pre-launch snapshot after the fixture's commit: the fixture's baseline names the HEAD
    that snapshot records (R2-T11 binds the baseline to the HEAD the session started from)."""
    f = tmp_path / "fixture_baseline_record.json"
    doc = json.loads(f.read_text())
    doc["head"] = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True,
                                 text=True).stdout.strip()
    produce(f, "baseline", doc)


def test_clean_run_passes_and_lists_the_read_only_allowance(run):
    go, _, _ = run
    code, out = go()
    assert (code, out["verdict"]) == (0, "PASS")
    assert out["read_only_allowance_used"] == ["ls scripts"]


@pytest.mark.parametrize("changed", ["neither", "working-only", "head-only"])
def test_round2_after_run_checks_release_mode_in_tree_and_commit(run, changed):
    """M-6: identical release bytes do not pass D when either the working or committed executable bit differs."""
    go, root, _ = run
    path = root / "scripts/x.py"
    if changed == "working-only":
        path.chmod(0o755)
    elif changed == "head-only":
        subprocess.run(["git", "-C", str(root), "update-index", "--chmod=+x", "scripts/x.py"], check=True)
        subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "mode"], check=True)
    code, out = go(packet_items=[{"path": "scripts/x.py", "op": "write", "sha256": sha("release x\n"),
                                 "release_mode": 0o644}])
    if changed == "neither":
        assert not out["D"] and code == 0
    else:
        assert any("executable bit" in text for text in out["D"]) and code == 1


@pytest.mark.parametrize("release_mode", [0o644, 0o755])
@pytest.mark.parametrize("tracked,drift", [
    (False, "none"), (False, "working"), (True, "none"),
    (True, "working"), (True, "head"), (True, "index-only"),
])
def test_round2b_native_protected_mode_receipt_observes_tracking(run, monkeypatch, release_mode, tracked, drift):
    """B235: native mode-only apply of ignored protected bytes passes A; wrong required modes still fail."""
    spec = importlib.util.spec_from_file_location(
        "protected_mode_fixture", Path(__file__).with_name("test_migration_kit_batch_protected.py"))
    t = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(t)
    go, member, tmp = run
    fw = tmp / "fw"
    tpl = fw / "template-x-aget"
    tpl.mkdir(parents=True)
    t.sh(tpl, "init", "-q")
    t.commit(tpl, {SKILL: "release\n"}, "v3.34.0")
    # A distinct from/to tag pair lets native preparation observe the target mode.
    wrong = 0o755 if release_mode == 0o644 else 0o644
    (tpl / SKILL).chmod(wrong)
    t.sh(tpl, "add", SKILL)
    if wrong == 0o755:
        t.sh(tpl, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "from mode")
    t.sh(tpl, "tag", "-f", "v3.34.0")
    (tpl / SKILL).chmod(release_mode)
    t.sh(tpl, "add", SKILL)
    t.sh(tpl, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "target mode")
    t.sh(tpl, "tag", "v3.35.0")
    (member / ".aget").mkdir()
    (member / ".aget/version.json").write_text(json.dumps({"template": "x"}))
    (member / ".gitignore").write_text(".claude/\n")
    if not tracked or drift == "index-only":
        t.sh(member, "rm", "--cached", SKILL)
    t.sh(member, "add", ".aget/version.json", ".gitignore")
    t.sh(member, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "fixture tracking")
    (member / SKILL).chmod(wrong)
    monkeypatch.setenv("AGET_FRAMEWORK_ROOT", str(fw))
    monkeypatch.setattr(t.P.L.W, "SPEC_PATHS", [])
    monkeypatch.setattr(t.P.L.W, "CORRECTION_ROW_4", [])
    t.P.UPSTREAM.clear()
    monkeypatch.setattr(t.A, "REGISTER", t.register(tmp, {"a": member}))
    entry = t.P.prepare("a", str(member))
    operation = next(o for o in entry["ops"] if o["path"] == SKILL)
    assert operation["op"] == "write" and operation["release_mode"] == release_mode
    packet = tmp / "protected.json"
    packet.write_text(json.dumps({"batch": "t", "apply_script_sha256": t.A.self_sha(), "agets": [entry]}))
    assert t.A.main(["--list", str(packet), "--apply", "--receipt-dir", str(tmp)]) == 0
    receipt = next(tmp.glob("APPLY_RECEIPT*.json"))
    assert (member / SKILL).stat().st_mode & 0o100 == (0o100 if release_mode == 0o755 else 0)
    if tracked:
        t.sh(member, "add", "-f", SKILL)
        if drift != "index-only":
            t.sh(member, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "--allow-empty", "-qm", "applied mode")
    if drift == "working":
        (member / SKILL).chmod(wrong)
    elif drift == "head":
        t.sh(member, "update-index", "--chmod=+x" if wrong == 0o755 else "--chmod=-x", SKILL)
        t.sh(member, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "HEAD mode drift")
    assert C.CI.git_tracked(member, SKILL) == tracked
    assert C.main(["--aget", "a", "--root", str(member), "--snapshot", str(tmp / "snap.json")]) == 0
    resnapshot_baseline(tmp, member)
    code, out = go(extra_args=["--receipt", str(receipt)])
    assert not out["inconclusive"]
    if drift == "none":
        assert (code, out["verdict"]) == (0, "PASS"), out
        assert not out["A"]
    else:
        assert code == 1 and any("executable bit" in x for x in out["A"]), out


@pytest.mark.parametrize("reader", ["git_blob_at", "git_tracked"])
def test_round2b_protected_mode_unavailable_required_git_read_is_inconclusive(run, monkeypatch, reader):
    """An unavailable HEAD/tracking read cannot grant the protected untracked exception."""
    _, root, _ = run
    def unavailable(*args, **kwargs):
        raise C.CI.InspectionFailed("required Git reading unavailable")
    monkeypatch.setattr(C.CI, reader, unavailable)
    out = {"A": [], "inconclusive": []}
    C.judge_release_mode(root, {"path": SKILL, "release_mode": 0o644}, "A", out)
    assert not out["A"] and out["inconclusive"] == ["A: required Git reading unavailable"]


def test_a_protected_file_changed_after_the_apply_fails_A(run):
    go, root, _ = run
    (root / SKILL).write_text("edited by the receiver\n")
    code, out = go()
    assert code == 1 and out["A"]


def test_a_settings_rule_added_fails_B(run):
    go, root, _ = run
    (root / ".claude" / "settings.local.json").write_text(
        json.dumps({"permissions": {"allow": ["Bash(git status)", "Bash(rm:*)"]}}))
    code, out = go()
    assert code == 1 and any("rule set changed" in x for x in out["B"])


def test_a_turn_in_another_mode_fails_B(run):
    go, _, _ = run
    code, out = go([{"type": "user", "permissionMode": "bypassPermissions"}])
    assert code == 1 and any("permission modes" in x for x in out["B"])


def test_a_write_to_a_protected_path_fails_C(run):
    go, root, _ = run
    code, out = go([tool_use("9", "Edit", {"file_path": str(root / "AGENTS.md")}), tool_result("9")])
    assert code == 1 and any("protected" in x for x in out["C"])


def test_a_write_outside_the_write_set_fails_C(run):
    go, root, _ = run
    code, out = go([tool_use("9", "Write", {"file_path": str(root / "docs" / "x.md")}), tool_result("9")])
    assert code == 1 and any("outside the declared write set" in x for x in out["C"])


def test_an_executed_write_form_bash_outside_the_allowed_prefixes_fails_C(run):
    go, _, _ = run
    code, out = go([tool_use("9", "Bash", {"command": "echo x > notes.txt"}), tool_result("9")])
    assert code == 1 and any("not allowed and not read-only" in x for x in out["C"])


def test_a_refused_call_is_not_counted_as_done(run):
    go, root, _ = run
    code, out = go([tool_use("9", "Write", {"file_path": str(root / ".claude" / "x")}),
                    tool_result("9", ok=False, content=DENIED)])
    assert code == 0 and out["verdict"] == "PASS"


def test_an_error_that_is_not_a_denial_counts_as_executed(run):
    go, root, _ = run
    code, out = go([tool_use("9", "Bash", {"command": "touch x"}), tool_result("9", ok=False, content="exit 1")])
    assert code == 1 and out["C"]


@pytest.mark.parametrize("cmd", [
    "git add . && rm -rf ~/x", "git commit -m m; curl -X POST u", "echo x >f", "echo x>f", "`rm f`",
    "/usr/bin/python3 -c x", "python3.12 -c x", "uv run x", "find . -name x -delete", "rsync a b", "open -a X",
    "gh api -X POST repos/x", "gh pr create", "cat f | tee g", "git push", "git config user.name x",
    "echo $(rm f)", "ls\nrm f",
    # round 2 (framework lane, after fb6927b4): an allowlisted first word with a writing or executing option
    "git diff --output=/tmp/x", "git log --output=AGENTS.md", "git show --output AGENTS.md", "git blame -o x",
    "sort -o AGENTS.md in", "uniq in AGENTS.md", "rg --pre=sh x .", "rg --pre sh x .", "tree -o out",
    "find . -fprint=x", "find . -fprint x", "find . -exec=x", "git diff --ext-diff", "git -c core.pager=x log",
    "file -C -m m", "date -s now", "git ls-remote --upload-pack=x origin", "git ls-remote -u x origin"])
def test_write_or_execute_forms_fail(run, cmd):
    go, _, _ = run
    code, out = go([tool_use("9", "Bash", {"command": cmd}), tool_result("9")])
    assert code == 1, cmd


@pytest.mark.parametrize("cmd", ["cat f", "git diff", "ls", "git log --oneline -3", "cat f | grep x | wc -l",
                                 "find . -name x"])
def test_read_only_forms_pass_and_are_listed(run, cmd):
    go, _, _ = run
    code, out = go([tool_use("9", "Bash", {"command": cmd}), tool_result("9")])
    assert code == 0 and cmd in out["read_only_allowance_used"]


def test_an_allowed_prefix_counts_only_without_chaining(run):
    go, _, _ = run
    assert go([tool_use("9", "Bash", {"command": "git commit -m done"}), tool_result("9")])[0] == 0
    assert go([tool_use("8", "Bash", {"command": "git commit -m done && git push"}), tool_result("8")])[0] == 1


def test_an_uninspected_tool_is_inconclusive(run):
    go, _, _ = run
    code, out = go([tool_use("9", "Agent", {"prompt": "x"}), tool_result("9")])
    assert code == 3 and any("not inspected" in x for x in out["inconclusive"])


def test_an_unstopped_watch_is_inconclusive(run, tmp_path):
    go, _, _ = run
    w2 = tmp_path / "w2.jsonl"
    w2.write_text(json.dumps({"event": "start", "t": 1.0, "heartbeat": 5, "interval": 0.5, "files": {},
                              "stat_tracked": True}) + "\n")
    code, out = go(watch=w2)
    assert code == 3 and out["verdict"] == "INCONCLUSIVE"


def test_a_copied_file_that_is_not_the_release_bytes_fails_D(run):
    go, root, _ = run
    (root / "scripts" / "x.py").write_text("release x")  # the trailing newline lost in re-typing
    code, out = go()
    assert code == 1 and out["D"]


def test_a_copied_file_left_out_of_the_commit_fails_D(run):
    go, root, _ = run
    subprocess.run(["git", "-C", str(root), "rm", "-q", "--cached", "scripts/x.py"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "x"],
                   check=True)
    code, out = go()
    assert code == 1 and any("not in HEAD" in x for x in out["D"])


def test_an_ignored_hook_changed_during_the_run_fails_E(run):
    go, root, tmp_path = run
    # created after the snapshot, under .claude/: an instruction file git may not show at all
    (root / ".claude" / "hooks").mkdir()
    (root / ".claude" / "hooks" / "pre.sh").write_text("echo injected\n")
    assert subprocess.run(["git", "-C", str(root), "check-ignore", "-q", ".claude/hooks/pre.sh"]).returncode == 0
    code, out = go()
    assert code == 1
    assert [x for x in out["E"] if x.startswith(".claude/hooks/pre.sh: .claude/ file changed")]
    assert not [x for x in out["E"] if x.startswith(".claude/hooks/pre.sh: changed by the run")]  # git cannot see it


def test_a_merge_item_is_judged_by_its_authored_lines_and_listed(run):
    """R3 (kit design pass; was "reported, not judged"): a hold/authored item is listed for review AND judged: every
    authored line's identity must survive in the working tree and at HEAD. The control keeps the line; the second
    case names a line the file does not hold."""
    go, _, _ = run
    keep = hashlib.sha256(b"release x").hexdigest()
    item = {"path": "scripts/x.py", "op": "hold", "kind": "authored", "authored_lines": 1, "staged": "s",
            "authored_ids": [keep]}
    code, out = go(packet_items=[item])
    assert code == 0 and out["merged"] and out["merged"][0].startswith("scripts/x.py")
    code, out = go(packet_items=[{**item, "authored_ids": [keep, hashlib.sha256(b"gone").hexdigest()]}])
    assert code == 1 and any("your own line(s) are gone" in x for x in out["D"])


def test_a_file_changed_outside_the_write_set_fails_E(run):
    go, root, _ = run
    (root / "governance.md").write_text("a row a test fabricated\n")  # a side effect no tool call shows
    code, out = go()
    assert code == 1 and any("governance.md" in x for x in out["E"])


def test_a_pre_existing_modified_file_changed_during_the_run_fails_E(run):
    go, root, _ = run
    (root / "notes.txt").write_text("touched during the run\n")
    code, out = go()
    assert code == 1 and any("notes.txt" in x for x in out["E"])


SUITE = "python3 run_suite.py --deselect-file tests/ci_known_failures.txt"


def _kit_report():
    import importlib.util
    spec = importlib.util.spec_from_file_location("_kit_report", Path(__file__).parent / "_kit_report.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _suite_transcript(tmp_path, outputs):
    """A transcript whose Bash calls ran SUITE once per output (the last is the after-run result)."""
    rows = []
    for i, text in enumerate(outputs):
        rows.append({"sessionId": "S", "message": {"content": [{"type": "tool_use", "id": f"s{i}", "name": "Bash",
                                              "input": {"command": SUITE, "timeout": 600000}}]}})
        rows.append({"sessionId": "S", "message": {"content": [{"type": "tool_result", "tool_use_id": f"s{i}", "is_error": True,
                                              "content": text}]}})
    t = tmp_path / "suite_t.jsonl"
    t.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    return t


def test_F_a_new_failure_in_the_sessions_own_suite_run_fails(tmp_path):
    """G3.6 row 12 B1 (batch 8): the receipt listed both new failures and still read ACCEPTED; F reads the suite
    command's own output in the transcript against the B6 baseline record."""
    base = tmp_path / "baseline_record.json"
    # C2b (R2-T11, changed, labelled): the baseline is bound to member "a" and HEAD "h"; C2c (R2-T17): and is the
    # current run of the baseline
    produce(base, "baseline", {"aget": "a", "head": "h", "output_complete": True, "verdict": "RECORDED",
                               "selection": _kit_report().SELECTION,   # C2c (labelled): the witness
                               "failures": ["tests/test_old.py::t"]})
    # B180 finding 1 (changed, labelled): the outputs are pytest's own form, a short summary section and a count line
    before = "=== short test summary info ===\nFAILED tests/test_old.py::t\n1 failed, 10 passed in 0.1s"
    after = ("=== short test summary info ===\nFAILED tests/test_old.py::t\n"
             "FAILED tests/test_identifier_injectivity.py::test_competing - 269 > 129\n2 failed, 9 passed in 0.1s")
    # C2a7 (B185 finding 1, changed, labelled): each run carries its kit report; F reads the ids from the report
    fb, fa = ["tests/test_old.py::t"], ["tests/test_old.py::t", "tests/test_identifier_injectivity.py::test_competing"]
    rpt, tok, (tb, ta) = _kit_report().reported(tmp_path / "r1.jsonl", [(before, fb), (after, fa)])
    new, why = C.suite_regressions(_suite_transcript(tmp_path, [tb, ta]), SUITE, base, "a", "h",
                                   report=rpt, token=tok)
    assert why is None and new == ["tests/test_identifier_injectivity.py::test_competing"]
    new, why = C.suite_regressions(_suite_transcript(tmp_path, [ta, tb]), SUITE, base, "a", "h",
                                   report=rpt, token=tok)
    assert why is None and new == []                              # the LAST run decides
    new, why = C.suite_regressions(_suite_transcript(tmp_path, [before, after]), SUITE, base, "a", "h",
                                   report=rpt, token=tok)
    assert new == [] and why                                      # the output names no invocation: not known


@pytest.mark.parametrize("outputs,base_ok", [
    ([], True),                                                   # the suite was never run
    (["Output too large (32KB). Full output saved to: /x"], True),   # truncated
    (["Command running in background with ID: b1"], True),      # backgrounded, then killed at exit
    (["FAILED tests/a.py::t"], True),                             # no completion summary
    (["1 failed, 9 passed\nFAILED tests/a.py::t"], False)])       # baseline record unreadable
def test_F_is_inconclusive_never_pass_when_the_run_cannot_be_read(tmp_path, outputs, base_ok):
    base = tmp_path / "baseline_record.json"
    if base_ok:
        produce(base, "baseline", {"aget": "a", "head": "h", "output_complete": True, "verdict": "RECORDED",
                               "selection": _kit_report().SELECTION,   # C2c (labelled): the witness
                               "failures": []})
    new, why = C.suite_regressions(_suite_transcript(tmp_path, outputs), SUITE, base, "a", "h")
    assert new == [] and why


def test_F_confirms_candidates_at_the_committed_revision_in_a_clean_clone(tmp_path):
    """The framework Aget's review (2026-09-29): sessions test before they commit, so a clean-tree test fails in the
    session's run and passes at the commit. F re-runs candidates at the named revision in a clone: a real regression
    stays F, a before-commit artefact is recorded; the receiver's folder is not touched."""
    root = tmp_path / "home" / "seat"
    (root / "tests").mkdir(parents=True)
    (root / "tests" / "test_x.py").write_text(
        "import os\n\ndef test_clean_tree():\n    assert not os.path.exists('uncommitted.txt')\n\n"
        "def test_real():\n    assert False\n")
    def g(*a):
        return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                              check=True, capture_output=True, text=True).stdout.strip()
    g("init", "-q")
    g("add", "-A")
    g("commit", "-q", "-m", "c")
    (root / "uncommitted.txt").write_text("dirt\n")                 # present in the receiver, absent in a clone
    ids = ["tests/test_x.py::test_clean_tree", "tests/test_x.py::test_real"]
    still, passed, why = C.confirm_at_head(root, "seat", ids, [], tmp_path / "work", g("rev-parse", "HEAD"))
    assert why is None and still == ["tests/test_x.py::test_real"] and passed == ["tests/test_x.py::test_clean_tree"]
    assert (root / "uncommitted.txt").exists() and g("status", "--porcelain") == "?? uncommitted.txt"
    still, passed, why = C.confirm_at_head(root, "seat", ids, [], tmp_path / "work", "no-such-rev")
    assert why and still == [] and passed == []                    # unconfirmable: the caller keeps them as F


def _confirm_repo(tmp_path, tests):
    """A committed receiver at tmp_path/home/seat holding tests/test_x.py; returns (root, git runner)."""
    root = tmp_path / "home" / "seat"
    (root / "tests").mkdir(parents=True)
    (root / "tests" / "test_x.py").write_text(tests)
    def g(*a):
        return subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                              check=True, capture_output=True, text=True).stdout.strip()
    g("init", "-q")
    g("add", "-A")
    g("commit", "-q", "-m", "c")
    return root, g


def test_a_confirmation_run_that_pushes_cannot_reach_the_receiver(tmp_path):
    """Review finding F-5 (2026-10-01): the confirmation clone's origin is the receiver's live folder, so a test that
    commits and pushes an explicit refspec created a ref there. The clone's push URL is disabled before any test
    runs, so the push fails in the clone and the receiver keeps its refs, HEAD and status."""
    root, g = _confirm_repo(tmp_path, (
        "import subprocess\n\ndef test_pushes():\n"
        "    subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q',\n"
        "                    '--allow-empty', '-m', 'rogue'])\n"
        "    assert subprocess.run(['git', 'push', '-q', 'origin', 'HEAD:refs/heads/rogue']).returncode != 0\n"))
    head, status, refs = g("rev-parse", "HEAD"), g("status", "--porcelain"), g("for-each-ref")
    ids = ["tests/test_x.py::test_pushes"]
    still, passed, why = C.confirm_at_head(root, "seat", ids, [], tmp_path / "work", head)
    assert why is None and still == [] and passed == ids           # the push was refused in the clone
    assert g("branch", "--list", "rogue") == "" and g("for-each-ref") == refs
    assert g("rev-parse", "HEAD") == head and g("status", "--porcelain") == status
    clone, = (tmp_path / "work").glob("*/seat.root/seat")   # E2g: the clone sits in this run's own folder
    assert subprocess.run(["git", "-C", str(clone), "remote", "get-url", "--push", "origin"],
                          capture_output=True, text=True).stdout.strip() == C.NO_PUSH_URL


def test_a_copied_sibling_repository_has_its_push_route_closed_and_the_live_sibling_is_unchanged(tmp_path):
    root, g = _confirm_repo(tmp_path, "def test_a():\n    assert True\n")
    sib = tmp_path / "home" / "sib"
    sib.mkdir()
    (sib / "f.txt").write_text("x\n")
    for a in (["init", "-q"], ["add", "-A"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c"],
              ["remote", "add", "origin", "https://example.invalid/sib.git"]):
        subprocess.run(["git", "-C", str(sib), *a], check=True, capture_output=True, text=True)
    live_config = (sib / ".git" / "config").read_text()
    ids = ["tests/test_x.py::test_a"]
    still, passed, why = C.confirm_at_head(root, "seat", ids, ["../sib"], tmp_path / "work", g("rev-parse", "HEAD"))
    assert why is None and still == [] and passed == ids
    copy, = (tmp_path / "work").glob("*/seat.root/sib")   # E2g: the clone sits in this run's own folder
    assert subprocess.run(["git", "-C", str(copy), "remote", "get-url", "--push", "origin"],
                          capture_output=True, text=True).stdout.strip() == C.NO_PUSH_URL
    assert (sib / ".git" / "config").read_text() == live_config and C.NO_PUSH_URL not in live_config


def test_a_sibling_whose_git_entry_is_not_a_directory_is_not_confirmed(tmp_path):
    """A linked worktree's or submodule's .git is a file naming a git folder outside the copy: setting a push URL
    through it would write the live repository's configuration, so the run is refused instead."""
    root, g = _confirm_repo(tmp_path, "def test_a():\n    assert True\n")
    sib = tmp_path / "home" / "sib"
    sib.mkdir()
    (sib / ".git").write_text("gitdir: /nonexistent/elsewhere\n")
    still, passed, why = C.confirm_at_head(root, "seat", ["tests/test_x.py::test_a"], ["../sib"], tmp_path / "work",
                                           g("rev-parse", "HEAD"))
    assert still == [] and passed == [] and "'../sib'" in why and "not a directory" in why


def test_the_confirmation_run_clones_nothing_while_the_environment_redirects_git(tmp_path, monkeypatch):
    """The same guard as the suite check: asked before the clone, so before the clone's first checkout."""
    root, g = _confirm_repo(tmp_path, "def test_a():\n    assert True\n")
    index = (root / ".git" / "index").read_bytes()
    monkeypatch.setenv("GIT_INDEX_FILE", str(root / ".git" / "index"))
    head = subprocess.run(["git", "--git-dir", str(root / ".git"), "rev-parse", "HEAD"], capture_output=True,
                          text=True).stdout.strip()
    still, passed, why = C.confirm_at_head(root, "seat", ["tests/test_x.py::test_a"], [], tmp_path / "work", head)
    assert still == [] and passed == [] and "GIT_INDEX_FILE" in why and not (tmp_path / "work").exists()
    assert (root / ".git" / "index").read_bytes() == index


def test_a_sibling_copy_whose_git_acts_on_the_live_sibling_is_not_confirmed(tmp_path):
    """The isolation every copy the kit makes goes through: a sibling whose config names its own live folder as
    core.worktree has a .git directory, so the push URL could be set, and its git commands would still act on the
    live sibling. Refused before any test runs."""
    root, g = _confirm_repo(tmp_path, "def test_a():\n    assert True\n")
    sib = tmp_path / "home" / "sib"
    sib.mkdir()
    subprocess.run(["git", "init", "-q", str(sib)], check=True)
    subprocess.run(["git", "-C", str(sib), "config", "core.worktree", str(sib.resolve())], check=True)
    still, passed, why = C.confirm_at_head(root, "seat", ["tests/test_x.py::test_a"], ["../sib"], tmp_path / "work",
                                           g("rev-parse", "HEAD"))
    assert still == [] and passed == [] and "'../sib'" in why and "acts on the working tree" in why


def test_a_sibling_copy_whose_git_folder_is_not_a_repository_is_refused_and_no_enclosing_repository_written(tmp_path):
    """The confirm folder could sit inside another working tree (the supervisor's). Git run in a copy whose .git folder
    is not a repository would search upward and act on the enclosing repository. Since E2g (R1-T1, R1 clause 5) a
    confirm folder inside any repository is refused as a work root before anything is made or cloned (until E2f the
    copy was refused later, because git named the enclosing tree as its working tree); disable_push, which names the
    copy's own .git, is never reached either way."""
    root, g = _confirm_repo(tmp_path, "def test_a():\n    assert True\n")
    g("remote", "add", "origin", "https://example.invalid/seat.git")
    (tmp_path / "home" / "sib" / ".git").mkdir(parents=True)
    enclosing = (root / ".git" / "config").read_text()
    still, passed, why = C.confirm_at_head(root, "seat", ["tests/test_x.py::test_a"], ["../sib"], root / "wk",
                                           g("rev-parse", "HEAD"))
    assert still == [] and passed == [] and "lies inside the git repository" in why and not (root / "wk").exists()
    # E2h INRUN: without a run folder the function refuses before any git act (until E2g3 it reached git and failed
    # with "could not list the remotes"); either way nothing is written upward
    assert C.disable_push(tmp_path / "home" / "sib").startswith("no run folder was named")
    assert (root / ".git" / "config").read_text() == enclosing


def test_a_clone_whose_push_route_cannot_be_closed_is_not_confirmed(tmp_path, monkeypatch):
    root, g = _confirm_repo(tmp_path, "def test_a():\n    assert True\n")
    # B151 finding 2: the confirmation clone goes through copy_isolation.isolate, whose push-URL step fails here
    monkeypatch.setattr(C.CI, "disable_push", lambda repo, url=None, env=None, run=None: "could not disable push for remote 'origin'")
    still, passed, why = C.confirm_at_head(root, "seat", ["tests/test_x.py::test_a"], [], tmp_path / "work",
                                           g("rev-parse", "HEAD"))
    assert still == [] and passed == [] and "could not disable push for remote 'origin'" in why
    assert "confirmation clone" in why and "not re-run" in why


def test_F_only_counts_the_declared_command(tmp_path):
    """A differently-spelled run (piped, or another command) is not the declared suite: INCONCLUSIVE, not PASS."""
    base = tmp_path / "baseline_record.json"
    produce(base, "baseline", {"aget": "a", "head": "h", "output_complete": True, "verdict": "RECORDED",
                               "selection": _kit_report().SELECTION,   # C2c (labelled): the witness
                               "failures": []})
    t = _suite_transcript(tmp_path, ["1 failed, 1 passed\nFAILED tests/a.py::t"])
    t.write_text(t.read_text().replace(SUITE, SUITE + " | tail -5"))
    new, why = C.suite_regressions(t, SUITE, base, "a", "h")
    assert new == [] and "no run of the declared suite command" in why


@pytest.mark.parametrize("cmd,ok", [
    ("git remote", True), ("git remote -v", True), ("git remote --verbose", True),
    ("git remote get-url origin", True), ("git remote get-url --push origin", True),
    ("git remote add x url", False), ("git remote remove origin", False), ("git remote set-url origin u", False),
    ("git remote rename origin x", False), ("git remote prune origin", False), ("git remote update", False),
    ("git remote rm origin", False), ("git remote set-head origin -a", False),
    ("git remote set-branches origin main", False),
    ("git remote show origin", False),                      # contacts the remote
    ("git remote get-url", False), ("git remote get-url a b", False), ("git remote -v add x u", False)])
def test_git_remote_reads_are_read_only_and_its_writes_are_not(cmd, ok):
    """Batch 8 V3.7 (2026-09-29) failed C on `git remote -v`, a config read the harness ran as read-only."""
    assert C.bash_is_read_only(cmd) is ok, cmd


def test_a_track_skills_session_is_not_checked_as_a_migration(run):
    """Batch 9t (2026-09-29): a skill-tracking pass run BEFORE the migration. Its packet lists the release payload,
    rightly not in place yet (D is the migration's), and committing its declared track paths is its purpose (not a
    sweep). A migration-mode session keeps both checks."""
    go, root, tmp = run
    subprocess.run(["git", "-C", str(root), "add", "notes.txt"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--amend",
                    "--no-edit"], check=True)
    (root / "scripts" / "x.py").write_text("not the release\n")
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-am", "x"],
                   check=True)
    pk = tmp / "packet.json"
    receiver = {"aget": "a", "items": [{"path": "scripts/x.py", "op": "write", "sha256": sha("release x\n")}]}
    pk.write_text(json.dumps({"receivers": [{**receiver, "mode": "track-skills", "track_paths": ["notes.txt"]}]}))
    code, out = go()
    assert not out["D"] and not any("notes.txt" in x for x in out["E"]), out
    assert any("track-skills" in x for x in out["recorded"])
    pk.write_text(json.dumps({"receivers": [receiver]}))                   # the same run judged as a migration
    code, out = go()
    assert out["D"] and any("notes.txt" in x and "committed" in x for x in out["E"])


def test_a_pre_existing_change_swept_into_the_migration_commit_fails_E(run):
    """Framework Aget's hazard 4 (2026-09-29): `git commit -a` keeps the pre-dirty file's bytes, so only the commit's
    path list shows it was swept in. Bytes unchanged here, so the digest test alone would pass."""
    go, root, _ = run
    subprocess.run(["git", "-C", str(root), "add", "notes.txt"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--amend",
                    "--no-edit"], check=True)
    code, out = go()
    assert code == 1 and any("notes.txt" in x and "committed" in x for x in out["E"])


def test_a_swept_pre_existing_change_inside_the_write_set_still_fails_E(run):
    """The write set covers the session's own new files (`sessions/**` at batch 8), not the receiver's earlier work
    under the same pattern: batch 8's framework Aget had 16 pre-existing changes under `sessions/`."""
    go, root, tmp = run
    (root / "scripts" / "old.py").write_text("receiver's own\n")
    subprocess.run(["git", "-C", str(root), "add", "scripts/old.py"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--amend",
                    "--no-edit"], check=True)
    snap = tmp / "snap.json"
    s = json.loads(snap.read_text())
    s["dirty"]["scripts/old.py"] = sha("receiver's own\n")             # dirty before the run, under `scripts/*`
    snap.write_text(json.dumps(s))
    code, out = go()
    assert code == 1 and any("scripts/old.py" in x and "committed" in x for x in out["E"])


# --- V3.5 re-qualification, 2026-09-27 (batch 1's two false FAILs; the repair packet's exact copy commands;
# the explicit-deny text measured in H1d; a repair packet's already-correct files) ---------------------------------

@pytest.mark.parametrize("cmd", ['date "+%Y-%m-%dT%H:%M:%S%z"', "date", "date -u +%s", "date -j -u '+%H:%M'",
                                 "git hash-object scripts/a.py scripts/b.py", "git hash-object -t blob scripts/a.py",
                                 "git hash-object --no-filters scripts/a.py"])
def test_batch1_false_fails_are_now_read_only(run, cmd):
    go, _, _ = run
    code, out = go([tool_use("9", "Bash", {"command": cmd}), tool_result("9")])
    assert code == 0 and cmd in out["read_only_allowance_used"], cmd


@pytest.mark.parametrize("cmd", ["date -s now", "date --set=now", "date --set now", "date 0101000026", "date -f x y",
                                 "date -v+1d", "git hash-object -w scripts/a.py", "git hash-object -tw blob x",
                                 "git hash-object --write x", "git hash-object --stdin-paths", "date '+%s' -s x"])
def test_date_and_hash_object_writing_forms_still_fail(run, cmd):
    go, _, _ = run
    code, out = go([tool_use("9", "Bash", {"command": cmd}), tool_result("9")])
    assert code == 1, cmd


def test_a_declared_exact_command_passes_only_verbatim(run):
    go, _, _ = run
    cp = "cp /stage/aget/scripts/x.py scripts/x.py"
    assert go([tool_use("9", "Bash", {"command": cp}), tool_result("9")], allow_exact=[cp])[0] == 0
    # a prefix match would let an extra operand copy both sources into a directory
    code, out = go([tool_use("8", "Bash", {"command": cp + " /etc"}), tool_result("8")], allow_exact=[cp])
    assert code == 1 and any("/etc" in x for x in out["C"])


def test_an_undeclared_cp_fails(run):
    go, _, _ = run
    code, _ = go([tool_use("9", "Bash", {"command": "cp a scripts/x.py"}), tool_result("9")],
                 allow_exact=["cp /stage/aget/scripts/x.py scripts/x.py"])
    assert code == 1


def test_an_explicit_deny_counts_as_not_executed(run):
    go, _, _ = run
    text = "Permission to use Bash with command git push origin main has been denied."
    code, out = go([tool_use("9", "Bash", {"command": "git push origin main"}), tool_result("9", ok=False, content=text)])
    assert code == 0 and not out["C"]


def test_a_verify_item_is_checked_like_a_write(run):
    go, root, _ = run
    items = [{"path": "scripts/x.py", "op": "verify", "sha256": sha("release x\n")}]
    assert go(packet_items=items)[0] == 0
    (root / "scripts" / "x.py").write_text("drifted\n")
    code, out = go(packet_items=items)
    assert code == 1 and any("scripts/x.py" in x for x in out["D"])


def test_a_commit_trailer_inside_the_quoted_message_passes(run):
    go, _, _ = run
    cmd = 'git commit -m "v3.35.0 migration, att\n\nCo-Authored-By: Claude <noreply@anthropic.com>"'
    code, out = go([tool_use("9", "Bash", {"command": cmd}), tool_result("9")])
    assert code == 0 and not out["C"]


@pytest.mark.parametrize("cmd", ['git commit -m "m"\nrm -rf x', 'git commit -m "m" && git push',
                                 'git commit -m "$(rm f)"', 'git commit -m "`rm f`"', 'git commit -m "a" -m "b\nc"',
                                 'git commit -m "a\\"\nrm f"'])
def test_a_commit_that_escapes_its_message_still_fails(run, cmd):
    go, _, _ = run
    code, _ = go([tool_use("9", "Bash", {"command": cmd}), tool_result("9")])
    assert code == 1, cmd


def test_missing_inputs_are_inconclusive(tmp_path):
    assert C.main(["--aget", "a", "--root", str(tmp_path)]) == 3


# --- gh#2802 ruling under route-b-restricted-hooks (V3.5 round 5, 2026-09-28) -----------------------------------

def _watch(tmp_path, name, middle):
    w = tmp_path / name
    w.write_text("\n".join(json.dumps(e) for e in [
        {"event": "start", "t": 100.0, "heartbeat": 5, "interval": 0.5, "files": {}, "stat_tracked": True},
        *middle, {"event": "stop", "t": 108.0}]) + "\n")
    return w


@pytest.fixture
def hooks_file(tmp_path):
    f = tmp_path / "hooks_only_settings.json"
    f.write_text('{"hooks": {}}\n')
    return f, sha('{"hooks": {}}\n')


def test_restricted_route_with_matching_settings_file_passes(run, hooks_file):
    go, _, _ = run
    code, out = go(route="restricted-hooks", settings=hooks_file)
    assert (code, out["verdict"], out["recorded"]) == (0, "PASS", [])


def test_restricted_route_settings_file_changed_fails_B(run, hooks_file):
    """Clause 1: the --settings file's digest blocks (before this, launch_batch only recorded it)."""
    go, _, _ = run
    hooks_file[0].write_text('{"hooks": {}, "permissions": {"allow": ["Bash(rm:*)"]}}\n')
    code, out = go(route="restricted-hooks", settings=hooks_file)
    assert code == 1 and any("--settings file" in x for x in out["B"])


def test_restricted_route_settings_file_deleted_fails_B(run, hooks_file):
    go, _, _ = run
    hooks_file[0].unlink()
    code, out = go(route="restricted-hooks", settings=hooks_file)
    assert code == 1 and any("absent" in x for x in out["B"])


def test_restricted_route_without_the_settings_digest_is_inconclusive(run):
    go, _, _ = run
    code, out = go(route="restricted-hooks")
    assert code == 3 and any("--settings file or its packet digest" in x for x in out["inconclusive"])


def test_restricted_route_records_a_between_poll_write_without_blocking(run, tmp_path, hooks_file):
    """Clause 3: batch 5's case (a user settings write, rule set equal) is recorded, not blocking."""
    go, _, _ = run
    w = _watch(tmp_path, "w_write.jsonl", [{"event": "write", "file": "user", "t": 104.0}])
    code, out = go(watch=w, route="restricted-hooks", settings=hooks_file)
    assert (code, out["verdict"]) == (0, "PASS")
    assert len(out["recorded"]) == 1 and "between-poll" in out["recorded"][0] and "(user)" in out["recorded"][0]


def test_default_route_keeps_a_between_poll_write_inconclusive(run, tmp_path):
    """The relaxation is scoped to the route: without --route it changes nothing."""
    go, _, _ = run
    w = _watch(tmp_path, "w_write2.jsonl", [{"event": "write", "file": "user", "t": 104.0}])
    code, out = go(watch=w)
    assert code == 3 and out["recorded"] == []


def test_restricted_route_an_observed_rule_change_still_fails(run, tmp_path, hooks_file):
    """Clause 2 plus the watcher: a rule added and later removed, when observed, is a FAIL, not a record."""
    go, _, _ = run
    w = _watch(tmp_path, "w_change.jsonl", [
        {"event": "change", "file": "user", "added": ["abc"], "removed": [], "t": 103.0},
        {"event": "change", "file": "user", "added": [], "removed": ["abc"], "t": 104.0}])
    code, out = go(watch=w, route="restricted-hooks", settings=hooks_file)
    assert code == 1 and any("watcher FAIL" in x for x in out["B"])


def test_restricted_route_a_rule_set_differing_from_the_snapshot_still_fails(run, hooks_file):
    go, root, _ = run
    (root / ".claude" / "settings.local.json").write_text(
        json.dumps({"permissions": {"allow": ["Bash(git status)", "Bash(rm:*)"]}}))
    code, out = go(route="restricted-hooks", settings=hooks_file)
    assert code == 1 and any("rule set changed" in x for x in out["B"])


def test_restricted_route_a_coverage_gap_is_still_inconclusive(run, tmp_path, hooks_file):
    """Only between-poll uncertainty is waived: an unstopped watch or a heartbeat gap still is not coverage."""
    go, _, _ = run
    w = tmp_path / "w_gap.jsonl"
    w.write_text("\n".join(json.dumps(e) for e in [
        {"event": "start", "t": 100.0, "heartbeat": 5, "interval": 0.5, "files": {}, "stat_tracked": True},
        {"event": "write", "file": "user", "t": 101.0}, {"event": "stop", "t": 160.0}]) + "\n")
    code, out = go(watch=w, route="restricted-hooks", settings=hooks_file)
    assert code == 3 and any("gap" in x for x in out["inconclusive"]) and out["recorded"]


@pytest.mark.parametrize("cmd", ["git grep -n foo", "git grep -e x -- scripts", "git grep -l --cached y",
                                 "git diff --no-index --full-index -U0 a b", "git log -1 --format=%H",
                                 "git diff --no-index --stat=0 a b", "git log --oneline -5 -- f"])
def test_git_grep_and_batch5_forms_are_read_only(run, cmd):
    go, _, _ = run
    code, out = go([tool_use("9", "Bash", {"command": cmd}), tool_result("9")])
    assert code == 0 and cmd in out["read_only_allowance_used"], cmd


@pytest.mark.parametrize("cmd", [
    "git grep -O foo", "git grep -Ovim foo", "git grep -nOvim foo", "git grep --open-files-in-pager=vim x",
    "git grep --open-files-in-pager x", "git grep --open x", "git grep --open=vim x",
    # abbreviations and attached values that exact matching missed, on the commands already allowed
    "git diff --outp=AGENTS.md", "git log --out=x", "git diff --ext", "git ls-remote -utouch origin",
    "git ls-remote --upload=x origin", "git show -ofile HEAD"])
def test_git_pager_output_and_exec_spellings_fail(run, cmd):
    go, _, _ = run
    code, out = go([tool_use("9", "Bash", {"command": cmd}), tool_result("9")])
    assert code == 1, cmd


def test_watcher_reports_between_poll_reasons_separately():
    W = C.W
    ev = [{"event": "start", "t": 1.0, "heartbeat": 5, "interval": 0.5, "files": {}, "stat_tracked": True},
          {"event": "write", "file": "user", "t": 2.0}, {"event": "stop", "t": 3.0}]
    v = W.verdict(ev)
    assert v["verdict"] == "INCONCLUSIVE" and v["between_poll"] and set(v["between_poll"]) <= set(v["reasons"])
    assert W.verdict(ev[:1] + ev[2:])["between_poll"] == []


def test_a_suite_run_with_report_only_flags_counts_and_a_narrowed_one_does_not():
    """Rehearsal 2026-09-30: `python3 -m pytest -q -rfE -p no:cacheprovider` read INCONCLUSIVE (no run of the declared
    command) although the prompt allows test arguments; the same packet had read PASS one run earlier."""
    ok = C.is_suite_run
    assert ok("python3 -m pytest -q", "python3 -m pytest -q")
    assert ok("python3 -m pytest -q -rfE -p no:cacheprovider", "python3 -m pytest -q")
    assert ok("python3 -m pytest -q --tb=short -vv", "python3 -m pytest -q")
    for narrowed in ("python3 -m pytest -q -x", "python3 -m pytest -q -k slow", "python3 -m pytest -q tests/a.py",
                     "python3 -m pytest -q --lf", "python3 -m pytest", "python3 -m pytest -q; rm -rf x"):
        assert not ok(narrowed, "python3 -m pytest -q"), narrowed


def test_an_unsafe_item_reads_inconclusive_not_merged(run):
    """Reviewer session, B131: a packet item left unmigrated because its path goes through a symbolic link must not
    let the run read PASS; it reads INCONCLUSIVE, so the push gate does not push the member."""
    go, root, tmp_path = run
    pk = tmp_path / "packet.json"
    d = json.loads(pk.read_text())
    d["receivers"][0]["items"].append({"path": "scripts/linked.py", "op": "unsafe",
                                       "why": "unsafe path: scripts/linked.py is a symbolic link"})
    pk.write_text(json.dumps(d))
    code, out = go()
    assert code == 3 and out["verdict"] == "INCONCLUSIVE"
    assert any(x.startswith("scripts/linked.py: not migrated") for x in out["inconclusive"])
    assert not any(x.startswith("scripts/linked.py") for x in out["merged"])


# --- Gate 3 of the kit design pass (v336-release:R28): R2 in the after-run check -----------------------------------

def _commit_receipt(root, text):
    (root / RECEIPT_AT["receipt_path"]).write_text(text)
    subprocess.run(["git", "-C", str(root), "add", RECEIPT_AT["receipt_path"]], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "r"],
                   check=True)


@pytest.mark.parametrize("text,kind", [
    ("## Attempt att-1\nTerminal: ACCEPTED\nTerminal: UNKNOWN\n", "inconclusive"),
    ("## Attempt att-1\n**Terminal: ACCEPTED**\n", "inconclusive"),
    ("## Attempt other\nTerminal: ACCEPTED\n", "inconclusive"),
    ("## Attempt att-1\nTerminal: REJECTED\n", "recorded")])
def test_r2_h_reads_the_receipt_terminal_at_head(run, text, kind):
    """After-run check H (R2; DESIGN's after-run "G (receipt grammar)", renamed H for D-11): the receipt at HEAD is
    read in the packet's attempt section. A malformed one reads INCONCLUSIVE; a valid REJECTED is recorded, not a
    finding (the push gate refuses it). At 34353311 the check never reads the receipt."""
    go, root, _ = run
    _commit_receipt(root, text)
    code, out = go()
    if kind == "inconclusive":
        assert out["verdict"] == "INCONCLUSIVE" and any(x.startswith("H: receipt terminal") for x in out["inconclusive"])
    else:
        assert out["verdict"] == "PASS" and any("REJECTED" in x and x.startswith("H:") for x in out["recorded"])


def test_r2_the_verdict_is_bound_to_its_run_and_session(run, tmp_path):
    """R2 clause 1, invoker-recorded (launch_batch.run_one): with --run-id and --session-id the verdict carries its
    binding (run, member, session, HEAD judged) and is the current run for its file; a --run-id that is not the run
    last started for that file is refused (exit 2) and writes nothing. At 34353311 neither option exists (a usage
    error)."""
    go, root, _ = run
    RBND = _rb()
    out = tmp_path / "o.json"
    rid = RBND.start_run("after_run_check", out, recorded_by="invoker")
    code, doc = go(extra_args=["--run-id", rid, "--session-id", "S-9"])
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert doc["binding"] == {"aget": "a", "session_id": "S-9", "subject": head, "run_id": rid}
    assert RBND.read_current("after_run_check", out)[1] is None
    RBND.start_run("after_run_check", out, recorded_by="invoker")                  # a later run started
    before = out.read_bytes()
    code, _ = go(extra_args=["--run-id", rid, "--session-id", "S-9"])
    assert code == 2 and out.read_bytes() == before


def _rb():
    spec = importlib.util.spec_from_file_location("result_binding", ROOT / "scripts/migration_kit/result_binding.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def test_r3_t3_a_kept_item_whose_bytes_changed_fails_D(run):
    """R3-T3, J-1 (S-256). A 0-line hold (KEEP) whose working-tree bytes differ from its `pre` is a D finding. At
    34353311 every hold is recorded as "merged" and D compares nothing, so the run PASSes."""
    go, _, _ = run
    kept = {"path": "scripts/x.py", "op": "hold", "kind": "unattributed", "authored_lines": 0, "staged": "s",
            "pre": hashlib.sha256(b"the receiver's own bytes\n").hexdigest()}
    code, out = go(packet_items=[kept])
    assert code == 1 and any("kept" in x for x in out["D"])
    code, out = go(packet_items=[{**kept, "pre": hashlib.sha256(b"release x\n").hexdigest()}])      # control
    assert code == 0


def test_r3_t4_an_unknown_item_label_is_inconclusive_in_D(run):
    """R3-T4, after-run half (S-256). An item with op 'bogus' reads INCONCLUSIVE. At 34353311 D has no else-branch,
    so the item is silently not examined and the run PASSes."""
    go, _, _ = run
    code, out = go(packet_items=[{"path": "scripts/x.py", "op": "bogus", "sha256": "0" * 64}])
    assert code == 3 and any("bogus" in x for x in out["inconclusive"])


def test_r1_t8b_a_write_through_a_hard_link_made_after_the_launch_sweep_fails_G(run, tmp_path):
    """R1-T8 (b), check G (R1-S (iii)); the detection test behind design read 2's D-1 limit. A write-set path that
    became a second name of an outside file after the launch sweep is written by the session. G names it and the
    verdict is FAIL. The test asserts detection, not prevention: the outside file HAS changed. At 34353311 the run
    PASSes: check C resolves the path, which stays inside the member, and nothing reads the link count. (A symbolic
    link is already caught by C at 34353311, which resolves it outside the member; G reports it too.)"""
    go, root, _ = run
    outside = tmp_path / "outside.py"
    outside.write_text("written through the hard link\n")                  # the session's write already landed
    os.link(outside, root / "scripts" / "late.py")
    code, out = go(extra_events=[tool_use("9", "Write", {"file_path": str(root / "scripts" / "late.py")}),
                                 tool_result("9")])
    assert code == 1 and any("late.py" in x and "hard link" in x for x in out.get("G", []))
    assert outside.read_text() == "written through the hard link\n"


def test_b148_5_g_includes_an_ignored_instruction_path_already_reported_by_e(run):
    """B148 finding 5 (REVW3's falsifier). An ignored `.claude/hooks/a.py`, replaced by a hard link to an outside file
    and written with no edit-tool call in the transcript: E reports the byte change, and G must report the second name
    too. On stage F2, G read only edit-tool paths and git's changed paths, so G was empty."""
    go, root, tmp = run
    p = root / ".claude/hooks/a.py"
    p.parent.mkdir()
    p.write_text("before\n")
    snap = tmp / "snap.json"
    d = json.loads(snap.read_text())
    d["claude_tree"][".claude/hooks/a.py"] = sha("before\n")
    snap.write_text(json.dumps(d))
    outside = tmp / "outside.py"
    outside.write_text("before\n")
    p.unlink()
    os.link(outside, p)
    p.write_text("changed\n")
    code, out = go()
    assert any(".claude/hooks/a.py" in s for s in out["E"]), out["E"]
    assert any(".claude/hooks/a.py" in s and "names" in s for s in out["G"]), out["G"]


# --- REVW6's B158 read of stage E2e6 -----------------------------------------------------------------------------

@pytest.mark.parametrize("character", ["\r", "\t", "\n", ""], ids=["cr", "tab", "lf", "plain"])
def test_b158_1_g_judges_the_real_file_for_an_unusual_dirty_name(tmp_path, monkeypatch, character):
    """B158 finding 1 (REVW6's falsifier; `plain` is its control). An untracked file `notes_<c>.txt` exists when the
    real snapshot producer runs; during the run it is replaced by a hard link to an outside file and written, with no
    edit-tool call naming it. The check must not PASS, and G must name the link. On stage E2e6 git's newline listing
    quoted the name, the snapshot recorded the quoted spelling as absent, E and G inspected a path that does not
    exist, and the verdict was PASS with E and G empty."""
    rel_name = "notes_" + character + ".txt"
    original = C.full_snapshot

    def capture(root):
        (Path(root) / rel_name).write_text("before\n")   # the dirty file exists when the real snapshot is taken
        return original(root)
    monkeypatch.setattr(C, "full_snapshot", capture)
    go, root, tmp = run.__wrapped__(tmp_path, monkeypatch)
    monkeypatch.setattr(C, "full_snapshot", original)
    f = root / rel_name
    outside = tmp / "outside.txt"
    outside.write_text("before\n")
    f.unlink()
    os.link(outside, f)
    f.write_text("after\n")
    code, out = go()
    assert code != 0 and any("names" in g for g in out["G"]), (code, out["verdict"], out["E"], out["G"])


def test_b158_1_status_paths_are_read_byte_for_byte_and_renames_name_both(tmp_path):
    """B158 finding 1, the shared reader's parse (control for `prepare_launch.pre_dirty`): `git status --porcelain -z`
    records are split on NUL, a name with a tab comes back as itself, and a rename names its new and old path."""
    CI_ = importlib.util.module_from_spec(importlib.util.spec_from_file_location(
        "copy_isolation", Path(__file__).resolve().parents[2] / "scripts/migration_kit/copy_isolation.py"))
    CI_.__spec__.loader.exec_module(CI_)
    root = tmp_path / "r"
    root.mkdir()
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    (root / "old.txt").write_text("x\n")
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c"],
                   check=True)
    subprocess.run(["git", "-C", str(root), "mv", "old.txt", "new.txt"], check=True)
    (root / "a\tb.txt").write_text("y\n")
    got = sorted(CI_.git_status_paths(root))
    assert got == sorted(["new.txt", "old.txt", "a\tb.txt"]), got


# --- REVW6's B159 read of stage E2e7 (finding 3) -----------------------------------------------------------------

def test_b159_3_a_failed_listing_records_inconclusive_and_exits_3(tmp_path, monkeypatch):
    """B159 finding 3 (REVW6's falsifier). The run's own temporary git index is damaged before the check, so the git
    listing fails: the result is INCONCLUSIVE, recorded, printed, and the exit is 3. On stage E2e7 the record was
    written and the printer then raised KeyError('A'); on stage E2e6 the same run read PASS."""
    go, root, tmp = run.__wrapped__(tmp_path, monkeypatch)
    (root / ".git" / "index").write_bytes(b"synthetic invalid index")
    code, out = go()
    assert code == 3 and out["verdict"] == "INCONCLUSIVE", (code, out)
    assert any("git listing" in x for x in out["inconclusive"]) and "git listing" in out["why"], out


@pytest.mark.parametrize("when", ["inside", "retargeted"])
def test_r1_t2c_a_hook_link_retargeted_outside_the_run_reads_inconclusive_after_the_run(run, when):
    """R1-T2 (c), the after-run half (E2g). After a rehearsal session in a copy, the check is given the copy's run
    folder (--copy-run) and asks LINKS again: a hook link that still resolves inside reads PASS; one retargeted
    outside during the run reads INCONCLUSIVE and is named. The option is new in E2g, so on stage E2f2 this test
    fails at argument parsing (labelled, not counted as a defect's falsifier: run_one's --copy-run is the
    behavioural one, test_r1_t2c_the_session_rehearsal_runs_under_the_contained_environment_with_the_copys_hooks)."""
    go, root, tmp_path = run
    # E2i: the pre-launch snapshot of a copy is taken with --copy-run, as launch_batch now takes it, so the ignore
    # state under the session's contained environment is recorded (without it IGN reads INCONCLUSIVE)
    assert C.main(["--aget", "a", "--root", str(root), "--snapshot", str(tmp_path / "snap.json"), "--copy-run", str(root)]) == 0
    resnapshot_baseline(tmp_path, root)
    outside = tmp_path / "outside.sh"
    outside.write_text("#!/bin/sh\n")
    (root / ".git" / "hooks").mkdir(exist_ok=True)
    (root / ".git" / "hooks" / "pre-commit").symlink_to("../../notes.txt" if when == "inside" else str(outside))
    code, out = go(extra_args=["--copy-run", str(root)])
    found = [x for x in out["inconclusive"] if x.startswith("LINKS after the run")]
    if when == "inside":
        assert (code, out["verdict"], found) == (0, "PASS", []), out
    else:
        assert out["verdict"] == "INCONCLUSIVE" and found and "pre-commit" in found[0], out


@pytest.mark.parametrize("where", ["sibling_outside", "sibling_inside"])
def test_b162_2_post_session_links_cover_a_declared_sibling(tmp_path, monkeypatch, where):
    """B162 finding 2 (REVW6's falsifier), after-run half. --copy-run names the folder holding the copy and a declared
    sibling; the sibling's hook link is retargeted outside it during the run: INCONCLUSIVE, naming the link. Control:
    left inside, PASS. On stage E2g the check walked only the copy (--root) and read PASS."""
    go, root, rdir = run.__wrapped__(tmp_path / "run", monkeypatch)
    # E2i: the pre-launch snapshot of a copy is taken with --copy-run, as launch_batch now takes it, so the ignore
    # state under the session's contained environment is recorded (without it IGN reads INCONCLUSIVE)
    assert C.main(["--aget", "a", "--root", str(root), "--snapshot", str(rdir / "snap.json"), "--copy-run", str(rdir)]) == 0
    resnapshot_baseline(rdir, root)
    sib = rdir / "sib"
    sib.mkdir()
    subprocess.run(["git", "init", "-q", str(sib)], check=True)
    (sib / ".git" / "hooks").mkdir(exist_ok=True)
    outside = tmp_path / "outside-hook"
    outside.write_text("#!/bin/sh\n")
    target = str(outside) if where == "sibling_outside" else str(rdir / "notes-inside")
    (sib / ".git" / "hooks" / "pre-commit").symlink_to(target)
    code, out = go(extra_args=["--copy-run", str(rdir)])
    found = [x for x in out["inconclusive"] if x.startswith("LINKS after the run")]
    if where == "sibling_inside":
        assert (code, out["verdict"], found) == (0, "PASS", []), out
    else:
        assert out["verdict"] == "INCONCLUSIVE" and found and "sib" in found[0], out


def test_b162_2_a_copy_run_that_does_not_hold_the_copy_is_not_accepted(run):
    """B162 finding 2's repair route: the run bound given is validated, not broadened to any caller path. A
    --copy-run that is neither the copy nor the folder holding it reads INCONCLUSIVE. On stage E2g any folder was
    accepted as the bound, and the check read PASS."""
    go, root, tmp_path = run
    elsewhere = tmp_path / "elsewhere"
    elsewhere.mkdir()
    code, out = go(extra_args=["--copy-run", str(elsewhere)])
    assert out["verdict"] == "INCONCLUSIVE" and any("neither the copy" in x for x in out["inconclusive"]), out


# --- REVW6's B163 read of stage E2g2 -----------------------------------------------------------------------------

@pytest.mark.parametrize("declared_by", ["option", "packet"])
def test_b163_1_a_copy_run_that_omits_a_declared_sibling_is_not_accepted(tmp_path, monkeypatch, declared_by):
    """B163 finding 1 (REVW6's falsifier). A sibling is declared (by --sibling-read, or in the packet's receiver row)
    and its hook link leads outside the run, but --copy-run names only the copy: INCONCLUSIVE, the run not checked.
    On stage E2g2 the copy alone was accepted as the bound, the sibling was not walked, and the check read PASS."""
    go, root, rdir = run.__wrapped__(tmp_path / "run", monkeypatch)
    sib = rdir / "sib"
    sib.mkdir()
    subprocess.run(["git", "init", "-q", str(sib)], check=True)
    (sib / ".git" / "hooks").mkdir(exist_ok=True)
    outside = tmp_path / "outside-hook"
    outside.write_text("#!/bin/sh\n")
    (sib / ".git" / "hooks" / "pre-commit").symlink_to(outside)
    extra = ["--copy-run", str(root)]
    if declared_by == "option":
        extra += ["--sibling-read", "../sib"]
    else:
        pk = rdir / "packet.json"
        doc = json.loads(pk.read_text())
        doc["receivers"][0]["sibling_reads"] = ["../sib"]
        pk.write_text(json.dumps(doc))
    code, out = go(extra_args=extra)
    assert out["verdict"] == "INCONCLUSIVE" and any("siblings are declared" in x for x in out["inconclusive"]), out


@pytest.mark.parametrize("where", ["outside", "inside"])
def test_b163_4_a_hooks_path_changed_outside_the_run_reads_inconclusive_after_the_run(tmp_path, monkeypatch, where):
    """B163 finding 4 (REVW6's falsifier). During the session the copy's `core.hooksPath` is set to a folder outside
    the run holding a regular pre-commit (no link anywhere): the after-run check, reading the value again under the
    session's configuration, reads INCONCLUSIVE. Control: a hooks folder in the run folder, beside the copy, reads
    PASS. On stage E2g2 the
    value was read only at the launch and the check read PASS."""
    go, root, rdir = run.__wrapped__(tmp_path / "run", monkeypatch)
    hooks = (tmp_path / "outside-hooks") if where == "outside" else (rdir / "inside-hooks")
    hooks.mkdir()
    (hooks / "pre-commit").write_text("#!/bin/sh\necho synthetic hook\n")
    (hooks / "pre-commit").chmod(0o755)
    subprocess.run(["git", "-C", str(root), "config", "core.hooksPath", str(hooks)], check=True)
    code, out = go(extra_args=["--copy-run", str(root)])
    found = [x for x in out["inconclusive"] if x.startswith("hooks after the run")]
    if where == "inside":
        # E2i: the session wrote the copy's .git/config, a configuration file git reads (clause 8 (iv)), so IGN reads
        # INCONCLUSIVE naming it; the hooks re-read itself finds nothing (until E2i this read PASS)
        assert (code, out["verdict"], found) == (3, "INCONCLUSIVE", []), out
        assert [x for x in out["inconclusive"] if x.startswith("IGN: git's ignore state changed during the run: "
                                                                "config file ") and x.endswith(".git/config")], out
        assert all(x.startswith("IGN: ") for x in out["inconclusive"]), out
    else:
        assert out["verdict"] == "INCONCLUSIVE" and found and "outside the run folder" in found[0], out


# --- REVW6's B164 read of stage E2g3 -----------------------------------------------------------------------------

def test_b164_1_a_session_s_core_worktree_change_is_seen_by_the_hooks_re_read(tmp_path, monkeypatch):
    """B164 finding 1 (REVW6's falsifier). During the session the copy's `core.hooksPath` is set to the relative
    `.git/hooks` and `core.worktree` to an outside folder holding the same files, so git runs the outside folder's
    hook. The after-run re-read sees that git no longer acts on the copy and reads INCONCLUSIVE. On stage E2g3 the
    relative value was joined to the copy, judged inside, and the check read PASS."""
    import shutil
    go, root, rdir = run.__wrapped__(tmp_path / "run", monkeypatch)
    outside = tmp_path / "outside-tree"
    shutil.copytree(root, outside, ignore=shutil.ignore_patterns(".git"))
    for a in (("core.hooksPath", ".git/hooks"), ("core.worktree", str(outside))):
        subprocess.run(["git", "-C", str(root), "config", *a], check=True)
    code, out = go(extra_args=["--copy-run", str(root)])
    found = [x for x in out["inconclusive"] if x.startswith("hooks after the run")]
    assert out["verdict"] != "PASS" and found and "cannot be judged" in found[0], out


@pytest.mark.parametrize("packet_state", ["declared", "unreadable"])
def test_b164_2_the_confirmation_copies_the_packet_s_declared_siblings(run, monkeypatch, packet_state):
    """B164 finding 2. A sibling declared only in the packet's row is given to F's confirmation run (the same
    population the post-run walk uses); a packet that is given but cannot be read makes F INCONCLUSIVE instead of
    confirming against no siblings. On stage E2g3 F passed only --sibling-read, so the packet's sibling was absent
    from the confirming clone (REVW6's native falsifier cleared a session failure that way)."""
    go, root, tmp_path = run
    pk = tmp_path / "packet.json"
    doc = json.loads(pk.read_text())
    doc["receivers"][0]["sibling_reads"] = ["../sib"]
    pk.write_text(json.dumps(doc) if packet_state == "declared" else "{not json")
    seen = {}
    monkeypatch.setattr(C, "suite_regressions", lambda *a, **k: (["tests/t.py::test_x"], None))

    def confirm(root_, aget, ids, siblings, work, rev="HEAD"):
        seen["siblings"] = list(siblings)
        return [], list(ids), None
    monkeypatch.setattr(C, "confirm_at_head", confirm)
    base = tmp_path / "base.json"
    base.write_text(json.dumps({"verdict": "RECORDED", "failures": []}))
    code, out = go(extra_args=["--suite-cmd", "python3 -m pytest -q", "--baseline-record", str(base),
                               "--confirm-dir", str(tmp_path / "confirm")])
    if packet_state == "declared":
        assert seen.get("siblings") == ["../sib"], seen
    else:
        assert "siblings" not in seen and any(x.startswith("F: the packet's declared siblings cannot be read")
                                              for x in out["inconclusive"]), out


# --- E2i: ignore state (IGN, R1 clause 8; H-3, R1-T9 (5)) ----------------------------------------------------------

def _global_ignore():
    """The default global ignore file git reads in this process's environment (core.excludesFile unset)."""
    xdg = os.environ.get("XDG_CONFIG_HOME")
    return (Path(xdg) if xdg else Path(os.environ["HOME"]) / ".config") / "git" / "ignore"


def test_e2i_r1_t9_5_a_global_ignore_change_during_the_session_is_inconclusive_naming_the_element(run):
    """R1-T9 (5), H-3 (live): the pre-launch --snapshot records git's ignore state; a session that changes the global
    ignore file and writes a file it hides is INCONCLUSIVE naming the element. Until E2i the hidden file was not
    listed by git, and E read PASS."""
    go, root, _ = run
    f = _global_ignore()
    f.parent.mkdir(parents=True, exist_ok=True)
    f.write_text("hidden*\n")
    (root / "hidden.txt").write_text("written by the session, hidden by the new rule\n")
    code, out = go()
    assert out["verdict"] == "INCONCLUSIVE" and code == 3, out
    assert [x for x in out["inconclusive"] if x.startswith("IGN: git's ignore state changed during the run: "
                                                            "core.excludesFile file")], out["inconclusive"]


def test_e2i_a_snapshot_without_ignore_state_is_inconclusive(run):
    """R1 clause 8: a pre-launch snapshot that does not record the ignore state (one taken by an earlier kit) cannot
    rule out a hidden write; E is INCONCLUSIVE, never PASS. Until E2i it read PASS."""
    go, root, tmp_path = run
    snap = tmp_path / "snap.json"
    doc = json.loads(snap.read_text())
    assert "ignore_state" in doc and "ignored" in doc
    del doc["ignore_state"]
    snap.write_text(json.dumps(doc))
    code, out = go()
    assert out["verdict"] == "INCONCLUSIVE"
    assert "IGN: the snapshot has no ignore state, so a write hidden by a changed ignore rule is not ruled out" in \
        out["inconclusive"]


def test_e2i_the_write_set_gitignore_is_recorded_and_what_it_newly_ignores_is_judged(tmp_path):
    """R1 clause 8's one exception: a `.gitignore` at a path the step writes (here the root `.gitignore`, a
    track-skills receiver's protected write) is recorded, not refused; every path git ignores after the run and did
    not before must then lie in the write set, else it is an E finding."""
    root = tmp_path / "aget"
    (root / "scripts").mkdir(parents=True)
    (root / ".gitignore").write_text("*.tmp\n")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "b"],
                   check=True)
    snap = C.full_snapshot(root)
    (root / ".gitignore").write_text("*.tmp\nscripts/*.log\nprivate.txt\n")
    (root / "scripts" / "run.log").write_text("in the write set\n")
    (root / "private.txt").write_text("outside the write set, now hidden\n")
    out = {"E": [], "inconclusive": [], "recorded": []}
    C.ignore_check(root, snap, {".gitignore"}, ["scripts/*"], out)
    assert out["inconclusive"] == []
    assert out["recorded"] == ["IGN: ['.gitignore .gitignore'] changed during the run (paths the step writes)"]
    assert out["E"] == ["private.txt: ignored after the run's change to ['.gitignore .gitignore'], and outside the "
                        "write set"]


def test_e2i_the_confirmation_run_is_not_confirmed_when_it_changes_the_ignore_state(tmp_path):
    """R1 clause 8 at F's confirmation run: a candidate whose rerun changes git's ignore state (a self-ignoring
    nested `.gitignore`) is not confirmed, and the reason names the element. Until E2i it was confirmed as passing
    at HEAD."""
    tests = ("from pathlib import Path\n\ndef test_a():\n    Path('sub').mkdir()\n"
             "    Path('sub/.gitignore').write_text('*\\n')\n    Path('sub/h.txt').write_text('x\\n')\n")
    root, g = _confirm_repo(tmp_path, tests)
    still, passed, why = C.confirm_at_head(root, "seat", ["tests/test_x.py::test_a"], [], tmp_path / "work",
                                           g("rev-parse", "HEAD"))
    assert still == [] and passed == [], (still, passed, why)
    assert why and "the confirmation run changed git's ignore state" in why and ".gitignore sub/.gitignore" in why


def test_r62_f5_default_suite_in_a_fresh_checkout_preserves_after_run_ignore_state(tmp_path, monkeypatch):
    """F-5: execute the actual member default, then judge IGN with the real after-run checker."""
    import shlex
    import sys
    spec = importlib.util.spec_from_file_location("r62_prepare", ROOT / "scripts/migration_kit/prepare_launch.py")
    prepare = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(prepare)
    global_config = tmp_path / "global.config"
    global_config.write_text("")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(global_config))
    monkeypatch.setenv("GIT_CONFIG_NOSYSTEM", "1")
    root = tmp_path / "fresh-member"
    (root / "tests").mkdir(parents=True)
    (root / "tests/test_member.py").write_text("def test_member():\n    assert 1 + 1 == 2\n")
    subprocess.run(["git", "init", "-q", str(root)], check=True)
    subprocess.run(["git", "-C", str(root), "add", "tests/test_member.py"], check=True)
    subprocess.run(["git", "-C", str(root), "-c", "user.name=Fixture", "-c", "user.email=f@local",
                    "commit", "-qm", "fresh member"], check=True)
    assert not (root / ".pytest_cache").exists()
    before = C.full_snapshot(root)
    suite = prepare.suite_command({})
    command = shlex.split(suite)
    assert command[0] == "python3"
    # Resolve that interpreter alias to this suite's interpreter, keeping every default argument.
    run = subprocess.run([sys.executable, *command[1:]], cwd=root, capture_output=True, text=True,
                         timeout=30, env=dict(os.environ, PYTHONDONTWRITEBYTECODE="1"))
    assert run.returncode == 0 and "1 passed" in run.stdout, (run.stdout, run.stderr)
    out = {"E": [], "inconclusive": [], "recorded": []}
    C.ignore_check(root, before, set(), [], out)
    assert out["inconclusive"] == [], (suite, out)
    assert out["E"] == [] and out["recorded"] == []
    assert not (root / ".pytest_cache").exists()
    assert C.RBND.is_suite_run(suite, suite)
    assert C.RBND.is_suite_run(suite + " -rfE", suite)


def test_e2i_a_copy_session_s_own_global_ignore_change_is_inconclusive(tmp_path, monkeypatch):
    """R1 clause 8 for a rehearsal copy (V3.7, --copy-run): the session ran under the contained environment, whose
    global ignore file lies in the run folder. The pre-launch snapshot, taken with --copy-run, reads the ignore state
    under that environment as well, and a change there is INCONCLUSIVE naming it. Until E2i neither was read."""
    go, root, rdir = run.__wrapped__(tmp_path / "run", monkeypatch)
    snap = rdir / "snap.json"
    assert C.main(["--aget", "a", "--root", str(root), "--snapshot", str(snap), "--copy-run", str(root)]) == 0
    resnapshot_baseline(rdir, root)
    assert "core.excludesFile file (session environment)" in json.loads(snap.read_text())["ignore_state"]
    xdg = Path(C.CI.contained_read_env(rdir, root)["XDG_CONFIG_HOME"])
    (xdg / "git").mkdir(parents=True, exist_ok=True)
    (xdg / "git" / "ignore").write_text("hidden*\n")
    code, out = go(extra_args=["--copy-run", str(root)])
    assert out["verdict"] == "INCONCLUSIVE", out
    assert "IGN: git's ignore state changed during the run: core.excludesFile file (session environment)" in \
        out["inconclusive"], out["inconclusive"]


@pytest.mark.parametrize("copy_root", [True, False])
def test_e2i_the_launch_takes_a_copy_s_snapshot_with_its_run_folder(tmp_path, monkeypatch, copy_root):
    """E2i: launch_batch's pre-launch snapshot passes --copy-run for a copy-root receiver (so the ignore state under
    the session's contained environment is recorded) and not for a live one. Until E2i it never passed it."""
    spec = importlib.util.spec_from_file_location("launch_batch", ROOT / "scripts/migration_kit/launch_batch.py")
    LB = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(LB)
    seen = []
    monkeypatch.setattr(LB.subprocess, "run", lambda argv, **k: seen.append(argv))
    r = {"aget": "a", "location": str(tmp_path / "run" / "a"), "sibling_reads": []}
    if copy_root:
        r["_copy_root"] = True
    LB.take_snapshot(r, tmp_path / "ev")
    assert ("--copy-run" in seen[0]) is copy_root
    if copy_root:
        assert seen[0][seen[0].index("--copy-run") + 1] == str(tmp_path / "run" / "a")


@pytest.mark.parametrize("case", ["no_result", "dry_run", "file_not_ok"])
def test_r2_t6_after_run_an_unbound_apply_entry_is_inconclusive_and_exempts_nothing(run, case):
    """R2-T6 at the after-run check: an apply entry with no result, from a trial run, or with a file the apply did not
    write reads INCONCLUSIVE (A), and its paths are not exempt from E. Before C2a a missing result passed, a trial-run
    receipt passed, and a failed file's path was exempt from E."""
    go, root, tmp_path = run
    rc = tmp_path / "receipt.json"
    d = json.loads(rc.read_text())
    {"no_result": lambda: d["agets"][0].pop("result"), "dry_run": lambda: d.update(mode="dry-run"),
     "file_not_ok": lambda: d["agets"][0]["files"][0].update(ok=False)}[case]()
    rc.write_text(json.dumps(d))
    code, out = go()
    assert out["verdict"] == "INCONCLUSIVE" and [x for x in out["inconclusive"] if x.startswith("A: ")], out


# --- REVW9's B179 read of stage C2a: F compares failing ids read whole --------------------------------------------

def _bound_baseline(path, failures):
    """A RECORDED baseline record written as its producer writes it (run recorded, result bound), naming member `a` and
    HEAD `h`, so the comparison below reads it on every later stage too."""
    RB = C.RBND
    doc = {"aget": "a", "head": "h", "verdict": "RECORDED", "output_complete": True, "failures": failures,
           "selection": _kit_report().SELECTION}                  # C2c (labelled): the witness
    RB.write_result("baseline", path, doc, RB.start_run("baseline", path, aget="a", recorded_by="invoker"))


def _regressions(t, base, report=None, token=None):
    # C2a7 (changed, labelled): the two extra arguments are now the kit report and its token; C2b (R2-T11): the
    # baseline is bound to member "a" and HEAD "h"
    return C.suite_regressions(t, SUITE, base, "a", "h", report=report, token=token)


def test_b179_3_a_different_failure_sharing_a_first_word_is_new(tmp_path):
    """B179 finding 3 (REVW9's falsifier, consumer half). The baseline lists `t[case alpha]`; the session's run fails
    `t[case beta]`. F names the new failure. On stage C2a both were read as `t[case` and the new failure was exempt."""
    base = tmp_path / "baseline_record.json"
    _bound_baseline(base, ["tests/t.py::t[case alpha]"])
    # B180 finding 1 (changed, labelled): pytest's short summary header added, as pytest prints it
    # C2a7 (B185 finding 1, changed, labelled): the run carries its kit report
    rpt, tok, texts = _kit_report().reported(tmp_path / "r.jsonl", [(
        "=== short test summary info ===\nFAILED tests/t.py::t[case beta] - assert 0\n1 failed, 1 passed in 0.1s",
        ["tests/t.py::t[case beta]"])])
    t = _suite_transcript(tmp_path, texts)
    new, why = _regressions(t, base, rpt, tok)
    assert why is None and new == ["tests/t.py::t[case beta]"], (new, why)


def test_b179_3_an_undelimitable_failing_id_makes_f_unavailable(tmp_path):
    """B179 finding 3: a failing id with an unbalanced `[` cannot be delimited, so F is unavailable (INCONCLUSIVE), not
    a comparison of a cut id."""
    base = tmp_path / "baseline_record.json"
    _bound_baseline(base, [])
    t = _suite_transcript(tmp_path, ["=== short test summary info ===\n"
                                     "FAILED tests/t.py::t[unclosed - boom\n1 failed, 1 passed in 0.1s"])
    new, why = _regressions(t, base)
    # B180 finding 1 (changed, labelled): pytest's summary header added; the reason now names an id whose end is not unique
    # (C2a5: a parametrized name cut before its `]`)
    # C2a7 (B185 finding 1, changed, labelled): with no kit report the ids are not known at all; with the report the
    # display line is not read and the report's whole id is compared
    assert new == [] and why and "kit report" in why, (new, why)
    rpt, tok, texts = _kit_report().reported(tmp_path / "r.jsonl", [(
        "=== short test summary info ===\nFAILED tests/t.py::t[unclosed - boom\n1 failed, 1 passed in 0.1s",
        ["tests/t.py::t[unclosed - boom]"])])
    new, why = _regressions(_suite_transcript(tmp_path, texts), base, rpt, tok)
    assert (new, why) == (["tests/t.py::t[unclosed - boom]"], None)


# --- REVW9's B179 read of stage C2a: the live check reads the index and working tree git selects ----------------

def test_b179_4_the_live_check_names_a_flag_change_in_the_selected_index(run, monkeypatch):
    """B179 finding 4 (REVW9's live falsifier). Under a fixed GIT_INDEX_FILE, a clean run is PASS; a path then marked
    skip-worktree in the selected index makes the run INCONCLUSIVE naming the index flags. On stage C2a2 it was PASS."""
    go, root, tmp_path = run
    index = tmp_path / "selected-index"
    index.write_bytes((root / ".git" / "index").read_bytes())
    monkeypatch.setenv("GIT_INDEX_FILE", str(index))
    snap_path = tmp_path / "snap.json"
    snap = json.loads(snap_path.read_text())
    state = C.full_snapshot(root)
    snap["ignore_state"], snap["ignored"] = state["ignore_state"], state["ignored"]
    snap_path.write_text(json.dumps(snap) + "\n")
    code, out = go()
    assert (code, out["verdict"]) == (0, "PASS"), out
    subprocess.run(["git", "-C", str(root), "update-index", "--skip-worktree", "notes.txt"], check=True)
    code, out = go()
    assert code != 0 and out["verdict"] != "PASS" and any("index flags" in s for s in out["inconclusive"]), out


@pytest.mark.parametrize("route", ["env", "config"])
def test_b179_5_the_live_check_names_a_change_in_the_selected_working_tree(run, monkeypatch, route):
    """B179 finding 5 (REVW9's live falsifier). Under a fixed GIT_WORK_TREE or core.worktree naming another tree, a
    clean run is PASS; a change to that tree's `.gitignore` makes it INCONCLUSIVE naming `.gitignore`. On stage C2a2
    the supplied folder was walked and the run was PASS."""
    import shutil
    go, root, tmp_path = run
    actual = tmp_path / "selected-tree"
    shutil.copytree(root, actual, ignore=shutil.ignore_patterns(".git"))
    if route == "env":
        monkeypatch.setenv("GIT_WORK_TREE", str(actual))
    else:
        subprocess.run(["git", "-C", str(root), "config", "core.worktree", str(actual)], check=True)
    rule = actual / ".gitignore"
    rule.write_text(rule.read_text() + "marker.txt\n")
    snap_path = tmp_path / "snap.json"
    snap = json.loads(snap_path.read_text())
    state = C.full_snapshot(root)
    snap["ignore_state"], snap["ignored"] = state["ignore_state"], state["ignored"]
    snap["dirty"][".gitignore"] = state["dirty"][".gitignore"]
    snap_path.write_text(json.dumps(snap) + "\n")
    code, out = go()
    assert (code, out["verdict"]) == (0, "PASS"), out
    rule.write_text(rule.read_text() + "# changed\n")
    code, out = go()
    assert code != 0 and out["verdict"] != "PASS" and any(".gitignore" in s for s in out["inconclusive"]), out


# --- REVW9's B180 read of stage C2a2: F reads only the summary's ids, accounted for --------------------------------

@pytest.mark.parametrize("output", [
    "FAILED tests/t.py::new - printed by a test\n=== short test summary info ===\nFAILED tests/t.py::old\n"
    "2 failed, 1 passed in 0.1s",                                     # one failure unlisted (advisory A)
    "=== short test summary info ===\nFAILED tests/t.py::t[same] - alpha[tail] - boom\n1 failed, 1 passed in 0.1s"])
def test_b180_1_f_is_unavailable_when_the_failing_ids_are_not_all_known(tmp_path, output):
    """B180 finding 1 at F (after_run_check.py:370-376; advisory A). A run reporting two failures whose summary lists
    one (a printed line outside it does not count), or an id whose end is not unique, makes F unavailable, never an
    empty list of new failures. On stage C2a2 F checked no count and read the shorter prefix."""
    base = tmp_path / "baseline_record.json"
    _bound_baseline(base, ["tests/t.py::old", "tests/t.py::t[same]"])
    new, why = _regressions(_suite_transcript(tmp_path, [output]), base)
    assert new == [] and why and "not all known" in why, (new, why)


# --- REVW9's B183 read of stage E2i10: a failed HEAD read is never "absent" ----------------------------------------

def test_b183_1_a_failed_head_read_in_check_a_is_inconclusive(run, monkeypatch):
    """B183 finding 1 with FWK-OVSR5's E2i10 advisory (5). A clean run is PASS; when the HEAD read of an applied file
    fails (here the selected index is a directory), check A reports it unavailable and the run is not PASS. On stage
    E2i10 check A skipped the comparison on any failed read."""
    go, root, tmp_path = run
    code, out = go()
    assert (code, out["verdict"]) == (0, "PASS"), out

    def failed(*a, **k):
        raise C.CI.InspectionFailed("the index git reads is not a regular file")
    monkeypatch.setattr(C.CI, "git_blob_at", failed)
    code, out = go()
    assert code != 0 and out["verdict"] != "PASS" and any(s.startswith("A: ") for s in out["inconclusive"]), out


# --- E2i13: REVW9's B189 read (a committed symbolic link is not file content) ----------------------------------

@pytest.mark.parametrize("case", ["release", "keep", "merge", "protected-A"])
def test_b189_1_a_committed_symbolic_link_does_not_pass_as_file_bytes(run, case):
    """B189 finding 1 (REVW9 `reviewer_e2i12_probes.py::test_after_run_refuses_a_committed_symbolic_link_as_regular_
    file_bytes[…]`, without its direct `git_blob_at` observation, which now raises by design): the working file stays
    a regular file with the right bytes; HEAD holds a mode-120000 entry whose target text is those bytes. On E2i12
    release, KEEP, MERGE and A read PASS."""
    import hashlib
    go, root, tmp_path = run
    digest = hashlib.sha256(b"release x\n").hexdigest()
    items = None
    if case == "keep":
        items = [{"path": "scripts/x.py", "op": "hold", "kind": "no-source", "pre": digest}]
    if case == "merge":
        items = [{"path": "scripts/x.py", "op": "hold", "kind": "authored", "authored_lines": 1,
                  "authored_ids": [hashlib.sha256(b"release x").hexdigest()]}]
    code, out = go(packet_items=items)
    assert (code, out["verdict"]) == (0, "PASS"), out
    path = SKILL if case == "protected-A" else "scripts/x.py"
    blob = subprocess.run(["git", "-C", str(root), "hash-object", "-w", "--stdin"], input=(root / path).read_bytes(),
                          capture_output=True, check=True).stdout.decode().strip()
    for args in (["update-index", "--cacheinfo", f"120000,{blob},{path}"], ["commit", "-qm", "link entry"]):
        subprocess.run(["git", "-C", str(root), "-c", "user.name=t", "-c", "user.email=t@t", *args], check=True,
                       capture_output=True)
    assert (root / path).is_file() and not (root / path).is_symlink()
    code, out = go(packet_items=items)
    assert out["verdict"] != "PASS" and any("120000" in x for x in out["inconclusive"]), out


# --- E2i14 (FWK-OVSR5's E2i13 advisory (1)): the working-tree side, through its consumers ----------------------------

def test_e2i13_advisory_1_a_link_to_the_applied_bytes_fails_A(run, tmp_path):
    """A file the apply wrote, replaced during the run by a link to a file with the same bytes. Check A read the
    working tree through `is_file()`/`read_bytes()`, which follow the link, so the digest matched and A passed."""
    go, root, _ = run
    outside = tmp_path / "outside.md"
    outside.write_text("release\n")
    (root / SKILL).unlink()
    (root / SKILL).symlink_to(outside)
    code, out = go()
    assert code == 1 and any(x.startswith(f"{SKILL}: working tree link") for x in out["A"]), out["A"]


def test_e2i13_advisory_1_a_pre_dirty_file_swapped_for_a_link_to_its_bytes_fails_E(run, tmp_path):
    """A file modified before the launch, replaced during the run by a link to a file with its pre-run bytes. Check E
    compared digests through the link, so the swap read as unchanged."""
    go, root, _ = run
    outside = tmp_path / "outside.txt"
    outside.write_text((root / "notes.txt").read_text())
    (root / "notes.txt").unlink()
    (root / "notes.txt").symlink_to(outside)
    code, out = go()
    assert code == 1 and "notes.txt: modified before the run, and changed during it" in out["E"], out["E"]


# --- E2i15: FWK-OVSR6's E2i14 pre-read 1 and 3 (reproduced), through their consumers -------------------------------

def test_e2i14_preread_1_a_linked_parent_folder_of_an_applied_file_fails_A(run, tmp_path):
    """The folder holding a file the apply wrote, replaced during the run by a link to a folder whose file has the
    same bytes. On E2i14 check A guarded the leaf only, walked through the linked folder, and passed."""
    go, root, _ = run
    outside = tmp_path / "outside_skill"
    outside.mkdir()
    (outside / "SKILL.md").write_text("release\n")
    import shutil
    shutil.rmtree(root / ".claude" / "skills" / "aget-x")
    (root / ".claude" / "skills" / "aget-x").symlink_to(outside)
    code, out = go()
    # changed at C2a11 (labelled; FWK-OVSR6's C2a10r pre-read): a reading not taken is INCONCLUSIVE, never A passed
    assert code != 0 and not out["A"] and any(x.startswith(f"A: {SKILL}: the working tree could not be read")
                                              for x in out["inconclusive"]), out


def test_e2i14_preread_3_a_merge_replaced_by_a_link_to_its_lines_fails_D(run, tmp_path):
    """FWK-OVSR6's E2i14 pre-read 3 (Codex #2, agy P4; reproduced 11:19): a MERGE item's file replaced by a link to
    a file holding the authored line read the line through the link: D empty, recorded as merged."""
    go, root, _ = run
    keep = hashlib.sha256(b"release x").hexdigest()
    item = {"path": "scripts/x.py", "op": "hold", "kind": "authored", "authored_lines": 1, "staged": "s",
            "authored_ids": [keep]}
    outside = tmp_path / "outside_x.py"
    outside.write_text("release x\n")
    (root / "scripts" / "x.py").unlink()
    (root / "scripts" / "x.py").symlink_to(outside)
    code, out = go(packet_items=[item])
    assert code == 1 and any("holds a link, not a regular file" in x for x in out["D"]), out["D"]


# --- E2i16: FWK-OVSR6's E2i15 pre-read 3 (reproduced): a reading that cannot be taken equals nothing ----------------

def test_e2i15_preread_3_a_pre_dirty_path_behind_a_linked_folder_is_inconclusive_not_unchanged(run, tmp_path):
    """A path modified before the launch whose folder is a link (so the snapshot read it as unreachable), with the
    bytes behind the link changed during the run. On E2i15 the two "unreachable" readings compared equal and E saw
    no change; now a reading that cannot be taken is INCONCLUSIVE at the comparison."""
    go, root, tmp = run
    hidden = tmp_path / "hidden"
    hidden.mkdir()
    (hidden / "n.txt").write_text("before\n")
    (root / "d").symlink_to(hidden)
    snap = tmp / "snap.json"
    doc = json.loads(snap.read_text())
    doc["dirty"]["d/n.txt"] = C.tree_print(root, "d/n.txt")
    assert doc["dirty"]["d/n.txt"].startswith("unreachable")
    snap.write_text(json.dumps(doc))
    (hidden / "n.txt").write_text("changed behind the link\n")
    code, out = go()
    assert any(x.startswith("E: d/n.txt: modified before the run, and not readable") for x in out["inconclusive"]), \
        out["inconclusive"]


def test_e2i16_preread_2_two_unreadable_settings_snapshots_are_inconclusive_not_unchanged(run, tmp_path, monkeypatch):
    """FWK-OVSR6's E2i16 pre-read 2: the settings watcher's `UNREADABLE` marker was not one of the spellings `unread()`
    knew, so a rule set unreadable before and after the run compared equal and B passed."""
    go, root, tmp = run
    snap = tmp / "snap.json"
    doc = json.loads(snap.read_text())
    role = sorted(doc["rules"])[0]
    doc["rules"][role] = "UNREADABLE"
    snap.write_text(json.dumps(doc))
    real = C.W.rules
    monkeypatch.setattr(C.W, "rules", lambda path, root_: "UNREADABLE" if path == C.W.files_for(root_)[role]
                        else real(path, root_))
    code, out = go()
    assert any(x.startswith(f"B: settings {role}: the rule set could not be read") for x in out["inconclusive"]), out


def test_c2a10_preread_8_a_kept_item_that_cannot_be_read_is_inconclusive_not_a_failure(run, tmp_path):
    """FWK-OVSR6's C2a10 pre-read 8: a KEEP item behind a linked folder read as unreachable and failed D ("kept, but
    the working tree holds unreacha…"); a reading not taken is INCONCLUSIVE, not a judged failure."""
    go, root, _ = run
    (tmp_path / "elsewhere").mkdir()
    (root / "lnk").symlink_to(tmp_path / "elsewhere")
    code, out = go(packet_items=[{"path": "lnk/m.py", "op": "hold", "kind": "no-source", "pre": "absent"}])
    assert not [x for x in out["D"] if x.startswith("lnk/m.py")], out["D"]
    assert any(x.startswith("D: lnk/m.py: the working tree could not be read") for x in out["inconclusive"]), out


# --- R2-T11 (C2b): after-run inputs a run did not bind are INCONCLUSIVE ------------------------------------------

def test_r2_t11_a_migrating_member_judged_without_its_suite_command_is_inconclusive(run):
    """R2-T11 (S-172). The packet's receiver is a migration (no `track-skills` mode), and the check is run without
    --suite-cmd: F was never computed, so a regression could not be seen. Before C2b: PASS."""
    go, _, _ = run
    code, out = go(drop=["--suite-cmd", "--baseline-record"])
    assert out["verdict"] == "INCONCLUSIVE" and any("without --suite-cmd" in x for x in out["inconclusive"]), out


@pytest.mark.parametrize("case", ["inconclusive", "other_member", "other_head", "not_complete", "not_sealed_one"])
def test_r2_t11_a_baseline_that_is_not_bound_supplies_no_exemption(run, case):
    """R2-T11 (S-174, S-327, S-328). The session's suite run fails one test the baseline lists, so an unbound
    baseline would exempt it. Each case is INCONCLUSIVE naming the baseline: an INCONCLUSIVE baseline (closed at B3,
    B143 finding 6: a control here), one for another member, one for another HEAD than the session started from, one
    whose output is not marked complete, and one that is not the baseline the launch sealed (--baseline-slot-sha256).
    Before C2b the last four exempted the failure and read PASS (the sealed-digest case is G's concern too; G reads
    the slot file, F read the record)."""
    go, root, tmp = run
    f = tmp / "fixture_baseline_record.json"
    doc = json.loads(f.read_text())
    doc["failures"] = ["tests/test_old.py::t"]
    doc["sha256"] = "s" * 64
    extra = []
    if case == "inconclusive":
        doc["verdict"] = "INCONCLUSIVE"
    elif case == "other_member":
        doc["aget"] = "b"
    elif case == "other_head":
        doc["head"] = "0" * 40
    elif case == "not_complete":
        doc["output_complete"] = False
    else:
        extra = ["--baseline-slot-sha256", "t" * 64]
    produce(f, "baseline", doc)
    events = [tool_use("9", "Bash", {"command": "python3 -m pytest -q"}),
              tool_result("9", content="FAILED tests/test_old.py::t\n1 failed, 1 passed in 0.01s")]
    code, out = go(extra_events=events, extra_args=extra)
    if case == "not_sealed_one":
        out["inconclusive"] = [x for x in out["inconclusive"] if not x.startswith("G")]
    assert out["verdict"] == "INCONCLUSIVE" and any(x.startswith("F: baseline record") for x in out["inconclusive"]), out


def test_r2_t11_positive_control_a_bound_baseline_exempts_its_failure(run):
    """R2-T11 positive control: the same failure, listed by a bound baseline, is exempted (PASS)."""
    go, root, tmp = run
    f = tmp / "fixture_baseline_record.json"
    doc = json.loads(f.read_text())
    doc["failures"] = ["tests/test_old.py::t"]
    produce(f, "baseline", doc)            # C2c (R2-T17): the current run of the baseline
    # C2a7 (changed at the C2b port onto E2i14, labelled): the later run carries its kit report, as the plugin writes it
    rpt, tok, (text,) = _kit_report().reported(tmp / "suite_report_2.jsonl", [(
        "=== short test summary info ===\nFAILED tests/test_old.py::t\n1 failed, 1 passed in 0.01s",
        ["tests/test_old.py::t"])])
    events = [tool_use("9", "Bash", {"command": "python3 -m pytest -q"}), tool_result("9", content=text)]
    code, out = go(extra_events=events, extra_args=["--suite-report", str(rpt), "--suite-report-token", tok])
    assert (code, out["verdict"]) == (0, "PASS"), out


@pytest.mark.parametrize("case", ["starts_late", "stops_early", "no_window"])
def test_r2_t11_a_watch_that_does_not_cover_the_session_is_inconclusive(run, case):
    """R2-T11 (S-176, S-180). The watch log is complete and gap-free but does not cover the session's window (the
    transcript's stamps, 101-107): it starts at 103, or stops at 105; or the window is unknown (no stamps and no
    --session-window). Before C2b the check never compared the watch with the session: PASS."""
    go, root, tmp = run
    w = tmp / f"w_{case}.jsonl"
    start, stop = {"starts_late": (103.0, 108.0), "stops_early": (100.0, 105.0), "no_window": (100.0, 108.0)}[case]
    w.write_text("\n".join(json.dumps(e) for e in [
        {"event": "start", "t": start, "heartbeat": 5, "interval": 0.5, "files": {}, "stat_tracked": True},
        {"event": "heartbeat", "t": (start + stop) / 2}, {"event": "stop", "t": stop}]) + "\n")
    if case == "no_window":
        t = tmp / "t.jsonl"
        rows = [json.loads(x) for x in t.read_text().splitlines() if x.strip()]
        t.write_text("\n".join(json.dumps({k: v for k, v in r.items() if k != "timestamp"}) for r in rows) + "\n")
    code, out = go(watch=w)
    want = "window is unknown" if case == "no_window" else "does not cover the requested window"
    assert out["verdict"] == "INCONCLUSIVE" and any(want in x for x in out["inconclusive"]), out


def test_r2_t11_the_session_window_option_takes_precedence(run):
    """R2-T11: --session-window (what launch_batch passes) is the window; a watch covering it passes, one starting
    after its start reads INCONCLUSIVE."""
    go, _, _ = run
    code, out = go(extra_args=["--session-window", "100.5", "107.5"])
    assert (code, out["verdict"]) == (0, "PASS"), out
    code, out = go(extra_args=["--session-window", "99", "107.5"])
    assert out["verdict"] == "INCONCLUSIVE" and any("requested window" in x for x in out["inconclusive"]), out


# --- C2a12: FWK-OVSR6's C2a11 pre-read 6 (reproduced): a reading not taken is INCONCLUSIVE, never FAIL ----------------

def test_c2a12_preread_6_a_non_regular_protected_path_is_inconclusive_not_fail(run, tmp_path):
    """Check A scored a protected path that is no longer a regular file (`tree_print`: `not a regular file (mode …)`,
    which `non_reading` reads as a reading not taken) as FAIL. It is INCONCLUSIVE, as an unreachable one is."""
    go, root, _ = run
    (root / SKILL).unlink()
    os.mkfifo(root / SKILL)
    code, out = go()
    assert code != 0 and not out["A"], out["A"]
    assert any(x.startswith(f"A: {SKILL}: the working tree could not be read (not a regular file")
               for x in out["inconclusive"]), out["inconclusive"]


class _Done(Exception):
    pass


@pytest.mark.parametrize("seq, verdict", [
    ([{"a"}, "UNREADABLE", {"a"}], "INCONCLUSIVE"),          # a reading not taken, back unchanged: not a change
    ([{"a"}, "UNREADABLE"], "INCONCLUSIVE"),                 # ends unreadable
    ([{"a"}, "UNREADABLE", {"a", "b"}], "FAIL"),             # a rule added while unreadable is still a change
    ([{"a"}, {"a", "b"}], "FAIL"),
])
def test_c2a12_preread_6_the_settings_watch_reads_an_unreadable_file_as_not_taken(monkeypatch, seq, verdict):
    """The settings watch emitted a change event for a file turning unreadable (and one with every rule `added` when it
    read again), so a reading not taken scored FAIL. It is now INCONCLUSIVE; on reading again the file is compared
    with its last readable rule set, so a rule added meanwhile still FAILs."""
    W = C.W
    it = iter(seq[1:])

    def rules(p, root=None):
        try:
            return next(it)
        except StopIteration:
            raise _Done
    monkeypatch.setattr(W, "rules", rules)
    monkeypatch.setattr(W.time, "sleep", lambda s: None)
    log = []
    monkeypatch.setattr(W, "_emit", lambda fh, e: log.append({**e, "t": len(log)}))
    with pytest.raises(_Done):
        W._loop(None, {"project": "p"}, "/r", {"project": seq[0]}, {}, 0, None, 10 ** 9)
    events = [{"event": "start", "t": -1, "heartbeat": 10 ** 9, "interval": 0, "stat_tracked": [], "files": {}},
              *log, {"event": "stop", "t": len(log)}]
    got = W.verdict(events)
    assert got["verdict"] == verdict, (got, log)


def test_b195_4_an_applied_file_turned_into_a_folder_is_inconclusive_in_A(run):
    """B195 finding 4 (REVW9's falsifier): an applied file that became a directory scored `working tree not a re…`
    as FAIL with no inconclusive reason. A kind-only observation is a reading not taken."""
    go, root, _ = run
    (root / SKILL).unlink()
    (root / SKILL).mkdir()
    code, out = go()
    assert code != 0 and not out["A"], out["A"]
    assert any(x.startswith(f"A: {SKILL}: the working tree could not be read (not a regular file")
               for x in out["inconclusive"]), out["inconclusive"]


def test_b195_4_a_settings_file_turned_into_a_folder_is_inconclusive_in_B(run, hooks_file):
    """B195 finding 4: the --settings adapter tested only `unreachable`/`unreadable` prefixes, so a kind-only
    observation was a digest mismatch (FAIL). It is now INCONCLUSIVE through the shared `non_reading` predicate."""
    go, _, _ = run
    hooks_file[0].unlink()
    hooks_file[0].mkdir()
    code, out = go(route="restricted-hooks", settings=hooks_file)
    assert not any("--settings file" in x for x in out["B"]), out["B"]
    assert any(x.startswith("B: --settings file") and "could not be read" in x for x in out["inconclusive"]), out


def test_c2a12_preread_the_settings_watch_reads_a_fifo_or_a_denied_stat_as_unreadable(tmp_path):
    """FWK-OVSR6's C2a12 pre-read (MEDIUM, reproduced): a FIFO at a settings path hung `rules()` (no UNREADABLE, no
    exception), and EACCES on the parent folder read as absent (None), a false rule removal. Both are UNREADABLE; a
    missing file stays absent and a JSON value that is not an object is UNREADABLE."""
    import threading
    W = C.W
    fifo = tmp_path / "settings.json"
    os.mkfifo(fifo)
    got = []
    t = threading.Thread(target=lambda: got.append(W.rules(str(fifo))), daemon=True)
    t.start()
    t.join(5)
    hung = t.is_alive()
    if hung:                            # unblock the reader on the old code, then fail
        fd = os.open(fifo, os.O_WRONLY | os.O_NONBLOCK)
        os.close(fd)
        t.join(5)
    assert not hung and got == ["UNREADABLE"], (hung, got)
    shut = tmp_path / "shut"
    shut.mkdir()
    (shut / "settings.json").write_text('{"permissions": {"allow": ["Bash(ls:*)"]}}')
    shut.chmod(0)
    try:
        assert W.rules(str(shut / "settings.json")) == "UNREADABLE"
    finally:
        shut.chmod(0o755)
    assert W.rules(str(tmp_path / "absent.json")) is None
    (tmp_path / "list.json").write_text("[1]")
    assert W.rules(str(tmp_path / "list.json")) == "UNREADABLE"


def test_r2_t17_f_reads_only_the_current_baseline_run(run):
    """R2-T17 (S-172, S-174). The session's suite run fails a test the baseline lists. A bound baseline record copied
    from another folder (no run recorded beside it) exempts nothing: F reads INCONCLUSIVE. A later baseline run that
    started and did not finish also leaves no exemption. Before C2c F read the record as a plain file and exempted the
    failure (PASS)."""
    go, root, tmp = run
    f = tmp / "fixture_baseline_record.json"
    doc = json.loads(f.read_text())
    doc.pop("binding", None)
    doc["failures"] = ["tests/test_old.py::t"]
    other = tmp / "other"
    other.mkdir()
    produce(other / "b.json", "baseline", doc)
    f.write_bytes((other / "b.json").read_bytes())
    # C2a7 (changed at the C2c port onto C2a10, labelled): the later run carries its kit report, as the plugin writes it
    rpt, tok, (text,) = _kit_report().reported(tmp / "suite_report_2.jsonl", [(
        "=== short test summary info ===\nFAILED tests/test_old.py::t\n1 failed, 1 passed in 0.01s",
        ["tests/test_old.py::t"])])
    rep = ["--suite-report", str(rpt), "--suite-report-token", tok]
    events = [tool_use("9", "Bash", {"command": "python3 -m pytest -q"}), tool_result("9", content=text)]
    code, out = go(extra_events=events, extra_args=rep)
    assert out["verdict"] == "INCONCLUSIVE" and any(x.startswith("F: baseline record") for x in out["inconclusive"]), out
    produce(f, "baseline", doc)
    code, out = go(extra_args=rep)
    assert (code, out["verdict"]) == (0, "PASS"), out                       # control: the current run exempts
    C.RBND.start_run("baseline", f, aget="a", recorded_by="invoker")         # a later run, never finished
    code, out = go(extra_args=rep)
    assert out["verdict"] == "INCONCLUSIVE" and any("not the current run" in x for x in out["inconclusive"]), out


def test_r2_t17_after_run_a_reads_only_the_finished_current_apply_receipt(run):
    """R2-T17 (S-164, S-171). The fixture's receipt, rewritten as a killed apply run leaves it (its run started, its
    bytes written, no FINISHED row), is not read: A reads INCONCLUSIVE and exempts nothing. Before C2d A read the
    plain file and passed."""
    go, root, tmp = run
    f = tmp / "receipt.json"
    doc = json.loads(f.read_text())
    doc.pop("binding", None)
    C.RBND.start_run("apply_protected", f)
    C.RBND.atomic_write(f, (json.dumps(doc) + "\n").encode())
    code, out = go()
    assert out["verdict"] == "INCONCLUSIVE" and any(x.startswith("A: apply receipt") and "not the current run" in x
                                                    for x in out["inconclusive"]), out


def test_d2_r3_a_held_protected_file_kept_as_it_was_is_compared_by_identity(run):
    """D2 (R3, DESIGN's apply-receipt clause): the receipt named held paths only, so after-run A never compared a
    held protected file the member was to keep as it was. The receipt now records each held path's op, kind and
    `pre`; A compares a `pre`-kept one by identity. Control: the file as listed (absent) passes A."""
    go, root, tmp = run
    receipt = tmp / "receipt.json"
    held = {"path": "scripts/m.py", "op": "hold", "kind": "no-source", "pre": "absent"}
    produce(receipt, "apply_protected", {"mode": "apply", "agets": [{"aget": "a", "result": "APPLIED",
                                         "location": str(root), "held": [held],
                                         "files": [{"path": SKILL, "post": sha("release\n"), "ok": True}]}]})
    code, out = go()
    assert not any("scripts/m.py" in x for x in out["A"]), out["A"]
    (root / "scripts" / "m.py").write_text("changed by the session\n")
    code, out = go()
    assert code == 1 and any("scripts/m.py" in x and "held as it was" in x for x in out["A"]), out["A"]
