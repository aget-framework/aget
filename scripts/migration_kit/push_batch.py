#!/usr/bin/env python3
"""Batch 1 phase 2: each receiver pushes its own receipt commit, only if its after-run verdict file says PASS.
Dry-run unless --push. `--push` checks the batch's recorded PUSH line before any receiver's gate (exit 6 without one
that passes). Only a records entry keyed with the batch key and `:push` is read (`record_authority.py --act push`
writes it); the batch's launch line is never push authority. The push line must also have the one fixed form (the
prefix, then `push the commits of batch N`, optionally more batches and ` with commit SHA`; a test of form, not a
reading of meaning: a line worded any other way is refused), and equal the whole typed prompt it is
found in, runs of whitespace collapsed and a pasted block among other words left out. The line counts as typed when
the newest principal entry in which check_principal_line.py finds it is a typed prompt other than a session's first,
or a human-origin entry queued mid-turn whose prompt source the tool does not read (batch_authority.py).

Per receiver, refuses unless ALL hold:
  - <evidence>/<aget>/after_run_check.json says PASS (a plain file in the --evidence folder; its origin is not
    verified, and the same holds for suite_at_commit.json);
  - the receiver's HEAD still equals the head_after in launch_record.json, or, when HEAD moved, is the one commit --extra-commit names;
  - the working tree has no change other than the packet's `pre_dirty`, the paths dirty at launch, and --allow-dirty;
  - the push is a fast-forward of the remote branch.
--extra-paths and --allow-dirty come from the command line alone: no typed line is compared with them; --extra-commit
must be a commit the recorded push line names (R2-T12).
A receiver this gate refuses prints NOT PUSHED and the refusal does not change the exit code: a run in which every
receiver is refused exits 0.
Then one headless receiver session to which this tool passes two allow rules, that exact push and `git ls-remote` of
that branch, and no deny list (the harness's built-in read-only allowance is left in place; this session's transcript
is not checked), and a read-only `git ls-remote` here confirming the remote now holds exactly that revision. Never
force-pushes.

Usage: python3 scripts/migration_kit/push_batch.py --packet <packet.json> [--only N ...] [--push]
"""
import argparse
import hashlib
import json
import os
import subprocess
import sys
import uuid
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_target as R  # noqa: E402  (the kit's one release parameter; carriage row 24)
import result_binding as RBND  # noqa: E402  (R2: the verdict and the receipt must be bound to this run)
import copy_isolation as CI  # noqa: E402  (git_paths: path listings read byte for byte, B158 finding 1)
import item_meaning as IM  # noqa: E402  (R3: one meaning table per classification)

HERE = Path(__file__).resolve().parent


def git(loc, *args):
    """Run a git read at the location and return the completed process; the read leaves the member's git folder as
    it was (copy_isolation.read_git(); B166 finding 2)."""
    return CI.read_git(loc, *args, text=True)


def push_command(r, push_cmd, branch, prompt, sid):
    """route-b-restricted-hooks (ruled 2026-09-27) applies to the push session too: no settings file's rules load; the
    receiver's own hooks come through --settings; the two allow rules this command passes are the exact
    push and ls-remote (the harness's built-in read-only allowance is left in place, and no after-run check reads this
    session)."""
    return ["claude", "-p", "--session-id", sid, "--restricted", "--tools", "Bash", "--settings", r["settings"]["path"],
            "--permission-mode", "dontAsk", "--permission-prompts", "none", "--allowedTools", f"Bash({push_cmd})",
            f"Bash(git ls-remote origin refs/heads/{branch})", "--output-format", "stream-json", "--verbose",
            "--max-turns", "6", prompt]


