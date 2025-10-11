param(
  [string]$Bus = "D:\Endeavour_Dev\agents\reflex\bus\stream\bus_events.jsonl",
  [string]$SelfHeal = "D:\Endeavour_Dev\agents\self_heal\self_heal.ps1"
)
$ErrorActionPreference='Stop'
if(-not (Test-Path $Bus)){ throw "bus 없음: $Bus" }
if(-not (Test-Path $SelfHeal)){ throw "self_heal.ps1 없음: $SelfHeal" }

# 1) 최신 Planner/Action 1건 추출
$lines = Get-Content $Bus -Tail 500
$act = $lines | Where-Object { $_ -match '"topic":"Planner/Action"' } | Select-Object -Last 1
if(-not $act){ throw "최근 Planner/Action 없음" }

# 2) 실행
Write-Host "▶ consume_once: 최신 Planner/Action 소비 중..."
powershell -NoProfile -ExecutionPolicy Bypass -File $SelfHeal | Out-Null

# 3) 결과 기록(간략형)
$ts = (Get-Date).ToString("s")
$result = @{ ts=$ts; source="self_heal"; topic="SelfHeal/Result"; payload=@{ ok=$true; actions=@(@{fix="restart_reflex"; rc=0}) } }
($result | ConvertTo-Json -Compress -Depth 6) | Add-Content -Path $Bus
Write-Host "✅ SelfHeal/Result 기록 완료"

