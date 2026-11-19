# 5. Evaluation

## Test one model

```bash
python evaluation/evaluate_run.py --model runs/tier2/fixed_equal_s0 --driver sac_cars --tier 2 --filter all
```

| Option | Meaning |
|---|---|
| `--model` | the run folder from `training/train.py`, or any folder with `final_model.zip` and `vec_normalize.pkl` |
| `--driver`, `--tier`, `--planner`, `--pivot` | the same values the model was trained with (a model must be tested with the planner it was trained with) |
| `--filter` | `none` (the driver's own commands), `cone` (the cone filter), `swept` (the swept-path filter of the paper), or `all` (all three) |
| `--episodes` | number of test episodes (the paper used 500) |
| `--out` | folder for the result files (default: the model folder) |

It prints a summary like this and writes `eval_<filter>.json` with one record per episode:

```
filter    SR %  coll %  tout %    CVR    SVR   SPL  t_goal s
swept     95.0     0.0     5.0  0.124  0.015  0.95      27.4
```

## The test protocol (same as the paper)

* Episode `k` uses random seed `1000 + k` and task number `k mod 5`, with the medium crowd of
  45 people. So episode 7 is the same situation for every driver and every filter, and the
  results can be compared episode by episode (the paper uses paired tests for this).
* Actions are deterministic (no exploration noise).
* The filters are used only in testing, never in training.
* One episode takes about 1 to 2 seconds, so 500 episodes take about 10 to 15 minutes for each
  filter setting.

Because the first episodes are the same, 50 episodes of a model give exactly the first 50
records of the paper's 500 for the same model.

## Test a model that ships with this repository

`ros2/models/` holds the best seed of every trained driver (19 models). Use these options:

| Folder in `ros2/models/` | Options |
|---|---|
| `fixed_equal_s2` | `--driver sac_cars --tier 2` |
| `nav_heavy_s4` | `--driver sac_cars_nav --tier 2` |
| `safe_heavy_s2` | `--driver sac_cars_safe --tier 2` |
| `cwn_s4` | `--driver sac_cwn --tier 2` |
| `attention_s4` | `--driver sac_attn --tier 2` |
| `vanilla_s3` | `--driver sac_blind --tier 2` |
| `risk_field_s0` | `--driver sac_risk --tier 2` |
| `residual_sf_s2` | `--driver residual --tier 2` |
| `td3_equal_s1` | `--driver td3_cars --tier 2` |
| `ppo_equal_s0` | `--driver ppo_cars --tier 2` |
| `mapless_fixed_equal_s3` | `--driver sac_cars --tier 2 --planner none` |
| `mapless_vanilla_s2` | `--driver sac_blind --tier 2 --planner none` |
| `t1_fixed_equal_s3`, `t1_nav_heavy_s4`, `t1_cwn_s2`, `t1_attention_s2` | `--driver sac_cars` (or `sac_cars_nav`, `sac_cwn`, `sac_attn`) `--tier 1` |
| `t1_vanilla_s2`, `t1_risk_field_s4` | `--driver sac_blind` (or `sac_risk`) `--tier 1` |
| `t1_mapless_fixed_equal_s0` | `--driver sac_cars --tier 1 --planner none` |

Example:

```bash
python evaluation/evaluate_run.py --model ros2/models/residual_sf_s2 --driver residual --tier 2 --filter swept --episodes 50
```

## Test the classical drivers (no training needed)

```bash
python evaluation/eval_classical.py tier2 planner_sf2 --shield_v2     # tuned social force + planner + swept filter
```

Controllers: `planner_sf2` (tuned SF), `planner_sf` (stock SF), `planner_pp` (pure pursuit),
`planner_orca` (ORCA), all on the route planner; `astar_pp` (its own A* path); `sf2` and `sf`
(no planner). Add `--shield` for the cone filter or `--shield_v2` for the swept filter. The
result goes to `runs/summary/<tier>/classical/`.

## Test a whole campaign group

After the campaign (guide 4) has trained every run of a group, it evaluates the group by
itself. You can also start it by hand:

```bash
python evaluation/eval_group.py tier2
```

For every run it writes `eval_final.json` (no filter), `eval_shield.json` (cone filter) and
`eval_shield2.json` (swept filter), and then the summary tables `table.json`, `per_task.json`
and `per_seed.json` in `runs/summary/<group>/`. This is exactly how `results/` was made.

## What is in a result record

Each episode record has: `task_id`, `success` (true or false), `end` (`success`, `collision`
or `timeout`), `steps` (0.1 s each), `cvr`, `svr`, `spl`, and `mpd` (closest distance to a
person, in metres).

Next: [6. Ablations and robustness](06_ablations.md)
