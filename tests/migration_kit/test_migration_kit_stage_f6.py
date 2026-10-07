"""Stage F6 (weekly-train:R34, one stage after REVW11's B204 read of F5): the failing-first rows for B204 finding 1, a
start and a completed outcome of the declared test's own code taken from different activations, from REVW11's
`revw11_f5_activation_refusal_probes.py` and FWK-OVSR11's `repro_activation_pairing.py`, each with its controls asserted
first. The control tree is stage F5. Starts and outcomes are now paired by the activation (its frame), and own code
running on another thread during the call cannot be paired with it, so it reads INCONCLUSIVE (the named cost)."""
import json

from test_migration_kit_stage_f3 import complete, kit, refused, seen

THREAD = "own code ran on another thread"

SETUP_RETURN = """import functools, threading, json
from pathlib import Path
import pytest
MODE = {mode!r}
old_ready = threading.Event()
old_release = threading.Event()
bad_ready = threading.Event()
bad_release = threading.Event()
entered = []
returned = []
old = []
new = []


def dec(f):
    @functools.wraps(f)
    def run():
        if MODE == 'failure':
            bad_release.set()
            f(False)
        elif MODE == 'stable':
            old_release.set()
            f(True)
        else:
            t = threading.Thread(target=f, args=(False,), daemon=True)
            new.append(t)
            t.start()
            assert bad_ready.wait(5)
            old_release.set()
            old[0].join(5)
            assert not old[0].is_alive()
            assert t.is_alive()
    return run


@dec
def test_x(ok=False):
    entered.append(ok)
    if ok:
        old_ready.set()
        old_release.wait()
        returned.append(ok)
        return
    bad_ready.set()
    bad_release.wait()
    assert False, 'proper call must fail once it reaches its assertion'


@pytest.fixture(autouse=True)
def prime():
    if MODE == 'case':
        t = threading.Thread(target=test_x.__wrapped__, args=(True,), daemon=True)
        old.append(t)
        t.start()
        assert old_ready.wait(5)
    yield
    Path('activation_facts.json').write_text(json.dumps(dict(entered=entered, returned=returned,
        primed_still_running=[t.is_alive() for t in old], call_still_running=[t.is_alive() for t in new])))
"""


def test_f6_b204_1_a_setup_activation_s_return_does_not_complete_a_call_activation(tmp_path):
    """B204 finding 1 (REVW11's `test_kit_refuses_to_combine_a_new_start_with_a_setup_activation_s_return`): a fixture
    starts the declared code (passing) during setup; in the call the wrapper starts it again (failing) and lets the
    setup activation return, while the call's own activation never finishes. F5 counted the start and the return by
    code alone and read COMPLETE. Controls: the failing run directly is seen; the passing run directly is complete;
    the member's facts show the shape (setup activation returned, call activation still running)."""
    assert seen(kit(tmp_path / "failure", {"test_x.py": SETUP_RETURN.format(mode="failure")}))
    assert complete(kit(tmp_path / "stable", {"test_x.py": SETUP_RETURN.format(mode="stable")}))
    root = tmp_path / "case"
    r = kit(root, {"test_x.py": SETUP_RETURN.format(mode="case")})
    facts = json.loads((root / "activation_facts.json").read_text())
    assert r[0] == 0 and facts == {"entered": [True, False], "returned": [True], "primed_still_running": [False],
                                   "call_still_running": [True]}, (r, facts)
    assert refused(r, THREAD), r


BLOCKED_CALL = """import functools, threading, pytest
MODE = {mode!r}
gate_setup = threading.Event(); entered = threading.Event(); hold_call = threading.Event()
threads = []


def dec(f):
    @functools.wraps(f)
    def run():
        if MODE == 'control':
            f(False, False)
            return
        t = threading.Thread(target=f, args=(False, True), daemon=True); t.start()
        entered.wait(5)
        gate_setup.set()
        threads[0].join(5)
    return run


@dec
def test_x(ok=True, block=False):
    if block:
        entered.set(); hold_call.wait(30)
    elif MODE == 'case':
        gate_setup.wait(5)
    assert ok


@pytest.fixture(autouse=True)
def prime():
    if MODE == 'case':
        t = threading.Thread(target=test_x.__wrapped__, args=(True, False), daemon=True); t.start(); threads.append(t)
"""


