# Position: decomposed agent instructions keep one reachable governance root

**Status**: v3.29 release candidate
**Tracking**: gh#1941, gh#2076, gh#2077, gh#2100

An oversized `AGENTS.md` may be decomposed, but size reduction is not the acceptance predicate. The root
file retains the session protocol, write boundary, gate discipline, and self-amendment control. Nested
files may add local rules; they may not claim to ignore, replace, or disable the root contract.

`AGENTS.md` is the governance instruction surface itself. Edits to `AGENTS.md`, `CLAUDE.md`, client skill
trees, hook configuration, or trust configuration remain governance/authorization-surface changes.
Decomposition never turns those surfaces into silently writable
content. Every client must preserve the operator-visible affirmation boundary applicable to that surface.

`scripts/check_agents_instruction_reach.py` is the v3.29 executable contract. It checks the root size,
load-bearing semantic markers, and nested weakening language. A repository passes only when both size and
reach pass; a shorter but semantically incomplete root fails.
