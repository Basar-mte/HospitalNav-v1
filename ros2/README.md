# ROS 2 package, Gazebo study and trained models

This folder runs the HospitalNav-v1 stack (route planner, driver, swept-path filter) in ROS 2:
in the Gazebo physics simulator, and on a real car-like robot.

| Folder | What it is |
|---|---|
| `hospitalnav_deploy/` | the ROS 2 package: route planner, controller (all drivers, built-in swept filter), LiDAR people tracker, loggers, launch files, worlds, robot models |
| `hospitalnav_gz_plugins/` | Gazebo (gz-sim) plugins: walking people with bodies, and replay for videos |
| `models/` | the best seed of every trained driver (19 models), each with its own `vec_normalize.pkl` |
| `sim/` | scripts that build the worlds and run, analyse and export the 480-run Gazebo study |
| `paper_data/` | all numbers of the Gazebo study as CSV (see `paper_data/DATA_README.md`) |
| `results_summary/` | reports of the Gazebo campaigns and the benchmark tables of the shipped models |
| `MANIFEST.json` | file hashes and benchmark scores of the shipped models |

Not included because of size (about 5 GB, available from the authors): the raw Gazebo run
folders, renders and videos (`results_runs*/`, `results_figures/`, `paper_figures/`). The
robot vendor's CAD meshes are not included either (see `hospitalnav_deploy/meshes/acker/README.md`);
the simplified robot model `urdf/hospitalnav_robot.urdf` needs no extra files.

## What you need

* Ubuntu 24.04 with **ROS 2 Jazzy** and **Gazebo Harmonic** (gz-sim), as in the paper.
  (Ubuntu 22.04 with ROS 2 Humble and Gazebo Classic also works for the quick demo below.)
* The Python packages of the main repository in the same Python that ROS uses
  (`pip install stable-baselines3 torch gymnasium numpy pyyaml`).

## Build

```bash
mkdir -p ~/hn_ws/src
cp -r ros2/hospitalnav_deploy ros2/hospitalnav_gz_plugins ~/hn_ws/src/
cd ~/hn_ws && colcon build --symlink-install && source install/setup.bash
export HOSPITALNAV_MODELS=/path/to/HospitalNav-v1/ros2/models     # where the trained models are
```

On ROS 2 Humble (Gazebo Classic), copy only `hospitalnav_deploy`: the plugins need Gazebo Harmonic.

## Run one Gazebo episode (the paper's setup)

```bash
# Residual driver, walled ward, 8 walking people, stall recovery on, with the Gazebo window and RViz
ros2 launch hospitalnav_deploy gz_bringup.launch.py preset:=residual_sf tier:=walled \
    peds:=busy escape_enabled:=true gui:=true rviz:=true
```

`preset:=` picks a model from `models/` and sets its driver, planner and algorithm. Presets:
`residual_sf`, `classical_sf2` (tuned social force, no model file), `fixed_equal`, `vanilla`,
`risk_field`, `mapless_fixed_equal`, `cwn`, `attention`, `nav_heavy`, and more in
`launch/gz_bringup.launch.py`. In RViz, check that `/rl_route` goes around the prayer room
before the robot starts.

## Quick demo with Gazebo Classic (ROS 2 Humble)

```bash
ros2 launch hospitalnav_deploy gazebo_full_bringup.launch.py \
    agent:=residual_sf cultural_ratio:=3.0 \
    model_zip:=$HOSPITALNAV_MODELS/residual_sf_s2/final_model.zip \
    vecnorm_pkl:=$HOSPITALNAV_MODELS/residual_sf_s2/vec_normalize.pkl

ros2 launch hospitalnav_deploy gazebo_full_bringup.launch.py agent:=classical_sf2 cultural_ratio:=3.0   # no model needed
```

## The trained models

Benchmark success rate on Tier 2 with the swept filter (from `results/`).

| Folder | Launch arguments | SR % | Note |
|---|---|---|---|
| `residual_sf_s2` | `agent:=residual_sf` | **99.4** | Residual (the best driver) |
| (no model) | `agent:=classical_sf2` | 97.8 | Tuned SF |
| `vanilla_s3` | `agent:=vanilla cultural_ratio:=0.0` | 96.1 | SAC-blind: takes the prayer-room shortcut |
| `fixed_equal_s2` | `agent:=fixed_equal` | 95.4 | SAC-CARS |
| `risk_field_s0` | `agent:=he2025 cultural_ratio:=0.0` | 95.7 | SAC-risk |
| `nav_heavy_s4` | `agent:=nav_heavy` | 95.2 | SAC-CARS-nav |
| `cwn_s4` | `agent:=cwn` | 94.8 | SAC-CWN |
| `attention_s4` | `agent:=attention` | 94.6 | SAC-Attn |
| `safe_heavy_s2` | `agent:=safe_heavy` | 94.6 | SAC-CARS-safe |
| `td3_equal_s1` | `agent:=fixed_equal algo:=td3` | 93.2 (this seed) | TD3-CARS |
| `ppo_equal_s0` | `agent:=fixed_equal algo:=ppo` | 0 | PPO-CARS: does not navigate (a negative result) |
| `mapless_fixed_equal_s3` | `agent:=fixed_equal` + `goal_publisher` | 63.4 (this seed) | no planner |
| `mapless_vanilla_s2` | `agent:=vanilla` + `goal_publisher` | 59.4 (this seed) | no planner, culture-blind |

* Models starting with `t1_` were trained on Tier 1 (the open floor). They use the same launch
  arguments as their Tier-2 namesakes. The Gazebo worlds are Tier-2 geometry, so treat Tier-1
  models as demonstrations.
