"""Test helper (C2a7, B185 finding 1): a kit report written as the kit's pytest plugin writes it, for tests that
hand-write a run's output text. Native runs of the plugin itself are in test_migration_kit_result_source.py."""
import json
import sys
import uuid
from pathlib import Path

import pytest

requires_monitoring = pytest.mark.skipif(
    sys.version_info < (3, 12),
    reason='requires sys.monitoring (Python 3.12+); below 3.12 the kit returns inconclusive by design (weekly-train:R15)',
)

MARK = "aget-kit-report: pytest "
# C2c (labelled): the selection witness these hand-written runs carry, and their baselines record (a baseline
# with no witness is refused: no witness, no policy)
SELECTION = {"roots": ["tests"], "ignored": [], "python_files": ["test_*.py", "*_test.py"], "python_classes": ["Test"], "python_functions": ["test"], "testpaths": [], "blocked": [], "plugins": [], "producers": ["fixture"], "autoload": ["on"]}   # C2c (labelled): the whole witness (pre-read M1)


def reported(path, runs):
    """Make the report at `path` and one invocation per run; `runs` is a list of (text, failing) with `failing` a list
    of node ids (a failed call) or (nodeid, phase) pairs. Returns (path, token, [each text with its report line])."""
    path = Path(path)
    token = uuid.uuid4().hex
    rows, texts = [], []
    for text, failing in runs:
        inv = uuid.uuid4().hex
        events = [(f, "call") if isinstance(f, str) else tuple(f) for f in failing]
        rows.append({"rec": "start", "token": token, "inv": inv, "pid": 1, "args": [], "dir": ".", "lf": False})
        # C2a8 (changed, labelled): each failing test also has its setup report, and the finish record counts the
        # collected and reported tests, as the plugin writes them
        tests = sorted({n for n, w in events if w != "collect"})
        setups = [(n, "setup", "failed" if (n, "setup") in events else "passed") for n in tests]
        evs = [x for x in setups] + [(n, w, "failed") for n, w in events if w != "setup"]
        rows += [{"rec": "event", "token": token, "inv": inv, "nodeid": n, "when": w, "outcome": o} for n, w, o in evs]
        rows.append({"rec": "finish", "token": token, "inv": inv, "exit": 1 if events else 0, "events": len(evs),
                     "collected": len(tests), "ran": len(tests), "deselected": [],
                     "narrowed": [], "dropped": 0, "suppressed": [], "selection": dict(SELECTION), "census": []})          # C2a10 (labelled): the two new finish fields; C2a12 (labelled): census
        texts.append(f"{MARK}{inv}\n{text}")
    path.write_text("".join(json.dumps(r) + "\n" for r in rows))
    return path, token, texts
