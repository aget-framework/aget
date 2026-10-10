#!/usr/bin/env python3
"""Plan v3.35 Gate 3, deliverable G3.1 — the per-Aget ledger that the fleet migration outcome is read from.

One row per member of the PINNED register (FLEET_STATE.yaml at the revision named when the goal was
committed), each classified mainly from observations at that Aget's PUBLISHED revision (the template and the
root workflow files, among others, are read from the local checkout). States come only
from here; totals are printed from the rows and never entered.

Terminal states (the migration outcome condition):
  VERIFIED         remote revision declares the target version or a later one; payload conforms to a
                   target-release source (template tag or core tag) at every payload path except the
                   version carriers (.aget/version.json, AGENTS.md, manifest.yaml, README.md,
                   CHANGELOG.md, CLAUDE.md: not compared by blob), or the difference is recorded;
                   the receiver's ingested receipt is contained in that revision; the checks were
                   not loosened since the pre-migration revision (or a ruling is recorded; when that
                   revision cannot be found or a workflow tree cannot be read, the comparison is NOT
                   MADE and the row reads INCONCLUSIVE unless a ruling named workflows-not-compared is recorded); every
                   workflow run on that exact revision concluded success.
  PUBLISHED-NO-CI  the version, payload and receipt conditions above hold, and the local checkout has
                   no workflow file (.yml/.yaml) at the repository root (or a recorded finding says a
                   shared root's workflow does not cover this Aget). The loosening test is NOT applied
                   before this state: an Aget that meets those conditions and whose root workflows were
                   all removed in the checkout reads PUBLISHED-NO-CI.
  EXCLUDED         a recorded principal ruling, quoted, with a reason class other than time or
                   difficulty.
Every other state is NON-TERMINAL and counts as unmet. Unreadable evidence is not always INCONCLUSIVE.
A remote revision that cannot be read or is not fetched and a template that cannot be resolved read
as INCONCLUSIVE; so does a failed CI query on a row that no earlier condition has settled, and so does
a workflow comparison that was not made (pre-migration revision not found, or the workflow tree
unreadable at either revision) on a row that reached the loosening test with no ruling named workflows-not-compared
recorded for the member. Among the
inputs that do not: a version.json absent or unparsable at the published revision reads as not
migrated (NOT-MIGRATED or UNPUBLISHED); a records file, receipt index or receipt evidence file that
cannot be read reads as empty (for example NO-RECEIPT or RECEIPT-NOT-ON-REVISION); a payload path
that cannot be resolved at the revision reads as absent.

Observations and their instruments (composed, not re-implemented):
  membership   `git show <pin>:.aget/fleet/FLEET_STATE.yaml`, the census's agent filter
  published    `git ls-remote --symref origin HEAD` at the repository root (read-only; no fetch).
               The remote revision must already be present locally to be read; if not, the row is
               INCONCLUSIVE ("not fetched"). This instrument never fetches into another Aget.
  version      `<sha>:<prefix>.aget/version.json` aget_version (check_version_at_remote's reading)
  template     this file's resolve_template, read from the working tree, not the published revision: a
               template ruling recorded for the member in records.json decides alone (unusable or
               unsourced gives no template); without one, version.json, manifest.yaml and archetype
               inference are read, and usable sources that disagree are a conflict (no template)
  payload      template diff between the release target's from-tag and to-tag (deleted and renamed-from
               paths must be absent, the other changed paths must match; version carriers skipped) plus
               wave_readiness.SPEC_PATHS and CORRECTION_ROW_4, compared by blob id
  receipt      docs/migration_inventory_<to tag>/OPERATIONAL_STATE.json claims (the ingestion route)
               and the evidence record's `receipt_revision`, which must be an ancestor of the
               published revision
  CI scope     workflows at the REPOSITORY ROOT (census_fleet_ci.repo_root); a shared root needs a
               recorded per-Aget coverage finding
  loosening    `.github/workflows` tree at the pre-migration revision vs the published revision
               (pre-migration revision not found, or either tree unreadable: NOT COMPARED, which reads
               INCONCLUSIVE unless a ruling named workflows-not-compared is recorded for the member;
               workflows-changed applies only to a changed tree, and another name passes neither comparison). Each row carries `checks_compared`: true,
               false, or null when the row was settled before this observation was made
  CI result    `gh run list --commit <sha>` (only with --online)
Recorded decisions and findings (exclusions, shared-root coverage, payload deviations, check-change
rulings, tightening reviews bound to a workflow tree, receipts not on the ingestion route) are read
from data/<slug>_ledger/records.json (slug from the target release: v336 for 3.36.0) and are never
inferred. The tool requires a recorded source for exclusions, receipts and template rulings; it does
not check a source for the other kinds.

It reads the Agets; with --json it writes the ledger document to OUT. Keep OUT outside every other Aget's
repository (operator rule, not enforced by the tool). Run from the repository root:
    python3 scripts/migration_kit/fleet_ledger.py [--online] [--json OUT] [--only NAME ...]
Exit: 0 ledger produced · 2 cannot produce it (pinned register unreadable, membership count wrong), or
an argument is refused · 1 the release target or the fleet pin is incomplete (stops with a message).
"""
from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import json
import re
import os
import subprocess
import sys
import time
from pathlib import Path

