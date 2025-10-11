param(
  [string]$File = "D:\Endeavour_Dev\data\rcl_fallback.json",
  [string]$Log  = "D:\Endeavour_Dev\agents\self_heal\self_heal.log"
)
$ErrorActionPreference = "Continue"
function W($m){ $ts=Get-Date -Format "yyyy-MM-dd HH:mm:ss"; Add-Content -Path $Log -Value "$ts [FIX_JSON] $m" }
function Remove-BOM([string]$s){ if($s.Length -ge 1 -and $s[0] -eq [char]0xFEFF){ return $s.Substring(1) } return $s }
function Remove-TrailingCommas([string]$s){
  $prev=$null;$cur=$s
  do { $prev=$cur; $cur=[regex]::Replace($cur, ',(\s*[}\]])', '$1') } while($cur -ne $prev)
  return $cur
}
function Find-BalancedEnd([string]$s){
  $stack=New-Object System.Collections.Stack; $inStr=$false; $esc=$false; $last=-1
  for($i=0;$i -lt $s.Length;$i++){
    $ch=$s[$i]
    if($inStr){ if($esc){$esc=$false;continue}; if($ch -eq '\'){$esc=$true;continue}; if($ch -eq '"'){$inStr=$false}; continue }
    if($ch -eq '"'){$inStr=$true;continue}
    if($ch -eq '{' -or $ch -eq '['){ $stack.Push($ch); continue }
    if($ch -eq '}' -or $ch -eq ']'){
      if($stack.Count -eq 0){ break }
      $top=$stack.Pop()
      if(($top -eq '{' -and $ch -ne '}') -or ($top -eq '[' -and $ch -ne ']')){ break }
      if($stack.Count -eq 0){ $last = $i+1 }
    }
  }
  return $last
}
function Show-Err([string]$s,[string]$err){
  $m=[regex]::Match($err,'line\s+(\d+),\s*position\s+(\d+)', 'IgnoreCase')
  if(-not $m.Success){ W "JSON 오류: $err"; return }
  $line=[int]$m.Groups[1].Value; $pos=[int]$m.Groups[2].Value
  $lines=$s -split "`r?`n"; $start=[Math]::Max(1,$line-2); $end=[Math]::Min($lines.Length,$line+2)
  W ("JSON 오류 지점 line={0}, pos={1}" -f $line,$pos)
  for($i=$start;$i -le $end;$i++){
    $prefix = if($i -eq $line){"-->"}else{"   "}
    W ("{0}{1,4}: {2}" -f $prefix,$i,$lines[$i-1])
  }
}
if (-not (Test-Path $File)) { W "대상 없음: $File"; exit 2 }
$raw = Get-Content $File -Raw
$raw = Remove-BOM $raw -replace "`r`n","`n" -replace "`r","`n"
$end = Find-BalancedEnd $raw
if($end -gt 0){ $raw = $raw.Substring(0,$end) }
$raw = Remove-TrailingCommas $raw
try { $null = $raw | ConvertFrom-Json } catch { Show-Err $raw $_.Exception.Message; exit 1 }
[IO.File]::WriteAllText($File, $raw, (New-Object Text.UTF8Encoding($false)))
W "교정/검증 완료: $File"; exit 0
