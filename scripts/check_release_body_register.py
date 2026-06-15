#!/usr/bin/env python3
"""
Release-Body Register / Value Check  (R-PUB-001-16)

The conformance validator (validate_release_body_conformance.py, R-PUB-001-15)
checks STRUCTURE — Theme / What's New / Compatibility sections present. It does
NOT check VALUE: a structurally-conformant body can still carry author-register
/ internal-operational content that serves no external reader. (L1081:
conformance != value. Worked instance: the v3.22.0 body shipped a push-window
guard advertisement and a "3.4x-stale gap" dogfooding anecdote while passing
structure conformance.)

This is the value-half gate. It flags KNOWN internal-register leak classes —
content whose value to an external adopter is zero, and which sometimes leaks
internal practice. Precision-first: each pattern targets a concrete observed
class. Extend the registry as new classes are found (mirrors the
sanitize_issue_content.py philosophy at the issue-promotion boundary).

NOT flagged (intentional — principal register, allowed on release bodies per
L944): CAP-NNN / T-IDs / gh#NNN traceability tokens.

OWNING-RUBRIC RECONCILIATION (L954): this script is the AUTOMATED FIRING-HALF of
two human-scored rubrics an instance may carry — it does not replace them, it makes
their mechanically-checkable dimensions fire at release time:
  - a voice-conformance rubric (REQ-HOM-Q-001) — scan_voice() automates its
    mechanical subset (em-dash-leading-bullet, >15-word sentence ratio); the
    interpretive dimensions (tone, principal-register judgement) stay human-scored.
  - a documentation-content-intent rubric — scan_register() automates the
    audience-fit "no internal-register leak" leg.
The interpretive dimensions remain human-scored; this script fires only the
mechanical subset. Pairs with validate_release_body_conformance.py (structure).

Two dimensions, two severities:
  - register leaks  -> BLOCK (precise, zero-adopter-value internal content)
  - voice flags     -> em-dash-leading-bullet BLOCKs; long-sentence ratio is
                       INFORMATIONAL (heuristic, reported not blocked)

Usage:
    python3 check_release_body_register.py --tag v3.22.0
    python3 check_release_body_register.py --file body.md
    cat body.md | python3 check_release_body_register.py --stdin
    python3 check_release_body_register.py --tag v3.22.0 --json
    python3 check_release_body_register.py --self-test

Exit Codes:
    0 - clean (no register leaks, no blocking voice flags)
    1 - one or more BLOCKing flags found (re-author for the reader)
    2 - input error (tag not found / no input)
"""

import argparse
import json
import re
import subprocess
import sys
from dataclasses import dataclass, asdict
from typing import Optional

REPO = "aget-framework/aget"

# Each class maps to: why it has zero value to an external reader.
# Precision-first patterns — targeted at concrete observed leak classes, not
# broad keyword nets. Tune/extend as new classes surface (L1081).
LEAK_PATTERNS = {
    "internal-cadence": (
        re.compile(
            r"(?i)\b(push[- ]window|weekend\s+push|refuses?\s+mon\w*\s*"
            r"(?:through|to|[-–])\s*fri\w*|Monday\s+through\s+Friday|Mon[–-]Fri)\b"
        ),
        "advertises the internal weekend-push cadence (L735); no adopter value",
    ),
    "session-narrative": (
        re.compile(r"(?i)\b(dogfood\w*|(?:its\s+)?first\s+live\s+run)\b"),
        "session/dogfooding war-story; belongs in a retrospective, not a release page",
    ),
    "stale-metric-anecdote": (
        re.compile(
            r"(?i)(\d+(?:\.\d+)?\s*[×x]\s*-?\s*stale|stale[- ]gap|gap\s+headline)"
        ),
        "references an internal metric meaningless to an external reader",
    ),
    "internal-workspace-path": (
        re.compile(r"workspace/[\w./-]+\.(?:jsonl|json|md)"),
        "exposes an internal workspace file path with no adopter value",
    ),
}


@dataclass
class Leak:
    leak_class: str
    match: str
    reason: str


def scan_register(body: str) -> list[Leak]:
    """Return all internal-register leaks found in a release body (pure, testable)."""
    leaks: list[Leak] = []
    for leak_class, (pattern, reason) in LEAK_PATTERNS.items():
        for m in pattern.finditer(body or ""):
            leaks.append(Leak(leak_class=leak_class, match=m.group(0).strip(), reason=reason))
    return leaks


