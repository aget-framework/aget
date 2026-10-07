"""Stage F3: the failing-first rows for FWK-OVSR9's D3 pre-read items 1-9 (`overseer_prereads/D3/repro/d3_item0N.sh`,
each rewritten here with its own controls, which are asserted first so a row fails only for its defect), and for the
member measurement on the F3 WIP (0 of 4 members complete: Python 3.14 keeps constant slices in `co_consts`, which
marshal formats below 5 cannot write, so every test that slices with constants read "identity could not be read").
The control tree is stage D3 (the defects are in D3's new identity and execution-hook code)."""
import importlib.util
import os
import subprocess
import sys
from pathlib import Path
from types import SimpleNamespace

import pytest

BATCH = Path(__file__).resolve().parents[2] / "scripts" / "migration_kit"
sys.path.insert(0, str(BATCH))


def load(name, folder=BATCH):
    spec = importlib.util.spec_from_file_location(name, folder / f"{name}.py")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


RBND = load("result_binding")
CENSUS = "not the one the census collected"
NOT_RUN = "own code did not run"            # F4 (weekly-train:R27): the declared test's own code was not witnessed
R27 = ("changed at F4 (weekly-train:R27, R15 (a)): a helper, default or class the test reaches is its setup; "
       "the kit proves the declared test's own code ran to an outcome, so this reads complete")


def kit(root, files, target="test_x.py", bytecode=False):
    """A member folder `root` with `files` and an empty pytest.ini, run under the kit's report plugin as the
    overseer's reproductions run it: (exit code, failing ids, the kit's refusal reason or None)."""
    root.mkdir(parents=True, exist_ok=True)
    (root / "pytest.ini").write_text("[pytest]\n")
    for name, src in files.items():
        (root / name).write_text(src)
    env = {k: v for k, v in os.environ.items() if k not in ("PYTEST_ADDOPTS", "PYTHONPATH", "PYTHONDONTWRITEBYTECODE")}
    if not bytecode:
        env["PYTHONDONTWRITEBYTECODE"] = "1"
    rep = str(root.parent / f"{root.name}.{len(list(root.parent.glob(root.name + '.*.report.jsonl')))}.report.jsonl")
    tok = RBND.new_report(rep)
    p = subprocess.run([sys.executable, "-m", "pytest", "-q", "-p", "no:cacheprovider", target], cwd=root,
                       env=RBND.report_env(env, rep, tok), capture_output=True, text=True)
    ids, why, _ = RBND.report_failures(rep, tok, p.stdout + p.stderr, exit_code=p.returncode)
    return p.returncode, list(ids or []), why


def seen(r):
    """The declared failure was seen and nothing was refused."""
    return r[0] == 1 and bool(r[1]) and r[2] is None


def complete(r):
    return r[0] == 0 and not r[1] and r[2] is None


def refused(r, *why):
    return r[2] is not None and (not why or any(w in r[2] for w in why))


# --- the member measurement: an identity without marshal ------------------------------------------------------------

SLICES = ("def test_x():\n    s = 'abcdef'\n    assert s[1:3] == 'bc' and s[::-1][:2] == 'fe' and s[2:] == 'cdef'\n")


def test_f3_member_a_test_that_slices_with_constants_has_a_readable_identity(tmp_path):
    """FWK-OVSR9's member measurement on the F3 WIP (`overseer_prereads/D3/FLEET_KIT_COST_4members_F3WIP_125bdd3.json`):
    0 of 4 members complete, 15-16 tests each refused as "identity could not be read". On Python 3.14 `s[1:3]`
    keeps `slice(1, 3, None)` in `co_consts` and `marshal.dumps(code, 2)` raises ValueError. Control: the same test
    without a slice reads complete. Cases: the slicing test reads complete, and with a failing body is seen failing,
    not refused. (Below Python 3.14 a slice is not a constant: the row passes on every stage there.)"""
    assert complete(kit(tmp_path / "plain", {"test_x.py": "def test_x():\n    assert 'abc'.upper() == 'ABC'\n"}))
    r = kit(tmp_path / "slices", {"test_x.py": SLICES})
    assert complete(r), r
    r = kit(tmp_path / "fails", {"test_x.py": SLICES.replace("== 'bc'", "== 'zz'")})
    assert seen(r), r


