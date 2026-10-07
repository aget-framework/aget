#!/usr/bin/env python3
"""Prepare a batch's receiver launch packet (route a1 + b1 `route-b-restricted-hooks`, detective check).

It reads each named receiver's working tree and git state. It writes the packet to the path named with --out, with
--apply-list an apply list to the path named there, and the stage folder described below, beside the --out packet under
<packet folder>/<release>/packets/ (AGET_MIGRATION_PACKET_BASE overrides). Keep --out and --apply-list outside the named receivers' repositories (operator rule, not enforced by
the tool).

For each receiver:
  - classifies every UNPROTECTED payload path, except the version carriers (.aget/version.json, manifest.yaml,
    README.md, CHANGELOG.md: skipped, not classified, not placed), against its working tree, as prepare_batch.py does
    for the protected ones: write / write-upstream (byte for byte an upstream version) / noop / hold (the receiver's
    own lines or changes: merge, keep them) / unsafe (the path is or goes through a symbolic link: left, not
    migrated) / delete / hold-delete;
  - SOURCES each path from the release: the correction-row-4 paths (`wave_readiness.CORRECTION_ROW_4`) from the CORE
    tag, not the template (release correction row 4; batch 1 took the guard script from the template,
    supervisor:L836), every other path from the template tag if it has it, else from core. A --resolved-file entry
    for one of that receiver's item paths sets the item's recorded `source` to the `repo@rev:path` it names and its
    sha256 to the digest of those bytes; that step leaves the item's `staged` path as it was and writes no `cp`
    command;
  - DERIVES the import closure: every file the installed .py files import or name (quoted paths, joined path segments
    such as REPO / "tests" / "fixtures" / "x.json", and imports) that exists at the release but is not in the payload
    (batch 1 omitted tests/fixtures/l980_session_2026_05_21_action_batch.json). Never hand-listed;
  - stages the release bytes and documents in one folder under the packet base (the tool does not make
    the folder read-only and does not check that git ignores it; the settings files and, later, launch_batch.py's
    baselines are written there too);
  - gives each write / write-upstream item a DECLARED EXACT command (`cp -f <staged> <path>`) that a migrating or repair
    prompt tells the member to run, and the prompt tells the member not to re-type the file (batch 1's re-typed test
    lost its trailing whitespace at three receivers). With --placed-by-apply the copy command is removed: the item is
    marked as placed by the principal's apply_protected.py and the prompt gives a hash command only (this tool does
    not check that the files were placed). A --resolved-file item that had no copy command (a hold, for one) gets
    none. A track-skills prompt lists no placing command;
  - declares the validation commands a receipt may run, each verbatim: three FIXED commands (VALIDATION) written for
    the 3.35.0 features, told to every migrating and repair member whatever the target release (a track-skills
    member is allowed them but not told to run them);
  - tells a migrating member to record a route text in its version history and receipt, and a repair member in its
    receipt only: the default ROUTE (a batch 1 label) unless --route is passed (a track-skills prompt carries no route);
  - writes the per-receiver `--settings` file carrying the receiver's OWN project hooks and no allow rules
    (route-b-restricted-hooks, ruled 2026-09-27), and the launch deny list.
`--repair` (batch 1): the receivers already hold a local migration commit. The packet lists only the files whose bytes
differ from the release (plus missing closure files), and marks the already-correct ones `verify`, so the after-run
check (D) compares those files with the release bytes too, not only the repaired ones (D does not compare a merged or
held file, and the version carriers are not items).

Usage (repository root):
    python3 scripts/migration_kit/prepare_launch.py --out <packet.json> --receipt <apply.json>
        [--repair] NAME [NAME ...]
"""
import argparse
import sys
import datetime as dt
import importlib.util
import json
import os
import re
import subprocess
import tempfile
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_target as R  # noqa: E402  (the kit's one release parameter; carriage row 24)
import result_binding as RBND  # noqa: E402  (R2: receipt path and terminals, one source)
import item_meaning as IM  # noqa: E402  (R3: one meaning table per classification)
import copy_isolation as CI  # noqa: E402  (destination_refusal: a write never goes through a link)
import place_file as PF  # noqa: E402  (E2i15: the one no-follow working-tree reader)

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
_s = importlib.util.spec_from_file_location("prepare_batch", HERE / "prepare_batch.py")
P = importlib.util.module_from_spec(_s)
_s.loader.exec_module(P)
L = P.L
W = L.W
_a = importlib.util.spec_from_file_location("apply_protected", HERE / "apply_protected.py")
A = importlib.util.module_from_spec(_a)
_a.loader.exec_module(A)   # read-only use: its release_bytes() is how a list's `source` is read, so both agree
# R1 clause 1(d) and 5 (D-3 of design read 1): each packet gets a fresh root PR under packet_base(--out), outside
# every repository; it holds the sealed stage (PR/stage) and one open baseline slot per receiver (PR/baselines/<aget>/).
# The old fixed stage inside this repository's working tree (shared by every batch, not git-ignored) is gone.
PACKET_BASE = Path(os.environ["AGET_MIGRATION_PACKET_BASE"]) if os.environ.get("AGET_MIGRATION_PACKET_BASE") else None
PACKET_ROOT = None      # set by main(): this packet's root
STAGE = None            # set by main(): PACKET_ROOT / "stage"
CORE_DOCS = [f"handoffs/RELEASE_HANDOFF_{R.TO_TAG}.md", f"handoffs/REMOTE_MIGRATION_MESSAGE_{R.TO_TAG}.md",
             f"DEPLOYMENT_SPEC_{R.TO_TAG}.yaml"]
CARRIERS = [".aget/version.json", "manifest.yaml"]
ALLOWED_BASH = ["git add", "git commit", "git rm", "python3 -m pytest"]


def packet_base(out):
    """Explicit packet-base override, or a release folder beside this batch's --out file (R55 P5)."""
    return PACKET_BASE if PACKET_BASE is not None else Path(out).resolve().parent / R.SLUG / "packets"


# The commands the batch 1 receipts used for behaviour evidence (after-run C, 2026-09-27), declared verbatim. They are
# fixed and were written for the 3.35.0 features: every migrating and repair member is told to run these three, whatever the target
# release (a track-skills member is allowed them but not told to run them).
VALIDATION = ["python3 scripts/propose_actions_handoff_scan.py --self-test",
              "python3 scripts/propose_actions_classify.py --self-test",
              "python3 scripts/close_gate_check.py --help"]
TOOLS = "Bash,Read,Edit,Write,Glob,Grep"
DENY = ["Bash(git push:*)", "Bash(git push *)", "Bash(gh:*)", "Bash(gh *)"]
ROUTE = "a1 + b1 route-b-restricted-hooks (detective), batch 1"
TERMINALS = ", ".join(RBND.TERMINALS)   # R2: the tuple lives in result_binding; joined here for display only
EXT = r"(?:py|ya?ml|json|md|txt|toml)"
QUOTED_PATH = re.compile(r"['\"]((?:[\w.-]+/)*[\w.-]+\." + EXT + r")['\"]")
JOINED = re.compile(r"(?:['\"][\w.-]+['\"]\s*/\s*)+['\"][\w.-]+\." + EXT + r"['\"]")
SEGMENT = re.compile(r"['\"]([\w.-]+)['\"]")
IMPORT = re.compile(r"^\s*(?:import|from)\s+([A-Za-z_]\w*)", re.M)
NEVER_CLOSURE = set(W.VERSION_FILES) | {"CLAUDE.md"}


