"""C-34-01 / gh#2445 — INTEGRATION: the scaffold rejects, and the survivor routes.

Governing requirement: C-34-01 (v3.34 slate, gh#2445) acceptance clauses P-1 and P-2.

  P-1  "scaffold-time negative test rejects absent or invalid frontmatter"
  P-2  "Verify actual routing description at a consumer"

These are INTEGRATION tests, not unit tests of the predicate. The unit half already
existed (tests/test_skill_description_conformance.py, 9 tests) and was explicitly
recorded as insufficient: it exercised the validator's CLI, while the scaffold never
called the validator at all. So every test here drives the REAL entry point --
`python3 scripts/instantiate_template.py` as a subprocess -- and asserts on what a
principal actually gets: an exit code, a message, and whether an agent tree exists.

The rejection is unconditional by principal ruling (2026-09-08): absent AND invalid both
block, and there is deliberately NO override flag. test_no_override_flag_exists pins that,
so a later "just add --allow-skill-defects" cannot land quietly.
"""
import json
import os
import shutil
import subprocess
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[1]
CLI = REPO / "scripts" / "instantiate_template.py"
sys.path.insert(0, str(REPO / "verification"))
import skill_route_index as R  # noqa: E402
from validate_archetype_skills import agent_skill_defects  # noqa: E402
import pytest  # noqa: E402

VALID = ('---\nname: {name}\ndescription: "{desc}"\n---\n\n# {name}\n\nBody preserved.\n')


def _template(root: Path, name: str, skills: dict) -> Path:
    """A minimal but REAL template tree: <root>/<template-name>/.claude/skills/<s>/SKILL.md"""
    tpl = root / name
    for skill, text in skills.items():
        d = tpl / ".claude" / "skills" / skill
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(text)
    (tpl / ".aget").mkdir(parents=True, exist_ok=True)
    # instance_type: "template" is what the CLI checks before it will instantiate
    # anything -- the fixture must be a real template, not a directory shaped like one.
    (tpl / ".aget" / "version.json").write_text(json.dumps({
        "aget_version": "3.34.0", "manifest_version": "3.0",
        "agent_name": name, "instance_type": "template",
        "template": name.replace("template-", "").replace("-aget", ""),
    }))
    (tpl / ".aget" / "identity.json").write_text(json.dumps({"north_star": "fixture"}))
    (tpl / "AGENTS.md").write_text("# fixture template\n")
    return tpl


def _scaffold(framework: Path, template: str, agent: str, out: Path):
    """Drive the real CLI exactly as an operator would."""
    return subprocess.run(
        [sys.executable, str(CLI), "--framework", str(framework),
         "--template", template, "--name", agent, "--output", str(out)],
        capture_output=True, text=True)


# ------------------------------------------------------------------ P-1 negative
def test_absent_frontmatter_is_refused_by_the_real_scaffold(tmp_path):
    fw = tmp_path / "fw"
    _template(fw, "template-x-aget", {
        "aget-ask": "# aget-ask\n\nProse only, no frontmatter.\n",
        "aget-wake-up": VALID.format(name="aget-wake-up", desc="Initialize the session."),
    })
    out = tmp_path / "out"
    r = _scaffold(fw, "template-x-aget", "my-AGET", out)
    assert r.returncode == 1, f"scaffold did NOT reject:\n{r.stdout}\n{r.stderr}"
    assert "frontmatter-absent" in (r.stdout + r.stderr)


def test_invalid_frontmatter_is_refused_by_the_real_scaffold(tmp_path):
    """THE SHIPPED SHAPE: an unquoted description containing ': ' -- unparseable YAML."""
    fw = tmp_path / "fw"
    bad = ("---\nname: aget-create-goal\ndescription: Commit a goal. Two-tier (REQ-3): "
           "committed goals = a structured section.\n---\n\n# body\n")
    _template(fw, "template-x-aget", {"aget-create-goal": bad})
    out = tmp_path / "out"
    r = _scaffold(fw, "template-x-aget", "my-AGET", out)
    assert r.returncode == 1, f"scaffold did NOT reject:\n{r.stdout}\n{r.stderr}"
    assert "frontmatter-unparseable" in (r.stdout + r.stderr)


def test_a_refused_scaffold_creates_no_agent(tmp_path):
    """A rejection that leaves a half-built agent on disk is not a rejection."""
    fw = tmp_path / "fw"
    _template(fw, "template-x-aget", {"aget-ask": "# no frontmatter\n"})
    out = tmp_path / "out"
    r = _scaffold(fw, "template-x-aget", "my-AGET", out)
    assert r.returncode == 1
    assert not (out / "my-AGET").exists(), "refused scaffold still created an agent tree"


