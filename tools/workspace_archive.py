#!/usr/bin/env python3
"""Inventory, content-addressed evidence archive and exact-path recovery.

Only inventory/archive/restore are implemented here. Deletion is a separate,
reviewable PowerShell step after archive and live-file validation.
"""
import argparse
import hashlib
import heapq
import json
import os
import stat
import subprocess
import time
import zipfile
from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
HOME = ROOT.parent
OUT = ROOT / 'logs/workspace_cleanup_20261007'
ARCHIVES = ROOT / 'logs/evidence_archives'
CHUNK = 8 * 1024 * 1024
PART = 32 * 1024 * 1024


def native(path):
    value = os.path.abspath(str(path))
    if os.name == 'nt' and not value.startswith('\\\\?\\'):
        return '\\\\?\\' + value
    return value


def plain(path):
    return str(path).removeprefix('\\\\?\\')


def sha(path):
    h = hashlib.sha256()
    with open(native(path), 'rb') as stream:
        # Avoid repeated 8MiB allocations for hundreds of thousands of tiny
        # runtime files; this preserves exactly the same SHA256 byte stream.
        for block in iter(lambda: stream.read(64 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2) + '\n', encoding='utf8')


def git(*args, cwd=ROOT):
    return subprocess.check_output(['git', '-C', str(cwd), *args]).decode('utf8')


def scan(root):
    sizes = defaultdict(int); records = {}; skipped = []; errors = []; stack = [native(root)]
    while stack:
        directory = stack.pop(); sizes[plain(directory)] += 0
        try:
            with os.scandir(directory) as entries:
                for entry in entries:
                    try:
                        s = entry.stat(follow_symlinks=False)
                        if getattr(s, 'st_file_attributes', 0) & 0x400 or entry.is_symlink():
                            skipped.append(plain(entry.path)); continue
                        if entry.is_dir(follow_symlinks=False):
                            stack.append(entry.path); continue
                        p = plain(entry.path)
                        records[p] = {'bytes': s.st_size, 'mtime_ns': s.st_mtime_ns,
                                      'mode': stat.S_IMODE(s.st_mode)}
                        sizes[plain(directory)] += s.st_size
                    except OSError as e:
                        errors.append({'path': plain(entry.path), 'error': str(e)})
        except OSError as e:
            errors.append({'path': plain(directory), 'error': str(e)})
    for directory in sorted(sizes, key=lambda p: p.count(os.sep), reverse=True):
        if directory != str(root): sizes[os.path.dirname(directory)] += sizes[directory]
    return records, sizes, skipped, errors


def other_states():
    result = {}
    for name in ('2026NGZR', 'stage2-location-recovery', 'stage2-location-recovery-v16-pr'):
        work = HOME / name
        paths = set(git('ls-files', '-z', '--modified', '--others', '--exclude-standard', cwd=work).split('\0'))
        fingerprints = {}
        for rel in sorted(paths - {''}):
            p = work / rel
            if p.is_file(): fingerprints[rel] = sha(p)
        result[name] = {'head': git('rev-parse', 'HEAD', cwd=work).strip(),
                        'status': git('status', '--porcelain=v1', '-z', cwd=work),
                        'files': fingerprints}
    return result


def products():
    source = ROOT / 'src1.6.7.1-200ms'
    return {p.name: sha(p) for p in source.iterdir() if p.is_file() and
            (p.suffix in ('.cpp', '.hpp', '.h') or p.name in ('CMakeLists.txt', 'words.txt'))}


def candidates():
    targets = []
    # Entire old version directories, including every ignored build-source copy.
    targets += [p for p in ROOT.iterdir() if p.is_dir() and p.name in
                ['src1.7'] + ['src1.7.' + str(i) for i in range(1, 8)]]
    # Preserve summary files and existing evidence archives at their original paths.
    for group in (ROOT / 'validation').iterdir():
        if group.is_dir():
            targets += [p for p in group.iterdir() if p.is_dir() and p.name not in
                        ('evidence', 'semantics', 'pair-evidence', 'postprocess', '中文题卡')]
    for group in (ROOT / 'test-results').iterdir():
        if group.is_dir():
            targets += [p for p in group.iterdir() if p.is_dir() and not
                        (p.name.startswith('analysis') or p.name in ('evidence', 'comparison', 'raw-metadata'))]
    lab = ROOT / 'experiments/full_probability'
    targets += [lab / name for name in ('builds', 'checks', 'runs', 'assets') if (lab / name).exists()]
    # Keep root summary/receipt JSON and the active source/next/drafts trees.
    return sorted(targets, key=str)


