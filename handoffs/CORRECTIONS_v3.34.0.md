# Corrections since tag — v3.34.0

**Contract**: this is the single correction record for post-tag fixes, following
the convention in `CORRECTIONS_v3.33.1.md`. Rows are append-only. Historical tag
bytes and verdicts remain unchanged; corrections describe a distinct subject.

**Tag**: `v3.34.0` (`43b35a3769c52ae8b8b2bdee087698659c62ecc1`).
**Opened**: 2026-09-16; rows 3–5 appended 2026-09-19. Published with this PR; this record still
asserts no receiver installation or acceptance. `DELIVERED_FILES_v3.34.0.yaml` is absent (third release running); use the payload manifest with the W1 correction as the integrity reference.

| # | SHA / subject | Date | Artifact(s) | Correction | Why tag copy is insufficient | Consumer action |
|---|---|---|---|---|---|---|
| 1 — W1 | Published tag `43b35a3769c52ae8b8b2bdee087698659c62ecc1`; **corrected manifest issued 2026-09-20: `handoffs/V334_PAYLOAD_MANIFEST_corrected.json`, sha256 `a50f927303b7b0692e5d8e97da4510f8aa3ed75c2d0ccf4a4cbb922ebd2a77b1`, bound to `5cfc055a` (4 substitutions: this entry + the three W3 files)** | 2026-09-16 | `handoffs/V334_PAYLOAD_MANIFEST.json`, entry `tests/test_host_layout_conformance.py` | The manifest declares `b7f2382c24d8584d610e12df4a31e940ca452f34289d8f54a8278cdbaa419e8e`; the file at the tag hashes to `b95392f34877a361ae26e70d263f4eff05b3b92bfb3dcdae26ff6bc317d3c46e`. | Exactly one of the 50 declared digests disagrees with the tag tree. A direct digest comparison rejects the correct tag file; an override can additionally misclassify it. | Preserve the original manifest as provenance. Use the tag-tree digest above for this entry in an explicitly corrected manifest. Do not change the published tag or interpret a metadata correction as receiver acceptance. |
| 2 — W3 | Repair `07d2090f90e8e174784a38af0aa0ee49462d06ae` | 2026-09-16 | `scripts/study_topic.py`, `verification/validate_archetype_skills.py`, `handoffs/FLEET_MIGRATION_CONTRACT_v3.30.0.json` | Add postponed annotation evaluation to both Python files. Update the contract's current resolver digest through its existing amendment mechanism; retain its historical digest. | Runtime evaluation of `Path \| None` raises `TypeError` on Python 3.9 at import. Parsing alone does not detect it. | Obtain the named repair through an authorized delivery route. Re-derive the composition's three changed file digests, retain the W1 correction, and verify on the receiver's actual interpreter and test suite before declaring migration complete. Include this annotation repair when composing any separately repaired resolver; its exact resulting digest must be measured afresh. |
| 3 — W3b | Repair *(this PR)* | 2026-09-19 | `scripts/check_claim_freshness.py`, `scripts/validate_spec_binding.py` | Same defect class as W3, two further sites **outside the 50-entry manifest** but inside the 90 delivered `scripts/`: one `X \| None` each, no future import. Found by node-1 (`private-aof1-aof-supervisor-AGET`, macOS system Python 3.9.6); reproduced by the producer under `/usr/bin/python3` 3.9.6 on all 90 delivered scripts (4 failures before, 0 after). Both had failed at v3.33.1 too. | W3's 43-path probe was scoped to manifest Python paths; these two are delivered but unmanifested, so a receiver installing `scripts/` wholesale still hits them. | Apply with W3. Guard: `tests/test_payload_imports_on_py39.py` imports every delivered script under the oldest registered interpreter and reports UNAVAILABLE where none < 3.10 exists. The floor discrepancy (`codemeta.json` 3.9+ vs `specs/AGET_CI_SPEC.md` matrix 3.10–3.13) is recorded above and is v3.35 input, not resolved here. |
| 4 | Repair *(this PR)*, DELTA staged at the framework seat | 2026-09-19 | `.claude/skills/aget-propose-goals/SKILL.md`, `.aget/specs/skills/SKILL-055_aget-propose-goals.yaml`, `rubrics/RUBRIC_goal_selection_v1.0.md`, `specs/AGET_GOAL_SPEC.md`, `drafts/AGET_GOAL_SPEC.md` | Five files cite a *sibling* `SOP_near_term_ambition_projection` that exists at no tag or seat; L1090 folded it into the propose-goals skill. | A receiver following the citation finds nothing and files a missing-instrument finding (node-1 did, 2026-09-19). | **Nothing is missing.** Read the citation as "retired into `/aget-propose-goals`". Wording repair rides the next window via the spec route; not changed in this PR. |
| 5 | Repair `60a1e20` (cherry-picked in this PR) | 2026-09-19 | `scripts/close_authorization_guard.py`, `tests/test_close_authorization_guard.py`, `tests/test_principal_attribution_pattern.py` | The principal-attribution pattern had no branch for "GO", the fleet's most common authorization word; the tag copy also lacks the 2026-08-28 gerund/`-ise` repair. A close recorded as "performed under principal GO" classified as *agent-autonomous* and PASSED on the wrong ground (node-1, 2026-09-19; reproduced on the tag copy). | A receiver running the tag guard cannot classify a principal-authorized close, so CHECK-A never fires on it. | Take the repaired guard and its tests from this PR, or treat the guard's *agent-autonomous* verdict as unreliable for any close whose text says GO. |
| 6 — W3c | Repair *(this PR)* | 2026-09-20 | `tests/test_skill_route_contract.py`, `scripts/check_capability_retention.py`, `tests/test_payload_imports_on_py39.py` | Two more 3.9 sites, both outside the import guard's first scope: a `dict \| None` in a test method signature (collection of `tests/` aborts on 3.9, so the handoff's own §Smoke Test cannot run as specified), and `ast.match_case` (3.10-only AST node) referenced at runtime by a delivered script. Found by node-1 running the candidate's suite on 3.9.6; reproduced here (1 collection error, then 8 failed / 1003 passed, one of them this). | The guard shipped in row 3 imported delivered `scripts/` only; a receiver that runs the release's smoke test hits the collection abort first and never reaches the results. | Apply with W3/W3b. The guard now imports `tests/` modules too. The `match_case` guard keeps behaviour on 3.10+ unchanged. Remaining 3.9 failures in the suite (7) are canonical-mount environment tests, not interpreter defects; node-1 sees the same set. |

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
