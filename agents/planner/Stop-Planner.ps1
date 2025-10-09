# =========================
# Planner Safe Stop Trigger
# =========================
$StopFlag = "D:\Endeavour_Dev\agents\planner\planner.stop"
New-Item -ItemType File -Force -Path $StopFlag | Out-Null
Write-Host "⏹ Stop flag 생성됨 → Planner 루프가 안전 종료됩니다."