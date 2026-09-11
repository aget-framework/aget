"""C-34-01 / gh#2445 — shipped skills must carry a parseable, non-empty description.

Both polarities, plus the exact YAML shape that shipped broken in all 13 registered
templates: an unquoted scalar whose text contains ': '.
"""
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
VALIDATOR = REPO / "verification" / "validate_archetype_skills.py"
sys.path.insert(0, str(REPO / "verification"))
import validate_archetype_skills as V  # noqa: E402

VALID = '---\nname: s\ndescription: "A meaningful description."\n---\n\n# body\n'


def _tree(tmp_path, skills):
    """A minimal <root>/<repo>/.claude/skills/<skill>/SKILL.md layout."""
    for name, text in skills.items():
        d = tmp_path / "template-x-aget" / ".claude" / "skills" / name
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(text)
    return tmp_path


# -------------------------------------------------------------------- positive
def test_valid_frontmatter_yields_no_defect(tmp_path):
    assert V.skill_description_defects(_tree(tmp_path, {"ok": VALID})) == []


def test_quoted_description_containing_colon_space_is_valid(tmp_path):
    """The repair shape: quoting makes a punctuated description parseable."""
    text = '---\nname: s\ndescription: "Two-tier (REQ-3): committed goals = a section."\n---\n\n# b\n'
    assert V.skill_description_defects(_tree(tmp_path, {"ok": text})) == []


# -------------------------------------------------------------------- negative
def test_absent_frontmatter_is_rejected(tmp_path):
    d = V.skill_description_defects(_tree(tmp_path, {"bad": "# aget-ask\n\nProse only.\n"}))
    assert [x["defect"] for x in d] == ["frontmatter-absent"]


def test_unquoted_colon_space_description_is_rejected(tmp_path):
    """THE SHIPPED DEFECT: aget-create-goal in all 13 templates."""
    text = ("---\nname: s\ndescription: Commit a goal. Two-tier (REQ-3): committed goals = "
            "a structured section in governance/GOALS.md.\n---\n\n# b\n")
    d = V.skill_description_defects(_tree(tmp_path, {"bad": text}))
    assert d and d[0]["defect"] == "frontmatter-unparseable"


def test_empty_description_is_rejected(tmp_path):
    d = V.skill_description_defects(_tree(tmp_path, {"bad": '---\nname: s\ndescription: ""\n---\n\n# b\n'}))
    assert [x["defect"] for x in d] == ["description-empty-or-absent"]


def test_missing_description_key_is_rejected(tmp_path):
    d = V.skill_description_defects(_tree(tmp_path, {"bad": "---\nname: s\n---\n\n# b\n"}))
    assert [x["defect"] for x in d] == ["description-empty-or-absent"]


def test_unterminated_frontmatter_is_rejected(tmp_path):
    d = V.skill_description_defects(_tree(tmp_path, {"bad": "---\nname: s\ndescription: x\n"}))
    assert d and d[0]["defect"] == "frontmatter-unterminated"


# ------------------------------------------------------------- scaffold-time gate
def test_cli_exits_1_on_defect_and_0_when_clean(tmp_path):
    """The scaffold-time negative test: a defective tree must FAIL the gate."""
    bad = _tree(tmp_path / "bad", {"b": "# no frontmatter\n"})
    r = subprocess.run([sys.executable, str(VALIDATOR), "--descriptions", "--root", str(bad)],
                       capture_output=True, text=True)
    assert r.returncode == 1, r.stdout + r.stderr

    good = _tree(tmp_path / "good", {"g": VALID})
    r = subprocess.run([sys.executable, str(VALIDATOR), "--descriptions", "--root", str(good)],
                       capture_output=True, text=True)
    assert r.returncode == 0, r.stdout + r.stderr


def test_json_output_carries_the_defect_count(tmp_path):
    import json
    bad = _tree(tmp_path, {"b": "# no frontmatter\n"})
    r = subprocess.run([sys.executable, str(VALIDATOR), "--descriptions", "--root", str(bad), "--json"],
                       capture_output=True, text=True)
    assert json.loads(r.stdout)["defect_count"] == 1