import yaml

import importlib.util

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[1]
sys.path.insert(0, str(HERE))
import census_fleet_ci as census  # noqa: E402

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_target as R  # noqa: E402  (the kit's one release parameter; carriage row 24)
import result_binding as RBND  # noqa: E402  (R2: the closed success list and the receipt grammar)
import item_meaning as IM  # noqa: E402  (R3: one meaning table per classification)
import copy_isolation as CI  # noqa: E402  (git_name_status: template diffs read byte for byte, B159 finding 1)


def _load(name, path):
    # By path, not by name: scripts/wave_readiness.py is an older, different module, and a
    # sys.path lookup silently picked it (measured 2026-09-27: no resolve_template attribute).
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


W = _load("v335_wave_readiness", HERE / "wave_readiness.py")

TARGET = R.TO
PIN = R.REGISTER_PIN
PINNED_MEMBERS = R.PINNED_MEMBERS
REGISTER = ".aget/fleet/FLEET_STATE.yaml"
OPSTATE = REPO / "docs" / f"migration_inventory_{R.TO_TAG}" / "OPERATIONAL_STATE.json"
RECORDS = REPO / "data" / f"{R.SLUG}_ledger" / "records.json"
TERMINAL = ("VERIFIED", "PUBLISHED-NO-CI", "EXCLUDED")
DISALLOWED_EXCLUSION_REASONS = {"time", "difficulty"}


class Unavailable(RuntimeError):
    """An observation could not establish its subject."""


def git(cwd, *args, timeout=60):
    """Run a git read in the given folder with a timeout; raise Unavailable if it cannot run or times out. The read
    leaves the folder's git folder as it was (copy_isolation.read_git(); B166 finding 2)."""
    try:
        return CI.read_git(cwd, *args, text=True, timeout=timeout)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Unavailable(f"git {args[0]} unavailable: {type(exc).__name__}") from exc


# ------------------------------------------------------------------ observations

def members(repo=REPO, pin=PIN):
    """Return (name, location) for every member of the fleet register as it stood at the pinned revision."""
    try:                                               # B191 finding 1: the register is a regular file at the pin
        b = CI.git_blob_at(repo, pin, REGISTER)
    except CI.InspectionFailed as e:
        raise Unavailable(f"pinned register unreadable at {pin[:8]}: {e}") from None
    if b is None:
        raise Unavailable(f"pinned register unreadable at {pin[:8]}: absent")
    d = yaml.safe_load(b.decode()) or {}
    out = []
    for pf in (d.get("fleet") or {}).values():
        if isinstance(pf, dict):
            for a in pf.get("agents", []) or []:
                if a.get("agent_name") and a.get("location"):
                    out.append((a["agent_name"], os.path.expanduser(a["location"])))
    return out


def remote_head(root):
    """Return (branch, sha) of origin's HEAD, read from the remote; raise Unavailable if it cannot be read."""
    r = git(root, "ls-remote", "--symref", "origin", "HEAD")
    if r.returncode != 0:
        raise Unavailable("ls-remote failed")
    branch = sha = None
    for line in r.stdout.splitlines():
        parts = line.split("\t")
        if line.startswith("ref: ") and len(parts) == 2:
            branch = parts[0][len("ref: "):].removeprefix("refs/heads/")
        elif len(parts) == 2 and parts[1] == "HEAD":
            sha = parts[0]
    if not sha:
        raise Unavailable("no remote HEAD")
    return branch, sha


def has_commit(root, sha):
    """Return True when the commit is present in the local repository."""
    return git(root, "cat-file", "-e", f"{sha}^{{commit}}").returncode == 0


def version_at(root, prefix, rev):
    """Return the framework version recorded at a revision, None if the file is absent, '?' if it is unreadable."""
    try:                                               # B191 finding 1: a regular file, absent, or unreadable ('?')
        b = CI.git_blob_at(root, rev, f"{prefix}.aget/version.json")
    except CI.InspectionFailed:
        return "?"
    if b is None:
        return None
    try:
        return json.loads(b).get("aget_version")
    except (ValueError, AttributeError):
        return "?"


def at_or_past(version, target=TARGET):
    """Return True when the version is at or past the target version; False if it cannot be parsed."""
    try:
        return tuple(int(x) for x in version.split(".")) >= tuple(int(x) for x in target.split("."))
    except (AttributeError, ValueError):
        return False


# R2-T15 (S-154, H-7): a check-change ruling passes only the comparison it names, one fixed name per route
RULING_NOT_COMPARED, RULING_CHANGED = "workflows-not-compared", "workflows-changed"


def recorded_coverage(entry):
    """R2-T15 (S-152): a shared root's per-Aget coverage as recorded, or None. `covered: false` makes a member
    PUBLISHED-NO-CI only with its source and the principal's typed line beside it (as a recorded ruling has them);
    without them it reads as not recorded."""
    if not isinstance(entry, dict) or not isinstance(entry.get("covered"), bool):
        return None
    if entry["covered"] is False and not all(isinstance(entry.get(k), str) and entry[k].strip()
                                             for k in ("line", "source")):
        return None
    return entry["covered"]


