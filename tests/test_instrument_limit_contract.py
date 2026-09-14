"""The defect-class contract: an instrument may not convert its own limit into a fact.

Four independent review rounds over two instruments produced what looked like eight defects.
They are one defect, eight times:

    THE INSTRUMENT CONVERTS A LIMIT OF ITS OWN INTO AN ASSERTION ABOUT ITS SUBJECT.

Patching instances did not converge -- each round's repair fixed the instance and the next round
found the next instance. This file tests the CLASS. It feeds every verdict-producing function an
input the instrument cannot read, and requires the answer to be indefinite.

A new check that repeats the class fails here without anyone having to notice the instance.
"""

from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
from warranted_verdict import (  # noqa: E402
    DEFINITE,
    INDEFINITE,
    UnwarrantedVerdict,
    Verdict,
    worst,
)


def load(name: str, rel: str):
    spec = importlib.util.spec_from_file_location(name, REPO / rel)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


crse = load("crse_c", "scripts/check_runtime_support_evidence.py")
fvg = load("fvg_c", "scripts/forecast_value_gate.py")
chlc = load("chlc_c", "scripts/check_host_layout_conformance.py")
crc = load("crc_c", "scripts/check_receipt_continuity.py")


# ============================ the primitive ============================


def test_a_definite_verdict_cannot_be_stated_without_a_warrant():
    for ctor in (Verdict.no, Verdict.yes, Verdict.passed, Verdict.failed):
        with pytest.raises(UnwarrantedVerdict):
            ctor("")


def test_a_definite_verdict_may_not_carry_a_limit():
    """A verdict resting on anything the instrument could NOT do is indefinite."""
    with pytest.raises(UnwarrantedVerdict):
        Verdict(state="NO", warrant="looked", limit="could not parse the layout")


def test_an_indefinite_verdict_must_name_its_limit():
    for ctor in (Verdict.unknown, Verdict.unavailable, Verdict.inert):
        with pytest.raises(UnwarrantedVerdict):
            ctor("")


def test_observed_absence_is_a_legitimate_warrant_for_NO():
    """The rule is not 'never say NO'. It is 'say NO only from an observation'."""
    v = Verdict.no(warrant="the executable does not resolve on PATH")
    assert v.state == "NO" and v.is_definite


def test_worst_does_not_launder_an_indefinite_state_into_a_pass():
    assert worst([Verdict.passed(warrant="ok"), Verdict.unknown(limit="not readable")]) == "UNKNOWN"
    assert (
        worst([Verdict.passed(warrant="ok"), Verdict.unavailable(limit="absent")]) == "UNAVAILABLE"
    )


def test_an_inert_check_neither_fails_nor_passes_on_its_own():
    assert worst([Verdict.inert(limit="precondition absent")]) == "INERT"
    assert worst([Verdict.passed(warrant="ok"), Verdict.inert(limit="did not fire")]) == "PASS"


# ==================== the class, applied to the real instruments ====================
# Each case is an input the instrument CANNOT read. The answer must be indefinite.


def test_CLASS_an_unreadable_help_layout_yields_no_claim_about_the_runtime(tmp_path, monkeypatch):
    """Reproduced on gcloud, npm, brew and git before the repair."""
    d = tmp_path / "bin"
    d.mkdir()
    p = d / "weird"
    p.write_text(
        '#!/bin/sh\nif [ "$1" = "--version" ]; then echo 1.0; exit 0; fi\n'
        "echo 'NAME\n    weird - does things\nSEE ALSO\n    the manual'\nexit 0\n"
    )
    p.chmod(0o755)
    monkeypatch.setenv("PATH", str(d))
    monkeypatch.setitem(crse.INSTRUCTION_SURFACES, "weird", ["exec"])
    r = crse.level2_instructable("weird")
    assert r["verdict"] in INDEFINITE, (
        "an unrecognised layout is OUR limit; it may not become 'the runtime has no surface'"
    )


def test_CLASS_a_declared_surface_is_not_a_capability_claim(tmp_path, monkeypatch):
    """`chat` is declared; non-interactivity is a separate claim needing separate evidence."""
    d = tmp_path / "bin"
    d.mkdir()
    p = d / "gui"
    p.write_text(
        '#!/bin/sh\nif [ "$1" = "--version" ]; then echo 1.0; exit 0; fi\n'
        "printf 'Subcommands\\n  chat   Pass in a prompt.\\n'\nexit 0\n"
    )
    p.chmod(0o755)
    monkeypatch.setenv("PATH", str(d))
    monkeypatch.setitem(crse.INSTRUCTION_SURFACES, "gui", ["chat"])
    r = crse.level2_instructable("gui")
    assert "chat" in r["surface_tokens_found"], "the surface IS declared"
    assert r["verdict"] in INDEFINITE, "declaration alone may not become a capability claim"


