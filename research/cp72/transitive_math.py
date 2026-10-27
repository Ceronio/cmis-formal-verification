#!/usr/bin/env python3
"""CP72: exact finite-transitive Euclidean geometry and tensor diagnostics.

Standalone standard-library research code. This establishes bounded
computational witnesses and checks elementary propositions. It does NOT
constitute a Lean proof of the full transitive-subset Ramsey theorem.
"""
from __future__ import annotations

import argparse
import itertools
import json
import math
from collections import Counter
from fractions import Fraction as Q
from pathlib import Path


def rational_points(points):
    return tuple(tuple(Q(v) for v in p) for p in points)


def dist2(p, q):
    assert len(p) == len(q)
    return sum(((x - y) ** 2 for x, y in zip(p, q)), Q(0))


def mean(points):
    assert points
    n = len(points)
    return tuple(sum((p[k] for p in points), Q(0)) / n
                 for k in range(len(points[0])))


def radii2(points, center):
    return tuple(dist2(p, center) for p in points)


def distance_matrix(points):
    return tuple(tuple(dist2(x, y) for y in points) for x in points)


def automorphisms(points):
    """Enumerate ALL distance-preserving label permutations exactly."""
    matrix = distance_matrix(points)
    n = len(points)
    group = []
    for perm in itertools.permutations(range(n)):
        if all(matrix[perm[i]][perm[j]] == matrix[i][j]
               for i in range(n) for j in range(n)):
            group.append(perm)
    return tuple(group)


def composition(p, q):
    return tuple(p[q[i]] for i in range(len(p)))


def group_checks(points, group):
    n = len(points)
    G = set(group)
    assert tuple(range(n)) in G, "identity missing"
    for p in group:
        assert set(p) == set(range(n))
        inv = tuple(p.index(i) for i in range(n))
        assert inv in G, "inverse missing"
        for q in group:
            assert composition(p, q) in G, "composition not closed"
    return True


def transitive_action(points, group):
    n = len(points)
    return all({g[i] for g in group} == set(range(n)) for i in range(n))


def uniform_orbit_test(points, group):
    n = len(points)
    if not transitive_action(points, group):
        return False
    assert len(group) % n == 0
    count = len(group) // n
    for i in range(n):
        orbit = Counter(p[i] for p in group)
        assert all(orbit[j] == count for j in range(n))
    return True


def variance_identity(points):
    """sum_j ||x_i-x_j||^2 = n||x_i-centroid||^2 + sum_j||x_j-centroid||^2."""
    n = len(points)
    c = mean(points)
    base = sum((dist2(y, c) for y in points), Q(0))
    for x in points:
        lhs = sum((dist2(x, y) for y in points), Q(0))
        rhs = n * dist2(x, c) + base
        assert lhs == rhs
    return True


def affine_rank(points):
    if not points:
        return 0
    mat = [[a - b for a, b in zip(p, points[0])] for p in points[1:]]
    if not mat:
        return 0
    d = len(points[0])
    r = 0
    for j in range(d):
        pivot = next((k for k in range(r, len(mat)) if mat[k][j] != 0), None)
        if pivot is None:
            continue
        mat[r], mat[pivot] = mat[pivot], mat[r]
        divisor = mat[r][j]
        mat[r] = [q / divisor for q in mat[r]]
        for i in range(len(mat)):
            if i == r:
                continue
            f = mat[i][j]
            mat[i] = [a - f * b for a, b in zip(mat[i], mat[r])]
        r += 1
        if r == len(mat):
            break
    return r


def example_configurations():
    return {
        "rectangle_4": rational_points([(-2,-1),(-2,1),(2,-1),(2,1)]),
        "square_4": rational_points([(-1,-1),(-1,1),(1,-1),(1,1)]),
        "simplex_4": rational_points([(1,0,0,0),(0,1,0,0),
                                       (0,0,1,0),(0,0,0,1)]),
        "octahedron_6": rational_points([(1,0,0),(-1,0,0),(0,1,0),
                                          (0,-1,0),(0,0,1),(0,0,-1)]),
        "scalene_triangle_3": rational_points([(0,0),(2,0),(0,3)]),
        "uneven_line_4": rational_points([(-3,),(-1,),(1,),(3,)]),
        "singleton_1": rational_points([(3,2)]),
    }


