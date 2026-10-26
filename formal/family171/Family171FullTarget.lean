import OAI.Combinatorics.Ramsey.Hypercube

namespace CMIS
namespace Family171

open OAI.HypercubeRamsey

/-- The exact full-headline target reviewed by CMIS for Family 171. -/
def FullHypercubeRamseyLinearBound : Prop :=
  ∃ C : ℝ, 0 < C ∧ ∀ n : ℕ,
    (ramseyNumber (cube n) : ℝ) ≤ C * (2 : ℝ) ^ n

/-- The CMIS target is definitionally the source manuscript's linear bound. -/
theorem fullTarget_iff_sourceStatement :
    FullHypercubeRamseyLinearBound ↔
      ∃ C : ℝ, 0 < C ∧ ∀ n : ℕ,
        (ramseyNumber (cube n) : ℝ) ≤ C * (2 : ℝ) ^ n := by
  rfl

/-- The formal interface currently present in the pinned source is the negation of the full target. -/
def ExistingNegatedInterface : Prop := ¬ FullHypercubeRamseyLinearBound

theorem negatedInterface_iff_sourceHypothesis :
    ExistingNegatedInterface ↔
      ¬ ∃ C : ℝ, 0 < C ∧ ∀ n : ℕ,
        (ramseyNumber (cube n) : ℝ) ≤ C * (2 : ℝ) ^ n := by
  rfl

#check OAI.HypercubeRamsey.counterexample_sequence_of_not_linear
#print axioms CMIS.Family171.fullTarget_iff_sourceStatement
#print axioms CMIS.Family171.negatedInterface_iff_sourceHypothesis

end Family171
end CMIS
