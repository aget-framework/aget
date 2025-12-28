#!/usr/bin/env python3
"""
Export Agent Knowledge

Exports portable content from an AGET agent for framework ejection or backup.
Implements CAP-PORT-002 (Export Mechanism) from AGET_PORTABILITY_SPEC.

Part of AGET v3.0.0-beta.3 - Portability implementation.

Usage:
    python3 export_agent_knowledge.py <agent_path> --output <export_dir>
    python3 export_agent_knowledge.py <agent_path> --output <export_dir> --format tar.gz
    python3 export_agent_knowledge.py <agent_path> --check  # Show what would be exported

Exit codes:
    0: Success
    1: Error
    2: Invalid arguments
"""

import argparse
import json
import os
import shutil
import sys
import tarfile
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Any, Optional, Set


class KnowledgeExporter:
    """Exports portable knowledge from AGET agent."""

    # Portable content (per AGET_PORTABILITY_SPEC CAP-PORT-001)
    PORTABLE_DIRS = [
        "governance",       # Charter, mission, scope
        "planning",         # Plans, decisions
        "sessions",         # Session notes
        "knowledge",        # Domain knowledge
        "docs",             # Documentation
        "products",         # Work products (developer+)
        "decisions",        # Decision records (architect+)
        "reports",          # Analysis reports (analyst+)
        "clients",          # Client work (advisor+) - respects .gitignore
        "src",              # Source code
        "tests",            # Test code
        "data",             # Data files
    ]

    # L-docs are portable (exception to .aget/ rule)
    PORTABLE_AGET = [
        ".aget/evolution",  # L-docs (Apache 2.0)
    ]

    # Framework-locked (NOT exported)
    FRAMEWORK_LOCKED = [
        ".aget/version.json",
        ".aget/identity.json",
        ".aget/persona",
        ".aget/memory",
        ".aget/reasoning",
        ".aget/skills",
        ".aget/context",
        ".aget/patterns",
        ".aget/archive",
        "manifest.yaml",
    ]

    def __init__(self, agent_path: Path):
        self.agent_path = agent_path
        self.export_items: List[Dict[str, Any]] = []
        self.skip_items: List[Dict[str, Any]] = []

    def analyze(self) -> Dict[str, Any]:
        """Analyze what would be exported."""
        self.export_items = []
        self.skip_items = []

        # Check portable directories
        for dir_name in self.PORTABLE_DIRS:
            dir_path = self.agent_path / dir_name
            if dir_path.exists() and dir_path.is_dir():
                size = self._get_dir_size(dir_path)
                file_count = self._count_files(dir_path)
                self.export_items.append({
                    "path": dir_name,
                    "type": "directory",
                    "size": size,
                    "file_count": file_count,
                    "category": "portable_content"
                })

        # Check .aget/evolution (L-docs)
        evolution_path = self.agent_path / ".aget" / "evolution"
        if evolution_path.exists():
            ldoc_files = list(evolution_path.glob("L*.md"))
            size = sum(f.stat().st_size for f in ldoc_files)
            self.export_items.append({
                "path": ".aget/evolution",
                "type": "directory",
                "size": size,
                "file_count": len(ldoc_files),
                "category": "learning_documents",
                "note": "L-docs exported as-is (Apache 2.0)"
            })

        # Check README and other root files
        for filename in ["README.md", "AGENTS.md", "CLAUDE.md"]:
            file_path = self.agent_path / filename
            if file_path.exists():
                self.export_items.append({
                    "path": filename,
                    "type": "file",
                    "size": file_path.stat().st_size,
                    "category": "documentation"
                })

        # Track what's skipped (framework-locked)
        for item in self.FRAMEWORK_LOCKED:
            item_path = self.agent_path / item
            if item_path.exists():
                self.skip_items.append({
                    "path": item,
                    "reason": "framework_locked"
                })

        # Calculate totals
        total_size = sum(item["size"] for item in self.export_items if "size" in item)
        total_files = sum(item.get("file_count", 1) for item in self.export_items)

        return {
            "agent": self.agent_path.name,
            "export_items": self.export_items,
            "skip_items": self.skip_items,
            "summary": {
                "export_count": len(self.export_items),
                "skip_count": len(self.skip_items),
                "total_size_bytes": total_size,
                "total_size_human": self._human_size(total_size),
                "total_files": total_files
            }
        }

    def export(self, output_path: Path, format: str = "directory") -> Dict[str, Any]:
        """Export portable content."""
        analysis = self.analyze()

        if not self.export_items:
            return {
                "success": False,
                "error": "No portable content found"
            }

        try:
            if format == "directory":
                return self._export_directory(output_path, analysis)
            elif format in ["tar.gz", "tgz"]:
                return self._export_tarball(output_path, analysis)
            else:
                return {
                    "success": False,
                    "error": f"Unknown format: {format}"
                }
        except Exception as e:
            return {
                "success": False,
                "error": str(e)
            }

    def _export_directory(self, output_path: Path, analysis: Dict) -> Dict[str, Any]:
        """Export to directory structure."""
        # Create output directory
        output_path.mkdir(parents=True, exist_ok=True)

        # Create export manifest
        manifest = {
            "export_date": datetime.now().isoformat(),
            "source_agent": self.agent_path.name,
            "spec_reference": "AGET_PORTABILITY_SPEC CAP-PORT-002",
            "constraint_acknowledgment": (
                "Exported content operates without AGET framework governance. "
                "Session protocols, validation, capability composition not available. "
                "L-docs remain Apache 2.0 licensed."
            ),
            "exported_items": [item["path"] for item in self.export_items]
        }

        # Copy items
        copied = []
        for item in self.export_items:
            src = self.agent_path / item["path"]
            dst = output_path / item["path"]

            if item["type"] == "directory":
                if src.exists():
                    shutil.copytree(src, dst, dirs_exist_ok=True)
                    copied.append(item["path"])
            else:
                dst.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(src, dst)
                copied.append(item["path"])

        # Write manifest
        manifest_path = output_path / "_export_manifest.json"
        with open(manifest_path, 'w') as f:
            json.dump(manifest, f, indent=2)

        # Write constraint acknowledgment
        ack_path = output_path / "CONSTRAINT_ACKNOWLEDGMENT.md"
        self._write_acknowledgment(ack_path)

        return {
            "success": True,
            "format": "directory",
            "output": str(output_path),
            "copied": copied,
            "manifest": str(manifest_path)
        }

    def _export_tarball(self, output_path: Path, analysis: Dict) -> Dict[str, Any]:
        """Export to tar.gz archive."""
        # Ensure output has correct extension
        if not str(output_path).endswith(('.tar.gz', '.tgz')):
            output_path = output_path.with_suffix('.tar.gz')

        output_path.parent.mkdir(parents=True, exist_ok=True)

        with tarfile.open(output_path, "w:gz") as tar:
            # Add exported items
            for item in self.export_items:
                src = self.agent_path / item["path"]
                if src.exists():
                    tar.add(src, arcname=item["path"])

            # Add manifest (created in memory)
            manifest = {
                "export_date": datetime.now().isoformat(),
                "source_agent": self.agent_path.name,
                "spec_reference": "AGET_PORTABILITY_SPEC CAP-PORT-002",
                "constraint_acknowledgment": "See CONSTRAINT_ACKNOWLEDGMENT.md",
                "exported_items": [item["path"] for item in self.export_items]
            }

            # Write temporary files and add to tar
            import tempfile
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(manifest, f, indent=2)
                temp_manifest = f.name
            tar.add(temp_manifest, arcname="_export_manifest.json")
            os.unlink(temp_manifest)

            # Add acknowledgment
            with tempfile.NamedTemporaryFile(mode='w', suffix='.md', delete=False) as f:
                f.write(self._get_acknowledgment_content())
                temp_ack = f.name
            tar.add(temp_ack, arcname="CONSTRAINT_ACKNOWLEDGMENT.md")
            os.unlink(temp_ack)

        return {
            "success": True,
            "format": "tar.gz",
            "output": str(output_path),
            "size": output_path.stat().st_size,
            "size_human": self._human_size(output_path.stat().st_size)
        }

    def _write_acknowledgment(self, path: Path):
        """Write constraint acknowledgment file."""
        with open(path, 'w') as f:
            f.write(self._get_acknowledgment_content())

    def _get_acknowledgment_content(self) -> str:
        """Get constraint acknowledgment content."""
        return f"""# Constraint Acknowledgment

**Export Date**: {datetime.now().strftime('%Y-%m-%d')}
**Source Agent**: {self.agent_path.name}

## What This Export Contains

This export contains **Portable_Content** from an AGET agent:

- Learning Documents (L-docs) from `.aget/evolution/`
- Governance documents (charter, mission, scope)
- Planning artifacts
- Session notes
- Domain knowledge
- Work products

## What Is NOT Included

The following **Framework_Configuration** is NOT exported:

- Agent identity (`.aget/version.json`, `.aget/identity.json`)
- Capability definitions (`.aget/skills/`)
- Persona configuration (`.aget/persona/`)
- Reasoning patterns (`.aget/reasoning/`)
- Context rules (`.aget/context/`)
- Validation patterns (`.aget/patterns/`)

## Operating Without AGET Framework

By using this exported content outside the AGET framework, you acknowledge:

1. **No Session Protocols**: Wake-up/wind-down protocols are not available
2. **No Validation**: Capability and composition validation is not enforced
3. **No Governance Intensity**: Governance modes (minimal/balanced/rigorous) do not apply
4. **No Memory Architecture**: Six-layer memory model is not active
5. **No Fleet Coordination**: Inter-agent communication is not available

## License

- **L-docs** (`.aget/evolution/`): Apache 2.0 (framework license)
- **Other content**: Subject to original agent's license (user's choice)

## Returning to AGET

To return this content to an AGET agent:

1. Create new agent from template: `instantiate_template.py`
2. Copy governance/, planning/, sessions/, knowledge/ directories
3. Copy L-docs to `.aget/evolution/`
4. Run validation: `python3 -m pytest tests/`

---

*Exported per AGET_PORTABILITY_SPEC CAP-PORT-002*
*"Portability requires visibility. Visibility enables choice."*
"""

    def _get_dir_size(self, path: Path) -> int:
        """Get total size of directory."""
        total = 0
        for f in path.rglob("*"):
            if f.is_file():
                total += f.stat().st_size
        return total

    def _count_files(self, path: Path) -> int:
        """Count files in directory."""
        return len([f for f in path.rglob("*") if f.is_file()])

    def _human_size(self, size: int) -> str:
        """Convert bytes to human-readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size < 1024:
                return f"{size:.1f} {unit}"
            size /= 1024
        return f"{size:.1f} TB"


def main():
    parser = argparse.ArgumentParser(
        description="Export portable knowledge from AGET agent (CAP-PORT-002)"
    )
    parser.add_argument(
        "agent_path",
        help="Path to agent directory"
    )
    parser.add_argument(
        "--output", "-o",
        help="Output directory or file"
    )
    parser.add_argument(
        "--format", "-f",
        choices=["directory", "tar.gz"],
        default="directory",
        help="Export format (default: directory)"
    )
    parser.add_argument(
        "--check",
        action="store_true",
        help="Show what would be exported without exporting"
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

    exporter = KnowledgeExporter(agent_path)

    # Check mode
    if args.check:
        analysis = exporter.analyze()

        print(f"Export Analysis: {agent_path.name}")
        print("=" * 60)
        print()

        print("WILL EXPORT (Portable Content):")
        for item in analysis["export_items"]:
            size = exporter._human_size(item.get("size", 0))
            files = item.get("file_count", 1)
            category = item.get("category", "")
            print(f"  + {item['path']:<30} ({size}, {files} files) [{category}]")

        print()
        print("WILL SKIP (Framework Locked):")
        for item in analysis["skip_items"]:
            print(f"  - {item['path']:<30} ({item['reason']})")

        print()
        print("SUMMARY:")
        summary = analysis["summary"]
        print(f"  Export: {summary['export_count']} items")
        print(f"  Skip: {summary['skip_count']} items")
        print(f"  Total size: {summary['total_size_human']}")
        print(f"  Total files: {summary['total_files']}")

        sys.exit(0)

    # Export mode
    if not args.output:
        parser.error("--output is required for export")

    output_path = Path(args.output)
    if not output_path.is_absolute():
        output_path = Path.cwd() / output_path

    print(f"Exporting knowledge from: {agent_path.name}")
    print(f"Output: {output_path}")
    print(f"Format: {args.format}")
    print()

    result = exporter.export(output_path, format=args.format)

    if result["success"]:
        print("SUCCESS: Knowledge exported")
        print(f"  Output: {result['output']}")
        if "size_human" in result:
            print(f"  Size: {result['size_human']}")
        if "copied" in result:
            print(f"  Items: {len(result['copied'])}")

        print()
        print("IMPORTANT: Review CONSTRAINT_ACKNOWLEDGMENT.md in export")
    else:
        print(f"ERROR: {result['error']}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
