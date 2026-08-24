"""AC-3 source-resolution contract — v3.32 prepared public delta.

Falsifiers for the defect measured on shipped blob
4ac6b576268b31d4ea580ea12293d7a8bbc95d1e: an explicit AGET_CANONICAL_ROOT that
does not resolve was silently discarded, a DIFFERENT repository was measured and
reported as canonical, and the process exited 0.

Each test below was demonstrated RED against that exact blob before being
accepted (L1425: a green suite cannot discharge a falsifier it does not encode).

The tests run the script as a SUBPROCESS on purpose. The defect lives in
module-level resolution (`CANONICAL, CANONICAL_STRATEGY = _default_repo()`), so
importing the module would bind the strategy once and make the environment
variable untestable.
"""
import json
import os
import subprocess
import sys
from pathlib import Path

SCRIPT = Path(__file__).resolve().parent.parent / "scripts" / "release_cadence_gap.py"

EXIT_OK, EXIT_BREACHED, EXIT_UNAVAILABLE = 0, 1, 2


def _run(env_root, *args):
    env = dict(os.environ)
    if env_root is None:
        env.pop("AGET_CANONICAL_ROOT", None)
    else:
        env["AGET_CANONICAL_ROOT"] = env_root
    return subprocess.run(
        [sys.executable, str(SCRIPT), *args],
        capture_output=True, text=True, env=env,
    )


def _breached_or_ok(r):
    """An exit code alone cannot be read as a verdict.

    EXIT_BREACHED is 1, and so is the exit code of almost any crash. The shipped
    test asserted `returncode in (EXIT_OK, EXIT_BREACHED)` and then parsed stdout;
    on Python 3.10 the script died in date parsing, exited 1 with EMPTY stdout, and
    the assertion passed VACUOUSLY -- the real failure surfaced downstream as a
    JSONDecodeError, one layer away from its cause.

    So: exit 1 may be interpreted as a legitimate BREACHED result only when stdout
    also carries non-empty, valid JSON. Otherwise it is a crash and is reported as
    one, at the point it happened.
    """
    assert r.returncode in (EXIT_OK, EXIT_BREACHED), (
        f"unexpected exit {r.returncode}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert r.stdout.strip(), (
        f"exit {r.returncode} with EMPTY stdout is a crash, not a verdict "
        f"(EXIT_BREACHED collides with a crash's exit 1)\nstderr:\n{r.stderr}"
    )
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(
            f"exit {r.returncode} with non-JSON stdout is a crash, not a verdict: {e}"
            f"\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
        ) from None


def _payload_of(r, expect_exit):
    """Same discipline as `_breached_or_ok`, for the UNAVAILABLE polarity.

    exit 2 is UNAVAILABLE and does NOT collide with a crash the way exit 1 does,
    but the JSON requirement is identical: a verdict whose stdout is empty or
    unparseable is a crash wearing a verdict's exit code.
    """
    assert r.returncode == expect_exit, (
        f"expected exit {expect_exit}, got {r.returncode}\nstdout:\n{r.stdout}\nstderr:\n{r.stderr}"
    )
    assert r.stdout.strip(), f"exit {r.returncode} with EMPTY stdout\nstderr:\n{r.stderr}"
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError as e:
        raise AssertionError(f"exit {r.returncode} with non-JSON stdout: {e}\nstdout:\n{r.stdout}") from None


def _run_argv(argv):
    """Run the script with argv, inheriting a clean environment."""
    env = dict(os.environ)
    env.pop("AGET_CANONICAL_ROOT", None)
    return subprocess.run([sys.executable, str(SCRIPT), *argv],
                          capture_output=True, text=True, env=env)


def test_utc_z_taggerdate_parses_deterministically():
    """Regression for the Python 3.10 CI failure. Deterministic: the tag date is
    pinned via env, so this asserts parsing, not the clock."""
    from datetime import datetime, timezone
    import importlib.util

    spec = importlib.util.spec_from_file_location("_rcg", SCRIPT)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)

    expected = datetime(2026, 8, 15, 18, 29, 0, tzinfo=timezone.utc)
    for form in ("2026-08-15T18:29:00Z", "2026-08-15T18:29:00+0000", "2026-08-15T18:29:00+00:00"):
        got = mod._parse_tagger_date(form)
        assert got == expected, f"{form!r} parsed to {got!r}, expected {expected!r}"

    import pytest as _pytest
    with _pytest.raises(ValueError):
        mod._parse_tagger_date("")


