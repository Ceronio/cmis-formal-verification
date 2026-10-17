#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT=$(pwd)
RECEIPT="$ROOT/cmis_receipt"
PROJECT="$ROOT/.cmis-work/openai-math/lean"
TOOLS="$ROOT/.cmis-tools"

bash "$ROOT/scripts/run_openai_math_selected_target.sh"

[[ -f "$RECEIPT/FINAL_STATUS.txt" && "$(cat "$RECEIPT/FINAL_STATUS.txt")" == PASS_SELECTED_THEOREM ]] || {
  echo "Base Comparator run did not pass." >&2
  exit 2
}

LEAN_HOME=$(find "$TOOLS" -maxdepth 1 -mindepth 1 -type d -name 'lean-*-linux' -print -quit)
[[ -n "$LEAN_HOME" && -x "$LEAN_HOME/bin/lake" ]] || {
  echo AXIOM_POSTCHECK_HOLD > "$RECEIPT/FINAL_STATUS.txt"
  echo "Admitted Lean/Lake toolchain not found for second theorem post-check." >&2
  exit 2
}
export PATH="$LEAN_HOME/bin:$TOOLS/bin:$PATH"

cat > "$RECEIPT/PostCheckAxiomsAll.lean" <<'EOF'
import OAI.Computability.SpaceSimulation.Main
#print axioms OAI.Fifths.Single.capped
#print axioms OAI.Fifths.Single.unknown
EOF

set +e
(
  cd "$PROJECT"
  lake env lean "$RECEIPT/PostCheckAxiomsAll.lean" \
    > "$RECEIPT/07_all_axioms.stdout" 2> "$RECEIPT/07_all_axioms.stderr"
)
AXIOM_RC=$?
set -e
printf '%s\n' "$AXIOM_RC" > "$RECEIPT/07_all_axioms.exit_code"
if [[ "$AXIOM_RC" -ne 0 ]]; then
  echo AXIOM_POSTCHECK_HOLD > "$RECEIPT/FINAL_STATUS.txt"
  exit "$AXIOM_RC"
fi

# Require both declaration names to appear in the post-check output.
grep -F 'OAI.Fifths.Single.capped' "$RECEIPT/07_all_axioms.stdout" >/dev/null || {
  echo AXIOM_POSTCHECK_HOLD > "$RECEIPT/FINAL_STATUS.txt"
  exit 4
}
grep -F 'OAI.Fifths.Single.unknown' "$RECEIPT/07_all_axioms.stdout" >/dev/null || {
  echo AXIOM_POSTCHECK_HOLD > "$RECEIPT/FINAL_STATUS.txt"
  exit 4
}

echo PASS_SELECTED_THEOREMS > "$RECEIPT/FINAL_STATUS.txt"
echo "PASS: Comparator accepted both one-tape simulation declarations; both axiom reports were produced."
