#!/usr/bin/env python3
"""
Learning-to-Enhancement Workflow Automation

Automate the workflow from capturing an L-doc to proposing a framework
enhancement. Generates GitHub issue drafts from L-docs.

Implements: #7 (Learning-to-Enhancement Workflow Automation)
Patterns: L004 (Learning Capture), L376 (Checklist-Driven)

Usage:
    python3 learning_to_enhancement.py --ldoc L420           # Process L-doc
    python3 learning_to_enhancement.py --ldoc L420 --dry-run # Preview only
    python3 learning_to_enhancement.py --ldoc L420 --create  # Create GitHub issue
    python3 learning_to_enhancement.py --scan                # Scan for candidates

Exit codes:
    0: Success
    1: L-doc not suitable for enhancement
    2: Processing error
    3: Configuration error

L021 Verification Table:
    | Check | Resource | Before Action |
    |-------|----------|---------------|
    | 1 | L-doc file | Verify exists before parsing |
    | 2 | issue_routing.yaml | Load routing config |
    | 3 | GitHub CLI | Check gh available for --create |

Author: aget-framework
Version: 1.0.0 (v3.1.0)
"""

import argparse
import json
import os
import re
import subprocess
import sys
import time
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, List, Optional, Tuple


# =============================================================================
# Configuration
# =============================================================================

# Categories that typically become enhancements
ENHANCEMENT_CATEGORIES = ['pattern', 'protocol', 'architecture', 'tooling']

# Minimum content length to be considered for enhancement
MIN_CONTENT_LENGTH = 200

# Issue template
ISSUE_TEMPLATE = """## Summary

{summary}

## Origin

- **L-doc**: {ldoc_id}
- **Category**: {category}
- **Created**: {created}
- **Source**: {source}

## Proposed Enhancement

{enhancement}

## Acceptance Criteria

{criteria}

## Related

{related}

---
*Generated from {ldoc_id} by learning_to_enhancement.py*
"""


# =============================================================================
# Timing
# =============================================================================

_start_time = time.time()


def log_diagnostic(msg: str) -> None:
    """Log diagnostic message to stderr."""
    elapsed = (time.time() - _start_time) * 1000
    print(f"[{elapsed:.0f}ms] {msg}", file=sys.stderr)


# =============================================================================
# L-doc Parsing
# =============================================================================

def find_ldoc(ldoc_id: str, search_paths: List[Path]) -> Optional[Path]:
    """Find L-doc file by ID."""
    for path in search_paths:
        if not path.is_dir():
            continue
        for ldoc_file in path.glob(f"{ldoc_id}*.md"):
            return ldoc_file
    return None


def parse_ldoc(file_path: Path) -> Dict[str, Any]:
    """
    Parse L-doc file.

    Returns parsed data.
    """
    result = {
        'id': None,
        'title': None,
        'category': 'observation',
        'created': None,
        'summary': '',
        'content': '',
        'related_ldocs': [],
        'related_issues': [],
        'enhancement_candidate': False,
        'enhancement_score': 0,
    }

    try:
        content = file_path.read_text()
    except IOError as e:
        result['error'] = f"Read error: {e}"
        return result

    result['content'] = content

    # Extract ID from filename
    match = re.match(r'^(L\d+)', file_path.name)
    if match:
        result['id'] = match.group(1)

    # Check for YAML frontmatter
    if content.startswith('---'):
        lines = content.split('\n')
        end_idx = None
        for i, line in enumerate(lines[1:], 1):
            if line.strip() == '---':
                end_idx = i
                break

        if end_idx:
            # Parse frontmatter
            for line in lines[1:end_idx]:
                if ':' in line:
                    key, _, value = line.partition(':')
                    key = key.strip()
                    value = value.strip().strip('"\'')

                    if key == 'title':
                        result['title'] = value
                    elif key == 'category':
                        result['category'] = value
                    elif key == 'created':
                        result['created'] = value
                    elif key == 'summary':
                        result['summary'] = value

    # Extract title from first header if not in frontmatter
    if not result['title']:
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            result['title'] = match.group(1)

    # Extract summary from content if not in frontmatter
    if not result['summary']:
        # Look for ## Summary or ## Context section
        match = re.search(r'##\s+(Summary|Context)\s*\n+(.+?)(?=\n##|\Z)',
                          content, re.DOTALL | re.IGNORECASE)
        if match:
            result['summary'] = match.group(2).strip()[:500]

    # Find related L-docs
    result['related_ldocs'] = list(set(re.findall(r'\bL\d{2,4}\b', content)))
    if result['id'] in result['related_ldocs']:
        result['related_ldocs'].remove(result['id'])

    # Find related issues
    result['related_issues'] = re.findall(r'#\d+', content)

    # Determine enhancement candidacy
    result['enhancement_candidate'], result['enhancement_score'] = \
        evaluate_enhancement_candidacy(result)

    return result


