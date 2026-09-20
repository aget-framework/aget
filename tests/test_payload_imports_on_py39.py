"""Every delivered script must IMPORT under the oldest interpreter a fleet host runs.

Found 2026-09-19 by the AOF1 supervisor on node-1 (macOS system Python 3.9.6): four of the
90 scripts shipped at v3.34.0 fail to import (one via a `verification/` sibling; the producer's
probe masked it behind the cross-directory import and node-1 named it) because a `X | None` annotation is evaluated at
definition time (PEP 604 needs 3.10 unless `from __future__ import annotations` is present).
Three of the four already failed at v3.33.1; two since v3.22.0. Every laptop seat runs a Homebrew interpreter, so no
internal rehearsal could surface it -- the class L1630 §3 reserves for the external lane.

This test runs each script under /usr/bin/python3 when that interpreter is < 3.10, and SKIPS
(loudly) otherwise: a skip here means the host cannot measure the class, not that it passed.
"""
import subprocess, sys
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parent.parent
SYS_PY = Path("/usr/bin/python3")
PROBE = r'''
import importlib.util, sys, io, contextlib, glob, os
os.chdir(sys.argv[1]); sys.path.insert(0, os.getcwd())
bad = []
for f in sorted(glob.glob("*.py")):
    sys.argv = [f]
    spec = importlib.util.spec_from_file_location(f[:-3], f); m = importlib.util.module_from_spec(spec)
    try:
        with contextlib.redirect_stdout(io.StringIO()), contextlib.redirect_stderr(io.StringIO()):
            spec.loader.exec_module(m)
    except SystemExit:
        pass
    except TypeError as e:
        if "unsupported operand type(s) for |" in str(e): bad.append(f)
    except Exception:
        pass  # sibling-import / probe artifacts are not this test's subject
print("\n".join(bad))
'''


def _sys_py_version():
    if not SYS_PY.exists():
        return None
    out = subprocess.run([str(SYS_PY), "-c", "import sys;print(sys.version_info[:2])"], capture_output=True, text=True)
    return eval(out.stdout.strip()) if out.returncode == 0 else None


def test_every_delivered_script_imports_on_the_oldest_fleet_interpreter():
    v = _sys_py_version()
    if v is None or v >= (3, 10):
        pytest.skip(f"UNAVAILABLE: no <3.10 interpreter at {SYS_PY} (found {v}); the PEP-604 class cannot be measured on this host")
    bad = []
    for d in ("scripts", "tests"):  # tests/ added 2026-09-20: a test module that cannot be collected on 3.9 is the same class
        out = subprocess.run([str(SYS_PY), "-c", PROBE, str(REPO / d)], capture_output=True, text=True, timeout=600)
        assert out.returncode == 0, out.stderr[-800:]
        bad += [f"{d}/{l}" for l in out.stdout.splitlines() if l.strip()]
    assert not bad, f"fail to import on {v[0]}.{v[1]} (add `from __future__ import annotations`): {bad}"
