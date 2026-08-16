"""Keep the v3.30 fleet-migration contract bound to its named payloads.

The contract carries byte digests for runtime payloads and verification
sources. A source changed after the contract was published and no canonical
test compared those declarations with the files they name. The contract could
therefore remain structurally valid while its evidence tuple was false.

This guard walks the declared surfaces rather than copying their current list.
The negative control mutates one digest in memory and proves the predicate can
detect the exact drift it is meant to prevent.
"""

import ast
import copy
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
CONTRACT = REPO / "handoffs" / "FLEET_MIGRATION_CONTRACT_v3.30.0.json"
DIGEST_FIELD = "sha256_at_v3.30.0"

# A payload may be amended AFTER the v3.30.0 tag and BEFORE its wave dispatches.
# When that happens the two facts are different and both must survive:
#
#   sha256_at_v3.30.0 - what the tag shipped. Historical. Never rewritten, or
#                       the field name becomes a lie and published evidence is
#                       silently restated.
#   sha256_current    - what a destination must match TODAY. Authoritative for
#                       verification whenever present.
#
# First amendment: gh#2257 (2026-08-15), CI-3000-01. Overwriting the tag digest
# in place would have been the cheap move and the wrong one -- it erases the
# record of what v3.30.0 actually was while the field still claims to hold it.
CURRENT_DIGEST_FIELD = "sha256_current"
DECLARATION_SECTIONS = ("runtime_payload", "verification_sources")
SKIP_NAMES = frozenset({"skipTest", "skip", "skipIf", "skipUnless"})


def effective_digest_field(artifact):
    """The field a destination must match: the amendment if any, else the tag."""
    return CURRENT_DIGEST_FIELD if CURRENT_DIGEST_FIELD in artifact else DIGEST_FIELD


def declared_artifacts(contract):
    """Yield each row ID, declaration section, and declared artifact."""
    for row in contract["semantic_rows"]:
        for section in DECLARATION_SECTIONS:
            for artifact in row.get(section, []):
                if DIGEST_FIELD in artifact:
                    yield row["id"], section, artifact


def digest_mismatches(repo, contract):
    """Return source-verifiable mismatches for every declared artifact."""
    mismatches = []
    for row_id, section, artifact in declared_artifacts(contract):
        relative_path = artifact["path"]
        source = repo / relative_path
        actual = (
            hashlib.sha256(source.read_bytes()).hexdigest()
            if source.is_file()
            else None
        )
        declared = artifact[effective_digest_field(artifact)]
        if actual != declared:
            mismatches.append(
                {
                    "row_id": row_id,
                    "section": section,
                    "path": relative_path,
                    "declared": declared,
                    "actual": actual,
                }
            )
    return mismatches


def load_contract():
    return json.loads(CONTRACT.read_text())


def test_every_declared_artifact_digest_matches_its_named_file():
    mismatches = digest_mismatches(REPO, load_contract())
    assert not mismatches, json.dumps(mismatches, indent=2, sort_keys=True)


def test_injected_one_byte_digest_mismatch_is_detected():
    contract = copy.deepcopy(load_contract())
    row_id, section, artifact = next(declared_artifacts(contract))
    # Mutate whichever field is AUTHORITATIVE for this artifact. Mutating the
    # tag field on an amended row would prove nothing -- the comparison no
    # longer reads it, so the negative control would pass while detecting
    # nothing, which is the exact failure this control exists to rule out.
    field = effective_digest_field(artifact)
    original = artifact[field]
    artifact[field] = ("0" if original[0] != "0" else "1") + original[1:]

    mismatches = digest_mismatches(REPO, contract)
    assert len(mismatches) == 1
    assert mismatches[0] == {
        "row_id": row_id,
        "section": section,
        "path": artifact["path"],
        "declared": artifact[field],
        "actual": original,
    }


def test_an_amended_row_is_verified_against_the_amendment_not_the_tag():
    """An amended payload must be checked against sha256_current.

    Both polarities, because a one-sided version of this is what would let the
    amendment be cosmetic: the live digest must DECIDE the comparison, and the
    tag digest must be INERT for verification while still being present as the
    historical record.
    """
    contract = copy.deepcopy(load_contract())
    amended = [
        (rid, art)
        for rid, _section, art in declared_artifacts(contract)
        if CURRENT_DIGEST_FIELD in art
    ]
    assert amended, "no amended rows — this guard would be vacuous"

    for _rid, artifact in amended:
        assert artifact[DIGEST_FIELD] != artifact[CURRENT_DIGEST_FIELD], (
            "an amended row must record two DIFFERENT digests; equal values mean "
            "the tag record was overwritten rather than preserved"
        )
        assert artifact.get("amended_post_tag"), (
            "an amendment must say why it happened — a digest that changed with "
            "no recorded reason is indistinguishable from tampering"
        )

    # POLARITY 1: corrupting the tag digest must NOT be reported (it is inert).
    tag_corrupted = copy.deepcopy(contract)
    for _rid, _s, art in declared_artifacts(tag_corrupted):
        if CURRENT_DIGEST_FIELD in art:
            art[DIGEST_FIELD] = "f" * 64
    assert not digest_mismatches(REPO, tag_corrupted), (
        "the tag digest must not decide verification on an amended row"
    )

    # POLARITY 2: corrupting the current digest MUST be reported.
    current_corrupted = copy.deepcopy(contract)
    for _rid, _s, art in declared_artifacts(current_corrupted):
        if CURRENT_DIGEST_FIELD in art:
            art[CURRENT_DIGEST_FIELD] = "f" * 64
    assert len(digest_mismatches(REPO, current_corrupted)) == len(amended), (
        "the current digest must decide verification on an amended row"
    )


