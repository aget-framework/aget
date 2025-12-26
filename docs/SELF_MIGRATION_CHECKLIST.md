# Self-Migration Checklist for v2.12.0

**Purpose**: Migrate your agent to AGET v2.12.0 without framework-aget assistance.

**Time**: ~15 minutes per agent

---

## Prerequisites

- [ ] Agent has `.aget/version.json`
- [ ] Agent has `AGENTS.md` (or `CLAUDE.md` symlink to `AGENTS.md`)
- [ ] Git repository initialized

---

## Step 1: Download Validators

```bash
cd /path/to/your/agent

# Download from GitHub
curl -sO https://raw.githubusercontent.com/aget-framework/aget/main/validation/validate_version_consistency.py
curl -sO https://raw.githubusercontent.com/aget-framework/aget/main/validation/validate_naming_conventions.py
```

---

## Step 2: Run Pre-Migration Assessment

```bash
# Check current state
python3 validate_version_consistency.py .
python3 validate_naming_conventions.py .
```

**Expected**: Validators will report any issues to fix before migration.

---

## Step 3: Fix Any Violations

### Version Mismatch (L366)

If `version.json` and `AGENTS.md` versions differ:

1. Edit `AGENTS.md`: Update `@aget-version: 2.12.0`
2. Edit `.aget/version.json`: Update `"aget_version": "2.12.0"`

### Naming Violations

| Pattern | Convention | Fix |
|---------|------------|-----|
| L-docs | `L###_snake_case.md` | Rename file |
| SOPs | `SOP_*.md` or `*_GUIDE.md` or `*_CHECKLIST.md` | Rename file |
| Patterns | `PATTERN_*.md` | Rename file |
| Duplicate L-numbers | Unique per agent | Renumber |

---

## Step 4: Update Version

### Edit `.aget/version.json`

```json
{
  "aget_version": "2.12.0",
  "updated": "2025-12-26",
  "migration_history": [
    "... existing entries ...",
    "v2.12.0: 2025-12-26 (capability architecture)"
  ]
}
```

### Edit `AGENTS.md`

Find and update:
```markdown
@aget-version: 2.12.0
```

---

## Step 5: Optional - Add manifest.yaml

For capability composition benefits, add `manifest.yaml`:

```bash
# Copy from your base template
cp /path/to/aget-framework/template-advisor-aget/manifest.yaml ./manifest.yaml

# Edit to match your agent
vim manifest.yaml
```

Example manifest.yaml:
```yaml
apiVersion: aget.framework/v1
kind: TemplateManifest

metadata:
  name: your-agent-name
  version: 1.0.0
  agent_type: Advisor  # or Worker, Developer, etc.
  created: "2025-12-26"
  author: your-name
  status: active

composition:
  base_template: advisor  # or worker, developer, etc.
  capabilities:
    - name: memory-management
      version: ">=1.0.0"
    - name: domain-knowledge
      version: ">=1.0.0"
      config:
        domain: your-domain

validation:
  dag_validated: true
  conflicts_checked: true
  last_validated: "2025-12-26"
```

---

## Step 6: Validate

```bash
python3 validate_version_consistency.py .
python3 validate_naming_conventions.py .
```

**Expected**: Both validators pass (exit code 0).

---

## Step 7: Commit

```bash
git add .
git commit -m "chore: migrate to AGET v2.12.0

- Updated version.json to 2.12.0
- Updated AGENTS.md @aget-version tag
- Added manifest.yaml (optional)
- All validators pass

See: https://github.com/aget-framework/aget/releases/tag/v2.12.0"
```

---

## Troubleshooting

### "version.json not found"

Create minimal version.json:
```json
{
  "agent_name": "your-agent-name",
  "aget_version": "2.12.0",
  "instance_type": "aget",
  "created": "2025-12-26"
}
```

### "AGENTS.md not found"

Create minimal AGENTS.md:
```markdown
# Agent Configuration

@aget-version: 2.12.0

## Purpose
[Your agent's purpose]
```

### Validator errors persist

See [FLEET_MIGRATION_GUIDE.md](FLEET_MIGRATION_GUIDE.md) for detailed troubleshooting.

---

## Clean Up (Optional)

```bash
# Remove downloaded validators
rm validate_version_consistency.py validate_naming_conventions.py
```

Or keep them for future self-validation.

---

## Success Criteria

- [ ] `validate_version_consistency.py` passes
- [ ] `validate_naming_conventions.py` passes
- [ ] `.aget/version.json` shows `"aget_version": "2.12.0"`
- [ ] `AGENTS.md` shows `@aget-version: 2.12.0`
- [ ] Changes committed

---

*Self-Migration Checklist v1.0 - AGET Framework v2.12.0*
