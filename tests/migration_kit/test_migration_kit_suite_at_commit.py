"""Tests for batch1/suite_at_commit.py (SOP B8a v1.31.0; plan G3.6 row 13 (a)). Hermetic git fixtures only."""
from _kit_report import requires_monitoring

import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_s = importlib.util.spec_from_file_location(
    "suite_at_commit", ROOT / "scripts/migration_kit/suite_at_commit.py")
S = importlib.util.module_from_spec(_s)
_s.loader.exec_module(S)
PYTEST = f"{sys.executable} -m pytest -q -p no:cacheprovider"
LOGS = ("from pathlib import Path\n\ndef test_appends_to_a_tracked_log():\n"
        "    with open(Path(__file__).resolve().parents[1] / 'logs' / 'run.log', 'a') as f:\n"
        "        f.write('ran\\n')\n")


def repo(tmp_path, tests, workflow=None, known=None):
    loc = tmp_path / "home" / "seat"
    (loc / "tests").mkdir(parents=True)
    (loc / "tests" / "test_x.py").write_text(tests)
    if workflow:
        (loc / ".github" / "workflows").mkdir(parents=True)
        (loc / ".github" / "workflows" / "ci.yml").write_text(workflow)
    if known:
        (loc / "tests" / "ci_known_failures.txt").write_text(known)
    def g(*a):
        return subprocess.run(["git", "-C", str(loc), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                              check=True, capture_output=True, text=True).stdout.strip()
    g("init", "-q")
    g("add", "-A")
    g("commit", "-q", "-m", "c")
    return loc, g


@requires_monitoring
def test_pass_and_fail_are_read_from_the_exact_commit_in_a_clean_clone(tmp_path):
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n")
    good = g("rev-parse", "HEAD")
    (loc / "tests" / "test_x.py").write_text("def test_a():\n    assert False\n")
    g("commit", "-q", "-am", "break")
    bad = g("rev-parse", "HEAD")
    (loc / "tests" / "test_x.py").write_text("def test_a():\n    assert True\n")   # the live folder is clean again,
    r1 = S.run(loc, "seat", good, PYTEST, work=tmp_path / "w")                    # uncommitted: never read
    r2 = S.run(loc, "seat", bad, PYTEST, work=tmp_path / "w")
    assert r1["verdict"] == "PASS" and r1["sha"] == good
    assert r2["verdict"] == "FAIL" and r2["failures"] == ["tests/test_x.py::test_a"]
    assert S.run(loc, "seat", "0" * 40, PYTEST, work=tmp_path / "w")["verdict"] == "INCONCLUSIVE"


def test_a_suite_that_pushes_cannot_reach_the_real_repository(tmp_path):
    """one receiver 2026-09-29: its wind-down commits and pushes inside a suite run; from the clean clone that pushed
    into the real repo. The clone's push URL is disabled, so the push fails and the real repo gets no new ref."""
    loc, g = repo(tmp_path, "import subprocess\n\ndef test_pushes():\n"
                            "    subprocess.run(['git', '-c', 'user.name=t', '-c', 'user.email=t@t', 'commit', '-q',\n"
                            "                    '--allow-empty', '-m', 'rogue'])\n"
                            "    subprocess.run(['git', 'push', '-q', 'origin', 'HEAD:refs/heads/rogue'])\n")
    sha = g("rev-parse", "HEAD")
    r = S.run(loc, "seat", sha, PYTEST, work=tmp_path / "w")
    # the suite committed inside the clone, so the tested commit is not the one that passed: never PASS
    assert r["verdict"] == "INCONCLUSIVE" and r["head_after"] != sha and "moved the clone's HEAD" in r["why"]
    assert g("branch", "--list", "rogue") == ""
    clone, = (tmp_path / "w").glob("*/seat.root/seat")   # E2g: the clone sits in this run's own folder
    assert subprocess.run(["git", "-C", str(clone), "remote", "get-url", "--push", "origin"],
                          capture_output=True, text=True).stdout.strip() == S.NO_PUSH_URL


@requires_monitoring
def test_processes_a_suite_leaves_running_are_killed_with_its_group(tmp_path):
    """2026-09-29 17:51: orphaned `pytest -q` processes survived the suite that started them. The run now owns a
    process group and kills it afterwards, so a background child is gone when the record is written."""
    import os
    pidfile = tmp_path / "bg.pid"
    loc, g = repo(tmp_path, "import subprocess\n\ndef test_spawns():\n"
                            "    p = subprocess.Popen(['sleep', '60'])\n"
                            f"    open({str(pidfile)!r}, 'w').write(str(p.pid))\n")
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, work=tmp_path / "w")
    assert r["verdict"] == "PASS"
    pid = int(pidfile.read_text())
    import time
    for _ in range(20):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            break
        time.sleep(0.1)
    else:
        raise AssertionError(f"background process {pid} outlived the suite run")


def test_a_timeout_kills_the_whole_group(tmp_path):
    loc, g = repo(tmp_path, "import subprocess, time\n\ndef test_slow():\n"
                            "    subprocess.Popen(['sleep', '60'])\n    time.sleep(30)\n")
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, work=tmp_path / "w", timeout=3)
    assert r["verdict"] == "INCONCLUSIVE" and "process group killed" in r["why"]


@requires_monitoring
def test_ci_exclusions_are_applied_and_disclosed(tmp_path):
    """The framework Aget's CI deselects a named file of known failures; the stand-in must do the same, or it fails
    where CI passes."""
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n\ndef test_known():\n    assert False\n",
                  workflow="run: cat tests/ci_known_failures.txt | sed 's/^/--deselect /'\n",
                  known="tests/test_x.py::test_known\n")
    rec = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, work=tmp_path / "w")
    assert rec["verdict"] == "PASS", rec
    assert rec["excluded"] == ["tests/test_x.py::test_known"] and "tests/ci_known_failures.txt (1)" in rec[
        "exclusion_sources"]


@requires_monitoring
def test_the_agets_own_pre_push_hook_runs_too_and_its_failure_fails(tmp_path):
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n")
    hook = loc / ".git" / "hooks" / "pre-push"
    hook.write_text("#!/bin/sh\necho gate says no\nexit 1\n")
    hook.chmod(0o755)
    rec = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, work=tmp_path / "w")
    assert rec["verdict"] == "FAIL" and rec["hook"]["present"] and rec["hook"]["exit"] == 1
    hook.write_text("#!/bin/sh\nexit 0\n")
    assert S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, work=tmp_path / "w")["verdict"] == "PASS"


def test_f3_a_pre_push_hook_past_the_timeout_reads_inconclusive_not_a_traceback(tmp_path):
    """F3 (BILD16's reason map, class 12): the suite's timeout was caught, the hook's was not, so a hook that ran past
    it stopped the tool with a traceback and left the record not finished. It reads INCONCLUSIVE, naming the hook."""
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n")
    hook = loc / ".git" / "hooks" / "pre-push"
    hook.write_text("#!/bin/sh\nsleep 30\n")
    hook.chmod(0o755)
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, work=tmp_path / "w", timeout=8)
    assert r["verdict"] == "INCONCLUSIVE" and "pre-push hook timed out" in r["why"], r
    assert r["hook"]["present"] and r["hook"]["run"] is True and r["hook"]["exit"] is None


@requires_monitoring
def test_declared_siblings_are_copied_beside_the_clone(tmp_path):
    loc, g = repo(tmp_path, "from pathlib import Path\n\ndef test_sib():\n"
                            "    assert (Path(__file__).parents[2] / 'sib' / 'x.txt').exists()\n")
    (loc.parent / "sib").mkdir()
    (loc.parent / "sib" / "x.txt").write_text("x\n")
    sha = g("rev-parse", "HEAD")
    assert S.run(loc, "seat", sha, PYTEST, work=tmp_path / "w")["verdict"] == "FAIL"          # blind without it
    assert S.run(loc, "seat", sha, PYTEST, ["../sib"], work=tmp_path / "w")["verdict"] == "PASS"


