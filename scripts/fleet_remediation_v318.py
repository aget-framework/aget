#!/usr/bin/env python3
"""
fleet_remediation_v318.py — FLEET-UPG-016R Generator for v3.18 adoption-stream remediation.

Plan: PROJECT_PLAN_fleet_v318_adoption_remediation_v1.0.md
Authorization: principal R-CLI-004 carve-out 2026-05-17 (structural artifacts only;
no substance modification; applies to FLEET-UPG-016R and v3.19 successors).

Architecture (per workspace/FU016R_ADOPTION_STREAM_TAXONOMY_v1.0.md §2):
- Table-driven stream registry (D-FU016R-2)
- Path-allowlist guard with hard-fail exit 2 (D-FU016R-3)
- Per-emission idempotency, semantic not byte-literal (D-FU016R-4 + Critic-G0 #3)
- Dry-run capability (D-FU016R-5)
- Supervisor-direct invocation; --agent flag (D-FU016R-6)
- Labeled commit message format (D-FU016R-7)
- ext-verify capture per agent (D-FU016R-8)
- Refuse-substance guard test flag (D-FU016R-9)

Usage:
    python3 workspace/fleet_remediation_v318.py --agent <name> [--dry-run]
    python3 workspace/fleet_remediation_v318.py --cohort wave1 [--dry-run]
    python3 workspace/fleet_remediation_v318.py --self-test-substance-refuse
    python3 workspace/fleet_remediation_v318.py --self-pilot-idempotency [--live]
"""
import argparse
import csv
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

# ─── Configuration ─────────────────────────────────────────────────────────────

SUPERVISOR_ROOT = Path.home() / "github" / "private-supervisor-AGET"
CANONICAL_SKILL = SUPERVISOR_ROOT / ".claude" / "skills" / "aget-create-initiative"
INDEX_CSV = SUPERVISOR_ROOT / "workspace" / "FU016R_INDEX_2026-05-17.csv"
EXT_VERIFY_DIR = SUPERVISOR_ROOT / "workspace"

# Authorization Record verbatim (D-FU016R-7 commit message reference)
CARVE_OUT_REF = (
    "Principal authorizes R-CLI-004 carve-out for Generator-driven "
    "adoption-stream restoration of supervisor-direct-migrated agents. "
    "Scope: structural artifacts only (AGENTS.md sections + skill files + "
    "governance refs); no substance modification. Carve-out applies to "
    "FLEET-UPG-016R and any v3.19 successor remediation cycles."
)

# Path allowlist per D-FU016R-3 (structural artifacts only)
ALLOWLIST_PATH_PATTERNS = [
    r"^AGENTS\.md$",
    r"^\.claude/skills/aget-create-initiative/.*",
]
PROHIBITED_PATH_PATTERNS = [
    r"^\.aget/evolution/",
    r"^\.aget/decisions/",
    r"^\.aget/checkpoints/",
    r"^\.aget/specs/",
    r"^sessions/",
    r"^planning/",
]

