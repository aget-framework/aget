#!/usr/bin/env python3
"""Validate an ACCEPTED target-scoped receipt against real repository history.

THE DEFECT THIS REPLACES
------------------------
An accepted receiver confirmation was treated as valid only while its recorded transaction
commit equalled current HEAD. Any later UNRELATED commit therefore revoked a confirmation whose
evidence was untouched. Observed live: four accepted routes passed, three confirmations
validated, and the wave stopped before any receiver mutation -- on HEAD equality alone.

The predicate conflated two different received states:

  * **accepted target continuity** -- is the target proven by the immutable receipt still
    continuously unchanged and conformant?
  * **pending transaction quiescence** -- is the whole repository at the exact clean HEAD
    required before a NEW mutation?

Permanent HEAD equality is right for the second and far too strong for the first. Current byte
equality alone is too weak for the first, because a target can be changed and then restored.

THE CONTRACT (all seven, for an already-accepted receipt)
---------------------------------------------------------
  1. receipt path, commit and target digest equal the immutable manifest fields;
  2. the accepted commit resolves AND is an ancestor of current HEAD;
  3. the target blob AT the accepted commit equals the accepted digest;
  4. NO commit in `accepted_commit..HEAD` touched the target -- this is the load-bearing one.
     Byte equality cannot see a touch-and-revert; history can;
  5. current target bytes equal the accepted digest, and the target carries no staged or
     unstaged diff;
  6. current installed-route verification passes;
  7. the result makes **NO whole-worktree-clean claim**.

Unrelated worktree dirt is reported and is NOT a failure. It is also never converted into a
clean claim -- the output separates the four received states so a caller cannot read one as
another:

    historical_receipt | target_continuity | current_worktree | pending_transaction

PENDING receivers are unchanged: exact HEAD, whole-worktree quiescence, custody, rollback and
serial order still apply, and `--pending` evaluates them separately.

Read-only. Runs `git` for history questions and never mutates the repository.

USAGE
  check_receipt_continuity.py --receipt R.json --manifest M.json --repo DIR
  check_receipt_continuity.py --receipt R.json --manifest M.json --repo DIR --pending
  check_receipt_continuity.py ... --installed-route "python3 -m mypkg --check" --json

EXIT CODES
  0  accepted target continuity HOLDS (and, with --pending, quiescence holds too)
  1  continuity FAILS
  2  a required input could not be evaluated -- UNAVAILABLE, never a pass
  3  inputs unusable
"""
from __future__ import annotations

import argparse
import hashlib
import json
import shlex
import subprocess
import sys
from pathlib import Path
from typing import Any

HOLDS, FAILS, UNAVAILABLE = "HOLDS", "FAILS", "UNAVAILABLE"
REQUIRED = ("path", "commit", "digest")


class InputError(Exception):
    pass


def git(repo: Path, *args: str) -> tuple[int, str]:
    try:
        p = subprocess.run(["git", "-C", str(repo), *args],
                           capture_output=True, text=True, timeout=60)
        return p.returncode, (p.stdout or "").strip()
    except (OSError, subprocess.SubprocessError):
        return -1, ""


def sha256_bytes(b: bytes) -> str:
    return hashlib.sha256(b).hexdigest()


def git_blob(repo: Path, commit: str, path: str) -> bytes | None:
    """Raw blob bytes. Deliberately NOT routed through git(), which strips output --
    stripping loses a trailing newline and made every digest comparison fail."""
    try:
        p = subprocess.run(["git", "-C", str(repo), "show", f"{commit}:{path}"],
                           capture_output=True, timeout=60)
        return p.stdout if p.returncode == 0 else None
    except (OSError, subprocess.SubprocessError):
        return None


def load(path: Path, label: str) -> dict[str, Any]:
    try:
        doc = json.loads(path.read_text())
    except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise InputError(f"{label} unreadable: {exc}") from exc
    if not isinstance(doc, dict):
        raise InputError(f"{label} must be a JSON object")
    missing = [k for k in REQUIRED if not str(doc.get(k, "")).strip()]
    if missing:
        raise InputError(f"{label} is missing {missing}")
    return doc


