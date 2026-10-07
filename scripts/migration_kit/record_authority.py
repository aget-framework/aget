"""Record a batch's authority in records.json, only from lines found in a prompt the principal TYPED (limits below).
(carriage row 62; supervisor original 2026-09-30)

Why: per-batch recorders once wrote authority the supervisor composed; the permission classifier refused one as
"Instruction Poisoning" and the principal had to run it by hand. Whoever writes the authority record can otherwise
mint authority. This recorder applies the checks below before writing. Limits: the line given with --line is matched
as a SUBSTRING of a typed prompt, so words the principal typed around it are not recorded and are not read by the
shape and act tests. That does not hold for `--act push` and `--ruling-line` (F-3): there the typed prompt must equal
the line. The batch-list test and the `--scope-override` and `--held` tests (Aget name, "held") do read
that prompt's text, less a paste quoted among other words: words around the line can satisfy them, and the batch list
tested is the first one in that text, inside the line or not. A line found in a mid-turn human entry, whose prompt
source the tool does not read, is accepted as typed, and the record's source says so. The --held-head value,
the SCOPE text and the CHANGE text are written as given on the command line, compared with no typed line:

- `batch_authority[key]` (never replaced): the batch line must pass `batch_authority.verify` for every batch in the key
  (typed, the principal line prefix, >= 30 characters, the typed prompt's first batch list names the batch).
- `--act launch|push` (R-F12): records the line as `batch_authority[key:act]`, a second line for one act. The line must
  also pass that act's test. Launch: no negation word within 30 characters before the word launch in one clause; the
  line need not name the launch. Push (F-3; the push tool reads only this entry, never the batch line): the line has
  the one fixed form `batch_authority.PUSH_FORM` (the prefix, then `push the commits of batch N`, optionally more
  batches and ` with commit SHA`) and is the whole typed prompt.
- `--scope-override AGET=SCOPE`: AGET must be a receiver in `--packet` AND be named in the typed batch prompt (its
  short name, e.g. "professional-core"). The key's batches are appended to its `batches`; the scope text goes only into
  a new `history` entry quoting the line; the existing `scope` is never rewritten.
- `--check-change AGET:NAME=CHANGE`: needs its own `--check-line`, verified on its own terms (typed, the prefix,
  >= 30 characters; the typed prompt that contains it names the Aget's short name and NAME), independent of any batch
  naming.
- `--held AGET=SHA,...`: each list must have as many entries as `git rev-list @{upstream}..HEAD` prints in that Aget
  (from `--packet`), each entry a prefix (any length, even empty; not checked distinct) of one of those commits; the
  entries are recorded as given. The typed batch prompt must name the Aget and contain "held".

Usage: python3 scripts/migration_kit/record_authority.py [--key 13 --line "<typed batch line>"] --session <8 hex>
           [--packet P] [--held AGET=SHA,...] [--held-head SHA] [--scope-override AGET=SCOPE]
           [--check-line "<typed check line>" --check-change AGET:NAME=CHANGE] [--dry-run]
"""
import argparse
import hashlib
import json
import re
import os
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import batch_authority  # noqa: E402
import result_binding as RBND  # noqa: E402  (weekly-train:R17: the selection digest)

RECORDS = batch_authority.RECORDS


def short_name(aget):
    """Return the Aget's short name: lower case, without the private- or public- prefix and the -aget suffix."""
    return re.sub(r"(?i)^(private|public)-|-aget$", "", aget).lower()


def typed_prompt(line, session, projects_dir=None):
    """(ok, why, prompt text) for a line on its own terms: typed, the principal line prefix, >= 30 characters."""
    import check_principal_line as C
    norm = " ".join(str(line).split())
    bad = batch_authority.line_shape(norm)
    if bad:
        return False, bad, None
    files = sorted(Path(projects_dir or C.DEFAULT_DIR).glob(f"{session}*.jsonl"))
    if not files:
        return False, f"no transcript for session {session!r}", None
    code, hit = C.check(files, norm)
    if code not in (0, 4):
        return False, f"not typed (check_principal_line exit {code})", None
    return True, f"{batch_authority.provenance(code)} {hit[0]}", hit[2]


def names(word, text):
    """Whole-word match, case-insensitive. A bare substring test let a one-letter check name ("G") match any line
    containing "GO", and a short Aget name match inside a longer word (found porting this recorder, 2026-09-30)."""
    return re.search(rf"(?<![a-z0-9]){re.escape(word.lower())}(?![a-z0-9])", (text or "").lower()) is not None


def receivers(packet):
    """Return the packet's receivers keyed by Aget name; empty when no packet is given."""
    return {r["aget"]: r for r in json.loads(Path(packet).read_text())["receivers"]} if packet else {}


def check_scope(aget, prompt, recv):
    """Return why a scope override cannot be recorded for this Aget, or None when it can."""
    if aget not in recv:
        return f"scope override for {aget}: not a receiver in the packet"
    if not names(short_name(aget), prompt):
        return f"scope override for {aget}: the typed prompt does not name {short_name(aget)!r}"
    return None