def test_CLASS_an_unresolvable_evidence_path_yields_no_claim_about_the_evidence(tmp_path):
    (tmp_path / "src.md").write_text("x")
    pkt = {
        "cap_su": 10,
        "pool_allows_two_l3": True,
        "candidates": [
            {
                "id": "A",
                "disposition": "SELECT",
                "tier": "T1",
                "su": 7,
                "predicted_v1": "L3",
                "class": "capability",
                "source": {"path": "/etc/hosts", "pattern": "localhost"},
            }
        ],
    }
    res = fvg.forecast(pkt, None, tmp_path)
    assert res["limbs"]["CON-EVIDENCE"]["verdict"] in INDEFINITE


def test_CLASS_a_class_we_cannot_resolve_yields_no_share_claim(tmp_path):
    (tmp_path / "src.md").write_text("x")
    pkt = {
        "cap_su": 10,
        "pool_allows_two_l3": True,
        "candidates": [
            {
                "id": "A",
                "disposition": "SELECT",
                "tier": "T1",
                "su": 7,
                "predicted_v1": "L3",
                "initiative_path": "planning/initiatives/ABSENT.md",
                "source": {"path": "src.md", "pattern": "x"},
            }
        ],
    }
    res = fvg.forecast(pkt, None, tmp_path)
    assert res["limbs"]["CON-CAPABILITY-SHARE"]["verdict"] in INDEFINITE


def test_CLASS_an_ungoverned_region_yields_no_conformance_claim(tmp_path):
    """CAP-HFL-006 in the same shape: no rule covers it, so it is not graded."""
    root = tmp_path / "r"
    (root / "junk").mkdir(parents=True)
    (root / "junk" / "x.tmp").write_text("x")
    m = tmp_path / "m.json"
    m.write_text(
        json.dumps({"paths": [{"pattern": "data/*.toml", "class": "config", "tier": "record"}]})
    )
    res = chlc.assess(m, root, None, ["/github/"])
    graded = [f for f in res["findings"] if f["subject"].startswith("observed:")]
    assert graded and all(f["outcome"] == chlc.OUTSIDE for f in graded)
    assert res["counts"][chlc.DRIFT] == 0


def test_CLASS_an_unrunnable_verification_yields_no_verification_claim(tmp_path):
    import subprocess

    r = tmp_path / "repo"
    r.mkdir()
    subprocess.run(["git", "-C", str(r), "init", "-q"], check=True)
    (r / "t.txt").write_text("x\n")
    subprocess.run(["git", "-C", str(r), "add", "-A"], check=True)
    subprocess.run(
        [
            "git",
            "-C",
            str(r),
            "-c",
            "user.name=t",
            "-c",
            "user.email=t@t",
            "-c",
            "commit.gpgsign=false",
            "commit",
            "-q",
            "-m",
            "c",
        ],
        check=True,
    )
    head = subprocess.run(
        ["git", "-C", str(r), "rev-parse", "HEAD"], capture_output=True, text=True, check=True
    ).stdout.strip()
    import hashlib

    dig = hashlib.sha256((r / "t.txt").read_bytes()).hexdigest()
    rec = {"path": "t.txt", "commit": head, "digest": dig}
    rp, mp = tmp_path / "r.json", tmp_path / "m.json"
    rp.write_text(json.dumps(rec))
    mp.write_text(json.dumps(rec))
    res = crc.evaluate(rec, rec, r, None, False)
    assert res["target_continuity"]["checks"]["installed_route"]["state"] == crc.UNAVAILABLE
    assert res["overall"] != crc.HOLDS


# ==================== the class stated as an invariant ====================