def evaluate(receipt: dict[str, Any], manifest: dict[str, Any], repo: Path,
             installed_route: str | None, pending: bool) -> dict[str, Any]:
    target = receipt["path"]
    accepted = receipt["commit"]
    digest = receipt["digest"]
    checks: dict[str, dict[str, Any]] = {}

    # (1) custody -- the receipt may not drift from the manifest that binds it.
    drift = [k for k in REQUIRED if str(receipt[k]) != str(manifest.get(k, ""))]
    checks["custody_immutable"] = {
        "state": FAILS if drift else HOLDS,
        "why": f"receipt fields diverge from the manifest: {drift}" if drift else None,
    }

    # (2) the accepted commit resolves and is ancestral. Fail CLOSED.
    rc, _ = git(repo, "rev-parse", "--verify", f"{accepted}^{{commit}}")
    resolves = rc == 0
    if not resolves:
        checks["accepted_commit_ancestral"] = {
            "state": FAILS, "why": f"accepted commit {accepted} does not resolve"}
    else:
        rc2, _ = git(repo, "merge-base", "--is-ancestor", accepted, "HEAD")
        checks["accepted_commit_ancestral"] = {
            "state": HOLDS if rc2 == 0 else FAILS,
            "why": None if rc2 == 0 else f"{accepted} is not an ancestor of HEAD"}

    # (3) the blob AT the accepted commit is what the receipt says it was.
    if resolves:
        blob = git_blob(repo, accepted, target)
        if blob is None:
            checks["accepted_blob_matches"] = {
                "state": FAILS, "why": f"{target} does not exist at {accepted}"}
        else:
            got = sha256_bytes(blob)
            checks["accepted_blob_matches"] = {
                "state": HOLDS if got == digest else FAILS, "observed": got,
                "why": None if got == digest else "blob at the accepted commit is not the accepted digest"}
    else:
        checks["accepted_blob_matches"] = {"state": UNAVAILABLE,
                                           "why": "accepted commit does not resolve"}

    # (4) THE LOAD-BEARING ONE. History, not bytes: a touch-and-revert restores the digest and
    # must still fail, because the target did not remain continuously unchanged.
    if resolves:
        rc4, touched = git(repo, "log", "--oneline", f"{accepted}..HEAD", "--", target)
        if rc4 != 0:
            checks["untouched_since_accepted"] = {
                "state": UNAVAILABLE, "why": "could not read history for the target"}
        else:
            hits = [l for l in touched.splitlines() if l.strip()]
            checks["untouched_since_accepted"] = {
                "state": HOLDS if not hits else FAILS, "touching_commits": hits[:10],
                "why": None if not hits else
                       f"{len(hits)} commit(s) in {accepted}..HEAD touched {target}; a "
                       f"touch-and-revert restores the bytes and still breaks continuity"}
    else:
        checks["untouched_since_accepted"] = {"state": UNAVAILABLE,
                                              "why": "accepted commit does not resolve"}

    # (5) current bytes, and the TARGET's own cleanliness -- not the worktree's.
    tp = repo / target
    if not tp.is_file():
        checks["current_target_matches"] = {"state": FAILS, "why": f"{target} is absent now"}
    else:
        try:
            got = sha256_bytes(tp.read_bytes())
        except OSError as exc:
            got = None
            checks["current_target_matches"] = {"state": UNAVAILABLE, "why": str(exc)}
        if got is not None:
            rc5, dirty = git(repo, "status", "--porcelain", "--", target)
            target_dirty = bool(dirty.strip()) if rc5 == 0 else None
            ok = got == digest and not target_dirty
            checks["current_target_matches"] = {
                "state": (FAILS if got != digest else UNAVAILABLE if rc5 != 0
                          else HOLDS if ok else FAILS),
                "observed": got, "target_dirty": target_dirty,
                "why": "could not read target status" if rc5 != 0 else
                       None if ok else ("target has a staged/unstaged diff" if target_dirty
                                        else "current target bytes are not the accepted digest")}

    # (6) the installed route. Absent instruction = UNAVAILABLE, never an assumed pass.
    if installed_route:
        try:
            pr = subprocess.run(shlex.split(installed_route), cwd=repo,
                                capture_output=True, text=True, timeout=300)
            checks["installed_route"] = {
                "state": HOLDS if pr.returncode == 0 else FAILS, "exit": pr.returncode,
                "why": None if pr.returncode == 0 else "installed-route verification exited non-zero"}
        except (OSError, subprocess.SubprocessError) as exc:
            checks["installed_route"] = {"state": UNAVAILABLE, "why": f"route could not run: {exc}"}
    else:
        checks["installed_route"] = {"state": UNAVAILABLE,
                                     "why": "no --installed-route supplied; not assumed to pass"}

    # --- the four received states, kept apart -----------------------------------
    continuity_keys = ("custody_immutable", "accepted_commit_ancestral", "accepted_blob_matches",
                       "untouched_since_accepted", "current_target_matches", "installed_route")
    states = [checks[k]["state"] for k in continuity_keys]
    continuity = FAILS if FAILS in states else (UNAVAILABLE if UNAVAILABLE in states else HOLDS)

    wt_rc, wt = git(repo, "status", "--porcelain")
    dirt = [l for l in wt.splitlines() if l.strip()]
    worktree = {
        "state": HOLDS if wt_rc == 0 else UNAVAILABLE,
        "dirty_entries": len(dirt) if wt_rc == 0 else None,
        "sample": dirt[:5] if wt_rc == 0 else None,
        # (7) The one thing this command must never say.
        "claim": "NO WHOLE-WORKTREE-CLEAN CLAIM IS MADE. Unrelated dirt neither invalidates an "
                 "accepted receipt nor is converted into a clean-worktree assertion.",
    }

    pending_state = None
    if pending:
        head_rc, head = git(repo, "rev-parse", "HEAD")
        exact = head == accepted if head_rc == 0 else None
        quiescent = not dirt if wt_rc == 0 else None
        state = (FAILS if exact is False or quiescent is False else
                 UNAVAILABLE if exact is None or quiescent is None else HOLDS)
        pending_state = {
            "state": state,
            "exact_head": exact, "worktree_quiescent": quiescent,
            "why": None if state == HOLDS else
                   "a PENDING transaction still requires exact HEAD and a quiescent worktree; "
                   "this is deliberately stricter than accepted continuity",
        }

    return {
        "target": target, "accepted_commit": accepted,
        "historical_receipt": {"state": checks["custody_immutable"]["state"]},
        "target_continuity": {"state": continuity, "checks": checks},
        "current_worktree": worktree,
        "pending_transaction": pending_state,
        "overall": continuity,
    }


