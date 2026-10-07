#!/usr/bin/env python3
"""Independently verify that a seat's receiver-authored lines survived its migration.

WHY THIS EXISTS. A receipt self-reports `extensions_lost`. For the one measurement
that decides whether the wave proceeds, a self-report is the weakest available
evidence: the receiver counts its own losses using its own definition of a loss.
This recomputes the answer from bytes, against a baseline captured BEFORE the
migration, with no dependence on anything the receiver said.

DEFINITION. A receiver-authored line is a non-blank line present in the seat's copy
of a payload-class file and absent from EVERY framework release of that file. Not
absent from the two endpoints — absent from all of them. A line matching an old
release is upstream-stale, not authored here, and counting it as authored is how the
first dispatch in this wave manufactured a local modification that did not exist.

USAGE
    verify_extension_survival.py <seat> --capture <file>   before the migration
    verify_extension_survival.py <seat> --verify  <file>   after it

EXIT (revised 2026-09-26, v3.35 plan "Gate 1 readiness repairs", K4-K5)
    0  every captured occurrence in the covered files is still present
    1  at least one captured occurrence lost (the lines are listed)
    2  cannot compare: the baseline belongs to another Aget, carries no identity, or the
       Aget is not in the register. Checked BEFORE comparison — a wrong baseline can read
       as false loss or false preservation, depending on overlapping content.
       Also (K8, 2026-09-26): a write-set baseline that is incomplete or malformed — the
       coverage list and the capture records do not match exactly, or a record's state is
       unknown — and any baseline whose bytes differ from --expect-sha256. Checked before
       any comparison.
    3  no coverage: the baseline captured no receiver-authored lines, so the run
       establishes nothing about preservation (neither a pass nor a loss)
    4  evidence unavailable (write-set baselines): the frozen upstream history is not exactly
       the core and the baseline's own template, has an entry with no tags, cannot be read,
       or no longer agrees with the baseline; a covered file cannot be read; or the private-
       mode key is missing or wrong
    5  no loss in the write set, but at least one path changed since capture lies OUTSIDE it
       (write-set baselines): preservation of that path is not measured, never a pass
Precedence when several hold: 2, then 1, then 4, then 5, then 3, then 0.

WRITE-SET MODE (K7, 2026-09-26): `--capture FILE --coverage COVERAGE.json [--private]`
takes its paths from the coverage file, subtracts the core's AND the pilot's template's
history (frozen as exact commits in the baseline), and binds the capture to identity,
location, HEAD, working-tree status and content digests. `--verify` on such a baseline
reports per path: retained, lost, no authored content, not covered, evidence unavailable.
`--private` stores keyed digests (key outside the repository) and never line text or a
receiver path outside the write set. `--snapshot` prints the content-snapshot aggregate.
Output is counts and scope only. Whether a migration hypothesis holds, or a wave proceeds,
is decided by the plan that reads these counts — not by this instrument. Coverage is the
files in PAYLOAD_CLASS as captured in the baseline; nothing outside them is measured.
"""
from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import release_target as R  # noqa: E402  (the kit's one place for the release and the framework root; R-F7)

# The repository the kit sits in: <root>/scripts/migration_kit/<this file>. Two folders up was `scripts/`, so the
# fleet register was looked for under scripts/.aget/fleet/ (found 2026-10-01 by a template-built supervisor).
ROOT = str(R.ROOT)
PAYLOAD_CLASS = [
    'scripts/study_topic.py',
    'scripts/health_check.py',
    'scripts/ground_artifact.py',
    '.claude/skills/aget-create-briefing/SKILL.md',
]


def sh(a):
    """Run a command and return the completed process with its output captured as text."""
    return subprocess.run(a, capture_output=True, text=True)


def seat_location(seat: str) -> str | None:
    """Return the location the fleet register records for the named Aget, or None when it is not listed."""
    import yaml
    reg = yaml.safe_load(open(os.path.join(ROOT, '.aget', 'fleet', 'FLEET_STATE.yaml')))
    for _p, sub in (reg.get('fleet') or {}).items():
        for a in sub.get('agents', []) or []:
            if a['agent_name'] == seat:
                return os.path.expanduser(a['location'])
    return None


