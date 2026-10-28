#!/usr/bin/env python3
"""CP74: exact 12-point spherical witness, polynomial identities, and floor-color obstruction.

All claimed identities are tested over Z[t] without numerical tolerances.
This executable is NOT a formal Lean proof of the source's universal result.
The proposed 16-color sharpening has a conventional proof in the
mathematical note; it has NOT been independently Lean-certified.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
import random
from fractions import Fraction as F
from pathlib import Path

P = tuple[int, ...]
D = (1, 0, 1)              # 1 + t^2
U = (1, 0, -1)             # 1 - t^2
V = (0, 2)                 # 2 t
BASE = ((1,0),(-1,0),(0,1),(0,-1))
WEIGHTS = (1,)*8+(-2,)*4
assert len(WEIGHTS)==12 and sum(WEIGHTS)==0 and sum(map(abs,WEIGHTS))==16


def normalize(p):
    a=list(p)
    while len(a)>1 and a[-1]==0:
        a.pop()
    return tuple(a) if a else (0,)


def add(*args):
    n=max((len(p) for p in args),default=1)
    return normalize(tuple(sum((p[i] if i<len(p) else 0 for p in args)) for i in range(n)))


def neg(p):
    return tuple(-a for a in p)


def sub(a,b):
    return add(a,neg(b))


def scale(p,k):
    return normalize(tuple(k*a for a in p))


def mul(a,b):
    out=[0]*(len(a)+len(b)-1)
    for i,x in enumerate(a):
        for j,y in enumerate(b):
            out[i+j]+=x*y
    return normalize(out)


def derive(p):
    return normalize(tuple(i*p[i] for i in range(1,len(p))))


def eval_poly(p,x):
    return sum((F(a)*x**i for i,a in enumerate(p)),F(0))


def poly_zero(p):
    return normalize(p)==(0,)


def coordinates_polynomials():
    """Each coordinate is numerator(t)/D(t); each derivative under δ is likewise."""
    witness=[]
    for group in (0,1,2):
        for qx,qy in BASE:
            if group==0:   # +theta rotated
                X=sub(scale(U,qx),scale(V,qy))
                Y=add(scale(V,qx),scale(U,qy))
                DX=sub(scale(neg(V),qx),scale(U,qy))
                DY=sub(scale(U,qx),scale(V,qy))
            elif group==1: # -theta rotated
                X=add(scale(U,qx),scale(V,qy))
                Y=add(scale(neg(V),qx),scale(U,qy))
                DX=add(scale(neg(V),qx),scale(U,qy))
                DY=add(scale(neg(U),qx),scale(neg(V),qy))
            else:
                X=scale(D,qx);Y=scale(D,qy)
                DX=(0,);DY=(0,)
            witness.append({
              "group":group,"square_label":[qx,qy],"weight":WEIGHTS[len(witness)],
              "numerators":[D,X,Y],"derivative_numerators":[(0,),DX,DY]
            })
    assert len(witness)==12
    return witness


def matrix_moments():
    """
    Check M0=Σβ p pT=0, M1=Σβ (δp)pT=0,
    M2=Σβ (δp)(δp)T=diag(0,4,4), with common denominator D^2.
    """
    w=coordinates_polynomials()
    matrices=[]
    for kind in (0,1,2):
        matrix=[]
        for i in range(3):
            row=[]
            for j in range(3):
                terms=[]
                for item in w:
                    A=(item["derivative_numerators"] if kind in (1,2) else item["numerators"])
                    B=(item["derivative_numerators"] if kind==2 else item["numerators"])
                    terms.append(scale(mul(A[i],B[j]),item["weight"]))
                row.append(add(*terms))
            matrix.append(row)
        matrices.append(matrix)
    expected0=[[(0,) for _ in range(3)] for _ in range(3)]
    target=[[scale(mul(D,D),4*int(i==j and i>0)) for j in range(3)]
            for i in range(3)]
    assert matrices[0]==expected0
    assert matrices[1]==expected0
    assert matrices[2]==target
    return matrices


def derivative_identites():
    """δ=((1+t²)/2)d/dt; prove δu=-v, δv=u by polynomial cross-multiplication."""
    # δ(N/D)=(N'D-ND')/(2D)
    left_u=sub(mul(derive(U),D),mul(U,derive(D)))
    left_v=sub(mul(derive(V),D),mul(V,derive(D)))
    assert add(left_u,scale(V,2))==(0,)
    assert sub(left_v,scale(U,2))==(0,)
    assert add(mul(U,U),mul(V,V))==mul(D,D)
    return {"delta_u_equals_negative_v":True,"delta_v_equals_u":True,
            "rotation_norm_identity":True}


def actual_points(t):
    assert isinstance(t,F) and t>0
    den=eval_poly(D,t)
    return tuple((eval_poly(item["numerators"][1],t)/den,
                  eval_poly(item["numerators"][2],t)/den)
                 for item in coordinates_polynomials())


def exact_sample(t):
    points=actual_points(t)
    u=eval_poly(U,t)/eval_poly(D,t)
    v=eval_poly(V,t)/eval_poly(D,t)
    assert 0<v<u<1
    assert len(points)==12 and len(set(points))==12
    assert all(x*x+y*y==1 for x,y in points)
    assert sum(WEIGHTS)==0
    # All three blocks individually sum to zero and have Σqq^T=2I.
    blocks=[points[k:k+4] for k in (0,4,8)]
    assert all(sum((p[j] for p in block),F(0))==0 for block in blocks for j in range(2))
    assert all(sum((p[i]*p[j] for p in block),F(0))==2*int(i==j)
               for block in blocks for i in range(2) for j in range(2))
    return {"t":str(t),"u":str(u),"v":str(v),
            "point_count":12,"unit_norm_points":12,
            "all_unique":True,"signed_weights_sum":0}


def signed_floor_sum(energies, multiplier=1):
    assert len(energies)==12 and multiplier>=1
    return sum(w*math.floor(multiplier*e) for w,e in zip(WEIGHTS,energies))


def colors(energies,multiplier,modulus):
    return tuple(math.floor(multiplier*e)%modulus for e in energies)


def test_floor_obstruction(samples=900):
    """Rational energy samples meeting Σβ e=8; check both source 50 and optional 16."""
    rnd=random.Random(20261028)
    recorded=[]
    for n in range(samples):
        while True:
            e=[F(rnd.randint(2,160),rnd.randint(2,13)) for _ in range(11)]
            val=(sum(e[:8],F(0))-2*sum(e[8:11],F(0))-8)/2
            if val>=0:
                break
        e.append(val)
        assert all(x>=0 for x in e)
        assert sum((w*x for w,x in zip(WEIGHTS,e)),F(0))==8
        S16=signed_floor_sum(e,1)
        S50=signed_floor_sum(e,3)
        assert 0<S16<16
        assert 16<S50<32
        assert S16%16!=0 and S50%50!=0
        assert len(set(colors(e,1,16)))>1
        assert len(set(colors(e,3,50)))>1
        if n<4:
            recorded.append({"weighted_floor_at_1":S16,"weighted_floor_at_3":S50,
                             "16_color_residues":list(colors(e,1,16)),
                             "50_color_residues":list(colors(e,3,50))})
    # Deliberate negative tests: energy invariant is REQUIRED, not optional.
    all_zero=[F(0)]*12
    assert sum((w*e for w,e in zip(WEIGHTS,all_zero)),F(0))==0
    assert len(set(colors(all_zero,1,16)))==1
    return {"samples":samples,"source_50_color_scale":3,
            "source_50_color_modulus":50,
            "derived_16_color_scale":1,
            "derived_16_color_modulus":16,
            "all_samples_obey_energy_identity":True,
            "all_samples_nonnegative":True,
            "all_samples_16_color_not_monochromatic":True,
            "all_samples_50_color_not_monochromatic":True,
            "sample_records":recorded,
            "all_zero_control_requires_invariant":True}


def parameter_bounds():
    # Partial sums of literal t=sum_{k>=1} 10^{-k!}; not the infinite number.
    partial=[]
    value=F(0)
    for k in range(1,5):
        power=math.factorial(k)
        value+=F(1,10**power)
        partial.append({"terms":k,"last_factorial":power,
                        "numerator_digits":len(str(value.numerator)),
                        "denominator_digits":len(str(value.denominator)),
                        "in_0_11_to_0_12":bool(F(11,100)<value<F(12,100))})
    assert partial[-1]["in_0_11_to_0_12"]
    assert partial[1]["in_0_11_to_0_12"] is False # exactly 0.11
    test=F(111,1000)
    exact_sample(test)
    return {"literal_series_first_terms":[1,2,6,24],
            "bounds_from_original_source":"11/100 < t < 12/100",
            "rational_partial_sums":partial,
            "source_transcendence_proof":"pinned Lean/Mathlib, not established by finite partial sums"}


def run():
    deriv=derivative_identites()
    moments=matrix_moments()
    examples=[exact_sample(v) for v in [F(11,100),F(111,1000),F(119,1000),F(1,9)]]
    result={
      "schema_version":"1.0","checkpoint":"CP74","family_id":172,
      "status":"PASS_EXACT_CP74_POLYNOMIAL_AND_FINITE_TESTS",
      "source_full_theorem":"OAI.GrahamSpherical.full_main",
      "theorem_exact_scope":"12 distinct unit-circle points, 50-color avoidance in every positive dimension, not Euclidean Ramsey",
      "witness_groups":3,"vertices_per_group":4,"total_vertices":12,
      "weighted_moment_identities":{"M0":"zero 3x3","M1":"zero 3x3",
         "M2":"diag(0,4,4)","polynomial_identity_checks":27,
         "all_exact_over_Z_t":True},
      "derivation_rational_function":deriv,
      "exact_rational_geometry_examples":examples,
      "factorial_parameter":parameter_bounds(),
      "floor_color_falsification":test_floor_obstruction(),
      "independent_deduction_16_colors":{
        "status":"CONVENTIONAL_PROOF_CONDITIONAL_ON_SOURCE_ENERGY_INVARIANT",
        "claim":"Given the source's universal weighted energy invariant, floor(energy) mod 16 avoids monochromatic isometric copies in all dimensions.",
        "proof_summary":"If 12 colors equal residue mod16, weighted sum of their floors is divisible by16 since weights sum0. But source identity Σw e=8 and floor inequalities force 0<S<16; contradiction.",
        "formal_Lean_kernel":"NOT_RUN","independent_external_peer_review":"NOT_DONE",
        "publisher_original_selected_theorem_is_50_colors":True},
      "full_50_color_avoiding_coloring_computed":False,
      "full_50_color_in_all_dimensions_proved_by_finite_search":False,
      "source_selected_Lean_status":"SEPARATE_PINNED_GITHUB_COMPARATOR",
      "whole_family_172_certified":False,"new_full_family_credit":0,
      "external_certification":"DEFERRED",
      "limitations":[
        "Computed rational t examples are not the transcendental Liouville witness.",
        "Formal transcendence and arbitrary real derivation existence are supplied by pinned source and require Lean verification for their full scope.",
        "Finite energy samples only test the integer floor lemma, not arbitrary dimension real colorings.",
        "16-color conditional corollary requires independent review and separate formalization before formal credit.",
        "No modification of existing CP71-CP73 proofs, main register, CBI or TBC."]
    }
    assert result["weighted_moment_identities"]["polynomial_identity_checks"]==27
    return result

if __name__=="__main__":
    parser=argparse.ArgumentParser()
    parser.add_argument("--output",type=Path)
    args=parser.parse_args()
    result=run()
    blob=json.dumps(result,sort_keys=True,indent=2)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(blob,encoding="utf8")
    print(blob)
