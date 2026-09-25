#!/usr/bin/env python3
"""propose_actions_handoff_scan.py -- the deferral scan for /aget-propose-actions (REQ-PA-012).

Before proposing actions, the skill checks whether a recent HANDOFF parked any candidate's
subject (L961: a handoff marks a deferral, not an invitation). Until v3.35 the skill prescribed
a one-line selector, and both forms in circulation were wrong in opposite directions (gh#2676):

    find docs -name "HANDOFF_*.md" -mtime -14      # fresh clone: EVERY handoff reads as recent
    git log --since='14 days ago' -- 'docs/...'    # an UNTRACKED handoff is invisible

and both scanned `docs/` only, so an Aget that keeps handoffs elsewhere had a guard that could
never fire, and "nothing matched" read the same as "nothing was looked at" (gh#2426).

POPULATION (documents on disk, never filesystem mtime):
    committed handoffs whose last AUTHOR date falls inside the window
  + untracked or locally modified handoffs (no authored date to filter on, so in-window)

LOCATIONS: configurable. Precedence: the `locations` argument / --location, then
`.aget/config.json` key `propose_actions.handoff_locations`, then the default
("docs", "planning", "inbox/outbound"). The release-class `handoffs/` directory is excluded by
default: release handoffs are not deferral markers (the skill's own deferral/release split).

VERDICTS (they must never render identically):
    MATCHED         a candidate names a subject                          exit 1
    NONE-MATCHED    candidates exist, none names a subject               exit 0
    NO-CANDIDATES   a location exists, nothing in the window             exit 0
    UNAVAILABLE     could not look (not a git work tree, no configured
                    location exists, a git call failed) -- NOT a pass    exit 2

Usage:
    python3 scripts/propose_actions_handoff_scan.py --subject "<s>" [--subject ...] [--days 14]
        [--location docs --location planning ...] [--repo .] [--json]
    python3 scripts/propose_actions_handoff_scan.py --self-test

Traceability: REQ-PA-012; gh#2676, gh#2426; tests/test_propose_actions_handoff_scan.py;
planning/PROJECT_PLAN_v3.35.0_value_row_propose_actions_repairs_v1.0.md (Gate 1, G1.1).
"""

from __future__ import annotations

import argparse
import json
import os
import subprocess
import sys
import tempfile
import time
from pathlib import Path

DEFAULT_LOCATIONS = ("docs", "planning", "inbox/outbound")
PATTERN = "HANDOFF_*.md"
SELECTOR = ("union(committed HANDOFF_*.md whose last author date is inside the window, "
            "untracked or locally modified HANDOFF_*.md); filesystem mtime is never read")


def _git(repo: Path, *args: str) -> subprocess.CompletedProcess:
    # A git that cannot be launched must surface as UNAVAILABLE, never as an uncaught
    # exception: Python exits 1 on an uncaught error, which is this script's MATCHED code
    # (independent review round 1, R1-02).
    cmd = ["git", "-C", str(repo), *args]
    try:
        return subprocess.run(cmd, capture_output=True, text=True)
    except OSError as exc:
        return subprocess.CompletedProcess(cmd, 127, "", f"git could not be run: {exc}")


def _configured_locations(repo: Path):
    cfg = repo / ".aget" / "config.json"
    try:
        data = json.loads(cfg.read_text())
    except (OSError, ValueError):
        return None
    locs = (data.get("propose_actions") or {}).get("handoff_locations")
    if isinstance(locs, list) and all(isinstance(x, str) for x in locs) and locs:
        return locs
    return None


def _unavailable(result: dict, reason: str) -> dict:
    result.update(verdict="UNAVAILABLE", reason=reason)
    return result