@dataclass
class VoiceFlag:
    flag_class: str
    match: str
    reason: str
    blocking: bool


# REQ-HOM-Q-001 voice rules — the mechanical subset of RUBRIC_voice_conformance.
# "No em-dash compound clauses LEADING bullets." Precision matters: an em-dash in
# CONTEXT (after a bold plain-language outcome or a completed sentence) is fine;
# only an em-dash in the LEAD clause is the anti-pattern. So a bullet is flagged
# only when an em-dash appears before any closed `**bold**` lead AND before the
# first sentence period — i.e., the em-dash is genuinely leading.
_BULLET_LINE = re.compile(r"(?m)^\s*[-*]\s+(.*)$")
_CLOSED_BOLD = re.compile(r"\*\*[^*]+\*\*")
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+")


def _emdash_leads_bullet(line: str) -> bool:
    """True iff an em-dash leads the bullet (no bold lead / no period precedes it)."""
    m = re.search(r"[—–]", line)
    if not m:
        return False
    before = line[: m.start()]
    if _CLOSED_BOLD.search(before):   # a plain-language bold outcome already led
        return False
    if "." in before:                  # a sentence completed before the em-dash
        return False
    return True
LONG_SENTENCE_WORDS = 15
LONG_SENTENCE_RATIO_THRESHOLD = 0.20  # REQ-HOM-Q-001: <20% of sentences > 15 words


def _strip_markdown(body: str) -> str:
    """Drop code spans, links-to-bare-text, and md markers so sentence/word counts
    reflect prose, not syntax. Best-effort, not a full parser."""
    text = re.sub(r"`[^`]*`", " ", body or "")          # inline code
    text = re.sub(r"\*\*|\*|_|#+|>", " ", text)            # emphasis / headers / quotes
    text = re.sub(r"\[([^\]]*)\]\([^)]*\)", r"\1", text)   # links -> link text
    return text


def scan_voice(body: str) -> list[VoiceFlag]:
    """Return REQ-HOM-Q-001 voice flags (pure, testable). Automatable subset of
    RUBRIC_voice_conformance; interpretive dimensions stay human-scored."""
    flags: list[VoiceFlag] = []

    for m in _BULLET_LINE.finditer(body or ""):
        line = m.group(1)
        if _emdash_leads_bullet(line):
            flags.append(VoiceFlag(
                flag_class="em-dash-leading-bullet",
                match=line.strip()[:60],
                reason="REQ-HOM-Q-001: bullet lead clause uses an em-dash compound; "
                       "lead with a plain-language outcome instead",
                blocking=True,
            ))

    # RUBRIC_documentation_content_intent D1: name the intended reader. Advisory
    # (INFORMATIONAL) — not a hard marker, so it never retroactively blocks past bodies.
    if not re.search(r"(?im)^\s*\**For\**\s*[:\-—]", body or ""):
        flags.append(VoiceFlag(
            flag_class="missing-for-reader-line",
            match="no `**For**:` reader line",
            reason="RUBRIC_documentation_content_intent D1: name the intended reader "
                   "(e.g. 'For: maintainers upgrading from vX') — INFORMATIONAL, not blocked",
            blocking=False,
        ))

    prose = _strip_markdown(body)
    sentences = [s for s in _SENTENCE_SPLIT.split(prose) if s.strip()]
    if sentences:
        long_sentences = [s for s in sentences if len(s.split()) > LONG_SENTENCE_WORDS]
        ratio = len(long_sentences) / len(sentences)
        if ratio > LONG_SENTENCE_RATIO_THRESHOLD:
            flags.append(VoiceFlag(
                flag_class="long-sentence-ratio",
                match=f"{len(long_sentences)}/{len(sentences)} sentences > "
                      f"{LONG_SENTENCE_WORDS} words ({ratio:.0%})",
                reason=f"REQ-HOM-Q-001: keep <{LONG_SENTENCE_RATIO_THRESHOLD:.0%} of "
                       f"sentences over {LONG_SENTENCE_WORDS} words (INFORMATIONAL — "
                       f"heuristic, not blocked)",
                blocking=False,
            ))

    return flags


def fetch_release_body(tag: str) -> Optional[str]:
    try:
        result = subprocess.run(
            ["gh", "release", "view", tag, "--repo", REPO, "--json", "body", "-q", ".body"],
            capture_output=True, text=True, check=True,
        )
        return result.stdout
    except subprocess.CalledProcessError:
        return None


