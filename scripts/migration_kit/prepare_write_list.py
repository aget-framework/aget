#!/usr/bin/env python3
"""Batch 2's ONE write list for the principal's approval (route a2, ruled 2026-09-28).

It reads files at the packet's Agets where they exist (among them each one's `.aget/version.json`). It writes the
list to the path named with --out and a scope-check result beside it (the same name with `_scope.json` in place of
the last extension, if it has one). Keep --out outside those Agets' repositories (operator rule, not enforced by
the tool).

Combines, per Aget, into the format the reviewed apply_protected.py reads:
  - the protected ops from prepare_batch.py's list (write / write-upstream / noop / hold / replace-line / hold-line);
  - the unprotected payload the packet marks placed (prepare_launch.apply_list): `write` with the digest the packet
    records (of the release bytes; of the committed bytes its source names for a receiver-authored item);
    a listed Aget's path named in --resolved-file here instead gets the digest of the bytes read from its source;
  - for each track-skills receiver, one `rewrite-claude-ignore` op on .gitignore (gh#1569), `post` computed here with
    the same function the apply script runs.
The principal approves the list at SOP step B4 by typing the batch line (the typed-line check binds the batch, not
this list's digest, and apply_protected.py does not run that check: approval before the apply is an operator rule,
not enforced by the tool); this Aget then runs apply_protected.py on it. The list records the apply script's digest, and the script refuses any other.

Usage: python3 scripts/migration_kit/prepare_write_list.py --protected <list> --packet <packet>
           --out <write_list.json>
"""
import argparse
import datetime as dt
import hashlib
import importlib.util
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_target as R  # noqa: E402  (the kit's one release parameter; carriage row 24)
import item_meaning as IM  # noqa: E402  (R3: only listed relabels)

B1 = Path(__file__).resolve().parent


def load(name):
    """Load a kit script by name from its folder and return it as a module."""
    s = importlib.util.spec_from_file_location(name, B1 / f"{name}.py")
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


A = load("apply_protected")
PL = load("prepare_launch")


def sha(b):
    """Return the SHA-256 hex digest of the bytes, or 'absent' when given None."""
    return hashlib.sha256(b).hexdigest() if b is not None else "absent"


RECORDS = Path(__file__).resolve().parents[2] / "data" / f"{R.SLUG}_ledger" / "records.json"
_c = importlib.util.spec_from_file_location("check_batch_scope", Path(__file__).resolve().parent / "check_batch_scope.py")
CBS = importlib.util.module_from_spec(_c)
_c.loader.exec_module(CBS)


def gate_scope(doc, packet_path, list_path):
    """Receiver bounds as a STRUCTURAL gate (2026-09-28: batch 2 was applied at one receiver without it, exit 2).
    An Aget whose check is not exit 0 and has no recorded principal override is `blocked`, which the apply script
    skips. The check runs over the list as built, so the list is written, checked, then rewritten with the result."""
    overrides = (json.loads(RECORDS.read_text()).get("scope_overrides") or {}) if RECORDS.is_file() else {}
    out = Path(list_path).with_name(Path(list_path).stem + "_scope.json")
    CBS.main(["--packet", str(packet_path), "--list", str(list_path), "--out", str(out)])
    rows = {r["aget"]: r for r in json.loads(out.read_text())["rows"]}
    for e in doc["agets"]:
        row = rows.get(e["aget"], {"exit": 2, "out": "not checked"})
        e["scope_check"] = {"exit": row["exit"], "detail": row.get("out", "")[-300:]}
        ov = overrides.get(e["aget"]) or {}
        covered = str(doc.get("batch")) in [str(b) for b in ov.get("batches", [])]   # an override names its batches
        if row["exit"] != 0 and not covered and not e.get("blocked"):
            e["blocked"] = (f"receiver bounds: check_receiver_write_scope exit {row['exit']}; needs a principal "
                            f"override naming {e['aget']} (records.json scope_overrides)")
        elif row["exit"] != 0:
            e["scope_override"] = overrides.get(e["aget"])
    return doc


def apply_resolved(doc, resolved, read=None):
    """Receiver-authored bytes (G3.6 row 11): for each {aget: {path: "repo@rev:path"}} entry, the list's op for that
    path becomes a `write` whose source is the receiver's own committed resolution. `source` uses the form the reviewed
    apply script already reads (`git show rev:path` under the framework root), so the script is unchanged; the digest
    of every such file is in the list for the principal's review, marked `receiver_authored`."""
    read = read or A.release_bytes
    for e in doc["agets"]:
        for path, source in (resolved.get(e["aget"]) or {}).items():
            data = read(source)
            if data is None:
                raise ValueError(f"{e['aget']}: cannot read {source}")
            old = [o for o in e["ops"] if o["path"] == path]
            if len(old) > 1:                 # B148 finding 4: every row removed below must be judged, so one only
                raise ValueError(f"{e['aget']}: {path} has {len(old)} rows ({[o['op'] for o in old]}); a classified "
                                 "path has exactly one; nothing was relabelled")
            if old:
                IM.meaning(old[0])    # B151 finding 4: an unknown old row is refused, never replaced
            if old and old[0]["op"] != "write" and (old[0]["op"], "write") not in IM.RELABELS:
                raise ValueError(f"{e['aget']}: {path} is {old[0]['op']!r}; it cannot be relabelled to write "
                                 "(R3: only listed transitions)")
            f = Path(e["location"]) / path
            op = {"path": path, "op": "write", "pre": sha(f.read_bytes() if f.is_file() else None), "post": sha(data),
                  "source": source, "source_sha256": sha(data), "receiver_authored": True}
            e["ops"] = [o for o in e["ops"] if o["path"] != path] + [op]
    return doc


