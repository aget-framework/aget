# Breaking Changes: v3.15.0

**Release Date**: 2026-04-25
**Governed by**: ADR-022 (Breaking-Change Policy)

v3.15.0 contains two breaking changes: BC-001 and BC-002. Both have structured remediation paths.

---

## BC-001 — `version.json` Old Field Names Removed

### What Changed

19 fields in `.aget/version.json` were renamed in v3.14.0 as part of the `aget_`-prefix normalization (ADR-019). A dual-read backward-compatibility shim allowed both old and new names during the v3.14.x series. **The shim is removed in v3.15.0.** Any script, skill, or agent code reading old names will break.

### Who is Affected

Agents that:
- Still have old field names in their `.aget/version.json` (the *keys* themselves)
- Have scripts or skills that read old field names from `version.json`

### Field Rename Table

| Old Name | New Name (`aget_`-prefixed) |
|----------|---------------------------|
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

> **Note**: Fields `created`, `updated`, `migration_history`, and `component` are NOT prefixed — they are generic metadata, not AGET-specific identity fields.

### Detection

**Step 1 — Check scripts and skills for old-name reads:**

```bash
grep -rE '"(agent_name|domain|portfolio|managed_by|manages|instance_type|archetype|specialization|template|identity_file|intelligence_enabled|collaboration_enabled|capabilities|patterns|knowledge_inheritance)"' \
  .aget/ scripts/ .claude/ 2>/dev/null
```

Expected: 0 matches (or only matches in non-AGET code).

**Step 2 — Check if `.aget/version.json` itself has old-named keys:**

```bash
python3 -c "
import json
old = ['agent_name','domain','portfolio','managed_by','manages',
       'instance_type','archetype','specialization','template',
       'identity_file','intelligence_enabled','collaboration_enabled',
       'capabilities','patterns','knowledge_inheritance']
v = json.load(open('.aget/version.json'))
hits = [f for f in old if f in v]
print('PASS: no old fields' if not hits else 'FAIL: old fields present: ' + str(hits))
"
```

### Remediation

**If Step 1 finds matches** (scripts/skills reading old names):
Update each occurrence to use the `aget_`-prefixed name from the table above.

**If Step 2 finds old keys in `version.json`** (two-step process required):

1. **First**: Rename the keys in `.aget/version.json`. Example:
   ```bash
   # Manual approach — edit .aget/version.json and rename keys in-place
   # Or use jq:
   jq '{
     aget_agent_name: .agent_name,
     aget_domain: .domain,
     aget_portfolio: .portfolio,
     aget_version: .aget_version,
     created: .created,
     updated: .updated
   }' .aget/version.json > /tmp/version_new.json && mv /tmp/version_new.json .aget/version.json
   ```
   Adjust for the fields your agent actually uses.

2. **Then**: Commit that change, then upgrade `aget_version` to `"3.15.0"`.

> **Why two steps?** The field rename (step 1) is a v3.14 migration artifact. The version bump (step 2) is the v3.15 upgrade. Combining them loses traceability about which change was which.

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

Expected: 0 matches.

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
| Agent with no old field names and no --fix usage | ~5 min (version bump only) |
| Agent with old field names in scripts/skills only | ~20–30 min |
| Agent with old field names in version.json AND scripts | ~45–60 min (two-step BC-001 + upgrade) |

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