def _self_test() -> int:
    bad = (
        "**Theme**: X\n## What's New\n- deployer with a push-window guard in "
        "`--apply` (refuses Monday through Friday) and live gap re-derivation. "
        "Its first live run corrected a 3.4x-stale gap headline, dogfooding the "
        "theme. Audit log at workspace/skill_deploy_audit.jsonl.\n## Compatibility\nNo breaking."
    )
    good = (
        "**Theme**: X\n## What's New\n- **Surgical skill deployer.** Per-skill "
        "filtering, dry-run default, audit log, independent post-deploy verify.\n"
        "## Compatibility\nNo breaking changes. *Traceability: deploy_skill.py, gh#1120*"
    )
    bad_leaks = scan_register(bad)
    good_leaks = scan_register(good)
    bad_classes = {l.leak_class for l in bad_leaks}
    assert "internal-cadence" in bad_classes, "should flag push-window/Mon-Fri"
    assert "session-narrative" in bad_classes, "should flag dogfooding/first-live-run"
    assert "stale-metric-anecdote" in bad_classes, "should flag 3.4x-stale gap headline"
    assert "internal-workspace-path" in bad_classes, "should flag workspace/*.jsonl"
    assert good_leaks == [], f"clean body should pass, got {good_leaks}"

    # voice (REQ-HOM-Q-001) — em-dash-leading bullet must block
    emdash_body = "**Theme**: X\n## What's New\n- the deployer — surgical and governed — ships.\n## Compatibility\nNo breaking."
    plain_body = "**Theme**: X\n## What's New\n- **Surgical deployer ships.** It is governed.\n## Compatibility\nNo breaking."
    emdash_flags = scan_voice(emdash_body)
    assert any(f.flag_class == "em-dash-leading-bullet" and f.blocking for f in emdash_flags), \
        "should block em-dash-leading bullet"
    assert not any(f.blocking for f in scan_voice(plain_body)), "plain bullets should not block"

    print("self-test PASS: 4 register leak classes + em-dash-leading-bullet block on "
          "known-bad; clean/plain bodies pass")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser(description="Release-body register/value check (R-PUB-001-16)")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--tag", help="release tag, e.g. v3.22.0 (fetched from aget-framework/aget)")
    group.add_argument("--file", help="path to a release-body file")
    group.add_argument("--stdin", action="store_true", help="read body from stdin")
    group.add_argument("--self-test", action="store_true", help="run built-in self-test")
    parser.add_argument("--json", action="store_true", help="emit JSON")
    args = parser.parse_args()

    if args.self_test:
        return _self_test()

    if args.tag:
        body = fetch_release_body(args.tag)
        if body is None:
            print(f"ERROR: release {args.tag} not found in {REPO}", file=sys.stderr)
            return 2
        label = args.tag
    elif args.file:
        try:
            with open(args.file) as f:
                body = f.read()
        except OSError as e:
            print(f"ERROR: {e}", file=sys.stderr)
            return 2
        label = args.file
    else:
        body = sys.stdin.read()
        label = "<stdin>"

    leaks = scan_register(body)
    voice_flags = scan_voice(body)
    blocking_voice = [f for f in voice_flags if f.blocking]
    info_voice = [f for f in voice_flags if not f.blocking]
    blocking = bool(leaks) or bool(blocking_voice)

    if args.json:
        print(json.dumps({
            "label": label,
            "clean": not blocking,
            "leaks": [asdict(l) for l in leaks],
            "voice_flags": [asdict(f) for f in voice_flags],
        }, indent=2))
    else:
        if not blocking:
            print(f"CLEAN: {label} — no register leaks, no blocking voice flags")
        else:
            print(f"FAIL: {label} — {len(leaks)} register leak(s), "
                  f"{len(blocking_voice)} blocking voice flag(s):")
            for l in leaks:
                print(f"  [BLOCK {l.leak_class}] \"{l.match}\" — {l.reason}")
            for f in blocking_voice:
                print(f"  [BLOCK {f.flag_class}] \"{f.match}\" — {f.reason}")
        for f in info_voice:
            print(f"  [info {f.flag_class}] {f.match} — {f.reason}")

    return 1 if blocking else 0


if __name__ == "__main__":
    sys.exit(main())
