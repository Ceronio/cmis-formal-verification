# CMIS CP71 — Independent mathematical contract and elementary subproofs
**Family 172 — Classification of finite Euclidean Ramsey configurations**  
**Source pin:** `openai/math` at `fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`.  
**Scope:** CP71 definitions, quantifiers, exact geometry and two-point tensor examples. This is *not* an independent proof of the full published classification.

## 1. Exact mathematical statement — no altered quantifiers

The publisher's Lean definition is, for a finite indexed configuration `a : Fin s → EuclideanSpace ℝ (Fin d)`:

`∀ r : ℕ, 2 ≤ r → ∃ D : ℕ, 1 ≤ D ∧ ∀ c : Space D → Fin r, ∃ b : Fin s → Space D, Congruent a b ∧ ∃ k : Fin r, ∀ i, c (b i) = k`.

`Congruent a b` means `∀ i j, dist (b i) (b j) = dist (a i) (a j)`. There is no dilation or adjustable scale. There is no measurability assumption on `c`. The dimension `D` may depend on the number `r` of colors but not on the coloring.

The full classification theorem assumes `s≥2`, `d≥1`, `a` injective and full affine span; it states `Ramsey a ↔ FieldCriterion a`. Dropping any hypothesis changes the theorem.

**Scope separation:** the seven comparator targets in the publisher's `lean/docs/172.md` refer to different positive and negative results. The tensor-field classification is not identical to the circle, transitive, cosphericity, quadratic-independence, nine-point or twelve-point statements.

## 2. Independent constructive proof: any two-point configuration is Euclidean Ramsey

Let `A={a₀,a₁}` and `δ=dist(a₀,a₁)>0`. Given an integer `r≥2`, set `D=r+1` and define `r+1` points in `ℝ^D` by `v_i=(δ/√2)e_i`, `i=0,...,r`, with `e_i` the standard coordinate unit vectors. For distinct `i,j`, we have

`‖v_i-v_j‖² = (δ²/2)‖e_i-e_j‖² = δ²`.

Any map `c:ℝ^D→{0,...,r-1}` colors these `r+1` vertices using `r` colors. By pigeonhole, some distinct pair `v_i,v_j` has the same color. Set `b₀=v_i,b₁=v_j`: this is a monochromatic congruent copy of `A` at exactly its original scale.

**Conclusion:** `∀r≥2, ∃D=r+1≥1` such that every `r`-coloring of `ℝ^D` contains the desired pair. This is a complete conventional mathematical proof of the two-point special case. It does not prove the classification of general finite configurations or any full Lean selected theorem. We make no claim that `D=r+1` is minimal.

If `a₀=a₁`, the two-index configuration is trivially monochromatic by repeating one selected point. Injectivity is needed in the full classification theorem, not the bare Ramsey definition.

## 3. Independent obstruction: dimension one cannot be fixed for the two-color case

For the same `δ>0`, define `c:ℝ→{0,1}` by `c(x)=⌊x/δ⌋ mod 2`. Half-open intervals remove all boundary ambiguity. Whenever `y=x+δ` or `y=x-δ`,

`⌊y/δ⌋=⌊x/δ⌋±1`

because addition by an integer commutes with floor. Therefore `c(y)≠c(x)`. All distinct pairs at distance `δ` in one dimension have opposite colors.

**Conclusion:** the ambient dimension matters; for `r=2`, the `D=1` version fails even though the configuration is Euclidean Ramsey because larger `D` is permitted. This formally separates `∃D∀c` from the erroneous assertion that the original dimension suffices.

## 4. Explicit exact tensor certificate for `A={0,t}⊂ℝ`, `t≠0`

Let `F=ℚ(t)⊂ℝ`, `B=F⊗_ℚ F`, and let indices `0,1` denote constant and spatial components of the augmented vector `p_i=(1,a_i)`.

Choose the not-necessarily-symmetric matrix
\[
P=\begin{pmatrix}
0 & 0\\
-(1\otimes t) & 1\otimes1
\end{pmatrix}\in\mathrm{Mat}_{2}(B).
\]

