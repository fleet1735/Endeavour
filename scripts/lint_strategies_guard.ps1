param([switch]\)

Stop = 'Stop'
D:\GoogleDrive\Endeavour = Split-Path -Parent \
Push-Location \D:\GoogleDrive\Endeavour

\ = if (\) {
  git ls-files
} else {
  git diff --cached --name-only --diff-filter=ACMRT
}

\ = 'src/endeavour/strategies/'
\ = @('__init__.py','schema.py','registry.py','README.md')
\ = @('.py','.md','.txt','.json','.ps1','.sh','.yml','.yaml','.toml')

\ = @()
foreach (\ in \) {
  if (-not (Test-Path \)) { continue }
  \ = [System.IO.Path]::GetExtension(\)
  if (-not (\ -contains \)) { continue }

  if (\ -like "\*") {
    \ = Split-Path \ -Leaf
    if (\ -contains \) { continue }
  }
  \ = Get-Content -Raw -Path \
  if (\ -match 'from\s+endeavour\.strategies' -or
      \ -match 'import\s+endeavour\.strategies' -or
      \ -match 'endeavour\.strategies\.') {
    \ += \
  }
}

if (\.Count -gt 0) {
  Write-Host "Found forbidden usage in:" -ForegroundColor Red
  \ | ForEach-Object { Write-Host " - \" }
  exit 2
} else {
  Write-Host "OK: no forbidden usage detected."
}
Pop-Location

