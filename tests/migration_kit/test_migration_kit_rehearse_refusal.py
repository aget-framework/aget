"""Gate 3 of the v3.36.0 kit design pass (v336-release:R28): R4 all-or-nothing in the rehearsal and launch tools, and
R1 at the act for the writes the rehearsals make in their copies.

Each test fails on 34353311 for the defect it names and passes after the change. Suites are stubbed (a command that
prints a pytest summary), the reference run is monkeypatched, and nothing outside tmp_path is touched.
"""
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import types
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "scripts/migration_kit"
# C2a7 (B185 finding 1, changed, labelled): the stub writes the kit report as the plugin does (it printed only a count)
STUB_SUITE = f"{sys.executable} {Path(__file__).parent / '_stub_suite.py'}"
OK_SUITE = {"exit": 0, "summary": "1 passed", "failures": [], "ran": True, "seconds": 0.0}


def load(name):
    spec = importlib.util.spec_from_file_location(name, BATCH / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def git_repo(loc, files):
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


MEMBER_FILES = {".aget/version.json": '{"aget_version": "3.34.0"}\n', "a.txt": "x\n", "docs/n.md": "n\n"}


def no_traceback(fn, *args):
    try:
        return fn(*args)
    except BaseException as e:   # noqa: BLE001
        pytest.fail(f"the tool ended in a traceback: {type(e).__name__}: {e}")


# --- B2, packet rehearsal (rehearse_batch2.py) -------------------------------------------------------------------

def b2_world(tmp_path, monkeypatch, receivers):
    """A packet and write list for `receivers` (name -> location), each with an empty op list (the apply writes
    nothing), the stub suite, and the reference run monkeypatched away."""
    RB = load("rehearse_batch2")
    A = load("apply_protected")
    monkeypatch.setattr(RB, "blind_spot_report", lambda r, s0, scratch: {"blind_spots": []})
    rs, entries = [], []
    for name, loc in receivers.items():
        head = subprocess.run(["git", "-C", str(loc), "rev-parse", "HEAD"], capture_output=True,
                              text=True).stdout.strip() or "(none)"
        rs.append({"aget": name, "location": str(loc), "head": head, "suite_cmd": STUB_SUITE, "items": []})
        entries.append({"aget": name, "location": str(loc), "head": head, "ops": []})
    pk, lst = tmp_path / "PACKET.json", tmp_path / "LIST.json"
    pk.write_text(json.dumps({"batch": "t", "receivers": rs}))
    lst.write_text(json.dumps({"batch": "t", "apply_script_sha256": A.self_sha(), "agets": entries}))
    return RB, pk, lst


def b2_run(RB, pk, lst, tmp_path):
    out = tmp_path / "V36.json"
    code = no_traceback(RB.main, ["--packet", str(pk), "--list", str(lst), "--scratch", str(tmp_path / "scr"),
                                  "--out", str(out)])
    return code, {x["aget"]: x for x in json.loads(out.read_text())["results"]}


def test_r4_t5_b2_one_refused_member_does_not_stop_the_others(tmp_path, monkeypatch):
    """R4-T5, J-7 code half (clause 3, C7). Two receivers, one a folder inside a shared repository (no .git of its
    own). Expected: exit 1, the result file names both, that one REFUSED, the other rehearsed. At 34353311 copy_of
    raises ValueError inside the unguarded pool.map: a traceback, and the result stays NOT_FINISHED."""
    good = tmp_path / "home" / "good"
    git_repo(good, MEMBER_FILES)
    shared = tmp_path / "home" / "shared"
    git_repo(shared, {"inner/" + k: v for k, v in MEMBER_FILES.items()})
    RB, pk, lst = b2_world(tmp_path, monkeypatch, {"inner": shared / "inner", "good": good})
    code, got = b2_run(RB, pk, lst, tmp_path)
    assert code == 1
    assert got["inner"]["verdict"].startswith("REFUSED") and "no .git of its own" in got["inner"]["verdict"]
    assert got["good"]["verdict"] == "PASS"


@pytest.mark.parametrize("kind", ["link", "folder"])
def test_r4_t6_b2_a_carrier_that_cannot_be_written_refuses_before_the_apply(tmp_path, monkeypatch, kind):
    """R4-T6 (C2, C7). An extra carrier that is a symbolic link (or a folder) in the copy. Expected: REFUSED, and no
    APPLY_RECEIPT in the evidence folder, because the apply never ran. At 34353311 the apply runs and then (link)
    safe_in_copy raises inside the pool: a traceback; or (folder) the carrier is skipped silently and the copy PASSes."""
    good = tmp_path / "home" / "good"
    outside = tmp_path / "outside.yaml"
    outside.write_text("canonical_version: 3.34.0\n")
    files = dict(MEMBER_FILES)
    g = git_repo(good, files)
    if kind == "link":
        (good / "carrier.yaml").symlink_to(outside)
    else:
        (good / "carrier.yaml").mkdir()
        (good / "carrier.yaml" / "keep").write_text("k\n")
    g("add", "-A")
    g("commit", "-q", "-m", "carrier")
    RB, pk, lst = b2_world(tmp_path, monkeypatch, {"good": good})
    doc = json.loads(pk.read_text())
    doc["receivers"][0]["extra_carriers"] = ["carrier.yaml"]
    pk.write_text(json.dumps(doc))
    code, got = b2_run(RB, pk, lst, tmp_path)
    assert code == 1 and got["good"]["verdict"].startswith("REFUSED")
    assert not list((tmp_path / "scr" / "evidence").rglob("APPLY_RECEIPT_*.json"))
    assert outside.read_text() == "canonical_version: 3.34.0\n"


def test_r4_t10_b2_a_failed_copy_commit_refuses(tmp_path, monkeypatch):
    """R4-T10 rehearsal half (S-089, S-091). `.git/index.lock` is present after the apply, so the copy's `git add`
    and `git commit` fail. Expected: `REFUSED: copy commit failed`, no S2, the result file written. At 34353311 the
    failed git commands are ignored and S2 runs."""
    good = tmp_path / "home" / "good"
    git_repo(good, MEMBER_FILES)
    RB, pk, lst = b2_world(tmp_path, monkeypatch, {"good": good})
    real = RB.apply_on_copy

    def apply_then_lock(entry, copy, ev):
        result = real(entry, copy, ev)
        (copy / ".git" / "index.lock").write_text("")
        return result
    monkeypatch.setattr(RB, "apply_on_copy", apply_then_lock)
    code, got = b2_run(RB, pk, lst, tmp_path)
    assert code == 1 and got["good"]["verdict"].startswith("REFUSED: copy commit failed")
    assert "S2" not in got["good"]


def _frames():
    f = sys._getframe(1)
    while f is not None:
        yield f
        f = f.f_back


def test_d6_b2_a_carrier_folder_swapped_after_its_check_is_never_written_through(tmp_path):
    """R1-T17 at the rehearsal's own copy writes (S-083..S-088), closing design-read-2 D-6 there. The check sees the
    real `.aget` folder; the write sees it swapped for a link to an outside folder. Expected: no outside byte changes
    (the write is refused). At 34353311 bump_carriers checks, then write_text follows the swapped link."""
    RB = load("rehearse_batch2")
    copy = tmp_path / "copy"
    (copy / ".aget").mkdir(parents=True)
    (copy / ".aget" / "version.json").write_text('{"aget_version": "3.34.0"}\n')
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "version.json").write_text('{"aget_version": "3.34.0"}\n')
    real = RB.safe_in_copy

    def check_then_swap(c, rel):
        p = real(c, rel)
        if rel == ".aget/version.json" and not (copy / ".aget").is_symlink():
            (copy / ".aget").rename(copy / ".aget.real")
            (copy / ".aget").symlink_to(outside)
        return p
    RB.safe_in_copy = check_then_swap
    try:
        RB.bump_carriers(copy, {}, today="2026-10-02")
    except ValueError:
        pass
    assert (outside / "version.json").read_text() == '{"aget_version": "3.34.0"}\n'
    assert sorted(p.name for p in outside.iterdir()) == ["version.json"]


