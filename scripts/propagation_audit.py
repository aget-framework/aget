#!/usr/bin/env python3
"""
propagation_audit.py - Template Propagation Tracking

Per CAP-REL-024: Logs expected vs actual propagation state.
Verifies against deployment targets (template repos), not authoring workspace.

Usage:
    python3 propagation_audit.py --version 3.6.0 --check       # Verify all targets
    python3 propagation_audit.py --version 3.6.0 --record       # Record current state
    python3 propagation_audit.py --test                          # Self-test

Specification: AGET_RELEASE_SPEC.md CAP-REL-024
Source: L605 (Release Observability Gap), L596 (Propagation Gap)

Exit Codes:
    0: Success (or all targets propagated)
    1: Incomplete propagation (--check mode)
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


def get_framework_root() -> Path:
    """Find the framework root directory."""
    env_dir = os.environ.get('AGET_FRAMEWORK_DIR')
    if env_dir:
        return Path(env_dir)
    current = Path(__file__).resolve()
    if current.parent.name == 'scripts':
        candidate = current.parent.parent.parent
        if any((candidate / d).is_dir() for d in ['template-worker-aget', 'aget']):
            return candidate
    # Fallback: use parent of current working directory or cwd itself
    cwd = Path.cwd()
    if any((cwd / d).is_dir() for d in ['template-worker-aget', 'aget']):
        return cwd
    if any((cwd.parent / d).is_dir() for d in ['template-worker-aget', 'aget']):
        return cwd.parent
    return cwd


def find_template_repos(framework_root: Path) -> list:
    """Find all template repos."""
    repos = []
    for d in sorted(framework_root.iterdir()):
        if d.is_dir() and d.name.startswith('template-') and d.name.endswith('-aget'):
            repos.append(d)
    return repos


def check_version_file(repo_path: Path, expected_version: str) -> dict:
    """Check if repo's version.json matches expected version."""
    for vpath in [repo_path / '.aget' / 'version.json', repo_path / 'version.json']:
        if vpath.is_file():
            try:
                data = json.loads(vpath.read_text())
                actual = data.get('aget_version', data.get('version', 'unknown'))
                return {
                    'file': str(vpath.relative_to(repo_path)),
                    'expected': expected_version,
                    'actual': actual,
                    'match': actual == expected_version,
                }
            except Exception as e:
                return {'file': str(vpath.relative_to(repo_path)), 'error': str(e), 'match': False}
    return {'file': 'version.json', 'error': 'not_found', 'match': False}


def check_changelog(repo_path: Path, expected_version: str) -> dict:
    """Check if CHANGELOG.md contains expected version entry."""
    changelog = repo_path / 'CHANGELOG.md'
    if not changelog.is_file():
        return {'file': 'CHANGELOG.md', 'error': 'not_found', 'match': False}
    try:
        content = changelog.read_text(encoding='utf-8')
        has_entry = expected_version in content
        return {
            'file': 'CHANGELOG.md',
            'expected': expected_version,
            'match': has_entry,
        }
    except Exception as e:
        return {'file': 'CHANGELOG.md', 'error': str(e), 'match': False}


def check_ontology_dir(repo_path: Path) -> dict:
    """Check if ontology/ directory exists with YAML files."""
    ont_dir = repo_path / 'ontology'
    if not ont_dir.is_dir():
        return {'exists': False, 'yaml_count': 0}
    yaml_count = len([f for f in ont_dir.iterdir() if f.suffix in ('.yaml', '.yml')])
    return {'exists': True, 'yaml_count': yaml_count}


def check_canonical_scripts(repo_path: Path) -> dict:
    """Check if canonical session scripts exist in scripts/.

    These are Framework_Artifacts that must be present in every template.
    Per L598/L599: scripts/ is the canonical deployment target.
    """
    canonical = ['wake_up.py', 'wind_down.py', 'study_up.py']
    scripts_dir = repo_path / 'scripts'
    present = []
    missing = []
    for script in canonical:
        if (scripts_dir / script).is_file():
            present.append(script)
        else:
            missing.append(script)
    return {
        'present': present,
        'missing': missing,
        'complete': len(missing) == 0,
    }


