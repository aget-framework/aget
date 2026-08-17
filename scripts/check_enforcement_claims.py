#!/usr/bin/env python3
"""Check whether specification enforcement declarations are truthful and governed.

The checker separates three questions that older Enforcement tables collapsed:

1. Does the declaration resolve to the exact instrument it names?
2. Does a non-test executable/configuration artifact invoke that instrument?
3. If the declaration honestly reports a gap, does that gap carry an unexpired
   build-or-remove date or an explicit principal election?

Scope is one repository per invocation. The result never supports a fleet claim.

Usage:
  python3 scripts/check_enforcement_claims.py --root ../aget
  python3 scripts/check_enforcement_claims.py --root ../aget --json
  python3 scripts/check_enforcement_claims.py --root . --self-check

Exit codes:
  0  PASS, or UNAVAILABLE when no named enforcement declarations were found
  1  FAIL: at least one declaration is false, ambiguous, uncalled, expired, or
     an ungoverned disclosed gap
"""

from __future__ import annotations

import argparse
import ast
import datetime as dt
import json
import pathlib
import re
import subprocess
import sys
from dataclasses import asdict, dataclass


ACTIVE_CLAIM = re.compile(r"\b(implemented|active|enforced|wired)\b", re.IGNORECASE)
DISCLOSED_GAP = re.compile(
    r"\b(planned|none|not implemented|unimplemented|absent|uncalled|"
    r"never invoked|not built|0 callers?)\b",
    re.IGNORECASE,
)
MANUAL_CLAIM = re.compile(r"\b(manual|human review|n/?a)\b", re.IGNORECASE)
PRINCIPAL_ELECTION = re.compile(
    r"\bprincipal(?:_election|[- ]election|[- ]approved|[- ]override)\b",
    re.IGNORECASE,
)
DATE_TOKEN = re.compile(r"\b(20\d{2}-\d{2}-\d{2})\b")

# Preserve the declared path. The former extractor returned only the basename,
# so `validation/x.py` incorrectly resolved to `verification/x.py`.
INSTRUMENT = re.compile(
    r"(?<![\w.-])(?P<path>(?:[A-Za-z0-9_.-]+/)*[A-Za-z_][\w-]*\.py)\b"
)

ENFORCEMENT_HEADING = re.compile(
    r"^#{1,4}\s*.*\b(enforcement|validator|implementation status|conformance|"
    r"validation status|enforced by)\b",
    re.IGNORECASE,
)
YAML_ENFORCEMENT_FIELD = re.compile(r"^\s*enforcement\s*:\s*(.+)$", re.IGNORECASE)
MARKDOWN_ENFORCEMENT_FIELD = re.compile(
    r"^\s*\*\*enforcement\*\*\s*:\s*(.+)$", re.IGNORECASE
)
WIRED_DECLARATION = re.compile(r"\bwired\s+into\b", re.IGNORECASE)
PUBLICATION_DISCLOSURE = re.compile(
    r"^\s*(?:[-*>]\s*)*(?:\*\*)?not implemented at publication\b",
    re.IGNORECASE,
)

EXEC_SUFFIXES = (".py", ".yml", ".yaml", ".sh", ".toml")
EXEC_FILENAMES = {"Makefile", "makefile", "Justfile", "justfile"}

FAILING_CLASSIFICATIONS = {
    "OVERCLAIM_ABSENT",
    "OVERCLAIM_AMBIGUOUS",
    "OVERCLAIM_UNCALLED",
    "OVERCLAIM_TEST_ONLY",
    "DISCLOSED_GAP_UNGOVERNED",
    "EXPIRED_GAP",
    "STALE_UNDERCLAIM",
}


@dataclass(frozen=True)
class Claim:
    spec: str
    line_number: int
    source_kind: str
    declaration_state: str
    instrument: str
    line: str
    deadline: str | None = None
    principal_election: bool = False


def tracked_files(root: pathlib.Path) -> list[str]:
    """Return repository-tracked files, or a filesystem walk outside git."""
    try:
        out = subprocess.run(
            ["git", "-C", str(root), "ls-files"],
            capture_output=True,
            text=True,
            check=True,
        ).stdout
        return [p for p in out.splitlines() if p]
    except (subprocess.CalledProcessError, FileNotFoundError):
        return [
            str(p.relative_to(root))
            for p in root.rglob("*")
            if p.is_file() and ".git" not in p.parts
        ]


