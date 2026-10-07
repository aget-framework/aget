"""launch_batch.session_env / run_grouped (G2 step 2): a push from a batch session to a remote whose URL starts with
one of seven listed prefixes fails (tested with a local-path remote only; a remote with an explicit pushurl, git://...
and user@host:... with a user other than git are not covered by the tool), and the session's process group is killed afterwards.
one receiver 2026-09-29 17:48: its suite's own wind-down committed and pushed 7 commits from inside the B6 session."""
import importlib.util
import os
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_s = importlib.util.spec_from_file_location(
    "launch_batch", ROOT / "scripts/migration_kit/launch_batch.py")
lb = importlib.util.module_from_spec(_s)
_s.loader.exec_module(lb)


def git(repo, *a, env=None):
    return subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                          capture_output=True, text=True, env=env)


def pair(tmp_path):
    origin, work = tmp_path / "origin.git", tmp_path / "work"
    subprocess.run(["git", "init", "-q", "--bare", str(origin)], check=True)
    subprocess.run(["git", "clone", "-q", str(origin), str(work)], check=True, capture_output=True)
    git(work, "commit", "-q", "--allow-empty", "-m", "c")
    return origin, work


def test_a_push_from_a_session_env_fails_and_reaches_nothing(tmp_path):
    """Fixture: a local-path remote (prefix "/"). The other six prefixes and the uncovered URL forms are not tested."""
    origin, work = pair(tmp_path)
    r = git(work, "push", "-q", "origin", "HEAD:refs/heads/main", env=lb.session_env())
    assert r.returncode != 0
    assert subprocess.run(["git", "-C", str(origin), "branch", "--list", "main"], capture_output=True,
                          text=True).stdout == ""


def test_the_same_push_without_it_succeeds(tmp_path):
    """Control: the fixture's push works, so the refusal above is the env's doing."""
    origin, work = pair(tmp_path)
    assert git(work, "push", "-q", "origin", "HEAD:refs/heads/main").returncode == 0


def test_session_env_drops_claudecode_and_keeps_commits_possible(tmp_path, monkeypatch):
    monkeypatch.setenv("CLAUDECODE", "1")
    env = lb.session_env()
    assert "CLAUDECODE" not in env
    _, work = pair(tmp_path)
    assert git(work, "commit", "-q", "--allow-empty", "-m", "d", env=env).returncode == 0


def test_run_grouped_kills_what_the_session_leaves_running(tmp_path):
    pidfile = tmp_path / "bg.pid"
    code = f"import subprocess; p = subprocess.Popen(['sleep', '60']); open({str(pidfile)!r}, 'w').write(str(p.pid))"
    r = lb.run_grouped([sys.executable, "-c", code], tmp_path, dict(os.environ), 30)
    assert r.returncode == 0
    pid = int(pidfile.read_text())
    for _ in range(20):
        try:
            os.kill(pid, 0)
        except ProcessLookupError:
            return
        time.sleep(0.1)
    raise AssertionError(f"process {pid} outlived the session")


def test_a_cli_version_change_across_batches_is_reported_and_no_change_is_silent(tmp_path):
    """Carriage row 27: the CLI moved mid-wave with nothing saying so. Both directions.

    Satisfies: R-TEST-001-02
    """
    import json as _json
    prior = [{"batch": "batch1", "claude_version": "2.1.283"}, {"batch": "batch2", "claude_version": "2.1.283"}]
    note = lb.cli_version_changes(prior, "2.1.284")
    assert note and "batch1: 2.1.283" in note and "this batch: 2.1.284" in note
    assert lb.cli_version_changes(prior, "2.1.283") is None
    # sibling batch folders are found; this batch's own packet is excluded
    (tmp_path / "batch1").mkdir(); (tmp_path / "batch2").mkdir()
    (tmp_path / "batch1" / "LAUNCH_PACKET_batch1.json").write_text(_json.dumps({"batch": "batch1", "claude_version": "2.1.283"}))
    me = tmp_path / "batch2" / "LAUNCH_PACKET_batch2.json"; me.write_text(_json.dumps({"batch": "batch2", "claude_version": "2.1.284"}))
    found = lb._prior_packets(me)
    assert [p["batch"] for p in found] == ["batch1"]
