"""Tests for the kit's open_receiver.py. Carried guards (moved Aget; inside a Claude session) and the principal's
`namedpreauth` rule (outside-filers:R9, 2026-09-29): a typed line at a terminal, or a pre-authorization naming the
window AND the batch. Both directions for each."""
import datetime as dt
import importlib.util
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_s = importlib.util.spec_from_file_location("open_receiver", ROOT / "scripts/migration_kit/open_receiver.py")
opener = importlib.util.module_from_spec(_s)
_s.loader.exec_module(opener)
NOW = dt.datetime(2026, 9, 30, 12, 0, tzinfo=dt.timezone.utc)


class _TTY:
    def __init__(self, tty=True):
        self._t = tty

    def isatty(self):
        return self._t


def seat(tmp_path):
    remote, loc = tmp_path / "r.git", tmp_path / "seat"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    subprocess.run(["git", "init", "-q", "-b", "main", str(loc)], check=True)

    def g(*a):
        return subprocess.run(["git", "-C", str(loc), "-c", "user.name=t", "-c", "user.email=t@t", *a],
                              check=True, capture_output=True, text=True).stdout.strip()
    (loc / "a").write_text("a\n"); g("add", "a"); g("commit", "-q", "-m", "a")
    g("remote", "add", "origin", str(remote)); g("push", "-q", "-u", "origin", "main")
    (loc / "b").write_text("b\n"); g("add", "b"); g("commit", "-q", "-m", "b")
    return loc, g


def _wire(tmp_path, monkeypatch):
    loc, g = seat(tmp_path)
    monkeypatch.chdir(opener.os.getcwd())          # main() chdirs before its (stubbed) exec
    monkeypatch.delenv("CLAUDECODE", raising=False)
    monkeypatch.setattr(opener.shutil, "which", lambda c: "/bin/claude")
    calls = []
    monkeypatch.setattr(opener.os, "execvp", lambda f, a: calls.append((f, a, opener.os.getcwd())))
    monkeypatch.setitem(opener.LINES, "k", (str(loc), "push your own 1 commit", "facts",
                                            {"head": g("rev-parse", "HEAD"), "ahead": 1}))
    return loc, g, calls


def _preauth(tmp_path, **entry):
    e = {"key": "k", "batch": "b12", "authorized_by": "principal", "typed_line": "GO supervisor - open k for b12",
         "expires": "2026-09-30T18:00:00+00:00"}
    e.update(entry)
    p = tmp_path / "preauth.json"
    p.write_text(json.dumps({"entries": [e]}))
    return p


def test_a_typed_open_line_at_a_terminal_opens_and_a_moved_aget_is_refused(tmp_path, monkeypatch, capsys):
    """Satisfies: R-TEST-001-02"""
    loc, g, calls = _wire(tmp_path, monkeypatch)
    monkeypatch.setattr("builtins.input", lambda _p: "OPEN k")
    opener.main(["k"], now=NOW, stdin=_TTY())
    assert calls and calls[0][1] == ["claude", "push your own 1 commit"]
    assert Path(calls[0][2]).resolve() == loc.resolve()
    (loc / "c").write_text("c\n"); g("add", "c"); g("commit", "-q", "-m", "c")
    calls.clear()
    assert opener.main(["k"], now=NOW, stdin=_TTY()) == 3 and not calls
    assert "REFUSED" in capsys.readouterr().out


def test_it_refuses_inside_a_claude_session(tmp_path, monkeypatch):
    """Satisfies: R-TEST-001-02"""
    _loc, _g, calls = _wire(tmp_path, monkeypatch)
    monkeypatch.setenv("CLAUDECODE", "1")
    assert opener.main(["k"], now=NOW, stdin=_TTY()) == 2 and not calls


def test_no_terminal_and_no_preauthorization_is_refused(tmp_path, monkeypatch, capsys):
    """FALSIFIER, the 2026-09-29 case: a supervisor process opens a window with no typed line.

    Satisfies: R-TEST-001-02
    """
    _loc, _g, calls = _wire(tmp_path, monkeypatch)
    assert opener.main(["k"], now=NOW, stdin=_TTY(False)) == 4 and not calls
    assert "NOT AUTHORIZED" in capsys.readouterr().out


def test_a_wrong_typed_line_is_refused(tmp_path, monkeypatch):
    """Satisfies: R-TEST-001-02"""
    _loc, _g, calls = _wire(tmp_path, monkeypatch)
    monkeypatch.setattr("builtins.input", lambda _p: "yes")
    assert opener.main(["k"], now=NOW, stdin=_TTY()) == 4 and not calls


def test_a_preauthorization_naming_the_window_and_batch_opens(tmp_path, monkeypatch):
    """Satisfies: R-TEST-001-02"""
    _loc, _g, calls = _wire(tmp_path, monkeypatch)
    p = _preauth(tmp_path)
    opener.main(["k", "--batch", "b12", "--preauth", str(p)], now=NOW, stdin=_TTY(False))
    assert calls and calls[0][1][0] == "claude"


def test_a_preauthorization_for_another_batch_or_expired_or_not_the_principals_is_refused(tmp_path, monkeypatch):
    """A pre-authorization is not a blank cheque: wrong batch, missing batch, expiry, author each refuse.

    Satisfies: R-TEST-001-02
    """
    _loc, _g, calls = _wire(tmp_path, monkeypatch)
    assert opener.main(["k", "--batch", "b13", "--preauth", str(_preauth(tmp_path))], now=NOW) == 4
    assert opener.main(["k", "--preauth", str(_preauth(tmp_path))], now=NOW) == 4
    assert opener.main(["k", "--batch", "b12", "--preauth", str(_preauth(tmp_path, expires="2026-09-30T06:00:00+00:00"))],
                       now=NOW) == 4
    assert opener.main(["k", "--batch", "b12", "--preauth", str(_preauth(tmp_path, authorized_by="supervisor"))],
                       now=NOW) == 4
    assert not calls


def test_receivers_are_data_not_code(tmp_path):
    """The kit ships the mechanism; the per-Aget lines are the running supervisor's data.

    Satisfies: R-TEST-001-02
    """
    r = tmp_path / "receivers.json"
    r.write_text(json.dumps({"x": {"folder": "/tmp", "line": "hello", "facts": "f", "expect": {"head": "h", "ahead": 0}}}))
    assert opener.load_receivers(r)["x"][1] == "hello"
    src = (ROOT / "scripts/migration_kit/open_receiver.py").read_text()
    assert "/Users/" not in src and "v3.35.0 migration" not in src
