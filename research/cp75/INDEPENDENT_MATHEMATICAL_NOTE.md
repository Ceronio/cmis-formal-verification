# CP75 — Independent mathematical review: nine algebraically independent circle points

**CMIS Phase 2 / Family 172 / 28 October 2026 / standalone checkpoint**

**Attribution:** Original source: OpenAI Mathematics, pin fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb, manuscript "A classification of finite Euclidean Ramsey configurations", Section 7, and the Lean Comparator challenge EuclideanRamseyNine. This file is an independent research audit of the original claims, not a claim of original authorship, research priority or external peer certification.

## 1. Exact target and hypotheses

The full original selected Lean theorem is

  OAI.EuclideanRamsey.NineStatement.nine_circle_configuration

It takes a function t : Fin 9 → ℝ and the essential hypothesis

  AlgebraicIndependent ℚ t.

For each i, define a_i = ((1-t_i²)/(1+t_i²), 2t_i/(1+t_i²)) in ℝ². The conclusion is the conjunction of (a) injectivity of i↦a_i, (b) unit-circle membership for all i and (c) ¬Ramsey(a).

The original Ramsey definition quantifies in the order: for EVERY integer r≥2, there EXISTS D≥1 such that for EVERY r-coloring of ℝ^D, there EXISTS an original-scale monochromatic congruent copy. Thus ¬Ramsey means some finite r defeats every possible positive dimension. The nine-point theorem does NOT specify the number of colors in its statement or give the explicit 50-color construction of CP74.

**Source-scope warning:** nine rational numerical sample parameters are not algebraically independent over ℚ. Finite random examples cannot instantiate the theorem's hypothesis. CP75's exact rational calculations are employed as *specializations of a polynomial determinant expression*, not as examples of the original non-Ramsey configuration.

## 2. Distinctness, circular geometry and full affine span

For any real t, the rational parametrization p(t)=(1,(1-t²)/(1+t²),2t/(1+t²)) satisfies x²+y²=1. The denominator is 1+t²>0.

Moreover the inverse formula is t=y/(1+x), because 1+x=2/(1+t²)>0. Hence p(t) is injective for real t. Algebraic independence implies t_i≠t_j for distinct i,j (otherwise the nonzero polynomial X_i-X_j vanishes). Consequently all nine points are distinct and lie on the unit circle. Any three distinct points on a nondegenerate circle are noncollinear, since intersection with a line is a quadratic equation with at most two roots. The nine points have full affine span in ℝ².

## 3. Exact tensor-field obstruction (why nine points matter)

The CP71 full-affine-span classification states that Ramsey(a) is equivalent to the field tensor criterion FieldCriterion(a). Its *necessary* direction is the one used here.

Let F=ℚ(t_1,...,t_9) inside ℝ. Algebraic independence identifies F with the rational function field in nine variables. Denote the tensor ring B=F ⊗_ℚ F. The two copies of F correspond to disjoint independent indeterminates T_1,...,T_9 and U_1,...,U_9. By localization, B embeds faithfully in K=ℚ(T_1,...,T_9,U_1,...,U_9); the independence hypothesis is essential for this embedding.

For the augmented vector p(z)=(1,(1-z²)/(1+z²),2z/(1+z²)), the nine tensor-evaluation equations form a 9×9 matrix M over K, indexed by i∈Fin9 and by all nine ordered pairs (α,β)∈{0,1,2}²:

  M[i,(α,β)] = p_α(T_i) p_β(U_i).

Each row corresponds to an original configuration point, and each column to one entry P_{αβ} of the unknown tensor-field matrix. If FieldCriterion(a) held, then M·vec(P)=0. If det(M)≠0 in K, then vec(P)=0 in K; since B→K is injective, P=0 in B. But FieldCriterion also requires the multiplied 2×2 spatial block of P to equal I₂. Contradiction.

Thus proving the *generic* nine-row determinant nonzero excludes FieldCriterion and hence excludes Ramsey(a) by the previously established CP71 theorem.

## 4. Independent nonzero determinant witness; the paper and Lean use two normalizations

Let g=(0,1,-1), and index the nine rows by ordered pairs (a,b)∈{0,1,2}². Specialize T_{ab}=g_a and U_{ab}=g_b. This is a valid evaluation of a rational or polynomial determinant expression, **not** an assertion that these nine numbers are algebraically independent.

