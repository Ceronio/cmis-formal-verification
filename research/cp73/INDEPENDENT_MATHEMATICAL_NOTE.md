# CP73 — Five circular points: independently reviewed mathematics

**CMIS Phase 2 / Family 172 / 27 October 2026.** Source attribution: OpenAI Mathematics, immutable source commit fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb. This document distinguishes new independent review from authorship or external certification. Its conclusions rely on the publisher's CP71-classification and separate CP73 formal Lean acceptance when that workflow succeeds.

## I. Original theorem and trust boundary

The exact theorem is **OAI.EuclideanRamsey.CircleConsequence.at_most_five_circle_points_ramsey**: for nonempty injectively indexed planar points of cardinality at most five, all at the same distance from one center, the Euclidean Ramsey property holds. In precise quantifiers, for every finite color count r≥2 there is D≥1 such that every arbitrary coloring of R^D with r colors has a monochromatic copy preserving **every original pairwise distance**. Radius may be zero; injectivity then forces a singleton.

The primary problem source is the manuscript's Section 7 corollary; the original Lean solution imports CircleRows, CircleSpan, CircleExtension and Quadratic. The Comparator permits propext, Quot.sound, Classical.choice. A source or syntax check alone never counts as proof acceptance.

## II. Circle geometry and quadratic isolators

A nondegenerate circle intersects a nontrivial line in at most two real points: replacing the line by z=z0+t v in norm(z-c)^2=R^2 produces a real quadratic in t with strictly positive leading coefficient norm(v)^2. Therefore **no three distinct circular points are collinear**, and three already affinely span the plane.

Choose five distinct points a0,...,a4. For each i partition the other four indices into pairs (j,k) and (l,m). Their secant-line equations L_jk and L_lm vanish at the corresponding pair. Set Q_i(z)=L_jk(z)*L_lm(z). Then Q_i(aj)=0 for j≠i and Q_i(ai)≠0 since no three are collinear. Normalizing E_i=Q_i/Q_i(ai) gives exact Kronecker interpolation: E_i(aj)=1 if i=j and 0 otherwise.

The coefficients lie in F=Q(all point coordinates), even for irrational points, because lines and the nonzero normalizer use only rational field operations on the coordinates. Consequently quadratic evaluation on the six monomials 1,x,y,x²,xy,y² maps onto F^5, and its five rows are independent over F. The source's 9 ordered augmented quadratic monomials include the six, so those five rows are also independent. Sphericity, full affine span and this field-relative independence meet the publisher's sufficient criterion. **The deep sufficient criterion is part of the original publisher proof, not a new theorem proved by enumerating rational examples.**

For 1≤s<5, positive-radius circles contain infinitely many distinct points by stereographic parametrization. Extend the given set to five distinct points and restrict any monochromatic congruent copy to the original s labels. At radius zero, injectivity forces the singleton case, which is trivially Ramsey. This covers every exact comparator hypothesis.

## III. General rank insight and a counterexample to an invalid inference

For distinct points on a genuine circle the degree≤2 polynomial evaluation matrix has rank min(n,5). When n≤5, extend to five and restrict independent rows. When n≥5, five rows are independent; the nonzero circle equation x²+y²-2c_x*x-2c_y*y+(norm(c)^2-R²) vanishes at every point, giving the upper bound rank≤5. For n≥3, the center and squared radius belong to the coordinate field by solving the two linear equations obtained by subtracting the circle equations at three noncollinear points.

**A six-point circular row matrix necessarily has dependent rows, but row independence is sufficient rather than necessary for being Ramsey. A six-point row-rank failure is NOT a non-Ramsey witness.**

Independent exact rational example: choose center (2/3,-3/4), radius 5/2, and stereographic parameters (-3,-2,-1,0,2,3), giving six distinct rational nodes. Their evaluation rank is five. Nonetheless the coordinate field is exactly Q and its tensor product over Q identifies with Q. The matrix with diagonal (c_x²+c_y²-R²,1,1) and entries P_01=P_10=-c_x, P_02=P_20=-c_y and other off-diagonals zero has spatial block I2 and evaluates to the circle equation at every node, **in the tensor field itself**. By the publisher's CP71 field criterion this six-point rational set is Ramsey. The source's separate nine-point algebraically independent configuration remains outside this argument; rational and transcendental coordinate fields are not interchangeable.

More generally, any finite distinct **rational-coordinate** subset of a genuine plane circle is Ramsey: for ≥3 points the circle center is rational, so the same matrix over Q certifies the tensor criterion; 1- and 2-point cases are trivial or CP71's established special case. This is a mathematical consequence of the source classification, not a claim of original priority.

## IV. Comprehensive bounded diagnostic and negative controls

The stdlib-only CP73 engine constructs exact rational quadratic isolators and a nonzero 5×5 minor for a concrete five-node offset circle; it checks 252 different five-node subsets of a 10-point rational circle, with 6,300 exact Kronecker evaluations. The 35 adversarial tests check circle radii, noncollinearity, determinant/rank, point identity, stereographic recovery, wrong tensor entries, repeated points, five collinear points with rank three, incorrect original-scale dilations, and the false conclusion drawn from six-node quadratic dependence. No floating-point tolerances are accepted.

An irregular five-point configuration with a trivial distance-automorphism group satisfies the circle theorem; this shows it need not satisfy CP72's transitivity hypothesis. Transitivity and the circle-five theorem are genuinely distinct comparator results.

No finite enumeration proves a statement about every real coordinate and every coloring. The conventional interpolation proof and original verified source solution carry the universal mathematical content; the bounded computations are falsification aids.

## V. Proof execution, attribution, and stopping rule

The research Github Action separately authenticates 15 original Git blobs, checks exact theorem hypotheses, runs all 35 tests and retains code, results and SHA256 receipts. The different full formal GitHub Action uses pinned Lean 4.34.1, Mathlib, Comparator and the exact selected circle theorem. Positive formal credit is allowed ONLY on genuine terminal PASS_SELECTED_THEOREM together with comparator/kernel acceptance, observed allowed axioms and independent receipt integrity.

CP71 classification and CP72 transitive subset were previously accepted as individual source-selected theorems. CP73 is the next distinct Family172 target. The four remaining comparator targets are not credited in CP73. No whole-family certification, no independent external human certification, no automatic main-branch merge, and no CBI/TBC/Mac writes are authorized.

**After CP73: stop, present the audited download to the user, and do not begin CP74 without review.**
