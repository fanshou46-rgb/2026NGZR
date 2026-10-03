#!/usr/bin/env python3
"""Analysis-only adapter; import unchanged production validation harness."""
import importlib.util
import json
from pathlib import Path
import sys

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location('frozen_probe_runner', ROOT/'src1.7.1/tests/run_probe_compare.py')
runner = importlib.util.module_from_spec(spec)
spec.loader.exec_module(runner)
runner.BASELINE = ROOT/'src1.6.7-200ms'

def original_71(suite):
    assert suite == 'legacy'
    audit = json.loads((ROOT/'src1.7/test-results/validation-20261002/input-audit.json').read_text())
    result = []
    for item in audit['cases']:
        relative = item['path'].split('/2026NGZR/', 1)[1]
        candidates = [ROOT/relative]
        if relative.startswith('src1.6.'):
            candidates += [ROOT/'HistoryVersion'/relative, ROOT/'src1.7/tests'/relative.split('/tests/',1)[1]]
        path = next((p for p in candidates if p.is_file() and runner.sha(p)==item['sha256']), None)
        assert path, (relative,item['sha256'])
        result.append(dict(item,path=str(path),kind='scored',suite='legacy',original_suite=item['suite']))
    assert len(result)==71
    return result

runner.cases = original_71
if __name__ == '__main__':
    runner.main()
