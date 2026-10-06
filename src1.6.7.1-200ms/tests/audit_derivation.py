#!/usr/bin/env python3
"""Verify the 200 ms candidate is exactly H1 applied to the 200 ms source."""
import hashlib
import json
import difflib
from pathlib import Path


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def product(root):
    return {p.name: sha(p) for p in root.iterdir()
            if p.is_file() and (p.suffix in ('.cpp', '.hpp', '.h')
                                or p.name in ('words.txt', 'CMakeLists.txt'))}


def main():
    root = Path(__file__).resolve().parents[2]
    original_300 = root / 'HistoryVersion/src1.6.7'
    original_200 = root / 'src1.6.7-200ms'
    h1_300 = root / 'src1.6.7.1'
    h1_200 = root / 'src1.6.7.1-200ms'
    names = set(product(original_200))
    assert names == set(product(original_300)) == set(product(h1_300)) == set(product(h1_200))
    changed = sorted(name for name in names if sha(original_200 / name) != sha(h1_200 / name))
    assert changed == ['CMakeLists.txt', 'rdfw.cpp', 'rdfw.hpp'], changed
    assert sorted(name for name in names if sha(original_300 / name) != sha(original_200 / name)) == ['rdfw.hpp']
    assert (original_200 / 'rdfw.hpp').read_bytes() == (
        original_300 / 'rdfw.hpp').read_bytes().replace(b'plan_safety_margin{300}', b'plan_safety_margin{200}')
    for name in names - set(changed):
        assert (original_200 / name).read_bytes() == (h1_200 / name).read_bytes(), name
    assert (h1_200 / 'CMakeLists.txt').read_bytes() == (h1_300 / 'CMakeLists.txt').read_bytes()
    assert (h1_200 / 'rdfw.hpp').read_bytes() == (
        h1_300 / 'rdfw.hpp').read_bytes().replace(b'plan_safety_margin{300}', b'plan_safety_margin{200}')
    assert (h1_200 / 'rdfw.cpp').read_bytes() == (
        h1_300 / 'rdfw.cpp').read_bytes().replace(
            b'1.6.7.1 lifecycle-hardening baseline=1.6.7 margin=300ms',
            b'1.6.7.1-200ms lifecycle-hardening baseline=1.6.7-200ms margin=200ms')
    result = dict(base='src1.6.7-200ms', candidate='src1.6.7.1-200ms',
                  changed_files=changed, base_sha256=product(original_200),
                  candidate_sha256=product(h1_200), planner_margin_ms=200,
                  h1_equivalence='same 300ms H1 changes except margin and version log')
    destination = h1_200 / 'docs'
    destination.mkdir(exist_ok=True)
    (destination / 'DERIVATION.json').write_text(
        json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf8')
    patches = []
    for name in changed:
        before = (original_200 / name).read_text(encoding='utf8').splitlines(keepends=True)
        after = (h1_200 / name).read_text(encoding='utf8').splitlines(keepends=True)
        patches.extend(difflib.unified_diff(
            before, after, fromfile='src1.6.7-200ms/' + name,
            tofile='src1.6.7.1-200ms/' + name))
    (destination / 'source.diff').write_text(''.join(patches), encoding='utf8')
    print('DERIVATION_OK', len(names), 'product files;', ', '.join(changed))


if __name__ == '__main__':
    main()
