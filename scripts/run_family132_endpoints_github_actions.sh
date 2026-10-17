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
  EXECUTION_MODE SELECTED_THEOREMS ENDPOINT_CHALLENGE_SHA256 ENDPOINT_CONFIG_SHA256
)
for name in "${required_env[@]}"; do
  [[ -n "${!name:-}" ]] || { write_status ENVIRONMENT_HOLD; echo "Missing environment variable: $name" >&2; exit 2; }
done
case "$EXECUTION_MODE" in admission|full) ;; *) write_status ENVIRONMENT_HOLD; echo "Invalid execution mode" >&2; exit 2;; esac

rm -rf "$RECEIPT" "$ADMISSION_RECEIPT"

# Reuse the already-audited quantitative harness strictly in admission mode.
# It installs and pins the exact toolchain, verifier binaries, source tree,
# dependency patches, cache and protected systemd/Landrun environment without
# compiling the solution module manually.
ORIGINAL_MODE="$EXECUTION_MODE"
export EXECUTION_MODE=admission
export SELECTED_THEOREM="$SELECTED_THEOREMS"
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

# The admitted subprocess cannot export its PATH back to this parent shell.
# Rebind the exact Lean installation that the admission step created.
LEAN_HOME=$(find "$TOOLS" -maxdepth 1 -mindepth 1 -type d -name 'lean-*-linux' -print -quit)
[[ -n "$LEAN_HOME" && -x "$LEAN_HOME/bin/lake" ]] || {
  write_status ENVIRONMENT_HOLD
  echo 'Admitted Lean/Lake toolchain was not found.' >&2
  exit 2
}
export PATH="$LEAN_HOME/bin:$TOOLS/bin:$PATH"

exec > >(tee "$RECEIPT/01_endpoint.stdout") 2> >(tee "$RECEIPT/01_endpoint.stderr" >&2)

for path in "$PROJECT" "$COMPARATOR_BIN" "$EXPORTER_BIN" "$LANDRUN_BIN"; do
  [[ -e "$path" ]] || { write_status ENVIRONMENT_HOLD; echo "Missing admitted path: $path" >&2; exit 2; }
done

printf '%s  %s\n' "$ENDPOINT_CHALLENGE_SHA256" "$ROOT/challenges/SensitivitySeparationEndpoints.lean" | sha256sum -c -
printf '%s  %s\n' "$ENDPOINT_CONFIG_SHA256" "$ROOT/configs/SensitivitySeparationEndpoints.json" | sha256sum -c -
cp "$ROOT/challenges/SensitivitySeparationEndpoints.lean" "$PROJECT/ComparatorChallenges/SensitivitySeparationEndpoints.lean"
cp "$ROOT/configs/SensitivitySeparationEndpoints.json" "$PROJECT/ComparatorChallenges/SensitivitySeparationEndpoints.json"
sha256sum \
  "$PROJECT/ComparatorChallenges/SensitivitySeparationEndpoints.lean" \
  "$PROJECT/ComparatorChallenges/SensitivitySeparationEndpoints.json" \
  > "$RECEIPT/02_endpoint_target_sha256.txt"

SYSTEMD_MODE=$(cat "$ADMISSION_RECEIPT/11_systemd_mode.txt")
{
  echo "selected_theorems=$SELECTED_THEOREMS"
  echo "endpoint_challenge_sha256=$ENDPOINT_CHALLENGE_SHA256"
  echo "endpoint_config_sha256=$ENDPOINT_CONFIG_SHA256"
  echo "systemd_mode=$SYSTEMD_MODE"
  echo "comparator_bin=$COMPARATOR_BIN"
  echo "lean4export_bin=$EXPORTER_BIN"
  echo "landrun_bin=$LANDRUN_BIN"
} > "$RECEIPT/03_endpoint_execution_contract.txt"

if [[ "$ORIGINAL_MODE" == admission ]]; then
  write_status ADMISSION_PASS
  exit 0
fi

# TRUST ORDER: this Comparator call is the first operation that may compile the
# solution module after the fresh admitted environment has been prepared.
INNER="$RECEIPT/run_endpoint_comparator_inner.sh"
cat > "$INNER" <<INNER_EOF
#!/usr/bin/env bash
set -Eeuo pipefail
export HOME='$HOME'
export PATH='$PATH'
export COMPARATOR_LANDRUN='$LANDRUN_BIN'
export COMPARATOR_LEAN4EXPORT='$EXPORTER_BIN'
cd '$PROJECT'
exec lake env '$COMPARATOR_BIN' ComparatorChallenges/SensitivitySeparationEndpoints.json
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
  echo 'Endpoint Comparator did not succeed.' >&2
  exit "$COMPARATOR_RC"
fi

grep -F 'Your solution is okay!' "$RECEIPT/04_comparator.stdout" > "$RECEIPT/05_comparator_success_marker.txt" || {
  write_status COMPARATOR_HOLD
  echo 'Comparator returned zero but the success marker was absent.' >&2
  exit 4
}

cat > "$RECEIPT/PostCheckAxioms.lean" <<'AXIOMS_EOF'
import OAI.Combinatorics.Sensitivity.Separation
#print axioms OAI.Paper320.quantitative_separation
#print axioms OAI.Paper320.unbounded_quadratic_separation
#print axioms OAI.Paper320.fixed_power_separation
AXIOMS_EOF
(
  cd "$PROJECT"
  lake env lean "$RECEIPT/PostCheckAxioms.lean" \
    > "$RECEIPT/06_axioms.stdout" 2> "$RECEIPT/06_axioms.stderr"
)

write_status PASS_ENDPOINT_THEOREMS
echo "PASS: Comparator accepted $SELECTED_THEOREMS. CMIS must review the receipt before upgrading status."
