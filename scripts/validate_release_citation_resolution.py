#!/usr/bin/env python3
"""Validate that cited paths in public release artifacts resolve against the public canonical tree.

Scans CHANGELOG.md, RELEASE_HANDOFF_*.md, SKILL.md (or any path) for three citation classes:
  - scripts/*.py     → resolves at <public_root>/scripts/<name>.py
  - L###             → resolves at <public_root>/.aget/evolution/L###_*.md (glob)
  - aget/specs/*     → resolves at <public_root>/../<path>  (citation already includes aget/ prefix)

Citations carrying `[instance-only per L600]` on the same line are exempt.

Exit 0 if zero unresolved-and-unannotated citations across all input artifacts; exit 1 otherwise.

Implements R-REL-044 (Citation Resolution Gate) per AGET_RELEASE_SPEC.
"""

from __future__ import annotations
import argparse, glob, json, os, re, sys
from typing import NamedTuple

SCRIPT_RE = re.compile(r'scripts/[a-z_][a-z0-9_]*\.py')
LDOC_RE = re.compile(r'\bL\d{2,4}\b')
SPEC_RE = re.compile(r'aget/(?:\.aget/)?specs(?:/skills)?/[A-Za-z0-9_-]+\.(?:yaml|md)')
ANNOTATION = '[instance-only per L600]'


class Citation(NamedTuple):
    kind: str        # 'script' | 'ldoc' | 'spec'
    token: str       # raw matched text
    artifact: str    # source artifact path
    line_no: int
    annotated: bool


def find_citations(artifact_path: str) -> list[Citation]:
    results: list[Citation] = []
    if not os.path.isfile(artifact_path):
        return results
    with open(artifact_path) as f:
        for line_no, line in enumerate(f, 1):
            annotated = ANNOTATION in line
            # Strip annotation phrase before scanning so its own L600 token
            # isn't double-counted as a citation.
            scan = line.replace(ANNOTATION, '') if annotated else line
            for m in SCRIPT_RE.findall(scan):
                results.append(Citation('script', m, artifact_path, line_no, annotated))
            for m in LDOC_RE.findall(scan):
                results.append(Citation('ldoc', m, artifact_path, line_no, annotated))
            for m in SPEC_RE.findall(scan):
                results.append(Citation('spec', m, artifact_path, line_no, annotated))
    return results


def resolve(c: Citation, public_root: str) -> bool:
    if c.kind == 'script':
        return os.path.isfile(os.path.join(public_root, c.token))
    if c.kind == 'ldoc':
        return bool(glob.glob(os.path.join(public_root, '.aget/evolution', f'{c.token}_*.md')))
    if c.kind == 'spec':
        # citation token starts with "aget/...": strip and join to public_root's parent
        parent = os.path.dirname(public_root.rstrip('/'))
        return os.path.isfile(os.path.join(parent, c.token))
    return False


def main(argv: list[str]) -> int:
    p = argparse.ArgumentParser(description=__doc__.split('\n')[0])
    p.add_argument('artifacts', nargs='+', help='Paths to release artifacts to scan')
    p.add_argument('--public-root', default=os.environ.get('AGET_PUBLIC_CANONICAL', '../aget'),
                   help='Public canonical aget/ tree (default: ../aget or $AGET_PUBLIC_CANONICAL)')
    p.add_argument('--json', action='store_true', help='Emit JSON report on stdout')
    p.add_argument('--quiet', action='store_true', help='Suppress per-citation output; only exit code matters')
    args = p.parse_args(argv)

    public_root = os.path.abspath(args.public_root)
    if not os.path.isdir(public_root):
        print(f"ERROR: --public-root not a directory: {public_root}", file=sys.stderr)
        return 2

    # Expand directories: recursively find SKILL.md (release-artifact convention).
    expanded: list[str] = []
    for a in args.artifacts:
        if os.path.isdir(a):
            expanded.extend(sorted(glob.glob(os.path.join(a, '**/SKILL.md'), recursive=True)))
        else:
            expanded.append(a)

    all_cites: list[Citation] = []
    for a in expanded:
        all_cites.extend(find_citations(a))

    resolved = []
    unresolved_annotated = []
    unresolved_unannotated = []
    for c in all_cites:
        if resolve(c, public_root):
            resolved.append(c)
        elif c.annotated:
            unresolved_annotated.append(c)
        else:
            unresolved_unannotated.append(c)

    report = {
        'public_root': public_root,
        'artifacts': expanded,
        'totals': {
            'cited': len(all_cites),
            'resolved': len(resolved),
            'unresolved_annotated_exempt': len(unresolved_annotated),
            'unresolved_unannotated_404': len(unresolved_unannotated),
        },
        'failures': [
            {'kind': c.kind, 'token': c.token, 'artifact': c.artifact, 'line': c.line_no}
            for c in unresolved_unannotated
        ],
    }

    if args.json:
        print(json.dumps(report, indent=2))
    elif not args.quiet:
        t = report['totals']
        print(f"Cited: {t['cited']} | Resolved: {t['resolved']} | "
              f"Exempt: {t['unresolved_annotated_exempt']} | 404: {t['unresolved_unannotated_404']}")
        if unresolved_unannotated:
            print("\nUnresolved (no [instance-only per L600] annotation):")
            for c in unresolved_unannotated:
                print(f"  {c.kind:6s} {c.token:55s} {c.artifact}:{c.line_no}")

    return 1 if unresolved_unannotated else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
