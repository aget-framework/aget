"""Falsifiers for the skill route-contract check (D-IG-12).

The check answers: does every `/aget-*` route a skill points at exist?

Both polarities matter, and the first draft of this check failed the negative
one. It matched `/aget-aget` inside the repo path `example-org/aget-aget` (present in
14 skills) and reported it as a broken route -- flagging a *mention* as a
*promise*, which is the exact confusion the check exists to catch. A check that
cries wolf is one readers learn to skip, so the over-report is not a cosmetic
bug; it destroys the control.

Equally, the hedge heuristic must not swallow real promises. "delegated to
/aget-enhance-coherence" is a routing instruction and must gate; "future
/aget-enhance-ci candidate" is prose and must not.
"""

import sys
import unittest
from pathlib import Path

REPO = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO / "scripts"))

import check_skill_route_contract as rc  # noqa: E402


class TestRoutePatternNegativePolarity(unittest.TestCase):
    """The regex must not turn repo paths and words into routes."""

    def test_repo_path_is_not_a_route(self):
        for line in (
            "| Tracking Issue | gh#1412 (example-org/aget-aget) |",
            "gh issue list --repo example-org/aget-aget --state all",
            "file an issue at github.com/example-org/aget-aget",
        ):
            with self.subTest(line=line):
                self.assertEqual(
                    rc.ROUTE_RE.findall(line), [],
                    "a repo path must not read as a route",
                )

    def test_path_segment_is_not_a_route(self):
        self.assertEqual(rc.ROUTE_RE.findall("../aget/.claude/aget-check-health"), [])

    def test_real_route_still_matches(self):
        """Positive polarity: the fix must not have disabled detection."""
        self.assertEqual(
            rc.ROUTE_RE.findall("run `/aget-check-health` first"),
            ["aget-check-health"],
        )
        self.assertEqual(
            rc.ROUTE_RE.findall("- `/aget-enhance-config` — pair with this"),
            ["aget-enhance-config"],
        )

    def test_multiple_routes_on_one_line(self):
        found = rc.ROUTE_RE.findall("`/aget-learn`, `/aget-checkpoint`")
        self.assertEqual(found, ["aget-learn", "aget-checkpoint"])


class TestHedgeClassification(unittest.TestCase):
    def test_unhedged_promise_gates(self):
        for line in (
            "- Remediate cross-artifact coherence (delegated to `/aget-enhance-coherence`)",
            "| V-CFG-001 | Specs | `/aget-check-spec` |",
            "pair with /aget-enhance-config for remediation",
        ):
            with self.subTest(line=line):
                self.assertFalse(rc.is_hedged(line), f"must gate: {line}")

    def test_hedged_mention_does_not_gate(self):
        for line in (
            "- Remediate CI/test failures (out of scope; future `/aget-enhance-ci` candidate)",
            "**Renamed**: `/aget-checkpoint` → `/aget-save-state`",
            "`/aget-fix-*` reserved for artifacts where correction applies",
            "optional guidance (deferred to `/aget-fleet-economics` when available)",
            "| Other patterns | ✗ Invalid | `/aget-skill-create` (O-V not S-V-O) |",
        ):
            with self.subTest(line=line):
                self.assertTrue(rc.is_hedged(line), f"must not gate: {line}")


class TestThreeStateContract(unittest.TestCase):
    """CONVENTION_check_three_state_contract: PASS / FAIL / UNREACHABLE."""

    def test_states_are_the_declared_three(self):
        report = self._report()
        self.assertIn(report["state"], {"PASS", "FAIL", "UNREACHABLE"})

    def test_unreachable_does_not_gate(self):
        """Contract rule 2: a missing surface degrades, it does not block."""
        original = rc.SKILLS_DIR
        try:
            rc.SKILLS_DIR = REPO / "no-such-skills-dir"
            self.assertEqual(rc.run(as_json=True), 0,
                             "UNREACHABLE must exit 0, not gate")
        finally:
            rc.SKILLS_DIR = original

    def test_owed_and_aspirational_are_counted_separately(self):
        """Contract rule 3: never fold the buckets into one number."""
        report = self._report()
        for key in ("owed", "aspirational", "canonical_only"):
            self.assertIn(key, report)

    def _report(self):
        import io
        import json
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc.run(as_json=True)
        return json.loads(buf.getvalue())


