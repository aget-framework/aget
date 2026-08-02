from pathlib import Path

from scripts.render_release_decision_view import EXPECTED_IDS, build_view, render_markdown


def _fixture(root: Path, *, clients=True):
    (root / "planning").mkdir()
    (root / "governance").mkdir()
    roster = " ".join(EXPECTED_IDS)
    (root / "planning" / "VERSION_SCOPE_v3.29.0.md").write_text(roster)
    (root / "planning" / "PROJECT_PLAN_v3.29.0_release_v1.0.md").write_text(roster)
    client_text = "Claude Code and Codex CLI" if clients else "Claude Code"
    (root / "planning" / "RULINGS_v329_release_2026-08-01.md").write_text(
        "## `v329-release:R1`\n## `v329-release:R2`\n## `v329-release:R3`\n" +
        f"{client_text}; generated-view count = 1; contradictions = 0; omissions = 0; "
        "manual cross-artifact joins = 0; downstream Codex-native recovery; "
        "2026-08-02T06:55:08-07:00")
    (root / "governance" / "GOALS.md").write_text("GOAL-V329-DELIVERED")
    (root / "governance" / "REQUIREMENTS_LEDGER.md").write_text("- id: REQ-TEST-001")


def test_exact_one_zero_zero_zero_view(tmp_path):
    """R-TEST-001-02: governed view meets exact 1/0/0/0 threshold."""
    _fixture(tmp_path)
    view = build_view(tmp_path, "3.29.0")
    assert (view["views"], view["contradictions"], view["omissions"], view["manual_joins"]) == (1, 0, 0, 0)
    assert view["state"] == "PASS"
    assert view["requirements_reach"]["target_rulings"] == [
        "v329-release:R1", "v329-release:R2", "v329-release:R3"]


def test_missing_supported_client_is_an_omission(tmp_path):
    """R-TEST-001-02: missing governed client is an omission."""
    _fixture(tmp_path, clients=False)
    view = build_view(tmp_path, "3.29.0")
    assert view["state"] == "FAIL"
    assert "missing fact: supported_clients" in view["issues"]


def test_markdown_contains_all_principal_decision_fields(tmp_path):
    """R-TEST-001-02: rendered view contains principal decision fields."""
    _fixture(tmp_path)
    text = render_markdown(build_view(tmp_path, "3.29.0"))
    for token in ("Locked outcomes", "Supported clients", "Delivery behavior", "Deadline", "Boundary"):
        assert token in text
