#!/usr/bin/env python3
"""R2, result binding: a value counts only when it is bound to this run, this member and this subject, and is on a
closed success list. One module; every producer and consumer of a fresh result calls it.

Run identity (R2 clause 1). Every fresh result has a run key, (step, output path), and a run log, `runs.jsonl` in the
output's folder. A run's first act, before it reads any input (and, where the operator runs the producer directly,
before argument parsing), appends a STARTED row naming a new run id; after it has written its result it appends a
FINISHED row with the sha256 of the bytes written. A result is CURRENT only when its `binding.run_id` is the last
STARTED row for its key, that run has a FINISHED row, and that row's digest equals the bytes the consumer read. So a
later run of the same key that started and did not finish (a usage error, a crash, a refusal) makes every earlier
result for that key unmet, whatever its inputs were; a result copied from another folder is not current there.

The one identity contract every consumer of an after-run verdict applies (design read 2, D-5): the verdict is the
current run for (after_run_check, <evidence>/<aget>/after_run_check.json), its binding names this member, and its
`session_id` equals the launch record's `session_id`. Equality with the launch record's `check_run_id` is NOT
required: a hand re-judge (after_run_check run directly, with --session-id) is a new run that supersedes the launch's
own check and is accepted on the same terms. `check_run_id` stays in the launch record for audit.

Stated limits (not closed here):
- An invocation that dies before its first act (an interpreter or import failure), or that cannot append to its run
  log, leaves no STARTED row: an earlier result for that key stays current. A run log that cannot be appended stops
  the producer with exit 2 before any other act; the operator reads that exit (SOP B3).
- Freshness is per key. A run that writes to another output path does not supersede this one.
- Runs recorded by the producer itself are a weaker custody than runs recorded by the invoker before the producer
  starts. The run log is a plain file: whoever can write it can forge a row. R2 binds results; it does not
  authenticate them.
"""
import argparse
import hashlib
import json
import os
import re
import uuid
from pathlib import Path

RUNS = "runs.jsonl"
NOT_CURRENT = "not the current run"

# The four receiver terminals (DEPLOYMENT_SPEC_v3.36.0.yaml:368-372) and the success lists (R2 clause 4).
TERMINALS = ("ACCEPTED", "BEHAVIOUR_VERIFIED", "REJECTED", "CANNOT-RUN")
SUCCESS = {
    "receiver_terminal": frozenset({"ACCEPTED", "BEHAVIOUR_VERIFIED"}),
    "after_run_verdict": frozenset({"PASS"}),
    "rehearsal_verdict": frozenset({"PASS"}),
    "baseline": frozenset({"RECORDED"}),
    "apply_entry": frozenset({"APPLIED"}),
}


class RunLogError(Exception):
    """The run log cannot be appended or read."""


def sha256(b):
    """sha256 hex of bytes."""
    return hashlib.sha256(b).hexdigest()


def key_path(out):
    """The output path as it is keyed in the run log: the folder resolved, the file name kept."""
    out = Path(out)
    return str(Path(os.path.realpath(out.parent)) / out.name)


def log_of(out):
    """The run log beside an output path."""
    return Path(out).parent / RUNS