def pin(repo):
    """Return the commit that the target release tag points to in the repository."""
    return subprocess.run(["git", "-C", str(repo), "rev-parse", f"{R.TO_TAG}^{{commit}}"], capture_output=True,
                          text=True).stdout.strip()


def source_repo(path, tpl_repo, core):
    """Correction row 4 always comes from core; otherwise the template if it ships the path, else core."""
    if path in W.CORRECTION_ROW_4:
        return core
    return tpl_repo if P.tag_bytes(tpl_repo, R.TO_TAG, path) is not None else core


def stage(src_repo, path):
    """Copy a path's bytes at the target tag into the stage folder; return (staged path, digest), or (None, None)."""
    source = CI.git_blob_at(src_repo, R.TO_TAG, path, with_mode=True)
    if source is None:
        return None, None
    data, mode = source
    CI.contained_write(STAGE, f"{src_repo.name}/{path}", data, mode=mode)  # bytes and executable bit from release
    return STAGE / src_repo.name / path, P.sha_bytes(data)


def references(path, text):
    """Relative paths a .py file names or imports (candidates; resolved against the release by the caller)."""
    names = set(QUOTED_PATH.findall(text))
    for m in JOINED.finditer(text):
        names.add("/".join(SEGMENT.findall(m.group(0))))
    names |= {f"{mod}.py" for mod in IMPORT.findall(text)}
    base = str(Path(path).parent)
    out = set()
    for n in names:
        out |= {n, f"scripts/{n}", f"{base}/{n}"}
    return {os.path.normpath(c) for c in out if not c.startswith("/") and ".." not in c}


def closure(payload, tpl_repo, core):
    """{path: source repo} for files the payload's .py files need, present at the release, absent from the payload.
    Transitive over .py files it adds."""
    found, queue = {}, [p for p in payload if p.endswith(".py")]
    seen = set(queue)
    while queue:
        path = queue.pop()
        src = source_repo(path, tpl_repo, core)
        data = P.tag_bytes(src, R.TO_TAG, path)
        if data is None:
            continue
        for cand in sorted(references(path, data.decode("utf-8", "replace"))):
            if cand in payload or cand in found or cand in NEVER_CLOSURE or P.protected(cand):
                continue
            crepo = source_repo(cand, tpl_repo, core)
            if P.tag_bytes(crepo, R.TO_TAG, cand) is None:
                continue
            found[cand] = crepo
            if cand.endswith(".py") and cand not in seen:
                seen.add(cand)
                queue.append(cand)
    return found


def classify_path(loc, path, src_repo, tpl_repo, why=None):
    """Classify one payload path for a receiver and return its launch-packet item. A path that is, or goes through, a
    symbolic link, or resolves outside the receiver's folder, is `unsafe` (copy_isolation.destination_refusal()): a
    `cp -f` or an edit would write wherever the link points. An `unsafe` item gets no command, no write-set entry and
    no Edit rule; the prompt tells the session to leave it, and the after-run check reads it INCONCLUSIVE, so the
    member is not pushed with the path unmigrated."""
    unsafe = CI.destination_refusal(loc, path)
    if unsafe:
        return {"path": path, "op": "unsafe", "why": f"unsafe path: {unsafe}", "pre": "unread"}
    f = Path(loc) / path
    cur = f.read_bytes() if f.is_file() else None
    old = P.tag_bytes(tpl_repo, R.FROM_TAG, path)
    staged, digest = stage(src_repo, path)
    if staged is None:          # R3 kind line 1: no source, so no authored count and nothing to take
        return {"path": path, "op": "hold", "kind": "no-source", "authored_lines": None,
                "why": f"no {R.TO_TAG} source", "pre": P.sha_bytes(cur)}
    new = staged.read_bytes()
    op, authored = P.classify_file(cur, old, new)
    release_mode = 0o755 if staged.stat().st_mode & 0o100 else 0o644
    if op == "noop" and f.is_file() and (0o755 if f.stat().st_mode & 0o100 else 0o644) != release_mode:
        op = "write"   # identical bytes still need a release executable-bit change
    ids = None
    if op == "hold":
        upstream = P.UPSTREAM.setdefault(path, P.upstream_line_set(path))
        op, authored = P.classify_file(cur, old, new, upstream)
        ids = IM.authored_ids(cur, upstream) if op == "hold" else None
    item = {"path": path, "op": op, "authored_lines": authored, "pre": P.sha_bytes(cur),
            "source": f"{src_repo.name}@{R.TO_TAG}:{path}", "staged": str(staged), "sha256": digest,
            "release_mode": release_mode}
    if op == "hold":
        item["kind"] = IM.classify_kind(op, True, authored)
        item["authored_ids"] = ids
    if why:
        item["why"] = why
    return item


def item_rows(r):
    """Every payload item's meaning row, in order (R3 clause 3; B148 finding 2): raises UnknownClassification for an
    item with no row, BEFORE any consumer filters items by a bare op, so an unknown item is never omitted silently."""
    return [IM.meaning(i) for i in r.get("items", [])]


def placing_commands(i, loc):
    """The declared exact commands that place one WRITE item. Mutates and returns the item. Raises
    UnknownClassification for an item with no meaning row (B148 finding 2)."""
    IM.meaning(i)
    if i["op"] in ("write", "write-upstream") and i.get("staged"):
        # R1 clause 7 (PLACER): the sealed placer in the packet's stage writes the file at the act (an fd walk with
        # O_NOFOLLOW, missing folders made the same way, a temp file and a rename); it replaces `cp -f` and `mkdir -p`,
        # which followed a link or truncated a hard-linked file in place (J-5).
        i["command"] = f"python3 {placer_path()} {loc} {i['path']} {i['staged']} {i['sha256']}"
        i["hash_command"] = f"git hash-object {i['path']}"  # refused under --restricted unless declared (V3.7)
        i.pop("mkdir", None)
    return i


def placer_path():
    """The sealed placer's path in this packet's stage."""
    return str((STAGE or Path("<packet root>/stage")) / "kit" / "place_file.py")


def delete_item(loc, path, old_bytes):
    """The item for a path the release deletes. B193 finding 2: the target is read with no link followed; an existing
    link, folder or FIFO, or a path that cannot be reached, is not absence: the item is unsafe (INCONCLUSIVE after the
    run), never a noop. A regular file is deleted when it holds the old release bytes (`old_bytes()`), else held."""
    try:
        kind, cur = PF.read_entry(loc, path)
    except (PF.Refused, OSError, ValueError) as e:
        kind, cur = "unreachable", str(e)
    if kind not in ("file", "absent"):
        return {"path": path, "op": "unsafe", "pre": "unread",
                "why": f"the release deletes {path}, but the member holds a {kind} there"}
    cur = cur if kind == "file" else None
    op = "noop" if cur is None else ("delete" if cur == old_bytes() else "hold-delete")
    return {"path": path, "op": op, "pre": P.sha_bytes(cur)}


class TemplateUnmet(Exception):
    """C2e (D-8, S-277): a receiver whose template is unresolved or only inferred gets no launch plan."""


