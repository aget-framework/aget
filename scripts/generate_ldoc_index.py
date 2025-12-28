#!/usr/bin/env python3
"""
Generate L-doc Index

Generates index.json for Learning Documents in .aget/evolution/ directory.
Required when L-doc count exceeds 50 (CAP-MEMORY-008).

Part of AGET v3.0.0-beta.3 - Gap A5 (L-doc Scaling).

Usage:
    python3 generate_ldoc_index.py <agent_path>
    python3 generate_ldoc_index.py <agent_path> --force
    python3 generate_ldoc_index.py <agent_path> --check

Exit codes:
    0: Success (index generated or up-to-date)
    1: Error (parsing failure, write failure)
    2: Invalid arguments
"""

import argparse
import json
import os
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set


class LdocIndexGenerator:
    """Generates index.json for L-doc scaling."""

    LDOC_PATTERN = re.compile(r'^L(\d{3})_(.+)\.md$')
    THRESHOLD = 50  # CAP-MEMORY-008-01: Required when count > 50

    def __init__(self, agent_path: Path):
        self.agent_path = agent_path
        self.evolution_path = agent_path / ".aget" / "evolution"
        self.index_path = self.evolution_path / "index.json"
        self.ldocs: List[Dict[str, Any]] = []
        self.categories: Dict[str, List[str]] = {}

    def check_needed(self) -> bool:
        """Check if index generation is needed."""
        if not self.evolution_path.exists():
            return False

        ldoc_count = len(list(self.evolution_path.glob("L*.md")))
        return ldoc_count > self.THRESHOLD

    def check_current(self) -> bool:
        """Check if existing index is up-to-date."""
        if not self.index_path.exists():
            return False

        try:
            with open(self.index_path) as f:
                existing = json.load(f)

            # Get current L-doc files
            current_files = set(p.name for p in self.evolution_path.glob("L*.md"))
            indexed_files = set(e["file"] for e in existing.get("entries", []))

            return current_files == indexed_files
        except (json.JSONDecodeError, KeyError):
            return False

    def generate(self) -> Dict[str, Any]:
        """Generate the index structure."""
        if not self.evolution_path.exists():
            return {
                "error": f"Evolution directory not found: {self.evolution_path}"
            }

        self.ldocs = []
        self.categories = {}

        # Process all L-doc files
        for ldoc_file in sorted(self.evolution_path.glob("L*.md")):
            entry = self._parse_ldoc(ldoc_file)
            if entry:
                self.ldocs.append(entry)
                # Add to categories
                for tag in entry.get("tags", []):
                    if tag not in self.categories:
                        self.categories[tag] = []
                    self.categories[tag].append(entry["id"])

        # Build index structure
        index = {
            "meta": {
                "version": "1.0.0",
                "generated": datetime.now().isoformat(),
                "count": len(self.ldocs),
                "threshold": self.THRESHOLD,
                "spec_reference": "AGET_MEMORY_SPEC CAP-MEMORY-008"
            },
            "entries": self.ldocs,
            "categories": dict(sorted(self.categories.items()))
        }

        return index

    def _parse_ldoc(self, ldoc_file: Path) -> Optional[Dict[str, Any]]:
        """Parse a single L-doc file."""
        filename = ldoc_file.name
        match = self.LDOC_PATTERN.match(filename)

        if not match:
            return None

        ldoc_id = f"L{match.group(1)}"
        slug = match.group(2)

        # Read file to extract metadata
        try:
            with open(ldoc_file, 'r', encoding='utf-8') as f:
                content = f.read()
        except Exception:
            content = ""

        # Extract title from first heading
        title = self._extract_title(content, slug)

        # Extract date
        date = self._extract_date(content, ldoc_file)

        # Extract tags from content
        tags = self._extract_tags(content, slug)

        # Determine status
        status = self._extract_status(content)

        return {
            "id": ldoc_id,
            "file": filename,
            "title": title,
            "date": date,
            "tags": tags,
            "status": status
        }

    def _extract_title(self, content: str, fallback_slug: str) -> str:
        """Extract title from L-doc content."""
        # Look for # L###: Title pattern
        match = re.search(r'^#\s+L\d+:\s*(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Look for any first heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Fallback to slug
        return fallback_slug.replace('_', ' ').title()

    def _extract_date(self, content: str, ldoc_file: Path) -> str:
        """Extract date from L-doc content or file stats."""
        # Look for **Date**: YYYY-MM-DD pattern
        match = re.search(r'\*\*Date\*\*:\s*(\d{4}-\d{2}-\d{2})', content)
        if match:
            return match.group(1)

        # Look for Date: YYYY-MM-DD pattern
        match = re.search(r'Date:\s*(\d{4}-\d{2}-\d{2})', content)
        if match:
            return match.group(1)

        # Fallback to file modification time
        try:
            mtime = ldoc_file.stat().st_mtime
            return datetime.fromtimestamp(mtime).strftime('%Y-%m-%d')
        except Exception:
            return "unknown"

    def _extract_tags(self, content: str, slug: str) -> List[str]:
        """Extract tags from L-doc content and slug."""
        tags: Set[str] = set()

        # Common tag keywords to look for
        tag_keywords = {
            'governance': ['governance', 'charter', 'authority', 'gate'],
            'design': ['design', 'architecture', 'pattern', 'spec'],
            'migration': ['migration', 'upgrade', 'transition'],
            'memory': ['memory', 'knowledge', 'learning', 'kb'],
            'session': ['session', 'wake', 'wind', 'handoff'],
            'validation': ['validation', 'test', 'verify', 'compliance'],
            'fleet': ['fleet', 'coordination', 'broadcast', 'agent'],
            'execution': ['execution', 'gate', 'discipline', 'workflow'],
        }

        content_lower = content.lower()
        slug_lower = slug.lower()

        for tag, keywords in tag_keywords.items():
            for keyword in keywords:
                if keyword in content_lower or keyword in slug_lower:
                    tags.add(tag)
                    break

        # If no tags found, use 'general'
        if not tags:
            tags.add('general')

        return sorted(list(tags))

    def _extract_status(self, content: str) -> str:
        """Extract status from L-doc content."""
        # Look for **Status**: Active/Archived/Superseded
        match = re.search(r'\*\*Status\*\*:\s*(\w+)', content)
        if match:
            status = match.group(1).lower()
            if status in ['active', 'archived', 'superseded', 'draft']:
                return status

        return "active"

    def write(self, index: Dict[str, Any]) -> bool:
        """Write index to file."""
        try:
            with open(self.index_path, 'w', encoding='utf-8') as f:
                json.dump(index, f, indent=2)
            return True
        except Exception as e:
            print(f"Error writing index: {e}", file=sys.stderr)
            return False


def main():
    parser = argparse.ArgumentParser(
        description="Generate L-doc index (CAP-MEMORY-008)"
    )
    parser.add_argument(
        "agent_path",
        help="Path to agent directory"
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Generate even if under threshold or up-to-date"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Check if index is needed/current without generating"
    )
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Show detailed output"
    )

    args = parser.parse_args()

    agent_path = Path(args.agent_path)
    if not agent_path.is_absolute():
        agent_path = Path.cwd() / agent_path

    if not agent_path.exists():
        print(f"Error: Agent path not found: {agent_path}", file=sys.stderr)
        sys.exit(2)

    generator = LdocIndexGenerator(agent_path)

    # Check mode
    if args.check:
        evolution_path = agent_path / ".aget" / "evolution"
        if not evolution_path.exists():
            print("No .aget/evolution/ directory")
            sys.exit(0)

        ldoc_count = len(list(evolution_path.glob("L*.md")))
        needed = generator.check_needed()
        current = generator.check_current()

        print(f"L-doc count: {ldoc_count}")
        print(f"Threshold: {generator.THRESHOLD}")
        print(f"Index needed: {'Yes' if needed else 'No'}")
        print(f"Index exists: {'Yes' if generator.index_path.exists() else 'No'}")
        if generator.index_path.exists():
            print(f"Index current: {'Yes' if current else 'No'}")

        if needed and not current:
            print("\nRecommendation: Run without --check to generate index")
            sys.exit(1)
        sys.exit(0)

    # Check if generation is needed
    if not args.force:
        if not generator.check_needed():
            evolution_path = agent_path / ".aget" / "evolution"
            ldoc_count = len(list(evolution_path.glob("L*.md"))) if evolution_path.exists() else 0
            print(f"L-doc count ({ldoc_count}) under threshold ({generator.THRESHOLD})")
            print("Index not required. Use --force to generate anyway.")
            sys.exit(0)

        if generator.check_current():
            print("Index is up-to-date. Use --force to regenerate.")
            sys.exit(0)

    # Generate index
    print(f"Generating L-doc index for: {agent_path.name}")
    index = generator.generate()

    if "error" in index:
        print(f"Error: {index['error']}", file=sys.stderr)
        sys.exit(1)

    # Write index
    if generator.write(index):
        print(f"Generated: {generator.index_path}")
        print(f"  Entries: {index['meta']['count']}")
        print(f"  Categories: {len(index['categories'])}")

        if args.verbose:
            print("\nCategories:")
            for cat, ids in sorted(index['categories'].items()):
                print(f"  {cat}: {len(ids)} L-docs")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
