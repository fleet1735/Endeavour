# ============================================================
# test_auto_recovery.ps1 (v1.2)
# - backup RCL (if exists), delete it, run engine, check integrated logs and recommendations
# ============================================================
$EngineRoot = "D:\Endeavour_Dev\agents\reflex"
$RCL_BACKUP = "D:\Endeavour_Dev\data\rcl_backup_test.json"
$RECOVERY_LOG = "D:\Endeavour_Dev\agents\reflex\logs\recovery_history.log"
$RECOMMEND = "D:\Endeavour_Dev\agents\reflex\config\recommendations.txt"

Write-Host "STEP 1: Preparing test environment..."
if ($env:RCL_PATH -and (Test-Path $env:RCL_PATH)) {
    Copy-Item -Path $env:RCL_PATH -Destination $RCL_BACKUP -Force
    Remove-Item -Path $env:RCL_PATH -Force
    Write-Host " - RCL backed up and removed."
} else {
    Write-Host " - No RCL present; continuing."
}

Write-Host "STEP 2: Run engine..."
& "D:\Endeavour_Dev\agents\reflex\auto_reflex_engine.ps1"

Start-Sleep -Seconds 2

Write-Host "STEP 3: Check logs..."
if (Test-Path $RECOVERY_LOG) {
    Get-Content $RECOVERY_LOG -Tail 10
} else {
    Write-Warning "Recovery log not found."
}

Write-Host "STEP 4: Check recommendations..."
if (Test-Path $RECOMMEND) {
    Get-Content $RECOMMEND -Tail 10
} else {
    Write-Warning "Recommendations file not found."
}

Write-Host "STEP 5: Restore backup RCL if existed..."
if (Test-Path $RCL_BACKUP) {
    Copy-Item -Path $RCL_BACKUP -Destination $env:RCL_PATH -Force
    Write-Host " - RCL restored from backup."
}

Write-Host "TEST COMPLETE."
