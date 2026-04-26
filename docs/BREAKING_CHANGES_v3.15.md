# Breaking Changes: v3.15.0

**Release Date**: 2026-04-25
**Governed by**: ADR-022 (Breaking-Change Policy)

v3.15.0 contains two breaking changes: BC-001 and BC-002. Both have structured remediation paths.

---

## BC-001 — Backward-Compat Shim Removed for `version.json` Field Reads

### What Changed

In v3.14.0, `aget_`-prefix normalization (ADR-019) was introduced. A dual-read backward-compatibility shim allowed scripts to reference either old names (`agent_name`) or new names (`aget_agent_name`) when reading `version.json`. **The shim is removed in v3.15.0.**

**Scope clarification**: The `.aget/version.json` file's own key names are **not changed** — the JSON structure continues to use `agent_name`, `domain`, `portfolio`, etc. BC-001 only affects scripts or skills that attempt to read the *new* `aget_`-prefixed names from version.json (which don't exist in the JSON), relying on the shim to resolve them. With the shim removed, those reads now return None/KeyError.

> Confirmed by template-worker-aget canonical state at v3.15.0: version.json retains `agent_name`, `domain`, `portfolio` as-is.

### Who is Affected

Agents that have scripts or skills referencing `aget_agent_name`, `aget_domain`, `aget_portfolio`, etc. when reading `version.json`. (Agents reading the original `agent_name`, `domain`, etc. directly are unaffected.)

### Field Reference Table

Scripts that read version.json should use these names (the actual JSON keys):

| JSON Key (unchanged) | What v3.14 shim mapped from |
|---------------------|----------------------------|
| `agent_name` | `aget_agent_name` |
| `domain` | `aget_domain` |
| `portfolio` | `aget_portfolio` |
| `managed_by` | `aget_managed_by` |
| `manages` | `aget_manages` |
| `instance_type` | `aget_instance_type` |
| `archetype` | `aget_archetype` |
| `specialization` | `aget_specialization` |
| `template` | `aget_template` |
| `identity_file` | `aget_identity_file` |
| `intelligence_enabled` | `aget_intelligence_enabled` |
| `collaboration_enabled` | `aget_collaboration_enabled` |
| `capabilities` | `aget_capabilities` |
| `patterns` | `aget_patterns` |
| `knowledge_inheritance` | `aget_knowledge_inheritance` |

### Detection

Check scripts and skills for references to `aget_`-prefixed names that don't exist in the JSON:

```bash
grep -rE '"(aget_agent_name|aget_domain|aget_portfolio|aget_managed_by|aget_manages|aget_instance_type|aget_archetype|aget_specialization|aget_template|aget_identity_file|aget_intelligence_enabled|aget_collaboration_enabled|aget_capabilities|aget_patterns|aget_knowledge_inheritance)"' \
  scripts/ .claude/ 2>/dev/null
```

Expected: 0 matches (or only in comments/documentation, not code paths).

### Remediation

Update any code that reads `aget_`-prefixed names to read the original names from the table above. The version.json file itself requires no changes.

---

## BC-002 — `--fix` Flag Removed from `/aget-check-health`

### What Changed

The `--fix` flag was documented in `/aget-check-health` (SKILL-003) and 13+ SKILL.md files since 2026-02-10, but was **never implemented** — it existed only as a documented surface with no behavior (L671: Classification Without Consequence). In v3.15.0, the flag is removed. Invoking `--fix` will produce an error.

**ADR-022 exemption**: R-DEP-011 grace-period exemption applies because there were no functional consumers — the flag was decorative. Classified BC-002 because the documented surface creates adopter expectation.

### Who is Affected

- Agents or scripts that invoke `/aget-check-health --fix`
- Any SKILL.md that documents `--fix` as a supported parameter

### Detection

```bash
grep -r -- '--fix' .claude/skills/ scripts/ 2>/dev/null
```

Expected: 0 matches (historical changelog references in comments are acceptable).

### Remediation

Replace `--fix` invocations with the new `/aget-enhance-health` skill (SKILL-049 v1.0.0):

| Old Pattern | New Pattern |
|-------------|-------------|
| `/aget-check-health --fix` | `/aget-enhance-health` |
| `/aget-check-health --fix --scope scripts` | `/aget-enhance-health` (full remediation) |

**Deploy the replacement skill:**

```bash
# Copy from template-worker-aget
cp -r /path/to/aget-framework/template-worker-aget/.claude/skills/aget-enhance-health/ \
      .claude/skills/aget-enhance-health/
```

See: `RELEASE_HANDOFF_v3.15.0.md` Step 3 for deployment details.

---

## Migration Time Estimate

| Agent type | Estimated time |
|-----------|---------------|
| Agent with no aget_-prefixed reads and no --fix usage | ~5 min (version bump only) |
| Agent with aget_-prefixed reads in scripts/skills | ~15–25 min |
| Agent with --fix surfaces to clean up | ~10–20 min |

---

## Rollback

If an upgrade fails, restore from your pre-upgrade git snapshot:

```bash
git stash  # or git checkout -- .
# Verify
python3 -c "import json; print(json.load(open('.aget/version.json'))['aget_version'])"
```

---

## Related

- `DEPLOYMENT_SPEC_v3.15.0.yaml` — machine-readable upgrade spec
- `handoffs/RELEASE_HANDOFF_v3.15.0.md` — step-by-step upgrade guide
- `governance/ADR-022.md` — Breaking-Change Policy
- `docs/VERSION_HISTORY.md` — version history
