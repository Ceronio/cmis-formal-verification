# CP74 — Independent review of the twelve-point spherical non-Ramsey configuration

**CMIS Phase 2 · Family 172 · 28 October 2026 · Standalone checkpoint**

**Original source:** OpenAI Mathematics, immutable commit fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb; Section 7 of *A classification of finite Euclidean Ramsey configurations*, Comparator challenge **OAI.GrahamSpherical.full_main** and its imported Lean proof modules. This document identifies independently checked mathematics separately from publisher provenance, actual Lean theorem acceptance and external certification. No new priority or authorship of the publisher's result is claimed.

## 1. Exact original theorem; do not narrow the scope

The original theorem is a conjunction of four claims about a specific twelve-point set \(X\subset\mathbb R^2\):

1. \(|X|=12\).
2. Every point has Euclidean norm exactly 1.
3. In **every** positive ambient dimension \(n\), there exists an **arbitrary** 50-coloring \(c:\mathbb R^n\to\{0,\ldots,49\}\) containing **no monochromatic distance-preserving copy** of \(X\).
4. Thus \(X\) is not Euclidean Ramsey.

The Lean version explicitly uses an isometry of the literal witness subtype, not a weakened affine-form assumption. Its 50-color statement is stronger than merely deducing non-Ramseyness using an unspecified finite number of colors. The challenge contains a placeholder; actual proof credit requires the separate original pinned Lean/Comparator execution.

## 2. Exact twelve-point witness and distinctness

Let
\[
t=\sum_{k=1}^\infty 10^{-k!},\qquad
u=(1-t^2)/(1+t^2),\qquad v=2t/(1+t^2).
\]
The source establishes \(11/100<t<12/100\) and transcendence of \(t\) over \(\mathbb Q\) by a Liouville argument. Thus \(0<v<u<1\) and \(u^2+v^2=1\).

Let \(Q=\{(1,0),(-1,0),(0,1),(0,-1)\}\), let \(R_+\) rotate the plane by \(\theta=2\arctan t\), and let \(R_-\) rotate by \(-\theta\). Define
\[
X=Q\;\cup\;R_+Q\;\cup\;R_-Q.
\]
The four base points have one coordinate zero; all eight rotated points have two nonzero coordinates. Within the rotated blocks, their coordinate magnitudes are \((u,v)\) or \((v,u)\) and the signs distinguish each point. Since \(0<v<u<1\), no two of the twelve points coincide. Orthogonality of \(R_\pm\), equivalently \(u^2+v^2=1\), proves every point lies on the unit circle.

**Negative control:** setting \(t=0\) collapses three squares to the same four points. The strict positive parameter bound and injectivity are essential, not decoration.

## 3. A polynomial identity proof of the three weighted moments

Index the blocks \(R_+Q\), \(R_-Q\), and \(Q\) and assign weights \(+1,+1,-2\), respectively. Each square satisfies
\(\sum_{q\in Q}q=0\) and \(\sum_{q\in Q}qq^T=2I_2\).

Let \(\delta=((1+t^2)/2)\,d/dt\) act on the rational function field \(\mathbb Q(t)\). The elementary quotient-rule identities are
\[
\delta u=-v,\qquad \delta v=u.
\]
These are **algebraic derivation identities**, not analytic differentiation of the factorial series as a function of a variable. The transcendence of the fixed real \(t\) identifies its coordinate field with a rational-function field, allowing the derivation to be defined there and then extended to the reals in the publisher's source.

For each of the twelve points, write \(p_i=(1,x_i,y_i)^T\) and \(\delta p_i=(0,\delta x_i,\delta y_i)^T\). The blocks have rotations \(\delta R_+=R_+J\), \(\delta R_-=-R_-J\), and \(\delta R_0=0\), where \(J=\begin{pmatrix}0&-1\\1&0\end{pmatrix}\). Direct matrix expansion gives
\[
\sum_i\beta_i p_ip_i^T=0,\qquad
\sum_i\beta_i(\delta p_i)p_i^T=0,\qquad
\sum_i\beta_i(\delta p_i)(\delta p_i)^T
=\operatorname{diag}(0,4,4).
\]

The attached exact polynomial engine does **not** infer these identities from floating-point samples. It clears the common denominator \((1+t^2)^2\), expands all 27 entries over \(\mathbb Z[t]\), and checks the coefficient vectors equal the zero or required target polynomial. The independent SymPy replay recalculates the expressions without importing that polynomial engine.

The derivation identity underlying the source's tensor obstruction follows from the Leibniz rule and these three moment equalities; replacing pre-multiplication tensor equations by an ordinary sphere equation would be invalid.

## 4. Copy-invariant derivation energy equals eight

The publisher's full Lean proof also establishes the following dimension-free identity for **every actual isometric copy**, which is considerably stronger than checking the original twelve points in the plane.

Let \(D:\mathbb R\to\mathbb R\) be a real algebraic derivation with \(Dt=(1+t^2)/2\), whose existence is established in the pinned source using a transcendence basis. Given an isometric placement of \(X\) into \(\mathbb R^n\), its affine-span Gram matrix allows an orthonormal pair of column vectors \(A,B\in\mathbb R^n\) and a translation \(z\) such that each image point is
\[
z+x_iA+y_iB.
\]
Define the nonnegative derivation energy
\[
e(w)=\sum_{j=1}^n (D(w_j))^2.
\]
For each ambient coordinate \(j\), the derivation expands to
\[
D(z_j)+D(A_j)x_i+D(B_j)y_i+A_j\,D(x_i)+B_j\,D(y_i).
\]
The three weighted moments cancel all translation, ordinary-coordinate and mixed terms in the weighted square. What remains is \(4(A_j^2+B_j^2)\). Summing over coordinates yields
\[
\boxed{\sum_{i=1}^{12}\beta_i e(\text{copy}(x_i)) =
4(\|A\|^2+\|B\|^2)=8.}
\]
This reproduces the published mathematical mechanism. The universal claim depends on the source's theorem that any isometric copy admits the stated affine placement and on the existence of the global real derivation. The finite polynomial tests alone do not establish either noncomputable assertion.

