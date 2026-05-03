#!/usr/bin/env python3
"""
verify_deployment.py — Version-parameterized deployment verification.

Verifies an AGET agent is correctly deployed at a given version by checking
version indicators, required directories, governance fields, terminology,
skills, and session scripts.

Usage:
    python3 scripts/verify_deployment.py --version 3.11.0
    python3 scripts/verify_deployment.py --version 3.11.0 --path /path/to/agent
    python3 scripts/verify_deployment.py --version 3.11.0 --json

Governance:
    R-REL-038 (Deployment Spec Required)
    L754 (Deployment Verification Script Gap)
    REQ-REL-F-007 (Deployment Verification Tooling)

History:
    v1.0.0 (2026-03-28): Initial creation during DVF-001. 8 check categories.
    v1.1.0 (2026-03-28): Framework core auto-detection. Self-exclusion from
        terminology scan. Fixed manifest.yaml regex for YAML comments.
    v1.2.0 (2026-03-28): Fixed false positives from supervisor FLEET-UPG-009 G1:
        manifest.yaml comment format, migration_history object format.
        Skill count corrected 16 -> 18. History/motivation docstring added.
    v1.3.0 (2026-05-02): v3.16-aware enhancement (release-completeness fix).
        Reads DEPLOYMENT_SPEC_v{version}.yaml dynamically. Spec-derived universal
        skill list replaces hardcoded 18-skill list (which was 11 behind the
        29-count CAP-TPL-016-04 mandate). Adds checks for archetype-conditional
        release-triad placement (CAP-TPL-016-07), optional v3.16 adoptions
        (/aget-go SKILL-048, .agetignore CAP-SEC-007, Plan_Status CAP-PP-003
        template), and sleeping CAPs disclosure (R-DEP-010). Falls back to
        legacy hardcoded check for pre-v3.16 versions or when spec absent.
    v1.3.1 (2026-05-02): Asymmetric-fallback fix surfaced by supervisor test.
        derive_universal_skills_from_baseline now tries the same home-fallback
        path that load_deployment_spec uses (~/github/aget-framework/...), so
        agents outside the aget-framework checkout (e.g., supervisor in its
        own git tree) get spec-derived 29-skill verification instead of silent
        fallback to legacy 18-skill check. Fallback WARN is now preserved
        (prepended to legacy results) so users know the verification surface
        is incomplete when baseline is unreachable.

Motivation:
    DEPLOYMENT_SPEC_v3.10.0 included verify_v3.10.0.sh (100+ lines, 7 check
    categories). DEPLOYMENT_SPEC_v3.11.0 was created without a verification
    script. The supervisor's fleet migration (FLEET-UPG-009) needed verification
    tooling at Gate 2 and it didn't exist. L754 captures the root cause:
    "A state description without verification tooling is a wish, not a spec."

    Three pilot self-reports (supervisor, impact-aget, cli-aget) all improvised
    ad hoc bash verification - proving the tool's necessity. The supervisor's
    analysis showed agents diagnose against wrong criteria without this script
    because they lack DEPLOYMENT_SPEC context to distinguish "required for all"
    from "required for release-managing only" from "scaffold only (future use)".

    v1.3.0 (2026-05-02) addresses the v3.16 instance of the same pattern.
    DEPLOYMENT_SPEC_v3.16.0.yaml line 29 explicitly disclosed "inherits: v3.15.0
    verification surface (no v3.16-specific checks added)" — meaning self-migrating
    agents had no automated verification of v3.16-specific changes (universal-skill
    32 -> 29 reconciliation, archetype-conditional release-triad placement,
    /aget-go primitive, .agetignore skeleton, Plan_Status template rename,
    sleeping CAPs). The script returned "OK" for v3.5-era agents passing
    --version 3.16.0 because it was behaviorally version-blind. v1.3.0 makes
    it version-aware via dynamic spec loading. Closes the gap surfaced by
    the principal 2026-05-02 ("how are agents supposed to verify
    self-migrations beyond manually?").

Exit Codes:
    0: All checks PASS (or PASS with warnings)
    1: One or more checks FAIL
"""

