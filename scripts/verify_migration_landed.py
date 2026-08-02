#!/usr/bin/env python3
"""verify_migration_landed.py — did a migration actually LAND at this seat?

## Why a script, and why the axes keep multiplying

A migration claim has several independent parts, and each round of hardening has found
one more. All of these pass probes 1-7 of `handoffs/REMOTE_MIGRATION_MESSAGE_v3.28.0.md`
as originally published, and every one was observed in the field:

  | Failure                      | What passes            | What is false                 |
  |------------------------------|------------------------|-------------------------------|
  | version without payload      | probe 6 (both strings) | the scripts never landed      |
  | payload without persistence  | probes 6, 7, smoke     | nothing committed; a checkout |
  |                              |                        | reverts the whole migration   |
  | exit=0 without work          | the dispatcher's rc    | the seat ran nothing at all   |
  | committed but OFF-TRUNK      | every HEAD-based probe | trunk is releases behind      |

They share a cause: the signal was always whatever was cheapest to read -- an exit
code, a version string, a hash of a file on disk -- never the thing actually claimed,
which is *this seat carries the capability, durably*.

## ⚠ THREE DEFECTS IN THIS SCRIPT'S OWN AXES, FIXED 2026-07-29

This file was written to kill the cheapest-to-read failure and shipped carrying three
instances of it. All three were surfaced by the originating supervisor seat measuring the same
fleet independently and disagreeing about *which seats* landed while agreeing on the
total. See `.aget/evolution/` at the framework seat and CORRECTIONS row 15.

  1. **The version axis read `HEAD`, not trunk.** a downstream seat on an unmerged branch sat on branch
     `session/2026-07-17-...` with `HEAD`=3.28.0 and `main`=**3.26.0**, and this script
     certified it LANDED. A payload on an unmerged branch is not durably held: the branch
     can be abandoned and nothing about the seat's trunk changes. `R-FU-014-6` at the
     consuming seat had already superseded HEAD with trunk; canonical had not converged.

  2. **The payload axis hashed the WORKING TREE while the version axis read a commit.**
     One local edit to a payload file made a downstream monorepo seat read
     DIVERGENT while its committed state was byte-exact. Two axes, two different refs,
     one verdict -- so the verdict answered no single question. Worktree drift is real
     information and is now reported SEPARATELY, as drift, without touching the verdict.

  3. **The payload axis silently scored ONE of THREE sha-bearing manifest sections.**
     `rows = man.get("additive_files")` -- with `delivered_files` and `optional_files`
     unread and unmentioned, while the manifest's own `verify_rule` names all three.
     For v3.28 the narrow read gave the *right answer for the wrong reason*: the
     `delivered_files` enforcement payload never shipped (CORRECTIONS row 3), so scoring
     it would have reported DIVERGENT at all evaluated seats. Being accidentally correct is not
     being correct -- the next release ships its `delivered_files` and the accident
     inverts. Sections are now explicit, per-section, and **always printed**, including
     the ones excluded. A filtered result that does not carry its filter is a false
     clean.

Defects 1 and 2 were sign-opposed and cancelled exactly, so two seats independently
reported **the same LANDED total** from different sets. An aggregate cannot show that; an
element-wise diff can. Publish the set, not the count.

## Verdicts

    LANDED         version + payload + committed ON TRUNK. The only one meaning delivered.
    OFF-TRUNK      committed, but not on trunk. Every HEAD-based probe passes. The
                   migration exists on a branch and the seat's trunk does not have it.
    NOT-COMMITTED  payload correct on disk, nothing committed. One `git checkout` from gone.
    NOT-APPLIED    payload absent or divergent. The dispatch did no work.
    VERSION-ONLY   version pinned, payload absent. The Gate-2 false-green shape.
    UNVERIFIABLE   an axis was not examined, or the seat could not be read.
                   NEVER treat as success. Exit 2 -- distinct from FAIL.
                   Running without --manifest leaves the payload axis unexamined and
                   therefore CANNOT yield LANDED. An unresolvable trunk is likewise
                   UNVERIFIABLE, never a pass (UNREACHABLE is not PASS).

## Trunk resolution, and why it is not just "main"

Seats differ: a seat whose trunk branch is `master` is on `master`. Resolution order is
`origin/HEAD` symref, then local `main`, then local `master`. If none resolves, the run
is UNVERIFIABLE -- guessing a trunk name is how a check starts certifying the wrong ref.
Trunk is read LOCALLY on purpose: fleet dispatch does not push, so "durably held at this
seat" is a claim about this clone's trunk, not about a remote.

## The monorepo trap -- the PATH form was always right; only the REF was wrong

`git show <ref>:<path>` resolves from the **repository root**, not the cwd. A seat that is
a subdirectory of a monorepo needs `git rev-parse --show-prefix` prepended, or every such
seat reads NOT-COMMITTED. That prefix is correct and is KEPT. Fixing defect 1 means
changing `HEAD` to trunk and *nothing else* -- dropping the prefix while fixing the ref
reintroduces the monorepo false alarm, which is the classic shape of a correction failing
to reach what was derived from it.

## Scope

Per-seat by design. The fleet loop belongs to the consumer, whose seat registry this
script deliberately does not know about (resolve it from FLEET_STATE, never a path glob):
`for p in <paths>; do verify_migration_landed.py "$p" --version X.Y.Z \
    --manifest <DELIVERED_FILES> --payload-sections additive_files,optional_files; done`

Exit codes: **0** LANDED · **1** a defect was found · **2** UNVERIFIABLE (an axis was
not examined). Two and one are different facts; collapsing them trains readers to
ignore the one that means "this run cannot answer your question."
"""

