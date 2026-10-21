#!/usr/bin/env python3
"""Capture exact public inputs and project-local Lean import closures; never compile."""
from pathlib import Path
from collections import deque
import hashlib, json, re, subprocess

PIN = 'fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
REPO = Path('.source-snapshot/openai-math')
OUT = Path('cmis_original_source_snapshot')
CONFIGS = ['ElementaryPositivity', 'RamseyFive', 'SharpLogRamsey']
PREFIXES = [
 'preprints/Elementary-Positivity-of-Chromatic-Quasisymmetric-Functions-September-24-2026/',
 'preprints/The-Sharp-Logarithmic-Exponent-of-r-5-t-September-24-2026/',
 'preprints/Sharp-Logarithmic-Exponents-for-Fixed-Off-Diagonal-Ramsey-Numbers-September-24-2026/',
]

def git(*args, raw=False):
    data = subprocess.check_output(['git', '-C', str(REPO), *args])
    return data if raw else data.decode('utf-8').strip()

def strip_comments(text):
    out=[]; i=0; depth=0; quote=False
    while i<len(text):
        if depth:
            if text.startswith('/-',i): depth+=1; out.extend('  '); i+=2
            elif text.startswith('-/',i): depth-=1; out.extend('  '); i+=2
            else: out.append('\n' if text[i]=='\n' else ' '); i+=1
        elif quote:
            if text[i]=='\\': out.extend('  '); i+=2
            elif text[i]=='"': quote=False; out.append(' '); i+=1
            else: out.append('\n' if text[i]=='\n' else ' '); i+=1
        elif text.startswith('/-',i): depth=1; out.extend('  '); i+=2
        elif text.startswith('--',i):
            end=text.find('\n',i); end=len(text) if end<0 else end
            out.extend(' '*(end-i)); i=end
        elif text[i]=='"': quote=True; out.append(' '); i+=1
        else: out.append(text[i]); i+=1
    if depth: raise ValueError('Unterminated block comment')
    return ''.join(out)

OUT.mkdir(parents=True,exist_ok=False)
if git('rev-parse','HEAD') != PIN: raise SystemExit('Wrong source pin')
entries={}
for rec in git('ls-tree','-rz',PIN,raw=True).split(b'\0'):
    if not rec: continue
    info,path=rec.split(b'\t',1); mode,typ,sha=info.decode().split()
    if typ=='blob': entries[path.decode()]=sha
captured={}
def capture(path):
    if path not in entries: raise FileNotFoundError(path)
    if path not in captured:
        data=git('show',f'{PIN}:{path}',raw=True)
        actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual != entries[path]: raise ValueError('Git blob mismatch '+path)
        dest=OUT/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        captured[path]={'path':path,'bytes':len(data),'git_blob':actual,
                        'sha256':hashlib.sha256(data).hexdigest()}
    return (OUT/path).read_text(encoding='utf-8')

def closure(root):
    seen={}; pending=deque([root]); external=set()
    while pending:
        mod=pending.popleft()
        if mod in seen: continue
        path='lean/'+mod.replace('.','/')+'.lean'
        if path not in entries:
            if mod.split('.')[0] not in {'Mathlib','Batteries','Lean','Init','Std','Qq','Aesop','ProofWidgets','ImportGraph','Plausible','LeanSearchClient'}:
                raise ValueError('Unresolved project import '+mod)
            external.add(mod);continue
        body=capture(path)
        clean=strip_comments(body)
        imports=[]
        for line in clean.splitlines():
            m=re.match(r'^\s*(?:public\s+)?import\s+(.+?)\s*$',line)
            if m:
                for token in m.group(1).split():
                    if not re.fullmatch(r'[\w.\u00A0-\uFFFF]+',token): raise ValueError('Unsupported import '+token)
                    imports.append(token)
        seen[mod]=imports
        pending.extend(imports)
        if len(seen)>6000: raise ValueError('Closure safety limit')
    done=set();active=set()
    def visit(m):
        if m in active: raise ValueError('Import cycle '+m)
        if m in done or m not in seen:return
        active.add(m)
        for child in seen[m]: visit(child)
        active.remove(m);done.add(m)
    visit(root)
    lexical=[]
    for mod in sorted(seen):
        path='lean/'+mod.replace('.','/')+'.lean'
        clean=strip_comments((OUT/path).read_text())
        for line_num,line in enumerate(clean.splitlines(),1):
            if re.search(r'\b(sorry|admit|axiom|unsafe|native_decide)\b',line):
                lexical.append({'path':path,'line':line_num,'text':line.strip()})
    return {'root':root,'modules':dict(sorted(seen.items())), 'module_count':len(seen),
            'external_direct_imports':sorted(external),'lexical_flags':lexical,
            'scope':'Project-local imports only; no Mathlib/core transitive closure or Lean execution.'}

closures={}
for name in CONFIGS:
    cfg=json.loads(capture(f'lean/ComparatorChallenges/{name}.json'))
    capture(f'lean/ComparatorChallenges/{name}.lean')
    closures[name]={'configuration':cfg,'solution':closure(cfg['solution_module']),
                    'challenge':closure(cfg['challenge_module'])}
for p in ['lean/docs/169.md','lean/docs/170.md','lean/lean-toolchain','lean/lake-manifest.json','lean/lakefile.lean','lean/lakefile.toml']:
    if p in entries:capture(p)
for path in sorted(entries):
    if any(path.startswith(prefix) for prefix in PREFIXES) and path.endswith(('.tex','.bib','.md')):capture(path)
(OUT/'CLOSURES.json').write_text(json.dumps(closures,indent=2)+'\n')
manifest={'source_repository':'openai/math','source_commit':PIN,'compiled':False,
          'files':list(sorted(captured.values(),key=lambda x:x['path'])),
          'note':'Exact public source capture only. No theorem, definition or axiom verdict.'}
(OUT/'SOURCE_MANIFEST.json').write_text(json.dumps(manifest,indent=2)+'\n')
print(json.dumps({k:{'solution_modules':v['solution']['module_count'],
                    'challenge_modules':v['challenge']['module_count'],
                    'lexical_flags':len(v['solution']['lexical_flags'])} for k,v in closures.items()},indent=2))