def check_held(aget, shas, prompt, recv):
    """Return why held commits cannot be recorded for this Aget, or None when they can."""
    if aget not in recv:
        return f"held commits for {aget}: not a receiver in the packet"
    if not names(short_name(aget), prompt) or not names("held", prompt):
        return f"held commits for {aget}: the typed prompt must name {short_name(aget)!r} and say 'held'"
    p = subprocess.run(["git", "--no-optional-locks", "--no-lazy-fetch", "-C", recv[aget]["location"], "rev-list",
                        "@{upstream}..HEAD"], capture_output=True, text=True,
                       env={**os.environ, "GIT_OPTIONAL_LOCKS": "0", "GIT_NO_LAZY_FETCH": "1"})  # B166 finding 2: a read that leaves the git folder as it was
    actual = p.stdout.split()
    if p.returncode or len(actual) != len(shas) or not all(any(a.startswith(s) for a in actual) for s in shas):
        return f"held commits for {aget}: {shas} is not @{{upstream}}..HEAD ({[a[:7] for a in actual]})"
    return None


def check_change_line(aget, name, prompt):
    """Return why a check change cannot be recorded from this prompt, or None when it can."""
    if not names(short_name(aget), prompt) or not names(name, prompt):
        return f"check change {aget}:{name}: the check line must name {short_name(aget)!r} and {name!r}"
    return None