def recorded_ruling(value):
    """The member's check-change rulings when they have the shape record_authority.py writes, else None: a non-empty
    mapping of check names to entries that each hold a non-empty text `change` and a non-empty text `line` (the
    principal's typed line); a number, a list or a mapping in either field is not a ruling. A bare word, an empty mapping or an entry without its line is not a ruling, so it does not pass an
    unmade or a changed comparison. This shape reader does not search the line in a transcript. classify() separately requires the
    comparison name: workflows-not-compared or workflows-changed; another name passes neither comparison."""
    if not isinstance(value, dict) or not value:
        return None
    for entry in value.values():
        if not (isinstance(entry, dict) and isinstance(entry.get("change"), str) and entry["change"].strip()
                and isinstance(entry.get("line"), str) and entry["line"].strip()):
            return None
    return value


def pre_migration_revision(root, prefix, sha):
    """The parent of the newest commit (reachable from sha) that moved version.json to >= TARGET, or None when no
    such commit is found (observe() then records the workflow checks as not compared)."""
    r = git(root, "log", "--format=%H", sha, "--", f"{prefix}.aget/version.json")
    if r.returncode != 0:
        return None
    for c in r.stdout.split():
        if at_or_past(version_at(root, prefix, c)) and not at_or_past(version_at(root, prefix, f"{c}^")):
            p = git(root, "rev-parse", f"{c}^")
            return p.stdout.strip() if p.returncode == 0 else None
    return None


def workflows_tree(root, rev):
    """Return the tree listing of .github/workflows at a revision, or None when it cannot be read."""
    r = git(root, "ls-tree", "-r", rev, "--", ".github/workflows")
    return r.stdout if r.returncode == 0 else None


def is_ancestor(root, a, b):
    """Return True when revision a is an ancestor of revision b."""
    return git(root, "merge-base", "--is-ancestor", a, b).returncode == 0


def blob(repo, rev, path):
    """Return the blob id of a path at a revision, or None when the path is absent there. B193 finding 3: the id is
    read with its mode (`ls-tree`), and only a regular file's id is returned as is; a link, folder or submodule entry
    returns its mode with the id, so it never equals a regular release blob. A failed listing raises Unavailable,
    never absence."""
    try:          # bytes, decoded with the file-system decoding: text mode would turn a `\r` in a name into `\n`
        r = CI.read_git(repo, "--literal-pathspecs", "ls-tree", "-z", rev, "--", path, timeout=60)
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise Unavailable(f"{path} at {rev} in {repo} cannot be listed ({exc})") from None
    if r.returncode != 0:
        raise Unavailable(f"{path} at {rev} in {repo} cannot be listed (exit {r.returncode})")
    for entry in (e for e in os.fsdecode(r.stdout).split("\0") if e):
        meta, _, name = entry.partition("\t")
        if name == path:
            mode, typ, oid = (meta.split() + ["", "", ""])[:3]
            return oid if typ == "blob" and mode in ("100644", "100755") else f"{mode} {typ} {oid}"
    return None


# Version carriers are Aget-specific by design; the version check reads .aget/version.json; the blob comparison skips every carrier.
CARRIERS = set(W.VERSION_FILES) | {"CLAUDE.md"}


def resolve_template(loc, name=None, records=None):
    """(template, route) or (None, reason). A principal template ruling recorded for `name` in records.json
    `templates` wins and is reported as such; without one, the sources below are read and any disagreement is a
    CONFLICT. Same order as wave_readiness.resolve_template, but a named template whose repository does not exist
    is NOT USABLE and the next source is tried. wave_readiness raises there instead (measured 2026-09-27:
    `template: "agent"` -> `git tag` exit 128 -> no archetype fallback), which may explain part of the next-batch
    packet's Tier D."""
    fw = W.V.framework_root()

    def usable(name):
        if not isinstance(name, str) or not name:
            return None
        name = name if name.startswith("template-") else f"template-{name.replace('_', '-')}-aget"
        # C2e (D-8, S-333): a template is a folder directly in the framework root, never a path and never a link out
        if os.sep in name or "/" in name or name in (".", ".."):
            return None
        repo = os.path.join(fw, name)
        if os.path.islink(repo) or not os.path.isdir(repo) \
                or Path(repo).resolve().parent != Path(fw).resolve():
            return None
        tags = git(repo, "tag").stdout.split()
        return name if {R.FROM_TAG, R.TO_TAG} <= set(tags) else None

    ruling = ((records if records is not None else load_json(RECORDS, {})).get("templates") or {}).get(name or "")
    if ruling:
        t = usable(ruling.get("template")) if ruling.get("source") else None
        if t:
            return t, f"principal ruling ({ruling['source']})"
        return None, f"recorded template ruling unusable or unsourced: {ruling.get('template')!r}"

    try:
        vj = json.loads(Path(loc, ".aget", "version.json").read_text())
    except (OSError, ValueError):
        vj = {}
    try:
        m = yaml.safe_load(Path(loc, "manifest.yaml").read_text()) or {}
        if not isinstance(m, dict):
            m = {}
    except (OSError, yaml.YAMLError):
        m = {}
    mt = (m.get("template") or {}).get("name") if isinstance(m.get("template"), dict) else None

    def manifest_key(key):
        # top level, or one block down (measured: `composition.base_template` at one Aget,
        # `template_origin` inside the identity block at one Aget)
        if isinstance(m.get(key), str):
            return m[key], f"manifest.yaml {key}"
        for block, value in m.items():
            if isinstance(value, dict) and isinstance(value.get(key), str):
                return value[key], f"manifest.yaml {block}.{key}"
        return None, f"manifest.yaml {key}"

    candidates = [(vj.get("template"), "version.json template"),
                  (mt, "manifest.yaml template.name"),
                  manifest_key("base_template"),
                  manifest_key("template_origin"),
                  (vj.get("archetype"), f"INFERRED from archetype {vj.get('archetype')!r}")]
    found = [(usable(name), route) for name, route in candidates]
    found = [(t, route) for t, route in found if t]
    # Sources that name different usable templates are a CONFLICT, never a choice: the 2026-09-26
    # next-batch packet found one Aget with archetype worker and manifest advisor.
    if len({t for t, _ in found}) > 1:
        return None, "template sources disagree: " + "; ".join(f"{r} -> {t}" for t, r in found)
    if found:
        return found[0]
    return None, (f"no usable template (version.json template={vj.get('template')!r}, "
                  f"archetype={vj.get('archetype')!r})")


