# ==== 리포지토리 상태 확인 스크립트 (최종판) ====

Write-Output "=== Endeavour Repo 상태 ==="

Write-Output ("브랜치: " + (git rev-parse --abbrev-ref HEAD))
Write-Output ("마지막 커밋: " + (git log -1 --oneline))
Write-Output "원격:"
git remote -v
Write-Output "상태:"
git status -s
