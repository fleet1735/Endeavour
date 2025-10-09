# ============================================================
# context_analyzer.ps1 — Reflex Context Insight & Report (v1.3.1)
# ============================================================

param([string]$EngineRoot = "D:\Endeavour_Dev\agents\reflex")

# --- ① 경로 자동 보정
if (-not (Test-Path $EngineRoot)) { 
    $EngineRoot = Split-Path -Parent $MyInvocation.MyCommand.Path 
}
Set-Location $EngineRoot

# --- ② 경로 정의
$CONTEXT_CACHE = Join-Path $EngineRoot "config\context_cache.json"
$LOG_DIR       = Join-Path $EngineRoot "logs"
$INSIGHT_FILE  = Join-Path $LOG_DIR ("daily_insight_{0}.log" -f (Get-Date -Format "yyyyMMdd"))

# --- ③ 디렉토리 확인
if (-not (Test-Path $LOG_DIR)) { 
    New-Item -Path $LOG_DIR -ItemType Directory -Force | Out-Null 
}

# --- ④ context_cache 자동 감지·복원
if (-not (Test-Path $CONTEXT_CACHE)) {
    Write-Host "⚠️ context_cache.json이 존재하지 않아 새로 생성합니다."
    $ctx = @{ events = @() }
    ($ctx | ConvertTo-Json -Depth 4) | Out-File -FilePath $CONTEXT_CACHE -Encoding UTF8 -Force
    Start-Sleep -Seconds 1
}

# --- ⑤ 메인 로직
try {
    $ctx = Get-Content $CONTEXT_CACHE -Raw | ConvertFrom-Json
    $events = $ctx.events | Sort-Object -Property timestamp -Descending | Select-Object -First 50
    $out = @()
    $out += "=== Reflex Daily Insight Report (v1.3.1) ==="
    $out += "📅 Generated: $(Get-Date -Format 'yyyy-MM-dd HH:mm:ss')"
    $out += ""
    $out += "📊 최근 이벤트 Top 50"
    $out += ""
    foreach ($e in $events) {
        $out += ("[{0}] {1} → {2}" -f $e.timestamp, $e.event, $e.detail)
    }
    $out += ""
    $out += "📈 이벤트 요약:"
    $counts = @{}
    foreach ($e in $ctx.events) {
        if (-not $counts.ContainsKey($e.event)) { $counts[$e.event] = 0 }
        $counts[$e.event]++
    }
    foreach ($k in $counts.Keys) { $out += (" - {0}: {1}" -f $k, $counts[$k]) }

    $out | Out-File -FilePath $INSIGHT_FILE -Encoding UTF8 -Force
    Write-Host "✅ Daily Insight 생성 완료: $INSIGHT_FILE"
}
catch {
    Write-Host "❌ 오류 발생: $($_.Exception.Message)"
    $errLog = Join-Path $LOG_DIR ("context_error_{0}.log" -f (Get-Date -Format 'yyyyMMdd_HHmmss'))
    "[$(Get-Date)] ERROR: $($_.Exception.Message)" | Out-File -FilePath $errLog -Encoding UTF8 -Force
}
