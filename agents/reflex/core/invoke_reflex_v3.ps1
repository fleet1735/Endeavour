$global:ReflexConfig = @{
  RulesPath = "D:\Endeavour_Dev\agents\reflex\config\rules.json"
  ErrorMem  = "D:\Endeavour_Dev\agents\reflex\logs\error_memory.jsonl"
  History   = "D:\Endeavour_Dev\agents\reflex\logs\recovery_history.log"
  MaxRetry  = 3
}

function Write-ReflexLog {
  param([string]$Message)
  $ts = (Get-Date).ToString("yyyy-MM-dd HH:mm:ss.fff")
  "$ts `t $Message" | Add-Content -Path $global:ReflexConfig.History -Encoding UTF8
  Write-Host $Message
}

function Load-Rules {
  $path = $global:ReflexConfig.RulesPath
  if (!(Test-Path $path)) { return @() }
  try { (Get-Content $path -Raw | ConvertFrom-Json) } catch { @() }
}

function Apply-Edits {
  param([string]$Source,[array]$Edits)
  $out = $Source
  foreach ($e in $Edits) {
    if ($e.type -eq "regex_replace") {
      $out = [regex]::Replace($out, $e.find, $e.replace)
    }
  }
  return $out
}

function Save-ErrorMemory {
  param(
    [string]$ScriptPath,
    [string]$ErrorMessage,
    [string]$Category = "Unknown",
    [string]$Snippet = ""
  )
  $rec = [pscustomobject]@{
    timestamp = (Get-Date).ToString("o")
    script    = $ScriptPath
    error     = $ErrorMessage
    category  = $Category
    snippet   = $Snippet
  } | ConvertTo-Json -Compress
  $rec | Add-Content -Path $global:ReflexConfig.ErrorMem -Encoding UTF8
}

function Test-ReflexSyntax {
  param([string]$Code)
  try {
    [ScriptBlock]::Create($Code) | Out-Null
    return $true
  } catch {
    return $false
  }
}

function Invoke-Reflex {
  param(
    [Parameter(Mandatory)][string]$ScriptPath,
    [int]$MaxRetry = $global:ReflexConfig.MaxRetry
  )

  Write-ReflexLog "RUN_START: $ScriptPath"

  if (!(Test-Path $ScriptPath)) {
    Write-ReflexLog "RUN_ABORT: file_not_found"
    return
  }

  try {
    & $ScriptPath
    Write-ReflexLog "RUN_OK: $ScriptPath"
  } catch {
    $err = $_.Exception.Message
    Write-ReflexLog "ERR_DETECTED: $($err -replace "`n",' ')"

    $rules = Load-Rules | Where-Object { $_.enabled -eq $true }
    $rule  = $rules | Where-Object { $err -match $_.pattern } | Select-Object -First 1

    if ($null -ne $rule) {
      Write-ReflexLog "RULE_MATCH: $($rule.id)"
      $orig  = Get-Content $ScriptPath -Raw
      $fixed = Apply-Edits -Source $orig -Edits $rule.edits

      if ($fixed -ne $orig) {
        # v3.1: 구문 검증
        if (Test-ReflexSyntax -Code $fixed) {
          $fixed | Set-Content -Path $ScriptPath -Encoding UTF8
          Write-ReflexLog "AUTO_FIX_APPLIED: $($rule.id)"

          if ($MaxRetry -le 0) {
            Write-ReflexLog "STOP_RETRY: max_retry_reached"
            return
          }
          Invoke-Reflex -ScriptPath $ScriptPath -MaxRetry ($MaxRetry - 1)
          return
        } else {
          # 검증 실패 → 롤백
          $orig | Set-Content -Path $ScriptPath -Encoding UTF8
          Write-ReflexLog "RULE_FAILED_VALIDATE: $($rule.id) -> ROLLBACK"
          Save-ErrorMemory -ScriptPath $ScriptPath -ErrorMessage "validate_fail: $($rule.id)" -Category "OverFix" -Snippet ($orig.Substring(0,[Math]::Min(200,$orig.Length)))
          return
        }
      } else {
        Write-ReflexLog "RULE_NO_EFFECT: $($rule.id)"
      }
    }

    # 규칙 미적용 → 학습 메모리 저장
    $snippet = ""
    try { $snippet = (Get-Content $ScriptPath -TotalCount 3) -join "`n" } catch {}
    Save-ErrorMemory -ScriptPath $ScriptPath -ErrorMessage $err -Category "Unmatched" -Snippet $snippet
    Write-ReflexLog "MEMO_SAVED: unmatched_error"
  }
}
