#!/usr/bin/env python3
"""plan_protected.py — the read-only trial run of the protected write (R-F9, rehearsal 2026-09-30).

    python3 scripts/migration_kit/plan_protected.py --list <list.json> [--only <aget> ...]

Prints, per Aget, what the reviewed protected-write script would do with this list: WOULD-APPLY (with the number of
files and any held ones), REFUSED (with the reason, such as an Aget that changed since the list was prepared), or
SKIPPED. It uses the protected-write script's own planning function, so the two cannot disagree, and it checks that
the list names that script's current bytes.

This file contains no write: it creates no file, writes no receipt, and cannot change a receiver. The rehearsal's
permission classifier refused the protected-write script's own trial run as a change to shared files; this tool is
the trial run, and the protected-write script is run only to write.

Exit codes: 0 every listed Aget would apply or is skipped; 1 at least one Aget is refused; 2 the list names a
different protected-write script than the one present.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import apply_protected as A  # noqa: E402  (its plan_aget() has no side effects; this tool adds none)
import release_target as R  # noqa: E402


def main(argv=None) -> int:
    """Command-line entry point: the read-only trial run of the protected write for a reviewed list."""
    R.require()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", type=Path, required=True)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--run", help="as apply_protected.py --run: a rehearsal's run folder (BIND, R1-T7)")
    a = ap.parse_args(argv)
    doc = json.loads(a.list.read_bytes())
    if doc.get("apply_script_sha256") != A.self_sha():
        print(f"REFUSED: the protected-write script here is {A.self_sha()[:12]}, the reviewed list names "
              f"{str(doc.get('apply_script_sha256'))[:12]}. Re-prepare the list, or restore the reviewed script.")
        return 2
    code = 0
    for entry in doc["agets"]:
        if a.only and entry["aget"] not in a.only:
            continue
        if entry.get("blocked"):
            print(f"{entry['aget']:34s} SKIPPED  {entry['blocked'][:80]}")
            continue
        why = A.bind_refusal(entry, a.run)                  # BIND (R1-T7), as the apply asks it
        ok, why, actions = (False, why, []) if why else A.plan_aget(entry)
        if not ok:
            code = 1
            print(f"{entry['aget']:34s} REFUSED  {why}")
            continue
        held = [o["path"] for o in entry["ops"] if o["op"] in ("hold", "hold-line")]
        print(f"{entry['aget']:34s} {'WOULD-APPLY':12s} {len(actions)} file(s)" + (f"; held {len(held)}" if held else ""))
        for path, _data, post in actions:
            print(f"    {path}  -> {post[:12]}")
    print("plan only: this tool writes nothing.")
    return code


if __name__ == "__main__":
    sys.exit(main())