@requires_monitoring
def test_review_fixes_env_sibling_ref_and_exclusions_come_from_the_commit(tmp_path, monkeypatch):
    """The framework Aget's review of e046a182: (1) a sibling is checked out at its remote default branch, not the
    live checkout's branch or dirt; (2) CLAUDE_PROJECT_DIR is the clone, AGET_TWG_* dropped; (3) the deselect file is
    read from the commit under test, not the live folder."""
    monkeypatch.setenv("CLAUDE_PROJECT_DIR", "/the/callers/live/folder")
    monkeypatch.setenv("AGET_TWG_WINDOW", "x")
    loc, g = repo(tmp_path,
                  "import os\nfrom pathlib import Path\n\n"
                  "def test_env():\n    assert Path(os.environ['CLAUDE_PROJECT_DIR']) == Path(__file__).resolve().parents[1]\n"
                  "    assert 'AGET_TWG_WINDOW' not in os.environ\n\n"
                  "def test_sib():\n    assert (Path(__file__).parents[2] / 'sib' / 'f.txt').read_text() == 'main\\n'\n\n"
                  "def test_known():\n    assert False\n",
                  workflow="run: cat tests/ci_known_failures.txt\n", known="tests/test_x.py::test_known\n")
    sha = g("rev-parse", "HEAD")
    (loc / "tests" / "ci_known_failures.txt").write_text("")          # live folder drops it: must not matter
    sib_origin, sib = tmp_path / "home" / "sib_origin", loc.parent / "sib"
    def run_g(d, *a):
        return subprocess.run(["git", "-C", str(d), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                              check=True, capture_output=True, text=True)
    sib_origin.mkdir()
    run_g(sib_origin, "init", "-q", "-b", "main")
    (sib_origin / "f.txt").write_text("main\n")
    run_g(sib_origin, "add", "f.txt")
    run_g(sib_origin, "commit", "-q", "-m", "m")
    subprocess.run(["git", "clone", "-q", str(sib_origin), str(sib)], check=True, capture_output=True)
    run_g(sib, "checkout", "-q", "-b", "release/x")
    (sib / "f.txt").write_text("release branch\n")
    run_g(sib, "commit", "-q", "-am", "r")
    (sib / "f.txt").write_text("uncommitted dirt\n")                  # the live sibling: another branch, and dirty
    rec = S.run(loc, "seat", sha, PYTEST, ["../sib"], work=tmp_path / "w")
    assert rec["verdict"] == "PASS", rec
    assert rec["excluded"] == ["tests/test_x.py::test_known"] and rec["sibling_refs"][0].startswith("../sib: origin/")


def repo_with_log(tmp_path, tests=LOGS):
    """A member whose suite appends to a tracked file under logs/, without committing."""
    loc, g = repo(tmp_path, tests)
    (loc / "logs").mkdir()
    (loc / "logs" / "run.log").write_text("first\n")
    g("add", "-f", "logs/run.log")
    g("commit", "-q", "-m", "log")
    return loc, g


@requires_monitoring
def test_a_suite_that_changes_a_tracked_file_without_committing_is_never_pass(tmp_path):
    """Review finding F-6: only HEAD was compared after the suite, so an uncommitted write left PASS and no trace."""
    loc, g = repo_with_log(tmp_path)
    sha = g("rev-parse", "HEAD")
    r = S.run(loc, "seat", sha, PYTEST, work=tmp_path / "w", allow_paths=[])
    assert r["verdict"] == "INCONCLUSIVE" and "the suite left 1 change(s)" in r["why"] and "logs/run.log" in r["why"]
    assert r["tree_after_suite"] == {"count": 1, "lines": [" M logs/run.log"]}
    assert r["tree_unallowed"] == [" M logs/run.log"] and r["tree_check"] == "enforced"
    assert r["summary"].startswith("1 passed") and "head_after" not in r     # the run passed and HEAD did not move
    assert (loc / "logs" / "run.log").read_text() == "first\n"                 # the live folder is not written
    r = S.run(loc, "seat", sha, PYTEST, work=tmp_path / "w")                   # the reference run's default
    assert r["verdict"] == "PASS" and r["tree_check"] == "recorded only" and r["tree_after_suite"]["count"] == 1


@requires_monitoring
def test_a_suite_that_creates_an_untracked_file_is_never_pass_unless_git_ignores_it(tmp_path):
    made = ("from pathlib import Path\n\ndef test_makes_a_file():\n"
            "    (Path(__file__).resolve().parents[1] / 'made_by_suite.txt').write_text('x\\n')\n")
    loc, g = repo(tmp_path, made)
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, work=tmp_path / "w", allow_paths=[])
    assert r["verdict"] == "INCONCLUSIVE" and r["tree_unallowed"] == ["?? made_by_suite.txt"]
    (loc / ".gitignore").write_text("made_by_suite.txt\n")
    g("add", ".gitignore")
    g("commit", "-q", "-m", "ignore")
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, work=tmp_path / "w", allow_paths=[])
    assert r["verdict"] == "PASS" and r["tree_after_suite"] == {"count": 0, "lines": []}


def test_a_hook_that_changes_a_file_is_never_pass(tmp_path):
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n")
    hook = loc / ".git" / "hooks" / "pre-push"
    hook.write_text("#!/bin/sh\necho changed >> tests/test_x.py\nexit 0\n")
    hook.chmod(0o755)
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, work=tmp_path / "w", allow_paths=[])
    assert r["verdict"] == "INCONCLUSIVE" and "the pre-push hook left 1 change(s)" in r["why"]
    assert r["hook"]["exit"] == 0 and r["tree_after_suite"]["count"] == 0
    assert r["tree_after_hook"] == {"count": 1, "lines": [" M tests/test_x.py"]}


def test_a_hook_that_commits_is_never_pass_whatever_is_allowed(tmp_path):
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n")
    hook = loc / ".git" / "hooks" / "pre-push"
    hook.write_text("#!/bin/sh\ngit -c user.name=t -c user.email=t@t commit -q --allow-empty -m rogue\nexit 0\n")
    hook.chmod(0o755)
    sha = g("rev-parse", "HEAD")
    for allow in (None, [], ["tests/"]):
        r = S.run(loc, "seat", sha, PYTEST, work=tmp_path / "w", allow_paths=allow)
        assert r["verdict"] == "INCONCLUSIVE" and "hook moved the clone's HEAD" in r["why"], r
        assert r["head_after_hook"] != sha and r["hook"]["exit"] == 0
    assert g("rev-parse", "HEAD") == sha


@requires_monitoring
def test_allow_path_lets_a_known_write_pass_and_the_record_shows_it(tmp_path, monkeypatch):
    loc, g = repo_with_log(tmp_path)
    sha = g("rev-parse", "HEAD")
    pk = tmp_path / "packet.json"
    pk.write_text(json.dumps({"receivers": [{"aget": "seat", "location": str(loc), "suite_cmd": PYTEST,
                                             "head": sha}]}))   # C2a (R2-T13): a packet names its head
    real = S.run
    monkeypatch.setattr(S, "run", lambda *a, **k: real(*a, work=tmp_path / "w", **k))
    args = ["--packet", str(pk), "--aget", "seat", "--evidence", str(tmp_path / "ev")]
    record = tmp_path / "ev" / "seat" / "suite_at_commit.json"
    assert S.main(args) == 3                                                    # no --allow-path: INCONCLUSIVE
    assert json.loads(record.read_text())["tree_unallowed"] == [" M logs/run.log"]
    assert S.main(args + ["--allow-path", "docs/x.md", "--allow-path", "logs/"]) == 0
    rec = json.loads(record.read_text())
    assert rec["verdict"] == "PASS" and rec["sha"] == sha and rec["tree_check"] == "enforced"
    assert rec["allow_paths"] == ["docs/x.md", "logs/"] and rec["tree_allowed"] == [" M logs/run.log"]
    assert rec["tree_after_suite"] == {"count": 1, "lines": [" M logs/run.log"]} and "tree_unallowed" not in rec
    assert S.run(loc, "seat", sha, PYTEST, allow_paths=["logs/run.log"])["verdict"] == "PASS"       # an exact path
    assert S.run(loc, "seat", sha, PYTEST, allow_paths=["logs"])["verdict"] == "INCONCLUSIVE"       # no "/": no prefix


def test_status_entries_renames_cache_folders_and_the_kept_number():
    text = "R  new name.txt\0old.txt\0?? pkg/__pycache__/m.cpython-312.pyc\0 M b.txt\0?? .pytest_cache/v/x\0"
    now = S.parse_porcelain(text)
    assert [line for line, _ in now] == ["R  new name.txt (from old.txt)", " M b.txt"]
    assert S.split_changes(now, [], ["new name.txt", "b.txt"]) == (["R  new name.txt (from old.txt)"], [" M b.txt"])
    assert S.split_changes(now, now[:1], []) == ([" M b.txt"], [])
    assert [x for x, _ in S.parse_porcelain(" D tests/__pycache__/t.pyc\0")] == [" D tests/__pycache__/t.pyc"]
    assert S.kept(None) is None and S.kept(now * 30)["count"] == 60 and len(S.kept(now * 30)["lines"]) == S.TREE_KEPT
    rec = {"tree_allowed": []}
    assert "could not be read" in S.tree_refusal(rec, "the suite", None, [], [])
    assert "left 2 change(s)" in S.tree_refusal(rec, "the suite", now, [], []) and len(rec["tree_unallowed"]) == 2


def repo_with_copied_input(tmp_path, tests):
    """A member with an untracked folder `support/` holding input.txt, declared as a sibling folder: the clean clone
    gets a copy INSIDE the clone, so git lists `?? support/input.txt` there before the suite runs."""
    loc, g = repo(tmp_path, tests)
    (loc / "support").mkdir()
    (loc / "support" / "input.txt").write_text("copied input\n")
    return loc, g


REWRITES = ("from pathlib import Path\n\ndef test_changes_copied_input():\n"
            "    Path('support/input.txt').write_text('changed by suite\\n')\n")


@requires_monitoring
def test_a_suite_that_rewrites_a_path_already_listed_before_it_is_never_pass(tmp_path):
    """F-6, second review (2026-10-02): the status line `?? support/input.txt` is the same before and after the
    suite that rewrote the file, and only new lines were compared, so the run read PASS. Now the content is compared
    too. Controls: the same member with a suite that only reads the file is PASS; the path allowed is PASS and shown;
    the reference run (no allow_paths) records and does not judge."""
    loc, g = repo_with_copied_input(tmp_path, REWRITES)
    sha = g("rev-parse", "HEAD")
    r = S.run(loc, "seat", sha, PYTEST, ["support"], work=tmp_path / "w", hook=False, allow_paths=[])
    assert r["verdict"] == "INCONCLUSIVE" and "the suite left 1 change(s)" in r["why"], r
    assert r["tree_unallowed"] == ["?? support/input.txt (content changed)"]
    assert r["tree_before_suite"] == r["tree_after_suite"] == {"count": 1, "lines": ["?? support/input.txt"]}
    assert r["summary"].startswith("1 passed")
    assert (loc / "support" / "input.txt").read_text() == "copied input\n"       # the live folder is not written
    r = S.run(loc, "seat", sha, PYTEST, ["support"], work=tmp_path / "w", hook=False, allow_paths=["support/"])
    assert r["verdict"] == "PASS" and r["tree_allowed"] == ["?? support/input.txt (content changed)"]
    r = S.run(loc, "seat", sha, PYTEST, ["support"], work=tmp_path / "w", hook=False)
    assert r["verdict"] == "PASS" and r["tree_check"] == "recorded only"
    reads = "from pathlib import Path\n\ndef test_reads():\n    assert Path('support/input.txt').read_text()\n"
    loc2, g2 = repo_with_copied_input(tmp_path / "second", reads)
    r = S.run(loc2, "seat", g2("rev-parse", "HEAD"), PYTEST, ["support"], work=tmp_path / "w2", hook=False,
              allow_paths=[])
    assert r["verdict"] == "PASS" and r["tree_after_suite"]["count"] == 1 and "tree_unallowed" not in r


