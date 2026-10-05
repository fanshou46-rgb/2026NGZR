"""Create a separate experiment; frozen release sources are never rewritten."""
from pathlib import Path
import hashlib, json, shutil

ROOT = Path(__file__).resolve().parents[2]
LAB = ROOT / 'experiments/full_probability'
SOURCE = ROOT / 'src1.7.7'

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

def main():
    receipt = LAB / 'source-receipt.json'
    if receipt.exists():
        saved = json.loads(receipt.read_text(encoding='utf8'))
        for relative, expected in saved['frozen_sources'].items():
            assert digest(ROOT / relative) == expected, relative
        print('EXISTING LAB; frozen releases verified')
        return
    assert not LAB.exists(), 'Refuse to overwrite an unregistered experiment'
    source = LAB / 'source'
    source.mkdir(parents=True)
    copied = {}
    for path in SOURCE.iterdir():
        if path.suffix in ('.cpp', '.hpp', '.h') or path.name in ('words.txt', 'CMakeLists.txt'):
            shutil.copy2(path, source / path.name)
            copied[path.name] = digest(path)
    shutil.copytree(SOURCE / 'tests', source / 'tests', ignore=shutil.ignore_patterns('__pycache__', 'test-results'))
    frozen = {}
    for release in ('src1.7.7', 'src1.6.7-200ms', 'HistoryVersion/src1.6.7'):
        for path in (ROOT / release).iterdir():
            if path.suffix in ('.cpp', '.hpp', '.h') or path.name == 'words.txt':
                frozen[path.relative_to(ROOT).as_posix()] = digest(path)
    receipt.write_text(json.dumps(dict(base_commit='68fe263b096e0d3075da4c358fe9560a98ebf359',
        copied=copied, frozen_sources=frozen, experiment='unversioned full probability policy',
        accepted_criteria='formal score improves; goals/base do not deteriorate; evidence-backed probes allowed'),
        ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    (LAB / '.gitignore').write_text('builds/\nchecks/\nruns/\nassets/\n*.jsonl\n__pycache__/\n', encoding='utf8')
    print('CREATED', LAB)

if __name__ == '__main__':
    main()