def plan_receiver(name, loc, repair=False, merged=()):
    """Return one receiver's launch plan: template, pins, HEAD, branch and the item for each payload path."""
    tpl, route = L.usable_template(loc, name)          # C2e (D-8, S-277): the launch's own template check
    if not tpl:
        raise TemplateUnmet(f"{name}: template unresolved ({route}); no packet entry is made")
    fw = Path(L.W.V.framework_root())
    tpl_repo, core = fw / tpl, fw / "aget"
    exp = L.payload_expectations(tpl)
    items = []
    for path, want in sorted(exp.items()):
        if P.protected(path) or path in L.CARRIERS:
            # Protected prepare/apply owns these paths, including mode-only writes and mode-bearing receipts.
            continue
        if want == "absent":
            items.append(delete_item(loc, path, lambda: P.tag_bytes(tpl_repo, R.FROM_TAG, path)))
            continue
        items.append(classify_path(loc, path, source_repo(path, tpl_repo, core), tpl_repo))
    payload = {p for p, w in exp.items() if w == "present"}
    named_only = []
    for path, src in sorted(closure(payload, tpl_repo, core).items()):
        if path.endswith(".md"):
            # A document named in code is usually an argument, not a dependency (2026-09-27: docs/README.md, passed
            # as a fake path in check_cross_client_hook_controls.py). Recorded, not installed; V3.6 shows a real need.
            named_only.append(path)
            continue
        item = classify_path(loc, path, src, tpl_repo, why="import closure")
        item["closure"] = True
        items.append(item)
    if repair:
        for n, i in enumerate(items):
            # R3 (S-229, S-241): a phase-1 hold becomes `merged` only if it has authored lines (judged by their
            # identities), else `kept` (judged by its digest); never assumed merged.
            if i["path"] in merged and i["op"] in ("hold", "write", "write-upstream"):
                to = "merged" if i.get("kind") == "authored" else "kept"
                why = ("merged in phase 1; the receiver's bytes stand" if to == "merged" else
                       "kept in phase 1; the receiver's bytes stand")
                items[n] = IM.relabel(i, to, why=why)
            elif i["op"] == "noop" and "sha256" in i:
                items[n] = IM.relabel(i, "verify")   # already the release bytes; the after-run check proves it (D)
    for i in items:
        placing_commands(i, loc)
    head = CI.read_git(loc, "rev-parse", "HEAD", text=True).stdout.strip()   # B166 finding 2: live reads unchanged
    branch = CI.read_git(loc, "rev-parse", "--abbrev-ref", "HEAD", text=True).stdout.strip()
    # R1 clause 1(c): the one push destination B10 may use, as git resolves it now (URL rewrites included). B1 is the
    # trust root: the register carries no remote URL, so B10 compares with this record.
    push = CI.read_git(loc, "remote", "get-url", "--push", "--all", "origin", text=True)
    push_url = push.stdout.split() if push.returncode == 0 else []
    return {"aget": name, "location": loc, "template": tpl, "template_route": route, "head": head, "branch": branch,
            "push_url": push_url,
            "pins": {"core": pin(core), tpl: pin(tpl_repo)}, "items": items, "closure_named_not_installed": named_only}


def receipt_path(r):
    """docs/ by default; a receiver whose own write scope forbids docs/ gets an allowed path (principal, batch 4:
    one receiver's receipt under .aget/). One source: result_binding.receipt_path."""
    return RBND.receipt_path(r)


def override_note(aget, batch):
    """The principal's recorded write-scope override for this Aget and batch, quoted for the receiver, or None."""
    rec = Path(REPO / "data" / f"{R.SLUG}_ledger" / "records.json")
    ov = ((json.loads(rec.read_text()).get("scope_overrides") or {}) if rec.is_file() else {}).get(aget) or {}
    if str(batch) not in [str(b) for b in ov.get("batches", [])]:
        return None
    return (f"Your .aget/version.json write_scope does not cover every path of this migration. The principal has "
            f"overridden it for this batch only; the record reads: \"{ov.get('source', '')}\". The override covers the "
            "files the approved write list placed (you only stage and commit them) and nothing else: write only the "
            "files this prompt names.")


def exact_commands(r):
    """Return the exact commands the receiver's session may run, in order."""
    cmds = []
    for i in r["items"]:
        if i.get("mkdir") and i["mkdir"] not in cmds:
            cmds.append(i["mkdir"])
        if i.get("command"):
            cmds.append(i["command"])
    cmds += [i["hash_command"] for i in r["items"] if i.get("hash_command")]
    cmds += [f"git hash-object {x['artifact']}" for x in r.get("amendments", [])]
    return cmds + VALIDATION + ([r["suite_cmd"]] if r.get("suite_cmd") else [])


def write_set(r, repair=False):
    """Return the paths the receiver's session may write. Raises UnknownClassification for an item with no row."""
    item_rows(r)
    # A file the principal's apply placed is pre-dirty at launch (the after-run check holds its bytes), never edited.
    paths = [i["path"] for i in r["items"] if (i["op"] in ("write", "write-upstream") if repair else
                                               IM.meaning(i).write_set) and not i.get("placed_by")] + [
        x["path"] for x in r.get("amendments", [])]
    extra = [] if repair else r.get("extra_carriers", []) + r.get("extra_write", [])
    return sorted(paths) + ([] if repair else CARRIERS) + extra + [receipt_path(r), "sessions/*"]


def allowlist(r, repair=False):
    """Return the permission rules the receiver's session is launched with. Raises UnknownClassification for an item
    with no row."""
    item_rows(r)
    rules = ["Read", "Glob", "Grep", "Bash(git status)", "Bash(git diff:*)", "Bash(git log:*)", "Bash(git show:*)"]
    edits = [receipt_path(r), "sessions/**"] + [x["path"] for x in r.get("amendments", [])] + (
        [] if repair else [i["path"] for i in r["items"] if IM.meaning(i).edit] + CARRIERS
        + r.get("extra_carriers", []) + r.get("extra_write", []))
    rules += [f"Edit({p})" for p in edits]
    rules += [f"Bash({c})" for c in exact_commands(r)]
    rules += [f"Bash({c}:*)" for c in ALLOWED_BASH if not (repair and c == "git rm")]
    return rules


def settings_file(r):
    """The receiver's own project hooks, and nothing else, for --settings (route-b-restricted-hooks). Hook events named
    in r["omit_hooks"] (a principal ruling per receiver, e.g. batch 8's SessionEnd) are left out, and disclosed."""
    # E2i14: never read through a link; E2i15 (FWK-OVSR6's E2i14 pre-read 2, reproduced): nor through a linked
    # .claude folder above it, so the whole path is reached with no link followed
    try:
        kind, raw = PF.read_entry(r["location"], ".claude/settings.json")
    except (PF.Refused, OSError, ValueError) as e:
        raise ValueError(f"{r['aget']}: .claude/settings.json cannot be read without following a link ({e})") from None
    if kind not in ("file", "absent"):
        raise ValueError(f"{r['aget']}: .claude/settings.json is not a regular file")
    raw = raw if kind == "file" else b"{}"
    doc = json.loads(raw or b"{}")
    try:                  # B189 finding 1: a regular file at HEAD only (B166 finding 2: read_git's read flags)
        tracked = CI.git_blob_at(r["location"], "HEAD", ".claude/settings.json")
    except CI.InspectionFailed:
        tracked = None    # a link, a tree or a failed read never matches the working file
    out = STAGE / "settings" / f"{r['aget']}.json"
    STAGE.mkdir(parents=True, exist_ok=True)
    omit = set(r.get("omit_hooks") or [])
    missing = omit - set(doc.get("hooks", {}))
    if missing:
        raise ValueError(f"{r['aget']}: omit_hooks names events its settings do not have: {sorted(missing)}")
    hooks = {k: v for k, v in doc.get("hooks", {}).items() if k not in omit}
    body = json.dumps({"hooks": hooks}, indent=2) + "\n"
    CI.contained_write(STAGE, f"settings/{r['aget']}.json", body.encode())
    return {"path": str(out), "sha256": P.sha_bytes(body.encode()), "from": str(Path(r["location"]) / ".claude" / "settings.json"),
            "from_sha256": P.sha_bytes(raw), "from_matches_head": tracked is not None and tracked == raw,
            "hook_events": sorted(hooks), "hook_events_omitted": sorted(omit), "allow_rules_dropped": len(
                (doc.get("permissions") or {}).get("allow", []))}