def payload_expectations(template):
    """{path: 'present' | 'absent'} for one template's payload at the release target."""
    fw = W.V.framework_root()
    try:                                  # B159 finding 1: NUL-separated, byte for byte
        records = CI.git_name_status(os.path.join(fw, template), "-M", R.FROM_TAG, R.TO_TAG)
    except CI.InspectionFailed as e:
        raise Unavailable(f"template diff unavailable or malformed: {e}") from None
    exp = {}
    for status, paths in records:
        if status[:1] == "D":
            exp.setdefault(paths[0], "absent")
        elif status[:1] == "R":
            exp.setdefault(paths[0], "absent")
            exp[paths[1]] = "present"
        else:
            exp[paths[-1]] = "present"
    for p in W.SPEC_PATHS + W.CORRECTION_ROW_4:
        exp[p] = "present"
    return exp


def payload_findings(root, prefix, sha, template, expectations, recorded):
    """Findings for payload paths other than the version carriers: an unrecorded path that does not meet its
    expectation (absent, or equal by blob id to a release source), or a recorded path whose record is not bound
    to what the revision holds there (its blob id, or 'absent')."""
    fw = W.V.framework_root()
    sources =[(os.path.join(fw, template), R.TO_TAG), (os.path.join(fw, "aget"), R.TO_TAG)]
    findings = []
    for path, want in sorted(expectations.items()):
        if path in CARRIERS:
            continue
        have = blob(root, sha, prefix + path)
        if path in recorded:
            # A record covers the exact bytes it was made for; a later change to the path is a new
            # finding, not silently still "recorded" (2026-09-27, prompted by the producer's question
            # whether to record before or after its repair revision).
            bound = recorded[path].get("blob")
            if not bound:
                findings.append(f"{path}: recorded without a blob binding")
            elif bound != (have or "absent"):
                findings.append(f"{path}: recorded for blob {bound[:8]}, revision holds {(have or 'absent')[:8]}")
            continue
        try:                              # design read 2, D-3 (S-283): a closed set; an unknown label is a finding
            want = IM.expectation(path, want)
        except IM.UnknownClassification as e:
            findings.append(str(e))
            continue
        if want == "absent":
            if have is not None:
                findings.append(f"{path}: present, release removes it")
            continue
        if have is None:
            findings.append(f"{path}: absent at the revision")
            continue
        if " " in have:      # B194 finding 3: an ordinary file is required, whatever kind the sources hold there
            findings.append(f"{path}: the revision holds a {have.split()[0]} entry, not a regular file")
            continue
        if not any(blob(repo, tag, path) == have for repo, tag in sources):
            findings.append(f"{path}: differs from every release source")
    return findings


RUN_LIMIT = 50   # B184 finding 1: `gh run list --limit`; a list that reaches it is not the whole population by itself


def _run_list(root, sha):
    """The runs on `sha`, or None when the query failed (any error, timeout or unreadable output). B184 finding 1 with
    FWK-OVSR5's C2a4 advisory (5): output that is not a list of objects is unreadable (None), never an empty list."""
    try:
        r = subprocess.run(["gh", "run", "list", "--commit", sha, "--limit", str(RUN_LIMIT),
                            "--json", "status,conclusion,workflowName,workflowDatabaseId"],
                           cwd=root, capture_output=True, text=True, timeout=60)
        rows = json.loads(r.stdout) if r.returncode == 0 else None
        return rows if isinstance(rows, list) and all(isinstance(x, dict) for x in rows) else None
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None


