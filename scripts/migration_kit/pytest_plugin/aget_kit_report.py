"""The kit's pytest report plugin (B185 finding 1, C2a7): pytest's own outcome records, written as JSON lines.

Why: pytest's terminal summary is display text. A node id may hold ` - `, and pytest omits a failure message that does
not fit the terminal, so no reading of that text fixes where an id ends (B180, B182, B185). This plugin writes what
pytest itself hands to its reporters: every collect and test report's `nodeid`, phase and outcome, as a JSON string
(json escapes every character of the id, so the id read back is the id pytest built), between a `start` record naming
the invocation (its arguments and folder) and a `finish` record naming its exit status and how many events it wrote.

It is loaded only by the kit, through the environment result_binding.report_env() builds:
`PYTEST_ADDOPTS=-p aget_kit_report` and this folder first on PYTHONPATH, with the report path, the run's token and the
member's own values of those two variables. At import, before pytest reads any conftest, it takes those variables out
of os.environ and puts the member's own values back, so member code and any pytest a test starts see the member's
environment, and a nested pytest neither loads this plugin nor writes to the report.

At the end of the terminal summary it prints one line, `aget-kit-report: pytest <invocation>`, so a consumer that holds
one run's output (a session's tool result) can name which invocation in the report that output came from. The report,
not that line, is the result; the line only selects. Not an authentication: code running inside pytest can read and
change this module and the report (result_binding's stated limit: R2 binds results, it does not authenticate them).
"""
import fnmatch
import inspect
import json
import os
import shlex
import stat
import threading
import types
import uuid

import pytest

_PATH = os.environ.pop("AGET_KIT_REPORT", None)
_TOKEN = os.environ.pop("AGET_KIT_REPORT_TOKEN", None)
_ORIG = os.environ.pop("AGET_KIT_ORIG", None)
try:
    for _k, _v in (json.loads(_ORIG) if _ORIG else {}).items():
        if _k in ("PYTEST_ADDOPTS", "PYTHONPATH"):
            if _v is None:
                os.environ.pop(_k, None)
            else:
                os.environ[_k] = _v
except (ValueError, AttributeError, TypeError):
    _PATH = None                     # the member's environment cannot be put back: write nothing (the run then reads
                                     # as having no result, never as a clean one)

INV = uuid.uuid4().hex
MARK = "aget-kit-report: pytest "
_fd = None
_n = 0
_collected = 0
_ran = set()
_deselected = []


def _write(rec):
    if _fd is None:
        return
    rec = {**rec, "token": _TOKEN, "inv": INV}
    os.write(_fd, (json.dumps(rec, sort_keys=True) + "\n").encode())


def pytest_configure(config):
    """Open the report the kit created (append, never through a link, never created here)."""
    global _fd
    if not _PATH or not _TOKEN or _fd is not None or hasattr(config, "workerinput"):
        return
    try:      # B188 finding 2: never blocks on a FIFO; anything but a regular file leaves the plugin silent (not known)
        fd = os.open(_PATH, os.O_WRONLY | os.O_APPEND | getattr(os, "O_NOFOLLOW", 0) | getattr(os, "O_NONBLOCK", 0))
    except OSError:
        return
    if stat.S_ISREG(os.fstat(fd).st_mode):
        _fd = fd
    else:
        os.close(fd)


def pytest_sessionstart(session):
    """Write the invocation start record, including its arguments, working directory and last-failed flag."""
    p = session.config.invocation_params
    lf = bool(session.config.getoption("lf", False))     # B190 finding 2: a last-failed run selects a subset
    _write({"rec": "start", "pid": os.getpid(), "args": [str(a) for a in p.args], "dir": str(p.dir), "lf": lf})


def pytest_deselected(items):
    """B190 finding 2: every test pytest deselects (`-k`, `-m`, `--deselect`, `--lf`, from the command or addopts)."""
    _deselected.extend(i.nodeid for i in items)


_itemcount = 0
_narrowed = []
_ignored = []
# pytest's own defaults, used when its parser does not expose them (C2a10, FWK-OVSR6's C2a10 pre-read 1)
_DEFAULTS = {"python_files": ["test_*.py", "*_test.py"], "python_classes": ["Test"], "python_functions": ["test"],
             "norecursedirs": ["*.egg", ".*", "_darcs", "build", "CVS", "dist", "node_modules", "venv", "{arch}"]}


@pytest.hookimpl(hookwrapper=True)
def pytest_ignore_collect(collection_path, config):
    """C2a10 (FWK-OVSR6's C2a10 pre-read 1, reproduced): every path any implementation (pytest's own, a plugin's, a
    conftest's) answers "ignore" for, before collection; the reader then needs no list of the ways to narrow."""
    outcome = yield
    try:
        if outcome.get_result():
            _ignored.append(str(collection_path))
    except Exception:
        _ignored.append(f"{collection_path} (the ignore hook raised)")


def _default(config, name):
    try:
        return list(config._parser._inidict[name][2])
    except (AttributeError, KeyError, IndexError, TypeError):
        return _DEFAULTS[name]


# F4 (weekly-train:R27, R15 (a); REVW11's B202 proof obligations): the witness that each declared test's own collected
# code ran to an outcome in its own call phase. sys.monitoring (Python 3.12+) on a tool id the kit claims: PY_START and
# PY_RETURN set locally on each collected declared code object only, PY_UNWIND (global-only) switched on just for the
# length of each call phase. An event counts only for the code of the item whose call phase is running: a setup or
# teardown call, a helper, or a test calling another test's function never witnesses anything.
_witness = {}        # nodeid -> {"code": …, "start": n, "end": None|"returned"|"raised", "raised": a raise seen in ANY
                     # paired activation; F6: "open" {id(frame): frame} activations begun in its call and not yet
                     # ended, "unfinished" how many were still open when the call ended, "thread" own code ran on
                     # another thread during its call, "unpaired" an outcome came from an activation not begun in it}
_in_call = [None]    # (nodeid, code, the thread running the call phase) while that item's call phase runs
_TOOL = []           # [the claimed tool id] or [the reason none is available]
_called = {}         # nodeid -> its call phase's outcome, as reported (in this process or, under xdist, a worker)
_lost = []           # nodeids during whose call the kit's tool id or callbacks were taken or changed
_TOOL_NAME = "aget-kit-witness"


