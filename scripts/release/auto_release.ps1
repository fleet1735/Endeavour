# ==============================================
# auto_release.ps1 – Endeavour Release Automation
# Version: v1.0.1d
# ==============================================

param (
    [string]$Operator = "system"
)

$ErrorActionPreference = "Stop"

# --- Step 1: 환경 검증 ---
if (-not (Get-Command bash -ErrorAction SilentlyContinue)) {
    Write-Host "[ERROR] Bash executable not found in PATH. Please install Git Bash or WSL." -ForegroundColor Red
    exit 1
}

# --- Step 2: 버전 식별 ---
$NEW_VERSION = (bash -c "git describe --tags --abbrev=0 2>/dev/null || echo v1.0.0") + "-next"
Write-Host ("[INFO] Preparing release for version: {0}" -f $NEW_VERSION)

# --- Step 3: 릴리즈 실행 (구문 안정화 완료) ---
try {
    bash -c "./scripts/release/generate_release.sh"
    Write-Host "[SUCCESS] Release script executed successfully." -ForegroundColor Green
    $result_status     = "SUCCESS"
    $finding_severity  = "Low"
    $corrective_action = "NONE"
}
catch {
    Write-Host ("[ERROR] Release failed: {0}" -f $_.Exception.Message) -ForegroundColor Red
    $result_status     = "FAILURE"
    $finding_severity  = "Critical"
    $corrective_action = "ROLLBACK"

    # --- 안전 롤백 절차 ---
    $tagCheck = bash -c ("git tag | grep -q '^" + $NEW_VERSION + "$'")
    if ($LASTEXITCODE -eq 0) {
        bash -c ("git tag -d " + $NEW_VERSION)
        bash -c ("git push origin ':refs/tags/" + $NEW_VERSION + "'")
        Write-Host ("[INFO] Rolled back tag: {0}" -f $NEW_VERSION)
    }
}

# --- Step 4: ComplianceAudit 로그 작성 ---
$timestamp = (Get-Date).ToUniversalTime().ToString("yyyy-MM-ddTHH:mm:ssZ")
$audit_id  = [guid]::NewGuid().ToString()
$logRoot   = (git rev-parse --show-toplevel)
$logPath   = Join-Path $logRoot "logs/audit"
if (-not (Test-Path $logPath)) { New-Item -ItemType Directory -Force -Path $logPath | Out-Null }
$logFile   = Join-Path $logPath ("auto_release_{0}.json" -f (Get-Date).ToString("yyyyMMdd_HHmm"))

$auditEntry = [ordered]@{
    audit_id          = $audit_id
    timestamp         = $timestamp
    release_version   = $NEW_VERSION
    result_status     = $result_status
    finding_severity  = $finding_severity
    corrective_action = $corrective_action
    reviewer          = $Operator
    notes             = ("Auto release execution completed with status: {0}" -f $result_status)
    linked_entity     = "ComplianceAudit"
}

$auditEntry | ConvertTo-Json -Depth 5 | Out-File -FilePath $logFile -Encoding UTF8
Write-Host ("[INFO] ComplianceAudit log written to {0}" -f $logFile) -ForegroundColor Cyan

# --- Step 5: Git 등록 (commit/push 제외) ---
git add "scripts/release/auto_release.ps1"
Write-Host "[INFO] auto_release.ps1 registered in Git index. Manual commit required." -ForegroundColor Yellow

