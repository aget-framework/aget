#!/usr/bin/env python3
"""halt_check.py — after a member is migrated, decide whether the batch must stop.

WHY THIS EXISTS
    A batch applier once rewrote the identity in nineteen members' AGENTS.md before anyone read the damage; replayed
    with this tool, its commits at three of those members changed 831 to 995 lines where a correct payload changes its
    pin lines. The procedure's wave rules stop at a wave boundary; nothing stopped a batch inside a wave. This tool is
    that stop. In the kit's batch procedure it runs on every member right after the apply (step B7a), and a HALT or
    UNAVAILABLE stops the batch before any session or push. With an applier that migrates one member at a time, run it
    after each member and do not start the next one on a HALT.

WHAT IT COMPARES
    The member's AGENTS.md at the commit before the migration (--before) against AGENTS.md now: the working tree, or
    --after <commit> to replay a past migration. Three signals, all from adoption_policy.py (halt.*):
      allowlist  every added or removed line in a line diff must match halt.allowed_change_patterns (default
                 whole-line version X.Y.Z and canonical-specs URL pins, with the fixed optional suffix
                 " — reliance-only conformance", itself optionally followed by the templates' fixed long form
                 " (D-1, 2026-07-04): this template runs the version's features; specs are canonical-referenced,
                 not copied locally"). Every allowed pattern uses fullmatch, never a prefix search.
                 Any other changed line halts, including blank lines
                 by default: a correct payload replaces pin lines in place. A receiver can declare extra patterns
                 only in .aget/adoption_policy.json; declarations EXTEND the defaults, deduplicated in order.
                 The JSON report's offending_lines lists the first five offending
                 lines (removed then added within each diff hunk), each truncated to 200 characters.
      identity   the lines matching halt.identity_patterns (by default the first-level heading and the Name / Type /
                 Purpose / Domain label lines, written as `**Name**:`, `- **Name**:` or `**Name:**`), in order.
                 When only the heading matched, the report says so: declare a pattern for the member's own name line. Any addition, removal or change halts. When no
                 line matched before the migration, identity cannot be verified and the verdict is UNAVAILABLE:
                 declare patterns that match this member's file.
      size       more than halt.max_agents_md_changed_lines lines added plus removed (default 10; a changed line
                 counts as one removed and one added).
    CLAUDE.md is also checked: file/link transitions, additions and deletions halt, and a regular file uses the same
    allowlist, identity and size checks (without requiring identity labels in a supplemental file). A symlink to
    AGENTS.md on both sides adds nothing. Other symlink targets are UNAVAILABLE unless changed, which HALTs.
    The JSON report's claude_md contains its separate comparison; changed_lines and identity_* at the top level
    describe AGENTS.md, while offending_lines and reasons also include CLAUDE.md violations.
    limits_source maps max_agents_md_changed_lines, identity_patterns and allowed_change_patterns to their
    resolved source ('default', 'file', or 'env'; patterns are file-only). For allowed_change_patterns, 'file' means
    the resolved list includes the file's extras as well as default pins, not that the defaults were replaced.
    Regex evaluation uses adoption_policy's caps: 256 characters per pattern, 4096 per input line, 50 ms per
    search/fullmatch for both identity and allowlist checks. A limit breach is UNAVAILABLE, never CONTINUE.
    The deadline requires POSIX timers in the main thread with no existing alarm; unavailable guards refuse.
    AGENTS.md changing between a regular file and a symbolic link halts. A link is followed inside the member (git
    stores a link's target path, not the instructions). The commit is read with a path relative to the member
    (`<commit>:./AGENTS.md`, git 2.11 or later), so a member nested inside a larger repository is compared correctly.

Usage
-----
    python3 scripts/migration_kit/halt_check.py --member <path> --before <commit> [--after <commit>] [--json]

Exit codes: 0 CONTINUE, 1 HALT, 2 UNAVAILABLE (the commit or AGENTS.md could not be read, or identity could not be
verified, or AGENTS.md is not valid UTF-8; treat it as a stop, never as a pass).
"""
from __future__ import annotations

import argparse
import difflib
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
ABSENT = object()                                     # the commit exists and has no AGENTS.md


def _load(name, path):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AP = _load("kit_adoption_policy_halt", HERE / "adoption_policy.py")
CI = _load("kit_copy_isolation_halt", HERE / "copy_isolation.py")


