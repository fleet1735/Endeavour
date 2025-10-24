param(
  [string]$RepoRoot = "D:\Endeavour_Dev",
  [string]$Mode = "smoke"  # smoke|full
)
$ErrorActionPreference = "Stop"
# Pre-checks: path, encoding, required scripts presence
$mustPaths = @(
  "$RepoRoot",
  "$RepoRoot\.git"
)
$errors = @()
foreach($p in $mustPaths){ if(!(Test-Path $p)){ $errors += "E-PRE-001: Missing path: $p" } }

# Encoding probe sample (no-op placeholder; real checks in Step 2)
# TODO(step2): scan *.py, *.ps1 for BOM and fix if needed

if($errors.Count -gt 0){
  $out = @{
    stage="Reflex-Pre"; status="FAIL"; error_codes=$errors; ts=(Get-Date).ToString("s")
  } | ConvertTo-Json -Depth 5
  $out
  exit 1
}else{
  $out = @{
    stage="Reflex-Pre"; status="OK"; error_codes=@(); ts=(Get-Date).ToString("s")
  } | ConvertTo-Json -Depth 5
  $out
  exit 0
}