def untracked_writes(r, head, receipt_files=()):
    """Every path this batch wrote for the member that is NOT in the commit it would push (G3.6 row 10, 2026-09-28).
    Batch 7 pushed three receivers whose protected skills were written on disk but git-ignored, so the pushes could not
    carry them (PAYLOAD-NONCONFORMING); on-disk digests could not see it. Covers the packet's written items, the apply
    receipt's files (the protected writes) and a track-skills member's paths."""
    if r.get("mode") == "track-skills":
        # Batch 9t (2026-09-29): a skill-tracking pass run BEFORE the migration writes only what its apply receipt
        # names (.gitignore) and commits its track paths; its packet's release items are the migration's, not written
        # here. The rule is unchanged: every path this batch wrote or tracked must be in the pushed commit.
        for i in r.get("items", []):   # B151 finding 4: not read here, but an unknown classification still refuses
            IM.meaning(i)
        wrote = set(receipt_files) | set(r.get("track_paths") or [])
    else:
        # R3: what this batch wrote is what the meaning table says the session or the list writes (a KEEP item
        # is not written); an unknown classification raises and the gate refuses
        wrote = {i["path"] for i in r.get("items", []) if IM.meaning(i).write_set or IM.meaning(i).apply_writes
                 or IM.meaning(i).after_run == "release"}
        wrote |= set(receipt_files) | set(r.get("track_paths") or [])
    tracked = set(CI.git_paths(r["location"], "ls-tree", "-r", "--name-only", head))   # B158 finding 1
    return sorted(p for p in wrote if p not in tracked)


def extra_commit_ok(r, head, checked, extra):
    """One commit above the checked HEAD (meant for a receiver-authored one; authorship is not tested), named and
    bounded by --extra-commit and --extra-paths on the command line (for a live push, main() has checked that the
    recorded push line names --extra-commit, R2-T12; no typed line is compared with --extra-paths; batch 8's
    `predicatefix`, 2026-09-29, was a principal line): HEAD's id starts with the named id (8 or more characters),
    its only parent is the checked HEAD, and it touches at least one path, no path outside the named ones, and no
    path of a packet item (a path that is only in the apply receipt or the track paths is not tested). Returns a
    refusal reason, or None."""
    sha, paths = extra
    if not head.startswith(sha) or len(sha) < 8:
        return f"HEAD {head[:8]} is not the named extra commit {sha[:8]}"
    parents = git(r["location"], "rev-list", "--parents", "-n", "1", head).stdout.split()[1:]
    if parents != [checked]:
        return f"the extra commit's parents {[p[:8] for p in parents]} are not exactly the checked HEAD {checked[:8]}"
    try:
        touched = set(CI.git_paths(r["location"], "diff-tree", "--no-commit-id", "--name-only", "-r", head))   # B158
    except CI.InspectionFailed as e:
        return f"the extra commit's paths could not be listed: {e}"
    if not touched or not touched <= set(paths):
        return f"the extra commit touches {sorted(touched - set(paths)) or 'nothing'} beyond the named paths"
    written = {i["path"] for i in r.get("items", [])}
    if touched & written:
        return f"the extra commit touches paths the batch wrote: {sorted(touched & written)}"
    return None