# --- Portability of the declared verification sources -----------------------
#
# Digest equality proves a declared source is the file it names. It does NOT
# prove that file can decide anything on a machine other than the author's.
#
# The 2026-08-10 case: the contract declared four verification sources; the
# published evidence bound only one of them; the unbound one asserted against
# the ambient host and was green on every developer workstation while failing
# on a bare runner. Digest checks were green throughout, because the digest was
# never the property in question.
#
# The predicate below is AST-based on purpose. A substring scan for "skipTest"
# cannot distinguish a *call* from a docstring that explains why the skips were
# removed, so it rejects the very repairs it should accept — and the cheapest
# way to satisfy it is to stop documenting the decision. Match at statement and
# decorator position instead, and prove both polarities.


def environment_conditional_skips(source: str):
    """Return (lineno, name) for every skip CALL or skip DECORATOR in a module.

    A mention inside a docstring, comment, or string literal is not a skip and
    must not be reported — that false positive penalises documentation.
    """
    # A skip DECORATOR written as a call (@unittest.skipIf(...)) is reachable
    # from both branches below, so collect into a set keyed by position — the
    # first draft of this predicate double-counted it, and its own negative
    # control is what caught that.
    found = set()
    tree = ast.parse(source)

    def name_of(node):
        if isinstance(node, ast.Attribute):
            return node.attr
        if isinstance(node, ast.Name):
            return node.id
        return None

    for node in ast.walk(tree):
        if isinstance(node, ast.Call):
            called = name_of(node.func)
            if called in SKIP_NAMES:
                found.add((node.lineno, called))
        elif isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.ClassDef)):
            for decorator in node.decorator_list:
                target = decorator.func if isinstance(decorator, ast.Call) else decorator
                decorated = name_of(target)
                if decorated in SKIP_NAMES:
                    found.add((decorator.lineno, decorated))
    return sorted(found)


def declared_verification_sources(contract):
    for row_id, section, artifact in declared_artifacts(contract):
        if section == "verification_sources":
            yield row_id, artifact["path"]


def test_every_declared_verification_source_is_environment_independent():
    """No declared source may decide its own applicability from the host."""
    offenders = {}
    checked = 0
    for row_id, relative_path in declared_verification_sources(load_contract()):
        source_file = REPO / relative_path
        assert source_file.is_file(), f"{row_id}: declared source missing: {relative_path}"
        skips = environment_conditional_skips(source_file.read_text())
        checked += 1
        if skips:
            offenders[relative_path] = skips
    assert checked, "no verification sources were checked — predicate reached nothing"
    assert not offenders, json.dumps(offenders, indent=2, sort_keys=True)


def test_a_skip_call_is_detected():
    """Negative control: the predicate detects the construct it forbids."""
    module = (
        "import unittest\n"
        "class T(unittest.TestCase):\n"
        "    def test_a(self):\n"
        "        if not host_has_it():\n"
        "            self.skipTest('no adjacent checkout on this host')\n"
    )
    assert [name for _, name in environment_conditional_skips(module)] == ["skipTest"]


def test_a_skip_decorator_is_detected():
    module = (
        "import unittest\n"
        "class T(unittest.TestCase):\n"
        "    @unittest.skipIf(not host_has_it(), 'ambient')\n"
        "    def test_a(self):\n"
        "        pass\n"
    )
    assert [name for _, name in environment_conditional_skips(module)] == ["skipIf"]


def test_a_documented_mention_is_not_a_skip():
    """The other polarity, and the reason this is AST-based.

    A file that removed its skips and says so in prose must PASS. A substring
    matcher fails this test, which is how it turns documentation into a defect.
    """
    module = (
        '"""This module used to call self.skipTest(...) when no checkout was\n'
        'adjacent; every test now synthesises its own topology instead.\n'
        '"""\n'
        "SKIP_DOC = 'skipIf and skipUnless are deliberately unused here'\n"
        "# self.skipTest('historical form, retained in a comment only')\n"
        "def test_a():\n"
        "    assert True\n"
    )
    assert environment_conditional_skips(module) == []
