# Start (or restart) the full campaign on Windows, the way the paper's campaign ran:
#   1. record provenance (code hashes and library versions) in runs\provenance\
#   2. register a watchdog task that restarts the orchestrator every 5 minutes if it stopped
#   3. start the orchestrator in a hidden window (log in runs\campaign_<time>.log)
#
#   powershell -NoProfile -ExecutionPolicy Bypass -File campaign\launch_windows.ps1
#
# Safe to run again: the orchestrator skips finished runs and resumes the rest from checkpoints.
# On Linux or macOS, run  python campaign/run_campaign.py  instead (for example inside tmux).
$root = Split-Path $PSScriptRoot -Parent
$py = Join-Path $root ".venv\Scripts\python.exe"
if (-not (Test-Path $py)) { $py = "python" }

& $py (Join-Path $root "campaign\provenance.py")
if ($LASTEXITCODE -ne 0) { Write-Error "provenance failed"; exit 1 }

$wd = Join-Path $root "campaign\watchdog_windows.ps1"
schtasks /Create /SC MINUTE /MO 5 /TN HospitalNavWatchdog /TR "powershell.exe -NoProfile -ExecutionPolicy Bypass -WindowStyle Hidden -File $wd" /F
if ($LASTEXITCODE -ne 0) { Write-Error "could not register the watchdog task"; exit 1 }

& powershell -NoProfile -ExecutionPolicy Bypass -File $wd
Write-Host "Campaign started. Watch it with:  python campaign\dashboard.py --watch"
Write-Host "Stop it with:  schtasks /Delete /TN HospitalNavWatchdog /F  and then stop the python processes running run_campaign.py and train_*.py"
