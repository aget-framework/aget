"""The kit ships in the public framework and runs at other people's supervisors (found 2026-09-30, before canonical
placement): receiver prompts named one laptop's supervisor, and comments and fixtures named private fleet members.
The supervisor's name now comes from AGET_MIGRATION_SUPERVISOR, else its own .aget/version.json, else a generic phrase.
The search test here looks for two shapes only, a member name with the private prefix and the aget suffix and a
/Users/ or /home/ path, in the kit's top-level .py, .md and .json files and the test files beside this one. It does
also checks private goal and portfolio identifiers. Readiness defaults to private capture unless a portfolio
explicitly declares public privacy; no producer-specific identifier selects that mode."""
import json
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
KIT = ROOT / "scripts" / "migration_kit"
# Generic shapes only: this file ships too, so it must not itself name an account. The framework's own public-surface
# audit covers repository owners.
PRIVATE = re.compile(r"private-[a-z0-9]+(?:-[a-z0-9]+)*-(?:aget|AGET)|/Users/[^/\s]+/|/home/[^/\s]+/|GOAL-[A-Z]{3}-[0-9]{3}|GM-[A-Z]{3}\b")


def test_no_private_names_or_paths_in_the_kit():
    files = [*KIT.glob("*.py"), *KIT.glob("*.md"), *KIT.glob("*.json"), *Path(__file__).parent.glob("*.py")]
    hits = [f"{f.name}:{i}" for f in files
            for i, line in enumerate(f.read_text().splitlines(), 1)
            if PRIVATE.search(line) and not line.startswith("PRIVATE = re.compile(")]
    assert not hits, hits


def _supervisor(root, env=None):
    code = "import release_target as R; print(R.SUPERVISOR)"
    e = {k: v for k, v in os.environ.items() if k != "AGET_MIGRATION_SUPERVISOR"}
    e.update(env or {})
    return subprocess.run([sys.executable, "-c", code], cwd=KIT, env=e, capture_output=True, text=True,
                          timeout=60).stdout.strip()


def test_the_supervisor_name_is_the_repositorys_own_or_set():
    vj = ROOT / ".aget" / "version.json"
    own = json.loads(vj.read_text()).get("agent_name") if vj.is_file() else None
    assert _supervisor(ROOT) == (own or "the supervisor")
    assert _supervisor(ROOT, {"AGET_MIGRATION_SUPERVISOR": "overseer-aget"}) == "overseer-aget"


def test_receiver_prompts_name_the_supervisor_from_the_parameter():
    src = (KIT / "prepare_launch.py").read_text()
    assert src.count("The supervisor, {R.SUPERVISOR}, launched") == 4
