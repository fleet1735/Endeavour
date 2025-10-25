param(
  [ValidateSet("engine","all")][string]$t = "engine",
  [string]$BASE = "D:\Endeavour_Dev",
  [string]$ReportPath = ""
)

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

# ------------------------------------
# Run-Engine (stdout/stderr 캡처 포함)
# ------------------------------------
function Run-Engine {
  param([string]$BASE)
  $tools = Join-Path $BASE "tools"
  $smoke = Join-Path $tools "smoke_engine.ps1"
  if(!(Test-Path $smoke)){ throw "Smoke script not found: $smoke" }

  $logDir = Join-Path $BASE "logs"
  if(!(Test-Path $logDir)){ New-Item -ItemType Directory -Force -Path $logDir | Out-Null }
  $ts = (Get-Date -Format "yyyyMMdd_HHmmss")
  $outLog = Join-Path $logDir ("smoke_engine_" + $ts + ".out.log")
  $errLog = Join-Path $logDir ("smoke_engine_" + $ts + ".err.log")

  Push-Location $BASE
  $env:PYTHONPATH = "$BASE;$($env:PYTHONPATH)"
  & $smoke -N 1000 -BASE $BASE 1> $outLog 2> $errLog
  $exit = $LASTEXITCODE
  Pop-Location

  $tailOut = (Get-Content $outLog -Tail 100 -ErrorAction SilentlyContinue) -join "`n"
  $tailErr = (Get-Content $errLog -Tail 100 -ErrorAction SilentlyContinue) -join "`n"

  return @{
    smoke_exit = $exit
    out_log    = $outLog
    err_log    = $errLog
    log_tail   = @{ stdout = $tailOut; stderr = $tailErr }
  }
}

# ------------------------------------
# 집계 (engine/all 동일 정책)
# ------------------------------------
$details = @{}
switch($t){
  "engine" {
    $info = Run-Engine -BASE $BASE
    $details.engine = $info
    $overallPass = ($info.smoke_exit -eq 0)
  }
  "all" {
    $info = Run-Engine -BASE $BASE
    $details.engine = $info
    $overallPass = ($info.smoke_exit -eq 0)
  }
}

# === BEGIN: DETERMINISTIC REPORT WRITE BLOCK ===
# 최소 details 보장
if(-not $details){ $details = @{} }
if(-not $details.ContainsKey("engine")){ $details.engine = @{ note = "engine smoke executed" } }

# summary 결정론 구성
$summary = [ordered]@{
  pass      = $overallPass
  target    = $t
  timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
}

# 리포트 JSON 기록
$report = [pscustomobject]@{
  summary = $summary
  details = $details
}
($report | ConvertTo-Json -Depth 12 -Compress) | Set-Content -Path $ReportPath -Encoding UTF8

# Gate 동기화: FAIL이면 플래그 삭제, PASS면 생성/갱신
$flagPath = Join-Path $BASE "gate_pass.flag"
if(-not $overallPass){
  if(Test-Path $flagPath){ Remove-Item $flagPath -Force -ErrorAction SilentlyContinue }
}else{
  & $gate -ReportPath $ReportPath -OutFlag $flagPath
}

# 종료 정책: CI=exit, Local=return (창 유지 + 코드 반영)
$code = $(if($overallPass){0}else{1})
if($env:GITHUB_ACTIONS -eq "true"){
  exit $code
}else{
  Write-Host "Local run (no auto-close). ExitCode=$code"
  $global:LASTEXITCODE = $code
  return $code
}
# === END: DETERMINISTIC REPORT WRITE BLOCK ===
