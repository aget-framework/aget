#!/usr/bin/env python3
"""V3.6 — rehearse the batch 1 repair packet on throwaway copies of the receivers. No model in the loop.

Per receiver (its folder is read and copied to <run>/<aget>, where <run> is a fresh folder `mkdtemp(dir=<--scratch>)`;
--scratch is the work root W, refused inside any git repository or overlapping a receiver or the framework root (R1
clause 5, E2g); nothing is removed and each run's folder is kept; evidence goes to <--scratch>/evidence; the copy's
remotes are removed; keep --out outside the receivers' repositories: operator rule, not enforced by the tool):
  S0 baseline   the copy checked out at the PRE-migration HEAD (the phase-1 packet's head): suite run, failures kept
  S1 regression the copy at the receiver's current HEAD (its unrepaired migration commit): suite run. Batch 1's
                defect is the regression case, so S1 must show NEW failures against S0, or the rehearsal cannot
                detect the defect it exists for
  S2 repaired   S1 plus the repair packet applied exactly as the receiver is told (each WRITE item's staged bytes
                copied; nothing re-typed): suite run. PASS needs no new failure against S0, every WRITE and VERIFY
                item equal to its release digest, and every correction-row-4 path sourced from core
An unrunnable suite is INCONCLUSIVE, which is not PASS.

All or nothing, per receiver (R4): the member's own `.git` is tested before anything is removed; after the copy, every
path the rehearsal places or amends and every staged source is tested before the first checkout, suite or write; each
checkout is read back and must reach its commit. A receiver that fails any of these, or whose rehearsal raises, reads
`REFUSED: <why>`, nothing more runs in that copy, and the other receivers are still rehearsed. A receiver missing from
--previous-packet, or an input that cannot be read, refuses the whole run before any copy is made (result REFUSED,
exit 2). The rehearsal's writes in a copy go through the contained writer (copy_isolation.contained_write).

Usage: python3 planning/artifacts/v3.35.0_fleet_migration/batch1/rehearse_repair.py --packet <repair.json>
           --previous-packet <phase1.json> --scratch <dir> --out <result.json> [--only NAME ...]
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import hashlib
import importlib.util
import json
import os
import re
import shlex
import shutil
import subprocess
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import copy_isolation as CI  # noqa: E402  (the one routine every copy the kit makes goes through)
import result_binding as RBND  # noqa: E402  (R2: run log and result binding)
import release_target as R  # noqa: E402  (the framework root a work root must not overlap)

HERE = Path(__file__).resolve().parent
_s = importlib.util.spec_from_file_location("wave_readiness", HERE / "wave_readiness.py")
WR = importlib.util.module_from_spec(_s)
_s.loader.exec_module(WR)
_p = importlib.util.spec_from_file_location("prepare_launch", HERE / "prepare_launch.py")
PL = importlib.util.module_from_spec(_p)
_p.loader.exec_module(PL)
SUITE_TIMEOUT = 1500
SUMMARY = re.compile(r"^(?:=+ )?(\d+ (?:passed|failed|error|errors|skipped|deselected|xfailed|xpassed|no tests ran)"
                     r".*?) in [\d.]+s")   # -q prints the summary with no ==== border


def sha(p):
    """Return the SHA-256 hex digest of the file's bytes, or 'absent' when it cannot be read."""
    try:
        return hashlib.sha256(Path(p).read_bytes()).hexdigest()
    except OSError:
        return "absent"


def git(root, *args, env=None):
    """Run git in the given root and return the completed process."""
    return subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True, env=env)


def kit_git_env(copy):
    """R1 ENV for a git act the kit makes in a copy: no transport, no copied hook (R1-T15), git bounded by the folder
    holding the copy (R1-T3). The run folder is the copy's parent, so the environment's own files stay out of it."""
    return CI.contained_env(Path(copy).parent, copy, CI.NO_TRANSPORT)


def code_env(copy):
    """R1 ENV for member code run in a copy (its suite): git bounded by the folder holding the copy, no operator
    configuration, CLAUDE_PROJECT_DIR the copy (R1-T16); transports as they are (the suite's own local tests)."""
    return CI.contained_env(Path(copy).parent, copy, check=False)   # suite() checks it immediately before use


