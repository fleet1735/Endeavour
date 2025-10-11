# ============================================================
# auto_reflex_engine.ps1 (v1.2) — Reflex Engine (Context-Ready)
# ============================================================
param(
    [string]$EngineRoot = "D:\Endeavour_Dev\agents\reflex"
)

# --- Configurable paths
$LOG_DIR        = Join-Path $EngineRoot "logs"
$RECOVERY_LOG   = Join-Path $LOG_DIR "recovery_history.log"
$ENGINE_OPS_LOG = Join-Path $LOG_DIR ("engine_ops_{0}.log" -f (Get-Date -Format "yyyyMMdd"))
$CONTEXT_CACHE  = Join-Path $EngineRoot "config\context_cache.json"
$RECOMMEND_FILE = Join-Path $EngineRoot "config\recommendations.txt"
$RCL_FALLBACK   = "D:\Endeavour_Dev\data\rcl_fallback.json"

# --- Ensure directories
if (-not (Test-Path $LOG_DIR)) { New-Item -Path $LOG_DIR -ItemType Directory -Force | Out-Null }
if (-not (Test-Path (Split-Path $CONTEXT_CACHE))) { New-Item -Path (Split-Path $CONTEXT_CACHE) -ItemType Directory -Force | Out-Null }

# --- Utility: Log writer
function Write-Log {
    param([string]$Level, [string]$Message)
    $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $line = "[$ts] [$Level] $Message"
    Add-Content -Path $ENGINE_OPS_LOG -Value $line -Encoding UTF8
    if ($Level -eq "ERROR") { Add-Content -Path $RECOVERY_LOG -Value $line -Encoding UTF8 }
}

# --- Context extraction
function Update-Context {
    param([string]$EventType, [string]$Detail)
    $ctx = @{}
    if (Test-Path $CONTEXT_CACHE) {
        try { $ctx = Get-Content $CONTEXT_CACHE -Raw | ConvertFrom-Json -ErrorAction Stop } catch { $ctx = @{} }
    }
    if (-not $ctx.events) { $ctx.events = @() }
    $entry = @{
        timestamp = (Get-Date).ToString("o")
        event     = $EventType
        detail    = $Detail
    }
    $ctx.events += $entry
    if ($ctx.events.Count -gt 500) { $ctx.events = $ctx.events[-500..-1] }
    ($ctx | ConvertTo-Json -Depth 6) | Out-File -FilePath $CONTEXT_CACHE -Encoding UTF8 -Force
}

# --- Simple recommender
function Generate-Recommendations {
    $suggestions = @()
    if (Test-Path $CONTEXT_CACHE) {
        $ctx = Get-Content $CONTEXT_CACHE -Raw | ConvertFrom-Json
        $counts = @{}
        foreach ($e in $ctx.events) {
            $k = $e.event
            if (-not $counts.ContainsKey($k)) { $counts[$k] = 0 }
            $counts[$k] += 1
        }
        if ($counts.ContainsKey("RCL_MISSING") -and $counts["RCL_MISSING"] -ge 3) { $suggestions += "권장: RCL 경로 레거시 검사 스크립트 추가 및 경로 등록 강화" }
        if ($counts.ContainsKey("EOF_FIX") -and $counts["EOF_FIX"] -ge 2)    { $suggestions += "권장: RCL 생성시 JSON 템플릿 유효성 검사(Pre-commit) 도입" }
        if ($counts.ContainsKey("TEST_RECOVERY") -and $counts["TEST_RECOVERY"] -ge 5) { $suggestions += "권장: 자동 복원 빈번 발생 → 원인 분석(Drive sync/permission) 권고" }
    }
    if ($suggestions.Count -lt 3) { $suggestions += "권장: 엔진 운영 로그 주기(예: daily) 및 주요 경보(Threshold) 설정" }
    $now = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss")
    $out = @("=== Recommendations (Generated: $now) ===")
    $idx = 1
    foreach ($s in $suggestions[0..([math]::Min($suggestions.Count-1,2))]) { $out += ("{0}. {1}" -f $idx, $s); $idx += 1 }
    $out | Out-File -FilePath $RECOMMEND_FILE -Encoding UTF8 -Force
    Write-Log "INFO" "Recommendations generated and saved."
}

# --- Recovery routine
function Invoke-Recovery {
    param([string]$ErrorMessage)

    Write-Log "ERROR" "Recovery initiated: $ErrorMessage"
    Update-Context -EventType "RECOVERY_INVOCATION" -Detail $ErrorMessage

    if ($ErrorMessage -match "Cannot find path") {
        Update-Context -EventType "RCL_MISSING" -Detail $ErrorMessage
        Write-Log "WARN" "RCL missing — attempting automatic discovery..."
        $candidate = Get-ChildItem -Path "D:\Endeavour_Dev" -Filter "rcl.json" -Recurse -ErrorAction SilentlyContinue | Select-Object -First 1
        if ($candidate) {
            $env:RCL_PATH = $candidate.FullName
            Write-Log "INFO" "RCL discovered at $env:RCL_PATH"
            Update-Context -EventType "RCL_DISCOVERED" -Detail $env:RCL_PATH
        } else {
            Write-Log "WARN" "RCL not found — creating fallback"
            $json = "{
  `"paths`": {
    `"data_root`": `"D:\\Endeavour_Dev\\data`",
    `"logs`": `"D:\\Endeavour_Dev\\data\\logs`",
    `"cache`": `"D:\\Endeavour_Dev\\data\\cache`"
  },
  `"auto_recovery`": {
    `"on_missing_path`": `"Set-Path -Force`",
    `"on_json_error`": `"Reload-RCL`"
  }
}"
            $json | Out-File -FilePath $RCL_FALLBACK -Encoding UTF8 -Force
            $env:RCL_PATH = $RCL_FALLBACK
            Update-Context -EventType "FALLBACK_CREATED" -Detail $env:RCL_PATH
            Write-Log "INFO" "Fallback RCL created: $env:RCL_PATH"
        }
    }

    if (Test-Path $env:RCL_PATH) {
        try {
            $content = Get-Content -Path $env:RCL_PATH -Raw -Encoding UTF8
            if ($content[-1] -ne "}") {
                Add-Content -Path $env:RCL_PATH -Value "}"
                Update-Context -EventType "EOF_FIX" -Detail $env:RCL_PATH
                Write-Log "INFO" "EOF fixed for $env:RCL_PATH"
            }
        } catch {
            Write-Log "ERROR" "EOF check failed: $($_.Exception.Message)"
        }
    }

    Add-Content -Path $RECOVERY_LOG -Value ("[{0}] AUTO-RECOVERY EXECUTED. PATH={1}" -f (Get-Date -Format "yyyy-MM-dd HH:mm:ss"), $env:RCL_PATH) -Encoding UTF8
    Write-Log "INFO" "Auto-recovery procedure completed."
    Generate-Recommendations
}

# --- Main wrapper
try {
    Write-Log "INFO" "Engine start attempt."
    if (-not $env:RCL_PATH) { $env:RCL_PATH = $RCL_FALLBACK }
    if (-not (Test-Path $env:RCL_PATH)) { throw "Cannot find path $env:RCL_PATH" }
    $RCL = Get-Content -Path $env:RCL_PATH -Raw -Encoding UTF8 | ConvertFrom-Json
    Write-Log "INFO" "RCL loaded from $env:RCL_PATH"
} catch {
    $err = $_.Exception.Message
    Invoke-Recovery -ErrorMessage $err
}