def _watched_frame(code):
    """F4 (FWK-OVSR11's F4 WIP pre-read, Codex 1): an event counts only when the interpreter raised it from a frame of
    the watched code itself; a callback a test calls by hand runs under that test's frame. F6 (B204 finding 1): that
    frame is returned, so a start and an outcome are paired by the activation (the frame), not only by the code."""
    import sys
    try:
        f = sys._getframe(2)
    except ValueError:
        return None
    return f if f.f_code is code else None


def _on_start(code, offset):
    c = _in_call[0]
    if c is not None and code is c[1]:
        f = _watched_frame(code)
        if f is None:
            return
        w = _witness[c[0]]
        if threading.get_ident() != c[2]:   # F6: an activation on another thread cannot be paired with this call
            w["thread"] = True
            return
        w["start"] += 1
        w["open"][id(f)] = f              # held until it ends or the call ends, so its id is never reused meanwhile


def _on_end(how):
    def cb(code, offset, value):
        c = _in_call[0]
        if c is not None and code is c[1]:
            f = _watched_frame(code)
            if f is None:
                return
            w = _witness[c[0]]
            if threading.get_ident() != c[2]:
                w["thread"] = True
                return
            if w["open"].pop(id(f), None) is not f:   # F6 (B204 finding 1): an outcome of an activation that did
                w["unpaired"] = True                  # not begin in this call (setup) never counts
                return
            w["end"] = how
            if how == "raised":           # F5 (B203 finding 1): kept, never overwritten by a later return
                w["raised"] = True
    return cb


_CALLBACKS = {}      # event -> the kit's callback, to check they are still registered


def _tool_intact(t):
    """The tool id is still the kit's and every callback still its own (FWK-OVSR11's F4 WIP pre-read, Codex 1 and agy
    6: a test that frees, re-takes or re-registers the kit's tool). Re-registering returns the previous callback,
    which must be the kit's; nothing changes when it is."""
    import sys
    mon = sys.monitoring
    try:
        if mon.get_tool(t) != _TOOL_NAME:
            return False
        return all(mon.register_callback(t, ev, cb) is cb for ev, cb in _CALLBACKS.items())
    except (ValueError, TypeError):
        return False


def _witness_tool():
    """The kit's sys.monitoring tool id, claimed once (3, else 4), or the reason there is none."""
    if not _TOOL:
        import sys
        mon = getattr(sys, "monitoring", None)
        if mon is None:
            _TOOL.append("this Python has no sys.monitoring (3.12 or later is needed)")
            return _TOOL[0]
        for t in (3, 4):
            try:
                if mon.get_tool(t) is not None:
                    continue
                mon.use_tool_id(t, _TOOL_NAME)
            except ValueError:
                continue
            E = mon.events
            _CALLBACKS.update({E.PY_START: _on_start, E.PY_RETURN: _on_end("returned"),
                               E.PY_UNWIND: _on_end("raised")})
            for ev, cb in _CALLBACKS.items():
                mon.register_callback(t, ev, cb)
            _TOOL.append(t)
            break
        else:
            _TOOL.append("no free sys.monitoring tool id (3 and 4 are taken)")
    return _TOOL[0]


def _witness_collect(item):
    """At collection: the item's declared code (`aget_kit_census.declared_function`), watched from now on."""
    try:
        import aget_kit_census
        f = aget_kit_census.declared_function(getattr(item, "obj", None)) \
            if hasattr(item, "function") or hasattr(item, "obj") else None
    except Exception:                 # noqa: BLE001 — unknown is never a witness
        f = None
    code = getattr(f, "__code__", None)
    _witness[item.nodeid] = {"code": code, "start": 0, "end": None, "raised": False, "open": {}, "unfinished": 0,
                             "thread": False, "unpaired": False}
    t = _witness_tool()
    if code is not None and isinstance(t, int):
        import sys
        E = sys.monitoring.events
        try:
            sys.monitoring.set_local_events(t, code, E.PY_START | E.PY_RETURN)
        except ValueError:            # the tool was freed meanwhile: never a member's error, a named refusal
            _lost.append(item.nodeid)


def pytest_itemcollected(item):
    """C2a10 (B192 finding 3): every item collection produced, before any hook removes one."""
    global _itemcount
    _itemcount += 1
    _itemids.add(item.nodeid)
    _witness_collect(item)            # F4 (R27): the declared code each item will be witnessed running
    if getattr(item, "callspec", None) is not None:     # C2a13r (pre-read M2): parameters as pytest made them
        _param_base[item.nodeid] = item.nodeid[:len(item.nodeid) - len(item.name)] + item.originalname


_param_base = {}


_itemids = set()
_census = []


_PRODUCER_HOOKS = ("pytest_collection", "pytest_collect_file", "pytest_collect_directory", "pytest_pycollect_makemodule",
                   "pytest_pycollect_makeitem", "pytest_make_collect_report", "pytest_generate_tests")


_registered_producers = []
_registered_execution = []   # D3 (B200 finding 1 (a)): execution-hook implementers, recorded when registered

# D2 (B199 finding 1 (a): execution-phase omissions are inside the population class): a member conftest or a plugin
# that is not pytest's own and implements a hook able to replace or skip a test's body cannot be accounted for, so a
# run where one is registered at any point is not proven (unsupported scope, weekly-train:R15)
_EXECUTION_HOOKS = ("pytest_pyfunc_call", "pytest_runtest_protocol", "pytest_runtestloop", "pytest_runtest_call")
_CFG = []
_dispatch = []          # D2: items whose `runtest` was replaced on the instance
_machinery_seen = []    # D2: a machinery change seen after any collector (a patch later restored is still seen)


