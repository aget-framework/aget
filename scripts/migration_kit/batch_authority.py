"""Does this batch carry the principal's TYPED authority? READ-ONLY. (carriage row 62; supervisor original 2026-09-30)

Why: a narrow auto-mode allow rule takes `launch_batch.py --launch` and `push_batch.py --push` out of the permission
classifier, which was the only check outside the supervisor. So `push_batch.py --push`, and `launch_batch.py --launch`
when `--copy-root` is NOT given, call this check and refuse (exit 6) unless all of these hold. A `--copy-root` launch
does not call it, and the allow rule covers that command too:

- records.json `batch_authority` has an entry whose key names the batch (keys join batches with `+`, e.g. `10t+10`)
  with a quoted `line`;
- that line starts with the principal line prefix (default `GO supervisor - `; set AGET_MIGRATION_LINE_PREFIX when the
  supervisor Aget has another name) and is at least 30 characters, so a short line such as "GO - yes" matches nothing;
- `check_principal_line.py` finds the recorded line inside a typed prompt of a transcript (exit 0), or inside a
  mid-turn human entry that the harness itself recorded (exit 4, accepted and disclosed); an accepted suggestion
  refuses. For a LAUNCH the recorded line is matched as a SUBSTRING: words typed before or after it are not read by
  the shape and act tests. For a PUSH (F-3, independent review 2026-10-02) the newest prompt that holds the line must
  EQUAL it once runs of whitespace are collapsed: a prompt with other words before or after the line refuses, also
  when an older prompt was the line alone. What is compared is the prompt's own text as
  `check_principal_line.own_text` gives it: a pasted block among other words is left out of the comparison (it is
  read as a quote), and a prompt that is only a paste is compared whole;
- the batch is bound by the TRANSCRIPT, not by records.json (which the supervisor writes): the typed prompt's first
  `batch N` / `batches N and M` list must name the batch, so an entry quoting another batch's line refuses;
- the ACT is tested too (R-F12, rehearsal 2026-09-30: a launch line ending "no push" authorized the push). Each tool
  asks for its own act (`launch`, `push`). A launch reads the batch's line (a per-act entry keyed with the batch key
  and `:launch` wins over it). That line is refused only when a negation word comes before the word launch, at most
  30 characters earlier, with no comma, semicolon, period or colon between ("do not launch"); it need not name the
  launch. A push (F-3) reads ONLY a per-act entry keyed with the batch key and `:push` (e.g. `2:push`, written by
  `record_authority.py --act push`): the batch's line is never push authority, whatever it says. The push line must
  have ONE FIXED FORM (PUSH_FORM below): the prefix, then `push the commits of batch N`, optionally more batches
  (`batches 10t and 10`), optionally ` with commit SHA` (or `commits SHA, SHA and SHA`; 7 to 40 hexadecimal
  characters each), and nothing else. Runs of whitespace are not compared, and after the prefix letter case is not
  compared either; the prefix keeps its letter case. Every other line refuses,
  so "the push is not approved yet", "the push remains unapproved", "the push is prohibited", "the push is held" and
  "push tomorrow" refuse, and so does an affirmative line worded another way ("batch 1, push the verified commits"):
  the principal types the form. This is a test of the line's form, not a reading of meaning. A per-act entry is
  ignored for the other act.

Limit: check() binds the batch's NAME, not the packet. A launch calls check() with only the batch and act,
so another packet with the same batch value passes that launch check; using the rehearsed packet is an operator
rule. A live push instead calls push_authority(): its per-act entry must hold the SHA-256 of the packet's bytes,
recorded by record_authority.py --act push --packet. A different digest refuses even when the batch matches.
A supplied --extra-commit must match a commit named in that recorded push line; omission refuses when the line
names a commit. When HEAD moved since the launch check, the caller compares HEAD with the longer matching id;
with HEAD unchanged, a supplied extra commit does not change the checked commit the gate permits.

The transcript searched is the session named in the entry (`session`, or `session <8 hex>` in its `source`), else every
transcript of this repository. Records live at <root>/data/<slug>_ledger/records.json, as for the other kit tools.
"""
from __future__ import annotations