@requires_monitoring
def test_a_suite_that_deletes_or_only_changes_the_mode_of_a_listed_path_is_never_pass(tmp_path):
    """F-6, second review's further control: the suite deletes the listed copied file, so its status line is gone
    and no line is new; and a suite that only makes the file executable leaves line and bytes as they were."""
    deletes = "from pathlib import Path\n\ndef test_deletes():\n    Path('support/input.txt').unlink()\n"
    loc, g = repo_with_copied_input(tmp_path, deletes)
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, ["support"], work=tmp_path / "w", hook=False,
              allow_paths=[])
    assert r["verdict"] == "INCONCLUSIVE" and r["tree_unallowed"] == ["?? support/input.txt (no longer listed)"], r
    assert (loc / "support" / "input.txt").exists()
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, ["support"], work=tmp_path / "w", hook=False,
              allow_paths=["support/input.txt"])
    assert r["verdict"] == "PASS" and r["tree_allowed"] == ["?? support/input.txt (no longer listed)"]
    chmods = "import os\n\ndef test_chmods():\n    os.chmod('support/input.txt', 0o755)\n"
    loc2, g2 = repo_with_copied_input(tmp_path / "second", chmods)
    (loc2 / "support" / "input.txt").chmod(0o644)
    r = S.run(loc2, "seat", g2("rev-parse", "HEAD"), PYTEST, ["support"], work=tmp_path / "w2", hook=False,
              allow_paths=[])
    assert r["verdict"] == "INCONCLUSIVE" and r["tree_unallowed"] == ["?? support/input.txt (content changed)"], r


def test_a_hook_that_deletes_a_listed_path_is_never_pass(tmp_path):
    loc, g = repo_with_copied_input(tmp_path, "def test_a():\n    assert True\n")
    hook = loc / ".git" / "hooks" / "pre-push"
    hook.write_text("#!/bin/sh\nrm support/input.txt\nexit 0\n")
    hook.chmod(0o755)
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, ["support"], work=tmp_path / "w", allow_paths=[])
    assert r["verdict"] == "INCONCLUSIVE" and "the pre-push hook left 1 change(s)" in r["why"], r
    assert r["tree_unallowed"] == ["?? support/input.txt (no longer listed)"]


@requires_monitoring
def test_a_permission_change_git_does_not_list_is_never_pass(tmp_path):
    """F-6, second review's last two controls: the suite changes the read and write bits of its own tracked, clean
    test file (git tracks only the executable bit, so no status line appears), or the permission bits of a copied
    folder. The working-tree snapshot sees both. Controls: the path allowed is PASS and shown; the reference run
    does not judge."""
    chmods = "from pathlib import Path\n\ndef test_chmods():\n    Path('tests/test_x.py').chmod(0o600)\n"
    loc, g = repo(tmp_path, chmods)
    (loc / "tests" / "test_x.py").chmod(0o644)
    sha = g("rev-parse", "HEAD")
    r = S.run(loc, "seat", sha, PYTEST, work=tmp_path / "w", hook=False, allow_paths=[])
    assert r["verdict"] == "INCONCLUSIVE" and r["tree_unallowed"] == ["changed tests/test_x.py"], r
    assert r["tree_after_suite"] == {"count": 0, "lines": []}                    # git lists nothing
    assert (loc / "tests" / "test_x.py").stat().st_mode & 0o777 == 0o644          # the live file is as it was
    r = S.run(loc, "seat", sha, PYTEST, work=tmp_path / "w", hook=False, allow_paths=["tests/"])
    assert r["verdict"] == "PASS" and r["tree_allowed"] == ["changed tests/test_x.py"]
    assert S.run(loc, "seat", sha, PYTEST, work=tmp_path / "w", hook=False)["verdict"] == "PASS"
    folder = "from pathlib import Path\n\ndef test_chmods_folder():\n    Path('support').chmod(0o700)\n"
    loc2, g2 = repo_with_copied_input(tmp_path / "second", folder)
    (loc2 / "support").chmod(0o755)
    r = S.run(loc2, "seat", g2("rev-parse", "HEAD"), PYTEST, ["support"], work=tmp_path / "w2", hook=False,
              allow_paths=[])
    assert r["verdict"] == "INCONCLUSIVE" and r["tree_unallowed"] == ["changed support/"], r


def test_a_hook_that_changes_permissions_git_does_not_list_is_never_pass(tmp_path):
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n")
    (loc / "tests" / "test_x.py").chmod(0o644)
    hook = loc / ".git" / "hooks" / "pre-push"
    hook.write_text("#!/bin/sh\nchmod 600 tests/test_x.py\nexit 0\n")
    hook.chmod(0o755)
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, work=tmp_path / "w", allow_paths=[])
    assert r["verdict"] == "INCONCLUSIVE" and "the pre-push hook left 1 change(s)" in r["why"], r
    assert r["tree_unallowed"] == ["changed tests/test_x.py"]


def test_the_snapshot_holds_tracked_and_untracked_paths_and_leaves_out_what_git_ignores(tmp_path):
    """snapshot() and snapshot_changes() as functions: tracked and untracked files, a link and folders are in it;
    `.git`, cache folders and ignored files and folders are not; a path the status lines already name, a path under
    a named folder, and a folder present in only one snapshot are not reported twice."""
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n")
    (loc / ".gitignore").write_text("ignored.txt\nbuild/\n")
    g("add", ".gitignore")
    g("commit", "-q", "-m", "ignore")
    (loc / "ignored.txt").write_text("x")
    (loc / "build").mkdir()
    (loc / "build" / "out.bin").write_text("x")
    (loc / "tests" / "__pycache__").mkdir()
    (loc / "tests" / "__pycache__" / "t.pyc").write_text("x")
    (loc / "new.txt").write_text("x")
    (loc / "link").symlink_to("new.txt")
    snap = S.snapshot(loc)
    rules = {".git/info/exclude", "(git config) core.excludesFile"}      # the ignore rules kept outside the tree
    assert set(snap) == {"./", ".gitignore", "tests/", "tests/test_x.py", "new.txt", "link"} | rules
    assert snap["link"] == "link:new.txt" and snap["tests/"].startswith("folder:")
    after = dict(snap, **{"new.txt": "other", "d/": "folder:755", "d/f.txt": "abc"})
    del after["link"]
    assert S.snapshot_changes(after, snap, set()) == [
        ("added d/f.txt", ["d/f.txt"]), ("removed link", ["link"]), ("changed new.txt", ["new.txt"])]
    assert S.snapshot_changes(after, snap, {"new.txt", "d/"}) == [("removed link", ["link"])]
    before, now = S.Reading(), S.Reading([("?? d/f.txt", ["d/f.txt"], "abc")])
    before.snapshot, now.snapshot = snap, after
    assert S.split_changes(now, before, ["d/f.txt"]) == (["removed link", "changed new.txt"], ["?? d/f.txt"])
    assert "could not be listed" in S.tree_refusal({"tree_allowed": []}, "the suite", S.Reading(), before, [])


def test_a_hook_that_rewrites_a_path_already_listed_is_never_pass(tmp_path):
    loc, g = repo_with_copied_input(tmp_path, "def test_a():\n    assert True\n")
    hook = loc / ".git" / "hooks" / "pre-push"
    hook.write_text("#!/bin/sh\necho changed > support/input.txt\nexit 0\n")
    hook.chmod(0o755)
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, ["support"], work=tmp_path / "w", allow_paths=[])
    assert r["verdict"] == "INCONCLUSIVE" and "the pre-push hook left 1 change(s)" in r["why"], r
    assert r["tree_unallowed"] == ["?? support/input.txt (content changed)"]


def test_content_of_listed_paths_files_links_folders_and_absent(tmp_path):
    """content_print and the content half of split_changes, as pure functions: a rewritten file, a retargeted link
    and a changed file under a folder git lists as one entry differ; a `.git` folder and cache folders under such a
    folder are left out; the same content does not differ; entries without content compare by line only."""
    d = tmp_path / "d"
    (d / "nested" / ".git").mkdir(parents=True)
    (d / "nested" / "__pycache__").mkdir()
    (d / "nested" / "a.txt").write_text("a")
    (d / "f.txt").write_text("one")
    (d / "l").symlink_to("f.txt")
    first = {x: S.content_print(d / x) for x in ("f.txt", "l", "nested", "gone")}
    assert first["gone"] == "absent" and first["l"] == "link:f.txt" and first["nested"].startswith("folder:")
    (d / "nested" / ".git" / "index").write_text("x")
    (d / "nested" / "__pycache__" / "m.pyc").write_text("x")
    assert S.content_print(d / "nested") == first["nested"]
    (d / "nested" / "a.txt").write_text("b")
    (d / "f.txt").write_text("two")
    (d / "l").unlink()
    (d / "l").symlink_to("nested")
    assert all(S.content_print(d / x) != first[x] for x in ("f.txt", "l", "nested"))
    before = [("?? f.txt", ["f.txt"], "1"), ("?? g.txt", ["g.txt"], "1")]
    now = [("?? f.txt", ["f.txt"], "2"), ("?? g.txt", ["g.txt"], "1"), ("?? h.txt", ["h.txt"], "1")]
    assert S.split_changes(now, before, []) == (["?? f.txt (content changed)", "?? h.txt"], [])
    assert S.split_changes(now, before, ["f.txt"]) == (["?? h.txt"], ["?? f.txt (content changed)"])
    assert S.split_changes([e[:2] for e in now], [e[:2] for e in before], []) == (["?? h.txt"], [])
    assert S.split_changes(now[1:], before, []) == (["?? h.txt", "?? f.txt (no longer listed)"], [])
    assert S.split_changes([], before, ["f.txt"]) == (["?? g.txt (no longer listed)"], ["?? f.txt (no longer listed)"])


def test_a_suite_that_adds_an_ignore_rule_and_then_writes_hidden_files_is_never_pass(tmp_path):
    """Second review leg, 2026-10-02: git stops listing a file once an ignore rule hides it, so a suite that appends
    a rule to .git/info/exclude and then writes files left PASS with the files in the clone. The rules kept outside
    the working tree are part of the snapshot. A tracked .gitignore changed by the suite is a status line already."""
    hides = ("from pathlib import Path\n\ndef test_hides():\n"
             "    with open('.git/info/exclude', 'a') as f:\n        f.write('hidden*\\n')\n"
             "    Path('hidden.txt').write_text('left behind\\n')\n")
    loc, g = repo(tmp_path, hides)
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, work=tmp_path / "w", hook=False, allow_paths=[])
    assert r["verdict"] == "INCONCLUSIVE" and r["tree_unallowed"] == ["changed .git/info/exclude"], r
    assert r["tree_after_suite"] == {"count": 0, "lines": []}                    # git lists nothing


