#!/usr/bin/env python3
"""The reviewed protected-write script for one batch (route a1). Dry-run unless --apply.

Run by the supervisor from this repository's root, under the principal's typed batch line, after the list is
reviewed (procedure step B7). The read-only trial run is plan_protected.py:
    python3 scripts/migration_kit/plan_protected.py --list <list.json>              # trial run, writes nothing
    python3 scripts/migration_kit/apply_protected.py --list <list.json> --apply     # write

What it does, and what it refuses (R4 all-or-nothing apply; R1 containment at the act):
- Refuses to run if its own sha256 differs from the one recorded in the list, so the reviewed script is the one run.
  That, an unreadable list, or a list that does not parse, is a batch refusal (C1): exit 2, nothing written anywhere.
- Phase A plans EVERY Aget before any write. Per Aget, the plan refuses the WHOLE Aget (C2: nothing written there)
  when: a file to be written differs from the list's `pre`, or a `noop` file from its `post` (the Aget changed since
  the list was prepared; `hold` and `hold-line` files are not compared); a listed path, or a folder on its way that
  exists, is a symbolic link, is not a folder, or resolves outside the Aget's folder; the target is not a regular
  file with one name, or is absent where the list's `pre` is not `absent` (copy_isolation.destination_refusal());
  the list entry names no `head`, or the Aget's HEAD differs from it.
- Phase B, per Aget: the receipt is written first with that Aget IN-PROGRESS, the preconditions are tested again
  (C2 on refusal), and copy_isolation.write_all() writes every file or none. Each write goes through the contained
  writer (an fd walk with O_NOFOLLOW to the folder, a temp file, a read-back, a rename: never through a link and
  never by truncating a file in place). A failure after the first write is rolled back and read back: REFUSED with
  `rolled_back` (C3) only when every target reads back as before; otherwise ROLLBACK-INCOMPLETE (C4), naming each
  path restored and not restored. One Aget's failure never stops the others.
- An interrupt (Ctrl-C, or SIGTERM, which is turned into the same exception) is C5 whatever else is true at that
  moment (C5 takes precedence over C3 and C4, which then describe only the in-flight Aget's rollback): no further
  Aget is started, the ones not reached read NOT-STARTED, the receipt is written, and the exit is 130. A kill that
  cannot be caught (C6) leaves the receipt with that Aget IN-PROGRESS.
- Results: APPLIED, WOULD-APPLY (dry run), REFUSED, SKIPPED, ROLLBACK-INCOMPLETE, NOT-STARTED, or IN-PROGRESS (left
  only by a killed run). Exit: 130 interrupted; 2 batch refusal; else 3 if any Aget is ROLLBACK-INCOMPLETE or the
  final receipt could not be written; else 1 if any is REFUSED; else 0. No path ends in a traceback.
- Phase B makes each Aget's plan again and refuses it (nothing written) if anything Phase A read has changed; the
  writer also checks that each target still holds the listed `pre` bytes. An interrupt that arrives during a
  rollback is still C5. An IN-PROGRESS receipt that cannot be written refuses that Aget before its first write.
- Stated limit (exclusive mutation): every guarantee here holds only while nothing but this apply changes the
  Aget's folder tree and its listed files for the whole run. That excludes a second kit run and ANY other process
  that writes, renames or moves a folder in the Aget. A folder the writer has opened can be moved out of the Aget by
  another process; the writer re-walks to it immediately before each act (each mkdir, temp file, rename, unlink and
  rmdir), which narrows that window and does not close it: a move after the last re-walk is not seen.
- Writes `write` / `write-upstream` entries (the bytes their `source` names, verified against `source_sha256`), a
  `replace-line` entry (the single old `@aget-version` line) and a `rewrite-claude-ignore` entry (the single bare
  `.claude/` line). Writes nothing for `hold`, `hold-line` or `noop` entries; a `noop` file is still read and checked, including its release executable bit when it names a payload source.
  A wrong-bit payload noop refuses with RELEASE MODE MISMATCH; re-prepare to list the mode-only protected write.
  With --apply, the receipt goes into --receipt-dir (default: this script's folder); the after-run check compares
  each receiver against it.
Writes no file other than the listed paths and that receipt. Never commits, launches or pushes.
"""
import argparse
import datetime as dt
import getpass
import hashlib
import json
import os
import signal
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_target as R  # noqa: E402  (the kit's one release parameter; carriage row 24)
import copy_isolation as CI  # noqa: E402  (destination_refusal: a write never goes through a link)
import result_binding as RBND  # noqa: E402  (atomic_write: the receipt's temp file is never a link)
import item_meaning as IM  # noqa: E402  (R3: every item's (op, kind) has a row before anything is skipped)

