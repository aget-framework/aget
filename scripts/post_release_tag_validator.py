#!/usr/bin/env python3
"""
post_release_tag_validator.py — CAP-REL-031 Post-Release Tag Validator (R-REL-027)

Verifies tag-resolvability invariants after release tag-cut + push.

Requirements implemented (per AGET_RELEASE_SPEC.md §CAP-REL-031):
  R-REL-031-01: tag reachable on remote via `git ls-remote origin v{VERSION}`
  R-REL-031-02: `git show v{VERSION}:handoffs/RELEASE_HANDOFF_v{VERSION}.md` resolves
                (the headline #1154 invariant — closes legalon #1152 root cause class)
  R-REL-031-03: IF DEPLOYMENT_SPEC published THEN tag resolves it
                (canonical: aget/DEPLOYMENT_SPEC_v{V}.yaml; legacy: DEPLOYMENT_SPEC_v{V}.yaml)
  R-REL-031-04: tag annotation includes version string + non-empty release-notes pointer
  R-REL-031-05: per-repo PASS/FAIL emitted to
                sessions/post_release_tag_audit_{VERSION}_{DATE}.md

Spec-layer pair to SOP_release_process.md v1.30 Phase 6.4.5 inline post-tag V-test.
SOP enforces ordering at release time; this script audits the invariant standalone.

CAP-REL-031 implementation closure: v3.17 G1.T1.2 (build 2026-05-09).
v3.16 G1.6 SPEC-LANDED → v3.17 G1.T1.2 IMPLEMENTATION LANDED.

Usage:
  python3 scripts/post_release_tag_validator.py --version 3.16.0
  python3 scripts/post_release_tag_validator.py --version 3.17.0 --cwd /path/to/repo
  python3 scripts/post_release_tag_validator.py --version 3.17.0 --quiet

Exit codes:
  0 = all required checks PASS (R-REL-031-03 N/A counts as PASS)
  1 = one or more required checks FAIL
"""

from __future__ import annotations

import argparse
import datetime
import subprocess
import sys
from pathlib import Path
from typing import Optional, Tuple


CheckResult = Tuple[Optional[bool], str]  # (True=PASS, False=FAIL, None=N/A, detail)


def _run(cmd: list[str], cwd: Optional[str] = None) -> Tuple[int, str, str]:
    """Run a command without shell expansion; return (rc, stdout, stderr)."""
    p = subprocess.run(cmd, cwd=cwd, capture_output=True, text=True)
    return p.returncode, p.stdout, p.stderr


def check_remote_tag(version: str, cwd: Optional[str] = None) -> CheckResult:
    """R-REL-031-01: tag reachable on remote via `git ls-remote origin v{VERSION}`."""
    rc, out, err = _run(["git", "ls-remote", "origin", f"v{version}"], cwd=cwd)
    if rc != 0:
        return False, f"git ls-remote failed: {err.strip() or '(no stderr)'}"
    if f"refs/tags/v{version}" not in out:
        return False, f"tag v{version} not present on remote (origin)"
    return True, f"tag v{version} reachable on remote (origin)"


def check_handoff_resolves(version: str, cwd: Optional[str] = None) -> CheckResult:
    """R-REL-031-02: tag resolves RELEASE_HANDOFF artifact. The #1154 invariant."""
    path = f"handoffs/RELEASE_HANDOFF_v{version}.md"
    rc, out, _ = _run(["git", "show", f"v{version}:{path}"], cwd=cwd)
    if rc != 0:
        return False, (
            f"#1154 regression — tag v{version} does not resolve {path} "
            f"(tag was likely cut before handoff artifact existed in working tree)"
        )
    if not out.strip():
        return False, f"{path} resolves at tag v{version} but is empty"
    return True, f"tag v{version} resolves {path} (#1154 invariant intact)"


def check_deployment_spec_resolves(version: str, cwd: Optional[str] = None) -> CheckResult:
    """R-REL-031-03: IF DEPLOYMENT_SPEC published THEN tag resolves it (conditional).

    Tries canonical path (aget/DEPLOYMENT_SPEC_v{V}.yaml) first, then legacy path
    (DEPLOYMENT_SPEC_v{V}.yaml at repo root, per L910 path canonicalization).
    Returns N/A if no DEPLOYMENT_SPEC was published for this release.
    """
    candidates = [
        f"aget/DEPLOYMENT_SPEC_v{version}.yaml",
        f"DEPLOYMENT_SPEC_v{version}.yaml",
    ]
    for path in candidates:
        rc, _, _ = _run(["git", "show", f"v{version}:{path}"], cwd=cwd)
        if rc == 0:
            return True, f"tag v{version} resolves {path}"
    return None, (
        f"DEPLOYMENT_SPEC_v{version}.yaml not tag-resolvable at canonical or legacy path "
        f"(N/A if release did not publish a deployment spec)"
    )