def scan(repo, subjects, days: int = 14, locations=None, now: float | None = None) -> dict:
    """Return the scan result dict. See the module docstring for the population and verdicts."""
    repo = Path(repo)
    subjects = [s for s in (subjects or []) if s and s.strip()]
    if locations is not None:
        locs, source = list(locations), "argument"
    else:
        cfg = _configured_locations(repo)
        locs, source = (cfg, "config") if cfg else (list(DEFAULT_LOCATIONS), "default")
    result = {
        "verdict": None, "reason": "", "window_days": days, "selector": SELECTOR,
        "subjects": subjects, "locations_source": source, "locations": [],
        "candidates": 0, "candidate_paths": [], "matches": [], "unreadable": [],
    }

    probe = _git(repo, "rev-parse", "--is-inside-work-tree")
    if probe.returncode == 127:
        return _unavailable(result, probe.stderr.strip() or "git could not be run")
    if probe.returncode != 0 or probe.stdout.strip() != "true":
        return _unavailable(result, f"not a git work tree: {repo}. The population is defined by git "
                                    "state (author dates, untracked status), so it cannot be enumerated")

    present = []
    for loc in locs:
        status = "present" if (repo / loc).is_dir() else "absent"
        result["locations"].append({"path": loc, "status": status, "candidates": 0})
        if status == "present":
            present.append(loc)
    if not present:
        return _unavailable(result, "none of the configured handoff locations exists: " + ", ".join(locs))

    cutoff = (now if now is not None else time.time()) - days * 86400
    candidates = []
    for loc in present:
        spec = f":(glob){loc}/**/{PATTERN}"
        st = _git(repo, "status", "--porcelain=v1", "-z", "-uall", "--", spec)
        ls = _git(repo, "ls-files", "-z", "--", spec)
        if st.returncode != 0 or ls.returncode != 0:
            return _unavailable(result, f"git could not enumerate {loc}: "
                                        f"{(st.stderr or ls.stderr).strip()[:200]}")
        # -z records: "XY path\0"; a rename or copy is "XY new\0old\0", so the record after
        # an R/C entry is the ORIGINAL path and is skipped. Without -z, git quotes paths that
        # contain spaces and the quoted form matched no file (R1-01).
        changed = {}
        records = st.stdout.split("\0")
        i = 0
        while i < len(records):
            rec = records[i]
            i += 1
            if len(rec) < 4:
                continue
            code, path = rec[:2], rec[3:]
            if "R" in code or "C" in code:
                i += 1
            changed[path] = code != "??"
        n = 0
        for path in [p for p in ls.stdout.split("\0") if p]:
            if path in changed:
                continue
            lg = _git(repo, "log", "-1", "--format=%at", "--", path)
            if lg.returncode != 0:
                return _unavailable(result, f"git log failed for {path}: {lg.stderr.strip()[:200]}")
            stamp = int(lg.stdout.strip() or 0)
            if stamp >= cutoff:
                candidates.append({"path": path, "tracked": True, "basis": "committed",
                                   "age_days": round((cutoff + days * 86400 - stamp) / 86400, 1)})
                n += 1
        for path, tracked in sorted(changed.items()):
            if (repo / path).is_file():
                candidates.append({"path": path, "tracked": tracked,
                                   "basis": "modified" if tracked else "untracked", "age_days": None})
                n += 1
        for entry in result["locations"]:
            if entry["path"] == loc:
                entry["candidates"] = n

    result["candidates"] = len(candidates)
    result["candidate_paths"] = [c["path"] for c in candidates]
    if not candidates:
        result.update(verdict="NO-CANDIDATES",
                      reason=f"no {PATTERN} in the window at: " + ", ".join(present))
        return result

    for cand in candidates:
        try:
            text = (repo / cand["path"]).read_text(errors="replace").lower()
        except OSError as exc:
            result["unreadable"].append({"path": cand["path"], "error": str(exc)})
            continue
        name = cand["path"].lower()
        for subj in subjects:
            s = subj.lower()
            if s in text or s in name:
                result["matches"].append(dict(cand, subject=subj))
    # An unreadable candidate could name a deferred subject, so it forbids a CLEAN verdict.
    # Matches found elsewhere still refuse (MATCHED); with no match, the scan is UNAVAILABLE
    # (independent review round 1, R1-03).
    unread = len(result["unreadable"])
    if result["matches"]:
        result.update(verdict="MATCHED",
                      reason=f"{len(result['matches'])} match(es) across {len(candidates)} candidate(s)"
                             + (f"; {unread} candidate(s) could not be read" if unread else ""))
    elif unread:
        return _unavailable(result, f"{unread} of {len(candidates)} candidate handoff(s) could not be read, "
                                    "so a clean result cannot be claimed: "
                                    + ", ".join(u["path"] for u in result["unreadable"]))
    else:
        result.update(verdict="NONE-MATCHED",
                      reason=f"{len(candidates)} candidate(s) searched; no subject named in any")
    return result


