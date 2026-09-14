from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]


def load(n, p):
    s = importlib.util.spec_from_file_location(n, REPO / p)
    m = importlib.util.module_from_spec(s)
    s.loader.exec_module(m)
    return m


voice = load("voice_subject", "scripts/check_voice_consumer_binding.py")


def test_unreached_voice_subject_has_all_four_limbs_and_limit(tmp_path):
    root = tmp_path / "r"
    root.mkdir()
    d = root / "x"
    d.mkdir()
    d.chmod(0o400)
    try:
        r = voice.assess(root, [])
        c = r["classification"]
        assert c["subject_bound"] and not c["subject_reached"]
        assert not c["definite"] and r["limit"] and r["ec2_satisfied"] is None
    finally:
        d.chmod(0o700)


def test_bound_observation_is_not_withheld(tmp_path):
    root = tmp_path / "r"
    (root / "knowledge/voice").mkdir(parents=True)
    (root / "knowledge/voice/README.md").write_text("voice")
    d = root / "consumer"
    d.mkdir()
    (d / "x.md").write_text("knowledge/voice/README.md\nSpecification Evidence Bank Enforcement")
    r = voice.assess(root, [])
    assert r["overall"] == voice.BOUND and r["classification"]["definite"]
    assert r["classification"]["affirming_evidence"] == ["consumer/x.md"]


def test_dangling_observation_survives_as_definite_finding(tmp_path):
    root = tmp_path / "r"
    root.mkdir()
    (root / "x.md").write_text("VOICE.md")
    r = voice.assess(root, [])
    assert r["overall"] == voice.DANGLING and voice.exit_code(r) == 1
