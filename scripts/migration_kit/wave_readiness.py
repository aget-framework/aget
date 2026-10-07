#!/usr/bin/env python3
"""Plan v3.35, goal "Decision-record" step 8 — classify the remaining wave members' readiness.

Implements the plan's declaration ("Decision-record goal — declarations before running", step 2, as
amended before this ran). It reads the members it classifies and writes its own files under
data/<slug>_wave_baselines/ in this repository (v336_wave_baselines for 3.36.0). It also runs up to four local
scripts the kit does not ship (see LOCAL_INSTRUMENTS) and does not limit what they write.

Per member (derived from the register: all registered minus the producer, minus Agets already at
3.35.0 on disk, minus the two pilots):
  template  resolved (1) version.json `template` normalized, (2) manifest.yaml template.name,
            (3) INFERRED from version.json `archetype` (unavailable pending confirmation),
            each only if template-*-aget exists locally
            with tags v3.34.0 and v3.35.0; else evidence unavailable
  coverage  template diff v3.34.0->v3.35.0 (all statuses) + deployment-spec template paths and
            source tests + correction row 4 + version files present at the member
  privacy   private mode unless the register portfolio explicitly declares privacy: public; when unclear, private
  checks    receiver rulings (--target 3.35.0), write scope over the coverage paths, liveness,
            free-seat preflight on the repository root, register drift, dirty state
  capture   content snapshot, write-set capture, snapshot again (must be equal), pinned digest,
            immediate --verify --expect-sha256 against the untouched member
Outcomes: preservation-ready (validated capture, verify exit 0, no not-ready reason — never migration
approval, never complete semantic preservation, never lasting: revalidate before migrating),
assessed-not-ready (reason), evidence unavailable (reason).

Run from the repository root:
    python3 planning/artifacts/v3.35.0_fleet_migration/wave_readiness.py [--only NAME ...]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

import yaml

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(Path(__file__).resolve().parent))
import verify_extension_survival as V  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_target as R  # noqa: E402  (the kit's one release parameter; carriage row 24)
import copy_isolation as CI  # noqa: E402  (git_name_status: template diffs read byte for byte, B159 finding 1)

OUT = REPO / 'data' / f'{R.SLUG}_wave_baselines'
# The kit's own copy, beside this file (R-F7 follow-on): a remote supervisor has no scripts/verify_extension_survival.py.
SURVIVAL = str(Path(__file__).resolve().with_name('verify_extension_survival.py'))
PRODUCER = R.PRODUCER   # the release's producer when it is a member of this fleet; unset for a remote fleet
PILOTS = R.PILOTS
TARGET = R.TO
SPEC_PATHS = [  # core v3.35.0 DEPLOYMENT_SPEC, template surface (M-3.35-1, M-3.35-3) + source tests
    'scripts/propose_actions_handoff_scan.py', 'scripts/propose_actions_classify.py',
    '.claude/skills/aget-propose-actions/SKILL.md', 'tests/test_propose_actions_handoff_scan.py',
    'tests/test_propose_actions_outcome_gating.py', 'tests/test_propose_actions_step_2_7.py',
    'tests/test_propose_actions_classify_hardening.py', 'scripts/close_gate_check.py',
    'scripts/close_gate_lifecycle.py', 'specs/AGET_PROJECT_PLAN_SPEC.md',
    '.claude/skills/aget-close-project/SKILL.md']
CORRECTION_ROW_4 = ['scripts/close_authorization_guard.py', 'tests/test_close_authorization_guard.py']
VERSION_FILES = ['.aget/version.json', 'AGENTS.md', 'manifest.yaml', 'README.md', 'CHANGELOG.md']


def run(cmd, cwd=None):
    """Run a command and return the completed process with its output captured as text. A git command is run as a
    read that leaves the repository's git folder as it was: no optional lock, no lazy fetch (B166 finding 2; this
    tool runs only git reads)."""
    if cmd and cmd[0] == "git":
        cmd = ["git", *CI.READ_FLAGS, *cmd[1:]]
        return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd, env={**os.environ, **CI.READ_ENV})
    return subprocess.run(cmd, capture_output=True, text=True, cwd=cwd)


class EvidenceUnavailable(RuntimeError):
    """A required observation could not establish its declared subject."""


def observed(cmd, cwd=None, allowed=(0,)):
    """Run a command and return its result; raise EvidenceUnavailable if it cannot run or exits outside the allowed codes."""
    operation = next((c for c in cmd[3:] if not c.startswith('-')), '?') if cmd[0] == 'git' else Path(cmd[1]).name
    try:
        result = run(cmd, cwd=cwd)
    except OSError as exc:
        raise EvidenceUnavailable(f'{operation} unavailable: {type(exc).__name__}') from exc
    if result.returncode not in allowed:
        # Do not copy receiver paths, command output or stderr into failure summaries.
        raise EvidenceUnavailable(f'{operation} failed: exit {result.returncode}')
    return result


def indexed_rows(result, field, identity, trailing_summary=False):
    """Parse a command's JSON output and return the rows of one field keyed by identity; raise EvidenceUnavailable if malformed."""
    try:
        if trailing_summary:
            document, _ = json.JSONDecoder().raw_decode(result.stdout.lstrip())
        else:
            document = json.loads(result.stdout)
        rows = document[field]
        if not isinstance(rows, list):
            raise ValueError('rows are not a list')
        indexed = {}
        for row in rows:
            name = row[identity]
            if not isinstance(name, str) or not name or name in indexed:
                raise ValueError('missing or duplicate identity')
            indexed[name] = row
        return indexed
    except (ValueError, KeyError, TypeError) as exc:
        raise EvidenceUnavailable(f'invalid {field} observation') from exc