import argparse
import hashlib
import json
import os
import re
import subprocess
import sys

VERDICTS = ("LANDED", "LANDED-AND-ADVANCED", "ADVANCED-UNPAIRED", "OFF-TRUNK",
            "NOT-COMMITTED", "VERSION-ONLY", "NOT-APPLIED", "UNVERIFIABLE")

#: Every manifest section that carries sha256 rows. `pin_edits` is excluded because it
#: is edited in place on the agent and carries no sha by design.
SHA_SECTIONS = ("delivered_files", "optional_files", "additive_files")


def _git(repo, *args):
    r = subprocess.run(["git", "-C", str(repo), *args],
                       capture_output=True, text=True, stdin=subprocess.DEVNULL)
    return r.stdout.strip() if r.returncode == 0 else None


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest() if data is not None else None


def _is_hash(value):
    """True only for a real sha256. The manifest uses non-hex SENTINELS such as
    `ABSENT-AT-REF` in the sha256 field to record 'this was never shipped'. Treating a
    sentinel as a hash makes every seat mismatch it -- see check_payload()."""
    v = (value or "").strip().lower()
    return len(v) == 64 and all(c in "0123456789abcdef" for c in v)


def sha256_file(path):
    if not os.path.isfile(path):
        return None
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _show_bytes(repo, ref, relpath):
    """Raw bytes of relpath as committed at ref, or None. Repo-root-relative."""
    prefix = _git(repo, "rev-parse", "--show-prefix")
    if prefix is None:
        return None
    r = subprocess.run(["git", "-C", str(repo), "show", f"{ref}:{prefix}{relpath}"],
                       capture_output=True, stdin=subprocess.DEVNULL)
    return r.stdout if r.returncode == 0 else None


def ever_held(repo, relpath, want_sha):
    """ANCESTOR-CONTAINMENT: did this seat's own history ever hold exactly `want_sha`?

    Distinguishes a seat that RECEIVED the payload and then advanced past it (the
    producing seat, by construction — it is where the next version is authored) from a
    seat that never held those bytes at all. Principal ruling 2026-07-29: this counts.

    ⚠ THIS PREDICATE IS MONOTONE, AND THAT IS ITS CEILING. Once true it is true forever;
    it can never return to False. So it CANNOT express regression. A seat may hold the
    payload, have it reverted or damaged by any later commit, and pass this check
    permanently. It answers *did the payload arrive*, never *is this seat correct now*.
    That is why `LANDED-AND-ADVANCED` requires a capability attestation — see classify().

    Implementation note: the commit list is MATERIALISED before iterating. A `git show`
    inside a `while read` pipeline consumes the loop's own stdin and shifts every result
    by one row — no error, confident garbage. That defect nearly inverted a conclusion at
    the framework seat on 2026-07-29; it is why this is a list comprehension.
    """
    if not want_sha:
        return None
    prefix = _git(repo, "rev-parse", "--show-prefix")
    if prefix is None:
        return None
    log = _git(repo, "log", "--format=%H", "--", f"{prefix}{relpath}")
    if not log:
        return False
    for commit in [ln.strip() for ln in log.splitlines() if ln.strip()]:
        blob = _show_bytes(repo, commit, relpath)
        if blob is not None and _sha256_bytes(blob) == want_sha:
            return True
    return False


