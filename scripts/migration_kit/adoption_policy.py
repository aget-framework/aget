#!/usr/bin/env python3
"""adoption_policy.py — the receiving supervisor's adoption policy: when to adopt a release, how far behind its fleet
may fall, how long the pilots soak, and when a batch halts.

WHY THIS EXISTS
    A remote supervisor applying a release had no written answer to "should I adopt this now?", no bound on how far its
    own members may lag, and no signal that stops a batch inside a wave. The producer had all three for its own fleet
    (a three-minor skew block, a two-minor currency flag, wave rules), but none of it was in the kit. This module is the
    single place a receiver declares its policy. The receiver owns the values; the kit only supplies defaults.

RESOLUTION (first found wins, per key — the same order as release_target.py; allowlist lists extend defaults)
    1. environment: AGET_ADOPTION_SKEW_BLOCKED_AT, AGET_ADOPTION_SKEW_FLAGGED_AT, AGET_ADOPTION_MIN_RELEASE_AGE_DAYS,
       AGET_ADOPTION_PATCH_POLICY, AGET_ADOPTION_WAVE1_SOAK_HOURS, AGET_ADOPTION_WAVE1_SOAK_SESSIONS,
       AGET_ADOPTION_HALT_MAX_AGENTS_MD_LINES
    2. <root>/.aget/adoption_policy.json, for example:
       {"skew": {"blocked_at": 3, "flagged_at": 2}, "min_release_age_days": 7, "patch_policy": "adopt-if-fixes-me",
        "wave1_soak": {"min_hours": 24, "min_sessions": 1},
        "halt": {"max_agents_md_changed_lines": 10, "identity_patterns": ["^# ", "^\\*\\*Name\\*\\*:"],
                 "allowed_change_patterns": ["^@aget-version: \\d+\\.\\d+\\.\\d+$", "^@aget-canonical-specs: https://github\\.com/aget-framework/aget/tree/v\\d+\\.\\d+\\.\\d+/specs(?: — reliance-only conformance(?: \\(D-1, 2026-07-04\\): this template runs the version's features; specs are canonical-referenced, not copied locally)?)?$"]}}
    3. the producer defaults below. Every value reports which of the three it came from, so a receiver that declared
       nothing is told the defaults were applied rather than left to assume it chose them.

DEFAULTS AND THEIR STANDING
    skew 3 / 2       the producer's own bounds (block the next upgrade at three published minors behind; flag at two).
                     Ruled as the receiver default.
    the others       producer proposals, each derived from the 2026-07-26..10-14 fleet history. They are open to change at
                     the next scope lock; a receiver may override any of them today.
        min_release_age_days 7: in the two migrations that were rolled back, the defect surfaced within six days of
                     publication. A receiver that waits a week adopts after the producer's own fleet has acted as its
                     canary.
        patch_policy "adopt-if-fixes-me": four of twelve releases in that period were never taken up by any wave; a
                     patch is worth a migration only when it repairs something the receiver has.
        wave1_soak 24 h and 1 session: the procedure's "at least one session", made measurable.
        halt 10 lines: a correct payload changes AGENTS.md by its pin lines (2 to 4 lines added plus removed in the
                     correct migrations replayed with halt_check.py, against 831 to 995 in the applier commits they
                     repaired). Identity lines never change in a correct migration.
        halt.allowed_change_patterns ["^@aget-version: \\d+\\.\\d+\\.\\d+$", "^@aget-canonical-specs: https://github\\.com/aget-framework/aget/tree/v\\d+\\.\\d+\\.\\d+/specs(?: — reliance-only conformance(?: \\(D-1, 2026-07-04\\): this template runs the version's features; specs are canonical-referenced, not copied locally)?)?$"]: every added or removed line must
                     match an allowed pattern; blank-line changes halt by default. Identity and size remain extra
                     stop signals even when all changed lines are allowed. File declarations EXTEND these pin
                     patterns, with duplicates removed in order; they cannot accidentally remove default pins.

Usage
-----
    python3 scripts/migration_kit/adoption_policy.py --show            # resolved policy, with sources, as JSON
    python3 scripts/migration_kit/adoption_policy.py --check-age --published 2026-10-10 [--today 2026-10-15]
        [--release X.Y.Z [--fixes-me]]

--check-age answers "may this release be adopted now?" under the policy: old enough (min_release_age_days), and,
for a patch release (Z > 0, given with --release), allowed by patch_policy: `always` adopts it, `never-alone` never
adopts a patch on its own (wait for the next minor), and `adopt-if-fixes-me` adopts it only when the supervisor
passes --fixes-me after reading the release notes. halt.identity_patterns and halt.allowed_change_patterns can be
declared only in the file.
Both regex lists are limited to 256 characters per pattern and 4096 characters per input line.
Each search/fullmatch (including validation probes) has a 50 ms wall-clock deadline. Exceeding a limit refuses
the policy or makes halt_check UNAVAILABLE. The POSIX timer requires the main thread and no existing alarm;
when that guard cannot be installed, matching refuses rather than running without a deadline.

Exit codes: 0 valid (or adopt now), 1 wait or skip, 2 invalid policy or unreadable input.
"""
from __future__ import annotations