def pre_dirty(loc):
    """Return the paths that git status reports as changed or untracked at the location."""
    return CI.git_status_paths(loc)    # B158 finding 1: NUL-separated, byte for byte; a rename names both paths


def untracked_protected(loc, paths):
    """Return those of the given paths that git does not track at the location. B183 finding 1 (FWK-OVSR5's E2i10
    advisory (7)): a failed read raises InspectionFailed (preparation stops), never reports a path untracked."""
    return [p for p in paths if not CI.git_tracked(loc, p)]


def _rules_block(r):
    return ([r["override_note"]] if r.get("override_note") else []) + [
        "This session has no interactive approvals. A refused tool call is final: do not retry it or try another way.",
        "Make one plain command per Bash call: no chaining (; && ||), no pipes, no redirects (> >>), no $(...), no "
        "backticks. The only Bash commands you may run are: each command this prompt shows, exactly as written; "
        "python3 -m pytest (with any test arguments); git add <one path>; git commit -m \"...\"; and read-only "
        "inspection (git status, git diff, git log, git show, git hash-object without -w, cat, ls). Nothing else.",
        ("This migration's files were placed as exact release bytes by the approved write list. Never write them with "
         "Read/Write/Edit or any command: re-typing loses bytes (batch 1 lost trailing whitespace this way)."
         if r.get("placed_by_apply") else
         "Place every file this prompt lists with its exact cp command. Never write those files with Read/Write/Edit: "
         "re-typing loses bytes (batch 1 lost trailing whitespace this way)."),
        "Do not use the Skill, Agent, Task or Monitor tools, and do not run your wake-up or other scripts except the "
        "validation commands below: the supervisor's check cannot see inside them. Never push.",
        *([f"These files were already modified before this session: {', '.join(r['pre_dirty'])}. Do not stage, "
           "commit, edit or discard them."] if r.get("pre_dirty") else []),
    ]


def prompt(r, attempt, protected_paths):
    """Return the migration prompt for one receiver's headless session."""
    untracked = r.get("untracked_protected") or []
    lines = [
        f"You are this repository's Aget ({r['aget']}). The supervisor, {R.SUPERVISOR}, launched this headless "
        f"session on the principal's authorization to migrate you from {R.FROM_TAG} to {R.TO_TAG}. Attempt: {attempt}.",
        *_rules_block(r), "",
        f"The principal has ALREADY written your protected files for this release (do not edit them): "
        f"{', '.join(protected_paths)}.",
        f"Release pins: core aget-framework/aget {R.TO_TAG} = {r['pins']['core']}; {r['template']} {R.TO_TAG} = "
        f"{r['pins'][r['template']]}. Release documents (read them): "
        + ", ".join(str((STAGE or Path("<packet root>/stage")) / "aget" / d) for d in CORE_DOCS) + ".",
        *([f"Your git does not track these protected files: {', '.join(untracked)}. Do not change your ignore "
           "rules; record in your receipt that a push will not carry them."] if untracked else []), "",
        "1. Read AGENTS.md. Your session record may go under sessions/. Write nothing else outside the files named "
        "below.",
        (f"2. Read {baseline_path(r)}: your pre-migration test run, taken by you in a separate session before any file "
         "was placed. It is this migration's baseline: its counts and every failing test id."
         if r.get("placed_by_apply") else
         f"2. Run: {suite_command(r)}   Record the counts and the id of every failing test."),
        ("3. The unprotected payload was ALREADY placed, as the release's exact bytes, by the approved write list "
         "before this session. Do not edit those files. Record each one's blob id with the command shown, and do the "
         "merges listed:" if r.get("placed_by_apply") else
         "3. Install the unprotected payload exactly as listed (each staged file is the release's exact bytes):"),
    ]
    for i in r["items"]:
        if i["op"] in ("write", "write-upstream") and i.get("placed_by"):
            lines.append(f"   - {i['path']}: placed; run {i['hash_command']}")
        elif i["op"] in ("write", "write-upstream"):
            if i.get("mkdir"):
                lines.append(f"   - Run: {i['mkdir']}")
            lines.append(f"   - Run: {i['command']}" + ("   (import closure: a shipped test needs it)"
                                                        if i.get("closure") else ""))
        else:                # R3: every other item's line comes from its meaning row; an unknown one raises
            text = IM.meaning(i).instruction
            if text is not None:
                lines.append(f"   - {text(i)}")
    # D2 (R3, DESIGN: "The prompt names protected holds from the protected-write list with their KEEP or LEAVE row"):
    # each protected file the principal's apply held is named with its own meaning row's line; a row with no line
    # (a held line) is LEAVE: not changed. An unknown classification raises, as for every item
    for h in r.get("protected_holds") or []:
        text = IM.meaning(h).instruction
        lines.append(f"   - {text(h)}" if text is not None else
                     f"   - LEAVE {h['path']}: a protected file the principal's apply held; do not change it.")
    lines += [
        "   Paths not listed are already current. Do not touch them.",
        f"4. Version carriers: in .aget/version.json set aget_version to {R.TO} (leave it if it already reads {R.TO}) and "
        f"append one migration_history entry (version {R.TO}, route '{ROUTE}', attempt {attempt}) in the same form as "
        "the list's existing entries (a string if they are strings). In manifest.yaml set the instance's version line "
        f"to {R.TO} only (leave it if it already reads {R.TO})."
        + (f" Also bump your own version carrier(s) {', '.join(r['extra_carriers'])} to {R.TO} in the same commit, as "
           "each file's own contract says (your pre-commit hook checks it against .aget/version.json)."
           if r.get("extra_carriers") else ""),
        *([f"4b. Your ratchet {r['known_missing_ruling']['file']}: in KNOWN_MISSING remove every entry your audit no "
           "longer finds, and add exactly these, which the principal ruled known-missing ("
           f"{r['known_missing_ruling']['source']}): "
           + "; ".join(f"({s}, {p})" for s, p in r["known_missing_ruling"]["entries"])
           + ". Add no other entry. Stage the file with the others in step 7."] if r.get("known_missing_ruling")
          else []),
        *[f"4c. {s}" for s in r.get("extra_steps", [])],
        *([f"4d. Rename imports, exactly and only these (whole-word module name): " + "; ".join(
            f"in {x['path']}, {x['old']} -> {x['new']}" for x in r["renames"])
           + ". Change nothing else in those files. Stage each with the others in step 7."] if r.get("renames")
          else []),
        *(["Some files placed before this session are YOUR OWN resolutions, committed earlier in your repository and "
           "placed from there: " + ", ".join(f"{i['path']} (from {i['source']})" for i in r["items"]
                                            if i.get("receiver_authored"))
           + ". Verify them as placed; do not re-merge them."] if any(i.get("receiver_authored") for i in r["items"])
          else []),
        f"5. Validate. Run: {suite_command(r)}   Compare with step 2 (counts and failing-test ids). Then run each of "
        "these, exactly: " + "; ".join(VALIDATION) + ". Name which shows the credited capability and which shows a "
        "rejection path.",
        f"6. In {receipt_path(r)}, {RBND.receipt_instruction(attempt)[0]}, with: member {r['aget']}; route '{ROUTE}'; "
        "the release pins; a table of every step-3 path with its action and its git blob id after (git hash-object "
        "<path>); the protected files (written by the principal, not edited here); tests before and after; the "
        "behaviour evidence from step 5; preservation (merges, kept lines); limitations; your pre-migration HEAD "
        f"{r['head']} as the rollback reference. {RBND.receipt_instruction(attempt)[1]}",
        "7. Commit. Stage each file by name, one git add per command (never git add . or -A). Stage: every step-3 "
        "and step-4 file, your receipt and your session record"
        + (f", AND the protected files the principal wrote, which are part of this migration: "
           f"{', '.join(r.get('commit_protected') or [])} (stage them; never edit them)" if r.get("commit_protected")
           else "")
        + f". Then: git commit -m \"{R.TO_TAG} migration, {attempt}\"   Do NOT push.",
        "8. End your reply with: the receipt path, the commit sha, and the terminal.",
    ]
    return "\n".join(lines)


