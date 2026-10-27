# CMIS Phase 2 — CP72 standalone independent mathematical review

**Family 172 — transitive Euclidean configurations and nonempty subsets.**

**Scope:** ONE original selected formal comparator, plus independently reasoned conventional orbit proofs, exact group calculations, tensor witnesses and negative controls. CP73 HOLD until user has reviewed the CP72 ZIP.

## Important deliverables

- `INDEPENDENT_MATHEMATICAL_NOTE.md` — precise hypotheses and quantifiers, exact centroid-sphere proof, uniform orbit proof, affine isometry extension and symmetric tensor-field witness. Carefully identifies reliance on the CP71 full classification result.
- `transitive_math.py` — all-integer and rational finite distance-automorphism and group checks; exact Q[X,Y] tensor witness, sampled finite configurations, negative controls.
- `test_cp72.py` — 29 adversarial independent mathematical checks for the bounded code.
- `SOURCE_PINS.json` — nine immutable publisher files: scope, original comparator, configuration, solution, previous classification dependency, manuscript introduction, tensor section, consequences proof and Apache licence.
- `verify_pinned_sources.py` — recomputes publisher Git blob SHA-1 identities and audits exact theorem hypotheses, manuscript scope and permitted axioms.
- GitHub Actions workflows under `.github/workflows/` — (a) quick research+original-source audit and (b) protected full source-pinned Lean/Comparator theorem run.

## Exact original theorem

`OAI.EuclideanRamsey.TransitiveConsequence.subset_of_finite_transitive_ramsey`

Requires `s>0`, injective subconfiguration and superset point indices, transitive **distance-preserving** permutations of the superset, and `range(a) ⊆ range(y)`. Proves `Ramsey a` under all finite colourings at original distance scale, with ambient dimension allowed to depend on the number of colours.

## Scope and trust boundary

- A green bounded research action authenticates source identities and executes exact finite tests; it is NOT the original universal theorem proof.
- A green formal source-pinned comparator job can certify the **exact selected Lean theorem** only; it cannot automatically validate the other five Family 172 comparator results outstanding after CP71 and CP72.
- External mathematical certification remains deferred; do not claim new authorship of the source result.
- Leave `main` and the separate CP71 review pull request unchanged. No merge, CBI or TBC writes, or publication.
- GitHub artifacts expire after their retention period. Final CP72 download includes original receipt bytes to preserve evidence independent of Action retention.

## Rerun public tests

```bash
python3 research/cp72/test_cp72.py -v
python3 research/cp72/transitive_math.py --output research/cp72/receipt/MATH_AUDIT.json
python3 research/cp72/verify_pinned_sources.py --output-dir research/cp72/receipt
```

**Next checkpoint:** CP73 is not started until CP72 is downloaded and reviewed.
