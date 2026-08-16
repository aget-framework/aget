"""Release-repository census regression tests.

Satisfies: R-SYNC-002, V-REL-REPO-CENSUS
"""

import importlib.util
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


def _load_module():
    spec = importlib.util.spec_from_file_location(
        "validate_changelogs", ROOT / "scripts" / "validate_changelogs.py"
    )
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


def test_changelog_validator_uses_complete_release_repo_set():
    """The changelog gate covers core plus all 13 public templates.

    Satisfies: R-SYNC-002, V-REL-REPO-CENSUS
    """
    repos = _load_module().REPOS
    assert len(repos) == 14
    assert len(set(repos)) == 14
    assert "aget" in repos
    assert "template-document-processor-AGET" in repos
