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
# `\bauthor` and `\brecord` (bare stems) NARROWED 2026-09-22 — the THIRD and FOURTH instance
# of the defect the `populat` note above records, and the file had already written the remedy.
# Measured: an audit action describing its own subject could not classify as audit, because
# "re-derive the AUTHORitative counterpart" and "cross-check the register of RECORD" both hit a
# synthesis stem. Three honest rewordings returned UNMET before the pattern set was probed;
# reaching PASS required naming the audit without naming the thing audited. Per the note above,
# over-matching is safe when it demotes a WRITE — here it demoted a re-derivation whose subject
# is, by the goal's own wording, "the authoritative copy".
#
# `author` takes the verb-form treatment: bare `author`/`authors`/`authored`/`authoring` stay
# synthesis; `authoritative`/`authority` no longer match, and neither is ever the verb, so the
# guard loses nothing.
#
# `record` is NOT given the same treatment, deliberately. Bare "record" IS a synthesis verb
# ("record the finding"), so restricting to suffixed forms would weaken the guard. Instead the
# colliding NOUN usages are excluded by their DETERMINER -- "of record", "the record",
# "a record". A determiner immediately before it marks the noun; the verb never carries one.
# Narrower than a stem change and it costs the guard nothing. ("the record" was found by the
# class-level test below on its first run, not by a reader -- which is the point of having it.)
#
# THE INVARIANT THIS DOES NOT FIX, stated so the next reader does not mistake a carrier repair
# for a resolution: substring matching is the wrong mechanism for classifying intent. Four
# word-by-word repairs in one layer is the signal. `test_no_synthesis_pattern_swallows_a_
# governance_noun` below converts this from patch-on-report into a class-level guard; it does
# not make regex the right mechanism. Tracked: #2687, #2675, #2304.
SYNTHESIS_VERBS = (
    # original 16
    r"compos", r"\bwrite\b", r"\bwrote\b", r"\bfold\b", r"\bfolds?\b", r"update",
    r"narrat", r"summar", r"\bdraft",
    # `populat` (bare stem) REPLACED by the verb forms, 2026-09-05. The stem swallowed the
    # NOUN "population"/"populations", and that noun is this seat's own governance vocabulary
    # for a control set or a denominator — AGENTS.md: "A guard's population is part of its
    # contract." Measured: "audit the ceremony control population" classified synthesis while
    # "audit the ceremony control set" classified audit, so three audit verbs in one sentence
    # (`re-derive`, `audit`, `re-count`) were overridden by a noun.
    #
    # This is NOT the safe over-match the note above licenses. Over-matching is safe when it
    # demotes a WRITE; here it demoted a CENSUS — the exact class REQ-PA-013 exists to
    # require — and left the friction's own remedy ("add an audit-class Action") unsatisfiable
    # while the action was described accurately. It is the same call already made for bare
    # `stamp` and resolved the same way: a false synthesis hit that "would have made the gate
    # unsatisfiable for legitimate audit wording and pushed authors to reword" is not worth it.
    r"populat(?:e|es|ed|ing)\b", r"integrat",
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
    r"generat", r"\bcreat", r"author(?:s|ed|ing)?\b", r"(?<!of )(?<!the )(?<!a )\brecord",
    # stamp family — HALF the known gap closed 2026-08-15; the other half stays open
    # deliberately, and the reason is worth keeping.
    #
    # `re-?stamp` is safe and unambiguously the verb: "stream-stamp" contains "m-stamp",
    # not "re-stamp", so it cannot false-match. Added.
    #
    # A bare `stamp` was tried and REVERTED. `(?<![-\w])stamps?\b` does dodge the
    # hyphenated domain noun "stream-stamp", but it still swallows the SPACED form —
    # measured: "audit the stream stamps" flipped from audit to synthesis, which is a
    # real phrasing here and an existing test fixture. That is the fail-SAFE direction,
    # so it would not have opened a hole; it would have made the gate unsatisfiable for
    # legitimate audit wording and pushed authors to reword. Not worth it for one rare
    # phrasing ("re-verify and stamp X") whose verb sense is already covered by
    # update/annotate, per the original exclusion note above.
    #
    # Residual masquerade after this change: bare "stamp" only, 1 of 32 measured.
    # Asserted as a bound in the hardening tests, not hidden.
    r"re-?stamp",
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
    group has an audit-class action, overall pairing_status PASS|UNMET, and -- as a
    SEPARATE value at the same altitude -- coverage COVERED|NO_SUBJECT|NONE_GOVERNED.
    Read BOTH: a PASS whose coverage is not COVERED means nothing was examined.
    """
    # Schema gate — fail CLOSED, not silently PASS.
    #
    # 2026-07-29: a batch submitted with keys {"desc","path"} instead of {"text","artifact"}
    # returned `pairing_status: PASS` with zero groups. Every artifact read as "", so nothing
    # was governed, so no group had >=2 members, so nothing could be unpaired. The L980
    # Layer-5 gate reported healthy on a batch it had not looked at. An optional check must
    # not default to healthy: a malformed batch is UNKNOWN, and UNKNOWN is not PASS.
    KNOWN = {"text", "artifact"}  # subject_id is optional and additive; not required for a batch to be readable
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

    # GROUPING KEY: declared subject_id, else normalized governed artifact path.
    #
    # 2026-08-30: the path-only key made a correctly-paired batch look unpaired. An audit
    # action re-derived a quantity into one artifact while the synthesis action wrote the
    # conclusion into another -- the pairing the rule exists to require, invisible to it,
    # because the rule keyed on path identity when the thing that matters is SUBJECT
    # identity. The batch's own pre-flight returned PASS/NO_SUBJECT and that was the
    # motivating evidence.
    #
    # `subject_id` is OPT-IN and free-form. When absent, behaviour is exactly as before,
    # so no existing caller changes. When present, actions carrying the same subject_id
    # group together whether or not they share a path.
    #
    # Deliberately NOT done: inferring a shared subject from prose. Guessing which actions
    # are "about the same thing" would make the gate's verdict depend on phrasing, which is
    # the failure mode CAP-PA-013-04 already fails safe against. A subject must be DECLARED.
    #
    # Governed-ness is still required to enter a group: an ungoverned artifact does not
    # become governed by being labelled. subject_id widens what can pair, never what is in
    # scope.
    groups: dict[str, list[int]] = {}
    ungoverned: list[int] = []
    subject_keyed: set[str] = set()
    for i, a in enumerate(actions):
        art = a.get("artifact", "")
        if not is_governed(art):
            ungoverned.append(i)
            continue
        # The path group is ALWAYS formed; a declared subject ADDS a second group and never
        # replaces the path key. Replacing it let two writes to one artifact escape the
        # same-artifact rule by declaring different subjects (independent review round 1,
        # R1-04; REQ-PA-013, V-PA-013 falsifier).
        groups.setdefault(normalize_path(art), []).append(i)
        subj = a.get("subject_id")
        if subj:
            key = f"subject:{subj}"
            subject_keyed.add(key)
            groups.setdefault(key, []).append(i)

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

    # COVERAGE IS A SECOND FACT, REPORTED AT THE SAME ALTITUDE AS THE VERDICT.
    #
    # Ruled 2026-08-30 (principal, requirements altitude: SPLIT), after this function
    # returned `pairing_status: PASS` on three consecutive batches whose own
    # `scope.vacuous` read true. The predicate was never wrong -- it computed the right
    # answer and wrote it into a nested field that callers do not consult, while the
    # verdict field said PASS. Twice the reading agent then substituted a hand-asserted
    # pairing; disclosure of the nested flag prevented neither.
    #
    # The malformed-input gate above already holds that "UNKNOWN is not PASS". This is
    # the same principle one step further in: an EMPTY SCOPE is also not a clean bill of
    # health. The difference is that a malformed batch is an error, while an empty scope
    # is a legitimate state -- so it is reported, not raised.
    #
    # Deliberately NOT done: adding a third `pairing_status` value. That option was put to
    # the principal as NAMED and rejected in favour of SPLIT. A caller switching on
    # PASS/UNMET keeps working; a caller that wants to know what was examined reads
    # `coverage`. Blocking on an empty scope was also rejected (FAIL) -- a control may not
    # be called blocking until shown failing on a genuine case.
    if not groups:
        coverage = "NONE_GOVERNED"   # no action targeted a governed artifact at all
    elif not same_artifact_groups:
        coverage = "NO_SUBJECT"      # governed artifacts present, but none touched twice
    else:
        coverage = "COVERED"         # the rule had something to test, and tested it

    return {
        "same_artifact_groups": detail,
        "unpaired_artifacts": unpaired,
        "pairing_status": status,
        "coverage": coverage,
        # Make the check's OWN SCOPE visible, so a PASS can be read for what it covered
        # (vg2:R3 — the instrument's view is not its output). A PASS over 0 governed
        # artifacts is trivially true and must not look like a clean bill of health.
        "scope": {
            "actions_seen": len(actions),
            "governed_actions": len(actions) - len(ungoverned),
            "ungoverned_action_indices": ungoverned,
            "same_artifact_group_count": len(same_artifact_groups),
            "subject_keyed_groups": sorted(k for k in same_artifact_groups if k.startswith("subject:")),
            "actions_declaring_subject": sum(1 for a in actions if a.get("subject_id")),
            "vacuous": not same_artifact_groups,
        },
    }


# ---- REQ-PA-022: outcome gating (gh#2703) ------------------------------------
# A batch aimed at an OUTCOME (a CI verdict, a pushed state, another Aget's repo) can close
# having moved only MEASUREMENT, because the step that moves the outcome is gated (the
# principal's push approval, a cross-Aget write, a ruling) and was silently dropped. Field
# case 2026-09-23: a 4h --batch --go "towards remediations" fixed a health instrument, left 22
# commits unpushed behind the principal's push approval, and closed. This check makes that shape
# fail at proposal time rather than at close.
FOCUS_KINDS = ("outcome", "measurement", "other")


def check_outcome_gating(batch: dict) -> dict:
    """REQ-PA-022. Batch: {"focus_kind": outcome|measurement|other, "focus": str,
    "acknowledges_no_outcome_mover": bool (optional),
    "actions": [{"text", "moves": outcome|measurement, "gated": bool, "gate": str,
    "decision_listed": bool}]}. Returns {"status": PASS|UNMET|UNAVAILABLE, "reasons",
    "gated_owed", "outcome_movers"}. An undeclared focus kind is UNAVAILABLE, never PASS."""
    if not isinstance(batch, dict) or batch.get("focus_kind") not in FOCUS_KINDS:
        return {"status": "UNAVAILABLE", "gated_owed": [], "outcome_movers": 0,
                "reasons": ["the batch declares no focus_kind in {outcome, measurement, other}; "
                            "an undeclared focus cannot be judged"]}
    actions = batch.get("actions")
    if not isinstance(actions, list) or not actions:
        return {"status": "UNAVAILABLE", "gated_owed": [], "outcome_movers": 0,
                "reasons": ["the batch carries no actions"]}
    # Strict shape check (independent review round 1, R1-05): a malformed action must be
    # UNAVAILABLE, never PASS by truthiness ("false" as a string) and never a crash.
    bad = []
    ack = batch.get("acknowledges_no_outcome_mover", False)
    if not isinstance(ack, bool):
        bad.append("acknowledges_no_outcome_mover must be a boolean")
    for i, a in enumerate(actions, start=1):
        if not isinstance(a, dict):
            bad.append(f"action {i} is not an object")
            continue
        if not isinstance(a.get("text"), str) or not a["text"].strip():
            bad.append(f"action {i} has no text")
        for flag in ("gated", "decision_listed"):
            if flag in a and not isinstance(a[flag], bool):
                bad.append(f"action {i}: {flag} must be a boolean")
        if a.get("moves") == "outcome" and a.get("gated") is True and \
                not (isinstance(a.get("gate"), str) and a["gate"].strip()):
            bad.append(f"action {i} is a gated outcome step that names no gate, so no exact change is ready to approve")
    if bad:
        return {"status": "UNAVAILABLE", "gated_owed": [], "outcome_movers": 0, "reasons": bad}
    reasons, gated_owed, movers = [], [], 0
    for i, a in enumerate(actions, start=1):
        text = str(a.get("text", "")).strip()
        moves = a.get("moves")
        if batch["focus_kind"] == "outcome" and moves not in ("outcome", "measurement"):
            reasons.append(f"action {i} ({text[:60]!r}) does not declare moves: outcome | measurement")
        if moves == "outcome":
            movers += 1
            if a.get("gated"):
                gate = a.get("gate") or "gate unspecified"
                gated_owed.append(f"{text} ({gate})")
                if not a.get("decision_listed"):
                    reasons.append(f"gated outcome step not listed under Decisions needed: {text} ({gate})")
    notes = []
    if batch["focus_kind"] == "outcome" and movers == 0:
        # The requirement is to SAY it (REQ-PA-022 (3)); a batch that says so passes this leg
        # (independent review round 1, R1-06). Silence is what fails.
        if ack:
            notes.append("the batch states that it cannot move its outcome")
        else:
            reasons.append("no action moves the outcome: this batch cannot move its outcome. Say so "
                           "(acknowledges_no_outcome_mover: true), or list the gated outcome step "
                           "under Decisions needed")
    return {"status": "UNMET" if reasons else "PASS", "reasons": reasons, "notes": notes,
            "gated_owed": gated_owed, "outcome_movers": movers}


def close_summary(outcome_changed: bool, measurement_changed: bool, gated_owed=()) -> str:
    """REQ-PA-022 close report: outcome and measurement are stated separately, and any gated act
    still owed is named. A batch that improved measurement only must not read as done."""
    parts = ["outcome changed" if outcome_changed else "outcome unchanged",
             "measurement improved" if measurement_changed else "measurement unchanged"]
    if gated_owed:
        parts.append("gated act owed: " + "; ".join(gated_owed))
    return "; ".join(parts)


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

    # REQ-PA-022 (gh#2703): the 2026-09-23 field case, both polarities
    fix = {"text": "fix the health instrument", "moves": "measurement"}
    push = {"text": "push the CI fixes", "moves": "outcome", "gated": True, "gate": "principal push approval"}
    og_bad = check_outcome_gating({"focus_kind": "outcome", "actions": [fix, dict(push, decision_listed=False)]})
    og_ok = check_outcome_gating({"focus_kind": "outcome", "actions": [fix, dict(push, decision_listed=True)]})
    og_none = check_outcome_gating({"actions": [fix]})
    if og_bad["status"] != "UNMET":
        failures.append(f"gated outcome step not listed == {og_bad['status']}, expected UNMET")
    if og_ok["status"] != "PASS":
        failures.append(f"gated outcome step listed == {og_ok['status']}, expected PASS")
    if og_none["status"] != "UNAVAILABLE":
        failures.append(f"undeclared focus == {og_none['status']}, expected UNAVAILABLE")

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
    ap.add_argument("--check-outcome-gating", metavar="JSON",
                    help="REQ-PA-022: path to a batch {focus_kind, actions:[{text, moves, gated, gate, decision_listed}]}")
    args = ap.parse_args(argv)

    if args.self_test:
        return _self_test()
    if args.check_outcome_gating:
        try:
            batch = json.loads(Path(args.check_outcome_gating).read_text())
        except (OSError, json.JSONDecodeError) as exc:
            print(f"MALFORMED INPUT: cannot read batch {args.check_outcome_gating!r}: {exc}")
            return 3
        rep = check_outcome_gating(batch)
        print(json.dumps(rep, indent=2))
        return {"PASS": 0, "UNMET": 2}.get(rep["status"], 3)
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
        # SPLIT (ruled 2026-08-30): the verdict must not be readable without the coverage.
        # Exit status is deliberately UNCHANGED -- blocking on an empty scope was put to
        # the principal as FAIL and rejected, because a control may not be called blocking
        # until shown failing on a genuine case. So the signal is a banner, not an exit code:
        # a human or log reader cannot see PASS without also seeing that nothing was examined.
        cov = rep.get("coverage")
        if cov != "COVERED":
            why = {
                "NONE_GOVERNED": "no action targeted a governed artifact",
                "NO_SUBJECT": "governed artifacts present, but none touched by 2+ actions",
            }.get(cov, "coverage not established")
            print(
                f"COVERAGE: {cov} -- pairing_status={rep['pairing_status']} was NOT EARNED: {why}. "
                f"The rule had nothing to test. Do not read this as a clean bill of health, and do "
                f"not substitute a hand-asserted pairing for it.",
                file=sys.stderr,
            )
        return 0 if rep["pairing_status"] == "PASS" else 2
    ap.print_help()
    return 0


if __name__ == "__main__":
    sys.exit(main())
