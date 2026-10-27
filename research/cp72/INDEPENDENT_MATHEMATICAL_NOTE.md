# CP72 — Independent mathematical review: finite transitive Euclidean configurations

**CMIS Phase 2 · Family 172 · Standalone research · 27 October 2026**

**Authority and separation.** This review is independently reasoned from the exact mathematics and pinned manuscript, but it is not a claim of original discovery. The source paper and formal solution are attributed to the OpenAI Mathematics repository. CP71 verified the general selected classification theorem through Comparator and Lean; CP72 reviews the separate transitive-subset result. Mathematical tests, exact-target formal acceptance, whole-family completion and later external certification are distinct units.

## 1. Precisely stated theorem and its hypotheses

Let \(\mathbb{R}^{D}\) be Euclidean space and \(Y=\{y_i:i\in\mathrm{Fin}(t)\}\) a finite injectively indexed set of points. Its distance-preserving permutation group is
\[
H=\{\sigma\in \operatorname{Sym}(t):
 \|y_{\sigma(i)}-y_{\sigma(j)}\|=\|y_i-y_j\|
 \text{ for every }i,j\}.
\]
It is *transitive* when, for every \(i,j\), some \(\sigma\in H\) satisfies \(\sigma(i)=j\).

Given a nonempty injectively indexed configuration \(A=\{a_i:i\in\mathrm{Fin}(s)\}\) in the same Euclidean space, assume \(A\subseteq Y\). The original exact-target theorem
`OAI.EuclideanRamsey.TransitiveConsequence.subset_of_finite_transitive_ramsey`
proves \(\operatorname{Ramsey}(A)\): for all integers \(r\ge2\), some positive ambient dimension \(N\) forces a congruent monochromatic copy at **the original distance scale** under every \(r\)-colouring of \(\mathbb{R}^N\).

The publisher's comparator explicitly requires \(s>0\), injectivity of \(A\) and \(Y\), point-set inclusion and transitivity of *distance-preserving permutations*. It does not assume that the subset \(A\) itself is transitive. Arbitrary colourings need not be measurable. This is one of seven Family 172 comparator results, not the whole family.

## 2. Independent elementary result: transitivity implies a centroid sphere

Let \(\bar y=t^{-1}\sum_jy_j\). For every \(i\), expand squared norms:
\[
\sum_j \|y_i-y_j\|^2 =
 t\|y_i-\bar y\|^2+\sum_j\|y_j-\bar y\|^2.
\]
Indeed, substitute \(y_i-y_j=(y_i-\bar y)- (y_j-\bar y)\) and use \(\sum_j (y_j-\bar y)=0\).

If \(\sigma\in H\) carries \(i\) to \(k\), the sum on the left for \(k\) equals the sum for \(i\), because \(\sigma\) bijects the labels and preserves every distance. Hence \(t\|y_i-\bar y\|^2\) is independent of \(i\), giving a sphere centred at \(\bar y\). This proof does not invoke any general Ramsey theorem.

**Do not reverse the implication.** A scalene triangle is cospherical (all three non-collinear points have a circumcircle) while its distance-automorphism group is trivial and not transitive. The arithmetic centroid is generally not its circumcentre.

## 3. Independent elementary result: uniform orbit sums

Because \(H\) is a finite transitive group, its action on indices is uniform. Fix any \(i,j\). Let \(h_0\in H\) carry \(i\) to \(j\). Right multiplication \(h\mapsto h h_0\) is a permutation of \(H\). For every map \(f:Y\to M\) into an additive commutative monoid,
\[
 \sum_{h\in H} f(y_{h(i)})
 =\sum_{h\in H} f(y_{hh_0(i)})
 =\sum_{h\in H} f(y_{h(j)}).
\]
Equivalently, every point in \(Y\) occurs exactly \(|H|/t\) times in the list \((h(i))_{h\in H}\). This is exact; neither approximate symmetry nor finite random sampling is sufficient.

The identity remains valid for the tensor-valued maps \(f(y)=y_j\otimes_\mathbb{Q} y_j\), and hence for arbitrary real coordinates when treated as a vector space over \(\mathbb Q\).

## 4. Affine isometry extension by distance polarization

