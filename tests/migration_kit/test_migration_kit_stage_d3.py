"""Stage D3 (REVW10's B200 read of D2): the failing-first rows for B200 findings 1-4 and the owed track-skills row.
Each test names its finding; the falsifiers are REVW10's (`revw10_d2_class_probes.py`, `revw10_d2_startup_probe.py`),
rewritten in this suite's helpers."""
import argparse
import importlib.util
import json
import subprocess
import sys
from pathlib import Path

import pytest

BATCH = Path(__file__).resolve().parents[2] / "scripts" / "migration_kit"
sys.path.insert(0, str(BATCH))


def load(name):
    spec = importlib.util.spec_from_file_location(name, BATCH / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RBND = load("result_binding")


# --- B200 finding 2: the prescan reads a value the way argparse does ---------------------------------------------

def _argparse_value(argv, flag):
    """What a parser with this flag (and two other options, as the producers have) takes as its value."""
    ap = argparse.ArgumentParser(add_help=False, exit_on_error=False)
    ap.add_argument(flag)
    ap.add_argument("--packet")
    ap.add_argument("--aget")
    ns, _ = ap.parse_known_args(argv)
    return getattr(ns, flag.lstrip("-").replace("-", "_"))


@pytest.mark.parametrize("value", ["-1", "-12", "-1.5", "-.5", "-", "plain", "with space -x", "-x y"])
def test_b200_2_prescan_takes_what_argparse_takes(value):
    """B200 finding 2 (REVW10's falsifier: `--evidence OTHER --evidence -1`): a value that looks like a negative
    number, or holds a space, is a value to argparse; D2's prescan read every leading `-` as an option, kept OTHER and
    left the effective slot's earlier PASS current."""
    argv = ["--packet", "p", "--evidence", "OTHER", "--evidence", value]
    assert RBND.prescan(argv, "--evidence") == _argparse_value(argv, "--evidence") == value


@pytest.mark.parametrize("nxt", ["--packet", "-x"])
def test_b200_2_a_following_option_is_still_not_the_value(nxt):
    """The D2 repair this must keep (FWK-OVSR9's D2 pre-read 2): a following option is never the value."""
    assert RBND.prescan(["--evidence", "A", "--evidence", nxt, "p"], "--evidence") == "A"


def test_b200_2_a_failed_attempt_at_a_negative_number_named_folder_invalidates_its_slot(tmp_path, monkeypatch):
    """B200 finding 2 end to end (REVW10's `revw10_d2_startup_probe.py`): an earlier PASS at evidence folder `-1`,
    then a later attempt whose last `--evidence` is `-1` fails in its run body. The slot argparse writes is the slot
    invalidated first, so the earlier PASS no longer reads current."""
    SAC = load("suite_at_commit")
    root = tmp_path / "member"
    root.mkdir()
    (root / "f").write_text("x\n")
    for a in (["init", "-q"], ["add", "f"], ["-c", "user.name=t", "-c", "user.email=t@t", "commit", "-qm", "c"]):
        subprocess.run(["git", "-C", str(root), *a], check=True, capture_output=True)
    head = subprocess.run(["git", "-C", str(root), "rev-parse", "HEAD"], capture_output=True, text=True).stdout.strip()
    packet = tmp_path / "packet.json"
    packet.write_text(json.dumps({"receivers": [{"aget": "seat", "location": str(root), "head": head,
                                                 "suite_cmd": "true"}]}))
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr(SAC, "run", lambda *a, **k: {"aget": "seat", "sha": head, "verdict": "PASS",
                                                     "tree_check": "enforced", "hook": {"present": False},
                                                     "tree_allowed": [], "summary": "1 passed"})
    assert SAC.main(["--packet", str(packet), "--aget", "seat", "--evidence", str(tmp_path / "-1")]) == 0
    slot = tmp_path / "-1" / "seat" / "suite_at_commit.json"
    prior, why = RBND.read_current("suite_at_commit", slot)
    assert prior and prior["verdict"] == "PASS" and why is None

    def fail(*a, **k):
        raise RuntimeError("later attempt failed")
    monkeypatch.setattr(SAC, "run", fail)
    with pytest.raises(RuntimeError):
        SAC.main(["--packet", str(packet), "--aget", "seat", "--evidence", str(tmp_path / "other"), "--evidence", "-1"])
    current, why = RBND.read_current("suite_at_commit", slot)
    assert current is None and why


# --- B200 findings 3 and 4: a held protected file keeps its whole meaning row ------------------------------------

TESTS = Path(__file__).resolve().parent


def load_test(name):
    """A sibling test module, for its fixture helpers (REVW10's probes use the same ones)."""
    spec = importlib.util.spec_from_file_location(f"_d3_{name}", TESTS / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_b200_3_an_unchanged_unattributed_held_file_is_compared_not_unknown(tmp_path, monkeypatch):
    """B200 finding 3 (REVW10's falsifier): A rebuilt a held entry from path/op/kind only, so a table-valid
    `hold/unattributed` (`authored_lines` 0) read "unattributed with authored_lines None", INCONCLUSIVE, and its
    identity was never compared. The no-source control is compared; the unattributed one must be too, and a changed
    file of either kind is an A finding."""
    M = load_test("test_migration_kit_after_run_check")
    go, root, tmp = M.run.__wrapped__(tmp_path, monkeypatch)
    held = "scripts/held.py"
    f = root / held
    f.write_text("retained member bytes\n")
    h = {"path": held, "op": "hold", "kind": "no-source", "pre": M.sha(f.read_text())}

    def take(h):
        M.produce(tmp / "receipt.json", "apply_protected",
                  {"mode": "apply", "agets": [{"aget": "a", "result": "APPLIED", "location": str(root), "held": [h],
                                               "files": [{"path": M.SKILL, "post": M.sha("release\n"), "ok": True}]}]})
        return go()
    code, out = take(h)
    assert code == 0 and not any(held in x for x in out["inconclusive"]), out
    h.update(kind="unattributed", authored_lines=0)
    code, out = take(h)
    assert not any(held in x for x in out["inconclusive"]), out
    f.write_text("changed by the session\n")
    code, out = take(h)
    assert any(x.startswith(f"{held}: held as it was") for x in out["A"]), out


def test_b200_4_a_protected_hold_s_keep_line_names_its_release_digest():
    """B200 finding 4 (REVW10's falsifier): `_held()` and the packet's protected holds kept path/op/kind/pre only, so
    an unattributed protected hold was told "release sha256 None". The list's `source_sha256` reaches the line, and a
    row with no release digest at all is refused, never rendered with None."""
    AP = load("apply_protected")
    M = load_test("test_migration_kit_instruction_fidelity")
    IM = load("item_meaning")
    digest = "a" * 64
    op = {"path": ".claude/skills/held/SKILL.md", "op": "hold", "kind": "unattributed", "authored_lines": 0,
          "pre": "b" * 64, "source": "template-x-aget@v:held", "source_sha256": digest}
    held = AP._held({"ops": [op]})
    prompt = M.PL.prompt({**M.R, "items": [], "protected_holds": held}, "att-1", [])
    line = next(ln for ln in prompt.splitlines() if "KEEP .claude/skills/held/SKILL.md" in ln)
    assert digest in line and "None" not in line, line
    bare = {k: v for k, v in op.items() if k != "source_sha256"}
    with pytest.raises(IM.UnknownClassification):
        IM.meaning(bare).instruction(bare)


def test_b200_4_the_packet_carries_each_protected_hold_s_whole_list_entry():
    """B200 finding 4, the packet half (`prepare_launch.py`'s protected holds): a hold's digest and authored count
    are carried from the list, so the prompt and A read the same row the apply held."""
    src = (Path(__file__).resolve().parents[2] / "scripts/migration_kit/prepare_launch.py").read_text()
    assert '"kind": o.get("kind"), "pre": o.get("pre"),' not in src


# --- owed since D2: the track-skills `git add` refusal row ----------------------------------------------------------

def test_d3_owed_a_failed_track_skills_git_add_refuses_before_a_copy_commit_or_s2(tmp_path, monkeypatch):
    """Owed since D2 (DESIGN's R3 remainder; REVW10 verified the refusal with its own test in B200): when `git add` of
    a track-skills receiver's paths fails in the rehearsal copy (an index lock), the member reads REFUSED naming the
    add, no copy commit and no S2 is made, and the member's own bytes are unchanged. Failing-first control: C2e
    (before D2 built the refusal); D2 already passes."""
    M = load_test("test_migration_kit_rehearse_refusal")
    good = tmp_path / "home" / "good"
    M.git_repo(good, M.MEMBER_FILES)
    before = {str(p.relative_to(good)): p.read_bytes() for p in good.rglob("*") if p.is_file()}
    RB, pk, lst = M.b2_world(tmp_path, monkeypatch, {"good": good})
    d = json.loads(pk.read_text())
    d["receivers"][0].update(mode="track-skills", track_paths=["AGENTS.md"])
    pk.write_text(json.dumps(d))
    real = RB.apply_on_copy

    def apply_then_lock(entry, copy, ev):
        result = real(entry, copy, ev)
        (copy / ".git" / "index.lock").write_text("held")
        return result
    monkeypatch.setattr(RB, "apply_on_copy", apply_then_lock)
    code, got = M.b2_run(RB, pk, lst, tmp_path)
    after = {str(p.relative_to(good)): p.read_bytes() for p in good.rglob("*") if p.is_file()}
    assert code == 1 and got["good"]["verdict"].startswith("REFUSED: copy commit failed: git add AGENTS.md"), got
    assert "S2" not in got["good"] and before == after


# --- FWK-OVSR9's D2 member-identity advisory: identity must not depend on reference counts ----------------------

def test_d3_identity_is_unchanged_when_a_cache_holds_one_of_the_test_s_literals():
    """FWK-OVSR9's advisory (`overseer_prereads/D2_member_identity/`, reproduced on two fleet members): marshal from
    format 3 marks a string constant held elsewhere, so once `fnmatch`'s cache held a test's own literal the same code
    object hashed differently at run time than at census time, a false "not the one the census collected" on ordinary
    passing tests. Control: the identity is stable with no cache warmed."""
    import fnmatch
    from types import SimpleNamespace
    sys.path.insert(0, str(BATCH / "pytest_plugin"))
    census = load_plugin("aget_kit_census")
    ns = {}
    exec(compile("import fnmatch\ndef test_x():\n    assert fnmatch.fnmatch('a/b.json', 'a/*.json-literal-x')\n",
                 str(BATCH / "t_mod.py"), "exec"), ns)
    item = SimpleNamespace(obj=ns["test_x"])
    fnmatch._compile_pattern.cache_clear()
    a = census.item_identity(item, str(BATCH))
    assert a == census.item_identity(item, str(BATCH))                 # control: stable, nothing warmed
    lit = next(c for c in ns["test_x"].__code__.co_consts if c == "a/*.json-literal-x")
    fnmatch.fnmatch("a/b.json", lit)                                       # the cache now holds the code's own literal
    try:
        assert census.item_identity(item, str(BATCH)) == a
    finally:
        fnmatch._compile_pattern.cache_clear()


def load_plugin(name):
    spec = importlib.util.spec_from_file_location(name, BATCH / "pytest_plugin" / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod
