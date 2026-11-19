# Archive

You do **not** need anything in this folder to use HospitalNav-v1 or to reproduce the paper.

It keeps earlier work for transparency: pilot experiments that shaped the final design, older
scripts, an older ROS 2 stack, and an Isaac Sim test bed. The project had another name at the
time, and these files still use the old module names (for example `envs.lmic_hospital_env`) and
old paths, so most of them will not run without changes.

| Folder | What it was |
|---|---|
| `experiments/stability_pilot/` | pilot runs that found the stable training recipe (reward normalisation off) and trained the pilot policies used by the planner screen |
| `experiments/planner/` | notes of the route-planner experiment (now `navstack/` and `ablations/planner_screen/`) |
| `experiments/shield_weaning/`, `shield_experiment/` | earlier safety-filter studies |
| `experiments/simple_experiment/`, `density_experiment/`, `context_experiment/`, `prayer_experiment/`, `holonomic_experiment/` | earlier side studies (simpler floor, crowd density, context input, prayer-room design, a robot that turns on the spot) |
| `scripts/` | scripts of earlier campaigns and packaging |
| `eval/`, `train/` | evaluation and training helpers of earlier campaigns |
| `deploy/` | the earlier ROS 2 stack (replaced by `ros2/`) and the Isaac Sim test bed |
| `configs/` | an earlier version of the Tier-1 floor |
| `docs/` | the change log of the earlier simulation |

The full history of every file is also in the git history of this repository.
