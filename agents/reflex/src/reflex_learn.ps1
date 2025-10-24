param(
  [string]$RepoRoot = "D:\Endeavour_Dev",
  [string]$ErrorsJson = ""
)
$ErrorActionPreference = "Stop"
$AUDIT_ROOT    = "D:\GoogleDrive\Endeavour_Gov\audit"
$AUDIT_LOG_DIR = Join-Path $AUDIT_ROOT "audit_logs"
$MEMO_DIR = Join-Path $PSScriptRoot "..\logs\learn_signatures"
if(!(Test-Path $MEMO_DIR)){ New-Item -ItemType Directory -Path $MEMO_DIR | Out-Null }

# Aggregate latest FAIL logs (pre/post) → normalized signatures
function Parse-Log($path){
  try{ (Get-Content $path -Raw -Enc UTF8) | ConvertFrom-Json }catch{ $null }
}
$logs = Get-ChildItem (Join-Path $PSScriptRoot "..\logs") -File -Filter "reflex_*_*.json" -EA SilentlyContinue | Sort-Object LastWriteTime -Desc | Select-Object -First 10
$codes = @()
foreach($l in $logs){
  $obj = Parse-Log $l.FullName
  if($obj -and $obj.status -eq "FAIL" -and $obj.error_codes){
    $codes += $obj.error_codes
  }
}
$codes = $codes | Select-Object -Unique
$signature = [ordered]@{ ts=(Get-Date).ToString("s"); learned_codes=$codes } | ConvertTo-Json -Depth 8

# Save memory & audit
$memoFile = Join-Path $MEMO_DIR ("learn_"+(Get-Date -Format "yyyyMMdd_HHmmss")+".json")
$signature | Set-Content $memoFile -Enc UTF8
try{ $auditFile = Join-Path $AUDIT_LOG_DIR ("reflex_learn_"+(Get-Date -Format "yyyyMMdd_HHmmss")+".json"); $signature | Set-Content $auditFile -Enc UTF8 }catch{}

Write-Host $signature
exit 0