def test_f3_member_identity_is_the_same_from_a_cold_and_a_warm_pycache(tmp_path):
    """The identity is read from the code's values, so a process that compiled the test (cold `__pycache__`) and one
    that loaded it from `__pycache__` (warm) read the same identity: the kit, with bytecode written, reads complete on
    the first run (the census may write the cache the run then loads) and on the second (both load it). Guard row for
    the new encoding (`aget_kit_census.code_bytes`): no failing-first claim."""
    files = {"test_x.py": SLICES + "\n\ndef test_y(fn=str.upper, k={'a': (1.5, -0.0, b'x', None, ...)}):\n"
                                   "    assert fn('a') == 'A' and k\n"}
    root = tmp_path / "member"
    first = kit(root, files, bytecode=True)
    assert list((root / "__pycache__").glob("test_x*.pyc")), "control: the first run wrote the cache"
    second = kit(root, files, bytecode=True)
    assert complete(first) and complete(second), (first, second)
    census = load("aget_kit_census", BATCH / "pytest_plugin")
    src = (root / "test_x.py").read_text()
    compiled = compile(src, str(root / "test_x.py"), "exec")
    import importlib.util as iu
    spec = iu.spec_from_file_location("test_x_warm", root / "test_x.py")
    loaded = spec.loader.get_code("test_x_warm")      # from the warm `__pycache__`
    assert census.code_bytes(compiled) == census.code_bytes(loaded)


def test_f3_member_an_unknown_code_constant_refuses_with_its_reason():
    """A constant `code_bytes` cannot write by value is not hashed by a fallback: the identity is unreadable and the
    census records why (the run's refusal names it: "its identity could not be read (unreadable (TypeError: …))")."""
    census = load("aget_kit_census", BATCH / "pytest_plugin")
    ns = {}
    exec(compile("def test_x():\n    return 1\n", str(BATCH / "t_mod.py"), "exec"), ns)
    f = ns["test_x"]
    f.__code__ = f.__code__.replace(co_consts=f.__code__.co_consts + (object(),))
    with pytest.raises(TypeError, match="a code constant of type builtins.object"):
        census.item_identity(SimpleNamespace(obj=f), str(BATCH))
    census.pytest_itemcollected(SimpleNamespace(nodeid="t_mod.py::test_x", obj=f,
                                                config=SimpleNamespace(rootpath=BATCH)))
    assert census._ident["t_mod.py::test_x"] == ["unreadable (TypeError: a code constant of type builtins.object)"]


# --- D3 pre-read items 1-5 and 7: the test's identity ------------------------------------------------------------------

def test_f3_i1_a_cyclic_default_swapped_by_an_earlier_test_is_setup_under_r27(tmp_path):
    """Reinterpreted at F4 under weekly-train:R27 (R15 (a)): the swap is the test's setup and the
    declared test's own code ran, so it reads complete; the history below is what F3 refused. Item 1 (`d3_item01.sh`): a self-referencing list default made the identity recurse; census and run both read
    "unreadable (RecursionError)", and the equal markers compared as one identity, so an earlier test swapping the
    test's function default for a no-op read complete."""
    body = ("unused = []\nunused.append({extra})\n\n\ndef body():\n    assert {ok}, 'declared failure'\n\n\n"
            "def test_a():\n{swap}    assert True\n\n\ndef test_x(fn=body, extra=unused):\n    fn()\n")
    swap = "    test_x.__defaults__ = (lambda: None, unused)\n"
    # changed at F4: the cyclic default is no longer walked (no RecursionError); the swapped default is setup (R27)
    assert complete(kit(tmp_path / "c2", {"test_x.py": body.format(extra="1", ok="True", swap="")}))
    assert seen(kit(tmp_path / "c3", {"test_x.py": body.format(extra="unused", ok="False", swap="")}))
    r = kit(tmp_path / "case", {"test_x.py": body.format(extra="unused", ok="False", swap=swap)})
    assert complete(r), (R27, r)