import json
import os
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import release_target as R  # noqa: E402  (the kit's one release parameter; carriage row 24)

RECORDS = HERE.parents[1] / "data" / f"{R.SLUG}_ledger" / "records.json"
MIN_LINE = 30
ACTS = ("launch", "push")
# An exclusion is read inside one clause: "no problem, launch it" does not exclude the launch. Only a negation word
# BEFORE the act word, at most 30 characters earlier, is read. act_shape() asks this for the launch only (F-3).
NEGATION = r"\b(?:no|not|without|never|don'?t|do not|skip(?:ping)?|hold(?:ing)? off(?: on)?)\b[^,;.:]{0,30}?"
# F-3: a push line, and a baseline-equal ruling line, is accepted only in one fixed form. What follows the prefix must
# match the whole pattern, in any letter case (the prefix itself is matched in its own case), once runs of whitespace are collapsed to one space. The only open
# places take a batch id (digits, optionally one letter) or a commit id (7 to 40 hexadecimal characters), so no other
# word can be put into an accepted line. A list of refused words would accept every withholding worded outside it
# ("the push remains unapproved"; independent review, 2026-10-02), so the test is the form.
_BATCH_ID = r"[0-9]+[a-z]?"
_COMMIT_ID = r"[0-9a-f]{7,40}"
PUSH_FORM = re.compile(rf"push the commits of batch(?:es)? {_BATCH_ID}(?:(?:, | and ){_BATCH_ID})*"
                       rf"(?: with commits? {_COMMIT_ID}(?:(?:, | and ){_COMMIT_ID})*)?", re.I)
PUSH_FORM_TEXT = "push the commits of batch N[ and M][ with commit SHA[, SHA]]"
RULING_FORM = re.compile(rf"the failures at ({_COMMIT_ID}) are baseline-equal", re.I)
RULING_FORM_TEXT = "the failures at SHA are baseline-equal"
# weekly-train:R17: the principal's approval of one member's narrowed suite, bound to the selection the baseline recorded
POLICY_FORM = re.compile(r"the narrowed suite of (\S+) at selection ([0-9a-f]{8,64}) is approved", re.I)
POLICY_FORM_TEXT = "the narrowed suite of AGET at selection DIGEST is approved"
FIRST_BATCHES = re.compile(r"\bbatch(?:es)?\s+([0-9]+[a-z]?(?:\s*(?:,|\band\b|\+|&)\s*[0-9]+[a-z]?)*)", re.I)


def line_prefix() -> str:
    """Return the prefix a principal's batch line must start with (overridable through the environment)."""
    return os.environ.get("AGET_MIGRATION_LINE_PREFIX") or "GO supervisor - "


def excludes(line, act):
    """True when a negation word comes before the act word, at most 30 characters earlier in the same clause
    ("no push", "do not launch", "without pushing"). A negation after the act word, or another withholding phrasing
    ("the push is not approved yet", "hold the push until I review"), returns False. act_shape() asks this for the
    launch only; a push line is tested by form_refusal()."""
    return re.search(NEGATION + rf"\b{act}(?:es|ed|ing)?\b", str(line), re.I) is not None


def after_prefix(line):
    """The line with runs of whitespace collapsed to one space and the principal line prefix taken off, or None when
    it does not start with the prefix."""
    norm, prefix = " ".join(str(line).split()), " ".join(line_prefix().split())
    return norm[len(prefix):].strip() if norm.startswith(prefix) else None


def form_refusal(line, form, text, kind):
    """None when the line starts with the prefix, in the prefix's own letter case, and what follows it matches the
    whole fixed form, in any letter case; else why not. A test of
    form, not a reading of meaning: an affirmative line worded another way is refused too."""
    rest = after_prefix(line)
    if rest is None or not form.fullmatch(rest):
        return (f"the {kind} line is not in the one accepted form, {line_prefix() + text!r} (N a batch id, SHA 7 to "
                "40 hexadecimal characters of a commit id), with nothing before or after it; a line worded any other "
                "way is refused, whatever it means")
    return None


