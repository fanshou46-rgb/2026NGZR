#!/usr/bin/env python3
"""Archive exact benchmark evidence, storing repeated SDK resources once."""
import argparse
import hashlib
import json
from pathlib import Path
import zipfile


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--full', type=Path, required=True)
    parser.add_argument('--pilot', type=Path, required=True)
    parser.add_argument('--checks', type=Path, required=True)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    assert (args.full / 'final-audit.json').exists(), 'benchmark must finish first'
    assert not args.output.exists(), 'preserve previous archives'
    args.output.parent.mkdir(parents=True, exist_ok=True)
    files = []
    for label, root in [('full', args.full), ('pilot', args.pilot)]:
        files.extend((label + '/' + p.relative_to(root).as_posix(), p)
                     for p in sorted(root.rglob('*')) if p.is_file())
    files.extend(('checks/' + p.name, p) for p in sorted(args.checks.iterdir()) if p.is_file())
    for name in ('unit', 'asan', 'asan-o2'):
        root = args.checks / name
        for p in sorted(root.rglob('*')):
            if p.is_file() and (p.name == 'CMakeCache.txt' or 'Testing' in p.parts):
                files.append(('checks/' + p.relative_to(args.checks).as_posix(), p))
    manifest = {}; stored = set(); raw_bytes = 0
    with zipfile.ZipFile(str(args.output), 'x', compression=zipfile.ZIP_DEFLATED, allowZip64=True) as archive:
        for logical, path in files:
            payload = path.read_bytes()
            digest = hashlib.sha256(payload).hexdigest()
            manifest[logical] = dict(sha256=digest, bytes=len(payload), mode=path.stat().st_mode & 0o777)
            raw_bytes += len(payload)
            if digest not in stored:
                archive.writestr('blobs/' + digest, payload)
                stored.add(digest)
        index = dict(format='sha256-content-addressed-v1', files=manifest,
                     files_count=len(manifest), unique_blobs=len(stored), raw_bytes=raw_bytes,
                     checks_policy='all top-level logs and receipts; CMakeCache and Testing logs; build objects omitted')
        archive.writestr('MANIFEST.json', json.dumps(index, ensure_ascii=False, indent=2) + '\n')
    with zipfile.ZipFile(str(args.output)) as archive:
        assert archive.testzip() is None
        for digest in stored:
            assert hashlib.sha256(archive.read('blobs/' + digest)).hexdigest() == digest
        assert json.loads(archive.read('MANIFEST.json').decode('utf8')) == index
    receipt = dict(archive=args.output.name, sha256=hashlib.sha256(args.output.read_bytes()).hexdigest(),
                   archive_bytes=args.output.stat().st_size, logical_files=len(manifest),
                   unique_blobs=len(stored), raw_bytes=raw_bytes, crc_and_sha256_verified=True)
    args.output.with_suffix('.receipt.json').write_text(json.dumps(receipt, indent=2) + '\n')
    print(json.dumps(receipt))


if __name__ == '__main__':
    main()
