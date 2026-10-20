#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

# CP39 receipt/cleanup hardening: local contract fixtures are not real systemd integration.
# Use the unchanged audited generic runner. The outer deadline includes admission,
# Comparator and the axiom postcheck; it cannot turn an interrupted run into PASS.
CMIS_BOUND_ROOT=$(pwd)
CMIS_BOUND_RECEIPT="$CMIS_BOUND_ROOT/cmis_receipt"
CMIS_BOUND_DIR=$(mktemp -d "$CMIS_BOUND_ROOT/.cmis-family165-bound.XXXXXX")
CMIS_BOUND_LOG="$CMIS_BOUND_DIR/budget_and_cleanup.txt"
CMIS_VERIFICATION_TIMEOUT_SECONDS="${CMIS_VERIFICATION_TIMEOUT_SECONDS:-19800}"

# systemd-run creates a detached service. On an interrupted/failed command,
# stop only a transient service whose ExecStart is this run's exact inner script.
# This does not alter Comparator, its arguments, the source, or the sandbox.
cmis_bound_ctl() {
  local cmis_limit=$1
  shift
  local cmis_remaining=$((CMIS_CLEANUP_DEADLINE - SECONDS))
  # Reserve the control command's KILL grace inside the cleanup allowance.
  (( cmis_remaining > 5 )) || return 124
  if (( cmis_limit > cmis_remaining - 5 )); then cmis_limit=$((cmis_remaining - 5)); fi
  timeout --signal=TERM --kill-after=5s "${cmis_limit}s" "${CMIS_BOUND_CTL[@]}" "$@"
}

cmis_stop_own_comparator() {
  local cmis_mode_file="$CMIS_BOUND_ROOT/cmis_admission_receipt/11_systemd_mode.txt"
  [[ -f "$cmis_mode_file" ]] || {
    echo "cleanup=selected_comparator_not_reached"
    return 0
  }
  case "$(cat "$cmis_mode_file")" in
    user) CMIS_BOUND_CTL=(systemctl --user) ;;
    system) CMIS_BOUND_CTL=(sudo -n systemctl) ;;
    *) echo "cleanup=unknown_systemd_mode"; return 1 ;;
  esac
  CMIS_CLEANUP_DEADLINE=$((SECONDS + 180))
  cmis_bound_ctl 15 list-units --all --type=service --plain --no-legend --no-pager \
    > "$CMIS_BOUND_DIR/service_units.txt" || return 1
  local cmis_unit cmis_rest cmis_exec cmis_found=0
  while read -r cmis_unit cmis_rest; do
    [[ "$cmis_unit" =~ ^run-[[:alnum:]_.@-]+\.service$ ]] || continue
    cmis_exec=$(cmis_bound_ctl 15 show --property=ExecStart --value "$cmis_unit") || return 1
    [[ "$cmis_exec" == "{ path=$CMIS_BOUND_RECEIPT/run_comparator_inner.sh ; "* ]] || continue
    cmis_found=$((cmis_found + 1))
    echo "stopping_own_unit=$cmis_unit"
    echo "verified_exec_start=$cmis_exec"
    cmis_bound_ctl 120 stop "$cmis_unit" || return 1
    echo "stopped_own_unit=$cmis_unit"
  done < "$CMIS_BOUND_DIR/service_units.txt"
  echo "cleanup=complete"
  echo "matching_active_or_loaded_units=$cmis_found"
}