import argparse
import json
import re
import sys
from pathlib import Path

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


# ============================================================================
# v3.16+ helpers (spec-driven verification)
# ============================================================================

def _version_ge(a, b):
    """Compare semver strings; return True if a >= b. Falls back to False on parse error."""
    try:
        a_parts = [int(p) for p in a.split('.')[:3]]
        b_parts = [int(p) for p in b.split('.')[:3]]
        while len(a_parts) < 3:
            a_parts.append(0)
        while len(b_parts) < 3:
            b_parts.append(0)
        return a_parts >= b_parts
    except (ValueError, AttributeError):
        return False


def find_aget_root_from_agent(agent_path):
    """Walk up from agent_path to find an aget-framework checkout root.

    Identified by the conjunction of (a) aget/specs/ directory AND (b) at least
    one template-*-aget sibling. The template-sibling check disambiguates from
    a private agent's own aget/ drafts directory (which lacks template siblings).
    Returns Path or None.
    """
    cur = agent_path
    template_indicators = ["template-worker-aget", "template-supervisor-aget", "template-advisor-aget"]
    for _ in range(6):
        has_specs = (cur / "aget" / "specs").is_dir()
        has_templates = any((cur / t).is_dir() for t in template_indicators)
        if has_specs and has_templates:
            return cur
        if cur.parent == cur:
            break
        cur = cur.parent
    return None


def load_deployment_spec(version, agent_path, framework_root):
    """Load DEPLOYMENT_SPEC_v{version}.yaml from canonical aget/ path.
    Returns (spec_dict, path) or (None, None)."""
    if not YAML_AVAILABLE:
        return None, None
    candidates = []
    if framework_root:
        candidates.append(framework_root / "aget" / f"DEPLOYMENT_SPEC_v{version}.yaml")
    candidates.append(agent_path / "aget" / f"DEPLOYMENT_SPEC_v{version}.yaml")
    candidates.append(Path.home() / "github" / "aget-framework" / "aget" / f"DEPLOYMENT_SPEC_v{version}.yaml")
    seen = set()
    for p in candidates:
        if p in seen:
            continue
        seen.add(p)
        if p.exists():
            try:
                with open(p) as f:
                    return yaml.safe_load(f), p
            except (yaml.YAMLError, OSError):
                continue
    return None, None


def derive_universal_skills_from_baseline(framework_root):
    """Derive canonical universal-skill list from template-worker-aget baseline.

    Excludes worker-archetype skills (aget-execute-task, aget-track-deliverable)
    and release-execution-archetype extras (release-triad). Per CAP-TPL-016-04
    the v3.16 universal-skill count is 29, with release-triad moved to
    archetype-specific per CAP-TPL-016-07.

    Tries candidate paths in order:
      1. framework_root / template-worker-aget / .claude / skills (when found via walk-up)
      2. ~/github/aget-framework/template-worker-aget/.claude/skills (home fallback;
         supports agents outside the aget-framework checkout, e.g., supervisor in
         its own git tree)

    Returns sorted list of skill names, or None if no baseline reachable.
    """
    candidates = []
    if framework_root is not None:
        candidates.append(framework_root / "template-worker-aget" / ".claude" / "skills")
    candidates.append(Path.home() / "github" / "aget-framework" / "template-worker-aget" / ".claude" / "skills")
    baseline_dir = next((c for c in candidates if c.is_dir()), None)
    if baseline_dir is None:
        return None
    archetype_specific = {
        "aget-execute-task", "aget-track-deliverable",
        "aget-release-build", "aget-release-audit-specs", "aget-release-critique",
    }
    skills = []
    for d in sorted(baseline_dir.iterdir()):
        if d.is_dir() and (d / "SKILL.md").exists() and d.name not in archetype_specific:
            skills.append(d.name)
    return skills if skills else None


