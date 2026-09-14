"""C-34-18 — three levels of runtime support evidence, never collapsed.

The negatives carry the requirement. R9 Part 3 collapsed "installed" into "supported target"
and read a desktop launcher's version as evidence about a terminal agent. Each test below
fails if either collapse returns.
"""
from __future__ import annotations

import importlib.util
import json
import os
import stat
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "crse", REPO / "scripts" / "check_runtime_support_evidence.py")
crse = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(crse)

YES, NO, UNKNOWN = "YES", "NO", "UNKNOWN"


def fake_exe(directory: Path, name: str, *, version="1.2.3", help_text=""):
    p = directory / name
    p.write_text(
        "#!/bin/sh\n"
        f'if [ "$1" = "--version" ]; then echo "{version}"; exit 0; fi\n'
        f'if [ "$1" = "--help" ]; then printf "%s" "{help_text}"; exit 0; fi\n'
        "exit 0\n"
    )
    p.chmod(p.stat().st_mode | stat.S_IEXEC | stat.S_IRWXU)
    return p


@pytest.fixture
def onpath(tmp_path, monkeypatch):
    d = tmp_path / "bin"
    d.mkdir()
    monkeypatch.setenv("PATH", str(d))
    return d


# --- L1 -------------------------------------------------------------------------

def test_absent_executable_is_NO_at_L1(onpath):
    assert crse.level1_installed("nope")["verdict"] == NO


def test_present_executable_reporting_a_version_is_YES_at_L1(onpath):
    fake_exe(onpath, "gemini", version="0.59.0")
    r = crse.level1_installed("gemini")
    assert r["verdict"] == YES and r["version"] == "0.59.0"


def test_a_symlink_into_an_app_bundle_is_flagged_as_a_desktop_launcher(tmp_path, monkeypatch):
    """The exact conflation in R9 Part 3: a launcher's version read as the agent's."""
    app = tmp_path / "Antigravity.app" / "Contents" / "Resources" / "app" / "bin"
    app.mkdir(parents=True)
    real = fake_exe(app, "antigravity", version="1.107.0")
    d = tmp_path / "bin"
    d.mkdir()
    (d / "antigravity").symlink_to(real)
    monkeypatch.setenv("PATH", str(d))
    r = crse.level1_installed("antigravity")
    assert r["is_desktop_launcher"] is True
    assert "DESKTOP LAUNCHER" in r["why"]


# --- L2 -------------------------------------------------------------------------

def test_no_instruction_surface_in_help_is_not_YES_at_L2(onpath):
    """Renamed: after F2 a help text can no longer yield NO -- our failure to parse is not the
    tool's incapacity. What is pinned is that nothing was found."""
    fake_exe(onpath, "gemini", help_text="Usage: gemini [options]")
    r = crse.level2_instructable("gemini")
    assert r["verdict"] != YES and r["surface_tokens_found"] == []


def test_an_instruction_surface_in_help_is_YES_at_L2(onpath):
    """YES needs BOTH a declared surface and an explicit non-interactive statement (F1)."""
    fake_exe(onpath, "gemini", help_text="Usage: gemini --prompt TEXT (non-interactive)")
    assert crse.level2_instructable("gemini")["verdict"] == YES


def test_an_undeclared_runtime_family_is_UNKNOWN_at_L2_not_NO(onpath):
    """We were not told what surface to look for. That is ignorance, not absence."""
    fake_exe(onpath, "someothercli", help_text="Usage: whatever")
    r = crse.level2_instructable("someothercli")
    assert r["verdict"] == UNKNOWN and "no instruction surface declared" in r["why"]


# --- L3: read from a receipt, never produced ------------------------------------

def test_L3_without_a_receipt_directory_is_UNKNOWN_never_NO(onpath):
    r = crse.level3_governed("gemini", None)
    assert r["verdict"] == UNKNOWN
    assert "never inferred" in r["why"]


def test_L3_with_a_matching_receipt_is_YES(tmp_path):
    rec = tmp_path / "receipts"
    rec.mkdir()
    (rec / "r1.json").write_text(
        '{"runtime": "gemini", "invoked": true, "outcome": "ok"}')
    assert crse.level3_governed("gemini", rec)["verdict"] == YES