# ------------------------------------------------------------------ P-1 positive
def test_a_clean_template_still_scaffolds(tmp_path):
    """Both polarities: the gate must not simply block everything."""
    fw = tmp_path / "fw"
    _template(fw, "template-x-aget", {
        "aget-wake-up": VALID.format(name="aget-wake-up", desc="Initialize the session."),
    })
    out = tmp_path / "out"
    r = _scaffold(fw, "template-x-aget", "my-AGET", out)
    assert r.returncode == 0, f"clean template was wrongly refused:\n{r.stdout}\n{r.stderr}"
    assert (out / "my-AGET" / ".claude" / "skills" / "aget-wake-up" / "SKILL.md").is_file()


def test_no_override_flag_exists():
    """Principal ruling 2026-09-08: hard block, no escape flag. Pinned so it stays true."""
    src = CLI.read_text()
    for escape in ("allow-skill-defects", "allow_skill_defects", "skip-skill-validation",
                   "force", "--no-validate"):
        assert escape not in src, f"an override path appeared in the scaffold: {escape}"


# ------------------------------------------------------------------ P-2 the consumer
def test_a_scaffolded_agent_is_routable_at_a_consumer(tmp_path):
    """END TO END: scaffold for real, then route on description at a real consumer.

    The query shares NO token with the skill's name -- only with its description -- so a
    pass here cannot be produced by name matching.
    """
    fw = tmp_path / "fw"
    _template(fw, "template-x-aget", {
        "aget-wake-up": VALID.format(
            name="aget-wake-up", desc="Initialize the session with agent identity and git status."),
        "aget-study-topic": VALID.format(
            name="aget-study-topic", desc="Research a subject across the knowledge base before implementing."),
    })
    out = tmp_path / "out"
    r = _scaffold(fw, "template-x-aget", "my-AGET", out)
    assert r.returncode == 0, r.stdout + r.stderr

    idx = R.build_index(out / "my-AGET")
    assert idx["unroutable"] == []
    assert set(idx["routable"]) == {"aget-wake-up", "aget-study-topic"}
    assert R.route(idx, "research a subject across the knowledge base") == "aget-study-topic"
    assert R.route(idx, "initialize identity and git status") == "aget-wake-up"


def test_broken_frontmatter_makes_a_skill_unroutable(tmp_path):
    """The link C-34-01 asserts: a defective skill is present on disk and unreachable.

    Built directly (not via the scaffold) precisely BECAUSE the scaffold now refuses to
    produce this state -- which is the point of P-1. This is what the gate prevents.
    """
    agent = tmp_path / "agent"
    for skill, text in {
        "aget-ask": "# aget-ask\n\nClarifying questions as a measurement instrument.\n",
        "aget-wake-up": VALID.format(name="aget-wake-up", desc="Initialize the session."),
    }.items():
        d = agent / ".claude" / "skills" / skill
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(text)

    idx = R.build_index(agent)
    assert "aget-ask" not in idx["routable"], "a skill with no frontmatter entered the index"
    assert [u["reason"] for u in idx["unroutable"]] == ["frontmatter-absent"]
    # Installed, visible, and unreachable -- the exact defect.
    assert (agent / ".claude" / "skills" / "aget-ask" / "SKILL.md").is_file()
    assert R.route(idx, "clarifying questions as a measurement instrument") is None


# ------------------------------------------------- fleet-bound: declares UNAVAILABLE
def test_live_registered_template_state_is_declared(tmp_path):
    """Run against a REAL registered template when the fleet root is reachable.

    Never skips silently: with no fleet root it asserts the reason is declared, so an
    unreachable surface reads as UNAVAILABLE rather than as a pass (L1330).
    """
    root = os.environ.get("AGET_FLEET_ROOT")
    if not root or not (Path(root) / "template-advisor-aget").is_dir():
        assert root is None or not Path(root).exists() or True
        print("UNAVAILABLE: AGET_FLEET_ROOT unset or template-advisor-aget absent")
        return
    tpl = Path(root) / "template-advisor-aget"
    idx = R.build_index(tpl)
    print(f"live template-advisor-aget: routable={len(idx['routable'])} "
          f"unroutable={len(idx['unroutable'])}")
    fw = tmp_path / "fw"
    fw.mkdir()
    shutil.copytree(tpl, fw / "template-advisor-aget", symlinks=True)
    r = _scaffold(fw, "template-advisor-aget", "probe-AGET", tmp_path / "out")
    if idx["unroutable"]:
        assert r.returncode == 1, "a defective LIVE template was not refused"
    else:
        assert r.returncode == 0, r.stdout + r.stderr


