"""C2a7, B185 finding 1 (REVW9's structural ruling): the failing ids every consumer compares come from a kit-owned
result source (the kit's pytest report plugin), never from pytest's display text. Native pytest throughout."""
from _kit_report import requires_monitoring

import ast
import importlib.util
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "scripts/migration_kit"


def load(name, folder=BATCH):
    spec = importlib.util.spec_from_file_location(name, folder / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    sys.path.insert(0, str(BATCH))
    spec.loader.exec_module(mod)
    return mod


RB = load("result_binding")
LB = load("launch_batch")
A = load("after_run_check")


def produce(path, step, doc):
    """C2c (R2-T16 (c), R2-T17; changed at the C2c port onto C2a10, labelled): write `doc` as its producer does, a
    run recorded first and the result bound to it. A record written by hand names no run and is not read."""
    doc = {k: v for k, v in doc.items() if k != "binding"}
    rid = A.RBND.start_run(step, path, aget=doc.get("aget"), recorded_by="invoker")
    A.RBND.write_result(step, path, doc, rid, binding={"aget": doc.get("aget"), "subject": doc.get("head")})
PYTEST = f"{sys.executable} -B -m pytest tests -q -rfE -p no:cacheprovider"


def g(loc, *a):
    return subprocess.run(["git", "-C", str(loc), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          check=True, capture_output=True, text=True).stdout.strip()


def member(tmp_path, files):
    root = tmp_path / "member"
    (root / "tests").mkdir(parents=True)
    for name, body in files.items():
        (root / "tests" / name).write_text(body)
    g(root, "init", "-q")
    g(root, "add", "-A")
    g(root, "commit", "-q", "-m", "c")
    return root


def native(root, cmd, env):
    import shlex
    p = subprocess.run(shlex.split(cmd), cwd=root, capture_output=True, text=True, env={**env, "COLUMNS": "80"})
    return p, p.stdout + p.stderr


def under_report(tmp_path, name="rep.jsonl", base=None):
    path = tmp_path / name
    token = RB.new_report(path)
    return path, token, RB.report_env(dict(os.environ if base is None else base), path, token)


def stream(text, cmd):
    """A session stream carrying one Bash call of `cmd` and its native output (the transport, not the result)."""
    return "\n".join(json.dumps(x) for x in (
        {"sessionId": "S", "message": {"content": [{"type": "tool_use", "id": "u1", "name": "Bash", "input": {"command": cmd}}]}},
        {"sessionId": "S", "message": {"content": [{"type": "tool_result", "tool_use_id": "u1", "content": text}]}})) + "\n"


def wide(tail):
    return ('def test_control():\n    pass\ndef scenario():\n    assert False, "synthetic failure"\n'
            f"globals()[{('test_synthetic' + 'x' * 110 + ' - ' + tail)!r}] = scenario\n")


@requires_monitoring
def test_b185_1_baseline_and_f_read_the_full_native_id_when_pytest_omits_the_message(tmp_path, monkeypatch):
    """B185 finding 1 (REVW9 `reviewer_c2a5_probes.py::test_baseline_and_f_refuse_a_full_native_id_when_pytest_omits_
    the_message[True]`): pytest at width 80 prints the whole id ending ` - alpha` and omits the message, so the text
    holds one ` - ` inside the id. The baseline producer (a real run_baseline, the session's pytest run natively under
    the environment the kit gives it) records the full id, and F reads the full ` - beta` id as new. On C2a6 the
    producer recorded the prefix and F returned ([], None)."""
    # This fixture needs width-based message omission; pytest disables it in CI.
    monkeypatch.delenv("CI", raising=False)
    monkeypatch.delenv("BUILD_NUMBER", raising=False)
    root = member(tmp_path, {"test_synthetic.py": wide("alpha")})
    prefix = "tests/test_synthetic.py::test_synthetic" + "x" * 110

    def session(cmd, cwd, env, timeout):          # the headless session: it runs the suite command, natively
        p, text = native(cwd, PYTEST, env)
        return subprocess.CompletedProcess(cmd, 0, stream(text, PYTEST), "")
    monkeypatch.setattr(LB, "run_grouped", session)
    pr = tmp_path / "packet-root"
    (pr / "baselines/a").mkdir(parents=True)
    r = {"aget": "a", "location": str(root), "head": g(root, "rev-parse", "HEAD"), "baseline_prompt": "synthetic",
         "suite_cmd": PYTEST, "settings": {"path": str(tmp_path / "settings.json")}}
    rec = LB.run_baseline(r, {"packet_root": str(pr), "baseline_cmd": PYTEST, "tools": [], "deny": []},
                          tmp_path / "evidence", tmp_path / "stage")
    assert rec["verdict"] == "RECORDED" and rec["failures"] == [prefix + " - alpha"], rec
    line = next(ln for ln in json.loads((tmp_path / "evidence/a/baseline_stream.jsonl").read_text().splitlines()[1])
                ["message"]["content"][0]["content"].splitlines() if ln.startswith("FAILED "))
    assert line.count(" - ") == 1, line                   # the display text is the ambiguous one
    (root / "tests/test_synthetic.py").write_text(wide("beta"))
    report, token, env = under_report(tmp_path, "session.jsonl")
    p, text = native(root, PYTEST, env)
    (tmp_path / "transcript.jsonl").write_text(stream(text, PYTEST))
    # C2b (R2-T11, changed, labelled): F binds the baseline to the member and the HEAD the session started from
    # C2c (R2-T17, changed, labelled): F reads the producer's own bound record, never the copy in the packet's slot
    new, why = A.suite_regressions(tmp_path / "transcript.jsonl", PYTEST, tmp_path / "evidence/a/baseline_record.json",
                                   "a", r["head"], report=report, token=token)
    assert (new, why) == ([prefix + " - beta"], None)


ODD = ("import pytest\n"
       "@pytest.mark.parametrize('v', ['a - b', 'x]y', 'tab\\there', 'é', 'a - b - c'], ids=lambda v: v)\n"
       "def test_p(v):\n    assert False\n"
       "def _f():\n    assert False\n"
       "globals()['test_nl\\nFAILED tests/test_odd.py::fake - x'] = _f\n"
       "globals()['test_dash - ' + 'z' * 120] = _f\n")
SIDE = ("import pytest\n"
        "def pytest_collection_modifyitems(items):\n"
        "    import os\n"
        "    with open(os.path.join(os.path.dirname(__file__), 'nodeids.txt'), 'w') as fh:\n"
        "        fh.write(repr([i.nodeid for i in items]))\n")


@requires_monitoring
def test_c2a7_the_report_ids_are_pytests_own_node_ids_byte_for_byte(tmp_path):
    """REVW9's ruling: faithful id encoding SHOWN. A conftest writes each collected item's `nodeid` (repr) before any
    test runs; the report's failing ids equal that population exactly, for ids holding ` - `, `]`, a tab, a non-ASCII
    character, a newline followed by text shaped like a summary line, and a width the message cannot fit."""
    root = member(tmp_path, {"test_odd.py": ODD, "conftest.py": SIDE})
    report, token, env = under_report(tmp_path)
    p, text = native(root, PYTEST, env)
    ids, why, events = RB.report_failures(report, token, text)
    want = ast.literal_eval((root / "tests/nodeids.txt").read_text())
    assert why is None and ids == sorted(want) and len(want) == 7, (why, ids, want)
    assert {e["when"] for e in events} == {"call"}
    assert RB.failing_ids(text)[1]                       # the display text cannot give them (contrast)


@pytest.mark.parametrize("case", ["no-line", "two-lines", "foreign-token", "added-event", "count-mismatch",
                                  "no-finish", "interrupted", "plugin-blocked", "no-report"])
def test_c2a7_an_incomplete_or_unreadable_record_gives_no_ids(tmp_path, case):
    """Every shortfall gives a reason and no ids (no exemption): the output names no invocation or two; a line of
    another run; an event appended after the run; a count line that disagrees with the report; an invocation that
    never finished (os._exit) or was interrupted; a run that did not load the plugin; no report at all."""
    body = "def test_a():\n    assert False\ndef test_b():\n    pass\n"
    if case == "no-finish":
        body += "def test_z():\n    import os\n    os._exit(0)\n"
    if case == "interrupted":
        body += "def test_z():\n    import pytest\n    pytest.exit('stop')\n"
    root = member(tmp_path, {"test_a.py": body})
    report, token, env = under_report(tmp_path)
    cmd = PYTEST + (" -p no:aget_kit_report" if case == "plugin-blocked" else "")
    p, text = native(root, cmd, env)
    if case == "no-line":
        text = "\n".join(ln for ln in text.splitlines() if not ln.startswith(RB.REPORT_MARK))
    if case == "two-lines":
        text = f"{RB.REPORT_MARK}pytest {'0' * 32}\n" + text
    if case == "foreign-token":
        with open(report, "a") as fh:
            fh.write(json.dumps({"rec": "event", "token": "other", "inv": "x"}) + "\n")
    if case == "added-event":
        inv = text.split(RB.REPORT_MARK + "pytest ")[1].split()[0]
        with open(report, "a") as fh:
            fh.write(json.dumps({"rec": "event", "token": token, "inv": inv, "nodeid": "tests/test_a.py::test_b",
                                 "when": "call", "outcome": "failed"}) + "\n")
    if case == "count-mismatch":
        text = text.replace("1 failed, 1 passed", "2 failed")
    ids, why, _ = RB.report_failures(None if case == "no-report" else report, token, text)
    assert ids == [] and why, (case, text[-400:])


@requires_monitoring
def test_c2a7_a_complete_clean_run_is_complete_with_no_ids(tmp_path):
    root = member(tmp_path, {"test_a.py": "def test_a():\n    pass\n"})
    report, token, env = under_report(tmp_path)
    p, text = native(root, PYTEST, env)
    assert p.returncode == 0 and RB.report_failures(report, token, text) == ([], None, [])


NESTED = ("import os, subprocess, sys\n"
          "def test_env_is_the_members():\n"
          "    assert os.environ.get('PYTEST_ADDOPTS') == '--strict-markers'\n"
          "    assert os.environ.get('PYTHONPATH') == 'member-path'\n"
          "    assert not [k for k in os.environ if k.startswith('AGET_KIT_')]\n"
          "def test_nested_pytest_writes_nothing(tmp_path):\n"
          "    (tmp_path / 'test_inner.py').write_text('def test_inner():\\n    assert False\\n')\n"
          "    p = subprocess.run([sys.executable, '-m', 'pytest', '-q', '-p', 'no:cacheprovider', str(tmp_path)],\n"
          "                       capture_output=True, text=True)\n"
          "    assert p.returncode == 1 and 'aget-kit-report' not in p.stdout\n")


@requires_monitoring
def test_c2a7_member_code_sees_its_own_environment_and_a_nested_pytest_writes_nothing(tmp_path):
    """The plugin puts the member's PYTEST_ADDOPTS and PYTHONPATH back and removes the kit's variables before any
    member code runs, so a pytest a test starts neither loads the plugin nor adds an invocation or a failure."""
    root = member(tmp_path, {"test_n.py": NESTED})
    report, token, env = under_report(tmp_path, base={**os.environ, "PYTEST_ADDOPTS": "--strict-markers",
                                                      "PYTHONPATH": "member-path"})
    p, text = native(root, PYTEST, env)
    assert RB.report_failures(report, token, text) == ([], None, []), text[-800:]
    assert sum(1 for ln in report.read_text().splitlines() if json.loads(ln)["rec"] == "start") == 1



def _wit(report):
    """C2c (labelled): a hand-written baseline beside a native run records that run's own selection witness (a baseline
    with no witness gives no policy and is refused)."""
    for ln in reversed(Path(report).read_text(errors="replace").splitlines()):
        try:
            r = json.loads(ln)
        except ValueError:
            continue
        if isinstance(r, dict) and r.get("rec") == "finish":
            return r.get("selection") or {}
    return {}

RUNNER = BATCH / "run_suite_parallel.py"


@pytest.mark.parametrize("crash", [pytest.param(False, marks=requires_monitoring), True])
def test_c2a7_the_parallel_runner_names_one_finished_invocation_per_file(tmp_path, crash):
    """run_suite_parallel's record lists one invocation per test file it started; the full wide id is read from the
    report; a file whose pytest dies before its summary (os._exit) leaves the whole run not complete."""
    files = {"test_a.py": wide("alpha"), "test_b.py": "def test_b():\n    pass\n"}
    if crash:
        files["test_c.py"] = "def test_c():\n    import os\n    os._exit(0)\n"
    root = member(tmp_path, files)
    report, token, env = under_report(tmp_path)
    p, text = native(root, f"{sys.executable} {RUNNER}", env)
    ids, why, _ = RB.report_failures(report, token, text)
    if crash:
        assert ids == [] and why, text[-600:]
    else:
        assert why is None and ids == ["tests/test_a.py::test_synthetic" + "x" * 110 + " - alpha"], (why, text[-600:])


def test_c2a7_ids_unknown_is_read_when_no_failure_is_counted():
    """FWK-OVSR5's C2a5 advisory (1), reproduced: an IDS-UNKNOWN line with a count of 0 failures read ([], None)."""
    text = "=== short test summary info ===\nIDS-UNKNOWN tests/test_x.py: unreadable\n10 passed in 0.1s\n"
    assert RB.summary_section(text)[3] and RB.failing_ids(text)[1]


@requires_monitoring
def test_c2a7_b8a_pass_needs_a_complete_result(tmp_path):
    """FWK-OVSR5's C2a5 advisory (2): B8a's PASS read only the exit status and the (empty) failure list. A suite that
    exits 0 with no kit result (here the member's command blocks the plugin) is INCONCLUSIVE, not PASS."""
    S = load("suite_at_commit")
    root = member(tmp_path, {"test_x.py": "def test_a():\n    pass\n"})
    ok = S.run(root, "a", g(root, "rev-parse", "HEAD"), PYTEST, work=tmp_path / "w")
    assert ok["verdict"] == "PASS" and ok["failures_complete"] is True, ok
    rec = S.run(root, "a", g(root, "rev-parse", "HEAD"), PYTEST + " -p no:aget_kit_report", work=tmp_path / "w")
    assert rec["verdict"] == "INCONCLUSIVE" and rec["failures_complete"] is False, rec


@requires_monitoring
def test_c2a7_a_confirmation_candidate_that_did_not_run_is_not_called_passed(tmp_path):
    """The confirmation run calls a candidate passed at HEAD only when the report shows its test phase passed."""
    root = member(tmp_path, {"test_x.py": "def test_real():\n    assert False\ndef test_ok():\n    pass\n"})
    head = g(root, "rev-parse", "HEAD")
    still, passed, why = A.confirm_at_head(root, "seat", ["tests/test_x.py::test_real", "tests/test_x.py::test_ok"],
                                           [], tmp_path / "work", head)
    assert (still, passed, why) == (["tests/test_x.py::test_real"], ["tests/test_x.py::test_ok"], None)
    still, passed, why = A.confirm_at_head(root, "seat", ["tests/test_x.py::test_gone"], [], tmp_path / "work2", head)
    assert passed == [] and why, (still, passed, why)


CONSUMERS = {"launch_batch.py": "RBND.report_failures(report, token, out, policy=\"baseline\", approved=approved)",  # C2a11, F4 (labelled)
             "after_run_check.py": "RBND.report_failures(report, token, text",
             # C2a10 (B192 finding 1, changed, labelled): the two callers that run pytest pass its process exit
             "suite_at_commit.py": "RBND.report_failures(report, token, out,",
             "rehearse_repair.py": "RBND.report_failures(report, token, out,"}


def test_c2a7_census_every_consumer_reads_the_kit_report_and_its_completeness():
    """By population: the baseline producer, F and the confirmation run (after_run_check, twice), B8a and the repair
    rehearsal read failing ids only through result_binding.report_failures, and no kit module reads them from display
    text (failing_ids) any longer; each consumer's reason gates its success value."""
    users = {p.name: p.read_text() for p in BATCH.glob("*.py")}
    assert {n for n, t in users.items() if "RBND.failing_ids(" in t} == {"run_suite_parallel.py"}   # display only
    for name, call in CONSUMERS.items():
        assert call in users[name], name
    assert users["after_run_check.py"].count("RBND.report_failures(") == 2
    sac = users["suite_at_commit.py"]
    assert 'if ok and rec["failures_complete"] is not True' in sac
    assert '"complete": summary is not None and not unknown' in users["launch_batch.py"]
    assert "if unknown:" in users["after_run_check.py"] and "if ran and unknown:" in users["rehearse_repair.py"]


KINDS = {
    "setup-teardown": ("import pytest\n@pytest.fixture\ndef f():\n    yield\n    raise RuntimeError('td')\n"
                       "@pytest.fixture\ndef s():\n    raise RuntimeError('su')\n"
                       "def test_t(f):\n    assert False\ndef test_s(s):\n    pass\ndef test_ok():\n    pass\n",
                       "", 0, ["tests/test_k.py::test_s", "tests/test_k.py::test_t"]),
    "strict-xpass": ("import pytest\n@pytest.mark.xfail(strict=True)\ndef test_x():\n    pass\n"
                     "@pytest.mark.xfail\ndef test_xf():\n    assert False\n@pytest.mark.skip\ndef test_sk():\n    pass\n",
                     "", 0, ["tests/test_k.py::test_x"]),
    "collection-continued": ("import nonexistent_module_c2a7\n", " --continue-on-collection-errors", 0,
                             ["tests/test_k.py"]),
    "collection-stopped": ("import nonexistent_module_c2a7\n", "", 1, []),
}


@pytest.mark.parametrize("kind", [pytest.param(v, marks=requires_monitoring) if v in ['collection-continued', 'setup-teardown', 'strict-xpass'] else v
                                  for v in sorted(KINDS)])
def test_c2a7_native_failure_kinds_tally_with_the_count_line(tmp_path, kind):
    """The count cross-check on native pytest: setup and teardown errors (two events for one failing test, one id),
    strict XPASS (failed), plain xfail and skip (not failures), a collection error with
    --continue-on-collection-errors (the file's id, exit 1). A run that stops at a collection error exits 2, having run
    no tests: not a complete result (an admission cost put to REVW9)."""
    body, flag, incomplete, ids = KINDS[kind]
    root = member(tmp_path, {"test_k.py": body, "test_z.py": "def test_z():\n    pass\n"})
    report, token, env = under_report(tmp_path)
    p, text = native(root, PYTEST + flag, env)
    got, why, events = RB.report_failures(report, token, text)
    if incomplete:
        assert p.returncode == 2 and got == [] and "exit 2" in why, (why, text[-500:])
    else:
        assert why is None and got == ids, (why, got, text[-800:])
    if kind == "setup-teardown":
        assert sorted((e["nodeid"][-6:], e["when"]) for e in events) == [
            ("test_s", "setup"), ("test_t", "call"), ("test_t", "teardown")]


# --- C2a8: REVW9's B188 read (report grammar, report storage) and FWK-OVSR5's C2a7 advisory ----------------------

def _clean_run(tmp_path, body="def test_a():\n    assert False\ndef test_b():\n    pass\n"):
    root = member(tmp_path, {"test_a.py": body})
    report, token, env = under_report(tmp_path)
    p, text = native(root, PYTEST, env)
    assert RB.report_failures(report, token, text)[1] is None
    return report, token, text


def _rewrite(report, fn):
    rows = [json.loads(ln) for ln in report.read_text().splitlines()]
    report.write_bytes(fn(rows))


GRAMMAR = {
    "invalid-utf8": lambda rows: "".join(json.dumps(r) + "\n" for r in rows).replace(
        "test_a", "test_\udcffa").encode("utf-8", "surrogateescape"),
    "unknown-outcome": lambda rows: "".join(json.dumps({**r, "outcome": "weird"} if r.get("outcome") == "failed" else r)
                                            + "\n" for r in rows).encode(),
    "bool-exit": lambda rows: "".join(json.dumps({**r, "exit": False} if r["rec"] == "finish" else r) + "\n"
                                      for r in rows).encode(),
    "empty-nodeid": lambda rows: "".join(json.dumps({**r, "nodeid": ""} if r.get("outcome") == "failed" else r) + "\n"
                                         for r in rows).encode(),
    "string-events": lambda rows: "".join(json.dumps({**r, "events": str(r["events"])} if r["rec"] == "finish" else r)
                                          + "\n" for r in rows).encode(),
    "collect-passed": lambda rows: "".join(json.dumps(r) + "\n" for r in rows).encode() + b"",
}


@requires_monitoring
@pytest.mark.parametrize("case", sorted(GRAMMAR))
def test_b188_1_a_malformed_report_gives_no_ids(tmp_path, case):
    """B188 finding 1 (REVW9 `reviewer_c2a7_probes.py` grammar rows): invalid UTF-8 (decoded with replacement it
    invented an id), an outcome outside pytest's set, a boolean exit, an empty node id, a non-integer count: each gives
    no ids and a reason. On C2a7 these read complete."""
    report, token, text = _clean_run(tmp_path)
    if case == "collect-passed":
        inv = text.split(RB.REPORT_MARK + "pytest ")[1].split()[0]
        rows = [json.loads(ln) for ln in report.read_text().splitlines()]
        fin = rows.pop()
        rows += [{"rec": "event", "token": token, "inv": inv, "nodeid": "tests/x.py", "when": "collect",
                  "outcome": "passed"}, {**fin, "events": fin["events"] + 1}]
        report.write_text("".join(json.dumps(r) + "\n" for r in rows))
    else:
        _rewrite(report, GRAMMAR[case])
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why, (case, why)


@requires_monitoring
@pytest.mark.parametrize("children", [[["a" * 32]], ["A" * 32], [7], "abc"])
def test_b188_1_a_malformed_runner_record_gives_no_ids_and_raises_nothing(tmp_path, children):
    """B188 finding 1: a runner record whose children are not a list of invocation ids gives a reason (on C2a7 a nested
    list raised TypeError at `set(invs)`)."""
    report, token, text = _clean_run(tmp_path)
    inv = text.split(RB.REPORT_MARK + "pytest ")[1].split()[0]
    run = "b" * 32
    with open(report, "a") as fh:
        fh.write(json.dumps({"rec": "runner", "token": token, "run": run, "files": 1, "children": children,
                             "complete": True}) + "\n")
    text = text.replace(f"{RB.REPORT_MARK}pytest {inv}", f"{RB.REPORT_MARK}runner {run}")
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why


@requires_monitoring
def test_b188_1_f_refuses_a_malformed_report_instead_of_exempting_an_invented_id(tmp_path):
    """B188 finding 1, consumer half (REVW9 `::test_f_refuses_a_malformed_report_instead_of_exempting_an_invented_id`):
    a malformed byte in the baseline's and the session's ids, replaced by the same character, made two different
    failures one id: the baseline read complete and F returned ([], None). Now neither reads complete."""
    report, token, text = _clean_run(tmp_path)
    _rewrite(report, GRAMMAR["invalid-utf8"])
    assert LB.parse_baseline(stream(text, PYTEST), PYTEST, report, token)["complete"] is False
    base = tmp_path / "base.json"
    produce(base, "baseline", {"aget": "a", "head": "h", "output_complete": True, "selection": _wit(report), "verdict": "RECORDED",   # C2b
                               "failures": ["tests/test_a.py::test_\ufffda"]})
    (tmp_path / "t.jsonl").write_text(stream(text, PYTEST))
    new, why = A.suite_regressions(tmp_path / "t.jsonl", PYTEST, base, "a", "h", report=report, token=token)
    assert new == [] and why and "UTF-8" in why


def _bounded(code, timeout=10):
    """Run `code` in a child python with this kit on its path; a block is a timeout, never a hung test."""
    return subprocess.run([sys.executable, "-c", f"import sys; sys.path.insert(0, {str(BATCH)!r}); {code}"],
                          capture_output=True, text=True, timeout=timeout)


@pytest.mark.parametrize("who", ["reader", "runner", "plugin"])
def test_b188_2_a_fifo_report_is_refused_without_waiting(tmp_path, who):
    """B188 finding 2 (REVW9's three FIFO rows): the reader, the parallel runner's append and the plugin opened a FIFO
    report blocking; now each refuses (or stays silent) at once."""
    fifo = tmp_path / "rep.jsonl"
    os.mkfifo(fifo)
    if who == "reader":
        p = _bounded(f"import result_binding as R; print(R.report_failures({str(fifo)!r}, 'a'*32, "
                     f"'aget-kit-report: pytest {'c' * 32}\\n1 passed in 0.1s'))")
        assert p.returncode == 0 and "regular file" in p.stdout, p.stdout + p.stderr
    elif who == "runner":
        p = _bounded(f"import result_binding as R\ntry:\n    R.append_runner_record({str(fifo)!r}, 'a'*32, 'b'*32, 0, "
                     "[], True)\nexcept OSError as e:\n    print('refused', e)")
        assert p.returncode == 0 and "refused" in p.stdout, p.stdout + p.stderr
    else:
        root = member(tmp_path, {"test_a.py": "def test_a():\n    pass\n"})
        env = RB.report_env(dict(os.environ), fifo, "a" * 32)
        import shlex
        p = subprocess.run(shlex.split(PYTEST), cwd=root, env=env, capture_output=True, text=True, timeout=20)
        assert p.returncode == 0 and RB.REPORT_MARK not in p.stdout   # silent: the run is not known, nothing blocked


@requires_monitoring
def test_c2a8_f_needs_the_last_suite_calls_own_result(tmp_path):
    """FWK-OVSR5's C2a7 advisory (1) (Codex, two real pytest runs): when the session's LAST suite call has no tool
    result in the transcript, F and the baseline parser took the earlier run's output and report as the result."""
    report, token, text = _clean_run(tmp_path)
    rows = stream(text, PYTEST).splitlines() + [json.dumps({"sessionId": "S", "message": {"content": [
        {"type": "tool_use", "id": "u2", "name": "Bash", "input": {"command": PYTEST}}]}})]
    (tmp_path / "t.jsonl").write_text("\n".join(rows) + "\n")
    base = tmp_path / "base.json"
    produce(base, "baseline", {"aget": "a", "head": "h", "output_complete": True, "selection": _wit(report), "verdict": "RECORDED",   # C2b
                               "failures": ["tests/test_a.py::test_a"]})
    new, why = A.suite_regressions(tmp_path / "t.jsonl", PYTEST, base, "a", "h", report=report, token=token)
    assert new == [] and why and "0 results" in why       # changed at C2a9 (labelled): the shared reader's wording
    assert LB.parse_baseline("\n".join(rows), PYTEST, report, token)["complete"] is False  # changed at C2a10 (labelled, B192 finding 2): a refusal is a record that is not complete


@requires_monitoring
def test_c2a8_a_run_that_stops_early_is_not_complete(tmp_path):
    """FWK-OVSR5's C2a7 advisory (2): `-x` (or `--maxfail`, from the command or a member's addopts) stops the run, so
    a new failure among the tests not run would be unseen; collected must equal reported."""
    root = member(tmp_path, {"test_a.py": "def test_a():\n    assert False\ndef test_b():\n    assert False\n"})
    report, token, env = under_report(tmp_path)
    p, text = native(root, PYTEST + " -x", env)
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why and "collected 2" in why, why


# --- C2a9: REVW9's B190 read (last call's own result; undeclared deselection; exact grammar) --------------------

def _two_runs(tmp_path):
    """Two native runs into one report: the older fails test_old, the newer fails test_new (each with a passing
    control). Returns (report, token, old_text, new_text)."""
    root = member(tmp_path, {"test_s.py": "def test_old():\n    assert False\ndef test_ok():\n    pass\n"})
    report, token, env = under_report(tmp_path)
    _, old = native(root, PYTEST, env)
    (root / "tests/test_s.py").write_text("def test_new():\n    assert False\ndef test_ok():\n    pass\n")
    env = RB.report_env(dict(os.environ), report, token)
    _, new = native(root, PYTEST, env)
    return report, token, old, new


def _calls(*events):
    rows = []
    for kind, ident, text in events:
        b = ({"type": "tool_use", "id": ident, "name": "Bash", "input": {"command": PYTEST}} if kind == "use" else
             {"type": "tool_result", "tool_use_id": ident, "content": text})
        rows.append(json.dumps({"sessionId": "S", "message": {"content": [b]}}))
    return "\n".join(rows) + "\n"


@pytest.mark.parametrize("order", [pytest.param("chronological", marks=requires_monitoring), pytest.param("last-result-first", marks=requires_monitoring), "duplicate-result"])
def test_b190_1_f_reads_the_last_calls_own_result_whatever_order_results_arrive(tmp_path, order):
    """B190 finding 1 (REVW9 `reviewer_c2a8_probes.py::test_f_refuses_an_older_calls_result_in_place_of_the_last_
    calls_own_result[True]`): F took the suite result that arrived last; when the newer call's own result came first
    it read the older run, ([], None). Now F and the baseline parser read the last call's own result by its id; two
    results for that id refuse."""
    report, token, old, new = _two_runs(tmp_path)
    ev = [("use", "u1", None), ("use", "u2", None)]
    ev += {"chronological": [("res", "u1", old), ("res", "u2", new)],
           "last-result-first": [("res", "u2", new), ("res", "u1", old)],
           "duplicate-result": [("res", "u2", new), ("res", "u1", old), ("res", "u2", old)]}[order]
    t = tmp_path / "t.jsonl"
    t.write_text(_calls(*ev))
    base = tmp_path / "base.json"
    produce(base, "baseline", {"aget": "a", "head": "h", "output_complete": True, "selection": _wit(report), "verdict": "RECORDED",   # C2b
                               "failures": ["tests/test_s.py::test_old"]})
    new_ids, why = A.suite_regressions(t, PYTEST, base, "a", "h", report=report, token=token)
    parsed = LB.parse_baseline(t.read_text(), PYTEST, report, token)
    if order == "duplicate-result":
        assert new_ids == [] and why and "2 results" in why and parsed["complete"] is False  # changed at C2a10 (labelled, B192 finding 2): a refusal is a record that is not complete
    else:
        assert (new_ids, why) == (["tests/test_s.py::test_new"], None)
        assert parsed["failures"] == ["tests/test_s.py::test_new"] and parsed["complete"]


@pytest.mark.parametrize("mode", [pytest.param("k", marks=requires_monitoring), pytest.param("m", marks=requires_monitoring), pytest.param("ini-deselect", marks=requires_monitoring), "lf", pytest.param("declared-deselect", marks=requires_monitoring)])
def test_b190_2_undeclared_deselection_is_not_a_complete_suite(tmp_path, mode):
    """B190 finding 2 (REVW9 `::test_f_refuses_undeclared_member_deselection_as_full_suite_completeness[…]`): a member's
    pytest.ini adding `-k`, `-m` or `--deselect`, or a `--lf` run, reduced the collection and read complete. Now only
    the invocation's own `--deselect` arguments (the kit's declared exclusions) may deselect."""
    body = ("import pytest\n@pytest.mark.old\ndef test_old():\n    assert False\ndef test_new():\n    assert False\n"
            "@pytest.mark.old\ndef test_ok_old():\n    pass\n")
    ini = {"k": "addopts = -k old\n", "m": "addopts = -m old\n",
           "ini-deselect": "addopts = --deselect tests/test_d.py::test_new\n", "lf": "", "declared-deselect": ""}[mode]
    root = member(tmp_path, {"test_d.py": body})
    (root / "pytest.ini").write_text("[pytest]\nmarkers =\n    old: old\n" + ini)
    report, token, env = under_report(tmp_path)
    cmd = {"lf": f"{sys.executable} -B -m pytest tests -q -rfE --lf",
           "declared-deselect": PYTEST + " --deselect tests/test_d.py::test_new"}.get(mode, PYTEST)
    if mode == "lf":                                      # a first run fills the cache; the --lf run selects from it
        native(root, f"{sys.executable} -B -m pytest tests -q -rfE --deselect tests/test_d.py::test_new", dict(os.environ))
    p, text = native(root, cmd, env)
    ids, why, _ = RB.report_failures(report, token, text)
    if mode == "declared-deselect":
        assert why is None and ids == ["tests/test_d.py::test_old"], (why, text[-500:])
    else:
        assert ids == [] and why and ("did not declare" in why or "--lf" in why), (mode, why, text[-500:])


def test_b190_3_ids_are_exactly_32_hex_digits():
    """B190 finding 3 (REVW9 `::test_reader_refuses_a_runner_whose_invocation_ids_are_not_exactly_32_hex_digits`):
    `^[0-9a-f]{32}$` admitted a final line feed. Every grammar id is a full-string match now."""
    assert RB._hex("a" * 32) and not RB._hex("a" * 32 + "\n") and not RB._hex("a" * 33) and not RB._hex("A" * 32)
    assert not RB._MARK_LINE.fullmatch(f"aget-kit-report: pytest {'a' * 32}\n")


@requires_monitoring
def test_c2a9_both_readers_take_the_same_declared_call(tmp_path):
    """FWK-OVSR5's C2a8 advisory (1) (Codex and agy): after a completed run, a later `… -q` call with no result was
    skipped by the baseline parser (exact command match) while F took it as the declared suite; producer and F
    disagreed. Both now use result_binding.is_suite_run: the baseline is not complete either."""
    report, token, text = _clean_run(tmp_path)
    rows = stream(text, PYTEST).splitlines() + [json.dumps({"sessionId": "S", "message": {"content": [
        {"type": "tool_use", "id": "u2", "name": "Bash", "input": {"command": PYTEST + " -q"}}]}})]
    assert LB.parse_baseline("\n".join(rows), PYTEST, report, token)["complete"] is False  # changed at C2a10 (labelled, B192 finding 2): a refusal is a record that is not complete
    assert A.is_suite_run.__code__.co_filename.endswith("result_binding.py")   # one rule, defined once


@pytest.mark.parametrize("case", ["exit5-suite", "exit1-no-failure", "duplicate-key", "nan"])
def test_c2a9_abnormal_runs_and_records_are_not_complete(tmp_path, case):
    """FWK-OVSR5's C2a8 advisory (single-product items): a whole suite that collected nothing (exit 5), an exit 1
    with no failing test (here `-W error` on a session-end warning stands in for `--cov-fail-under`), a key twice in
    one record, and NaN each read as no known ids."""
    if case == "exit5-suite":
        root = member(tmp_path, {"test_e.py": "x = 1\n"})
    elif case == "exit1-no-failure":
        root = member(tmp_path, {"test_e.py": "def test_ok():\n    pass\n",
                                 "conftest.py": "def pytest_sessionfinish(session):\n    session.exitstatus = 1\n"})
    else:
        root = member(tmp_path, {"test_e.py": "def test_ok():\n    pass\n"})
    report, token, env = under_report(tmp_path)
    p, text = native(root, PYTEST, env)
    if case == "duplicate-key":
        rows = report.read_text().splitlines()
        rows[0] = rows[0][:-1] + ', "lf": false}'
        report.write_text("\n".join(rows) + "\n")
    if case == "nan":
        rows = report.read_text().splitlines()
        rows[-1] = rows[-1].replace('"exit": 0', '"exit": NaN')
        report.write_text("\n".join(rows) + "\n")
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why, (case, why, text[-400:])


# --- C2a10: FWK-OVSR5's C2a9 pre-read (Codex and agy), B190 finding 1's class -----------------------------------------

def _rows(*events):
    """Like `_calls`, with a command per use: (\"use\", id, command) or (\"res\", id, text)."""
    rows = []
    for kind, ident, x in events:
        b = ({"type": "tool_use", "id": ident, "name": "Bash", "input": {"command": x}} if kind == "use" else
             {"type": "tool_result", "tool_use_id": ident, "content": x})
        rows.append(json.dumps({"sessionId": "S", "message": {"content": [b]}}))
    return "\n".join(rows) + "\n"


@pytest.mark.parametrize("case", ["reused-id", "early-result", "wrapped-later", pytest.param("commented-later", marks=requires_monitoring)])
def test_c2a10_the_last_suite_call_is_read_by_its_own_id_and_form(tmp_path, case):
    """FWK-OVSR5's C2a9 advisory 2, 3 and 5 (Codex and agy, both products). On C2a9: (a) an id first used by a
    non-matching call was not counted, so that call's result became the suite call's; (b) a result that arrived
    before its call was dropped, so a second result for the last call went unseen; (c) a later run of the suite
    through a pipe was not the declared command, so F read the earlier run; (d) a later run with a trailing shell
    comment was missed the same way. Each read the older, clean run ([], None). Now (a), (b), (c) refuse in F and the
    baseline parser alike, and (d) is the declared command and its run is read."""
    report, token, old, new = _two_runs(tmp_path)
    ev = {"reused-id": [("use", "u1", PYTEST), ("res", "u1", new), ("use", "u2", "echo hi"), ("use", "u2", PYTEST),
                        ("res", "u2", old)],
          "early-result": [("res", "u2", old), ("use", "u1", PYTEST), ("res", "u1", old), ("use", "u2", PYTEST),
                           ("res", "u2", new)],
          "wrapped-later": [("use", "u1", PYTEST), ("res", "u1", old), ("use", "u2", PYTEST + " 2>&1 | tail -80"),
                            ("res", "u2", new)],
          "commented-later": [("use", "u1", PYTEST), ("res", "u1", old), ("use", "u2", PYTEST + "  # again"),
                              ("res", "u2", new)]}[case]
    t = tmp_path / "t.jsonl"
    t.write_text(_rows(*ev))
    base = tmp_path / "base.json"
    produce(base, "baseline", {"aget": "a", "head": "h", "output_complete": True, "selection": _wit(report),   # C2b: bound
                               "verdict": "RECORDED", "failures": ["tests/test_s.py::test_old"]})
    new_ids, why = A.suite_regressions(t, PYTEST, base, "a", "h", report=report, token=token)
    parsed = LB.parse_baseline(t.read_text(), PYTEST, report, token)
    if case == "commented-later":
        assert (new_ids, why) == (["tests/test_s.py::test_new"], None)
        assert parsed["failures"] == ["tests/test_s.py::test_new"]
    else:
        assert new_ids == [] and why and parsed["complete"] is False, (new_ids, why, parsed)
        # changed at C2a10's pre-read fixes (labelled): the earlier, stricter rules refuse these first
        assert {"reused-id": "used by more than one call", "early-result": "arrives before its call",
                "wrapped-later": "a later call runs the command"}[case] in why, why


# --- C2a10: REVW9's B192 finding 1 (the final exit) ---------------------------------------------------------------------

_SESSIONFINISH_WRAPPER = ("import pytest\n@pytest.hookimpl(hookwrapper=True)\n"
                          "def pytest_sessionfinish(session, exitstatus):\n    yield\n    session.exitstatus = 1\n")
_UNCONFIGURE_WRAPPER = ("import pytest\n_s = []\ndef pytest_sessionstart(session):\n    _s.append(session)\n"
                        "@pytest.hookimpl(hookwrapper=True, tryfirst=True)\ndef pytest_unconfigure(config):\n"
                        "    yield\n    _s[0].exitstatus = 1\n")


def test_b192_1_an_exit_changed_by_a_member_sessionfinish_wrapper_is_not_a_clean_run(tmp_path):
    """B192 finding 1 (REVW9 `reviewer_c2a9_probes.py::test_reader_refuses_an_exit_changed_after_the_plugin_finish_
    hook`): a member conftest's `pytest_sessionfinish` hookwrapper sets the status to 1 after the plugin's `trylast`
    record. Native exit 1, report exit 0: the reader, the baseline parser and F read a clean run ([], None). Now the
    finish record is written at unconfigure, after every sessionfinish wrapper, so it holds exit 1 with no failing
    test, which is not complete."""
    root = member(tmp_path, {"test_a.py": "def test_a():\n    pass\n", "conftest.py": _SESSIONFINISH_WRAPPER})
    report, token, env = under_report(tmp_path)
    p, text = native(root, PYTEST, env)
    assert p.returncode == 1
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why and "exited 1 with no failing test" in why, why
    base = tmp_path / "base.json"
    produce(base, "baseline", {"aget": "a", "head": "h", "output_complete": True, "selection": _wit(report),   # C2b: bound
                               "verdict": "RECORDED", "failures": []})
    (tmp_path / "t.jsonl").write_text(stream(text, PYTEST))
    new, fwhy = A.suite_regressions(tmp_path / "t.jsonl", PYTEST, base, "a", "h", report=report, token=token)
    assert new == [] and fwhy, fwhy
    assert LB.parse_baseline(stream(text, PYTEST), PYTEST, report, token)["complete"] is False


@requires_monitoring
def test_b192_1_a_status_changed_after_unconfigure_is_caught_by_the_process_exit(tmp_path):
    """B192 finding 1, closing route "compare with the invoker's exit wherever it is available": a member that
    changes the status even later (its own unconfigure wrapper, outside the plugin's) is not seen by the report, but
    where the kit ran pytest itself the process exit differs and the result is not known; where only a transcript
    exists, the error-marked tool result with no failing test is refused."""
    root = member(tmp_path, {"test_a.py": "def test_a():\n    pass\n", "conftest.py": _UNCONFIGURE_WRAPPER})
    report, token, env = under_report(tmp_path)
    p, text = native(root, PYTEST, env)
    assert p.returncode == 1
    ids, why, _ = RB.report_failures(report, token, text, exit_code=p.returncode)
    assert ids == [] and why and "the process exited 1" in why, why
    rows = [{"sessionId": "S", "message": {"content": [{"type": "tool_use", "id": "u1", "name": "Bash", "input": {"command": PYTEST}}]}},
            {"sessionId": "S", "message": {"content": [{"type": "tool_result", "tool_use_id": "u1", "content": text, "is_error": True}]}}]
    t = tmp_path / "t.jsonl"
    t.write_text("\n".join(json.dumps(r) for r in rows) + "\n")
    base = tmp_path / "base.json"
    produce(base, "baseline", {"aget": "a", "head": "h", "output_complete": True, "selection": _wit(report),   # C2b: bound
                               "verdict": "RECORDED", "failures": []})
    new, fwhy = A.suite_regressions(t, PYTEST, base, "a", "h", report=report, token=token)
    assert new == [] and fwhy and "marked as an error" in fwhy, fwhy
    assert LB.parse_baseline(t.read_text(), PYTEST, report, token)["complete"] is False


# --- C2a10: REVW9's B192 finding 3 (the collected population) -----------------------------------------------------------

BARE = f"{sys.executable} -B -m pytest -q -rfE -p no:cacheprovider"     # names no path: testpaths and addopts apply


def _tree_member(tmp_path, files):
    """`member`, with sub-folders under tests/."""
    root = tmp_path / "member"
    for name, body in files.items():
        (root / "tests" / name).parent.mkdir(parents=True, exist_ok=True)
        (root / "tests" / name).write_text(body)
    g(root, "init", "-q")
    g(root, "add", "-A")
    g(root, "commit", "-q", "-m", "c")
    return root
_NEW = "def test_new():\n    assert False\n"
_NARROW = {
    "ignore": ({"pytest.ini": "[pytest]\naddopts = --ignore=tests/test_new.py\n"}, {}),
    "ignore-glob": ({"pytest.ini": "[pytest]\naddopts = --ignore-glob=*_new.py\n"}, {}),
    "testpaths": ({"pytest.ini": "[pytest]\ntestpaths = tests/a\n"}, {}),
    "addopts-path": ({"pytest.ini": "[pytest]\naddopts = tests/a\n"}, {}),
    "collect-ignore": ({}, {"conftest.py": "collect_ignore = ['test_new.py']\n"}),
    "drop-items": ({}, {"conftest.py": "def pytest_collection_modifyitems(items):\n"
                                       "    items[:] = [i for i in items if 'new' not in i.nodeid]\n"}),
}


@requires_monitoring
@pytest.mark.parametrize("case", sorted(_NARROW))
def test_b192_3_an_undeclared_collection_omission_is_not_a_complete_suite(tmp_path, case):
    """B192 finding 3 (REVW9 `reviewer_c2a9_probes.py::test_f_refuses_undeclared_collection_path_omissions[…]`): a new
    failing test left out of collection by an ini `--ignore`/`--ignore-glob`, `testpaths`, a path in addopts, a
    conftest `collect_ignore`, or a hook that drops items without deselecting them. On C2a9 each recorded collected =
    ran for the smaller set and read complete, F ([], None). Now the plugin names the narrowing inputs and dropped
    items, and the run is not complete."""
    at_root, in_tests = _NARROW[case]
    root = _tree_member(tmp_path, {"a/test_a.py": "def test_a():\n    pass\n", "test_new.py": _NEW, **in_tests})
    for name, body in at_root.items():
        (root / name).write_text(body)
    report, token, env = under_report(tmp_path)
    p, text = native(root, BARE, env)
    assert "test_new" not in text, text                       # the failing test really was left out
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why and ("narrowed" in why or "dropped" in why), why
    base = tmp_path / "base.json"
    produce(base, "baseline", {"aget": "a", "head": "h", "output_complete": True,   # C2b: bound
                               "verdict": "RECORDED", "failures": []})
    (tmp_path / "t.jsonl").write_text(stream(text, BARE))
    new, fwhy = A.suite_regressions(tmp_path / "t.jsonl", BARE, base, "a", "h", report=report, token=token)
    assert new == [] and fwhy, fwhy                    # F: the baseline holds no selection witness, so refused
    # changed at C2a11 (labelled; REVW9's B194 answer 3): the baseline run records its narrowed selection as the
    # standing policy, unless an item was dropped (never a policy)
    # changed at F4 (labelled; REVW11's B201 finding 2, weekly-train:R17): the narrowed selection is still recorded,
    # but the baseline reads complete only with a recorded approval of that exact selection
    parsed = LB.parse_baseline(stream(text, BARE), BARE, report, token)
    if case == "drop-items":
        assert parsed["complete"] is False
    else:
        assert parsed["complete"] is False and parsed["selection"], parsed
        assert "no recorded approval of its selection" in parsed["failures_unknown"], parsed
        assert LB.parse_baseline(stream(text, BARE), BARE, report, token,
                                 approved={RB.selection_digest(parsed["selection"])})["complete"]


@requires_monitoring
@pytest.mark.parametrize("declared,complete", [("tests/test_s.py::test_t", False), ("tests/test_s.py", True)])
def test_b192_3_a_declared_exclusion_is_an_identity_not_a_prefix(tmp_path, declared, complete):
    """B192 finding 3 (REVW9 `::test_b8a_refuses_prefix_deselection_of_an_unlisted_new_node`): pytest's `--deselect
    tests/test_s.py::test_t` also drops `test_t2`, and C2a9 admitted every deselected id that starts with a declared
    one, so a new failing `test_t2` was exempt. Now a declared id covers itself only; a declared path (no `::`) is a
    scope the operator wrote (positive control)."""
    root = member(tmp_path, {"test_s.py": "def test_t():\n    assert False\ndef test_t2():\n    assert False\n",
                             "test_ok.py": "def test_ok():\n    pass\n"})
    report, token, env = under_report(tmp_path)
    p, text = native(root, f"{BARE} --deselect {declared}", env)
    ids, why, _ = RB.report_failures(report, token, text)
    if complete:
        assert (ids, why) == ([], None), why
    else:
        assert ids == [] and why and "did not declare" in why and "test_t2" in why, why


@requires_monitoring
def test_b192_3_positive_control_an_unnarrowed_run_is_complete(tmp_path):
    """C2a10 positive control: the same member with no narrowing input reads complete with its failing test."""
    root = _tree_member(tmp_path, {"a/test_a.py": "def test_a():\n    pass\n", "test_new.py": _NEW})
    report, token, env = under_report(tmp_path)
    p, text = native(root, BARE, env)
    assert RB.report_failures(report, token, text)[:2] == (["tests/test_new.py::test_new"], None)


# --- C2a10: FWK-OVSR6's C2a10 pre-read (reproduced on the C2a10 draft) ------------------------------------------------

_HIDDEN = {
    "ignore-hook": ({}, {"conftest.py": "def pytest_ignore_collect(collection_path, config):\n"
                                        "    return True if collection_path.name == 'test_new.py' else None\n"}),
    "python-files": ({"pytest.ini": "[pytest]\npython_files = test_a*.py\n"}, {}),
    "norecursedirs": ({"pytest.ini": "[pytest]\nnorecursedirs = new\n"}, {}),
}


@requires_monitoring
@pytest.mark.parametrize("case", sorted(_HIDDEN))
def test_c2a10_preread_1_a_population_left_out_before_collection_is_not_complete(tmp_path, case):
    """FWK-OVSR6's C2a10 pre-read 1 (HIGH, reproduced): a conftest `pytest_ignore_collect`, changed `python_files`, or
    changed `norecursedirs` left a failing test out before collection, outside every listed narrowing input: the
    draft read the run complete. Now the plugin records every path any ignore hook excluded and non-default discovery
    patterns."""
    at_root, in_tests = _HIDDEN[case]
    new_path = "new/test_new.py" if case == "norecursedirs" else "test_new.py"
    root = _tree_member(tmp_path, {"a/test_a.py": "def test_a():\n    pass\n", new_path: _NEW, **in_tests})
    for name, body in at_root.items():
        (root / name).write_text(body)
    report, token, env = under_report(tmp_path)
    p, text = native(root, BARE, env)
    assert "test_new" not in text, text
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why and "narrowed" in why, why


@requires_monitoring
def test_c2a10_preread_9_an_options_value_in_addopts_is_not_a_path(tmp_path):
    """FWK-OVSR6's C2a10 pre-read 9: `--junit-prefix tests` in addopts read as a path written into addopts."""
    root = _tree_member(tmp_path, {"a/test_a.py": "def test_a():\n    pass\n"})
    (root / "pytest.ini").write_text("[pytest]\naddopts = --junit-prefix tests\n")
    report, token, env = under_report(tmp_path)
    p, text = native(root, BARE, env)
    assert RB.report_failures(report, token, text)[:2] == ([], None)


@pytest.mark.parametrize("case", ["early-only", "duplicate-unrelated", "two-sessions", "list-id"])
def test_c2a10_preread_2_ownership_refuses_every_malformed_stream(tmp_path, case):
    """FWK-OVSR6's C2a10 pre-read 2: a single result before its call, two unrelated calls sharing an id, a stream
    holding two sessions were accepted, and a list id raised TypeError in both readers."""
    report, token, old, new = _two_runs(tmp_path)
    use = lambda i, c=PYTEST, sid=None: {"sessionId": "S", "message": {"content": [{"type": "tool_use", "id": i, "name": "Bash",
                                                                  "input": {"command": c}}]}, **({"sessionId": sid} if sid else {})}
    res = lambda i, t: {"sessionId": "S", "message": {"content": [{"type": "tool_result", "tool_use_id": i, "content": t}]}}
    rows = {"early-only": [use("u1"), res("u1", old), res("u2", new), use("u2")],
            "duplicate-unrelated": [use("x", "ls"), use("x", "pwd"), use("u1"), res("u1", new)],
            "two-sessions": [use("u1", sid="s1"), res("u1", old), use("u2", sid="s2"), res("u2", new)],
            "list-id": [use("u1"), res("u1", old), use(["u2"]), res(["u2"], new)]}[case]
    t = "\n".join(json.dumps(r) for r in rows) + "\n"
    out, why = RB.last_call_output(t, lambda c: RB.is_suite_run(c, PYTEST), bash_only=True)
    assert out is None and why, why
    assert LB.parse_baseline(t, PYTEST, report, token)["complete"] is False


@pytest.mark.parametrize("spelling,refused", [('{py} -m "pytest" tests -k foo', True),
                                              ("sh -c '{py} -m pytest tests -k foo'", True),
                                              ("echo done  # {py} -m pytest tests", False)])
def test_c2a10_preread_3_a_later_suite_call_is_recognised_by_its_words(tmp_path, spelling, refused):
    """FWK-OVSR6's C2a10 pre-read 3: a later narrowed run spelled with quotes or inside `sh -c` was not recognised,
    so the earlier full run was kept; a mention inside a comment refused. Compared as shell words now."""
    cmd = f"{sys.executable} -B -m pytest tests"
    later = spelling.format(py=f"{sys.executable} -B")
    assert RB.mentions_suite(later, cmd) is refused


def test_c2a10_preread_4_5_6_masked_drop_runner_exit_and_ign_spelling(tmp_path):
    """FWK-OVSR6's C2a10 pre-read 4-6 at the reader: the same declared id deselected twice no longer hides a dropped
    test (distinct ids; plugin side tested natively above); a parallel runner killed (137) is not complete; IGN reads
    an `UNREADABLE` element in either spelling as a non-reading."""
    CI = A.CI
    changed, unread = CI.ignore_changes({"x": "UNREADABLE: y"}, {"x": "UNREADABLE: y"})
    assert unread == ["x"] and changed == []
    src = (Path(A.__file__).parent / "pytest_plugin/aget_kit_report.py").read_text()
    assert "len(set(_deselected))" in src
    assert 'kind == "runner" and exit_code not in (0, 1)' in Path(RB.__file__).read_text()


# --- C2a11: FWK-OVSR6's refreshed C2a10 pre-read (`25a1a11a7`), the parts that do not depend on B194's ruling --------

@pytest.mark.parametrize("later", ["env {c};", 'bash -lc "{c};"', "env {m}", "{c}; true", "{c}&&true", "{c}|cat"])
def test_c2a11_shell_punctuation_does_not_hide_a_later_suite_run(later):
    """FWK-OVSR6's C2a10r pre-read 3: shlex kept `pytest;` as one word and `-mpytest` as one, so these later runs were
    not recognised and an earlier full run was credited. Operators are now boundaries and `-mX` is `-m X`."""
    cmd = f"{sys.executable} -B -m pytest tests"
    text = later.format(c=cmd, m=f"{sys.executable} -B -mpytest tests")
    assert RB.mentions_suite(text, cmd), text


def test_c2a11_session_ids_of_different_types_are_two_sessions():
    """FWK-OVSR6's C2a10r pre-read: `sessionId` 1 and "1" collapsed into one session."""
    use = lambda i, sid: {"sessionId": sid, "message": {"content": [{"type": "tool_use", "id": i, "name": "Bash",
                                                                     "input": {"command": PYTEST}}]}}
    # changed at C2a12 (labelled; B195 #3): every event now names its session, the results with the int form
    res = lambda i: {"sessionId": 1, "message": {"content": [{"type": "tool_result", "tool_use_id": i, "content": "x"}]}}
    t = "\n".join(json.dumps(r) for r in [use("u1", 1), res("u1"), use("u2", "1"), res("u2")]) + "\n"
    out, why = RB.last_call_output(t, lambda c: RB.is_suite_run(c, PYTEST), bash_only=True)
    assert out is None and "2 sessions" in why, why


# --- C2a11: REVW9's B194 finding 6 (the selection witness; REVW9's accepted route) --------------------------------------

def _run_member(tmp_path, files, ini=None, env_extra=None):
    root = _tree_member(tmp_path, files)
    if ini:
        (root / "pytest.ini").write_text(ini)
    report, token, env = under_report(tmp_path, base={**os.environ, **(env_extra or {})})   # the member's own env
    p, text = native(root, BARE, env)
    return root, report, token, text


def test_b194_6_a_collection_hook_that_creates_no_item_is_refused(tmp_path):
    """B194 finding 6 (REVW9's makeitem row): a `pytest_pycollect_makeitem` hook returning [] for test functions hid
    them from every count ("1 passed", narrowed [], dropped 0). The plugin now records them as suppressed, and a run
    with a suppressed candidate is never complete, whatever the policy."""
    hook = ("def pytest_pycollect_makeitem(collector, name, obj):\n"
            "    return [] if name.startswith('test_new') else None\n")
    _, report, token, text = _run_member(tmp_path, {"test_s.py": "def test_a():\n    pass\n" + _NEW, "conftest.py": hook})
    for policy in (None, "record"):
        ids, why, _ = RB.report_failures(report, token, text, policy=policy)
        assert ids == [] and why and "uncreated" in why, why


@requires_monitoring
def test_b194_6_a_plugin_blocked_through_pytest_addopts_is_a_narrowing(tmp_path):
    """B194 finding 6 (REVW9's blocked-producer row): `PYTEST_ADDOPTS=-p no:X` read complete, its value skipped."""
    _, report, token, text = _run_member(tmp_path, {"test_s.py": "def test_a():\n    pass\n"},
                                         env_extra={"PYTEST_ADDOPTS": "-p no:doctest"})
    ids, why, _ = RB.report_failures(report, token, text)
    assert why and "plugin blocked doctest" in why, why
    assert "doctest" in RB.invocation_selection(report, token, text)["blocked"]


@requires_monitoring
def test_b194_6_a_standing_policy_equal_to_its_baseline_counts_and_a_changed_one_refuses(tmp_path):
    """REVW9's B194 answer 3 (accepted as a design route, conditional on a complete witness): a standing
    `collect_ignore_glob = ["templates/*"]` made every run incomplete on C2a10 (an availability defect). The baseline
    now records its selection witness as the standing policy; F's judged run counts only when its selection equals
    it. A second ignore added between the two refuses (positive and negative)."""
    files = {"test_s.py": "def test_a():\n    pass\n", "templates/test_t.py": "def test_t():\n    pass\n",
             "conftest.py": "collect_ignore_glob = ['templates/*']\n"}
    _, report, token, text = _run_member(tmp_path / "one", files)
    base = RB.invocation_selection(report, token, text)
    assert base and RB.report_failures(report, token, text, policy="record")[1] is None
    why = RB.report_failures(report, token, text, policy=base)[1]                   # R17: equal, no approval
    assert why and "no recorded approval" in why, why
    assert RB.report_failures(report, token, text, policy=base,
                              approved={RB.selection_digest(base)})[1] is None    # equal and approved: counts
    assert RB.report_failures(report, token, text)[1]                                    # no policy: refused
    files2 = {**files, "conftest.py": "collect_ignore_glob = ['templates/*', 'test_new.py']\n", "test_new.py": _NEW}
    _, report2, token2, text2 = _run_member(tmp_path / "two", files2)
    ids, why, _ = RB.report_failures(report2, token2, text2, policy=base)
    assert ids == [] and why and "differs from the baseline" in why, why


# --- C2a12: FWK-OVSR6's C2a11 pre-read (`8c5a4ece2`), reproduced items --------------------------------------------------

def test_c2a12_preread_2_a_parallel_run_whose_children_ran_no_test_is_not_complete(tmp_path):
    """FWK-OVSR6's C2a11 pre-read 2 (HIGH, reproduced): two files that collect nothing (pytest exit 5) and each print a
    collection warning gave runner rc 0, `2 warnings in …`, and ([], None, []): a clean result with zero tests. A
    parallel run whose children ran no test in total is not a run of the suite."""
    cls = "class TestNot:\n    def __init__(self):\n        pass\n    def test_x(self):\n        pass\n"
    root = member(tmp_path, {"test_a.py": cls, "test_b.py": cls})
    report, token, env = under_report(tmp_path)
    p, text = native(root, f"{sys.executable} {RUNNER}", env)
    assert "warning" in text and p.returncode == 0, text[-600:]           # the reproduced shape
    for code in (None, p.returncode):
        ids, why, _ = RB.report_failures(report, token, text, exit_code=code)
        assert ids == [] and why and "ran no test" in why, (why, text[-600:])


@pytest.mark.parametrize("other", ["missing", None])
def test_c2a12_preread_5_a_call_without_a_session_id_is_not_part_of_one_session(other):
    """FWK-OVSR6's C2a11 pre-read 5 (MEDIUM, reproduced): the pairs A/missing and A/null `sessionId` were accepted as
    one session (only A/B refused). In a transcript that names a session, a call or result naming none refuses."""
    def ev(sid, body):
        e = {"message": {"content": [body]}}
        if sid != "missing":
            e["sessionId"] = sid
        return e
    use = lambda i: {"type": "tool_use", "id": i, "name": "Bash", "input": {"command": PYTEST}}
    res = lambda i: {"type": "tool_result", "tool_use_id": i, "content": "x"}
    t = "\n".join(json.dumps(r) for r in [ev("A", use("u1")), ev("A", res("u1")), ev(other, use("u2")),
                                          ev(other, res("u2"))]) + "\n"
    out, why = RB.last_call_output(t, lambda c: RB.is_suite_run(c, PYTEST), bash_only=True)
    assert out is None and why and "names no session" in why, why
    clean = "\n".join(json.dumps(r) for r in [ev("A", use("u1")), ev("A", res("u1"))]) + "\n"
    assert RB.last_call_output(clean, lambda c: RB.is_suite_run(c, PYTEST), bash_only=True) == ("x", None)


@requires_monitoring
def test_c2a12_preread_3_the_witness_is_compared_with_the_baseline_even_when_nothing_reads_narrowed(tmp_path):
    """FWK-OVSR6's C2a11 pre-read 3 (MEDIUM, reproduced): the selection witness was compared with the baseline's only
    when the run read as narrowed, so a judged run with plugin autoload switched off by the environment was accepted
    against a baseline that had it on. Positive control: the same environment twice is accepted."""
    files = {"test_s.py": "def test_a():\n    pass\n"}
    _, report, token, text = _run_member(tmp_path / "b", files)
    policy = RB.invocation_selection(report, token, text)
    assert policy and policy["autoload"] == ["on"], policy
    _, report, token, text = _run_member(tmp_path / "same", files)
    assert RB.report_failures(report, token, text, policy=policy)[:2] == ([], None)
    _, report, token, text = _run_member(tmp_path / "off", files, env_extra={"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"})
    ids, why, _ = RB.report_failures(report, token, text, policy=policy)
    assert ids == [] and why and "differs from the baseline" in why and "autoload" in why, why


@pytest.mark.parametrize("op", [";", "&", "|"])
def test_c2a12_preread_7_a_later_line_with_an_unbalanced_quote_does_not_hide_a_suite_run(op):
    """FWK-OVSR6's C2a11 pre-read 7 (MEDIUM, reproduced): a multi-line command whose first line ends in `;`, `&` or
    `|` and whose later line has an unbalanced quote fell back to a whitespace split (`pytest;` one word), so the run
    bash makes of its first line was not seen and an earlier result was used."""
    cmd = f"{sys.executable} -B -m pytest tests"
    assert RB.mentions_suite(f"{cmd}{op}\necho \"unbalanced", cmd)
    assert not RB.mentions_suite("echo done;\necho \"unbalanced", cmd)


def test_b195_2_an_unparsable_later_call_naming_the_suite_is_ambiguous_not_judged_by_a_best_effort_split():
    """B195 finding 2 (HIGH, continuing B194 #5): a parse failure must never restore an older result. A command shlex
    cannot read that holds the suite's own words in any arrangement counts as a mention (the run is unavailable);
    one that holds none does not. REVW9's own spelling is included."""
    cmd = f"{sys.executable} -B -m pytest tests"
    for text in (f"{sys.executable} -m pytest;\n echo \"unterminated",            # REVW9's falsifier, other flags
                 "cd x && pytest tests -x 'unterminated",
                 f"{sys.executable} -B -m pytest -k \"a tests"):
        assert RB.mentions_suite(text, cmd), text
    assert not RB.mentions_suite("echo 'unterminated", cmd)
    s = stream("1 passed", cmd) + json.dumps({"sessionId": "S", "message": {"content": [{"type": "tool_use", "id": "u2", "name": "Bash",
                                                                       "input": {"command": "cd x && pytest tests -x 'u"}}]}}) + "\n"
    out, why = RB.last_call_output(s, lambda c: RB.is_suite_run(c, cmd), bash_only=True,
                                   mentions=lambda c: RB.mentions_suite(c, cmd))
    assert out is None and why, why


@pytest.mark.parametrize("sids, refused", [
    ((None, None), "names no session"), (("missing", "missing"), "names no session"),       # B195 #3: all absent
    (("S1", "S2"), "2 sessions"),                                                            # pre-read: snake case
    (("S1", "S1"), None)])
def test_b195_3_session_identity_is_required_in_either_key(sids, refused):
    """B195 finding 3 (MEDIUM): with `sessionId` null or absent on every event the set of identities was empty and the
    transcript read as one session. Identity is now required on every call and result, read from `sessionId` or the
    stream-json `session_id` (FWK-OVSR6's C2a12 pre-read: two snake-case sessions were accepted)."""
    def ev(sid, body):
        return {"message": {"content": [body]}, **({} if sid == "missing" else {"session_id": sid})}
    use = {"type": "tool_use", "id": "u1", "name": "Bash", "input": {"command": PYTEST}}
    res = {"type": "tool_result", "tool_use_id": "u1", "content": "x"}
    t = json.dumps(ev(sids[0], use)) + "\n" + json.dumps(ev(sids[1], res)) + "\n"
    out, why = RB.last_call_output(t, lambda c: RB.is_suite_run(c, PYTEST), bash_only=True)
    if refused:
        assert out is None and why and refused in why, why
    else:
        assert (out, why) == ("x", None)


@pytest.mark.parametrize("later", ["echo `{c}`", "x=`{c}`", "{i} -m \\\npytest tests", "{i} \\\n-m pytest tests",
                                   "cd /x && {i} -m \\\npytest", "pytest -q", "py.test", "$({c})"])
def test_c2a12_preread_a_later_call_holding_the_suite_program_word_is_a_mention(later):
    """FWK-OVSR6's C2a12 pre-read (HIGH, continuing B195 #2's class, reproduced): a later run in backticks or split by
    a backslash continuation was not a mention, so the earlier result was credited. The suite's program word anywhere
    as a word is now a mention. Controls: `pytest.ini`, `pytest-cov` and an unrelated command are not."""
    cmd = f"{sys.executable} -B -m pytest tests"
    assert RB.mentions_suite(later.format(c=cmd, i=sys.executable), cmd), later
    for other in ("cat pytest.ini", "pip show pytest-cov", "echo done", "ls tests/"):
        assert not RB.mentions_suite(other, cmd), other


# --- C2a12: B195 finding 1 (HIGH, continuing B194 #6): the independent census and the producer witness -------------

_DROP = ("import pytest\n@pytest.hookimpl(hookwrapper=True)\ndef pytest_make_collect_report(collector):\n"
         "    outcome = yield\n    rep = outcome.get_result()\n"
         "    rep.result[:] = [r for r in rep.result if not r.name.startswith('test_new')]\n")


def test_b195_1_a_make_collect_report_wrapper_that_drops_tests_is_refused_by_the_census(tmp_path):
    """B195 finding 1 (REVW9's first falsifier; FWK-OVSR6's C2a11 pre-read 1): a `pytest_make_collect_report` wrapper
    left newly failing functions out of its collection result; the witness stayed equal, suppressed [], dropped 0, and
    F read ([], None). The AST census of the suite's files names them."""
    files = {"test_s.py": "def test_a():\n    pass\n" + _NEW + "def test_new2():\n    assert False\n",
             "conftest.py": _DROP}
    _, report, token, text = _run_member(tmp_path, files)
    assert "1 passed" in text, text[-300:]
    for policy in (None, "record"):
        ids, why, _ = RB.report_failures(report, token, text, policy=policy)
        # changed at C2a13 (labelled; B196 #1): the wrapping conftest is now unsupported scope, refused before its count
        assert ids == [] and why and "implements pytest_make_collect_report" in why, why


@requires_monitoring
def test_b195_1_census_control_parameters_classes_and_non_tests_do_not_trip_it(tmp_path):
    """Control: parametrized tests, test-class methods, a class with `__init__` (pytest does not collect it), a
    `__test__ = False` class and a fixture named like a test are all accounted for; the run is complete."""
    body = ("import pytest\n@pytest.mark.parametrize('x', [1, 2])\ndef test_p(x):\n    pass\n"
            "class TestK:\n    def test_m(self):\n        pass\n"
            "class TestInit:\n    def __init__(self):\n        pass\n    def test_never(self):\n        pass\n"
            "class TestOff:\n    __test__ = False\n    def test_off(self):\n        pass\n"
            "@pytest.fixture\ndef test_fixture_like():\n    return 1\n")
    _, report, token, text = _run_member(tmp_path, {"test_c.py": body})
    ids, why, _ = RB.report_failures(report, token, text)
    assert (ids, why) == ([], None), (why, text[-400:])


@requires_monitoring
def test_b195_1_a_local_producer_no_longer_activated_changes_the_witness(tmp_path):
    """B195 finding 1 (REVW9's second falsifier): a local plugin activated through PYTEST_ADDOPTS at baseline and not
    at the judged run left the witness equal (`list_plugin_distinfo` names distributions only). Every active
    producer is now in the witness, so F refuses the changed selection. Control: the same activation twice."""
    files = {"test_s.py": "def test_a():\n    pass\n"}
    prod = "def pytest_configure(config):\n    pass\n"
    env = {"PYTEST_ADDOPTS": "-p localprod"}

    def run_with(name, extra):
        root = _tree_member(tmp_path / name, files)
        (root / "localprod.py").write_text(prod)
        report, token, e = under_report(tmp_path / name, base={**os.environ, "PYTHONPATH": str(root), **extra})
        return report, token, native(root, BARE, e)[1]
    report, token, text = run_with("b", env)
    policy = RB.invocation_selection(report, token, text)
    assert "localprod" in policy["producers"], policy["producers"]
    report, token, text = run_with("same", env)
    assert RB.report_failures(report, token, text, policy=policy)[:2] == ([], None)
    report, token, text = run_with("off", {})
    ids, why, _ = RB.report_failures(report, token, text, policy=policy)
    assert ids == [] and why and "producers" in why, why


# --- C2a13: B196 findings 1-3 (the census as an independent collection; unsupported producers; program identity) ----

_PATCH_HIDE = ("import _pytest.python as P\n"
               "def _wrap(cls):\n    orig = cls.collect\n"
               "    cls.collect = lambda self: [x for x in orig(self) if 'new' not in x.name.lower()]\n"
               "_wrap(P.Module)\n_wrap(P.Class)\n")


@pytest.mark.parametrize("body", [
    "def test_a():\n    pass\n" + _NEW,                                                                 # plain
    "import pytest\n@pytest.mark.parametrize('s', ['left', 'right'])\ndef test_x(s):\n    pass\n"
    "@pytest.mark.parametrize('s', ['new_case'])\ndef test_y(s):\n    assert False\n",                    # parameters
    "import unittest\nclass Legacy(unittest.TestCase):\n    def test_a(self):\n        pass\n"
    "class LegacyNew(unittest.TestCase):\n    def test_b(self):\n        assert False\n",                   # unittest
    "class TestOuter:\n    def test_a(self):\n        pass\n    class TestInnerNew:\n"
    "        def test_b(self):\n            assert False\n",                                              # nested
    "__test__ = False\n__test__ = True\ndef test_a():\n    pass\n" + _NEW])                               # reassigned
def test_b196_1_a_conftest_that_hides_tests_without_any_hook_is_refused_by_the_independent_collection(tmp_path, body):
    """B196 finding 1 (HIGH, continuing): the AST census rebuilt pytest's rules and missed what they differ on. The
    census is now pytest's own collection of the same roots with no conftest and no member plugin. Here a conftest
    hides every collector named `*new*` by patching pytest at import (no hook implemented, so only the independent
    collection can see it): every shape above is refused."""
    _, report, token, text = _run_member(tmp_path, {"test_s.py": body, "conftest.py": _PATCH_HIDE})
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why and "never became a collected item" in why, (why, text[-300:])


@requires_monitoring
def test_b196_1_control_the_same_shapes_without_the_hiding_conftest_are_complete(tmp_path):
    """Control: parameters, unittest, nested classes, an imported test and a module-level dynamic skip elsewhere are
    all pytest's own in both collections; the run is complete."""
    files = {"test_s.py": ("import pytest, unittest\nfrom helper_tests import test_imported\n"
                           "@pytest.mark.parametrize('s', ['left', 'right'])\ndef test_x(s):\n    pass\n"
                           "class Legacy(unittest.TestCase):\n    def test_a(self):\n        pass\n"
                           "class TestOuter:\n    class TestInner:\n        def test_b(self):\n            pass\n"),
             "helper_tests.py": "def test_imported():\n    pass\n",
             "test_skipmod.py": "import pytest\npytest.importorskip('not_installed_anywhere')\ndef test_z():\n    pass\n"}
    _, report, token, text = _run_member(tmp_path, files)
    assert RB.report_failures(report, token, text)[:2] == ([], None), text[-400:]


@pytest.mark.parametrize("hook", ["pytest_make_collect_report", "pytest_generate_tests", "pytest_collect_file"])
def test_b196_1_a_member_producer_hook_is_unsupported_scope(tmp_path, hook):
    """B196 finding 1 ("exact accounting or refusal of unsupported scope"; REVW9's same-active-producer row): a member
    conftest implementing a hook that can create or hide items makes the population unknown, so the run refuses
    even when nothing is hidden. Cost, stated for F3: such suites need another route."""
    conftest = {"pytest_make_collect_report": "import pytest\n@pytest.hookimpl(hookwrapper=True)\n"
                                              "def pytest_make_collect_report(collector):\n    yield\n",
                "pytest_generate_tests": "def pytest_generate_tests(metafunc):\n    pass\n",
                "pytest_collect_file": "def pytest_collect_file(file_path, parent):\n    return None\n"}[hook]
    _, report, token, text = _run_member(tmp_path, {"test_s.py": "def test_a():\n    pass\n", "conftest.py": conftest})
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why and f"implements {hook}" in why, why


def test_b196_1_an_unnamed_producer_is_in_the_witness(tmp_path):
    """C2a12 second pass M3 / B196 finding 1: a plugin registered without a name (pluggy names it by id()) was dropped
    from the producer witness. It is recorded by its class."""
    files = {"test_s.py": "def test_a():\n    pass\n",
             "conftest.py": "class Producer:\n    pass\ndef pytest_configure(config):\n"
                            "    config.pluginmanager.register(Producer())\n"}
    _, report, token, text = _run_member(tmp_path, files)
    sel = RB.invocation_selection(report, token, text)
    assert any(p.endswith(".Producer") for p in sel["producers"]), sel["producers"]


def test_b196_3_a_fifo_named_like_a_test_file_does_not_block_the_census(tmp_path):
    """B196 finding 3 (MEDIUM): a FIFO named `tests/test_fifo.py` blocked the AST census's plain open (no finish
    record). The census is pytest's own collection, which treats it as the run does; the run returns promptly."""
    root = _tree_member(tmp_path, {"test_s.py": "def test_a():\n    pass\n"})
    os.mkfifo(root / "tests" / "test_fifo.py")
    report, token, env = under_report(tmp_path)
    import shlex
    p = subprocess.run(shlex.split(BARE), cwd=root, capture_output=True, text=True, env={**env, "COLUMNS": "80"},
                       timeout=120)
    assert "aget-kit-report" in p.stdout + p.stderr, (p.stdout + p.stderr)[-400:]


@pytest.mark.parametrize("declared, later, mention", [
    ("python -W ignore -m pytest", "python -m pytest -q", True),                     # B196 finding 2 (REVW9)
    ("uv run pytest tests", "python3 -m pytest tests", True),                       # second pass M13
    ("uv run pytest tests", "uv pip list", False),
    ("python3 -m pytest", "py\\\ntest -q", True),                                   # second pass M12
    ("make test", "ls", True),                                                      # unresolved program
    ("python3 -m pytest", "cat pytest.ini", False)])
def test_b196_2_the_suite_program_is_pytest_or_the_declared_module_or_script(declared, later, mention):
    """B196 finding 2 (HIGH, continuing): the program word was the first word after the interpreter, so an option's
    operand (`-W ignore`) or a wrapper (`uv`) became the program. pytest's runner words always count, with every
    `-m` module and `.py` script of the declared command; a declared command naming none leaves the program
    unresolved, and every later call is then a mention (unavailable, never an older result)."""
    assert RB.mentions_suite(later, declared) is mention


# --- C2a13r: FWK-OVSR7's C2a13 pre-read (reproduced H1-H3, M1-M3; P7) --------------------------------------------------

def test_c2a13_preread_h1_a_hook_bound_by_specname_is_unsupported_scope(tmp_path):
    """H1: `@pytest.hookimpl(specname="pytest_generate_tests")` on a function named otherwise passed the check, which
    matched attribute names. The registered hookimpls are read now."""
    conftest = ("import pytest\n@pytest.hookimpl(specname='pytest_generate_tests')\n"
                "def pytest_quietly(metafunc):\n    pass\n")   # pytest registers only `pytest_*` names from conftests
    _, report, token, text = _run_member(tmp_path, {"test_s.py": "def test_a():\n    pass\n", "conftest.py": conftest})
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why and "implements pytest_generate_tests" in why, why


def test_c2a13_preread_h2_a_test_modules_pytest_plugins_makes_the_census_not_independent(tmp_path):
    """H2: `pytest_plugins = ["x"]` in a test module loads x into the run AND the census, so a hookless x that hides a
    test hid it in both. Any plugin in the census process refuses."""
    files = {"test_s.py": "pytest_plugins = ['hider']\ndef test_a():\n    pass\n" + _NEW,
             "hider.py": _PATCH_HIDE}
    _, report, token, text = _run_member(tmp_path, files, env_extra={"PYTHONPATH": str(tmp_path / "member" / "tests")})
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why and "the census itself loaded plugin" in why, (why, text[-300:])


def test_c2a13_preread_h3_parameters_added_outside_the_census_are_unsupported_scope(tmp_path):
    """H3: a conftest fixture with params a, b plus a hookless patch dropping `test_x[b]` read complete, because the
    bare census id `test_x` was matched by `test_x[a]`. A census id the run made only as parameterized items is now
    unsupported scope (refused), with or without the hiding patch."""
    fixture = "import pytest\n@pytest.fixture(params=['a', 'b'])\ndef s(request):\n    return request.param\n"
    hide_b = ("import _pytest.python as P\n_o = P.Function.from_parent.__func__\n"
              "def _f(cls, parent, **kw):\n    return _o(cls, parent, **kw)\n")
    for extra in ("", hide_b):
        _, report, token, text = _run_member(tmp_path / (extra and "hide" or "plain"),
                                             {"test_s.py": "def test_x(s):\n    pass\n", "conftest.py": fixture + extra})
        ids, why, _ = RB.report_failures(report, token, text)
        assert ids == [] and why and "parameters added outside the census" in why, why


@requires_monitoring
def test_c2a13_preread_m1_m2_import_mode_and_a_literal_bracket_are_pytests_own(tmp_path):
    """M1: the census dropped `--import-mode`, so two folders each holding `test_same.py` under importlib were refused.
    M2: a test named with a literal `[` was read as parameters. Both are complete now."""
    root = _tree_member(tmp_path, {"a/test_same.py": "def test_a():\n    pass\n",
                                   "b/test_same.py": "def test_b():\n    pass\n",
                                   "test_lit.py": "def scenario():\n    pass\nglobals()['test_[literal]'] = scenario\n"})
    report, token, env = under_report(tmp_path)
    text = native(root, BARE + " --import-mode=importlib", env)[1]
    assert RB.report_failures(report, token, text)[:2] == ([], None), text[-400:]


def test_c2a13_preread_m3_a_test_file_operand_is_not_a_program_word():
    """M3: `pytest tests/test_feature.py` made `test_feature.py` a program word, so a later `git diff` of it refused."""
    assert not RB.mentions_suite("git diff tests/test_feature.py", "pytest tests/test_feature.py")
    assert RB.mentions_suite("python3 -m pytest -q", "pytest tests/test_feature.py")


def test_c2a13_preread_p7_pycache_is_not_in_the_selection_witness(tmp_path):
    """P7 (agy, read in the code): pytest's own `__pycache__` skip entered the witness's `ignored`, so a standing policy
    compared unequal between runs with and without bytecode folders."""
    root = _tree_member(tmp_path, {"test_s.py": "def test_a():\n    pass\n"})
    (root / "tests" / "__pycache__").mkdir()
    report, token, env = under_report(tmp_path)
    text = native(root, BARE, env)[1]
    assert not any("__pycache__" in x for x in RB.invocation_selection(report, token, text)["ignored"])


# --- C2a14: B197 #1-#2 and FWK-OVSR7's C2a13 second-pass items (reproduced) -------------------------------------------

_COND = "import os\ndef test_a():\n    pass\nif not os.environ.get('SYNTHETIC_SKIP_NEW'):\n" + "    " + _NEW.replace("\n    ", "\n        ")


@pytest.mark.parametrize("name, files, needle", [
    ("b197_1_env", {"test_s.py": _COND, "conftest.py": "import os\nos.environ['SYNTHETIC_SKIP_NEW'] = '1'\n"},
     "never became a collected item"),
    pytest.param("skip_marker", {"test_s.py": "def test_a():\n    pass\n" + _NEW,
                     "conftest.py": "import pytest\ndef pytest_collection_modifyitems(items):\n"
                                    "    for i in items:\n        if 'new' in i.name:\n"
                                    "            i.add_marker(pytest.mark.skip(reason='x'))\n"},
     "not produced by the census", marks=requires_monitoring),   # changed at C2a14r (labelled): one skip rule
    pytest.param("fixture_skip", {"test_s.py": "def test_a():\n    pass\n" + _NEW,
                      "conftest.py": "import pytest\n@pytest.fixture(autouse=True)\ndef _s(request):\n"
                                     "    if 'new' in request.node.name:\n        pytest.skip('x')\n"},
     "not produced by the census", marks=requires_monitoring),   # changed at C2a14r (labelled): one skip rule
    ("swap", {"test_s.py": "def test_a():\n    pass\n" + _NEW,
              "conftest.py": "import pytest\ndef pytest_collection_modifyitems(items):\n    for n, i in enumerate(items):\n"
                             "        if 'new' in i.name:\n"
                             "            items[n] = pytest.Function.from_parent(i.parent, name='test_replacement', callobj=lambda: None)\n"},
     "an item collection did not create"),
    ("pluggy_prefix", {"test_s.py": "pytest_plugins = ['pluggy_hider']\ndef test_a():\n    pass\n" + _NEW,
                       "pluggy_hider.py": _PATCH_HIDE}, "the census itself loaded plugin pluggy_hider"),
    ("self_unregister", {"test_s.py": "def test_a():\n    pass\n" + _NEW,
                         "conftest.py": "import pytest\nclass Hide:\n    @pytest.hookimpl(hookwrapper=True)\n"
                                        "    def pytest_make_collect_report(self, collector):\n        out = yield\n"
                                        "        r = out.get_result()\n        r.result[:] = [x for x in r.result if 'new' not in x.name]\n"
                                        "    def pytest_collection_finish(self, session):\n"
                                        "        session.config.pluginmanager.unregister(self)\n"
                                        "def pytest_configure(config):\n    config.pluginmanager.register(Hide())\n"},
     "implements pytest_make_collect_report")])
def test_c2a14_population_changes_outside_the_census_are_not_proven(tmp_path, name, files, needle):
    """B197 #1 (HIGH, continuing): a conftest set an ordinary variable at import and the census, copying the run's
    environment, lost the same test. The census now runs before any conftest is imported, from the environment the kit
    plugin found. FWK-OVSR7's second pass (reproduced): a conftest-added skip marker, a skip raised from a conftest
    fixture, an item swapped in by modifyitems, a `pluggy_`-prefixed module plugin, and a producer that unregisters
    itself are each "not proven" (weekly-train:R15)."""
    env = {"PYTHONPATH": str(tmp_path / name / "member" / "tests")} if name == "pluggy_prefix" else None
    _, report, token, text = _run_member(tmp_path / name, files, env_extra=env)
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why and needle in why, (why, text[-300:])


def test_c2a14_doctests_are_in_the_census_when_the_run_collects_them(tmp_path):
    """FWK-OVSR7's second pass 2: the census omitted `--doctest-modules`, so a conftest emptying DoctestModule.collect
    read complete. The run's doctest options now reach the census. Control: the same run without the patch is
    complete."""
    mod = {"test_s.py": "def test_a():\n    pass\n", "lib.py": "def f():\n    '''\n    >>> 1\n    2\n    '''\n"}
    patch = ("import _pytest.doctest as D\n_o = D.DoctestModule.collect\n"
             "D.DoctestModule.collect = lambda self: iter(())\n")
    _, report, token, text = _run_member(tmp_path / "hid", {**mod, "conftest.py": patch},
                                         env_extra={"PYTEST_ADDOPTS": "--doctest-modules"})
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why and "never became a collected item" in why, (why, text[-300:])


@pytest.mark.parametrize("declared, later, mention", [
    ("python -m pytest", "python -m py${SYNTHETIC_EMPTY}test -q", True),             # B197 #2 (REVW9)
    ("python3 -m pytest", "$RUNNER -q", True),
    ("env SETTINGS=config.py python3 -m suite_runner", "python3 -m suite_runner -k one", True),   # second pass 3
    ("env SETTINGS=config.py python3 -m suite_runner", "ls", False),
    ("python3 -m pytest", "pytest-3 -q", True),                                        # add-on 6
    ("python3 -m pytest", "/usr/bin/pytest-3.12 tests", True),
    ("python3 -m pytest", "pip show pytest-cov", False),
    ("python3 -m pytest", "echo $HOME", False)])
def test_c2a14_later_program_identity(declared, later, mention):
    """B197 #2 (HIGH, continuing): a later program (or `-m` module, or script) the shell must expand is unresolved
    and counts as a mention. Declared programs are found after `env`, assignments and interpreter options; a
    versioned runner is the runner."""
    assert RB.mentions_suite(later, declared) is mention


@pytest.mark.parametrize("mode", ["hard", "sym"])
def test_b197_3_the_census_output_is_never_written_through_shared_storage(tmp_path, mode):
    """B197 finding 3 (HIGH, new): the census wrote its result with `open(out, "w")`, so test-module code in the census
    process that put a symlink or a hardlink at that pathname had the kit overwrite a sentinel, and the run read
    complete. The kit now creates the file itself (O_EXCL, O_NOFOLLOW) and passes the census a descriptor; it reads
    back through its own descriptor and admits only an unshared regular file. Here the census-side code finds the file
    through the descriptor and links it (hard) or replaces it with a link to the sentinel (sym): both refuse, and the
    sentinel is intact."""
    sentinel = tmp_path / "sentinel.txt"
    sentinel.write_text("SENTINEL\n")
    body = ("import os, sys\nout = os.environ.get('AGET_KIT_CENSUS_OUT')\n"      # C2a13's pathname route (REVW9)
            f"if out and {mode!r} == 'hard':\n    os.link({str(sentinel)!r}, out)\n"
            f"elif out:\n    os.symlink({str(sentinel)!r}, out)\n"
            "fd = os.environ.get('AGET_KIT_CENSUS_FD')\nif fd:\n"
            "    if sys.platform == 'darwin':\n        import fcntl\n"
            "        path = fcntl.fcntl(int(fd), fcntl.F_GETPATH, bytes(1024)).rstrip(b'\\0').decode()\n"
            "    else:\n        path = os.readlink(f'/proc/self/fd/{fd}')\n"
            f"    if {mode!r} == 'hard':\n        os.link(path, {str(tmp_path / 'hl')!r})\n"
            f"    else:\n        os.unlink(path)\n        os.symlink({str(sentinel)!r}, path)\n"
            "def test_a():\n    pass\n")
    _, report, token, text = _run_member(tmp_path / "m", {"test_s.py": body})
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why and "census" in why, (why, text[-300:])
    assert sentinel.read_text() == "SENTINEL\n"


# --- C2a14r: FWK-OVSR7's C2a14 pre-read 1-7 (reproduced) ---------------------------------------------------------------

_HELPER = "import pytest\ndef skip_it():\n    pytest.skip('x')\ndef imp():\n    pytest.importorskip('not_installed_anywhere')\n"


@requires_monitoring
@pytest.mark.parametrize("name, files, needle", [
    ("replace_fn", {"test_s.py": "def test_a():\n    pass\n" + _NEW,
                    "conftest.py": "def pytest_collection_modifyitems(items):\n    for i in items:\n"
                                   "        if 'new' in i.name:\n            i.obj = lambda: None\n"},
     "the function that ran is not the one"),
    ("helper_skip", {"test_s.py": "def test_a():\n    pass\n" + _NEW, "skiphelp.py": _HELPER,
                     "conftest.py": "import pytest, skiphelp\n@pytest.fixture(autouse=True)\ndef _s(request):\n"
                                    "    if 'new' in request.node.name:\n        skiphelp.skip_it()\n"},
     "not produced by the census"),
    ("helper_importorskip", {"test_s.py": "def test_a():\n    pass\n" + _NEW, "skiphelp.py": _HELPER,
                             "conftest.py": "import pytest, skiphelp\n@pytest.fixture(autouse=True)\ndef _s(request):\n"
                                            "    if 'new' in request.node.name:\n        skiphelp.imp()\n"},
     "test_new: skip (Skipped: could not import"),
    ("condition_flip", {"test_s.py": "import pytest\ndef test_a():\n    pass\n@pytest.mark.skipif(False, reason='r')\n" + _NEW,
                        "conftest.py": "import pytest\ndef pytest_collection_modifyitems(items):\n    for i in items:\n"
                                       "        for m in list(i.iter_markers('skipif')):\n"
                                       "            i.own_markers[:] = [pytest.mark.skipif(True, reason='r').mark]\n"},
     "not produced by the census"),
    ("late_marker", {"test_s.py": "def test_a():\n    pass\n" + _NEW,
                     "conftest.py": "import pytest\ndef pytest_runtest_setup(item):\n    if 'new' in item.name:\n"
                                    "        item.add_marker(pytest.mark.skip(reason='late'))\n        pytest.skip('late')\n"},
     "not produced by the census")])
def test_c2a14r_skips_and_replacements_the_census_does_not_reproduce_are_not_proven(tmp_path, name, files, needle):
    """FWK-OVSR7's C2a14 pre-read 1-5 (reproduced): a replaced function, a skip through a helper module, importorskip
    through it, a flipped skipif condition and a late marker each read complete. Under weekly-train:R15 a test skipped
    or xfailed in any phase is proven only when the census's own evaluation of its marks gives the same outcome and
    reason, and the function that runs must be the one the census collected."""
    _, report, token, text = _run_member(tmp_path / name, files,
                                         env_extra={"PYTHONPATH": str(tmp_path / name / "member" / "tests")})
    ids, why, _ = RB.report_failures(report, token, text)
    # changed at F4 (labelled; weekly-train:R27): a replaced test function is also refused by the witness
    assert ids == [] and why and (needle in why or name == "replace_fn" and "own code did not run" in why), \
        (why, text[-300:])


@requires_monitoring
def test_c2a14r_declared_skips_and_xfails_are_proven(tmp_path):
    """Control: a skip, a true skipif and an xfail declared in the test module are produced by the census too."""
    body = ("import pytest\ndef test_a():\n    pass\n@pytest.mark.skip(reason='s')\ndef test_s():\n    pass\n"
            "@pytest.mark.skipif(True, reason='c')\ndef test_c():\n    pass\n"
            "@pytest.mark.xfail(reason='x')\ndef test_x():\n    assert False\n")
    _, report, token, text = _run_member(tmp_path, {"test_s.py": body})
    assert RB.report_failures(report, token, text)[:2] == ([], None), text[-300:]


@requires_monitoring
def test_c2a14r_preread_7_a_collect_ignore_that_matched_nothing_is_no_narrowing(tmp_path):
    """FWK-OVSR7's C2a14 pre-read 7 (MEDIUM): `collect_ignore_glob = ["elsewhere/*"]` matching nothing narrowed the
    run. Only paths pytest's ignore hook actually skipped narrow it. Control: a pattern that matches does."""
    files = {"test_s.py": "def test_a():\n    pass\n", "conftest.py": "collect_ignore_glob = ['elsewhere/*']\n"}
    _, report, token, text = _run_member(tmp_path / "none", files)
    assert RB.report_failures(report, token, text)[:2] == ([], None), text[-300:]
    files = {"test_s.py": "def test_a():\n    pass\n", "test_b.py": "def test_b():\n    pass\n",
             "conftest.py": "collect_ignore_glob = ['test_b.py']\n"}
    _, report, token, text = _run_member(tmp_path / "some", files)
    assert RB.report_failures(report, token, text)[1], text[-300:]


@pytest.mark.parametrize("later", ["nice py${EMPTY}test -k x", "uv run py${E}test", "poetry run python -m py${E}test",
                                   "bash -c 'py${E}test -q'", "time py${E}test", "exec py${E}test",
                                   "/usr/bin/env py${E}test", "env -u X py${E}test"])
def test_c2a14r_preread_6_wrapped_unresolved_programs_are_mentions(later):
    """FWK-OVSR7's C2a14 pre-read 6 (reproduced): an unresolved program behind a wrapper or a shell `-c` string was no
    mention, so the earlier result was credited. Controls: `echo $HOME`, `nice ls`, `bash -c 'echo $HOME'`."""
    assert RB.mentions_suite(later, "python3 -m pytest")
    for other in ("echo $HOME", "nice ls", "bash -c 'echo $HOME'"):
        assert not RB.mentions_suite(other, "python3 -m pytest"), other


@requires_monitoring
def test_c2c_a_pycache_folder_under_the_tests_is_not_a_narrowing(tmp_path):
    """Found by BILD14 re-running the suite on C2a12 (intermittent in the parallel-runner test): pytest's own ignore
    hook skips `__pycache__`, and a run that met one read as "narrowed" (an availability defect). Control: an
    undeclared `--ignore` in addopts still narrows."""
    root = _tree_member(tmp_path, {"test_s.py": "def test_a():\n    pass\n"})
    (root / "tests" / "__pycache__").mkdir()
    report, token, env = under_report(tmp_path)
    text = native(root, BARE, env)[1]
    assert RB.report_failures(report, token, text)[:2] == ([], None), text[-300:]
    (root / "pytest.ini").write_text("[pytest]\naddopts = --ignore=tests/test_s.py\n")
    report, token, env = under_report(tmp_path, "r2.jsonl")
    text = native(root, BARE, env)[1]
    assert RB.report_failures(report, token, text)[1], text[-300:]


@requires_monitoring
def test_c2c_a_baseline_with_no_selection_witness_gives_no_policy(tmp_path):
    """Owed since B195/B196, FWK-OVSR6's C2a12 pre-read MEDIUM: F judged against a baseline holding no witness (`{}`)
    accepted a run with plugin autoload switched off. No witness, no policy: refused. Control: the same run against its
    own witness is complete."""
    _, report, token, text = _run_member(tmp_path / "off", {"test_s.py": "def test_a():\n    pass\n"},
                                         env_extra={"PYTEST_DISABLE_PLUGIN_AUTOLOAD": "1"})
    ids, why, _ = RB.report_failures(report, token, text, policy={})
    assert ids == [] and why and "holds no selection witness" in why, why
    own = RB.invocation_selection(report, token, text)
    assert RB.report_failures(report, token, text, policy=own)[:2] == ([], None)


def test_c2c_preread_h1_a_second_result_for_a_finished_run_is_refused_and_never_current(tmp_path):
    """FWK-OVSR7's C2c pre-read H1 (HIGH, reproduced): a second `write_result` for a run that had finished appended a
    second FINISHED row, and its PASS replaced the run's FAIL as current. The second write is refused before the file
    is touched; a log holding two FINISHED rows for the run is not current either. Control: the first write reads."""
    out = tmp_path / "ev" / "after_run_check.json"
    rid = RB.start_run("after_run_check", out)
    RB.write_result("after_run_check", out, {"verdict": "FAIL"}, rid)
    assert RB.read_current("after_run_check", out)[0]["verdict"] == "FAIL"
    with pytest.raises(RB.RunLogError):
        RB.write_result("after_run_check", out, {"verdict": "PASS"}, rid)
    assert RB.read_current("after_run_check", out)[0]["verdict"] == "FAIL"
    data = (json.dumps({"verdict": "PASS", "binding": {"run_id": rid}}, indent=2) + "\n").encode()
    RB.atomic_write(out, data)
    RB.finish_run("after_run_check", out, rid, data)        # the late row, appended past write_result
    doc, why = RB.read_current("after_run_check", out)
    assert doc is None and "2 FINISHED rows" in why, why


def test_c2c_preread_h2_a_finished_row_of_another_step_does_not_finish_the_run(tmp_path):
    """FWK-OVSR7's C2c pre-read H2 (HIGH, reproduced): the FINISHED lookup ignored the step, so a FINISHED row of step
    `rehearsal` finished an after_run_check run (PASS, reason None). Control: the run's own step finishes it."""
    out = tmp_path / "ev" / "after_run_check.json"
    rid = RB.start_run("after_run_check", out)
    data = (json.dumps({"verdict": "PASS", "binding": {"run_id": rid}}, indent=2) + "\n").encode()
    RB.atomic_write(out, data)
    RB.finish_run("rehearsal", out, rid, data)
    doc, why = RB.read_current("after_run_check", out)
    assert doc is None and "did not finish" in why, why
    with pytest.raises(RB.RunLogError):                      # nor does write_result write for a step not started
        RB.write_result("rehearsal", out, {"verdict": "PASS"}, rid)
    RB.finish_run("after_run_check", out, rid, data)
    assert RB.read_current("after_run_check", out) == ({"verdict": "PASS", "binding": {"run_id": rid}}, None)


def test_c2c_preread_m2_a_reused_run_id_that_started_again_and_never_finished_is_not_current(tmp_path):
    """FWK-OVSR7's C2c pre-read M2 (MEDIUM, reproduced through the public `run_id`): start X, finish, start X again and
    never finish, and the old result read current. The FINISHED row must follow the run's latest STARTED row."""
    out = tmp_path / "ev" / "baseline_record.json"
    RB.start_run("baseline", out, run_id="run-X")
    RB.write_result("baseline", out, {"failures": []}, "run-X")
    assert RB.read_current("baseline", out)[1] is None
    RB.start_run("baseline", out, run_id="run-X")
    doc, why = RB.read_current("baseline", out)
    assert doc is None and "did not finish" in why, why


@requires_monitoring
def test_c2c_preread_m1_a_partial_selection_witness_proves_no_selection(tmp_path):
    """FWK-OVSR7's C2c pre-read M1 (MEDIUM, reproduced): a test-module fixture replaced the plugin's witness with
    `{'unexpected': []}`; recorded as the baseline, the same partial witness approved a narrowed run. A witness (the
    run's or the baseline's) with any other key set than the kit's whole witness proves nothing. Control: the whole
    witness of the same run, recorded as its policy, is complete."""
    files = {"test_s.py": "def test_a():\n    pass\n"}
    hidden = {**files, "test_s.py": files["test_s.py"] + (
        "import pytest\n@pytest.fixture(autouse=True)\ndef _w():\n    import aget_kit_report as m\n"
        "    yield\n    m._selection.clear()\n    m._selection['unexpected'] = []\n")}
    _, report, token, text = _run_member(tmp_path / "partial", hidden)
    for policy in ({"unexpected": []}, "record"):
        ids, why, _ = RB.report_failures(report, token, text, policy=policy)
        assert ids == [] and why, (policy, text[-300:])
    assert RB.invocation_selection(report, token, text) is None
    _, report, token, text = _run_member(tmp_path / "whole", files)
    ids, why, _ = RB.report_failures(report, token, text, policy={"unexpected": []})
    assert ids == [] and why and "not the kit's whole witness" in why, why
    own = RB.invocation_selection(report, token, text)
    assert len(own) == 10 and RB.report_failures(report, token, text, policy=own)[:2] == ([], None)


@requires_monitoring
def test_c2c_preread_h3_a_parallel_run_is_judged_against_its_baselines_per_file_witness(tmp_path):
    """FWK-OVSR7's C2c pre-read H3 (HIGH, reproduced): the parallel runner's children were judged with no policy, so a
    baseline holding no witness, a malformed one or a foreign one read ([], None), where plain pytest refuses. A
    parallel run's policy is now each child's whole witness by its one root (`invocation_selection` records it).
    Control: the run against its own recorded policy is complete."""
    root = member(tmp_path, {"test_a.py": "def test_a():\n    pass\n", "test_b.py": "def test_b():\n    pass\n"})
    report, token, env = under_report(tmp_path)
    p, text = native(root, f"{sys.executable} {RUNNER}", env)
    for policy in ({}, {"roots": None}, {"roots": ["elsewhere"]}):
        ids, why, _ = RB.report_failures(report, token, text, exit_code=p.returncode, policy=policy)
        assert ids == [] and why, policy
    own = RB.invocation_selection(report, token, text)
    assert own and set(own) == {"per_file"} and sorted(own["per_file"]) == ["tests/test_a.py", "tests/test_b.py"]
    assert RB.report_failures(report, token, text, exit_code=p.returncode, policy=own)[:2] == ([], None), text[-400:]
    one = sorted(own["per_file"])[0]
    changed = {"per_file": {**own["per_file"], one: {**own["per_file"][one], "autoload": ["on-changed"]}}}
    fewer = {"per_file": {one: own["per_file"][one]}}
    for policy in (own["per_file"][one], changed, fewer):
        ids, why, _ = RB.report_failures(report, token, text, exit_code=p.returncode, policy=policy)
        assert ids == [] and why, policy


def test_c2c_preread_m3_baseline_equal_ruled_reads_the_current_baseline_by_default(tmp_path):
    """FWK-OVSR7's C2c pre-read M3 (MEDIUM, function level; the gate route was not reproduced): with `base` omitted,
    `baseline_equal_ruled` read the baseline record raw. Its default read is now `read_current`: a hand-written record
    names no run and is refused with that reason."""
    PB = load("push_batch")
    ev = tmp_path / "ev"
    ev.mkdir()
    (ev / "baseline_equal_ruling.json").write_text(json.dumps({"sha": "0" * 40, "line": "x"}))
    (ev / "baseline_record.json").write_text(json.dumps({"failures": [], "complete": True}))
    ok, why = PB.baseline_equal_ruled(ev, {}, "1" * 40)
    assert ok is False and "not current" in why, why


# --- REVW9's B198 read (C2a15) ----------------------------------------------------------------------------------

_B198_TESTS = "def test_control():\n    pass\ndef bad():\n    assert False\ndef good():\n    pass\ndef test_new():\n    bad()\n"


@requires_monitoring
@pytest.mark.parametrize("case", ["co_names", "rebound_helper", "collect_patch"])
def test_c2a15_b198_1_changed_execution_or_collection_machinery_is_not_proven(tmp_path, case):
    """B198 finding 1 (HIGH, continuing): (i) a conftest changed only `test_new`'s code-name table
    (`__code__.replace(co_names=("good",))`), and the identity hashed bytecode and constants only: 2 passed, complete;
    a conftest rebinding the module-level helper the test calls is the same class; (ii) a test module patching
    `_pytest.python.Module.collect` hid a test from the census and the run alike. Each now reads not proven.
    Control: the same files without the change surface the failing test."""
    files = {"test_s.py": _B198_TESTS}
    _, report, token, text = _run_member(tmp_path / "plain", files)
    assert RB.report_failures(report, token, text)[:2] == (["tests/test_s.py::test_new"], None), text[-300:]
    if case == "co_names":
        files["conftest.py"] = ("def pytest_collection_modifyitems(items):\n    for i in items:\n"
                                "        if i.name == 'test_new':\n"
                                "            i.obj.__code__ = i.obj.__code__.replace(co_names=('good',))\n")
    elif case == "rebound_helper":
        files["conftest.py"] = ("def pytest_collection_modifyitems(items):\n    for i in items:\n"
                                "        if i.name == 'test_new':\n"
                                "            i.obj.__globals__['bad'] = i.obj.__globals__['good']\n")
    else:
        files["test_0_patch.py"] = ("import _pytest.python as P\n_orig = P.Module.collect\n"
                                    "def limited(self):\n    return [i for i in _orig(self) if i.name != 'test_new']\n"
                                    "P.Module.collect = limited\ndef test_patch_control():\n    pass\n")
    _, report, token, text = _run_member(tmp_path / case, files)
    ids, why, _ = RB.report_failures(report, token, text)
    # changed at F4 (labelled; weekly-train:R27, R15 (a)): a helper or default swapped by setup is setup; the
    # declared test's own code ran, so the run is complete (REVW11's B202 asked for each old probe reinterpreted)
    assert ids == [] and ((why is None) if case == "rebound_helper" else why), (case, text[-300:])


@pytest.mark.parametrize("later", ["python -c \"import importlib; importlib.import_module('py'+'test').main()\"",
                                   "python3 -Bc 'import pytest; pytest.main()'", "python3 - <<EOF", "echo x | python3"])
def test_c2a15_b198_2_later_interpreter_code_is_a_mention(later):
    """B198 finding 2 (HIGH, continuing): a later `python -c` program that imports pytest by a computed name really
    ran the suite, was no mention, and the earlier pass was credited. Interpreter code the kit cannot resolve (`-c`,
    a `-Bc` cluster, stdin) is a mention. Controls: a named script, `--version`, `ls`."""
    assert RB.mentions_suite(later, "python3 -m pytest")
    for other in ("python3 scripts/wake_up.py", "python3 --version", "python3 -B scripts/x.py --json", "ls"):
        assert not RB.mentions_suite(other, "python3 -m pytest"), other


@requires_monitoring
def test_c2a15_b198_3_the_census_output_is_a_pipe_with_no_storage_to_share(tmp_path):
    """B198 finding 3 (HIGH, continuing): census-side test-module code hardlinked the inode of its inherited output
    descriptor before the census wrote, so the kit's later refusal came after a write through shared storage. The
    descriptor is now a pipe: no inode a path can name. The test module records what it was handed."""
    seen = tmp_path / "seen.txt"
    probe = ("import os, stat\nfd = os.environ.get('AGET_KIT_CENSUS_FD')\nif fd:\n"
             f"    open({str(seen)!r}, 'w').write('fifo' if stat.S_ISFIFO(os.fstat(int(fd)).st_mode) else 'file')\n"
             "def test_a():\n    pass\n")
    _, report, token, text = _run_member(tmp_path / "m", {"test_s.py": probe})
    assert seen.read_text() == "fifo", seen.read_text()
    assert RB.report_failures(report, token, text)[:2] == ([], None), text[-300:]


def test_c2a15_b198_4_prescan_reads_options_as_argparse_does():
    """B198 finding 4 (HIGH, new): `--evidence OTHER --evidence EFFECTIVE`: the first-act prescan took the first value
    and argparse the last, so the attempt invalidated OTHER and EFFECTIVE's earlier PASS stayed current. The prescan
    now takes the last occurrence and argparse's unambiguous abbreviations, and stops at a bare `--`."""
    assert RB.prescan(["--evidence", "OTHER", "--evidence", "EFFECTIVE"], "--evidence") == "EFFECTIVE"
    assert RB.prescan(["--evidence", "OTHER", "--evidence=EFFECTIVE"], "--evidence") == "EFFECTIVE"
    assert RB.prescan(["--evidence", "A", "--evid", "B"], "--evidence") == "B"
    assert RB.prescan(["--evidence", "A", "--", "--evidence", "B"], "--evidence") == "A"
    assert RB.prescan(["--aget", "x"], "--evidence") is None


# --- FWK-OVSR8's C2a15 + C2e pre-read (reproduced on the saved C2e; D2) -----------------------------------------

@pytest.mark.parametrize("later", ["if true; then python -c 'import importlib'; fi", "! python3 -c x",
                                   "for f in a; do python3 -c x; done", "while python3 -c x; do :; done"])
def test_d2_preread_1_a_shell_keyword_before_later_interpreter_code_is_a_mention(later):
    """FWK-OVSR8's C2a15+C2e pre-read 1 (reproduced): `then`/`do`/`else`/`!` opening a command hid the later
    `python -c` suite run (no mention, the earlier result credited). A keyword is not the program."""
    assert RB.mentions_suite(later, "python3 -m pytest"), later


@requires_monitoring
def test_d2_preread_3_a_callable_default_swapped_for_a_no_op_changes_the_identity(tmp_path):
    """FWK-OVSR8's C2a15+C2e pre-read 3 (reproduced): an unmarshallable default (a function) collapsed to its type
    name, so a conftest swapping a test's callable default for a no-op kept the identity. Control: plain run."""
    tests = ("def bad():\n    assert False\ndef test_control():\n    pass\n"
             "def test_new(check=bad):\n    check()\n")
    _, report, token, text = _run_member(tmp_path / "plain", {"test_s.py": tests})
    assert RB.report_failures(report, token, text)[:2] == (["tests/test_s.py::test_new"], None), text[-300:]
    swap = ("def pytest_collection_modifyitems(items):\n    for i in items:\n        if i.name == 'test_new':\n"
            "            i.obj.__defaults__ = (lambda: None,)\n")
    _, report, token, text = _run_member(tmp_path / "swap", {"test_s.py": tests, "conftest.py": swap})
    ids, why, _ = RB.report_failures(report, token, text)
    # changed at F4 (labelled; weekly-train:R27, R15 (a)): a helper or default swapped by setup is setup; the
    # declared test's own code ran, so the run is complete (REVW11's B202 asked for each old probe reinterpreted)
    assert ids == [] and why is None, text[-300:]


def test_d2_preread_2_an_empty_option_value_is_a_value_for_the_first_act():
    """FWK-OVSR8's C2a15+C2e pre-read 2 (reproduced): a repeated final `--evidence=` with an empty value read as
    absent (falsy), so the first act invalidated nothing while argparse took "" for the run. The producers now test
    `is not None`; prescan returns the empty string."""
    assert RB.prescan(["--evidence=/x", "--evidence="], "--evidence") == ""
    src = (BATCH / "suite_at_commit.py").read_text()
    assert "if ev_arg is not None and aget_arg is not None:" in src


# --- REVW9's B199 read (D2) --------------------------------------------------------------------------------------

@requires_monitoring
@pytest.mark.parametrize("case", ["item_runtest", "pyfunc_hook", "restored_collection"])
def test_d2_b199_1_execution_machinery_the_kit_cannot_account_for_is_not_proven(tmp_path, case):
    """B199 finding 1 (HIGH, continuing; answer (a): execution-phase omissions are inside the class): an item whose
    `runtest` was replaced on the instance, a member `pytest_pyfunc_call` returning True, and a collector patched by
    one module's import and restored before collection ended each read complete. Each now reads not proven.
    Control: the plain files surface the failing test."""
    files = {"test_s.py": _B198_TESTS}
    _, report, token, text = _run_member(tmp_path / "plain", files)
    assert RB.report_failures(report, token, text)[:2] == (["tests/test_s.py::test_new"], None), text[-300:]
    if case == "item_runtest":
        files["conftest.py"] = ("def pytest_collection_modifyitems(items):\n    for i in items:\n"
                                "        if i.name == 'test_new':\n            i.runtest = lambda: None\n")
    elif case == "pyfunc_hook":
        files["conftest.py"] = ("def pytest_pyfunc_call(pyfuncitem):\n"
                                "    return True if pyfuncitem.name == 'test_new' else None\n")
    else:
        files["test_0_patch.py"] = ("import _pytest.python as P\n_orig = P.Module.collect\n"
                                    "def limited(self):\n    return [i for i in _orig(self) if i.name != 'test_new']\n"
                                    "P.Module.collect = limited\ndef test_patch_control():\n    pass\n")
        files["test_t_restore.py"] = ("import _pytest.python as P, test_0_patch as X\nP.Module.collect = X._orig\n"
                                      "def test_restore_control():\n    pass\n")
    _, report, token, text = _run_member(tmp_path / case, files)
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why, (case, text[-300:])


def test_d2_b199_2_a_later_call_whose_output_shows_a_pytest_run_is_not_ignored():
    """B199 finding 2 (HIGH, continuing; no named-script waiver): a later named local script really ran pytest (its
    output holds a count line), was no mention, and the earlier pass was credited. A later call of any form whose own
    output shows a pytest run now leaves the result unavailable. Control: a later call with ordinary output."""
    suite = "python3 -m pytest"
    def stream(later_out):
        ev = []
        for i, (cmd, out) in enumerate([(suite, "aget-kit-report: pytest " + "a" * 32 + "\n1 passed in 0.01s"),
                                        ("python3 scripts/check.py", later_out)]):
            ev += [{"sessionId": "S", "message": {"content": [{"type": "tool_use", "id": f"u{i}", "name": "Bash",
                                                                "input": {"command": cmd}}]}},
                   {"sessionId": "S", "message": {"content": [{"type": "tool_result", "tool_use_id": f"u{i}",
                                                                "content": out}]}}]
        return "\n".join(json.dumps(e) for e in ev)
    got, why = RB.last_call_output(stream("1 failed, 1 passed in 0.02s"), lambda c: RB.is_suite_run(c, suite),
                                   bash_only=True, mentions=lambda c: RB.mentions_suite(c, suite))
    assert got is None and "shows a pytest run" in why, why
    got, why = RB.last_call_output(stream("checked 3 files"), lambda c: RB.is_suite_run(c, suite),
                                   bash_only=True, mentions=lambda c: RB.mentions_suite(c, suite))
    assert why is None and "1 passed" in got


@requires_monitoring
def test_d2_preread_7_a_self_restoring_collection_patch_in_the_test_module_is_not_proven(tmp_path):
    """FWK-OVSR8's C2a15+C2e pre-read 7 (reproduced on the saved D2 first build): a test module patched
    `PyCollector.collect` to hide its own `test_hidden` and restored the patch inside that one collect call, so no
    hook boundary saw it and the census (importing the same module) agreed: complete. After each test module is
    collected, every test function defined in it must be an item. Control: the module without the patch."""
    body = "def test_visible():\n    pass\ndef test_hidden():\n    assert False\n"
    _, report, token, text = _run_member(tmp_path / "plain", {"test_mod.py": body})
    assert RB.report_failures(report, token, text)[:2] == (["tests/test_mod.py::test_hidden"], None), text[-300:]
    patch = ("from _pytest.python import PyCollector\n_old = PyCollector.collect\n"
             "def _once(self):\n    PyCollector.collect = _old\n"
             "    return [i for i in _old(self) if i.name != 'test_hidden']\n"
             "PyCollector.collect = _once\n")
    _, report, token, text = _run_member(tmp_path / "patched", {"test_mod.py": patch + body})
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why and "defined in its module" in why, (why, text[-300:])


@requires_monitoring
def test_d2_overseer_preread_1_a_testcase_overriding_how_its_test_runs_is_not_proven(tmp_path):
    """FWK-OVSR9's D2 pre-read 1 (reproduced on the first D2 save): a unittest.TestCase overriding `run()` to return
    None read "1 passed", complete, with its failing test never run. A TestCase class that overrides how its test
    method is run (`run`, `__call__`, `debug`, `_callTestMethod`, …) is not proven. Control: no override."""
    base = "import unittest\nclass MyTest(unittest.TestCase):\n{over}    def test_bad(self):\n        self.fail('x')\n"
    _, report, token, text = _run_member(tmp_path / "plain", {"test_tc.py": base.format(over="")})
    assert RB.report_failures(report, token, text)[:2] == (["tests/test_tc.py::MyTest::test_bad"], None), text[-300:]
    over = "    def run(self, result=None):\n        return None\n"
    _, report, token, text = _run_member(tmp_path / "over", {"test_tc.py": base.format(over=over)})
    ids, why, _ = RB.report_failures(report, token, text)
    assert ids == [] and why, text[-300:]


def test_d2_overseer_preread_2_a_valueless_repeated_option_never_takes_the_next_option_as_its_path():
    """FWK-OVSR9's D2 pre-read 2 (mechanism): `--evidence A --evidence --packet p` made prescan return `--packet` as
    the evidence path. argparse refuses the valueless flag; the earlier value stays the one invalidated."""
    assert RB.prescan(["--evidence", "A", "--evidence", "--packet", "p"], "--evidence") == "A"
    assert RB.prescan(["--evidence", "-", "--packet", "p"], "--evidence") == "-"


# --- REVW10's B200 read (D3) -------------------------------------------------------------------------------------

_B200_HELPER = "def bad():\n    assert False\ndef good():\n    pass\ndef check(action=bad):\n    action()\n"


@requires_monitoring
@pytest.mark.parametrize("case", ["unregistered_execution_hook", "helper_callable_default", "nested_callable_default"])
def test_d3_b200_1_execution_history_and_delegated_callables_are_proven_or_refused(tmp_path, case):
    """B200 finding 1 (HIGH, continuing; REVW10's three falsifiers): (a) a conftest's `pytest_pyfunc_call` that
    unregisters its own plugin was absent from the final hook list D2 scanned; (b) a collection hook changed the
    default of a helper the test calls, and identity hashed the helper's code only; (c) it changed the default inside
    the callable that is the test's own default, and identity hashed that callable's code only. Each read "1 passed",
    complete, with the failing body never run; each now reads not proven. Control: the files with no conftest
    surface the failure."""
    if case == "unregistered_execution_hook":
        body = "def test_new():\n    assert False\n"
        hook = ("import sys\ndef pytest_pyfunc_call(pyfuncitem):\n"
                "    pyfuncitem.config.pluginmanager.unregister(sys.modules[__name__])\n    return True\n")
    elif case == "helper_callable_default":
        body = _B200_HELPER + "def test_new():\n    check()\n"
        hook = ("def pytest_collection_modifyitems(items):\n    for i in items:\n        if i.name == 'test_new':\n"
                "            i.obj.__globals__['check'].__defaults__ = (i.obj.__globals__['good'],)\n")
    else:
        body = _B200_HELPER + "def test_new(action=check):\n    action()\n"
        hook = ("def pytest_collection_modifyitems(items):\n    for i in items:\n        if i.name == 'test_new':\n"
                "            i.obj.__defaults__[0].__defaults__ = (i.obj.__globals__['good'],)\n")
    _, report, token, text = _run_member(tmp_path / "plain", {"test_s.py": body})
    assert RB.report_failures(report, token, text)[:2] == (["tests/test_s.py::test_new"], None), text[-300:]
    _, report, token, text = _run_member(tmp_path / case, {"test_s.py": body, "conftest.py": hook})
    assert "1 passed" in text, text[-300:]          # the body did not run: the falsifier's own premise
    ids, why, _ = RB.report_failures(report, token, text)
    # changed at F4 (labelled; weekly-train:R27, R15 (a)): a helper or default swapped by setup is setup; the
    # declared test's own code ran, so the run is complete (REVW11's B202 asked for each old probe reinterpreted)
    assert ids == [] and ((why is None) if case.endswith("callable_default") else why), (case, text[-300:])


@requires_monitoring
def test_d3_b200_1_an_unchanged_helper_and_default_still_read_complete(tmp_path):
    """The other side of B200 finding 1's repair: hashing defaults and closures must not refuse an unchanged test.
    A test with a callable default whose helper has a default, a partial and a builtin reads complete."""
    body = ("import functools\n" + _B200_HELPER.replace("assert False", "pass") +
            "@functools.lru_cache\ndef cached():\n    return 1\n"
            "def test_ok(action=check, p=functools.partial(check, good), b=len, c=cached):\n    action(); p(); b([]); c()\n")
    _, report, token, text = _run_member(tmp_path / "ok", {"test_s.py": body})
    assert RB.report_failures(report, token, text)[:2] == ([], None), text[-300:]


# --- weekly-train:R17 (F3): a narrowed population counts only with a recorded approval of its selection ----------

@requires_monitoring
def test_f3_r17_a_narrowed_population_needs_an_approval_of_its_exact_selection(tmp_path):
    """weekly-train:R17 (principal, 2026-10-05 ~00:2x): "The kit accepts a narrowed population only with a recorded
    approval of that narrowing; without one the suite reads INCONCLUSIVE naming the missing approval." On D3 F counted
    a narrowed run whose selection equalled the baseline's with no approval. An approval of another selection does not
    count; an unnarrowed run needs none."""
    files = {"test_s.py": "def test_a():\n    pass\n", "templates/test_t.py": "def test_t():\n    pass\n",
             "conftest.py": "collect_ignore_glob = ['templates/*']\n"}
    _, report, token, text = _run_member(tmp_path / "narrow", files)
    base = RB.invocation_selection(report, token, text)
    ids, why, _ = RB.report_failures(report, token, text, policy=base)
    assert ids == [] and why and "no recorded approval of its selection" in why, why
    assert RB.report_failures(report, token, text, policy=base, approved={"0" * 64})[1]
    assert RB.report_failures(report, token, text, policy=base, approved={RB.selection_digest(base)})[1] is None
    _, report, token, text = _run_member(tmp_path / "plain", {"test_s.py": "def test_a():\n    pass\n"})
    plain = RB.invocation_selection(report, token, text)
    assert RB.report_failures(report, token, text, policy=plain)[1] is None          # nothing narrowed: no approval


@requires_monitoring
def test_f4_r17_an_unapproved_narrowed_baseline_is_not_complete_but_keeps_its_witness(tmp_path):
    """B201 finding 2 (REVW11's `revw11_r17_cost_probes.py::test_kit_refuses_to_call_an_unapproved_narrowed_baseline_complete`):
    the baseline producer read a narrowed suite with policy "record", which F3 exempted, so an unapproved narrowed
    suite was complete and RECORDED. Now the baseline (policy "baseline") keeps the selection witness, so it can be
    approved, and reads INCONCLUSIVE naming the missing approval until that exact selection is approved. Controls:
    F already refuses the same unapproved selection; an unnarrowed baseline needs no approval."""
    files = {"test_s.py": "def test_a():\n    pass\n", "templates/test_t.py": "def test_t():\n    pass\n",
             "conftest.py": "collect_ignore_glob = ['templates/*']\n"}
    _, report, token, text = _run_member(tmp_path / "narrow", files)
    sel = RB.invocation_selection(report, token, text)
    assert "no recorded approval" in RB.report_failures(report, token, text, policy=sel)[1]          # control: F
    parsed = LB.parse_baseline(stream(text, BARE), BARE, report, token)
    assert not parsed["complete"] and "no recorded approval of its selection" in parsed["failures_unknown"], parsed
    assert parsed["selection"] == sel and sel                                     # the witness is kept to approve
    assert not LB.parse_baseline(stream(text, BARE), BARE, report, token, approved={"0" * 64})["complete"]
    assert LB.parse_baseline(stream(text, BARE), BARE, report, token,
                             approved={RB.selection_digest(sel)})["complete"]
    _, report, token, text = _run_member(tmp_path / "plain", {"test_s.py": "def test_a():\n    pass\n"})
    assert LB.parse_baseline(stream(text, BARE), BARE, report, token)["complete"]      # control: nothing narrowed


def test_f4_r17_the_baseline_reads_the_member_s_recorded_approvals():
    """B201 finding 2, the producer's wiring: `run_baseline` passes the member's recorded approvals (the same reader
    F uses, `after_run_check.policy_approvals`) to the baseline parser."""
    src = (BATCH / "launch_batch.py").read_text()
    assert "parse_baseline(p.stdout, suite_cmd, report, token, approved=ARC.policy_approvals(r[\"aget\"]))" in src


@requires_monitoring
@pytest.mark.parametrize("variant", ["exact", "append_report", "insert_report"])
def test_b216_reporting_only_placement_keeps_a_native_full_suite_complete(tmp_path, variant):
    """B216 falsifier: native two-test baseline/current reports reach F with complete bound identities."""
    import shlex
    pl = load("prepare_launch")
    root = member(tmp_path, {"test_member.py": "def test_a():\n    pass\ndef test_b():\n    pass\n"})
    head, declared = g(root, "rev-parse", "HEAD"), pl.suite_command({})

    def run(command, env):
        words = shlex.split(command)
        assert words[0] == "python3"
        p = subprocess.run([sys.executable, *words[1:]], cwd=root, env=env,
                           capture_output=True, text=True, timeout=30)
        assert p.returncode == 0, (p.stdout, p.stderr)
        return p.stdout + p.stderr

    baseline_report, baseline_token, env = under_report(tmp_path, "baseline.jsonl")
    text = run(pl.BASELINE_CMD, env)
    parsed = LB.parse_baseline(stream(text, pl.BASELINE_CMD), pl.BASELINE_CMD, baseline_report, baseline_token)
    assert parsed["complete"], parsed
    baseline = tmp_path / "baseline_record.json"
    produce(baseline, "baseline", dict(aget="a", head=head, verdict="RECORDED", output_complete=True,
                                      failures=parsed["failures"], selection=parsed["selection"]))
    command = {"exact": declared, "append_report": declared + " -rfE", "insert_report": pl.BASELINE_CMD}[variant]
    report, token, env = under_report(tmp_path, "current.jsonl")
    text = run(command, env)
    transcript = tmp_path / "transcript.jsonl"
    transcript.write_text(stream(text, command))
    ids, why, events = RB.report_failures(report, token, text, outcomes=True, policy=parsed["selection"])
    assert ids == [] and why is None
    assert len({event["nodeid"] for event in events}) == 2
    assert not (root / ".pytest_cache").exists()
    result = A.suite_regressions(transcript, declared, baseline, "a", head, report=report, token=token)
    assert result == ([], None), (command, declared, result)


@pytest.mark.parametrize("later", [
    "python3 -m pytest -q tests/test_a.py", "python3 -m pytest -q -k only_one",
    "python3 -m pytest -q -x", "python3 -m pytest -q",
    # Keep the same refusals when all declared flags are present, too.
    "python3 -m pytest -q -p no:cacheprovider tests/test_a.py",
    "python3 -m pytest -q -p no:cacheprovider -k only_one",
    "python3 -m pytest -q -p no:cacheprovider -x",
    "python3 -m pytest -p no:cacheprovider",  # cannot omit declared -q either
])
def test_b216_later_nonmatching_run_cannot_reuse_the_previous_complete_result(later):
    """B216's four later-run controls plus fully declared narrowed runs and a missing declared -q."""
    declared = load("prepare_launch").suite_command({})
    earlier = stream("2 passed in 0.1s", declared)
    later_stream = stream("1 passed in 0.1s", later).replace("u1", "u2")
    out, why = RB.last_call_output(earlier + later_stream, lambda c: RB.is_suite_run(c, declared),
                                  bash_only=True, mentions=lambda c: RB.mentions_suite(c, declared))
    assert out is None and why, (later, out, why)


@pytest.mark.parametrize("extra", ["-q", "-qq", "-v", "-vv", "-rfE", "--tb=short", "--no-header",
                                    "-p no:cacheprovider", "--color=no", "--durations=1"])
def test_b216_each_permitted_report_flag_can_be_interleaved_without_reordering_declared_tokens(extra):
    # Cache-provider option and value are one argument pair; no insertion inside the pair.
    words = ["python3", "-m", "pytest", "-q", "-p no:cacheprovider"]
    declared = " ".join(words)
    for at in range(1, len(words) + 1):
        command = " ".join(words[:at] + [extra] + words[at:])
        assert RB.is_suite_run(command, declared), (at, extra, command)
    assert not RB.is_suite_run("-rfE " + declared, declared)  # preserve the executable
    assert not RB.is_suite_run("python3 -m pytest -q -p -rfE no:cacheprovider", declared)
    assert not RB.is_suite_run("python3 pytest -m -q -p no:cacheprovider", declared)
    assert not RB.is_suite_run(declared + " --maxfail=1", declared)
    quoted_pair = "python3 -m pytest -q '-p no:cacheprovider'"
    assert not RB.is_suite_run(quoted_pair, declared)
    assert not RB.is_suite_run(declared, quoted_pair)


def test_without_sys_monitoring_a_native_pass_is_inconclusive(tmp_path):
    """Below 3.12 the native path refuses; newer Pythons exercise the same missing-facility path in a child."""
    root = member(tmp_path, {
        "test_x.py": "def test_x():\n    assert True\n",
        "conftest.py": "import sys\nif hasattr(sys, 'monitoring'):\n    del sys.monitoring\n",
    })
    report, token, env = under_report(tmp_path)
    p, text = native(root, PYTEST, env)
    ids, why, _ = RB.report_failures(report, token, text)
    assert p.returncode == 0 and "1 passed" in text, text
    assert ids == [] and why and "this Python has no sys.monitoring" in why, (ids, why)
    parsed = LB.parse_baseline(stream(text, PYTEST), PYTEST, report, token)
    assert parsed["complete"] is False and "this Python has no sys.monitoring" in parsed["failures_unknown"], parsed
