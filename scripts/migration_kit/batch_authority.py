"""Does this batch carry the principal's TYPED authority? (carriage row 62; supervisor original 2026-09-30)

Launch checks read the ledger and its anchored permanent scope archive without writing either.

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
- every prompt containing a recorded scope quote refuses launch for EVERY batch. Prompt identity is timestamp and
  normalized full prompt text, never the transcript filename. Scope history is searched across every readable project
  transcript, independently of storage keys, sessions and batch lists. Recognized affirmative scope wording also
  refuses. Any old-format scope entry anywhere in the active ledger refuses every checked launch. The principal
  must confirm the old override no longer applies using --retire-scope (archive before removal); re-recording onto an
  old entry is refused. Current history has a typed line and per-line batches_added covering every entry batch.
  A separate typed launch prompt without a recorded scope quote is required;
- the ACT is tested too (R-F12, rehearsal 2026-09-30: a launch line ending "no push" authorized the push). Each tool
  asks for its own act (`launch`, `push`). A launch reads the batch's line (a per-act entry keyed with the batch key
  and `:launch` wins over it). Its act-shape test refuses when a negation word comes before the word launch, at most
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

import fcntl
import hashlib
import json
import os
import re
import sys
import unicodedata
from pathlib import Path
from datetime import datetime, timezone

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
_SCOPE = r"(?:write[ _-]+)?scopes?"
_DETERMINER = r"(?:(?:the|its|this|their|our|a|an)[ -]+)?"
_SCOPE_CHANGE = r"(?:over-?rid(?:e|es|ing|den)|broaden(?:s|ed|ing)?|expand(?:s|ed|ing)?|extend(?:s|ed|ing)?|widen(?:s|ed|ing)?)"
SCOPE_OVERRIDE = re.compile(
    rf"\bscopes?[ _-]+(?:overrides?|overridden|exceptions?|expansions?|extensions?)\b|"
    rf"\b(?:wider|broader|expanded|extended|broadened|widened)[ -]+{_SCOPE}\b|"
    rf"\b(?:{_SCOPE_CHANGE}|outside|beyond)[ -]+{_DETERMINER}"
    rf"(?:[\w.-]+(?:'s)?[ -]+(?=write[ _-]+))?{_SCOPE}\b|"
    rf"\b{_SCOPE}[ -]+(?:(?:is|are|has been|have been)[ -]+)?{_SCOPE_CHANGE}\b|"
    rf"\bexceptions?[ -]+to[ -]+{_DETERMINER}{_SCOPE}\b|"
    rf"\badd[ -]+[^,;:!?]{{1,80}}?[ -]+to[ -]+{_DETERMINER}{_SCOPE}\b", re.I)
SCOPE_NEGATION = re.compile(
    r"\b(?:no|not|never|without|don't|do not|zero)"
    r"(?: (?:need(?: for)?|grant(?:ing)?|writ(?:e|ing)|allow(?:ing)?))?(?: (?:a|an|any|the))? $", re.I)
SCOPE_DENIAL_TAIL = re.compile(
    r"\s*(?::\s*)?(?:(?:is|are)\s+)?(?:none|not needed|unnecessary)\b|"
    r"(?:\s+(?:from|for)\s+batch\s+[0-9]+[a-z]?)?\s+(?:does not apply|stays closed|remains closed)\b", re.I)


def contains_scope_text(quote, text):
    """Case-sensitive, whitespace-normalized containment with word boundaries at word-bearing quote edges."""
    import check_principal_line as C
    quote = C.normalize(quote)
    if not quote:
        return False
    left = r"(?<!\w)" if re.match(r"\w", quote[0]) else ""
    right = r"(?!\w)" if re.match(r"\w", quote[-1]) else ""
    return re.search(left + re.escape(quote) + right, C.normalize(text)) is not None


def scope_wording(line):
    """Recognized scope grants, with local denials excluded. This is wording detection, not semantic inference.

    Normalize compatibility characters, dash variants and the review's Cyrillic-o spelling of 'scope' only for
    wording detection; prompt identity continues to use whitespace normalization alone.
    """
    text = unicodedata.normalize("NFKC", line).casefold()
    text = " ".join("".join("-" if unicodedata.category(c) == "Pd" else c for c in text).split())
    text = text.replace("scоpe", "scope")
    for match in SCOPE_OVERRIDE.finditer(text):
        if SCOPE_NEGATION.search(text[:match.start()]):
            continue
        tail = text[match.end():]
        if SCOPE_DENIAL_TAIL.match(tail):
            continue
        if match[0].startswith("outside ") and re.match(r" of\b", tail):
            continue
        return True
    return False


def batch_id(batch):
    """Batch names are case-insensitive, including their optional letter suffix."""
    return str(batch).casefold()


def authority_key(key):
    """Normalize only batch names; act spellings remain exact."""
    base, sep, act = key.partition(":")
    return batch_id(base) + sep + act


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
        if batch_id(batch) not in [batch_id(b) for b in base.split("+")] or not isinstance(e, dict) or not e.get("line"):
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
    if act == "launch":
        refusal = scope_launch_refusal(None, batch, records)
        if refusal:
            return False, refusal
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
    return verify(key, e, batch, projects_dir, act, scope_records=records if act == "launch" else None)


def transcript_files(entry, projects_dir=None):
    """Select launch evidence by session; an empty entry selects every project transcript for scope history."""
    import check_principal_line as C
    root = Path(projects_dir or C.DEFAULT_DIR)
    m = re.search(r"session ([0-9a-f]{8})", str(entry.get("source", "")))
    sid = entry.get("session") or (m.group(1) if m else "")
    return sorted(root.glob(f"{sid}*.jsonl")) if sid else sorted(root.glob("*.jsonl"))


ARCHIVE_REVERSE_MIN = 24


class ScopeArchiveError(ValueError):
    """An unreadable or unwritable archive cannot be ignored by a launch or scope mutation."""


SYMLINK_REMEDY = ("replace the symlink with the real file/directory; "
                   "the ledger and archive must live in the kit's data directory")


def lexical_absolute(path):
    """Make an absolute path without resolving links or removing parent traversals."""
    path = Path(path)
    return path if path.is_absolute() else Path.cwd() / path


def refuse_scope_symlinks(path, root):
    """Check each component from the lexical root down, including dangling links.

    A resolved-path comparison also catches links in ancestors of the configured root. Test archive overrides
    may be outside the root; in that case check their entire path as well.
    """
    path, root = lexical_absolute(path), lexical_absolute(root)
    base = root if path.is_relative_to(root) else Path(path.anchor)
    current = base
    for component in (None, *path.relative_to(base).parts):
        if component is not None:
            current = current / component
        if os.path.islink(current):
            raise ScopeArchiveError(f"symlink at {current}; {SYMLINK_REMEDY}")
    try:
        resolved = path.resolve()
    except (OSError, RuntimeError) as err:
        raise ScopeArchiveError(f"cannot resolve lexical path {path} (symlink); {SYMLINK_REMEDY}") from err
    if path != resolved:
        raise ScopeArchiveError(f"lexical path {path} differs from its resolved path (symlink); {SYMLINK_REMEDY}")


def scope_ledger_location(records=RECORDS):
    """Shared gate/recorder location predicate: production is confined to the configured kit data directory."""
    active = lexical_absolute(records)
    test_mode = os.environ.get("AGET_MIGRATION_TEST_MODE") == "1"
    root = active.parent.parent if test_mode else lexical_absolute(HERE.parents[1] / "data")
    relative = active.relative_to(root) if active.is_relative_to(root) else None
    if (".." in active.parts or (not test_mode and
            (relative is None or len(relative.parts) != 2 or not relative.parts[0].endswith("_ledger")
             or relative.parts[1] != "records.json"))):
        raise ScopeArchiveError(f"active records path {active} must be <root>/<name>_ledger/records.json "
                                f"lexically, without '..', under {root}; the ledger and archive must live "
                                "in the kit's data directory")
    refuse_scope_symlinks(root, root)
    refuse_scope_symlinks(active, root)
    return active, root


def scope_archive_path(records=RECORDS, document=None):
    """Production always uses the ledger root's archive; overrides and other paths are test-only."""
    active, root = scope_ledger_location(records)
    base = active.parent
    if document is None:
        document = scope_ledger_snapshot(active)[0]
    anchor = document.get("scope_archive_anchor")
    relative = "../scope_archive.jsonl"
    test_mode = os.environ.get("AGET_MIGRATION_TEST_MODE") == "1"
    if anchor is not None:
        if (not test_mode and isinstance(anchor, dict)
                and (not isinstance(anchor.get("path"), str)
                     or Path(os.path.abspath(base / anchor["path"])) != root / "scope_archive.jsonl")):
            raise ScopeArchiveError("anchor path is not the ledger root's archive; restore the anchor")
        if (not isinstance(anchor, dict) or not isinstance(anchor.get("path"), str)
                or not anchor["path"] or Path(anchor["path"]).is_absolute()
                or type(anchor.get("rows")) is not int or anchor["rows"] < 0
                or not isinstance(anchor.get("chain"), str)
                or not (re.fullmatch(r"[0-9a-f]{64}", anchor["chain"])
                        if anchor["rows"] else anchor["chain"] == "")):
            raise ScopeArchiveError("invalid scope_archive_anchor; restore records.json and scope archive "
                                    "together from the last intact committed pair")
        relative = anchor["path"]
    bound = Path(os.path.abspath(base / relative))
    override = os.environ.get("AGET_MIGRATION_SCOPE_ARCHIVE") if test_mode else None
    chosen = Path(os.path.abspath(base / override)) if override else bound
    refuse_scope_symlinks(bound, root)
    refuse_scope_symlinks(chosen, root)
    if anchor is not None and chosen != bound:
        raise ScopeArchiveError(f"scope archive path {chosen} differs from anchor path {bound}; "
                                "remove the test override or set it to the anchored path")
    if chosen == active:
        raise ScopeArchiveError("scope archive must be separate from records.json; restore the anchor's "
                                "separate regular archive file and its committed records.json")
    if chosen.exists() and not chosen.is_file():
        raise ScopeArchiveError(f"scope archive {chosen} is not a regular file; restore the regular archive "
                                "and records.json together; remove any invalid test override")
    return chosen


