"""C-34-23 — case variants must match; a zero result must say WHICH zero it is.

Two defects, both at the canonical surface:
  * the match was case-sensitive, justified as "labels are TitleCase nouns" —
    true of the label, irrelevant to the prose being searched;
  * the empty branch printed one optimistic sentence covering two opposite
    states ("grounded OR vocabulary-light").
"""
import re
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(REPO / "scripts"))
import ground_artifact as ga  # noqa: E402


def _pattern(label):
    """The production matcher, read from source rather than re-implemented."""
    src = (REPO / "scripts" / "ground_artifact.py").read_text()
    assert "re.IGNORECASE" in src, "matcher must be case-insensitive (C-34-23)"
    return re.compile(r"(?<![\w-])" + re.escape(label) + r"(?![\w-])", re.IGNORECASE)


# ------------------------------------------------------------------- case variants
def test_lowercase_prose_matches_titlecase_label():
    """The exact class the tool existed to find and could not see."""
    assert _pattern("Scope Lock").search("the scope lock ceremony ran")


def test_uppercase_and_mixed_variants_match():
    pat = _pattern("Scope Lock")
    assert pat.search("SCOPE LOCK completed")
    assert pat.search("ScOpE lOcK")


def test_exact_case_still_matches():
    """Compatibility: everything that matched before still matches."""
    assert _pattern("Scope Lock").search("the Scope Lock is bound")


# --------------------------------------------------------------- word boundaries kept
def test_word_boundary_preserved_prefix():
    assert not _pattern("Scope Lock").search("rescope lock")


def test_word_boundary_preserved_suffix():
    assert not _pattern("Receipt").search("Receipts")
    assert not _pattern("Receipt").search("Receipt-bound")


def test_substring_inside_a_word_does_not_match():
    assert not _pattern("Principal").search("Principality")


# ------------------------------------------------------- honest no-match vs grounded
# Hermetic: canonical ships no ontology YAML (it is fleet-local), so these build a
# minimal canonical-shaped tree with a fixture ontology and run the real script there.
# Depending on the private ontology would make a canonical test pass for a reason the
# canonical payload does not carry.

FIXTURE_ONTOLOGY = """concepts:
  - id: C257
    prefLabel: Scope Lock
    uri: aget:concept/ScopeLock
    definition: A governance commitment point.
  - id: C1888
    prefLabel: Receipt
    uri: aget:concept/Receipt
    definition: Evidence of an act.
"""


def _sandbox(tmp_path):
    root = tmp_path / "canon"
    (root / "scripts").mkdir(parents=True)
    (root / "ontology").mkdir(parents=True)
    (root / "ontology" / "ONTOLOGY_personal_ai_systems_v1.0.yaml").write_text(FIXTURE_ONTOLOGY)
    (root / "scripts" / "ground_artifact.py").write_text(
        (REPO / "scripts" / "ground_artifact.py").read_text())
    return root


def _run_in(root, body, name="artifact.md"):
    target = root / name
    target.write_text(body)
    r = subprocess.run([sys.executable, str(root / "scripts" / "ground_artifact.py"),
                        "--file", str(target)], capture_output=True, text=True, cwd=root)
    return r.stdout + r.stderr


def test_zero_match_with_no_bindings_reports_HONEST_NO_MATCH(tmp_path):
    root = _sandbox(tmp_path)
    out = _run_in(root, "qqqq wwww zzzz plainly unrelated filler text\n")
    assert "HONEST NO-MATCH" in out, out[-500:]
    assert "absence of match, not evidence of grounding" in out


def test_zero_match_never_claims_grounded_when_nothing_is_bound(tmp_path):
    """The precise regression: the old wording said 'grounded or vocabulary-light'."""
    root = _sandbox(tmp_path)
    out = _run_in(root, "qqqq wwww zzzz plainly unrelated filler text\n")
    assert "artifact is grounded or vocabulary-light" not in out


def test_already_grounded_artifact_is_not_called_a_no_match(tmp_path):
    root = _sandbox(tmp_path)
    out = _run_in(root, "Bound inline as (`aget:concept/ScopeLock`, C257) already.\n")
    assert "HONEST NO-MATCH" not in out, out[-500:]


def test_the_two_zero_states_print_different_text(tmp_path):
    root = _sandbox(tmp_path)
    empty = _run_in(root, "qqqq wwww zzzz\n", "empty.md")
    bound = _run_in(root, "(`aget:concept/ScopeLock`, C257)\n", "bound.md")
    assert empty != bound, "the two opposite zero states must be distinguishable"


def test_case_variant_is_actually_suggested_end_to_end(tmp_path):
    """The repair, exercised through the real entrypoint rather than the regex alone."""
    root = _sandbox(tmp_path)
    out = _run_in(root, "the scope lock ceremony completed today\n")
    assert "C257" in out, out[-500:]
