#!/usr/bin/env python3
"""Validate the skill-reliance manifest (.aget/skill_reliance_manifest.yaml).

Serves gmelli/aget-aget#1748 / C-24-02 — makes the {S}/{O}/{D} reliance contract
release-pinned AND checkable (the gap was that tiers were "unspecified and uncheckable").

Checks (each returns a finding; any ERROR => exit 1):
  C1  every declared skill (S/O/D) exists in .claude/skills/
  C2  no skill appears in more than one tier
  C3  the {S} core set equals the authoritative universal_skills in
      ../aget/specs/ARCHETYPE_SKILLS_INDEX.yaml (when reachable; else WARN)
  C4  manifest carries a release pin (meta.as_of_version)
  C5  coverage: skills on disk not declared in any tier are reported (WARN, not ERROR)

Usage:
  python3 scripts/check_skill_reliance_manifest.py            # human-readable
  python3 scripts/check_skill_reliance_manifest.py --json     # machine / wake-up
"""
from __future__ import annotations
import json
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
MANIFEST = REPO / ".aget" / "skill_reliance_manifest.yaml"
SKILLS_DIR = REPO / ".claude" / "skills"
# gh#1837 defect 2 (v3.26 C-26-06): the single parent-relative path only resolves
# from the canonical repo itself; on every deployed agent (~/github/<agent>) the
# C3 check silently degraded to WARN "archetype index unreachable" fleet-wide.
# Candidate list, first existing wins.
_ARCHETYPE_CANDIDATES = [
    REPO.parent / "aget" / "specs" / "ARCHETYPE_SKILLS_INDEX.yaml",
    REPO.parent / "aget-framework" / "aget" / "specs" / "ARCHETYPE_SKILLS_INDEX.yaml",
    Path.home() / "github" / "aget-framework" / "aget" / "specs" / "ARCHETYPE_SKILLS_INDEX.yaml",
]
ARCHETYPE_INDEX = next((p for p in _ARCHETYPE_CANDIDATES if p.exists()),
                       _ARCHETYPE_CANDIDATES[0])

TIER_KEYS = {"core_S": "S", "optional_O": "O", "domain_D": "D"}


def _load_yaml(path: Path):
    import yaml  # local import so the module imports even if pyyaml absent
    with path.open() as fh:
        return yaml.safe_load(fh)


def validate() -> dict:
    findings: list[dict] = []

    def add(level: str, check: str, msg: str):
        findings.append({"level": level, "check": check, "msg": msg})

    if not MANIFEST.exists():
        add("ERROR", "load", f"manifest not found: {MANIFEST}")
        return _result(findings)

    manifest = _load_yaml(MANIFEST) or {}
    tiers = {k: list(manifest.get(k) or []) for k in TIER_KEYS}
    declared = {s: TIER_KEYS[k] for k, lst in tiers.items() for s in lst}

    on_disk = {p.name for p in SKILLS_DIR.iterdir() if p.is_dir()} if SKILLS_DIR.exists() else set()

    # C1 — declared skills exist on disk
    for skill, tier in sorted(declared.items()):
        if skill not in on_disk:
            add("ERROR", "C1-exists", f"{{{tier}}} '{skill}' declared but absent from .claude/skills/")

    # C2 — no skill in multiple tiers
    seen: dict[str, str] = {}
    for k, lst in tiers.items():
        for s in lst:
            if s in seen and seen[s] != TIER_KEYS[k]:
                add("ERROR", "C2-unique", f"'{s}' declared in multiple tiers ({seen[s]} and {TIER_KEYS[k]})")
            seen[s] = TIER_KEYS[k]

    # C3 — {S} core equals authoritative universal_skills
    if ARCHETYPE_INDEX.exists():
        try:
            idx = _load_yaml(ARCHETYPE_INDEX) or {}
            universal = set((idx.get("universal_skills") or {}).get("list") or [])
            core = set(tiers["core_S"])
            if universal and core != universal:
                missing = universal - core
                extra = core - universal
                if missing:
                    add("ERROR", "C3-core", f"{{S}} core missing authoritative universal skills: {sorted(missing)}")
                if extra:
                    add("ERROR", "C3-core", f"{{S}} core has non-universal skills: {sorted(extra)}")
        except Exception as exc:  # pragma: no cover - defensive
            add("WARN", "C3-core", f"could not compare against archetype index: {exc}")
    else:
        add("WARN", "C3-core", "archetype index unreachable (cross-repo); {S} authority unverified")

    # C4 — release pin present
    as_of = ((manifest.get("meta") or {}).get("as_of_version"))
    if not as_of:
        add("ERROR", "C4-pin", "manifest missing meta.as_of_version (a manifest must be release-pinned)")

    # C5 — coverage (WARN)
    undeclared = sorted(on_disk - set(declared))
    if undeclared:
        add("WARN", "C5-coverage", f"{len(undeclared)} skill(s) on disk not declared in any tier: {undeclared}")

    return _result(findings, declared=len(declared), on_disk=len(on_disk))


def _result(findings, **extra) -> dict:
    errors = [f for f in findings if f["level"] == "ERROR"]
    return {
        "ok": not errors,
        "errors": len(errors),
        "warnings": len([f for f in findings if f["level"] == "WARN"]),
        "findings": findings,
        **extra,
    }


def main(argv: list[str]) -> int:
    res = validate()
    if "--json" in argv:
        print(json.dumps(res, indent=2))
    else:
        status = "PASS" if res["ok"] else "FAIL"
        print(f"Skill Reliance Manifest: {status} "
              f"({res.get('declared', 0)} declared / {res.get('on_disk', 0)} on disk; "
              f"{res['errors']} errors, {res['warnings']} warnings)")
        for f in res["findings"]:
            print(f"  [{f['level']}] {f['check']}: {f['msg']}")
    return 0 if res["ok"] else 1


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