def _append(out, row):
    try:
        Path(out).parent.mkdir(parents=True, exist_ok=True)
        fd = os.open(log_of(out), os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        try:
            os.write(fd, (json.dumps(row, sort_keys=True) + "\n").encode())
            os.fsync(fd)
        finally:
            os.close(fd)
    except OSError as e:
        raise RunLogError(f"the run log {log_of(out)} cannot be appended ({e})") from None


def start_run(step, out, *, aget=None, run_id=None, recorded_by="producer"):
    """Append a STARTED row for (step, out) and return its run id (a new uuid4 unless `run_id` is given by the
    invoker). Raises RunLogError."""
    run_id = run_id or str(uuid.uuid4())
    _append(out, {"event": "STARTED", "run_id": run_id, "step": step, "out": key_path(out), "aget": aget,
                  "recorded_by": recorded_by})
    return run_id


def finish_run(step, out, run_id, result_bytes, exit_code=0):
    """Append the FINISHED row for a run, naming the digest of the bytes it wrote. Raises RunLogError."""
    _append(out, {"event": "FINISHED", "run_id": run_id, "step": step, "out": key_path(out),
                  "result_sha256": sha256(result_bytes), "exit": exit_code})


def _rows(out):
    try:
        text = log_of(out).read_text()
    except FileNotFoundError:
        return []
    except (OSError, UnicodeDecodeError) as e:     # C2d (C2d pre-read 4): undecodable is unreadable, never a crash
        raise RunLogError(f"the run log {log_of(out)} cannot be read ({type(e).__name__})") from None
    rows = []
    for n, line in enumerate(text.splitlines(), 1):
        if not line.strip():
            continue
        try:
            row = json.loads(line)
        except ValueError:
            raise RunLogError(f"line {n} of {log_of(out)} does not parse; every key in it is unmet") from None
        if not isinstance(row, dict):
            raise RunLogError(f"line {n} of {log_of(out)} is not an object; every key in it is unmet")
        rows.append(row)
    return rows


def last_started(step, out):
    """The run id of the last STARTED row for (step, out), or None."""
    k = key_path(out)
    ids = [r.get("run_id") for r in _rows(out) if r.get("event") == "STARTED" and r.get("step") == step
           and r.get("out") == k]
    return ids[-1] if ids else None


def current(step, out, run_id, result_bytes):
    """None when `run_id` is the current run for (step, out) and finished with exactly these bytes; else why not
    (R2 clause 1 (a)-(c))."""
    if not run_id:
        return f"{NOT_CURRENT}: the result names no run id"
    if not isinstance(run_id, str):     # C2d (C2d pre-read 4): a malformed binding is unavailable, never a crash
        return f"{NOT_CURRENT}: the result's run id is not a string"
    try:
        rows = _rows(out)
    except RunLogError as e:
        return f"{NOT_CURRENT}: {e}"
    k = key_path(out)
    started = [(i, r.get("run_id")) for i, r in enumerate(rows) if r.get("event") == "STARTED"
               and r.get("step") == step and r.get("out") == k]
    if not started:
        return f"{NOT_CURRENT}: no run of {step} is recorded for {k}"
    last, last_id = started[-1]
    if last_id != run_id:
        return f"{NOT_CURRENT}: a later run of {step} ({str(last_id)[:8]}) started for {k} after run {run_id[:8]}"
    # C2c (FWK-OVSR7's C2c pre-read H1, H2, M2): the run's FINISHED row is of this step, follows the run's latest
    # STARTED row (a reused id that started again and never finished is not finished), and is the only one (a second
    # write for a finished run is a late write, never a replacement result)
    fin = _finished_after(rows, step, k, run_id, last)
    if not fin:
        return f"{NOT_CURRENT}: run {run_id[:8]} of {step} did not finish"
    if len(fin) != 1:
        return f"{NOT_CURRENT}: run {run_id[:8]} of {step} has {len(fin)} FINISHED rows (a result written after it finished)"
    if fin[0].get("result_sha256") != sha256(result_bytes):
        return f"{NOT_CURRENT}: the bytes read are not the bytes run {run_id[:8]} wrote"
    return None


def _finished_after(rows, step, k, run_id, start):
    """The FINISHED rows of (step, k, run_id) after row index `start` (the run's latest STARTED row)."""
    return [r for r in rows[start + 1:] if r.get("event") == "FINISHED" and r.get("run_id") == run_id
            and r.get("step") == step and r.get("out") == k]


def write_result(step, out, doc, run_id, exit_code=0, binding=None):
    """Write a JSON result with its `binding` (run id plus `binding`) atomically, then the FINISHED row. Returns the
    bytes written. Raises OSError or RunLogError."""
    doc = {**doc, "binding": {**(binding or {}), "run_id": run_id}}
    data = (json.dumps(doc, indent=2) + "\n").encode()
    # C2c (FWK-OVSR7's C2c pre-read H1): a run writes its result once; a write for a run that is not this step's
    # latest started run, or that already finished, is refused before the result file is touched
    rows, k = _rows(out), key_path(out)
    started = [i for i, r in enumerate(rows) if r.get("event") == "STARTED" and r.get("step") == step
               and r.get("out") == k]
    if not started or rows[started[-1]].get("run_id") != run_id:
        # C2d (FWK-OVSR8's C2d pre-read 3): only this step's latest started run writes; a superseded run never
        # replaces the newer run's result
        raise RunLogError(f"run {str(run_id)[:8]} of {step} is not the latest started run for {k}; its result is "
                          f"not written")
    if _finished_after(rows, step, k, run_id, started[-1]):
        raise RunLogError(f"run {str(run_id)[:8]} of {step} already finished; a second result is not written")
    atomic_write(out, data)
    finish_run(step, out, run_id, data, exit_code)
    return data


def read_current(step, out):
    """(doc, None) when the JSON result at `out` is current for `step`; (None, why) otherwise."""
    try:
        data = Path(out).read_bytes()
        doc = json.loads(data)
    except (OSError, ValueError) as e:
        return None, f"{out} cannot be read ({type(e).__name__})"
    if not isinstance(doc, dict):
        return None, f"{out} is not a result object"
    if doc.get("binding") is not None and not isinstance(doc["binding"], dict):   # C2d (C2d pre-read 4)
        return None, f"{NOT_CURRENT}: the result's binding is not an object"
    why = current(step, out, (doc.get("binding") or {}).get("run_id"), data)
    return (None, why) if why else (doc, None)


def _is_option(tok):
    """Whether argparse reads `tok` as an option string rather than a value (D3, B200 finding 2). Asked of argparse's
    own classifier (`ArgumentParser._parse_optional`, the method its parser uses for this decision) on a parser with
    no options of its own, as the kit's producers have none that look like negative numbers: a leading `-` is an
    option unless the token is `-` alone, looks like a negative number, or holds a space."""
    return _OPTION_PROBE._parse_optional(tok) is not None


_OPTION_PROBE = argparse.ArgumentParser(add_help=False)


def prescan(argv, flag):
    """The value of `flag` in an argument list, read before argument parsing (a usage error must still invalidate the
    earlier result), or None. Accepts `--flag value` and `--flag=value`.
    C2a15 (B198 finding 4): argparse's own reading, so the slot invalidated first is the slot the run writes: the LAST
    occurrence wins, an unambiguous abbreviation (`--evid`, argparse's allow_abbrev) counts as the flag, and nothing
    after a bare `--` is an option."""
    found = None
    i = 0
    while i < len(argv):
        x = argv[i]
        if x == "--":
            break
        name, eq, val = x.partition("=")
        if name.startswith("--") and len(name) > 2 and flag.startswith(name):
            if eq:
                found = val
            elif i + 1 < len(argv) and not _is_option(argv[i + 1]):
                # D2 (FWK-OVSR9's D2 pre-read 2): a following option is not this flag's value (argparse refuses the
                # flag); the earlier value stays the one invalidated, never a path named `--packet`. D3 (B200
                # finding 2): "an option" is argparse's own reading, so `-1`, `-.5` and a word holding a space are values
                found = argv[i + 1]
                i += 1
        i += 1
    return found


def verdict_bound_to_launch(verdict_doc, launch, aget):
    """The one identity contract for an after-run verdict (D-5), the run-currency half excepted (read_current does
    that): the binding names this member and the launch record's session. None when it holds, else why."""
    b = verdict_doc.get("binding") or {}
    if b.get("aget") != aget:
        return f"the verdict names member {b.get('aget')!r}, not {aget!r}"
    if not launch.get("session_id") or b.get("session_id") != launch.get("session_id"):
        return (f"the verdict judges session {str(b.get('session_id'))[:8]}, the launch record names "
                f"{str(launch.get('session_id'))[:8]}")
    return None


# --- the receipt grammar (R2 clause 4, receiver terminal; design read 1, D-5) ------------------------------------

HEADING = re.compile(r"^## Attempt ([A-Za-z0-9._-]+)(?: \([^)]*\))?\s*$")
TERMINAL_LABEL = re.compile(r"(?i)^terminal(?:\s+[a-z]+)?\s*[:=|–—-]")
TERMINAL_LINE = re.compile(r"^Terminal: (\S+)\s*$")


def _normalized(line):
    s = line.replace("*", "").replace("`", "")
    return re.sub(r"^[\s#>|+\-]*(?:\d+[.)]\s*)?", "", s).strip()


def _terminal_shaped(line):
    n = _normalized(line)
    return bool(TERMINAL_LABEL.match(n)) or n.upper() in {*TERMINALS, "UNKNOWN"}


def receipt_terminal(data, attempt):
    """(value, None) or (None, reason): the single terminal of the authoritative attempt section of a receipt.
    The section starts at the one heading `## Attempt <attempt>` and runs to the end of the file; no attempt heading
    may follow it; earlier text is history and is not read. In the section there must be exactly one terminal-shaped
    line, it must be exactly `Terminal: <V>` with V in TERMINALS, and it must be the section's last non-blank line.
    Success is a separate test: V in SUCCESS["receiver_terminal"]."""
    if isinstance(data, bytes):
        try:
            text = data.decode("utf-8")
        except UnicodeDecodeError:
            return None, "the receipt is not UTF-8"
    else:
        text = data
    if not attempt:
        return None, "no expected attempt is named"
    lines = text.splitlines()
    heads = []
    for i, ln in enumerate(lines):
        m = HEADING.match(ln)
        if m:
            heads.append((i, m.group(1)))
        elif ln.lstrip().startswith("#") and "attempt" in ln.lower():
            return None, f"malformed attempt heading at line {i + 1}: {ln.strip()[:60]}"
    mine = [i for i, a in heads if a == attempt]
    if not mine:
        return None, f"no section `## Attempt {attempt}`"
    if len(mine) > 1:
        return None, f"`## Attempt {attempt}` appears {len(mine)} times"
    if any(i > mine[0] for i, _ in heads):
        return None, f"a later attempt section follows `## Attempt {attempt}`"
    section = lines[mine[0] + 1:]
    shaped = [ln for ln in section if _terminal_shaped(ln)]
    if len(shaped) != 1:
        return None, f"{len(shaped)} terminal-shaped lines in the attempt section (exactly one is required)"
    m = TERMINAL_LINE.match(shaped[0].rstrip())
    if not m or shaped[0].rstrip() != f"Terminal: {m.group(1)}":
        return None, f"the terminal line is not exactly `Terminal: <V>`: {shaped[0].strip()[:60]}"
    if m.group(1) not in TERMINALS:
        return None, f"unsupported terminal value {m.group(1)!r}"
    last = [ln for ln in section if ln.strip()][-1]
    if last is not shaped[0] and last.rstrip() != shaped[0].rstrip():
        return None, "the terminal line is not the section's last non-blank line"
    return m.group(1), None


def producer_start(step, out, not_finished):
    """A producer's first act, before argument parsing (R2 clause 1, recorded by the producer): append STARTED for
    (step, out) and write `not_finished` there. Returns (run_id, None), or (None, reason) when the run cannot be
    recorded (the caller exits 2 having done nothing else). With no output path found, (None, None): the argument
    parser then refuses, and an earlier result stays current (a stated limit)."""
    if out is None:  # D2 (C2e pre-read 2): an empty value is a value (argparse takes `--x=`), never absent
        return None, None
    try:
        rid = start_run(step, out)
        Path(out).write_text(json.dumps(not_finished, indent=2) + "\n")
        return rid, None
    except (RunLogError, OSError) as e:
        return None, f"REFUSED: this run cannot be recorded ({e}); nothing else was done"


_SUMMARY_HEADER = re.compile(r"^=+ short test summary info =+$")
_COUNT_LINE = re.compile(r"^(?:=+ )?\d+ (?:passed|failed|errors?|skipped|deselected|xfailed|xpassed|warnings?)\b.* in "
                         r"[\d.]+s\b")
_KIND = re.compile(r"^(FAILED|ERROR) (.*)$")
# A line the kit's parallel runner prints for a file whose failing ids it could not read: never an id (B182 finding 1)
IDS_UNKNOWN = "IDS-UNKNOWN "


def _one_id(rest):
    """The id at the front of a summary line's remainder, or None when its end is not unique (B180, B182 finding 1).
    pytest prints `<id>` or `<id> - <message>`, and a node id may itself hold ` - ` (a parameter, or a name given
    through `globals()`), so text alone fixes the end only when the line holds at most one ` - `: none, the whole line
    is the id; one, the id ends there; more, the end is not unique. An empty id is not an id, and a parametrized
    name (a `[` after the last `::`) that does not end with its `]` is a cut id, not an id."""
    cuts = rest.count(" - ")
    one = rest if cuts == 0 else rest.split(" - ", 1)[0] if cuts == 1 else None
    if not one or one.strip() != one or ("[" in one.rpartition("::")[2] and not one.endswith("]")):
        return None
    return one


def summary_section(text):
    """pytest's own short test summary in `text`, as (FAILED/ERROR lines, failed count, error count, reason or None).
    B182 finding 1: a run's output must hold exactly ONE pytest count line and at most ONE `short test summary info`
    header, before it; a second of either (printed by a test, by an `atexit` callback after pytest's own summary, or
    by a newline in an unescaped id) leaves the section not known, never resolved to the last or the first."""
    lines = (text or "").splitlines()
    heads = [i for i, ln in enumerate(lines) if _SUMMARY_HEADER.match(ln.strip())]
    counts = [i for i, ln in enumerate(lines) if _COUNT_LINE.match(ln.strip())]
    if len(counts) != 1:
        return [], 0, 0, f"{len(counts)} pytest count lines in the output, not one"
    if len(heads) > 1:
        return [], 0, 0, f"{len(heads)} short test summary sections in the output, not one"
    if heads and heads[0] > counts[0]:
        return [], 0, 0, "the short test summary comes after the count line"
    if any(ln.startswith(IDS_UNKNOWN) for ln in lines[:counts[0]]):   # C2a7 (FWK-OVSR5's C2a5 advisory (1)): read
        return [], 0, 0, "the kit's parallel runner could not read every file's failing ids"   # before the 0 return
    tally = lines[counts[0]].strip()
    failed = sum(int(n) for n in re.findall(r"(\d+) (?:\w+ )?failed\b", tally))   # `subtests failed` included
    errors = sum(int(n) for n in re.findall(r"(\d+) errors?\b", tally))
    if not failed and not errors:
        return [], 0, 0, None
    if not heads:
        return [], failed, errors, f"{failed} failed and {errors} error(s) reported, but no short test summary lists them"
    section = lines[heads[0] + 1:counts[0]]
    if any(ln.startswith(IDS_UNKNOWN) for ln in section):
        return [], failed, errors, "the kit's parallel runner could not read every file's failing ids"
    return [ln for ln in section if _KIND.match(ln)], failed, errors, None


def failing_ids(text):
    """The failing test ids of a pytest run, read only from pytest's own short test summary (summary_section), as
    (sorted distinct ids, None), or (ids read, reason) when the ids are not all known. The one reader for the baseline
    producer, F, the confirmation run, B8a and the repair rehearsal (census test); the parallel runner applies it to
    each file's output.
    - Each id is read whole and its end must be unique (_one_id); an ambiguous or empty id is a reason.
    - `FAILED` lines must equal the count line's failed count and `ERROR` lines its error count, each separately (a
      FAILED line never stands in for a missing ERROR id; events, so one test's setup and teardown errors are two).
    - No failure reported: no ids. Failures reported with no summary, more than one summary or count line: a reason."""
    found, failed, errors, why = summary_section(text)
    if why:
        return [], why
    ids, seen, bad = set(), {"FAILED": 0, "ERROR": 0}, 0
    for ln in found:
        kind, rest = _KIND.match(ln).groups()
        seen[kind] += 1
        one = _one_id(rest)
        if one is None:
            bad += 1
        else:
            ids.add(one)
    why = []
    if bad:
        why.append(f"{bad} failing id(s) whose end is not unique")
    if seen["FAILED"] != failed:
        why.append(f"{seen['FAILED']} FAILED line(s) for {failed} failed")
    if seen["ERROR"] != errors:
        why.append(f"{seen['ERROR']} ERROR line(s) for {errors} error(s)")
    return sorted(ids), "; ".join(why) or None


# --- the structured result source (B185 finding 1, C2a7) ---------------------------------------------------------
# pytest's terminal summary cannot fix where a node id ends (an id may hold ` - `, and pytest omits a message that does
# not fit), so the failing ids every consumer compares come from the kit's pytest plugin (pytest_plugin/
# aget_kit_report.py): pytest's own reports as JSON lines, between a `start` and a `finish` record per invocation.
# The run's output text only SELECTS the invocation (its one `aget-kit-report:` line) and is a cross-check (its count
# line must equal the report's tally); it never supplies an id.

PLUGIN_DIR = Path(__file__).resolve().parent / "pytest_plugin"
PLUGIN = "aget_kit_report"
REPORT_MARK = "aget-kit-report: "
_MARK_LINE = re.compile(r"aget-kit-report: (pytest|runner) ([0-9a-f]{32})")   # fullmatch only (B190 finding 3)
_PASSING_EXITS = (0, 1, 5)           # pytest: all passed, some failed, nothing collected; 2-4 interrupted/internal/usage


def new_report(path):
    """Create an empty report file at `path` for one run (it must not exist: a run's report is fresh, never an earlier
    run's), and return the run's token (a new uuid4). Raises OSError."""
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL | getattr(os, "O_NOFOLLOW", 0), 0o600)
    os.close(fd)
    return uuid.uuid4().hex


