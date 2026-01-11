# SOP: Learning Publication

**Version**: 1.0.0
**Created**: 2026-01-11
**Owner**: aget-framework
**Implements**: CAP-EVOL-007 (Public Learning Publication), CP-008
**Related**: L455 (Migration AGENTS.md Invocation Gap), L457 (Cross-Machine Pre-Flight), AGET_EVOLUTION_SPEC, AGET_LDOC_SPEC

---

## Purpose

Standard operating procedure for publishing Learning documents from private `.aget/evolution/` directories to the public `docs/learnings/` directory. Ensures consistent quality, sanitization, and discoverability of published learnings.

---

## Scope

**Applies to**: All Learning documents considered for public publication

**Covers**:
- Selection criteria for publication candidates
- Sanitization of internal references
- Publication metadata requirements
- Verification of published content

**Does NOT cover**:
- Private L-doc creation (see AGET_LDOC_SPEC)
- Pattern graduation (see CP-003)
- Framework releases (see SOP_release_process.md)

---

## Prerequisites

Before starting Learning Publication:

1. **Source L-doc exists**: Valid L-doc in `.aget/evolution/` with v2 format
2. **Pattern validated**: Learning has been applied successfully 2+ times
3. **Fleet-wide applicability**: Learning applies beyond single agent
4. **No blocking dependencies**: Publication doesn't reveal unreleased features

---

## Procedure

### Gate 1: Selection

**Objective**: Determine if L-doc is a publication candidate

#### 1.1 Selection Criteria Checklist

| # | Criterion | Check |
|---|-----------|-------|
| 1.1.1 | L-doc has fleet-wide or universal applicability | [ ] |
| 1.1.2 | Pattern executed successfully 2+ times | [ ] |
| 1.1.3 | No internal references that cannot be generalized | [ ] |
| 1.1.4 | Provides clear value to external users | [ ] |
| 1.1.5 | Does not expose unreleased framework features | [ ] |

#### V-SEL-001: Applicability Check

```bash
# Review L-doc for scope indicators
grep -i "fleet\|universal\|all agents\|any agent" /path/to/source/L###_*.md
# Expected: At least one indicator of broad applicability
```

**Decision Point**: Selection criteria met? [GO/NOGO]

- **GO**: Proceed to Gate 2 (Sanitization)
- **NOGO**: Document reason, defer or reject

---

### Gate 2: Sanitization

**Objective**: Remove internal references, generalize content for external consumption

#### 2.1 Sanitization Checklist

| # | Check | Find Pattern | Replace With |
|---|-------|--------------|--------------|
| 2.1.1 | No `.aget/` paths | `.aget/evolution/` | `.aget/evolution/` (keep) or remove |
| 2.1.2 | No private agent names | `private-*-AGET` | `your-agent` or remove |
| 2.1.3 | No internal paths | `~/github/GM-*` | `/path/to/your/` |
| 2.1.4 | No internal tracking | `#123` (internal issue) | Remove or generalize |
| 2.1.5 | No machine-specific paths | `/Users/username/` | `/path/to/your/` |

#### V-SAN-001: Internal Reference Check

```bash
SOURCE_FILE="/path/to/source/L###_*.md"

# Check for private agent names
! grep -q "private-.*-AGET" "$SOURCE_FILE" && echo "PASS: No private agents" || echo "FAIL: Sanitize agent names"

# Check for internal paths
! grep -q "~/github/GM-\|/Users/[a-z]*/" "$SOURCE_FILE" && echo "PASS: No internal paths" || echo "FAIL: Generalize paths"
```

#### 2.2 Content Generalization

- Replace specific agent names with generic references
- Replace internal tracking numbers with descriptions
- Ensure V-tests use placeholder paths
- Add "Common Locations" section if path-dependent

**Decision Point**: Sanitization complete? [GO/NOGO]

- **GO**: Proceed to Gate 3 (Publication)
- **NOGO**: Complete sanitization, re-verify

---

### Gate 3: Publication

**Objective**: Create Published_Learning in `docs/learnings/`

#### 3.1 Publication Steps

1. **Copy sanitized content** to `docs/learnings/L###_*.md`
2. **Preserve L-number** from source (CAP-EVOL-007-04)
3. **Add publication metadata** (optional but recommended):

```markdown
---
publication_date: YYYY-MM-DD
source: ".aget/evolution/L###_*.md"
applicability: fleet | universal
---
```

4. **Update Integration Points** section to reflect public location

#### 3.2 File Naming

