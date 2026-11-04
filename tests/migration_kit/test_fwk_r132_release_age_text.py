"""Current adoption defaults must agree across implementation explanation and receiver SOP."""
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]

def test_sop_example_and_default_row_use_ruled_zero():
    text = (ROOT / 'sops/SOP_fleet_migration.md').read_text()
    section = text.split('### Receiver adoption policy, skew limit and batch halt', 1)[1]
    example = re.search(r'```json\n(.*?)\n```', section, re.S)
    assert example is not None
    assert json.loads(example.group(1))['min_release_age_days'] == 0
    row = re.search(r'^\| `min_release_age_days` \| (.*?) \| (.*?) \|$', section, re.M)
    assert row is not None
    assert row.group(1).strip() == '0'
    assert 'ruled' in row.group(2).lower()

def test_ruled_age_explanation_is_outside_producer_proposals():
    text = (ROOT / 'scripts/migration_kit/adoption_policy.py').read_text()
    assert text.index('min_release_age_days 0:') < text.index('    the others       producer proposals')
