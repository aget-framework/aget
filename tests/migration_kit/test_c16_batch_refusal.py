"""A refused template blocks its members, leaving the rest of the batch usable."""
import importlib.util
import json
from pathlib import Path
import subprocess
import sys

import pytest

ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('c16_prepare_batch', ROOT / 'scripts/migration_kit/prepare_batch.py')
PB = importlib.util.module_from_spec(spec)
spec.loader.exec_module(PB)


@pytest.mark.parametrize('refusal', ['unresolved', 'payload'])
def test_mixed_batch_preserves_member_blocks(tmp_path, monkeypatch, capsys, refusal):
    names = ['good', 'blocked-one', 'blocked-two']
    for name in names:
        (tmp_path / name).mkdir()
    monkeypatch.setattr(PB.L, 'members', lambda: [(n, str(tmp_path / n)) for n in names])
    monkeypatch.setattr(PB.L, 'usable_template', lambda loc, name:
                        ('template-good-aget', 'declared') if name == 'good' else
                        ((None, 'inferred') if refusal == 'unresolved' else ('template-bad-aget', 'declared')))
    monkeypatch.setattr(PB.CI, 'head_of', lambda loc: 'a' * 40)

    def expectations(template):
        if template == 'template-bad-aget':
            raise PB.L.Unavailable('compiled cache: tests/__pycache__/bad.pyc')
        return {}

    monkeypatch.setattr(PB.L, 'payload_expectations', expectations)
    monkeypatch.setattr(PB.subprocess, 'run', lambda cmd, **kw:
                        subprocess.CompletedProcess(cmd, 0, 'fixture', ''))
    out = tmp_path / 'list.json'
    monkeypatch.setattr(sys, 'argv', ['prepare_batch', '--batch', 'B1', '--out', str(out), *names])
    assert PB.main() == 0
    entries = json.loads(out.read_text())['agets']
    assert 'blocked' not in entries[0]
    reason = ('template unresolved: inferred' if refusal == 'unresolved' else
              'release payload refused: compiled cache: tests/__pycache__/bad.pyc')
    assert [entry['blocked'] for entry in entries[1:]] == [reason, reason]
    assert all(entry['ops'] == [] for entry in entries[1:])
    assert capsys.readouterr().out.count('BLOCKED: ' + reason) == 2
