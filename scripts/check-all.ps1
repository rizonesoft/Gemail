#Requires -Version 7.0
<#
.SYNOPSIS
  Runs every local gate: build, type check, lint, tests, manifest, and the plan tooling.
.DESCRIPTION
  1. npm run build            (webpack production build; skipped with -SkipBuild)
  2. npx tsc --noEmit         (type check the whole project)
  3. npm run lint             (office-addin-lint: ESLint + Prettier)
  4. npx jest --ci            (the whole unit suite)
  5. npm run validate         (office-addin-manifest validate manifest.xml; skipped with -SkipManifest,
                               because the validator calls an online service)
  6. python scripts/todo-graph.py self-test
  7. python scripts/todo-graph.py validate
  8. python scripts/todo-graph.py plan --check
  9. python scripts/todo-claims.py
  10. python scripts/todo-findings.py --check
  11. python scripts/todo-runs.py --check
  12. python scripts/campaign_guard.py --self-test
  A python gate whose script is absent is skipped with a warning. Every gate
  runs even after an earlier failure; the exit code is 1 when any gate failed.
.EXAMPLE
  pwsh scripts/check-all.ps1
  pwsh scripts/check-all.ps1 -SkipBuild -SkipManifest
#>
[CmdletBinding()]
param(
  [switch]$SkipBuild,
  [switch]$SkipManifest
)
$ErrorActionPreference = 'Stop'
. "$PSScriptRoot/_common.ps1"

$results = [System.Collections.Generic.List[object]]::new()

function Invoke-Gate([string]$Name, [scriptblock]$Body) {
  Write-Step $Name
  $sw = [Diagnostics.Stopwatch]::StartNew()
  $status = 'PASS'
  try {
    $global:LASTEXITCODE = 0
    & $Body
    if ($LASTEXITCODE -ne 0) { $status = "FAIL (exit $LASTEXITCODE)" }
  } catch {
    $status = "FAIL ($($_.Exception.Message))"
  }
  $results.Add([pscustomobject]@{ Gate = $Name; Status = $status; Seconds = [math]::Round($sw.Elapsed.TotalSeconds, 1) })
}

function Invoke-PythonGate([string]$Name, [string]$Script, [string[]]$Arguments) {
  $path = Join-Path $RepoRoot "scripts/$Script"
  if (-not (Test-Path $path)) {
    Write-Warning "check-all: $Script not found; skipping '$Name'"
    $results.Add([pscustomobject]@{ Gate = $Name; Status = 'SKIP (script absent)'; Seconds = 0 })
    return
  }
  $py = $script:Python
  Invoke-Gate $Name ({ & $py $path @Arguments }.GetNewClosure())
}

$script:Python = if (Get-Command python -ErrorAction SilentlyContinue) { 'python' } elseif (Get-Command python3 -ErrorAction SilentlyContinue) { 'python3' } else { $null }

Push-Location $RepoRoot
try {
  if (-not (Test-Path (Join-Path $RepoRoot 'node_modules'))) {
    Write-Warning 'check-all: node_modules is missing; run npm ci first'
  }
  if (-not $SkipBuild) {
    Invoke-Gate 'build (webpack production)' { npm run --silent build }
  }
  Invoke-Gate 'typecheck (tsc --noEmit)' { npx --no-install tsc --noEmit }
  Invoke-Gate 'lint (office-addin-lint)' { npm run --silent lint }
  Invoke-Gate 'test (jest)' { npx --no-install jest --ci }
  if (-not $SkipManifest) {
    Invoke-Gate 'manifest validate' { npm run --silent validate }
  }

  if ($script:Python) {
    Invoke-PythonGate 'todo-graph self-test' 'todo-graph.py' @('self-test')
    Invoke-PythonGate 'todo-graph validate' 'todo-graph.py' @('validate')
    Invoke-PythonGate 'todo-graph plan --check' 'todo-graph.py' @('plan', '--check')
    Invoke-PythonGate 'todo-claims' 'todo-claims.py' @()
    Invoke-PythonGate 'todo-findings --check' 'todo-findings.py' @('--check')
    Invoke-PythonGate 'todo-runs --check' 'todo-runs.py' @('--check')
    Invoke-PythonGate 'campaign_guard self-test' 'campaign_guard.py' @('--self-test')
  } else {
    Write-Warning 'check-all: python not found on PATH; skipping plan gates'
    $results.Add([pscustomobject]@{ Gate = 'python gates'; Status = 'SKIP (no python)'; Seconds = 0 })
  }
} finally {
  Pop-Location
}

$results | Format-Table -AutoSize | Out-String | Write-Host
$failed = @($results | Where-Object { $_.Status -like 'FAIL*' })
if ($failed.Count -gt 0) {
  Write-Host "check-all: $($failed.Count) gate(s) failed" -ForegroundColor Red
  exit 1
}
Write-Host 'check-all: all gates passed' -ForegroundColor Green
exit 0