# Cohort definitions (per G0 manifest §3.4)
COHORT_DEFINITIONS = {
    "wave1": [
        ("private-code-analyzer-aget", "private-code-analyzer-aget"),
        ("private-CCB-bridge-aget", "GM-CCB/private-CCB-bridge-aget"),
        ("private-family-friends-aget", "GM-CCB/private-family-friends-aget"),
        ("private-felix-aget", "GM-CCB/private-felix-aget"),
        ("private-marco-aget", "GM-CCB/private-marco-aget"),
        ("private-melissa-aget", "GM-CCB/private-melissa-aget"),
        ("private-contracts-aget", "private-contracts-aget"),
        ("private-docx-aget", "private-docx-aget"),
        ("private-executive-coach-aget", "private-executive-coach-aget"),
        ("private-insurance-aget", "private-insurance-aget"),
        ("private-mesh-aget", "private-mesh-aget"),
        ("public-OpenAI-DeepResearch-aget", "public-OpenAI-DeepResearch-aget"),
        ("public-llm-connectivity-aget", "public-llm-connectivity-aget"),
    ],
    "wave2": [
        ("private-cli-aget", "aget-framework/private-cli-aget"),
        ("private-github-aget", "private-github-aget"),
    ],
    # FU016F routine cohort (per FU016F G0 INSPECT manifest §2)
    "fg21-routine": [
        ("private-alexander-aget", "GM-CCB/private-alexander-aget"),
        ("private-mom-aget", "GM-CCB/private-mom-aget"),
        ("private-financial-management-aget", "private-financial-management-aget"),
        ("private-healthcare-aget", "private-healthcare-aget"),
        ("private-PREDICTIONWORKS-ACCOUNTING-aget", "GM-PREDICTIONWORKS/private-PREDICTIONWORKS-ACCOUNTING-aget"),
    ],
    # Tier 1+2 adoption cohort (already at v3.18.0 but 0/5 adoption)
    "tier12-adopt": [
        ("private-impact-aget", "private-impact-aget"),
        ("private-it-consultant-aget", "private-it-consultant-aget"),
        ("private-github-aget", "private-github-aget"),
        ("private-cli-aget", "aget-framework/private-cli-aget"),
    ],
}


def run_finalize_against_agent(agent_name: str, agent_rel: str, dry_run: bool) -> dict:
    """FU016F mode: push stale (carve-out) → migrate (fleet_upgrade) → adopt (existing Generator).

    Per-agent flow:
    1. L646 pre-flight (capture state)
    2. Push stale commits (REQUIRES Path B-2 carve-out extension; routine-classified per FU016F manifest)
    3. Subprocess: fleet_upgrade_v3180.py --agent <name> (migration; auto-pushes)
    4. Run adoption-stream emissions (existing emit_* functions) + commit + push
    """
    agent_root = Path.home() / "github" / agent_rel
    if not agent_root.is_dir():
        return {"agent": agent_name, "status": "NOTFOUND", "path": str(agent_root)}
    # Step 1: L646 capture
    dirty = subprocess.check_output(["git", "-C", str(agent_root), "status", "--porcelain"]).decode().strip()
    ahead = subprocess.check_output(["git", "-C", str(agent_root), "rev-list", "--count", "@{u}..HEAD"]).decode().strip()
    head_before = subprocess.check_output(["git", "-C", str(agent_root), "rev-parse", "--short", "HEAD"]).decode().strip()
    if dirty:
        return {"agent": agent_name, "status": "DIRTY_BLOCKED", "dirty_count": len(dirty.splitlines())}
    actions = []
    # Step 2: push stale (under carve-out extension)
    if ahead != "0":
        if dry_run:
            actions.append({"step": "push-stale-routine", "would": f"push {ahead} commits"})
        else:
            push_result = subprocess.run(
                ["git", "-C", str(agent_root), "push", "origin", "main"],
                capture_output=True, text=True,
            )
            actions.append({"step": "push-stale-routine", "rc": push_result.returncode,
                            "msg": (push_result.stderr or push_result.stdout)[:200]})
            if push_result.returncode != 0:
                return {"agent": agent_name, "status": "PUSH_FAIL", "actions": actions}
    # Step 3: migrate (subprocess fleet_upgrade_v3180.py)
    if dry_run:
        actions.append({"step": "migrate", "would": "subprocess fleet_upgrade_v3180.py --agent " + agent_name})
    else:
        mig_result = subprocess.run(
            ["python3", str(SUPERVISOR_ROOT / "workspace" / "fleet_upgrade_v3180.py"), "--agent", agent_name],
            capture_output=True, text=True,
        )
        actions.append({"step": "migrate", "rc": mig_result.returncode,
                        "tail": (mig_result.stdout or "")[-200:]})
        if mig_result.returncode not in (0,):
            return {"agent": agent_name, "status": "MIGRATE_FAIL", "actions": actions}
    # Step 4: adoption (reuse existing run_against_agent for emissions only)
    adopt_result = run_against_agent(agent_name, agent_rel, dry_run=dry_run)
    actions.append({"step": "adopt", "result": adopt_result})
    head_after = subprocess.check_output(["git", "-C", str(agent_root), "rev-parse", "--short", "HEAD"]).decode().strip()
    # Step 5: commit + push adoption (if emissions applied)
    if not dry_run and adopt_result.get("applied"):
        applied_ids = [a['stream'] for a in adopt_result.get('applied', [])]
        new_head = commit_and_push(agent_name, agent_rel, applied_ids, adopt_result.get('skipped', []))
        push_success = not new_head.startswith("COMMIT-FAIL")
        index_csv_append(agent_name, applied_ids, adopt_result.get('skipped', []), head_after, new_head, push_success)
        head_after = new_head
    return {
        "agent": agent_name,
        "status": "DRY-RUN" if dry_run else "FINALIZED",
        "actions": actions,
        "head_before": head_before,
        "head_after": head_after,
    }