For `a₀=0`, `(p₀⊗1)^TP(1⊗p₀)=P₀₀=0`.
For `a₁=t`, expand the tensor-field evaluation, without applying the multiplication map:
\[
(t\otimes1)(-(1\otimes t))+(t\otimes1)(1\otimes1)(1\otimes t)
=-\,t\otimes t+t\otimes t=0 .
\]

For the only spatial pair `(1,1)`, `m_F(P₁₁)=m_F(1⊗1)=1`. Thus the exact field criterion holds for this two-point full-affine-span representative, *over the tensor product*, for any real nonzero `t`.

The publisher's criterion does not require `P` to be symmetric, nor does it impose separate multiplied constraints on the constant row and column. Requiring either would silently change the theorem.

This is an independent explicit subcase certificate. Its existence also illustrates the consistency of the full theorem with the geometric simplex proof.

## 5. Why testing only after tensor multiplication is unsound

Replace `P₁₀` above by `-(t⊗1)`, keeping `P₁₁=1⊗1`. At `a₁=t`, the tensor evaluation becomes
\[
(t\otimes t)-(t^2\otimes1).
\]
Applying `m_F` sends both terms to `t^2`, giving zero. **But the pre-multiplication tensor is generally nonzero.**

For a transcendental `t`, the rational vectors `1,t,t^2` are linearly independent. There exist `ℚ`-linear functionals `u,v:F→ℚ` with `u(t)=1,u(t^2)=0` and `v(t)=1,v(1)=0`. The tensor functional `u⊗v` sends the displayed difference to `1`. Therefore the tensor difference is nonzero. This separates the two equalities rigorously.

The computational engine uses `ℚ[X,Y]` for the formal tensor variables `X=t⊗1,Y=1⊗t` to demonstrate a universal polynomial identity and its negative control. It does not claim that `ℚ[X,Y]` is isomorphic to `F⊗_ℚ F` for arbitrary `t`, especially algebraic `t`.

## 6. Tensor condition implies an ordinary sphere equation

Suppose `P` satisfies the tensor-field criterion for a full-dimensional configuration. Apply `m_F` to its vanishing evaluations. Since the spatial block `m_F(P_{jk})` is the identity, each point satisfies
\[
\|a_i\|^2+\ell\cdot a_i+c=0,
\]
where `c=m_F(P_{00})` and `ℓ_j=m_F(P_{0j}+P_{j0})`. Completing the square yields
\[
\|a_i+\ell/2\|^2=\|\ell\|^2/4-c,
\]
the same nonnegative squared radius for every `i`. This supplies a conventional direct derivation of necessary cosphericity **from the field criterion**, but not the converse. It does not justify dropping the original tensor equalities or upgrading the general theorem to kernel checked.

For the explicit `{0,t}` certificate, `ℓ=-t,c=0`, and the center is `t/2` with squared radius `t^2/4`.

## 7. Bounded computational evidence and limitations

`math_audit.py` independently enumerates all `r^{r+1}` colorings of the coordinate-axis simplex for `r=2,3,4,5`. It also confirms the `r!` injective `r`-colorings of `r` distinct marked vertices, checks periodic 1D obstruction points using exact rational floors, computes affine ranks through rational Gaussian elimination, tests isometry and dilation negative controls, and checks the tensor matrix via exact sparse-polynomial arithmetic.

These finite checks support the derivations; they do not turn a finite search into a proof for arbitrary `r`. The general statements in §§2–6 are established by the written elementary mathematical arguments, not inferred from a finite sample.

## 8. Source-to-theorem reconciliation

The publisher's manuscript introduction (section 01) and tensor analysis (section 02), comparator challenge and configuration, and Lean solution interface are bound by exact Git object hashes in `SOURCE_PINS.json`. The GitHub Action fetches the six pinned source objects, recomputes each Git blob SHA-1, and runs fail-closed literal definition/hypothesis/axiom contract checks.

**Not completed in CP71:** kernel replay of the general `OAI.EuclideanRamsey.classification` theorem; complete transitive imported Lean dependency closure; independent external peer review; all seven comparator targets; the entire 26-page manuscript proof; any public assertion of novel authorship, priority or programme-wide certification.

**Release classification:** CP71 standalone **bounded mathematical contract and special-case evidence**, with completed independent GitHub test execution if and only if the live Actions receipt confirms it. Full Family172 formal certification remains deferred, as agreed.
