"""Stage F4, under weekly-train:R27 (principal, 2026-10-05 ~11:4x: "Prove the test's own code"; R15 (a)): the kit
proves each declared test's own collected code ran to an outcome (`aget_kit_report`'s witness, sys.monitoring), and a
change a test's setup makes to its helpers is setup, stated, not compared. Rows: a replaced declared body refuses; a
measured fleet member's ordinary fixture reads complete; REVW11's B201 (i) keyword-binding case and FWK-OVSR11's
F3 pre-read leads reinterpreted; the witness's own refusals (no tool id, a decorator that drops `__wrapped__`, an
async test with no plugin) and its coexistence with another sys.monitoring tool. Each with its control first. The
control tree is stage F3. B201 finding 2's rows are in test_migration_kit_result_source.py (`test_f4_r17_…`)."""
from _kit_report import requires_monitoring

import pytest

from test_migration_kit_stage_f3 import CENSUS, NOT_RUN, R27, complete, kit, refused, seen

SWAP = "import pytest\n\n\n@pytest.fixture(autouse=True)\ndef swap(request):\n    {swap}\n"

# REVW11's B201 (i) keyword-binding case: (body, the conftest fixture's swap)
B201 = {
    "kwdefault_callable_reassigned_key": (
        "def bad():\n    assert False, 'declared failure'\n\n\ndef good():\n    pass\n\n\n"
        "def check(*, action=bad, unused=good):\n    action()\n\n\ndef test_x():\n    check()\n",
        "request.module.check.__kwdefaults__ = {'unused': request.module.bad, 'action': request.module.good}"),
}


@requires_monitoring
@pytest.mark.parametrize("case", sorted(B201))
def test_f4_b201_1_a_keyword_default_rebound_by_setup_is_setup_under_r27(tmp_path, case):
    """B201 finding 1 (i) (REVW11): a fixture rebinds which callable a helper's keyword default names. F3 kept the
    identity (dict keys dropped). Under R27 the helper and its defaults are the test's setup and the test's own code
    ran, so it reads complete; the same holds for (ii)-(v) (inherited method, global or closure container, instance
    attribute), which the F3 row file shows. Control: unswapped, the declared failure is seen."""
    body, swap = B201[case]
    assert seen(kit(tmp_path / "c1", {"test_x.py": body}))
    r = kit(tmp_path / "case", {"test_x.py": body, "conftest.py": SWAP.format(swap=swap)})
    assert complete(r), (R27, r)


@requires_monitoring
def test_f4_preread_codex1_a_hook_whose_code_names_pytest_s_file_is_a_member_plugin(tmp_path):
    """FWK-OVSR11's F3 pre-read Codex 1: a member `pytest_pyfunc_call` whose code object's `co_filename` is replaced
    with `_pytest/python.py`, registered on a module named `_pytest.fake`, was trusted as pytest's own. It is not the
    object its declared home (its own module, a member file) holds under pytest's files. Control: the same module
    registered without the forged hook sees the failure."""
    conf = ("import types\nimport _pytest.python as P\n\n\ndef bypass(pyfuncitem):\n    return True\n\n\n"
            "bypass.__code__ = bypass.__code__.replace(co_filename=P.__file__)\n\n\n"
            "def pytest_configure(config):\n    fake = types.ModuleType('_pytest.fake')\n{attach}"
            "    config.pluginmanager.register(fake, 'fake')\n")
    bad = {"test_x.py": "def test_x():\n    assert False, 'declared failure'\n"}
    assert seen(kit(tmp_path / "c1", {**bad, "conftest.py": conf.format(attach="")}))
    r = kit(tmp_path / "case", {**bad, "conftest.py": conf.format(attach="    fake.pytest_pyfunc_call = bypass\n")})
    assert refused(r, "implements pytest_pyfunc_call"), r


@requires_monitoring
def test_f4_preread_codex5_a_dict_of_callables_reinserted_by_an_earlier_test_is_not_a_refusal(tmp_path):
    """FWK-OVSR11's F3 pre-read Codex 5, a false refusal: `b` calls `a`, both in a default dict; an earlier test
    re-inserts `a`. F3's walk marked whichever it reached second `<seen>`, so walk order changed the identity. Now each
    callable is identified once, and a dict is walked in key order. Control: nothing re-inserted."""
    src = ("def a():\n    return True\n\n\ndef b():\n    return a()\n\n\nhooks = {{'a': a, 'b': b}}\n\n\n"
           "def test_a():\n    {act}\n\n\ndef test_x(fs=hooks):\n    assert all(f() for f in fs.values())\n")
    assert complete(kit(tmp_path / "c1", {"test_x.py": src.format(act="pass")}))
    r = kit(tmp_path / "case", {"test_x.py": src.format(act="hooks['a'] = hooks.pop('a')")})
    assert complete(r), r