HERE = Path(__file__).resolve().parent
# BIND (R1-T7): a list entry's location must be the location this register records for its Aget, or lie inside the
# run folder a rehearsal names with --run
REGISTER = R.ROOT / ".aget" / "fleet" / "FLEET_STATE.yaml"
WRITE_OPS = ("write", "write-upstream", "replace-line", "rewrite-claude-ignore")
# R3: the closed set of ops this script understands; any other is refused at the plan.
APPLY_OPS = WRITE_OPS + ("noop", "hold", "hold-line", "unsafe")
OLD_LINE, NEW_LINE = f"@aget-version: {R.FROM}", f"@aget-version: {R.TO}"
# gh#1569, the rewrite scripts/apply_skill_tracking.py performs: a bare `.claude/` is a directory pattern git never
# descends, so no negation below it can work; `.claude/*` is descended, and `!.claude/skills/` then tracks skills.
CLAUDE_IGNORE_NEW = (".claude/*\n"
                     "# Skills are agent capability, not churning state: untracked here\n"
                     "# meant one `rm` from unrecoverable. The negation works only because\n"
                     "# the parent rule is `.claude/*` (git descends), not `.claude/`.\n"
                     "!.claude/skills/")


def rewrite_claude_ignore(text):
    """Exactly one line that is `.claude/` becomes the tracked-skills form; anything else refuses (None)."""
    lines = text.split("\n")
    hits = [i for i, ln in enumerate(lines) if ln.strip() == ".claude/"]
    if len(hits) != 1:
        return None
    lines[hits[0]] = CLAUDE_IGNORE_NEW
    return "\n".join(lines)


def sha(b):
    """Return the SHA-256 hex digest of the bytes, or 'absent' when given None."""
    return hashlib.sha256(b).hexdigest() if b is not None else "absent"


def self_sha():
    """Return the SHA-256 hex digest of this script's own file, which a reviewed list must name."""
    return sha(Path(__file__).read_bytes())


def framework_root():
    """Return the folder that holds the framework's repositories."""
    return R.framework_root()


def release_bytes(source, with_mode=False):
    """Return the bytes named by a 'repo@rev:path' source (rev is a tag or other revision), read by git show, or None."""
    repo, rest = source.split("@", 1)
    tag, path = rest.split(":", 1)
    # B191 finding 1: only a regular file at the revision is release bytes; a link, folder, submodule or failed read
    # raises InspectionFailed
    return CI.git_blob_at(framework_root() / repo, tag, path, with_mode=True) if with_mode else CI.git_blob_at(
        framework_root() / repo, tag, path)


def replace_version_line(text):
    """Return the text with its single old version line replaced, or None unless exactly one such line exists."""
    lines = text.split("\n")
    if sum(1 for ln in lines if ln.strip() == OLD_LINE) != 1:
        return None
    return "\n".join(NEW_LINE if ln.strip() == OLD_LINE else ln for ln in lines)


def bind_refusal(entry, run=None):
    """BIND (R1-T7; copy_isolation.member_refusal()): why the entry's location is not one this script may write, as
    "NOT A MEMBER LOCATION: …", or None. It must be the location the fleet register (REGISTER) records for the
    entry's Aget, or lie inside `run`, the run folder a rehearsal names with --run. Asked before each plan_aget()."""
    why = CI.member_refusal(entry["aget"], entry["location"], run, REGISTER)
    return f"NOT A MEMBER LOCATION: {why}" if why else None


