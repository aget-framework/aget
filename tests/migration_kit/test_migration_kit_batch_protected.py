"""Tests for the batch protected-write list (prepare_batch.py) and the principal's apply script (apply_protected.py).

Hermetic: a fixture framework (template with v3.34.0 / v3.35.0 tags) and a fixture Aget; nothing real is touched.
"""
import importlib.util
import json
import subprocess
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
BATCH = ROOT / "scripts/migration_kit"


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


P = load("prepare_batch", BATCH / "prepare_batch.py")
A = load("apply_protected", BATCH / "apply_protected.py")
SKILL = ".claude/skills/aget-x/SKILL.md"


@pytest.mark.parametrize("release_mode,member_mode", [(0o755, 0o644), (0o644, 0o755)])
def test_round2b_protected_mode_only_release_is_not_silently_applied(world, tmp_path, release_mode, member_mode):
    """B231 falsifier: identical protected bytes with a wrong release executable bit must not be omitted."""
    import stat
    fw, member = world
    tpl = fw / "template-x-aget"
    source = tpl / SKILL
    source.chmod(release_mode)
    sh(tpl, "add", SKILL)
    if release_mode == 0o755:
        sh(tpl, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "release mode")
    sh(tpl, "tag", "-f", "v3.35.0")
    dest = member / SKILL
    dest.parent.mkdir(parents=True)
    dest.write_bytes(source.read_bytes())
    dest.chmod(member_mode)
    sh(member, "add", "-A")
    sh(member, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "member")
    packet, entry = make_list(tmp_path, member)
    code = A.main(["--list", str(packet), "--apply", "--receipt-dir", str(tmp_path)])
    actual = stat.S_IMODE(dest.stat().st_mode)
    assert code != 0 or actual == release_mode, "APPLIED may not omit the listed release executable bit"
    assert code == 0 and actual == release_mode
    operation = next(o for o in entry["ops"] if o["path"] == SKILL)
    assert operation["op"] == "write" and operation["release_mode"] == release_mode
    receipt = json.loads(next(tmp_path.glob("APPLY_RECEIPT*.json")).read_text())
    written = next(f for f in receipt["agets"][0]["files"] if f["path"] == SKILL)
    assert written["release_mode"] == release_mode