@requires_monitoring
def test_f4_preread_codex6_an_int_constant_over_4300_digits_has_a_readable_identity(tmp_path):
    """FWK-OVSR11's F3 pre-read Codex 6, a false refusal: `str()` of an int over 4300 decimal digits raises, so the
    identity was unreadable. Ints are written in hex. Control: a small int."""
    assert complete(kit(tmp_path / "c1", {"test_x.py": "def test_x():\n    assert 7 > 0\n"}))
    big = "def test_x():\n    assert (1 << 20000) > 0 and 0x" + "f" * 4000 + " > 0\n"
    r = kit(tmp_path / "case", {"test_x.py": big})
    assert complete(r), r


# --- R27's own rows ---------------------------------------------------------------------------------------------

GITHUB = ("class Tracker:\n    def check_connectivity(self):\n        raise RuntimeError('no network in tests')\n\n"
          "    def status(self):\n        return 'offline' if not self.check_connectivity() else 'online'\n\n\n"
          "import pytest\n\n\n@pytest.fixture\ndef repo(monkeypatch):\n"
          "    monkeypatch.setattr(Tracker, 'check_connectivity', lambda self: False)\n\n\n"
          "def test_x(repo):\n    assert Tracker().status() == 'offline'{fail}\n")


@requires_monitoring
def test_f4_r27_a_fixture_patching_the_member_s_own_class_reads_complete(tmp_path):
    """The shape of one measured fleet member's exposure tests (FWK-OVSR11's 22-member run on F3: 6 refused "not the
    one the census collected" on both interpreters, an R18 fail): a fixture in the test's own file monkeypatches a
    method of the member's own class, and the body runs. Under R27 that is setup: complete. Controls: the same test
    failing is seen failing; a replaced declared body is refused."""
    plain = GITHUB.replace("raise RuntimeError('no network in tests')", "return False")
    assert seen(kit(tmp_path / "c1", {"test_x.py": GITHUB.format(fail=" and False")}))
    assert refused(kit(tmp_path / "c2", {"test_x.py": plain.format(fail=""), "conftest.py": SWAP.format(
        swap="request.function.__code__ = (lambda repo: None).__code__")}), CENSUS, NOT_RUN)
    r = kit(tmp_path / "case", {"test_x.py": GITHUB.format(fail="")})
    assert complete(r), r


@requires_monitoring
@pytest.mark.parametrize("swap", [
    "request.function.__code__ = (lambda: None).__code__",         # the declared function's code replaced
    "request.node.obj = lambda: None",                              # the item's function replaced
], ids=["code_object", "item_function"])
def test_f4_r27_a_replaced_declared_body_is_refused(tmp_path, swap):
    """R27's other half: a declared test's own code that is replaced before its call never runs, so it is not
    witnessed. Control: unreplaced, the declared failure is seen."""
    bad = {"test_x.py": "def test_x():\n    assert False, 'declared failure'\n"}
    assert seen(kit(tmp_path / "c1", bad))
    r = kit(tmp_path / "case", {**bad, "conftest.py": SWAP.format(swap=swap)})
    assert refused(r, CENSUS, NOT_RUN), r


@requires_monitoring
def test_f4_r27_an_earlier_test_in_the_same_module_swapping_a_helper_is_setup(tmp_path):
    """FWK-OVSR11's agy 1 and D3 item 1 shapes (REVW11's B202 same-file falsifiers): an earlier test in the module
    swaps a callable the later test calls. The later test's own code ran: complete under R27 (stated). Controls: not
    swapped, the declared failure is seen; the earlier test itself replacing the later test's code is refused."""
    src = ("def bad():\n    assert False, 'declared failure'\n\n\nhooks = [bad]\n\n\n"
           "def test_a():\n{act}    assert True\n\n\ndef test_b():\n    hooks[0]()\n")
    assert seen(kit(tmp_path / "c1", {"test_x.py": src.format(act="")}))
    assert refused(kit(tmp_path / "c2", {"test_x.py": src.format(
        act="    test_b.__code__ = (lambda: None).__code__\n")}), CENSUS, NOT_RUN)
    r = kit(tmp_path / "case", {"test_x.py": src.format(act="    hooks[0] = lambda: None\n")})
    assert complete(r), (R27, r)


