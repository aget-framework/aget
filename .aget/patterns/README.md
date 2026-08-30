# Patterns

Small, reusable executable units that agents invoke directly, grouped by the surface they act on.

## Why this directory exists

Not every reusable control is a top-level script. Some are narrow utilities bound to one external
surface — an issue tracker, a release API, a filesystem convention — and belong grouped with that
surface rather than flattened into `scripts/`.

## What belongs here

- `github/` — controls acting on issues, pull requests, and releases. Content sanitization at the
  private-to-public boundary lives here.
- Further subdirectories per surface, added when a second control for that surface exists. **One file is
  not a category** — do not create a subdirectory for a single script.

## Contract

A pattern is executable, has a `--check` or equivalent read-only mode, and **fails closed**. A control
that exits zero when it cannot evaluate its subject is worse than absent: it reports success for a check
that never ran. If a pattern cannot reach what it is meant to inspect, it must say so and exit non-zero.