def pytest_plugin_registered(plugin, manager):
    """C2a14 (FWK-OVSR7's add-on 9): a producer hook is recorded when its plugin is registered (a historic hook, so
    plugins registered before this one are replayed), so a plugin that unregisters itself before the census scan
    is still seen."""
    try:
        for h in _PRODUCER_HOOKS:
            for impl in getattr(manager.hook, h).get_hookimpls():
                if impl.plugin is plugin:
                    _registered_producers.append((h, plugin))
        # D3 (B200 finding 1 (a)): an execution hook is recorded at registration too, so a member plugin that
        # unregisters itself before the end of the run is still seen (D2 scanned only the final hook list)
        for h in _EXECUTION_HOOKS:
            for impl in getattr(manager.hook, h).get_hookimpls():
                if impl.plugin is plugin:
                    _registered_execution.append((h, _impl_owner(impl)))
    except Exception:                                    # unknown is never empty
        _registered_producers.append(("(registration unreadable)", plugin))


def _plugin_module(pl):
    """A plugin's module: a module's name, a class's own module (pytest registers classes, e.g. legacypath-tmpdir),
    else the instance's class's module."""
    if isinstance(pl, types.ModuleType):
        return pl.__name__
    return pl.__module__ if isinstance(pl, type) else type(pl).__module__


def _own(mod):
    """Whether a plugin module is pytest's own or the kit's."""
    # C2a14 (FWK-OVSR7's add-on 8): exact modules, never a name prefix (`pluggy_hider` is a member's plugin)
    return mod in ("pytest", "_pytest", "pluggy", "aget_kit_report", "aget_kit_census") or mod.startswith(
        ("_pytest.", "pluggy."))


def _own_dirs():
    import _pytest
    import pluggy
    return tuple(os.path.realpath(os.path.dirname(m.__file__)) + os.sep for m in (_pytest, pluggy)) + (
        os.path.realpath(os.path.dirname(__file__)) + os.sep,)


def _impl_owner(impl):
    """F3 (FWK-OVSR9's D3 pre-read 6, reproduced: a conftest re-registered pytest's own `_pytest.python` with its
    `pytest_pyfunc_call` replaced): an execution hook's owner is its plugin's module and, for a plugin that reads as
    pytest's own or the kit's, the file of the function that implements the hook; a function whose code is not in
    pytest's, pluggy's or the kit's own files is named by that file, so it is not own; F4: so is one that is not the
    object at its declared module and name."""
    mod = _plugin_module(impl.plugin)
    if not _own(str(mod)):
        return mod
    code = getattr(getattr(impl, "function", None), "__code__", None)
    if code is None:
        return f"(no code for {getattr(impl, 'function', None)!r:.40})"
    f = os.path.realpath(code.co_filename)
    if not f.startswith(_own_dirs()):
        return f"code at {f}"
    # F4 (FWK-OVSR11's F3 pre-read, Codex 1: a member function whose code object names `_pytest/python.py` was
    # trusted): a function that reads as pytest's, pluggy's or the kit's own must also BE the object its declared
    # module (itself loaded from pytest's, pluggy's or the kit's files) holds at its qualified name; a forged code object resolves to the original, never to itself
    fn = getattr(impl.function, "__func__", impl.function)
    import sys
    import aget_kit_census
    hm = sys.modules.get(getattr(fn, "__module__", None) or "")
    hf = getattr(hm, "__file__", None)
    home = aget_kit_census.resolve(hm, getattr(fn, "__qualname__", ""))
    if not (isinstance(hf, str) and os.path.realpath(hf).startswith(_own_dirs())) \
            or getattr(home, "__func__", home) is not fn:
        return f"code at {f}, not the object at {getattr(fn, '__module__', None)}.{getattr(fn, '__qualname__', None)}"
    return mod


_census0 = {}
try:                       # C2a15 (B198 finding 1): taken when the kit's plugin loads, before conftests and test modules
    import aget_kit_census as _akc
    _MACHINERY = _akc.machinery_snapshot()
except Exception:          # an unavailable snapshot is reported at the end, never a silent pass
    _MACHINERY = None
# C2a14 (B197 finding 1): the environment as the kit plugin found it (the member's own values put back above), taken
# before any member conftest is imported; the census runs from it, never from a process a conftest has changed
_ENV0 = dict(os.environ)


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_load_initial_conftests(early_config, parser, args):
    """C2a14 (B197 finding 1): the census is taken here, BEFORE the member's conftests are imported, so a conftest's
    import-time changes (environment, files it writes, imports it patches) cannot reach it. Collection-time ignores
    are subtracted when the run's collection is done (`_census_missing`)."""
    if _PATH and _TOKEN and not hasattr(early_config, "workerinput"):
        try:
            _census0.update(_run_census(early_config))
        except Exception as e:                       # unknown is never empty
            _census0["unavailable"] = f"{type(e).__name__}: {str(e)[:120]}"
    yield


