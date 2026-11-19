# 4. Training

## Train one driver

```bash
python training/train.py --driver sac_cars --tier 2 --seed 0
```

That is all. The script prints the exact command it runs, which is the same command the
paper's campaign used, so a run made here is a run of the paper.

| Option | Values | Default |
|---|---|---|
| `--driver` | `sac_cars`, `sac_cars_nav`, `sac_cars_safe`, `sac_cwn`, `sac_attn`, `sac_blind`, `sac_risk`, `residual`, `td3_cars`, `ppo_cars` | (required) |
| `--tier` | `1` (open floor) or `2` (walled ward) | `2` |
| `--seed` | any whole number (the paper used 0 to 4) | `0` |
| `--planner` | `cultural` (kappa = 3), `geometric` (kappa = 0), `none` (no planner) | cultural, but geometric for `sac_blind` and `sac_risk` |
| `--steps` | training steps | 2,000,000 (1,000,000 with `--pivot`) |
| `--pivot` | a chassis that can turn on the spot (an ablation) | off |
| `--resume` | continue from the newest checkpoint after a stop | off |
| `--dry_run` | only print the command | off |

**Start with a short run** to check your setup: `--steps 5000` takes a few minutes.

**How long?** One full run (2 million steps) takes about a day on one CPU core. A GPU does not
help much for these small networks. You can run several seeds or drivers at the same time,
one per CPU core.

## What you get

```
runs/tier2/fixed_equal_s0/                  # runs/<group>/<agent id>_s<seed>/
    fixed_equal_seed0_<time>/
        final_model.zip                     # the trained network (Stable-Baselines3)
        vec_normalize.pkl                   # observation scaling, ALWAYS keep it with the model
        checkpoints/                        # every 100,000 steps (used by --resume)
        best_model/                         # best checkpoint on the training evaluations (not used in the paper)
        monitor.monitor.csv                 # one line per training episode
        ...                                 # TensorBoard logs
```

Watch training with `tensorboard --logdir runs/`. Then test the model:
[5. Evaluation](05_evaluation.md).

The paper always evaluates the **final** model, never the best checkpoint. Picking the best
checkpoint would move single seeds by -17.8 to +9.8 points.

## The training recipe

All learned drivers use Stable-Baselines3 with these settings (from `campaign/run_campaign.py`).

| Setting | Value |
|---|---|
| Network | two hidden layers of 256 units (ReLU), for policy and critics |
| SAC | learning rate 1e-4, discount 0.99, target smoothing 0.005, replay buffer 1,000,000, batch 256, 4 gradient steps every 4 environment steps, automatic entropy with target -2 |
| TD3 | the same as SAC where it applies, Gaussian exploration noise with a standard deviation of 0.1 times half the action range |
| PPO | the library defaults |
| Normalisation | observations by running mean and standard deviation, clipped at 10; rewards only for PPO |
| Environments | one per run, on the CPU, one thread |
| Length | 2 million steps (1 million for the pivot chassis) |

### How the settings are applied

The trainers are `training/train_sac.py`, `training/train_td3.py` and `training/train_ppo.py`.
They are never called directly. `training/patches.py` runs first: it reads a few environment
variables, adjusts the trainer in memory (for example it switches on the route planner or the
residual driver), and then starts the trainer. `training/train.py` sets these variables for
you; `training/drivers.py` holds the table of drivers and their settings, and
`tests/test_drivers.py` checks that this table gives exactly the campaign's commands.

| Variable | Meaning |
|---|---|
| `PLANNER_MODE` | `cult` or `geo`: switch on the route planner (unset = no planner) |
| `PLANNER_RATIO`, `PLANNER_L`, `PLANNER_LOS`, `PLANNER_DIST`, `PLANNER_PROGRESS` | kappa (3.0), look-ahead (2.5 m), line-of-sight pull-back (1), distance input (`geo` = route length), progress along the route in training (1) |
| `PILOT_NORM_REWARD` | `0` = reward normalisation off (SAC, TD3) |
| `PILOT_AGENT` | `safe_heavy` or `residual_sf`: the two extra drivers |
| `PILOT_PIVOT` | `1` = the chassis that turns on the spot |
| `PILOT_ALGO` | `td3` or `ppo`: load these checkpoints in evaluation |

## Run the whole campaign (96 runs)

The paper's results come from one campaign of 96 runs in 10 groups:

| Group | Drivers x seeds | What it tests |
|---|---|---|
| `tier2`, `tier1` | 6 SAC reward designs x 5 seeds, each tier | main results |
| `tier2_mapless` | SAC-CARS and SAC-blind x 5, no planner | what the planner adds |
| `tier1_mapless` | SAC-CARS x 3, no planner | the same on Tier 1 |
| `tier2_planner_ablation` | SAC-CARS with the geometric planner, SAC-blind with the cultural planner, x 3 | does the reward or the planner decide compliance? |
| `tier2_residual`, `tier2_safe`, `tier2_td3` | Residual, SAC-CARS-safe, TD3-CARS x 3 | other drivers |
| `tier2_ppo` | PPO-CARS x 5 | another algorithm |
| `tier2_pivot` | SAC-CARS x 3, chassis that turns on the spot, 1 million steps | the cost of car-like steering |

```bash
HOSPITALNAV_SMOKE=1 python campaign/run_campaign.py   # first: a tiny version of every group (about 15 minutes)
python campaign/run_campaign.py                       # then: the real campaign
python campaign/dashboard.py --watch                  # in a second terminal: progress of every run
```

* It trains several runs at the same time (2/3 of your CPU threads, at most 16; set
  `HOSPITALNAV_MAX_RUNS` to change it). The paper's campaign took 128.8 hours on a 24-thread
  desktop.
* It is safe to stop and start again: finished runs are skipped and the others continue from
  their newest checkpoint.
* When all runs of a group are done, it evaluates the group (guide 5) and writes the tables to
  `runs/summary/<group>/`.
* On Windows, `campaign\launch_windows.ps1` also records the code version
  (`campaign/provenance.py`) and registers a watchdog that restarts the campaign after a reboot.
  On Linux, run it inside `tmux` or `screen`.

Next: [5. Evaluation](05_evaluation.md)