def _read_archetype(agent_path):
    """Read agent archetype from .aget/identity.json. Returns lowercase
    canonicalized archetype or None.

    Per gmelli/aget-aget#1200: archetype is OPTIONAL with vocabulary mismatch
    across IDENTITY_JSON_SCHEMA / IDENTITY_SPEC / DEPLOYMENT_SPEC. Many agents
    lack the field entirely; some carry capitalized non-canonical values."""
    identity_path = agent_path / ".aget" / "identity.json"
    if not identity_path.exists():
        return None
    try:
        with open(identity_path) as f:
            data = json.load(f)
    except (json.JSONDecodeError, OSError):
        return None
    arch_field = data.get("archetype")
    if not arch_field:
        dims = data.get("identity_dimensions") or {}
        if isinstance(dims, dict):
            arch_field = dims.get("archetype")
    if not isinstance(arch_field, str):
        return None
    return arch_field.lower().replace("_", "-").strip()


def check_version_indicators(agent_path, version, is_framework=False):
    results = []
    vj_path = agent_path / ".aget" / "version.json"
    if vj_path.exists():
        try:
            with open(vj_path) as f:
                data = json.load(f)
            actual = data.get("aget_version", "MISSING")
            if actual == version:
                results.append(("OK", f"version.json: {actual}"))
            else:
                results.append(("FAIL", f"version.json: {actual} (expected {version})"))
        except (json.JSONDecodeError, KeyError) as e:
            results.append(("FAIL", f"version.json: parse error - {e}"))
    else:
        results.append(("FAIL", "version.json: file not found"))

    if is_framework:
        results.append(("OK", "AGENTS.md: N/A (framework core)"))
    elif (agent_path / "AGENTS.md").exists():
        content = (agent_path / "AGENTS.md").read_text()
        match = re.search(r"@aget-version:\s*(\S+)", content)
        if match:
            actual = match.group(1)
            if actual == version:
                results.append(("OK", f"AGENTS.md: {actual}"))
            else:
                results.append(("FAIL", f"AGENTS.md: {actual} (expected {version})"))
        else:
            results.append(("FAIL", "AGENTS.md: @aget-version line not found"))
    else:
        results.append(("FAIL", "AGENTS.md: file not found"))

    manifest_path = agent_path / "manifest.yaml"
    if manifest_path.exists():
        content = manifest_path.read_text()
        match = re.search(r"^version:\s*[\"']?([0-9]+\.[0-9]+\.[0-9]+)[\"']?", content, re.MULTILINE)
        if match:
            actual = match.group(1)
            if actual == version:
                results.append(("OK", f"manifest.yaml: {actual}"))
            else:
                results.append(("FAIL", f"manifest.yaml: {actual} (expected {version})"))
        else:
            results.append(("WARN", "manifest.yaml: version field not found"))
    else:
        results.append(("WARN", "manifest.yaml: file not found"))
    return results


def check_migration_history(agent_path, version):
    results = []
    vj_path = agent_path / ".aget" / "version.json"
    if vj_path.exists():
        try:
            with open(vj_path) as f:
                data = json.load(f)
            history = data.get("migration_history", [])
            has_version = any(
                version in (str(entry) if isinstance(entry, str) else json.dumps(entry))
                for entry in history
            )
            if has_version:
                results.append(("OK", f"migration_history: includes {version}"))
            else:
                results.append(("WARN", f"migration_history: missing {version} entry"))
        except (json.JSONDecodeError, KeyError):
            results.append(("WARN", "migration_history: parse error"))
    return results


def check_required_directories(agent_path):
    results = []
    req_dir = agent_path / "requirements"
    if req_dir.is_dir():
        results.append(("OK", "requirements/ directory exists"))
    else:
        agent_name = agent_path.name
        if "template-" in agent_name or agent_name == "aget":
            results.append(("FAIL", "requirements/ directory MISSING"))
        else:
            results.append(("WARN", "requirements/ directory missing (optional for private agents)"))

    hooks_dir = agent_path / ".claude" / "hooks"
    if hooks_dir.is_dir():
        results.append(("OK", ".claude/hooks/ directory exists"))
        if (hooks_dir / "README.md").exists():
            results.append(("OK", ".claude/hooks/README.md exists"))
        else:
            results.append(("WARN", ".claude/hooks/README.md missing"))
    else:
        results.append(("FAIL", ".claude/hooks/ directory MISSING"))
    return results