def _workflow_paths(root):
    """B181 finding 3: {workflow id: committed path} for the repository's workflows (`gh workflow list --all`; the
    Actions API gives a workflow's `path` as the file's path in the repository, e.g. `.github/workflows/ci.yml`, read
    2026-10-04), or None when the query failed. A run is bound to a workflow by its `workflowDatabaseId`."""
    try:
        r = subprocess.run(["gh", "workflow", "list", "--all", "--limit", "500", "--json", "id,path"],
                           cwd=root, capture_output=True, text=True, timeout=60)
        rows = json.loads(r.stdout or "[]") if r.returncode == 0 else None
        return {x["id"]: x["path"] for x in rows} if isinstance(rows, list) else None
    except (OSError, subprocess.TimeoutExpired, ValueError, KeyError, TypeError):
        return None


def _api_run_count(root, sha):
    """An independent count: the Actions REST endpoint's `total_count` for head_sha, or None on any failure."""
    try:
        r = subprocess.run(["gh", "api", f"repos/{{owner}}/{{repo}}/actions/runs?head_sha={sha}&per_page=1",
                            "--jq", ".total_count"], cwd=root, capture_output=True, text=True, timeout=60)
        return int(r.stdout.strip()) if r.returncode == 0 else None
    except (OSError, subprocess.TimeoutExpired, ValueError):
        return None


def committed_workflows(root, sha):
    """R2-T3 (S-151, S-157, S-332): the root workflows committed at `sha`, as [(path, name)], read from the commit, never
    from the working tree (a workflow deleted there but not committed still runs in CI). `name` is the file's top-level
    `name:`, or its path when it has none (as GitHub names a run). [] when the commit has no `.github/workflows`."""
    # FWK-OVSR5's C2a4 advisory (2): absence is a listing that succeeded with no entry, never a failed probe
    probe = git(root, "ls-tree", "-z", sha, "--", ".github/workflows")
    if probe.returncode:
        raise Unavailable(f"whether {sha[:8]} has a workflow folder cannot be read")
    if not probe.stdout:
        return []
    r = git(root, "ls-tree", "-z", "--name-only", f"{sha}:.github/workflows")
    if r.returncode:
        raise Unavailable(f"the workflow folder at {sha[:8]} cannot be listed")
    out = []
    for n in sorted(x for x in r.stdout.split("\0") if x.endswith((".yml", ".yaml"))):
        path = f".github/workflows/{n}"
        try:                                           # B191 finding 1: a workflow is a regular file at the commit
            b = CI.git_blob_at(root, sha, path)
        except CI.InspectionFailed as e:
            raise Unavailable(f"the workflow {path} at {sha[:8]}: {e}") from None
        if b is None:
            raise Unavailable(f"the workflow {path} is listed at {sha[:8]} but cannot be read")
        m = re.search(r"^name:\s*(.+?)\s*$", b.decode(errors="replace"), re.M)
        out.append((path, m.group(1).strip("'\"") if m else path))
    return out


def ci_result(root, sha, online, retry_delay=3.0, workflows=None):
    """CI on exactly `sha`. A failed query is QUERY-FAILED (classified INCONCLUSIVE), never NO-RUN.

    Defect fixed 2026-09-28 (principal: "a failed query reads INCONCLUSIVE, never CI-NO-RUN"): at 09:57:58 an online
    run read one Aget as CI-NO-RUN while run 36449344994 had succeeded on that SHA; the rerun at 09:59:09
    read VERIFIED. An empty list with exit 0 was taken as proof of no run. Now an empty list counts as NO-RUN only
    when a retry is still empty AND the independent REST count is exactly 0; any failure or disagreement is
    QUERY-FAILED. Absence has to be shown twice, by two routes; presence once is enough."""
    if not online:
        return "NOT-QUERIED", ""
    runs = _run_list(root, sha)
    if runs is None:
        return "QUERY-FAILED", "gh run list failed"
    if not runs:
        time.sleep(retry_delay)
        again, count = _run_list(root, sha), _api_run_count(root, sha)
        if again:
            runs = again
        elif again is None or count is None:
            return "QUERY-FAILED", "empty run list, and the confirming query failed"
        elif count != 0:
            return "QUERY-FAILED", f"empty run list twice, but the REST count is {count}"
        else:
            return "NO-RUN", "no run on this SHA (run list empty twice; REST total_count 0)"
    if len(runs) >= RUN_LIMIT:
        # B184 finding 1 (DESIGN.md:300): a run list that reaches its limit may hide runs beyond it; it counts only
        # when the independent REST count names exactly as many runs on the SHA
        count = _api_run_count(root, sha)
        if count != len(runs):
            return "QUERY-FAILED", (f"the run list reached its limit ({RUN_LIMIT}) and the REST count is "
                                    f"{count if count is not None else 'unreadable'}, so runs may be unseen")
    if any(x.get("status") != "completed" for x in runs):
        return "PENDING", ""
    bad = sorted({x.get("workflowName", "?") for x in runs if x.get("conclusion") != "success"})
    if bad:
        return "FAIL", ", ".join(bad)
    # R2-T3: every workflow committed at this SHA has a successful run; a success elsewhere does not stand for it.
    # B181 finding 3: a run covers the committed workflow whose PATH it ran (DESIGN.md:436), never one that merely
    # shares its display name; a run whose path cannot be established covers nothing
    if workflows and any("path" not in x for x in runs):
        ids = _workflow_paths(root)
        if ids is None:
            return "QUERY-FAILED", "the workflow list (run -> workflow path) could not be read"
        runs = [x if "path" in x else {**x, "path": ids.get(x.get("workflowDatabaseId"))} for x in runs]
    names = [name for _, name in (workflows or [])]
    shared = sorted({n for n in names if names.count(n) > 1})   # B179 finding 1: one run cannot be told to cover each
    if shared:
        return "INCOMPLETE", f"committed workflows share a name ({shared}), so a run cannot be matched to each"
    ran = {x.get("path") for x in runs if isinstance(x.get("path"), str)}
    missing = sorted(name for path, name in (workflows or []) if path not in ran)
    if missing:
        return "INCOMPLETE", f"no run on this SHA for {missing}"
    return "PASS", f"{len(runs)} run(s)"


