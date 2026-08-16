"""Two-polarity guard: the knowledge/ontology tier must reach BOTH .md and .yaml.

Defect this closes (gh#2257, found by private-legalon-contributor-reinvent-AGET
2026-08-15, corroborated here): `find_knowledge()` globbed `rglob('*.md')` only,
while `SURFACES_SEARCHED` advertised `knowledge/** + ontology/**` and has since
v3.25 (C-25-14, 2026-07-04). Governed vocabulary lives in `ONTOLOGY_*.yaml`, so
the tier the surface exists to expose was never opened on any run. The specs tier
(find_specs) already globbed BOTH extensions, which is the argument that the
ontology glob was an oversight rather than a scope decision.

Measured at this seat before the fix: 82 yaml files / 3,678,886 bytes unreachable
against 3 md files / 53,726 bytes reachable -- 1.4% of ontology bytes. The term
`FrameworkManagerArchetype`, this agent's OWN archetype concept (C610, cited in
its own AGENTS.md), occurred 31 times in ontology/*.yaml and returned 0 hits.

WHY THIS FILE ASSERTS NON-ZERO, AND WHY THAT IS THE LOAD-BEARING PART.
The nearest house template, test_study_topic_searches_spec_tier, asserts only
that the findings key EXISTS ("key present even if empty") and that a substring
appears in the SURFACES_SEARCHED source. That test PASSES against the exact
defect gh#2257 reports: a declared tier returning a confident zero. A guard
copied from it would have been a surviving mutant. A fix verified only by "the
suite still passes" cannot distinguish repaired from unchanged, so every positive
polarity below asserts a POSITIVE COUNT over a term planted only in a .yaml.

SCOPE AT CANONICAL: this copy carries the reach polarities only. The
instance seat additionally derives the SURFACES_SEARCHED row from a
KNOWLEDGE_EXTENSIONS tuple and guards that separately; canonical has the
minimal glob fix, so those assertions are omitted here rather than failing
against symbols canonical does not define.

BOTH POLARITIES ARE ASSERTED ON PURPOSE (the L1300 house idiom):
  - a term present only in .yaml MUST be found  -> fails before the fix;
  - a term present only in .md MUST still be found -> the fix adds reach without
    trading it away;
  - a term present in NEITHER MUST return zero -> proves the positive polarities
    are real matches and not a matcher that accepts everything.

Refs: gh#2257 (this defect) -- gh#1852 (open umbrella: treat the study_topic
scope/index/scoring family as ONE search-contract audit, not point-fixes) --
L1300 (declared scope must be DERIVED from executed scope; study_topic.py is its
instance #1) -- L1266 (a vocabulary pre-check that read one surface and reported
absence) -- L1330 (absence claims fail on polarity, not on care).
"""
import os
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import study_topic  # noqa: E402

# A term with no other referent anywhere in the corpus, so a hit can only have
# come from the planted file. Deliberately not a real concept name.
PLANTED = "Zarquon_Vocabulary_Probe"
ABSENT = "Nonexistent_Probe_Never_Written_Anywhere"


class _FakeSeat:
    """A synthetic agent root with a knowledge/ and ontology/ tier."""

    def __init__(self, tmpdir):
        self.root = Path(tmpdir) / "instance"
        (self.root / "knowledge").mkdir(parents=True)
        (self.root / "ontology").mkdir(parents=True)

    def write(self, relpath, text):
        target = self.root / relpath
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(text)

    def __enter__(self):
        self._prev = os.environ.get("AGET_STUDY_ROOT")
        os.environ["AGET_STUDY_ROOT"] = str(self.root)
        return self

    def __exit__(self, *exc):
        if self._prev is None:
            os.environ.pop("AGET_STUDY_ROOT", None)
        else:
            os.environ["AGET_STUDY_ROOT"] = self._prev
        return False


def _yaml_concept(term):
    """A minimally realistic SKOS-shaped concept entry."""
    return (
        "concepts:\n"
        "  - id: C999\n"
        f"    prefLabel: {term}\n"
        f"    skos:definition: \"A planted {term} used by the gh#2257 guard.\"\n"
        f"    altLabel: [{term}]\n"
    )


