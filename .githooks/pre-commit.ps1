Write-Host "[pre-commit] running..."
$ok = $true
Get-ChildItem -Recurse -Include *.ps1 | ForEach-Object {
  try {
    $c = Get-Content $_.FullName -Raw -Encoding UTF8
    if ($c.Length -lt 200000) { [ScriptBlock]::Create($c) | Out-Null }
  } catch {
    Write-Host "[pre-commit] Syntax check failed: "
    Write-Host $_.Exception.Message
    $ok = $false
  }
}
if (-not $ok) { Write-Host "[pre-commit] WARNING: syntax issues detected (허용 모드)" }
exit 0