def suite(root, label, ev, cmd=None):
    """The receiver's suite; `cmd` is a per-receiver suite command when one is ruled (e.g. the parallel runner)."""
    t0 = time.time()
    argv = shlex.split(cmd) if cmd else [sys.executable, "-m", "pytest", "-q", "-rfE", "-p", "no:cacheprovider"]
    try:
        env = code_env(root)
        why = (CI.env_route_refusal(Path(os.path.abspath(root)), env, Path(os.path.abspath(root)).parent)
               if (Path(root) / ".git").is_dir() else None)
        if why:
            raise CI.ContainmentRefused(f"under the contained environment: {why}")
    except CI.ContainmentRefused as e:                   # B160 finding 1: the suite does not run
        (ev / f"{label}.txt").write_text(f"NOT RUN: {e}\n")
        return {"exit": "refused", "summary": None, "failures": [], "ran": False, "seconds": 0.0, "why": str(e)}
    report = Path(ev) / f"{label}_pytest_report.jsonl"   # B185 finding 1 (C2a7): a fresh kit report per suite run
    report.unlink(missing_ok=True)
    token = RBND.new_report(report)
    env = RBND.report_env(env, report, token)
    ign0 = CI.ignore_state(root, also=[("suite environment", env)])   # R1 clause 8 (IGN, R1-T9): immediately before
    try:
        r = subprocess.run(argv, cwd=root, capture_output=True, text=True, timeout=SUITE_TIMEOUT, env=env)
        out, rc = r.stdout + r.stderr, r.returncode
    except subprocess.TimeoutExpired as exc:
        out, rc = (exc.stdout or b"").decode() if isinstance(exc.stdout, bytes) else (exc.stdout or ""), "timeout"
    ign = CI.ignore_refusal(ign0, CI.ignore_state(root, also=[("suite environment", env)]), "the suite")
    (ev / f"{label}.txt").write_text(out[-200000:] + (f"\nIGNORE STATE: {ign}\n" if ign else ""))
    fails, unknown, _ = RBND.report_failures(report, token, out,   # B185 finding 1: the kit's report, not display text
                                             exit_code=rc if isinstance(rc, int) else None)   # C2a10 (B192 #1)
    summ = next((m.group(1) for ln in reversed(out.splitlines()) if (m := SUMMARY.search(ln))), None)
    ran = rc in (0, 1) and summ is not None      # pytest: 0 all passed, 1 some failed; 2-5 = interrupted/usage/none
    res = {"exit": rc, "summary": summ, "failures": fails, "ran": ran, "seconds": round(time.time() - t0, 1)}
    if ran and unknown:                          # S1_new/S2_new compare id sets: an unknown set does not count
        res.update(ran=False, exit="failing ids not all known", why=unknown)
    if ign:                                      # the result does not count: INCONCLUSIVE at every caller
        res.update(ran=False, exit="ignore state changed", why=ign)
    return res


def amend(root, x):
    """The receiver's own-row amendment, as its prompt states it: sha256_current re-pinned for one artifact of one
    row, sha256_at_v3.30.0 kept, one sentence appended to amended_post_tag. Semantic edit (the suite reads JSON)."""
    p = root / x["path"]
    doc = json.loads(p.read_text())
    hits = 0

    def walk(o):
        nonlocal hits
        if isinstance(o, dict):
            if o.get("id") == x["row"]:
                for art in o.get("runtime_payload", []):
                    if art.get("path") == x["artifact"]:
                        art["sha256_current"] = x["sha256"]
                        art["amended_post_tag"] = (art.get("amended_post_tag", "") + " " + x["note"]).strip()
                        hits += 1
            for v in o.values():
                walk(v)
        elif isinstance(o, list):
            for v in o:
                walk(v)
    walk(doc)
    CI.contained_write(root, x["path"], (json.dumps(doc, indent=2) + "\n").encode())
    actual = sha(root / x["artifact"])
    return {"row": x["row"], "artifact": x["artifact"], "entries_amended": hits,
            "pinned_equals_file": actual == x["sha256"]}


