"""Canonical pattern tier reachability — both polarities, in every environment.

Guards the 2026-08-08 fix to `find_patterns()`. Asserts BOTH directions, because
the defect this closes was invisible to a one-directional test: `find_patterns()`
returned results the whole time, so "patterns are found" passed while every
FRAMEWORK pattern was unreachable.

Polarity 1 — the tier is reached when a canonical checkout is adjacent.
Polarity 2 — the declared surface reads UNAVAILABLE when it is not.

A fix that hardcodes the tier as always-present passes 1 and fails 2; that is
manufactured coverage, which is the mirror defect and equally a regression.

WHY EVERY TEST HERE SYNTHESISES ITS OWN TOPOLOGY (2026-08-10).

This file previously resolved both polarities from the *ambient host*: two tests
bailed out with an environment-conditional skip ("no adjacent canonical checkout
on this host") and one asserted `find_patterns('step back review kb')` against
whatever the running seat happened to contain. That is a property of the checkout
layout, not of this repository, and it cost a fleet migration a gate:

  * `test_local_patterns_still_reachable_no_regression` FAILED in standalone
    `aof-AGET` CI (run 31362991908, py3.11) with `AssertionError: [] is not true`
    — the seat has no local pattern tree, so the literal query matched nothing.
    That seat's v3.30 migration was reverted and the representative cohort
    falsified. Measured the same day: a substantial majority of instances fail
    this shape in an isolated checkout, and some of those failures have a
    *populated* `docs/patterns/` whose content simply does not match the query —
    so "has a patterns dir" was never the predicate.
  * The two environment-conditional guards were green everywhere and therefore
    proved nothing anywhere: each environment exercised only ONE polarity, so a
    regression in the branch a given host does not take stays invisible in CI.
    `test_study_topic_specs_tier.py` reached this same conclusion first and
    records it in its own docstring; this file is the sibling that had not yet
    absorbed it.

So: no test here reads the ambient agent root, and no test skips. Each builds the
topology it needs — mounted or unmounted — and patches `get_agent_root()` to it,
which makes both polarities run on a developer workstation and on a bare runner
alike. The pattern this file guards must be reachable by a query; that pattern is
therefore created by the fixture, not assumed of the host.
"""

import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

import study_topic  # noqa: E402

LOCAL_PATTERN = 'PATTERN_step_back_review_kb'
LOCAL_TOPIC = 'step back review kb'
CANONICAL_PATTERN = 'PATTERN_weekly_fleet_health_monitor'
CANONICAL_TOPIC = 'weekly fleet health monitor'


class SyntheticSeat:
    """Build an instance root, optionally beside a canonical framework checkout.

    The resolver's contract is the marker file `specs/AGET_SESSION_SPEC.md` in a
    SIBLING of the agent root — not a directory name and not a depth. The mounted
    fixture reproduces exactly that, so this test stays honest if the resolver's
    accepted layouts change: it would start failing rather than silently skipping.
    """

    def __init__(self, canonical_mounted: bool):
        self.canonical_mounted = canonical_mounted
        self._ctx = None
        self.root = None
        self.canonical_patterns = None

    def __enter__(self):
        self._ctx = tempfile.TemporaryDirectory()
        self._tmp = Path(self._ctx.name)
        self.root = self._tmp / 'instance'
        local = self.root / 'docs' / 'patterns'
        local.mkdir(parents=True)
        (local / f'{LOCAL_PATTERN}.md').write_text(
            f'# {LOCAL_TOPIC}\n\nStep back and review the KB before proposing.\n'
        )
        # A minimal instance corpus so the surrounding pipeline has a tree to walk.
        (self.root / '.aget' / 'evolution').mkdir(parents=True)
        (self.root / '.aget' / 'evolution' / 'L001_seed.md').write_text('# L001\nseed\n')
        if self.canonical_mounted:
            framework = self._tmp / 'framework-checkout'
            specs = framework / 'specs'
            specs.mkdir(parents=True)
            # The marker file IS the resolver's contract.
            (specs / 'AGET_SESSION_SPEC.md').write_text('session spec')
            self.canonical_patterns = framework / 'docs' / 'patterns'
            self.canonical_patterns.mkdir(parents=True)
            (self.canonical_patterns / f'{CANONICAL_PATTERN}.md').write_text(
                f'# {CANONICAL_TOPIC}\n\nWeekly fleet health monitor pattern.\n'
            )
        return self

    def __exit__(self, *exc):
        self._ctx.cleanup()
        return False


def mounted():
    return SyntheticSeat(canonical_mounted=True)


def unmounted():
    return SyntheticSeat(canonical_mounted=False)