#: `@aget-canonical-specs` pins a `/tree/vX.Y.Z/specs` ref and declares reliance-only
#: conformance. Read at three surfaces because they disagree; see check_pin().
_PIN_RE = re.compile(r'@aget-canonical-specs:\s*\S*?/tree/v([0-9.]+)/')
_VER_RE = re.compile(r'@aget-version:\s*([0-9.]+)')


def _strip_emphasis(text):
    # Markdown emphasis silently exempts a term from every audit that follows
    # (CORRECTIONS row 12). Strip before matching prose identifiers.
    return re.sub(r'[*`_]', '', text or '')


def check_pin(repo, trunk_ref, want):
    """The `@aget-canonical-specs` axis, at worktree / trunk / PUBLISHED.

    ⚠ WHY THE PUBLISHED SURFACE NEEDS ITS OWN READ. `@aget-canonical-specs` is a
    reliance-only conformance declaration — the line another agent reads to learn which
    spec revision this seat's behaviour was built against. A pin correct only locally is
    correct nowhere a remote consumer looks.

    SCOPE, per principal ruling 2026-07-29: the published surface is BLOCKING for
    publicly-readable repos and ADVISORY for private ones, because cross-seat reads in a
    private fleet happen on the local filesystem (L480) — there, trunk is what a peer
    actually reads. The scope is REPORTED here, never silently applied.

    ⚠ AND THE READ MUST CARRY THE REPO-ROOT PREFIX. `git show <ref>:<path>` resolves from
    the repository root. Three GM-RKB monorepo seats read as UNMEASURABLE on 2026-07-29
    from an unprefixed probe — and TWO of them were actually STALE, so two real failures
    sat inside a bucket labelled "couldn't check". An unmeasured bucket adjacent to a
    failing axis absorbs failures. This routes through _show_bytes(), which prefixes.
    """
    rep = {"worktree": None, "trunk": None, "published": None,
           "has_pin": False, "has_remote": False, "state": "UNMEASURED",
           "blocking": _is_public_repo(repo), "want": want}
    try:
        with open(os.path.join(repo, "AGENTS.md"), encoding="utf-8", errors="replace") as f:
            wt = f.read()
    except OSError:
        rep["state"] = "NO-AGENTS-FILE"
        return rep
    wt = _strip_emphasis(wt)
    rep["has_pin"] = "@aget-canonical-specs" in wt
    m = _PIN_RE.search(wt)
    rep["worktree"] = m.group(1) if m else None

    def pin_at(ref):
        blob = _show_bytes(repo, ref, "AGENTS.md")
        if blob is None:
            return None
        mm = _PIN_RE.search(_strip_emphasis(blob.decode("utf-8", "replace")))
        return mm.group(1) if mm else None

    if trunk_ref:
        rep["trunk"] = pin_at(trunk_ref)
        pub_ref = f"origin/{trunk_ref}"
        if _git(repo, "rev-parse", "--verify", "--quiet", pub_ref) is not None:
            rep["has_remote"] = True
            rep["published"] = pin_at(pub_ref)

    if not rep["has_pin"]:
        # A seat with no pin line at all is a GOVERNED ABSENCE candidate, not drift.
        # Never invent one to make a sweep look complete.
        rep["state"] = "NO-PIN-GOVERNED-ABSENCE"
    elif not rep["has_remote"]:
        rep["state"] = "UNMEASURED-NO-REMOTE"      # NOT a pass (UNREACHABLE is not PASS)
    elif rep["published"] == want:
        rep["state"] = "PUBLISHED-CURRENT"
    elif rep["trunk"] == want:
        rep["state"] = "COMMITTED-NOT-PUBLISHED"
    else:
        rep["state"] = "DRIFTED"
    return rep