def _run_census(early_config):
    """The independent collection (C2a13), run before the member's conftests: `pytest --collect-only` with
    `--noconftest`, autoload off, PYTEST_ADDOPTS/PYTEST_PLUGINS and the report environment dropped, from the
    environment the kit plugin found, with an ini holding only the discovery patterns, `norecursedirs`, `testpaths` and
    `pythonpath`; same rootdir, positional roots, `--pyargs` and `--import-mode`. Returns {"result": …} or
    {"unavailable": why}."""
    import subprocess
    import sys
    import tempfile
    ns = early_config.known_args_namespace
    ini_names = ("python_files", "python_classes", "python_functions", "norecursedirs", "testpaths", "pythonpath")
    vals = {n: [str(x) for x in early_config.getini(n)] for n in ini_names}   # `pythonpath` holds absolute paths
    if any(any(c.isspace() for c in x) for v in vals.values() for x in v):
        return {"unavailable": "a discovery pattern holds whitespace"}
    env = {k: v for k, v in _ENV0.items() if k not in (
        "AGET_KIT_REPORT", "AGET_KIT_REPORT_TOKEN", "AGET_KIT_ORIG", "PYTEST_ADDOPTS", "PYTEST_PLUGINS")}
    here = os.path.dirname(os.path.abspath(__file__))
    env["PYTHONPATH"] = here + (os.pathsep + env["PYTHONPATH"] if env.get("PYTHONPATH") else "")
    env.update(PYTEST_DISABLE_PLUGIN_AUTOLOAD="1", PYTHONDONTWRITEBYTECODE="1")
    with tempfile.TemporaryDirectory(prefix="aget-kit-census-") as tmp:
        ini = os.path.join(tmp, "census.ini")
        with open(ini, "w") as fh:
            fh.write("[pytest]\n" + "".join(f"{n} = {' '.join(v)}\n" for n, v in vals.items() if v))
        # C2a14 (B197 finding 3): the census writes through a DESCRIPTOR the kit created, never through a pathname.
        # C2a15 (B198 finding 3): that descriptor is the write end of a PIPE, so there is no storage to share: no
        # inode a test module could link before the census writes. The kit drains the read end while the census runs
        # and takes only what arrived once the census ended and every write end closed
        import threading
        rd, wr = os.pipe()
        env["AGET_KIT_CENSUS_FD"] = str(wr)
        chunks = []

        def drain():
            while True:
                b = os.read(rd, 1 << 20)
                if not b:
                    return
                chunks.append(b)
        reader = threading.Thread(target=drain, daemon=True)
        reader.start()
        cmd = [sys.executable, "-m", "pytest", "--collect-only", "-q", "--noconftest", "-p", "no:cacheprovider",
               "--continue-on-collection-errors", "-p", "aget_kit_census", "-c", ini,
               f"--rootdir={early_config.rootpath}", f"--import-mode={getattr(ns, 'importmode', 'prepend')}",
               *(["--pyargs"] if getattr(ns, "pyargs", False) else []),
               # C2a14 (FWK-OVSR7's C2a13 second pass 2): the run's doctest collection is collected by the census too
               # (a conftest.py is never imported by the census, not even as a doctest module: it would run there)
               *(["--doctest-modules", "--ignore-glob=*conftest.py"] if getattr(ns, "doctestmodules", False) else []),
               *[f"--doctest-glob={g}" for g in (getattr(ns, "doctestglob", None) or [])],
               "--", *[str(a) for a in (getattr(ns, "file_or_dir", None) or [])]]
        try:
            try:
                p = subprocess.run(cmd, cwd=str(early_config.invocation_params.dir), env=env, capture_output=True,
                                   text=True, timeout=900, pass_fds=(wr,))
            finally:
                os.close(wr)
            reader.join(timeout=30)
            if reader.is_alive():       # a process the census left behind still holds the write end
                return {"unavailable": "the census output stayed open after the census ended"}
            if p.returncode not in (0, 1, 5):
                tail = ((p.stdout + p.stderr).strip().splitlines() or [""])[-1][:120]
                return {"unavailable": f"collection exit {p.returncode}: {tail}"}
            return {"result": json.loads(b"".join(chunks).decode("utf-8"))}
        except (OSError, ValueError, subprocess.SubprocessError) as e:
            return {"unavailable": f"no census output: {type(e).__name__}"}
        finally:
            if not reader.is_alive():
                os.close(rd)


def _census_missing(session):
    """C2a13 (B195 finding 1, REVW9's census ruling, collection form; FWK-OVSR6's C2a12 second pass: the AST form
    re-implemented pytest's collection rules, and each place it differed let a hook hide a test). An independent
    collection of the same roots, which no member conftest or plugin takes part in: `pytest --collect-only` in a
    subprocess with `--noconftest`, plugin autoload off, PYTEST_ADDOPTS/PYTEST_PLUGINS dropped and the ini replaced by
    one carrying only the discovery patterns and `norecursedirs` (no addopts); same rootdir, roots (`--pyargs` kept),
    and every path pytest's ignore hook skipped in this run passed as `--ignore` (those are witnessed as narrowing).
    The kit's census module records every item that collection creates; each must be an item this run created
    (exact id: parameters, nested and unittest classes, linked folders and node-id roots are pytest's own). Returns the
    ids this run did not create. Unknown is never empty: a census that cannot run (exit other than 0 or 5, timeout,
    unreadable output) is returned as `census unavailable (…)`. Scope: tests produced by conftests or plugins are not
    in this collection (the producer set is witnessed instead); hooks in the test modules themselves are part of the
    declared population."""
    import subprocess
    import sys
    import tempfile
    config = session.config
    # B196 finding 1 ("exact accounting or refusal of unsupported scope"): a member conftest or a plugin that is not
    # pytest's own and implements a hook able to create or hide items makes the population one the census cannot
    # account for (a producer's membership is not witnessed by its name). Removal by `modifyitems` is counted as
    # `dropped`; ignore hooks are witnessed as narrowing
    # C2a13r (FWK-OVSR7's pre-read H1): the REGISTERED implementations of each hook are read, so a function bound by
    # `@hookimpl(specname=…)`, a wrapper and a runtime `register` all count, not attribute names
    unsupported = {}
    seen = [(h, impl.plugin) for h in _PRODUCER_HOOKS for impl in getattr(config.pluginmanager.hook, h).get_hookimpls()]
    for h, plugin in seen + _registered_producers:      # C2a14 (add-on 9): also those registered and then removed
        mod = _plugin_module(plugin)
        if _own(mod):
            continue
        label = getattr(plugin, "__file__", None) or mod
        label = os.path.relpath(label, str(config.invocation_params.dir)) if os.path.isabs(label) else label
        if h not in unsupported.setdefault(label, []):
            unsupported[label].append(h)
    if unsupported:
        return [f"census unavailable (producer {lab} implements {', '.join(hs)})" for lab, hs in unsupported.items()]
    if any(" (the ignore hook raised)" in p for p in _ignored):
        return ["census unavailable (an ignore hook raised)"]
    if _swapped:
        return [f"census unavailable ({n[:100]}: an item collection did not create)" for n in _swapped]
    if _census0.get("unavailable"):
        return [f"census unavailable ({_census0['unavailable']})"]
    ids = _census0.get("result")
    if not (isinstance(ids, dict) and all(isinstance(ids.get(k), list) and all(isinstance(i, str) for i in ids[k])
                                          for k in ("ids", "errors", "plugins"))):
        return ["census unavailable (malformed or missing census output)"]
    if ids["plugins"]:        # C2a13r (pre-read H2): a test module's `pytest_plugins` loads code into the census too
        return [f"census unavailable (the census itself loaded plugin {p[:80]}, so it is not independent)"
                for p in ids["plugins"]]
    if ids.get("machinery"):  # C2a15 (B198 finding 1): pytest's collection code was patched in the census process
        return [f"census unavailable (pytest's own collection code was changed during collection: {n[:80]})"
                for n in ids["machinery"][:5]]
    # C2a14: the census collected before this run's conftests and ignore hooks; what pytest's ignore hook skipped in
    # this run (witnessed as narrowing) is subtracted here, by path relative to the rootdir
    root = str(config.rootpath)
    skipped = tuple(os.path.relpath(p, root).replace(os.sep, "/") for p in set(_ignored))

    def ignored(nodeid):
        path = nodeid.split("::", 1)[0]
        return any(path == s or path.startswith(s.rstrip("/") + "/") for s in skipped)
    # a file the census could not collect (an import that needs a conftest, say) has an unknown population unless the
    # run could not collect it either
    unseen = [e for e in ids["errors"] if e not in _collect_failed and not ignored(e)]
    if unseen:
        return [f"census unavailable (the census could not collect {e[:100]}, which this run collected)"
                for e in unseen]
    if not all(isinstance(ids.get(k), dict) for k in ("ident", "disp")):
        return ["census unavailable (the census recorded no item identities)"]
    _census_items.update(ident=ids["ident"], disp=ids["disp"])
    ids = [i for i in ids["ids"] if not ignored(i)]
    # every census id must be created exactly. C2a13r (pre-read H3; B196 #1, "exact accounting or refusal of
    # unsupported scope"): a census id this run created only as parameterized items (parameters added outside the
    # census: a conftest fixture's `params=`, say) cannot be accounted for case by case, so it is unsupported scope;
    # parameters are read from the run item's own callspec, never from a `[` in the id (pre-read M2)
    based = set(_param_base.values())
    out = []
    for i in dict.fromkeys(ids):
        if i in _itemids:
            continue
        out.append(f"census unavailable ({i[:100]}: parameters added outside the census)" if i in based else i)
    return out


