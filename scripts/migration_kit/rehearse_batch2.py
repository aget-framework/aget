#!/usr/bin/env python3
"""V3.6 for batch 2 (route a2) on throwaway copies. No model in the loop.

It reads each packet receiver's folder and copies it into a fresh run folder `mkdtemp(dir=<--scratch>)`, where the list
is applied and the suites run (R1 clause 5, E2g): --scratch is the work root W, refused when it lies inside any git
repository or is, holds or lies inside a receiver, a declared sibling source or the framework root; nothing under it
is removed, and each run's folder is kept (removing old ones is the operator's). Evidence goes to <--scratch>/evidence.
The reference run clones the receiver into a run folder under ~/.cache/aget-suite-at-commit/reference/ and runs its
suite there. The result goes to --out (keep it outside the receivers' repositories: operator rule, not enforced). The
tool does not confine what a suite writes while it runs; the suites and the known-missing auditor run under the
contained environment (R1 ENV), and the auditor must lie inside the copy's run folder or the kit.

Migration receivers (one receiver, one receiver):
  S0  the copy at HEAD: suite (baseline)
  --  the approved write list applied to the COPY by the reviewed apply_protected.py (list location = copy); the
      version carriers bumped mechanically as the prompt tells the receiver (.aget/version.json aget_version,
      and in manifest.yaml, if present, the first `version:` followed by the from-release). MERGE items are the
      receiver's and are not rehearsed (listed).
  S2  suite. PASS: no failure new against S0, every placed or protected write equal to its listed `post`.
Track-skills receiver (one receiver):
  the list's rewrite applied to the copy; the BARE `git check-ignore --no-index` exit code must not be 0 for any skill
  (only 0 fails; an error code is not told apart from 1); each path staged as the prompt says; the suite after must
  show no failure that the suite before did not (the two suite runs are not otherwise compared).
An unrunnable suite is INCONCLUSIVE, which is not PASS.

All or nothing, per receiver (R4): every precondition of a receiver's copy is tested before anything is removed or
written (the member has its own `.git`; each declared sibling is a folder beside it; every path the rehearsal writes in
the copy is a regular file or absent, through no link). A receiver whose copy fails a precondition, or whose rehearsal
raises, reads `REFUSED: <why>`, nothing more runs in that copy, and the other receivers are still rehearsed; the
result file names every receiver. Copies are disposable and are not restored. The writes the rehearsal makes in a copy
go through the contained writer (copy_isolation.contained_write: never through a link, never by truncation in place).
An input that cannot be read is a refusal of the run: the result reads REFUSED and the exit is 2.

Usage: python3 scripts/migration_kit/rehearse_batch2.py --packet <packet> --list <write list>
           --scratch <dir> --out <result.json>
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import importlib.util
import json
import os
import re
import shutil
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_target as R  # noqa: E402  (the kit's one release parameter; carriage row 24)
import copy_isolation as CI  # noqa: E402  (the one routine every copy the kit makes goes through)
import result_binding as RBND  # noqa: E402  (R2: run log and result binding)
import item_meaning as IM  # noqa: E402  (R3: one meaning table per classification)

B1 = Path(__file__).resolve().parent
_s = importlib.util.spec_from_file_location("rehearse_repair", B1 / "rehearse_repair.py")
RR = importlib.util.module_from_spec(_s)
_s.loader.exec_module(RR)
_t = importlib.util.spec_from_file_location("suite_at_commit", B1 / "suite_at_commit.py")
SAC = importlib.util.module_from_spec(_t)
_t.loader.exec_module(SAC)


STEP = "rehearse_batch2"
NOT_FINISHED = {"state": "started, not finished", "verdict": "FAIL", "results": []}   # what the result file holds until a run reaches its end


def copy_of(r, scratch, siblings=()):
    """The receiver's copy. With `siblings` (paths OUTSIDE its folder that its tests read, e.g. `../aget`; G3.6 row
    12, B2), the copy sits in its own `<aget>.root/` folder and each sibling is copied to the same relative place, so
    the copy's S0 reads what the real Aget's tests read (batch 8: without `../aget`, the identifier test already
    failed in S0 and its real regression could not show as new).
    `scratch` is this run's own folder (main() makes it fresh under the work root), so nothing is removed to make the
    copy: a copy folder that already exists there is refused (E2g).
    Every copy goes through copy_isolation: the folder filled must not be the receiver's own folder or a declared
    sibling's source, hold one or lie inside one (asked before anything is copied; R1-T1); the receiver's copy and each copied sibling that has a
    `.git` entry must be its own working tree with its own git folder (asked before any git command in it); the
    receiver's copy then loses its remotes and each sibling's remotes get a push URL that cannot resolve. Raises
    ValueError, with nothing run in the copy, when one of these does not hold."""
    why = CI.name_refusal(r["aget"])                   # B162 finding 1: a name, never a path
    if why:
        raise ValueError(why)
    base = scratch / f"{r['aget']}.root" if siblings else None
    dest = (base / r["aget"]) if siblings else (scratch / r["aget"])
    why = CI.run_child_refusal(scratch, base or dest, "the rehearsal copy folder") or CI.place_refusal(
        base or dest, r["location"], "the rehearsal copy folder",
                           sources=CI.sibling_sources(r["location"], siblings))
    if why:
        raise ValueError(f"{r['aget']}: {why}")
    # R4: every copy precondition before the first removal (the member's own .git, the siblings are folders)
    if not os.path.lexists(Path(r["location"]) / ".git"):
        raise ValueError(f"{r['aget']}: {r['location']} has no .git of its own (a member that is a folder inside "
                         "another repository?); no kit route rehearses it; nothing was removed or copied")
    for rel_path in siblings:
        src = (Path(r["location"]) / rel_path).resolve()
        target = (dest / rel_path).resolve()
        if not src.is_dir() or base.resolve() not in target.parents:
            raise ValueError(f"sibling {rel_path!r}: not a folder beside the Aget ({src}) or it leaves the copy root")
    if os.path.lexists(base or dest):                  # E2g: a run's folder is fresh; nothing is removed in it
        raise ValueError(f"{r['aget']}: {base or dest} already exists in this run's folder; nothing was removed or "
                         "copied")
    if siblings:
        for rel_path in siblings:
            src = (Path(r["location"]) / rel_path).resolve()
            target = (dest / rel_path).resolve()
            shutil.copytree(src, target, symlinks=True)
            why = CI.isolate(target, "no-push", run=base)
            if why:
                raise ValueError(f"sibling {rel_path!r}: its copy is not usable, nothing was run in it: {why}")
    shutil.copytree(r["location"], dest, symlinks=True)
    why = CI.isolate(dest, "remove", member=True, run=base or dest)   # LINKS: inside this run's folder
    if why:
        raise ValueError(f"{r['aget']}: the rehearsal copy is not usable, nothing was run in it: {why}")
    return dest


def apply_on_copy(entry, copy, ev):
    """Run the protected-write script on the throwaway copy; return its exit code and the tail of its output."""
    lst = ev / "write_list_copy.json"
    doc = json.loads(Path(entry["_list"]).read_text())
    doc["agets"] = [{**{k: v for k, v in entry.items() if k != "_list"}, "location": str(copy)}]
    lst.write_text(json.dumps(doc, indent=2) + "\n")
    p = subprocess.run([sys.executable, str(B1 / "apply_protected.py"), "--list", str(lst), "--apply",
                        "--receipt-dir", str(ev), "--run", str(Path(copy).parent)],   # BIND: the copy's run folder
                       capture_output=True, text=True)
    return p.returncode, p.stdout.strip()[-400:]


def safe_in_copy(copy, rel):
    """copy / rel, after copy_isolation.destination_refusal(): the copy keeps the member's symbolic links
    (symlinks=True), and a write through one lands wherever it points. Raises ValueError, with nothing written."""
    why = CI.destination_refusal(copy, rel)
    if why:
        raise ValueError(f"not safe to write in the rehearsal copy: {why}")
    return copy / rel


def write_in_copy(copy, rel, text):
    """Write `text` to copy/rel through the contained writer (R1 at the act). Raises ValueError, with nothing
    written, when the act is refused."""
    try:
        CI.contained_write(copy, rel, text.encode())
    except CI.ContainmentRefused as e:
        raise ValueError(f"not safe to write in the rehearsal copy: {e}") from None


def copy_write_paths(copy, r):
    """Every path the rehearsal itself writes in the copy, after the apply: the version carriers, the extra carriers
    that exist, the rename targets and the KNOWN_MISSING file."""
    paths = [".aget/version.json"]
    if os.path.lexists(copy / "manifest.yaml"):
        paths.append("manifest.yaml")
    paths += [rel for rel in r.get("extra_carriers", []) if os.path.lexists(copy / rel)]
    paths += [x["path"] for x in r.get("renames", [])]
    if r.get("known_missing_ruling"):
        paths.append(r["known_missing_ruling"]["file"])
    return paths


def copy_write_refusals(copy, r):
    """R4 C2 for the rehearsal's own writes, before the apply runs: each path is a regular file with one name,
    through no link (destination_refusal, op write), and exists (each is read before it is written)."""
    out = []
    for rel in copy_write_paths(copy, r):
        why = CI.destination_refusal(copy, rel, "write")
        if why:
            out.append(why)
        elif not os.path.lexists(copy / rel):
            out.append(f"{copy / rel} does not exist")
    return out


def bump_carriers(copy, r=None, today=None):
    """Set the copy's .aget/version.json aget_version to the target version; in manifest.yaml, when present, replace the
    from-release at the first `version:` it follows (extra carriers: see the comment below), as the receiver's session is told to do."""
    vj = safe_in_copy(copy, ".aget/version.json")
    d = json.loads(vj.read_text())
    d["aget_version"] = R.TO
    write_in_copy(copy, ".aget/version.json", json.dumps(d, indent=2) + "\n")
    mf = copy / "manifest.yaml"
    if mf.is_file() or mf.is_symlink():
        mf = safe_in_copy(copy, "manifest.yaml")
        t = mf.read_text()
        write_in_copy(copy, "manifest.yaml",
                      re.sub(r"(version:\s*['\"]?)" + re.escape(R.FROM), r"\g<1>" + R.TO, t, count=1))
    # A receiver-specific carrier its own hooks demand (G3.6 row 8: one receiver's data/fleet/CANONICAL_AGET_VERSION.yaml,
    # whose pre-commit hook asserts canonical_version == .aget/version.json aget_version): in the first line that
    # begins with canonical_version / aget_version / version and whose value starts with the from version, that version is
    # replaced by the target version; in the first line that begins with `stamped`, the date is replaced by today, as the receiver's session is told to do.
    today = today or dt.date.today().isoformat()
    for rel in (r or {}).get("extra_carriers", []):
        f = copy / rel
        if f.is_file() or f.is_symlink():
            f = safe_in_copy(copy, rel)
            t = re.sub(r"^((?:canonical_version|aget_version|version):\s*['\"]?)" + re.escape(R.FROM), r"\g<1>" + R.TO,
                       f.read_text(), count=1, flags=re.M)
            write_in_copy(copy, rel, re.sub(r"^(stamped:\s*)\S+", r"\g<1>" + today, t, count=1, flags=re.M))