# --- B2 repair rehearsal (rehearse_repair.py) ---------------------------------------------------------------------

def repair_world(tmp_path):
    """A member with two commits (pre-head and head), a staged release file, and a receiver record for it."""
    member = tmp_path / "home" / "rep"
    g = git_repo(member, {**MEMBER_FILES, "scripts/x.py": "old\n", "data/pins.json": "{}\n"})
    pre = g("rev-parse", "HEAD")
    (member / "scripts" / "x.py").write_text("migrated\n")
    g("commit", "-q", "-am", "migration")
    head = g("rev-parse", "HEAD")
    staged = tmp_path / "stage" / "x.py"
    staged.parent.mkdir()
    staged.write_text("release\n")
    r = {"aget": "rep", "location": str(member), "head": head,
         "items": [{"path": "scripts/x.py", "op": "write", "staged": str(staged),
                    "sha256": hashlib.sha256(b"release\n").hexdigest()}]}
    return member, r, pre, head


def test_r4_t7_repair_rehearsal_tests_amendment_paths_before_any_write(tmp_path, monkeypatch):
    """R4-T7 (a) (C2, C7). An amendment path that is a link, plus a todo write. Expected: REFUSED, and the todo target
    in the copy still holds the head's bytes. At 34353311 the todo is written first, then the amendment is refused
    (INCONCLUSIVE) with the copy already changed. The link leads to a file inside the member (stage E2b: a link
    leading outside the run now refuses the whole copy first, by LINKS, which would not test this ordering)."""
    RR = load("rehearse_repair")
    monkeypatch.setattr(RR, "suite", lambda *a, **k: dict(OK_SUITE))
    member, r, pre, head = repair_world(tmp_path)
    outside = member / "data" / "real.json"
    outside.write_text("{}\n")
    (member / "data" / "pins.json").unlink()
    (member / "data" / "pins.json").symlink_to("real.json")
    subprocess.run(["git", "-C", str(member), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(member), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m",
                    "link"], check=True)
    r["head"] = subprocess.run(["git", "-C", str(member), "rev-parse", "HEAD"], capture_output=True,
                               text=True).stdout.strip()
    r["amendments"] = [{"path": "data/pins.json", "row": "x", "artifact": "scripts/x.py", "sha256": "0" * 64,
                        "note": "n"}]
    res = no_traceback(RR.rehearse, r, pre, tmp_path / "scr", tmp_path / "ev")
    assert res["verdict"].startswith("REFUSED")
    assert (tmp_path / "scr" / "rep" / "scripts" / "x.py").read_text() == "migrated\n"
    assert outside.read_text() == "{}\n"


def test_r4_t7b_repair_rehearsal_refuses_a_checkout_that_does_not_reach_its_commit(tmp_path, monkeypatch):
    """R4-T7 (b), S-195. An unknown pre_head. Expected: REFUSED naming the checkout. At 34353311 the failed checkout is
    ignored and S0 runs at the wrong revision."""
    RR = load("rehearse_repair")
    monkeypatch.setattr(RR, "suite", lambda *a, **k: dict(OK_SUITE))
    member, r, pre, head = repair_world(tmp_path)
    res = no_traceback(RR.rehearse, r, "f" * 40, tmp_path / "scr", tmp_path / "ev")
    assert res["verdict"].startswith("REFUSED") and "checkout" in res["verdict"] and "S0" not in res


def test_d6_repair_placement_swapped_after_its_check_is_never_written_through(tmp_path, monkeypatch):
    """R1-T17 at rehearse_repair's placement (S-010, S-106; rehearse_repair.py:155 `shutil.copyfile`), closing
    design-read-2 D-6 there. Every check sees the real `scripts` folder; the placement sees it swapped for a link to
    an outside folder. Expected: no outside byte changes. At 34353311 copyfile follows the swapped link."""
    RR = load("rehearse_repair")
    monkeypatch.setattr(RR, "suite", lambda *a, **k: dict(OK_SUITE))
    member, r, pre, head = repair_world(tmp_path)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "x.py").write_text("outside\n")
    copy = tmp_path / "scr" / "rep"
    real = RR.CI.destination_refusal

    def swap_after_check(root, rel, *a, **k):
        parent, hidden = copy / "scripts", copy / "scripts.real"
        if parent.is_symlink():
            parent.unlink()
            hidden.rename(parent)
        why = real(root, rel, *a, **k)
        if rel == "scripts/x.py" and not why:
            parent.rename(hidden)
            parent.symlink_to(outside)
        return why
    monkeypatch.setattr(RR.CI, "destination_refusal", swap_after_check)
    try:
        RR.rehearse(r, pre, tmp_path / "scr", tmp_path / "ev")
    except Exception:   # noqa: BLE001 — after the change the act is refused; the assertion is on the outside bytes
        pass
    assert (outside / "x.py").read_text() == "outside\n"


