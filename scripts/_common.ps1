# Shared helpers for scripts/*.ps1. Dot-source it: . "$PSScriptRoot/_common.ps1"
Set-StrictMode -Version Latest

$script:RepoRoot = Split-Path -Parent $PSScriptRoot

function Write-Step([string]$Message) {
  Write-Host "==> $Message" -ForegroundColor Cyan
}

function Invoke-Native {
  # Runs a native command and throws on a non-zero exit code. Deliberately a
  # simple function (no param block) so flags like -o reach the command as-is.
  $file, $rest = $args
  & $file @rest
  if ($LASTEXITCODE -ne 0) { throw "$file $($rest -join ' ') failed with exit code $LASTEXITCODE" }
}

function Get-AppVersion {
  # The one version source: package.json. `npm version` syncs the manifests
  # and the task pane footer from it (scripts/sync-manifest-version.js).
  return (Get-Content (Join-Path $script:RepoRoot 'package.json') -Raw | ConvertFrom-Json).version
}
