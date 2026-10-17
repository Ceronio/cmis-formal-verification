#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT=$(pwd)
RECEIPT="$ROOT/cmis_receipt"
TOOLS="$ROOT/.cmis-tools"
WORK="$ROOT/.cmis-work"
mkdir -p "$RECEIPT" "$TOOLS/bin" "$WORK"

status_written=0
finalized=0
write_status() {
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
  exit "$rc"
}
trap finalize_exit EXIT

exec > >(tee "$RECEIPT/00_workflow.stdout") 2> >(tee "$RECEIPT/00_workflow.stderr" >&2)

required_env=(
  EXECUTION_MODE OPENAI_MATH_COMMIT LEAN_VERSION LEAN_ASSET_URL LEAN_ASSET_SHA256
  COMPARATOR_COMMIT LEAN4EXPORT_COMMIT LANDRUN_COMMIT MATHLIB_COMMIT
  CONFIG_BLOB CHALLENGE_BLOB SOLUTION_BLOB SELECTED_THEOREM
)
for name in "${required_env[@]}"; do
  [[ -n "${!name:-}" ]] || { write_status ENVIRONMENT_HOLD; echo "Missing environment variable: $name" >&2; exit 2; }
done

case "$EXECUTION_MODE" in admission|full) ;; *) write_status ENVIRONMENT_HOLD; echo "Invalid execution mode" >&2; exit 2;; esac

{
  echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "github_repository=${GITHUB_REPOSITORY:-unknown}"
  echo "github_run_id=${GITHUB_RUN_ID:-unknown}"
  echo "github_run_attempt=${GITHUB_RUN_ATTEMPT:-unknown}"
  echo "runner_os=${RUNNER_OS:-unknown}"
  echo "runner_arch=${RUNNER_ARCH:-unknown}"
  echo "execution_mode=$EXECUTION_MODE"
  uname -a
  lscpu || true
  free -h || true
  df -h || true
  go version
  git --version
  systemd-run --version | head -1 || true
} > "$RECEIPT/01_runner_identity.txt"

[[ "$(uname -m)" == "x86_64" ]] || { write_status ENVIRONMENT_HOLD; echo "This harness pins the x86_64 Lean asset." >&2; exit 2; }

{
  echo 'Before cleanup:'
  df -h /
  sudo rm -rf /usr/local/lib/android /usr/share/dotnet /opt/ghc /usr/local/.ghcup /opt/hostedtoolcache/CodeQL || true
  sudo apt-get clean || true
  echo 'After cleanup:'
  df -h /
} > "$RECEIPT/02_disk_cleanup.txt" 2>&1

sudo apt-get update > "$RECEIPT/03_apt_update.log" 2>&1
sudo DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
  ca-certificates curl git jq zstd xz-utils unzip systemd > "$RECEIPT/04_apt_install.log" 2>&1

LEAN_ARCHIVE="$WORK/lean-${LEAN_VERSION}-linux.tar.zst"
curl --fail --location --retry 5 --retry-all-errors "$LEAN_ASSET_URL" -o "$LEAN_ARCHIVE"
printf '%s  %s\n' "$LEAN_ASSET_SHA256" "$LEAN_ARCHIVE" | sha256sum -c -
tar --zstd -xf "$LEAN_ARCHIVE" -C "$TOOLS"
LEAN_HOME=$(find "$TOOLS" -maxdepth 1 -mindepth 1 -type d -name "lean-${LEAN_VERSION}-linux" -print -quit)
[[ -n "$LEAN_HOME" ]] || { write_status ENVIRONMENT_HOLD; echo "Lean extraction directory not found" >&2; exit 2; }
export PATH="$LEAN_HOME/bin:$TOOLS/bin:$PATH"

lean --version | tee "$RECEIPT/05_lean_version.txt"
lake --version | tee "$RECEIPT/06_lake_version.txt"
[[ "$(lean --version)" == *"version ${LEAN_VERSION}"* ]] || { write_status ENVIRONMENT_HOLD; echo "Lean version mismatch" >&2; exit 2; }

git clone --quiet https://github.com/Zouuup/landrun.git "$WORK/landrun"
git -C "$WORK/landrun" checkout --quiet --detach "$LANDRUN_COMMIT"
[[ "$(git -C "$WORK/landrun" rev-parse HEAD)" == "$LANDRUN_COMMIT" ]] || { write_status ENVIRONMENT_HOLD; exit 2; }
(
  cd "$WORK/landrun"
  go build -trimpath -o "$TOOLS/bin/landrun" ./cmd/landrun
)
"$TOOLS/bin/landrun" --version > "$RECEIPT/07_landrun_version.txt" 2>&1 || true
sha256sum "$TOOLS/bin/landrun" > "$RECEIPT/07_landrun_sha256.txt"
"$TOOLS/bin/landrun" --best-effort --ldd --add-exec /usr/bin/true

