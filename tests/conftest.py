"""Suite-wide isolation from git's repository-location variables (gmelli/aget-aget#2965).

git obeys these variables in every command, whatever folder the command runs in. A hook run from a
linked worktree hands the suite an absolute GIT_DIR, so a test that runs `git init` or `git config`
in its scratch folder writes into the repository that GIT_DIR names instead (measured on v3.36.0:
tests/test_release_cadence_gap.py added a test identity to that repository's config). GIT_CONFIG does
the same for `git config` alone: git writes to the file it names, as if `--file` had been given.

They are removed here, at import, before any test module is collected, so collection-time code is
covered too. A test that needs one sets it itself (monkeypatch or a child environment).

The list is the migration kit's GIT_LOCATION_VARS (scripts/migration_kit/copy_isolation.py) plus
GIT_PREFIX and GIT_CONFIG; tests/test_conftest_git_env_isolation.py fails if the kit's list gains a
name this one lacks.
"""
import os
import tempfile as _tempfile

REPO_LOCATION_VARS = ("GIT_DIR", "GIT_WORK_TREE", "GIT_COMMON_DIR", "GIT_INDEX_FILE",
                      "GIT_OBJECT_DIRECTORY", "GIT_ALTERNATE_OBJECT_DIRECTORIES",
                      "GIT_NAMESPACE", "GIT_PREFIX", "GIT_CONFIG")

for _var in REPO_LOCATION_VARS:
    os.environ.pop(_var, None)

# git also searches upward for a repository from a folder that is not one. When the temp folder sits inside a
# working tree (a harness that keeps TMPDIR in its checkout), a test running git in a non-repository scratch
# folder would commit into the enclosing repository. Stop that search at the temp root.
_tmp_root = _tempfile.gettempdir()
_ceilings = [_tmp_root, os.path.realpath(_tmp_root)] + [p for p in os.environ.get("GIT_CEILING_DIRECTORIES", "").split(os.pathsep) if p]
os.environ["GIT_CEILING_DIRECTORIES"] = os.pathsep.join(dict.fromkeys(_ceilings))
