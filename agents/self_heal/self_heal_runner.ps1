function HashLine {
  param([Parameter(Mandatory=$true)][string]$s)
  $sha1 = [System.Security.Cryptography.SHA1]::Create()
  try {
    $bytes = [Text.Encoding]::UTF8.GetBytes($s)
    $hash  = $sha1.ComputeHash($bytes)
    -join ($hash | ForEach-Object { $_.ToString("x2") })
  } finally { $sha1.Dispose() }
}
$ErrorActionPreference="Continue"
$mtx=New-Object Threading.Mutex($false,"Global\EndeavourSelfHealRunner")
if(-not $mtx.WaitOne(0,$false)){Write-Host "[RUNNER] Another instance is running. Exit."; exit 0}
$Bus="D:\Endeavour_Dev\agents\reflex\bus\stream\bus_events.jsonl"
$Heal="D:\Endeavour_Dev\agents\self_heal\self_heal.ps1"
$Log="D:\Endeavour_Dev\agents\self_heal\self_heal.log"
$Stop="D:\Endeavour_Dev\agents\self_heal\runner.stop"
$State="D:\Endeavour_Dev\agents\self_heal\runner.state"
$Seen="D:\Endeavour_Dev\agents\self_heal\runner.seen"
$Rate="D:\Endeavour_Dev\agents\self_heal\runner.rate"
function W($m){$ts=Get-Date -Format "yyyy-MM-dd HH:mm:ss"; Add-Content -Path $Log -Value "$ts [RUNNER] $m"}
function HashLine($s){$sha1=[Security.Cryptography.SHA1]::Create();($sha1.ComputeHash([Text.Encoding]::UTF8.GetBytes($s))|% ToString x2) -join ''}
W "Runner start (mutex+ff+dedup+ratelimit)"
$seen=@{}; if(Test-Path $Seen){foreach($h in (Get-Content $Seen -EA SilentlyContinue)){if($h){$seen[$h]=$true}}}
$last=0; if(Test-Path $Bus){$t=(Get-Content $Bus|measure -l).Lines; $last=$t; Set-Content $State $last; W "FF → $last"}
$rate=5
while($true){
  if(Test-Path $Stop){Remove-Item $Stop -EA SilentlyContinue -Force; W "Runner exit"; break}
  if(Test-Path $Bus){
    $t=(Get-Content $Bus|measure -l).Lines
    if($t -gt $last){
      $new=Get-Content $Bus | Select-Object -Skip $last
      foreach($line in $new){
        $evt=$null; try{$evt=$line|ConvertFrom-Json}catch{$evt=$null}; if(-not $evt){continue}
        if($evt.topic -eq "Planner/Action" -and $evt.payload.action -match "self_heal\.ps1"){
          $h=HashLine($line); if($seen.ContainsKey($h)){continue}; $seen[$h]=$true; Add-Content -Path $Seen -Value $h
          $now=[DateTime]::UtcNow
          $lastRun=if(Test-Path $Rate){try{[DateTime]::ParseExact((Get-Content $Rate -Raw).Trim(),"o",$null)}catch{[DateTime]::MinValue}}else{[DateTime]::MinValue}
          if(($now-$lastRun).TotalSeconds -lt $rate){continue}; $now.ToString("o")|Set-Content -Path $Rate
          W "Planner/Action → self_heal.ps1"; & $Heal
        }
      }
      $last=$t; Set-Content $State $last
    }
  }
  Start-Sleep 2
}
