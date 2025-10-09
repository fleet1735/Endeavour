param(
  [string]$Root = "D:\Endeavour_Dev",
  [string]$Log  = "D:\Endeavour_Dev\agents\self_heal\self_heal.log"
)
function W($m){ $ts=Get-Date -Format "yyyy-MM-dd HH:mm:ss"; Add-Content -Path $Log -Value "$ts [FIX] $m" }
$need = @(
  (Join-Path $Root "agents\reflex\logs"),
  (Join-Path $Root "agents\reflex\bus\stream")
)
$need | ForEach-Object {
  if (-not (Test-Path $_)) { New-Item -ItemType Directory -Force -Path $_ | Out-Null; W "경로 복구: $_" }
}
exit 0