def _is_public_repo(repo):
    """Publicly readable? Decides whether the published pin axis BLOCKS or advises."""
    name = os.path.basename(os.path.realpath(repo).rstrip("/"))
    if name.startswith("public-"):
        return True
    url = _git(repo, "remote", "get-url", "origin") or ""
    return "aget-framework/" in url


def resolve_trunk(repo):
    """(ref, how). Never guesses -- returns (None, reason) when it cannot resolve."""
    sym = _git(repo, "symbolic-ref", "--quiet", "refs/remotes/origin/HEAD")
    if sym:
        short = sym.rsplit("/", 1)[-1]
        if _git(repo, "rev-parse", "--verify", "--quiet", short) is not None:
            return short, f"origin/HEAD -> {short}"
    for cand in ("main", "master"):
        if _git(repo, "rev-parse", "--verify", "--quiet", cand) is not None:
            return cand, f"local {cand}"
    return None, "no origin/HEAD, main, or master resolves"


def disk_version(repo):
    vj = os.path.join(repo, ".aget", "version.json")
    if not os.path.isfile(vj):
        return None
    try:
        with open(vj) as f:
            return json.load(f).get("aget_version")
    except (OSError, ValueError):
        return None


def version_at(repo, ref):
    """version.json AS COMMITTED AT ref. Repo-root-relative -- see §The monorepo trap."""
    if ref is None:
        return None
    blob = _show_bytes(repo, ref, ".aget/version.json")
    if not blob:
        return None
    try:
        return json.loads(blob.decode("utf-8", "replace")).get("aget_version")
    except ValueError:
        return None


def classify(disk, head, trunk, payload_ok, want, advanced=None, capability=None):
    """The whole decision, as a pure function -- which is what the self-test exercises.

    payload_ok is tri-state: True / False / None (axis not checked).
    `trunk` is the version AT the trunk ref, or None if trunk was unresolvable.
    `advanced` -- every mismatching payload file's pinned blob was once held here
                  (ancestor-containment). MONOTONE: see ever_held().
    `capability` -- executed-surface/probe-7 attestation for this seat. This instrument
                  CANNOT determine it (it does not run the seat's suite), so it must be
                  supplied. None means "not attested", which is never a pass.
    """
    if disk is None:
        return "UNVERIFIABLE"
    if disk != want:
        return "NOT-APPLIED"
    if trunk is None:
        # Trunk unresolvable. UNREACHABLE is not PASS -- do not fall back to HEAD, which
        # is the very substitution defect 1 was.
        return "UNVERIFIABLE"

    # PRECEDENCE: the trunk-position question is answered BEFORE the payload question,
    # and the ordering is load-bearing (corrected 2026-07-29 on first live run).
    #
    # The payload axis is scored AT TRUNK. So when trunk is behind, the payload at trunk
    # is *necessarily* behind too -- it is a CONSEQUENCE of the trunk position, not an
    # independent finding. Scoring payload first made a downstream seat on an unmerged branch read
    # VERSION-ONLY, whose stated meaning is "version pinned, payload absent" -- the
    # Gate-2 false-green shape, whose remedy is re-migration. career's actual remedy is a
    # conflict-free fast-forward. Reporting a consequence instead of its cause hands the
    # reader the wrong repair, which is worse than a vague answer.
    if trunk != want:
        if head == want:
            # Committed somewhere, absent from trunk. Remedy: merge, NOT re-migration.
            return "OFF-TRUNK"
        # Nothing committed at the target anywhere. Remedy: commit.
        return "NOT-COMMITTED"

    if payload_ok is None:
        # ZERO-DENOMINATOR GATE (2026-07-28, gh#2045). This returned LANDED -- a PASS --
        # on an axis that was never examined. A conjunction over an unexamined conjunct
        # is not satisfied; it is unevaluated. Fail closed.
        return "UNVERIFIABLE"
    if payload_ok is False:
        # Trunk IS at the target version and the payload does not back it.
        #
        # ANCESTOR-CONTAINMENT (principal ruling 2026-07-29). If every mismatching file's
        # pinned blob was once held HERE, this seat received the payload and advanced past
        # it — which is what the PRODUCING seat does by construction, because it is where
        # the next version is authored. A wave that counts the producer in a
        # hash-match-against-frozen-tag denominator fails the moment the producer resumes
        # work. That is a spec defect, not a compliance defect (L742).
        #
        # THE PAIRING CONSTRAINT IS STRUCTURAL, NOT ADVISORY. `advanced` is monotone and
        # therefore blind to regression: hold the bytes once, diverge arbitrarily forever,
        # still True. So provenance alone MUST NOT yield a pass. Without a capability
        # attestation the verdict is ADVANCED-UNPAIRED and the exit code is a failure.
        # Unpaired, this state would become "differences are fine if you once matched" —
        # precedent the next wave inherits.
        if advanced:
            return "LANDED-AND-ADVANCED" if capability else "ADVANCED-UNPAIRED"
        # Never held the bytes: a genuine non-delivery, no role privilege available.
        return "VERSION-ONLY"
    return "LANDED"


