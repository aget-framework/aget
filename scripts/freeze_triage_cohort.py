#!/usr/bin/env python3
"""Freeze, review and verify an untriaged-issue cohort on any GitHub tracker.

Read-only GitHub instrument. It refuses a fallback label list: a frozen cohort must
record the LIVE label universe that minted it. The governed snapshot omits issue
bodies and records their digests; an optional private temporary file carries bodies
for the bounded review.

WHAT IT IS FOR

    Any AGET seat, or any operator of a GitHub issue tracker, that needs a frozen,
    auditable snapshot of the issues NOT yet carrying a classification label.

    Run freeze mode against your own tracker to mint a dated snapshot, review it out
    of band, then run --reconcile and --verify to prove the review covered exactly
    the frozen cohort and that nothing was added, dropped, or edited underneath it.
    **The verify step is the point** -- it is what makes a triage pass auditable
    rather than merely done.

    Supply the tracker with --repo OWNER/NAME. Requires `gh`, authenticated for it.

COHORT-INDEPENDENT

    Promoted from a cycle-scoped instrument. Two kinds of version-dependence were
    removed, and the second was load-bearing:

      * the schema identifiers named one release cycle;
      * **verify() hardcoded one cohort's counts** -- 192 members, 19 surfaced, 7
        clusters. Those literals meant verification passed for exactly one
        population and failed for every other, for the wrong reason: a different
        cohort is a different size, not a custody breach.

    Custody, coverage and partition are properties of ANY cohort. They are now
    derived from the artifacts under verification instead of asserted as constants,
    so this command verifies your tracker's cohort, not somebody else's.

MODES
  freeze      --repo OWNER/NAME --snapshot-output S --private-body-output P
  reconcile   --reconcile --snapshot-input S --review-input R... --clusters-input C
              --result-output O
  verify      --verify --snapshot-input S --clusters-input C --result-output O
"""
from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path


# NO MODULE-LEVEL REPOSITORY DEFAULT.
#
# This carried a hardcoded module-level constant naming one private issue tracker
# until 2026-08-23 -- inside an instrument intended for public release. The
# generalization is one line of removal plus a required argument; it was never a
# redesign. (The constant is not reproduced here: naming it would reintroduce the
# private reference this change exists to remove.)
#
# The argument is REQUIRED rather than defaulted, for the same reason
# release_cadence_gap.py refuses an unresolvable explicit root instead of falling
# back: an instrument that quietly substitutes a subject gives a confident answer
# about the wrong thing. A default here would silently point every consumer at
# whichever tracker the author happened to use.
NAMESPACES = ("type:", "state:", "status:", "priority:", "severity:")
EXPLICIT = {"route:resolved", "route:escalated", "route:supervisor"}
NOT_CLASSIFICATION = {"route:needs-triage", "status:needs-triage"}
NOT_CLASSIFICATION_SUFFIX = ("needs-triage", "untriaged")


def gh(*args: str) -> str:
    result = subprocess.run(
        ["gh", *args], capture_output=True, text=True, timeout=180, check=False
    )
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or "gh command failed")
    return result.stdout


def live_classification_labels(repo: str) -> list[str]:
    labels = gh("api", f"repos/{repo}/labels", "--paginate", "--jq", ".[].name")
    selected = {
        label.strip()
        for label in labels.splitlines()
        if label.strip().startswith(NAMESPACES)
        and label.strip() not in NOT_CLASSIFICATION
        and not label.strip().endswith(NOT_CLASSIFICATION_SUFFIX)
    }
    selected.update(EXPLICIT)
    if not selected:
        raise RuntimeError("live classification-label enumeration returned zero")
    return sorted(selected)


def search_issues(query: str) -> list[dict]:
    raw = gh(
        "api", "-X", "GET", "search/issues", "-f", f"q={query}",
        "-f", "per_page=100", "--paginate",
    )
    decoder = json.JSONDecoder()
    offset = 0
    pages: list[dict] = []
    while offset < len(raw):
        while offset < len(raw) and raw[offset].isspace():
            offset += 1
        if offset >= len(raw):
            break
        page, offset = decoder.raw_decode(raw, offset)
        pages.append(page)
    items = [item for page in pages for item in page.get("items", [])]
    return sorted(items, key=lambda item: item["number"])


