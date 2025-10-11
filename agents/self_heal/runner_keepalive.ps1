param(
  [int]$IntervalSec = 300,
  [switch]$DryRun
)
$ErrorActionPreference = 'Stop'
$root = Split-Path -Parent $PSCommandPath
$main = Join-Path $root 'self_heal.ps1'

if ($DryRun) { Write-Host "[runner_keepalive] DryRun"; exit 0 }
if (!(Test-Path $main)) { Write-Warning "[runner_keepalive] self_heal.ps1 not found"; exit 0 }

# (필요시) 주기 점검 루프는 운영 스케줄러에서 관리
Write-Host "[runner_keepalive] ping ok (IntervalSec=$IntervalSec)"
exit 0
