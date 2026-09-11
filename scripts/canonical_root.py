#!/usr/bin/env python3
"""Resolve the canonical checkout the way the conformance harness already does.

WHY THIS EXISTS
---------------
A receiver at v3.32.0 reported three INCOMPLETE rows it could not clear by any action, because
the defect was in the release's own instruments. Two of the three were this:

    SKIPPED tests/test_release_cadence_gap.py: canonical ../aget not present

The receiver's canonical sits at `aget-framework/aget` -- a layout the conformance script
resolves correctly, printing `canonical: .../aget-framework/aget` and running both live controls
against it. **The harness could find canonical and the test could not**, because the test used a
hardcoded relative `../aget` while the script honours `AGET_CANONICAL_ROOT` and `AGET_FLEET_ROOT`.

Two consumers of one fact, disagreeing, is how a receiver gets an INCOMPLETE with no reachable
remedy. There is now one resolver.

DECLARED-BUT-UNRESOLVABLE IS NOT ABSENT
---------------------------------------
The two cases must not collapse:

  * **absent**    -- nothing declared a canonical root and no default exists. A consumer repo
                     need not have one, so a portability skip is legitimate.
  * **declared**  -- someone SET `AGET_CANONICAL_ROOT` (or a fleet root) and it does not
                     resolve. Skipping there hides a misconfiguration behind a green run, so
                     this raises instead.

Resolution order: `AGET_CANONICAL_ROOT` -> `$AGET_FLEET_ROOT/aget` -> `<repo>/../aget`.
"""
from __future__ import annotations

import os
from pathlib import Path


class CanonicalDeclaredButUnresolvable(RuntimeError):
    """A canonical root was named and does not exist. Never silently skipped."""


def resolve(repo: Path | None = None) -> Path | None:
    """Return the canonical checkout, or None when none is declared and no default exists.

    Raises CanonicalDeclaredButUnresolvable when a root WAS declared and does not resolve.
    """
    declared = os.environ.get("AGET_CANONICAL_ROOT")
    if declared:
        p = Path(declared).expanduser()
        if (p / ".git").exists():
            return p
        raise CanonicalDeclaredButUnresolvable(
            f"AGET_CANONICAL_ROOT={declared!r} does not resolve to a git checkout. "
            f"A declared-but-missing root is a misconfiguration, not an absent canonical.")

    fleet = os.environ.get("AGET_FLEET_ROOT")
    if fleet:
        p = Path(fleet).expanduser() / "aget"
        if (p / ".git").exists():
            return p
        raise CanonicalDeclaredButUnresolvable(
            f"AGET_FLEET_ROOT={fleet!r} declares a fleet root whose 'aget' is not a git "
            f"checkout. Declared and missing is not the same as absent.")

    if repo is not None:
        p = repo.parent / "aget"
        if (p / ".git").exists():
            return p
    return None


def resolve_or_skip(repo: Path | None, pytest_mod) -> Path:
    """Test helper: skip ONLY when genuinely absent; a declared-but-missing root fails."""
    found = resolve(repo)          # raises on declared-but-unresolvable
    if found is None:
        pytest_mod.skip("no canonical checkout is declared or discoverable; portability skip. "
                        "Set AGET_CANONICAL_ROOT to run this against a real canonical.")
    return found