def test_L3_with_receipts_that_do_not_name_the_runtime_is_UNKNOWN(tmp_path):
    rec = tmp_path / "receipts"
    rec.mkdir()
    (rec / "r1.json").write_text('{"runtime": "codex", "invoked": true, "outcome": "ok"}')
    r = crse.level3_governed("gemini", rec)
    assert r["verdict"] == UNKNOWN
    assert "not a demonstrated NO" in r["why"]


# --- the collapses this row exists to prevent -----------------------------------

def test_installed_alone_does_not_yield_a_supported_target(onpath):
    """R9: 'The binary is present and executes here. It does not establish that the tool
    remains a supported target.'"""
    fake_exe(onpath, "gemini", version="0.59.0", help_text="Usage: gemini --prompt TEXT")
    r = crse.assess("gemini", None)
    assert r["L1_installed"]["verdict"] == YES
    assert r["overall"] != "SUPPORTED-TARGET"
    assert r["overall"] == "PARTIAL-EVIDENCE"


def test_unknown_never_exits_zero(onpath):
    fake_exe(onpath, "gemini", version="0.59.0", help_text="Usage: gemini --prompt TEXT")
    assert crse.exit_code([crse.assess("gemini", None)]) == 2


def test_a_definite_no_exits_one(onpath):
    assert crse.exit_code([crse.assess("absent-runtime", None)]) == 1


def test_all_three_levels_yes_exits_zero(tmp_path, monkeypatch):
    d = tmp_path / "bin"
    d.mkdir()
    fake_exe(d, "gemini", version="0.59.0", help_text="Usage: gemini --prompt TEXT (non-interactive)")
    monkeypatch.setenv("PATH", str(d))
    rec = tmp_path / "receipts"
    rec.mkdir()
    (rec / "r.json").write_text('{"runtime": "gemini", "invoked": true, "outcome": "ok"}')
    r = crse.assess("gemini", rec)
    assert r["overall"] == "SUPPORTED-TARGET"
    assert crse.exit_code([r]) == 0


# --- control boundary (CAP-CCP) --------------------------------------------------

def test_the_checker_never_invokes_the_runtime_for_L3(tmp_path):
    """Producing L3 by running the runtime is the state-changing act the boundary forbids."""
    src = (REPO / "scripts" / "check_runtime_support_evidence.py").read_text()
    body = src.split("def level3_governed", 1)[1].split("\ndef ", 1)[0]
    assert "_run(" not in body, "L3 must be read from a receipt, never produced by invocation"


def test_probes_are_limited_to_version_and_help(tmp_path):
    src = (REPO / "scripts" / "check_runtime_support_evidence.py").read_text()
    assert '"--version"' in src and '"--help"' in src
    for forbidden in ("install", "login", "auth", "--yes", "config set"):
        assert f'_run([name, "{forbidden}"' not in src


# ===================================================================================
# Regressions from the independent review of 2026-09-09. The reviewer drove a desktop
# launcher to SUPPORTED-TARGET with exit 0 through the very tool built to prevent it.
# ===================================================================================

def launcher_on_path(tmp_path, monkeypatch, *, help_text):
    app = tmp_path / "Antigravity.app" / "Contents" / "Resources" / "app" / "bin"
    app.mkdir(parents=True)
    real = fake_exe(app, "antigravity", version="1.107.0", help_text=help_text)
    d = tmp_path / "bin"
    d.mkdir()
    (d / "antigravity").symlink_to(real)
    monkeypatch.setenv("PATH", str(d))
    return d


def test_B2_a_desktop_launcher_never_reaches_supported_target(tmp_path, monkeypatch):
    """The reviewer's exact reproduction: launcher + help naming an 'agent' + a receipt."""
    launcher_on_path(tmp_path, monkeypatch,
                     help_text="Antigravity desktop agent launcher. Usage: antigravity [file]")
    rec = tmp_path / "receipts"
    rec.mkdir()
    (rec / "r.json").write_text(
        '{"runtime": "antigravity", "invoked": true, "outcome": "ok"}')
    r = crse.assess("antigravity", rec)
    assert r["L1_installed"]["verdict"] == UNKNOWN, "a launcher is not a terminal agent"
    assert r["overall"] != "SUPPORTED-TARGET"
    assert crse.exit_code([r]) != 0