def entry_for(batch, records=RECORDS, act=None):
    """The entry for this batch and act: a `<key>:<act>` entry first, else the batch's own line, except for a push
    (F-3): a push gets only a `<key>:push` entry and never the batch's line. An entry for the other act is never
    returned."""
    auth = (json.loads(Path(records).read_text()).get("batch_authority") or {})
    generic = (None, None)
    for key, e in auth.items():
        base, _, kact = key.partition(":")
        if str(batch) not in base.split("+") or not isinstance(e, dict) or not e.get("line"):
            continue
        if kact and kact == act:
            return key, e
        if not kact and generic[0] is None:
            generic = (key, e)
    return (None, None) if act == "push" else generic


def named_batches(prompt):
    """The batches the typed prompt itself names: its FIRST `batch N` / `batches N and M` list. In
    "batch 12 as batch 10 with ..." that is ['12']; in "batches 10t and 10 as batch 7" it is ['10t', '10']."""
    m = FIRST_BATCHES.search(prompt or "")
    return re.findall(r"[0-9]+[a-z]?", m.group(1).lower()) if m else []


def line_shape(line):
    """None if the line has the required shape, else why not."""
    norm = " ".join(str(line).split())
    if not norm.startswith(line_prefix()) or len(norm) < MIN_LINE:
        return (f"the quoted line must start {line_prefix()!r} and be at least {MIN_LINE} characters "
                "(a short line matches too many prompts)")
    return None


def act_shape(line, act):
    """None if the line may authorize this act, else why not."""
    if act is None:
        return None
    if act not in ACTS:
        return f"unknown act {act!r} (expected one of {ACTS})"
    if act == "push":
        return form_refusal(line, PUSH_FORM, PUSH_FORM_TEXT, "push")
    if excludes(line, act):
        return f"the line excludes {act} (R-F12: a launch line ending 'no push' never authorizes the push)"
    return None


def check(batch, records=RECORDS, projects_dir=None, act=None, *, entry=None):
    """Return (ok, reason): whether the one entry entry_for() picks for this batch and act passes verify(), with the act
    test if an act is given (a launch line need not name the launch). Other entries naming the batch are not tried;
    for a push only a `:push` entry is picked, so a batch with none refuses whatever its own line says."""
    if entry is not None:       # C2a12 (C2b pre-read 2): the (key, entry) the caller read once and goes on to use
        key, e = entry
    else:
        try:
            key, e = entry_for(batch, records, act)
        except (OSError, ValueError) as err:
            return False, f"records unreadable: {err}"
    if not e and act == "push":
        return False, (f"no batch_authority entry keyed with batch {batch!r} and ':push' has a quoted line: a push "
                       "needs its own recorded push line (record_authority.py --act push); the batch's line is never "
                       "used as push authority")
    if not e:
        return False, f"no batch_authority entry names batch {batch!r} with a quoted line"
    return verify(key, e, batch, projects_dir, act)


COMMITS_NAMED = re.compile(rf"\bwith commits? ({_COMMIT_ID}(?:(?:, | and ){_COMMIT_ID})*)", re.I)