def test_f3_i2_a_wrapped_test_s_closure_swap_is_refused(tmp_path):
    """Item 2 (`d3_item02.sh`): a `functools.wraps` test whose wrapper's closure cell (the declared body) a run-only
    conftest fixture swaps for a no-op."""
    dec = ("import functools\n\n\ndef dec(f):\n    @functools.wraps(f)\n    def w():\n        return f()\n    return w"
           "\n\n\n@dec\ndef test_x():\n    assert False, 'declared failure'\n")
    plain = "def test_x():\n    assert False, 'declared failure'\n"
    fix = "import pytest\n\n\n@pytest.fixture(autouse=True)\ndef _swap(request):\n    {act}\n"
    assert seen(kit(tmp_path / "c1", {"test_x.py": dec, "conftest.py": fix.format(act="pass")}))
    assert refused(kit(tmp_path / "c2", {"test_x.py": plain, "conftest.py": fix.format(
        act="request.function.__code__ = (lambda: None).__code__")}))
    r = kit(tmp_path / "case", {"test_x.py": dec, "conftest.py": fix.format(
        act="request.function.__closure__[0].cell_contents = lambda: None")})
    assert refused(r, CENSUS, NOT_RUN), r          # F4: the wrapped declared body never ran (the witness)


def test_f3_i3_a_partial_test_swapped_for_another_partial_is_refused(tmp_path):
    """Item 3 (`d3_item03.sh`): a test collected from a module-level `functools.partial` had identity [item class]
    only, so swapping the item's partial for `partial(no-op)` at run time was not seen."""
    head = ("import functools\n\nimport pytest\n\n\ndef _body():\n    assert False, 'declared failure'\n\n\n"
            "def _noop():\n    return None\n\n\n")
    swap = "@pytest.fixture(autouse=True)\ndef _swap(request):\n    request.node.obj = {new}\n\n\n"
    partial, plain = "test_x = functools.partial(_body)\n", "def test_x():\n    assert False, 'declared failure'\n"
    assert refused(kit(tmp_path / "c1", {"test_x.py": head + swap.format(new="_noop") + plain}), CENSUS, NOT_RUN)
    assert seen(kit(tmp_path / "c2", {"test_x.py": head + partial}))
    r = kit(tmp_path / "case", {"test_x.py": head + swap.format(new="functools.partial(_noop)") + partial})
    assert refused(r, CENSUS, NOT_RUN), r          # F4: the partial's declared function never ran (the witness)


def test_f3_i4_a_helper_s_own_global_rebound_is_setup_under_r27(tmp_path):
    """Reinterpreted at F4 under weekly-train:R27 (R15 (a)): the swap is the test's setup and the
    declared test's own code ran, so it reads complete; the history below is what F3 refused. Item 4 (`d3_item04.sh`): the test calls `helper()`, which calls `body()`; a conftest fixture rebinds the
    module's `body` (two calls deep) to a no-op. Control: rebinding `helper` (one call deep) is refused."""
    test = "def body():\n    assert False, 'declared failure'\n\n\ndef helper():\n    body()\n\n\ndef test_x():\n    helper()\n"
    swap = "import pytest\n\n\n@pytest.fixture(autouse=True)\ndef _swap(request):\n    request.module.{n} = lambda: None\n"
    assert seen(kit(tmp_path / "c0", {"test_x.py": test}))
    assert complete(kit(tmp_path / "c1", {"test_x.py": test, "conftest.py": swap.format(n="helper")})), R27
    r = kit(tmp_path / "case", {"test_x.py": test, "conftest.py": swap.format(n="body")})
    assert complete(r), (R27, r)


CONF5 = "import pytest\n\n\n@pytest.fixture(autouse=True)\ndef _swap(request):\n    {swap}\n    yield\n"
INST5 = "class Body:\n    def __call__(self):\n{body}\n\n\nbody = Body()\n\n\ndef test_x():\n    body()\n"
KLASS5 = "class Body:\n    def __init__(self):\n{body}\n\n\ndef test_x(fn=Body):\n    fn()\n"
FAIL5 = "        assert False, 'declared failure'"


