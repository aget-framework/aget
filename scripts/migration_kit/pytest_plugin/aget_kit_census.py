"""The kit's census collection module (C2a13, B195 finding 1). Loaded only by the independent `--collect-only` run
that `aget_kit_report` starts (`-p aget_kit_census`, no conftest, no other plugin): it records the id of every item
that collection creates, before any deselection, through the descriptor AGET_KIT_CENSUS_FD names (the kit's, C2a14)."""
import json
import os
import sys

_ids = []
_errors = []
_ident = {}
_disp = {}


_CODE_FIELDS = ("co_argcount", "co_posonlyargcount", "co_kwonlyargcount", "co_flags", "co_nlocals", "co_stacksize",
                "co_firstlineno", "co_name", "co_qualname", "co_names", "co_varnames", "co_freevars", "co_cellvars",
                "co_code", "co_linetable", "co_exceptiontable")


def _tag(t, b):
    return t + str(len(b)).encode() + b":" + b


def const_bytes(k):
    """A constant by its exact type and value, tagged and length-prefixed (`code_bytes`; F4: also a container's
    constant keys). An int is written in hex, which has no length limit (F4, FWK-OVSR11's F3 pre-read Codex 6: an
    int over 4300 decimal digits made `str()` raise, an unreadable identity). Any other type raises TypeError naming
    it."""
    import struct
    import types
    t = type(k)
    if k is None or k is Ellipsis:
        return _tag(b"N" if k is None else b"E", b"")
    if t is bool:
        return _tag(b"B", b"1" if k else b"0")
    if t is int:
        return _tag(b"I", format(k, "x").encode())
    if t is float:                    # F5 (B203 finding 2): the exact IEEE-754 bits; `hex()` wrote +nan and -nan alike
        return _tag(b"F", struct.pack(">d", k))
    if t is complex:
        return _tag(b"C", struct.pack(">dd", k.real, k.imag))
    if t is str:
        return _tag(b"S", k.encode("utf-8", "surrogatepass"))
    if t is bytes:
        return _tag(b"Y", k)
    if t is tuple:
        return _tag(b"T", b"".join(const_bytes(x) for x in k))
    if t is frozenset:
        return _tag(b"Z", b"".join(sorted(const_bytes(x) for x in k)))
    if t is slice:
        return _tag(b"L", const_bytes(k.start) + const_bytes(k.stop) + const_bytes(k.step))
    if isinstance(k, types.CodeType):
        return _tag(b"K", code_bytes(k))
    raise TypeError(f"a code constant of type {t.__module__}.{t.__qualname__}")


def resolve(module, qualname):
    """The object a module holds at a qualified name (`A.b.c`), or None (a `<locals>` name, a missing attribute)."""
    obj = module
    for part in (qualname or "").split("."):
        if not part or part.startswith("<"):
            return None
        obj = getattr(obj, part, None)
        if obj is None:
            return None
    return obj


def code_bytes(code):
    """F3 (FWK-OVSR9's member advisory, measured: 0 of 4 members complete on the F3 WIP): a code object as bytes,
    without `marshal`. Python 3.14 keeps constant slices in `co_consts`, which marshal formats below 5 cannot write
    (ValueError: an unreadable identity on every test that slices with constants), and formats from 3 on mark objects
    held elsewhere, which depends on the process. Here every field that decides what the code does is written by
    value, tagged and length-prefixed, and every constant by its exact type: None, Ellipsis, bool, int, float (its
    IEEE-754 bits, so -0.0 and each nan are exact), complex, str, bytes, tuple, frozenset (sorted), slice and nested code. The
    file name is left out (the item's own file is a field of its identity); `co_code` is the unspecialized bytecode,
    the same in a process that loaded the code from `__pycache__` and in one that compiled it. A constant of any other
    type raises TypeError naming the type: the identity is then unreadable, with that reason, and the test refused."""
    out = [_tag(name.encode(), const_bytes(getattr(code, name, None))) for name in _CODE_FIELDS]
    out.append(_tag(b"co_consts", b"".join(const_bytes(k) for k in code.co_consts)))
    return b"".join(out)