@requires_monitoring
def test_f4_r27_a_decorator_without_wraps_makes_its_wrapper_the_test_s_own_code(tmp_path):
    """A stated limit (FWK-OVSR11's point 1): a decorator that does not keep `__wrapped__` makes its wrapper the
    test's own code, so a wrapper that never calls the body reads complete. With `functools.wraps`, the body is the
    declared code and a wrapper that skips it is refused."""
    dec = ("{imp}def dec(f):\n{wraps}    def w():\n        return None\n    return w\n\n\n"
           "@dec\ndef test_x():\n    assert False, 'declared failure'\n")
    r = kit(tmp_path / "wraps", {"test_x.py": dec.format(imp="import functools\n\n\n",
                                                         wraps="    @functools.wraps(f)\n")})
    assert refused(r, NOT_RUN), r
    r = kit(tmp_path / "plain", {"test_x.py": dec.format(imp="", wraps="")})
    assert complete(r), r


@requires_monitoring
def test_f4_r27_no_free_monitoring_tool_id_is_inconclusive(tmp_path):
    """FWK-OVSR11's point 2: the witness needs a sys.monitoring tool id (3 or 4); a member that holds both makes the
    run INCONCLUSIVE, named. Control: the same member without the conftest reads complete."""
    ok = {"test_x.py": "def test_x():\n    assert True\n"}
    assert complete(kit(tmp_path / "c1", ok))
    take = "import sys\n\nsys.monitoring.use_tool_id(3, 'member')\nsys.monitoring.use_tool_id(4, 'member')\n"
    r = kit(tmp_path / "case", {**ok, "conftest.py": take})
    assert refused(r, "no free sys.monitoring tool id"), r


@requires_monitoring
def test_f4_r27_the_witness_coexists_with_a_coverage_style_monitoring_tool(tmp_path):
    """FWK-OVSR11's point 2: coverage.py's sysmon core uses tool id 1 with its own events; the kit's witness uses its
    own id and still proves each test. Control: the failing body under the same tool is seen failing."""
    cov = ("import sys\n\nE = sys.monitoring.events\nsys.monitoring.use_tool_id(1, 'coverage-like')\n"
           "sys.monitoring.register_callback(1, E.PY_START, lambda code, off: None)\n"
           "sys.monitoring.set_events(1, E.PY_START | E.PY_RETURN)\n")
    assert seen(kit(tmp_path / "c1", {"test_x.py": "def test_x():\n    assert False\n", "conftest.py": cov}))
    r = kit(tmp_path / "case", {"test_x.py": "def test_x():\n    assert True\n", "conftest.py": cov})
    assert complete(r), r


@requires_monitoring
def test_f4_r27_an_async_test_with_no_plugin_is_a_failure(tmp_path):
    """FWK-OVSR11's point 3: pytest fails an `async def` test with no async plugin before its code runs; that is a
    failure, reported as one (the witness is required only for a call reported passed; an async plugin's execution
    hook is refused as before). A generator test is a collection error in pytest itself. Control: plain, complete."""
    assert complete(kit(tmp_path / "c1", {"test_x.py": "def test_x():\n    assert True\n"}))
    r = kit(tmp_path / "case", {"test_x.py": "async def test_x():\n    assert True\n"})
    assert seen(r), r


# --- FWK-OVSR11's F4 WIP pre-read (`F4WIP_preread_ovsr11/repro_false_completes.py`): attacks on the witness itself ---