@pytest.mark.parametrize("test, swap", [
    (INST5, "request.module.Body.__call__ = lambda self: None"),     # a global callable instance's method
    (KLASS5, "request.module.Body.__init__ = lambda self: None"),    # a class default's constructor
], ids=["instance_method", "class_default_init"])
def test_f3_i5_a_rebound_method_of_the_member_s_class_is_setup_under_r27(tmp_path, test, swap):
    """Reinterpreted at F4 under weekly-train:R27 (R15 (a)): the swap is the test's setup and the
    declared test's own code ran, so it reads complete; the history below is what F3 refused. Item 5 (`d3_item05.sh`): a conftest fixture rebinds a method of a class the test reaches. Controls: the
    declared failure is seen with no conftest; the ordinary function rebind is refused; a conftest that changes
    nothing on a passing test reads complete."""
    func = "def body():\n    assert False, 'declared failure'\n\n\ndef test_x():\n    body()\n"
    assert seen(kit(tmp_path / "c1", {"test_x.py": INST5.format(body=FAIL5)}))
    assert complete(kit(tmp_path / "c2", {"test_x.py": func, "conftest.py": CONF5.format(
        swap="request.module.body = lambda: None")})), R27
    assert complete(kit(tmp_path / "c3", {"test_x.py": INST5.format(body="        return None"),
                                          "conftest.py": CONF5.format(swap="pass")}))
    r = kit(tmp_path / "case", {"test_x.py": test.format(body=FAIL5), "conftest.py": CONF5.format(swap=swap)})
    assert complete(r), (R27, r)


@pytest.mark.parametrize("src", [
    "class A:\n    def __call__(self):\n        return True\n\n\ndef test_x(fn=A()):\n    assert fn()\n",
    "import functools\n\n\n@functools.lru_cache()\ndef helper():\n    return True\n\n\ndef test_x(fn=helper):\n"
    "    assert fn()\n",
], ids=["callable_instance_default", "lru_cache_default"])
def test_f3_i7_a_correct_run_with_a_callable_default_reads_complete(tmp_path, src):
    """Item 7 (`d3_item07.sh`): a callable default the identity could not name by value (an instance, an
    `lru_cache` wrapper) was identified by something that differs between processes, so a correct run was refused
    "not the one the census collected". Control: a plain function default reads complete."""
    plain = "def helper():\n    return True\n\n\ndef test_x(fn=helper):\n    assert fn()\n"
    assert complete(kit(tmp_path / "c0", {"test_x.py": plain}))
    r = kit(tmp_path / "case", {"test_x.py": src})
    assert complete(r), r


def test_f3_i8_data_appended_to_a_helper_s_default_by_an_earlier_test_is_not_a_refusal(tmp_path):
    """Item 8 (`d3_item08.sh`): an earlier passing test appends to a list that a helper's default holds; every body
    runs and only ordinary data changes (B199's calibration), but D3's identity walked the list's elements, so the
    later test read "not the one the census collected" whenever the writer ran first. Control: the reader first."""
    head = "shared = []\n\n\ndef helper(data=shared):\n    return True\n\n\n"
    a, b = "def test_a():\n    shared.append(1)\n\n\n", "def test_b():\n    assert helper()\n\n\n"
    assert complete(kit(tmp_path / "c1", {"test_x.py": head + b + a}))
    r = kit(tmp_path / "case", {"test_x.py": head + a + b})
    assert complete(r), r


