#!/usr/bin/env bash
set -Eeuo pipefail
umask 077

ROOT=$(pwd)
RECEIPT="$ROOT/cmis_receipt"
ADMISSION_RECEIPT="$ROOT/cmis_family159_admission_receipt"
TOOLS="$ROOT/.cmis-tools"
WORK="$ROOT/.cmis-work"
PROJECT="$WORK/openai-math/lean"
COMPARATOR_BIN="$WORK/comparator/.lake/build/bin/comparator"
EXPORTER_BIN="$WORK/comparator/.lake/packages/lean4export/.lake/build/bin/lean4export"
LANDRUN_BIN="$TOOLS/bin/landrun"

UPSTREAM_CONFIG_SOURCE="lean/ComparatorChallenges/ErdosReciprocal.json"
UPSTREAM_CONFIG_BLOB="a45f490fd89777caab153921c84896d564f7b77f"
UPSTREAM_CHALLENGE_SOURCE="lean/ComparatorChallenges/ErdosReciprocal.lean"
UPSTREAM_CHALLENGE_BLOB="746c77956e8e936da5df5ae00e815246cd05bcf0"
UPSTREAM_UMBRELLA_SOURCE="lean/OAI/Combinatorics/Progressions/Main.lean"
UPSTREAM_UMBRELLA_BLOB="6eb0380a56083c87686d154c255ba8e22211ce4b"
NARROW_SOLUTION_SOURCE="lean/OAI/Combinatorics/Progressions/Results/Conclusions.lean"
NARROW_SOLUTION_BLOB="ca90287d54ff26e7a16e531b342974726f369327"
UPSTREAM_SOLUTION_MODULE="OAI.Combinatorics.Progressions.Main"
NARROW_SOLUTION_MODULE="OAI.Combinatorics.Progressions.Results.Conclusions"
SELECTED_THEOREM="OAI.Erdos3.manuscriptReciprocalProgressionTheorem"
DERIVED_CONFIG_REL="ComparatorChallenges/CMISFamily159ErdosReciprocalNarrow.json"

status_written=0
finalized=0
write_status() {
  mkdir -p "$RECEIPT"
  printf '%s\n' "$1" > "$RECEIPT/FINAL_STATUS.txt"
  status_written=1
}
finalize_exit() {
  rc=$?
  if [[ $finalized -eq 1 ]]; then exit "$rc"; fi
  finalized=1
  trap - EXIT
  if [[ $status_written -eq 0 ]]; then write_status UNCLASSIFIED_HOLD; fi
  {
    echo "exit_code=$rc"
    echo "utc=$(date -u +%Y-%m-%dT%H:%M:%SZ)"
  } > "$RECEIPT/98_exit.txt"
  find "$RECEIPT" -maxdepth 1 -type f ! -name '99_receipt_sha256.txt' -print0 \
    | sort -z | xargs -0 sha256sum > "$RECEIPT/99_receipt_sha256.txt"
  exit "$rc"
}
trap finalize_exit EXIT

case "${EXECUTION_MODE:-full}" in admission|full) ;; *)
  write_status ENVIRONMENT_HOLD
  echo "Invalid EXECUTION_MODE=${EXECUTION_MODE:-}" >&2
  exit 2
esac
ORIGINAL_MODE="${EXECUTION_MODE:-full}"

rm -rf "$RECEIPT" "$ADMISSION_RECEIPT"

# Reuse the audited generic admission path, but pin the exact theorem-bearing
# Conclusions source rather than the much broader umbrella Main module.
export EXECUTION_MODE=admission
export TARGET_LABEL=family159_narrowed_admission
export CONFIG_SOURCE_PATH="$UPSTREAM_CONFIG_SOURCE"
export CONFIG_RUNTIME_PATH="ComparatorChallenges/ErdosReciprocal.json"
export TARGET_CONFIG_BLOB="$UPSTREAM_CONFIG_BLOB"
export CHALLENGE_SOURCE_PATH="$UPSTREAM_CHALLENGE_SOURCE"
export TARGET_CHALLENGE_BLOB="$UPSTREAM_CHALLENGE_BLOB"
export SOLUTION_SOURCE_PATH="$NARROW_SOLUTION_SOURCE"
export TARGET_SOLUTION_BLOB="$NARROW_SOLUTION_BLOB"
export SOLUTION_MODULE="$NARROW_SOLUTION_MODULE"
export SELECTED_THEOREM="$SELECTED_THEOREM"
export AXIOM_IMPORT_MODULE="$NARROW_SOLUTION_MODULE"
export AXIOM_DECLARATIONS="$SELECTED_THEOREM"
bash "$ROOT/scripts/run_openai_math_selected_target.sh"
export EXECUTION_MODE="$ORIGINAL_MODE"

