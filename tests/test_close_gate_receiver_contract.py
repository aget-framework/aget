"""Receiver-shaped acceptance oracle for the close-gate correction package."""

import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
GUARD = ROOT / "scripts" / "close_gate_check.py"
LIFECYCLE = ROOT / "scripts" / "close_gate_lifecycle.py"


def run_guard(path, *args, as_json=False, env=None, guard=GUARD, cwd=ROOT):
    command = [sys.executable, str(guard), str(path)]
    if as_json:
        command.append("--json")
    command.extend(args)
    merged_env = os.environ.copy()
    merged_env["PYTHONDONTWRITEBYTECODE"] = "1"
    if env:
        merged_env.update(env)
    result = subprocess.run(command, capture_output=True, text=True, cwd=cwd, env=merged_env)
    payload = json.loads(result.stdout) if as_json and result.stdout.strip() else None
    return result, payload


def write_plan(path, body="", status="In Progress"):
    path.write_text(
        f"# PROJECT_PLAN: Receiver Probe\n\n**Plan_Status**: {status}\n\n{body}\n",
        encoding="utf-8")
    return path


def unfinished(reason_key, subject, disposition="obsolete", note="reason=receiver probe"):
    return (
        "## Unfinished at Close\n\n"
        "| reason_key | affected_subject | disposition | note |\n"
        "|---|---|---|---|\n"
        f"| {reason_key} | {subject} | {disposition} | {note} |\n"
    )


def test_package_owns_complete_executable_module_and_default_spec_path():
    assert LIFECYCLE.is_file()
    assert not (ROOT / "scripts" / "close_gate_lifecycle_ext.py").exists()
    source = GUARD.read_text(encoding="utf-8")
    lifecycle_source = LIFECYCLE.read_text(encoding="utf-8")
    assert "from close_gate_lifecycle import" in source
    assert "close_gate_lifecycle_ext" not in source
    assert 'parent.parent / "specs"' in lifecycle_source
    assert 'parents[2] / "aget"' not in lifecycle_source


@pytest.mark.parametrize("as_json", [False, True])
def test_orphan_only_accounting_blocks_identically_in_both_channels(tmp_path, as_json):
    plan = write_plan(tmp_path / "orphan.md", unfinished(
        "gate_status_pending", "absent subject"))
    result, payload = run_guard(
        plan, "--phase", "exit", "--disposition", "Closed", as_json=as_json)
    assert result.returncode == 2
    if as_json:
        assert payload["exit_code"] == 2
        assert payload["accounting"]["orphan"]
    else:
        assert "close-gate: BLOCK" in result.stdout
        assert "[accounting-orphan]" in result.stdout


@pytest.mark.parametrize("as_json", [False, True])
def test_nonwaivable_accounting_blocks_identically_in_both_channels(tmp_path, as_json):
    body = "## Closure Checklist\n\n- [ ] Retrospective written\n\n" + unfinished(
        "unchecked_closure_item", "Retrospective written")
    plan = write_plan(tmp_path / "nonwaivable.md", body)
    result, payload = run_guard(
        plan, "--phase", "exit", "--disposition", "Closed", as_json=as_json)
    assert result.returncode == 2
    if as_json:
        assert payload["accounting"]["nonwaivable"]
    else:
        assert "[accounting-nonwaivable]" in result.stdout


def test_transition_only_block_has_nonzero_human_reason_count(tmp_path):
    plan = write_plan(tmp_path / "transition.md", status="Draft")
    result, _ = run_guard(plan, "--phase", "entry", "--disposition", "Complete")
    assert result.returncode == 2
    assert "BLOCK — 1 decision reason(s)" in result.stdout
    assert "[lawful-transition]" in result.stdout


def test_human_channel_surfaces_independence_and_value_warnings(tmp_path):
    body = "## Closure Checklist\n\n- [x] Downstream deployment verified\n"
    plan = write_plan(tmp_path / "warnings.md", body, status="Complete")
    result, _ = run_guard(plan, "--phase", "exit", "--disposition", "Complete")
    assert result.returncode == 0
    assert "⚠ INDEPENDENCE" in result.stdout
    assert "⚠ VALUE" in result.stdout