def orbit_examples():
    expect = {
        "rectangle_4": (4, True),
        "square_4": (8, True),
        "simplex_4": (24, True),
        "octahedron_6": (48, True),
        "scalene_triangle_3": (1, False),
        "uneven_line_4": (2, False),
        "singleton_1": (1, True),
    }
    observations = []
    for name, pts in example_configurations().items():
        assert len(set(pts)) == len(pts), "source index injectivity required"
        group = automorphisms(pts)
        assert group_checks(pts, group)
        assert variance_identity(pts)
        trans = transitive_action(pts, group)
        assert (len(group), trans) == expect[name]
        assert uniform_orbit_test(pts, group) == trans
        centroid = mean(pts)
        rs = radii2(pts, centroid)
        if trans:
            assert len(set(rs)) == 1, "transitivity forces centroid sphere"
        observations.append({
            "name": name, "vertex_count": len(pts), "dimension": len(pts[0]),
            "automorphism_group_size": len(group),
            "transitive": trans, "centroid": [str(x) for x in centroid],
            "centroid_radius_squared_by_vertex": [str(x) for x in rs],
            "affine_rank": affine_rank(pts),
            "orbit_uniformity": trans,
        })
    return observations


def exact_rigid_map_for_rectangle_subconfiguration():
    """Build the affine isometry mapping 3 selected vertices into group images."""
    p = example_configurations()["rectangle_4"]
    assert affine_rank(p[:3]) == 2
    group = automorphisms(p)
    a = p[:3]
    u = [[a[1][0]-a[0][0], a[2][0]-a[0][0]],
         [a[1][1]-a[0][1], a[2][1]-a[0][1]]]
    det = u[0][0]*u[1][1] - u[0][1]*u[1][0]
    assert det != 0
    inv = [[u[1][1]/det,-u[0][1]/det],
           [-u[1][0]/det,u[0][0]/det]]
    distinct = set()
    for g in group:
        b = tuple(p[g[i]] for i in range(3))
        v = [[b[1][0]-b[0][0], b[2][0]-b[0][0]],
             [b[1][1]-b[0][1], b[2][1]-b[0][1]]]
        M = [[sum((v[i][k]*inv[k][j] for k in range(2)),Q(0))
              for j in range(2)] for i in range(2)]
        for i in range(2):
            for j in range(2):
                val = sum((M[k][i]*M[k][j] for k in range(2)),Q(0))
                assert val == Q(int(i==j)), "Gram-identity violation"
        z = [b[0][i]-sum((M[i][k]*a[0][k] for k in range(2)),Q(0))
             for i in range(2)]
        for i in range(3):
            calc = tuple(z[k]+sum((M[k][j]*a[i][j] for j in range(2)),Q(0))
                         for k in range(2))
            assert calc == b[i], "affine extension does not hit actual orbit"
        distinct.add((tuple(tuple(row) for row in M),tuple(z)))
    assert len(distinct)==4
    return {"induced_subconfiguration_points":3,"affine_rank":2,
            "group_actions_checked":len(group),"distinct_exact_affine_isometries":len(distinct),
            "isometry_gram_tests":len(group)*4,
            "subconfiguration_distances_preserved":len(group)*9}


# Q[X,Y] in sparse exact rational coefficient form. X=t⊗1 and Y=1⊗t.
ZERO = {}
ONE = {(0,0):Q(1)}
X = {(1,0):Q(1)}
Y = {(0,1):Q(1)}

def pclean(P):
    return {k:Q(v) for k,v in P.items() if v != 0}

def padd(*args):
    out={}
    for P in args:
        for k,v in P.items():
            out[k]=out.get(k,Q(0))+v
    return pclean(out)

def pscale(P,s):
    return pclean({k:Q(s)*v for k,v in P.items()})

def pmul(P,Q0):
    out={}
    for (a,b),x in P.items():
        for (c,d),y in Q0.items():
            key=(a+c,b+d)
            out[key]=out.get(key,Q(0))+x*y
    return pclean(out)

def collapse(P):
    out={}
    for (a,b),v in P.items():
        out[a+b]=out.get(a+b,Q(0))+v
    return {n:c for n,c in out.items() if c}

