#!/usr/bin/env python3
"""Receiver conformance: detection, manifest integrity, and the acceptance terminal.

WHY THIS EXISTS
---------------
A receiver that had adopted a release correctly, byte-for-byte, reported STATUS: INCOMPLETE
with four rows -- and **three were structurally unreachable**. No action at the receiver could
clear them, because the defect was in the release's own instruments:

    INCOMPLETE detection:CD-xxx-01   exit=0; skipped=1     <- test hardcoded ../aget
    INCOMPLETE detection:CD-xxx-02   exit=0; skipped=1     <- two registry expectations
    INCOMPLETE integrity: digest_fields=0                  <- spec verifies digests the
                                                              manifest does not carry
    INCOMPLETE acceptance_terminal: PENDING                <- CORRECT. Leave it alone.

An INCOMPLETE a receiver cannot clear is not a finding about the receiver.

THE THREE REPAIRS, AND THE ONE NON-REPAIR
------------------------------------------
1. **Detection** resolves canonical through `canonical_root.resolve()`, the way the conformance
   harness already does, instead of a hardcoded relative path; and a canonical that was
   DECLARED and does not resolve fails loudly rather than skipping.
2. **Integrity**: an ordered manifest that claims "verify every ordered manifest digest before
   execution" must actually carry digests. Entries with `path` and no
   `sha256`/`sha`/`digest`/`checksum` cannot support the claim the spec makes about them, and
   are reported as UNVERIFIABLE -- not as verified, and not as absent.
3. **Skips** are counted and named. A skipped detection row is UNVERIFIED, never a pass.

**The non-repair is load-bearing.** `acceptance_terminal: PENDING` is the principal's
signature line and is deliberately not the agent's to write. Repairing the other three rows
MUST NOT turn the aggregate green: exit 2 stays exit 2 while acceptance is PENDING. This
command therefore treats PENDING as blocking by construction, and a test pins it.

Read-only.

USAGE
  check_receiver_conformance.py --manifest handoffs/DELIVERED_FILES_vX.Y.Z.yaml --repo DIR
  check_receiver_conformance.py --manifest M --repo DIR --acceptance .aget/acceptance/vX.Y.Z/
  check_receiver_conformance.py --manifest M --repo DIR --json

EXIT CODES
  0  every row COMPLETE
  2  INCOMPLETE -- including whenever the acceptance terminal is PENDING
  3  inputs unusable
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

COMPLETE, INCOMPLETE, UNVERIFIABLE = "COMPLETE", "INCOMPLETE", "UNVERIFIABLE"
DIGEST_FIELDS = ("sha256", "sha", "digest", "checksum")


class InputError(Exception):
    pass


def load_manifest(path: Path) -> dict[str, Any]:
    try:
        text = path.read_text()
    except (OSError, UnicodeDecodeError) as exc:
        raise InputError(f"manifest unreadable: {exc}") from exc
    try:
        doc = json.loads(text)
    except json.JSONDecodeError:
        pass
    else:
        if not isinstance(doc, dict):
            raise InputError("manifest must parse to a mapping")
        return doc
    try:
        import yaml
    except ImportError as exc:
        raise InputError("manifest is not JSON and PyYAML is unavailable") from exc
    try:
        doc = yaml.safe_load(text)
    except Exception as exc:  # noqa: BLE001
        raise InputError(f"manifest is not parseable: {exc}") from exc
    if not isinstance(doc, dict):
        raise InputError("manifest must parse to a mapping")
    return doc


def manifest_entries(doc: dict[str, Any]) -> list[dict[str, Any]]:
    for key in ("files", "payload", "entries", "delivered"):
        v = doc.get(key)
        if isinstance(v, list):
            if not v or any(not isinstance(e, dict) for e in v):
                raise InputError("manifest entries must be a nonempty list of mappings")
            return v
    raise InputError("manifest carries no ordered file list "
                     "(looked for files/payload/entries/delivered)")


def check_integrity(entries: list[dict[str, Any]], repo: Path) -> dict[str, Any]:
    """Every ordered entry must carry a digest the receiver can verify."""
    carried, missing, mismatched, unreadable = [], [], [], []
    invalid = []
    for index, e in enumerate(entries):
        if not isinstance(e, dict):
            invalid.append(index)
            continue
        rel = e.get("path")
        if not isinstance(rel, str) or not rel.strip():
            invalid.append(index)
            continue
        field = next((f for f in DIGEST_FIELDS if str(e.get(f, "")).strip()), None)
        if field is None:
            missing.append(rel)
            continue
        carried.append(rel)
        target = repo / rel
        try:
            got = hashlib.sha256(target.read_bytes()).hexdigest()
        except (OSError, ValueError):
            unreadable.append(rel)
            continue
        if got.lower() != str(e[field]).strip().lower():
            mismatched.append(rel)
    if not entries or invalid:
        state, why = UNVERIFIABLE, "empty manifest or ordered entries without valid paths"
    elif mismatched:
        state, why = INCOMPLETE, f"{len(mismatched)} payload digest(s) do not match"
    elif missing:
        # The spec says "verify every ordered manifest digest". An entry with no digest field
        # cannot support that claim; it is UNVERIFIABLE, which is neither verified nor absent.
        state, why = UNVERIFIABLE, (
            f"{len(missing)} of {len(entries)} ordered entries carry no "
            f"{'/'.join(DIGEST_FIELDS)} field, so the integrity clause cannot be satisfied "
            f"by this manifest")
    elif unreadable:
        state, why = UNVERIFIABLE, f"{len(unreadable)} payload file(s) unreadable at the receiver"
    else:
        state, why = COMPLETE, None
    return {"state": state, "digest_fields": len(carried), "entries": len(entries),
            "invalid_entries": invalid,
            "missing_digest": missing[:10], "mismatched": mismatched[:10],
            "unreadable": unreadable[:10], "why": why}


def check_acceptance(acceptance_dir: Path | None) -> dict[str, Any]:
    """The principal's signature line. Never written here, never cleared here."""
    if acceptance_dir is None:
        return {"state": INCOMPLETE, "terminal": "UNREAD",
                "why": "no --acceptance supplied; the terminal is not assumed"}
    if not acceptance_dir.is_dir():
        return {"state": INCOMPLETE, "terminal": "ABSENT",
                "why": f"no acceptance record at {acceptance_dir}"}
    terminals, evidence, failures = set(), [], []
    declaration = re.compile(
        r"^\s*(?:\*\*)?(?:Acceptance(?:\s+terminal)?|Terminal)(?:\*\*)?\s*:\s*"
        r"(?:\*\*)?(PENDING|ACCEPTED|REJECTED)(?:\*\*)?\s*$", re.IGNORECASE)
    for f in sorted(acceptance_dir.rglob("*")):
        if not f.is_file():
            continue
        try:
            if not f.stat().st_mode & 0o400:
                raise PermissionError("acceptance file lacks owner-read permission")
            text = f.read_text()
        except (OSError, UnicodeDecodeError) as exc:
            failures.append(f"{f}: {exc}")
            continue
        for number, line in enumerate(text.splitlines(), 1):
            match = declaration.fullmatch(line)
            if match:
                terminals.add(match.group(1).upper())
                evidence.append({"path": str(f), "line": number, "declaration": line})
    terminal = next(iter(terminals)) if len(terminals) == 1 else (
        "CONFLICT" if terminals else "PENDING")
    return {
        "state": UNVERIFIABLE if failures else COMPLETE if terminal == "ACCEPTED" else INCOMPLETE,
        "terminal": terminal,
        "evidence": evidence, "read_failures": failures,
        "scope": "terminal declarations only; signer and release identity require caller verification",
        "why": "acceptance population was not fully read" if failures else
               None if terminal == "ACCEPTED" else
               f"acceptance terminal is {terminal}. This is the principal's signature line and "
               f"is deliberately not the agent's to write. Repairing every other row does NOT "
               f"clear it.",
    }


