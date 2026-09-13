#!/usr/bin/env python3
"""Host-layout conformance against AGET_HOST_RUNTIME_SPEC (CAP-HFL-001..007).

Three subjects, checked separately:

  MANIFEST  CAP-HFL-002/004/006 -- every observed runtime artifact sits under the path its
            declared lifecycle class determines, and a region with NO governing rule is not
            graded at all.
  ROSTER    CAP-HFL-007 -- no node daemon executes from an agent's repo checkout; daemons run
            from deployed copies owned by the operator agent.
  ENVELOPE  CAP-HFL-005 -- the record/exhaust tier boundary, including the manifest-declared
            per-row record-predicate where one stream mixes tiers.

THREE OUTCOMES, AND THE THIRD IS THE POINT
------------------------------------------
  DRIFT             a governing rule exists and the observed layout violates it (CAP-HFL-004).
  MISSING-EVIDENCE  a rule exists but the artifact could not be read, so conformance is
                    UNKNOWN. Not a pass and not a violation.
  OUTSIDE-CONTRACT  no governing rule covers this region, so its disorder is NOT graded.
                    CAP-HFL-006 states this directly: **absence is not drift.** Grading an
                    ungoverned region is the failure mode this spec names, so it is reported
                    as a distinct, non-failing outcome and never counted as DRIFT.

SCOPE, per the selected outcome
-------------------------------
This is **the checker**, not the host initiative. It grades a layout supplied to it and makes no
claim that any node is deployed or enforced. A local fixture PASS is **not** deployed
enforcement: node deployment belongs to its authorized operator and must be verified at source.
The spec's behavioural V-tests are runtime-pending by design (ADR-007 honest testability); this
command is what makes them runnable once a layout exists.

Read-only. No writes, no network, no daemon control.

USAGE
  python3 scripts/check_host_layout_conformance.py --manifest layout_manifest.yaml --root .
  python3 scripts/check_host_layout_conformance.py --manifest m.json --root . --roster r.json
  python3 scripts/check_host_layout_conformance.py --manifest m.json --root . --json

EXIT CODES
  0  no DRIFT and no MISSING-EVIDENCE (OUTSIDE-CONTRACT regions may exist; they do not fail)
  1  at least one DRIFT
  2  no DRIFT, but at least one MISSING-EVIDENCE
  3  inputs unusable
"""
from __future__ import annotations

import argparse
import fnmatch
import json
import sys
from pathlib import Path
from typing import Any

DRIFT, MISSING, OUTSIDE, OK = "DRIFT", "MISSING-EVIDENCE", "OUTSIDE-CONTRACT", "CONFORMANT"

# CAP-HFL-001 lifecycle classes and the location each determines.
CLASS_LOCATIONS = {
    "config": "repo data/<node>/config/",
    "data": "repo data/<node>/",
    "state": "host ~/aof/state/",
    "telemetry": "host ~/aof/state/",
    "cache": "host ~/aof/cache/",
    "logs": "host ~/Library/Logs/aof-*.log",
    "runtime": "host $TMPDIR or ~/aof/run/",
}
TIERS = {"record", "exhaust"}


class InputError(Exception):
    pass


def load_mapping(path: Path) -> dict[str, Any]:
    """Accept JSON or YAML. A manifest we cannot parse is an input error, never a pass."""
    try:
        text = path.read_text()
    except (OSError, UnicodeDecodeError) as exc:
        raise InputError(f"cannot read {path}: {exc}") from exc
    try:
        data = json.loads(text)
    except json.JSONDecodeError:
        pass
    else:
        if not isinstance(data, dict):
            raise InputError(f"{path} must parse to a mapping")
        return data
    try:
        import yaml  # optional
    except ImportError as exc:
        raise InputError(
            f"{path} is not JSON and PyYAML is unavailable to parse it as YAML") from exc
    try:
        data = yaml.safe_load(text)
    except Exception as exc:  # noqa: BLE001 - yaml raises a family of errors
        raise InputError(f"{path} is not parseable as YAML: {exc}") from exc
    if not isinstance(data, dict):
        raise InputError(f"{path} must parse to a mapping")
    return data


def manifest_rules(manifest: dict[str, Any]) -> list[dict[str, Any]]:
    paths = manifest.get("paths")
    if not isinstance(paths, list) or not paths:
        raise InputError("manifest has no 'paths' list (CAP-HFL-002)")
    rules = []
    for i, rule in enumerate(paths):
        if not isinstance(rule, dict) or not isinstance(rule.get("pattern"), str) or not rule["pattern"]:
            raise InputError(f"manifest paths[{i}] has no pattern")
        rules.append(rule)
    return rules


