#!/usr/bin/env python3
"""Validate AGET's bounded Agent Skills package using only the Python standard library.

The check enforces the normative frontmatter constraints published at
https://agentskills.io/specification as verified 2026-08-08, plus AGET's
package-manifest, digest, path-containment, and enforcement-disclosure contract.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


SCHEMA = "aget.agent-skills-package.v1"
NAME_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
ALLOWED_FIELDS = {
    "name", "description", "license", "compatibility", "metadata", "allowed-tools"
}


def _scalar(raw: str) -> str:
    value = raw.strip()
    if len(value) >= 2 and value[0] == value[-1] == '"':
        parsed = json.loads(value)
        if not isinstance(parsed, str):
            raise ValueError("quoted scalar is not a string")
        return parsed
    if len(value) >= 2 and value[0] == value[-1] == "'":
        return value[1:-1].replace("''", "'")
    return value


def parse_frontmatter(path: Path) -> tuple[dict, str, list[str]]:
    errors: list[str] = []
    try:
        text = path.read_text(encoding="utf-8")
    except OSError as exc:
        return {}, "", [f"cannot read {path}: {exc}"]
    lines = text.splitlines()
    if not lines or lines[0].strip() != "---":
        return {}, "", [f"{path}: SKILL.md must begin with YAML frontmatter"]
    try:
        end = next(i for i, line in enumerate(lines[1:], 1) if line.strip() == "---")
    except StopIteration:
        return {}, "", [f"{path}: frontmatter has no closing ---"]

    data: dict[str, object] = {}
    current: str | None = None
    for number, line in enumerate(lines[1:end], 2):
        if not line.strip() or line.lstrip().startswith("#"):
            continue
        if line[:1].isspace():
            if current != "metadata":
                errors.append(f"{path}:{number}: nested YAML is supported only for metadata")
                continue
            match = re.match(r"^\s+([^:#]+):\s*(.*)$", line)
            if not match:
                errors.append(f"{path}:{number}: malformed metadata entry")
                continue
            key, raw = match.groups()
            value = _scalar(raw)
            if not key.strip() or not value:
                errors.append(f"{path}:{number}: metadata keys and values must be non-empty strings")
            else:
                metadata = data.setdefault("metadata", {})
                assert isinstance(metadata, dict)
                metadata[key.strip()] = value
            continue
        match = re.match(r"^([A-Za-z][A-Za-z0-9-]*):\s*(.*)$", line)
        if not match:
            errors.append(f"{path}:{number}: unsupported YAML form")
            current = None
            continue
        key, raw = match.groups()
        if key in data:
            errors.append(f"{path}:{number}: duplicate frontmatter field {key}")
        current = key
        if key == "metadata" and not raw.strip():
            data[key] = {}
        elif not raw.strip():
            errors.append(f"{path}:{number}: {key} must be a scalar string")
            data[key] = ""
        else:
            data[key] = _scalar(raw)

    body = "\n".join(lines[end + 1:]).strip()
    if not body:
        errors.append(f"{path}: Markdown body is empty")
    return data, body, errors


def validate_skill(skill_dir: Path, expected_name: str) -> list[str]:
    path = skill_dir / "SKILL.md"
    data, _body, errors = parse_frontmatter(path)
    unknown = sorted(set(data) - ALLOWED_FIELDS)
    if unknown:
        errors.append(f"{path}: unsupported frontmatter fields: {', '.join(unknown)}")
    name = data.get("name")
    if not isinstance(name, str) or not NAME_RE.fullmatch(name) or len(name) > 64:
        errors.append(f"{path}: name must be 1-64 lowercase alphanumeric/hyphen characters")
    if name != expected_name or name != skill_dir.name:
        errors.append(f"{path}: name must match manifest and parent directory ({expected_name})")
    description = data.get("description")
    if not isinstance(description, str) or not 1 <= len(description) <= 1024:
        errors.append(f"{path}: description must be a non-empty string of at most 1024 characters")
    for field, limit in (("license", 500), ("compatibility", 500)):
        value = data.get(field)
        if value is not None and (not isinstance(value, str) or not 1 <= len(value) <= limit):
            errors.append(f"{path}: {field} must be a non-empty string of at most {limit} characters")
    allowed = data.get("allowed-tools")
    if allowed is not None and (not isinstance(allowed, str) or not allowed.strip()):
        errors.append(f"{path}: allowed-tools must be a non-empty space-separated string")
    metadata = data.get("metadata")
    if metadata is not None and (
        not isinstance(metadata, dict)
        or any(not isinstance(k, str) or not isinstance(v, str) for k, v in metadata.items())
    ):
        errors.append(f"{path}: metadata must map strings to strings")
    return errors


def _inside(root: Path, path: Path) -> bool:
    try:
        path.resolve(strict=True).relative_to(root.resolve(strict=True))
        return True
    except (OSError, ValueError):
        return False


def validate_package(root: Path, manifest_path: Path) -> dict:
    errors: list[str] = []
    try:
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        return {"status": "FAIL", "errors": [f"cannot load manifest: {exc}"], "skills_checked": 0}

    if manifest.get("schema") != SCHEMA:
        errors.append(f"schema must equal {SCHEMA}")
    package = manifest.get("package")
    if not isinstance(package, dict) or package.get("distribution") != "manual":
        errors.append("package.distribution must equal manual")
    enforcement = manifest.get("enforcement")
    if not isinstance(enforcement, dict):
        errors.append("enforcement disclosure is required")
    else:
        if enforcement.get("portable") is not False or enforcement.get("hooks_included") is not False:
            errors.append("v3.30 bounded package must declare portable=false and hooks_included=false")
        disclosure = enforcement.get("disclosure")
        if not isinstance(disclosure, str) or not re.search(
            r"\bdo(?:es)? not travel\b", disclosure.lower()
        ):
            errors.append("enforcement.disclosure must state that structural enforcement does not travel")

    runtime = manifest.get("runtime")
    receiver_owned_paths: set[str] = set()
    if not isinstance(runtime, dict):
        errors.append("runtime disclosure is required")
    else:
        if runtime.get("portable") is not False or runtime.get("substrate") != "AGET repository":
            errors.append("runtime must declare portable=false and substrate=AGET repository")
        raw_paths = runtime.get("receiver_owned_paths")
        if not isinstance(raw_paths, list) or any(
            not isinstance(path, str) or not path for path in raw_paths
        ):
            errors.append("runtime.receiver_owned_paths must be a list of non-empty strings")
        else:
            receiver_owned_paths = set(raw_paths)
        runtime_disclosure = runtime.get("disclosure")
        if not isinstance(runtime_disclosure, str) or not re.search(
            r"\bdoes not carry or digest-bind\b", runtime_disclosure.lower()
        ):
            errors.append("runtime.disclosure must state that receiver runtime does not carry or digest-bind")

    guide = manifest.get("manual_guide")
    guide_path = root / guide if isinstance(guide, str) else root / "__missing__"
    if not isinstance(guide, str) or not _inside(root, guide_path) or not guide_path.is_file():
        errors.append("manual_guide must resolve to a file inside the repository")
    else:
        guide_text = guide_path.read_text(encoding="utf-8")
        for required in ("validate_agent_skill_package.py", "cp -RL", "does **not** carry"):
            if required not in guide_text:
                errors.append(f"manual guide lacks required disclosure/instruction: {required}")

    skills = manifest.get("skills")
    if not isinstance(skills, list) or not skills:
        errors.append("skills must be a non-empty list")
        skills = []
    seen: set[str] = set()
    for index, item in enumerate(skills):
        if not isinstance(item, dict):
            errors.append(f"skills[{index}] must be an object")
            continue
        name, rel, source, digest = (item.get(k) for k in ("name", "path", "source", "sha256"))
        if not all(isinstance(v, str) and v for v in (name, rel, source, digest)):
            errors.append(f"skills[{index}] requires non-empty name/path/source/sha256 strings")
            continue
        if name in seen:
            errors.append(f"duplicate skill name: {name}")
        seen.add(name)
        skill_dir, source_dir = root / rel, root / source
        skill_md, source_md = skill_dir / "SKILL.md", source_dir / "SKILL.md"
        if not _inside(root, skill_md) or not _inside(root, source_md):
            errors.append(f"{name}: package or source path escapes/misses repository")
            continue
        if skill_md.resolve() != source_md.resolve():
            errors.append(f"{name}: package path does not resolve to declared canonical source")
        actual = hashlib.sha256(skill_md.read_bytes()).hexdigest()
        if not re.fullmatch(r"[0-9a-f]{64}", digest) or actual != digest:
            errors.append(f"{name}: sha256 mismatch (manifest={digest}, actual={actual})")
        errors.extend(validate_skill(skill_dir, name))
        body = skill_md.read_text(encoding="utf-8")
        for target in sorted(set(re.findall(r"\bpython3?\s+(scripts/[A-Za-z0-9_./-]+\.py)\b", body))):
            if target not in receiver_owned_paths:
                errors.append(f"{name}: invoked runtime target is not declared receiver-owned: {target}")
                continue
            target_path = root / target
            if not _inside(root, target_path) or not target_path.is_file():
                errors.append(f"{name}: declared receiver runtime target is absent from AGET source: {target}")

    return {
        "status": "PASS" if not errors else "FAIL",
        "schema": manifest.get("schema"),
        "manifest": str(manifest_path),
        "skills_checked": len(skills),
        "errors": errors,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--root", type=Path, default=Path(__file__).resolve().parent.parent)
    parser.add_argument("--manifest", type=Path)
    parser.add_argument("--json", action="store_true")
    args = parser.parse_args()
    root = args.root.resolve()
    manifest = args.manifest.resolve() if args.manifest else root / "AGENT_SKILLS_PACKAGE.json"
    result = validate_package(root, manifest)
    if args.json:
        print(json.dumps(result, indent=2))
    else:
        print(f"Agent Skills package: {result['status']} ({result['skills_checked']} skills)")
        for error in result["errors"]:
            print(f"  FAIL: {error}")
    return 0 if result["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