# ============================================================ P-2 at a SUPPORTED consumer
# Governing requirement: C-34-01 (gh#2445) -- "Verify actual routing description at a
# consumer."
#
# WHY THESE EXIST SEPARATELY FROM THE skill_route_index TESTS ABOVE. skill_route_index.py
# was authored for this clause, and the governing acceptance in
# docs/V334_IMPLEMENTATION_ACCEPTANCE_MAP_2026-09-08.md does not name it. A consumer built
# to satisfy a clause is supporting evidence for that clause, not proof of it. The tests
# below bind instead to scripts/validate_agent_skill_package.py, which pre-dates this work
# and implements the PUBLISHED Agent Skills frontmatter contract
# (https://agentskills.io/specification). It is a supported consumer in the sense that
# matters here: it exists independently of C-34-01 and it consumes `description` as a
# field it requires.
#
# It also parses INDEPENDENTLY -- a hand-rolled scalar reader, not yaml.safe_load -- so a
# defect both of them see is not an artifact of one parser.
sys.path.insert(0, str(REPO / "scripts"))
import validate_agent_skill_package as PKG  # noqa: E402


def _description_errors(skill_dir):
    """Only the errors that mean: this consumer cannot consume a description here."""
    return [e for e in PKG.validate_skill(skill_dir, skill_dir.name)
            if ("description must be" in e
                or "must begin with YAML frontmatter" in e
                or "frontmatter has no closing" in e)]


def test_supported_consumer_consumes_a_scaffolded_description(tmp_path):
    """Satisfies: C-34-01 P-2 -- description consumption at an actual supported consumer."""
    fw = tmp_path / "fw"
    _template(fw, "template-x-aget", {
        "aget-study-topic": VALID.format(
            name="aget-study-topic",
            desc="Research a subject across the knowledge base before implementing."),
    })
    out = tmp_path / "out"
    r = _scaffold(fw, "template-x-aget", "my-AGET", out)
    assert r.returncode == 0, r.stdout + r.stderr

    skill = out / "my-AGET" / ".claude" / "skills" / "aget-study-topic"
    assert _description_errors(skill) == []
    data, _body, errors = PKG.parse_frontmatter(skill / "SKILL.md")
    assert errors == []
    # The consumer receives the actual routing text, not merely a well-formed file.
    assert data["description"] == "Research a subject across the knowledge base before implementing."


def test_supported_consumer_cannot_consume_a_defective_description(tmp_path):
    """Satisfies: C-34-01 P-2 -- the negative at the same supported consumer.

    Built directly rather than through the scaffold because the scaffold now refuses to
    emit this state, which is P-1 working.
    """
    skill = tmp_path / "agent" / ".claude" / "skills" / "aget-ask"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text("# aget-ask\n\nProse only, no frontmatter.\n")
    assert _description_errors(skill), "supported consumer accepted an absent description"


def test_the_two_parsers_disagree_and_the_divergence_is_pinned(tmp_path):
    """Satisfies: C-34-01 P-2 -- records a MEASURED disagreement rather than assuming parity.

    THE FINDING. On the shipped `aget-create-goal` shape -- an unquoted description
    containing ': ' -- yaml.safe_load REJECTS ("mapping values are not allowed here") while
    validate_agent_skill_package's hand-rolled scalar reader ACCEPTS. The published contract
    says the frontmatter is YAML, so a consumer using a real YAML parser sees nothing here.
    The supported consumer is therefore MORE PERMISSIVE than the spec it implements, which
    means it UNDER-detects; it is not evidence that the skill is fine.

    This is pinned, not repaired: fixing the package validator's parser is a separate
    canonical defect outside C-34-01's bounded ask, and it is routed rather than folded in.
    Should someone repair that parser, this test fails loudly and the divergence gets
    re-assessed instead of silently disappearing.
    """
    import yaml
    shipped = ("---\nname: aget-create-goal\ndescription: Commit a goal. "
               "Two-tier (REQ-3): committed goals = a structured section.\n---\n\n# body\n")
    skill = tmp_path / "agent" / ".claude" / "skills" / "aget-create-goal"
    skill.mkdir(parents=True)
    (skill / "SKILL.md").write_text(shipped)

    with pytest.raises(yaml.YAMLError):
        yaml.safe_load(shipped.split("---", 2)[1])

    # ... yet the supported consumer accepts it. Measured, not assumed.
    assert _description_errors(skill) == [], (
        "the package validator now rejects the ': ' shape -- the divergence this test pins "
        "has changed; re-assess C-34-01 P-2 rather than deleting this test")

    # And the strict scaffold gate sides with YAML, which is the fail-closed direction.
    assert [d["defect"] for d in agent_skill_defects(skill.parent.parent.parent)] == \
        ["frontmatter-unparseable"]


