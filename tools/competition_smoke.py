#!/usr/bin/env python3
"""Build the frozen competition source and smoke-test Stage 1/2 in IT/NT.

Run on the compatible official Linux SDK. Source files and installed SDK stay
unchanged; only the runtime dictionary is LF-normalized.
"""
import argparse
import hashlib
import importlib.util
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile

sys.dont_write_bytecode = True
ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / 'src1.6.7.1-200ms'


def sha(p):
    return hashlib.sha256(p.read_bytes()).hexdigest()


def product():
    return {p.name: sha(p) for p in SOURCE.iterdir() if p.is_file() and
            (p.suffix in ('.cpp', '.hpp', '.h') or p.name in ('words.txt', 'CMakeLists.txt'))}


def save(p, value):
    p.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--sdk', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    sdk = args.sdk.resolve(); out = args.output.resolve()
    out.mkdir(parents=True, exist_ok=False)
    before = product()
    sdk_before = {str(p.relative_to(sdk)): sha(p) for folder in ('src', 'include', 'res')
                  for p in (sdk / folder).rglob('*') if p.is_file()}
    native = Path(tempfile.mkdtemp(prefix='competition-1671-200-'))
    local = native / 'source'; local.mkdir()
    for name in before: shutil.copy2(str(SOURCE / name), str(local / name))
    assert {name: sha(local / name) for name in before} == before
    command = ['g++', '-std=c++11', '-O2', '-g', '-Wall', '-Wextra', '-pthread',
               '-I' + str(sdk / 'include'), '-I' + str(sdk / 'src'), '-I' + str(local)]
    command += [str(p) for p in sorted(local.glob('*.cpp'))]
    command += ['-L' + str(sdk / 'lib'), '-lframe', '-lutility', '-lboost_thread', '-lboost_system',
                '-lboost_chrono', '-lboost_date_time', '-lboost_regex', '-lpthread', '-ldl', '-o', str(native / 'example')]
    with (out / 'build.log').open('w') as log:
        subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
    subprocess.run(['g++', '-shared', '-fPIC', str(SOURCE / 'tests/seed_rng.cpp'), '-ldl', '-o', str(native / 'seed.so')], check=True)
    assets = out / 'assets'; assets.mkdir()
    (assets / 'words.txt').write_bytes((SOURCE / 'words.txt').read_bytes().replace(b'\r\n', b'\n'))
    helper = ROOT / 'HistoryVersion/src1.1.2 (x)/tools/baseline.py'
    spec = importlib.util.spec_from_file_location('competition_baseline', str(helper))
    runner = importlib.util.module_from_spec(spec); spec.loader.exec_module(runner)
    catalogue = json.loads((ROOT / '题目/2026_comprehensive_200/catalogue.json').read_text(encoding='utf8'))['cases']
    selected = [next(c for c in catalogue if c['stage'] == stage and c['kind'] == 'full') for stage in (1, 2)]
    os.environ.update(LD_PRELOAD=str(native / 'seed.so'), RDFW_TEST_SEED='20260928', RDFW_STAGE_TIMING='0')
    os.environ.pop('RDFW_TASK_GROUP_MODE', None)
    results = []
    for case in selected:
        for mode in ('it', 'nt'):
            key = case['id'] + '-' + mode
            xml = ROOT / '题目/2026_comprehensive_200' / case['path']
            assert sha(xml) == case['sha256']
            result = runner.run_case(sdk, assets, native / 'example', xml, case['stage'], mode, out / key, 5000, None)
            result['id'] = case['id']; result['seed'] = 20260928
            save(out / (key + '.json'), result); results.append(result)
            assert result['status'] == 'ok' and result['official_score'] is not None and result['final_goals'] is not None, result
            assert not result['external_timeout'] and not result['platform_timed_out'], result
            print('SMOKE', key, 'G', result['final_goals'], 'score', result['official_score'], flush=True)
    assert product() == before
    assert all(sha(sdk / p) == value for p, value in sdk_before.items())
    result = {'passed': len(results), 'source_unchanged': True, 'sdk_source_model_unchanged': True,
              'source_sha256': before, 'sdk_sha256': sdk_before,
              'binary_sha256': sha(native / 'example'), 'seed_shim_sha256': sha(native / 'seed.so'),
              'compiler': subprocess.check_output(['g++', '--version']).decode(), 'command': command,
              'native_build': str(native), 'dictionary_policy': 'temporary LF copy',
              'seed': 20260928, 'sdk_deadline_ms': 5000, 'policy': 'default', 'results': results}
    save(out / 'SUMMARY.json', result)
    print('ALL FOUR OFFICIAL SDK SMOKES PASSED', flush=True)


if __name__ == '__main__': main()