def _sibling_with_remote(tmp_path, loc):
    """A sibling repository beside the member, with a bare remote named origin; returns (sibling, remote)."""
    sib, remote = loc.parent / "sib", tmp_path / "sib_remote.git"
    sib.mkdir()
    (sib / "x.txt").write_text("x\n")
    run = lambda *a: subprocess.run(["git", "-C", str(sib), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                                    check=True, capture_output=True, text=True).stdout.strip()
    run("init", "-q")
    run("add", "-A")
    run("commit", "-q", "-m", "c")
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    run("remote", "add", "origin", str(remote))
    return sib, remote


PUSHES_FROM_SIBLING = ("import subprocess\n\ndef test_pushes_from_the_sibling():\n"
                       "    subprocess.run(['git', '-C', '../sib', 'push', 'origin', 'HEAD:refs/heads/from-suite'])\n")


@requires_monitoring
def test_a_suite_cannot_push_from_a_copied_sibling_to_its_real_remote(tmp_path):
    """Both review legs, 2026-10-02: pushing was closed for the clone's remotes and left open in each copied sibling,
    so a suite running `git -C ../sib push origin ...` put a ref in the sibling's real remote and the run read PASS.
    The copied sibling's remotes now get the push URL that cannot resolve; the live sibling's settings are not
    written."""
    loc, g = repo(tmp_path, PUSHES_FROM_SIBLING)
    sib, remote = _sibling_with_remote(tmp_path, loc)
    before = (sib / ".git" / "config").read_text()
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, ["../sib"], work=tmp_path / "w", hook=False)
    refs = subprocess.run(["git", "--git-dir", str(remote), "for-each-ref"], capture_output=True, text=True).stdout
    assert refs == "" and r["verdict"] == "PASS", (refs, r)
    copy_cfg = next((tmp_path / "w").glob("*/seat.root/sib/.git/config")).read_text()   # E2g: the run's own folder
    assert S.NO_PUSH_URL in copy_cfg and (sib / ".git" / "config").read_text() == before


def test_a_copied_sibling_whose_git_acts_on_the_live_sibling_is_refused_before_anything_runs(tmp_path):
    """The same isolation as the member's rehearsal copy: a sibling whose config names its own live folder as
    core.worktree would have `git checkout --force` and `git clean` in the copy act on the live sibling."""
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n")
    sib, _ = _sibling_with_remote(tmp_path, loc)
    subprocess.run(["git", "-C", str(sib), "config", "core.worktree", str(sib.resolve())], check=True)
    (sib / "uncommitted.txt").write_text("live work\n")
    r = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, ["../sib"], work=tmp_path / "w", hook=False)
    assert r["verdict"] == "INCONCLUSIVE" and "sibling '../sib'" in r["why"] and "acts on the working tree" in r["why"]
    assert (sib / "uncommitted.txt").read_text() == "live work\n" and "summary" not in r     # no suite ran


@requires_monitoring
def test_the_clone_folder_may_not_be_or_hold_the_member(tmp_path):
    """A work root that holds the member is refused. Since E2g (R1-T1, R1 clause 5) so is one inside the member's
    repository: until E2f a work folder inside the member was accepted ("inside is accepted"), and the clone was made
    in the live working tree. The control, a work root apart from the member, passes."""
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n")
    sha = g("rev-parse", "HEAD")
    (loc.parent / "seat.root").symlink_to(loc.parent, target_is_directory=True)   # work/<aget>.root would hold the member
    r = S.run(loc, "seat", sha, PYTEST, work=loc.parent, hook=False)
    assert r["verdict"] == "INCONCLUSIVE" and "nothing was made" in r["why"] and loc.is_dir()
    r = S.run(loc, "seat", sha, PYTEST, work=loc / "wk", hook=False)
    assert r["verdict"] == "INCONCLUSIVE" and "lies inside the git repository" in r["why"]
    assert not (loc / "wk").exists()
    assert S.run(loc, "seat", sha, PYTEST, work=tmp_path / "apart", hook=False)["verdict"] == "PASS"   # control


@requires_monitoring
def test_main_writes_the_record_the_push_gate_reads(tmp_path):
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n")
    pk = tmp_path / "packet.json"
    pk.write_text(json.dumps({"receivers": [{"aget": "seat", "location": str(loc), "suite_cmd": PYTEST,
                                             "head": g("rev-parse", "HEAD")}]}))   # C2a (R2-T13): a packet names its head
    S.WORK = tmp_path / "w"
    assert S.main(["--packet", str(pk), "--aget", "seat", "--evidence", str(tmp_path / "ev")]) == 0
    rec = json.loads((tmp_path / "ev" / "seat" / "suite_at_commit.json").read_text())
    assert rec["sha"] == g("rev-parse", "HEAD") and rec["verdict"] == "PASS"


# --- REVW5's B153 read of stage E2e (finding 2): the suite group is killed on every exit -------------------------

import os  # noqa: E402

import pytest  # noqa: E402


class _Process:
    pid, returncode = 123456789, None

    def __init__(self, exc=None, stdin=None):
        self.exc, self.stdin = exc, stdin

    def wait(self, timeout=None):
        if timeout is not None and self.exc:
            raise self.exc("synthetic suite wait failure")
        self.returncode = -9
        return -9


@pytest.mark.parametrize("exc", [RuntimeError, KeyboardInterrupt])
def test_b153_2_the_suite_group_is_killed_when_its_wait_raises(tmp_path, monkeypatch, exc):
    """B153 finding 2 (REVW5's falsifier). An exception from `run_bounded`'s timed wait still kills the group and
    waits. On stage E2e `kill_group` was skipped. No real process is made."""
    seen = []
    monkeypatch.setattr(S.subprocess, "Popen", lambda *a, **k: _Process(exc))
    monkeypatch.setattr(S, "kill_group", lambda pid: seen.append(pid))
    with pytest.raises(exc):
        S.run_bounded(["synthetic-command"], tmp_path, 1, dict(os.environ))
    assert seen == [123456789]


def test_b153_2_the_suite_group_is_killed_when_its_input_write_raises(tmp_path, monkeypatch):
    """B153 finding 2 (REVW5's falsifier): a broken pipe writing the hook's stdin still kills the group."""
    seen = []

    class Input:
        def write(self, data):
            raise BrokenPipeError("synthetic closed child stdin")

        def close(self):
            pass
    monkeypatch.setattr(S.subprocess, "Popen", lambda *a, **k: _Process(None, Input()))
    monkeypatch.setattr(S, "kill_group", lambda pid: seen.append(pid))
    with pytest.raises(BrokenPipeError):
        S.run_bounded(["synthetic-command"], tmp_path, 1, dict(os.environ), input="hello")
    assert seen == [123456789]


# --- E2i: ignore state (IGN, R1 clause 8; H-3, R1-T9) ---------------------------------------------------------------
# Each variant's suite changes one IGN element and then writes a file that the change hides. The judged run and the
# reference run (no allow_paths, the V3.6 reference) must both read INCONCLUSIVE naming the element. Until E2i the
# reference run read PASS for every variant, and the judged run named no ignore element.
IGN_VARIANTS = {
    # the operator's default global ignore file: the suite keeps HOME, and the kit's tree checks read git under the
    # checker's own environment, so a rule written here hides the suite's later writes from them
    "home_default_ignore": ("'core.excludesFile file'",
                            "import os\nfrom pathlib import Path\n\ndef test_hides():\n"
                            "    f = Path(os.environ['HOME']) / '.config' / 'git' / 'ignore'\n"
                            "    f.parent.mkdir(parents=True, exist_ok=True)\n"
                            "    f.write_text('hidden*\\n')\n    Path('hidden.txt').write_text('x\\n')\n"),
    "xdg_global_ignore": ("core.excludesFile file (suite environment)",
                          "import os\nfrom pathlib import Path\n\ndef test_hides():\n"
                          "    f = Path(os.environ['XDG_CONFIG_HOME']) / 'git' / 'ignore'\n"
                          "    f.parent.mkdir(parents=True, exist_ok=True)\n"
                          "    f.write_text('hidden*\\n')\n    Path('hidden.txt').write_text('x\\n')\n"),
    "info_exclude": ("info/exclude",
                     "from pathlib import Path\n\ndef test_hides():\n"
                     "    with open('.git/info/exclude', 'a') as f:\n        f.write('hidden*\\n')\n"
                     "    Path('hidden.txt').write_text('x\\n')\n"),
    "nested_self_ignoring_gitignore": (".gitignore sub/.gitignore",
                                       "from pathlib import Path\n\ndef test_hides():\n"
                                       "    Path('sub').mkdir()\n    Path('sub/.gitignore').write_text('*\\n')\n"
                                       "    Path('sub/hidden.txt').write_text('x\\n')\n"),
    "skip_worktree": ("index flags",
                      "import subprocess\nfrom pathlib import Path\n\ndef test_hides():\n"
                      "    subprocess.run(['git', 'update-index', '--skip-worktree', 'data.txt'], check=True)\n"
                      "    Path('data.txt').write_text('changed\\n')\n"),
}


@pytest.mark.parametrize("variant", sorted(IGN_VARIANTS))
def test_e2i_r1_t9_a_suite_that_changes_the_ignore_state_is_inconclusive_naming_the_element(tmp_path, monkeypatch,
                                                                                              variant):
    """R1-T9 (1)-(4), H-3: a suite that changes git's ignore state (with HOME and XDG set to tmp: the operator's
    default global ignore file, which the kit's own tree checks read, and the global ignore file under the suite's own
    XDG_CONFIG_HOME; `.git/info/exclude`; an untracked nested `.gitignore` that ignores itself; a skip-worktree flag)
    and then writes a file the change hides never reads PASS, and the reason names the IGN element."""
    element, tests = IGN_VARIANTS[variant]
    monkeypatch.setenv("HOME", str(tmp_path / "operator-home"))           # R1-T9: HOME and XDG set to tmp
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    loc, g = repo(tmp_path, tests)
    (loc / "data.txt").write_text("tracked\n")
    g("add", "data.txt")
    g("commit", "-q", "-m", "data")
    sha = g("rev-parse", "HEAD")
    ref = S.run(loc, "seat", sha, PYTEST, work=tmp_path / "w", hook=False)                 # the reference run
    assert ref["verdict"] == "INCONCLUSIVE" and element in ref["why"], ref
    left = tmp_path / "operator-home" / ".config" / "git" / "ignore"       # the first run's rule outlives its clone;
    if left.exists():                                                       # in force before the next run, it is
        left.unlink()                                                       # clause 8's stated gap, so reset it
    judged = S.run(loc, "seat", sha, PYTEST, work=tmp_path / "w", hook=False, allow_paths=[])
    assert judged["verdict"] == "INCONCLUSIVE" and element in judged["why"], judged


