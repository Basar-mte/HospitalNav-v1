# Watchdog for the campaign on Windows (scheduled task "HospitalNavWatchdog", every 5 minutes
# while you are logged in, registered by launch_windows.ps1). It starts campaign\run_campaign.py
# again if it is not running and runs\ALL_DONE does not exist yet. The orchestrator then
# resumes every unfinished run from its newest checkpoint.
$root = Split-Path $PSScriptRoot -Parent
$runs = Join-Path $root "runs"
New-Item -ItemType Directory -Force $runs | Out-Null

if (Test-Path (Join-Path $runs "ALL_DONE")) { exit 0 }

$alive = Get-CimInstance Win32_Process -Filter "Name='python.exe'" |
    Where-Object { $_.CommandLine -like '*run_campaign.py*' }
if ($alive) { exit 0 }

$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = (Get-Command python).Source }

$ts = Get-Date -Format "yyyyMMdd_HHmmss"
Start-Process -FilePath $py `
    -ArgumentList "campaign\run_campaign.py" `
    -WorkingDirectory $root -WindowStyle Hidden `
    -RedirectStandardOutput (Join-Path $runs "campaign_$ts.log") `
    -RedirectStandardError (Join-Path $runs "campaign_$ts.err")
Add-Content (Join-Path $runs "watchdog.log") "$(Get-Date -Format 'yyyy-MM-dd HH:mm:ss') orchestrator (re)started -> campaign_$ts.log"
