"""R-F9 (rehearsal 2026-09-30): the trial run of the protected write is its own read-only tool.

apply_protected.py without --apply writes nothing, yet the rehearsal's permission classifier refused that run as a
change to shared files: the tool's name and its write path read as a write. plan_protected.py answers the same
question (what would the reviewed script write, and would it refuse?) from a file that contains no write at all.
"""
import io
import contextlib
import tokenize
from pathlib import Path

from test_migration_kit_batch_protected import A, BATCH, SKILL, load, make_list, world  # noqa: F401  (world: fixture)

PLAN = BATCH / "plan_protected.py"


def _planner(monkeypatch):
    """plan_protected.py, loaded, with its apply_protected reading the test's fleet register (BIND, E2i): the
    planner imports its own copy of apply_protected, which the `world` fixture's register does not reach."""
    mod = load("plan_protected", PLAN)
    monkeypatch.setattr(mod.A, "REGISTER", getattr(A, "REGISTER", None), raising=False)
    return mod


def _run(mod, argv):
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        code = mod.main(argv)
    return code, out.getvalue().splitlines()


def test_the_plan_reports_what_would_be_written_and_writes_nothing(world, tmp_path, monkeypatch):
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    before = sorted(p.name for p in tmp_path.iterdir())
    code, lines = _run(_planner(monkeypatch), ["--list", str(lst)])
    assert code == 0 and any("WOULD-APPLY" in ln for ln in lines), lines
    assert not (aget / SKILL).exists() and "3.34.0" in (aget / "AGENTS.md").read_text()
    assert sorted(p.name for p in tmp_path.iterdir()) == before          # no receipt, no other file


def test_the_plan_agrees_with_the_apply_scripts_own_trial_run(world, tmp_path, monkeypatch):
    """FALSIFIER: a planner that drifts from the script it speaks for would approve a write nobody reviewed."""
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    _, planned = _run(_planner(monkeypatch), ["--list", str(lst)])
    _, dry = _run(A, ["--list", str(lst), "--receipt-dir", str(tmp_path)])
    per_aget = lambda lines: [ln for ln in lines if ln.startswith("fixture-aget")]  # noqa: E731
    assert per_aget(planned) and per_aget(planned) == per_aget(dry)


def test_the_plan_refuses_a_changed_aget_like_the_apply_script(world, tmp_path, monkeypatch):
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    (aget / "AGENTS.md").write_text("changed since the list\n")
    code, lines = _run(_planner(monkeypatch), ["--list", str(lst)])
    assert code == 1 and any("REFUSED" in ln and "STALE" in ln for ln in lines), lines


def test_the_plan_refuses_a_list_that_names_another_apply_script(world, tmp_path, monkeypatch):
    _, aget = world
    lst, _ = make_list(tmp_path, aget)
    lst.write_text(lst.read_text().replace(A.self_sha(), "0" * 64))
    code, lines = _run(_planner(monkeypatch), ["--list", str(lst)])
    assert code == 2 and any("REFUSED" in ln for ln in lines), lines


def test_the_planner_contains_no_write_at_all():
    """The reason it exists: nothing in this file can change a receiver, so its name and its body agree."""
    names = {t.string for t in tokenize.generate_tokens(io.StringIO(PLAN.read_text()).readline)
             if t.type == tokenize.NAME}
    assert not names & {"write_bytes", "write_text", "mkdir", "unlink", "rename", "open", "apply"}, names
