#!/usr/bin/env python3
"""
validate_ontology_inheritance.py - Validate ontology inheritance chains

Per CAP-INST-007: The system shall validate ontology inheritance declarations
at gate boundaries. Resolves `extends:` references, detects phantom inheritance,
flags term collisions, and checks acyclic chains.

Usage:
    python3 validate_ontology_inheritance.py                 # Scan current agent
    python3 validate_ontology_inheritance.py --dir /path     # Scan specific agent
    python3 validate_ontology_inheritance.py --check         # Exit 0/1 for CI
    python3 validate_ontology_inheritance.py --verbose       # Show all refs checked
    python3 validate_ontology_inheritance.py --test          # Self-test

Specification: AGET_INSTANCE_SPEC.md CAP-INST-007
Source: L601, L602, L608 (density constraint: reduce noise, not add rules)
"""

import argparse
import os
import sys
from pathlib import Path
from typing import Dict, List, NamedTuple, Optional, Set

# Try to import yaml; fall back gracefully
try:
    import yaml
    HAS_YAML = True
except ImportError:
    HAS_YAML = False


class OntologyRef(NamedTuple):
    """A resolved ontology reference."""
    source_file: str
    extends_target: str
    resolved_path: Optional[str]
    resolved: bool


class Finding(NamedTuple):
    """A validation finding."""
    severity: str  # ERROR, WARN
    source: str
    message: str


def find_agent_root(start_path: Optional[Path] = None) -> Optional[Path]:
    """Find agent root by looking for .aget/ directory."""
    path = Path(start_path).resolve() if start_path else Path.cwd()

    for _ in range(4):
        if (path / '.aget').is_dir():
            return path
        if path.parent == path:
            break
        path = path.parent
    return None


def find_framework_root(agent_path: Path) -> Optional[Path]:
    """Find framework root (parent containing aget/)."""
    current = agent_path
    for _ in range(4):
        if (current / 'aget').is_dir():
            return current
        current = current.parent
        if current == current.parent:
            break
    return None


def parse_yaml_safe(filepath: Path) -> Optional[dict]:
    """Parse a YAML file, returning None on failure."""
    if HAS_YAML:
        try:
            with open(filepath) as f:
                return yaml.safe_load(f)
        except Exception:
            return None

    # Fallback: extract extends from metadata using simple parsing
    try:
        content = filepath.read_text(encoding='utf-8')
        data = {'metadata': {}, 'concepts': []}
        in_metadata = False

        for line in content.split('\n'):
            stripped = line.strip()
            if stripped == 'metadata:':
                in_metadata = True
                continue
            if in_metadata:
                if stripped and not stripped.startswith('#') and not line.startswith(' '):
                    in_metadata = False
                    continue
                if stripped.startswith('extends:'):
                    value = stripped.split(':', 1)[1].strip()
                    data['metadata']['extends'] = value
                elif stripped.startswith('name:'):
                    data['metadata']['name'] = stripped.split(':', 1)[1].strip()

            # Extract concept prefLabels for collision detection
            if stripped.startswith('prefLabel:'):
                value = stripped.split(':', 1)[1].strip()
                data['concepts'].append({'prefLabel': value})

        return data
    except Exception:
        return None


def scan_ontology_files(agent_path: Path) -> List[Path]:
    """Find all YAML ontology files in agent's ontology/ directory."""
    ontology_dir = agent_path / 'ontology'
    if not ontology_dir.is_dir():
        return []

    files = []
    for f in ontology_dir.iterdir():
        if f.is_file() and f.suffix in ('.yaml', '.yml'):
            files.append(f)
    return sorted(files)


def resolve_extends(source_file: Path, extends_target: str,
                    agent_path: Path, framework_root: Optional[Path]) -> Optional[Path]:
    """Resolve an extends: reference to an actual file path.

    Search order:
    1. Same directory as source file
    2. Agent's ontology/ directory
    3. Framework aget/ontology/ directory (if framework root found)
    4. Any template-*/ontology/ directory in framework root
    """
    candidates = [
        source_file.parent / extends_target,
        agent_path / 'ontology' / extends_target,
    ]

    if framework_root:
        candidates.append(framework_root / 'aget' / 'ontology' / extends_target)
        # Search in all agents/templates under framework root
        for d in framework_root.iterdir():
            if d.is_dir() and (d / 'ontology' / extends_target).exists():
                candidates.append(d / 'ontology' / extends_target)

    for candidate in candidates:
        if candidate.exists():
            return candidate.resolve()

    return None


