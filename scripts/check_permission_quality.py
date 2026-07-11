#!/usr/bin/env python3
"""
check_permission_quality.py — Permission QUALITY check (v3.26 C-26-10, gh#1843)

The count-based permission check (health_check.py, v3.25: WARN >100 / CRITICAL
>200) measures quantity only. Field evidence (2026-07-05): an agent persisted
bare `Edit` and `Write` grants from a session-scoped "allow all edits" choice —
unscoped write-capable grants pass the count check green while silently removing
the exact permission-prompt class the healthy-friction doctrine protects
(authority-expanding edit prompts; user-memory
feedback-public-repo-edit-prompts-are-healthy-friction).

Classification per grant:
  BARE       — tool name only ("Bash", "Edit"): no scoping at all
  UNIVERSAL  — wildcard-everything pattern ("Bash(*)", "Bash(*:*)", "Edit(**)")
  SCOPED     — any non-universal pattern, INCLUDING broad-but-namespaced forms
               like "Bash(git:*)" (those are PREFERRED per SOP_permission_cleanup
               / L027+L500 — breadth within a namespace is policy, not a defect)

Severity: write-capable tools (Edit, Write, Bash, NotebookEdit, mcp *write*)
BARE/UNIVERSAL → the quality WARN that motivates this check. Read-only tools
BARE → INFO (visible, not alarming).

Output follows the three-state contract (C-26-09,
docs/CONVENTION_check_three_state_contract.md): PASS / WARN(=FAIL-class, exit 1)
/ UNREACHABLE (no settings files; non-gating, exit 0).

Usage: python3 scripts/check_permission_quality.py [--dir /path/to/agent] [--json]
"""

import argparse
import json
import re
import sys
from pathlib import Path

WRITE_CAPABLE = {'bash', 'edit', 'write', 'notebookedit'}
UNIVERSAL_RE = re.compile(r'^\(\s*(\*|\*\*|\*:\*)\s*\)$')


def classify(grant: str):
    """Return (tool, kind) — kind ∈ {BARE, UNIVERSAL, SCOPED}."""
    m = re.match(r'^([A-Za-z_][\w\-]*(?:__[\w\-]+)*)(\(.*\))?$', grant.strip())
    if not m:
        return grant, 'SCOPED'  # unparseable → assume scoped (fail-safe: no false alarm storm)
    tool, pattern = m.group(1), m.group(2)
    if pattern is None or pattern == '()':
        return tool, 'BARE'
    if UNIVERSAL_RE.match(pattern):
        return tool, 'UNIVERSAL'
    return tool, 'SCOPED'


def check(agent_dir: Path):
    files = [agent_dir / '.claude' / 'settings.json',
             agent_dir / '.claude' / 'settings.local.json']
    present = [f for f in files if f.is_file()]
    if not present:
        return {'state': 'UNREACHABLE',
                'msg': 'no .claude/settings*.json found — quality unverifiable from this vantage',
                'findings': []}

    findings = []
    total = 0
    for f in present:
        try:
            data = json.loads(f.read_text())
        except (json.JSONDecodeError, OSError) as e:
            findings.append({'file': f.name, 'grant': '-', 'kind': 'UNREACHABLE',
                             'severity': 'INFO', 'note': f'unparseable: {e}'})
            continue
        for grant in (data.get('permissions', {}) or {}).get('allow', []) or []:
            total += 1
            tool, kind = classify(grant)
            if kind in ('BARE', 'UNIVERSAL'):
                write_cap = (tool.lower() in WRITE_CAPABLE
                             or ('write' in tool.lower() and tool.lower().startswith('mcp')))
                findings.append({
                    'file': f.name, 'grant': grant, 'kind': kind,
                    'severity': 'WARN' if write_cap else 'INFO',
                    'note': ('write-capable tool with no scoping — removes the '
                             'authority-expanding prompt class entirely' if write_cap
                             else 'read-only tool unscoped — visible, low risk')})

    warns = [x for x in findings if x['severity'] == 'WARN']
    state = 'WARN' if warns else 'PASS'
    msg = (f'{len(warns)} write-capable BARE/UNIVERSAL grant(s) across {total} total — '
           f'quality WARN independent of count' if warns
           else f'{total} grants, none write-capable-unscoped '
                f'({len(findings)} read-only bare grants noted)' if findings
           else f'{total} grants, all scoped')
    return {'state': state, 'msg': msg, 'findings': findings, 'total_grants': total}


def main(argv=None):
    p = argparse.ArgumentParser(description='Permission quality check (gh#1843, C-26-10)')
    p.add_argument('--dir', type=Path, default=Path.cwd())
    p.add_argument('--json', action='store_true')
    args = p.parse_args(argv)

    res = check(args.dir)
    if args.json:
        print(json.dumps(res, indent=2))
    else:
        print(f"permission-quality: {res['state']} — {res['msg']}")
        for x in res['findings']:
            print(f"  [{x['severity']}] {x['file']}: {x['grant']} ({x['kind']}) — {x['note']}")
    # Three-state: WARN gates softly (exit 1, matches health_check warning tier);
    # UNREACHABLE non-gating (ADR-004).
    return 1 if res['state'] == 'WARN' else 0


if __name__ == '__main__':
    sys.exit(main())
