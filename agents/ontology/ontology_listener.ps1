param([string]$BusFile = "D:\Endeavour_Dev\agents\reflex\bus\stream\bus_events.jsonl")
$Emit = "D:\Endeavour_Dev\agents\reflex\bus\emit_event.ps1"
if(-not (Test-Path $BusFile)){ return }
(Get-Content $BusFile -Tail 100) | ForEach-Object {
  try{
    $e = $_ | ConvertFrom-Json
    if($e.source -ne "reflex"){ return }
    $tag = switch ($e.topic) {
      "RCL/Recovery"      { "STATE:DEGRADED" }
      "RCL/EOF_FIX"       { "STATE:CONFIG_FIX" }
      "Health/Error"      { "STATE:ERROR" }
      "Context/Recommend" { "STATE:NORMAL" }
      default             { "STATE:NORMAL" }
    }
    & $Emit -Topic "Ontology/State" -Payload @{ tag=$tag; from=$e.topic } | Out-Null
  } catch {}
}
