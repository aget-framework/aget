#!/usr/bin/env python3
"""Render and verify the single governed v3.29 release-decision view."""
from __future__ import annotations

import argparse
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXPECTED_IDS = ["H-29-003", "H-29-012", "H-29-013", "H-29-016", "H-29-018", "H-29-022"]
RULING_RE = re.compile(r"^#{2,4}\s+.*?(?:(?P<qual>[a-z0-9][a-z0-9-]*):)?(?P<id>R\d+)", re.M | re.I)
RULING_ROW_RE = re.compile(r"^\|\s*\**`?(?:(?P<qual>[a-z0-9][a-z0-9-]*):)?(?P<id>R\d+)`?\**\s*\|", re.M | re.I)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8") if path.is_file() else ""


def _requirements_reach(root: Path) -> dict:
    records = []
    unqualified = 0
    by_id = {}
    for path in sorted((root / "planning").glob("RULINGS_*.md")):
        body = _read(path)
        seen = set()
        for regex in (RULING_RE, RULING_ROW_RE):
            for match in regex.finditer(body):
                rid = match.group("id").upper()
                if rid in seen:
                    continue
                seen.add(rid)
                qualifier = (match.group("qual") or "").lower()
                records.append((path.name, qualifier, rid))
                if not qualifier:
                    unqualified += 1
                by_id.setdefault(rid, set()).add(path.name)
    ledger_entries = re.findall(r"^\s*-?\s*id:\s*(REQ-[A-Z0-9-]+)",
                                _read(root / "governance" / "REQUIREMENTS_LEDGER.md"), re.M)
    target = sorted({f"{qual}:{rid}" for _path, qual, rid in records if qual == "v329-release"})
    return {"ruling_files": len({p for p, _q, _r in records}), "rulings": len(records),
            "ledger_entries": len(ledger_entries),
            "collision_ids": len([rid for rid, paths in by_id.items() if len(paths) > 1]),
            "unqualified_headings": unqualified, "target_rulings": target}


def build_view(root: Path, version: str) -> dict:
    sources = {
        "scope": root / "planning" / f"VERSION_SCOPE_v{version}.md",
        "rulings": root / "planning" / "RULINGS_v329_release_2026-08-01.md",
        "plan": root / "planning" / f"PROJECT_PLAN_v{version}_release_v1.0.md",
        "goal": root / "governance" / "GOALS.md",
        "ledger": root / "governance" / "REQUIREMENTS_LEDGER.md",
    }
    text = {key: _read(path) for key, path in sources.items()}
    selected = sorted(set(re.findall(r"H-29-(?:003|012|013|016|018|022)", text["scope"])))
    plan_selected = sorted(set(re.findall(r"H-29-(?:003|012|013|016|018|022)", text["plan"])))
    contradictions = []
    omissions = []
    if selected != EXPECTED_IDS:
        omissions.append("scope roster is not the exact six-family set")
    if plan_selected != EXPECTED_IDS:
        contradictions.append("plan and scope selected rosters differ")
    reach = _requirements_reach(root)
    required_facts = {
        "supported_clients": all(name in text["rulings"] for name in ("Claude Code", "Codex CLI")),
        "decision_threshold": all(token in text["rulings"] for token in
                                  ("generated-view count = 1", "contradictions = 0",
                                   "omissions = 0", "manual cross-artifact joins = 0")),
        "ordinary_use": all(token in text["rulings"] for token in
                            ("downstream", "Codex-native", "recovery")),
        "deadline": "2026-08-02T06:55:08-07:00" in text["rulings"],
        "goal_bound": "GOAL-V329-DELIVERED" in text["goal"],
        "promotion_home": reach["ledger_entries"] > 0,
        "target_rulings": reach["target_rulings"] == [
            "v329-release:R1", "v329-release:R2", "v329-release:R3"],
    }
    omissions.extend(f"missing fact: {key}" for key, present in required_facts.items() if not present)
    return {
        "schema": "aget.release-decision-view.v1",
        "version": version,
        "views": 1,
        "contradictions": len(contradictions),
        "omissions": len(omissions),
        "manual_joins": 0,
        "selected_outcomes": EXPECTED_IDS,
        "supported_clients": ["Claude Code", "Codex CLI"],
        "delivery_behavior": "downstream Codex-native discovery, invocation, and recovery",
        "literal_slash_compatibility": "excluded to v3.30",
        "deadline": "2026-08-02T06:55:08-07:00",
        "gate_boundary": "pre-push; Gate 3 requires new explicit GO",
        "source_set": {key: str(path.relative_to(root)) for key, path in sources.items()},
        "source_checks": required_facts,
        "requirements_reach": reach,
        "issues": contradictions + omissions,
        "state": "PASS" if not contradictions and not omissions else "FAIL",
    }


def render_markdown(view: dict) -> str:
    rows = "\n".join(f"| {key} | {value} |" for key, value in (
        ("Generated views", view["views"]), ("Contradictions", view["contradictions"]),
        ("Omissions", view["omissions"]), ("Manual joins", view["manual_joins"])))
    return (f"# v{view['version']} release decision view\n\n**State**: {view['state']}\n\n"
            f"**Locked outcomes**: {', '.join(view['selected_outcomes'])}\n\n"
            f"**Supported clients**: {', '.join(view['supported_clients'])}\n\n"
            f"**Delivery behavior**: {view['delivery_behavior']}\n\n"
            f"**Deadline**: `{view['deadline']}`\n\n"
            f"**Boundary**: {view['gate_boundary']}\n\n"
            "| Measure | Result |\n|---|---:|\n" + rows + "\n")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--version", required=True)
    parser.add_argument("--root", type=Path, default=ROOT)
    parser.add_argument("--output", type=Path)
    parser.add_argument("--markdown-output", type=Path)
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    view = build_view(args.root.resolve(), args.version)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(view, indent=2) + "\n")
    if args.markdown_output:
        args.markdown_output.parent.mkdir(parents=True, exist_ok=True)
        args.markdown_output.write_text(render_markdown(view))
    print(json.dumps(view, indent=2) if args.json else render_markdown(view))
    return 0 if (not args.verify or view["state"] == "PASS") else 1


if __name__ == "__main__":
    raise SystemExit(main())