def emulate_renames(copy, r):
    """The receiver's step 4d import renames, applied mechanically so V3.6 sees their effect (row 11: the framework
    Aget's own run of its step 4c found 3 new failures V3.6 could not see). Returns [(path, replacements)]."""
    done = []
    for x in r.get("renames", []):
        f = safe_in_copy(copy, x["path"])
        text = f.read_text()
        new, count = re.subn(rf"\b{re.escape(x['old'])}\b", x["new"], text)
        write_in_copy(copy, x["path"], new)
        done.append((x["path"], count))
    return done


def emulate_known_missing(copy, r):
    """The receiver's ratchet edit, done mechanically (G3.6 row 8): KNOWN_MISSING becomes (old entries its auditor still
    finds) + (the entries the principal ruled known-missing). Nothing else is added, so any OTHER newly missing
    instrument still fails the receiver's own test. Returns (removed, added)."""
    k = r.get("known_missing_ruling")
    if not k:
        return None
    f = safe_in_copy(copy, k["file"])
    text = f.read_text()
    m = re.search(r"^KNOWN_MISSING = \{\n(.*?)^\}\n", text, re.S | re.M)
    old = set(re.findall(r'\(\s*"([^"]+)",\s*"([^"]+)"\s*\)', m.group(1)))
    auditor = auditor_path(copy, k["auditor"])
    try:
        env = RR.code_env(copy)
        why = (CI.env_route_refusal(Path(os.path.abspath(copy)), env, Path(os.path.abspath(copy)).parent)
               if (Path(copy) / ".git").is_dir() else None)
        if why:
            raise CI.ContainmentRefused(f"under the contained environment: {why}")
    except CI.ContainmentRefused as e:                  # R1 ENV, checked before use (as RR.suite())
        raise CopyStepFailed(f"the known-missing auditor was not run: {e}") from None
    ign0 = CI.ignore_state(copy, also=[("auditor environment", env)])   # R1 clause 8 (IGN): around the auditor too
    out = subprocess.run([sys.executable, str(auditor)], cwd=copy, capture_output=True, text=True, env=env).stdout
    why = CI.ignore_refusal(ign0, CI.ignore_state(copy, also=[("auditor environment", env)]),
                            "the known-missing auditor")
    if why:
        raise CopyStepFailed(f"the known-missing auditor's result does not count: {why}")
    found = {tuple(x.strip() for x in ln.split("  ->  ")) for ln in out.splitlines() if "  ->  " in ln}
    ruled = {tuple(e) for e in k["entries"]}
    new = sorted((old & found) | ruled)
    body = "".join(f'    ("{s}", "{p}"),\n' for s, p in new)
    write_in_copy(copy, k["file"], text[:m.start(1)] + body + text[m.end(1):])
    return sorted(old - set(new)), sorted(set(new) - old)


