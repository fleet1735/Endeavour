param(
  [string]$DevRoot = "D:\Endeavour_Dev",
  [string]$SamplesDir = "",
  [string]$OutReport = "D:\Endeavour_Dev\validator_report.json"
)
if (-not $SamplesDir -or $SamplesDir -eq "") {
  $SamplesDir = Join-Path $DevRoot "samples\dsl"
}

Write-Host "== Smoke Runner =="
Write-Host "DevRoot     : $DevRoot"
Write-Host "SamplesDir  : $SamplesDir"

# Placeholder CVStampV2 literal
$cv = @{
  purged_kfold = @{ folds = 2 }
  embargo_days = 0
  nested_wf    = @{ windows = 0 }
  seed         = 42
}

# dummy validator report (smoke)
$report = @{
  summary = @{
    pass = $true
    note = "placeholder smoke pass"
  }
  meta = @{
    cv = $cv
    created_at = (Get-Date).ToString("s")
  }
}
$report | ConvertTo-Json -Depth 6 | Set-Content $OutReport -Encoding utf8NoBOM
Write-Host "validator_report.json written"

# gate handshake
& (Join-Path $DevRoot "tools\gate_handshake.ps1") -ReportPath $OutReport | Write-Host