def test_f6_b204_1_the_overseer_s_shape_reads_inconclusive(tmp_path):
    """B204 finding 1 as FWK-OVSR11 reproduced it (`repro_activation_pairing.py`): the call's activation blocks before
    its assertion; the setup activation supplies the return. Control: the failing body run directly is seen."""
    assert seen(kit(tmp_path / "c1", {"test_x.py": BLOCKED_CALL.format(mode="control")}))
    r = kit(tmp_path / "case", {"test_x.py": BLOCKED_CALL.format(mode="case")})
    assert r[0] == 0 and not r[1], r
    assert refused(r, THREAD), r


IN_THREAD = """import functools, threading
MODE = {mode!r}


def dec(f):
    @functools.wraps(f)
    def run():
        if MODE == 'direct':
            f()
            return
        t = threading.Thread(target=f, daemon=True); t.start(); t.join(5)
    return run


@dec
def test_x():
    assert 1 + 1 == 2
"""


def test_f6_cost_own_code_that_completes_on_another_thread_reads_inconclusive(tmp_path):
    """The named cost: the declared code started and returned during the call, but on a thread other than the one
    running the call, so the kit cannot pair it with the call and the run reads INCONCLUSIVE. Control: the same code
    called directly on the call's thread reads complete."""
    assert complete(kit(tmp_path / "c1", {"test_x.py": IN_THREAD.format(mode="direct")}))
    r = kit(tmp_path / "case", {"test_x.py": IN_THREAD.format(mode="thread")})
    assert refused(r, THREAD), r


HELPER_THREAD = """import threading


def work(out):
    out.append(sum(range(10)))


def test_x():
    out = []
    t = threading.Thread(target=work, args=(out,)); t.start(); t.join(5)
    assert out == [45]
"""


def test_f6_a_test_whose_helper_runs_on_a_thread_still_reads_complete(tmp_path):
    """The other side: a test that runs a helper (not its own code) on a thread, on its call's thread, reads complete;
    and its failing twin is seen."""
    assert seen(kit(tmp_path / "c1", {"test_x.py": HELPER_THREAD.replace("[45]", "[46]")}))
    assert complete(kit(tmp_path / "case", {"test_x.py": HELPER_THREAD}))


AFTER_CALL = """import functools, threading, pytest
MODE = {mode!r}
after = threading.Event()
late = []


def dec(f):
    @functools.wraps(f)
    def run():
        t = threading.Thread(target=lambda: after.wait(5) and f(False), daemon=True); t.start(); late.append(t)
        if MODE == 'also_direct':
            f(True)
    return run


@dec
def test_x(ok=True):
    assert ok


@pytest.fixture(autouse=True)
def release_after_the_call():
    yield
    after.set()
    late[0].join(5)
"""


def test_f6_a_run_begun_only_after_the_call_is_neither_counted_nor_refused_as_threaded(tmp_path):
    """FWK-OVSR12's WIP pre-read point 1: a thread started in the call whose run of the test's own code begins only
    after the call has ended (teardown releases it) is outside the call. Alone, nothing ran in the call, so it is not
    proven; next to a direct run on the call's thread that returned, the call is proven and the late run is not
    counted either way. Control: the direct-only failure is seen."""
    assert seen(kit(tmp_path / "c1", {"test_x.py": "def test_x():\n    assert False\n"}))
    r = kit(tmp_path / "late_only", {"test_x.py": AFTER_CALL.format(mode="late_only")})
    assert refused(r, "own code did not run"), r
    assert complete(kit(tmp_path / "both", {"test_x.py": AFTER_CALL.format(mode="also_direct")}))
