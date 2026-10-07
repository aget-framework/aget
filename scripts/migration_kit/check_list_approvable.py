#!/usr/bin/env python3
"""SOP B4 gate: a write list is approvable only if every member that is NOT blocked in it has a V3.6 verdict of PASS in
the batch's V3.6 result. READ-ONLY. Exit 0 approvable; 1 not approvable (names each member and why); 2 unreadable input.

Why (G3.6 row 10, framework-lane review of 6e82854e): batch 7's one receiver failed V3.6 but stayed `ok` in the approved list;
only `--only` kept the apply off it. `--drop` (prepare_write_list.py) marks a dropped member blocked, but it depends on
the operator remembering it. This check makes the approval step itself refuse such a list, without touching
apply_protected.py's reviewed digest.

Digest binding (supervisor:L843, 2026-09-28): each result must name the list it rehearsed, and that digest must equal
sha256(--list). Before this, a V3.7 result written for batch 8's list 5040d231 would have passed list a06ecb52. The
V3.6 result's `list_sha256` and the V3.7 result's `list_sha256` (or the 64-hex digest inside its `list` text) are read.
The one allowed difference is a --drop re-list: `--relisted-from OLD` names the rehearsed list; both results must
name OLD's digest, and the new list may differ from OLD only by members newly marked `blocked` (and `prepared_at`).
The test that none of them is the V3.7 member reads a `receiver` key in the V3.7 result, which `rehearse_v37.py` does
not write, so with that tool's result it refuses nothing: not approving a re-list that drops the session-rehearsal
member is an operator rule, not enforced by the tool.

Result binding (R2, kit design pass): each result must also be the CURRENT run at its own path: its `binding.run_id`
is the last run its rehearsal tool started for that file (runs.jsonl beside it), and that run finished with exactly
these bytes. A result copied from another folder, or one a later run of the same output superseded (a run that
failed, even before argument parsing), is refused even when it names this list's digest. The V3.7 digest is the
recorded `list_sha256` only (no hex fallback), and the re-list test reads the V3.7 result's `members`.

Usage: python3 planning/artifacts/v3.35.0_fleet_migration/batch2/check_list_approvable.py --list L --v36 V36_RESULT.json
       --v37 V37_RESULT.json [--relisted-from REHEARSED_LIST.json]
"""
import argparse
import hashlib
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import result_binding as RBND  # noqa: E402  (R2: a result counts only when it is the current run at its path)
import item_meaning as IM  # noqa: E402  (R3: one meaning table per classification)


def problems(list_doc, v36_doc, v37_doc=None):
    """V3.6 PASS for every unblocked member, and (when a V3.7 result is given) V3.7 PASS for the batch (the
    framework Aget's finding, 2026-09-28: the gate required V3.6 only)."""
    verdicts = {r["aget"]: r.get("verdict") for r in v36_doc.get("results", [])}
    out = []
    if v37_doc is not None and v37_doc.get("verdict") != "PASS":
        out.append(f"batch V3.7 is {v37_doc.get('verdict')!r}, not PASS")
    for e in list_doc.get("agets", []):
        if e.get("blocked"):
            continue
        v = verdicts.get(e["aget"])
        if v is None:
            out.append(f"{e['aget']}: unblocked in the list but has no V3.6 result")
        elif v != "PASS":
            out.append(f"{e['aget']}: unblocked in the list but V3.6 is {v!r}; re-list with --drop or re-rehearse")
    return out


def covers(test_id, written, location):
    """A blind-spot test covers a written file when its test file IS a written path, or its source names a written
    file (its file name, or its stem for .py modules). A heuristic, stated: it errs toward 'covers'."""
    tfile = test_id.split("::")[0]
    if tfile in written:
        return True
    try:
        src = (Path(location) / tfile).read_text(errors="replace")
    except OSError:
        return True                                           # unreadable: assume it covers (fail safe)
    for w in written:
        name = Path(w).name
        stem = Path(w).stem if w.endswith(".py") else None
        if name in src or (stem and re.search(rf"\b{re.escape(stem)}\b", src)):
            return True
    return False


def blind_spot_problems(list_doc, v36_doc, accepted=()):
    """Plan G3.6 row 13 (b): print each member's V3.6 blind spots (tests failing only on the copy, so a regression in
    them cannot show as new); refuse when one covers a file the batch writes, unless the principal names it
    (--accept-blind TEST_ID). A result without a blind-spot report is refused too: unknown is not empty."""
    res = {r["aget"]: r for r in v36_doc.get("results", [])}
    out = []
    for e in list_doc.get("agets", []):
        if e.get("blocked") or e["aget"] not in res:
            continue
        r = res[e["aget"]]
        try:
            # C2e (D-8, S-351): the mode is the LIST's (what the member was prepared as); a V3.6 result labelled with
            # another mode is a problem, never a reason to skip the gate
            mode, rmode = IM.receiver_mode(e), IM.receiver_mode(r)
            if mode != rmode:
                out.append(f"{e['aget']}: the list prepares it as {mode}, its V3.6 result is labelled {rmode}")
                continue
            if mode == "track-skills":       # D-3: an unknown mode is a problem, not "migrate"
                continue
        except IM.UnknownClassification as exc:
            out.append(f"{e['aget']}: {exc}")
            continue
        blind = r.get("blind_spots")
        if blind is None:
            out.append(f"{e['aget']}: no V3.6 blind-spot report ({r.get('blind_spots_why', 'result predates it')})")
            continue
        print(f"BLIND SPOTS {e['aget']}: {len(blind)} test(s) fail only on the copy: {blind}")
        # D-4 (S-253): what the apply writes comes from the meaning table; an unknown classification is refused,
        # never counted as written (or as not written).
        written = set()
        for o in e.get("ops", []):
            try:
                if IM.meaning(o).apply_writes:
                    written.add(o["path"])
            except IM.UnknownClassification as exc:
                out.append(f"{e['aget']}: {exc}; the list cannot be approved with it")
        for t in blind:
            if t not in accepted and covers(t, written, e.get("location", "")):
                out.append(f"{e['aget']}: blind-spot test {t} covers a file the batch writes "
                           "(needs the principal's --accept-blind)")
    return out