# ------------------------------------------------------------------ classification (pure)

def usable_template(loc, name=None, records=None):
    """C2e (D-8, S-216/S-277/S-350): the template a member's payload is judged against, for the list, the launch and
    the ledger alike. A template only INFERRED from the archetype is a guess, not a source: unmet, with the reason
    (record a template ruling). Returns (template or None, route or reason)."""
    tpl, route = resolve_template(loc, name) if records is None else resolve_template(loc, name, records)
    if tpl and str(route).startswith("INFERRED"):
        return None, f"template only {route} (an inferred route is unmet; record a template ruling)"
    return tpl, route


def classify(o):
    """(state, reason) from one Aget's observations. Order is the goal's order of conditions."""
    ex = o.get("exclusion")
    if ex:
        if not ex.get("ruling_quote") or not ex.get("source"):
            return "INCONCLUSIVE", "exclusion recorded without a quoted ruling and its source"
        if ex.get("reason_class") in DISALLOWED_EXCLUSION_REASONS or not ex.get("reason_class"):
            return "EXCLUSION-INVALID", f"reason class {ex.get('reason_class')!r} does not count"
        return "EXCLUDED", ex["reason_class"]
    if o.get("unavailable"):
        return "INCONCLUSIVE", o["unavailable"]
    if not at_or_past(o.get("remote_version")):
        if at_or_past(o.get("local_version")):
            return "UNPUBLISHED", f"remote {o.get('remote_version')}, local {o.get('local_version')}"
        return "NOT-MIGRATED", f"remote {o.get('remote_version')}"
    if not o.get("template"):
        return "INCONCLUSIVE", f"payload unverifiable: {o.get('template_reason')}"
    if o.get("payload_findings"):
        f = o["payload_findings"]
        return "PAYLOAD-NONCONFORMING", f"{len(f)} path(s): {f[0]}" + (" …" if len(f) > 1 else "")
    if not o.get("receipt_terminal"):
        return "NO-RECEIPT", "no ingested receiver terminal"
    # R2 (wrapper r7 F-1): a terminal counts only when it is on the closed success list, by exact string; and, on the
    # records route, only when the receipt at its revision, read by the receipt grammar, holds it.
    if o.get("receipt_read_error"):
        return "RECEIPT-NOT-SUCCESS", o["receipt_read_error"]
    if o["receipt_terminal"] not in RBND.SUCCESS["receiver_terminal"]:
        return "RECEIPT-NOT-SUCCESS", f"the receiver's terminal is {o['receipt_terminal']!r}, not a success"
    if o.get("receipt_unconfined"):     # C2e (D-8, S-331): the unconfined source is named
        return "RECEIPT-NOT-ON-REVISION", ("ingested receipt source outside the inventory folder: "
                                           + ", ".join(o["receipt_unconfined"])[:200])
    if not o.get("receipt_on_revision"):
        return "RECEIPT-NOT-ON-REVISION", "ingested receipt revision is not in the published revision"
    if not o.get("root_workflows"):
        return "PUBLISHED-NO-CI", "no workflow at the repository root"
    if o.get("shared_root"):
        cov = o.get("coverage")
        if cov is None:
            return "SHARED-ROOT-UNRESOLVED", "shared root; per-Aget coverage not recorded"
        if cov is False:
            return "PUBLISHED-NO-CI", "shared root workflow recorded as not covering this Aget"
    rulings = o.get("check_change_ruling") or {}
    if not o.get("checks_compared") and RULING_NOT_COMPARED not in rulings:
        # Not compared is not "unchanged". Only a check-change ruling naming this comparison passes it (R2-T15,
        # S-154); a ruling naming another check does not. A tightening review does not pass it.
        return "INCONCLUSIVE", ("workflow checks not compared with the pre-migration revision "
                                f"({o.get('checks_not_compared') or 'no comparison recorded'}); "
                                f"no check-change ruling named {RULING_NOT_COMPARED!r} recorded for this Aget")
    if o.get("checks_changed") and RULING_CHANGED not in rulings:
        # A change passes without a principal ruling only when a review recorded for THIS exact
        # workflow tree classifies it as tightening (the fleet migration outcome voids loosening, not all change).
        rv = o.get("check_change_review") or {}
        bound = rv.get("workflows_tree_sha256") == o.get("workflows_tree_sha256")
        if not (bound and rv.get("classification") == "tightening" and rv.get("evidence")):
            return "CHECKS-CHANGED", (f"workflows differ from the pre-migration revision; no ruling named "
                                      f"{RULING_CHANGED!r}, and no tightening review bound to this workflow tree")
    ci, detail = o.get("ci", ("NOT-QUERIED", ""))
    if ci in ("QUERY-FAILED", "UNREACHABLE"):
        return "INCONCLUSIVE", f"CI query failed ({detail or ci}); unreadable evidence is never a state"
    if ci == "PASS":
        return "VERIFIED", detail
    if ci == "FAIL":
        return "PUBLISHED-NOT-VERIFIED", f"failed: {detail}"
    return f"CI-{ci}", detail


