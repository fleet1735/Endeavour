param(
  [int]$WindowSec = 60
)
$ErrorActionPreference='Stop'
$bus = 'D:\Endeavour_Dev\agents\reflex\bus\stream\bus_events.jsonl'
if(-not (Test-Path $bus)){ Write-Host 'FAIL  (BUS 없음)'; exit 1 }

$cnt = (Get-Content $bus -Tail 500 | ?{$_ -match '""topic"":""SelfHeal/Result""'} | ConvertFrom-Json |
  ?{ [datetime]$_.ts -gt (Get-Date).AddSeconds(-$WindowSec) } |
  %{
     $_.payload.actions = @($_.payload.actions | Sort-Object fix)
     ($_.payload.actions | ConvertTo-Json -Compress)
   } | Sort-Object -Unique).Count

if($cnt -ge 1){
  Write-Host ("PASS  (최근 {0}s 내 SelfHeal/Result {1}건)" -f $WindowSec, $cnt)
  exit 0
}else{
  Write-Host ("FAIL  (최근 {0}s 내 SelfHeal/Result 미발견)" -f $WindowSec)
  exit 1
}