def test_r4_t14b_repair_rehearsal_one_members_failure_does_not_stop_the_others(tmp_path, monkeypatch):
    """R4-T14 (b). Two receivers; the copy of the first raises OSError. Expected: the second finishes, the result names
    both, exit 1, no traceback. At 34353311 the OSError escapes the pool: a traceback, no result for either."""
    RR = load("rehearse_repair")
    monkeypatch.setattr(RR, "suite", lambda *a, **k: dict(OK_SUITE))
    m1, r1, pre1, _ = repair_world(tmp_path / "one")
    m2, r2, pre2, _ = repair_world(tmp_path / "two")
    r1["aget"], r2["aget"] = "one", "two"
    real = RR.shutil.copytree

    def copytree(src, dst, *a, **k):
        if Path(src) == m1:
            raise OSError("copy failed")
        return real(src, dst, *a, **k)
    monkeypatch.setattr(RR.shutil, "copytree", copytree)
    pk, prev, out = tmp_path / "P.json", tmp_path / "PREV.json", tmp_path / "OUT.json"
    pk.write_text(json.dumps({"receivers": [r1, r2]}))
    prev.write_text(json.dumps({"receivers": [{"aget": "one", "head": pre1}, {"aget": "two", "head": pre2}]}))
    code = no_traceback(RR.main, ["--packet", str(pk), "--previous-packet", str(prev), "--scratch",
                                  str(tmp_path / "scr"), "--out", str(out)])
    got = {x["aget"]: x["verdict"] for x in json.loads(out.read_text())["results"]}
    assert code == 1 and got["one"].startswith("REFUSED") and "copy failed" in got["one"]
    assert "two" in got and not got["two"].startswith("REFUSED")


# --- B3, session rehearsal (rehearse_v37.py) ----------------------------------------------------------------------

def v37_inputs(tmp_path, names, listed):
    member = tmp_path / "home" / "m-aget"
    g = git_repo(member, MEMBER_FILES)
    pk, lst = tmp_path / "PACKET.json", tmp_path / "LIST.json"
    pk.write_text(json.dumps({"batch": "99", "stage": str(tmp_path / "stage"), "receivers": [
        {"aget": n, "location": str(member), "head": g("rev-parse", "HEAD")} for n in names]}))
    lst.write_text(json.dumps({"agets": [{"aget": n} for n in listed]}))
    return member, pk, lst


def test_r4_t8_b3_a_name_missing_from_the_list_is_refused_before_any_copy(tmp_path, monkeypatch):
    """R4-T8 (C1 for that name). A name absent from the write list, every launch stubbed to exit 0. Expected: the
    result names it REFUSED, <scratch>/<name> is never created, exit 1. At 34353311 the copy is made first, then
    `next(...)` at rehearse_v37.py:124 raises StopIteration: a traceback."""
    RV = load("rehearse_v37")
    monkeypatch.setattr(RV, "run", lambda *cmd: 0)
    member, pk, lst = v37_inputs(tmp_path, ["m-aget"], [])
    out = tmp_path / "V37.json"
    code = no_traceback(RV.main, ["--batch", "99", "--scratch", str(tmp_path / "scr"), "--packet", str(pk), "--list",
                                  str(lst), "--out", str(out), "m-aget"])
    doc = json.loads(out.read_text())
    assert code == 1 and doc["members"]["m-aget"]["verdict"].startswith("REFUSED")
    assert not (tmp_path / "scr" / "m-aget").exists()


def test_r4_t14c_b3_one_names_failure_does_not_stop_the_next(tmp_path, monkeypatch):
    """R4-T14 (c). `rehearse` raises for the first name. Expected: the second name is rehearsed, the result names both,
    exit 1, no traceback. At 34353311 the exception escapes the main loop."""
    RV = load("rehearse_v37")
    member, pk, lst = v37_inputs(tmp_path, ["a-aget", "b-aget"], ["a-aget", "b-aget"])

    def rehearse(name, *a, **k):
        if name == "a-aget":
            raise RuntimeError("copy could not be made")
        return "PASS"
    monkeypatch.setattr(RV, "rehearse", rehearse)
    out = tmp_path / "V37.json"
    code = no_traceback(RV.main, ["--batch", "99", "--scratch", str(tmp_path / "scr"), "--packet", str(pk), "--list",
                                  str(lst), "--out", str(out), "a-aget", "b-aget"])
    members = json.loads(out.read_text())["members"]
    assert code == 1 and members["a-aget"]["verdict"].startswith("REFUSED") and members["b-aget"]["verdict"] == "PASS"


# --- B6/B8, launch (launch_batch.py) ------------------------------------------------------------------------------

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


def launch_world(tmp_path, monkeypatch, names):
    """Members and a packet for a live launch, with `claude --version` answered, the typed-authority check passed,
    and every real session forbidden (run_grouped raises)."""
    LB = load("launch_batch")
    monkeypatch.setattr(LB, "launch_rules_refusal", lambda r, packet: None)   # D2 (labelled): minimal receivers, no items; the rules recompute has its own row
    settings = tmp_path / "settings.json"
    settings.write_text("{}\n")
    rs = []
    for n in names:
        loc = tmp_path / "home" / n
        g = git_repo(loc, MEMBER_FILES)
        rs.append({"aget": n, "location": str(loc), "head": g("rev-parse", "HEAD"), "prompt": "p",
                   "baseline_prompt": "b", "attempt": "1", "allowlist": [], "write_set": ["a.txt", "sessions/*"],
                   "allow_bash": [], "items": [{"path": "a.txt", "op": "write", "pre": "x", "placed_by": "apply"}],
                   "settings": {"path": str(settings), "sha256": hashlib.sha256(settings.read_bytes()).hexdigest()}})
    pk = tmp_path / "PACKET.json"
    pk.write_text(json.dumps({"batch": "99", "claude_version": "stub 1.0", **sealed_packet_root(tmp_path, names),
                              "tools": "Bash", "deny": [], "apply_receipt": str(tmp_path / "R.json"),
                              "baseline_cmd": "python3 -m pytest -q", "receivers": rs}))
    real = subprocess.run

    def fake(cmd, *a, **k):
        if [str(c) for c in cmd[:2]] == ["claude", "--version"]:
            return subprocess.CompletedProcess(cmd, 0, "stub 1.0\n", "")
        return real(cmd, *a, **k)
    monkeypatch.setattr(subprocess, "run", fake)
    monkeypatch.setitem(sys.modules, "batch_authority",
                        types.SimpleNamespace(check=lambda batch, act=None: (True, "test authority")))

    def no_session(*a, **k):
        raise AssertionError("a session was started")
    monkeypatch.setattr(LB, "run_grouped", no_session)
    return LB, pk


