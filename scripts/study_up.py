#!/usr/bin/env python3
"""
Study Up Protocol - Focused Topic Research

Search KB for topic-related artifacts and report findings.
Use before diving into implementation to understand existing patterns.

Implements: CAP-SESSION-007 (Study Up)
- R-SESSION-007-01: Accept topic argument
- R-SESSION-007-02: Search KB for topic
- R-SESSION-007-03: Report related artifacts
- R-SESSION-007-04: JSON output mode
- R-SESSION-007-05: Verify mode

See: aget/specs/AGET_SESSION_SPEC.md (CAP-SESSION-007)
Index: aget/specs/SESSION_SKILLS_INDEX.yaml
Tests: tests/test_session_protocol.py::TestStudyUpProtocol
Related: L187 (Silent execution), L335 (Memory Architecture)

Usage:
    python3 study_up.py --topic "wind down"       # Research wind down
    python3 study_up.py --topic "release" --json  # JSON output
    python3 study_up.py --verify                  # Migration verification

Exit Codes:
    0: Success
    1: Failure or no topic provided
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def get_agent_root():
    """Get the agent root directory.

    Works from both canonical (scripts/) and legacy (.aget/patterns/session/) locations.
    """
    current = Path(__file__).resolve()
    # Canonical: scripts/study_up.py → parent.parent
    if current.parent.name == 'scripts':
        return current.parent.parent
    # Legacy: .aget/patterns/session/study_up.py → parent^4
    return current.parent.parent.parent.parent


def search_file_for_topic(file_path: Path, topic: str, case_insensitive: bool = True) -> dict:
    """Search a file for topic matches.

    Args:
        file_path: Path to search
        topic: Topic string to search for
        case_insensitive: Whether to ignore case

    Returns:
        Dict with match info or None if no match
    """
    try:
        content = file_path.read_text()
        pattern = re.escape(topic)
        flags = re.IGNORECASE if case_insensitive else 0

        matches = list(re.finditer(pattern, content, flags))
        if not matches:
            return None

        # Extract context lines for first few matches
        lines = content.split('\n')
        contexts = []
        for match in matches[:3]:  # First 3 matches
            # Find line number
            line_start = content.count('\n', 0, match.start())
            if line_start < len(lines):
                context_line = lines[line_start].strip()
                if len(context_line) > 100:
                    context_line = context_line[:100] + '...'
                contexts.append({
                    'line': line_start + 1,
                    'context': context_line
                })

        return {
            'file': str(file_path.relative_to(get_agent_root())),
            'match_count': len(matches),
            'contexts': contexts
        }
    except Exception:
        return None


def search_directory(path: Path, topic: str, extensions: list = None) -> list:
    """Search a directory for topic-related files.

    Args:
        path: Directory to search
        topic: Topic to search for
        extensions: File extensions to include (default: .md, .yaml, .json)

    Returns:
        List of dicts with file match info
    """
    if extensions is None:
        extensions = ['.md', '.yaml', '.json', '.py']

    results = []
    if not path.exists():
        return results

    # Recursive search
    for file in path.rglob('*'):
        if file.is_file() and file.suffix in extensions:
            match = search_file_for_topic(file, topic)
            if match:
                results.append(match)

    # Sort by match count (most relevant first)
    results.sort(key=lambda x: x['match_count'], reverse=True)
    return results


def find_ldocs(topic: str) -> list:
    """Find L-docs related to topic.

    Args:
        topic: Topic to search for

    Returns:
        List of matching L-doc info
    """
    agent_root = get_agent_root()
    evolution_path = agent_root / '.aget' / 'evolution'

    results = []
    if not evolution_path.exists():
        return results

    for file in evolution_path.glob('L*.md'):
        match = search_file_for_topic(file, topic)
        if match:
            # Extract L-doc title from first heading
            try:
                content = file.read_text()
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else file.stem
            except Exception:
                title = file.stem

            results.append({
                'ldoc': file.stem,
                'title': title,
                'file': match['file'],
                'match_count': match['match_count']
            })

    results.sort(key=lambda x: x['match_count'], reverse=True)
    return results


def find_patterns(topic: str) -> list:
    """Find pattern documents related to topic.

    Args:
        topic: Topic to search for

    Returns:
        List of matching pattern info
    """
    agent_root = get_agent_root()
    patterns_path = agent_root / 'docs' / 'patterns'

    results = []
    if not patterns_path.exists():
        return results

    for file in patterns_path.glob('PATTERN_*.md'):
        match = search_file_for_topic(file, topic)
        if match:
            results.append({
                'pattern': file.stem,
                'file': match['file'],
                'match_count': match['match_count']
            })

    results.sort(key=lambda x: x['match_count'], reverse=True)
    return results


def find_project_plans(topic: str) -> list:
    """Find PROJECT_PLANs related to topic.

    Args:
        topic: Topic to search for

    Returns:
        List of matching plan info
    """
    agent_root = get_agent_root()
    planning_path = agent_root / 'planning'

    results = []
    if not planning_path.exists():
        return results

    for file in planning_path.glob('PROJECT_PLAN*.md'):
        match = search_file_for_topic(file, topic)
        if match:
            # Check if active
            try:
                content = file.read_text()
                is_active = 'IN PROGRESS' in content or 'Status**: IN PROGRESS' in content
            except Exception:
                is_active = False

            results.append({
                'plan': file.name,
                'file': match['file'],
                'match_count': match['match_count'],
                'is_active': is_active
            })

    results.sort(key=lambda x: x['match_count'], reverse=True)
    return results


def find_sops(topic: str) -> list:
    """Find SOPs related to topic.

    Args:
        topic: Topic to search for

    Returns:
        List of matching SOP info
    """
    agent_root = get_agent_root()
    sops_path = agent_root / 'sops'

    results = []
    if not sops_path.exists():
        return results

    for file in sops_path.glob('SOP_*.md'):
        match = search_file_for_topic(file, topic)
        if match:
            results.append({
                'sop': file.name,
                'file': match['file'],
                'match_count': match['match_count']
            })

    results.sort(key=lambda x: x['match_count'], reverse=True)
    return results


def find_governance(topic: str) -> list:
    """Find governance docs related to topic.

    Args:
        topic: Topic to search for

    Returns:
        List of matching governance doc info
    """
    agent_root = get_agent_root()
    governance_path = agent_root / 'governance'

    results = []
    if not governance_path.exists():
        return results

    for file in governance_path.glob('*.md'):
        match = search_file_for_topic(file, topic)
        if match:
            results.append({
                'doc': file.name,
                'file': match['file'],
                'match_count': match['match_count']
            })

    results.sort(key=lambda x: x['match_count'], reverse=True)
    return results


def generate_report(topic: str, findings: dict) -> str:
    """Generate human-readable study report.

    Args:
        topic: Topic that was searched
        findings: Dict of findings from search

    Returns:
        Formatted markdown report
    """
    lines = []
    lines.append("=" * 60)
    lines.append(f"STUDY UP: {topic}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"**Search Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Topic**: {topic}")
    lines.append("")

    # Summary
    total = sum(len(v) for v in findings.values() if isinstance(v, list))
    lines.append(f"### Summary")
    lines.append("")
    lines.append(f"Found **{total}** related artifacts:")
    lines.append("")
    lines.append("| Category | Count | Top Match |")
    lines.append("|----------|:-----:|-----------|")

    for key, items in findings.items():
        if isinstance(items, list) and items:
            top = items[0].get('ldoc') or items[0].get('pattern') or items[0].get('plan') or items[0].get('sop') or items[0].get('doc') or 'N/A'
            lines.append(f"| {key.replace('_', ' ').title()} | {len(items)} | {top} |")
        elif isinstance(items, list):
            lines.append(f"| {key.replace('_', ' ').title()} | 0 | - |")

    lines.append("")

    # L-docs section
    if findings.get('ldocs'):
        lines.append("### Related L-docs")
        lines.append("")
        for item in findings['ldocs'][:5]:  # Top 5
            lines.append(f"- **{item['ldoc']}**: {item['title']} ({item['match_count']} matches)")
        if len(findings['ldocs']) > 5:
            lines.append(f"- ... and {len(findings['ldocs']) - 5} more")
        lines.append("")

    # Patterns section
    if findings.get('patterns'):
        lines.append("### Related Patterns")
        lines.append("")
        for item in findings['patterns'][:5]:
            lines.append(f"- {item['pattern']} ({item['match_count']} matches)")
        lines.append("")

    # PROJECT_PLANs section
    if findings.get('project_plans'):
        lines.append("### Related PROJECT_PLANs")
        lines.append("")
        for item in findings['project_plans'][:5]:
            status = "ACTIVE" if item['is_active'] else "inactive"
            lines.append(f"- {item['plan']} [{status}] ({item['match_count']} matches)")
        lines.append("")

    # SOPs section
    if findings.get('sops'):
        lines.append("### Related SOPs")
        lines.append("")
        for item in findings['sops'][:5]:
            lines.append(f"- {item['sop']} ({item['match_count']} matches)")
        lines.append("")

    # Governance section
    if findings.get('governance'):
        lines.append("### Related Governance")
        lines.append("")
        for item in findings['governance'][:5]:
            lines.append(f"- {item['doc']} ({item['match_count']} matches)")
        lines.append("")

    # Recommendation
    lines.append("### Recommendation")
    lines.append("")
    if total == 0:
        lines.append("No existing artifacts found. This appears to be a **novel topic**.")
        lines.append("Consider creating an L-doc to capture learnings.")
    elif total < 3:
        lines.append(f"Limited coverage ({total} artifacts). Review available materials before proposing new work.")
    else:
        lines.append(f"Good coverage ({total} artifacts). Cite precedents when proposing changes.")

    lines.append("")
    lines.append("=" * 60)

    return '\n'.join(lines)


def main():
    parser = argparse.ArgumentParser(
        description='Study Up Protocol - Focused Topic Research',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 study_up.py --topic "wind down"       # Research wind down protocol
  python3 study_up.py --topic "release" --json  # JSON output
  python3 study_up.py --topic "L477"            # Find L477 references
  python3 study_up.py --verify                  # Migration verification
        '''
    )
    parser.add_argument('--topic', '-t', type=str, help='Topic to research')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--verify', action='store_true', help='Verification mode for migration')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')

    args = parser.parse_args()

    # Verification mode for migration testing
    if args.verify:
        print("VERIFY: study_up protocol (study_up.py)")
        return 0

    # Topic is required for actual research
    if not args.topic:
        print("Error: --topic is required for research")
        print("Use --verify for migration verification")
        parser.print_help()
        return 1

    # Perform focused research
    findings = {
        'ldocs': find_ldocs(args.topic),
        'patterns': find_patterns(args.topic),
        'project_plans': find_project_plans(args.topic),
        'sops': find_sops(args.topic),
        'governance': find_governance(args.topic)
    }

    # JSON output
    if args.json:
        output = {
            'timestamp': datetime.now().isoformat(),
            'agent_path': str(get_agent_root()),
            'topic': args.topic,
            'findings': findings,
            'total_artifacts': sum(len(v) for v in findings.values() if isinstance(v, list))
        }
        print(json.dumps(output, indent=2, default=str))
        return 0

    # Human-readable output
    report = generate_report(args.topic, findings)
    print(report)

    return 0


if __name__ == '__main__':
    sys.exit(main())
