#!/usr/bin/env python3
"""CP71 bounded exact mathematical tests for Family 172.

Run entirely with Python standard library. These checks verify the geometry
and tensor substrate and independent elementary examples. They do NOT prove
OAI.EuclideanRamsey.classification or certify all Euclidean Ramsey sets.
"""
from __future__ import annotations
import argparse
import itertools
import json
import math
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path

# A polynomial over Q[X,Y] is a sparse map (degree_X, degree_Y) -> rational.
# X and Y symbolically represent t⊗1 and 1⊗t. An identity in Q[X,Y]
# specializes to every field-tensor pair. This model is not claimed to be
# a faithful description of F⊗_Q F for algebraic t.
def clean(d):
    return {k: Q(v) for k, v in d.items() if Q(v) != 0}

def plus(*ps):
    out={}
    for p in ps:
        for k,v in p.items():out[k]=out.get(k,Q(0))+Q(v)
    return clean(out)

def neg(p):
    return {k:-v for k,v in p.items()}

def times(a,b):
    out={}
    for (i,j),v in a.items():
        for (k,l),w in b.items():
            t=(i+k,j+l)
            out[t]=out.get(t,Q(0))+v*w
    return clean(out)

ZERO={}
ONE={(0,0):Q(1)}
X={(1,0):Q(1)}
Y={(0,1):Q(1)}

def eval_tensor(witness, point):
    """Exact augmented-row matrix contraction in Q[X,Y]."""
    left=[ONE,point[0]];right=[ONE,point[1]]
    out=ZERO
    for a in range(2):
        for b in range(2):
            out=plus(out,times(times(left[a],witness[a][b]),right[b]))
    return out

GOOD_P=((ZERO,ZERO),(neg(Y),ONE))
BAD_P=((ZERO,ZERO),(neg(X),ONE))

def collapse_multiplication(p):
    """Specialize the formal tensor variables to the same indeterminate."""
    out={}
    for (i,j),v in p.items():
        deg=i+j;out[deg]=out.get(deg,Q(0))+v
    return {k:v for k,v in out.items() if v}

def squared_distance(a,b):
    assert len(a)==len(b)
    return sum(((Q(x)-Q(y))**2 for x,y in zip(a,b)),Q(0))

def affine_rank(points):
    """Row reduction of differences over Q; no floating point."""
    if not points:return 0
    dim=len(points[0])
    rows=[[Q(x)-Q(y) for x,y in zip(row,points[0])] for row in points[1:]]
    rank=0
    for col in range(dim):
        pivot=next((i for i in range(rank,len(rows)) if rows[i][col]),None)
        if pivot is None:continue
        rows[rank],rows[pivot]=rows[pivot],rows[rank]
        val=rows[rank][col]
        rows[rank]=[x/val for x in rows[rank]]
        for i in range(len(rows)):
            if i!=rank:
                factor=rows[i][col]
                rows[i]=[x-factor*y for x,y in zip(rows[i],rows[rank])]
        rank+=1
        if rank==len(rows):break
    return rank

def simplex_test(r):
    """Use r+1 coordinate-axis vertices: squared pair-distance exactly 2."""
    verts=[tuple(Q(int(i==j)) for j in range(r+1)) for i in range(r+1)]
    assert all(squared_distance(verts[i],verts[j])==2
       for i in range(r+1) for j in range(i+1,r+1))
    count=0
    for colouring in itertools.product(range(r),repeat=r+1):
        count+=1
        if len(set(colouring))==r+1:
            raise AssertionError("No equal-colour pair in r+1 slots")
    # Sharpness of this particular pigeonhole bound: at r points,
    # r! injective colorings avoid a same-colour pair.
    without=0
    for colouring in itertools.product(range(r),repeat=r):
        if len(set(colouring))==r:without+=1
    assert count==r**(r+1)
    assert without==math.factorial(r)
    return {"colors":r,"simplex_vertices":r+1,"ambient_dimension":r+1,
            "colorings_checked":count,
            "counterexamples":0,
            "sharpness_avoiding_r_point_colorings":without}

def one_dimensional_countercolour(delta):
    """Exact examples illustrating c(x)=floor(x/delta) mod 2."""
    assert delta>0
    n=0
    for a in range(-30,31):
        for den in (2,3,5,7):
            x=Q(a,den)*delta
            k=(x/delta).__floor__()
            for y in (x+delta,x-delta):
                if k%2==(y/delta).__floor__()%2:
                    raise AssertionError("Periodic 1D obstruction failed")
                n+=1
    return n