def baseline_path(r):
    """a2: the receiver's own pre-migration suite run, recorded by launch_batch.py --baseline before the list is
    applied, in that receiver's baseline slot of the packet root (PR/baselines/<aget>/baseline.json). The slot stays
    open until the receiver's B8 launch seals it; the session reads it through --add-dir PR."""
    return str((PACKET_ROOT or Path("<packet root>")) / "baselines" / r["aget"] / "baseline.json")


BASELINE_CMD = "python3 -m pytest -q -rfE -p no:cacheprovider"


def suite_command(r):
    """The receiver's suite command: its ruled per-receiver command (row 11), else pytest without its cache provider."""
    return r.get("suite_cmd") or "python3 -m pytest -q -p no:cacheprovider"


def baseline_prompt(r):
    """Return the prompt for the session that records a receiver's test baseline."""
    return (f"You are this repository's Aget ({r['aget']}). The supervisor, {R.SUPERVISOR}, launched this "
            f"headless session on the principal's authorization to record your test baseline before the {R.TO_TAG} "
            f"migration. Make exactly one Bash call: {r.get('suite_cmd') or BASELINE_CMD}   Make no other tool call "
            "and change nothing. "
            "Then reply with the summary line and every FAILED or ERROR test id, exactly as printed.")


def untracked_skill_paths(loc):
    """SKILL.md files under .claude/skills/ that git does not track (gh#1569), sorted."""
    tracked = set(CI.git_paths(loc, "ls-files", ".claude/"))   # B158 finding 1
    base = Path(loc) / ".claude" / "skills"
    # The name AS STORED on disk (G3.6 row 2, 2026-09-28): on a case-insensitive filesystem rglob("SKILL.md") matched a
    # `skill.md` but reported the pattern's spelling, and `git add` of that spelling staged nothing.
    found = [str(p.relative_to(loc)) for p in base.rglob("*")
             if p.is_file() and p.name.lower() == "skill.md"] if base.is_dir() else []
    return sorted(p for p in found if p not in tracked)


def track_commands(r):
    """The exact commands of a track-skills session: one bare check-ignore probe, one git add per path."""
    probe = next((p for p in r["track_paths"] if p != ".gitignore"), None)
    return ([f"git check-ignore --no-index {probe}"] if probe else []) + [f"git add {p}" for p in r["track_paths"]]


def track_skills_prompt(r, attempt):
    """Return the prompt for a session that only tracks the receiver's skill files."""
    skills = [p for p in r["track_paths"] if p != ".gitignore"]
    lines = [
        f"You are this repository's Aget ({r['aget']}). The supervisor, {R.SUPERVISOR}, launched this headless "
        f"session on the principal's authorization to TRACK your skill files (gh#1569). Attempt: {attempt}.",
        "Your .gitignore ignored the whole .claude/ directory with a bare `.claude/` rule, so your skills under "
        ".claude/skills/ were untracked: one deletion from unrecoverable, and no push could carry them (four of them are "
        f"{R.TO_TAG} payload files, which is why the fleet ledger reads your migration as not conforming).",
        "The approved write list has ALREADY rewritten that one rule, before this session: `.claude/` became `.claude/*` "
        "followed by `!.claude/skills/`. The rest of .claude/ stays ignored. Do not edit .gitignore or any skill file.",
        *_rules_block(r), "",
        f"1. Run exactly: {track_commands(r)[0]}   It must exit 1 (1 = not ignored). If it exits 0, stop: commit "
        "nothing, and report CANNOT-RUN." if skills else "1. (no skill files to track)",
        "2. Stage, one command each, exactly: " + "; ".join(f"git add {p}" for p in r["track_paths"]) + ".",
        "3. Run: git status --short   Nothing else may be staged.",
        f"4. In {receipt_path(r)}, {RBND.receipt_instruction(attempt, 'skill tracking')[0]}: the rule change; the "
        f"{len(skills)} skill files now tracked; the check-ignore result; limitations; your HEAD {r['head']} as the "
        f"rollback reference. {RBND.receipt_instruction(attempt)[1]} Then: git add {receipt_path(r)}",
        f"5. Commit: git commit -m \"{R.TO_TAG}: track skill files (gh#1569), {attempt}\"   Do NOT push.",
        "6. End your reply with: the receipt path, the commit sha, and the terminal.",
    ]
    return "\n".join(lines)


def history(r):
    """What was wrong at THIS receiver only (F7, 2026-09-27: github's prompt named defects it never had)."""
    todo = [i for i in r["items"] if i["op"] in ("write", "write-upstream")]
    parts = []
    if any(i["path"] in W.CORRECTION_ROW_4 for i in todo):
        parts.append("the supervisor's packet took scripts/close_authorization_guard.py from the template instead of "
                     "the core release")
    parts += [f"the packet omitted {i['path']}, which the release's tests need" for i in todo if i.get("closure")]
    parts += [f"your copy of {i['path']}, re-typed from the staged release file, does not match its bytes"
              for i in todo if not i.get("closure") and i["path"] not in W.CORRECTION_ROW_4]
    parts += [f"your merge of {x['artifact']} breaks your own contract row {x['row']} in {x['path']}, as your "
              "receipt recorded" for x in r.get("amendments", [])]
    return "; ".join(parts) + "." if parts else "nothing beyond the verification below."


