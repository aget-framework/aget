# Git hooks

Repository-managed git hooks, enabled per clone with:

```bash
git config core.hooksPath .githooks
```

## Why this directory exists

Boundary and hygiene controls that must run **at commit time** live here. Nothing else does.

A commit message is a carrier that content scanners do not read. It is also immutable once pushed. That
combination is why a commit-time check belongs in the repository rather than in a contributor's habits —
a control that only fires when someone remembers it is not a control.

## What belongs here

- `commit-msg` — rejects a commit whose message carries content that must not leave, before it can be
  pushed anywhere.
- `pre-commit` — cheap, fast checks that must not be skippable by forgetting.

Hooks here are **repository-scoped**, not agent-scoped. An agent's own conversational tooling belongs
under `.claude/hooks/`, which is a different mechanism with different triggers; do not conflate them.

## Enabling is per-clone, and that is a real limitation

`core.hooksPath` is **local configuration**. It is not inherited by a clone. A hook can therefore be
present in the tree and dead on your machine. Any check that depends on these hooks must verify they are
active rather than assume presence implies enforcement — and should be falsified by switching the hook
off and confirming the check notices.