def test_e2i_r1_t9_a_hook_that_changes_the_ignore_state_is_inconclusive_naming_the_element(tmp_path):
    """R1 clause 8: IGN is read after the hook too. A pre-push hook that adds a self-ignoring nested `.gitignore`
    and writes under it never reads PASS."""
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n")
    hook = loc / ".git" / "hooks" / "pre-push"
    hook.write_text("#!/bin/sh\nmkdir -p sub && printf '*\\n' > sub/.gitignore && echo x > sub/h.txt\nexit 0\n")
    hook.chmod(0o755)
    for allow in (None, []):
        rec = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, work=tmp_path / "w", allow_paths=allow)
        assert rec["verdict"] == "INCONCLUSIVE" and "the pre-push hook changed git's ignore state" in rec["why"], rec
        assert ".gitignore sub/.gitignore" in rec["why"]


@requires_monitoring
def test_e2i_r1_t9_positive_control_a_write_into_a_cache_folder_still_passes(tmp_path):
    """R1-T9's positive control: a suite that writes only into a `__pycache__` folder (git's ignore state unchanged)
    reads PASS, judged and as the reference run."""
    writes = ("from pathlib import Path\n\ndef test_caches():\n"
              "    d = Path(__file__).resolve().parent / '__pycache__'\n    d.mkdir(exist_ok=True)\n"
              "    (d / 'extra.bin').write_bytes(b'x')\n")
    loc, g = repo(tmp_path, writes)
    sha = g("rev-parse", "HEAD")
    for allow in (None, []):
        rec = S.run(loc, "seat", sha, PYTEST, work=tmp_path / "w", hook=False, allow_paths=allow)
        assert rec["verdict"] == "PASS", rec


# --- C2a: R2-T13, the exclusions are read at the packet's head ---------------------------------------------------

def _migration_world(tmp_path, how):
    """A member at its packet head with one passing test; the migration commit adds a failing test and, by `how`,
    an exclusion for it: a `--deselect` in a root workflow ("workflow"), or an entry in the deselect file the suite
    command declares ("declared"). Returns (packet, evidence, suite command)."""
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n")
    (loc / "tests" / "known.txt").write_text("# none\n")
    g("add", "-A")
    g("commit", "-q", "-m", "known")
    head = g("rev-parse", "HEAD")
    (loc / "tests" / "test_new.py").write_text("def test_new():\n    assert False\n")
    if how == "workflow":
        (loc / ".github" / "workflows").mkdir(parents=True)
        (loc / ".github" / "workflows" / "ci.yml").write_text("run: pytest --deselect tests/test_new.py::test_new\n")
    else:
        (loc / "tests" / "known.txt").write_text("tests/test_new.py::test_new\n")
    g("add", "-A")
    g("commit", "-q", "-m", "migration")
    cmd = PYTEST + (" --deselect-file tests/known.txt" if how == "declared" else "")
    pk = tmp_path / "packet.json"
    pk.write_text(json.dumps({"receivers": [{"aget": "seat", "location": str(loc), "suite_cmd": cmd,
                                             "head": head}]}))
    return pk, tmp_path / "ev"


@pytest.mark.parametrize("how,code,verdict", [("workflow", 1, "FAIL"), ("declared", 3, "INCONCLUSIVE")])
def test_r2_t13_a_migration_commit_cannot_exclude_its_own_new_failure(tmp_path, how, code, verdict):
    """R2-T13 (S-181). The migration commit adds a failing test and excludes it: a `--deselect` in a root workflow is
    not applied (the exclusions are read at the packet's head), so the record reads FAIL; a new entry in the declared
    deselect file, which pytest reads from the tested commit itself, makes it INCONCLUSIVE. Before C2a both read
    PASS: the exclusions were read at the tested commit."""
    pk, ev = _migration_world(tmp_path, how)
    S.WORK = tmp_path / "w"
    assert S.main(["--packet", str(pk), "--aget", "seat", "--evidence", str(ev)]) == code
    rec = json.loads((ev / "seat" / "suite_at_commit.json").read_text())
    assert rec["verdict"] == verdict, rec


def test_r2_t13_a_packet_without_a_head_is_refused(tmp_path):
    """R2-T13: without the packet's head the exclusions in force before the migration are unknown; the tool refuses
    (exit 2) and no record that counts is left: since C2c (R2-T16 (c)) the run's first act records it and writes the
    record as not finished, and that record is not current (no FINISHED row), so the push gate refuses it."""
    loc, g = repo(tmp_path, "def test_a():\n    assert True\n")
    pk = tmp_path / "packet.json"
    pk.write_text(json.dumps({"receivers": [{"aget": "seat", "location": str(loc), "suite_cmd": PYTEST}]}))
    assert S.main(["--packet", str(pk), "--aget", "seat", "--evidence", str(tmp_path / "ev")]) == 2
    rec = tmp_path / "ev" / "seat" / "suite_at_commit.json"
    assert not rec.exists() or S.RBND.read_current("suite_at_commit", rec)[1], "a refused run left a current record"


# --- REVW9's B171 read of stage E2i: IGN path spellings and unreadable inputs -----------------------------------

def _named_home_spelling(target):
    """`~<user>/…` naming `target` (a temporary file): git expands `~<user>` to that user's home, and the relative
    part walks from there to the target, so nothing is read or written in the home itself."""
    import getpass
    import pwd
    user = getpass.getuser()
    return f"~{user}/" + os.path.relpath(target, pwd.getpwnam(user).pw_dir)