def check_governance_intensity(agent_path):
    results = []
    agents_path = agent_path / "AGENTS.md"
    if agents_path.exists():
        content = agents_path.read_text()
        if re.search(r"governance.intensity|Governance Intensity", content, re.IGNORECASE):
            results.append(("OK", "governance_intensity field present"))
        else:
            results.append(("FAIL", "governance_intensity field MISSING in AGENTS.md"))
    return results


def check_terminology(agent_path):
    results = []
    count = 0
    files_with = []
    for check_file in ["AGENTS.md", "CLAUDE.md"]:
        fpath = agent_path / check_file
        if fpath.exists():
            content = fpath.read_text()
            matches = len(re.findall(r"sanity.check", content, re.IGNORECASE))
            if matches:
                count += matches
                files_with.append(check_file)
    scripts_dir = agent_path / "scripts"
    if scripts_dir.is_dir():
        for py_file in scripts_dir.glob("*.py"):
            if py_file.name == "verify_deployment.py":
                continue
            try:
                content = py_file.read_text()
            except (OSError, FileNotFoundError):
                # Broken symlink or unreadable file; skip silently
                continue
            matches = len(re.findall(r"sanity.check", content, re.IGNORECASE))
            if matches:
                count += matches
                files_with.append(py_file.name)
    if count == 0:
        results.append(("OK", "terminology: 0 'sanity check' in operational files"))
    else:
        results.append(("WARN", f"terminology: {count} 'sanity check' in {', '.join(files_with)}"))
    return results


def check_universal_skills(agent_path):
    results = []
    skills_dir = agent_path / ".claude" / "skills"
    if not skills_dir.is_dir():
        results.append(("FAIL", "skills: .claude/skills/ directory not found"))
        return results
    UNIVERSAL = [
        "aget-wake-up", "aget-wind-down", "aget-study-topic",
        "aget-check-health", "aget-check-kb", "aget-check-evolution",
        "aget-check-sessions", "aget-create-project", "aget-review-project",
        "aget-save-state", "aget-record-lesson", "aget-record-observation",
        "aget-file-issue", "aget-propose-skill", "aget-enhance-spec",
        "aget-create-skill", "aget-analyze-ontology", "aget-expand-ontology",
    ]
    missing = []
    for skill in UNIVERSAL:
        if not (skills_dir / skill).is_dir():
            missing.append(skill)
    if not missing:
        results.append(("OK", f"skills: all {len(UNIVERSAL)} universal skills present"))
    else:
        results.append(("FAIL", f"skills: {len(missing)} missing - {', '.join(missing[:3])}{'...' if len(missing) > 3 else ''}"))
    RETIRED = ["aget-capture-observation", "aget-capture-nugget", "aget-study-up"]
    for old_name in RETIRED:
        if (skills_dir / old_name).is_dir():
            results.append(("WARN", f"skills: retired name '{old_name}' still exists"))
    return results


def check_session_scripts(agent_path):
    results = []
    scripts_dir = agent_path / "scripts"
    REQUIRED = ["wake_up.py", "wind_down.py", "study_topic.py", "health_check.py"]
    for script in REQUIRED:
        if (scripts_dir / script).exists():
            results.append(("OK", f"scripts/{script}"))
        elif (agent_path / ".aget" / "patterns" / "session" / script).exists():
            results.append(("WARN", f"{script}: at deprecated path (.aget/patterns/session/)"))
        else:
            results.append(("WARN", f"{script}: not found"))
    return results


