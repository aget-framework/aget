#!/usr/bin/env python3
"""
Study Topic Protocol - Focused Topic Research

Search KB for topic-related artifacts and report findings.
Use before diving into implementation to understand existing patterns.

Renamed from study_up.py in v3.12.0 (L762: Script-Skill Name Alignment Debt).
Aligns script name with skill name: /aget-study-topic (SNR2, #480).

Implements: CAP-SESSION-007 (Study Topic)
- R-SESSION-007-01: Accept topic argument
- R-SESSION-007-02: Search KB for topic
- R-SESSION-007-03: Report related artifacts
- R-SESSION-007-04: JSON output mode
- R-SESSION-007-05: Verify mode
- R-SESSION-007-06: Epistemic purpose parameter (CAP-SESSION-007-06)
- R-SESSION-007-07: Domain relevance weighting (CAP-SESSION-007-07)

See: aget/specs/AGET_SESSION_SPEC.md (CAP-SESSION-007)
Index: aget/specs/SESSION_SKILLS_INDEX.yaml
Tests: tests/test_session_protocol.py::TestStudyTopicProtocol
Related: L187 (Silent execution), L335 (Memory Architecture), L761, L762

Usage:
    python3 study_topic.py --topic "wind down"       # Research wind down
    python3 study_topic.py --topic "release" --json  # JSON output
    python3 study_topic.py --verify                  # Migration verification
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path


def get_agent_root():
    """Get the agent root directory."""
    current = Path(__file__).resolve()
    return current.parent.parent


def load_study_topic_config():
    """Load study_topic config from .aget/config.json.

    Returns config dict or empty dict if not configured.
    Three-tier degradation (ADR-004):
      Tier 1: Full config with priority_areas + domain_keywords
      Tier 2: Partial config (domain_keywords only)
      Tier 3: No config — default behavior (backward-compatible)

    Implements: CAP-SESSION-007-06 (config fallback), CAP-SESSION-007-07 (domain config)
    """
    config_path = get_agent_root() / '.aget' / 'config.json'
    if not config_path.exists():
        return {}
    try:
        config = json.loads(config_path.read_text())
        return config.get('study_topic', {})
    except (json.JSONDecodeError, OSError):
        return {}


def resolve_purpose(explicit_purpose, config):
    """Resolve epistemic purpose from flag or config default.

    Priority: explicit --purpose flag > config default_purpose > 'exploration'

    Implements: CAP-SESSION-007-06 (purpose resolution)
    """
    if explicit_purpose:
        return explicit_purpose
    return config.get('default_purpose', 'exploration')


def get_purpose_globs(purpose, config):
    """Get file glob patterns for a purpose from config.

    Returns list of glob patterns that should be boosted for this purpose.

    Implements: CAP-SESSION-007-06 (priority_areas)
    """
    priority_areas = config.get('priority_areas', {})
    return priority_areas.get(purpose, [])


def compute_purpose_boost(file_path_str, purpose_globs):
    """Compute purpose boost for a file based on glob matching.

    Returns 2.0 if file matches any purpose glob, 1.0 otherwise.

    Implements: CAP-SESSION-007-06 (purpose weighting)
    """
    if not purpose_globs:
        return 1.0
    from fnmatch import fnmatch
    for glob_pattern in purpose_globs:
        if fnmatch(file_path_str, glob_pattern) or fnmatch(file_path_str, '*/' + glob_pattern):
            return 2.0
    return 1.0


def compute_domain_boost(content, domain_keywords):
    """Compute domain relevance boost based on keyword presence.

    Returns 1.0 + 0.25 per matching keyword (max 2.0).

    Implements: CAP-SESSION-007-07 (domain relevance weighting)
    """
    if not domain_keywords:
        return 1.0
    matches = sum(1 for kw in domain_keywords if kw.lower() in content.lower())
    return min(2.0, 1.0 + matches * 0.25)


def search_file_for_topic(file_path: Path, topic: str, case_insensitive: bool = True,
                          domain_keywords: list = None) -> dict:
    """Search a file for topic matches.

    Args:
        file_path: Path to search
        topic: Topic string to search for
        case_insensitive: Whether to ignore case
        domain_keywords: Optional list of domain keywords for relevance boosting (CAP-SESSION-007-07)

    Returns:
        Dict with match info or None if no match
    """
    try:
        content = file_path.read_text()
        flags = re.IGNORECASE if case_insensitive else 0

        # Tokenize multi-word topics into keywords, filtering punctuation-only tokens
        keywords = [kw for kw in topic.split() if re.search(r'\w', kw)]
        if len(keywords) <= 1:
            # Single keyword: original behavior
            matches = list(re.finditer(re.escape(topic), content, flags))
        else:
            # Multi-keyword: search each independently, require majority coverage
            keyword_matches = {}
            all_matches = []
            for kw in keywords:
                kw_matches = list(re.finditer(re.escape(kw), content, flags))
                if kw_matches:
                    keyword_matches[kw] = len(kw_matches)
                    all_matches.extend(kw_matches)
            # Require at least 50% of keywords present (min 1 for 2-keyword, min 2 for 3+)
            min_required = max(1, (len(keywords) + 1) // 2) if len(keywords) >= 2 else 1
            if len(keyword_matches) < min(min_required, len(keywords)):
                return None
            matches = all_matches

        if not matches:
            return None

        # Extract context lines for first few matches
        lines = content.split('\n')
        contexts = []
        seen_lines = set()
        for match in matches:
            line_start = content.count('\n', 0, match.start())
            if line_start in seen_lines:
                continue
            seen_lines.add(line_start)
            if line_start < len(lines):
                context_line = lines[line_start].strip()
                if len(context_line) > 100:
                    context_line = context_line[:100] + '...'
                contexts.append({
                    'line': line_start + 1,
                    'context': context_line
                })
            if len(contexts) >= 3:
                break

        result = {
            'file': str(file_path.relative_to(get_agent_root())),
            'match_count': len(matches),
            'contexts': contexts
        }
        # Add keyword coverage for multi-word ranking
        if len(keywords) > 1:
            result['keyword_coverage'] = len(keyword_matches) / len(keywords)
        # Add domain boost if keywords provided (CAP-SESSION-007-07)
        if domain_keywords:
            result['domain_boost'] = compute_domain_boost(content, domain_keywords)
        return result
    except (OSError, UnicodeDecodeError):
        return None


def search_directory(path: Path, topic: str, extensions: list = None,
                     purpose_globs: list = None, domain_keywords: list = None) -> list:
    """Search a directory for topic-related files.

    Args:
        path: Directory to search
        topic: Topic to search for
        extensions: File extensions to include (default: .md, .yaml, .json)
        purpose_globs: Glob patterns for purpose-based boosting (CAP-SESSION-007-06)
        domain_keywords: Domain keywords for relevance boosting (CAP-SESSION-007-07)

    Returns:
        List of dicts with file match info, sorted by composite score
    """
    if extensions is None:
        extensions = ['.md', '.yaml', '.json', '.py']

    results = []
    if not path.exists():
        return results

    # Recursive search
    for file in path.rglob('*'):
        if file.is_file() and file.suffix in extensions:
            match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
            if match:
                # Add purpose boost (CAP-SESSION-007-06)
                if purpose_globs:
                    match['purpose_boost'] = compute_purpose_boost(match['file'], purpose_globs)
                results.append(match)

    # Sort by composite score: keyword_coverage * purpose_boost * domain_boost * match_count
    def sort_key(x):
        coverage = x.get('keyword_coverage', 1.0)
        purpose = x.get('purpose_boost', 1.0)
        domain = x.get('domain_boost', 1.0)
        return coverage * purpose * domain * x['match_count']

    results.sort(key=sort_key, reverse=True)
    return results


def find_ldocs(topic: str, domain_keywords: list = None) -> list:
    """Find L-docs related to topic.

    Args:
        topic: Topic to search for
        domain_keywords: Optional domain keywords for boosting (CAP-SESSION-007-07)

    Returns:
        List of matching L-doc info
    """
    agent_root = get_agent_root()
    evolution_path = agent_root / '.aget' / 'evolution'

    results = []
    if not evolution_path.exists():
        return results

    for file in evolution_path.glob('L*.md'):
        match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
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
                'match_count': match['match_count'],
                'domain_boost': match.get('domain_boost', 1.0)
            })

    results.sort(key=lambda x: x['domain_boost'] * x['match_count'], reverse=True)
    return results


def find_patterns(topic: str, domain_keywords: list = None) -> list:
    """Find pattern documents related to topic.

    Args:
        topic: Topic to search for
        domain_keywords: Optional domain keywords for boosting

    Returns:
        List of matching pattern info
    """
    agent_root = get_agent_root()
    patterns_path = agent_root / 'docs' / 'patterns'

    results = []
    if not patterns_path.exists():
        return results

    for file in patterns_path.glob('PATTERN_*.md'):
        match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
        if match:
            results.append({
                'pattern': file.stem,
                'file': match['file'],
                'match_count': match['match_count']
            })

    results.sort(key=lambda x: x['match_count'], reverse=True)
    return results


def find_project_plans(topic: str, domain_keywords: list = None) -> list:
    """Find PROJECT_PLANs related to topic.

    Args:
        topic: Topic to search for
        domain_keywords: Optional domain keywords for boosting

    Returns:
        List of matching plan info
    """
    agent_root = get_agent_root()
    planning_path = agent_root / 'planning'

    results = []
    if not planning_path.exists():
        return results

    for file in planning_path.glob('PROJECT_PLAN*.md'):
        match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
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


def find_sops(topic: str, domain_keywords: list = None) -> list:
    """Find SOPs related to topic.

    Args:
        topic: Topic to search for
        domain_keywords: Optional domain keywords for boosting

    Returns:
        List of matching SOP info
    """
    agent_root = get_agent_root()
    sops_path = agent_root / 'sops'

    results = []
    if not sops_path.exists():
        return results

    for file in sops_path.glob('SOP_*.md'):
        match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
        if match:
            results.append({
                'sop': file.name,
                'file': match['file'],
                'match_count': match['match_count']
            })

    results.sort(key=lambda x: x['match_count'], reverse=True)
    return results


def find_governance(topic: str, domain_keywords: list = None) -> list:
    """Find governance docs related to topic.

    Args:
        topic: Topic to search for
        domain_keywords: Optional domain keywords for boosting

    Returns:
        List of matching governance doc info
    """
    agent_root = get_agent_root()
    governance_path = agent_root / 'governance'

    results = []
    if not governance_path.exists():
        return results

    for file in governance_path.glob('*.md'):
        match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
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
    lines.append(f"STUDY TOPIC: {topic}")
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
        description='Study Topic Protocol - Focused Topic Research',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 study_topic.py --topic "wind down"       # Research wind down protocol
  python3 study_topic.py --topic "release" --json  # JSON output
  python3 study_topic.py --topic "L477"            # Find L477 references
  python3 study_topic.py --verify                  # Migration verification
        '''
    )
    parser.add_argument('--topic', '-t', type=str, help='Topic to research')
    parser.add_argument('--purpose', choices=['pre-implementation', 'pre-release', 'exploration', 'audit'],
                        help='Epistemic purpose — weights results by KB area (CAP-SESSION-007-06)')
    parser.add_argument('--domain-keywords', nargs='*', metavar='KEYWORD',
                        help='Domain keywords for relevance boosting (CAP-SESSION-007-07)')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--verify', action='store_true', help='Verification mode for migration')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')

    args = parser.parse_args()

    # Verification mode for migration testing
    if args.verify:
        print("VERIFY: study_topic protocol (study_topic.py)")
        return 0

    # Topic is required for actual research
    if not args.topic:
        print("Error: --topic is required for research")
        print("Use --verify for migration verification")
        parser.print_help()
        return 1

    # Load config and resolve epistemic parameters (CAP-SESSION-007-06/07)
    config = load_study_topic_config()
    purpose = resolve_purpose(args.purpose, config)
    purpose_globs = get_purpose_globs(purpose, config)

    # Domain keywords: explicit flag > config > none
    domain_keywords = args.domain_keywords or config.get('domain_keywords')

    # Perform focused research with epistemic parameters
    findings = {
        'ldocs': find_ldocs(args.topic, domain_keywords=domain_keywords),
        'patterns': find_patterns(args.topic, domain_keywords=domain_keywords),
        'project_plans': find_project_plans(args.topic, domain_keywords=domain_keywords),
        'sops': find_sops(args.topic, domain_keywords=domain_keywords),
        'governance': find_governance(args.topic, domain_keywords=domain_keywords)
    }

    # JSON output
    if args.json:
        output = {
            'timestamp': datetime.now().isoformat(),
            'agent_path': str(get_agent_root()),
            'topic': args.topic,
            'purpose': purpose,
            'domain_keywords': domain_keywords,
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
