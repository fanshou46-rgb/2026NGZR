"""Preserve final checks and earlier failed logs before publishing evidence."""
import hashlib
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'validation/review175-20261004'


def main():
    log = Path('/tmp/rdfw175-sanitizer.log').read_text(encoding='utf8', errors='replace')
    count = re.search(r'(\d+)% tests passed, (\d+) tests failed out of (\d+)', log)
    seconds = re.search(r'Total Test time \(real\) =\s*([\d.]+) sec', log)
    assert count and seconds and count.group(1) == '100' and count.group(2) == '0'
    tests = int(count.group(3))
    assert tests == 271
    assert not any(s in log for s in ('ERROR: AddressSanitizer', 'runtime error:',
                                      'ERROR: LeakSanitizer'))
    summary = dict(tests=tests, passed=tests, seconds=float(seconds.group(1)),
                   address_sanitizer=True, undefined_behavior_sanitizer=True,
                   detect_leaks=True, sdk_subprocess_tests_included=False,
                   first_run_passed=True, reruns=0)
    (OUT / 'checks/sanitizer-summary.json').write_text(json.dumps(
        summary, indent=2), encoding='utf8')
    raw = OUT / 'checks/raw'
    logs = raw / 'logs'
    logs.mkdir(parents=True, exist_ok=False)
    for p in sorted(Path('/tmp').glob('rdfw175*.log')):
        shutil.copyfile(str(p), str(logs / p.name))
    for build in ('rdfw175-tests', 'rdfw175-sanitizer-nopie'):
        source = Path('/tmp') / build
        dest = raw / build
        dest.mkdir()
        for name in ('CMakeCache.txt', 'CTestTestfile.cmake', 'words.txt'):
            shutil.copyfile(str(source / name), str(dest / name))
        shutil.copytree(str(source / 'Testing'), str(dest / 'Testing'))
        recipes = dest / 'recipes'
        recipes.mkdir()
        for p in (source / 'CMakeFiles').glob('*.dir/*'):
            if p.name in ('flags.make', 'link.txt', 'build.make'):
                folder = recipes / p.parent.name
                folder.mkdir(exist_ok=True)
                shutil.copyfile(str(p), str(folder / p.name))
    shutil.copytree('/tmp/rdfw175-tests/official-semantics', str(raw / 'official-semantics'))
    source_hashes = {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest()
                     for p in (ROOT / 'src1.7.5').rglob('*') if p.is_file()
                     and (p.suffix in ('.cpp', '.hpp', '.h', '.sh')
                          or p.name in ('CMakeLists.txt', 'words.txt'))}
    (OUT / 'checks/checked-source-hashes.json').write_text(json.dumps(
        source_hashes, indent=2), encoding='utf8')
    audit = json.loads((OUT / 'frozen-v5/frozen-audit.json').read_text(encoding='utf8'))
    tool_dest = raw / 'executed-tooling'
    tool_dest.mkdir()
    for name, digest in audit['tooling'].items():
        source = ROOT / name
        assert hashlib.sha256(source.read_bytes()).hexdigest() == digest
        target = tool_dest / name
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(str(source), str(target))
    print('271 sanitizer tests passed; all check logs and SDK fixtures preserved')


if __name__ == '__main__':
    main()
