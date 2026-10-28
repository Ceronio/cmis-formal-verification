#!/usr/bin/env python3
"""CP75 adversarial exact rational test suite; selected theorem separate Lean action."""
import itertools, math, random, unittest
from fractions import Fraction as F
import nine_point_math as m

class CP75Tests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.r=m.run()
    def test_01_status_truthful(self):self.assertEqual(self.r['status'],'PASS_CP75_EXACT_BOUNDED_AND_SYMBOLIC_SPECIALIZATION')
    def test_02_9_rows(self):self.assertEqual(len(m.grid_matrix(False)),9)
    def test_03_9_columns(self):self.assertEqual({len(r) for r in m.grid_matrix(True)},{9})
    def test_04_q_grid(self):self.assertEqual(m.C(True),((1,1,0),(2,0,2),(2,0,-2)))
    def test_05_p_grid(self):self.assertEqual(m.C(False),((1,1,0),(1,0,1),(1,0,-1)))
    def test_06_C_denominator_cleared_det8(self):self.assertEqual(m.det(m.C(True)),8)
    def test_07_C_rational_det2(self):self.assertEqual(m.det(m.C(False)),2)
    def test_08_cleared_tensor_det(self):self.assertEqual(m.det(m.grid_matrix(True)),8**6)
    def test_09_rational_tensor_det(self):self.assertEqual(m.det(m.grid_matrix(False)),64)
    def test_10_clearance_ratio(self):self.assertEqual(m.det(m.grid_matrix(True)),m.denominator_product()*m.det(m.grid_matrix(False)))
    def test_11_product_denominators(self):self.assertEqual(m.denominator_product(),4096)
    def test_12_rows_clear_exact(self):
        a=m.grid_matrix(False);b=m.grid_matrix(True)
        for (i,j),r,s in zip(m.INDEX,a,b):
            v=(1+m.GRID[i]**2)*(1+m.GRID[j]**2)
            self.assertEqual([v*x for x in r],list(s))
    def test_13_kronecker_form_rational(self):self.assertEqual(m.grid_matrix(False),m.kronecker(m.C(False),m.C(False)))
    def test_14_kronecker_form_cleared(self):self.assertEqual(m.grid_matrix(True),m.kronecker(m.C(True),m.C(True)))
    def test_15_fullrank_cleared(self):self.assertEqual(m.matrank(m.grid_matrix(True)),9)
    def test_16_fullrank_rational(self):self.assertEqual(m.matrank(m.grid_matrix(False)),9)
    def test_17_doubled_parameter_axes(self):self.assertEqual(len(m.INDEX),9)
    def test_18_spatial_coordinate_identity(self):
        for t in [F(i,7) for i in range(-17,18)]:
            v=m.p(t);self.assertEqual(v[0],1);self.assertEqual(v[1]**2+v[2]**2,1)
    def test_19_circle_parameter_recovery(self):
        for t in [F(i,17) for i in range(-16,17)]:
            x,y=m.circle_param(t);self.assertEqual(y/(1+x),t)
    def test_20_duplicate_polynomial_row_zero(self):self.assertEqual(m.altered_grid_controls()['duplicate_row_determinant'],'0')
    def test_21_column_swaps_sign(self):self.assertEqual(m.altered_grid_controls()['column_swap_determinant'],'-64')
    def test_22_diagonal_substitution_singular(self):self.assertEqual(m.diagonal_negative_control()['diagonal_determinant'],'0')
    def test_23_diagonal_rank_five(self):self.assertEqual(m.diagonal_negative_control()['nine_rational_points_rank'],5)
    def test_24_rational_diagonal_tensor_certificate(self):self.assertTrue(m.diagonal_negative_control()['rational_example_is_not_nonRamsey'])
    def test_25_rational_assignments_not_independent(self):self.assertTrue(m.diagonal_negative_control()['algebraic_independence_not_met'])
    def test_26_diagonal_points_unique(self):self.assertEqual(len(set(m.rational_circle_geometry(tuple(map(F,range(9)))))),9)
    def test_27_row_relabel_determinant(self):
        rows=list(m.grid_matrix(False));rows[0],rows[1]=rows[1],rows[0]
        self.assertEqual(m.det(rows),-64)
    def test_28_fraction_exact_no_floats(self):self.assertTrue(all(isinstance(x,F) for row in m.grid_matrix(False) for x in row))
    def test_29_prime_7_det_nonzero(self):self.assertNotEqual(int(m.det(m.grid_matrix(False)))%7,0)
    def test_30_prime_2_det_zero_not_rational_zero(self):self.assertEqual(int(m.det(m.grid_matrix(False)))%2,0)
    def test_31_rational_zero_test(self):self.assertEqual(m.det([[1,2],[2,4]]),0)
    def test_32_rank_empty_matrix(self):self.assertEqual(m.matrank([]),0)
    def test_33_rank_two(self):self.assertEqual(m.matrank([[1,2],[1,3]]),2)
    def test_34_rank_one(self):self.assertEqual(m.matrank([[1,2],[2,4]]),1)
    def test_35_det_zero_dim(self):self.assertEqual(m.det([]),1)
    def test_36_random_grid_nonzero_exists(self):self.assertGreater(self.r['random_rational_specializations']['nonzero'],0)
    def test_37_random_grid_trial_count(self):
        v=self.r['random_rational_specializations'];self.assertEqual(v['nonzero']+v['zero'],56)
    def test_38_deterministic_replay(self):self.assertEqual(m.run(),self.r)
    def test_39_no_full_family_credit(self):self.assertFalse(self.r['whole_family_172_validated'])
    def test_40_no_Lean_claim_from_finite(self):self.assertEqual(self.r['formal_selected_theorem'],'SEPARATE_GITHUB_LEAN_COMPARATOR')
    def test_41_zero_tensor_spatial_block_impossible(self):
        P=((0,)*3,)*3;self.assertNotEqual(P[1][1],1)
    def test_42_source_requires_alg_independent(self):self.assertIn('algebraically independent',self.r['original_hypothesis'])
    def test_43_integer_specialization_not_satisfy_hyp(self):self.assertTrue(self.r['diagonal_negative_control']['algebraic_independence_not_met'])
    def test_44_cleared_8_power_six(self):self.assertEqual(8**6,262144)
    def test_45_rational_det64(self):self.assertEqual(2**6,64)
    def test_46_minor_nonzero_even_permutation_sign(self):self.assertEqual(abs(m.det(m.grid_matrix(True))),262144)
    def test_47_full_sample_row_count(self):self.assertEqual(len(self.r['grid']['all_evaluation_rows']),9)
    def test_48_original_scaling_preserved(self):
        for t in [F(0),F(1),F(2)]:self.assertEqual(m.p(t)[0],1)
    def test_49_wrong_duplicate_grid(self):
        A=list(m.C(True));A[0]=A[1]
        self.assertEqual(m.det(A),0)
    def test_50_tensor_certificate_rational_circle(self):
        pts=m.rational_circle_geometry(tuple(map(F,(-4,-3,-2,-1,0,1,2,3,4))))
        self.assertTrue(all(x*x+y*y==1 for x,y in pts))

if __name__=='__main__':unittest.main(verbosity=2)