STEP = "rehearse_repair"
NOT_FINISHED = {"state": "started, not finished", "verdict": "FAIL", "results": []}   # what the result file holds until a run reaches its end


def rehearse_or_refuse(r, pre_head, scratch, ev_root):
    """rehearse(), with R4 clause 3 and C7: any failure becomes this receiver's `REFUSED: <why>` result."""
    try:
        return rehearse(r, pre_head, scratch, ev_root)
    except Exception as e:                                  # noqa: BLE001 — R4 clause 4: no traceback
        return {"aget": r.get("aget"), "verdict": f"REFUSED: {type(e).__name__}: {e}"}


def placement_refusals(copy, r, todo):
    """R4 C2, before the first checkout, suite or write in the copy: each path to place is writable (destination_refusal,
    op write), each amendment's file exists and is writable, and each staged source is a regular file."""
    out = []
    if not r.get("placed_by_apply"):
        for i in todo:
            why = CI.destination_refusal(copy, i["path"], "write")
            if why:
                out.append(f"a path to place is not safe to write in the copy: {why}")
            st = i.get("staged")
            if not st or not Path(st).is_file() or Path(st).is_symlink():
                out.append(f"the staged source for {i['path']} is not a regular file: {st}")
    for x in r.get("amendments", []):
        why = CI.destination_refusal(copy, x["path"], "write") or (
            None if (copy / x["path"]).is_file() else f"{copy / x['path']} does not exist")
        if why:
            out.append(f"an amendment's file is not safe to write in the copy: {why}")
    return out


def checkout(copy, rev):
    """Check out `rev` in the copy and read HEAD back, then ask LINKS again (R1 clause 4: the checkout makes that
    commit's symbolic links); None when it reached `rev` and no link leads outside the copy, else the reason."""
    try:
        env = kit_git_env(copy)
    except CI.ContainmentRefused as e:                   # B160 finding 1
        return f"checkout of {rev[:12]} not made: {e}"
    why = CI.act_refusal(copy, env, copy)                # B165 finding 1: identity and LINKS before the act
    if why:
        return f"checkout of {rev[:12]} not made: {why}"
    p = git(copy, "checkout", "-q", "-f", rev, env=env)   # R1-T15: no copied hook runs
    got = git(copy, "rev-parse", "HEAD").stdout.strip()
    if p.returncode or got != rev:
        return (f"checkout of {rev[:12]} failed (exit {p.returncode}, HEAD {got[:12] or 'unreadable'}: "
                f"{(p.stderr.strip() or 'no output').splitlines()[-1][:120]})")
    why = CI.checked_out_refusal(copy)   # LINKS, and the push routes again (B154 finding 1)
    return f"after the checkout of {rev[:12]}: {why}" if why else None


