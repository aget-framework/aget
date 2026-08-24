# AGET Framework — Deprecation Registry

**Status**: PREPARED CANDIDATE — not published. Target `aget-framework/aget` → `governance/DEPRECATIONS.md`.

**Scope**: deprecations a **public consumer of the AGET framework** can act on. A row is here only if the
deprecation changes something you do — migrate a call, re-cite a path, stop relying on a flag. Deprecations
that bind only the maintainer's own installation are deliberately **excluded**; see *What is not here*.

Every row carries the five `R-DEP-010` fields: **what** is deprecated, **why**, its **replacement**, a
**removal timeline**, and how to **detect** it. A removal timeline nobody can detect is decorative metadata,
so the detection instruction sits in the Status column and is not optional.

**Grace policy** (`R-DEP-011`): non-breaking deprecations carry a two-minor grace window — marked in vN,
carried in vN+1, removable in vN+2. Breaking changes wait for the next major.

---

## Active — act on these

| Item | What is deprecated, and why | Replacement | Earliest removal | Status and detection |
|---|---|---|---|---|
| **DEP-BASENAME-VPP-001** | The script **name** `scripts/validate_project_plan.py` — the name only, not the behaviour. The code is unchanged and now lives at `scripts/validate_execution_authorization.py`. **Why**: the name asserted a predicate the script never had. It checks whether *any* governance artifact exists — its subject is the *action* — and it never validated a plan. A different, larger file, `verification/validate_project_plan.py`, *does* validate plans; its subject is the *document*. One basename, two referents, opposite questions. The collision was cashed as six false "safe to proceed" reports on 2026-07-26 before it was classified. | **Authorization gate** → `scripts/validate_execution_authorization.py`. **Plan conformance** → `verification/validate_project_plan.py <path> --strict`. A delegating shim remains at the old name for the grace window: same stdout, same exit codes, `DeprecationWarning` on stderr. | **v3.34.0** — marked v3.32 → carried v3.33 → shim removable v3.34 (`R-DEP-011`, non-breaking two-minor grace) | **Active — grace window open.** **Detection**: `rg -n 'validate_project_plan' .` in your own repository. A hit that names the basename **without a directory** is ambiguous between the two files in the Replacement column regardless of which was meant, and should be re-cited with its path. A hit that invokes `scripts/validate_project_plan.py` is a live call site on the deprecated name and will stop working at v3.34.0. |

## Closed — history, no action required

Kept because the artifacts they describe are still visible in public distributions, so a reader can still
encounter the old name and needs to know its disposition.

| Item | What was deprecated, and why | Replacement | Earliest removal | Status and detection |
|---|---|---|---|---|
| **DEP-FIX-FLAG-001** | The `/aget-check-health --fix` flag. **Why**: documented across skill files and a skill specification, never implemented — a remediation promise with nothing behind it. | `/aget-enhance-health` (SKILL-049), the canonical `check → enhance` pipeline per `DESIGN_DIRECTION` §Principle 9. | v3.15.0 — immediate; the `R-DEP-011` grace window is for artifacts that worked, and this one never did | **Removed in v3.15.0.** **Detection**: `rg -n '\-\-fix' .aget/specs/skills/ .claude/skills/` — the flag no longer exists in any code path. Statements describing it may still be readable in older skill specifications; they document a flag that was never functional. |
| **DEP-REQ-HOM-F-006** | Requirement REQ-HOM-F-006, *Content Preservation During Rewrites*. **Why**: it defended an inline-preservation pattern that the current homepage architecture no longer uses, so the requirement protected a non-canonical layout. | No successor requirement. Preservation is now structural rather than stated: a consolidated release-notes archive, per-version GitHub Release bodies, and `CHANGELOG.md`, all linked from the "Earlier Releases" section. | v3.20.0 — `R-DEP-011` non-breaking two-minor grace from v3.18.0 | **Retired in v3.18.0.** **Detection**: `rg -n 'REQ-HOM-F-006' requirements/` — the requirement block is retained in `requirements/REQ-HOM_homepage_quality.md` with `status: retired` and a five-field retirement record. Cite it only as history. |

