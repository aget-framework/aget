#!/usr/bin/env python3
"""Launch batch 1's receivers, phase 1 (install, validate, commit, receipt; NO push). Dry-run unless --launch.

Per receiver, in order:
  1. `claude --version` must equal the packet's (E-3); otherwise the whole batch stops;
  2. a pre-launch settings snapshot (after_run_check.py --snapshot) and the settings watcher, started first;
  3. one headless session in the receiver's directory, route-b-restricted-hooks (ruled 2026-09-27):
     --restricted --tools <packet tools> --settings <the receiver's own hooks only>, dontAsk, --permission-prompts none,
     the packet's allowlist, --disallowedTools <packet deny: push, gh>, --add-dir <stage> (read the release bytes);
  4. the watcher stopped, the transcript located, and after_run_check.py run -> PASS / FAIL / INCONCLUSIVE.
Evidence goes to <--evidence>/<aget>/ (default: the evidence folder beside this script). A --baseline launch also writes
<packet stage>/baselines/<aget>.json. For a migration session the tool looks for the transcript under ~/.claude/projects/
and uses its own stream.jsonl when none is found. Receivers run concurrently (separate repositories).
A receiver's verdict file gates its phase-2 push (push_batch.py reads it); this script never pushes, and a live migration
launch exits 0 whatever the after-run verdicts are (a --baseline launch exits 1 unless every baseline is RECORDED).

Before any session starts (R4 C1, R1-S (ii)), every receiver is swept: each item it places or deletes, and each
write-set path that is not a glob, must pass copy_isolation's per-operation test (no link on the way, a regular file
with one name for a write, a regular file for a delete); `sessions` must be absent or a folder holding no symbolic
link; and the settings snapshot is taken for every receiver. Any refusal stops the run with exit 2 before any session.
Once sessions start, one receiver's failure never stops the others (R4 clause 3): an exception before its session
starts is recorded as REFUSED, one after as `session_started: true` (a record that claims nothing about the member's
bytes), and the launch then exits 1. These checks bound the window; they do not close it: a link made after the sweep
is followed by the session's own writes and is reported only after the run (a stated limit).

Usage: python3 scripts/migration_kit/launch_batch.py --packet <packet.json> [--only NAME ...] [--launch]
"""
import argparse
import concurrent.futures as cf
import datetime as dt
import hashlib
import json
import re
import signal
import os
import subprocess
import sys
import time
import uuid
from pathlib import Path

HERE = Path(__file__).resolve().parent
WATCHER = HERE / "watch_settings_rules.py"
CHECK = HERE / "after_run_check.py"
LIMIT_S = 3600
MAX_TURNS = "150"


def command(r, stage, sid, tools, deny):
    """route-b-restricted-hooks (ruled 2026-09-27; H1d D2): --restricted ignores user, project and local settings
    files; --settings supplies only the receiver's own hooks; --disallowedTools carries the packet's deny list (Bash calls starting git push or gh) whatever else loads."""
    return (["claude", "-p", "--session-id", sid, "--restricted", "--tools", tools, "--settings", r["settings"]["path"],
             "--permission-mode", "dontAsk", "--permission-prompts", "none", "--allowedTools", *r["allowlist"],
             "--disallowedTools", *deny, "--add-dir", stage, "--output-format", "stream-json", "--verbose",
             "--max-turns", MAX_TURNS, r["prompt"]])


SUMMARY = re.compile(r"^(?:=+ )?(\d+ (?:passed|failed|error|errors|skipped|deselected|xfailed|xpassed)[^\n]*?) in "
                     r"[\d.]+s")


def baseline_command(r, sid, tools, deny, baseline_cmd):
    """a2 phase 0: the receiver's own suite, before the approved list places anything. One allow rule (the suite command)."""
    return ["claude", "-p", "--session-id", sid, "--restricted", "--tools", "Bash", "--settings", r["settings"]["path"],
            "--permission-mode", "dontAsk", "--permission-prompts", "none", "--allowedTools", f"Bash({baseline_cmd})",
            "--disallowedTools", *deny, "--output-format", "stream-json", "--verbose", "--max-turns", "4",
            r["baseline_prompt"]]


def parse_baseline(stream_text, baseline_cmd, report=None, token=None, approved=()):
    """The output of the last call whose command equals the baseline command, from the session's stream: the last pytest
    summary line, and the failing ids of that call's run read from the kit's report (`report`, `token`; B185 finding 1)."""
    # B190 finding 1, with FWK-OVSR5's C2a8 advisory (1): the one reader and the one declared-call rule F uses
    # C2a10 (FWK-OVSR5's C2a9 advisory, agy): Bash calls only, as F reads them, and a later wrapped run refuses
    out, why, is_error = RBND.last_call_output(stream_text, lambda c: RBND.is_suite_run(c, baseline_cmd),
                                               bash_only=True, with_error=True,
                                               mentions=lambda c: RBND.mentions_suite(c, baseline_cmd))
    if out is None:        # C2a10 (B192 finding 2): a refusal is a record that is not complete, with its reason
        return {"summary": None, "failures": None, "failure_events": None, "complete": False,
                "reported_failing": 0, "failures_unknown": why}
    lines = out.splitlines()
    summary = next((m.group(1) for ln in reversed(lines) if (m := SUMMARY.search(ln))), None)
    # R2-T14 (S-168), B185 finding 1 (C2a7): the failing ids are pytest's own node ids from the kit's report, for the
    # one invocation this call's output names; the output text only selects it and cross-checks its counts. Any
    # shortfall (no report line, a truncated tool result, an unfinished invocation) leaves the ids not known
    # C2a11 (B194 finding 6): the baseline is the standing selection policy; its witness is recorded with it
    # F4 (B201 finding 2, weekly-train:R17): policy "baseline": a narrowed suite needs its selection's approval
    failures, unknown, events = RBND.report_failures(report, token, out, policy="baseline", approved=approved)
    selection = RBND.invocation_selection(report, token, out)
    reported = sum(int(n) for n, _ in re.findall(r"(\d+) (failed|errors?)\b", summary or ""))
    if is_error and not failures and not unknown:   # C2a10 (B192 finding 2): F's rule, for the producer too
        unknown = "the tool result is marked as an error, but its run names no failing test"
    return {"summary": summary, "failures": failures, "failure_events": events, "selection": selection,
            "complete": summary is not None and not unknown, "reported_failing": reported,
            "failures_unknown": unknown}