@pytest.mark.parametrize(
    "layout,label",
    [
        ("NAME\n    tool - does things\nSEE ALSO\n    the manual\n", "man-page"),
        ("\x1b[1mCommands:\x1b[0m\n  \x1b[32mexec\x1b[0m  run it\n", "ANSI-coloured"),
        ("Befehle:\n  exec   nicht-interaktiv starten\n", "localized heading"),
        ("Available Commands:\n  exec   run\n", "cobra"),
        ("positional arguments:\n  {exec,chat}\n", "argparse"),
        ("CORE COMMANDS\n  exec:  run\n", "gh-style"),
        ("", "no output at all"),
    ],
)
def test_CLASS_a_layout_this_parser_cannot_read_never_yields_a_definite_verdict(
    tmp_path, monkeypatch, layout, label
):
    """The one-sentence rule, exercised end-to-end on layouts the parser genuinely cannot read.

    This is the test a NEW check must pass without anyone re-deriving the eight instances. Six
    of these seven layouts belong to real, widely-used CLIs, and the parser reads none of them
    today -- which is fine, and is exactly the point: not reading a layout is a fact about this
    parser, and it may not be reported as a fact about the tool.
    """
    d = tmp_path / "bin"
    d.mkdir()
    script = d / "subject"
    body = layout.replace("\\", "\\\\").replace("'", "'\\''")
    script.write_text(
        "#!/bin/sh\n"
        'if [ "$1" = "--version" ]; then echo 1.0; exit 0; fi\n'
        f"printf '%s' '{body}'\n"
        "exit 0\n"
    )
    script.chmod(0o755)
    monkeypatch.setenv("PATH", str(d))
    monkeypatch.setitem(crse.INSTRUCTION_SURFACES, "subject", ["exec"])

    r = crse.level2_instructable("subject")
    if r["surface_tokens_found"]:
        pytest.skip(f"the parser DID read the {label} layout; not a limit case")
    assert r["verdict"] in INDEFINITE, (
        f"{label}: the parser found nothing, and the verdict is {r['verdict']!r}. "
        f"A layout this parser cannot read is OUR limit and must never be reported as the "
        f"runtime lacking a surface."
    )
    assert r["why"], "an indefinite verdict must say what could not be established"


def test_CLASS_the_contract_covers_every_verdict_state_the_runtime_checker_can_emit():
    """Guard against the contract silently ceasing to apply: if a new definite state is added
    to the checker, this test names it."""
    emitted = {crse.YES, crse.NO, crse.UNKNOWN}
    assert emitted <= (DEFINITE | INDEFINITE), (
        f"the checker emits a state the warrant contract does not classify: "
        f"{emitted - (DEFINITE | INDEFINITE)}"
    )


# ==================== the primitive must be LOAD-BEARING, not decorative ====================
# A control that is true in prose and absent in code is round three's MAJOR-G, and it was the
# first state of this very module: `warranted_verdict` existed and NOTHING imported it.


def test_the_runtime_checker_actually_uses_the_checked_constructors():
    src = (REPO / "scripts" / "check_runtime_support_evidence.py").read_text()
    assert "from warranted_verdict import Verdict" in src, (
        "the primitive is decorative unless the instrument imports it"
    )
    import re

    bare = re.findall(r'"verdict":\s*(?:NO|YES)\b', src)
    assert not bare, (
        f"{len(bare)} definite verdict(s) are still constructed as bare dicts, bypassing the "
        f"warrant check. Partial wiring is how a control becomes decorative."
    )


def test_every_definite_verdict_the_runtime_checker_emits_carries_a_warrant(tmp_path, monkeypatch):
    """Behavioural, not a grep: drive the checker and inspect what it produced."""
    d = tmp_path / "bin"
    d.mkdir()
    monkeypatch.setenv("PATH", str(d))
    results = [crse.assess("definitely-absent", None)]
    p = d / "gemini"
    p.write_text(
        '#!/bin/sh\nif [ "$1" = "--version" ]; then echo 1.0; exit 0; fi\n'
        "echo 'Usage: gemini -p P (non-interactive)'\nexit 0\n"
    )
    p.chmod(0o755)
    rec = tmp_path / "rec"
    rec.mkdir()
    (rec / "r.json").write_text('{"runtime":"gemini","invoked":true,"outcome":"ok"}')
    results.append(crse.assess("gemini", rec))

    for res in results:
        for key in ("L1_installed", "L2_instructable", "L3_governed"):
            lv = res[key]
            if lv["verdict"] in DEFINITE:
                assert (lv.get("warrant") or "").strip(), (
                    f"{res['runtime']} {key} = {lv['verdict']} with no warrant: "
                    f"a claim about the subject with nothing entitling it"
                )
            else:
                assert (lv.get("limit") or lv.get("why") or "").strip(), (
                    f"{res['runtime']} {key} = {lv['verdict']} without naming its limit"
                )
