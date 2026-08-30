#!/usr/bin/env python3
"""
Study Topic Protocol - Focused Topic Research

Search KB for topic-related artifacts and report findings.
Use before diving into implementation to understand existing patterns.

Renamed from study_up.py in v3.12.0 (L762: Script-Skill Name Alignment Debt).
Aligns script name with skill name: /aget-study-topic (SNR2, #480).

Implements: CAP-SESSION-007 (Study Topic)
- R-SESSION-007-01: Accept topic argument
- R-SESSION-007-02: Search KB for topic
- R-SESSION-007-03: Report related artifacts
- R-SESSION-007-04: JSON output mode
- R-SESSION-007-05: Verify mode
- R-SESSION-007-06: Epistemic purpose parameter (CAP-SESSION-007-06)
- R-SESSION-007-07: Domain relevance weighting (CAP-SESSION-007-07)

See: aget/specs/AGET_SESSION_SPEC.md (CAP-SESSION-007)
Index: aget/specs/SESSION_SKILLS_INDEX.yaml
Tests: tests/test_session_protocol.py::TestStudyTopicProtocol
Related: L187 (Silent execution), L335 (Memory Architecture), L761, L762

Usage:
    python3 study_topic.py --topic "wind down"       # Research wind down
    python3 study_topic.py --topic "release" --json  # JSON output
    python3 study_topic.py --verify                  # Migration verification

Exit codes:
    0 — study completed (including a zero-result study; an empty result is a
        finding, not an error — see the surfaces banner for what was reachable)
    1 — invalid invocation (no --topic and no --verify), or --verify failed
"""

import argparse
import importlib.util
import json
import os
import re
import sys
import urllib.parse
from datetime import datetime
from pathlib import Path


def get_agent_root():
    """Get the agent root directory."""
    if os.environ.get('AGET_STUDY_ROOT'):
        return Path(os.environ['AGET_STUDY_ROOT']).resolve()
    current = Path(__file__).resolve()
    return current.parent.parent


def load_study_topic_config():
    """Load study_topic config from .aget/config.json.

    Returns config dict or empty dict if not configured.
    Three-tier degradation (ADR-004):
      Tier 1: Full config with priority_areas + domain_keywords
      Tier 2: Partial config (domain_keywords only)
      Tier 3: No config — default behavior (backward-compatible)

    Implements: CAP-SESSION-007-06 (config fallback), CAP-SESSION-007-07 (domain config)
    """
    config_path = get_agent_root() / '.aget' / 'config.json'
    if not config_path.exists():
        return {}
    try:
        config = json.loads(config_path.read_text())
        return config.get('study_topic', {})
    except (json.JSONDecodeError, OSError):
        return {}


def resolve_purpose(explicit_purpose, config):
    """Resolve epistemic purpose from flag or config default.

    Priority: explicit --purpose flag > config default_purpose > 'exploration'

    Implements: CAP-SESSION-007-06 (purpose resolution)
    """
    if explicit_purpose:
        return explicit_purpose
    return config.get('default_purpose', 'exploration')


def get_purpose_globs(purpose, config):
    """Get file glob patterns for a purpose from config.

    Returns list of glob patterns that should be boosted for this purpose.

    Implements: CAP-SESSION-007-06 (priority_areas)
    """
    priority_areas = config.get('priority_areas', {})
    if purpose in priority_areas:
        return priority_areas[purpose]
    defaults = {
        'pre-implementation': ['planning/**', 'specs/**', '*/specs/**', 'docs/patterns/**'],
        'pre-release': ['planning/PROJECT_PLAN*', 'sops/SOP_release*', 'release-notes/**',
                        'handoffs/RELEASE*', 'specs/*RELEASE*', '*/specs/*RELEASE*'],
        'audit': ['governance/**', 'tests/**', 'scripts/**', '.claude/hooks/**', '.codex/hooks/**'],
        'exploration': ['knowledge/**', 'ontology/**', '.aget/evolution/**'],
    }
    return defaults.get(purpose, [])


def compute_purpose_boost(file_path_str, purpose_globs):
    """Compute purpose boost for a file based on glob matching.

    Returns 2.0 if file matches any purpose glob, 1.0 otherwise.

    Implements: CAP-SESSION-007-06 (purpose weighting)
    """
    if not purpose_globs:
        return 1.0
    from fnmatch import fnmatch
    for glob_pattern in purpose_globs:
        if fnmatch(file_path_str, glob_pattern) or fnmatch(file_path_str, '*/' + glob_pattern):
            return 2.0
    return 1.0


def compute_domain_boost(content, domain_keywords):
    """Compute domain relevance boost based on keyword presence.

    Returns 1.0 + 0.25 per matching keyword (max 2.0).

    Implements: CAP-SESSION-007-07 (domain relevance weighting)
    """
    if not domain_keywords:
        return 1.0
    matches = sum(1 for kw in domain_keywords if kw.lower() in content.lower())
    return min(2.0, 1.0 + matches * 0.25)


# ---------------------------------------------------------------------------
# Search contract (v3.26 C-26-11 — gh#1852 audit enactment; gh#1850/#1757/#1560)
#
# The contract is DECLARED, not implied: the report prints which surfaces are
# searched and which are excluded (with provenance), so absence-from-results
# is interpretable (audit Finding S1/C1).
# ---------------------------------------------------------------------------

# Tokens that must never act as keywords (audit M1: "and" matched every file
# and its occurrence counts dominated ranking in all four seats' failures).
STOPWORDS = {'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
             'in', 'is', 'it', 'of', 'on', 'or', 's', 'the', 'this', 'to',
             'with',
             # gh#1876: common function words that passed hygiene and diluted
             # OR-union results at multiple seats (2026-07-11, e.g. "after").
             'after', 'all', 'any', 'before', 'but', 'can', 'do', 'does',
             'has', 'have', 'how', 'if', 'into', 'its', 'not', 'our', 'over',
             'so', 'some', 'than', 'that', 'their', 'then', 'there', 'these',
             'they', 'under', 'up', 'was', 'we', 'were', 'what', 'when',
             'where', 'which', 'who', 'why', 'will', 'you'}

SHORT_TOKEN_LEN = 5      # tokens ≤ this use word-boundary matching (audit M4)
FILENAME_BOOST = 3.0     # name/title match is the strongest feature (audit R2, #1757)
RELEVANCE_FLOOR_DEFAULT = 2.0  # composite-score floor (audit R3, #1560); --no-floor escapes

SURFACES_SEARCHED = [
    '.aget/evolution/**/L*.md (RECURSIVE — includes discoveries/; 2026-07-25 fix)',
    'docs/patterns/**/*.md AND patterns/**/*.md (both roots INSTANCE-LOCAL, any filename '
    '— 2026-07-25 fix; "both roots" read as complete coverage until 2026-08-08)',
    'canonical framework pattern tier (resolved from a local sibling checkout; '
    'reported as unavailable when absent)',
    'planning/PROJECT_PLAN*.md',
    'planning/initiatives/INIT-*.md + PROPOSAL_init_*.md (2026-08-14 fix — see below)',
    'sops/SOP_*.md', 'governance/*.md',
    'knowledge/** + ontology/** (v3.25 C-25-14)',
    'specs/** + .aget/specs/** (gh#1580 — instance-local spec tier)',
    'canonical framework spec tier (resolved from a local sibling checkout; '
    'reported as unavailable when absent)',
    'inbox/ ≤14d (v3.26 C-26-11 — S2 revisit ruling: NOTIFYs are study-relevant, gh#1850)',
]
SURFACES_EXCLUDED = [
    'sessions/, workspace/, data/ (deliberate — 2026-07-04 scope decision, noise at study-time; '
    'sessions/ is reachable on request via --include-sessions)',
    'docs/ outside patterns/, handoffs/, release-notes/, .claude/skills/ '
    '(unconfigured — candidates for a future scope ruling)',
]
# 2026-08-14: planning/initiatives/ moved from EXCLUDED to SEARCHED.
#
# Why. A study of "AGET's support for connectors and MCP" ran this script and got 13
# artifacts across 5 surfaces. The single most load-bearing artifact in the whole answer
# — planning/initiatives/INIT-CROSS-CLI-PORTABILITY.md, which carries CAP-CCP-017, the
# normative requirement governing the exact question asked — was NOT among them. It was
# found by a hand-rolled grep afterwards, and the script had faithfully printed it under
# "NOT searched". The banner was accurate and the study was still wrong.
#
# This is the surface where ACTIVE capability contracts live. PROJECT_PLANs are vehicles;
# initiatives are the scope-and-requirement layer above them (AGET_INITIATIVE_SPEC), and
# a CAP-/V- requirement lands in an initiative manifest, not in a plan. Excluding it made
# the script structurally unable to surface the governing requirement for any topic whose
# scope is owned by an initiative — the precise failure mode /aget-study-topic exists to
# prevent (L467 layer 3: "searchable index").
#
# Bounded like the other additions: manifests and their proposals only (INIT-*.md,
# PROPOSAL_init_*.md), not the whole planning/ tree — planning/artifacts/ is receipt
# spew and would reproduce the sessions/ noise problem the 2026-07-04 ruling avoided.
#
# Guarded: tests/test_session_protocol.py::TestStudyTopicProtocol
#   ::test_study_topic_searches_initiatives_surface asserts BOTH polarities — the surface
#   is reachable, AND planning/artifacts/ is still excluded. See L1388.
SURFACES_OUT_OF_UNIVERSE = (
    'this list is REPO-INTERNAL ONLY. Two classes lie outside it and are never searched: '
    'the WORK REPO this agent contributes to, and the WEB / external prior art. '
    'A topic settled in either is invisible here and will be re-derived — pair this study '
    'with an explicit search of both before concluding a gap exists'
)


