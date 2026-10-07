"""R-F7 (rehearsal 2026-09-30): the framework root is read from the release-target file, not only the environment.

The kit took the folder holding the framework clones only from AGET_FRAMEWORK_ROOT. Shell state does not persist
between a session's commands, so every kit command needed an `export ...;` prefix, and the prefix stopped the
session's command rules from matching: the classifier refused a push the rules allowed (batch 9). The root now
resolves like the release target: environment, else `framework_root` in .aget/migration_target.json, else the
default, through one function in release_target.py that every tool calls.
"""
import io
import json
import os
import shutil
import subprocess
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "scripts" / "migration_kit"


def _kit_copy(tmp_path, config=None):
    """A copy of the kit under <tmp>/scripts/migration_kit, so release_target resolves <tmp> as its root."""
    dst = tmp_path / "scripts" / "migration_kit"
    shutil.copytree(KIT, dst, ignore=shutil.ignore_patterns("__pycache__"))
    if config is not None:
        (tmp_path / ".aget").mkdir()
        (tmp_path / ".aget" / "migration_target.json").write_text(json.dumps(config))
    return dst


def _run(cwd, code, **env):
    e = {k: v for k, v in os.environ.items() if k != "AGET_FRAMEWORK_ROOT"}
    e.update(env)
    return subprocess.run([sys.executable, "-c", code], cwd=cwd, env=e, capture_output=True, text=True, timeout=60)


def test_root_comes_from_the_target_file_without_any_environment(tmp_path):
    """FALSIFIER: with the variable unset, every tool must read the root from the file.

    Satisfies: R-TEST-001-02
    """
    kit = _kit_copy(tmp_path, {"framework_root": "/srv/fw"})
    r = _run(kit, "import release_target as R, apply_protected as A, verify_extension_survival as V;"
                  "print(R.framework_root(), A.framework_root(), V.framework_root(), V.core_repo())")
    assert r.returncode == 0, r.stderr
    assert r.stdout.split() == ["/srv/fw", "/srv/fw", "/srv/fw", "/srv/fw/aget"]


def test_environment_still_wins_over_the_file(tmp_path):
    kit = _kit_copy(tmp_path, {"framework_root": "/srv/fw"})
    r = _run(kit, "import release_target as R; print(R.framework_root())", AGET_FRAMEWORK_ROOT="/opt/other")
    assert r.stdout.strip() == "/opt/other"


def test_a_relative_value_resolves_against_the_repository_root(tmp_path):
    kit = _kit_copy(tmp_path, {"framework_root": "../aget-framework"})
    r = _run(kit, "import release_target as R; print(R.framework_root())")
    assert r.stdout.strip() == str((tmp_path / "../aget-framework").resolve())


def test_with_neither_set_the_default_is_unchanged(tmp_path):
    kit = _kit_copy(tmp_path)
    r = _run(kit, "import release_target as R; print(R.framework_root())")
    assert r.stdout.strip() == os.path.expanduser("~/github/aget-framework")


def _code_strings(path):
    for t in tokenize.generate_tokens(io.StringIO(path.read_text()).readline):
        if t.type == tokenize.STRING:
            yield t.start[0], t.string


def test_readiness_runs_the_kits_own_survival_check():
    """FALSIFIER (found with R-F7, 2026-10-01): wave_readiness ran `scripts/verify_extension_survival.py` from the
    repository root. A remote supervisor has only the kit's copy under scripts/migration_kit/, so every capture exited
    2; a local one silently ran an older copy that still read the root from the environment alone."""
    src = (KIT / "wave_readiness.py").read_text()
    assert "'scripts/verify_extension_survival.py'" not in src
    assert "SURVIVAL = str(Path(__file__).resolve().with_name('verify_extension_survival.py'))" in src
    assert src.count("SURVIVAL,") == 2