def evaluate_enhancement_candidacy(ldoc: Dict[str, Any]) -> Tuple[bool, int]:
    """
    Evaluate if L-doc is suitable for enhancement proposal.

    Returns (is_candidate, score).
    """
    score = 0

    # Category check
    if ldoc.get('category') in ENHANCEMENT_CATEGORIES:
        score += 30

    # Content length check
    content_len = len(ldoc.get('content', ''))
    if content_len > MIN_CONTENT_LENGTH:
        score += 20
    if content_len > 500:
        score += 10

    # Has summary
    if ldoc.get('summary'):
        score += 15

    # Has related L-docs (indicates pattern)
    if len(ldoc.get('related_ldocs', [])) >= 2:
        score += 15

    # Title quality (not just ID)
    title = ldoc.get('title', '')
    if title and not title.startswith('L'):
        score += 10

    # Is candidate if score >= 50
    return score >= 50, score


# =============================================================================
# Enhancement Generation
# =============================================================================

def generate_enhancement_issue(ldoc: Dict[str, Any], routing: Dict[str, Any] = None) -> Dict[str, Any]:
    """
    Generate GitHub issue content from L-doc.

    Returns issue data.
    """
    issue = {
        'title': f"[Enhancement] {ldoc.get('title', ldoc.get('id', 'Unknown'))}",
        'body': '',
        'labels': ['enhancement', 'from-ldoc'],
        'repo': None,
    }

    # Determine target repo from routing
    if routing:
        category = ldoc.get('category', 'observation')
        issue['repo'] = routing.get('category_routing', {}).get(category)
        if not issue['repo']:
            issue['repo'] = routing.get('default_repo')

    # Generate summary
    summary = ldoc.get('summary', '')
    if not summary:
        summary = f"Enhancement based on learning document {ldoc.get('id')}."

    # Generate enhancement description
    enhancement = f"""Based on {ldoc.get('id')}, the following enhancement is proposed:

1. Document the pattern/protocol formally
2. Add validation or tooling support
3. Update relevant templates"""

    # Generate acceptance criteria
    criteria = """- [ ] Pattern/protocol documented in specs/
- [ ] Validation script created (if applicable)
- [ ] Template(s) updated with new capability
- [ ] Tests added"""

    # Generate related section
    related_parts = []
    if ldoc.get('related_ldocs'):
        related_parts.append(f"- L-docs: {', '.join(ldoc['related_ldocs'][:5])}")
    if ldoc.get('related_issues'):
        related_parts.append(f"- Issues: {', '.join(ldoc['related_issues'][:5])}")
    related = '\n'.join(related_parts) if related_parts else "None identified"

    # Format body
    issue['body'] = ISSUE_TEMPLATE.format(
        summary=summary,
        ldoc_id=ldoc.get('id', 'Unknown'),
        category=ldoc.get('category', 'unknown'),
        created=ldoc.get('created', 'unknown'),
        source=ldoc.get('source', 'local'),
        enhancement=enhancement,
        criteria=criteria,
        related=related,
    )

    return issue


def load_issue_routing(agent_path: Path) -> Dict[str, Any]:
    """Load issue routing configuration."""
    routing_file = agent_path / '.aget' / 'config' / 'issue_routing.yaml'

    if not routing_file.exists():
        return {}

    try:
        import yaml
        with open(routing_file) as f:
            return yaml.safe_load(f) or {}
    except ImportError:
        # Fallback: simple parsing
        return {}
    except Exception:
        return {}


def create_github_issue(issue: Dict[str, Any], dry_run: bool = False) -> Tuple[bool, str]:
    """
    Create GitHub issue using gh CLI.

    Returns (success, message).
    """
    if dry_run:
        return True, "Would create issue (dry-run)"

    repo = issue.get('repo')
    if not repo:
        return False, "No target repository specified"

    # Check gh CLI available
    try:
        subprocess.run(['gh', '--version'], capture_output=True, check=True)
    except (subprocess.SubprocessError, FileNotFoundError):
        return False, "GitHub CLI (gh) not available"

    # Create issue
    cmd = [
        'gh', 'issue', 'create',
        '--repo', repo,
        '--title', issue['title'],
        '--body', issue['body'],
    ]

    for label in issue.get('labels', []):
        cmd.extend(['--label', label])

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
        if result.returncode == 0:
            # Extract issue URL from output
            url = result.stdout.strip()
            return True, f"Created: {url}"
        else:
            return False, f"gh error: {result.stderr}"
    except subprocess.TimeoutExpired:
        return False, "gh command timed out"
    except Exception as e:
        return False, f"Error: {e}"


# =============================================================================
# Scanning
# =============================================================================

def scan_for_candidates(search_paths: List[Path], verbose: bool = False) -> List[Dict[str, Any]]:
    """Scan for L-docs suitable for enhancement."""
    candidates = []

    for path in search_paths:
        if not path.is_dir():
            continue

        for ldoc_file in path.glob('L*.md'):
            if verbose:
                log_diagnostic(f"Scanning {ldoc_file.name}...")

            ldoc = parse_ldoc(ldoc_file)
            if ldoc.get('enhancement_candidate'):
                candidates.append({
                    'id': ldoc.get('id'),
                    'title': ldoc.get('title'),
                    'category': ldoc.get('category'),
                    'score': ldoc.get('enhancement_score'),
                    'file': str(ldoc_file),
                })

    # Sort by score descending
    candidates.sort(key=lambda x: x.get('score', 0), reverse=True)
    return candidates