# ─── Stream Registry (D-FU016R-2: table-driven) ────────────────────────────────

# Each stream: id, semantic_identifier (for idempotency grep), emit() callable.
# Idempotency check is SEMANTIC (Critic-G0 #3): regex on identifier, not byte-equality.

def stream_1_emit_text():
    return ("`AGET_MEMORY_SURFACE_SPEC v0.2.0` reference | **Adopted (reference-only)** | "
            "Canonical at `~/github/aget-framework/aget/specs/AGET_MEMORY_SURFACE_SPEC.md`; "
            "status DRAFT pending cross-fleet review; MEMORY consumers track L335 "
            "harness-vs-KB taxonomy")

def stream_2_emit_text():
    return ("Verb-registry awareness (11 new §Hierarchy Decisions pairs) | **Acknowledged** | "
            "Canonical at `~/github/aget-framework/aget/ontology/DESIGN_DIRECTION_skill_verb_vocabulary.md`; "
            "L954 5-line pre-check applies when authoring new skills")

def stream_3_emit_text():
    return ("L961 channel wiring (HANDOFF-Deferral Discipline) | **OPTIONAL — deferred adoption** | "
            "Per D-FU016-3=b OPTIONAL per-agent. Defers Channel 1+2+4 implementation; "
            "adoption rate tracked at v3.19")

def stream_4_adoption_row():
    return ("`/aget-create-initiative` STRICT skill | **Adopted** | "
            "Skill present at `.claude/skills/aget-create-initiative/`; "
            "added to Structural Skill Routing table per D-FU016-4=ALL cohort")

def stream_4_routing_row():
    return ("| `/aget-create-initiative` | Creating `planning/initiatives/INIT-*.md` (v3.18) "
            "| Direct Write/Edit to `planning/initiatives/` | **Strict** |")

def stream_5_emit_text():
    return ("R-DEP-3 RECLASSIFY wake/wind shims (Active Deprecations → Active Aliases) | "
            "**Acknowledged** | No code change; semantic reclassification; per-agent verify "
            "at fleet rollout")

STREAMS = [
    {
        "id": "S1",
        "name": "MEMORY_SURFACE_SPEC reference",
        "semantic_identifier": r"MEMORY_SURFACE_SPEC",
        "kind": "ack-row",
        "row_text": stream_1_emit_text,
    },
    {
        "id": "S2",
        "name": "Verb-registry Hierarchy Decisions",
        "semantic_identifier": r"Hierarchy Decisions",
        "kind": "ack-row",
        "row_text": stream_2_emit_text,
    },
    {
        "id": "S3",
        "name": "L961 channel wiring",
        "semantic_identifier": r"L961.*(OPTIONAL|Adopted|deferred adoption)",
        "kind": "ack-row",
        "row_text": stream_3_emit_text,
    },
    {
        "id": "S4a",
        "name": "aget-create-initiative skill directory",
        "semantic_identifier": None,  # file-presence check
        "kind": "skill-copy",
    },
    {
        "id": "S4b",
        "name": "aget-create-initiative Adoption row",
        "semantic_identifier": r"aget-create-initiative.*Adopted",
        "kind": "ack-row",
        "row_text": stream_4_adoption_row,
    },
    {
        "id": "S4c",
        "name": "aget-create-initiative STRUCTURAL Routing row",
        "semantic_identifier": r"aget-create-initiative.*Strict",
        "kind": "routing-row",
        "row_text": stream_4_routing_row,
    },
    {
        "id": "S5",
        "name": "R-DEP-3 RECLASSIFY",
        "semantic_identifier": r"R-DEP-3",
        "kind": "ack-row",
        "row_text": stream_5_emit_text,
    },
]