def report_env(env, path, token):
    """`env` with the kit's plugin loaded by every pytest started under it: PYTEST_ADDOPTS gains `-p aget_kit_report`,
    PYTHONPATH gains only the plugin's folder (never the kit's own modules), and the report path, the token and the
    member's own values of those two variables are carried for the plugin, which puts the member's values back before
    any member code runs."""
    env = dict(env)
    orig = {k: env.get(k) for k in ("PYTEST_ADDOPTS", "PYTHONPATH")}
    env["PYTEST_ADDOPTS"] = f"-p {PLUGIN}" + (f" {orig['PYTEST_ADDOPTS']}" if orig["PYTEST_ADDOPTS"] else "")
    env["PYTHONPATH"] = str(PLUGIN_DIR) + (os.pathsep + orig["PYTHONPATH"] if orig["PYTHONPATH"] else "")
    env.update(AGET_KIT_REPORT=str(path), AGET_KIT_REPORT_TOKEN=token, AGET_KIT_ORIG=json.dumps(orig))
    return env


_HEX32 = re.compile(r"[0-9a-f]{32}")      # B190 finding 3: used with fullmatch only (`$` admits a final LF)
_PHASES = ("collect", "setup", "call", "teardown")
_OUTCOMES = ("passed", "failed", "skipped")            # pytest's report outcomes (TestReport/CollectReport)


def _int(v, low=0):
    return isinstance(v, int) and not isinstance(v, bool) and v >= low


def _hex(v):
    return isinstance(v, str) and bool(_HEX32.fullmatch(v))


def _record_fault(row):
    """None when `row` is a well-formed report record (B188 finding 1: a closed, typed grammar), else what is wrong."""
    rec = row.get("rec")
    if rec in ("start", "event", "finish") and not _hex(row.get("inv")):
        return "an invocation id that is not 32 hex digits"
    if rec == "start":
        ok = (_int(row.get("pid"), 1) and isinstance(row.get("args"), list)
              and all(isinstance(a, str) for a in row["args"]) and isinstance(row.get("dir"), str)
              and isinstance(row.get("lf"), bool))
        return None if ok else "a start record without (pid, args, dir, lf)"
    if rec == "event":
        ok = (isinstance(row.get("nodeid"), str) and row["nodeid"] != "" and row.get("when") in _PHASES
              and row.get("outcome") in _OUTCOMES and (row["when"] != "collect" or row["outcome"] == "failed"))
        return None if ok else "an event that is not (non-empty nodeid, pytest phase, pytest outcome)"
    if rec == "finish":
        ok = (_int(row.get("exit")) and _int(row.get("events")) and _int(row.get("collected")) and _int(row.get("ran"))
              and isinstance(row.get("deselected"), list)
              and all(isinstance(x, str) and x for x in row["deselected"])
              and isinstance(row.get("narrowed"), list) and all(isinstance(x, str) and x for x in row["narrowed"])
              and _int(row.get("dropped"))
              and isinstance(row.get("suppressed"), list) and all(isinstance(x, str) and x for x in row["suppressed"])
              and isinstance(row.get("selection"), dict)
              and isinstance(row.get("census"), list) and all(isinstance(x, str) and x for x in row["census"])
              and all(isinstance(k, str) and isinstance(v, list) and all(isinstance(x, str) for x in v)
                      for k, v in row["selection"].items()))
        return None if ok else ("a finish record without integer (exit, events, collected, ran, dropped), "
                                "deselected ids and narrowing inputs")
    if rec == "runner":
        ok = (_hex(row.get("run")) and _int(row.get("files")) and isinstance(row.get("children"), list)
              and all(_hex(c) for c in row["children"]) and isinstance(row.get("complete"), bool))
        return None if ok else "a runner record without (run, files, children, complete)"
    return f"an unknown record kind {str(rec)[:20]!r}"


