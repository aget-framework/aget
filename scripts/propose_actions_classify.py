#!/usr/bin/env python3
"""
propose_actions_classify.py — L980 audit-after-synthesis classification heuristic.

Implements the machine-checkable heuristics behind /aget-propose-actions Step 2.7
(REQ-PA-013 / CAP-PA-013-01..04). Codifies L980 (audit-after-synthesis pairing) +
gh#1476 (Healthy Friction codification, Layer 5 — structural).

Two levels:
  1. classify(action_text)            -> 'synthesis' | 'audit'   (single-action, verb-based)
  2. check_pairing(actions)           -> pairing report          (batch-level, same-artifact)

Pairing rule (REQ-PA-013): WHEN >=2 proposed Actions target the same normalized
artifact path, at least one of those Actions MUST classify as 'audit'. If UNMET,
the skill surfaces a Healthy Friction violation (L178 override available).

Design decisions (Gate 0):
  - CAP-PA-013-01 audit-class:   description contains a primary-source re-derivation
                                 verb (re-count/re-derive/audit/verify-from-source/
                                 re-grep/re-read/re-verify/reconcile/cross-check).
  - CAP-PA-013-02 synthesis-class: description contains a composition verb
                                 (compose/write/fold/update/narrate/summarize/draft/
                                 populate/integrate/stamp/annotate/add-row) on a
                                 governed artifact path.
  - CAP-PA-013-03 same-artifact: normalized path (strip ./, repo-relative, lowercased
                                 extension) equality across Actions in the batch.
  - CAP-PA-013-04 ambiguity:     fail-safe — when neither verb-set matches, OR when
                                 both match, default to 'synthesis'. 'audit' is only
                                 returned when an audit verb is present AND no synthesis
                                 verb is present, so a synthesis action cannot masquerade
                                 as audit to satisfy the pairing (friction surfaces, not hides).

Usage:
  python3 scripts/propose_actions_classify.py --self-test     # exit 0 on PASS
  python3 scripts/propose_actions_classify.py --classify "Audit stream-stamps ..."
  python3 scripts/propose_actions_classify.py --check-batch path/to/batch.json

Exit codes (CAP-SCRIPT-004-03) — verified against behaviour, not asserted:
  0  PASS — --classify printed a class, or --self-test passed, or the batch satisfies
     REQ-PA-013 pairing
  1  --self-test failed
  2  UNMET — a same-artifact group carries only synthesis-class actions (Healthy
     Friction surface; blocking is principal-elected, not automatic)
  3  MALFORMED INPUT — unreadable/invalid batch file, or a batch whose actions carry
     none of the required keys {"text", "artifact"}. Deliberately NOT 0 and NOT 2:
     such a batch used to return pairing_status=PASS over zero groups, so the gate
     reported healthy on input it had never read. UNKNOWN is not PASS, and it is not
     UNMET either — conflating them would make a schema bug look like a governance
     finding.
"""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

# CAP-PA-013-01: primary-source re-derivation verbs (audit-class signal)
#
# NB: "reconcile" REMOVED 2026-08-15 — it was the one entry here that is not a
# re-derivation. "Reconcile" is ambiguous between *compare against source* (audit)
# and *make agree by editing* (synthesis), and the second sense is the common one on
# a governed artifact ("reconcile the INDEX counts" = write to the INDEX). Because it
# carried no synthesis verb, CAP-PA-013-04's masquerade guard never fired, so a batch
# of two writes to one artifact satisfied the pairing gate outright:
#
#   [{"artifact": "planning/initiatives/INDEX.md", "text": "update the stream rows"},
#    {"artifact": "planning/initiatives/INDEX.md", "text": "reconcile the counts"}]
#   -> pairing_status: PASS, has_audit: true, vacuous: false      (measured pre-fix)
#
# That is the L980 vector the gate exists to close, passing through the gate. Removed
# rather than moved to SYNTHESIS_VERBS: the word genuinely has both senses, and the
# fail-safe (matches neither set -> synthesis, CAP-PA-013-04) is the correct disposition
# for an ambiguous verb. An action that really does re-derive should say so —
# "re-derive", "cross-check", "verify-from-source" all remain and all still match.
# Pinned both polarities: tests/test_propose_actions_classify_hardening.py.
AUDIT_VERBS = (
    r"re-?count", r"re-?deriv", r"re-?grep", r"re-?read", r"re-?verif",
    r"audit", r"verify[- ]from[- ]source", r"cross-?check",
    r"re-?sum", r"re-?tally", r"re-?check",
)

