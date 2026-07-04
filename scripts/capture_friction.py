#!/usr/bin/env python3
"""capture_friction.py — template-shippable friction-capture hook (UserPromptSubmit).

Implements AGET_FRICTION_SPEC v0.1.0 CAP-FRIC-001 (capture) + CAP-FRIC-002 (persist).

Guarantees that any user message containing a friction marker (note|record|capture|log
+ a typo-tolerant "friction:") is recorded verbatim to a durable, harvestable ledger the
instant it is submitted — independent of whether the assistant remembers to transcribe it
(the L656 structural fix; the L669 capture-choke-point made recall-biased).

PROPAGATION (CAP-FRIC-005-01 — the L1111 root fix): this script lives in TRACKED `scripts/`,
NOT gitignored `.claude/hooks/`. That is the whole point — a friction instrument in a
non-propagating (gitignored) location is single-agent by construction. Shipped here, it
propagates via template to every scaffolded agent. Wire it in `.claude/settings.json`:

    {"hooks": {"UserPromptSubmit": [{"hooks": [
        {"type": "command", "command": "python3 scripts/capture_friction.py"}]}]}}

Contract: never blocks the prompt. Exit 0 always. Silent unless a note was captured.
Self-test (V-FRIC-001): `python3 scripts/capture_friction.py --self-test` (exit 0 = PASS).

Generalized from the dogfooded supervisor instrument (private-supervisor-AGET,
.claude/hooks/capture_friction.py, L656/L669) per PP-052; lane: framework propagation surface.
"""
import json
import os
import re
import sys
from datetime import datetime

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
LEDGER = os.path.join(REPO, "sessions", "FRICTION_LEDGER.md")

# CAP-FRIC-001-02/03: recall-biased marker. A dropped capture is invisible (worst failure);
# an over-capture is cleaned cheaply at harvest. Verbs note/record/capture/log; noun is
# typo-tolerant (f..r..t..) so "friction"/"firction"/"fricton" all match. The verb prefix is
# load-bearing (CAP-FRIC-001-03): it blocks self-capture of quoted "friction:" text.
MARKER = re.compile(r"(?:note|record|capture|log)\s+f\w*r\w*t\w*\s*:\s*(.*)",
                    re.IGNORECASE | re.DOTALL)

LEDGER_HEADER = """# Friction Ledger

Durable, append-only capture of principal-reported friction, auto-recorded by
`scripts/capture_friction.py` (UserPromptSubmit hook). Enhancement-backlog substrate
(AGET_FRICTION_SPEC CAP-FRIC-002 / L656 harvestable corpus).

**Entry format**: `## FRICTION <iso-ts> | session <id> | status: <new|filed #N|wontfix|dedup #N>`
followed by the verbatim note. **Harvest** (CAP-FRIC-003): grep `status: new`, cluster, dedup
against open issues (non-optional, L669), file via `/aget-file-issue`, then update status.
"""


def extract(prompt):
    """Return the verbatim friction text following the marker, or None (CAP-FRIC-001)."""
    m = MARKER.search(prompt)
    if not m:
        return None
    text = m.group(1).strip()
    # If wrapped like "(... note friction: ... )", drop one unbalanced trailing ).
    if text.endswith(")") and text.count("(") < text.count(")"):
        text = text[:-1].rstrip()
    return text or "(marker present but no text followed)"


def append_entry(note, session, ts, ledger=LEDGER):
    """CAP-FRIC-002: persist verbatim to the harvestable ledger with a status field."""
    # CAP-FRIC-006-03/04 (v3.25): the capture surface carries the value-class
    # forward; at capture time the class is by definition untriaged, so the
    # ambiguity fail-safe applies — default `owed` (tracked, never auto-remediated),
    # refined by /aget-record-friction triage at harvest. Never default `avoidable`.
    entry = f"\n## FRICTION {ts} | session {session} | status: new | value-class: owed (pending-triage default, CAP-FRIC-006-04)\n{note}\n"
    os.makedirs(os.path.dirname(ledger), exist_ok=True)
    if not os.path.exists(ledger):
        with open(ledger, "w") as f:
            f.write(LEDGER_HEADER)
    with open(ledger, "a") as f:
        f.write(entry)


def self_test():
    """V-FRIC-001: verb variant + typo captured; no-verb quoted text rejected."""
    cases = [
        ("note friction: X", True),
        ("record friction: own-repo Edit prompted", True),
        ("record firction: typo still caught", True),   # typo-tolerant noun
        ("CAPTURE FRICTION: case-insensitive", True),
        ('he said "friction: foo" in passing', False),  # no verb prefix → not captured
        ("just a normal prompt", False),
    ]
    failures = []
    for prompt, should_match in cases:
        got = extract(prompt) is not None
        if got != should_match:
            failures.append(f"  {prompt!r}: expected match={should_match}, got {got}")
    if failures:
        print("V-FRIC-001 FAIL:\n" + "\n".join(failures))
        return 1
    print("V-FRIC-001 PASS (6/6: verb variants + typo captured; no-verb noise rejected)")
    return 0


def main():
    if "--self-test" in sys.argv:
        return self_test()
    try:
        payload = json.load(sys.stdin)
    except Exception:
        return 0  # malformed input: never block (CAP-FRIC-001 contract)
    note = extract(payload.get("prompt", "") or "")
    if note is None:
        return 0  # no marker: silent pass
    session = (payload.get("session_id") or "unknown")[:8]
    ts = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
    append_entry(note, session, ts)
    # UserPromptSubmit stdout enters the assistant's context — confirm capture so the
    # assistant knows it is logged (CAP-FRIC-001-04 backstop awareness).
    print(f"[friction-capture] logged to sessions/FRICTION_LEDGER.md (status: new) @ {ts}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
