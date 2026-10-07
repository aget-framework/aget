#!/usr/bin/env python3
"""Prepare a batch's protected-write list for the principal's review (route a1; plan G3.2).

At the named Agets the code reads working-tree files and asks git whether a path is tracked; in the framework
clones it runs `git tag`, `git diff` and `git show`. It writes the list to the path named with --out. Keep that
path outside the named Agets' repositories (operator rule, not enforced by the tool).

For each Aget whose template resolves, each protected payload path expected present (`.claude/**` paths that the
template's diff between the release target's tags `v<from>` -> `v<to>` adds, changes or renames to, and those in the
kit's fixed `SPEC_PATHS` list in wave_readiness.py) is classified against the Aget's WORKING TREE, because skill files
are often untracked (gh#1569); the `AGENTS.md` version line is classified when `AGENTS.md` is a file, not a symlink:
  write         file absent, or identical to the template's `<from>` bytes and not already its `<to>` bytes
                -> the principal's script writes the `<to>` bytes and executable bit; equal bytes with a different
                release executable bit also use this write route
  write-upstream  differs from both tags, but is byte for byte one upstream release version of the path (an older
                untouched copy) -> written; nothing receiver-authored is lost. A file whose every line some upstream
                version holds, but which equals none of them (lines deleted, reordered, re-indented or repeated), is
                `hold` with 0 authored lines: the difference may be the receiver's own
  noop          already identical to the template's bytes and executable bit at the target release tag; AGENTS.md:
                that release's version line is present and the earlier release's is absent
  hold          has authored lines (in no upstream release version). Never overwritten; listed, with the count,
                for a merge decision
  replace-line  AGENTS.md: exactly one `@aget-version: <from>` line becomes `@aget-version: <to>`
  hold-line     AGENTS.md: that line is not present exactly once (noop instead when it is absent and the
                `@aget-version: <to>` line is present with no surrounding whitespace)
Each entry, except a `hold` for a path with no `<to>`-tag source in the template, records `pre` (a sha256 for the file
now, or `absent`) and `post` (the sha256 expected after the apply step; equal to `pre` when nothing is written). The
apply script refuses an Aget when the file of an entry other than `hold` or `hold-line` does not match its recorded
digest, and the detective check (route (ii)) compares, after the receiver's run, the files the apply receipt records
as written with `post`.

Usage (repository root):
    python3 scripts/migration_kit/prepare_batch.py --batch 1 --out <list.json> NAME [NAME ...]
"""
import argparse
import sys
import datetime as dt
import hashlib
import importlib.util
import json
import os
import subprocess
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import release_target as R  # noqa: E402  (the kit's one release parameter; carriage row 24)
import copy_isolation as CI  # noqa: E402  (destination_refusal: a write never goes through a link)
import item_meaning as IM  # noqa: E402  (R3: one meaning table per classification)

HERE = Path(__file__).resolve().parent
_s = importlib.util.spec_from_file_location("v335_fleet_ledger", HERE / "fleet_ledger.py")
L = importlib.util.module_from_spec(_s)
_s.loader.exec_module(L)

OLD, NEW = R.FROM, R.TO
VERSION_LINE = "@aget-version: {}"
UPSTREAM = {}


def protected(path):
    """Return True for a protected path: anything under .claude/, or AGENTS.md or CLAUDE.md."""
    return path.startswith(".claude/") or path in ("AGENTS.md", "CLAUDE.md")


def sha_bytes(b):
    """Return the SHA-256 hex digest of the bytes, or 'absent' when given None."""
    return hashlib.sha256(b).hexdigest() if b is not None else "absent"


def tag_bytes(repo, tag, path):
    """Return the bytes of a path at a tag in the repository, or None when it is absent there. B191 finding 1: only a
    regular file at the tag is release bytes; a link, folder, submodule or failed read raises InspectionFailed."""
    return CI.git_blob_at(repo, tag, path)


class UpstreamLines(set):
    """The stripped lines of every upstream release version of a path, with `digests`: the SHA-256 of each
    version's bytes. A plain set (no `digests`) matches no version."""

    def __init__(self, lines=(), digests=()):
        super().__init__(lines)
        self.digests = set(digests)


def classify_file(current, old, new, upstream_lines=None):
    """(op, authored_line_count). A line is AUTHORED only if no upstream release version of this path holds it (the
    pilot baselines' definition). `write-upstream` only when the file is byte for byte one upstream release version
    (its SHA-256 is in `upstream_lines.digests`): replacing it loses nothing. A file with 0 authored lines that equals
    no upstream version (lines deleted, reordered, re-indented or repeated) is `hold` with 0: the line set cannot
    tell the receiver's own change from an older copy."""
    if current is not None and new is not None and current == new:
        return "noop", 0
    if current is None or (old is not None and current == old):
        return "write", 0
    if upstream_lines is None:
        return "hold", None
    authored = [ln for ln in current.decode("utf-8", "replace").splitlines()
                if ln.strip() and ln.strip() not in upstream_lines]
    if authored:
        return "hold", len(authored)
    if sha_bytes(current) in getattr(upstream_lines, "digests", ()):
        return "write-upstream", 0
    return "hold", 0


