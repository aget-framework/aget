# RELEASE HANDOFF: v3.11.1

**Version**: 3.11.1
**Released**: 2026-04-04
**Type**: PATCH (Script Rename Stabilization)

---

## Summary

v3.11.1 stabilizes two script renames and associated spec amendments. It also includes post-v3.11.0 fixes and new deployment tooling.

### Script Renames

| Old Name | New Name |
|----------|----------|
| `scripts/aget_housekeeping_protocol.py` | `scripts/health_check.py` |
| `scripts/study_up.py` | `scripts/study_topic.py` |
| Config: `skip_sanity` | Config: `skip_health_check` |

### New Tooling

- `scripts/tag_release.py`: Automated tag + release for all repos
- `scripts/verify_deployment.py`: Version-parameterized deployment verification

### Spec Amendments

- AGET_SESSION_SPEC: CAP-SESSION-008 updated for `health_check.py`
- AGET_RELEASE_SPEC: V-test references updated
- SOP_release_process.md: v1.33 → v1.37

---

## Migration

For each agent, rename local scripts and update references:

```bash
mv scripts/aget_housekeeping_protocol.py scripts/health_check.py 2>/dev/null
mv scripts/study_up.py scripts/study_topic.py 2>/dev/null
sed -i '' 's/aget_housekeeping_protocol/health_check/g' AGENTS.md
sed -i '' 's/study_up/study_topic/g' AGENTS.md
```

Update `.aget/config.json` if `skip_sanity` key exists → rename to `skip_health_check`.

---

## Deprecation Cycle Complete

All 3 items from v3.10.0 deprecation are now removed:
- `capture` verb → `record`
- `study-up` → `study-topic`
- `record-nugget` → `record-observation` Quick mode

---

## Context for External Fleets

If you manage a fleet of AGET agents that pulls from `aget-framework/` templates:

1. **Script renames are breaking**: Any automation referencing `aget_housekeeping_protocol.py` or `study_up.py` by name will fail after upgrading to v3.11.1.
2. **Config key renamed**: `skip_sanity` → `skip_health_check` in wind_down configuration. Check your `.aget/config.json` files.
3. **Spec references changed**: If your agents validate against SESSION_SPEC or RELEASE_SPEC, the expected script names have changed.
4. **New tooling available**: `tag_release.py` and `verify_deployment.py` are now in `scripts/`. Both are optional but recommended.

---

*RELEASE_HANDOFF_v3.11.1.md*