def rehearse(r, pre_head, scratch, ev_root):
    """Rehearse one receiver's repair on a throwaway copy and return the result with its verdict."""
    copy = scratch / r["aget"]
    res = {"aget": r["aget"], "copy": str(copy), "pre_head": pre_head, "head": r["head"]}
    why = CI.name_refusal(r["aget"]) or CI.run_child_refusal(scratch, copy, "the rehearsal copy folder")
    if why:                                            # B162 finding 1, before the evidence folder below
        res["verdict"] = f"REFUSED: {why}"
        return res
    ev = ev_root / r["aget"]
    ev.mkdir(parents=True, exist_ok=True)
    try:                     # R3 (B148 finding 2): every item has a meaning row before any item is filtered by op
        PL.item_rows(r)
    except PL.IM.UnknownClassification as e:
        res["verdict"] = f"REFUSED: UNKNOWN CLASSIFICATION: {e}; nothing was copied"
        return res
    # Every copy the kit makes goes through copy_isolation: the folder is not the receiver's own, and git run in the
    # copy acts on the copy, before anything is removed, checked out or run.
    why = CI.place_refusal(copy, r["location"], "the rehearsal copy folder")
    if why:
        res["verdict"] = f"INCONCLUSIVE: {why}"
        return res
    if not os.path.lexists(Path(r["location"]) / ".git"):
        res["verdict"] = (f"INCONCLUSIVE: {r['location']} has no .git of its own; no kit route rehearses it; "
                          "nothing was removed or copied")
        return res
    if os.path.lexists(copy):                         # E2g: a run's folder is fresh; nothing is removed in it
        res["verdict"] = f"INCONCLUSIVE: {copy} already exists in this run's folder; nothing was removed or copied"
        return res
    shutil.copytree(r["location"], copy, symlinks=True)
    why = CI.isolate(copy, "remove", member=True)
    if why:
        res["verdict"] = f"INCONCLUSIVE: the rehearsal copy is not usable, nothing was run in it: {why}"
        return res
    if git(copy, "rev-parse", "HEAD").stdout.strip() != r["head"]:
        res["verdict"] = "INCONCLUSIVE: the receiver's HEAD moved since the packet was prepared"
        return res
    todo = [i for i in r["items"] if i["op"] in ("write", "write-upstream")]
    refused = placement_refusals(copy, r, todo)
    if refused:
        res["verdict"] = f"REFUSED: {refused[0]}"
        return res
    why = checkout(copy, pre_head)
    if why:
        res["verdict"] = f"REFUSED: {why}"
        return res
    res["S0"] = suite(copy, "S0_baseline", ev)
    why = checkout(copy, r["head"])
    if why:
        res["verdict"] = f"REFUSED: {why}"
        return res
    res["S1"] = suite(copy, "S1_unrepaired", ev)
    if r.get("placed_by_apply"):
        # F5-apply-script: the principal's reviewed apply_protected.py, run here on the COPY (list location = copy)
        lst = ev / "apply_list_copy.json"
        lst.write_text(json.dumps(PL.apply_list({"batch": "1-repair-rehearsal", "receivers": [r]},
                                                {r["aget"]: str(copy)}), indent=2) + "\n")
        ap = subprocess.run([sys.executable, str(HERE / "apply_protected.py"), "--list", str(lst), "--apply",
                             "--receipt-dir", str(ev), "--run", str(Path(copy).parent)],   # BIND (R1-T7)
                            capture_output=True, text=True)
        res["apply"] = {"exit": ap.returncode, "out": ap.stdout.strip()[-400:]}
        if ap.returncode != 0:
            res["verdict"] = f"REFUSED: the principal's apply script refused or failed on the copy (exit {ap.returncode})"
            return res
    else:
        for i in todo:   # what `cp -f <staged> <path>` does, at the act: never through a link (R1 clause 2)
            CI.contained_write(copy, i["path"], Path(i["staged"]).read_bytes())
    res["amendments"] = [amend(copy, x) for x in r.get("amendments", [])]
    res["S2"] = suite(copy, "S2_repaired", ev)
    res["digest_mismatches"] = [i["path"] for i in r["items"] if i["op"] in ("write", "write-upstream", "verify")
                                and sha(copy / i["path"]) != i["sha256"]]
    res["wrong_source"] = [i["path"] for i in r["items"] if i["path"] in WR.CORRECTION_ROW_4
                           and i.get("source") and not i["source"].startswith("aget@")]
    base = set(res["S0"]["failures"])
    res["S1_new"] = sorted(set(res["S1"]["failures"]) - base)
    res["S2_new"] = sorted(set(res["S2"]["failures"]) - base)
    res["S2_fixed_vs_baseline"] = sorted(base - set(res["S2"]["failures"]))
    if not all(res[s]["ran"] for s in ("S0", "S1", "S2")):
        res["verdict"] = "INCONCLUSIVE: a suite did not run to a summary (" + ", ".join(
            f"{s} exit {res[s]['exit']}" for s in ("S0", "S1", "S2") if not res[s]["ran"]) + ")"
    elif res["digest_mismatches"] or res["wrong_source"] or res["S2_new"] or any(
            m["entries_amended"] != 1 or not m["pinned_equals_file"] for m in res["amendments"]):
        res["verdict"] = "FAIL"
    elif not res["S1_new"]:
        res["verdict"] = "FAIL: the regression case shows no new failure, so this rehearsal cannot see the defect"
    else:
        res["verdict"] = "PASS"
    return res


