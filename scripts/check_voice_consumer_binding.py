#!/usr/bin/env python3
"""Verify that a downstream consumer actually CITES AND CONSUMES the voice artifact.

WHY THIS EXISTS
---------------
`INIT-VOICE-FRAMEWORK` EC-2 reads: *"Voice governance artifacts cited by >=1 downstream
consumer (template or agent) -- verify: consumer reference."* That verification was prose, and
prose could not tell three very different situations apart:

  * 13 templates each carry an identical copy of `knowledge/voice/README.md`. **A copy is not
    a consumer.** Nothing in a scaffold file consumes the scaffold.
  * 13 templates cite `VOICE.md` in `aget-create-briefing`. **That file exists in no template
    and in canonical.** A citation that resolves nowhere is worse than none: it reads as
    adoption and behaves as "if available" -> silently absent.
  * A consumer that names a resolvable artifact and applies its composition order. **Only this
    is adoption.**

This command draws those lines mechanically so EC-2 cannot be closed by the first two.

OUTCOMES
  BOUND     the consumer cites a RESOLVABLE voice artifact and references the composition order
  PARTIAL   cites a resolvable artifact but no composition order (consumes without composing)
  DANGLING  cites a voice artifact path that does not resolve -- counted as a DEFECT, not adoption
  ABSENT    the consumer makes no voice citation

Carrying the scaffold is never, on its own, any of the above: a scaffold file is excluded from
the consumer set, because a document cannot be its own consumer.

USAGE
  python3 scripts/check_voice_consumer_binding.py --root .
  python3 scripts/check_voice_consumer_binding.py --root . --consumer .claude/skills --json

EXIT CODES
  0  at least one BOUND consumer and no DANGLING citation  (EC-2 satisfied)
  1  at least one DANGLING citation
  2  no DANGLING, but no BOUND consumer either  (EC-2 unsatisfied, nothing broken)
  3  inputs unusable
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any

BOUND, PARTIAL, DANGLING, ABSENT = "BOUND", "PARTIAL", "DANGLING", "ABSENT"

# The scaffold itself. A consumer is something OTHER than these.
SCAFFOLD_PATHS = ("knowledge/voice/README.md",)

# A voice citation is a reference to a voice artifact path.
CITATION = re.compile(r"(?:^|[\s`(\[])((?:[\w./-]*)(?:VOICE\.md|knowledge/voice/[\w./-]*))", re.M)

# The composition order the scaffold prescribes (5-layer model).
COMPOSITION_TOKENS = ("Specification", "Evidence Bank", "Enforcement",
                      "Calibration Memory", "Ontology")


def resolves(root: Path, cited: str) -> bool:
    cand = cited.lstrip("./")
    if (root / cand).exists():
        return True
    # a bare filename may legitimately live under the voice directory
    if "/" not in cand and (root / "knowledge" / "voice" / cand).exists():
        return True
    return False


def scan_consumer(path: Path, root: Path) -> dict[str, Any] | None:
    rel = str(path.relative_to(root))
    if rel in SCAFFOLD_PATHS:
        return None  # a document cannot be its own consumer
    try:
        text = path.read_text()
    except (OSError, UnicodeDecodeError):
        return None
    cites = sorted({m.group(1) for m in CITATION.finditer(text)})
    if not cites:
        return None
    unresolved = [c for c in cites if not resolves(root, c)]
    has_order = sum(t in text for t in COMPOSITION_TOKENS) >= 3
    if unresolved:
        outcome, why = DANGLING, f"cites {unresolved}, which resolve nowhere under {root}"
    elif has_order:
        outcome, why = BOUND, None
    else:
        outcome, why = PARTIAL, ("cites a resolvable artifact but references no composition "
                                 "order; consuming without composing")
    return {"consumer": rel, "outcome": outcome, "cites": cites,
            "unresolved": unresolved, "why": why}


def assess(root: Path, subdirs: list[str]) -> dict[str, Any]:
    if not root.is_dir():
        raise NotADirectoryError(root)
    seen: list[dict[str, Any]] = []
    roots = [root / s for s in subdirs] if subdirs else [root]
    for r in roots:
        if not r.exists():
            continue
        for p in sorted(r.rglob("*.md")):
            if not p.is_file():
                continue
            got = scan_consumer(p, root)
            if got:
                seen.append(got)
    counts = {k: sum(1 for s in seen if s["outcome"] == k) for k in (BOUND, PARTIAL, DANGLING)}
    if counts[DANGLING]:
        overall = DANGLING
    elif counts[BOUND]:
        overall = BOUND
    else:
        overall = ABSENT
    return {"consumers": seen, "counts": counts, "overall": overall,
            "ec2_satisfied": overall == BOUND}


def render(res: dict[str, Any]) -> str:
    out = [f"voice consumer binding (INIT-VOICE-FRAMEWORK EC-2): {res['overall']}", ""]
    for c in res["consumers"]:
        out.append(f"  {c['outcome']:<9} {c['consumer']}")
        out.append(f"            cites: {', '.join(c['cites'])}")
        if c.get("why"):
            out.append(f"            -- {c['why']}")
    n = res["counts"]
    out += ["", f"  bound={n[BOUND]}  partial={n[PARTIAL]}  dangling={n[DANGLING]}",
            f"  EC-2 satisfied: {res['ec2_satisfied']}",
            "  A copy of the scaffold is not a consumer; a citation that resolves nowhere is a "
            "defect, not adoption."]
    return "\n".join(out)


def exit_code(res: dict[str, Any]) -> int:
    if res["counts"][DANGLING]:
        return 1
    return 0 if res["counts"][BOUND] else 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Verify voice consumer binding (EC-2).")
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--consumer", action="append", default=None,
                    help="subdirectory to scan; repeatable. Default: whole root")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        res = assess(args.root, args.consumer or [])
    except (OSError, NotADirectoryError) as exc:
        print(f"UNAVAILABLE: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(res, indent=1) if args.json else render(res))
    return exit_code(res)


if __name__ == "__main__":
    sys.exit(main())
