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
# === BEGIN: DETERMINISTIC REPORT WRITE BLOCK ===
# (1) details 최소 보장
if(-not $details){ $details = @{} }
if(-not $details.ContainsKey("engine")){ $details.engine = @{ note = "engine smoke executed" } }

# (2) summary를 명시적으로 구성 (결정론적)
$summary = [ordered]@{
  pass      = $overallPass
  target    = $t
  timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
}

# (3) 리포트 객체(PSCustomObject) → JSON
$report = [pscustomobject]@{
  summary = $summary
  details = $details
}
($report | ConvertTo-Json -Depth 12 -Compress) | Set-Content -Path $ReportPath -Encoding UTF8

# (4) Gate 연동: report 존재 시에만
$flagPath = Join-Path $BASE "gate_pass.flag"
if(Test-Path $ReportPath){
  & $gate -ReportPath $ReportPath -OutFlag $flagPath
} else {
  Write-Warning "report not found — skip gate"
}

# (5) 로컬/CI 종료 동작 통일
$code = $(if($overallPass){0}else{1})
if($env:GITHUB_ACTIONS -eq "true"){ exit $code } else {
  Write-Host "Local run (no auto-close). ExitCode=$code"
  $global:LASTEXITCODE = $code
  return $code
}
# === END: DETERMINISTIC REPORT WRITE BLOCK ===
}
}