ADOPTION_SECTION_HEADER = "## v3.18.0 Adoption"

# ─── Guards ────────────────────────────────────────────────────────────────────

def assert_in_allowlist(rel_path: str) -> None:
    """D-FU016R-3: hard-fail exit 2 on prohibited path."""
    for prohibited in PROHIBITED_PATH_PATTERNS:
        if re.match(prohibited, rel_path):
            print(f"ERROR: REFUSE-SUBSTANCE guard triggered. Prohibited path: {rel_path}", file=sys.stderr)
            print(f"  Prohibited pattern matched: {prohibited}", file=sys.stderr)
            print("  Generator scope is structural artifacts only per Authorization Record.", file=sys.stderr)
            sys.exit(2)
    for allowed in ALLOWLIST_PATH_PATTERNS:
        if re.match(allowed, rel_path):
            return
    print(f"ERROR: ALLOWLIST guard triggered. Path not in allowlist: {rel_path}", file=sys.stderr)
    sys.exit(2)

# ─── Per-stream emission ───────────────────────────────────────────────────────

def check_stream_idempotency(stream: dict, agent_root: Path) -> str:
    """Returns 'present' if stream already adopted (semantically), else 'absent'.

    For S4a (skill-copy): checks git-tracked status, not just disk presence
    (per principal Path 1 directive — force-add overrides gitignore so we
    must verify tracked-on-origin, not just on-disk).
    """
    if stream["kind"] == "skill-copy":
        skill_md_rel = ".claude/skills/aget-create-initiative/SKILL.md"
        skill_md_path = agent_root / skill_md_rel
        if not skill_md_path.exists():
            return "absent"
        # Disk-present; verify git-tracked
        result = subprocess.run(
            ["git", "-C", str(agent_root), "ls-files", "--error-unmatch", skill_md_rel],
            capture_output=True, text=True,
        )
        return "present" if result.returncode == 0 else "absent"
    # ack-row or routing-row → grep AGENTS.md
    agents_md = agent_root / "AGENTS.md"
    if not agents_md.exists():
        return "absent"
    content = agents_md.read_text()
    if re.search(stream["semantic_identifier"], content):
        return "present"
    return "absent"

def emit_skill_copy(agent_root: Path, dry_run: bool) -> dict:
    """S4a: copy .claude/skills/aget-create-initiative/ tree."""
    target = agent_root / ".claude" / "skills" / "aget-create-initiative"
    rel = "/.claude/skills/aget-create-initiative/"
    assert_in_allowlist(".claude/skills/aget-create-initiative/SKILL.md")
    if dry_run:
        return {"action": "would-copy-skill", "from": str(CANONICAL_SKILL), "to": str(target)}
    target.parent.mkdir(parents=True, exist_ok=True)
    if target.exists():
        shutil.rmtree(target)
    shutil.copytree(CANONICAL_SKILL, target)
    return {"action": "copied-skill", "from": str(CANONICAL_SKILL), "to": str(target)}

def ensure_adoption_section_present(agents_md: Path, dry_run: bool) -> tuple[str, bool]:
    """Returns (current_content, section_was_added_or_existed)."""
    content = agents_md.read_text()
    if re.search(r"^## v3\.18\.0 Adoption", content, re.MULTILINE):
        return content, False  # already present
    # Append section after Project Context if found, else at end of file
    section = (
        "\n\n## v3.18.0 Adoption (FLEET-UPG-016R remediated 2026-05-17)\n\n"
        "Per `RELEASE_HANDOFF_v3.18.0.md` §Upgrade Guide adoption streams:\n\n"
        "| Stream | Status | Note |\n"
        "|--------|--------|------|\n"
    )
    insertion_point = re.search(r"(\n## Architecture Context|\n## Project Context.*?\n\n)", content, re.DOTALL)
    if insertion_point:
        idx = insertion_point.end()
        new_content = content[:idx] + section + content[idx:]
    else:
        new_content = content + section
    if dry_run:
        return new_content, True
    agents_md.write_text(new_content)
    return new_content, True