[[ -f "$RECEIPT/FINAL_STATUS.txt" && "$(cat "$RECEIPT/FINAL_STATUS.txt")" == ADMISSION_PASS ]] || {
  echo "Narrowed family-159 admission did not pass." >&2
  exit 2
}

mv "$RECEIPT" "$ADMISSION_RECEIPT"
mkdir -p "$RECEIPT"
tar -czf "$RECEIPT/00_admission_receipt.tar.gz" -C "$ROOT" "$(basename "$ADMISSION_RECEIPT")"
sha256sum "$RECEIPT/00_admission_receipt.tar.gz" > "$RECEIPT/00_admission_receipt.sha256"

LEAN_HOME=$(find "$TOOLS" -maxdepth 1 -mindepth 1 -type d -name 'lean-*-linux' -print -quit)
[[ -n "$LEAN_HOME" && -x "$LEAN_HOME/bin/lake" ]] || {
  write_status ENVIRONMENT_HOLD
  echo "Admitted Lean/Lake toolchain not found." >&2
  exit 2
}
export PATH="$LEAN_HOME/bin:$TOOLS/bin:$PATH"
exec > >(tee "$RECEIPT/01_family159_narrow.stdout") \
     2> >(tee "$RECEIPT/01_family159_narrow.stderr" >&2)

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
  printf '%s %s\n' "$actual" "$path" >> "$RECEIPT/02_target_blob_checks.txt"
  [[ "$actual" == "$expected" ]] || {
    write_status ENVIRONMENT_HOLD
    echo "Blob mismatch: $path" >&2
    exit 2
  }
}
check_blob "$UPSTREAM_CONFIG_SOURCE" "$UPSTREAM_CONFIG_BLOB"
check_blob "$UPSTREAM_CHALLENGE_SOURCE" "$UPSTREAM_CHALLENGE_BLOB"
check_blob "$UPSTREAM_UMBRELLA_SOURCE" "$UPSTREAM_UMBRELLA_BLOB"
check_blob "$NARROW_SOLUTION_SOURCE" "$NARROW_SOLUTION_BLOB"

# Create a derived runtime configuration from the exact upstream JSON.
# The only semantic change is solution_module: umbrella Main -> theorem-bearing
# Results.Conclusions. The theorem, challenge, definitions and permitted axioms
# remain byte-for-byte equivalent after JSON parsing.
python3 - \
  "$WORK/openai-math/$UPSTREAM_CONFIG_SOURCE" \
  "$PROJECT/$DERIVED_CONFIG_REL" \
  "$UPSTREAM_SOLUTION_MODULE" \
  "$NARROW_SOLUTION_MODULE" \
  "$SELECTED_THEOREM" \
  "$RECEIPT/03_config_derivation.json" <<'PY'
import hashlib
import json
import pathlib
import sys

source_path = pathlib.Path(sys.argv[1])
derived_path = pathlib.Path(sys.argv[2])
upstream_module = sys.argv[3]
narrow_module = sys.argv[4]
selected = sys.argv[5]
report_path = pathlib.Path(sys.argv[6])

original_bytes = source_path.read_bytes()
original = json.loads(original_bytes)
assert original["solution_module"] == upstream_module
assert original["theorem_names"] == [selected]
assert original.get("definition_names", []) == []
assert original["permitted_axioms"] == ["propext", "Quot.sound", "Classical.choice"]

derived = dict(original)
derived["solution_module"] = narrow_module
derived_path.parent.mkdir(parents=True, exist_ok=True)
derived_bytes = (json.dumps(derived, indent=2) + "\n").encode()
derived_path.write_bytes(derived_bytes)

