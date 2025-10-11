$StopFlag = "D:\Endeavour_Dev\agents\self_heal\runner.stop"
New-Item -ItemType File -Force -Path $StopFlag | Out-Null
Write-Host "⏹ Self-Heal Runner 종료 요청됨"

