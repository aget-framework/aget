#!/usr/bin/env python3
"""H-29-012 supported-client outcome matrix (Claude Code + Codex CLI)."""
from __future__ import annotations

import argparse
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POC = ROOT / "poc" / "codex-hook-controls" / "codex_pretool_guard.py"
CLAUDE_POC = ROOT / "poc" / "claude-hook-controls" / "claude_pretool_guard.py"
CLAUDE_FIXTURE = ROOT / "poc" / "claude-hook-controls" / "settings.fixture.json"


def _load_poc(path: Path, name: str):
    spec = importlib.util.spec_from_file_location(name, path)
    module = importlib.util.module_from_spec(spec)
    assert spec and spec.loader
    spec.loader.exec_module(module)
    return module


def claude_result(root: Path = ROOT) -> dict:
    settings = root / ".claude" / "settings.json"
    evidence_kind = "live-settings"
    if not settings.is_file():
        settings = CLAUDE_FIXTURE
        evidence_kind = "sanitized-portable-fixture"
    payload = json.loads(settings.read_text()) if settings.is_file() else {}
    hooks = ((payload.get("hooks") or {}).get("PreToolUse") or [])
    blob = json.dumps(hooks)
    module = _load_poc(CLAUDE_POC, "claude_pretool_guard")
    blocked = module.decide({"path": ".claude/settings.json"})
    allowed = module.decide({"path": "docs/README.md"})
    affirmed = module.decide({"path": "AGENTS.md", "affirmed": True})
    dimensions = {
        "applicability": bool(hooks) and "guard" in blob.lower(),
        "trust_boundary": bool(payload.get("permissions")) or bool(hooks),
        "positive_block": blocked["decision"] == "block",
        "negative_control": allowed["decision"] == "allow" and affirmed["decision"] == "allow",
        "denied_no_side_effect": blocked == {
            "decision": "block", "reason": "individual-affirmation-required"
        },
    }
    return {"client": "Claude Code", "state": "PASS" if all(dimensions.values()) else "FAIL",
            "dimensions": dimensions,
            "evidence": str(settings.relative_to(ROOT if settings == CLAUDE_FIXTURE else root)),
            "evidence_kind": evidence_kind}


def codex_result() -> dict:
    module = _load_poc(POC, "codex_pretool_guard")
    blocked = module.decide({"trusted": True, "path": ".codex/config.toml"})
    allowed = module.decide({"trusted": True, "path": "docs/README.md"})
    affirmed = module.decide({"trusted": True, "path": "AGENTS.md", "affirmed": True})
    untrusted = module.decide({"trusted": False, "path": "AGENTS.md"})
    dimensions = {
        "applicability": POC.is_file(),
        "trust_boundary": untrusted["decision"] == "unavailable",
        "positive_block": blocked["decision"] == "block",
        "negative_control": allowed["decision"] == "allow" and affirmed["decision"] == "allow",
        "denied_no_side_effect": blocked == {"decision": "block", "reason": "individual-affirmation-required"},
    }
    return {"client": "Codex CLI", "state": "PASS" if all(dimensions.values()) else "FAIL",
            "dimensions": dimensions, "evidence": str(POC.relative_to(ROOT))}


def matrix(root: Path = ROOT) -> dict:
    clients = [claude_result(root), codex_result()]
    return {"supported_clients": [c["client"] for c in clients],
            "state": "PASS" if all(c["state"] == "PASS" for c in clients) else "FAIL",
            "clients": clients,
            "excluded_clients": "N/A — outside principal-ruled supported-client set"}


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = matrix()
    print(json.dumps(result, indent=2) if args.json else f"cross-client-hook-controls: {result['state']}")
    return 0 if result["state"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
