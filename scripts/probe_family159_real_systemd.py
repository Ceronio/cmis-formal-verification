#!/usr/bin/env python3
"""Bounded real-systemd integration probe, with a synthetic mathematical command.
No Lean, source download, proof compilation, or mathematical acceptance occurs.
AI-assisted engineering. Test the exact preserved Family159 CP39 wrapper.
"""
from pathlib import Path
import hashlib, json, os, shutil, subprocess, sys, time

WRAPPER_BLOB='66fe6ee5f14def6a499bdf2a2948e00213242621'
INNER_FILES={
 'run_openai_math_selected_target.sh':'1a90e61237618a912b3faed38cde5083b5bd4a23',
 'run_family132_github_actions.sh':'84415eae7efc28b447307a598828292f67398923',
 'run_family159_narrowed_target.sh':'ee8538e238b7dd790ebc5fbfbbd60351210d74cf',
}

def blob(data):return hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
def command(args,**kw):return subprocess.run(args,text=True,capture_output=True,timeout=20,**kw)
def show(unit,field):
 p=command(['sudo','-n','systemctl','show',unit,'--property='+field,'--value'])
 return p.stdout.strip()
def write_json(path,value):path.write_text(json.dumps(value,indent=2)+'\n')

SHIM=r'''#!/usr/bin/python3
from pathlib import Path
import hashlib,json,os,subprocess,sys,time
root=Path.cwd(); receipt=root/'cmis_receipt';receipt.mkdir()
(receipt/'FIXTURE_ONLY.txt').write_text('SYNTHETIC mathematical command. Real service controls. Zero proof credit.\n')
name=os.environ['CMIS_PROBE_CASE']; unit=os.environ['CMIS_PROBE_UNIT']
if len(sys.argv)!=2 or Path(sys.argv[1]).resolve()!=root/'scripts/run_family159_narrowed_target.sh':
 raise SystemExit('Unexpected intercepted command')
admission=root/'cmis_admission_receipt';admission.mkdir()
(admission/'11_systemd_mode.txt').write_text('system\n')
if name=='synthetic_success':
 (receipt/'FINAL_STATUS.txt').write_text('PASS_SELECTED_THEOREM\n')
else:
 inner=receipt/'run_comparator_inner.sh'
 inner.write_text('#!/usr/bin/python3\nimport os,json,subprocess,time\nfrom pathlib import Path\np=subprocess.Popen(["/bin/sleep","80"])\nPath(__file__).with_name("probe_pids.json").write_text(json.dumps({"parent":os.getpid(),"child":p.pid}))\ntime.sleep(80)\n')
 inner.chmod(0o700)
 decoy=unit.replace('-own-','-decoy-')
 common=['sudo','-n','systemd-run','--collect','--property=RuntimeMaxSec=90s','--property=TimeoutStopSec=5s',
         '--uid='+str(os.getuid()),'--gid='+str(os.getgid())]
 subprocess.run(common+['--unit='+decoy,'/bin/sh','-c','exec /bin/sleep 80',str(inner)],check=True,timeout=15)
 subprocess.run(common+['--property=RestrictAddressFamilies=~AF_UNIX','--unit='+unit,str(inner)],check=True,timeout=15)
 for _ in range(100):
  if (receipt/'probe_pids.json').exists():break
  time.sleep(.02)
 if not (receipt/'probe_pids.json').exists():raise SystemExit('Own service never wrote PID evidence')
 def show(u,field):return subprocess.check_output(['sudo','-n','systemctl','show',u,'--property='+field,'--value'],text=True,timeout=10).strip()
 state={'own_active':show(unit,'ActiveState'),'decoy_active':show(decoy,'ActiveState'),
        'own_exec':show(unit,'ExecStart'),'decoy_exec':show(decoy,'ExecStart')}
 (root/'BEFORE.json').write_text(json.dumps(state,indent=2)+'\n')
 if name=='explicit_failure':(receipt/'FINAL_STATUS.txt').write_text('COMPARATOR_HOLD\n')
# Preserve a synthetic inner manifest to test nested-manifest retention.
marker=receipt/'FIXTURE_ONLY.txt'
(receipt/'99_receipt_sha256.txt').write_text(hashlib.sha256(marker.read_bytes()).hexdigest()+'  '+str(marker)+'\n')
if name=='timeout':time.sleep(80)
if name=='explicit_failure':raise SystemExit(23)
# Missing status deliberately returns success while the detached service remains.
'''

def validate_manifest(receipt):
 rows=[]
 for line in (receipt/'99_receipt_sha256.txt').read_text().splitlines():
  digest,filename=line.split(maxsplit=1);filename=filename.lstrip('*')
  p=Path(filename);p=p if p.is_absolute() else receipt/p
  if not p.resolve().is_relative_to(receipt.resolve()):raise ValueError('Manifest escapes receipt')
  rows.append({'file':p.name,'matches':hashlib.sha256(p.read_bytes()).hexdigest()==digest})
 observed={p.name for p in receipt.iterdir() if p.is_file() and p.name!='99_receipt_sha256.txt'}
 return rows, observed=={r['file'] for r in rows}

