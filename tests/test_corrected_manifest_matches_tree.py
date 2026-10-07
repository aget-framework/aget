"""A corrected payload manifest must match the tree it is published in.

Found by an independent AGET contributor 2026-09-20: PR #103 published
V334_PAYLOAD_MANIFEST_corrected.json bound to 5cfc055 and, in the same PR, edited one of
the 50 manifested paths (row 6) -- so the manifest was stale by one digest the moment it
landed. This test recomputes every entry of every handoffs/*_corrected.json against the
working tree; CI runs it on every PR, so a manifest cannot outrun its own PR again.

POST-RELEASE AMENDMENT (2026-09-26). Without it, every later edit to any of the 50 pinned
paths failed CI forever. The remedy reuses the convention the fleet migration contract
already carries and tests (tests/test_fleet_migration_contract_digests.py): an entry may add
`sha256_current` plus a non-empty `amended_post_tag` reason. The released `sha256` stays
INTACT as the record of what shipped; `sha256_current`, when present, decides the comparison.
An edit with no amendment still fails -- the PR #103 case this test exists for.
"""
import copy, hashlib, json
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parent.parent
MANIFESTS = sorted((REPO / "handoffs").glob("*PAYLOAD_MANIFEST*_corrected.json"))
DIGEST_FIELD, CURRENT_DIGEST_FIELD = "sha256", "sha256_current"


def _entries(d: dict) -> list:
    return d.get("entries") or d.get("files")


def stale_entries(repo: Path, d: dict) -> list:
    stale = []
    for e in _entries(d):
        p = repo / e["path"]
        if not p.exists():
            stale.append((e["path"], "ABSENT")); continue
        if CURRENT_DIGEST_FIELD in e:
            if not e.get("amended_post_tag"):
                stale.append((e["path"], "amended with no amended_post_tag reason")); continue
            if e[CURRENT_DIGEST_FIELD] == e[DIGEST_FIELD]:
                stale.append((e["path"], "sha256_current equals the released sha256: record overwritten, not amended")); continue
        want = e.get(CURRENT_DIGEST_FIELD, e[DIGEST_FIELD])
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h != want:
            which = "sha256_current" if CURRENT_DIGEST_FIELD in e else "sha256 (no amendment)"
            stale.append((e["path"], f"{which} {want[:12]} != tree {h[:12]}"))
    return stale


@pytest.mark.parametrize("manifest", MANIFESTS, ids=[m.name for m in MANIFESTS])
def test_corrected_manifest_matches_the_tree_it_is_published_in(manifest):
    stale = stale_entries(REPO, json.loads(manifest.read_text()))
    assert not stale, f"{manifest.name} is stale against this tree: {stale}"


def test_at_least_one_corrected_manifest_is_covered():
    assert MANIFESTS, "no corrected manifest found -- if that is intended, delete this test with the file"


# --- both polarities of the amendment rule, on a scratch repository -------------------------

def _scratch(tmp_path, content=b"v1\n"):
    (tmp_path / "f.txt").write_bytes(content)
    return {"files": [{"path": "f.txt", "sha256": hashlib.sha256(b"v1\n").hexdigest()}]}


def test_unchanged_file_passes(tmp_path):
    assert stale_entries(tmp_path, _scratch(tmp_path)) == []


def test_unamended_edit_fails__the_pr103_case(tmp_path):
    assert "no amendment" in stale_entries(tmp_path, _scratch(tmp_path, b"v2\n"))[0][1]


def test_amended_edit_passes_and_the_released_digest_is_inert(tmp_path):
    d = _scratch(tmp_path, b"v2\n")
    e = d["files"][0]
    e["sha256_current"] = hashlib.sha256(b"v2\n").hexdigest()
    e["amended_post_tag"] = "test"
    assert stale_entries(tmp_path, d) == []
    corrupted = copy.deepcopy(d)
    corrupted["files"][0]["sha256"] = "f" * 64          # released digest must not decide
    assert stale_entries(tmp_path, corrupted) == []
    corrupted["files"][0]["sha256_current"] = "e" * 64  # current digest must decide
    assert stale_entries(tmp_path, corrupted)


def test_amendment_without_a_reason_fails(tmp_path):
    d = _scratch(tmp_path, b"v2\n")
    d["files"][0]["sha256_current"] = hashlib.sha256(b"v2\n").hexdigest()
    assert "no amended_post_tag" in stale_entries(tmp_path, d)[0][1]


def test_overwriting_the_released_digest_is_not_an_amendment(tmp_path):
    d = _scratch(tmp_path)
    d["files"][0]["sha256_current"] = d["files"][0]["sha256"]
    d["files"][0]["amended_post_tag"] = "test"
    assert "overwritten" in stale_entries(tmp_path, d)[0][1]