def plan_aget(entry):
    """(ok, reason, actions) with actions = [(path, bytes_to_write, expected_post)]; no side effects. R4 pre_ok:
    (a) containment and (b) file type through copy_isolation.destination_refusal(op="write"), (c) the byte
    preconditions, (d) HEAD equal to the list entry's `head` (required). Its callers ask bind_refusal() first."""
    loc = Path(entry["location"])
    if not entry.get("head"):
        return False, "NO HEAD: the list entry names no head; re-prepare the list", []
    actions = []
    for op in entry["ops"]:
        if op["op"] not in APPLY_OPS:        # R3 clause 3 (S-221): an unknown label is refused, never written
            return False, f"UNKNOWN CLASSIFICATION: {op['path']} has op {op['op']!r}", []
        try:                                 # B148 finding 2: a hold is skipped only once its (op, kind) has a row
            IM.meaning(op)
        except IM.UnknownClassification as e:
            return False, f"UNKNOWN CLASSIFICATION: {e}", []
        if op["op"] in ("hold", "hold-line", "unsafe"):
            continue
        why = CI.destination_refusal(loc, op["path"], "write")
        if why:
            return False, f"UNSAFE PATH: {why}", []
        f = loc / op["path"]
        cur = f.read_bytes() if os.path.lexists(f) else None
        if op["op"] == "noop":
            if sha(cur) != op["post"]:
                return False, f"STALE: {op['path']} changed since the list (noop entry)", []
            if "source_sha256" in op:
                source = release_bytes(op["source"], with_mode=True)
                if source is None or sha(source[0]) != op["source_sha256"]:
                    return False, f"SOURCE MISMATCH: {op['source']}", []
                if "release_mode" in op and op["release_mode"] != source[1]:
                    return False, f"SOURCE MODE MISMATCH: {op['source']}; re-prepare the list", []
                actual = 0o755 if f.stat().st_mode & 0o100 else 0o644
                if actual != source[1]:
                    return False, f"RELEASE MODE MISMATCH: {op['path']} (noop); re-prepare the protected list", []
            continue
        if sha(cur) != op["pre"]:
            return False, f"STALE: {op['path']} is {sha(cur)[:8]}, the list recorded {op['pre'][:8]}", []
        if op["op"] == "replace-line":
            new = replace_version_line(cur.decode())
            data = new.encode() if new is not None else None
        elif op["op"] == "rewrite-claude-ignore":
            new = rewrite_claude_ignore(cur.decode()) if cur is not None else None
            data = new.encode() if new is not None else None
        else:                                # write, write-upstream (APPLY_OPS)
            source = release_bytes(op["source"], with_mode=True)
            data = source[0] if source is not None else None
            if data is not None and sha(data) != op["source_sha256"]:
                return False, f"SOURCE MISMATCH: {op['source']}", []
            if source is not None and "release_mode" in op and op["release_mode"] != source[1]:
                return False, f"SOURCE MODE MISMATCH: {op['source']}; re-prepare the list", []
        if data is None or sha(data) != op["post"]:
            return False, f"CANNOT PRODUCE the listed post bytes for {op['path']}", []
        actions.append((op["path"], data, op["post"]))
    head = CI.head_of(loc)
    if head != entry["head"]:
        return False, f"HEAD MOVED: {loc} is at {head or 'no repository of its own'}, the list names {entry['head']}", []
    return True, "", actions


def shape_refusal(entries):
    """Why the list's members are not well-formed, or None: each is an object with string `aget` and `location`,
    and `ops` a list of objects each with string `path` and `op`. Tested before any member act (C1)."""
    for i, e in enumerate(entries):
        if not isinstance(e, dict) or not isinstance(e.get("aget"), str) or not isinstance(e.get("location"), str):
            return f"member {i} is not an object with string `aget` and `location`"
        ops = e.get("ops")
        if not isinstance(ops, list) or not all(isinstance(o, dict) and isinstance(o.get("path"), str)
                                                and isinstance(o.get("op"), str) for o in ops):
            return f"member {e['aget']}: `ops` is not a list of objects with string `path` and `op`"
    return None