EXIT = {"MATCHED": 1, "NONE-MATCHED": 0, "NO-CANDIDATES": 0, "UNAVAILABLE": 2}


def _self_test() -> int:
    failures = []
    env = dict(os.environ, GIT_AUTHOR_NAME="t", GIT_AUTHOR_EMAIL="t@t",
               GIT_COMMITTER_NAME="t", GIT_COMMITTER_EMAIL="t@t")

    def git(repo, *a, extra=None):
        e = dict(env, **(extra or {}))
        subprocess.run(["git", "-C", str(repo), *a], check=True, capture_output=True, env=e)

    with tempfile.TemporaryDirectory() as tmp:
        repo = Path(tmp) / "seat"
        repo.mkdir()
        git(repo, "init", "-q")
        r = scan(repo, ["x"])
        if r["verdict"] != "UNAVAILABLE":
            failures.append(f"no locations -> {r['verdict']}, expected UNAVAILABLE")
        (repo / "docs").mkdir()
        old = repo / "docs" / "HANDOFF_old.md"
        old.write_text("parked: alpha\n")
        git(repo, "add", "docs/HANDOFF_old.md")
        stamp = time.strftime("%Y-%m-%dT%H:%M:%S", time.localtime(time.time() - 40 * 86400))
        git(repo, "commit", "-q", "-m", "old", extra={"GIT_AUTHOR_DATE": stamp, "GIT_COMMITTER_DATE": stamp})
        os.utime(old, None)
        r = scan(repo, ["alpha"])
        if r["verdict"] != "NO-CANDIDATES":
            failures.append(f"old committed handoff after fresh-clone mtime -> {r['verdict']}, expected NO-CANDIDATES")
        (repo / "planning").mkdir()
        (repo / "planning" / "HANDOFF_new.md").write_text("parked: beta\n")
        r = scan(repo, ["beta"])
        if r["verdict"] != "MATCHED" or r["matches"][0]["tracked"] is not False:
            failures.append(f"untracked handoff in planning/ -> {r['verdict']}, expected MATCHED untracked")
        r = scan(repo, ["gamma"])
        if r["verdict"] != "NONE-MATCHED":
            failures.append(f"unmatched subject -> {r['verdict']}, expected NONE-MATCHED")
    with tempfile.TemporaryDirectory() as tmp:
        r = scan(Path(tmp), ["x"])
        if r["verdict"] != "UNAVAILABLE":
            failures.append(f"not a git work tree -> {r['verdict']}, expected UNAVAILABLE")
    if failures:
        print("SELF-TEST FAIL:")
        for f in failures:
            print("  -", f)
        return 1
    print("PASS")
    return 0


def main(argv=None) -> int:
    ap = argparse.ArgumentParser(description="REQ-PA-012 deferral scan for /aget-propose-actions")
    ap.add_argument("--repo", default=".", help="the Aget's repository root (default: .)")
    ap.add_argument("--subject", action="append", default=[], help="candidate subject (repeatable)")
    ap.add_argument("--days", type=int, default=14, help="window in days (default 14)")
    ap.add_argument("--location", action="append", default=None,
                    help="handoff location, repo-relative (repeatable; overrides config and default)")
    ap.add_argument("--json", action="store_true", help="print the full result as JSON")
    ap.add_argument("--self-test", action="store_true", help="run built-in both-direction cases")
    args = ap.parse_args(argv)
    if args.self_test:
        return _self_test()
    r = scan(args.repo, args.subject, days=args.days, locations=args.location)
    if args.json:
        print(json.dumps(r, indent=2))
    else:
        print(f"{r['verdict']}: {r['reason']}")
        print(f"  searched: {', '.join(l['path'] + '(' + l['status'] + ')' for l in r['locations']) or '-'}"
              f"; window {r['window_days']}d; candidates {r['candidates']}")
        for m in r["matches"]:
            print(f"  MATCH {m['subject']!r} in {m['path']} ({m['basis']})")
    return EXIT[r["verdict"]]


if __name__ == "__main__":
    sys.exit(main())
