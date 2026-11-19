# Training

**Start with `train.py`:**

```bash
python training/train.py --driver sac_cars --tier 2 --seed 0
```

| File | What it does |
|---|---|
| `train.py` | train one driver by its paper name with the paper's recipe (prints the exact command) |
| `drivers.py` | the table of drivers: paper name, agent id, trainer, planner, settings |
| `patches.py` | applies the paper's settings (planner, residual driver, reward normalisation off, ...) to a trainer in memory, then runs it |
| `train_sac.py` | the SAC trainer (all SAC drivers) |
| `train_td3.py` | the TD3 trainer (TD3-CARS) |
| `train_ppo.py` | the PPO trainer (PPO-CARS) |
| `pivot_chassis.py` | the chassis that turns on the spot, for the kinematics ablation |
| `callbacks.py` | checkpoints, evaluations during training, logging |

See [docs/04_training.md](../docs/04_training.md).
