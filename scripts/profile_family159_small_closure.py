#!/usr/bin/env python3
"""Engineering-only A/B profile of exact public Lean sources; never admits a theorem.
The diagnostic-only two-thread arm adds LEAN_NUM_THREADS to Landrun's allowlist.
This change is NOT deployed to the original Comparator or verification workflow.
"""
from pathlib import Path
from collections import deque
import hashlib, json, os, re, shlex, subprocess, time
PIN='fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
TARGET='OAI.Combinatorics.Progressions.Polynomial.PolynomialPatchProductBudget'
OUT=Path('family159_small_closure_profile').resolve()
ROOT=Path.cwd(); PROJECT=ROOT/'.cmis-work/openai-math/lean'

def cmd(args, **kw):
    return subprocess.run(args,text=True,capture_output=True,timeout=20,**kw)
def show(unit,key):
    p=cmd(['sudo','-n','systemctl','show',unit,'--property='+key,'--value'])
    return p.stdout.strip()
def save(p,x):p.write_text(json.dumps(x,indent=2)+'\n')
def blob(b):return hashlib.sha1(b'blob '+str(len(b)).encode()+b'\0'+b).hexdigest()

def main():
    OUT.mkdir(exist_ok=False)
    if cmd(['git','-C',str(PROJECT),'rev-parse','HEAD']).stdout.strip()!=PIN:raise ValueError('Wrong source pin')
    leanhome=next((ROOT/'.cmis-tools').glob('lean-4.34.1-linux'))
    landrun=ROOT/'.cmis-tools/bin/landrun'
    path=str(leanhome/'bin')+':'+str(ROOT/'.cmis-tools/bin')+':'+os.environ['PATH']
    baseenv=os.environ.copy();baseenv['PATH']=path;baseenv['LEAN_ABORT_ON_PANIC']='1';baseenv.pop('LEAN_NUM_THREADS',None)
    modules={};pending=deque([TARGET])
    while pending:
        m=pending.popleft()
        if m in modules:continue
        p=PROJECT/(m.replace('.','/')+'.lean');b=p.read_bytes()
        expected=cmd(['git','-C',str(PROJECT),'rev-parse',PIN+':lean/'+str(p.relative_to(PROJECT))]).stdout.strip()
        if blob(b)!=expected:raise ValueError('Source differs '+m)
        imports=re.findall(r'^import\s+(OAI\.[\w.]+)\s*$',b.decode(),re.M)
        modules[m]={'git_blob':expected,'sha256':hashlib.sha256(b).hexdigest(),'imports':imports}
        pending.extend(imports)
    if len(modules)!=8:raise ValueError('Unexpected benchmark closure')
    save(OUT/'SOURCE_IDENTITIES.json',{'pin':PIN,'target':TARGET,'modules':modules})
    metadata={'kind':'ENGINEERING_ONLY_NO_PROOF_CREDIT','target':TARGET,'source_pin':PIN,
      'diagnostic_scope':'Eight-module completed-source proxy, NOT the 3302-module frontier.',
      'altered_environment_arm':'LEAN_NUM_THREADS=2, diagnostic allowlist only; original Comparator unchanged.',
      'cpu_count':os.cpu_count(),'affinity_cpus':sorted(os.sched_getaffinity(0)),
      'memory_kib':{k:int(v.split()[0]) for k,v in (line.split(':',1) for line in Path('/proc/meminfo').read_text().splitlines()) if k in ['MemTotal','SwapTotal']},
      'lean_version':cmd([str(leanhome/'bin/lean'),'--version']).stdout.strip(),
      'lake_version':cmd([str(leanhome/'bin/lake'),'--version']).stdout.strip(),
      'trial_command_ceiling_seconds':240,'trial_order':['default','two_threads','two_threads','default']}
    save(OUT/'ENVIRONMENT.json',metadata)
    for name,argv in [('lean_help',[str(leanhome/'bin/lean'),'--help']),('lake_help',[str(leanhome/'bin/lake'),'--help'])]:
        r=cmd(argv);(OUT/(name+'.txt')).write_text(r.stdout+r.stderr)
    results=[]
    for idx,mode in enumerate(metadata['trial_order'],1):
        trial=OUT/f'{idx}_{mode}';trial.mkdir()
        build=PROJECT/'.lake/build'
        if build.exists():build.rename(PROJECT/'.lake'/f'build-preserved-before-profile-{idx}')
        unit=f'run-cmis159-profile-{os.environ.get("GITHUB_RUN_ID","local")}-{idx}.service'
        env=baseenv.copy()
        args=[str(landrun),'--best-effort','--ro','/','--rw','/dev','-ldd','-add-exec','--env','PATH','--env','HOME','--env','LEAN_ABORT_ON_PANIC']
        if mode=='two_threads':env['LEAN_NUM_THREADS']='2';args+=['--env','LEAN_NUM_THREADS']
        args+=['--ro',str(PROJECT),'--rwx',str(PROJECT/'.lake'),'--rox',str(leanhome),'--rox','/usr/bin/git','--','lake','build',TARGET]
        inner=trial/'inner.sh'
        exports='export PATH='+shlex.quote(path)+'\nexport HOME='+shlex.quote(os.environ['HOME'])+'\nexport LEAN_ABORT_ON_PANIC=1\n'
        exports+=('export LEAN_NUM_THREADS=2\n' if mode=='two_threads' else 'unset LEAN_NUM_THREADS\n')
        inner.write_text('#!/usr/bin/env bash\nset -Eeuo pipefail\n'+exports+'cd '+shlex.quote(str(PROJECT))+'\nexec '+shlex.join(args)+'\n');inner.chmod(0o700)
        invocation=['sudo','-n','systemd-run','--wait','--pipe','--collect','--unit='+unit,
            '--uid='+str(os.getuid()),'--gid='+str(os.getgid()),'--property=RestrictAddressFamilies=~AF_UNIX',
            '--property=RuntimeMaxSec=240s','--property=TimeoutStopSec=5s',
            '--property=CPUAccounting=yes','--property=MemoryAccounting=yes',str(inner)]
        start=time.monotonic();samples=[];cg=None
        with (trial/'stdout.log').open('w') as stdout,(trial/'stderr.log').open('w') as stderr:
            proc=subprocess.Popen(invocation,cwd=PROJECT,env=env,stdout=stdout,stderr=stderr,text=True)
            while proc.poll() is None:
                if time.monotonic()-start>255:
                    cmd(['sudo','-n','systemctl','stop',unit]);proc.terminate();break
                if cg is None:
                    value=show(unit,'ControlGroup')
                    if value.startswith('/') and '..' not in Path(value).parts:cg=Path('/sys/fs/cgroup')/value.lstrip('/')
                row={'seconds':round(time.monotonic()-start,4)}
                if cg and cg.is_dir():
                    for name in ['cpu.stat','memory.current','memory.peak','memory.swap.current','memory.events','io.stat','pids.current']:
                        p=cg/name
                        if p.exists():
                            try:row[name]=p.read_text().strip()
                            except OSError:pass
                    p=cg/'cgroup.procs'
                    if p.exists():
                        try:row['process_count']=len(p.read_text().splitlines())
                        except OSError:pass
                samples.append(row);time.sleep(.5)
            try:rc=proc.wait(timeout=15)
            except subprocess.TimeoutExpired:
                proc.kill();rc=proc.wait()
        elapsed=time.monotonic()-start
        cmd(['sudo','-n','systemctl','stop',unit])
        output=(trial/'stdout.log').read_text();done=re.findall(r'Built (OAI\.[\w.]+) \(([0-9.]+)(ms|s)\)',output)
        observed={x[0] for x in done}
        source_ok=all(blob((PROJECT/(m.replace('.','/')+'.lean')).read_bytes())==v['git_blob'] for m,v in modules.items())
        numeric=lambda field:max([int(r[field]) for r in samples if field in r]+[0])
        cpu=max([int(dict(line.split() for line in r['cpu.stat'].splitlines()).get('usage_usec',0)) for r in samples if 'cpu.stat' in r]+[0])
        events={}
        for r in samples:
            for line in r.get('memory.events','').splitlines():
                k,v=line.split();events[k]=max(events.get(k,0),int(v))
        result={'trial':idx,'mode':mode,'returncode':rc,'seconds':round(elapsed,4),
          'completed_modules':sorted(observed),'module_durations':{m:float(v)*(.001 if u=='ms' else 1) for m,v,u in done},
          'source_unchanged':source_ok,'exact_eight_modules_built':observed==set(modules),
          'sampled_cpu_seconds':cpu/1e6,'sampled_peak_memory_bytes':numeric('memory.current'),
          'cgroup_peak_memory_bytes':numeric('memory.peak'),'sampled_peak_swap_bytes':numeric('memory.swap.current'),
          'memory_events':events,'samples':len(samples),
          'success':rc==0 and source_ok and observed==set(modules),
          'formal_credit':0}
        save(trial/'RESULT.json',result)
        (trial/'RESOURCE_SAMPLES.jsonl').write_text(''.join(json.dumps(r)+'\n' for r in samples))
        results.append(result)
        if not result['success']:break
    summary={'kind':'ENGINEERING_ONLY','environment':metadata,'results':results,
       'all_trials_completed':len(results)==4 and all(r['success'] for r in results),
       'formal_credit':0,'limitation':'Two cold workspace-build trials per arm; shared pinned external cache and warm filesystem. Proxy cannot establish the unfinished frontier or final proof runtime.'}
    save(OUT/'SUMMARY.json',summary)
    print(json.dumps(summary,indent=2))
    raise SystemExit(0 if summary['all_trials_completed'] else 1)
if __name__=='__main__':main()
