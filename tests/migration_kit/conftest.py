"""Kit tests run against the v3.35 target the kit was built on, set here and nowhere in the tools (carriage row 24).

The values below are test fixtures, not kit defaults: release_target.py carries no default release.
"""
import os

import pytest


@pytest.fixture(autouse=True)
def isolated_scope_archive(tmp_path, monkeypatch):
    """Independent synthetic fleets must not share scope taint via pytest's parent directory."""
    monkeypatch.setenv("AGET_MIGRATION_TEST_MODE", "1")
    monkeypatch.setenv("AGET_MIGRATION_SCOPE_ARCHIVE", str(tmp_path / "scope_archive.jsonl"))

os.environ.setdefault("AGET_MIGRATION_FROM", "3.34.0")
os.environ.setdefault("AGET_MIGRATION_TO", "3.35.0")
os.environ.setdefault("AGET_MIGRATION_REGISTER_PIN", "711ddac949ed1e0aca011c47b56dad18e2daf175")
os.environ.setdefault("AGET_MIGRATION_PINNED_MEMBERS", "5")
os.environ.setdefault("AGET_MIGRATION_PILOTS", "pilot-one-aget,pilot-two-aget")
