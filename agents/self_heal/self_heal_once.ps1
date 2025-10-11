param(
  [switch]$WhatIf,
  [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSCommandPath
$main = Join-Path $root 'self_heal.ps1'

if (!(Test-Path $main)) { Write-Warning "[self_heal_once] self_heal.ps1 not found"; exit 0 }
if ($WhatIf -or $DryRun) { Write-Host "[self_heal_once] DryRun"; exit 0 }

# (향후) 실제 1회 실행 위임: & $main -Once
Write-Host "[self_heal_once] ok"
exit 0