def declared_function(obj):
    """F4 (weekly-train:R27, R15 (a)): the declared test's own function: the collected object unwrapped through bound
    methods, `functools.partial` and `functools.wraps` (`__wrapped__`) to the innermost Python function, or None
    when there is none (a doctest, a plugin's item, a callable instance). A decorator that does not keep `__wrapped__`
    makes its wrapper the test's own function (a stated limit)."""
    import functools
    import types
    f, seen = obj, set()
    while id(f) not in seen:
        seen.add(id(f))
        if isinstance(f, functools.partial):
            f = f.func
        elif isinstance(f, types.MethodType):
            f = f.__func__
        elif isinstance(f, (staticmethod, classmethod)):
            f = f.__func__
        elif isinstance(f, types.FunctionType) and "__wrapped__" in vars(f):   # its own attribute, not a lookup
            f = vars(f)["__wrapped__"]
        else:
            break
    return f if isinstance(f, types.FunctionType) else None


def item_identity(item, root):
    """C2a14 (FWK-OVSR7's C2a14 pre-read 1): what an item will run, shared by the census and the run: its class, its
    function's file (relative to `root`) and first line, and a hash of what it runs.
    F4 (weekly-train:R27, the principal 2026-10-05 ~11:4x: "Prove the test's own code"; R15 (a)): the hash is the
    declared test's OWN code (`declared_function`, then `code_bytes`), never what it calls. Helpers, defaults, closure
    values, classes and globals the test reaches are its setup: changes made to them are not compared (stated). Each
    run of that code is then witnessed (`aget_kit_report`, sys.monitoring): the identity says which code was collected,
    the witness that it ran to an outcome. A test object with no Python function of its own is identified by its kind
    and has no witness (refused at the run). Nothing here depends on a process (no address, no PID, no reference count,
    no `__pycache__`)."""
    import hashlib
    obj = getattr(item, "obj", None) if hasattr(item, "function") or hasattr(item, "obj") else None
    kind = f"{type(item).__module__}.{type(item).__qualname__}"
    if obj is None:                       # not a Python test object (a doctest, a plugin's own item): its kind
        return [kind]
    func = declared_function(obj)
    if func is None:                      # a test object with no function of its own: named by its kind
        return [kind, "no own function"]
    code = func.__code__
    return [kind, os.path.relpath(code.co_filename, root), str(code.co_firstlineno),
            hashlib.sha256(code_bytes(code)).hexdigest()]


# C2a15 (B198 finding 1, second falsifier): pytest's own collection and run machinery, fingerprinted when this module
# is imported (before any test module or member conftest runs) and compared later. A test module that patches it
# (`_pytest.python.Module.collect = …`) changes the census and the run alike, so neither can prove the population:
# unsupported scope, refused (weekly-train:R15)
_MACHINERY_MODULES = ("_pytest.python", "_pytest.main", "_pytest.nodes", "_pytest.runner", "_pytest.fixtures",
                      "_pytest.skipping", "_pytest.mark.structures", "_pytest.doctest", "_pytest.unittest",
                      "_pytest.reports", "_pytest.hookspec", "pluggy._manager", "pluggy._hooks", "pluggy._callers")


def machinery_snapshot():
    """{owner.name: (object, its code)} for every function and method of pytest's collection and run modules."""
    import importlib
    import types
    snap = {}
    for mn in _MACHINERY_MODULES:
        try:
            m = importlib.import_module(mn)
        except Exception:
            continue
        owners = [(mn, m)] + [(f"{mn}.{k}", v) for k, v in vars(m).items()
                              if isinstance(v, type) and getattr(v, "__module__", "") == mn]
        for on, owner in owners:
            for k, v in list(vars(owner).items()):
                f = v.__func__ if isinstance(v, (classmethod, staticmethod)) else v
                f = getattr(f, "fget", f)
                if isinstance(f, types.FunctionType) and (owner is not m or f.__module__ == mn):
                    snap[f"{on}.{k}"] = (owner, k, v, f.__code__)
    return snap