# ------------------------------------------------------------------ assembly

def load_json(path, default):
    """Return the parsed JSON file, or the default when it is missing or unreadable."""
    try:
        return json.loads(Path(path).read_text())
    except (OSError, ValueError):
        return default


def _inside(path, folder):
    """True when `path`, every link resolved, lies inside `folder` (resolved)."""
    try:
        return Path(path).resolve().is_relative_to(Path(folder).resolve())
    except (OSError, ValueError, RuntimeError):
        return False


def ingestion_index(records=None):
    """Receipts by Aget: the ingestion route's MATCH-bound terminal claims, plus receipts recorded in
    records.json `receipts` for Agets that are not on that route (this Aget's self-migration, the
    producer's). A recorded receipt needs its terminal, receipt_revision and validation source."""
    d = load_json(OPSTATE, {})
    out = {}
    for name, rec in ((records or {}).get("receipts") or {}).items():
        if rec.get("terminal") and rec.get("receipt_revision") and rec.get("source"):
            out[name] = {"terminal": rec["terminal"], "receipt_revisions": [rec["receipt_revision"]]}
            if rec.get("attempt") or rec.get("receipt_path"):        # R2: what the ledger re-reads (SOP B11)
                out[name].update(attempt=rec.get("attempt"), receipt_path=rec.get("receipt_path"))
            out[name]["route"] = "records"
    for a in d.get("agents", []) or []:
        claim = (a.get("claims") or {}).get("receiver_terminal") or {}
        if claim.get("effective") and claim.get("binding") == "MATCH":
            srcs = [(d.get("sources") or {}).get(s) or {} for s in claim.get("sources", [])]
            revs, unconfined = [], []
            for s in srcs:
                # C2e (D-8, S-331): a source is read only inside the inventory folder; one that resolves outside it
                # (a `..` path, an absolute path, a link out) makes the claim unmet and is named
                if s.get("path") and not _inside(REPO / s["path"], OPSTATE.parent):
                    unconfined.append(str(s["path"]))
                    continue
                ev = load_json(REPO / s["path"], {}) if s.get("path") else {}
                if ev.get("receipt_revision"):
                    revs.append(ev["receipt_revision"])
            out[a["agent"]] = {"terminal": claim["effective"], "receipt_revisions": [] if unconfined else revs,
                               "unconfined": unconfined}
    return out


def reread_receipt(root, prefix, ing):
    """R2, records route: None when the receipt at its recorded revision, in the recorded attempt's section, holds
    exactly the recorded terminal; else why. An entry without `attempt` or `receipt_path` is unmet."""
    if not ing.get("attempt") or not ing.get("receipt_path"):
        return "records.json names no attempt or receipt_path for this receipt; the terminal cannot be re-read"
    rev = ing["receipt_revisions"][0]
    try:                  # B189 finding 1: a regular file at the revision only (B166 finding 2: no lazy fetch)
        p = CI.git_blob_at(root, rev, f"{prefix}{ing['receipt_path']}")
    except CI.InspectionFailed as e:
        return f"the receipt at {rev[:8]}: {e}"
    if p is None:
        return f"the receipt {ing['receipt_path']} is not at {rev[:8]}"
    value, why = RBND.receipt_terminal(p, ing["attempt"])
    if why:
        return f"receipt terminal: {why}"
    if value != ing.get("terminal"):
        return f"records.json says {ing.get('terminal')!r}, the receipt at {rev[:8]} holds {value!r}"
    return None