def test_B2_the_launcher_flag_actually_drives_the_verdict(tmp_path, monkeypatch):
    """It was computed, printed, and never consulted."""
    launcher_on_path(tmp_path, monkeypatch, help_text="Usage: antigravity exec CMD")
    r = crse.level1_installed("antigravity")
    assert r["is_desktop_launcher"] is True
    assert r["verdict"] != YES, "the flag must demote the verdict, not merely annotate it"


def test_M5_a_flag_substring_does_not_count_as_an_instruction_surface(onpath):
    """`-p` matched inside `--output-path`.

    The verdict is UNKNOWN rather than NO because the help DOES declare an option we did not
    seek -- an unmatched token list is an unproven expectation, not a demonstrated absence
    (BLOCKING-A). What this test pins is the original point: `-p` is not found.
    """
    fake_exe(onpath, "gemini",
             help_text="Usage: gemini --output-path FILE (interactive only)")
    r = crse.level2_instructable("gemini")
    assert r["surface_tokens_found"] == [], "-p must not match inside --output-path"
    assert r["verdict"] != YES
    assert "--output-path" in r["declared_surfaces"]["options"]


def test_M5_a_word_in_prose_does_not_count_as_an_instruction_surface(onpath):
    fake_exe(onpath, "antigravity", help_text="A desktop agent launcher for your files.")
    r = crse.level2_instructable("antigravity")
    assert r["verdict"] != YES and r["declared_surfaces"]["subcommands"] == []


def test_M5_a_real_flag_still_matches(onpath):
    fake_exe(onpath, "gemini",
             help_text="Usage: gemini -p PROMPT (non-interactive)\n  --output-path FILE")
    assert crse.level2_instructable("gemini")["verdict"] == YES


def test_M4_a_receipt_that_records_no_invocation_is_not_L3(tmp_path):
    """The reviewer's reproduction: a receipt saying the runtime was NOT invoked scored YES."""
    rec = tmp_path / "receipts"
    rec.mkdir()
    (rec / "note.json").write_text(
        '{"runtime": "antigravity", "invoked": false, "note": "was NOT invoked"}')
    r = crse.level3_governed("antigravity", rec)
    assert r["verdict"] == UNKNOWN
    assert r["malformed"], "a naming-only file must be reported as malformed, not accepted"


def test_M4_the_checkers_own_output_cannot_certify_it(tmp_path):
    """Self-certification: --receipts pointed at this command's own --json output."""
    rec = tmp_path / "receipts"
    rec.mkdir()
    (rec / "prior.json").write_text(json.dumps(
        [{"runtime": "gemini", "L1_installed": {"verdict": "YES"}, "overall": "PARTIAL-EVIDENCE"}]))
    assert crse.level3_governed("gemini", rec)["verdict"] == UNKNOWN


def test_M4_a_well_formed_receipt_is_L3(tmp_path):
    rec = tmp_path / "receipts"
    rec.mkdir()
    (rec / "r.json").write_text(
        '{"runtime": "gemini", "invoked": true, "outcome": "exit 0, 1m43s"}')
    assert crse.level3_governed("gemini", rec)["verdict"] == YES


def test_M4_an_invocation_with_no_outcome_is_not_L3(tmp_path):
    rec = tmp_path / "receipts"
    rec.mkdir()
    (rec / "r.json").write_text('{"runtime": "gemini", "invoked": true, "outcome": "  "}')
    assert crse.level3_governed("gemini", rec)["verdict"] == UNKNOWN


def test_M7_overall_is_pinned_for_a_definite_no(onpath):
    """`overall` is what render() shows and the matrix reports; it had no test."""
    r = crse.assess("absent-runtime", None)
    assert r["overall"] == "NOT-DEMONSTRATED"


def test_M7_overall_is_pinned_for_partial_evidence(onpath):
    fake_exe(onpath, "gemini", version="0.59.0", help_text="Usage: gemini -p PROMPT")
    assert crse.assess("gemini", None)["overall"] == "PARTIAL-EVIDENCE"


def test_M7_an_executable_reporting_no_version_is_UNKNOWN_at_L1(onpath):
    p = onpath / "silent"
    p.write_text("#!/bin/sh\nexit 0\n")
    p.chmod(0o755)
    assert crse.level1_installed("silent")["verdict"] == UNKNOWN