def mark_dropped(doc, drops):
    """Mark each dropped member `blocked` with its reason; the reviewed apply script skips blocked entries even without
    --only (batch 7: one receiver was dropped at V3.6 but stayed `ok` in list e1fd6749). The mark is in the write list
    only: launch_batch.py never reads this list, so a dropped member still in the packet stays among the
    receivers a launch takes from it unless the packet is rebuilt without it or --only leaves it out (a --baseline
    launch also skips a receiver with no baseline prompt)."""
    unknown = set(drops) - {e["aget"] for e in doc["agets"]}
    if unknown:
        raise ValueError(f"--drop names Agets not in the list: {sorted(unknown)}")
    for e in doc["agets"]:
        if e["aget"] in drops:
            e["blocked"] = f"dropped after the list was built: {drops[e['aget']]}"
    return doc


def build(protected, packet):
    """Combine, per Aget, the protected operations and the packet's placed files into one list of entries."""
    placed = {x["aget"]: x for x in PL.apply_list(packet)["agets"]}
    by_aget = {x["aget"]: x for x in protected["agets"]}
    out = []
    for r in packet["receivers"]:
        name = r["aget"]
        if r.get("mode") == "track-skills":
            gi = Path(r["location"]) / ".gitignore"
            cur = gi.read_bytes() if gi.is_file() else None
            new = A.rewrite_claude_ignore(cur.decode()) if cur is not None else None
            entry = {"aget": name, "location": r["location"], "head": r.get("head"), "mode": "track-skills",
                     "purpose": "gh#1569 skill tracking", "ops": [
                {"path": ".gitignore", "op": "rewrite-claude-ignore", "pre": sha(cur),
                 "post": sha(new.encode()) if new is not None else None,
                 "source": "the bare `.claude/` rule -> `.claude/*` + `!.claude/skills/` (apply_skill_tracking.py form)"}]}
            if new is None:
                entry["blocked"] = ".gitignore has no single bare `.claude/` line; the rewrite would refuse"
            out.append(entry)
            continue
        entry = dict(by_aget.get(name) or {"aget": name, "location": r["location"], "ops": []})
        if entry.get("head") and r.get("head") and entry["head"] != r["head"]:
            raise ValueError(f"{name}: the protected list was prepared at {entry['head']}, the packet names "
                             f"{r['head']}; re-prepare one of them")
        entry["head"] = r.get("head") or entry.get("head")
        entry["mode"] = r.get("mode", "migrate")      # C2e (D-8, S-351): the gate reads the mode from the list
        entry["ops"] = list(entry.get("ops", [])) + placed.get(name, {}).get("ops", [])
        out.append(entry)
    return out


def main(argv=None):
    """Command-line entry point: write the batch's one write list for the principal's approval."""
    R.require()
    ap = argparse.ArgumentParser()
    ap.add_argument("--protected", type=Path, required=True)
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--resolved-file", type=Path, help="JSON {aget: {path: 'repo@rev:path'}}: receiver-authored bytes "
                    "the list places (G3.6 row 11)")
    ap.add_argument("--drop", nargs="*", default=[], metavar="AGET=REASON",
                    help="a member dropped after the list was first built (e.g. at V3.6): marked `blocked` with the "
                         "reason, so no apply of this list can write to it, with or without --only (G3.6 row 10)")
    a = ap.parse_args(argv)
    protected = json.loads(a.protected.read_text())
    packet = json.loads(a.packet.read_text())
    doc = {"schema": "v335_protected_list/1", "batch": packet["batch"], "route": "a2 (ruled 2026-09-28)",
           "prepared_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
           "prepared_by": f"{R.SUPERVISOR} (read-only)", "packet": str(a.packet),
           "packet_sha256": sha(a.packet.read_bytes()), "protected_list_sha256": sha(a.protected.read_bytes()),
           "apply_script_sha256": sha((B1 / "apply_protected.py").read_bytes()),
           "agets": None}
    try:
        doc["agets"] = build(protected, packet)
    except ValueError as exc:
        ap.error(str(exc))
    if a.resolved_file:
        doc["resolved_file"] = str(a.resolved_file)
        doc["resolved_file_sha256"] = sha(a.resolved_file.read_bytes())
        apply_resolved(doc, json.loads(a.resolved_file.read_text()))
    a.out.write_text(json.dumps(doc, indent=2) + "\n")
    doc = gate_scope(doc, a.packet, a.out)
    try:
        mark_dropped(doc, dict(x.split("=", 1) for x in a.drop))
    except ValueError as exc:
        ap.error(str(exc))
    a.out.write_text(json.dumps(doc, indent=2) + "\n")
    for e in doc["agets"]:
        ops = [o["op"] for o in e["ops"]]
        print(f"{e['aget']:34s} " + " ".join(f"{k} {ops.count(k)}" for k in sorted(set(ops)))
              + (f"  BLOCKED: {e['blocked']}" if e.get("blocked") else ""))
    print(f"write list sha256 {sha(a.out.read_bytes())}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
