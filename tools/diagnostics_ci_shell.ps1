param(
  [string]$BASE = "D:\Endeavour_Dev"
)

Write-Host "=== Diagnostics: Shell/Profiles/Env ==="

# 1) PowerShell 프로필 스캔 (여러 범위)
$profiles = @()
try { $profiles += $PROFILE } catch {}
try { $profiles += $PROFILE.CurrentUserAllHosts } catch {}
try { $profiles += $PROFILE.CurrentUserCurrentHost } catch {}
try { $profiles += $PROFILE.AllUsersAllHosts } catch {}
try { $profiles += $PROFILE.AllUsersCurrentHost } catch {}
$profiles = $profiles | Where-Object { $_ -and (Test-Path $_) } | Select-Object -Unique

if($profiles.Count -eq 0){
  Write-Host "[Profiles] 발견된 프로필 없음"
}else{
  Write-Host "[Profiles] 검색 경로:"
  $profiles | ForEach-Object { Write-Host " - $_" }
  Write-Host "[Profiles] 종료 문구 스캔:"
  $patterns = @('^\s*exit\s+\d*','Exit-PSHostProcess','Stop-Process\s+-Id\s+\$PID')
  foreach($p in $profiles){
    $hits = @()
    foreach($pat in $patterns){
      $m = Select-String -Path $p -Pattern $pat -SimpleMatch:$false -AllMatches -ErrorAction SilentlyContinue
      if($m){ $hits += $m }
    }
    if($hits.Count -gt 0){
      Write-Warning " - $p 에 종료 지시 의심 라인 발견:"
      $hits | ForEach-Object { Write-Host ("   line {0}: {1}" -f $_.LineNumber, $_.Line) }
    } else {
      Write-Host " - $p: 종료 지시 무(OK)"
    }
  }
}

# 2) 실행 정책
try{
  $ep = Get-ExecutionPolicy -List | Format-Table -AutoSize | Out-String
  Write-Host "`n[ExecutionPolicy]`n$ep"
}catch{ Write-Warning "ExecutionPolicy 조회 실패: $_" }

# 3) 환경 변수 요약
Write-Host "`n[Env] PYTHONPATH=$env:PYTHONPATH"
Write-Host "[Env] GITHUB_ACTIONS=$env:GITHUB_ACTIONS"
Write-Host "[Env] PWD=$(Get-Location)"

# 4) 핵심 파일 존재 점검
$req = @(
  (Join-Path $BASE 'tools\ci_local_runner.ps1'),
  (Join-Path $BASE 'tools\smoke_engine.ps1'),
  (Join-Path $BASE 'tools\gate_handshake.ps1')
)
Write-Host "`n[Files] Required:"
foreach($r in $req){ Write-Host (" - {0}: {1}" -f $r, (Test-Path $r ? 'OK' : 'MISSING')) }
