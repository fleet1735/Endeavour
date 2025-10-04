# -*- powershell -*-
# Extra guard: forbid 'strategy_examples' usage (except README in docs/strategy_examples/)
Stop = 'Stop'
Push-Location (Split-Path -Parent \)
\ = git diff --cached --name-only --diff-filter=ACMRT | Out-String | % { \.Split("
") } | ? { \ -ne '' }

# 1) 기존 strategies-guard(이미 설치) 로직 유지: import 차단은 별도 스크립트에서 수행된다고 가정
# 2) strategy_examples 경로/문자열 차단 (예외: docs/strategy_examples/README.*)
\ = @()
foreach (\ in \) {
  if (\ -like "docs/strategy_examples/*") {
    \ = Split-Path \ -Leaf
    if (\ -notmatch "^README(\.|$)") { \ += \ }
  } else {
    # staged 내용 검사
    \ = [System.IO.Path]::GetExtension(\)
    if (\ -in @('.py','.md','.txt','.json','.ps1','.sh','.yml','.yaml','.toml')) {
      \# -*- coding: utf-8 -*-
# Back-compat wrapper: moved to scripts/runtime_clean.py (operational tool)
# Note: import from Python is not recommended; invoke as a script if needed.
 = git show -- ":\" 2>\
      if (\# -*- coding: utf-8 -*-
# Back-compat wrapper: moved to scripts/runtime_clean.py (operational tool)
# Note: import from Python is not recommended; invoke as a script if needed.
 -match "strategy_examples") { \ += \ }
    }
  }
}
if (\.Count -gt 0) {
  Write-Host "⛔ Pre-commit blocked: 'strategy_examples' references detected." -ForegroundColor Red
  \ | % { Write-Host " - \" }
  Write-Host "  Please use 'setup_examples' instead (README in docs/strategy_examples is allowed only)."
  Pop-Location; exit 1
}
Pop-Location; exit 0
