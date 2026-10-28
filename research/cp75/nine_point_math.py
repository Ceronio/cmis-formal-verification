#!/usr/bin/env python3
"""CMIS CP75 exact finite specialization of nine-parameter tensor obstruction.

Independent stdlib implementation; rational grid specializations do not themselves
satisfy algebraic independence. Universal theorem is checked SEPARATELY via the
original pinned Lean/Comparator workflow and not inferred from these tests.
"""
from __future__ import annotations
import argparse, itertools, json, random
from fractions import Fraction as F
from pathlib import Path

GRID=(F(0), F(1), F(-1))
INDEX=tuple(itertools.product(range(3),repeat=2))

def q(t):
    t=F(t)
    return (1+t*t,1-t*t,2*t)

def p(t):
    v=q(t); return tuple(F(z, v[0]) if isinstance(z,int) else z/v[0] for z in v)

def kronecker(A,B):
    return tuple(tuple(x*y for x in row_a for y in row_b) for row_a in A for row_b in B)

def matrank(A):
    A=[list(map(F,row)) for row in A]
    if not A:return 0
    n=len(A);m=len(A[0]);assert all(len(row)==m for row in A)
    r=0
    for col in range(m):
        piv=next((i for i in range(r,n) if A[i][col]),None)
        if piv is None:continue
        A[r],A[piv]=A[piv],A[r]
        div=A[r][col];A[r]=[v/div for v in A[r]]
        for i in range(n):
            if i!=r:
                coef=A[i][col]
                A[i]=[a-coef*b for a,b in zip(A[i],A[r])]
        r+=1
        if r==n:break
    return r

def det(A):
    """Exact rational elimination determinant independent of a symbolic package."""
    A=[list(map(F,row)) for row in A]
    n=len(A)
    assert all(len(row)==n for row in A)
    value=F(1)
    for i in range(n):
        k=next((k for k in range(i,n) if A[k][i]),None)
        if k is None:return F(0)
        if k!=i:A[k],A[i]=A[i],A[k];value=-value
        pivot=A[i][i];value*=pivot
        for j in range(i+1,n):
            r=A[j][i]/pivot
            for k in range(i+1,n):A[j][k]-=r*A[i][k]
            A[j][i]=F(0)
    return value

def grid_matrix(clear=False):
    c=q if clear else p
    return tuple(tuple(c(GRID[i])[a]*c(GRID[j])[b] for (a,b) in INDEX)
                 for (i,j) in INDEX)

def C(clear=False):
    return tuple((q(t) if clear else p(t)) for t in GRID)

def denominator_product():
    v=F(1)
    for i,j in INDEX:v*=(1+GRID[i]**2)*(1+GRID[j]**2)
    return v

def circle_param(t):
    return p(t)[1:]

def rational_circle_geometry(values):
    points=[circle_param(t) for t in values]
    assert len(set(points))==len(points)
    for x,y in points:assert x*x+y*y==1
    assert len(set(values))==len(values)
    for t,(x,y) in zip(values,points):
        assert y/(1+x)==t, 'Stereographic recovery must hold for each sample'
    return points

def independent_grid_proof():
    A=C(False);B=C(True);M=grid_matrix(False);E=grid_matrix(True)
    assert A==((F(1),F(1),F(0)),(F(1),F(0),F(1)),(F(1),F(0),F(-1)))
    assert B==((F(1),F(1),F(0)),(F(2),F(0),F(2)),(F(2),F(0),F(-2)))
    assert M==kronecker(A,A)
    assert E==kronecker(B,B)
    detA=det(A);detB=det(B)
    detM=det(M);detE=det(E)
    denom=denominator_product()
    assert detA==2 and detB==8
    assert detM==64 and detE==8**6==262144
    assert denom==4096 and detE==denom*detM
    assert matrank(M)==9 and matrank(E)==9
    rows=[]
    for (a,b),rawrow,numerrow in zip(INDEX,M,E):
        fac=(1+GRID[a]**2)*(1+GRID[b]**2)
        assert all(fac*x==y for x,y in zip(rawrow,numerrow))
        rows.append({'index':[a,b],'T_grid':str(GRID[a]),'U_grid':str(GRID[b]),
                     'row_denominator':str(fac),'rational_row':[str(x) for x in rawrow],
                     'cleared_row':[str(x) for x in numerrow]})
    return {'C_rational':[[str(x) for x in row] for row in A],
            'C_cleared':[[str(x) for x in row] for row in B],
            'det_C_rational':str(detA),'det_C_cleared':str(detB),
            'Kronecker_rational_det':str(detM),
            'Kronecker_cleared_det':str(detE),
            'denominator_product':str(denom),'all_evaluation_rows':rows}

