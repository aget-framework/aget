#!/usr/bin/env python3
"""
generate_template_ontology.py - Generate SKOS+EARS ontology for AGET templates

Per L481 (Ontology-Driven Agent Creation) and L482 (SKOS+EARS Grounding),
templates must have vocabulary specifications that DRIVE instance behavior.

Usage:
    python3 generate_template_ontology.py --template template-researcher-aget
    python3 generate_template_ontology.py --template template-researcher-aget --output-dir ./specs/
    python3 generate_template_ontology.py --all  # Generate for all templates

Outputs:
    specs/{ARCHETYPE}_VOCABULARY.md   - SKOS vocabulary specification
    specs/{ARCHETYPE}_SPEC.md         - EARS capability specification

References:
    - L481: Ontology-Driven Agent Creation
    - L482: Executable Ontology - SKOS+EARS Grounding
    - R-REL-015: Template Ontology Conformance
"""

import argparse
import json
import os
import sys
from datetime import date
from pathlib import Path

# Archetype-specific vocabulary terms
ARCHETYPE_VOCABULARIES = {
    "Researcher": {
        "domain": "research",
        "core_concepts": [
            ("Research_Question", "A focused inquiry that guides investigation and discovery"),
            ("Knowledge_Gap", "An identified area where current understanding is incomplete"),
            ("Evidence", "Data, observations, or facts that support or refute a hypothesis"),
            ("Synthesis", "Integration of multiple sources into coherent understanding"),
            ("Discovery", "New knowledge or insight gained through systematic investigation"),
        ],
        "capabilities": [
            ("CAP-RES-001", "Systematic Investigation", "Conduct methodical exploration of research questions"),
            ("CAP-RES-002", "Source Evaluation", "Assess credibility and relevance of information sources"),
            ("CAP-RES-003", "Knowledge Synthesis", "Integrate findings into coherent conclusions"),
        ],
    },
    "Spec_Engineer": {
        "domain": "specification",
        "core_concepts": [
            ("Requirement", "A documented need that a system must satisfy"),
            ("EARS_Pattern", "Easy Approach to Requirements Syntax - structured requirement format"),
            ("Capability", "A discrete function or behavior the system provides"),
            ("Constraint", "A limitation or restriction on system design or behavior"),
            ("Verification", "Process of confirming requirement satisfaction"),
        ],
        "capabilities": [
            ("CAP-SE-001", "Requirements Elicitation", "Extract and document stakeholder needs"),
            ("CAP-SE-002", "EARS Formalization", "Transform needs into EARS-compliant requirements"),
            ("CAP-SE-003", "Specification Validation", "Verify specs are complete, consistent, and testable"),
        ],
    },
    "Advisor": {
        "domain": "advisory",
        "core_concepts": [
            ("Recommendation", "A suggested course of action based on analysis"),
            ("Trade_Off", "Comparative evaluation of competing options"),
            ("Risk_Assessment", "Identification and evaluation of potential negative outcomes"),
            ("Best_Practice", "Proven approach that produces reliable results"),
            ("Stakeholder_Context", "Understanding of who is affected by decisions"),
        ],
        "capabilities": [
            ("CAP-ADV-001", "Contextual Analysis", "Understand situation before advising"),
            ("CAP-ADV-002", "Option Evaluation", "Compare alternatives with trade-off analysis"),
            ("CAP-ADV-003", "Actionable Guidance", "Provide clear, implementable recommendations"),
        ],
    },
    "Consultant": {
        "domain": "consulting",
        "core_concepts": [
            ("Engagement", "A scoped consulting interaction with defined objectives"),
            ("Deliverable", "A tangible work product provided to the client"),
            ("Assessment", "Systematic evaluation of current state"),
            ("Transformation", "Planned change from current to desired state"),
            ("Value_Proposition", "Clear articulation of benefit provided"),
        ],
        "capabilities": [
            ("CAP-CON-001", "Problem Diagnosis", "Identify root causes of client challenges"),
            ("CAP-CON-002", "Solution Design", "Develop approaches to address identified issues"),
            ("CAP-CON-003", "Implementation Support", "Guide execution of recommended changes"),
        ],
    },
    "Developer": {
        "domain": "development",
        "core_concepts": [
            ("Code_Quality", "Attributes that make code maintainable and reliable"),
            ("Implementation", "Translation of design into working code"),
            ("Testing", "Verification that code behaves as expected"),
            ("Refactoring", "Improving code structure without changing behavior"),
            ("Technical_Debt", "Accumulated cost of shortcuts in codebase"),
        ],
        "capabilities": [
            ("CAP-DEV-001", "Code Implementation", "Write clean, functional code"),
            ("CAP-DEV-002", "Code Review", "Evaluate code quality and provide feedback"),
            ("CAP-DEV-003", "Debugging", "Identify and fix code defects"),
        ],
    },
    "Supervisor": {
        "domain": "supervision",
        "core_concepts": [
            ("Fleet", "Collection of agents under supervision"),
            ("Delegation", "Assignment of work to appropriate agents"),
            ("Coordination", "Orchestration of multi-agent activities"),
            ("Escalation", "Raising issues to appropriate authority level"),
            ("Governance", "Rules and processes for agent behavior"),
        ],
        "capabilities": [
            ("CAP-SUP-001", "Fleet Oversight", "Monitor and manage agent fleet"),
            ("CAP-SUP-002", "Work Distribution", "Assign tasks to appropriate agents"),
            ("CAP-SUP-003", "Quality Assurance", "Ensure agent outputs meet standards"),
        ],
    },
    "Worker": {
        "domain": "execution",
        "core_concepts": [
            ("Task", "A discrete unit of work to be completed"),
            ("Execution", "Performance of assigned work"),
            ("Completion_Criteria", "Conditions that define task success"),
            ("Handoff", "Transfer of work or context to another agent"),
            ("Status_Report", "Communication of progress and blockers"),
        ],
        "capabilities": [
            ("CAP-WRK-001", "Task Execution", "Complete assigned work reliably"),
            ("CAP-WRK-002", "Progress Reporting", "Communicate status accurately"),
            ("CAP-WRK-003", "Escalation", "Raise blockers appropriately"),
        ],
    },
    "Analyst": {
        "domain": "analysis",
        "core_concepts": [
            ("Data", "Raw information to be analyzed"),
            ("Pattern", "Recurring structure or trend in data"),
            ("Insight", "Actionable understanding derived from analysis"),
            ("Metric", "Quantifiable measure of a characteristic"),
            ("Visualization", "Visual representation of data or findings"),
        ],
        "capabilities": [
            ("CAP-ANL-001", "Data Analysis", "Extract meaning from data"),
            ("CAP-ANL-002", "Pattern Recognition", "Identify trends and anomalies"),
            ("CAP-ANL-003", "Insight Communication", "Present findings clearly"),
        ],
    },
    "Architect": {
        "domain": "architecture",
        "core_concepts": [
            ("Architecture", "Fundamental structure of a system"),
            ("Component", "Discrete unit within an architecture"),
            ("Interface", "Boundary between components"),
            ("Quality_Attribute", "Non-functional requirement like performance or security"),
            ("Design_Decision", "Significant choice affecting system structure"),
        ],
        "capabilities": [
            ("CAP-ARC-001", "System Design", "Define system structure and components"),
            ("CAP-ARC-002", "Trade-Off Analysis", "Evaluate architectural alternatives"),
            ("CAP-ARC-003", "Documentation", "Record architecture decisions and rationale"),
        ],
    },
    "Executive": {
        "domain": "leadership",
        "core_concepts": [
            ("Strategy", "Long-term plan to achieve objectives"),
            ("Decision", "Choice among alternatives with significant impact"),
            ("Priority", "Relative importance of competing demands"),
            ("Resource", "Asset available for allocation"),
            ("Outcome", "Result of strategic actions"),
        ],
        "capabilities": [
            ("CAP-EXE-001", "Strategic Planning", "Define long-term direction"),
            ("CAP-EXE-002", "Decision Making", "Make high-impact choices"),
            ("CAP-EXE-003", "Resource Allocation", "Distribute resources effectively"),
        ],
    },
    "Operator": {
        "domain": "operations",
        "core_concepts": [
            ("Process", "Repeatable sequence of activities"),
            ("Incident", "Unplanned event requiring response"),
            ("Runbook", "Documented procedure for operations"),
            ("Monitoring", "Continuous observation of system state"),
            ("Recovery", "Restoration of normal operations after incident"),
        ],
        "capabilities": [
            ("CAP-OPS-001", "Process Execution", "Follow operational procedures"),
            ("CAP-OPS-002", "Incident Response", "Handle unplanned events"),
            ("CAP-OPS-003", "System Monitoring", "Observe and report system state"),
        ],
    },
    "Reviewer": {
        "domain": "review",
        "core_concepts": [
            ("Artifact", "Work product subject to review"),
            ("Criteria", "Standards against which artifacts are evaluated"),
            ("Finding", "Issue or observation identified during review"),
            ("Severity", "Impact level of a finding"),
            ("Recommendation", "Suggested action based on findings"),
        ],
        "capabilities": [
            ("CAP-REV-001", "Artifact Evaluation", "Assess work products against criteria"),
            ("CAP-REV-002", "Finding Documentation", "Record issues with appropriate detail"),
            ("CAP-REV-003", "Improvement Guidance", "Provide actionable feedback"),
        ],
    },
}


