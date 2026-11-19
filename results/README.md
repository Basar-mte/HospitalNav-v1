# The paper's results

Everything the 96 training runs produced, except the networks and replay buffers (too large;
the best seed of every driver is in `ros2/models/`). These files are the source of every
benchmark number in the paper. Do not edit them; your own runs go to `runs/`.

## Layout

```
summary/<group>/table.json        mean (and SD) over seeds per driver, for each test setting
summary/<group>/per_seed.json     the same, per seed
summary/<group>/per_task.json     success rate and CVR per task
summary/<group>/classical/        classical drivers: <driver>[_shield|_shield2].json
summary/tier2/robustness/         robustness tests: <condition>__<driver>[_shield2].json
summary/tier2/...                 extra Tier-2 studies (collision anatomy, speed caps, filter versions)
<group>/<agent>_s<seed>/          per-episode records of one run:
    eval_final.json                 final model, no filter
    eval_shield.json                final model, cone filter
    eval_shield2.json               final model, swept-path filter
provenance/                       code version (git.txt), file hashes (sha256.txt), library versions
                                  (versions.txt, pip_freeze.txt) and a copy of the code that ran (snapshot/)
```

Test settings in `table.json`: `final` = no filter, `shield` = cone filter, `shield2` = swept
filter, `mid` = the model at 1 million steps, `best` = the best training checkpoint (reported
for completeness only; the paper always uses `final`).

## One episode record

| Field | Meaning |
|---|---|
| `task_id` | `STAT_medicine`, `nurse_call`, `specimen`, `restock` or `idle_return` |
| `success` | reached the goal |
| `end` | `success`, `collision` or `timeout` |
| `steps` | length in steps of 0.1 s |
| `cvr`, `svr` | cultural and social violation rate of the episode |
| `spl` | success weighted by path length |
| `mpd` | closest distance to any person (m) |

Episode `k` of every file used seed `1000 + k` and task `k mod 5`, so files can be compared
episode by episode.

## Notes

* `provenance/` was recorded when the campaign ran, before the code was reorganised. Its file
  paths are the old ones (`experiments/planner/arc_shield.py` is now `navstack/swept_filter.py`,
  `scripts/campaign_v5_stable.py` is now `campaign/run_campaign.py`, and so on), and the folder
  was then called `runs_v5/`. Since then only file names, paths, comments and helper scripts
  have changed: replaying campaign checkpoints through the current code gives the same episode
  records as these files.
* `summary/tier2/classical/planner_sf2_tuned_shield2.json` was made with the first version of
  the swept filter, whose margins were later changed. `planner_sf2_tunedb_shield2.json` repeats
  `planner_sf2_shield2.json`. Neither is counted in the paper.