def archive_json(value):
    """Canonical UTF-8 JSON used for both the content and complete-row hashes."""
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=True)


def archive_hash(value):
    return hashlib.sha256(archive_json(value).encode("utf-8")).hexdigest()


def scope_raw_fields(value, path=""):
    """Every string value, unchanged, indexed by JSON pointer (also retains malformed/old nested fields)."""
    if isinstance(value, str):
        return {path: value}
    fields = {}
    items = value.items() if isinstance(value, dict) else enumerate(value) if isinstance(value, list) else []
    for key, child in items:
        escaped = str(key).replace("~", "~0").replace("/", "~1")
        fields.update(scope_raw_fields(child, path + "/" + escaped))
    return fields


ARCHIVE_RESTORE = ("restore scope_archive.jsonl and records.json together from the last intact committed pair; "
                   "for a torn/corrupt tail, preserve the damaged file separately and recover the complete "
                   "archive from committed copies and source ledgers before --anchor-archive; never drop evidence")


def archive_chain(rows):
    """Genesis is the empty string; concatenate lowercase hex digests as ASCII at each step."""
    chain = ""
    for row in rows:
        chain = hashlib.sha256((chain + row["sha256"]).encode("ascii")).hexdigest()
    return chain


def read_archive_rows(stream):
    rows = []
    for number, line in enumerate(stream, 1):
        if not line.endswith("\n"):
            raise ValueError(f"incomplete row {number}")
        row = json.loads(line)
        if not isinstance(row, dict):
            raise ValueError(f"invalid row {number}")
        payload = {k: v for k, v in row.items() if k != "sha256"}
        if row.get("sha256") != archive_hash(payload):
            raise ValueError(f"sha256 mismatch at row {number}")
        # Older rows retain their original hash and taint. New rows use a portable relative ledger identity;
        # the absolute source remains provenance in the row hash, never in the new content hash.
        content = {"ledger": row.get("ledger_relative", row["ledger"]), "aget": row["aget"], "entry": row["entry"]}
        if (not isinstance(row.get("recorded_at"), str)
                or row.get("content_sha256") != archive_hash(content)
                or row.get("fields") != scope_raw_fields(row["entry"])
                or row.get("batches") != (row["entry"].get("batches", [])
                                         if isinstance(row["entry"], dict) else [])):
            raise ValueError(f"invalid content at row {number}")
        rows.append(row)
    return rows