def extract_prefLabels(filepath: Path) -> Set[str]:
    """Extract all prefLabel values from an ontology file."""
    data = parse_yaml_safe(filepath)
    if not data:
        return set()

    labels = set()

    # Handle concepts list
    concepts = data.get('concepts', [])
    if isinstance(concepts, list):
        for concept in concepts:
            if isinstance(concept, dict):
                label = concept.get('prefLabel', '')
                if label:
                    labels.add(str(label))

    # Handle conceptScheme.concepts (alternative structure)
    scheme = data.get('conceptScheme', {})
    if isinstance(scheme, dict):
        for concept in scheme.get('concepts', []):
            if isinstance(concept, dict):
                label = concept.get('prefLabel', '')
                if label:
                    labels.add(str(label))

    return labels


def validate_inheritance(agent_path: Path, framework_root: Optional[Path],
                         verbose: bool = False) -> tuple:
    """Validate ontology inheritance chains.

    Returns (refs, findings) tuple.
    """
    refs = []
    findings = []
    ontology_files = scan_ontology_files(agent_path)

    if not ontology_files:
        return refs, findings

    # Build inheritance graph for cycle detection
    graph = {}  # source -> target (resolved paths)

    for ont_file in ontology_files:
        data = parse_yaml_safe(ont_file)
        if not data:
            continue

        metadata = data.get('metadata', {})
        if not isinstance(metadata, dict):
            continue

        extends_target = metadata.get('extends', '')
        if not extends_target:
            continue

        rel_source = str(ont_file.relative_to(agent_path))
        resolved = resolve_extends(ont_file, extends_target, agent_path, framework_root)

        ref = OntologyRef(
            source_file=rel_source,
            extends_target=extends_target,
            resolved_path=str(resolved) if resolved else None,
            resolved=resolved is not None,
        )
        refs.append(ref)

        if verbose:
            status = "RESOLVED" if resolved else "UNRESOLVED"
            print(f"  REF: {rel_source} extends {extends_target} -> {status}")

        # CAP-INST-007-02: Report unresolvable references
        if not resolved:
            findings.append(Finding(
                severity='ERROR',
                source=rel_source,
                message=f"Phantom inheritance: '{extends_target}' cannot be resolved",
            ))
        else:
            graph[str(ont_file.resolve())] = str(resolved)

            # CAP-INST-007-03: Check term collisions
            source_labels = extract_prefLabels(ont_file)
            target_labels = extract_prefLabels(resolved)
            collisions = source_labels & target_labels

            if collisions:
                collision_list = ', '.join(sorted(collisions)[:5])
                suffix = f" (and {len(collisions) - 5} more)" if len(collisions) > 5 else ""
                findings.append(Finding(
                    severity='WARN',
                    source=rel_source,
                    message=f"Term collision with {extends_target}: {collision_list}{suffix}",
                ))

    # CAP-INST-007-04: Check for cycles
    visited = set()
    for start in graph:
        path = []
        current = start
        while current and current not in visited:
            if current in path:
                cycle = ' -> '.join(
                    [Path(p).name for p in path[path.index(current):]] + [Path(current).name]
                )
                findings.append(Finding(
                    severity='ERROR',
                    source=Path(start).name,
                    message=f"Cyclic inheritance chain: {cycle}",
                ))
                break
            path.append(current)
            current = graph.get(current)
        visited.update(path)

    return refs, findings


