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

Exit Codes:
    0: All checks PASS (or PASS with warnings)
    1: One or more checks FAIL
"""

import argparse
import json
import os
import re
import sys
from pathlib import Path


def check_version_indicators(agent_path: Path, version: str) -> list:
    """Check all version-bearing files match target version."""
    results = []

    # version.json
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
            results.append(("FAIL", f"version.json: parse error — {e}"))
    else:
        results.append(("FAIL", "version.json: file not found"))

    # AGENTS.md
    agents_path = agent_path / "AGENTS.md"
    if agents_path.exists():
        content = agents_path.read_text()
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

    # manifest.yaml
    manifest_path = agent_path / "manifest.yaml"
    if manifest_path.exists():
        content = manifest_path.read_text()
        match = re.search(r"^version:\s*[\"']?(\S+?)[\"']?\s*$", content, re.MULTILINE)
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


def check_migration_history(agent_path: Path, version: str) -> list:
    """Check migration history includes target version."""
    results = []
    vj_path = agent_path / ".aget" / "version.json"
    if vj_path.exists():
        try:
            with open(vj_path) as f:
                data = json.load(f)
            history = data.get("migration_history", [])
            has_version = any(version in entry for entry in history)
            if has_version:
                results.append(("OK", f"migration_history: includes {version}"))
            else:
                results.append(("WARN", f"migration_history: missing {version} entry"))
        except (json.JSONDecodeError, KeyError):
            results.append(("WARN", "migration_history: parse error"))
    return results


def check_required_directories(agent_path: Path) -> list:
    """Check v3.11.0+ required directories exist."""
    results = []

    # requirements/ — required for templates, optional for private agents
    req_dir = agent_path / "requirements"
    if req_dir.is_dir():
        results.append(("OK", "requirements/ directory exists"))
    else:
        # Check if this is a template (has README.md with "template" in name)
        agent_name = agent_path.name
        if "template-" in agent_name or agent_name == "aget":
            results.append(("FAIL", "requirements/ directory MISSING"))
        else:
            results.append(("WARN", "requirements/ directory missing (optional for private agents)"))

    # .claude/hooks/
    hooks_dir = agent_path / ".claude" / "hooks"
    if hooks_dir.is_dir():
        results.append(("OK", ".claude/hooks/ directory exists"))
        # Check for README
        hooks_readme = hooks_dir / "README.md"
        if hooks_readme.exists():
            results.append(("OK", ".claude/hooks/README.md exists"))
        else:
            results.append(("WARN", ".claude/hooks/README.md missing"))
    else:
        results.append(("FAIL", ".claude/hooks/ directory MISSING"))

    return results


def check_governance_intensity(agent_path: Path) -> list:
    """Check governance_intensity field exists in AGENTS.md."""
    results = []
    agents_path = agent_path / "AGENTS.md"
    if agents_path.exists():
        content = agents_path.read_text()
        if re.search(r"governance.intensity|Governance Intensity", content, re.IGNORECASE):
            results.append(("OK", "governance_intensity field present"))
        else:
            results.append(("FAIL", "governance_intensity field MISSING in AGENTS.md"))
    return results


def check_terminology(agent_path: Path) -> list:
    """Check 'sanity check' replaced with 'health check' in operational files.

    Only checks AGENTS.md, CLAUDE.md, and scripts/*.py — not SOPs, L-docs,
    or historical documents where 'sanity' may appear in valid context.
    """
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
            content = py_file.read_text()
            matches = len(re.findall(r"sanity.check", content, re.IGNORECASE))
            if matches:
                count += matches
                files_with.append(py_file.name)

    if count == 0:
        results.append(("OK", "terminology: 0 'sanity check' in operational files"))
    else:
        results.append(("WARN", f"terminology: {count} 'sanity check' in {', '.join(files_with)}"))

    return results


def check_universal_skills(agent_path: Path) -> list:
    """Check universal skills exist (16 minimum for v3.10.0+)."""
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
        "aget-create-skill"
    ]

    missing = []
    for skill in UNIVERSAL:
        if not (skills_dir / skill).is_dir():
            missing.append(skill)

    if not missing:
        results.append(("OK", f"skills: all 16 universal skills present"))
    else:
        results.append(("FAIL", f"skills: {len(missing)} missing — {', '.join(missing[:3])}{'...' if len(missing) > 3 else ''}"))

    # Check retired names
    RETIRED = ["aget-capture-observation", "aget-capture-nugget", "aget-study-up"]
    for old_name in RETIRED:
        if (skills_dir / old_name).is_dir():
            results.append(("WARN", f"skills: retired name '{old_name}' still exists"))

    return results


def check_session_scripts(agent_path: Path) -> list:
    """Check session scripts exist in scripts/ (not deprecated .aget/patterns/session/)."""
    results = []
    scripts_dir = agent_path / "scripts"

    REQUIRED = ["wake_up.py", "wind_down.py", "study_up.py", "aget_housekeeping_protocol.py"]

    for script in REQUIRED:
        if (scripts_dir / script).exists():
            results.append(("OK", f"scripts/{script}"))
        elif (agent_path / ".aget" / "patterns" / "session" / script).exists():
            results.append(("WARN", f"{script}: at deprecated path (.aget/patterns/session/)"))
        else:
            results.append(("WARN", f"{script}: not found"))

    return results


def check_structural_enforcement(agent_path: Path) -> list:
    """Check D71 structural enforcement sections exist (v3.10.0+)."""
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


def main():
    parser = argparse.ArgumentParser(description="AGET Deployment Verification")
    parser.add_argument("--version", required=True, help="Target version (e.g., 3.11.0)")
    parser.add_argument("--path", default=".", help="Agent directory path (default: .)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    agent_path = Path(args.path).resolve()
    version = args.version

    print(f"=== AGET Deployment Verification: v{version} ===")
    print(f"Agent: {agent_path.name}")
    print()

    all_results = []

    categories = [
        ("Version Indicators", check_version_indicators(agent_path, version)),
        ("Migration History", check_migration_history(agent_path, version)),
        ("Required Directories (v3.11+)", check_required_directories(agent_path)),
        ("Governance Intensity (v3.11+)", check_governance_intensity(agent_path)),
        ("Terminology (v3.11+)", check_terminology(agent_path)),
        ("Universal Skills", check_universal_skills(agent_path)),
        ("Session Scripts", check_session_scripts(agent_path)),
        ("Structural Enforcement (v3.10+)", check_structural_enforcement(agent_path)),
    ]

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
            all_results.append({"category": category, "status": status, "message": msg})
        print()

    # Summary
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
            "results": all_results,
        }
        print(json.dumps(json_output, indent=2))

    sys.exit(exit_code)


if __name__ == "__main__":
    main()
