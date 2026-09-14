"""C-34-02 — an accepted receipt survives unrelated history, and only unrelated history.

Real git repositories, not fixtures: the load-bearing predicate is "no commit in
accepted..HEAD touched the target", and a touch-and-revert restores the BYTES. Only history
can tell the two apart, so only a real history can test it.

Live shape this replaces: four accepted routes passed, three confirmations validated, and a
migration wave stopped on current-HEAD equality alone.
"""
from __future__ import annotations

import hashlib
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "crc", REPO / "scripts" / "check_receipt_continuity.py")
crc = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(crc)

HOLDS, FAILS, UNAVAILABLE = crc.HOLDS, crc.FAILS, crc.UNAVAILABLE
TARGET = "governed/target.txt"


@pytest.mark.parametrize("unavailable", ["target", "worktree", "head"])
def test_unreadable_git_state_is_not_clean_or_quiescent(repo, monkeypatch, unavailable):
    r, accepted, digest = repo
    receipt = {"path": TARGET, "commit": accepted, "digest": digest}
    route = f"{sys.executable} -c 'from pathlib import Path; assert Path(\"{TARGET}\").is_file()'"
    control = crc.evaluate(receipt, receipt, r, route, True)
    assert crc.exit_code(control) == 0
    original_git = crc.git
    failed_args = {"target": ("status", "--porcelain", "--", TARGET),
                   "worktree": ("status", "--porcelain"),
                   "head": ("rev-parse", "HEAD")}[unavailable]

    def failed_read(root, *args):
        return (128, "") if args == failed_args else original_git(root, *args)

    monkeypatch.setattr(crc, "git", failed_read)
    result = crc.evaluate(receipt, receipt, r, route, True)
    assert crc.exit_code(result) == 2
    if unavailable == "target":
        check = result["target_continuity"]["checks"]["current_target_matches"]
        assert check["state"] == UNAVAILABLE
        assert check["target_dirty"] is None
    else:
        assert result["overall"] == HOLDS
        assert result["pending_transaction"]["state"] == UNAVAILABLE
        if unavailable == "worktree":
            assert result["pending_transaction"]["worktree_quiescent"] is None
            assert result["current_worktree"]["dirty_entries"] is None
        else:
            assert result["pending_transaction"]["exact_head"] is None


def run(repo: Path, *args: str) -> str:
    return subprocess.run(["git", "-C", str(repo), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


def commit(repo: Path, msg: str) -> str:
    run(repo, "add", "-A")
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t",
                    "-c", "commit.gpgsign=false", "commit", "-q", "-m", msg], check=True)
    return run(repo, "rev-parse", "HEAD")


def write(repo: Path, rel: str, text: str):
    p = repo / rel
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text)


@pytest.fixture
def repo(tmp_path):
    r = tmp_path / "repo"
    r.mkdir()
    run(r, "init", "-q")
    write(r, TARGET, "accepted content\n")
    write(r, "other.txt", "unrelated\n")
    accepted = commit(r, "accept the target")
    digest = hashlib.sha256((r / TARGET).read_bytes()).hexdigest()
    return r, accepted, digest


def papers(tmp_path, accepted, digest, *, path=TARGET, commit_=None, dig=None):
    rec = {"path": path, "commit": commit_ or accepted, "digest": dig or digest}
    rp, mp = tmp_path / "receipt.json", tmp_path / "manifest.json"
    rp.write_text(json.dumps(rec))
    mp.write_text(json.dumps(rec))
    return rp, mp


def ev(repo_, rp, mp, **kw):
    return crc.evaluate(json.loads(rp.read_text()), json.loads(mp.read_text()), repo_, None, kw.get("pending", False))


# --- the whole point: unrelated history must NOT revoke ----------------------------

