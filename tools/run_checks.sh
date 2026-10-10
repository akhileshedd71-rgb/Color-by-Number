#!/usr/bin/env bash
# All tests use separate user:// files. No player progress is modified.
set -euo pipefail
cd "$(dirname "$0")/.."
GODOT_BIN="${GODOT_BIN:-godot4}"
python3 -m unittest discover -s tests -p 'test_*.py' -v
"$GODOT_BIN" --headless --path . --editor --import --quit
log_file="$(mktemp)"
trap 'rm -f "$log_file"' EXIT
set +e
"$GODOT_BIN" --headless --path . tests/test_runner.tscn > "$log_file" 2>&1
run_status=$?
set -e
cat "$log_file"
if [[ "$run_status" -ne 0 ]]; then exit "$run_status"; fi
if ! rg -q 'RESULT: [1-9][0-9]* checks; 0 failures' "$log_file"; then exit 1; fi
if rg -q 'SCRIPT ERROR|ERROR:' "$log_file"; then exit 1; fi
