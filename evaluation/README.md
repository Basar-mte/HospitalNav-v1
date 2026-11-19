# Evaluation

**Start with `evaluate_run.py`:**

```bash
python evaluation/evaluate_run.py --model ros2/models/fixed_equal_s2 --driver sac_cars --tier 2 --filter all --episodes 50
```

| File | What it does |
|---|---|
| `evaluate_run.py` | test one model with the paper's protocol: no filter, cone filter, swept filter |
| `evaluate.py` | loads a model with its normaliser and runs the protocol episodes without a filter |
| `eval_group.py` | tests every run of a campaign group and writes the summary tables (used by the campaign) |
| `eval_classical.py` | tests the classical drivers (social force, tuned SF, ORCA, pure pursuit, A*) |
| `eval_planner.py` | switches the route planner on at test time (planner screen and robustness tests) |

See [docs/05_evaluation.md](../docs/05_evaluation.md).
