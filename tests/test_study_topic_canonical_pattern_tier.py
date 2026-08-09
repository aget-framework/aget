"""Canonical pattern tier reachability — both polarities.

Guards the 2026-08-08 fix to `find_patterns()`. Asserts BOTH directions, because
the defect this closes was invisible to a one-directional test: `find_patterns()`
returned results the whole time, so "patterns are found" passed while every
FRAMEWORK pattern was unreachable.

Polarity 1 — the tier is reached when a canonical checkout is adjacent.
Polarity 2 — the declared surface reads UNAVAILABLE when it is not.

A fix that hardcodes the tier as always-present passes 1 and fails 2; that is
manufactured coverage, which is the mirror defect and equally a regression.
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent / 'scripts'))

import study_topic  # noqa: E402


class TestCanonicalPatternTier(unittest.TestCase):

    def test_canonical_pattern_roots_resolve_when_checkout_is_adjacent(self):
        """Polarity 1: an adjacent canonical checkout yields a pattern root."""
        agent_root = study_topic.get_agent_root()
        spec_roots = study_topic.find_canonical_spec_roots(agent_root)
        if not spec_roots:
            self.skipTest('no adjacent canonical checkout on this host')
        roots = study_topic.find_canonical_pattern_roots(agent_root)
        self.assertTrue(roots, 'canonical spec tier resolved but pattern tier did not')
        for root in roots:
            self.assertTrue(root.is_dir())
            self.assertEqual(root.name, 'patterns')

    def test_pattern_roots_are_derived_from_the_spec_resolver_not_a_second_probe(self):
        """A parallel layout guess would drift from the resolver that carries the lesson."""
        agent_root = study_topic.get_agent_root()
        spec_roots = study_topic.find_canonical_spec_roots(agent_root)
        pattern_roots = study_topic.find_canonical_pattern_roots(agent_root)
        # Every pattern root must be the docs/patterns sibling of a resolved spec root.
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
            isolated = Path('/nonexistent-parent-xyz/agent-root')
            study_topic.refresh_canonical_pattern_surface(isolated)
            entry = next(v for v in study_topic.SURFACES_SEARCHED
                         if v.startswith('canonical framework pattern'))
            self.assertIn('UNAVAILABLE', entry)
        finally:
            study_topic.SURFACES_SEARCHED[:] = saved

    def test_declared_surface_is_derived_from_what_resolves(self):
        """The reported surface must name the resolved root, not a literal."""
        saved = list(study_topic.SURFACES_SEARCHED)
        try:
            agent_root = study_topic.get_agent_root()
            roots = study_topic.find_canonical_pattern_roots(agent_root)
            study_topic.refresh_canonical_pattern_surface(agent_root)
            entry = next(v for v in study_topic.SURFACES_SEARCHED
                         if v.startswith('canonical framework pattern'))
            if roots:
                self.assertIn(str(roots[0]), entry)
                self.assertNotIn('UNAVAILABLE', entry)
            else:
                self.assertIn('UNAVAILABLE', entry)
        finally:
            study_topic.SURFACES_SEARCHED[:] = saved

    def test_the_exhibit_is_reachable_by_its_own_title(self):
        """The measured 2026-08-08 case: the pattern was absent from a study for its own name."""
        agent_root = study_topic.get_agent_root()
        if not study_topic.find_canonical_pattern_roots(agent_root):
            self.skipTest('no adjacent canonical checkout on this host')
        results = study_topic.find_patterns('weekly fleet health monitor')
        names = {r['pattern'] for r in results}
        self.assertIn('PATTERN_weekly_fleet_health_monitor', names)

    def test_local_patterns_still_reachable_no_regression(self):
        """Widening to canonical must not displace the instance-local roots."""
        results = study_topic.find_patterns('step back review kb')
        self.assertTrue(results, 'local pattern tier regressed')


if __name__ == '__main__':
    unittest.main()