# One current version per path, local to this process. Every check still enumerates the root and stats its files.
_scope_ledger_cache = {}
_scope_archive_cache = {}


def scope_ledger_snapshot(records):
    """Cache parsed documents and portable content hashes after checking the lexical location on every call."""
    path, root = scope_ledger_location(records)
    try:
        stat = path.stat()
        signature = (stat.st_mtime_ns, stat.st_size)
        cached = _scope_ledger_cache.get(path)
        if cached is None or cached[0] != signature:
            doc = json.loads(path.read_text())
            if not isinstance(doc, dict):
                raise ValueError("records.json is not a mapping")
            ovs = doc.get("scope_overrides", {})
            digests = tuple(archive_hash({"ledger": str(path.relative_to(root)), "aget": aget, "entry": ov})
                            for aget, ov in ovs.items()) if isinstance(ovs, dict) else ()
            cached = (signature, doc, digests)
            _scope_ledger_cache[path] = cached
    except (OSError, ValueError, RecursionError) as err:
        raise ScopeArchiveError(f"scope ledger {path}: {err}; repair or move it out of the data folder") from err
    return cached[1], cached[2]


def archive_index(rows, *, root=None):
    """Content membership and every rolling prefix, computed once per archive version."""
    prefixes = [""]
    seen = {row["content_sha256"] for row in rows}
    for row in rows:
        prefixes.append(hashlib.sha256((prefixes[-1] + row["sha256"]).encode("ascii")).hexdigest())
        if root is not None and "ledger_relative" not in row:
            source = Path(row["ledger"])
            # Preserve seeded legacy rows at their original root, without treating foreign sources as local.
            # Only explicit seeding appends a portable row; archived history and prefix hashes stay intact.
            if source.is_absolute() and source.is_relative_to(root):
                seen.add(archive_hash({"ledger": str(source.relative_to(root)),
                                       "aget": row["aget"], "entry": row["entry"]}))
    return seen, prefixes


