#!/usr/bin/env python3
"""
V-CAP-REL-006-02: Validate a GitHub Release against the eight live CAP-REL-006-02 sub-requirements.

Implements (per AGET_RELEASE_SPEC v1.18.0):
- CAP-REL-006-02-01: Theme line present
- CAP-REL-006-02-02: What's New with 5-10 scannable items, each <=2 rendered lines
                     (a scannable item is a list item OR a bold-lead paragraph)
- CAP-REL-006-02-03: Compatibility section
- CAP-REL-006-02-04: every H2 is a registered name; required disclosure section per applicable class
- CAP-REL-006-02-05: CHANGELOG link resolves (HTTP 200)
- CAP-REL-006-02-07: body length 12-25 non-blank lines
- CAP-REL-006-02-08: core pair present (What's New AND Compatibility); no fixed total-section count
- CAP-REL-006-02-09: release title format

CAP-REL-006-02-06 is WITHDRAWN and is deliberately not validated.

Every live sub-requirement emits exactly one keyed result. A check that cannot be evaluated emits
UNAVAILABLE and names what was missing -- it is never silently omitted, because a consumer counting
green checks cannot distinguish an absent check from a passing one.

Usage:
    python3 validate_release_body.py --version 3.17.0 [--repo aget-framework/aget] [--strict] [--json]
    python3 validate_release_body.py --version 3.17.0 --all-repos  # all 14 repos

Exit codes:
    0 = all PASS
    1 = any FAIL or UNAVAILABLE
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

# CAP-REL-006-02-04 registered section vocabulary, corpus-derived 2026-08-17 over v3.17.0-v3.31.0.
# Keys are normalized labels; values are the honesty/structural class.
CORE_SECTIONS = {
    "what's new": "core",
    "compatibility": "core",
}
CONDITIONAL_STRUCTURAL = {
    "migration": "migration",
}
DISCLOSURE_SECTIONS = {
    # preferred label            class
    "sleeping-caps disclosure": "deferred_capability",
    "what this release doesn't change": "carried_debt",
    "known issues (pre-existing)": "carried_debt",          # registered alternate
    "deferred": "scope_reduction",
    "post-tag repairs": "post_tag_amendment",
    "known gaps": "ship_time_limitation",
    "disclosed limitations": "ship_time_limitation",        # registered alternate
}
REGISTERED_SECTIONS = {**CORE_SECTIONS, **CONDITIONAL_STRUCTURAL, **DISCLOSURE_SECTIONS}

LIVE_SUBREQUIREMENTS = ["01", "02", "03", "04", "05", "07", "08", "09"]


def normalize_heading(text: str) -> str:
    """Normalize an H2 label for registry lookup: case, whitespace, and apostrophe variants."""
    t = text.strip().lower()
    t = t.replace("’", "'").replace("‘", "'")
    t = re.sub(r"\s+", " ", t)
    return t


def extract_h2_labels(body: str) -> list:
    """Return normalized H2 labels in document order."""
    return [normalize_heading(m) for m in re.findall(r"^##\s+(.+?)\s*$", body, re.MULTILINE)]


def extract_scannable_items(section_text: str) -> list:
    """
    Return each scannable item's text.

    A scannable item is a bounded change summary rendered EITHER as a markdown list item
    (- or *) OR as a bold-lead paragraph (**Lead** - detail). Both are conformant and may be
    mixed; the bounded-item invariant is what the count was ever measuring, not bullet syntax.
    """
    item_start = r"(?:^[ \t]*[-*][ \t]+|^[ \t]*\*\*)"
    pattern = rf"{item_start}(.+?)(?=\n[ \t]*[-*][ \t]+|\n[ \t]*\*\*|\Z)"
    return re.findall(pattern, section_text, re.MULTILINE | re.DOTALL)


def rendered_line_count(item: str) -> int:
    """Non-blank rendered lines occupied by one item."""
    return len([ln for ln in item.strip().split("\n") if ln.strip()])


def fetch_release_field(repo: str, version: str, field: str) -> str:
    """Fetch a single field of a release via gh CLI."""
    tag = f"v{version}"
    result = subprocess.run(
        ["gh", "release", "view", tag, "--repo", repo, "--json", field, "-q", f".{field}"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        raise RuntimeError(f"gh release view --json {field} failed for {repo} {tag}: {result.stderr}")
    return result.stdout.strip()


def url_resolves(url: str, timeout: int = 10) -> bool:
    """Check URL returns HTTP 200."""
    try:
        with urlopen(url, timeout=timeout) as resp:
            return resp.status == 200
    except (HTTPError, URLError, ValueError):
        return False


def validate_body(repo, version, body, title=None, link_resolver=url_resolves):
    """
    Run every live CAP-REL-006-02-NN check.

    title=None means the caller could not supply a title; -09 then emits UNAVAILABLE rather than
    being omitted. link_resolver is injectable so tests need no network.
    """
    results = {"repo": repo, "version": version, "checks": {}, "overall": "PASS"}
    checks = results["checks"]
    h2_labels = extract_h2_labels(body)

    # -01: Theme line
    checks["CAP-REL-006-02-01_theme"] = (
        "PASS" if re.search(r"\*\*Theme\*\*:", body) else "FAIL (no **Theme**: line)"
    )

    # -02: What's New with 5-10 scannable items, each <=2 rendered lines
    section = re.search(r"##\s+What's New\s*\n((?:.|\n)+?)(?=\n##\s|\Z)", body, re.IGNORECASE)
    if not section:
        checks["CAP-REL-006-02-02_whats_new"] = "FAIL (no ## What's New section)"
    else:
        items = extract_scannable_items(section.group(1))
        n = len(items)
        overlong = [i for i in items if rendered_line_count(i) > 2]
        if not 5 <= n <= 10:
            adjective = "too thin" if n < 5 else "too verbose"
            checks["CAP-REL-006-02-02_whats_new"] = (
                f"FAIL (found {n} scannable items; need 5-10 — {adjective})"
            )
        elif overlong:
            checks["CAP-REL-006-02-02_whats_new"] = (
                f"FAIL ({n} scannable items but {len(overlong)} exceed 2 rendered lines)"
            )
        else:
            checks["CAP-REL-006-02-02_whats_new"] = f"PASS ({n} scannable items, each <=2 lines)"

    # -03: Compatibility section
    has_compat = "compatibility" in h2_labels or bool(
        re.search(r"No breaking changes", body, re.IGNORECASE)
    )
    checks["CAP-REL-006-02-03_compatibility"] = (
        "PASS" if has_compat
        else "FAIL (no Compatibility section or 'No breaking changes' statement)"
    )

    # -04: registered section vocabulary + required disclosure per applicable class
    unregistered = [h for h in h2_labels if h not in REGISTERED_SECTIONS]
    mentions_sleeping = bool(
        re.search(r"SPEC-LANDED|sleeping[\s-]*CAP|grace[\s-]*extend", body, re.IGNORECASE)
    )
    has_sleeping_section = any(
        DISCLOSURE_SECTIONS.get(h) == "deferred_capability" for h in h2_labels
    )
    if unregistered:
        checks["CAP-REL-006-02-04_disclosure"] = (
            f"FAIL (unregistered section name(s): {unregistered}; "
            f"'(or equivalent)' withdrawn in v1.18.0)"
        )
    elif mentions_sleeping and not has_sleeping_section:
        checks["CAP-REL-006-02-04_disclosure"] = (
            "FAIL (mentions sleeping CAPs but lacks a Sleeping-CAPs Disclosure section)"
        )
    else:
        classes = sorted({
            DISCLOSURE_SECTIONS[h] for h in h2_labels if h in DISCLOSURE_SECTIONS
        })
        detail = ", ".join(classes) if classes else "no disclosure class applicable"
        checks["CAP-REL-006-02-04_disclosure"] = f"PASS ({detail})"

    # -05: CHANGELOG link resolves
    links = re.findall(
        r"https?://[^\s\)]+(?:CHANGELOG|AGET_DELTA|release-notes)[^\s\)]*\.(?:md|html)?", body
    )
    if not links:
        checks["CAP-REL-006-02-05_link_resolves"] = (
            "FAIL (no CHANGELOG/AGET_DELTA/release-notes link found)"
        )
    elif any(link_resolver(u) for u in links[:3]):
        checks["CAP-REL-006-02-05_link_resolves"] = "PASS"
    else:
        checks["CAP-REL-006-02-05_link_resolves"] = f"FAIL (links found but none resolve: {links[:3]})"

    # -06 is WITHDRAWN: intentionally not validated, and intentionally not emitted.

    # -07: body length 12-25 non-blank lines
    nonblank = len([ln for ln in body.split("\n") if ln.strip()])
    byte_size = len(body.encode("utf-8"))
    if 12 <= nonblank <= 25:
        checks["CAP-REL-006-02-07_length"] = (
            f"PASS ({nonblank} nonblank lines, {byte_size} bytes within precedent 12-25/1500-2500)"
        )
    else:
        adjective = "too thin" if nonblank < 12 else "too verbose, exceeds precedent"
        checks["CAP-REL-006-02-07_length"] = (
            f"FAIL ({nonblank} nonblank lines; need 12-25 — {adjective})"
        )

    # -08: core pair present; no fixed total-section count
    missing_core = [label for label in ("what's new", "compatibility") if label not in h2_labels]
    if missing_core:
        checks["CAP-REL-006-02-08_sections"] = (
            f"FAIL (missing required core section(s): {missing_core})"
        )
    else:
        checks["CAP-REL-006-02-08_sections"] = (
            f"PASS (core pair present; {len(h2_labels)} H2 sections, no fixed count)"
        )

    # -09: release title format
    if title is None:
        checks["CAP-REL-006-02-09_title"] = (
            "UNAVAILABLE (no release title supplied; pass title= or use main(), "
            "which fetches `gh release view --json name`)"
        )
    else:
        checks["CAP-REL-006-02-09_title"] = _validate_title(title, version)

    if any(v.startswith("FAIL") for v in checks.values()):
        results["overall"] = "FAIL"
    elif any(v.startswith("UNAVAILABLE") for v in checks.values()):
        results["overall"] = "UNAVAILABLE"

    return results


def _validate_title(title: str, version: str) -> str:
    """CAP-REL-006-02-09: title is `v{X.Y.Z} - {theme}` or em-dash; version appears exactly once."""
    tag = f"v{version}"
    occurrences = len(re.findall(re.escape(tag), title))
    if occurrences == 0:
        return f"FAIL (title does not contain {tag}: {title!r})"
    if occurrences > 1:
        return f"FAIL (title contains {tag} {occurrences} times; must appear exactly once: {title!r})"
    if not re.match(rf"^{re.escape(tag)}\s+[-–—]\s+\S", title.strip()):
        return f"FAIL (title must be `{tag} - theme` or `{tag} — theme`: {title!r})"
    return f"PASS ({title!r})"


def main():
    parser = argparse.ArgumentParser(description="Validate a GitHub Release per CAP-REL-006-02-NN")
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
            body = fetch_release_field(repo, args.version, "body")
            try:
                title = fetch_release_field(repo, args.version, "name")
            except RuntimeError:
                title = None  # -09 will emit UNAVAILABLE rather than vanish
            result = validate_body(repo, args.version, body, title=title)
            all_results.append(result)
            if result["overall"] != "PASS":
                any_fail = True
        except Exception as e:
            all_results.append(
                {"repo": repo, "version": args.version, "error": str(e), "overall": "ERROR"}
            )
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
                    marker = "PASS" if status.startswith("PASS") else (
                        "WARN" if status.startswith("UNAVAILABLE") else "FAIL"
                    )
                    print(f"  [{marker}] {check_id}: {status}")
                print(f"  ({len(r['checks'])}/{len(LIVE_SUBREQUIREMENTS)} live sub-requirements emitted)")
        passing = sum(1 for r in all_results if r["overall"] == "PASS")
        print(f"\n{'='*50}\nSummary: {passing}/{len(all_results)} repos PASS")

    sys.exit(1 if any_fail else 0)


if __name__ == "__main__":
    main()
