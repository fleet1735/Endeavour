# pre-commit: enforce UTF-8 no BOM & LF for core docs; auto-stage fixes; block large staged files
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"

$docCandidates = @(
  "docs/IPD.md",
  "docs/CHANGE_LOG.md",
  "docs/프로젝트청사진.md",
  "Migration_pack.md",
  "docs/Migration_pack.md"
) | Where-Object { Test-Path $_ }

$logDir = "data/logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = Join-Path $logDir "hooks.log"

function Convert-ToUtf8NoBom {
  param([string]$Path)
  $bytes  = [System.IO.File]::ReadAllBytes($Path)
  $hasBOM = ($bytes.Length -ge 3 -and $bytes[0] -eq 0xEF -and $bytes[1] -eq 0xBB -and $bytes[2] -eq 0xBF)
  $text   = [System.Text.Encoding]::UTF8.GetString($bytes)
  $text   = $text -replace "`r`n","`n"  # normalize to LF
  $utf8   = New-Object System.Text.UTF8Encoding($false) # no BOM
  [System.IO.File]::WriteAllBytes($Path, $utf8.GetBytes($text))
  return $hasBOM
}

$fixed = @()
foreach ($p in $docCandidates) {
  try {
    $before = Get-Content -Raw -LiteralPath $p
    $hadBom = Convert-ToUtf8NoBom -Path $p
    $after  = Get-Content -Raw -LiteralPath $p
    if ($before -ne $after) {
      git add -- "$p" | Out-Null
      $fixed += [pscustomobject]@{ path = $p; bomFixed = $hadBom }
    }
  } catch {
    "$([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')) [pre-commit][ERROR] $p : $($_.Exception.Message)" | Add-Content -LiteralPath $logFile
    Write-Error "pre-commit 실패: '$p' 처리 중 오류 → 커밋 중단"
    exit 1
  }
}

# Large-file block on STAGED entries only
$staged = (git diff --cached --name-only) -split "`r?`n" | Where-Object { $_ }
$tooLarge = @()
foreach ($f in $staged) {
  if (Test-Path $f) {
    if ((Get-Item $f).Length -gt 25MB) { $tooLarge += $f }
  }
}
if ($tooLarge.Count -gt 0) {
  Write-Host "다음 파일이 25MB를 초과합니다 (커밋 차단):"
  $tooLarge | ForEach-Object { Write-Host " - $_" }
  exit 1
}

# Summary formatting (build array THEN -join)
if ($fixed.Count -gt 0) {
  $entries = $fixed | ForEach-Object { "[{0}] (BOM fixed: {1})" -f $_.path, $_.bomFixed }
  $summary = "$([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')) [pre-commit][OK] fixed: " + ($entries -join "; ")
} else {
  $summary = "$([DateTime]::Now.ToString('yyyy-MM-dd HH:mm:ss')) [pre-commit][OK] no changes"
}
$summary | Add-Content -LiteralPath $logFile

exit 0
