#!/usr/bin/env python3
"""R3, instruction fidelity: what a session is told, permitted and judged on follows from one meaning table per
classification, never from a bare label. One module; every classifier and every consumer of a payload item uses it.

A classification is the pair (op, kind). `kind` is defined only for op in {hold, merged, kept}; every other op has the
single kind "-". For those three ops the kind is the first line that matches (they cannot overlap, and the order is
stated so that no reader has to check it):
  1. no-source     no release source bytes exist for the path (`authored_lines` is not computed: stored null);
  2. authored      source bytes exist and `authored_lines` is an integer >= 1;
  3. unattributed  source bytes exist and `authored_lines == 0`;
  4. otherwise (source bytes exist, `authored_lines` missing, negative or not an integer): no kind, and meaning()
     refuses the item.
Pairings: hold takes any of the three kinds, merged only authored, kept only unattributed or no-source.

R3 holds when (1) MEANING has exactly one row per classification; (2) every consumer reads that row and nothing else;
(3) a classification with no row is refused by every consumer (an exception, REFUSED or INCONCLUSIVE), never passed,
written or omitted silently; (4) a relabel is allowed only for a transition the table lists, and every field derived
from the old meaning is derived again.

Two further closed label sets live here for the same reason (design read 2, D-3): the receiver modes a packet may
name, and the payload expectations a template may state. A value outside either is refused by its consumer.

Stated limits: whether a session follows its instruction cannot be enforced (R3 makes the instruction true and bounds
the session by permission and after-run identity); merge quality is not judged (for hold/authored only the survival
of every authored line is checked); a KEEP item's difference record is not checked (no tool reads the receipt for it).
"""
import hashlib
from typing import Callable, NamedTuple, Optional

KINDLESS = "-"
KINDS = ("no-source", "authored", "unattributed")
RECEIVER_MODES = ("migrate", "track-skills")          # a packet receiver with no `mode` is "migrate"
PAYLOAD_EXPECTATIONS = ("present", "absent")


class UnknownClassification(ValueError):
    """An item whose (op, kind) has no row in MEANING, or whose fields contradict its kind; refused."""


def classify_kind(op, source_present, authored_lines):
    """The kind of an item (lines 1 to 4 of the predicate), or None (line 4). Only for op in hold/merged/kept;
    every other op returns "-"."""
    if op not in ("hold", "merged", "kept"):
        return KINDLESS
    if not source_present:
        return "no-source"
    if isinstance(authored_lines, bool) or not isinstance(authored_lines, int) or authored_lines < 0:
        return None
    return "authored" if authored_lines >= 1 else "unattributed"


def authored_ids(current, upstream_lines):
    """sha256 of each stripped authored line (a non-blank line no upstream version holds), in file order. The
    after-run check requires every one of them to survive a merge (M4: preservation by identity, not by count)."""
    if current is None:
        return []
    return [hashlib.sha256(ln.strip().encode()).hexdigest()
            for ln in current.decode("utf-8", "replace").splitlines()
            if ln.strip() and ln.strip() not in upstream_lines]


class Meaning(NamedTuple):
    """One row: what the session is told (None: nothing), whether it gets an Edit rule, whether the path is in the
    session's write set and in the scope check, whether the principal's apply writes it, and how the after-run check
    judges it: "release" (the release digest), "pre" (unchanged from `pre`), "authored_ids" (every authored line
    survives), "absent", "inconclusive", or "none" (not examined)."""
    instruction: Optional[Callable]
    edit: bool
    write_set: bool
    scope: bool
    apply_writes: bool
    after_run: str


def _merge(i):
    return (f"MERGE {i['path']}: your copy has {i.get('authored_lines')} line(s) of your own. Take the release changes "
            f"from {i.get('staged')} and keep every line of your own. Record the merge.")


def _keep_unattributed(i):
    # D3 (B200 finding 4): the release digest is the packet item's `sha256` or the protected list's `source_sha256`;
    # a row with neither cannot be instructed and is refused, never rendered with None
    # F3 (FWK-OVSR9's D3 pre-read 9): a digest is 64 lowercase hex; "", "None" or any other string is refused, never
    # rendered, and two given digests must agree (an empty `sha256` does not fall through to `source_sha256`)
    given = [i[k] for k in ("sha256", "source_sha256") if i.get(k) is not None]
    if not given:
        raise UnknownClassification(f"{i.get('path')}: unattributed hold with no release digest")
    if not all(isinstance(d, str) and len(d) == 64 and all(c in "0123456789abcdef" for c in d) for d in given):
        raise UnknownClassification(f"{i.get('path')}: unattributed hold whose release digest is not a sha256 "
                                    f"({str(given[0])[:20]!r})")
    if len(set(given)) > 1:
        raise UnknownClassification(f"{i.get('path')}: unattributed hold with two different release digests")
    digest = given[0]
    return (f"KEEP {i['path']}: your copy may hold changes of your own that no line count shows. Keep your copy, do "
            "not take the release bytes, and record the difference (your sha256 against the release sha256 "
            f"{digest}) in your receipt.")


def _keep_no_source(i):
    return (f"KEEP {i['path']}: no release source exists for this path. Keep your copy and record its sha256 in your "
            "receipt.")


def _leave(i):
    return (f"LEAVE {i['path']}: not migrated in this run ({i.get('why')}). Do not write, edit, copy over, delete or "
            "follow it; record it in your receipt as not migrated.")


def _delete(i):
    return f"DELETE {i['path']}: the release removes it. Run: git rm {i['path']}"


