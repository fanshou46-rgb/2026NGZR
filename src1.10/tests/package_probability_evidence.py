#!/usr/bin/env python3
"""Preserve every experiment, including regressions; verify archive contents."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import zipfile

SOURCE = Path(__file__).resolve().parents[1]


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--suites', nargs='+', required=True, type=Path)
    parser.add_argument('--snapshots', nargs='*', default=[], type=Path)
    parser.add_argument('--logs', nargs='*', default=[], type=Path)
    parser.add_argument('--output', required=True, type=Path)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=False)
    manifest = dict(archives=[], scope='development evidence, not a competition release')
    trees = [(p.name, p) for p in args.suites]
    for _, tree in trees:
        audit = json.loads((tree / 'final-audit.json').read_text(encoding='utf-8'))
        assert all(audit[k] for k in ('products_unchanged', 'inputs_unchanged', 'sdk_model_unchanged')), tree
        assert not audit['violations'], tree
    trees.extend((p.name, p) for p in args.snapshots)
    trees.append(('current-source', SOURCE))
    for name, tree in trees:
        archive = args.output / (name + '.zip')
        files, omitted = {}, {}
        with zipfile.ZipFile(str(archive), 'w', compression=zipfile.ZIP_DEFLATED) as z:
            paths = []
            for directory, children, names in os.walk(str(tree)):
                if tree == SOURCE:
                    children[:] = [n for n in children if n not in ('test-results', '__pycache__')]
                paths.extend(Path(directory) / n for n in names)
            for path in sorted(paths):
                relative = path.relative_to(tree)
                digest = sha(path)
                if path.name in ('iclingo', 'example', 'seed.so'):
                    omitted[relative.as_posix()] = digest
                    continue  # duplicate executables are identified by SHA, not erased locally
                files[relative.as_posix()] = digest
                z.write(str(path), relative.as_posix())
        with zipfile.ZipFile(str(archive)) as z:
            assert z.testzip() is None
            assert set(z.namelist()) == set(files)
            for relative, digest in files.items():
                assert hashlib.sha256(z.read(relative)).hexdigest() == digest
        manifest['archives'].append(dict(name=archive.name, sha256=sha(archive), files=files, omitted_binaries=omitted))
    archive = args.output / 'local-checks.zip'
    with zipfile.ZipFile(str(archive), 'w', compression=zipfile.ZIP_DEFLATED) as z:
        for path in args.logs:
            assert path.is_file(), path
            z.write(str(path), path.name)
    with zipfile.ZipFile(str(archive)) as z:
        assert z.testzip() is None
    manifest['archives'].append(dict(name=archive.name, sha256=sha(archive),
        files={p.name: sha(p) for p in args.logs}))
    (args.output / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print('Verified archives:', len(manifest['archives']))


if __name__ == '__main__':
    main()
