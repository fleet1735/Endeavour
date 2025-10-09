# pre-commit.ps1 — 경량 구문 점검(허용 모드), 항상 0으로 종료
Write-Host "[pre-commit] PowerShell hook running..."
\False = \True
Get-ChildItem -Recurse -Include *.ps1 | ForEach-Object {
  try {
    \$ErrorActionPreference='Stop'
param([string]$msg)

  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $line = "$ts $msg"
  Add-Content -Path $Log -Value $line
  if(-not [System.Diagnostics.EventLog]::SourceExists($EvtSrc)){ try{ New-EventLog -LogName Application -Source $EvtSrc }catch{} }
  try { Write-EventLog -LogName Application -Source $EvtSrc -EntryType Information -EventId 1000 -Message $line } catch {}
 = param([string]$msg)

  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $line = "$ts $msg"
  Add-Content -Path $Log -Value $line
  if(-not [System.Diagnostics.EventLog]::SourceExists($EvtSrc)){ try{ New-EventLog -LogName Application -Source $EvtSrc }catch{} }
  try { Write-EventLog -LogName Application -Source $EvtSrc -EntryType Information -EventId 1000 -Message $line } catch {}

param([string]$Path, [long]$MaxBytes=5MB, [int]$Keep=7)

  if(!(Test-Path $Path)){return}
  $fi = Get-Item $Path; if($fi.Length -lt $MaxBytes){return}
  for($i=$Keep-1;$i -ge 1;$i--){ $old="$Path.$i"; $new="$Path." + ($i+1); if(Test-Path $old){ Rename-Item $old $new -Force } }
  Copy-Item $Path "$Path.1" -Force; Clear-Content $Path
 = param([string]$Path, [long]$MaxBytes=5MB, [int]$Keep=7)

  if(!(Test-Path $Path)){return}
  $fi = Get-Item $Path; if($fi.Length -lt $MaxBytes){return}
  for($i=$Keep-1;$i -ge 1;$i--){ $old="$Path.$i"; $new="$Path." + ($i+1); if(Test-Path $old){ Rename-Item $old $new -Force } }
  Copy-Item $Path "$Path.1" -Force; Clear-Content $Path

param([string]$topic, [object]$payload, [string]$source="self_heal")

  $o = [pscustomobject]@{ ts=(Get-Date).ToString("s"); source=$source; topic=$topic; payload=$payload }
  Add-Content -Path $Bus -Value ($o | ConvertTo-Json -Depth 8 -Compress)
   = param([string]$topic, [object]$payload, [string]$source="self_heal")

  $o = [pscustomobject]@{ ts=(Get-Date).ToString("s"); source=$source; topic=$topic; payload=$payload }
  Add-Content -Path $Bus -Value ($o | ConvertTo-Json -Depth 8 -Compress)

param([string]$Path)

  if(!(Test-Path $Path)){ return @{rc=0; note="skip(missing)"} }
  $raw = Get-Content $Path -Raw
  $raw = $raw -replace "^\xEF\xBB\xBF","" -replace "}\s*[^}]*$","}" -replace ",\s*([}\]])","`$1"
  try { $obj = $raw | ConvertFrom-Json -ErrorAction Stop } catch { return @{rc=1; err="json_parse_fail"} }
  Set-Content $Path ($obj | ConvertTo-Json -Depth 50) -Encoding UTF8
  return @{rc=0}
 = param([string]$Path)

  if(!(Test-Path $Path)){ return @{rc=0; note="skip(missing)"} }
  $raw = Get-Content $Path -Raw
  $raw = $raw -replace "^\xEF\xBB\xBF","" -replace "}\s*[^}]*$","}" -replace ",\s*([}\]])","`$1"
  try { $obj = $raw | ConvertFrom-Json -ErrorAction Stop } catch { return @{rc=1; err="json_parse_fail"} }
  Set-Content $Path ($obj | ConvertTo-Json -Depth 50) -Encoding UTF8
  return @{rc=0}


  $candidates = @("auto_reflex_engine.ps1","context_analyzer.ps1") | % { Join-Path $Reflex $_ } | ?{ Test-Path $_ }
  if($candidates.Count -gt 0){
    $target = $candidates[0]
    Start-Process -FilePath $Pwsh -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File', $target) -WindowStyle Hidden
    return @{rc=0; fix="restart_reflex"; started=$target}
  } else {
    return @{rc=$null; fix="restart_reflex"; note="no_reflex_entry"}
  }
 = 
  $candidates = @("auto_reflex_engine.ps1","context_analyzer.ps1") | % { Join-Path $Reflex $_ } | ?{ Test-Path $_ }
  if($candidates.Count -gt 0){
    $target = $candidates[0]
    Start-Process -FilePath $Pwsh -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File', $target) -WindowStyle Hidden
    return @{rc=0; fix="restart_reflex"; started=$target}
  } else {
    return @{rc=$null; fix="restart_reflex"; note="no_reflex_entry"}
  }


  Rotate-Log -Path $Log -MaxBytes 5MB -Keep 7
  Write-Log "[INFO] Self-Heal 시작"
  $now = Get-Date
  $sig = "json_eof|recreate_paths|restart_reflex"

  if($g.last_sig -eq $sig -and $g.last_at){
    $lastAt = Get-Date $g.last_at
    if(($now - $lastAt).TotalSeconds -lt $DEDUPE_SECONDS){
      Write-Log "[DEDUP] $DEDUPE_SECONDS 초 이내 동일 시나리오 억제"
      Post-Bus -topic "SelfHeal/Result" -payload @{ ok=$true; dedup=$true; actions=@(@{fix="dedup_suppress"; rc=0}) }
      return @{ok=$true; dedup=$true}
    }
  }

  $a1 = Fix-JsonFile -Path $Rcl; if($a1.rc -eq 0){ Write-Log "[FIX_JSON] 교정/검증 완료: $Rcl" } else { Write-Log "[FIX_JSON] 실패: $($a1|ConvertTo-Json -Compress)" ; $a1.rc=1; $a1.fix="json_eof" }
  foreach($p in @($SelfH,$Reflex,(Split-Path $Bus),$LogDir)){ if(!(Test-Path $p)){ New-Item $p -ItemType Directory -Force | Out-Null } }
  $a2 = @{fix="recreate_paths"; rc=0}
  $a3 = Restart-Reflex

  $res = @{ ok=$true; actions=@(
    @{fix="json_eof"; rc=$a1.rc},
    $a2,
    @{fix="restart_reflex"; rc=$a3.rc}
  )}
  Write-Log ("[INFO] Self-Heal 완료: " + ($res|ConvertTo-Json -Compress))
  Post-Bus -topic "SelfHeal/Result" -payload $res
  $g.last_sig = $sig; $g.last_at = $now.ToString("o"); Save-State $g
  return $res
 = 
  Rotate-Log -Path $Log -MaxBytes 5MB -Keep 7
  Write-Log "[INFO] Self-Heal 시작"
  $now = Get-Date
  $sig = "json_eof|recreate_paths|restart_reflex"

  if($g.last_sig -eq $sig -and $g.last_at){
    $lastAt = Get-Date $g.last_at
    if(($now - $lastAt).TotalSeconds -lt $DEDUPE_SECONDS){
      Write-Log "[DEDUP] $DEDUPE_SECONDS 초 이내 동일 시나리오 억제"
      Post-Bus -topic "SelfHeal/Result" -payload @{ ok=$true; dedup=$true; actions=@(@{fix="dedup_suppress"; rc=0}) }
      return @{ok=$true; dedup=$true}
    }
  }

  $a1 = Fix-JsonFile -Path $Rcl; if($a1.rc -eq 0){ Write-Log "[FIX_JSON] 교정/검증 완료: $Rcl" } else { Write-Log "[FIX_JSON] 실패: $($a1|ConvertTo-Json -Compress)" ; $a1.rc=1; $a1.fix="json_eof" }
  foreach($p in @($SelfH,$Reflex,(Split-Path $Bus),$LogDir)){ if(!(Test-Path $p)){ New-Item $p -ItemType Directory -Force | Out-Null } }
  $a2 = @{fix="recreate_paths"; rc=0}
  $a3 = Restart-Reflex

  $res = @{ ok=$true; actions=@(
    @{fix="json_eof"; rc=$a1.rc},
    $a2,
    @{fix="restart_reflex"; rc=$a3.rc}
  )}
  Write-Log ("[INFO] Self-Heal 완료: " + ($res|ConvertTo-Json -Compress))
  Post-Bus -topic "SelfHeal/Result" -payload $res
  $g.last_sig = $sig; $g.last_at = $now.ToString("o"); Save-State $g
  return $res

Invoke-SelfHeal | Out-Null
 = Get-Content \.FullName -Raw -Encoding UTF8
    if (\$ErrorActionPreference='Stop'
param([string]$msg)

  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $line = "$ts $msg"
  Add-Content -Path $Log -Value $line
  if(-not [System.Diagnostics.EventLog]::SourceExists($EvtSrc)){ try{ New-EventLog -LogName Application -Source $EvtSrc }catch{} }
  try { Write-EventLog -LogName Application -Source $EvtSrc -EntryType Information -EventId 1000 -Message $line } catch {}
 = param([string]$msg)

  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $line = "$ts $msg"
  Add-Content -Path $Log -Value $line
  if(-not [System.Diagnostics.EventLog]::SourceExists($EvtSrc)){ try{ New-EventLog -LogName Application -Source $EvtSrc }catch{} }
  try { Write-EventLog -LogName Application -Source $EvtSrc -EntryType Information -EventId 1000 -Message $line } catch {}

param([string]$Path, [long]$MaxBytes=5MB, [int]$Keep=7)

  if(!(Test-Path $Path)){return}
  $fi = Get-Item $Path; if($fi.Length -lt $MaxBytes){return}
  for($i=$Keep-1;$i -ge 1;$i--){ $old="$Path.$i"; $new="$Path." + ($i+1); if(Test-Path $old){ Rename-Item $old $new -Force } }
  Copy-Item $Path "$Path.1" -Force; Clear-Content $Path
 = param([string]$Path, [long]$MaxBytes=5MB, [int]$Keep=7)

  if(!(Test-Path $Path)){return}
  $fi = Get-Item $Path; if($fi.Length -lt $MaxBytes){return}
  for($i=$Keep-1;$i -ge 1;$i--){ $old="$Path.$i"; $new="$Path." + ($i+1); if(Test-Path $old){ Rename-Item $old $new -Force } }
  Copy-Item $Path "$Path.1" -Force; Clear-Content $Path

param([string]$topic, [object]$payload, [string]$source="self_heal")

  $o = [pscustomobject]@{ ts=(Get-Date).ToString("s"); source=$source; topic=$topic; payload=$payload }
  Add-Content -Path $Bus -Value ($o | ConvertTo-Json -Depth 8 -Compress)
   = param([string]$topic, [object]$payload, [string]$source="self_heal")

  $o = [pscustomobject]@{ ts=(Get-Date).ToString("s"); source=$source; topic=$topic; payload=$payload }
  Add-Content -Path $Bus -Value ($o | ConvertTo-Json -Depth 8 -Compress)

param([string]$Path)

  if(!(Test-Path $Path)){ return @{rc=0; note="skip(missing)"} }
  $raw = Get-Content $Path -Raw
  $raw = $raw -replace "^\xEF\xBB\xBF","" -replace "}\s*[^}]*$","}" -replace ",\s*([}\]])","`$1"
  try { $obj = $raw | ConvertFrom-Json -ErrorAction Stop } catch { return @{rc=1; err="json_parse_fail"} }
  Set-Content $Path ($obj | ConvertTo-Json -Depth 50) -Encoding UTF8
  return @{rc=0}
 = param([string]$Path)

  if(!(Test-Path $Path)){ return @{rc=0; note="skip(missing)"} }
  $raw = Get-Content $Path -Raw
  $raw = $raw -replace "^\xEF\xBB\xBF","" -replace "}\s*[^}]*$","}" -replace ",\s*([}\]])","`$1"
  try { $obj = $raw | ConvertFrom-Json -ErrorAction Stop } catch { return @{rc=1; err="json_parse_fail"} }
  Set-Content $Path ($obj | ConvertTo-Json -Depth 50) -Encoding UTF8
  return @{rc=0}


  $candidates = @("auto_reflex_engine.ps1","context_analyzer.ps1") | % { Join-Path $Reflex $_ } | ?{ Test-Path $_ }
  if($candidates.Count -gt 0){
    $target = $candidates[0]
    Start-Process -FilePath $Pwsh -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File', $target) -WindowStyle Hidden
    return @{rc=0; fix="restart_reflex"; started=$target}
  } else {
    return @{rc=$null; fix="restart_reflex"; note="no_reflex_entry"}
  }
 = 
  $candidates = @("auto_reflex_engine.ps1","context_analyzer.ps1") | % { Join-Path $Reflex $_ } | ?{ Test-Path $_ }
  if($candidates.Count -gt 0){
    $target = $candidates[0]
    Start-Process -FilePath $Pwsh -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File', $target) -WindowStyle Hidden
    return @{rc=0; fix="restart_reflex"; started=$target}
  } else {
    return @{rc=$null; fix="restart_reflex"; note="no_reflex_entry"}
  }


  Rotate-Log -Path $Log -MaxBytes 5MB -Keep 7
  Write-Log "[INFO] Self-Heal 시작"
  $now = Get-Date
  $sig = "json_eof|recreate_paths|restart_reflex"

  if($g.last_sig -eq $sig -and $g.last_at){
    $lastAt = Get-Date $g.last_at
    if(($now - $lastAt).TotalSeconds -lt $DEDUPE_SECONDS){
      Write-Log "[DEDUP] $DEDUPE_SECONDS 초 이내 동일 시나리오 억제"
      Post-Bus -topic "SelfHeal/Result" -payload @{ ok=$true; dedup=$true; actions=@(@{fix="dedup_suppress"; rc=0}) }
      return @{ok=$true; dedup=$true}
    }
  }

  $a1 = Fix-JsonFile -Path $Rcl; if($a1.rc -eq 0){ Write-Log "[FIX_JSON] 교정/검증 완료: $Rcl" } else { Write-Log "[FIX_JSON] 실패: $($a1|ConvertTo-Json -Compress)" ; $a1.rc=1; $a1.fix="json_eof" }
  foreach($p in @($SelfH,$Reflex,(Split-Path $Bus),$LogDir)){ if(!(Test-Path $p)){ New-Item $p -ItemType Directory -Force | Out-Null } }
  $a2 = @{fix="recreate_paths"; rc=0}
  $a3 = Restart-Reflex

  $res = @{ ok=$true; actions=@(
    @{fix="json_eof"; rc=$a1.rc},
    $a2,
    @{fix="restart_reflex"; rc=$a3.rc}
  )}
  Write-Log ("[INFO] Self-Heal 완료: " + ($res|ConvertTo-Json -Compress))
  Post-Bus -topic "SelfHeal/Result" -payload $res
  $g.last_sig = $sig; $g.last_at = $now.ToString("o"); Save-State $g
  return $res
 = 
  Rotate-Log -Path $Log -MaxBytes 5MB -Keep 7
  Write-Log "[INFO] Self-Heal 시작"
  $now = Get-Date
  $sig = "json_eof|recreate_paths|restart_reflex"

  if($g.last_sig -eq $sig -and $g.last_at){
    $lastAt = Get-Date $g.last_at
    if(($now - $lastAt).TotalSeconds -lt $DEDUPE_SECONDS){
      Write-Log "[DEDUP] $DEDUPE_SECONDS 초 이내 동일 시나리오 억제"
      Post-Bus -topic "SelfHeal/Result" -payload @{ ok=$true; dedup=$true; actions=@(@{fix="dedup_suppress"; rc=0}) }
      return @{ok=$true; dedup=$true}
    }
  }

  $a1 = Fix-JsonFile -Path $Rcl; if($a1.rc -eq 0){ Write-Log "[FIX_JSON] 교정/검증 완료: $Rcl" } else { Write-Log "[FIX_JSON] 실패: $($a1|ConvertTo-Json -Compress)" ; $a1.rc=1; $a1.fix="json_eof" }
  foreach($p in @($SelfH,$Reflex,(Split-Path $Bus),$LogDir)){ if(!(Test-Path $p)){ New-Item $p -ItemType Directory -Force | Out-Null } }
  $a2 = @{fix="recreate_paths"; rc=0}
  $a3 = Restart-Reflex

  $res = @{ ok=$true; actions=@(
    @{fix="json_eof"; rc=$a1.rc},
    $a2,
    @{fix="restart_reflex"; rc=$a3.rc}
  )}
  Write-Log ("[INFO] Self-Heal 완료: " + ($res|ConvertTo-Json -Compress))
  Post-Bus -topic "SelfHeal/Result" -payload $res
  $g.last_sig = $sig; $g.last_at = $now.ToString("o"); Save-State $g
  return $res

Invoke-SelfHeal | Out-Null
.Length -lt 200000) { [ScriptBlock]::Create(\$ErrorActionPreference='Stop'
param([string]$msg)

  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $line = "$ts $msg"
  Add-Content -Path $Log -Value $line
  if(-not [System.Diagnostics.EventLog]::SourceExists($EvtSrc)){ try{ New-EventLog -LogName Application -Source $EvtSrc }catch{} }
  try { Write-EventLog -LogName Application -Source $EvtSrc -EntryType Information -EventId 1000 -Message $line } catch {}
 = param([string]$msg)

  $ts = Get-Date -Format "yyyy-MM-dd HH:mm:ss"
  $line = "$ts $msg"
  Add-Content -Path $Log -Value $line
  if(-not [System.Diagnostics.EventLog]::SourceExists($EvtSrc)){ try{ New-EventLog -LogName Application -Source $EvtSrc }catch{} }
  try { Write-EventLog -LogName Application -Source $EvtSrc -EntryType Information -EventId 1000 -Message $line } catch {}

param([string]$Path, [long]$MaxBytes=5MB, [int]$Keep=7)

  if(!(Test-Path $Path)){return}
  $fi = Get-Item $Path; if($fi.Length -lt $MaxBytes){return}
  for($i=$Keep-1;$i -ge 1;$i--){ $old="$Path.$i"; $new="$Path." + ($i+1); if(Test-Path $old){ Rename-Item $old $new -Force } }
  Copy-Item $Path "$Path.1" -Force; Clear-Content $Path
 = param([string]$Path, [long]$MaxBytes=5MB, [int]$Keep=7)

  if(!(Test-Path $Path)){return}
  $fi = Get-Item $Path; if($fi.Length -lt $MaxBytes){return}
  for($i=$Keep-1;$i -ge 1;$i--){ $old="$Path.$i"; $new="$Path." + ($i+1); if(Test-Path $old){ Rename-Item $old $new -Force } }
  Copy-Item $Path "$Path.1" -Force; Clear-Content $Path

param([string]$topic, [object]$payload, [string]$source="self_heal")

  $o = [pscustomobject]@{ ts=(Get-Date).ToString("s"); source=$source; topic=$topic; payload=$payload }
  Add-Content -Path $Bus -Value ($o | ConvertTo-Json -Depth 8 -Compress)
   = param([string]$topic, [object]$payload, [string]$source="self_heal")

  $o = [pscustomobject]@{ ts=(Get-Date).ToString("s"); source=$source; topic=$topic; payload=$payload }
  Add-Content -Path $Bus -Value ($o | ConvertTo-Json -Depth 8 -Compress)

param([string]$Path)

  if(!(Test-Path $Path)){ return @{rc=0; note="skip(missing)"} }
  $raw = Get-Content $Path -Raw
  $raw = $raw -replace "^\xEF\xBB\xBF","" -replace "}\s*[^}]*$","}" -replace ",\s*([}\]])","`$1"
  try { $obj = $raw | ConvertFrom-Json -ErrorAction Stop } catch { return @{rc=1; err="json_parse_fail"} }
  Set-Content $Path ($obj | ConvertTo-Json -Depth 50) -Encoding UTF8
  return @{rc=0}
 = param([string]$Path)

  if(!(Test-Path $Path)){ return @{rc=0; note="skip(missing)"} }
  $raw = Get-Content $Path -Raw
  $raw = $raw -replace "^\xEF\xBB\xBF","" -replace "}\s*[^}]*$","}" -replace ",\s*([}\]])","`$1"
  try { $obj = $raw | ConvertFrom-Json -ErrorAction Stop } catch { return @{rc=1; err="json_parse_fail"} }
  Set-Content $Path ($obj | ConvertTo-Json -Depth 50) -Encoding UTF8
  return @{rc=0}


  $candidates = @("auto_reflex_engine.ps1","context_analyzer.ps1") | % { Join-Path $Reflex $_ } | ?{ Test-Path $_ }
  if($candidates.Count -gt 0){
    $target = $candidates[0]
    Start-Process -FilePath $Pwsh -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File', $target) -WindowStyle Hidden
    return @{rc=0; fix="restart_reflex"; started=$target}
  } else {
    return @{rc=$null; fix="restart_reflex"; note="no_reflex_entry"}
  }
 = 
  $candidates = @("auto_reflex_engine.ps1","context_analyzer.ps1") | % { Join-Path $Reflex $_ } | ?{ Test-Path $_ }
  if($candidates.Count -gt 0){
    $target = $candidates[0]
    Start-Process -FilePath $Pwsh -ArgumentList @('-NoProfile','-ExecutionPolicy','Bypass','-File', $target) -WindowStyle Hidden
    return @{rc=0; fix="restart_reflex"; started=$target}
  } else {
    return @{rc=$null; fix="restart_reflex"; note="no_reflex_entry"}
  }


  Rotate-Log -Path $Log -MaxBytes 5MB -Keep 7
  Write-Log "[INFO] Self-Heal 시작"
  $now = Get-Date
  $sig = "json_eof|recreate_paths|restart_reflex"

  if($g.last_sig -eq $sig -and $g.last_at){
    $lastAt = Get-Date $g.last_at
    if(($now - $lastAt).TotalSeconds -lt $DEDUPE_SECONDS){
      Write-Log "[DEDUP] $DEDUPE_SECONDS 초 이내 동일 시나리오 억제"
      Post-Bus -topic "SelfHeal/Result" -payload @{ ok=$true; dedup=$true; actions=@(@{fix="dedup_suppress"; rc=0}) }
      return @{ok=$true; dedup=$true}
    }
  }

  $a1 = Fix-JsonFile -Path $Rcl; if($a1.rc -eq 0){ Write-Log "[FIX_JSON] 교정/검증 완료: $Rcl" } else { Write-Log "[FIX_JSON] 실패: $($a1|ConvertTo-Json -Compress)" ; $a1.rc=1; $a1.fix="json_eof" }
  foreach($p in @($SelfH,$Reflex,(Split-Path $Bus),$LogDir)){ if(!(Test-Path $p)){ New-Item $p -ItemType Directory -Force | Out-Null } }
  $a2 = @{fix="recreate_paths"; rc=0}
  $a3 = Restart-Reflex

  $res = @{ ok=$true; actions=@(
    @{fix="json_eof"; rc=$a1.rc},
    $a2,
    @{fix="restart_reflex"; rc=$a3.rc}
  )}
  Write-Log ("[INFO] Self-Heal 완료: " + ($res|ConvertTo-Json -Compress))
  Post-Bus -topic "SelfHeal/Result" -payload $res
  $g.last_sig = $sig; $g.last_at = $now.ToString("o"); Save-State $g
  return $res
 = 
  Rotate-Log -Path $Log -MaxBytes 5MB -Keep 7
  Write-Log "[INFO] Self-Heal 시작"
  $now = Get-Date
  $sig = "json_eof|recreate_paths|restart_reflex"

  if($g.last_sig -eq $sig -and $g.last_at){
    $lastAt = Get-Date $g.last_at
    if(($now - $lastAt).TotalSeconds -lt $DEDUPE_SECONDS){
      Write-Log "[DEDUP] $DEDUPE_SECONDS 초 이내 동일 시나리오 억제"
      Post-Bus -topic "SelfHeal/Result" -payload @{ ok=$true; dedup=$true; actions=@(@{fix="dedup_suppress"; rc=0}) }
      return @{ok=$true; dedup=$true}
    }
  }

  $a1 = Fix-JsonFile -Path $Rcl; if($a1.rc -eq 0){ Write-Log "[FIX_JSON] 교정/검증 완료: $Rcl" } else { Write-Log "[FIX_JSON] 실패: $($a1|ConvertTo-Json -Compress)" ; $a1.rc=1; $a1.fix="json_eof" }
  foreach($p in @($SelfH,$Reflex,(Split-Path $Bus),$LogDir)){ if(!(Test-Path $p)){ New-Item $p -ItemType Directory -Force | Out-Null } }
  $a2 = @{fix="recreate_paths"; rc=0}
  $a3 = Restart-Reflex

  $res = @{ ok=$true; actions=@(
    @{fix="json_eof"; rc=$a1.rc},
    $a2,
    @{fix="restart_reflex"; rc=$a3.rc}
  )}
  Write-Log ("[INFO] Self-Heal 완료: " + ($res|ConvertTo-Json -Compress))
  Post-Bus -topic "SelfHeal/Result" -payload $res
  $g.last_sig = $sig; $g.last_at = $now.ToString("o"); Save-State $g
  return $res

Invoke-SelfHeal | Out-Null
) | Out-Null }
  } catch {
    Write-Host "[pre-commit] Syntax check failed: "
    Write-Host \.Exception.Message
    \False = \False
  }
}
if (-not \False) {
  Write-Host "[pre-commit] WARNING: syntax issues detected (허용 모드)"
}
exit 0