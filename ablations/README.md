# Ablations and robustness tests

* `planner_screen/`: the evaluation-only test that fixed kappa = 3 and the 2.5 m look-ahead.
* `robustness/`: one broken assumption at a time (unmapped obstacles, actuation noise, a crowd
  that does not step aside, LiDAR noise).
  * `run_robustness.py` runs all tests.
  * `uncertainty.py` injects the conditions.
  * `gen_unmapped.py` made the unmapped-obstacle floors in `configs/unmapped_obstacles/`.
  * `summarize.py` prints the results.

The one-change-at-a-time ablations (no planner, no filter, other rewards, other drivers) are
ordinary training runs with other options. See [docs/06_ablations.md](../docs/06_ablations.md)
for every command.
