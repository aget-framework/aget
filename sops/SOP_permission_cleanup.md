# SOP: Permission Cleanup

**Version**: 2.0.0
**Status**: Active
**Created**: 2026-01-10 (framework-instance v1.0.1) · **Promoted to canonical**: 2026-07-05
**Author**: Framework Manager
**Companion script**: `scripts/permission_cleanup.py` (dry-run first; field-proven)
**Related**: permission-governance + detection-gap lessons are recorded in the
operating agent's own `.aget/evolution/` — this canonical copy deliberately carries no
L-doc IDs, which are unique per agent and do not resolve across seats.

---

## Purpose

Remediate accumulated CLI permissions in `.claude/settings.local.json` when `health_check.py` reports the permission-accumulation row at WARN or CRITICAL. This SOP is the target of the health check's remediation pointer (v3.25.0+).

## Thresholds

| Metric | OK | WARN | CRITICAL |
|--------|-----|------|----------|
| Count | 0–100 | 101–200 | >200 |
| Size | 0–30KB | 31–50KB | >50KB |

**Calibration note (open question, field-raised 2026-07-05)**: the count line is flat across archetypes, but a fleet supervisor legitimately holds more tool classes than a single-domain worker. Do NOT prune legitimate broad grants merely to satisfy the count metric (Goodhart) — landing slightly over the line with a documented rationale is the honest outcome. The size line has discriminated unambiguously in the field (4.1KB vs 50KB). Threshold redesign (archetype-scaled or size-weighted) is tracked for grooming.

## Procedure

### 1. Dry-run first

```bash
python3 scripts/permission_cleanup.py --dry-run
```

Review the sample removals — they should all be junk classes (§3). If anything looks load-bearing, stop and review manually.

### 2. Execute (backs up automatically)

```bash
python3 scripts/permission_cleanup.py
```

Writes a dated backup (`settings.local.json.bak.YYYYMMDD`) before modifying, then prints before/after metrics.

### 3. What is kept vs removed

**Keep** (high value, reusable):
- Broad patterns ending with `:*)` (e.g., `Bash(git commit:*)`) that carry no user-specific absolute path
- All `WebFetch(domain:...)` entries
- `WebSearch`

**Remove** (low value, bloat):
- Heredoc patterns (git commits with `<<'EOF'`)
- Specific file paths (`/Users/...`, `/tmp/...`)
- Shell fragments (`Bash(do)`, `Bash(fi)`, etc.)
- One-off commands with inline scripts

**Healthy-friction guard (CAP-FRIC-006 alignment)**: pruned entries re-prompt at next use — that prompt is a healthy authority-boundary control, NOT a regression. Never prune deny/ask rules, and never treat the re-prompt tail as a defect to be remediated by re-broadening.

### 4. Verify

```bash
python3 scripts/health_check.py     # permission row: OK or WARN (not CRITICAL)
python3 scripts/wake_up.py          # smoke: session tooling still works
git status                          # smoke: git grants intact
```

### 5. Document (if reduction >50%)

Note before/after counts + sizes in your session record.

## Rollback

```bash
cp .claude/settings.local.json.bak.YYYYMMDD .claude/settings.local.json
```

## Prevention

- Prefer broad patterns (`Bash(git:*)`) over specific commands when approving
- Avoid approving heredoc patterns (use `Bash(git commit:*)`; multi-line commit messages via `-F <file>`)
- Run the health check periodically; quarterly cleanup recommended

## Field record

| Instance | Before | After | Δ | Date |
|----------|--------|-------|---|------|
| Framework Manager | 434 / — | 91 / — | −79% | 2026-03 (SOP origin) |
| Fleet Supervisor | 649 / 54.2KB | 104 / 4.1KB | −84% / −92% | 2026-07-05 (recipe applied verbatim; CRITICAL cleared; zero healthy-friction controls touched) |

## Reference

- Permission-governance and detection-gap lessons live in each agent's own
  `.aget/evolution/`. L-doc IDs are agent-scoped and are intentionally not cited here:
  a bare `LNNN` resolves to different lessons in different agents.