def repair_prompt(r, attempt, previous):
    """Return the prompt for a session that repairs a receiver's earlier, rejected attempt. Raises
    UnknownClassification for an item with no row (B148 finding 2)."""
    item_rows(r)
    todo = [i for i in r["items"] if i["op"] in ("write", "write-upstream")]
    placed = r.get("placed_by_apply", False)
    lines = [
        f"You are this repository's Aget ({r['aget']}). The supervisor, {R.SUPERVISOR}, launched this headless "
        f"session on the principal's authorization to REPAIR your {R.TO_TAG} migration. Attempt: {attempt}.",
        f"Your previous attempt ({previous}) is your commit {r['head']} and its receipt {receipt_path(r)}. You "
        "REJECTED it, correctly. Here is what was wrong, for you: " + history(r) + " This packet corrects those and "
        "changes nothing else.",
        *_rules_block(r), "",
        f"Release pins: core aget-framework/aget {R.TO_TAG} = {r['pins']['core']}; {r['template']} {R.TO_TAG} = "
        f"{r['pins'][r['template']]}. Your protected files, your version carriers and your merge of "
        f"{', '.join(i['path'] for i in r['items'] if i['op'] == 'merged') or 'none'} are already correct: do not "
        "edit them.",
        "",
        f"1. Read {receipt_path(r)}. Its step-2 test run, before the migration, is this repair's baseline: note its "
        "counts and every failing test id.",
    ]
    if placed:
        lines.append("2. The principal has ALREADY placed these files, as the release's exact bytes (the principal's apply "
                     "script, run before this session). Do not edit them. Record each blob id with the command shown:")
        for i in todo:
            lines.append(f"   - {i['path']}: run {i['hash_command']}   (expected release sha256 {i['sha256'][:12]})")
    else:
        lines.append("2. Place these files, each with exactly the command shown (each staged file is the release's "
                     "exact bytes):")
        for i in todo:
            if i.get("mkdir"):
                lines.append(f"   - Run: {i['mkdir']}")
            why = i.get("why") or ("release bytes differ from yours" if i.get("pre") != i["sha256"] else "")
            lines.append(f"   - Run: {i['command']}" + (f"   ({why})" if why else ""))
            lines.append(f"     then: {i['hash_command']}   (its blob id, for your receipt)")
    for x in r.get("amendments", []):
        lines.append(
            f"   - AMEND your own contract row {x['row']} in {x['path']} (principal ruling {x['ruling']}): in its "
            f"runtime_payload entry for {x['artifact']}, set sha256_current to {x['sha256']} (the sha256 of your "
            f"merged {x['artifact']}, as committed at {r['head'][:8]}); leave every other sha256_at_* field unchanged; append to "
            f"amended_post_tag one sentence: \"{x['note']}\". Use the Edit tool for this file only. Change nothing "
            f"else in it. Then run: git hash-object {x['artifact']}")
    lines += [
        "   Touch nothing else.",
        f"3. Run: {suite_command(r)}   List every test that fails now and did not fail in the step-1 baseline.",
        "4. Run each of these, exactly: " + "; ".join(VALIDATION) + ". Name which shows the credited capability and "
        "which shows a rejection path.",
        f"5. In {receipt_path(r)}, {RBND.receipt_instruction(attempt, 'repair')[0]}, with: route '" + ROUTE + "'; "
        "each file from step 2 with its git blob id after (git hash-object <path>); tests: the baseline and now, and "
        f"every new failure; the behaviour evidence from step 4; limitations; your commit {r['head']} as the rollback "
        f"reference. {RBND.receipt_instruction(attempt)[1]} "
        "A new failure against the baseline means the terminal cannot be ACCEPTED or BEHAVIOUR_VERIFIED.",
        "6. Commit. Stage each file by name, one git add per command (never git add . or -A): every file from step 2 "
        "(including any contract you amended), "
        f"your receipt, and your session record if you wrote one. Then: git commit -m \"{R.TO_TAG} migration, {attempt}\"   "
        "Do NOT push.",
        "7. End your reply with: the receipt path, the commit sha, and the terminal.",
    ]
    return "\n".join(lines)


def exclude_items(r, excl):
    """Remove the named payload paths from a receiver's packet, recording each with its reason; a path not in the
    packet refuses (a typo must not pass silently)."""
    missing = set(excl) - {i["path"] for i in r["items"]}
    if missing:
        raise ValueError(f"--exclude names paths not in its packet: {sorted(missing)}")
    if excl:
        r["excluded"] = [{"path": p, "reason": why} for p, why in sorted(excl.items())]
        r["items"] = [i for i in r["items"] if i["path"] not in excl]
    return r


def apply_list(packet, location_override=None):
    """The principal's list for the reviewed apply_protected.py (unchanged; its digest is recorded here): one `write`
    entry per placed item, `pre` = the file's digest now, `post` = `source_sha256` = the item's `sha256` (the release digest, or
    for a --resolved-file item the digest of the bytes its source names)."""
    script = HERE / "apply_protected.py"
    agets = []
    for r in packet["receivers"]:
        ops = [{"path": i["path"], "op": "write", "pre": i["pre"], "post": i["sha256"], "source": i["source"],
                "source_sha256": i["sha256"]} for i in r["items"] if i.get("placed_by")]
        agets.append({"aget": r["aget"], "location": (location_override or {}).get(r["aget"], r["location"]),
                      "head": r.get("head"), "ops": ops})
    return {"schema": "v335_protected_list/1", "batch": packet["batch"], "purpose": "batch 1 repair: unprotected "
            "payload files placed by the principal (ruling F5-apply-script, 2026-09-28)",
            "apply_script_sha256": P.sha_bytes(script.read_bytes()), "agets": agets}


def seal_packet(out):
    """Seal the stage (every entry not writable, no link, a manifest {rel: sha256} kept in the packet), make one open
    baseline slot per receiver that takes a baseline, and make PR and PR/baselines not writable. A failed prepare
    leaves an unsealed PR and no packet; every launch refuses an unsealed stage."""
    root = Path(out["packet_root"])
    for r in out["receivers"]:
        if r.get("baseline_prompt"):
            CI.contained_mkdir(root, f"baselines/{r['aget']}")
    (root / "baselines").mkdir(exist_ok=True)
    out["stage_manifest"] = CI.seal_tree(root, "stage")     # B151 finding 7: through fds, no second name
    CI.seal_folder(root, "baselines")                         # same class, found while building: no chmod by path
    CI.seal_folder(root)


