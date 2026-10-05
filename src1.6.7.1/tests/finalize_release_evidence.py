"""Archive final logs, source/fixture diffs and score-time checks without deletion."""
import difflib
import hashlib
import json
import argparse
import re
import shutil
import zipfile
from pathlib import Path

root = Path(__file__).resolve().parents[2]
current = root / 'src1.6.6'
baseline = root / 'src1.6.5'
out = current / 'test-results/validation-20260928'
out.mkdir(parents=True, exist_ok=True)
parser = argparse.ArgumentParser()
parser.add_argument('--runs', type=Path, default=Path('/tmp/rdfw-166-final'))
args = parser.parse_args()

logs = {
    'unit-config.log': '/tmp/rdfw-166-config.log',
    'unit-build.log': '/tmp/rdfw-166-build.log',
    'asan-config.log': '/tmp/rdfw-166-asan-config.log',
    'asan-build.log': '/tmp/rdfw-166-asan-build.log',
    'baseline-probe-config.log': '/tmp/rdfw-166-probe-config.log',
    'baseline-probe-build.log': '/tmp/rdfw-166-probe-build.log',
    'baseline-probe-ctest.log': '/tmp/rdfw-166-probe-ctest.log',
    'baseline-probe-detail.log': '/tmp/rdfw-166-baseline-probe/Testing/Temporary/LastTest.log',
    'release-matrix.log': str(args.runs) + '.log',
}
for name, source in logs.items():
    shutil.copy2(str(source), str(out / name))
control = args.runs / 'deadline-variation.json'
if control.exists():
    shutil.copy2(str(control), str(out / control.name))
    shutil.copy2('/tmp/rdfw-166-deadline-controls.log', str(out / 'deadline-controls.log'))
    for i in range(1,4):
        suite = 'deadline-self-r' + str(i)
        source = args.runs / suite
        shutil.copy2(str(source / 'results.json'), str(out / (suite + '-results.json')))
        with zipfile.ZipFile(str(out / (suite + '-evidence.zip')), 'w',
                             compression=zipfile.ZIP_DEFLATED) as archive:
            for name in ['server.log','client.log','runtime/vanswer.txt']:
                for item in sorted(source.glob('*/' + name)):
                    archive.write(str(item),str(item.relative_to(source)))

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def delta(old, new):
    a = old.read_text(encoding='utf-8-sig').splitlines(True) if old.exists() else []
    b = new.read_text(encoding='utf-8-sig').splitlines(True)
    return ''.join(difflib.unified_diff(a, b, fromfile=str(old.relative_to(root)),
                                      tofile=str(new.relative_to(root))))

product = [p for p in current.iterdir() if p.suffix in ('.cpp', '.hpp', '.h')
           or p.name in ('CMakeLists.txt', 'words.txt')]
changed = []
for path in sorted(product):
    old = baseline / path.name
    if not old.exists() or digest(old) != digest(path):
        changed.append(path)
(out / 'source.diff').write_text(''.join(delta(baseline / p.name, p) for p in changed), encoding='utf-8')

fixture_changes = []
for path in sorted((current / 'tests').rglob('*.cpp')):
    old = baseline / path.relative_to(current)
    if old.exists() and digest(old) != digest(path):
        fixture_changes.append(path)
(out / 'fixture-migration.diff').write_text(
    ''.join(delta(baseline / p.relative_to(current), p) for p in fixture_changes), encoding='utf-8')

checks = []
behavior = []
for suite in ['full-release', 'target-release-r1', 'target-release-r2', 'target-release-r3', 'off-release']:
    rows = json.loads((out / (suite + '-results.json')).read_text())
    for row in rows:
        if row['baseline']['official'] == row['current']['official']:
            continue
        b, c = row['baseline'], row['current']
        if b['base'] != c['base'] or b['action_sequence'] != c['action_sequence']:
            behavior.append(dict(suite=suite, **row))
            continue
        bonuses = [2 * int((5 - side['platform_seconds']) * 10) for side in (b, c)]
        valid = (b['base'] == c['base'] and b['action_sequence'] == c['action_sequence']
                 and b['official'] == b['base'] + bonuses[0]
                 and c['official'] == c['base'] + bonuses[1])
        assert valid, row
        checks.append(dict(suite=suite, case=row['case'], stage=row['stage'], mode=row['mode'],
                           base=b['base'], official=[b['official'], c['official']],
                           seconds=[b['platform_seconds'], c['platform_seconds']],
                           time_bonus=bonuses, explained_by_sdk_formula=valid))
(out / 'official-time-differences.json').write_text(json.dumps(checks, ensure_ascii=False, indent=2), encoding='utf-8')
(out / 'behavior-differences.json').write_text(json.dumps(behavior, ensure_ascii=False, indent=2), encoding='utf-8')
def passing_tests(path):
    m = re.search(r'100% tests passed, 0 tests failed out of (\d+)', path.read_text())
    assert m, path
    return dict(passed=int(m[1]), total=int(m[1]))

probe = re.search(r'0% tests passed, (\d+) tests failed out of (\d+)',
                  (out / 'baseline-probe-ctest.log').read_text())
assert probe and probe[1] == probe[2], 'All before assertions must reproduce'

manifest = {
    'baseline': 'src1.6.5', 'current': 'src1.6.6',
    'changed_product_files': [p.name for p in changed],
    'fixture_setup_migrations': [p.relative_to(current).as_posix() for p in fixture_changes],
    'product_sha256': {p.name: digest(p) for p in sorted(product)},
    'test_source_sha256': {p.relative_to(current).as_posix(): digest(p)
                           for p in sorted((current / 'tests').rglob('*'))
                           if p.is_file() and p.suffix in ('.cpp', '.hpp', '.h', '.py', '.txt')},
    'baseline_snapshot_files': len(json.loads((current / 'docs/BASELINE_SHA256.json').read_text())),
    'ctest': passing_tests(out / 'ctest-summary.log'),
    'asan_ubsan': passing_tests(out / 'asan-summary.log'),
    'before_probes': {'expected_assertion_failures': int(probe[1]), 'total': int(probe[2])},
    'after_probes': {'passed': int(probe[1]), 'total': int(probe[2])},
    'official_time_differences': len(checks),
    'behavior_differences': len(behavior),
    'regression_summary': json.loads((out / 'summary.json').read_text()),
    'deadline_same_binary_control_pairs': 3 if control.exists() else 0,
}
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print('Archived evidence:', len(changed), 'product changes;', len(fixture_changes), 'fixture migrations;', len(checks), 'SDK time-only differences')