def random_separate_axes(samples=56):
    rng=random.Random(17275)
    good=0;bad=0;zero=0;first=[]
    # Independent assignments of (T_i,U_i) used only to evaluate the
    # generic 18-variable rational determinant. They are not witnesses
    # satisfying the theorem's algebraic independence hypothesis.
    space=[F(-3),F(-2),F(-1),F(0),F(1),F(2),F(3)]
    for z in range(samples):
        pairs=[(rng.choice(space),rng.choice(space)) for _ in range(9)]
        matrix=[tuple(a*b for a,b in itertools.product(p(t),p(u))) for t,u in pairs]
        determinant=det(matrix)
        if determinant:good+=1
        else:zero+=1
        if z<6:first.append({'pairs':[[str(a),str(b)] for a,b in pairs],
                             'determinant':str(determinant)})
    assert good>0 and good+zero==samples
    return {'sample_assignments':samples,'nonzero':good,'zero':zero,
            'interpretation':'Rational polynomial SPECIALIZATIONS only; not 9 algebraically independent real parameters',
            'first_examples':first}

def diagonal_negative_control():
    vals=tuple(map(F,(-4,-3,-2,-1,0,1,2,3,4)))
    rational_circle_geometry(vals)
    rows=[tuple(a*b for a,b in itertools.product(p(t),p(t))) for t in vals]
    r=matrank(rows)
    assert r==5 and det(rows)==0
    # These nine *rational* points on the unit circle satisfy the
    # CP71 tensor criterion with P=diag(-1,1,1) over Q⊗_Q Q.
    P=((F(-1),F(0),F(0)),(F(0),F(1),F(0)),(F(0),F(0),F(1)))
    for t in vals:
        v=p(t)
        assert sum((v[i]*P[i][j]*v[j] for i in range(3) for j in range(3)),F(0))==0
    return {'nine_rational_points_rank':r,'diagonal_determinant':'0',
            'rational_field_tensor_certificate':'P=diag(-1,1,1) in Q tensor Q',
            'rational_example_is_not_nonRamsey':True,
            'algebraic_independence_not_met':True,
            'tensor_spatial_block':'I2'}

def altered_grid_controls():
    base=grid_matrix(False)
    assert det(base)==64
    change=[list(row) for row in base]
    change[1]=change[0][:]
    assert det(change)==0
    # Reversing one column has determinant -64, not zero.
    perm=[tuple(row[1] if j==0 else row[0] if j==1 else row[j] for j in range(9)) for row in base]
    assert det(perm)==-64
    # Numerator clearance is essential; it changes scale but not nonvanishing.
    assert det(grid_matrix(True))!=64
    # Avoid accidental claim that setting T_i=U_i tests a generic tensor.
    assert diagonal_negative_control()['diagonal_determinant']=='0'
    return {'duplicate_row_determinant':'0','column_swap_determinant':'-64',
            'incorrect_256k_equals_64_rejected':True,
            'diagonal_specialization_singular':True}

def run():
    grid=independent_grid_proof()
    return {'checkpoint':'CP75','family_id':172,
      'theorem':'OAI.EuclideanRamsey.NineStatement.nine_circle_configuration',
      'status':'PASS_CP75_EXACT_BOUNDED_AND_SYMBOLIC_SPECIALIZATION',
      'original_hypothesis':'Nine algebraically independent real parameters over Q',
      'core_exact_result':'9x9 polynomial determinant is nonzero: evaluation at grid has 8^6=262144; rational determinant 64',
      'grid':grid,'random_rational_specializations':random_separate_axes(),
      'diagonal_negative_control':diagonal_negative_control(),
      'altered_grid_controls':altered_grid_controls(),
      'formal_selected_theorem':'SEPARATE_GITHUB_LEAN_COMPARATOR',
      'independent_external_certification':'DEFERRED',
      'whole_family_172_validated':False,'additional_whole_family_credit':0,
      'limits':['Finite rational values do not instantiate algebraic independence',
                'Nonzero polynomial specialization proves generic determinant is nonzero, not all specializations',
                'Nine rational points on a circle can be Ramsey via a rational tensor certificate',
                'Proof depends on faithful tensor-field embedding and CP71 necessity direction',
                'No selected theorem has been credited solely by this computation']}

if __name__=='__main__':
    cli=argparse.ArgumentParser();cli.add_argument('--output',type=Path)
    args=cli.parse_args();data=json.dumps(run(),indent=2,sort_keys=True)+'\n'
    if args.output:args.output.parent.mkdir(parents=True,exist_ok=True);args.output.write_text(data)
    print(data)