def test_M6_the_command_creates_no_files(tmp_path, monkeypatch):
    """The old non-mutating test compared mtimes of PRE-EXISTING files, so a NEW file survived."""
    d = tmp_path / "bin"
    d.mkdir()
    fake_exe(d, "gemini", version="0.59.0", help_text="Usage: gemini -p P (non-interactive)")
    monkeypatch.setenv("PATH", str(d))
    before = {p for p in tmp_path.rglob("*")}
    crse.assess("gemini", None)
    assert {p for p in tmp_path.rglob("*")} == before, "no file may be created"


# ===================================================================================
# Round-two review, 2026-09-09.
# ===================================================================================

def test_MAJOR4_prose_beginning_with_the_token_is_not_an_instruction_surface(onpath):
    """`^\\s*<tok>` matched any line starting with the word -- including prose DENYING it."""
    for help_text in ("Interactive shell only.\nexec support was removed in 2.0.",
                      "Description:\n  exec is not supported; this build is interactive only."):
        fake_exe(onpath, "codex", help_text=help_text)
        # After F2 a help text yields UNKNOWN, never NO. What this test pins is that the
        # prose did not DECLARE `exec`.
        r = crse.level2_instructable("codex")
        assert r["verdict"] != YES, repr(help_text)
        assert "exec" not in r["declared_surfaces"]["subcommands"], repr(help_text)


def test_MAJOR4_prose_naming_agent_bundles_is_not_an_instruction_surface(onpath):
    fake_exe(onpath, "antigravity",
             help_text="Antigravity launcher.\nagent bundles live in ~/.antigravity")
    r = crse.level2_instructable("antigravity")
    assert r["verdict"] != YES
    assert "agent" not in r["declared_surfaces"]["subcommands"]


def test_MAJOR4_a_real_subcommand_entry_still_matches(onpath):
    fake_exe(onpath, "codex", help_text="Commands:\n  exec     Run a prompt non-interactively\n")
    assert crse.level2_instructable("codex")["verdict"] == YES


def test_MAJOR4_a_usage_line_subcommand_still_matches(onpath):
    fake_exe(onpath, "codex", help_text="Usage: codex exec <PROMPT>\n")
    assert "exec" in crse.level2_instructable("codex")["declared_surfaces"]["subcommands"]


def test_MAJOR5_invoked_false_with_an_outcome_is_not_L3(tmp_path):
    """Unmasks the `invoked` guard: the prior fixture also lacked an outcome, so the
    outcome guard rejected it either way and removing the invoked guard went undetected."""
    rec = tmp_path / "receipts"
    rec.mkdir()
    (rec / "r.json").write_text(
        '{"runtime": "gemini", "invoked": false, "outcome": "planned only; not executed"}')
    r = crse.level3_governed("gemini", rec)
    assert r["verdict"] == UNKNOWN, "invoked:false must not certify, outcome notwithstanding"
    assert r["malformed"]


def test_MAJOR6_a_malformed_config_exits_three(tmp_path):
    import subprocess, sys as _s
    cmd = REPO / "scripts" / "check_runtime_support_evidence.py"
    for payload in ('["gemini"]', '{"runtimes": [5]}', '{"runtimes": [["x"]]}',
                    '{"runtimes": "gem"}', '{"runtimes": {"a": 1}}'):
        cfg = tmp_path / "c.json"
        cfg.write_text(payload)
        proc = subprocess.run([_s.executable, str(cmd), "--config", str(cfg)],
                              capture_output=True, text=True)
        assert proc.returncode == 3, f"{payload} should exit 3, got {proc.returncode}"


def test_MAJOR6_a_string_runtimes_value_does_not_iterate_characters(tmp_path):
    """`"gem"` reported on runtimes 'g', 'e', 'm'."""
    import subprocess, sys as _s
    cfg = tmp_path / "c.json"
    cfg.write_text('{"runtimes": "gem"}')
    proc = subprocess.run([_s.executable, str(REPO / "scripts" /
                           "check_runtime_support_evidence.py"), "--config", str(cfg)],
                          capture_output=True, text=True)
    assert "g:" not in proc.stdout and proc.returncode == 3


