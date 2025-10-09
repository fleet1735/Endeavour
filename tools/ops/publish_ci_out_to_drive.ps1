param()
Set-StrictMode -Version Latest
$ErrorActionPreference = "Stop"
$RepoRoot  = "D:\Endeavour_Dev"
$DriveDocs = "D:\GoogleDrive\Endeavour\docs"
$Stage     = Join-Path $RepoRoot "ci_out"
$AuditS    = Join-Path $Stage "audit_logs"
$PromoS    = Join-Path $Stage "promotion_checklist.md"

if(-not (Test-Path $Stage)){ Write-Host "ci_out 스테이징이 없습니다." -ForegroundColor Yellow; exit 0 }
if(-not (Test-Path $DriveDocs)){ throw "Drive docs 경로 없음: $DriveDocs" }
$AuditD = Join-Path $DriveDocs "audit_logs"; if(-not(Test-Path $AuditD)){ New-Item -ItemType Directory -Path $AuditD | Out-Null }

# 1) audit_logs 병합
if(Test-Path $AuditS){
  Get-ChildItem -LiteralPath $AuditS -File -Filter "*.md" | ForEach-Object {
    $src = $_.FullName
    $dst = Join-Path $AuditD $_.Name
    $chunk = Get-Content -LiteralPath $src -Raw
    if(Test-Path $dst){
      $old = Get-Content -LiteralPath $dst -Raw
      [System.IO.File]::WriteAllText($dst, ($chunk + "`r`n" + $old), (New-Object System.Text.UTF8Encoding $false))
    } else {
      [System.IO.File]::WriteAllText($dst, $chunk, (New-Object System.Text.UTF8Encoding $false))
    }
  }
}

# 2) promotion_checklist 병합
if(Test-Path $PromoS){
  $dstPromo = Join-Path $DriveDocs "promotion_checklist.md"
  $add = Get-Content -LiteralPath $PromoS -Raw
  if(Test-Path $dstPromo){
    $old = Get-Content -LiteralPath $dstPromo -Raw
    [System.IO.File]::WriteAllText($dstPromo, ($old + "`r`n" + $add), (New-Object System.Text.UTF8Encoding $false))
  } else {
    [System.IO.File]::WriteAllText($dstPromo, $add, (New-Object System.Text.UTF8Encoding $false))
  }
}

Write-Host "✅ 퍼블리시 완료: ci_out → Drive\\docs 반영" -ForegroundColor Green