def check_skill_script_refs(repo_path: Path) -> dict:
    """Check that every skill's script references resolve to existing files.

    Per L607 (Referential Integrity): propagating a skill definition without
    its implementing script causes the skill to fail for users.
    """
    skills_dir = repo_path / '.claude' / 'skills'
    if not skills_dir.is_dir():
        return {'checked': 0, 'broken': [], 'complete': True}

    broken = []
    checked = 0
    for skill_dir in sorted(skills_dir.iterdir()):
        skill_md = skill_dir / 'SKILL.md'
        if not skill_md.is_file():
            continue
        try:
            content = skill_md.read_text(encoding='utf-8')
        except Exception:
            continue

        # Find script references: python3 scripts/X.py or python3 .aget/patterns/*/X.py
        for match in re.finditer(r'python3\s+(scripts/\S+\.py|\.aget/patterns/\S+\.py)', content):
            script_ref = match.group(1)
            checked += 1
            if not (repo_path / script_ref).is_file():
                broken.append({
                    'skill': skill_dir.name,
                    'reference': script_ref,
                })

    return {
        'checked': checked,
        'broken': broken,
        'complete': len(broken) == 0,
    }


def audit_propagation(version: str, framework_root: Path) -> dict:
    """Audit propagation across all template repos (CAP-REL-024-01 through 024-04)."""
    repos = find_template_repos(framework_root)

    record = {
        'timestamp': datetime.now(timezone.utc).isoformat(),
        'aget_version': version,
        'source_repo': 'aget',
        'targets': [],
        'all_complete': True,
    }

    for repo in repos:
        target = {
            'repo': repo.name,
            'checks': {},
            'complete': True,
            'missing': [],
        }

        # Check version file
        ver_check = check_version_file(repo, version)
        target['checks']['version_json'] = ver_check
        if not ver_check['match']:
            target['complete'] = False
            target['missing'].append('version_json')

        # Check changelog
        cl_check = check_changelog(repo, version)
        target['checks']['changelog'] = cl_check
        if not cl_check['match']:
            target['complete'] = False
            target['missing'].append('changelog')

        # Check ontology directory
        ont_check = check_ontology_dir(repo)
        target['checks']['ontology'] = ont_check
        if not ont_check['exists']:
            target['complete'] = False
            target['missing'].append('ontology')

        # Check canonical scripts (L598/L599)
        scripts_check = check_canonical_scripts(repo)
        target['checks']['canonical_scripts'] = scripts_check
        if not scripts_check['complete']:
            target['complete'] = False
            target['missing'].append(f"scripts({','.join(scripts_check['missing'])})")

        # Check skill→script referential integrity (L607)
        refs_check = check_skill_script_refs(repo)
        target['checks']['skill_script_refs'] = refs_check
        if not refs_check['complete']:
            target['complete'] = False
            for b in refs_check['broken']:
                target['missing'].append(f"ref({b['skill']}→{b['reference']})")

        if not target['complete']:
            record['all_complete'] = False

        record['targets'].append(target)

    return record


def get_log_path(agent_path: Path = None) -> Path:
    """Get the propagation log path."""
    if agent_path is None:
        agent_path = Path.cwd()
    log_dir = agent_path / '.aget' / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)
    return log_dir / 'propagation_log.jsonl'