def test_MINOR12_L2_has_one_schema_whether_or_not_the_runtime_is_installed(onpath):
    absent = crse.assess("definitely-absent", None)["L2_instructable"]
    fake_exe(onpath, "gemini", version="1.0", help_text="Usage: gemini -p P (non-interactive)")
    present = crse.assess("gemini", None)["L2_instructable"]
    assert set(absent) == set(present), f"two L2 shapes: {set(absent) ^ set(present)}"


# ===================================================================================
# Round three. BLOCKING-A: the checker reported a confident L2 NO for a runtime whose
# help declares a prompt-taking `chat` subcommand, and the matrix published it as fact.
# ===================================================================================

ANTIGRAVITY_HELP = """Antigravity 1.107.0

Usage: antigravity [options] [paths...]

Options
  -d --diff <file> <file>   Compare two files with each other.
  -g --goto <file:line>     Open a file at the path.

Subcommands
  chat         Pass in a prompt to run in a chat session in the current working
               directory.
  serve-web    Run a server that displays the editor UI in browsers.
  tunnel       Make the current machine accessible from vscode.dev.
"""


def test_BLOCKINGA_a_declared_subcommand_block_is_read(onpath):
    """Verbatim shape of the real help. `chat` IS declared -- which round three got right --
    but declaration alone is not L2 (F1), so the verdict is UNKNOWN, not YES."""
    fake_exe(onpath, "antigravity", help_text=ANTIGRAVITY_HELP)
    r = crse.level2_instructable("antigravity")
    assert "chat" in r["declared_surfaces"]["subcommands"]
    assert "chat" in r["surface_tokens_found"]
    assert r["verdict"] == UNKNOWN


def test_BLOCKINGA_an_unmatched_token_list_is_UNKNOWN_not_NO(onpath, monkeypatch):
    """The tool's own rule, applied to its own config: not finding what we sought is an
    unproven expectation, not a demonstrated absence."""
    monkeypatch.setitem(crse.INSTRUCTION_SURFACES, "antigravity", ["exec", "--prompt"])
    fake_exe(onpath, "antigravity", help_text=ANTIGRAVITY_HELP)
    r = crse.level2_instructable("antigravity")
    assert r["verdict"] == UNKNOWN
    assert "chat" in r["why"] and "unproven expectation" in r["why"]


def test_a_help_text_with_no_surfaces_at_all_is_UNKNOWN_not_NO(onpath):
    """F2: NO is a claim about the RUNTIME and must never be reachable from OUR parser
    failing. Measured on gcloud, npm and brew before this change."""
    fake_exe(onpath, "gemini", help_text="An interactive editor. No flags, no subcommands.")
    r = crse.level2_instructable("gemini")
    assert r["verdict"] == UNKNOWN
    assert "statement about the parser, not about the runtime" in r["why"]


# --- MAJOR-B: the five false positives and five false negatives ---------------------

@pytest.mark.parametrize("help_text", [
    "Note: codex exec was removed in 2.0; use the API instead.",
    "Interactive only. Run codex\nexec is not supported.",
    "The codex exec subcommand has been REMOVED.",
    "Notes:\n  agent  bundles are not runnable from the CLI.",
    "This build ignores -p entirely; interactive only.",
])
def test_MAJORB_prose_never_declares_a_surface(onpath, help_text):
    fake_exe(onpath, "codex", help_text=help_text)
    assert "exec" not in crse.level2_instructable("codex")["declared_surfaces"]["subcommands"]


@pytest.mark.parametrize("help_text", [
    "Commands:\n\texec\tRun non-interactively",
    "Commands:\n  exec Run non-interactively",
    "Commands:\n  exec\n  login",
    "Commands:\n  exec:  Run non-interactively",
    "Usage: codex exec <PROMPT>",
])
def test_MAJORB_real_help_formats_are_read(onpath, help_text):
    """Parser intent: the format is READ. The verdict is a separate question (F1)."""
    fake_exe(onpath, "codex", help_text=help_text)
    r = crse.level2_instructable("codex")
    assert "exec" in r["declared_surfaces"]["subcommands"], \
        f"format not read: {help_text!r} -> {r['declared_surfaces']}"


# --- MAJOR-F: a present-but-empty outcome ---------------------------------------------

