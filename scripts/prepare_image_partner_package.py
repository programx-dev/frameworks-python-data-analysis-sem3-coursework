"""Prepare independent image annotation tasks with persistent numeric sample IDs."""

import copy
import hashlib
import json
from pathlib import Path
import urllib.parse
import zipfile


ROOT = Path(__file__).resolve().parents[1]
ANNOTATIONS = ROOT / "data" / "annotations"
SOURCE = ANNOTATIONS / "image_markup_nikita.json"
REGISTRY = ANNOTATIONS / "image_sample_ids.json"
OUTPUT = ANNOTATIONS / "partner_images"
ARCHIVE = ANNOTATIONS / "aod4_partner_package.zip"

CONFIG = """<View>
  <Header value="$display_name"/>
  <Image name="photo" value="$image" zoom="true"/>

  <RectangleLabels name="objects" toName="photo">
    <Label value="bird" background="#52B788"/>
    <Label value="drone" background="#FF9F43"/>
  </RectangleLabels>

  <Header value="Источник фотографии"/>
  <Text name="source_url_display" value="$source_url"/>

  <Header value="Автор"/>
  <Text name="author_display" value="$author"/>

  <Header value="Лицензия"/>
  <Text name="license_display" value="$license"/>
</View>
"""

README = """# Независимая разметка пополнения AOD-4

В комплекте 103 фотографии, JSON задач и настройка интерфейса Label Studio.
Источник, автор и лицензия уже заполнены. Они показаны под фотографией и
сохраняются в разделе `data` при экспорте. Размечать нужно только рамки.

## Запуск

При работе через Git получите ветку с этими файлами и фотографиями.
Архив не нужен. Из корня своей копии репозитория запустите:

```bash
bash data/annotations/partner_images/start_label_studio.sh
```

Для Windows / PowerShell из корня репозитория:

```powershell
powershell -ExecutionPolicy Bypass -File data/annotations/partner_images/start_label_studio.ps1
```

Если данные переданы архивом, распакуйте его целиком и запустите скрипт
`start_label_studio.sh` или `start_label_studio.ps1` из распакованной папки.
Скрипты находят каталог `data` и в репозитории, и в распакованном комплекте.
Перед запуском остановите предыдущий экземпляр Label Studio, если он запущен.

Скрипты рассчитаны на установленный Label Studio. Если команда `label-studio`
не найдена, активируйте окружение, в котором он установлен, и повторите запуск.
Для WSL можно указать путь явно:

```bash
LABEL_STUDIO_BIN="$HOME/tools/label-studio/.venv/bin/label-studio" bash data/annotations/partner_images/start_label_studio.sh
```

На Windows аналогично можно задать переменную `LABEL_STUDIO_BIN` с полным
путём к `label-studio.exe`. Приложение откройте по http://localhost:8080.

## Создание проекта

1. Создайте новый пустой проект.
2. В Settings → Labeling Interface → Code вставьте содержимое
   `labeling_interface_partner.xml` и сохраните.
3. Через Import загрузите `image_tasks_partner.json` один раз.
4. Должно появиться 103 задачи без готовых рамок. Проверьте, что фотография
   открывается, а источник, автор и лицензия показаны под ней.

В репозитории JSON и XML находятся в `data/annotations/partner_images`.
Файл `image_markup_nikita.json` содержит готовую разметку Никиты;
для независимой разметки импортируется именно `image_tasks_partner.json`.

Папку Cloud Storage подключать и синхронизировать не нужно: ссылки на локальные
файлы уже находятся в JSON. Отдельно загружать изображения через Import тоже
не нужно. Запускайте Label Studio с тем же корнем `data`, пока идёт разметка.

## Разметка и экспорт

Обведите каждый видимый объект отдельной рамкой bird или drone и нажмите Submit.
Не меняйте имена файлов и sample_id. Строго сохраняйте те же изображения,
масштаб и границы кадра; увеличение в интерфейсе для удобства допустимо.

После завершения нажмите Export → JSON (полный формат, не JSON-MIN).
Итоговый файл можно назвать `image_markup_partner.json`.
В нём должны остаться `data.sample_id`, `data.image`, `data.source_url`,
`data.author`, `data.license`, а в `annotations` появятся ваши рамки.

## Идентификаторы

Общий sample_id — целое число от 1 до 103. Эти номера уже записаны в разметке
Никиты. Внутренние ID задач, аннотаций и рамок Label Studio могут отличаться.
Для сравнения фотографий используется sample_id; рамки сопоставляются по
положению и перекрытию. Назначать рамкам одинаковые ID вручную не нужно.
"""

BASH = """#!/usr/bin/env bash
set -euo pipefail
SCRIPT_DIR="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")" && pwd)"
if [[ -d "$SCRIPT_DIR/data/images" ]]; then
    PACKAGE_ROOT="$SCRIPT_DIR"
elif [[ -d "$SCRIPT_DIR/../../../data/images" ]]; then
    PACKAGE_ROOT="$(cd -- "$SCRIPT_DIR/../../.." && pwd)"
else
    printf 'Cannot find data/images next to the package or in the repository.\\n' >&2
    exit 1
fi
export LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED=true
export LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT="$PACKAGE_ROOT/data"
exec "${LABEL_STUDIO_BIN:-label-studio}" start --no-browser --port 8080
"""

