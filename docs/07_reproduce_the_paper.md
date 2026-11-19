# 7. Reproduce the paper

You can check the paper at three depths. Start with the first; each one takes longer.

## Level 1: rebuild the tables and check the numbers (seconds)

Every per-episode result of the paper is in `results/`. Two scripts read them:

```bash
python paper/build_paper_tables.py      # writes the LaTeX tables to paper/output/
python paper/audit_paper_numbers.py     # checks the headline numbers of the text, prints OK or FAIL
```

`build_paper_tables.py` also compares every number it writes with the number printed in the
paper and lists them at the end.

| Table in the paper | File written | Built from |
|---|---|---|
| Ablation on Tier 2: one change at a time | `tab_ablation.tex` | `results/<group>/<run>/eval_*.json`, `results/summary/tier2/classical/` |
| Local drivers on Tier 2 under three filter settings | `tab_drivers.tex` | the same |
| Goals reached in the 480 Gazebo runs | `tab_gazebo.tex` | `ros2/paper_data/runs.csv` |
| The nine field trials | `tab_real.tex` | `real_robot/data/real_robot_trials.csv` |
| Supplement: SAC designs on both tiers | `tab_main.tex` | `results/` |
| Supplement: robustness tests | `tab_robust.tex` | `results/summary/tier2/robustness/` |

The other tables of the paper describe the setup (protocol, parameters, hypotheses) or other
papers' results, so they hold no data of ours.

## Level 2: re-run the evaluation of the shipped models (minutes to hours)

The best seed of every driver is in `ros2/models/`. Testing it with guide 5 gives exactly the
same episodes as the paper's records of that run. For example, the first 50 episodes:

```bash
python evaluation/evaluate_run.py --model ros2/models/residual_sf_s2 --driver residual --tier 2 --filter all --episodes 50
```

Compare `eval_swept.json` with `results/tier2_residual/residual_sf_s2/eval_shield2.json`: the
records are the same, episode by episode.

## Level 3: train everything again (days)

```bash
python campaign/run_campaign.py
HOSPITALNAV_RESULTS=runs python paper/build_paper_tables.py
HOSPITALNAV_RESULTS=runs python paper/audit_paper_numbers.py
```

Training on another computer will not give bit-identical networks (thread timing and library
versions change the floating-point numbers), but the averages over seeds should match the
paper within the spread between seeds. The paper's exact library versions are in
`results/provenance/`.

## What is in `results/`

```
results/
  summary/<group>/table.json        mean over seeds per driver and filter (final = no filter,
                                    shield = cone filter, shield2 = swept filter, mid = 1M steps, best)
  summary/<group>/per_seed.json     the same per seed
  summary/<group>/per_task.json     success and CVR per task
  summary/<group>/classical/        classical drivers (one file per driver and filter)
  summary/tier2/robustness/         the robustness tests
  <group>/<agent>_s<seed>/          per-episode records of one training run:
      eval_final.json                 no filter
      eval_shield.json                cone filter
      eval_shield2.json               swept filter
  provenance/                       the code version, file hashes and library versions of the campaign
```

See `results/README.md` for the details. The Gazebo study's data are in `ros2/paper_data/`
(see `DATA_README.md` there), and the real-robot logs are in `real_robot/data/`.

## Where each number comes from

* **Benchmark numbers**: `results/`, 500 test episodes per run on the same episode seeds.
* **Planner settings** (kappa = 3, look-ahead 2.5 m): `ablations/planner_screen/results/`.
* **Gazebo numbers**: `ros2/paper_data/runs.csv` (one row per run).
* **Real-robot numbers**: `real_robot/data/` (one row per trial and the 5 Hz logs).

The supplementary material of the paper explains how the parameters were chosen and how
independent each choice is from the test episodes.