import argparse
import copy
import datetime as dt
import json
import os
import re
import signal
import sys
import threading
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # <root>/scripts/migration_kit/adoption_policy.py
CONFIG_NAME = ".aget/adoption_policy.json"
PATCH_POLICIES = ("adopt-if-fixes-me", "always", "never-alone")
MAX_PATTERN_CHARS = 256
MAX_MATCH_LINE_CHARS = 4096
MATCH_SECONDS = 0.05

DEFAULTS = {
    "skew": {"blocked_at": 3, "flagged_at": 2},
    "min_release_age_days": 7,
    "patch_policy": "adopt-if-fixes-me",
    "wave1_soak": {"min_hours": 24, "min_sessions": 1},
    "halt": {
        "max_agents_md_changed_lines": 10,
        "identity_patterns": [r"^# ", r"^\s*(?:[-*]\s+)?\*\*(?:Name|Type|Purpose|Domain)(?:\*\*:|:\*\*)"],
        # Pin forms: handoffs/REMOTE_MIGRATION_MESSAGE_v3.25.0.md:16 and
        # handoffs/CORRECTIONS_v3.28.0.md:449-450; SOP_fleet_migration.md B7 names the URL ref.
        "allowed_change_patterns": [
            r"^@aget-version: \d+\.\d+\.\d+$",
            r"^@aget-canonical-specs: https://github\.com/aget-framework/aget/tree/v\d+\.\d+\.\d+/specs(?: — reliance-only conformance(?: \(D-1, 2026-07-04\): this template runs the version's features; specs are canonical-referenced, not copied locally)?)?$",
        ],
    },
}
RULED = {"skew.blocked_at", "skew.flagged_at"}       # default ruled by the principal; every other default is a proposal

_ENV = {
    "skew.blocked_at": ("AGET_ADOPTION_SKEW_BLOCKED_AT", int),
    "skew.flagged_at": ("AGET_ADOPTION_SKEW_FLAGGED_AT", int),
    "min_release_age_days": ("AGET_ADOPTION_MIN_RELEASE_AGE_DAYS", int),
    "patch_policy": ("AGET_ADOPTION_PATCH_POLICY", str),
    "wave1_soak.min_hours": ("AGET_ADOPTION_WAVE1_SOAK_HOURS", int),
    "wave1_soak.min_sessions": ("AGET_ADOPTION_WAVE1_SOAK_SESSIONS", int),
    "halt.max_agents_md_changed_lines": ("AGET_ADOPTION_HALT_MAX_AGENTS_MD_LINES", int),
}
_KEYS = list(_ENV) + ["halt.identity_patterns", "halt.allowed_change_patterns"]


class PolicyError(ValueError):
    """The declared policy is unreadable or invalid."""


class RegexLimitError(ValueError):
    """A regex evaluation could not run within the declared resource limits."""


def compile_pattern(pattern: str):
    if len(pattern) > MAX_PATTERN_CHARS:
        raise RegexLimitError(f"pattern exceeds {MAX_PATTERN_CHARS} characters")
    return re.compile(pattern)


def bounded_match(reg, line: str, *, full: bool = False) -> bool:
    """Evaluate a single regex with length caps and a POSIX wall-clock deadline; never replace an active alarm."""
    if len(line) > MAX_MATCH_LINE_CHARS:
        raise RegexLimitError(f"input line exceeds {MAX_MATCH_LINE_CHARS} characters")
    if threading.current_thread() is not threading.main_thread() or not hasattr(signal, "setitimer"):
        raise RegexLimitError("regex deadline requires POSIX timers in the main thread")
    if signal.getitimer(signal.ITIMER_REAL)[0]:
        raise RegexLimitError("regex deadline cannot replace an existing alarm")

    def expired(signum, frame):
        raise RegexLimitError(f"regex deadline exceeded ({MATCH_SECONDS:g} seconds)")

    previous = signal.signal(signal.SIGALRM, expired)
    try:
        signal.setitimer(signal.ITIMER_REAL, MATCH_SECONDS)
        return (reg.fullmatch(line) if full else reg.search(line)) is not None
    finally:
        signal.setitimer(signal.ITIMER_REAL, 0)
        signal.signal(signal.SIGALRM, previous)


_MISSING = object()