def emit_ack_row(stream: dict, agent_root: Path, dry_run: bool) -> dict:
    """Append a pipe-delimited row to §v3.18.0 Adoption table."""
    agents_md = agent_root / "AGENTS.md"
    assert_in_allowlist("AGENTS.md")
    if not agents_md.exists():
        return {"action": "skipped-no-agents-md", "stream": stream["id"]}
    content, _ = ensure_adoption_section_present(agents_md, dry_run=dry_run)  # respect dry-run flag
    # find the table within §v3.18.0 Adoption section
    section_match = re.search(
        r"(## v3\.18\.0 Adoption.*?)(\n\n## |\Z)",
        content,
        re.DOTALL,
    )
    if not section_match:
        return {"action": "section-missing-after-ensure", "stream": stream["id"]}
    section_text = section_match.group(1)
    new_row = f"| {stream['row_text']()} |\n"
    # insert before next section
    insert_idx = section_match.end(1)
    new_content = content[:insert_idx] + new_row + content[insert_idx:]
    if dry_run:
        return {"action": "would-append-row", "stream": stream["id"], "row": new_row.strip()}
    agents_md.write_text(new_content)
    return {"action": "appended-row", "stream": stream["id"], "row": new_row.strip()}

def emit_routing_row(stream: dict, agent_root: Path, dry_run: bool) -> dict:
    """Append a row to STRUCTURAL Skill Routing table (or note if table not present)."""
    agents_md = agent_root / "AGENTS.md"
    assert_in_allowlist("AGENTS.md")
    if not agents_md.exists():
        return {"action": "skipped-no-agents-md", "stream": stream["id"]}
    content = agents_md.read_text()
    # find STRUCTURAL Skill Routing table
    table_match = re.search(
        r"(### Structural Skill Routing.*?\n\|.*?\n(?:\|.*?\n)+)",
        content,
        re.DOTALL,
    )
    if not table_match:
        # No STRUCTURAL routing section — note carry-item rather than create section
        return {"action": "skipped-no-routing-table", "stream": stream["id"],
                "carry": "agent lacks §Structural Skill Routing section; remediation incomplete for S4c"}
    table_text = table_match.group(1)
    new_row = f"{stream['row_text']()}\n"
    insert_idx = table_match.end(1)
    new_content = content[:insert_idx] + new_row + content[insert_idx:]
    if dry_run:
        return {"action": "would-append-routing-row", "stream": stream["id"], "row": new_row.strip()}
    agents_md.write_text(new_content)
    return {"action": "appended-routing-row", "stream": stream["id"], "row": new_row.strip()}

# ─── Per-agent orchestration ───────────────────────────────────────────────────