@pytest.mark.parametrize("release_mode", [0o644, 0o755])
@pytest.mark.parametrize("legacy_list", [False, True])
def test_round2b_a_noop_with_mode_drift_refuses_by_name(world, tmp_path, release_mode, legacy_list):
    """Equal-byte noops must refuse an executable-bit drift, including older lists without release_mode."""
    fw, member = world
    tpl = fw / "template-x-aget"
    source = tpl / SKILL
    source.chmod(release_mode)
    sh(tpl, "add", SKILL)
    if release_mode == 0o755:
        sh(tpl, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "release mode")
    sh(tpl, "tag", "-f", "v3.35.0")
    dest = member / SKILL
    dest.parent.mkdir(parents=True)
    dest.write_bytes(source.read_bytes())
    dest.chmod(release_mode)
    sh(member, "add", "-A")
    sh(member, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "member")
    packet, entry = make_list(tmp_path, member)
    assert next(o for o in entry["ops"] if o["path"] == SKILL)["op"] == "noop"
    if legacy_list:
        doc = json.loads(packet.read_text())
        for op in doc["agets"][0]["ops"]:
            op.pop("release_mode", None)
        packet.write_text(json.dumps(doc))
    assert A.plan_aget(entry)[0]  # matching executable-bit control
    dest.chmod(0o755 if release_mode == 0o644 else 0o644)
    assert A.main(["--list", str(packet), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    receipt = json.loads(next(tmp_path.glob("APPLY_RECEIPT*.json")).read_text())
    assert receipt["agets"][0]["result"] == "REFUSED"
    assert "RELEASE MODE MISMATCH" in receipt["agets"][0]["why"]


def test_round2b_release_mode_change_after_review_refuses(world, tmp_path):
    """A protected write list binds release mode as well as bytes; moving its source mode invalidates review."""
    fw, member = world
    packet, entry = make_list(tmp_path, member)
    assert A.plan_aget(entry)[0]
    tpl = fw / "template-x-aget"
    (tpl / SKILL).chmod(0o755)
    sh(tpl, "add", SKILL)
    sh(tpl, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "source mode moved")
    sh(tpl, "tag", "-f", "v3.35.0")
    assert A.main(["--list", str(packet), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    receipt = json.loads(next(tmp_path.glob("APPLY_RECEIPT*.json")).read_text())
    assert "SOURCE MODE MISMATCH" in receipt["agets"][0]["why"]


def sh(cwd, *args):
    subprocess.run(["git", "-C", str(cwd), *args], check=True, capture_output=True)


def commit(repo, files, tag):
    for rel, text in files.items():
        p = repo / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(text)
    sh(repo, "add", "-A")
    sh(repo, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", tag)
    sh(repo, "tag", tag)


@pytest.fixture
def world(tmp_path, monkeypatch):
    fw = tmp_path / "fw"
    tpl = fw / "template-x-aget"
    tpl.mkdir(parents=True)
    sh(tpl, "init", "-q")
    commit(tpl, {SKILL: "line a\nline b\n", "AGENTS.md": "t\n"}, "v3.34.0")
    commit(tpl, {SKILL: "line a\nline b\nline c\n", "AGENTS.md": "t2\n"}, "v3.35.0")
    core = fw / "aget"
    core.mkdir()
    sh(core, "init", "-q")
    commit(core, {"README.md": "core\n"}, "v3.35.0")
    monkeypatch.setenv("AGET_FRAMEWORK_ROOT", str(fw))
    monkeypatch.setattr(P.L.W, "SPEC_PATHS", [])
    monkeypatch.setattr(P.L.W, "CORRECTION_ROW_4", [])
    P.UPSTREAM.clear()
    aget = tmp_path / "aget"
    (aget / ".aget").mkdir(parents=True)
    (aget / ".aget" / "version.json").write_text(json.dumps({"template": "x"}))
    (aget / "AGENTS.md").write_text("# A\n@aget-version: 3.34.0\nbody\n")
    sh(aget, "init", "-q")
    # BIND (E2i, R1-T7): the apply acts only at the location the fleet register records for the Aget; each list
    # these tests make rewrites this register to name its members (make_list, list_of)
    monkeypatch.setattr(A, "REGISTER", register(tmp_path, {"fixture-aget": aget}), raising=False)
    return fw, aget


def register(tmp_path, members):
    """A fleet register file (FLEET_STATE.yaml's shape) listing `members` (name -> location)."""
    path = tmp_path / "FLEET_STATE.yaml"
    path.write_text("fleet:\n  main:\n    agents:\n" + "".join(
        f"    - agent_name: {n}\n      location: '{loc}'\n" for n, loc in members.items()))
    return path


def make_list(tmp_path, aget):
    entry = P.prepare("fixture-aget", str(aget))
    doc = {"batch": "t", "apply_script_sha256": A.self_sha(), "agets": [entry]}
    register(tmp_path, {entry["aget"]: entry["location"]})
    path = tmp_path / "list.json"
    path.write_text(json.dumps(doc))
    return path, entry


def ops(entry):
    return {o["path"]: o["op"] for o in entry["ops"]}


@pytest.mark.parametrize("existing", [False, True])
def test_round2_protected_apply_preserves_release_executable_bit(world, tmp_path, existing):
    """M-6: the apply route writes the release mode through the contained writer for new and existing files."""
    fw, aget = world
    tpl = fw / "template-x-aget"
    (tpl / SKILL).chmod(0o755)
    sh(tpl, "add", SKILL)
    sh(tpl, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "release mode")
    # Adjust only this hermetic fixture's release tag, never a public tag.
    sh(tpl, "tag", "-f", "v3.35.0")
    if existing:
        (aget / SKILL).parent.mkdir(parents=True)
        (aget / SKILL).write_text("line a\nline b\n")
        (aget / SKILL).chmod(0o644)
    path, entry = make_list(tmp_path, aget)
    assert A.main(["--list", str(path), "--apply", "--receipt-dir", str(tmp_path)]) == 0
    assert (aget / SKILL).stat().st_mode & 0o111 == 0o111


def test_absent_skill_is_written_and_version_line_replaced(world, tmp_path):
    _, aget = world
    _, entry = make_list(tmp_path, aget)
    assert ops(entry) == {SKILL: "write", "AGENTS.md": "replace-line"}


def test_old_release_copy_is_write_and_current_is_noop(world, tmp_path):
    _, aget = world
    (aget / SKILL).parent.mkdir(parents=True)
    (aget / SKILL).write_text("line a\nline b\n")
    assert ops(make_list(tmp_path, aget)[1])[SKILL] == "write"
    (aget / SKILL).write_text("line a\nline b\nline c\n")
    assert ops(make_list(tmp_path, aget)[1])[SKILL] == "noop"


def test_write_upstream_only_for_an_exact_upstream_version_else_hold(world, tmp_path):
    """Independent review (wrapper, packet r6, F-1): a file whose every line some upstream version holds was
    `write-upstream` and overwritten, so a receiver's deletion, reordering, re-indentation or repeated line was lost.
    Now only a file that is byte for byte one upstream version is `write-upstream`; the others hold with 0 authored
    lines. An authored line still holds with its count."""
    fw, aget = world
    tpl = fw / "template-x-aget"
    sh(tpl, "checkout", "-q", "v3.34.0")
    commit(tpl, {SKILL: "line q\nline a\n"}, "v3.20.0")                    # an older upstream version
    (aget / SKILL).parent.mkdir(parents=True)
    for text in ("line b\nline a\n",                                       # reordered
                 "line a\n",                                               # a line deleted
                 "  line a\nline b\n",                                     # re-indented
                 "line a\nline a\nline b\n",                               # a line repeated
                 "line a\nline b\n\n"):                                    # trailing blank line
        (aget / SKILL).write_text(text)
        P.UPSTREAM.clear()
        e = make_list(tmp_path, aget)[1]
        assert ops(e)[SKILL] == "hold", text
        assert [o["authored_lines"] for o in e["ops"] if o["path"] == SKILL] == [0]
    (aget / SKILL).write_text("line q\nline a\n")                         # exactly the v3.20.0 bytes
    P.UPSTREAM.clear()
    assert ops(make_list(tmp_path, aget)[1])[SKILL] == "write-upstream"
    assert P.classify_file(b"line b\nline a\n", b"x", b"y", {"line a", "line b"}) == ("hold", 0)  # no digests: hold
    (aget / SKILL).write_text("line a\nmy own line\n")
    P.UPSTREAM.clear()
    e = make_list(tmp_path, aget)[1]
    assert ops(e)[SKILL] == "hold"
    assert [o["authored_lines"] for o in e["ops"] if o["path"] == SKILL] == [1]


def test_version_line_not_exactly_once_is_held(world, tmp_path):
    _, aget = world
    (aget / "AGENTS.md").write_text("@aget-version: 3.34.0\n@aget-version: 3.34.0\n")
    assert ops(make_list(tmp_path, aget)[1])["AGENTS.md"] == "hold-line"


def test_dry_run_writes_nothing(world, tmp_path):
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    assert A.main(["--list", str(lst), "--receipt-dir", str(tmp_path)]) == 0
    assert not (aget / SKILL).exists()
    assert "3.34.0" in (aget / "AGENTS.md").read_text()


def test_apply_writes_listed_bytes_and_a_receipt(world, tmp_path):
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    assert A.main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 0
    assert (aget / SKILL).read_text() == "line a\nline b\nline c\n"
    assert "@aget-version: 3.35.0" in (aget / "AGENTS.md").read_text()
    receipt = json.loads(next(tmp_path.glob("APPLY_RECEIPT_batcht_*.json")).read_text())
    assert receipt["agets"][0]["result"] == "APPLIED"
    assert all(f["ok"] for f in receipt["agets"][0]["files"])


def test_a_changed_aget_is_refused_whole(world, tmp_path):
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    (aget / "AGENTS.md").write_text("# A\n@aget-version: 3.34.0\nedited after the list\n")
    assert A.main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    assert not (aget / SKILL).exists()  # nothing written at that Aget


def test_held_files_are_never_touched(world, tmp_path):
    _, aget = world
    (aget / SKILL).parent.mkdir(parents=True)
    (aget / SKILL).write_text("line a\nmy own line\n")
    lst, _ = make_list(tmp_path, aget)
    assert A.main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 0
    assert (aget / SKILL).read_text() == "line a\nmy own line\n"


def test_an_unreviewed_script_refuses(world, tmp_path):
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    doc = json.loads(lst.read_text())
    doc["apply_script_sha256"] = "0" * 64
    lst.write_text(json.dumps(doc))
    assert A.main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 2
    assert not (aget / SKILL).exists()


# --- gh#1569 skill tracking in a write list (batch 2, principal go 2026-09-28) -------------------------------------

def test_rewrite_claude_ignore_turns_the_bare_rule_into_the_tracked_skills_form():
    out = A.rewrite_claude_ignore("node_modules/\n.claude/\n*.log\n")
    assert out == "node_modules/\n" + A.CLAUDE_IGNORE_NEW + "\n*.log\n"
    assert "!.claude/skills/" in out and ".claude/*" in out


@pytest.mark.parametrize("text", ["*.log\n", ".claude/\n.claude/\n", ".claude/*\n!.claude/skills/\n", ".claude\n"])
def test_rewrite_claude_ignore_refuses_anything_but_exactly_one_bare_rule(text):
    assert A.rewrite_claude_ignore(text) is None


def test_the_rewrite_actually_untracks_skills_in_git(tmp_path):
    repo = tmp_path / "r"
    (repo / ".claude" / "skills" / "s").mkdir(parents=True)
    (repo / ".claude" / "skills" / "s" / "SKILL.md").write_text("x\n")
    (repo / ".claude" / "settings.local.json").write_text("{}\n")
    (repo / ".gitignore").write_text(".claude/\n")
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    ign = lambda p: subprocess.run(["git", "-C", str(repo), "check-ignore", "--no-index", p]).returncode == 0
    assert ign(".claude/skills/s/SKILL.md")
    (repo / ".gitignore").write_text(A.rewrite_claude_ignore(".claude/\n"))
    assert not ign(".claude/skills/s/SKILL.md")          # BARE exit code: 1 = not ignored
    assert ign(".claude/settings.local.json")            # the rest of .claude/ stays ignored


def test_apply_plans_a_rewrite_op_and_refuses_a_stale_pre(tmp_path):
    loc = tmp_path / "a"
    loc.mkdir()
    sh(loc, "init", "-q")
    (loc / ".gitignore").write_text("x\n.claude/\n")
    pre = A.sha(b"x\n.claude/\n")
    post = A.sha(A.rewrite_claude_ignore("x\n.claude/\n").encode())
    entry = {"location": str(loc), "head": "(unborn)",
             "ops": [{"path": ".gitignore", "op": "rewrite-claude-ignore", "pre": pre, "post": post}]}
    ok, why, actions = A.plan_aget(entry)
    assert ok and actions[0][2] == post
    (loc / ".gitignore").write_text("changed\n.claude/\n")
    assert not A.plan_aget(entry)[0]


def _linked(aget, tmp_path, where):
    """Make the skill path go through a symbolic link: `leaf` links the file, `parent` links its folder, `dangling`
    links the file to a path that does not exist yet. Returns the outside path the link leads to."""
    outside = tmp_path / "outside"
    outside.mkdir(exist_ok=True)
    skill = aget / SKILL
    skill.parent.parent.mkdir(parents=True, exist_ok=True)
    if where == "parent":
        (outside / "aget-x").mkdir(exist_ok=True)
        sentinel = outside / "aget-x" / "SKILL.md"
        sentinel.write_text("line a\nline b\n")
        skill.parent.symlink_to(outside / "aget-x")
    else:
        skill.parent.mkdir(exist_ok=True)
        sentinel = outside / "SKILL.md"
        if where == "leaf":
            sentinel.write_text("line a\nline b\n")
        skill.symlink_to(sentinel)
    return sentinel


@pytest.mark.parametrize("where", ["leaf", "parent", "dangling"])
def test_a_linked_destination_is_held_when_listed_and_refused_when_applied(world, tmp_path, where):
    """Independent review (wrapper, packet r6, F-2): apply read and wrote through a symbolic link, so a listed path
    linked elsewhere (another repository) was written there; a dangling link created a file outside the Aget and the
    read-back said APPLIED. The list now holds such a path, and apply refuses the whole Aget at its plan for a list
    that names it as a write anyway; the outside file is unchanged or not created."""
    _, aget = world
    sentinel = _linked(aget, tmp_path, where)
    before = sentinel.read_text() if sentinel.exists() else None
    lst, entry = make_list(tmp_path, aget)
    held = [o for o in entry["ops"] if o["path"] == SKILL][0]
    assert held["op"] == "unsafe" and "unsafe path" in held["why"]          # R3 (B131): `unsafe`, never a hold
    doc = json.loads(lst.read_text())
    doc["agets"][0]["ops"] = [{"path": SKILL, "op": "write", "pre": A.sha(sentinel.read_bytes()) if before else
                               "absent", "post": A.sha(b"line a\nline b\nline c\n"),
                               "source": "template-x-aget@v3.35.0:" + SKILL,
                               "source_sha256": A.sha(b"line a\nline b\nline c\n")}]
    lst.write_text(json.dumps(doc))
    assert A.main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    assert (sentinel.read_text() if sentinel.exists() else None) == before


def test_apply_tests_the_destination_again_immediately_before_writing(world, tmp_path, monkeypatch):
    """The plan's test is repeated at the write: a link that appears after the plan is refused there, nothing is
    written through it, and the receipt says why."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    real_plan = A.plan_aget

    def plan_then_link(entry):
        result = real_plan(entry)
        _linked(aget, tmp_path, "dangling")                                 # the link appears after the plan
        return result

    monkeypatch.setattr(A, "plan_aget", plan_then_link)
    assert A.main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    assert not (tmp_path / "outside" / "SKILL.md").exists()
    receipt = json.loads(next(tmp_path.glob("APPLY_RECEIPT_batcht_*.json")).read_text())
    assert receipt["agets"][0]["result"] == "REFUSED" and "UNSAFE PATH" in receipt["agets"][0]["why"]


def test_destination_refusal_reads_every_component():
    """copy_isolation.destination_refusal: absolute and climbing paths, a linked root, a linked folder on the way, a
    linked leaf; an ordinary path inside the folder, existing or not, is accepted."""
    import tempfile
    CI = load("copy_isolation", BATCH / "copy_isolation.py")
    with tempfile.TemporaryDirectory() as d:
        root = Path(d) / "m"
        (root / "a" / "b").mkdir(parents=True)
        (root / "a" / "b" / "f").write_text("x")
        assert CI.destination_refusal(root, "a/b/f") is None and CI.destination_refusal(root, "a/new/g") is None
        assert CI.destination_refusal(root, "/etc/passwd") and CI.destination_refusal(root, "a/../../x")
        (root / "a" / "l").symlink_to(root / "a" / "b")                    # a link that stays inside: still refused
        assert "symbolic link" in CI.destination_refusal(root, "a/l/f")
        (root / "a" / "b" / "g").symlink_to(Path(d) / "elsewhere")
        assert "symbolic link" in CI.destination_refusal(root, "a/b/g")
        linked_root = Path(d) / "lr"
        linked_root.symlink_to(root)
        assert "symbolic link" in CI.destination_refusal(linked_root, "a/b/f")


# --- Gate 3 of the v3.36.0 kit design pass (v336-release:R28): R4 all-or-nothing apply and R1 at the act ----------
#
# Each test below fails on 34353311 for the defect it names and passes after the change. The seam helper reaches the
# member writes through whichever writer the code under test has: the contained writer (after the change) or
# Path.write_bytes (at 34353311), so the same test runs on both.

import os  # noqa: E402
import signal  # noqa: E402
import sys  # noqa: E402

NEW_SKILL = "line a\nline b\nline c\n"


def member_write_hook(monkeypatch, members, hook):
    """Call hook(member, rel, n) before each write the apply makes into one of `members`; n counts that member's
    writes from 1 (a rollback's restore counts too)."""
    counts = {}

    def note(root, rel):
        m = str(root)
        counts[m] = counts.get(m, 0) + 1
        hook(Path(m), str(rel), counts[m])

    real_cw = getattr(A.CI, "contained_write", None)
    if real_cw is not None:
        def cw(root, rel, data, **kw):
            note(root, rel)
            return real_cw(root, rel, data, **kw)
        monkeypatch.setattr(A.CI, "contained_write", cw)
    real_wb = Path.write_bytes

    def wb(self, data):
        for m in members:
            if str(self).startswith(str(m) + os.sep):
                note(m, os.path.relpath(self, m))
                break
        return real_wb(self, data)
    monkeypatch.setattr(Path, "write_bytes", wb)


def new_aget(tmp_path, name, commit_it=False):
    """Another fixture Aget beside the world's, with the same starting files."""
    aget = tmp_path / name
    (aget / ".aget").mkdir(parents=True)
    (aget / ".aget" / "version.json").write_text(json.dumps({"template": "x"}))
    (aget / "AGENTS.md").write_text("# A\n@aget-version: 3.34.0\nbody\n")
    sh(aget, "init", "-q")
    if commit_it:
        sh(aget, "add", "-A")
        sh(aget, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "-m", "c")
    return aget


def list_of(tmp_path, agets):
    entries = [P.prepare(a.name, str(a)) for a in agets]
    register(tmp_path, {e["aget"]: e["location"] for e in entries})
    path = tmp_path / "list.json"
    path.write_text(json.dumps({"batch": "t", "apply_script_sha256": A.self_sha(), "agets": entries}))
    return path


def snapshot(aget):
    """Every entry under the Aget (outside .git): kind, mode and bytes."""
    out = {}
    for d, dirs, files in os.walk(aget):
        dirs[:] = [x for x in dirs if x != ".git"]
        for n in dirs + files:
            p = Path(d) / n
            st = os.lstat(p)
            out[str(p.relative_to(aget))] = (st.st_mode, p.read_bytes() if p.is_file() and not p.is_symlink() else None)
    return out


def receipt_of(tmp_path):
    return json.loads(next(tmp_path.glob("APPLY_RECEIPT_batcht_*.json")).read_text())


def run_main(argv):
    """A.main, with any escaping exception (a traceback at the command line) turned into a test failure."""
    try:
        return A.main(argv)
    except BaseException as e:   # noqa: BLE001
        pytest.fail(f"apply ended in a traceback: {type(e).__name__}: {e}")


def test_r4_t1_a_link_found_at_the_write_rolls_back_earlier_writes(world, tmp_path, monkeypatch):
    """R4-T1, J-4 (C3). At 34353311 a refusal at the per-write re-check `break`s with op 1 already written, and the
    member reads VERIFY-FAILED. Now op 1 is rolled back and read back, and the member reads REFUSED naming it."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    outside = tmp_path / "outside_agents.md"
    outside.write_text("# A\n@aget-version: 3.34.0\nbody\n")
    before = snapshot(aget)
    real = A.CI.destination_refusal

    def link_after_op1(root, rel, *args, **kw):
        if (aget / SKILL).exists() and not (aget / "AGENTS.md").is_symlink():
            (aget / "AGENTS.md").unlink()
            (aget / "AGENTS.md").symlink_to(outside)
        return real(root, rel, *args, **kw)
    monkeypatch.setattr(A.CI, "destination_refusal", link_after_op1)
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    rec = receipt_of(tmp_path)["agets"][0]
    assert rec["result"] == "REFUSED" and rec["rolled_back"] == [SKILL]
    assert not (aget / SKILL).exists() and not (aget / ".claude").exists()      # op 1 and its folders undone
    assert outside.read_text() == "# A\n@aget-version: 3.34.0\nbody\n"
    after = snapshot(aget)
    after.pop("AGENTS.md"), before.pop("AGENTS.md")                              # the test itself linked it
    assert after == before


def test_r4_t2_a_listed_absent_path_that_is_a_folder_refuses_at_the_plan(world, tmp_path):
    """R4-T2, J-6 (C2). At 34353311 a folder reads as absent, op 1 is written, then IsADirectoryError, no receipt."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    doc = json.loads(lst.read_text())
    (aget / "docs" / "dir_target").mkdir(parents=True)
    doc["agets"][0]["ops"].append({"path": "docs/dir_target", "op": "write", "pre": "absent",
                                   "post": A.sha(NEW_SKILL.encode()), "source": "template-x-aget@v3.35.0:" + SKILL,
                                   "source_sha256": A.sha(NEW_SKILL.encode())})
    lst.write_text(json.dumps(doc))
    before = snapshot(aget)
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    rec = receipt_of(tmp_path)["agets"][0]
    assert rec["result"] == "REFUSED" and "not a regular file" in rec["why"]
    assert snapshot(aget) == before


def test_r4_t3_a_moved_head_or_a_list_without_head_refuses(world, tmp_path):
    """R4-T3 (C2). At 34353311 HEAD is not compared (apply_protected.py:18-19): APPLIED."""
    _, aget = world
    aget2 = new_aget(tmp_path, "moved", commit_it=True)
    lst = list_of(tmp_path, [aget2])
    sh(aget2, "-c", "user.name=t", "-c", "user.email=t@t", "commit", "-q", "--allow-empty", "-m", "moved")
    before = snapshot(aget2)
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    assert receipt_of(tmp_path)["agets"][0]["result"] == "REFUSED" and snapshot(aget2) == before
    for f in tmp_path.glob("APPLY_RECEIPT_*.json"):
        f.unlink()
    doc = json.loads(lst.read_text())
    doc["agets"][0].pop("head", None)
    lst.write_text(json.dumps(doc))
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    assert receipt_of(tmp_path)["agets"][0]["result"] == "REFUSED" and snapshot(aget2) == before


def _fail_member_write(monkeypatch, members, member, at, exc):
    def hook(m, rel, n):
        if m == member and n == at:
            raise exc
    member_write_hook(monkeypatch, members, hook)


def test_r4_t4_a_failed_second_write_restores_the_first(world, tmp_path, monkeypatch):
    """R4-T4 (C3). At 34353311 the OSError propagates: a traceback, op 1 written, no receipt."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    before = snapshot(aget)
    _fail_member_write(monkeypatch, [aget], aget, 2, OSError("disk full"))
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    rec = receipt_of(tmp_path)["agets"][0]
    assert rec["result"] == "REFUSED" and rec["rolled_back"] == [SKILL] and "disk full" in rec["why"]
    assert snapshot(aget) == before


def test_r4_t10_rollback_incomplete_is_its_own_result(world, tmp_path, monkeypatch):
    """R4-T10 (C4). The second write fails and so does the restore of the first. Expected: exit 3, ROLLBACK-INCOMPLETE
    naming op 1 (never REFUSED), a reader that marks it INCONCLUSIVE, and a re-run that refuses the member as STALE
    and writes nothing. At 34353311: an OSError traceback and no receipt."""
    _, aget = world
    (aget / SKILL).parent.mkdir(parents=True)
    (aget / SKILL).write_text("line a\nline b\n")                                # op 1 has prior bytes to restore
    lst, entry = make_list(tmp_path, aget)
    assert ops(entry)[SKILL] == "write"

    def hook(m, rel, n):
        if n in (2, 3):
            raise OSError(f"write {n} fails")
    member_write_hook(monkeypatch, [aget], hook)
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 3
    rec = receipt_of(tmp_path)["agets"][0]
    assert rec["result"] == "ROLLBACK-INCOMPLETE" and [x["path"] for x in rec["not_restored"]] == [SKILL]
    assert rec["result"] not in (None, "APPLIED")                                # after_run_check.py:417: INCONCLUSIVE
    monkeypatch.undo()
    monkeypatch.setattr(A, "REGISTER", tmp_path / "FLEET_STATE.yaml", raising=False)   # E2i: undo() removed the register
    held = snapshot(aget)
    for f in tmp_path.glob("APPLY_RECEIPT_*.json"):
        f.unlink()
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    rec = receipt_of(tmp_path)["agets"][0]
    assert rec["result"] == "REFUSED" and "STALE" in rec["why"] and snapshot(aget) == held


@pytest.mark.parametrize("case", ["runtime-error", "write-all-raises"])
def test_r4_t11_any_exception_reaches_rollback(world, tmp_path, monkeypatch, case):
    """R4-T11 (C3, C4). (a) A RuntimeError, not an OSError, at the second write: op 1 restored, REFUSED. (b) The
    writer makes one write and then raises: ROLLBACK-INCOMPLETE, never an unverified REFUSED. At 34353311: (a) a
    traceback, no receipt; (b) the seam and the result value do not exist, and the member reads APPLIED."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    before = snapshot(aget)
    if case == "runtime-error":
        _fail_member_write(monkeypatch, [aget], aget, 2, RuntimeError("unexpected"))
        assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
        rec = receipt_of(tmp_path)["agets"][0]
        assert rec["result"] == "REFUSED" and rec["rolled_back"] == [SKILL] and snapshot(aget) == before
    else:
        def one_write_then_raise(root, actions, root_id=None):
            rel, data, _ = actions[0]
            (Path(root) / rel).parent.mkdir(parents=True, exist_ok=True)
            (Path(root) / rel).write_bytes(data)
            raise RuntimeError("after one write")
        monkeypatch.setattr(A.CI, "write_all", one_write_then_raise, raising=False)
        assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 3
        assert receipt_of(tmp_path)["agets"][0]["result"] == "ROLLBACK-INCOMPLETE"


@pytest.mark.parametrize("how", ["keyboard", "sigterm"])
def test_r4_t12_an_interrupt_is_c5_and_stops_the_batch_cleanly(world, tmp_path, monkeypatch, how):
    """R4-T12 (C5), closing design-read-2 D-7: an interrupt matches C3's 'any exception after the first write' too,
    and C5 must win. Three members; the interrupt comes at member 2's second write. Expected: member 1 APPLIED, member
    2 REFUSED with op 1 restored, member 3 NOT-STARTED, the receipt written, exit 130, no traceback. At 34353311: a
    KeyboardInterrupt escapes (sigterm: no handler is installed), no receipt, member 2 partly written."""
    _, a1 = world
    a2, a3 = new_aget(tmp_path, "two"), new_aget(tmp_path, "three")
    lst = list_of(tmp_path, [a1, a2, a3])
    b2, b3 = snapshot(a2), snapshot(a3)

    def hook(m, rel, n):
        if m == a2 and n == 2:
            if how == "keyboard":
                raise KeyboardInterrupt
            handler = signal.getsignal(signal.SIGTERM)
            if not callable(handler):
                raise AssertionError("no SIGTERM handler is installed during the apply")
            handler(signal.SIGTERM, None)
    member_write_hook(monkeypatch, [a1, a2, a3], hook)
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 130
    got = {r["aget"]: r for r in receipt_of(tmp_path)["agets"]}
    assert got["aget"]["result"] == "APPLIED"
    assert got["two"]["result"] == "REFUSED" and got["two"]["rolled_back"] == [SKILL]
    assert got["three"]["result"] == "NOT-STARTED"
    assert snapshot(a2) == b2 and snapshot(a3) == b3


KILL_RUNNER = r'''
import importlib.util, os, sys
from pathlib import Path
spec = importlib.util.spec_from_file_location("apply_protected", sys.argv[1])
A = importlib.util.module_from_spec(spec); spec.loader.exec_module(A)
A.REGISTER = Path(os.environ.get("KIT_TEST_REGISTER", getattr(A, "REGISTER", "")))   # the test's fleet register (BIND, E2i)
member, n = sys.argv[2], [0]
def note(root):
    if str(root) == member:
        n[0] += 1
        if n[0] == 2:
            os._exit(137)
cw = getattr(A.CI, "contained_write", None)
if cw is not None:
    def wrapped(root, rel, data, **kw):
        note(root); return cw(root, rel, data, **kw)
    A.CI.contained_write = wrapped
wb = Path.write_bytes
def wbw(self, data):
    if str(self).startswith(member + os.sep):
        note(member)
    return wb(self, data)
Path.write_bytes = wbw
sys.exit(A.main(sys.argv[3:]))
'''


def test_r4_t13_a_killed_run_leaves_an_in_progress_receipt(world, tmp_path):
    """R4-T13 (C6). The apply is killed (os._exit) right after member 1's first write. Expected: a receipt on disk
    with the member IN-PROGRESS; op 1's target all post bytes, op 2's all pre bytes; a re-run refuses the member as
    STALE and writes nothing. At 34353311 no receipt exists: it is written only at the end."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    runner = tmp_path / "kill_runner.py"
    runner.write_text(KILL_RUNNER)
    p = subprocess.run([sys.executable, str(runner), str(BATCH / "apply_protected.py"), str(aget), "--list", str(lst),
                        "--apply", "--receipt-dir", str(tmp_path)], capture_output=True, text=True,
                       env={**os.environ, "KIT_TEST_REGISTER": str(getattr(A, "REGISTER", ""))})
    assert p.returncode == 137
    receipts = list(tmp_path.glob("APPLY_RECEIPT_batcht_*.json"))
    assert receipts, "no receipt after a killed run"
    assert json.loads(receipts[0].read_text())["agets"][0]["result"] == "IN-PROGRESS"
    assert (aget / SKILL).read_text() == NEW_SKILL
    assert (aget / "AGENTS.md").read_text() == "# A\n@aget-version: 3.34.0\nbody\n"
    held = snapshot(aget)
    receipts[0].unlink()
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    rec = receipt_of(tmp_path)["agets"][0]
    assert rec["result"] == "REFUSED" and "STALE" in rec["why"] and snapshot(aget) == held


def test_r4_t14a_one_members_exception_does_not_stop_the_others(world, tmp_path, monkeypatch):
    """R4-T14 (a), clause 3, J-7 class in apply_protected: member 1's plan raises. Expected: member 2 applied, both
    named in the receipt, nonzero exit, no traceback. At 34353311: a RuntimeError traceback and no receipt."""
    _, a1 = world
    a2 = new_aget(tmp_path, "two")
    lst = list_of(tmp_path, [a1, a2])
    real = A.plan_aget

    def plan(entry):
        if entry["aget"] == "aget":
            raise RuntimeError("member 1 cannot be planned")
        return real(entry)
    monkeypatch.setattr(A, "plan_aget", plan)
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    got = {r["aget"]: r["result"] for r in receipt_of(tmp_path)["agets"]}
    assert got == {"aget": "REFUSED", "two": "APPLIED"}


def test_r1_t6_a_hard_linked_member_file_is_never_written_through(world, tmp_path):
    """R1-T6, J-5. A member file hard-linked to a file in another repository: the list holds it, and apply refuses a
    list that names it as a write anyway; the other file is unchanged. At 34353311 the list says `write` and
    write_bytes truncates the shared inode in place, so the other repository's file changes."""
    _, aget = world
    other = tmp_path / "other_repo" / "SKILL.md"
    other.parent.mkdir()
    other.write_text("line a\nline b\n")
    (aget / SKILL).parent.mkdir(parents=True)
    os.link(other, aget / SKILL)
    lst, entry = make_list(tmp_path, aget)
    assert [o["op"] for o in entry["ops"] if o["path"] == SKILL] == ["unsafe"]   # R3: refused paths are unsafe
    doc = json.loads(lst.read_text())
    doc["agets"][0]["ops"] = [{"path": SKILL, "op": "write", "pre": A.sha(b"line a\nline b\n"),
                               "post": A.sha(NEW_SKILL.encode()), "source": "template-x-aget@v3.35.0:" + SKILL,
                               "source_sha256": A.sha(NEW_SKILL.encode())}]
    lst.write_text(json.dumps(doc))
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    assert other.read_text() == "line a\nline b\n"


def _frames():
    f = sys._getframe(1)
    while f is not None:
        yield f
        f = f.f_back


def test_r1_t17_a_parent_swapped_after_every_check_is_refused_at_the_act(world, tmp_path, monkeypatch):
    """R1-T17 at the apply site, closing design-read-2 D-6 there: every check sees the real folder, and the write
    sees the parent swapped for a link to an outside folder (after each check made outside the plan, so the plan's
    own read sees the real file). Expected: no outside byte changes. At 34353311
    destination_refusal passes and write_bytes then writes through the swapped link."""
    _, aget = world
    (aget / SKILL).parent.mkdir(parents=True)
    (aget / SKILL).write_text("line a\nline b\n")
    lst, entry = make_list(tmp_path, aget)
    assert ops(entry)[SKILL] == "write"
    outside = tmp_path / "outside_dir"
    outside.mkdir()
    (outside / "SKILL.md").write_text("outside bytes\n")
    parent, hidden = (aget / SKILL).parent, (aget / SKILL).parent.with_name("aget-x.real")
    real = A.CI.destination_refusal

    def swap_after_check(root, rel, *args, **kw):
        if parent.is_symlink():                                                  # un-swap: the check sees the truth
            parent.unlink()
            hidden.rename(parent)
        why = real(root, rel, *args, **kw)
        in_plan = any(f.f_code.co_name == "plan_aget" for f in _frames())
        if rel == SKILL and not why and not in_plan:                             # swap: the act sees the link
            parent.rename(hidden)
            parent.symlink_to(outside)
        return why
    monkeypatch.setattr(A.CI, "destination_refusal", swap_after_check)
    rc = run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)])
    assert (outside / "SKILL.md").read_text() == "outside bytes\n"
    assert sorted(p.name for p in outside.iterdir()) == ["SKILL.md"]
    # The link is still in place when the rollback reads back, so C4 (ROLLBACK-INCOMPLETE, exit 3) is the honest
    # result; C3 (REFUSED, exit 1) if it was undone first. Never APPLIED.
    assert (rc, receipt_of(tmp_path)["agets"][0]["result"]) in ((1, "REFUSED"), (3, "ROLLBACK-INCOMPLETE"))


def test_a_member_with_nothing_to_write_reads_applied(world, tmp_path):
    """Found while building Gate 3 stage B (not a design-read finding): with the contained writer, a member whose ops
    are all `noop` or `hold` must still read APPLIED with no files, not ROLLBACK-INCOMPLETE. 34353311 reads APPLIED;
    this pins it."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    doc = json.loads(lst.read_text())
    doc["agets"][0]["ops"] = [o for o in doc["agets"][0]["ops"] if o["op"] in ("hold", "noop")]
    lst.write_text(json.dumps(doc))
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 0
    assert receipt_of(tmp_path)["agets"][0]["result"] == "APPLIED"


# --- REVW's B141 read of stage A (REPLY_2026-10-02_claude_codex_B141_stageA_class_review.md) ----------------------
#
# Each test is REVW's falsifier (reviewer_contract_probes.py), carried into the kit suite. They are defects of the new
# stage-A code, so their failing-first control is the stage-B draft (GATE3_DRAFT_stageB.patch), recorded in
# gate3/CONTROL_stageB2.json; at 34353311 the code they test does not exist in this form.

def test_b141_1_phase_b_retests_the_listed_pre_bytes(world, tmp_path, monkeypatch):
    """B141 finding 1 (HIGH). Member 1 is edited after both members are planned, HEAD unchanged. Expected: member 1
    REFUSED with the edit kept, member 2 APPLIED, exit 1. Stage B overwrote the edit and read both APPLIED."""
    _, a1 = world
    a2 = new_aget(tmp_path, "two")
    lst = list_of(tmp_path, [a1, a2])
    real = A.plan_aget
    edited = "# A\n@aget-version: 3.34.0\nnew principal bytes after planning\n"
    done = []

    def plan(e):
        answer = real(e)
        if e["aget"] == "two" and not done:
            (a1 / "AGENTS.md").write_text(edited)
            done.append(1)
        return answer
    monkeypatch.setattr(A, "plan_aget", plan)
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    assert (a1 / "AGENTS.md").read_text() == edited
    assert {r["aget"]: r["result"] for r in receipt_of(tmp_path)["agets"]} == {"aget": "REFUSED", "two": "APPLIED"}


def test_b141_3_an_interrupt_during_the_rollback_is_still_c5(world, tmp_path, monkeypatch):
    """B141 finding 3 (HIGH). Member 1's second write fails; while its first file is being restored, the installed
    SIGTERM handler runs. Expected: exit 130 and member 2 NOT-STARTED. Stage B swallowed the interrupt in the
    rollback: exit 3 and member 2 APPLIED."""
    _, a1 = world
    a2 = new_aget(tmp_path, "two")
    (a1 / SKILL).parent.mkdir(parents=True)
    (a1 / SKILL).write_text("line a\nline b\n")
    lst = list_of(tmp_path, [a1, a2])

    def hook(m, rel, n):
        if m == a1 and n == 2:
            raise OSError("second write fails")
        if m == a1 and n == 3:
            handler = signal.getsignal(signal.SIGTERM)
            assert callable(handler)
            handler(signal.SIGTERM, None)
    member_write_hook(monkeypatch, [a1, a2], hook)
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 130
    assert {r["aget"]: r["result"] for r in receipt_of(tmp_path)["agets"]}["two"] == "NOT-STARTED"


def test_b141_4_a_receipt_that_cannot_be_written_refuses_without_a_traceback(world, tmp_path, monkeypatch):
    """B141 finding 4 (MEDIUM). The IN-PROGRESS receipt write raises OSError once. Expected: no traceback, a nonzero
    exit, and the member refused with nothing written. Stage B let the OSError escape main."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    before = snapshot(aget)
    real, n = A._write_receipt, []

    def once(path, doc, *run):              # C2d: the final write also passes its run id (R2-T17)
        n.append(1)
        if len(n) == 1:
            raise OSError("receipt folder unwritable")
        return real(path, doc, *run)
    monkeypatch.setattr(A, "_write_receipt", once)
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) != 0
    assert receipt_of(tmp_path)["agets"][0]["result"] == "REFUSED" and snapshot(aget) == before


@pytest.mark.parametrize("agets", [["not-an-entry"], [{"aget": "x"}], [{"aget": "x", "location": "/tmp", "ops": [1]}]])
def test_b141_5_a_parsed_but_malformed_list_is_a_c1_refusal(world, tmp_path, agets):
    """B141 finding 5 (MEDIUM). Valid JSON with the right script digest but malformed members. Expected: exit 2, no
    traceback, no receipt. Stage B raised AttributeError (and KeyError) out of main."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    doc = json.loads(lst.read_text())
    doc["agets"] = agets
    lst.write_text(json.dumps(doc))
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 2
    assert not list(tmp_path.glob("APPLY_RECEIPT_*.json"))


def test_b141_6_a_parent_moved_out_after_the_walk_is_not_written(tmp_path, monkeypatch):
    """B141 finding 6 (HIGH). The writer opens member/parent; then that folder is moved outside the member and
    replaced by a link. Expected: the moved folder's file is unchanged and the act is refused. Stage B wrote through
    the already-open fd into the moved folder. The fix narrows this window (a fresh walk immediately before each
    act); it does not close it (stated limit: single writer)."""
    CI = A.CI
    root = tmp_path / "member"
    (root / "parent").mkdir(parents=True)
    (root / "parent" / "target").write_bytes(b"old")
    outside = tmp_path / "outside"
    (outside / "sink").mkdir(parents=True)
    (outside / "sink" / "target").write_bytes(b"sink")
    moved = outside / "moved"
    real, done = CI._walk, []

    def walk(r, comps, *a, **k):
        fd = real(r, comps, *a, **k)
        if Path(r) == root and comps == ["parent"] and not done:
            (root / "parent").rename(moved)
            (root / "parent").symlink_to(outside / "sink")
            done.append(1)
        return fd
    monkeypatch.setattr(CI, "_walk", walk)
    with pytest.raises(CI.ContainmentRefused):
        CI.contained_write(root, "parent/target", b"kit new", root_id=CI.root_identity(root))
    assert (moved / "target").read_bytes() == b"old" and (outside / "sink" / "target").read_bytes() == b"sink"
    assert sorted(p.name for p in moved.iterdir()) == ["target"]                 # no temp file left there either


# --- REVW2's B143 read of stage B2 (REPLY_2026-10-02_claude_codex_B143_stageB2_class_review.md) -------------------
# REVW2's falsifiers (reviewer_stageB2_probes.py), carried in. Failing-first control: the stage-B2 tree
# (gate3/CONTROL_stageB3_vs_stageB2.json).

@pytest.mark.parametrize("act", ["mkdir", "write"])
def test_b143_1_a_missing_parent_is_made_only_after_a_fresh_walk(tmp_path, monkeypatch, act):
    """B143 finding 1 (HIGH). After member/parent is opened it is moved outside and an ordinary folder put in its
    place; the next missing component must not be made in the moved folder. Stage B2 made outside/moved/nested."""
    CI = A.CI
    root = tmp_path / "member"
    p = root / "parent"
    p.mkdir(parents=True)
    moved = tmp_path / "outside" / "moved"
    moved.parent.mkdir()
    real, done = CI._open_child_dir, []

    def opened(fd, name, where):
        nfd = real(fd, name, where)
        if Path(where) == p and not done:
            p.rename(moved)
            p.mkdir()
            done.append(1)
        return nfd
    monkeypatch.setattr(CI, "_open_child_dir", opened)
    rid = CI.root_identity(root)
    with pytest.raises(CI.ContainmentRefused):
        if act == "mkdir":
            CI.contained_mkdir(root, "parent/nested", root_id=rid)
        else:
            CI.contained_write(root, "parent/nested/file", b"new", root_id=rid)
    assert not (moved / "nested").exists()


@pytest.mark.parametrize("site", ["phase_a", "final_receipt"])
def test_b143_3_an_interrupt_in_planning_or_the_final_receipt_is_c5(world, tmp_path, monkeypatch, site):
    """B143 finding 3 (HIGH). A KeyboardInterrupt during Phase A, or during the final receipt write, must end in exit
    130 with a receipt, not a traceback. Stage B2 let both escape main."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    if site == "phase_a":
        def interrupt(e):
            raise KeyboardInterrupt("planning")
        monkeypatch.setattr(A, "plan_aget", interrupt)
    else:
        real, n = A._write_receipt, []

        def write(path, doc, *run):         # C2d: the final write also passes its run id (R2-T17)
            n.append(1)
            if len(n) == 2:
                raise KeyboardInterrupt("final receipt")
            return real(path, doc, *run)
        monkeypatch.setattr(A, "_write_receipt", write)
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 130
    rec = receipt_of(tmp_path)
    assert rec.get("interrupted") is True
    assert rec["agets"][0]["result"] == ("NOT-STARTED" if site == "phase_a" else "APPLIED")


@pytest.mark.parametrize("kind", ["symbolic", "hard"])
def test_b143_receipt_temp_never_writes_through_a_link(tmp_path, kind):
    """B143, informational (outside R1's scope, evidence folders): the receipt's temp file was a predictable name
    written in place, so a link planted there changed an outside file. Now a new random temp file. Stage B2: the
    outside file changed."""
    out = tmp_path / "receipt.json"
    outside = tmp_path / "outside.txt"
    outside.write_bytes(b"safe")
    temp = out.with_name(f".{out.name}.{os.getpid()}.tmp")
    if kind == "symbolic":
        temp.symlink_to(outside)
    else:
        os.link(outside, temp)
    A._write_receipt(out, {"agets": []})
    assert outside.read_bytes() == b"safe" and not out.is_symlink()


# --- E2i: BIND (R1 clause 1, running code; R1-T7) --------------------------------------------------------------------

def test_e2i_r1_t7_an_entry_not_at_its_register_location_is_refused_and_nothing_written(world, tmp_path, monkeypatch):
    """R1-T7 (S-022/023/040/047/061/145): a list entry whose location is neither the register location of its Aget
    nor inside a rehearsal's run folder reads REFUSED, and nothing is written. Until E2i it read APPLIED."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    monkeypatch.setattr(A, "REGISTER", register(tmp_path, {"fixture-aget": tmp_path / "elsewhere"}), raising=False)
    assert A.main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    rec = json.loads(next(tmp_path.glob("APPLY_RECEIPT_*.json")).read_text())["agets"][0]
    assert rec["result"] == "REFUSED" and rec["why"].startswith("NOT A MEMBER LOCATION: ") and "elsewhere" in rec["why"]
    assert not (aget / SKILL).exists() and "3.34.0" in (aget / "AGENTS.md").read_text()


@pytest.mark.parametrize("reg", ["unlisted", "unreadable", "twice"])
def test_e2i_r1_t7_a_register_that_does_not_show_the_location_refuses(world, tmp_path, monkeypatch, reg):
    """BIND: an Aget the register does not list, a register that cannot be read, or one listing the Aget twice,
    refuses the entry (it never reads as a match). Until E2i the entry read APPLIED."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    path = {"unlisted": register(tmp_path, {"other-aget": aget}), "unreadable": tmp_path / "no-such-register.yaml",
            "twice": tmp_path / "twice.yaml"}[reg]
    if reg == "twice":
        path.write_text("fleet:\n  a:\n    agents:\n    - {agent_name: fixture-aget, location: '%s'}\n"
                        "  b:\n    agents:\n    - {agent_name: fixture-aget, location: '%s'}\n" % (aget, aget))
    monkeypatch.setattr(A, "REGISTER", path, raising=False)
    assert A.main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1
    assert not (aget / SKILL).exists()


def test_e2i_r1_t7_a_copy_inside_the_named_run_folder_is_applied(world, tmp_path, monkeypatch):
    """BIND's copy route: the rehearsal tools pass their run folder with --run, and an entry whose location lies
    inside it is applied although the register names the live member elsewhere."""
    _, aget = world
    lst, entry = make_list(tmp_path, aget)
    run = tmp_path / "run"
    copy = run / "fixture-aget"
    import shutil
    shutil.copytree(aget, copy, symlinks=True)
    doc = json.loads(lst.read_text())
    doc["agets"][0]["location"] = str(copy)
    lst.write_text(json.dumps(doc))
    assert A.main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 1          # no --run: refused
    assert not (copy / SKILL).exists()
    assert A.main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path), "--run", str(run)]) == 0
    assert (copy / SKILL).exists() and not (aget / SKILL).exists()


