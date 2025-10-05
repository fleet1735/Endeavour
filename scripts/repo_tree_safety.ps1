# === auto-generated safety script ===
$ErrorActionPreference="Stop"
$DevRoot="D:\Endeavour_Dev"
$DriveDocs="D:\GoogleDrive\Endeavour\docs"
$TreeTarget=Join-Path $DriveDocs "repo_tree_latest.txt"
$LogDir=Join-Path $DevRoot "data\logs"
if (!(Test-Path $LogDir)){New-Item -ItemType Directory -Force -Path $LogDir|Out-Null}
$Now=(Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
$LogFile=Join-Path $LogDir "repo_tree_restore_$Now.log"
$files=Get-ChildItem -Path $DevRoot -Recurse -Force|Where-Object{ -not $_.PSIsContainer }|ForEach-Object{ $_.FullName.Substring($DevRoot.Length+1)}
Set-Content -Path $TreeTarget -Value $files -Encoding UTF8
Add-Content -Path $LogFile -Value "repo_tree regenerated at $Now"
Write-Host "✅ repo_tree_latest.txt updated at $TreeTarget"


# === Guard: forbid docs reparse points (symlinks) ===
$devDocs = "D:\Endeavour_Dev\docs"
try {
  $rp = fsutil reparsepoint query $devDocs 2>$null
  if ($LASTEXITCODE -eq 0) {
    Write-Host "❌ 안전차단: Dev/docs가 ReparsePoint(심볼릭 링크)입니다. 스크립트를 중단합니다."
    exit 2
  }
} catch { }
