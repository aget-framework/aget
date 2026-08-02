"""Tests for gh#2063 remedy 1 — the omission list must bound itself.

`study_topic.py` prints a prominent NOT-searched banner. That banner is the artifact's
own honesty mechanism, and it enumerated omissions *inside the repo* while presenting
itself as the complete statement of what the study could not see. A reader — including
the agent that ran it — treats a visibly-caveated artifact as having declared all its
limits. An artifact with no caveat would have drawn the question sooner.

Two classes sat outside the repo and therefore outside the list entirely: the work repo
this agent contributes to, and the web / external prior art. Demonstrated cost (gh#2063):
two duplicate derivations one day apart, the second re-deriving a worse version of a
conclusion settled the previous day.

The falsifier that matters is the UNCONDITIONAL one: an out-of-universe note that only
prints in some runs restores exactly the laundering it exists to remove.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import study_topic as st  # noqa: E402


def _report(**kw):
    return st.generate_report("any topic", {"ldocs": []}, **kw)


def test_out_of_universe_constant_names_both_external_classes():
    """The two classes that are structurally unreachable must be named, not implied.

    Satisfies: R-TEST-001-02
    """
    text = st.SURFACES_OUT_OF_UNIVERSE.lower()
    assert "work repo" in text, "the work repo must be named explicitly"
    assert "web" in text, "the web / external prior art must be named explicitly"
    assert "repo-internal" in text, "the list must declare its own scope"


def test_banner_prints_the_scope_of_its_omission_list():
    """FALSIFIER: a NOT-searched banner with no self-bounding clause is the gh#2063
    defect. The scope line must reach the rendered report.

    Satisfies: R-TEST-001-02
    """
    out = _report()
    assert "**NOT searched (repo-internal)**" in out, (
        "the omission list must label itself repo-internal at the point of use"
    )
    assert st.SURFACES_OUT_OF_UNIVERSE in out, (
        "the out-of-universe scope note must be printed, not merely defined"
    )


def test_scope_note_is_unconditional_across_every_report_variant():
    """The load-bearing falsifier. A caveat that appears only sometimes is worse than
    none, because its absence in a given run reads as 'nothing further omitted'.

    Satisfies: R-TEST-001-02
    """
    import inspect

    sig = inspect.signature(st.generate_report)
    # Exercise every boolean/optional knob generate_report exposes, in both states.
    toggles = [n for n, p in sig.parameters.items()
               if isinstance(p.default, bool)]
    variants = [{}]
    for name in toggles:
        variants.append({name: True})
        variants.append({name: False})

    for kw in variants:
        out = _report(**kw)
        assert st.SURFACES_OUT_OF_UNIVERSE in out, (
            f"scope note absent for variant {kw} — a conditional caveat re-opens gh#2063"
        )


def test_deliberate_and_unconfigured_omissions_stay_distinguishable():
    """Pre-existing behaviour, pinned here because gh#2063 reported it as missing and it
    is not: the two exclusion classes carry different wording, and collapsing them would
    make a scope ruling indistinguishable from an unmade decision.

    Satisfies: R-TEST-001-02
    """
    joined = " ; ".join(st.SURFACES_EXCLUDED)
    assert "deliberate" in joined, "a ruled exclusion must say so, with its date"
    assert "unconfigured" in joined, "an unmade decision must not read as a ruling"
    assert "--include-sessions" in joined, (
        "a deliberately-excluded surface that IS reachable must name its escape hatch"
    )
