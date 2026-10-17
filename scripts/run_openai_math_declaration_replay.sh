#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT=$(pwd)
RECEIPT="$ROOT/cmis_receipt"
ADMISSION_RECEIPT="$ROOT/cmis_admission_receipt"
TOOLS="$ROOT/.cmis-tools"
WORK="$ROOT/.cmis-work"
PROJECT="$WORK/openai-math/lean"

status_written=0
finalized=0
write_status() { mkdir -p "$RECEIPT"; printf '%s\n' "$1" > "$RECEIPT/FINAL_STATUS.txt"; status_written=1; }
finalize_exit() {
  rc=$?
  if [[ $finalized -eq 1 ]]; then exit "$rc"; fi
  finalized=1; trap - EXIT
  [[ $status_written -eq 1 ]] || write_status UNCLASSIFIED_HOLD
  { echo "exit_code=$rc"; echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"; } > "$RECEIPT/98_exit.txt"
  find "$RECEIPT" -maxdepth 1 -type f ! -name 99_receipt_sha256.txt -print0 | sort -z | xargs -0 sha256sum > "$RECEIPT/99_receipt_sha256.txt"
  exit "$rc"
}
trap finalize_exit EXIT

for name in TARGET_LABEL MODULE SOURCE_PATH SOURCE_BLOB DECLARATIONS; do
  [[ -n "${!name:-}" ]] || { write_status ENVIRONMENT_HOLD; echo "Missing $name" >&2; exit 2; }
done

rm -rf "$RECEIPT" "$ADMISSION_RECEIPT"
export EXECUTION_MODE=admission
export SELECTED_THEOREM="${BOOTSTRAP_SELECTED_THEOREM:-OAI.Paper320.quantitative_separation}"
bash "$ROOT/scripts/run_family132_github_actions.sh"
[[ -f "$RECEIPT/FINAL_STATUS.txt" && "$(cat "$RECEIPT/FINAL_STATUS.txt")" == ADMISSION_PASS ]] || {
  echo 'Base admission did not pass.' >&2; exit 2;
}
find "$RECEIPT" -maxdepth 1 -type f ! -name 99_receipt_sha256.txt -print0 | sort -z | xargs -0 sha256sum > "$RECEIPT/99_receipt_sha256.txt"
mv "$RECEIPT" "$ADMISSION_RECEIPT"
mkdir -p "$RECEIPT"
tar -czf "$RECEIPT/00_admission_receipt.tar.gz" -C "$ROOT" "$(basename "$ADMISSION_RECEIPT")"
sha256sum "$RECEIPT/00_admission_receipt.tar.gz" > "$RECEIPT/00_admission_receipt.sha256"

LEAN_HOME=$(find "$TOOLS" -maxdepth 1 -mindepth 1 -type d -name 'lean-*-linux' -print -quit)
[[ -n "$LEAN_HOME" && -x "$LEAN_HOME/bin/lake" ]] || { write_status ENVIRONMENT_HOLD; exit 2; }
export PATH="$LEAN_HOME/bin:$TOOLS/bin:$PATH"
exec > >(tee "$RECEIPT/01_${TARGET_LABEL}.stdout") 2> >(tee "$RECEIPT/01_${TARGET_LABEL}.stderr" >&2)

ACTUAL_BLOB=$(git -C "$WORK/openai-math" rev-parse "$OPENAI_MATH_COMMIT:$SOURCE_PATH")
printf '%s %s\n' "$ACTUAL_BLOB" "$SOURCE_PATH" > "$RECEIPT/02_source_blob.txt"
[[ "$ACTUAL_BLOB" == "$SOURCE_BLOB" ]] || { write_status ENVIRONMENT_HOLD; echo 'Source blob mismatch.' >&2; exit 2; }
{
  echo "target_label=$TARGET_LABEL"
  echo "module=$MODULE"
  echo "source_path=$SOURCE_PATH"
  echo "source_blob=$ACTUAL_BLOB"
  echo "declarations=$DECLARATIONS"
  lean --version
  lake --version
} > "$RECEIPT/03_replay_contract.txt"

set +e
(
  cd "$PROJECT"
  lake build "$MODULE"
) > "$RECEIPT/04_build.stdout" 2> "$RECEIPT/04_build.stderr"
BUILD_RC=$?
set -e
printf '%s\n' "$BUILD_RC" > "$RECEIPT/04_build.exit_code"
if [[ "$BUILD_RC" -ne 0 ]]; then write_status MODULE_BUILD_HOLD; exit "$BUILD_RC"; fi

{
  echo "import $MODULE"
  for decl in $DECLARATIONS; do
    echo "#check $decl"
    echo "#print axioms $decl"
  done
} > "$RECEIPT/PostCheckDeclarations.lean"

set +e
(
  cd "$PROJECT"
  lake env lean "$RECEIPT/PostCheckDeclarations.lean"
) > "$RECEIPT/05_declarations.stdout" 2> "$RECEIPT/05_declarations.stderr"
POST_RC=$?
set -e
printf '%s\n' "$POST_RC" > "$RECEIPT/05_declarations.exit_code"
if [[ "$POST_RC" -ne 0 ]]; then write_status DECLARATION_REPLAY_HOLD; exit "$POST_RC"; fi

for decl in $DECLARATIONS; do
  grep -F "$decl" "$RECEIPT/05_declarations.stdout" >/dev/null || {
    write_status DECLARATION_REPLAY_HOLD
    echo "Declaration absent from replay output: $decl" >&2
    exit 4
  }
done

git -C "$WORK/openai-math" status --short > "$RECEIPT/06_tracked_status.txt"
write_status PASS_DECLARATION_REPLAY
printf '%s\n' 'PASS: pinned source declarations built and replayed. This does not establish equivalence to an unformalized catalogue claim.'
