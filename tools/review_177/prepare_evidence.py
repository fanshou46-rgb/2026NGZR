"""Create version-specific packaging and Git-byte audit tools; not a runner."""
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
DEST=ROOT/'tools/review_177'

def main():
    source=(ROOT/'tools/review_176/collect_and_package.py').read_text(encoding='utf8')
    source=source.replace('review176','review177').replace('rdfw176','rdfw177')
    source=source.replace("RUN=OUT/'raw/frozen-v2'", "RUN=OUT/'raw/frozen-v1'")
    source=source.replace("['runs']==416", "['runs']==304")
    source=source.replace("'rdfw177-tests-5.log',304", "'rdfw177-tests-8.log',320")
    source=source.replace("'rdfw177-sanitizer.log',275", "'rdfw177-sanitizer-final.log',291")
    source=source.replace("first_run_passed=kind=='sanitizer'", "final_frozen_sources=True,draft_sanitizer_not_final_evidence=True")
    source=source.replace("ROOT/'src1.7.6'", "ROOT/'src1.7.7'")
    source=source.replace("for v in ('src1.7.5','src1.7.6')", "for v in ('src1.7.6','src1.7.7')")
    source=source.replace("validation/review175-20261004/frozen-v2/build-current", "validation/review176-20261004/raw/frozen-v2/build-current")
    source=source.replace("    failed += [p for p in (OUT/'raw/frozen-v1').rglob('*') if p.is_file()]\n", '')
    source=source.replace("    failed += [p for p in (OUT/'raw/counterexamples').rglob('*') if p.is_file()]\n", '')
    source=source.replace("    save(dest/'manifest.json',manifest)", "    draft=[p for p in (OUT/'raw/preflight-v1').rglob('*') if p.is_file()]\n    draft += [p for p in (OUT/'raw/preflight-v1-questions').rglob('*') if p.is_file()]\n    bundle('preflight-v1-failure.zip',draft)\n    save(dest/'manifest.json',manifest)")
    source=source.replace('ROOT=Path(__file__).resolve().parents[2]', "TEMP=Path('/tmp') if __import__('os').name!='nt' else Path('//wsl.localhost/Ubuntu-18.04/tmp')\nROOT=Path(__file__).resolve().parents[2]")
    source=source.replace("Path('/tmp').glob", 'TEMP.glob').replace("source=Path('/tmp')/build", 'source=TEMP/build')
    source=source.replace("shutil.copytree('/tmp/rdfw177-tests/official-semantics'", "shutil.copytree(str(TEMP/'rdfw177-tests/official-semantics')")
    source=source.replace("    audit=json.loads((RUN/'frozen-audit.json').read_text(encoding='utf8'))", "    frozen=json.loads((checks/'pre-final-check-source-hashes.json').read_text(encoding='utf8'))\n    assert all(sha(ROOT/'src1.7.7'/name)==h for name,h in frozen.items())\n    audit=json.loads((RUN/'frozen-audit.json').read_text(encoding='utf8'))")
    (DEST/'collect_and_package.py').write_text(source,encoding='utf8')
    source=(ROOT/'tools/review_176/verify_publication.py').read_text(encoding='utf8')
    source=source.replace('review176','review177').replace('src1.7.6','src1.7.7')
    (DEST/'verify_publication.py').write_text(source,encoding='utf8')

if __name__=='__main__': main()