def test_r4_t9_a_write_path_linked_after_preparation_stops_the_launch_before_any_session(tmp_path, monkeypatch):
    """R4-T9 (C1, R1-S (ii)). The packet's write item path is a symbolic link by launch time. Expected: exit 2 and no
    session started. At 34353311 nothing tests the path at launch and the session starts (here: run_grouped is
    reached)."""
    LB, pk = launch_world(tmp_path, monkeypatch, ["m-aget"])
    loc = tmp_path / "home" / "m-aget"
    outside = tmp_path / "outside.txt"
    outside.write_text("x\n")
    (loc / "a.txt").unlink()
    (loc / "a.txt").symlink_to(outside)
    monkeypatch.setattr(LB, "take_snapshot", lambda r, ev: None, raising=False)
    assert no_traceback(LB.main, ["--packet", str(pk), "--launch", "--evidence", str(tmp_path / "ev")]) == 2


def test_r4_t9b_a_failed_snapshot_stops_the_launch_without_a_traceback(tmp_path, monkeypatch):
    """R4-T9 second case. The settings snapshot fails. Expected: exit 2, no session, no traceback. At 34353311 the
    snapshot runs inside run_one with check=True, inside the pool: a CalledProcessError traceback."""
    LB, pk = launch_world(tmp_path, monkeypatch, ["m-aget"])
    failing = tmp_path / "fail_check.py"
    failing.write_text("import sys; sys.exit(1)\n")
    monkeypatch.setattr(LB, "CHECK", failing)
    assert no_traceback(LB.main, ["--packet", str(pk), "--launch", "--evidence", str(tmp_path / "ev")]) == 2


def test_r4_t14d_launch_one_receivers_exception_does_not_stop_the_others(tmp_path, monkeypatch, capsys):
    """R4-T14 (d). run_one raises for the first receiver. Expected: the second receiver's record is made, exit 1, no
    traceback. At 34353311 the exception escapes pool.map."""
    LB, pk = launch_world(tmp_path, monkeypatch, ["a-aget", "b-aget"])
    monkeypatch.setattr(LB, "take_snapshot", lambda r, ev: None, raising=False)

    def run_one(r, packet, ev, state=None):
        if r["aget"] == "a-aget":
            raise RuntimeError("watcher could not start")
        return {"aget": r["aget"], "exit": 0, "elapsed_s": 1, "head_before": r["head"], "head_after": r["head"],
                "check_exit": 0}
    monkeypatch.setattr(LB, "run_one", run_one)
    assert no_traceback(LB.main, ["--packet", str(pk), "--launch", "--evidence", str(tmp_path / "ev")]) == 1
    out = capsys.readouterr().out
    assert "a-aget" in out and "watcher could not start" in out and "b-aget" in out and "check PASS" in out


def test_r4_t14e_baseline_one_receivers_exception_does_not_stop_the_others(tmp_path, monkeypatch, capsys):
    """R4-T14 (e). run_baseline raises for the first receiver. Expected: the second is RECORDED, exit 1, no
    traceback. At 34353311 the exception escapes pool.map."""
    LB, pk = launch_world(tmp_path, monkeypatch, ["a-aget", "b-aget"])

    def run_baseline(r, packet, ev, stage, state=None):
        if r["aget"] == "a-aget":
            raise RuntimeError("baseline session failed")
        return {"aget": r["aget"], "verdict": "RECORDED", "summary": "1 passed", "failures": []}
    monkeypatch.setattr(LB, "run_baseline", run_baseline)
    assert no_traceback(LB.main, ["--packet", str(pk), "--launch", "--baseline", "--evidence",
                                  str(tmp_path / "ev")]) == 1
    out = capsys.readouterr().out
    assert "baseline session failed" in out and "b-aget" in out and "RECORDED" in out


# --- REVW2's B143 read of stage B2: falsifiers carried in (control: the stage-B2 tree) -----------------------------

@pytest.mark.parametrize("kind", ["symbolic", "hard"])
def test_b143_2_the_custody_marker_is_never_written_through_a_link(tmp_path, monkeypatch, kind):
    """B143 finding 2 (HIGH). After the copy's git identity is checked, the marker path becomes a link to an outside
    file. Expected: the outside file unchanged. Stage B2 wrote the custody JSON into it."""
    RV = load("rehearse_v37")
    member, pk, lst = v37_inputs(tmp_path, ["m-aget"], ["m-aget"])
    packet = json.loads(pk.read_text())
    packet["receivers"][0]["mode"] = "track-skills"
    copy = tmp_path / "scratch" / "m-aget"
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"safe")
    marker = copy / ".git" / RV.COPY_MARKER
    real = RV.LB.git_identity_refusal

    def check_then_link(folder, *a, **k):
        why = real(folder, *a, **k)
        if kind == "symbolic":
            marker.symlink_to(outside)
        else:
            os.link(outside, marker)
        return why
    monkeypatch.setattr(RV.LB, "git_identity_refusal", check_then_link)
    monkeypatch.setattr(RV, "run", lambda *cmd: 1)
    no_traceback(RV.rehearse, "m-aget", pk, packet, json.loads(lst.read_text()), tmp_path / "scratch")
    assert outside.read_bytes() == b"safe"


@pytest.mark.parametrize("shape", ["missing", "malformed", "bad_receiver"])
def test_b143_5_launch_packet_input_is_c1(tmp_path, shape):
    """B143 finding 5 (MEDIUM), launch half. A missing, malformed or ill-shaped packet: exit 2, no traceback. Stage B2:
    FileNotFoundError, JSONDecodeError, or a TypeError from the receiver loop."""
    LB = load("launch_batch")
    pk = tmp_path / "packet.json"
    if shape == "malformed":
        pk.write_text("{bad json")
    elif shape == "bad_receiver":
        pk.write_text(json.dumps({"batch": "x", "claude_version": "v", "receivers": [42]}))
    assert no_traceback(LB.main, ["--packet", str(pk), "--evidence", str(tmp_path / "ev")]) == 2


