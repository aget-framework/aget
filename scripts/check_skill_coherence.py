#!/usr/bin/env python3
"""
check_skill_coherence.py — Release-time skill self-description ↔ shipped-tree gate.

Closes #1614 (C-22-29, v3.22): a shipped SKILL.md can assert artifacts that are
ABSENT or MISLABELED in the shipped tree — a release-integrity gap distinct from
missing-field hygiene (#1335) and instance→template drift (#1489). Stale
self-descriptions are confabulation seeds (FLEET-UPG-021: a reviewer trusted a
"future" label and reported a shipped spec as absent).

Per skill, validates two failure modes (deliberately high-precision — only
declared contracts + explicit framing, NOT every incidental path mention, to
avoid the #1605 false-positive class):

  (A) MISSING: a path declared as Governing Spec / Governing SOP does not exist
      in the shipped tree (repo root or ../aget canonical sibling).
  (B) STALE-FUTURE: the self-description frames an artifact as future / not-yet-
      authored ("future AGET_X", "until X is authored", "authored at vN+") but
      that artifact actually ships.

Companion to check_skill_grounding.py (ontology binding) — this validates that a
skill's prose claims about its governing artifacts match the tree.

Usage:
  python3 scripts/check_skill_coherence.py
  python3 scripts/check_skill_coherence.py --json
  python3 scripts/check_skill_coherence.py --skill aget-create-initiative
  python3 scripts/check_skill_coherence.py --self-test

Exit codes:
  0  No coherence defects (or read-only/self-test pass)
  1  At least one skill has a MISSING or STALE-FUTURE defect (release-blocking)
  2  Usage / environment error
"""

import argparse
import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
SKILLS_DIR = REPO_ROOT / ".claude" / "skills"
# Canonical public artifacts live at the sibling ../aget; the shipped tree a
# release gate inspects includes both the instance and canonical surfaces.
SEARCH_ROOTS = [REPO_ROOT, REPO_ROOT.parent / "aget"]

# A declared governing contract line: "**Governing Spec**: ... <path>"
GOVERNING_LINE = re.compile(
    r"\*\*Governing (?:Spec|SOP)\*\*:\s*(.+)", re.IGNORECASE
)
# Artifact paths/basenames inside a line (specs + SOPs).
ARTIFACT_REF = re.compile(
    r"(?:[\w./-]*?)((?:AGET_[A-Z0-9_]+_SPEC|SOP_[a-z0-9_]+)\.(?:md|yaml))"
)
# Stale-future framing naming a concrete artifact.
STALE_FUTURE = re.compile(
    r"(?:future\s+|not[- ]yet[- ]authored\s+|until\s+\S*?|authored at v[\d.]+\+?\s*[—-]?\s*)"
    r"[`'\"]?((?:AGET_[A-Z0-9_]+_SPEC|SOP_[a-z0-9_]+)(?:\.(?:md|yaml))?)",
    re.IGNORECASE,
)
# Verb-anchored only: the artifact must be the SUBJECT of the future-claim
# ("X is future / is authored at v / is to be authored"). A bare nearby
# "future" is NOT enough — it may modify a *later* artifact (#1605 false-
# positive class: "SOP_x (...) + future AGET_Y_SPEC" must flag Y, not x).
FUTURE_NEAR = re.compile(
    r"((?:AGET_[A-Z0-9_]+_SPEC|SOP_[a-z0-9_]+)(?:\.(?:md|yaml))?)"
    r"\s+(?:is\s+)?(?:still\s+)?(?:is\s+)?(?:future\b|to be authored|not yet authored|"
    r"authored at v[\d.]+)",
    re.IGNORECASE,
)


def artifact_exists(basename: str) -> bool:
    """True if an artifact with this basename exists under any search root."""
    stem = basename.split("/")[-1]
    for root in SEARCH_ROOTS:
        if not root.exists():
            continue
        # cheap: rglob by exact name (bounded — skills/specs/sops trees are small)
        for _ in root.rglob(stem):
            return True
    return False


def _norm(name: str) -> str:
    n = name.strip().strip("`'\"")
    if not n.endswith((".md", ".yaml")):
        # default specs/SOPs to .md when extension omitted in prose
        n = n + ".md"
    return n