def auditor_path(copy, auditor):
    """The known-missing auditor to run (R1 clause 1, running code; E2g): `auditor`, relative to the copy or absolute,
    with every link resolved, must be a regular file inside the copy's run folder (the folder holding the copy) or
    inside the kit's own folder. A path into the live receiver, or anywhere else, would run code outside the run.
    Raises CopyStepFailed, with nothing run."""
    p = Path(auditor) if os.path.isabs(auditor) else Path(copy) / auditor
    real = Path(os.path.realpath(p))
    bounds = [Path(os.path.realpath(Path(copy).parent)), Path(os.path.realpath(B1))]
    if not any(b in real.parents for b in bounds):
        raise CopyStepFailed(f"the known-missing auditor {auditor} resolves to {real}, outside the copy's run folder "
                             "and the kit; it was not run")
    if not real.is_file():
        raise CopyStepFailed(f"the known-missing auditor {auditor} is not a file in the copy ({real}); it was not run")
    return real


def commit_applied(copy, r):
    """Row 13 (c): commit what the rehearsal changed in the disposable copy before S2, so a test that needs a clean
    tree reads the migration as the receiver's session will leave it (committed). Pre-existing changes stay
    uncommitted, as in S0, staged ones included: the commit is limited to the migration's paths (`--only`), and the
    paths it committed are read back (B160 finding 4). It runs under the contained environment, so no copied hook
    runs (R1-T15). Returns the committed paths; raises CopyStepFailed otherwise."""
    pre = set(r.get("pre_dirty") or [])
    # B158 finding 1 (byte for byte); B161 finding 1: no rename compression, so a rename names both endpoints
    changed = set(CI.git_paths(copy, "diff", "--name-only", "--no-renames", "HEAD"))
    changed |= set(CI.git_paths(copy, "ls-files", "--others", "--exclude-standard"))
    paths = sorted(changed - pre)
    if paths:
        try:
            env = RR.kit_git_env(copy)
        except CI.ContainmentRefused as e:              # B160 finding 1
            raise CopyStepFailed(f"copy commit not made: {e}") from None
        env = {**env, "GIT_LITERAL_PATHSPECS": "1"}     # B161 finding 2: each path names itself, never a pattern
        why = CI.act_refusal(copy, env, Path(copy).parent)   # B165 finding 1: identity and LINKS, after member code
        if why:
            raise CopyStepFailed(f"copy commit not made: {why}")
        before = RR.git(copy, "rev-parse", "HEAD").stdout.strip()
        present = [x for x in paths if os.path.lexists(Path(copy) / x)]
        gone = [x for x in paths if x not in present]   # B161 finding 1: a deletion or a rename's source
        steps = ([("add", "-f", "--", *present)] if present else []) + (
            [("rm", "--cached", "-q", "--ignore-unmatch", "--", *gone)] if gone else []) + [
            ("-c", "user.name=v36", "-c", "user.email=v36@rehearsal", "commit", "-q", "--no-verify",
             "--only", "-m", "V3.6 rehearsal: the applied migration (disposable copy)", "--", *paths)]
        for step in steps:
            p = RR.git(copy, *step, env=env)
            if p.returncode:
                raise CopyStepFailed(f"copy commit failed: git {step[0] if step[0] != '-c' else 'commit'} exit "
                                     f"{p.returncode} ({(p.stderr.strip() or 'no output').splitlines()[-1][:160]})")
        committed = sorted(CI.git_paths(copy, "diff", "--name-only", "--no-renames", before, "HEAD"))   # B161 #1
        if committed != paths:                          # B160 finding 4: read back what the commit took
            raise CopyStepFailed(f"the copy commit took {committed[:5]}, not the migration's paths {paths[:5]}")
    return paths


