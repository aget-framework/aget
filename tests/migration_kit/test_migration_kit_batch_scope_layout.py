"""Rehearsal finding 2026-09-30: check_batch_scope.py resolved its checker from the supervisor's old folder depth
and from the supervisor's own scripts/, which no remote supervisor has. Every receiver read exit 2 and the whole
batch BLOCKED. These tests run it from the kit's layout, with the checker the kit now ships."""
import importlib.util
import json
from pathlib import Path

KIT = Path(__file__).resolve().parents[2] / "scripts" / "migration_kit"


def load(name):
    spec = importlib.util.spec_from_file_location(name, KIT / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def receiver(tmp_path, name, version_json=None):
    root = tmp_path / name
    (root / ".aget").mkdir(parents=True)
    if version_json is not None:
        (root / ".aget" / "version.json").write_text(json.dumps(version_json))
    return root


def run(tmp_path, roots):
    packet = tmp_path / "packet.json"
    packet.write_text(json.dumps({"receivers": [{"aget": n, "location": str(r), "write_set": ["AGENTS.md"]}
                                                for n, r in roots.items()]}))
    wl = tmp_path / "list.json"
    wl.write_text(json.dumps({"agets": [{"aget": n, "ops": [{"path": ".claude/skills/x/SKILL.md"}]} for n in roots]}))
    return load("check_batch_scope").main(["--packet", str(packet), "--list", str(wl)])


def test_the_checker_ships_in_the_kit_and_is_what_the_scope_check_runs():
    assert load("check_batch_scope").CHECK == KIT / "check_receiver_write_scope.py"
    assert (KIT / "check_receiver_write_scope.py").is_file() and (KIT / "write_scope_rules.py").is_file()


def test_a_receiver_with_no_declared_write_scope_passes(tmp_path):
    # changed at C2e (D-8, S-191; DESIGN's R2-T17 (c), labelled): a receiver that declares no write_scope cannot be
    # checked, so the gate blocks it (exit 2: an override names it), where it used to pass
    assert run(tmp_path, {"a": receiver(tmp_path, "a", {"aget_version": "3.35.0"})}) == 2


def test_a_strict_write_scope_that_excludes_the_payload_needs_an_override(tmp_path):
    strict = {"aget_version": "3.35.0", "write_scope": {"enforcement": "strict", "allowed_paths": [".aget/evolution/"],
                                                        "forbidden_paths": ["*"]}}
    assert run(tmp_path, {"b": receiver(tmp_path, "b", strict)}) == 1


def test_wave_readiness_runs_the_kit_checker_not_a_supervisor_script():
    src = (KIT / "wave_readiness.py").read_text()
    assert "'scripts/check_receiver_write_scope.py'" not in src and "check_receiver_write_scope.py'" in src


# --- C2e: the D-8 appendix (DESIGN's R2-T17 `test_scope_check_covers_session_write_set`, S-190/S-191/S-248/S-250) ----

STRICT = {"aget_version": "3.35.0", "write_scope": {"enforcement": "strict",
                                                    "allowed_paths": [".aget/", "manifest.yaml", ".claude/", "AGENTS.md",
                                                                      "docs/"],
                                                    "forbidden_paths": ["*"]}}


def _scope(tmp_path, write_set, items=(), name="s"):
    root = receiver(tmp_path, name, STRICT)
    packet = tmp_path / f"{name}_packet.json"
    packet.write_text(json.dumps({"receivers": [{"aget": name, "location": str(root), "write_set": list(write_set),
                                                 "items": list(items)}]}))
    wl = tmp_path / f"{name}_list.json"
    wl.write_text(json.dumps({"agets": [{"aget": name, "ops": [{"path": ".claude/skills/x/SKILL.md"}]}]}))
    out = tmp_path / f"{name}_rows.json"
    code = load("check_batch_scope").main(["--packet", str(packet), "--list", str(wl), "--out", str(out)])
    return code, json.loads(out.read_text())["rows"][0]


def test_c2e_d8_the_scope_check_covers_the_session_write_set(tmp_path):
    """D-8 (S-190, S-191, S-248, S-250): (i) a write_scope allow-list without `sessions`, the session's write set
    holding `sessions/*`: the glob was dropped and the check read exit 0; now its literal prefix `sessions` is checked
    (exit 1, naming it); (ii) a delete item outside the allow-list was not checked: exit 1; (iv) a write-set entry `**`
    has no literal prefix: exit 2. ((iii), no write_scope, is the changed test above.) Control: the same receiver
    with only paths inside its allow-list: exit 0."""
    assert _scope(tmp_path, ["docs/RECEIPT.md"], name="ok")[0] == 0
    code, row = _scope(tmp_path, ["docs/RECEIPT.md", "sessions/*"], name="i")
    assert code == 1 and "sessions" in row["out"], row
    code, row = _scope(tmp_path, ["docs/RECEIPT.md"], [{"path": "scripts/old.py", "op": "delete"}], name="ii")
    assert code == 1 and "scripts/old.py" in row["out"], row
    code, row = _scope(tmp_path, ["**"], name="iv")
    assert code == 2 and "**" in row["out"], row


def test_d2_preread_7_8_option_named_paths_and_traversal_are_not_passed_by_the_scope_check(tmp_path):
    """FWK-OVSR8's C2a15+C2e pre-read 8 and 9 (reproduced): a delete named `--json` was consumed as an option by the
    checker (not checked); `docs/../scripts/*` passed a `docs/` allowance by its literal prefix. Paths now follow
    `--`, and a path that is not plain relative is unverifiable (exit 2). Control: the plain receiver exits 0."""
    assert _scope(tmp_path, ["docs/RECEIPT.md"], name="ok2")[0] == 0
    code, row = _scope(tmp_path, ["docs/RECEIPT.md"], [{"path": "--json", "op": "delete"}], name="opt")
    assert code == 1 and "--json" in row["out"], row
    code, row = _scope(tmp_path, ["docs/../scripts/*"], name="trav")
    assert code == 2 and "docs/../scripts" in row["out"], row