def _write_receipt(path, receipt, run_id=None):
    """Write the whole receipt atomically: a new temp file (O_EXCL, a random name, so never an existing link or
    second name; B143) in the same folder, then os.replace, which replaces the name and never follows it. With
    `run_id` (the final write, R2-T17) the receipt is written as that run's result (result_binding.write_result: the
    run id in the receipt, then the FINISHED row); the IN-PROGRESS writes are not results, so a killed run leaves a
    receipt no consumer reads."""
    if run_id:
        RBND.write_result("apply_protected", path, receipt, run_id, binding={"list_sha256": receipt.get("list_sha256")})
    else:
        RBND.atomic_write(path, (json.dumps(receipt, indent=2) + "\n").encode())


def _on_sigterm(signum, frame):
    raise KeyboardInterrupt(f"signal {signum}")


def phase_a(entries, only, run=None):
    """Plan every Aget before any write: [(entry, verdict, why, actions)], verdict None (planned), SKIPPED or REFUSED.
    A plan that raises is that Aget's REFUSED (C2); a KeyboardInterrupt propagates to the caller (C5)."""
    planned = []
    for entry in entries:
        if only and entry["aget"] not in only:
            continue
        if entry.get("blocked"):
            planned.append((entry, "SKIPPED", entry["blocked"], None))
            continue
        try:
            why = bind_refusal(entry, run)
            ok, why, actions = (False, why, []) if why else plan_aget(entry)
        except Exception as e:                                            # noqa: BLE001 — C2, no traceback
            ok, why, actions = False, f"PLAN FAILED: {type(e).__name__}: {e}", []
        planned.append((entry, None if ok else "REFUSED", why, actions))
    return planned


def _held(entry):
    """D2 (R3, DESIGN's apply-receipt clause): the held paths with their op, kind and listed `pre`, so after-run A
    compares a held protected file kept as it was by identity."""
    return [dict(o) for o in entry["ops"] if o["op"] in ("hold", "hold-line")]   # D3 (B200 finding 4): the whole entry


def apply_one(entry, actions, pre, run=None):
    """Phase B for one Aget: the member record, from write_all()'s category. `pre` maps path -> listed `pre`.
    Every Phase A precondition is tested again first (the plan is made again and must produce the same actions; B141
    finding 1: an Aget changed after Phase A must not be overwritten), and the writer is given the listed `pre` of
    each target, so the bytes it records are the bytes the plan was made from."""
    loc = Path(entry["location"])
    refusals = CI.write_refusals(loc, [(p, pre[p]) for p, _, _ in actions], head=entry["head"])
    if refusals:
        return {"aget": entry["aget"], "result": "REFUSED", "why": "; ".join(refusals)}, None
    why = bind_refusal(entry, run)
    ok, why, again = (False, why, []) if why else plan_aget(entry)
    if not ok or again != actions:
        return {"aget": entry["aget"], "result": "REFUSED",
                "why": why or "the plan made again differs from Phase A's; the Aget changed after it was planned"}, None
    modes = {}
    for op in entry["ops"]:
        if op["op"] in ("write", "write-upstream"):
            source = release_bytes(op["source"], with_mode=True)
            if source is None or sha(source[0]) != op["source_sha256"]:
                return {"aget": entry["aget"], "result": "REFUSED", "why": f"SOURCE MISMATCH: {op['source']}"}, None
            if "release_mode" in op and op["release_mode"] != source[1]:
                return {"aget": entry["aget"], "result": "REFUSED",
                        "why": f"SOURCE MODE MISMATCH: {op['source']}; re-prepare the list"}, None
            modes[op["path"]] = source[1]
    res = CI.write_all(loc, actions, expect_pre={p: pre[p] for p, _, _ in actions}, modes=modes)
    if res.ok():
        return {"aget": entry["aget"], "result": "APPLIED", "location": entry["location"],   # C2d (pre-read 1)
                "files": [{"path": p, "post": post, "ok": True,
                           **({"release_mode": modes[p]} if p in modes else {})} for p, _, post in actions]}, res
    if res.category in ("C2", "C3"):
        rec = {"aget": entry["aget"], "result": "REFUSED", "why": res.why, "rolled_back": res.rolled_back}
    else:
        rec = {"aget": entry["aget"], "result": "ROLLBACK-INCOMPLETE", "why": res.why, "restored": res.restored,
               "not_restored": res.not_restored}
    return rec, res