def test_b143_5_b2_malformed_receiver_is_c1_before_any_copy(tmp_path):
    """B143 finding 5 (MEDIUM), packet-rehearsal half. `receivers: [42]`: exit 2 and a REFUSED result, no copy.
    Stage B2: a TypeError and NOT_FINISHED left."""
    RB = load("rehearse_batch2")
    pk, wl, out, scr = tmp_path / "p.json", tmp_path / "l.json", tmp_path / "o.json", tmp_path / "scr"
    pk.write_text(json.dumps({"batch": "x", "receivers": [42]}))
    wl.write_text(json.dumps({"agets": []}))
    assert no_traceback(RB.main, ["--packet", str(pk), "--list", str(wl), "--scratch", str(scr), "--out",
                                  str(out)]) == 2
    assert json.loads(out.read_text())["verdict"] == "REFUSED" and not (scr / "evidence").exists()


@pytest.mark.parametrize("started", [False, True])
def test_b143_6_a_failed_launch_replaces_the_members_prior_launch_record(tmp_path, monkeypatch, started):
    """B143 finding 6 (HIGH), launch half. A prior launch record for the member, then run_one fails (before or after
    its session started). Expected: the record on disk is the failure, not the prior one. Stage B2: the failure was
    only printed and the old record survived byte for byte."""
    LB, pk = launch_world(tmp_path, monkeypatch, ["a-aget", "b-aget"])
    ev = tmp_path / "ev"
    (ev / "a-aget").mkdir(parents=True)
    dest = ev / "a-aget" / "launch_record.json"
    prior = {"aget": "a-aget", "session_id": "old", "check_exit": 0}
    dest.write_text(json.dumps(prior))
    monkeypatch.setattr(LB, "take_snapshot", lambda r, e: None, raising=False)

    def run_one(r, packet, e, state=None):
        if r["aget"] == "a-aget":
            state["session_started"] = started
            raise RuntimeError("receiver failure")
        return {"aget": r["aget"], "exit": 0, "elapsed_s": 0, "head_before": r["head"], "head_after": r["head"],
                "check_exit": 0}
    monkeypatch.setattr(LB, "run_one", run_one)
    assert no_traceback(LB.main, ["--packet", str(pk), "--launch", "--evidence", str(ev)]) == 1
    now = json.loads(dest.read_text())
    assert now != prior and (now.get("error") or now.get("result") == "REFUSED")


def test_b143_6_a_failed_baseline_replaces_its_prior_record_and_gives_no_exemptions(tmp_path, monkeypatch):
    """B143 finding 6 (HIGH), baseline half. A prior RECORDED baseline listing a failure, then the baseline fails.
    Expected: the record on disk is the failure, and after-run check F, reading it, is inconclusive instead of
    subtracting the old failure. Stage B2: the old RECORDED survived and F subtracted the failure."""
    LB, pk = launch_world(tmp_path, monkeypatch, ["a-aget", "b-aget"])
    ev = tmp_path / "ev"
    (ev / "a-aget").mkdir(parents=True)
    dest = ev / "a-aget" / "baseline_record.json"
    prior = {"aget": "a-aget", "verdict": "RECORDED", "session_id": "old", "failures": ["tests/x.py::test_x"]}
    dest.write_text(json.dumps(prior))

    def run_baseline(r, *a, state=None):
        if r["aget"] == "a-aget":
            raise RuntimeError("baseline failure")
        return {"aget": r["aget"], "verdict": "RECORDED", "summary": "1 passed", "failures": []}
    monkeypatch.setattr(LB, "run_baseline", run_baseline)
    assert no_traceback(LB.main, ["--packet", str(pk), "--launch", "--baseline", "--evidence", str(ev)]) == 1
    assert json.loads(dest.read_text()) != prior
    t = tmp_path / "t.jsonl"
    t.write_text("\n".join(json.dumps(e) for e in [
        {"sessionId": "S", "message": {"content": [{"type": "tool_use", "name": "Bash", "id": "t",
                                  "input": {"command": "python3 -m pytest -q"}}]}},
        {"sessionId": "S", "message": {"content": [{"type": "tool_result", "tool_use_id": "t",
                                  "content": "FAILED tests/x.py::test_x\n1 failed in 0.01s\n"}]}}]) + "\n")
    new, why = load("after_run_check").suite_regressions(t, "python3 -m pytest -q", dest, "a-aget", "h")
    assert new == [] and why


def test_b143_7_the_session_rehearsal_uses_the_receipt_its_apply_wrote(tmp_path, monkeypatch):
    """B143 finding 7 (HIGH). A prior APPLY_RECEIPT_ZZZ… sorts after the one this apply writes. Expected: the launch
    is given the new one. Stage B2 picked the prior one by sort order."""
    RV = load("rehearse_v37")
    member, pk, lst = v37_inputs(tmp_path, ["m-aget"], ["m-aget"])
    packet = json.loads(pk.read_text())
    packet["receivers"][0]["mode"] = "track-skills"
    ev = tmp_path / "scratch" / "evidence" / "m-aget"
    ev.mkdir(parents=True)
    (ev / "APPLY_RECEIPT_ZZZ_prior.json").write_text('{"agets": []}')
    current, seen = ev / "APPLY_RECEIPT_20261003_current.json", {}

    def run(*cmd):
        words = [str(c) for c in cmd]
        if words[1].endswith("apply_protected.py"):
            current.write_text('{"agets": []}')
            return 0
        seen["receipt"] = words[words.index("--apply-receipt") + 1]
        (ev / "after_run_check.json").write_text('{"verdict": "PASS"}')
        return 0
    monkeypatch.setattr(RV, "run", run)
    no_traceback(RV.rehearse, "m-aget", pk, packet, json.loads(lst.read_text()), tmp_path / "scratch")
    assert seen.get("receipt") == str(current)


def test_d3_s343_an_unknown_receiver_mode_is_refused_not_rehearsed_as_migrate(tmp_path, monkeypatch):
    """Design read 2, D-3 (S-343, rehearse_batch2.py:243). A packet receiver with mode 'bogus' must not be rehearsed
    as a migration. At 34353311 any mode other than track-skills takes the migration branch, and the copy PASSes."""
    good = tmp_path / "home" / "good"
    git_repo(good, MEMBER_FILES)
    RB, pk, lst = b2_world(tmp_path, monkeypatch, {"good": good})
    doc = json.loads(pk.read_text())
    doc["receivers"][0]["mode"] = "bogus"
    pk.write_text(json.dumps(doc))
    code, got = b2_run(RB, pk, lst, tmp_path)
    assert code == 1 and got["good"]["verdict"].startswith("REFUSED") and "bogus" in got["good"]["verdict"]


# --- REVW2's B145 read of stage B3: nested input shapes (reviewer_followup_probes.py, carried in) ------------------