def _dig(d: dict, dotted: str, default=None):
    cur = d
    for part in dotted.split("."):
        if not isinstance(cur, dict) or part not in cur:
            return default
        cur = cur[part]
    return cur


def _put(d: dict, dotted: str, value) -> None:
    parts = dotted.split(".")
    for part in parts[:-1]:
        d = d.setdefault(part, {})
    d[parts[-1]] = value


_SECTIONS = {"skew", "wave1_soak", "halt"}
_TOP = {"skew", "min_release_age_days", "patch_policy", "wave1_soak", "halt"}
_SUB = {"skew": {"blocked_at", "flagged_at"}, "wave1_soak": {"min_hours", "min_sessions"},
        "halt": {"max_agents_md_changed_lines", "identity_patterns", "allowed_change_patterns"}}


def _shape_errors(cfg: dict) -> list[str]:
    """Unknown keys and non-object sections are errors: a misspelled key must not silently fall back to a default."""
    errs = [f"unknown key {k!r}" for k in cfg if k not in _TOP]
    for sec in _SECTIONS:
        if sec in cfg:
            if not isinstance(cfg[sec], dict):
                errs.append(f"{sec!r} must be an object")
            else:
                errs += [f"unknown key {sec}.{k}" for k in cfg[sec] if k not in _SUB[sec]]
    return errs


def load(root: Path | str = ROOT, env: dict | None = None) -> dict:
    """Return {"policy": {...}, "sources": {key: "env"|"file"|"default"}, "config": path, "defaults_ruled": [...]}.

    Raises PolicyError when the file exists but cannot be parsed, or when a resolved value is invalid. An absent file is
    not an error: the defaults apply and every source says so. A file's allowed_change_patterns extends the default
    pins (ordered, deduplicated), while other declared keys replace their defaults. Its source is 'file' when any
    extras were declared, even though default pins are retained."""
    env = os.environ if env is None else env
    path = Path(os.path.expanduser(str(root))) / CONFIG_NAME
    cfg: dict = {}
    if path.exists() and not path.is_file():
        raise PolicyError(f"{path}: exists but is not a regular file")
    if path.is_file():
        try:
            cfg = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, ValueError) as exc:
            raise PolicyError(f"{path}: unreadable ({type(exc).__name__})") from None
        if not isinstance(cfg, dict):
            raise PolicyError(f"{path}: top level must be an object")
        shape = _shape_errors(cfg)
        if shape:
            raise PolicyError(f"{path}: " + "; ".join(shape))
    policy = copy.deepcopy(DEFAULTS)
    sources = {}
    for key in _KEYS:
        env_name, cast = _ENV.get(key, (None, None))
        raw_env = env.get(env_name) if env_name else None
        if raw_env not in (None, ""):
            try:
                _put(policy, key, cast(raw_env))
            except ValueError:
                raise PolicyError(f"{env_name}={raw_env!r}: not a valid {cast.__name__}") from None
            sources[key] = "env"
        elif _dig(cfg, key, _MISSING) is not _MISSING:
            _put(policy, key, _dig(cfg, key))                   # a declared null is kept, and refused by validate()
            sources[key] = "file"
        else:
            sources[key] = "default"
    errors = validate(policy)
    if errors:
        raise PolicyError("; ".join(errors))
    if sources["halt.allowed_change_patterns"] == "file":
        # Validate declarations first: merging must not disguise an invalid empty list or null.
        policy["halt"]["allowed_change_patterns"] = list(dict.fromkeys(
            DEFAULTS["halt"]["allowed_change_patterns"] + policy["halt"]["allowed_change_patterns"]))
    return {"policy": policy, "sources": sources, "config": str(path), "config_present": path.is_file(),
            "defaults_ruled": sorted(RULED), "defaults_proposed": sorted(set(_KEYS) - RULED)}


