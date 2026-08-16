"""A zero denominator must not read as a pass.

The shipped suite for validate_changelogs asserted `len(REPOS) == 14` and nothing
else -- it never called check_changelog() or main(). So the defect below was 100%
uncovered and shipped:

    Results: 0 OK, 0 missing
    PASS: All 0 repos have CHANGELOG entry for v3.31.0.
    exit 0

Repos that cannot be resolved were SKIPped and dropped from both the numerator and
the denominator, leaving the success branch reachable having opened no file at all.
A consumer who cloned this repo alone, or into a differently-named parent, received
a green light from a check that inspected nothing.

This is the zero-denominator family that check_deprecation_removals' own docstring
already forbids -- "an unparseable row must not read as a clean one". The rule was
written down in the file next door and not applied here, which is why the test
matters more than the fix: the fix is four lines, the missing coverage is why it
survived.

Both polarities are asserted. A test that only proves the failure path would let a
blanket "always fail" regression through, which is the opposite defect.
"""

from __future__ import annotations

import contextlib
import importlib.util
import io
import pathlib
import sys

import pytest

MODULE = pathlib.Path(__file__).resolve().parent.parent / "scripts" / "validate_changelogs.py"


def _load():
    """Fresh module each time — REPOS is module-level state the tests mutate."""
    spec = importlib.util.spec_from_file_location("validate_changelogs", MODULE)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _run(repos, version="3.30.0"):
    mod = _load()
    if repos is not None:
        mod.REPOS = repos
    argv = sys.argv
    sys.argv = ["validate_changelogs.py", "--version", version]
    buf = io.StringIO()
    try:
        with contextlib.redirect_stdout(buf):
            try:
                rc = mod.main()
            except SystemExit as exc:
                rc = exc.code
    finally:
        sys.argv = argv
    return rc, buf.getvalue()


def test_zero_readable_repos_is_a_failure_not_a_pass():
    """The regression itself: nothing inspected must not exit 0."""
    rc, out = _run([f"nonexistent-repo-{i}" for i in range(14)])
    assert rc != 0, (
        "a check that resolved zero repositories reported success; "
        "it has not passed, it has not run"
    )
    assert "PASS" not in out.split("FAIL")[0], "the word PASS must not precede the failure"


def test_partial_coverage_is_a_failure():
    """Unread repos are unknown, not clean.

    The exit-code assertion runs everywhere: partial coverage must never exit 0,
    and that holds whether one repo resolves or none do.

    The coverage-string assertion needs one repo to actually resolve, so it is
    guarded the same way as the two tests below. At the producing seat the sibling
    `aget/` is on disk and '1 of 14' is real; from a consumer's clone there are no
    siblings, nothing resolves, and asserting '1 of 14' fails on the environment
    rather than on the behaviour.

    Found 2026-08-15 by re-running the consumer rehearsal against the re-cut tag:
    passed at the producing seat, failed from a clean --no-local clone. Fourth
    instance in this release of the class its own notes disclose -- a promoted test
    that passes where it was written and fails where it lands -- and this one guards
    the release's headline fix, so it would have been the first thing a consumer saw
    break.
    """
    mod = _load()
    root = pathlib.Path(mod.__file__).resolve().parent.parent.parent
    rc, out = _run(["aget"] + [f"nonexistent-repo-{i}" for i in range(13)])
    assert rc != 0, "partial coverage reported success"
    if not (root / "aget").is_dir():
        pytest.skip("no sibling repo resolves in this checkout; the exit-code half above still ran")
    assert "1 of 14" in out or "1/14" in out, "the failure must state the actual coverage"


def test_full_coverage_still_passes():
    """Opposite polarity: the fix must not degrade into an unconditional refusal.

    Skips rather than fails where the sibling repos are not checked out, because a
    consumer legitimately may not have them — and that condition is exactly what the
    other two tests already cover.
    """
    mod = _load()
    root = pathlib.Path(mod.__file__).resolve().parent.parent.parent
    if not all((root / r).is_dir() for r in mod.REPOS):
        pytest.skip("sibling repos not present in this checkout; covered by the other cases")
    rc, out = _run(None)
    assert rc == 0, f"full coverage should pass, got exit {rc}:\n{out}"
    assert f"{len(mod.REPOS)}/{len(mod.REPOS)}" in out, "a pass must state its denominator"


def test_pass_message_always_carries_its_denominator():
    """A count without its denominator is the defect one layer up."""
    mod = _load()
    root = pathlib.Path(mod.__file__).resolve().parent.parent.parent
    if not all((root / r).is_dir() for r in mod.REPOS):
        pytest.skip("sibling repos not present in this checkout")
    _, out = _run(None)
    assert "All 0 repos" not in out, "the original defect's exact string must never reappear"