class TestOntologyTierReachesYaml(unittest.TestCase):
    """POLARITY 1 -- the falsifier. Must FAIL against the pre-fix glob."""

    def test_term_only_in_ontology_yaml_is_found(self):
        """A term present ONLY in ontology/*.yaml must be reachable.

        Satisfies: CAP-SESSION-007-02 (search KB for topic-related artifacts)
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            with _FakeSeat(tmpdir) as seat:
                seat.write("ontology/ONTOLOGY_probe_v1.0.yaml", _yaml_concept(PLANTED))
                seat.write("ontology/README.md", "This tier holds the vocabulary.\n")
                hits = study_topic.find_knowledge(PLANTED)
                self.assertGreater(
                    len(hits), 0,
                    "gh#2257: a term present ONLY in ontology/*.yaml must be "
                    "reachable. A zero here is manufactured absence -- the "
                    "banner advertises 'ontology/**' while the glob reads "
                    "'*.md' only, so the caller reads 'the vocabulary does not "
                    "contain this' when the truth is 'the vocabulary was never "
                    "opened'.",
                )
                self.assertTrue(
                    any(h["doc"].endswith(".yaml") for h in hits),
                    "the hit must come FROM the .yaml file, not from a "
                    "neighbouring .md that happens to score",
                )
                # Satisfies: CAP-SESSION-007-02 (search the KB surface)

    def test_term_only_in_knowledge_yaml_is_found(self):
        """knowledge/ holds .yaml at some seats for the same reason (gh#2257).

        Satisfies: CAP-SESSION-007-02
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            with _FakeSeat(tmpdir) as seat:
                seat.write("knowledge/METRICS_probe.yaml", _yaml_concept(PLANTED))
                hits = study_topic.find_knowledge(PLANTED)
                self.assertGreater(
                    len(hits), 0,
                    "gh#2257: the fix applies to BOTH tiers the loop walks, "
                    "not to ontology/ alone.",
                )
                # Satisfies: CAP-SESSION-007-02


class TestOntologyTierStillReachesMarkdown(unittest.TestCase):
    """POLARITY 2 -- the fix must ADD reach, not trade it."""

    def test_term_only_in_ontology_markdown_is_still_found(self):
        """Pre-existing .md reach must survive the .yaml fix.

        Satisfies: CAP-SESSION-007-02
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            with _FakeSeat(tmpdir) as seat:
                seat.write(
                    "ontology/NOTES_probe.md",
                    f"# Notes\n\nThe {PLANTED} concept is discussed here.\n",
                )
                hits = study_topic.find_knowledge(PLANTED)
                self.assertGreater(
                    len(hits), 0,
                    "the pre-existing .md reach must survive the .yaml fix",
                )
                # Satisfies: CAP-SESSION-007-02


class TestOntologyTierDoesNotMatchEverything(unittest.TestCase):
    """POLARITY 3 -- proves the positive polarities are real matches.

    Without this, a matcher that returned every file would satisfy polarities 1
    and 2 while meaning nothing. This is the assertion that makes the non-zero
    assertions above load-bearing rather than decorative.
    """

    def test_term_in_neither_extension_returns_zero(self):
        """A term written nowhere must return zero.

        Satisfies: CAP-SESSION-007-02
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            with _FakeSeat(tmpdir) as seat:
                seat.write("ontology/ONTOLOGY_probe_v1.0.yaml", _yaml_concept(PLANTED))
                seat.write("ontology/NOTES_probe.md", f"The {PLANTED} concept.\n")
                hits = study_topic.find_knowledge(ABSENT)
                self.assertEqual(
                    len(hits), 0,
                    "a term written nowhere must return zero; a non-zero here "
                    "means the tier matches indiscriminately and the positive "
                    "polarities prove nothing",
                )
                # Satisfies: CAP-SESSION-007-02


if __name__ == "__main__":
    unittest.main()