def check_structural_enforcement(agent_path):
    results = []
    agents_path = agent_path / "AGENTS.md"
    if not agents_path.exists():
        return results
    content = agents_path.read_text()
    checks = [
        ("Governed Project Creation", "MUST-invoke /aget-create-project"),
        ("Structural Skill Routing", "D71 routing table"),
        ("Governance Bypass Detection", "D71 bypass detection"),
    ]
    for section, desc in checks:
        if section in content:
            results.append(("OK", f"D71: {desc}"))
        else:
            results.append(("WARN", f"D71: {desc} section MISSING"))
    return results


# ============================================================================
# v3.16+ check functions (spec-driven)
# ============================================================================

def check_universal_skills_v316(agent_path, framework_root):
    """v3.16+ : spec-derived universal skill list from template-worker-aget baseline."""
    results = []
    skills_dir = agent_path / ".claude" / "skills"
    if not skills_dir.is_dir():
        results.append(("FAIL", "skills: .claude/skills/ directory not found"))
        return results
    spec_skills = derive_universal_skills_from_baseline(framework_root)
    if not spec_skills:
        legacy_results = check_universal_skills(agent_path)
        return [("WARN", "skills: cannot locate template-worker-aget baseline (tried framework_root + ~/github/aget-framework); falling back to legacy 18-skill hardcoded check — verification is INCOMPLETE for v3.16+ skill mandate")] + legacy_results
    spec_count = len(spec_skills)
    missing = [s for s in spec_skills if not (skills_dir / s).is_dir()]
    if not missing:
        results.append(("OK", f"skills: all {spec_count} universal skills present (spec-derived from template-worker-aget baseline)"))
    else:
        msg = f"skills: {len(missing)}/{spec_count} missing - {', '.join(missing[:5])}"
        if len(missing) > 5:
            msg += f" + {len(missing) - 5} more"
        results.append(("FAIL", msg))
    RETIRED = ["aget-capture-observation", "aget-capture-nugget", "aget-study-up"]
    for old_name in RETIRED:
        if (skills_dir / old_name).is_dir():
            results.append(("WARN", f"skills: retired name '{old_name}' still exists"))
    return results


def check_archetype_action(agent_path, spec):
    """v3.16+ CAP-TPL-016-07: archetype-conditional release-triad placement."""
    results = []
    if not spec or "archetype_specific" not in spec:
        return results
    arch_spec = spec["archetype_specific"]
    release_archetypes = set(arch_spec.get("release_execution_archetypes", []))
    triad_skills = arch_spec.get("release_triad_skills", [])
    per_archetype = arch_spec.get("per_archetype_action", {})

    archetype = _read_archetype(agent_path)
    skills_dir = agent_path / ".claude" / "skills"
    triad_present = [s for s in triad_skills if (skills_dir / s).is_dir()]
    triad_count = len(triad_present)

    if not archetype:
        msg = (f"archetype: identity.json archetype field absent or unreadable "
               f"(per gmelli/aget-aget#1200 spec-fault); "
               f"diagnostic-only: {triad_count}/{len(triad_skills)} release-triad skills present")
        results.append(("WARN", msg))
        return results

    if archetype not in per_archetype:
        canonical = ", ".join(sorted(per_archetype.keys()))
        results.append(("WARN", f"archetype: '{archetype}' not in DEPLOYMENT_SPEC catalog (canonical: {canonical}); cannot verify CAP-TPL-016-07"))
        return results

    if archetype == "document-processor":
        results.append(("OK", f"archetype: '{archetype}' (dormant per #1121); no triad check"))
        return results

    if archetype in release_archetypes:
        if triad_count == len(triad_skills):
            results.append(("OK", f"archetype: '{archetype}' (release-execution) has all {triad_count}/{len(triad_skills)} release-triad skills (CAP-TPL-016-07)"))
        else:
            missing = [s for s in triad_skills if s not in triad_present]
            results.append(("FAIL", f"archetype: '{archetype}' (release-execution) missing {len(missing)} release-triad skill(s): {', '.join(missing)}"))
    else:
        if triad_count == 0:
            results.append(("OK", f"archetype: '{archetype}' (non-release) correctly has no release-triad skills (CAP-TPL-016-07)"))
        else:
            results.append(("WARN", f"archetype: '{archetype}' (non-release per CAP-TPL-016-07) has unexpected release-triad skill(s): {', '.join(triad_present)}"))
    return results


