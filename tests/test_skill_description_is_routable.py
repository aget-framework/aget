"""Every shipped skill must present a routable description to the model.

THE DEFECT THIS CLOSES (measured 2026-08-10).

Three canonical skills shipped with no YAML frontmatter at all — `aget-ask`,
`aget-promote-issue`, `aget-propose-goals`. Each carried a perfectly good
one-line description in its body, under the H1, which never reached the router.
With no `description:` field the catalog falls back to the skill's own name, so
the model saw:

    aget-ask:            aget-ask
    aget-promote-issue:  /aget-promote-issue
    aget-propose-goals:  /aget-propose-goals

against siblings that read like sentences. A skill the model cannot tell apart
from its own name is a skill the model cannot choose on purpose. The files were
present, valid, and documented; only the routing was dead — which is why no
existing check caught it, and why it survived long enough to be found by a
downstream instance auditing its *inherited* copies rather than by the producer.

WHY PRESENCE ALONE IS NOT THE PREDICATE. A presence-only guard passes on
`description: aget-ask` — frontmatter exists, the field exists, and the router is
exactly as blind as before. The defect's observable symptom was
description-equals-name, so that is what this asserts against. Checking for the
container instead of the property is how the class stays open.

SCOPE, relative to the neighbour. `test_health_check_structural_frontmatter.py`
asserts a different invariant over a different population: the four D71-STRUCTURAL
skills must not carry `disable-model-invocation: true`. It iterates four skills
and inspects one flag. This file iterates every shipped skill and inspects the
routing contract. Neither subsumes the other.
"""

import pathlib

import pytest
import yaml

REPO = pathlib.Path(__file__).resolve().parents[1]
SKILLS = REPO / ".claude" / "skills"


def shipped_skills():
    return sorted(d for d in SKILLS.iterdir() if (d / "SKILL.md").is_file())


def frontmatter(text):
    """Return (mapping, error). Absent and INVALID are different defects.

    Distinguished because their consequences differ. Absent frontmatter means no
    description exists for any consumer. Invalid YAML means one exists and some
    loaders accept it while strict parsers get nothing — Claude Code's catalog
    tolerated an unquoted `: ` inside a plain scalar that `yaml.safe_load`
    rejects outright, so the skill routed correctly in one client and vanished
    from `validate_agent_skill_package.py`. Reporting both as "no frontmatter"
    sends the second one to the wrong repair.
    """
    if not text.startswith("---"):
        return None, "no YAML frontmatter"
    parts = text.split("---", 2)
    if len(parts) < 3:
        return None, "frontmatter delimiter is unterminated"
    try:
        loaded = yaml.safe_load(parts[1])
    except yaml.YAMLError as exc:
        detail = str(exc).splitlines()[0]
        return None, f"frontmatter is not valid YAML ({detail})"
    if not isinstance(loaded, dict):
        return None, "frontmatter is not a mapping"
    return loaded, None


def routing_errors(name, text):
    """Return the reasons this skill cannot be selected by description."""
    meta, error = frontmatter(text)
    if meta is None:
        return [error]
    errors = []
    if not str(meta.get("name") or "").strip():
        errors.append("frontmatter has no name")
    description = str(meta.get("description") or "").strip()
    if not description:
        errors.append("frontmatter has no description")
        return errors
    # The degenerate forms the missing-frontmatter fallback produced verbatim.
    degenerate = {name.lower(), f"/{name}".lower()}
    if description.lower().rstrip(".") in degenerate:
        errors.append(f"description is degenerate (equals the skill name): {description!r}")
    return errors


def test_every_shipped_skill_presents_a_routable_description():
    skills = shipped_skills()
    assert skills, "no skills found — predicate reached nothing"
    offenders = {}
    for skill in skills:
        errors = routing_errors(skill.name, (skill / "SKILL.md").read_text(errors="replace"))
        if errors:
            offenders[skill.name] = errors
    assert not offenders, offenders


def test_absent_frontmatter_is_detected():
    """The exact shape the three canonical skills shipped in."""
    assert routing_errors("aget-ask", "# aget-ask\n\nAsk clarifying questions.\n") == [
        "no YAML frontmatter"
    ]


def test_invalid_yaml_is_reported_as_invalid_not_absent():
    """The fourth offender, and a different repair.

    `aget-create-goal` carried a description containing an unquoted `: ` inside a
    plain scalar. Claude Code's loader accepted it and the description reached
    the catalog; `yaml.safe_load` rejected the whole block. Reported as "absent"
    it would be repaired by adding frontmatter that already exists.
    """
    text = (
        "---\nname: aget-create-goal\n"
        "description: Two-tier (REQ-3): committed goals go in GOALS.md\n"
        "---\n\n# /aget-create-goal\n"
    )
    errors = routing_errors("aget-create-goal", text)
    assert len(errors) == 1
    assert errors[0].startswith("frontmatter is not valid YAML")
    assert "no YAML frontmatter" not in errors[0]


@pytest.mark.parametrize("description", ["aget-ask", "/aget-ask", "Aget-Ask."])
def test_name_as_description_is_detected(description):
    """Presence is not the property — a name-shaped description routes no better."""
    text = f"---\nname: aget-ask\ndescription: {description}\n---\n\n# aget-ask\n"
    errors = routing_errors("aget-ask", text)
    assert any("degenerate" in error for error in errors), errors


def test_a_real_description_passes():
    """The other polarity, so the guard cannot pass by rejecting everything."""
    text = (
        "---\nname: aget-ask\n"
        "description: Ask clarifying questions as an entropy-reduction instrument "
        "for next-action prediction.\n---\n\n# aget-ask\n"
    )
    assert routing_errors("aget-ask", text) == []