def _given(args, flag):
    """The values `flag` takes on the invocation's own command line (`flag X` or `flag=X`)."""
    out = []
    for i, a in enumerate(args):
        if a == flag and i + 1 < len(args):
            out.append(args[i + 1])
        elif a.startswith(flag + "="):
            out.append(a.split("=", 1)[1])
    return out


def _selection_narrowed(session):
    """C2a10 (B192 finding 3): the inputs that narrowed what pytest collected without the invocation's own command
    line declaring them: `--ignore`/`--ignore-glob` from ini or addopts, a conftest's `collect_ignore(_glob)`, roots
    taken from `testpaths`, or a path written into addopts. Each is named; the reader treats any as a subset."""
    config = session.config
    args = [str(a) for a in config.invocation_params.args]
    out = []
    for opt, flag in (("ignore", "--ignore"), ("ignore_glob", "--ignore-glob")):
        declared = _given(args, flag)
        out += [f"{flag} {v}" for v in (config.getoption(opt, None) or []) if str(v) not in declared]
    # C2a14 (FWK-OVSR7's C2a14 pre-read 7): a conftest's `collect_ignore` narrows only through the paths pytest's
    # ignore hook actually skipped (listed below as `ignored …`); one that matched nothing is no narrowing
    source = getattr(config, "args_source", None)
    if source is not None and getattr(source, "name", "") == "TESTPATHS":
        out.append("roots from testpaths " + " ".join(str(x) for x in config.getini("testpaths")))
    try:
        added = shlex.split(" ".join(config.getini("addopts") or [])) + shlex.split(os.environ.get("PYTEST_ADDOPTS", ""))
    except ValueError:
        added = ["(unparsable addopts)"]
    base = str(config.invocation_params.dir)
    # C2a10 (FWK-OVSR6's C2a10 pre-read 1): what any ignore hook left out, beyond pytest's default skipped folders,
    # a virtual environment, and the command line's own `--ignore`/`--ignore-glob`
    keep = _default(config, "norecursedirs")
    declared = [os.path.abspath(os.path.join(base, v)) for v in _given(args, "--ignore")]
    globs = _given(args, "--ignore-glob")
    for p in sorted(set(_ignored)):
        name = os.path.basename(p.rstrip("/"))
        # C2a13 (found re-running C2a12's suite; C2a12 second pass): pytest's own ignore hook also skips `__pycache__`,
        # so a run that met one read as narrowed (an availability defect, intermittent in the parallel runner)
        if name == "__pycache__" or any(fnmatch.fnmatch(name, pat) for pat in keep) or any(
                p == d or p.startswith(d + os.sep) for d in declared):
            continue
        if any(fnmatch.fnmatch(p, g) for g in globs) or os.path.exists(os.path.join(p, "pyvenv.cfg")):
            continue
        out.append(f"ignored {os.path.relpath(p, base)}")
    # discovery patterns other than pytest's defaults, unless the command line sets them itself (`-o name=...`)
    for name in ("python_files", "python_classes", "python_functions"):
        if [str(x) for x in config.getini(name)] != _default(config, name) and not any(
                a.startswith(name + "=") for a in _given(args, "-o") + _given(args, "--override-ini")):
            out.append(f"{name} = {' '.join(str(x) for x in config.getini(name))}")
    # C2a11 (B194 finding 6): a plugin blocked anywhere but the command line (`-p no:X` in addopts/PYTEST_ADDOPTS)
    out += [f"plugin blocked {added[i + 1][3:] if w == '-p' else w[5:]}" for i, w in enumerate(added)
            if (w == "-p" and i + 1 < len(added) and added[i + 1].startswith("no:")) or w.startswith("-pno:")]
    # a word that is the value of the option before it (`--deselect X`, `-k X`, ...) is not a path to collect
    valued = {"--deselect", "--ignore", "--ignore-glob", "-k", "-m", "-p", "-c", "-o", "--override-ini", "-W",
              "--rootdir", "--confcutdir", "--basetemp", "--maxfail", "--tb", "--durations", "--deselect-file",
              "--junitxml", "--junit-xml", "--log-file", "--cov", "--cov-report", "--cov-config", "-n", "--dist",
              "--junit-prefix", "--log-level", "--log-format", "--color", "--import-mode", "--capture", "--pyargs"}
    out += [f"addopts path {w}" for i, w in enumerate(added)
            if not w.startswith("-") and (i == 0 or added[i - 1] not in valued) and w not in args
            and os.path.exists(os.path.join(base, w.split("::")[0]))]
    return out