# CAP-PA-013-02: composition verbs (synthesis-class signal).
# NB: "stamp" deliberately excluded — collides with the domain noun "stream-stamp"
# (false-matched the audit example "Audit stream-stamps ..."); the verb sense of
# stamping a status is covered by update/annotate, and the fail-safe default (neither
# verb-set -> synthesis) catches any residual stamp-only action.
# EXPANDED 2026-08-15. The 16-entry list below used to end at `\bmerge\b`, and that
# under-coverage made CAP-PA-013-04's masquerade guard almost inert. Measured before
# the expansion: of 32 ordinary composition verbs, **32/32** produced a false audit
# when paired with an audit verb —
#
#   classify("re-verify and rewrite the INDEX counts")  ->  "audit"     (pre-fix)
#
# `\bwrite\b` did not even match "rewrite", the most obvious composition verb there is.
# The asymmetry to hold onto: AUDIT_VERBS may stay narrow, because it is the *claim*;
# SYNTHESIS_VERBS must be broad, because it is the *guard*. A missing audit verb costs
# a legitimate action its audit-class (fail-safe, more friction). A missing synthesis
# verb lets a write buy audit-class (fail-open, the L980 vector).
#
# Over-matching here is therefore the SAFE direction: a false synthesis hit demotes an
# action to synthesis, which can only make the pairing gate harder to satisfy.
#
# Residual bound, stated rather than hidden: this is still an enumeration, so an
# unlisted verb still slips. `stamp` remains deliberately absent (it false-matched the
# domain noun "stream-stamp" in the audit example; see the note above), so "re-stamp"
# is a known live gap. The list approach has a floor it cannot cross — tracked, not
# silently relied upon. Both polarities pinned in
# tests/test_propose_actions_classify_hardening.py.
SYNTHESIS_VERBS = (
    # original 16
    r"compos", r"\bwrite\b", r"\bwrote\b", r"\bfold\b", r"\bfolds?\b", r"update",
    r"narrat", r"summar", r"\bdraft", r"populat", r"integrat",
    r"annotat", r"add[- ]row", r"add a row", r"multi-?row", r"\bmerge\b",
    # re-write family — the gap that let "re-verify and rewrite" read as audit
    r"re-?writ", r"re-?word", r"re-?work", r"re-?format", r"restructur", r"refactor",
    # edit / amend family
    r"revis", r"\bamend", r"\bedit", r"\bcorrect(?:s|ed|ing|ions?)?\b", r"\bfix",
    r"\bpatch", r"adjust", r"\bbump", r"tidy", r"clean[- ]?up", r"normaliz",
    # add / remove family
    r"replac", r"insert", r"append", r"\bdelet", r"\bremov", r"expand", r"extend",
    r"backfill", r"migrat",
    # authoring family
    r"generat", r"\bcreat", r"\bauthor", r"\brecord",
)

# Governed artifact path prefixes / files (CAP-PA-013-02 scope)
GOVERNED_PREFIXES = (
    "planning/", "governance/", ".aget/", "aget/", "ontology/", "sops/", "docs/",
)
GOVERNED_FILES = ("agents.md", "claude.md")


def _matches_any(text: str, patterns) -> bool:
    low = text.lower()
    return any(re.search(p, low) for p in patterns)


def classify(action_text: str) -> str:
    """Classify a single proposed Action's description as 'synthesis' or 'audit'.

    Fail-safe (CAP-PA-013-04): 'audit' only when an audit verb is present AND no
    synthesis verb is present; otherwise 'synthesis' (covers neither-match and
    both-match). Conservative so synthesis cannot masquerade as audit.
    """
    has_audit = _matches_any(action_text, AUDIT_VERBS)
    has_synth = _matches_any(action_text, SYNTHESIS_VERBS)
    if has_audit and not has_synth:
        return "audit"
    return "synthesis"


def normalize_path(p: str) -> str:
    """CAP-PA-013-03: repo-relative, leading-./ stripped, lowercased extension."""
    if not p:
        return ""
    p = p.strip().lstrip("./")
    # split extension, lowercase only the extension
    m = re.match(r"^(.*?)(\.[A-Za-z0-9]+)?$", p)
    if m and m.group(2):
        return m.group(1) + m.group(2).lower()
    return p


def is_governed(artifact_path: str) -> bool:
    norm = normalize_path(artifact_path)
    low = norm.lower()
    base = low.rsplit("/", 1)[-1]
    return low.startswith(GOVERNED_PREFIXES) or base in GOVERNED_FILES


