from __future__ import annotations

import importlib.util
import os
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def load(n, p):
    s = importlib.util.spec_from_file_location(n, REPO / p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


v = load("voice_accept", "scripts/check_voice_consumer_binding.py")
rte = load("runtime_accept", "scripts/check_runtime_support_evidence.py")
fvg = load("forecast_accept", "scripts/forecast_value_gate.py")
ORDER = "Specification Evidence Bank Enforcement"


def root_with_bound(tmp_path):
    root = tmp_path / "r"
    (root / "knowledge/voice").mkdir(parents=True)
    (root / "knowledge/voice/README.md").write_text("x")
    (root / "ok.md").write_text("knowledge/voice/README.md " + ORDER)
    return root


def test_entry_types_containment_and_double_count(tmp_path):
    root = root_with_bound(tmp_path)
    outside = tmp_path / "elsewhere"
    outside.mkdir()
    (outside / "VOICE.md").write_text("x")
    (root / "out").symlink_to(outside, target_is_directory=True)
    (root / "file.md").symlink_to(root / "ok.md")
    fifo = root / "pipe.md"
    os.mkfifo(fifo)
    r = v.assess(root, [".", "."])
    assert r["overall"] == v.UNAVAILABLE and r["ec2_satisfied"] is None and v.exit_code(r) == 3
    assert r["counts"][v.BOUND] == 1


def test_citation_side_escape_never_binds(tmp_path):
    root = root_with_bound(tmp_path)
    outside = tmp_path / "VOICE.md"
    outside.write_text("x")
    (root / "ok.md").write_text("../VOICE.md " + ORDER)
    r = v.assess(root, [])
    assert r["counts"][v.DANGLING] == 1 and not r["ec2_satisfied"]


def test_template_scaffold_copy_is_never_consumer(tmp_path):
    root = tmp_path / "r"
    p = root / "template/knowledge/voice"
    p.mkdir(parents=True)
    (p / "README.md").write_text("knowledge/voice/README.md " + ORDER)
    r = v.assess(root, [])
    assert r["consumers"] == [] and r["overall"] == v.ABSENT


def test_renderer_and_exit_expose_limit(tmp_path):
    root = root_with_bound(tmp_path)
    d = root / "blocked"
    d.mkdir()
    d.chmod(0o400)
    try:
        r = v.assess(root, [])
        text = v.render(r)
        assert "LIMIT:" in text and "UNREACHED:" in text and v.exit_code(r) == 3
    finally:
        d.chmod(0o700)


def test_runtime_partial_read_does_not_create_absence(tmp_path):
    rec = tmp_path / "rec"
    rec.mkdir()
    (rec / "bad.json").write_bytes(b"\xff\xfe")
    r = rte.level3_governed("x", rec)
    assert (
        r["verdict"] == "UNKNOWN" and not r["fully_read"] and "could not fully read" in r["limit"]
    )


def test_runtime_positive_receipt_survives_unread_sibling(tmp_path):
    rec = tmp_path / "rec"
    rec.mkdir()
    (rec / "ok.json").write_text('{"runtime":"x","invoked":true,"outcome":"ok"}')
    (rec / "bad.json").write_bytes(b"\xff\xfe")
    r = rte.level3_governed("x", rec)
    assert r["verdict"] == "YES" and r["receipts"] and not r["fully_read"]


def test_forecast_refuses_unreadable_and_escaping_evidence(tmp_path):
    p = tmp_path / "x.md"
    p.write_text("needle")
    p.chmod(0)
    row = {
        "id": "A",
        "disposition": "SELECT",
        "tier": "T1",
        "su": 7,
        "predicted_v1": "L3",
        "class": "capability",
        "source": {"path": "x.md", "pattern": "needle"},
    }
    try:
        assert fvg.evidence_states([row], tmp_path)["A"]["state"] == fvg.UNAVAILABLE
    finally:
        p.chmod(0o600)
    row["source"]["path"] = "../x.md"
    assert fvg.evidence_states([row], tmp_path)["A"]["state"] == fvg.UNAVAILABLE
