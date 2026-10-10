"""write_scope allow-list rules: scope() reads a receiver's declared write_scope, refused() judges one path.

Extracted unchanged from the supervisor's build_r0917b_path_list.py (2026-09-30 rehearsal): the checker needs only
these two functions, and the source module also carries a hard-coded list of Agets and past releases that the kit's
release-literal guard rightly refuses."""
import pathlib
import re


def scope(root):
    """These seats declare write_scope as an ALLOW-LIST plus a catch-all deny.

    My first pass read only `forbidden_paths` and reported "68 refused" at every seat because
    every list ends with `*`. That was the right number for the wrong reason, and the wrong
    reason would have framed R-0917-B as "extend the permitted set by a few classes."

    The governing structure is `write_scope.allowed_paths` with `enforcement: strict`; the `*`
    in `forbidden_paths` is the catch-all that closes it. So the real question is not which
    payload paths match a deny rule -- it is WHICH PAYLOAD PATHS FALL OUTSIDE THE ALLOW-LIST,
    and at these seats the allow-list is seven `.aget/` subtrees that the payload never touches.
    """
    vj = pathlib.Path(root) / '.aget/version.json'
    if not vj.exists():
        return [], [], 'none', False
    raw = vj.read_text(errors='replace')
    allow = re.search(r'"allowed_paths"\s*:\s*\[(.*?)\]', raw, re.S)
    deny = re.search(r'"forbidden_paths"\s*:\s*\[(.*?)\]', raw, re.S)
    enf = re.search(r'"enforcement"\s*:\s*"(\w+)"', raw)
    carve = bool(re.search(r'permitted_paths|maintenance_carveout', raw, re.I))
    return (re.findall(r'"([^"]+)"', allow.group(1)) if allow else [],
            re.findall(r'"([^"]+)"', deny.group(1)) if deny else [],
            enf.group(1) if enf else 'unstated', carve)


def _globs(path, rule):
    r = rule.rstrip('*').rstrip('/')
    return bool(r) and (path == r or path.startswith(r + '/'))


def refused(path, allow, deny):
    """Outside the allow-list, or named by a deny rule. Returns the governing reason."""
    if any(_globs(path, a) for a in allow):
        return None
    named = [d for d in deny if d != '*' and (_globs(path, d) or d == path)]
    if named:
        return 'outside allow-list; also named by %s' % ', '.join(named)
    return 'outside allow-list (catch-all `*`)' if '*' in deny else 'outside allow-list'
