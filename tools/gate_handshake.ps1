param(
  [string] = ".\validator_report.json",
  [string] = ".\gate_pass.flag"
)
if(-not(Test-Path )){ Write-Host "validator_report.json not found"; exit 2 }
 = Get-Content  -Raw -Encoding UTF8 | ConvertFrom-Json
if(.summary.pass -eq True){
  Set-Content -Path  -Value "PASS" -Encoding utf8NoBOM
  Write-Host "PASS flag created: "
  exit 0
}else{
  Write-Host "Gate FAIL (summary.pass != true)"
  exit 1
}