def test_b171_1_an_excludes_file_named_with_a_user_home_is_the_file_git_reads(tmp_path):
    """B171 finding 1 (REVW9's falsifier, at the helper). `core.excludesFile` is spelled `~<user>/…`; the file git
    resolves gains a rule between two readings: IGN names the change. On stage E2i the spelling was read as a path
    relative to the repository, absent at both readings, and no change was reported."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    ignore = tmp_path / "ignore-file"
    ignore.write_text("# none\\n")
    g("config", "core.excludesFile", _named_home_spelling(ignore))
    before = CI.ignore_state(loc)
    assert os.path.realpath(before["core.excludesFile file"].rsplit(": ", 1)[0]) == os.path.realpath(ignore)
    ignore.write_text("hidden*\\n")
    why = CI.ignore_refusal(before, CI.ignore_state(loc), "the suite")
    assert why and "core.excludesFile file" in why, why


@pytest.mark.parametrize("source", ["configured", "default"])
def test_b171_2_an_ignore_file_unreadable_at_both_readings_is_reported(tmp_path, monkeypatch, source):
    """B171 finding 2 (REVW9's falsifier). The configured or default ignore file is unreadable (mode 000) at both
    readings: IGN reports it (unreadable, naming the element), so the reference run reads INCONCLUSIVE. On stage E2i
    the reading `path: unreadable` was not recognised as unreadable, and the run read PASS."""
    CI = S.CI
    monkeypatch.setenv("HOME", str(tmp_path / "operator-home"))
    monkeypatch.delenv("XDG_CONFIG_HOME", raising=False)
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    if source == "configured":
        ignore = tmp_path / "configured-ignore"
        g("config", "core.excludesFile", str(ignore))
    else:
        ignore = tmp_path / "operator-home" / ".config" / "git" / "ignore"
        ignore.parent.mkdir(parents=True)
    ignore.write_text("# rules\\n")
    ignore.chmod(0)
    try:
        state = CI.ignore_state(loc)
        assert state["core.excludesFile file"].startswith("unreadable"), state["core.excludesFile file"]
        why = CI.ignore_refusal(state, CI.ignore_state(loc), "the suite")
        assert why and "could not be read" in why and "core.excludesFile file" in why, why
        if source == "default":   # a configured excludes file is the member's own config, which a clean clone lacks
            rec = S.run(loc, "seat", g("rev-parse", "HEAD"), PYTEST, work=tmp_path / "w", hook=False)
            assert rec["verdict"] == "INCONCLUSIVE" and "core.excludesFile file" in rec["why"], rec
    finally:
        ignore.chmod(0o644)


# --- REVW9's B172 read of stage E2i2: relative names are read as git reads them ----------------------------------

@pytest.mark.parametrize("var", ["XDG_CONFIG_HOME", "HOME"])
def test_b172_1_a_default_ignore_file_under_a_relative_environment_path_is_the_one_git_reads(tmp_path, var):
    """B172 finding 1 (REVW9's falsifier, at the helper). The environment git is given names the default ignore file
    by a relative path; git reads it from the member's folder. A change to that file is named by IGN. On stage E2i2
    the kit opened the relative path from its own working folder: absent at both readings, no change reported."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    env = {k: v for k, v in os.environ.items() if k not in ("XDG_CONFIG_HOME",)}
    env[var] = "rel-env"
    ignore = loc / "rel-env" / ("git" if var == "XDG_CONFIG_HOME" else ".config/git") / "ignore"
    ignore.parent.mkdir(parents=True)
    ignore.write_text("# none\\n")
    before = CI.ignore_state(loc, env)
    assert before["core.excludesFile file"].startswith(str(ignore)), before["core.excludesFile file"]
    ignore.write_text("hidden*\\n")
    why = CI.ignore_refusal(before, CI.ignore_state(loc, env), "the suite")
    assert why and "core.excludesFile file" in why, why


@pytest.mark.parametrize("scope", ["GLOBAL", "SYSTEM"])
def test_b172_1_a_relative_config_file_with_no_entries_is_read_as_git_reads_it(tmp_path, monkeypatch, scope):
    """B172 finding 1, configuration files (clause 8 (iv)): GIT_CONFIG_GLOBAL or GIT_CONFIG_SYSTEM is a relative name
    of a file holding only a comment, so `--show-origin` names nothing; `git var` returns the relative name. A change
    to its bytes is named. The kit runs from another folder holding a decoy file of the same relative name, which
    must not be the one read. On stage E2i2 the relative name was read from the kit's own folder."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    elsewhere = tmp_path / "kit-cwd"
    elsewhere.mkdir()
    (elsewhere / "gcfg").write_text("# decoy, never changes\\n")
    monkeypatch.chdir(elsewhere)
    (loc / "gcfg").write_text("# comment only\\n")
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_CONFIG_NOSYSTEM",)}
    env[f"GIT_CONFIG_{scope}"] = "gcfg"
    if scope == "SYSTEM":
        env["GIT_CONFIG_GLOBAL"] = "/dev/null"
    else:
        env["GIT_CONFIG_NOSYSTEM"] = "1"
    before = CI.ignore_state(loc, env)
    assert f"config file {loc / 'gcfg'}" in before, sorted(before)
    assert f"config file {elsewhere / 'gcfg'}" not in before and "config file gcfg" not in before, sorted(before)
    (loc / "gcfg").write_text("# comment only, changed\\n")
    why = CI.ignore_refusal(before, CI.ignore_state(loc, env), "the suite")
    assert why and f"config file {loc / 'gcfg'}" in why, why


def test_b172_1_every_ign_file_named_by_git_is_read_through_the_one_anchoring_reader():
    """B172 finding 1, by class (census): in ignore_state_one(), the only direct file reading is the `.gitignore`
    walk, whose paths are absolute (the walk starts at the absolute member path). Every other file is read through
    _git_file_print(), which anchors a relative name to the member's folder, so a new producer of a name cannot skip
    the anchoring. On stage E2i2 three producers anchored on their own and two did not."""
    import inspect
    src = inspect.getsource(S.CI.ignore_state_one)
    direct = [line.strip() for line in src.splitlines() if "_file_print(" in line and "_git_file_print(" not in line]
    assert direct == ['out[key] = f"link:{os.readlink(p)}" if p.is_symlink() else _file_print(p)'], direct
    assert "open(" not in src and "os.path.join(str(repo)" not in src, "a file read or anchoring outside the reader"
    assert "_git_file_print(" in inspect.getsource(S.CI._named_file_reading)


# --- REVW9's B173 read of stage E2i3: names git returns are recovered byte for byte ------------------------------

@pytest.mark.parametrize("name", ["meta\nfolder", "meta\rfolder", "meta folder"])
def test_b173_1_a_metadata_folder_whose_path_holds_a_line_break_is_read_where_git_reads_it(tmp_path, name):
    """B173 finding 1 (REVW9's falsifier, separate git folder). The member's git folder is named with a line feed (and,
    as controls, a carriage return and a space); a change to its `info/exclude` is named by IGN. On stage E2i3 the
    four `--git-path` names were one newline-split listing, so with a line feed `info/exclude` read a fragment,
    absent at both readings, and no change was reported."""
    CI = S.CI
    loc = tmp_path / "work"
    meta = tmp_path / name
    subprocess.run(["git", "init", "-q", f"--separate-git-dir={meta}", str(loc)], check=True)
    (meta / "info").mkdir(exist_ok=True)
    (meta / "info" / "exclude").write_text("# none\n")
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
    before = CI.ignore_state(loc, env)
    assert before["info/exclude"] != "absent", before["info/exclude"]
    (meta / "info" / "exclude").write_text("hidden*\n")
    why = CI.ignore_refusal(before, CI.ignore_state(loc, env), "the suite")
    assert why and "info/exclude" in why, why


@pytest.mark.parametrize("scope", ["GLOBAL", "SYSTEM"])
def test_b173_1_a_config_file_named_with_a_line_break_is_read_as_git_names_it(tmp_path, scope):
    """B173 finding 1, configuration files: GIT_CONFIG_GLOBAL or GIT_CONFIG_SYSTEM names a comment-only file whose
    name holds a line feed (no `--show-origin` entry); a change to its bytes is named. On stage E2i3 `git var`'s output
    was split on line feeds and the fragments read absent."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    cfg = tmp_path / "g\ncfg"
    cfg.write_text("# comment only\n")
    env = {k: v for k, v in os.environ.items() if k != "GIT_CONFIG_NOSYSTEM"}
    env[f"GIT_CONFIG_{scope}"] = str(cfg)
    if scope == "SYSTEM":
        env["GIT_CONFIG_GLOBAL"] = "/dev/null"
    else:
        env["GIT_CONFIG_NOSYSTEM"] = "1"
    before = CI.ignore_state(loc, env)
    assert f"config file {cfg}" in before, sorted(before)
    cfg.write_text("# comment only, changed\n")
    after = CI.ignore_state(loc, env)
    assert f"config file {cfg}" in CI.ignore_changes(before, after)[0]     # the reason prints names with repr()
    assert CI.ignore_refusal(before, after, "the suite")


def test_b173_1_global_names_that_cannot_be_told_apart_read_unavailable(tmp_path):
    """B173 finding 1: GIT_CONFIG_GLOBAL unset, git lists the global files one per line; with a line feed in HOME the
    list cannot be split back into names, so the element reads unavailable and the run INCONCLUSIVE, never absent."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    home = tmp_path / "ho\nme"
    home.mkdir()
    env = {k: v for k, v in os.environ.items() if k not in ("GIT_CONFIG_GLOBAL", "XDG_CONFIG_HOME")}
    env.update(HOME=str(home), GIT_CONFIG_NOSYSTEM="1")
    state = CI.ignore_state(loc, env)
    assert state["config file (global)"].startswith("unreadable"), state.get("config file (global)")
    why = CI.ignore_refusal(state, CI.ignore_state(loc, env), "the suite")
    assert why and "could not be read" in why and "config file (global)" in why, why


def test_b173_1_no_ign_producer_splits_a_name_list_except_the_guarded_global_listing():
    """B173 finding 1, by population (census): ignore_state_one() asks git for one name per query (_git_name). The one
    newline split left is `git var GIT_CONFIG_GLOBAL` with the variable unset, where git prints several names; it runs
    only after the guard that neither HOME nor XDG_CONFIG_HOME holds a line feed. On stage E2i3 three producers split."""
    import inspect
    src = inspect.getsource(S.CI.ignore_state_one)
    assert src.count('.split("\\n")') == 1, src.count('.split("\\n")')
    guard = src.index('any("\\n" in env.get(k, "") for k in ("HOME", "XDG_CONFIG_HOME"))')
    assert guard < src.index('.split("\\n")')
    # E2i5: the four --git-path names (git var is read in one loop, B174); E2i9 (B179 finding 5, changed census): the
    # working tree git uses, one name from `rev-parse --show-toplevel`
    assert src.count("_git_name(") == 3       # E2i10 (B181 finding 2, changed census): the selected index's path
    assert src.count('_git_name(repo, env, "rev-parse", "--show-toplevel")') == 1



# --- REVW9's B174 read of stage E2i4: whether git reads an input is git's answer ----------------------------------

@pytest.mark.parametrize("flag", ["0", "false", "no", "off", "", None, "1", "true"])
def test_b174_1_the_system_file_is_read_exactly_when_git_reads_it(tmp_path, flag):
    """B174 finding 1 (REVW9's falsifier). GIT_CONFIG_SYSTEM names a comment-only file; GIT_CONFIG_NOSYSTEM is each
    spelling (None: unset). Where git reads the system file (`0`, `false`, `no`, `off`, empty, unset: its boolean
    reading) a change to it is named; where git reads none (`1`, `true`) IGN records git's answer, `none`, and
    nothing is named. On stage E2i4 Python's truth decided, so the four false-valued spellings skipped the file and
    its change passed."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    sysfile = tmp_path / "sysconfig"
    sysfile.write_text("# comment only\n")
    env = {k: v for k, v in os.environ.items() if k != "GIT_CONFIG_NOSYSTEM"}
    env.update(GIT_CONFIG_SYSTEM=str(sysfile), GIT_CONFIG_GLOBAL="/dev/null")
    if flag is not None:
        env["GIT_CONFIG_NOSYSTEM"] = flag
    git_reads = subprocess.run(["git", "var", "GIT_CONFIG_SYSTEM"], env=env, capture_output=True).returncode == 0
    assert git_reads == (flag not in ("1", "true")), (flag, git_reads)      # git's own reading of the flag
    before = CI.ignore_state(loc, env)
    sysfile.write_text("# comment only, changed\n")
    changed = CI.ignore_changes(before, CI.ignore_state(loc, env))[0]
    if git_reads:
        assert f"config file {sysfile}" in changed, (flag, changed)
    else:
        assert before["config file (system)"].startswith("none") and not changed, (flag, before.get("config file (system)"), changed)


def test_b174_1_an_empty_global_variable_is_git_s_answer_not_unavailable(tmp_path):
    """B174 finding 1, global: GIT_CONFIG_GLOBAL empty makes git read no global file (`git var` exits 1 with no output);
    IGN records that answer, `none`, rather than reading it as unavailable."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    env = dict(os.environ, GIT_CONFIG_GLOBAL="", GIT_CONFIG_NOSYSTEM="1")
    state = CI.ignore_state(loc, env)
    assert state["config file (global)"].startswith("none"), state.get("config file (global)")
    assert state["config file (system)"].startswith("none"), state.get("config file (system)")


def test_b174_1_no_ign_producer_reads_git_s_environment_for_a_selection():
    """B174 finding 1, by population (census): ignore_state_one() does not read GIT_CONFIG_NOSYSTEM (git var answers
    whether the system file is read). Its only environment reads are HOME and XDG_CONFIG_HOME (the default ignore
    file's path, composed as git composes it, and the line-feed guard) and the presence of GIT_CONFIG_GLOBAL (set:
    git names one file). On stage E2i4 it branched on Python's truth of GIT_CONFIG_NOSYSTEM."""
    import inspect, re
    src = inspect.getsource(S.CI.ignore_state_one)
    body = src[src.index('    repo = Path(os.path.abspath(repo))'):]
    body = "\n".join(line.split("#")[0] for line in body.splitlines())
    assert "GIT_CONFIG_NOSYSTEM" not in body
    reads = set(re.findall(r'env\.get\("([A-Z_]+)"', body)) | set(re.findall(r'"([A-Z_]+)" in env', body))
    assert reads == {"HOME", "XDG_CONFIG_HOME", "GIT_CONFIG_GLOBAL"}, reads


# --- REVW9's B175 read of stage E2i5: every included configuration file is in the population ---------------------

@pytest.mark.parametrize("form", ["absolute", "relative", "home", "onbranch", "inactive"])
def test_b175_1_an_included_file_with_no_settings_is_read(tmp_path, monkeypatch, form):
    """B175 finding 1 (REVW9's falsifier). The global file includes a file holding comments only, so it has no
    `--show-origin` entry; a change to its bytes is named. Forms: an absolute path, a path relative to the including
    file, a `~/` path git expands, an `includeIf.onbranch:` include that is active, and an include whose condition is
    false (read too: a disclosed admission cost). On stage E2i5 the population was the origins only, and the change
    passed."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\\\n    assert True\\\\n")
    home = tmp_path / "home"
    (home / "inc").mkdir(parents=True)
    child = home / "inc" / "child.cfg"
    child.write_text("# comments only\\n")
    branch = g("rev-parse", "--abbrev-ref", "HEAD")
    value = {"absolute": str(child), "relative": "inc/child.cfg", "home": "~/inc/child.cfg",
             "onbranch": str(child), "inactive": str(child)}[form]
    section = {"onbranch": f'[includeIf "onbranch:{branch}"]', "inactive": '[includeIf "gitdir:/no/such/place/"]'}
    gcfg = home / "gcfg"
    gcfg.write_text(f"{section.get(form, '[include]')}\n\tpath = {value}\n")
    env = {k: v for k, v in os.environ.items() if k not in ("XDG_CONFIG_HOME",)}
    env.update(HOME=str(home), GIT_CONFIG_GLOBAL=str(gcfg), GIT_CONFIG_NOSYSTEM="1")
    before = CI.ignore_state(loc, env)
    child.write_text("# comments only, changed\\n")
    changed = CI.ignore_changes(before, CI.ignore_state(loc, env))[0]
    assert f"config file {child}" in changed, (form, changed, sorted(before))


def test_b175_1_an_include_git_cannot_expand_reads_unavailable(tmp_path):
    """B175 finding 1: an include value git cannot expand as a path (`~nosuchuser/x`) is never left out: git's own
    listing fails on it (read from git 2.50.1), so the listing element reads unavailable and the run INCONCLUSIVE; were
    the listing to succeed, the include's own element would read unavailable."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\\\n    assert True\\\\n")
    gcfg = tmp_path / "gcfg"
    gcfg.write_text("[include]\n\tpath = ~nosuchuser-aget-kit/x.cfg\n")
    env = dict(os.environ, GIT_CONFIG_GLOBAL=str(gcfg), GIT_CONFIG_NOSYSTEM="1")
    state = CI.ignore_state(loc, env)
    # changed at E2i10 (B181 finding 1, labelled): git's repository question now fails first on the same bad include
    # (`fatal: bad config line`), so `repository` itself reads unavailable; the reading stays unavailable either way
    bad = [k for k, v in state.items() if k.startswith(("config include", "config file (listing)", "repository"))
           and str(v).startswith("unreadable")]
    assert bad, sorted(state)


# --- REVW9's B176 read of stage E2i6: no listing entry is passed over -------------------------------------------

@pytest.mark.parametrize("form", ["unconditional", "onbranch"])
def test_b176_1_a_file_included_by_process_configuration_is_read(tmp_path, form):
    """B176 finding 1 (REVW9's falsifier). Process configuration (GIT_CONFIG_COUNT/KEY_0/VALUE_0, origin `command
    line:`) includes a comment-only file, unconditionally or by an active `onbranch:`; a change to that file is named.
    On stage E2i6 the `command line:` origin was skipped before the include check, and the change passed."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    child = tmp_path / "proc-child.cfg"
    child.write_text("# comments only\n")
    key = "include.path" if form == "unconditional" else f"includeIf.onbranch:{g('rev-parse', '--abbrev-ref', 'HEAD')}.path"
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", GIT_CONFIG_COUNT="1",
               GIT_CONFIG_KEY_0=key, GIT_CONFIG_VALUE_0=str(child))
    before = CI.ignore_state(loc, env)
    child.write_text("# comments only, changed\n")
    changed = CI.ignore_changes(before, CI.ignore_state(loc, env))[0]
    assert f"config file {child}" in changed, (form, changed)


def test_b176_1_an_origin_ign_cannot_read_is_unavailable(tmp_path, monkeypatch):
    """B176 finding 1, by construction: a listing entry whose origin is neither a file nor process configuration
    (here a `blob:` origin, injected into the listing) reads unavailable, never passed over."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    real = CI._ign_git

    def fake(repo_, env_, *args):
        p = real(repo_, env_, *args)
        if args[:3] == ("config", "--list", "--show-origin"):
            p = subprocess.CompletedProcess(p.args, 0, p.stdout + b"blob:abc123\0x.y\nz\0", p.stderr)
        return p
    monkeypatch.setattr(CI, "_ign_git", fake)
    state = CI.ignore_state(loc, dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null"))
    bad = [k for k, v in state.items() if k.startswith("config origin") and str(v).startswith("unreadable")]
    assert bad == ["config origin 'blob:abc123'"], sorted(state)


def test_b176_1_the_listing_loop_passes_no_entry_over():
    """B176 finding 1, by population (census): the configuration listing loop in ignore_state_one() has no `continue`
    (every entry is read, or its origin reads unavailable). On stage E2i6 a non-file origin was skipped."""
    import inspect
    src = inspect.getsource(S.CI.ignore_state_one)
    loop = src[src.index('for origin, entry in zip(tokens[0:-1:2], tokens[1::2]):'):src.index('for path, v in sorted(')]
    assert "continue" not in loop
    assert 'f"config origin {o!r}"' in loop


# --- REVW9's B177 read of stage E2i7: IGN's queries describe the scope ordinary git reads -----------------------

@pytest.mark.parametrize("alternate", [True, False])
def test_b177_1_an_alternate_config_query_file_does_not_hide_an_input(tmp_path, alternate):
    """B177 finding 1 (REVW9's falsifier). The global file includes a comment-only file; with GIT_CONFIG naming another
    file (which only `git config` reads), a change to the included file is still named. On stage E2i7 the listing came
    from the alternate file, and the change passed. Control: without GIT_CONFIG it is named on both stages."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    child = tmp_path / "child.cfg"
    child.write_text("# comments only\n")
    gcfg = tmp_path / "gcfg"
    gcfg.write_text(f"[include]\n\tpath = {child}\n")
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(gcfg))
    if alternate:
        alt = tmp_path / "alternate.cfg"
        alt.write_text("[x]\n\ty = z\n")
        env["GIT_CONFIG"] = str(alt)
    before = CI.ignore_state(loc, env)
    child.write_text("# comments only, changed\n")
    changed = CI.ignore_changes(before, CI.ignore_state(loc, env))[0]
    assert f"config file {child}" in changed, (alternate, changed)


def test_b177_1_ign_queries_never_carry_git_config():
    """B177 finding 1, by population (census): every IGN git query goes through _ign_git, which removes GIT_CONFIG."""
    import inspect
    assert 'run_env.pop("GIT_CONFIG", None)' in inspect.getsource(S.CI._ign_git)
    src = inspect.getsource(S.CI.ignore_state_one)
    assert "subprocess.run(" not in src, "an IGN query outside _ign_git"


# --- REVW9's B179 read of stage C2a: IGN reads the index and working tree git selects ----------------------------

@pytest.mark.parametrize("selected", [True, False])
def test_b179_4_a_flag_change_in_the_selected_index_is_named(tmp_path, selected):
    """B179 finding 4 (REVW9's falsifier). With GIT_INDEX_FILE selecting another index, git marks a path skip-worktree
    there; IGN names the index flags. On stage C2a2 read_git dropped GIT_INDEX_FILE and copied the default index, so
    the change passed. Control: with no selection the default index is read on both stages."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
    if selected:
        index = tmp_path / "selected-index"
        index.write_bytes((loc / ".git" / "index").read_bytes())
        env["GIT_INDEX_FILE"] = str(index)
    before = CI.ignore_state(loc, env)
    subprocess.run(["git", "-C", str(loc), "update-index", "--skip-worktree", "tests/test_x.py"], env=env, check=True)
    changed = CI.ignore_changes(before, CI.ignore_state(loc, env))[0]
    assert "index flags" in changed, (selected, changed)


def test_b179_4_read_git_reads_a_copy_of_the_selected_index(tmp_path):
    """B179 finding 4: read_git copies the index git selects (a caller's GIT_INDEX_FILE), reads that copy, and leaves
    the selected index's bytes as they were. On stage C2a2 it read the default index."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    (loc / "only-in-selected.txt").write_text("x\n")
    index = tmp_path / "selected-index"
    index.write_bytes((loc / ".git" / "index").read_bytes())
    env = dict(os.environ, GIT_INDEX_FILE=str(index))
    subprocess.run(["git", "-C", str(loc), "add", "only-in-selected.txt"], env=env, check=True)
    held = index.read_bytes()
    p = CI.read_git(loc, "ls-files", env=env, text=True)
    assert "only-in-selected.txt" in p.stdout.split(), p.stdout
    assert index.read_bytes() == held
    assert "only-in-selected.txt" not in g("ls-files").split()      # the default index is not the one read


@pytest.mark.parametrize("selected", ["env", "config", False])
def test_b179_5_a_change_to_the_selected_working_tree_ignore_file_is_named(tmp_path, selected):
    """B179 finding 5 (REVW9's falsifier). With GIT_WORK_TREE or core.worktree selecting another working tree, a change
    to that tree's `.gitignore` is named. On stage C2a2 the walk read the supplied folder, and the change passed.
    Control: with no selection the supplied folder is git's tree on both stages."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
    actual = tmp_path / "selected-tree" if selected else loc
    actual.mkdir(exist_ok=True)
    if selected == "env":
        env["GIT_WORK_TREE"] = str(actual)
    elif selected == "config":
        g("config", "core.worktree", str(actual))
    rule = actual / ".gitignore"
    rule.write_text("marker.txt\n")
    before = CI.ignore_state(loc, env)
    rule.write_text("marker.txt\n# changed\n")
    changed = CI.ignore_changes(before, CI.ignore_state(loc, env))[0]
    assert ".gitignore .gitignore" in changed, (selected, changed)


def test_b179_5_a_working_tree_selection_is_itself_an_element(tmp_path):
    """B179 finding 5: a selection of another working tree reads as an element of its own, so a run that starts
    selecting another tree is named even when the two trees hold the same `.gitignore` bytes."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    actual = tmp_path / "selected-tree"
    actual.mkdir()
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
    before = CI.ignore_state(loc, env)
    after = CI.ignore_state(loc, dict(env, GIT_WORK_TREE=str(actual)))
    assert ".gitignore (working tree)" not in before
    assert after[".gitignore (working tree)"].startswith("selected by git: ")
    assert ".gitignore (working tree)" in CI.ignore_changes(before, after)[0]


def test_b179_5_a_working_tree_git_does_not_name_is_unavailable(tmp_path, monkeypatch):
    """B179 finding 5, refusal side: when git does not name the working tree it uses, element (i) reads unavailable
    and no folder is walked in its place."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    (loc / ".gitignore").write_text("x\n")
    real = CI._git_name

    def fake(repo_, env_, *args):
        return None if args == ("rev-parse", "--show-toplevel") else real(repo_, env_, *args)
    monkeypatch.setattr(CI, "_git_name", fake)
    state = CI.ignore_state(loc, dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null"))
    assert state[".gitignore (working tree)"].startswith("unreadable")
    assert ".gitignore .gitignore" not in state


# --- REVW9's B181 read of stage E2i9: git's answer decides the repository; an unreadable selected index fails -------

@pytest.mark.parametrize("element", ["exclude", "config"])
@pytest.mark.parametrize("route", ["git_dir", "ancestor"])
def test_b181_1_a_repository_git_selects_without_a_local_dotgit_is_read(tmp_path, route, element):
    """B181 finding 1 (REVW9's falsifier). The supplied folder has no `.git` entry, but git selects a repository for it
    (GIT_DIR, or discovery in an ancestor); a change to that repository's `info/exclude`, or to its `config` (a key
    that changes its bytes: on macOS `git init` already writes `core.ignorecase = true`), is named. On stage E2i9 the
    local `.git` entry decided, the folder read `repository: none`, and the change passed."""
    CI = S.CI
    top, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
    if route == "git_dir":
        loc = tmp_path / "plain"
        loc.mkdir()
        env.update(GIT_DIR=str(top / ".git"), GIT_WORK_TREE=str(loc))
    else:
        loc = top / "nested"
        loc.mkdir()
    exclude = top / ".git" / "info" / "exclude"
    exclude.parent.mkdir(exist_ok=True)
    exclude.write_text("# before\n")
    before = CI.ignore_state(loc, env)
    assert "repository" not in before, before
    if element == "exclude":
        exclude.write_text("# after\n")
    else:
        g("config", "status.showUntrackedFiles", "no")
    changed = CI.ignore_changes(before, CI.ignore_state(loc, env))[0]
    want = "info/exclude" if element == "exclude" else f"config file {top / '.git' / 'config'}"
    assert any(c == want or (element == "config" and c.startswith("config file") and c.endswith("config"))
               for c in changed), (route, element, changed)


def test_b181_1_a_folder_git_names_no_repository_for_is_plain(tmp_path):
    """B181 finding 1, control: a folder git names no repository for (outside every repository, discovery stopped by
    GIT_CEILING_DIRECTORIES) still reads `repository: none`."""
    CI = S.CI
    loc = tmp_path / "plain"
    loc.mkdir()
    state = CI.ignore_state(loc, dict(os.environ, GIT_CEILING_DIRECTORIES=str(tmp_path)))
    assert state["repository"] == "none: git names no repository", state


def test_b181_1_no_answer_from_git_is_unavailable(tmp_path, monkeypatch):
    """B181 finding 1, refusal side: when git does not say whether the folder is a repository, the reading is
    unavailable, never the plain-folder state."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    real = CI._ign_git

    def fake(repo_, env_, *args):
        if args == ("rev-parse", "--absolute-git-dir"):
            return subprocess.CompletedProcess(args, 129, b"", b"usage: something else")
        return real(repo_, env_, *args)
    monkeypatch.setattr(CI, "_ign_git", fake)
    state = CI.ignore_state(loc, dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null"))
    assert state["repository"].startswith("unreadable"), state


def test_b181_2_a_selected_index_that_is_not_a_regular_file_fails_the_read(tmp_path):
    """B181 finding 2 (REVW9's falsifier). The selected index path is a directory: git refuses to map it, and so does
    read_git; IGN's index flags read unavailable. On stage E2i9 read_git returned an empty, successful read."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    index = tmp_path / "selected-index"
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null", GIT_INDEX_FILE=str(index))
    assert CI.read_git(loc, "ls-files", env=env).returncode == 0          # absent: empty, as in git
    index.mkdir()
    assert subprocess.run(["git", "-C", str(loc), "ls-files"], env=env, capture_output=True).returncode != 0
    p = CI.read_git(loc, "ls-files", env=env)
    assert p.returncode != 0 and b"not a regular file" in p.stderr, p
    assert CI.ignore_state(loc, env)["index flags"].startswith("unreadable")


def test_b181_2_a_switch_of_selected_index_is_named_even_with_equal_flags(tmp_path):
    """B181 finding 2, by construction (FWK-OVSR4's E2i9 advisory (5)): a caller-selected index is itself an element, so
    a switch to another index holding the same flags is named."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    one, two = tmp_path / "one-index", tmp_path / "two-index"
    for x in (one, two):
        x.write_bytes((loc / ".git" / "index").read_bytes())
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
    before = CI.ignore_state(loc, dict(env, GIT_INDEX_FILE=str(one)))
    after = CI.ignore_state(loc, dict(env, GIT_INDEX_FILE=str(two)))
    assert before["index flags"] == after["index flags"]
    assert "index file" in CI.ignore_changes(before, after)[0]


# --- REVW9's B183 read of stage E2i10: a failed query is never an answer ------------------------------------------

@pytest.mark.parametrize("lookalike", [True, False])
def test_b183_1_a_failed_discovery_query_is_unavailable_whatever_its_text(tmp_path, lookalike):
    """B183 finding 1 (REVW9's falsifier). The global config git reads is invalid; its file is named `not a git
    repository.cfg` (or, control, an ordinary name). git's repository question fails with `bad config line …`, so
    the reading is unavailable, and a change of those bytes is not a pass. On stage E2i10 the substring test read the
    lookalike name as "no repository" at both readings and the change passed."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    bad = tmp_path / ("not a git repository.cfg" if lookalike else "global.cfg")
    bad.write_text("[broken\n")
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=str(bad))
    before = CI.ignore_state(loc, env)
    bad.write_text("[still broken\n")
    after = CI.ignore_state(loc, env)
    assert before["repository"].startswith("unreadable"), before
    assert CI.ignore_refusal(before, after, "a run"), (before, after)


@pytest.mark.parametrize("form", ["git_dir", "gitfile"])
def test_b183_1_a_selection_naming_no_repository_is_unavailable(tmp_path, form):
    """B183 finding 1 with FWK-OVSR5's E2i10 advisory (2): a GIT_DIR, or a `.git` file's `gitdir:`, naming nothing makes
    git say `not a git repository: '<path>'`, which is not its discovery answer: unavailable, not a plain folder."""
    CI = S.CI
    loc = tmp_path / "plain"
    loc.mkdir()
    env = dict(os.environ, GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL="/dev/null")
    if form == "git_dir":
        env["GIT_DIR"] = str(tmp_path / "nowhere")
    else:
        (loc / ".git").write_text(f"gitdir: {tmp_path / 'nothing'}\n")
    assert CI.ignore_state(loc, env)["repository"].startswith("unreadable")


def test_b183_1_only_gits_discovery_answer_reads_as_a_plain_folder():
    """B183 finding 1: the classifier takes git's whole diagnostic, in its two discovery forms only."""
    CI = S.CI
    assert CI.NO_REPOSITORY.fullmatch(b"fatal: not a git repository (or any of the parent directories): .git\n")
    assert CI.NO_REPOSITORY.fullmatch(b"fatal: not a git repository (or any parent up to mount point /v)\n"
                                      b"Stopping at filesystem boundary (GIT_DISCOVERY_ACROSS_FILESYSTEM not set).\n")
    for other in (b"fatal: bad config line 1 in file /x/not a git repository.cfg\n",
                  b"fatal: not a git repository: '/x/nowhere'\n",
                  b"fatal: not a git repository (or any of the parent directories): .git\\nmore\n"):
        assert not CI.NO_REPOSITORY.fullmatch(other), other


def test_b183_1_tracked_and_blob_readers_tell_absent_from_failed(tmp_path):
    """B183 finding 1 with FWK-OVSR5's E2i10 advisory (5) and (7): git_tracked and git_blob_at answer only from a read
    that succeeded; a failed read (here a selected index that is a directory) raises InspectionFailed, never reads
    "untracked" or "absent"."""
    CI = S.CI
    loc, g = repo(tmp_path, "def test_a():\\n    assert True\\n")
    assert CI.git_tracked(loc, "tests/test_x.py") is True
    assert CI.git_tracked(loc, "nope.txt") is False
    assert CI.git_blob_at(loc, "HEAD", "tests/test_x.py").startswith(b"def test_a")
    assert CI.git_blob_at(loc, "HEAD", "nope.txt") is None
    index = tmp_path / "index-dir"
    index.mkdir()
    env = dict(os.environ, GIT_INDEX_FILE=str(index))
    with pytest.raises(CI.InspectionFailed):
        CI.git_tracked(loc, "tests/test_x.py", env=env)
    with pytest.raises(CI.InspectionFailed):
        CI.git_blob_at(loc, "HEAD", "tests/test_x.py", env=env)


def test_b183_1_no_kit_tool_reads_a_failed_git_query_as_an_answer():
    """B183 finding 1, by population (census): no kit tool uses `--error-unmatch` (its exit status does not tell an
    untracked path from a failed read); after-run checks A and D and the KEEP/MERGE judgement read HEAD through
    git_blob_at. Scope: the `read_git` sites that read a failure as an answer (four on stage E2i10); `git show` reads
    through the tools' own `git()` wrappers are not covered by this census."""
    kit = Path(S.__file__).resolve().parent
    assert not [p.name for p in kit.glob("*.py") if '"--error-unmatch"' in p.read_text()]   # as a git argument
    arc = (kit / "after_run_check.py").read_text()
    # E2i13 added H; Round 2 adds the executable-bit judgement through the same validated reader.
    assert arc.count('CI.git_blob_at(root, "HEAD"') == 5
