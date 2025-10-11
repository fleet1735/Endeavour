# ============================================
# Reflex HealthCheck v2.1 (Hotfix)
# 작성: 2025-10-10 / JK 전무님 전용
# 수정: Tee-Object 인코딩 매개변수 제거
# ============================================

$Base = "D:\Endeavour_Dev\agents\reflex"
$Report = @{}
$ts = Get-Date -Format 'yyyyMMdd_HHmmss'
$LogFile = "$Base\logs\health_report_$ts.txt"

# ---------- 함수 정의 ----------
function Exists($path){ if(Test-Path $path){return "✅ 존재"} else {return "❌ 없음"} }
function ValidJson($path){ 
    if(!(Test-Path $path)){return "❌ 파일 없음"}
    try { (Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json) | Out-Null; return "✅ JSON 정상" }
    catch { return "❌ JSON 파싱 오류" }
}
function ValidScript($path){
    if(!(Test-Path $path)){return "❌ 파일 없음"}
    try { [ScriptBlock]::Create((Get-Content $path -Raw -Encoding UTF8)) | Out-Null; return "✅ 구문 OK" }
    catch { return "❌ 구문 오류" }
}

# ---------- 파일 검사 ----------
$Report.MainEngine   = "auto_reflex_engine.ps1 : " + (ValidScript "$Base\auto_reflex_engine.ps1")
$Report.ContextAnal  = "context_analyzer.ps1   : " + (ValidScript "$Base\context_analyzer.ps1")
$Report.InitDirs     = "init_reflex_dirs.ps1   : " + (ValidScript "$Base\init_reflex_dirs.ps1")
$Report.LogRotate    = "log_rotation.ps1       : " + (ValidScript "$Base\log_rotation.ps1")
$Report.BusEmit      = "bus\\emit_event.ps1    : " + (ValidScript "$Base\bus\emit_event.ps1")
$Report.BusHandler   = "bus\\event_bus.ps1     : " + (ValidScript "$Base\bus\event_bus.ps1")

# ---------- Config 검사 ----------
$Report.SelfHealConf   = "self_heal.json        : " + (ValidJson "$Base\config\self_heal.json")
$Report.SelfHealState  = "self_heal_state.json  : " + (ValidJson "$Base\config\self_heal_state.json")
$Report.ContextCache   = "context_cache.json    : " + (ValidJson "$Base\config\context_cache.json")
$Report.RecommendTxt   = "recommendations.txt   : " + (Exists "$Base\config\recommendations.txt")

# ---------- 로그 검사 ----------
$logDir = "$Base\logs"
$logs = Get-ChildItem $logDir -File -ErrorAction SilentlyContinue | Sort-Object LastWriteTime -Descending
if($logs.Count -gt 0){
    $latest = $logs[0]
    $Report.LatestLog = "📄 최신 로그: $($latest.Name) / $([int]((Get-Date)-$latest.LastWriteTime).TotalMinutes)분 전 갱신"
}else{
    $Report.LatestLog = "❌ 로그 파일 없음"
}

# ---------- 이벤트 버스 검사 ----------
$busFile = "$Base\bus\stream\bus_events.jsonl"
if(Test-Path $busFile){
    $size = (Get-Item $busFile).Length
    $Report.BusEvents = "bus_events.jsonl 크기: $size bytes"
    $lastLine = Get-Content $busFile -Tail 1 -ErrorAction SilentlyContinue
    if($lastLine){ $Report.BusLastEvent = "마지막 이벤트: $($lastLine.Substring(0,[Math]::Min(200,$lastLine.Length)))" }
}else{
    $Report.BusEvents = "❌ bus_events.jsonl 없음"
}

# ---------- 보고서 출력 ----------
"=== Reflex Health Report ($ts) ===" | Tee-Object -FilePath $LogFile
foreach($k in $Report.Keys){
    "$k : $($Report[$k])" | Tee-Object -FilePath $LogFile -Append
}
"`nReport saved to: $LogFile" | Tee-Object -FilePath $LogFile -Append
# ============================================