class TestCanonicalPatternTier(unittest.TestCase):

    def test_canonical_pattern_roots_resolve_when_checkout_is_adjacent(self):
        """Polarity 1: an adjacent canonical checkout yields a pattern root."""
        with mounted() as seat:
            with patch.object(study_topic, 'get_agent_root', return_value=seat.root):
                spec_roots = study_topic.find_canonical_spec_roots(seat.root)
                self.assertTrue(spec_roots, 'synthetic marker did not resolve a spec root')
                roots = study_topic.find_canonical_pattern_roots(seat.root)
                self.assertTrue(roots, 'canonical spec tier resolved but pattern tier did not')
                for root in roots:
                    self.assertTrue(root.is_dir())
                    self.assertEqual(root.name, 'patterns')

    def test_canonical_pattern_roots_are_empty_without_an_adjacent_checkout(self):
        """Polarity 1's falsifier: absent the marker, the tier must resolve to nothing."""
        with unmounted() as seat:
            with patch.object(study_topic, 'get_agent_root', return_value=seat.root):
                self.assertEqual(study_topic.find_canonical_spec_roots(seat.root), [])
                self.assertEqual(study_topic.find_canonical_pattern_roots(seat.root), [])

    def test_pattern_roots_are_derived_from_the_spec_resolver_not_a_second_probe(self):
        """A parallel layout guess would drift from the resolver that carries the lesson."""
        with mounted() as seat:
            with patch.object(study_topic, 'get_agent_root', return_value=seat.root):
                spec_roots = study_topic.find_canonical_spec_roots(seat.root)
                pattern_roots = study_topic.find_canonical_pattern_roots(seat.root)
                self.assertTrue(pattern_roots)
                expected = {sr.parent / 'docs' / 'patterns' for sr in spec_roots}
                for root in pattern_roots:
                    self.assertIn(root, expected)

    def test_unreachable_tier_reports_UNAVAILABLE_not_a_coverage_claim(self):
        """Polarity 2: no adjacent checkout => the banner must NOT claim the surface.

        This is the half that fails if someone 'fixes' reachability by asserting
        the path unconditionally.
        """
        saved = list(study_topic.SURFACES_SEARCHED)
        try:
            with unmounted() as seat:
                with patch.object(study_topic, 'get_agent_root', return_value=seat.root):
                    study_topic.refresh_canonical_pattern_surface(seat.root)
                    entry = next(v for v in study_topic.SURFACES_SEARCHED
                                 if v.startswith('canonical framework pattern'))
                    self.assertIn('UNAVAILABLE', entry)
        finally:
            study_topic.SURFACES_SEARCHED[:] = saved

    def test_declared_surface_is_derived_from_what_resolves(self):
        """The reported surface must name the resolved root, not a literal.

        Both polarities run here, in every environment — which is the property the
        ambient-host form could not provide.
        """
        saved = list(study_topic.SURFACES_SEARCHED)
        try:
            with mounted() as seat:
                with patch.object(study_topic, 'get_agent_root', return_value=seat.root):
                    roots = study_topic.find_canonical_pattern_roots(seat.root)
                    self.assertTrue(roots)
                    study_topic.refresh_canonical_pattern_surface(seat.root)
                    entry = next(v for v in study_topic.SURFACES_SEARCHED
                                 if v.startswith('canonical framework pattern'))
                    self.assertIn(str(roots[0]), entry)
                    self.assertNotIn('UNAVAILABLE', entry)
            study_topic.SURFACES_SEARCHED[:] = list(saved)
            with unmounted() as seat:
                with patch.object(study_topic, 'get_agent_root', return_value=seat.root):
                    study_topic.refresh_canonical_pattern_surface(seat.root)
                    entry = next(v for v in study_topic.SURFACES_SEARCHED
                                 if v.startswith('canonical framework pattern'))
                    self.assertIn('UNAVAILABLE', entry)
        finally:
            study_topic.SURFACES_SEARCHED[:] = saved

    def test_the_exhibit_is_reachable_by_its_own_title(self):
        """The measured 2026-08-08 case: the pattern was absent from a study for its own name."""
        with mounted() as seat:
            with patch.object(study_topic, 'get_agent_root', return_value=seat.root):
                results = study_topic.find_patterns(CANONICAL_TOPIC)
                names = {r['pattern'] for r in results}
                self.assertIn(CANONICAL_PATTERN, names)

    def test_local_patterns_still_reachable_no_regression(self):
        """Widening to canonical must not displace the instance-local roots.

        Synthetic, not ambient: the local pattern this asserts is created by the
        fixture. The ambient form of this assertion failed in aof-AGET CI run
        31362991908 and reverted that seat's v3.30 migration.
        """
        with mounted() as seat:
            with patch.object(study_topic, 'get_agent_root', return_value=seat.root):
                results = study_topic.find_patterns(LOCAL_TOPIC)
                names = {r['pattern'] for r in results}
                self.assertIn(LOCAL_PATTERN, names)

    def test_local_patterns_reachable_with_no_canonical_checkout(self):
        """The instance-local tier must not depend on the canonical tier resolving."""
        with unmounted() as seat:
            with patch.object(study_topic, 'get_agent_root', return_value=seat.root):
                results = study_topic.find_patterns(LOCAL_TOPIC)
                names = {r['pattern'] for r in results}
                self.assertIn(LOCAL_PATTERN, names)


if __name__ == '__main__':
    unittest.main()
