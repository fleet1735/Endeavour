# === auto-generated safety script ===
$ErrorActionPreference="Stop"
$DevRoot="D:\Endeavour_Dev"
$DriveDocs="D:\GoogleDrive\Endeavour\docs"
$TreeTarget=Join-Path $DriveDocs "repo_tree_latest.txt"
$LogDir=Join-Path $DevRoot "data\logs"
if (!(Test-Path $LogDir)){New-Item -ItemType Directory -Force -Path $LogDir|Out-Null}
$Now=(Get-Date).ToString("yyyy-MM-dd_HH-mm-ss")
$LogFile=Join-Path $LogDir "repo_tree_restore_$Now.log"
if (Test-Path $TreeTarget){Copy-Item -Force $TreeTarget "$TreeTarget.bak_$Now"}
$files=Get-ChildItem -Path $DevRoot -Recurse -Force|Where-Object{ -not $_.PSIsContainer }|ForEach-Object{ $_.FullName.Substring($DevRoot.Length+1)}
Set-Content -Path $TreeTarget -Value $files -Encoding utf8NoBOM
Add-Content -Path $LogFile -Value "repo_tree regenerated at $Now"
Write-Host "✅ repo_tree_latest.txt updated at $TreeTarget"
