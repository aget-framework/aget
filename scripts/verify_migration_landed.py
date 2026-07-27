#!/usr/bin/env python3
"""verify_migration_landed.py — did a migration actually LAND at this seat?

## Why a script, and why three axes

A migration claim has three independent parts, and the fleet's verification battery
read only one of them. All three of these failures pass probes 1-7 of
`handoffs/REMOTE_MIGRATION_MESSAGE_v3.28.0.md` as originally published, and all three
were observed in the field within 24 hours of the v3.28.0 tag:

  | Failure                      | What passes            | What is false                 |
  |------------------------------|------------------------|-------------------------------|
  | version without payload      | probe 6 (both strings) | the scripts never landed      |
  | payload without persistence  | probes 6, 7, smoke     | nothing committed; a checkout |
  |                              |                        | reverts the whole migration   |
  | exit=0 without work          | the dispatcher's rc    | the seat ran nothing at all   |

They share a cause: the signal was always whatever was cheapest to read -- an exit
code, a version string, a hash of a file on disk -- never the thing actually claimed,
which is *this seat carries the capability, durably*.

Measured across one 31-seat fleet at a single instant, 2026-07-27:

    version.json on disk == 3.28.0 ............ 17
    ... and payload sha matches manifest ...... 15
    ... and version.json == 3.28.0 at HEAD .... 13

Four seats claimed the version and did not hold it, in two non-overlapping modes.
Every count published that day was the 17.

## Verdicts

    LANDED         version + payload + committed. The only one that means delivered.
    NOT-COMMITTED  payload correct on disk, HEAD behind. One `git checkout` from gone.
    NOT-APPLIED    payload absent or divergent. The dispatch did no work.
    VERSION-ONLY   version pinned, payload absent. The Gate-2 false-green shape.
    UNVERIFIABLE   could not read the seat. NEVER treat as success.

## The monorepo trap

`git show HEAD:<path>` resolves from the **repository root**, not the cwd. A seat that
is a subdirectory of a monorepo needs `git rev-parse --show-prefix` prepended, or every
such seat reads NOT-COMMITTED. That is a false alarm rather than a false pass -- but a
check that cries wolf during normal operation gets ignored exactly when it is right.

## Scope

Per-seat by design. The fleet loop belongs to the consumer, whose seat registry this
script deliberately does not know about: `for p in <paths>; do verify_migration_landed.py
"$p" --version X.Y.Z; done`. Exit code is 0 only for LANDED, so the loop is scriptable.
"""

import argparse
import hashlib
import json
import os
import subprocess
import sys

VERDICTS = ("LANDED", "NOT-COMMITTED", "VERSION-ONLY", "NOT-APPLIED", "UNVERIFIABLE")


def _git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return r.stdout.strip() if r.returncode == 0 else None


def sha256_file(path):
    if not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def disk_version(repo):
    vj = os.path.join(repo, ".aget", "version.json")
    if not os.path.isfile(vj):
        return None
    try:
        with open(vj) as f:
            return json.load(f).get("aget_version")
    except (OSError, ValueError):
        return None


def head_version(repo):
    """version.json AS COMMITTED. Repo-root-relative -- see §The monorepo trap."""
    prefix = _git(repo, "rev-parse", "--show-prefix")
    if prefix is None:
        return None
    blob = _git(repo, "show", f"HEAD:{prefix}.aget/version.json")
    if not blob:
        return None
    try:
        return json.loads(blob).get("aget_version")
    except ValueError:
        return None


def classify(disk, head, payload_ok, want):
    """The whole decision, as a pure function -- which is what the self-test exercises.

    payload_ok is tri-state: True / False / None (no manifest given, axis not checked).
    """
    if disk is None:
        return "UNVERIFIABLE"
    if disk != want:
        return "NOT-APPLIED"
    if payload_ok is False:
        return "VERSION-ONLY"
    if head is None:
        return "UNVERIFIABLE"
    if head != want:
        return "NOT-COMMITTED"
    return "LANDED"


