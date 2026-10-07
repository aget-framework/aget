#!/usr/bin/env python3
"""V3.7: one headless receiver session on a THROWAWAY COPY, launched with the real launch's command (route-b-restricted-hooks,
the packet's allowlist and prompt) but through `launch_batch.py --copy-root`, which runs NO typed-authority check and
accepts the folder only when it is apart from the receiver's own folder, git run in it names it as its own working tree
with its own .git folder, it carries this tool's custody marker for this packet and receiver, has no git remote, and
has its HEAD equal to the packet's; then the after-run check. It copies each named receiver's folder into --scratch
(refusing, before it removes or copies anything, a copy folder that is the receiver's own folder, holds it or lies
inside it), refuses a copy in which git would act on another working tree or git folder (for example a `core.worktree`
setting copied from the member), removes the copy's remotes, gives each copied sibling repository the same test and a
push URL that cannot resolve, writes the custody marker into the copy's .git
folder, applies the approved list to the COPY, and launches there. The marker holds the SHA-256 of the packet file's
bytes and the receiver's name: it says this tool made the folder for this packet, and anyone able to write that file
can forge it. The session runs under the contained environment with the copy's own hooks in force (R1 ENV
hooks="copy", R1-T2 (c)); every link under the copy must resolve inside its run folder at the launch and again after
the session (else INCONCLUSIVE).
--scratch is the work root W (R1 clause 5, E2g): refused inside any git repository or overlapping a receiver, a
declared sibling source or the framework root. Each run makes a fresh folder `mkdtemp(dir=W)` and copies into
<run>/<name> (or <run>/<name>.root/<name> when siblings are declared); nothing is removed, and each run's folder is
kept. Evidence goes to <--scratch>/evidence and the result to --out (or the default named below); keep --out outside
every receiver's repository (operator rule, not enforced by the tool).

Migration receivers get a baseline session first (as at the real launch); track-skills receivers do not.

Promoted 2026-09-28 (plan G3.6 row 3) from the session-local workspace/.tmp/b2_v37.py so the SOP batch procedure can call a
tracked tool. One change: the stage's baseline file is removed afterwards ONLY if the stage held none before the
rehearsal ran (the earlier script also removed a real receiver's baseline that a batch had left in the stage; batch 5t,
G3.6 row 2).

Usage: python3 scripts/migration_kit/rehearse_v37.py --batch N --scratch DIR --packet PACKET --list WRITE_LIST --out RESULT NAME ...
(without --packet, --list and --out it reads the packet and the write list from, and writes its result to, the folder
batchN beside this tool's folder)
Exit 0 when, for every named receiver, the baseline launch (migrating members), the apply and the session launch
returned 0 and <scratch>/evidence/<name>/after_run_check.json, written by that session launch, then reads PASS; else 1
(2 on a usage error). An after-run record and a launch record left in the evidence folder by an earlier rehearsal are
removed before the session launch, and the tool's first act, before it reads the packet or makes a folder, is to write
the result file with verdict FAIL and the state "started, not finished", so a run that stops at any step leaves no
earlier PASS behind (a result path the tool cannot write stops it there, with a traceback). The rest of the evidence folder is not
cleared.

All or nothing, per receiver (R4): each name is looked up in the packet and in the write list before any copy is
made; a name missing from either reads `REFUSED: <why>`, and nothing is made for it. The member's own `.git` is
tested before anything is removed. A rehearsal that raises reads `REFUSED: <type>: <message>`, nothing more runs in
its copy, and the tool goes on to the next name; the result file names every name. An input that cannot be read
refuses the run (result REFUSED, exit 2).
"""
import argparse
import datetime as dt
import hashlib
import json
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
B1 = HERE
sys.path.insert(0, str(HERE))
import launch_batch as LB  # noqa: E402  (the folder tests the launcher makes of a --copy-root folder)
import copy_isolation as CI  # noqa: E402  (the one routine every copy the kit makes goes through)
import result_binding as RBND  # noqa: E402  (R2: run log and result binding)
import release_target as R  # noqa: E402  (the framework root a work root must not overlap)
STEP = "rehearse_v37"
NOT_FINISHED = {"state": "started, not finished", "verdict": "FAIL", "results": []}   # what the result file holds until a run reaches its end
COPY_MARKER = "aget_rehearsal_copy.json"   # launch_batch.py --copy-root reads it from <copy>/.git/ under the same name