def gate(r, evidence_root=None, receipt_files=None, extra=None, allow_dirty=None):
    """Return (push facts, '') when the receiver may push its commit, or (None, reason) when it may not."""
    ev = (evidence_root or HERE / "evidence") / r["aget"]
    try:
        launch = json.loads((ev / "launch_record.json").read_text())
        launch["head_after"]
    except (OSError, ValueError, KeyError, TypeError):
        return None, "no phase-1 evidence"
    # R2: the verdict counts only when it is the current run of the after-run check for this verdict file, names this
    # member and the session the launch record names (one identity contract, D-5), and reads PASS.
    doc, why = RBND.read_current("after_run_check", ev / "after_run_check.json")
    if why:
        return None, f"after-run verdict: {why}"
    why = RBND.verdict_bound_to_launch(doc, launch, r["aget"])
    if why:
        return None, f"after-run verdict: {why}"
    verdict = doc.get("verdict")
    if verdict not in RBND.SUCCESS["after_run_verdict"]:
        return None, f"after-run check {verdict}"
    head = git(r["location"], "rev-parse", "HEAD").stdout.strip()
    subject = (doc.get("binding") or {}).get("subject")
    if subject not in (launch["head_after"], head):
        return None, f"the verdict judged {str(subject)[:8]}, not the launch's commit {launch['head_after'][:8]}"
    if head != launch["head_after"]:
        why = extra_commit_ok(r, head, launch["head_after"], extra) if extra else None
        if not extra or why:
            return None, why or f"HEAD moved since the check ({head[:8]} != {launch['head_after'][:8]})"
    if head == r["head"]:
        return None, "no migration commit (HEAD equals the pre-migration HEAD)"
    # R2 (S-160, wrapper r7 F-1): the receiver's own terminal, read at the commit to be pushed, in the packet's
    # attempt section, by the receipt grammar; only ACCEPTED or BEHAVIOUR_VERIFIED is a success.
    try:                  # B189 finding 1: a regular file in the commit only (B166 finding 2: read_git's read flags)
        shown = CI.git_blob_at(r["location"], head, RBND.receipt_path(r))
    except CI.InspectionFailed as e:
        return None, f"the receipt in the commit to be pushed: {e}"
    if shown is None:
        return None, f"the receipt {RBND.receipt_path(r)} is not in the commit to be pushed"
    value, why = RBND.receipt_terminal(shown, r.get("attempt"))
    if why:
        return None, f"receipt terminal: {why}"
    if value not in RBND.SUCCESS["receiver_terminal"]:
        return None, f"the receiver's terminal is {value}, not a success"
    # Row 11 (framework Aget -dc's finding, 2026-09-28): the packet's pre_dirty is frozen at preparation, and paths
    # can appear between preparation and launch. The launch's own snapshot (settings_snapshot_pre.json, taken just
    # before the session) records every then-dirty path; both are allowed. Paths are listed the way that snapshot lists
    # them (diff against HEAD plus untracked, not-ignored FILES), not by `git status`, which collapses a folder.
    try:                                  # B158 finding 1: byte for byte; a failed listing refuses
        dirty = sorted(set(CI.git_paths(r["location"], "diff", "--name-only", "HEAD"))
                       | set(CI.git_paths(r["location"], "ls-files", "--others", "--exclude-standard")))
    except CI.InspectionFailed as e:
        return None, f"the working tree could not be listed: {e}"
    at_launch, why = launch_snapshot_dirty(ev, launch)     # R2-T10 (S-330): the launch's own snapshot only
    if why:
        return None, why
    # --allow-dirty (batch 9, 2026-09-29): exact paths given on the command line (no typed line is compared), e.g. the
    # receiver's own hook writing its friction ledger after launch; a push never carries uncommitted changes, and any
    # other path still refuses.
    extra = [p for p in dirty if p not in set(r.get("pre_dirty") or []) | at_launch | set(allow_dirty or {})]
    if extra:
        return None, f"uncommitted changes beyond the pre-existing ones: {extra[:3]}"
    branch = r["branch"]
    # R1 clause 1(c) (R1-T14): origin's push destination, as git resolves it now, must be the one recorded at B1
    now = git(r["location"], "remote", "get-url", "--push", "--all", "origin")
    if not r.get("push_url"):
        return None, "the packet records no push URL for this member; re-prepare the packet"
    if now.returncode or now.stdout.split() != list(r["push_url"]):
        return None, (f"origin now pushes to {now.stdout.split() or 'nothing readable'}, not the "
                      f"{r['push_url']} recorded at B1")
    remote = git(r["location"], "ls-remote", "origin", f"refs/heads/{branch}").stdout.split()
    if not remote:
        return None, f"remote branch {branch} unreadable"
    if git(r["location"], "merge-base", "--is-ancestor", remote[0], head).returncode != 0:
        return None, f"not a fast-forward of origin/{branch} ({remote[0][:8]})"
    if receipt_files is None and r.get("mode") != "track-skills":
        return None, "no apply receipt given (--apply-receipt): the protected writes cannot be checked as tracked"
    try:
        missing = untracked_writes(r, head, receipt_files or ())
    except IM.UnknownClassification as e:
        return None, f"R3: {e}"
    except CI.InspectionFailed as e:
        return None, f"the pushed commit's paths could not be listed: {e}"
    if missing:
        return None, (f"{len(missing)} path(s) this batch wrote are not in the commit, so the push cannot carry them "
                      f"(git-ignored?): {missing[:5]}")
    # SOP step B8a (plan G3.6 row 13 (a); supervisor:L844): a suite_at_commit.json naming the EXACT commit to be
    # pushed with verdict PASS (suite_at_commit.py writes one from a full run of the declared suite: clean clone,
    # siblings, CI exclusions, own hook). The gate reads the file's fields; it does not verify what wrote the file.
    if not (ev / "suite_at_commit.json").exists():
        return None, "no B8a record (suite_at_commit.json): run suite_at_commit.py on the commit to be pushed"
    sac, why = RBND.read_current("suite_at_commit", ev / "suite_at_commit.json")   # R2-T16 (c): the current run
    if why:
        return None, f"B8a record: {why}"
    if sac.get("sha") != head:
        return None, f"the B8a record names {str(sac.get('sha'))[:8]}, not the commit to be pushed {head[:8]}"
    # R2-T10 (S-161): the record is for this member, and its tree check judged the clone (a record whose tree check
    # was only recorded, as the packet rehearsal's reference run writes it, is not a B8a result)
    if sac.get("aget") != r["aget"]:
        return None, f"the B8a record is for {sac.get('aget')!r}, not {r['aget']!r}"
    if sac.get("tree_check") != "enforced":
        return None, f"the B8a record's tree check is {sac.get('tree_check')!r}, not 'enforced'"
    if sac.get("verdict") != "PASS":
        # C2a12 (C2b pre-read 2): one read (the current run, R2-T17), bound and then compared
        base, bwhy = RBND.read_current("baseline", ev / "baseline_record.json")
        why = baseline_bound(ev, r, launch, base=base, why=bwhy)   # R2-T10 (S-162): the baseline the launch sealed
        if why:
            return None, f"B8a {sac.get('verdict')} on {head[:8]}: {why}"
        ok, why = baseline_equal_ruled(ev, sac, head, base=base)   # the ruling's line is checked as typed (K1)
        if not ok:
            return None, f"B8a {sac.get('verdict')} on {head[:8]}: {sac.get('failures') or sac.get('why')}{why}"
    return {"head": head, "branch": branch, "remote_before": remote[0]}, ""


