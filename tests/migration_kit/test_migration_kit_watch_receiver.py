"""R-F16 (rehearsal 2026-09-30): the kit ships the receiver watcher the procedure tells a supervisor to arm.

SOP v1.10.0 says to watch a receiver's last turn as well as its HEAD, and the kit carried no watcher, so the
rehearsal's supervisor ended its turn on a receiver act and waited on nothing. watch_receiver.py exits on the first
of three events: the receiver's turn ends, its HEAD moves, its remote moves. A failed probe is reported and never
read as "no change".
"""
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "scripts" / "migration_kit"
ENV = {"GIT_AUTHOR_NAME": "t", "GIT_AUTHOR_EMAIL": "t@t", "GIT_COMMITTER_NAME": "t", "GIT_COMMITTER_EMAIL": "t@t",
       "PATH": __import__("os").environ["PATH"], "HOME": __import__("os").environ.get("HOME", "")}


def _load():
    spec = importlib.util.spec_from_file_location("watch_receiver", KIT / "watch_receiver.py")
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m


def _git(repo, *args):
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True, text=True, env=ENV, check=True).stdout


def _receiver(tmp_path):
    origin = tmp_path / "origin.git"
    subprocess.run(["git", "init", "-q", "--bare", "-b", "main", str(origin)], check=True, env=ENV)
    repo = tmp_path / "receiver"
    subprocess.run(["git", "init", "-q", "-b", "main", str(repo)], check=True, env=ENV)
    (repo / "a").write_text("a\n")
    _git(repo, "add", "a")
    _git(repo, "commit", "-qm", "base")
    _git(repo, "remote", "add", "origin", str(origin))
    _git(repo, "push", "-q", "origin", "main")
    projects = tmp_path / "projects"
    projects.mkdir()
    return repo, projects


def _entry(kind, stop=None):
    return json.dumps({"type": kind, "message": {"stop_reason": stop} if stop else {}}) + "\n"


def _commit(repo, name):
    (repo / name).write_text(name)
    _git(repo, "add", name)
    _git(repo, "commit", "-qm", name)


def _watch(W, repo, projects, during, **kw):
    """Run the watch loop with a fake clock; `during` acts between the baseline and the first poll."""
    lines, ticks = [], iter(range(0, 10_000, 5))
    state = {"n": 0}

    def sleep(_):
        if state["n"] == 0 and during:
            during()
        state["n"] += 1

    code = W.watch(repo, "refs/heads/main", projects, interval=5, remote_interval=5, timeout=kw.get("timeout", 60),
                   say=lines.append, sleep=sleep, clock=lambda: next(ticks))
    return code, lines


def test_exits_on_a_head_move(tmp_path):
    W = _load()
    repo, projects = _receiver(tmp_path)
    code, lines = _watch(W, repo, projects, lambda: _commit(repo, "b"))
    assert code == 0 and any(l.startswith("EVENT head-moved") for l in lines), lines


def test_exits_on_a_remote_move(tmp_path):
    W = _load()
    repo, projects = _receiver(tmp_path)
    other = tmp_path / "other"
    subprocess.run(["git", "clone", "-q", str(tmp_path / "origin.git"), str(other)], check=True, env=ENV)

    def push_from_elsewhere():
        _commit(other, "c")
        _git(other, "push", "-q", "origin", "main")

    code, lines = _watch(W, repo, projects, push_from_elsewhere)
    assert code == 0 and any(l.startswith("EVENT remote-moved") for l in lines), lines


def test_exits_when_the_receivers_turn_ends(tmp_path):
    W = _load()
    repo, projects = _receiver(tmp_path)
    t = projects / "s.jsonl"
    t.write_text(_entry("user") + _entry("assistant", "tool_use"))
    code, lines = _watch(W, repo, projects, lambda: t.open("a").write(_entry("assistant", "end_turn")))
    assert code == 0 and any(l.startswith("EVENT turn-ended") for l in lines), lines


def test_a_tool_call_is_not_a_turn_end(tmp_path):
    """FALSIFIER: a watcher that fires on any transcript growth would release the supervisor mid-turn."""
    W = _load()
    repo, projects = _receiver(tmp_path)
    t = projects / "s.jsonl"
    t.write_text(_entry("user"))
    code, lines = _watch(W, repo, projects, lambda: t.open("a").write(_entry("assistant", "tool_use")), timeout=20)
    assert code == 3 and any(l.startswith("TIMEOUT") for l in lines), lines


def test_a_failed_probe_is_reported_not_read_as_no_change(tmp_path):
    W = _load()
    repo, projects = _receiver(tmp_path)
    code, lines = _watch(W, repo, projects, lambda: __import__("shutil").rmtree(repo / ".git"))
    assert code == 2 and any(l.startswith("PROBE-FAILED") for l in lines), lines


