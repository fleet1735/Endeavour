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

$report = @{
  summary = @{
    pass = $overallPass
    target = $t
    timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
  }
  details = $details
}
New-Json $report | Write-FileUtf8 -Path $ReportPath

# gate_handshake 연동: summary.pass=true -> flag 생성
$flagPath = Join-Path $BASE "gate_pass.flag"
& $gate -ReportPath $ReportPath -OutFlag $flagPath

# --- graceful termination (CI vs Local) ---
$code = $(if($overallPass){0}else{1})
if($env:GITHUB_ACTIONS -eq "true"){
  # GitHub Actions 등 CI 환경: 종료코드로 종료
  exit $code
}else{
  # 로컬 인터랙티브: 창 자동 종료 금지, 종료코드만 반환
  Write-Host "Local run (no auto-close). ExitCode=$code"
  return $code
}