---

## Keeping this registry true — the maintenance loop

A public registry derived from a private one, with nothing binding them, decays silently. This is the
binding. It is deliberately small enough to actually run.

| | |
|---|---|
| **Owner** | The framework release agent — the same role that executes the release process and owns `sops/SOP_release_process.md`. Ownership is a role, not a person, so it survives handoffs. |
| **Trigger** | Any change to the source registry, **and** every release. Whichever comes first. A deprecation is *created* by a release and *discharged* by a release, so the release is the only event guaranteed to catch both. |
| **Review** | Run the checker against this file: `python3 scripts/check_deprecation_removals.py --registry governance/DEPRECATIONS.md --json`. It returns `PASS` (every row inside its grace window), `FAIL` (a removal version has passed with the row still open), or `UNAVAILABLE` (it could not read the registry — never a silent pass). Then re-apply the consumer-actionability test to any row added to the source since the last pass: does it change what a consumer does? |
| **Consequence** | The check runs in the release gate battery. `FAIL` means the release ships an unactuated rule: either remove the artifact and mark the row, or re-baseline the removal version **with a stated reason**. A row may not simply be carried again in silence — that is the failure this file exists to make visible. `UNAVAILABLE` blocks the same way `FAIL` does; an unread registry is not a clean one. |
| **Cadence** | Per release. Between releases the trigger is event-driven, not scheduled — a calendar reminder over an unchanged file produces noise and trains the reader to skip it. |
| **Falsifier** | If this file's row set ever diverges from the source registry's public-scoped rows and neither the checker nor the release gate says so, the loop is not working, whatever the process document claims. |

## What is not here, and why

**Rows that bind only the maintainer's own installation are excluded.** The source registry governs an
internal governance tree and carries entries a consumer cannot possess, cannot detect, and cannot act on.
Publishing them would present noise as policy: the reader cannot tell them apart from rows that do bind.
Two of the source registry's five rows were excluded on this basis:

- a retired clause in an internal ontology definition — the file is not distributed;
- a deprecated shell script that **was never in any public distribution**. Verified at source rather than
  assumed: the path is absent from the release tag that announced the deprecation, absent from the current
  release tag, and absent from every commit on every public branch, while a control file checked with the
  identical command at the identical commits was found. Its replacement already shipped, and always had.
  There is nothing for a consumer to migrate from.

**This is a split, not a copy.** It is derived from a larger internal registry and re-scoped, so it does not
track that file automatically. That obligation is the maintenance loop above, which is why the loop names a
consequence rather than an intention.

**Sanitization applied**: references to internal installation paths were removed or replaced with the public
path of the same artifact. Where an internal measurement supported a claim, the claim was kept and the
measurement's internal detail dropped.

## Known limitations of this draft

1. **Detection commands have not been exercised against a plain consumer checkout.** They were authored
   against the maintainer's corpus, then rewritten to remove tree-specific path exclusions. They should run
   anywhere `rg` is available, but "should" is not "was measured".
2. **The Active row's possession leg is weak, and this is deliberate.** The deprecated script is not itself
   distributed publicly; what *is* public is the other file the name collides with. The row is here because
   the **ambiguity** is a consumer's problem, not because the consumer holds the deprecated file. If a
   reviewer rejects that reasoning, the correct consequence is that this registry has zero Active rows —
   not that a different row should be added to fill the section.
3. **One row's specification text outlived its removal.** `DEP-FIX-FLAG-001` was removed in v3.15.0, but
   statements describing the flag are still readable in a public skill specification. The row is what
   resolves the contradiction for a reader who finds them; the specification itself is not repaired here.

## Why this artifact exists

An announced deprecation its audience cannot see is an overclaim. The Active row above is scheduled for
removal on a published timeline, and until this file ships there is **no public surface on which a consumer
can discover it**. The framework's own removal checker returns `UNAVAILABLE` against a public checkout for
exactly the same reason: the registry it reads does not ship.
