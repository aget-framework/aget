# Corrections since tag — v3.34.0

**Contract**: this is the single correction record for post-tag fixes, following
the convention in `CORRECTIONS_v3.33.1.md`. Rows are append-only. Historical tag
bytes and verdicts remain unchanged; corrections describe a distinct subject.

**Tag**: `v3.34.0` (`43b35a3769c52ae8b8b2bdee087698659c62ecc1`).
**Opened**: 2026-09-16. The repair below is committed locally; this record does
not assert remote publication or receiver installation/acceptance.

| # | SHA / subject | Date | Artifact(s) | Correction | Why tag copy is insufficient | Consumer action |
|---|---|---|---|---|---|---|
| 1 — W1 | Published tag `43b35a3769c52ae8b8b2bdee087698659c62ecc1` | 2026-09-16 | `handoffs/V334_PAYLOAD_MANIFEST.json`, entry `tests/test_host_layout_conformance.py` | The manifest declares `b7f2382c24d8584d610e12df4a31e940ca452f34289d8f54a8278cdbaa419e8e`; the file at the tag hashes to `b95392f34877a361ae26e70d263f4eff05b3b92bfb3dcdae26ff6bc317d3c46e`. | Exactly one of the 50 declared digests disagrees with the tag tree. A direct digest comparison rejects the correct tag file; an override can additionally misclassify it. | Preserve the original manifest as provenance. Use the tag-tree digest above for this entry in an explicitly corrected manifest. Do not change the published tag or interpret a metadata correction as receiver acceptance. |
| 2 — W3 | Repair `07d2090f90e8e174784a38af0aa0ee49462d06ae` | 2026-09-16 | `scripts/study_topic.py`, `verification/validate_archetype_skills.py`, `handoffs/FLEET_MIGRATION_CONTRACT_v3.30.0.json` | Add postponed annotation evaluation to both Python files. Update the contract's current resolver digest through its existing amendment mechanism; retain its historical digest. | Runtime evaluation of `Path \| None` raises `TypeError` on Python 3.9 at import. Parsing alone does not detect it. | Obtain the named repair through an authorized delivery route. Re-derive the composition's three changed file digests, retain the W1 correction, and verify on the receiver's actual interpreter and test suite before declaring migration complete. Include this annotation repair when composing any separately repaired resolver; its exact resulting digest must be measured afresh. |

## Exact repaired bytes

SHA-256 values below are read from Git objects at `07d2090f90e8e174784a38af0aa0ee49462d06ae`:

| Path | SHA-256 |
|---|---|
| `scripts/study_topic.py` | `671ce3ab4b8dce578b6b8ea80c61239eb8bf418a5482adcfd8adba2ca8434d21` |
| `verification/validate_archetype_skills.py` | `5c63ffac2b3b55b031b7d4ae686f865184673753d1df8363a58f5d651b1585d0` |
| `handoffs/FLEET_MIGRATION_CONTRACT_v3.30.0.json` | `8d4cab207da43d07713d093dce44d4d5519a202a60273a95e581aa01aec7c2ee` |

The unchanged tag manifest therefore disagrees with four paths at the repair:
the three changed files above and the original W1 entry. That expected difference
requires a corrected composition manifest; it is not permission to ignore integrity failures.
Retain mode encoding compatibility when composing: `0o644` / `0o755` are permission
notations; `100644` / `100755` are the corresponding regular-file Git modes.

## Validation and limits

Independent clean Git exports, using actual Python 3.9.6 and one fresh process per
manifest Python path, reproduced **7 import failures out of 43 at the tag** and
**0 out of 43 at the repair**. Five failures were downstream imports of the two
defective modules. The export contains the full committed repository to provide
dependencies; this does not establish that the 50-entry payload is dependency-complete.
The interpreter's installed dependencies remain part of the test environment.

Import success is not whole-suite success, behavioral preservation, or a support-policy
change. `specs/AGET_CI_SPEC.md` records the dated v1.1.0 decision to move its matrix to
3.10–3.13; this repair does not reverse that decision. `codemeta.json` still says
Python 3.9+; that policy/metadata discrepancy remains open. No Python 3.8 execution
was performed here. Separately, `audit_instrument_verdict_contract.py` uses
`ast.unparse`, which is unavailable on 3.8 when that code path executes.

Receiver-specific behavior, local extensions, prerequisites, protected-path handling,
rollback, committed installation and receiver-owned acceptance remain migration obligations.
These two correction rows do not clear other preflight failures.
