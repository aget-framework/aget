#!/usr/bin/env python3
"""C-28-01 independence leg — a release-quality score may not settle on self-assessment.

WHAT THIS CLOSES
----------------
`GOAL-VERIFICATION-INDEPENDENCE` (governance/GOALS.md): no closed-loop-vulnerable
claim is "asserted as settled on self-verification alone - each carries an
independent verification leg (an unconditionally-firing structural gate, or a
headless independent-audit dispatch) before it is treated as authoritative".

The Phase 7.1.5 release-quality score is the archetypal closed loop: the seat that
ships the release scores the release. v3.27.0's score says so in prose --

    "Provenance caveat (self-audit, not independent): this score is producer-run
     -- the seat that shipped v3.27.0 scoring its own release."

-- and prose is not a control. An honest caveat that blocks nothing is the L671
decorative-metadata shape. This script makes the caveat structural: a score either
declares a resolvable independent leg, or it does not pass.

VERIFIER QUALITY -- THREE GAPS CLOSED 2026-07-26 (C-28-01 residue)
------------------------------------------------------------------
The first version verified that a leg was DECLARED and that its evidence EXISTED.
Three ways past it were left open, each now closed by a check rather than a caution:

 1. `verifier=` was an arbitrary string. Any value that was not this seat's own name
    passed -- including a seat that does not exist. Now resolved against FLEET_STATE
    via `scripts/fleet_scope.py --list`, the authoritative instrument (never a path
    glob -- L1220 §Count).

 2. `evidence=` resolved on EXISTENCE, so an artifact containing only a verdict
    passed. This cycle produced that exact artifact: the Gate-2 Critic journalled
    `material_count: 11`, `verdict: AMEND-FIRST` and *no findings text*, and seven of
    eleven findings died with the subagent's transcript. `v328-shipday:R10`'s standard
    -- a verdict without its findings is not a landed leg -- is now enforced.

 3. Nothing recorded that the reply was held under test. A headless verifier is a
    domain-generalist that confabulates citations (L1058/L718), so `v328-shipday:R41`
    holds its reply CLAIMS-UNDER-TEST until re-verified at source. Now required.

WHAT THIS STILL DOES *NOT* CLOSE (stated, not hidden)
-----------------------------------------------------
A registered seat can still be a cooperative one, and findings prose can still be
thin. This makes the leg *falsifiable* -- a named seat that does not exist, an
evidence artifact with no findings, or an unrecorded claims-under-test step now all
fail -- but it does not measure adversarial rigour. That remains owed (L671), and it
is a judgement a script cannot make.

Exit 0 = pass | 1 = fail | 2 = usage/not-found
"""
from __future__ import annotations

import argparse
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# The declaration block a score must carry. Deliberately readable-in-markdown
# rather than YAML frontmatter: these files are principal-read documents first.
BLOCK_RE = re.compile(
    r"^\s*[-*]?\s*\*\*independence\*\*\s*:\s*(?P<body>.+?)(?=\n\s*\n|\Z)",
    re.IGNORECASE | re.MULTILINE | re.DOTALL,
)
FIELD_RE = re.compile(r"(?P<k>type|verifier|evidence|date)\s*=\s*(?P<v>[^;|\n]+)", re.IGNORECASE)

VALID_TYPES = {"headless-audit", "peer-seat-review", "structural-gate"}


def _producer_seat() -> str:
    """This seat's registered identity. Resolved from the repo, not asserted."""
    try:
        import json
        return json.loads((ROOT / ".aget" / "version.json").read_text()).get(
            "agent_name", ROOT.name)
    except Exception:
        return ROOT.name


def _evidence_resolves(ev: str) -> tuple[bool, str]:
    """Evidence must point at something that exists. Three accepted forms."""
    ev = ev.strip().strip("`")
    if re.fullmatch(r"(?:[\w./-]+)?#\d+", ev):                    # gh issue ref
        repo, _, num = ev.rpartition("#")
        repo = repo or "gmelli/aget-aget"
        r = subprocess.run(["gh", "issue", "view", num, "-R", repo, "--json", "number"],
                           capture_output=True, text=True)
        return (r.returncode == 0, f"gh issue {repo}#{num}"
                + ("" if r.returncode == 0 else " NOT FOUND"))
    if ev.startswith("http://") or ev.startswith("https://"):
        return True, f"URL {ev} (existence not checked -- network claim)"
    p = (ROOT / ev)
    return (p.exists(), f"path {ev}" + ("" if p.exists() else " NOT FOUND"))


def _registered_seats() -> set[str] | None:
    """FLEET_STATE seat names. None = resolver unavailable (check degrades to advisory).

    Instrument is `fleet_scope.py --list`, never a `../private-*` glob: a glob omits
    public agents and nested seats, and would silently under-populate the set, turning
    a real seat into a spurious failure.
    """
    r = subprocess.run([sys.executable, str(ROOT / "scripts" / "fleet_scope.py"), "--list"],
                       capture_output=True, text=True)
    if r.returncode != 0 or not r.stdout.strip():
        return None
    seats = set()
    for line in r.stdout.splitlines():
        parts = line.split()
        if len(parts) >= 2 and parts[0] in ("ok", "missing"):
            seats.add(parts[1].strip().lower())
    return seats or None