def main(argv=None):
    """Command-line entry point: rehearse a repair packet on throwaway copies of its receivers."""
    argv = sys.argv[1:] if argv is None else list(argv)
    # R2 clause 1, first act, before argument parsing: record this run and invalidate any earlier result for this
    # output, so a usage error or a stop at any later step leaves no earlier result current.
    run_id, early = RBND.producer_start(STEP, RBND.prescan(argv, "--out"), NOT_FINISHED)
    if early:
        print(early)
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--previous-packet", type=Path, required=True)
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--only", nargs="*")
    a = ap.parse_args(argv)
    # First act, before any input is read or any folder is made: the result file says NOT FINISHED, so a run that
    # stops at any later step leaves no earlier result.
    a.out.write_text(json.dumps(NOT_FINISHED, indent=2) + "\n")
    try:                 # R4 C1: inputs, and every receiver's previous head, before any copy is made
        packet = json.loads(a.packet.read_text())
        prev = {r["aget"]: r["head"] for r in json.loads(a.previous_packet.read_text())["receivers"]}
        receivers = [r for r in packet["receivers"] if not a.only or r["aget"] in a.only]
        missing = [r["aget"] for r in receivers if r["aget"] not in prev]
        if missing:
            raise KeyError(f"receivers missing from --previous-packet: {missing}")
        for r in receivers:                            # B162 finding 1: before any folder is made
            why = CI.name_refusal(r["aget"])
            if why:
                raise ValueError(why)
        # R1 clause 5 (E2g): --scratch is the work root; this run's copies go into a fresh folder in it. B162 finding
        # 4: the avoid set holds every receiver's declared sibling sources too, as the other work-root callers' do
        avoid = [x for r in packet["receivers"]
                 for x in (r["location"], *CI.sibling_sources(r["location"], r.get("sibling_reads") or []))]
        run = CI.run_folder(a.scratch, avoid + [R.framework_root()], prefix="repair-")
        (a.scratch / "evidence").mkdir(exist_ok=True)
    except (OSError, ValueError, KeyError, TypeError, CI.ContainmentRefused) as e:
        RBND.write_result(STEP, a.out, {"verdict": "REFUSED", "why": f"{type(e).__name__}: {e}", "results": []},
                          run_id, 2)
        print(f"REFUSED: {type(e).__name__}: {e}; no copy was made")
        return 2
    ev_root = a.scratch / "evidence"   # full suite output can hold receiver content: kept out of this repository
    started = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    head = {"row": "V3.6", "packet": str(a.packet), "packet_sha256": sha(a.packet), "started": started,
            "run_folder": str(run)}
    a.out.write_text(json.dumps({**head, **NOT_FINISHED}, indent=2) + "\n")     # the same state, with the digest
    with cf.ThreadPoolExecutor(max_workers=max(1, len(receivers))) as pool:
        results = list(pool.map(lambda r: rehearse_or_refuse(r, prev[r["aget"]], run, ev_root), receivers))
    doc = {**head, "ended": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
           "python": sys.version.split()[0], "results": results}
    code = 0 if results and all(x["verdict"] == "PASS" for x in results) else 1
    RBND.write_result(STEP, a.out, doc, run_id, code)
    for x in results:
        print(f"{x['aget']:34s} {x['verdict']}")
        for s in ("S0", "S1", "S2"):
            if s in x:
                print(f"    {s} {x[s]['summary']} ({x[s]['seconds']}s)")
        print(f"    new vs baseline: unrepaired {x.get('S1_new')} | repaired {x.get('S2_new')}")
        if x.get("digest_mismatches") or x.get("wrong_source"):
            print(f"    digest mismatches {x['digest_mismatches']} wrong source {x['wrong_source']}")
    return 0 if results and all(x["verdict"] == "PASS" for x in results) else 1


if __name__ == "__main__":
    sys.exit(main())