class CopyStepFailed(Exception):
    """A step of the rehearsal in its copy failed; the receiver reads REFUSED and nothing more runs in that copy."""


def blind_spot_report(r, s0, scratch):
    """Row 13 (b): compare the copy's S0 with a clean-clone run of the Aget's current commit (the packet's HEAD) with its
    siblings, never its live folder (a full suite there writes tracked files, gh#1961 class). Tests failing only on
    the copy are the rehearsal's blind spots: a regression in them cannot show as new. The Aget's last CI result on
    that commit is recorded beside it as corroboration where it has CI. The reference applies the CI exclusions that suite_at_commit.py finds;
    a copy failure the reference excludes is listed as excluded, not blind."""
    ref = SAC.run(r["location"], r["aget"], r["head"], r.get("suite_cmd"), r.get("sibling_reads") or [],
                  work=SAC.WORK / "reference", hook=False)
    out = {"reference": {k: ref.get(k) for k in ("verdict", "sha", "summary", "failures", "why", "excluded")},
           "reference_ci": ci_on_commit(r["location"], r["head"])}
    if ref.get("verdict") not in ("PASS", "FAIL"):
        out["blind_spots"] = None
        out["blind_spots_why"] = f"reference run {ref.get('verdict')}: {ref.get('why')}"
        return out
    copy_fail, ref_fail, excl = set(s0.get("failures") or []), set(ref.get("failures") or []), set(ref.get("excluded") or [])
    # C2e (D-8, S-193/S-325): CI corroborates only when every committed root workflow passed on this SHA
    ci_green = isinstance(out["reference_ci"], dict) and out["reference_ci"].get("state") == "PASS"
    if ci_green and ref_fail:
        # supervisor:L816: the reference shares the local environment with the copy, so a failure in BOTH is invisible
        # to copy-minus-reference. CI passed this commit (with the same exclusions), so each such failure is local:
        # the rehearsal is blind there too (row 13 proof, 2026-09-29: 4 shared failures, CI success, list was empty).
        out["reference_disagrees_with_ci"] = sorted(ref_fail - excl)
        out["blind_spots"] = sorted(copy_fail - excl)
    else:
        out["blind_spots"] = sorted(copy_fail - ref_fail - excl)
    out["copy_failures_excluded_by_ci"] = sorted(copy_fail & excl)
    return out