def resolve_template(loc):
    """Return (template, how it was found) for the Aget at this location, or (None, reason) when none is usable."""
    fw = V.framework_root()

    def usable(name):
        if not name:
            return None
        name = name if name.startswith('template-') else f'template-{name}-aget'
        repo = os.path.join(fw, name)
        tags = observed(['git', '-C', repo, 'tag']).stdout.split()
        return name if {R.FROM_TAG, R.TO_TAG} <= set(tags) else None

    try:
        vj = json.load(open(os.path.join(loc, '.aget', 'version.json')))
    except (OSError, ValueError):
        vj = {}
    t = usable(vj.get('template') if isinstance(vj.get('template'), str) else None)
    if t:
        return t, 'version.json template'
    try:
        m = yaml.safe_load(open(os.path.join(loc, 'manifest.yaml'))) or {}
        mt = (m.get('template') or {}).get('name') if isinstance(m.get('template'), dict) else None
    except (OSError, yaml.YAMLError, AttributeError):
        mt = None
    t = usable(mt)
    if t:
        return t, 'manifest.yaml template.name'
    arch = vj.get('archetype')
    t = usable(arch.replace('_', '-') if isinstance(arch, str) else None)
    if t:
        return t, f'INFERRED from archetype {arch!r}'
    return None, (f'no usable template (version.json template={vj.get("template")!r}, '
                  f'archetype={vj.get("archetype")!r})')


def coverage_paths(loc, template):
    """Return, without repeats, the paths a migration of this Aget from this template must cover."""
    fw = V.framework_root()
    try:                                  # B159 finding 1: NUL-separated, byte for byte
        records = CI.git_name_status(os.path.join(fw, template), '-M', R.FROM_TAG, R.TO_TAG)
    except CI.InspectionFailed as e:
        raise EvidenceUnavailable(f'template diff unavailable or malformed: {e}') from None
    paths = []
    for _status, ps in records:
        paths.extend(ps)                              # renames contribute both sides
    paths += SPEC_PATHS + CORRECTION_ROW_4
    paths += [p for p in VERSION_FILES if os.path.exists(os.path.join(loc, p))]
    claude = os.path.join(loc, 'CLAUDE.md')
    if os.path.isfile(claude) and not os.path.islink(claude):
        paths.append('CLAUDE.md')
    seen, out = set(), []
    for p in paths:
        if p not in seen:
            seen.add(p)
            out.append(p)
    return out


# This tool's own run (main) calls four instruments that are NOT shipped with the kit: they exist in the supervisor
# repository the readiness run was written in. The batch procedure does not call this run (membership is checked by
# hand at B0); other kit tools import this module for its functions only. A supervisor without the instruments is told
# which, before anything is written (review finding, 2026-10-01).
LOCAL_INSTRUMENTS = ('check_register_version_drift.py', 'check_receiver_version_rulings.py',
                     'check_dispatch_liveness.py', 'preflight_seat_is_free.py')


def missing_local_instruments(repo=REPO):
    """Return the names of the required local scripts that are missing from the repository."""
    return [n for n in LOCAL_INSTRUMENTS if not (repo / 'scripts' / n).is_file()]