def _state(line: str, source_kind: str) -> str:
    # Negated/non-enforcement language wins over the embedded word "implemented".
    if DISCLOSED_GAP.search(line):
        return "disclosed_gap"
    if MANUAL_CLAIM.search(line):
        return "manual"
    if ACTIVE_CLAIM.search(line):
        return "active"
    # Naming an instrument in a field or table whose subject is Enforcement is
    # itself an assertion. Requiring a second magic status word made the canonical
    # `enforcement: validator.py` form invisible.
    if source_kind in {
        "section_table",
        "yaml_field",
        "markdown_field",
        "wired_declaration",
    }:
        return "active"
    return "unknown"


def extract_claims(text: str, spec: str) -> list[Claim]:
    """Extract typed named-instrument declarations with stable source identities."""
    lines = text.splitlines()
    candidates: dict[int, str] = {}
    in_section = False
    section_level = 0

    for index, line in enumerate(lines, start=1):
        heading = re.match(r"^(#{1,6})\s", line)
        if heading:
            level = len(heading.group(1))
            if ENFORCEMENT_HEADING.match(line):
                in_section, section_level = True, level
                continue
            if in_section and level <= section_level:
                in_section = False

        source_kind: str | None = None
        if MARKDOWN_ENFORCEMENT_FIELD.match(line):
            source_kind = "markdown_field"
        elif YAML_ENFORCEMENT_FIELD.match(line):
            source_kind = "yaml_field"
        elif WIRED_DECLARATION.search(line) and INSTRUMENT.search(line):
            source_kind = "wired_declaration"
        elif PUBLICATION_DISCLOSURE.search(line) and INSTRUMENT.search(line):
            source_kind = "disclosed_declaration"
        elif in_section and line.lstrip().startswith("|") and INSTRUMENT.search(line):
            source_kind = "section_table"

        if source_kind:
            candidates[index] = source_kind

    claims: list[Claim] = []
    for line_number, source_kind in sorted(candidates.items()):
        line = lines[line_number - 1]
        declaration_state = _state(line, source_kind)
        for match in INSTRUMENT.finditer(line):
            deadline_match = DATE_TOKEN.search(line)
            claims.append(
                Claim(
                    spec=spec,
                    line_number=line_number,
                    source_kind=source_kind,
                    declaration_state=declaration_state,
                    instrument=match.group("path").lstrip("./"),
                    line=line.strip()[:240],
                    deadline=deadline_match.group(1) if deadline_match else None,
                    principal_election=bool(PRINCIPAL_ELECTION.search(line)),
                )
            )
    return claims


def _module_forms(candidate: str) -> set[str]:
    without_suffix = candidate[:-3] if candidate.endswith(".py") else candidate
    dotted = without_suffix.replace("/", ".")
    stem = pathlib.PurePath(candidate).stem
    return {dotted, stem}


def _call_name(node: ast.AST) -> str:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _call_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else node.attr
    return ""


def _string_constants(node: ast.AST) -> list[str]:
    return [n.value for n in ast.walk(node) if isinstance(n, ast.Constant) and isinstance(n.value, str)]


def _python_invocation_keys(body: str) -> set[str]:
    """Return import/command identities from executable Python syntax."""
    try:
        tree = ast.parse(body)
    except SyntaxError:
        return set()

    keys: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                keys.update({alias.name, alias.name.rsplit(".", 1)[-1]})
        elif isinstance(node, ast.ImportFrom):
            module = node.module or ""
            if module:
                keys.update({module, module.rsplit(".", 1)[-1]})
            for alias in node.names:
                keys.add(alias.name)
                if module:
                    keys.add(f"{module}.{alias.name}")
        elif isinstance(node, ast.Call) and _call_name(node.func) in {
            "subprocess.run",
            "subprocess.call",
            "subprocess.check_call",
            "subprocess.check_output",
            "subprocess.Popen",
            "os.system",
            "runpy.run_path",
        }:
            for value in _string_constants(node):
                for match in INSTRUMENT.finditer(value):
                    path = match.group("path").lstrip("./")
                    keys.update({path, pathlib.PurePath(path).name})
    return keys


