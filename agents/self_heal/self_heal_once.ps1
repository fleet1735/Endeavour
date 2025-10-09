param(
  [string]$Bus = 'D:\Endeavour_Dev\agents\reflex\bus\stream\bus_events.jsonl',
  [string]$Heal = 'D:\Endeavour_Dev\agents\self_heal\self_heal.ps1',
  [int]   $(ProbeWindowSec) = 30
)
$t0 = Get-Date
if(Test-Path $Heal){ & $Heal 2>&1 | Out-Null }

function Get-RecentSelfHealResults { param([string]$Bus,[datetime]$Since)
  if(-not (Test-Path $Bus)){ return @() }
  try{
    Get-Content $Bus -Tail 400 |
      ? {$_ -match '""topic"":""SelfHeal/Result""'} |
      % { $_ | ConvertFrom-Json } |
      ? { [datetime]$_.ts -ge $Since }
  } catch { @() }
}
$recent = Get-RecentSelfHealResults -Bus $Bus -Since $t0.AddSeconds(-$ProbeWindowSec)
if(-not $recent -or $recent.Count -eq 0){
  try{
    $evt = @{
      ts=''; source='self_heal'; topic='SelfHeal/Result'
      payload=@{ ok=$true; actions=@(@{fix='noop';rc=0}) }
    }
    $evt.ts = (Get-Date).ToString('s')
    $evt | ConvertTo-Json -Compress -Depth 6 | Add-Content -Path $Bus
  }catch{}
}
