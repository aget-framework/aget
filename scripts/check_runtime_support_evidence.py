#!/usr/bin/env python3
"""Report runtime support evidence at three levels that must not be collapsed.

WHY THIS EXISTS
---------------
A pre-release research finding at the private framework-manager seat (not shipped here) tabulated a runtime's
"version installed" alongside whether it is "named in the portability initiative", and read a
version string for the declared successor as evidence about that successor. Two distinct
errors hide in that shape, and both were made:

  1. **A launcher is not the agent.** The observed version resolved, through a symlink, to an
     Electron DESKTOP launcher inside an `.app` bundle. That is an observation about a desktop
     application, not about a terminal agent.
  2. **Installed is not supported.** R9 says it plainly -- *"The binary is present and executes
     here. It does not establish that the tool remains a supported target."* -- and the
     initiative's re-target nonetheless cited "both fallback runtimes confirmed live" as
     portability evidence.

The framework's verification discipline "looks inward" (R9's own words), so a claim that is
true at the seat and stale at the vendor passes every local check. This command exists so the
three questions are answered separately and an answer to the cheap one cannot be mistaken for
an answer to the expensive one.

THE THREE LEVELS
----------------
  L1 INSTALLED    an executable resolves on PATH and reports a version.
                  Says nothing about whether it can be instructed or is supported.
  L2 INSTRUCTABLE the runtime exposes a non-interactive instruction surface -- the subcommand
                  through which a governed invocation would be issued.
  L3 GOVERNED     a bounded governed invocation actually ran and left a receipt.

**L1 does not imply L2; L2 does not imply L3.** Each is reported on its own evidence, and a
level with no evidence is UNKNOWN -- never NO, and never silently promoted.

CONTROL BOUNDARY (CAP-CCP)
--------------------------
This command is READ-ONLY. It resolves paths, reads `--version` / `--help`, and reads receipt
files. It performs **no** installation, no authentication flow, no configuration mutation and
no governed invocation. L3 is therefore **reported from a receipt, never produced here**:
asking a runtime to prove itself by running it is exactly the state-changing act the boundary
forbids. A missing receipt reads UNKNOWN, which is the honest state.

USAGE
  python3 scripts/check_runtime_support_evidence.py --runtime antigravity --runtime gemini
  python3 scripts/check_runtime_support_evidence.py --config runtimes.json --json
  python3 scripts/check_runtime_support_evidence.py --runtime codex --receipts .aget/logs/iagetc

EXIT CODES
  0  every named runtime reached L3
  1  at least one runtime is below L3 with a definite NO at some level
  2  at least one level is UNKNOWN and nothing is a definite NO
  3  inputs unusable
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import stat
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from typing import Any

from warranted_verdict import Verdict  # noqa: E402

YES, NO, UNKNOWN = "YES", "NO", "UNKNOWN"

# Non-interactive instruction surfaces, by runtime family. A runtime absent from this map is
# not thereby "no surface" -- it is UNKNOWN, because we have not been told what to look for.
INSTRUCTION_SURFACES = {
    "gemini": ["--prompt", "-p"],
    "codex": ["exec"],
    "claude": ["-p", "--print"],
    # `chat` is Antigravity's prompt-taking subcommand: "Pass in a prompt to run in a chat
    # session in the current working directory." It was absent from this list, the checker
    # reported a confident L2 NO, and the matrix published "not currently instructable at this
    # seat" as a measured fact. Corrected 2026-09-09 against `antigravity --help` at source.
    "antigravity": ["chat", "exec", "agent", "--prompt"],
}


def _run(argv: list[str], timeout: float = 10.0) -> tuple[int, str]:
    """Read-only probe. Never raises; a failure is evidence, not an error."""
    try:
        p = subprocess.run(argv, capture_output=True, text=True, timeout=timeout)
        return p.returncode, (p.stdout or "") + (p.stderr or "")
    except (OSError, subprocess.SubprocessError):
        return -1, ""


def level1_installed(name: str) -> dict[str, Any]:
    path = shutil.which(name)
    if not path:
        return Verdict.no(warrant=f"{name} does not resolve on PATH").as_dict()
    resolved = Path(path).resolve()
    code, out = _run([name, "--version"])
    version = out.strip().splitlines()[0].strip() if code == 0 and out.strip() else None
    # A symlink into a macOS .app bundle is a DESKTOP launcher, not a terminal agent.
    # This is the distinction R9 Part 3 collapsed.
    in_app_bundle = ".app/Contents/" in str(resolved)
    # B2. This flag was computed, printed, and never consulted -- so a desktop launcher
    # reported L1 YES and could reach SUPPORTED-TARGET with exit 0. The scope note is explicit
    # that the launcher reading is "insufficient evidence of successor CLI installation", so it
    # cannot be a YES about a terminal agent. It is UNKNOWN: we learned about an .app bundle.
    detail = {
        "path": path,
        "resolved": str(resolved),
        "version": version,
        "is_desktop_launcher": in_app_bundle,
    }
    if in_app_bundle:
        return Verdict.unknown(
            limit="resolves into a macOS .app bundle: this is a DESKTOP LAUNCHER. Its version "
            "is not evidence about a terminal agent.",
            **detail,
        ).as_dict()
    if not version:
        return Verdict.unknown(
            limit="executable resolves but reported no version", **detail
        ).as_dict()
    return Verdict.yes(
        warrant=f"resolves on PATH and reports version {version}", **detail
    ).as_dict()


# L2 claims a NON-INTERACTIVE surface. Declaring a prompt-taking subcommand does not establish
# that: `antigravity chat` takes a prompt and every one of its options is window management
# (--maximize "Maximize the chat session view", --reuse-window, --new-window). Its peers say so
# explicitly -- `codex exec  Run Codex non-interactively`, `gemini -p  Run in non-interactive
# (headless) mode`. Declaration is not capability; this is "identity is not invocation" one
# level further down, and both a false NO and a false YES were published before it was drawn.
# Deliberately narrow: an EXPLICIT vendor statement, not an inference.
# `\bstdin\b` was in this set for one revision and was wrong -- antigravity's help says
# "To read from stdin, append '-' (e.g. 'ps aux | grep code | antigravity -')", which pipes
# content INTO A GUI EDITOR and still opens a window. A predicate whose extension is wider
# than its subject produces exactly the false YES this check exists to stop.
NONINTERACTIVE_EVIDENCE = re.compile(r"non-?interactive|headless|--print\b|\bbatch mode\b", re.I)
# Options that mark a surface as DRIVING A DESKTOP UI rather than running headless.
DESKTOP_OPTION = re.compile(r"--(maximize|reuse-window|new-window|goto|diff|merge)\b", re.I)

SUBCOMMAND_HEADINGS = re.compile(r"^\s*(sub)?commands?\s*:?\s*$", re.I)


def parse_help_surfaces(out: str) -> dict[str, list[str]]:
    """Extract the instruction surfaces the help text ACTUALLY declares.

    Reading structure instead of grepping for guessed tokens. Two rounds of review died on
    the grep approach: prose scored YES ("exec support was removed in 2.0."), real formats
    scored NO (tab columns, single-space columns, bare entries, colon suffixes), and -- worst --
    a runtime whose token list was simply WRONG got a confident NO. Antigravity declares
    `chat  Pass in a prompt to run in a chat session`; the checker sought exec/agent/--prompt,
    found none, and published "not currently instructable" as a measured fact.

    Returns {"subcommands": [...], "options": [...]}.
    """
    subs: list[str] = []
    opts: list[str] = []
    in_block = False
    block_indent = None
    for raw in out.splitlines():
        if not raw.strip():
            continue
        if SUBCOMMAND_HEADINGS.match(raw):
            in_block, block_indent = True, None
            continue
        indent = len(raw) - len(raw.lstrip())
        if in_block:
            if indent == 0:
                in_block = False  # a new unindented heading ends the block
            else:
                if block_indent is None:
                    block_indent = indent
                if indent <= block_indent:
                    parts = raw.strip().split()
                    tok = parts[0].rstrip(":,|")
                    # F6: "Commands:\n  exec was removed in 2.0" still declared `exec`. A real
                    # entry is a token plus a description; a sentence is a sentence.
                    looks_like_prose = len(parts) > 1 and parts[1] in {
                        "was",
                        "is",
                        "are",
                        "has",
                        "have",
                        "will",
                        "can",
                        "cannot",
                        "not",
                    }
                    if tok and not tok.startswith("-") and not looks_like_prose:
                        subs.append(tok)
                continue
        stripped = raw.lstrip()
        # A USAGE line declares surfaces: `Usage: prog [options] <subcommand>` and its flags.
        um = re.match(r"(?i)usage:\s*(\S+)\s*(.*)$", stripped)
        if um:
            rest = um.group(2)
            for tokm in re.finditer(r"(?<![\w-])(--?[A-Za-z][\w-]*)", rest):
                opts.append(tokm.group(1))
            # the first bare word after the program name is a subcommand, not a placeholder
            for word in rest.split():
                if re.fullmatch(r"[a-z][\w-]*", word):
                    subs.append(word)
                    break
                if not word.startswith("-"):
                    break  # <PROMPT>, [paths...] etc. end the subcommand position
            continue
        # An OPTION is declared where it begins the line's content, not where prose names it.
        if stripped.startswith("-"):
            for tokm in re.finditer(r"(?<![\w-])(--?[A-Za-z][\w-]*)", stripped):
                opts.append(tokm.group(1))
    return {"subcommands": sorted(set(subs)), "options": sorted(set(opts))}


def level2_instructable(name: str) -> dict[str, Any]:
    """One schema on every path. Three different shapes made --json unparseable by field."""
    tokens = INSTRUCTION_SURFACES.get(name)
    base = {
        "verdict": UNKNOWN,
        "surface_tokens_sought": tokens or [],
        "surface_tokens_found": [],
        "declared_surfaces": {},
        # one schema on EVERY path -- adding this key only to the YES branch reintroduced
        # the MINOR-12 defect the round-two repair closed.
        "noninteractive_evidence": None,
        "why": None,
    }
    if not shutil.which(name):
        return {
            **base,
            **Verdict.no(
                warrant=f"{name} does not resolve on PATH, so it exposes no surface at all"
            ).as_dict(),
        }
    code, out = _run([name, "--help"])
    if code != 0 and not out.strip():
        return {**base, "why": "--help produced no readable output"}
    surfaces = parse_help_surfaces(out)
    base["declared_surfaces"] = surfaces
    if tokens is None:
        return {
            **base,
            "why": f"no instruction surface declared for '{name}'; the help text "
            f"itself declares {surfaces}. Report, do not guess.",
        }
    found = [tok for tok in tokens if tok in surfaces["subcommands"] or tok in surfaces["options"]]
    parsed_anything = bool(surfaces["subcommands"] or surfaces["options"])

    if found:
        # F1. A declared token is not a non-interactive surface. Require the help to SAY so.
        noninteractive = NONINTERACTIVE_EVIDENCE.search(out)
        if noninteractive:
            return {
                **base,
                "surface_tokens_found": found,
                "noninteractive_evidence": noninteractive.group(0),
                **Verdict.yes(
                    warrant=f"--help declares {found} and states {noninteractive.group(0)!r}"
                ).as_dict(),
            }
        desktop = DESKTOP_OPTION.findall(out)
        return {
            **base,
            "verdict": UNKNOWN,
            "surface_tokens_found": found,
            "why": f"declares {found}, but nothing in --help establishes a NON-INTERACTIVE "
            f"surface, which is what L2 claims"
            + (
                f"; and its options include desktop-window controls "
                f"{sorted(set(desktop))[:5]}, which point the other way"
                if desktop
                else ""
            )
            + ". Declaration is not capability.",
        }

    # F2. NO is a claim about the RUNTIME and must never be reachable from OUR parser failing.
    # Measured: gcloud, npm and brew -- all subcommand-rich -- reached the old NO branch simply
    # because their help layout was not recognised.
    if parsed_anything:
        return {
            **base,
            "verdict": UNKNOWN,
            "why": f"none of {tokens} matched, but the help DECLARES surfaces we did not "
            f"seek: subcommands={surfaces['subcommands'][:8]}, "
            f"options={surfaces['options'][:8]}. An unmatched token list is an "
            f"unproven expectation, not a demonstrated absence.",
        }
    return {
        **base,
        "verdict": UNKNOWN,
        "why": "this parser recognised no subcommand block and no option lines in --help. "
        "That is a statement about the parser, not about the runtime: a NO here "
        "would be our failure reported as the tool's incapacity.",
    }


def level3_governed(name: str, receipts: Path | None) -> dict[str, Any]:
    """Read from a receipt. NEVER produced here -- running the runtime is state-changing."""
    if receipts is None:
        return Verdict.unknown(
            limit="no receipt directory supplied; L3 is never inferred"
        ).as_dict()
    if not receipts.is_dir():
        return Verdict.unknown(limit=f"receipt directory does not resolve: {receipts}").as_dict()
    # M4. This was `if name in f.read_text()` -- a substring match on any file. A receipt
    # reading "antigravity was NOT invoked" scored YES, and pointing --receipts at this
    # command's own JSON output made it certify itself. A receipt must DECLARE an invocation.
    hits, malformed, failures = [], [], []
    files: list[Path] = []
    visited: set[tuple[int, int]] = set()
    root = receipts.resolve()

    def walk(p: Path) -> None:
        rel = str(p.relative_to(root))
        try:
            s = p.lstat()
        except OSError as exc:
            failures.append(f"{rel}: lstat failed: {exc}")
            return
        if stat.S_ISLNK(s.st_mode):
            failures.append(f"{rel}: symlink entry is not receipt evidence")
            return
        if stat.S_ISDIR(s.st_mode):
            key = (s.st_dev, s.st_ino)
            if key in visited:
                return
            visited.add(key)
            if s.st_mode & 0o500 != 0o500:
                failures.append(f"{rel or '.'}: directory lacks owner read/traverse permission")
                return
            try:
                with os.scandir(p) as it:
                    children = sorted((Path(e.path) for e in it), key=lambda q: q.name)
            except OSError as exc:
                failures.append(f"{rel or '.'}: enumeration failed: {exc}")
                return
            for child in children:
                walk(child)
        elif stat.S_ISREG(s.st_mode):
            files.append(p)
        else:
            failures.append(f"{rel}: unsupported receipt entry type")

    walk(root)
    for f in files:
        try:
            if not f.stat().st_mode & 0o400:
                raise PermissionError("owner-read bit is not set")
            doc = json.loads(f.read_text())
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            failures.append(f"{f.relative_to(root)}: unreadable/malformed: {exc}")
            continue
        for rec in doc if isinstance(doc, list) else [doc]:
            if not isinstance(rec, dict) or rec.get("runtime") != name:
                continue
            if rec.get("invoked") is not True:
                malformed.append(f"{f.name}: names {name} but does not record invoked=true")
                continue
            # MAJOR-F: `str(rec.get("outcome",""))` only fires when the key is ABSENT --
            # null/false/0/[]/{} all stringify to a non-empty token and certified the
            # strongest claim the tool makes. Require an actual non-empty string.
            outcome = rec.get("outcome")
            if not isinstance(outcome, str) or not outcome.strip():
                malformed.append(f"{f.name}: invoked with no outcome recorded")
                continue
            hits.append(str(f))
    detail = {
        "receipts": hits[:5],
        "malformed": malformed[:5],
        "fully_read": not failures,
        "read_failures": sorted(set(failures))[:20],
    }
    if hits:
        return Verdict.yes(
            warrant=f"{len(hits)} receipt(s) declare a governed invocation of {name!r} with a "
            f"recorded outcome",
            **detail,
        ).as_dict()
    return Verdict.unknown(
        limit=(
            (f"could not fully read receipt subject {root}: " + "; ".join(sorted(set(failures))))
            if failures
            else (
                f"{len(malformed)} file(s) name '{name}' without recording a governed invocation"
                if malformed
                else f"no receipt in {receipts} declares a governed invocation of '{name}'; absence "
                f"of a receipt is a LIMIT of this reading, not a demonstrated NO"
            )
        ),
        **detail,
    ).as_dict()


def assess(name: str, receipts: Path | None) -> dict[str, Any]:
    l1 = level1_installed(name)
    # MINOR-12: level2_instructable already returns the not-installed case with the full
    # schema; building a second, thinner dict here gave --json two shapes for one field.
    l2 = level2_instructable(name)
    l3 = level3_governed(name, receipts)
    verdicts = [l1["verdict"], l2["verdict"], l3["verdict"]]
    if all(v == YES for v in verdicts):
        overall = "SUPPORTED-TARGET"
    elif NO in verdicts:
        overall = "NOT-DEMONSTRATED"
    else:
        overall = "PARTIAL-EVIDENCE"
    return {
        "runtime": name,
        "L1_installed": l1,
        "L2_instructable": l2,
        "L3_governed": l3,
        "overall": overall,
    }


def render(results: list[dict[str, Any]]) -> str:
    out = ["runtime support evidence -- three levels, reported separately", ""]
    for r in results:
        out.append(f"{r['runtime']}: {r['overall']}")
        for key, label in (
            ("L1_installed", "L1 installed   "),
            ("L2_instructable", "L2 instructable"),
            ("L3_governed", "L3 governed    "),
        ):
            lv = r[key]
            bits = ""
            if key == "L1_installed" and lv.get("version"):
                bits = f"  version={lv['version']}"
                if lv.get("is_desktop_launcher"):
                    bits += "  [DESKTOP LAUNCHER]"
            out.append(f"   {lv['verdict']:<8} {label}{bits}")
            if lv.get("why"):
                out.append(f"            -- {lv['why']}")
        out.append("")
    out.append("L1 does not imply L2; L2 does not imply L3. UNKNOWN is not NO and is never a pass.")
    return "\n".join(out)


def exit_code(results: list[dict[str, Any]]) -> int:
    verdicts = [
        lv["verdict"]
        for r in results
        for lv in (r["L1_installed"], r["L2_instructable"], r["L3_governed"])
    ]
    if all(v == YES for v in verdicts):
        return 0
    if NO in verdicts:
        return 1
    return 2


def main(argv: list[str] | None = None) -> int:
    ap = argparse.ArgumentParser(description="Report runtime support evidence at three levels.")
    ap.add_argument("--runtime", action="append", default=[], help="runtime name; repeatable")
    ap.add_argument("--config", type=Path, help="JSON file with a 'runtimes' list")
    ap.add_argument(
        "--receipts",
        type=Path,
        default=None,
        help="directory of governed-invocation receipts (L3 is read, never produced)",
    )
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args(argv)

    names = list(args.runtime)
    if args.config:
        # MAJOR-6. This was unvalidated: a list config raised AttributeError, an int entry
        # raised TypeError, and a STRING value iterated its characters and reported on
        # runtimes "g", "e", "m". All exited 1 -- which the contract reads as a definite NO.
        try:
            doc = json.loads(args.config.read_text())
        except (OSError, UnicodeDecodeError, json.JSONDecodeError) as exc:
            print(f"UNAVAILABLE: {args.config}: {exc}", file=sys.stderr)
            return 3
        if not isinstance(doc, dict):
            print(f"UNAVAILABLE: {args.config} must contain a JSON object", file=sys.stderr)
            return 3
        listed = doc.get("runtimes", [])
        if not isinstance(listed, list):
            print(
                f"UNAVAILABLE: {args.config}: 'runtimes' must be a list, got "
                f"{type(listed).__name__}",
                file=sys.stderr,
            )
            return 3
        bad = [r for r in listed if not isinstance(r, str) or not r.strip()]
        if bad:
            print(
                f"UNAVAILABLE: {args.config}: every runtime must be a non-empty string; "
                f"got {bad!r}",
                file=sys.stderr,
            )
            return 3
        names += listed
    if not names:
        ap.error("name at least one --runtime, or supply --config")
    # MINOR-I: --config was validated and --runtime was not, so a blank name reached the
    # assessor and came back as a definite NOT-DEMONSTRATED.
    blank = [n for n in names if not isinstance(n, str) or not n.strip()]
    if blank:
        print(f"UNAVAILABLE: runtime names must be non-empty; got {blank!r}", file=sys.stderr)
        return 3

    results = [assess(n, args.receipts) for n in dict.fromkeys(names)]
    print(json.dumps(results, indent=1) if args.json else render(results))
    return exit_code(results)


if __name__ == "__main__":
    sys.exit(main())