def _config_invocation_keys(body: str) -> set[str]:
    """Return script identities from run/shell command lines, excluding registries."""
    keys: set[str] = set()
    for raw in body.splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if not re.search(r"(^|\b)(run\s*:|python3?|bash|sh)\b", line, re.IGNORECASE):
            continue
        for match in INSTRUMENT.finditer(line):
            path = match.group("path").lstrip("./")
            keys.update({path, pathlib.PurePath(path).name})
    return keys


def build_invocation_index(root: pathlib.Path, files: list[str]) -> dict[str, set[str]]:
    """Parse every caller surface once and index the identities it invokes."""
    index: dict[str, set[str]] = {}
    for rel in files:
        pure = pathlib.PurePath(rel)
        if not (rel.endswith(EXEC_SUFFIXES) or pure.name in EXEC_FILENAMES):
            continue
        try:
            body = (root / rel).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        keys = _python_invocation_keys(body) if rel.endswith(".py") else _config_invocation_keys(body)
        for key in keys:
            index.setdefault(key, set()).add(rel)
    return index


def _is_test_path(path: str) -> bool:
    pure = pathlib.PurePath(path)
    return "tests" in pure.parts or pure.name.startswith("test_")


def resolve_instrument(
    declared: str,
    files: list[str],
    root: pathlib.Path,
    invocation_index: dict[str, set[str]] | None = None,
) -> dict:
    """Resolve declared identity exactly, then enumerate typed static callers."""
    declared = declared.lstrip("./")
    if "/" in declared:
        candidates = [declared] if declared in files else []
    else:
        candidates = sorted(f for f in files if pathlib.PurePath(f).name == declared)

    result = {
        "declared_path": declared,
        "candidates": candidates,
        "exists": len(candidates) == 1,
        "ambiguous": len(candidates) > 1,
        "callers": [],
        "operational_callers": [],
        "test_callers": [],
    }
    if len(candidates) != 1:
        return result

    candidate = candidates[0]
    invocation_index = invocation_index or build_invocation_index(root, files)
    forms = {
        candidate,
        pathlib.PurePath(candidate).name,
        *_module_forms(candidate),
    }
    callers = sorted({
        caller
        for form in forms
        for caller in invocation_index.get(form, set())
        if caller != candidate
    })

    result["callers"] = callers
    result["test_callers"] = [p for p in callers if _is_test_path(p)]
    result["operational_callers"] = [p for p in callers if not _is_test_path(p)]
    return result


def _classify(claim: Claim, resolution: dict, today: dt.date) -> tuple[str, str]:
    exists = resolution["exists"]
    operational = resolution["operational_callers"]
    tests = resolution["test_callers"]

    if claim.declaration_state == "disclosed_gap":
        if exists and operational:
            return "STALE_UNDERCLAIM", "declared gap has an operational caller"
        if claim.principal_election:
            return "DISCLOSED_GAP_ELECTED", "gap carries an explicit principal election"
        if claim.deadline:
            deadline = dt.date.fromisoformat(claim.deadline)
            if deadline < today:
                return "EXPIRED_GAP", f"build-or-remove deadline expired {claim.deadline}"
            return "DISCLOSED_GAP_MONITORED", f"unexpired build-or-remove deadline {claim.deadline}"
        return "DISCLOSED_GAP_UNGOVERNED", "disclosed gap has no deadline or principal election"

    if claim.declaration_state == "manual":
        return "MANUAL_DECLARATION", "manual enforcement declaration"
    if resolution["ambiguous"]:
        return "OVERCLAIM_AMBIGUOUS", "bare name resolves to multiple tracked paths"
    if not exists:
        return "OVERCLAIM_ABSENT", "declared path does not resolve"
    if operational:
        return "VERIFIED_REACHED", "exact instrument has an operational static caller"
    if tests:
        return "OVERCLAIM_TEST_ONLY", "instrument is reached only from tests"
    return "OVERCLAIM_UNCALLED", "instrument has no invocation caller"


