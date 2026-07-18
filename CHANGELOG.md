# Changelog

All notable changes to the AGET Framework will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

**Note**: This CHANGELOG reflects the public aget-framework/aget repository. For complete version history including release gaps and template-specific changes, see [VERSION_HISTORY.md](docs/VERSION_HISTORY.md).

---

## [3.27.0] - 2026-07-18 - "Finish & Verify"

### Changed
- Theme: the portfolio learns to FINISH (EC tick-state maintained signal CIS-010; CIS-008 Achieve-only re-spec; NASCENT typing backfill; L-doc ID injectivity remediation L1200-L1209 + tombstone registry) and the release learns to VERIFY what it shipped runs (migration Rung-4 behavioral verification + mandatory Behavioral Smoke; 3-axis tag-payload coherence [14 origins x tagged-tree paths x executed-surface]; single Corrections-since-tag surface; DoD ID-axis row-completeness ratchet; public-graph coherence joins computed DoD; verify-before-claim coverage matrix). Also: Transactional Execution doctrine + workspace convention in all template AGENTS.md; universal-skill conformance 14/14 (core + document-processor backfilled); single-slash permission-rule detector; dual-status mask scanner; wind-down double-fire guard; delegated-prompt date contract; Filing_Candidate L-doc marker standard.

## [Unreleased]

Items confirmed in-flight for a future release (latest released: **3.26.0**). Per Keep a Changelog 1.1.0 forward-work convention.

- Issue-governance spec delta for the `/aget-file-issue` pre-filing probes (skill layer shipped in 3.26.0; formal requirement rides the next spec pass).
- Template `/aget-file-issue` structural refresh (routing + probe steps to all templates; fleet routing propagation staged per the 3.26.0 rollout decision).

## [3.26.0] - 2026-07-11

**Theme**: Signals & Contracts

> The release hears its consumers — a wake-up currency signal, extension hooks at the halt points downstream agents actually hit, supervisor-relay issue routing — and hardens its contracts: three-state check reporting, terminal-state vocabulary, a search contract for KB research, a verify-before-claim coverage matrix, and the first exercised deprecation under the new N-2 policy.

### Added

- **Release-currency signal in `wake_up.py`** — session start reports when the local framework version is behind the latest release (`Framework: vX local · vY latest — verify DEPLOYMENT_SPEC before upgrading`); silent when current or unknown (fail-soft, config-gated). Uses `gh api` (the `gh release view` form hangs indefinitely under non-tty subprocess — documented for adopters of the earlier reference implementation).
- **Extension hooks for `health_check.py` + `study_topic.py`** (`health_check_ext.py:post_health`, `study_topic_ext.py:post_study`) — instance customization without forking Framework_Artifacts; the fork-pressure halt observed downstream is the motivating case.
- **Three-state check contract** (`docs/CONVENTION_check_three_state_contract.md`) — every check reports PASS / FAIL / **UNREACHABLE** distinctly; a missing dependency is not a conformance failure, and "nothing found" on an unsearched surface is not a pass. Exemplar wired into `check_skill_reliance_manifest.py`.
- **Terminal-state vocabulary** (`docs/CONVENTION_terminal_state_vocabulary.md`) — IMPLEMENTED-AWAITING-DEPLOYMENT-EVIDENCE / PILOTED / STAGED as honest plan states with advancement pointers; "artifact created" no longer masquerades as "running".
- **Verify-before-claim coverage matrix** (`docs/CONVENTION_verify_before_claim_coverage_matrix.md`) — verify-before-claim as claim-channels × enforcement-gates, with placements: `/aget-file-issue` **Step 3.5** pre-filing dedup + target-existence probes; `/aget-close-project` **Step 5.5 / C-CLOSE-008** has-it-run gate (executable-mechanism deliverables need execution evidence pre-COMPLETE); conversational channel registered as AGET_SESSION_SPEC CAP-SESSION-015; lesson-propagation channel via `/aget-record-lesson` Step 4.5.
- **`/aget-close-project` C-CLOSE-007** — the closer mutates the scaffolded checklist in place; parallel prose sign-offs beside unticked scaffolds are prohibited (dual-representation defect class).
- **`/aget-file-issue` supervisor-intake routing** (Step 2.5) — managed agents default to a supervisor-relay intake artifact; supervisors and principal-supervised sessions file direct.
- **`/aget-record-lesson` Step 4.5 propagation check** — multi-seat or framework-relevant lessons route to lesson-first filing (CAP-ISSUE-011) with a cross-namespace join label, ending three-private-captures-of-one-lesson scatter.
- **Tag-payload coherence gate** (`scripts/check_tag_payload_coherence.py` + SOP Phase 3.6) — post-tag repairs can no longer leave the tag silently divergent from the shipped payload.
- **Permission-quality check** (`scripts/check_permission_quality.py`) — classifies grants BARE / UNIVERSAL / SCOPED; a write-capable unscoped grant WARNs even when the permission count is green.
- **Deprecation policy N-2 adopted** (R-DEP-020..023) with the registry's **first exercised rehearsal**: `check_pretag_inventory.sh` deprecated in favor of the `--pre-tag` successor, all five R-DEP-010 fields, runtime warning live, removal v3.28.
- **Interaction-channel pattern (first rung)** (`docs/patterns/PATTERN_interaction_channel.md`) — engine-agnostic rendered-review channel substrate; promotion is pilot-gated (non-author validation before template rollout).
- **AGET_SESSION_SPEC 1.3.0** — CAP-SESSION-015 pre-assertion gate (verify-before-claim, conversational channel); CAP-SESSION-007-08..12 study-topic search contract; CAP-SESSION-008-06 extension hook. **AGET_ISSUE_GOVERNANCE_SPEC 2.3.0** — seat-conditional routing default.
- **Fleet-migration Wave-0 entry criterion** (SOP_fleet_migration) + RELEASE_HANDOFF template **Migration Target** block — a migration dispatch names its target version explicitly or gets a discovery answer; never an inferred N-1.

### Fixed

