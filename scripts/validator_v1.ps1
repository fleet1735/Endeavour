param()
$ErrorActionPreference = "Stop"

$DEV_BASE  = Split-Path -Parent $PSCommandPath | Split-Path -Parent  # /scripts -> repo root
$GOV_AUDIT = "D:\GoogleDrive\Endeavour_Gov\audit\audit_logs"

$CI_PATH   = Join-Path $DEV_BASE "ci_report.json"
$DBG_DIR   = Join-Path $DEV_BASE "_dbg_smoke_v2_6r2"
$DBG_JSON  = Join-Path $DBG_DIR "engine_debug.json"
$SUM1      = Join-Path $DBG_DIR "summary_run1.csv"
$SUM2      = Join-Path $DBG_DIR "summary_run2.csv"
$VAL_REPORT= Join-Path $DEV_BASE "validator_report.json"
$SCHEMA    = Join-Path $DEV_BASE "validator_schema_v1.json"

function Write-JsonNoBom($Path, $Object, [int]$Depth=64){
  $json = $Object | ConvertTo-Json -Depth $Depth -Compress
  [System.IO.File]::WriteAllText($Path,$json,(New-Object System.Text.UTF8Encoding($false)))
}
function Iso8601Like($s){ return ($s -match "^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?([+-]\d{2}:\d{2}|Z)$") }

# 기본 스키마(없다면 생성)
if (-not (Test-Path $SCHEMA)) {
  $schema = @{
    title="Sprint4 Validator Schema v1"; description="ci_report.json 및 산출물 규칙";
    required_files=@($CI_PATH,$DBG_JSON,$SUM1,$SUM2);
    ci_report=@{
      summary=@{ required=@("pass","target","timestamp"); target_prefix=@("Sprint3_Smoke_v2_6r2_","Sprint3_Smoke_v2_6r2") };
      details=@{
        engine=@{ required=@("exit_code","determinism","summary_hash","freq"); determinism_must_be_true=$true };
        reflex_pre=@{ required=@("dev_log","gov_log","exit_code"); both_logs_must_exist=$true };
        ssot=@{
          required=@("cv_stamp_literal","excel_params_required");
          cv_stamp_literal_exact='{"purged_kfold":{"folds":5},"embargo_days":10,"nested_wf":{"windows":3},"seed":42}';
          excel_params_required_set=@("cv_stamp","data_hash","code_hash","param_hash","universe_hash","seed?");
        }
      }
    }
  }
  Write-JsonNoBom -Path $SCHEMA -Object $schema -Depth 64
}

$errors = New-Object System.Collections.Generic.List[string]
$warns  = New-Object System.Collections.Generic.List[string]

# 필수 파일
foreach($f in (Get-Content $SCHEMA | ConvertFrom-Json).required_files){ if(-not (Test-Path $f)){ $errors.Add("E-FILE-404: $f") } }

# Reflex logs (최근 1개씩)
$reflex_dev = Get-ChildItem (Join-Path $DEV_BASE "reflex_pre_validation_log_*.json") -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
$reflex_gov = Get-ChildItem (Join-Path $GOV_AUDIT "reflex_pre_validation_log_*.json") -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending | Select-Object -First 1
if(-not $reflex_dev){ $errors.Add("E-REFLEX-404: Dev log not found") }
if(-not $reflex_gov){ $errors.Add("E-REFLEX-404: Gov log not found") }

# ci_report load
$ci=$null; if(Test-Path $CI_PATH){ try{$ci=Get-Content $CI_PATH -Raw | ConvertFrom-Json}catch{$errors.Add("E-CI-JSON: parse fail: $($_.Exception.Message)")}} else {$errors.Add("E-CI-404: not found")}

if($ci -ne $null){
  # summary
  foreach($k in @("pass","target","timestamp")){ if(-not ($ci.summary.PSObject.Properties.Name -contains $k)){ $errors.Add("E-CI-SUMMARY-MISS: '$k'") } }
  if($ci.summary.target -and -not ($ci.summary.target -like "Sprint3_Smoke_v2_6r2_*" -or $ci.summary.target -like "Sprint3_Smoke_v2_6r2")){
    $warns.Add("W-TARGET-PREFIX: '$($ci.summary.target)'")
  }
  if($ci.summary.timestamp -and -not (Iso8601Like $ci.summary.timestamp)){ $errors.Add("E-TIME-ISO8601: invalid timestamp") }

  # engine
  foreach($k in @("exit_code","determinism","summary_hash","freq")){ if(-not ($ci.details.engine.PSObject.Properties.Name -contains $k)){ $errors.Add("E-ENGINE-MISS: '$k'") } }
  if($ci.details.engine.determinism -ne $true){ $errors.Add("E-DET-FAIL: determinism must be true") }
  if(-not $ci.details.engine.summary_hash){ $errors.Add("E-ENGINE-HASH: empty summary_hash") }

  # reflex_pre
  foreach($k in @("dev_log","gov_log","exit_code")){ if(-not ($ci.details.reflex_pre.PSObject.Properties.Name -contains $k)){ $errors.Add("E-REFLEX-MISS: '$k'") } }
  if($ci.details.reflex_pre.dev_log -and -not (Test-Path $ci.details.reflex_pre.dev_log)){ $errors.Add("E-REFLEX-DEV-404: $($ci.details.reflex_pre.dev_log)") }
  if($ci.details.reflex_pre.gov_log -and -not (Test-Path $ci.details.reflex_pre.gov_log)){ $errors.Add("E-REFLEX-GOV-404: $($ci.details.reflex_pre.gov_log)") }

  # ssot
  if(-not $ci.details.ssot){ $errors.Add("E-CI-SSOT: missing block") }
  else {
    if($ci.details.ssot.cv_stamp_literal -ne '{"purged_kfold":{"folds":5},"embargo_days":10,"nested_wf":{"windows":3},"seed":42}'){
      $errors.Add("E-SSOT-CVSTAMP: literal mismatch")
    }
    $need=@("cv_stamp","data_hash","code_hash","param_hash","universe_hash","seed?")
    $have=@(); if($ci.details.ssot.excel_params_required){ $have=@($ci.details.ssot.excel_params_required) }
    foreach($req in $need){ if(-not ($have -contains $req)){ $errors.Add("E-SSOT-EXCEL-PARAMS: missing '$req'") } }
  }

  # Sprint3 기대
  if($ci.summary.pass -ne $true){ $errors.Add("E-CI-PASS: summary.pass should be true") }
}

$report=[pscustomobject]@{
  summary=[pscustomobject]@{
    pass=($errors.Count -eq 0)
    error_count=$errors.Count
    warn_count=$warns.Count
    timestamp=(Get-Date).ToString("o")
  }
  details=[pscustomobject]@{
    errors=@($errors); warnings=@($warns)
    inputs=[pscustomobject]@{
      ci_report_path=$CI_PATH; dbg_json_path=$DBG_JSON; summary_csvs=@($SUM1,$SUM2)
      reflex_dev_log=$(if($reflex_dev){$reflex_dev.FullName}else{"(not found)"})
      reflex_gov_log=$(if($reflex_gov){$reflex_gov.FullName}else{"(not found)"})
    }
  }
}
Write-JsonNoBom -Path (Join-Path $DEV_BASE "validator_report.json") -Object $report -Depth 64

if($report.summary.pass){ Write-Host "[VALIDATOR] PASS — $($report.summary.error_count) errors, $($report.summary.warn_count) warnings"; exit 0 }
else{ Write-Host "[VALIDATOR] FAIL — $($report.summary.error_count) errors, $($report.summary.warn_count) warnings"; exit 1 }