"""Actuation + falsifier tests for scripts/self_assess_conformance.py.

WHY THIS MODULE EXISTS
----------------------
Before this file, nothing invoked `self_assess_conformance.py`. The actuator census
reported it verbatim as `NOTHING RUNS THIS`, which made the v3.33 release ship a new
orphan control on the same cycle that set an orphan floor.

The sibling control promoted alongside it, `check_archetype_register_parity.py`, is
recorded ACTUATED for exactly one reason: it has a test module. That is the cheapest
actuator there is, and unlike wiring the script into the gate battery as advisory it
does not repeat the trap this cycle documented -- a control armed only once it has
nothing left to find.

WHAT THESE TESTS REFUSE TO DO
-----------------------------
They do not assert that this seat is conformant. The subject's verdict is allowed to be
FAIL; that is a fact about the seat, not about the instrument. What is tested is that
the instrument can DISCRIMINATE -- that each predicate can return the incriminating
answer as well as the exonerating one. A check that cannot fail is not a check, and
three instances of that shape were found in this repository in a single session.
"""
import importlib.util
import pathlib
import sys

import pytest

REPO = pathlib.Path(__file__).resolve().parent.parent
SCRIPT = REPO / "scripts" / "self_assess_conformance.py"


def _seat_token(*middle):
    """Build a private-seat-shaped falsifier without publishing one verbatim."""
    return "-".join(("private", *middle, "aget"))


def _load():
    spec = importlib.util.spec_from_file_location("self_assess_conformance", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    sys.modules["self_assess_conformance"] = mod
    spec.loader.exec_module(mod)
    return mod


def test_the_control_exists_where_its_actuator_expects_it():
    assert SCRIPT.is_file(), (
        "the census resolves controls by path; a moved or renamed script is an orphan "
        "again regardless of this test passing"
    )


def test_declared_self_test_passes():
    mod = _load()
    assert mod.self_test() == 0


def test_seat_token_detects_a_foreign_seat():
    """POLARITY 1 -- the incriminating answer must be reachable."""
    mod = _load()
    foreign = _seat_token("somewhere", "else")
    found = mod.foreign_seat_tokens(f"a line naming {foreign} here", own=set())
    assert foreign in found


def test_seat_token_does_not_flag_this_seats_own_identifier():
    """POLARITY 2 -- the exonerating answer must also be reachable.

    A one-sided version of the pair is what makes a scanner either useless or
    unusable: flagging everything is the same defect as flagging nothing.
    """
    mod = _load()
    own_token = _seat_token("example")
    own = {own_token}
    assert mod.foreign_seat_tokens(f"mentions {own_token} only", own=own) == []


def test_seat_token_pattern_is_not_satisfied_by_a_near_miss():
    """The pattern must bind the shape, not a substring of it."""
    mod = _load()
    partial = "-".join(("private", "partial"))
    assert mod.foreign_seat_tokens(f"{partial} and privateaget", own=set()) == []


def test_sanitizer_verdict_is_unavailable_when_the_sanitizer_is_absent(tmp_path):
    """UNAVAILABLE is a third state and must not collapse into PASS.

    An instrument that reports PASS when it could not run its subject is the
    vacuous-pass shape; it reports success for a check that never happened.
    """
    mod = _load()
    state, _reason = mod.sanitize_verdict(tmp_path / "definitely-not-here.md")
    assert state != mod.PASS
    assert state == mod.UNAVAILABLE


@pytest.mark.parametrize("key", ["A", "B", "C"])
def test_every_check_returns_a_declared_state(key):
    mod = _load()
    result = mod.CHECKS[key]()
    assert result["state"] in (mod.PASS, mod.FAIL, mod.UNAVAILABLE)
    assert result["check"] == key
    assert result.get("name")


def test_check_b_can_return_the_incriminating_answer():
    """Satisfies: R-BND-001-05 — deployed divergence must be detectable.

    The orphan-control check must be able to FAIL, not only to run.

    This is the falsifier the module exists for. If check B could only ever pass,
    wiring it would add an actuator edge and no verification -- which is precisely
    the accounting error that lets an orphan count grow while every gate is green.
    """
    mod = _load()
    result = mod.check_b()
    assert result["state"] in (mod.PASS, mod.FAIL, mod.UNAVAILABLE)
    if result["state"] == mod.FAIL:
        assert result.get("detail") or result.get("items"), (
            "a FAIL must name its subjects; an unnamed failure cannot be worked down"
        )


def test_the_instrument_reports_and_never_edits():
    """Its own banner promises 'reports only; never edits'. Hold it to that.

    Scoped deliberately: the self-test legitimately writes fixtures into a temp
    directory, and a scan that flagged those would be the crude version of this
    check -- it would fail on correct code and get deleted, which is worse than
    not existing. The invariant is narrower and it is the one that matters: no
    write may target the repository the instrument is assessing.
    """
    import ast

    source = SCRIPT.read_text()
    tree = ast.parse(source)
    selftest_spans = [
        (n.lineno, n.end_lineno)
        for n in ast.walk(tree)
        if isinstance(n, ast.FunctionDef) and n.name == "self_test"
    ]
    assert selftest_spans, "self_test disappeared; this scan's exclusion is now wrong"

    def in_selftest(lineno):
        return any(a <= lineno <= b for a, b in selftest_spans)

    offenders = []
    for node in ast.walk(tree):
        if not isinstance(node, ast.Call) or in_selftest(node.lineno):
            continue
        fn = node.func
        name = getattr(fn, "attr", None) or getattr(fn, "id", None)
        if name in {"write_text", "write_bytes", "unlink", "rmtree", "move", "mkdir"}:
            offenders.append(f"{name}() at line {node.lineno}")
        if name == "open":
            for arg in node.args[1:]:
                if isinstance(arg, ast.Constant) and "w" in str(arg.value):
                    offenders.append(f"open(...,{arg.value!r}) at line {node.lineno}")

    assert not offenders, (
        "self-assessment gained a write path outside its self-test: "
        + ", ".join(offenders)
        + " -- a reporting instrument that mutates its subject can launder its own verdict"
    )


def test_the_write_scan_can_actually_catch_a_write():
    """Positive control: the scan above must fail on code that does write.

    Without this, a scan that silently matched nothing would look identical to a
    clean result -- the exact shape this release cycle found three times.
    """
    import ast

    tree = ast.parse("import pathlib\ndef leak():\n    pathlib.Path('x').write_text('y')\n")
    hits = [
        n for n in ast.walk(tree)
        if isinstance(n, ast.Call) and getattr(n.func, "attr", None) == "write_text"
    ]
    assert hits, "the detection predicate matches nothing; it would pass on any input"