_suppressed = []
_selection = {}


@pytest.hookimpl(hookwrapper=True)
def pytest_pycollect_makeitem(collector, name, obj):
    """C2a11 (B194 finding 6): a test-pattern function or class that a collection hook turned into no item (`[]` or
    None) is a suppressed candidate. Items never created are invisible to every count, so they are recorded here."""
    outcome = yield
    try:
        res = outcome.get_result()
    except Exception:
        return
    if res not in (None, []):
        return
    try:
        fn = inspect.isfunction(obj) and collector.funcnamefilter(name)
        cls = inspect.isclass(obj) and collector.classnamefilter(name)
    except Exception:
        fn, cls = False, True
    if fn or cls:
        _suppressed.append(f"{collector.nodeid}::{name}")


def _selection_witness(session):
    """C2a11 (B194 finding 6, REVW9's accepted route): the effective selection of this run, every element typed as a
    list of strings, so a standing policy can be compared with its baseline: roots, every path an ignore hook
    excluded, discovery patterns, testpaths, plugins blocked (`-p no:X` from the command line, addopts or
    PYTEST_ADDOPTS), plugin distributions loaded, and whether plugin autoload is disabled."""
    config = session.config
    base = str(config.invocation_params.dir)
    try:
        added = shlex.split(" ".join(config.getini("addopts") or [])) + shlex.split(os.environ.get("PYTEST_ADDOPTS", ""))
    except ValueError:
        added = ["(unparsable addopts)"]
    words = [str(a) for a in config.invocation_params.args] + added
    blocked = sorted({w.split("no:", 1)[1] for i, w in enumerate(words)
                      if (w.startswith("-pno:") or (w.startswith("no:") and i and words[i - 1] == "-p"))})
    try:
        dists = sorted({f"{d.project_name}" for _, d in config.pluginmanager.list_plugin_distinfo()})
    except Exception:
        dists = ["(unavailable)"]
    return {"roots": [os.path.relpath(str(a), base) for a in config.args],
            "ignored": sorted({os.path.relpath(p, base) for p in _ignored            # C2a13r (pre-read P7): pytest's
                               if os.path.basename(p.rstrip(os.sep)) != "__pycache__"}),   # own skip is no policy
            "python_files": [str(x) for x in config.getini("python_files")],
            "python_classes": [str(x) for x in config.getini("python_classes")],
            "python_functions": [str(x) for x in config.getini("python_functions")],
            "testpaths": [str(x) for x in config.getini("testpaths")],
            "blocked": blocked, "plugins": dists,
            # C2a12 (B195 finding 1): every ACTIVE producer, not only installed distributions: each registered
            # plugin's name (a local `-p module`, a conftest by its path relative to the invocation folder)
            # C2a13 (C2a12 second pass M3): a plugin registered without a name (pluggy names it by `id()`, pytest's
            # own documented idiom) is recorded by its module or class, never dropped
            "producers": sorted({(os.path.relpath(n, base) if os.path.isabs(str(n)) else str(n)) if not str(n).isdigit()
                                 else (pl.__name__ if isinstance(pl, types.ModuleType)
                                       else f"{type(pl).__module__}.{type(pl).__qualname__}")
                                 for n, pl in config.pluginmanager.list_name_plugin() if pl is not None}),
            "autoload": ["off" if os.environ.get("PYTEST_DISABLE_PLUGIN_AUTOLOAD") else "on"]}


_SKIPMARKS = ("skip", "skipif", "xfail")


_census_items = {}
_run_ident = {}
_run_skips = {}


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_runtest_call(item):
    """C2a14 (FWK-OVSR7's C2a14 pre-read 1): the identity of what is about to run, compared at the end with the
    census's item of that id (a conftest that swapped the function, or the item, is caught)."""
    try:
        import aget_kit_census
        _run_ident[item.nodeid] = aget_kit_census.item_identity(item, str(item.config.rootpath))
    except Exception as e:
        _run_ident[item.nodeid] = [f"unreadable ({type(e).__name__}: {str(e)[:80]})"]   # F3: with its reason
    # F3 (FWK-OVSR9's D3 pre-read 6): pytest's run code compared as each test is about to run, so a change a fixture
    # makes after collection and restores before the session ends is still seen
    if _MACHINERY is not None and not _machinery_seen:
        try:
            _machinery_seen.extend(aget_kit_census.machinery_changed(_MACHINERY))
        except Exception as e:        # noqa: BLE001 — an unreadable check is reported, never a pass
            _machinery_seen.append(f"(the check raised {type(e).__name__})")
    if "runtest" in vars(item):       # D2 (B199 finding 1): the item's own dispatch replaced, not its class's
        _dispatch.append(item.nodeid)
    # D2 (FWK-OVSR9's D2 pre-read 1, reproduced): a unittest TestCase that overrides how its test method is run
    # (`run`, `__call__`, `debug`, `_callTestMethod`, …) can report a pass without running the body: not proven
    try:
        import unittest
        cls = getattr(getattr(item, "parent", None), "obj", None)
        if isinstance(cls, type) and issubclass(cls, unittest.TestCase):
            for name in ("run", "__call__", "debug", "_callTestMethod", "_callSetUp", "_callTearDown"):
                if getattr(cls, name, None) is not getattr(unittest.TestCase, name, None):
                    _dispatch.append(item.nodeid)
                    break
    except Exception:                 # noqa: BLE001 — unknown dispatch is not proven
        _dispatch.append(item.nodeid)
    # F4 (R27): the witness window is this item's call phase, and only it
    # A lost or changed tool never changes the member's test outcome (agy 6): every monitoring call here is guarded,
    # and the loss is a named refusal at the end
    w, t = _witness.get(item.nodeid), _witness_tool()
    if w is not None and w["code"] is not None and isinstance(t, int) and _tool_intact(t):
        import sys
        _in_call[0] = (item.nodeid, w["code"], threading.get_ident())
        try:
            sys.monitoring.set_events(t, sys.monitoring.events.PY_UNWIND)
        except ValueError:
            _lost.append(item.nodeid)
        try:
            yield
        finally:
            _in_call[0] = None
            w["unfinished"] += len(w["open"])   # F6: begun in its call, not ended in it (frames released here)
            w["open"].clear()
            if not _tool_intact(t):
                _lost.append(item.nodeid)
            else:
                try:
                    sys.monitoring.set_events(t, 0)
                except ValueError:
                    _lost.append(item.nodeid)
    else:
        if w is not None and w["code"] is not None and isinstance(t, int):
            _lost.append(item.nodeid)
        yield