def assess(manifest_path: Path, repo: Path, acceptance: Path | None,
           detection: list[dict[str, Any]] | None) -> dict[str, Any]:
    doc = load_manifest(manifest_path)
    entries = manifest_entries(doc)
    rows: dict[str, Any] = {}

    for d in (detection or []):
        if not isinstance(d, dict) or not isinstance(d.get("name"), str) or not d["name"].strip():
            raise InputError("every detection row must name its check")
        name = d["name"]
        if f"detection:{name}" in rows:
            raise InputError(f"duplicate detection name: {name}")
        skipped = d.get("skipped", 0)
        exit_code_ = d.get("exit")
        if type(exit_code_) is not int or type(skipped) is not int or skipped < 0:
            raise InputError(f"detection {name} requires an integer exit and nonnegative skipped count")
        if skipped:
            rows[f"detection:{name}"] = {
                "state": INCOMPLETE, "skipped": skipped,
                "why": f"{skipped} mandated check(s) SKIPPED. A skip is UNVERIFIED, never a "
                       f"pass: {d.get('skip_reasons') or 'no reason recorded'}"}
        else:
            rows[f"detection:{name}"] = {
                "state": COMPLETE if exit_code_ == 0 else INCOMPLETE, "skipped": 0,
                "why": None if exit_code_ == 0 else f"detection exited {exit_code_}"}

    rows["integrity"] = check_integrity(entries, repo)
    rows["acceptance_terminal"] = check_acceptance(acceptance)

    incomplete = [k for k, v in rows.items() if v["state"] != COMPLETE]
    return {"rows": rows, "incomplete": incomplete,
            "overall": COMPLETE if not incomplete else INCOMPLETE}


def render(res: dict[str, Any]) -> str:
    out = [f"STATUS: {res['overall']}", ""]
    for k, v in res["rows"].items():
        out.append(f"  {v['state']:<13} {k}")
        if v.get("why"):
            out.append(f"                -- {v['why']}")
    out += ["", "  A skipped detection row is UNVERIFIED, not passed. An ordered entry with no "
                "digest is UNVERIFIABLE.",
            "  A PENDING acceptance terminal keeps this INCOMPLETE however many other rows are "
            "repaired."]
    return "\n".join(out)


def exit_code(res: dict[str, Any]) -> int:
    return 0 if res["overall"] == COMPLETE else 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Receiver conformance rows.")
    ap.add_argument("--manifest", type=Path, required=True)
    ap.add_argument("--repo", type=Path, default=Path("."))
    ap.add_argument("--acceptance", type=Path, default=None)
    ap.add_argument("--detection", type=Path, default=None,
                    help="JSON list of {name, exit, skipped, skip_reasons}")
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)
    try:
        det = json.loads(args.detection.read_text()) if args.detection else None
        if det is not None and not isinstance(det, list):
            raise InputError("--detection must contain a JSON list")
        res = assess(args.manifest, args.repo, args.acceptance, det)
    except (InputError, OSError, json.JSONDecodeError) as exc:
        print(f"UNAVAILABLE: {exc}", file=sys.stderr)
        return 3
    print(json.dumps(res, indent=1) if args.json else render(res))
    return exit_code(res)


if __name__ == "__main__":
    sys.exit(main())