NO_PUSH = "no-push://disabled-by-launch-batch/"
PUSH_PREFIXES = ("git@", "ssh://", "https://", "http://", "file://", "/", "~")


# Carriage rows 70/72: variables whose names end in API_KEY are dropped inside the tool (no other token or secret is
# removed), not by an `env -u ... python3` prefix on the command line. The prefix kept suites from making paid API
# calls, but it also stopped the session-only allow rules in batch_rules.json (which match commands starting
# `python3 scripts/migration_kit/...`) from matching. The claude sessions authenticate by login, not by these keys.
NO_API_KEYS = re.compile(r"API_KEY$")


def session_env():
    """The environment for a batch session (B6 baseline, B8 migration, V3.7). A remote URL that starts with one of the
    seven PUSH_PREFIXES is rewritten for pushing to an unresolvable one through git's GIT_CONFIG_* variables, so nothing
    is written into the receiver. NOT covered: a remote with an explicit `pushurl` (git ignores pushInsteadOf for that
    remote), and any other URL form, for example git://... or user@host:... with a user other than git.
    one receiver 2026-09-29 17:48: its suite ran its own wind-down inside the B6 session, which committed and pushed 7
    commits to its remote. B10's push is push_batch.py's own process and is unaffected."""
    env = {k: v for k, v in os.environ.items() if k != "CLAUDECODE" and not k.startswith("GIT_CONFIG_")
           and not NO_API_KEYS.search(k)}
    for i, prefix in enumerate(PUSH_PREFIXES):
        env[f"GIT_CONFIG_KEY_{i}"] = f"url.{NO_PUSH}.pushInsteadOf"
        env[f"GIT_CONFIG_VALUE_{i}"] = prefix
    env["GIT_CONFIG_COUNT"] = str(len(PUSH_PREFIXES))
    # R1 (kit design pass, R1-T13): a push to a path the prefixes above cannot name (a relative path such as
    # ../remote.git) reached the remote. No transport is allowed in a session: git refuses every protocol, local
    # paths included. Stated limit: a member's test that clones, fetches or pushes, even to a local path, fails inside
    # its sessions (the baseline session and the migration session alike).
    # B151 finding 1: the value is the EMPTY list. "none" is a list naming one protocol, `none`, so a helper
    # `git-remote-none` on PATH still received the push. SESSION_ALLOW_PROTOCOL is the one value; ENV for code in
    # copies (a later stage) must reuse it.
    env["GIT_ALLOW_PROTOCOL"] = SESSION_ALLOW_PROTOCOL
    return env


SESSION_ALLOW_PROTOCOL = ""   # git's protocol whitelist, empty: git starts no transport, remote helpers included


def run_grouped(cmd, cwd, env, timeout):
    """Run a session in its own process group; send SIGKILL to that group afterwards and on timeout (a descendant that
    left the group is not reached; a failed kill is ignored)."""
    # Output goes to files, not pipes: a background child that inherits a pipe would hold it open and make the wait
    # last until the timeout. We wait for the MAIN process, then kill the group, then read.
    import tempfile
    with tempfile.TemporaryFile("w+") as fo, tempfile.TemporaryFile("w+") as fe:
        p = subprocess.Popen(cmd, cwd=cwd, env=env, text=True, start_new_session=True, stdout=fo, stderr=fe,
                             stdin=subprocess.DEVNULL)
        timed_out = False
        try:
            p.wait(timeout=timeout)
        except subprocess.TimeoutExpired:
            timed_out = True
        finally:                  # B152 finding 5: any exception (an interrupt included) still kills the group
            _kill_group(p.pid)
            p.wait()
        fo.seek(0)
        fe.seek(0)
        out, err = fo.read(), fe.read()
    if timed_out:
        raise subprocess.TimeoutExpired(cmd, timeout, output=out, stderr=err)
    return subprocess.CompletedProcess(cmd, p.returncode, out, err)


def _kill_group(pgid):
    try:
        os.killpg(pgid, signal.SIGKILL)
    except (ProcessLookupError, PermissionError):
        pass


def stop_watcher(watcher):
    """Terminate the settings watcher and wait up to 10 s, then kill it (B152 finding 5: called from a finally)."""
    watcher.terminate()
    try:
        watcher.wait(timeout=10)
    except subprocess.TimeoutExpired:
        watcher.kill()


def run_baseline(r, packet, evidence_root, stage, state=None):
    """Run one receiver's own suite in a headless session before anything is placed, and record the baseline."""
    ev = evidence_root / r["aget"]
    ev.mkdir(parents=True, exist_ok=True)
    # B143 finding 6, first act: an earlier baseline for this receiver stops counting (its record and the slot's
    # file are replaced), so a run that fails at any later step leaves no earlier RECORDED behind.
    # R2-T17: the run is recorded first, by the invoker, and the record is a result bound to it
    run_id = RBND.start_run("baseline", ev / "baseline_record.json", aget=r["aget"], recorded_by="invoker")
    (ev / "baseline_record.json").write_text(json.dumps({"aget": r["aget"], "verdict": "STARTED",
                                                         "state": "started, not finished"}, indent=2) + "\n")
    root, rel = baseline_target(r, packet)
    CI.contained_unlink(root, rel)
    status_before = CI.read_git(r["location"], "status", "--porcelain", text=True).stdout   # B166 finding 2
    sid = str(uuid.uuid4())
    env = copy_session_env(r["location"]) if r.get("_copy_root") else session_env()   # R1-T2 (c)
    # B185 finding 1 (C2a7): a fresh kit report for this run, in the kit's evidence folder; every pytest the session
    # starts writes its outcome records there (result_binding.report_env)
    report = ev / "baseline_pytest_report.jsonl"
    report.unlink(missing_ok=True)
    token = RBND.new_report(report)
    env = RBND.report_env(env, report, token)
    suite_cmd = r.get("suite_cmd") or packet["baseline_cmd"]   # per-receiver suite command, when ruled (row 11)
    cmd = baseline_command(r, sid, packet["tools"], packet["deny"], suite_cmd)
    started = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    if state is not None:
        state["session_started"] = True
    p = run_grouped(cmd, r["location"], env, LIMIT_S)
    (ev / "baseline_stream.jsonl").write_text(p.stdout)
    import after_run_check as ARC                       # F4 (B201 finding 2): the member's recorded approvals
    parsed = parse_baseline(p.stdout, suite_cmd, report, token, approved=ARC.policy_approvals(r["aget"]))
    head = CI.read_git(r["location"], "rev-parse", "HEAD", text=True).stdout.strip()
    status_after = CI.read_git(r["location"], "status", "--porcelain", text=True).stdout
    complete = bool(parsed and parsed["summary"] and parsed.get("complete"))   # R2-T14: not a truncated output
    doc = {"aget": r["aget"], "session_id": sid, "started": started, "head": head, "command": suite_cmd,
           "summary": (parsed or {}).get("summary"), "failures": (parsed or {}).get("failures"),
           "failure_events": (parsed or {}).get("failure_events"), "selection": (parsed or {}).get("selection"),
           "result_source": {"report": str(report), "report_sha256": file_sha(report),
                             "unknown": (parsed or {}).get("failures_unknown") if parsed else "no run of the command"},
           "output_complete": complete, "tree_unchanged": status_before == status_after and head == r["head"],
           "verdict": "RECORDED" if complete and status_before == status_after and head == r["head"]
           else "INCONCLUSIVE"}
    data = (json.dumps(doc, indent=2) + "\n").encode()
    CI.contained_write(root, rel, data)                 # R1 at the act, into the open slot (or the rehearsal copy)
    out = Path(root) / rel
    doc["sha256"] = hashlib.sha256(data).hexdigest()
    RBND.write_result("baseline", ev / "baseline_record.json", {**doc, "file": str(out),
                                                                "command_line": cmd[:-1] + ["<PROMPT>"]},
                      run_id, binding={"aget": r["aget"], "subject": head})
    return doc


