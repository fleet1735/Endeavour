# =========================================================
# Reflex v3.2 — Promote-Rule Loop
# 파일: core\promote_rules_v3_2.ps1
# 기능:
#  - error_memory.jsonl → 후보 규칙 생성
#  - 후보 조회/리포트
#  - Dry-Run 검증 후 rules.json으로 승격
# =========================================================

$global:ReflexPaths = @{
  RulesPath     = "D:\Endeavour_Dev\agents\reflex\config\rules.json"
  ErrorMemPath  = "D:\Endeavour_Dev\agents\reflex\logs\error_memory.jsonl"
  CandDir       = "D:\Endeavour_Dev\agents\reflex\config\candidates"
  CandPath      = "D:\Endeavour_Dev\agents\reflex\config\candidates\candidate_rules.json"
  ReportPath    = "D:\Endeavour_Dev\agents\reflex\config\candidates\candidates_report.md"
  HistoryPath   = "D:\Endeavour_Dev\agents\reflex\logs\recovery_history.log"
}

function Write-ReflexAudit {
  param([string]$Msg)
  $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
  "$ts `t $Msg" | Add-Content -Path $global:ReflexPaths.HistoryPath -Encoding UTF8
  Write-Host $Msg
}

function Ensure-JsonFile {
  param([string]$Path,[string]$DefaultJson="[]")
  if (!(Test-Path $Path)) { $DefaultJson | Set-Content -Path $Path -Encoding UTF8 }
}

function Load-Json {
  param([string]$Path)
  if (!(Test-Path $Path)) { return @() }
  try { (Get-Content $Path -Raw | ConvertFrom-Json) } catch { @() }
}

function Save-Json {
  param([string]$Path,[object]$Obj)
  ($Obj | ConvertTo-Json -Depth 8) | Set-Content -Path $Path -Encoding UTF8
}

function Normalize-ErrorText {
  param([string]$Text)
  # 라인/경로/숫자 등을 정규화해 "패턴"만 남김
  $t = $Text -replace "`r?`n"," "
  $t = $t -replace ":[0-9]+",""          # 라인/열 번호 제거
  $t = $t -replace "\\\\","\"            # 경로 백슬래시 정규화
  $t = $t.Trim()
  return $t
}

function Escape-RegexLiteral {
  param([string]$Text)
  [Regex]::Escape($Text)
}

function New-RuleCandidates {
  param(
    [int]$TopN = 10,
    [int]$MinCount = 1
  )
  Ensure-JsonFile -Path $global:ReflexPaths.CandPath
  $cand = Load-Json -Path $global:ReflexPaths.CandPath
  $mem  = @()
  if (Test-Path $global:ReflexPaths.ErrorMemPath) {
    $mem = Get-Content $global:ReflexPaths.ErrorMemPath | ForEach-Object {
      try { $_ | ConvertFrom-Json } catch { $null }
    } | Where-Object { $_ -ne $null }
  }
  if ($mem.Count -eq 0) {
    Write-Host "error_memory.jsonl 비어 있음 — 생성할 후보가 없습니다."
    return
  }

  # 그룹핑
  $groups = $mem | ForEach-Object {
    [pscustomobject]@{
      key     = Normalize-ErrorText $_.error
      example = $_
    }
  } | Group-Object key | Where-Object { $_.Count -ge $MinCount } |
      Sort-Object Count -Descending | Select-Object -First $TopN

  $newCands = @()
  $idx = 1
  foreach ($g in $groups) {
    $key = $g.Name
    $rx  = Escape-RegexLiteral $key
    $id  = ("CAND_{0:0000}" -f $idx)
    $idx++

    # 기본 후보 스켈레톤 (edits는 관리자가 채움)
    $obj = [pscustomobject]@{
      id          = $id
      description = "Auto-generated from error_memory: " + ($key.Substring(0, [Math]::Min(90,$key.Length)))
      pattern     = $rx
      edits       = @()     # 관리자가 Promote-Rule 시 채움
      enabled     = $false
      confidence  = 0.6
      samples     = ($g.Group | Select-Object -First 3)  # 참고 샘플
      count       = $g.Count
    }
    $newCands += $obj
  }

  # 기존 후보와 중복 제거(패턴 기준)
  foreach ($nc in $newCands) {
    if (-not ($cand | Where-Object { $_.pattern -eq $nc.pattern })) {
      $cand += $nc
    }
  }
  Save-Json -Path $global:ReflexPaths.CandPath -Obj $cand

  # MD 리포트
  $lines = @("# Candidate Rules (auto-generated)", "", "| id | count | confidence | description |", "|---|---:|---:|---|")
  foreach ($c in $cand | Sort-Object count -Descending) {
    $lines += "| {0} | {1} | {2} | {3} |" -f $c.id,$c.count,$c.confidence,($c.description -replace "\|","/")
  }
  $lines -join "`n" | Set-Content -Path $global:ReflexPaths.ReportPath -Encoding UTF8

  Write-ReflexAudit "CANDIDATES_GENERATED: $($newCands.Count) item(s)"
  Write-Host "  • 후보 JSON : $($global:ReflexPaths.CandPath)"
  Write-Host "  • 리포트    : $($global:ReflexPaths.ReportPath)"
}

