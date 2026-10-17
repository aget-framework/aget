"""C9 producer regressions: working-tree copies and complete release trees."""
import importlib.util
from datetime import date
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
from instantiate_template import TemplateInstantiator


def load(name, path):
    spec = importlib.util.spec_from_file_location(name, ROOT / path)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


GATE = load('c9_release_gate', 'verification/validate_release_gate.py')
COHERENCE = load('c9_coherence', 'scripts/check_tag_payload_coherence.py')
DEPLOY = load('c9_deploy_skill', 'scripts/deploy_skill.py')


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], check=True,
                          capture_output=True, text=True).stdout.strip()


BAD_PATHS = ['tests/__pycache__/x.cpython-314.pyc', 'scripts/X.PYC',
             'scripts/X.PYO', 'tests/__PYCACHE__/cache.dat']


@pytest.mark.parametrize('tracked', [False, True], ids=['walk', 'git'])
@pytest.mark.parametrize('bad', BAD_PATHS)
def test_instantiation_filters_caches_at_every_depth(tmp_path, tracked, bad):
    src, dst = tmp_path / 'template', tmp_path / 'agent'
    (src / '.aget').mkdir(parents=True)
    (src / '.aget/version.json').write_text(json.dumps({'instance_type': 'template'}))
    (src / '.aget/identity.json').write_text('{}')
    (src / 'tests').mkdir()
    (src / 'tests/test_good.py').write_text('# delivered\n')
    if tracked:
        git(src, 'init', '-q')
        git(src, 'add', '.')
    cache = src / bad
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(b'compiled cache')
    result = TemplateInstantiator(src, 'my-agent-aget', dst).instantiate()
    assert result['success'], result
    assert (dst / 'tests/test_good.py').is_file()
    assert not (dst / bad).exists()


def test_git_copy_delivers_tracked_files_only(tmp_path):
    src, dst = tmp_path / 'template', tmp_path / 'agent'
    src.mkdir()
    git(src, 'init', '-q')
    (src / 'deliver.py').write_text('tracked\n')
    (src / 'alias.py').symlink_to('deliver.py')
    git(src, 'add', '.')
    (src / 'scratch.txt').write_text('untracked\n')
    TemplateInstantiator(src, 'agent-aget', dst)._copy_template(False)
    assert not (dst / 'scratch.txt').exists()
    assert (dst / 'deliver.py').read_text() == 'tracked\n'
    assert (dst / 'alias.py').is_symlink()


@pytest.mark.parametrize('bad', BAD_PATHS)
def test_sibling_skill_deployer_filters_template_caches(tmp_path, monkeypatch, bad):
    source = tmp_path / 'template-worker-aget/.claude/skills'
    skill = source / 'example'
    skill.mkdir(parents=True)
    (skill / 'SKILL.md').write_text('# delivered skill\n')
    cache = skill / bad
    cache.parent.mkdir(parents=True, exist_ok=True)
    cache.write_bytes(b'compiled cache')
    target = tmp_path / 'template-target-aget'
    monkeypatch.setattr(DEPLOY, 'AUDIT_LOG', tmp_path / 'audit.jsonl')
    result = DEPLOY.deploy('example', source, target, True, date(2026, 10, 17))
    assert result['action'] == 'DEPLOYED'
    assert (target / '.claude/skills/example/SKILL.md').is_file()
    assert not (target / '.claude/skills/example' / bad).exists()


@pytest.fixture
def release_tree(tmp_path, monkeypatch):
    tpl = tmp_path / 'template-x-aget'
    tpl.mkdir()
    git(tpl, 'init', '-q')
    for path in COHERENCE.release_coupled_paths('1.0.1'):
        p = tpl / path
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text('release artifact\n')
    monkeypatch.setattr(GATE, 'TEMPLATE_REPOS', [tpl.name])
    return tpl


def commit(repo, message):
    git(repo, 'add', '-A')
    git(repo, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
        'commit', '-qm', message)


@pytest.mark.parametrize('bad', BAD_PATHS)
def test_release_gate_rejects_unchanged_cache_at_target_tag(release_tree, bad):
    tpl = release_tree
    p = tpl / bad
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_bytes(b'cache')
    commit(tpl, 'old release with cache')
    git(tpl, 'tag', 'v1.0.0')
    (tpl / 'CHANGELOG.md').write_text('new release\n')
    commit(tpl, 'unchanged cache')
    git(tpl, 'tag', 'v1.0.1')
    p.unlink()  # a clean working tree must not hide dirty tag contents
    _, failed, issues = GATE.validate_release('1.0.1', tpl, tpl.parent)
    assert 'template_payloads' in issues, issues
    assert any(bad in e for e in issues['template_payloads'])
    assert failed
    assert COHERENCE.check('1.0.1', cwd=str(tpl))[0] == 'FAIL'


def test_release_gate_allows_cache_deletion(release_tree):
    tpl = release_tree
    p = tpl / 'tests/__pycache__/x.pyc'
    p.parent.mkdir(parents=True)
    p.write_bytes(b'old cache')
    commit(tpl, 'old release')
    git(tpl, 'tag', 'v1.0.0')
    p.unlink()
    commit(tpl, 'delete cache')
    git(tpl, 'tag', 'v1.0.1')
    p.write_bytes(b'untracked working-tree cache')
    _, _, issues = GATE.validate_release('1.0.1', tpl, tpl.parent)
    assert 'template_payloads' not in issues
    assert COHERENCE.check('1.0.1', cwd=str(tpl))[0] == 'PASS'


def test_pretag_gate_blocks_compiled_cache_before_publication(release_tree):
    tpl = release_tree
    p = tpl / 'tests/__PYCACHE__/cache.dat'
    p.parent.mkdir(parents=True)
    p.write_bytes(b'cache')
    commit(tpl, 'candidate with cache')
    assert COHERENCE.main(['--version', '1.0.1', '--cwd', str(tpl), '--pre-tag']) == 2


def test_release_gate_fails_when_target_tree_unavailable(release_tree):
    _, _, issues = GATE.validate_release('1.0.1', release_tree, release_tree.parent)
    assert 'template_payloads' in issues
    assert 'v1.0.1' in ' '.join(issues['template_payloads'])
