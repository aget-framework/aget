#!/usr/bin/env python3
"""
Permission cleanup — companion script to sops/SOP_permission_cleanup.md (v2.0.0).

Implements the SOP keep-filter + dated backup + before/after metrics.
Origin: framework-instance SOP v1.0.1 recipe; script form field-proven at the
fleet-supervisor instance 2026-07-05 (649 -> 104 entries, CRITICAL cleared,
zero healthy-friction controls touched) and adapted to canonical from that copy.

Keep: WebFetch(...), WebSearch*, broad ':*)' patterns without user-specific paths.
Remove: heredocs, specific paths, shell fragments, one-off inline commands.

Healthy-friction note (CAP-FRIC-006): pruned entries re-prompt at next use — that
prompt is a healthy authority-boundary control, not a regression. Deny/ask rules
are never touched.

Usage:
    python3 scripts/permission_cleanup.py --dry-run   # review removals first
    python3 scripts/permission_cleanup.py             # backup + write
"""
import json
import shutil
import sys
from datetime import date
from pathlib import Path

SETTINGS = Path(".claude/settings.local.json")


def should_keep(p: str) -> bool:
    # Non-Bash categories (Skill/Read/Edit/WebFetch/WebSearch/...) are durable
    # governance grants — always preserved. The staleness heuristic applies
    # ONLY within Bash(...) entries. BL-20260706-001: a category-blind version
    # of this filter dropped every Skill(...)/Read(...) grant (supervisor
    # instance 621->98); fix field-proven there 2026-07-06, upstreamed 2026-07-11.
    if not p.startswith("Bash("):
        return True
    if "/Users/" in p or "/home/" in p:
        return False
    if p.endswith(":*)"):
        return True
    return False


def main():
    # Fail loud on anything but the one known flag — an unknown argument
    # (--help included) must never fall through to the mutating default path.
    # Field data 2026-07-11: '--help' silently applied a live cleanup, twice
    # (supervisor seat, then framework seat reproducing the report).
    unknown = [a for a in sys.argv[1:] if a != "--dry-run"]
    if unknown:
        print(f"usage: {sys.argv[0]} [--dry-run]")
        print(f"unknown argument(s): {' '.join(unknown)} — no changes made")
        return 2
    dry = "--dry-run" in sys.argv
    if not SETTINGS.is_file():
        print(f"no {SETTINGS} — nothing to clean")
        return 0
    data = json.loads(SETTINGS.read_text())
    perms = data.get("permissions", {}).get("allow", [])
    if not perms:
        print("allow-list empty — nothing to clean")
        return 0
    size_before = SETTINGS.stat().st_size

    kept = sorted(set(p for p in perms if should_keep(p)))
    removed = [p for p in perms if not should_keep(p)]

    print(f"BEFORE: {len(perms)} entries / {size_before/1024:.1f}KB")
    print(f"AFTER (planned): {len(kept)} entries "
          f"({len(removed)} removed, {len(perms)-len(set(perms))} were dupes)")
    if dry:
        print("DRY: sample removals:")
        for p in removed[:8]:
            print(f"  - {p[:100]}")
        return 0

    bak = SETTINGS.with_suffix(f".json.bak.{date.today().strftime('%Y%m%d')}")
    shutil.copy2(SETTINGS, bak)
    data["permissions"]["allow"] = kept
    SETTINGS.write_text(json.dumps(data, indent=2) + "\n")
    size_after = SETTINGS.stat().st_size
    print(f"WROTE: {len(kept)} entries / {size_after/1024:.1f}KB | backup: {bak.name}")
    print(f"REDUCTION: {100*(1-len(kept)/len(perms)):.0f}% count, "
          f"{100*(1-size_after/size_before):.0f}% size")
    return 0


if __name__ == "__main__":
    sys.exit(main())