@pytest.mark.parametrize("outcome", ["null", "false", "0", "[]", "{}", '"   "'])
def test_MAJORF_an_empty_outcome_does_not_certify(tmp_path, outcome):
    rec = tmp_path / "receipts"
    rec.mkdir()
    (rec / "r.json").write_text(
        '{"runtime": "gemini", "invoked": true, "outcome": %s}' % outcome)
    assert crse.level3_governed("gemini", rec)["verdict"] == UNKNOWN, outcome


# --- MINOR-H: a behavioural boundary test, not a source grep ---------------------------

def test_MINORH_L3_never_invokes_the_runtime(tmp_path, monkeypatch):
    """Replaces a grep with a fake runtime that RECORDS every invocation."""
    d = tmp_path / "bin"
    d.mkdir()
    log = tmp_path / "invocations.log"
    p = d / "gemini"
    p.write_text("#!/bin/sh\necho \"$@\" >> %s\nexit 0\n" % log)
    p.chmod(0o755)
    monkeypatch.setenv("PATH", str(d))
    rec = tmp_path / "receipts"
    rec.mkdir()
    (rec / "r.json").write_text('{"runtime": "gemini", "invoked": true, "outcome": "ok"}')
    crse.level3_governed("gemini", rec)
    assert not log.exists(), "L3 must read a receipt, never invoke the runtime"


def test_MINORH_L1_and_L2_invoke_only_version_and_help(tmp_path, monkeypatch):
    d = tmp_path / "bin"
    d.mkdir()
    log = tmp_path / "invocations.log"
    p = d / "gemini"
    p.write_text("#!/bin/sh\necho \"$@\" >> %s\nexit 0\n" % log)
    p.chmod(0o755)
    monkeypatch.setenv("PATH", str(d))
    crse.assess("gemini", None)
    seen = {l.strip() for l in log.read_text().splitlines()} if log.exists() else set()
    assert seen <= {"--version", "--help"}, f"unexpected invocation(s): {seen}"


# --- the three untested crse paths (C10, C16, C17) --------------------------------------

def test_C10_a_not_installed_runtime_is_a_definite_NO_at_L2(onpath):
    """NO is legitimate here and this is the boundary of the class rule: we OBSERVED the
    absence on PATH. The warrant says so, rather than 'we did not find a surface'."""
    r = crse.level2_instructable("gemini")          # declared family, absent binary
    assert r["verdict"] == NO
    assert "does not resolve on PATH" in r["warrant"]


def test_C16_a_version_from_a_failing_binary_is_not_accepted(onpath):
    p = onpath / "gemini"
    p.write_text("#!/bin/sh\nif [ \"$1\" = \"--version\" ]; then echo 9.9.9; exit 7; fi\nexit 0\n")
    p.chmod(0o755)
    assert crse.level1_installed("gemini")["verdict"] == UNKNOWN


def test_C17_a_receipts_path_that_is_not_a_directory_is_UNKNOWN(tmp_path):
    f = tmp_path / "notadir"
    f.write_text("x")
    r = crse.level3_governed("gemini", f)
    assert r["verdict"] == UNKNOWN and "does not resolve" in r["why"]


def test_MINORI_a_blank_runtime_name_exits_three(tmp_path):
    import subprocess as _sp, sys as _s
    proc = _sp.run([_s.executable, str(REPO / "scripts" / "check_runtime_support_evidence.py"),
                    "--runtime", "  "], capture_output=True, text=True)
    assert proc.returncode == 3


# ===================================================================================
# Round four. F1: the retraction that removed a false NO published a false YES.
# ===================================================================================

CHAT_ONLY_HELP = """Antigravity 1.107.0

Usage: antigravity [options] [paths...]

To read from stdin, append '-' (e.g. 'ps aux | grep code | antigravity -')

Subcommands
  chat         Pass in a prompt to run in a chat session in the current working
               directory.
"""

NONINTERACTIVE_HELP = """Codex 1.0

Commands:
  exec     Run Codex non-interactively [aliases: e]
"""