Suppose \(A\) has at least two points. Replace it by a congruent representative in its *full affine dimension* \(d\ge1\). For every \(h\in H\), map each representative point \(a_i\) to the orbit point \(h(y_{e(i)})\), using an injection \(e:\mathrm{Fin}(s)\hookrightarrow\mathrm{Fin}(t)\) from the given subset inclusion.

Pairwise distance preservation implies equality of inner products of all difference vectors:
\[
 2\langle a_i-a_0,a_j-a_0\rangle
 =\|a_i-a_0\|^2+\|a_j-a_0\|^2-\|a_i-a_j\|^2.
\]
The mapped vectors have the same Gram matrix. Because the original differences span \(\mathbb R^d\), the prescribed map extends to a linear isometry \(Q_h:\mathbb R^d\to\mathbb R^D\) and translation \(z_h\) satisfying \(h(y_{e(i)})=z_h+Q_h a_i\) for every \(i\).

The finite diagnostic suite constructs all four exact affine orthogonal extensions of a three-vertex rectangle subset, using rational matrix inversion and checking \(Q_h^TQ_h=I_2\) without floating-point tolerances.

## 5. Finite-group averaging gives the required tensor certificate

Work in \(W=\mathbb R\times\mathbb R^d\), considered over \(\mathbb Q\). Each affine coordinate of \(z_h+Q_h x\) is a linear functional in the augmented variable \((1,x)\). Write its coefficient vector as \(w_{hj}\in W\) for \(h\in H\), \(j\in\mathrm{Fin}(D)\), so
\[
 e_i(w_{hj})=(h(y_{e(i)}))_j.
\]
Fix the first label \(i_0\) and define the constant coefficient vector \(c_{hj}=((h(y_{e(i_0)}))_j,0,\dots,0)\in W\).

Consider the symmetric rational tensor
\[
 T=\frac1{|H|}\sum_{h\in H}\sum_{j=1}^D
       \bigl(w_{hj}\otimes_\mathbb Q w_{hj}
       -c_{hj}\otimes_\mathbb Q c_{hj}\bigr).
\]

For each \(i\), its evaluation is
\[
 (e_i\otimes e_i)(T)=\frac1{|H|}\sum_{h,j}
 \left[(h(y_{e(i)}))_j\otimes(h(y_{e(i)}))_j
 -(h(y_{e(i_0)}))_j\otimes(h(y_{e(i_0)}))_j\right]=0.
\]
The last identity is the *exact tensor-valued orbit-sum equality* from §3. It is an equality **before** applying the tensor multiplication map; no illegitimate collapse to ordinary scalar second moments has occurred.

The tensor's spatial gradient block is
\[
 G(T)=\frac1{|H|}\sum_{h\in H}\sum_{j=1}^D
            u_{hj}u_{hj}^{T}
 =\frac1{|H|}\sum_h Q_h^TQ_h=I_d,
\]
where \(u_{hj}\) is the spatial row of \(Q_h\); the constant \(c_{hj}\) contributes no spatial gradient.

Thus \(T\) satisfies the *real symmetric tensor criterion*. The pinned source's rational-field descent and exact tensor equivalence (verified at the original selected classification theorem in CP71) yield a tensor-field witness. The classification's sufficient direction gives \(\operatorname{Ramsey}(A)\).

Singletons are immediate; lower-affine-span cases are handled by passing to a congruent representative in their actual affine dimension and translating back. This is a conventional proof reconstruction of the published corollary *conditional on the CP71 classification equivalence*. It does not represent an original independent proof of that deep classification itself.

## 6. Exact nontrivial symbolic instance over a transcendental parameter

Take \(t\in\mathbb R\) transcendental and \(Y=\{(\pm t,\pm1)\}\), with group \(H=C_2\times C_2\) acting by two independent coordinate-sign flips. It is a finite transitive four-point configuration even though a generic rectangle is not a regular square.

Its field is \(F=\mathbb Q(t)\). The matrix
\[
P=
\begin{pmatrix}
 -(t\otimes t+1\otimes1)&0&0\\
 0&1\otimes1&0\\
 0&0&1\otimes1
\end{pmatrix}
\in\operatorname{Mat}_{3}(F\otimes_\mathbb Q F)
\]
satisfies the exact tensor equations at **each of the four points**: the spatial quadratic term is \(t\otimes t+1\otimes1\) regardless of signs, and cancels the constant entry. Its multiplied spatial block is \(I_2\). Every three-point subset has full affine span, so this is also a valid criterion for that subset; every two-point or singleton subset is already Ramsey.