def check_payload(repo, manifest_path, ref, sections):
    """(ok, report). Scores manifest shas AT ref -- the same ref the version axis uses.

    report carries per-section tallies, the sections EXCLUDED, and worktree drift.
    A section that was not scored is named in the output, never silently dropped.
    """
    report = {"ref": ref, "sections_scored": list(sections),
              "sections_excluded": [], "per_section": {}, "details": [],
              "worktree_drift": [], "mismatched": []}
    if not manifest_path:
        return None, report
    try:
        import yaml
        with open(manifest_path) as f:
            man = yaml.safe_load(f) or {}
    except Exception as exc:                      # noqa: BLE001 - report, don't crash
        report["details"].append(f"manifest unreadable: {exc}")
        return None, report

    report["sections_excluded"] = [
        s for s in SHA_SECTIONS
        if s not in sections and any(
            r.get("sha256") for r in (man.get(s) or []) if isinstance(r, dict))
    ]
    if ref is None:
        report["details"].append("payload axis needs a resolvable ref; not scored")
        return None, report

    scored = 0
    ok = True
    for sect in sections:
        rows = [r for r in (man.get(sect) or []) if isinstance(r, dict)]
        s_ok = s_bad = s_absent = s_anom = 0
        for row in rows:
            rel, want = row.get("path"), (row.get("sha256") or "").strip().strip('"')
            if not rel or not want:
                continue
            got = _sha256_bytes(_show_bytes(repo, ref, rel))

            if not _is_hash(want):
                # DECLARED ABSENCE, not a hash claim. The v3.28 manifest writes
                # `sha256: ABSENT-AT-REF` for every enforcement-payload row, because that
                # payload was never propagated (CORRECTIONS rows 3 and 5 -- "every row
                # reads ABSENT-AT-REF, which is the defect in row 3 stated machine-
                # readably"). There is nothing to deliver, so there is nothing to match.
                # Scoring it as a hash mismatch would report all evaluated seats DIVERGENT for
                # correctly not having a file that was never shipped -- turning a
                # disclosed producer-side gap into 31 phantom consumer defects.
                s_absent += 1
                if got is not None:
                    # Present at the seat while the manifest declares it absent at the
                    # source ref: not a delivery failure, but it did not come from here.
                    s_anom += 1
                    report["details"].append(
                        f"[{sect}] {rel}: PRESENT at {ref} but manifest declares "
                        f"'{want}' — provenance unknown, not from this release")
                continue

            scored += 1
            if got == want:
                s_ok += 1
            else:
                s_bad += 1
                ok = False
                report["mismatched"].append({"path": rel, "want": want, "got": got})
                report["details"].append(
                    f"[{sect}] {rel}: "
                    f"{'ABSENT-AT-' + str(ref) if got is None else got[:12]} "
                    f"!= {want[:12]}")
            wt = sha256_file(os.path.join(repo, rel))
            if wt is not None and got is not None and wt != got:
                report["worktree_drift"].append(rel)
        report["per_section"][sect] = {"match": s_ok, "mismatch": s_bad,
                                       "declared_absent": s_absent,
                                       "present_but_declared_absent": s_anom,
                                       "rows": len(rows)}

    if scored == 0:
        report["details"].append(
            "no HASH-bearing rows in the requested sections -- axis NOT scored. "
            "Declared-absent rows cannot establish delivery.")
        return None, report
    return ok, report