class Undecodable(ValueError):
    """AGENTS.md is not valid UTF-8; comparing replacement characters would hide real changes."""


def _git(member: Path, *args: str) -> subprocess.CompletedProcess | None:
    """A read of a live member through the kit's shared reader: no optional lock, no lazy fetch, a private index copy,
    so the member's git folder is left as it was. stdout stays bytes; the caller decodes it strictly."""
    try:
        return CI.read_git(member, *args, timeout=60)
    except (OSError, subprocess.TimeoutExpired):
        return None


def _decode(b: bytes, name: str = "AGENTS.md") -> str:
    try:
        return b.decode("utf-8")
    except UnicodeDecodeError as exc:
        raise Undecodable(f"{name} is not valid UTF-8 ({exc.reason} at byte {exc.start})") from None


def commit_exists(member: Path, commit: str) -> bool:
    r = _git(member, "cat-file", "-e", f"{commit}^{{commit}}")
    return r is not None and r.returncode == 0


def agents_md_at(member: Path, commit: str, name: str = "AGENTS.md", _depth: int = 0, *, follow_links: bool = True):
    """(text, is_link) of AGENTS.md at the commit, relative to the member. ABSENT when the commit has no such file;
    None when it cannot be read. A git symbolic link (mode 120000) is followed inside the member, at most two links.
    With follow_links=False return the raw link target instead, for CLAUDE.md's mirror check."""
    ls = _git(member, "ls-tree", commit, "--", f"./{name}")
    if ls is None or ls.returncode != 0:
        return None
    if not ls.stdout.strip():
        return ABSENT
    out = _git(member, "show", f"{commit}:./{name}")
    if out is None or out.returncode != 0:
        return None
    if not follow_links:
        return (_decode(out.stdout, name), ls.stdout.split()[0] == b"120000")
    if ls.stdout.split()[0] == b"120000":
        target = _decode(out.stdout).strip() if out.stdout else ""
        # a relative link target resolves against the folder holding the link, never the member root
        resolved = os.path.normpath(os.path.join(os.path.dirname(name), target)) if target else ""
        if (_depth >= 2 or not target or target.startswith("/") or resolved.startswith("..")
                or os.path.isabs(resolved)):
            return None
        res = agents_md_at(member, commit, resolved, _depth + 1)
        return res if (res is None or res is ABSENT) else (res[0], True)
    return (_decode(out.stdout), _depth > 0)


def git_lines(text: str) -> list[str]:
    """Split on LF only, normalizing CRLF; other Unicode/control separators remain line content."""
    lines = text.split("\n")
    if lines[-1] == "":
        lines.pop()  # a final LF terminates a line; it does not add a blank line
    return [line.removesuffix("\r") for line in lines]


def identity_lines(text: str, patterns: list[str]) -> list[str]:
    """Every line matching the identity patterns, in order, each prefixed with its line number ("12: **Name**: x").

    Deliberately not Markdown-aware: three successive attempts to skip fenced code blocks each let a real identity
    change pass. And identity is compared by position as well as text: comparing text alone let a swap pass (the name
    in prose and a name in a code example exchanged places, leaving the same set of lines). A correct payload replaces
    pin lines in place, so identity lines keep their numbers; a move halts. Both choices can only cause a false HALT,
    the safe direction."""
    regs = [AP.compile_pattern(p) for p in patterns]
    return [f"{i}: {ln}" for i, ln in enumerate(git_lines(text), 1) if any(AP.bounded_match(r, ln) for r in regs)]


def changed_lines(before: str, after: str) -> list[str]:
    """Added and removed lines, including blank lines; a replacement contributes both sides."""
    a, b = git_lines(before), git_lines(after)
    lines = []
    for tag, i1, i2, j1, j2 in difflib.SequenceMatcher(None, a, b, autojunk=False).get_opcodes():
        if tag != "equal":
            lines.extend(a[i1:i2])
            lines.extend(b[j1:j2])
    return lines


def compare(before: str, after: str, patterns: list[str], max_lines: int,
            allowed_patterns: list[str] | None = None, *, require_identity: bool = True,
            name: str = "AGENTS.md") -> dict:
    """Compare with bounded regex evaluation; an exhausted/unavailable guard always stops the batch."""
    try:
        return _compare(before, after, patterns, max_lines, allowed_patterns,
                        require_identity=require_identity, name=name)
    except AP.RegexLimitError as exc:
        return {"verdict": "UNAVAILABLE", "reasons": [], "offending_lines": [],
                "unavailable_reason": f"{name}: {exc}"}