def unavailable_run(reason):
    """Write and print an 'evidence unavailable' report with the reason, and return exit code 2."""
    report = {'target': TARGET, 'outcome': 'evidence unavailable', 'why': reason, 'members': []}
    (OUT / 'READINESS.json').write_text(json.dumps(report, indent=2) + '\n')
    print(f'evidence unavailable: {reason}', flush=True)
    return 2


def main():
    """Command-line entry point: classify the remaining wave members' readiness."""
    R.require(pin=True)
    ap = argparse.ArgumentParser()
    ap.add_argument('--only', nargs='*')
    args = ap.parse_args()
    missing = missing_local_instruments()
    if missing:
        print('evidence unavailable: this readiness run needs instruments that are not shipped with the kit and are '
              'absent from scripts/ here: ' + ', '.join(missing) + '. Nothing was written. Check membership by hand '
              '(procedure step B0).', flush=True)
        return 2
    OUT.mkdir(parents=True, exist_ok=True)

    fleet = yaml.safe_load((REPO / '.aget/fleet/FLEET_STATE.yaml').read_text())['fleet']
    try:
        drift = indexed_rows(observed(
            [sys.executable, 'scripts/check_register_version_drift.py', '--json'],
            cwd=REPO, allowed=(0, 1)), 'seats', 'seat', trailing_summary=True)
        versions = {name: (row.get('disk'), row.get('register')) for name, row in drift.items()}
        rulings = indexed_rows(observed(
            [sys.executable, 'scripts/check_receiver_version_rulings.py', '--target', TARGET, '--json'],
            cwd=REPO, allowed=(0, 1)), 'rows', 'seat')
    except EvidenceUnavailable as exc:
        return unavailable_run(str(exc))

    members = []
    for pid, p in fleet.items():
        for a in p.get('agents') or []:
            name = a['agent_name']
            disk = versions.get(name, (None, None))[0]
            if name == PRODUCER or name in PILOTS or disk == TARGET:
                continue
            if args.only and name not in args.only:
                continue
            members.append((name, pid, os.path.realpath(os.path.expanduser(a['location']))))
    try:
        live = indexed_rows(observed(
            [sys.executable, 'scripts/check_dispatch_liveness.py', '--seats',
             *[m[0] for m in members], '--json'], cwd=REPO, allowed=(0, 1)), 'seats', 'name')
    except EvidenceUnavailable as exc:
        return unavailable_run(str(exc))

    results = []
    for name, pid, loc in sorted(members, key=lambda m: m[0].lower()):
        private = (fleet.get(pid) or {}).get('privacy') != 'public'
        rec = {'aget': name, 'mode': 'private' if private else 'text',
               'disk': versions.get(name, ('?', '?'))[0],
               'register': versions.get(name, ('?', '?'))[1]}
        reasons, unavailable = [], []
        try:
            root = observed(['git', '-C', loc, 'rev-parse', '--show-toplevel']).stdout.strip()
            if not os.path.isabs(root) or os.path.commonpath([loc, root]) != root:
                raise EvidenceUnavailable('repository root is missing or does not contain member')
            if name not in versions or versions[name][0] in (None, '?', 'UNKNOWN'):
                raise EvidenceUnavailable('member version observation missing or unknown')
            template, route = resolve_template(loc)
            rec['template'], rec['template_route'] = template, route
            ruling = rulings.get(name)
            if not isinstance(ruling, dict) or not isinstance(ruling.get('blocking'), list):
                raise EvidenceUnavailable('member ruling observation missing or malformed')
            if ruling.get('blocking'):
                reasons.append(f'a receiver ruling holds {R.TO}')
            rec['write_scope_form'] = ruling.get('write_scope_form')
            state = live.get(name, {}).get('state', 'UNKNOWN')
            rec['liveness'] = state
            if state in ('OCCUPIED', 'RECENT-WRITE'):
                reasons.append(f'liveness {state}')
            elif state != 'CLEAR':
                unavailable.append(f'liveness {state}')
            pre = observed([sys.executable, 'scripts/preflight_seat_is_free.py', root],
                           cwd=REPO, allowed=(0, 1, 2))
            rec['preflight_exit'] = pre.returncode
            if pre.returncode == 1:
                reasons.append('preflight: signal of concurrent activity')
            elif pre.returncode == 2:
                unavailable.append('preflight cannot tell')
            # R1-T12: a read; the global option keeps git from refreshing and rewriting the member's index
            dirty = observed(['git', '-C', loc, '--no-optional-locks', 'status', '--porcelain']).stdout.splitlines()
            rec['dirty_paths'] = len(dirty)
            if dirty:
                reasons.append(f'dirty tree: {len(dirty)} path(s)')
            if route.startswith('INFERRED'):
                unavailable.append('template identity inferred; confirmation required before capture')
            if not template:
                unavailable.append(route)
            if unavailable:
                raise EvidenceUnavailable('; '.join(unavailable))
            else:
                cov = coverage_paths(loc, template)
                rec['coverage_paths'] = len(cov)
                rel = os.path.relpath(loc, root)
                scope = observed([sys.executable, str(Path(__file__).resolve().parent / 'check_receiver_write_scope.py'), '--json', root,
                                  *[p if rel == '.' else os.path.join(rel, p) for p in cov]],
                                 cwd=REPO, allowed=(0, 1, 2))
                rec['write_scope_exit'] = scope.returncode
                if scope.returncode == 1:
                    reasons.append('write scope forbids some migration paths')
                elif scope.returncode not in (0,):
                    unavailable.append(f'write-scope check exit {scope.returncode}')
                try:
                    scope_data = json.loads(scope.stdout)
                    planned = [p if rel == '.' else os.path.join(rel, p) for p in cov]
                    if (os.path.realpath(scope_data['root']) != os.path.realpath(root)
                            or scope_data['paths'] != planned
                            or scope_data['exit_code'] != scope.returncode):
                        raise ValueError('scope subject mismatch')
                    expected = {0: ('inside_scope', 'unrestricted'),
                                1: ('outside_scope',), 2: ('unverifiable',)}
                    if scope_data['verdict'] not in expected.get(scope.returncode, ()):
                        raise ValueError('scope verdict not positive or known negative')
                except (ValueError, KeyError, TypeError) as exc:
                    raise EvidenceUnavailable('scope result unavailable or unbound') from exc
                if unavailable:
                    raise EvidenceUnavailable('; '.join(unavailable))
                covfile = OUT / f'{name}.coverage.json'
                covfile.write_text(json.dumps({
                    'schema': V.COVERAGE_SCHEMA, 'seat': name, 'template': template,
                    'template_route': route,
                    'declared_in': f'the fleet migration plan for {R.TO_TAG}, Decision-record goal, step 2',
                    'paths': cov}, indent=2) + '\n')
                before = V.content_snapshot(loc)[0]
                base = OUT / f'{name}.writeset.json'
                cap = run([sys.executable, SURVIVAL, name, '--capture',
                           str(base), '--coverage', str(covfile), *(['--private'] if private else [])],
                          cwd=REPO)
                after = V.content_snapshot(loc)[0]
                rec['capture_exit'] = cap.returncode
                if cap.returncode != 0:
                    unavailable.append(f'capture exit {cap.returncode}')
                elif before != after:
                    base.unlink()
                    unavailable.append('member changed during capture; capture discarded')
                else:
                    digest = hashlib.sha256(base.read_bytes()).hexdigest()
                    rec['snapshot'], rec['baseline_sha256'] = before, digest
                    ver = run([sys.executable, SURVIVAL, name,
                               '--verify', str(base), '--expect-sha256', digest], cwd=REPO)
                    rec['verify_exit'] = ver.returncode
                    if ver.returncode == 3:
                        reasons.append('no receiver-authored lines captured; the check would establish nothing')
                    elif ver.returncode != 0:
                        unavailable.append(f'immediate verify exit {ver.returncode}')
        except EvidenceUnavailable as exc:
            unavailable = [str(exc)]

        if unavailable:
            rec['outcome'], rec['why'] = 'evidence unavailable', '; '.join(unavailable + reasons)
        elif reasons:
            rec['outcome'], rec['why'] = 'assessed-not-ready', '; '.join(reasons)
        else:
            rec['outcome'], rec['why'] = 'preservation-ready', (
                'validated capture of the declared coverage; revalidate before migrating')
        results.append(rec)
        print(f'{name:<42} {rec["outcome"]:<22} {rec["why"][:110]}', flush=True)

    (OUT / 'READINESS.json').write_text(json.dumps(
        {'target': TARGET, 'members': results}, indent=2, sort_keys=True) + '\n')
    from collections import Counter
    print(dict(Counter(r['outcome'] for r in results)))


if __name__ == '__main__':
    raise SystemExit(main())
