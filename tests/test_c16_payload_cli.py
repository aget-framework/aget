"""Public producer entry points: payload-only checks must be local and blocking."""
import importlib.util
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('c16_release_gate', ROOT / 'verification/validate_release_gate.py')
GATE = importlib.util.module_from_spec(spec)
spec.loader.exec_module(GATE)


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True, check=True)


@pytest.fixture
def framework(tmp_path):
    for name in GATE.TEMPLATE_REPOS:
        repo = tmp_path / name
        repo.mkdir()
        git(repo, 'init', '-q')
        (repo / 'good.py').write_text('# release payload\n')
        git(repo, 'add', '.')
        git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
            'commit', '-qm', 'payload')
        git(repo, 'tag', 'v3.37.0')
    return tmp_path


@pytest.mark.parametrize('entrypoint', ['fleet', 'single'])
@pytest.mark.parametrize('state', ['clean', 'dirty', 'missing-tree', 'missing-repo'])
def test_payload_only_cli(framework, entrypoint, state):
    repo = framework / GATE.TEMPLATE_REPOS[0]
    if state == 'dirty':
        # Unchanged caches still count; a local delete must not hide them.
        (repo / 'X.PYC').write_bytes(b'compiled')
        git(repo, 'add', '.')
        git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
            'commit', '-qm', 'cache')
        git(repo, 'tag', '-f', 'v3.37.0')
        (repo / 'X.PYC').unlink()
    elif state == 'missing-tree':
        git(repo, 'tag', '-d', 'v3.37.0')
        if entrypoint == 'single':
            git(repo, 'update-ref', '-d', 'HEAD')
    elif state == 'missing-repo':
        repo = framework / 'absent'
        (framework / GATE.TEMPLATE_REPOS[0]).rename(framework / 'moved')

    if entrypoint == 'fleet':
        command = [sys.executable, str(ROOT / 'verification/validate_release_gate.py'),
                   '3.37.0', '--payload-only', '--framework-path', str(framework)]
    else:
        command = [sys.executable, str(ROOT / 'scripts/check_tag_payload_coherence.py'),
                   '--version', '3.37.0', '--pre-tag', '--payload-only', '--cwd', str(repo)]
    result = subprocess.run(command, capture_output=True, text=True, stdin=subprocess.DEVNULL, timeout=30)
    assert result.returncode == (0 if state == 'clean' else 2), result.stderr + result.stdout
    assert ('PASS' if state == 'clean' else 'FAIL') in result.stdout
    assert 'payload' in result.stdout.lower()
    if state == 'dirty':
        assert 'X.PYC' in result.stdout