class TestOutputTemplateSurface(unittest.TestCase):
    """Bare (slash-less) names inside an output template are claims, not mentions.

    Origin (2026-08-10): `aget-analyze-ontology` disclosed at :199 that
    `/aget-analyze-kb` does not exist, and still named `aget-analyze-kb` at :157
    inside its `## Output Format` template as an existing consuming skill.
    ROUTE_RE saw only :199 -- so hedging the confession moved the route to
    `aspirational` while the line that PERFORMS the false claim shipped unseen.

    Both polarities are load-bearing here for the same reason the slash regex
    needed them: matching bare names in ordinary prose would flag every sibling
    mention in every Related/changelog section, and a noisy check is a dead one.
    """

    def _scan_fixture(self, body: str, dirname: str = "aget-demo",
                      also: dict | None = None) -> dict:
        import tempfile
        original = rc.SKILLS_DIR
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            (root / dirname).mkdir()
            (root / dirname / "SKILL.md").write_text(body)
            for extra in (also or {}):
                (root / extra).mkdir()
                (root / extra / "SKILL.md").write_text(also[extra])
            try:
                rc.SKILLS_DIR = root
                return rc.scan()
            finally:
                rc.SKILLS_DIR = original

    def test_bare_name_in_output_template_is_detected(self):
        """V-ROUTE-001: the :157 shape (bare name in an output template) must be seen."""
        refs = self._scan_fixture(
            "# demo\n\n## Output Format\n\n```\n"
            "Consuming skills: 2 (aget-demo, aget-ghost)\n```\n"
        )
        self.assertIn("aget-ghost", refs)
        self.assertEqual(refs["aget-ghost"][0]["surface"], "output-template")

    def test_bare_name_in_prose_is_not_detected(self):
        """V-ROUTE-002: bare names in ordinary prose must NOT flag — the noise failure."""
        refs = self._scan_fixture(
            "# demo\n\n## Related Skills\n\n"
            "- aget-ghost - deep analysis sibling\n\n"
            "## Changelog\n\n| 1.0 | absorbed aget-ghost |\n"
        )
        self.assertNotIn("aget-ghost", refs)

    def test_bare_name_in_non_output_fence_is_not_detected(self):
        """V-ROUTE-003: a non-output fenced block naming a script is not a route promise."""
        refs = self._scan_fixture(
            "# demo\n\n## Execution\n\n```bash\n"
            "python3 scripts/aget-ghost-helper.py --check\n```\n"
        )
        self.assertNotIn("aget-ghost-helper", refs)

    def test_self_name_in_output_template_is_not_flagged(self):
        """V-ROUTE-004: a skill naming itself in its own template is never a broken promise."""
        refs = self._scan_fixture(
            "# demo\n\n## Output Format\n\n```\n=== aget-demo ===\n```\n"
        )
        self.assertNotIn("aget-demo", refs)

    def test_installed_route_named_bare_does_not_gate(self):
        """V-ROUTE-005: an installed skill named bare in a template must resolve, not gate."""
        import io
        import json
        import contextlib
        import tempfile
        original = rc.SKILLS_DIR
        with tempfile.TemporaryDirectory() as td:
            root = Path(td)
            for name in ("aget-demo", "aget-real"):
                (root / name).mkdir()
                (root / name / "SKILL.md").write_text(f"# {name}\n")
            (root / "aget-demo" / "SKILL.md").write_text(
                "# aget-demo\n\n## Output Format\n\n```\nConsuming: aget-real\n```\n"
            )
            try:
                rc.SKILLS_DIR = root
                buf = io.StringIO()
                with contextlib.redirect_stdout(buf):
                    rc.run(as_json=True)
                report = json.loads(buf.getvalue())
            finally:
                rc.SKILLS_DIR = original
        self.assertEqual([d["route"] for d in report["owed"]], [],
                         "an installed skill named bare must not gate")

    def test_live_corpus_catches_the_originating_defect(self):
        """V-ROUTE-006: regression anchor — the real :157 line, in the real corpus."""
        import io
        import json
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc.run(as_json=True)
        report = json.loads(buf.getvalue())
        hits = [d for d in report["owed"] if d["route"] == "aget-analyze-kb"]
        if not hits:
            self.skipTest("aget-analyze-ontology:157 already repaired")
        surfaces = {m["surface"] for m in hits[0]["mentions"]}
        self.assertIn("output-template", surfaces)


@unittest.skipUnless(
    rc.SKILLS_DIR.is_dir() and any(rc.SKILLS_DIR.iterdir()),
    "live-corpus test: this repo carries no .claude/skills tree, so there are no "
    "local routes to resolve. Absence of the corpus is not a route defect.")
class TestAgainstLiveCorpus(unittest.TestCase):
    def test_self_reference_resolves(self):
        """This seat's own built routes must not report as dangling."""
        report = self._report()
        owed = {d["route"] for d in report["owed"]}
        for built in ("aget-enhance-initiative", "aget-close-initiative",
                      "aget-check-initiatives", "aget-enhance-goal"):
            self.assertNotIn(built, owed, f"{built} exists on disk")

    def test_enhance_initiative_is_no_longer_owed(self):
        """Direct regression for the D-IG-12 build.

        Instance-scoped by nature: it asserts one NAMED skill is present. A consumer
        repo that never carried that skill has no regression to guard against, so
        absence skips rather than fails. Presence-but-broken still fails.
        """
        skill = REPO / ".claude" / "skills" / "aget-enhance-initiative"
        if not skill.is_dir():
            self.skipTest(
                "instance-scoped regression: aget-enhance-initiative is not built in "
                "this repo, so the D-IG-12 regression does not apply here")
        self.assertTrue((skill / "SKILL.md").is_file(),
                        "skill directory exists but carries no SKILL.md")

    def _report(self):
        import io
        import json
        import contextlib
        buf = io.StringIO()
        with contextlib.redirect_stdout(buf):
            rc.run(as_json=True)
        return json.loads(buf.getvalue())


if __name__ == "__main__":
    unittest.main()