def render(res: dict[str, Any]) -> str:
    out = [f"receipt continuity for {res['target']} @ {res['accepted_commit'][:12]}: "
           f"{res['overall']}", ""]
    for k, v in res["target_continuity"]["checks"].items():
        out.append(f"  {v['state']:<12} {k}")
        if v.get("why"):
            out.append(f"               -- {v['why']}")
    w = res["current_worktree"]
    out += ["", f"  current worktree: {w['dirty_entries']} dirty entry(ies) -- reported, not graded",
            f"  {w['claim']}"]
    if res["pending_transaction"]:
        p = res["pending_transaction"]
        out.append(f"  pending transaction: {p['state']} (exact_head={p['exact_head']}, "
                   f"quiescent={p['worktree_quiescent']})")
    return "\n".join(out)


def exit_code(res: dict[str, Any]) -> int:
    if res["overall"] == FAILS:
        return 1
    if res["pending_transaction"] and res["pending_transaction"]["state"] == FAILS:
        return 1
    if res["overall"] == UNAVAILABLE or (
            res["pending_transaction"] and
            res["pending_transaction"]["state"] == UNAVAILABLE):
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Validate an accepted target-scoped receipt.")
    ap.add_argument("--receipt", type=Path, required=True)
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--repo", type=Path, required=True)
    ap.add_argument("--installed-route", default=None)
    ap.add_argument("--pending", action="store_true",
                    help="additionally evaluate PENDING quiescence (exact HEAD + clean worktree)")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        if not (args.repo / ".git").exists():
            raise InputError(f"{args.repo} is not a git repository")
        res = evaluate(load(args.receipt, "receipt"), load(args.manifest, "manifest"),
                       args.repo, args.installed_route, args.pending)
    except InputError as exc:
        print(f"UNAVAILABLE: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(res, indent=1) if args.json else render(res))
    return exit_code(res)


if __name__ == "__main__":
    sys.exit(main())