```
docs/learnings/L{NUMBER}_{snake_case_title}.md
```

**Example**: `docs/learnings/L455_migration_agents_md_invocation_gap.md`

#### V-PUB-001: File Created

```bash
TARGET="docs/learnings/L###_*.md"  # Replace with actual path
test -f "$TARGET" && echo "PASS: File exists" || echo "FAIL: Create file"
```

**Decision Point**: Publication complete? [GO/NOGO]

- **GO**: Proceed to Gate 4 (Verification)
- **NOGO**: Complete publication steps

---

### Gate 4: Verification

**Objective**: Validate Published_Learning meets quality standards

#### 4.1 Run Validator

```bash
python3 validation/validate_public_learnings.py docs/learnings/L###_*.md
```

**Expected**: All checks pass or only WARN-level issues

#### 4.2 Verification Checklist

| # | Check | Command | Expected |
|---|-------|---------|----------|
| 4.2.1 | File pattern valid | `ls docs/learnings/L*.md` | File listed |
| 4.2.2 | Has ## Learning section | `grep "## Learning"` | Match found |
| 4.2.3 | Has ## Evidence section | `grep "## Evidence"` | Match found |
| 4.2.4 | No private references | `grep -v "private-"` | No matches |
| 4.2.5 | No internal paths | `grep -v "~/github/GM-"` | No matches |

#### V-PUB-002: Full Validation

```bash
# Run all checks
python3 validation/validate_public_learnings.py docs/learnings/

# Expected output:
# ✅ L455: PASS
# ✅ L457: PASS
# ✅ L###: PASS (new file)
```

**Decision Point**: Verification passed? [COMPLETE/NOGO]

- **COMPLETE**: Publication successful, proceed to commit
- **NOGO**: Fix issues, re-run verification

---

## Post-Publication

### Commit Changes

```bash
git add docs/learnings/L###_*.md
git commit -m "docs: Publish L### to docs/learnings/ (CAP-EVOL-007)"
```

### Update Cross-References

If the L-doc is referenced by other documents:
1. Update references to point to `docs/learnings/` location
2. Note in CHANGELOG.md

### Notify Stakeholders

For significant learnings:
- Note in release notes (if bundled with release)
- Reference in FLEET_MIGRATION_GUIDE if migration-related

---

## Rollback

If publication needs to be reverted:

```bash
# Remove published file
git rm docs/learnings/L###_*.md

# Commit rollback
git commit -m "revert: Remove L### from docs/learnings/"
```

**Note**: Source L-doc in `.aget/evolution/` remains unchanged.

---

## Examples

### Example: L455 Publication

**Source**: `.aget/evolution/L455_migration_agents_md_invocation_gap.md`
**Target**: `docs/learnings/L455_migration_agents_md_invocation_gap.md`

**Selection**:
- Fleet-wide applicability: ✅ (affects all agents during migration)
- Pattern executed 3+ times: ✅ (v2.12, v3.0, v3.2.1 migrations)
- No internal references: ✅ (generalized)
- External value: ✅ (prevents first-session failures)

**Sanitization**:
- No private agent names (already general)
- No internal paths (uses placeholders)
- V-tests use generic `$AGENT_PATH`

**Verification**:
```bash
python3 validation/validate_public_learnings.py docs/learnings/L455_migration_agents_md_invocation_gap.md
# ✅ L455: PASS
```

---

## Troubleshooting

| Issue | Cause | Solution |
|-------|-------|----------|
| V-SAN-001 fails | Private agent names in content | Search/replace with generic names |
| V-PUB-002 warns | Missing publication_date | Add metadata (optional, WARN only) |
| Validator not found | Script not deployed | Run from aget/ directory |

---

## References

- AGET_EVOLUTION_SPEC.md (CAP-EVOL-007)
- AGET_LDOC_SPEC.md (L-doc format)
- CP-008 (Public Learning Governance)
- validate_public_learnings.py (Validator)

---

## Changelog

### v1.0.0 (2026-01-11)

- Initial SOP
- Four gates: Selection, Sanitization, Publication, Verification
- Implements CAP-EVOL-007 requirements
- Example walkthrough (L455)

---

## Graduation History

```yaml
graduation:
  source: "PROJECT_PLAN_public_learning_governance_v1.0.md"
  trigger: "Gap analysis revealed docs/learnings/ lacked formal governance"
  rationale: "Formalize ad-hoc publication pattern observed with L455, L457"
```

---

*SOP_learning_publication.md - Learning publication procedure for AGET framework*
