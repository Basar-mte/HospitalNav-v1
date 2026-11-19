# Planner screen

The evaluation-only test that fixed the route planner's settings before the main campaign.
Policies trained **without** a planner (six pilot policies) were tested with each planner
variant switched on at test time, 200 episodes each, on the protocol episode seeds, with the
cone filter.

| Variant id | What changes |
|---|---|
| `noplan_shield` | no planner |
| `geo_shield` | geometric planner (kappa = 0) |
| `cult_shield`, `cult` | cultural planner (kappa = 1), with and without the cone filter |
| `cult3_shield` | cultural planner with kappa = 3 (the setting chosen for the campaign) |
| `cult_L1.5_shield`, `cult_L4_shield` | look-ahead 1.5 m or 4 m instead of 2.5 m |
| `cult_geodist_shield` | distance input = remaining route length |
| `cult_nolos_shield` | no line-of-sight pull-back of the waypoint |

* `results/`: the paper's results, one file per policy and variant
  (`<policy>__<variant>.json`), and the run log.
* `summarize.py`: prints the results as tables. `python ablations/planner_screen/summarize.py`
* `run_planner_screen.py`: runs the screen again. It needs policies trained without a planner:

```bash
HOSPITALNAV_PILOT_RUNS=runs/tier2_mapless python ablations/planner_screen/run_planner_screen.py --phase all
```

Because the screen used the same episode seeds as the later evaluation, the chosen settings
are not fully independent of the test data. The paper and its supplement discuss this.
