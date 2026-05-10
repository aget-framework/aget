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


# Default 14-repo list (aget + 13 templates). Same as
# post_release_changelog_validator.py — symmetry per F-V317-G1-CRITIC-019
# closure (CAP-REL-030/031 enumeration parity).
RELEASE_REPOS_DEFAULT = [
    "aget",
    "template-advisor-aget",
    "template-analyst-aget",
    "template-architect-aget",
    "template-consultant-aget",
    "template-developer-aget",
    "template-executive-aget",
    "template-operator-aget",
    "template-researcher-aget",
    "template-reviewer-aget",
    "template-spec-engineer-aget",
    "template-supervisor-aget",
    "template-worker-aget",
    "template-document-processor-AGET",
]


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


def check_handoff_resolves(
    version: str, cwd: Optional[str] = None, repo_name: Optional[str] = None
) -> CheckResult:
    """R-REL-031-02: tag resolves RELEASE_HANDOFF artifact. The #1154 invariant.

    Per AGET_RELEASE_SPEC.md §CAP-REL-031 R-REL-031-02: "for the framework repo (aget/)".
    Non-aget repos return N/A (handoffs/ artifacts live only at aget/ core).
    """
    if repo_name is not None and repo_name != "aget":
        return None, f"N/A — R-REL-031-02 applies to aget/ core only (not {repo_name})"
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


def emit_audit_multi_repo(
    version: str,
    per_repo: dict[str, dict[str, CheckResult]],
    audit_path: Path,
) -> None:
    """R-REL-031-05: emit aggregated per-repo PASS/FAIL to audit artifact."""
    audit_path.parent.mkdir(parents=True, exist_ok=True)
    lines = [
        f"# Post-Release Tag Audit — v{version}",
        "",
        f"**Date**: {datetime.date.today().isoformat()}",
        f"**Validator**: scripts/post_release_tag_validator.py (CAP-REL-031)",
        f"**Spec**: AGET_RELEASE_SPEC.md §CAP-REL-031 (R-REL-027)",
        f"**Repos**: {len(per_repo)} ({', '.join(per_repo.keys())})",
        "",
        "## Per-Repo Results",
        "",
        "| Repo | R-REL-031-01 | R-REL-031-02 | R-REL-031-03 | R-REL-031-04 | Overall |",
        "|------|:------------:|:------------:|:------------:|:------------:|:-------:|",
    ]
    for repo, checks in per_repo.items():
        cells = []
        any_fail = False
        for cid in ("R-REL-031-01", "R-REL-031-02", "R-REL-031-03", "R-REL-031-04"):
            status, _ = checks.get(cid, (False, "missing"))
            if status is True:
                cells.append("PASS")
            elif status is False:
                cells.append("FAIL")
                any_fail = True
            else:
                cells.append("N/A")
        overall = "FAIL" if any_fail else "PASS"
        lines.append(f"| {repo} | " + " | ".join(cells) + f" | {overall} |")
    lines.append("")
    lines.append("## Failure Details")
    lines.append("")
    any_failures = False
    for repo, checks in per_repo.items():
        repo_failures = [(cid, detail) for cid, (status, detail) in checks.items() if status is False]
        if repo_failures:
            any_failures = True
            lines.append(f"### {repo}")
            lines.append("")
            for cid, detail in repo_failures:
                lines.append(f"- **{cid}**: {detail}")
            lines.append("")
    if not any_failures:
        lines.append("None — all checks passed across all repos.")
        lines.append("")
    audit_path.write_text("\n".join(lines))


