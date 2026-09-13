"""C-34-25 — a downstream consumer that actually cites and consumes the voice artifact.

INIT-VOICE-FRAMEWORK EC-2 says voice governance artifacts must be "cited by >=1 downstream
consumer -- verify: consumer reference". Before this check, three situations were
indistinguishable, and two of them were live in the fleet:

  * 13 templates carried an identical COPY of knowledge/voice/README.md  (not a consumer)
  * 13 templates cited VOICE.md, which existed nowhere                    (dangling, not adoption)
  * an actual binding                                                     (adoption)

Each test below fails if those collapse back together.
"""
from __future__ import annotations

import importlib.util
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "cvcb", REPO / "scripts" / "check_voice_consumer_binding.py")
cvcb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(cvcb)

BOUND, PARTIAL, DANGLING, ABSENT = cvcb.BOUND, cvcb.PARTIAL, cvcb.DANGLING, cvcb.ABSENT

SCAFFOLD = "# Principal Voice\n\nThis directory holds the characterization.\n"
ORDER = ("Specification -> Evidence Bank -> Enforcement -> Calibration Memory -> Ontology")


def test_unreadable_cited_target_is_unavailable_not_dangling(tmp_path):
    root = agent(tmp_path, consumer_text="knowledge/voice/README.md " + ORDER)
    assert cvcb.assess(root, [])["overall"] == BOUND
    target = root / "knowledge/voice/README.md"
    target.chmod(0)
    try:
        result = cvcb.assess(root, [])
        assert result["overall"] == cvcb.UNAVAILABLE
        assert result["ec2_satisfied"] is None
        assert result["counts"][DANGLING] == 0
        assert cvcb.exit_code(result) == 3
    finally:
        target.chmod(0o600)


def test_unreadable_citation_does_not_hide_observed_dangling(tmp_path):
    root = agent(tmp_path, consumer_text="knowledge/voice/README.md MISSING/VOICE.md " + ORDER)
    target = root / "knowledge/voice/README.md"
    target.chmod(0)
    try:
        result = cvcb.assess(root, [])
        assert result["overall"] == DANGLING
        assert result["counts"][DANGLING] == 1
        assert result["consumers"][0]["unresolved"] == ["MISSING/VOICE.md"]
        assert result["fully_read"] is False
        assert result["limit"]
    finally:
        target.chmod(0o600)


def agent(tmp: Path, *, with_scaffold=True, consumer_text=None) -> Path:
    root = tmp / "agent"
    if with_scaffold:
        (root / "knowledge" / "voice").mkdir(parents=True)
        (root / "knowledge" / "voice" / "README.md").write_text(SCAFFOLD)
    if consumer_text is not None:
        d = root / ".claude" / "skills" / "some-skill"
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(consumer_text)
    root.mkdir(parents=True, exist_ok=True)
    return root


def test_a_copy_of_the_scaffold_is_not_a_consumer(tmp_path):
    """13 templates each carry this file. None of them thereby consumes it."""
    root = agent(tmp_path)
    res = cvcb.assess(root, [])
    assert res["consumers"] == []
    assert res["overall"] == ABSENT
    assert res["ec2_satisfied"] is False


def test_a_dangling_citation_is_a_defect_not_adoption(tmp_path):
    """The live fleet state: aget-create-briefing cited VOICE.md, which existed nowhere."""
    root = agent(tmp_path, consumer_text="- Apply VOICE.md anti-patterns if available\n")
    res = cvcb.assess(root, [])
    assert res["overall"] == DANGLING
    assert res["ec2_satisfied"] is False
    assert cvcb.exit_code(res) == 1


def test_a_resolvable_citation_with_the_composition_order_is_BOUND(tmp_path):
    root = agent(tmp_path, consumer_text=(
        "Compose from `knowledge/voice/`, contract in `knowledge/voice/README.md`.\n" + ORDER))
    res = cvcb.assess(root, [])
    assert res["overall"] == BOUND
    assert res["ec2_satisfied"] is True
    assert cvcb.exit_code(res) == 0


def test_a_resolvable_citation_without_a_composition_order_is_only_PARTIAL(tmp_path):
    """Consuming without composing. Cites the artifact, applies nothing from it."""
    root = agent(tmp_path, consumer_text="See `knowledge/voice/README.md` for voice.\n")
    res = cvcb.assess(root, [])
    assert res["consumers"][0]["outcome"] == PARTIAL
    assert res["ec2_satisfied"] is False
    assert cvcb.exit_code(res) == 2


def test_dangling_outranks_bound_so_one_broken_citation_still_fails(tmp_path):
    root = agent(tmp_path, consumer_text=(
        "Compose from `knowledge/voice/README.md`.\n" + ORDER))
    d = root / ".claude" / "skills" / "other"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text("Apply VOICE.md if available\n")
    res = cvcb.assess(root, [])
    assert res["counts"][BOUND] == 1 and res["counts"][DANGLING] == 1
    assert res["overall"] == DANGLING and res["ec2_satisfied"] is False


def test_the_scaffold_is_excluded_even_when_it_names_the_layers(tmp_path):
    """A document cannot be its own consumer, however complete it is."""
    root = tmp_path / "agent"
    (root / "knowledge" / "voice").mkdir(parents=True)
    (root / "knowledge" / "voice" / "README.md").write_text(
        SCAFFOLD + ORDER + "\nsee knowledge/voice/README.md\n")
    res = cvcb.assess(root, [])
    assert res["consumers"] == [], "the scaffold must never count as its own consumer"


def test_scanning_can_be_scoped_to_a_subdirectory(tmp_path):
    root = agent(tmp_path, consumer_text=(
        "Compose from `knowledge/voice/README.md`.\n" + ORDER))
    assert cvcb.assess(root, [".claude/skills"])["ec2_satisfied"] is True
    missing = cvcb.assess(root, ["docs"])
    assert missing["overall"] == cvcb.UNAVAILABLE
    assert missing["ec2_satisfied"] is None and cvcb.exit_code(missing) == 3


def test_a_missing_root_is_an_input_error_never_a_pass(tmp_path):
    import pytest
    with pytest.raises(NotADirectoryError):
        cvcb.assess(tmp_path / "nope", [])


def test_the_repaired_canonical_skill_is_bound_against_a_scaffolded_root(tmp_path):
    """End-to-end on the real artifact: canonical's skill + a template's scaffold."""
    src = REPO / ".claude" / "skills" / "aget-create-briefing" / "SKILL.md"
    if not src.exists():
        import pytest
        pytest.skip("aget-create-briefing not present in this checkout")
    root = tmp_path / "agent"
    (root / "knowledge" / "voice").mkdir(parents=True)
    (root / "knowledge" / "voice" / "README.md").write_text(SCAFFOLD)
    d = root / ".claude" / "skills" / "aget-create-briefing"
    d.mkdir(parents=True)
    (d / "SKILL.md").write_text(src.read_text())
    res = cvcb.assess(root, [])
    assert res["ec2_satisfied"] is True, (
        "the shipped skill must cite a resolvable voice artifact and its composition order")
    assert res["counts"][DANGLING] == 0, "the shipped skill must cite no dangling voice path"