def check_manifest(rules: list[dict[str, Any]], root: Path) -> list[dict[str, Any]]:
    """CAP-HFL-002/004/006 over the observed tree."""
    findings: list[dict[str, Any]] = []
    governed_globs = [r["pattern"].lstrip("./") for r in rules]

    for rule in rules:
        pattern, cls, tier = rule["pattern"], rule.get("class"), rule.get("tier")
        subject = f"manifest:{pattern}"
        if cls not in CLASS_LOCATIONS:
            findings.append({"subject": subject, "outcome": DRIFT,
                             "why": f"declared class {cls!r} is not a CAP-HFL-001 lifecycle class"})
            continue
        if tier is not None and tier not in TIERS:
            findings.append({"subject": subject, "outcome": DRIFT,
                             "why": f"declared tier {tier!r} is not record|exhaust (CAP-HFL-005)"})
            continue
        # host-anchored patterns cannot be graded from a repo root
        if pattern.startswith("~") or pattern.startswith("$"):
            findings.append({"subject": subject, "outcome": MISSING,
                             "why": "host-anchored path; not observable from the supplied root"})
            continue
        matches = [p for p in root.rglob("*") if p.is_file()
                   and fnmatch.fnmatch(str(p.relative_to(root)), pattern.lstrip("./"))]
        if not matches:
            findings.append({"subject": subject, "outcome": MISSING,
                             "why": "manifest declares this path; no artifact observed under root"})
            continue
        misplaced = []
        for path in matches:
            parts = path.relative_to(root).parts
            under_data = len(parts) >= 3 and parts[0] == "data"
            # Section 4 admits durable state/telemetry summaries as record outputs.
            record_summary = cls in {"state", "telemetry"} and tier == "record"
            correct = under_data and (cls == "data" or record_summary or (
                cls == "config" and len(parts) >= 4 and parts[2] == "config"))
            if not correct or tier == "exhaust":
                misplaced.append(str(path.relative_to(root)))
        if misplaced:
            findings.append({"subject": subject, "outcome": DRIFT,
                             "why": "observed artifact is outside its lifecycle-class/tier "
                                    "location (CAP-HFL-001/004/005)",
                             "expected": CLASS_LOCATIONS[cls], "misplaced": misplaced})
            continue
        findings.append({"subject": subject, "outcome": OK,
                         "why": None, "observed": len(matches)})

    # CAP-HFL-004 / CAP-HFL-006: observed artifacts NOT covered by any rule.
    for p in sorted(root.rglob("*")):
        if not p.is_file():
            continue
        rel = str(p.relative_to(root))
        if any(fnmatch.fnmatch(rel, g) for g in governed_globs):
            continue
        findings.append({
            "subject": f"observed:{rel}", "outcome": OUTSIDE,
            "why": "no governing layout rule covers this region; CAP-HFL-006 forbids grading its "
                   "disorder as a violation (absence != drift)",
        })
    return findings


def check_roster(roster: dict[str, Any] | None, repo_markers: list[str]) -> list[dict[str, Any]]:
    """CAP-HFL-007: a daemon executing from an agent's repo checkout is non-conformant."""
    if roster is None:
        return [{"subject": "roster", "outcome": MISSING,
                 "why": "no roster supplied; CAP-HFL-007 cannot be evaluated. Absence of a roster "
                        "is not evidence of conformance"}]
    daemons = roster.get("daemons")
    if not isinstance(daemons, list):
        return [{"subject": "roster", "outcome": MISSING, "why": "roster has no 'daemons' list"}]
    out = []
    for d in daemons:
        if not isinstance(d, dict):
            out.append({"subject": "daemon", "outcome": MISSING,
                        "why": "roster entry is not a mapping"})
            continue
        name, exec_path = d.get("name", "<unnamed>"), d.get("exec_path")
        if not isinstance(exec_path, str) or not exec_path:
            out.append({"subject": f"daemon:{name}", "outcome": MISSING,
                        "why": "roster entry declares no exec_path"})
            continue
        from_repo = any(m in exec_path for m in repo_markers)
        out.append({
            "subject": f"daemon:{name}", "outcome": DRIFT if from_repo else OK,
            "exec_path": exec_path,
            "why": ("runs from an agent repo checkout (run-from-repo); CAP-HFL-007 requires a "
                    "deployed copy owned by the operator agent") if from_repo else None,
        })
    return out


