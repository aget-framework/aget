"""
Regression tests for health_check.check_structural_skill_frontmatter (F2).

D71 invariant: no D71-STRUCTURAL skill (create-project, close-project,
create-initiative, file-issue) may carry `disable-model-invocation: true`,
which would block the agent model-invocation that D71 mandates.

References: gmelli/aget-aget#1489 (SGR remediation F2);
PROJECT_PLAN_structural_skill_governance_remediation_v1.0 Gate 1.
"""

import importlib.util
import tempfile
import unittest
from pathlib import Path

_spec = importlib.util.spec_from_file_location(
    "health_check", Path(__file__).resolve().parents[1] / "scripts" / "health_check.py")
health_check = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(health_check)


def _make_skill(root: Path, skill: str, frontmatter: str) -> None:
    d = root / ".claude" / "skills" / skill
    d.mkdir(parents=True, exist_ok=True)
    (d / "SKILL.md").write_text(f"---\nname: {skill}\n{frontmatter}---\n\n# /{skill}\n")


class TestStructuralSkillFrontmatter(unittest.TestCase):

    def test_flag_on_structural_skill_fails(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _make_skill(root, "aget-create-project", "disable-model-invocation: true\n")
            r = health_check.check_structural_skill_frontmatter(root)
            self.assertFalse(r.passed)
            self.assertEqual(r.severity, "error")
            self.assertIn("aget-create-project", r.message)

    def test_clean_structural_skill_passes(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _make_skill(root, "aget-create-project", "")
            r = health_check.check_structural_skill_frontmatter(root)
            self.assertTrue(r.passed)

    def test_flag_on_non_structural_skill_ignored(self):
        # disable-model-invocation is LEGITIMATE on non-structural skills (e.g. create-skill)
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _make_skill(root, "aget-create-skill", "disable-model-invocation: true\n")
            r = health_check.check_structural_skill_frontmatter(root)
            self.assertTrue(r.passed)

    def test_no_skills_dir_not_applicable(self):
        with tempfile.TemporaryDirectory() as t:
            r = health_check.check_structural_skill_frontmatter(Path(t))
            self.assertTrue(r.passed)

    def test_multiple_offenders_listed(self):
        with tempfile.TemporaryDirectory() as t:
            root = Path(t)
            _make_skill(root, "aget-create-project", "disable-model-invocation: true\n")
            _make_skill(root, "aget-file-issue", "disable-model-invocation: true\n")
            r = health_check.check_structural_skill_frontmatter(root)
            self.assertFalse(r.passed)
            self.assertIn("aget-create-project", r.message)
            self.assertIn("aget-file-issue", r.message)


if __name__ == "__main__":
    unittest.main()
