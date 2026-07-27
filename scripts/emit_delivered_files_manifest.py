#!/usr/bin/env python3
"""Emit / verify a per-release delivered-files manifest (gmelli/aget-aget#1870).

Closes the v3.25 delivered-but-not-committed vector (#1828): the per-agent
payload commit staged from a static path list, so files delivered outside that
enumeration were silently left untracked on ~20 agents for 6 days.

Two halves, one source of truth:
  emit    — derive the payload file list from DEPLOYMENT_SPEC_vX.Y.Z.yaml rows,
            sha256 each file at the release ref, write
            handoffs/DELIVERED_FILES_vX.Y.Z.yaml
  verify  — on an upgraded agent tree, assert every manifest path that exists
            on disk is git-tracked (the post-stage porcelain cross-check that
            SOP_fleet_upgrade v1.10.0 G0.2 consumes). Untracked = exit 4.

Stdlib-only (#1660 import-closure discipline).

Usage:
  python3 scripts/emit_delivered_files_manifest.py --version 3.26.0 [--ref v3.26.0]
  python3 scripts/emit_delivered_files_manifest.py --verify /path/to/agent --version 3.26.0
"""
import argparse
import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime, timezone

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Payload path extraction: file paths named in a row's detection or description.
#
# ⚠ 2026-07-26: this regex named only `scripts/` and `.claude/skills/`, so it was
# STRUCTURALLY BLIND to `.claude/hooks/` — and v3.28.0's central deliverable was a
# PreToolUse hook. The manifest is the copy-list a fleet dispatch derives its
# add-list from, so an unmatched payload path is not an omission in a report: it is
# a file the fleet never receives. v3.28.0 emitted 2 rows for a 7-artifact payload
# and named neither the hook (M-3.28-2/-4) nor the traceability test (M-3.28-6).
# Directories are enumerated rather than globbed so a new payload location fails
# loudly here instead of vanishing from the copy-list.
PATH_RE = re.compile(
    r"(?:scripts|tests|rubrics|\.claude/(?:skills|hooks|agents)|\.aget/patterns)"
    r"/[\w./-]+\.(?:py|md|sh|yaml|json)"
)
# Rows whose detections test agent state edited in place (pins), not delivered files.
PIN_PATHS = {"M": [(".aget/version.json", "version pin"), ("AGENTS.md", "@aget-version pin")]}


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True)
    return r.returncode, r.stdout


def parse_spec_rows(spec_text):
    """Line-based parse of mandatory / optional / recommended / additive rows.

    `recommended_changes` is normalised to `optional_changes`: DEPLOYMENT_SPEC
    v3.28.0 used that heading for its two edge-checker rows and this parser did not
    recognise it, so both were dropped silently — the same blindness as an
    unmatched PATH_RE, one level up. An unknown section heading is a payload the
    fleet never sees, so the alternation is explicit rather than permissive.
    """
    rows, section, cur = [], None, None
    for line in spec_text.splitlines():
        s = line.strip()
        m = re.match(
            r"^(mandatory_changes|optional_changes|recommended_changes|additive_artifacts):",
            line,
        )
        if m:
            section = m.group(1)
            if section == "recommended_changes":
                section = "optional_changes"
            continue
        if re.match(r"^\w", line) and ":" in line and not line.startswith(" "):
            section = None
        if section and s.startswith("- id:"):
            cur = {"id": s.split(":", 1)[1].strip().strip('"'), "section": section, "text": ""}
            rows.append(cur)
        elif section and cur and s and not s.startswith("- id:"):
            cur["text"] += " " + s
    return rows


def payload_map(spec_text):
    """row id -> sorted payload paths named by that row."""
    out = {}
    for row in parse_spec_rows(spec_text):
        paths = sorted(set(PATH_RE.findall(row["text"])))
        # additive rows name canonical_source dirs; keep only concrete file paths
        if paths:
            out[row["id"]] = {"section": row["section"], "paths": paths}
    return out


def sha_at_ref(ref, path):
    rc, blob = git(REPO, "show", f"{ref}:{path}")
    if rc != 0:
        return None
    return hashlib.sha256(blob.encode()).hexdigest()


TEMPLATE_REPO = os.path.join(os.path.dirname(REPO), "template-worker-aget")
# Files the fleet receives that are pinned in place rather than copied; never manifest rows.
_PIN_BASENAMES = {".aget/version.json", "AGENTS.md", "CHANGELOG.md", "README.md"}


