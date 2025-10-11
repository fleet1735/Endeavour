param([string]$JsonLine)
$path = "D:\Endeavour_Dev\agents\reflex\bus\stream\bus_events.jsonl"
Add-Content -Path $path -Value $JsonLine -Encoding UTF8