def test_f3_i8_a_callable_put_into_a_helper_s_default_list_is_setup_under_r27(tmp_path):
    """Reinterpreted at F4 under weekly-train:R27 (R15 (a)): the swap is the test's setup and the
    declared test's own code ran, so it reads complete; the history below is what F3 refused. The other side of item 8's repair: a container contributes the callables it holds, so a test whose helper's
    default list has its callable swapped by an earlier test is still refused. Control: nothing swapped."""
    src = ("def bad():\n    assert False, 'declared failure'\n\n\nhooks = [bad]\n\n\n"
           "def check(fns=hooks):\n    for f in fns:\n        f()\n\n\n"
           "def test_a():\n{swap}    assert True\n\n\ndef test_b():\n    check()\n")
    assert seen(kit(tmp_path / "c1", {"test_x.py": src.format(swap="")}))
    r = kit(tmp_path / "case", {"test_x.py": src.format(swap="    hooks[0] = lambda: None\n")})
    assert complete(r), (R27, r)


# --- D3 pre-read item 6: execution hooks -------------------------------------------------------------------------------

HEAD6 = ("import _pytest.python as P\nimport pytest\n\n\ndef _bypass(pyfuncitem):\n    return True\n\n\n"
         "@pytest.fixture(autouse=True, scope='session')\ndef _swap(pytestconfig):\n"
         "    pm = pytestconfig.pluginmanager\n    orig = P.pytest_pyfunc_call\n{setup}    yield\n{teardown}")
REREG6 = "    pm.unregister(P)\n    P.pytest_pyfunc_call = {fn}\n    pm.register(P, 'python')\n"
BAD = {"test_x.py": "def test_x():\n    assert False, 'declared failure'\n"}


def test_f3_i6_pytest_s_own_run_hook_replaced_and_restored_is_refused(tmp_path):
    """Item 6 (`d3_item06.sh`): a session fixture re-registers pytest's own `_pytest.python` with its
    `pytest_pyfunc_call` replaced (after collection), and restores it before the session ends, so neither the
    collector-time nor the end-of-run machinery check saw it; the declared failing body never ran. Controls: the
    same re-registration unchanged sees the failure; the replacement never restored is refused."""
    conf = lambda s, t: {**BAD, "conftest.py": HEAD6.format(setup=s, teardown=t)}
    assert seen(kit(tmp_path / "c1", conf(REREG6.format(fn="orig"), REREG6.format(fn="orig"))))
    assert refused(kit(tmp_path / "c2", conf(REREG6.format(fn="_bypass"), "    pass\n")),
                   "pytest's own collection or run code was changed")
    r = kit(tmp_path / "case", conf(REREG6.format(fn="_bypass"), REREG6.format(fn="orig")))
    assert refused(r, "pytest's own collection or run code was changed"), r


def test_f3_i6_an_execution_hook_registered_under_a_pytest_like_module_name_is_refused(tmp_path):
    """A variant of item 6 found while building it: a member registers a module object it names `_pytest.…`, whose
    `pytest_pyfunc_call` is the member's own function. D3 judged an execution hook by its plugin's module name only.
    Control: the same module registered with no execution hook sees the failure."""
    conf = ("import types\n\n\ndef _bypass(pyfuncitem):\n    return True\n\n\n"
            "def pytest_configure(config):\n    fake = types.ModuleType('_pytest.fake_exec')\n{attach}"
            "    config.pluginmanager.register(fake, 'fake_exec')\n")
    assert seen(kit(tmp_path / "c1", {**BAD, "conftest.py": conf.format(attach="")}))
    r = kit(tmp_path / "case", {**BAD, "conftest.py": conf.format(attach="    fake.pytest_pyfunc_call = _bypass\n")})
    assert refused(r, "implements pytest_pyfunc_call"), r


# --- D3 pre-read item 9: a KEEP line's release digest ------------------------------------------------------------------

ROW9 = dict(path=".claude/skills/held/SKILL.md", op="hold", kind="unattributed", authored_lines=0, pre="b" * 64)


@pytest.mark.parametrize("given", [{"source_sha256": ""}, {"source_sha256": "None"}, {"source_sha256": "absent"},
                                   {"source_sha256": "not-a-digest"}, {"sha256": "", "source_sha256": "c" * 64},
                                   {"source_sha256": "C" * 64}, {"sha256": "c" * 64, "source_sha256": "d" * 64}],
                         ids=["empty", "None", "absent", "not_a_digest", "empty_sha_falls_through", "upper_hex",
                              "two_disagree"])
