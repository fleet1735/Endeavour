param([string]$Mode="run")
$ErrorActionPreference="Stop"
function Run-Engine { python ".\engine_core\parallel_backtest.py" }
function Run-Validator { python ".\validators\validator.py" }
if($Mode -eq "run"){ Run-Engine; Run-Validator }
elseif($Mode -eq "validate"){ Run-Validator }
else{ Write-Error "Unknown Mode: $Mode" }
