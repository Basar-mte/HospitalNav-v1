# 6. Ablations and robustness

An ablation changes **one part** of the full stack and measures what that part was worth. A
robustness test **breaks one assumption** on purpose and measures what happens.

## One change at a time (Table "Ablation on Tier 2" in the paper)

The full stack is SAC-CARS with the cultural planner (kappa = 3) and the swept filter. Each row
below is one training command (guide 4) and one evaluation command (guide 5). All on Tier 2,
seeds 0 to 4 (or 0 to 2 where the paper used three seeds).

| Change | Train | Test with |
|---|---|---|
| none (full stack) | `--driver sac_cars` | `--filter swept` |
| no planner | `--driver sac_cars --planner none` | `--filter swept --planner none` |
| no filter | (same model as the full stack) | `--filter none` |
| cone filter instead of swept | (same model) | `--filter cone` |
| geometric planner (kappa = 0) | `--driver sac_cars --planner geometric` | `--filter swept --planner geometric` |
| culture-blind reward | `--driver sac_blind --planner cultural` | `--filter swept --planner cultural` |
| both culture-blind | `--driver sac_blind` | `--filter swept` |
| risk-field reward | `--driver sac_risk` | `--filter swept` |
| navigation-heavy / safety-heavy weights | `--driver sac_cars_nav` / `sac_cars_safe` | `--filter swept` |
| learned weights (CWN / attention) | `--driver sac_cwn` / `sac_attn` | `--filter swept` |
| tuned SF driver (no learning) | nothing to train | `python evaluation/eval_classical.py tier2 planner_sf2 --shield_v2` |
| residual driver | `--driver residual` | `--filter swept` |
| chassis that turns on the spot | `--driver sac_cars --pivot` | `--filter swept --pivot` |

The campaign (guide 4) trains all of these in its groups, so `python campaign/run_campaign.py`
gives the whole table.

## Planner screen: `ablations/planner_screen/`

This is the test that fixed the planner settings **before** the main campaign: kappa (1 or 3),
the look-ahead (1.5, 2.5 or 4 m), the line-of-sight pull-back, and the distance input. It
switches the planner on at test time for policies that were trained **without** a planner, so it
needs no training of its own. The paper used six pilot policies, which are not shipped (too
large). To repeat it with your own mapless runs:

```bash
HOSPITALNAV_PILOT_RUNS=runs/tier2_mapless python ablations/planner_screen/run_planner_screen.py --phase all
python ablations/planner_screen/summarize.py
```

The paper's results of this screen are in `ablations/planner_screen/results/`
(`summarize.py` prints them as tables).

## Robustness tests: `ablations/robustness/`

Each test breaks one assumption of the stack, on Tier 2, for three drivers (SAC-CARS seed 1,
SAC-blind seed 0, tuned SF), each without a filter and with the swept filter.

| Test | Broken assumption | How |
|---|---|---|
| unmapped obstacles (A1) | the map is correct | 6 boxes the planner cannot see, 10 layouts in `configs/unmapped_obstacles/` (made by `gen_unmapped.py`) |
| actuation noise (A2) | the wheels do what the filter allows | 10 % noise added to the command after the filter |
| non-yielding crowd (A3) | people step aside for the robot | people ignore the robot |
| LiDAR noise (A4) | the sensor sees everything | 5 % range noise and 2 % of rays dropped |

```bash
python training/train.py --driver sac_cars --tier 2 --seed 1     # the two learned drivers it needs
python training/train.py --driver sac_blind --tier 2 --seed 0
python ablations/robustness/run_robustness.py
HOSPITALNAV_RESULTS=runs python ablations/robustness/summarize.py
```

Without `HOSPITALNAV_RESULTS=runs`, `summarize.py` prints the paper's own results from `results/`.

How the conditions are injected: `ablations/robustness/uncertainty.py` (environment variables
`UNC_PED_NOYIELD`, `UNC_LIDAR`, `UNC_LIDAR_DROP`, `UNC_ACT`). The same variables work with
`evaluation/eval_planner.py` and `evaluation/eval_classical.py`, so you can test any model
under any condition.

Next: [7. Reproduce the paper](07_reproduce_the_paper.md)