def self_test():
    W = "3.28.0"
    O = "3.27.0"
    # (name, (disk, head, trunk, payload_ok), expected)
    cases = [
        ("clean landing",                    (W, W, W, True),   "LANDED"),
        # Inverted 2026-07-28: the prior case asserted LANDED and passed 8/8, which is how
        # a suite comes to DEFEND a defect. A self-test is a claim under test (gh#2045).
        ("unchecked payload is NOT a pass",  (W, W, W, None),   "UNVERIFIABLE"),
        ("unchecked axis, stale version still NOT-APPLIED",
                                             (O, O, O, None),   "NOT-APPLIED"),
        # Added 2026-07-29 -- defect 1. This is the career case, which the pre-fix script
        # scored LANDED. If this case ever reads LANDED again, the regression is back.
        ("committed on a branch, trunk behind -> OFF-TRUNK",
                                             (W, W, "3.26.0", True), "OFF-TRUNK"),
        ("trunk behind AND head behind -> NOT-COMMITTED",
                                             (W, O, O, True),   "NOT-COMMITTED"),
        # Added 2026-07-29 -- fail closed when trunk cannot be resolved. Must NOT fall
        # back to HEAD; falling back is exactly the substitution defect 1 was.
        ("unresolvable trunk is NOT a pass", (W, W, None, True), "UNVERIFIABLE"),
        ("version pinned, no payload",       (W, W, W, False),  "VERSION-ONLY"),
        # PRECEDENCE FLIP, 2026-07-29, recorded rather than silently re-asserted. This case
        # read VERSION-ONLY before the reorder, encoding payload-before-trunk. Nothing is
        # committed at the target on any ref here, so "nothing committed" is the dominant
        # and actionable fact; the stale payload at a stale trunk is entailed by it.
        ("nothing committed anywhere -> NOT-COMMITTED, not VERSION-ONLY",
                                             (W, O, O, False),  "NOT-COMMITTED"),
        ("dispatch did nothing",             (O, O, O, None),   "NOT-APPLIED"),
        ("no version on disk",               (None, W, W, True), "UNVERIFIABLE"),

        # ---- ancestor-containment, added 2026-07-29 (principal ruling) ----
        # The producing seat: held the pinned blob, advanced past it, capability attested.
        ("advanced + capability attested -> LANDED-AND-ADVANCED",
                                             (W, W, W, False, True, True),
                                             "LANDED-AND-ADVANCED"),
        # THE FALSIFIER THAT NOTHING ELSE COVERS. `advanced` is MONOTONE: once a seat has
        # held the blob it passes forever, so it cannot fail on regression. A seat that
        # held the payload and then had it reverted or damaged looks IDENTICAL to the
        # producing seat on that axis. The only thing separating them is the capability
        # attestation — so if this row ever reads LANDED-AND-ADVANCED, the pairing
        # constraint has been dropped and provenance is being read as correctness.
        ("held-then-REGRESSED, no capability -> NOT a pass",
                                             (W, W, W, False, True, False),
                                             "ADVANCED-UNPAIRED"),
        ("advanced but capability merely UNSTATED -> still not a pass",
                                             (W, W, W, False, True, None),
                                             "ADVANCED-UNPAIRED"),
        # No role privilege: a seat that never held the bytes cannot reach the state, and
        # an attestation does not buy it either.
        ("never held the blob -> VERSION-ONLY even WITH capability",
                                             (W, W, W, False, False, True),
                                             "VERSION-ONLY"),
        ("ancestor-containment unknown -> VERSION-ONLY, not a pass",
                                             (W, W, W, False, None, True),
                                             "VERSION-ONLY"),
    ]
    failed = []
    for name, args, want in cases:
        got = classify(*args[:4], W, *args[4:])
        ok = got == want
        if not ok:
            failed.append(f"{name}: got {got}, want {want}")
        print(f"  {'PASS' if ok else 'FAIL'}  {name:50s} -> {got}")
    print(f"\nself-test: {len(cases) - len(failed)}/{len(cases)}")
    for f in failed:
        print(f"  FAILED: {f}")
    return 1 if failed else 0


