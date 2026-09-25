"""AGET_CI_SPEC:V-CI-011 (CAP-CI-010-03), PARTIAL: the suite is executed in an environment that
does not reproduce the authoring host.

CAP-CI-010-03 says Test_Hermeticity is established by EXECUTION in a Distinct_Environment, never by
source inspection alone. This repository's Distinct_Environment is the CI test job: a GitHub-hosted
runner, a fresh checkout of this repository, and a blocking run of the whole suite there.

What this file verifies (stated plainly, because the V-test has three parts):
  (a) the suite is executed: at least one unconditional, blocking step runs pytest over the whole
      `tests` directory on push or pull request (workflow configuration);
  (b) in a distinct environment: that job runs on a GitHub-hosted image from a fresh checkout of
      this repository, and, when these tests themselves run inside GitHub Actions, the runner
      reports itself as github-hosted (evidence from the run, not only from the file).
What it does NOT verify:
  (c) that any claim of Test_Hermeticity waited for that run. Nothing machine-readable records such
      a claim today, so part (c) is owed, not implemented.
"""

import os
import re
import shlex
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"
HOSTED = re.compile(r"^(ubuntu|windows|macos)-(latest|\d+(\.\d+)?)(-arm|-large|-xlarge)?$")
REJECT_ARGS = {"--co", "--collect-only", "-k", "--deselect", "--lf", "--last-failed"}


def _doc():
    return yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))


def _triggers(doc):
    # PyYAML (YAML 1.1) reads the bare key `on` as the boolean True.
    trig = doc.get("on", doc.get(True)) or {}
    return set(trig) if isinstance(trig, (dict, list)) else {trig}


def _unconditional(node):
    return "if" not in node and not node.get("continue-on-error", False)


def _runs_full_suite(step):
    """True only for a blocking command that runs pytest over the whole `tests` directory."""
    if not _unconditional(step) or "working-directory" in step:
        return False
    run = str(step.get("run", "")).replace("\\\n", " ")
    for line in run.splitlines():
        try:
            tokens = shlex.split(line, comments=True)
        except ValueError:
            continue
        if tokens[:1] == ["pytest"]:
            args = tokens[1:]
        elif tokens[:3] in (["python", "-m", "pytest"], ["python3", "-m", "pytest"]):
            args = tokens[3:]
        else:
            continue
        if "||" in args or "|" in args or REJECT_ARGS & set(args):
            continue
        if any(a.rstrip("/") == "tests" for a in args if not a.startswith("-")):
            return True
    return False


def _suite_jobs():
    return {name: job for name, job in _doc()["jobs"].items()
            if _unconditional(job) and any(_runs_full_suite(s) for s in job.get("steps", []))}


def test_full_suite_runs_blocking_on_push_or_pull_request():
    assert _triggers(_doc()) & {"push", "pull_request"}, "CI does not run on push or pull_request"
    assert _suite_jobs(), "no unconditional, blocking CI step runs the whole suite (pytest tests)"


def test_suite_job_uses_a_github_hosted_image():
    jobs = _suite_jobs()
    assert jobs
    for name, job in jobs.items():
        runs_on = job.get("runs-on")
        labels = runs_on if isinstance(runs_on, list) else [runs_on]
        assert all(isinstance(x, str) and HOSTED.match(x) for x in labels), (
            f"job {name!r} runs-on {runs_on!r} is not a GitHub-hosted image label")


def test_suite_job_starts_from_a_fresh_checkout_of_this_repository():
    jobs = _suite_jobs()
    assert jobs
    for name, job in jobs.items():
        steps = job.get("steps", [])
        first = next(i for i, s in enumerate(steps) if _runs_full_suite(s))
        checkouts = [s for s in steps[:first]
                     if str(s.get("uses", "")).startswith("actions/checkout@") and _unconditional(s)]
        assert checkouts, f"job {name!r} runs the suite without an unconditional checkout before it"
        assert all("repository" not in (s.get("with") or {}) for s in checkouts), (
            f"job {name!r} checks out another repository before the suite")


def test_this_run_is_on_a_github_hosted_runner_when_in_actions():
    # Evidence from the execution itself (CAP-CI-010-03), not from the workflow file.
    if os.environ.get("GITHUB_ACTIONS") != "true":
        return  # outside Actions there is no runner to report; the three tests above still apply
    assert os.environ.get("RUNNER_ENVIRONMENT") == "github-hosted", (
        f"RUNNER_ENVIRONMENT={os.environ.get('RUNNER_ENVIRONMENT')!r}")
