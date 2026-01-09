# Vocabulary Prose Migration Guide

**Version**: 1.0.0
**Status**: Active
**Created**: 2026-01-09
**Source**: L493 (Vocabulary_Prose_Marking_Pattern)

---

## Overview

This guide helps migrate AGET documentation from informal prose to L493-compliant prose where all AGET Vocabulary terms are self-disambiguating compound forms.

## Core Principle

> **Self-disambiguation by construction eliminates context-dependent judgment.**

If all AGET Vocabulary terms are compound (`Aget_Agent`, `Task_Entity`, `Aget_Session`), they are unambiguous in ANY context.

---

## Before/After Examples

### Example 1: Capability Purpose

**Before (Ambiguous)**:
```yaml
purpose: |
  Enable agents to track action items that emerge from sessions.
```

**After (Self-Disambiguating)**:
```yaml
purpose: |
  Enable Aget_Instances to track Action_Items that emerge from Aget_Sessions.
```

**Analysis**:
| Before | After | Rationale |
|--------|-------|-----------|
| agents | Aget_Instances | "agents" is generic English |
| action items | Action_Items | Compound Vocabulary term |
| sessions | Aget_Sessions | "sessions" is generic English |

---

### Example 2: L-Document Description

**Before**:
```markdown
The agent uses a session protocol to initialize the workspace and load capabilities.
```

**After**:
```markdown
The Aget_Instance uses a Session_Protocol to initialize the Aget_Workspace and load Aget_Capabilities.
```

---

### Example 3: Specification Requirement

**Before**:
```markdown
The template must include identity configuration and behavior specification.
```

**After**:
```markdown
The Aget_Template must include Version_Json (identity) and Agents_Md (behavior).
```

---

## Term Migration Table

### Core Framework Terms

| Generic/Old | Compound Form | Notes |
|-------------|---------------|-------|
| agent | Aget_Instance | Concrete agent |
| Agent | Aget_Agent | Abstract concept |
| session | Aget_Session | Framework session |
| capability | Aget_Capability | Framework capability |
| template | Aget_Template | Agent template |
| principal | Aget_Principal | Human operator |
| fleet | Aget_Fleet | Agent collection |
| supervisor | Aget_Supervisor | Supervising agent |
| portfolio | Aget_Portfolio | Organizational group |

### EKO Terms (Abstraction Axis)

| Old | New | Category |
|-----|-----|----------|
| Algorithm | Algorithm_Concept | Aget_Concept |
| Process | Process_Concept | Aget_Concept |
| Procedure | Procedure_Concept | Aget_Concept |
| Function | Function_Concept | Aget_Concept |
| Workflow | Workflow_Concept | Aget_Concept |
| Protocol | Protocol_Concept | Aget_Concept |

### EKO Terms (Determinism Axis)

| Old | New | Category |
|-----|-----|----------|
| Deterministic | Deterministic_Property | Aget_Property |
| Probabilistic | Probabilistic_Property | Aget_Property |
| Syllogistic | Syllogistic_Property | Aget_Property |

### EKO Terms (Reusability Axis)

| Old | New | Category |
|-----|-----|----------|
| Universal | Universal_Property | Aget_Property |
| Parameterized | Parameterized_Property | Aget_Property |
| One_Time | One_Time_Property | Aget_Property |

### Artifact Types

| Old | New | Notes |
|-----|-----|-------|
| SOP | SOP_Artifact | Standard Operating Procedure |
| Runbook | Runbook_Artifact | Operational runbook |
| Playbook | Playbook_Artifact | Strategic playbook |

### Domain Entities

| Old | New | Category |
|-----|-----|----------|
| Person | Person_Entity | Continuant_Category |
| Organization | Organization_Entity | Continuant_Category |
| Document | Document_Entity | Continuant_Category |
| Project | Project_Entity | Continuant_Category |
| Task | Task_Entity | Occurrent_Category |
| Event | Event_Entity | Occurrent_Category |
| Decision | Decision_Entity | Abstract_Category |
| Requirement | Requirement_Entity | Abstract_Category |

---

## Migration Scripts

### sed Scripts for Common Migrations