def test_missing_transcripts_are_declared_at_arming(tmp_path):
    W = _load()
    repo, _ = _receiver(tmp_path)
    code, lines = _watch(W, repo, tmp_path / "absent", None, timeout=10)
    assert code == 3
    assert any("turn-end UNAVAILABLE" in l for l in lines), lines


def test_the_command_line_runs_and_times_out_cleanly(tmp_path):
    repo, projects = _receiver(tmp_path)
    r = subprocess.run([sys.executable, str(KIT / "watch_receiver.py"), str(repo), "--projects-dir", str(projects),
                        "--interval", "1", "--timeout", "2"], capture_output=True, text=True, timeout=60)
    assert r.returncode == 3 and "armed" in r.stdout and "TIMEOUT" in r.stdout, r.stdout + r.stderr


def test_the_tool_never_writes_to_the_receiver():
    src = (KIT / "watch_receiver.py").read_text()
    for verb in ('"commit"', '"push"', '"add"', '"fetch"', '"checkout"', '"reset"', "write_text", ".open(\"w\""):
        assert verb not in src, verb


# --- Several sessions in one receiver folder (found in review, 2026-10-01) -------------------------------------
# The first version summed turn ends across every transcript in the receiver's folder and did not say which session
# an event came from. On 2026-09-30 one Aget had three sessions in one checkout: the watcher would have released a
# supervisor on an unrelated session's turn. Events now name their session, and one session can be watched alone.

def _two_sessions(projects):
    s1, s2 = projects / "aaaa1111-one.jsonl", projects / "bbbb2222-two.jsonl"
    s1.write_text(_entry("user"))
    s2.write_text(_entry("user"))
    return s1, s2


def _watch_one(W, repo, projects, during, session, timeout=20):
    lines, ticks, state = [], iter(range(0, 10_000, 5)), {"n": 0}

    def sleep(_):
        if state["n"] == 0 and during:
            during()
        state["n"] += 1

    code = W.watch(repo, "refs/heads/main", projects, interval=5, remote_interval=5, timeout=timeout,
                   say=lines.append, sleep=sleep, clock=lambda: next(ticks), session=session)
    return code, lines


def test_a_turn_end_names_the_session_it_came_from(tmp_path):
    W = _load()
    repo, projects = _receiver(tmp_path)
    _, s2 = _two_sessions(projects)
    code, lines = _watch(W, repo, projects, lambda: s2.open("a").write(_entry("assistant", "end_turn")))
    assert code == 0
    assert any(l.startswith("EVENT turn-ended") and "bbbb2222" in l and "aaaa1111" not in l for l in lines), lines


def test_watching_one_session_ignores_another_sessions_turn_end(tmp_path):
    """FALSIFIER: the supervisor must not be released by a session it is not waiting on."""
    W = _load()
    repo, projects = _receiver(tmp_path)
    _, s2 = _two_sessions(projects)
    code, lines = _watch_one(W, repo, projects, lambda: s2.open("a").write(_entry("assistant", "end_turn")),
                             session="aaaa1111")
    assert code == 3 and not any(l.startswith("EVENT turn-ended") for l in lines), lines


def test_watching_one_session_fires_on_its_own_turn_end(tmp_path):
    W = _load()
    repo, projects = _receiver(tmp_path)
    s1, _ = _two_sessions(projects)
    code, lines = _watch_one(W, repo, projects, lambda: s1.open("a").write(_entry("assistant", "end_turn")),
                             session="aaaa1111")
    assert code == 0 and any(l.startswith("EVENT turn-ended") and "aaaa1111" in l for l in lines), lines


def test_a_session_with_no_transcript_is_declared_at_arming(tmp_path):
    W = _load()
    repo, projects = _receiver(tmp_path)
    _two_sessions(projects)
    code, lines = _watch_one(W, repo, projects, None, session="cccc3333", timeout=10)
    assert code == 3 and any("turn-end UNAVAILABLE" in l and "cccc3333" in l for l in lines), lines


def test_arming_says_how_many_sessions_it_is_watching(tmp_path):
    W = _load()
    repo, projects = _receiver(tmp_path)
    _two_sessions(projects)
    _, lines = _watch(W, repo, projects, None, timeout=10)
    assert any(l.startswith("armed") and "2 session transcripts" in l for l in lines), lines


def test_a_head_move_carries_the_commit_subject(tmp_path):
    """HEAD belongs to the checkout, not to a session: the subject lets the supervisor tell whose commit moved it."""
    W = _load()
    repo, projects = _receiver(tmp_path)
    code, lines = _watch(W, repo, projects, lambda: _commit(repo, "receiver-work"))
    assert code == 0 and any(l.startswith("EVENT head-moved") and "receiver-work" in l for l in lines), lines
