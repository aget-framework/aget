"""Two-polarity guard: the declared canonical surface must be DERIVED, not asserted.

Defect this closes (measured 2026-08-05): `SURFACES_SEARCHED` was a static list
literal printed unconditionally by generate_report(), while find_specs() skipped
unresolvable roots with `continue`. On hosts without the canonical root, every
study printed a coverage claim for a tier it never searched — manufactured
coverage, the mirror of the manufactured absence gh#1580 was filed against.

BOTH POLARITIES ARE ASSERTED ON PURPOSE. A one-sided test is what let this
regress twice:
  - one prior form assumed the canonical checkout was the agent-root sibling;
  - another assumed it was nested under a sibling checkout.
Each passed in one local layout. Neither was portable. So: a mounted seat MUST
report the resolved path, and an unmounted seat MUST report UNAVAILABLE, and no
test here may hardcode an absolute checkout layout.
"""
import sys
import tempfile
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import study_topic  # noqa: E402


class TestCanonicalSurfaceIsDerived(unittest.TestCase):

    def setUp(self):
        self._original = list(study_topic.SURFACES_SEARCHED)

    def tearDown(self):
        study_topic.SURFACES_SEARCHED[:] = self._original

    def test_unmounted_seat_reports_unavailable(self):
        """POLARITY 1 — no adjacent canonical checkout: the claim must be withdrawn.

        Satisfies: R-SESSION-007-03 (report related artifacts) — the reported
        surface is part of the report, so an unreachable tier must be declared
        unreachable. CAP-SESSION-007 study-topic protocol.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "instance"
            root.mkdir()
            self.assertEqual(study_topic.find_canonical_spec_roots(root), [])
            study_topic.refresh_canonical_spec_surface(root)
            self.assertTrue(
                any("UNAVAILABLE" in s for s in study_topic.SURFACES_SEARCHED),
                "an unmounted seat must NOT advertise the canonical tier",
            )

    def test_mounted_seat_reports_the_resolved_path(self):
        """POLARITY 2 — canonical present: the claim must be made, and be concrete.

        Satisfies: R-SESSION-007-03 — a reachable tier must be reported, and
        reported as the resolved path rather than a pattern. CAP-SESSION-007.
        """
        with tempfile.TemporaryDirectory() as tmpdir:
            root = Path(tmpdir) / "instance"
            canonical = Path(tmpdir) / "framework-copy" / "specs"
            root.mkdir()
            canonical.mkdir(parents=True)
            (canonical / "AGET_SESSION_SPEC.md").write_text("spec")

            self.assertEqual(study_topic.find_canonical_spec_roots(root), [canonical])
            study_topic.refresh_canonical_spec_surface(root)
            surfaces = " ".join(study_topic.SURFACES_SEARCHED)
            self.assertIn(str(canonical), surfaces)
            self.assertNotIn("UNAVAILABLE", surfaces)

    def test_resolver_accepts_both_supported_checkout_layouts(self):
        """Checkout NAME is not a contract, and neither is its DEPTH.

        Satisfies: R-SESSION-007-03 · CAP-SESSION-007 — portability of the
        canonical resolver across the two supported checkout layouts.

        Both shapes are supported; a resolver that knows only one
        produces a false surface claim in the other.
        """
        for label, rel in (("repo-is-sibling", ("canon", "specs")),
                           ("repo-contains-aget", ("canon", "aget", "specs"))):
            with self.subTest(layout=label):
                with tempfile.TemporaryDirectory() as tmpdir:
                    root = Path(tmpdir) / "instance"
                    root.mkdir()
                    canonical = Path(tmpdir).joinpath(*rel)
                    canonical.mkdir(parents=True)
                    (canonical / "AGET_SESSION_SPEC.md").write_text("spec")
                    self.assertEqual(
                        study_topic.find_canonical_spec_roots(root), [canonical],
                        f"{label} layout must resolve",
                    )

    def test_no_surface_entry_is_an_unconditional_path_literal(self):
        """The regression vector itself: a hardcoded relative path in the banner.

        Satisfies: R-SESSION-007-03 · CAP-SESSION-007 — falsifier for the
        defect CLASS, not just the instance.

        Falsifier for the whole class — if someone re-introduces a literal like
        '../aget/specs/**' into SURFACES_SEARCHED, it prints whether or not it
        resolves, and this test fails.
        """
        for surface in study_topic.SURFACES_SEARCHED:
            self.assertNotIn(
                "../aget/", surface,
                "canonical tier must be resolved at runtime, never asserted as a literal",
            )


if __name__ == "__main__":
    unittest.main()
