# CMIS CP73 standalone research checkpoint

**Family 172 — nonempty sets of at most five distinct points on a circle.** 27 October 2026. Pinned publisher source: OpenAI Mathematics commit fd4aeeb2ee4fc729c18d98444fed42fd0529eeeb.

### Exact theorem and scope

- Formal target: **OAI.EuclideanRamsey.CircleConsequence.at_most_five_circle_points_ramsey**.
- Nonempty s≤5, injective planar indexing, exists center and common radius; conclusion is original-scale Euclidean Ramsey for arbitrary finite colorings.
- CP71 and CP72 are previous accepted selected targets; CP73 is only the third of seven Family172 comparator statements.
- External human certification remains deferred; the other four targets do not gain credit.
- This branch is a standalone public research review, not a canonical merge or formal publication.

### Files

- **INDEPENDENT_MATHEMATICAL_NOTE.md** — conventional five-point interpolation argument, exact field/rank reasoning, six-point rational countercheck to a false inference.
- **circle_math.py** — exact Fraction-based quadratic isolators, determinant, rank, rational tensor examples, 252 five-node subset checks.
- **test_cp73.py** — 35 adversarial exact mathematical tests.
- **SOURCE_PINS.json** — exact 15 original publisher Git blobs, module and allowed-axiom metadata.
- **verify_pinned_sources.py** — read-only original SHA1 blob reconstruction, original theorem statement/hypothesis/source checks.
- Two GitHub workflows: bounded reproducible research and full exact original Lean/Comparator selected theorem. Full proof success is not claimed unless the second workflow really passes.

### Reproduce

Run from the repository root:

    python3 research/cp73/test_cp73.py -v
    python3 research/cp73/circle_math.py --output research/cp73/receipt/MATH_AUDIT.json
    GITHUB_TOKEN=READ_ONLY_TOKEN python3 research/cp73/verify_pinned_sources.py --output-dir research/cp73/receipt

The GitHub receipts expire under Actions retention; exact receipt copies go into the user's standalone CP73 download. No GitHub merge to main, no CBI/TBC/local project edits.

**Stop before CP74 until user reviews and authorizes continuing.**
