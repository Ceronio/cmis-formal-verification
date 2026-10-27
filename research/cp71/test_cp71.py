#!/usr/bin/env python3
"""Adversarial CP71 contract tests; finite checks are not full theorem proofs."""
import copy
import math
import unittest
from fractions import Fraction as Q
from math_audit import (ZERO,ONE,X,Y,GOOD_P,BAD_P,affine_rank,collapse_multiplication,
    eval_tensor,exact_geometric_invariance,one_dimensional_countercolour,
    plus,neg,run,simplex_test,squared_distance,tensor_checks,times)

class TestCP71Mathematics(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.result=run()

    def test_report_no_false_formal_credit(self):
        self.assertEqual(self.result["additional_formal_credit"],0)
        self.assertFalse(self.result["family_whole_scope_validated"])
        self.assertEqual(self.result["publisher_classification_lean_kernel"],"NOT_RUN")

    def test_simplex_exhaustive_colouring_has_collision(self):
        for row in self.result["simplex_pigeonhole"]:
            self.assertEqual(row["counterexamples"],0)
            self.assertEqual(row["colorings_checked"],row["colors"]**(row["colors"]+1))

    def test_simplex_sharpness_count(self):
        for r in (2,3,4,5):
            self.assertEqual(simplex_test(r)["sharpness_avoiding_r_point_colorings"],math.factorial(r))

    def test_rational_distances_do_not_require_floats(self):
        self.assertEqual(squared_distance((Q(0),Q(0)),(Q(3,2),Q(4,3))),Q(145,36))
        self.assertIsInstance(squared_distance((Q(0),),(Q(1),)),Q)

    def test_original_scale_rejects_dilation(self):
        self.assertEqual(exact_geometric_invariance()["incorrect_scalings_rejected"],3)

    def test_rigid_motion_preserves_pairwise_distances(self):
        self.assertEqual(exact_geometric_invariance()["exact_pairwise_checks"],9)

    def test_affine_rank_full_triangle(self):
        self.assertEqual(affine_rank([(Q(0),Q(0)),(Q(1),Q(0)),(Q(0),Q(1))]),2)

    def test_affine_rank_collinear(self):
        self.assertEqual(affine_rank([(Q(0),Q(0)),(Q(1),Q(1)),(Q(2),Q(2))]),1)

    def test_affine_rank_duplicate_points(self):
        self.assertEqual(affine_rank([(Q(0),Q(0)),(Q(0),Q(0))]),0)

    def test_tensor_exact_evaluations_zero(self):
        self.assertEqual(eval_tensor(GOOD_P,(ZERO,ZERO)),ZERO)
        self.assertEqual(eval_tensor(GOOD_P,(X,Y)),ZERO)

    def test_tensor_spatial_block_is_identity(self):
        self.assertEqual(GOOD_P[1][1],ONE)

    def test_negative_tensor_control_fail_before_multiplication(self):
        self.assertNotEqual(eval_tensor(BAD_P,(X,Y)),ZERO)

    def test_negative_tensor_control_fake_pass_after_multiplication(self):
        self.assertEqual(collapse_multiplication(eval_tensor(BAD_P,(X,Y))),{})

    def test_permuting_matrix_indices_breaks_certificate(self):
        tampered=((ONE,ZERO),(neg(Y),ZERO))
        self.assertNotEqual(eval_tensor(tampered,(ZERO,ZERO)),ZERO)

    def test_one_dimensional_2_color_obstruction(self):
        self.assertEqual(one_dimensional_countercolour(Q(5,3)),488)

    def test_periodic_negative_rational_positions(self):
        self.assertEqual(one_dimensional_countercolour(Q(3,7)),488)

    def test_exact_sphere_center_pair(self):
        for t in (Q(2),Q(-2),Q(7,9)):
            self.assertEqual((Q(0)-t/2)**2,(t-t/2)**2)

    def test_pitfall_five_circle_is_not_classification(self):
        self.assertNotIn("PASS_SELECTED_THEOREM",self.result["status"])

    def test_all_checks_deterministic(self):
        self.assertEqual(run(),self.result)

if __name__=="__main__":
    unittest.main(verbosity=2)