@pytest.mark.parametrize("shape", ["settings_path", "settings_digest", "item_shape", "write_set_shape"])
def test_b145_nested_launch_packet_shapes_are_c1(tmp_path, monkeypatch, shape):
    """B145 finding 1 (MEDIUM), launch half. `settings` without `path` or `sha256`, an item that is not an object, or
    a write set that is not a list of strings: exit 2 before any act, no traceback, the member unchanged. Stage B3:
    KeyError or AttributeError in the pre-session sweep."""
    LB, pk = launch_world(tmp_path, monkeypatch, ["a-aget"])
    doc = json.loads(pk.read_text())
    r = doc["receivers"][0]
    if shape == "settings_path":
        r["settings"].pop("path")
    elif shape == "settings_digest":
        r["settings"].pop("sha256")
    elif shape == "item_shape":
        r["items"] = [42]
    else:
        r["write_set"] = "a.txt"
    pk.write_text(json.dumps(doc))
    before = (Path(r["location"]) / "a.txt").read_bytes()
    assert no_traceback(LB.main, ["--packet", str(pk)]) == 2
    assert (Path(r["location"]) / "a.txt").read_bytes() == before


@pytest.mark.parametrize("field,value", [("sibling_reads", 42), ("items", [42]), ("renames", [{"path": 1}]),
                                         ("location", None)])
def test_b145_nested_receiver_shapes_are_c1_in_the_packet_rehearsal(tmp_path, monkeypatch, field, value):
    """B145 finding 1 (MEDIUM), packet-rehearsal half. A receiver whose nested fields are the wrong shape: exit 2 and
    a REFUSED result, with no receiver work started. Stage B3: a TypeError outside the C1 try, NOT_FINISHED left."""
    RB = load("rehearse_batch2")
    monkeypatch.setattr(RB, "rehearse", lambda *a, **k: pytest.fail("receiver work started"))
    r = {"aget": "a-aget", "location": str(tmp_path / "m"), "head": "h", field: value}
    pk, wl, out = tmp_path / "packet.json", tmp_path / "list.json", tmp_path / "result.json"
    pk.write_text(json.dumps({"batch": "99", "receivers": [r]}))
    wl.write_text('{"agets": []}')
    assert no_traceback(RB.main, ["--packet", str(pk), "--list", str(wl), "--out", str(out), "--scratch",
                                  str(tmp_path / "scratch")]) == 2
    assert json.loads(out.read_text())["verdict"] == "REFUSED"


def test_r1_t2a_repair_rehearsal_asks_links_again_after_each_checkout(tmp_path, monkeypatch):
    """R1-T2 (a) at the repair rehearsal's checkouts (LINKS after a checkout, R1 clause 4). The member's head has no
    link, so the copy passes isolation; its pre-migration commit tracks `ext -> <outside folder>`, which the
    rehearsal's checkout of that commit creates. Expected: a non-success verdict naming the link, before any suite
    runs in it. At 34353311 the checkout makes the link and the suites run with it in place."""
    RR = load("rehearse_repair")
    ran = []
    monkeypatch.setattr(RR, "suite", lambda *a, **k: ran.append(a[1]) or dict(OK_SUITE))
    outside = tmp_path / "outside"
    outside.mkdir()
    member = tmp_path / "home" / "rep"
    g = git_repo(member, {**MEMBER_FILES, "scripts/x.py": "old\n"})
    (member / "ext").symlink_to(outside)
    g("add", "-A")
    g("commit", "-q", "-m", "pre with an outside link")
    pre = g("rev-parse", "HEAD")
    (member / "ext").unlink()
    (member / "scripts" / "x.py").write_text("migrated\n")
    g("add", "-A")
    g("commit", "-q", "-m", "migration")
    staged = tmp_path / "stage" / "x.py"
    staged.parent.mkdir()
    staged.write_text("release\n")
    r = {"aget": "rep", "location": str(member), "head": g("rev-parse", "HEAD"),
         "items": [{"path": "scripts/x.py", "op": "write", "staged": str(staged),
                    "sha256": hashlib.sha256(b"release\n").hexdigest()}]}
    res = no_traceback(RR.rehearse, r, pre, tmp_path / "scr", tmp_path / "ev")
    assert ran == [], f"suites ran in the copy with the outside link checked out: {ran}"
    assert not res["verdict"].startswith("PASS") and "leads outside" in res["verdict"], res["verdict"]
    assert list(outside.iterdir()) == []


def test_b148_2_the_repair_rehearsal_does_not_pass_an_unknown_item(tmp_path, monkeypatch):
    """B148 finding 2 (REVW3's falsifier, the consequential consumer). A repair item with op `bogus`, deterministic
    suites (S1 shows the regression, S2 none): the rehearsal is REFUSED before any copy. On stage F2 the todo and
    digest filters skipped the item by bare op and the rehearsal read PASS with it never judged."""
    RR = load("rehearse_repair")
    member, r, pre, head = repair_world(tmp_path)
    r["items"][0]["op"] = "bogus"
    monkeypatch.setattr(RR, "suite", lambda copy, label, ev, *a: {
        "ran": True, "exit": 0, "summary": "1 passed", "failures": ["regression"] if label == "S1_unrepaired" else []})
    res = no_traceback(RR.rehearse, r, pre, tmp_path / "scr", tmp_path / "ev")
    assert res["verdict"].startswith("REFUSED") and "CLASSIFICATION" in res["verdict"], res["verdict"]
    assert not (tmp_path / "scr" / "rep").exists()


@pytest.mark.parametrize("shape", ["packet_root_int", "manifest_digest_list", "allowlist_missing", "prompt_int",
                                   "tools_missing"])
def test_b148_3_every_launch_field_is_checked_at_c1(tmp_path, monkeypatch, shape):
    """B148 finding 3 (REVW3's falsifier). A packet field the launch reads, with the wrong type or missing, stops the
    run at C1 (exit 2, no traceback). On stage F2: `packet_root: 42` passed validation and raised TypeError at the
    stage check; a missing receiver allowlist or top-level `tools` raised KeyError in the dry run; a non-string prompt
    was accepted. `manifest_digest_list` is REVW3's positive control (already refused)."""
    LB, pk = launch_world(tmp_path, monkeypatch, ["a-aget"])
    d = json.loads(pk.read_text())
    if shape == "packet_root_int":
        d["packet_root"] = 42
    elif shape == "manifest_digest_list":
        d["stage_manifest"]["kit/place_file.py"] = []
    elif shape == "allowlist_missing":
        d["receivers"][0].pop("allowlist")
    elif shape == "prompt_int":
        d["receivers"][0]["prompt"] = 42
    else:
        d.pop("tools")
    pk.write_text(json.dumps(d))
    assert no_traceback(LB.main, ["--packet", str(pk)]) == 2


