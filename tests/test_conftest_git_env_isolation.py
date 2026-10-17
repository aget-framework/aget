"""Falsifier for tests/conftest.py's repository-location isolation (gmelli/aget-aget#2965).

The second test runs the probe below in a child pytest whose environment points every git location
variable at a VICTIM repository, and asserts that the victim's config is unchanged, that the probe saw
none of the variables, and that the probe actually ran (a marker file it writes). Without the conftest,
the probe's `git config` writes into the victim. The check is made by execution in a separate process,
not by reading conftest.py (CAP-CI-010-03).
"""
import ast
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PROBE = "tests/test_conftest_git_env_isolation.py::test_probe_acts_only_on_its_own_scratch_repo"
LOCATION_VARS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                 "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                 "GIT_NAMESPACE", "GIT_PREFIX", "GIT_CONFIG")
MARKER_VAR = "AGET_GIT_ISOLATION_PROBE_MARKER"


def test_probe_acts_only_on_its_own_scratch_repo(tmp_path):
    """Run as a child by the test below (and harmlessly in the normal suite): git must act on tmp_path only.

    git runs BEFORE the variables are checked, as the defect's own test did: without the conftest, this
    `git config` lands in the victim, and the parent's comparison of the victim's config shows it.
    """
    marker = os.environ.get(MARKER_VAR)
    if marker:
        Path(marker).write_text("ran\n")
    scratch = tmp_path / "scratch"
    subprocess.run(["git", "init", "-q", str(scratch)], check=True)
    subprocess.run(["git", "-C", str(scratch), "config", "user.name", "probe-identity"], check=True)
    out = subprocess.run(["git", "-C", str(scratch), "rev-parse", "--absolute-git-dir"],
                         capture_output=True, text=True, check=True).stdout.strip()
    # Compare values one by one, never `in os.environ`: a failing membership assertion makes pytest print
    # the whole environment, tokens included, into the test log.
    leaked = [name for name in LOCATION_VARS if os.environ.get(name) is not None]
    assert not leaked, f"conftest must remove git location variables before any test runs (found {leaked})"
    assert Path(out).resolve() == (scratch / ".git").resolve()


def test_inherited_git_location_variables_cannot_reach_a_victim_repository(tmp_path):
    victim = tmp_path / "victim"
    subprocess.run(["git", "init", "-q", str(victim)], check=True)
    git_dir = victim / ".git"
    before = (git_dir / "config").read_bytes()
    marker = tmp_path / "probe-ran"
    env = {k: v for k, v in os.environ.items() if k != "PYTEST_ADDOPTS"}
    env.update(GIT_DIR=str(git_dir), GIT_WORK_TREE=str(victim), GIT_COMMON_DIR=str(git_dir),
               GIT_INDEX_FILE=str(git_dir / "index"), GIT_OBJECT_DIRECTORY=str(git_dir / "objects"),
               GIT_ALTERNATE_OBJECT_DIRECTORIES=str(git_dir / "objects"), GIT_NAMESPACE="victim",
               GIT_PREFIX="", GIT_CONFIG=str(git_dir / "config"))
    env[MARKER_VAR] = str(marker)
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", PROBE],
                       cwd=ROOT, env=env, capture_output=True, text=True)
    after = (git_dir / "config").read_bytes()
    assert after == before, "the child suite wrote into the victim repository's config:\n" + after.decode()
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert marker.exists(), "the child pytest exited 0 without running the probe:\n" + r.stdout[-2000:]


def test_conftest_covers_every_variable_the_migration_kit_names():
    """The kit's GIT_LOCATION_VARS is the framework's list of variables that relocate git; the suite must not lag it."""
    tree = ast.parse((ROOT / "scripts" / "migration_kit" / "copy_isolation.py").read_text())
    kit = next(ast.literal_eval(node.value) for node in ast.walk(tree)
               if isinstance(node, ast.Assign)
               and any(getattr(t, "id", None) == "GIT_LOCATION_VARS" for t in node.targets))
    conftest = ast.parse((ROOT / "tests" / "conftest.py").read_text())
    ours = next(ast.literal_eval(node.value) for node in ast.walk(conftest)
                if isinstance(node, ast.Assign)
                and any(getattr(t, "id", None) == "REPO_LOCATION_VARS" for t in node.targets))
    assert set(kit) <= set(ours), f"conftest lacks {sorted(set(kit) - set(ours))}"
    assert set(LOCATION_VARS) == set(ours), "this test's list and conftest's list must name the same variables"


DISCOVERY_PROBE = "tests/test_conftest_git_env_isolation.py::test_probe_git_does_not_climb_out_of_the_temp_root"


def test_probe_git_does_not_climb_out_of_the_temp_root():
    """Run as a child by the test below (harmless in the normal suite): git run in a scratch folder that is NOT a
    repository must not find an enclosing repository above the temp root and commit into it."""
    import tempfile
    marker = os.environ.get(MARKER_VAR)
    if marker:
        Path(marker).write_text("ran\n")
    scratch = Path(tempfile.mkdtemp())
    (scratch / "probe.txt").write_text("probe\n")
    subprocess.run(["git", "-C", str(scratch), "add", "-A"], capture_output=True)
    subprocess.run(["git", "-C", str(scratch), "-c", "user.name=probe", "-c", "user.email=probe@example.invalid",
                    "commit", "-q", "-m", "probe commit"], capture_output=True)


def test_git_in_a_non_repository_scratch_folder_cannot_reach_an_enclosing_repository(tmp_path):
    """With TMPDIR inside a working tree (as a harness that keeps its temp folder in the checkout sets it), git's
    upward repository search must stop at the temp root (GIT_CEILING_DIRECTORIES, set by conftest)."""
    outer = tmp_path / "outer"
    subprocess.run(["git", "init", "-q", str(outer)], check=True)
    (outer / "seed.txt").write_text("seed\n")
    subprocess.run(["git", "-C", str(outer), "add", "seed.txt"], check=True)
    subprocess.run(["git", "-C", str(outer), "-c", "user.name=seed", "-c", "user.email=seed@example.invalid",
                    "commit", "-q", "-m", "seed"], check=True)
    inner_tmp = outer / "tmp"
    inner_tmp.mkdir()
    marker = tmp_path / "discovery-probe-ran"
    env = {k: v for k, v in os.environ.items() if k not in ("PYTEST_ADDOPTS", "GIT_CEILING_DIRECTORIES")}
    env.update(TMPDIR=str(inner_tmp))
    env[MARKER_VAR] = str(marker)
    r = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", "--basetemp",
                        str(inner_tmp / "basetemp"), DISCOVERY_PROBE], cwd=ROOT, env=env, capture_output=True, text=True)
    count = subprocess.run(["git", "-C", str(outer), "rev-list", "--all", "--count"],
                           capture_output=True, text=True, check=True).stdout.strip()
    assert count == "1", f"a scratch-folder commit landed in the enclosing repository ({count} commits)"
    assert r.returncode == 0, r.stdout[-2000:] + r.stderr[-2000:]
    assert marker.exists(), "the child pytest exited 0 without running the probe:\n" + r.stdout[-2000:]