# --- K7 write-set baselines (v3.35 plan, "K7 preparation", 2026-09-26) ---------------------------
#
# The four-file PAYLOAD_CLASS baselines cover one of the 18 paths each v3.35 pilot's template writes.
# A write-set baseline takes its paths from a coverage file, subtracts the history of the core AND of
# the pilot's template (frozen as exact commits, so a later tag cannot reclassify a line), binds the
# capture to identity, location, HEAD, working-tree status and content digests, and at verify time
# reports five classes per path plus every changed path the coverage does not name. Private mode
# keeps line text and any receiver path outside the write set out of the baseline and the output.

SCHEMA_V2 = 'aget-preservation-baseline/2'
COVERAGE_SCHEMA = 'aget-preservation-coverage/1'
DEFAULT_KEY_FILE = '~/.aget/secrets/preservation_hmac.key'
RETAINED, LOST, NO_AUTHORED = 'retained', 'lost', 'no authored content'
NOT_COVERED, UNAVAILABLE = 'not covered', 'evidence unavailable'


def framework_root() -> str:
    """Return, as a string, the folder that holds the framework's repositories."""
    return str(R.framework_root())


def core_repo() -> str:
    """The core framework clone, whose release tags hold every line a payload file has carried."""
    return os.path.join(framework_root(), 'aget')


