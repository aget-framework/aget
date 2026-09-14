#!/usr/bin/env python3
"""A verdict that cannot be stated without the warrant that entitles it.

THE DEFECT CLASS THIS EXISTS TO CLOSE
-------------------------------------
Four independent review rounds over two instruments found what looked like eight defects. They
are one defect, eight times:

    THE INSTRUMENT CONVERTS A LIMIT OF ITS OWN INTO AN ASSERTION ABOUT ITS SUBJECT.

  our token list missed `chat`        -> "the runtime is not instructable"
  our check saw a declared token      -> "the runtime is non-interactive"
  our parser could not read the help  -> "the runtime declares no surface"
  our reader found the runtime named  -> "a governed invocation occurred"
  our regex matched a substring       -> "an instruction surface exists"
  our resolver found a class          -> "the validator would accept this packet"
  our dict overwrote a duplicate key  -> "the evidence resolves"
  our read escaped the root           -> "the evidence is present"

Each was repaired individually and the next round found the next instance. Patching instances
does not converge, because nothing in the code distinguished "I observed X" from "I failed to
observe not-X". This module makes that distinction structural.

THE RULE
--------
A **definite** verdict (YES / NO / PASS / FAIL) may only be constructed with a `warrant`: the
positive observation that entitles it. "I looked and did not find" is NOT a warrant for NO --
it is a limit, and a limit yields an **indefinite** verdict (UNKNOWN / UNAVAILABLE) carrying
the `limit` that produced it.

    Verdict.no("the runtime declares no surface")            # refused: no warrant
    Verdict.unknown(limit="this parser did not recognise the help layout")   # correct
    Verdict.no(warrant="the executable does not exist on PATH")             # correct

The asymmetry is deliberate and is the whole content of the module: **absence of evidence is
constructible only as UNKNOWN.** An instrument may always report what it could not do; it may
never promote that into a fact about the thing it was pointed at.

USAGE IN A CHECK
----------------
    from warranted_verdict import Verdict

    def level(...) -> Verdict:
        if not shutil.which(name):
            return Verdict.no(warrant=f"{name} does not resolve on PATH")   # observed absence
        surfaces = parse(help_text)
        if not surfaces:
            return Verdict.unknown(limit="no recognised layout in --help")  # OUR limit
        ...

Every verdict renders as its state plus the sentence that entitles it, so a reader always sees
which of the two they are being told.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any

YES, NO, PASS, FAIL = "YES", "NO", "PASS", "FAIL"
UNKNOWN, UNAVAILABLE, INERT = "UNKNOWN", "UNAVAILABLE", "INERT"

DEFINITE = frozenset({YES, NO, PASS, FAIL})
INDEFINITE = frozenset({UNKNOWN, UNAVAILABLE, INERT})


class UnwarrantedVerdict(ValueError):
    """A definite verdict was constructed without the observation that entitles it."""


@dataclass(frozen=True)
class Verdict:
    state: str
    warrant: str | None = None
    limit: str | None = None
    detail: dict[str, Any] = field(default_factory=dict)

    def __post_init__(self) -> None:
        if self.state in DEFINITE:
            if not (self.warrant or "").strip():
                raise UnwarrantedVerdict(
                    f"{self.state} is a claim about the subject and requires a warrant -- the "
                    f"positive observation that entitles it. If the reason is that this "
                    f"instrument could not establish the opposite, that is a LIMIT, and the "
                    f"verdict is {UNKNOWN}.")
            if self.limit:
                raise UnwarrantedVerdict(
                    f"{self.state} carries a limit ({self.limit!r}). A verdict resting on "
                    f"anything this instrument could not do is indefinite by construction.")
        elif self.state in INDEFINITE:
            if not (self.limit or "").strip():
                raise UnwarrantedVerdict(
                    f"{self.state} must name the limit that produced it, so a reader can tell "
                    f"an unexamined subject from an examined one.")
        else:
            raise UnwarrantedVerdict(f"unknown verdict state {self.state!r}")

    # -- constructors, named so the call site reads as what it is ------------------
    @classmethod
    def yes(cls, warrant: str, **detail: Any) -> "Verdict":
        return cls(YES, warrant=warrant, detail=detail)

    @classmethod
    def no(cls, warrant: str, **detail: Any) -> "Verdict":
        """NO asserts the subject LACKS the property. Requires observing the lack."""
        return cls(NO, warrant=warrant, detail=detail)

    @classmethod
    def passed(cls, warrant: str, **detail: Any) -> "Verdict":
        return cls(PASS, warrant=warrant, detail=detail)

    @classmethod
    def failed(cls, warrant: str, **detail: Any) -> "Verdict":
        return cls(FAIL, warrant=warrant, detail=detail)

    @classmethod
    def unknown(cls, limit: str, **detail: Any) -> "Verdict":
        """The instrument could not establish the answer. Never a pass, never a NO."""
        return cls(UNKNOWN, limit=limit, detail=detail)

    @classmethod
    def unavailable(cls, limit: str, **detail: Any) -> "Verdict":
        return cls(UNAVAILABLE, limit=limit, detail=detail)

    @classmethod
    def inert(cls, limit: str, **detail: Any) -> "Verdict":
        """The check did not fire. Distinct from passing."""
        return cls(INERT, limit=limit, detail=detail)

    @property
    def is_definite(self) -> bool:
        return self.state in DEFINITE

    @property
    def why(self) -> str:
        return self.warrant or self.limit or ""

    def as_dict(self) -> dict[str, Any]:
        """Dict form. `why` carries the warrant or the limit, whichever applies, so a consumer
        that only reads `why` still sees the sentence entitling the verdict -- while `warrant`
        and `limit` stay separate for a consumer that needs to know WHICH it is."""
        return {"verdict": self.state, "warrant": self.warrant, "limit": self.limit,
                "why": self.why or None, **self.detail}

    def __str__(self) -> str:
        kind = "warrant" if self.is_definite else "limit"
        return f"{self.state} ({kind}: {self.why})"


def worst(verdicts: list["Verdict"]) -> str:
    """Aggregate without laundering: any FAIL dominates, then any indefinite state.

    INERT does not dominate -- a check that did not fire is not a check that failed -- but it
    also never contributes a pass on its own.
    """
    states = [v.state for v in verdicts]
    if FAIL in states or NO in states:
        return FAIL if FAIL in states else NO
    if UNAVAILABLE in states:
        return UNAVAILABLE
    if UNKNOWN in states:
        return UNKNOWN
    return PASS if PASS in states else (YES if YES in states else INERT)
