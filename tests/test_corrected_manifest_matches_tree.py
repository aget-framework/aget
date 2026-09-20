"""A corrected payload manifest must match the tree it is published in.

Found by node-1 (private-aof1-aof-supervisor-AGET) 2026-09-20: PR #103 published
V334_PAYLOAD_MANIFEST_corrected.json bound to 5cfc055 and, in the same PR, edited one of
the 50 manifested paths (row 6) -- so the manifest was stale by one digest the moment it
landed. This test recomputes every entry of every handoffs/*_corrected.json against the
working tree; CI runs it on every PR, so a manifest cannot outrun its own PR again.
"""
import hashlib, json
from pathlib import Path
import pytest

REPO = Path(__file__).resolve().parent.parent
MANIFESTS = sorted((REPO / "handoffs").glob("*PAYLOAD_MANIFEST*_corrected.json"))


@pytest.mark.parametrize("manifest", MANIFESTS, ids=[m.name for m in MANIFESTS])
def test_corrected_manifest_matches_the_tree_it_is_published_in(manifest):
    d = json.loads(manifest.read_text())
    entries = d.get("entries") or d.get("files")
    stale = []
    for e in entries:
        p = REPO / e["path"]
        if not p.exists():
            stale.append((e["path"], "ABSENT")); continue
        h = hashlib.sha256(p.read_bytes()).hexdigest()
        if h != e["sha256"]:
            stale.append((e["path"], f"{e['sha256'][:12]} != tree {h[:12]}"))
    assert not stale, f"{manifest.name} is stale against this tree: {stale}"


def test_at_least_one_corrected_manifest_is_covered():
    assert MANIFESTS, "no corrected manifest found -- if that is intended, delete this test with the file"
