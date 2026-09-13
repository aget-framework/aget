"""C-34-27 — bind local vocabulary to external standards at the warranted strength.

The acceptance says: "do not assert equivalence where only similarity is warranted", and the
scope note names the failure directly: "a local record is not thereby a cryptographic receipt."
These tests hold that line, and the shipped bindings are checked by the same instrument.
"""
from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location(
    "csb", REPO / "scripts" / "check_standard_bindings.py")
csb = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(csb)

OK, OVERCLAIM, MALFORMED = csb.OK, csb.OVERCLAIM, csb.MALFORMED
SHIPPED = REPO / "ontology" / "EXTERNAL_STANDARD_BINDINGS_receipt_v1.0.yaml"


@pytest.mark.parametrize("value", [[], None, 1, "binding"])
def test_json_binding_document_requires_mapping(tmp_path, value):
    path = tmp_path / "bindings.json"
    path.write_text(json.dumps(value))
    with pytest.raises(csb.InputError):
        csb.load(path)


def b(**kw):
    base = {"concept": "C1 Thing", "predicate": "closeMatch",
            "source": "ISO/IEC 13888-1:2020",
            "scope": {"covers": "shared purpose", "does_not_cover": "the mechanism"}}
    base.update(kw)
    return base


# --- the strength rule ---------------------------------------------------------------

def test_exactMatch_without_a_justification_is_an_overclaim():
    r = csb.check_one(b(predicate="exactMatch"))
    assert r["state"] == OVERCLAIM
    assert "interchangeability" in r["problems"][0]


def test_exactMatch_from_a_noncrypto_local_to_a_crypto_standard_is_refused():
    """The specific overclaim: 'a local record is not thereby a cryptographic receipt'."""
    r = csb.check_one(b(predicate="exactMatch",
                        equivalence_justification="both are called a receipt",
                        external_is_cryptographic=True, local_is_cryptographic=False))
    assert r["state"] == OVERCLAIM
    assert "not thereby a cryptographic receipt" in r["problems"][0]


def test_exactMatch_is_allowed_when_both_are_cryptographic_and_justified():
    r = csb.check_one(b(predicate="exactMatch",
                        equivalence_justification="identical signature-over-inclusion-proof form",
                        external_is_cryptographic=True, local_is_cryptographic=True))
    assert r["state"] == OK


def test_closeMatch_to_a_crypto_standard_is_fine():
    """Similarity is exactly what closeMatch is for."""
    assert csb.check_one(b(predicate="closeMatch", external_is_cryptographic=True,
                           local_is_cryptographic=False))["state"] == OK


@pytest.mark.parametrize("pred", ["notAMatch", "sameAs", "", None])
def test_an_unrecognised_predicate_is_malformed(pred):
    assert csb.check_one(b(predicate=pred))["state"] == MALFORMED


# --- scope must state non-coverage ------------------------------------------------------

def test_a_binding_without_stated_non_coverage_is_malformed():
    """'A binding that states only what it covers is an equivalence claim in disguise.'"""
    r = csb.check_one(b(scope={"covers": "shared purpose"}))
    assert r["state"] == MALFORMED
    assert any("does_not_cover" in p for p in r["problems"])


def test_a_binding_without_coverage_is_malformed():
    assert csb.check_one(b(scope={"does_not_cover": "x"}))["state"] == MALFORMED


# --- sources must be consumer-resolvable --------------------------------------------------

@pytest.mark.parametrize("src", [
    "ISO/IEC 13888-1:2020", "RFC 4998", "IETF draft-ietf-scitt-architecture",
    "https://slsa.dev", "NIST SP 800-57", "doi:10.1000/xyz",
])
def test_a_standard_identifier_is_consumer_resolvable(src):
    assert csb.check_one(b(source=src))["state"] == OK


@pytest.mark.parametrize("src", [
    "ontology/ONTOLOGY_personal_ai_systems_v1.0.yaml", "see the L-doc", "../aget/specs/X.md",
    "our internal wiki", "L1573",
])
def test_a_local_reference_is_not_a_consumer_resolvable_source(src):
    r = csb.check_one(b(source=src))
    assert r["state"] == MALFORMED
    assert any("consumer-resolvable" in p for p in r["problems"])


# --- the shipped bindings ------------------------------------------------------------------

def test_the_shipped_bindings_validate():
    res = csb.assess(csb.load(SHIPPED))
    assert res["overall"] == OK, res
    assert res["counts"][OK] >= 6


def test_no_shipped_binding_claims_exactMatch():
    """Every receipt-family correspondence is similarity, not interchangeability."""
    doc = csb.load(SHIPPED)
    assert not [x for x in doc["bindings"] if x["predicate"] == "exactMatch"]


def test_the_scitt_binding_records_the_self_asserted_receipt_finding():
    """M-3.1: {actor, invoked, outcome} satisfies neither C1893 nor SCITT."""
    doc = csb.load(SHIPPED)
    scitt = [x for x in doc["bindings"]
             if "C1893" in x["concept"] and "scitt" in x["source"].lower()]
    assert scitt, "the C1893 -> SCITT binding must exist"
    excl = scitt[0]["scope"]["does_not_cover"]
    assert "invoked" in excl and "not a C1893" in excl
    assert "M-3.1" in excl


def test_every_shipped_binding_names_a_recognised_standard_body():
    doc = csb.load(SHIPPED)
    for x in doc["bindings"]:
        assert csb.RESOLVABLE.match(x["source"]), x["source"]


# --- input hygiene ----------------------------------------------------------------------

def test_a_bindings_file_without_a_list_is_an_input_error(tmp_path):
    p = tmp_path / "b.json"
    p.write_text(json.dumps({"nope": 1}))
    with pytest.raises(csb.InputError):
        csb.assess(csb.load(p))


def test_an_unparseable_bindings_file_is_an_input_error(tmp_path):
    p = tmp_path / "b.yaml"
    p.write_text("{[bad")
    with pytest.raises(csb.InputError):
        csb.load(p)
