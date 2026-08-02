# Position: decomposed agent instructions keep one reachable governance root

**Status**: v3.29 post-tag correction active on public `main`
**Tracking**: gh#1941, gh#2076, gh#2077, gh#2100, gh#2103

An oversized `AGENTS.md` may be decomposed, but size reduction is not the acceptance predicate. The root
file retains the session protocol, write boundary, gate discipline, and self-amendment control. Nested
files may add local rules; they may not claim to ignore, replace, or disable the root contract.

## Session Protocol

The reachable root retains its Wake Up Protocol or equivalent client bootstrap. A nested instruction file
may extend that protocol for its subtree; it does not replace the root bootstrap.

## Write Scope

The reachable root states its read-only boundaries and scoped write permissions. Decomposition does not
broaden either boundary, and a nested file cannot grant a write that the root withholds.

## Gate Execution Discipline

A Gate without plan update and committed verification evidence is incomplete. Structural Skill Routing
continues to apply after decomposition; moving prose to a nested file does not bypass a required gate or
structural route.

`AGENTS.md` is the governance instruction surface itself. Edits to `AGENTS.md`, `CLAUDE.md`, client skill
trees, hook configuration, or trust configuration remain governance/authorization-surface changes.
Decomposition never turns those surfaces into silently writable
content. Every client must preserve the operator-visible affirmation boundary applicable to that surface.

`scripts/check_agents_instruction_reach.py` is the v3.29 executable textual contract. It checks the root
size, load-bearing semantic markers, and nested weakening language. A repository passes only when both
size and reach pass; a shorter but semantically incomplete root fails. Passing this textual contract does
not establish that the document was included in the governed manifest, received by a seat, loaded by a
client, or followed in ordinary use; those are separate distribution, receipt, and behavior predicates.