def check_envelope(rules: list[dict[str, Any]], root: Path) -> list[dict[str, Any]]:
    """CAP-HFL-005: tier boundary, including a manifest-declared per-row record-predicate."""
    out = []
    for rule in rules:
        pred = rule.get("record_predicate")
        if not pred:
            continue
        subject = f"envelope:{rule['pattern']}"
        field = pred.get("field") if isinstance(pred, dict) else None
        if not field:
            out.append({"subject": subject, "outcome": DRIFT,
                        "why": "record_predicate declares no field (CAP-HFL-005 per-row form)"})
            continue
        matches = [p for p in root.rglob("*") if p.is_file()
                   and fnmatch.fnmatch(str(p.relative_to(root)), rule["pattern"].lstrip("./"))]
        if not matches:
            out.append({"subject": subject, "outcome": MISSING,
                        "why": "stream declares a per-row predicate; no artifact observed"})
            continue
        unreadable, rows, bad = [], 0, 0
        for m in matches:
            try:
                if not m.stat().st_mode & 0o400:
                    raise PermissionError("stream is not readable")
                for line in m.read_text().splitlines():
                    if not line.strip():
                        continue
                    rows += 1
                    try:
                        row = json.loads(line)
                        if not isinstance(row, dict) or field not in row:
                            bad += 1
                    except json.JSONDecodeError:
                        bad += 1
            except (OSError, UnicodeDecodeError):
                unreadable.append(str(m))
        if unreadable:
            out.append({"subject": subject, "outcome": MISSING,
                        "why": f"envelope not readable: {unreadable[:3]}"})
        elif not rows:
            out.append({"subject": subject, "outcome": MISSING,
                        "why": "no stream rows observed; row classification is unverified"})
        elif bad:
            out.append({"subject": subject, "outcome": DRIFT,
                        "why": f"{bad} of {rows} rows lack the declared record-predicate field "
                               f"{field!r}, so their tier is undecidable"})
        else:
            out.append({"subject": subject, "outcome": OK, "why": None, "rows": rows})
    return out


def assess(manifest_path: Path, root: Path, roster_path: Path | None,
           repo_markers: list[str]) -> dict[str, Any]:
    manifest = load_mapping(manifest_path)
    rules = manifest_rules(manifest)
    roster = load_mapping(roster_path) if roster_path else None
    findings = (check_manifest(rules, root)
                + check_roster(roster, repo_markers)
                + check_envelope(rules, root))
    counts = {k: sum(1 for f in findings if f["outcome"] == k)
              for k in (OK, DRIFT, MISSING, OUTSIDE)}
    return {"findings": findings, "counts": counts,
            "overall": DRIFT if counts[DRIFT] else (MISSING if counts[MISSING] else OK)}


def render(res: dict[str, Any]) -> str:
    out = [f"host layout conformance: {res['overall']}", ""]
    for f in res["findings"]:
        line = f"  {f['outcome']:<17} {f['subject']}"
        out.append(line)
        if f.get("why"):
            out.append(f"                    -- {f['why']}")
    c = res["counts"]
    out += ["", f"  conformant={c[OK]}  drift={c[DRIFT]}  missing-evidence={c[MISSING]}  "
                f"outside-contract={c[OUTSIDE]}",
            "  OUTSIDE-CONTRACT is not a failure: CAP-HFL-006 forbids grading an ungoverned region.",
            "  A fixture PASS is not deployed enforcement (node deployment is the operator's, "
            "verified at source)."]
    return "\n".join(out)


def exit_code(res: dict[str, Any]) -> int:
    if res["counts"][DRIFT]:
        return 1
    if res["counts"][MISSING]:
        return 2
    return 0


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Host-layout conformance (CAP-HFL-001..007).")
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--root", type=Path, default=Path("."))
    ap.add_argument("--roster", type=Path, default=None)
    ap.add_argument("--repo-marker", action="append", default=None,
                    help="substring identifying an agent repo checkout; repeatable")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    markers = args.repo_marker or ["/github/", "-aget/", "-AGET/"]
    try:
        res = assess(args.manifest, args.root, args.roster, markers)
    except InputError as exc:
        print(f"UNAVAILABLE: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(res, indent=1) if args.json else render(res))
    return exit_code(res)


if __name__ == "__main__":
    sys.exit(main())