COPY_BASELINE = ".git/aget_rehearsal_baseline.json"     # a rehearsal's baseline: inside its copy, never in the packet


def baseline_target(r, packet):
    """(root, relative path) where this receiver's baseline is written (R1 lifecycle, D-3 of design read 1): for a
    live launch, its slot PR/baselines/<aget>/baseline.json, which must still be open (a B8 launch seals it); for a
    rehearsal (--copy-root), inside the copy. Raises ContainmentRefused for a sealed slot or a packet with no root."""
    if r.get("_copy_root"):
        return r["location"], COPY_BASELINE
    root = packet.get("packet_root")
    if not root:
        raise CI.ContainmentRefused("the packet has no packet root; re-prepare it")
    slot = Path(root) / "baselines" / r["aget"]
    if not slot.is_dir() or slot.is_symlink() or not os.access(slot, os.W_OK):
        raise CI.ContainmentRefused(f"the baseline slot {slot} is sealed or absent; a baseline is taken before the "
                                    "receiver's launch, never after")
    return root, f"baselines/{r['aget']}/baseline.json"


def seal_baseline_slot(r, packet):
    """Seal the receiver's baseline slot before its B8 session (a-w on the file and the folder) and return the
    baseline's sha256, or None when there is none. The seal is made by the contained walk
    (copy_isolation.contained_seal; B148 finding 1): a slot or ancestor reached through a link, or a baseline file
    with a second name, raises ContainmentRefused before any mode changes, and the launch records REFUSED for this
    receiver with no session started. A slot that does not exist is not sealed (None)."""
    root = packet.get("packet_root")
    if not root:
        return None
    try:
        return CI.contained_seal(root, f"baselines/{r['aget']}", "baseline.json")
    except CI.ContainmentRefused as e:
        if str(e).endswith("does not exist"):
            return None
        raise


def file_sha(path):
    """Return the SHA-256 hex digest of the file's bytes, or 'absent' when it cannot be read."""
    try:
        return hashlib.sha256(Path(path).read_bytes()).hexdigest()
    except OSError:
        return "absent"


COPY_MARKER = "aget_rehearsal_copy.json"   # rehearse_v37.py writes it into <copy>/.git/ and sets the same name


sys.path.insert(0, str(HERE))
import copy_isolation as CI  # noqa: E402  (the one routine every copy the kit makes goes through)
import result_binding as RBND  # noqa: E402  (R2: the check's run is recorded by this invoker before the session)
import item_meaning as IM  # noqa: E402  (R3: every payload item's (op, kind) has a meaning row)
import release_target as R  # noqa: E402  (the release slug names the default work root)

# R1 clause 5 (E2g, R1-T1): the work root W. F's confirmation clones go into a fresh run folder under it, outside every
# repository; by default beside the packet under <release>/runs/ (R55 P5). AGET_MIGRATION_WORK overrides.
WORK_ROOT = Path(os.environ["AGET_MIGRATION_WORK"]) if os.environ.get("AGET_MIGRATION_WORK") else None


def copy_session_env(copy_root):
    """R1 ENV for a rehearsal session in a copy (V3.7; R1-T2 (c), clause 6(c)): session_env()'s drops and its empty
    transport list (SESSION_ALLOW_PROTOCOL), then copy_isolation.contained_env() with the copy's own hooks in force
    (hooks="copy"): git bounded by the folder holding the copy, no operator configuration, CLAUDE_PROJECT_DIR the
    copy. Checked under itself before it is returned (env_route_refusal(): the copy's push routes resolve only to the
    dead scheme, closed). A hook that runs is the copy's; LINKS, asked before the launch and again by the after-run
    check (--copy-run), requires every link under the copy to resolve inside its run folder. Raises
    ContainmentRefused."""
    env = CI.contained_env(Path(copy_root).parent, copy_root, SESSION_ALLOW_PROTOCOL, hooks="copy",
                           base=session_env())
    why = CI.hooks_path_refusal(copy_root, Path(copy_root).parent, env)   # clause 6(c): the hooks git will run
    if why:
        raise CI.ContainmentRefused(f"under the contained environment: {why}")
    return env


def copy_run_of(r):
    """A --copy-root receiver's run folder for LINKS: the copy, or with declared siblings the folder holding the copy
    and its siblings (as copy_root_refusal() asks it)."""
    return Path(r["location"]).parent if r.get("sibling_reads") else Path(r["location"])


_same_folder, folders_overlap, GIT_LOCATION_VARS = CI.same_folder, CI.folders_overlap, CI.GIT_LOCATION_VARS