def test_b148_2_the_packet_rehearsal_refuses_an_unknown_item_before_any_copy(tmp_path, monkeypatch):
    """B148 finding 2's class, found by the builder at the packet rehearsal: an item with op `bogus` is that
    receiver's REFUSED result before its copy is made or any suite or apply runs. On stage E2b the rehearsal read the
    table only after its apply (`merges_left_to_receiver`), with the copy made and the suite and apply already run."""
    RB = load("rehearse_batch2")
    ran = []
    monkeypatch.setattr(RB.RR, "suite", lambda *a, **k: ran.append("suite") or dict(OK_SUITE))
    monkeypatch.setattr(RB, "apply_on_copy", lambda *a, **k: ran.append("apply") or (0, ""))
    member = tmp_path / "home" / "m"
    g = git_repo(member, MEMBER_FILES)
    r = {"aget": "m", "location": str(member), "head": g("rev-parse", "HEAD"),
         "items": [{"path": "q.py", "op": "bogus", "staged": "/unused", "pre": "absent"}]}
    res = RB.rehearse_or_refuse(r, {"aget": "m", "ops": []}, tmp_path / "scr", tmp_path / "ev")
    assert ran == [] and not (tmp_path / "scr" / "m").exists(), (ran, res)
    assert res["verdict"].startswith("REFUSED") and "CLASSIFICATION" in res["verdict"], res["verdict"]


# --- REVW4's B151 read of stage E2c ------------------------------------------------------------------------------

@pytest.mark.parametrize("shape", ["batch_missing", "batch_list", "kind_list"])
def test_b151_6_route_specific_packet_fields_are_c1(tmp_path, monkeypatch, shape):
    """B151 finding 6 (REVW4's falsifier). A live launch with no `batch`, or an item whose `kind` is a list, is a
    named exit-2 refusal with no escaping exception. On stage E2c the first raised KeyError before the authority check
    (`packet["batch"]`) and the second TypeError at the meaning table (an unhashable key). `batch_list` is REVW4's
    positive control (refused by the full check on E2c too)."""
    LB, pk = launch_world(tmp_path, monkeypatch, ["a-aget"])
    d = json.loads(pk.read_text())
    args = ["--packet", str(pk)]
    if shape == "batch_missing":
        d.pop("batch")
        args += ["--launch"]
    elif shape == "batch_list":
        d["batch"] = []
        args += ["--launch"]
    else:
        d["receivers"][0]["items"] = [{"path": "x.py", "op": "hold", "kind": []}]
    pk.write_text(json.dumps(d))
    assert LB.main(args) == 2


def test_b151_6_meaning_never_takes_an_unhashable_kind():
    """B151 finding 6, at the table itself: any caller handing `meaning` a non-string kind gets UnknownClassification,
    never a TypeError (the launch's C1 check is one caller; the table is the other end)."""
    IM = load("item_meaning")
    with pytest.raises(IM.UnknownClassification):
        IM.meaning({"path": "x.py", "op": "hold", "kind": []})


# --- REVW5's B152 read of stage E2d ------------------------------------------------------------------------------

class _FakeWatcher:
    def __init__(self):
        self.stopped = False

    def terminate(self):
        self.stopped = True

    def kill(self):
        self.stopped = True

    def wait(self, timeout=None):
        return 0


@pytest.mark.parametrize("route", ["migration", "baseline"])
def test_b152_2_a_route_field_is_checked_before_any_session(tmp_path, monkeypatch, route):
    """B152 finding 2 (REVW5's falsifier for the migration route; the baseline route is the same class). A live
    migration launch with no `apply_receipt` (none in the packet, no --apply-receipt), or a baseline launch with no
    `baseline_cmd` for a taker naming no `suite_cmd`, is a named exit-2 refusal before any session or first act. On
    stage E2d the migration session ran and then `KeyError: 'apply_receipt'` was recorded (exit 1); the baseline
    route invalidated the earlier baseline and then failed on `KeyError: 'baseline_cmd'`."""
    LB, pk = launch_world(tmp_path, monkeypatch, ["a-aget"])
    packet = json.loads(pk.read_text())
    packet.pop("apply_receipt" if route == "migration" else "baseline_cmd")
    pk.write_text(json.dumps(packet))
    seen, watch, real_popen = [], _FakeWatcher(), LB.subprocess.Popen
    # only the settings watcher is replaced (no real watcher outlives the test); every other Popen is real
    monkeypatch.setattr(LB.subprocess, "Popen", lambda cmd, *a, **k: watch if str(LB.WATCHER) in map(str, cmd)
                        else real_popen(cmd, *a, **k))
    monkeypatch.setattr(LB.time, "sleep", lambda *a: None)
    monkeypatch.setattr(LB, "run_grouped",
                        lambda *a, **k: (seen.append("session") or subprocess.CompletedProcess(a[0], 0, "", "")))
    monkeypatch.setattr(LB, "take_snapshot", lambda r, ev: (Path(ev) / r["aget"]).mkdir(parents=True, exist_ok=True)
                        or (Path(ev) / r["aget"] / "settings_snapshot_pre.json").write_text("{}\n"))
    args = ["--packet", str(pk), "--launch", "--evidence", str(tmp_path / "ev")] + (["--baseline"] if route == "baseline"
                                                                                     else [])
    got = no_traceback(LB.main, args)
    assert got == 2 and not seen, (got, seen)
    assert not (tmp_path / "ev" / "a-aget" / ("launch_record.json" if route == "migration"
                                              else "baseline_record.json")).exists()


@pytest.mark.parametrize("exc", [RuntimeError, KeyboardInterrupt])
def test_b152_5_the_settings_watcher_is_stopped_when_the_session_run_raises(tmp_path, monkeypatch, exc):
    """B152 finding 5 (REVW5's falsifier; the watcher candidate row). An exception other than TimeoutExpired from the
    session run, an interrupt included, still stops the settings watcher. On stage E2d the stop was outside any
    finally and the watcher kept running (up to LIMIT_S + 120 s)."""
    LB, pk = launch_world(tmp_path, monkeypatch, ["a-aget"])
    packet = json.loads(pk.read_text())
    r = {**packet["receivers"][0], "_copy_root": True}
    watch = _FakeWatcher()
    ev = tmp_path / "ev"
    (ev / r["aget"]).mkdir(parents=True)
    (ev / r["aget"] / "settings_snapshot_pre.json").write_text("{}\n")
    monkeypatch.setattr(LB.subprocess, "Popen", lambda *a, **k: watch)
    monkeypatch.setattr(LB, "copy_session_env", lambda loc: LB.session_env())   # E2g: not this test's subject
    monkeypatch.setattr(LB.time, "sleep", lambda *a: None)

    def fail(*a, **k):
        raise exc("synthetic session failure")
    monkeypatch.setattr(LB, "run_grouped", fail)
    with pytest.raises(exc):
        LB.run_one(r, packet, ev)
    assert watch.stopped


