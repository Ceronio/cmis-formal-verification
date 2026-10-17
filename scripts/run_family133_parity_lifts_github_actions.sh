#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT=$(pwd)
RECEIPT="$ROOT/cmis_receipt"
ADMISSION_RECEIPT="$ROOT/cmis_admission_receipt"
TOOLS="$ROOT/.cmis-tools"
WORK="$ROOT/.cmis-work"
PROJECT="$WORK/openai-math/lean"
COMPARATOR_BIN="$WORK/comparator/.lake/build/bin/comparator"
EXPORTER_BIN="$WORK/comparator/.lake/packages/lean4export/.lake/build/bin/lean4export"
LANDRUN_BIN="$TOOLS/bin/landrun"

status_written=0
finalized=0
write_status() {
  mkdir -p "$RECEIPT"
  printf '%s\n' "$1" > "$RECEIPT/FINAL_STATUS.txt"
  status_written=1
}
finalize_exit() {
  rc=$?
  if [[ $finalized -eq 1 ]]; then
    exit "$rc"
  fi
  finalized=1
  trap - EXIT
  if [[ $status_written -eq 0 ]]; then
    write_status "UNCLASSIFIED_HOLD"
  fi
  {
    echo "exit_code=$rc"
    echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "$RECEIPT/98_exit.txt"
  find "$RECEIPT" -maxdepth 1 -type f ! -name '99_receipt_sha256.txt' -print0 \
    | sort -z | xargs -0 sha256sum > "$RECEIPT/99_receipt_sha256.txt"
  exit "$rc"
}
trap finalize_exit EXIT

required_env=(
  EXECUTION_MODE PARITY_CONFIG_BLOB PARITY_CHALLENGE_BLOB PARITY_SOLUTION_BLOB
  SELECTED_THEOREM
)
for name in "${required_env[@]}"; do
  [[ -n "${!name:-}" ]] || {
    write_status ENVIRONMENT_HOLD
    echo "Missing environment variable: $name" >&2
    exit 2
  }
done
case "$EXECUTION_MODE" in
  admission|full) ;;
  *) write_status ENVIRONMENT_HOLD; echo "Invalid execution mode" >&2; exit 2 ;;
esac

rm -rf "$RECEIPT" "$ADMISSION_RECEIPT"

# Reuse the audited pinned-environment bootstrap strictly in admission mode.
# This installs and identifies the exact toolchain, verifier sources, project
# checkout, dependency patches, cache and protected systemd/Landrun route.
ORIGINAL_MODE="$EXECUTION_MODE"
export EXECUTION_MODE=admission
bash "$ROOT/scripts/run_family132_github_actions.sh"
export EXECUTION_MODE="$ORIGINAL_MODE"

[[ -f "$RECEIPT/FINAL_STATUS.txt" ]] || { echo 'Admission receipt missing' >&2; exit 2; }
[[ "$(cat "$RECEIPT/FINAL_STATUS.txt")" == "ADMISSION_PASS" ]] || { echo 'Admission did not pass' >&2; exit 2; }
find "$RECEIPT" -maxdepth 1 -type f ! -name '99_receipt_sha256.txt' -print0 \
  | sort -z | xargs -0 sha256sum > "$RECEIPT/99_receipt_sha256.txt"
mv "$RECEIPT" "$ADMISSION_RECEIPT"
mkdir -p "$RECEIPT"
tar -czf "$RECEIPT/00_admission_receipt.tar.gz" -C "$ROOT" "$(basename "$ADMISSION_RECEIPT")"
sha256sum "$RECEIPT/00_admission_receipt.tar.gz" > "$RECEIPT/00_admission_receipt.sha256"

# The admitted subprocess cannot export PATH into this parent shell.
LEAN_HOME=$(find "$TOOLS" -maxdepth 1 -mindepth 1 -type d -name 'lean-*-linux' -print -quit)
[[ -n "$LEAN_HOME" && -x "$LEAN_HOME/bin/lake" ]] || {
  write_status ENVIRONMENT_HOLD
  echo 'Admitted Lean/Lake toolchain was not found.' >&2
  exit 2
}
export PATH="$LEAN_HOME/bin:$TOOLS/bin:$PATH"

exec > >(tee "$RECEIPT/01_parity_lifts.stdout") 2> >(tee "$RECEIPT/01_parity_lifts.stderr" >&2)

for path in "$PROJECT" "$COMPARATOR_BIN" "$EXPORTER_BIN" "$LANDRUN_BIN"; do
  [[ -e "$path" ]] || {
    write_status ENVIRONMENT_HOLD
    echo "Missing admitted path: $path" >&2
    exit 2
  }
