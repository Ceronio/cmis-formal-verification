"""Reproduce frozen CP10 A/B mathematical suites, not a universal proof.
No network, repository writes or installation is performed by this runner.
Usage: python -I -B audits/cp10/run_original_suites.py --output RECEIPT_DIRECTORY
"""
from pathlib import Path, PurePosixPath
import argparse, hashlib, importlib.metadata, json, os, platform, shutil, subprocess, sys, tempfile, time
BASE=Path(__file__).resolve().parent
REPO=BASE.parents[1]
def digest(p): return hashlib.sha256(p.read_bytes()).hexdigest()
def verify_inputs():
    manifest=json.loads((BASE/'PAYLOAD_SHA256.json').read_text())
    if not isinstance(manifest,dict) or not manifest:raise ValueError('Empty payload manifest')
    for name,expected in manifest.items():
        p=PurePosixPath(name)
        if p.is_absolute() or '..' in p.parts:raise ValueError('Unsafe manifest path')
        target=REPO/name
        if target.is_symlink() or not target.is_file() or digest(target)!=expected:raise ValueError('Payload hash mismatch: '+name)
    mapping=json.loads((BASE/'SOURCE_PARITY.json').read_text())['files']
    if len(mapping)!=17 or len({x['payload_path'] for x in mapping})!=17:raise ValueError('Source map changed')
    for item in mapping:
        if digest(REPO/item['payload_path'])!=item['sha256']:raise ValueError('Original-source binding mismatch')
    return len(manifest),len(mapping)
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--output',type=Path,required=True);args=ap.parse_args()
    out=args.output.resolve();out.mkdir(parents=True,exist_ok=True)
    report={'status':'HOLD','scope':'ORIGINAL_CP10_MATHEMATICAL_SUITES_ONLY','universal_theorem_proved':False,'archive_release_checks_executed':False,'github_execution':os.environ.get('GITHUB_ACTIONS')=='true','python':sys.version,'platform':platform.platform(),'environment':{k:os.environ.get(k) for k in ['GITHUB_RUN_ID','GITHUB_RUN_ATTEMPT','GITHUB_SHA','GITHUB_REF','GITHUB_JOB']},'results':[]}
    try:
        report['payload_files'],report['original_source_files']=verify_inputs()
        report['dependencies']={name:importlib.metadata.version(name) for name in ['sympy','mpmath']}
        if report['dependencies']!={'sympy':'1.14.0','mpmath':'1.3.0'}:raise ValueError('Dependency versions differ from pinned recovery environment')
        jobs=[('A','run_primary.py','TWO_ADIC_PRIMARY.json',True,595),('A','run_negative.py','NEGATIVE_CASES.json',True,46),('A','run_comparison.py','COMPARISON.json',False,392),('B','run_primary.py','PRIMARY_REPLAY.json',True,247),('B','run_comparison.py','SYMBOLIC_COMPARISON.json',False,66)]
        with tempfile.TemporaryDirectory(prefix='cmis-cp10-original-') as tmp:
            for v in ['A','B']:
                target=Path(tmp)/v;shutil.copytree(BASE/f'original_{v}',target);(target/'results').mkdir(exist_ok=True)
            for v,script,result,stdlib,count in jobs:
                target=Path(tmp)/v;expected=json.loads((BASE/f'original_{v}/expected'/result).read_text())
                wrapper='import sys,runpy;sys.path.insert(0,sys.argv[1]);runpy.run_path(sys.argv[2],run_name="__main__")'
                cmd=[sys.executable,'-I','-B']+(['-S'] if stdlib else [])+['-c',wrapper,str(target/'code'),str(target/'code'/script)]
                begin=time.monotonic();p=subprocess.run(cmd,cwd=target,capture_output=True,text=True,timeout=120)
                actual=json.loads((target/'results'/result).read_text())
                valid=(p.returncode==0 and actual.get('status')=='PASS' and actual.get('check_count')==count and actual.get('checks')==expected.get('checks') and all(type(c.get('pass')) is bool and c['pass'] for c in actual['checks']))
                rec={'variant':v,'script':script,'status':'PASS' if valid else 'HOLD','records':count,'exit_code':p.returncode,'elapsed_seconds':time.monotonic()-begin,'command':cmd,'checks_equal_to_historical':actual.get('checks')==expected.get('checks')}
                report['results'].append(rec)
                (out/f'{v}_{result}').write_text(json.dumps(actual,indent=2));(out/f'{v}_{script}.stdout.txt').write_text(p.stdout);(out/f'{v}_{script}.stderr.txt').write_text(p.stderr)
                if not valid:raise ValueError(f'Original suite mismatch: {v}/{script}')
        report['variant_totals']={'A':1033,'B':313};report['status']='PASS_ORIGINAL_MATHEMATICAL_SUITES'
    except Exception as e: report['error']=type(e).__name__+': '+str(e)
    (out/'RESULT.json').write_text(json.dumps(report,indent=2))
    shutil.copy2(BASE/'SOURCE_PARITY.json',out/'SOURCE_PARITY.json');shutil.copy2(BASE/'PAYLOAD_SHA256.json',out/'PAYLOAD_SHA256.json')
    print(json.dumps({'status':report['status'],'github_execution':report['github_execution'],'variant_totals':report.get('variant_totals')}))
    return 0 if report['status']=='PASS_ORIGINAL_MATHEMATICAL_SUITES' else 1
if __name__=='__main__':raise SystemExit(main())