function Show-RuleCandidates {
  if (!(Test-Path $global:ReflexPaths.CandPath)) { Write-Host "후보 없음."; return }
  $cand = Load-Json -Path $global:ReflexPaths.CandPath | Sort-Object count -Descending
  if (!$cand) { Write-Host "후보 없음."; return }
  $cand | Select-Object id,count,confidence,description | Format-Table -AutoSize
}

function DryRun-Validate-Rule {
  <#
    후보 규칙을 특정 스크립트에 가상 적용해 파싱 성공 여부 확인
    예) DryRun-Validate-Rule -Id CAND_0001 -Find 'regex' -Replace 'text' -ScriptPath '...\test.ps1'
  #>
  param(
    [Parameter(Mandatory)][string]$Id,
    [Parameter(Mandatory)][string]$Find,
    [Parameter(Mandatory)][string]$Replace,
    [Parameter(Mandatory)][string]$ScriptPath
  )
  if (!(Test-Path $ScriptPath)) { Write-Host "파일 없음: $ScriptPath"; return $false }
  $cand = Load-Json -Path $global:ReflexPaths.CandPath | Where-Object { $_.id -eq $Id } | Select-Object -First 1
  if (!$cand) { Write-Host "후보 없음: $Id"; return $false }
  $raw = Get-Content $ScriptPath -Raw
  $fixed = [regex]::Replace($raw, $Find, $Replace)
  try {
    [ScriptBlock]::Create($fixed) | Out-Null
    Write-Host "Dry-Run OK (파싱 성공)"
    return $true
  } catch {
    Write-Host "Dry-Run 실패 (파싱 오류): $($_.Exception.Message)"
    return $false
  }
}

function Promote-Rule {
  <#
    후보를 실제 규칙으로 승격
    -Find/-Replace는 최소 1개 필수. 여러 개 승격하려면 여러 번 실행.
    예) Promote-Rule -Id CAND_0001 -Find '\\[int\\]\\s*\\)' -Replace '[int]$n)' -Confidence 0.8
  #>
  param(
    [Parameter(Mandatory)][string]$Id,
    [Parameter(Mandatory)][string]$Find,
    [Parameter(Mandatory)][string]$Replace,
    [double]$Confidence = 0.8
  )
  Ensure-JsonFile -Path $global:ReflexPaths.CandPath
  Ensure-JsonFile -Path $global:ReflexPaths.RulesPath

  $candAll = Load-Json -Path $global:ReflexPaths.CandPath
  $cand    = $candAll | Where-Object { $_.id -eq $Id } | Select-Object -First 1
  if (!$cand) { Write-Host "후보 없음: $Id"; return }

  $rules = Load-Json -Path $global:ReflexPaths.RulesPath

  $new = [pscustomobject]@{
    id          = $Id
    description = $cand.description
    pattern     = $cand.pattern
    edits       = @(@{type="regex_replace"; find=$Find; replace=$Replace})
    enabled     = $true
    confidence  = $Confidence
  }

  # 중복 패턴 방지
  if ($rules | Where-Object { $_.pattern -eq $new.pattern }) {
    Write-Host "이미 동일 패턴 규칙이 존재합니다. (pattern 중복)"
    return
  }

  $rules = @($rules) + @($new)
  Save-Json -Path $global:ReflexPaths.RulesPath -Obj $rules

  # 후보 목록에서 제거
  $candAll = $candAll | Where-Object { $_.id -ne $Id }
  Save-Json -Path $global:ReflexPaths.CandPath -Obj $candAll

  Write-ReflexAudit "RULE_PROMOTED: $Id (pattern added)"
  Write-Host "승격 완료 → rules.json 반영"
}
# =========================================================