done

check_blob() {
  local path=$1 expected=$2
  local actual
  actual=$(git -C "$WORK/openai-math" rev-parse "$OPENAI_MATH_COMMIT:$path")
  printf '%s %s\n' "$actual" "$path" >> "$RECEIPT/02_parity_lifts_blob_checks.txt"
  [[ "$actual" == "$expected" ]] || {
    write_status ENVIRONMENT_HOLD
    echo "Blob mismatch: $path" >&2
    exit 2
  }
}
check_blob lean/ComparatorChallenges/ParityLifts.json "$PARITY_CONFIG_BLOB"
check_blob lean/ComparatorChallenges/ParityLifts.lean "$PARITY_CHALLENGE_BLOB"
check_blob lean/OAI/Combinatorics/ParityLifts/Main.lean "$PARITY_SOLUTION_BLOB"

SYSTEMD_MODE=$(cat "$ADMISSION_RECEIPT/11_systemd_mode.txt")
{
  echo "selected_theorem=$SELECTED_THEOREM"
  echo "parity_config_blob=$PARITY_CONFIG_BLOB"
  echo "parity_challenge_blob=$PARITY_CHALLENGE_BLOB"
  echo "parity_solution_blob=$PARITY_SOLUTION_BLOB"
  echo "systemd_mode=$SYSTEMD_MODE"
  echo "comparator_bin=$COMPARATOR_BIN"
  echo "lean4export_bin=$EXPORTER_BIN"
  echo "landrun_bin=$LANDRUN_BIN"
  lean --version
  lake --version
  df -h /
} > "$RECEIPT/03_parity_lifts_execution_contract.txt"

if [[ "$ORIGINAL_MODE" == admission ]]; then
  write_status ADMISSION_PASS
  exit 0
fi

# TRUST ORDER: Comparator is the first operation that may compile the
# ParityLifts solution module after the fresh admitted environment is prepared.
INNER="$RECEIPT/run_parity_lifts_comparator_inner.sh"
cat > "$INNER" <<INNER_EOF
#!/usr/bin/env bash
set -Eeuo pipefail
export HOME='$HOME'
export PATH='$PATH'
export COMPARATOR_LANDRUN='$LANDRUN_BIN'
export COMPARATOR_LEAN4EXPORT='$EXPORTER_BIN'
cd '$PROJECT'
exec lake env '$COMPARATOR_BIN' ComparatorChallenges/ParityLifts.json
INNER_EOF
chmod 700 "$INNER"

set +e
if [[ "$SYSTEMD_MODE" == user ]]; then
  systemd-run --user --wait --pipe --collect \
    --property='RestrictAddressFamilies=~AF_UNIX' \
    --working-directory="$PROJECT" \
    "$INNER" > "$RECEIPT/04_comparator.stdout" 2> "$RECEIPT/04_comparator.stderr"
  COMPARATOR_RC=$?
else
  sudo systemd-run --wait --pipe --collect \
    --uid="$(id -un)" --gid="$(id -gn)" \
    --property='RestrictAddressFamilies=~AF_UNIX' \
    --working-directory="$PROJECT" \
    "$INNER" > "$RECEIPT/04_comparator.stdout" 2> "$RECEIPT/04_comparator.stderr"
  COMPARATOR_RC=$?
fi
set -e
printf '%s\n' "$COMPARATOR_RC" > "$RECEIPT/04_comparator.exit_code"
if [[ "$COMPARATOR_RC" -ne 0 ]]; then
  write_status COMPARATOR_HOLD
  echo 'ParityLifts Comparator did not succeed. No formal success claim is permitted.' >&2
  exit "$COMPARATOR_RC"
fi

grep -F 'Your solution is okay!' "$RECEIPT/04_comparator.stdout" > "$RECEIPT/05_comparator_success_marker.txt" || {
  write_status COMPARATOR_HOLD
  echo 'Comparator returned zero but the success marker was absent.' >&2
  exit 4
}

# Corroborating axiom report only after Comparator has accepted the selected target.
cat > "$RECEIPT/PostCheckAxioms.lean" <<'AXIOMS_EOF'
import OAI.Combinatorics.ParityLifts.Main
#print axioms OAI.ParityWL.parity_reduction
AXIOMS_EOF
(
  cd "$PROJECT"
  lake env lean "$RECEIPT/PostCheckAxioms.lean" \
    > "$RECEIPT/06_axioms.stdout" 2> "$RECEIPT/06_axioms.stderr"
)

write_status PASS_SELECTED_THEOREM
echo "PASS: Comparator accepted $SELECTED_THEOREM. CMIS must review the receipt before upgrading status."
