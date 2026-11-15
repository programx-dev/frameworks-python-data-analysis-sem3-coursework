#!/usr/bin/env bash
set -euo pipefail

# Отдельное окружение Label Studio установлено в WSL.
PROJECT_ROOT="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
LABEL_STUDIO_BIN="${LABEL_STUDIO_BIN:-$HOME/tools/label-studio/.venv/bin/label-studio}"

if [[ ! -x "$LABEL_STUDIO_BIN" ]]; then
    printf 'Не найден Label Studio: %s\n' "$LABEL_STUDIO_BIN" >&2
    printf 'Установите его в ~/tools/label-studio/.venv или задайте LABEL_STUDIO_BIN.\n' >&2
    exit 1
fi

mkdir -p "$PROJECT_ROOT/data/images"
export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
export LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT="$PROJECT_ROOT/data"

printf 'Проект: %s\n' "$PROJECT_ROOT"
printf 'Фотографии: %s/data/images\n' "$PROJECT_ROOT"
printf 'Интерфейс после запуска: http://localhost:8080\n'
printf 'Остановка: Ctrl+C\n'

exec "$LABEL_STUDIO_BIN" start --no-browser --port 8080