def main(argv=None, records=RECORDS, projects_dir=None):
    """Command-line entry point: record a batch's authority from lines found typed (limits in the module docstring)."""
    ap = argparse.ArgumentParser()
    ap.add_argument("--key", help="the batch key, batches joined by '+', e.g. 11t+11")
    ap.add_argument("--line", help="the principal's typed batch line")
    ap.add_argument("--act", choices=batch_authority.ACTS, help="record the line for one act only (key:act)")
    ap.add_argument("--session", required=True)
    ap.add_argument("--packet", type=Path)
    ap.add_argument("--held", nargs="*", default=[], metavar="AGET=SHA,SHA")
    ap.add_argument("--held-head")
    ap.add_argument("--scope-override", nargs="*", default=[], metavar="AGET=SCOPE")
    ap.add_argument("--check-line", help="the principal's typed ruling line for --check-change")
    ap.add_argument("--check-change", nargs="*", default=[], metavar="AGET:NAME=CHANGE")
    ap.add_argument("--baseline-equal", nargs="*", default=[], metavar="AGET=SHA",
                    help="record the principal's ruling that a B8a FAIL at this commit is baseline-equal (K1)")
    ap.add_argument("--ruling-line", help="the principal's typed ruling line for --baseline-equal")
    ap.add_argument("--evidence", type=Path, help="the batch's evidence folder (with --baseline-equal)")
    ap.add_argument("--policy", nargs="*", default=[], metavar="AGET=DIGEST",
                    help="record the principal's approval of a member's narrowed suite (weekly-train:R17); DIGEST "
                         "is the selection digest of the member's baseline record in --evidence")
    ap.add_argument("--policy-line", help="the principal's typed approval line for --policy")
    ap.add_argument("--dry-run", action="store_true")
    a = ap.parse_args(argv)

    def refuse(why):
        print(f"REFUSED, nothing written: {why}")
        return 1

    if bool(a.key) != bool(a.line):
        return refuse("--key and --line go together")
    if (a.held or a.scope_override) and not a.key:
        return refuse("--held and --scope-override need a batch --key and --line")
    if a.check_change and not a.check_line:
        return refuse("--check-change needs its own --check-line")
    if a.baseline_equal and not (a.ruling_line and a.evidence):
        return refuse("--baseline-equal needs --ruling-line and --evidence")
    if a.policy and not (a.policy_line and a.evidence):
        return refuse("--policy needs --policy-line and --evidence")
    approvals = []          # weekly-train:R17: bound to the selection the member's baseline record holds
    for spec in a.policy:
        aget, _, short = spec.partition("=")
        try:
            sel = json.loads((a.evidence / aget / "baseline_record.json").read_text()).get("selection")
        except (OSError, ValueError, AttributeError):
            sel = None
        if not isinstance(sel, dict) or not sel:
            return refuse(f"policy {aget}: no baseline record with a selection in {a.evidence / aget}")
        full = RBND.selection_digest(sel)
        if len(short) < 8 or not full.startswith(short.lower()):
            return refuse(f"policy {aget}: the baseline's selection is {full[:12]}, not {short!r}")
        entry = {"line": " ".join(a.policy_line.split()), "session": a.session}
        ok, how = batch_authority.verify_policy(entry, aget, full, projects_dir)
        if not ok:
            return refuse(f"policy {aget}: {how}")
        entry["source"] = f"principal, {how}, session {a.session}; recorded by record_authority.py"
        approvals.append((aget, full, entry))
    recv = receivers(a.packet)
    whys, prompt = [], None
    if a.key:
        probe = {"line": a.line, "session": a.session}
        for b in a.key.split("+"):
            ok, why = batch_authority.verify(a.key, probe, b, projects_dir, a.act)
            if not ok:
                return refuse(f"batch {b}: {why}")
            whys.append(why)
        prompt = typed_prompt(a.line, a.session, projects_dir)[2]
    held = {k: v.split(",") for k, v in (h.split("=", 1) for h in a.held)}
    scopes = dict(s.split("=", 1) for s in a.scope_override)
    for aget, shas in held.items():
        why = check_held(aget, shas, prompt, recv)
        if why:
            return refuse(why)
    for aget in scopes:
        why = check_scope(aget, prompt, recv)
        if why:
            return refuse(why)
    changes = []
    if a.check_change:
        ok, why, cprompt = typed_prompt(a.check_line, a.session, projects_dir)
        if not ok:
            return refuse(f"check line: {why}")
        for c in a.check_change:
            head, change = c.split("=", 1)
            aget, name = head.split(":", 1)
            bad = check_change_line(aget, name, cprompt)
            if bad:
                return refuse(bad)
            changes.append((aget, name, change, why))

    # K1: a baseline-equal ruling is written here, so no hand step is needed (nothing stops a file written by hand).
    # It is bound to the commit the B8a record names and to a line found typed in a transcript the --session value
    # selects (F-3: it has the one fixed ruling form and is the whole typed prompt; no member name); push_batch.py
    # repeats the same line check when it reads the file.
    be_rulings = []
    for spec in a.baseline_equal:
        aget, _, short = spec.partition("=")
        folder = a.evidence / aget
        try:
            full = json.loads((folder / "suite_at_commit.json").read_text()).get("sha") or ""
        except (OSError, ValueError):
            return refuse(f"baseline-equal {aget}: no B8a record (suite_at_commit.json) in {folder}")
        if len(short) < 7 or not full.startswith(short.lower()):
            return refuse(f"baseline-equal {aget}: the B8a record names {full[:8] or 'no commit'}, not {short!r}")
        target = folder / "baseline_equal_ruling.json"
        if target.exists():
            return refuse(f"baseline-equal {aget}: {target} already exists")
        line = " ".join(a.ruling_line.split())
        ruling = {"sha": full, "line": line, "session": a.session}
        ok, how = batch_authority.verify_ruling(ruling, full, projects_dir)
        if not ok:
            return refuse(f"baseline-equal {aget}: {how}")
        ruling["source"] = f"principal, {how}, session {a.session}; recorded by record_authority.py"
        be_rulings.append((target, ruling))

    d = json.loads(Path(records).read_text())
    src = f"principal, typed, session {a.session} ({'; '.join(whys)}; recorded by record_authority.py): \"{a.line}\""
    if a.act and (held or scopes):
        return refuse("--act records one act's line only; --held and --scope-override go with the batch line")
    if a.key:
        ba = d.setdefault("batch_authority", {})
        store = f"{a.key}:{a.act}" if a.act else a.key
        if store in ba:
            return refuse(f"batch_authority[{store}] already exists")
        entry = {"line": a.line, "session": a.session, "source": src}
        if a.act == "push":           # R2-T12: a push line is bound to the packet it authorizes pushing from
            if not a.packet:
                return refuse("--act push needs --packet: the push line is recorded for one packet's bytes")
            entry["packet_sha256"] = hashlib.sha256(Path(a.packet).read_bytes()).hexdigest()
        if held:
            entry["held_commits"] = held
        if a.held_head:
            entry["held_head"] = a.held_head
        ba[store] = entry
    for aget, scope in scopes.items():
        ov = d.setdefault("scope_overrides", {}).setdefault(aget, {"batches": []})
        added = [b for b in a.key.split("+") if b not in ov["batches"]]
        ov["batches"].extend(added)
        ov.setdefault("history", []).append({"batches_added": added, "scope": scope, "line": a.line, "source": src})
        ov["source"] = src
    for aget, full, entry in approvals:
        d.setdefault("policy_approvals", {}).setdefault(aget, {})[full] = entry
    for aget, name, change, why in changes:
        rulings = d.setdefault("check_change_rulings", {}).setdefault(aget, {})
        if name in rulings:
            return refuse(f"check_change_rulings[{aget}][{name}] already exists")
        rulings[name] = {"change": change, "line": a.check_line,
                         "source": f"principal, typed, session {a.session} ({why}; recorded by record_authority.py)"}
    if a.dry_run:
        print("dry run: nothing written; would record",
              {"batch": a.key, "held": held, "scopes": list(scopes), "check_changes": [c[:2] for c in changes],
               "baseline_equal": [str(t) for t, _ in be_rulings]})
        return 0
    if a.key or changes or approvals:        # a ruling alone leaves the records file untouched
        Path(records).write_text(json.dumps(d, indent=2, ensure_ascii=True) + "\n")
    for target, ruling in be_rulings:
        target.write_text(json.dumps(ruling, indent=1) + "\n")
    print(f"recorded: batch {a.key}, held {list(held)}, scopes {list(scopes)}, check changes {[c[:2] for c in changes]}"
          + (f", baseline-equal rulings {[t.parent.name for t, _ in be_rulings]}" if be_rulings else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main())