def test_an_unrelated_later_commit_does_not_invalidate_the_receipt(repo, tmp_path):
    r, accepted, digest = repo
    write(r, "other.txt", "changed, and nothing to do with the target\n")
    commit(r, "unrelated advance")
    rp, mp = papers(tmp_path, accepted, digest)
    res = ev(r, rp, mp)
    assert res["target_continuity"]["checks"]["untouched_since_accepted"]["state"] == HOLDS
    assert res["target_continuity"]["checks"]["accepted_commit_ancestral"]["state"] == HOLDS


def test_unrelated_worktree_dirt_does_not_invalidate_and_is_not_a_clean_claim(repo, tmp_path):
    r, accepted, digest = repo
    write(r, "scratch.txt", "uncommitted unrelated dirt\n")
    rp, mp = papers(tmp_path, accepted, digest)
    res = ev(r, rp, mp)
    assert res["target_continuity"]["checks"]["current_target_matches"]["state"] == HOLDS
    assert res["current_worktree"]["dirty_entries"] >= 1
    assert "NO WHOLE-WORKTREE-CLEAN CLAIM" in res["current_worktree"]["claim"]


# --- and only unrelated history ----------------------------------------------------

def test_a_touch_and_revert_fails_even_though_the_bytes_match(repo, tmp_path):
    """The load-bearing case. Byte equality passes; continuity must not."""
    r, accepted, digest = repo
    write(r, TARGET, "tampered\n")
    commit(r, "touch the target")
    write(r, TARGET, "accepted content\n")
    commit(r, "restore identical bytes")
    assert hashlib.sha256((r / TARGET).read_bytes()).hexdigest() == digest, "bytes restored"
    rp, mp = papers(tmp_path, accepted, digest)
    res = ev(r, rp, mp)
    c = res["target_continuity"]["checks"]
    assert c["current_target_matches"]["state"] == HOLDS, "bytes do match -- that is the trap"
    assert c["untouched_since_accepted"]["state"] == FAILS
    assert len(c["untouched_since_accepted"]["touching_commits"]) == 2
    assert res["overall"] == FAILS


def test_a_dirty_target_fails(repo, tmp_path):
    r, accepted, digest = repo
    write(r, TARGET, "uncommitted edit to the governed target\n")
    rp, mp = papers(tmp_path, accepted, digest)
    res = ev(r, rp, mp)
    assert res["target_continuity"]["checks"]["current_target_matches"]["state"] == FAILS
    assert res["overall"] == FAILS


def test_digest_movement_fails(repo, tmp_path):
    r, accepted, digest = repo
    write(r, TARGET, "moved on\n")
    commit(r, "move the target")
    rp, mp = papers(tmp_path, accepted, digest)
    assert ev(r, rp, mp)["overall"] == FAILS


# --- fail closed --------------------------------------------------------------------

def test_a_missing_accepted_commit_fails_closed(repo, tmp_path):
    r, accepted, digest = repo
    rp, mp = papers(tmp_path, accepted, digest, commit_="0" * 40)
    res = ev(r, rp, mp)
    assert res["target_continuity"]["checks"]["accepted_commit_ancestral"]["state"] == FAILS
    assert res["overall"] == FAILS


def test_a_non_ancestral_commit_fails_closed(repo, tmp_path):
    r, accepted, digest = repo
    run(r, "checkout", "-q", "-b", "side")
    write(r, "sidefile.txt", "side\n")
    side = commit(r, "side commit")
    run(r, "checkout", "-q", "-")
    rp, mp = papers(tmp_path, accepted, digest, commit_=side)
    assert ev(r, rp, mp)["target_continuity"]["checks"][
        "accepted_commit_ancestral"]["state"] == FAILS


def test_a_receipt_that_diverges_from_the_manifest_fails(repo, tmp_path):
    """Alternate or rewritten receipt paths cannot replace manifest-bound evidence."""
    r, accepted, digest = repo
    rp = tmp_path / "receipt.json"
    mp = tmp_path / "manifest.json"
    rp.write_text(json.dumps({"path": "governed/OTHER.txt", "commit": accepted, "digest": digest}))
    mp.write_text(json.dumps({"path": TARGET, "commit": accepted, "digest": digest}))
    res = ev(r, rp, mp)
    assert res["historical_receipt"]["state"] == FAILS
    assert res["overall"] == FAILS