def ci_on_commit(location, sha):
    """The CI state of a commit, read as the ledger reads it (C2e, D-8 / R2-T3 new case, S-193/S-325): every root
    workflow committed at `sha` must have a successful run on exactly that SHA (`fleet_ledger.ci_result`, with its
    run-limit and REST corroboration). A success of some other workflow, or a list cut at its limit, is not PASS."""
    import importlib.util as _iu
    spec = _iu.spec_from_file_location("v335_fleet_ledger", Path(__file__).resolve().parent / "fleet_ledger.py")
    FL = sys.modules.get("v335_fleet_ledger")
    if FL is None:
        FL = _iu.module_from_spec(spec)
        spec.loader.exec_module(FL)
    try:
        wfs = FL.committed_workflows(location, sha)
        state, why = FL.ci_result(location, sha, True, workflows=wfs) if wfs else ("NO-WORKFLOW", "")
    except FL.Unavailable as e:
        return {"state": "UNAVAILABLE", "why": str(e)[:200]}
    return {"state": state, "why": why}


def receiver_refusal(r):
    """Why a packet receiver's nested fields cannot be rehearsed, or None (C1, before any receiver work; B145). Its
    name must be one folder name (B162 finding 1)."""
    name = r.get("aget")
    why = CI.name_refusal(name)
    if why:
        return why
    for key in ("location", "head"):
        if not isinstance(r.get(key), str):
            return f"receiver {name}: `{key}` is not a string"
    for key in ("sibling_reads", "extra_carriers", "track_paths", "pre_dirty"):
        v = r.get(key) or []
        if not isinstance(v, list) or not all(isinstance(x, str) for x in v):
            return f"receiver {name}: `{key}` is not a list of strings"
    items = r.get("items") or []
    if not isinstance(items, list) or not all(isinstance(i, dict) and isinstance(i.get("path"), str)
                                              and isinstance(i.get("op"), str) for i in items):
        return f"receiver {name}: `items` is not a list of objects with string `path` and `op`"
    renames = r.get("renames") or []
    if not isinstance(renames, list) or not all(isinstance(x, dict) and all(isinstance(x.get(k), str)
                                                                            for k in ("path", "old", "new"))
                                                for x in renames):
        return f"receiver {name}: `renames` is not a list of objects with string `path`, `old` and `new`"
    km = r.get("known_missing_ruling")
    if km is not None and not (isinstance(km, dict) and isinstance(km.get("file"), str)
                               and isinstance(km.get("auditor"), str) and isinstance(km.get("entries"), list)):
        return f"receiver {name}: `known_missing_ruling` is not an object with `file`, `auditor` and `entries`"
    if r.get("suite_cmd") is not None and not isinstance(r.get("suite_cmd"), str):
        return f"receiver {name}: `suite_cmd` is not a string"
    return None


