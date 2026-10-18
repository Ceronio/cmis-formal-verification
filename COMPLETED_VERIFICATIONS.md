# CMIS completed-verification register

**Living register — update this file as new evidence is completed.**

Last updated: **18 October 2026**

## Current totals

| Measure | Count |
|---|---:|
| Selected formal theorem declarations passed | **42** |
| Declarations supporting complete family validation | **36** |
| Supporting or partial-scope declarations | **6** |
| Families validated at recorded pure-mathematical scope | **18** |
| Family reviews complete but not validated | **9** |
| Total resolved family reviews | **27** |
| Current execution holds | **1** |

> A theorem receipt and a family validation are not the same unit. The 42 declarations are evidence components across 22 families. Eighteen families have complete recorded mathematical-scope validation; four additional families have successful supporting or partial theorem receipts without whole-family validation.

## Validated families

| Family | Mathematical work | Verified declarations | GitHub run(s) | Status |
|---:"|---|---:|---|---|
| **1005** | Irrationality of Catalan’s constant | **1** | [39069346447](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39069346447) | Validated — recorded pure-mathematical scope |
| **132** | A counterexample to the quadratic sensitivity conjecture | **3** | [39065819244](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39065819244)<br>[39071193887](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39071193887) | Validated — recorded pure-mathematical scope |
| **133** | The complexity of Weisfeiler–Leman refinement | **4** | [39071880237](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39071880237)<br>[39074816714](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39074816714)<br>[39074836683](https://github.com/Ceronio/cmis-formal-verification/actions/runs/390748366839<br>[39074859446](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39074859446) | Validated — recorded pure-mathematical scope |
| **134** | Generalized star height at most three | **1** | [39077024941](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39077024941) | Validated — recorded pure-mathematical scope |
| **135** | Sharp homogeneous depth-five complexity of matrix products | **1** | [39077369934](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39077369934) | Validated — recorded pure-mathematical scope |
| **137** | One-tape time simulation in two-fifths-power space | **2** | [39077800526](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39077800526) | Validated — recorded pure-mathematical scope |
| **139** | Subpolynomial queries for log-concave sampling | **1** | [39078979726](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39078979726) | Validated — recorded pure-mathematical scope |
| **140** | Memory–sample lower bounds for noiseless Gaussian regression | **8** | [39079350083](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39079350083) | Validated — recorded pure-mathematical scope |
| **143** | Uniform limit-cycle bounds in Hilbert’s sixteenth problem | **1** | [39113799488](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39113799488) | Validated — recorded pure-mathematical scope |
| **144** | Banach’s simple Lebesgue-spectrum problem | **1** | [39113828752](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39113828752) | Validated — recorded pure-mathematical scope |
| **145** | Rokhlin’s multiple-mixing problem | **1** | [39113856845](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39113856845) | Validated — recorded pure-mathematical scope |
| **146** | Sinai���s positive-entropy conjecture for the standard map | **3** | [39113889697](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39113889697) | Validated — recorded pure-mathematical scope |
| **148** | The dimension formula for self-similar measures on the line | **3** | [39127975290](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39127975290) | Validated — recorded pure-mathematical scope |
| **151** | A C1 counterexample to Shub’s entropy conjecture | **1** | [39127995324](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39127995324) | Validated — recorded pure-mathematical scope |
| **155** | A counterexample to periodic tiling in dimension three | **1** | [39129543413](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129543413) | Validated — recorded pure-mathematical scope |
| **156** | Borsuk’s conjecture fails in dimension nine | **1** | [39129568496](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129568496) | Validated — recorded pure-mathematical scope |
| **158** | The Euclidean plane cannot be colored with five colors | **2** | [39129693771](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129693771) | Validated — recorded pure-mathematical scope |
| **160** | Superexponential van der Waerden numbers | **1** | [39129756059](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129756059) | Validated — recorded pure-mathematical scope |

## Complete reviews without whole-family validation

| Family | Mathematical work | Successful supporting targets | Final reason |
|---:"|---|---:|---|
| **136** | The quasilinear PCP-for-PPAD conjecture | **0** | Central conjecture proposition remains unproved; only a partial module build was reproduced. |
| **138** | Subset Sum in O(2z0.49n) time | **0** | Available declarations do not match the original O(2z0.49n) time claim. |
| **147** | The near-boundary Birkhoff conjecture | **0** | Exact source contract reviewed, but no matching Lean/Comparator target was available. |
| **149** | Permanence for weakly reversible reaction networks | **1** | Verified persistence theorem is narrower than the family’s common absorbing-set claim. |
| **150** | Weak mixing of irrational triangular billiards | **1** | Verified theorem proves ergodicity, not the headline weak-mixing claim. |
| **152** | Zero entropy does not guarantee a smooth positive-volume model | **1** | Verified theorem supplies finite entropy, not the headline zero-entropy result. |
| **153** | Arithmetic classification of Bernoulli convolutions | **0** | Exact source contract reviewed, but no matching formal target was available. |
| **154** | Pointwise multiple ergodic averages for mixing transformations | **0** | Exact source contract reviewed, but no matching formal target was available. |
| **157** | Counterexamples to the Hadwiger and Colin de Verdière conjectures | **3** | Verified targets cover ordinary and list-Hadwiger results; fractional-chromatic and Colin de Verdière strengthenings remain outside. |

## All 42 completed formal theorem declarations

| # | Family | Lean declaration | Scope credit | Evidence run |
|---:|---:"|---|---|---:|
| 1 | 005 | `OAI.InternalCatalan.catalan_irrational` | Family-validating | [39069346447](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39069346447) |
| 2 | 132 | `OAI.Paper320.quantitative_separation` | Family-validating | [39065819244](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39065819244) |
| 3 | 132 | `OAI.Paper320.unbounded_quadratic_separation` | Family-validating | [39071193887](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39071193887) |
| 4 | 132 | `OAI.Paper320.fixed_power_separation` | Family-validating | [39071193887](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39071193887) |
| 5 | 133 | `OAI.ParityWL.parity_reduction` | Family-validating | [39071880237](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39071880237) |
| 6 | 133 | `OAI.WLIdentification.main` | Family-validating | [39074816714](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39074816714) |
| 7 | 133 | `OAI.WLTime.unconditional_time_lower_bound` | Family-validating | [39074836683](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39074836683) |
| 8 | 133 | `OAI.VariableWL.main` | Family-validating | [39074859446](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39074859446) |
| 9 | 134 | `OAI.GeneralizedStarHeight.main` | Family-validating | [39077024941](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39077024941) |
| 10 | 135 | `OAI.Problem335.main` | Family-validating | [39077369934](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39077369934) |
| 11 | 137 | `OAI.Fifths.Single.capped` | Family-validating | [39077800526](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39077800526) |
| 12 | 137 | `OAI.Fifths.Single.unknown` | Family-validating | [39077800526](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39077800526) |
| 13 | 139 | `OAI.LogConcaveSampling.exact_source_main` | Family-validating | [39078979726](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39078979726) |
| 14 | 140 | `OAI.MemoryPrecision.main` | Family-validating | [39079350083](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39079350083) |
| 15 | 140 | `OAI.NoiselessRegression.main` | Family-validating | [39079350083](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39079350083) |
| 16 | 140 | `OAI.PosteriorReplicas.source_main` | Family-validating | [39079350083](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39079350083) |
| 17 | 140 | `OAI.RepeatedLocalization.FiniteEntropy.finite_expected_regularization` | Family-validating | [39079350083](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39079350083) |
| 18 | 140 | `OAI.RepeatedLocalization.repeated_localization` | Family-validating | [39079350083](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39079350083) |
| 19 | 140 | `OAI.ProjectionMoments.main` | Family-validating | [39079350083](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39079350083) |
| 20 | 140 | `OAI.CurrentProjection.mixedMomentMain` | Family-validating | [39079350083](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39079350083) |
| 21 | 140 | `OAI.SubsphereCurrent.full_current_main_scope` | Family-validating | [39079350083](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39079350083) |
| 22 | 143 | `OAI.QuinticLienard.main` | Family-validating | [39113799488](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39113799488) |
| 23 | 144 | `OAI.ThreeTorus.simple_lebesgue_spectrum` | Family-validating | [39113828752](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39113828752) |
| 24 | 145 | `OAI.Rokhlin.mixing_all_finite_orders` | Family-validating | [39113856845](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39113856845) |
| 25 | 146 | `OAI.StandardMapEntropy.main_components` | Family-validating | [39113889697](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39113889697) |
| 26 | 146 | `OAI.StandardMapEntropy.main_entropy` | Family-validating | [39113889697](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39113889697) |
| 27 | 146 | `OAI.StandardMapEntropy.main_entropy_complete` | Family-validating | [39113889697](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39113889697) |
| 28 | 148 | `OAI.EntropyRateDimension.entropy_rate_dimension` | Family-validating | [39127975290](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39127975290) |
| 29 | 148 | `OAI.EntropyRateDimension.Extensions.homogeneous_dimension_direct` | Family-validating | [39127975290](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39127975290) |
| 30 | 148 | `OAI.CorSetReference.cor_set` | Family-validating | [39127975290](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39127975290) |
| 31 | 149 | `OAI.Problem326.global_bounded_persistent_solution` | Supporting only | [39128187459](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39128187459) |
| 32 | 150 | `OAI.TriangularBilliards.irrational_triangle_billiard` | Supporting only | [39128206649](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39128206649) |
| 33 | 151 | `OAI.Problem340.exists_C1_entropy_counterexample` | Family-validating | [39127995324](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39127995324) |
| 34 | 152 | `OAI.SmoothObstruction.main` | Supporting only | [39128229929](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39128229929) |
| 35 | 155 | `OAI.PeriodicTilingThree.periodic_tiling_counterexample_and_minimality` | Family-validating | [39129543413](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129543413) |
| 36 | 156 | `OAI.BorsukNine.main_theorem` | Family-validating | [39129568496](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129568496) |
| 37 | 157 | `OAI.HadwigerCounterexample.exists_counterexamples` | Partial family coverage | [39129637021](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129637021) |
| 38 | 157 | `OAI.HadwigerCounterexample.not_hadwiger_conjecture` | Partial family coverage | [39129637021](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129637021) |
| 39 | 157 | `OAI.LinearListHadwiger.main_theorem` | Partial family coverage | [39129637021](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129637021) |
| 40 | 158 | `OAI.EuclideanFiveColor.no_proper_five_coloring` | Family-validating | [39129693771](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129693771) |
| 41 | 158 | `OAI.Problem160.properColoring_seven` | Family-validating | [39129693771](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129693771) |
| 42 | 160 | `OAI.QuantitativeVanDerWaerdeen.uniform_lower_bound` | Family-validating | [39129756059](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129756059) |

## Current execution hold

| Family | Target | Run | Disposition |
|---:|---|---:|---|
| **159** | `OAI.Erdos3.manuscriptReciprocalProgressionTheorem` | [39129728984](https://github.com/Ceronio/cmis-formal-verification/actions/runs/39129728984) | Cancelled at the 350-minute workflow timeout during the Lean build. No Comparator or kernel verdict; excluded from completed totals. |

## Update rule

When adding a result:

1. Preserve the exact family claim and source pin.
2. Add the exact theorem declaration and workflow run.
3. Record whether it is family-validating, supporting-only, or partial-family evidence.
4. Upgrade a family only when the verified target set matches the complete recorded family scope.
5. Record timeouts, build holds, mismatches and non-validations without deleting them.