def get_template_identity(template_path: Path) -> dict:
    """Read template identity.json."""
    identity_path = template_path / ".aget" / "identity.json"
    if identity_path.exists():
        with open(identity_path) as f:
            return json.load(f)
    return {}


def get_archetype(identity: dict, template_name: str) -> str:
    """Extract archetype from identity or infer from template name."""
    if "archetype" in identity:
        return identity["archetype"]

    # Infer from template name (e.g., template-researcher-aget -> Researcher)
    name = template_name.replace("template-", "").replace("-aget", "")
    return name.replace("-", "_").title().replace("_", "_")


def generate_vocabulary_md(template_name: str, archetype: str, identity: dict) -> str:
    """Generate SKOS-compliant vocabulary specification."""
    vocab = ARCHETYPE_VOCABULARIES.get(archetype, ARCHETYPE_VOCABULARIES.get("Worker"))
    domain = vocab["domain"]
    today = date.today().isoformat()

    # Build concepts section
    concepts_yaml = ""
    for concept_name, definition in vocab["core_concepts"]:
        concepts_yaml += f"""
### {concept_name}

```yaml
{concept_name}:
  skos:prefLabel: "{concept_name.replace('_', ' ')}"
  skos:definition: "{definition}"
  skos:broader: {archetype}_Core_Concepts
  skos:inScheme: {archetype}_Vocabulary
```
"""

    return f"""# {archetype} Domain Vocabulary

**Version**: 1.0.0
**Status**: Active
**Owner**: {template_name}
**Created**: {today}
**Scope**: Template vocabulary (DRIVES instance behavior per L481)
**Archetype**: {archetype}

---

## Meta

```yaml
vocabulary:
  meta:
    domain: "{domain}"
    version: "1.0.0"
    owner: "{template_name}"
    created: "{today}"
    theoretical_basis:
      - "L481: Ontology-Driven Agent Creation"
      - "L482: Executable Ontology - SKOS+EARS Grounding"
    archetype: "{archetype}"
```

---

## Concept Scheme

```yaml
{archetype}_Vocabulary:
  skos:prefLabel: "{archetype.replace('_', ' ')} Vocabulary"
  skos:definition: "Vocabulary for {archetype.replace('_', ' ').lower()} domain agents"
  skos:hasTopConcept:
    - {archetype}_Core_Concepts
  rdf:type: skos:ConceptScheme
```

---

## Core Concepts
{concepts_yaml}
---

## Extension Points

Instances extending this template vocabulary should:
1. Add domain-specific terms under appropriate broader concepts
2. Maintain SKOS compliance (prefLabel, definition, broader/narrower)
3. Reference foundation L-docs where applicable
4. Use `research_status` for terms under investigation

---

## References

- L481: Ontology-Driven Agent Creation
- L482: Executable Ontology - SKOS+EARS Grounding
- R-REL-015: Template Ontology Conformance
- AGET_VOCABULARY_SPEC.md

---

*{archetype}_VOCABULARY.md v1.0.0 — SKOS-compliant template vocabulary*
*Generated: {today}*
"""


