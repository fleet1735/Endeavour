@echo off
REM pre-commit.cmd — Git for Windows 표준 훅 셔틀
REM 동일 폴더의 pre-commit.ps1을 pwsh로 실행
where pwsh >nul 2>nul
if %ERRORLEVEL%==0 (
  pwsh -NoProfile -ExecutionPolicy Bypass -File "%~dp0pre-commit.ps1"
) else (
  powershell -NoProfile -ExecutionPolicy Bypass -File "%~dp0pre-commit.ps1"
)
exit /b %ERRORLEVEL%
