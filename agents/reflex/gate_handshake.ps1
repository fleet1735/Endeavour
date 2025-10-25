param(
  [string]$PythonExe = "python",
  [string]$OutDir = ""
)
if ([string]::IsNullOrWhiteSpace($OutDir)) {
  $OutDir = "D:\GoogleDrive\Endeavour_Gov\audit\audit_logs"
}

Write-Host "== Endeavour Gate Handshake =="
Write-Host "Python :" $PythonExe
Write-Host "OutDir :" $OutDir

# Python 존재 확인
$pyv = & $PythonExe --version 2>$null
if ($LASTEXITCODE -ne 0) {
  Write-Error "Python 실행을 찾지 못했습니다. PATH를 확인하세요."
  exit 2
} else {
  Write-Host "[OK] $pyv"
}

# 엔진 실행
$runner = "D:\Endeavour_Dev\engine_core\parallel_backtest.py"
if (!(Test-Path $runner)) { Write-Error "엔진 러너가 없습니다: $runner"; exit 3 }

$cmd = "$PythonExe `"$runner`" --smoke --out `"$OutDir`""
Write-Host "[RUN]" $cmd
$proc = & $PythonExe $runner --smoke --out $OutDir
$code = $LASTEXITCODE
$proc | Write-Host

# 결과 점검
$report = Join-Path $OutDir "validator_report.json"
if (!(Test-Path $report)) { Write-Error "검증 리포트가 생성되지 않았습니다."; exit 4 }

# validator_report.json에서 pass 확인
try {
  $json = Get-Content $report -Raw -Encoding UTF8 | ConvertFrom-Json
  if ($json.pass -ne $true) {
    Write-Error "Validator PASS=false — 세부 체크를 확인하세요: $report"
    exit 5
  }
} catch {
  Write-Error "validator_report.json 파싱 실패: $report"
  exit 6
}

Write-Host "== HANDSHAKE PASS =="
Write-Host "ledger / report가 Gov audit_logs에 생성되었습니다."
exit 0
