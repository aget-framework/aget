"""Keep the v3.30 fleet-migration contract bound to its named payloads.

The contract carries byte digests for runtime payloads and verification
sources. A source changed after the contract was published and no canonical
test compared those declarations with the files they name. The contract could
therefore remain structurally valid while its evidence tuple was false.

This guard walks the declared surfaces rather than copying their current list.
The negative control mutates one digest in memory and proves the predicate can
detect the exact drift it is meant to prevent.
"""

import copy
import hashlib
import json
from pathlib import Path


REPO = Path(__file__).resolve().parents[1]
CONTRACT = REPO / "handoffs" / "FLEET_MIGRATION_CONTRACT_v3.30.0.json"
DIGEST_FIELD = "sha256_at_v3.30.0"
DECLARATION_SECTIONS = ("runtime_payload", "verification_sources")


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
        declared = artifact[DIGEST_FIELD]
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
    original = artifact[DIGEST_FIELD]
    artifact[DIGEST_FIELD] = ("0" if original[0] != "0" else "1") + original[1:]

    mismatches = digest_mismatches(REPO, contract)
    assert len(mismatches) == 1
    assert mismatches[0] == {
        "row_id": row_id,
        "section": section,
        "path": artifact["path"],
        "declared": artifact[DIGEST_FIELD],
        "actual": original,
    }
