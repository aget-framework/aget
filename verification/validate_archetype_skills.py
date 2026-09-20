#!/usr/bin/env python3
"""
Archetype Skills Conformance Validator (CAP-TPL-016-04)

Audits universal-skill conformance across the aget-framework fleet (aget/ core +
13 templates). Flags drift between AGET_TEMPLATE_SPEC mandate ("32 universal skills
in all templates", v3.15.0) and filesystem reality.

This validator was referenced in AGET_TEMPLATE_SPEC as the enforcer for
CAP-TPL-016-04 but did not previously exist (L671 instance — classification
without consequence). This is the L671 closure.

The "universal" set is derived empirically from template-worker-aget, which is
the historical baseline reference (per ARC-001). Templates are compared against
this baseline; the spec's count claim is itself verified.

Usage:
    python3 validate_archetype_skills.py
    python3 validate_archetype_skills.py --json
    python3 validate_archetype_skills.py --root /path/to/aget-framework
    python3 validate_archetype_skills.py --baseline-template worker

Exit codes:
    0  = all templates conformant
    1  = one or more templates non-conformant
    2  = configuration error (baseline missing, root not found, etc.)

See: AGET_TEMPLATE_SPEC CAP-TPL-016-04, L671, L656
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SPEC_MANDATE = 29  # CAP-TPL-016-04 (v3.16.0: 32 → 29; release-triad moved to release-execution archetype catalog per CAP-TPL-016-07)
DEFAULT_BASELINE = "template-worker-aget"

# Skills moved from universal baseline to release-execution archetype at v3.16.0
# (CAP-TPL-016-07). These are PRESENT in worker (release-execution archetype) but
# are NOT counted as part of the universal baseline. Subtracted from worker's
# skill set to derive the universal-29.
RELEASE_EXECUTION_EXTRAS = [
    "aget-release-build",
    "aget-release-audit-specs",
    "aget-release-critique",
]

# Archetype skill mapping (from validate_v3.5.0.py ARC-001).
# Skills listed here are EXPECTED extras beyond the universal baseline.
# At v3.16.0+ the worker archetype's release-triad is consolidated into
# RELEASE_EXECUTION_EXTRAS above (worker IS a release-execution archetype).
ARCHETYPE_EXTRAS = {
    "worker": ["aget-execute-task", "aget-report-progress"] + RELEASE_EXECUTION_EXTRAS,
    "supervisor": ["aget-broadcast-fleet", "aget-review-agent", "aget-escalate-issue"] + RELEASE_EXECUTION_EXTRAS,
    "developer": ["aget-run-tests", "aget-lint-code", "aget-review-pr"],
    "consultant": ["aget-assess-client", "aget-propose-engagement"],
    "advisor": ["aget-assess-risk", "aget-recommend-action"],
    "analyst": ["aget-analyze-data", "aget-generate-report"],
    "architect": ["aget-design-architecture", "aget-assess-tradeoffs"],
    "researcher": ["aget-search-literature", "aget-document-finding"],
    "operator": ["aget-handle-incident", "aget-run-playbook"],
    "executive": ["aget-make-decision", "aget-review-budget"],
    "reviewer": ["aget-review-artifact", "aget-provide-feedback"],
    "spec-engineer": ["aget-validate-spec", "aget-generate-requirement"],
    "document-processor": [],  # not yet defined; template lacks .claude/skills/
}


def archetype_of(template_dir: str) -> str:
    """Strip 'template-' prefix and '-aget'/'-AGET' suffix."""
    name = template_dir
    if name.startswith("template-"):
        name = name[len("template-"):]
    for suffix in ("-aget", "-AGET"):
        if name.endswith(suffix):
            name = name[: -len(suffix)]
            break
    return name


def list_skills(target_dir: Path) -> list[str]:
    """Return sorted list of skill names under target_dir/.claude/skills/.
    Returns empty list if .claude/skills/ does not exist."""
    skills_dir = target_dir / ".claude" / "skills"
    if not skills_dir.is_dir():
        return []
    return sorted(p.name for p in skills_dir.iterdir() if p.is_dir())


def discover_root(start: Path) -> Path | None:
    """Walk up from start to find the aget-framework/ root (contains aget/ and template-*)."""
    current = start.resolve()
    while current != current.parent:
        if (current / "aget").is_dir() and any(current.glob("template-*")):
            return current
        current = current.parent
    return None


def find_templates(root: Path) -> list[Path]:
    """Return all template-*-aget and template-*-AGET directories under root."""
    templates = []
    for child in sorted(root.iterdir()):
        if not child.is_dir():
            continue
        if child.name.startswith("template-") and (
            child.name.endswith("-aget") or child.name.endswith("-AGET")
        ):
            templates.append(child)
    return templates


def audit(root: Path, baseline_name: str) -> dict:
    """Run the conformance audit. Returns a structured result dict."""
    baseline_dir = root / baseline_name
    if not baseline_dir.is_dir():
        return {"error": f"Baseline template not found: {baseline_dir}"}

    baseline_skills = set(list_skills(baseline_dir))
    if not baseline_skills:
        return {"error": f"Baseline template has no .claude/skills/: {baseline_dir}"}

    baseline_archetype = archetype_of(baseline_name)
    baseline_extras = set(ARCHETYPE_EXTRAS.get(baseline_archetype, []))
    universal_set = baseline_skills - baseline_extras
    universal_count = len(universal_set)

    spec_alignment = {
        "spec_mandate": SPEC_MANDATE,
        "derived_universal": universal_count,
        "delta_vs_spec": universal_count - SPEC_MANDATE,
        "aligned": universal_count == SPEC_MANDATE,
    }

    targets = [root / "aget"] + find_templates(root)
    template_results = []
    non_conformant = 0

    for target in targets:
        skills = set(list_skills(target))
        archetype = archetype_of(target.name) if target.name != "aget" else "core"
        expected_extras = set(ARCHETYPE_EXTRAS.get(archetype, []))

        missing_universal = sorted(universal_set - skills)
        unexpected_extras = sorted(skills - universal_set - expected_extras)
        expected_extras_present = sorted(skills & expected_extras)
        expected_extras_missing = sorted(expected_extras - skills)

        is_conformant = len(missing_universal) == 0
        if not is_conformant:
            non_conformant += 1

        template_results.append({
            "name": target.name,
            "archetype": archetype,
            "skill_count": len(skills),
            "missing_universal_count": len(missing_universal),
            "missing_universal": missing_universal,
            "expected_archetype_extras": sorted(expected_extras),
            "expected_extras_present": expected_extras_present,
            "expected_extras_missing": expected_extras_missing,
            "unexpected_extras": unexpected_extras,
            "has_claude_skills": (target / ".claude" / "skills").is_dir(),
            "conformant": is_conformant,
        })

    return {
        "root": str(root),
        "baseline_template": baseline_name,
        "spec_alignment": spec_alignment,
        "template_count": len(targets),
        "conformant_count": len(targets) - non_conformant,
        "non_conformant_count": non_conformant,
        "templates": template_results,
    }


def render_human(result: dict) -> str:
    if "error" in result:
        return f"ERROR: {result['error']}"

    lines = []
    sa = result["spec_alignment"]
    lines.append(f"Root: {result['root']}")
    lines.append(f"Baseline: {result['baseline_template']}")
    lines.append("")
    lines.append("SPEC ALIGNMENT (CAP-TPL-016-04):")
    lines.append(f"  Spec mandate          : {sa['spec_mandate']} universal skills")
    lines.append(f"  Derived from baseline : {sa['derived_universal']} universal skills")
    lines.append(f"  Delta vs spec         : {sa['delta_vs_spec']:+d}")
    lines.append(f"  Aligned               : {'YES' if sa['aligned'] else 'NO (spec or baseline drift)'}")
    lines.append("")
    lines.append(f"FLEET CONFORMANCE: {result['conformant_count']}/{result['template_count']} conformant")
    lines.append("")
    lines.append(f"{'Template':<42} {'Skills':>7} {'Missing':>8} {'Has Skills Dir':>15} {'Status':>10}")
    lines.append("-" * 90)
    for t in result["templates"]:
        status = "OK" if t["conformant"] else f"GAP ({t['missing_universal_count']})"
        lines.append(
            f"{t['name']:<42} {t['skill_count']:>7} {t['missing_universal_count']:>8} "
            f"{'yes' if t['has_claude_skills'] else 'NO':>15} {status:>10}"
        )
    lines.append("")
    gaps = [t for t in result["templates"] if not t["conformant"]]
    if gaps:
        lines.append("GAPS DETAIL:")
        for t in gaps:
            lines.append(f"\n  {t['name']} (archetype: {t['archetype']}):")
            if not t["has_claude_skills"]:
                lines.append("    [STRUCTURAL] No .claude/skills/ directory at all")
            if t["missing_universal"]:
                lines.append(f"    Missing universal ({t['missing_universal_count']}):")
                for skill in t["missing_universal"]:
                    lines.append(f"      - {skill}")
            if t["expected_extras_missing"]:
                lines.append(f"    Missing archetype extras:")
                for skill in t["expected_extras_missing"]:
                    lines.append(f"      - {skill}")
    return "\n".join(lines)



# --------------------------------------------------------------------------- C-34-01
def agent_skill_defects(agent_path: Path) -> list:
    """The same predicate as skill_description_defects, scoped to ONE agent directory.

    C-34-01 / gh#2445. The scaffold validates the agent it just created, not the tree of
    repositories around it, so the sweeping function cannot be reused directly: pointing
    it at agent_path.parent would fail an instantiation because of an unrelated sibling.

    Paths are reported relative to agent_path. This is the single predicate; the repo
    sweep below delegates to it so the scaffold gate and the audit can never drift apart.
    """
    defects = []
    skills_dir = agent_path / ".claude" / "skills"
    if not skills_dir.is_dir():
        return defects
    for skill in sorted(q for q in skills_dir.iterdir() if q.is_dir()):
        f = skill / "SKILL.md"
        if not f.is_file():
            continue
        text = f.read_text(encoding="utf-8", errors="replace")
        rel = str(f.relative_to(agent_path))
        if not text.startswith("---"):
            defects.append({"path": rel, "skill": skill.name, "defect": "frontmatter-absent"})
            continue
        parts = text.split("---", 2)
        if len(parts) < 3:
            defects.append({"path": rel, "skill": skill.name, "defect": "frontmatter-unterminated"})
            continue
        try:
            import yaml
            meta = yaml.safe_load(parts[1])
        except Exception as exc:
            defects.append({"path": rel, "skill": skill.name,
                            "defect": "frontmatter-unparseable", "detail": str(exc)[:120]})
            continue
        if not isinstance(meta, dict):
            defects.append({"path": rel, "skill": skill.name, "defect": "frontmatter-not-a-mapping"})
        else:
            # `str(...)` coercion was the hole. It turned YAML null into "None", True into
            # "True", 42 into "42" and a mapping into "{'a': 'b'}" -- all non-empty after
            # strip, so six invalid shapes (explicit null, implicit null, boolean, integer,
            # mapping, list) were ACCEPTED and copied into new agents. A consumer asking for
            # a description string gets a non-string or nothing in every one of those cases.
            # scripts/validate_agent_skill_package.py never had this hole: it has always
            # required isinstance(description, str). This aligns with that.
            desc = meta.get("description")
            if desc is None:
                defects.append({"path": rel, "skill": skill.name,
                                "defect": "description-empty-or-absent"})
            elif not isinstance(desc, str):
                defects.append({"path": rel, "skill": skill.name,
                                "defect": "description-not-a-string",
                                "detail": type(desc).__name__})
            elif not desc.strip():
                defects.append({"path": rel, "skill": skill.name,
                                "defect": "description-empty-or-absent"})
    return defects


def skill_description_defects(root: Path) -> list:
    """Every shipped SKILL.md must carry a STRICTLY-PARSEABLE, non-empty description.

    C-34-01 / gh#2445. Presence was already audited; parseability was not, so a skill
    could ship with no frontmatter at all, or with frontmatter whose description is an
    unquoted YAML scalar containing ': ' — which YAML reads as a mapping separator and
    rejects, making the whole block unparseable. Both shipped in all 13 registered
    templates: six skills with no frontmatter, and aget-create-goal unparseable.

    A consumer that routes on `description` sees nothing in either case, so the skill is
    invisible to routing while appearing present to a presence-only audit. That gap
    between "the file is there" and "the router can read it" is the defect.

    Returns one dict per defect; empty list means every shipped skill is routable.
    """
    defects = []
    for skills_dir in sorted(root.glob("*/.claude/skills")):
        agent_path = skills_dir.parent.parent
        prefix = agent_path.relative_to(root)
        for d in agent_skill_defects(agent_path):
            defects.append({**d, "path": str(prefix / d["path"])})
    return defects


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    parser.add_argument("--json", action="store_true", help="JSON output")
    parser.add_argument("--descriptions", action="store_true",
                        help="C-34-01: audit shipped SKILL.md frontmatter descriptions "
                             "under strict YAML parsing (exit 1 on any defect)")
    parser.add_argument("--root", type=Path, help="aget-framework root (auto-detect if omitted)")
    parser.add_argument(
        "--baseline-template",
        default=DEFAULT_BASELINE,
        help=f"Template used to derive universal-skill set (default: {DEFAULT_BASELINE})",
    )
    args = parser.parse_args()

    root = args.root if args.root else discover_root(Path.cwd())
    if not root or not root.is_dir():
        msg = f"Could not locate aget-framework root from {Path.cwd()}"
        print(json.dumps({"error": msg}) if args.json else msg, file=sys.stderr)
        return 2

    if args.descriptions:
        defects = skill_description_defects(root)
        payload = {"check": "skill_description_conformance",
                   "defects": defects, "defect_count": len(defects)}
        if args.json:
            print(json.dumps(payload, indent=2))
        elif defects:
            print(f"skill descriptions: {len(defects)} DEFECT(S)")
            for d in defects:
                print(f"  [{d['defect']}] {d['path']}")
        else:
            print("skill descriptions: all shipped skills carry a parseable description")
        return 0 if not defects else 1

    result = audit(root, args.baseline_template)
    if "error" in result:
        print(json.dumps(result) if args.json else f"ERROR: {result['error']}", file=sys.stderr)
        return 2

    print(json.dumps(result, indent=2) if args.json else render_human(result))
    return 0 if result["non_conformant_count"] == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