def git_identity_refusal(folder, env=None):
    """copy_isolation.git_identity_refusal() with the environment a batch session gets (session_env() unless `env`
    is given): why git, run in this folder, would act on a repository or working tree other than the folder's own,
    or None (F-4, independent review 2026-10-02: a copy with its own .git folder whose `core.worktree` named the
    member made `git checkout` in the copy rewrite the member's file)."""
    return CI.git_identity_refusal(folder, session_env() if env is None else env)


def copy_root_refusal(copy_root, location, packet_sha, aget, siblings=()):
    """Why a --copy-root folder is refused, or None. Refused when the resolved folder is the packet receiver's own
    location, contains it, lies inside it or shares its .git folder (a symbolic link); when git_identity_refusal()
    refuses it (git run there would act on another working tree or git folder); and when
    <copy_root>/.git/COPY_MARKER is missing, unreadable, or does not name both this packet (`packet_sha`, the SHA-256
    of the --packet file's bytes) and this receiver. None establishes that the folder is apart from the packet's
    location, that git run in it names the folder as its working tree and <folder>/.git as its git folder and common
    folder, and that it carries the marker rehearse_v37.py writes into a copy it made for this packet and receiver.
    R1 LINKS, asked again at each launch: refused when a symbolic link in the copy leads outside the run's folder
    (the copy, or with declared `siblings` the folder holding the copy and its siblings).
    It does NOT establish that the folder is disposable, nor that the rehearsal tool wrote the marker: anyone able to
    write that file can forge it."""
    cr, loc = Path(copy_root).resolve(), Path(location).resolve()
    if folders_overlap(cr, loc):
        return (f"--copy-root {cr} is, contains or lies inside {aget}'s own folder {loc}; "
                "a rehearsal copy is a separate folder")
    if _same_folder(cr / ".git", loc / ".git"):
        return (f"--copy-root {cr} shares its .git folder with {aget}'s own folder {loc} (a linked .git); "
                "a rehearsal copy has its own")
    run = cr.parent if siblings else cr         # B162 finding 2: the whole run, siblings included, is walked
    why = CI.link_refusal(run, run) or git_identity_refusal(cr)
    if why:
        return f"--copy-root: {why}"
    marker = cr / ".git" / COPY_MARKER
    try:
        doc = json.loads(marker.read_text())
    except (OSError, ValueError):
        doc = None
    if not isinstance(doc, dict):
        return f"no readable custody marker at {marker}; rehearse_v37.py writes one into each copy it makes"
    if doc.get("packet_sha256") != packet_sha or doc.get("aget") != aget:
        return (f"the custody marker at {marker} names packet {str(doc.get('packet_sha256'))[:12]} and receiver "
                f"{doc.get('aget')!r}, not this packet ({packet_sha[:12]}) and {aget!r}; make the copy again with "
                "rehearse_v37.py")
    return None


class LaunchRulesDiffer(Exception):
    """D2 (R3, launch_batch.py:44): the packet's allowlist or write set is not the one its items give."""


def launch_rules_refusal(r, packet):
    """D2 (R3, DESIGN: "At launch, launch_batch.py:44 recomputes allowlist(r) and write_set(r) from the items and
    refuses if they differ from the packet"): None when the packet's session rules are exactly the ones preparation
    derives from this receiver's items, else why. An item with no meaning row, or a recompute that fails, refuses."""
    import importlib.util
    try:
        spec = importlib.util.spec_from_file_location("prepare_launch", HERE / "prepare_launch.py")
        PL = sys.modules.get("prepare_launch")
        if PL is None or getattr(PL, "__file__", None) != str(HERE / "prepare_launch.py"):
            PL = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(PL)
        if r.get("mode") == "track-skills":
            want_allow = PL.allowlist(r, True) + [f"Bash({c})" for c in PL.track_commands(r)]
            want_write = [PL.receipt_path(r), "sessions/*"]
        else:
            repair = str(packet.get("batch", "")).endswith("-repair")
            want_allow, want_write = PL.allowlist(r, repair), PL.write_set(r, repair)
    except Exception as e:                                  # noqa: BLE001 — unknown is never "equal"
        return f"the session rules cannot be recomputed from the items ({type(e).__name__}: {str(e)[:120]})"
    if want_allow != r.get("allowlist"):
        return "the packet's allowlist is not the one its items give; re-prepare the packet"
    if want_write != r.get("write_set"):
        return "the packet's write set is not the one its items give; re-prepare the packet"
    return None