def main(argv=None):
    if argv is None:
        argv = sys.argv[1:]
    if "--self-test" in argv:
        return self_test()

    ap = argparse.ArgumentParser(
        description="Report whether a migration LANDED at a seat: "
                    "version + payload + committed ON TRUNK.")
    ap.add_argument("repo", help="seat repository path")
    ap.add_argument("--version", required=True, help="target version, e.g. 3.28.0")
    ap.add_argument("--manifest", help="DELIVERED_FILES_vX.Y.Z.yaml — enables the payload "
                                       "axis. Without it that axis reports UNCHECKED, "
                                       "never PASS.")
    ap.add_argument("--payload-sections", default=",".join(SHA_SECTIONS),
                    help="comma-separated manifest sections to score. "
                         "Default: all sha-bearing sections (%(default)s). "
                         "Excluded sections are ALWAYS reported.")
    ap.add_argument("--capability-attested", metavar="EVIDENCE",
                    help="Attest that the executed-surface/probe-7 check PASSED at this "
                         "seat, with evidence text (recorded in output). REQUIRED to reach "
                         "LANDED-AND-ADVANCED: ancestor-containment is monotone and cannot "
                         "detect regression, so provenance alone is never a pass.")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    sections = [s.strip() for s in args.payload_sections.split(",") if s.strip()]
    bad = [s for s in sections if s not in SHA_SECTIONS]
    if bad:
        print(f"unknown --payload-sections: {', '.join(bad)} "
              f"(known: {', '.join(SHA_SECTIONS)})", file=sys.stderr)
        return 3

    repo = os.path.expanduser(args.repo)
    if not os.path.isdir(os.path.join(repo, ".git")) and not _git(repo, "rev-parse", "--git-dir"):
        print(f"UNVERIFIABLE {repo}: not a git repository", file=sys.stderr)
        return 3

    trunk_ref, trunk_how = resolve_trunk(repo)
    disk = disk_version(repo)
    head = version_at(repo, "HEAD")
    trunk = version_at(repo, trunk_ref)
    payload_ok, report = check_payload(repo, args.manifest, trunk_ref, sections)

    # ANCESTOR-CONTAINMENT: only asked when the payload actually mismatches, and it must
    # hold for EVERY mismatching file. One file this seat never held is enough to make the
    # whole claim false -- "some of the payload arrived" is not a landing.
    advanced = None
    held_detail = []
    if payload_ok is False and report["mismatched"]:
        results = []
        for row in report["mismatched"]:
            h = ever_held(repo, row["path"], row["want"])
            results.append(h)
            held_detail.append({"path": row["path"], "ever_held": h})
        advanced = all(r is True for r in results)

    pin = check_pin(repo, trunk_ref, args.version)
    capability = args.capability_attested or None
    verdict = classify(disk, head, trunk, payload_ok, args.version, advanced, capability)
    payload_state = ("UNCHECKED" if payload_ok is None
                     else "MATCH" if payload_ok else "DIVERGENT")
    # The published pin BLOCKS only where the repo is publicly readable (principal ruling
    # 2026-07-29). Reported for every seat either way -- the scope is stated, not silent.
    pin_blocks = pin["blocking"] and pin["state"] in ("DRIFTED", "COMMITTED-NOT-PUBLISHED")

    if args.json:
        print(json.dumps({
            "repo": repo, "verdict": verdict,
            "version_disk": disk, "version_head": head, "version_trunk": trunk,
            "trunk_ref": trunk_ref, "trunk_resolved_by": trunk_how,
            "payload": payload_state, "payload_ref": report["ref"],
            "payload_sections_scored": report["sections_scored"],
            "payload_sections_excluded": report["sections_excluded"],
            "payload_per_section": report["per_section"],
            "payload_detail": report["details"],
            "worktree_drift": sorted(set(report["worktree_drift"])),
            "advanced": advanced,
            "ancestor_containment": held_detail,
            "capability_attested": capability,
            "pin": pin,
            "pin_blocks": pin_blocks,
        }, indent=2))
    else:
        print(f"{verdict:15s} {os.path.basename(repo.rstrip('/'))}")
        print(f"  version  disk={disk}  trunk[{trunk_ref}]={trunk}  HEAD={head}  "
              f"want={args.version}")
        print(f"  trunk    {trunk_how}")
        print(f"  payload  {payload_state}"
              + (f" (at {report['ref']})" if report["ref"] else ""))
        for sect, t in report["per_section"].items():
            hashed = t["match"] + t["mismatch"]
            line = f"             {sect:18s} {t['match']}/{hashed} hash-match"
            if t["mismatch"]:
                line += f", {t['mismatch']} MISMATCH"
            if t["declared_absent"]:
                line += (f", {t['declared_absent']} declared-absent"
                         " (never shipped — not scoreable)")
            if t["present_but_declared_absent"]:
                line += f", {t['present_but_declared_absent']} PRESENT-ANOMALY"
            print(line)
        if report["sections_excluded"]:
            # Never let a scoped pass read as a full one.
            print(f"           ⚠ NOT SCORED: {', '.join(report['sections_excluded'])}"
                  f" — this result is scoped to the sections above")
        for d in report["details"]:
            print(f"           {d}")
        drift = sorted(set(report["worktree_drift"]))
        if drift:
            print(f"  drift    working tree differs from {trunk_ref} at "
                  f"{len(drift)} payload file(s): {', '.join(drift)}")
            print("           Reported, NOT counted against the verdict — the committed")
            print("           state is what the seat durably holds.")
        if verdict == "OFF-TRUNK":
            print(f"  ⛔ Committed, but {trunk_ref} does not carry it. Every HEAD-based")
            print("     probe passes. The remedy is a merge, not a re-migration.")
        if verdict == "NOT-COMMITTED":
            print("  ⛔ The working tree is correct and nothing is committed. Every")
            print("     filesystem probe passes. One `git checkout` reverts the migration.")
        if verdict == "VERSION-ONLY":
            print("  ⛔ The version claims delivery the payload does not support.")
        for h in held_detail:
            print(f"  ancestor {h['path']}: ever held pinned blob = {h['ever_held']}")
        if verdict == "LANDED-AND-ADVANCED":
            print(f"  ✅ Held the payload, then advanced past it. Capability attested: "
                  f"{capability}")
            print("     Provenance + capability. Ancestor-containment ALONE is monotone")
            print("     and cannot detect regression — the attestation is what carries it.")
        if verdict == "ADVANCED-UNPAIRED":
            print("  ⛔ This seat HELD the payload and advanced past it, but no capability")
            print("     attestation was supplied. Ancestor-containment is monotone: a seat")
            print("     whose payload was reverted or damaged reads identically here.")
            print("     Re-run with --capability-attested '<probe-7 evidence>'.")
        print(f"  pin      @aget-canonical-specs: {pin['state']}  "
              f"(worktree={pin['worktree']} trunk={pin['trunk']} "
              f"published={pin['published']})")
        print(f"           scope: {'BLOCKING (publicly readable)' if pin['blocking'] else 'advisory (private — peers read trunk on the filesystem, L480)'}")
        if pin_blocks:
            print("  ⛔ Published pin is stale on a PUBLICLY READABLE repo. This is the one")
            print("     surface a remote consumer actually reads. Blocking.")

    # Three states, not two (gh#2045 request 2): UNVERIFIABLE is not FAIL, and collapsing
    # them trains readers to ignore it.
    if verdict == "UNVERIFIABLE":
        return 2
    if verdict in ("LANDED", "LANDED-AND-ADVANCED"):
        return 1 if pin_blocks else 0
    return 1


if __name__ == "__main__":
    sys.exit(main())