def _late_unproven():
    """C2a14 (pre-read 1-5; weekly-train:R15), at the end of the run: a test that ran a function other than the one
    the census collected, and a test skipped or xfailed in any phase whose outcome and reason the census's own static
    evaluation of its marks does not give (a conftest's skip, helper or importorskip, a changed condition, a late
    marker) is not proven."""
    ident, disp = _census_items.get("ident") or {}, _census_items.get("disp") or {}
    # C2a15 (B198 finding 1): pytest's collection or run code changed in this process after the kit loaded
    changed = []
    try:
        import aget_kit_census
        changed = aget_kit_census.machinery_changed(_MACHINERY)
    except Exception as e:
        changed = [f"(the check raised {type(e).__name__})"]
    changed = list(dict.fromkeys(_machinery_seen + changed))
    pre = [f"pytest's own collection or run code was changed during the run: {n[:80]}" for n in changed[:5]]
    pre += [f"{n[:100]}: its runtest was replaced on the item, so its body is not proven to have run" for n in _dispatch]
    pre += [f"{n[:100]}: a test function defined in its module was not collected" for n in _module_unproven]
    found = list(_registered_execution)   # D3 (B200 finding 1 (a)): registered at any time, the final list as well
    if _CFG:                          # D2 (B199 finding 1 (a)): execution hooks from member code
        pm = _CFG[0].pluginmanager
        for h in _EXECUTION_HOOKS:
            found += [(h, _impl_owner(impl)) for impl in getattr(pm.hook, h).get_hookimpls()]
    for h, mod in dict.fromkeys((h, str(m)) for h, m in found):
        if not _own(mod):
            pre.append(f"a member plugin implements {h} ({mod[:60]}), so a test body is not proven to have run")
    # F4 (weekly-train:R27): each item that reached its call phase ran its own declared code to an outcome, as
    # witnessed in this process; an item with no witness here (an xdist worker ran it, the Python has no
    # sys.monitoring, no tool id was free, it has no function of its own) is not proven
    t = _witness_tool() if _called else None
    if _called and not isinstance(t, int):
        pre.append(f"the run's test bodies cannot be witnessed: {t}")
    elif _called:
        # Only a call phase reported PASSED needs the witness: a failure is already a failing id (a test failed before
        # its body ran, e.g. a missing import in a `mock.patch` decorator, is still a failure), and a reported skip is
        # judged by the skip/xfail checks below (proven static, or not proven)
        for n in sorted(dict.fromkeys(_lost)):
            pre.append(f"{n[:100]}: the kit's sys.monitoring tool was taken or changed during its call, so its run "
                       f"is not witnessed")
        CO_GEN = 0x20 | 0x80 | 0x100 | 0x200   # generator, coroutine, iterable coroutine, async generator
        for n in sorted(k for k, o in _called.items() if o == "passed"):
            w = _witness.get(n)
            if w is None or w["code"] is None:
                pre.append(f"{n[:100]}: it has no function of its own here (a doctest, a plugin's item, a run in "
                           f"another process), so its run is not witnessed")
            elif w["code"].co_flags & CO_GEN:    # Codex 2, agy 1-2: an activation is not attributable to this call
                pre.append(f"{n[:100]}: its own code is a generator or coroutine, whose run the witness cannot "
                           f"attribute to its call")
            elif w.get("thread"):        # F6 (B204 finding 1): no activation there can be paired with this call
                pre.append(f"{n[:100]}: its own code ran on another thread during its call, so that run cannot be "
                           f"paired with its call")
            elif w.get("unpaired"):
                pre.append(f"{n[:100]}: its own code's outcome came from a run that did not start in its call")
            elif not w["start"] or not w["end"]:
                pre.append(f"{n[:100]}: the declared test's own code did not run to an outcome in its call "
                           f"(started {w['start']}, ended {w['end']})")
            elif w.get("unfinished"):
                pre.append(f"{n[:100]}: its own code started a run in its call that did not finish in it")
            elif w["end"] == "raised" or w.get("raised"):   # agy 3; F5 (B203 finding 1): in ANY activation
                pre.append(f"{n[:100]}: the declared test's own code raised during its call, yet the call was "
                           f"reported passed")
    if not _census_items:
        return pre
    def unreadable(x):
        return str((x or [""])[0]).startswith("unreadable")
    # F3 (FWK-OVSR9's D3 pre-read 1): an identity that could not be read on either side proves nothing, even when the
    # two unreadable markers are equal; it is named with its reason (the census's first, else the run's)
    out = pre + [f"{n[:100]}: its identity could not be read "
                 f"({str((ident[n] if unreadable(ident[n]) else got)[0])[:120]}), so its body is not proven"
                 for n, got in _run_ident.items() if n in ident and (unreadable(got) or unreadable(ident[n]))]
    out += [f"{n[:100]}: the function that ran is not the one the census collected"
            for n, got in _run_ident.items() if n in ident and ident[n] != got
            and not (unreadable(got) or unreadable(ident[n]))]
    for n, (kind, reason) in _run_skips.items():
        d = disp.get(n) or {}
        want = d.get("skip") if kind == "skip" else d.get("xfail")
        ok = want is not None and reason in (want, f"Skipped: {want}", f"reason: {want}", f"[NOTRUN] {want}")
        if not ok:
            out.append(f"{n[:100]}: {kind} ({str(reason)[:60]}) not produced by the census's own evaluation")
    return out


_swapped = []