def run_one(r, packet, evidence_root, state=None):
    """Launch one receiver's headless session under the settings watcher, run the after-run check, and return the launch record."""
    why = launch_rules_refusal(r, packet)   # D2 (R3): before anything is started for this receiver
    if why:
        raise LaunchRulesDiffer(why)
    ev = evidence_root / r["aget"]
    ev.mkdir(parents=True, exist_ok=True)
    sid = str(uuid.uuid4())
    # B143 finding 6, first act: the launch record says STARTED (no session yet), replacing any earlier one.
    (ev / "launch_record.json").write_text(json.dumps({"aget": r["aget"], "status": "STARTED"}, indent=2) + "\n")
    # R1 lifecycle (B8): a live launch seals this receiver's baseline slot before the session, and records its digest
    baseline_sha = None if r.get("_copy_root") else seal_baseline_slot(r, packet)
    settings_pre = file_sha(r["settings"]["path"])
    snap, watch_log = ev / "settings_snapshot_pre.json", ev / "settings_watch.jsonl"
    if not snap.is_file():                     # main() takes it in the pre-session sweep; a direct caller here
        take_snapshot(r, evidence_root)
    snapshot_sha = file_sha(snap)              # R2-T10 (S-330): the push gate reads only this snapshot's dirty paths
    # R2 clause 1, recorded by the invoker: before the session, the after-run check's run is started for this
    # receiver's verdict file, any earlier verdict is removed, and the launch record names the session and that run.
    verdict_file = ev / "after_run_check.json"
    check_run_id = RBND.start_run("after_run_check", verdict_file, aget=r["aget"], recorded_by="invoker")
    verdict_file.unlink(missing_ok=True)
    (ev / "launch_record.json").write_text(json.dumps({"aget": r["aget"], "session_id": sid,
                                                       "check_run_id": check_run_id, "status": "STARTED",
                                                       "baseline_sha256": baseline_sha,
                                                       "snapshot_sha256": snapshot_sha}, indent=2) + "\n")
    # R1-T2 (c): built and checked before the watcher starts, so a refused environment starts nothing
    env = copy_session_env(r["location"]) if r.get("_copy_root") else session_env()
    # B185 finding 1 (C2a7): F reads the session's suite runs from a fresh kit report, never from display text
    report = ev / "session_pytest_report.jsonl"
    report.unlink(missing_ok=True)
    token = RBND.new_report(report)
    env = RBND.report_env(env, report, token)
    watcher = subprocess.Popen([sys.executable, str(WATCHER), "--root", r["location"], "--log", str(watch_log),
                                "--interval", "0.5", "--heartbeat", "5", "--duration", str(LIMIT_S + 120)],
                               stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    try:                          # B153 finding 2: from the watcher's start, every step is inside the finally
        time.sleep(2)
        cmd = command(r, packet.get("packet_root") or packet["stage"], sid, packet["tools"], packet["deny"])
        started = dt.datetime.now().astimezone().isoformat(timespec="seconds")
        t0, hang = time.time(), False
        if state is not None:
            state["session_started"] = True
        try:
            p = run_grouped(cmd, r["location"], env, LIMIT_S)
            rc, out, err = p.returncode, p.stdout, p.stderr
        except subprocess.TimeoutExpired as exc:
            hang, rc = True, None
            out = exc.stdout.decode() if isinstance(exc.stdout, bytes) else (exc.stdout or "")
            err = exc.stderr.decode() if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        t1 = time.time()
        elapsed = round(t1 - t0, 1)
        time.sleep(3)
    finally:                      # B152 finding 5: the watcher is stopped on every exit, an interrupt included
        stop_watcher(watcher)
    (ev / "stream.jsonl").write_text(out)
    (ev / "stderr.txt").write_text(err[-4000:])
    hits = list((Path.home() / ".claude" / "projects").glob(f"*/{sid}.jsonl"))
    transcript = str(hits[0]) if hits else str(ev / "stream.jsonl")
    chk = subprocess.run([sys.executable, str(CHECK), "--aget", r["aget"], "--root", r["location"],
                          "--run-id", check_run_id, "--session-id", sid,
                          "--receipt", packet["apply_receipt"], "--snapshot-file", str(snap), "--watch-log",
                          str(watch_log), "--transcript", transcript, "--mode", "dontAsk",
                          "--packet", packet["_path"],
                          "--session-window", f"{t0:.3f}", f"{t1:.3f}",   # R2-T11: what the watch must cover
                          *([] if not baseline_sha else ["--baseline-slot-sha256", baseline_sha]),
                          # every launch here is route-b-restricted-hooks (command() above): gh#2802 ruling applies
                          "--route", "restricted-hooks", "--settings-file", r["settings"]["path"],
                          "--settings-sha256", r["settings"]["sha256"],
                          "--write-set", *r["write_set"], "--allow-bash", *r["allow_bash"],
                          "--allow-exact", *r.get("allow_exact", []), "--json", str(verdict_file),
                          # F (G3.6 row 12, B1): a migrating session's suite run against its B6 baseline record
                          *([] if r.get("mode") == "track-skills" else
                            ["--suite-cmd", r.get("suite_cmd") or "python3 -m pytest -q -p no:cacheprovider",
                             "--baseline-record", str(ev / "baseline_record.json"),
                             "--suite-report", str(report), "--suite-report-token", token,
                             # candidates re-run at the committed HEAD in a clean clone (sessions test before commit)
                             "--confirm-dir", str(WORK_ROOT if WORK_ROOT is not None else
                                                  Path(packet["_path"]).resolve().parent / R.SLUG / "runs"),
                             # R55 P5: beside the batch packet; R1-T1 still refuses a root inside a repository
                             "--sibling-read", *(r.get("sibling_reads") or [])]),
                          *(["--copy-run", str(copy_run_of(r))] if r.get("_copy_root") else [])],
                         capture_output=True, text=True)
    head = CI.read_git(r["location"], "rev-parse", "HEAD", text=True).stdout.strip()
    settings_post = file_sha(r["settings"]["path"])
    record = {"aget": r["aget"], "attempt": r["attempt"], "session_id": sid, "check_run_id": check_run_id,
              "status": "FINISHED", "baseline_sha256": baseline_sha, "snapshot_sha256": snapshot_sha,
              "suite_report": str(report), "suite_report_token": token,
              "prompt_sha256_packet": r.get("prompt_sha256_packet"),
              "prompt_sha256_launched": hashlib.sha256(r["prompt"].encode()).hexdigest(),
              "started": started, "elapsed_s": elapsed,
              "exit": rc, "hang": hang, "transcript": transcript, "transcript_found": bool(hits),
              "location": r["location"], "effective_grant": {
                  "route": packet.get("route"), "allowlist": r["allowlist"], "deny": packet["deny"],
                  "settings_file": r["settings"]["path"], "settings_sha256_packet": r["settings"]["sha256"],
                  "settings_sha256_pre": settings_pre, "settings_sha256_post": settings_post,
                  "settings_unchanged": settings_pre == settings_post == r["settings"]["sha256"],
                  "read_only_allowance": "harness built-in (H1b reading C1); judged by the after-run check C"},
              "head_before": r["head"], "head_after": head, "check_exit": chk.returncode,
              "check_summary": chk.stdout.strip()[-1500:], "command": cmd[:-1] + ["<PROMPT>"]}
    (ev / "launch_record.json").write_text(json.dumps(record, indent=2) + "\n")
    return record


def take_snapshot(r, evidence_root):
    """The pre-launch settings snapshot (after_run_check.py --snapshot) into <evidence>/<aget>/; raises
    subprocess.CalledProcessError when it fails."""
    ev = evidence_root / r["aget"]
    ev.mkdir(parents=True, exist_ok=True)
    subprocess.run([sys.executable, str(CHECK), "--aget", r["aget"], "--root", r["location"], "--snapshot",
                    str(ev / "settings_snapshot_pre.json"),
                    *(["--copy-run", str(copy_run_of(r))] if r.get("_copy_root") else [])],   # IGN: the session's env
                   check=True, capture_output=True)


def is_glob(path):
    """Whether a write-set entry is a glob pattern rather than one path."""
    return any(c in path for c in "*?[")


def launch_refusals(r):
    """R4 C1 and R1-S (ii) for one receiver, before any session: every reason, not only the first."""
    loc, out = Path(r["location"]), []
    for i in r.get("items", []):
        try:                                # B148 finding 2: an item with no meaning row is refused, never skipped
            IM.meaning(i)
        except IM.UnknownClassification as e:
            out.append(f"UNKNOWN CLASSIFICATION: {e}")
            continue
        if i.get("op") in ("write", "write-upstream"):
            out += CI.write_refusals(loc, [(i["path"], None if i.get("placed_by") else i.get("pre"))])
        elif i.get("op") == "delete" and os.path.lexists(loc / i["path"]):
            why = CI.destination_refusal(loc, i["path"], "delete")
            if why:
                out.append(f"UNSAFE PATH: {why}")
    for path in r.get("write_set", []):
        if not is_glob(path):
            why = CI.destination_refusal(loc, path, "write")
            if why:
                out.append(f"UNSAFE PATH: {why}")
    why = CI.destination_refusal(loc, "sessions", "mkdir")
    if why:
        out.append(f"UNSAFE PATH: {why}")
    elif (loc / "sessions").is_dir():
        for folder, dirs, files in os.walk(loc / "sessions"):
            for name in dirs + files:
                if os.path.islink(os.path.join(folder, name)):
                    out.append(f"UNSAFE PATH: {os.path.join(folder, name)} is a symbolic link under sessions/")
    return sorted(set(out))


def guarded(fn, r, *args, record=None, evidence_root=None):
    """Run fn(r, state, *args) for one receiver (R4 clause 3): an exception becomes that receiver's record. Before its
    session started: REFUSED. After: `session_started: true`, which is not a refusal and claims nothing about the
    member's bytes. With `record` (launch_record.json or baseline_record.json), that failure record is also written
    to <evidence>/<aget>/<record>, replacing any earlier one (B143 finding 6: durable, never only printed)."""
    state = {"session_started": False}
    try:
        return fn(r, *args, state=state)
    except Exception as e:                                  # noqa: BLE001 — R4 clause 4: no traceback
        why = f"{type(e).__name__}: {e}"
        if state["session_started"]:
            rec = {"aget": r.get("aget"), "session_started": True, "error": why}
        else:
            rec = {"aget": r.get("aget"), "result": "REFUSED", "why": why}
        if record and evidence_root is not None:
            try:
                d = Path(evidence_root) / str(r.get("aget"))
                d.mkdir(parents=True, exist_ok=True)
                (d / record).write_text(json.dumps(rec, indent=2) + "\n")
            except OSError as e2:
                rec["record_not_written"] = f"{type(e2).__name__}: {e2}"
        return rec


def _str_list(v):
    return isinstance(v, list) and all(isinstance(x, str) for x in v)


# C1 (B143 finding 5, B145, B148 finding 3): every packet field this tool reads, with the type it reads it as.
# REQUIRED fields are read on every route (the dry run included); OPTIONAL ones only on some, and must have their type
# when present. A field read by subscription on a route is never left to a later KeyError or TypeError.
PACKET_REQUIRED = {"claude_version": str, "tools": str, "deny": "str_list", "stage": str}
PACKET_OPTIONAL = {"packet_root": str, "stage_manifest": "str_map", "baseline_cmd": str, "batch": (str, int),
                   "route": (str, type(None)), "apply_receipt": (str, type(None))}
RECEIVER_REQUIRED = {"aget": str, "location": str, "head": str, "allowlist": "str_list", "write_set": "str_list",
                     "allow_bash": "str_list", "prompt": str, "attempt": str}
RECEIVER_OPTIONAL = {"allow_exact": "str_list", "sibling_reads": "str_list", "baseline_prompt": str, "suite_cmd": str}


def _typed(v, t):
    if t == "str_list":
        return _str_list(v)
    if t == "str_map":
        return isinstance(v, dict) and all(isinstance(k, str) and isinstance(x, str) for k, x in v.items())
    return isinstance(v, t) and not (t is int and isinstance(v, bool))


def _fields_refusal(doc, required, optional, what):
    for k, t in required.items():
        if k not in doc or not _typed(doc[k], t):
            return f"{what}: `{k}` is missing or not {t if isinstance(t, str) else getattr(t, '__name__', t)}"
    for k, t in optional.items():
        if k in doc and not _typed(doc[k], t):
            return f"{what}: `{k}` is not {t if isinstance(t, str) else getattr(t, '__name__', t)}"
    return None


def packet_refusal(packet, fields=True):
    """Why a parsed packet cannot be launched, or None (C1, before any receiver act; B143 finding 5). With `fields`
    (B148 finding 3) also every field the launch reads, PACKET_* and RECEIVER_* above. main() asks without `fields`
    first, so a packet with no typed authority still reads exit 6, then with `fields` before anything else reads it."""
    if not isinstance(packet, dict) or not isinstance(packet.get("receivers"), list):
        return "the packet is not an object with a `receivers` list"
    if fields:
        why = _fields_refusal(packet, PACKET_REQUIRED, PACKET_OPTIONAL, "the packet")
        if why:
            return why
    for i, r in enumerate(packet["receivers"]):
        if not isinstance(r, dict) or not all(isinstance(r.get(k), str) for k in ("aget", "location", "head")):
            return f"receiver {i} is not an object with string `aget`, `location` and `head`"
        why = CI.name_refusal(r["aget"], f"receiver {i}'s name")   # B162 finding 1: evidence folders are joined on it
        if why:
            return why
        if fields:
            why = _fields_refusal(r, RECEIVER_REQUIRED, RECEIVER_OPTIONAL, f"receiver {r['aget']}")
            if why:
                return why
        s = r.get("settings")
        if not isinstance(s, dict) or not isinstance(s.get("path"), str) or not isinstance(s.get("sha256"), str):
            return f"receiver {r['aget']}: `settings` is not an object with string `path` and `sha256` (B145)"
        items = r.get("items", [])
        if not isinstance(items, list) or not all(isinstance(i, dict) and isinstance(i.get("path"), str)
                                                  and isinstance(i.get("op"), str) for i in items):
            return f"receiver {r['aget']}: `items` is not a list of objects with string `path` and `op` (B145)"
        if any("kind" in i and not isinstance(i["kind"], str) for i in items):   # B151 finding 6
            return f"receiver {r['aget']}: an item's `kind` is not a string"
    if not isinstance(packet.get("claude_version"), str):
        return "the packet names no claude_version"
    return None


def route_refusal(packet, receivers, launch, baseline):
    """Why a field this route reads is missing, or None (B152 finding 2: C1 by route, after any command-line override
    and before any session). A migration launch reads `apply_receipt` (packet or --apply-receipt) when it builds the
    after-run check; a baseline launch reads `baseline_cmd` for each baseline taker that names no `suite_cmd`. The
    dry run reads neither."""
    if not launch:
        return None
    if baseline:
        bare = [r["aget"] for r in receivers if r.get("baseline_prompt") and not r.get("suite_cmd")]
        if bare and not packet.get("baseline_cmd"):
            return f"a baseline launch needs `baseline_cmd` for {bare} (no `suite_cmd` of their own)"
        return None
    if not packet.get("apply_receipt"):
        return "a migration launch needs `apply_receipt` (in the packet or by --apply-receipt)"
    return None


def failed_record(rec):
    """A record that is a refusal or an exception record (R4 clause 3)."""
    return rec.get("result") == "REFUSED" or "error" in rec


def cli_version_changes(prior_packets, current):
    """Carriage row 27 (SOP v1.27.0 finding, 2026-09-28): the CLI changed 2.1.283 -> 2.1.284 mid-wave and nothing said
    so, because the launch check compares versions only within one batch. Returns one report line naming every earlier
    batch prepared on a different CLI version than this one, or None. A report, not a stop: the per-batch E-3 check
    already stops a batch whose own packet disagrees."""
    diffs = []
    for pk in prior_packets:
        v = pk.get("claude_version")
        if v and v != current:
            diffs.append(f"{pk.get('batch') or pk.get('_path', '?')}: {v}")
    return ("NOTE: CLI version changed across batches: " + "; ".join(diffs) + f" -> this batch: {current}") if diffs else None


def _prior_packets(packet_path):
    """Earlier batches' launch packets: batch folders are siblings of this packet's folder."""
    here = Path(packet_path).resolve()
    out = []
    for f in sorted(here.parent.parent.glob("*/LAUNCH_PACKET_*.json")):
        if f.resolve() == here:
            continue
        try:
            out.append({**json.loads(f.read_text()), "_path": str(f)})
        except (OSError, ValueError):
            continue
    return out


def main(argv=None):
    """Command-line entry point: launch the packet's receivers for phase 1; a dry run unless --launch is given.

    Members are the packet's receivers filtered by --only (a --baseline launch also skips receivers without a baseline
    prompt): the write list is never read, so a receiver marked blocked or dropped there is still a member unless --only
    leaves it out. --launch without --copy-root needs a recorded principal line that batch_authority.check accepts (exit 6
    without it; a line queued mid-turn, whose prompt source the tool does not read, is accepted as well as a
    typed one); with --copy-root no authority check runs, and the folder is refused (exit 2, reason printed) unless
    copy_root_refusal returns None (the folder is not the receiver's own location, does not contain it, is not inside
    it and does not share its .git folder; git run there names the folder as its working tree and its .git folder as
    its git folder and common folder; and its .git folder holds the custody marker rehearse_v37.py writes, naming the
    digest of this --packet file's bytes and this receiver), `git remote` prints nothing there, and its HEAD
    equals the packet's. That establishes that the folder carries the rehearsal tool's marker for this packet; it does
    not prove a disposable copy, because anyone able to write the marker can forge it. A live launch returns 0
    whatever the after-run checks said (a --baseline launch returns 1 unless every baseline is RECORDED)."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--packet", type=Path, required=True)
    ap.add_argument("--only", nargs="*")
    ap.add_argument("--launch", action="store_true")
    ap.add_argument("--copy-root", type=Path, help="V3.7: run ONE receiver in this throwaway copy instead of its "
                    "repository (the copy must be at the packet's HEAD and have no push remote)")
    ap.add_argument("--evidence", type=Path, help="evidence folder (default scripts/migration_kit/evidence)")
    ap.add_argument("--baseline", action="store_true", help="a2 phase 0: record each receiver's own suite baseline "
                    "(before the approved list is applied); launches nothing else")
    ap.add_argument("--apply-receipt", type=Path, help="a2: the receipt of the approved list's apply (overrides the "
                    "packet's)")
    a = ap.parse_args(argv)
    try:                          # R4 C1 (B143 finding 5): an unusable packet stops the run before any act
        raw = a.packet.read_bytes()   # the bytes parsed are the bytes a --copy-root custody marker must name
        packet = json.loads(raw)
        bad = packet_refusal(packet, fields=False)
        if bad:
            raise ValueError(bad)
    except (OSError, ValueError) as e:
        print(f"STOPPED: the packet {a.packet} cannot be used ({type(e).__name__}: {e}); no session was started")
        return 2
    packet["_path"] = str(a.packet.resolve())
    if a.launch and not a.copy_root:
        # carriage row 62: a live launch (baseline or B8) WITHOUT --copy-root checks the batch's recorded
        # authority here through batch_authority.check. WITH --copy-root no authority check runs (the folder tests
        # below run instead), and the session allow rule covers both forms.
        # B151 finding 6: the field the authority check reads is checked before it is read
        if "batch" not in packet or not _typed(packet["batch"], PACKET_OPTIONAL["batch"]):
            print(f"STOPPED: the packet {a.packet} cannot be used (ValueError: a live launch needs `batch`, a string "
                  "or an integer, for its authority check); no session was started")
            return 2
        sys.path.insert(0, str(Path(__file__).resolve().parent))
        import batch_authority
        ok, why = batch_authority.check(packet["batch"], act="launch")
        if not ok:
            print(f"STOPPED: no typed authority for batch {packet['batch']}: {why}")
            return 6
        print(f"authority: {why}")
    bad = packet_refusal(packet)                 # C1, every field read below (B148 finding 3), before any act
    if bad:
        print(f"STOPPED: the packet {a.packet} cannot be used (ValueError: {bad}); no session was started")
        return 2
    # R1 lifecycle, the start of every launch (after the authority check): the stage equals its sealed manifest
    if not packet.get("packet_root") or not isinstance(packet.get("stage_manifest"), dict):
        print("STOPPED: the packet has no sealed packet root (an old or failed preparation); re-prepare it")
        return 2
    why = CI.sealed_refusal(Path(packet["packet_root"]) / "stage", packet["stage_manifest"])
    if why:
        print(f"STOPPED: the sealed stage changed: {why}; no session was started")
        return 2
    if a.apply_receipt:
        packet["apply_receipt"] = str(a.apply_receipt.resolve())
    receivers = [r for r in packet["receivers"] if not a.only or r["aget"] in a.only]
    if a.copy_root:
        if len(receivers) != 1:
            print("STOPPED: --copy-root runs exactly one receiver (use --only)")
            return 2
        why = copy_root_refusal(a.copy_root, receivers[0]["location"], hashlib.sha256(raw).hexdigest(),
                                receivers[0]["aget"], receivers[0].get("sibling_reads") or ())
        if why:
            print(f"STOPPED: {why}")
            return 2
        remotes = CI.read_git(a.copy_root, "remote", text=True).stdout
        # git remote does not list remotes defined by files under .git/remotes or .git/branches; git push uses them
        legacy = [p.name for p in CI.legacy_remote_files(a.copy_root / ".git")]
        if remotes.strip() or legacy:
            print(f"STOPPED: the copy has remotes ({remotes.split() + legacy}); a rehearsal copy must not be able "
                  "to push")
            return 2
        try:                         # R1-T2 (c): the session's environment, checked under itself, before any act
            copy_session_env(a.copy_root.resolve())
        except CI.ContainmentRefused as e:
            print(f"STOPPED: --copy-root: the session environment: {e}")
            return 2
        r0 = receivers[0]
        # R1 lifecycle (rehearsal): the baseline goes into the copy, never into the packet; the prompt's single
        # occurrence of the packet's baseline path is replaced by the copy's, and both prompts' digests are recorded.
        old = str(Path(packet.get("packet_root") or "") / "baselines" / r0["aget"] / "baseline.json")
        new = str(a.copy_root.resolve() / COPY_BASELINE)
        count = r0.get("prompt", "").count(old)
        if count > 1 or (count == 0 and r0.get("baseline_prompt") and r0.get("placed_by_apply")):
            print(f"STOPPED: the prompt names the packet's baseline path {count} times; exactly once is required")
            return 2
        receivers = [{**r0, "location": str(a.copy_root.resolve()), "_copy_root": True,
                      "prompt": r0.get("prompt", "").replace(old, new),
                      "prompt_sha256_packet": hashlib.sha256(r0.get("prompt", "").encode()).hexdigest()}]
    version = subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip()
    if version != packet["claude_version"]:
        print(f"STOPPED: claude is {version!r}, the packet was prepared on {packet['claude_version']!r} (E-3)")
        return 2
    note = cli_version_changes(_prior_packets(a.packet), version)
    if note:
        print(note)
    for r in receivers:
        ahead = CI.read_git(r["location"], "rev-parse", "HEAD", text=True).stdout.strip()
        if ahead != r["head"]:
            print(f"STOPPED: {r['aget']} HEAD moved ({ahead[:8]} != packet {r['head'][:8]}); re-prepare the packet")
            return 2
        if file_sha(r["settings"]["path"]) != r["settings"]["sha256"]:  # gh#2802 clause 1, before any launch
            print(f"STOPPED: {r['aget']} --settings file differs from the packet digest; re-prepare the packet")
            return 2
        why = launch_refusals(r)
        if why:
            print(f"STOPPED: {r['aget']}: " + "; ".join(why) + " (no session was started)")
            return 2
    # B152 finding 2: after every read-only check, before the first act (snapshot, baseline, session)
    why = route_refusal(packet, receivers, a.launch, a.baseline)
    if why:
        print(f"STOPPED: the packet {a.packet} cannot be used on this route (ValueError: {why}); no session was "
              "started")
        return 2
    if not a.launch:
        for r in receivers:
            print(f"DRY RUN {r['aget']}: cwd {r['location']}; {len(r['allowlist'])} allow rules; "
                  f"write set {len(r['write_set'])}; " +
                  " ".join(command(r, packet["stage"], "<sid>", packet["tools"], packet["deny"])[:14]) + " ...")
        return 0
    evidence_root = a.evidence or HERE / "evidence"
    if a.baseline:
        takers = [r for r in receivers if r.get("baseline_prompt")]
        with cf.ThreadPoolExecutor(max_workers=max(1, len(takers))) as pool:
            docs = list(pool.map(lambda r: guarded(run_baseline, r, packet, evidence_root, packet["stage"],
                                                   record="baseline_record.json", evidence_root=evidence_root), takers))
        for d in docs:
            if failed_record(d):
                print(f"{d['aget']:34s} baseline NOT RECORDED: {d.get('why') or d.get('error')}")
            else:
                print(f"{d['aget']:34s} baseline {d['verdict']}: {d['summary']} ({len(d['failures'] or [])} failing)")
        return 0 if docs and all(d.get("verdict") == "RECORDED" for d in docs) else 1
    for r in receivers:                    # R4 C1: every snapshot before the first session
        try:
            take_snapshot(r, evidence_root)
        except (subprocess.CalledProcessError, OSError) as e:
            print(f"STOPPED: {r['aget']}: the pre-launch settings snapshot failed ({type(e).__name__}); no session "
                  "was started")
            return 2
    with cf.ThreadPoolExecutor(max_workers=max(1, len(receivers))) as pool:
        records = list(pool.map(lambda r: guarded(run_one, r, packet, evidence_root, record="launch_record.json",
                                                  evidence_root=evidence_root), receivers))
    for rec in records:
        if failed_record(rec):
            print(f"{rec['aget']:34s} " + (f"REFUSED before its session: {rec['why']}" if rec.get("result") else
                                          f"session started, then {rec['error']}"))
            continue
        print(f"{rec['aget']:34s} exit {rec['exit']} {rec['elapsed_s']}s head {rec['head_before'][:8]}->{rec['head_after'][:8]} "
              f"check {({0: 'PASS', 1: 'FAIL', 3: 'INCONCLUSIVE'}).get(rec['check_exit'], rec['check_exit'])}")
    return 1 if any(failed_record(rec) for rec in records) else 0


if __name__ == "__main__":
    sys.exit(main())