def _compare(before: str, after: str, patterns: list[str], max_lines: int,
             allowed_patterns: list[str] | None, *, require_identity: bool, name: str) -> dict:
    ib, ia = identity_lines(before, patterns), identity_lines(after, patterns)
    lines = changed_lines(before, after)
    n = len(lines)
    regs = [AP.compile_pattern(p) for p in (AP.DEFAULTS["halt"]["allowed_change_patterns"]
                                   if allowed_patterns is None else allowed_patterns)]
    offending = []
    for line in lines:
        if not any(AP.bounded_match(r, line, full=True) for r in regs):
            offending.append(line[:200])
            if len(offending) == 5:
                break
    rep = {"changed_lines": n, "max_changed_lines": max_lines, "identity_before": ib, "identity_after": ia,
           "offending_lines": offending}
    if ib and all(ln.split(": ", 1)[1].startswith("# ") for ln in ib):
        rep["identity_coverage"] = ("heading only: no other identity line matched; declare halt.identity_patterns "
                                    "for this member's name line to protect it")
    if not ib and require_identity:
        rep.update({"verdict": "UNAVAILABLE", "reasons": [],
                    "unavailable_reason": "no identity line matched before the migration; declare "
                                          "halt.identity_patterns that match this member's AGENTS.md"})
        return rep
    reasons = []
    if offending:
        reasons.append(f"{name} line changed outside the allowed patterns: {offending[0]!r}")
    if ib != ia:
        reasons.append("identity lines changed" if name == "AGENTS.md" else f"{name} identity lines changed")
    if n > max_lines:
        reasons.append(f"{n} {name} lines changed (limit {max_lines})")
    rep.update({"verdict": "HALT" if reasons else "CONTINUE", "reasons": reasons})
    return rep


def compare_claude(member: Path, before_commit: str, after_commit: str | None, halt: dict) -> dict:
    """Compare the CLI's mirror without following a symlink that merely repeats AGENTS.md."""
    try:
        b = agents_md_at(member, before_commit, "CLAUDE.md", follow_links=False)
        if after_commit:
            a = agents_md_at(member, after_commit, "CLAUDE.md", follow_links=False)
        else:
            now = member / "CLAUDE.md"
            if now.is_symlink():
                a = (os.readlink(now), True)
            elif now.exists():
                a = (_decode(now.read_bytes(), "CLAUDE.md"), False)
            else:
                a = ABSENT
    except (Undecodable, OSError) as exc:
        return {"verdict": "UNAVAILABLE", "unavailable_reason": f"CLAUDE.md unreadable ({exc})"}
    if a is None or b is None:
        return {"verdict": "UNAVAILABLE", "unavailable_reason": "CLAUDE.md could not be read"}
    if a is ABSENT and b is ABSENT:
        return {"verdict": "CONTINUE", "reasons": []}
    if a is ABSENT or b is ABSENT:
        return {"verdict": "HALT", "reasons": ["CLAUDE.md added or deleted by the migration"]}
    if a[1] != b[1]:
        return {"verdict": "HALT", "reasons": ["CLAUDE.md changed between a regular file and a symbolic link"]}
    if a[1]:
        if all(entry[0] in ("AGENTS.md", "./AGENTS.md") for entry in (a, b)):
            return {"verdict": "CONTINUE", "reasons": []}
        if a[0] != b[0]:
            return {"verdict": "HALT", "reasons": ["CLAUDE.md symbolic link target changed"]}
        return {"verdict": "UNAVAILABLE", "unavailable_reason": "CLAUDE.md symlink does not name AGENTS.md"}
    return compare(b[0], a[0], halt["identity_patterns"], halt["max_agents_md_changed_lines"],
                   halt["allowed_change_patterns"], require_identity=False, name="CLAUDE.md")