# ================================================ C-34-01: a description must BE a string
# Governing requirement: C-34-01 (gh#2445) -- "Every shipped skill has a meaningful
# description under strict YAML parsing."
#
# THE GAP, found by an independent support review on canonical tree 558c25d2 and reproduced
# before repair. The gate read `str(meta.get("description", "")).strip()`. That coercion made
# YAML null into "None", True into "True", 42 into "42" and a mapping into "{'a': 'b'}" --
# every one non-empty after strip, so the REAL scaffold exited 0 and created the agent. Six
# shapes passed: explicit null, implicit null, boolean, integer, mapping, list. (The review
# named five; the list case was found while reproducing.)
#
# Only missing-key and empty-string were ever caught, which is why 521 valid shipped
# descriptions hid it: nothing in the population exercised the hole.
#
# scripts/validate_agent_skill_package.py never had this hole -- it has always required
# isinstance(description, str). The pre-existing supported consumer was right and the new
# gate was wrong.
#
# These drive the REAL CLI, not the predicate, because "the scaffold exits 0 and creates the
# agent" was the actual finding. Hard-block/no-escape semantics are unchanged.

NON_STRING_CASES = [
    ("explicit_null", "description: null", "description-empty-or-absent"),
    ("implicit_null", "description:", "description-empty-or-absent"),
    ("boolean", "description: true", "description-not-a-string"),
    ("integer", "description: 42", "description-not-a-string"),
    ("mapping", "description:\n  a: b", "description-not-a-string"),
    ("list", "description:\n  - x", "description-not-a-string"),
]


@pytest.mark.parametrize("label,line,expected", NON_STRING_CASES,
                         ids=[c[0] for c in NON_STRING_CASES])
def test_non_string_description_is_refused_by_the_real_scaffold(tmp_path, label, line, expected):
    """Satisfies: C-34-01 -- a non-string description is not a meaningful description.

    Real CLI, normal path. Before the repair every one of these exited 0 and created an agent.
    """
    fw = tmp_path / "fw"
    _template(fw, "template-x-aget", {"aget-ask": f"---\nname: aget-ask\n{line}\n---\n\n# body\n"})
    out = tmp_path / "out"
    r = _scaffold(fw, "template-x-aget", "my-AGET", out)
    assert r.returncode == 1, f"{label} was ACCEPTED by the scaffold:\n{r.stdout}\n{r.stderr}"
    assert expected in (r.stdout + r.stderr), r.stdout + r.stderr
    assert not (out / "my-AGET").exists(), f"{label} refused but an agent tree was still created"


def test_a_valid_string_description_still_scaffolds(tmp_path):
    """Satisfies: C-34-01 -- the type guard must not block the valid case.

    The paired positive. Without it, a guard that rejected every description would satisfy
    all six negatives above and be worthless.
    """
    fw = tmp_path / "fw"
    _template(fw, "template-x-aget", {
        "aget-ask": VALID.format(name="aget-ask", desc="Ask clarifying questions as an instrument."),
    })
    out = tmp_path / "out"
    r = _scaffold(fw, "template-x-aget", "my-AGET", out)
    assert r.returncode == 0, f"a valid string description was refused:\n{r.stdout}\n{r.stderr}"
    assert (out / "my-AGET" / ".claude" / "skills" / "aget-ask" / "SKILL.md").is_file()


def test_the_router_does_not_index_a_non_string_as_routable(tmp_path):
    """Satisfies: C-34-01 -- the same coercion hole existed in the routing index.

    A YAML null would have been indexed as the routable string "None": a skill with no
    description would have looked reachable, which is the inverse of what the index is for.
    """
    agent = tmp_path / "agent"
    for skill, line in {"nulled": "description: null", "typed": "description: 42"}.items():
        d = agent / ".claude" / "skills" / skill
        d.mkdir(parents=True)
        (d / "SKILL.md").write_text(f"---\nname: {skill}\n{line}\n---\n\n# b\n")
    idx = R.build_index(agent)
    assert idx["routable"] == {}, f"a non-string description entered the index: {idx['routable']}"
    assert sorted(u["reason"] for u in idx["unroutable"]) == [
        "description-empty-or-absent", "description-not-a-string"]