def generate_spec_md(template_name: str, archetype: str, identity: dict) -> str:
    """Generate EARS-compliant capability specification."""
    vocab = ARCHETYPE_VOCABULARIES.get(archetype, ARCHETYPE_VOCABULARIES.get("Worker"))
    today = date.today().isoformat()
    north_star = identity.get("north_star", f"Provide {archetype.lower().replace('_', ' ')} capabilities")

    # Build requirements section
    requirements = ""
    for cap_id, cap_name, cap_desc in vocab["capabilities"]:
        requirements += f"""
### {cap_id}: {cap_name}

**WHEN** performing {archetype.lower().replace('_', ' ')} activities
**THE** agent SHALL {cap_desc.lower()}

**Rationale**: Core {archetype.replace('_', ' ').lower()} capability
**Verification**: Instance demonstrates capability in operation
"""

    return f"""# {archetype} Capability Specification

**Version**: 1.0.0
**Status**: Active
**Owner**: {template_name}
**Created**: {today}
**Archetype**: {archetype}

---

## Purpose

{north_star}

---

## Scope

This specification defines the core capabilities that all {archetype.replace('_', ' ').lower()} instances must provide.

### In Scope

- Core {archetype.replace('_', ' ').lower()} capabilities ({len(vocab['capabilities'])} requirements)
- EARS-compliant requirement format
- Verification approach

### Out of Scope

- Instance-specific extensions
- Integration with specific tools or systems

---

## Requirements
{requirements}
---

## Verification

| Requirement | Verification Method |
|-------------|---------------------|
{chr(10).join([f"| {cap[0]} | Operational demonstration |" for cap in vocab['capabilities']])}

---

## References

- L481: Ontology-Driven Agent Creation
- L482: Executable Ontology - SKOS+EARS Grounding
- {archetype}_VOCABULARY.md
- AGET_INSTANCE_SPEC.md

---

*{archetype}_SPEC.md v1.0.0 — EARS-compliant capability specification*
*Generated: {today}*
"""