def test_fully_accounted_human_verdict_does_not_claim_no_signals(tmp_path):
    body = "**Gate_Status**: Pending\n\n" + unfinished(
        "gate_status_pending", "**Gate_Status**: Pending")
    plan = write_plan(tmp_path / "accounted.md", body)
    result, _ = run_guard(plan, "--phase", "exit", "--disposition", "Closed")
    assert result.returncode == 0
    assert "close-gate: CLEAN — 1 unfinished finding occurrence(s) fully accounted" in result.stdout
    assert "no unchecked conformance signals" not in result.stdout


def test_rejected_mutation_preserves_target_bytes(tmp_path):
    plan = write_plan(tmp_path / "preserved.md", "**Gate_Status**: Pending")
    before = plan.read_bytes()
    rows = tmp_path / "rows.json"
    rows.write_text(json.dumps([{
        "reason_key": "gate_status_pending",
        "affected_subject": "wrong subject",
        "disposition": "obsolete",
        "note": "reason=does not reconcile",
    }]), encoding="utf-8")
    result, payload = run_guard(
        plan, "--phase", "exit", "--disposition", "Closed",
        "--write-unfinished-json", str(rows), as_json=True)
    assert result.returncode == 2
    assert payload["mutation"] == "rejected-target-preserved"
    assert plan.read_bytes() == before


def test_valid_mutation_is_atomic_and_received_state_repasses(tmp_path):
    plan = write_plan(tmp_path / "committed.md", "**Gate_Status**: Pending")
    inode_before = plan.stat().st_ino
    rows = tmp_path / "rows.json"
    rows.write_text(json.dumps([{
        "reason_key": "gate_status_pending",
        "affected_subject": "**Gate_Status**: Pending",
        "disposition": "obsolete",
        "note": "reason=accepted receiver disposition",
    }]), encoding="utf-8")
    result, payload = run_guard(
        plan, "--phase", "exit", "--disposition", "Closed",
        "--write-unfinished-json", str(rows), as_json=True)
    assert result.returncode == 0, payload
    assert payload["mutation"] == "committed-atomically"
    assert plan.stat().st_ino != inode_before
    received, received_payload = run_guard(
        plan, "--phase", "exit", "--disposition", "Closed", as_json=True)
    assert received.returncode == 0
    assert received_payload["mutation"] == "not-requested"


@pytest.mark.parametrize("case", ["missing-phase", "missing-file", "missing-schema"])
def test_json_errors_are_structured(case, tmp_path):
    plan = write_plan(tmp_path / "plan.md")
    args = ["--phase", "exit", "--disposition", "Complete"]
    env = None
    target = plan
    if case == "missing-phase":
        args = ["--disposition", "Complete"]
    elif case == "missing-file":
        target = tmp_path / "absent.md"
    else:
        env = {"AGET_PROJECT_PLAN_SPEC": str(tmp_path / "absent-spec.md")}
    result, payload = run_guard(target, *args, as_json=True, env=env)
    assert result.returncode == 3
    assert payload["schema"] == "close_gate_check/error/v1"
    assert payload["exit_code"] == 3
    assert payload["error"].startswith("E-")


def test_clean_room_copy_runs_without_sibling_repository_topology(tmp_path):
    package = tmp_path / "received"
    scripts = package / "scripts"
    specs = package / "specs"
    scripts.mkdir(parents=True)
    specs.mkdir()
    shutil.copy2(GUARD, scripts / GUARD.name)
    shutil.copy2(LIFECYCLE, scripts / LIFECYCLE.name)
    shutil.copy2(ROOT / "specs" / "AGET_PROJECT_PLAN_SPEC.md",
                 specs / "AGET_PROJECT_PLAN_SPEC.md")
    plan = write_plan(package / "plan.md")
    result, payload = run_guard(
        plan, "--phase", "exit", "--disposition", "Complete", as_json=True,
        guard=scripts / GUARD.name, cwd=package)
    assert result.returncode == 0, payload


def test_public_skill_has_no_stale_unconditional_gate_rule():
    skill = (ROOT / ".claude" / "skills" / "aget-close-project" / "SKILL.md").read_text(
        encoding="utf-8")
    assert "REFUSE close if any gate `[ ]`" not in skill
    assert "transactional writer" in skill
    assert "preserves the target bytes unchanged" in skill