This example tests a genuinely non-rational coordinate field rather than merely solving an ordinary real-valued sphere equation. The computational engine uses sparse polynomials in independent formal symbols \(X=t\otimes1\) and \(Y=1\otimes t\), with exact rational coefficients, as a faithful polynomial subring for transcendental \(t\).

**Adversarial countercheck:** replace \(P_{00}\) with \(-(t^2\otimes1+1\otimes1)\). Its evaluation becomes \(t\otimes t-t^2\otimes1\). Multiplication sends this to \(t^2-t^2=0\), but the tensor itself is nonzero for transcendental \(t\). A linear functional on \(F\otimes_\mathbb Q F\) detecting the two independent tensor monomials demonstrates the failure. Therefore a post-multiplication numerical check can pass while the actual theorem hypothesis fails.

## 7. Finite independent diagnostics and negative controls

All computations use exact \(\mathbb Q\)-valued squared distances, explicit permutation enumeration and rational polynomial arithmetic. They include:

- Full distance-automorphism groups: 4 for a non-square rectangle, 8 for a square, 24 for a regular four-vertex simplex, 48 for an octahedron.
- Negative controls: one automorphism for a scalene triangle; two for a four-point uneven line. Neither nontransitive set is mislabeled transitive.
- Every permutation is checked for distance preservation; inverses and products are checked for group closure.
- Uniform orbit counts and the centroid variance identity are tested at every vertex.
- Exact rational reconstruction of every induced affine isometry of a three-vertex rectangle subset, including Gram matrices and image equality.
- Symbolic tensor cancellation at all four transcendental rectangle labels, spatial identity block and the deliberately invalid tensor candidate.
- A systematic 255-configuration sweep of every subset of size 1 through 4 of the integer \(3\times3\) square grid; positive transitivity is never inferred merely from equal radii.
- Vertex-relabeling invariance and test-code tamper controls.

These tests support the independent derivations. They neither establish the theorem for *arbitrary* finite transitive sets nor prove the full publisher comparison by numerical enumeration.

### Why the tempting one-line Hales–Jewett shortcut is unsound

A naive construction concatenates orbit copies in each word coordinate and applies a combinatorial line. If \(m\) positions are variable, its Euclidean distance is \(\sqrt m\) times the original distance. Since \(m\) is selected *after* applying the Hales–Jewett theorem to a coloring, rescaling the already chosen line by \(1/\sqrt m\) changes the coloring and does not prove monochromaticity at the original scale. The independent proof above avoids that gap through exact tensor averaging and the established classification theorem.

## 8. What the actual GitHub workflow is required to prove

The bounded research workflow must execute every adversarial Python test, recompute the exact finite results, fetch nine original publisher files at commit
`fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb`, compare their Git blob identities, and preserve an integrity-checked research receipt. This stage is not a Lean proof.

The separate full workflow must select exactly
`OAI.EuclideanRamsey.TransitiveConsequence.subset_of_finite_transitive_ramsey`,
pin source config/challenge/solution and compiler versions, execute the Comparator and Lean kernel, inspect observed axioms and produce a formal receipt. Only if that run returns a verified `PASS_SELECTED_THEOREM` can CP72 record selected-theorem-level formal acceptance. This does not upgrade all seven Family 172 results.

### Required final review boundaries

- Only the CP72 transitive-subset comparator can receive new formal selected-theorem credit in this checkpoint.
- The CP71 main-classification selected-theorem result is preserved, not executed again merely to inflate totals.
- Independent external mathematician certification remains DEFERRED as authorised.
- Source licence and attribution remain attached; no personal, CBI, AIREM, TBC, commercial or unpublished materials may be pushed.
- PR remains draft and unmerged; no GitHub release publishing.
- **CP73 must not begin before user review of the finished CP72 archive.**

**Primary cited source:** `openai/math` pinned at the above exact commit, manuscript Section 7, original comparator and original Lean solution. See `SOURCE_PINS.json` for every exact source blob.