- **`study_topic.py` search contract** (7 audited defects): surface manifest with exclusion provenance in output, keyword hygiene (stopwords no longer count as keywords), token-boundary matching, log-damped ranking with filename-match boost, relevance floor with `--no-floor` escape, contract-derived recommendation text, and `inbox/` joining the searched surfaces (14-day window).
- **v3.25-payload defects**: `wake_up.py` pending-work glob was case-sensitive (newest session notes invisible); `check_skill_reliance_manifest.py` archetype-index candidate paths never resolved on deployed agents; `close_gate_check.py` independence-WARN half restored (dropped by the prior release's sync).
- **Release-history hygiene**: v3.21 DEPLOYMENT_SPEC private-name leak scrubbed; canonical DoD row-completeness for R-REL-038.

### Changed

- `release_cycle_rollup.py` renders compound lock-states correctly (`LOCKED` rather than `?`).

## [3.25.0] - 2026-07-04

**Theme**: Grounded Entities & Trusted Releases (balanced double-bill: capability + release-integrity)

### Added
- **AGET_ENTITY_DIMENSION_SPEC v0.1.0** (canonical) — first spec normatively binding vocabulary by `aget:concept/` URI; 7 entity-characterization dimensions; + `scripts/validate_entity_dimension.py` (V-ENTDIM-001..016 conformance validator, Advisory→Strict).
- **AGET_FRICTION_SPEC v1.0.0 Active** — promoted from draft after non-author forward-validation (H-FPC-001b); capture surfaces now stamp a triage value-class (`owed` fail-safe default, CAP-FRIC-006).
- **aget-ask production v1.0.0** (SKILL-045) — entropy-reducing clarification/followup skill with altitude filter; shipped to all 13 templates.
- **Release-integrity mechanization**: computed Definition-of-Done wired into the close path (`release_close_guard.py` composes SOP-deliverable enumeration + binary DoD; close BLOCKS on RED); `close_gate_check.py` gains closure-substance detection; `health_check.py` gains reliance-manifest self-attestation (R-BND-001-03) + permission-accumulation gates; `wake_up.py` self-attests reliance conformance.

### Fixed
- `study_topic.py`: live plans no longer render `[inactive]` (case-insensitive, Plan_Status-first detection); knowledge/ + ontology/ join the search surface.
- Release SOP: migration guide + deep release notes now required in the tagged tree (reachability-at-tag), received-state V-test rule, headless enforce-on-contradiction.

### Changed
- Template conformance model: **reliance-only** — templates carry an `@aget-canonical-specs` reference line and run the version's features; no spec copies shipped.

---

## [3.24.0] - 2026-06-27

**Theme**: Reliance & Boundaries

> What can a principal *rely on* an AGET to provide at a release — and *where* do an always-on node's artifacts live? v3.24 makes both checkable. The theme is advanced, not completed: friction-handling triage is staged to a following release.

### Added

- **R-BND-001 — Boundary & Reliance Requirements** (`specs/requirements/`). A cross-boundary reliance (framework→downstream, supervisor→agent, agent→agent) SHALL be a **principal-owned, externally-verifiable requirement with a single source of truth** — version-pinned, verified *meets-declared-minimum* (not parity-to-template), with drift detectable.
- **Skill-reliance manifest framework feature.** A release-pinned `{S}` core / `{O}` optional / `{D}` domain reliance contract any AGET can declare and **self-check**: a governed manifest schema (`schemas/skill_reliance_manifest.schema.yaml`) + a generic validator (`scripts/check_skill_reliance_manifest.py`). Resolves the gap where skill tiers were unspecified and uncheckable.
- **AGET_HOST_RUNTIME_SPEC v1.0.0** (`specs/`) — host-runtime **filesystem-layout standard** for always-on nodes: lifecycle-class separation (config/data/state/cache/logs), a record/exhaust tier boundary, bounded-growth rotation, and deployed-copy decoupling. Behavioral conformance checks activate at first node deployment (honest-testability, ADR-007).

### Notes

- Theme framed honestly as **advanced, not fulfilled** — the reliance and boundary *contracts* land; friction-handling triage and host-node deployment continue in following cycles.

---

## [3.23.1] - 2026-06-20

**Theme**: Goal Tier (canonical) + Close-Authorization Guard

> The fast-follow the 3.23.0 preview promised: the Goal Tier lands in canonical, and the close-authorization guard (built but explicitly *not* shipped in 3.23.0) is now in `aget/` with template propagation.

### Added
- **Goal Tier — canonical**: `AGET_GOAL_SPEC` v0.2.0 promoted to `specs/`. Defines the Goal artifact (a durable cross-session **outcome**: North Star → Goal → Initiative → Action), KAOS goal typing (Achieve / Maintain / Soft), and the ≥1-loop requirement (a Goal owns a regulating loop, or it decays as an orphan).
- **`aget-create-goal`** + **`aget-propose-goals`**: the propose→commit verb pair, now with the spec canonical. Committed Goals are a two-tier store (committed vs aspirational).
- **`aget-close-project`** + **`close_authorization_guard.py`**: the close-time authorization guard (the 3.23.0-deferred capability), wired into close as Step 2.5 — blocks a project close that claims authorization without a linked event.

### Changed
- Version 3.23.0 → 3.23.1 across `aget/` + 13 templates; the three new skills synced to all templates dependency-aware (with their engine scripts).

### Notes
- The full Goal-Value scoring rubric is deferred to a future release; this cycle minimally grounds the value dimension.

---

## [3.23.0] - 2026-06-20

**Theme**: Goal Tier (preview)

### Added
- **Goal Tier (preview)**: `aget-create-goal` skill + `AGET_GOAL_SPEC` v0.2.0 (draft) — commit a selected candidate goal into a governed Goal artifact (North Star → Goal → Initiative). Canonical spec promotion follows in 3.23.1.
- `aget-propose-goals` skill (SKILL-055): plural candidate-goal generator scored ex-ante by `RUBRIC_goal_selection`.

### Notes
- Reduced scope (REQ-9 time-protection): the self-oversight ratchet generalization and the interaction-channel rung deferred to 3.24.
- Goal-Tier canonical promotion (ontology grounding) deferred to the 3.23.1 fast-follow.
- A close-time authorization guard was built and exercised in the framework-manager instance this cycle; it is **not** part of this public release — it lands in canonical (with a pilot) in 3.23.1. (The earlier "Integrity Hardening" theme + a guard bullet were corrected post-release: those referenced a capability not present in canonical `aget/`. The two internal release-tooling fixes (#1654/#1656) likewise live in the manager instance, not canonical, and were removed from this public entry.)

---

## [3.22.0] - 2026-06-13

**Theme**: Skill-Support Delivery + Verify-at-Point-of-Use + Hygiene

> **No breaking changes.** Minor — additive governed tooling. First deliberately-ambitious minor cycle (instrumented capacity experiment, H-AMB-322): scope locked over the conservative `RUBRIC_minor_release_scope` band by design, with per-item actuals fed back to recalibrate the rubric. Two organizing principles ship as runnable gates: **propagation SHALL carry a paired point-of-use verify** (the freshness/coherence gates *are* the verify half) and **distribute ≠ homogenize** (the deployer is per-skill surgical, not a blanket overwrite).

### Added
- **`scripts/deploy_skill.py`** — governed surgical skill deployer: per-skill filter, companion artifacts, dry-run default, audit log (`workspace/skill_deploy_audit.jsonl`), independent post-deploy verify, **push-window guard encoded in `--apply`** (refuses Mon–Fri per the public push-window discipline), and **live gap re-derivation** (computes the real skill gap rather than trusting a stale table). On its first live run it corrected a 3.4×-stale gap headline — dogfooding the verify-at-point-of-use theme.
- **`scripts/check_claim_freshness.py`** — citation/claim freshness gate: parses governed artifacts for `#NNNN STATE` issue-citations, `--online` re-derives each via `gh`, `--strict` exits 1 for CI/release-gate.
- **`scripts/check_skill_coherence.py`** — release-time skill-frontmatter↔tree coherence gate: detects declared-but-absent Governing-Spec/SOP and stale-"future" framing of shipped artifacts.
- **`scripts/validate_spec_binding.py`** (+ `scripts/ground_artifact.py` loader dependency) — ONTOLOGY-SPEC-BINDING validator-half.
- **+20 V-tests** across the new scripts (all passing in canonical).

### Changed
- **`/aget-propose-actions` → v1.8.0**: Step 3.5 Self-Critique (10-point checklist from L025 obs093–105) + REQ-PA-018/019/020 (named-person leverage and ≥1-non-artifact-action at ≥1-day budgets) + a **Type** column making action-type bias visible. Propagated to all 13 templates (v1.6.0 → v1.8.0, also clearing accumulated v1.7.x propagation lag).
- **`scripts/validate_ontology_reciprocity.py`** — scope fix: dangling→whole-vocab, cross-cluster→non-defect (excluded from TOTAL DEFECTS).

### Notes
- The 5 pre-existing test failures (contract-test reference-rate + config tier-detection + skill-count map) are carried debt, disclosed not hidden — not introduced by this release.

---

## [3.21.0] - 2026-06-06

**Theme**: Always-On Fleet Operations (governance-scoped)

> **No breaking changes.** Minor — governance scaffolding for unattended/always-on operation. This release ships the **artifacts**; the operational runtime (24×7 host, cross-machine dispatch, fleet-cohort) is deferred to v3.22. This is a net governance-inflow release landing alongside an open fleet-wide inflow-governance gap; the first concrete *outflow* primitive (MEMORY.md compaction) landed in the same cycle.

### Added
- **Unattended-autonomy specification** (`aget/specs/AGET_UNATTENDED_AUTONOMY_SPEC.md` v1.0.0): 8 EARS requirements (CAP-UNATTEND-001..008) bounding what an agent MAY do unattended (scheduled/headless/always-on) vs MUST escalate — autonomy envelope (declared in `.aget/config.json`), fail-safe escalation default, dispatch trust-channel, bounded self-modification, audit-record, advisory multi-tenant share. Composes existing cross-fleet, push-window, self-modification, and trust-channel disciplines. All behavioral V-tests runtime-pending (governs a runtime not yet built — no test-theater).
- **`check_initiatives.py`** — read-only portfolio rollup across `planning/initiatives/INIT-*.md` (inventory by status, 0-COMPLETE anomaly, past-target Loading-Dock, staleness, cohort clusters); 10 V-tests.
- **`/aget-create-initiative`** deployed to canonical core (STRICT, D71). **⚠️ Errata (2026-06-07, gh#1461):** this does **not** close the verb-pair gap as originally stated — the producer half (`/aget-propose-initiative` skill) and `SOP_initiative.md` are **not** shipped in canonical at this tag, so the STRICT route is **non-functional** (it refuses without an APPROVED `PROPOSAL_init_*.md` and `cat`s an absent SOP). The route is **gated (not enforced)** until the producer half ships. See gh#1461.

### Changed
- **IAC SOP** (`SOP_cross_aget_communication.md`) per-pattern maturity reconciliation (P1 Relay + P1.5 Read-at-Source → Implemented; cross-machine patterns honestly Pending).
- **Release observability** (C-21-16): release-metrics ledger now live-captures real build-gate data; `deployment_monitor.py` outcome-record crash fixed (gh#1589).

---

## [3.20.3] - 2026-05-31

**Theme**: C-P3 Correctness Fix

> **No breaking changes.** Patch — corrects a verifier defect shipped in v3.20.2, before fleet rollout (fix-once-not-N).

### Fixed

- **C-P3 silent-skip → false-clean (gmelli/aget-aget#1553)** — `check_structural_skill_frontmatter` skipped any D71-STRUCTURAL skill whose `SKILL.md` was absent (`if not sk.is_file(): continue`) and then reported "clean," conflating *present-and-clean* with *absent, couldn't check*. It now emits a **warning** listing absent structural skills (`"N/4 present + clean; ABSENT: …"`) — a mandated-but-missing skill is surfaced, not hidden (an absent D71-STRUCTURAL skill is arguably the worse violation: the agent cannot model-invoke it). Propagated to all 13 templates. Surfaced during the v3.20.2 supervisor pilot; the C-P3 defect would have false-passed a run-and-check-clean rollout pilot, so it was fixed in canonical before any fleet dispatch.

---

## [3.20.2] - 2026-05-31

**Theme**: **Consumer-Surface Delivery**. v3.20.0 advertised three consumer-facing capabilities (C-F1/C-P1/C-P3) that were implemented and changelogged but **never reached the 13 template repositories consumers pull** (verified 0/13). v3.20.2 delivers them to the consumer surface — closing the author-surface/consumer-surface gap that let an advertised capability pass release green while absent from what consumers actually pull.

> **No breaking changes.** Existing instances upgrade by version-bump only.

### Added (delivered to consumer surface)

- **C-F1 / C-P1 / C-P3 now present in all 13 templates** (verified 13/13 by the consumer's own check) — previously author-surface-only:
  - **C-F1** `/aget-propose-actions` presentation (Evidence column · ▶ Recommendation · ⚠ Decisions) — synced into 12 templates; **created** in `template-document-processor-AGET` (which lacked the skill).
  - **C-P1** `close_gate_check.py` close-gate conformance guard — added to all 13.
  - **C-P3** `check_structural_skill_frontmatter` — added **additively** to each template's `health_check.py` (local checks preserved; not a wholesale replace).

### Fixed

- **Consumer-surface propagation gap (gmelli/aget-aget#1551)** — v3.20.0's "Functional Capability" theme reached the author surface but not the templates; v3.20.2 completes the delivery (0/13 → 13/13).

### Deferred (NOT shipped in v3.20.2 — tracked for fast-follow)

- **Blocking consumer-reachability release gate** (Tier 2) — the structural gate that resolves every advertised capability to the consumer surface at release time. **Priority fast-follow**; not built here (would be rushed).
- **Canonical skill source-of-truth + skill divergence gating** (Tier 3) — pending a canonical-home decision.
- **`template-document-processor-AGET` CI** — the template lacks `ci.yml` and standard v3.0 structure; adding CI would expose a pre-existing red. Structural completion deferred.

### Notes

- **v3.20.1** was tagged in canonical (tag-vs-HEAD reachability fix, gmelli/aget-aget#1549) but never released to the consumer surface; v3.20.2 is that consumer-surface completion. The 3 capabilities are verified present 13/13 by direct re-derivation, not by proxy.

---

## [3.20.0] - 2026-05-30

**Theme**: **Debt Paydown + Structural-Guard Deployment + Functional Capability**. The cycle spends an accumulated reliability dividend on three fronts: retiring carry-forward debt (the long-standing citation-resolution 404s and a spec-scoring fault), deploying structural guards that make release-and-close discipline enforced rather than advisory, and adding direct user-facing value on the highest-frequency session surface. The functional floor was raised mid-cycle so the release ships at least one high-reach capability improvement, not only internal hardening.

> **No breaking changes** in v3.20. Existing instances upgrade by version-bump only.

### Added

- **`/aget-propose-actions` presentation enhancement (C-F1)** — the fleet's highest-frequency session command now surfaces, per proposed action, an **Evidence column** (the grounding citation, previously dropped from the table), a **▶ Recommendation line** (the agent's single lead pick + why), and a **⚠ Decisions-needed callout** that lifts judgment-call items out of the autonomous rows. Principals see a recommendation, not just a menu.
- **Close-gate conformance guard (C-P1)** — a close-gate conformance check (`close_gate_check.py`) mechanically blocks marking a PROJECT_PLAN COMPLETE while V-test gates remain unchecked (replaces manual eyeballing of the prose gate). Wired into the close-project flow.
- **Structural-skill frontmatter guard (C-P3)** — `health_check.py` gains `check_structural_skill_frontmatter` (ref gmelli/aget-aget#1489): detects D71 structural skills carrying `disable-model-invocation: true` (which would leave the agent unable to model-invoke them) and flags them as errors. *(Corrected 2026-05-30: the prior entry described "health/wind-down signal-class severity," which did not match the shipped artifact — the v3.20 `health_check.py` change is the #1489 frontmatter guard, and `wind_down.py` was unchanged. Release-accuracy fix per gmelli/aget-aget#1549.)*
- **"Verify with the consumer's own check" rule (C-P4)** — codified in the release SOP: cross-repo/CI claims are verified by the consumer's actual check (e.g. the real GitHub CI run), not by a local proxy.

### Fixed

- **Duplicate `CAP-REL-035` declaration in `AGET_RELEASE_SPEC` (C-S1)** — the capability was declared twice, tripping the declaration-uniqueness gate and scoring the entire 224-requirement spec as NONE. Merged into the single mature block; spec now scores L5 (Governed).
- **Citation-resolution remediation (R-REL-044 / CAP-REL-035) (C-D2)** — resolved the unannotated citations the release citation validator flagged on published v3.18/v3.19 surfaces; cross-repo readers no longer hit unexplained 404s.
- **Citation validator `.aget/specs/` resolver** — the validator falsely 404'd correct `.aget/specs/...` citations (a leading-dot path-resolution bug); now resolves them against the canonical tree, with a regression test.
- **Framework CI capability (C-I1)** — pre-push hook hardening; corrected a `--critical` mode that would have run hardcoded tests absent from templates.

### Notes

- This release carries internal anti-confabulation and audit-after-synthesis disciplines that govern how the cycle itself was built; those are documented in the framework's internal evolution record.  [instance-only per L600]

---

## [3.19.0] - 2026-05-23

**Theme**: **Discipline + Healthy Friction Codification**. The cycle's defining contribution is the framework's anti-confabulation and authorization-shape disciplines landing as *enforced structure* rather than prose advice: the agent's NBA-fill refusal (L976/L979), audit-after-synthesis pairing (L980), and over-application scope discipline (L983) are now wired into the skills, specs, and SOPs that govern day-to-day operation. "Healthy Friction" — surfacing a decision rather than rolling past it — is treated as a first-class release quality.  [instance-only per L600]

> **No breaking changes** in v3.19. Existing instances upgrade by version-bump only.

> **Sleeping CAPs — CAP-REL-032 + CAP-REL-033** (R-REL-028/029 post-release validators): grace-extended to v3.19.0 under an R-DEP-4 structural commitment (implement OR explicitly reclassify by v3.19; *no further grace authorized*). v3.19 did **not** implement them, so per the R-DEP-4 disposition they were **formally RECLASSIFIED** (2026-05-23, principal-elected) from the "will-implement grace" track to **Spec-Landed / Implementation-Optional** (no implement-deadline; permanently non-blocking; a future cycle MAY implement as net-new work). This closes the L671 decorative-grace risk rather than extending grace a 5th cycle. No *operational* degradation and no *new* sleeping CAPs in v3.19. See `governance/POLICY_deprecation.md`.  [instance-only per L600]

> **Scope carry**: Tier 2 PCRV citation-resolution remediation (245 unannotated 404s on v3.18 surfaces) re-baselined to v3.20 as a priority carry — theme-orthogonal, and the citation validator is not yet auto-enforced in the pre-release chain (L131 transparency flag recorded).  [instance-only per L600]

### Added — Tier 1 (Implementation)

- **`/aget-propose-actions` Step 2.7 — Audit-After-Synthesis pre-check** (REQ-PA-013 + CAP-PA-013-01..04): when ≥2 proposed Next-Best-Actions write synthesis-class rows to the same governed artifact, at least one must classify as audit-class (re-derives quantities from primary sources). Reference classifier `propose_actions_classify.py`; replay suite `test_propose_actions_step_2_7.py` (7 tests). This is the **structural (Channel-5)** landing of the L980 audit-after-synthesis discipline and gh#1476 Healthy Friction codification.  [instance-only per L600]

- **`/aget-propose-actions` Step 2.8 — Aspirational-Flag Authorization-Shape pre-check** (REQ-PA-014 + REQ-PA-015): distinguishes **agent-mode** self-issued aspirational flag-forms (`--count=auto`/`--batch`/`--go` not in the skill's documented parameter set) → **REFUSE** (closes the L976/L979 NBA-fill / 24h-recurrence vector), from **principal-mode** principal-typed flag-forms → **ACCEPT without ceremony** (the F1 friction-reduction default). Budget remains a ceiling; trigger-presence is the floor.  [instance-only per L600]

- **`AGET_ISSUE_GOVERNANCE_SPEC` v2.1.0 → v2.2.0** (PP-042 Stream 1): introduces issue `routing_mode` ∈ {`direct`, `supervisor_intake`, `supervisor_editorial`, `lesson_first`} with CAP-ISSUE-009..014 + V-ISSUE-015..020 (CAP-001..008 intact). Lesson-first filings reference a captured L-doc as substrate (L977) for L-doc↔issue traceability. Paired with **ADR-021 Amendment 1** (supervisor relay modes).  [instance-only per L600]

- **gh#1476 Healthy Friction codification — SOP point-of-use channel** (L467 Channel-2): `SOP_scope_lock_ceremony` gains a standing **§G1.AUDIT** step (generalizing the ad-hoc audit-counts pass into a reusable audit-after-synthesis gate); `SOP_release_process` gains an audit-after-synthesis note at the Version-Inventory synthesis surface. No new L-doc — L980 is the anchor (anti-banner-inflation).  [instance-only per L600]

- **L983 over-application scope discipline** (in-cycle application): the L735 public-push-window banner now carries an explicit scope qualifier (`origin = aget-framework/*` only; private `gmelli/*` repos exempt), preventing restrictive-discipline citations from being applied out of scope.  [instance-only per L600]

---

## [3.18.0] - 2026-05-16

**Theme**: **Substrate Hygiene + Memory-Layer Self-Application** (Hybrid A primary + B-tagged streams). The L908 family closed at memory layer (L960 + L963 + L964 graduated); the agent caught its own confabulation patterns in-cycle; Gate 1.5 shipped PARTIAL by honest acknowledgment of LOCK-time composition defect rather than by inventing the 18-item composition.  [instance-only per L600]

> **No breaking changes** in v3.18. Existing instances upgrade by version-bump only.

> **Spec-fault carry**: gh#1179 + gh#1180 remain OPEN per L708 annotation precedent (best-effort artifact, not blocking).  [instance-only per L600]

> **Sleeping CAPs from v3.17 — status update**: CAP-REL-032 + CAP-REL-033 GRACE-EXTENDED to v3.19.0 (second grace; R-DEP-4 explicit v3.19 IMPLEMENT commitment; T1.15 closure). R-DEP-3 RECLASSIFY (B.1): 4 wake/wind shim items moved from Active Deprecations to Active Aliases. v3.18 ships ZERO new sleeping CAPs at V-test layer.

### Added — Tier 1 (Implementation)

- **`AGET_MEMORY_SURFACE_SPEC` v0.2.0 canonical promotion** (T1.16): drafts/ → `specs/AGET_MEMORY_SURFACE_SPEC.md` at canonical path (canonical commit `596dea1`). Codifies harness-vs-KB taxonomy per L335. R-MS-001..007 + V-MS-001..008 + CAP-MS-001..003 at LANDED rigor. Keystones the L908 family memory-layer closure.  [instance-only per L600]

- **Verb Registry Currency** (T1.9 = PP-021, gh#1204; 8-gate sub-plan): `aget/ontology/DESIGN_DIRECTION_skill_verb_vocabulary.md` refreshed to 37 Active + 4 Reserved verbs + 11 §Hierarchy Decisions pairs (incl. `analyze ⊂ check`, `scan ⊂ study`, `update ⊂ enhance`, `verify ⊂ validate`, `research ⊂ study`). `SOP_verb_registry_maintenance.md` v1.0.0 wired into `SOP_release_process` Phase 1. `scripts/audit_verb_registry.py` drift-detector ships. Closes INIT-FRAMEWORK-COHERENCE Stream 2 verify/validate boundary at G3.1. Canonical promotion `63ef568`.  [instance-only per L600]

- **Fork C Hybrid homepage surface architecture** (T1.12, 8-gate sub-plan): Org-profile inline release entries bounded to v3.10+ (14 pre-v3.10 entries archived to `release-notes/archive/HOMEPAGE_INLINE_RELEASES_v2.10_to_v3.9.md`); `## Roadmap` section renamed to `## Release History` (L943 closure); release-narrative authorship concentrated in Releases body + CHANGELOG. Cross-repo evidence: `aget` `b35517d`/`6ae6724`/`ae7a3a5`/`95e5a2e` + `.github` `f7f8cf3`/`05d13d6`. L941-L944 anti-pattern cluster closed structurally.  [instance-only per L600]

- **`release_homepage_update.py` ADR-008 Generator** (T1.12 Gate 3 = Generator Plan G0+G1+G2 folded inline): 8-surface atomic update + `--check` mode powering the broadened V-G7.5; closes L935 V-G7.5 synecdoche + L941 6th-recurrence pattern.  [instance-only per L600]

- **REQ-HOM v1.2.0 — Fork C bounding** (T1.12 Gate 2): REQ-HOM-Q-003 scope explicitly bounded to N=2 surfaces (1 coherence pair); REQ-HOM-F-006 retired with R-DEP-010 5-field block + v3.20 grace.

- **/aget-go capture wiring** (T1.8 + T1.10, INIT-PRINCIPLED-EXECUTION Stream 1): SKILL-024 (`/aget-propose-actions`) v1.3.0 amended with REQ-PA-006a (Step 4.5 Batch GO Capture). `scripts/extract_go_records.py` + `scripts/audit_pa_006a.py` (V-PA-006a falsifier) + `scripts/wind_down_ext.py` GO-telemetry surface ship. Empirical: 31 cumulative `/aget-go` records / 58% override rate visible at session-close. Closes gh#1267.  [instance-only per L600]

- **SOP_release_process Phase 7.8 Cross-AGENT Pilot Pre-Flight Gate** (T1.7): Pilot Pair = framework-agent + supervisor-agent; failure-mode = hard-block with L178 override path. Implements L656 + L671 + L908 + L940 Mitigation 3 simultaneously. Closes gh#1281. Private working v1.47; canonical promotion deferred.  [instance-only per L600]

- **`scripts/validate_release_body_conformance.py` canonical promotion** (T1.6, gh#1308): private → canonical with L909 header sanitization (private-context refs removed; CAP-REL-006-02-NN logic preserved verbatim). Canonical `9b3fcd9` (combined T1.4 + T1.6 commit).  [instance-only per L600]

- **Canonical aget pytest collection fix** (T1.4, gh#1279): 4× `'validation'` → `'verification'` path corrections at `tests/capability_architecture/` + new `conftest.py` `collect_ignore_glob = ["templates/*"]`. `pytest --collect-only` returns 0 errors; 235 tests collected (delta +63 from prior 172). Canonical `9b3fcd9`.

- **`/aget-close-session` v1.0.0 → v1.1.0** (T1.2, gh#1300): R-CLOSE-046 conditional invocation of `record_invocation.py` + V-CLOSE-046 V-test added. WARN text when record_invocation.py absent; changelog v1.1.0 entry.

- **TEMPLATE_REPOS 3 stale pin sites canonical** (T1.1, gh#1287 CLOSED): code already at canonical `7929d4d` (2026-05-10); v3.18 administrative closure with issue close + state-verification audit (F-001 captured at V3_18_IMPROVEMENTS.md — agent caught the recency-state-verification gap during pre-build Critic).

- **R-DEP-010 disposition registry update** (T1.15): `governance/POLICY_deprecation.md` §Active Grace Extensions (CAP-REL-032/033 v3.19 + R-DEP-4 commitment) + new §Active Aliases (4 wake/wind shim RECLASSIFIED per B.1). Closes the 4th/5th grace cycle L671 decorative-classification risk.  [instance-only per L600]

### Added — Tier 2 (Specification Authoring; PARTIAL close)

- **AGET_MEMORY_SURFACE_SPEC V-tests + cross-references wiring** (T2.37, PAIRED-AFTER T1.16): `aget/specs/AGET_MEMORY_SURFACE_SPEC.md` R-MS-003 path convention prelude + R-MS-005 Spec class row split + Outbound/Inbound subsections; `aget/specs/AGET_LDOC_SPEC.md` + `aget/specs/AGET_EVOLUTION_SPEC.md` cross-refs added. Canonical `0579a3a`. L908 family memory-layer closure keystone.  [instance-only per L600]

- **PP-035 Migration PR-Recording Column + V-test + v3.17 backfill** (T2.44, closes gh#1392): Adds `Migration PR` column to `RELEASE_HANDOFF_TEMPLATE.md` (canonical + private mirror); wires V-UPGRADE-004 in `SOP_point_upgrade.md` Phase 4; backfills v3.17.0 handoff (3 confirmed agents). Predecessor substrate to T2.42 `/aget-document-migration` (v3.19). Canonical `7c0ea21..265813f`.

- **`/aget-create-initiative` Strict skill promotion** (T2.46): D71 verb-pair gap closed. Direct authoring of `planning/initiatives/INIT-*.md` now PROHIBITED unless skill invoked. Mirrors `/aget-create-project` Strict precedent. Three Strict skills now: `/aget-create-project`, `/aget-create-initiative`, `/aget-file-issue`.

### Changed

- **`SOP_release_process.md` v1.45 → v1.49 (canonical)**: V-G7.5 broadened from single-surface badge grep to 8-surface multi-condition correctness via `release_homepage_update.py --check`; Keep-a-Changelog `[Unreleased]` adoption pattern documented (L944 closure).  [instance-only per L600]
- **`POLICY_deprecation.md`**: CAP-REL-032 + CAP-REL-033 second grace extension recorded (v3.18 → v3.19; R-DEP-011 + R-DEP-4 IMPLEMENT commitment); §Active Aliases section added (4 wake/wind shim items reclassified from Active Deprecations per R-DEP-3 B.1).

### Gate 1.5 PARTIAL Close — DEFECT-2/4 Acknowledgment

v3.18 ships with **Tier 2 LANDED-rate = 3/18 (17%; ceiling-bound)** under explicit structural defect documentation:

- **DEFECT-2**: VERSION_SCOPE Tier 2 catalog lacks per-row IN/OUT marker column.
- **DEFECT-4**: LOCK ceremony at 2026-05-16T23:18:38Z captured aggregate counts (39 IN / 131 SU) but did not persist cohort composition. Structurally incomplete L908 self-instance at LOCK boundary.  [instance-only per L600]

Agent-side path (b) enumeration produced 42 candidate items (not 18); the 24 trim decisions were not derivable from on-disk rules. Producing an 18-item list would have required inventing 24 trim decisions = direct L964 instance (*Fabricating Capture Data While Authoring Capture Discipline*). The agent **refused to confabulate** and re-routed to path (c) partial-close + structural defect documentation.  [instance-only per L600]

Four forward-routables filed to v3.19:
- F-G1.5-AUDIT-1: `AGET_PROJECT_PLAN_SPEC` amendment (per-row IN/OUT markers when aggregate-only counts claimed)
- F-G1.5-AUDIT-2: `SCOPE_LOCK_SPEC` heading-uniqueness validator
- F-G1.5-AUDIT-3: Lock-time markdown structural defect validator strengthening
- F-G1.5-AUDIT-4: `SCOPE_LOCK_SPEC` lock-event MUST capture explicit IN-set, not only aggregate counts

The honest acknowledgment is itself the deliverable.

### Memory-Layer L-doc graduations (L960–L966)  [instance-only per L600]

- **L960** Memory-Entry-as-Claim-Not-Premise — graduated 2026-05-16 per T1.11 (the L908 family memory-layer principle)  [instance-only per L600]
- **L961** HANDOFF-Deferral-Not-Invitation cross-session L908  [instance-only per L600]
- **L963** Verify-Before-Authorize Not-Only-Before-Recommend (`/aget-go` step extension of L960)  [instance-only per L600]
- **L964** Fabricating Capture Data While Authoring Capture Discipline (L908 self-instance) — the cycle's defining pattern; fired correctly at Gate 1.5 path (b)  [instance-only per L600]
- **L965** V-Test Regex Defect Cascade (macOS BSD sed vs GNU)  [instance-only per L600]
- **L966** Scaffold-Only Discipline Subordinated to Velocity Opportunity (T1.12 G6 close)  [instance-only per L600]
- **L962** L-doc candidate pending graduation — v3.19 scope  [instance-only per L600]

### Cycle Metrics

- Tier 1 LANDED-rate at Gate 1 close: **15/17 = 88%** — exceeds H-V318-RELEASE-001 target ≥11/17 (65%) by 23 percentage points.
- Tier 2 LANDED-rate at Gate 1.5 close: 3/18 = 17% (ceiling-bound per DEFECT-4).
- Gate 1 velocity: 11 LANDED / ~6 hr = ~9 SU/hr (~1.8× v3.17 baseline 5 SU/hr).
- T1.9 PP-021: 15 SU est / ~2 hr actual = ~7.5× planned rate (baseline-credit cascades + execute-stop-commit discipline).
- T1.12 Homepage Fork: ~10 SU est / ~75 min actual = ~8× planned rate.

---

## [3.17.0] - 2026-05-09

**Theme**: **C3 — Canonical Coherence + Structural Self-Conformance**. Framework self-conforms to its own canonical artifacts at every gate boundary. v3.16's #1 lesson hardened: V-tests must verify correctness, not presence — extended in v3.17 to a SECOND axis (scope-of-validation: V-test must cover the actual canonical-artifact universe, not the assumed universe).

> **No breaking changes** in v3.17. The framework-manager archetype field addition is additive (existing `archetype: "operator"` instances continue to function; new `archetype: "framework-manager"` is the formalization for framework-AGETs that previously had no archetype slot).

> **Spec-fault carry**: gh#1179 (R-REL-022-01 enum vs R-REL-029-05 'LOCKED' status, 3-way vocabulary collision) and gh#1180 (V-PP-007 enum vs CAP-PP-001/003-01 enum, 3-way collision) remain OPEN. Disposition: best-effort artifact + L708 annotation per v3.16 precedent. No release-blocking impact.  [instance-only per L600]

> **Sleeping CAPs from v3.16 — status update**: CAP-REL-030/031/032/033 SPEC-LANDED-IMPLEMENTATION-DEFERRED were committed for v3.17 implementation. Status: CAP-REL-030 + CAP-REL-031 IMPLEMENTED (T1.1 + T1.2 closed Gate 1); CAP-REL-032 + CAP-REL-033 grace-extended to v3.18.0 (T1.3 + T1.4 GRACE-EXTEND per Q1=B disposition; R-DEP-011 grace-period rationale recorded).

### Added — Tier 1 (Implementation)

- **CAP-REL-030 Post-Release CHANGELOG Validator** (T1.1): Implementation script + multi-site equality V-test against v3.16.0 reference (14/14 PASS). Closes the post-release CHANGELOG-quality-validation gap.

- **CAP-REL-031 Post-Release Tag Validator** (T1.2): Implementation script + 5-site PASS against v3.16.0 reference. Closes the tag-monotonicity + tag-message-presence gap.

- **`scripts/health_check.py` substance-aware evolution check** (T1.8, gh#1211): New `check_evolution_directory_substance(agent_path)` returning (file_count, byte_size, non_ldoc_count) substance metrics. Thresholds: WARN at non_ldoc_count > 2× l_doc_count; CRITICAL at non_ldoc_count > 10× l_doc_count OR byte_size > 100 MB. Closes the L656 check-by-shape vs check-by-substance gap surfaced at a fleet-upgrade readiness review (one agent had 192k *-EXT.md hoarded files invisible to L-doc-only glob).  [instance-only per L600]

- **`sops/SOP_release_process.md` v1.32 → v1.45** (T1.5 + T1.6): H-RHSC-001 G3 + G4 SOP wiring — Phase 6.3 + Phase 7 amendments invoke the self-containment validator as BLOCKING V-tests; V-G7.1..V-G7.5 broadened from presence-style to multi-condition correctness; explicit RELEASE_REPOS array (14-element including `template-document-processor-AGET` uppercase suffix that case-sensitive bash glob silently skipped). Closes Synecdoche-HIGH/MEDIUM gaps from `docs/AUDIT_validator_synecdoche_2026-05-08.md`.

- **`framework-manager` agent archetype** (T1.7, per VERSION_SCOPE Q4=A.2): Coined the new archetype for framework public-repo management; closes self-classification gap surfaced via L908 self-application audit. 6-site amendment: `.aget/identity.json` + `.aget/version.json` + `governance/CHARTER.md` + `governance/SCOPE_BOUNDARIES.md` + `AGENTS.md`/`CLAUDE.md` + ontology C610 FrameworkManagerArchetype (full SKOS structure). Multi-site equality V-T1.7-EXT (11 conditions) PASS empirically. Theoretical basis: Stewardship Theory of Management (Davis/Schoorman/Donaldson 1997).  [instance-only per L600]

### Added — Tier 2 (Specification Authoring)

- **`sops/SOP_scope_lock_ceremony.md` v1.0.0 LANDED** (T2.18): Standard operating procedure for the scope-lock ceremony — structured 4-gate ritual transitioning `VERSION_SCOPE_vX.Y.Z.md` from PLANNING to READY FOR RELEASE. Empirically grounded by v3.16 (commit `91c5871`) and v3.17 (commit `e50a182`) lock events. Theme C3 self-conformance: this SOP codifies the very ceremony executed at the v3.17 lock event.

- **`specs/AGET_SKILL_LIFECYCLE_SPEC.md` v1.0.0 LANDED** (T2.19): Codifies the AGET skill artifact model — 6 distinct artifact attributes (Skill executable / Proposal / Private SKILL.md / Private Spec / Canonical SKILL.md / Canonical Spec) + Promotion State enum (Private-Only / Yaml-Promoted / Mirrored / Drifted / ID-Conflict) + canonical-vs-private governance discipline (per L910). 7 CAPs at LANDED rigor with 14 EARS-formalized requirement IDs (2 sub-requirements per CAP) + 7 V-tests authored as multi-condition correctness checks + Conformance Matrix. Closes ADR-008 progression gap (L-doc → SOP → Spec → Skill) at the skill governance layer. NO sleeping CAPs (rejected v3.16 SPEC-LANDED-IMPL-DEFERRED precedent in favor of full V-test authoring).  [instance-only per L600]

- **`specs/drafts/AGET_FLEET_UPGRADE_SPEC_v0.1.md` v0.1.0 DRAFT** (T2.20): Codifies supervisor cross-agent modification authority + fleet upgrade modes (centralized vs distributed) + required gate ceremony for fleet-wide version bumps + L826 friction taxonomy F1-F4 defense. 4 CAPs at SKELETON rigor grounded in `scripts/fleet_upgrade.py` operational substrate (multiple historical fleet-upgrade executions). LANDED + V-test authoring + canonical promotion deferred to v3.18 P1 per L103 Premature Abstraction discipline.  [instance-only per L600]

- **`specs/drafts/AGET_TASK_ROUTING_SPEC_v0.1.md` v0.1.0 DRAFT** (T2.23): Codifies SOP-before-skill precedence rule + procedure-selection grammar (4-candidate enumeration) + D71 STRUCTURAL routing extension. 3 CAPs at SKELETON rigor + Routing Decision Matrix. LANDED + V-test authoring + canonical promotion + operational tool deferred to v3.18 P1.

### Changed

- **`AGET_RELEASE_SPEC` v1.16.1 → v1.17.0**: Pre-Release Conformance Gate (R-REL-029-05) status enum amended. Spec-fault carry per gh#1179 (3-way vocabulary collision; L708 annotation, not blocking).  [instance-only per L600]
- **`AGET_PROJECT_PLAN_SPEC` v1.2.2 → v1.2.3**: V-PP-007 enum amended. Spec-fault carry per gh#1180 (3-way collision; L708 annotation).  [instance-only per L600]
- **`POLICY_deprecation.md` Active Grace Extensions**: CAP-REL-032 + CAP-REL-033 entries added (Q1=B GRACE-EXTEND); v3.18.0 removal threshold; R-DEP-011 grace-period rationale.
- **`POLICY_deprecation.md` Active Deprecations**: 4 wake/wind shim entries (`wake_up.py`, `wind_down.py`, `wake_up_ext.py`, `wind_down_ext.py`) earliest-removal extended v3.17.0 → v3.18.0 per Q9=B grace extension.

### Inherited (from spec drop, 2026-05-03)

- **`specs/AGET_RELEASE_HANDOFF_SELF_CONTAINMENT_SPEC.md` v0.1.0** (REVIEWED): Defines self-containment as a testable property of `RELEASE_HANDOFF_v{X.Y.Z}.md` via 8 CAPs (CAP-RHSC-001..008) and 11 sub-requirements. Extends `AGET_RELEASE_SPEC v1.17.0` CAP-REL-020. Theoretical basis: Extended Mind (Clark/Chalmers), Stigmergy (Grassé), Cybernetics — Requisite Variety (Ashby).
- **`verification/validate_handoff_self_containment.py` v0.1.0**: Implements 11 V-RHSC tests against any RELEASE_HANDOFF artifact. v3.17 G3+G4 wiring: Phase 6.3 BLOCKING invocation; v3.10–v3.16 backfill audit deferred to G5 L901 re-grading.  [instance-only per L600]
- **`handoffs/SPEC_DROP_HANDOFF_self_containment_v0.1.md`**: Forwardable briefing for remote fleet supervisors.

### Theme C3 Lesson — V-test Scope-of-Validation as Second Axis of Correctness

v3.17's empirical learning, ratified at multiple gate boundaries: V-test correctness has TWO axes —
1. **Assertion correctness** (defended by multi-condition equality / set-membership / cross-site equality) — v3.16's #1 lesson
2. **Scope correctness** (defended by Critic review of declared scope vs canonical-artifact universe) — v3.17 ratification

Multiple recurrence instances:
- T1.7 framework-manager archetype: V-T1.7 v0 (4-site declared scope) PASSED but Critic-at-exit caught L908 self-application gaps requiring scope extension to V-T1.7-EXT (6 sites). Pattern: declared scope ≠ canonical artifact universe.  [instance-only per L600]
- Gate 2 CITATION.cff: V-2.1 declared 5 sites including AGENTS.md; aget/ canonical does not have AGENTS.md (script artifact_types listing showed only 3 sites for aget/); V-test corrected at execution.
- Gate 2 CITATION.cff drift: V-2.1 + V-2.6 multi-site equality CAUGHT 3-cycle drift (v3.14.1 stale through v3.15+v3.16) that script's `[OK]` output had masked. Presence-only check would have missed it.

Candidate v3.18 L-doc: "V-test scope-of-validation as second axis of correctness."

### Acknowledgments

v3.17 closes substantial framework-discipline scope (Tier 1 9/9 + Tier 2 4/4) within the Saturday push window per L735. Theme C3 self-demonstrated multiple times — at lock event (post-lock closure remediation per H-V317-LOCK-001 falsification clauses), at T1.7 build (V-T1.7 → V-T1.7-EXT), at T2.18 LANDED (SOP codifies its own ceremony), at Gate 2 CITATION.cff (script spec at fault for own behavior).  [instance-only per L600]

### Deployment-Spec-Optional Disclosure (post-publication; per gh#1274 supervisor-side audit)

v3.17.0 ships **deployment-spec-optional** by explicit policy. Unlike prior releases (v3.6.0, v3.7.0, v3.8.0, v3.9.0, v3.12.0, v3.15.0, v3.16.0 each shipped with a per-release `DEPLOYMENT_SPEC_v{X.Y.Z}.yaml`), v3.17.0 does not ship with `DEPLOYMENT_SPEC_v3.17.0.yaml`. Rationale: the DEPLOYMENT_SPEC convention has been inconsistently applied across releases (5 of ~17 cycles missing per `RELEASE_SURFACES_AUDIT_v3.17.md`); v3.17 makes the inconsistency explicit policy and routes formal `aget/specs/AGET_DEPLOYMENT_SPEC_FORMAT.md` standardization to v3.18. Fleet-upgrade tooling SHALL use the latest available `DEPLOYMENT_SPEC_v{X.Y.Z}.yaml` (currently `v3.16.0`) as the contractual artifact set; v3.17.0 inherits v3.16.0's DEPLOYMENT_SPEC contract semantically (no breaking changes).  [instance-only per L600]

### Tag-vs-HEAD Policy (post-publication; per gh#1274 supervisor-side audit)

v3.17.0 release tag `bb2f688` is **frozen at release-publication moment**; subsequent commits (`a09c66c` AGET_DELTA_v3.17.md + `cdde067` spec-debt closure CAP-REL-006-02-NN + V-tests + SOP wiring + `330cd05` precedent-grounded spec v2 + `42b8a41` title-format spec v3) are **post-tag spec polish**, not v3.17.0 deliverables. Fleet-upgrade tooling MAY pin to either:
- **`v3.17.0` tag** (canonical-frozen): instances upgrade from a stable, immutable reference matching the publication moment
- **`main` HEAD** (best-known-good): instances upgrade from current state with all post-tag spec polish applied

**Recommendation**: pin to `v3.17.0` tag for production fleet-upgrade unless post-tag spec amendments are operationally required. If pinning HEAD, document the specific commit SHA in the upgrade record. v3.18 SOP_release_process amendment (already landed Phase 6.5 BLOCKING V-test gate) ensures future releases retire the tag-vs-HEAD ambiguity by closing all release-day spec-debt before tag cut.

---

## [3.16.0] - 2026-05-02

**Theme**: Framework-Discipline Closure + Wave-1A Spec Contracts + /aget-go Production + Knowledge-Tier Isolation Skeleton

> **Sleeping-CAPs Disclosure (NEW)**: This release ships 4 spec contracts (CAP-REL-030/031/032/033) at `SPEC-LANDED; IMPLEMENTATION DEFERRED v3.17` status. Requirements are defined; enforcement scripts (`scripts/post_release_*_validator.py`) do NOT exist at v3.16.0. R-DEP-010 grace period: 2 minor versions (v3.18 removal if implementation does not land by v3.17). This is honest spec-truthfulness, surfaced by post-Gate-1 distributed defects audit (2026-05-02). Consumers SHALL NOT treat these CAPs as runtime-binding until implementation lands.

> **No breaking changes** in v3.16. The `**Status**:` → `**Plan_Status**:` template field rename is documentation-vocabulary; `wind_down.py` extended to recognize both old and new prefixes (backward-compatible).

### Added

- **`sops/SOP_fleet_migration.md` v1.5.0 → v1.6.0**: New `Wave Sequencing` section. Wave 0 (supervisor self-upgrade) → Wave 1 (pilot agents) → Wave 2 (full fleet); wave-to-phase mapping; wave-boundary V-tests; wave-skip prohibition without principal approval; wave-boundary rollback procedure.
- **`specs/AGET_LDOC_SPEC.md` v2.2.0 → v2.3.0**: Qualified L-doc IDs `{agent_short_name}-L{NNN}` for cross-fleet citation disambiguation. New `CAP-LDOC-010` (conditional EARS: cross-agent citation SHALL qualify). Backward-compat: unqualified IDs valid within agent scope. Cross-Agent Discovery example regex updated to match both forms (`r'^([a-z][a-z0-9-]*-)?L\d+$'`). Closes the L801/L807 cross-fleet collision class.  [instance-only per L600]
- **`specs/AGET_RELEASE_SPEC.md` v1.16.1 → v1.17.0**: 4 NEW Wave-1A spec contracts (sleeping; see disclosure above):
  - **CAP-REL-030 (R-REL-026)**: Post-Release CHANGELOG Validator — verifies entry presence + sanitization, BC-NNN coverage. Roots: #1149, #1151.
  - **CAP-REL-031 (R-REL-027)**: Post-Release Tag Validator — `git show vX.Y.Z:handoffs/RELEASE_HANDOFF_vX.Y.Z.md` MUST resolve. Spec-layer pair to SOP_release_process v1.30 Phase 6.4.5 fix. Root: #1154.
  - **CAP-REL-032 (R-REL-028)**: Post-Release Badge/Parity Validator — org homepage + per-repo version coherence. Definition of Done "Discoverable" enforcement.
  - **CAP-REL-033 (R-REL-029)**: Post-Release Contract-Test Validator — tests run against released tag; BC-NNN coverage matrix. Root: #1148.
- **`specs/AGET_PROJECT_PLAN_SPEC.md` v1.2.2 → v1.2.3**: New `CAP-PP-019-04` wires `/aget-go` (SKILL-048) as the canonical authorization mechanism for Gate Decision_Point (CAP-PP-019-02). Backward compat: free-text "go" remains valid for low-risk gates.
- **`specs/AGET_SECURITY_SPEC.md` v1.0.1 → v1.1.0**: New `CAP-SEC-007` (Knowledge-Tier Isolation, L805 / #874). 4 SHALL requirements covering trust-tier model (T0..T3), `.agetignore` contract, MAC-style input classification, future hook enforcement. Theoretical basis: Least Privilege (Saltzer 1975), Bell-LaPadula (1973), MAC, Defense in Depth.  [instance-only per L600]
- **`.agetignore` (NEW canonical file at aget/ root)**: Skeleton v0.1 for knowledge-tier isolation. Per-tier sections `[T0]..[T3]` (custom INI-style format; future hook will do custom parsing — gitignore parsers do NOT recognize section markers). Patterns within each section are gitignore-syntax-compatible. Hook enforcement deferred (CAP-SEC-007-04).
- **`sops/SOP_release_process.md` v1.29 → v1.30**: New `Phase 6.4.5: Tag & Release (Authoritative Position for v3.16+)` after Phase 6.4. Tag-cut moves to AFTER handoff artifacts exist in working tree (#1154 Option A). Phase 3 reduced to historical pointer for v3.15-and-earlier audits. New BLOCKING post-tag V-test: `git show vX.Y.Z:handoffs/RELEASE_HANDOFF_vX.Y.Z.md` MUST resolve.
- **SKILL-048 `/aget-go` v0.1.0 (proposed) → v1.0.0 (production)**: Records principal authorization with Healthy Friction enforcement of the principle-triad (spec+verify-first, coherence-next, evidence-driven). Composition discipline: authorizes only; does NOT execute the authorized work. 10 capabilities (CAP-GO-001..010), 10 V-tests, 6 constraints, espanso migration table (POL-DEP-001 grace `;;g*pr*` → `;;ago*`).
- **Universal-skills migration**: 10 archetype templates (advisor through spec-engineer) brought to universal-skill conformance via validator-driven batch deployment from `template-worker-aget` baseline. 150 skill directories deployed.

### Changed

- **`specs/AGET_TEMPLATE_SPEC.md` CAP-TPL-016-04**: Universal-skill mandate **32 → 29**. Release-triad skills (`aget-release-build`, `aget-release-audit-specs`, `aget-release-critique`) moved from universal baseline to release-execution archetype catalog per new `CAP-TPL-016-07`. Worker + supervisor templates retain release-triad (release-execution archetype); 10 other archetype templates do NOT (advisor/analyst/architect/consultant/developer/executive/operator/researcher/reviewer/spec-engineer). Closes the "presence-not-fit" misfit surfaced by Gate 1 defects audit (L582 instance).  [instance-only per L600]
- **`verification/validate_archetype_skills.py`**: SPEC_MANDATE 32 → 29; new `RELEASE_EXECUTION_EXTRAS` list extends worker + supervisor `ARCHETYPE_EXTRAS` to include the moved release-triad. Validator now reports 12/14 templates conformant (was 12/14 under old mandate; alignment preserved at the new boundary).
- **`templates/PROJECT_PLAN_TEMPLATE.md`**: `**Status**:` → `**Plan_Status**:` (plan-level header) and `**Status:** Pending` → `**Gate_Status:** Pending` (per-gate). Closes D4 root (plan state declared by text editing, not verifiable assertions). Backward compat preserved: `wind_down.py` extended to recognize both old (`**status**:`) and new (`**plan_status**:`) prefixes.
- **`scripts/wind_down.py`**: Extended pending-plan detection prefix list to recognize `plan_status:` / `**plan_status**:` / `**plan_status:` (in addition to legacy `status:` variants).

### Sleeping Requirements (NEW disclosure mechanism)

Per R-DEP-010 (sleeping-requirement annotation): 4 of 5 Wave-1A CAPs ship requirements without implementation at v3.16.0:

| CAP | Status | Implementation Target |
|-----|--------|----------------------|
| CAP-REL-029 (R-REL-025) Release Readiness Gate | LANDED + IMPLEMENTED 2026-04-25 | (already shipped at v3.15.0) |
| CAP-REL-030 (R-REL-026) Post-Release CHANGELOG Validator | SPEC-LANDED 2026-05-02 | v3.17 |
| CAP-REL-031 (R-REL-027) Post-Release Tag Validator | SPEC-LANDED 2026-05-02 | v3.17 (procedural V-test in SOP v1.30 Phase 6.4.5 enforces invariant inline meanwhile) |
| CAP-REL-032 (R-REL-028) Post-Release Badge/Parity Validator | SPEC-LANDED 2026-05-02 | v3.17 |
| CAP-REL-033 (R-REL-029) Post-Release Contract-Test Validator | SPEC-LANDED 2026-05-02 | v3.17 |

Removal threshold per R-DEP-011: 2 minor versions (v3.18) if implementations do not land by v3.17.

### Discipline / Process Changes (post-Gate-1-defects-audit)

- **L916 (NEW L-doc) Spec-Claimed-Delegate-Without-Implementation**: Anti-pattern documented. A spec asserts a *specific* delegate/consumer relationship that the named target does not implement. Stronger than L671 because the metadata actively misleads (vs. inert decorative metadata). Fixed instance in this release: SKILL-048 spec line 30 previously claimed `delegates: SKILL-015 aget-close-session (reads authorization records for retrospective)` — close-session does NOT read records. Removed false delegate claim; replaced with honest `consumers: TBD v3.17` stub.  [instance-only per L600]
- **Distributed gating-Triad mechanism**: Post-Gate-1-close defects audit ran an independent Agent-tool subagent Auditor that confirmed 5/8 Builder-self-audit defects, refuted 1/8 (Builder over-correction), partially-confirmed 2/8, surfaced 2 NEW under-corrections, caught 1 Builder fabrication. Pattern: gating-Triad with full prior-gate-closure context catches what Builder rationalizes past. v3.17 will formalize this as CAP-PP-019 amendment.

### Continuing Deprecations (from v3.14 / v3.15; no removal in v3.16)

- `scripts/wake_up.py` → `scripts/aget_open_session.py` (POL-DEP-001; **removal target v3.17 OR v3.18** per R-DEP-011 grace; revisit at v3.17 grooming)  [instance-only per L600]
- `scripts/wind_down.py` → `scripts/aget_close_session.py` (POL-DEP-001; same grace)  [instance-only per L600]

### Migration Guide

- **No breaking changes**: existing instances upgrade by version-bump only.
- **Optional adoption**: agents that author PROJECT_PLAN files SHOULD migrate to `**Plan_Status**:` / `**Gate_Status:**` schema in new plans. Existing plans continue to work unchanged.
- **Optional adoption**: agents that produce cross-fleet citations SHOULD use qualified L-doc IDs `{agent_short_name}-L{NNN}` (CAP-LDOC-010). Local-scope citations remain valid in unqualified form.
- **`/aget-go` adoption**: optional v3.16; recommended for any gate involving spec amendment, fleet-wide change, or >1 SU work. Free-text "go" remains valid for low-risk gates.

---

## [3.15.0] - 2026-04-25

**Theme**: Two-Level Model Coherence + Security Hardening + Weekly Release Cadence Formalization

> **⚠️ Breaking Release**: v3.15 contains two breaking changes (BC-001, BC-002). See `docs/BREAKING_CHANGES_v3.15.md` and the Migration Guide below.

### Added

- `requirements/REQUIREMENTS_FORMAT.md` v1.0 → **v1.1**: Optional `constraints:` per-REQ field for ADRs, governance docs, and SOPs that bound a requirement without implementing it. Clarified acceptable `specifications:` types (CAP-*, R-*, SKILL-*, RUBRIC_*). Added Field Selection Decision Tree.
- `requirements/REQ-CORE_critical_foundations.md` — **published** (10 REQs)
- `requirements/REQ-GOV_agent_governance.md` — **published** (6 REQs)
- `specs/AGET_SESSION_SPEC.md` — **CAP-SESSION-013** (Close-Session Protocol, 10 sub-requirements). Orchestrates wind-down as a delegate phase; non-breaking composition pattern.
- `specs/AGET_SESSION_SPEC.md` — **CAP-SESSION-014** (Health Remediation Protocol, 10 sub-requirements). Tier A/B/C routing; governance boundary (SHALL NOT modify public framework files).
- **`/aget-enhance-health` skill (SKILL-049 v1.0.0)**: Remediates drift detected by `/aget-check-health` through 7 phases. Generator layer per ADR-008; fourth member of the `enhance-*` skill family (enhance-spec SKILL-041, enhance-config, enhance-coherence). Deploys to all 13 template agents.
- **`specs/AGET_BUDGET_GRAMMAR_SPEC.md` v0.2**: Four CAP-BGG-001..004 contracts at full EARS rigor. Formalizes the budget grammar used across skills and session protocols. Shipping in `drafts/` per D-BGG-CANONICAL deferral.
- **`specs/AGET_SECURITY_SPEC.md` v0.2**: Eight CAP-SEC-001..008 contracts — four outside-threat (boundary enforcement, input validation, information disclosure, dependency integrity) and four within-threat (authority overstep, scope creep, output contamination, autonomous action bounds). First dedicated security spec in the framework. Shipping in `drafts/` per D-SEC-CANONICAL deferral.
- **`verification/validate_archetype_skills.py`**: Promoted to canonical `aget/verification/` (from development location). Validates template conformance against AGET_TEMPLATE_SPEC universal-skill mandate. Closes L671 decorative-classification gap: AGET_TEMPLATE_SPEC CAP-TPL-016-04 mandate now mechanically enforced.  [instance-only per L600]
- **CAP-REL-029 (Release Readiness Gate)**: First Wave-1A spec contract — formalizes the pre-release gate checklist as a testable EARS requirement.
- **`governance/POLICY_release_cadence.md` (POL-REL-001)**: Formalizes the weekly Saturday release policy from empirical practice (6 consecutive Saturdays v3.10–v3.14). First release explicitly governed by this policy.
- **ADR-022 (Breaking-Change Policy)**: Ratified 2026-04-25 — codifies Q3=(b) interpretation (honor stated deprecation timelines; BC-001 and BC-002 are the only accelerations).
- **PIR scoring infrastructure**: `sops/SOP_release_process.md` v1.39 Phase 7.1.5 — Post-Implementation Review as a BLOCKING gate in the release process. First dogfood application: this release.

### Changed

- **`/aget-check-health` (SKILL-003) v1.0.0 → v1.1.0**: Declares detect-only scope. SC-007 (`--fix` flag) removed per DEP-FIX-FLAG-001 (documented but never implemented). Replacement: `/aget-enhance-health`.
- All 4 published REQ-* documents (CORE, GOV, HOM, REL) — Path A retrofit per REQUIREMENTS_FORMAT v1.1: off-type citations routed to `evidence:` or `constraints:`, 35 displaced citations corrected.
- `requirements/REQ-HOM_homepage_quality.md` v1.0.0 → **v1.1.0**: Refactored to YAML+Markdown REQ blocks; mechanically scorable.

### Breaking Changes

> See `docs/BREAKING_CHANGES_v3.15.md` for full migration guide.

- **BC-001 — `version.json` old field names removed**: 19 fields renamed in v3.14 (e.g., `agent_name` → `aget_agent_name`, `domain` → `aget_domain`). Dual-read backward-compat shim removed in v3.15. Any script or skill reading old names breaks. Run migration grep: `grep -rE '"(agent_name|domain|portfolio|...)"' .aget/ scripts/ .claude/`
- **BC-002 — `--fix` flag surfaces removed**: Flag documented across 13+ SKILL.md surfaces since 2026-02-10 but never implemented (L671 decorative classification). Removed in this release; `--fix` invocations will error. Replacement: `/aget-enhance-health` (SKILL-049). Note: R-DEP-011 grace-period exemption applies (no functional consumers); classified BC-002 because the documented surface creates adopter expectation.  [instance-only per L600]

### Deprecated (continuing from v3.14)

- `scripts/wake_up.py` → `scripts/aget_open_session.py` (removal v3.16 per POL-DEP-001)  [instance-only per L600]
- `scripts/wind_down.py` → `scripts/aget_close_session.py` (removal v3.16 per POL-DEP-001)  [instance-only per L600]

Grace period honored per ADR-022 interpretation (b) — both shims remain active through v3.15.

### Deprecated (new in v3.15)

- **`/aget-check-health --fix` flag** (DEP-FIX-FLAG-001): Removed same release per R-DEP-011 grace-period exemption (decorative artifact, no consumers). Registered in `governance/POLICY_deprecation.md`.

### Surfaced (v3.16 candidates)

- 12 missing CAP-* / R-* / RUBRIC_* contracts referenced by REQ-* but not yet authored. Now visible as L2 (Defined) regressions in mechanical rubric scoring. Wave-1B authoring is a v3.16 candidate.
- `REQ-OPS-F-001` (agent maintains operational health) — missing REQ-layer artifact for the health domain. Candidate for v3.16 authoring.

### Notes

- First breaking release in the 3.x minor cycle (ADR-022). Migration cost estimate: 30–60 min per agent (vs 15–20 min for prior non-breaking releases).
- REQUIREMENTS_FORMAT v1.1 `constraints:` field is additive (no removed fields). The breaking changes are in version.json field names (BC-001) and --fix flag removal (BC-002) — not in requirement format changes.
- First release explicitly governed by POL-REL-001 (Weekly Saturday Release Policy). The empirical Saturday cadence has been formalized as a durable policy artifact.

---

## [3.14.1] - 2026-04-18

**Theme**: #979 Installer Partial-Propagation Hotfix

### Fixed

- `installer/install.py` in `template-advisor-aget`, `template-developer-aget`, and `template-spec-engineer-aget` now references `scripts/health_check.py` (was `scripts/housekeeping_protocol.py` — stale reference from partial #979 propagation in v3.11.1). Restores CI green on the 3 affected templates; `test_enhanced_installer.py::test_standard_install` and `test_advanced_install` assertions satisfied.  [instance-only per L600]

### Scope

- 4 repos bumped to v3.14.1: aget/ core (coordination) + 3 fixed templates. Other 10 templates unchanged and remain at v3.14.0. Surgical scope matches the asymmetric fix footprint.
- No breaking changes. No new deprecations.

### Notes

Hotfix driven by supervisor's pre-upgrade CI gate. Framework shipped v3.14.0 onto CI-red in these 3 templates because `validate_release_gate.py` does not query downstream fleet CI (see v3.15 candidate enhancement for pre-release fleet-readiness gate). v3.14.1 restores fleet deployability.

---
## [3.14.0] - 2026-04-18

**Theme**: v3.13 Loop Closure + Scope-Lock Discipline

### Added

- **CAP-REL-028 Upstream Deployment Feedback spec** (REQ-REL-F-009): Formalizes the feedback channel from fleet agents back to the framework owner when deployment reveals gaps (L827 runtime dependency). Closes the deployment→framework feedback loop.  [instance-only per L600]
- **DEPLOYMENT_SPEC_v3.13.0.yaml**: Template baseline + reconciliation steps for fleet upgrade. Pairs with SOP Phase 2.5 deployment artifact sync.
- **`log_skill_invocation.py`**: Skill telemetry logger. Appends structured JSONL entries to `skill_invocations.jsonl` when skills are invoked. Substrate for principal-facing skill-usage analytics.
- **CAP-SNAME-001-06 (Single-Verb Exception Registry)** in `SKILL_NAMING_CONVENTION_SPEC` v1.4.0: Permits `aget-{verb}` form for approved single-verb skills (`aget-ask` SP-018, `aget-name` SP-015). Caught as governance-debt during this release's Gate 0 test remediation.
- **Version-bump script coverage** (`.aget/patterns/release/version_bump.py`): Added `template-document-processor-AGET` to apply/check enumerations. Previously silently skipped.

### Changed

- **AGET_TEMPLATE_SPEC**: Universal skills 15 → 31. Supervisor skills 18 → 37. Reflects skill-creation work completed this cycle; template conformance now tracks the expanded set.
- **v3.13.0 handoff artifact** enriched with lessons-from-main-fleet content for WorkCo (cross-fleet pattern transfer) and DEPLOYMENT_SPEC reference + skill-deployment guide. Handoff artifacts are now self-contained for remote fleets.
- **Version bump**: 3.13.0 → 3.14.0 across aget/ core and 13 templates (29 version-bearing files updated atomically; L429 compliance).  [instance-only per L600]

### Fixed

- **R-ISSUE-011 sanitization**: 3 `private-*` references removed from public v3.13 handoff. Pattern generalized into `/aget-file-issue` sanitization path (L638 private-first routing).  [instance-only per L600]
- **SESSION_SKILLS_INDEX canonical paths**: `.aget/patterns/session/` → `scripts/` per DEPLOYMENT_SPEC v1.1.0.

### Deprecated

Per POL-DEP-001 (2 minor-version grace per R-DEP-011):

- `scripts/wake_up.py` → `scripts/aget_open_session.py` (removal v3.16.0)  [instance-only per L600]
- `scripts/wind_down.py` → `scripts/aget_close_session.py` (removal v3.16.0)  [instance-only per L600]
- `scripts/wake_up_ext.py` → `scripts/aget_open_session_ext.py` (removal v3.16.0)  [instance-only per L600]
- `scripts/wind_down_ext.py` → `scripts/aget_close_session_ext.py` (removal v3.16.0)  [instance-only per L600]

v3.14 and v3.15 accept both old and new names.

### Governance

- **v3.14 scope-locked** at v1.0.0 (2026-04-18). 56 items across 6 committed themes: prefix normalization, fleet tooling, triad generalization, requirements publication, framework transparency, fleet economics. Execution through v3.14.x patches and v3.15 — this release does not claim delivery of the 56 items.

### Notes

This CHANGELOG entry is retrospective-dominant: v3.14.0's content is primarily what the v3.13 cycle finally landed, plus governance-debt repayment caught during release-day verification.

---

## [3.13.0] - 2026-04-12

**Theme**: Operational Maturation & Fleet Automation

### Added

- **validate_release_gate.py**: Structural exit-code enforcement — orchestrates 7 validators, gates on combined result, logs to gate_log.jsonl. Fixes L784 (Observation Without Consequence). (#823)  [instance-only per L600]
- **fleet_upgrade.py**: Single-script fleet migration across 14 repos. Reduces permission prompts from 25-40 to ≤5. Dry-run mode, JSON output, per-repo error handling. (#829)
- **Release Delivery Triad v0.2.0**: Builder (SP-012), Spec Auditor (SP-013), Critic (SP-014) — three-perspective quality assessment at every gate boundary. Requirements sections, tool integration, telemetry logging. (L818, #933)  [instance-only per L600]
- **8 new skills** (24→31): aget-promote-issue (SP-004), aget-describe-session (SP-009), aget-propose-actions (SP-011), aget-create-rubric (SP-003), aget-check-initiative (SP-004b), aget-process-observation (SP-002), aget-open-session (SP-010), aget-check-facts (SP-007)
- **Skill Telemetry Infrastructure**: Mandatory `## Requirements` section in SKILL.template.md. Invocation logger (log_skill_invocation.py → skill_invocations.jsonl).
- **HEALTH_CHECK_ORCHESTRATION_SPEC v0.1.0**: 3-tier health check definition (Quick/Standard/Full). Resolves L787 interpretation divergence. (#834)  [instance-only per L600]
- **WIND_DOWN_DISPLAY_SPEC v0.1.0**: Formal wind-down output format with section markers, ordering, content requirements. Unblocks SP-008 close-session. (#831)
- **GOVERNED_DISCOURSE_BOUNDARY_SPEC v0.1.0**: Governed vs Informal artifact classification. 3 high-impact terms defined. (#852)
- **check_script_divergence.py**: Tracks health_check.py, study_topic.py, wake_up.py, wind_down.py divergence across 13 templates by hash groups. (#845)
- **MIGRATION_COMPLETION_REPORT template**: Structured format for supervisor fleet upgrade reporting. (#843)
- **Catch-Up Guide**: Conditional handoff section for agents skipping versions. (#844)
- **SKILL-043 aget-create-briefing**: Universal Creation skill for narrative documents. (#810)

### Changed

- **validate_release_gate.py** (public): Added missing `import os`, updated template list from 12 (3 phantom) to 13 (actual). Critic subagent finding.
- **Handoff template**: Self-contained for remote fleets — DEPLOYMENT_SPEC access note added. (#846)

### Fixed

- **ADOPTION_GUIDE**: Removed fabricated `"fleet"` object from version.json example. (#914)
- **fleet_upgrade.py**: Removed hardcoded path fallback, replaced with environment variable. Critic subagent finding.

---

## [3.12.0] - 2026-04-04

**Theme**: Developer Surface & Governance Maturation

### Added

- **AGET_ISSUE_GOVERNANCE_SPEC v2.1.0**: 3 new capabilities — CAP-ISSUE-006 (Issue Triage), CAP-ISSUE-007 (Issue Lifecycle), CAP-ISSUE-008 (Issue Forms). 9 new EARS requirements (R-ISSUE-015 through R-ISSUE-023). 54 new SKOS vocabulary terms across 4 concept groups (triage, lifecycle, labeling, promotion_workflow). 3 new anti-patterns.
- **Issue Forms**: 3 GitHub Issue Form templates (enhancement, bug, feature) for structured public filing on aget-framework/aget.
- **Faceted label taxonomy**: 26 governed labels across 5 categories (type, priority, domain, status, owner) deployed to issue tracker.
- **REQ-HOM requirements**: 6 functional + 3 quality requirements for homepage messaging quality.
- **study_topic.py epistemic parameterization**: `--purpose` (4 values) and `--domain-keywords` flags for agent-aware KB search. Purpose weighting via config priority_areas, domain boosting via config domain_keywords. CAP-SESSION-007-06/07.
- **SOP_fleet_migration v1.4**: `gh release list` discovery step (L723).  [instance-only per L600]

### Changed

- **README.md rewritten**: 169 → 104 lines. Quick Start at line 14 (was 106). Pain-point framing. Platform claims corrected (Codex/Gemini: Compatible, not Validated). R-HOM-001 conformance 1/7 → 6/7.
- **ISSUE_FILING_GUIDE v2.1**: Added triage, lifecycle, and faceted label sections.
- **3 sections relocated to docs/**: STRATEGIC_CONTEXT.md, ARCHETYPE_ECOSYSTEM.md, ONTOLOGY_DESIGN.md (from README.md per REQ-HOM-F-005).

### Deprecated

- First deprecation cycle COMPLETE: `capture` verb, `study-up` script reference, `record-nugget` skill directory — all removed (POL-DEP-001).

---

## [3.11.1] - 2026-04-04

**Theme**: Script Rename Stabilization

### Changed

- **Script rename**: `aget_housekeeping_protocol.py` → `health_check.py` across core + 12 templates (HCNA-001). Spec amendments: AGET_SESSION_SPEC CAP-SESSION-008, AGET_RELEASE_SPEC, SESSION_SKILLS_INDEX.yaml.
- **Script rename**: `study_up.py` → `study_topic.py` across core + 12 templates (SSNA #805).
- **Config key**: `skip_sanity` → `skip_health_check` in wind_down configuration.
- **SOP_release_process.md** v1.33 → v1.37: VERSION_SCOPE state machine (L708), Phase 3.5 BLOCKING deployment_monitor --init (L772), Phase 4 structural invocation requirement (#738), repo count 13→14, tag_release.py preferred method.  [instance-only per L600]

### Added

- **tag_release.py**: Automated tag + push + GitHub Release for all 14 repos. Dynamic repo discovery, ADR-004 three-tier degradation, --dry-run support. (#739)
- **verify_deployment.py**: Version-parameterized deployment verification script (REQ-REL-F-007, #744).
- **REQ-REL-F-008**: Remote Fleet Notification requirement + AGET_RELEASE_SPEC v1.13.0 (L755, #754).  [instance-only per L600]

### Fixed

- **Homepage**: Aligned to principal's voice (L733). Conformance fixes (R-HOM-001-03/04/05).  [instance-only per L600]
- **Public handoff**: Sanitized per R-ISSUE-011 (HFX-004).
- **verify_deployment.py**: Multiple fixes — manifest format, migration_history support, self-exclusion, framework core detection.

---

## [3.11.0] - 2026-03-28

**Theme**: Skill Conformance, Configuration & Requirements Formalization

### Added

- **Requirements directory** (`requirements/`): New human-level requirements layer per L742 two-level model. REQUIREMENTS_FORMAT.md v1.0 defines the format. REQ-REL v1.1.0 is the first exemplar (6 functional + 3 quality requirements for release quality). (#725)  [instance-only per L600]
- **Hooks directory** (`.claude/hooks/`): Scaffolded across all 12 templates with README. HOOK_ADOPTION_GUIDE.md published. ADR-008 Generator level infrastructure. (#505)
- **Governance intensity field**: All 12 template AGENTS.md files now declare `governance_intensity` (Rigorous/Standard/Lightweight). 6/12 contract tests added. (#732)
- **Pre-push hook** (`push_window_guard.sh`): Blocks non-Saturday pushes to aget-framework repos. ADR-008 Generator level. (#672)
- **Homepage roadmap section**: "What's Next" section in README.md. (#637)
- **DEPLOYMENT_SPEC_v3.11.0.yaml**: State specification for v3.11.0 deployment verification.

### Changed

- **AGET_RELEASE_SPEC** v1.10.0 → v1.11.0: Added Requirements Grounding section (L742). First bidirectional requirements ↔ spec traceability. Maps 9 REQ-REL requirements to 27 CAP-RELs.  [instance-only per L600]
- **17 skill instructions remediated** for L736 conformance (SICR, #678). Assert-before-verify anti-pattern eliminated across all SKILL.md files.  [instance-only per L600]
- **"sanity check" → "health check"** terminology: 72 references updated across 12 files. (#658)
- **study_up.py**: Fixed punctuation token filter + 2-keyword threshold for cross-cutting topics. (#731)
- **REQ-REL** v1.0.0 → v1.1.0: Added CAP-REL traceability column. Status draft → proposed.

### Fixed

- **Phantom traceability**: 2 phantom CAP references cleaned (CAP-CLI-082/083, CAP-SKILL-005-001..011). (#552)
- **wind_down.py** content sync: sanity → health terminology aligned between private and public copies.

---

## [3.10.0] - 2026-03-21

**Theme**: Structural Enforcement — converting behavioral governance to structural governance

### Added

- **MUST-invoke directives** in CLAUDE.md for `/aget-create-project` and `/aget-file-issue` — structural prevention of ungoverned project creation and issue filing (D71 Layer 1)

- **Gate Boundary Protocol** in SOP_release_process.md — 6-item checklist requiring plan update + commit as structural proof of gate completion (D71 Layer 2)

- **Skill Completion Signal** pattern in `/aget-create-project` and `/aget-enhance-spec` — signal absence = incomplete execution (D71 Layer 3)

- **Structural Skill Routing table** and **Governance Bypass Detection** in CLAUDE.md — machine-readable routing with 3 bypass-type detection

- **SOP Phase -0.5: Content Sync** in SOP_release_process.md — private→public content synchronization before version bump, 4-item checklist (D69/GOV-040)

- **R-SYNC-002** spec — 6 EARS requirements governing 4 artifact types (scripts, SOPs, specs, templates) with security scan + sync manifest

- **validate_content_sync.py** — validates file-by-file sync between private and public repos

- **validate_changelogs.py** — validates CHANGELOG.md consistency across all repos for a target version

- **SYNC_MANIFEST template** — tracks sync pairs with security scan status per release

- **SKILL_SPEC_TEMPLATE.yaml** deployed to all 12 templates (#439)

- **Structural Trigger Conditions** in PATTERN_step_back_review_kb — gate completion, assumption-changing findings, boundary slack detection

### Changed

- **Skill renames** (#480): `aget-capture-observation` → `aget-record-observation`, `aget-capture-nugget` → `aget-record-nugget`, `aget-study-up` → `aget-study-topic` — 633 refs + 30 dirs across 14 repos

- **`capture` verb retired** from Learning family, replaced by `record` (CS-002 conformance)

- **Gate Execution Discipline (L001)** strengthened: MUST update plan + MUST commit at every gate boundary  [instance-only per L600]

### Fixed

- **Template hygiene** (#574): VERSION, setup.py classifier, SECURITY.md version corrected in 4 templates

- **wind_down.py**: smarter status detection (first 30 lines), new `scan_nuggets()` function

## [3.9.0] - 2026-03-15

**Theme**: Governance Enforcement — release readiness, version management, process standardization

### Added

- **Phase -1: Release Readiness** in SOP_release_process.md: 3 sub-phases (B.1 Assessment, B.2 Conformance Audit, B.3 Principal Approval) with 12-item checklist — governs Gap B transition (L663)  [instance-only per L600]

- **Phase 0.85: Deliverable Conformance Check** in SOP_release_process.md: SHALL violations are BLOCKING. Inserted between Phase 0.8 (Verification Logging) and Phase 0.9 (Pre-Release Summary)

- **Gate 0: Spec Verification (MP-1)** in TEMPLATE_PROJECT_PLAN.md: Mandatory spec verification sweep before implementation begins. Includes L611 guidance (~40% pre-resolved probability)  [instance-only per L600]

- **GOVERNANCE_PRINCIPLES.md**: 6 Tier 1 + 5 Tier 2 meta-principles (first publication to public repo)

- **release-notes/v3.9.0.md**: Deep release notes with migration guide

### Changed

- **version_bump.py**: Extended from 2/5 to 5/5 artifact types — now covers version.json, README.md, AGENTS.md, codemeta.json, CITATION.cff. New `--check VERSION` mode validates all 27 files with exit code 1 on mismatch (D64)

### Fixed

- **aget-enhance-spec SKILL.md**: Phase Selection table now includes Phase 6 (Self-Compliance) for all categories (#418). Phantom AGET_SKILLS_SPEC reference replaced with SKILL_NAMING_CONVENTION_SPEC (#419)

## [3.8.0] - 2026-03-08

**Theme**: Governance Maturation — principle codification, deliverable conformance, structural enforcement

### Added

- **GOVERNANCE_PRINCIPLES.md v1.1.0**: 6 Tier 1 + 5 Tier 2 meta-principles codifying "what rules govern the rules" (L643, H-MPC-001 CONFIRMED)  [instance-only per L600]

- **Structural Aesthetics Principle**: Third design principle integrated into DESIGN_PHILOSOPHY.md, MISSION.md, and homepage (L635, H-AES-001 CONFIRMED)  [instance-only per L600]

- **Skills**:
  - `aget-enhance-spec` v1.1.0: Specification enhancement lifecycle skill (30 requirements, 15 V-tests)
  - `aget-expand-ontology` v1.0.0: SKOS ontology expansion with web-researched, evidence-backed concepts

- **Scripts**:
  - `scripts/validate_project_plan.py`: PROJECT_PLAN existence validator — prevents prompt-as-plan anti-pattern (L340, R-GOV-PLAN-001/002/003)  [instance-only per L600]
  - `.aget/patterns/upgrade/pre_sync_check.py`: Skill customization detection before upgrade (CAP-DEP-010/011/012)

- **TEMPLATE_AGENTS_MD_SPEC v1.0.0**: Governance pattern backport to all 12 templates — `.claude/` scaffolding, skill routing tables, CLI feature adoption patterns (L640)  [instance-only per L600]

- **DEPLOYMENT_SPEC_v3.8.0.yaml**: Target-state deployment specification with verification script

### Changed

- **Conformance script**: 3 missing v3.7.0-specific check methods implemented (D16)
- **Session scripts**: 4 scripts migrated from `.aget/patterns/session/` to `scripts/` (D17)
- **identity.json**: `type` field added across templates (D19)
- **CLAUDE.md**: Stale references updated across templates (D20)
- **identity.json variants**: Archetype-specific variants aligned (D21)
- **Notification validation**: Post-release validator checks notification delivery (D13)
- **SOP headers**: 19 mechanical header edits for CAP-SOP-001 compliance (D32)
- **Deliverable conformance**: 5 SHALL violations fixed across scripts, skills, SOPs (Gate 4.5)

### Fixed

- **codemeta.json**: Version corrected from 3.6.0 to 3.8.0 (missed in v3.7.0)
- **CITATION.cff**: Version corrected from 3.6.0 to 3.8.0 (missed in v3.7.0)

### Notes

- 16/38 VERSION_SCOPE items implemented; remaining deferred to v3.9.0
- Contract tests: 135 passing
- Velocity: 0.15x estimated time (3.5h actual vs 23.5h estimated for development gates)
- Gate 4.5 (unplanned): Cross-artifact conformance audit found 5 SHALL violations — all fixed before release

---

## [3.7.0] - 2026-03-05

**Theme**: Quality Reconciliation — aligning claims with reality, closing SOP gaps, content integrity

### Added

- **CONTENT_INTEGRITY_VALIDATION_SPEC v1.0.0** (L608 remediation):  [instance-only per L600]
  - 8 CAP-CIV groups covering all L608 content claim drift dimensions  [instance-only per L600]
  - 38 EARS requirements with enforcement matrix (pre-release, post-release, conformance)
  - SKOS vocabulary (6 terms), 3 operational validators mapped

- **Specification Enhancement Lifecycle** (L622, ADR-008):  [instance-only per L600]
  - SKILL-041 `aget-enhance-spec` v1.1.0: 30 requirements, 15 V-tests
  - SOP_specification_enhancement.md: 7-phase lifecycle (Advisory enforcement)
  - Governance logging requirements (L624)  [instance-only per L600]

- **SOPs**:
  - `SOP_release_scope_decision.md` v1.0.0: 7-phase scope decision lifecycle with P1/P2/P3 rubric, value-cost scoring, deferral staleness tracking, and JSONL decision log
  - `SOP_pre_release_research.md` v1.3.0: Pre-release research procedure (18 requirements, 7 phases)

- **Spec Enhancements**:
  - AGET_RELEASE_SPEC v1.9.0: R-REL-019-07 public release handoff requirement (L511, L612)  [instance-only per L600]
  - CAP-INST-001: Instance Content Accuracy requirements (fleet count, portfolio count)
  - v3.6.0 upgrade guide section in UPGRADING.md

- **Validation Tooling**:
  - `tests/test_instantiate_template.py`: Agent creation template tests
  - `verify/validate_py_version_strings.py`: Python version string scanner (L608 Dim 8)  [instance-only per L600]

- **Release Artifacts** (L628 remediation):  [instance-only per L600]
  - `DEPLOYMENT_SPEC_v3.7.0.yaml`: Target-state deployment specification with embedded verification script
  - v3.7.0 conformance checks in `conformance_config.yaml`: 20 checks including verb naming, skill count, positioning
  - v3.6.0→v3.7.0 migration section in `docs/UPGRADING.md`: 5-step guide with verb rename commands

### Changed

- **AGET_SOP_SPEC v1.2.0**: CAP-SOP-006 SOP Lifecycle Management — 8 EARS requirements for lifecycle states (Draft, Active, Deprecated), phantom resolution, deprecation/redirect, referential integrity. 7 stale AGET_CORE_VOCABULARY cross-references fixed (→ AGET_VOCABULARY_SPEC).

- **Evidence-Based Positioning** (P2.7 — 15 READMEs + 2 specs):
  - AGET_POSITIONING_SPEC v1.3.0: Audience tiers reframed with evidenced capabilities
  - AGET_IDENTITY_SPEC v1.2.0: Value proposition reframed to lead with domain intelligence
  - All 12 template READMEs + 3 core READMEs: Removed undemonstrated profession claims, lead with persistent domain knowledge value

- **SOP_release_process.md v1.9.0**: Phase 6.4 added — release handoff creation, content sanitization checklist (no private agent names, repo references, fleet size), publication to `aget/handoffs/`, 4 V-tests (V-REL-038 through V-REL-041)

- **SOP_skill_deployment.md v1.1.0**: Phase 4 added — deprecation marking with `status: deprecated`, `superseded_by`, `deprecated_date` frontmatter fields. Validator integration (`validate_skill_deprecation.py`). Key principle: deprecated = warning, not error (ADR-008).

- **Skill Verb Vocabulary Reconciliation** (P2.10 — ~75 files across 14 repos):
  - 4 skill renames: `aget-healthcheck-*` → `aget-check-*`, `aget-sanity-check` → `aget-check-health`, `aget-studyup` → `aget-study-up`
  - YAML spec renames, SKILL.md content updates, `.claude/skills/` directory renames across all 12 templates
  - `check` and `study` registered as approved verbs
  - DESIGN_DIRECTION_skill_verb_vocabulary.md published

- **Skill Count Alignment** (P1.1): 3-way mismatch resolved — spec, README, and deployed skill counts aligned at 15 universal skills (was 14/14/15). INDEX.md v1.3.0 with 4 stale name fixes. 10 files updated.

- **`scripts/instantiate_template.py`**: Enhanced agent creation script with improved template instantiation

- **Supervisor Template**: 2 new archetype skills (`aget-check-fleet`, `aget-review-handoff`), evidence-rich `/aget-create-project` mode, version-aware health check fix. 21 total skills (6 archetype + 15 universal).

### Fixed

- **Phantom SOP Reference**: `SOP_session_end.md` → `SOP_session_handoff.md` in AGET_GOVERNANCE_HIERARCHY_SPEC (P2.5 — file never existed)
- **Stale Cross-References**: 7 `AGET_CORE_VOCABULARY` references → `AGET_VOCABULARY_SPEC` in AGET_SOP_SPEC (P2.8)
- **CHANGELOG Version Support**: "Latest Stable" corrected from v3.5.0 to current release

### Notes

- 19/26 VERSION_SCOPE items complete; 8 deferred to v3.8.0 (P2.3, P3.1-P3.5, CAP-REL-027, CAP-REL-028, CAP-DEP-010/011/012)
- Phantom SOP recount (P2.5): Original "17 phantom SOPs" from v3.6.0 reduced to 2 actionable gaps after systematic audit — most had been created during v3.6.0 and v3.7.0 development
- First `/aget-enhance-spec` dogfood complete (L624) — skill deployment deferred to v3.8.0; SOP + spec ship in this release  [instance-only per L600]
- Governance docs (CHARTER, MISSION, SCOPE_BOUNDARIES) enhanced with 5 structural improvements: canonical template registry, rolling goals, decision authority attribution, governance intensity declaration, quantitative baselines (P2.12)
- Release governance gap trilogy identified (L626/L627/L628): release planning lifecycle, SOP coverage completeness, version-coupled artifact inventory — structural fixes deferred to v3.8.0, immediate mitigations in release plan  [instance-only per L600]
- Contract tests: 134 passing + 1 skip (transient version state)

---

## [3.6.0] - 2026-02-21

**Theme**: Infrastructure Maturation — observability, content integrity, ontology

### Added

- **Release Observability Tooling** (L605 remediation — 5 scripts):  [instance-only per L600]
  - `scripts/validation_logger.py`: Persistent validation logging to `.aget/logs/validation_log.jsonl` (CAP-REL-021)
  - `scripts/run_gate.py`: Gate execution enforcement with sequential dependencies (CAP-REL-022)
  - `scripts/release_snapshot.py`: Pre/post release state snapshots (CAP-REL-023)
  - `scripts/propagation_audit.py`: Template propagation tracking with referential integrity (CAP-REL-024)
  - `scripts/health_logger.py`: Healthcheck result persistence (CAP-REL-025)

- **Validation Tooling**:
  - `verification/validate_template_references.py`: Reference integrity validation (Part A, ER-568)
  - `verification/validate_ontology_inheritance.py`: Ontology inheritance resolution (CAP-INST-007)
  - `verification/validate_skill_deprecation.py`: Skill deprecation lifecycle (CAP-SKILL-LIFE-001)

- **Universal Skill**: `aget-studyup` — focused KB research before implementation (14th universal skill, propagated to all 12 templates)

- **Canonical Script**: `scripts/study_up.py` — study-up protocol implementation  [instance-only per L600]

- **DEPLOYMENT_SPEC_v3.6.0.yaml**: Complete target state specification for fleet deployment

- **Vocabulary Terms** (AGET_VOCABULARY_SPEC v1.16.0):
  - `Declarative_Compliance`, `Behavioral_Compliance`, `Compliance_Divergence`, `Instruction_Asymmetry` — precision terms from cross-fleet compliance research

- **Spec Enhancements**:
  - AGET_RELEASE_SPEC v1.8.0: CAP-REL-021 through CAP-REL-026, Known Hazards Registry (CAP-REL-026)
  - AGET_MIGRATION_SPEC v1.6.0: CAP-MIG-018 lineage classification (7-scenario decision matrix)
  - 11 artifact scope vocabulary terms (CAP-CORE-006, CAP-TPL-017, CAP-SOP-005)

- **Learnings**: L606 (Development Standard Enforcement Gap), L607 (Referential Integrity Across Deployment Boundaries), L608 (Content Claim Drift)  [instance-only per L600]

### Changed

- **Canonical Scripts v2.0.0**: `wake_up.py` and `wind_down.py` rewritten with C3+C1 architecture (config-driven display + hook-based extensions)
- **Platform Claims**: All AGENTS.md now reference "Claude Code, Codex CLI, Gemini CLI" (was "Claude Code, Cursor, Aider, Windsurf"). Cursor and Aider moved to "Experimental" in CLI Support Matrix.
- **validate_ontology_compliance.py**: Extended with YAML ontology validation support (CAP-INST-008)
- **SOP_release_process.md v1.8.0**: Three-pass update (requirement refs, tool refs, observability tooling section)
- **SCRIPT_REGISTRY.yaml**: 50 entries (was 39, +11 new scripts)
- **README.md**: Platform status table with CLI Support Matrix link
- **GETTING_STARTED.md**: Added Codex CLI and Gemini CLI setup sections

### Fixed

- **Content Integrity** (6 dimensions of L607/L608):  [instance-only per L600]
  - Private agent name sanitization: 134 instances removed from public repo
  - template-spec-engineer-aget AGENTS.md: Replaced 1368-line copy-paste error with correct content
  - 3 missing template AGENTS.md created (executive, operator, reviewer)
  - Skill counts corrected: "13 universal" → "14 universal" in 8 files
  - Sub-template platform claims: 15 files across 5 templates updated
  - Dead links in README.md: ARCHETYPE_GUIDE.md → GETTING_STARTED.md, CONTRIBUTING.md → Issues page

### Notes

- This release builds enforcement tooling (Gates 1-3) before using it for release execution (Gates 4-6), breaking the cycle identified in L605  [instance-only per L600]
- Phase 0.9 pilot subsumed by comprehensive conformance check (12/12 templates CONFORMANT)
- 17 phantom SOPs documented as known gap (deferred to v3.7.0)
- VERSION_HISTORY.md backfill included (v3.4.0, v3.5.0, v3.6.0 entries)

---

## [3.5.0] - 2026-02-14

**Theme**: Archetype Customization + Issue Governance

### Added

- **Archetype-Specific Skills** (26 skills across 12 archetypes):
  - `aget-assess-risk`, `aget-recommend-action` (advisor)
  - `aget-analyze-data`, `aget-generate-report` (analyst)
  - `aget-design-architecture`, `aget-assess-tradeoffs` (architect)
  - `aget-assess-client`, `aget-propose-engagement` (consultant)
  - `aget-run-tests`, `aget-lint-code`, `aget-review-pr` (developer)
  - `aget-make-decision`, `aget-review-budget` (executive)
  - `aget-handle-incident`, `aget-run-playbook` (operator)
  - `aget-search-literature`, `aget-document-finding` (researcher)
  - `aget-review-artifact`, `aget-provide-feedback` (reviewer)
  - `aget-validate-spec`, `aget-generate-requirement` (spec-engineer)
  - `aget-broadcast-fleet`, `aget-review-agent`, `aget-escalate-issue` (supervisor)
  - `aget-execute-task`, `aget-report-progress` (worker)

- **Issue Governance Skill** (L520):  [instance-only per L600]
  - `aget-file-issue`: Universal skill for filing issues with L520 compliance  [instance-only per L600]
  - Automatic destination routing (private → {private-tracker}, public → aget-framework/aget)
  - Content sanitization for private patterns

- **Archetype Ontologies** (12 YAML files):
  - `ontology/ONTOLOGY_{archetype}.yaml` in all templates
  - SKOS+EARS format per L482  [instance-only per L600]

- **Skills Specification Infrastructure**:
  - `.aget/specs/skills/INDEX.md`: 40 skills index (14 universal + 26 archetype)  [instance-only per L600]
  - `.aget/specs/skills/SKILL_VOCABULARY.md` v1.2.0: 32 terms + governance terms  [instance-only per L600]
  - `ONTOLOGY_skills.yaml`: SKOS-compliant skill concepts

- **Agent Capability Ontology** (C041-C047):
  - Agent_Capability, Capability_Instance, Capability_Cluster concepts
  - AGET_VOCABULARY_SPEC Part 8: Capability Governance Terms

- **TEMPLATE_unit_test.py**: Formal template for unit test files (CAP-TEST-002-05)
- **L529 Migration Integrity Checks**: P6 check in aget_verify_conformance.py  [instance-only per L600]
  - V-SIZE: AGENTS.md < 1000 bytes = corruption
  - V-SYNTAX: @aget-version marker required

### Changed

- **AGET_TEMPLATE_SPEC.md**: 3.3.2 → 3.4.0 (archetype skills requirement)
- **AGET_TESTING_SPEC.md**: 1.0.0 → 1.1.0 (added CAP-TEST-002-05, template reference)
- **aget_verify_conformance.py**: 1.0.0 → 1.1.0 (added L529 integrity checks)  [instance-only per L600]
- **SOP_aget_create.md**: 2.1.0 → 2.2.0 (archetype skill deployment)
- **SOP_aget_migrate.md**: 1.1.0 → 1.2.0 (archetype migration)

### Breaking Changes

- **validation/ → verification/**: Directory renamed (44 files moved)
  - **Migration**: Update import paths: `from validation.X` → `from verification.X`
  - **Migration**: Update script references: `validation/` → `verification/`
  - **Rationale**: Naming consistency (verification scripts verify conformance)
  - **Affects**: Any code importing from `aget/validation/`

---

## [3.4.0] - 2026-01-18

**Theme**: Session Skills Maturity + Governance Formalization

### Added

- **Session Protocol Enhancements** (CAP-SESSION-010, 011, 012):
  - `wind_down.py`: Re-entrancy guard prevents concurrent executions (CAP-SESSION-010)
  - `wind_down.py`: Sanity gate runs abbreviated health check before session end (CAP-SESSION-012)
  - `wake_up.py`: Calendar awareness displays date and release window notifications (CAP-SESSION-011)
  - Cross-CLI validation on Claude Code, Codex CLI, and Gemini CLI

- **Governance Artifact SOPs and Templates**:
  - `SOP_L-DOC_CREATION.md`: Standard procedure for creating L-docs
  - `TEMPLATE_L-DOC.md`: Reusable L-doc template
  - `SOP_ENHANCEMENT_REQUEST.md`: Standard procedure for Enhancement Requests
  - `TEMPLATE_ENHANCEMENT_REQUEST.md`: Reusable Enhancement Request template
  - `SOP_project_plan_archival.md`: PROJECT_PLAN → evolution workflow (CAP-EVOL-008)

- **Release Governance** (VERSION_SCOPE formalization):
  - AGET_VOCABULARY_SPEC: 8 VERSION_SCOPE terms formalized
  - CAP-REL-012 through CAP-REL-018: VERSION_SCOPE requirements in EARS format
  - SOP Phase 2.5: Vocabulary/spec reconciliation protocol
  - SOP Phase 2.6: SOP/Template reconciliation protocol

- **Behavioral Governance**:
  - L552: Imperative Escalation Bypass pattern documented  [instance-only per L600]
  - R-BEHAV-EAC-*: Behavioral requirements for escalation acknowledgment

- **Spec-First Documentation**:
  - `AGET_IDENTITY_SPEC.yaml`: Agent identity specification (machine-readable)
  - `AGET_POSITIONING_SPEC.yaml`: Market positioning specification (machine-readable)
  - `codemeta.json`: Software metadata standard
  - `CITATION.cff`: Citation file format for academic reference

- **Template Infrastructure**:
  - `sops/` directory with SOP_escalation.md in all 12 templates (R-TEMPLATE-001)

- **Standards Document Ontology** (L502, PROJECT_PLAN_standards_ontology_elevation_v1.0):  [instance-only per L600]
  - AGET_VOCABULARY_SPEC Part 7: Document type hierarchy, authority model, traceability properties
  - 6 exemplar specification entries with `aget:defines` traceability
  - `check_ontology_coherence.sh`: Lightweight vocabulary coherence checker
  - `SOP_specification_consolidation.md`: Consolidation process
  - `SOP_artifact_deprecation.md`: Deprecation process with authority lifecycle
  - INDEX.md Authority column (CANONICAL, Active, Draft, Deprecated)

- **Release Window Timing** (CAP-REL-011):
  - AGET_RELEASE_SPEC v1.3.0: Release_Window vocabulary, CAP-REL-011 requirements
  - SOP_release_process.md v1.3.0: V0.0 timing check in Phase 0
  - Preferred windows: Thursday AM, Friday PM
  - Advisory (SHOULD) requirement with acknowledgment for off-window releases

### Changed

- **AGET_SESSION_SPEC.md**: 1.1.0 → 1.2.0 (CAP-SESSION-010, 011, 012)
- **AGET_PROJECT_PLAN_SPEC.md**: 1.1.0 → 1.2.0 (CAP-PP-013 through 018)
- **AGET_TEMPLATE_SPEC.md**: 3.3.1 → 3.3.2 (R-TEMPLATE-001)
- **AGET_EVOLUTION_SPEC.md**: 1.0.0 → 1.1.0 (PROJECT_PLAN_Entry type, CAP-EVOL-008)

- **PROJECT_PLAN Template v2.0** (L515, #233, #247):  [instance-only per L600]
  - Consolidated to single canonical template at `templates/PROJECT_PLAN_TEMPLATE.md`
  - Removed duplicate from `docs/templates/`
  - Added Plan_Status controlled vocabulary (#232)
  - Added Gate Naming Convention guidance (#233)
  - Added mandatory Project Closure Checklist (#247)
  - Added status transition rules
  - Added Gate -1 (Pre-Execution) gate
  - Added Operational Context section (CAP-PP-014)
  - Added Retrospective section (L435)  [instance-only per L600]

- **validate_project_plan.py** (L515, #233):  [instance-only per L600]
  - Now supports multiple gate naming conventions: G-N:, Gate N:, Gate N.M:, {Track}-N:
  - Extended --strict mode to check closure checklist (L515/#247)  [instance-only per L600]
  - Improved error messages with gate name truncation

- **AGET Lifecycle SOPs renamed to active verb pattern** (AI-1, SOP_SOP_CREATION.md):
  - `SOP_agent_instance_creation.md` → `SOP_aget_create.md`
  - `SOP_instance_migration_v3.md` → `SOP_aget_migrate.md`
  - Pattern: `SOP_aget_{active_verb}.md` per naming convention
  - 50 files updated across 7 repositories

### Learnings Captured

- L554: Hierarchical PROJECT_PLAN gap — SOP needs top-level vs contributing guidance  [instance-only per L600]
- L555-candidate: KB review should precede governance artifact creation  [instance-only per L600]
- L556-candidate: V-tests validate presence, not correctness  [instance-only per L600]

### Metrics

| Metric | Value |
|--------|-------|
| GO issues resolved | 10 |
| Implementations completed | 12 |
| Specs updated | 4 |
| New SOPs | 4 |
| New templates | 3 |
| Templates with sops/ + SOP files | 12/12 |
| Session tests passing | 38 |

### Migration Guide

**For Existing Agents**:
1. Update version files: Bump `.aget/version.json` to 3.4.0
2. Create sops/ directory: If not present, create `sops/` and add at least one SOP file (e.g., `SOP_escalation.md`)
3. Review session scripts: Verify wake_up.py and wind_down.py compatibility

**Breaking Changes**: None. v3.4.0 is backward compatible with v3.3.x agents.

### Contributing Projects

This release aggregates work from six completed PROJECT_PLANs:
1. PROJECT_PLAN_session_skills_maturity_v1.0.md
2. PROJECT_PLAN_conformance_rubric_v3.4_v1.0.md
3. PROJECT_PLAN_spec_first_documentation_v1.0.md
4. PROJECT_PLAN_version_scope_standardization_v1.0.md
5. PROJECT_PLAN_project_plan_creation_sop_v1.0.md
6. PROJECT_PLAN_sop_creation_sop_v1.0.md

---

## [3.3.0] - 2026-01-10

**Theme**: Shell Integration + Executable Knowledge Ontology

### Added

- **Shell Integration** (L452):  [instance-only per L600]
  - `shell/aget.zsh`: Main shell orchestration file
  - `shell/profiles.zsh`: CLI backend profiles (Claude Code, Cursor, Aider, Gemini, Windsurf)
  - `scripts/generate_agents_zsh.py`: Alias generator for agent directories
  - `docs/SHELL_INTEGRATION.md`: User documentation

- **Executable Knowledge Ontology** (L451, L453):  [instance-only per L600]
  - `AGET_EXECUTABLE_KNOWLEDGE_SPEC.md`: EKO axis definitions (Determinism, Reusability, Abstraction)
  - `AGET_EVOLUTION_SPEC.md`: Evolution entry type standardization (L-doc, D-doc, DISC-doc)
  - VOCABULARY_SPEC Part 5: EKO terms

- **Ontology-Driven Agent Creation** (L481, L482):  [instance-only per L600]
  - `SOP_aget_create.md`: SKOS+EARS-grounded creation process
  - `scripts/generate_template_ontology.py`: Template vocabulary generator
  - `validation/validate_ontology_compliance.py`: SKOS compliance validator
  - 12 template vocabularies: All templates now have specs/*_VOCABULARY.md
  - R-REL-015: "We do not leave published templates behind"

- **Session Governance**:
  - `SOP_point_upgrade.md`: Formal point upgrade procedure (L444 conformance)  [instance-only per L600]
  - CAP-PP-012: Artifact comprehensibility (merged #67)

- **18 New L-docs**: L451-L453, L460-L468, L478-L482, L500-L503  [instance-only per L600]

### Changed

- **Template Conformance**: All 12 templates now have SKOS-compliant vocabularies
- **SOP_release_process.md**: v1.10 with R-REL-015 (template conformance)
- **AGET_PORTABILITY_SPEC.md**: Shell integration references
- **AGET_COMPATIBILITY_SPEC.md**: Zsh/bash support section

### Fixed

- **Version Documentation Gap**: README.md and VERSION_HISTORY.md updated (were stale at v2.11.0)

### Notes

This release establishes the foundation for ontology-driven agent creation, where template
vocabularies DRIVE instance behavior (L481). All published templates now conform to  [instance-only per L600]
SKOS vocabulary standards, enabling fleet supervisors to validate instance compliance.

---

## [3.2.1] - 2026-01-04

**Theme**: Version Inventory Coherence (L444 Remediation)  [instance-only per L600]

### Fixed

- **Version Consistency**: All version-bearing files now consistent across 7 repos
  - AGENTS.md headers updated (were stuck at v3.1.0)
  - manifest.yaml version fields updated (were stuck at 3.1.0)
  - version.json files updated to 3.2.1
- **Coherence Testing**: Added V7.1.4, V7.1.5, V7.1.6 tests to Gate 7
  - V7.1.4: AGENTS.md header version check
  - V7.1.5: manifest.yaml version field check
  - V7.1.6: No stale version references check
- **SOP Update**: `SOP_release_process.md` v1.7 with L444 coherence testing section  [instance-only per L600]

### Added

- **L444**: Version Inventory Coherence Requirement learning document  [instance-only per L600]
- **R-REL-VER-001**: New requirement for version inventory coherence

### Notes

This patch release addresses version inconsistencies discovered during v3.2.0 retrospective.
Root cause: Gate 7 checklist verified version.json but not AGENTS.md or manifest.yaml.

See L444 for full 5-why analysis and process improvements.  [instance-only per L600]

---

## [3.2.0] - 2026-01-04

**Theme**: Specification Architecture

### Added

- **7 New Specifications**: Comprehensive governance coverage
  - `AGET_TESTING_SPEC.md`: Contract testing requirements (CAP-TEST-001 to CAP-TEST-009)
  - `AGET_RELEASE_SPEC.md`: Release process requirements (CAP-REL-001 to CAP-REL-006)
  - `AGET_DOCUMENTATION_SPEC.md`: Documentation standards (CAP-DOC-001 to CAP-DOC-007)
  - `AGET_ORGANIZATION_SPEC.md`: Organization artifacts (CAP-ORG-001 to CAP-ORG-003)
  - `AGET_ERROR_SPEC.md`: Error handling patterns (CAP-ERR-001 to CAP-ERR-005)
  - `AGET_SECURITY_SPEC.md`: Security requirements (CAP-SEC-001 to CAP-SEC-004)
  - `AGET_PROJECT_PLAN_SPEC.md`: Planning standards (CAP-PP-001 to CAP-PP-011)
- **Naming Convention Expansion**: 4 → 10 categories (L439)  [instance-only per L600]
  - Category F: Standard Open-Source Files (README, LICENSE, CHANGELOG, CONTRIBUTING)
  - Category G: Requirement Documents (R-XXX-NNN pattern)
  - Category H: Change Proposals (CP-NNN_name.md)
  - Category I: Protocol Documents (*_PROTOCOL.md)
  - Category J: Checklists (*_CHECKLIST.md)
  - Domain Codes Registry (17 registered: REL, TPL, WAKE, etc.)
  - Git Branch Naming (feature/, fix/, docs/, etc.)
  - Git Tag Naming (vM.m.p[-prerelease])
- **Specification Index System**:
  - `INDEX.md`: Master list of 30 specifications
  - `REQUIREMENTS_MATRIX.md`: 78 CAP requirements cross-referenced
- **Standardized Spec Headers**:
  - YAML frontmatter with version, status, domain, dependencies
  - `migrate_spec_headers.py` migration script
  - JSON Schema for header validation
- **6 New Validators** (L433 remediation):  [instance-only per L600]
  - `validate_license_compliance.py`: Apache 2.0 verification (CAP-LIC-001 to CAP-LIC-004)
  - `validate_agent_structure.py`: 5D directory validation (CAP-STRUCT-001 to CAP-STRUCT-005)
  - `validate_release_gate.py`: Release gate enforcement (R-REL-006, L440)  [instance-only per L600]
  - `validate_ldoc_index.py`: L-doc index consistency (CAP-MEMORY-008)
  - `validate_sop_compliance.py`: SOP format validation (CAP-SOP-001 to CAP-SOP-004)
  - `validate_homepage_messaging.py`: Homepage validation (CAP-ORG-001, CAP-ORG-002)

### Changed

- Validator inventory: 24 → 30 implemented
- Spec count: 23 → 30 (7 new specifications)
- Naming categories: 4 → 10 (6 new categories)
- All specs now have standardized headers with version, status, dependencies
- VALIDATOR_INVENTORY.md now tracks theater ratio (33% → target <10%)

### Documentation

- INDEX.md: Central specification registry
- REQUIREMENTS_MATRIX.md: Complete CAP requirement inventory
- PROJECT_PLAN_TEMPLATE.md: Standard planning format with V-tests (CAP-PP-011)

### Learnings Captured

- L439: Standard Open-Source Files as Category F  [instance-only per L600]
- L440: "A checkbox is not a verification. A passing test is."  [instance-only per L600]
- L441: Theater Ratio as Specification Quality Metric  [instance-only per L600]
- L442: Declarative vs Executable Verification  [instance-only per L600]
- L443: Theater Ratio Paradox (new specs increase denominator)  [instance-only per L600]

### Tests

30 validators implemented (theater ratio 33%, target <10% for v3.3.0)

---

## [3.1.0] - 2026-01-04

### Added

- **Complete Session Lifecycle**: Full session protocol suite in all templates
  - `wake_up.py`: Session initialization (R-WAKE-001 to R-WAKE-007)
  - `aget_housekeeping_protocol.py`: Mid-session sanity checks (R-SANITY-001 to R-SANITY-007)
  - `wind_down.py`: Session close with sanity gate (R-WIND-001 to R-WIND-006)
- **L-Doc Format v2**: Structured metadata for cross-agent pattern discovery
  - `format_version: "2.0"` header
  - `migrate_ldoc_to_v2.py` migration tool
  - JSON Schema validation (`schemas/ldoc_v2.json`)
- **Fleet Governance Patterns**:
  - Role Boundary Awareness (PATTERN_role_boundary_awareness.md)
  - Version Sync (`version_sync.py`) for fleet-wide consistency
  - Issue Routing via `.aget/config/issue_routing.yaml`
- **Workflow Automation Scripts**:
  - `learning_to_enhancement.py`: L-doc → GitHub Issue workflow
  - `cascade_ldoc_to_sop.py`: L-doc → SOP cascade automation
  - `validate_cli_settings.py`: CLI settings hygiene validation
  - `validate_fleet.py`: Fleet-wide validation
- **CLI Settings Standard**: R-CLI-001 to R-CLI-005 for Claude Code, Codex, Cursor
- **Organization Artifact Specification**: CAP-ORG-001 (homepage update requirements)

### Changed

- All scripts support `--json` output for cross-CLI automation
- All scripts implement L038 (Agent-Agnostic) and L021 (Verify-Before-Modify)  [instance-only per L600]
- AGET_FRAMEWORK_SPEC updated to 10 capability domains (added CAP-ORG)
- RELEASE_VERIFICATION_CHECKLIST updated with Gate 7 (Organization Artifacts)

### Fixed

- #14: Naming validator index file exception
- #15: Migration guide documentation enhancements
- #16: AGENTS.md Project Context version in migration script

---

## [3.0.0] - 2025-12-28

### Added

- **5D Composition Architecture**: Structured directories for agent composition
  - `.aget/persona/` - Agent identity and behavioral characteristics
  - `.aget/memory/` - Session handoffs and persistent state
  - `.aget/reasoning/` - Decision frameworks and policies
  - `.aget/skills/` - Patterns, SOPs, and automation scripts
  - `.aget/context/` - Environmental and domain information
- **Instance Type System**: Clear distinction between `aget` (advisory), `AGET` (action-taking), and `template`
- **Template Field**: Replaces `roles` array with single `template` field in version.json
- **Archetype Field**: High-level classification (supervisor, worker, advisor, consultant, developer, spec-engineer)
- **v3.0 Contract Tests**: Updated test suite supporting 5D architecture and v3.0 schema

### Changed

- **BREAKING**: `roles` field removed from version.json (use `template` and `instance_type`)
- **BREAKING**: `persona` field in version.json now optional (use `.aget/persona/` directory)
- Manifest version: 2.0 → 3.0
- All 6 templates migrated to 5D architecture

### Migration Guide

Agents upgrading from v2.x:
1. Add `template` field (archetype name)
2. Add `instance_type` field (`aget`, `AGET`, or `template`)
3. Add `archetype` field (high-level classification)
4. Create `.aget/persona/`, `.aget/memory/`, `.aget/reasoning/`, `.aget/skills/`, `.aget/context/` directories
5. Remove `roles` field (deprecated)
6. See `docs/FLEET_MIGRATION_GUIDE.md` for detailed steps

---

## [2.12.0] - 2025-12-25

### Added

- **Capability Architecture Completion**: Full implementation of capability composition system
- **CAPABILITY_SPEC_v1.0_SCHEMA.yaml**: JSON Schema for capability specifications
- **TEMPLATE_MANIFEST_v1.0_SCHEMA.yaml**: JSON Schema for agent composition declarations
- **COMPOSITION_SPEC_v1.0.md**: DAG composition rules, conflict detection, resolution strategies
- **5 Capability Specifications**:
  - `memory-management` (upgraded from DRAFT to v1.0 APPROVED)
  - `domain-knowledge` (P0 - 12+ agent demand)
  - `structured-outputs` (P0 - 8+ agent demand)
  - `collaboration` (P1 - multi-agent coordination)
  - `org-kb` (P1 - 5W+H organizational knowledge base)
- **3 Validators**:
  - `validate_capability_spec.py`: Schema compliance for capability specs
  - `validate_template_manifest.py`: Manifest structure validation
  - `validate_composition.py`: DAG conflict detection, prerequisite checking
- **80 Capability Architecture Tests**: Comprehensive test suite across 5 test files
- **3 Practitioner Guides**:
  - `CAPABILITY_AUTHOR_GUIDE.md`: How to create new capabilities (521 lines)
  - `COMPOSITION_GUIDE.md`: How to compose agents from capabilities (556 lines)
  - `FLEET_MIGRATION_GUIDE.md`: Step-by-step migration procedures (618 lines)

### Changed

- Architecture completeness: 65% → 100% (all 5 layers complete)
- Fleet Migration Phase 2 prerequisites: All satisfied

### Documentation

- Pattern documents for structured-outputs and collaboration capabilities
- Cross-referenced documentation ecosystem for practitioners
- Pilot agent inventory with version gap analysis

### Tests

80 passing (capability architecture tests)
- test_capability_spec_validation.py (18 tests)
- test_template_manifest_validation.py (14 tests)
- test_composition_validation.py (16 tests)
- test_agent_type_instantiation.py (12 tests)
- test_capability_contracts.py (20 tests)

### Fleet Migration Enablement

- 5 pilot agents documented with projected compositions
- Migration complexity ranking established
- Recommended migration order (3 waves)

---

## [2.11.0] - 2025-12-24

### Added

- **Memory Architecture (L335)**: 6-layer information model for persistent knowledge across sessions  [instance-only per L600]
- **L352 Traceability Pattern**: Five-tier requirement-to-test traceability system  [instance-only per L600]
- **R-PUB-001 Public Release Completeness**: 8 requirements ensuring user-visible release quality
- **Post-release validation automation**: `post_release_validation.py` automates 6/8 completeness checks
- **Public framework governance documentation**: VERSIONING.md, RELEASES.md, UPGRADING.md, COMMUNICATION_STANDARDS.md
- **Configurable wake-up output**: 7 customizable sections for agent session initialization
- **Version migration protocol (R-REL-006)**: Framework manager self-updates before releasing public repos
- **Process Specification Pilot (v0.1)**: YAML-based workflow definitions
- **Vocabulary Standard**: SKOS-based terminology management
- **CLI Settings templates**: Pre-configured settings for Claude Code, Codex, Gemini, Cursor

### Changed

- Enhanced RELEASE_PROCESS.md with Phase 4 (Post-Release Validation) and Phase 5 (Public Announcement)
- Framework Specification pattern now supports cumulative + delta views
- SESSION_HANDOFF protocol updated with memory layer integration

### Documentation

- Created VERSION_HISTORY.md: Complete version timeline with transparent gap acknowledgment
- Created PUBLIC_RELEASE_VALIDATION.md: Manual validation checklist for releases
- Enhanced organizational homepage with current version consistency
- Added 40 contract tests with full L352 traceability matrix  [instance-only per L600]

### Learnings Captured

- L353: Pattern Efficiency Scaling  [instance-only per L600]
- L354: Meta-Testing Viability  [instance-only per L600]
- L355: Pilot-Phase Flexibility  [instance-only per L600]
- L356: User-Driven Enhancement Value  [instance-only per L600]
- L357: Version Migration as Explicit Deliverable  [instance-only per L600]
- L358: Tags ≠ Releases on GitHub (process gap discovery)  [instance-only per L600]

### Tests

80 passing (40 L352 pattern tests + 40 baseline tests)  [instance-only per L600]

**See**: [AGET_DELTA_v2.11.md](specs/deltas/AGET_DELTA_v2.11.md) for complete technical specification

---

## [2.10.0] - 2025-12-24

**Note**: Work completed 2025-12-13. GitHub Release created retroactively on 2025-12-24 as part of public framework governance enhancement.

### Added

- **Capability Composition Architecture**: Framework for defining agent types via capability combinations
- **6 Agent Type Specifications**: Data Science, Executive Advisor, Specification Owner, Software Development Owner, Knowledge Owner, Research Advisor
- **Executive Advisor Pattern**: 5W+H knowledge base architecture for strategic guidance
- **Domain Specialist Pattern**: Structured output formats for specialized agent responses
- **Theoretical Grounding Protocol (L332)**: Maps framework concepts to established theory (BDI, Actor Model, Extended Mind, Cybernetics)  [instance-only per L600]
- **Knowledge Inheritance Requirement (L330)**: Framework owners must inherit institutional knowledge  [instance-only per L600]

### Changed

- Agent type model: From rigid categories to capability-based composition
- Pattern documentation: Structured format with theoretical foundations

### Learnings Captured

- L330: Knowledge Inheritance Requirement  [instance-only per L600]
- L331: Theoretical Foundations of Agency  [instance-only per L600]
- L332: Theoretical Grounding Protocol  [instance-only per L600]

### Tests

39 passing (contract tests for capability specifications)

**See**: specs/deltas/AGET_DELTA_v2.10.md for complete changes (if available)

---

## [2.9.0] - 2025-11-24

**Note**: Partial release - only advisor-family templates received GitHub Releases. Core aget/ repository did not have a public release.

### Added

- **Session location standard**: sessions/ directory at repository root
- **Session metadata standard**: YAML frontmatter for session files
- **Memory layer for advisors**: .memory/ directory structure for knowledge persistence
- **5-layer knowledge architecture**: Organized knowledge storage system
- **Fleet-wide migration protocol**: Coordinated version updates across 28 agents

### Changed

- Information storage standardized across all agent types
- Memory patterns enhanced for long-running advisory sessions

**See**: Template-specific releases for detailed changes:
- [template-advisor-aget v2.9.0](https://github.com/aget-framework/template-advisor-aget/releases/tag/v2.9.0)
- [template-consultant-aget v2.9.0](https://github.com/aget-framework/template-consultant-aget/releases/tag/v2.9.0)
- [template-developer-aget v2.9.0](https://github.com/aget-framework/template-developer-aget/releases/tag/v2.9.0)
- [template-spec-engineer-aget v2.9.0](https://github.com/aget-framework/template-spec-engineer-aget/releases/tag/v2.9.0)

---

## [2.8.0] - 2025-11-10

**Note**: Core aget/ repository did not have a public GitHub Release for this version.

### Added

- **Friction Reduction Enhancements**: Streamlined workflows for common agent tasks
- **Enhancement Filing Protocol**: Standardized process for proposing framework improvements
- **Planning Framework**: PROJECT_PLAN templates for multi-gate work

### Changed

- Agent configuration templates simplified
- Documentation structure reorganized for better discoverability

**See**: Template-specific releases for detailed changes (all 6 templates released)

---

## [2.7.0] - 2025-10-13

**Note**: Core aget/ repository did not have a public GitHub Release for this version.

### Added

- **Portfolio Governance**: Multi-portfolio agent management (main, ccb, workco, etc.)
- **Portfolio Field**: `portfolio` metadata in .aget/version.json
- **Naming Conventions**: Standardized agent naming patterns (domain-specialty-type format)
- **Advisor Personas**: Enhanced role definitions for advisor-type agents

### Changed

- Agent identity model expanded to include portfolio affiliation
- Scope boundaries clarified across portfolios

**See**: Template-specific releases for detailed changes

---

## [2.6.0] - 2025-10-12

**Note**: Version documented in internal migration history but no public GitHub Releases created (known gap).

### Added

- **Size Management**: Mechanisms for handling large knowledge bases

### Known Gap

This version exists in migration_history but was never published as a GitHub Release. Work transitioned directly to v2.7.0.

---

## [2.5.0] - 2025-10-04

**Note**: Partial release - only some templates (template-worker-aget confirmed).

### Added

- **Validation Framework**: Contract testing infrastructure
- **Quality Gates**: Validation checkpoints for agent compliance

**See**: [template-worker-aget v2.5.0](https://github.com/aget-framework/template-worker-aget/releases/tag/v2.5.0) for details

---

## [2.4.0] - 2025-10-03

### Added

- **Clarity Enhancements**: Improved documentation and agent instructions
- **Configuration Refinements**: Streamlined AGENTS.md templates

**See**: [template-worker-aget v2.4.0](https://github.com/aget-framework/template-worker-aget/releases/tag/v2.4.0)

---

## [2.3.0] - 2025-10-02

### Added

- **Collaboration Infrastructure**: Patterns for human-AI collaboration
- **Session Protocols**: Standards for agent session management

**See**: [template-worker-aget v2.3.0](https://github.com/aget-framework/template-worker-aget/releases/tag/v2.3.0)

---

## [2.2.0] - 2025-09-30

### Added

- **Intelligence-Enabled Specification Creation**: AI-assisted spec generation
- **Specification Templates**: Structured formats for requirement documentation

**See**: [template-worker-aget v2.2.0](https://github.com/aget-framework/template-worker-aget/releases/tag/v2.2.0)

---

## [2.1.0] - 2025-09-29

**The Ownership Release**

### Added

- **Ownership Model**: Agents manage specific repositories and artifacts
- **Responsibility Boundaries**: Clear definitions of agent scope and authority

**See**: [template-worker-aget v2.1.0](https://github.com/aget-framework/template-worker-aget/releases/tag/v2.1.0)

---

## [2.0.0] - 2025-09-XX

**Initial Public Framework Architecture**

### Added

- **AGET Framework Core**: CLI-based human-AI collaborative coding framework
- **Template System**: Reusable agent configurations (Worker, Advisor, Supervisor)
- **AGENTS.md Standard**: Configuration file format for CLI tool integration
- **Contract Testing**: Validation system for agent compliance
- **.aget/ Directory Structure**: Standard configuration and pattern storage

### Core Principles Established

- AGET = Configuration & Lifecycle Management (not a runtime)
- Conversation layer only (no code execution)
- Optimizes for human-AI collaboration quality

**Breaking Changes from v1.x**

- Complete architecture redesign
- New configuration format
- Template-based approach replaces ad-hoc configurations

---

## Historical Version Gaps

**Transparency Note**: The aget/ core repository had incomplete GitHub Release history prior to v2.11.0 due to the private→public transition process focusing on content visibility without establishing comprehensive public release discipline.

**Gaps**:
- v2.5.0 through v2.9.0: No aget/ releases (template releases exist)
- v2.6.0: No releases for any repository
- v2.9.0: Partial release (4/7 templates)

**Root Cause**: Internal versioning (version.json) was maintained rigorously, but public releases (GitHub Releases) were inconsistent.

**Resolution**: v2.11.0 established public framework governance with R-PUB-001 requirements and automated post-release validation.

**See**: [VERSION_HISTORY.md](docs/VERSION_HISTORY.md) for complete gap analysis

---

## Version Support

**Latest Stable**: v3.15.0
**Support Window**: Latest release receives full support (bug fixes, enhancements)
**Previous Minor** (v3.14.x): Security fixes only
**Older Versions**: No active support (upgrade recommended)

---

## How to Upgrade

See [UPGRADING.md](docs/UPGRADING.md) for version-specific migration guides and safe upgrade procedures.

---

## Links

- [GitHub Releases](https://github.com/aget-framework/aget/releases)
- [Version History](docs/VERSION_HISTORY.md)
- [Versioning Policy](docs/VERSIONING.md)
- [Release Process](docs/RELEASES.md)
- [Upgrade Guide](docs/UPGRADING.md)
- [Issue Tracker](https://github.com/aget-framework/aget/issues)

---

*CHANGELOG.md - Updated 2026-03-01*
*Maintained by: aget-framework maintainers*
