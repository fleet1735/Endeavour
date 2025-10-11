param(
  [string]$Script = "D:\Endeavour_Dev\agents\self_heal\self_heal.ps1",
  [int]$WindowSec = 10
)

# 1) 전역 Mutex로 동시실행 차단
$mtxName = "Global\Endeavour_SelfHeal_Gate"
$mtx = New-Object System.Threading.Mutex($false, $mtxName)
$hasLock = $false
try {
  $hasLock = $mtx.WaitOne(0)
  if(-not $hasLock){
    Write-Host "[SKIP] another run in progress (mutex)"
    exit 259
  }

  # 2) 최근 실행 스탬프로 짧은 중복 억제
  $stamp = "D:\Endeavour_Dev\agents\self_heal\.last_run"
  $now = Get-Date
  if(Test-Path $stamp){
    try {
      $last = [datetime](Get-Content $stamp -Raw)
      if( ($now - $last).TotalSeconds -lt $WindowSec ){
        Write-Host "[SKIP] dedup window ($([int]($now-$last).TotalSeconds)s < $WindowSec s)"
        exit 259
      }
    } catch { }
  }
  $now.ToString("o") | Set-Content -Path $stamp -Encoding UTF8

  # 3) 본 실행
  & $Script
}
finally{
  if($hasLock){ $mtx.ReleaseMutex() }
  $mtx.Dispose()
}