def test_e2i_r1_t7_a_run_folder_holding_the_live_member_does_not_make_it_a_copy(world, tmp_path, monkeypatch):
    """BIND: `--run` naming a folder that holds the Aget's register location would otherwise admit the live member
    as a copy; it is refused. (The register here names `aget`; the list names the same folder.)"""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    monkeypatch.setattr(A, "REGISTER", register(tmp_path, {"fixture-aget": aget}), raising=False)
    doc = json.loads(lst.read_text())
    doc["agets"][0]["location"] = str(aget / ".")
    lst.write_text(json.dumps(doc))
    assert A.main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path), "--run", str(tmp_path)]) == 1
    rec = json.loads(sorted(tmp_path.glob("APPLY_RECEIPT_*.json"))[-1].read_text())["agets"][0]
    assert "holds fixture-aget's location in the fleet register" in rec["why"]
    assert not (aget / SKILL).exists()


def test_e2i_r1_t7_the_trial_run_refuses_what_the_apply_refuses(world, tmp_path, monkeypatch, capsys):
    """plan_protected.py shares plan_aget(): the read-only trial run refuses an entry BIND refuses."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    monkeypatch.setattr(A, "REGISTER", register(tmp_path, {"fixture-aget": tmp_path / "elsewhere"}), raising=False)
    assert A.bind_refusal(json.loads(lst.read_text())["agets"][0]).startswith("NOT A MEMBER LOCATION: ")
    import importlib.util
    spec = importlib.util.spec_from_file_location("plan_protected", BATCH / "plan_protected.py")
    PP = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(PP)
    monkeypatch.setattr(PP.A, "REGISTER", getattr(A, "REGISTER", None), raising=False)
    assert PP.main(["--list", str(lst)]) == 1
    assert "REFUSED  NOT A MEMBER LOCATION: " in capsys.readouterr().out


def test_c2d_preread_2_an_interrupt_after_the_receipt_was_recorded_is_not_reported_as_not_written(world, tmp_path,
                                                                                                    monkeypatch, capsys):
    """FWK-OVSR8's C2d pre-read 2 (MEDIUM, reproduced): an interrupt right after the final receipt's FINISHED row made
    the retry refuse (the run had finished) and the apply print "RECEIPT NOT WRITTEN … not recorded anywhere", while the
    receipt was current and every reader accepted it. It now reports the receipt as recorded. Exit 130 stays."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    real, n = A._write_receipt, []

    def write(path, doc, *run):
        out = real(path, doc, *run)
        if run and run[0]:
            n.append(1)
            if len(n) == 1:
                raise KeyboardInterrupt("after the FINISHED row")
        return out
    monkeypatch.setattr(A, "_write_receipt", write)
    assert run_main(["--list", str(lst), "--apply", "--receipt-dir", str(tmp_path)]) == 130
    said = capsys.readouterr().out
    assert "RECEIPT NOT WRITTEN" not in said and "RECEIPT RECORDED" in said, said[-400:]
    assert receipt_of(tmp_path)["agets"][0]["result"] == "APPLIED"