def test_rejected_explicit_root_is_unavailable_not_success():
    """RED on 4ac6b576: returned 0. An operator-named subject that cannot be
    read must never be reported as a successful measurement."""
    r = _run("/nonexistent/xyz", "--json")
    assert r.returncode == EXIT_UNAVAILABLE, (
        f"expected UNAVAILABLE({EXIT_UNAVAILABLE}), got {r.returncode}"
    )


def test_rejected_explicit_root_is_not_conflated_with_breach():
    """UNAVAILABLE(2) and BREACHED(1) are different claims. 'Non-zero' is not an
    acceptable contract -- collapsing them is the conflation this repair ends."""
    r = _run("/nonexistent/xyz", "--json")
    assert r.returncode != EXIT_BREACHED


def test_rejected_explicit_root_discloses_the_rejection():
    """RED on 4ac6b576: disclosed nothing. Source disclosure, not just source
    selection -- a reader must be able to tell which rule won."""
    r = _run("/nonexistent/xyz", "--json")
    payload = _payload_of(r, EXIT_UNAVAILABLE)
    assert payload["status"] == "UNAVAILABLE"
    assert "AGET_CANONICAL_ROOT" in payload["source_strategy"]
    assert "no fallback applied" in payload["source_strategy"]


def test_rejected_explicit_root_never_substitutes_another_subject():
    """The sharpest form of the defect: 4ac6b576 reported a throwaway scratch
    directory as the canonical public repo and exited 0."""
    r = _run("/nonexistent/xyz", "--json")
    payload = _payload_of(r, EXIT_UNAVAILABLE)
    assert payload["source_repo"] is None, (
        f"a rejected explicit input must not be replaced; got {payload['source_repo']!r}"
    )


def test_valid_explicit_root_still_measures_and_discloses_strategy():
    """Positive polarity. A repair that only ever returns UNAVAILABLE would pass
    every negative test above and be useless.

    Gate 0 repair (2026-08-22): this computed the repo root at `parents[3]`, which
    from the prepared-delta harness was `docs/` -- not a git repository, so the
    test handed the script a non-repository as its EXPLICIT root, the script
    correctly rejected it, and the positive polarity was never exercised: the test
    was asserting the negative case while claiming to prove the positive one.
    Relocated to `tests/` for v3.32 publication, the repo root is `parents[1]`.
    The `.git` assertion below is what makes a wrong depth fail loudly instead of
    silently degrading back into the negative case.
    """
    repo_root = Path(__file__).resolve().parents[1]
    assert (repo_root / ".git").exists(), (
        f"fixture cannot locate a git repository at {repo_root}; the positive polarity "
        "must not silently degrade into the negative one again"
    )
    repo = str(repo_root)
    r = _run(repo, "--json")
    payload = _breached_or_ok(r)
    assert payload["source_strategy"] == "explicit:AGET_CANONICAL_ROOT"
    assert payload["source_repo"] == repo