WITNESS_ATTACKS = {'codex1_fabricated_monitoring_events': ('import functools, sys\n\ndef dec(f):\n    @functools.wraps(f)\n    def run():\n        m = sys.monitoring\n        t = next(i for i in (3, 4) if m.get_tool(i) == "aget-kit-witness")\n        start = m.register_callback(t, m.events.PY_START, None)\n        end = m.register_callback(t, m.events.PY_RETURN, None)\n        m.free_tool_id(t)\n        m.use_tool_id(t, "member")\n        start(f.__code__, 0)\n        end(f.__code__, 0, None)\n    return run\n\n@dec\ndef test_x():\n    assert False\n', 'import functools\n\ndef dec(f):\n    @functools.wraps(f)\n    def run():\n        return f()\n    return run\n\n@dec\ndef test_x():\n    assert False\n'), 'codex2_setup_generator_activation': ('import functools, pytest\nold, held = [], []\n\ndef dec(f):\n    @functools.wraps(f)\n    def run():\n        g = f()\n        next(g)\n        held.append(g)\n        next(old[0], None)\n    return run\n\n@dec\ndef test_x(ok=False):\n    yield\n    assert ok\n\n@pytest.fixture(autouse=True)\ndef prime():\n    g = test_x.__wrapped__(True)\n    next(g)\n    old.append(g)\n', 'import functools, pytest\nold, held = [], []\n\ndef dec(f):\n    @functools.wraps(f)\n    def run():\n        g = f()\n        next(g)\n        held.append(g)\n        next(g, None)\n    return run\n\n@dec\ndef test_x(ok=False):\n    yield\n    assert ok\n\n@pytest.fixture(autouse=True)\ndef prime():\n    g = test_x.__wrapped__(True)\n    next(g)\n    old.append(g)\n'), 'agy1_generator_closed_early': ('import functools\n\ndef runner(f):\n    @functools.wraps(f)\n    def wrapper():\n        g = f()\n        next(g)\n        g.close()\n        return None\n    return wrapper\n\n@runner\ndef test_generator_aborted():\n    yield\n    assert False\n', 'import functools\n\ndef runner(f):\n    @functools.wraps(f)\n    def wrapper():\n        g = f()\n        next(g)\n        next(g, None)\n        return None\n    return wrapper\n\n@runner\ndef test_generator_aborted():\n    yield\n    assert False\n'), 'agy2_cancelled_coroutine': ('import asyncio, functools\n\ndef async_runner(f):\n    @functools.wraps(f)\n    def wrapper():\n        async def run():\n            t = asyncio.create_task(f())\n            await asyncio.sleep(0)\n            t.cancel()\n            try: await t\n            except asyncio.CancelledError: pass\n        asyncio.run(run())\n        return None\n    return wrapper\n\n@async_runner\nasync def test_cancelled():\n    await asyncio.sleep(0.01)\n    assert False\n', 'import asyncio, functools\n\ndef async_runner(f):\n    @functools.wraps(f)\n    def wrapper():\n        async def run():\n            await f()\n        asyncio.run(run())\n        return None\n    return wrapper\n\n@async_runner\nasync def test_cancelled():\n    await asyncio.sleep(0.01)\n    assert False\n'), 'agy3_swallowed_assertion': ('import functools\n\ndef swallow(f):\n    @functools.wraps(f)\n    def wrapper():\n        try: f()\n        except AssertionError: pass\n        return None\n    return wrapper\n\n@swallow\ndef test_failing():\n    assert False\n', 'import functools\n\ndef swallow(f):\n    @functools.wraps(f)\n    def wrapper():\n        f()\n        return None\n    return wrapper\n\n@swallow\ndef test_failing():\n    assert False\n')}


@requires_monitoring
@pytest.mark.parametrize("case", sorted(WITNESS_ATTACKS))
def test_f4_witness_attack_is_refused(tmp_path, case):
    """Each read COMPLETE with the declared failure hidden on the F4 WIP: callbacks fabricated after the tool was freed
    and re-taken (Codex 1); a generator activation primed in setup (Codex 2), closed early (agy 1) or a coroutine
    cancelled (agy 2): a generator or coroutine declared code is refused; a wrapper swallowing the declared code's
    failure (agy 3): raised yet reported passed is refused. Control (the harness's): the same without the attack, the
    declared failure seen."""
    case_src, control_src = WITNESS_ATTACKS[case]
    assert seen(kit(tmp_path / "c1", {"test_x.py": control_src}))
    r = kit(tmp_path / "case", {"test_x.py": case_src})
    assert r[2] is not None, r


@requires_monitoring
def test_f4_a_test_freeing_the_kit_s_tool_keeps_its_outcome_and_is_named(tmp_path):
    """FWK-OVSR11's F4 WIP pre-read agy 6: a test that frees tool id 3 made both tests FAIL natively under the kit; the
    witness must never change a member's outcome. Now the native result is unchanged and the run reads INCONCLUSIVE
    naming the lost tool. Control: without the freeing test, complete."""
    ok = "def test_b():\n    assert True\n"
    assert complete(kit(tmp_path / "c1", {"test_x.py": ok}))
    frees = ("import sys\n\n\ndef test_a_frees_tool():\n    for t in (3, 4):\n"
             "        if sys.monitoring.get_tool(t) == 'aget-kit-witness':\n            sys.monitoring.free_tool_id(t)\n\n\n")
    r = kit(tmp_path / "case", {"test_x.py": frees + ok})
    assert r[0] == 0 and refused(r, "tool was taken or changed"), r


