param(
  [string]$Root = "D:\Endeavour_Dev",
  [string]$Log  = "D:\Endeavour_Dev\agents\self_heal\self_heal.log"
)
$ErrorActionPreference = "Continue"

function Write-Log($msg){ $ts=Get-Date -Format "yyyy-MM-dd HH:mm:ss"; Add-Content -Path $Log -Value "$ts [CHECK] $msg" }

$results = [ordered]@{
  json_rcl_fallback_ok = $false
  paths_ok             = $false
}

# ① rcl_fallback.json JSON 유효성 검사
$rclPath = Join-Path $Root "data\rcl_fallback.json"
if (Test-Path $rclPath) {
  try { Get-Content $rclPath -Raw | ConvertFrom-Json | Out-Null; $results.json_rcl_fallback_ok = $true }
  catch { Write-Log "rcl_fallback.json JSON 파싱 실패: $($_.Exception.Message)"; $results.json_rcl_fallback_ok = $false }
} else {
  Write-Log "rcl_fallback.json 미존재"
}

# ② 필수 경로 존재 검사
$must = @(
  (Join-Path $Root "agents\reflex"),
  (Join-Path $Root "agents\reflex\logs"),
  (Join-Path $Root "agents\reflex\bus\stream")
)
$missing = $must | Where-Object { -not (Test-Path $_) }
if ($missing.Count -eq 0) { $results.paths_ok = $true }
else { Write-Log ("필수 경로 미존재: " + ($missing -join ", ")) }

# 결과 출력(JSON)
$results | ConvertTo-Json -Compress

