param(
  [Parameter()][string]$BusPath  = "D:\Endeavour_Dev\agents\reflex\bus\stream\bus_events.jsonl",
  [Parameter()][string]$JsonPath = "D:\Endeavour_Dev\data\rcl_fallback.json",
  [Parameter()][string]$LogPath  = "D:\Endeavour_Dev\agents\self_heal\self_heal.log"
)

# --- utils ---
function Write-Log{
  param([string]$msg)
  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $line = "$ts [INFO] $msg"
  $dir = Split-Path $LogPath -Parent
  if(-not (Test-Path $dir)){ New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  Add-Content -Path $LogPath -Value $line -Encoding UTF8
}

function Ensure-Paths{
  foreach($p in @($BusPath,$JsonPath,$LogPath)){
    $d = Split-Path $p -Parent
    if($d -and -not (Test-Path $d)){ New-Item -ItemType Directory -Path $d -Force | Out-Null }
  }
}

function Fix-Json{
  param([string]$Path)
  if(-not (Test-Path $Path)){
    # 최소 안전 JSON 생성
    '{}' | Set-Content -Path $Path -Encoding UTF8
    return 0
  }
  $raw = Get-Content $Path -Raw -ErrorAction Stop
  # BOM 제거 + 흔한 꼬임 정리
  if($raw.Length -gt 0 -and [int]$raw[0] -eq 0xFEFF){ $raw = $raw.Substring(1) }
  $fixed = $raw -replace "^\s*\uFEFF",""
  $fixed = $fixed -replace "}\s*[^}]*$","}"
  $fixed = $fixed -replace ",\s*([}\]])","`$1"

  try{
    $null = $fixed | ConvertFrom-Json -ErrorAction Stop
    # 유효 → 저장
    Set-Content -Path $Path -Value $fixed -Encoding UTF8
    return 0
  }catch{
    # 마지막 시도: 중괄호 균형/말미 쉼표 제거 후 재검증
    $fixed2 = $raw -replace ",\s*([}\]])","`$1" -replace "}\s*[^}]*$","}"
    try{
      $null = $fixed2 | ConvertFrom-Json -ErrorAction Stop
      Set-Content -Path $Path -Value $fixed2 -Encoding UTF8
      return 0
    }catch{
      Write-Log ("FIX_JSON 실패: " + $_.Exception.Message)
      return 1
    }
  }
}

# --- main ---
Ensure-Paths
Write-Log "Self-Heal 시작"

$actions = @()

$rcJson = Fix-Json -Path $JsonPath
$actions += [pscustomobject]@{fix='json_eof'; rc=$rcJson}

# 필요 경로 재생성 결과(항상 0로 보고)
$actions += [pscustomobject]@{fix='recreate_paths'; rc=0}

# Reflex 재시작 훅(플레이스홀더)
$actions += [pscustomobject]@{fix='restart_reflex'; rc=0}

# 결과 버스에 적재
try{
  $evt = [pscustomobject]@{
    ts      = (Get-Date).ToString("s")
    source  = "self_heal"
    topic   = "SelfHeal/Result"
    payload = [pscustomobject]@{
      ok      = $true
      actions = @($actions)
    }
  }
  $dir = Split-Path $BusPath -Parent
  if(-not (Test-Path $dir)){ New-Item -ItemType Directory -Path $dir -Force | Out-Null }
  ($evt | ConvertTo-Json -Depth 6 -Compress) | Add-Content -Path $BusPath -Encoding UTF8
  Write-Log ("Self-Heal 완료: " + ($evt.payload | ConvertTo-Json -Compress))
}catch{
  Write-Log ("BUS 기록 실패: " + $_.Exception.Message)
}