def pytest_collection_finish(session):
    """Record the selected population, selection policy and independent census for the completed collection."""
    global _collected
    _CFG[:] = [session.config]
    # C2a14 (add-on 7): an item collection never created (swapped in by modifyitems) cannot be accounted for
    _swapped[:] = [i.nodeid for i in session.items if i.nodeid not in _itemids]
    _collected = len(session.items)
    if not hasattr(session.config, "workerinput"):
        _narrowed[:] = _selection_narrowed(session)
        try:
            _selection.update(_selection_witness(session))
        except Exception as e:                   # no witness: the reader refuses a narrowed run without one
            _selection.clear()
            _narrowed.append(f"selection witness unavailable ({type(e).__name__})")
        try:                                     # C2a12 (B195 finding 1): the census; unknown is never empty
            _census[:] = _census_missing(session) if _fd is not None else []
        except Exception as e:
            _census[:] = [f"census unavailable ({type(e).__name__}: {str(e)[:120]})"]


@pytest.hookimpl(optionalhook=True)
def pytest_xdist_node_collection_finished(node, ids):
    """Under pytest-xdist the controller collects nothing itself; each worker reports the same collection."""
    global _collected
    _collected = len(ids)
    _itemids.update(ids)


def _event(nodeid, when, outcome):
    global _n
    if _fd is None:
        return
    _n += 1
    if when == "setup":
        _ran.add(nodeid)
    _write({"rec": "event", "nodeid": nodeid, "when": when, "outcome": outcome})


_collect_failed = set()


_module_unproven = []   # D2 (C2a15+C2e pre-read 7): a module's own test functions that collection did not yield


@pytest.hookimpl(hookwrapper=True)
def pytest_make_collect_report(collector):
    """D2 (C2a15+C2e pre-read 7; B199 finding 1): after a test module is collected, every function DEFINED in it at
    module level whose name pytest's `python_functions` would collect must be one of its items (by original name). A
    patch that hides a test and restores itself inside that one collect call, and a module-level change shared with
    the census, both leave the function in the module without an item: not proven (weekly-train:R15)."""
    outcome = yield
    try:
        if not isinstance(collector, pytest.Module):
            return
        rep = outcome.get_result()
        if rep.outcome != "passed":
            return
        mod = collector.obj
        got = {getattr(i, "originalname", None) or i.name for i in rep.result}
        for n, v in vars(mod).items():
            if (inspect.isfunction(v) and getattr(v, "__module__", None) == mod.__name__
                    and collector.funcnamefilter(n) and not hasattr(v, "_fixture_function_marker")
                    and not getattr(v, "_pytestfixturefunction", None) and n not in got
                    and getattr(v, "__test__", True) is not False):
                _module_unproven.append(f"{collector.nodeid}::{n}")
    except Exception as e:                                  # noqa: BLE001 — unknown is never "all collected"
        _module_unproven.append(f"{getattr(collector, 'nodeid', '?')}: the module check raised {type(e).__name__}")


def pytest_collectstart(collector):
    """D2 (C2a15+C2e pre-read 7, self-restoring patch): the machinery is also compared as each collector STARTS, so a
    patch that restores itself inside the collect call it replaced is seen before that call runs."""
    pytest_collectreport(None)


def pytest_collectreport(report):
    # D2 (B199 finding 1, restored collection): the machinery is compared after EVERY collector, so a patch made by one
    # module's import and restored before the end of collection is still seen
    """Detect changed collection machinery and record failed collectors before the suite runs."""
    if not _machinery_seen and _MACHINERY is not None:
        try:
            import aget_kit_census
            _machinery_seen.extend(aget_kit_census.machinery_changed(_MACHINERY))
        except Exception as e:
            _machinery_seen.append(f"(the check raised {type(e).__name__})")
    if report is not None and report.failed:
        _collect_failed.add(report.nodeid)
        _event(report.nodeid, "collect", "failed")


def pytest_runtest_logreport(report):
    """Record each phase outcome and retain runtime skips and call outcomes for witness comparison."""
    _event(report.nodeid, report.when, report.outcome)
    if report.when == "call":         # F4 (R27): every call phase needs its witness, wherever it ran
        _called[report.nodeid] = report.outcome
    if report.skipped and report.nodeid not in _run_skips:     # C2a14 (pre-read 2-5): every skip and xfail, any phase
        if hasattr(report, "wasxfail"):
            _run_skips[report.nodeid] = ("xfail", report.wasxfail)
        else:
            lr = report.longrepr
            _run_skips[report.nodeid] = ("skip", lr[2] if isinstance(lr, tuple) and len(lr) == 3 else str(lr))


_session = None


@pytest.hookimpl(tryfirst=True)
def pytest_sessionfinish(session, exitstatus):
    """Retain the session for the final exit record written after session-finish hooks complete."""
    global _session
    _session = session


@pytest.hookimpl(hookwrapper=True, tryfirst=True)
def pytest_unconfigure(config):
    """C2a10 (B192 finding 1): the finish record is written when pytest unconfigures, after every `pytest_sessionfinish`
    implementation and wrapper has run, so it holds the status pytest returns (C2a9's `trylast` sessionfinish ordered
    plain hooks only; a member's wrapper set the status after it). A later change (a member's own unconfigure) is
    caught where the kit ran pytest itself, by comparing with the process's exit (`report_failures(exit_code=…)`)."""
    yield
    if _session is not None:
        _write({"rec": "finish", "exit": int(_session.exitstatus), "events": _n, "collected": _collected,
                "ran": len(_ran), "deselected": list(_deselected), "narrowed": list(_narrowed),
                "suppressed": list(_suppressed), "selection": dict(_selection),
                "census": list(_census) + [f"census unavailable ({x[:160]})" for x in _late_unproven()],  # C2a14
                # C2a10 (B192 finding 3): items collection produced that neither ran nor were deselected
                "dropped": max(_itemcount - _collected - len(set(_deselected)), 0)})   # distinct ids (pre-read 4)


def pytest_terminal_summary(terminalreporter):
    """Print this invocation's report marker when the kit report descriptor is available."""
    if _fd is not None:
        terminalreporter.write_line(MARK + INV)