def scope_archive_snapshot(archive, stream, *, root):
    """Called under the archive lock; never cache an absent archive or a failed validation."""
    stat = os.fstat(stream.fileno())
    signature = (stat.st_mtime_ns, stat.st_size, root)
    cached = _scope_archive_cache.get(archive)
    if cached is None or cached[0] != signature:
        rows = read_archive_rows(stream)
        cached = (signature, rows, archive_index(rows, root=root))
        _scope_archive_cache[archive] = cached
    return cached[1], cached[2]


def validate_root_archive(records, archive, rows, *, complete=True, index=None):
    """Shared root predicate. Launches require all raw entries; recorder recovery checks all anchors.

    Enumerate <root>/*_ledger/records.json plus the active ledger on every call. Cold cost is linear in directory
    entries, ledger/archive bytes and scope entries. Warm cost is directory enumeration, O(L) stats/path checks and
    O(E) cached-hash membership checks (L ledgers, E scope entries); prefix checks are O(1) per anchor. New, changed
    and missing files are always reconsidered. Seeding may be incremental, but cannot bless a lost anchored prefix.
    """
    active, root = scope_ledger_location(records)
    paths = set()
    for directory in root.glob("*_ledger"):
        # Check the directory before looking for records.json: even an empty or dangling linked sibling refuses.
        refuse_scope_symlinks(directory, root)
        path = directory / "records.json"
        refuse_scope_symlinks(path, root)
        if path.exists():
            paths.add(path)
    seen, prefixes = index if index is not None else archive_index(rows, root=root)
    unseeded = []
    # Check siblings first so a fresh active ledger cannot hide a previous ledger's loss.
    for path in [*sorted(paths - {active}), active]:
        try:
            doc, digests = scope_ledger_snapshot(path)
            bound = scope_archive_path(path, doc)
            if bound != archive:
                raise ScopeArchiveError("ledger archive differs from the active root archive; restore the anchor")
            anchor = doc.get("scope_archive_anchor")
            if anchor is not None:
                if not archive.exists():
                    raise ScopeArchiveError(f"archive is missing while ledger {path} has an anchor; {ARCHIVE_RESTORE}")
                if len(rows) < anchor["rows"]:
                    raise ScopeArchiveError(f"archive shorter than ledger {path}'s anchor "
                                            f"({len(rows)} < {anchor['rows']}); {ARCHIVE_RESTORE}")
                if prefixes[anchor["rows"]] != anchor["chain"]:
                    raise ScopeArchiveError(f"archive chain does not match ledger {path}'s anchor; {ARCHIVE_RESTORE}")
            ovs = doc.get("scope_overrides", {})
            if complete and ((not isinstance(ovs, dict) and ovs) or any(h not in seen for h in digests)):
                unseeded.append(path)
        except (OSError, ValueError, TypeError, KeyError, RecursionError) as err:
            raise ScopeArchiveError(f"scope ledger {path}: {err}; restore the ledger and archive") from err
    if unseeded:
        commands = "; ".join(f"record_authority.py --archive-ledger {path}" for path in unseeded)
        missing = "scope archive is absent; " if not archive.exists() else ""
        raise ScopeArchiveError(f"{missing}unseeded scope history in ledger(s) {', '.join(map(str, unseeded))}; "
                                f"run {commands}")