* Mapless models must get the straight-line goal (`ros2 run hospitalnav_deploy goal_publisher`),
  not the planner's waypoint, because that is what they were trained with.
* **Always keep each model with its own `vec_normalize.pkl`.** A wrong normaliser silently ruins
  the driving.

## Key parameters

| Parameter | Default | Meaning |
|---|---|---|
| `agent` | | driver (see the table) |
| `algo` | `sac` | algorithm of the model file: `sac`, `td3` or `ppo` |
| `cultural_ratio` | 3.0 | kappa of the route planner; **0.0 for `vanilla` and `he2025`** (they were trained with the geometric planner) |
| `shield_version` | 2 | 2 = swept-path filter, 1 = cone filter |
| `residual_scale` | 0.5 | residual driver only; must match training |
| `lookahead` | 2.5 | waypoint distance in metres (trained value, do not change) |

## Repeat the 480-run Gazebo study

```bash
python3 sim/run_campaign.py --peds busy,crowd45 --seeds 1-10 --out results_runs_repeats   # about 13 hours
python3 sim/analyze_repeats.py      # success rates with Wilson intervals -> results_summary/gazebo_repeats.md
python3 sim/export_data.py          # all numbers -> paper_data/ (see paper_data/DATA_README.md)
python3 sim/plot_paths.py           # route figures
```

The study: 6 drivers x 2 wards x 8 or 45 walkers x stall recovery on or off x 10 pedestrian
seeds. Every run goes from the nurse desk to the emergency room with the clock in a prayer
time, and succeeds if the robot comes within 0.4 m of the goal in 300 s (simulated time).

## How the simulation is built

**Worlds** (`sim/gen_worlds.py`; the collision geometry is copied from the benchmark):

| `tier:=` | What it is | Same LiDAR view as the benchmark? |
|---|---|---|
| `walled` | Tier 2: all walls, beds, staff, doors and wall finishes | yes (`sim/verify_scan_invariance.py`: within 0.14 mm) |
| `open` | Tier 2 without its interior walls; rooms remain only as zones. (This is **not** Tier 1.) | yes (within 0.21 mm) |
| `real` | the same as `walled` (kept as an alias) | yes |
| `furnished` | `walled` plus 97 pieces of furniture that are not on the map | no, on purpose: a test with unmapped clutter |

**What the cameras and the LiDAR see.** Every visual item carries flags so that the cameras see
a realistic ward (door frames, open doors, occupied beds, staff), while the LiDAR sees exactly
the shapes the policies were trained on. The robot's LiDAR ignores camera-only items, and the
figure cameras ignore LiDAR-only shapes.

**People** (`peds:=none|light|busy|crowd45`): `light` = 4 and `busy` = 8 designed walkers
(nurse, doctor, visitor, patient with a cane) on loops through the corridor and rooms
(`hospitalnav_deploy/ped_routes.py`); `crowd45` adds 37 generated walkers
(`sim/gen_crowd_routes.py`). The robot's own LiDAR people tracker feeds the driver, as on a
real robot (`people_source:=lidar`; `gt` uses the true positions instead). The
`PedestrianBodies` plugin moves every walker:

* **Social force walking** (Helbing and Molnar, 1995): each walker follows its loop, keeps its
  own pace, and gives room to other people, the robot and the walls.
* **Bodies**: each walker is a 70 kg cylinder with a bounded push, so the robot cannot drive
  through a person and a person can shove the robot but not knock it over. A walker squeezed
  against the robot gives way (without this rule, a walker squeezing past a stopped robot rolled
  it over in 2 runs; those runs were archived). `ped_yield:=false` turns giving way off.
* **Different crowds per run**: `ped_seed:=N` starts every walker at a different point of its
  loop.
* **Logged truth**: the simulated walker positions are logged to `peds.csv` for every run. The
  proximity measures come from them: closest approach, close passes (centre distance below
  0.5 m), touches (below 0.35 m) and seconds within 1.2 m.

**Robot pose**: the wheel odometry of the Ackermann plugin drifts, so the stack uses the true
pose from Gazebo. Localisation is therefore perfect, by design, so a run measures navigation,
not localisation.

**Stall recovery** (`escape_enabled`): when the robot is stuck for 8 s, a counter-steered
reverse is sent directly to the wheels for 1.6 s, **bypassing the safety filter**, after one
check that 0.35 m behind the robot is clear. The benchmark has no such recovery, so the study
reports runs with and without it.

**Robot models**: `urdf/hospitalnav_robot.urdf` is the simple model with the training wheelbase.
`urdf/mentorpi_real.urdf` is the detailed model of the physical ASMR's chassis (wheelbase
0.137 m, LiDAR at 0.1535 m), built from the chassis vendor's description; its meshes are not
included. The command adapter (`gz_cmd_adapter.py`) converts the driver's steering angle into a
yaw rate with the **training** wheelbase (0.20 m), so the robot drives the arc the policy
intended (see `real_robot/DEPLOYMENT_GUIDE.md`).

## Report demonstrations honestly

Report Gazebo and real-robot runs per driver as "reached" or "not reached" (with the failure
mode), or "reached in N of M runs". Do not turn a few demonstration runs into a success rate
that looks comparable to the 500-episode benchmark.

## Known limits (measured in the benchmark)

* A crowd that does not step aside defeats every driver at this density. The filter cannot stop
  a person who walks into the robot.
* Unmapped obstacles cause no contact with the swept filter, but more timeouts.
* The no-contact result assumes the wheels do what they are told: 10 % actuation noise gives
  1.4 to 3.0 % contacts.

## Real robot

See [real_robot/README.md](../real_robot/README.md).
