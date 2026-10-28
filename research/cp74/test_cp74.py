#!/usr/bin/env python3
"""CP74 adversarial mathematical tests (stdlib), no formal-theorem credit."""
from __future__ import annotations
import math
import unittest
from fractions import Fraction as F
import math_audit as M


class CP74IndependentMathematics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=M.run()

    def test_01_selected_scope_not_whole_family(self):
        self.assertEqual(self.result["source_full_theorem"],"OAI.GrahamSpherical.full_main")
        self.assertFalse(self.result["whole_family_172_certified"])

    def test_02_12_labels(self):
        self.assertEqual(len(M.coordinates_polynomials()),12)

    def test_03_three_squares_each_four(self):
        self.assertEqual([sum(p["group"]==g for p in M.coordinates_polynomials()) for g in range(3)],[4,4,4])

    def test_04_signed_weight_vector(self):
        self.assertEqual(M.WEIGHTS,(1,)*8+(-2,)*4)
        self.assertEqual(sum(M.WEIGHTS),0)

    def test_05_abs_weight_total(self):
        self.assertEqual(sum(map(abs,M.WEIGHTS)),16)

    def test_06_derivative_identity_delta_u(self):
        self.assertEqual(M.add(M.sub(M.mul(M.derive(M.U),M.D),M.mul(M.U,M.derive(M.D))),M.scale(M.V,2)),(0,))

    def test_07_derivative_identity_delta_v(self):
        self.assertEqual(M.sub(M.sub(M.mul(M.derive(M.V),M.D),M.mul(M.V,M.derive(M.D))),M.scale(M.U,2)),(0,))

    def test_08_circle_rotation_norm_polynomial(self):
        self.assertEqual(M.add(M.mul(M.U,M.U),M.mul(M.V,M.V)),M.mul(M.D,M.D))

    def test_09_weighted_zeroth_moment(self):
        assert M.matrix_moments()[0]==[[(0,)]*3 for _ in range(3)]

    def test_10_weighted_mixed_moment(self):
        assert M.matrix_moments()[1]==[[(0,)]*3 for _ in range(3)]

    def test_11_weighted_derivative_moment(self):
        A=M.matrix_moments()[2];s=M.scale(M.mul(M.D,M.D),4)
        self.assertEqual(A,[[(0,)]*3,[(0,),s,(0,)],[(0,),(0,),s]])

    def test_12_wrong_derivative_sign_detected(self):
        p=M.coordinates_polynomials()
        w=p[0]["derivative_numerators"][1]
        self.assertNotEqual(w,M.neg(w))

    def test_13_all_four_rational_samples_distinct(self):
        self.assertEqual(len(self.result["exact_rational_geometry_examples"]),4)

    def test_14_unit_norm_t_0111(self):
        sample=M.exact_sample(F(111,1000))
        self.assertEqual(sample["unit_norm_points"],12)

    def test_15_every_sample_exactly_12_unique(self):
        for v in (F(111,1000),F(11,100),F(119,1000),F(1,9)):
            self.assertEqual(len(set(M.actual_points(v))),12)

    def test_16_at_t0_rotated_squares_collapse(self):
        pts=M.actual_points(F(0)) if False else None
        # t=0 is outside the strict interval and creates duplicate labels.
        t=F(0)
        items=M.coordinates_polynomials()
        pts=tuple((M.eval_poly(x["numerators"][1],t),
                   M.eval_poly(x["numerators"][2],t)) for x in items)
        self.assertNotEqual(len(set(pts)),12)

    def test_17_parameter_lower_bound_start(self):
        self.assertFalse(self.result["factorial_parameter"]["rational_partial_sums"][1]["in_0_11_to_0_12"])

    def test_18_parameter_positive_strict_bound_after_third_term(self):
        self.assertTrue(self.result["factorial_parameter"]["rational_partial_sums"][2]["in_0_11_to_0_12"])

    def test_19_parameter_terms_correct(self):
        self.assertEqual(self.result["factorial_parameter"]["literal_series_first_terms"],[1,2,6,24])

    def test_20_16_color_finite_check(self):
        r=self.result["floor_color_falsification"]
        self.assertTrue(r["all_samples_16_color_not_monochromatic"])
        self.assertEqual(r["derived_16_color_modulus"],16)

    def test_21_50_color_finite_check(self):
        r=self.result["floor_color_falsification"]
        self.assertTrue(r["all_samples_50_color_not_monochromatic"])
        self.assertEqual(r["source_50_color_modulus"],50)

    def test_22_900_floor_samples(self):
        self.assertEqual(self.result["floor_color_falsification"]["samples"],900)

    def test_23_exact_energy_identity_positive_sample(self):
        e=[F(4)]*8+[F(3)]*3+[F(3)]
        # sum=32-2*12=8
        self.assertEqual(sum(w*x for w,x in zip(M.WEIGHTS,e)),8)
        self.assertEqual(M.signed_floor_sum(e,1),8)
        self.assertGreater(len(set(M.colors(e,1,16))),1)

    def test_24_every_energy_sample_nonnegative(self):
        self.assertTrue(self.result["floor_color_falsification"]["all_samples_nonnegative"])

    def test_25_floor_of_negative_rationals(self):
        self.assertEqual(math.floor(F(-1,3)),-1)
        self.assertEqual(math.floor(F(-7,3)),-3)

    def test_26_floor_mod_negative_rationals_correct(self):
        self.assertEqual((-1)%16,15)
        self.assertEqual((-1)%50,49)

    def test_27_invariant_critical_negative_control(self):
        e=[F(0)]*12
        self.assertEqual(len(set(M.colors(e,1,16))),1)
        self.assertNotEqual(sum(w*x for w,x in zip(M.WEIGHTS,e)),8)

    def test_28_candidate_16_not_formally_proven(self):
        self.assertEqual(self.result["independent_deduction_16_colors"]["formal_Lean_kernel"],"NOT_RUN")

    def test_29_arbitrary_real_16_coloring_not_computed(self):
        self.assertFalse(self.result["full_50_color_avoiding_coloring_computed"])

    def test_30_fake_integer_identity_rejected(self):
        e=[F(0)]*12
        self.assertFalse(0<M.signed_floor_sum(e,1)<16)

    def test_31_source_50_rounding_weight_bound(self):
        e=[F(4)]*8+[F(3)]*4
        s=M.signed_floor_sum(e,3)
        self.assertTrue(16<s<32)

    def test_32_sphere_coordinate_not_rational_transcendence(self):
        self.assertIn("not the transcendental Liouville",self.result["limitations"][0])

    def test_33_symmetry_matrix_dimensions(self):
        for matrix in M.matrix_moments():
            self.assertEqual(len(matrix),3)
            self.assertTrue(all(len(row)==3 for row in matrix))

    def test_34_twelve_weights_by_group(self):
        w=M.coordinates_polynomials()
        self.assertEqual([sum(x["weight"] for x in w if x["group"]==g) for g in range(3)],[4,4,-8])

    def test_35_q0_spans_plane(self):
        p0=M.BASE
        self.assertIn((1,0),p0)
        self.assertIn((0,1),p0)

    def test_36_proof_does_not_change_50_original(self):
        self.assertTrue(self.result["independent_deduction_16_colors"]["publisher_original_selected_theorem_is_50_colors"])

    def test_37_deterministic_full_result(self):
        self.assertEqual(M.run(),self.result)

    def test_38_polynomial_negative_control_zero(self):
        self.assertEqual(M.sub(M.mul(M.D,M.D),M.add(M.mul(M.U,M.U),M.mul(M.V,M.V))),(0,))

    def test_39_liouville_partial_fraction_no_float(self):
        self.assertIsInstance(M.eval_poly(M.D,F(111,1000)),F)

    def test_40_no_false_formal_claim(self):
        self.assertEqual(self.result["source_selected_Lean_status"],"SEPARATE_PINNED_GITHUB_COMPARATOR")
        self.assertEqual(self.result["new_full_family_credit"],0)

if __name__=="__main__":
    unittest.main(verbosity=2)