round_trip = json.loads(derived_bytes)
assert round_trip["challenge_module"] == original["challenge_module"]
assert round_trip["theorem_names"] == original["theorem_names"]
assert round_trip.get("definition_names", []) == original.get("definition_names", [])
assert round_trip["permitted_axioms"] == original["permitted_axioms"]
assert round_trip.get("enable_nanoda") == original.get("enable_nanoda")
assert round_trip["solution_module"] == narrow_module

report = {
    "upstream_config_path": str(source_path),
    "derived_config_path": str(derived_path),
    "upstream_sha256": hashlib.sha256(original_bytes).hexdigest(),
    "derived_sha256": hashlib.sha256(derived_bytes).hexdigest(),
    "changed_fields": {
        "solution_module": {
            "from": upstream_module,
            "to": narrow_module,
        }
    },
    "unchanged_contract": {
        "challenge_module": original["challenge_module"],
        "theorem_names": original["theorem_names"],
        "definition_names": original.get("definition_names", []),
        "permitted_axioms": original["permitted_axioms"],
        "enable_nanoda": original.get("enable_nanoda"),
    },
}
report_path.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n")
PY

sha256sum "$PROJECT/$DERIVED_CONFIG_REL" > "$RECEIPT/03_derived_config.sha256"
cp "$PROJECT/$DERIVED_CONFIG_REL" "$RECEIPT/03_derived_config.json"

# Inspect the static project-local import closure without building anything.
python3 - \
  "$PROJECT" \
  "$UPSTREAM_SOLUTION_MODULE" \
  "$NARROW_SOLUTION_MODULE" \
  "$RECEIPT" <<'PY'
import hashlib
import json
import pathlib
import re
import sys

root = pathlib.Path(sys.argv[1])
modules = {
    "upstream_umbrella": sys.argv[2],
    "narrow_theorem_module": sys.argv[3],
}
receipt = pathlib.Path(sys.argv[4])

import_re = re.compile(r"^\s*import\s+(.+?)\s*$")

def module_path(module):
    return root / (module.replace(".", "/") + ".lean")

def direct_imports(module):
    path = module_path(module)
    if not path.exists():
        return [], [module]
    local = []
    external = []
    for line in path.read_text(errors="replace").splitlines():
        match = import_re.match(line)
        if not match:
            continue
        text = match.group(1).split("--", 1)[0].strip()
        for token in text.split():
            if module_path(token).exists():
                local.append(token)
            else:
                external.append(token)
    return local, external

def closure(start):
    seen = set()
    external = set()
    stack = [start]
    while stack:
        module = stack.pop()
        if module in seen:
            continue
        seen.add(module)
        local, ext = direct_imports(module)
        stack.extend(local)
        external.update(ext)
    return seen, external

report = {}
closures = {}
for label, module in modules.items():
    direct, direct_external = direct_imports(module)
    seen, external = closure(module)
    closures[label] = seen
    report[label] = {
        "root_module": module,
        "root_file": str(module_path(module).relative_to(root)),
        "direct_project_imports": len(direct),
        "direct_external_imports": sorted(direct_external),
        "project_local_closure_modules": len(seen),
        "external_import_roots": sorted(external),
    }
    list_path = receipt / f"04_{label}_import_closure.txt"
    text = "\n".join(sorted(seen)) + "\n"
    list_path.write_text(text)
    report[label]["closure_list_sha256"] = hashlib.sha256(text.encode()).hexdigest()

original_only = closures["upstream_umbrella"] - closures["narrow_theorem_module"]
narrow_only = closures["narrow_theorem_module"] - closures["upstream_umbrella"]
report["comparison"] = {
    "modules_avoided_by_narrow_root": len(original_only),
    "modules_added_by_narrow_root": len(narrow_only),
    "narrow_is_subset_of_upstream": not narrow_only,
}
(receipt / "04_import_closure_summary.json").write_text(
    json.dumps(report, indent=2, sort_keys=True) + "\n"
)
PY

SYSTEMD_MODE=$(awk -F= '$1=="systemd_mode"{print $2}' "$ADMISSION_RECEIPT/03_execution_contract.txt")
[[ "$SYSTEMD_MODE" == user || "$SYSTEMD_MODE" == system ]] || {
  write_status ENVIRONMENT_HOLD
  echo "Could not recover admitted systemd mode." >&2
  exit 2
}

