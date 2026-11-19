# The campaign (all 96 training runs)

```bash
HOSPITALNAV_SMOKE=1 python campaign/run_campaign.py    # tiny version of every group, to check the setup
python campaign/run_campaign.py                        # the real campaign (days)
python campaign/dashboard.py --watch                   # progress, in a second terminal
```

| File | What it does |
|---|---|
| `run_campaign.py` | trains every run of the 10 groups, several at a time, resumes after a stop, and evaluates each finished group. Holds the group definitions and the training recipe. |
| `dashboard.py`, `dashboard_helpers.py` | live view of every run (steps, speed, success during training) |
| `thermal_guard.py` | Windows only: pauses runs if the CPU gets too hot |
| `provenance.py` | records the code version, file hashes and library versions |
| `launch_windows.ps1`, `watchdog_windows.ps1` | Windows: start the campaign in the background and restart it after a reboot |

Outputs go to `runs/` (set `HOSPITALNAV_RUNS` for another folder). See
[docs/04_training.md](../docs/04_training.md).