def test_F1_a_declared_prompt_subcommand_is_not_proof_of_non_interactivity(onpath, monkeypatch):
    """L2 means 'exposes a NON-INTERACTIVE instruction surface'. `chat` is declared and every
    one of its options is window management; declaration is not capability."""
    monkeypatch.setitem(crse.INSTRUCTION_SURFACES, "antigravity", ["chat"])
    fake_exe(onpath, "antigravity", help_text=CHAT_ONLY_HELP)
    r = crse.level2_instructable("antigravity")
    assert r["surface_tokens_found"] == ["chat"]
    assert r["verdict"] == UNKNOWN, "a declared token must not buy a YES"
    assert "NON-INTERACTIVE" in r["why"]


def test_F1_an_explicit_vendor_statement_earns_YES(onpath, monkeypatch):
    monkeypatch.setitem(crse.INSTRUCTION_SURFACES, "codex", ["exec"])
    fake_exe(onpath, "codex", help_text=NONINTERACTIVE_HELP)
    r = crse.level2_instructable("codex")
    assert r["verdict"] == YES and r["noninteractive_evidence"] == "non-interactive"


def test_F1_stdin_alone_is_not_evidence_of_headless_operation(onpath, monkeypatch):
    """`ps aux | grep code | antigravity -` pipes into a GUI editor and still opens a window."""
    monkeypatch.setitem(crse.INSTRUCTION_SURFACES, "antigravity", ["chat"])
    fake_exe(onpath, "antigravity", help_text=CHAT_ONLY_HELP)
    assert "stdin" in CHAT_ONLY_HELP
    assert crse.level2_instructable("antigravity")["verdict"] == UNKNOWN


def test_F1_desktop_window_options_are_named_as_counter_evidence(onpath, monkeypatch):
    monkeypatch.setitem(crse.INSTRUCTION_SURFACES, "antigravity", ["chat"])
    fake_exe(onpath, "antigravity", help_text=CHAT_ONLY_HELP +
             "\n  --maximize  Maximize the chat session view.\n  --new-window  Open a window.\n")
    r = crse.level2_instructable("antigravity")
    assert r["verdict"] == UNKNOWN and "desktop-window controls" in r["why"]


# --- F2: NO must never be reachable from OUR parser failing ---------------------------

def test_F2_an_unparsed_help_layout_is_UNKNOWN_not_NO(onpath, monkeypatch):
    """Measured on gcloud, npm and brew -- all subcommand-rich -- under the old branch."""
    monkeypatch.setitem(crse.INSTRUCTION_SURFACES, "weird", ["exec"])
    fake_exe(onpath, "weird", help_text="NAME\n    weird - does things\n\nSEE ALSO\n    docs\n")
    r = crse.level2_instructable("weird")
    assert r["verdict"] == UNKNOWN
    assert "statement about the parser, not about the runtime" in r["why"]


def test_F2_no_help_output_at_all_is_UNKNOWN(onpath, monkeypatch):
    monkeypatch.setitem(crse.INSTRUCTION_SURFACES, "silent", ["exec"])
    p = onpath / "silent"
    p.write_text("#!/bin/sh\nexit 1\n")
    p.chmod(0o755)
    assert crse.level2_instructable("silent")["verdict"] == UNKNOWN


# --- F6: prose inside a Commands block ---------------------------------------------------

@pytest.mark.parametrize("body", [
    "  exec was removed in 2.0; use the API instead.",
    "  exec is not supported in this build.",
    "  agent cannot be run from the CLI.",
])
def test_F6_prose_inside_a_commands_block_declares_nothing(body):
    got = crse.parse_help_surfaces(f"Commands:\n{body}\n")
    assert got["subcommands"] == [], got


def test_F6_a_real_entry_inside_a_commands_block_still_parses():
    got = crse.parse_help_surfaces("Commands:\n  exec     Run non-interactively\n")
    assert got["subcommands"] == ["exec"]


# --- F9: the receipt runtime match is a field read, not a substring ----------------------

def test_F9_a_runtime_named_only_in_another_field_does_not_certify(tmp_path):
    rec = tmp_path / "receipts"
    rec.mkdir()
    (rec / "r.json").write_text(json.dumps(
        {"runtime": "codex", "invoked": True, "outcome": "compared against gemini output"}))
    assert crse.level3_governed("gemini", rec)["verdict"] == UNKNOWN, \
        "'gemini' appears in the outcome text, not in the runtime field"
