# Corrections since tag — v{X.Y.Z}

**Contract** (SOP_release_process v1.57 Phase 3.6 Rule 2; gh#1882): this file is the ONE
write target per post-tag fix. Guidance surfaces (release body, RELEASE_HANDOFF,
REMOTE_MIGRATION_MESSAGE, SUPERVISOR_PROMPT) point here and never duplicate the enumeration.
Consumers pulling AT THE TAG: apply every row below on top of the tag payload.

**Tag**: v{X.Y.Z} (`{tag-SHA}`) · **Surface opened**: {YYYY-MM-DD} · **Rows are append-only.**

| # | SHA | Date | Artifact(s) | What | Why tag copy insufficient | Consumer action |
|---|-----|------|-------------|------|---------------------------|-----------------|
| 1 | `{sha}` | {date} | `{path}` | {one line} | {breakage if consumed at tag} | {pull from main / re-run step N / none-informational} |

---
*TEMPLATE_CORRECTIONS v1.0.0 (2026-07-18, v3.27 G2.3 / C-27-10). Machine-checkable shape: the v3.26 Post-Release Corrections table (`8eb0112`) is the ancestor.*
