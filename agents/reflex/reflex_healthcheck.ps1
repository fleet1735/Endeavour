$Base = "D:\Endeavour_Dev\agents\reflex"
$Report = @{}

function Test-File($path){
    if(Test-Path $path){return "✅ [$path] 존재"}
    else{return "❌ [$path] 없음"}
}

function Test-Json($path){
    try { (Get-Content $path -Raw -Encoding UTF8 | ConvertFrom-Json) | Out-Null; return "✅ JSON 정상" }
    catch { return "❌ JSON 파싱 오류" }
}

function Test-Script($path){
    try { [ScriptBlock]::Create((Get-Content $path -Raw -Encoding UTF8)) | Out-Null; return "✅ 구문 OK" }
    catch { return "❌ 구문 오류" }
}

$Report.RCL = Test-File "$Base\config\rcl.json"
$Report.RCLParse = Test-Json "$Base\config\rcl.json"
$Report.LLM_Prompt = Test-File "$Base\config\llm_analyzer_prompt.txt"
$Report.SelfHeal = Test-Script "$Base\self_heal.ps1"
$Report.Reflex = Test-Script "$Base\reflex.ps1"

$LogDir = "$Base\logs\errors"
if(!(Test-Path $LogDir)){ New-Item -ItemType Directory -Path $LogDir | Out-Null }
"테스트 로그" | Out-File "$LogDir\health_test_$(Get-Date -Format 'yyyyMMdd_HHmmss').txt" -Encoding UTF8

$Report | Format-List