@pytest.mark.parametrize("exc", [RuntimeError, KeyboardInterrupt])
def test_b152_5_the_session_group_is_killed_when_its_wait_raises(tmp_path, monkeypatch, exc):
    """B152 finding 5 (REVW5's falsifier), one level down: an exception from the session process's timed wait still
    kills its process group. On stage E2d `_kill_group` and the final wait were skipped. No real process is made."""
    LB = load("launch_batch")
    seen = []

    class Process:
        pid, returncode = 123456789, None

        def wait(self, timeout=None):
            if timeout is not None:
                raise exc("synthetic wait failure")
            self.returncode = -9
            return -9
    monkeypatch.setattr(LB.subprocess, "Popen", lambda *a, **k: Process())
    monkeypatch.setattr(LB, "_kill_group", lambda pid: seen.append(pid))
    with pytest.raises(exc):
        LB.run_grouped(["synthetic-command"], tmp_path, dict(os.environ), 1)
    assert seen == [123456789]


# --- REVW5's B153 read of stage E2e ------------------------------------------------------------------------------

@pytest.mark.parametrize("exc", [RuntimeError, KeyboardInterrupt])
def test_b153_2_the_watcher_is_stopped_during_its_startup_delay(tmp_path, monkeypatch, exc):
    """B153 finding 2 (REVW5's falsifier). An exception or interrupt during the watcher's 2-second startup delay
    still stops it. On stage E2e the delay and the command build came before the try, and the watcher kept running."""
    LB, pk = launch_world(tmp_path, monkeypatch, ["a-aget"])
    packet = json.loads(pk.read_text())
    r = {**packet["receivers"][0], "_copy_root": True}
    ev = tmp_path / "ev"
    (ev / r["aget"]).mkdir(parents=True)
    (ev / r["aget"] / "settings_snapshot_pre.json").write_text("{}\n")
    watch = _FakeWatcher()
    monkeypatch.setattr(LB.subprocess, "Popen", lambda *a, **k: watch)
    monkeypatch.setattr(LB, "copy_session_env", lambda loc: LB.session_env())   # E2g: not this test's subject

    def fail(seconds):
        if seconds == 2:
            raise exc("synthetic startup-delay failure")
    monkeypatch.setattr(LB.time, "sleep", fail)
    with pytest.raises(exc):
        LB.run_one(r, packet, ev)
    assert watch.stopped


# --- REVW6's B162 read of stage E2g ------------------------------------------------------------------------------

def test_b162_4_the_repair_work_root_may_not_lie_in_a_declared_plain_sibling(tmp_path):
    """B162 finding 4 (REVW6's falsifier). A repair receiver declares a plain sibling folder (no `.git`) and
    `--scratch` lies inside it: the run is refused, and nothing is made in the sibling. On stage E2g the repair
    rehearsal's work-root check left sibling sources out of its avoid set, and its run folder, copy and suites were made
    there."""
    RR = load("rehearse_repair")
    member, r, pre, head = repair_world(tmp_path)
    sibling = member.parent / "plain-sibling"
    sibling.mkdir()
    (sibling / "keep.txt").write_text("sentinel\n")
    r["sibling_reads"] = ["../plain-sibling"]
    pk, prev, out = tmp_path / "packet.json", tmp_path / "previous.json", tmp_path / "result.json"
    pk.write_text(json.dumps({"receivers": [r]}))
    prev.write_text(json.dumps({"receivers": [{"aget": r["aget"], "head": pre}]}))
    work = sibling / "work"
    code = no_traceback(RR.main, ["--packet", str(pk), "--previous-packet", str(prev), "--scratch", str(work),
                                  "--out", str(out)])
    assert code == 2 and json.loads(out.read_text())["verdict"] == "REFUSED"
    assert not work.exists() and sorted(p.name for p in sibling.iterdir()) == ["keep.txt"]


# --- E2i: ignore state (IGN, R1 clause 8) around the rehearsal suites and the known-missing auditor ----------------

def test_e2i_a_rehearsal_suite_that_changes_the_ignore_state_does_not_count(tmp_path):
    """R1 clause 8 at the V3.6 rehearsal suites (rehearse_repair.suite(), also used by rehearse_batch2): a suite that
    adds a self-ignoring nested `.gitignore` and writes under it is not a completed run (`ran` False, so the
    rehearsal is INCONCLUSIVE), and the evidence names the element. Until E2i it read as ran, 1 passed."""
    RR = load("rehearse_repair")
    copy = tmp_path / "run" / "seat"
    git_repo(copy, {"tests/test_x.py": "from pathlib import Path\n\ndef test_a():\n    Path('sub').mkdir()\n"
                                       "    Path('sub/.gitignore').write_text('*\\n')\n"
                                       "    Path('sub/h.txt').write_text('x\\n')\n"})
    assert RR.CI.isolate(copy, "remove", member=True, run=copy.parent) is None     # as the rehearsal makes it
    ev = tmp_path / "ev"
    ev.mkdir()
    res = RR.suite(copy, "S0_baseline", ev)
    assert res["ran"] is False and ".gitignore sub/.gitignore" in res.get("why", ""), res
    assert "IGNORE STATE: the suite changed git's ignore state" in (ev / "S0_baseline.txt").read_text()


def test_e2i_a_rehearsal_suite_that_leaves_the_ignore_state_alone_still_counts(tmp_path):
    """The positive control for the test above: the same suite without the ignore change reads as ran."""
    RR = load("rehearse_repair")
    copy = tmp_path / "run" / "seat"
    git_repo(copy, {"tests/test_x.py": "from pathlib import Path\n\ndef test_a():\n    Path('h.txt').write_text('x')\n"})
    assert RR.CI.isolate(copy, "remove", member=True, run=copy.parent) is None     # as the rehearsal makes it
    ev = tmp_path / "ev"
    ev.mkdir()
    res = RR.suite(copy, "S0_baseline", ev)
    assert res["ran"] is True and res["summary"].startswith("1 passed"), res