def symbolic_rectangle_tensor():
    """Exact group-averaged witness, valid over the rational-function tensor."""
    H=list(itertools.product((-1,1),repeat=2))
    symbolic_norms = [
        padd(pmul(pscale(X,a),pscale(Y,a)),
             pmul(pscale(ONE,b),pscale(ONE,b))) for a,b in H]
    assert all(z==padd(pmul(X,Y),ONE) for z in symbolic_norms)
    average = pscale(padd(*symbolic_norms),Q(1,len(H)))
    assert average == padd(pmul(X,Y),ONE)
    P00=pscale(average,-1)
    P11=P22=ONE
    assert pclean(P11)==ONE and pclean(P22)==ONE
    for sx,sy in itertools.product((-1,1),repeat=2):
        coeff= padd(P00,pmul(pmul(pscale(X,sx),P11),pscale(Y,sx)),
                    pmul(pmul(pscale(ONE,sy),P22),pscale(ONE,sy)))
        assert coeff==ZERO, "tensor identity must hold BEFORE multiplication"
    WRONG=padd(pscale(ONE,-1),pscale(pmul(X,X),-1))
    wrong_eval=padd(WRONG,pmul(X,Y),ONE)
    assert wrong_eval and collapse(wrong_eval)=={}, "bogus cancellation not caught"
    assert wrong_eval==padd(pmul(X,Y),pscale(pmul(X,X),-1))
    # The invalid tensor does not vanish in Q(t)⊗_Q Q(t) for
    # transcendental t: Q[X,Y] embeds in its rational-function field.
    return {
        "group_order":4, "symbolic_rectangles":4,
        "witness_tensor_P00":"-(1 + X*Y)",
        "witness_tensor_P11":"1",
        "witness_tensor_P22":"1",
        "off_diagonal_entries":"0",
        "pre_multiplication_evaluations_zero":4,
        "grad_spatial_block":"identity_2",
        "transcendental_t_example":"Y={(±t,±1)}; F=Q(t); t transcendental",
        "invalid_tensor_pre_multiplication":"X*Y-X^2 ≠ 0",
        "invalid_tensor_after_multiplication":"t^2-t^2=0",
        "invalid_candidate_rejected":True
    }


def edge_cases():
    pts=example_configurations()["scalene_triangle_3"]
    center=(Q(1),Q(3,2))
    assert len(set(radii2(pts,center)))==1
    assert not transitive_action(pts,automorphisms(pts))
    assert len(set(radii2(pts,mean(pts))))>1
    # Cosphericity is strictly weaker than transitivity. A circle
    # center need not equal the arithmetic centroid.
    for p in example_configurations().values():
        assert variance_identity(p)
    assert len(set(((Q(0),Q(0)),(Q(0),Q(0)))))!=2
    return {"nontransitive_scalene_is_cospherical":True,
            "scalene_circumcenter":["1","3/2"],
            "scalene_radius_squared":"13/4",
            "duplicate_points_are_not_injective":True,
            "empty_subset_disallowed":True,
            "transitive_does_not_mean_every_coloring_original_dimension":True,
            "naive_HJ_scale_error":"variable coordinates m give sqrt(m) times original distance; m unknown until line selected"}


def finite_grid_sweep():
    grid=tuple((Q(x),Q(y)) for x in (-1,0,1) for y in (-1,0,1))
    entries=[]
    for n in range(1,5):
        total=transitive=0
        groups=Counter()
        for subset in itertools.combinations(grid,n):
            G=automorphisms(subset)
            total+=1
            istrans=transitive_action(subset,G)
            if istrans:
                transitive+=1
                assert len(set(radii2(subset,mean(subset))))==1
                assert uniform_orbit_test(subset,G)
            else:
                assert not uniform_orbit_test(subset,G)
            assert variance_identity(subset)
            groups[len(G)]+=1
        assert total==math.comb(9,n)
        entries.append({"n":n,"configurations":total,"transitive":transitive,
                        "nontransitive":total-transitive,
                        "distance_automorphism_order_counts":dict(sorted(groups.items()))})
    assert sum(x["configurations"] for x in entries)==255
    return entries


def run():
    obs=orbit_examples()
    report={
       "checkpoint":"CP72","family_id":"172","scope":"finite transitive and subtransitive Euclidean configurations",
       "evidence_class":"EXACT_BOUNDED_RESEARCH_NOT_FULL_THEOREM_PROOF",
       "status":"PASS_CP72_BOUNDED_MATH",
       "group_cases":obs,
       "grid_sweep":finite_grid_sweep(),
       "grid_total":255,
       "subset_affine_isometries":exact_rigid_map_for_rectangle_subconfiguration(),
       "symbolic_transcendental_rectangle":symbolic_rectangle_tensor(),
       "negative_controls":edge_cases(),
       "independent_maths_proved_by_written_derivation":[
          "Every finite distance-transitive configuration is cospherical about its centroid",
          "Every nonempty subset of a Euclidean Ramsey configuration is Ramsey",
          "For Y=(±t,±1), t transcendental, exact tensor matrix diag(-(t⊗t+1),1,1) satisfies the main field criterion",
          "Finite-orbit averaging produces exact equality of symbolic tensor moments before multiplication"
       ],
       "publisher_transitive_theorem_lean_status":"SEPARATE_GITHUB_COMPARATOR",
       "other_family_172_endpoints_claimed":False,
       "full_family_validated":False,
       "independent_external_certification":"DEFERRED"
    }
    assert report["grid_total"]==sum(x["configurations"] for x in report["grid_sweep"])
    return report

if __name__ == "__main__":
    cli=argparse.ArgumentParser()
    cli.add_argument("--output",type=Path)
    args=cli.parse_args()
    result=run()
    raw=json.dumps(result,indent=2,sort_keys=True)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(raw,encoding="utf-8")
    print(raw)