cmis_bound_finalize() {
  local cmis_rc=$?
  trap - EXIT
  set +e
  echo "bounded_command_exit_code=$cmis_rc" >> "$CMIS_BOUND_LOG"
  echo "finished_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)" >> "$CMIS_BOUND_LOG"
  mkdir -p "$CMIS_BOUND_RECEIPT" || {
    echo "Unable to create terminal receipt; execution is not accepted." >&2
    exit 4
  }
  local cmis_status cmis_cleanup_rc=0 cmis_receipt_rc=0
  cmis_status=$(cat "$CMIS_BOUND_RECEIPT/FINAL_STATUS.txt" 2>/dev/null)

  # Resolve the status/exit contract BEFORE deciding whether cleanup is needed.
  if (( cmis_rc == 0 )); then
    case "${EXECUTION_MODE:-}:$cmis_status" in
      full:PASS_SELECTED_THEOREM|admission:ADMISSION_PASS) ;;
      *) cmis_status=EXECUTION_CONTRACT_HOLD; cmis_rc=4 ;;
    esac
  fi
  if (( cmis_rc != 0 )); then
    cmis_stop_own_comparator >> "$CMIS_BOUND_LOG" 2>&1
    cmis_cleanup_rc=$?
  fi
  if (( cmis_cleanup_rc != 0 )); then
    cmis_status=RESOURCE_CLEANUP_HOLD
    echo "cleanup_exit_code=$cmis_cleanup_rc" >> "$CMIS_BOUND_LOG"
    (( cmis_rc != 0 )) || cmis_rc=2
  elif (( cmis_rc == 124 )); then
    cmis_status=RESOURCE_TIMEOUT_HOLD
  elif (( cmis_rc == 137 )); then
    # SIGKILL can also reflect resource termination; do not assert its cause.
    cmis_status=RESOURCE_TERMINATION_HOLD
  elif (( cmis_rc != 0 )); then
    if [[ -z "$cmis_status" || "$cmis_status" == PASS_SELECTED_THEOREM || "$cmis_status" == ADMISSION_PASS ]]; then
      cmis_status=EXECUTION_HOLD
    fi
  fi
  printf '%s\n' "$cmis_status" > "$CMIS_BOUND_RECEIPT/FINAL_STATUS.txt" || cmis_receipt_rc=1
  cp "$CMIS_BOUND_LOG" "$CMIS_BOUND_RECEIPT/97_bounded_execution.txt" || cmis_receipt_rc=1
  # Retain the inner receipt's earlier manifest; never leave it under the final
  # manifest name if outer finalization fails.
  if [[ -f "$CMIS_BOUND_RECEIPT/99_receipt_sha256.txt" ]]; then
    mv "$CMIS_BOUND_RECEIPT/99_receipt_sha256.txt" "$CMIS_BOUND_RECEIPT/96_inner_receipt_sha256.txt" || cmis_receipt_rc=1
  fi
  if (( cmis_receipt_rc != 0 )); then
    cmis_rc=4
    printf '%s\n' RECEIPT_FINALIZATION_HOLD > "$CMIS_BOUND_RECEIPT/FINAL_STATUS.txt"
  fi
  {
    echo "exit_code=$cmis_rc"
    echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "$CMIS_BOUND_RECEIPT/98_bounded_exit.txt" || cmis_receipt_rc=1
  if (( cmis_receipt_rc != 0 )); then
    cmis_rc=4
    printf '%s\n' RECEIPT_FINALIZATION_HOLD > "$CMIS_BOUND_RECEIPT/FINAL_STATUS.txt"
    {
      echo "exit_code=$cmis_rc"
      echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } > "$CMIS_BOUND_RECEIPT/98_bounded_exit.txt"
  fi
  # A partial checksum stream is not a completed manifest. Publish it atomically
  # only after hashing succeeds; otherwise record a non-PASS finalization hold.
  if (
    cd "$CMIS_BOUND_RECEIPT" || exit 2
    find . -maxdepth 1 -type f ! -name 99_receipt_sha256.txt -print0 \
      | sort -z | xargs -0 sha256sum > "$CMIS_BOUND_DIR/receipt_sha256.pending"
  ) && mv "$CMIS_BOUND_DIR/receipt_sha256.pending" "$CMIS_BOUND_RECEIPT/99_receipt_sha256.txt"; then
    :
  else
    cmis_rc=4
    printf '%s\n' RECEIPT_FINALIZATION_HOLD > "$CMIS_BOUND_RECEIPT/FINAL_STATUS.txt"
    {
      echo "exit_code=$cmis_rc"
      echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
    } > "$CMIS_BOUND_RECEIPT/98_bounded_exit.txt"
    echo "Terminal receipt finalization failed; execution is not accepted." >&2
  fi
  exit "$cmis_rc"
}
trap cmis_bound_finalize EXIT

{
  echo "started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "verification_command_budget_seconds=$CMIS_VERIFICATION_TIMEOUT_SECONDS"
  echo "verification_termination_grace_seconds=60"
  echo "cleanup_budget_seconds=180"
  echo "scope=unchanged_original_config_generic_runner_with_external_resource_bound"
} > "$CMIS_BOUND_LOG"
[[ "$CMIS_VERIFICATION_TIMEOUT_SECONDS" =~ ^[1-9][0-9]{0,4}$ ]] \
  && (( CMIS_VERIFICATION_TIMEOUT_SECONDS <= 19800 )) || exit 2

# Pin both audited harness components because cleanup relies on their exact
# inner-script path and systemd invocation convention.
[[ "$(git hash-object scripts/run_openai_math_selected_target.sh)" == 1a90e61237618a912b3faed38cde5083b5bd4a23 ]] || exit 2
[[ "$(git hash-object scripts/run_family132_github_actions.sh)" == 84415eae7efc28b447307a598828292f67398923 ]] || exit 2
timeout --signal=TERM --kill-after=60s "${CMIS_VERIFICATION_TIMEOUT_SECONDS}s" \
  bash "$CMIS_BOUND_ROOT/scripts/run_openai_math_selected_target.sh"