def validate_archive_anchor(doc, archive, rows, *, reanchor=False, initialize=False, prefixes=None):
    anchor = doc.get("scope_archive_anchor")
    if anchor is None:
        if reanchor or initialize:
            return
        if archive.exists():
            raise ScopeArchiveError("scope archive has no ledger anchor; run record_authority.py --anchor-archive "
                                    "against the active ledger after verifying the complete archive")
        if doc.get("scope_overrides"):
            raise ScopeArchiveError("scope_overrides history has no scope_archive_anchor; run "
                                    "record_authority.py --archive-ledger <active records.json> to seed and anchor it")
        return
    if not archive.exists():
        raise ScopeArchiveError(f"anchored scope archive {archive} is missing; {ARCHIVE_RESTORE}")
    if len(rows) < anchor["rows"]:
        raise ScopeArchiveError(f"scope archive is shorter than anchor ({len(rows)} < {anchor['rows']}); {ARCHIVE_RESTORE}")
    chain = prefixes[anchor["rows"]] if prefixes is not None else archive_chain(rows[:anchor["rows"]])
    if chain != anchor["chain"]:
        raise ScopeArchiveError(f"scope archive chain mismatched; {ARCHIVE_RESTORE}")
    if len(rows) > anchor["rows"] and not reanchor:
        raise ScopeArchiveError("scope archive has extra rows after the anchor (possible interrupted ledger write); "
                                "verify the complete archive, then re-anchor with record_authority.py --anchor-archive")


def read_scope_archive(records=RECORDS, document=None):
    """Read-only gate path: never creates a file, directory, row or anchor."""
    try:
        _, root = scope_ledger_location(records)
        doc = document if document is not None else scope_ledger_snapshot(records)[0]
        archive = scope_archive_path(records, doc)
        rows = []
        if archive.exists():
            with archive.open("r", encoding="utf-8") as stream:
                fcntl.flock(stream.fileno(), fcntl.LOCK_SH)
                rows, index = scope_archive_snapshot(archive, stream, root=root)
                validate_root_archive(records, archive, rows, index=index)
                validate_archive_anchor(doc, archive, rows, prefixes=index[1])
        else:
            validate_root_archive(records, archive, rows)
            validate_archive_anchor(doc, archive, rows)
        return rows
    except ScopeArchiveError:
        raise
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as err:
        raise ScopeArchiveError(f"scope archive: {err}; {ARCHIVE_RESTORE}") from err