def v37_digest(v37_doc):
    """The list digest a V3.7 result names: its recorded `list_sha256` only. A hex string found in free text is not
    a binding (S-184): it is not read."""
    return v37_doc.get("list_sha256") or None


def newly_blocked(old_doc, new_doc):
    """Members blocked in NEW but not OLD, or None when the lists differ in any other way (prepared_at excepted)."""
    strip = lambda d: {k: v for k, v in d.items() if k not in ("prepared_at", "agets")}
    if strip(old_doc) != strip(new_doc):
        return None
    old, new = old_doc.get("agets", []), new_doc.get("agets", [])
    if [e.get("aget") for e in old] != [e.get("aget") for e in new]:
        return None
    added = []
    for o, n in zip(old, new):
        if {k: v for k, v in n.items() if k != "blocked"} != {k: v for k, v in o.items() if k != "blocked"}:
            return None
        if n.get("blocked") and not o.get("blocked"):
            added.append(n["aget"])
        elif n.get("blocked") != o.get("blocked"):
            return None
    return added


def digest_problems(raw, v36_doc, v37_doc, old_raw=None):
    """Each result must name the digest of the list it rehearsed, and that list must be this one (or, with a
    --drop re-list, OLD, differing only by newly blocked members that do not include the V3.7 member)."""
    sha = hashlib.sha256(raw).hexdigest()
    want, out = sha, []
    if old_raw is not None:
        want = hashlib.sha256(old_raw).hexdigest()
        added = newly_blocked(json.loads(old_raw), json.loads(raw))
        if added is None:
            out.append("--relisted-from: the list differs from the rehearsed list by more than newly blocked members")
        else:
            rehearsed = set((v37_doc.get("members") or {}).keys())
            if not rehearsed:
                out.append("--relisted-from: the V3.7 result names no members, so the newly blocked ones cannot be "
                           "checked against it")
            out += [f"--relisted-from: {a} is newly blocked but is a V3.7 member" for a in added if a in rehearsed]
    for name, got in (("V3.6", v36_doc.get("list_sha256")), ("V3.7", v37_digest(v37_doc))):
        if not got:
            out.append(f"the {name} result names no list digest; cannot tell which list it rehearsed")
        elif got != want:
            out.append(f"the {name} result rehearsed list {got[:12]}, not {want[:12]}"
                       + ("" if old_raw is None else " (the --relisted-from list)"))
    return out


def main(argv=None):
    """Command-line entry point: decide whether a write list is approvable from its rehearsal results."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--list", type=Path, required=True)
    ap.add_argument("--v36", type=Path, required=True)
    ap.add_argument("--v37", type=Path, required=True, help="the batch's V3.7 result (its `verdict` must be PASS)")
    ap.add_argument("--relisted-from", type=Path, default=None,
                    help="the list the results rehearsed, when --drop re-listed it afterwards")
    ap.add_argument("--accept-blind", nargs="*", default=[], metavar="TEST_ID",
                    help="blind-spot tests the principal accepts although they cover a written file (row 13 (b))")
    a = ap.parse_args(argv)
    try:
        raw = a.list.read_bytes()
        lst = json.loads(raw)
        # C2e (R2-T17 rest, --relisted-from with current results): each result is read ONCE, through read_current,
        # and the bytes judged are the bytes bound (a separate second read could judge other bytes). A result that is
        # not current is a problem; its file is parsed only to name what else it says
        cur = {name: (RBND.read_current(step, path), path) for name, step, path in
               (("V3.6", "rehearse_batch2", a.v36), ("V3.7", "rehearse_v37", a.v37))}
        stale = [f"the {name} result {path}: {why}" for name, ((_, why), path) in cur.items() if why]
        v36, v37 = (doc if doc is not None else json.loads(Path(path).read_text())
                    for (doc, _), path in (cur["V3.6"], cur["V3.7"]))
        old_raw = a.relisted_from.read_bytes() if a.relisted_from else None
        if old_raw is not None:
            json.loads(old_raw)
    except (OSError, ValueError) as exc:
        print(f"UNREADABLE: {exc}")
        return 2
    found = (stale + digest_problems(raw, v36, v37, old_raw) + problems(lst, v36, v37)
             + blind_spot_problems(lst, v36, set(a.accept_blind)))
    for t in a.accept_blind:
        print(f"ACCEPTED BLIND SPOT (principal): {t}")
    for p in found:
        print("NOT APPROVABLE", p)
    if not found:
        print(f"APPROVABLE: V3.6 and V3.7 rehearsed this list and every unblocked member passed V3.6 "
              f"(list sha256 {hashlib.sha256(raw).hexdigest()[:12]})")
    return 1 if found else 0


if __name__ == "__main__":
    sys.exit(main())
