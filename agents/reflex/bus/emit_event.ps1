param([string]$Topic, [hashtable]$Payload)
$evt = @{
  ts=(Get-Date).ToString("o")
  topic=$Topic
  payload=$Payload
  source="reflex"
}
$json = $evt | ConvertTo-Json -Compress -Depth 10
& "D:\Endeavour_Dev\agents\reflex\bus\event_bus.ps1" -JsonLine $json
