"""Same-binary controls for the wall-clock-sensitive 06 IT tail, serial only."""
import argparse
import hashlib
import json
import os
import sys
from pathlib import Path
sys.dont_write_bytecode = True
from run_guarded_compare import main as compare_main

parser = argparse.ArgumentParser()
parser.add_argument('--runs', type=Path, required=True)
parser.add_argument('--baseline', type=Path, required=True)
parser.add_argument('--seed-library', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[2]
case = root / '题目/realcompetiton_2024/06.xml'
os.environ['RDFW_STAGE_TIMING'] = '0'
controls = []
for round_id in range(1, 4):
    output = args.runs / ('deadline-self-r' + str(round_id))
    sys.argv = ['run_guarded_compare.py', '--sdk', '/home/yifan/env-release-2026',
                '--runner', str(root / 'HistoryVersion/src1.1.2 (x)/tools/baseline.py'),
                '--baseline', str(args.baseline), '--current', str(args.baseline),
                '--words', str(root / 'src1.6.6/words.txt'), '--output', str(output),
                '--seed-library', str(args.seed_library), '--seed', '20260924',
                '--baseline-mode', 'guarded', '--current-mode', 'guarded',
                '2:' + str(case), '--modes', 'it']
    assert compare_main() == 0
    controls.extend(json.loads((output / 'results.json').read_text()))
observations = []
for suite in ['full-release', 'target-release-r1', 'target-release-r2',
              'target-release-r3', 'perf-target']:
    for row in json.loads((args.runs / suite / 'results.json').read_text()):
        if Path(row['case']) == case and row['mode'] == 'it':
            observations.append(dict(suite=suite, **row))
summary = dict(baseline_binary_sha256=hashlib.sha256(args.baseline.read_bytes()).hexdigest(),
               case_sha256=hashlib.sha256(case.read_bytes()).hexdigest(),
               controls=controls, release_observations=observations,
               note='Wall-clock deadline/complete-plan gating is unchanged; controls use one identical binary for both labels. Retain the original differing pair.')
(args.runs / 'deadline-variation.json').write_text(json.dumps(summary, ensure_ascii=False, indent=2), encoding='utf-8')
print('Baseline scores:', [side['base'] for row in controls for side in (row['baseline'], row['current'])])
