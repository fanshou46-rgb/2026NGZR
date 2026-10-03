#!/usr/bin/env python3
"""Build this version and run the complete official release matrix serially."""
import argparse
import os
from pathlib import Path
import subprocess
import sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument('--output', type=Path, required=True)
    p.add_argument('--baseline', type=Path, required=True)
    p.add_argument('--seed-library', type=Path, required=True)
    a = p.parse_args()
    root = Path(__file__).resolve().parents[2]
    tests = Path(__file__).resolve().parent
    sys.path.insert(0, str(root / 'HistoryVersion/src1.1.2 (x)/tools'))
    from compare_legal import build
    a.output.mkdir(parents=True, exist_ok=False)
    executable = build('src1.6.5', Path('/home/yifan/env-release-2026'),
                       a.output / 'build-release')
    for matrix, name, repeat in [('full','full-release',1),
                                ('target','target-release-r1',1),
                                ('target','target-release-r2',2),
                                ('target','target-release-r3',3),
                                ('off','off-release',1),
                                ('target','perf-target',1)]:
        env = dict(os.environ)
        env['RDFW_STAGE_TIMING'] = '1' if name == 'perf-target' else '0'
        command = [sys.executable, str(tests / 'run_state_matrix.py'), matrix,
                   '--repeat', str(repeat), '--baseline', str(a.baseline),
                   '--current', str(executable), '--output', str(a.output / name),
                   '--seed-library', str(a.seed_library)]
        with (a.output / (name + '.log')).open('w') as log:
            subprocess.run(command, env=env, stdout=log, stderr=subprocess.STDOUT, check=True)
        script = 'summarize_state_performance.py' if name == 'perf-target' else 'summarize_state_matrix.py'
        subprocess.run([sys.executable, str(tests / script), str(a.output / name)], check=True)


if __name__ == '__main__':
    main()