def observe(name, loc, records, ingested, sharing, online):
    """Gather what can be observed about one member: exclusion, remote revision, versions, template, payload, CI."""
    o = {"exclusion": (records.get("exclusions") or {}).get(name)}
    if o["exclusion"]:
        return o
    try:
        root = census.repo_root(loc)
        if not root:
            raise Unavailable("not in a git repository")
        prefix = git(loc, "rev-parse", "--show-prefix").stdout.strip()
        branch, sha = remote_head(root)
        o.update(branch=branch, sha=sha)
        if not has_commit(root, sha):
            raise Unavailable(f"remote revision {sha[:8]} not present locally (not fetched)")
        o["remote_version"] = version_at(root, prefix, sha)
        o["local_version"] = version_at(root, prefix, "HEAD")
        if not at_or_past(o["remote_version"]):
            return o
        o["template"], o["template_reason"] = usable_template(loc, name, records)       # C2e (D-8, S-350)
        if o["template"]:
            recorded = (records.get("deviations") or {}).get(name) or {}
            o["payload_findings"] = payload_findings(root, prefix, sha, o["template"],
                                                     payload_expectations(o["template"]), recorded)
        ing = ingested.get(name) or {}
        o["receipt_terminal"] = ing.get("terminal")
        if ing.get("route") == "records":
            o["receipt_read_error"] = reread_receipt(root, prefix, ing)
        o["receipt_on_revision"] = bool(ing.get("receipt_revisions")) and all(
            is_ancestor(root, r, sha) for r in ing["receipt_revisions"])
        o["receipt_unconfined"] = list(ing.get("unconfined") or [])          # C2e (D-8, S-331)
        wfs = committed_workflows(root, sha)            # R2-T3: the committed workflows, not the working tree's
        o["root_workflows"] = len(wfs)
        o["shared_root"] = sharing.get(root, 0) > 1
        o["coverage"] = recorded_coverage((records.get("ci_coverage") or {}).get(name))   # R2-T15 (S-152)
        pre = pre_migration_revision(root, prefix, sha)
        tree = workflows_tree(root, sha)
        pre_tree = workflows_tree(root, pre) if pre is not None else None
        # True only when the pre-migration revision was found and both workflow trees were read.
        o["checks_compared"] = pre_tree is not None and tree is not None
        if not o["checks_compared"]:
            o["checks_not_compared"] = ("pre-migration revision not found" if pre is None else
                                        "workflow tree unreadable at the pre-migration or the published revision")
        o["checks_changed"] = o["checks_compared"] and pre_tree != tree
        o["workflows_tree_sha256"] = hashlib.sha256((tree or "").encode()).hexdigest()
        o["check_change_ruling"] = recorded_ruling((records.get("check_change_rulings") or {}).get(name))
        o["check_change_review"] = (records.get("check_change_reviews") or {}).get(name)
        if o["root_workflows"]:
            o["ci"] = ci_result(root, sha, online, workflows=wfs)
    except Unavailable as exc:
        o["unavailable"] = str(exc)
    return o


def build(online=False, only=None):
    """Return classified ledger rows for pinned-register members selected by the optional only filter."""
    seats = members()
    if len(seats) != PINNED_MEMBERS:
        raise Unavailable(f"pinned membership is {len(seats)}, expected {PINNED_MEMBERS}")
    records = load_json(RECORDS, {})
    ingested = ingestion_index(records)
    sharing = {}
    for _, loc in seats:
        root = census.repo_root(loc)
        if root:
            sharing[root] = sharing.get(root, 0) + 1
    rows = []
    for name, loc in sorted(seats):
        if only and name not in only:
            continue
        o = observe(name, loc, records, ingested, sharing, online)
        state, reason = classify(o)
        rows.append({"aget": name, "state": state, "terminal": state in TERMINAL, "reason": reason,
                     "revision": o.get("sha"), "branch": o.get("branch"),
                     "template": o.get("template"), "template_route": o.get("template_reason"),
                     "payload_findings": o.get("payload_findings") or [],
                     "checks_compared": o.get("checks_compared")})
    return rows


def totals(rows):
    """Return the number of rows in each state, sorted by state name."""
    out = {}
    for r in rows:
        out[r["state"]] = out.get(r["state"], 0) + 1
    return dict(sorted(out.items()))


def main(argv=None):
    """Command-line entry point: print the per-Aget ledger and optionally write it as JSON."""
    R.require(pin=True)
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--online", action="store_true", help="query CI runs per revision (gh; network)")
    ap.add_argument("--json", type=Path, help="write the ledger document here")
    ap.add_argument("--only", nargs="*", help="restrict to these Agets (totals then cover only them)")
    a = ap.parse_args(argv)
    try:
        rows = build(a.online, set(a.only) if a.only else None)
    except Unavailable as exc:
        print(f"cannot produce the ledger: {exc}", file=sys.stderr)
        return 2
    for r in rows:
        print(f"{r['state']:24s} {r['aget']:42s} {(r['revision'] or '-')[:8]:8s} {r['reason']}")
    t = totals(rows)
    unmet = sum(1 for r in rows if not r["terminal"])
    print(f"\nrows {len(rows)} (pinned register {PIN[:8]}, target {TARGET}); terminal "
          f"{len(rows) - unmet}, unmet {unmet}")
    print("  " + " · ".join(f"{k} {v}" for k, v in t.items()))
    if not a.online:
        print("CI results NOT QUERIED (run with --online): no row can be VERIFIED from this run.")
    if a.json:
        doc = {"schema": "v335_fleet_ledger/1", "target": TARGET, "pinned_register": PIN,
               "online": a.online, "generated_at": dt.datetime.now(dt.timezone.utc).isoformat(),
               "rows": rows, "totals": t}
        a.json.write_text(json.dumps(doc, indent=2) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