def check_optional_adoptions_v316(agent_path):
    """v3.16 optional adoptions O-3.16-1..4 — WARN-tier when absent (non-blocking)."""
    results = []
    skills_dir = agent_path / ".claude" / "skills"

    # O-3.16-3: /aget-go (SKILL-048; CAP-PP-019-04)
    if (skills_dir / "aget-go").is_dir() and (skills_dir / "aget-go" / "SKILL.md").exists():
        results.append(("OK", "O-3.16-3: /aget-go skill present (SKILL-048)"))
    else:
        results.append(("WARN", "O-3.16-3: /aget-go skill not present (optional; free-text 'go' remains valid)"))

    # CAP-SEC-007 .agetignore (v3.16 NEW; hook deferred to v3.17)
    if (agent_path / ".agetignore").exists():
        results.append(("OK", ".agetignore: present (CAP-SEC-007 knowledge-tier isolation skeleton)"))
    else:
        results.append(("WARN", ".agetignore: not present (CAP-SEC-007 v3.16 NEW; hook enforcement deferred to v3.17)"))

    # O-3.16-1: Plan_Status / Gate_Status template adoption (CAP-PP-003)
    template_path = agent_path / "templates" / "PROJECT_PLAN_TEMPLATE.md"
    alt_template = agent_path / ".aget" / "templates" / "PROJECT_PLAN_TEMPLATE.md"
    template = template_path if template_path.exists() else (alt_template if alt_template.exists() else None)
    if template:
        content = template.read_text()
        has_plan = "**Plan_Status**:" in content
        has_gate = "**Gate_Status:**" in content
        rel = template.relative_to(agent_path) if str(template).startswith(str(agent_path)) else template.name
        if has_plan and has_gate:
            results.append(("OK", f"O-3.16-1: PROJECT_PLAN_TEMPLATE adopts Plan_Status + Gate_Status schema (CAP-PP-003) — {rel}"))
        elif has_plan or has_gate:
            results.append(("WARN", f"O-3.16-1: PROJECT_PLAN_TEMPLATE partial schema adoption (Plan_Status={has_plan}, Gate_Status={has_gate})"))
        else:
            results.append(("WARN", "O-3.16-1: PROJECT_PLAN_TEMPLATE uses legacy **Status**: schema (CAP-PP-003 not adopted; old schema remains valid)"))
    else:
        results.append(("WARN", "O-3.16-1: no PROJECT_PLAN_TEMPLATE.md found at templates/ or .aget/templates/"))

    return results


def check_sleeping_caps_disclosure(spec):
    """v3.16: sleeping CAP-REL-030/031/032/033 disclosed (R-DEP-010 grace); informational reminder."""
    results = []
    if not spec or "sleeping_requirements" not in spec:
        return results
    sleep = spec["sleeping_requirements"]
    affected = sleep.get("affected_caps", [])
    if affected:
        ids = [c.get("id", "?") for c in affected]
        impl = affected[0].get("implementation_target", "v3.17")
        rem = affected[0].get("removal_threshold", "v3.18")
        results.append(("WARN", f"Sleeping CAPs disclosed (R-DEP-010 grace): {', '.join(ids)} — impl target {impl}, removal threshold {rem}"))
    return results


# ============================================================================
# main
# ============================================================================