def check_skill(path: Path) -> dict:
    """Return coherence findings for a single SKILL.md."""
    text = path.read_text(encoding="utf-8", errors="replace")
    name = path.parent.name
    missing, stale = [], []

    # (A) declared governing contracts must exist
    for line in text.splitlines():
        m = GOVERNING_LINE.search(line)
        if not m:
            continue
        for ref in ARTIFACT_REF.findall(m.group(1)):
            base = _norm(ref)
            if not artifact_exists(base):
                missing.append({"artifact": base, "context": "Governing Spec/SOP", "line": line.strip()[:120]})

    # (B) stale-future framing about a shipped artifact
    seen = set()
    for pat in (STALE_FUTURE, FUTURE_NEAR):
        for ref in pat.findall(text):
            base = _norm(ref)
            if base in seen:
                continue
            seen.add(base)
            if artifact_exists(base):
                stale.append({"artifact": base, "issue": "framed as future/unauthored but ships"})

    return {
        "skill": name,
        "missing_governing": missing,
        "stale_future": stale,
        "defects": len(missing) + len(stale),
    }


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__.split("\n\n")[0])
    p.add_argument("--json", action="store_true", help="Emit machine-readable JSON")
    p.add_argument("--skill", default=None, help="Check a single skill by directory name")
    p.add_argument("--self-test", action="store_true", help="Run built-in self-test and exit")
    args = p.parse_args()

    if args.self_test:
        return _self_test()

    if not SKILLS_DIR.exists():
        print(f"ERROR: skills dir not found: {SKILLS_DIR}", file=sys.stderr)
        return 2

    files = sorted(SKILLS_DIR.glob("*/SKILL.md"))
    if args.skill:
        files = [f for f in files if f.parent.name == args.skill]
        if not files:
            print(f"ERROR: skill not found: {args.skill}", file=sys.stderr)
            return 2

    results = [check_skill(f) for f in files]
    defective = [r for r in results if r["defects"]]

    if args.json:
        print(json.dumps({"checked": len(results), "defective": len(defective), "results": defective}, indent=2))
    else:
        print(f"=== skill-coherence gate (#1614) — {len(results)} skills checked ===")
        if not defective:
            print("All skills coherent: declared specs/SOPs exist; no stale-future framing.")
        for r in defective:
            print(f"\n{r['skill']}  ({r['defects']} defect(s)):")
            for m in r["missing_governing"]:
                print(f"  MISSING  {m['artifact']} — declared {m['context']} but absent from tree")
            for s in r["stale_future"]:
                print(f"  STALE    {s['artifact']} — {s['issue']}")

    return 1 if defective else 0


def _self_test() -> int:
    """Deterministic self-test using synthetic in-memory SKILL bodies."""
    import tempfile, os
    failures = []
    with tempfile.TemporaryDirectory() as td:
        # a shipped artifact (exists) and reference to a truly-absent one
        root = Path(td)
        (root / "specs").mkdir()
        (root / "specs" / "AGET_SHIPS_SPEC.md").write_text("x")
        global SEARCH_ROOTS
        saved = SEARCH_ROOTS
        SEARCH_ROOTS = [root]
        try:
            sk = root / ".claude" / "skills" / "demo"
            sk.mkdir(parents=True)
            body = (
                "**Governing Spec**: AGET_ABSENT_SPEC.md — canonical\n"
                "serves until AGET_SHIPS_SPEC is authored at v9.9+\n"
            )
            f = sk / "SKILL.md"
            f.write_text(body)
            r = check_skill(f)
            if not any(m["artifact"] == "AGET_ABSENT_SPEC.md" for m in r["missing_governing"]):
                failures.append("did not flag absent governing spec")
            if not any(s["artifact"] == "AGET_SHIPS_SPEC.md" for s in r["stale_future"]):
                failures.append("did not flag stale-future framing of a shipped spec")
            # negative: a coherent skill yields 0 defects
            (sk / "SKILL.md").write_text("**Governing Spec**: AGET_SHIPS_SPEC.md — Active\n")
            r2 = check_skill(f)
            if r2["defects"] != 0:
                failures.append(f"false positive on coherent skill: {r2}")
        finally:
            SEARCH_ROOTS = saved
    if failures:
        print("SELF-TEST FAIL:\n  " + "\n  ".join(failures))
        return 1
    print("PASS")
    return 0


if __name__ == "__main__":
    sys.exit(main())
