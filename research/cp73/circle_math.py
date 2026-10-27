#!/usr/bin/env python3
"""CMIS CP73. Exact rational circle/quad interpolation; not a universal theorem proof.

This code uses only Python stdlib; all arithmetic is Fraction-exact.
The publisher-selected theorem needs its own protected Lean/Comparator run.
"""
from __future__ import annotations
import argparse,itertools,json,math
from fractions import Fraction as Q
from pathlib import Path
MONOMIALS=((0,0),(1,0),(0,1),(2,0),(1,1),(0,2))
def rat(v): return v if isinstance(v,Q) else Q(v)
def stereo(t,center=(Q(0),Q(0)),radius=Q(1)):
    t=rat(t);a,b=map(rat,center);r=rat(radius)
    assert r>0
    return (a+r*(1-t*t)/(1+t*t),b+r*2*t/(1+t*t))
def distance_squared(a,b):return sum(((x-y)**2 for x,y in zip(a,b)),Q(0))
def area2(a,b,c):return (b[0]-a[0])*(c[1]-a[1])-(b[1]-a[1])*(c[0]-a[0])
def secant(a,b):
    assert a!=b
    x,y=a;u,v=b
    return (y-v,u-x,x*v-u*y)
def secant_eval(L,p):
    x,y=p;a,b,c=L
    return a*x+b*y+c
def product(L,M):
    a,b,c=L;d,e,f=M
    return (c*f,a*f+c*d,b*f+c*e,a*d,a*e+b*d,b*e)
def peval(coeff,p):
    x,y=p
    return sum((v*x**i*y**j for v,(i,j) in zip(coeff,MONOMIALS)),Q(0))
def isolate_five(points):
    pts=tuple(points)
    assert len(pts)==5 and len(set(pts))==5
    result=[]
    for i in range(5):
        j=[k for k in range(5) if k!=i]
        f=product(secant(pts[j[0]],pts[j[1]]),secant(pts[j[2]],pts[j[3]]))
        normal=peval(f,pts[i])
        assert normal!=0
        g=tuple(v/normal for v in f)
        assert all(peval(g,p)==int(k==i) for k,p in enumerate(pts))
        result.append(g)
    return tuple(result)
def eval_rows(points):
    return [tuple(x**a*y**b for a,b in MONOMIALS) for x,y in points]
def rank(A):
    A=[list(map(rat,row)) for row in A]
    if not A:return 0
    n=len(A);cols=len(A[0]);r=0
    assert all(len(z)==cols for z in A)
    for c in range(cols):
        pivot=next((i for i in range(r,n) if A[i][c]),None)
        if pivot is None:continue
        A[r],A[pivot]=A[pivot],A[r]
        v=A[r][c];A[r]=[x/v for x in A[r]]
        for i in range(n):
            if i!=r:
                w=A[i][c];A[i]=[x-w*y for x,y in zip(A[i],A[r])]
        r+=1
        if r==n:break
    return r
def det(A):
    A=[list(map(rat,row)) for row in A];n=len(A)
    assert all(len(row)==n for row in A)
    if not n:return Q(1)
    result=Q(1)
    for c in range(n):
        pivot=next((i for i in range(c,n) if A[i][c]),None)
        if pivot is None:return Q(0)
        if pivot!=c:A[c],A[pivot]=A[pivot],A[c];result=-result
        v=A[c][c];result*=v
        for i in range(c+1,n):
            w=A[i][c]/v
            for j in range(c+1,n):A[i][j]-=w*A[c][j]
            A[i][c]=0
    return result
def circle_poly(center,radius):
    a,b=map(rat,center);r=rat(radius)
    return (a*a+b*b-r*r,-2*a,-2*b,Q(1),Q(0),Q(1))
def rational_tensor(center,radius):
    a,b=map(rat,center);r=rat(radius)
    return ((a*a+b*b-r*r,-a,-b),(-a,Q(1),Q(0)),(-b,Q(0),Q(1)))
def verify_tensor(points,center,radius):
    P=rational_tensor(center,radius)
    assert all(P[i+1][j+1]==int(i==j) for i in range(2) for j in range(2))
    for x,y in points:
        u=(Q(1),x,y)
        assert sum((u[i]*P[i][j]*u[j] for i in range(3) for j in range(3)),Q(0))==0
    return P
def no_three_collinear(points):
    return all(area2(a,b,c)!=0 for a,b,c in itertools.combinations(points,3))