def generate_ontology(template_path: Path, output_dir: Path = None) -> tuple:
    """Generate vocabulary and spec for a template."""
    template_name = template_path.name
    identity = get_template_identity(template_path)
    archetype = get_archetype(identity, template_name)

    # Normalize archetype to match our dictionary
    archetype_normalized = archetype.replace(" ", "_").replace("-", "_")
    if archetype_normalized not in ARCHETYPE_VOCABULARIES:
        # Try to match by first word
        for known in ARCHETYPE_VOCABULARIES:
            if known.lower() in archetype_normalized.lower():
                archetype_normalized = known
                break

    if output_dir is None:
        output_dir = template_path / "specs"

    output_dir.mkdir(parents=True, exist_ok=True)

    vocab_content = generate_vocabulary_md(template_name, archetype_normalized, identity)
    spec_content = generate_spec_md(template_name, archetype_normalized, identity)

    vocab_path = output_dir / f"{archetype_normalized}_VOCABULARY.md"
    spec_path = output_dir / f"{archetype_normalized}_SPEC.md"

    with open(vocab_path, 'w') as f:
        f.write(vocab_content)

    with open(spec_path, 'w') as f:
        f.write(spec_content)

    return vocab_path, spec_path


def main():
    parser = argparse.ArgumentParser(
        description="Generate SKOS+EARS ontology for AGET templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__
    )
    parser.add_argument(
        "--template", "-t",
        help="Template name or path (e.g., template-researcher-aget)"
    )
    parser.add_argument(
        "--output-dir", "-o",
        help="Output directory (default: template/specs/)"
    )
    parser.add_argument(
        "--all", "-a",
        action="store_true",
        help="Generate ontologies for all templates"
    )
    parser.add_argument(
        "--framework-dir",
        default="/Users/gabormelli/github/aget-framework",
        help="Path to aget-framework directory"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show what would be generated without writing files"
    )

    args = parser.parse_args()

    framework_dir = Path(args.framework_dir)

    if args.all:
        templates = sorted(framework_dir.glob("template-*-aget"))
        if not templates:
            print(f"ERROR: No templates found in {framework_dir}")
            sys.exit(1)

        print(f"Generating ontologies for {len(templates)} templates...")
        for template_path in templates:
            if args.dry_run:
                identity = get_template_identity(template_path)
                archetype = get_archetype(identity, template_path.name)
                print(f"  {template_path.name} -> {archetype}_VOCABULARY.md, {archetype}_SPEC.md")
            else:
                vocab_path, spec_path = generate_ontology(template_path)
                print(f"  {template_path.name}")
                print(f"    -> {vocab_path}")
                print(f"    -> {spec_path}")

        print(f"\n{'Would generate' if args.dry_run else 'Generated'} {len(templates) * 2} files")

    elif args.template:
        template_path = Path(args.template)
        if not template_path.is_absolute():
            template_path = framework_dir / args.template

        if not template_path.exists():
            print(f"ERROR: Template not found: {template_path}")
            sys.exit(1)

        output_dir = Path(args.output_dir) if args.output_dir else None

        if args.dry_run:
            identity = get_template_identity(template_path)
            archetype = get_archetype(identity, template_path.name)
            out = output_dir or template_path / "specs"
            print(f"Would generate:")
            print(f"  {out / f'{archetype}_VOCABULARY.md'}")
            print(f"  {out / f'{archetype}_SPEC.md'}")
        else:
            vocab_path, spec_path = generate_ontology(template_path, output_dir)
            print(f"Generated:")
            print(f"  {vocab_path}")
            print(f"  {spec_path}")

    else:
        parser.print_help()
        sys.exit(1)


if __name__ == "__main__":
    main()