# --- the four states stay separate ---------------------------------------------------

def test_the_installed_route_is_unavailable_not_assumed_to_pass(repo, tmp_path):
    r, accepted, digest = repo
    rp, mp = papers(tmp_path, accepted, digest)
    res = crc.evaluate(json.loads(rp.read_text()), json.loads(mp.read_text()), r, None, False)
    assert res["target_continuity"]["checks"]["installed_route"]["state"] == UNAVAILABLE
    assert res["overall"] == UNAVAILABLE
    assert crc.exit_code(res) == 2, "an unevaluated route must never exit 0"


def test_a_passing_installed_route_completes_continuity(repo, tmp_path):
    r, accepted, digest = repo
    rp, mp = papers(tmp_path, accepted, digest)
    res = crc.evaluate(json.loads(rp.read_text()), json.loads(mp.read_text()), r,
                       "python3 -c \"raise SystemExit(0)\"", False)
    assert res["overall"] == HOLDS
    assert crc.exit_code(res) == 0


def test_a_failing_installed_route_fails_continuity(repo, tmp_path):
    r, accepted, digest = repo
    rp, mp = papers(tmp_path, accepted, digest)
    res = crc.evaluate(json.loads(rp.read_text()), json.loads(mp.read_text()), r,
                       "python3 -c \"raise SystemExit(3)\"", False)
    assert res["overall"] == FAILS


def test_pending_remains_stricter_than_accepted_continuity(repo, tmp_path):
    """The whole point of separating the states: an unrelated commit leaves continuity intact
    and correctly breaks PENDING quiescence."""
    r, accepted, digest = repo
    write(r, "other.txt", "unrelated advance\n")
    commit(r, "advance HEAD")
    rp, mp = papers(tmp_path, accepted, digest)
    res = crc.evaluate(json.loads(rp.read_text()), json.loads(mp.read_text()), r,
                       "python3 -c \"raise SystemExit(0)\"", True)
    assert res["target_continuity"]["state"] == HOLDS
    assert res["pending_transaction"]["state"] == FAILS
    assert res["pending_transaction"]["exact_head"] is False


def test_received_state_output_separates_all_four(repo, tmp_path):
    r, accepted, digest = repo
    rp, mp = papers(tmp_path, accepted, digest)
    res = crc.evaluate(json.loads(rp.read_text()), json.loads(mp.read_text()), r, None, True)
    for key in ("historical_receipt", "target_continuity", "current_worktree",
                "pending_transaction"):
        assert key in res and res[key] is not None


# --- input hygiene --------------------------------------------------------------------

def test_a_receipt_missing_required_fields_is_an_input_error(tmp_path):
    p = tmp_path / "r.json"
    p.write_text(json.dumps({"path": "x"}))
    with pytest.raises(crc.InputError):
        crc.load(p, "receipt")


def test_an_unparseable_receipt_is_an_input_error(tmp_path):
    p = tmp_path / "r.json"
    p.write_text("{not json")
    with pytest.raises(crc.InputError):
        crc.load(p, "receipt")


def test_a_route_that_cannot_run_is_unavailable_not_a_pass(repo, tmp_path):
    """Found by mutation testing: the exception branch had no test, so turning it into a
    pass went undetected. An unrunnable verification is unknown, never satisfied."""
    r, accepted, digest = repo
    rp, mp = papers(tmp_path, accepted, digest)
    res = crc.evaluate(json.loads(rp.read_text()), json.loads(mp.read_text()), r,
                       "definitely-not-an-executable-anywhere --check", False)
    assert res["target_continuity"]["checks"]["installed_route"]["state"] == UNAVAILABLE
    assert res["overall"] != HOLDS
    assert crc.exit_code(res) != 0
