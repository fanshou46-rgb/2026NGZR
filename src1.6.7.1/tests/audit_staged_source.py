#!/usr/bin/env python3
"""Check staged product bytes against frozen benchmark inputs, including EOLs."""
import hashlib
import json
from pathlib import Path
import subprocess


def main():
    root = Path(__file__).resolve().parents[2]
    output = root / 'src1.6.7.1/test-results/comprehensive200-20261005'
    audit = json.loads((output / 'input-audit.json').read_text(encoding='utf8'))
    entries = []
    for arm, folder in [('baseline', 'HistoryVersion/src1.6.7'), ('current', 'src1.6.7.1')]:
        for name, expected in audit['products'][arm].items():
            path = folder + '/' + name
            raw = (root / path).read_bytes()
            blob = subprocess.check_output(['git', 'show', ':' + path], cwd=str(root))
            assert hashlib.sha256(raw).hexdigest() == expected, path
            identical = raw == blob
            eol_only = raw.replace(b'\r\n', b'\n') == blob.replace(b'\r\n', b'\n')
            assert identical or eol_only, path
            entries.append(dict(arm=arm, path=path, frozen_raw_sha256=expected,
                                git_blob_sha256=hashlib.sha256(blob).hexdigest(),
                                bytes_identical=identical, only_crlf_difference=not identical and eol_only))
    value = dict(product_files=len(entries), semantic_differences=0,
                 eol_only_files=sum(e['only_crlf_difference'] for e in entries), files=entries)
    (output / 'git-byte-audit.json').write_text(json.dumps(value, indent=2) + '\n')
    print('STAGED_SOURCE_AUDIT', value['product_files'], 'files;', value['eol_only_files'], 'EOL-only differences')


if __name__ == '__main__':
    main()
