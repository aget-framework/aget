import ast
import pytest
from pathlib import Path

from scripts.release_distribution_evidence import PREDICATES, validate

ROOT = Path(__file__).resolve().parents[1]


def test_all_four_predicates_are_required():
    """R-TEST-001-02: all four delivery predicates are independently required."""
    receipt = {name: True for name in PREDICATES}
    assert validate(receipt)["state"] == "PASS"
    for missing in PREDICATES:
        candidate = dict(receipt)
        candidate[missing] = False
        result = validate(candidate)
        assert result["state"] == "FAIL"
        assert result["missing"] == [missing]


def test_producer_cannot_imply_downstream_delivery():
    """R-TEST-001-02: producer evidence cannot imply downstream delivery."""
    result = validate({"producer": True, "distribution_point": True})
    assert result["state"] == "FAIL"
    assert result["predicates"]["received_state"] is False
    assert result["predicates"]["downstream_behavior"] is False
    assert result["inference_prohibited"] is True


def test_tag_actuator_calls_battery_before_repo_loop():
    """R-TEST-001-02: tag actuator gates before repository mutation."""
    if not (ROOT / "scripts" / "tag_release.py").is_file():
        pytest.skip("tag_release.py is manager-owned; core validates the predicate model only")
    source = (ROOT / "scripts" / "tag_release.py").read_text()
    tree = ast.parse(source)
    main = next(node for node in tree.body if isinstance(node, ast.FunctionDef) and node.name == "main")
    calls = []
    for node in ast.walk(main):
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            calls.append((node.lineno, node.func.id))
    battery_line = min(line for line, name in calls if name == "run_release_gate_battery")
    mutation_lines = [line for line, name in calls if name in {"tag_repo", "push_tag", "create_release"}]
    assert mutation_lines
    assert battery_line < min(mutation_lines)


def test_tag_actuator_fails_closed_on_battery_failure():
    """R-TEST-001-02: battery failure stops the actuator."""
    if not (ROOT / "scripts" / "tag_release.py").is_file():
        pytest.skip("tag_release.py is manager-owned; core validates the predicate model only")
    source = (ROOT / "scripts" / "tag_release.py").read_text()
    assert "if not gate_ok:" in source
    assert "RELEASE GATE BATTERY FAILED" in source