def test_no_tool_but_release_target_reads_the_root_itself():
    """FALSIFIER: a second reader of the variable, or a hardcoded clone path, re-opens R-F7 for that tool."""
    found = []
    for f in sorted(KIT.glob("*.py")):
        if f.name == "release_target.py":
            continue
        for line, s in _code_strings(f):
            if "AGET_FRAMEWORK_ROOT" in s or "~/github/aget-framework" in s:
                found.append(f"{f.name}:{line}: {s[:60]}")
    assert not found, "framework root read outside release_target.py:\n" + "\n".join(found)


def test_the_readiness_run_names_the_instruments_it_needs_and_stops_before_writing(tmp_path):
    """FALSIFIER (review, 2026-10-01): wave_readiness.py's own run calls four scripts that exist only in the
    supervisor repository it was written in. A supervisor without them must be told which, at the start, with nothing
    written; before this it stopped mid-run on the first one with a report already on disk."""
    kit = _kit_copy(tmp_path, {"from": "3.34.0", "to": "3.35.0", "register_pin": "0" * 40, "pinned_members": 1})
    r = subprocess.run([sys.executable, str(kit / "wave_readiness.py")], cwd=tmp_path, capture_output=True, text=True,
                       env={k: v for k, v in os.environ.items() if not k.startswith("AGET_")}, timeout=60)
    assert r.returncode == 2, r.stdout + r.stderr
    for name in ("check_register_version_drift.py", "check_receiver_version_rulings.py",
                 "check_dispatch_liveness.py", "preflight_seat_is_free.py"):
        assert name in r.stdout, r.stdout
    assert "not shipped with the kit" in r.stdout
    assert not (tmp_path / "data").exists()


def test_the_declared_instruments_are_exactly_the_ones_the_run_calls():
    """The declaration must not drift from the code: every `scripts/<name>.py` the run executes is declared."""
    import re
    src = (KIT / "wave_readiness.py").read_text()
    called = set(re.findall(r"\[sys\.executable, 'scripts/([a-z_]+\.py)'", src))
    declared = set(re.findall(r"'([a-z_]+\.py)'", src.split("LOCAL_INSTRUMENTS = (", 1)[1].split(")", 1)[0]))
    assert called and called == declared, (called, declared)


# --- A supervisor built from the template alone (investigation of 2026-10-01) ------------------------------------

def test_every_library_the_kit_imports_beyond_python_itself_is_declared():
    """FALSIFIER: the kit imported a YAML library that neither it nor the supervisor template declared. In a clean
    Python environment even `fleet_ledger.py --help` stopped with ModuleNotFoundError."""
    import ast
    stdlib = set(sys.stdlib_module_names)
    own = {f.stem for f in KIT.glob("*.py")}
    used = set()
    for f in KIT.glob("*.py"):
        for node in ast.walk(ast.parse(f.read_text())):
            names = [a.name for a in node.names] if isinstance(node, ast.Import) else \
                    [node.module] if isinstance(node, ast.ImportFrom) and node.module and node.level == 0 else []
            used |= {n.split(".")[0] for n in names}
    third_party = used - stdlib - own
    declared = {ln.split(">")[0].split("=")[0].strip().lower()
                for ln in (KIT / "requirements.txt").read_text().splitlines() if ln.strip() and not ln.startswith("#")}
    names = {"yaml": "pyyaml"}                      # import name -> distribution name
    assert third_party and {names.get(m, m).lower() for m in third_party} <= declared, (third_party, declared)


def test_the_survival_check_finds_the_fleet_register_at_the_repository_root(tmp_path):
    """FALSIFIER: verify_extension_survival.py looked for the register under scripts/.aget/fleet/, because its root
    was computed for a file one folder higher than where the kit puts it."""
    kit = _kit_copy(tmp_path, {"from": "3.34.0", "to": "3.35.0"})
    (tmp_path / ".aget" / "fleet").mkdir(parents=True, exist_ok=True)
    (tmp_path / ".aget" / "fleet" / "FLEET_STATE.yaml").write_text(
        "fleet:\n  main:\n    agents:\n      - agent_name: some-aget\n        location: /srv/some-aget\n")
    r = _run(kit, "import verify_extension_survival as V; print(V.seat_location('some-aget'))")
    assert r.returncode == 0 and r.stdout.strip() == "/srv/some-aget", r.stdout + r.stderr