def write_copy_marker(copy, packet_sha, name):
    """Write the custody marker into the copy's .git folder, where git status and the after-run check do not look: the
    SHA-256 of the packet file's bytes and the receiver's name. Raises OSError when the copy has no .git folder or it
    is a symbolic link. The marker records that this tool made the folder for this packet; anyone able to write the
    file can forge it."""
    git_dir = Path(copy) / ".git"
    if git_dir.is_symlink():
        raise OSError(f"{git_dir} is a symbolic link: the copy shares the member's repository")
    data = (json.dumps({"schema": "aget_rehearsal_copy/1", "written_by": "rehearse_v37.py",
                        "packet_sha256": packet_sha, "aget": name}, indent=2) + "\n").encode()
    try:                         # B143 finding 2: at the act, through the contained writer, never through a link
        CI.contained_write(copy, f".git/{COPY_MARKER}", data)
    except CI.ContainmentRefused as e:
        raise OSError(str(e)) from None


def run(*cmd):
    """Run a command, print a short trace of it and of its output, and return its exit code."""
    p = subprocess.run([str(c) for c in cmd], capture_output=True, text=True)
    print("$", " ".join(str(c) for c in cmd[:3]), "...", "exit", p.returncode)
    print(p.stdout.strip()[-900:], p.stderr.strip()[-300:])
    return p.returncode


def rehearse(name, packet_path, packet, wl, scratch, packet_sha=None, ev=None):
    """Run one receiver's headless session on a throwaway copy and return the verdict in the receiver's after_run_check.json
    under the evidence folder, written by this run's session launch (an earlier one is removed first, and a launch
    that does not exit 0 gives no verdict), or why there is none. The copy
    gets the custody marker for `packet_sha` (default: the SHA-256 of the bytes at `packet_path` now). `scratch` is
    this run's own folder (main() makes it fresh under the work root), so nothing is removed to make the copy; `ev`
    is the evidence folder (default <scratch>/evidence)."""
    r = next(x for x in packet["receivers"] if x["aget"] == name)
    if not Path(r["location"], ".git").exists() and not Path(r["location"], ".git").is_symlink():
        return (f"REFUSED: {r['location']} has no .git of its own; no kit route rehearses it; nothing was removed "
                "or copied")
    ev = scratch / "evidence" if ev is None else ev
    siblings = r.get("sibling_reads") or []
    # B2 (G3.6 row 12): with declared siblings the copy sits in its own root, the siblings beside it, so the session's
    # suite and after-run check F read what the real Aget's tests read.
    why = CI.name_refusal(name)                       # B162 finding 1: a name, never a path
    if why:
        return f"copy not made: {why}"
    copy = (scratch / f"{name}.root" / name) if siblings else (scratch / name)
    # F-4: nothing is removed and nothing is copied when the folder this run would clear and fill is the member's own
    # folder, holds it or lies inside it (a --scratch that is the folder holding the members makes scratch/<name> the
    # member itself).
    doomed = copy.parent if copy.parent != scratch else copy
    why = CI.env_refusal(LB.session_env())
    if why:
        return f"copy not made: {why}; nothing was removed"
    if LB.folders_overlap(doomed, r["location"]):
        return (f"copy not made: {doomed.resolve()} is, contains or lies inside {name}'s own folder "
                f"{Path(r['location']).resolve()}; nothing was removed")
    why = CI.run_child_refusal(scratch, doomed, "the rehearsal copy folder") or CI.place_refusal(
        doomed, r["location"], "the rehearsal copy folder",
        sources=CI.sibling_sources(r["location"], siblings))                     # R1-T1: a sibling source too
    if why:
        return f"copy not made: {why}"
    if os.path.lexists(doomed):                       # E2g: a run's folder is fresh; nothing is removed in it
        return f"copy not made: {doomed} already exists in this run's folder; nothing was removed"
    copy.parent.mkdir(parents=True, exist_ok=True)
    subprocess.run(["cp", "-a", r["location"], str(copy)], check=True)
    for rel_path in siblings:
        src, target = (Path(r["location"]) / rel_path).resolve(), (copy / rel_path).resolve()
        if not src.is_dir() or copy.parent.resolve() not in target.parents:
            return f"sibling {rel_path!r} unavailable"
        subprocess.run(["cp", "-a", str(src), str(target)], check=True)
        why = CI.isolate(target, "no-push", LB.session_env(), run=copy.parent)   # remotes kept, pushing closed
        if why:
            return f"copy not usable, nothing applied or launched: sibling {rel_path!r}: {why}"
    # F-4: `cp -a` copies the member's git settings too. Before any git command, the apply or a launch in the copy,
    # git run there must name the copy as its working tree and the copy's own .git folder (the launcher repeats this).
    # R1 LINKS (J-2, H-4): `cp -a` keeps the member's symbolic links; none may lead outside this run's folder.
    # B151 finding 2: full isolation (URL rewrites removed, remotes removed, every push route read back)
    why = CI.isolate(copy, "remove", member=True, run=copy.parent if siblings else copy)
    if why:
        return f"copy not usable, nothing applied or launched: {why}"
    try:
        write_copy_marker(copy, packet_sha or hashlib.sha256(Path(packet_path).read_bytes()).hexdigest(), name)
    except OSError as exc:
        return f"custody marker not written into the copy's .git folder: {exc}"
    common = [sys.executable, B1 / "launch_batch.py", "--packet", packet_path, "--only", name, "--copy-root", copy,
              "--evidence", ev, "--launch"]
    if r.get("mode") != "track-skills" and run(*common, "--baseline") != 0:
        return "baseline not RECORDED"
    entry = next(e for e in wl["agets"] if e["aget"] == name)
    ev.mkdir(parents=True, exist_ok=True)
    lst = ev / f"write_list_copy_{name}.json"
    lst.write_text(json.dumps(dict(wl, agets=[{**entry, "location": str(copy)}]), indent=2) + "\n")
    (ev / name).mkdir(parents=True, exist_ok=True)
    # B143 finding 7: the receipt is the one this apply invocation wrote (the one new file), never a name chosen by
    # sort order from whatever the folder held. Its contents are judged by the after-run check (A).
    before = set((ev / name).glob("APPLY_RECEIPT_*.json"))
    if run(sys.executable, B1 / "apply_protected.py", "--list", lst, "--apply", "--receipt-dir", ev / name,
           "--run", scratch) != 0:                               # BIND (R1-T7): this run's folder
        return "apply failed"
    new = sorted(set((ev / name).glob("APPLY_RECEIPT_*.json")) - before)
    if len(new) != 1:
        return f"REFUSED: the apply wrote {len(new)} new receipt(s) in {ev / name}, not exactly one"
    receipt = new[0]
    # A verdict is this run's only: the two records the launch writes are removed first, and the launch must exit 0.
    for stale in ("after_run_check.json", "launch_record.json"):
        try:
            (ev / name / stale).unlink(missing_ok=True)
        except OSError as exc:
            return f"an earlier {stale} could not be removed from the evidence folder: {exc}"
    LAUNCHED.add(name)          # C2e (D-8, S-198/S-323): this member's evidence records are this run's from here on
    code = run(*common, "--apply-receipt", receipt)
    if code != 0:
        return f"session launch failed (exit {code})"
    try:
        return json.loads((ev / name / "after_run_check.json").read_text())["verdict"]
    except (OSError, ValueError, KeyError):
        return "no after-run result"


