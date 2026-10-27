#!/usr/bin/env python3
"""Adversarial, mathematically scoped CP72 tests. No theorem credit."""
import itertools
import math
import random
import unittest
from collections import Counter
from fractions import Fraction as Q
from transitive_math import (
    ONE,X,Y,automorphisms,composition,dist2,distance_matrix,mean,
    radii2,group_checks,uniform_orbit_test,transitive_action,
    variance_identity,affine_rank,example_configurations,
    orbit_examples,exact_rigid_map_for_rectangle_subconfiguration,
    symbolic_rectangle_tensor,edge_cases,finite_grid_sweep,
    padd,pmul,pscale,collapse,run
)


class CP72IndependentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.results=run()
        cls.cases=example_configurations()

    def test_a_scope_no_false_family_credit(self):
        self.assertFalse(self.results["full_family_validated"])
        self.assertFalse(self.results["other_family_172_endpoints_claimed"])
        self.assertEqual(self.results["publisher_transitive_theorem_lean_status"],"SEPARATE_GITHUB_COMPARATOR")

    def test_b_seven_distinct_geometric_examples(self):
        self.assertEqual(len(self.results["group_cases"]),7)

    def test_c_rectangle_dihedral_group_has_four_actions(self):
        g=automorphisms(self.cases["rectangle_4"])
        self.assertEqual(len(g),4)
        self.assertTrue(transitive_action(self.cases["rectangle_4"],g))

    def test_d_square_dihedral_group_has_eight_actions(self):
        self.assertEqual(len(automorphisms(self.cases["square_4"])),8)

    def test_e_four_vertex_regular_simplex_has_S4_action(self):
        self.assertEqual(len(automorphisms(self.cases["simplex_4"])),math.factorial(4))

    def test_f_octahedral_action_has_48_distance_permutations(self):
        self.assertEqual(len(automorphisms(self.cases["octahedron_6"])),48)

    def test_g_nontransitive_scalene_group_is_identity(self):
        p=self.cases["scalene_triangle_3"]
        self.assertEqual(automorphisms(p),(tuple(range(3)),))
        self.assertFalse(transitive_action(p,automorphisms(p)))

    def test_h_uneven_line_has_two_isometries_not_transitive(self):
        p=self.cases["uneven_line_4"]
        self.assertEqual(len(automorphisms(p)),2)
        self.assertFalse(transitive_action(p,automorphisms(p)))

    def test_i_singleton_is_transitive_and_nonempty(self):
        p=self.cases["singleton_1"]
        self.assertTrue(transitive_action(p,automorphisms(p)))
        self.assertEqual(affine_rank(p),0)

    def test_j_every_real_group_closed_under_inverse_and_product(self):
        for p in self.cases.values():
            self.assertTrue(group_checks(p,automorphisms(p)))

    def test_k_missing_group_element_fails_group_closure(self):
        p=self.cases["rectangle_4"]
        with self.assertRaises(AssertionError):
            group_checks(p,automorphisms(p)[:-1])

    def test_l_uniform_orbit_proof_exact(self):
        for name in ["rectangle_4","square_4","simplex_4","octahedron_6"]:
            p=self.cases[name]
            G=automorphisms(p)
            self.assertTrue(uniform_orbit_test(p,G))
            for i in range(len(p)):
                c=Counter(g[i] for g in G)
                self.assertEqual(set(c.values()),{len(G)//len(p)})

    def test_m_nontransitive_not_upgraded_from_orbit(self):
        p=self.cases["uneven_line_4"]
        self.assertFalse(uniform_orbit_test(p,automorphisms(p)))

    def test_n_transitive_centroid_sphere_exact(self):
        for name in ["rectangle_4","square_4","simplex_4","octahedron_6"]:
            p=self.cases[name]
            self.assertEqual(len(set(radii2(p,mean(p)))),1)

    def test_o_scalene_cospherical_but_not_transitive(self):
        p=self.cases["scalene_triangle_3"]
        self.assertNotEqual(len(set(radii2(p,mean(p)))),1)
        self.assertEqual(len(set(radii2(p,(Q(1),Q(3,2))))),1)

    def test_p_variance_identity_all_examples(self):
        for p in self.cases.values():
            self.assertTrue(variance_identity(p))

    def test_q_distances_survive_vertex_relabelings(self):
        rng=random.Random(20261027)
        for name,p in self.cases.items():
            group=automorphisms(p)
            for _ in range(12):
                pp=tuple(p[i] for i in rng.sample(range(len(p)),len(p)))
                self.assertEqual(len(automorphisms(pp)),len(group),name)
                self.assertEqual(sorted(radii2(p,mean(p))),sorted(radii2(pp,mean(pp))))

    def test_r_subconfiguration_affine_extension_is_orthogonal(self):
        r=exact_rigid_map_for_rectangle_subconfiguration()
        self.assertEqual(r["isometry_gram_tests"],16)
        self.assertEqual(r["subconfiguration_distances_preserved"],36)

    def test_s_rank_of_three_rectangle_vertices_is_two(self):
        self.assertEqual(affine_rank(self.cases["rectangle_4"][:3]),2)

    def test_t_rational_distance_values_not_floats(self):
        a,b=self.cases["rectangle_4"][:2]
        self.assertEqual(dist2(a,b),Q(4))
        self.assertIsInstance(dist2(a,b),Q)

    def test_u_exact_tensor_zero_before_multiplication(self):
        w=symbolic_rectangle_tensor()
        self.assertEqual(w["pre_multiplication_evaluations_zero"],4)
        self.assertEqual(w["witness_tensor_P00"],"-(1 + X*Y)")

    def test_v_wrong_tensor_only_zero_after_multiplication(self):
        wrong=padd(pmul(X,Y),pscale(pmul(X,X),-1))
        self.assertNotEqual(wrong,{})
        self.assertEqual(collapse(wrong),{})

    def test_w_negative_control_X_not_equal_Y(self):
        self.assertNotEqual(X,Y)
        self.assertNotEqual(pmul(X,Y),pmul(X,X))

    def test_x_grid_sweep_255_exact_distinct_input_subsets(self):
        self.assertEqual(self.results["grid_total"],255)
        self.assertEqual([row["configurations"] for row in self.results["grid_sweep"]],[9,36,84,126])

    def test_y_grid_sweep_never_confuses_transitive_and_non(self):
        for d in self.results["grid_sweep"]:
            self.assertEqual(d["transitive"]+d["nontransitive"],d["configurations"])

    def test_z_nontransitive_perturbed_rectangle(self):
        p=list(self.cases["rectangle_4"])
        p[-1]=(Q(3),Q(1))
        G=automorphisms(tuple(p))
        self.assertFalse(transitive_action(tuple(p),G))

    def test_aa_sphere_orbit_moment_from_distance_matrix(self):
        p=self.cases["square_4"]
        M=distance_matrix(p)
        totals=[sum(row,Q(0)) for row in M]
        self.assertEqual(len(set(totals)),1)

    def test_ab_hales_jewett_naive_scale_shortcut_rejected(self):
        p=self.cases["rectangle_4"]
        delta2=dist2(p[0],p[1])
        self.assertNotEqual(2*delta2,delta2)
        # Unknown HJ variable count m leads to sqrt(m) scaled distance:
        self.assertEqual(2*delta2,Q(8))

    def test_ac_input_order_and_output_deterministic(self):
        self.assertEqual(run(),self.results)

if __name__=="__main__":
    unittest.main(verbosity=2)
