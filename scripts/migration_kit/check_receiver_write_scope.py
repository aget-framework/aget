#!/usr/bin/env python3
"""Pre-write check: would writing these paths cross the receiver's declared write scope?

Run this BEFORE any cross-Aget write, per root, over the exact enumerated path list.

Why this exists (2026-09-23): a principal-approved four-root batch wrote
`.github/workflows/ci.yml` at two receivers whose `.aget/version.json` declares a strict
`write_scope` allow-list that excludes it. The preflight had searched the receivers' AGENTS.md
prose; the binding declaration lives in the version file. The same miss was already recorded
as a lesson, and remembering it did not prevent it — so it is a command now, not a note.

It REUSES the allow-list semantics of `build_r0917b_path_list.py` (`scope()` / `refused()`),
which R-0917-B was derived with, rather than re-deriving them. It adds only what a pre-write
gate needs on top: a structural read of how many `write_scope` blocks exist, and fail-safe
handling of every shape those regex readers cannot interpret.

Exit codes:
    0  every path is inside the allow-list, or the receiver declares no write_scope at all
    1  at least one path is outside a declared allow-list (REFUSE the write)
    2  cannot tell: no version file, unreadable JSON, a write_scope without an allow-list,
       more than one write_scope block, or a carve-out clause. Read it by hand; never treat
       2 as permission.

Usage:
    python3 scripts/migration_kit/check_receiver_write_scope.py <receiver_root> <path> [<path> ...] [--json]
"""
import argparse
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).resolve().parent))
from write_scope_rules import refused, scope  # noqa: E402


def _write_scope_blocks(node, trail=()):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == 'write_scope':
                yield '.'.join(trail + (key,)), value
            yield from _write_scope_blocks(value, trail + (key,))
    elif isinstance(node, list):
        for index, value in enumerate(node):
            yield from _write_scope_blocks(value, trail + (str(index),))


def check(root, paths):
    """Return the verdict, exit code and refused paths for writing these paths under the receiver's declared write scope."""
    root = pathlib.Path(root)
    result = {'root': str(root), 'paths': list(paths), 'verdict': None, 'exit_code': None,
              'reason': None, 'declared_at': [], 'enforcement': None, 'refused': {}}

    def done(verdict, code, reason):
        result.update(verdict=verdict, exit_code=code, reason=reason)
        return result

    version_file = root / '.aget' / 'version.json'
    if not version_file.is_file():
        return done('unverifiable', 2, 'no .aget/version.json — not an Aget root, or not readable')
    try:
        document = json.loads(version_file.read_text(errors='replace'))
    except ValueError as exc:
        return done('unverifiable', 2, f'version.json is not valid JSON: {exc}')

    blocks = list(_write_scope_blocks(document))
    result['declared_at'] = [where for where, _ in blocks]
    if not blocks:
        return done('no_scope_declared', 0, 'receiver declares no write_scope')
    if len(blocks) > 1:
        return done('unverifiable', 2, 'more than one write_scope block; the regex reader would '
                                       'silently pick one — read them by hand')
    where, block = blocks[0]
    if isinstance(block, str) and block.strip().lower() == 'unrestricted':
        # An explicit declaration, not a missing list: llm-connectivity declares exactly this,
        # which this command first read as unverifiable (its own answer corrected it, 2026-09-23).
        result['enforcement'] = 'unrestricted'
        return done('unrestricted', 0, f'{where} is declared "unrestricted"')
    if not isinstance(block, dict) or not isinstance(block.get('allowed_paths'), list):
        return done('unverifiable', 2, f'{where} declares no allowed_paths list; its meaning is '
                                       'not machine-readable here')

    allow, deny, enforcement, carve_out = scope(root)
    result['enforcement'] = enforcement
    if carve_out:
        return done('unverifiable', 2, 'a permitted_paths / maintenance carve-out is present; '
                                       'carve-outs need a human read')
    if sorted(allow) != sorted(block['allowed_paths']):
        return done('unverifiable', 2, 'the shared scope() reader and the structural read disagree '
                                       'on allowed_paths')

    for path in paths:
        reason = refused(path, allow, deny)
        if reason:
            result['refused'][path] = reason
    if result['refused']:
        return done('outside_scope', 1, f'{len(result["refused"])} of {len(paths)} path(s) outside '
                                        f'the declared allow-list (enforcement: {enforcement})')
    return done('inside_scope', 0, f'all {len(paths)} path(s) inside the declared allow-list')


def main(argv=None):
    """Command-line entry point: check the given paths against one receiver's declared write scope."""
    parser = argparse.ArgumentParser(description=__doc__.split('\n\n')[0])
    parser.add_argument('root', help='receiver repository root')
    parser.add_argument('paths', nargs='+', help='repo-relative paths the write would touch')
    parser.add_argument('--json', action='store_true')
    args = parser.parse_args(argv)
    result = check(args.root, args.paths)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"{result['verdict'].upper()}: {result['root']} — {result['reason']}")
        for path, reason in result['refused'].items():
            print(f'  REFUSE {path}: {reason}')
    return result['exit_code']


if __name__ == '__main__':
    raise SystemExit(main())
