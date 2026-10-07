#!/usr/bin/env python3
"""Create portable review and complete evidence ZIPs without expanding the worktree."""
import argparse
import hashlib
import json
import os
import posixpath
import re
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PREFIX = 'robocup-development-evidence/'
TEXT = {'.md', '.json', '.jsonl', '.csv', '.txt', '.log', '.xml', '.lp', '.yaml', '.yml', '.diff', '.patch', '.pdf'}
SOURCE = {'.cpp', '.hpp', '.h', '.c', '.py', '.ps1', '.sh', '.cmake'}
VERSIONS = ['HistoryVersion/src1.6.7', 'src1.6.7-200ms', 'src1.6.7.1', 'src1.6.7.1-200ms'] + ['src1.7'] + ['src1.7.' + str(i) for i in range(1, 8)]
PRIMARY = ['docs/development_1.7plus.md', 'docs/failure_cases.md']


def git(*args):
    return subprocess.check_output(['git', '-C', str(ROOT), *args])


def digest(data):
    return hashlib.sha256(data).hexdigest()


def selected(rel):
    # This is the sender's local delivery receipt, written after packaging.
    # Readers use the package README and manifest rather than stale D: links.
    if rel == 'docs/development_share.md':
        return False
    parts = rel.split('/')
    if any(p in ('__pycache__', '.git', '.venv', 'build', 'builds', 'runs', 'runtime') or p.startswith('build-') for p in parts[:-1]):
        return False
    suffix = Path(rel).suffix.lower()
    if rel.startswith('tools/'):
        return suffix in SOURCE | TEXT and 'apply_workspace_cleanup' not in rel
    if any(rel.startswith(version + '/') for version in VERSIONS):
        return suffix in SOURCE | TEXT or Path(rel).name == 'CMakeLists.txt'
    if rel.startswith(('docs/', 'validation/', 'experiments/full_probability/', 'logs/representative_failures/', 'logs/competition_smoke_20261007/')):
        return suffix in SOURCE | TEXT
    if rel.startswith('logs/workspace_cleanup_20261007/'):
        return suffix in TEXT and Path(rel).name not in ('protected.json', 'inventory-files.json')
    if rel.startswith('题目/'):
        return suffix in TEXT | SOURCE
    if rel.startswith('HistoryVersion/src1.1.2 (x)/tools/'):
        return suffix in SOURCE | TEXT
    return False


