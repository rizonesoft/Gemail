#Requires -Version 5.1
<#
.SYNOPSIS
  Verifies and repairs the developer toolchain for Gemail on Windows.
.DESCRIPTION
  Legs:
    node     Node.js on PATH whose major version satisfies package.json `engines.node`
             (repair: prints the winget command; Node is never installed silently).
    deps     node_modules present and installed on THIS platform (a tree copied from
             WSL carries Linux-only shims); repair runs `npm ci`.
    certs    the Office add-in localhost dev certificates trusted in the Windows store
             (`npx office-addin-dev-certs verify`); repair runs `install`, which prompts
             for elevation once.
    hooks    git core.hooksPath = tools/githooks and tools/githooks/pre-commit present.
    python   Python 3 on PATH (plan gates in scripts/check-all.ps1 and the commit hook).
  -Verify runs the checks only: exit 0 when all legs are green, 1 otherwise.
  Without -Verify, failing legs are repaired, then verified again.
  Run: pwsh tools/provision.ps1 [-Verify] [-SkipCerts]
#>
[CmdletBinding()]
param(
  [switch]$Verify,
  [switch]$SkipCerts
)
$ErrorActionPreference = 'Stop'
$Root = Split-Path -Parent $PSScriptRoot

function Get-EnginesMajor {
  $pkg = Get-Content (Join-Path $Root 'package.json') -Raw | ConvertFrom-Json
  $range = $null
  if ($pkg.PSObject.Properties.Name -contains 'engines') { $range = $pkg.engines.node }
  if (-not $range) { return 20 }
  if ($range -match '(\d+)') { return [int]$Matches[1] }
  return 20
}

function Test-NodeLeg {
  $want = Get-EnginesMajor
  $cmd = Get-Command node -ErrorAction SilentlyContinue
  if (-not $cmd) { return @{ Name = 'node'; Ok = $false; Detail = 'node not on PATH' } }
  $v = (& $cmd.Source --version).TrimStart('v')
  $major = [int]($v.Split('.')[0])
  if ($major -lt $want) { return @{ Name = 'node'; Ok = $false; Detail = "node $v is below the engines floor $want" } }
  return @{ Name = 'node'; Ok = $true; Detail = "node $v ($($cmd.Source))" }
}

function Test-DepsLeg {
  $bin = Join-Path $Root 'node_modules/.bin'
  if (-not (Test-Path $bin)) { return @{ Name = 'deps'; Ok = $false; Detail = 'node_modules missing' } }
  if (-not (Test-Path (Join-Path $bin 'webpack.cmd'))) {
    return @{ Name = 'deps'; Ok = $false; Detail = 'node_modules has no Windows shims (installed under WSL?)' }
  }
  return @{ Name = 'deps'; Ok = $true; Detail = 'node_modules installed for Windows' }
}

function Test-CertsLeg {
  if ($SkipCerts) { return @{ Name = 'certs'; Ok = $true; Detail = 'skipped (-SkipCerts)' } }
  Push-Location $Root
  try {
    $out = (& npx --no-install office-addin-dev-certs verify 2>&1 | Out-String)
  } finally { Pop-Location }
  if ($out -match 'need to install') { return @{ Name = 'certs'; Ok = $false; Detail = 'dev certificates not trusted in the Windows store' } }
  return @{ Name = 'certs'; Ok = $true; Detail = 'dev certificates trusted' }
}

function Test-HooksLeg {
  $hp = (& git -C $Root config core.hooksPath) 2>$null
  $hook = Join-Path $Root 'tools/githooks/pre-commit'
  if ($hp -ne 'tools/githooks') { return @{ Name = 'hooks'; Ok = $false; Detail = "core.hooksPath is '$hp'" } }
  if (-not (Test-Path $hook)) { return @{ Name = 'hooks'; Ok = $false; Detail = 'tools/githooks/pre-commit missing' } }
  return @{ Name = 'hooks'; Ok = $true; Detail = 'core.hooksPath = tools/githooks' }
}

function Test-PythonLeg {
  foreach ($c in 'python', 'python3', 'py') {
    $cmd = Get-Command $c -ErrorAction SilentlyContinue
    if ($cmd) {
      $v = (& $cmd.Source --version 2>&1 | Out-String).Trim()
      if ($v -match 'Python 3') { return @{ Name = 'python'; Ok = $true; Detail = "$v ($($cmd.Source))" } }
    }
  }
  return @{ Name = 'python'; Ok = $false; Detail = 'no Python 3 on PATH' }
}

function Repair([string]$Leg) {
  switch ($Leg) {
    'node' { Write-Host "Install Node.js LTS: winget install OpenJS.NodeJS.LTS" -ForegroundColor Yellow }
    'deps' { Push-Location $Root; try { & npm ci } finally { Pop-Location } }
    'certs' { Push-Location $Root; try { & npx --no-install office-addin-dev-certs install } finally { Pop-Location } }
    'hooks' { & git -C $Root config core.hooksPath tools/githooks }
    'python' { Write-Host "Install Python 3: winget install Python.Python.3.13" -ForegroundColor Yellow }
  }
}

function Test-All { @((Test-NodeLeg), (Test-DepsLeg), (Test-CertsLeg), (Test-HooksLeg), (Test-PythonLeg)) }

$legs = Test-All
if (-not $Verify) {
  foreach ($l in $legs) { if (-not $l.Ok) { Write-Host "repairing $($l.Name): $($l.Detail)"; Repair $l.Name } }
  $legs = Test-All
}
foreach ($l in $legs) {
  $mark = if ($l.Ok) { 'ok  ' } else { 'FAIL' }
  Write-Host ("{0} {1,-7} {2}" -f $mark, $l.Name, $l.Detail)
}
if (@($legs | Where-Object { -not $_.Ok }).Count -gt 0) { exit 1 }
exit 0
