# ==== repo_tree.ps1 (repo_trees 전용) ====
$timestamp = Get-Date -Format "yyyyMMdd_HHmm"
$targetDir = "repo_trees"

if (-not (Test-Path $targetDir)) { New-Item -ItemType Directory -Path $targetDir | Out-Null }

tree /F > "$targetDir\repo_tree_$timestamp.txt"
Write-Output "📄 트리 파일 생성됨: $targetDir\repo_tree_$timestamp.txt"