def check_payload(repo, manifest_path):
    """(ok, details). None when no manifest was supplied -- an unchecked axis is
    reported as unchecked, never silently as pass."""
    if not manifest_path:
        return None, []
    try:
        import yaml
        with open(manifest_path) as f:
            man = yaml.safe_load(f) or {}
    except Exception as exc:                      # noqa: BLE001 - report, don't crash
        return None, [f"manifest unreadable: {exc}"]
    rows = man.get("additive_files") or []
    if not rows:
        return None, ["manifest has no additive_files rows"]
    ok, details = True, []
    for row in rows:
        rel, want = row.get("path"), (row.get("sha256") or "").strip().strip('"')
        if not rel or not want:
            continue
        got = sha256_file(os.path.join(repo, rel))
        if got != want:
            ok = False
            details.append(f"{rel}: {'ABSENT' if got is None else got[:12]} != {want[:12]}")
    return ok, details


def self_test():
    W = "3.28.0"
    cases = [
        ("clean landing",            (W, W, True),  "LANDED"),
        ("payload axis unchecked",   (W, W, None),  "LANDED"),
        ("applied, not committed",   (W, "3.27.0", True),  "NOT-COMMITTED"),
        ("version pinned, no payload", (W, W, False), "VERSION-ONLY"),
        ("version-only beats persistence", (W, "3.27.0", False), "VERSION-ONLY"),
        ("dispatch did nothing",     ("3.27.0", "3.27.0", None), "NOT-APPLIED"),
        ("no version on disk",       (None, W, True), "UNVERIFIABLE"),
        ("HEAD unreadable",          (W, None, True), "UNVERIFIABLE"),
    ]
    failed = []
    for name, args, want in cases:
        got = classify(*args, W)
        ok = got == want
        if not ok:
            failed.append(name)
        print(f"  {'PASS' if ok else 'FAIL'}  {name:34s} -> {got}")
    print(f"\nself-test: {len(cases) - len(failed)}/{len(cases)}")
    return 1 if failed else 0


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if "--self-test" in argv:
        return self_test()

    ap = argparse.ArgumentParser(
        description="Report whether a migration LANDED at a seat: version + payload + committed.")
    ap.add_argument("repo", help="seat repository path")
    ap.add_argument("--version", required=True, help="target version, e.g. 3.28.0")
    ap.add_argument("--manifest", help="DELIVERED_FILES_vX.Y.Z.yaml — enables the payload axis. "
                                       "Without it that axis reports UNCHECKED, never PASS.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    repo = os.path.expanduser(args.repo)
    if not os.path.isdir(os.path.join(repo, ".git")) and not _git(repo, "rev-parse", "--git-dir"):
        print(f"UNVERIFIABLE {repo}: not a git repository", file=sys.stderr)
        return 3

    disk, head = disk_version(repo), head_version(repo)
    payload_ok, payload_detail = check_payload(repo, args.manifest)
    verdict = classify(disk, head, payload_ok, args.version)

    if args.json:
        print(json.dumps({"repo": repo, "verdict": verdict, "version_disk": disk,
                          "version_head": head,
                          "payload": ("UNCHECKED" if payload_ok is None
                                      else "MATCH" if payload_ok else "DIVERGENT"),
                          "payload_detail": payload_detail}, indent=2))
    else:
        print(f"{verdict:15s} {os.path.basename(repo.rstrip('/'))}")
        print(f"  version  disk={disk}  HEAD={head}  want={args.version}")
        print(f"  payload  {'UNCHECKED (no --manifest)' if payload_ok is None else 'MATCH' if payload_ok else 'DIVERGENT'}")
        for d in payload_detail:
            print(f"           {d}")
        if verdict == "NOT-COMMITTED":
            print("  ⛔ The working tree is correct and nothing is committed. Every filesystem")
            print("     probe passes. One `git checkout` reverts the migration.")
        if verdict == "VERSION-ONLY":
            print("  ⛔ The version claims delivery the payload does not support.")
    return 0 if verdict == "LANDED" else 1


if __name__ == "__main__":
    sys.exit(main())