def main() -> int:
    ap = argparse.ArgumentParser(
        description="Post-Release Tag Validator (CAP-REL-031, R-REL-027)",
    )
    ap.add_argument("--version", required=True, help="Released version, e.g. 3.16.0 (no leading 'v')")
    ap.add_argument(
        "--cwd",
        default=None,
        help="aget-framework root directory (default: current dir; expects sibling repos at this level)",
    )
    ap.add_argument(
        "--repos",
        default=None,
        help="Comma-separated repo list (default: 14-repo RELEASE_REPOS_DEFAULT). Closes F-V317-G1-CRITIC-009 + F-V317-G1-CRITIC-019; symmetry with post_release_changelog_validator.py per CAP-REL-030/031 parity.",
    )
    ap.add_argument(
        "--sessions-dir",
        default="sessions",
        help="Directory for R-REL-031-05 audit emission (default: sessions/)",
    )
    ap.add_argument("--quiet", action="store_true", help="Suppress per-check stdout")
    args = ap.parse_args()

    version = args.version.lstrip("v")
    framework_root = Path(args.cwd) if args.cwd else Path.cwd()
    repos = (
        [r.strip() for r in args.repos.split(",") if r.strip()]
        if args.repos
        else list(RELEASE_REPOS_DEFAULT)
    )

    per_repo: dict[str, dict[str, CheckResult]] = {}
    failed_overall = False

    for repo in repos:
        repo_root = framework_root / repo
        if not repo_root.exists():
            per_repo[repo] = {
                "R-REL-031-01": (False, f"repo dir not found: {repo_root}"),
                "R-REL-031-02": (False, "skipped (repo dir missing)"),
                "R-REL-031-03": (False, "skipped (repo dir missing)"),
                "R-REL-031-04": (False, "skipped (repo dir missing)"),
            }
            failed_overall = True
            continue
        per_repo[repo] = {
            "R-REL-031-01": check_remote_tag(version, cwd=str(repo_root)),
            "R-REL-031-02": check_handoff_resolves(version, cwd=str(repo_root), repo_name=repo),
            "R-REL-031-03": check_deployment_spec_resolves(version, cwd=str(repo_root)),
            "R-REL-031-04": check_tag_annotation(version, cwd=str(repo_root)),
        }
        if any(s is False for s, _ in per_repo[repo].values()):
            failed_overall = True

    # Audit emission path resolution. Closes F-V317-G1-B3-CRITIC-001 (sessions/
    # pollution at framework-root): when --cwd points to a directory without
    # .aget/ marker (i.e., framework-root level), require explicit --sessions-dir
    # rather than auto-creating sessions/ at that level.
    cwd_has_aget = (framework_root / ".aget").exists()
    sessions_dir_path = Path(args.sessions_dir)
    if sessions_dir_path.is_absolute():
        sessions_dir = sessions_dir_path
    elif cwd_has_aget:
        sessions_dir = framework_root / sessions_dir_path
    elif args.sessions_dir != "sessions":
        # Caller explicitly specified non-default; honor it relative to framework_root
        sessions_dir = framework_root / sessions_dir_path
    else:
        # Framework-root cwd + default sessions-dir = ambiguous. Refuse rather than
        # pollute framework_root/sessions/ (which is no agent's owned tree).
        print(
            "ERROR: --cwd points to a path without .aget/ (framework-root level) "
            "and --sessions-dir defaulted to 'sessions'. This would create "
            f"'{framework_root}/sessions/' which is outside any agent's session tree. "
            "Specify --sessions-dir explicitly (absolute path OR a path you intend "
            "to live under framework_root).",
            file=sys.stderr,
        )
        return 2
    audit_path = sessions_dir / f"post_release_tag_audit_{version}_{datetime.date.today().isoformat()}.md"
    emit_audit_multi_repo(version, per_repo, audit_path)

    if not args.quiet:
        for repo, checks in per_repo.items():
            for cid, (status, detail) in checks.items():
                if status is True:
                    print(f"PASS {repo}/{cid}: {detail}")
                elif status is False:
                    print(f"FAIL {repo}/{cid}: {detail}")
                else:
                    print(f"N/A  {repo}/{cid}: {detail}")
        print(f"\nAudit emitted: {audit_path}")

    return 1 if failed_overall else 0


if __name__ == "__main__":
    sys.exit(main())