def push_authority(batch, packet_sha256, extra_commit=None, records=RECORDS, projects_dir=None, *, bound_out=None):
    """(ok, reason) for a live push (R2-T12, S-163, S-186, S-200): check(act="push"), and the push entry is bound to
    the packet being pushed from (its `packet_sha256`, written by record_authority.py --act push --packet, equals the
    digest of that packet's bytes), so another packet with the same batch number does not inherit the line; and an
    --extra-commit is one the push line names (`with commit SHA`), the shorter id a prefix of the longer.
    C2a12 (FWK-OVSR6's C2b pre-read 1): a full id named in the line was weakened to the command line's 8-character
    prefix, and HEAD was never compared with the named id. With a list `bound_out`, an accepted push appends the
    LONGER of --extra-commit and the named id it matches, so, when HEAD moved since the launch check, the caller tests HEAD against every character the
    principal typed. With HEAD unchanged, the gate still permits the checked commit. The records are read once (C2b pre-read 2)."""
    try:
        entry = entry_for(batch, records, "push")
    except (OSError, ValueError):
        entry = None            # check() reads again and states why the records cannot be read; never accepted
    ok, why = check(batch, records, projects_dir, act="push", entry=entry)
    if not ok:
        return ok, why
    if entry is None:
        return False, "records unreadable"
    key, e = entry
    if not e.get("packet_sha256"):
        return False, (f"batch_authority[{key}] names no packet digest: re-record the push line with "
                       "record_authority.py --act push --packet")
    if e["packet_sha256"] != packet_sha256:
        return False, f"batch_authority[{key}] was recorded for another packet (sha256 differs)"
    bound = None
    if not extra_commit and COMMITS_NAMED.search(str(e["line"])):   # C2a12 (C2a12 pre-read, LOW): never silent
        return False, ("the push line names a commit to push with the batch, but no --extra-commit was given: "
                       "pass it, or record a line that names none")
    if extra_commit:
        m = COMMITS_NAMED.search(str(e["line"]))
        named = re.split(r", | and ", m.group(1).lower()) if m else []
        x = extra_commit.lower()
        hits = [c for c in named if x.startswith(c) or c.startswith(x)]
        if not hits:
            return False, (f"the push line names commit(s) {named or 'none'}, not --extra-commit {extra_commit[:12]}")
        bound = max(hits + [x], key=len)
        if not all(bound.startswith(c) for c in hits + [x]):
            return False, f"--extra-commit {extra_commit[:12]} matches named commits that disagree: {hits}"
    if bound_out is not None:
        bound_out.append(bound)
    return True, why


def verify(key, e, batch, projects_dir=None, act=None):
    """The transcript test for one entry, one batch and (when given) one act (record_authority.py refuses to write
    what this refuses). The shape and act tests read the line AS RECORDED. For a launch, or with no act, the transcript
    test accepts that line as a substring of a typed prompt, so words the principal typed around it are not tested.
    For a push (F-3) the newest prompt that holds the line must equal it after whitespace normalization, own text
    only (see the module docstring), so a condition typed before or after the line refuses."""
    bad = line_shape(e["line"]) or act_shape(e["line"], act)
    if bad:
        return False, f"batch_authority[{key}]: {bad}"
    import check_principal_line as C
    root = Path(projects_dir or C.DEFAULT_DIR)
    m = re.search(r"session ([0-9a-f]{8})", str(e.get("source", "")))
    sid = e.get("session") or (m.group(1) if m else "")
    files = sorted(root.glob(f"{sid}*.jsonl")) if sid else sorted(root.glob("*.jsonl"))
    if not files:
        return False, f"no transcript for session {sid!r} in {root}"
    code, hit = C.check(files, e["line"])
    if code in (0, 4):
        if act == "push" and C.normalize(hit[2]) != C.normalize(str(e["line"])):
            return False, (f"batch_authority[{key}]: the typed prompt is not exactly the recorded push line (other "
                           "words come before or after it); a push line is typed as a whole prompt of its own")
        named = named_batches(hit[2])
        if str(batch).lower() not in named:
            return False, f"batch_authority[{key}]: the typed prompt names batch(es) {named or 'none'}, not {batch!r}"
        for_act = f" for {act}" if act else ""
        return True, f"batch_authority[{key}]{for_act} {provenance(code)} {hit[0]}, naming batch(es) {named}"
    why = {2: "the line is in no principal prompt",
           5: "the line is only in the session's first prompt, which a launch argument also produces (R-F1); "
              "the principal types it again once the session is running"}.get(
        code, f"not typed (promptSource {hit[1]!r})" if hit else "not typed")
    return False, f"batch_authority[{key}]: {why}"


def ruling_names_commit(line, sha):
    """True when the line carries a hex token of 7 or more characters that the commit id starts with."""
    return any(str(sha).lower().startswith(t.lower()) for t in re.findall(r"\b[0-9a-fA-F]{7,40}\b", str(line)))


