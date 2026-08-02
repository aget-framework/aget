#!/usr/bin/env python3
"""Validate that release delivery predicates remain distinct and complete."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

PREDICATES = ("producer", "distribution_point", "received_state", "downstream_behavior")


def validate(receipt: dict) -> dict:
    states = {name: receipt.get(name) is True for name in PREDICATES}
    missing = [name for name, passed in states.items() if not passed]
    return {
        "state": "PASS" if not missing else "FAIL",
        "predicates": states,
        "missing": missing,
        "inference_prohibited": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    result = validate(json.loads(args.receipt.read_text()))
    print(json.dumps(result, indent=2) if args.json else f"release-distribution-evidence: {result['state']}")
    return 0 if result["state"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
