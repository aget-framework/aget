#!/usr/bin/env python3
"""Receiver bounds for a batch (ruling 2026-09-23; route a2 addendum): run scripts/check_receiver_write_scope.py per
root over EVERY path the batch writes or the receiver commits (write list ops + the packet's write set, carriers,
receipt). Exit 1 or 2 at any root means a principal override naming that Aget is needed. It reads the packet, the list
and the .aget/version.json of each receiver in the packet, where that file exists; with --out it writes its rows to
that path. Keep --out outside the receivers' repositories (operator rule, not enforced by the tool).

Usage: python3 scripts/migration_kit/check_batch_scope.py --packet <p> --list <l> [--out <json>]
"""
import argparse
import json
import subprocess
import sys
from pathlib import Path

# Rehearsal finding 2026-09-30: this read parents[4] (the supervisor's old batch-folder depth) and the checker from the
# supervisor's own scripts/, which no remote supervisor has; every receiver then read exit 2 and the whole batch
# BLOCKED. The checker now ships in the kit beside this file.
CHECK = Path(__file__).resolve().parent / "check_receiver_write_scope.py"
sys.path.insert(0, str(Path(__file__).resolve().parent))
import item_meaning as IM  # noqa: E402  (C2e, D-8: the meaning table says which items the scope check covers)
CARRIERS = [".aget/version.json", "manifest.yaml"]


def _literal_prefix(glob):
    """The path components of `glob` before its first component holding a wildcard."""
    out = []
    for c in glob.strip("/").split("/"):
        if any(x in c for x in "*?["):
            break
        out.append(c)
    return out


def main(argv=None):
    """Command-line entry point: check the concrete declared batch paths against each receiver's write scope."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--list", type=Path, required=True)
    ap.add_argument("--out", type=Path)
    a = ap.parse_args(argv)
    packet = json.loads(a.packet.read_text())
    wl = {e["aget"]: e for e in json.loads(a.list.read_text())["agets"]}
    rows, worst = [], 0
    for r in packet["receivers"]:
        paths = {o["path"] for o in wl.get(r["aget"], {}).get("ops", [])}
        # C2e (D-8, S-190/S-250): a glob in the session's write set is checked by its literal prefix (the path
        # components before the first wildcard component; `sessions/*` and `sessions/**` give `sessions`), which is
        # sound because `refused()` is a prefix test; a glob with no literal prefix (`**`) cannot be checked: exit 2
        bad, globs = [], set()
        for w in r.get("write_set", []):
            if any(c in w for c in "*?["):
                pre = "/".join(_literal_prefix(w))
                (globs.add(pre) if pre else bad.append(w))
            else:
                paths.add(w)
        paths |= globs | set(r.get("track_paths", []))
        # C2e (D-8, S-191/S-248): every packet item whose meaning row puts it in the scope check (deletes and held
        # deletes included), not only the list's ops
        unknown = []
        for i in r.get("items", []) or []:
            try:
                if IM.meaning(i).scope:
                    paths.add(i["path"])
            except (IM.UnknownClassification, KeyError, TypeError) as e:
                unknown.append(str(e)[:80])
        if r.get("mode") != "track-skills":
            paths |= set(CARRIERS)
        # D2 (C2e pre-read 8): a path that is not a plain relative path (`docs/../scripts/x`, `./x`, `/x`) is not
        # checked by prefix: unverifiable
        bad += sorted(x for x in paths if x.startswith("/") or any(c in ("..", ".") for c in x.split("/")))
        if bad or unknown:
            why = (f"unverifiable write-set entr(ies): no literal prefix or not a plain relative path: {bad}" if bad else f"unclassified item(s): {unknown}")
            rows.append({"aget": r["aget"], "exit": 2, "paths": len(paths), "verdict": "unverifiable", "out": why})
            worst = max(worst, 2)
            print(f"{r['aget']:34s} exit 2 ({why[:80]})")
            continue
        # D2 (C2e pre-read 7): `--` ends the options, so a path named `--json` is a path, never an option
        p = subprocess.run([sys.executable, str(CHECK), r["location"], "--json", "--", *sorted(paths)],
                           capture_output=True, text=True)
        try:
            verdict = json.loads(p.stdout).get("verdict")
        except (ValueError, AttributeError):
            verdict = None
        code = p.returncode
        # C2e (D-8, S-191, DESIGN's R2-T17 (c)): only a declared scope that holds every path, or an explicit
        # `unrestricted`, passes; a receiver that declares no write_scope cannot be checked (exit 2, an override)
        if code == 0 and verdict not in ("inside_scope", "unrestricted"):
            code = 2
        rows.append({"aget": r["aget"], "exit": code, "paths": len(paths), "verdict": verdict,
                     "out": p.stdout.strip()[-600:]})
        worst = max(worst, code)
        print(f"{r['aget']:34s} exit {code} ({len(paths)} paths; {verdict})")
    if a.out:
        a.out.write_text(json.dumps({"rows": rows}, indent=2) + "\n")
    return worst


if __name__ == "__main__":
    sys.exit(main())