def launch_snapshot_dirty(ev, launch):
    """(paths dirty at launch, None), or (None, reason): the paths the launch's own pre-session snapshot
    (`settings_snapshot_pre.json`) lists as dirty, read only when its bytes have the sha256 the launch record names
    (`snapshot_sha256`, R2-T10, S-330), so a snapshot written or replaced after the launch cannot widen what the gate
    allows. No snapshot file: no path is allowed by it (nothing is widened). A file the launch record names no digest
    for, or another digest, refuses."""
    try:
        data = (ev / "settings_snapshot_pre.json").read_bytes()
    except FileNotFoundError:
        return set(), None
    except OSError as e:
        return None, f"the launch snapshot could not be read: {e}"
    want = launch.get("snapshot_sha256")
    if not want:
        return None, "the launch record names no snapshot digest, so the snapshot's dirty paths cannot be used"
    if hashlib.sha256(data).hexdigest() != want:
        return None, "the launch snapshot is not the one the launch record names (sha256 differs)"
    try:
        return set(json.loads(data).get("dirty") or {}), None
    except (ValueError, AttributeError) as e:
        return None, f"the launch snapshot could not be parsed: {e}"


_UNSET = object()      # C2a12 (C2a12 pre-read, LOW): a record whose JSON is `false` is not "not given"


def baseline_bound(ev, r, launch, base=_UNSET, why=None):
    """Why this member's baseline record cannot be read by the ruled route, or None (R2-T10, S-162; R2-T17): it must be
    the current run of the baseline for this record (a later baseline run that did not finish supersedes it), name this
    member (`aget`) and the packet's pre-migration HEAD (`head`), and, where the launch sealed a baseline slot, its
    `sha256` must be the slot digest the launch record names (`baseline_sha256`). With `base` (C2a12, C2b pre-read 2),
    the record the caller read once (and `why`, its read_current reason) is judged, never a second read."""
    if base is _UNSET:
        base, why = RBND.read_current("baseline", ev / "baseline_record.json")   # R2-T17: the current baseline run
    if why:
        return f"baseline record: {why}"
    if not isinstance(base, dict):
        return "no readable baseline record"
    if base.get("aget") != r["aget"]:
        return f"the baseline record is for {base.get('aget')!r}, not {r['aget']!r}"
    if base.get("head") != r["head"]:
        return f"the baseline record judged {str(base.get('head'))[:8]}, not the pre-migration HEAD {r['head'][:8]}"
    if launch.get("baseline_sha256") and base.get("sha256") != launch["baseline_sha256"]:
        return "the baseline record is not the baseline the launch sealed (sha256 differs)"
    return None