def verify_ruling(ruling, sha, projects_dir=None):
    """(ok, why) for a baseline-equal ruling (K1, second rehearsal 2026-10-01). The ruling was a file the supervisor
    wrote by hand, and the push tool read it without asking where its line came from. A ruling counts only when its
    line has the principal line shape (the prefix, 30 characters) and is found TYPED in the session's transcript
    (exit 0, or 4 typed mid-turn). F-3: the line must have ONE FIXED FORM (RULING_FORM): the prefix, then
    `the failures at SHA are baseline-equal`, where SHA is 7 to 40 hexadecimal characters that this commit's id
    starts with, and nothing else (runs of whitespace are not compared, nor letter case after the prefix); and the
    newest prompt that
    holds it must equal it after whitespace normalization (own text only). Every other line refuses: "do not treat
    abc1234 as baseline-equal", "abc1234 baseline ruling remains unapproved", and an affirmative ruling worded
    another way. Limits: a test of form, not a reading of meaning, and the member is not named. The
    session is the ruling's `session`, else `session <8 hex>` in its `source` (the shape the rehearsal's hand-written
    file had), else every transcript of this repository."""
    line = (ruling or {}).get("line") or ""
    bad = line_shape(line) or form_refusal(line, RULING_FORM, RULING_FORM_TEXT, "ruling")
    if bad:
        return False, bad
    if not ruling_names_commit(line, sha):
        return False, f"the ruling line does not name the commit {str(sha)[:8]} (7 or more characters of its id)"
    return typed_whole(line, ruling, projects_dir)


def verify_policy(approval, aget, digest, projects_dir=None):
    """(ok, why) for an approval of a member's narrowed suite (weekly-train:R17). The line has the principal line shape
    and ONE FIXED FORM (POLICY_FORM): the prefix, then `the narrowed suite of AGET at selection DIGEST is approved`,
    AGET this member's name and DIGEST 8 to 64 hexadecimal characters that the baseline's selection digest starts
    with; it is found typed in the session's transcript as a whole prompt of its own. A test of form, not of meaning."""
    line = (approval or {}).get("line") or ""
    bad = line_shape(line) or form_refusal(line, POLICY_FORM, POLICY_FORM_TEXT, "approval")
    if bad:
        return False, bad
    m = POLICY_FORM.fullmatch(after_prefix(line))
    if m.group(1).lower() != str(aget).lower():
        return False, f"the approval line names {m.group(1)!r}, not {aget!r}"
    if not str(digest).lower().startswith(m.group(2).lower()):
        return False, f"the approval line names selection {m.group(2)!r}, not the baseline's {str(digest)[:12]}"
    return typed_whole(line, approval, projects_dir)


def typed_whole(line, rec, projects_dir=None):
    """(ok, why): the line is found typed (exit 0, or 4 typed mid-turn) in the session's transcript, and the newest
    prompt holding it equals it (whitespace normalized). Shared by baseline-equal rulings and policy approvals."""
    ruling = rec
    import check_principal_line as C
    root = Path(projects_dir or C.DEFAULT_DIR)
    m = re.search(r"session ([0-9a-f]{8})", str(ruling.get("source", "")))
    sid = ruling.get("session") or (m.group(1) if m else "")
    files = sorted(root.glob(f"{sid}*.jsonl")) if sid else sorted(root.glob("*.jsonl"))
    if not files:
        return False, f"no transcript for session {sid!r} in {root}"
    code, hit = C.check(files, " ".join(line.split()))
    if code in (0, 4):
        if C.normalize(hit[2]) != C.normalize(line):
            return False, ("the typed prompt is not exactly the ruling line (other words come before or after it); "
                           "a ruling line is typed as a whole prompt of its own")
        return True, f"{provenance(code)} {hit[0]}"
    return False, f"the ruling line is not typed in the session (check_principal_line exit {code})"


def provenance(code):
    """How the line reached the transcript, disclosed in every record. Exit 4 is the harness's own evidence (a
    queued_command whose origin kind is human: typed while the session was busy), never a flag the supervisor sets."""
    return "typed" if code == 0 else "typed mid-turn (harness queued_command, origin human; disclosed)"