def open_report(path, flags):
    """An open descriptor on the report at `path`, never through a link and never blocking (B188 finding 2: a FIFO
    is refused, not waited on), and only when it is a regular file; raises OSError otherwise."""
    import stat
    fd = os.open(path, flags | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    try:
        if not stat.S_ISREG(os.fstat(fd).st_mode):
            raise OSError(f"{path} is not a regular file")
    except BaseException:
        os.close(fd)
        raise
    return fd


def _no_duplicate_keys(pairs):
    """C2a9: a report object with a key twice is malformed (json keeps the last silently)."""
    keys = [k for k, _ in pairs]
    if len(keys) != len(set(keys)):
        raise ValueError("a key appears twice")
    return dict(pairs)


def _no_constant(name):
    """C2a9: NaN and Infinity are not JSON; the report grammar has no place for them."""
    raise ValueError(f"{name} is not a JSON value")


def _report_rows(path, token):
    try:
        fd = open_report(path, os.O_RDONLY)
    except OSError as e:
        return None, f"the run's report {path} cannot be opened as a regular file ({e})"
    with os.fdopen(fd, "rb") as fh:
        data = fh.read()
    try:
        text = data.decode("utf-8")                    # B188 finding 1: strict; a replaced byte would invent an id
    except UnicodeDecodeError as e:
        return None, f"the run's report is not UTF-8 (byte {e.start})"
    rows = []
    for n, line in enumerate(text.split("\n"), 1):
        if not line:
            continue
        try:
            row = json.loads(line, object_pairs_hook=_no_duplicate_keys, parse_constant=_no_constant)
        except ValueError:
            return None, f"line {n} of the run's report does not parse"
        if not isinstance(row, dict) or row.get("token") != token:
            return None, f"line {n} of the run's report is not a record of this run"
        fault = _record_fault(row)
        if fault:
            return None, f"line {n} of the run's report holds {fault}"
        rows.append(row)
    return rows, None


def _declared_deselections(args):
    """The node-id prefixes an invocation's own command line deselects (`--deselect X`, `--deselect=X`), as a tuple."""
    out = []
    for i, a in enumerate(args):
        if a == "--deselect" and i + 1 < len(args):
            out.append(args[i + 1])
        elif a.startswith("--deselect="):
            out.append(a.split("=", 1)[1])
    return tuple(x for x in out if x)


# C2c (FWK-OVSR7's C2c pre-read M1): the plugin's whole selection witness (aget_kit_report._selection_witness). A
# witness, the run's or the baseline's, with any other key set is not one: it proves no selection
WITNESS_KEYS = frozenset({"roots", "ignored", "python_files", "python_classes", "python_functions", "testpaths",
                          "blocked", "plugins", "producers", "autoload"})
# C2c (FWK-OVSR7's C2c pre-read H3): a parallel run's standing policy is each child's whole witness, by its one root
PER_FILE = "per_file"


def _invocation(rows, inv, child=False, policy=None, approved=()):
    """(events, None) for one complete pytest invocation in the report, else (None, why)."""
    mine = [r for r in rows if r.get("inv") == inv]
    starts = [r for r in mine if r.get("rec") == "start"]
    fins = [r for r in mine if r.get("rec") == "finish"]
    events = [r for r in mine if r.get("rec") == "event"]
    if len(starts) != 1 or len(fins) != 1:
        return None, f"invocation {inv[:8]} has {len(starts)} start and {len(fins)} finish record(s), not one each"
    if fins[0].get("exit") not in _PASSING_EXITS:
        return None, f"invocation {inv[:8]} ended with pytest exit {fins[0].get('exit')!r} (interrupted or failed)"
    # C2a9 (FWK-OVSR5's C2a8 advisory): exit 5 (nothing collected) is a complete result only for one file of the
    # kit's parallel runner; a whole suite that collected nothing is not a run of it. Exit 1 must have a failing
    # event: a failure pytest counts outside any test (`--cov-fail-under`, `-W error` at session end) has no id
    failing = sum(1 for e in events if e.get("outcome") == "failed")
    if fins[0]["exit"] == 5 and not child:
        return None, f"invocation {inv[:8]} collected no test (pytest exit 5)"
    if fins[0]["exit"] == 1 and not failing:
        return None, f"invocation {inv[:8]} exited 1 with no failing test: a failure no test id names"
    if fins[0]["exit"] == 0 and failing:
        return None, f"invocation {inv[:8]} exited 0 with {failing} failing event(s)"
    if fins[0].get("events") != len(events):
        return None, f"invocation {inv[:8]} wrote {fins[0].get('events')!r} event(s); the report holds {len(events)}"
    # C2a8 (FWK-OVSR5's C2a7 advisory (2)): every collected test was reported (a `-x`/`--maxfail` stop leaves the rest
    # unrun, so a new failure among them would be unseen); `ran` is the plugin's count, re-derived here from the events
    # B190 finding 2: a last-failed run, or a test deselected by anything but the invocation's own `--deselect`
    # arguments (the kit's declared exclusions: B8a's CI list, the parallel runner's --deselect-file), is a subset
    if starts[0]["lf"]:
        return None, f"invocation {inv[:8]} ran with --lf (last failed): a subset of the suite"
    # C2a10 (B192 finding 3): a declared exclusion is an identity. A declared id covers itself only (pytest's own
    # `--deselect` also drops every id it prefixes: `…::t` takes `…::t2`); a declared PATH (no `::`) is a scope the
    # operator wrote and covers the ids under it
    declared = _declared_deselections(starts[0]["args"])
    extra = [x for x in fins[0]["deselected"]
             if x not in declared and not any("::" not in d and (x.startswith(d.rstrip("/") + "::")
                                                                 or x.startswith(d.rstrip("/") + "/"))
                                              for d in declared)]
    if fins[0]["suppressed"]:       # C2a11 (B194 finding 6): never a standing policy
        return None, (f"invocation {inv[:8]} left {len(fins[0]['suppressed'])} test candidate(s) uncreated by a "
                      f"collection hook, e.g. {fins[0]['suppressed'][0][:80]}")
    if fins[0]["census"]:           # C2a12 (B195 finding 1): the independent census; never a standing policy
        return None, (f"invocation {inv[:8]}: {len(fins[0]['census'])} declared test candidate(s) in the suite's files "
                      f"never became a collected item (or the census is unavailable), e.g. {fins[0]['census'][0][:100]}")
    # C2a11 (B194 finding 6, REVW9's accepted route): a narrowed population counts only as a standing policy: when
    # the caller records the policy (the baseline, the confirmation run: policy "record"), or when the run's whole
    # selection witness equals the baseline's (`policy` a dict). Anything else, a missing witness included, refuses
    # C2a12 (FWK-OVSR6's C2a11 pre-read 3): against a baseline that holds a witness, the whole witness is compared
    # whether or not the run reads as narrowed (plugin autoload switched off, a changed plugin set, an empty witness)
    if set(fins[0]["selection"]) != WITNESS_KEYS:  # C2c (C2c pre-read M1)
        return None, (f"invocation {inv[:8]}'s selection witness is not the kit's whole witness (keys "
                      f"{', '.join(sorted(fins[0]['selection']))[:120] or 'none'}), so its population is not proven")
    if isinstance(policy, dict) and policy and set(policy) != WITNESS_KEYS:
        return None, (f"invocation {inv[:8]} is judged against a baseline witness that is not the kit's whole "
                      f"witness (keys {', '.join(sorted(policy))[:120]}), so its population cannot be compared")
    if isinstance(policy, dict) and not policy:   # C2c (C2a12 pre-read; B195/B196 owed): no witness = no policy
        return None, (f"invocation {inv[:8]} is judged against a baseline that holds no selection witness, so its "
                      f"population cannot be compared")
    if isinstance(policy, dict) and policy and fins[0]["selection"] != policy:
        diff = sorted(k for k in set(policy) | set(fins[0]["selection"] or {})
                      if (fins[0]["selection"] or {}).get(k) != policy.get(k))
        return None, (f"invocation {inv[:8]}'s selection differs from the baseline's standing policy "
                      f"({', '.join(diff)[:120]})")
    if (fins[0]["narrowed"] and isinstance(policy, dict) and policy and fins[0]["selection"] == policy
            and selection_digest(policy) not in set(approved or ())):
        # weekly-train:R17: a narrowed population equal to the baseline's counts only with a recorded approval of
        # that selection; recording a witness is not approving it
        return None, (f"invocation {inv[:8]} collected a narrowed population ({'; '.join(fins[0]['narrowed'])[:120]}) "
                      f"with no recorded approval of its selection {selection_digest(policy)[:12]} "
                      f"(record_authority.py --policy, weekly-train:R17)")
    if (fins[0]["narrowed"] and policy == "baseline" and fins[0]["selection"]
            and selection_digest(fins[0]["selection"]) not in set(approved or ())):
        # F4 (B201 finding 2, weekly-train:R17): the baseline records a narrowed suite's selection witness (so its
        # approval can be asked for and recorded), but the suite reads complete only once that exact selection is
        # approved; recording the witness is not approving it
        return None, (f"invocation {inv[:8]} collected a narrowed population ({'; '.join(fins[0]['narrowed'])[:120]}) "
                      f"with no recorded approval of its selection {selection_digest(fins[0]['selection'])[:12]}; the "
                      f"witness is recorded so it can be approved (record_authority.py --policy, weekly-train:R17), "
                      f"then the baseline is recorded again")
    if fins[0]["narrowed"] and (policy in ("record", "baseline") and fins[0]["selection"]
                                or isinstance(policy, dict) and policy and fins[0]["selection"] == policy):
        pass
    elif fins[0]["narrowed"] and isinstance(policy, dict):
        return None, (f"invocation {inv[:8]} collected a narrowed population whose selection differs from the "
                      f"baseline's (or the baseline holds none): {'; '.join(fins[0]['narrowed'])[:160]}")
    elif fins[0]["narrowed"]:
        return None, (f"invocation {inv[:8]} collected a population narrowed by inputs its command line does not "
                      f"declare: {'; '.join(fins[0]['narrowed'])[:200]}")
    if fins[0]["dropped"]:
        return None, (f"invocation {inv[:8]} dropped {fins[0]['dropped']} collected test(s) without deselecting "
                      f"them (a collection hook removed them)")
    if extra:
        return None, (f"invocation {inv[:8]} deselected {len(extra)} test(s) the kit did not declare "
                      f"(-k, -m, --deselect or --lf from its options), e.g. {extra[0][:80]}")
    ran = len({e["nodeid"] for e in events if e["when"] == "setup"})
    if fins[0]["ran"] != ran or fins[0]["collected"] != ran:
        return None, (f"invocation {inv[:8]} collected {fins[0]['collected']} test(s) and reported {ran} "
                      f"(it stopped early, or its records are incomplete)")
    return events, None


def _count_tally(text):
    """(failed, errors, None) from the run's one pytest count line, else (0, 0, why)."""
    lines = [ln.strip() for ln in (text or "").splitlines()]
    counts = [ln for ln in lines if _COUNT_LINE.match(ln)]
    if len(counts) != 1:
        return 0, 0, f"{len(counts)} pytest count lines in the output, not one"
    failed = sum(int(n) for n in re.findall(r"(\d+) (?:\w+ )?failed\b", counts[0]))
    errors = sum(int(n) for n in re.findall(r"(\d+) errors?\b", counts[0]))
    return failed, errors, None


def selection_digest(selection):
    """weekly-train:R17: the sha256 of a selection witness (canonical JSON), the value an approval names."""
    return hashlib.sha256(json.dumps(selection, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def report_failures(path, token, text, outcomes=False, exit_code=None, policy=None, approved=()):
    """The failing test ids of one run, from the kit's report (not from display text), as (ids, reason, events):
    `ids` the sorted distinct node ids with a failed outcome in any phase (collect included); `events` every failed
    (nodeid, phase) record, kept for the record; `reason` None only when the result is complete:
    - the run's output holds exactly one `aget-kit-report:` line, naming a pytest invocation, or a run of the kit's
      parallel runner whose record lists one invocation per test file it started;
    - every line of the report parses and carries this run's token (a fresh report per run: current-run);
    - each named invocation has one start and one finish record, ended with pytest exit 0, 1 or 5, and holds exactly
      the number of events its finish record counts;
    - cross-check: the output's one count line reports as many failed and errors as the report's events.
    Any shortfall gives a reason and no ids: an incomplete or unreadable record gives no exemption, and a consumer
    that reads `reason` must not count the run as clean (census test). With `outcomes`, `events` is every event of
    the invocation(s), passed and skipped included (the confirmation run asks which candidates actually ran).
    C2a10 (B192 finding 1): with `exit_code` (the invoking process's own exit, where the caller ran pytest itself),
    one pytest invocation's recorded exit must equal it: a hook that changes the status after the report was written
    makes the result not known, never clean."""
    if not path or not token:
        return [], "no kit report was made for this run (the failing ids are read only from the kit's report)", []
    marks = [ln.strip() for ln in (text or "").splitlines() if ln.strip().startswith(REPORT_MARK)]
    if len(marks) != 1 or not _MARK_LINE.fullmatch(marks[0]):
        return [], f"{len(marks)} kit report line(s) in the output, not exactly one well-formed line", []
    kind, ident = _MARK_LINE.fullmatch(marks[0]).groups()
    rows, why = _report_rows(path, token)
    if why:
        return [], why, []
    if kind == "pytest":
        invs = [ident]
    else:
        runner = [r for r in rows if r.get("rec") == "runner" and r.get("run") == ident]
        if len(runner) != 1:
            return [], f"{len(runner)} record(s) of parallel run {ident[:8]} in the report, not one", []
        rr = runner[0]
        invs = rr["children"]
        if rr["complete"] is not True or len(invs) != rr["files"] or len(set(invs)) != len(invs):
            return [], f"parallel run {ident[:8]} does not name one finished invocation per test file", []
    if isinstance(exit_code, int) and not isinstance(exit_code, bool) and kind == "runner" and exit_code not in (0, 1):
        return [], f"the parallel runner's process exited {exit_code} (killed or failed), not 0 or 1", []   # pre-read 5
    runner_exit = exit_code if isinstance(exit_code, int) and not isinstance(exit_code, bool) and kind == "runner" \
        else None
    if isinstance(exit_code, int) and not isinstance(exit_code, bool) and kind == "pytest":
        fin = [r for r in rows if r.get("inv") == ident and r.get("rec") == "finish"]
        if len(fin) == 1 and fin[0].get("exit") != exit_code:
            return [], (f"the process exited {exit_code}, but the report records pytest exit {fin[0].get('exit')!r} "
                        f"(the status changed after the report was written)"), []
    events = []
    child_policy = {}
    if kind == "runner" and isinstance(policy, dict):
        # C2c (FWK-OVSR7's C2c pre-read H3): a parallel run is judged against the baseline too. Its standing policy is
        # each child's whole witness by the child's one root, for exactly the files the baseline ran; anything else
        # (no witness, a plain run's witness, another file set) leaves the population not compared
        if not policy:
            return [], (f"parallel run {ident[:8]} is judged against a baseline that holds no selection witness, so "
                        f"its population cannot be compared"), []
        per = policy.get(PER_FILE) if set(policy) == {PER_FILE} else None
        if not isinstance(per, dict):
            return [], (f"parallel run {ident[:8]} is judged against a baseline witness that is not a parallel run's "
                        f"(keys {', '.join(sorted(policy))[:120]}), so its population cannot be compared"), []
        roots = _child_roots(rows, invs)
        if roots is None or sorted(roots) != sorted(per):
            return [], (f"parallel run {ident[:8]} ran a different set of test files from its baseline's, so its "
                        f"population cannot be compared"), []
        child_policy = {inv: per[root] if isinstance(per[root], dict) else {} for inv, root in zip(invs, roots)}
    for inv in invs:
        pol = (child_policy[inv] if child_policy else policy if policy in ("record", "baseline") else None) \
            if kind == "runner" else policy
        got, why = _invocation(rows, inv, child=kind == "runner", policy=pol, approved=approved)
        if why:
            return [], why, []
        events += got
    failing = [e for e in events if e["outcome"] == "failed"]
    # C2a12 (FWK-OVSR6's C2a11 pre-read 2): each child may collect nothing (exit 5), but a parallel run whose children
    # ran no test in total is not a run of the suite ("2 warnings in 0.1s" read clean with zero tests)
    if kind == "runner" and not failing and not any(e["when"] == "setup" for e in events):
        return [], f"parallel run {ident[:8]}: its {len(invs)} child run(s) ran no test", []
    failed, errors, why = _count_tally(text)
    if why:
        return [], f"cross-check: {why}", []
    n_failed = sum(1 for e in failing if e["when"] == "call")
    if (failed, errors) != (n_failed, len(failing) - n_failed):
        return [], (f"cross-check: the output counts {failed} failed and {errors} error(s), the report "
                    f"{n_failed} and {len(failing) - n_failed}"), []
    ids = sorted({e["nodeid"] for e in failing})
    # C2a11 (FWK-OVSR6's C2a10r pre-read): the runner's own exit agrees with its children's failures
    if runner_exit == 1 and not ids:
        return [], "the parallel runner exited 1, but no child run names a failing test", []
    if runner_exit == 0 and ids:
        return [], f"the parallel runner exited 0 with {len(ids)} failing test(s)", []
    return ids, None, [{"nodeid": e["nodeid"], "when": e["when"], **({"outcome": e["outcome"]} if outcomes else {})}
                       for e in (events if outcomes else failing)]


# Flags that change how pytest REPORTS, never which tests run or when it stops. The receiver prompt allows
# "python3 -m pytest (with any test arguments)", and a session that ran `python3 -m pytest -q -rfE -p no:cacheprovider`
# read INCONCLUSIVE because only the exact declared command counted (rehearsal, 2026-09-30: the same packet read PASS
# and then INCONCLUSIVE, depending on which flags the model added). Selection or early-stop flags (-k, -m, -x,
# --lf, a path) still do not count: a narrowed run cannot show the whole suite's regressions.
_REPORT_ONLY = re.compile(r"^(-q|-qq|-v|-vv|-r[a-zA-Z]+|--tb=(short|long|line|native|no|auto)|--no-header|"
                          r"-p no:cacheprovider|--color=(yes|no|auto)|--durations=\d+)$")


def is_suite_run(cmd, suite_cmd):
    """Declared command in order, with permitted reporting-only flags between its arguments or appended."""
    import shlex
    try:       # C2a10 (FWK-OVSR5's C2a9 advisory 5): a trailing shell comment is no part of the command bash runs
        got, want = shlex.split(cmd or "", comments=True), shlex.split(suite_cmd or "")
    except ValueError:
        return False
    def arguments(words):
        # The cache-provider option and its value stay together; no insertion inside this pair.
        out, i = [], 0
        while i < len(words):
            if words[i:i + 2] == ["-p", "no:cacheprovider"]:
                out.append(("-p", "no:cacheprovider"))
                i += 2
            else:
                out.append(words[i])
                i += 1
        return out
    got, want = arguments(got), arguments(want)
    if not want or not got or got[0] != want[0]:
        return False
    # Preserve every declared argument in its declared order. Only the already permitted reporting
    # flags may be inserted between them or appended; a declared flag cannot be dropped.
    i = 1
    for tok in got[1:]:
        if i < len(want) and tok == want[i]:
            i += 1
        elif tok != ("-p", "no:cacheprovider") and not _REPORT_ONLY.match(tok):
            return False
    return i == len(want)


def mentions_suite(cmd, suite_cmd):
    """Whether a command holds the declared suite command's words anywhere (wrapped, chained, backgrounded, piped):
    a call that runs the suite in a form `is_suite_run` does not judge."""
    # C2a10 (FWK-OVSR6's C2a10 pre-read 3): compared as shell words, so quoting (`"pytest"`) and an `sh -c '…'`
    # argument do not hide it, and a mention inside a trailing comment does not count
    import shlex

    def words(text, depth=0):
        # C2a11 (FWK-OVSR6's C2a10r pre-read 3): shell operators (`;`, `&&`, `||`, `|`, `&`) are boundaries, never
        # part of a word, and `-mpytest` is `-m pytest`
        try:
            lex = shlex.shlex(text or "", posix=True, punctuation_chars=True)
            lex.whitespace_split = True
            lex.commenters = "#"
            got = list(lex)
        except ValueError:
            # C2a12 (FWK-OVSR6's C2a11 pre-read 7): a command shlex cannot read (a later line with an unbalanced
            # quote) is still run by bash line by line; split it at whitespace, operators and quotes, so `pytest;`
            # on its first line is not one word
            if depth == 0:
                unparsable.append(text)
            got = [w for w in re.split(r"[\s;&|'\"`()]+", text or "") if w]
        out = []
        for g in got:
            if depth < 2 and " " in g:
                out += words(g, depth + 1)
            elif g.startswith("-m") and len(g) > 2 and not g.startswith("--"):
                out += ["-m", g[2:]]
            else:
                out.append(g)
        return out
    unparsable = []
    # C2a13 (C2a12 second pass M12): bash removes a backslash-newline pair before splitting words (`py\<nl>test` runs
    # pytest), so the pair is removed before parsing
    cmd, suite_cmd = (cmd or "").replace("\\\n", ""), (suite_cmd or "").replace("\\\n", "")
    want = words(suite_cmd)
    unparsable.clear()                       # only the judged command's own parse counts
    have = words(cmd)
    if want and any(have[i:i + len(want)] == want for i in range(len(have) - len(want) + 1)):
        return True
    # C2a12 (B195 #2): a parse failure never restores an older result. A command shlex cannot read is ambiguous
    # when it holds any of the suite's own words (the interpreter and flags aside): it counts as a mention, so the
    # earlier result is not used and the run is unavailable
    own = [w for w in want[1:] if not w.startswith("-")]
    if unparsable and any(w in (cmd or "") for w in own):
        return True
    # C2a12 (FWK-OVSR6's C2a12 pre-read, HIGH): shell grammar is not enumerated. A later call holding the suite's
    # PROGRAM word (the `-m` module, or the script's file name; `py.test` for pytest) anywhere as a word, after
    # joining backslash-continued lines, is a mention: backticks, `$(…)`, `x=`…``, continuation lines and wrappers
    # included. A false mention costs a rerun; a missed one credits an older result
    # (a parsed command is searched in its shell words, so a trailing `# …` comment stays no mention, C2a10)
    text = (cmd or "").replace("\\\n", "") if unparsable else " ".join(have)
    progs = _program_words(want)
    if progs is None:           # C2a13 (B196 finding 2): an unresolved program: any later call may be the suite
        return bool((cmd or "").strip())
    # C2a14 (B197 finding 2): a later command whose program (or its `-m` module / script) needs the shell to expand
    # it (`py${X}test`, a backtick, a glob) cannot be identified: it counts as a mention, never as some other program
    if not unparsable:
        starts = [0] + [n + 1 for n, w in enumerate(have) if w in (";", "&&", "||", "|", "&", "(", ")", "|&")]
        for st in starts:
            if st < len(have) and _unresolved(have, st):
                return True
    # C2a14 (FWK-OVSR7's add-on 6): a versioned runner (`pytest-3`, `/usr/bin/pytest-3.12`) is the runner too
    return any(re.search(rf"(?:(?<![\w.\-])|(?<=-m)){re.escape(w)}(?!\w|-[^\d]|\.\w)", text) for w in progs)


def _program_words(want):
    """The words that name the suite's program (C2a13, B196 finding 2: `python -W ignore -m pytest` made `ignore` the
    program word): pytest's own runner words always (`pytest`, `py.test`), plus every module named after `-m` and the
    file name of every `.py` script the declared command holds. A declared command naming none of these leaves the
    program unresolved: `None`, and every later call then counts as a mention (unavailable, never an older result)."""
    words = {"pytest", "py.test"}
    prog = _program_at(want, 0)
    if prog is None:
        return None
    if prog not in ("pytest", "py.test"):
        words.add(prog)
    return sorted(words)


_ASSIGN = re.compile(r"[A-Za-z_][A-Za-z0-9_]*=")
_RUNNER = re.compile(r"(?:pytest|py\.test)(?:-\d[\d.]*)?")      # pytest, py.test, pytest-3, pytest-3.12
_EXPANDS = re.compile(r"[$`*?\[{~]")


_WRAPPERS = {"nice", "time", "exec", "nohup", "env", "sudo", "command", "builtin", "xargs", "timeout", "stdbuf",
             "uv", "uvx", "poetry", "pdm", "hatch", "pipenv", "rye", "tox", "nox", "make", "npx", "doas", "caffeinate"}
_SHELLS = {"bash", "sh", "zsh", "dash", "ksh", "fish"}


_SH_KEYWORDS = ("then", "do", "else", "elif", "if", "while", "until", "!", "{", "time", "coproc")


def _unresolved(ws, i):
    """Whether the command starting at word `i` names its program, or its interpreter's `-m` module or script, only
    through something the shell expands (C2a14, B197 finding 2). C2a14 (FWK-OVSR7's C2a14 pre-read 6): wrappers
    (`nice`, `time`, `exec`, `/usr/bin/env`, `env -u X`, `uv run`, `poetry run`, …) and a shell's `-c` string are
    looked through, so every program position is checked, not only the first word."""
    while i < len(ws):
        # D2 (C2e pre-read 1): a shell keyword opening a command (`then`, `do`, `else`, `elif`, `!`, …) is not its
        # program; the program is the next word
        while i < len(ws) and (_ASSIGN.match(ws[i]) or ws[i] in ("run", "--", "exec") or ws[i] in _SH_KEYWORDS):
            i += 1
        if i >= len(ws):
            return False
        w = ws[i]
        if _EXPANDS.search(w):
            return True
        b = os.path.basename(w)
        if b in _WRAPPERS:
            i += 1
            while i < len(ws) and ws[i].startswith("-"):       # the wrapper's options (`env -u X`: X is skipped too)
                i += 2 if ws[i] in ("-u", "-C", "-S", "-n", "-k", "-s") and i + 1 < len(ws) else 1
            if b == "timeout" and i < len(ws) and ws[i][:1].isdigit():
                i += 1
            continue
        if b in _SHELLS:
            i += 1
            while i < len(ws) and ws[i].startswith("-"):
                i += 1                                           # `-c`, `-lc`: the string was split into words
            continue
        if b.startswith("python"):
            j = i + 1
            while j < len(ws):
                if ws[j] == "-m":
                    return j + 1 < len(ws) and bool(_EXPANDS.search(ws[j + 1]))
                if ws[j] in _PY_OPERAND:
                    j += 2
                elif ws[j] in ("-V", "--version", "-VV", "-h", "--help"):     # prints and exits: no program runs
                    return False
                elif ws[j] == "-" or (ws[j].startswith("-") and not ws[j].startswith("--") and "c" in ws[j][1:]):
                    # C2a15 (B198 finding 2): interpreter code the kit cannot resolve (`-c '…'`, a `-Bc` cluster, a
                    # program read from stdin `-`): it may run the suite (`import_module('py'+'test')`), so it is a
                    # mention, never some other program
                    return True
                elif ws[j].startswith("-"):
                    j += 1
                elif ws[j] in ("<", "<<", "<<<", "|"):
                    return True
                else:
                    return bool(_EXPANDS.search(ws[j]))
            # C2a15 (B198 finding 2): an interpreter given no script and no module reads its program from stdin (a
            # heredoc, a pipe): unresolved
            return True
        return False
        return False
    return False


_PY_OPERAND = ("-W", "-X", "-Q", "--check-hash-based-pycs")


def _program_at(ws, i):
    """C2a14 (FWK-OVSR7's C2a13 second pass 3; C2a13r M3): the program the command starting at word `i` runs, as one
    word: `env` and its options, `NAME=value` assignments and interpreter options (with their operands: `-W ignore`)
    are skipped; an interpreter runs its `-m` module or its script (file name); `pytest`/`py.test` run pytest; any other
    first word (a wrapper: `uv run`, `tox`, `make`) is looked through for a runner word, an interpreter or a `.py`
    script. None when no program is identified (unresolved)."""
    while i < len(ws) and (ws[i] == "env" or _ASSIGN.match(ws[i]) or (ws[i].startswith("-") and i and ws[i - 1] == "env")):
        i += 1
    if i >= len(ws):
        return None
    w = os.path.basename(ws[i])
    if _RUNNER.fullmatch(w):
        return "pytest"
    if w.startswith("python"):
        j = i + 1
        while j < len(ws):
            if ws[j] == "-m":
                return ws[j + 1] if j + 1 < len(ws) else None
            if ws[j] in _PY_OPERAND:
                j += 2
            elif ws[j].startswith("-"):
                j += 1
            else:
                return os.path.basename(ws[j])
        return None
    if w.endswith(".py"):
        return w
    for j in range(i + 1, len(ws)):         # a wrapper: the first program inside it
        b = os.path.basename(ws[j])
        if _RUNNER.fullmatch(b) or b.startswith("python") or b.endswith(".py"):
            return _program_at(ws, j)
    return None


def last_call_output(stream_text, matches, bash_only=False, mentions=None, with_error=False):
    """(output, None) for the LAST tool call in a session stream or transcript whose command `matches`, or (None,
    why). B190 finding 1, by class (the one reader for F and the baseline producer): the output is the result whose
    `tool_use_id` is that call's own id, whatever order results arrive in; no result, more than one, or a call id
    used twice gives a reason, never an earlier call's output. A list result is joined by line feeds, so its lines
    stay lines.
    C2a10 (FWK-OVSR5's C2a9 advisory 2, 3 and 5, Codex and agy): an id is counted over EVERY tool call, so a
    non-matching call cannot lend the suite call its id and its result; a result that arrives before its call (or has
    none) refuses, as do two calls sharing an id and a stream holding more than one session; and a later call that `mentions` the command without matching it (a wrapper, a chain, a
    background run) refuses, since its run would be the session's last and cannot be judged.
    C2a10 (B192 finding 2): a matching call or a result with no string id refuses (ids are never joined as None);
    with `with_error`, returns (output, why, is_error) so a consumer can refuse an error-marked result its run does
    not explain."""
    ids, calls, results, last, after, err, noid, sessions, early = {}, set(), {}, None, None, {}, False, set(), []
    unnamed = False         # C2a12 (C2a11 pre-read 5): a call or result whose event names no session
    seq = []                # D2 (B199 finding 2): the calls in transcript order
    for line in (stream_text or "").splitlines():
        try:
            ev = json.loads(line)
        except ValueError:
            continue
        msg = ev.get("message") if isinstance(ev, dict) and isinstance(ev.get("message"), dict) else {}
        for key in ("sessionId", "session_id"):   # C2a12 (C2a12 pre-read): stream-json writes `session_id`
            if isinstance(ev, dict) and ev.get(key) is not None:     # C2a10 (pre-read 2): one session only
                sessions.add(repr(ev.get(key)))     # 1 and "1" are two sessions (C2a10r pre-read)
        content = msg.get("content")
        if isinstance(content, list) and any(isinstance(b, dict) and b.get("type") in ("tool_use", "tool_result")
                                             for b in content) and (not isinstance(ev, dict)
                                                                    or ev.get("sessionId") is None
                                                                    and ev.get("session_id") is None):
            unnamed = True
        for b in content if isinstance(content, list) else []:
            if not isinstance(b, dict):
                continue
            if b.get("type") == "tool_use":
                if not (isinstance(b.get("id"), str) and b.get("id")):  # C2a10 (pre-read 2): a list id never hashes
                    noid = True
                    continue
                ids[b.get("id")] = ids.get(b.get("id"), 0) + 1
                seq.append(b.get("id"))
                cmd = (b.get("input") or {}).get("command")
                if not isinstance(cmd, str) or (bash_only and b.get("name") != "Bash"):
                    continue
                if matches(cmd):
                    noid = noid or not (isinstance(b.get("id"), str) and b.get("id"))
                    calls.add(b.get("id"))
                    last, after = b.get("id"), None
                elif mentions is not None and mentions(cmd):
                    after = cmd
            elif b.get("type") == "tool_result":
                if not (isinstance(b.get("tool_use_id"), str) and b.get("tool_use_id")):
                    noid = True
                    continue
                if b.get("tool_use_id") not in ids:       # C2a10 (pre-read 2): a result before (or without) its call
                    early.append(b.get("tool_use_id"))
                c = b.get("content")
                text = c if isinstance(c, str) else "\n".join(
                    x.get("text", "") for x in c if isinstance(x, dict)) if isinstance(c, list) else ""
                results.setdefault(b.get("tool_use_id"), []).append(text)
                err.setdefault(b.get("tool_use_id"), []).append(b.get("is_error") is True)

    def no(why):
        return (None, why, None) if with_error else (None, why)
    if noid:
        return no("a call or a tool result has no id")
    if len(sessions) > 1:
        return no(f"the transcript holds {len(sessions)} sessions, not one")
    if unnamed:     # C2a12 (C2a11 pre-read 5; B195 #3): a session identity is required on every call and result, so
        #             an all-missing (or null) transcript is not "one session" by an empty set
        return no("a tool call or result names no session (sessionId missing or null)")
    if any(n != 1 for n in ids.values()):
        return no("a tool call id is used by more than one call")
    if early:
        return no(f"a tool result arrives before its call, or has none ({str(early[0])[:12]})")
    if last is None:
        return no("no call of the command in the transcript")
    if after is not None:
        return no(f"a later call runs the command in a form the kit does not judge: {after[:80]}")
    # D2 (B199 finding 2; no named-script waiver): a later call of ANY form whose own output shows a pytest run (a
    # pytest count line, or the kit's report line) is a run the kit did not judge, so the earlier result is not used
    if mentions is not None and last in seq:
        for cid in seq[seq.index(last) + 1:]:
            for t in results.get(cid, []):
                if REPORT_MARK in t or any(_COUNT_LINE.match(ln.strip()) for ln in t.splitlines()):
                    return no(f"a later call's output shows a pytest run the kit does not judge ({str(cid)[:12]})")
    if ids[last] != 1:
        return no(f"the last call's id {str(last)[:12]} is used by {ids[last]} calls")
    got = results.get(last, [])
    if len(got) != 1:
        return no(f"the last call of the command has {len(got)} results in the transcript, not one")
    return (got[0], None, err[last][0]) if with_error else (got[0], None)


def append_runner_record(path, token, run, files, children, complete):
    """The kit's parallel runner's record of one run: the number of test files it started and each one's invocation.
    Appended to the report (never through a link, never created here). Raises OSError."""
    fd = open_report(path, os.O_WRONLY | os.O_APPEND)   # B188 finding 2: a non-regular report is refused, unwaited
    try:
        os.write(fd, (json.dumps({"rec": "runner", "token": token, "run": run, "files": files,
                                  "children": children, "complete": complete}, sort_keys=True) + "\n").encode())
    finally:
        os.close(fd)


def apply_entry(receipt, aget, list_sha256=None, batch=None, location=None):
    """R2-T6 (S-164, S-171, S-187, S-321, S-329): the apply receipt's entry for `aget`, as (entry, None), only when it
    is bound: the receipt is an object written by an applying run (`mode` "apply", not "dry-run" or absent), naming
    `list_sha256` when the caller knows the reviewed list's digest, with exactly one entry for `aget`, whose `result`
    is APPLIED and whose every file is an object with a string `path`, a string `post` and `ok` true. Otherwise
    (None, reason): no consumer takes files, exemptions or a pass from an unbound entry."""
    if not isinstance(receipt, dict):
        return None, "the apply receipt is not an object"
    if receipt.get("mode") != "apply":
        return None, f"the apply receipt's mode is {receipt.get('mode')!r}, not 'apply' (a trial run writes nothing)"
    if list_sha256 is not None and receipt.get("list_sha256") != list_sha256:
        return None, (f"the apply receipt names list {str(receipt.get('list_sha256'))[:12]}, not the reviewed list "
                      f"{str(list_sha256)[:12]}")
    # C2d (FWK-OVSR8's C2d pre-read 1): the receipt is this batch's, where the caller knows the batch
    if batch is not None and str(receipt.get("batch")) != str(batch):
        return None, f"the apply receipt is batch {str(receipt.get('batch'))[:20]!r}'s, not batch {str(batch)[:20]!r}'s"
    rows = [x for x in receipt.get("agets") or [] if isinstance(x, dict) and x.get("aget") == aget]
    if len(rows) != 1:
        return None, f"the apply receipt has {len(rows)} entries for {aget}, not one"
    entry = rows[0]
    if location is not None and not _same_location(entry.get("location"), location):   # C2d (C2d pre-read 1)
        return None, (f"the apply receipt's entry for {aget} was applied at {str(entry.get('location'))[:80]!r}, not at "
                      f"this member's location")
    if entry.get("result") != "APPLIED":
        return None, f"the apply receipt's result for {aget} is {entry.get('result')!r}, not APPLIED"
    files = entry.get("files", [])
    if not isinstance(files, list) or not all(isinstance(f, dict) and isinstance(f.get("path"), str)
                                              and isinstance(f.get("post"), str) and f.get("ok") is True
                                              for f in files):
        return None, f"the apply receipt's files for {aget} are not each written (path, post, ok true)"
    return entry, None


def _same_location(a, b):
    """True when two member locations name the same folder (user and links expanded)."""
    if not isinstance(a, str) or not isinstance(b, (str, os.PathLike)) or not a:
        return False
    return os.path.realpath(os.path.expanduser(a)) == os.path.realpath(os.path.expanduser(str(b)))


def receipt_path(r):
    """Where a receiver writes its receipt: the packet's `receipt_path`, else docs/V335_RECEIVER_RECEIPT_<aget>.md.
    The one source for the launch prompt, the after-run check H and the push gate."""
    return r.get("receipt_path") or f"docs/V335_RECEIVER_RECEIPT_{r['aget']}.md"


ATTEMPT_ID = re.compile(r"^[A-Za-z0-9._-]+$")


def receipt_instruction(attempt, note=None):
    """The receipt instruction every prompt family gives (R2 and R3 own it together; one source): the section
    heading the grammar reads and the one terminal line. Raises ValueError for an attempt id the heading cannot
    carry."""
    if not ATTEMPT_ID.match(attempt or ""):
        raise ValueError(f"attempt id {attempt!r} is not [A-Za-z0-9._-]+, so no receipt heading can name it")
    head = f"## Attempt {attempt}" + (f" ({note})" if note else "")
    return (f"add a section headed exactly `{head}` after all earlier text (keep every earlier attempt as it is)",
            f"End that section with exactly one line `Terminal: <X>`, X one of {', '.join(TERMINALS)}, as its last "
            "line. No other line in the section may begin with 'Terminal' or be a terminal value alone.")


def atomic_write(path, data):
    """Replace `path` with `data`: a new temp file with a random name made with O_EXCL (so never an existing link or
    a second name of another file), in the same folder, then os.replace, which replaces the name without following
    it. For the tools' own output files (receipts, results); member files go through copy_isolation's writer."""
    import tempfile
    path = Path(path)
    fd, tmp = tempfile.mkstemp(dir=path.parent, prefix=f".{path.name}.", suffix=".tmp")
    try:
        with os.fdopen(fd, "wb") as fh:
            fh.write(data)
        os.replace(tmp, path)
        tmp = None
    finally:
        if tmp is not None:
            try:
                os.unlink(tmp)
            except OSError:
                pass


def _child_roots(rows, invs):
    """The one root of each child invocation, from its finish record's witness, or None when any child has not
    exactly one finish record naming exactly one root, or two children share a root."""
    roots = []
    for inv in invs:
        fin = [r for r in rows if r.get("inv") == inv and r.get("rec") == "finish"]
        sel = fin[0].get("selection") if len(fin) == 1 else None
        if not isinstance(sel, dict) or not isinstance(sel.get("roots"), list) or len(sel["roots"]) != 1:
            return None
        roots.append(sel["roots"][0])
    return roots if len(set(roots)) == len(roots) else None


def invocation_selection(path, token, text):
    """C2a11 (B194 finding 6): the selection witness of the one pytest invocation `text` names, or None (no report
    line, an unreadable report, a witness that is not the kit's whole witness). The baseline records it as its
    standing policy. C2c (FWK-OVSR7's C2c pre-read H3): for a run of the kit's parallel runner, `{"per_file": {root:
    witness}}` over its children, each by its one root."""
    marks = [ln.strip() for ln in (text or "").splitlines() if ln.strip().startswith(REPORT_MARK)]
    if len(marks) != 1 or not _MARK_LINE.fullmatch(marks[0]):
        return None
    kind, ident = _MARK_LINE.fullmatch(marks[0]).groups()
    rows, why = _report_rows(path, token)
    if why:
        return None
    if kind == "pytest":
        fin = [r for r in rows if r.get("inv") == ident and r.get("rec") == "finish"]
        sel = fin[0].get("selection") if len(fin) == 1 else None
        return dict(sel) if isinstance(sel, dict) and set(sel) == WITNESS_KEYS else None
    runner = [r for r in rows if r.get("rec") == "runner" and r.get("run") == ident]
    if len(runner) != 1 or not isinstance(runner[0].get("children"), list):
        return None
    invs = runner[0]["children"]
    roots = _child_roots(rows, invs)
    if roots is None:
        return None
    per = {}
    for inv, root in zip(invs, roots):
        sel = [r for r in rows if r.get("inv") == inv and r.get("rec") == "finish"][0]["selection"]
        if set(sel) != WITNESS_KEYS:
            return None
        per[root] = dict(sel)
    return {PER_FILE: per}
