param(
  [string]$RepoRoot = "D:\Endeavour_Dev"
)
$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

$AUDIT_ROOT    = "D:\GoogleDrive\Endeavour_Gov\audit"
$AUDIT_LOG_DIR = Join-Path $AUDIT_ROOT "audit_logs"
$CV_STAMP_LITERAL = '{"purged_kfold":{"folds":5},"embargo_days":10,"nested_wf":{"windows":3},"seed":42}'
$REQUIRED = @("cv_stamp","data_hash","code_hash","param_hash","universe_hash","seed")

function Find-File($root,$patterns){ foreach($pat in $patterns){ $f=Get-ChildItem -Path $root -Recurse -File -Filter $pat -EA SilentlyContinue | Select-Object -First 1; if($f){ return $f.FullName } } return $null }
function Read-Json($file){ try{ (Get-Content $file -Raw -Enc UTF8) | ConvertFrom-Json }catch{ $null } }
function Has-Keys($obj,$keys){ foreach($k in $keys){ if(-not ($obj.PSObject.Properties.Name -contains $k)){ return $false } } $true }
function Read-SummaryHash($file){
  if(-not $file){ return $null }
  $txt = Get-Content $file -Raw -Encoding UTF8
  try{ $j=$txt|ConvertFrom-Json; if($j.summary_hash){return [string]$j.summary_hash}; if($j.summaryHash){return [string]$j.summaryHash} }catch{}
  if($txt -match 'summary_hash\s*[:=]\s*"?([A-Fa-f0-9]{16,})"?'){ return $Matches[1] }
  $null
}

$errors=@(); $notes=@()
# Locate products (heuristics)
$excel = Find-File $RepoRoot @("excel_export*.json","*excel*summary*.json","*params*.json")
$ledger= Find-File $RepoRoot @("*ledger*.json","*ledger*.md")
$report= Find-File $RepoRoot @("*report*.json","*summary*.json")

# 1) Excel Params 5+1
$excel_obj = Read-Json $excel
if($excel_obj){ if(-not (Has-Keys $excel_obj $REQUIRED)){ $errors += "E-AUDIT-502: Excel Params 5+1 missing/invalid ($excel)" } }
else{ $notes += "INFO: Excel JSON not found (params check skipped)" }

# 2) cv_stamp literal
$cv_ok=$false
foreach($root in @($RepoRoot,"D:\GoogleDrive\Endeavour_Gov\docs",$AUDIT_ROOT)){
  if(Test-Path $root){
    Get-ChildItem -Path $root -Recurse -File -Include *.md,*.json,*.yml,*.yaml,*.txt -EA SilentlyContinue |
      ForEach-Object{
        try{ $t=Get-Content $_.FullName -Raw -Enc UTF8; if($t -like "*$CV_STAMP_LITERAL*"){ $cv_ok=$true; throw [Exception]"break" } }catch{}
      }
  }
}
if(-not $cv_ok){ $errors += "E-CV-101: CVStampV2 literal not found" }

# 3) summary_hash chain一致
$h_excel  = Read-SummaryHash $excel
$h_ledger = Read-SummaryHash $ledger
$h_report = Read-SummaryHash $report
if( ($h_excel) -and ($h_ledger) -and ($h_report) ){
  if( ($h_excel -ne $h_ledger) -or ($h_excel -ne $h_report) ){ $errors += "E-HASH-201: summary_hash mismatch (excel=$h_excel, ledger=$h_ledger, report=$h_report)" }
}else{
  $notes += "INFO: summary_hash chain incomplete (excel=$h_excel, ledger=$h_ledger, report=$h_report)"
}

$status = if($errors.Count){ "FAIL" } else { "OK" }
$out = [ordered]@{
  stage="Reflex-Post"; status=$status; error_codes=$errors; notes=$notes; ts=(Get-Date).ToString("s"); audit_log_dir=$AUDIT_LOG_DIR
} | ConvertTo-Json -Depth 8

try{ $localLog = Join-Path (Join-Path $PSScriptRoot "..\logs") ("reflex_post_"+(Get-Date -Format "yyyyMMdd_HHmmss")+".json"); $out | Set-Content $localLog -Enc UTF8 }catch{}
try{ $auditLog = Join-Path $AUDIT_LOG_DIR ("reflex_post_"+(Get-Date -Format "yyyyMMdd_HHmmss")+".json"); $out | Set-Content $auditLog -Enc UTF8 }catch{}
Write-Host $out
if($status -eq "FAIL"){ exit 1 } else { exit 0 }