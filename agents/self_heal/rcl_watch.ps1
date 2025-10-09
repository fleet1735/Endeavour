$ErrorActionPreference="SilentlyContinue"
$Rcl = "D:\Endeavour_Dev\data\rcl_fallback.json"
$Bus = "D:\Endeavour_Dev\agents\reflex\bus\stream\bus_events.jsonl"
if(-not (Test-Path $Rcl)){ New-Item -ItemType File -Path $Rcl | Out-Null }
$fsw = New-Object IO.FileSystemWatcher (Split-Path $Rcl), (Split-Path $Rcl -Leaf)
$fsw.IncludeSubdirectories=$false; $fsw.EnableRaisingEvents=$true
$action = {
  param($source,$eventArgs)
  try{
    $evt = @{ ts=(Get-Date).ToString("s"); source="planner"; topic="Planner/Action";
              payload=@{ action="ACTION: run self_heal.ps1"; reason="rcl_changed" } }
    $evt | ConvertTo-Json -Compress -Depth 6 | Add-Content -Path $using:Bus
  }catch{}
}
# Changed / Created 둘 다 훅
Register-ObjectEvent -InputObject $fsw -EventName Changed -Action $action | Out-Null
Register-ObjectEvent -InputObject $fsw -EventName Created -Action $action | Out-Null
# 포그라운드 생존 루프
while($true){ Start-Sleep 2 }