def test_absent_explicit_input_still_discovers(tmp_path):
    """Discovery is only disabled when an explicit input was GIVEN and rejected.
    With no explicit input, rules 2 and 3 must behave exactly as before.

    Gate 0 repair (2026-08-22): discovery rules 2 and 3 are DEPTH-DEPENDENT by
    design -- the script resolves `__file__.parent.parent` as its own repo root.
    Run from the staging tree at `docs/prepared/v3.32/scripts/`, that resolves to
    `docs/prepared/v3.32/`, and the sibling probe to `docs/prepared/aget/`; neither
    exists, so the rule can only ever return UNAVAILABLE. The script was never
    wrong -- the fixture measured it at a depth it will never run at. Verified
    2026-08-22: the same file at `<repo>/scripts/` exits 0 with
    `discovered:own-repo-root`. So the fixture now runs it at LANDING depth, which
    is the tree that ships.
    """
    landing = tmp_path / "repo"
    (landing / "scripts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(landing)], check=True)
    for k, v in (("user.email", "fixture@example.com"), ("user.name", "Fixture")):
        subprocess.run(["git", "-C", str(landing), "config", k, v], check=True)
    (landing / "seed.txt").write_text("seed\n")
    subprocess.run(["git", "-C", str(landing), "add", "seed.txt"], check=True)
    subprocess.run(["git", "-C", str(landing), "commit", "-qm", "seed"], check=True)
    subprocess.run(["git", "-C", str(landing), "tag", "-a", "v3.31.0", "-m", "r"], check=True)

    landed = landing / "scripts" / SCRIPT.name
    landed.write_bytes(SCRIPT.read_bytes())

    env = dict(os.environ)
    env.pop("AGET_CANONICAL_ROOT", None)
    r = subprocess.run(
        [sys.executable, str(landed), "--json"], capture_output=True, text=True, env=env
    )
    payload = _breached_or_ok(r)
    assert payload["source_strategy"] == "discovered:own-repo-root"
    assert payload["source_repo"] == str(landing)


def test_staged_depth_is_unavailable_and_says_so_rather_than_substituting(tmp_path):
    """Negative polarity of the repair above, and the reason it is not a papered-over
    failure: at a depth where discovery genuinely cannot resolve, the script must
    return UNAVAILABLE and name that -- never substitute a different repository.
    That is the original AC-3 defect, asserted here at the staging depth itself.
    """
    orphan = tmp_path / "nowhere" / "scripts"
    orphan.mkdir(parents=True)
    landed = orphan / SCRIPT.name
    landed.write_bytes(SCRIPT.read_bytes())

    env = dict(os.environ)
    env.pop("AGET_CANONICAL_ROOT", None)
    r = subprocess.run(
        [sys.executable, str(landed), "--json"], capture_output=True, text=True, env=env
    )
    assert r.returncode == EXIT_UNAVAILABLE
    payload = _payload_of(r, EXIT_UNAVAILABLE)
    assert payload["source_repo"] is None
    assert payload["source_strategy"].startswith("UNAVAILABLE:")


def test_human_output_discloses_strategy_not_only_path(tmp_path):
    """Both polarities on the path an operator actually reads.

    Found 2026-08-23 by rehearsing the shipped instrument end to end. Both --json
    paths carried `source_strategy` from the start; the default text path printed
    only `source : <repo>`. So an explicitly-named subject and a discovered one
    rendered IDENTICALLY -- which is exactly the distinction the 2026-08-21 repair
    exists to make visible, absent from the output most people see.

    The assertion that matters is not "the word appears" but "the two cases are
    DISTINGUISHABLE". A disclosure that renders the same for both resolutions
    discloses nothing, and would pass a naive substring check.
    """
    repo_root = Path(__file__).resolve().parents[1]
    assert (repo_root / ".git").exists(), "fixture cannot locate a git repository"

    explicit = _run(str(repo_root))
    assert explicit.returncode in (EXIT_OK, EXIT_BREACHED), explicit.stdout
    assert "explicit:AGET_CANONICAL_ROOT" in explicit.stdout, (
        "human path does not say the subject was explicitly named:\n" + explicit.stdout
    )

    # Discovery polarity: a real repo with the script at landing depth (<repo>/scripts/).
    land = tmp_path / "landing"
    (land / "scripts").mkdir(parents=True)
    subprocess.run(["git", "init", "-q", str(land)], check=True)
    (land / "scripts" / SCRIPT.name).write_text(SCRIPT.read_text())
    env = dict(os.environ)
    env.pop("AGET_CANONICAL_ROOT", None)
    discovered = subprocess.run(
        [sys.executable, str(land / "scripts" / SCRIPT.name)],
        capture_output=True, text=True, env=env,
    )
    assert "discovered:own-repo-root" in discovered.stdout, (
        "human path does not say the subject was discovered:\n" + discovered.stdout
    )

    assert "explicit:" not in discovered.stdout, (
        "a discovered subject must not render as an explicitly-named one"
    )


# --- CLI channel (--repo) -----------------------------------------------------
# Added v3.32 Phase 3. The independent review falsified four propositions against
# the --repo channel and noted the cause: "the cadence source-contract tests do not
# exercise either valid or invalid explicit --repo input". Five green matrix cells
# passed a payload whose headline claim was false through its own CLI flag. Every
# channel is now covered, because fixing only the named instance is how this
# defect reached a review in the first place.

def test_invalid_explicit_repo_is_unavailable_not_breach():
    """F1+F2: an unresolvable --repo is UNAVAILABLE (2), never BREACHED (1)."""
    r = _run_argv(["--repo", "/nonexistent/xyz", "--json"])
    assert r.returncode == EXIT_UNAVAILABLE, (
        f"expected exit 2, got {r.returncode}. Exit 1 here is indistinguishable from "
        f"BREACHED, which is the conflation this module exists to end.\n{r.stdout}{r.stderr}"
    )
    payload = _payload_of(r, EXIT_UNAVAILABLE)
    assert payload["source_repo"] is None, "a rejected subject must not be substituted"
    assert "--repo" in payload["source_strategy"], "the rejection must name the channel"


def test_invalid_explicit_repo_emits_json_not_empty_stdout():
    """F2 corollary: the failure is a verdict, not a crash."""
    r = _run_argv(["--repo", "/nonexistent/xyz", "--json"])
    assert r.stdout.strip(), "exit with empty stdout is a crash wearing a verdict's exit code"
    json.loads(r.stdout)


def test_valid_explicit_repo_discloses_the_channel_that_selected_it(tmp_path):
    """F4: the disclosed strategy must be the strategy that chose the subject.

    The shipped defect reported 'discovered:own-repo-root' for a repo supplied via
    --repo -- measuring one repository and disclosing a different basis for it.
    """
    repo = tmp_path / "r"
    (repo).mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    for k, v in (("user.email", "f@example.com"), ("user.name", "F")):
        subprocess.run(["git", "-C", str(repo), "config", k, v], check=True)
    (repo / "s.txt").write_text("s\n")
    subprocess.run(["git", "-C", str(repo), "add", "s.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "s"], check=True)
    subprocess.run(["git", "-C", str(repo), "tag", "-a", "v3.31.0", "-m", "r"], check=True)

    r = _run_argv(["--repo", str(repo), "--json"])
    payload = _breached_or_ok(r)
    assert payload["source_repo"] == str(repo), "must measure the repo it was given"
    assert payload["source_strategy"] == "explicit:--repo", (
        f"disclosed strategy {payload['source_strategy']!r} is not the channel that "
        "selected the subject -- source disclosure, not merely source selection"
    )


def test_explicit_repo_outranks_environment(tmp_path):
    """F3: discovery and env must not run when --repo was given."""
    repo = tmp_path / "r2"
    repo.mkdir()
    subprocess.run(["git", "init", "-q", str(repo)], check=True)
    for k, v in (("user.email", "f@example.com"), ("user.name", "F")):
        subprocess.run(["git", "-C", str(repo), "config", k, v], check=True)
    (repo / "s.txt").write_text("s\n")
    subprocess.run(["git", "-C", str(repo), "add", "s.txt"], check=True)
    subprocess.run(["git", "-C", str(repo), "commit", "-qm", "s"], check=True)
    subprocess.run(["git", "-C", str(repo), "tag", "-a", "v3.31.0", "-m", "r"], check=True)

    env = dict(os.environ)
    env["AGET_CANONICAL_ROOT"] = "/nonexistent/should-be-ignored"
    r = subprocess.run([sys.executable, str(SCRIPT), "--repo", str(repo), "--json"],
                       capture_output=True, text=True, env=env)
    payload = _breached_or_ok(r)
    assert payload["source_strategy"] == "explicit:--repo", (
        "an explicit --repo must outrank the environment variable"
    )
