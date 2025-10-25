param(
  [ValidateSet("engine","all")][string]$t = "engine",
  [string]$BASE = "D:\Endeavour_Dev",
  [string]$ReportPath = ""
)

function New-Json([hashtable]$obj){ ($obj | ConvertTo-Json -Depth 10) }
function Write-FileUtf8($Path, [string]$Content){
  $dir = Split-Path -Parent $Path
  if(!(Test-Path $dir)){ New-Item -ItemType Directory -Force -Path $dir | Out-Null }
  Set-Content -Path $Path -Value $Content -Encoding UTF8
}

if([string]::IsNullOrWhiteSpace($ReportPath)){
  $ReportPath = Join-Path $BASE "ci_report.json"
}

$tools = Join-Path $BASE "tools"
$smoke = Join-Path $tools "smoke_engine.ps1"
$gate  = Join-Path $tools "gate_handshake.ps1"
if(!(Test-Path $smoke)){ throw "Smoke script not found: $smoke" }
if(!(Test-Path $gate )){ throw "Gate script not found:  $gate"  }

$overallPass = $true
$details = @{}

function Run-Engine {
  param([string]$BASE)
  $env:PYTHONPATH = "$BASE;$($env:PYTHONPATH)"
  Push-Location $BASE
  & (Join-Path $BASE "tools\smoke_engine.ps1") -N 1000 -BASE $BASE
  $exit = $LASTEXITCODE
  Pop-Location
  return $exit
}

switch($t){
  "engine" {
    $e = Run-Engine -BASE $BASE
    $details.engine = @{ smoke_exit = $e; note = "0 means all assertions passed" }
    if($e -ne 0){ $overallPass = $false }
  }
  "all" {
    # 현재는 engine만 포함. 추후 validator/export 등 단계 추가 예정.
    $e = Run-Engine -BASE $BASE
    $details.engine = @{ smoke_exit = $e; note = "0 means all assertions passed" }
    if($e -ne 0){ $overallPass = $false }
  }
}

# Compose details if missing
if(-not $details){ $details = @{} }
# Ensure engine block has some note for visibility
if(-not $details.ContainsKey("engine")){ Append-Detail -Details $details -Key "engine" -Msg "engine smoke not executed or missing block" }

# Compose summary & report object
$report = @{
  summary = @{
    pass = $overallPass
    target = $t
    timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
  }
  details = $details
}

# Write report robustly (retry + fallback)
$wrote = Write-RobustReport -Path $ReportPath -Obj $report
if(-not $wrote){
  # last-resort fallback content
  $fallback = '{"summary":{"pass":false,"target":"' + $t + '","timestamp":"' + (Get-Date).ToString("yyyy-MM-dd HH:mm:ss") + '","note":"report-write-failed"},"details":{}}'
  $fallback | Set-Content -Path $ReportPath -Encoding UTF8
}

# Verify report readability and inject quick reason when FAIL
try {
  $rp = Get-Content $ReportPath -Raw | ConvertFrom-Json
  if(-not $overallPass){
    if(-not $rp.details){ $rp | Add-Member -NotePropertyName details -NotePropertyValue @{} }
    $rp.details.fail_reason = "one or more smoke steps returned non-zero (see .details.engine)"
    ($rp | ConvertTo-Json -Depth 12 -Compress) | Set-Content -Path $ReportPath -Encoding UTF8
  }
} catch {
  # leave as-is; gate will still run but pass likely false
}

# Gate handshake with explicit file presence check
$flagPath = Join-Path $BASE "gate_pass.flag"
if(Test-Path $ReportPath){
  & $gate -ReportPath $ReportPath -OutFlag $flagPath
}else{
  Write-Host "[warn] report not found, skipping gate"
}

# --- graceful termination (CI vs Local) ---
$code = $(if($overallPass){0}else{1})
if($env:GITHUB_ACTIONS -eq "true"){ exit $code } else {
  Write-Host "Local run (no auto-close). ExitCode=$code"
  $global:LASTEXITCODE = $code
  return $code
}
}




