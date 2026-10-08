"""Stage F5 (weekly-train:R29, the principal's narrow stage after REVW11's B203 read of F4): the failing-first rows for
B203 findings 1 and 2, from REVW11's `revw11_f4_witness_refusal_probes.py`, each with its control asserted first. The
control tree is stage F4."""
from _kit_report import requires_monitoring

import struct

from test_migration_kit_stage_f3 import BATCH, CENSUS, complete, kit, load, refused, seen

RAISED = "raised during its call"

SECOND_CALL = """import functools
MODE = {mode!r}


def dec(f):
    @functools.wraps(f)
    def w():
        try:
            f()
        except AssertionError:
            if MODE == 'control':
                raise
        if MODE == 'case':
            f(True)
    return w


@dec
def test_x(ok=False):
    assert ok, 'declared failure'
"""


@requires_monitoring
def test_f5_b203_1_an_earlier_raise_is_not_hidden_by_a_later_return(tmp_path):
    """B203 finding 1 (REVW11's `test_kit_refuses_an_earlier_raised_body_hidden_by_a_second_return`): F4 kept only the
    last end of the test's own code, so a wrapper that caught its failure and called it again (returning) read
    COMPLETE. Every raise is now kept. Control: the wrapper re-raises; the failure is seen."""
    assert seen(kit(tmp_path / "c1", {"test_x.py": SECOND_CALL.format(mode="control")}))
    r = kit(tmp_path / "case", {"test_x.py": SECOND_CALL.format(mode="case")})
    assert refused(r, RAISED), r


@requires_monitoring
def test_f5_b203_1_a_single_clean_run_still_reads_complete(tmp_path):
    """The other side: a wrapper that calls the test's own code once and it returns reads complete."""
    r = kit(tmp_path / "case", {"test_x.py": SECOND_CALL.format(mode="none").replace("assert ok,", "assert not ok,")})
    assert complete(r), r


SIGNED_NAN = """import math, sys
MODE = {mode!r}


def test_x():
    assert math.copysign(1.0, 99.0) > 0, 'declared negative sign fails'


# same test name, location and bytecode; a different float constant in the census than in the run
value = math.copysign(float('nan'), 1.0 if MODE == 'case' and 'aget_kit_report' in sys.modules else -1.0)
test_x.__code__ = test_x.__code__.replace(
    co_consts=tuple(value if type(k) is float and k == 99.0 else k for k in test_x.__code__.co_consts))
"""


@requires_monitoring
def test_f5_b203_2_own_code_constants_differing_only_in_nan_sign_are_different_code(tmp_path):
    """B203 finding 2 (REVW11's `test_kit_refuses_distinct_signed_nan_own_code_constants`): `float.hex()` wrote +nan
    and -nan alike, so the census's and the run's different own-code constants shared an identity. Floats are now
    written by their exact IEEE-754 bits. Control: the negative constant in both, the declared failure is seen."""
    assert seen(kit(tmp_path / "c1", {"test_x.py": SIGNED_NAN.format(mode="control")}))
    r = kit(tmp_path / "case", {"test_x.py": SIGNED_NAN.format(mode="case")})
    assert refused(r, CENSUS), r


def test_f5_b203_2_float_and_complex_constants_are_written_by_their_bits():
    """`const_bytes` keeps every bit: +nan, -nan, a nan payload, +0.0 and -0.0 are all different, and complex parts too.
    Control: equal values give equal bytes."""
    census = load("aget_kit_census", BATCH / "pytest_plugin")
    nan_payload = struct.unpack(">d", bytes.fromhex("7ff8000000000001"))[0]
    vals = [float("nan"), -float("nan"), nan_payload, 0.0, -0.0]
    assert len({census.const_bytes(v) for v in vals}) == len(vals)
    assert census.const_bytes(complex(0.0, float("nan"))) != census.const_bytes(complex(0.0, -float("nan")))
    assert census.const_bytes(1.5) == census.const_bytes(3.0 / 2)