def baseline_equal_ruled(ev, sac, head, projects_dir=None, base=_UNSET):
    """A B8a FAIL passes only with a ruling file for THIS commit (evidence
    `baseline_equal_ruling.json`: {"sha", "line", "session", "source"}) AND a failure set exactly equal to the member's
    B6 baseline record (one receiver 2026-09-29: 15 failed + 13 errors before and after, no CI; the principal's typed
    ruling 01:00:16Z). A timeout or unreadable run never qualifies; nor does any new or missing failure.

    K1 (second rehearsal, 2026-10-01): the ruling file was written by hand and its line was never checked. The line
    must now be found in the transcripts whose names start with the session id the ruling names (every transcript in the
    folder searched when it names none), the newest match across them being a typed prompt that is not a session's
    first, or a human-origin entry queued mid-turn whose prompt source the tool does not read,
    and have the one fixed form (F-3): the prefix, then `the failures at SHA are baseline-equal`, SHA being 7 to 40
    characters this commit's id starts with (batch_authority.verify_ruling), and it must be the whole typed prompt.
    `record_authority.py --baseline-equal` writes the file. Limits: that is a test of form, not a reading of
    meaning (a ruling worded any other way is refused), and the line does not name the member;
    and the ruling, the baseline record and the B8a record are plain files in the --evidence folder whose origin is
    not verified."""
    try:
        ruling = json.loads((ev / "baseline_equal_ruling.json").read_text())
        if base is _UNSET:      # C2a12 (C2b pre-read 2): the caller's one read of the record it bound, when given
            # C2c (FWK-OVSR7's C2c pre-read M3): the default read is the current run's record too (read_current)
            base, why = RBND.read_current("baseline", ev / "baseline_record.json")
            if why:
                return False, f" (baseline record is not current: {why})"
    except (OSError, ValueError):
        return False, ""
    if not isinstance(base, dict):
        return False, ""
    if ruling.get("sha") != head or not ruling.get("line"):
        return False, " (baseline-equal ruling names another commit)"
    import batch_authority
    typed, how = batch_authority.verify_ruling(ruling, head, projects_dir)
    if not typed:
        return False, f" (baseline-equal ruling is not bound to a typed line: {how})"
    if sac.get("failures_complete") is not True:      # B179 finding 3: a cut failing id is not comparable
        return False, " (baseline-equal ruling needs a B8a failure list whose ids are all complete)"
    if sac.get("verdict") != "FAIL" or base.get("verdict") != "RECORDED":
        return False, " (baseline-equal ruling needs a completed FAIL run and a RECORDED baseline)"
    now, before = set(sac.get("failures") or []), set(base.get("failures") or [])
    if not now or now != before:
        return False, f" (not baseline-equal: new {sorted(now - before)[:3]}, gone {sorted(before - now)[:3]})"
    return True, ""


PUSH_RECEIVER_REQUIRED = ("aget", "location", "head", "branch")


def packet_refusal(packet, push):
    """Why the packet cannot be pushed from, or None: checked before the authority check and before the first
    receiver's push (BILD6's finding at E2c, same class as B148 finding 3 and B151 finding 6), so a malformed later
    receiver stops the run with nothing pushed instead of a traceback after an earlier receiver's push. Covers every
    receiver field the gate and the loop read by subscription, and `batch` when --push reads it."""
    if not isinstance(packet, dict) or not isinstance(packet.get("receivers"), list):
        return "the packet is not an object with a `receivers` list"
    if push and (not isinstance(packet.get("batch"), (str, int)) or isinstance(packet.get("batch"), bool)):
        return "a push needs `batch`, a string or an integer, for its authority check"
    for i, r in enumerate(packet["receivers"]):
        if not isinstance(r, dict) or not all(isinstance(r.get(k), str) for k in PUSH_RECEIVER_REQUIRED):
            return f"receiver {i} is not an object with string {', '.join(PUSH_RECEIVER_REQUIRED)}"
        for k in ("pre_dirty", "track_paths", "push_url"):
            v = r.get(k)
            if v is not None and not (isinstance(v, list) and all(isinstance(x, str) for x in v)):
                return f"receiver {r['aget']}: `{k}` is not a list of strings"
        items = r.get("items", [])
        if not isinstance(items, list) or not all(isinstance(x, dict) and isinstance(x.get("path"), str)
                                                  for x in items):
            return f"receiver {r['aget']}: `items` is not a list of objects with a string `path`"
        for k in ("mode", "receipt_path", "attempt"):
            if r.get(k) is not None and not isinstance(r[k], str):
                return f"receiver {r['aget']}: `{k}` is not a string"
        s = r.get("settings")
        if push and not (isinstance(s, dict) and isinstance(s.get("path"), str)):
            return f"receiver {r['aget']}: a push session needs `settings` with a string `path`"
    return None