git clone --quiet https://github.com/leanprover/comparator.git "$WORK/comparator"
git -C "$WORK/comparator" checkout --quiet --detach "$COMPARATOR_COMMIT"
[[ "$(git -C "$WORK/comparator" rev-parse HEAD)" == "$COMPARATOR_COMMIT" ]] || { write_status ENVIRONMENT_HOLD; exit 2; }
actual_export_rev=$(jq -r '.packages[] | select(.name=="lean4export") | .rev' "$WORK/comparator/lake-manifest.json")
[[ "$actual_export_rev" == "$LEAN4EXPORT_COMMIT" ]] || { write_status ENVIRONMENT_HOLD; echo "lean4export pin mismatch" >&2; exit 2; }
(
  cd "$WORK/comparator"
  lake build lean4export comparator 2>&1 | tee "$RECEIPT/08_comparator_build.log"
)
COMPARATOR_BIN="$WORK/comparator/.lake/build/bin/comparator"
EXPORTER_BIN="$WORK/comparator/.lake/packages/lean4export/.lake/build/bin/lean4export"
[[ -x "$COMPARATOR_BIN" && -x "$EXPORTER_BIN" ]] || { write_status ENVIRONMENT_HOLD; echo "Verifier binaries missing" >&2; exit 2; }
sha256sum "$COMPARATOR_BIN" "$EXPORTER_BIN" > "$RECEIPT/09_verifier_sha256.txt"

git clone --quiet --filter=blob:none --no-checkout https://github.com/openai/math.git "$WORK/openai-math"
git -C "$WORK/openai-math" sparse-checkout init --cone
git -C "$WORK/openai-math" sparse-checkout set lean
git -C "$WORK/openai-math" checkout --quiet --detach "$OPENAI_MATH_COMMIT"
[[ "$(git -C "$WORK/openai-math" rev-parse HEAD)" == "$OPENAI_MATH_COMMIT" ]] || { write_status ENVIRONMENT_HOLD; exit 2; }

check_blob() {
  local path=$1 expected=$2
  local actual
  actual=$(git -C "$WORK/openai-math" rev-parse "$OPENAI_MATH_COMMIT:$path")
  printf '%s %s\n' "$actual" "$path" >> "$RECEIPT/10_project_blob_checks.txt"
  [[ "$actual" == "$expected" ]] || { write_status ENVIRONMENT_HOLD; echo "Blob mismatch: $path" >&2; exit 2; }
}
check_blob lean/ComparatorChallenges/SensitivitySeparation.json "$CONFIG_BLOB"
check_blob lean/ComparatorChallenges/SensitivitySeparation.lean "$CHALLENGE_BLOB"
check_blob lean/OAI/Combinatorics/Sensitivity/Separation.lean "$SOLUTION_BLOB"
check_blob lean/lean-toolchain ba8ebf2dbaf6a668cd2a0e086186d6d569b69ff5
check_blob lean/lakefile.lean 66c3867331c7c607ffc0e60955cc86cccf046e12
check_blob lean/lake-manifest.json 67d01d2717d0aaff59fb8814bb53581b961f42b4

PROJECT="$WORK/openai-math/lean"
[[ "$(tr -d '\r\n' < "$PROJECT/lean-toolchain")" == "leanprover/lean4:v${LEAN_VERSION}" ]] || { write_status ENVIRONMENT_HOLD; exit 2; }
[[ "$(jq -r '.packages | length' "$PROJECT/lake-manifest.json")" == "42" ]] || { write_status ENVIRONMENT_HOLD; exit 2; }
[[ "$(jq -r '.fixedToolchain' "$PROJECT/lake-manifest.json")" == "true" ]] || { write_status ENVIRONMENT_HOLD; exit 2; }
[[ "$(jq -r '.packages[] | select(.name=="mathlib") | .rev' "$PROJECT/lake-manifest.json")" == "$MATHLIB_COMMIT" ]] || { write_status ENVIRONMENT_HOLD; exit 2; }

SYSTEMD_MODE=''
if systemd-run --user --wait --pipe --collect --property='RestrictAddressFamilies=~AF_UNIX' /usr/bin/true \
    > "$RECEIPT/11_systemd_user_test.txt" 2>&1; then
  SYSTEMD_MODE=user
elif sudo systemd-run --wait --pipe --collect \
    --uid="$(id -un)" --gid="$(id -gn)" \
    --property='RestrictAddressFamilies=~AF_UNIX' /usr/bin/true \
    > "$RECEIPT/11_systemd_system_test.txt" 2>&1; then
  SYSTEMD_MODE=system