# Keywords whose corpus document-frequency is too low to GATE a match. They are
# still searched, still contribute match counts, and still rank — they simply do not
# enter the majority-coverage denominator. Populated once by
# compute_nongating_keywords() in main(). Module-level because the denominator is
# applied per-file inside search_file_for_topic() and threading a parameter through
# every finder would touch every call site for no behavioural gain.
_NONGATING_KEYWORDS = set()

# A keyword is non-gating when its document frequency is at or below
# max(_GATING_DF_MIN, _GATING_DF_RATIO * corpus_size). Overridable via
# .aget/config.json -> study_topic.gating_df_ratio.
_GATING_DF_RATIO = 0.005
_GATING_DF_MIN = 3

# Roots probed for document-frequency. Mirrors SURFACES_SEARCHED; deliberately a
# separate cheap list because the DF probe only needs "does this token occur at all",
# not per-surface attribution.
_DF_PROBE_ROOTS = ('.aget/evolution', '.aget/specs', 'docs', 'planning', 'sops',
                   'governance', 'knowledge', 'ontology', 'specs', 'patterns', 'inbox')
_DF_PROBE_EXTS = ('.md', '.yaml', '.yml')


def compute_nongating_keywords(topic: str, root: Path = None,
                               ratio: float = None) -> tuple:
    """Return (non_gating_keywords, df_map, corpus_size) for the topic (ST-010).

    Why this exists (gh#1876 / RQ-378 "IDF-vs-floor"): STOPWORDS is a fixed
    function-word list with no corpus-rarity term. A token that is not a function
    word but is vanishingly rare ("8hrs" df=1, "esp" df=11 of 2900 docs) survives
    hygiene and then inflates the denominator of the >=50% majority-coverage filter
    in search_file_for_topic(), SUPPRESSING genuinely relevant artifacts. Measured
    2026-08-14: the same topic returned 55 artifacts with two such tokens appended
    and 715 without — a 13x collapse, in the direction that reads to a human as
    "novel topic, no precedent".

    That polarity is the dangerous one and is NOT what gh#2211 records (there the
    distinguishing token is STRIPPED, yielding falsely HIGH coverage). Both are
    hygiene defects; they fail in opposite directions, and a fix for one can cause
    the other.

    Which is why these keywords are made NON-GATING rather than dropped. Dropping a
    rare token would break the narrow-lookup case that gh#2211 is about: a specific
    identifier ("L1013") is legitimately rare AND is the whole point of the query.
    Removing it from the denominator only ever RELAXES the filter (min_required
    falls), so recall cannot decrease; the token still searches, still contributes
    match_count, and still earns FILENAME_BOOST. Precision is held by the relevance
    floor and composite ranking, not by the denominator.

    Cost: one extra read pass over _DF_PROBE_ROOTS. Bounded by corpus size.
    """
    keywords = prepare_keywords(topic, apply_df_filter=False)
    if len(keywords) < 2:
        return set(), {}, 0              # denominator is 1; nothing to distort
    root = root or get_agent_root()
    ratio = _GATING_DF_RATIO if ratio is None else ratio
    patterns = {kw: _token_pattern(kw) for kw in keywords}
    df = {kw: 0 for kw in keywords}
    corpus = 0
    for rel in _DF_PROBE_ROOTS:
        base = root / rel
        if not base.exists():
            continue
        for path in base.rglob('*'):
            if not path.is_file() or path.suffix.lower() not in _DF_PROBE_EXTS:
                continue
            try:
                text = path.read_text(encoding='utf-8', errors='ignore')
            except (OSError, UnicodeDecodeError):
                continue
            corpus += 1
            for kw, pat in patterns.items():
                if re.search(pat, text, re.IGNORECASE):
                    df[kw] += 1
    if not corpus:
        return set(), df, 0
    threshold = max(_GATING_DF_MIN, ratio * corpus)
    non_gating = {kw for kw, count in df.items() if count <= threshold}
    # Never make every keyword non-gating: if the whole topic is rare, the topic IS
    # the rare thing and the ordinary majority rule should apply to it.
    if len(non_gating) == len(keywords):
        return set(), df, corpus
    return non_gating, df, corpus


_URLISH = re.compile(r'^(?:[a-z][a-z0-9+.\-]*://|www\.)', re.I)

# Web mechanics only. Deliberately NOT domain vocabulary: a path segment like
# "WhatLinksHere" is part of what the caller asked about, and rarity is handled at the
# majority-coverage denominator (compute_nongating_keywords), not by discarding tokens.
_URL_NOISE = {
    'http', 'https', 'ftp', 'www', 'com', 'org', 'net', 'io', 'edu', 'gov', 'co',
    'html', 'htm', 'php', 'aspx', 'jsp', 'index', 'api', 'cgi', 'bin',
}


def _decompose_url(token: str) -> list:
    """Split a URL-shaped token into its meaningful path/query segments.

    Why this exists (2026-08-28): keyword hygiene tokenized on whitespace alone, and a
    URL contains none. The entire URL therefore survived as ONE keyword, matched
    nothing, and the report announced "0 artifacts found ... This appears to be a novel
    topic". That is a false absence generated by the instrument -- the worst kind,
    because the output is a confident negative rather than an error.

    Observed: /aget-study-topic on a wiki URL returned 0; the same subject typed as
    words returned 74 artifacts across 8 surfaces.
    """
    decoded = urllib.parse.unquote(token)
    out = []
    # Underscore is a SEPARATOR here, not a word character: wiki and doc URLs encode
    # spaces as "_", so \w-based splitting leaves "Concept_Page_Creation_Task" as one
    # unmatchable token -- the same false-absence one level down.
    for part in re.split(r'[^A-Za-z0-9]+', decoded):
        if not part or part.isdigit() or part.lower() in _URL_NOISE:
            continue
        out.append(part)
    return out


def prepare_keywords(topic: str, apply_df_filter: bool = True) -> list:
    """Token hygiene (audit M1-M3): tokenize, drop punctuation-only tokens and
    stopwords, dedupe case-insensitively (order-preserving), fold trailing
    possessive ("supervisor's" -> "supervisor"). Light folds only — not a stemmer.
    Falls back to raw tokens when hygiene would empty the list (all-stopword topic).

    gh#1876 (2026-07-11): edge punctuation is stripped BEFORE stopword/boundary
    handling — a trailing comma ("health,") previously survived into the token
    and broke word-boundary matching silently. Internal punctuation survives
    ("v3.26" is untouched; only token edges are stripped).

    ST-010 (2026-08-14): the returned list is UNCHANGED by document frequency —
    every hygiened keyword is still searched. Rarity is applied at the
    majority-coverage denominator instead (see _NONGATING_KEYWORDS and
    compute_nongating_keywords). apply_df_filter is retained for call-site clarity
    and is a no-op on the returned tokens.
    """
    raw = []
    for kw in topic.split():
        if not re.search(r'\w', kw):
            continue
        # A URL is one whitespace token but many search terms (2026-08-28).
        raw.extend(_decompose_url(kw) if _URLISH.match(kw) else [kw])
    seen, out = set(), []
    for kw in raw:
        kw = kw.strip('.,;:!?"\'`()[]{}<>*_-/\\')  # edges only (gh#1876)
        if not kw:
            continue
        kw = kw[:-2] if kw.lower().endswith("'s") else kw
        key = kw.lower()
        if key in STOPWORDS or key in seen:
            continue
        seen.add(key)
        out.append(kw)
    return out or raw


def _token_pattern(kw: str) -> str:
    """Boundary semantics (audit M4 + M3): short tokens are word-boundary
    anchored with light inflection tolerance (so "check" stops matching
    "checklist" but still matches "checks"/"checked"); longer tokens keep
    substring semantics (so "lesson" still matches "lessons")."""
    if len(kw) <= SHORT_TOKEN_LEN:
        return r'\b' + re.escape(kw) + r'(?:s|es|ed|ing)?\b'
    return re.escape(kw)


