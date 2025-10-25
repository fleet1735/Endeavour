param([string]$BASE="D:\Endeavour_Dev")
Set-Location $BASE
$env:PYTHONPATH = "$BASE;$env:PYTHONPATH"
& "$BASE\tools\ci_local_runner.ps1" -t all -BASE $BASE -ReportPath "$BASE\ci_report.json"
