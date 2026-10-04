"""Verify published Git bytes match the sources and inputs actually checked."""
import argparse
import hashlib
import json
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'validation/review176-20261004'

def digest(data):
    return hashlib.sha256(data).hexdigest()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--ref', default=':', help=': for index, otherwise commit/ref')
    parser.add_argument('--output', default='staged-publication-audit.json')
    args = parser.parse_args()
    audit = json.loads((OUT / 'frozen-audit.json').read_text(encoding='utf8'))
    expected = {}
    for version, files in audit['sources'].items():
        for name, value in files.items():
            expected[version + '/' + name.replace('\\', '/')] = value
    for category in ('inputs', 'tooling'):
        for name, value in audit[category].items():
            expected[name.replace('\\', '/')] = value
    checked = json.loads((OUT / 'checks/pre-final-check-source-hashes.json').read_text(encoding='utf8'))
    for name, value in checked.items():
        path = 'src1.7.6/' + name.replace('\\', '/')
        assert path not in expected or expected[path] == value
        expected[path] = value
    failures = []
    normalized = []
    archive = OUT / 'checks/executed-input-tooling.zip'
    for path, value in sorted(expected.items()):
        spec = ':' + path if args.ref == ':' else args.ref + ':' + path
        blob = subprocess.check_output(['git', 'show', spec], cwd=str(ROOT))
        actual = (ROOT / path).read_bytes()
        if digest(actual) != value:
            failures.append(path)
        elif digest(blob) != value:
            # Older tracked XML/catalogue/helper files were already normalized
            # by Git. Do not rewrite historical versions: publish executed bytes
            # separately and explicitly record this representation difference.
            if blob != actual.replace(b'\r\n', b'\n') or path.startswith('src1.7.6/'):
                failures.append(path)
            else:
                spec_archive = (':' if args.ref == ':' else args.ref + ':') + archive.relative_to(ROOT).as_posix()
                archive_blob = subprocess.check_output(['git','show',spec_archive],cwd=str(ROOT))
                assert digest(archive_blob) == digest(archive.read_bytes())
                with zipfile.ZipFile(str(archive)) as z:
                    assert digest(z.read(path)) == value
                normalized.append(path)
    assert not failures, failures
    result = dict(ref=args.ref, exact_git_and_workspace_files=len(expected)-len(normalized),
                  checked_files=len(checked), mismatches=failures,
                  historical_git_line_ending_differences=normalized,
                  exact_executed_input_tooling_archive_sha256=digest(archive.read_bytes()),
                  expected_sha256=expected)
    (OUT / 'checks' / args.output).write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf8')
    print('Verified files:',len(expected),'exact Git bytes:',len(expected)-len(normalized),
          'historical newline variants archived exactly:',len(normalized))

if __name__ == '__main__':
    main()
