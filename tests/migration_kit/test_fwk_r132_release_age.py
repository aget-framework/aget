"""The published correction changes only the default wait; receiver controls still bind."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys

import pytest

KIT = Path(__file__).resolve().parents[2] / 'scripts' / 'migration_kit'
spec = importlib.util.spec_from_file_location('r132_adoption_policy', KIT / 'adoption_policy.py')
AP = importlib.util.module_from_spec(spec)
spec.loader.exec_module(AP)

def write_policy(root, policy):
    (root / '.aget').mkdir(exist_ok=True)
    (root / '.aget' / 'adoption_policy.json').write_text(json.dumps(policy))

def cli(root, *args, extra_env=None):
    e = {k: v for k, v in os.environ.items() if not k.startswith('AGET_ADOPTION_')}
    e.update(extra_env or {})
    return subprocess.run([sys.executable, str(KIT / 'adoption_policy.py'), '--root', str(root), *args],
                          env=e, capture_output=True, text=True)

def age(root, *args, extra_env=None):
    return cli(root, '--check-age', '--published', '2026-11-02', '--today', '2026-11-02',
               *args, extra_env=extra_env)

def test_unset_policy_defaults_to_zero_and_reports_ruled(tmp_path):
    res = AP.load(tmp_path, env={})
    assert res['policy']['min_release_age_days'] == 0
    assert res['sources']['min_release_age_days'] == 'default'
    assert 'min_release_age_days' in res['defaults_ruled']
    assert 'min_release_age_days' not in res['defaults_proposed']
    assert res['policy']['wave1_soak'] == {'min_hours': 24, 'min_sessions': 1}
    assert res['policy']['patch_policy'] == 'adopt-if-fixes-me'

@pytest.mark.parametrize('days', [0, 1, 6, 7])
def test_cli_default_adopts_published_minor_during_first_week(tmp_path, days):
    res = cli(tmp_path, '--check-age', '--published', '2026-11-02', '--today', f'2026-11-{2+days:02d}', '--release', '3.38.0')
    assert res.returncode == 0, res.stdout + res.stderr
    assert 'minimum 0 (default)' in res.stdout
    assert 'ADOPT NOW' in res.stdout

def test_default_rejects_future_publication(tmp_path):
    r = cli(tmp_path, '--check-age', '--published', '2026-11-03', '--today', '2026-11-02')
    assert r.returncode == 1
    assert 'DO NOT ADOPT YET' in r.stdout

@pytest.mark.parametrize('declared', ['file', 'env'])
def test_receiver_may_still_require_seven_days(tmp_path, declared):
    e = {}
    if declared == 'file':
        write_policy(tmp_path, {'min_release_age_days': 7})
    else:
        e['AGET_ADOPTION_MIN_RELEASE_AGE_DAYS'] = '7'
    before = age(tmp_path, extra_env=e)
    assert before.returncode == 1
    assert f'minimum 7 ({declared})' in before.stdout
    exact = cli(tmp_path, '--check-age', '--published', '2026-11-02', '--today', '2026-11-09', extra_env=e)
    assert exact.returncode == 0

def test_environment_zero_wins_over_file_wait(tmp_path):
    write_policy(tmp_path, {'min_release_age_days': 7})
    r = age(tmp_path, extra_env={'AGET_ADOPTION_MIN_RELEASE_AGE_DAYS': '0'})
    assert r.returncode == 0
    assert 'minimum 0 (env)' in r.stdout

@pytest.mark.parametrize('value', ['-1', 'banana'])
def test_invalid_environment_is_refused(tmp_path, value):
    assert age(tmp_path, extra_env={'AGET_ADOPTION_MIN_RELEASE_AGE_DAYS': value}).returncode == 2

@pytest.mark.parametrize('policy,fixes,expected', [
    ('adopt-if-fixes-me', False, 1), ('adopt-if-fixes-me', True, 0),
    ('always', False, 0), ('never-alone', True, 1)])
def test_patch_controls_remain_binding_on_publication_day(tmp_path, policy, fixes, expected):
    write_policy(tmp_path, {'patch_policy': policy})
    r = age(tmp_path, '--release', '3.37.1', *(['--fixes-me'] if fixes else []))
    assert r.returncode == expected
    assert 'minimum 0 (default)' in r.stdout

def test_patch_fixes_me_does_not_bypass_receiver_age_override(tmp_path):
    write_policy(tmp_path, {'min_release_age_days': 7, 'patch_policy': 'always'})
    assert age(tmp_path, '--release', '3.37.1', '--fixes-me').returncode == 1

def test_cli_show_reports_zero_and_source(tmp_path):
    r = cli(tmp_path, '--show')
    assert r.returncode == 0
    res = json.loads(r.stdout)
    assert res['policy']['min_release_age_days'] == 0
    assert res['sources']['min_release_age_days'] == 'default'
