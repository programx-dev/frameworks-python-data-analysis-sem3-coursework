#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -d "$SCRIPT_DIR/data/images" ]]; then
    PACKAGE_ROOT="$SCRIPT_DIR"
elif [[ -d "$SCRIPT_DIR/../../../data/images" ]]; then
    PACKAGE_ROOT="$(cd -- "$SCRIPT_DIR/../../.." && pwd)"
else
    printf 'Cannot find data/images next to the package or in the repository.\n' >&2
    exit 1
fi
export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
export LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT="$PACKAGE_ROOT/data"
exec "${LABEL_STUDIO_BIN:-label-studio}" start --no-browser --port 8080