def prev_tag(version):
    """The release tag immediately preceding v{version} in the template repo."""
    rc, out = git(TEMPLATE_REPO, "tag", "--list", "v[0-9]*.[0-9]*.[0-9]*", "--sort=-v:refname")
    if rc != 0:
        return None
    tags = [t.strip() for t in out.splitlines() if t.strip()]
    try:
        return tags[tags.index(f"v{version}") + 1]
    except (ValueError, IndexError):
        return None


def template_shipped_paths(version):
    """Paths the FLEET actually receives, derived from the template tag diff.

    ⚠ 2026-07-26: this cross-check exists because the manifest was derived
    EXCLUSIVELY from DEPLOYMENT_SPEC M-rows, which means **anything shipped
    without an M-row naming it is invisible to the copy-list** — not flagged,
    not warned, simply absent. v3.28.0 shipped four fleet scripts
    (study_topic / check_initiatives / close_gate_check / wind_down, +585 lines,
    byte-identical canonical↔tag) that no M-row mentions. The emitted manifest
    listed six enforcement artifacts, every one ABSENT-AT-REF, and none of the
    four files agents were actually going to receive.

    A downstream seat deriving its add-list from that manifest, exactly as
    SOP_fleet_upgrade G0.2 instructs, would have staged **zero** fleet-facing
    files. Found by `private-supervisor-AGET`'s independent migration-prep audit, not
    by this producer.

    The spec is the contract, so a shipped-but-uncontracted file is a real
    finding in its own right — it is emitted as an additive row carrying
    NO-M-ROW so the gap is visible rather than silently absorbed.
    """
    prev = prev_tag(version)
    if not prev or not os.path.isdir(TEMPLATE_REPO):
        return None, None
    rc, out = git(TEMPLATE_REPO, "diff", "--name-only", prev, f"v{version}")
    if rc != 0:
        return None, prev
    paths = [p.strip() for p in out.splitlines() if p.strip()]
    return [p for p in paths if p not in _PIN_BASENAMES], prev


