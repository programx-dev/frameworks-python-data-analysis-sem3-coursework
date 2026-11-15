$ErrorActionPreference = 'Stop'
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