def receipt_refusal(receipt):
    """Why the parsed apply receipt's shape cannot be read by the loop, or None (B152 finding 3: a later row's `files`
    was read per receiver, after an earlier receiver's push). The loop reads `agets`, each row's `aget` and `files`,
    and each file's `path`. Its currency and binding are not checked here (C2)."""
    if receipt is None:
        return None
    if not isinstance(receipt, dict) or not isinstance(receipt.get("agets"), list):
        return "it is not an object with an `agets` list"
    for i, x in enumerate(receipt["agets"]):
        if not isinstance(x, dict) or not isinstance(x.get("aget"), str):
            return f"row {i} is not an object with a string `aget`"
        files = x.get("files", [])
        if not isinstance(files, list) or not all(isinstance(f, dict) and isinstance(f.get("path"), str)
                                                  for f in files):
            return f"row {x['aget']}: `files` is not a list of objects with a string `path`"
    return None


def main(argv=None):
    """Command-line entry point: push each receiver's checked commit for phase 2; a dry run unless --push is given.

    Exit 1 with a message when the release target is incomplete (checked first); 2 when argparse rejects the arguments,
    when --extra-commit lacks --extra-paths or exactly one --only Aget, or when an --allow-dirty reason is empty; 6 when
    --push has no recorded typed authority; 1 when a push ran and was not confirmed. A run that reaches the end of the
    receiver loop with no unconfirmed push returns 0, also when the gate refused a receiver (it prints NOT PUSHED) or
    every receiver. Exit 2 also when a parsed packet lacks a field the gate or the loop reads (packet_refusal),
    checked before the authority check and before any push, or when the parsed apply receipt's shape cannot be read
    (receipt_refusal), checked before any push. An uncaught error (for example an unreadable packet or
    receipt, an --allow-dirty entry without "=",
    or a push session past its 1800-second timeout) ends in a traceback, exit 1."""
    R.require()
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--push", action="store_true")
    ap.add_argument("--evidence", type=Path, help="the run's evidence folder (default scripts/migration_kit/evidence)")
    ap.add_argument("--apply-receipt", type=Path, help="the batch's apply receipt: its files must be tracked at the "
                    "pushed commit (required for a migrating member; G3.6 row 10)")
    ap.add_argument("--extra-commit", metavar="SHA", help="one receiver-authored commit above the checked HEAD, "
                    "named in the principal's push line (with --extra-paths; --only one Aget)")
    ap.add_argument("--extra-paths", nargs="*", default=[], help="the only paths --extra-commit may touch")
    ap.add_argument("--allow-dirty", nargs="*", default=[], metavar="PATH=REASON",
                    help="an exact uncommitted path the principal allowed for this push (recorded)")
    a = ap.parse_args(argv)
    if a.extra_commit and (not a.extra_paths or not a.only or len(a.only) != 1):
        ap.error("--extra-commit needs --extra-paths and exactly one --only Aget")
    extra = (a.extra_commit, a.extra_paths) if a.extra_commit else None
    allow_dirty = dict(s.split("=", 1) for s in a.allow_dirty)
    if any(not v.strip() for v in allow_dirty.values()):
        ap.error("--allow-dirty needs PATH=REASON")
    packet_bytes = a.packet.read_bytes()      # C2a12 (C2b pre-read 2): one read, parsed and hashed
    packet = json.loads(packet_bytes)
    bad = packet_refusal(packet, a.push)
    if bad:
        print(f"NOT PUSHED: the packet {a.packet} cannot be used: {bad}; nothing was pushed")
        return 2
    if a.push:
        # carriage row 62: a live push needs the batch's typed authority, so a narrow allow rule that skips the
        # permission classifier does not also skip the principal.
        import batch_authority
        bound = []                # C2a12 (C2b pre-read 1): HEAD is tested against every character the line names
        ok, why = batch_authority.push_authority(packet["batch"], hashlib.sha256(packet_bytes).hexdigest(),
                                                 a.extra_commit, bound_out=bound)   # R2-T12: this packet, and a
        if not ok:                                                                  # named extra commit
            print(f"NOT PUSHED: no typed authority for batch {packet['batch']}: {why}")
            return 6
        if bound and bound[0]:
            extra = (bound[0], a.extra_paths)
        print(f"authority: {why}")
    evidence_root = a.evidence or HERE / "evidence"
    receipt = None
    if a.apply_receipt:              # R2-T17 (D-4): only the current run of the apply that wrote this receipt
        receipt, why = RBND.read_current("apply_protected", a.apply_receipt)
        if why:
            print(f"NOT PUSHED: the apply receipt {a.apply_receipt} cannot be used: {why}; nothing was pushed")
            return 2
    bad = receipt_refusal(receipt)       # B152 finding 3: before the first push, as the packet's fields are
    if bad:
        print(f"NOT PUSHED: the apply receipt {a.apply_receipt} cannot be used: {bad}; nothing was pushed")
        return 2
    code = 0
    for r in packet["receivers"]:
        if a.only and r["aget"] not in a.only:
            continue
        files = None
        if receipt is not None:              # R2-T6: only a bound entry (applying run, APPLIED, every file ok) counts
            # C2d (FWK-OVSR8's C2d pre-read 1): this packet's batch and this receiver's location
            entry, why = RBND.apply_entry(receipt, r["aget"], batch=packet.get("batch"), location=r.get("location"))
            if why:
                print(f"{r['aget']:34s} NOT PUSHED: {why}")
                continue
            files = [f["path"] for f in entry.get("files", [])]
        g, why = gate(r, evidence_root, files, extra, allow_dirty)
        if not g:
            print(f"{r['aget']:34s} NOT PUSHED: {why}")
            continue
        refspec = f"{g['head']}:refs/heads/{g['branch']}"
        push_cmd = f"git push origin {refspec}"
        if not a.push:
            print(f"{r['aget']:34s} WOULD PUSH {refspec} (fast-forward of {g['remote_before'][:8]})")
            continue
        prompt = (f"You are this repository's Aget. The supervisor's check of your {R.TO_TAG} migration passed and the "
                  "principal approved the push. Make exactly two Bash calls, with no other tool call:\n"
                  f"1. {push_cmd}\n2. git ls-remote origin refs/heads/{g['branch']}\n"
                  "Do not retry a refused or failed call. Report both outputs.")
        env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE" and not k.endswith("API_KEY")}  # rows 70/72
        cmd = push_command(r, push_cmd, g["branch"], prompt, str(uuid.uuid4()))
        p = subprocess.run(cmd, cwd=r["location"], env=env, capture_output=True, text=True, timeout=1800)
        ev = evidence_root / r["aget"]
        (ev / "push_stream.jsonl").write_text(p.stdout)
        after = git(r["location"], "ls-remote", "origin", f"refs/heads/{g['branch']}").stdout.split()
        ok = bool(after) and after[0] == g["head"]
        rec = {"aget": r["aget"], "refspec": refspec, "remote_before": g["remote_before"],
               "remote_after": after[0] if after else None, "pushed": ok, "session_exit": p.returncode,
               "allowed_dirty": allow_dirty}
        (ev / "push_record.json").write_text(json.dumps(rec, indent=2) + "\n")
        print(f"{r['aget']:34s} {'PUSHED' if ok else 'PUSH NOT CONFIRMED'} remote {(after[0] if after else '-')[:8]}")
        code = code or (0 if ok else 1)
    return code


if __name__ == "__main__":
    sys.exit(main())
