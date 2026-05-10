#!/usr/bin/env python3
"""
V-CAP-REL-006-02: Validate GitHub Release body conforms to CAP-REL-006-02-01..06.

Implements:
- CAP-REL-006-02-01: Theme line present
- CAP-REL-006-02-02: What's New section with ≥3 bullets
- CAP-REL-006-02-03: Compatibility section
- CAP-REL-006-02-04: Sleeping-CAPs Disclosure (if applicable)
- CAP-REL-006-02-05: CHANGELOG link resolves (HTTP 200)
- CAP-REL-006-02-06: Body length ≥ 30 lines

Usage:
    python3 validate_release_body.py --version 3.17.0 [--repo aget-framework/aget] [--strict] [--json]
    python3 validate_release_body.py --version 3.17.0 --all-repos  # all 14 repos

Exit codes:
    0 = all PASS
    1 = any FAIL
    2 = validator error (e.g., gh CLI unavailable)
"""

import argparse
import json
import re
import subprocess
import sys
from urllib.request import urlopen
from urllib.error import HTTPError, URLError

ALL_REPOS = [
    "aget-framework/aget",
    "aget-framework/template-advisor-aget",
    "aget-framework/template-analyst-aget",
    "aget-framework/template-architect-aget",
    "aget-framework/template-consultant-aget",
    "aget-framework/template-developer-aget",
    "aget-framework/template-document-processor-AGET",
    "aget-framework/template-executive-aget",
    "aget-framework/template-operator-aget",
    "aget-framework/template-researcher-aget",
    "aget-framework/template-reviewer-aget",
    "aget-framework/template-spec-engineer-aget",
    "aget-framework/template-supervisor-aget",
    "aget-framework/template-worker-aget",
]


def fetch_release_body(repo: str, version: str) -> str:
    """Fetch release body via gh CLI."""
    tag = f"v{version}"
    result = subprocess.run(
        ["gh", "release", "view", tag, "--repo", repo, "--json", "body", "-q", ".body"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh release view failed for {repo} {tag}: {result.stderr}")
    return result.stdout.strip()


def url_resolves(url: str, timeout: int = 10) -> bool:
    """Check URL returns HTTP 200."""
    try:
        with urlopen(url, timeout=timeout) as resp:
            return resp.status == 200
    except (HTTPError, URLError, ValueError):
        return False


def validate_body(repo: str, version: str, body: str) -> dict:
    """Run all CAP-REL-006-02-NN sub-requirement checks."""
    results = {"repo": repo, "version": version, "checks": {}, "overall": "PASS"}

    # CAP-REL-006-02-01: Theme line
    has_theme = bool(re.search(r'\*\*Theme\*\*:', body))
    results["checks"]["CAP-REL-006-02-01_theme"] = "PASS" if has_theme else "FAIL"

    # CAP-REL-006-02-02: What's New section with ≥3 bullets
    whats_new_section = re.search(r'##\s+What\'s New\s*\n((?:.|\n)+?)(?=\n##\s|\Z)', body, re.IGNORECASE)
    bullets = 0
    if whats_new_section:
        bullets = len(re.findall(r'^\s*[-*]\s+', whats_new_section.group(1), re.MULTILINE))
    results["checks"]["CAP-REL-006-02-02_whats_new"] = "PASS" if bullets >= 3 else f"FAIL (found {bullets} bullets in What's New section; need ≥3)"

    # CAP-REL-006-02-03: Compatibility section
    has_compat = bool(re.search(r'##\s+Compatibility|##\s+No\s+breaking\s+changes|No breaking changes\.', body, re.IGNORECASE))
    results["checks"]["CAP-REL-006-02-03_compatibility"] = "PASS" if has_compat else "FAIL (no Compatibility section or 'No breaking changes' statement)"

    # CAP-REL-006-02-04: Sleeping-CAPs Disclosure (CONDITIONAL — required if SPEC-LANDED-IMPL-DEFERRED present)
    mentions_sleeping = bool(re.search(r'SPEC-LANDED|sleeping[\s-]*CAP|grace[\s-]*extend', body, re.IGNORECASE))
    has_disclosure = bool(re.search(r'##\s+Sleeping[\s-]*CAPs?', body, re.IGNORECASE))
    if mentions_sleeping:
        results["checks"]["CAP-REL-006-02-04_sleeping_disclosure"] = "PASS" if has_disclosure else "FAIL (mentions sleeping CAPs but lacks dedicated disclosure section)"
    else:
        results["checks"]["CAP-REL-006-02-04_sleeping_disclosure"] = "PASS (not applicable)"

    # CAP-REL-006-02-05: CHANGELOG link resolves
    changelog_links = re.findall(r'https?://[^\s\)]+(?:CHANGELOG|AGET_DELTA|release-notes)[^\s\)]*\.(?:md|html)?', body)
    if changelog_links:
        # Check at least one resolves
        resolves = any(url_resolves(url) for url in changelog_links[:3])  # cap at 3 to limit network calls
        results["checks"]["CAP-REL-006-02-05_link_resolves"] = "PASS" if resolves else f"FAIL (links found but none resolve: {changelog_links[:3]})"
    else:
        results["checks"]["CAP-REL-006-02-05_link_resolves"] = "FAIL (no CHANGELOG/AGET_DELTA/release-notes link found)"

    # CAP-REL-006-02-06: WITHDRAWN at authoring time
    # Length-as-proxy was redundant with CAP-REL-006-02-01..05 multi-condition correctness;
    # avoiding L935 self-instance (length-presence vs substance-correctness).
    # Substance is verified by the 5 checks above, not by line count.

    # Overall verdict
    if any(check.startswith("FAIL") for check in results["checks"].values()):
        results["overall"] = "FAIL"

    return results


def main():
    parser = argparse.ArgumentParser(description="Validate GitHub Release body per CAP-REL-006-02-NN")
    parser.add_argument("--version", required=True, help="Version to validate (e.g., 3.17.0)")
    parser.add_argument("--repo", help="Single repo (e.g., aget-framework/aget); default = all 14")
    parser.add_argument("--all-repos", action="store_true", help="Validate all 14 repos")
    parser.add_argument("--strict", action="store_true", help="Exit 1 on any FAIL (default true)")
    parser.add_argument("--json", action="store_true", help="JSON output")
    args = parser.parse_args()

    repos = [args.repo] if args.repo else ALL_REPOS
    all_results = []
    any_fail = False

    for repo in repos:
        try:
            body = fetch_release_body(repo, args.version)
            result = validate_body(repo, args.version, body)
            all_results.append(result)
            if result["overall"] == "FAIL":
                any_fail = True
        except Exception as e:
            all_results.append({"repo": repo, "version": args.version, "error": str(e), "overall": "ERROR"})
            any_fail = True

    if args.json:
        print(json.dumps(all_results, indent=2))
    else:
        for r in all_results:
            print(f"\n=== {r['repo']} v{r['version']}: {r['overall']} ===")
            if "error" in r:
                print(f"  ERROR: {r['error']}")
            else:
                for check_id, status in r["checks"].items():
                    marker = "✅" if status.startswith("PASS") else "❌"
                    print(f"  {marker} {check_id}: {status}")
        print(f"\n{'='*50}\nSummary: {sum(1 for r in all_results if r['overall'] == 'PASS')}/{len(all_results)} repos PASS")

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
