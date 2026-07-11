#!/usr/bin/env python3
"""
check_tag_payload_coherence.py — Tag-Payload Coherence Gate (v3.26 C-26-03, gh#1834)

Detects the verified 3-instance class from v3.25.0: post-tag repairs landing on
main leave the tag payload silently divergent while migrating fleets fetch AT
THE TAG (codemeta/CITATION stale at tag; DEPLOYMENT_SPEC back-filled on main;
migration-message hardening notes not tag-reachable — recursively including the
note that said where to find the fix).

Two rules enforced (gh#1834 layers):
  1. PREVENTION (advisory here, ordering lives in SOP Phase 3.6): computed DoD
     full-green precedes TAG CREATION, not merely release-close.
  2. DISCLOSURE: WHEN any commit touches release-coupled artifacts after the
     version tag, the GitHub release body SHALL carry a post-tag-repairs
     section same-day (v3.25.0's 2026-07-05 body edit is the exemplar).

Reporting follows the three-state check contract (v3.26 C-26-09,
docs/CONVENTION_check_three_state_contract.md): PASS / FAIL / UNREACHABLE —
UNREACHABLE (no tag, no git, gh absent) is distinct and non-gating.

Usage:
  python3 scripts/check_tag_payload_coherence.py --version 3.25.0
  python3 scripts/check_tag_payload_coherence.py --version 3.26.0 --cwd /path/to/repo

Exit codes: 0 = PASS (or UNREACHABLE per ADR-004 non-gating) · 2 = FAIL
"""

import argparse
import subprocess
import sys


def _run(cmd, cwd=None, timeout=30):
    return subprocess.run(cmd, capture_output=True, text=True, timeout=timeout,
                          cwd=cwd, stdin=subprocess.DEVNULL)


def release_coupled_paths(version: str):
    """Artifacts a migrating consumer reads at-tag (gh#1834 inventory + Phase 3.0 family)."""
    return [
        'codemeta.json',
        'CITATION.cff',
        f'DEPLOYMENT_SPEC_v{version}.yaml',
        f'handoffs/RELEASE_HANDOFF_v{version}.md',
        f'handoffs/REMOTE_MIGRATION_MESSAGE_v{version}.md',
        'CHANGELOG.md',
    ]


def check(version: str, cwd: str = None, repo: str = 'aget-framework/aget'):
    tag = f'v{version}'
    # Reachability: git + tag present
    r = _run(['git', 'rev-parse', '--verify', f'refs/tags/{tag}'], cwd=cwd)
    if r.returncode != 0:
        return ('UNREACHABLE', f'tag {tag} not found in this clone — cannot compare', [])

    divergent = []
    for path in release_coupled_paths(version):
        log = _run(['git', 'log', '--oneline', f'{tag}..HEAD', '--', path], cwd=cwd)
        if log.returncode == 0 and log.stdout.strip():
            commits = [ln.split()[0] for ln in log.stdout.strip().splitlines()]
            divergent.append((path, commits))

    if not divergent:
        return ('PASS', f'no post-tag commits touch release-coupled artifacts for {tag}', [])

    # Disclosure check: does the release body carry a post-tag-repairs section?
    disclosed = None  # None = unreachable, True/False = checked
    rb = _run(['gh', 'release', 'view', tag, '--repo', repo, '--json', 'body',
               '-q', '.body'], cwd=cwd, timeout=15)
    if rb.returncode == 0:
        body = rb.stdout.lower()
        disclosed = ('post-tag repair' in body or 'post-tag-repair' in body
                     or 'post-tag repairs' in body)

    if disclosed is True:
        return ('PASS', f'{len(divergent)} release-coupled path(s) diverged post-tag '
                        f'AND the release body discloses post-tag repairs (gh#1834 rule 2 satisfied)',
                divergent)
    if disclosed is None:
        return ('FAIL', f'{len(divergent)} release-coupled path(s) diverged post-tag; '
                        f'disclosure state UNREACHABLE (gh unavailable) — treat as undisclosed until verified',
                divergent)
    return ('FAIL', f'{len(divergent)} release-coupled path(s) diverged post-tag with NO '
                    f'post-tag-repairs disclosure in the release body (gh#1834 rule 2 violated)',
            divergent)


def main(argv=None):
    p = argparse.ArgumentParser(description='Tag-payload coherence gate (gh#1834, C-26-03)')
    p.add_argument('--version', required=True)
    p.add_argument('--cwd', default=None, help='repo clone to check (default: cwd)')
    p.add_argument('--repo', default='aget-framework/aget', help='GitHub repo for release-body disclosure check')
    args = p.parse_args(argv)

    state, msg, divergent = check(args.version, cwd=args.cwd, repo=args.repo)
    print(f'tag-payload-coherence v{args.version}: {state} — {msg}')
    for path, commits in divergent:
        print(f'  - {path}: {len(commits)} post-tag commit(s): {", ".join(commits[:5])}')
    # Three-state contract: UNREACHABLE is non-gating (ADR-004); FAIL gates.
    return 2 if state == 'FAIL' else 0


if __name__ == '__main__':
    sys.exit(main())
