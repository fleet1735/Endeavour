@echo off
setlocal
set BASE=D:\Endeavour_Dev
set REPORT=%BASE%\ci_report.json
set PS=pwsh

rem 새 콘솔 창을 -NoExit로 열어 로그가 남도록 함
%PS% -NoExit -ExecutionPolicy Bypass -File "%BASE%\tools\ci_local_runner.ps1" -t all -BASE "%BASE%" -ReportPath "%REPORT%"
endlocal
