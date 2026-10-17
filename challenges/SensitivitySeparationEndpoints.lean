import ComparatorChallenges.SensitivitySeparation

namespace OAI

noncomputable section
open scoped Classical

namespace Paper320

theorem unbounded_quadratic_separation (C : ℝ) (hC : 0 < C) :
    ∃ (n : ℕ) (f : (Fin n → Bool) → Bool),
      0 < n ∧ f (fun _ => false) = false ∧
      (∃ x y : Fin n → Bool, f x ≠ f y) ∧
      C * (sensitivity f : ℝ) ^ 2 < (blockSensitivity f : ℝ) := by
  sorry

theorem fixed_power_separation :
    ∃ α : ℝ, 2 < α ∧
      ∃ (n : ℕ → ℕ) (F : ∀ m : ℕ, (Fin (n m) → Bool) → Bool),
        (∀ m : ℕ, 1 ≤ m →
          0 < n m ∧ F m (fun _ => false) = false ∧
          (∃ x y : Fin (n m) → Bool, F m x ≠ F m y) ∧
          (sensitivity (F m) : ℝ) ^ α ≤
            (blockSensitivityAt (F m) (fun _ => false) : ℝ)) ∧
        Filter.Tendsto
          (fun m : ℕ => (blockSensitivityAt (F m) (fun _ => false) : ℝ))
          Filter.atTop Filter.atTop := by
  sorry

end Paper320

end

end OAI