def check_pairing(actions: list[dict]) -> dict:
    """Batch-level REQ-PA-013 pairing check.

    actions: list of {"text": str, "artifact": str}
    Returns a report dict: per-artifact groups touched by >=2 actions, whether each
    group has an audit-class action, and overall pairing_status PASS|UNMET.
    """
    # Schema gate — fail CLOSED, not silently PASS.
    #
    # 2026-07-29: a batch submitted with keys {"desc","path"} instead of {"text","artifact"}
    # returned `pairing_status: PASS` with zero groups. Every artifact read as "", so nothing
    # was governed, so no group had >=2 members, so nothing could be unpaired. The L980
    # Layer-5 gate reported healthy on a batch it had not looked at. An optional check must
    # not default to healthy: a malformed batch is UNKNOWN, and UNKNOWN is not PASS.
    KNOWN = {"text", "artifact"}
    malformed = [
        i for i, a in enumerate(actions)
        if not isinstance(a, dict) or not KNOWN & set(a)
    ]
    if malformed:
        raise ValueError(
            f"check_pairing: {len(malformed)} action(s) at indices {malformed} carry none of "
            f"the required keys {sorted(KNOWN)}. Refusing to report a pairing status for a "
            f"batch that was not read (would emit a vacuous PASS). Got keys: "
            + "; ".join(
                sorted(set(k for a in actions if isinstance(a, dict) for k in a)) or ["<none>"]
            )
        )

    # group action indices by normalized governed artifact path
    groups: dict[str, list[int]] = {}
    ungoverned: list[int] = []
    for i, a in enumerate(actions):
        art = a.get("artifact", "")
        if not is_governed(art):
            ungoverned.append(i)
            continue
        groups.setdefault(normalize_path(art), []).append(i)

    same_artifact_groups = {k: v for k, v in groups.items() if len(v) >= 2}
    unpaired = []
    detail = {}
    for art, idxs in same_artifact_groups.items():
        classes = [classify(actions[i].get("text", "")) for i in idxs]
        has_audit = "audit" in classes
        detail[art] = {"action_indices": idxs, "classes": classes, "has_audit": has_audit}
        if not has_audit:
            unpaired.append(art)

    status = "PASS" if not unpaired else "UNMET"
    return {
        "same_artifact_groups": detail,
        "unpaired_artifacts": unpaired,
        "pairing_status": status,
        # Make the check's OWN SCOPE visible, so a PASS can be read for what it covered
        # (vg2:R3 — the instrument's view is not its output). A PASS over 0 governed
        # artifacts is trivially true and must not look like a clean bill of health.
        "scope": {
            "actions_seen": len(actions),
            "governed_actions": len(actions) - len(ungoverned),
            "ungoverned_action_indices": ungoverned,
            "same_artifact_group_count": len(same_artifact_groups),
            "vacuous": not same_artifact_groups,
        },
    }


# ---- L980 arc replay fixture (Gate 0 / Gate 2 reference) --------------------
L980_ARC = [
    {"text": "Fold NASCENT initiative INTO active table", "artifact": "planning/initiatives/INDEX.md"},
    {"text": "Update Q5 row: ACTIVE count 8->7 hits ceiling", "artifact": "planning/initiatives/INDEX.md"},
    {"text": "Audit stream-stamps across retained ACTIVE manifests", "artifact": "planning/initiatives/INDEX.md"},
]


def _self_test() -> int:
    failures = []

    # Gate 0 V-test: single-action classification
    cases = [
        ("Fold NASCENT initiative INTO active table", "synthesis"),
        ("Audit stream-stamps across retained ACTIVE manifests", "audit"),
        ("Re-derive Tier-1 SU from candidate inventory", "audit"),
        ("Compose the v3.19 theme narrative", "synthesis"),
        ("Re-count ACTIVE roster but also write the summary row", "synthesis"),  # both -> synthesis (fail-safe)
        ("Ping the supervisor", "synthesis"),  # neither -> synthesis (fail-safe)
    ]
    for text, expected in cases:
        got = classify(text)
        if got != expected:
            failures.append(f"classify({text!r}) == {got!r}, expected {expected!r}")

    # batch: L980 arc (Actions 1+2 synthesis, Action 3 audit) -> PASS pairing
    rep = check_pairing(L980_ARC)
    if rep["pairing_status"] != "PASS":
        failures.append(f"L980 arc pairing == {rep['pairing_status']}, expected PASS")

    # negative: remove the audit action -> UNMET
    rep_neg = check_pairing(L980_ARC[:2])
    if rep_neg["pairing_status"] != "UNMET":
        failures.append(f"L980 arc minus audit == {rep_neg['pairing_status']}, expected UNMET")

    # false-positive avoidance: two synthesis actions on DIFFERENT artifacts -> PASS (no same-artifact group)
    diff = [
        {"text": "Write Tier placement", "artifact": "planning/VERSION_SCOPE_v3.19.0.md"},
        {"text": "Update INDEX roster", "artifact": "planning/initiatives/INDEX.md"},
    ]
    rep_fp = check_pairing(diff)
    if rep_fp["pairing_status"] != "PASS":
        failures.append(f"different-artifact batch == {rep_fp['pairing_status']}, expected PASS (no same-artifact group)")

    if failures:
        print("SELF-TEST FAIL:")
        for f in failures:
            print("  -", f)
        return 1
    print("PASS")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="L980 audit-after-synthesis classifier")
    ap.add_argument("--self-test", action="store_true", help="run built-in heuristic tests")
    ap.add_argument("--classify", metavar="TEXT", help="classify one action description")
    ap.add_argument("--check-batch", metavar="JSON", help="path to JSON list of {text,artifact}")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()
    if args.classify is not None:
        print(classify(args.classify))
        return 0
    if args.check_batch:
        try:
            actions = json.loads(Path(args.check_batch).read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"MALFORMED INPUT: cannot read batch {args.check_batch!r}: {exc}")
            return 3
        try:
            rep = check_pairing(actions)
        except (ValueError, AttributeError, TypeError) as exc:
            # A schema failure is not a governance finding — keep the codes distinct so a
            # caller cannot read "wrong keys" as "unpaired synthesis".
            print(f"MALFORMED INPUT: {exc}")
            return 3
        print(json.dumps(rep, indent=2))
        return 0 if rep["pairing_status"] == "PASS" else 2
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