def main(argv=None):
    """Command-line entry point: rehearse the named receivers' sessions on throwaway copies."""
    argv = sys.argv[1:] if argv is None else list(argv)
    # R2 clause 1, first act, before argument parsing: record this run and invalidate any earlier result for this
    # output, so a usage error or a stop at any later step leaves no earlier result current.
    run_id, early = RBND.producer_start(STEP, default_out(argv), NOT_FINISHED)
    if early:
        print(early)
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--scratch", type=Path, required=True, help="a folder outside every receiver")
    ap.add_argument("--out", type=Path, help="the result file (default batchN/V37_RESULT_batchN.json)")
    ap.add_argument("--packet", type=Path, help="the packet (default batchN/LAUNCH_PACKET_batchN.json)")
    ap.add_argument("--list", type=Path, help="the write list (default batchN/WRITE_LIST_batchN.json)")
    ap.add_argument("names", nargs="+")
    a = ap.parse_args(argv)
    bd = HERE.parent / f"batch{a.batch}"
    out = a.out or bd / f"V37_RESULT_batch{a.batch}.json"
    # First act, before any input is read or any folder is made: the result file says NOT FINISHED, so a run that
    # stops at any later step (an unreadable packet, a scratch folder that cannot be made, a copy that is refused, a
    # baseline or an apply that fails, an error) leaves no earlier PASS for the approval step.
    out.write_text(json.dumps(NOT_FINISHED, indent=2) + "\n")
    packet_path = a.packet or bd / f"LAUNCH_PACKET_batch{a.batch}.json"
    list_path = a.list or bd / f"WRITE_LIST_batch{a.batch}.json"
    try:                 # R4 C1: an input that cannot be read refuses the run before any copy is made
        raw = packet_path.read_bytes()   # the marker names the digest of the bytes parsed here
        packet, wl = json.loads(raw), json.loads(list_path.read_text())
        packet_sha = hashlib.sha256(raw).hexdigest()
        in_packet = {x["aget"] for x in packet["receivers"]}
        in_list = {e["aget"] for e in wl["agets"]}
        for n in a.names:                              # B162 finding 1: before any folder is made
            why = CI.name_refusal(n)
            if why:
                raise ValueError(why)
        # R1 clause 5 (E2g, R1-T1): --scratch is the work root; this run's copies go into a fresh folder in it
        avoid = [x for r in packet["receivers"]
                 for x in (r["location"], *CI.sibling_sources(r["location"], r.get("sibling_reads") or []))]
        run_dir = CI.run_folder(a.scratch, avoid + [R.framework_root()], prefix=f"v37-{a.batch}-")
        (a.scratch / "evidence").mkdir(exist_ok=True)
    except (OSError, ValueError, KeyError, TypeError, CI.ContainmentRefused) as e:
        RBND.write_result(STEP, out, {"verdict": "REFUSED", "why": f"input unreadable: {type(e).__name__}: {e}",
                                      "members": {}}, run_id, 2)
        print(f"REFUSED: input unreadable: {type(e).__name__}: {e}")
        return 2
    started = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    out.write_text(json.dumps({**result_doc(a.batch, packet_path, list_path, a.scratch / "evidence", {}, started),
                               **NOT_FINISHED}, indent=2) + "\n")     # the same state, now naming the digests
    verdicts = {}
    for n in a.names:
        missing = [where for where, names in (("the packet", in_packet), ("the write list", in_list)) if n not in names]
        if missing:
            verdicts[n] = f"REFUSED: {n} is not in {' or '.join(missing)}; nothing was made for it"
        else:
            try:
                # R1 lifecycle: the launcher writes a rehearsal's baseline inside its copy, never into the packet, so
                # nothing here touches the packet root (the stage guard that used to restore it is gone)
                verdicts[n] = rehearse(n, packet_path, packet, wl, run_dir, packet_sha, a.scratch / "evidence")
            except Exception as e:                          # noqa: BLE001 — R4 clause 3: go on to the next name
                verdicts[n] = f"REFUSED: {type(e).__name__}: {e}"
        print("=" * 60, n, verdicts[n])
    doc = result_doc(a.batch, packet_path, list_path, a.scratch / "evidence", verdicts, started)
    RBND.write_result(STEP, out, doc, run_id, 0 if doc["verdict"] == "PASS" else 1)
    print("result:", out)
    return 0 if all(v == "PASS" for v in verdicts.values()) else 1


