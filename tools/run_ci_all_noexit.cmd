@echo off
setlocal
set "BASE=D:\Endeavour_Dev"
set "REPORT=%BASE%\ci_report.json"
set "PS=pwsh"
"%PS%" -NoExit -ExecutionPolicy Bypass -File "%BASE%\tools\ci_local_runner.ps1" -t all -BASE "%BASE%" -ReportPath "%REPORT%"
endlocal