def check_tag_annotation(version: str, cwd: Optional[str] = None) -> CheckResult:
    """R-REL-031-04: tag annotation includes version string + non-empty release-notes pointer."""
    rc, out, err = _run(["git", "cat-file", "-p", f"v{version}"], cwd=cwd)
    if rc != 0:
        return False, f"git cat-file v{version} failed: {err.strip() or '(no stderr)'}"
    # Annotated tag object format: header lines, blank line, message body.
    # Lightweight tags have no annotation object — cat-file returns commit object instead.
    if not out.startswith("object "):
        return False, f"v{version} appears to be a lightweight tag (no annotation object)"
    parts = out.split("\n\n", 1)
    if len(parts) < 2 or not parts[1].strip():
        return False, f"tag v{version} annotation has empty message body"
    message = parts[1].strip()
    if version not in message:
        return False, f"tag annotation does not include version string '{version}'"
    # Release-notes pointer heuristic: URL, release-notes/ path, or RELEASE_HANDOFF reference.
    pointers = ["http://", "https://", "release-notes/", "RELEASE_HANDOFF"]
    if not any(p in message for p in pointers):
        return False, (
            "tag annotation lacks release-notes pointer "
            "(expected URL, release-notes/ path, or RELEASE_HANDOFF reference)"
        )
    return True, "tag annotation includes version + release-notes pointer"


def emit_audit(
    version: str,
    results: dict[str, CheckResult],
    audit_path: Path,
) -> None:
    """R-REL-031-05: emit per-check PASS/FAIL to audit artifact."""
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Post-Release Tag Audit — v{version}",
        "",
        f"**Date**: {datetime.date.today().isoformat()}",
        f"**Validator**: scripts/post_release_tag_validator.py (CAP-REL-031)",
        f"**Spec**: AGET_RELEASE_SPEC.md §CAP-REL-031 (R-REL-027)",
        "",
        "## Checks",
        "",
        "| Requirement | Status | Detail |",
        "|-------------|:------:|--------|",
    ]
    for check_id, (status, detail) in results.items():
        if status is True:
            label = "PASS"
        elif status is False:
            label = "FAIL"
        else:
            label = "N/A"
        lines.append(f"| {check_id} | {label} | {detail} |")
    lines.append("")
    failed = [cid for cid, (s, _) in results.items() if s is False]
    if failed:
        lines.append(f"**Overall**: FAIL ({len(failed)} check(s) failed: {', '.join(failed)})")
    else:
        lines.append("**Overall**: PASS")
    lines.append("")
    audit_path.write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Post-Release Tag Validator (CAP-REL-031, R-REL-027)",
    )
    ap.add_argument("--version", required=True, help="Released version, e.g. 3.16.0 (no leading 'v')")
    ap.add_argument("--cwd", default=None, help="Repository root (default: current directory)")
    ap.add_argument(
        "--sessions-dir",
        default="sessions",
        help="Directory for R-REL-031-05 audit emission (default: sessions/)",
    )
    ap.add_argument("--quiet", action="store_true", help="Suppress per-check stdout")
    args = ap.parse_args()

    version = args.version.lstrip("v")
    results: dict[str, CheckResult] = {}

    results["R-REL-031-01"] = check_remote_tag(version, cwd=args.cwd)
    results["R-REL-031-02"] = check_handoff_resolves(version, cwd=args.cwd)
    results["R-REL-031-03"] = check_deployment_spec_resolves(version, cwd=args.cwd)
    results["R-REL-031-04"] = check_tag_annotation(version, cwd=args.cwd)

    sessions_dir = Path(args.cwd) / args.sessions_dir if args.cwd else Path(args.sessions_dir)
    audit_path = sessions_dir / f"post_release_tag_audit_{version}_{datetime.date.today().isoformat()}.md"
    emit_audit(version, results, audit_path)
    results["R-REL-031-05"] = (audit_path.exists(), f"audit emitted to {audit_path}")

    if not args.quiet:
        for check_id, (status, detail) in results.items():
            if status is True:
                print(f"PASS {check_id}: {detail}")
            elif status is False:
                print(f"FAIL {check_id}: {detail}")
            else:
                print(f"N/A  {check_id}: {detail}")

    failed = [cid for cid, (status, _) in results.items() if status is False]
    return 1 if failed else 0


if __name__ == "__main__":
    sys.exit(main())