def exact_geometric_invariance():
    pts=[(Q(0),Q(0)),(Q(2),Q(0)),(Q(1),Q(3))]
    transformed=[(-p[1]+Q(7,3),p[0]-Q(5,7)) for p in pts]
    checks=0
    for i in range(len(pts)):
        for j in range(len(pts)):
            assert squared_distance(pts[i],pts[j])==squared_distance(transformed[i],transformed[j])
            checks+=1
    scaled=[(2*x,2*y) for x,y in pts]
    rejected=sum(squared_distance(pts[i],pts[j])!=squared_distance(scaled[i],scaled[j])
                 for i in range(len(pts)) for j in range(i+1,len(pts)))
    assert rejected==3, "Scaling by two must NOT preserve original distances"
    assert affine_rank(pts)==2
    assert affine_rank(transformed)==2
    assert affine_rank([(Q(0),Q(0)),(Q(1),Q(0)),(Q(2),Q(0))])==1
    assert affine_rank([(Q(0),Q(0)),(Q(0),Q(0))])==0
    return {"exact_pairwise_checks":checks,"incorrect_scalings_rejected":rejected,
            "plane_rank":2,"collinear_rank":1,"collision_rank":0}

def tensor_checks():
    # For a=(0,t) in affine dimension 1 and formal X=t⊗1,Y=1⊗t:
    # p0=(1,0), p1=(1,t);
    # P00=0, P01=0, P10=-(1⊗t), P11=1⊗1.
    # Both equations hold exactly before applying multiplication.
    good0=eval_tensor(GOOD_P,(ZERO,ZERO))
    good1=eval_tensor(GOOD_P,(X,Y))
    assert good0==ZERO and good1==ZERO
    assert GOOD_P[1][1]==ONE
    bad=eval_tensor(BAD_P,(X,Y))
    assert bad and not collapse_multiplication(bad)
    # Under multiplication B -> F the bogus matrix looks correct
    # but fails before multiplying, exactly the key pitfall.
    a=[]
    for t in [Q(1),Q(2),Q(5,3),Q(-3,4)]:
        for x in (Q(0),t):
            assert x*x-t*x==0
            center=t/2
            assert (x-center)**2==(t/2)**2
        a.append(str(t))
    return {"correct_tensor_evaluations":2,
            "bogus_candidate_rejected_before_multiplication":True,
            "bogus_candidate_passes_after_multiplication":True,
            "spatial_multiplication_identity":True,
            "two_point_spherical_examples":a}

def run():
    simplex=[simplex_test(r) for r in (2,3,4,5)]
    periodic={str(d):one_dimensional_countercolour(d)
              for d in [Q(1),Q(2),Q(5,3)]}
    return {
      "schema_version":"1.0",
      "checkpoint":"CP71",
      "family_id":172,
      "status":"PASS_EXACT_BOUNDED_CP71",
      "mathematical_scope":"Definitions, exact-distance invariants, constructive two-point Ramsey example, 1D obstruction and symbolic tensor witness; NO general classification proof",
      "simplex_pigeonhole":simplex,
      "one_dimensional_alternating_colouring":{"samples":periodic,
        "universal_argument":"floor((x ± delta)/delta) = floor(x/delta) ± 1 for delta>0; parity changes"},
      "exact_geometry":exact_geometric_invariance(),
      "exact_tensor":tensor_checks(),
      "theorem_claims":[
         "For a pair at positive distance delta, the r+1 coordinate-axis simplex in R^(r+1), scaled by delta/sqrt(2), forces equal-colour vertices for any r>=2.",
         "In R^1, alternating half-open intervals of length delta two-colour the line with no monochromatic pair distance delta.",
         "A non-symmetric 2x2 tensor matrix P with P10=-(1⊗t), P11=1 and other entries zero certifies the two-point configuration (0,t), t != 0.",
         "Equalities after applying the tensor multiplication map alone are insufficient for the publisher's criterion."
      ],
      "publisher_classification_lean_kernel":"NOT_RUN",
      "publisher_classification_statement_comparator":"NOT_RUN",
      "family_whole_scope_validated":False,
      "additional_formal_credit":0,
      "independent_external_human_review":"NOT_PERFORMED",
      "research_run_is_not_theorem_certification":True
    }

if __name__ == "__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--output",type=Path)
    args=p.parse_args()
    report=run()
    data=json.dumps(report,sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(data,encoding="utf-8")
    print(data)
