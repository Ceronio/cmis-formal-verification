#!/usr/bin/env python3
"""Read exact Git blobs and capture Family 159's local import graph; never compile."""
from pathlib import Path
from collections import deque
import hashlib, json, re, subprocess
PIN='fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb'
ROOTS=['OAI.Combinatorics.Progressions.Main','OAI.Combinatorics.Progressions.Results.Conclusions']
REPO=Path('.family159-source/openai-math')
OUT=Path('family159_dependency_snapshot')

def git(*args):return subprocess.check_output(['git','-C',str(REPO),*args])
def clean(text):
    out=[];i=0;depth=0;quote=False
    while i<len(text):
        if depth:
            if text.startswith('/-',i):depth+=1;out.extend('  ');i+=2
            elif text.startswith('-/',i):depth-=1;out.extend('  ');i+=2
            else:out.append('\n' if text[i]=='\n' else ' ');i+=1
        elif quote:
            if text[i]=='\\':out.extend('  ');i+=2
            elif text[i]=='"':quote=False;out.append(' ');i+=1
            else:out.append('\n' if text[i]=='\n' else ' ');i+=1
        elif text.startswith('/-',i):depth=1;out.extend('  ');i+=2
        elif text.startswith('--',i):
            j=text.find('\n',i);j=len(text) if j<0 else j;out.extend(' '*(j-i));i=j
        elif text[i]=='"':quote=True;out.append(' ');i+=1
        else:out.append(text[i]);i+=1
    if depth or quote:raise ValueError('Unterminated comment/string')
    return ''.join(out)

def main():
    if git('rev-parse','HEAD').decode().strip()!=PIN:raise ValueError('Wrong source pin')
    OUT.mkdir(exist_ok=False)
    tree={}
    for row in git('ls-tree','-rz',PIN).split(b'\0'):
        if not row:continue
        info,path=row.split(b'\t',1);mode,kind,sha=info.decode().split()
        if kind=='blob':tree[path.decode()]=sha
    batch=subprocess.Popen(['git','-C',str(REPO),'cat-file','--batch'],stdin=subprocess.PIPE,stdout=subprocess.PIPE)
    captured={};graph={};external=set()
    def read(path):
        if path in captured:return (OUT/path).read_bytes()
        sha=tree[path];batch.stdin.write((sha+'\n').encode());batch.stdin.flush()
        header=batch.stdout.readline().decode().split()
        if len(header)!=3 or header[0]!=sha or header[1]!='blob':raise ValueError(header)
        size=int(header[2]);data=batch.stdout.read(size)
        if batch.stdout.read(1)!=b'\n':raise ValueError('Bad cat-file framing')
        actual=hashlib.sha1(b'blob '+str(len(data)).encode()+b'\0'+data).hexdigest()
        if actual!=sha:raise ValueError('Wrong Git identity '+path)
        dest=OUT/path;dest.parent.mkdir(parents=True,exist_ok=True);dest.write_bytes(data)
        captured[path]={'path':path,'bytes':len(data),'git_blob':sha,'sha256':hashlib.sha256(data).hexdigest()}
        return data
    queue=deque(ROOTS)
    while queue:
        mod=queue.popleft()
        if mod in graph:continue
        path='lean/'+mod.replace('.','/')+'.lean'
        if path not in tree:
            if mod.startswith('OAI.'):raise ValueError('Missing local module '+mod)
            external.add(mod);continue
        text=clean(read(path).decode());imports=[]
        for line in text.splitlines():
            m=re.match(r'^\s*(?:public\s+|private\s+)?import\s+(.+?)\s*$',line)
            if m:
                for name in m.group(1).split():
                    if not re.fullmatch(r'[\w.]+',name):raise ValueError('Unsupported module '+name)
                    imports.append(name)
        graph[mod]=imports;queue.extend(imports)
        if len(graph)>6000:raise ValueError('Unexpected closure growth')
    def reachable(root):
        seen=set();pending=[root]
        while pending:
            x=pending.pop()
            if x in seen or x not in graph:continue
            seen.add(x);pending.extend(graph[x])
        return sorted(seen)
    closures={r:reachable(r) for r in ROOTS}
    for p in ['lean/ComparatorChallenges/ErdosReciprocal.json','lean/ComparatorChallenges/ErdosReciprocal.lean','lean/docs/159.md','lean/lakefile.toml','lean/lakefile.lean','lean/lake-manifest.json','lean/lean-toolchain']:
        if p in tree:read(p)
    batch.stdin.close();batch.wait(timeout=10)
    metadata={'source_pin':PIN,'source_repository':'openai/math','compiled':False,
      'local_graph':dict(sorted(graph.items())),'closures':closures,'external_import_roots':sorted(external),
      'limit':'Lexical project-local import graph; no external transitive closure or declaration-use pruning.'}
    (OUT/'DEPENDENCY_GRAPH.json').write_text(json.dumps(metadata,indent=2)+'\n')
    (OUT/'SOURCE_MANIFEST.json').write_text(json.dumps({'source_pin':PIN,'files':sorted(captured.values(),key=lambda d:d['path'])},indent=2)+'\n')
    print(json.dumps({'closures':{r:len(v) for r,v in closures.items()},'captured_files':len(captured),'compiled':False},indent=2))
if __name__=='__main__':main()