def main(output):
    output.mkdir(parents=True, exist_ok=True)
    head = git('rev-parse', 'HEAD').decode().strip()
    entries = {}
    for directory in ['docs', 'validation', 'experiments/full_probability', 'tools', 'logs/representative_failures',
                      'logs/workspace_cleanup_20261007', 'logs/competition_smoke_20261007', '题目',
                      'HistoryVersion/src1.1.2 (x)/tools'] + VERSIONS:
        base = ROOT / directory
        if not base.exists():
            continue
        for current, dirs, files in os.walk(base, followlinks=False):
            dirs[:] = [d for d in dirs if d != '__pycache__' and not (Path(current) / d).is_symlink()]
            for name in files:
                p = Path(current) / name
                rel = p.relative_to(ROOT).as_posix()
                if selected(rel):
                    entries[rel] = ('disk', p)
    tracked = git('ls-tree', '-rz', '--full-tree', head, '--', *VERSIONS).split(b'\0')
    for record in tracked:
        if not record:
            continue
        meta, raw_name = record.split(b'\t', 1)
        rel = raw_name.decode('utf8')
        if selected(rel) and rel not in entries:
            entries[rel] = ('git', meta.split()[2].decode())
    archive_root = ROOT / 'logs/evidence_archives'
    with zipfile.ZipFile(archive_root / 'INDEX.zip') as z:
        index = json.loads(z.read('MANIFEST.json'))
    handles = {}

    def archived(rel):
        item = index['files'][rel]
        blocks = []
        for key in item['chunks']:
            part = index['blobs'][key]['part']
            if part not in handles:
                handles[part] = zipfile.ZipFile(archive_root / part)
            blocks.append(handles[part].read('blobs/' + key))
        data = b''.join(blocks)
        assert digest(data) == item['sha256'], rel
        return data

    for rel in list(entries):
        if entries[rel][0] == 'git' and rel in index['files']:
            entries[rel] = ('archive', rel)
    failure_index = json.loads((ROOT / 'logs/representative_failures/INDEX.json').read_text(encoding='utf8'))
    for sample in failure_index['samples']:
        for item in sample['files']:
            assert item['saved'] in entries, ('Missing representative evidence', item['saved'])
    generated = {}
    commit_ids = ['ecafa0bc', '91517cd6', '59c51b58', '86e9c074', '9c600988', '60457237',
                  '8acf6718', '21f1a9bf', '567619fe', '68fe263b', 'b54ac972', '19c994f5', '4336a368']
    commits = []
    paths = VERSIONS + ['experiments/full_probability/source', 'experiments/full_probability/next', 'tools/full_probability']
    for short in commit_ids:
        full = git('rev-parse', short).decode().strip()
        commits.append({'short': short, 'commit': full, 'subject': git('show', '-s', '--format=%s', full).decode().strip(),
                        'diff': 'git_diffs/' + short + '.patch'})
        generated['git_diffs/' + short + '.patch'] = git('show', '--format=fuller', '--binary', '--find-renames', full, '--', *paths, ':!**/test-results/**')
    generated['git_diffs/COMMITS.json'] = (json.dumps(commits, ensure_ascii=False, indent=2) + '\n').encode()
    generated['git_diffs/README.md'] = ('# 历史提交\n\nCOMMITS.json记录完整提交ID和标题；patch保留相关产品、测试和实验实现的改动。'
        '大型日志不重复放进diff，完整证据位于完整包的原始ZIP及分块归档。源码目录使用打包时工作区/Git快照；'
        '已删除目录优先读取原字节归档。patch用于阅读实现变化，应用到其他版本前应核对其父提交。\n').encode()
    generated['README.md'] = f'''# RoboCup开发历史与失败证据：转发版

快照提交：`{head}`。解压整个ZIP后，先打开本文件。

## 从这里开始

- [1.7至1.7.7与概率实验开发历史](docs/development_1.7plus.md)
- [七组典型失败及原始记录索引](docs/failure_cases.md)
- [所有典型失败的机器索引](logs/representative_failures/INDEX.json)
- [逐版源码与commit/diff](git_diffs/README.md)
- [比赛版配置、依赖和验证边界](docs/competition_version.md)

阅读包包含版本源码/测试/原发布说明、直接对照报告、逐题统计、题库、原始典型日志、评分、SDK终态、审计与复算脚本。
完整包包含阅读包全部内容，另加78个原开发证据ZIP、报告引用的旧版证据ZIP、两份比赛完整证据、29个补充分块ZIP和现有发布ZIP。
`SOURCE_MANIFEST.json`逐项记录实际来源、字节数、SHA256。原始日志与评分不改写；其中本机绝对路径用于历史溯源，
阅读使用本包相对路径。四组未提交概率草稿以原目录保存，是未完成的研发材料，不能当作验证通过的功能。

## 无需Git即可查看和恢复

源码和diff已直接附上。阅读报告、逐题统计、典型失败不需要Git或官方SDK。
接收者不必打开发送者的电脑路径，也不必重新获取发送者的工作区。

完整包解压后，在本目录使用Python3.9+：

```powershell
python tools/verify_share.py
python tools/workspace_archive.py restore --prefix validation/review177-100-20261004/runs/new-A01-02-s1-it-r1-177 --destination recovered
python tools/workspace_archive.py restore --prefix experiments/full_probability/runs --destination recovered
```

恢复工具写入包内 `recovered` 子目录，不覆盖不同内容。完整原始数据可按索引中的任意前缀恢复。
补充归档含174735个逻辑文件，全部展开约16.42GiB；按所需前缀恢复即可。
阅读包不带大型ZIP；需要恢复完整矩阵或审查全部日志时使用完整包。

## 分数复算与运行

`tools/review177_100/analyze.py`、`tools/full_probability/audit_repeats.py`等是原复算/审计工具；
工具使用的汇总和逐题JSON/CSV/JSONL已附上。读取完整原始轨迹的工具需先从完整包恢复相应runs目录。
重新运行机器人并重新生成正式分数需要接收者自己的官方SDK和Boost/C++环境；这两份包未附第三方SDK安装目录。
原运行命令中机器专属路径应按接收者环境调整。`tools/competition_smoke.py`支持用 `--sdk` 指定SDK路径。
普通验证与四项SDK冒烟通过；连续sanitizer检查仍未完成。

## 完整性

ZIP已核对CRC及每个成员的SHA256，并检查90个典型失败文件的来源哈希。
ZIP旁的SHA256文件用于核对转发后整个ZIP是否改变；解压后运行 `python tools/verify_share.py` 核对成员。
`LINK_AUDIT.json`列出报告中的本包相对链接、在归档中可恢复的路径以及历史外部路径。
原文中的Git恢复命令属于原工作区记录；接收者使用本README中的解压/恢复方法。
'''.encode()
    generated['tools/verify_share.py'] = b'''import hashlib,json
from pathlib import Path
root=Path(__file__).resolve().parents[1]
m=json.loads((root/'SOURCE_MANIFEST.json').read_text(encoding='utf8'))
for e in m['files']:
 p=root/e['path']; h=hashlib.sha256()
 with p.open('rb') as f:
  for b in iter(lambda:f.read(1024*1024),b''):h.update(b)
 assert p.stat().st_size==e['bytes'] and h.hexdigest()==e['sha256'],e['path']
print('PASS:',len(m['files']),'files; all SHA256 match')
'''

    def read_entry(rel):
        kind, value = entries[rel]
        if kind == 'disk':
            return value.read_bytes()
        if kind == 'archive':
            return archived(value)
        return git('cat-file', 'blob', value)

    # Make release-report paths directly clickable in the portable copies.
    for rel in PRIMARY:
        data = read_entry(rel)
        text = data.decode('utf8')
        text = re.sub(r'`(src1\.7(?:\.[1-7])?/docs/[^`]+\.md)`',
                      lambda m: '[' + m[1] + '](../' + m[1].replace(' ', '%20') + ')', text)
        generated[rel] = text.encode('utf8')
        entries.pop(rel)

    existing = json.loads((ROOT / 'logs/workspace_cleanup_20261007/existing-development-evidence-audit.json').read_text())
    competition = json.loads((ROOT / 'logs/workspace_cleanup_20261007/existing-competition-evidence-audit.json').read_text())
    extra = {row['path']: ('disk', ROOT / row['path']) if (ROOT / row['path']).exists() else ('archive', row['path']) for row in existing + competition}
    extra['src1.6.7.1-200ms.zip'] = ('disk', ROOT / 'src1.6.7.1-200ms.zip')
    for p in archive_root.iterdir():
        if p.suffix == '.zip' or p.name == 'receipt.json':
            extra[p.relative_to(ROOT).as_posix()] = ('disk', p)

    # Follow the linked reports themselves, so their attachments also travel.
    # Keep original source/log bytes; repair the historical rename only in its
    # portable report copy and state exactly what was changed.
    renamed_report = 'src1.7.3/test-results/validation-20261004/REPORT.md'
    report_text = read_entry(renamed_report).decode('utf8')
    if 'ROBOT_FLOW_1.9.md' in report_text:
        generated[renamed_report] = (report_text.replace('ROBOT_FLOW_1.9.md', 'ROBOT_FLOW_1.7.3.md') +
            '\n转发版链接修正：原ROBOT_FLOW_1.9.md已在仓库重命名为ROBOT_FLOW_1.7.3.md；仅修正链接，原评分和记录不变。\n').encode('utf8')
        entries.pop(renamed_report)
    report_queue = PRIMARY + ['docs/competition_version.md', 'docs/workspace_cleanup.md', 'docs/AUDIT_1.7.2_1.7.4.md']
    linked_reports = set()
    while report_queue:
        rel = report_queue.pop()
        if rel in linked_reports:
            continue
        linked_reports.add(rel)
        data = generated.get(rel) or read_entry(rel)
        for value in re.findall(r'\]\(([^)]+)\)', data.decode('utf8')):
            if re.match(r'\w+://', value) or value.startswith('#'):
                continue
            target = posixpath.normpath(posixpath.join(posixpath.dirname(rel), value.split('#', 1)[0].replace('%20', ' ')))
            assert not target.startswith('../') and not target.startswith('/'), ('Outside package', target)
            available = set(entries) | set(generated) | set(extra)
            if target not in available and not any(p.startswith(target + '/') for p in available):
                if (ROOT / target).is_file():
                    entries[target] = ('disk', ROOT / target)
                elif target in index['files']:
                    (extra if target.endswith('.zip') else entries)[target] = ('archive', target)
                else:
                    raise AssertionError(('Historical report attachment missing', rel, target))
            if target.endswith('.md'):
                report_queue.append(target)

    def links(available):
        rows = []
        for rel in sorted(linked_reports):
            data = generated.get(rel) or read_entry(rel)
            for value in re.findall(r'\]\(([^)]+)\)', data.decode('utf8')):
                if re.match(r'\w+://', value) or value.startswith('#'):
                    continue
                value = value.split('#', 1)[0].replace('%20', ' ')
                target = posixpath.normpath(posixpath.join(posixpath.dirname(rel), value))
                status = 'included' if target in available else 'included_directory' if any(p.startswith(target + '/') for p in available) else 'complete_package_only' if target in extra else 'restore_from_chunk_archive' if target in index['files'] else 'unresolved'
                rows.append({'document': rel, 'target': target, 'status': status})
        assert not [r for r in rows if r['status'] == 'unresolved'], rows
        return rows

    results = []
    for complete in (False, True):
        name = 'robocup-development-failures-' + ('complete' if complete else 'review') + '-20261007.zip'
        target = output / name
        assert not target.exists(), target
        current = dict(entries)
        if complete:
            current.update(extra)
        manifest = {'snapshot_commit': head, 'package': 'complete' if complete else 'review', 'files': []}
        additions = dict(generated)
        additions['LINK_AUDIT.json'] = (json.dumps(links(set(current) | set(additions)), ensure_ascii=False, indent=2) + '\n').encode()
        with zipfile.ZipFile(target, 'x', compression=zipfile.ZIP_DEFLATED, compresslevel=6, allowZip64=True) as z:
            for number, rel in enumerate(sorted(set(current) | set(additions)), 1):
                if rel in additions:
                    data = additions[rel]; source = 'portable_document' if rel in PRIMARY else 'generated'
                else:
                    kind, value = current[rel]
                    source = kind
                    data = value.read_bytes() if kind == 'disk' else archived(value) if kind == 'archive' else git('cat-file', 'blob', value)
                    assert not data.startswith(b'version https://git-lfs.github.com/spec/v1\n'), ('Unresolved LFS pointer', rel)
                z.writestr(PREFIX + rel, data, compress_type=zipfile.ZIP_STORED if rel.endswith('.zip') else zipfile.ZIP_DEFLATED)
                manifest['files'].append({'path': rel, 'bytes': len(data), 'sha256': digest(data), 'source': source})
                if number % 300 == 0:
                    print(name, 'WROTE', number, flush=True)
            z.writestr(PREFIX + 'SOURCE_MANIFEST.json', json.dumps(manifest, ensure_ascii=False, indent=2).encode())
        print(name, 'VERIFY', flush=True)
        with zipfile.ZipFile(target) as z:
            assert z.testzip() is None
            assert len(z.namelist()) == len(manifest['files']) + 1
            for row in manifest['files']:
                h = hashlib.sha256(); length = 0
                with z.open(PREFIX + row['path']) as f:
                    for block in iter(lambda: f.read(1024 * 1024), b''):
                        h.update(block); length += len(block)
                assert h.hexdigest() == row['sha256'] and length == row['bytes'], row['path']
            lookup = {row['path']: row['sha256'] for row in manifest['files']}
            failures = json.loads(z.read(PREFIX + 'logs/representative_failures/INDEX.json'))
            samples = failures if isinstance(failures, list) else failures['samples']
            count = 0
            for sample in samples:
                for row in sample['files']:
                    assert lookup[row['saved']] == row['sha256'], row['saved']
                    count += 1
        h = hashlib.sha256()
        with target.open('rb') as f:
            for block in iter(lambda: f.read(1024 * 1024), b''):
                h.update(block)
        checksum = h.hexdigest()
        target.with_suffix('.zip.sha256').write_text(checksum + '  ' + name + '\n', encoding='ascii')
        result = {'path': str(target), 'bytes': target.stat().st_size, 'sha256': checksum, 'files': len(manifest['files']),
                  'crc_pass': True, 'all_member_sha256_pass': True, 'failure_provenance_files': count,
                  'primary_link_audit_pass': True, 'source_snapshot': head}
        results.append(result)
        print(json.dumps(result), flush=True)
    for z in handles.values():
        z.close()
    (output / 'PACKAGE_RECEIPT.json').write_text(json.dumps(results, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    return results


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    main(args.output.resolve())
