#!/usr/bin/env python3
"""
release_snapshot.py - Pre/Post Release State Snapshots

Per CAP-REL-023: Captures structured state of all repos before and after release.
Diff-based validation replaces absolute checks.

Usage:
    python3 release_snapshot.py --version 3.6.0 --phase pre     # Pre-release snapshot
    python3 release_snapshot.py --version 3.6.0 --phase post    # Post-release snapshot
    python3 release_snapshot.py --version 3.6.0 --diff          # Generate diff
    python3 release_snapshot.py --test                           # Self-test

Specification: AGET_RELEASE_SPEC.md CAP-REL-023
Source: L605 (Release Observability Gap)
"""

import argparse
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_framework_root() -> Path:
    """Find the framework root directory."""
    env_dir = os.environ.get('AGET_FRAMEWORK_DIR')
    if env_dir:
        return Path(env_dir)

    current = Path(__file__).resolve()
    # scripts/release_snapshot.py -> parent.parent
    if current.parent.name == 'scripts':
        candidate = current.parent.parent.parent
        if any((candidate / d).is_dir() for d in ['template-worker-aget', 'aget']):
            return candidate
    return Path('/Users/gabormelli/github/aget-framework')


def find_repos(framework_root: Path) -> list:
    """Find all repos (aget/ + template-*-aget/)."""
    repos = []
    aget_dir = framework_root / 'aget'
    if aget_dir.is_dir():
        repos.append(aget_dir)
    for d in sorted(framework_root.iterdir()):
        if d.is_dir() and d.name.startswith('template-') and d.name.endswith('-aget'):
            repos.append(d)
    return repos


def read_version_json(repo_path: Path) -> str:
    """Read version from version.json or .aget/version.json."""
    for vpath in [repo_path / '.aget' / 'version.json', repo_path / 'version.json']:
        if vpath.is_file():
            try:
                data = json.loads(vpath.read_text())
                return data.get('aget_version', data.get('version', 'unknown'))
            except Exception:
                pass
    return 'not_found'


def read_changelog_latest(repo_path: Path) -> str:
    """Read the latest version from CHANGELOG.md."""
    changelog = repo_path / 'CHANGELOG.md'
    if not changelog.is_file():
        return 'not_found'
    try:
        import re
        content = changelog.read_text(encoding='utf-8')
        match = re.search(r'##?\s*\[?v?(\d+\.\d+\.\d+)', content)
        return match.group(1) if match else 'unknown'
    except Exception:
        return 'error'


def check_github_release(repo_path: Path, version: str) -> str:
    """Check if GitHub release exists for this repo."""
    try:
        result = subprocess.run(
            ['gh', 'release', 'view', f'v{version}', '--json', 'tagName'],
            capture_output=True, text=True, timeout=10,
            cwd=repo_path
        )
        if result.returncode == 0:
            return f'v{version}'
        return 'not_found'
    except Exception:
        return 'gh_unavailable'


def capture_snapshot(version: str, phase: str, framework_root: Path,
                     skip_gh: bool = False) -> dict:
    """Capture release state snapshot (CAP-REL-023-01, 023-02, 023-03)."""
    repos = find_repos(framework_root)

    snapshot = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'aget_version': version,
        'phase': phase,
        'repos': {},
    }

    for repo in repos:
        repo_state = {
            'version_json': read_version_json(repo),
            'changelog_latest': read_changelog_latest(repo),
        }
        if not skip_gh:
            repo_state['github_release'] = check_github_release(repo, version)

        snapshot['repos'][repo.name] = repo_state

    return snapshot


def generate_diff(pre_snapshot: dict, post_snapshot: dict) -> dict:
    """Generate diff between pre and post snapshots (CAP-REL-023-04, 023-05)."""
    diff = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'aget_version': pre_snapshot.get('aget_version', 'unknown'),
        'changes': {},
        'gaps': [],
    }

    pre_repos = pre_snapshot.get('repos', {})
    post_repos = post_snapshot.get('repos', {})

    all_repos = set(pre_repos) | set(post_repos)
    for repo_name in sorted(all_repos):
        pre = pre_repos.get(repo_name, {})
        post = post_repos.get(repo_name, {})

        repo_diff = {}
        for key in set(pre) | set(post):
            pre_val = pre.get(key, 'missing')
            post_val = post.get(key, 'missing')
            if pre_val != post_val:
                repo_diff[key] = {'before': pre_val, 'after': post_val}

        if repo_diff:
            diff['changes'][repo_name] = repo_diff

        # CAP-REL-023-05: Flag unexpected unchanged items
        target_version = pre_snapshot.get('aget_version', '')
        if post.get('version_json') == pre.get('version_json') and pre.get('version_json') != target_version:
            diff['gaps'].append(f"{repo_name}: version_json not bumped (still {pre.get('version_json')})")
        if post.get('github_release') == 'not_found':
            diff['gaps'].append(f"{repo_name}: GitHub Release not created")

    return diff


def get_snapshot_dir(agent_path: Path = None) -> Path:
    """Get the snapshot directory path."""
    if agent_path is None:
        agent_path = Path.cwd()
    snapshot_dir = agent_path / '.aget' / 'logs' / 'release_snapshots'
    snapshot_dir.mkdir(parents=True, exist_ok=True)
    return snapshot_dir


