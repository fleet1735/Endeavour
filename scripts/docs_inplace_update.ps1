param([string]$DocsRoot = 'D:\GoogleDrive\Endeavour\docs')
$ErrorActionPreference = 'Stop'

function FindDoc([string]$name) {
  $hit = Get-ChildItem -Path $DocsRoot -Recurse -File -Filter $name -ErrorAction SilentlyContinue | Select-Object -First 1
  if ($hit) { return $hit.FullName } else { return (Join-Path $DocsRoot $name) }
}
function EditDoc([string]$Path) {
  if (!(Test-Path $Path)) { Set-Content -Path $Path -Value "# $Path
" -Encoding UTF8 }
  $before = Get-Content -Raw -Path $Path -Encoding UTF8

  $t = $before
  $t = $t -replace 'stragegies','strategies'
  $t = $t -replace 'JSON\s*전략\s*스키마','셋업(JSON) 스키마'
  $t = $t -replace '(?m)^(#{1,6}\s*)(전략 정의|전략 정의 계층)','$1셋업 정의'
  $t = $t -replace '전략\s*스키마','셋업 스키마'
  $t = $t -replace '전략 예제','셋업 예제'
  $t = $t -replace 'python\s+-m\s+src\.utils\.data_handler','python -m endeavour.cli ingest'
  $t = $t -replace 'python\s+-m\s+src\.endeavour\.utils\.data_handler','python -m endeavour.cli ingest'
  $t = $t -replace '(?i)\b--strategy\b','--setup'
  $t = $t -replace 'docs/strategy_examples','docs/setup_examples'
  if ($t -notmatch 'Dev↔Drive 분리 원칙') {
    $t += "
> **Dev↔Drive 분리 원칙**
> - Dev: D:\Endeavour_Dev / Drive: D:\GoogleDrive\Endeavour(단방향 복제)
> - 코드와 문서는 물리적으로 분리합니다."
  }

  # 내용이 바뀐 경우에만 저장 (백업 없음)
  if ($t -ne $before) {
    Set-Content -Path $Path -Value $t -Encoding UTF8
    return True
  }
  return False
}

$IPD = FindDoc 'IPD.md'
$BP  = FindDoc '프로젝트청사진.md'
$MIG = FindDoc 'Migration_pack.md'
$CHG = FindDoc 'CHANGE_LOG.md'
$IDX = Join-Path $DocsRoot 'README_index.md'

$changed = False
$changed = (EditDoc $IPD) -or $changed
$changed = (EditDoc $BP)  -or $changed
$changed = (EditDoc $MIG) -or $changed

# CHANGE_LOG: 실제 변경이 있었을 때만 prepend
if ($changed) {
  if (!(Test-Path $CHG)) { Set-Content -Path $CHG -Value '' -Encoding UTF8 }
  $now = Get-Date -Format 'yyyy-MM-dd HH:mm:ss'
  $entry = "## [$now] docs refresh (Drive in-place)
- 용어/실행 예시 보정 및 안내 갱신
"
  $cur = Get-Content -Raw -Path $CHG -Encoding UTF8
  if (-not $cur.StartsWith($entry)) {
    Set-Content -Path $CHG -Value ($entry + "
" + $cur) -Encoding UTF8
  }
}

# 인덱스 보강 (항상 최신화)
$idx = @"
# 📚 Endeavour 문서 인덱스 (Drive)
- **IPD** / **프로젝트청사진** / **Migration Pack** / **CHANGE_LOG**
- **setup_examples/**: 셋업(JSON) 예제 모음
실행 표준:
- ingest:  python -m endeavour.cli ingest --universe docs/universe/target_tickers.csv
- backtest:python -m endeavour.cli backtest --setup docs/setup_examples/sma_cross.json
"@
Set-Content -Path $IDX -Value $idx -Encoding UTF8
Write-Host "[OK] Docs updated (no backups): $DocsRoot"