def validate(policy: dict) -> list[str]:
    """Return problems with a resolved policy (empty when valid).

    Refuse an allowed-change pattern if it fullmatches the empty string OR every arbitrary-line probe
    ('x', '# Agent Instructions'). These declarations would disable the fence or allow blank-line edits;
    this conservative probe check is not a proof that every other pattern is narrow. Both regex lists use
    the 256-character pattern cap and bounded_match's line cap/deadline, including these probes.
    """
    errs = []
    for key in _ENV:
        v = _dig(policy, key)
        if key == "patch_policy":
            if v not in PATCH_POLICIES:
                errs.append(f"patch_policy {v!r} not one of {', '.join(PATCH_POLICIES)}")
        elif not isinstance(v, int) or isinstance(v, bool) or v < 0:
            errs.append(f"{key} must be a non-negative integer (got {v!r})")
    b, f = _dig(policy, "skew.blocked_at"), _dig(policy, "skew.flagged_at")
    if isinstance(b, int) and isinstance(f, int) and not isinstance(b, bool):
        if b < 1:
            errs.append("skew.blocked_at must be at least 1")
        if f > b:
            errs.append(f"skew.flagged_at ({f}) must not exceed skew.blocked_at ({b})")
    for key in ("halt.identity_patterns", "halt.allowed_change_patterns"):
        pats = _dig(policy, key)
        if not isinstance(pats, list) or not pats or not all(isinstance(p, str) and p for p in pats):
            errs.append(f"{key} must be a non-empty list of strings")
        else:
            for p in pats:
                try:
                    reg = compile_pattern(p)
                    if key == "halt.allowed_change_patterns" and (
                            bounded_match(reg, "", full=True) or all(
                                bounded_match(reg, s, full=True) for s in ("x", "# Agent Instructions"))):
                        errs.append(f"{key}: {p!r} is overly broad (matches empty or arbitrary probe lines)")
                except re.error as exc:
                    errs.append(f"{key}: {p!r} is not a valid pattern ({exc})")
                except RegexLimitError as exc:
                    errs.append(f"{key}: {exc}")
    return errs


def release_age_days(published: dt.date, today: dt.date) -> int:
    return (today - published).days


def check_age(published: dt.date, today: dt.date, min_days: int) -> tuple[bool, int]:
    """(old_enough, age_in_days). A release published in the future is never old enough."""
    age = release_age_days(published, today)
    return (age >= 0 and age >= min_days, age)


def patch_decision(release: str, patch_policy: str, fixes_me: bool) -> tuple[bool, str]:
    """(may_adopt, reason) for the patch rule. A non-patch release (X.Y.0) always passes this rule."""
    import re
    m = re.fullmatch(r"(\d+)\.(\d+)\.(\d+)", (release or "").strip())
    if not m:
        raise PolicyError(f"release {release!r} is not X.Y.Z")
    if int(m.group(3)) == 0:
        return True, "not a patch release"
    if patch_policy == "always":
        return True, "patch release; patch_policy always"
    if patch_policy == "never-alone":
        return False, "patch release; patch_policy never-alone: wait for the next minor release"
    if fixes_me:
        return True, "patch release; --fixes-me given under adopt-if-fixes-me"
    return False, ("patch release; patch_policy adopt-if-fixes-me: read its notes and pass --fixes-me only if it "
                   "repairs something this fleet has")


def _date(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Resolve and check the receiving supervisor's adoption policy.")
    ap.add_argument("--root", default=str(ROOT), help="repository root holding .aget/adoption_policy.json")
    g = ap.add_mutually_exclusive_group(required=True)
    g.add_argument("--show", action="store_true", help="print the resolved policy and each value's source")
    g.add_argument("--check-age", action="store_true", help="is the release old enough to adopt under the policy?")
    ap.add_argument("--published", help="the release's publication date, YYYY-MM-DD (with --check-age)")
    ap.add_argument("--today", help="override today's date, YYYY-MM-DD (with --check-age)")
    ap.add_argument("--release", help="the release version, X.Y.Z (with --check-age; applies the patch policy)")
    ap.add_argument("--fixes-me", action="store_true", help="the patch repairs something this fleet has")
    a = ap.parse_args(argv)
    try:
        res = load(a.root)
    except PolicyError as exc:
        print(f"adoption policy: INVALID — {exc}", file=sys.stderr)
        return 2
    if a.show:
        print(json.dumps(res, indent=1))
        if not res["config_present"]:
            print(f"adoption policy: no {CONFIG_NAME} at {a.root}; producer defaults applied", file=sys.stderr)
        return 0
    if not a.published:
        print("adoption policy: --check-age needs --published YYYY-MM-DD", file=sys.stderr)
        return 2
    try:
        published = _date(a.published)
        today = _date(a.today) if a.today else dt.date.today()
    except ValueError as exc:
        print(f"adoption policy: bad date ({exc})", file=sys.stderr)
        return 2
    min_days = res["policy"]["min_release_age_days"]
    ok, age = check_age(published, today, min_days)
    src = res["sources"]["min_release_age_days"]
    print(f"release age {age} day(s); minimum {min_days} ({src}) -> {'OLD ENOUGH' if ok else 'WAIT'}")
    if a.release:
        try:
            pok, why = patch_decision(a.release, res["policy"]["patch_policy"], a.fixes_me)
        except PolicyError as exc:
            print(f"adoption policy: {exc}", file=sys.stderr)
            return 2
        print(f"patch rule: {why} ({res['sources']['patch_policy']}) -> {'ALLOWED' if pok else 'SKIP'}")
        ok = ok and pok
    print("ADOPT NOW" if ok else "DO NOT ADOPT YET")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
