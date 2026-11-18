$ErrorActionPreference = 'Stop'
$projectRoot = (Resolve-Path -LiteralPath (Join-Path $PSScriptRoot '..')).Path
$env:LABEL_STUDIO_LOCAL_FILES_SERVING_ENABLED = 'true'
$env:LABEL_STUDIO_LOCAL_FILES_DOCUMENT_ROOT = Join-Path $projectRoot 'data'
$studioCommand = if ($env:LABEL_STUDIO_BIN) { $env:LABEL_STUDIO_BIN } else { 'label-studio' }
& $studioCommand start --no-browser --port 8080
exit $LASTEXITCODE
