#!/usr/bin/env python3
"""CP73 35 adversarial exact mathematical unit tests; not a universal proof."""
import itertools,math,unittest
from fractions import Fraction as Q
import circle_math as m
class IndependentCP73Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.res=m.research();cls.c=(Q(2,3),Q(-3,4));cls.r=Q(5,2)
        cls.P=tuple(m.stereo(t,cls.c,cls.r) for t in (-3,-2,-1,0,2))
        cls.I=m.isolate_five(cls.P)
    def test_01_no_new_family_credit(self):
        self.assertEqual(self.res["additional_whole_family_validation"],0)
        self.assertEqual(self.res["selected_full_theorem_status"],"SEPARATE_PINNED_LEAN_COMPARATOR")
    def test_02_five_unique_nodes(self):self.assertEqual(len(set(self.P)),5)
    def test_03_circle_radius_exact(self):self.assertEqual({m.distance_squared(p,self.c) for p in self.P},{self.r**2})
    def test_04_no_three_collinear(self):self.assertTrue(m.no_three_collinear(self.P))
    def test_05_delta_interpolators(self):
        self.assertEqual([[m.peval(self.I[i],self.P[j]) for j in range(5)] for i in range(5)],
                         [[Q(int(i==j)) for j in range(5)] for i in range(5)])
    def test_06_row_rank_five(self):self.assertEqual(m.rank(m.eval_rows(self.P)),5)
    def test_07_minor_det_nonzero(self):self.assertNotEqual(Q(self.res["witness_minor_det"]),0)
    def test_08_minor_recomputes(self):
        cols=self.res["witness_minor_columns"]
        A=[[row[i] for i in cols] for row in m.eval_rows(self.P)]
        self.assertEqual(str(m.det(A)),self.res["witness_minor_det"])
    def test_09_six_circle_rank_five(self):
        self.assertEqual(m.rank(m.eval_rows(self.P+(m.stereo(3,self.c,self.r),))),5)
    def test_10_seven_circle_rank_five(self):
        self.assertEqual(m.rank(m.eval_rows(self.P+(m.stereo(3,self.c,self.r),m.stereo(4,self.c,self.r)))),5)
    def test_11_six_row_dependence_does_not_prove_nonramsey(self):
        self.assertTrue(self.res["six_rational_circle_tensor_valid"])
        self.assertTrue(self.res["six_point_rank_failure_does_not_prove_nonramsey"])
    def test_12_five_collinear_rank_three(self):
        self.assertEqual(m.rank(m.eval_rows([(Q(i),Q(0)) for i in range(5)])),3)
    def test_13_five_collinear_interpolation_fails(self):
        with self.assertRaises(AssertionError):m.isolate_five([(Q(i),Q(0)) for i in range(5)])
    def test_14_duplicate_nodes_rejected(self):
        with self.assertRaises(AssertionError):m.isolate_five(self.P[:4]+(self.P[2],))
    def test_15_valid_rational_tensor_five(self):m.verify_tensor(self.P,self.c,self.r)
    def test_16_valid_rational_tensor_six(self):m.verify_tensor(self.P+(m.stereo(3,self.c,self.r),),self.c,self.r)
    def test_17_invalid_tensor_constant_rejected(self):
        A=[list(row) for row in m.rational_tensor(self.c,self.r)]
        A[0][0]+=1;v=(Q(1),)+self.P[0]
        self.assertEqual(sum((v[i]*A[i][j]*v[j] for i in range(3) for j in range(3)),Q(0)),1)
    def test_18_spatial_identity(self):
        P=m.rational_tensor(self.c,self.r)
        self.assertEqual([P[1][1],P[1][2],P[2][1],P[2][2]],[1,0,0,1])
    def test_19_wrong_dilation_changes_original_distance(self):
        a,b=self.P[:2]
        self.assertEqual(m.distance_squared((2*a[0],2*a[1]),(2*b[0],2*b[1])),4*m.distance_squared(a,b))
    def test_20_irregular_circular_set_not_transitive(self):
        self.assertEqual(m.distance_automorphisms(self.P),(1,False))
    def test_21_sweep_subsets(self):self.assertEqual(self.res["subsets_of_10_tested"],252)
    def test_22_sweep_kronecker_cells(self):self.assertEqual(self.res["subset_evaluations"],6300)
    def test_23_stereographic_parameter_recovery(self):
        x,y=m.stereo(Q(2,7))
        self.assertEqual(y/(1+x),Q(2,7))
    def test_24_stereographic_circle_identity(self):
        for t in (-9,-3,-1,0,1,2,5,12):
            self.assertEqual(m.distance_squared(m.stereo(t),(Q(0),Q(0))),1)
    def test_25_secant_through_endpoints(self):
        for a,b in itertools.combinations(self.P,2):
            L=m.secant(a,b)
            self.assertEqual(m.secant_eval(L,a),0)
            self.assertEqual(m.secant_eval(L,b),0)
    def test_26_third_circle_point_never_on_secant(self):
        for a,b,c in itertools.combinations(self.P,3):
            self.assertNotEqual(m.secant_eval(m.secant(a,b),c),0)
    def test_27_zero_radius_singleton(self):self.assertTrue(self.res["zero_radius_singleton_is_trivially_ramsey"])
    def test_28_extensions_all_sizes(self):
        self.assertEqual(len(self.res["extension_cases"]),5)
        self.assertEqual(sum(x["new_points"] for x in self.res["extension_cases"].values()),10)
    def test_29_more_points_row_rank_no_more_than_five(self):
        self.assertEqual(m.rank(m.eval_rows([m.stereo(t) for t in range(7)])),5)
        self.assertEqual(self.res["additional_whole_family_validation"],0)
    def test_30_rank_zero_empty(self):self.assertEqual(m.rank([]),0)
    def test_31_affine_span_three_circle_nodes(self):self.assertNotEqual(m.area2(*self.P[:3]),0)
    def test_32_singular_matrix_det_zero(self):self.assertEqual(m.det([[1,2],[2,4]]),0)
    def test_33_tensor_radius_changes_constant(self):
        self.assertNotEqual(m.rational_tensor((Q(0),Q(0)),1),m.rational_tensor((Q(0),Q(0)),2))
    def test_34_bad_nonsymmetric_tensor_changes_evaluation(self):
        P=[list(row) for row in m.rational_tensor(self.c,self.r)]
        P[0][1]+=1
        v=(Q(1),)+self.P[0]
        self.assertNotEqual(sum((v[i]*P[i][j]*v[j] for i in range(3) for j in range(3)),Q(0)),0)
    def test_35_deterministic_replay(self):self.assertEqual(m.research(),self.res)
if __name__=="__main__":unittest.main(verbosity=2)