def write_scope_records(records, doc):
    """Replace the ledger durably, after its archive has been fsynced."""
    import tempfile
    target, _ = scope_ledger_location(records)
    scope_archive_path(records, doc)
    fd, name = tempfile.mkstemp(prefix=".records-", dir=target.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            stream.write(json.dumps(doc, indent=2, ensure_ascii=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())
        os.replace(name, target)
        directory = os.open(target.parent, os.O_RDONLY)
        try:
            os.fsync(directory)
        finally:
            os.close(directory)
    finally:
        if os.path.exists(name):
            os.unlink(name)


def scope_archive_rows(ovs, records=RECORDS, *, document=None, source_records=None, previous=None,
                       reanchor=False, dry_run=False):
    """Recorder transaction: validate, append/fsync archive, then save its anchor and ledger under the lock.

    Returns the number actually appended (or that would be appended for a dry run). Re-anchoring only accepts
    additional verified rows; it can never bless a missing, shorter or mismatched anchored prefix.
    """
    may_have_appended = False
    recovery = ("; a scope archive row may have been appended; verify the complete archive, then re-anchor "
                "with record_authority.py --anchor-archive")
    try:
        active, root = scope_ledger_location(records)
        doc = document if document is not None else json.loads(Path(records).read_text())
        archive = scope_archive_path(records, doc)
        exists = archive.exists()
        if not exists:
            validate_root_archive(records, archive, [], complete=False)
        if reanchor and not exists:
            raise ScopeArchiveError(f"scope archive {archive} is missing; {ARCHIVE_RESTORE}")
        if not exists and not dry_run:
            archive.parent.mkdir(parents=True, exist_ok=True)
        # Dry runs use read mode and never create even an empty archive.
        import contextlib
        opener = archive.open("r" if dry_run else "a+", encoding="utf-8") if exists or not dry_run else contextlib.nullcontext(None)
        with opener as stream:
            if stream is not None:
                fcntl.flock(stream.fileno(), fcntl.LOCK_SH if dry_run else fcntl.LOCK_EX)
                stream.seek(0)
            rows = read_archive_rows(stream) if stream is not None else []
            validate_root_archive(records, archive, rows, complete=False)
            # Explicit seeding also initializes a fresh ledger against an already existing, verified archive.
            initialize = not exists or (source_records is not None and doc.get("scope_archive_anchor") is None)
            validate_archive_anchor(doc, archive, rows, reanchor=reanchor, initialize=initialize)
            seen = {row["content_sha256"] for row in rows}
            appended = 0
            sources = [(records, previous or {}), (source_records or records, ovs)]
            for source, entries in sources:
                if not isinstance(entries, dict):
                    raise ValueError("scope_overrides is not a mapping")
                for aget, ov in entries.items():
                    source_path = lexical_absolute(source)
                    content = {"ledger": os.path.relpath(source_path, root), "aget": aget, "entry": ov}
                    digest = archive_hash(content)
                    if digest in seen:
                        continue
                    row = {**content, "ledger": str(source_path), "ledger_relative": content["ledger"],
                           "content_sha256": digest,
                           "recorded_at": datetime.now(timezone.utc).isoformat(),
                           "batches": ov.get("batches", []) if isinstance(ov, dict) else [],
                           "fields": scope_raw_fields(ov)}
                    row["sha256"] = archive_hash(row)
                    if not dry_run:
                        may_have_appended = True
                        stream.write(archive_json(row) + "\n")
                    rows.append(row)
                    seen.add(digest)
                    appended += 1
            if not dry_run:
                stream.flush()
                os.fsync(stream.fileno())
                anchor_path = (os.path.relpath(archive, active.parent)
                               if os.environ.get("AGET_MIGRATION_TEST_MODE") == "1" else "../scope_archive.jsonl")
                doc["scope_archive_anchor"] = {"path": anchor_path,
                                               "rows": len(rows), "chain": archive_chain(rows)}
                write_scope_records(records, doc)
            return appended
    except ScopeArchiveError as err:
        if may_have_appended:
            raise ScopeArchiveError(str(err) + recovery) from err
        raise
    except (OSError, ValueError, TypeError, KeyError, RecursionError) as err:
        raise ScopeArchiveError(f"scope archive: {err}; {ARCHIVE_RESTORE}" +
                                (recovery if may_have_appended else "")) from err


def archived_scope_refusal(line, rows):
    """Permanent taint across ledgers and batches. Reverse containment needs >=24 normalized characters:
    short/trivial prompts would otherwise match incidental metadata in almost any raw field.
    """
    import check_principal_line as C
    text = C.normalize(line)
    for row in rows:
        ov = row["entry"]
        history = ov.get("history", []) if isinstance(ov, dict) else []
        if isinstance(history, list):
            for h in history:
                if isinstance(h, dict) and isinstance(h.get("line"), str) and contains_scope_text(h["line"], text):
                    return f"scope-override evidence from scope archive for {row['aget']}: history quote in prompt"
        if len(text) >= ARCHIVE_REVERSE_MIN and any(text in C.normalize(raw) for raw in row["fields"].values()):
            return f"scope-override evidence from scope archive for {row['aget']}: full prompt in raw field"
    return None


def scope_format_refusal(ovs, records=RECORDS):
    """One format predicate for the launch gate and recorder; no conversion of old scope entries.

    Every history item needs its line. Recorded batch lists together must cover the entry's batches.
    Empty batches_added is valid for a later scope line that adds no batches to an already current entry.
    """
    if not isinstance(ovs, dict):
        return "unreadable scope history: scope_overrides is not a mapping"
    old_keys = [
        key for key, ov in ovs.items()
        if not (isinstance(ov, dict) and isinstance(ov.get("batches"), list)
                and isinstance(ov.get("history"), list) and ov["history"]
                and all(isinstance(h, dict) and isinstance(h.get("line"), str) and h["line"].strip()
                        for h in ov["history"])
                and {batch_id(b) for b in ov["batches"]}
                <= {batch_id(b) for h in ov["history"] if isinstance(h.get("batches_added"), list)
                    for b in h["batches_added"]})
    ]
    if old_keys:
        commands = "; ".join(f'record_authority.py --session <id> --retire-scope {key} '
                             f'--principal-line "{line_prefix()}the old scope override for {key} no longer applies"'
                             for key in old_keys)
        return (f"old-format scope_overrides entries: {', '.join(repr(key) for key in old_keys)}; "
                "ask the principal to confirm the old scope override no longer applies, then run "
                f"{commands} against {records}. Retirement archives the raw entry before removing it. "
                "Record fresh scope under an unused batch key if needed, and launch from a separate typed prompt; "
                "archived scope quotes remain tainted permanently")
    return None


def scope_launch_refusal(line, batch, records=RECORDS, *, identity=None, projects_dir=None):
    """Return a scope refusal or None, shared by recorder and launch gate.

    Every prompt containing a scope quote is tainted, including earlier/later matches and transcript copies.
    Pins verify history; they never narrow taint. Old filename-bearing pins compare by timestamp and text only.
    Any old-format entry blocks ALL launches, before wording, keys or transcript checks.
    Pass line=None to check the archive anchor and ledger format. With all-current entries, unverifiable history
    fails closed for its governed batches, while positive evidence taints across ALL batches.
    Record every scope prompt and type launch separately: neutral, unrecorded scope instructions cannot be inferred.
    """
    try:
        ovs = scope_ledger_snapshot(records)[0].get("scope_overrides", {})
    except ScopeArchiveError as err:
        return str(err)
    except (OSError, ValueError, AttributeError):
        return "unreadable scope history in records.json"
    if not isinstance(ovs, dict):
        return scope_format_refusal(ovs, records)
    try:
        archived = read_scope_archive(records)
    except ScopeArchiveError as err:
        return str(err)
    refusal = scope_format_refusal(ovs, records)
    if refusal:
        return refusal
    if line is None:
        return None
    import check_principal_line as C
    if scope_wording(line):
        return "scope-override evidence in the prompt's wording"
    refusal = archived_scope_refusal(line, archived)
    if refusal:
        return refusal
    project_prompts = None
    for aget, ov in ovs.items():
        governed = batch_id(batch) in [batch_id(b) for b in ov["batches"]]
        evidence = [(f"{aget} history[{i}]", h) for i, h in enumerate(ov["history"])]
        for where, h in evidence:
            quote = C.normalize(h["line"])
            if contains_scope_text(quote, line):
                return f"scope-override evidence from {where} in the launch prompt"
            if project_prompts is None:
                project_prompts = []
                for f in transcript_files({}, projects_dir):
                    try:
                        project_prompts.extend(C.prompt_identity(f, p) for p in C.prompts(f)
                                               if p[1] in ("typed", C.QUEUED_HUMAN))
                    except (OSError, ValueError, AttributeError, TypeError):
                        continue  # only readable project transcripts; missing evidence is handled below
            matches = [p for p in project_prompts if contains_scope_text(quote, p["text"])]
            if identity in matches:
                return f"scope-override evidence from {where} in the launch prompt"
            bound = h.get("prompt")
            if "prompt" in h:
                if (isinstance(bound, dict) and isinstance(bound.get("timestamp"), str)
                        and isinstance(bound.get("text"), str)):
                    bound = {"timestamp": bound["timestamp"], "text": C.normalize(bound["text"])}
                if bound == identity:
                    return f"scope-override evidence pinned by {where}"
                if governed and bound not in matches:
                    return f"unverifiable scope history for {where}: pinned prompt not found across project transcripts"
            elif governed and not matches:
                return f"unverifiable scope history for {where}: quote not found across project transcripts"
    return None


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


def verify(key, e, batch, projects_dir=None, act=None, *, scope_records=None):
    """The transcript test for one entry, one batch and (when given) one act (record_authority.py refuses to write
    what this refuses). The shape and act tests read the line AS RECORDED. For a launch, or with no act, the transcript
    test accepts that line as a substring of a typed prompt. With launch scope records, the scope predicate reads
    the full matched prompt, including words around the quote; other shape and act tests read the recorded line.
    For a push (F-3) the newest prompt that holds the line must equal it after whitespace normalization, own text
    only (see the module docstring), so a condition typed before or after the line refuses."""
    if act == "launch" and scope_records is not None:
        refusal = scope_launch_refusal(None, batch, scope_records)
        if refusal:
            return False, f"batch_authority[{key}]: {refusal}"
    bad = line_shape(e["line"]) or act_shape(e["line"], act)
    if bad:
        return False, f"batch_authority[{key}]: {bad}"
    import check_principal_line as C
    files = transcript_files(e, projects_dir)
    if not files:
        return False, f"no transcript for session {e.get('session')!r} in {Path(projects_dir or C.DEFAULT_DIR)}"
    identities, errors = [], []
    code, hit = C.check(files, e["line"], identity_out=identities, errors_out=errors)
    if errors:
        return False, f"batch_authority[{key}]: {'; '.join(errors)}"
    if code in (0, 4):
        if act == "launch" and scope_records is not None:
            refusal = scope_launch_refusal(hit[2], batch, scope_records, identity=identities[0], projects_dir=projects_dir)
            if refusal:
                return False, (f"batch_authority[{key}]: {refusal}; scope-override evidence never authorizes launch. "
                               "Use a separate typed launch prompt (record_authority.py --act launch); "
                               "if history is unverifiable, restore its transcript or repair that history first")
        if act == "push" and C.normalize(hit[2]) != C.normalize(str(e["line"])):
            return False, (f"batch_authority[{key}]: the typed prompt is not exactly the recorded push line (other "
                           "words come before or after it); a push line is typed as a whole prompt of its own")
        named = named_batches(hit[2])
        if batch_id(batch) not in named:
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
    errors = []
    code, hit = C.check(files, " ".join(line.split()), errors_out=errors)
    if errors:
        return False, "; ".join(errors)
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