def main():
    parser = argparse.ArgumentParser(description="AGET Deployment Verification")
    parser.add_argument("--version", required=True, help="Target version (e.g., 3.16.0)")
    parser.add_argument("--path", default=".", help="Agent directory path (default: .)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    agent_path = Path(args.path).resolve()
    version = args.version

    is_framework = (agent_path.name == "aget" and
                    not (agent_path / "AGENTS.md").exists() and
                    (agent_path / "specs").is_dir())

    print(f"=== AGET Deployment Verification: v{version} ===")
    print(f"Agent: {agent_path.name}" + (" (framework core)" if is_framework else ""))

    # v3.16+ : spec-driven verification (load DEPLOYMENT_SPEC_v{version}.yaml)
    framework_root = find_aget_root_from_agent(agent_path)
    spec, spec_path = load_deployment_spec(version, agent_path, framework_root)
    use_v316_surface = bool(spec) and _version_ge(version, "3.16.0") and not is_framework
    if spec:
        ucount = (spec.get("universal_skills") or {}).get("count", "?")
        archs = (spec.get("archetype_specific") or {}).get("per_archetype_action") or {}
        print(f"Spec: {spec_path.name} (v3.16+ surface; {ucount} universal skills; {len(archs)} archetypes)")
    elif _version_ge(version, "3.16.0"):
        if not YAML_AVAILABLE:
            print(f"Spec: pyyaml NOT INSTALLED — falling back to legacy v3.15 surface (install: pip install pyyaml)")
        else:
            print(f"Spec: DEPLOYMENT_SPEC_v{version}.yaml NOT FOUND — falling back to legacy v3.15 surface")
    print()

    if is_framework:
        categories = [
            ("Version Indicators", check_version_indicators(agent_path, version, is_framework=True)),
            ("Migration History", check_migration_history(agent_path, version)),
            ("Required Directories (v3.11+)", check_required_directories(agent_path)),
            ("Session Scripts", check_session_scripts(agent_path)),
        ]
    else:
        categories = [
            ("Version Indicators", check_version_indicators(agent_path, version)),
            ("Migration History", check_migration_history(agent_path, version)),
            ("Required Directories (v3.11+)", check_required_directories(agent_path)),
            ("Governance Intensity (v3.11+)", check_governance_intensity(agent_path)),
            ("Terminology (v3.11+)", check_terminology(agent_path)),
        ]
        if use_v316_surface:
            categories.append(("Universal Skills (v3.16 spec-derived)", check_universal_skills_v316(agent_path, framework_root)))
        else:
            categories.append(("Universal Skills (legacy v3.5-era hardcoded)", check_universal_skills(agent_path)))
        categories.append(("Session Scripts", check_session_scripts(agent_path)))
        categories.append(("Structural Enforcement (v3.10+)", check_structural_enforcement(agent_path)))
        if use_v316_surface:
            categories.append(("Archetype Action (CAP-TPL-016-07 v3.16)", check_archetype_action(agent_path, spec)))
            categories.append(("Optional Adoptions (O-3.16-1..4)", check_optional_adoptions_v316(agent_path)))
            categories.append(("Sleeping Requirements (R-DEP-010)", check_sleeping_caps_disclosure(spec)))

    errors = 0
    warnings = 0
    passes = 0

    for category, results in categories:
        print(f"--- {category} ---")
        for status, msg in results:
            if status == "OK":
                print(f"  [OK]   {msg}")
                passes += 1
            elif status == "FAIL":
                print(f"  [FAIL] {msg}")
                errors += 1
            elif status == "WARN":
                print(f"  [WARN] {msg}")
                warnings += 1
        print()

    total = passes + errors + warnings
    print("=== Summary ===")
    if errors == 0 and warnings == 0:
        print(f"PASS: Agent correctly deployed at v{version} ({passes}/{total} checks)")
        exit_code = 0
    elif errors == 0:
        print(f"PASS (with {warnings} warning(s)): Agent deployed at v{version} ({passes}/{total} OK)")
        exit_code = 0
    else:
        print(f"FAIL: {errors} error(s), {warnings} warning(s) ({passes}/{total} OK)")
        exit_code = 1

    if args.json:
        json_output = {
            "version": version,
            "agent": str(agent_path),
            "passes": passes,
            "errors": errors,
            "warnings": warnings,
            "total": total,
            "exit_code": exit_code,
        }
        print(json.dumps(json_output, indent=2))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