def machinery_changed(snap):
    """The names in `snap` rebound, deleted, or whose code was replaced since the snapshot."""
    out = []
    for name, (owner, k, v, code) in snap.items():
        now = vars(owner).get(k)
        f = now.__func__ if isinstance(now, (classmethod, staticmethod)) else now
        f = getattr(f, "fget", f)
        if now is not v or getattr(f, "__code__", None) is not code:
            out.append(name)
    return out


_MACHINERY = machinery_snapshot()


def item_disposition(item):
    """C2a14 (pre-read 2-5; weekly-train:R15): the skip/xfail outcome pytest's own static evaluation of the item's
    marks gives, so a skip or xfail at run time is proven only when the census produces the same one."""
    from _pytest.skipping import evaluate_skip_marks, evaluate_xfail_marks
    s, x = evaluate_skip_marks(item), evaluate_xfail_marks(item)
    skip = s.reason if s else None
    if skip is None:
        # F4 (FWK-OVSR11's F4 WIP pre-read, codex 5): unittest's own `skip`/`skipIf`/`skipUnless` decorators are
        # decided when the module is imported, as a mark is, so the census evaluates them too (the method's, else its
        # class's); a skip raised at run time (`self.skipTest`, `raise SkipTest`) is still not proven
        for o in (getattr(item, "obj", None), getattr(getattr(item, "parent", None), "obj", None)):
            if getattr(o, "__unittest_skip__", False) is True:
                skip = str(getattr(o, "__unittest_skip_why__", ""))
                break
    return {"skip": skip, "xfail": x.reason if x else None, "run": x.run if x else None}


def pytest_itemcollected(item):
    """Record the collected id, declared-code identity and static disposition before deselection."""
    _ids.append(item.nodeid)
    root = str(item.config.rootpath)
    try:
        _ident[item.nodeid] = item_identity(item, root)
    except Exception as e:
        _ident[item.nodeid] = [f"unreadable ({type(e).__name__}: {str(e)[:80]})"]   # F3: with its reason
    try:
        _disp[item.nodeid] = item_disposition(item)
    except Exception as e:
        _disp[item.nodeid] = {"unreadable": type(e).__name__}


_SEEN = []


def pytest_collectstart(collector):
    """D2 (C2a15+C2e pre-read 7): compared as each collector starts too (a patch restoring itself inside its call)."""
    if not _SEEN:
        _SEEN.extend(machinery_changed(_MACHINERY))


def pytest_collectreport(report):
    """Record collection failures and any changed collection machinery after each collector."""
    if not _SEEN:                     # D2 (B199 finding 1): a patch restored before the end of collection is seen
        _SEEN.extend(machinery_changed(_MACHINERY))
    if report.failed:
        _errors.append(report.nodeid)


def pytest_collection_finish(session):
    """Writes the ids, the collection errors, and every plugin in this process that is neither pytest's own nor this
    module (a test module's `pytest_plugins` loads one: the census is then not independent of the run)."""
    import types
    plugins = []
    for pl in session.config.pluginmanager.get_plugins():
        mod = pl.__name__ if isinstance(pl, types.ModuleType) else (pl.__module__ if isinstance(pl, type)
                                                                     else type(pl).__module__)
        if mod in ("pytest", "_pytest", "pluggy", "aget_kit_census") or mod.startswith(("_pytest.", "pluggy.")):
            continue
        if isinstance(pl, types.ModuleType) and getattr(pl, "__file__", "").endswith("conftest.py"):
            plugins.append(f"conftest {pl.__file__}")
            continue
        plugins.append(mod)
    fd = os.environ.get("AGET_KIT_CENSUS_FD")       # C2a14 (B197 finding 3): the kit's descriptor, never a pathname
    import stat                                     # C2a15 (B198 finding 3): only the kit's pipe, never a file
    if fd and fd.isdigit() and stat.S_ISFIFO(os.fstat(int(fd)).st_mode):
        data = json.dumps({"ids": _ids, "errors": _errors, "plugins": sorted(set(plugins)),
                           "ident": _ident, "disp": _disp,
                           "machinery": list(dict.fromkeys(_SEEN + machinery_changed(_MACHINERY)))}).encode()     # C2a15 (B198 finding 1)
        n, out = 0, int(fd)
        while n < len(data):
            n += os.write(out, data[n:])