def _git(repo, *args, text=True):
    """A git read of `repo` that leaves its git folder as it was: no optional lock, no lazy fetch (B166 finding 2;
    copy_isolation.READ_FLAGS and READ_ENV, repeated here)."""
    return subprocess.run(['git', '--no-optional-locks', '--no-lazy-fetch', '-C', repo, *args], capture_output=True,
                          text=text, env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1"})


def tag_commits(repo: str) -> list | None:
    """[[tag, commit], ...] sorted; None when the repository cannot be read."""
    r = _git(repo, 'tag')
    if r.returncode != 0:
        return None
    out = []
    for tag in sorted(r.stdout.split()):
        c = _git(repo, 'rev-parse', f'{tag}^{{commit}}')
        if c.returncode == 0:
            out.append([tag, c.stdout.strip()])
    return out


def frozen_upstream(history: list, path: str) -> set | None:
    """Every non-blank line `path` carried at any recorded commit. None = history unavailable."""
    seen = set()
    for h in history:
        repo = os.path.join(framework_root(), h['name'])
        for _tag, commit in h['tags']:
            if _git(repo, 'cat-file', '-e', f'{commit}^{{commit}}').returncode != 0:
                return None
            # B193 finding 3: an ordinary committed file only (mode 100644/100755); a link's target text is not
            # authored source, so a non-regular entry makes the history unavailable
            t = _git(repo, '--literal-pathspecs', 'ls-tree', '-z', commit, '--', path, text=False)
            if t.returncode != 0:
                return None
            names = os.fsdecode(t.stdout).split('\0')       # bytes: text mode would turn `\r` in a name into `\n`
            ent = [e.partition('\t')[0].split() for e in names if e.partition('\t')[2] == path]
            if not ent:
                continue                       # the path did not exist at that commit
            if ent[0][:2] not in (['100644', 'blob'], ['100755', 'blob']):
                return None
            r = _git(repo, 'show', f'{commit}:{path}')
            if r.returncode != 0:
                return None
            seen.update(s for s in (x.strip() for x in r.stdout.splitlines()) if s)
    return seen


def content_snapshot(repo: str):
    """The algorithm recorded in the v3.35 plan (K7 preparation), implemented independently of the
    step-1 script so the step-4 comparison also cross-checks the two. Returns
    (aggregate, tracked, untracked, {path: [kind, sha256]})."""
    import hashlib

    def listing(*args):
        r = _git(repo, 'ls-files', '-z', *args, text=False)
        return [p.decode('utf-8', 'surrogateescape') for p in r.stdout.split(b'\0') if p]

    files = {}
    for kind, paths in (('T', listing()), ('U', listing('--others', '--exclude-standard'))):
        for p in paths:
            fp = os.path.join(repo, p)
            if os.path.islink(fp):
                d = hashlib.sha256(os.readlink(fp).encode('utf-8', 'surrogateescape')).hexdigest()
            elif os.path.isfile(fp):
                with open(fp, 'rb') as fh:
                    d = hashlib.sha256(fh.read()).hexdigest()
            else:
                d = 'MISSING'
            files[p] = [kind, d]
    text = ''.join(f'{k}\t{p}\t{d}\n' for p, (k, d) in sorted(files.items()))
    agg = hashlib.sha256(text.encode('utf-8', 'surrogateescape')).hexdigest()
    return (agg, sum(1 for v in files.values() if v[0] == 'T'),
            sum(1 for v in files.values() if v[0] == 'U'), files)


class _Hasher:
    """Identity in text mode; keyed digests (HMAC-SHA256) in private mode."""

    def __init__(self, key: bytes | None):
        self.key = key

    def __call__(self, s: str) -> str:
        if self.key is None:
            return s
        import hashlib
        import hmac
        return hmac.new(self.key, s.encode('utf-8', 'surrogateescape'), hashlib.sha256).hexdigest()

    def key_id(self) -> str | None:
        import hashlib
        return None if self.key is None else hashlib.sha256(b'key-id:' + self.key).hexdigest()[:16]


def _read_key(path: str) -> bytes | None:
    try:
        with open(os.path.expanduser(path), 'rb') as fh:
            return fh.read()
    except OSError:
        return None


def _lines(fp: str) -> list:
    with open(fp, encoding='utf-8', errors='replace') as fh:
        return fh.read().splitlines()


def capture_writeset(seat, loc, coverage, private, key):
    """Build a write-set baseline. Returns (baseline, problem)."""
    import hashlib
    from collections import defaultdict
    h = _Hasher(key if private else None)
    history = []
    for name in ('aget', coverage['template']):
        tags = tag_commits(os.path.join(framework_root(), name))
        if not tags:
            return None, f'upstream history unavailable: {name} has no readable tags'
        history.append({'name': name, 'tags': tags})
    paths = {}
    for rel in coverage['paths']:
        fp = os.path.join(loc, rel)
        if not os.path.isfile(fp):
            paths[rel] = {'state': 'absent', 'authored': {}}
            continue
        up = frozen_upstream(history, rel)
        if up is None:
            return None, f'upstream history unavailable while reading {rel}'
        authored = defaultdict(lambda: {'count': 0, 'lines': []})
        for n, raw in enumerate(_lines(fp), 1):
            s = raw.strip()
            if s and s not in up:
                entry = authored[h(s)]
                entry['count'] += 1
                entry['lines'].append(n)
        with open(fp, 'rb') as fh:
            digest = hashlib.sha256(fh.read()).hexdigest()
        paths[rel] = {'state': 'present', 'sha256': h(digest) if private else digest,
                      'authored': dict(authored)}
    agg, tracked, untracked, files = content_snapshot(loc)
    head = _git(loc, 'rev-parse', 'HEAD').stdout.strip()
    porcelain = _git(loc, '--no-optional-locks', 'status', '--porcelain').stdout   # R1-T12: index not rewritten
    snap_files = {h(p): [k, h(d)] for p, (k, d) in files.items()}
    binding = {'seat': seat, 'location': os.path.realpath(loc), 'head': head,
               'porcelain': (None if private else porcelain),
               'porcelain_lines': len(porcelain.splitlines()),
               'porcelain_sha256': h(hashlib.sha256(porcelain.encode()).hexdigest()),
               'snapshot': {'aggregate': agg, 'tracked': tracked, 'untracked': untracked,
                            'files': snap_files}}
    return {'schema': SCHEMA_V2, 'seat': seat, 'mode': 'private' if private else 'text',
            'key_id': h.key_id(), 'template': coverage['template'],
            'coverage': list(coverage['paths']), 'history': history, 'binding': binding,
            'paths': paths}, None


def structure_problems(base) -> list:
    """K8 (a): coverage list and capture records match exactly, both directions; states are known.
    A record missing for a covered path would let that path's loss vanish from the report."""
    problems = []
    coverage, paths = base.get('coverage'), base.get('paths')
    if not isinstance(coverage, list) or not isinstance(paths, dict) or not coverage:
        return ['coverage list or capture records missing']
    if len(coverage) != len(set(coverage)):
        problems.append('coverage list has duplicate entries')
    for p in sorted(set(coverage) - set(paths)):
        problems.append(f'covered path without a capture record: {p}')
    for p in sorted(set(paths) - set(coverage)):
        problems.append(f'capture record without a coverage entry: {p}')
    for p, rec in paths.items():
        state = rec.get('state') if isinstance(rec, dict) else None
        if state not in ('present', 'absent'):
            problems.append(f'capture record with unknown state {state!r}: {p}')
        elif not isinstance(rec.get('authored'), dict):
            problems.append(f'capture record without an authored map: {p}')
        elif state == 'absent' and rec['authored']:
            problems.append(f'absent path with authored lines: {p}')
    return problems


def history_problems(base) -> list:
    """K8 (b): exactly the core and the baseline's own template, each with tags, every commit
    readable. An empty history would otherwise read as 'no upstream lines' and pass."""
    history = base.get('history')
    expected = ['aget', base.get('template')]
    if not isinstance(history, list) or [h.get('name') for h in history
                                         if isinstance(h, dict)] != expected:
        got = [h.get('name') for h in history if isinstance(h, dict)] \
            if isinstance(history, list) else history
        return [f'frozen history names {got!r}, expected {expected!r}']
    problems = []
    for h in history:
        tags = h.get('tags')
        if not isinstance(tags, list) or not tags:
            problems.append(f'frozen history {h["name"]!r} has no tags')
            continue
        repo = os.path.join(framework_root(), h['name'])
        for entry in tags:
            ok = (isinstance(entry, list) and len(entry) == 2 and isinstance(entry[1], str)
                  and len(entry[1]) == 40)
            if not ok or _git(repo, 'cat-file', '-e', f'{entry[1]}^{{commit}}').returncode != 0:
                problems.append(f'frozen history {h["name"]!r}: commit unreadable or malformed '
                                f'for {entry!r}')
                break
    return problems


def verify_writeset(seat, loc, base, key):
    """Print the per-path report. Returns the exit code (see the module docstring)."""
    from collections import Counter
    problems = structure_problems(base)
    if problems:
        print('REFUSED: the baseline is incomplete or malformed; nothing was compared.',
              file=sys.stderr)
        for p in problems:
            print(f'  {p}', file=sys.stderr)
        return 2
    if base.get('seat') != seat or base['binding'].get('seat') != seat:
        print(f'REFUSED: baseline belongs to {base.get("seat")!r}, not {seat!r}. '
              f'No comparison was made.', file=sys.stderr)
        return 2
    if base['binding'].get('location') != os.path.realpath(loc):
        print(f'REFUSED: baseline was captured at another location, not {loc!r}. '
              f'No comparison was made.', file=sys.stderr)
        return 2
    private = base.get('mode') == 'private'
    h = _Hasher(key if private else None)
    if private and h.key_id() != base.get('key_id'):
        print('evidence unavailable: the private-mode key does not match the baseline\'s key.')
        return 4
    problems = history_problems(base)
    if problems:
        print(f'{UNAVAILABLE}: the frozen upstream history is not usable; nothing was compared.')
        for p in problems:
            print(f'  {p}')
        return 4
    results, details, unavailable = {}, [], False
    for rel, cap in base['paths'].items():
        if not cap['authored']:
            results[rel] = (NO_AUTHORED, 0, 0)
            continue
        up = frozen_upstream(base['history'], rel)
        if up is None or any(h(s) in cap['authored'] for s in up):
            results[rel] = (UNAVAILABLE, 0, 0)
            unavailable = True
            continue
        fp = os.path.join(loc, rel)
        try:
            now = Counter(h(s) for s in (x.strip() for x in _lines(fp)) if s)
        except FileNotFoundError:
            now = Counter()
        except OSError:
            results[rel] = (UNAVAILABLE, 0, 0)
            unavailable = True
            continue
        captured = sum(e['count'] for e in cap['authored'].values())
        lost = 0
        for key_, e in cap['authored'].items():
            short = max(0, e['count'] - now.get(key_, 0))
            if short:
                lost += short
                where = ', '.join(f'line {n}' for n in e['lines'])
                shown = '' if private else f'> {key_[:92]}'
                details.append(f'      LOST x{short} ({rel}, {where}) {shown}'.rstrip())
        results[rel] = (LOST if lost else RETAINED, captured, lost)

    # Post-install coverage: every path whose content changed since capture, inside or outside.
    _agg, _t, _u, files_now = content_snapshot(loc)
    before = base['binding']['snapshot']['files']
    now_h = {h(p): [k, h(d)] for p, (k, d) in files_now.items()}
    changed = {p for p in set(before) | set(now_h) if before.get(p) != now_h.get(p)}
    covered_keys = {h(p): p for p in base['coverage']}
    outside = sorted(changed - set(covered_keys))

    print(f'{"path":<52} {"class":<22} {"captured":>8} {"lost":>5}')
    for rel, (cls, captured, lost) in results.items():
        print(f'{rel:<52} {cls:<22} {captured:>8} {lost:>5}')
    for d in details:
        print(d)
    print()
    inside = sorted(covered_keys[k] for k in changed & set(covered_keys))
    print(f'changed paths since capture: {len(changed)} — {len(inside)} inside the write set, '
          f'{len(outside)} outside')
    if outside:
        if private:
            print(f'{NOT_COVERED}: {len(outside)} changed path(s) outside the write set '
                  f'(not named: private mode)')
        else:
            for p in outside:
                print(f'{NOT_COVERED}: {p}')
    total_captured = sum(c for _c, c, _l in results.values())
    total_lost = sum(lo for _c, _x, lo in results.values())
    print(f'scope: {len(base["coverage"])} write-set path(s); lines outside them are not measured')
    if total_lost:
        print(f'*** {total_lost} of {total_captured} captured occurrence(s) LOST ***')
        return 1
    if unavailable:
        print(f'{UNAVAILABLE}: at least one path could not be classified (history or file).')
        return 4
    if outside:
        return 5
    if total_captured == 0:
        print('NO COVERAGE: no receiver-authored lines were captured in the write set.')
        return 3
    print(f'0 of {total_captured} captured occurrence(s) lost.')
    return 0


class NotRegular(RuntimeError):
    """B194 finding 3: a committed source entry that is not an ordinary file (a link, folder or submodule)."""


def upstream_lines(path: str) -> set:
    """Every line this file has EVER carried, across every release tag. B194 finding 3: an ordinary committed file
    only (mode 100644/100755, read with its mode by `ls-tree`); a link's target text is not authored source, so a
    non-regular entry at any tag raises NotRegular."""
    core = core_repo()
    tags = sh(['git', '-C', core, 'tag']).stdout.split()
    seen = set()
    for t in tags:
        ls = _git(core, '--literal-pathspecs', 'ls-tree', '-z', t, '--', path, text=False)
        ent = [e.partition('\t')[0].split() for e in os.fsdecode(ls.stdout).split('\0')
               if e.partition('\t')[2] == path] if ls.returncode == 0 else []
        if not ent:
            continue
        if ent[0][:2] not in (['100644', 'blob'], ['100755', 'blob']):
            raise NotRegular(f'{path} at {t} is a {" ".join(ent[0][:2])} entry, not a regular file')
        r = sh(['git', '-C', core, 'show', f'{t}:{path}'])
        if r.returncode != 0:
            continue
        for line in r.stdout.splitlines():
            s = line.strip()
            if s:
                seen.add(s)
    return seen


def authored(loc: str) -> dict:
    """Receiver-authored lines WITH THEIR OCCURRENCE COUNTS.

    Counting occurrences rather than membership, because a set comparison cannot
    detect losing one of a duplicated pair: if the seat holds a line twice and the
    migration drops one copy, the set still contains it and the loss reads as zero.

    For 333 distinctive lines that risk is low — short common lines are excluded
    because they appear upstream — but this is the instrument that decides whether
    the wave proceeds, and "low risk" is not "cannot happen". A peer caught this
    before the receipt landed; the fix is one line and the cost of finding out
    afterwards would have been the whole hypothesis.
    """
    from collections import Counter
    out = {}
    for path in PAYLOAD_CLASS:
        fp = os.path.join(loc, path)
        if not os.path.exists(fp):
            continue
        up = upstream_lines(path)
        mine = [l.strip() for l in
                open(fp, encoding='utf-8', errors='replace').read().splitlines() if l.strip()]
        counts = Counter(l for l in mine if l not in up)
        out[path] = dict(sorted(counts.items()))
    return out


def main() -> int:
    """Command-line entry point: capture an Aget's own lines before a migration, or verify afterwards that they survived."""
    ap = argparse.ArgumentParser(description=__doc__,
                                 formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument('seat')
    ap.add_argument('--capture', metavar='FILE')
    ap.add_argument('--verify', metavar='FILE')
    ap.add_argument('--coverage', metavar='FILE',
                    help='write-set mode: a coverage file (schema aget-preservation-coverage/1)')
    ap.add_argument('--location', metavar='DIR',
                    help='use this checkout instead of the register location (controls on copies)')
    ap.add_argument('--private', action='store_true',
                    help='write-set capture for a very_personal Aget: keyed digests, no text')
    ap.add_argument('--key-file', metavar='FILE', default=DEFAULT_KEY_FILE,
                    help='private-mode key, kept outside the repository')
    ap.add_argument('--snapshot', action='store_true',
                    help='print the content-snapshot aggregate and counts (never paths)')
    ap.add_argument('--expect-sha256', metavar='HEX',
                    help='refuse (exit 2) a --verify baseline whose bytes do not have this digest')
    args = ap.parse_args()

    loc = args.location or seat_location(args.seat)
    if not loc:
        print(f'{args.seat} not in register', file=sys.stderr)
        return 2

    if args.snapshot:
        agg, tracked, untracked, _files = content_snapshot(loc)
        print(f'{args.seat} aggregate={agg} tracked={tracked} untracked={untracked}')
        return 0

    if args.capture and args.coverage:
        coverage = json.load(open(args.coverage))
        if coverage.get('schema') != COVERAGE_SCHEMA or coverage.get('seat') != args.seat:
            print(f'REFUSED: coverage file is for {coverage.get("seat")!r} (schema '
                  f'{coverage.get("schema")!r}), not {args.seat!r}.', file=sys.stderr)
            return 2
        key = _read_key(args.key_file) if args.private else None
        if args.private and not key:
            print(f'private mode needs a key at {args.key_file}', file=sys.stderr)
            return 4
        base, problem = capture_writeset(args.seat, loc, coverage, args.private, key)
        if problem:
            print(f'{UNAVAILABLE}: {problem}. Nothing captured.', file=sys.stderr)
            return 4
        with open(args.capture, 'w') as fh:
            json.dump(base, fh, indent=2, sort_keys=True)
            fh.write('\n')
        present = sum(1 for p in base['paths'].values() if p['state'] == 'present')
        occ = sum(e['count'] for p in base['paths'].values() for e in p['authored'].values())
        frozen = ', '.join(f'{h["name"]} {len(h["tags"])} tags' for h in base['history'])
        print(f'captured {occ} authored occurrence(s) across {present} present of '
              f'{len(base["paths"])} write-set path(s); mode {base["mode"]}; frozen history: '
              f'{frozen}')
        print(f'snapshot aggregate={base["binding"]["snapshot"]["aggregate"]}')
        print(f'baseline: {args.capture}')
        return 0

    if args.capture:
        try:
            data = authored(loc)
        except NotRegular as e:                  # B194 finding 3: refused, never a capture of a link's target
            print(f'UNAVAILABLE: {e}', file=sys.stderr)
            return 2
        total = sum(sum(c.values()) for c in data.values())
        distinct = sum(len(c) for c in data.values())
        with_dupes = {p: {l: n for l, n in c.items() if n > 1} for p, c in data.items()}
        json.dump({'seat': args.seat, 'location': loc, 'authored': data,
                   'total_occurrences': total, 'distinct_lines': distinct},
                  open(args.capture, 'w'), indent=2)
        print(f'captured {total} authored line occurrence(s), {distinct} distinct, '
              f'across {len(data)} file(s)')
        for p, c in data.items():
            dup = sum(n - 1 for n in c.values() if n > 1)
            print(f'   {sum(c.values()):>4} occurrences ({len(c):>3} distinct'
                  + (f', {dup} duplicate copies' if dup else '') + f')  {p}')
        if any(with_dupes.values()):
            print('\n  duplicated authored lines exist — a set comparison would have been blind')
            print('  to losing one copy of each. This baseline counts occurrences.')
        print(f'\nbaseline: {args.capture}')
        return 0

    if args.verify:
        from collections import Counter
        # Hash and parse one byte buffer: reopening can consume different bytes.
        with open(args.verify, 'rb') as fh:
            baseline_bytes = fh.read()
        if args.expect_sha256:
            # K8 (c): structure and history checks cannot see an edit inside a valid record (one
            # authored entry deleted), so the plan pins each baseline's digest and G1.3 passes it.
            import hashlib
            actual = hashlib.sha256(baseline_bytes).hexdigest()
            if actual != args.expect_sha256.lower():
                print(f'REFUSED: baseline {args.verify} has sha256 {actual}, expected '
                      f'{args.expect_sha256}. No comparison was made.', file=sys.stderr)
                return 2
        base = json.loads(baseline_bytes)
        if base.get('schema') == SCHEMA_V2:
            key = _read_key(args.key_file) if base.get('mode') == 'private' else None
            if base.get('mode') == 'private' and not key:
                print(f'{UNAVAILABLE}: private mode needs its key at {args.key_file}.')
                return 4
            return verify_writeset(args.seat, loc, base, key)
        # K4 (2026-09-26): the subject is checked BEFORE any line is compared. A baseline for
        # another Aget can read as false loss or as false preservation, depending on how much
        # content the two share, so no comparison result is meaningful until identity holds.
        owner = base.get('seat')
        if owner != args.seat:
            print(f'REFUSED: baseline {args.verify} belongs to {owner!r}, not {args.seat!r}. '
                  f'No comparison was made.', file=sys.stderr)
            return 2
        lost_total = captured_total = covered = 0
        print(f'{"file":<48} {"captured":>9} {"surviving":>10} {"LOST":>6}')
        for path, counts in base.get('authored', {}).items():
            captured = sum(counts.values())
            if not captured:
                # K5: a file with nothing captured measures nothing; it is not "survived".
                print(f'{path:<48} {"no coverage":>27}')
                continue
            covered += 1
            captured_total += captured
            fp = os.path.join(loc, path)
            now = Counter()
            if os.path.exists(fp):
                now = Counter(l.strip() for l in
                              open(fp, encoding='utf-8', errors='replace').read().splitlines()
                              if l.strip())
            # Occurrence-wise, not membership-wise: a line held twice and returned
            # once is one line LOST, and a set comparison would score it as intact.
            lost_here = sum(max(0, n - now.get(line, 0)) for line, n in counts.items())
            lost_total += lost_here
            print(f'{path:<48} {captured:>9} {captured-lost_here:>10} {lost_here:>6}')
            for line, n in counts.items():
                short = max(0, n - now.get(line, 0))
                if short:
                    print(f'      LOST x{short}> {line[:92]}')
        missing = [p for p in PAYLOAD_CLASS if p not in base.get('authored', {})]
        for p in missing:
            print(f'{p:<48} {"not in baseline":>27}')
        print()
        # K5: counts only. Whether a hypothesis holds or a wave proceeds is decided by the plan
        # that reads these counts, not by the instrument.
        scope = (f'scope: {covered} covered file(s) of {len(base.get("authored", {}))} in the '
                 f'baseline; lines outside them are not measured')
        if covered == 0:
            print('NO COVERAGE: the baseline captured no receiver-authored lines; this run '
                  'establishes nothing about preservation.')
            print(scope)
            return 3
        if lost_total == 0:
            print(f'0 of {captured_total} captured occurrence(s) lost across {covered} covered '
                  f'file(s).')
            print(scope)
            return 0
        print(f'*** {lost_total} of {captured_total} captured occurrence(s) LOST across {covered} '
              f'covered file(s) ***')
        print(scope)
        return 1

    print('name --capture or --verify', file=sys.stderr)
    return 2


if __name__ == '__main__':
    raise SystemExit(main())
