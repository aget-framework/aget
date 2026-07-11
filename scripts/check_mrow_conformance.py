#!/usr/bin/env python3
"""M-row conformance sweep across ALL release origins (gmelli/aget-aget#1871, half 3).

The v3.26.0 defect: C-26-09's delta landed canonical-only; all 13 template tags
shipped a check_skill_reliance_manifest.py that fails the M-3.26-6 detection —
per-item template staging was asserted per build row, never computed as a
closing sweep. This gate computes it: for each DEPLOYMENT_SPEC M/O-row whose
detection is a file-content clause (`grep -q '<pat>' <path>`), run the clause
against EVERY origin's tree at the given ref (staged HEAD pre-push at G4, or
the release tag post-hoc).

Rows whose detections test per-agent state (version pins: jq on .aget/,
AGENTS.md header) are reported SKIP-agent-state — they have no origin-payload
meaning. A file a given origin does not ship at all is ABSENT (informational);
shipping the file WITHOUT the pattern is FAIL (the #1871 defect shape).

Stdlib-only (#1660 import-closure discipline).

Usage:
  python3 scripts/check_mrow_conformance.py --version 3.26.0 --ref v3.26.0
  python3 scripts/check_mrow_conformance.py --version 3.26.0 --ref HEAD   # G4 pre-push sweep

Exit: 0 all conformant · 4 any FAIL row.
"""
import argparse
import glob
import os
import re
import subprocess
import sys

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
GREP_RE = re.compile(r"grep -q '([^']+)' ([\w./-]+)")


def git(repo, *args):
    r = subprocess.run(["git", "-C", repo] + list(args), capture_output=True, text=True)
    return r.returncode, r.stdout


def parse_rows(spec_text):
    """(row_id, detection, blocking) for mandatory_changes + optional_changes rows."""
    rows, section, cur_id, cur_blocking = [], None, None, True
    for line in spec_text.splitlines():
        m = re.match(r"^(mandatory_changes|optional_changes|additive_artifacts|deprecations):", line)
        if m:
            section = m.group(1)
            continue
        if re.match(r"^\w", line):
            section = None
        if section in ("mandatory_changes", "optional_changes"):
            s = line.strip()
            if s.startswith("- id:"):
                cur_id = s.split(":", 1)[1].strip().strip('"')
                cur_blocking = section == "mandatory_changes"
            elif s.startswith("blocking:"):
                cur_blocking = "true" in s
            elif s.startswith("detection:") and cur_id:
                rows.append((cur_id, s.split(":", 1)[1].strip().strip('"'), cur_blocking))
                cur_id = None
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--version", required=True)
    ap.add_argument("--ref", default=None, help="git ref per origin (default v<version>)")
    ap.add_argument("--spec-ref", default=None, help="ref to read the spec from on canonical (default --ref)")
    a = ap.parse_args()
    ref = a.ref or f"v{a.version}"
    spec_ref = a.spec_ref or ref

    rc, spec_text = git(REPO, "show", f"{spec_ref}:DEPLOYMENT_SPEC_v{a.version}.yaml")
    if rc != 0:
        sys.exit(f"ERROR: DEPLOYMENT_SPEC_v{a.version}.yaml not readable at {spec_ref} on canonical")

    checks, skipped = [], []
    for row_id, detection, blocking in parse_rows(spec_text):
        clauses = GREP_RE.findall(detection)
        if clauses:
            checks.append((row_id, clauses, blocking))
        else:
            skipped.append(row_id)

    origins = [REPO] + sorted(glob.glob(os.path.join(os.path.dirname(REPO), "template-*")))
    fails, warns, absents = [], [], 0
    for origin in origins:
        name = os.path.basename(origin)
        for row_id, clauses, blocking in checks:
            # OR-semantics across a detection's grep clauses on the SAME path;
            # AND across distinct paths (mirrors the spec's '&&' between files).
            by_path = {}
            for pat, path in clauses:
                by_path.setdefault(path, []).append(pat)
            for path, pats in by_path.items():
                rc, blob = git(origin, "show", f"{ref}:{path}")
                if rc != 0:
                    absents += 1
                    continue
                # grep -q patterns are regex (BRE): ^ anchors etc. — re.search
                # with MULTILINE is the equivalent, NOT literal substring.
                if not any(re.search(p, blob, re.MULTILINE) for p in pats):
                    (fails if blocking else warns).append((name, row_id, path))

    print(f"mrow-conformance v{a.version} @ {ref}: {len(origins)} origins × {len(checks)} content-rows "
          f"(SKIP-agent-state: {', '.join(skipped) or 'none'}; ABSENT cells: {absents})")
    for name, row_id, path in warns:
        print(f"  WARN {name}: {row_id} (non-blocking) — {path} ships without the detection pattern")
    if fails:
        print(f"FAIL rows (blocking): {len(fails)}")
        for name, row_id, path in fails:
            print(f"  FAIL {name}: {row_id} — {path} ships without the detection pattern")
        sys.exit(4)
    print(f"PASS — every origin shipping a payload file carries every blocking M-row delta at this ref"
          f"{' (non-blocking WARNs above)' if warns else ''}")


if __name__ == "__main__":
    main()