POWERSHELL = """$ErrorActionPreference = 'Stop'
$packageRoot = if (Test-Path -LiteralPath (Join-Path $PSScriptRoot 'data/images')) {
    $PSScriptRoot
} elseif (Test-Path -LiteralPath (Join-Path $PSScriptRoot '../../../data/images')) {
    (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '../../..')).Path
} else {
    throw 'Cannot find data/images next to the package or in the repository.'
}
$env:LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED = 'true'
$env:LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT = Join-Path $packageRoot 'data'
$studioCommand = if ($env:LABEL_STUDIO_BIN) { $env:LABEL_STUDIO_BIN } else { 'label-studio' }
& $studioCommand start --no-browser --port 8080
exit $LASTEXITCODE
"""


def dump_json(value):
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"


def image_path(task):
    query = urllib.parse.parse_qs(urllib.parse.urlsplit(task["data"]["image"]).query)
    relative = query.get("d", [""])[0]
    if not relative:
        raise ValueError(f"Unsupported image URL: {task['data']['image']}")
    file = ROOT / "data" / relative
    if not file.resolve().is_relative_to((ROOT / "data").resolve()):
        raise ValueError(f"Image path outside data: {relative}")
    if not file.is_file():
        raise FileNotFoundError(file)
    return relative, file


def metadata(task, name):
    answers = [
        text.strip()
        for annotation in task["annotations"]
        if not annotation.get("was_cancelled", False)
        for result in annotation.get("result", [])
        if result.get("type") == "textarea" and result.get("from_name") == name
        for text in result.get("value", {}).get("text", [])
        if isinstance(text, str) and text.strip()
    ]
    if len(answers) != 1:
        raise ValueError(f"Expected one {name} answer for task {task['id']}")
    return answers[0]


def main():
    original = json.loads(SOURCE.read_text(encoding="utf-8"))
    updated = copy.deepcopy(original)
    registry = json.loads(REGISTRY.read_text()) if REGISTRY.exists() else []
    by_path = {row["image_path"]: row for row in registry}
    ids = [row["sample_id"] for row in registry]
    if len(by_path) != len(registry) or len(set(ids)) != len(ids):
        raise ValueError("Duplicate registry keys")
    if any(type(sample_id) is not int or sample_id <= 0 for sample_id in ids):
        raise ValueError("sample_id must be a positive integer")
    next_id = max(ids, default=0) + 1
    tasks = []
    files = []

    for task in updated:
        relative, file = image_path(task)
        checksum = hashlib.sha256(file.read_bytes()).hexdigest()
        record = by_path.get(relative)
        if record is None:
            record = {"sample_id": next_id, "image_path": relative, "sha256": checksum}
            registry.append(record)
            by_path[relative] = record
            next_id += 1
        elif record["sha256"] != checksum:
            raise ValueError(f"Image changed for sample_id {record['sample_id']}")

        sample_id = record["sample_id"]
        existing = task["data"].get("sample_id")
        if existing is not None and existing != sample_id:
            raise ValueError(f"Conflicting sample_id for {relative}")
        task["data"].update(
            sample_id=sample_id,
            file_name=file.name,
            display_name=f"sample_id: {sample_id} | {file.name}",
            source_url=metadata(task, "source_url"),
            author=metadata(task, "author"),
            license=metadata(task, "license"),
        )
        tasks.append({"data": copy.deepcopy(task["data"])})
        files.append((relative, file))

    sample_ids = [task["data"]["sample_id"] for task in tasks]
    if len(sample_ids) != len(set(sample_ids)):
        raise ValueError("Duplicate images or sample IDs in source export")
    for before, after in zip(original, updated):
        assert {k: v for k, v in before.items() if k != "data"} == {
            k: v for k, v in after.items() if k != "data"
        }
    assert all(set(task) == {"data"} for task in tasks)

    OUTPUT.mkdir(parents=True, exist_ok=True)
    package_files = {
        "image_tasks_partner.json": dump_json(tasks),
        "labeling_interface_partner.xml": CONFIG,
        "README.md": README,
        "start_label_studio.sh": BASH,
        "start_label_studio.ps1": POWERSHELL,
    }
    for name, text in package_files.items():
        (OUTPUT / name).write_text(text, encoding="utf-8")

    temporary_archive = ARCHIVE.with_suffix(".zip.tmp")
    with zipfile.ZipFile(temporary_archive, "w", compression=zipfile.ZIP_STORED) as archive:
        for name in package_files:
            archive.write(OUTPUT / name, f"aod4_partner/{name}")
        for relative, file in files:
            archive.write(file, f"aod4_partner/data/{relative}")
    with zipfile.ZipFile(temporary_archive) as archive:
        if archive.testzip() is not None:
            raise ValueError("Archive verification failed")
        assert len([name for name in archive.namelist() if "/data/images/" in name]) == len(tasks)
        assert json.loads(archive.read("aod4_partner/image_tasks_partner.json")) == tasks

    REGISTRY.write_text(dump_json(registry), encoding="utf-8")
    SOURCE.write_text(dump_json(updated), encoding="utf-8")
    temporary_archive.replace(ARCHIVE)
    print(dump_json({
        "tasks": len(tasks),
        "sample_id_min": min(sample_ids),
        "sample_id_max": max(sample_ids),
        "annotations_in_partner_file": 0,
        "source_annotations_unchanged": True,
        "archive_bytes": ARCHIVE.stat().st_size,
        "archive": str(ARCHIVE),
    }))


if __name__ == "__main__":
    main()
