#!/usr/bin/env python3
"""Public CP05 bounded exact-moment proof checker. No user archive or external deps.
This is not a full CP05 source replay, Lean proof, or external certification.
"""
from fractions import Fraction as F
from itertools import product
from pathlib import Path
from hashlib import sha256
import argparse, json, platform, re
counts={}
pattern=re.compile(r'[+-]?\d+(?:/\d+|\.\d+)?\Z',re.ASCII)
def assert_eq(group,actual,want):
    counts[group]=counts.get(group,0)+1
    if actual!=want:raise AssertionError(f'{group} #{counts[group]}: {actual!r} vs {want!r}')
def Q(value):
    if type(value) is int: return F(value)
    if type(value) is not str or not 0<len(value)<=1300 or not pattern.fullmatch(value):raise ValueError('exact rational only')
    try:f=F(value)
    except (ZeroDivisionError,ValueError) as exc:raise ValueError('invalid denominator') from exc
    if max(abs(f.numerator).bit_length(),f.denominator.bit_length())>2048:raise ValueError('rational budget')
    return f

def verify(model,cert):
    try:
        if type(model) is not dict or set(model)!={'worlds','H','lo','hi','cost'}:return False
        if type(cert) is not dict or set(cert)!={'kind','alpha','up','down','mass','claimed'}:return False
        paths=model['worlds'];H=model['H'];n=len(paths);k=len(H)
        if type(paths) is not list or not 1<=n<=64 or len(set(paths))!=n:return False
        if any(type(w) is not str or not w for w in paths):return False
        if type(H) is not list or any(type(r) is not list or len(r)!=n for r in H):return False
        H=[[Q(x) for x in r] for r in H]
        lo=list(map(Q,model['lo']));hi=list(map(Q,model['hi']));cost=list(map(Q,model['cost']))
        up=list(map(Q,cert['up']));dn=list(map(Q,cert['down']))
        if any(len(x)!=k for x in (lo,hi,up,dn)) or len(cost)!=n:return False
        if any(l>u for l,u in zip(lo,hi)) or any(u<0 for u in up) or any(d>0 for d in dn):return False
        alpha=Q(cert['alpha']);bound=alpha+sum((up[i]*hi[i]+dn[i]*lo[i] for i in range(k)),F(0))
        kind=cert['kind']
        if type(kind) is not str or kind not in ('max','min','infeasible'):return False
        sign=1 if kind=='max' else -1 if kind=='min' else 0
        for j in range(n):
            lhs=alpha+sum(((up[i]+dn[i])*H[i][j] for i in range(k)),F(0))
            if lhs<sign*cost[j]:return False
        if kind=='infeasible':return cert['mass']==[] and Q(cert['claimed'])==bound and bound<0
        mass=list(map(Q,cert['mass']))
        if len(mass)!=n or any(m<0 for m in mass) or sum(mass,F(0))!=1:return False
        if any(not lo[i]<=sum((H[i][j]*mass[j] for j in range(n)),F(0))<=hi[i] for i in range(k)):return False
        val=sum((cost[j]*mass[j] for j in range(n)),F(0))
        return val==Q(cert['claimed']) and bound==sign*val
    except (ValueError,TypeError,KeyError,ZeroDivisionError,OverflowError):return False

def run():
    for e in (0,1,2,10,40,80,120,150):
        for q in (F(1,10**e),F(1)-F(1,10**e)):
            m={'worlds':['0','1'],'H':[['0','1']],'lo':[str(q)],'hi':[str(q)],'cost':['0','1']}
            for sense in ('max','min'):
                c={'kind':sense,'alpha':'0','up':['1' if sense=='max' else '0'],
                   'down':['0' if sense=='max' else '-1'],'mass':[str(1-q),str(q)],'claimed':str(q)}
                assert_eq('sharp_exact_optimum',verify(m,c),True)
                for k,bad in [('claimed','2'),('alpha','1'),('mass',['0','0']),('up',['-1']),('down',['1']),('up',[True]),('claimed',float('nan'))]:
                    assert_eq('invalid_optimum_rejected',verify(m,{**c,k:bad}),False)
                assert_eq('wrong_dimension_rejected',verify({**m,'cost':['0','1','0']},c),False)
    # Exact Farkas contradiction: same moment forced to be simultaneously 0 and 1.
    m={'worlds':['0','1'],'H':[['0','1'],['0','1']],'lo':['1','0'],'hi':['1','0'],'cost':['0','1']}
    c={'kind':'infeasible','alpha':'0','up':['0','1'],'down':['-1','0'],'mass':[],'claimed':'-1'}
    assert_eq('strict_farkas',verify(m,c),True)
    for k,v in [('claimed','0'),('alpha','1'),('up',['0','0']),('down',['0','0']),('mass',['1','0']),('kind','max'),('up',['0',True])]:
        assert_eq('invalid_farkas_rejected',verify(m,{**c,k:v}),False)
    f={**m,'lo':['0','0'],'hi':['1','1']}
    assert_eq('feasible_is_not_contradiction',verify(f,c),False)
    for n in (1,2,3):
        paths=[''.join(bits) for bits in product('01',repeat=n)]
        for j in range(len(paths)):
            mask=[str(int(i==j)) for i in range(len(paths))]
            m={'worlds':paths,'H':[mask],'lo':['1'],'hi':['1'],'cost':mask}
            c={'kind':'max','alpha':'0','up':['1'],'down':['0'],'mass':mask,'claimed':'1'}
            assert_eq('atomic_maximum',verify(m,c),True)
            assert_eq('altered_atom_rejected',verify(m,{**c,'claimed':'0'}),False)

def main():
    parser=argparse.ArgumentParser();parser.add_argument('--out',required=True);a=parser.parse_args()
    error=None
    try:run();status='PASS'
    except Exception as exc:status='FAIL';error=f'{type(exc).__name__}: {exc}'
    report={'checkpoint':'CP05','status':status,'counts':counts,'assertions':sum(counts.values()),
        'source_sha256':sha256(Path(__file__).read_bytes()).hexdigest(),
        'python':platform.python_version(),
        'scope':'Synthetic exact finite-moment primal/dual and Farkas certificates ONLY; original archival suite and whole-source identity not checked by this GitHub run.',
        'error':error}
    dst=Path(a.out);dst.parent.mkdir(parents=True,exist_ok=True);dst.write_text(json.dumps(report,sort_keys=True,indent=2)+'\n')
    print(json.dumps(report,sort_keys=True,indent=2));return 0 if status=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