def rehearse_or_refuse(r, entry, scratch, ev_root):
    """rehearse(), with R4 clause 3 and C7: any failure becomes this receiver's `REFUSED: <why>` result, nothing more
    runs in its copy, and the other receivers are not affected."""
    try:
        if entry is None:
            return {"aget": r.get("aget"), "verdict": "REFUSED: the write list has no entry for this receiver"}
        return rehearse(r, entry, scratch, ev_root)
    except CopyStepFailed as e:
        return {"aget": r.get("aget"), "verdict": f"REFUSED: {e}"}
    except Exception as e:                                  # noqa: BLE001 — R4 clause 4: no traceback
        return {"aget": r.get("aget"), "verdict": f"REFUSED: {type(e).__name__}: {e}"}


def rehearse(r, entry, scratch, ev_root):
    """Rehearse one receiver's batch on a throwaway copy and return the result with its verdict."""
    why = CI.name_refusal(r.get("aget"))               # B162 finding 1: before its evidence folder is made
    if why:
        return {"aget": r.get("aget"), "verdict": f"REFUSED: {why}"}
    ev = ev_root / r["aget"]
    ev.mkdir(parents=True, exist_ok=True)
    res = {"aget": r["aget"], "mode": IM.receiver_mode(r), "sibling_reads": r.get("sibling_reads") or []}
    try:                     # R3 (B148 finding 2's class): every item has a meaning row before any receiver work
        for i in r.get("items", []):
            IM.meaning(i)
    except IM.UnknownClassification as e:
        res["verdict"] = f"REFUSED: UNKNOWN CLASSIFICATION: {e}; nothing was copied"
        return res
    copy = copy_of(r, scratch, r.get("sibling_reads") or ())
    if RR.git(copy, "rev-parse", "HEAD").stdout.strip() != r["head"]:
        res["verdict"] = "INCONCLUSIVE: the Aget's HEAD moved since the packet"
        return res
    if r.get("mode") != "track-skills":
        refused = copy_write_refusals(copy, r)
        if refused:      # R4 C2/C7: before any suite or the apply, so nothing is written in the copy and nothing more runs there
            res["verdict"] = f"REFUSED: a path the rehearsal writes in the copy is not writable: {refused[0]}"
            return res
    res["S0"] = RR.suite(copy, "S0_baseline", ev, r.get("suite_cmd"))
    res.update(blind_spot_report(r, res["S0"], scratch))
    code, out = apply_on_copy(entry, copy, ev)
    res["apply"] = {"exit": code, "out": out}
    if code != 0:
        res["verdict"] = f"REFUSED: the apply script refused or failed on the copy (exit {code})"
        return res
    if IM.receiver_mode(r) == "track-skills":     # D-3 (S-343): an unknown mode raises -> REFUSED, never "migrate"
        skills = [p for p in r["track_paths"] if p != ".gitignore"]
        still = [p for p in skills if RR.git(copy, "check-ignore", "--no-index", p).returncode == 0]
        kenv = RR.kit_git_env(copy)
        why = CI.act_refusal(copy, kenv, Path(copy).parent)   # B165 finding 1: before the kit's `git add`
        if why:
            raise CopyStepFailed(f"the track-skills paths were not staged: {why}")
        for p in r["track_paths"]:
            ad = RR.git(copy, "add", p, env=kenv)
            if ad.returncode:      # D2 (R4-T10, S-091 residue): a failed `git add` refuses, never staged silently
                raise CopyStepFailed(f"copy commit failed: git add {p} exited {ad.returncode}: "
                                     f"{(ad.stderr or '').strip()[-120:]}")
        staged = set(CI.git_paths(copy, "diff", "--cached", "--name-only"))   # B158 finding 1
        res.update(still_ignored=still, staged=len(staged), unstaged_wanted=sorted(set(r["track_paths"]) - staged))
        res["committed_in_copy"] = commit_applied(copy, r)
        res["S2"] = RR.suite(copy, "S2_after", ev, r.get("suite_cmd"))
        ok = not still and not res["unstaged_wanted"]
    else:
        bump_carriers(copy, r)
        if r.get("renames"):
            res["renames_emulated"] = emulate_renames(copy, r)
        km = emulate_known_missing(copy, r)
        if km is not None:
            res["known_missing_emulated"] = {"removed": km[0], "added": km[1]}
        res["merges_left_to_receiver"] = [i["path"] for i in r["items"] if IM.meaning(i).edit]
        res["committed_in_copy"] = commit_applied(copy, r)
        res["S2"] = RR.suite(copy, "S2_after", ev, r.get("suite_cmd"))
        res["post_mismatches"] = [o["path"] for o in entry["ops"] if o["op"] in ("write", "write-upstream",
                                                                                 "replace-line")
                                  and RR.sha(copy / o["path"]) != o["post"]]
        ok = not res["post_mismatches"]
    base = set(res["S0"]["failures"])
    res["S2_new"] = sorted(set(res["S2"]["failures"]) - base)
    if not (res["S0"]["ran"] and res["S2"]["ran"]):
        res["verdict"] = "INCONCLUSIVE: a suite did not run to a summary"
    elif not ok or res["S2_new"]:
        res["verdict"] = "FAIL"
    else:
        res["verdict"] = "PASS"
    return res


