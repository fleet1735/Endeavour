param(
  [string]$RepoRoot = "D:\Endeavour_Dev",
  [ValidateSet("smoke","full")] [string]$Mode = "full"
)

$ErrorActionPreference = "Stop"
$PSNativeCommandUseErrorActionPreference = $true

# ===== Config (must match project standard) =====
$AUDIT_ROOT    = "D:\GoogleDrive\Endeavour_Gov\audit"
$AUDIT_LOG_DIR = Join-Path $AUDIT_ROOT "audit_logs"

# SSOT v8.2 규범: CVStampV2 literal (문자 그대로; 공백/개행 불가)
$CV_STAMP_LITERAL = '{"purged_kfold":{"folds":5},"embargo_days":10,"nested_wf":{"windows":3},"seed":42}'

# Excel Params 5+1 필드 요구(필수 키)
$EXCEL_REQUIRED_KEYS = @("cv_stamp","data_hash","code_hash","param_hash","universe_hash","seed")

# 파일 검색 패턴 (일반화)
$TEXT_PATTERNS   = @("*.md","*.json","*.yaml","*.yml","*.txt")
$PARAMS_CANDIDATES = @("excel_params*.json","*params_excel*.json","*excel*params*.json")
$LEDGER_CANDIDATES = @("*ledger*.json","*ledger*.md")
$REPORT_CANDIDATES = @("*report*.json","*report*.md","*summary*.json")

# ===== Checks =====
$errors = New-Object System.Collections.Generic.List[string]
$notes  = New-Object System.Collections.Generic.List[string]

# 1) 기본 경로 존재
foreach($p in @("$RepoRoot","$RepoRoot\.git", $AUDIT_ROOT, $AUDIT_LOG_DIR)){
  if(!(Test-Path $p)){ $errors.Add("E-PRE-001: Missing path: $p") }
}

# 2) CVStampV2 literal 존재 여부(RepoRoot 전역 + Gov audit/docs 일부 텍스트 파일 탐색)
$cv_found = $false
try{
  $scanRoots = @($RepoRoot, "D:\GoogleDrive\Endeavour_Gov\docs", $AUDIT_ROOT)
  foreach($root in $scanRoots){
    if(Test-Path $root){
      foreach($pat in $TEXT_PATTERNS){
        Get-ChildItem -Path $root -Recurse -File -Filter $pat -ErrorAction SilentlyContinue |
          ForEach-Object {
            try{
              $txt = Get-Content $_.FullName -Raw -Encoding UTF8
              if($txt -like "*$CV_STAMP_LITERAL*"){ $cv_found = $true; throw [System.Exception]::new("break") }
            }catch{}
          }
      }
    }
  }
}catch{}

if(-not $cv_found){
  if($Mode -eq "full"){ $errors.Add("E-CV-101: CVStampV2 literal not found") } else { $notes.Add("WARN: CVStampV2 literal not found (smoke)") }
}

# 3) Excel Params 5+1 필드 검사 (후보 JSON 자동 탐색)
function Test-JsonFileHasKeys($file, $keys){
  try{
    $j = Get-Content $file -Raw -Encoding UTF8 | ConvertFrom-Json
    foreach($k in $keys){
      if(-not ($j.PSObject.Properties.Name -contains $k)){ return $false }
    }
    return $true
  }catch{ return $false }
}

$excel_ok = $false
$paramFiles = @()
foreach($pat in $PARAMS_CANDIDATES){
  $paramFiles += Get-ChildItem -Path $RepoRoot -Recurse -File -Filter $pat -ErrorAction SilentlyContinue
}
$paramFiles = $paramFiles | Select-Object -ExpandProperty FullName -Unique

foreach($pf in $paramFiles){
  if(Test-JsonFileHasKeys $pf $EXCEL_REQUIRED_KEYS){ $excel_ok = $true; break }
}
if(-not $excel_ok){
  if($Mode -eq "full"){ $errors.Add("E-AUDIT-502: Excel Params 5+1 missing or invalid") } else { $notes.Add("WARN: Excel Params (5+1) not verified (smoke)") }
}

# 4) summary_hash 체인 체크 (Excel ↔ Ledger ↔ Report)
function Find-FirstJsonByPatterns($root, $patterns){
  foreach($pat in $patterns){
    $f = Get-ChildItem -Path $root -Recurse -File -Filter $pat -ErrorAction SilentlyContinue | Select-Object -First 1
    if($f){ return $f.FullName }
  }
  return $null
}
function Read-SummaryHash($file){
  if(-not $file){ return $null }
  try{
    $txt = Get-Content $file -Raw -Encoding UTF8
    try{
      $j = $txt | ConvertFrom-Json
      if($j.summary_hash){ return [string]$j.summary_hash }
      if($j.summaryHash){ return [string]$j.summaryHash }
    }catch{
      # JSON이 아니면 텍스트에서 summary_hash=... 패턴 추출
      if($txt -match 'summary_hash\s*[:=]\s*"?([A-Fa-f0-9]{16,})"?'){ return $Matches[1] }
    }
  }catch{}
  return $null
}

$excel_json = (Find-FirstJsonByPatterns $RepoRoot @("excel_export*.json","*excel*summary*.json"))
$ledger_any = Find-FirstJsonByPatterns $RepoRoot $LEDGER_CANDIDATES
$report_any = Find-FirstJsonByPatterns $RepoRoot $REPORT_CANDIDATES

$h_excel  = Read-SummaryHash $excel_json
$h_ledger = Read-SummaryHash $ledger_any
$h_report = Read-SummaryHash $report_any

if(($h_excel) -and ($h_ledger) -and ($h_report)){
  if( ($h_excel -ne $h_ledger) -or ($h_excel -ne $h_report) ){
    $errors.Add("E-HASH-201: summary_hash mismatch (excel=$h_excel, ledger=$h_ledger, report=$h_report)")
  }
}else{
  $notes.Add("INFO: summary_hash chain incomplete (excel=$h_excel, ledger=$h_ledger, report=$h_report)")
}

# 5) 감사 로그 경로 접근성(쓰기 가능)
try{
  $probe = Join-Path $AUDIT_LOG_DIR ("probe_"+(Get-Date -Format "yyyyMMdd_HHmmss_fff")+".tmp")
  "probe" | Set-Content -Path $probe -Encoding UTF8
  Remove-Item $probe -Force -ErrorAction SilentlyContinue
}catch{
  $errors.Add("E-PRE-104: Audit logs root not accessible: $AUDIT_LOG_DIR")
}

# ===== Output =====
$status = if($errors.Count -gt 0){"FAIL"} else {"OK"}
$out = [ordered]@{
  stage       = "Reflex-Pre"
  status      = $status
  mode        = $Mode
  error_codes = $errors
  notes       = $notes
  ts          = (Get-Date).ToString("s")
  audit_log_dir = $AUDIT_LOG_DIR
} | ConvertTo-Json -Depth 8

# 로컬 로그와 감사 로그에 동시 기록
try{
  $localLog = Join-Path (Join-Path $PSScriptRoot "..\logs") ("reflex_pre_"+(Get-Date -Format "yyyyMMdd_HHmmss")+".json")
  $out | Set-Content -Path $localLog -Encoding UTF8
}catch{}
try{
  $auditLog = Join-Path $AUDIT_LOG_DIR ("reflex_pre_"+(Get-Date -Format "yyyyMMdd_HHmmss")+".json")
  $out | Set-Content -Path $auditLog -Encoding UTF8
}catch{}

Write-Host $out
if($status -eq "FAIL"){ exit 1 } else { exit 0 }