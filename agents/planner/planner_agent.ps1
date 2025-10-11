# ============================
# Planner Agent v1.5.2 (Stable)
# - DEGRADED 감지 시 Self-Heal 기록
# - NORMAL 스팸 무시 및 쿨다운 적용
# - 자동 복귀 NORMAL 이벤트 삽입
# - Stop-Flag 기반 안전 종료 지원
# ============================
$ErrorActionPreference = "SilentlyContinue"
$BusPath   = "D:\Endeavour_Dev\agents\reflex\bus\stream\bus_events.jsonl"
$TraceLog  = "D:\Endeavour_Dev\agents\planner\planner_trace.log"
$StopFlag  = "D:\Endeavour_Dev\agents\planner\planner.stop"

$cooldownSeconds = 5
$lastHealAt = [datetime]::MinValue
Write-Host "[Planner Agent v1.5.2] 루프 시작..."

while ($true) {
    if (Test-Path $StopFlag) {
        Remove-Item $StopFlag -Force -ErrorAction SilentlyContinue
        Write-Host "⏹ Planner 정상 종료"
        break
    }

    if (Test-Path $BusPath) {
        $recent = Get-Content $BusPath -Tail 40
        foreach ($line in $recent) {
            $evt = $null
            try { $evt = $line | ConvertFrom-Json } catch { $evt = $null }
            if ($null -eq $evt) { continue }

            # DEGRADED 감지 및 쿨다운
            if ($evt.topic -eq "Ontology/State" -and $evt.payload.tag -eq "STATE:DEGRADED") {
                if ((Get-Date) - $lastHealAt -lt (New-TimeSpan -Seconds $cooldownSeconds)) { continue }

                # 1️⃣ Self-Heal 액션 기록
                $action = @{
                    ts      = (Get-Date).ToString("s")
                    source  = "planner"
                    topic   = "Planner/Action"
                    payload = @{ action = "ACTION: run self_heal.ps1"; reason = "STATE:DEGRADED" }
                }
                $action | ConvertTo-Json -Compress | Add-Content -Path $BusPath
                Add-Content -Path $TraceLog -Value ("{0} - Planner reacted to DEGRADED → self_heal" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"))
                Write-Host "✅ Self-heal action 기록됨"

                # 2️⃣ 자동 NORMAL 복귀 이벤트 삽입
                Start-Sleep -Seconds 2
                $norm = @{
                    ts      = (Get-Date).ToString("s")
                    source  = "planner"
                    topic   = "Planner/State"
                    payload = @{ tag = "STATE:NORMAL"; from = "Planner/AutoRecover" }
                }
                $norm | ConvertTo-Json -Compress | Add-Content -Path $BusPath

                $lastHealAt = Get-Date
            }
        }
    }
    Start-Sleep -Seconds 2
}