The rational-coordinate three-row matrix is

  C = [ [1,1,0], [1,0,1], [1,0,-1] ],   det C = 2.

Then the nine-row rational specialization is exactly C⊗C (Kronecker square), with determinant (det C)^6=2^6=64.

The pinned Lean grid proof instead first clears denominators and uses

  q(z) = (1+z², 1-z², 2z),
  C' = [ [1,1,0], [2,0,2], [2,0,-2] ], det C' = 8.

Its nine-row specialized polynomial matrix is C'⊗C', with determinant (det C')^6=8^6=262,144.

These two outputs are **mathematically consistent**. The product of the nine specialized row denominators (1+T_i²)(1+U_i²) is 4,096, so

  262,144 / 4,096 = 64.

The standalone exact-rational engine independently constructs each of the nine rows, checks the Kronecker equality, both three-by-three determinants, both nine-by-nine determinants, and the denominator product. It reproduces the original manuscript result and the separate Lean normalization without rounding.

This is a decisive reproducible witness that the cleared **polynomial determinant** is not identically zero. Since the generic rational-function denominator is nonzero, the generic rational determinant is also nonzero. It is NOT a claim that its determinant is nonzero for every numerical specialization.

## 5. Independent falsification controls and limitations

The following negative checks are necessary to avoid illegitimate conclusions:

**Diagonal tensor collapse.** Substituting U_i=T_i for nine rational points creates the matrix of ordinary quadratic evaluations. Its rank is 5 (circle relation x²+y²=1) and its 9×9 determinant is zero. This is consistent with the generic tensor matrix having nonzero determinant, since the diagonal substitution is a special singular locus. It does not contradict the theorem.

**Nine rational circle points can be Ramsey.** With distinct rational t_i, the coordinate field is F=ℚ. For the unit circle, the rational matrix P=diag(-1,1,1) satisfies the original tensor criterion over ℚ⊗_ℚ ℚ=ℚ, including the spatial identity. By CP71 classification these rational points *are* Ramsey, although their diagonal evaluation matrix has rank 5. Thus rational samples are not negative Ramsey examples.

**Changed row or column.** Duplicating one grid row makes the determinant zero. Swapping two columns changes the sign from 64 to -64, not its nonvanishing. Both are explicitly checked.

**Partial polynomial specialization.** A single nonzero determinant evaluation proves a polynomial is not identically zero; it does not establish the converse assertion that every assignment makes the determinant nonzero.

**No constructive color count.** The original selected theorem proves ¬Ramsey(a). The 50-color explicit construction from CP74 is a different theorem with a different literal witness. Do not transfer its color count to CP75.

**No invented real instance.** The algebraic-independence requirement cannot be verified for a finite list of ad hoc rational or decimal samples. CP75 does not present such values as satisfying the theorem's source hypothesis.

## 6. Independent execution and source assurance

The stdlib-only research engine verifies 50 adversarial tests, 56 deterministic rational specializations on the 18-variable evaluation expression, the exact nine-row grid and the diagonal singular case. The independent second implementation uses SymPy matrices and Kronecker determinants and does not import the research engine.

The GitHub source checker authenticates 20 original publisher Git blobs: selected challenge/config/solution, nine-point geometry, field/tensor and determinant modules, original CP71 classification dependency, manuscript and Apache license. Every Git blob SHA-1 is recomputed from raw bytes at the immutable source commit; SHA-256 records are written for each source snapshot. This checks identity and interface, not Lean theorem correctness.

The separate pinned Lean/Comparator GitHub workflow must execute exactly OAI.EuclideanRamsey.NineStatement.nine_circle_configuration, verify the original selected comparator, record all observed axioms and preserve its full proof receipt. A green Python test run does not replace this.

## 7. Certification, ownership and continuation boundary

Previous CP71, CP72, CP73 and CP74 each verified one distinct original selected theorem. CP75 may add one selected theorem after successful exact GitHub formal receipt review, leaving the two original Family 172 comparators for quadratic independence and cosphericity uncredited. Any full-family status must be evaluated separately after every relevant scope is resolved.

**External independent human mathematical certification remains deferred** as authorized. The CP75 package will include a standalone Word report, Excel progress and claim register, source snapshot and proofs, two original GitHub receipts, independent SymPy replay and SHA-256 manifests.

No branch merge, public release, changes to the original main register, Mac canonical archives, CBI or TBC. Stop at CP75. **CP76 is not started before user review.**