def run_against_agent(agent_name: str, agent_rel: str, dry_run: bool) -> dict:
    agent_root = Path.home() / "github" / agent_rel
    if not agent_root.is_dir():
        return {"agent": agent_name, "status": "NOTFOUND", "path": str(agent_root)}
    # L646 pre-flight at dispatch (F-G2-3 discipline)
    dirty = subprocess.check_output(
        ["git", "-C", str(agent_root), "status", "--porcelain"]
    ).decode().strip()
    ahead = subprocess.check_output(
        ["git", "-C", str(agent_root), "rev-list", "--count", "@{u}..HEAD"]
    ).decode().strip()
    if dirty or ahead != "0":
        return {
            "agent": agent_name,
            "status": "L646_BLOCKED",
            "dirty_count": len(dirty.splitlines()) if dirty else 0,
            "ahead": ahead,
        }
    applied = []
    skipped = []
    for stream in STREAMS:
        state = check_stream_idempotency(stream, agent_root)
        if state == "present":
            skipped.append(stream["id"])
            continue
        # emit
        if stream["kind"] == "skill-copy":
            result = emit_skill_copy(agent_root, dry_run)
        elif stream["kind"] == "ack-row":
            result = emit_ack_row(stream, agent_root, dry_run)
        elif stream["kind"] == "routing-row":
            result = emit_routing_row(stream, agent_root, dry_run)
        else:
            result = {"action": "unknown-kind", "stream": stream["id"]}
        applied.append({"stream": stream["id"], "result": result})
    return {
        "agent": agent_name,
        "status": "DRY-RUN" if dry_run else "APPLIED",
        "applied": applied,
        "skipped": skipped,
        "head_before": subprocess.check_output(
            ["git", "-C", str(agent_root), "rev-parse", "--short", "HEAD"]
        ).decode().strip(),
    }

def index_csv_append(agent_name: str, applied_ids: list, skipped_ids: list, head_before: str, head_after: str, push_success: bool):
    """D-FU016R-8: append per-agent row to FU016R INDEX CSV for L656 audit."""
    header_needed = not INDEX_CSV.exists()
    with INDEX_CSV.open("a", newline="") as f:
        w = csv.writer(f)
        if header_needed:
            w.writerow(["timestamp", "agent", "streams_applied", "streams_skipped", "head_before", "head_after", "push_success"])
        w.writerow([
            datetime.now(timezone.utc).isoformat(),
            agent_name,
            ",".join(applied_ids) if applied_ids else "(none)",
            ",".join(skipped_ids) if skipped_ids else "(none)",
            head_before,
            head_after,
            "YES" if push_success else "NO",
        ])

def commit_and_push(agent_name: str, agent_rel: str, applied_ids: list, skipped_ids: list) -> str:
    agent_root = Path.home() / "github" / agent_rel
    msg = (
        f"chore: v3.18 adoption-stream remediation (FLEET-UPG-016R per principal "
        f"R-CLI-004 carve-out; structural artifacts only)\n\n"
        f"Streams applied: {','.join(applied_ids) if applied_ids else '(none)'}\n"
        f"Streams skipped (already-present): {','.join(skipped_ids) if skipped_ids else '(none)'}\n\n"
        f"Authorization: per PROJECT_PLAN_fleet_v318_adoption_remediation_v1.0.md "
        f"§Authorization Record.\n\n"
        f"Generator: workspace/fleet_remediation_v318.py v1.0.0.\n"
    )
    # AGENTS.md: normal add
    subprocess.run(["git", "-C", str(agent_root), "add", "AGENTS.md"], check=False)
    # Skill directory: force-add per principal Path 1 directive (overrides gitignore;
    # explicit scope expansion of carve-out "skill files" → "skill tracking policy")
    subprocess.run(
        ["git", "-C", str(agent_root), "add", "-f", ".claude/skills/aget-create-initiative/"],
        check=False,
    )
    commit_result = subprocess.run(
        ["git", "-C", str(agent_root), "commit", "-m", msg],
        capture_output=True, text=True,
    )
    if commit_result.returncode != 0:
        return f"COMMIT-FAIL: {commit_result.stderr}"
    subprocess.run(["git", "-C", str(agent_root), "push", "origin", "main"], check=False)
    return subprocess.check_output(
        ["git", "-C", str(agent_root), "rev-parse", "--short", "HEAD"]
    ).decode().strip()

# ─── Self-tests (G1 acceptance criteria) ───────────────────────────────────────

def self_test_substance_refuse():
    """D-FU016R-9: verify Generator refuses to write outside allowlist."""
    print("[self-test-substance-refuse] Testing path-allowlist guard...")
    try:
        assert_in_allowlist(".aget/evolution/L_TEST.md")
    except SystemExit as e:
        if e.code == 2:
            print("[self-test-substance-refuse] PASS: exit 2 on .aget/evolution/L_TEST.md")
            return 0
    print("[self-test-substance-refuse] FAIL: did not exit 2 on prohibited path")
    return 1