def inventory():
    assert not (OUT / 'before.json').exists(), 'Preserve this dated audit; use a new dated output for another cleanup'
    OUT.mkdir(parents=True, exist_ok=True)
    records, sizes, skipped, errors = scan(HOME)
    if errors: raise RuntimeError('Inventory must be complete: ' + repr(errors[:5]))
    tracked = set(git('ls-files', '-z').split('\0')) - {''}
    targets = []
    for p in candidates():
        rel = p.relative_to(ROOT).as_posix()
        targets.append({'path': rel, 'absolute': str(p), 'bytes': sizes.get(str(p), 0),
                        'tracked_files': sum(x == rel or x.startswith(rel + '/') for x in tracked),
                        'archive_index': 'logs/evidence_archives/INDEX.zip',
                        'restore': 'python tools/workspace_archive.py restore --prefix ' + rel,
                        'policy': 'verified archive first; sparse tracked files; delete archived residuals'})
    target_prefixes = [t['absolute'] + os.sep for t in targets]
    selected = {Path(p).relative_to(ROOT).as_posix(): value for p, value in records.items()
                if any(p.startswith(prefix) for prefix in target_prefixes)}
    save(OUT / 'inventory-files.json', selected)
    report = {'head': git('rev-parse', 'HEAD').strip(), 'files': len(records),
              'total_bytes': sizes[str(HOME)], 'main_bytes': sizes[str(ROOT)],
              'top20_directories': sorted(({'path': k, 'bytes': v} for k, v in sizes.items()
                                          if k != str(HOME)), key=lambda x: x['bytes'], reverse=True)[:20],
              'top20_files': heapq.nlargest(20, ({'path': k, 'bytes': v['bytes']} for k, v in records.items()),
                                            key=lambda x: x['bytes']),
              'targets': targets, 'selected_files': len(selected),
              'selected_bytes': sum(x['bytes'] for x in selected.values()), 'skipped_reparse': skipped,
              'errors': errors}
    save(OUT / 'before.json', report)
    save(OUT / 'protected.json', {'products': products(), 'release_zip': sha(ROOT / 'src1.6.7.1-200ms.zip'),
                                'evidence_zip': sha(ROOT / 'src1.6.7.1-200ms/test-results/comprehensive200-20261006/EVIDENCE.zip'),
                                'others': other_states(), 'refs': git('show-ref')})
    print(json.dumps({k: report[k] for k in ('files', 'total_bytes', 'main_bytes', 'selected_files', 'selected_bytes')}), flush=True)