def test_f3_i9_a_keep_line_needs_a_64_hex_release_digest(given):
    """Item 9 (`d3_item09.sh`): an unattributed hold whose release digest is an empty or non-digest string was
    rendered as a KEEP instruction ("release sha256 " with nothing after it). Controls: a missing digest is refused
    and a 64-hex digest is rendered."""
    IM = load("item_meaning")
    render = lambda **f: IM.meaning(dict(ROW9, **f)).instruction(dict(ROW9, **f))
    with pytest.raises(IM.UnknownClassification):
        render()
    assert ("c" * 64) in render(source_sha256="c" * 64) and ("c" * 64) in render(sha256="c" * 64)
    with pytest.raises(IM.UnknownClassification):
        render(**given)


# --- FWK-OVSR11's member baseline (it-consultant, both interpreters): a fixture patching a library class ----------

PATCHED_LIBRARY = (
    "from pathlib import Path\n\nimport pytest\n\n\n@pytest.fixture\ndef home(tmp_path, monkeypatch):\n"
    "    monkeypatch.setattr(Path, 'home', classmethod(lambda cls: tmp_path))\n    return tmp_path\n\n\n"
    "def test_x(home):\n    assert Path.home() == home{fail}\n")


def test_f3_member_a_fixture_patching_a_library_class_the_test_names_is_not_a_refusal(tmp_path):
    """FWK-OVSR11's member baseline on the F3 WIP (`overseer_prereads/F3WIP_member_baseline_ovsr11/`, `8233b6a41`):
    it-consultant's `tests/test_wind_down_script_cov.py` read 9 "the function that ran is not the one the census
    collected" on Python 3.12 and 3.14. Its `wd` fixture monkeypatches `pathlib.Path.home` with the member's lambda,
    and the tests name `Path`: the identity treated `pathlib.Path` as the member's class once one of its attributes
    held the member's code, and walked it at run time only. Controls: the same test with the fixture's failure is seen
    failing; a member class whose method a fixture rebinds is still refused (item 5)."""
    assert seen(kit(tmp_path / "c1", {"test_x.py": PATCHED_LIBRARY.format(fail=" and False")}))
    assert refused(kit(tmp_path / "c2", {"test_x.py": "def test_x():\n    assert False\n", "conftest.py":
                       CONF5.format(swap="request.function.__code__ = (lambda: None).__code__")}), CENSUS, NOT_RUN)
    r = kit(tmp_path / "case", {"test_x.py": PATCHED_LIBRARY.format(fail="")})
    assert complete(r), r


BOUND = {
    "bound_at_module_level": ("def run(self):\n    assert False, 'declared failure'\n\n\nclass Helper:\n    pass\n\n\n"
                              "Helper.run = run\n\n\ndef test_x():\n    Helper().run()\n"),
    "library_subclass_attribute": ("import collections\n\n\ndef run(self):\n    assert False, 'declared failure'\n\n\n"
                                   "class Helper(collections.UserDict):\n    run = run\n\n\n"
                                   "def test_x():\n    Helper().run()\n"),
}


@pytest.mark.parametrize("name", sorted(BOUND))
def test_f3_member_a_member_class_whose_methods_are_bound_outside_its_body_is_setup_under_r27(tmp_path, name):
    """Reinterpreted at F4 under weekly-train:R27 (R15 (a)): the swap is the test's setup and the
    declared test's own code ran, so it reads complete; the history below is what F3 refused. FWK-OVSR11's lead on the class rule above: a member class with no function written in its own body (its method
    bound at module level, or a member subclass of a library class that only sets attributes) is still the member's,
    by its module, so a fixture swapping that method for a no-op is refused. Control: unswapped, the failure is seen.
    Guard row for the new class rule: no failing-first claim (the F3 WIP followed these classes)."""
    assert seen(kit(tmp_path / "c1", {"test_x.py": BOUND[name]}))
    r = kit(tmp_path / "case", {"test_x.py": BOUND[name], "conftest.py": CONF5.format(
        swap="request.module.Helper.run = lambda self: None")})
    assert complete(r), (R27, r)
