#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

# Use the unchanged audited runner. The outer deadline includes admission,
# Comparator and the axiom postcheck; it cannot turn an interrupted run into PASS.
CMIS_BOUND_ROOT=$(pwd)
CMIS_BOUND_RECEIPT="$CMIS_BOUND_ROOT/cmis_receipt"
CMIS_BOUND_DIR=$(mktemp -d "$CMIS_BOUND_ROOT/.cmis-family161-bound.XXXXXX")
CMIS_BOUND_LOG="$CMIS_BOUND_DIR/budget_and_cleanup.txt"
CMIS_VERIFICATION_TIMEOUT_SECONDS="${CMIS_VERIFICATION_TIMEOUT_SECONDS:-19800}"

# systemd-run creates a detached service. On an interrupted/failed command,
# stop only a transient service whose ExecStart is this run's exact inner script.
# This does not alter Comparator, its arguments, the source, or the sandbox.
cmis_bound_ctl() {
  local cmis_limit=$1
  shift
  local cmis_remaining=$((CMIS_CLEANUP_DEADLINE - SECONDS))
  (( cmis_remaining > 0 )) || return 124
  if (( cmis_limit > cmis_remaining )); then cmis_limit=$cmis_remaining; fi
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
    [[ "$cmis_exec" == *"path=$CMIS_BOUND_RECEIPT/run_comparator_inner.sh ;"* ]] || continue
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
  local cmis_cleanup_rc=0
  if (( cmis_rc != 0 )); then
    cmis_stop_own_comparator >> "$CMIS_BOUND_LOG" 2>&1
    cmis_cleanup_rc=$?
  fi
  mkdir -p "$CMIS_BOUND_RECEIPT"
  if (( cmis_cleanup_rc != 0 )); then
    printf '%s\n' RESOURCE_CLEANUP_HOLD > "$CMIS_BOUND_RECEIPT/FINAL_STATUS.txt"
    echo "cleanup_exit_code=$cmis_cleanup_rc" >> "$CMIS_BOUND_LOG"
    (( cmis_rc != 0 )) || cmis_rc=2
  elif (( cmis_rc == 124 )); then
    printf '%s\n' RESOURCE_TIMEOUT_HOLD > "$CMIS_BOUND_RECEIPT/FINAL_STATUS.txt"
  elif (( cmis_rc == 137 )); then
    # SIGKILL can also reflect resource termination; do not assert its cause.
    printf '%s\n' RESOURCE_TERMINATION_HOLD > "$CMIS_BOUND_RECEIPT/FINAL_STATUS.txt"
  else
    local cmis_status
    cmis_status=$(cat "$CMIS_BOUND_RECEIPT/FINAL_STATUS.txt" 2>/dev/null)
    if (( cmis_rc == 0 )); then
      case "${EXECUTION_MODE:-}:$cmis_status" in
        full:PASS_SELECTED_THEOREM|admission:ADMISSION_PASS) ;;
        *) printf '%s\n' EXECUTION_CONTRACT_HOLD > "$CMIS_BOUND_RECEIPT/FINAL_STATUS.txt"; cmis_rc=4 ;;
      esac
    elif [[ -z "$cmis_status" || "$cmis_status" == PASS_SELECTED_THEOREM || "$cmis_status" == ADMISSION_PASS ]]; then
      printf '%s\n' EXECUTION_HOLD > "$CMIS_BOUND_RECEIPT/FINAL_STATUS.txt"
    fi
  fi
  cp "$CMIS_BOUND_LOG" "$CMIS_BOUND_RECEIPT/97_bounded_execution.txt" || cmis_rc=4
  {
    echo "exit_code=$cmis_rc"
    echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "$CMIS_BOUND_RECEIPT/98_bounded_exit.txt"
  (
    cd "$CMIS_BOUND_RECEIPT" || exit 2
    find . -maxdepth 1 -type f ! -name 99_receipt_sha256.txt -print0 \
      | sort -z | xargs -0 sha256sum > 99_receipt_sha256.txt
  ) || cmis_rc=4
  exit "$cmis_rc"
}
trap cmis_bound_finalize EXIT

{
  echo "started_utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  echo "verification_command_budget_seconds=$CMIS_VERIFICATION_TIMEOUT_SECONDS"
  echo "verification_termination_grace_seconds=60"
  echo "cleanup_budget_seconds=180"
  echo "scope=unchanged_generic_runner_with_external_resource_bound"
} > "$CMIS_BOUND_LOG"
[[ "$CMIS_VERIFICATION_TIMEOUT_SECONDS" =~ ^[1-9][0-9]{0,4}$ ]] \
  && (( CMIS_VERIFICATION_TIMEOUT_SECONDS <= 19800 )) || exit 2

# Pin both audited harness components because cleanup relies on their exact
# inner-script path and systemd invocation convention.
[[ "$(git hash-object scripts/run_openai_math_selected_target.sh)" == 1a90e61237618a912b3faed38cde5083b5bd4a23 ]] || exit 2
[[ "$(git hash-object scripts/run_family132_github_actions.sh)" == 84415eae7efc28b447307a598828292f67398923 ]] || exit 2
timeout --signal=TERM --kill-after=60s "${CMIS_VERIFICATION_TIMEOUT_SECONDS}s" \
  bash "$CMIS_BOUND_ROOT/scripts/run_openai_math_selected_target.sh"