def distance_automorphisms(points):
    n=len(points);D=[[distance_squared(p,q) for q in points] for p in points]
    G=[p for p in itertools.permutations(range(n)) if all(D[i][j]==D[p[i]][p[j]] for i in range(n) for j in range(n))]
    return len(G),all({p[i] for p in G}==set(range(n)) for i in range(n))
def five_witness(points,center,radius):
    assert no_three_collinear(points)
    iso=isolate_five(points);mat=eval_rows(points)
    assert rank(mat)==5
    minor=next(((cols,det([[row[k] for k in cols] for row in mat]))
                 for cols in itertools.combinations(range(6),5)
                 if det([[row[k] for k in cols] for row in mat])),None)
    assert minor is not None and minor[1]!=0
    assert all(peval(iso[i],points[j])==int(i==j) for i in range(5) for j in range(5))
    assert all(peval(circle_poly(center,radius),p)==0 for p in points)
    verify_tensor(points,center,radius)
    return iso,minor
def research():
    center=(Q(2,3),Q(-3,4));radius=Q(5,2)
    params=(-3,-2,-1,0,2)
    points=tuple(stereo(t,center,radius) for t in params)
    assert len(set(points))==5
    assert all(distance_squared(p,center)==radius**2 for p in points)
    isolates,(minor,delta)=five_witness(points,center,radius)
    assert distance_automorphisms(points)==(1,False), "five-point circle need not be transitive"
    six=points+(stereo(3,center,radius),)
    assert rank(eval_rows(six))==5
    assert all(rank(eval_rows([p for j,p in enumerate(six) if j!=i]))==5 for i in range(6))
    # A six-point rational circle has a direct valid tensor witness even though
    # its six quadratic rows are necessarily dependent. Avoid false negative!
    verify_tensor(six,center,radius)
    collinear=[(Q(i),Q(0)) for i in range(5)]
    assert rank(eval_rows(collinear))==3
    assert not no_three_collinear(collinear)
    pool=tuple(stereo(t,center,radius) for t in range(-5,5))
    count=0
    for choice in itertools.combinations(range(10),5):
        nodes=tuple(pool[i] for i in choice)
        assert no_three_collinear(nodes)
        iso=isolate_five(nodes)
        assert rank(eval_rows(nodes))==5
        assert all(peval(iso[i],nodes[j])==int(i==j) for i in range(5) for j in range(5))
        count+=1
    assert count==252
    extension={}
    for n in range(1,6):
        original=points[:n];extra=points[n:]
        assert len(set(original+extra))==5
        isolate_five(original+extra)
        extension[str(n)]={"original":n,"new_points":len(extra)}
    assert distance_squared(center,center)==0
    return {
        "checkpoint":"CP73","family":172,"status":"PASS_CP73_EXACT_BOUNDED_RESEARCH",
        "mathematical_scope":"five-circle-point quadratic isolators and full-rank witnesses; not full general theorem",
        "parameters":[str(z) for z in params],"points":[[str(v) for v in p] for p in points],
        "center":[str(v) for v in center],"radius":str(radius),
        "five_quadratic_rank":rank(eval_rows(points)),"exact_interpolation_checks":25,
        "quadratic_isolator_coefficients":[[str(z) for z in row] for row in isolates],
        "witness_minor_columns":list(minor),"witness_minor_det":str(delta),
        "nontransitive_circular_five":True,
        "six_circle_quadratic_rank":5,"six_rational_circle_tensor_valid":True,
        "six_point_rank_failure_does_not_prove_nonramsey":True,
        "five_collinear_quadratic_rank":3,
        "subsets_of_10_tested":count,"subset_evaluations":count*25,
        "extension_cases":extension,"zero_radius_singleton_is_trivially_ramsey":True,
        "rational_tensor_matrix":[[str(z) for z in row] for row in rational_tensor(center,radius)],
        "selected_full_theorem_status":"SEPARATE_PINNED_LEAN_COMPARATOR",
        "other_family_172_targets_claimed":False,
        "additional_whole_family_validation":0,
        "independent_external_certification":"DEFERRED",
        "limitations":["finite computation cannot prove arbitrary real-input or arbitrary-color theorem",
                       "six-row dependence is not a non-Ramsey counterexample",
                       "rational tensor shortcut does not extend to arbitrary irrational coordinates"]
    }
if __name__=="__main__":
    cli=argparse.ArgumentParser();cli.add_argument("--output",type=Path)
    args=cli.parse_args();report=research()
    txt=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(txt,encoding="utf-8")
    print(txt)