def main():
 repo=Path.cwd();out=repo/'cmis_family159_systemd_probe';out.mkdir(exist_ok=False)
 wrapper=repo/'scripts/run_family159_cp39_bounded_target.sh'
 if blob(wrapper.read_bytes())!=WRAPPER_BLOB:raise ValueError('Wrong preserved wrapper')
 for name,sha in INNER_FILES.items():
  if blob((repo/'scripts'/name).read_bytes())!=sha:raise ValueError('Wrong inherited harness '+name)
 if Path('/proc/1/comm').read_text().strip()!='systemd':raise RuntimeError('Real systemd PID1 required')
 command(['sudo','-n','true']).check_returncode()
 facts={'pid1':Path('/proc/1/comm').read_text().strip(),
        'systemd_version':command(['systemctl','--version']).stdout.splitlines()[0],
        'architecture':os.uname().machine,'logical_cpu_count':os.cpu_count(),
        'scope':'real systemd and GNU timeout; synthetic mathematical command only',
        'wrapper_git_blob':WRAPPER_BLOB,'source_pin_changes':0,'proof_credit':0}
 write_json(out/'ENVIRONMENT.json',facts)
 results=[]
 for idx,(name,expected_code,expected_status) in enumerate([
  ('synthetic_success',0,'PASS_SELECTED_THEOREM'),
  ('explicit_failure',23,'COMPARATOR_HOLD'),
  ('missing_status',4,'EXECUTION_CONTRACT_HOLD'),
  ('timeout',124,'RESOURCE_TIMEOUT_HOLD'),
 ]):
  root=out/name;root.mkdir();(root/'scripts').mkdir();(root/'bin').mkdir()
  for f in INNER_FILES:shutil.copy2(repo/'scripts'/f,root/'scripts'/f)
  shim=root/'bin/bash';shim.write_text(SHIM);shim.chmod(0o700)
  unit=f'run-cmis159-own-{os.environ.get("GITHUB_RUN_ID","local")}-{idx}.service'
  decoy=unit.replace('-own-','-decoy-')
  env=os.environ.copy();env.update(PATH=str(root/'bin')+':'+env['PATH'],EXECUTION_MODE='full',
       CMIS_VERIFICATION_TIMEOUT_SECONDS='8',CMIS_PROBE_CASE=name,CMIS_PROBE_UNIT=unit)
  start=time.monotonic()
  try:
   p=subprocess.run(['/bin/bash',str(wrapper)],cwd=root,env=env,text=True,capture_output=True,timeout=230)
   elapsed=time.monotonic()-start
   (root/'outer.stdout').write_text(p.stdout);(root/'outer.stderr').write_text(p.stderr)
   receipt=root/'cmis_receipt';status=(receipt/'FINAL_STATUS.txt').read_text().strip()
   rows,complete=validate_manifest(receipt)
   nested=(receipt/'96_inner_receipt_sha256.txt').read_text().splitlines()
   nested_ok=all(hashlib.sha256(Path(line.split(maxsplit=1)[1]).read_bytes()).hexdigest()==line.split()[0] for line in nested)
   checks={'exit_code':p.returncode==expected_code,'classified_status':status==expected_status,
      'outer_manifest_hashes':all(r['matches'] for r in rows),'outer_manifest_complete':complete,
      'inner_manifest_preserved':nested_ok,'elapsed_under_30_seconds':elapsed<30}
   state={}
   if name!='synthetic_success':
    before=json.loads((root/'BEFORE.json').read_text())
    state={'own_state':show(unit,'ActiveState'),'own_load':show(unit,'LoadState'),
           'decoy_state':show(decoy,'ActiveState')}
    pids=json.loads((receipt/'probe_pids.json').read_text())
    time.sleep(.2)
    state['pids_surviving']={k:Path(f'/proc/{v}').exists() for k,v in pids.items()}
    checks.update({'own_service_started':before['own_active']=='active',
      'decoy_started':before['decoy_active']=='active',
      'own_service_stopped':state['own_state'] not in ('active','activating','deactivating'),
      'own_parent_and_child_stopped':not any(state['pids_surviving'].values()),
      'decoy_untouched':state['decoy_state']=='active',
      'decoy_contains_target_only_as_argument':str(receipt/'run_comparator_inner.sh') in before['decoy_exec']
            and before['decoy_exec'].startswith('{ path=/bin/sh ; '),
      'own_exec_exact':before['own_exec'].startswith('{ path='+str(receipt/'run_comparator_inner.sh')+' ; '),
      'receipt_cannot_claim_pass':not status.startswith('PASS')})
   result={'case':name,'engineering_fixture_only':True,'code':p.returncode,'status':status,
      'seconds':round(elapsed,3),'checks':checks,'states':state,'manifest':rows,
      'pass':all(checks.values())}
  except Exception as exc:result={'case':name,'pass':False,'error':type(exc).__name__+': '+str(exc)}
  finally:
   for u in (unit,decoy):command(['sudo','-n','systemctl','stop',u])
  results.append(result);write_json(root/'RESULT.json',result)
 summary={'schema':'CMIS_FAMILY159_REAL_SYSTEMD_PROBE_V1','environment':facts,'cases':results,
   'case_count':len(results),'passed_cases':sum(x['pass'] for x in results),
   'all_passed':all(x['pass'] for x in results),'mathematical_builds':0,'formal_credit':0,
   'limitations':['Mathematical command replaced by explicit fixture shim.',
       'System mode tested; user-manager mode not tested.',
       'Not a performance benchmark or proof run.']}
 write_json(out/'SUMMARY.json',summary)
 print(json.dumps(summary,indent=2))
 raise SystemExit(0 if summary['all_passed'] else 1)
if __name__=='__main__':main()