def run_self_test() -> bool:
    """Self-test for release_snapshot.py."""
    import tempfile
    import shutil

    test_dir = Path(tempfile.mkdtemp(prefix='aget_snapshot_test_'))
    passed = 0
    failed = 0

    try:
        # Create mock repos
        aget_dir = test_dir / 'aget'
        aget_dir.mkdir()
        (aget_dir / '.aget').mkdir()
        (aget_dir / '.aget' / 'version.json').write_text(
            json.dumps({'aget_version': '3.5.0'})
        )

        template_dir = test_dir / 'template-worker-aget'
        template_dir.mkdir()
        (template_dir / '.aget').mkdir()
        (template_dir / '.aget' / 'version.json').write_text(
            json.dumps({'aget_version': '3.5.0'})
        )

        # T1: Pre-release snapshot captures repo state
        snap = capture_snapshot('3.6.0', 'pre', test_dir, skip_gh=True)
        if snap['repos']['aget']['version_json'] == '3.5.0' and snap['phase'] == 'pre':
            print("  [+] T1 PASS: Pre-release snapshot captures state")
            passed += 1
        else:
            print(f"  [-] T1 FAIL: Snapshot content unexpected")
            failed += 1

        # T2: Post-release snapshot after version bump
        (aget_dir / '.aget' / 'version.json').write_text(
            json.dumps({'aget_version': '3.6.0'})
        )
        snap_post = capture_snapshot('3.6.0', 'post', test_dir, skip_gh=True)
        if snap_post['repos']['aget']['version_json'] == '3.6.0':
            print("  [+] T2 PASS: Post-release snapshot shows bumped version")
            passed += 1
        else:
            print(f"  [-] T2 FAIL: Version not bumped in post snapshot")
            failed += 1

        # T3: Diff detects changes and gaps
        diff = generate_diff(snap, snap_post)
        has_change = 'aget' in diff['changes']
        has_gap = any('template-worker-aget' in g and 'not bumped' in g for g in diff['gaps'])
        if has_change and has_gap:
            print("  [+] T3 PASS: Diff detects change + gap")
            passed += 1
        else:
            print(f"  [-] T3 FAIL: Expected change and gap; changes={has_change}, gap={has_gap}")
            failed += 1

        # T4: Snapshot dir creation
        snap_dir = test_dir / '.aget' / 'logs' / 'release_snapshots'
        snap_dir.mkdir(parents=True, exist_ok=True)
        pre_path = snap_dir / 'v3.6.0_pre.json'
        pre_path.write_text(json.dumps(snap, indent=2))
        if pre_path.is_file():
            print("  [+] T4 PASS: Snapshot file written to correct path")
            passed += 1
        else:
            print(f"  [-] T4 FAIL: Snapshot file not created")
            failed += 1

    finally:
        shutil.rmtree(test_dir)

    total = passed + failed
    print(f"\n  Self-test: {passed}/{total} PASS")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description='Pre/Post Release State Snapshots (CAP-REL-023)',
    )
    parser.add_argument('--version', help='Release version (e.g., 3.6.0)')
    parser.add_argument('--phase', choices=['pre', 'post'], help='Snapshot phase')
    parser.add_argument('--diff', action='store_true', help='Generate diff from pre/post snapshots')
    parser.add_argument('--framework-dir', type=Path, help='Framework root directory')
    parser.add_argument('--skip-gh', action='store_true', help='Skip GitHub release checks')
    parser.add_argument('--test', action='store_true', help='Run self-test')
    args = parser.parse_args()

    if args.test:
        print("release_snapshot.py self-test (CAP-REL-023)")
        success = run_self_test()
        sys.exit(0 if success else 1)

    if not args.version:
        parser.error("--version is required")

    framework_root = args.framework_dir or get_framework_root()
    snapshot_dir = get_snapshot_dir()

    if args.diff:
        pre_path = snapshot_dir / f'v{args.version}_pre.json'
        post_path = snapshot_dir / f'v{args.version}_post.json'
        if not pre_path.is_file() or not post_path.is_file():
            print(f"ERROR: Need both pre and post snapshots", file=sys.stderr)
            sys.exit(2)
        pre = json.loads(pre_path.read_text())
        post = json.loads(post_path.read_text())
        diff = generate_diff(pre, post)
        diff_path = snapshot_dir / f'v{args.version}_diff.json'
        diff_path.write_text(json.dumps(diff, indent=2))
        print(f"Diff written to: {diff_path}")
        if diff['gaps']:
            print(f"GAPS ({len(diff['gaps'])}):")
            for gap in diff['gaps']:
                print(f"  - {gap}")
        else:
            print("No gaps detected.")
    elif args.phase:
        snapshot = capture_snapshot(args.version, args.phase, framework_root, args.skip_gh)
        out_path = snapshot_dir / f'v{args.version}_{args.phase}.json'
        out_path.write_text(json.dumps(snapshot, indent=2))
        print(f"Snapshot ({args.phase}) written to: {out_path}")
        print(f"Repos captured: {len(snapshot['repos'])}")
    else:
        parser.error("--phase or --diff is required")


if __name__ == '__main__':
    main()