else
  write_status SECURITY_HOLD
  echo 'Neither protected systemd-run mode is available.' >&2
  exit 3
fi
printf '%s\n' "$SYSTEMD_MODE" > "$RECEIPT/11_systemd_mode.txt"

(
  cd "$PROJECT"
  sha256sum lake-manifest.json > "$RECEIPT/12_manifest_before.txt"
  lake update 2>&1 | tee "$RECEIPT/13_lake_update.log"
  sha256sum lake-manifest.json > "$RECEIPT/14_manifest_after.txt"
  git -C "$WORK/openai-math" status --porcelain --untracked-files=no > "$RECEIPT/15_tracked_status.txt"
  [[ ! -s "$RECEIPT/15_tracked_status.txt" ]] || {
    write_status ENVIRONMENT_HOLD
    echo 'Pinned project tracked files changed during dependency preparation.' >&2
    exit 2
  }
  lake exe cache get 2>&1 | tee "$RECEIPT/16_cache_get.log"
)

{
  echo "openai_math_commit=$OPENAI_MATH_COMMIT"
  echo "lean_version=$LEAN_VERSION"
  echo "comparator_commit=$COMPARATOR_COMMIT"
  echo "lean4export_commit=$LEAN4EXPORT_COMMIT"
  echo "landrun_commit=$LANDRUN_COMMIT"
  echo "mathlib_commit=$MATHLIB_COMMIT"
  echo "selected_theorem=$SELECTED_THEOREM"
  echo "systemd_mode=$SYSTEMD_MODE"
  echo "comparator_bin=$COMPARATOR_BIN"
  echo "lean4export_bin=$EXPORTER_BIN"
  echo "landrun_bin=$TOOLS/bin/landrun"
  df -h /
} > "$RECEIPT/17_execution_contract.txt"

if [[ "$EXECUTION_MODE" == admission ]]; then
  write_status ADMISSION_PASS
  exit 0
fi

INNER="$RECEIPT/run_comparator_inner.sh"
cat > "$INNER" <<EOF
#!/usr/bin/env bash
set -Eeuo pipefail
export HOME='$HOME'
export PATH='$PATH'
export COMPARATOR_LANDRUN='$TOOLS/bin/landrun'
export COMPARATOR_LEAN4EXPORT='$EXPORTER_BIN'
cd '$PROJECT'
# Comparator must inherit Lake's LEAN_PATH so lean4export can resolve project modules.
exec lake env '$COMPARATOR_BIN' ComparatorChallenges/SensitivitySeparation.json
EOF
chmod 700 "$INNER"

set +e
if [[ "$SYSTEMD_MODE" == user ]]; then
  systemd-run --user --wait --pipe --collect \
    --property='RestrictAddressFamilies=~AF_UNIX' \
    --working-directory="$PROJECT" \
    "$INNER" > "$RECEIPT/18_comparator.stdout" 2> "$RECEIPT/18_comparator.stderr"
  COMPARATOR_RC=$?
else
  sudo systemd-run --wait --pipe --collect \
    --uid="$(id -un)" --gid="$(id -gn)" \
    --property='RestrictAddressFamilies=~AF_UNIX' \
    --working-directory="$PROJECT" \
    "$INNER" > "$RECEIPT/18_comparator.stdout" 2> "$RECEIPT/18_comparator.stderr"
  COMPARATOR_RC=$?
fi
set -e
printf '%s\n' "$COMPARATOR_RC" > "$RECEIPT/18_comparator.exit_code"
if [[ "$COMPARATOR_RC" -ne 0 ]]; then
  write_status COMPARATOR_HOLD
  echo 'Comparator did not succeed. No formal success claim is permitted.' >&2
  exit "$COMPARATOR_RC"
fi

grep -F 'Your solution is okay!' "$RECEIPT/18_comparator.stdout" > "$RECEIPT/19_comparator_success_marker.txt" || {
  write_status COMPARATOR_HOLD
  echo 'Comparator exit was zero but the success marker was absent.' >&2
  exit 4
}

cat > "$RECEIPT/PostCheckAxioms.lean" <<'EOF'
import OAI.Combinatorics.Sensitivity.Separation
#print axioms OAI.Paper320.quantitative_separation
#print axioms OAI.Paper320.unbounded_quadratic_separation
#print axioms OAI.Paper320.fixed_power_separation
EOF
(
  cd "$PROJECT"
  lake env lean "$RECEIPT/PostCheckAxioms.lean" \
    > "$RECEIPT/20_axioms.stdout" 2> "$RECEIPT/20_axioms.stderr"
)

write_status PASS_SELECTED_THEOREM
echo "PASS: Comparator accepted $SELECTED_THEOREM. CMIS must still review the receipt before upgrading status."
