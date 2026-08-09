import hashlib
import importlib.util
import json
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/validate_agent_skill_package.py"
SPEC = importlib.util.spec_from_file_location("validate_agent_skill_package", SCRIPT)
module = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(module)


def _fixture(tmp_path: Path) -> tuple[Path, Path]:
    source = tmp_path / ".claude/skills/example-skill"
    package = tmp_path / ".agents/skills/example-skill"
    source.mkdir(parents=True)
    package.mkdir(parents=True)
    skill = source / "SKILL.md"
    skill.write_text(
        "---\nname: example-skill\ndescription: Does an example task when asked.\n"
        "metadata:\n  version: \"1.0\"\nallowed-tools: Read\n---\n\n# Example\n",
        encoding="utf-8",
    )
    (package / "SKILL.md").symlink_to("../../../.claude/skills/example-skill/SKILL.md")
    guide = tmp_path / "docs/GUIDE.md"
    guide.parent.mkdir()
    guide.write_text(
        "Run validate_agent_skill_package.py, then cp -RL the skill. The package does **not** carry hooks.",
        encoding="utf-8",
    )
    manifest = {
        "schema": module.SCHEMA,
        "package": {"name": "example", "version": "1", "license": "Apache-2.0", "distribution": "manual"},
        "manual_guide": "docs/GUIDE.md",
        "skills": [{
            "name": "example-skill",
            "path": ".agents/skills/example-skill",
            "source": ".claude/skills/example-skill",
            "sha256": hashlib.sha256(skill.read_bytes()).hexdigest(),
        }],
        "runtime": {
            "portable": False,
            "substrate": "AGET repository",
            "receiver_owned_paths": [],
            "disclosure": "The package does not carry or digest-bind receiver runtime paths.",
        },
        "enforcement": {
            "portable": False,
            "hooks_included": False,
            "disclosure": "Structural enforcement does not travel with this package.",
        },
    }
    manifest_path = tmp_path / "AGENT_SKILLS_PACKAGE.json"
    manifest_path.write_text(json.dumps(manifest), encoding="utf-8")
    return tmp_path, manifest_path


def test_valid_package_passes(tmp_path):
    root, manifest = _fixture(tmp_path)
    result = module.validate_package(root, manifest)
    assert result["status"] == "PASS", result["errors"]


def test_name_must_match_directory(tmp_path):
    root, manifest = _fixture(tmp_path)
    source = root / ".claude/skills/example-skill/SKILL.md"
    source.write_text(source.read_text().replace("name: example-skill", "name: wrong-name"))
    data = json.loads(manifest.read_text())
    data["skills"][0]["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(data))
    result = module.validate_package(root, manifest)
    assert result["status"] == "FAIL"
    assert any("name must match" in error for error in result["errors"])


def test_allowed_tools_must_be_scalar(tmp_path):
    root, manifest = _fixture(tmp_path)
    source = root / ".claude/skills/example-skill/SKILL.md"
    source.write_text(source.read_text().replace("allowed-tools: Read", "allowed-tools:\n  - Read"))
    data = json.loads(manifest.read_text())
    data["skills"][0]["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    manifest.write_text(json.dumps(data))
    result = module.validate_package(root, manifest)
    assert result["status"] == "FAIL"
    assert any("nested YAML" in error or "allowed-tools" in error for error in result["errors"])


def test_digest_drift_fails(tmp_path):
    root, manifest = _fixture(tmp_path)
    data = json.loads(manifest.read_text())
    data["skills"][0]["sha256"] = "0" * 64
    manifest.write_text(json.dumps(data))
    result = module.validate_package(root, manifest)
    assert any("sha256 mismatch" in error for error in result["errors"])


def test_path_escape_fails(tmp_path):
    root, manifest = _fixture(tmp_path)
    data = json.loads(manifest.read_text())
    data["skills"][0]["path"] = "../outside"
    manifest.write_text(json.dumps(data))
    result = module.validate_package(root, manifest)
    assert any("escapes/misses" in error for error in result["errors"])


def test_invoked_runtime_target_must_be_declared_and_exist(tmp_path):
    root, manifest = _fixture(tmp_path)
    source = root / ".claude/skills/example-skill/SKILL.md"
    source.write_text(source.read_text() + "\n```bash\npython3 scripts/missing.py\n```\n")
    data = json.loads(manifest.read_text())
    data["skills"][0]["sha256"] = hashlib.sha256(source.read_bytes()).hexdigest()
    data["runtime"]["receiver_owned_paths"] = ["scripts/missing.py"]
    manifest.write_text(json.dumps(data))
    result = module.validate_package(root, manifest)
    assert result["status"] == "FAIL"
    assert any("runtime target is absent" in error for error in result["errors"])


def test_live_package_passes():
    root = Path(__file__).resolve().parents[1]
    result = module.validate_package(root, root / "AGENT_SKILLS_PACKAGE.json")
    assert result["status"] == "PASS", result["errors"]
