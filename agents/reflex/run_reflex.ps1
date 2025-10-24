param(
  [ValidateSet("pre","post","learn")] [string]$Stage = "pre",
  [string]$RepoRoot = "D:\Endeavour_Dev",
  [string]$Mode = "smoke"
)
$PSNativeCommandUseErrorActionPreference = $true
$ErrorActionPreference = "Stop"
$SRC = Join-Path $PSScriptRoot "src"
$LOG = Join-Path (Join-Path $PSScriptRoot "logs") ("reflex_"+$Stage+"_"+(Get-Date -Format "yyyyMMdd_HHmmss")+".json")

switch($Stage){
  "pre"   { $res = & (Join-Path $SRC "reflex_pre.ps1") -RepoRoot $RepoRoot -Mode $Mode }
  "post"  { $res = & (Join-Path $SRC "reflex_post.ps1") -RepoRoot $RepoRoot }
  "learn" { $res = & (Join-Path $SRC "reflex_learn.ps1") -RepoRoot $RepoRoot }
}
if($LASTEXITCODE -ne 0){ $status="FAIL" } else { $status="OK" }

$res | Set-Content -Path $LOG -Encoding UTF8
Write-Host $res
exit ([int]($status -eq "FAIL"))