def format_human_output(ldoc: Dict[str, Any], issue: Dict[str, Any]) -> str:
    """Format output for human reading."""
    lines = []

    lines.append(f"\n=== Enhancement Proposal: {ldoc.get('id')} ===\n")

    lines.append(f"Title: {ldoc.get('title', 'Unknown')}")
    lines.append(f"Category: {ldoc.get('category')}")
    lines.append(f"Enhancement Score: {ldoc.get('enhancement_score')}/100")
    lines.append(f"Candidate: {'Yes' if ldoc.get('enhancement_candidate') else 'No'}")
    lines.append("")

    if issue:
        lines.append("--- Generated Issue ---")
        lines.append(f"Title: {issue.get('title')}")
        lines.append(f"Repo: {issue.get('repo', 'Not specified')}")
        lines.append(f"Labels: {', '.join(issue.get('labels', []))}")
        lines.append("")
        lines.append("Body Preview:")
        lines.append("-" * 40)
        lines.append(issue.get('body', '')[:500])
        if len(issue.get('body', '')) > 500:
            lines.append("...")
        lines.append("-" * 40)

    lines.append("")
    return "\n".join(lines)


# =============================================================================
# Main
# =============================================================================

def main():
    parser = argparse.ArgumentParser(
        description='Learning-to-Enhancement workflow (v3.1)',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 learning_to_enhancement.py --ldoc L420
  python3 learning_to_enhancement.py --ldoc L420 --dry-run
  python3 learning_to_enhancement.py --scan

Exit codes:
  0 - Success
  1 - L-doc not suitable for enhancement
  2 - Processing error
  3 - Configuration error
        """
    )
    parser.add_argument(
        '--ldoc',
        type=str,
        help='L-doc ID to process (e.g., L420)'
    )
    parser.add_argument(
        '--scan',
        action='store_true',
        help='Scan for enhancement candidates'
    )
    parser.add_argument(
        '--create',
        action='store_true',
        help='Create GitHub issue (requires gh CLI)'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Preview without creating issue'
    )
    parser.add_argument(
        '--json',
        action='store_true',
        help='Output as JSON'
    )
    parser.add_argument(
        '--dir',
        type=Path,
        help='Agent directory (default: current)'
    )
    parser.add_argument(
        '--verbose', '-v',
        action='store_true',
        help='Enable diagnostic output'
    )
    parser.add_argument(
        '--version',
        action='version',
        version='learning_to_enhancement.py 1.0.0 (AGET v3.1.0)'
    )

    args = parser.parse_args()

    if not args.ldoc and not args.scan:
        parser.error("Must specify --ldoc ID or --scan")

    if args.verbose:
        log_diagnostic("Starting learning-to-enhancement workflow")

    # Determine agent path
    if args.dir:
        agent_path = args.dir.resolve()
    else:
        agent_path = Path.cwd()

    # Search paths for L-docs
    search_paths = [
        agent_path / '.aget' / 'evolution',
        agent_path / 'evolution',
    ]

    # Scan mode
    if args.scan:
        candidates = scan_for_candidates(search_paths, args.verbose)

        if args.json:
            print(json.dumps({'candidates': candidates}, indent=2))
        else:
            print(f"\n=== Enhancement Candidates ({len(candidates)} found) ===\n")
            for c in candidates[:10]:  # Top 10
                print(f"  [{c['score']:3d}] {c['id']}: {c.get('title', 'Untitled')}")
                print(f"        Category: {c.get('category')}")
            if len(candidates) > 10:
                print(f"\n  ... and {len(candidates) - 10} more")
            print("")

        return 0

    # Process specific L-doc
    ldoc_file = find_ldoc(args.ldoc, search_paths)
    if not ldoc_file:
        print(f"Error: L-doc {args.ldoc} not found", file=sys.stderr)
        return 3

    if args.verbose:
        log_diagnostic(f"Found L-doc: {ldoc_file}")

    ldoc = parse_ldoc(ldoc_file)
    ldoc['source'] = str(ldoc_file)

    if ldoc.get('error'):
        print(f"Error: {ldoc['error']}", file=sys.stderr)
        return 2

    # Load routing config
    routing = load_issue_routing(agent_path)

    # Generate enhancement issue
    issue = generate_enhancement_issue(ldoc, routing)

    if args.json:
        print(json.dumps({
            'ldoc': ldoc,
            'issue': issue,
        }, indent=2, default=str))
    else:
        print(format_human_output(ldoc, issue))

    # Check candidacy
    if not ldoc.get('enhancement_candidate'):
        print(f"Note: {args.ldoc} scored {ldoc.get('enhancement_score')}/100 (threshold: 50)")
        print("Consider adding more detail or categorizing as pattern/protocol.")
        return 1

    # Create issue if requested
    if args.create:
        success, message = create_github_issue(issue, args.dry_run)
        print(f"\nIssue creation: {message}")
        if not success:
            return 2

    return 0


if __name__ == '__main__':
    sys.exit(main())