def run_self_test() -> bool:
    """Self-test to verify validator behavior."""
    import tempfile
    import shutil

    test_dir = Path(tempfile.mkdtemp(prefix='aget_inherit_test_'))
    passed = 0
    failed = 0

    try:
        # Set up mock agent structure
        (test_dir / '.aget').mkdir()
        (test_dir / 'ontology').mkdir()

        # Create base ontology
        base_content = """apiVersion: aget.framework/v1
kind: OntologySpec
metadata:
  name: base-ontology
  version: 1.0.0
concepts:
  - id: C001
    prefLabel: Agent
  - id: C002
    prefLabel: Session
"""
        (test_dir / 'ontology' / 'ONTOLOGY_base.yaml').write_text(base_content)

        # Create child ontology that extends base (valid)
        child_content = """apiVersion: aget.framework/v1
kind: OntologySpec
metadata:
  name: child-ontology
  extends: ONTOLOGY_base.yaml
concepts:
  - id: D001
    prefLabel: CustomConcept
"""
        (test_dir / 'ontology' / 'ONTOLOGY_child.yaml').write_text(child_content)

        # Create phantom ontology (extends non-existent)
        phantom_content = """apiVersion: aget.framework/v1
kind: OntologySpec
metadata:
  name: phantom-ontology
  extends: ONTOLOGY_nonexistent.yaml
concepts:
  - id: E001
    prefLabel: Orphan
"""
        (test_dir / 'ontology' / 'ONTOLOGY_phantom.yaml').write_text(phantom_content)

        # Create collision ontology (same prefLabel as base)
        collision_content = """apiVersion: aget.framework/v1
kind: OntologySpec
metadata:
  name: collision-ontology
  extends: ONTOLOGY_base.yaml
concepts:
  - id: F001
    prefLabel: Agent
  - id: F002
    prefLabel: NewConcept
"""
        (test_dir / 'ontology' / 'ONTOLOGY_collision.yaml').write_text(collision_content)

        # Test 1: Valid extends resolves
        refs, findings = validate_inheritance(test_dir, None)
        valid_refs = [r for r in refs if r.resolved and 'child' in r.source_file]
        if valid_refs:
            print("  [+] T1 PASS: Valid extends reference resolved")
            passed += 1
        else:
            print(f"  [-] T1 FAIL: Expected valid ref for child, got {len(valid_refs)}")
            failed += 1

        # Test 2: Phantom reference detected
        phantom_findings = [f for f in findings if 'Phantom' in f.message and 'nonexistent' in f.message]
        if phantom_findings:
            print("  [+] T2 PASS: Phantom inheritance detected")
            passed += 1
        else:
            print(f"  [-] T2 FAIL: Expected phantom finding")
            failed += 1

        # Test 3: Term collision flagged
        collision_findings = [f for f in findings if 'collision' in f.message.lower()]
        if collision_findings:
            print("  [+] T3 PASS: Term collision flagged")
            passed += 1
        else:
            print(f"  [-] T3 FAIL: Expected collision finding")
            failed += 1

        # Test 4: No cycles in acyclic graph
        cycle_findings = [f for f in findings if 'Cyclic' in f.message]
        if not cycle_findings:
            print("  [+] T4 PASS: No false cycle detected in acyclic graph")
            passed += 1
        else:
            print(f"  [-] T4 FAIL: False cycle detected")
            failed += 1

        # Test 5: Cycle detection
        # Create cycle: A extends B, B extends A
        (test_dir / 'ontology' / 'ONTOLOGY_phantom.yaml').unlink()
        (test_dir / 'ontology' / 'ONTOLOGY_collision.yaml').unlink()

        cycle_a = """apiVersion: aget.framework/v1
kind: OntologySpec
metadata:
  name: cycle-a
  extends: ONTOLOGY_cycle_b.yaml
concepts:
  - id: CA1
    prefLabel: CycleConceptA
"""
        cycle_b = """apiVersion: aget.framework/v1
kind: OntologySpec
metadata:
  name: cycle-b
  extends: ONTOLOGY_cycle_a.yaml
concepts:
  - id: CB1
    prefLabel: CycleConceptB
"""
        (test_dir / 'ontology' / 'ONTOLOGY_cycle_a.yaml').write_text(cycle_a)
        (test_dir / 'ontology' / 'ONTOLOGY_cycle_b.yaml').write_text(cycle_b)

        # Remove child to simplify
        (test_dir / 'ontology' / 'ONTOLOGY_child.yaml').unlink()

        refs2, findings2 = validate_inheritance(test_dir, None)
        cycle_findings2 = [f for f in findings2 if 'Cyclic' in f.message]
        if cycle_findings2:
            print("  [+] T5 PASS: Cyclic inheritance detected")
            passed += 1
        else:
            print(f"  [-] T5 FAIL: Expected cycle detection")
            failed += 1

    finally:
        shutil.rmtree(test_dir)

    total = passed + failed
    print(f"\n  Self-test: {passed}/{total} PASS")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description='Validate ontology inheritance chains (CAP-INST-007)',
    )
    parser.add_argument(
        '--dir', type=Path,
        help='Agent directory to scan (default: current directory)',
    )
    parser.add_argument(
        '--check', action='store_true',
        help='Exit with code 1 if errors found (CI mode)',
    )
    parser.add_argument(
        '--verbose', action='store_true',
        help='Show all references checked',
    )
    parser.add_argument(
        '--test', action='store_true',
        help='Run self-test',
    )
    args = parser.parse_args()

    if args.test:
        print("validate_ontology_inheritance.py self-test")
        success = run_self_test()
        sys.exit(0 if success else 1)

    # Find agent root
    agent_path = find_agent_root(args.dir)
    if not agent_path:
        print("ERROR: Cannot find .aget/ directory", file=sys.stderr)
        sys.exit(2)

    # Find framework root for cross-scope resolution
    framework_root = find_framework_root(agent_path)

    # Validate
    refs, findings = validate_inheritance(agent_path, framework_root, args.verbose)

    errors = [f for f in findings if f.severity == 'ERROR']
    warnings = [f for f in findings if f.severity == 'WARN']

    # Report
    if findings:
        for finding in findings:
            print(f"  [{finding.severity}] {finding.source}: {finding.message}")

    # Summary
    print(f"\nOntology files scanned: {len(scan_ontology_files(agent_path))}")
    print(f"Inheritance refs checked: {len(refs)}")
    print(f"Errors: {len(errors)} | Warnings: {len(warnings)}")

    if not errors and not warnings:
        print("PASS: All inheritance chains resolve")

    if args.check and errors:
        sys.exit(1)

    sys.exit(0)


if __name__ == '__main__':
    main()