def composite_score(item: dict) -> float:
    """Ranking contract (audit R1/R2): log-damped match_count so length x
    token-commonness cannot outrank topical precision, times coverage,
    epistemic boosts, and the filename boost."""
    import math
    count = max(1, item.get('match_count', 1))
    return (item.get('keyword_coverage', 1.0)
            * item.get('purpose_boost', 1.0)
            * item.get('domain_boost', 1.0)
            * item.get('filename_boost', 1.0)
            * (1 + math.log2(count)))


def search_file_for_topic(file_path: Path, topic: str, case_insensitive: bool = True,
                          domain_keywords: list = None) -> dict:
    """Search a file for topic matches.

    Args:
        file_path: Path to search
        topic: Topic string to search for
        case_insensitive: Whether to ignore case
        domain_keywords: Optional list of domain keywords for relevance boosting (CAP-SESSION-007-07)

    Returns:
        Dict with match info or None if no match
    """
    try:
        content = file_path.read_text()
        flags = re.IGNORECASE if case_insensitive else 0

        # Filename-index (instance fix 2026-06-26, canonicalized v3.26 C-26-11):
        # filename tokens (raw stem + slug-normalized) join the searchable text,
        # so a topic equal to an artifact's name surfaces that artifact even
        # when the body never echoes the slug. Recall-half of audit R2/#1757;
        # the rank-half is FILENAME_BOOST below.
        fname_text = file_path.stem + ' ' + re.sub(r'[_\-.]+', ' ', file_path.stem)
        haystack = content + '\n' + fname_text

        # Token hygiene (v3.26 C-26-11): stopwords/dupes dropped, possessive folded
        keywords = prepare_keywords(topic)
        if len(keywords) <= 1:
            single = keywords[0] if keywords else topic
            matches = list(re.finditer(_token_pattern(single), haystack, flags))
        else:
            # Multi-keyword: search each independently, require majority coverage
            keyword_matches = {}
            all_matches = []
            for kw in keywords:
                kw_matches = list(re.finditer(_token_pattern(kw), haystack, flags))
                if kw_matches:
                    keyword_matches[kw] = len(kw_matches)
                    all_matches.extend(kw_matches)
            # Require at least 50% of the GATING keywords present. Vanishingly-rare
            # tokens are excluded from the denominator (ST-010): they are still
            # searched above and still counted in all_matches / coverage numerator,
            # they just cannot raise the bar. Without this, appending two noise
            # tokens to a 4-keyword topic silently moved the requirement from
            # 2-of-4 real tokens to 4-of-6 including two unsatisfiable ones —
            # measured as a 13x coverage collapse on 2026-08-14.
            gating = [kw for kw in keywords if kw not in _NONGATING_KEYWORDS] or keywords
            gating_hits = sum(1 for kw in keyword_matches if kw in gating)
            min_required = max(1, (len(gating) + 1) // 2) if len(gating) >= 2 else 1
            if gating_hits < min(min_required, len(gating)):
                return None
            matches = all_matches

        if not matches:
            return None

        # Extract context lines for first few matches
        lines = content.split('\n')
        contexts = []
        seen_lines = set()
        for match in matches:
            if match.start() >= len(content):
                continue  # filename-derived match; no body context to show
            line_start = content.count('\n', 0, match.start())
            if line_start in seen_lines:
                continue
            seen_lines.add(line_start)
            if line_start < len(lines):
                context_line = lines[line_start].strip()
                if len(context_line) > 100:
                    context_line = context_line[:100] + '...'
                contexts.append({
                    'line': line_start + 1,
                    'context': context_line
                })
            if len(contexts) >= 3:
                break

        # `relative_to` RAISES for any path outside the agent root, and that is
        # very likely why the spec tier was never wired despite being advertised
        # in SURFACES_SEARCHED since gh#1580: the canonical contract tier lives at
        # `../aget/specs/` (AGENTS.md §Canonical Path Resolution), one level ABOVE
        # the agent root, so the first attempt to search it would have crashed the
        # whole run. A helper that cannot express a path outside the repo silently
        # bounds every surface to the repo.
        try:
            rel = str(file_path.relative_to(get_agent_root()))
        except ValueError:
            rel = str(file_path)          # cross-repo (canonical tier) — keep absolute
        result = {
            'file': rel,
            'match_count': len(matches),
            'contexts': contexts
        }
        # Add keyword coverage for multi-word ranking. Denominator is the GATING
        # set, matching the filter above (ST-010) — otherwise a non-gating token
        # that cannot realistically match still depresses every artifact's score
        # and pushes it under the relevance floor, reintroducing the same
        # suppression through the back door.
        if len(keywords) > 1:
            _gating = [kw for kw in keywords if kw not in _NONGATING_KEYWORDS] or keywords
            _hits = sum(1 for kw in keyword_matches if kw in _gating)
            result['keyword_coverage'] = _hits / len(_gating)
        # Add domain boost if keywords provided (CAP-SESSION-007-07)
        if domain_keywords:
            result['domain_boost'] = compute_domain_boost(content, domain_keywords)
        # Filename boost (audit R2, #1757): a token in the file's own name is
        # the strongest single relevance feature in the corpus.
        stem = file_path.stem.lower()
        if any(kw.lower() in stem for kw in keywords):
            result['filename_boost'] = FILENAME_BOOST
        result['score'] = composite_score(result)
        return result
    except (OSError, UnicodeDecodeError):
        return None


def search_directory(path: Path, topic: str, extensions: list = None,
                     purpose_globs: list = None, domain_keywords: list = None) -> list:
    """Search a directory for topic-related files.

    Args:
        path: Directory to search
        topic: Topic to search for
        extensions: File extensions to include (default: .md, .yaml, .json)
        purpose_globs: Glob patterns for purpose-based boosting (CAP-SESSION-007-06)
        domain_keywords: Domain keywords for relevance boosting (CAP-SESSION-007-07)

    Returns:
        List of dicts with file match info, sorted by composite score
    """
    if extensions is None:
        extensions = ['.md', '.yaml', '.json', '.py']

    results = []
    if not path.exists():
        return results

    # Recursive search
    for file in path.rglob('*'):
        if file.is_file() and file.suffix in extensions:
            match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
            if match:
                # Add purpose boost (CAP-SESSION-007-06)
                if purpose_globs:
                    match['purpose_boost'] = compute_purpose_boost(match['file'], purpose_globs)
                results.append(match)

    # Composite ranking (v3.26 C-26-11): recompute score once purpose_boost is
    # attached; log-damped count per the ranking contract (audit R1).
    for x in results:
        x['score'] = composite_score(x)
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def find_ldocs(topic: str, domain_keywords: list = None) -> list:
    """Find L-docs related to topic.

    Args:
        topic: Topic to search for
        domain_keywords: Optional domain keywords for boosting (CAP-SESSION-007-07)

    Returns:
        List of matching L-doc info
    """
    agent_root = get_agent_root()
    evolution_path = agent_root / '.aget' / 'evolution'

    results = []
    if not evolution_path.exists():
        return results

    # rglob, not glob: `.aget/evolution/discoveries/` (and any other
    # sub-directory a seat uses) held real, citable KB and was invisible to a
    # non-recursive glob. Field evidence 2026-07-25: a study-topic run reported
    # "no direct pattern/governance hits" for a north-star query while
    # `.aget/evolution/discoveries/north_star_revelation.md` — the origin-story
    # artifact for that exact concept — sat unsearched. The caller then cited it
    # anyway, from a manual read, without noticing the instrument had implicitly
    # denied it existed. A clean zero from a scoped search is not absence.
    # Prefix rule differs by depth, and conflating the two is what caused the
    # original miss AND its first attempted fix. Top level: keep the `L*` filter
    # (that IS the L-doc naming convention). Sub-directories: curated KB with
    # their own conventions — `discoveries/north_star_revelation.md` carries no
    # `L` prefix, so a recursive walk that still demanded one re-excluded the
    # exact artifact the recursion was added to reach.
    for file in sorted(evolution_path.rglob('*.md')):
        if file.parent == evolution_path and not file.name.startswith('L'):
            continue
        match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
        if match:
            # Extract L-doc title from first heading
            try:
                content = file.read_text()
                title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                title = title_match.group(1) if title_match else file.stem
            except Exception:
                title = file.stem

            results.append({
                'ldoc': file.stem,
                'title': title,
                'file': match['file'],
                'match_count': match['match_count'],
                'keyword_coverage': match.get('keyword_coverage', 1.0),
                'domain_boost': match.get('domain_boost', 1.0),
                'score': match.get('score', 0.0)
            })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def find_patterns(topic: str, domain_keywords: list = None) -> list:
    """Find pattern documents related to topic.

    Args:
        topic: Topic to search for
        domain_keywords: Optional domain keywords for boosting

    Returns:
        List of matching pattern info
    """
    agent_root = get_agent_root()

    # TWO pattern roots, and neither filename convention is universal.
    # `docs/patterns/PATTERN_*.md` was the only surface searched until
    # 2026-07-25; seats also keep patterns at a top-level `patterns/` tree with
    # descriptive names (e.g. `patterns/identity/north_star_pattern.md`), which
    # matches neither the directory nor the `PATTERN_*` prefix. Both were
    # therefore reported as "no pattern hits" while the governing pattern
    # document existed. Recurse both roots and drop the prefix requirement.
    # Local roots, then the CANONICAL pattern tier. Both local roots were the
    # 2026-07-25 fix; neither leaves this repo, so every framework pattern was
    # unreachable while the banner read "both roots". See
    # find_canonical_pattern_roots() for the measured cost.
    pattern_roots = [agent_root / 'docs' / 'patterns', agent_root / 'patterns']
    pattern_roots.extend(find_canonical_pattern_roots(agent_root))

    results = []
    seen = set()
    for patterns_path in pattern_roots:
        if not patterns_path.exists():
            continue
        for file in sorted(patterns_path.rglob('*.md')):
            resolved = file.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
            if match:
                results.append({
                    'pattern': file.stem,
                    'file': match['file'],
                    'match_count': match['match_count'],
                    'score': match.get('score', 0.0)
                })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def find_project_plans(topic: str, domain_keywords: list = None) -> list:
    """Find PROJECT_PLANs related to topic.

    Args:
        topic: Topic to search for
        domain_keywords: Optional domain keywords for boosting

    Returns:
        List of matching plan info
    """
    agent_root = get_agent_root()
    planning_path = agent_root / 'planning'

    results = []
    if not planning_path.exists():
        return results

    for file in planning_path.glob('PROJECT_PLAN*.md'):
        match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
        if match:
            # Check if active
            try:
                content = file.read_text()
                # v3.25 C-25-14 (gh#1809 + gh#1791): case-insensitive, Plan_Status-first.
                # Plans write "In Progress" (title case) — the old upper-case-only probe
                # rendered every live plan [inactive]. Prefer the disambiguated
                # Plan_Status header (CAP-PP-003); fall back to legacy header Status,
                # then to whole-content scan for pre-template-2.1 plans.
                m = (re.search(r'\*\*Plan_Status\*\*:\s*([^\n]*)', content)
                     or re.search(r'\*\*Status\*\*:\s*([^\n]*)', content))
                probe = m.group(1) if m else content
                is_active = 'IN PROGRESS' in probe.upper()
            except Exception:
                is_active = False

            results.append({
                'plan': file.name,
                'file': match['file'],
                'match_count': match['match_count'],
                'is_active': is_active,
                'score': match.get('score', 0.0)
            })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def find_initiatives(topic: str, domain_keywords: list = None) -> list:
    """Find initiative manifests and their proposals related to topic.

    Added 2026-08-14 (L1388). planning/initiatives/ is the scope-and-requirement tier:
    CAP-/V- requirements live in INIT-*.md manifests, not in PROJECT_PLANs. Excluding it
    made this script structurally unable to return the governing requirement for any topic
    an initiative owns — measured that day on the connector/MCP study, where CAP-CCP-017
    was the answer and was not returned.

    Scope is deliberately narrow: manifests (INIT-*.md) and their proposals
    (PROPOSAL_init_*.md). planning/artifacts/ stays out — it is receipt/JSON spew and
    would reproduce the noise problem the 2026-07-04 sessions/ ruling avoided.

    Args:
        topic: Topic to search for
        domain_keywords: Optional domain keywords for boosting

    Returns:
        List of matching initiative info, highest score first
    """
    agent_root = get_agent_root()
    results = []

    candidates = []
    initiatives_path = agent_root / 'initiatives'
    if (agent_root / 'planning' / 'initiatives').exists():
        initiatives_path = agent_root / 'planning' / 'initiatives'
        candidates.extend(sorted(initiatives_path.glob('INIT-*.md')))
    proposals_path = agent_root / 'planning' / 'project-proposals'
    if proposals_path.exists():
        candidates.extend(sorted(proposals_path.glob('PROPOSAL_init_*.md')))

    for file in candidates:
        match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
        if not match:
            continue

        # Initiative lifecycle is a declared field, NOT the PROJECT_PLAN vocabulary.
        # AGET_INITIATIVE_SPEC states: NASCENT / ACTIVE / DORMANT / COMPLETE / CLOSED /
        # FOLDED / GRADUATED. Reporting one of these as "[inactive]" (the plan predicate)
        # would mislabel every NASCENT initiative — including the one whose omission
        # motivated this function. Read the field; do not infer it.
        # The value is frequently BOLDED -- "**Status**: **ACTIVE** (rescoped ...)".
        # An earlier version of this line excluded '*' from the capture class, which
        # made a bolded value capture the empty string and report UNDECLARED. Caught
        # 2026-08-14 by running the instrument against source the same session it was
        # written: it reported INIT-FRAMEWORK-COHERENCE and INIT-ALWAYS-ON-HOST as
        # UNDECLARED when both declare **ACTIVE**. Capture to end-of-line, then strip
        # emphasis and any trailing parenthetical rationale.
        status = 'UNDECLARED'
        try:
            content = file.read_text()
            m = re.search(r'\*\*(?:Initiative_)?Status\*\*:\s*([^\n]*)', content)
            if m:
                raw = m.group(1).split('(')[0]
                status = raw.replace('*', '').replace('_', ' ').strip() or 'UNDECLARED'
        except Exception:
            pass

        results.append({
            'initiative': file.name,
            'file': match['file'],
            'match_count': match['match_count'],
            'status': status,
            'score': match.get('score', 0.0),
        })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def find_sops(topic: str, domain_keywords: list = None) -> list:
    """Find SOPs related to topic.

    Args:
        topic: Topic to search for
        domain_keywords: Optional domain keywords for boosting

    Returns:
        List of matching SOP info
    """
    agent_root = get_agent_root()
    sops_path = agent_root / 'sops'

    results = []
    if not sops_path.exists():
        return results

    for file in sops_path.glob('SOP_*.md'):
        match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
        if match:
            results.append({
                'sop': file.name,
                'file': match['file'],
                'match_count': match['match_count'],
                'score': match.get('score', 0.0)
            })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results


KNOWLEDGE_AREAS = ('knowledge', 'ontology')

# The ONE place the knowledge/ontology tier's reach is defined. The banner row
# in SURFACES_SEARCHED is DERIVED from this tuple by
# refresh_knowledge_surface(), so the declaration cannot drift from the glob
# again (L1300: a declared scope must be derived from the executed scope, never
# asserted alongside it). Before gh#2257 the row read 'knowledge/** + ontology/**'
# while the glob read '*.md' -- two globs, same file, disagreeing.
#
# .ttl / .jsonld / .wiki are deliberately EXCLUDED, and that is a scope decision
# rather than an oversight: at this seat they live under
# ontology/publication_staging/ and are SERIALIZATIONS GENERATED FROM the .yaml
# source. Searching them would return the same concept twice from a generated
# mirror -- inflating hit counts and manufacturing duplicate derivations, which
# is the failure gh#2063 names. Source of truth is searched; its exports are not.
KNOWLEDGE_EXTENSIONS = ('*.md', '*.yaml')


def _knowledge_files(base: Path):
    """Every file the knowledge/ontology tier actually opens, in stable order."""
    files = []
    for pattern in KNOWLEDGE_EXTENSIONS:
        files.extend(sorted(base.rglob(pattern)))
    return files


def refresh_knowledge_surface() -> None:
    """Rewrite the knowledge/ontology banner row to state the executed globs.

    L1300 applied to this row: the two canonical rows have been derived since
    2026-08-05, but the remaining rows stayed hand-asserted literals. This is
    the row that fell over (gh#2257). Deriving it means a future edit narrowing
    KNOWLEDGE_EXTENSIONS narrows the printed claim in the same motion.
    """
    exts = ' + '.join(e.lstrip('*') for e in KNOWLEDGE_EXTENSIONS)
    areas = ' + '.join(f'{a}/**' for a in KNOWLEDGE_AREAS)
    surface = (f'{areas} filtered to {exts} (v3.25 C-25-14; extension set '
               f'closed gh#2257 — generated exports .ttl/.jsonld/.wiki excluded)')
    for index, value in enumerate(SURFACES_SEARCHED):
        if value.startswith('knowledge/'):
            SURFACES_SEARCHED[index] = surface
            break


def find_knowledge(topic: str, domain_keywords: list = None) -> list:
    """Find knowledge-base notes related to topic (v3.25 C-25-14, gh#1809).

    Scope decision (framework requirements-level, 2026-07-04): knowledge/ and
    ontology/ join the search surface — they are curated KB areas an agent is
    expected to consult. sessions/, workspace/, and data/ stay OUT: transient
    or bulk surfaces whose hits are noise at study-time (revisit on evidence).

    BOTH EXTENSIONS, and the .yaml half is the one that matters (gh#2257).
    This tier globbed '*.md' only from the day the surface was declared until
    2026-08-15, while SURFACES_SEARCHED advertised 'knowledge/** + ontology/**'.
    Governed vocabulary lives in ONTOLOGY_*.yaml, so the tier never opened the
    file it exists to expose. Measured at this seat pre-fix: 82 yaml files /
    3,678,886 bytes unreachable against 3 md / 53,726 bytes reachable — 1.4% of
    ontology bytes. `FrameworkManagerArchetype`, this agent's OWN archetype
    concept (C610, cited in its own AGENTS.md), occurred 31 times and returned 0.

    Why that is worse than a plain miss: a declared-but-unsearched surface emits
    a zero that reads as evidence of absence, so callers concluded "the
    vocabulary does not contain this" when the truth was "the vocabulary was
    never opened" — false novelty, at review time, with the instrument that
    would have caught it reporting a confident zero. find_specs() below has
    globbed BOTH extensions since gh#1580, which is the argument that this was
    an oversight rather than a scope decision.

    Guarded: tests/test_study_topic_ontology_surface.py (four polarities, and
    the positive ones assert a NON-ZERO count — a fix verified only by "the
    suite still passes" cannot distinguish repaired from unchanged).
    """
    agent_root = get_agent_root()
    results = []
    for area in KNOWLEDGE_AREAS:
        base = agent_root / area
        if not base.exists():
            continue
        for file in _knowledge_files(base):
            match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
            if match:
                results.append({
                    'doc': str(file.relative_to(agent_root)),
                    'file': match['file'],
                    'match_count': match['match_count'],
                    'score': match.get('score', 0.0)
                })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def find_sessions(topic: str, domain_keywords: list = None, days: int = 90) -> list:
    """Find session records related to topic — OPT-IN only (--include-sessions).

    Scope revisit (2026-07-26), on the evidence the 2026-07-04 decision asked for.
    That decision excluded sessions/ as "noise at study-time (revisit on evidence)"
    and the exclusion is CORRECT for the common case: 4,935 session files fleet-wide,
    and a generic topic hits hundreds of them with no research value.

    But the exclusion is total, and that made the skill unable to answer a whole
    QUESTION CLASS — the one where sessions ARE the subject. Field failure, this
    session: the principal asked for an analysis of "language, syntax, structure,
    semantics in session and lessons and project files", and /aget-study-topic
    printed "NOT searched: sessions/" for the largest surface in the request. The
    whole analysis had to be done outside the skill.

    So: opt-in, not default-on. Default behaviour is unchanged (the 2026-07-04
    rationale survives); a caller who says sessions are the subject gets them.

    Bounded two ways, because unbounded is what made them noise in the first place:
      - recency window (default 90 days) — old sessions are superseded by their
        own successors far more often than L-docs are
      - filename date, not mtime — a git checkout rewrites mtime for the whole
        tree, which would put every session "in window" (this exact artifact was
        observed in the parallel 2026-07-26 corpus study)
    """
    import datetime as _dt
    agent_root = get_agent_root()
    base = agent_root / 'sessions'
    if not base.exists():
        return []
    cutoff = (_dt.date.today() - _dt.timedelta(days=days)).isoformat()
    results = []
    for file in base.glob('*.md'):
        m = re.search(r'(\d{4})-(\d{2})-(\d{2})', file.name)
        if m:
            if '-'.join(m.groups()) < cutoff:
                continue
        else:
            # Undated filename: include rather than silently drop. An absence of
            # a date is not evidence of age (L1220 §Absence).
            pass
        match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
        if match:
            results.append({
                'doc': file.stem,
                'file': match['file'],
                'match_count': match['match_count'],
                'score': match.get('score', 0.0)
            })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def find_canonical_spec_roots(agent_root: Path) -> list:
    """Resolve canonical framework specs from any adjacent local checkout.

    Instances are portable across checkout layouts: the framework repository's
    directory NAME is not a contract, and neither is its DEPTH. Two layouts are
    both live in this fleet as of 2026-08-05:

      <parent>/aget/specs/AGET_SESSION_SPEC.md          — canonical repo IS the sibling
      <parent>/<checkout>/aget/specs/AGET_SESSION_SPEC.md — canonical repo CONTAINS aget/

    Presence of the marker file `specs/AGET_SESSION_SPEC.md` is the contract;
    where it sits relative to the sibling is not. Probing only one shape is how
    this function was lost and re-lost: `parent/'aget'` (this seat's prior form)
    resolved at 2 of 32 seats, and `sibling/'aget'/'specs'` (the aof form,
    010b21b) resolves at aof but NOT here — verified 2026-08-05, it returns []
    against an `../aget/specs/AGET_SESSION_SPEC.md` that demonstrably exists.
    A resolver that assumes one layout produces a false surface claim in the
    other, which is the exact defect this whole function exists to prevent.
    """
    roots = []
    parent = agent_root.parent
    if not parent.is_dir():
        return roots
    for sibling in sorted(parent.iterdir()):
        if not sibling.is_dir() or sibling == agent_root:
            continue
        for candidate in (sibling / 'specs', sibling / 'aget' / 'specs'):
            if candidate.is_dir() and (candidate / 'AGET_SESSION_SPEC.md').is_file():
                roots.append(candidate)
    return roots


def find_canonical_pattern_roots(agent_root: Path) -> list:
    """Resolve canonical framework PATTERNS from any adjacent local checkout.

    THE DEFECT THIS CLOSES — and it is the specs-tier defect one directory over.
    `find_patterns()` rooted both of its pattern trees at `agent_root`, so no
    framework pattern was reachable by any study, at any seat, ever. The banner
    said "docs/patterns/** AND patterns/** (both roots)", which a reader
    correctly parses as complete coverage; both roots were agent-local.

    Measured cost, 2026-08-08: three seats in one day published false
    canonical-absence claims downstream of this — "canonical is silent on the
    procedure", "no fleet-review surface exists at any layer", and a recurrence
    vocabulary claim — while `docs/patterns/PATTERN_weekly_fleet_health_monitor.md`
    (v1.0.0, Active, 2026-04-26) sat in canonical the whole time. A study for
    that file's own literal title returned three unrelated local patterns.

    Note the lineage: this function's 2026-07-25 predecessor fixed the SAME
    failure mode — "reported as no pattern hits while the governing pattern
    document existed" — by widening one local root to two local roots. The
    repair stopped at the repo boundary and moved the blind spot instead of
    removing it. Scope the fix to the boundary the claim crosses.

    Reuses find_canonical_spec_roots()'s marker probe rather than adding a
    second layout guess: that resolver already carries the two-layout lesson,
    and a parallel probe would drift from it.
    """
    roots = []
    for spec_root in find_canonical_spec_roots(agent_root):
        candidate = spec_root.parent / 'docs' / 'patterns'
        if candidate.is_dir():
            roots.append(candidate)
    return roots


def refresh_canonical_pattern_surface(agent_root: Path) -> None:
    """Make the reported pattern surface match what this run can actually reach.

    Same contract as refresh_canonical_spec_surface: DERIVE the claim, never
    assert it. An unreachable tier must read UNAVAILABLE, because a banner that
    names a surface it cannot open is what turns a zero into manufactured
    absence.
    """
    roots = find_canonical_pattern_roots(agent_root)
    if roots:
        surface = 'canonical framework patterns: ' + ', '.join(str(root) for root in roots)
    else:
        surface = ('canonical framework pattern tier: UNAVAILABLE '
                   '(no adjacent checkout with aget/specs/AGET_SESSION_SPEC.md)')
    for index, value in enumerate(SURFACES_SEARCHED):
        if value.startswith('canonical framework pattern'):
            SURFACES_SEARCHED[index] = surface
            break


def refresh_canonical_spec_surface(agent_root: Path) -> None:
    """Make the reported search contract match locally resolvable authority.

    The declared surface must be DERIVED from what the run can actually reach,
    never asserted as a literal. `SURFACES_SEARCHED` is printed unconditionally
    by generate_report(); before this function existed, a seat with no adjacent
    canonical checkout printed a coverage claim for a path that could not
    resolve — measured 2026-08-05 at 30 of 32 fleet seats. That is manufactured
    coverage, the mirror of the manufactured absence gh#1580 was filed for.
    """
    roots = find_canonical_spec_roots(agent_root)
    if roots:
        surface = 'canonical framework specs: ' + ', '.join(str(root) for root in roots)
    else:
        surface = ('canonical framework spec tier: UNAVAILABLE '
                   '(no adjacent checkout with aget/specs/AGET_SESSION_SPEC.md)')
    for index, value in enumerate(SURFACES_SEARCHED):
        if value.startswith('canonical framework spec'):
            SURFACES_SEARCHED[index] = surface
            break


def find_specs(topic: str, domain_keywords: list = None) -> list:
    """Find specifications related to topic — the spec tier (gh#1580).

    THE DEFECT THIS CLOSES, stated precisely because it is subtle:
    `SURFACES_SEARCHED` has advertised "specs/** + .aget/specs/** (gh#1580 —
    instance-local spec tier)" while no finder ever populated a `specs` key. The
    surface was CLAIMED and not SEARCHED, so every study reported zero specs, and
    a reader trusting the banner reads "0 specs" as "no spec exists".

    That is worse than an omission. An unlisted surface is a known gap; a listed
    one that returns nothing is *manufactured absence* — the tool actively
    supplies false evidence of non-existence, which is the exact failure mode
    gh#1580 is named for and which this fleet's own L1220 §Absence warns about
    ("search for the behavior, not the identifier").

    Searches both tiers: canonical `../aget/specs/` (contract authority, read-only
    cross-repo) and instance-local `specs/` + `.aget/specs/`.

    Args:
        topic: Topic to search for
        domain_keywords: Optional domain keywords for boosting

    Returns:
        List of matching spec info
    """
    agent_root = get_agent_root()
    results = []
    seen = set()

    # Instance-local tiers, then the canonical contract tier from ANY adjacent
    # sibling checkout. AGENTS.md §Canonical Path Resolution: canonical specs
    # live outside this repo — a cwd-scoped search produces silent
    # false-negatives. But `parent/'aget'` was equally wrong: it hardcodes one
    # seat's directory layout, so at 30 of 32 fleet seats the root does not
    # exist, `continue` skips it, and the banner still claims it was searched
    # (measured 2026-08-05). The checkout's NAME is not a contract; the
    # presence of aget/specs/AGET_SESSION_SPEC.md is. Restored from the
    # implementation authored at aof-AGET (010b21b) and destroyed by the
    # v3.29.0 fleet upgrade (b8ece25) — see find_canonical_spec_roots.
    roots = [
        agent_root / 'specs',
        agent_root / '.aget' / 'specs',
        *find_canonical_spec_roots(agent_root),
    ]

    for root in roots:
        if not root.exists():
            continue
        for file in sorted(root.rglob('*.md')) + sorted(root.rglob('*.yaml')):
            if file.name in seen:
                continue
            match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
            if match:
                seen.add(file.name)
                results.append({
                    'spec': file.stem,
                    'doc': file.name,
                    'file': (str(file.relative_to(agent_root))
                             if agent_root in file.parents else str(file)),
                    # THE SECOND MANUFACTURED-ABSENCE DEFECT, in the same function
                    # the first one was fixed in. The finder was restored and the
                    # SCORING path re-zeroed it, so `Specs: 0` survived the fix
                    # that was written to end it (measured 2026-08-05: 62 results
                    # found, 0 rendered, on every topic).
                    #
                    # Two independent emission bugs, both here, both silent:
                    #   1. `matches` — this was the ONLY finder not emitting
                    #      `match_count`. main() re-scores every item through
                    #      composite_score(), which reads `match_count` and
                    #      defaults it to 1 → log2(1)=0 → the count term
                    #      collapses to 1 for every spec.
                    #   2. `keyword_coverage` default 0.0 — every other finder
                    #      defaults 1.0 (lines 425/782/853). search_file_for_topic
                    #      OMITS the key entirely for single-token topics, so the
                    #      default IS the value, and composite_score multiplies by
                    #      it: 0.0 × anything = 0.0, below RELEVANCE_FLOOR_DEFAULT.
                    #
                    # Net: the spec tier was unconditionally suppressed for every
                    # topic at every seat, and the report printed a confident 0.
                    # `matches` is retained because generate_report() falls back to
                    # it; `match_count` is what the scorer actually reads.
                    'match_count': match.get('match_count', 0),
                    'matches': match.get('match_count', 0),
                    'keyword_coverage': match.get('keyword_coverage', 1.0),
                    'score': match.get('score', 0.0),
                })

    results.sort(key=lambda r: r.get('score', 0.0), reverse=True)
    return results


def find_governance(topic: str, domain_keywords: list = None) -> list:
    """Find governance docs related to topic.

    Args:
        topic: Topic to search for
        domain_keywords: Optional domain keywords for boosting

    Returns:
        List of matching governance doc info
    """
    agent_root = get_agent_root()
    governance_path = agent_root / 'governance'

    results = []
    if not governance_path.exists():
        return results

    for file in governance_path.glob('*.md'):
        match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
        if match:
            results.append({
                'doc': file.name,
                'file': match['file'],
                'match_count': match['match_count'],
                'keyword_coverage': match.get('keyword_coverage', 1.0),
                'score': match.get('score', 0.0)
            })

    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def find_inbox(topic: str, domain_keywords: list = None, window_days: int = 14) -> list:
    """Find recent inbox items related to topic (v3.26 C-26-11, gh#1850).

    Scope ruling (audit S2 revisit, enacted with the search-contract change):
    inbox/ JOINS the search surface, recency-windowed (default 14 days) —
    NOTIFYs are precisely study-relevant, and gh#1850's same-day NOTIFY being
    invisible while the report claimed "Good coverage" was the motivating
    failure. sessions/, workspace/, data/ remain OUT (2026-07-04 rationale
    holds; no seat's failure implicates them).
    """
    import time
    agent_root = get_agent_root()
    inbox_path = agent_root / 'inbox'

    results = []
    if not inbox_path.exists():
        return results

    cutoff = time.time() - window_days * 86400
    for file in inbox_path.rglob('*.md'):
        try:
            if file.stat().st_mtime < cutoff:
                continue
        except OSError:
            continue
        match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
        if match:
            results.append({
                'doc': str(file.relative_to(agent_root)),
                'file': match['file'],
                'match_count': match['match_count'],
                'score': match.get('score', 0.0)
            })
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def find_skills(topic: str, domain_keywords: list = None) -> list:
    """Find skill definitions when explicitly requested — OPT-IN (--include-skills).

    `.claude/skills/` was a DECLARED-EXCLUDED surface ("unconfigured — candidates
    for a future scope ruling"). Field failure 2026-08-17: a study on the topic
    `skill` returned 672 artifacts and could not search the 53-skill corpus — the
    single most relevant body of text for that topic. Same shape as the 2026-07-26
    `sessions/` failure that produced `--include-sessions`, and resolved the same
    way: the default surface list is unchanged, the omission becomes recoverable.

    Opt-in rather than default for the reason sessions/ is: SKILL.md files are long,
    procedural, and dense in governance vocabulary, so on a generic topic they would
    dominate the ranking without adding research value. When skills ARE the subject,
    they are the whole point.

    Covers all three skill roots, not just `.claude/` — a skill resolves from any of
    them, and a search that sees one root while the agent obeys three is the
    identity-is-not-invocation error in miniature.
    """
    agent_root = get_agent_root()
    results = []
    seen = set()
    roots = (agent_root / '.claude' / 'skills',
             agent_root / '.agents' / 'skills',
             agent_root / '.codex' / 'skills')
    for base in roots:
        if not base.exists():
            continue
        for file in sorted(base.rglob('*.md')):
            if not file.is_file():
                continue
            resolved = file.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
            if match:
                results.append({'doc': str(file.relative_to(agent_root)),
                                'file': match['file'],
                                'match_count': match['match_count'],
                                'keyword_coverage': match.get('keyword_coverage', 1.0),
                                'score': match.get('score', 0.0)})
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def find_instruments(topic: str, domain_keywords: list = None) -> list:
    """Find executable instruments when explicitly requested.

    Scripts, tests, and hook sources are excluded by default because their token
    density can dominate KB prose. The opt-in makes that omission recoverable.
    """
    agent_root = get_agent_root()
    results = []
    seen = set()
    roots = (agent_root / 'scripts', agent_root / 'tests',
             agent_root / '.claude' / 'hooks', agent_root / '.codex' / 'hooks')
    for base in roots:
        if not base.exists():
            continue
        for file in sorted(base.rglob('*')):
            if not file.is_file() or file.suffix not in ('.py', '.sh', '.js', '.ts', '.json'):
                continue
            resolved = file.resolve()
            if resolved in seen:
                continue
            seen.add(resolved)
            match = search_file_for_topic(file, topic, domain_keywords=domain_keywords)
            if match:
                results.append({'doc': str(file.relative_to(agent_root)),
                                'file': match['file'],
                                'match_count': match['match_count'],
                                'keyword_coverage': match.get('keyword_coverage', 1.0),
                                'score': match.get('score', 0.0)})
    results.sort(key=lambda x: x['score'], reverse=True)
    return results


def generate_report(topic: str, findings: dict, floor_info: dict = None,
                    purpose: str = None, purpose_globs: list = None) -> str:
    """Generate human-readable study report.

    Args:
        topic: Topic that was searched
        findings: Dict of findings from search
        floor_info: Optional {'floor': float, 'suppressed': int} from relevance
            filtering (v3.26 C-26-11; audit R3/C1)

    Returns:
        Formatted markdown report
    """
    lines = []
    lines.append("=" * 60)
    lines.append(f"STUDY TOPIC: {topic}")
    lines.append("=" * 60)
    lines.append("")
    lines.append(f"**Search Date**: {datetime.now().strftime('%Y-%m-%d %H:%M')}")
    lines.append(f"**Topic**: {topic}")
    lines.append(f"**Keywords (after hygiene)**: {', '.join(prepare_keywords(topic))}")
    if _NONGATING_KEYWORDS:
        # Reported, not silent: the gating set determines what could match at all,
        # and the reader is entitled to see the query that actually ran (ST-010).
        lines.append(
            f"**Non-gating (too rare to require)**: "
            f"{', '.join(sorted(_NONGATING_KEYWORDS))} — still searched and still "
            f"ranked, but excluded from the coverage denominator so they cannot "
            f"suppress relevant artifacts (gh#1876 / RQ-378)")
    lines.append(f"**Purpose**: {purpose or 'exploration'}; priority globs: "
                 f"{', '.join(purpose_globs or []) or 'none configured'}")
    lines.append("")
    # Declared surface manifest (audit S1/C1): absence is now interpretable.
    lines.append("**Surfaces searched**: " + " ; ".join(SURFACES_SEARCHED))
    lines.append("**NOT searched (repo-internal)**: " + " ; ".join(SURFACES_EXCLUDED))
    lines.append("**⚠ Scope of that list**: " + SURFACES_OUT_OF_UNIVERSE)
    lines.append("")

    # Summary
    total = sum(len(v) for v in findings.values() if isinstance(v, list))
    lines.append("### Summary")
    lines.append("")
    lines.append(f"Found **{total}** related artifacts:")
    lines.append("")
    lines.append("| Category | Count | Top Match |")
    lines.append("|----------|:-----:|-----------|")

    for key, items in findings.items():
        if isinstance(items, list) and items:
            top = (items[0].get('ldoc') or items[0].get('pattern') or items[0].get('plan')
                   or items[0].get('initiative') or items[0].get('sop')
                   or items[0].get('doc') or 'N/A')
            lines.append(f"| {key.replace('_', ' ').title()} | {len(items)} | {top} |")
        elif isinstance(items, list):
            lines.append(f"| {key.replace('_', ' ').title()} | 0 | - |")

    lines.append("")

    # L-docs section
    if findings.get('ldocs'):
        lines.append("### Related L-docs")
        lines.append("")
        for item in findings['ldocs'][:5]:  # Top 5
            lines.append(f"- **{item['ldoc']}**: {item['title']} ({item['match_count']} matches)")
        if len(findings['ldocs']) > 5:
            lines.append(f"- ... and {len(findings['ldocs']) - 5} more")
        lines.append("")

    # Patterns section
    if findings.get('patterns'):
        lines.append("### Related Patterns")
        lines.append("")
        for item in findings['patterns'][:5]:
            lines.append(f"- {item['pattern']} ({item['match_count']} matches)")
        lines.append("")

    # PROJECT_PLANs section
    if findings.get('project_plans'):
        lines.append("### Related PROJECT_PLANs")
        lines.append("")
        for item in findings['project_plans'][:5]:
            status = "ACTIVE" if item['is_active'] else "inactive"
            lines.append(f"- {item['plan']} [{status}] ({item['match_count']} matches)")
        lines.append("")

    # Initiatives section (2026-08-14, L1388 — the scope-and-requirement tier)
    if findings.get('initiatives'):
        lines.append("### Related Initiatives")
        lines.append("")
        for item in findings['initiatives'][:5]:
            lines.append(
                f"- {item['initiative']} [{item['status']}] ({item['match_count']} matches)"
            )
        lines.append("")

    # SOPs section
    if findings.get('sops'):
        lines.append("### Related SOPs")
        lines.append("")
        for item in findings['sops'][:5]:
            lines.append(f"- {item['sop']} ({item['match_count']} matches)")
        lines.append("")

    # Governance section
    if findings.get('governance'):
        lines.append("### Related Governance")
        lines.append("")
        for item in findings['governance'][:5]:
            lines.append(f"- {item['doc']} ({item['match_count']} matches)")
        lines.append("")

    # Knowledge section (v3.25 C-25-14)
    if findings.get('knowledge'):
        lines.append("### Related Knowledge/Ontology")
        lines.append("")
        for item in findings['knowledge'][:5]:
            lines.append(f"- {item['doc']} ({item['match_count']} matches)")
        lines.append("")

    # Every opt-in or contract tier is rendered, not merely counted in Summary.
    for key, title in (('specs', 'Related Specifications'), ('inbox', 'Related Inbox'),
                       ('sessions', 'Related Sessions'), ('instruments', 'Related Instruments')):
        if findings.get(key):
            lines.append(f"### {title}")
            lines.append("")
            for item in findings[key][:5]:
                label = item.get('spec') or item.get('doc') or item.get('file')
                count = item.get('match_count', item.get('matches', 0))
                lines.append(f"- {label} ({count} matches)")
            lines.append("")

    # Recommendation — contract-derived (audit C1): states quantity over the
    # declared surface; no quality adjective the tool cannot demonstrate.
    lines.append("### Recommendation")
    lines.append("")
    suppressed = (floor_info or {}).get('suppressed', 0)
    floor_val = (floor_info or {}).get('floor')
    floor_note = (f"; {suppressed} below score floor {floor_val}, suppressed — "
                  f"use --no-floor to see all" if floor_val is not None and suppressed else "")
    # Relevance split (#1560 instance semantics, canonicalized): bucket on
    # keyword coverage >= 0.5, so token-noise raw hits never read as coverage.
    all_items = [x for v in findings.values() if isinstance(v, list) for x in v]
    relevant = [x for x in all_items if x.get('keyword_coverage', 1.0) >= 0.5]
    noise = len(all_items) - len(relevant)
    if total == 0:
        lines.append("0 artifacts found on the searched surfaces. This appears to be a "
                     "**novel topic** — but check the NOT-searched list above before "
                     "concluding novelty.")
    elif not relevant:
        lines.append(f"**novel topic** as far as the searched surfaces show: "
                     f"{noise} raw hits, all below the relevance threshold "
                     f"(keyword coverage < 0.5) — token-noise, not coverage{floor_note}.")
    else:
        plural = 'artifact' if len(relevant) == 1 else 'artifacts'
        noise_note = f" ({noise} additional raw hits below the relevance threshold)" if noise else ""
        lines.append(f"{len(relevant)} relevant {plural} across the searched "
                     f"surfaces{noise_note}{floor_note}.")
        lines.append("Cite precedents from these when proposing changes; consult the "
                     "NOT-searched list for surfaces this study cannot speak to.")

    lines.append("")
    lines.append("=" * 60)

    return '\n'.join(lines)


def call_extension_hook(payload):
    """Study extension hook (v3.26 C-26-05, gh#1836/#1848): call
    scripts/study_topic_ext.py:post_study(payload) if present.

    Contract mirrors wake_up.py WU-008: payload = {'topic', 'purpose',
    'findings', 'floor_info'}; hook returns augmented dict (additive-only,
    L464 — e.g. instance-specific search surfaces or annotations); absence =
    no-op; failure = warning + continue (ADR-004).
    """
    ext_path = get_agent_root() / 'scripts' / 'study_topic_ext.py'
    if not ext_path.exists():
        return payload
    try:
        spec = importlib.util.spec_from_file_location('study_topic_ext', str(ext_path))
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        if hasattr(module, 'post_study'):
            result = module.post_study(payload)
            if isinstance(result, dict):
                return result
    except Exception as e:
        print(f"Warning: study_topic extension hook failed: {e}", file=sys.stderr)
    return payload


def main():
    # Derive the declared canonical surface from what this seat can actually
    # reach, BEFORE any report is generated. Must precede report generation:
    # generate_report() prints SURFACES_SEARCHED verbatim.
    refresh_canonical_spec_surface(get_agent_root())
    refresh_canonical_pattern_surface(get_agent_root())
    refresh_knowledge_surface()

    parser = argparse.ArgumentParser(
        description='Study Topic Protocol - Focused Topic Research',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog='''
Examples:
  python3 study_topic.py --topic "wind down"       # Research wind down protocol
  python3 study_topic.py --topic "release" --json  # JSON output
  python3 study_topic.py --topic "L477"            # Find L477 references
  python3 study_topic.py --verify                  # Migration verification
        '''
    )
    parser.add_argument('--topic', '-t', type=str, help='Topic to research')
    parser.add_argument('--purpose', choices=['pre-implementation', 'pre-release', 'exploration', 'audit'],
                        help='Epistemic purpose — weights results by KB area (CAP-SESSION-007-06)')
    parser.add_argument('--domain-keywords', nargs='*', metavar='KEYWORD',
                        help='Domain keywords for relevance boosting (CAP-SESSION-007-07)')
    parser.add_argument('--json', action='store_true', help='Output in JSON format')
    parser.add_argument('--no-floor', action='store_true',
                        help='Disable the relevance floor (v3.26 C-26-11; useful for exhaustive ID lookups)')
    parser.add_argument('--verify', action='store_true', help='Verification mode for migration')
    parser.add_argument('--quiet', '-q', action='store_true', help='Minimal output')
    parser.add_argument('--include-sessions', action='store_true',
                        help='Also search sessions/ (OFF by default — 2026-07-04 scope '
                             'decision). Use when sessions are the SUBJECT of the study.')
    parser.add_argument('--session-days', type=int, default=90, metavar='N',
                        help='Recency window for --include-sessions (default 90)')
    parser.add_argument('--include-skills', action='store_true',
                        help='Also search .claude/.agents/.codex skills/ (OFF by default; '
                             'the skill corpus is dense and dominates generic topics). '
                             'Use when skills are the SUBJECT of the study.')
    parser.add_argument('--include-instruments', action='store_true',
                        help='Also search scripts/tests/hooks (OFF by default; executable surface)')
    parser.add_argument('--web', action='store_true',
                        help='Search external prior art. The script has no retrieval '
                             'capability, so this reports UNAVAILABLE and names the '
                             'capable layer rather than silently omitting the surface')

    args = parser.parse_args()

    # Verification mode for migration testing
    if args.verify:
        print("VERIFY: study_topic protocol (study_topic.py)")
        return 0

    # Topic is required for actual research
    if not args.topic:
        print("Error: --topic is required for research")
        print("Use --verify for migration verification")
        parser.print_help()
        return 1

    # Load config and resolve epistemic parameters (CAP-SESSION-007-06/07)
    config = load_study_topic_config()
    purpose = resolve_purpose(args.purpose, config)
    purpose_globs = get_purpose_globs(purpose, config)

    # Domain keywords: explicit flag > config > none
    domain_keywords = args.domain_keywords or config.get('domain_keywords')

    # ST-010 / RQ-378: drop zero-document-frequency tokens BEFORE any finder runs,
    # so they never enter the majority-coverage denominator. Must precede the
    # finders — prepare_keywords() is consulted per-file inside them.
    global _NONGATING_KEYWORDS
    _NONGATING_KEYWORDS, _kw_df, _kw_corpus = compute_nongating_keywords(
        args.topic, ratio=config.get('gating_df_ratio'))

    # Perform focused research with epistemic parameters
    findings = {
        'ldocs': find_ldocs(args.topic, domain_keywords=domain_keywords),
        'patterns': find_patterns(args.topic, domain_keywords=domain_keywords),
        'project_plans': find_project_plans(args.topic, domain_keywords=domain_keywords),
        'initiatives': find_initiatives(args.topic, domain_keywords=domain_keywords),
        'sops': find_sops(args.topic, domain_keywords=domain_keywords),
        'governance': find_governance(args.topic, domain_keywords=domain_keywords),
        'specs': find_specs(args.topic, domain_keywords=domain_keywords),
        'knowledge': find_knowledge(args.topic, domain_keywords=domain_keywords),
        'inbox': find_inbox(args.topic, domain_keywords=domain_keywords)
    }
    # Opt-in surface (2026-07-26 scope revisit). Added only when asked for, so the
    # default surface list and its rationale are unchanged.
    if args.include_sessions:
        findings['sessions'] = find_sessions(
            args.topic, domain_keywords=domain_keywords, days=args.session_days)
        SURFACES_SEARCHED.append(
            f'sessions/*.md, last {args.session_days}d (OPT-IN via --include-sessions)')
        for i, s in enumerate(SURFACES_EXCLUDED):
            if s.startswith('sessions/'):
                SURFACES_EXCLUDED[i] = (
                    'workspace/, data/ (deliberate — 2026-07-04 scope decision, noise at '
                    'study-time). sessions/ is INCLUDED this run via --include-sessions')
    if args.include_skills:
        findings['skills'] = find_skills(args.topic, domain_keywords=domain_keywords)
        SURFACES_SEARCHED.append(
            '.claude/skills/** + .agents/skills/** + .codex/skills/** '
            '(OPT-IN via --include-skills)')
        # Keep the excluded-surface line honest: it must not still claim the skills
        # tree is unsearched on a run that searched it.
        for i, s in enumerate(SURFACES_EXCLUDED):
            if '.claude/skills/' in s:
                SURFACES_EXCLUDED[i] = s.replace(
                    '.claude/skills/',
                    '(skills/ INCLUDED this run via --include-skills; normally .claude/skills/)')
    if args.include_instruments:
        findings['instruments'] = find_instruments(args.topic, domain_keywords=domain_keywords)
        SURFACES_SEARCHED.append(
            'scripts/** + tests/** + .claude/hooks/** + .codex/hooks/** '
            '(OPT-IN via --include-instruments)')

    # ST-009 / gh#1643 / gh#2063: --web is a DECLARED BOUNDARY, not a feature.
    #
    # For three weeks the report carried a banner telling the reader to "pair this
    # study with an explicit search of the web" while offering no way to do it —
    # a capability gap converted into a reader obligation, then reported as rigour.
    # The remediation that shipped for the gap was the sentence admitting it.
    #
    # This script cannot retrieve: it has no network dependency and must run in
    # offline and CI contexts. So it does the one honest thing available to it —
    # returns UNAVAILABLE naming the layer that CAN retrieve. An UNAVAILABLE is a
    # reportable state a downstream reader can act on; an unread paragraph is not.
    web_status = None
    if args.web:
        web_status = {
            'requested': True,
            'state': 'UNAVAILABLE',
            'missing_capability': 'external retrieval (no network client in this script)',
            'capable_layer': '/aget-study-topic SKILL.md External Prior Art step, which '
                             'uses the invoking harness web tools when present',
            'consequence': 'external prior art was NOT searched; a topic settled in '
                           'external literature will read as novel here',
        }

    # Purpose weighting is applied after all default and opt-in finders have run,
    # so no result tier can silently bypass the advertised epistemic parameter.
    for items in findings.values():
        if not isinstance(items, list):
            continue
        for item in items:
            item['purpose_boost'] = compute_purpose_boost(item.get('file', ''), purpose_globs)
            item['score'] = composite_score(item)
        items.sort(key=lambda item: item.get('score', 0.0), reverse=True)

    # Relevance floor (v3.26 C-26-11; audit R3, gh#1560): suppress items whose
    # composite score sits below the floor. Configurable; --no-floor escapes.
    floor = None if args.no_floor else config.get('relevance_floor', RELEVANCE_FLOOR_DEFAULT)
    suppressed = 0
    if floor is not None:
        for key in findings:
            kept = [x for x in findings[key] if x.get('score', floor) >= floor]
            suppressed += len(findings[key]) - len(kept)
            findings[key] = kept
    floor_info = {'floor': floor, 'suppressed': suppressed} if floor is not None else None

    # Extension hook (v3.26 C-26-05) — instance surfaces/annotations join here
    payload = call_extension_hook({'topic': args.topic, 'purpose': purpose,
                                   'findings': findings, 'floor_info': floor_info})
    findings = payload.get('findings', findings)
    floor_info = payload.get('floor_info', floor_info)

    # JSON output
    if args.json:
        output = {
            'timestamp': datetime.now().isoformat(),
            'agent_path': str(get_agent_root()),
            'topic': args.topic,
            'purpose': purpose,
            'domain_keywords': domain_keywords,
            'findings': findings,
            'total_artifacts': sum(len(v) for v in findings.values() if isinstance(v, list)),
            'search_contract': {
                'keywords': prepare_keywords(args.topic),
                'keywords_nongating_low_df': sorted(_NONGATING_KEYWORDS),
                'keyword_document_frequency': _kw_df,
                'df_corpus_size': _kw_corpus,
                'surfaces_searched': SURFACES_SEARCHED,
                'surfaces_excluded': SURFACES_EXCLUDED,
                'surfaces_out_of_universe': SURFACES_OUT_OF_UNIVERSE,
                'purpose_globs': purpose_globs,
                'sessions': {'included': args.include_sessions,
                             'recency_days': args.session_days if args.include_sessions else None,
                             'date_basis': 'filename date; undated files included'},
                'skills_included': args.include_skills,
                'instruments_included': args.include_instruments,
                'web': web_status or {'requested': False, 'state': 'NOT_REQUESTED'},
                'relevance_floor': floor,
                'suppressed_below_floor': suppressed if floor is not None else None
            }
        }
        print(json.dumps(output, indent=2, default=str))
        return 0

    # Human-readable output
    report = generate_report(args.topic, findings, floor_info=floor_info,
                             purpose=purpose, purpose_globs=purpose_globs)
    print(report)

    if web_status:
        print()
        print("### External Prior Art — UNAVAILABLE")
        print()
        print(f"`--web` was requested. Missing capability: "
              f"{web_status['missing_capability']}.")
        print(f"Capable layer: {web_status['capable_layer']}.")
        print(f"Consequence: {web_status['consequence']}.")

    return 0


if __name__ == '__main__':
    sys.exit(main())
