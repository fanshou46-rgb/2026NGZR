#!/usr/bin/env python3
"""Run integration-of-model tests and a compile-negative domain check under Linux."""
import argparse
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser()
parser.add_argument('--sdk', type=Path, required=True)
parser.add_argument('--output', type=Path, required=True)
args = parser.parse_args()
root = Path(__file__).resolve().parents[1]
args.output = args.output.resolve()
args.output.mkdir(parents=True, exist_ok=False)
command = ['g++', '-std=c++11', '-O1', '-g', '-D_GLIBCXX_ASSERTIONS',
           '-I' + str(root), '-I' + str(args.sdk / 'include'), '-I' + str(args.sdk / 'src'),
           str(root / 'tests/core_tests.cpp'), str(root / 'rdfw.cpp'), str(root / 'parser.cpp'),
           '-L' + str(args.sdk / 'lib'), '-lframe', '-lutility', '-lboost_thread',
           '-lboost_system', '-lboost_chrono', '-lboost_date_time', '-lboost_regex',
           '-lpthread', '-ldl', '-o', str(args.output / 'core_tests')]
with (args.output / 'build.log').open('w') as log:
    subprocess.run(command, stdout=log, stderr=subprocess.STDOUT, check=True)
with (args.output / 'core-tests.log').open('w') as log:
    subprocess.run([str(args.output / 'core_tests'), str(root / 'words.txt')],
                   stdout=log, stderr=subprocess.STDOUT, check=True)
bad = args.output / 'wrong_domain.cpp'
bad.write_text('#include "indexed_vector.hpp"\nint main() { _home::ObjectVector<int> table(2,0); '
               'return table[_home::LocationId(1)]; }\n', encoding='utf-8')
with (args.output / 'compile-negative.log').open('w') as log:
    result = subprocess.run(['g++', '-std=c++11', '-I' + str(root), '-fsyntax-only', str(bad)],
                            stdout=log, stderr=subprocess.STDOUT)
assert result.returncode != 0, 'wrong-domain access unexpectedly compiled'
subprocess.run(['python3', '-m', 'unittest', 'discover', '-s', str(root / 'tests'), '-p', 'test_*.py', '-v'], check=True)
print('All core, domain, budget and baseline parser checks passed')
