# ============================================================
# Reflex v1.5.1 — Ontology/Planner Stub (Scoped Safe)
# ============================================================

$ROOT = "D:\Endeavour_Dev\agents"
$Reflex = Join-Path $ROOT "reflex"
$BusDir = Join-Path $Reflex "bus"
$Stream = Join-Path $BusDir "stream"
$Ont = Join-Path $ROOT "ontology"
$Plan = Join-Path $ROOT "planner"
$Logs = Join-Path $Reflex "logs"

# 글로벌 스코프 보장
Set-Variable -Name ROOT -Value $ROOT -Scope Global
Set-Variable -Name Reflex -Value $Reflex -Scope Global
Set-Variable -Name BusDir -Value $BusDir -Scope Global
Set-Variable -Name Stream -Value $Stream -Scope Global
Set-Variable -Name Ont -Value $Ont -Scope Global
Set-Variable -Name Plan -Value $Plan -Scope Global
Set-Variable -Name Logs -Value $Logs -Scope Global

# 모든 폴더 강제 생성
$dirs = @($Reflex, $BusDir, $Stream, $Ont, $Plan, $Logs)
foreach ($d in $dirs) {
    if (-not (Test-Path $d)) {
        New-Item -ItemType Directory -Force -Path $d | Out-Null
    }
}

Write-Host "✅ 폴더 생성 완료:"
$dirs | ForEach-Object { Write-Host " - $_" }