def main(argv=None):
    """Command-line entry point: apply the reviewed protected-write list; a dry run unless --apply is given."""
    R.require()
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--list", type=Path, required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--receipt-dir", type=Path, default=HERE)
    ap.add_argument("--run", help="a rehearsal's run folder: an entry whose location lies inside it is a copy, and "
                                  "is planned without its register location (BIND, R1-T7)")
    a = ap.parse_args(argv)
    try:                                                                  # C1: batch input
        raw = a.list.read_bytes()
        doc = json.loads(raw)
        batch, entries = doc["batch"], list(doc["agets"])
        bad = shape_refusal(entries)                                      # B141 finding 5: parsed is not well-formed
        if bad:
            raise TypeError(bad)
    except (OSError, ValueError, KeyError, TypeError) as e:
        print(f"REFUSED: the list {a.list} cannot be read ({type(e).__name__}: {e}); nothing was written.")
        return 2
    if doc.get("apply_script_sha256") != self_sha():
        print(f"REFUSED: this script is {self_sha()[:12]}, the reviewed list names "
              f"{str(doc.get('apply_script_sha256'))[:12]}. Run the reviewed script, or re-prepare the list.")
        return 2
    receipt = {"schema": "v336_protected_apply_receipt/1", "batch": batch, "mode": "apply" if a.apply else "dry-run",
               "list_sha256": sha(raw), "apply_script_sha256": self_sha(), "run_by": getpass.getuser(),
               "started": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "agets": []}
    out = a.receipt_dir / f"APPLY_RECEIPT_batch{batch}_{dt.datetime.now().strftime('%Y%m%dT%H%M%S')}.json"
    run_id = None
    if a.apply:      # R2-T17 (D-4): the run is recorded before any member act; only its final receipt is a result
        try:
            run_id = RBND.start_run("apply_protected", out)
        except RBND.RunLogError as e:
            print(f"REFUSED: this run cannot be recorded ({e}); nothing was written")
            return 2
    # C5 covers the whole invocation (B143 finding 3): the SIGTERM handler is installed before Phase A, and an
    # interrupt during Phase A or the final receipt write is C5 as well.
    old = signal.signal(signal.SIGTERM, _on_sigterm) if a.apply else None
    interrupted = False
    # Phase A: plan every Aget before any write.
    planned = []
    try:
        planned = phase_a(entries, a.only, a.run)
    except KeyboardInterrupt:
        interrupted = True
        planned = [(e, "NOT-STARTED", "interrupted during planning; nothing was written", None) for e in entries
                   if not a.only or e["aget"] in a.only]
    records = {}
    try:
        for entry, verdict, why, actions in planned:
            name = entry.get("aget", "?")
            if interrupted:
                records[name] = {"aget": name, "result": "NOT-STARTED"}
                continue
            if verdict == "SKIPPED":
                records[name] = {"aget": name, "result": "SKIPPED", "why": why}
                continue
            if verdict == "REFUSED":
                records[name] = {"aget": name, "result": "REFUSED", "why": why}
                continue
            if not a.apply:
                records[name] = {"aget": name, "result": "WOULD-APPLY",
                                 "files": [{"path": p, "post": post, "ok": True} for p, _, post in actions],
                                 "held": _held(entry)}
                continue
            records[name] = {"aget": name, "result": "IN-PROGRESS"}
            receipt["agets"] = [records[e.get("aget", "?")] for e, *_ in planned if e.get("aget", "?") in records]
            try:
                _write_receipt(out, receipt)
            except OSError as e:                                          # B141 finding 4: no write begins without it
                records[name] = {"aget": name, "result": "REFUSED",
                                 "why": f"the IN-PROGRESS receipt could not be written ({e}); nothing was written"}
                continue
            pre = {o["path"]: o.get("pre") for o in entry["ops"]}
            res = None
            try:
                rec, res = apply_one(entry, actions, pre, a.run)
            except KeyboardInterrupt:
                rec, interrupted = {"aget": name, "result": "REFUSED", "why": "interrupted before the first write"}, True
            except Exception as e:                                        # noqa: BLE001
                # write_all() was called and raised: a write may have begun, so no unverified REFUSED (C4)
                rec = {"aget": name, "result": "ROLLBACK-INCOMPLETE", "why": f"{type(e).__name__}: {e}",
                       "restored": [], "not_restored": [{"path": p, "why": "unknown"} for p, _, _ in actions]}
            if res is not None and res.interrupted is not None:
                interrupted = True
            rec["held"] = _held(entry)
            records[name] = rec
    except KeyboardInterrupt:
        interrupted = True
    finally:
        for entry, *_ in planned:
            records.setdefault(entry.get("aget", "?"), {"aget": entry.get("aget", "?"), "result": "NOT-STARTED"})
        receipt["agets"] = [records[e.get("aget", "?")] for e, *_ in planned]
        receipt["ended"] = dt.datetime.now().astimezone().isoformat(timespec="seconds")
        if interrupted:
            receipt["interrupted"] = True
        receipt_error, landed = None, False

        def _landed():
            # C2d (FWK-OVSR8's C2d pre-read 2): an interrupt after the FINISHED row leaves this run's receipt current;
            # it is recorded, and a retry (refused: the run already finished) must not report it as not written
            doc, why = RBND.read_current("apply_protected", out)
            return why is None and isinstance(doc.get("binding"), dict) and doc["binding"].get("run_id") == run_id
        if a.apply:
            for attempt_no in (1, 2):                 # an interrupt here is C5 too; the receipt is written once more
                try:
                    _write_receipt(out, receipt, run_id)   # R2-T17: the final receipt is this run's result
                    receipt_error = None
                    break
                except KeyboardInterrupt as e:
                    interrupted, receipt["interrupted"], receipt_error = True, True, e
                    if _landed():
                        receipt_error, landed = None, True
                        break
                except (OSError, RBND.RunLogError) as e:
                    receipt_error = e
                    if _landed():
                        receipt_error, landed = None, True
                    break
        if old is not None:
            signal.signal(signal.SIGTERM, old)
    if landed:
        print(f"RECEIPT RECORDED: {out} was written and recorded before the interrupt; the receipt does not carry the "
              "interrupt, and every member result below is in it.")
    if receipt_error is not None:
        print(f"RECEIPT NOT WRITTEN: {out} ({receipt_error}). The member results below are not recorded anywhere; "
              "re-check each member by hand before any further step.")
    for r in receipt["agets"]:
        held = r.get("held") or []
        extra = r.get("why") or ((f"{len(r.get('files', []))} file(s)" + (f"; held {len(held)}" if held else ""))
                                 if "files" in r else "")
        print(f"{r['aget']:34s} {r['result']:12s} {str(extra)[:100]}")
    if a.apply:
        print(f"receipt: {out}")
    else:
        print("dry run: nothing written. Add --apply to write.")
    results = {r["result"] for r in receipt["agets"]}
    if interrupted:
        return 130
    if receipt_error is not None:
        return 3
    if "ROLLBACK-INCOMPLETE" in results:
        return 3
    if "REFUSED" in results:
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