```bash
# Core framework terms
sed -i 's/\bagent\b/Aget_Instance/g' file.md
sed -i 's/\bAgent\b/Aget_Agent/g' file.md
sed -i 's/\bsession\b/Aget_Session/g' file.md
sed -i 's/\bSession\b/Aget_Session/g' file.md
sed -i 's/\bcapability\b/Aget_Capability/g' file.md
sed -i 's/\btemplate\b/Aget_Template/g' file.md
sed -i 's/\bprincipal\b/Aget_Principal/g' file.md

# EKO concept terms
sed -i 's/\bAlgorithm\b/Algorithm_Concept/g' file.md
sed -i 's/\bProtocol\b/Protocol_Concept/g' file.md
sed -i 's/\bWorkflow\b/Workflow_Concept/g' file.md

# EKO property terms
sed -i 's/\bDeterministic\b/Deterministic_Property/g' file.md
sed -i 's/\bProbabilistic\b/Probabilistic_Property/g' file.md
sed -i 's/\bSyllogistic\b/Syllogistic_Property/g' file.md

# Domain entities
sed -i 's/\bPerson\b/Person_Entity/g' file.md
sed -i 's/\bOrganization\b/Organization_Entity/g' file.md
sed -i 's/\bDocument\b/Document_Entity/g' file.md
sed -i 's/\bTask\b/Task_Entity/g' file.md
```

### Batch Migration Script

```bash
#!/bin/bash
# migrate_vocabulary_prose.sh
# Migrate a file to L493-compliant prose

FILE=$1

if [ -z "$FILE" ]; then
    echo "Usage: migrate_vocabulary_prose.sh <file>"
    exit 1
fi

# Create backup
cp "$FILE" "${FILE}.bak"

# Framework terms
sed -i '' 's/\bagent\b/Aget_Instance/g' "$FILE"
sed -i '' 's/\bsession\b/Aget_Session/g' "$FILE"
sed -i '' 's/\bcapability\b/Aget_Capability/g' "$FILE"
sed -i '' 's/\btemplate\b/Aget_Template/g' "$FILE"

echo "Migrated: $FILE"
echo "Backup: ${FILE}.bak"
echo ""
echo "Review changes with: diff ${FILE}.bak $FILE"
```

---

## Regex Patterns

### Detect AGET Vocabulary Terms

```regex
# Match compound terms (correct)
[A-Z][a-z]+(_[A-Z][a-z0-9]+)+

# Examples matched:
# Aget_Instance
# Action_Item
# Session_Handoff
# Algorithm_Concept
```

### Detect Potential Violations

```regex
# Single capitalized word that might be vocabulary
\b[A-Z][a-z]+\b(?!_)

# Lowercase term that might need marking
\b(agent|session|capability|template|principal)\b
```

---

## Validation

After migration, validate with:

```bash
# Check vocabulary spec terms
python validation/validate_vocabulary_prose.py --check-terms specs/AGET_VOCABULARY_SPEC.md

# Check prose in migrated file
python validation/validate_vocabulary_prose.py --check-prose path/to/file.md
```

---

## Migration Checklist

- [ ] Identify all generic English that refers to AGET concepts
- [ ] Replace with exact `skos:prefLabel` compound form
- [ ] Run validator to catch inconsistencies
- [ ] Review context to ensure meaning preserved
- [ ] Update any cross-references

---

## When NOT to Migrate

Keep lowercase/generic when:
- The word is truly generic English, not AGET vocabulary
- The context is clearly non-AGET (external documentation)
- The term is in a code block showing external system

**Examples**:
```markdown
# Keep generic (not AGET vocabulary)
"The user session expired" → "session" is HTTP session, not Aget_Session
"Work commitments" → generic phrase, not AGET term
"Template method pattern" → software pattern, not Aget_Template
```

---

## References

- L493: Vocabulary_Prose_Marking_Pattern
- L494: Vocabulary_Meta_Ontology_Pattern
- AGET_VOCABULARY_SPEC.md: Canonical term definitions
- validate_vocabulary_prose.py: Automated validation

---

*Vocabulary Prose Migration Guide v1.0.0*
*"Self-disambiguation by construction"*