def upstream_line_set(path):
    """Stripped lines of `path` at every tag of every local template clone and core, with the SHA-256 of each of
    those versions' bytes (UpstreamLines.digests)."""
    fw = Path(L.W.V.framework_root())
    lines, digests = set(), set()
    for repo in sorted(p for p in fw.iterdir() if (p.name.startswith("template-") or p.name == "aget")
                       and (p / ".git").exists()):
        for t in subprocess.run(["git", "-C", str(repo), "tag"], capture_output=True, text=True).stdout.split():
            b = tag_bytes(repo, t, path)
            if b is not None:
                lines.update(ln.strip() for ln in b.decode("utf-8", "replace").splitlines())
                digests.add(sha_bytes(b))
    return UpstreamLines(lines, digests)


def agents_line(text):
    """(op, new_text) for the AGENTS.md version carrier."""
    line_old, line_new = VERSION_LINE.format(OLD), VERSION_LINE.format(NEW)
    count = sum(1 for ln in text.splitlines() if ln.strip() == line_old)
    if VERSION_LINE.format(NEW) in text.splitlines() and count == 0:
        return "noop", text
    if count != 1:
        return "hold-line", None
    out = [line_new if ln.strip() == line_old else ln for ln in text.split("\n")]
    return "replace-line", "\n".join(out)


def prepare(name, loc):
    """Build one Aget's entry of the protected-write list: the operation for each protected payload path."""
    tpl, route = L.usable_template(loc, name)          # C2e (D-8, S-216): an inferred template blocks the member
    entry = {"aget": name, "location": loc, "template": tpl, "template_route": route, "head": CI.head_of(loc),
             "ops": []}
    if not tpl:
        entry["blocked"] = f"template unresolved: {route}"
        return entry
    fw = Path(L.W.V.framework_root()) / tpl
    exp = L.payload_expectations(tpl)
    for path, want in sorted(exp.items()):
        if not protected(path) or want != "present" or path == "AGENTS.md" or path == "CLAUDE.md":
            continue
        unsafe = CI.destination_refusal(loc, path)
        if unsafe:   # R3 (S-212, B131): `unsafe`, never a hold kind; never written
            entry["ops"].append({"path": path, "op": "unsafe", "why": f"unsafe path: {unsafe}"})
            continue
        f = Path(loc) / path
        cur = f.read_bytes() if f.is_file() else None
        old = tag_bytes(fw, R.FROM_TAG, path)
        release = CI.git_blob_at(fw, R.TO_TAG, path, with_mode=True)
        if release is None:
            entry["ops"].append({"path": path, "op": "hold", "kind": "no-source", "authored_lines": None,
                                 "why": f"no {R.TO_TAG} source in the template"})
            continue
        new, release_mode = release
        op, authored = classify_file(cur, old, new)
        # Equal bytes with a different executable bit are a protected write, not a noop.
        if op == "noop" and (0o755 if f.stat().st_mode & 0o100 else 0o644) != release_mode:
            op = "write"
        if op == "hold":
            op, authored = classify_file(cur, old, new, UPSTREAM.setdefault(path, upstream_line_set(path)))
        tracked = CI.git_tracked(loc, path)   # B166 finding 2; B183 finding 1: a failed read raises, never "untracked"
        o = {"path": path, "op": op, "tracked": tracked, "pre": sha_bytes(cur),
             "post": sha_bytes(new) if op in ("write", "write-upstream", "noop") else sha_bytes(cur),
             "authored_lines": authored, "source": f"{tpl}@{R.TO_TAG}:{path}", "source_sha256": sha_bytes(new),
             "release_mode": release_mode}
        if op == "hold":
            o["kind"] = IM.classify_kind(op, True, authored)
        entry["ops"].append(o)
    agents = Path(loc) / "AGENTS.md"
    if agents.is_file() and not agents.is_symlink():
        text = agents.read_text()
        op, new_text = agents_line(text)
        entry["ops"].append({"path": "AGENTS.md", "op": op, "pre": sha_bytes(text.encode()),
                             "post": sha_bytes(new_text.encode()) if new_text is not None else sha_bytes(text.encode()),
                             "source": f"version line {VERSION_LINE.format(OLD)} -> {VERSION_LINE.format(NEW)}"})
    claude = Path(loc) / "CLAUDE.md"
    entry["claude_md"] = ("symlink" if claude.is_symlink() else "file" if claude.is_file() else "absent")
    return entry


def main():
    """Command-line entry point: prepare a batch's protected-write list for the principal's review."""
    R.require()
    ap = argparse.ArgumentParser()
    ap.add_argument("--batch", required=True)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("names", nargs="+")
    a = ap.parse_args()
    locs = dict(L.members())
    doc = {"schema": "v335_protected_list/1", "batch": a.batch, "target": NEW,
           "prepared_at": dt.datetime.now().astimezone().isoformat(timespec="seconds"),
           "prepared_by": f"{R.SUPERVISOR} (read-only)",
           "apply_script_sha256": sha_bytes((HERE / "apply_protected.py").read_bytes()), "claude_version":
               subprocess.run(["claude", "--version"], capture_output=True, text=True).stdout.strip(),
           "agets": [prepare(n, os.path.expanduser(locs[n])) for n in a.names]}
    a.out.write_text(json.dumps(doc, indent=2) + "\n")
    for e in doc["agets"]:
        ops = [o["op"] for o in e["ops"]]
        print(f"{e['aget']:34s} {e.get('template') or '-':26s} " +
              " ".join(f"{k} {ops.count(k)}" for k in ("write", "write-upstream", "noop", "hold", "replace-line", "hold-line")
                       if ops.count(k))
              + (f"  BLOCKED: {e['blocked']}" if e.get("blocked") else "") + f"  CLAUDE.md {e.get('claude_md')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