def default_out(argv):
    """The result path this run will write, read from the arguments before they are parsed: --out, else the batch
    folder's default for --batch; None when neither is there (the parser then refuses)."""
    out = RBND.prescan(argv, "--out")
    if out is not None:  # D2 (C2e pre-read 2): an empty value is a value (argparse takes `--x=`), never absent
        return out
    batch = RBND.prescan(argv, "--batch")
    return str(HERE.parent / f"batch{batch}" / f"V37_RESULT_batch{batch}.json") if batch else None


# C2e (D-8, S-198/S-323; DESIGN's new R2-T7 case): the members whose launch this invocation started, after their
# earlier after-run and launch records were removed. Only their records are embedded in the result
LAUNCHED = set()


def result_doc(batch, packet_path, list_path, ev, verdicts, started):
    """B3 (G3.6 row 12; supervisor:L843): the rehearsal writes its own result, naming the list digest it rehearsed,
    from the records in its evidence folder. Batch 8's results were hand-composed afterwards, which is where a stale digest
    survived and a FAIL had to be transcribed."""
    sha = lambda p: hashlib.sha256(Path(p).read_bytes()).hexdigest()
    members = {}
    for n, v in verdicts.items():
        m = {"verdict": v}
        for f in ("after_run_check", "launch_record"):
            if n not in LAUNCHED:       # stopped before its launch: a record there is an earlier run's, never this one's
                m[f] = None
                continue
            try:
                m[f] = json.loads((ev / n / f"{f}.json").read_text())
            except (OSError, ValueError):
                m[f] = None
        members[n] = m
    return {"schema": "v335_v37_result/2", "batch": str(batch), "written_by": "rehearse_v37.py",
            "list_sha256": sha(list_path), "packet_sha256": sha(packet_path), "started": started,
            "ended": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "evidence": str(ev),
            "members": members,
            "verdict": "PASS" if verdicts and all(v == "PASS" for v in verdicts.values()) else "FAIL"}


if __name__ == "__main__":
    sys.exit(main())