def main(argv=None):
    """Command-line entry point: rehearse a batch's write list on throwaway copies of its receivers."""
    argv = sys.argv[1:] if argv is None else list(argv)
    # R2 clause 1, first act, before argument parsing: record this run and invalidate any earlier result for this
    # output, so a usage error or a stop at any later step leaves no earlier result current.
    run_id, early = RBND.producer_start(STEP, RBND.prescan(argv, "--out"), NOT_FINISHED)
    if early:
        print(early)
        return 2
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--list", type=Path, required=True)
    ap.add_argument("--scratch", type=Path, required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--sibling-read", nargs="*", default=[], metavar="AGET=REL",
                    help="a folder outside the Aget that its tests read, when the packet does not declare it "
                         "(G3.6 row 12 B2; e.g. re-rehearsing a list prepared before `sibling_reads` existed)")
    a = ap.parse_args(argv)
    # First act, before any input is read or any folder is made: the result file says NOT FINISHED, so a run that
    # stops at any later step leaves a result the approval step refuses, and no earlier result.
    a.out.write_text(json.dumps(NOT_FINISHED, indent=2) + "\n")
    R.require()          # the release target is required before any receiver work, after the result is invalidated
    try:                 # R4 C1: an input that cannot be read refuses the run before any receiver work
        packet = json.loads(a.packet.read_text())
        wl = json.loads(a.list.read_text())
        entries = {e["aget"]: {**e, "_list": str(a.list)} for e in wl["agets"]}
        packet["batch"]
        if not isinstance(packet.get("receivers"), list) or not all(
                isinstance(r, dict) and isinstance(r.get("aget"), str) for r in packet["receivers"]):
            raise TypeError("the packet's receivers are not objects with a string `aget`")   # B143 finding 5
        for r in packet["receivers"]:                                                     # B145: nested shapes too
            bad = receiver_refusal(r)
            if bad:
                raise TypeError(bad)
        extra = {}
        for s in a.sibling_read:
            name, _, rel_path = s.partition("=")
            extra.setdefault(name, []).append(rel_path)
        rs = [{**r, "sibling_reads": sorted(set(r.get("sibling_reads") or []) | set(extra.get(r["aget"], [])))}
              for r in packet["receivers"]]
        # R1 clause 5 (E2g, R1-T1): --scratch is the work root; this run's copies go into a fresh folder in it
        avoid = [x for r in rs for x in (r["location"], *CI.sibling_sources(r["location"], r["sibling_reads"]))]
        run = CI.run_folder(a.scratch, avoid + [R.framework_root()],
                            prefix="b" + re.sub(r"[^\w.-]", "_", str(packet["batch"])) + "-")
        (a.scratch / "evidence").mkdir(exist_ok=True)
    except (OSError, ValueError, KeyError, TypeError, CI.ContainmentRefused) as e:
        RBND.write_result(STEP, a.out, {"verdict": "REFUSED", "why": f"input unreadable: {type(e).__name__}: {e}",
                                        "results": []}, run_id, 2)
        print(f"REFUSED: input unreadable: {type(e).__name__}: {e}")
        return 2
    started = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    head = {"row": "V3.6", "batch": packet["batch"], "packet_sha256": RR.sha(a.packet), "list_sha256": RR.sha(a.list),
            "started": started, "run_folder": str(run)}
    a.out.write_text(json.dumps({**head, **NOT_FINISHED}, indent=2) + "\n")     # the same state, with the digests
    with cf.ThreadPoolExecutor(max_workers=max(1, len(rs))) as pool:
        results = list(pool.map(lambda r: rehearse_or_refuse(r, entries.get(r["aget"]), run,
                                                             a.scratch / "evidence"), rs))
    doc = {**head, "ended": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "results": results}
    code = 0 if results and all(x["verdict"] == "PASS" for x in results) else 1
    RBND.write_result(STEP, a.out, doc, run_id, code)
    for x in results:
        print(f"{x['aget']:34s} {x['verdict']}  S0 {x.get('S0', {}).get('summary')} | S2 {x.get('S2', {}).get('summary')}"
              f" | new {x.get('S2_new')} | mismatches {x.get('post_mismatches')} | still ignored "
              f"{x.get('still_ignored')} | merges left {x.get('merges_left_to_receiver')}")
    return 0 if results and all(x["verdict"] == "PASS" for x in results) else 1


if __name__ == "__main__":
    sys.exit(main())
