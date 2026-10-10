"""release_target.py — the migration kit's one release parameter.

Carriage row 24 (2026-09-28): the v3.35 kit hardcoded its release in 8 of its tools (78 literal occurrences), so
every release needed a hand edit of each tool before a fleet could migrate. This module is the single place a
migration names its releases and its fleet pin. The kit carries NO default release: nine tools (apply_protected,
fleet_ledger, plan_protected, prepare_batch, prepare_launch, prepare_write_list, push_batch, rehearse_batch2,
wave_readiness) stop without a valid target and say how to set one, instead of silently migrating to a past release.
The other tools make no such check.

Resolution, first found wins per key:
  1. environment: AGET_MIGRATION_FROM, AGET_MIGRATION_TO, AGET_MIGRATION_REGISTER_PIN,
     AGET_MIGRATION_PINNED_MEMBERS, AGET_MIGRATION_PILOTS (comma-separated)
  2. <root>/.aget/migration_target.json: {"from": "3.35.0", "to": "3.36.0", "register_pin": "<commit>",
     "pinned_members": 12, "pilots": ["pilot-one-aget"]}

Import never exits (a process exit at import fails receivers' test contracts; carriage row 29). Unset values read
as UNSET; those nine tools call require() at the start of main() (fleet_ledger and wave_readiness also require the
fleet pin).
"""
from __future__ import annotations

import json
import os
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]          # <root>/scripts/migration_kit/release_target.py
CONFIG = ROOT / ".aget" / "migration_target.json"
UNSET = "UNSET"
_SEMVER = re.compile(r"^\d+\.\d+\.\d+$")


def _config() -> dict:
    try:
        return json.loads(CONFIG.read_text()) if CONFIG.is_file() else {}
    except (OSError, ValueError):
        return {}


def _get(env: str, key: str, cfg: dict):
    v = os.environ.get(env)
    return v if v not in (None, "") else cfg.get(key)


def _resolve() -> dict:
    cfg = _config()
    pilots = _get("AGET_MIGRATION_PILOTS", "pilots", cfg)
    if isinstance(pilots, str):
        pilots = [p.strip() for p in pilots.split(",") if p.strip()]
    members = _get("AGET_MIGRATION_PINNED_MEMBERS", "pinned_members", cfg)
    return {
        "from": _get("AGET_MIGRATION_FROM", "from", cfg) or UNSET,
        "to": _get("AGET_MIGRATION_TO", "to", cfg) or UNSET,
        "register_pin": _get("AGET_MIGRATION_REGISTER_PIN", "register_pin", cfg) or UNSET,
        "pinned_members": int(members) if members not in (None, "") else None,
        "pilots": set(pilots or []),
    }


_T = _resolve()
FROM: str = _T["from"]
TO: str = _T["to"]
FROM_TAG: str = f"v{FROM}"
TO_TAG: str = f"v{TO}"
SLUG: str = "v" + "".join(TO.split(".")[:2]) if TO != UNSET else "vUNSET"   # 3.36.0 -> v336 (data folder names)
REGISTER_PIN: str = _T["register_pin"]
PINNED_MEMBERS = _T["pinned_members"]
PILOTS: set = _T["pilots"]


def _own_name() -> str:
    """The supervisor running the kit: AGET_MIGRATION_SUPERVISOR, else its own .aget/version.json agent_name. Receiver
    prompts name it; the staged kit named one laptop's supervisor there (found 2026-09-30, before canonical placement)."""
    v = os.environ.get("AGET_MIGRATION_SUPERVISOR")
    if v:
        return v
    try:
        return json.loads((ROOT / ".aget" / "version.json").read_text()).get("agent_name") or "the supervisor"
    except (OSError, ValueError):
        return "the supervisor"


SUPERVISOR: str = _own_name()
# The release's producer, when it is also a fleet member (a local fleet only); never true for a remote fleet.
PRODUCER = os.environ.get("AGET_MIGRATION_PRODUCER") or _config().get("producer")

DEFAULT_FRAMEWORK_ROOT = "~/github/aget-framework"


def framework_root() -> Path:
    """The folder holding the framework clones: the core `aget/` and the templates.

    R-F7 (rehearsal 2026-09-30): the kit read this only from AGET_FRAMEWORK_ROOT. Shell state does not persist between
    a session's commands, so every kit command needed an `export ...;` prefix, and the prefix stopped the session's
    command rules from matching. Resolution, first found wins: AGET_FRAMEWORK_ROOT, else "framework_root" in
    .aget/migration_target.json (a relative value resolves against this repository's root), else the default. Every
    kit tool that needs this folder gets it from here; none reads the variable itself."""
    v = os.environ.get("AGET_FRAMEWORK_ROOT") or _config().get("framework_root") or DEFAULT_FRAMEWORK_ROOT
    p = Path(os.path.expanduser(str(v)))
    return p if p.is_absolute() else (ROOT / p).resolve()


def require(*, pin: bool = False) -> None:
    """Stop with a clear message unless the release target (and, if asked, the fleet pin) is set."""
    missing = [k for k, v in (("from", FROM), ("to", TO)) if v == UNSET or not _SEMVER.match(v)]
    if pin:
        if REGISTER_PIN == UNSET:
            missing.append("register_pin")
        if PINNED_MEMBERS is None:
            missing.append("pinned_members")
    if missing:
        raise SystemExit(
            "migration kit: release target incomplete (" + ", ".join(missing) + "). Set AGET_MIGRATION_FROM / "
            "AGET_MIGRATION_TO (and AGET_MIGRATION_REGISTER_PIN / AGET_MIGRATION_PINNED_MEMBERS for fleet tools), "
            f"or write {CONFIG}. The kit carries no default release.")
