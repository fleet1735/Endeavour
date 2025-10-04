param(
  [string]$FromDocs = "D:\Endeavour_Dev\docs",
  [string]$FromReports = "D:\Endeavour_Dev\data\reports",
  [string]$To = "D:\GoogleDrive\Endeavour_Share"
)
Write-Host "[export] -> "
robocopy "$FromDocs" "$To\docs" *.md /S /XO /XN /XC /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
robocopy "$FromReports" "$To\reports" *.* /S /XO /XN /XC /R:1 /W:1 /NFL /NDL /NJH /NJS | Out-Null
Write-Host "[export] done."