{
  echo "target_label=family159_erdos_reciprocal_narrowed"
  echo "selected_theorem=$SELECTED_THEOREM"
  echo "upstream_config=$UPSTREAM_CONFIG_SOURCE"
  echo "derived_runtime_config=$DERIVED_CONFIG_REL"
  echo "upstream_solution_module=$UPSTREAM_SOLUTION_MODULE"
  echo "narrow_solution_module=$NARROW_SOLUTION_MODULE"
  echo "narrow_solution_source=$NARROW_SOLUTION_SOURCE"
  echo "systemd_mode=$SYSTEMD_MODE"
  echo "comparator_bin=$COMPARATOR_BIN"
  echo "lean4export_bin=$EXPORTER_BIN"
  echo "landrun_bin=$LANDRUN_BIN"
  lean --version
  lake --version
  df -h /
} > "$RECEIPT/05_execution_contract.txt"

if [[ "$ORIGINAL_MODE" == admission ]]; then
  write_status ADMISSION_PASS
  exit 0
fi

# TRUST ORDER: Comparator remains the first operation allowed to build the
# narrowed theorem-bearing solution module in this fresh admitted environment.
INNER="$RECEIPT/run_comparator_inner.sh"
cat > "$INNER" <<INNER_EOF
#!/usr/bin/env bash
set -Eeuo pipefail
export HOME='$HOME'
export PATH='$PATH'
export COMPARATOR_LANDRUN='$LANDRUN_BIN'
export COMPARATOR_LEAN4EXPORT='$EXPORTER_BIN'
cd '$PROJECT'
exec lake env '$COMPARATOR_BIN' '$DERIVED_CONFIG_REL'
INNER_EOF
chmod 700 "$INNER"

set +e
if [[ "$SYSTEMD_MODE" == user ]]; then
  systemd-run --user --wait --pipe --collect \
    --property='RestrictAddressFamilies=~AF_UNIX' \
    --working-directory="$PROJECT" \
    "$INNER" > "$RECEIPT/06_comparator.stdout" 2> "$RECEIPT/06_comparator.stderr"
  COMPARATOR_RC=$?
else
  sudo systemd-run --wait --pipe --collect \
    --uid="$(id -un)" --gid="$(id -gn)" \
    --property='RestrictAddressFamilies=~AF_UNIX' \
    --working-directory="$PROJECT" \
    "$INNER" > "$RECEIPT/06_comparator.stdout" 2> "$RECEIPT/06_comparator.stderr"
  COMPARATOR_RC=$?
fi
set -e
printf '%s\n' "$COMPARATOR_RC" > "$RECEIPT/06_comparator.exit_code"

if [[ "$COMPARATOR_RC" -ne 0 ]]; then
  write_status COMPARATOR_HOLD
  echo "Comparator did not accept the narrowed family-159 target." >&2
  exit "$COMPARATOR_RC"
fi

grep -F 'Your solution is okay!' "$RECEIPT/06_comparator.stdout" \
  > "$RECEIPT/07_comparator_success_marker.txt" || {
  write_status COMPARATOR_HOLD
  exit 4
}

cat > "$RECEIPT/PostCheckAxioms.lean" <<AXIOM_EOF
import $NARROW_SOLUTION_MODULE
#print axioms $SELECTED_THEOREM
AXIOM_EOF
(
  cd "$PROJECT"
  lake env lean "$RECEIPT/PostCheckAxioms.lean" \
    > "$RECEIPT/08_axioms.stdout" 2> "$RECEIPT/08_axioms.stderr"
)
grep -F "$SELECTED_THEOREM" "$RECEIPT/08_axioms.stdout" >/dev/null || {
  write_status AXIOM_POSTCHECK_HOLD
  echo "Axiom report absent for $SELECTED_THEOREM" >&2
  exit 4
}
for axiom in propext Quot.sound Classical.choice; do
  grep -F "$axiom" "$RECEIPT/08_axioms.stdout" >/dev/null || {
    write_status AXIOM_POSTCHECK_HOLD
    echo "Expected permitted axiom absent: $axiom" >&2
    exit 4
  }
done

write_status PASS_SELECTED_THEOREM
echo "PASS: Comparator accepted the narrowed family-159 target. This remains partial family coverage."