def predicate_text() -> str:
    """Render the actual constants used by the implementation."""
    return (
        "PREDICATE (generated from implementation constants)\n"
        f"  claim headings : /{ENFORCEMENT_HEADING.pattern}/i\n"
        "  inline forms   : enforcement:; **Enforcement**:; Wired into; "
        "Not implemented at publication\n"
        f"  active words   : /{ACTIVE_CLAIM.pattern}/i\n"
        f"  gap words      : /{DISCLOSED_GAP.pattern}/i\n"
        "  identity       : exact declared path; a bare basename must resolve uniquely\n"
        "  reached        : >=1 non-test tracked Python import/subprocess call or run/shell command\n"
        "  governed gap   : explicit principal election or unexpired YYYY-MM-DD obligation\n"
        "  scope          : one repository working tree at --root; NOT a fleet claim"
    )


def scan(root: pathlib.Path, spec_glob: str, today: dt.date | None = None) -> dict:
    files = tracked_files(root)
    specs = sorted(p for p in files if re.search(spec_glob, p))
    invocation_index = build_invocation_index(root, files)
    evaluated: list[dict] = []
    resolution_cache: dict[str, dict] = {}
    today = today or dt.date.today()

    for rel in specs:
        try:
            text = (root / rel).read_text(encoding="utf-8", errors="ignore")
        except OSError:
            continue
        for claim in extract_claims(text, rel):
            if claim.instrument not in resolution_cache:
                resolution_cache[claim.instrument] = resolve_instrument(
                    claim.instrument, files, root, invocation_index
                )
            resolution = resolution_cache[claim.instrument]
            classification, reason = _classify(claim, resolution, today)
            evaluated.append(
                {
                    **asdict(claim),
                    **resolution,
                    "classification": classification,
                    "reason": reason,
                    "failing": classification in FAILING_CLASSIFICATIONS,
                }
            )

    findings = [row for row in evaluated if row["failing"]]
    summary: dict[str, int] = {}
    for row in evaluated:
        summary[row["classification"]] = summary.get(row["classification"], 0) + 1

    return {
        "root": str(root),
        "as_of": today.isoformat(),
        "specs_scanned": len(specs),
        "claims_checked": len(evaluated),
        "active_claims_checked": sum(r["declaration_state"] == "active" for r in evaluated),
        "summary": dict(sorted(summary.items())),
        "claims": evaluated,
        "findings": findings,
        "status": "FAIL" if findings else ("PASS" if evaluated else "UNAVAILABLE"),
        "predicate": predicate_text(),
    }


def self_check(root: pathlib.Path) -> dict:
    """Require a non-test caller; a unit-test import is not operational reachability."""
    declared = "scripts/check_enforcement_claims.py"
    if declared not in tracked_files(root):
        declared = pathlib.Path(__file__).name
    files = tracked_files(root)
    resolution = resolve_instrument(declared, files, root, build_invocation_index(root, files))
    passed = resolution["exists"] and bool(resolution["operational_callers"])
    return {
        "instrument": declared,
        **resolution,
        "status": "PASS" if passed else "FAIL",
        "note": "self-check requires a non-test tracked caller",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    parser.add_argument("--root", default=".", help="repository root to scan")
    parser.add_argument("--spec-glob", default=r"specs/.*\.md$", help="regex for spec paths")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--self-check", action="store_true")
    args = parser.parse_args()
    root = pathlib.Path(args.root).resolve()

    result = self_check(root) if args.self_check else scan(root, args.spec_glob)
    if args.json:
        print(json.dumps(result, indent=2))
    elif args.self_check:
        print(
            f"{result['status']}: {result['instrument']} exists={result['exists']} "
            f"operational_callers={len(result['operational_callers'])} "
            f"test_callers={len(result['test_callers'])}\n  {result['note']}"
        )
    else:
        print(result["predicate"])
        print(f"\nscope: {result['root']}  (ONE repository — not a fleet claim)")
        print(
            f"specs scanned: {result['specs_scanned']}  claims checked: {result['claims_checked']}  "
            f"status: {result['status']}  findings: {len(result['findings'])}"
        )
        for row in result["findings"]:
            print(
                f"\n  {row['spec']}:{row['line_number']}\n"
                f"    {row['classification']}: {row['instrument']} — {row['reason']}\n"
                f"    claim: {row['line']}"
            )
    return 1 if result["status"] == "FAIL" else 0


if __name__ == "__main__":
    sys.exit(main())
