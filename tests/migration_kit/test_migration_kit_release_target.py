"""Carriage row 24: the kit names its release in one place and hardcodes it nowhere. Both directions."""
import importlib.util
import io
import os
import re
import subprocess
import sys
import tokenize
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "scripts" / "migration_kit"
REL = re.compile(r"3\.3[0-9]\.\d|v33[0-9]\b|v3_3[0-9]")

# Record-format names and importlib module labels: they name data formats and loader handles, not the target
# release. Renaming a format breaks reading records already written; kept, and listed exactly (no prefix wildcard).
ALLOWED = {'"v335_protected_apply_receipt/1"', '"v335_wave_readiness"', '"v335_fleet_ledger/1"', '"v335_fleet_ledger"',
           '"v335_protected_list/1"', '"v335_launch_packet/2"', '"v335_v37_result/2"', '"v335_suite_at_commit/1"'}
# open_receiver.py re-shaped 2026-09-29: receivers are data, so nothing is pending.
PENDING: set = set()


# Python 3.12+ tokenizes an f-string as FSTRING_START / FSTRING_MIDDLE / FSTRING_END, not STRING, so a guard that
# reads STRING tokens alone could not see a literal inside any f-string (every receiver prompt is one). Found
# 2026-09-30 when a prompt read "migrate you from v3.34.0 to v3.35.0" with this test green.
_FSTRING_PARTS = {getattr(tokenize, n) for n in ("FSTRING_MIDDLE",) if hasattr(tokenize, n)}
_FSTRING_START = getattr(tokenize, "FSTRING_START", None)


def _code_string_literals(path):
    toks = list(tokenize.generate_tokens(io.StringIO(path.read_text()).readline))
    prev = None
    in_code_fstring = False
    for t in toks:
        if t.type == tokenize.STRING and prev not in (None, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT):
            yield t.start[0], t.string
        if t.type == _FSTRING_START:
            in_code_fstring = prev not in (None, tokenize.NEWLINE, tokenize.INDENT, tokenize.DEDENT)
        if t.type in _FSTRING_PARTS and in_code_fstring:
            yield t.start[0], t.string
        if t.type not in (tokenize.NL, tokenize.COMMENT) and t.type not in _FSTRING_PARTS:
            prev = t.type


def test_the_guard_sees_inside_f_strings(tmp_path):
    f = tmp_path / "t.py"
    f.write_text('x = 1\nprompt = f"migrate {x} from v3.34.0 to v3.35.0"\n')
    assert any(REL.search(s) for _, s in _code_string_literals(f))


def test_no_tool_hardcodes_a_release_in_code():
    """FALSIFIER: the v3.35 kit carried 78 release literals across 8 tools; a new one must fail here.

    Satisfies: R-TEST-001-02
    """
    found = []
    for f in sorted(KIT.glob("*.py")):
        if f.name in PENDING or f.name == "release_target.py":
            continue
        for line, s in _code_string_literals(f):
            if REL.search(s) and s not in ALLOWED:
                found.append(f"{f.name}:{line}: {s[:60]}")
    assert not found, "hardcoded release literals:\n" + "\n".join(found)


def _run(code, **env):
    e = {k: v for k, v in os.environ.items() if not k.startswith("AGET_MIGRATION_")}
    e.update(env)
    return subprocess.run([sys.executable, "-c", code], cwd=KIT, env=e, capture_output=True, text=True, timeout=60)


def test_an_unset_target_stops_with_a_message_and_import_does_not_exit():
    """No default release; and no process exit at import (carriage row 29).

    Satisfies: R-TEST-001-02
    """
    r = _run("import release_target as R; print('imported', R.TO); R.require()")
    assert "imported UNSET" in r.stdout
    assert r.returncode != 0 and "no default release" in r.stderr


def test_changing_the_target_changes_what_the_tools_use():
    """The same tool, pointed at a different release, names that release's files.

    Satisfies: R-TEST-001-02
    """
    code = ("import importlib.util as u; s=u.spec_from_file_location('pl','prepare_launch.py'); m=u.module_from_spec(s); "
            "s.loader.exec_module(m); print(m.CORE_DOCS[0]); print(m.packet_base('/run/B/LAUNCH_PACKET.json'))")
    r = _run(code, AGET_MIGRATION_FROM="3.35.0", AGET_MIGRATION_TO="3.36.0")
    assert r.returncode == 0, r.stderr
    assert "RELEASE_HANDOFF_v3.36.0.md" in r.stdout and "/v336/packets" in r.stdout     # R1: per-packet roots
    assert "3.35.0.md" not in r.stdout


def test_every_tool_resolves_the_same_repo_root():
    """FALSIFIER (found while porting, 2026-09-29): one tool resolved one level too shallow and no test noticed.

    Satisfies: R-TEST-001-02
    """
    roots = {}
    for name in ("fleet_ledger.py", "prepare_launch.py", "wave_readiness.py", "release_target.py"):
        spec = importlib.util.spec_from_file_location(f"rt_{name[:-3]}", KIT / name)
        mod = importlib.util.module_from_spec(spec)
        sys.path.insert(0, str(KIT))
        spec.loader.exec_module(mod)
        roots[name] = Path(getattr(mod, "REPO", getattr(mod, "ROOT", None))).resolve()
    assert set(roots.values()) == {ROOT.resolve()}, roots