def emit(version, ref):
    rc, spec_text = git(REPO, "show", f"{ref}:DEPLOYMENT_SPEC_v{version}.yaml")
    if rc != 0:
        sys.exit(f"ERROR: DEPLOYMENT_SPEC_v{version}.yaml not readable at {ref}")
    pmap = payload_map(spec_text)

    sections = {"mandatory_changes": [], "optional_changes": [], "additive_artifacts": []}
    seen = {}
    for row_id, info in sorted(pmap.items()):
        for path in info["paths"]:
            key = (info["section"], path)
            if key in seen:
                seen[key]["spec_rows"].append(row_id)
                continue
            sha = sha_at_ref(ref, path)
            entry = {"path": path, "spec_rows": [row_id], "sha256": sha}
            seen[key] = entry
            sections[info["section"]].append(entry)

    # Cross-check against what the FLEET actually receives (see template_shipped_paths).
    shipped, prev = template_shipped_paths(version)
    uncontracted = []
    if shipped is not None:
        contracted = {p for (_sec, p) in seen}
        for path in sorted(set(shipped) - contracted):
            sha = sha_at_ref(ref, path)
            entry = {"path": path, "spec_rows": ["NO-M-ROW"], "sha256": sha}
            uncontracted.append(entry)
            sections["additive_artifacts"].append(entry)

    ts = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
    lines = [
        f"# DELIVERED_FILES_v{version}.yaml — machine-readable per-payload delivered-files manifest",
        "# Emit half of gmelli/aget-aget#1870 (closes the #1828 delivered-but-not-committed vector).",
        "# Consumer: SOP_fleet_upgrade G0.2 — commit add-list derives from THIS manifest;",
        "# post-stage porcelain cross-check asserts no manifest path remains untracked.",
        f'version: "{version}"',
        f'source_ref: "{ref}"  # canonical aget/ (payload-source ruling 2026-07-11: canonical, not template — see #1871)',
        f'generated: "{ts}"',
        'generator: "scripts/emit_delivered_files_manifest.py"',
        'tracking: "gmelli/aget-aget#1870"',
        "",
        "pin_edits:  # edited in place on the agent, not file-copied — outside the porcelain cross-check",
    ]
    if uncontracted:
        lines[4:4] = [
            f"# ⚠ {len(uncontracted)} file(s) ship to the fleet with NO M-row contracting them",
            f"#   (template diff {prev}..v{version}). They appear under additive_files with",
            "#   spec_rows: [NO-M-ROW]. Derive your add-list from the FULL manifest — a",
            "#   mandatory-rows-only reading of v3.28.0 yields zero fleet-facing files.",
            "#   The missing M-rows are a DEPLOYMENT_SPEC gap, owed to the next release.",
        ]
    for path, note in PIN_PATHS["M"]:
        lines.append(f'  - path: "{path}"  # {note}')
    for section, label in [
        ("mandatory_changes", "delivered_files"),
        ("optional_changes", "optional_files"),
        ("additive_artifacts", "additive_files"),
    ]:
        lines.append("")
        lines.append(f"{label}:")
        if not sections[section]:
            lines.append("  []")
            continue
        for e in sections[section]:
            lines.append(f'  - path: "{e["path"]}"')
            lines.append(f'    spec_rows: [{", ".join(e["spec_rows"])}]')
            sha = e["sha256"] if e["sha256"] else "ABSENT-AT-REF"
            lines.append(f'    sha256: "{sha}"')
    lines += [
        "",
        "verify_rule: |",
        "  Post-upgrade, every path in delivered_files, optional_files AND additive_files",
        "  present on the agent's disk MUST be git-tracked. `git status --porcelain` showing",
        "  any manifest path as untracked (??) is the #1828 defect class — the upgrade is NOT",
        "  complete until it is staged.",
        "",
        "  ⚠ additive_files is NOT optional to check. This rule enumerated only the first two",
        "  sections until 2026-07-26, when additive_files was added to carry payload no M-row",
        "  contracts — which for v3.28.0 is EVERY file the fleet actually receives. The header",
        "  said 'derive from the FULL manifest'; this rule, the half a consuming SOP mechanises,",
        "  still named two of three sections. Prose fixed, actuator not — inside the commit that",
        "  closed the previous instance of that same shape. Found by the manifest's first",
        "  consumer (`private-supervisor-AGET`) before it ran G0.2, not by the producer.",
    ]
    out_path = os.path.join(REPO, "handoffs", f"DELIVERED_FILES_v{version}.yaml")
    with open(out_path, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"wrote {out_path}")
    total = sum(len(v) for v in sections.values())
    print(f"rows: {total} file entries "
          f"(mandatory {len(sections['mandatory_changes'])}, optional {len(sections['optional_changes'])}, "
          f"additive {len(sections['additive_artifacts'])})")
    return out_path


def verify(agent_path, version):
    manifest = os.path.join(REPO, "handoffs", f"DELIVERED_FILES_v{version}.yaml")
    if not os.path.exists(manifest):
        sys.exit(f"ERROR: {manifest} missing — run emit first")
    paths = re.findall(r'^\s+- path: "([^"]+)"', open(manifest).read(), re.M)
    payload = [p for p in paths if p not in [x for x, _ in PIN_PATHS["M"]]]
    rc, tracked_out = git(agent_path, "ls-files")
    if rc != 0:
        sys.exit(f"ERROR: {agent_path} is not a git repository")
    tracked = set(tracked_out.splitlines())
    untracked, absent, ok = [], [], []
    for p in payload:
        on_disk = os.path.exists(os.path.join(agent_path, p))
        if not on_disk:
            absent.append(p)
        elif p in tracked:
            ok.append(p)
        else:
            untracked.append(p)
    print(f"verify {agent_path}: {len(ok)} tracked, {len(absent)} absent (not adopted), {len(untracked)} UNTRACKED")
    for p in untracked:
        print(f"  UNTRACKED (#1828 class): {p}")
    if untracked:
        sys.exit(4)
    print("PASS — no manifest-delivered file left untracked")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    ap.add_argument("--ref", default=None, help="git ref for emit (default: v<version>)")
    ap.add_argument("--verify", metavar="AGENT_PATH", help="verify an upgraded agent tree instead of emitting")
    a = ap.parse_args()
    if a.verify:
        verify(a.verify, a.version)
    else:
        emit(a.version, a.ref or f"v{a.version}")


if __name__ == "__main__":
    main()