## 5. Independent derivation of the exact fifty-color obstruction

The pinned formalization uses
\[
c_{50}(w)=\left\lfloor3e(w)\right\rfloor\bmod50.
\]
Suppose all twelve images of a copy have the same residue. Define
\(S=\sum_i\beta_i\lfloor3e_i\rfloor\), with eight \(+1\) coefficients and four \(-2\) coefficients. Since \(\sum_i\beta_i=0\), equal residues force \(S\equiv0\pmod{50}\).

Write \(\varepsilon_i=3e_i-\lfloor3e_i\rfloor\), where \(0\le\varepsilon_i<1\). The energy identity gives
\[
 S=24-\sum_{\beta_i=+1}\varepsilon_i
        +2\sum_{\beta_i=-2}\varepsilon_i .
\]
There are eight errors of the first kind and four of the second, hence **strictly**
\[
16<S<32.
\]
No integer strictly between 16 and 32 is divisible by 50. Contradiction. Therefore no monochromatic isometric copy exists under this colouring in any positive dimension.

The exact color map uses the source's globally defined derivation \(D\), so this is not a numerically evaluable color map for arbitrary real coordinates. Nonetheless it is a mathematically legitimate nonconstructive coloring in the source's set-theoretic context.

By choosing 50 colors for every dimension we contradict the exact \(\forall r\,\exists n\,\forall c\) Ramsey quantifier at \(r=50\); thus \(X\) is not Euclidean Ramsey.

## 6. Additional conditional result: a 16-color strengthening

The same fixed copy-invariant energy identity admits a **shorter 16-color argument**, which is mathematically separate from the original selected 50-color theorem. Set
\[
c_{16}(w)=\lfloor e(w)\rfloor\bmod16.
\]
If a copy were monochromatic, \(S'=\sum_i\beta_i\lfloor e_i\rfloor\) would be a multiple of 16. Writing \(\eta_i=e_i-\lfloor e_i\rfloor\in[0,1)\), the same weighted energy identity gives
\[
S'=8-\sum_{+}\eta_i+2\sum_{-}\eta_i.
\]
Therefore **\(0<S'<16\)**, impossible for a multiple of 16. Consequently, *assuming the source's universally established derivation and energy invariant*, one can use 16 colours instead of 50 to avoid all monochromatic copies of this witness.

This is a conventional deductive sharpening of the source's explicit invariant. It has **not** undergone a separate Lean kernel verification or independent mathematical peer review. Do not count it as another accepted original Comparator theorem, a proved independent manuscript, a discovery of global novelty, or additional Family172 certification.

The bounded code checks this arithmetic implication using 900 distinct nonnegative rational energy vectors that exactly satisfy the weighted identity and includes a negative control with all-zero energies, which fails the required invariant. Those experiments corroborate the algebra but cannot replace the universal proof.

## 7. Parameter evidence and limitations

The source's literal factorial series starts with \(10^{-1}+10^{-2}+10^{-6}+10^{-24}+\cdots\); **it is not the variant that starts at \(10^{-2}\)**. Strict bounds and transcendence are proved in its exact Lean module using Mathlib's Liouville-number theorem, not by a floating-point approximation.

The polynomial computation uses rational test parameters in \([0.11,0.12)\) to check the geometry, but rational values **do not satisfy the transcendence hypothesis**. The source's 50-color theorem is not inferred from those sample points. The original all-dimensions avoiding coloring is noncomputable in the literal sense, because the real derivation is chosen via abstract field theory.

Do not substitute the nine-point algebraically-independent example from CP75 for the literal twelve-point set in CP74. They are separate original results.

## 8. Verification ladder, provenance, and release policy

**Independent exact identities:** CP74 test suite, exact integer polynomials, 900 rational energy-vectors, boundary and scale negative controls, independent SymPy arithmetic replay.

**Publisher provenance:** 25 original source blobs pinned to one immutable OpenAI Mathematics commit. The GitHub research workflow recomputes Git blob SHA-1 and SHA-256 and stores the exact publisher source bytes.

**Full theorem verification:** A separate protected GitHub workflow uses the established pin-checked Lean 4.34.1 / Mathlib / Comparator harness. The only selected original theorem is **OAI.GrahamSpherical.full_main**. The workflow must return **PASS_SELECTED_THEOREM**, Comparator success, default-kernel acceptance and an allowed axiom report. A success on Python or source audits alone does not grant selected-theorem credit.

**Family accounting:** CP71, CP72, CP73 are three historical selected statements. CP74 adds a fourth only if its own formal receipt passes independently. The other three original Family172 Comparator targets are not credited. Whole-family verification and external human certification remain separate.

**Repository/privacy:** Only public mathematical research files go to the isolated CP74 review branch and unmerged draft PR. There are no writes to main, CBI, TBC, the user's Mac or any canonical storage. GitHub artifacts expire; the original downloaded proof receipts must be preserved within the verified CP74 ZIP.

**Stop after CP74:** Present one self-contained package with Word, Excel, original GitHub receipts and reproducible scripts. **Do not start CP75 until user reviews CP74.**
