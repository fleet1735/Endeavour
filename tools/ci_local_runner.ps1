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

# Ensure paths
$tools = Join-Path $BASE "tools"
$smoke = Join-Path $tools "smoke_engine.ps1"
$gate  = Join-Path $tools "gate_handshake.ps1"
if(!(Test-Path $smoke)){ throw "Smoke script not found: $smoke" }
if(!(Test-Path $gate )){ throw "Gate script not found:  $gate"  }

$overallPass = $true
$details = @{}

switch($t){
  "engine" {
    # Run smoke (imports, CV consistency, vectorbt presence)
    $env:PYTHONPATH = "$BASE;$($env:PYTHONPATH)"
    Push-Location $BASE

    # smoke_engine.ps1 내부가 3개 파이썬 블록을 실행:
    # 각 블록 실패 시 python은 non-zero로 종료 -> $LASTEXITCODE로 감지
    & $smoke -N 1000 -BASE $BASE
    $exitCode = $LASTEXITCODE
    Pop-Location

    $passed = ($exitCode -eq 0)
    $details.engine = @{ smoke_exit = $exitCode; note = "0 means all assertions passed" }
    if(-not $passed){ $overallPass = $false }
  }
  "all" {
    # 확장 시 다른 타깃도 추가
    Write-Host "[info] only 'engine' target implemented currently."
  }
}

# Compose report.json (gate가 참조하는 summary.pass 필드 포함)
$report = @{
  summary = @{
    pass = $overallPass
    target = $t
    timestamp = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
  }
  details = $details
}
New-Json $report | Write-FileUtf8 -Path $ReportPath

# Gate handshake: summary.pass=true면 flag 생성
$flagPath = Join-Path $BASE "gate_pass.flag"
& $gate -ReportPath $ReportPath -OutFlag $flagPath

if($overallPass){
  Write-Host "✅ CI(engine) PASS — report: $ReportPath, flag: $flagPath"
  exit 0
}else{
  Write-Host "❌ CI(engine) FAIL — report: $ReportPath"
  exit 1
}
