#!/usr/bin/env python3
"""
V-CAP-REL-008b: Validate template README currency per R-REL-010b-01..03.

Implements:
- R-REL-010b-01: Each template's README.md displays current version near top
- R-REL-010b-02: Each template's README.md "Framework" reference matches released version
- R-REL-010b-03: Atomic across all 13 templates

Usage:
    python3 validate_template_readme_currency.py --version 3.17.0 [--templates-dir ../] [--json]

Closes 5-cycle chronic stale-template-README pattern (v3.13-v3.17 all silently shipped at v3.12.0).

Exit codes:
    0 = all PASS
    1 = any FAIL
    2 = validator error
"""

import argparse
import json
import re
import sys
from pathlib import Path

TEMPLATES = [
    "template-advisor-aget", "template-analyst-aget", "template-architect-aget",
    "template-consultant-aget", "template-developer-aget", "template-document-processor-AGET",
    "template-executive-aget", "template-operator-aget", "template-researcher-aget",
    "template-reviewer-aget", "template-spec-engineer-aget", "template-supervisor-aget",
    "template-worker-aget",
]


def validate_template_readme(template_path: Path, version: str) -> dict:
    """Run R-REL-010b-NN checks against a single template README."""
    readme = template_path / "README.md"
    if not readme.exists():
        return {"template": template_path.name, "checks": {}, "overall": "ERROR", "error": "README.md not found"}

    content = readme.read_text(encoding='utf-8')
    results = {"template": template_path.name, "checks": {}, "overall": "PASS"}

    # R-REL-010b-01: Header version line near top (≤ first 20 lines)
    header = '\n'.join(content.split('\n')[:20])
    header_version_matches = re.findall(r'\*\*Version\*\*:\s*v?(\d+\.\d+\.\d+)', header)
    if header_version_matches:
        if version in header_version_matches:
            results["checks"]["R-REL-010b-01_header_version"] = "PASS"
        else:
            results["checks"]["R-REL-010b-01_header_version"] = f"FAIL (header version is {header_version_matches[0]}; expected {version})"
    else:
        results["checks"]["R-REL-010b-01_header_version"] = "FAIL (no **Version**: vX.Y.Z line in first 20 lines)"

    # R-REL-010b-02: "Framework" reference line `[AGET v{X.Y.Z}]`
    framework_refs = re.findall(r'\[AGET\s+v?(\d+\.\d+\.\d+)\]', content)
    if framework_refs:
        if version in framework_refs:
            results["checks"]["R-REL-010b-02_framework_ref"] = "PASS"
        else:
            results["checks"]["R-REL-010b-02_framework_ref"] = f"FAIL ([AGET vX.Y.Z] reference is {framework_refs[0]}; expected {version})"
    else:
        results["checks"]["R-REL-010b-02_framework_ref"] = "FAIL (no [AGET vX.Y.Z] reference found)"

    if any(check.startswith("FAIL") for check in results["checks"].values()):
        results["overall"] = "FAIL"

    return results


def main():
    parser = argparse.ArgumentParser(description="Validate template README currency per R-REL-010b-NN")
    parser.add_argument("--version", required=True, help="Released version (e.g., 3.17.0)")
    parser.add_argument("--templates-dir", default="..", help="Directory containing template repos")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    base = Path(args.templates_dir)
    all_results = []
    any_fail = False

    for template_name in TEMPLATES:
        template_path = base / template_name
        if not template_path.exists():
            all_results.append({"template": template_name, "error": f"Template directory not found: {template_path}", "overall": "ERROR"})
            any_fail = True
            continue
        result = validate_template_readme(template_path, args.version)
        all_results.append(result)
        if result["overall"] != "PASS":
            any_fail = True

    if args.json:
        print(json.dumps(all_results, indent=2))
    else:
        for r in all_results:
            marker_overall = "✅" if r["overall"] == "PASS" else "❌"
            print(f"{marker_overall} {r['template']}: {r['overall']}")
            if "error" in r:
                print(f"    ERROR: {r['error']}")
            else:
                for check_id, status in r["checks"].items():
                    if not status.startswith("PASS"):
                        print(f"    {check_id}: {status}")
        passed = sum(1 for r in all_results if r["overall"] == "PASS")
        print(f"\n{'='*50}\nSummary: {passed}/{len(all_results)} templates PASS")

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