def check(member: Path, before_commit: str, root: Path = ROOT, env: dict | None = None,
          after_commit: str | None = None) -> dict:
    member = Path(os.path.expanduser(str(member)))
    rep = {"member": str(member), "before": before_commit, "after": after_commit or "working tree",
           "verdict": "UNAVAILABLE"}
    if shutil.which("git") is None:
        rep["unavailable_reason"] = "git is not installed or not on PATH"
        return rep
    try:
        pol = AP.load(root, env=env)
    except AP.PolicyError as exc:
        rep["unavailable_reason"] = f"adoption policy invalid: {exc}"
        return rep
    halt = pol["policy"]["halt"]
    rep["limits_source"] = {"max_agents_md_changed_lines": pol["sources"]["halt.max_agents_md_changed_lines"],
                            "identity_patterns": pol["sources"]["halt.identity_patterns"],
                            "allowed_change_patterns": pol["sources"]["halt.allowed_change_patterns"]}
    try:
        b = agents_md_at(member, before_commit)
    except Undecodable as exc:
        rep["unavailable_reason"] = f"{exc} at {before_commit}"
        return rep
    if b is None or b is ABSENT:
        rep["unavailable_reason"] = f"AGENTS.md not readable at {before_commit} in {member}"
        return rep
    before, before_link = b
    if after_commit:
        if not commit_exists(member, after_commit):
            rep["unavailable_reason"] = f"commit {after_commit} not found in {member}"
            return rep
        try:
            a = agents_md_at(member, after_commit)
        except Undecodable as exc:
            rep["unavailable_reason"] = f"{exc} at {after_commit}"
            return rep
        if a is ABSENT:
            rep.update({"verdict": "HALT", "reasons": ["AGENTS.md deleted by the migration"]})
            return rep
        if a is None:
            rep["unavailable_reason"] = f"AGENTS.md not readable at {after_commit} in {member}"
            return rep
        after, after_link = a
    else:
        now = member / "AGENTS.md"
        if not now.exists() and not now.is_symlink():
            rep.update({"verdict": "HALT", "reasons": ["AGENTS.md missing after the migration"]})
            return rep
        after_link = now.is_symlink()
        try:
            after = _decode(now.read_bytes())                           # follows a symbolic link
        except Undecodable as exc:
            rep["unavailable_reason"] = str(exc)
            return rep
        except OSError as exc:
            rep["unavailable_reason"] = f"AGENTS.md unreadable now ({type(exc).__name__})"
            return rep
    rep.update(compare(before, after, halt["identity_patterns"], halt["max_agents_md_changed_lines"],
                       halt["allowed_change_patterns"]))
    if before_link != after_link and rep["verdict"] != "UNAVAILABLE":
        rep["verdict"] = "HALT"
        rep["reasons"].append("AGENTS.md changed between a regular file and a symbolic link")
    mirror = compare_claude(member, before_commit, after_commit, halt)
    rep["claude_md"] = mirror
    rep["reasons"].extend(mirror.get("reasons", []))
    rep["offending_lines"] = (rep["offending_lines"] + mirror.get("offending_lines", []))[:5]
    if "HALT" in (rep["verdict"], mirror["verdict"]):
        rep["verdict"] = "HALT"
    elif mirror["verdict"] == "UNAVAILABLE":
        rep.update({"verdict": "UNAVAILABLE", "unavailable_reason": mirror["unavailable_reason"]})
    return rep


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Stop a migration batch on instruction changes outside the allowlist, "
                                 "identity changes, or excessive diffs in AGENTS.md / CLAUDE.md.")
    ap.add_argument("--member", required=True, help="path to the migrated member")
    ap.add_argument("--before", required=True, help="the member's commit before the migration")
    ap.add_argument("--after", help="compare against this commit instead of the working tree")
    ap.add_argument("--json", action="store_true")
    a = ap.parse_args(argv)
    rep = check(Path(a.member), a.before, after_commit=a.after)
    if a.json:
        print(json.dumps(rep, indent=1))
    else:
        tail = "; ".join(rep.get("reasons") or []) or rep.get("unavailable_reason", "")
        print(f"halt check {rep['member']}: {rep['verdict']}" + (f" — {tail}" if tail else ""))
        if rep.get("identity_coverage"):
            print(f"  note: identity is protected by the {rep['identity_coverage']}")
        if rep["verdict"] == "HALT":
            print("  Stop the batch. Read this member's AGENTS.md diff before anything else.")
        elif rep["verdict"] == "UNAVAILABLE":
            print("  Stop the batch. The check could not run; fix the reason above, then run it again.")
    return {"CONTINUE": 0, "HALT": 1}.get(rep["verdict"], 2)


if __name__ == "__main__":
    sys.exit(main())
