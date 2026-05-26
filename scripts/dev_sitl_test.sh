#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR/.."

for d in sitl/scenarios/*/; do
    manifest="$d/manifest.yaml"
    [ -f "$manifest" ] || continue
    type=$(awk -F: '/^type:/ {gsub(/[" ]/, "", $2); print $2; exit}' "$manifest")
    if [ "$type" != "pytest" ]; then
        continue
    fi
    name="$(basename "$d")"
    echo "--- Running SITL scenario: $name ---"
    zydro sitl run "$name"
done
