"""Gate 3 of the v3.36.0 kit design pass (v336-release:R28): R1 containment, the packet root (sealed stage, baseline
slots), the placer, and the kit's stage and baseline writes at the act (design read 2, D-6).

Each behavioural test fails on 34353311 for the defect it names and passes after the change; the placer's own refusals
test a script that does not exist at 34353311 (its behavioural counterpart: the prompt no longer issues `cp -f`).
Nothing outside tmp_path is touched; no session is launched.
"""
import hashlib
import importlib.util
import json
import os
import stat
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "scripts/migration_kit"


def load(name):
    spec = importlib.util.spec_from_file_location(name, BATCH / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


@pytest.mark.parametrize("existing", [None, 0o644, 0o755])
@pytest.mark.parametrize("release_mode", [0o644, 0o755])
def test_round2_placer_carries_release_executable_bit(tmp_path, monkeypatch, existing, release_mode):
    """M-6: the sealed stage decides the git executable bit, including replacement of an existing file."""
    PF = load("place_file")
    member = tmp_path / "member"
    member.mkdir()
    staged = tmp_path / "tool.sh"
    staged.write_bytes(b"#!/bin/sh\nexit 0\n")
    staged.chmod(release_mode & ~0o222)  # the packet seal clears write bits
    target = member / "tool.sh"
    if existing is not None:
        target.write_bytes(b"old\n")
        target.chmod(existing)
    monkeypatch.chdir(member)
    PF.place(str(member), "tool.sh", str(staged), hashlib.sha256(staged.read_bytes()).hexdigest())
    assert stat.S_IMODE(target.stat().st_mode) == release_mode
    subprocess.run(["git", "init", "-q", str(member)], check=True)
    subprocess.run(["git", "-C", str(member), "add", "tool.sh"], check=True)
    index = subprocess.check_output(["git", "-C", str(member), "ls-files", "--stage"], text=True)
    assert index.startswith("100755" if release_mode == 0o755 else "100644")


@pytest.mark.parametrize("release_mode", [0o644, 0o755])
def test_round2_stage_carries_committed_mode(tmp_path, monkeypatch, release_mode):
    """M-6: the contained stage writer must receive the mode from the release tree, not its umask."""
    PL = load("prepare_launch")
    source = tmp_path / "source"
    git_member(source)
    tool = source / "tool.sh"
    tool.write_bytes(b"#!/bin/sh\nexit 0\n")
    tool.chmod(release_mode)
    subprocess.run(["git", "-C", str(source), "add", "tool.sh"], check=True)
    subprocess.run(["git", "-C", str(source), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "tool"], check=True)
    subprocess.run(["git", "-C", str(source), "tag", PL.R.TO_TAG], check=True)
    stage = tmp_path / "stage"
    stage.mkdir()
    monkeypatch.setattr(PL, "STAGE", stage)
    staged, digest = PL.stage(source, "tool.sh")
    assert digest == hashlib.sha256(tool.read_bytes()).hexdigest()
    assert stat.S_IMODE(staged.stat().st_mode) == release_mode


def test_round2_writer_checks_mode_and_rolls_it_back(tmp_path, monkeypatch):
    """M-6: explicit release modes are verified; a later failed write restores the original bytes and mode."""
    CI = load("copy_isolation")
    (tmp_path / "a").write_bytes(b"old")
    (tmp_path / "a").chmod(0o644)
    data = b"new"
    actions = [("a", data, hashlib.sha256(data).hexdigest()), ("b", data, "0" * 64)]
    res = CI.write_all(tmp_path, actions, modes={"a": 0o755, "b": 0o755})
    assert res.category == "C3"
    assert (tmp_path / "a").read_bytes() == b"old"
    assert stat.S_IMODE((tmp_path / "a").stat().st_mode) == 0o644
    assert not (tmp_path / "b").exists()
    res = CI.write_all(tmp_path, actions[:1], modes={"a": 0o755})
    assert res.ok() and stat.S_IMODE((tmp_path / "a").stat().st_mode) == 0o755


def git_member(loc):
    loc.mkdir(parents=True)
    (loc / "a.txt").write_text("x\n")
    subprocess.run(["git", "init", "-q", str(loc)], check=True)
    subprocess.run(["git", "-C", str(loc), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(loc), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c"],
                   check=True)
    return subprocess.run(["git", "-C", str(loc), "rev-parse", "HEAD"], capture_output=True,
                          text=True).stdout.strip()


def tree_state(root):
    """Every entry under root: kind, mode and bytes."""
    out = {}
    for folder, dirs, files in os.walk(root):
        for n in dirs + files:
            p = Path(folder) / n
            st = os.lstat(p)
            out[str(p.relative_to(root))] = (st.st_mode, p.read_bytes() if stat.S_ISREG(st.st_mode) else None)
    return out


def baseline_world(tmp_path, monkeypatch):
    """A member, a packet root with a stage and an open slot, and a stubbed baseline session whose stream shows the
    suite command and a pytest summary."""
    LB = load("launch_batch")
    loc = tmp_path / "home" / "a"
    head = git_member(loc)
    pr = tmp_path / "pr"
    (pr / "stage" / "kit").mkdir(parents=True)
    (pr / "stage" / "kit" / "f").write_text("staged\n")
    (pr / "baselines" / "a").mkdir(parents=True)
    suite = "python3 -m pytest -q"
    def session(cmd, cwd, env, t):
        # C2a7 (B185 finding 1, changed, labelled): the stubbed session's pytest writes the kit report the kit made for
        # it (one clean invocation, as the plugin writes it) and its output names that invocation
        rows = [{"rec": "start", "inv": "e" * 32, "pid": 1, "args": [], "dir": ".", "lf": False},
                {"rec": "finish", "inv": "e" * 32, "exit": 0, "events": 0, "collected": 0, "ran": 0, "deselected": [],
                     "narrowed": [], "dropped": 0, "suppressed": [], "selection": {"roots": ["tests"], "ignored": [], "python_files": ["test_*.py", "*_test.py"], "python_classes": ["Test"], "python_functions": ["test"], "testpaths": [], "blocked": [], "plugins": [], "producers": ["fixture"], "autoload": ["on"]}, "census": []}]    # C2a10 (labelled): the two new finish fields; C2c (labelled): the whole witness
        with open(env["AGET_KIT_REPORT"], "a") as fh:
            fh.write("".join(json.dumps({**x, "token": env["AGET_KIT_REPORT_TOKEN"]}) + "\n" for x in rows))
        stream = "\n".join(json.dumps(e) for e in [
            # C2a10 (B192 finding 2, changed, labelled): a Bash call, as both readers now require
            {"sessionId": "S", "message": {"content": [{"type": "tool_use", "id": "t", "name": "Bash", "input": {"command": suite}}]}},
            {"sessionId": "S", "message": {"content": [{"type": "tool_result", "tool_use_id": "t",
                                      "content": f"aget-kit-report: pytest {'e' * 32}\n1 passed in 0.01s"}]}}])
        return subprocess.CompletedProcess(cmd, 0, stream, "")
    monkeypatch.setattr(LB, "run_grouped", session)
    r = {"aget": "a", "location": str(loc), "head": head, "settings": {"path": str(tmp_path / "s.json")},
         "baseline_prompt": "b"}
    packet = {"packet_root": str(pr), "stage": str(pr / "stage"), "tools": "Bash", "deny": [], "baseline_cmd": suite}
    return LB, r, packet, pr


def test_r1_t10b_a_baseline_goes_into_its_slot_and_leaves_the_stage_alone(tmp_path, monkeypatch):
    """R1-T10 (b) (design read 1 D-3). The live baseline is written to PR/baselines/<aget>/baseline.json, and no byte or
    mode under PR/stage changes. At 34353311 it is written into the shared stage (<stage>/baselines/<aget>.json)."""
    LB, r, packet, pr = baseline_world(tmp_path, monkeypatch)
    before = tree_state(pr / "stage")
    doc = LB.run_baseline(r, packet, tmp_path / "ev", packet["stage"])
    assert doc["verdict"] == "RECORDED"
    assert json.loads((pr / "baselines" / "a" / "baseline.json").read_text())["verdict"] == "RECORDED"
    assert tree_state(pr / "stage") == before


def test_r1_t10c_a_launch_seals_the_slot_and_a_later_baseline_is_refused(tmp_path, monkeypatch):
    """R1-T10 (c). The B8 launch seals the receiver's slot and records the baseline's digest; a later --baseline for
    that receiver is refused, and the sealed baseline is unchanged. At 34353311 nothing is sealed: a later baseline
    overwrites the one the session was given."""
    LB, r, packet, pr = baseline_world(tmp_path, monkeypatch)
    LB.run_baseline(r, packet, tmp_path / "ev", packet["stage"])
    f = pr / "baselines" / "a" / "baseline.json"
    first = f.read_bytes()
    digest = LB.seal_baseline_slot(r, packet)
    assert digest == hashlib.sha256(first).hexdigest()
    with pytest.raises(Exception):
        LB.run_baseline(r, packet, tmp_path / "ev", packet["stage"])
    assert f.read_bytes() == first


def test_r1_t10d_a_rehearsal_baseline_never_touches_the_packet(tmp_path, monkeypatch):
    """R1-T10 (d). A --copy-root baseline leaves the packet root byte- and mode-identical and is written inside the
    copy. At 34353311 the rehearsal writes into the shared stage (and rehearse_v37 had to restore it afterwards)."""
    LB, r, packet, pr = baseline_world(tmp_path, monkeypatch)
    assert load("copy_isolation").isolate(r["location"], "remove", member=True) is None   # a copy is isolated (E2g)
    before = tree_state(pr)
    LB.run_baseline({**r, "_copy_root": True}, packet, tmp_path / "ev", packet["stage"])
    assert tree_state(pr) == before
    assert (Path(r["location"]) / ".git" / "aget_rehearsal_baseline.json").is_file()


def test_d6_a_baseline_slot_reached_through_a_link_is_never_written_through(tmp_path, monkeypatch):
    """Design read 2, D-6 (baseline writes at the act). The packet's baselines folder is a link to an outside folder.
    Expected: the write is refused and the outside folder is unchanged. At 34353311 the baseline is written through
    the link (<stage>/baselines -> outside)."""
    LB, r, packet, pr = baseline_world(tmp_path, monkeypatch)
    outside = tmp_path / "outside"
    (outside / "a").mkdir(parents=True)
    os.rename(pr / "baselines", tmp_path / "real_baselines")
    (pr / "baselines").symlink_to(outside)
    (pr / "stage" / "baselines").symlink_to(outside)               # the old layout's folder, the same way
    before = tree_state(outside)
    try:
        LB.run_baseline(r, packet, tmp_path / "ev", packet["stage"])
    except Exception:   # noqa: BLE001 — after the change the act is refused; the assertion is on the outside folder
        pass
    assert tree_state(outside) == before


def test_d6_a_stage_folder_swapped_for_a_link_is_never_written_through(tmp_path, monkeypatch):
    """Design read 2, D-6 (stage writes at the act). A stage subfolder is a link to an outside folder when the release
    bytes are staged. Expected: refused, the outside folder unchanged. At 34353311 stage() writes through it."""
    PL = load("prepare_launch")
    repo = tmp_path / "core"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    (repo / "docs").mkdir()
    (repo / "docs" / "x.md").write_text("release\n")
    subprocess.run(["git", "-C", str(repo), "add", "-A"], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c"],
                   check=True)
    subprocess.run(["git", "-C", str(repo), "tag", PL.R.TO_TAG], check=True)
    stage = tmp_path / "stage"
    stage.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (stage / "core").symlink_to(outside)
    monkeypatch.setattr(PL, "STAGE", stage)
    try:
        PL.stage(repo, "docs/x.md")
    except Exception:   # noqa: BLE001
        pass
    assert list(outside.iterdir()) == []


def test_r1_t11_a_changed_stage_stops_every_launch_before_any_session(tmp_path, monkeypatch):
    """R1-T11. A staged file whose bytes changed after the seal: the launch exits 2 and starts no session. At
    34353311 nothing is compared, and the session starts (here: run_grouped is reached)."""
    spec = importlib.util.spec_from_file_location("rr", Path(__file__).with_name(
        "test_migration_kit_rehearse_refusal.py"))
    M = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(M)
    LB, pk = M.launch_world(tmp_path, monkeypatch, ["a-aget"])
    monkeypatch.setattr(LB, "take_snapshot", lambda r, ev: None, raising=False)
    doc = json.loads(pk.read_text())
    staged = Path(doc["packet_root"]) / "stage" / "kit" / "place_file.py"
    os.chmod(staged, 0o644)
    staged.write_text("# changed after the seal\n")
    assert M.no_traceback(LB.main, ["--packet", str(pk), "--launch", "--evidence", str(tmp_path / "ev")]) == 2


# --- the placer (R1-T19) -----------------------------------------------------------------------------------------

def placer(member, rel, staged, digest):
    return subprocess.run([sys.executable, str(BATCH / "place_file.py"), str(member), rel, str(staged), digest],
                          cwd=member, capture_output=True, text=True)


def test_r1_t19_the_prompt_places_with_the_placer_not_cp(tmp_path):
    """R1-T19, behavioural half. placing_commands emits no `cp -f` and no `mkdir -p`. At 34353311 it emits `cp -f
    <staged> <path>`, which follows a link and truncates a hard-linked file in place."""
    PL = load("prepare_launch")
    i = PL.placing_commands({"path": "sub/f.py", "op": "write", "staged": "/s/f.py", "sha256": "d" * 64},
                            str(tmp_path))
    assert not i["command"].startswith("cp ") and "place_file.py" in i["command"] and "mkdir" not in i


@pytest.mark.parametrize("shape", ["link_leaf", "hard_leaf", "link_parent", "bad_digest"])
def test_r1_t19_the_placer_refuses_what_cp_would_write_through(tmp_path, shape):
    """R1-T19 (the placer itself; new script, no 34353311 counterpart). A destination that is a link or has a second
    name, a parent that is a link, or a staged file whose digest differs: refused, nothing outside changes."""
    member = tmp_path / "m"
    (member / "sub").mkdir(parents=True)
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "f.py").write_text("outside\n")
    staged = tmp_path / "staged.py"
    staged.write_text("release\n")
    digest = hashlib.sha256(b"release\n").hexdigest()
    if shape == "link_leaf":
        (member / "sub" / "f.py").symlink_to(outside / "f.py")
    elif shape == "hard_leaf":
        os.link(outside / "f.py", member / "sub" / "f.py")
    elif shape == "link_parent":
        (member / "sub").rmdir()
        (member / "sub").symlink_to(outside)
    else:
        digest = "0" * 64
    p = placer(member, "sub/f.py", staged, digest)
    assert p.returncode == 2 and "REFUSED" in p.stderr
    assert (outside / "f.py").read_text() == "outside\n" and sorted(x.name for x in outside.iterdir()) == ["f.py"]


def test_r1_t19_the_placer_writes_an_ordinary_target_and_makes_its_folders(tmp_path):
    """Control: an absent target in a missing folder is placed with the staged bytes."""
    member = tmp_path / "m"
    member.mkdir()
    staged = tmp_path / "staged.py"
    staged.write_text("release\n")
    p = placer(member, "new/deep/f.py", staged, hashlib.sha256(b"release\n").hexdigest())
    assert p.returncode == 0 and (member / "new" / "deep" / "f.py").read_text() == "release\n"


# --- push routes (R1 clause 4 and 1(c)): J-3, R1-T4, R1-T13, R1-T14 ---------------------------------------------

def member_with_remote(tmp_path, name="m"):
    remote = tmp_path / f"{name}_remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    loc = tmp_path / name
    git_member(loc)
    subprocess.run(["git", "-C", str(loc), "remote", "add", "origin", str(remote)], check=True)
    return loc, remote


def refs(remote):
    return subprocess.run(["git", "--git-dir", str(remote), "for-each-ref"], capture_output=True, text=True).stdout


def test_r1_t4_an_alias_keyed_to_a_removed_remote_cannot_push_from_a_copy(tmp_path):
    """R1-T4, J-3. A member whose config holds `url.<its remote>.insteadOf = origin`. In its isolated copy, `git push
    origin` must not reach the remote. At 34353311 isolation removes the remote `origin`, the alias turns the word
    `origin` back into the remote's path, and the push lands."""
    import shutil
    CI = load("copy_isolation")
    loc, remote = member_with_remote(tmp_path)
    subprocess.run(["git", "-C", str(loc), "config", f"url.{remote}.insteadOf", "origin"], check=True)
    copy = tmp_path / "copy"
    shutil.copytree(loc, copy, symlinks=True)
    assert CI.isolate(copy, "remove", member=True) is None
    p = subprocess.run(["git", "-C", str(copy), "push", "origin", "HEAD:refs/heads/x"], capture_output=True)
    assert p.returncode != 0 and refs(remote) == ""


def test_r1_t13_a_session_cannot_push_to_a_relative_path(tmp_path):
    """R1-T13. Under the session environment, `git push ../remote.git` must fail. At 34353311 the push-URL rewrite
    covers `file://` and absolute paths (measured) but not a relative path, and the push lands."""
    LB = load("launch_batch")
    loc, remote = member_with_remote(tmp_path)
    p = subprocess.run(["git", "-C", str(loc), "push", f"../{remote.name}", "HEAD:refs/heads/x"],
                       capture_output=True, env=LB.session_env())
    assert p.returncode != 0 and refs(remote) == ""


def test_r1_t14_the_push_gate_refuses_a_destination_that_changed_since_b1(tmp_path):
    """R1-T14. Every other push condition holds (bound PASS verdict, success receipt, B8a PASS); B1 recorded origin's
    push URL, and by B10 a `pushInsteadOf` rule redirects it to another repository. The gate must refuse. At 34353311
    (with the result-binding module present for the trace) nothing is compared and the gate returns push facts."""
    spec = importlib.util.spec_from_file_location("rb_tests", Path(__file__).with_name(
        "test_migration_kit_result_binding.py"))
    RBT = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(RBT)
    PB = load("push_batch")
    r, ev, head = RBT.gate_world(tmp_path)
    RBT.launch_trace(ev, head)
    assert PB.gate(r, tmp_path / "ev", [])[0]                                    # control: as recorded, it passes
    elsewhere = tmp_path / "elsewhere.git"
    subprocess.run(["git", "init", "-q", "--bare", str(elsewhere)], check=True)
    subprocess.run(["git", "-C", r["location"], "config", f"url.{elsewhere}.pushInsteadOf", r["push_url"][0]],
                   check=True)
    ok, why = PB.gate(r, tmp_path / "ev", [])
    assert ok is None and "recorded at B1" in why, why


# --- R1 LINKS (J-2, H-4, H-5): every symbolic link in a copy resolves inside the run's folder ---------------------

def linked_member(tmp_path, target, name="m", track=False):
    """A member repository with `docs -> target`; with `track` the link is committed (a clone checks it out)."""
    loc = tmp_path / name
    git_member(loc)
    (loc / "docs").symlink_to(target)
    if track:
        subprocess.run(["git", "-C", str(loc), "add", "docs"], check=True)
        subprocess.run(["git", "-C", str(loc), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m",
                        "link"], check=True)
    return loc


def marked_copy(LB, loc, copy, sha="0" * 64, aget="m"):
    import shutil
    shutil.copytree(loc, copy, symlinks=True)
    (copy / ".git" / LB.COPY_MARKER).write_text(json.dumps({"packet_sha256": sha, "aget": aget}))
    return copy


@pytest.mark.parametrize("site", ["isolate", "rehearse_batch2", "suite_at_commit", "launch_copy_root"])
def test_r1_t2a_a_link_leading_outside_the_run_is_refused_before_any_launch(tmp_path, site):
    """R1-T2 (a), J-2/H-5. A member with `docs -> <outside folder>`: every copy route refuses it before anything runs
    in the copy (isolation, used by the packet and repair rehearsals; the packet rehearsal's copy; the B8a clone after
    its checkout; and the launch's --copy-root check, asked at each launch). At 34353311 each accepts it: isolation
    tests only links under .git, and `copytree(symlinks=True)` and `cp -a` keep the link."""
    import shutil
    outside = tmp_path / "outside"
    outside.mkdir()
    (outside / "f.md").write_text("outside\n")
    loc = linked_member(tmp_path, outside, track=(site == "suite_at_commit"))
    if site == "isolate":
        CI = load("copy_isolation")
        copy = tmp_path / "copy"
        shutil.copytree(loc, copy, symlinks=True)
        why = CI.isolate(copy, "remove", member=True)
        assert why and "leads outside" in why, why
    elif site == "rehearse_batch2":
        RB = load("rehearse_batch2")
        with pytest.raises(ValueError, match="leads outside"):
            RB.copy_of({"aget": "m", "location": str(loc)}, tmp_path / "scratch")
    elif site == "suite_at_commit":
        SC = load("suite_at_commit")
        sha = subprocess.run(["git", "-C", str(loc), "rev-parse", "HEAD"], capture_output=True,
                             text=True).stdout.strip()
        clone, why = SC.clean_clone(loc, "m", sha, [], tmp_path / "work")
        assert clone is None and "leads outside" in why, why
    else:
        LB = load("launch_batch")
        copy = marked_copy(LB, loc, tmp_path / "copy")
        why = LB.copy_root_refusal(copy, loc, "0" * 64, "m")
        assert why and "leads outside" in why, why
    assert (outside / "f.md").read_text() == "outside\n"


def test_r1_t2b_a_hook_linked_into_the_members_tree_is_admitted_and_runs_inside_the_copy(tmp_path):
    """R1-T2 (b), H-4. `.git/hooks/pre-commit -> ../../scripts/pre-commit` stays inside the copy, so isolation and
    the launch's --copy-root check admit it, and a commit in the copy runs it with its sentinel landing inside the
    copy. At 34353311 the boundary was `.git`, so the layout was refused ("leads outside .../.git")."""
    import shutil
    CI, LB = load("copy_isolation"), load("launch_batch")
    loc = tmp_path / "m"
    git_member(loc)
    (loc / "scripts").mkdir()
    hook = loc / "scripts" / "pre-commit"
    hook.write_text("#!/bin/sh\ntouch hook_ran\n")
    hook.chmod(0o755)
    (loc / ".git" / "hooks").mkdir(exist_ok=True)
    (loc / ".git" / "hooks" / "pre-commit").symlink_to("../../scripts/pre-commit")
    copy = tmp_path / "copy"
    shutil.copytree(loc, copy, symlinks=True)
    assert CI.isolate(copy, "remove", member=True) is None
    marked = marked_copy(LB, loc, tmp_path / "copy2")
    assert LB.copy_root_refusal(marked, loc, "0" * 64, "m") is None
    (copy / "b.txt").write_text("y\n")
    subprocess.run(["git", "-C", str(copy), "add", "b.txt"], check=True)
    subprocess.run(["git", "-C", str(copy), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c2"],
                   check=True)
    assert (copy / "hook_ran").exists() and not (loc / "hook_ran").exists()


def test_r1_links_a_link_into_a_copied_sibling_is_admitted_and_one_past_the_run_is_not(tmp_path):
    """R1 LINKS, boundary RUN (control). With a declared sibling the run's folder holds the copy and the sibling, so
    a member link into `../sib` is admitted; a plain sibling folder whose link leads out of the run is refused
    (H-5: at 34353311 a sibling with no .git was copied with its links and never tested)."""
    RB = load("rehearse_batch2")
    sib = tmp_path / "sib"
    sib.mkdir()
    (sib / "x.md").write_text("x\n")
    loc = linked_member(tmp_path, Path("../sib/x.md"))
    dest = RB.copy_of({"aget": "m", "location": str(loc)}, tmp_path / "s1", siblings=["../sib"])
    assert (dest / "docs").read_text() == "x\n" and (dest.parent / "sib").is_dir()
    outside = tmp_path / "outside"
    outside.mkdir()
    (sib / "out").symlink_to(outside)
    with pytest.raises(ValueError, match="leads outside"):
        RB.copy_of({"aget": "m", "location": str(loc)}, tmp_path / "s2", siblings=["../sib"])


# --- REVW3's B148 read: findings carried in with its falsifiers -------------------------------------------------

@pytest.mark.parametrize("shape", ["ancestor_symlink", "hard_baseline"])
def test_b148_1_baseline_seal_never_changes_an_outside_target(tmp_path, monkeypatch, shape):
    """B148 finding 1 (REVW3's falsifier). Sealing a baseline slot is an act: a slot reached through a linked
    ancestor (`PR/baselines -> outside`), or a baseline file with a second name outside, must not have its mode
    changed. On stage F2 both chmods followed the link and the hard-linked file went 0644 -> 0444."""
    LB, r, pk, pr = baseline_world(tmp_path, monkeypatch)
    outside = tmp_path / "outside"
    (outside / "a").mkdir(parents=True)
    f = outside / "a" / "baseline.json"
    f.write_text("outside\n")
    f.chmod(0o644)
    if shape == "ancestor_symlink":
        os.rename(pr / "baselines", tmp_path / "old_slots")
        (pr / "baselines").symlink_to(outside)
    else:
        os.link(f, pr / "baselines" / "a" / "baseline.json")
    before = (f.read_bytes(), stat.S_IMODE(f.stat().st_mode), stat.S_IMODE((outside / "a").stat().st_mode))
    try:
        got = LB.seal_baseline_slot(r, pk)
    except Exception as e:   # noqa: BLE001
        got = e
    after = (f.read_bytes(), stat.S_IMODE(f.stat().st_mode), stat.S_IMODE((outside / "a").stat().st_mode))
    assert after == before, f"an outside mode changed: {before} -> {after}"
    assert type(got).__name__ == "ContainmentRefused", got


def test_b148_1_an_ordinary_slot_is_still_sealed_and_its_digest_returned(tmp_path, monkeypatch):
    """B148 finding 1, control: an ordinary slot and baseline are sealed (no write bit left) and the digest returned;
    a slot that does not exist returns None."""
    LB, r, pk, pr = baseline_world(tmp_path, monkeypatch)
    f = pr / "baselines" / "a" / "baseline.json"
    f.write_text("{}\n")
    assert LB.seal_baseline_slot(r, pk) == hashlib.sha256(b"{}\n").hexdigest()
    assert not (f.stat().st_mode & 0o222) and not ((pr / "baselines" / "a").stat().st_mode & 0o222)
    assert LB.seal_baseline_slot({**r, "aget": "none"}, pk) is None


# --- REVW4's B151 read of stage E2c: findings carried in with its falsifiers ------------------------------------

def _run_git(p, *a, env=None):
    return subprocess.run(["git", "-C", str(p), *a], env=env, capture_output=True, text=True)


def test_b151_1_session_protocol_admits_no_remote_helper(tmp_path):
    """B151 finding 1 (REVW4's falsifier). A session's git starts no transport, a remote helper included. On stage
    E2c `GIT_ALLOW_PROTOCOL=none` named one protocol, `none`, so a synthetic `git-remote-none` on PATH received
    `push` and git exited 0. The helper only logs; nothing leaves tmp_path."""
    LB = load("launch_batch")
    m = tmp_path / "m"
    git_member(m)
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    sentinel = tmp_path / "transport.txt"
    helper = bin_ / "git-remote-none"
    helper.write_text("#!/usr/bin/env python3\nimport os, sys\nfrom pathlib import Path\n"
                      "p = Path(os.environ['KIT_TEST_TRANSPORT_SENTINEL'])\n"
                      "for line in sys.stdin:\n"
                      "    p.open('a').write(line)\n"
                      "    if line.startswith('capabilities'): print('push\\n', flush=True)\n"
                      "    elif line.startswith('list'): print('', flush=True)\n"
                      "    elif line.startswith('push '): print('ok ' + line.strip().split(':')[-1] + '\\n', flush=True)\n")
    helper.chmod(0o755)
    env = {**LB.session_env(), "PATH": str(bin_) + os.pathsep + os.environ["PATH"],
           "KIT_TEST_TRANSPORT_SENTINEL": str(sentinel)}
    p = _run_git(m, "push", "none::synthetic", "HEAD:refs/heads/main", env=env)
    assert not sentinel.exists() and p.returncode != 0, (p.returncode, p.stderr, sentinel.read_text()
                                                         if sentinel.exists() else None)
    q = _run_git(m, "push", str(tmp_path / "nowhere.git"), "HEAD:refs/heads/main", env=env)   # a local path too
    assert q.returncode != 0 and "not allowed" in q.stderr, q.stderr


def test_b151_2_confirmation_sibling_has_no_remaining_named_alias_push(tmp_path, monkeypatch):
    """B151 finding 2 (REVW4's falsifier). The confirmation copy's sibling goes through full isolation: a copied
    sibling's `url.<bare>.insteadOf=named-alias` must not push. On stage E2c `confirm_at_head` set push URLs only, so
    the push from the copy reached the temporary bare repository. The pytest call is replaced by that push and a
    one-test summary; clone, sibling copy and isolation are the real code."""
    A = load("after_run_check")
    m = tmp_path / "m"
    git_member(m)
    sib = tmp_path / "sib"
    git_member(sib)
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    assert _run_git(sib, "config", f"url.{remote}.insteadOf", "named-alias").returncode == 0
    original = A.subprocess.run
    pushed = {}

    def run(cmd, *a, **k):
        if len(cmd) > 3 and cmd[1:4] == ["-m", "pytest", "-q"]:
            copied = Path(k["cwd"]).parent / "sib"
            pushed["p"] = original(["git", "-C", str(copied), "push", "named-alias", "HEAD:refs/heads/main"],
                                   capture_output=True, text=True)
            return subprocess.CompletedProcess(cmd, 0, "1 passed in 0.01s\n", "")
        return original(cmd, *a, **k)
    monkeypatch.setattr(A.subprocess, "run", run)
    got = A.confirm_at_head(m, "m", ["tests/t.py::test_t"], ["../sib"], tmp_path / "work")
    landed = _run_git(remote, "rev-parse", "refs/heads/main")
    assert landed.returncode != 0, (got, pushed)


def test_b151_2_the_session_rehearsal_copy_keeps_no_url_rewrite(tmp_path, monkeypatch):
    """B151 finding 2, the same class at the session rehearsal's member copy (REVW4: `remove_remotes` only). A member
    whose own config carries `url.<bare>.insteadOf=named-alias` is copied; before the launch runs in the copy, no push
    route may remain. On stage E2c the remotes were removed and the rewrite rule kept."""
    V = load("rehearse_v37")
    CI = load("copy_isolation")
    m = tmp_path / "m"
    head = git_member(m)
    remote = tmp_path / "remote.git"
    subprocess.run(["git", "init", "-q", "--bare", str(remote)], check=True)
    assert _run_git(m, "config", f"url.{remote}.insteadOf", "named-alias").returncode == 0
    pk = tmp_path / "packet.json"
    packet = {"receivers": [{"aget": "m", "location": str(m), "head": head}]}
    pk.write_text(json.dumps(packet))
    seen = {}

    def fake_run(*cmd):
        copy = tmp_path / "scratch" / "m"
        seen["routes"] = CI.push_routes(copy)
        return 1
    monkeypatch.setattr(V, "run", fake_run)
    got = V.rehearse("m", pk, packet, None, tmp_path / "scratch")
    assert "routes" in seen, got
    assert seen["routes"] == {}, seen["routes"]


@pytest.mark.parametrize("base", ["no-push://disabled-by-the-migration-kit", "https://example.invalid/"])
def test_b151_3_unused_global_rewrite_to_the_dead_url_does_not_refuse_an_isolated_copy(tmp_path, base):
    """B151 finding 3 (REVW4's falsifier). On the remove route, an unused inherited rewrite that resolves only to the
    kit's own dead URL is admitted. On stage E2c the remove route's allowed set was empty and the copy was refused.
    Control: a rewrite to any other destination (the HTTPS case) is still refused (the declared conservative policy)."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    config = tmp_path / "global"
    config.write_text(f'[url "{base}"]\n insteadOf = unused-alias:\n')
    env = {**os.environ, "GIT_CONFIG_GLOBAL": str(config)}
    why = CI.isolate(m, "remove", env, member=True)
    if base.startswith("no-push://"):
        assert why is None, why
    else:
        assert why and "unused-alias" in why, why


def test_b151_7_seal_tree_never_chmods_an_outside_hardlink(tmp_path):
    """B151 finding 7 (REVW4's falsifier). A stage file with a second name outside is refused before any mode change.
    On stage E2c `seal_tree` chmodded by path and the outside file went 0644 -> 0444."""
    CI = load("copy_isolation")
    root = tmp_path / "stage"
    root.mkdir()
    (root / "ok.txt").write_text("ok\n")
    outside = tmp_path / "outside"
    outside.write_text("safe\n")
    outside.chmod(0o644)
    os.link(outside, root / "a")
    with pytest.raises(CI.ContainmentRefused, match="names"):
        CI.seal_tree(root)
    assert stat.S_IMODE(outside.stat().st_mode) == 0o644
    assert stat.S_IMODE((root / "ok.txt").stat().st_mode) & 0o200 and stat.S_IMODE(root.stat().st_mode) & 0o200


def test_b151_7_seal_tree_reaches_its_root_without_a_link(tmp_path):
    """B151 finding 7 (REVW4: the root was not opened by the contained walk). A stage root that is a symbolic link is
    refused with no mode changed (on stage E2c `os.walk` listed the link's target and every file there was sealed);
    root/rel through a linked component is refused too; an ordinary tree is sealed and its manifest returned
    (control)."""
    CI = load("copy_isolation")
    real = tmp_path / "real"
    (real / "d").mkdir(parents=True)
    (real / "d" / "f").write_text("x\n")
    pr = tmp_path / "pr"
    pr.mkdir()
    (pr / "stage").symlink_to(real)
    try:
        CI.seal_tree(pr / "stage")
        refused = False
    except CI.ContainmentRefused:
        refused = True
    mode = stat.S_IMODE((real / "d" / "f").stat().st_mode)
    for q in (real / "d" / "f", real / "d", real):
        q.chmod(0o755 if q.is_dir() else 0o644)
    assert refused and mode & 0o200, (refused, oct(mode))
    with pytest.raises(CI.ContainmentRefused):
        CI.seal_tree(pr, "stage")
    assert stat.S_IMODE((real / "d" / "f").stat().st_mode) & 0o200
    os.unlink(pr / "stage")
    os.rename(real, pr / "stage")
    got = CI.seal_tree(pr, "stage")
    assert got == {"d/": "folder", "d/f": hashlib.sha256(b"x\n").hexdigest()}
    assert not ((pr / "stage" / "d" / "f").stat().st_mode & 0o222) and not ((pr / "stage").stat().st_mode & 0o222)
    for p in (pr / "stage" / "d", pr / "stage"):
        p.chmod(0o755)


# --- REVW5's B152 read of stage E2d: findings carried in with its falsifiers ------------------------------------

def _helper(bin_, name, env_key):
    h = bin_ / name
    h.write_text("#!/usr/bin/env python3\nimport os, sys\nfrom pathlib import Path\n"
                 f"p = Path(os.environ['{env_key}'])\n"
                 "for line in sys.stdin:\n"
                 "    p.open('a').write(line)\n"
                 "    if line.startswith('capabilities'): print('push\\n', flush=True)\n"
                 "    elif line.startswith('list'): print('', flush=True)\n"
                 "    elif line.startswith('push '): print('ok ' + line.strip().split(':')[-1] + '\\n', flush=True)\n")
    h.chmod(0o755)


@pytest.mark.parametrize("route", ["named_remote", "dead_url_alias"])
def test_b152_1_the_dead_url_cannot_start_an_inherited_helper(tmp_path, route):
    """B152 finding 1 (REVW5's falsifier, and the remove route's admitted dead-URL alias, B151 #3). With a synthetic
    `git-remote-no-push` on PATH and no empty allow-list (the kit's own git acts run outside sessions), a push from an
    isolated copy by its named remote, or by an inherited alias resolving to the dead URL, must not start the helper.
    On stage E2d isolation returned None and the push started the helper and exited 0."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    sentinel = tmp_path / "helper.txt"
    _helper(bin_, "git-remote-no-push", "KIT_TEST_HELPER")
    env = {**os.environ, "PATH": str(bin_) + os.pathsep + os.environ["PATH"], "KIT_TEST_HELPER": str(sentinel)}
    env.pop("GIT_ALLOW_PROTOCOL", None)
    if route == "named_remote":
        subprocess.run(["git", "-C", str(m), "remote", "add", "origin", str(tmp_path / "unused.git")], check=True)
        why = CI.isolate(m, "no-push", env, member=True)
        target = "origin"
    else:
        config = tmp_path / "global"
        config.write_text(f'[url "{CI.NO_PUSH_URL}"]\n insteadOf = unused-alias:\n')
        env["GIT_CONFIG_GLOBAL"] = str(config)
        why = CI.isolate(m, "remove", env, member=True)
        target = "unused-alias:x"
    assert why is None, why                       # isolation succeeds; the scheme is closed in the copy
    p = _run_git(m, "push", target, "HEAD:refs/heads/main", env=env)
    assert not sentinel.exists() and p.returncode != 0, (p.returncode, p.stderr,
                                                         sentinel.read_text() if sentinel.exists() else None)


@pytest.mark.parametrize("override", ["allow_protocol_env", "config_env"])
def test_b152_1_an_environment_that_reopens_the_dead_scheme_is_refused(tmp_path, override):
    """B152 finding 1, the override the closure depends on: an inherited `GIT_ALLOW_PROTOCOL` naming the scheme (git
    then ignores protocol.<name>.allow), or a `GIT_CONFIG_*` entry setting it back to `always`, makes isolation refuse."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_CONFIG_") and k != "GIT_ALLOW_PROTOCOL"}
    if override == "allow_protocol_env":
        env["GIT_ALLOW_PROTOCOL"] = "file:no-push"
    else:
        env.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "protocol.no-push.allow",
                    "GIT_CONFIG_VALUE_0": "always"})
    why = CI.isolate(m, "remove", env, member=True)
    assert why and "no-push" in why, why


def test_b152_1_other_local_transports_are_left_open_for_the_suite_check(tmp_path):
    """B152 finding 1, control for the scope of the closure: only the dead scheme is closed. A clone from the isolated
    copy by local path still works (the suite check at the commit runs members' local transport tests)."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    env = {k: v for k, v in os.environ.items() if k != "GIT_ALLOW_PROTOCOL"}
    assert CI.isolate(m, "remove", env, member=True) is None
    c = subprocess.run(["git", "-C", str(m), "clone", "-q", str(m), str(tmp_path / "c")], env=env,
                       capture_output=True, text=True)
    assert c.returncode == 0, c.stderr


def test_b152_4_seal_folder_refuses_parent_escape(tmp_path):
    """B152 finding 4 (REVW5's falsifier). `seal_folder(root, "../outside")` is refused before anything is opened, the
    outside mode unchanged. On stage E2d the walk opened `..` and the sibling went 0755 -> 0555."""
    CI = load("copy_isolation")
    root = tmp_path / "root"
    root.mkdir()
    outside = tmp_path / "outside"
    outside.mkdir()
    outside.chmod(0o755)
    try:
        CI.seal_folder(root, "../outside")
        refused = False
    except CI.ContainmentRefused:
        refused = True
    after = stat.S_IMODE(outside.stat().st_mode)
    outside.chmod(0o755)
    assert refused and after == 0o755, (refused, oct(after))


# --- REVW5's B153 read of stage E2e ------------------------------------------------------------------------------

@pytest.mark.parametrize("route", ["no-push", "remove"])
def test_b153_1_a_dormant_conditional_include_cannot_reopen_the_dead_scheme(tmp_path, route):
    """B153 finding 1 (REVW5's falsifier). An existing `protocol.no-push.allow` entry placed before a dormant
    `includeIf "onbranch:later"` whose file says `always`: after isolation and an ordinary checkout of `later`, a push
    by the named remote (or the remove route's admitted dead-URL alias) must not start the helper. On stage E2e
    isolation set `never` at the existing entry, before the include; the checkout activated `always`; the helper ran."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    assert _run_git(m, "branch", "later").returncode == 0
    assert _run_git(m, "remote", "add", "origin", str(tmp_path / "unused.git")).returncode == 0
    conditional = tmp_path / "conditional.config"
    conditional.write_text('[protocol "no-push"]\n allow = always\n')
    with (m / ".git" / "config").open("a") as f:
        f.write(f'[protocol "no-push"]\n allow = user\n[includeIf "onbranch:later"]\n path = {conditional}\n')
    bin_ = tmp_path / "bin"
    bin_.mkdir()
    sentinel = tmp_path / "helper.txt"
    _helper(bin_, "git-remote-no-push", "KIT_TEST_HELPER")
    env = {**os.environ, "PATH": str(bin_) + os.pathsep + os.environ["PATH"], "KIT_TEST_HELPER": str(sentinel)}
    env.pop("GIT_ALLOW_PROTOCOL", None)
    if route == "remove":
        g = tmp_path / "global"
        g.write_text(f'[url "{CI.NO_PUSH_URL}"]\n insteadOf = unused-alias:\n')
        env["GIT_CONFIG_GLOBAL"] = str(g)
    why = CI.isolate(m, route, env, member=True)
    if why is not None:                           # E2e3: an onbranch include is refused at isolation (B154 #1)
        assert "onbranch" in why, why
        return
    assert _run_git(m, "checkout", "-q", "later", env=env).returncode == 0
    p = _run_git(m, "push", "origin" if route == "no-push" else "unused-alias:x", "HEAD:refs/heads/main", env=env)
    assert not sentinel.exists() and p.returncode != 0, (p.returncode, p.stderr,
                                                         sentinel.read_text() if sentinel.exists() else None)


@pytest.mark.parametrize("scope", ["command", "worktree"])
def test_b153_1_an_include_read_after_the_copys_own_config_is_refused(tmp_path, scope):
    """B153 finding 1, the scopes git reads after the copy's own file: an include (here conditional) given through
    the environment, or in a worktree configuration, could reopen the scheme later; isolation refuses. On stage E2e
    both were accepted (the scheme read `never` until the condition held)."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    conditional = tmp_path / "conditional.config"
    conditional.write_text('[protocol "no-push"]\n allow = always\n')
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_CONFIG_") and k != "GIT_ALLOW_PROTOCOL"}
    if scope == "command":
        env.update({"GIT_CONFIG_COUNT": "1", "GIT_CONFIG_KEY_0": "includeIf.onbranch:later.path",
                    "GIT_CONFIG_VALUE_0": str(conditional)})
    else:
        assert _run_git(m, "config", "extensions.worktreeConfig", "true").returncode == 0
        (m / ".git" / "config.worktree").write_text(f'[includeIf "onbranch:later"]\n path = {conditional}\n')
    why = CI.isolate(m, "remove", env, member=True)
    assert why and "includes another file" in why, why


def test_b153_1_an_include_in_the_copys_own_file_is_overridden_not_refused(tmp_path):
    """B153 finding 1, control: an include in the copy's own file stays (a member may use one); the kit's entry is
    written after it, so even an active include saying `always` is overridden and isolation succeeds."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    inc = tmp_path / "inc.config"
    inc.write_text('[protocol "no-push"]\n allow = always\n')
    with (m / ".git" / "config").open("a") as f:
        f.write(f'[include]\n path = {inc}\n')
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_CONFIG_") and k != "GIT_ALLOW_PROTOCOL"}
    assert CI.isolate(m, "remove", env, member=True) is None
    assert _run_git(m, "config", "--get", "protocol.no-push.allow", env=env).stdout.strip() == "never"


# --- REVW5's B154 read of stage E2e2 -----------------------------------------------------------------------------

def _clean_env(**extra):
    env = {k: v for k, v in os.environ.items() if not k.startswith("GIT_CONFIG_") and k != "GIT_ALLOW_PROTOCOL"}
    env.update(extra)
    return env


@pytest.mark.parametrize("scope", ["local", "global"])
def test_b154_1_a_dormant_url_rewrite_cannot_redirect_the_existing_named_remote(tmp_path, scope):
    """B154 finding 1 (REVW5's falsifier, and the same include in the operator's global configuration). A dormant
    `includeIf "onbranch:later"` names a file with `url.<bare>.insteadOf = <the dead URL>`. Isolation must refuse,
    or the push by `origin` after an ordinary checkout must not land. On stage E2e2 isolation passed and, after the
    checkout, `origin` resolved to the bare repository and the push landed."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    head = git_member(m)
    assert _run_git(m, "branch", "later").returncode == 0
    assert _run_git(m, "remote", "add", "origin", str(tmp_path / "unused.git")).returncode == 0
    bare = tmp_path / "bare.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    rewrite = tmp_path / "rewrite.config"
    rewrite.write_text(f'[url "{bare}"]\n insteadOf = {CI.NO_PUSH_URL}\n')
    inc = f'[includeIf "onbranch:later"]\n path = {rewrite}\n'
    env = _clean_env()
    if scope == "local":
        with (m / ".git" / "config").open("a") as f:
            f.write(inc)
    else:
        g = tmp_path / "global"
        g.write_text(inc)
        env["GIT_CONFIG_GLOBAL"] = str(g)
    why = CI.isolate(m, "no-push", env, member=True)
    if why is None:
        assert _run_git(m, "checkout", "-q", "later", env=env).returncode == 0
        _run_git(m, "push", "origin", "HEAD:refs/heads/review", env=env)
    landed = _run_git(bare, "rev-parse", "refs/heads/review")
    assert landed.returncode != 0, (why, landed.stdout.strip(), head)
    assert why and "onbranch" in why and "gitdir:" in why, why   # the message names the remedy


def test_b154_1_a_hasconfig_include_is_refused(tmp_path):
    """B154 finding 1, the other state-dependent condition: `includeIf "hasconfig:remote.*.url:…"` follows
    configuration, which code can change after isolation; refused. On stage E2e2 isolation passed."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    (tmp_path / "x.config").write_text("[user]\n name = x\n")
    with (m / ".git" / "config").open("a") as f:
        f.write(f'[includeIf "hasconfig:remote.*.url:https://example.invalid/**"]\n path = {tmp_path / "x.config"}\n')
    why = CI.isolate(m, "remove", _clean_env(), member=True)
    assert why and "hasconfig" in why, why


def test_b154_1_an_include_whose_target_is_inside_the_copy_is_refused(tmp_path):
    """B154 finding 1, (b): an unconditional include whose file is in the copy's working tree (`../shared.gitconfig`
    from `.git/`) changes with a checkout; refused. On stage E2e2 isolation passed."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    (m / "shared.gitconfig").write_text("[user]\n name = x\n")
    with (m / ".git" / "config").open("a") as f:
        f.write('[include]\n path = ../shared.gitconfig\n')
    why = CI.isolate(m, "remove", _clean_env(), member=True)
    assert why and "inside the copy" in why, why


def test_b154_1_a_gitdir_include_outside_the_copy_is_admitted(tmp_path):
    """B154 finding 1, control: the common operator form, a global `includeIf "gitdir:…"` for identity, with its file
    outside the copy, is admitted (its condition cannot change for a copy that does not move)."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    ident = tmp_path / "work.gitconfig"
    ident.write_text("[user]\n email = w@example.invalid\n")
    g = tmp_path / "global"
    g.write_text(f'[includeIf "gitdir:{tmp_path}/"]\n path = {ident}\n')
    assert CI.isolate(m, "remove", _clean_env(GIT_CONFIG_GLOBAL=str(g)), member=True) is None


def test_b154_1_the_routes_are_read_again_after_a_kit_checkout(tmp_path, monkeypatch):
    """B154 finding 1, (c): after a checkout the kit makes in a copy (here the repair rehearsal's), the push routes
    are read again; a route that appeared after isolation (a rewrite of the dead URL to a real repository, standing
    in for any configuration change) is a refusal. On stage E2e2 the checkout asked LINKS only and returned None."""
    CI = load("copy_isolation")
    RR = load("rehearse_repair")
    m = tmp_path / "m"
    head = git_member(m)
    assert CI.isolate(m, "remove", _clean_env(), member=True) is None
    monkeypatch.setattr(os, "environ", _clean_env())
    bare = tmp_path / "bare.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    assert _run_git(m, "config", f"url.{bare}.insteadOf", CI.NO_PUSH_URL).returncode == 0
    assert _run_git(m, "config", "remote.pushDefault", CI.NO_PUSH_URL).returncode == 0
    why = RR.checkout(m, head)
    assert why and "push" in why, why


@pytest.mark.parametrize("query", ["include_scope", "url_rules", "remote_list"])
def test_b154_2_a_failed_mandatory_inspection_is_a_refusal(tmp_path, monkeypatch, query):
    """B154 finding 2 (REVW5's falsifier for the include query, and the class: the URL-rule and remote listings the
    route check reads). A mandatory query that fails (exit 129, empty output) is a refusal with its reason, never an
    empty answer. On stage E2e2 each failure read as "nothing found" and isolation returned None."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    real = CI._git
    match = {"include_scope": lambda a: "--show-scope" in a,
             "url_rules": lambda a: "--get-regexp" in a and any("insteadof" in x for x in a),
             "remote_list": lambda a: list(a) == ["remote"]}[query]

    def fake(repo, env, *args):
        if match(args):
            return subprocess.CompletedProcess(args, 129, "", "fatal: synthetic inspection failure\n")
        return real(repo, env, *args)
    monkeypatch.setattr(CI, "_git", fake)
    why = CI.isolate(m, "remove", _clean_env(), member=True)
    assert why and ("failed" in why or "synthetic" in why), why


# --- REVW5's B155 read of stage E2e3 -----------------------------------------------------------------------------

@pytest.mark.parametrize("home", ["inside_copy", "outside_copy"])
def test_b155_1_a_tilde_include_is_resolved_with_the_home_git_uses(tmp_path, home):
    """B155 finding 1 (REVW5's falsifier, with its control). A global `include.path = ~/route.cfg`: with git's HOME
    (the `env` it runs with) inside the copy, the file git reads is in the copy and isolation refuses; with git's HOME
    outside, the include is admitted. On stage E2e3 `~` was expanded with this process's HOME and the inside case
    passed."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    h = m if home == "inside_copy" else tmp_path / "home"
    h.mkdir(exist_ok=True)
    (h / "route.cfg").write_text('[user]\n name = x\n')
    g = tmp_path / "global"
    g.write_text('[include]\n path = ~/route.cfg\n')
    env = _clean_env(HOME=str(h), GIT_CONFIG_GLOBAL=str(g), GIT_CONFIG_NOSYSTEM="1")
    why = CI.isolate(m, "remove", env, member=True)
    if home == "inside_copy":
        assert why and "inside the copy" in why, why
    else:
        assert why is None, why


@pytest.mark.parametrize("which", ["alias", "named_remote"])
def test_b155_2_a_failed_route_resolution_is_a_refusal(tmp_path, monkeypatch, which):
    """B155 finding 2 (REVW5's falsifier for the alias branch; the named-remote branch is the same class). A failed
    resolution of a push route is a refusal, never the raw name. REVW5's fixture: a global rewrite maps the dead URL to
    a path, so the dead URL is an alias candidate; `ls-remote --get-url` fails. On stage E2e3 the alias branch fell
    back to the raw dead URL (allowed) and isolation returned None. The named-remote case is a control (E2e3 already
    refused it through an "unreadable" sentinel; E2e4 raises InspectionFailed in both branches)."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    g = tmp_path / "global"
    g.write_text(f'[url "{tmp_path}/synthetic-remote.git"]\n insteadOf = {CI.NO_PUSH_URL}\n')
    env = _clean_env(GIT_CONFIG_GLOBAL=str(g), GIT_CONFIG_NOSYSTEM="1")
    route = "no-push" if which == "named_remote" else "remove"
    if which == "named_remote":
        assert _run_git(m, "remote", "add", "origin", str(tmp_path / "unused.git")).returncode == 0
        g.write_text("")
    assert which == "named_remote" or CI.isolate(m, route, env, member=True)   # native: refused (the rewrite)
    real = CI._git
    target = ("ls-remote", "--get-url") if which == "alias" else ("remote", "get-url")

    def fake(repo, env_, *args):
        if args[:2] == target and (which == "alias" or "--push" in args):
            return subprocess.CompletedProcess(args, 129, "", "fatal: synthetic route resolution failure\n")
        return real(repo, env_, *args)
    monkeypatch.setattr(CI, "_git", fake)
    m2 = tmp_path / "m2"
    git_member(m2)
    if which == "named_remote":
        assert _run_git(m2, "remote", "add", "origin", str(tmp_path / "unused.git")).returncode == 0
    why = CI.isolate(m2, route, env, member=True)
    assert why, why            # named_remote is a control: E2e3 already refused it (an "unreadable" sentinel)


# --- REVW5's B156 read of stage E2e4 -----------------------------------------------------------------------------

@pytest.mark.parametrize("route", ["remove", "no-push"])
def test_b156_1_a_push_only_rewrite_of_the_dead_url_is_resolved_as_a_push(tmp_path, route):
    """B156 finding 1 (REVW5's falsifier). An inherited `url.<bare>.pushInsteadOf = <dead URL>`, with
    `remote.pushDefault = <dead URL>` and `push.default = current`: isolation must refuse, or a plain `git push` must
    not land. On stage E2e4 the candidate was resolved as a fetch URL (`ls-remote --get-url`, which ignores
    pushInsteadOf), isolation passed, and the plain push landed the current branch in the bare repository."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    if route == "no-push":
        assert _run_git(m, "remote", "add", "origin", str(tmp_path / "unused.git")).returncode == 0
    bare = tmp_path / "bare.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    g = tmp_path / "global"
    g.write_text(f'[url "{bare}"]\n pushInsteadOf = {CI.NO_PUSH_URL}\n[remote]\n pushDefault = {CI.NO_PUSH_URL}\n'
                 '[push]\n default = current\n')
    env = _clean_env(GIT_CONFIG_GLOBAL=str(g), GIT_CONFIG_NOSYSTEM="1")
    why = CI.isolate(m, route, env, member=True)
    branch = _run_git(m, "rev-parse", "--abbrev-ref", "HEAD").stdout.strip()
    if why is None:
        _run_git(m, "push", env=env)
    landed = _run_git(bare, "rev-parse", f"refs/heads/{branch}")
    assert landed.returncode != 0, (why, landed.stdout.strip())
    assert why and "push" in why, why
    assert not any("kit-route-probe" in ln for ln in _run_git(m, "config", "--local", "--list").stdout.splitlines())


@pytest.mark.parametrize("home", ["empty", "unset"])
def test_b156_2_an_empty_or_missing_git_home_is_not_replaced_by_this_processs_home(tmp_path, home):
    """B156 finding 2 (REVW5's falsifier for the empty HOME; the missing HOME is the same class). With git's HOME
    empty, `~/<copy>/route.cfg` names `/<copy>/route.cfg`, a file inside the copy: refused. With no HOME at all, git
    cannot expand `~`: refused rather than guessed. On stage E2e4 both used this process's HOME and passed."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    (m / "route.cfg").write_text("[user]\n name = x\n")
    g = tmp_path / "global"
    g.write_text(f'[include]\n path = ~{m.resolve()}/route.cfg\n')
    env = _clean_env(GIT_CONFIG_GLOBAL=str(g), GIT_CONFIG_NOSYSTEM="1")
    if home == "empty":
        env["HOME"] = ""
    else:
        env.pop("HOME", None)
    why = CI.isolate(m, "remove", env, member=True)
    if home == "empty":
        assert why and "inside the copy" in why, why
    else:                      # git itself rejects the unexpandable include (a bad config line): refused either way
        assert why, why


def test_b156_3_a_quoted_config_origin_is_decoded_before_a_relative_include_is_resolved(tmp_path):
    """B156 finding 3 (REVW5's falsifier). A global config in a folder whose name holds a tab includes
    `member/route.cfg`, a file inside the copy. Git's display form quotes that origin; the check must use the real
    file name and refuse. On stage E2e4 the quoted name was taken literally, its parent was another path, and the
    include was admitted."""
    CI = load("copy_isolation")
    d = tmp_path / "folder\tquoted"
    d.mkdir()
    m = d / "member"
    git_member(m)
    (m / "route.cfg").write_text("[user]\n name = x\n")
    g = d / "global"
    g.write_text('[include]\n path = member/route.cfg\n')
    why = CI.isolate(m, "remove", _clean_env(GIT_CONFIG_GLOBAL=str(g), GIT_CONFIG_NOSYSTEM="1"), member=True)
    assert why and "inside the copy" in why, why


# --- REVW6's B157 read of stage E2e5 -----------------------------------------------------------------------------

@pytest.mark.parametrize("character", ["\r", "\r\n", "\n"], ids=["cr", "crlf", "lf"])
@pytest.mark.parametrize("point", ["isolate", "after_checkout"])
def test_b157_1_an_unusual_origin_name_is_kept_byte_for_byte(tmp_path, character, point):
    """B157 finding 1 (REVW6's falsifier; LF is its control). A global config in a folder whose name holds a carriage
    return (or CRLF) includes `member/route.cfg`, which reaches a file inside the copy through a link: refused at
    isolation and at the after-checkout check. On stage E2e5 the listing was decoded in text mode, the CR became LF,
    the origin's parent was another folder, and the include was admitted."""
    CI = load("copy_isolation")
    folder = tmp_path / ("origin" + character + "name")
    folder.mkdir()
    m = tmp_path / "member"
    git_member(m)
    (folder / "member").symlink_to(m, target_is_directory=True)
    if point == "after_checkout":
        assert CI.isolate(m, "remove", _clean_env(GIT_CONFIG_GLOBAL="/dev/null"), member=True) is None
    (m / "route.cfg").write_text("[user]\n name = synthetic\n")
    g = folder / "global"
    g.write_text("[include]\n path = member/route.cfg\n")
    env = _clean_env(GIT_CONFIG_GLOBAL=str(g))
    why = CI.isolate(m, "remove", env, member=True) if point == "isolate" else CI.checked_out_refusal(m, env=env)
    assert why and "inside the copy" in why, why


def test_b157_2_a_route_probe_never_reuses_or_deletes_an_existing_remote(tmp_path, monkeypatch):
    """B157 finding 2 (REVW6's falsifier). An existing remote with the probe's name (the name selector forced to it):
    the probe must not read that remote's `pushurl` or delete its section; it refuses, configuration unchanged. On
    stage E2e5 the probe returned the old pushurl and removed the pre-existing section."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    env = _clean_env(GIT_CONFIG_GLOBAL="/dev/null")
    name = "kit-route-probe-1234abcd"
    assert _run_git(m, "config", f"remote.{name}.url", str(tmp_path / "unused.git")).returncode == 0
    assert _run_git(m, "config", f"remote.{name}.pushurl", CI.NO_PUSH_URL).returncode == 0
    before = (m / ".git" / "config").read_bytes()
    monkeypatch.setattr(CI.secrets, "token_hex", lambda n: "1234abcd")
    with pytest.raises(CI.InspectionFailed):
        CI._push_urls_of(m, env, str(tmp_path / "different.git"))
    assert (m / ".git" / "config").read_bytes() == before


def test_b157_2_a_probe_collision_does_not_admit_a_push_only_rewrite(tmp_path, monkeypatch):
    """B157 finding 2 (REVW6's falsifier). An existing remote with the probe's name, an inherited push-only rewrite of
    the dead URL and `remote.pushDefault` the dead URL: isolation refuses, or a plain push does not land. On stage
    E2e5 isolation passed and the push landed the source HEAD in the bare repository."""
    CI = load("copy_isolation")
    m = tmp_path / "m"
    git_member(m)
    bare = tmp_path / "bare.git"
    subprocess.run(["git", "init", "-q", "--bare", str(bare)], check=True)
    g = tmp_path / "global"
    g.write_text(f'[url "{bare}"]\n pushInsteadOf = {CI.NO_PUSH_URL}\n[remote]\n pushDefault = {CI.NO_PUSH_URL}\n'
                 '[push]\n default = current\n')
    env = _clean_env(GIT_CONFIG_GLOBAL=str(g))
    assert _run_git(m, "remote", "add", "kit-route-probe-1234abcd", str(tmp_path / "unused.git")).returncode == 0
    monkeypatch.setattr(CI.secrets, "token_hex", lambda n: "1234abcd")
    why = CI.isolate(m, "no-push", env, member=True)
    branch = _run_git(m, "symbolic-ref", "HEAD").stdout.strip()
    if why is None:
        _run_git(m, "push", env=env)
    assert _run_git(bare, "rev-parse", branch).returncode != 0, why
    assert why, why


# --- REVW6's B159 read of stage E2e7 (finding 2) -----------------------------------------------------------------

@pytest.mark.parametrize("character", ["", "\r", "\t", "\n"], ids=["plain", "cr", "tab", "lf"])
def test_b159_2_pre_existing_files_in_an_untracked_folder_are_not_committed_in_the_copy(tmp_path, character):
    """B159 finding 2 (REVW6's falsifier). `old<c>/own.txt` exists, untracked, when B1's `pre_dirty` is taken; the
    migration then adds `new.txt`. The packet rehearsal's commit in the copy must take `new.txt` only. On stage E2e7
    `pre_dirty` was `['old<c>/']` (git's default untracked mode lists the folder), the commit set listed
    `old<c>/own.txt`, and the pre-existing file was committed (ordinary names too)."""
    PL = load("prepare_launch")
    B2 = load("rehearse_batch2")
    root = tmp_path / "copy"
    git_member(root)
    rel_name = "old" + character + "/own.txt"
    (root / rel_name).parent.mkdir()
    (root / rel_name).write_text("own\n")
    pre = PL.pre_dirty(str(root))
    (root / "new.txt").write_text("migration\n")
    assert load("copy_isolation").isolate(root, "remove", member=True, run=tmp_path) is None   # as the rehearsal does
    got = B2.commit_applied(root, {"pre_dirty": pre})
    tracked = [os.fsdecode(x) for x in subprocess.check_output(
        ["git", "-C", str(root), "ls-tree", "-r", "--name-only", "HEAD", "-z"]).split(b"\0") if x]
    assert rel_name not in tracked and got == ["new.txt"], (pre, got, tracked)


# --- E2f: R1 ENV (DESIGN R1-T3, R1-T15, R1-T16) ------------------------------------------------------------------

def _hook(repo, name, sentinel):
    h = repo / ".git" / "hooks" / name
    h.parent.mkdir(parents=True, exist_ok=True)
    h.write_text(f"#!/bin/sh\necho ran >> '{sentinel}'\n")
    h.chmod(0o755)


def test_r1_t15_a_copied_hook_does_not_run_in_the_kits_checkout_or_commit(tmp_path):
    """R1-T15. A copied `post-checkout` and `post-commit` hook that write a sentinel do not run during the repair
    rehearsal's checkout or the packet rehearsal's copy commit (`commit --no-verify` skips pre-commit only). At E2e7
    both ran (the kit's git acts ran with the copy's hooks in force)."""
    RR = load("rehearse_repair")
    B2 = load("rehearse_batch2")
    run = tmp_path / "run"
    copy = run / "m"
    head = git_member(copy)
    sentinel = tmp_path / "hook-ran.txt"
    for name in ("post-checkout", "post-commit"):
        _hook(copy, name, sentinel)
    assert load("copy_isolation").isolate(copy, "remove", member=True, run=run) is None   # as every caller does
    assert RR.checkout(copy, head) is None
    (copy / "new.txt").write_text("migration\n")
    assert B2.commit_applied(copy, {"pre_dirty": []}) == ["new.txt"]
    assert not sentinel.exists(), sentinel.read_text()


def test_r1_t16_member_code_in_a_copy_gets_the_contained_environment(tmp_path):
    """R1-T16. The environment the repair rehearsal gives a suite in a copy has GIT_CEILING_DIRECTORIES the folder
    holding the copy, CLAUDE_PROJECT_DIR the copy, and no operator git configuration. At E2e7 the suite ran with the
    caller's environment unchanged."""
    RR = load("rehearse_repair")
    run = tmp_path / "run"
    copy = run / "m"
    git_member(copy)
    assert load("copy_isolation").isolate(copy, "remove", member=True, run=run) is None   # as the rehearsal does
    probe = ("import os, json; print(json.dumps({k: os.environ.get(k) for k in "
             "('GIT_CEILING_DIRECTORIES', 'CLAUDE_PROJECT_DIR', 'GIT_CONFIG_GLOBAL', 'GIT_CONFIG_NOSYSTEM')}))")
    ev = tmp_path / "ev"
    ev.mkdir()
    RR.suite(copy, "env", ev, f"{sys.executable} -c \"{probe}\"")
    got = json.loads((ev / "env.txt").read_text().strip().splitlines()[0])
    assert got["GIT_CEILING_DIRECTORIES"] == str(run.resolve()) and got["CLAUDE_PROJECT_DIR"] == str(copy), got
    assert got["GIT_CONFIG_NOSYSTEM"] == "1" and got["GIT_CONFIG_GLOBAL"].startswith(str(run)), got


def test_r1_t3_git_in_a_plain_copied_sibling_finds_no_enclosing_repository(tmp_path):
    """R1-T3. With the work folder inside a git repository, `git rev-parse` in a copied plain sibling (no .git), under
    the suite check's environment, reports "not a git repository". At E2e7 it found the enclosing repository."""
    SC = load("suite_at_commit")
    outer = tmp_path / "outer"
    git_member(outer)
    base = outer / "work" / "a.root"
    dest = base / "a"
    git_member(dest)
    assert load("copy_isolation").isolate(dest, "no-push", url=SC.NO_PUSH_URL, member=True) is None   # as B8a does
    plain = base / "sib"
    plain.mkdir()
    (plain / "f.txt").write_text("x\n")
    p = subprocess.run(["git", "-C", str(plain), "rev-parse", "--show-toplevel"], capture_output=True, text=True,
                       env=SC.suite_env(dest))
    assert p.returncode != 0 and "not a git repository" in p.stderr, (p.returncode, p.stdout, p.stderr)


# --- REVW6's B160 read of stage E2f ------------------------------------------------------------------------------

def _rerouted_copy(tmp_path, monkeypatch, route, scope):
    """REVW6's fixture: a copy whose `remote.pushDefault` is a bare repository and `push.default=matching`, with the
    caller's global (or XDG) configuration rewriting that bare path to the kit's dead URL, so isolation reads the
    route as dead. Returns (CI, run, copy, bare, branch, head)."""
    CI = load("copy_isolation")
    run = tmp_path / "run"
    copy = run / "copy"
    git_member(copy)
    bare = tmp_path / "local.git"
    subprocess.run(["git", "init", "--bare", "-q", str(bare)], check=True)
    branch = _run_git(copy, "symbolic-ref", "--short", "HEAD").stdout.strip()
    for a in (("remote", "add", "origin", str(bare)), ("config", "remote.pushDefault", str(bare)),
              ("push", "-q", "origin", branch)):
        assert _run_git(copy, *a).returncode == 0, a
    (copy / "advance.txt").write_text("new copy commit\n")
    _run_git(copy, "add", "advance.txt")
    _run_git(copy, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "advance")
    head = _run_git(copy, "rev-parse", "HEAD").stdout.strip()
    assert _run_git(copy, "config", "push.default", "matching").returncode == 0
    cfg = tmp_path / "global.cfg" if scope == "global" else tmp_path / "xdg" / "git" / "config"
    cfg.parent.mkdir(parents=True, exist_ok=True)
    cfg.write_text(f'[url "{CI.NO_PUSH_URL}"]\n insteadOf = {bare}\n')
    if scope == "global":
        monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(cfg))
    else:
        monkeypatch.delenv("GIT_CONFIG_GLOBAL", raising=False)
        monkeypatch.setenv("XDG_CONFIG_HOME", str(tmp_path / "xdg"))
    assert CI.isolate(copy, route, member=True, run=run) is None   # the caller's configuration reads it as dead
    return CI, run, copy, bare, branch, head


@pytest.mark.parametrize("route", ["no-push", "remove"])
@pytest.mark.parametrize("scope", ["global", "xdg"])
def test_b160_1_the_contained_environment_does_not_reopen_a_route_isolation_read_as_dead(tmp_path, monkeypatch,
                                                                                       route, scope):
    """B160 finding 1 (REVW6's falsifier, the repair rehearsal's suite). Under the caller's configuration the route
    resolves to the dead URL; the suite's contained environment drops that rewrite. The suite must not run (or its
    plain `git push` must not land). On stage E2f the environment was not checked and the push advanced the bare
    repository to the copy's commit."""
    CI, run, copy, bare, branch, head = _rerouted_copy(tmp_path, monkeypatch, route, scope)
    RR = load("rehearse_repair")
    ev = tmp_path / "ev"
    ev.mkdir()
    res = RR.suite(copy, "push", ev, "git push")
    landed = _run_git(bare, "rev-parse", f"refs/heads/{branch}").stdout.strip()
    assert landed != head, (res, landed)
    assert res.get("ran") is False and "contained environment" in (ev / "push.txt").read_text(), res


@pytest.mark.parametrize("scope", ["global", "xdg"])
def test_b160_1_the_suite_check_at_the_commit_refuses_the_same_route(tmp_path, monkeypatch, scope):
    """B160 finding 1, at B8a: `suite_at_commit.run` with the clone step replaced by REVW6's isolated copy (the real
    suite path from there on): the suite does not run and nothing lands. On stage E2f the plain push landed."""
    CI, run, copy, bare, branch, head = _rerouted_copy(tmp_path, monkeypatch, "no-push", scope)
    SC = load("suite_at_commit")
    monkeypatch.setattr(SC, "clean_clone", lambda *a, **k: (copy, []))
    monkeypatch.setattr(SC, "ci_exclusions", lambda dest, cmd: ([], [], []))
    rec = SC.run(str(copy), "a", head, suite_cmd="git push", hook=False)
    landed = _run_git(bare, "rev-parse", f"refs/heads/{branch}").stdout.strip()
    assert landed != head, (rec.get("verdict"), rec.get("why"), landed)
    assert rec["verdict"] == "INCONCLUSIVE" and "not run" in rec["why"], rec


@pytest.mark.parametrize("act", ["checkout", "commit"])
def test_b160_2_a_populated_hooks_off_folder_is_refused(tmp_path, act):
    """B160 finding 2 (REVW6's falsifier). A file already in `.kit-env/nohooks` would run as a hook; the kit's checkout
    and copy commit refuse instead. On stage E2f git ran it (the sentinel read `ran`)."""
    CI = load("copy_isolation")
    RR = load("rehearse_repair")
    B2 = load("rehearse_batch2")
    run = tmp_path / "run"
    copy = run / "m"
    head = git_member(copy)
    assert CI.isolate(copy, "remove", member=True, run=run) is None
    sentinel = tmp_path / "ran.txt"
    nohooks = run / ".kit-env" / "nohooks"
    nohooks.mkdir(parents=True)
    for name in ("post-checkout", "post-commit"):
        (nohooks / name).write_text(f"#!/bin/sh\necho ran >> '{sentinel}'\n")
        (nohooks / name).chmod(0o755)
    if act == "checkout":
        why = RR.checkout(copy, head)
        assert why and "not empty" in why, why
    else:
        (copy / "new.txt").write_text("x\n")
        with pytest.raises(B2.CopyStepFailed, match="not empty"):
            B2.commit_applied(copy, {"pre_dirty": []})
    assert not sentinel.exists()


def test_b160_3_a_relative_copy_path_gives_absolute_environment_paths(tmp_path, monkeypatch):
    """B160 finding 3 (REVW6's falsifier). A copy named by a relative path: every path in the environment is absolute
    and names the real files, as a child started in the copy sees them. On stage E2f the child resolved them under
    `<copy>/run/copy/…`."""
    RR = load("rehearse_repair")
    monkeypatch.chdir(tmp_path)
    git_member(tmp_path / "run" / "copy")
    env = RR.code_env(Path("run/copy"))      # the repair rehearsal's suite environment (REVW6's entry point)
    for k in ("CLAUDE_PROJECT_DIR", "GIT_CONFIG_GLOBAL", "XDG_CONFIG_HOME", "GIT_CONFIG_VALUE_0"):
        assert os.path.isabs(env[k]), (k, env[k])
    assert Path(env["CLAUDE_PROJECT_DIR"]) == tmp_path / "run" / "copy"
    assert Path(env["GIT_CONFIG_GLOBAL"]).is_file()


@pytest.mark.parametrize("state", ["added", "modified"])
def test_b160_4_the_copy_commit_does_not_sweep_pre_existing_staged_work(tmp_path, state):
    """B160 finding 4 (REVW6's falsifier). `own.txt` staged (added, or modified and staged) before B1's `pre_dirty`;
    the migration adds `new.txt`. The copy commit takes `new.txt` only and leaves `own.txt` staged. On stage E2f (and
    E2e7) the unbounded commit took both and the returned list said `['new.txt']`."""
    CI = load("copy_isolation")
    PL = load("prepare_launch")
    B2 = load("rehearse_batch2")
    root = tmp_path / "copy"
    git_member(root)
    if state == "modified":
        (root / "own.txt").write_text("v1\n")
        _run_git(root, "add", "own.txt")
        _run_git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "own v1")
    (root / "own.txt").write_text("own work\n")
    _run_git(root, "add", "own.txt")
    pre = PL.pre_dirty(str(root))
    before = _run_git(root, "rev-parse", "HEAD").stdout.strip()
    (root / "new.txt").write_text("migration\n")
    assert CI.isolate(root, "remove", member=True, run=tmp_path) is None
    assert B2.commit_applied(root, {"pre_dirty": pre}) == ["new.txt"]
    committed = [os.fsdecode(x) for x in subprocess.check_output(
        ["git", "-C", str(root), "diff", "--name-only", "-z", before, "HEAD"]).split(b"\0") if x]
    assert committed == ["new.txt"], committed


# --- REVW6's B161 read of stage E2f2 -----------------------------------------------------------------------------

@pytest.mark.parametrize("staged", [True, False], ids=["staged", "unstaged"])
@pytest.mark.parametrize("character", ["", "\t"], ids=["plain", "tab"])
def test_b161_1_a_renamed_file_is_committed_with_both_endpoints(tmp_path, staged, character):
    """B161 finding 1 (REVW6's falsifier). A tracked `old<c>.txt` renamed to `new<c>.txt` by the migration (staged with
    `git mv`, or a plain rename): the copy commit takes both endpoints, and the read-back agrees. On stage E2f2 the
    staged case committed only the destination (the source stayed in HEAD) and the unstaged case was refused."""
    CI = load("copy_isolation")
    B2 = load("rehearse_batch2")
    root = tmp_path / "copy"
    git_member(root)
    old, new = f"old{character}.txt", f"new{character}.txt"
    (root / old).write_text("x\n")
    _run_git(root, "add", "--", old)
    _run_git(root, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "old")
    assert CI.isolate(root, "remove", member=True, run=tmp_path) is None
    if staged:
        assert _run_git(root, "mv", "--", old, new).returncode == 0
    else:
        (root / old).rename(root / new)
    got = B2.commit_applied(root, {"pre_dirty": []})
    tree = [os.fsdecode(x) for x in subprocess.check_output(
        ["git", "-C", str(root), "ls-tree", "-r", "--name-only", "-z", "HEAD"]).split(b"\0") if x]
    assert sorted(got) == sorted([old, new]) and new in tree and old not in tree, (got, tree)


@pytest.mark.parametrize("name,own", [("new*.txt", "new-own.txt"), ("new?.txt", "newx.txt"), ("[ab].txt", "a.txt")])
def test_b161_2_a_migration_file_name_is_a_literal_path_not_a_pattern(tmp_path, name, own):
    """B161 finding 2 (REVW6's falsifier). Pre-existing staged work in `own`, and a migration file whose name is a
    pathspec pattern matching it: the copy commit takes the literal file only and leaves `own` staged. On stage E2f2
    (and E2f) `add`/`commit -- <paths>` expanded the pattern and committed the member's own work."""
    CI = load("copy_isolation")
    PL = load("prepare_launch")
    B2 = load("rehearse_batch2")
    root = tmp_path / "copy"
    git_member(root)
    (root / own).write_text("own\n")
    _run_git(root, "add", "--", own)
    pre = PL.pre_dirty(str(root))
    before = _run_git(root, "rev-parse", "HEAD").stdout.strip()
    (root / name).write_text("migration\n")
    assert CI.isolate(root, "remove", member=True, run=tmp_path) is None
    assert B2.commit_applied(root, {"pre_dirty": pre}) == [name]
    committed = [os.fsdecode(x) for x in subprocess.check_output(
        ["git", "-C", str(root), "diff", "--name-only", "-z", before, "HEAD"]).split(b"\0") if x]
    assert committed == [name], committed


# --- Stage E2g: per-run folders under a work root (R1 clause 5), R1-T1, R1-T2 (c) and (d), the auditor path ------

def test_e2g_each_clone_gets_its_own_run_folder_and_an_earlier_one_is_kept(tmp_path):
    """R1 clause 5 (RUN = mkdtemp(dir=W)). Two suite checks at the commit with the same work root: each clones into
    its own run folder, and the first clone is still there after the second. On stage E2f2 both used
    `<work>/<aget>.root`, and the second run removed the first's folder (the shared-folder collision and the
    cross-run removal the design names)."""
    SC = load("suite_at_commit")
    loc = tmp_path / "m"
    sha = git_member(loc)
    first, why = SC.clean_clone(loc, "m", sha, [], tmp_path / "work")
    assert why == [] and first is not None
    (first / "marker.txt").write_text("first run\n")
    second, why = SC.clean_clone(loc, "m", sha, [], tmp_path / "work")
    assert second is not None and second != first, (first, second)
    assert (first / "marker.txt").read_text() == "first run\n"


def test_e2g_a_work_root_inside_a_repository_is_refused_before_anything_is_made(tmp_path):
    """R1 clause 5 and R1-T3's precondition. A work root inside any git repository is refused, and nothing is made in
    it. On stage E2f2 a work folder inside the member itself was accepted (`inside_ok`) and the clone was made in the
    member's working tree."""
    SC = load("suite_at_commit")
    loc = tmp_path / "m"
    sha = git_member(loc)
    clone, why = SC.clean_clone(loc, "m", sha, [], loc / "work")
    assert clone is None and "lies inside the git repository" in why, why
    assert not (loc / "work").exists()
    assert _run_git(loc, "status", "--porcelain").stdout == ""


def test_r1_t1_a_scratch_inside_a_declared_sibling_source_is_refused_and_the_sibling_is_unchanged(tmp_path):
    """R1-T1. The packet rehearsal's copy with a declared sibling `../sib`, and a scratch folder inside that sibling's
    live folder: refused before anything is removed or copied, and the sibling's bytes are unchanged. On stage E2f2
    `place_refusal` tested the member only, and the rehearsal removed `<scratch>/<aget>.root` inside the sibling (and
    then copied the sibling into its own tree)."""
    B2 = load("rehearse_batch2")
    home = tmp_path / "home"
    loc = home / "m"
    git_member(loc)
    sib = home / "sib"
    (sib / "scr" / "m.root").mkdir(parents=True)
    (sib / "f.txt").write_text("sibling\n")
    keep = sib / "scr" / "m.root" / "keep.txt"
    keep.write_text("keep\n")
    try:
        B2.copy_of({"aget": "m", "location": str(loc)}, sib / "scr", ["../sib"])
        raised = None
    except Exception as e:                                  # noqa: BLE001 — the old route may fail any way
        raised = e
    assert keep.exists(), "the rehearsal removed a folder inside the live sibling"
    assert isinstance(raised, ValueError) and "live sibling folder" in str(raised), raised
    assert sorted(p.name for p in sib.rglob("*")) == ["f.txt", "keep.txt", "m.root", "scr"]


def test_r1_t1_a_confirm_folder_inside_a_repository_is_refused(tmp_path):
    """R1-T1. F's confirmation run given a confirm folder inside a git repository (another one than the receiver's):
    refused before anything is cloned there. On stage E2f2 it was accepted and the receiver was cloned inside that
    repository's working tree."""
    A = load("after_run_check")
    root = tmp_path / "home" / "m"
    head = git_member(root)
    other = tmp_path / "other"
    git_member(other)
    still, passed, why = A.confirm_at_head(root, "m", ["tests/t.py::test_t"], [], other / "wk", head)
    assert still == [] and passed == [] and why and "lies inside the git repository" in why, why
    assert not (other / "wk").exists() and _run_git(other, "status", "--porcelain").stdout == ""


def _copy_root_launch(tmp_path, monkeypatch, hook_target="../../scripts/pre-commit"):
    """An isolated, marked rehearsal copy with `.git/hooks/pre-commit -> hook_target`, launched by run_one with a
    stubbed session that runs `git commit` in the copy under the environment it is given, a stub watcher and a stub
    after-run check that records its arguments. Returns (record, session env, check argv, copy)."""
    LB = load("launch_batch")
    monkeypatch.setattr(LB, "launch_rules_refusal", lambda r, packet: None)   # D2 (labelled): minimal receivers, no items; the rules recompute has its own row
    CI = load("copy_isolation")
    run = tmp_path / "run"
    copy = run / "m"
    head = git_member(copy)
    (copy / "scripts").mkdir()
    (copy / "scripts" / "pre-commit").write_text("#!/bin/sh\ntouch hook_ran\n")
    (copy / "scripts" / "pre-commit").chmod(0o755)
    (copy / ".git" / "hooks").mkdir(exist_ok=True)
    (copy / ".git" / "hooks" / "pre-commit").symlink_to(hook_target)
    assert CI.isolate(copy, "remove", member=True, run=copy) is None          # as rehearse_v37 does
    settings = tmp_path / "settings.json"
    settings.write_text("{}\n")
    stub = tmp_path / "stub.py"
    stub.write_text("import json, sys\nopen(sys.argv[0] + '.argv.json', 'w').write(json.dumps(sys.argv[1:]))\n")
    monkeypatch.setattr(LB, "WATCHER", stub)
    monkeypatch.setattr(LB, "CHECK", stub)
    monkeypatch.setattr(LB.time, "sleep", lambda *a: None)
    seen = {}

    def session(cmd, cwd, env, timeout):
        seen["env"] = dict(env)
        subprocess.run(["git", "-C", str(cwd), "commit", "-q", "--allow-empty", "-m", "session"], env=env,
                       capture_output=True, text=True)
        return subprocess.CompletedProcess(cmd, 0, "", "")
    monkeypatch.setattr(LB, "run_grouped", session)
    r = {"aget": "m", "location": str(copy), "head": head, "prompt": "p", "attempt": "1", "allowlist": [],
         "write_set": ["a.txt"], "allow_bash": [], "_copy_root": True,
         "settings": {"path": str(settings), "sha256": hashlib.sha256(settings.read_bytes()).hexdigest()}}
    packet = {"stage": str(tmp_path / "stage"), "tools": "Bash", "deny": [], "apply_receipt": str(tmp_path / "R"),
              "_path": str(tmp_path / "P.json")}
    ev = tmp_path / "ev"
    (ev / "m").mkdir(parents=True)
    (ev / "m" / "settings_snapshot_pre.json").write_text("{}\n")
    rec = LB.run_one(r, packet, ev)
    argv = json.loads((tmp_path / "stub.py.argv.json").read_text())
    return rec, seen.get("env"), argv, copy


def test_r1_t2c_the_session_rehearsal_runs_under_the_contained_environment_with_the_copys_hooks(tmp_path,
                                                                                              monkeypatch):
    """R1-T2 (c), clause 6(c). A rehearsal session in a copy (V3.7, --copy-root) runs under ENV with the copy's own
    hooks in force: git bounded by the folder holding the copy, no operator configuration, CLAUDE_PROJECT_DIR the copy,
    no transport; a `git commit` there runs the copy's pre-commit hook (linked into its own tree), whose sentinel lands
    inside the copy; and the after-run check is asked to re-run LINKS (--copy-run). On stage E2f2 the session got
    the live-session environment (no GIT_CEILING_DIRECTORIES, the operator's git configuration) and no LINKS after."""
    rec, env, argv, copy = _copy_root_launch(tmp_path, monkeypatch)
    assert env is not None
    assert env.get("GIT_CEILING_DIRECTORIES") == str(copy.parent.resolve()), env.get("GIT_CEILING_DIRECTORIES")
    assert env.get("CLAUDE_PROJECT_DIR") == str(copy) and env.get("GIT_CONFIG_NOSYSTEM") == "1"
    assert env.get("GIT_CONFIG_GLOBAL", "").startswith(str(copy.parent)) and env.get("GIT_ALLOW_PROTOCOL") == ""
    assert "core.hooksPath" not in [env.get(k) for k in env if k.startswith("GIT_CONFIG_KEY_")]
    assert (copy / "hook_ran").exists()
    assert "--copy-run" in argv and argv[argv.index("--copy-run") + 1] == str(copy), argv


def test_r1_t1_the_launchs_confirmation_folder_is_outside_the_kit(tmp_path, monkeypatch):
    """R1-T1 (confirm-dir). The confirmation folder the launch gives the after-run check lies outside this kit's own
    folder tree. On stage E2f2 it was `<kit repository>/workspace/.tmp/f_confirm`, inside the kit's working tree."""
    rec, env, argv, copy = _copy_root_launch(tmp_path, monkeypatch)
    confirm = Path(argv[argv.index("--confirm-dir") + 1]).resolve()
    assert ROOT.resolve() not in confirm.parents and confirm != ROOT.resolve(), confirm


def _hook_member(tmp_path, link):
    """A member with a passing test, `scripts/pre-push` committed (it prints `committed`) and then changed in the
    working tree only (it prints `live`), and `.git/hooks/pre-push -> link`."""
    loc = tmp_path / "m"
    git_member(loc)
    (loc / "tests").mkdir()
    (loc / "tests" / "test_a.py").write_text("def test_a():\n    assert True\n")
    (loc / "scripts").mkdir()
    (loc / "scripts" / "pre-push").write_text("#!/bin/sh\necho committed\n")
    (loc / "scripts" / "pre-push").chmod(0o755)
    _run_git(loc, "add", "-A")
    _run_git(loc, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "hook")
    sha = _run_git(loc, "rev-parse", "HEAD").stdout.strip()
    (loc / "scripts" / "pre-push").write_text("#!/bin/sh\necho live\n")
    (loc / ".git" / "hooks").mkdir(exist_ok=True)
    (loc / ".git" / "hooks" / "pre-push").symlink_to(link)
    return loc, sha


def test_r1_t2d_a_hook_linked_into_the_members_tree_runs_the_bytes_at_the_tested_commit(tmp_path):
    """R1-T2 (d), clause 6(b). B8a with `pre-push -> ../../scripts/pre-push`: the hook that runs is a regular file in
    the clone whose bytes are `scripts/pre-push` at the tested commit (it prints `committed`), not the live working
    tree's (`live`). On stage E2f2 `is_file()` and `copy2` followed the link to the live file."""
    SC = load("suite_at_commit")
    loc, sha = _hook_member(tmp_path, "../../scripts/pre-push")
    rec = SC.run(loc, "m", sha, f"{sys.executable} -m pytest -q -p no:cacheprovider", work=tmp_path / "w")
    assert rec["hook"].get("present") and "committed" in rec["hook"].get("tail", ""), rec
    assert "live" not in rec["hook"].get("tail", "")
    placed, = (tmp_path / "w").glob("*/m.root/m/.git/hooks/pre-push")
    st = os.lstat(placed)
    assert stat.S_ISREG(st.st_mode) and st.st_nlink == 1


def test_r1_t2d_a_hook_linked_outside_the_member_is_not_run_and_reads_inconclusive(tmp_path):
    """R1-T2 (d). A pre-push link leading outside the member: the hook is not run and the result is INCONCLUSIVE
    ("hook present, not run"), never PASS. On stage E2f2 the link was followed, the outside script ran and the
    result read PASS."""
    SC = load("suite_at_commit")
    sentinel = tmp_path / "outside_ran"
    outside = tmp_path / "outside_hook.sh"
    outside.write_text(f"#!/bin/sh\ntouch '{sentinel}'\n")
    outside.chmod(0o755)
    loc, sha = _hook_member(tmp_path, str(outside))
    rec = SC.run(loc, "m", sha, f"{sys.executable} -m pytest -q -p no:cacheprovider", work=tmp_path / "w")
    assert not sentinel.exists()
    assert rec["verdict"] == "INCONCLUSIVE" and "hook present, not run" in rec["why"], rec


def _ratchet_copy(tmp_path):
    copy = tmp_path / "run" / "m"
    (copy / "tests").mkdir(parents=True)
    (copy / "tests" / "test_ratchet.py").write_text('KNOWN_MISSING = {\n    ("a", "scripts/a.py"),\n}\n')
    return copy


def test_e2g_the_known_missing_auditor_outside_the_run_and_the_kit_is_not_run(tmp_path):
    """The auditor path check (rehearse_batch2's known-missing emulation). An auditor path into the live receiver,
    outside the copy's run folder and the kit, is refused and not run. On stage E2f2 it ran with the copy as its
    working folder (its sentinel was written beside the live script)."""
    B2 = load("rehearse_batch2")
    copy = _ratchet_copy(tmp_path)
    live = tmp_path / "home" / "m"
    live.mkdir(parents=True)
    (live / "audit.py").write_text("import pathlib\npathlib.Path(__file__).with_name('ran').write_text('x')\n")
    r = {"known_missing_ruling": {"file": "tests/test_ratchet.py", "auditor": str(live / "audit.py"),
                                  "entries": []}}
    try:
        B2.emulate_known_missing(copy, r)
        raised = None
    except Exception as e:                                  # noqa: BLE001
        raised = e
    assert not (live / "ran").exists(), "the live auditor ran"
    assert raised is not None and "outside the copy's run folder" in str(raised), raised


def test_e2g_the_known_missing_auditor_runs_under_the_contained_environment(tmp_path):
    """The auditor in the copy runs under R1 ENV: git bounded by the copy's run folder, CLAUDE_PROJECT_DIR the copy.
    On stage E2f2 it ran with the caller's environment unchanged."""
    B2 = load("rehearse_batch2")
    copy = _ratchet_copy(tmp_path)
    (copy / "audit.py").write_text("import json, os\njson.dump({k: os.environ.get(k) for k in "
                                   "('GIT_CEILING_DIRECTORIES', 'CLAUDE_PROJECT_DIR')}, open('env.json', 'w'))\n")
    r = {"known_missing_ruling": {"file": "tests/test_ratchet.py", "auditor": "audit.py", "entries": []}}
    B2.emulate_known_missing(copy, r)
    got = json.loads((copy / "env.json").read_text())
    assert got == {"GIT_CEILING_DIRECTORIES": str(copy.parent.resolve()), "CLAUDE_PROJECT_DIR": str(copy)}, got


# --- REVW6's B162 read of stage E2g ------------------------------------------------------------------------------

@pytest.mark.parametrize("shape", ["absolute", "parent"])
@pytest.mark.parametrize("site", ["run_folder", "packet_copy", "B8a", "confirm"])
def test_b162_1_a_path_shaped_receiver_name_makes_nothing_outside_the_work_root(tmp_path, site, shape):
    """B162 finding 1 (REVW6's falsifier). A receiver name that is a path (absolute, or `../…`) makes no folder outside
    the work root: the run folder's prefix is a display prefix, and every producer refuses a name that is not one
    folder name before any folder is made for it. On stage E2g `mkdtemp`'s prefix and the producers' joins took the
    name as a path, and the run folder, copy or clone was made outside W (or outside RUN)."""
    CI, B2, SC, A = load("copy_isolation"), load("rehearse_batch2"), load("suite_at_commit"), load("after_run_check")
    member = tmp_path / "member"
    head = git_member(member)
    work = tmp_path / "work"
    name = str(tmp_path / "escaped") if shape == "absolute" else "../escaped"
    try:
        if site == "run_folder":
            made = CI.run_folder(work, [member], prefix=name + "-")
            assert made.parent == work.resolve() or made.parent == work, made
        elif site == "packet_copy":
            run = CI.run_folder(work, [member])
            with pytest.raises(ValueError, match="not a single folder name"):
                B2.copy_of({"aget": name, "location": str(member)}, run)
        elif site == "B8a":
            clone, why = SC.clean_clone(member, name, head, (), work)
            assert clone is None and "not a single folder name" in why, why
        else:
            still, passed, why = A.confirm_at_head(member, name, ["tests/t.py::test_t"], (), work, head)
            assert why and "not a single folder name" in why, why
    finally:
        assert sorted(p.name for p in tmp_path.iterdir()) in (["member"], ["member", "work"])


def test_b162_1_the_suite_check_cli_refuses_a_path_shaped_name_before_any_folder(tmp_path):
    """B162 finding 1, at the command line (REVW6's falsifier). `suite_at_commit.py --aget <absolute path>`: refused
    (exit 2), and no evidence, run folder or clone is made at that path. On stage E2g it read PASS (exit 0) with the
    clone and the evidence at the named path."""
    SC = load("suite_at_commit")
    member = tmp_path / "member"
    head = git_member(member)
    name = str(tmp_path / "escaped")
    pk = tmp_path / "packet.json"
    pk.write_text(json.dumps({"receivers": [{"aget": name, "location": str(member), "head": head,
                                             "suite_cmd": f"{sys.executable} -c pass"}]}))
    assert SC.main(["--packet", str(pk), "--aget", name, "--evidence", str(tmp_path / "ev")]) == 2
    assert not (tmp_path / "escaped").exists() and not (tmp_path / "ev").exists()


def _sibling_run(tmp_path, link_target):
    """A run folder holding an isolated copy `m` and a declared sibling repository `sib` whose
    `.git/hooks/pre-commit` links to `link_target`; the copy carries the custody marker for packet sha 0…0."""
    LB, CI = load("launch_batch"), load("copy_isolation")
    run = tmp_path / "run" / "m.root"
    copy = run / "m"
    git_member(copy)
    sib = run / "sib"
    git_member(sib)
    (sib / ".git" / "hooks").mkdir(exist_ok=True)
    (sib / ".git" / "hooks" / "pre-commit").symlink_to(link_target)
    assert CI.isolate(copy, "remove", member=True, run=run) is None
    (copy / ".git" / LB.COPY_MARKER).write_text(json.dumps({"packet_sha256": "0" * 64, "aget": "m"}))
    return LB, run, copy


def test_b162_2_the_launch_walks_every_declared_sibling_of_the_copy(tmp_path):
    """B162 finding 2, launch half (clause 4: every symbolic link under RUN). A declared sibling beside the copy has a
    hook link leading outside the run: the --copy-root check refuses. Control: the same link leading inside the run is
    accepted. On stage E2g the launch walked only the copy, so the sibling's link was not seen."""
    outside = tmp_path / "outside-hook"
    outside.write_text("#!/bin/sh\n")
    LB, run, copy = _sibling_run(tmp_path, str(outside))
    why = LB.copy_root_refusal(copy, tmp_path / "live", "0" * 64, "m", ["../sib"])
    assert why and "leads outside" in why and "sib" in why, why
    (run / "sib" / ".git" / "hooks" / "pre-commit").unlink()
    (run / "sib" / ".git" / "hooks" / "pre-commit").symlink_to("../../a.txt")
    assert LB.copy_root_refusal(copy, tmp_path / "live", "0" * 64, "m", ["../sib"]) is None


def test_b162_2_the_session_environment_refuses_a_hooks_path_outside_the_run(tmp_path):
    """B162 finding 2's class, clause 6(c): with the copy's own hooks in force, `core.hooksPath` naming a folder
    outside the run would run code outside it. The copy-root session environment refuses it. Control: a hooks path
    inside the run is accepted. On stage E2g the environment was returned and those hooks would have run."""
    LB, CI = load("launch_batch"), load("copy_isolation")
    run = tmp_path / "run"
    copy = run / "m"
    git_member(copy)
    assert CI.isolate(copy, "remove", member=True, run=copy) is None
    outside = tmp_path / "outside-hooks"
    outside.mkdir()
    _run_git(copy, "config", "core.hooksPath", str(outside))
    with pytest.raises(LB.CI.ContainmentRefused, match="core.hooksPath"):
        LB.copy_session_env(copy)
    _run_git(copy, "config", "core.hooksPath", ".githooks")            # control: inside the copy
    assert LB.copy_session_env(copy)["CLAUDE_PROJECT_DIR"] == str(copy)


@pytest.mark.parametrize("failure", ["global_config", "config_count"])
def test_b162_3_a_failed_repository_query_refuses_the_work_root(tmp_path, monkeypatch, failure):
    """B162 finding 3 (REVW6's falsifier). Git cannot answer whether the work root lies in a repository (a malformed
    global configuration; an invalid GIT_CONFIG_COUNT): refused, and nothing is made. On stage E2g any non-zero exit
    read as "not in a repository", and the run folder was made inside the enclosing repository."""
    CI = load("copy_isolation")
    other = tmp_path / "other"
    git_member(other)
    if failure == "global_config":
        bad = tmp_path / "bad-config"
        bad.write_text("not valid git configuration\n")
        monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(bad))
    else:
        monkeypatch.setenv("GIT_CONFIG_COUNT", "invalid")
    with pytest.raises(CI.ContainmentRefused, match="cannot be read"):
        CI.run_folder(other / "work", [tmp_path / "member"])
    assert not (other / "work").exists()


def test_b162_5_a_hooks_folder_linked_outside_the_member_is_not_run(tmp_path):
    """B162 finding 5 (REVW6's falsifier). The member's `.git/hooks` folder is itself a link to an outside folder holding
    a regular `pre-push`: B8a does not run it and reads INCONCLUSIVE. On stage E2g the entry's own lstat read a regular
    file, so the outside hook was materialized and run, and B8a read PASS."""
    SC = load("suite_at_commit")
    loc, sha = _hook_member(tmp_path, "../../scripts/pre-push")
    outside = tmp_path / "outside-hooks"
    outside.mkdir()
    sentinel = tmp_path / "outside_ran"
    (outside / "pre-push").write_text(f"#!/bin/sh\ntouch '{sentinel}'\n")
    (outside / "pre-push").chmod(0o755)
    os.rename(loc / ".git" / "hooks", loc / ".git" / "original-hooks")
    (loc / ".git" / "hooks").symlink_to(outside, target_is_directory=True)
    rec = SC.run(loc, "m", sha, f"{sys.executable} -m pytest -q -p no:cacheprovider", work=tmp_path / "w")
    assert not sentinel.exists()
    assert rec["verdict"] == "INCONCLUSIVE" and "hook present, not run" in rec["why"], rec


@pytest.mark.parametrize("form,ending", [("worktree", "\r"), ("separate", " "), ("separate", "\t")])
def test_b162_6_the_common_git_folder_is_read_byte_for_byte(tmp_path, form, ending):
    """B162 finding 6 (REVW6's falsifiers). A member whose common git folder's name ends in a CR (a linked worktree of
    a repository so named), a space or a tab (a separate git folder): its pre-push hook is found and run. On stage E2g
    the folder name was decoded with newline translation and trimmed, the hook read as absent (`present: false`) and
    B8a read PASS without it."""
    SC = load("suite_at_commit")
    base = tmp_path / (("common" + ending) if form == "worktree" else "base")
    git_member(base)
    (base / "tests").mkdir()
    (base / "tests" / "test_a.py").write_text("def test_a():\n    assert True\n")
    _run_git(base, "add", "-A")
    _run_git(base, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "t")
    member = tmp_path / "member"
    if form == "worktree":
        common = base / ".git"
        p = _run_git(base, "worktree", "add", "--detach", str(member), "HEAD")
    else:
        common = tmp_path / ("gitdir" + ending)
        p = subprocess.run(["git", "clone", "-q", "--no-hardlinks", "--separate-git-dir", str(common), str(base),
                            str(member)], capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    sha = _run_git(member, "rev-parse", "HEAD").stdout.strip()
    (common / "hooks").mkdir(exist_ok=True)
    (common / "hooks" / "pre-push").write_text("#!/bin/sh\necho common hook\n")
    (common / "hooks" / "pre-push").chmod(0o755)
    rec = SC.run(member, "m", sha, f"{sys.executable} -m pytest -q -p no:cacheprovider", work=tmp_path / "w")
    assert rec["hook"].get("present") and "common hook" in rec["hook"].get("tail", ""), rec


# --- REVW6's B163 read of stage E2g2 -----------------------------------------------------------------------------

@pytest.mark.parametrize("ending", ["\n", "\n\n"])
def test_b163_2_the_hooks_path_is_read_byte_for_byte(tmp_path, ending):
    """B163 finding 2 (REVW6's falsifier). `core.hooksPath` names a folder `<run>\\n` beside the run folder (outside
    it): the copy-session environment refuses it. On stage E2g2 the value was trimmed of trailing line feeds, read as
    the run folder itself, and the environment was returned (a session commit then ran the outside hook)."""
    LB = load("launch_batch")
    run = tmp_path / "run"
    copy = run / "m"
    git_member(copy)
    assert LB.CI.isolate(copy, "remove", member=True, run=copy) is None
    outside = Path(str(run) + ending)
    outside.mkdir()
    (outside / "pre-commit").write_text("#!/bin/sh\necho synthetic outside hook\n")
    (outside / "pre-commit").chmod(0o755)
    _run_git(copy, "config", "core.hooksPath", str(outside))
    with pytest.raises(LB.CI.ContainmentRefused, match="outside the run folder"):
        LB.copy_session_env(copy)


def test_b163_3_a_diagnostic_naming_the_phrase_is_not_git_s_answer(tmp_path, monkeypatch):
    """B163 finding 3 (REVW6's falsifier). Inside a repository, a malformed global configuration whose file is named
    `not a git repository` makes git fail with a diagnostic holding those words: the work root is refused and nothing
    is made. On stage E2g2 the words anywhere in stderr were read as git's answer, and the run folder was made inside
    the repository."""
    CI = load("copy_isolation")
    other = tmp_path / "other"
    git_member(other)
    bad = tmp_path / "not a git repository"
    bad.write_text("not valid git configuration\n")
    monkeypatch.setenv("GIT_CONFIG_GLOBAL", str(bad))
    with pytest.raises(CI.ContainmentRefused, match="cannot be read"):
        CI.run_folder(other / "work", [tmp_path / "member"])
    assert not (other / "work").exists()


# --- Stage E2h: INRUN (R1-T5) and read-only status (R1-T12) ---------------------------------------------------------

def test_r1_t5_isolation_changes_no_remote_of_a_folder_outside_the_named_run(tmp_path):
    """R1-T5 (INRUN). Isolation is asked to act on a repository that does not lie inside the run folder it is given:
    refused, and the repository keeps its remotes and configuration. On stage E2g3 the remote-changing functions took
    no run, so isolation removed the remotes of a folder outside the named run."""
    CI = load("copy_isolation")
    live = tmp_path / "live"
    git_member(live)
    _run_git(live, "remote", "add", "origin", str(tmp_path / "somewhere.git"))
    config = (live / ".git" / "config").read_bytes()
    run = tmp_path / "run"
    run.mkdir()
    why = CI.isolate(live, "remove", member=True, run=run)
    assert why and "does not lie inside the run folder" in why, why
    assert _run_git(live, "remote").stdout.split() == ["origin"] and (live / ".git" / "config").read_bytes() == config


@pytest.mark.parametrize("fn", ["remove_remotes", "disable_push", "remove_legacy_remotes", "remove_url_rewrites",
                                "dead_scheme_refusal"])
def test_r1_t5_each_remote_or_config_writer_refuses_without_a_run_that_holds_the_repository(tmp_path, fn):
    """R1-T5 (INRUN, in each function itself). Called with no run folder, or with one that does not hold the
    repository, each function that changes remotes or configuration refuses before any git act; the repository's
    config is unchanged. On stage E2g3 the first call (no run folder) acted on the repository and returned None."""
    CI = load("copy_isolation")
    live = tmp_path / "live"
    git_member(live)
    _run_git(live, "remote", "add", "origin", str(tmp_path / "somewhere.git"))
    config = (live / ".git" / "config").read_bytes()
    f = getattr(CI, fn)
    assert f(live).startswith("no run folder was named")
    other = tmp_path / "run"
    other.mkdir()
    assert "does not lie inside the run folder" in f(live, run=other)
    assert (live / ".git" / "config").read_bytes() == config


def _stale_member(tmp_path):
    """A member whose tracked file's stat data no longer matches its index entry (same bytes, new mtime), so a status
    read that may write would refresh and rewrite `.git/index`. Returns (folder, index bytes)."""
    loc = tmp_path / "home" / "a"
    git_member(loc)
    st = os.stat(loc / "a.txt")
    os.utime(loc / "a.txt", (st.st_atime + 120, st.st_mtime + 120))
    return loc, (loc / ".git" / "index").read_bytes()


def test_r1_t12_the_kit_s_status_listing_leaves_the_index_unchanged(tmp_path):
    """R1-T12. `git_status_paths` on a member with stale stat data leaves `.git/index` byte for byte as it was. On
    stage E2g3 the status read took git's optional lock and rewrote the index."""
    CI = load("copy_isolation")
    loc, index = _stale_member(tmp_path)
    assert CI.git_status_paths(loc) == []
    assert (loc / ".git" / "index").read_bytes() == index


def test_r1_t12_the_baseline_launch_s_status_reads_leave_the_index_unchanged(tmp_path, monkeypatch):
    """R1-T12. The baseline launch reads the live member's status before and after the session; with stale stat data
    the index is unchanged. On stage E2g3 those reads rewrote it."""
    LB, r, packet, pr = baseline_world(tmp_path, monkeypatch)
    loc = Path(r["location"])
    st = os.stat(loc / "a.txt")
    os.utime(loc / "a.txt", (st.st_atime + 120, st.st_mtime + 120))
    index = (loc / ".git" / "index").read_bytes()
    LB.run_baseline(r, packet, tmp_path / "ev", packet["stage"])
    assert (loc / ".git" / "index").read_bytes() == index


# --- REVW6's B165 read of stage E2h ------------------------------------------------------------------------------

def test_b165_1_the_route_probe_writes_no_config_reached_through_a_late_link(tmp_path):
    """B165 finding 1 (REVW6's falsifier). An isolated copy whose `remote.pushDefault` is the dead URL (so the route
    reader adds its short-lived probe remote), and whose `.git/config` member code then replaced with a link to an
    outside file: reading the routes refuses, and the outside file's bytes and inode are unchanged. On stage E2h the
    probe wrote the copy's config through the link before any check."""
    CI = load("copy_isolation")
    run = tmp_path / "run"
    copy = run / "m"
    git_member(copy)
    assert CI.isolate(copy, "remove", member=True, run=run) is None
    _run_git(copy, "config", "remote.pushDefault", CI.NO_PUSH_URL)
    outside = tmp_path / "outside-config"
    outside.write_bytes((copy / ".git" / "config").read_bytes().rstrip(b"\n"))
    (copy / ".git" / "config").unlink()
    (copy / ".git" / "config").symlink_to(outside)
    before, inode = outside.read_bytes(), outside.stat().st_ino
    why = CI.push_route_refusal(copy, allowed=(CI.NO_PUSH_URL,))          # no run named: refused, nothing written
    assert why and outside.read_bytes() == before and outside.stat().st_ino == inode, why
    why = CI.push_route_refusal(copy, allowed=(CI.NO_PUSH_URL,), run=run)  # the run named: the identity test refuses
    assert why and "leads outside" in why, why
    assert outside.read_bytes() == before and outside.stat().st_ino == inode


def test_b165_1_the_copy_commit_refuses_an_object_store_linked_outside(tmp_path):
    """B165 finding 1 (REVW6's falsifier). After isolation, member code moves the copy's `.git/objects` outside and
    links it back: the kit's copy commit refuses before any git act, HEAD is unchanged and nothing is added outside.
    On stage E2h the commit went through, moved HEAD and wrote object files outside the run."""
    import shutil
    B2 = load("rehearse_batch2")
    run = tmp_path / "run"
    copy = run / "m"
    git_member(copy)
    assert load("copy_isolation").isolate(copy, "remove", member=True, run=run) is None
    outside = tmp_path / "outside-objects"
    shutil.move(str(copy / ".git" / "objects"), str(outside))
    (copy / ".git" / "objects").symlink_to(outside, target_is_directory=True)
    before = sorted(str(p) for p in outside.rglob("*"))
    head = _run_git(copy, "rev-parse", "HEAD").stdout.strip()
    (copy / "new.txt").write_text("migration\n")
    with pytest.raises(B2.CopyStepFailed, match="copy commit not made"):
        B2.commit_applied(copy, {"pre_dirty": []})
    assert _run_git(copy, "rev-parse", "HEAD").stdout.strip() == head
    assert sorted(str(p) for p in outside.rglob("*")) == before


def test_b165_2_a_diff_read_of_a_live_member_leaves_its_index_unchanged(tmp_path):
    """B165 finding 2 (REVW6's falsifier). The after-run check's changed-path read (`git diff`) of a member with stale
    stat data leaves `.git/index` byte for byte as it was. On stage E2h `git diff` refreshed and rewrote it (even with
    GIT_OPTIONAL_LOCKS=0)."""
    A = load("after_run_check")
    loc, index = _stale_member(tmp_path)
    head = _run_git(loc, "rev-parse", "HEAD").stdout.strip()
    assert A.changed_paths(loc, head) == set()
    assert (loc / ".git" / "index").read_bytes() == index


def test_b165_2_an_object_read_of_a_partial_clone_fetches_nothing(tmp_path):
    """B165 finding 2 (REVW6's falsifier). A member that is a blob-filtered local clone: the after-run check's
    `git show` of a missing blob reads nothing rather than fetching it, and the member's object store is unchanged.
    On stage E2h the read fetched the blob from the local source, writing pack files into the member's `.git`."""
    A = load("after_run_check")
    src = tmp_path / "src"
    git_member(src)
    bare = tmp_path / "src.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(src), str(bare)], check=True)
    _run_git(bare, "config", "uploadpack.allowFilter", "true")
    member = tmp_path / "member"
    p = subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout", f"file://{bare}", str(member)],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    before = sorted(str(x) for x in (member / ".git" / "objects").rglob("*"))
    shown = A.git_out(member, "show", "HEAD:a.txt")
    assert shown == "" and sorted(str(x) for x in (member / ".git" / "objects").rglob("*")) == before


@pytest.mark.parametrize("value", [{}, False, 0, ""])
def test_b165_3_a_false_valued_sibling_declaration_is_not_an_empty_population(tmp_path, value):
    """B165 finding 3 (REVW6's falsifier). A packet row whose `sibling_reads` is `{}`, `false`, `0` or `""` is an
    invalid declaration, not an empty one: the population is reported as not known. On stage E2h `or []` turned each
    into an empty, valid population (and F confirmed a failure against it)."""
    import types as _t
    A = load("after_run_check")
    pk = tmp_path / "packet.json"
    pk.write_text(json.dumps({"receivers": [{"aget": "a", "sibling_reads": value}]}))
    siblings, why = A.declared_siblings(_t.SimpleNamespace(packet=str(pk), aget="a", sibling_read=[]))
    assert why and "not a list of strings" in why, (siblings, why)


# --- REVW7's B166 read of stage E2h2 -----------------------------------------------------------------------------

def _isolated_copy_with_outside_reflog_name(tmp_path):
    """An isolated copy whose `.git/logs/HEAD` has a second name outside the run (a hard link). Returns
    (copy, run, outside name, its bytes, HEAD)."""
    run = tmp_path / "run"
    copy = run / "m"
    head = git_member(copy)
    assert load("copy_isolation").isolate(copy, "remove", member=True, run=run) is None
    reflog = copy / ".git" / "logs" / "HEAD"
    assert reflog.is_file()
    outside = tmp_path / "outside-reflog"
    os.link(reflog, outside)
    return copy, run, outside, outside.read_bytes(), head


def test_b166_1_the_copy_commit_refuses_a_reflog_with_a_second_name(tmp_path):
    """B166 finding 1 (REVW7's falsifier). The copy's HEAD reflog has a second name outside the run: the kit's copy
    commit refuses before any git act, HEAD is unchanged and the outside file keeps its bytes. On stage E2h2 the
    identity test walked symbolic links only; the commit went through and appended the reflog through the link."""
    B2 = load("rehearse_batch2")
    copy, _, outside, before, head = _isolated_copy_with_outside_reflog_name(tmp_path)
    (copy / "new.txt").write_text("migration\n")
    with pytest.raises(B2.CopyStepFailed, match="more than one name"):
        B2.commit_applied(copy, {"pre_dirty": []})
    assert _run_git(copy, "rev-parse", "HEAD").stdout.strip() == head
    assert outside.read_bytes() == before


def test_b166_1_the_repair_checkout_refuses_a_reflog_with_a_second_name(tmp_path):
    """B166 finding 1 (REVW7's falsifier): the repair rehearsal's checkout refuses, and the outside name keeps its
    bytes. On stage E2h2 the checkout ran and appended to the shared reflog."""
    RR = load("rehearse_repair")
    copy, _, outside, before, head = _isolated_copy_with_outside_reflog_name(tmp_path)
    why = RR.checkout(copy, head)
    assert why and "more than one name" in why, why
    assert outside.read_bytes() == before


def test_b166_1_a_configuration_writer_refuses_a_config_with_a_second_name(tmp_path):
    """B166 finding 1, the INRUN writers: a copy whose `.git/config` has a second name outside the run is refused by
    the remote and configuration writers before any write (git rewrites config by lock and rename, so here the
    outside name would only fall out of step; the refusal is the same predicate). On stage E2h2 it was admitted."""
    CI = load("copy_isolation")
    run = tmp_path / "run"
    copy = run / "m"
    git_member(copy)
    os.link(copy / ".git" / "config", tmp_path / "outside-config")
    why = CI.remove_remotes(copy, run=run)
    assert why and "more than one name" in why, why


def test_b166_1_control_a_local_clone_sharing_its_objects_is_still_admitted(tmp_path):
    """The control for B166 finding 1, changed in E2h5 (B168 finding 1: the object-store exemption is removed). A
    plain local clone shares its object files with the source by hard link and is now refused, with the reason; the
    same clone made with `--no-hardlinks`, as every kit clone is, is admitted. (Until E2h5 the hard-linked clone was
    admitted; the test name is kept for the control records.)"""
    CI = load("copy_isolation")
    src = tmp_path / "src"
    git_member(src)
    clone = tmp_path / "run" / "c"
    subprocess.run(["git", "clone", "-q", str(src), str(clone)], check=True)
    objs = [p for p in (clone / ".git" / "objects").rglob("*") if p.is_file() and os.lstat(p).st_nlink > 1]
    assert objs, "the fixture's clone shares no object file; the control would not test the refusal"
    why = CI.git_identity_refusal(clone)
    assert why and "more than one name" in why, why
    own = tmp_path / "run" / "own"
    subprocess.run(["git", "clone", "-q", "--no-hardlinks", str(src), str(own)], check=True)
    assert CI.git_identity_refusal(own) is None

def _partial_member(tmp_path):
    """A live member that is a blob-filtered local clone with no checkout (its blobs missing, fetchable from a local
    source), holding `.claude/settings.json` at HEAD. Returns (member, .git bytes by path)."""
    src = tmp_path / "src"
    git_member(src)
    (src / ".claude").mkdir()
    (src / ".claude" / "settings.json").write_text("{}\n")
    _run_git(src, "add", ".claude/settings.json")
    _run_git(src, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "settings")
    bare = tmp_path / "src.git"
    subprocess.run(["git", "clone", "-q", "--bare", str(src), str(bare)], check=True)
    _run_git(bare, "config", "uploadpack.allowFilter", "true")
    member = tmp_path / "member"
    p = subprocess.run(["git", "clone", "-q", "--filter=blob:none", "--no-checkout", f"file://{bare}", str(member)],
                       capture_output=True, text=True)
    assert p.returncode == 0, p.stderr
    return member, _git_bytes(member)


def _git_bytes(member):
    return {str(p.relative_to(member / ".git")): p.read_bytes() for p in (member / ".git").rglob("*") if p.is_file()}


@pytest.mark.parametrize("reader", ["prepare_settings", "fleet_receipt", "wave_wrapper", "push_receipt"])
def test_b166_2_live_object_reads_outside_the_shared_helper_fetch_nothing(tmp_path, monkeypatch, reader):
    """B166 finding 2 (REVW7's falsifier). Each kit reader of a live member's objects (launch preparation's tracked
    settings, the ledger's receipt re-read, the readiness tool's git runner, the push gate's receipt read) leaves a
    partial clone's git folder byte for byte as it was. On stage E2h2 the first three fetched four pack files."""
    member, before = _partial_member(tmp_path)
    if reader == "prepare_settings":
        PL = load("prepare_launch")
        monkeypatch.setattr(PL, "STAGE", tmp_path / "packet" / "stage")
        PL.settings_file({"location": str(member), "aget": "synthetic"})
    elif reader == "fleet_receipt":
        load("fleet_ledger").reread_receipt(member, "", {"attempt": "synthetic", "receipt_path": ".claude/settings.json",
                                                         "receipt_revisions": ["HEAD"], "terminal": "ACCEPTED"})
    elif reader == "wave_wrapper":
        load("wave_readiness").run(["git", "-C", str(member), "show", "HEAD:.claude/settings.json"])
    else:
        load("push_batch").git(str(member), "show", "HEAD:.claude/settings.json")
    assert _git_bytes(member) == before


# Every git invocation in the kit that is not a member read through the shared mechanism, with the reason it may be
# plain: it acts in a copy or clone the kit made, or reads a framework repository, not a member (B166 finding 2).
NOT_MEMBER_READS = {
    ("after_run_check.py", '["git", "clone", "-q", "--no-hardlinks"'): "clones into the confirmation run folder",
    ("after_run_check.py", '["git", "-C", str(dest), "checkout"'): "an act in the confirmation clone",
    ("copy_isolation.py", 'git = ["git", "--git-dir", str(Path(repo) / ".git")]'): "INRUN writers in a copy",
    ("copy_isolation.py", '["git", "--git-dir", str(Path(repo) / ".git"), *args]'): "_git: acts in a copy",
    ("prepare_batch.py", '["git", "-C", str(repo), "tag"]'): "framework release tags",
    ("prepare_launch.py", '["git", "-C", str(repo), "rev-parse", f"{R.TO_TAG}'): "the framework release tag",
    ("suite_at_commit.py", '["git", "clone", "-q", "--no-hardlinks"'): "clones into the suite's run folder",
    ("verify_extension_survival.py", "['git', '-C', core, 'tag']"): "framework core tags",
    ("verify_extension_survival.py", "['git', '-C', core, 'show'"): "framework core release bytes",
    ("wave_readiness.py", "observed(['git'"): "run() adds READ_FLAGS and READ_ENV to every git command",
    ("rehearse_repair.py", '["git", "-C", str(root), *args], capture_output=True, text=True, env=env)'):
        "git() acts and reads in the rehearsal copy",
}


# changed at E2i14 (B191 finding 1, labelled): the two framework release-byte readers now read through
# copy_isolation.git_blob_at (READ_FLAGS), so they left the exception list
def test_b166_2_every_kit_git_invocation_is_a_read_that_writes_nothing_or_a_named_exception():
    """B166 finding 2, the census (REVW7's closing route: "apply the immutability mechanism across all live readers
    and inspect direct `show` calls as well as wrappers"). Every git command line the kit's tools build takes no
    optional lock and fetches no missing object (copy_isolation.READ_FLAGS, or the same two options written out), or
    is listed in NOT_MEMBER_READS with its reason. On stage E2h2 the census found member reads without them in
    prepare_launch, fleet_ledger, launch_batch, push_batch, prepare_batch, record_authority, open_receiver,
    watch_receiver, verify_extension_survival, census_fleet_ci and suite_at_commit."""
    import re
    found, unused = [], set(NOT_MEMBER_READS)
    for f in sorted(BATCH.glob("*.py")):
        for n, line in enumerate(f.read_text().splitlines(), 1):
            if not re.search(r"""\[["']git["'],""", line) or line.lstrip().startswith("#"):
                continue
            if ("*READ_FLAGS" in line or "*CI.READ_FLAGS" in line
                    or re.search(r"""["']--no-optional-locks["'], ["']--no-lazy-fetch["']""", line)):
                continue
            hit = [k for k in NOT_MEMBER_READS if k[0] == f.name and k[1] in line]
            if hit:
                unused.discard(hit[0])
                continue
            found.append(f"{f.name}:{n}: {line.strip()[:100]}")
    assert found == [], found
    assert unused == set(), f"stale exceptions: {sorted(unused)}"


# --- REVW7's B167 read of stage E2h3 -----------------------------------------------------------------------------

def _copy_with_aliased_shared_reflog(tmp_path, alias):
    """An isolated copy whose HEAD reflog is reached through a symbolic link that stays inside the copy (admitted by
    LINKS), while the file behind it has a second name outside the run. `alias` is "file" (`.git/logs/HEAD` links to a
    worktree file) or "directory" (`.git/logs` links to a worktree folder). Returns (copy, outside, bytes, HEAD)."""
    import shutil
    run = tmp_path / "run"
    copy = run / "m"
    head = git_member(copy)
    assert load("copy_isolation").isolate(copy, "remove", member=True, run=run) is None
    logs = copy / ".git" / "logs"
    if alias == "file":
        target = copy / "internal-reflog"
        shutil.move(str(logs / "HEAD"), str(target))
        (logs / "HEAD").symlink_to(os.path.relpath(target, logs))
    else:
        target_dir = copy / "internal-logs"
        shutil.move(str(logs), str(target_dir))
        logs.symlink_to(os.path.relpath(target_dir, logs.parent), target_is_directory=True)
        target = target_dir / "HEAD"
    outside = tmp_path / "outside-reflog"
    os.link(target, outside)
    assert load("copy_isolation").link_refusal(copy, run) is None      # the alias stays inside: LINKS admits it
    return copy, outside, outside.read_bytes(), head


@pytest.mark.parametrize("alias", ["file", "directory"])
@pytest.mark.parametrize("act", ["commit", "checkout"])
def test_b167_1_a_shared_reflog_behind_an_internal_alias_is_refused(tmp_path, alias, act):
    """B167 finding 1 (REVW7's falsifier). The reflog is reached through an internal file or folder alias and the file
    behind it has an outside second name: the copy commit and the repair checkout refuse, and the outside name keeps
    its bytes. On stage E2h3 the shared-storage walk did not follow links; the commit and checkout appended through
    the alias (127 → 310 and 127 → 332 bytes in REVW7's run)."""
    copy, outside, before, head = _copy_with_aliased_shared_reflog(tmp_path, alias)
    if act == "commit":
        B2 = load("rehearse_batch2")
        (copy / "new.txt").write_text("migration\n")
        with pytest.raises(B2.CopyStepFailed, match="more than one name"):
            B2.commit_applied(copy, {"pre_dirty": []})
    else:
        why = load("rehearse_repair").checkout(copy, head)
        assert why and "more than one name" in why, why
    assert outside.read_bytes() == before


def test_b167_1_a_folder_alias_cycle_ends_and_an_unshared_alias_is_admitted(tmp_path):
    """The walk follows folder aliases once each: a cycle of aliases inside the git folder ends, and a copy whose
    aliases lead only to singly-named files is admitted."""
    CI = load("copy_isolation")
    run = tmp_path / "run"
    copy = run / "m"
    git_member(copy)
    (copy / ".git" / "loop").mkdir()
    (copy / ".git" / "loop" / "back").symlink_to("..", target_is_directory=True)
    (copy / ".git" / "loop" / "self").symlink_to(".", target_is_directory=True)
    assert CI.shared_git_file(copy / ".git") is None   # E2h5: (path, reason) or None
    assert CI.git_identity_refusal(copy) is None


# --- REVW8's B168 read of stage E2h4 -----------------------------------------------------------------------------

@pytest.mark.parametrize("into", ["objects/pack", "objects/aa", "objects/non_object"])
@pytest.mark.parametrize("act", ["commit", "checkout"])
def test_b168_1_a_shared_reflog_aliased_into_the_object_store_is_refused(tmp_path, into, act):
    """B168 finding 1 (REVW8's falsifier). `.git/logs` is moved into a folder of the object store and linked back,
    and its HEAD reflog has an outside second name: the copy commit and the repair checkout refuse, and the outside
    name keeps its bytes. On stage E2h4 the real visit of the object folder marked it seen and skipped it, the alias
    visit was then suppressed, and both acts appended (127 → 310 and 127 → 332 bytes in REVW8's run)."""
    import shutil
    run = tmp_path / "run"
    copy = run / "m"
    head = git_member(copy)
    assert load("copy_isolation").isolate(copy, "remove", member=True, run=run) is None
    logs, dest = copy / ".git" / "logs", copy / ".git" / into     # the object folder itself holds the reflogs
    dest.mkdir(parents=True, exist_ok=True)
    for item in logs.iterdir():
        shutil.move(str(item), str(dest / item.name))
    logs.rmdir()
    logs.symlink_to(os.path.relpath(dest, logs.parent), target_is_directory=True)
    outside = tmp_path / "outside-reflog"
    os.link(dest / "HEAD", outside)
    before = outside.read_bytes()
    if act == "commit":
        B2 = load("rehearse_batch2")
        (copy / "new.txt").write_text("migration\n")
        with pytest.raises(B2.CopyStepFailed, match="more than one name"):
            B2.commit_applied(copy, {"pre_dirty": []})
    else:
        why = load("rehearse_repair").checkout(copy, head)
        assert why and "more than one name" in why, why
    assert outside.read_bytes() == before


def test_b168_1_a_git_folder_that_cannot_be_listed_is_refused(tmp_path):
    """E2h5: a folder under `.git` the walk cannot list is refused (what git may write there is unknown), never
    skipped."""
    CI = load("copy_isolation")
    run = tmp_path / "run"
    copy = run / "m"
    git_member(copy)
    locked = copy / ".git" / "refs" / "locked"
    locked.mkdir()
    locked.chmod(0)
    try:
        why = CI.git_identity_refusal(copy)
    finally:
        locked.chmod(0o755)
    assert why and "cannot be listed" in why, why


# --- REVW8's B169 read of stage E2h5 -----------------------------------------------------------------------------

@pytest.mark.parametrize("shared", [True, False])
def test_b169_1_a_reflog_that_is_a_fifo_is_refused_whatever_its_names(tmp_path, shared):
    """B169 finding 1 (REVW8's falsifier, at the preflight). `.git/logs/HEAD` is a FIFO, with or without a second
    name outside the run: the act preflight (identity and LINKS) refuses before any git act, so no git write reaches
    whatever reads the FIFO. Checked at the predicate, which act_refusal and INRUN both use: on the base stage a git
    write into the FIFO would block. On stage E2h5 only regular files were link-counted and the FIFO was admitted."""
    CI = load("copy_isolation")
    run = tmp_path / "run"
    copy = run / "m"
    git_member(copy)
    reflog = copy / ".git" / "logs" / "HEAD"
    reflog.unlink()
    os.mkfifo(reflog)
    if shared:
        os.link(reflog, tmp_path / "outside-fifo")
    why = CI.act_refusal(copy, dict(os.environ), run)
    assert why and "is not a regular file or folder" in why, why
    assert CI.inrun_refusal(copy, run) is not None


def test_b169_2_a_failed_inspection_of_a_git_file_is_a_refusal(tmp_path, monkeypatch):
    """B169 finding 2 (REVW8's falsifier, at the preflight). `lstat` of the real `.git/logs/HEAD`, which has an
    outside second name, fails (EACCES injected for that one path): the preflight refuses, naming the entry. On stage
    E2h5 a failed stat was skipped and the shared reflog was admitted."""
    import errno
    CI = load("copy_isolation")
    run = tmp_path / "run"
    copy = run / "m"
    git_member(copy)
    reflog = copy / ".git" / "logs" / "HEAD"
    os.link(reflog, tmp_path / "outside-reflog")
    real_lstat = os.lstat

    def lstat(p, *a, **k):
        if str(p) == str(reflog):
            raise PermissionError(errno.EACCES, "injected", str(p))
        return real_lstat(p, *a, **k)
    monkeypatch.setattr(CI.os, "lstat", lstat)
    why = CI.shared_git_file(copy / ".git")
    assert why and why[0] == reflog and "cannot be inspected (PermissionError)" in why[1], why


def test_b169_2_control_a_dangling_link_in_the_git_folder_is_still_skipped(tmp_path):
    """The control for B169 finding 2: a symbolic link under `.git` whose target does not exist names nothing to
    append to; it is skipped, not refused."""
    CI = load("copy_isolation")
    copy = tmp_path / "run" / "m"
    git_member(copy)
    (copy / ".git" / "dangling").symlink_to("no-such-file")
    assert CI.shared_git_file(copy / ".git") is None


# --- E2i12: REVW9's B186 read (a member nested in its git-selected working tree) and FWK-OVSR5's E2i11 advisory ----

def _g(loc, *a):
    return subprocess.run(["git", "-C", str(loc), "-c", "user.name=t", "-c", "user.email=t@t", *a], check=True,
                          capture_output=True)


@pytest.mark.parametrize("nested", [False, True])
def test_b186_1_a_relative_excludes_file_is_read_from_the_selected_tree_top(tmp_path, nested):
    """B186 finding 1 (REVW9 `reviewer_e2i11_probes.py::test_ign_refuses_changed_relative_excludes_in_the_git_selected_
    working_tree[True]`): git reads a relative core.excludesFile from the top of the working tree it selects; from a
    nested supplied folder the kit read `nested/<name>` (absent) and missed a change git sees. On E2i11-C2a7 the nested
    case gave no refusal."""
    CI = load("copy_isolation")
    root = tmp_path / "member"
    git_member(root)
    (root / "nested").mkdir()
    rules = root / ".synthetic-excludes"
    rules.write_text("one.txt\n")
    _g(root, "config", "core.excludesFile", ".synthetic-excludes")
    folder = root / "nested" if nested else root
    before = CI.ignore_state(folder)
    assert before["core.excludesFile file"].startswith(str(rules) + ": "), before["core.excludesFile file"]
    rules.write_text("two.txt\n")
    assert CI.ignore_refusal(before, CI.ignore_state(folder), "relative excludes")


@pytest.mark.parametrize("nested,literal", [(False, False), (True, False), (True, True)])
def test_b186_2_index_flags_are_listed_across_the_selected_tree(tmp_path, nested, literal):
    """B186 finding 2 (REVW9 `::test_ign_refuses_changed_index_flags_across_the_git_selected_working_tree[True]`): a
    skip-worktree flag set outside the nested supplied folder changes IGN. On E2i11-C2a7 `ls-files -v` ran in the
    subfolder and listed only it. A caller's GIT_LITERAL_PATHSPECS does not turn the kit's `:(top)` into a name."""
    CI = load("copy_isolation")
    root = tmp_path / "member"
    git_member(root)
    (root / "nested").mkdir()
    (root / "nested" / "inside.txt").write_text("i\n")
    (root / "outside.txt").write_text("o\n")
    _g(root, "add", "nested/inside.txt", "outside.txt")
    folder = root / "nested" if nested else root
    env = {**os.environ, "GIT_LITERAL_PATHSPECS": "1"} if literal else None
    before = CI.ignore_state(folder, env=env)
    assert before["index flags"].startswith("0: "), before["index flags"]
    _g(root, "update-index", "--skip-worktree", "outside.txt")
    after = CI.ignore_state(folder, env=env)
    assert after["index flags"].startswith("1: ") and CI.ignore_refusal(before, after, "selected-tree flags")


def test_e2i11_advisory_1_git_tracked_is_an_exact_literal_entry(tmp_path):
    """FWK-OVSR5's E2i11 advisory (1), reproduced: `git_tracked` read True for a tracked folder and for pathspec magic
    (`:(glob)*`). Only an index entry for exactly the literal path counts."""
    CI = load("copy_isolation")
    root = tmp_path / "member"
    git_member(root)
    (root / "d").mkdir()
    (root / "d" / "f").write_text("f\n")
    _g(root, "add", "d/f")
    assert CI.git_tracked(root, "d/f") is True and CI.git_tracked(root, "a.txt") is True
    assert CI.git_tracked(root, "d") is False
    assert CI.git_tracked(root, ":(glob)*") is False and CI.git_tracked(root, "*.txt") is False
    assert CI.git_tracked(root, "absent.txt") is False


def test_e2i11_advisory_2_git_blob_at_reads_only_a_file_entry(tmp_path):
    """FWK-OVSR5's E2i11 advisory (2), reproduced: `git_blob_at(r, 'HEAD', 'd')` returned `git show`'s tree listing
    as if it were file bytes. A tree entry now raises InspectionFailed; a file reads its blob; absence is None."""
    CI = load("copy_isolation")
    root = tmp_path / "member"
    git_member(root)
    (root / "d").mkdir()
    (root / "d" / "f").write_text("f\n")
    _g(root, "add", "d/f")
    _g(root, "commit", "-q", "-m", "d")
    assert CI.git_blob_at(root, "HEAD", "d/f") == b"f\n" and CI.git_blob_at(root, "HEAD", "absent") is None
    with pytest.raises(CI.InspectionFailed):
        CI.git_blob_at(root, "HEAD", "d")
    with pytest.raises(CI.InspectionFailed):
        CI.git_blob_at(root, "no-such-rev", "d/f")


# --- E2i13: REVW9's B189 read (a committed symbolic link is not file content) ----------------------------------

def _commit_link(root, path, target):
    """Commit `path` as a symbolic link to `target` (mode 120000) through the index only: no link is written."""
    blob = subprocess.run(["git", "-C", str(root), "hash-object", "-w", "--stdin"], input=target.encode(),
                          capture_output=True, check=True).stdout.decode().strip()
    _g(root, "update-index", "--add", "--cacheinfo", f"120000,{blob},{path}")
    _g(root, "commit", "-q", "-m", "link")


def test_b189_1_git_blob_at_refuses_a_committed_symbolic_link(tmp_path):
    """B189 finding 1 (REVW9 `reviewer_e2i12_probes.py::test_after_run_refuses_a_committed_symbolic_link_as_regular_
    file_bytes[…]`): git stores a link as a blob with mode 120000; `git_blob_at` returned its target as file bytes.
    Only modes 100644 and 100755 are file content now; an executable file still reads."""
    CI = load("copy_isolation")
    root = tmp_path / "member"
    git_member(root)
    _commit_link(root, "linked.txt", "x\n")
    (root / "run.sh").write_text("echo\n")
    (root / "run.sh").chmod(0o755)
    _g(root, "add", "run.sh")
    _g(root, "commit", "-q", "-m", "exec")
    with pytest.raises(CI.InspectionFailed, match="120000"):
        CI.git_blob_at(root, "HEAD", "linked.txt")
    assert CI.git_blob_at(root, "HEAD", "run.sh") == b"echo\n" and CI.git_blob_at(root, "HEAD", "a.txt") == b"x\n"


def test_b189_1_census_committed_file_bytes_are_read_only_through_git_blob_at():
    """B189 finding 1, by population: the HEAD/commit readers of file bytes (A, release, KEEP/MERGE, the receipt in H,
    the push gate and the ledger's re-read, the settings comparison) use `git_blob_at`; no kit module reads committed
    bytes with `read_git(..., "show", ...)` any more. Raw `git show` through a tool's own wrapper remains in fleet_ledger
    (register, version.json, workflow names), suite_at_commit (deselect files) and the framework-tag readers
    (prepare_batch, apply_protected): disclosed, not in this census."""
    import re
    raw = re.compile(r"read_git\([^)]*\"show\"")
    hits = {p.name for p in BATCH.glob("*.py") if raw.search(p.read_text())}
    assert hits == set(), hits
    users = {p.name for p in BATCH.glob("*.py") if "CI.git_blob_at(" in p.read_text()}
    assert {"after_run_check.py", "push_batch.py", "fleet_ledger.py", "prepare_launch.py"} <= users, users


def test_b189_1_the_receipt_at_head_is_refused_when_it_is_a_link(tmp_path):
    """B189 finding 1, receipt readers: a committed link whose target text is a well-formed receipt section must not
    read as the receipt (the push gate, the ledger re-read and H read it the same way)."""
    CI = load("copy_isolation")
    root = tmp_path / "member"
    git_member(root)
    _commit_link(root, "docs/RECEIPT.md", "## Attempt a1\nTerminal: ACCEPTED\n")
    with pytest.raises(CI.InspectionFailed, match="not a regular file"):
        CI.git_blob_at(root, "HEAD", "docs/RECEIPT.md")
    LG = load("fleet_ledger")
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    why = LG.reread_receipt(root, "", {"attempt": "a1", "receipt_path": "docs/RECEIPT.md", "receipt_revisions": [head],
                                       "terminal": "ACCEPTED"})
    assert why and "not a regular file" in why, why


@pytest.mark.parametrize("mode", [None, "GIT_GLOB_PATHSPECS", "GIT_ICASE_PATHSPECS"])
def test_c2a9_committed_reads_from_a_nested_folder_and_under_caller_pathspec_modes(tmp_path, mode):
    """FWK-OVSR5's E2i12 advisory (1)-(2) (Codex and agy): from a folder nested in its repository every
    `git_blob_at` lookup refused (top-relative names compared with a folder-relative path), and a caller's
    GIT_GLOB_PATHSPECS / GIT_ICASE_PATHSPECS made `--literal-pathspecs` fail. Both were refusals, not false passes."""
    CI = load("copy_isolation")
    root = tmp_path / "member"
    git_member(root)
    (root / "sub").mkdir()
    (root / "sub" / "f.txt").write_text("f\n")
    _g(root, "add", "sub/f.txt")
    _g(root, "commit", "-q", "-m", "sub")
    env = {**os.environ, mode: "1"} if mode else None
    assert CI.git_blob_at(root / "sub", "HEAD", "f.txt", env=env) == b"f\n"
    assert CI.git_blob_at(root, "HEAD", "sub/f.txt", env=env) == b"f\n"
    assert CI.git_tracked(root / "sub", "f.txt", env=env) is True and CI.git_tracked(root, "sub", env=env) is False


# --- E2i14: REVW9's B191 read (every committed-file reader refuses a link) and FWK-OVSR5's E2i13 advisory -------

def test_b191_1_every_committed_file_reader_refuses_a_committed_link(tmp_path):
    """B191 finding 1 (REVW9 `reviewer_e2i13_probes.py`, six refusal rows): raw `git show` wrappers read a committed
    mode-120000 entry as the file: B8a's exclusion source, the ledger's version, register and workflow names, and the
    two release-source readers. Each now reads through `git_blob_at`'s regular-file contract."""
    root = tmp_path / "member"
    git_member(root)
    (root / ".github" / "workflows").mkdir(parents=True)
    _commit_link(root, ".github/workflows/ci.yml", "name: linked\nrun: pytest --deselect tests/t.py::x\n")
    _commit_link(root, ".aget/version.json", '{"aget_version": "3.35.0"}')
    _commit_link(root, ".aget/fleet/FLEET_STATE.yaml", "fleet: {}\n")
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    S, LG, PB = load("suite_at_commit"), load("fleet_ledger"), load("prepare_batch")
    with pytest.raises(S.CI.InspectionFailed):
        S.ci_exclusions(root, "python3 -m pytest", head)
    assert LG.version_at(root, "", head) == "?"
    with pytest.raises(LG.Unavailable):
        LG.committed_workflows(root, head)
    with pytest.raises(LG.Unavailable):
        LG.members(root, head)
    with pytest.raises(Exception, match="not a regular file"):
        PB.tag_bytes(root, head, ".aget/version.json")


def test_e2i13_advisory_1_a_working_tree_link_is_not_the_file_it_leads_to(tmp_path):
    """FWK-OVSR5's E2i13 advisory (1) (Codex and agy): check A, D and DELETE read the working tree through
    `is_file()`/`read_bytes()`, which follow a link, so a link to matching bytes passed and a folder or dangling link
    read as absent. `tree_print` reads the entry itself."""
    A = load("after_run_check")
    (tmp_path / "real.txt").write_text("x\n")
    (tmp_path / "link.txt").symlink_to(tmp_path / "real.txt")
    (tmp_path / "dangling").symlink_to(tmp_path / "nowhere")
    (tmp_path / "folder").mkdir()
    # changed at E2i15 (labelled): tree_print takes the member root and the relative path, so it walks the whole path
    assert A.tree_print(tmp_path, "real.txt") == A.sha(b"x\n")
    assert A.tree_print(tmp_path, "link.txt").startswith("link:")
    assert A.tree_print(tmp_path, "dangling").startswith("link:")
    assert A.tree_print(tmp_path, "folder").startswith("not a regular file")
    assert A.tree_print(tmp_path, "absent") == "absent"


# --- E2i15: FWK-OVSR6's E2i14 pre-read 1-2 (reproduced): no link followed anywhere on a working-tree path ------------

def test_e2i14_preread_1_a_linked_or_dangling_parent_folder_is_not_read_through(tmp_path):
    """FWK-OVSR6's E2i14 pre-read 1 (Codex #1, agy P1; reproduced 11:19): `tree_print` guarded only the leaf, so
    `<linked folder>/p.py` read as the target file's digest and `<dangling link>/p.py` as absent. A missing folder
    above the file is still absent (positive control)."""
    A = load("after_run_check")
    member, outside = tmp_path / "member", tmp_path / "outside"
    member.mkdir()
    outside.mkdir()
    (outside / "p.py").write_text("x\n")
    (member / "d").symlink_to(outside)
    (member / "gone").symlink_to(tmp_path / "nowhere")
    assert A.tree_print(member, "d/p.py").startswith("unreachable without following a link")
    assert A.tree_print(member, "gone/p.py").startswith("unreachable without following a link")
    assert A.tree_print(member, "missing/p.py") == "absent"


def test_e2i14_preread_2_settings_and_exclusion_sources_are_not_read_through_a_linked_folder(tmp_path, monkeypatch):
    """FWK-OVSR6's E2i14 pre-read 2 (Codex #1, agy P2 and P6; reproduced 11:19): a `.claude` folder that is a link to
    a folder holding `settings.json` gave its hooks with no refusal, and B8a's working-tree exclusion read followed a
    linked `.github` folder the same way."""
    PL, S = load("prepare_launch"), load("suite_at_commit")
    member, outside = tmp_path / "member", tmp_path / "outside"
    git_member(member)
    (outside / "workflows").mkdir(parents=True)
    (outside / "settings.json").write_text(json.dumps({"hooks": {"PreToolUse": []}}))
    (outside / "workflows" / "ci.yml").write_text("name: ci\nrun: pytest --deselect tests/t.py::x\n")
    (member / ".claude").symlink_to(outside)
    (member / ".github").symlink_to(outside)
    monkeypatch.setattr(PL, "STAGE", tmp_path / "stage")
    with pytest.raises(ValueError, match="without following a link"):
        PL.settings_file({"location": str(member), "aget": "synthetic"})
    with pytest.raises(S.CI.InspectionFailed):
        S.ci_exclusions(member, "python3 -m pytest", None)


# --- E2i16: FWK-OVSR6's E2i15 pre-read 1-2 (reproduced) ----------------------------------------------------------------

def test_e2i15_preread_1_a_linked_member_folder_named_with_a_trailing_slash_is_not_read_through(tmp_path):
    """FWK-OVSR6's E2i15 pre-read 1: `<link>/` opens the folder the link leads to even with O_NOFOLLOW, so a member
    folder that is a link, named with a trailing slash, read as the files behind it."""
    PF, A = load("place_file"), load("after_run_check")
    (tmp_path / "real" / "m").mkdir(parents=True)
    (tmp_path / "real" / "m" / "f").write_text("x\n")
    (tmp_path / "member").symlink_to(tmp_path / "real")
    with pytest.raises(PF.Refused):
        PF.read_entry(str(tmp_path / "member") + "/", "m/f")
    assert A.tree_print(str(tmp_path / "member") + "/", "m/f").startswith("unreachable")
    assert PF.read_entry(str(tmp_path / "real") + "/", "m/f") == ("file", b"x\n")      # positive control


def test_e2i15_preread_2_a_nul_in_a_working_tree_path_refuses_without_a_crash(tmp_path):
    """FWK-OVSR6's E2i15 pre-read 2: a NUL byte in the path raised ValueError out of `tree_print` and B8a's working
    tree read, which their callers do not catch, so the check ended without a verdict."""
    A, S = load("after_run_check"), load("suite_at_commit")
    assert A.tree_print(tmp_path, "f\0").startswith("unreachable")
    with pytest.raises(S.CI.InspectionFailed):
        S.ci_exclusions(tmp_path, "python3 -m pytest --deselect-file tests/a\0b.txt", None)


# --- C2a10: FWK-OVSR6's E2i16 pre-read 1-3 (reproduced), and the two escapes both tools named ------------------------

def test_e2i16_preread_1_b8a_never_reads_two_unreadable_readings_as_unchanged(tmp_path):
    """FWK-OVSR6's E2i16 pre-read 1: B8a's tree judgment compared `unreadable` with `unreadable` as unchanged, and
    unreadable → readable as an allowed change; a folder's digest folded a file's error text in. Now each refuses."""
    S = load("suite_at_commit")
    same = [("?? x", ["x"], "unreadable")]
    rec = {"tree_allowed": [], "tree_unallowed": []}
    assert "could not be read" in (S.tree_refusal(rec, "the suite", same, same, []) or "")
    assert "could not be read" in (S.tree_refusal(rec, "the suite", [("?? x", ["x"], "ab:644")], same, ["x"]) or "")
    assert S.tree_refusal(rec, "the suite", [("?? x", ["x"], "ab:644")], [("?? x", ["x"], "ab:644")], []) is None
    folder = tmp_path / "d"
    folder.mkdir()
    (folder / "f").write_text("x")
    (folder / "f").chmod(0)
    try:
        assert S.content_print(folder).startswith("unreadable")
    finally:
        (folder / "f").chmod(0o644)


def test_e2i16_preread_3_a_member_named_with_dot_segments_is_refused(tmp_path):
    """FWK-OVSR6's E2i16 pre-read 3: `<link>/./` and `<link>/sub/../` left `.` or `..` for O_NOFOLLOW to open, which
    goes through the link: the files behind it were read, while `<link>/` refused."""
    PF = load("place_file")
    (tmp_path / "real" / "sub").mkdir(parents=True)
    (tmp_path / "real" / "f").write_text("x\n")
    (tmp_path / "member").symlink_to(tmp_path / "real")
    for spelling in ("member/./", "member/sub/../", "member/."):
        with pytest.raises(PF.Refused):
            PF.read_entry(str(tmp_path / spelling), "f")


def test_e2i16_preread_a_nul_in_a_committed_path_is_refused_not_a_crash(tmp_path):
    """FWK-OVSR6's E2i16 pre-read (both tools): a NUL in a receipt or item path raised ValueError out of the HEAD
    lookup (`git_blob_at`), which the after-run check does not catch, so it ended with no verdict."""
    CI = load("copy_isolation")
    root = tmp_path / "member"
    git_member(root)
    with pytest.raises(CI.InspectionFailed):
        CI.git_blob_at(root, "HEAD", "a\0b")


def test_c2a10_preread_7_b8a_does_not_manufacture_readings(tmp_path):
    """FWK-OVSR6's C2a10 pre-read 7: a FIFO or device read as `absent`, and an unlistable folder as an empty folder's
    digest (os.walk without onerror). Now a non-reading, which B8a refuses."""
    S, CI = load("suite_at_commit"), load("copy_isolation")
    fifo = tmp_path / "f"
    os.mkfifo(fifo)
    assert CI.non_reading(S.content_print(fifo)) and S.content_print(fifo) != "absent"
    sub = tmp_path / "d" / "locked"
    sub.mkdir(parents=True)
    sub.chmod(0)
    try:
        assert CI.non_reading(S.content_print(tmp_path / "d"))
    finally:
        sub.chmod(0o755)


# --- C2a10: REVW9's B193 findings 1-3 -------------------------------------------------------------------------------

@pytest.mark.parametrize("spelling", ["member/./", "member/sub/..", "member/"])
def test_b193_1_the_placer_refuses_a_linked_member_however_its_name_is_written(tmp_path, spelling):
    """B193 finding 1 (REVW9's native placer row): `place_file.py <link>/./ …` exited 0, printed "placed", and wrote
    through the linked member root. The root is now validated by the walk every reader and writer shares."""
    real = tmp_path / "real"
    (real / "sub").mkdir(parents=True)
    (real / "f.txt").write_text("before\n")
    (tmp_path / "member").symlink_to(real)
    staged = tmp_path / "staged"
    staged.write_bytes(b"after\n")
    want = hashlib.sha256(b"after\n").hexdigest()
    p = subprocess.run([sys.executable, str(ROOT / "scripts/migration_kit/place_file.py"), str(tmp_path / spelling),
                        "f.txt", str(staged), want], cwd=real, capture_output=True, text=True)
    assert p.returncode == 2 and "REFUSED" in p.stderr, (p.returncode, p.stdout, p.stderr)
    assert (real / "f.txt").read_text() == "before\n"


@pytest.mark.parametrize("kind", ["folder", "dangling", "link", "fifo"])
def test_b193_2_a_delete_target_that_exists_as_a_non_file_is_not_absent(tmp_path, kind):
    """B193 finding 2 (REVW9's DELETE preparation rows): `plan_receiver` read the target with `is_file()`, so an
    existing link, folder or FIFO planned `noop, pre: absent`, and the after-run check passed. Now it is unsafe."""
    PL = load("prepare_launch")
    loc = tmp_path / "m"
    loc.mkdir()
    t = loc / "gone.txt"
    {"folder": lambda: t.mkdir(), "dangling": lambda: t.symlink_to(tmp_path / "nowhere"),
     "link": lambda: t.symlink_to(loc), "fifo": lambda: os.mkfifo(t)}[kind]()
    item = PL.delete_item(loc, "gone.txt", lambda: b"old\n")
    assert item["op"] == "unsafe" and "member holds a" in item["why"], item
    (tmp_path / "m2").mkdir()
    assert PL.delete_item(tmp_path / "m2", "gone.txt", lambda: b"old\n")["op"] == "noop"      # positive control


def test_b193_3_a_committed_link_with_a_regular_blobs_id_is_not_that_file(tmp_path, monkeypatch):
    """B193 finding 3 (REVW9's ledger and frozen-upstream rows): a link whose target text equals a regular file's
    bytes has the same object id; `payload_findings`' `blob()` compared ids without modes, and `frozen_upstream`
    read the link's target as authored lines. Mode now accompanies the id."""
    LG, V = load("fleet_ledger"), load("verify_extension_survival")
    repo = tmp_path / "fw" / "tpl"
    git_member(repo)
    (repo / "a.txt").write_text("same")
    (repo / "b.txt").symlink_to("same")
    subprocess.run(["git", "-C", str(repo), "add", "a.txt", "b.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "l"], check=True)
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    assert LG.blob(repo, head, "a.txt") and LG.blob(repo, head, "b.txt") != LG.blob(repo, head, "a.txt")
    assert LG.blob(repo, head, "b.txt").startswith("120000")
    monkeypatch.setattr(V, "framework_root", lambda: str(tmp_path / "fw"))
    assert V.frozen_upstream([{"name": "tpl", "tags": [["t", head]]}], "b.txt") is None
    assert V.frozen_upstream([{"name": "tpl", "tags": [["t", head]]}], "a.txt") == {"same"}   # positive control


def test_c2a11_unlistable_folders_and_folder_links_are_not_empty(tmp_path):
    """FWK-OVSR6's C2a10r pre-read: `snapshot()` dropped a folder it could not list, `content_print` read a folder of
    folder links as an empty folder, `_named_file_reading` hid a non-reading's marker, and the placer crashed on a NUL."""
    S, CI = load("suite_at_commit"), load("copy_isolation")
    d = tmp_path / "d"
    d.mkdir()
    (d / "to").symlink_to(tmp_path)
    empty = tmp_path / "e"
    empty.mkdir()
    assert S.content_print(d) != S.content_print(empty)
    clone = tmp_path / "clone"
    git_member(clone)
    (clone / "locked").mkdir()
    (clone / "locked" / "x").write_text("x")
    (clone / "locked").chmod(0)
    try:
        assert S.snapshot(clone) is None
    finally:
        (clone / "locked").chmod(0o755)
    PF = load("place_file")
    assert PF.main([str(tmp_path), "a\x00b", str(tmp_path / "x"), "0" * 64]) == 2


# --- C2a11: REVW9's B194 findings 1 and 3 ----------------------------------------------------------------------------

@pytest.mark.parametrize("spelling", ["member/sub/..", "member/./", "member/"])
def test_b194_1_every_contained_writer_refuses_a_linked_member_however_named(tmp_path, spelling):
    """B194 finding 1 (REVW9's native `write_all` row): the protected all-or-nothing writer wrote through
    `<link>/sub/..` (ok, written [f], before → after). `copy_isolation.member_root` now applies the placer's root
    contract in `root_identity` and `_open_root`, which every contained writer and `write_all` open through."""
    CI = load("copy_isolation")
    real = tmp_path / "real"
    (real / "sub").mkdir(parents=True)
    (real / "f").write_text("before\n")
    (tmp_path / "member").symlink_to(real)
    root = str(tmp_path / spelling)
    res = CI.write_all(root, [("f", b"after\n", hashlib.sha256(b"after\n").hexdigest())],
                       expect_pre={"f": hashlib.sha256(b"before\n").hexdigest()})
    assert not res.ok(), res
    with pytest.raises(CI.ContainmentRefused):
        CI.contained_write(root, "g", b"x")
    assert (real / "f").read_text() == "before\n" and not (real / "g").exists()


def test_b194_3_an_ordinary_file_is_required_whatever_kind_the_sources_hold(tmp_path, monkeypatch):
    """B194 finding 3: two equal non-file identities (sources and member both a link) satisfied `payload_findings`,
    and the non-frozen `upstream_lines` read a committed link's target as authored lines."""
    LG, V = load("fleet_ledger"), load("verify_extension_survival")
    repo = tmp_path / "core"
    git_member(repo)
    (repo / "b.txt").symlink_to("synthetic authored line")
    subprocess.run(["git", "-C", str(repo), "add", "b.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "l"], check=True)
    subprocess.run(["git", "-C", str(repo), "tag", "v1"], check=True)
    head = subprocess.run(["git", "-C", str(repo), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    found = LG.payload_findings(repo, "", head, "tpl", {"b.txt": "present"}, {})   # the kind check precedes sources
    assert any("not a regular file" in f for f in found), found
    monkeypatch.setattr(V, "core_repo", lambda: str(repo))
    with pytest.raises(V.NotRegular):
        V.upstream_lines("b.txt")


@pytest.mark.parametrize("winner", ["folder", "link", "file"])
def test_r55_k3_shared_environment_creation_accepts_concurrent_folder_only(tmp_path, monkeypatch, winner):
    """Force creation between the missing-directory stat and mkdir: both B2 members must proceed for a folder;
    links/files appearing in that same window must still refuse, never write outside the run."""
    import concurrent.futures
    import threading
    ci = load("copy_isolation")
    run = tmp_path / "run"
    outside = tmp_path / "outside"
    run.mkdir()
    outside.mkdir()
    real_same_place = ci._same_place
    barrier = threading.Barrier(2, timeout=10)
    injected = []
    def same_place(root, parents, fd, root_id=None):
        real_same_place(root, parents, fd, root_id)
        if not parents and not (run / ci.KIT_ENV_DIR).exists():
            if winner == "folder":
                barrier.wait()
            elif not injected:
                injected.append(True)
                if winner == "link":
                    (run / ci.KIT_ENV_DIR).symlink_to(outside, target_is_directory=True)
                else:
                    (run / ci.KIT_ENV_DIR).write_text("not a folder")
    monkeypatch.setattr(ci, "_same_place", same_place)
    if winner == "folder":
        with concurrent.futures.ThreadPoolExecutor(max_workers=2) as pool:
            jobs = [pool.submit(ci.contained_env, run, check=False) for _ in range(2)]
            failures = []
            envs = []
            for job in jobs:
                try:
                    envs.append(job.result())
                except Exception as exc:
                    failures.append(f"{type(exc).__name__}: {exc}")
        assert not failures, failures
        assert len(envs) == 2 and envs[0] == envs[1]
        assert (run / ci.KIT_ENV_DIR / "gitconfig").read_bytes().startswith(b"[user]\n")
        assert list((run / ci.KIT_ENV_DIR / "nohooks").iterdir()) == []
    else:
        with pytest.raises(ci.ContainmentRefused, match="symbolic link or not a folder"):
            ci.contained_env(run, check=False)
        assert list(outside.iterdir()) == []
