# ============================================================
# log_rotation.ps1 — rotate reflex logs older than N days
# Usage: scheduled daily via Task Scheduler or cron equivalent
# ============================================================
param(
    [string]$EngineRoot = "D:\Endeavour_Dev\agents\reflex",
    [int]$KeepDays = 7
)

$LOG_DIR = Join-Path $EngineRoot "logs"
$ARCHIVE_DIR = Join-Path $LOG_DIR "archive"

if (-not (Test-Path $ARCHIVE_DIR)) { New-Item -Path $ARCHIVE_DIR -ItemType Directory -Force | Out-Null }

Get-ChildItem -Path $LOG_DIR -File -Exclude "archive" | ForEach-Object {
    if ($_.LastWriteTime -lt (Get-Date).AddDays(-$KeepDays)) {
        $zipName = Join-Path $ARCHIVE_DIR ($_.BaseName + "_" + ($_.LastWriteTime.ToString("yyyyMMdd")) + ".zip")
        # compress then remove original
        try {
            Add-Type -AssemblyName System.IO.Compression.FileSystem
            [System.IO.Compression.ZipFile]::CreateFromDirectory(($_.DirectoryName), $zipName)
            # remove the single file if zipped successfully (we zipped whole dir; safe fallback: move file)
            Remove-Item -Path $_.FullName -Force -ErrorAction SilentlyContinue
        } catch {
            # fallback: move to archive folder
            Move-Item -Path $_.FullName -Destination $ARCHIVE_DIR -Force
        }
    }
}
