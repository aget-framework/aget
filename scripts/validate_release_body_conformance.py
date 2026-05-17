#!/usr/bin/env python3
"""
validate_release_body_conformance.py — GitHub Release body template conformance validator.

Implements CAP-REL-006-02-NN structured-template requirement (v3.17+).
Template per L944 + v3.17 release-body exemplar:
    - Theme: line  (required)
    - What's New (required, bulleted)
    - Sleeping-CAPs Disclosure (required only if sleeping CAPs exist)
    - Compatibility (required)
    - Migration (required only if breaking change)

Promoted to canonical aget/scripts/ in v3.18 (gh#1308 / T1.6). Sibling to
post_release_changelog_validator.py and post_release_tag_validator.py.

Usage:
    validate_release_body_conformance.py --tag v3.17.0
    validate_release_body_conformance.py --last 10
    validate_release_body_conformance.py --all --json

Exit codes:
    0: all checked releases conformant
    1: one or more non-conformant
    2: gh CLI error or auth failure

Traceability: CAP-REL-006-02-NN | L944 | gh#1306 | gh#1308
"""
from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from typing import Optional

REPO = "aget-framework/aget"

# CAP-REL-006-02-NN required markers (regex patterns, case-insensitive)
MARKERS = {
    "theme": re.compile(r"(?i)^\s*\**Theme\**\s*[:\-—]", re.MULTILINE),
    "whats_new": re.compile(r"(?i)^#{0,3}\s*\**what'?s new\**", re.MULTILINE),
    "compatibility": re.compile(r"(?i)^#{0,3}\s*\**compatibility\**", re.MULTILINE),
    # Conditional markers (only required when triggered):
    "sleeping_caps": re.compile(r"(?i)sleeping[- ]caps?[- ]disclosure", re.MULTILINE),
    "migration": re.compile(r"(?i)^#{0,3}\s*\**migration\**", re.MULTILINE),
    # Affirmative breaking-change detection only — must distinguish "breaking changes: NONE" from
    # actual declarations. Heuristic: BC-NNN labels OR "Breaking Release/Section" header OR
    # numeric count "N breaking changes". Negated forms ("no breaking", "NONE", "zero breaking")
    # do NOT trigger.
    "breaking": re.compile(
        r"(?im)(?:^#{0,3}\s*\**Breaking\s+(?:Release|Changes?)\**|"
        r"\bBC-\d+\b|"
        r"\b\d+\s+breaking\s+changes?\b)",
        re.MULTILINE,
    ),
    "breaking_negated": re.compile(
        r"(?i)(?:\bno\s+(?:new\s+)?breaking|breaking\s+changes?\s*[:\-]\s*none|"
        r"zero\s+breaking|breaking\s+changes?\s*:\s*NONE)",
        re.MULTILINE,
    ),
}


@dataclass
class ConformanceResult:
    tag: str
    has_theme: bool
    has_whats_new: bool
    has_compatibility: bool
    declares_breaking: bool
    has_migration: bool
    declares_sleeping_caps: bool
    body_length: int
    conformant: bool
    failures: list[str]


def fetch_release_body(tag: str) -> Optional[str]:
    """Return the release body for the given tag, or None if not found."""
    try:
        result = subprocess.run(
            ["gh", "release", "view", tag, "--repo", REPO, "--json", "body", "-q", ".body"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def evaluate(tag: str, body: str) -> ConformanceResult:
    """Apply CAP-REL-006-02-NN markers to a release body and return result."""
    has_theme = bool(MARKERS["theme"].search(body))
    has_whats_new = bool(MARKERS["whats_new"].search(body))
    has_compatibility = bool(MARKERS["compatibility"].search(body))
    affirmative_breaking = bool(MARKERS["breaking"].search(body))
    declares_breaking = affirmative_breaking
    has_migration = bool(MARKERS["migration"].search(body))
    declares_sleeping_caps = bool(MARKERS["sleeping_caps"].search(body))

    failures: list[str] = []
    if not has_theme:
        failures.append("missing Theme: marker")
    if not has_whats_new:
        failures.append("missing What's New section")
    if not has_compatibility:
        failures.append("missing Compatibility section")
    if declares_breaking and not has_migration:
        failures.append("declares breaking change but missing Migration section")

    return ConformanceResult(
        tag=tag,
        has_theme=has_theme,
        has_whats_new=has_whats_new,
        has_compatibility=has_compatibility,
        declares_breaking=declares_breaking,
        has_migration=has_migration,
        declares_sleeping_caps=declares_sleeping_caps,
        body_length=len(body),
        conformant=(len(failures) == 0),
        failures=failures,
    )


def list_recent_tags(limit: int) -> list[str]:
    result = subprocess.run(
        ["gh", "release", "list", "--repo", REPO, "-L", str(limit), "--json", "tagName", "-q", ".[].tagName"],
        capture_output=True, text=True, check=True,
    )
    return [line.strip() for line in result.stdout.splitlines() if line.strip()]


def format_text(results: list[ConformanceResult]) -> str:
    lines = []
    lines.append(f"{'Tag':<12} {'Conformant':<11} {'Body':>5} {'Markers (T/W/C/B/M/S)':<25} Failures")
    lines.append("-" * 100)
    for r in results:
        markers = "{}/{}/{}/{}/{}/{}".format(
            "Y" if r.has_theme else "·",
            "Y" if r.has_whats_new else "·",
            "Y" if r.has_compatibility else "·",
            "Y" if r.declares_breaking else "·",
            "Y" if r.has_migration else "·",
            "Y" if r.declares_sleeping_caps else "·",
        )
        status = "PASS" if r.conformant else "FAIL"
        fail_text = "; ".join(r.failures) if r.failures else ""
        lines.append(f"{r.tag:<12} {status:<11} {r.body_length:>5} {markers:<25} {fail_text}")
    return "\n".join(lines)


def main() -> int:
    parser = argparse.ArgumentParser(description="GitHub Release body CAP-REL-006-02-NN conformance validator")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tag", help="single release tag, e.g. v3.17.0")
    group.add_argument("--last", type=int, help="check N most recent releases")
    group.add_argument("--all", action="store_true", help="check all releases (uses --last 100)")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    if args.tag:
        tags = [args.tag]
    else:
        limit = 100 if args.all else args.last
        tags = list_recent_tags(limit)

    results: list[ConformanceResult] = []
    for tag in tags:
        body = fetch_release_body(tag)
        if body is None:
            print(f"ERROR: could not fetch release {tag}", file=sys.stderr)
            return 2
        results.append(evaluate(tag, body))

    if args.json:
        print(json.dumps([asdict(r) for r in results], indent=2))
    else:
        print(format_text(results))

    any_failures = any(not r.conformant for r in results)
    return 1 if any_failures else 0


if __name__ == "__main__":
    sys.exit(main())