def _keep_hold_delete(i):
    return f"KEEP {i['path']}: the release removes it but your copy has your own changes. Keep it; record it."


MEANING = {
    ("write", KINDLESS): Meaning(None, False, True, True, True, "release"),
    ("write-upstream", KINDLESS): Meaning(None, False, True, True, True, "release"),
    ("verify", KINDLESS): Meaning(None, False, False, False, False, "release"),
    ("noop", KINDLESS): Meaning(None, False, False, False, False, "none"),
    ("delete", KINDLESS): Meaning(_delete, False, False, True, False, "absent"),
    ("hold-delete", KINDLESS): Meaning(_keep_hold_delete, False, False, False, False, "pre"),
    ("unsafe", KINDLESS): Meaning(_leave, False, False, False, False, "inconclusive"),
    ("hold", "authored"): Meaning(_merge, True, True, True, False, "authored_ids"),
    ("hold", "unattributed"): Meaning(_keep_unattributed, False, False, False, False, "pre"),
    ("hold", "no-source"): Meaning(_keep_no_source, False, False, False, False, "pre"),
    ("merged", "authored"): Meaning(None, False, False, False, False, "authored_ids"),
    ("kept", "unattributed"): Meaning(None, False, False, False, False, "pre"),
    ("kept", "no-source"): Meaning(None, False, False, False, False, "pre"),
    # the protected-write list's own ops (prepare_batch, apply_protected); never in a launch packet
    ("hold-line", KINDLESS): Meaning(None, False, False, False, False, "none"),
    ("replace-line", KINDLESS): Meaning(None, False, False, False, True, "release"),
    ("rewrite-claude-ignore", KINDLESS): Meaning(None, False, False, False, True, "release"),
}

# Relabels the table lists (R3 clause 4): (from_op, to_op). Anything else is refused.
RELABELS = {("hold", "merged"), ("hold", "kept"), ("noop", "verify"), ("write", "kept"), ("write-upstream", "kept"),
            ("hold", "write")}


def kind_of(item):
    """The item's recorded kind, or the kind its fields give (for items prepared before kinds were recorded, the
    stored `kind` is required for hold/merged/kept)."""
    op = item.get("op")
    if op not in ("hold", "merged", "kept"):
        return KINDLESS
    return item.get("kind")


def meaning(item):
    """The row for an item; raises UnknownClassification for a missing row or for fields that contradict the kind."""
    if not isinstance(item, dict):
        raise UnknownClassification(f"not an item: {item!r}")
    op, kind = item.get("op"), kind_of(item)
    if not isinstance(op, str) or not isinstance(kind, (str, type(None))):   # B151 finding 6: never an unhashable key
        raise UnknownClassification(f"{item.get('path')}: op {op!r} or kind {kind!r} is not a string")
    row = MEANING.get((op, kind))
    if row is None:
        raise UnknownClassification(f"{item.get('path')}: no meaning for ({op!r}, {kind!r})")
    if kind == "no-source" and (item.get("authored_lines") is not None or item.get("staged")):
        raise UnknownClassification(f"{item.get('path')}: no-source with authored lines or staged bytes")
    n = item.get("authored_lines")
    whole = isinstance(n, int) and not isinstance(n, bool)     # B151 finding 5: the classifier's predicate
    if kind == "authored" and not (whole and n >= 1):
        raise UnknownClassification(f"{item.get('path')}: authored with authored_lines {item.get('authored_lines')!r}")
    if kind == "unattributed" and not (whole and n == 0):
        raise UnknownClassification(f"{item.get('path')}: unattributed with authored_lines "
                                    f"{item.get('authored_lines')!r}")
    return row


def relabel(item, new_op, **fields):
    """Relabel an item to `new_op` only for a listed transition; the kind is derived again and the placing fields
    of the old meaning (command, mkdir, hash_command) are removed (the caller derives them again). Raises
    UnknownClassification."""
    meaning(item)                     # B151 finding 4: the old row must have a meaning before it is relabelled
    if (item.get("op"), new_op) not in RELABELS:
        raise UnknownClassification(f"{item.get('path')}: relabel {item.get('op')!r} -> {new_op!r} is not listed")
    out = {k: v for k, v in item.items() if k not in ("command", "mkdir", "hash_command")}
    out.update(fields, op=new_op)
    out["kind"] = classify_kind(new_op, bool(out.get("staged")), out.get("authored_lines"))
    if out["kind"] == "no-source":
        out["authored_lines"] = None
    if new_op in ("hold", "merged", "kept") and out["kind"] is None:
        raise UnknownClassification(f"{item.get('path')}: no kind after relabel to {new_op!r}")
    if new_op not in ("hold", "merged", "kept"):
        out.pop("kind", None)
    meaning(out)
    return out


def receiver_mode(r):
    """The receiver's mode from the closed set (absent means migrate); raises UnknownClassification otherwise."""
    mode = r.get("mode", "migrate") if isinstance(r, dict) else None
    if mode not in RECEIVER_MODES:
        raise UnknownClassification(f"receiver {r.get('aget') if isinstance(r, dict) else r!r}: unknown mode "
                                    f"{mode!r}; known: {RECEIVER_MODES}")
    return mode


def expectation(path, want):
    """A template's payload expectation from the closed set; raises UnknownClassification otherwise."""
    if want not in PAYLOAD_EXPECTATIONS:
        raise UnknownClassification(f"{path}: unknown payload expectation {want!r}; known: {PAYLOAD_EXPECTATIONS}")
    return want