def archive():
    inventory = json.loads((OUT / 'inventory-files.json').read_text(encoding='utf8'))
    ARCHIVES.mkdir(parents=True, exist_ok=True)
    assert not (ARCHIVES / 'INDEX.zip').exists(), 'Archive already exists; verify before reusing'
    blobs = {}; files = {}; parts = []; stream = None; number = 0; total = 0
    # Resume closed, valid parts after an interruption. Original files have not
    # been deleted. Corrupt/incomplete parts are rejected and retained for audit.
    for existing in sorted(ARCHIVES.glob('workspace-*.zip')):
        with zipfile.ZipFile(existing) as previous:
            assert previous.testzip() is None, ('Incomplete part', str(existing))
            for member in previous.namelist():
                key = member.removeprefix('blobs/')
                payload = previous.read(member)
                assert hashlib.sha256(payload).hexdigest() == key
                blobs[key] = {'part': existing.name, 'bytes': len(payload)}
        parts.append(existing.name); number += 1
    def next_part():
        nonlocal stream, number
        if stream: stream.close()
        number += 1
        name = 'workspace-' + str(number).zfill(3) + '.zip'
        parts.append(name)
        stream = zipfile.ZipFile(ARCHIVES / name, 'x', zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True)
    next_part()
    def load(item):
        relative, expected = item
        path = ROOT / relative; s = os.stat(native(path))
        assert s.st_size == expected['bytes'] and s.st_mtime_ns == expected['mtime_ns'], ('Changed before archive', relative)
        digest = hashlib.sha256(); chunks = []; payloads = []; n = 0
        read_size = max(1, min(CHUNK, s.st_size))
        with open(native(path), 'rb') as source:
            for payload in iter(lambda: source.read(read_size), b''):
                digest.update(payload); n += len(payload); key = hashlib.sha256(payload).hexdigest(); chunks.append(key)
                payloads.append((key, payload))
        end = os.stat(native(path))
        assert (s.st_size, s.st_mtime_ns) == (end.st_size, end.st_mtime_ns) and n == expected['bytes'], relative
        return relative, dict(expected, sha256=digest.hexdigest(), chunks=chunks), payloads
    def prefetched():
        # Bounded batches prevent the executor retaining an entire 17GB tree.
        items = iter(inventory.items())
        with ThreadPoolExecutor(max_workers=8) as pool:
            while True:
                batch = []
                for unused in range(16):
                    try: batch.append(next(items))
                    except StopIteration: break
                if not batch: return
                yield from pool.map(load, batch)
    started = time.monotonic()
    for i, (relative, item, payloads) in enumerate(prefetched(), 1):
        for key, payload in payloads:
                if key not in blobs:
                    if stream.fp.tell() > PART: next_part()
                    stream.writestr('blobs/' + key, payload)
                    blobs[key] = {'part': parts[-1], 'bytes': len(payload)}
        files[relative] = item
        total += item['bytes']
        if i % 10000 == 0: print('ARCHIVE', i, '/', len(inventory), 'unique chunks', len(blobs), 'seconds', round(time.monotonic()-started), flush=True)
    stream.close()
    index = {'format': 'workspace-chunked-sha256-v1', 'chunk_bytes': CHUNK, 'files': files, 'blobs': blobs,
             'parts': parts, 'logical_files': len(files), 'raw_bytes': total, 'base_commit': git('rev-parse', 'HEAD').strip()}
    with zipfile.ZipFile(ARCHIVES / 'INDEX.zip', 'x', zipfile.ZIP_DEFLATED) as z:
        z.writestr('MANIFEST.json', json.dumps(index, ensure_ascii=False, separators=(',', ':')))
    verify()


def read_index():
    with zipfile.ZipFile(ARCHIVES / 'INDEX.zip') as z:
        assert z.testzip() is None
        return json.loads(z.read('MANIFEST.json'))


def verify():
    index = read_index(); handles = {}; checked = set(); raw = 0
    try:
        for name in index['parts']:
            z = zipfile.ZipFile(ARCHIVES / name); handles[name] = z
            assert z.testzip() is None, name
        for key, location in index['blobs'].items():
            payload = handles[location['part']].read('blobs/' + key)
            assert len(payload) == location['bytes'] and hashlib.sha256(payload).hexdigest() == key, key
        for relative, item in index['files'].items():
            assert sum(index['blobs'][k]['bytes'] for k in item['chunks']) == item['bytes'], relative
            signature = (item['sha256'], tuple(item['chunks']))
            if signature not in checked:
                h = hashlib.sha256()
                for key in item['chunks']: h.update(handles[index['blobs'][key]['part']].read('blobs/' + key))
                assert h.hexdigest() == item['sha256'], relative
                checked.add(signature)
            raw += item['bytes']
        assert raw == index['raw_bytes'] and len(index['files']) == index['logical_files']
    finally:
        for z in handles.values(): z.close()
    receipt = {'format': index['format'], 'logical_files': index['logical_files'], 'raw_bytes': raw,
               'unique_file_contents': len(checked), 'unique_chunks': len(index['blobs']),
               'crc_all_parts': True, 'sha256_all_chunks_and_files': True,
               'archives': {name: {'bytes': (ARCHIVES / name).stat().st_size, 'sha256': sha(ARCHIVES / name)}
                            for name in ['INDEX.zip'] + index['parts']}}
    save(ARCHIVES / 'receipt.json', receipt)
    print('VERIFY', json.dumps({k: receipt[k] for k in ('logical_files', 'raw_bytes', 'unique_chunks')}), flush=True)
    return receipt


