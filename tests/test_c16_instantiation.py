"""Small instantiation corrections: preflight tracked inputs and archive scope."""
import json
from pathlib import Path
import subprocess
import sys

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from instantiate_template import TemplateInstantiator


def git(repo, *args):
    return subprocess.run(['git', '-C', str(repo), *args], capture_output=True,
                          text=True, check=True).stdout.strip()


@pytest.fixture
def template(tmp_path):
    src = tmp_path / 'template'
    (src / '.aget').mkdir(parents=True)
    (src / '.aget/version.json').write_text(json.dumps({'instance_type': 'template'}))
    (src / '.aget/identity.json').write_text('{}')
    for name in ['a.py', 'z.py']:
        (src / name).write_text('# payload\n')
    git(src, 'init', '-q')
    git(src, 'add', '.')
    git(src, '-c', 'user.name=Fixture', '-c', 'user.email=fixture@example.test',
        'commit', '-qm', 'template')
    return src


@pytest.mark.parametrize('sparse', [False, True], ids=['deleted', 'sparse'])
def test_missing_tracked_input_refuses_before_copy(template, tmp_path, sparse):
    if sparse:
        git(template, 'sparse-checkout', 'set', '--no-cone', '/.aget/', '/z.py')
    else:
        (template / 'a.py').unlink()
    dst = tmp_path / 'agent'
    result = TemplateInstantiator(template, 'my-agent-aget', dst).instantiate()
    assert not result['success']
    assert 'tracked file unavailable: a.py' in result['error']
    assert not dst.exists(), 'preflight refusal must leave no partial instance'


@pytest.mark.parametrize('populated', [False, True])
def test_submodule_refuses_before_copy(template, tmp_path, populated):
    head = git(template, 'rev-parse', 'HEAD')
    git(template, 'update-index', '--add', '--cacheinfo', f'160000,{head},vendor')
    if populated:
        (template / 'vendor').mkdir()
        (template / 'vendor/lib.py').write_text('# submodule\n')
    dst = tmp_path / 'agent'
    result = TemplateInstantiator(template, 'my-agent-aget', dst).instantiate()
    assert not result['success']
    assert 'unsupported submodule: vendor' in result['error']
    assert not dst.exists()


@pytest.mark.parametrize('tracked', [False, True], ids=['walk', 'git'])
def test_archive_exclusions_keep_original_scope(tmp_path, tracked):
    src, dst = tmp_path / 'template', tmp_path / 'agent'
    delivered = ['docs/archive/old.md', 'docs/Archive/old.md', 'Archive/old.md', '.aget/Archive/old.md']
    excluded = ['archive', '.aget/archive/old.md']
    # macOS's default filesystem folds case: test one path at a time.
    for i, relative in enumerate(delivered + excluded):
        case_src, case_dst = src / str(i), dst / str(i)
        p = case_src / relative
        p.parent.mkdir(parents=True)
        p.write_text('payload\n')
        if tracked:
            git(case_src, 'init', '-q')
            git(case_src, 'add', '.')
        TemplateInstantiator(case_src, 'my-agent-aget', case_dst)._copy_template(False)
        assert (case_dst / relative).exists() == (relative in delivered), relative