def main():
    """Command-line entry point: prepare a batch's receiver launch packet."""
    R.require()
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--receipt", type=Path, help="the protected-write apply receipt (batch 1 and its repair)")
    ap.add_argument("--protected-list", type=Path, help="a2: the write list to be approved; protected paths from it")
    ap.add_argument("--batch", help="batch id (default 1 / 1-repair)")
    ap.add_argument("--route", help="route label recorded in the packet and receipts")
    ap.add_argument("--receipt-at", nargs="*", default=[], metavar="AGET=PATH",
                    help="write that receiver's receipt at PATH instead of docs/ (its own scope forbids docs/)")
    ap.add_argument("--track-skills", nargs="*", default=[], metavar="AGET",
                    help="these receivers get a gh#1569 skill-tracking session instead of a migration")
    ap.add_argument("--repair", action="store_true", help="batch 1 repair: on top of each receiver's local commit")
    ap.add_argument("--previous-packet", type=Path, help="with --repair: the phase-1 packet (attempt names, merges)")
    ap.add_argument("--own-row-amendment", action="append", default=[], metavar="AGET:PATH:ROW:ARTIFACT:RULING",
                    help="with --repair: the receiver re-pins its OWN contract row's sha256_current to its merged "
                         "ARTIFACT (digest read here from its tree), only on a principal RULING")
    ap.add_argument("--placed-by-apply", action="store_true",
                    help="with --repair (F5 ruling `F5-apply-script`): the principal's apply_protected.py places the "
                         "WRITE items; the receiver verifies and commits them and is given no copy command")
    ap.add_argument("--apply-list", type=Path, help="with --placed-by-apply: write the principal's apply list here")
    ap.add_argument("--carrier", nargs="*", default=[], metavar="AGET=PATH",
                    help="a receiver-specific version carrier its hooks demand (G3.6 row 8)")
    ap.add_argument("--extra-write", nargs="*", default=[], metavar="AGET=PATH",
                    help="a receiver file its session may edit beyond the payload (G3.6 row 8: its ratchet)")
    ap.add_argument("--known-missing", nargs="*", default=[], metavar="AGET=SKILL:PATH",
                    help="entries the principal ruled known-missing for that receiver's ratchet")
    ap.add_argument("--known-missing-file", nargs="*", default=[], metavar="AGET=PATH:AUDITOR",
                    help="that receiver's ratchet file and the auditor it runs")
    ap.add_argument("--known-missing-source", help="the ruling the known-missing entries quote")
    ap.add_argument("--resolved-file", type=Path, help="JSON {aget: {path: 'repo@rev:path'}}: receiver-authored "
                    "bytes the approved list places; the receiver verifies and commits them (G3.6 row 11)")
    ap.add_argument("--omit-hook", nargs="*", default=[], metavar="AGET=EVENT",
                    help="a hook event left out of that receiver's launch settings, on a principal ruling (row 11: the "
                         "framework Aget's SessionEnd wind-down writes a session file and appends a tracked log)")
    ap.add_argument("--rename-import", nargs="*", default=[], metavar="AGET=OLD:NEW:PATH",
                    help="a module rename the receiver applies in PATH (step 4c), stated as data so V3.6 applies it "
                         "too (row 11: the framework Aget's 4 importers; prose-only 4c hid a regression from V3.6)")
    ap.add_argument("--suite-cmd", nargs="*", default=[], metavar="AGET=CMD",
                    help="a ruled per-receiver suite command for V3.6, the baseline and steps 2 and 5 (row 11)")
    ap.add_argument("--sibling-read", nargs="*", default=[], metavar="AGET=REL",
                    help="a folder outside the Aget that its tests read (e.g. ../aget); V3.6 copies it beside the "
                         "copy (G3.6 row 12, B2: batch 8's identifier regression was invisible without it)")
    ap.add_argument("--exclude", nargs="*", default=[], metavar="AGET=PATH=REASON",
                    help="a payload path removed from that receiver's packet, with the reason recorded (G3.6 row 11: "
                         "the framework Aget's .aget/config.json is machine-local, git-ignored and untracked, so a "
                         "merge could never be committed and the B10 push check would refuse the batch)")
    ap.add_argument("--extra-step", nargs="*", default=[], metavar="AGET=TEXT",
                    help="one more instruction for that receiver's session, given as step 4c (e.g. rewrite importers)")
    ap.add_argument("names", nargs="+")
    a = ap.parse_args()
    for spec in a.extra_step:
        name, sep, text = spec.partition("=")
        if not sep or name not in a.names or not text.strip():
            ap.error(f"--extra-step {spec!r}: expected a requested member name and non-empty TEXT (AGET=TEXT)")
    global ROUTE
    if a.route:        # the prompt's version entry and receipt carry the packet's route (batch 8 V3.7 wrote "a1 … batch 1")
        ROUTE = a.route
    if not (a.receipt or a.protected_list):
        ap.error("one of --receipt (batch 1) or --protected-list (a2) is required")
    receipt_applied, unbound, receipt_held = {}, {}, {}
    if a.receipt and a.protected_list:    # C2d (FWK-OVSR8's C2d pre-read 5): the packet would name a receipt never read
        ap.error("--receipt and --protected-list together: the apply receipt would be named in the packet without being "
                 "read; pass one")
    if a.receipt and not a.protected_list:   # R2-T6, before anything is staged: files only from a bound entry
        receipt, why = RBND.read_current("apply_protected", a.receipt)   # R2-T17: the apply run's current receipt
        if why:
            ap.error(f"--receipt {a.receipt} cannot be used: {why}")
        if not isinstance(receipt, dict) or receipt.get("mode") != "apply":
            ap.error(f"--receipt {a.receipt}: {RBND.apply_entry(receipt, None)[1]}")
        # C2d (FWK-OVSR8's C2d pre-read 1): this batch's receipt, each entry applied at the member's own location
        this_batch = a.batch or ("1-repair" if a.repair else "1")
        if str(receipt.get("batch")) != str(this_batch):
            ap.error(f"--receipt {a.receipt}: {RBND.apply_entry(receipt, None, batch=this_batch)[1]}; no packet is made")
        for x in receipt.get("agets") or []:
            name = x.get("aget") if isinstance(x, dict) else None
            entry, why = RBND.apply_entry(receipt, name, batch=this_batch)
            if why:
                unbound[name] = why
            else:
                receipt_applied[name] = [f["path"] for f in entry.get("files", [])]
                receipt_held[name] = [h for h in entry.get("held") or [] if isinstance(h, dict)]   # D2 (R3)
        for n in a.names:                     # B179 finding 2: every requested member has exactly one bound entry
            if n not in receipt_applied:
                ap.error(f"{n}: {unbound.get(n, 'the apply receipt has no entry for this Aget')}; no packet is made")
        member_locs = dict(L.members())       # C2d (pre-read 1): each requested entry was applied at its location
        for n in a.names:
            why = RBND.apply_entry(receipt, n, batch=this_batch, location=member_locs.get(n, ""))[1]
            if why:
                ap.error(f"{n}: {why}; no packet is made")
    # C2e (D-8, S-277): every requested receiver's template is checked before any packet folder is made
    for n, loc in L.members():
        if n in a.names:
            tpl, route = L.usable_template(os.path.expanduser(loc), n)
            if not tpl:
                ap.error(f"{n}: template unresolved ({route}); no packet is made")
    global PACKET_ROOT, STAGE
    base = packet_base(a.out)
    why = CI.work_refusal(base, avoid=[os.path.expanduser(loc) for _, loc in L.members()]
                          + [L.W.V.framework_root()])
    if why:
        ap.error(f"packet base: {why} (set AGET_MIGRATION_PACKET_BASE)")
    base.mkdir(parents=True, exist_ok=True)
    PACKET_ROOT = Path(tempfile.mkdtemp(dir=base, prefix=f"{a.batch or 'b1'}-"))
    STAGE = PACKET_ROOT / "stage"
    STAGE.mkdir()
    CI.contained_write(STAGE, "kit/place_file.py", (HERE / "place_file.py").read_bytes())
    core = Path(L.W.V.framework_root()) / "aget"
    for d in CORE_DOCS:
        stage(core, d)
    if a.protected_list:
        # a2 (batch 2 on): the packet is built BEFORE the approved list is applied, so the protected paths come from the
        # list; launch_batch.py takes the real apply receipt at launch (--apply-receipt)
        lst = json.loads(a.protected_list.read_text())
        applied = {x["aget"]: [o["path"] for o in x.get("ops", []) if o["op"] in ("write", "write-upstream",
                                                                                   "replace-line")
                               and P.protected(o["path"])] for x in lst["agets"]}
        holds = {x["aget"]: [dict(o)   # D3 (B200 finding 4): the list's whole entry (digest, authored count, source)
                             for o in x.get("ops", []) if o["op"] in ("hold", "hold-line") and P.protected(o["path"])]
                 for x in lst["agets"]}                  # D2 (R3): the protected holds the prompt names
    else:
        applied = dict(receipt_applied)
        holds = dict(receipt_held)
    resolved = json.loads(a.resolved_file.read_text()) if a.resolved_file else {}
    for aget_name, paths in resolved.items():   # receiver-authored protected bytes are placed by the list as well
        applied.setdefault(aget_name, [])
        applied[aget_name] += [p for p in paths if P.protected(p) and p not in applied[aget_name]]
    prev = {}
    if a.previous_packet:
        prev = {r["aget"]: r for r in json.loads(a.previous_packet.read_text())["receivers"]}
    locs = dict(L.members())
    out = {"schema": "v335_launch_packet/2", "batch": a.batch or ("1-repair" if a.repair else "1"),
           "route": a.route or ROUTE,
           "prepared_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"), "stage": str(STAGE),
           "packet_root": str(PACKET_ROOT),
           "apply_receipt": str(a.receipt) if a.receipt else None, "write_list": str(a.protected_list or ""),
           "tools": TOOLS, "deny": DENY, "validation": VALIDATION, "baseline_cmd": BASELINE_CMD,
           "claude_version": subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip(),
           "receivers": []}
    for n in a.names:
        merged = {i["path"] for i in prev.get(n, {}).get("items", []) if i["op"] == "hold"}
        r = plan_receiver(n, os.path.expanduser(locs[n]), repair=a.repair, merged=merged)
        for spec in a.own_row_amendment:
            aget, path, row, artifact, ruling = spec.split(":")
            if aget == n:
                data = (Path(r["location"]) / artifact).read_bytes()
                r.setdefault("amendments", []).append({
                    "path": path, "row": row, "artifact": artifact, "ruling": ruling, "sha256": P.sha_bytes(data),
                    "note": f"{R.TO_TAG}: a migration merged the release's {artifact} with this Aget's own lines; "
                            f"sha256_current re-pinned to the merged bytes on the principal's ruling {ruling}."})
        for k, i in enumerate(r["items"]):   # an unprotected path with a receiver-authored resolution: the list places
            src = (resolved.get(n) or {}).get(i["path"])   # those bytes
            if src:
                resolved_source = A.release_bytes(src, with_mode=True)
                if resolved_source is None:
                    ap.error(f"{n}: cannot read {src}")
                data, resolved_mode = resolved_source
                cur = Path(os.path.expanduser(locs[n])) / i["path"]
                try:           # R3 (S-233, S-242): a listed transition only; the release `cp` is not carried over
                    r["items"][k] = IM.relabel(
                        {x: v for x, v in i.items() if x not in ("staged", "kind", "authored_ids")}, "write",
                        sha256=P.sha_bytes(data), source=src, receiver_authored=True,
                        placed_by="the write list (receiver-authored bytes)",
                        pre=P.sha_bytes(cur.read_bytes()) if cur.is_file() else "absent",
                        hash_command=f"git hash-object {i['path']}") if i["op"] != "write" else {
                        **{x: v for x, v in i.items() if x not in ("staged", "command", "mkdir")}, "sha256":
                        P.sha_bytes(data), "source": src, "receiver_authored": True,
                        "placed_by": "the write list (receiver-authored bytes)",
                        "hash_command": f"git hash-object {i['path']}"}
                except IM.UnknownClassification as exc:
                    ap.error(f"{n}: {exc}")
                r["items"][k]["release_mode"] = resolved_mode
        omit = [s.split("=", 1)[1] for s in a.omit_hook if s.split("=", 1)[0] == n]
        if omit:
            r["omit_hooks"] = omit
        renames = [dict(zip(("old", "new", "path"), s.split("=", 1)[1].split(":", 2)))
                   for s in a.rename_import if s.split("=", 1)[0] == n]
        if renames:
            r["renames"] = renames
            r["extra_write"] = sorted(set(r.get("extra_write", [])) | {x["path"] for x in renames})
        sc = [s.split("=", 1)[1] for s in a.suite_cmd if s.split("=", 1)[0] == n]
        if sc:
            r["suite_cmd"] = sc[0]
        sib = sorted({s.split("=", 1)[1] for s in a.sibling_read if s.split("=", 1)[0] == n})
        if sib:
            r["sibling_reads"] = sib
        try:
            exclude_items(r, {s.split("=", 2)[1]: s.split("=", 2)[2] for s in a.exclude if s.split("=", 2)[0] == n})
        except ValueError as exc:
            ap.error(f"{n}: {exc}")
        steps = [s.split("=", 1)[1] for s in a.extra_step if s.split("=", 1)[0] == n]
        if steps:
            r["extra_steps"] = steps
        placed_paths = []
        if a.placed_by_apply:
            r["placed_by_apply"] = True
            for i in r["items"]:
                if i["op"] in ("write", "write-upstream"):
                    i.pop("command", None)
                    i.pop("mkdir", None)
                    i["placed_by"] = "principal apply_protected.py"
                    placed_paths.append(i["path"])
        if a.receipt and not a.protected_list and n not in receipt_applied:   # R2-T6, B179 finding 2: absent too
            ap.error(f"{n}: {unbound.get(n, 'the apply receipt has no entry for this Aget')}; no packet is made")
        r["pre_dirty"] = [p for p in pre_dirty(r["location"]) if p not in applied.get(n, []) and p not in placed_paths]
        for key, spec in (("extra_carriers", a.carrier), ("extra_write", a.extra_write)):
            paths = [s.split("=", 1)[1] for s in spec if s.split("=", 1)[0] == n]
            if paths:
                r[key] = paths
        km = [s.split("=", 1)[1].split(":", 1) for s in a.known_missing if s.split("=", 1)[0] == n]
        kf = [s.split("=", 1)[1].split(":", 1) for s in a.known_missing_file if s.split("=", 1)[0] == n]
        if km:
            if not kf or not a.known_missing_source:
                ap.error(f"--known-missing for {n} needs --known-missing-file and --known-missing-source")
            r["known_missing_ruling"] = {"file": kf[0][0], "auditor": kf[0][1], "entries": km,
                                         "source": a.known_missing_source}
        r.update({k: v for k, v in (("receipt_path", dict(x.split("=", 1) for x in a.receipt_at).get(n)),
                                    ("override_note", override_note(n, out["batch"]))) if v})
        short = n.replace("private-", "").replace("public-", "")
        if n in a.track_skills:
            attempt = f"{R.SLUG}-b{out['batch']}-{short}-track-skills"
            skills = [x for x in untracked_skill_paths(r["location"])]
            r.update(mode="track-skills", attempt=attempt, track_paths=[".gitignore"] + skills)
            r["prompt"] = track_skills_prompt(r, attempt)
            r.update(allowlist=allowlist(r, True) + [f"Bash({c})" for c in track_commands(r)],
                     write_set=[receipt_path(r), "sessions/*"], allow_bash=ALLOWED_BASH,
                     allow_exact=exact_commands(r) + track_commands(r), settings=settings_file(r))
            out["receivers"].append(r)
            print(f"{n:34s} track-skills: .gitignore + {len(skills)} skill file(s)")
            continue
        if a.repair:
            attempt = f"{R.SLUG}-b1-{short}-repair"
            r.update(attempt=attempt, previous_attempt=prev.get(n, {}).get("attempt"))
            r["prompt"] = repair_prompt(r, attempt, r["previous_attempt"])
        else:
            r["protected_holds"] = holds.get(n, [])     # D2 (R3): named in the prompt with their KEEP or LEAVE row
            r["untracked_protected"] = untracked_protected(r["location"], applied.get(n, []))
            r["commit_protected"] = [p for p in applied.get(n, []) if p not in r["untracked_protected"]]
            attempt = f"{R.SLUG}-b{out['batch']}-{short}"
            r.update(attempt=attempt, prompt=prompt(r, attempt, applied.get(n, [])))
            if r.get("placed_by_apply"):
                r["baseline_prompt"] = baseline_prompt(r)
        r.update(allowlist=allowlist(r, a.repair), write_set=write_set(r, a.repair), allow_bash=ALLOWED_BASH,
                 allow_exact=exact_commands(r), settings=settings_file(r))
        out["receivers"].append(r)
        ops = [i["op"] for i in r["items"]]
        print(f"{n:34s} {r['template']:24s} head {r['head'][:8]} " +
              " ".join(f"{k} {ops.count(k)}" for k in sorted(set(ops))) +
              f"  closure {sum(1 for i in r['items'] if i.get('closure'))}  allowlist {len(r['allowlist'])}  "
              f"hooks {r['settings']['hook_events']}")
    seal_packet(out)        # R1 lifecycle, B1: the packet file is written only after the stage is sealed
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    if a.apply_list:
        a.apply_list.write_text(json.dumps(apply_list(out), indent=2) + "\n")
        print(f"apply list: {a.apply_list}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
