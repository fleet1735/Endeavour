param([string]$Bus = 'D:\Endeavour_Dev\agents\reflex\bus\stream\bus_events.jsonl',[string]$Once = 'D:\Endeavour_Dev\agents\self_heal\self_heal_once.ps1')
$mtx = New-Object System.Threading.Mutex(False,'Global\EndeavourSelfHealKeepalive')
try{
  if(-not $mtx.WaitOne(0)){ return }
  if(-not (Test-Path $Once)){ throw 'missing once runner' }
  & 'C:\Program Files\PowerShell\7\pwsh.exe' -NoProfile -ExecutionPolicy Bypass -File "$Once" -Bus "$Bus" 2>&1 | Out-Null
} finally { if($mtx){ $mtx.ReleaseMutex() | Out-Null } }