def digest(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def reconcile(snapshot_path: Path, review_paths: list[Path], clusters_path: Path,
              result_path: Path) -> int:
    snapshot = json.loads(snapshot_path.read_text())
    reviews = [row for path in review_paths for row in json.loads(path.read_text())]
    review_by_number = {row["number"]: row for row in reviews}
    expected = [item["number"] for item in snapshot["items"]]
    if len(reviews) != len(expected) or sorted(review_by_number) != sorted(expected):
        raise RuntimeError("review rows do not match the frozen member register")

    cluster_doc = json.loads(clusters_path.read_text())
    surfaced = {
        number for cluster in cluster_doc["clusters"] for number in cluster["issues"]
    }
    unknown = surfaced - set(expected)
    if unknown:
        raise RuntimeError(f"cluster rows outside the frozen input: {sorted(unknown)}")

    items = []
    for source in snapshot["items"]:
        review = review_by_number[source["number"]]
        independent = review["verdict"]
        if source["number"] in surfaced:
            final = "SURFACE"
        elif independent in {"SURFACE", "VERIFY"}:
            final = "VERIFY"
        else:
            final = "NOT_SURFACE"
        items.append({
            "number": source["number"],
            "body_sha256": source["body_sha256"],
            "independent_verdict": independent,
            "final_verdict": final,
            "rationale": review["rationale"],
            "proposed_owner": review["proposed_owner"],
            "next_action": review["next_action"],
        })

    counts = {
        verdict: sum(item["final_verdict"] == verdict for item in items)
        for verdict in ("SURFACE", "VERIFY", "NOT_SURFACE")
    }
    result = {
        "schema": "triage-cohort-review-result/1.0",
        "source_member_number_sha256": snapshot["member_number_sha256"],
        "source_count": snapshot["count"],
        "reviewed_count": len(items),
        "final_counts": counts,
        "surfaced_cluster_count": len(cluster_doc["clusters"]),
        "surfaced_issue_count": len(surfaced),
        "clusters": cluster_doc["clusters"],
        "items": items,
    }
    result_path.parent.mkdir(parents=True, exist_ok=True)
    result_path.write_text(json.dumps(result, indent=2) + "\n")
    print(json.dumps({
        "reviewed_count": len(items), "final_counts": counts,
        "surfaced_cluster_count": len(cluster_doc["clusters"]),
        "surfaced_issue_count": len(surfaced), "result_output": str(result_path),
    }, indent=2))
    return 0


def verify(snapshot_path: Path, clusters_path: Path, result_path: Path) -> int:
    """Verify custody, complete coverage, and surfaced-cluster semantics."""
    snapshot = json.loads(snapshot_path.read_text())
    clusters = json.loads(clusters_path.read_text())["clusters"]
    result = json.loads(result_path.read_text())

    source_numbers = [item["number"] for item in snapshot["items"]]
    source_by_number = {item["number"]: item for item in snapshot["items"]}
    result_numbers = [item["number"] for item in result["items"]]
    expected_digest = digest("\n".join(str(number) for number in source_numbers))
    surfaced = {
        item["number"] for item in result["items"]
        if item["final_verdict"] == "SURFACE"
    }
    clustered = {number for cluster in clusters for number in cluster["issues"]}
    # COHORT-INDEPENDENT BY CONSTRUCTION.
    #
    # This block previously hardcoded one cycle's cohort: `== 192` in three places,
    # `== 19` surfaced and `== 7` clusters, plus a PASS line quoting them. Those
    # literals made verification pass for exactly one population and fail for every
    # other -- not because custody broke, but because the next cohort is a different
    # size. Custody, coverage and partition are properties of ANY cohort; they are
    # derived here from the artifacts themselves.
    n_source = len(source_numbers)
    checks = {
        "source_count_exact": snapshot["count"] == n_source,
        "source_members_unique": len(source_numbers) == len(set(source_numbers)),
        "source_digest_exact": snapshot["member_number_sha256"] == expected_digest,
        "result_custody_exact": (
            result["source_count"] == snapshot["count"]
            and result["source_member_number_sha256"] == expected_digest
            and result["reviewed_count"] == len(result_numbers) == n_source
            and result_numbers == source_numbers
        ),
        "body_hashes_preserved": all(
            item["body_sha256"] == source_by_number[item["number"]]["body_sha256"]
            for item in result["items"]
        ),
        "verdict_partition_exact": (
            sum(result["final_counts"].values()) == n_source
            and result["final_counts"] == {
                verdict: sum(item["final_verdict"] == verdict for item in result["items"])
                for verdict in ("SURFACE", "VERIFY", "NOT_SURFACE")
            }
        ),
        "surface_equals_clusters": (
            surfaced == clustered
            and len(surfaced) == result["surfaced_issue_count"]
            and len(clusters) == result["surfaced_cluster_count"]
        ),
        "clusters_actionable": all(
            cluster.get("issues")
            and cluster.get("proposed_owner", "").strip()
            and cluster.get("next_action", "").strip()
            and cluster.get("principal_effect", "").strip()
            for cluster in clusters
        ),
    }
    print(json.dumps(checks, indent=2))
    failed = [name for name, passed in checks.items() if not passed]
    if failed:
        raise RuntimeError(f"verification failed: {', '.join(failed)}")
    print(f"PASS: {n_source}/{n_source} reviewed; {len(surfaced)} surfaced in "
          f"{len(clusters)} actionable clusters")
    return 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--repo",
        metavar="OWNER/NAME",
        help="Issue tracker to read, e.g. 'octo/handbook'. REQUIRED in freeze mode; "
             "there is deliberately no default (see the note at the top of this file).",
    )
    parser.add_argument("--snapshot-output", type=Path)
    parser.add_argument("--private-body-output", type=Path)
    parser.add_argument("--reconcile", action="store_true")
    parser.add_argument("--verify", action="store_true")
    parser.add_argument("--snapshot-input", type=Path)
    parser.add_argument("--review-input", type=Path, action="append", default=[])
    parser.add_argument("--clusters-input", type=Path)
    parser.add_argument("--result-output", type=Path)
    args = parser.parse_args()

    if args.reconcile or args.verify:
        required = [args.snapshot_input, args.clusters_input, args.result_output]
        if any(path is None for path in required):
            parser.error("review mode requires snapshot, clusters, and result paths")
        if args.verify:
            return verify(args.snapshot_input, args.clusters_input, args.result_output)
        if not args.review_input:
            parser.error("--reconcile requires at least one review path")
        return reconcile(
            args.snapshot_input, args.review_input, args.clusters_input, args.result_output
        )
    if not args.snapshot_output or not args.private_body_output:
        parser.error("freeze mode requires --snapshot-output and --private-body-output")
    if not args.repo:
        parser.error(
            "freeze mode requires --repo OWNER/NAME. There is no default: this tool "
            "reads a live issue tracker, and substituting an unnamed subject is the "
            "defect this argument exists to prevent."
        )
    if args.repo.count("/") != 1 or not all(args.repo.split("/")):
        parser.error(f"--repo must be OWNER/NAME; got {args.repo!r}")

    labels = live_classification_labels(args.repo)
    negative = " ".join(f'-label:"{label}"' for label in labels)
    query = f"repo:{args.repo} is:issue is:open {negative}"
    issues = search_issues(query)
    frozen_at = datetime.now(timezone.utc).isoformat()

    governed_items = []
    private_items = []
    for item in issues:
        body = item.get("body") or ""
        base = {
            "number": item["number"],
            "title": item["title"],
            "url": item["html_url"],
            "created_at": item["created_at"],
            "updated_at": item["updated_at"],
            "labels": sorted(label["name"] for label in item.get("labels", [])),
            "body_sha256": digest(body),
        }
        governed_items.append(base)
        private_items.append({**base, "body": body})

    member_digest = digest("\n".join(str(item["number"]) for item in governed_items))
    snapshot = {
        "schema": "triage-cohort-review-input/1.0",
        "repo": args.repo,
        "frozen_at": frozen_at,
        "population_predicate": "open issue with no live classification label",
        "classification_labels": labels,
        "query": query,
        "count": len(governed_items),
        "member_number_sha256": member_digest,
        "body_custody": "bodies omitted; each item carries a source digest",
        "items": governed_items,
    }
    private = {**snapshot, "body_custody": "temporary review copy", "items": private_items}

    args.snapshot_output.parent.mkdir(parents=True, exist_ok=True)
    args.private_body_output.parent.mkdir(parents=True, exist_ok=True)
    args.snapshot_output.write_text(json.dumps(snapshot, indent=2) + "\n")
    args.private_body_output.write_text(json.dumps(private, indent=2) + "\n")
    print(json.dumps({
        "count": len(governed_items),
        "member_number_sha256": member_digest,
        "snapshot_output": str(args.snapshot_output),
        "private_body_output": str(args.private_body_output),
    }, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