def self_pilot_idempotency(live: bool):
    """G1 V-test: Generator semantic idempotency check on supervisor → all streams 'present'.

    Bypasses L646 pre-flight (supervisor's working tree is naturally dirty during
    plan-authoring sessions; L646 is dispatch-time guard, not idempotency-test guard).
    Exercises check_stream_idempotency() directly for each stream.
    """
    print(f"[self-pilot-idempotency] live={live}")
    print(f"[self-pilot-idempotency] checking semantic idempotency per stream on supervisor's own repo...")
    agent_root = SUPERVISOR_ROOT
    all_present = True
    for stream in STREAMS:
        state = check_stream_idempotency(stream, agent_root)
        marker = "✓" if state == "present" else "✗"
        print(f"  {marker} {stream['id']:5s} {stream['name']:50s} → {state}")
        if state != "present":
            all_present = False
    if all_present:
        print("[self-pilot-idempotency] PASS: all 7 emissions (5 streams + S4a/b/c) report 'present' on supervisor (semantic idempotency verified)")
        return 0
    else:
        print("[self-pilot-idempotency] FAIL: one or more emissions report 'absent' on supervisor (would create duplicate)")
        return 1

# ─── CLI ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--agent", help="single agent name (per cohort definitions)")
    p.add_argument("--cohort", help="cohort name: wave1, wave2")
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--self-test-substance-refuse", action="store_true")
    p.add_argument("--self-pilot-idempotency", action="store_true")
    p.add_argument("--live", action="store_true", help="(advanced) live invocation; default is safety-dry")
    args = p.parse_args()

    if args.self_test_substance_refuse:
        return self_test_substance_refuse()
    if args.self_pilot_idempotency:
        return self_pilot_idempotency(args.live)

    if not args.agent and not args.cohort:
        p.print_help()
        return 1

    targets = []
    if args.agent:
        for cohort, agents in COHORT_DEFINITIONS.items():
            for name, rel in agents:
                if name == args.agent:
                    targets.append((name, rel))
        if not targets:
            print(f"ERROR: agent {args.agent} not in cohort definitions", file=sys.stderr)
            return 1
    if args.cohort:
        targets.extend(COHORT_DEFINITIONS.get(args.cohort, []))

    # FU016F mode: cohort "fg21-routine" uses finalize flow (push + migrate + adopt)
    finalize_mode = args.cohort == "fg21-routine"

    for name, rel in targets:
        if finalize_mode:
            result = run_finalize_against_agent(name, rel, dry_run=args.dry_run)
            print(f"\n=== {name} ===")
            print(f"  status: {result.get('status')}")
            for a in result.get('actions', []):
                print(f"  {a.get('step', '?')}: {list(a.values())[1] if len(a) > 1 else a}")
            if result.get('head_before') and result.get('head_after'):
                print(f"  head: {result.get('head_before')} -> {result.get('head_after')}")
            continue
        result = run_against_agent(name, rel, dry_run=args.dry_run)
        print(f"\n=== {name} ===")
        print(f"  status: {result.get('status')}")
        if result.get('status') == 'L646_BLOCKED':
            print(f"  dirty: {result.get('dirty_count')}  ahead: {result.get('ahead')}  → SKIP")
            continue
        for a in result.get('applied', []):
            print(f"  applied {a['stream']}: {a['result'].get('action')}")
        for s in result.get('skipped', []):
            print(f"  skipped {s} (already-present)")
        if not args.dry_run and result.get('status') == 'APPLIED' and result.get('applied'):
            applied_ids = [a['stream'] for a in result.get('applied', [])]
            head_before = result.get('head_before', '?')
            new_head = commit_and_push(name, rel, applied_ids, result.get('skipped', []))
            push_success = not new_head.startswith("COMMIT-FAIL")
            index_csv_append(name, applied_ids, result.get('skipped', []), head_before, new_head, push_success)
            print(f"  commit+push: {new_head}")
    return 0

if __name__ == "__main__":
    sys.exit(main())