# A finding is prose attached to an identifier. A bare verdict, a count, or a list of
# bare IDs is not. Requires >=25 chars of text on the marker's line so that "M4" or
# "- M7" alone cannot satisfy it.
FINDING_RE = re.compile(
    r"^\s*(?:[-*|]\s*)?\**(?:M|F|D|finding\s*)\d+\**\s*[-—:|]\s*(?P<text>.{25,})$",
    re.IGNORECASE | re.MULTILINE)
CUT_RE = re.compile(r"claims?[- ]under[- ]test", re.IGNORECASE)


def _evidence_carries_findings(ev: str) -> tuple[bool | None, str]:
    """v328-shipday:R10 — a verdict without its findings is not a landed leg."""
    ev = ev.strip().strip("`")
    if ev.startswith("http"):
        return None, "URL evidence — findings cannot be read locally (unchecked)"
    p = ROOT / ev
    if not p.is_file():
        return None, "evidence is not a local file — findings unchecked"
    hits = FINDING_RE.findall(p.read_text())
    return (len(hits) >= 1,
            f"{len(hits)} finding(s) with prose in {ev}"
            + ("" if hits else " — verdict/count only, no findings text"))


def check(version: str, *, strict: bool = True) -> int:
    score = ROOT / "rubrics" / f"RUBRIC_release_quality_v{version}_score.md"
    if not score.is_file():
        print(f"❌ no score artifact at rubrics/{score.name}")
        print("   The independence leg cannot be checked because nothing was scored.")
        return 2

    text = score.read_text()
    m = BLOCK_RE.search(text)
    if not m:
        print(f"❌ {score.name}: no **independence** declaration")
        print("   GOAL-VERIFICATION-INDEPENDENCE: a producer-run score is not settled")
        print("   evidence. Declare one, e.g.:")
        print("   - **independence**: type=headless-audit; verifier=<seat>; "
              "evidence=<path|#issue>; date=YYYY-MM-DD")
        return 1 if strict else 0

    fields = {k.lower(): v.strip() for k, v in
              ((mm.group("k"), mm.group("v")) for mm in FIELD_RE.finditer(m.group("body")))}
    missing = [k for k in ("type", "verifier", "evidence", "date") if k not in fields]
    if missing:
        print(f"❌ {score.name}: independence block missing {', '.join(missing)}")
        return 1 if strict else 0

    ok = True
    if fields["type"] not in VALID_TYPES:
        print(f"❌ type={fields['type']!r} not in {sorted(VALID_TYPES)}")
        ok = False

    producer = _producer_seat()
    if fields["verifier"].strip().lower() == producer.strip().lower():
        print(f"❌ verifier == producer ({producer}) — that is the closed loop this")
        print("   check exists to refuse. A seat cannot be its own independent leg.")
        ok = False

    # GAP 1 — the verifier must be a seat that exists, not any string that isn't mine.
    seats = _registered_seats()
    vf = fields["verifier"].strip().lower()
    if seats is None:
        print("⚠ verifier registration UNCHECKED — fleet_scope.py unavailable "
              "(degraded to advisory; the leg is weaker than it reads)")
    elif vf not in seats:
        print(f"❌ verifier={fields['verifier']!r} is not in FLEET_STATE "
              f"({len(seats)} registered seats)")
        print("   An unregistered verifier cannot be re-contacted, re-audited, or held")
        print("   to a finding. Naming one is indistinguishable from naming nobody.")
        ok = False

    resolved, detail = _evidence_resolves(fields["evidence"])
    if not resolved:
        print(f"❌ evidence does not resolve: {detail}")
        ok = False

    # GAP 2 — v328-shipday:R10. Existence is not content.
    has_findings, fdetail = _evidence_carries_findings(fields["evidence"])
    if has_findings is False:
        print(f"❌ evidence carries no findings text: {fdetail}")
        print("   v328-shipday:R10 — a verdict without its findings is not a landed")
        print("   leg. This cycle's own Gate-2 Critic journalled 11 material findings")
        print("   and zero finding texts; seven died with the subagent's transcript.")
        ok = False
    elif has_findings is None:
        print(f"⚠ findings UNCHECKED — {fdetail}")

    # GAP 3 — v328-shipday:R41 / L1058: a headless reply is a claim, not evidence.
    if not CUT_RE.search(text):
        print("❌ no claims-under-test record in the score")
        print("   A headless verifier is a domain-generalist that confabulates")
        print("   citations (L1058/L718). R41 holds its reply under test until")
        print("   re-verified at source; the score must say that happened.")
        ok = False

    if ok:
        print(f"✅ {score.name}: independence leg declared, resolves, and is falsifiable")
        print(f"   type={fields['type']} verifier={fields['verifier']} ({detail})")
        print(f"   findings={fdetail}; claims-under-test recorded")
        return 0
    return 1 if strict else 0


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--version", required=True, help="release version, e.g. 3.28.0")
    ap.add_argument("--advisory", action="store_true",
                    help="report but exit 0 (for retroactive audits of old scores)")
    a = ap.parse_args()
    return check(a.version, strict=not a.advisory)


if __name__ == "__main__":
    sys.exit(main())