def validate_live():
    index = read_index()
    def check(item):
        relative, expected = item; p = ROOT / relative
        assert os.path.exists(native(p)) and sha(p) == expected['sha256'], ('Changed since archive; retain it', relative)
        return True
    entries = iter(index['files'].items()); count = 0
    with ThreadPoolExecutor(max_workers=8) as pool:
        while True:
            batch = []
            for unused in range(128):
                try: batch.append(next(entries))
                except StopIteration: break
            if not batch: break
            assert all(pool.map(check, batch))
            count += len(batch)
            if count % 20096 == 0: print('LIVE CHECK', count, flush=True)
    save(OUT / 'live-validation.json', {'files': len(index['files']), 'all_sha256_match': True,
                                      'verified_at_unix': time.time(), 'index_sha256': sha(ARCHIVES / 'INDEX.zip')})
    print('All live files match verified archive', flush=True)


def validate_targets():
    index = read_index(); before = json.loads((OUT / 'before.json').read_text(encoding='utf8'))
    live = set()
    for target in before['targets']:
        records, unused, links, errors = scan(ROOT / target['path'])
        assert not links and not errors, (target['path'], links, errors)
        live.update(Path(p).relative_to(ROOT).as_posix() for p in records)
    archived = set(index['files'])
    assert live == archived, {'new_files': sorted(live - archived), 'missing_files': sorted(archived - live)}
    save(OUT / 'target-set-validation.json', {'files': len(live), 'complete_target_set_match': True,
                                             'index_sha256': sha(ARCHIVES / 'INDEX.zip'), 'verified_at_unix': time.time()})
    print('No new/unarchived files in deletion targets', len(live), flush=True)


def restore(prefix, destination=None):
    index = read_index(); prefix = prefix.replace('\\', '/').strip('/')
    assert prefix and '..' not in prefix.split('/') and ':' not in prefix
    destination = Path(destination).resolve() if destination else ROOT
    selected = {p: v for p, v in index['files'].items() if p == prefix or p.startswith(prefix + '/')}
    assert selected, 'Prefix not found in archive'
    # Preflight the entire prefix: never partially overwrite existing content.
    for rel, item in selected.items():
        p = destination / rel
        assert destination == p.resolve() or destination in p.resolve().parents
        if os.path.exists(native(p)): assert sha(p) == item['sha256'], ('Existing file differs', str(p))
    handles = {n: zipfile.ZipFile(ARCHIVES / n) for n in index['parts']}
    try:
        for rel, item in selected.items():
            p = destination / rel
            if os.path.exists(native(p)): continue
            os.makedirs(native(p.parent), exist_ok=True)
            with open(native(p), 'xb') as out:
                for key in item['chunks']: out.write(handles[index['blobs'][key]['part']].read('blobs/' + key))
            assert sha(p) == item['sha256']
            os.chmod(native(p), item['mode']); os.utime(native(p), ns=(item['mtime_ns'], item['mtime_ns']))
    finally:
        for z in handles.values(): z.close()
    print('RESTORED', len(selected), 'files to', destination, flush=True)


def after():
    protected = json.loads((OUT / 'protected.json').read_text(encoding='utf8'))
    assert products() == protected['products'], 'Competition product bytes changed'
    assert sha(ROOT / 'src1.6.7.1-200ms.zip') == protected['release_zip']
    assert sha(ROOT / 'src1.6.7.1-200ms/test-results/comprehensive200-20261006/EVIDENCE.zip') == protected['evidence_zip']
    assert other_states() == protected['others'], 'Other worktree state changed'
    files, sizes, skipped, errors = scan(HOME)
    assert not errors, errors
    before = json.loads((OUT / 'before.json').read_text(encoding='utf8'))
    result = {'files': len(files), 'total_bytes': sizes[str(HOME)], 'main_bytes': sizes[str(ROOT)],
              'released_logical_bytes': before['total_bytes'] - sizes[str(HOME)],
              'competition_hashes_unchanged': True, 'other_worktrees_unchanged': True,
              'skipped_reparse': skipped, 'errors': errors}
    save(OUT / 'after.json', result)
    print(json.dumps(result, ensure_ascii=True), flush=True)


if __name__ == '__main__':
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument('action', choices=['inventory', 'archive', 'verify', 'validate-live', 'validate-targets', 'restore', 'after'])
    p.add_argument('--prefix'); p.add_argument('--destination')
    a = p.parse_args()
    if a.action == 'restore': restore(a.prefix, a.destination)
    elif a.action == 'validate-live': validate_live()
    elif a.action == 'validate-targets': validate_targets()
    else: globals()[a.action]()