UT = ("import unittest\n\n\nclass TestX(unittest.TestCase):\n{dec}    def test_x(self):\n{body}\n")


@requires_monitoring
def test_f4_a_static_unittest_skip_is_a_proven_disposition(tmp_path):
    """FWK-OVSR11's F4 WIP pre-read codex 5: `@unittest.skip` (and `skipIf`/`skipUnless`) is decided at import, like a
    mark; the census evaluates it, so the run reads complete. Control: a skip raised at run time (`self.skipTest`) is
    still not proven."""
    r = kit(tmp_path / "rt", {"test_x.py": UT.format(dec="", body="        self.skipTest('at run time')")})
    assert refused(r, "not produced by the census"), r
    r = kit(tmp_path / "case", {"test_x.py": UT.format(dec="    @unittest.skip('known')\n", body="        assert False")})
    assert complete(r), r


@requires_monitoring
def test_f4_a_failure_before_the_body_runs_is_a_failure_not_a_witness_refusal(tmp_path):
    """A measured member's shape (F4 WIP, 22 members): `@mock.patch('<module>.attr')` on a host without the module
    fails the test before its body runs. The witness is required only for a call reported passed, so this is a failing
    id, as natively. Control: the module present, complete."""
    t = "from unittest import mock\n\n\n@mock.patch('{mod}.thing')\ndef test_x(m):\n    assert True\n"
    (tmp_path / "c1").mkdir()
    assert complete(kit(tmp_path / "c1", {"test_x.py": t.format(mod="present_mod"), "present_mod.py": "thing = 1\n"}))
    r = kit(tmp_path / "case", {"test_x.py": t.format(mod="absent_module_for_this_row")})
    assert seen(r), r


@requires_monitoring
@pytest.mark.parametrize("head, dec", [
    ("HAS_TIER = False\n\n\n", "    @unittest.skipUnless(HAS_TIER, 'requires_canonical_tier')\n"),       # aof's shape
    ("_NEEDS = unittest.skipIf(True, 'coverage is not installed')\n\n\n", "    @_NEEDS\n"),          # it-consultant's
], ids=["skipUnless_module_flag", "skipIf_bound_to_a_name"])
def test_f4_measured_members_fired_unittest_skips_read_as_proven_dispositions(tmp_path, head, dec):
    """FWK-OVSR11's F4 WIP member run (21 members): aof (`@unittest.skipUnless(HAS_CANONICAL_TIER, …)`) and
    it-consultant (`_NEEDS_COVERAGE = unittest.skipIf(…)`) failed exit (g) with "the declared test's own code did not
    run to an outcome", an F4 regression: F3 read them as named runtime skips. A skipped call goes to the skip
    checks, never the witness, and a static unittest skip is now a proven disposition. Control: the same class with
    the skip not fired runs and passes."""
    src = "import unittest\n\n" + head + "class TestX(unittest.TestCase):\n{dec}    def test_x(self):\n        assert {ok}\n"
    assert complete(kit(tmp_path / "c1", {"test_x.py": src.format(dec="", ok="True")}))
    r = kit(tmp_path / "case", {"test_x.py": src.format(dec=dec, ok="False")})
    assert complete(r), r


@requires_monitoring
def test_f4_a_unittest_skip_attribute_set_after_collection_is_not_proven(tmp_path):
    """FWK-OVSR11's note on the static unittest skip: the census reads `__unittest_skip__` at collection, without the
    member's conftest, so a fixture that sets it at run time is not a static disposition and the run is refused.
    Control: the same test with the decorator reads complete."""
    src = "import unittest\n\n\nclass TestX(unittest.TestCase):\n{dec}    def test_x(self):\n        assert False\n"
    assert complete(kit(tmp_path / "c1", {"test_x.py": src.format(dec="    @unittest.skip('known')\n")}))
    late = ("import pytest\n\n\n@pytest.fixture(autouse=True)\ndef late(request):\n"
            "    request.function.__func__.__unittest_skip__ = True\n"
            "    request.function.__func__.__unittest_skip_why__ = 'known'\n")
    r = kit(tmp_path / "case", {"test_x.py": src.format(dec=""), "conftest.py": late})
    assert r[0] == 0 and refused(r, "not produced by the census"), r