def run_self_test() -> bool:
    """Self-test for propagation_audit.py."""
    import tempfile
    import shutil

    test_dir = Path(tempfile.mkdtemp(prefix='aget_propagation_test_'))
    passed = 0
    failed = 0

    try:
        # Create mock framework with 2 template repos
        t1 = test_dir / 'template-worker-aget'
        t1.mkdir()
        (t1 / '.aget').mkdir()
        (t1 / '.aget' / 'version.json').write_text(json.dumps({'aget_version': '3.6.0'}))
        (t1 / 'CHANGELOG.md').write_text('## v3.6.0\n- Changes\n')
        (t1 / 'ontology').mkdir()
        (t1 / 'ontology' / 'ONTOLOGY_worker.yaml').write_text('kind: OntologySpec\n')
        (t1 / 'scripts').mkdir()
        for s in ['wake_up.py', 'wind_down.py', 'study_up.py']:
            (t1 / 'scripts' / s).write_text(f'# {s}\n')

        t2 = test_dir / 'template-advisor-aget'
        t2.mkdir()
        (t2 / '.aget').mkdir()
        (t2 / '.aget' / 'version.json').write_text(json.dumps({'aget_version': '3.5.0'}))
        # No changelog, no ontology

        # T1: Complete repo passes
        record = audit_propagation('3.6.0', test_dir)
        worker = next(t for t in record['targets'] if t['repo'] == 'template-worker-aget')
        if worker['complete']:
            print("  [+] T1 PASS: Complete repo detected as complete")
            passed += 1
        else:
            print(f"  [-] T1 FAIL: Expected complete; missing={worker['missing']}")
            failed += 1

        # T2: Incomplete repo detected
        advisor = next(t for t in record['targets'] if t['repo'] == 'template-advisor-aget')
        if not advisor['complete'] and 'version_json' in advisor['missing']:
            print("  [+] T2 PASS: Incomplete repo detected with missing items")
            passed += 1
        else:
            print(f"  [-] T2 FAIL: Expected incomplete; complete={advisor['complete']}")
            failed += 1

        # T3: all_complete is false when any target incomplete
        if not record['all_complete']:
            print("  [+] T3 PASS: all_complete=false when incomplete target exists")
            passed += 1
        else:
            print(f"  [-] T3 FAIL: Expected all_complete=false")
            failed += 1

        # T4: Canonical scripts check
        t3_scripts = test_dir / 'template-scripts-aget'
        t3_scripts.mkdir()
        (t3_scripts / '.aget').mkdir()
        (t3_scripts / 'scripts').mkdir()
        (t3_scripts / 'scripts' / 'wake_up.py').write_text('# wake up\n')
        (t3_scripts / 'scripts' / 'wind_down.py').write_text('# wind down\n')
        # Missing study_up.py
        sc = check_canonical_scripts(t3_scripts)
        if not sc['complete'] and 'study_up.py' in sc['missing']:
            print("  [+] T4 PASS: Missing canonical script detected")
            passed += 1
        else:
            print(f"  [-] T4 FAIL: Expected missing study_up.py; missing={sc['missing']}")
            failed += 1

        # T5: Skill→script referential integrity
        t4_refs = test_dir / 'template-refs-aget'
        t4_refs.mkdir()
        (t4_refs / '.claude' / 'skills' / 'test-skill').mkdir(parents=True)
        (t4_refs / '.claude' / 'skills' / 'test-skill' / 'SKILL.md').write_text(
            '# Test\n```bash\npython3 scripts/missing_script.py\n```\n'
        )
        rc = check_skill_script_refs(t4_refs)
        if not rc['complete'] and any(b['reference'] == 'scripts/missing_script.py' for b in rc['broken']):
            print("  [+] T5 PASS: Broken skill→script reference detected")
            passed += 1
        else:
            print(f"  [-] T5 FAIL: Expected broken ref; broken={rc['broken']}")
            failed += 1

        # T6: Skill with valid script passes
        (t4_refs / 'scripts').mkdir()
        (t4_refs / 'scripts' / 'missing_script.py').write_text('# now exists\n')
        rc2 = check_skill_script_refs(t4_refs)
        if rc2['complete']:
            print("  [+] T6 PASS: Valid skill→script reference passes")
            passed += 1
        else:
            print(f"  [-] T6 FAIL: Expected complete; broken={rc2['broken']}")
            failed += 1

        # T7: Record serializable to JSONL
        try:
            line = json.dumps(record) + '\n'
            parsed = json.loads(line.strip())
            if parsed['aget_version'] == '3.6.0':
                print("  [+] T7 PASS: Record serializes to JSONL")
                passed += 1
            else:
                print(f"  [-] T7 FAIL: Version mismatch after serialization")
                failed += 1
        except Exception as e:
            print(f"  [-] T7 FAIL: Serialization error: {e}")
            failed += 1

    finally:
        shutil.rmtree(test_dir)

    total = passed + failed
    print(f"\n  Self-test: {passed}/{total} PASS")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description='Template Propagation Tracking (CAP-REL-024)',
    )
    parser.add_argument('--version', help='Release version to check (e.g., 3.6.0)')
    parser.add_argument('--check', action='store_true', help='Check propagation and report')
    parser.add_argument('--record', action='store_true', help='Record propagation state to log')
    parser.add_argument('--framework-dir', type=Path, help='Framework root directory')
    parser.add_argument('--test', action='store_true', help='Run self-test')
    args = parser.parse_args()

    if args.test:
        print("propagation_audit.py self-test (CAP-REL-024)")
        success = run_self_test()
        sys.exit(0 if success else 1)

    if not args.version:
        parser.error("--version is required")

    framework_root = args.framework_dir or get_framework_root()
    record = audit_propagation(args.version, framework_root)

    if args.record:
        log_path = get_log_path()
        with open(log_path, 'a') as f:
            f.write(json.dumps(record) + '\n')
        print(f"Propagation record written to: {log_path}")

    # Report
    complete_count = sum(1 for t in record['targets'] if t['complete'])
    total_count = len(record['targets'])

    print(f"\nPropagation Audit: v{args.version}")
    print(f"Targets: {complete_count}/{total_count} complete")

    for target in record['targets']:
        status = 'OK' if target['complete'] else f"INCOMPLETE ({', '.join(target['missing'])})"
        print(f"  {target['repo']}: {status}")

    if record['all_complete']:
        print(f"\nPASS: All targets propagated")
    else:
        incomplete = [t['repo'] for t in record['targets'] if not t['complete']]
        print(f"\nFAIL: {len(incomplete)} target(s) incomplete")

    if args.check and not record['all_complete']:
        sys.exit(1)


if __name__ == '__main__':
    main()
