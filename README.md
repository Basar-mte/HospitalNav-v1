# HospitalNav-v1

**A benchmark and a navigation stack for service robots in crowded hospitals.**

Hospitals can get very crowded. Sometimes this is normal, when there are more patients than
beds. Sometimes it is sudden, during an emergency or a disaster. Patients then lie in
corridors and on the floor, family members stay beside them, and staff hurry through. A
service robot that carries medicine or samples in such a hospital must arrive on time, never
touch anyone, and respect places such as a prayer room or a ward for women only.

This repository has everything we used to study this problem, so that you can repeat it,
check it, or build on it:

* **The benchmark (HospitalNav-v1).** A [Gymnasium](https://gymnasium.farama.org/) environment
  with two hospital floors, up to 74 people of four kinds, five delivery tasks with deadlines,
  and a small car-like robot (an Ackermann-steered mobile robot, ASMR).
* **The navigation stack.** Three parts that work together. A *route planner* puts a price on
  culturally sensitive places. A *driver* (learned, classical, or both) moves through the
  crowd. A *safety filter* stops any command whose path would touch a person.
* **Everything behind the paper.** Training code, the 96 training runs and their per-episode
  results, ablations, robustness tests, trained models, a ROS 2 package with a Gazebo study
  (480 runs), and logs of nine trials on a real robot.

![The two hospital floors of the benchmark](docs/figures/fig_tiers.png)

---

## Results at a glance

All numbers are on Tier 2 (the walled ward) with 45 people, 500 test episodes per training
run. SR = success rate.

| What we tested | Result |
|---|---|
| Route planner on or off (SAC-CARS driver) | SR rises from 48.2 % to 80.4 % |
| Swept-path safety filter | No contact in 42,500 episodes of planner-guided drivers; 4 contacts in all 54,000 filtered episodes |
| Best driver (residual learning on top of a tuned social-force controller, with the filter) | SR 99.4 % |
| Cultural route planner instead of the shortest path | Cultural violation rate on the urgent (STAT) task falls from 0.080 to 0.002, with the same SR |
| Gazebo physics simulation (480 runs) | Robot went more than 1 m into the prayer room in 62 of 62 successful culture-blind runs, but in only 4 of 118 successful culture-aware runs |
| Real robot (9 trials, apartment set up as a small hospital) | Goal reached in 8 of 9 trials, 6 of them with no help |
| Crowd that does not step aside for the robot | Every driver loses 30 to 40 points of SR, with or without the filter |

The full tables are in [docs/07_reproduce_the_paper.md](docs/07_reproduce_the_paper.md).

---

## Quick start (about 10 minutes)

**1. Install** (Python 3.10 or newer; a GPU is not needed).

```bash
git clone https://github.com/Basar-mte/HospitalNav-v1.git
cd HospitalNav-v1
python -m venv .venv
source .venv/bin/activate          # on Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

**2. Check that everything works.**

```bash
pytest tests/
```

**3. Test a trained model** that ships with this repository (SAC-CARS, Tier 2, with the swept-path filter, 20 episodes).

```bash
python evaluation/evaluate_run.py --model ros2/models/fixed_equal_s2 --driver sac_cars --tier 2 --filter swept --episodes 20
```

**4. Train your own driver** (a short test run first, then the full run of the paper).

```bash
python training/train.py --driver sac_cars --tier 2 --seed 0 --steps 5000     # a few minutes
python training/train.py --driver sac_cars --tier 2 --seed 0                   # 2 million steps, about a day on one CPU core
python evaluation/evaluate_run.py --model runs/tier2/fixed_equal_s0 --driver sac_cars --tier 2 --filter all
```

**5. Rebuild the paper's tables** from the saved results (no training needed, takes seconds).

```bash
python paper/build_paper_tables.py
python paper/audit_paper_numbers.py
```

---

## Find what you need

| I want to ... | Read | Main code |
|---|---|---|
| install and check the setup | [docs/01_install.md](docs/01_install.md) | `tests/` |
| understand the benchmark (floors, people, robot, tasks, metrics) | [docs/02_benchmark.md](docs/02_benchmark.md) | `envs/`, `configs/` |
| understand the planner, drivers and safety filter | [docs/03_navigation_stack.md](docs/03_navigation_stack.md) | `navstack/`, `baselines/`, `rewards/` |
| train a driver, or the whole campaign | [docs/04_training.md](docs/04_training.md) | `training/`, `campaign/` |
| test a model | [docs/05_evaluation.md](docs/05_evaluation.md) | `evaluation/` |
| run the ablations and robustness tests | [docs/06_ablations.md](docs/06_ablations.md) | `ablations/` |
| rebuild every table and check every number of the paper | [docs/07_reproduce_the_paper.md](docs/07_reproduce_the_paper.md) | `paper/`, `results/` |
| run the stack in Gazebo with ROS 2 | [ros2/README.md](ros2/README.md) | `ros2/` |
| run the stack on a real robot | [real_robot/README.md](real_robot/README.md) | `ros2/`, `real_robot/` |
| look up a name or an abbreviation | [docs/glossary.md](docs/glossary.md) | |

## Repository layout

```
configs/       the two hospital floors (YAML), and floors with extra unmapped obstacles
envs/          the Gymnasium environment: floor plan, crowd model, robot, sensors, metrics
rewards/       the CARS reward (culture-aware reward shaping)
navstack/      the method: route planner, swept-path safety filter, residual driver
baselines/     comparison methods: classical controllers, ORCA, risk-field reward, cone filter
training/      train one driver (train.py) and the trainers it uses (SAC, TD3, PPO)
evaluation/    test one model (evaluate_run.py), a campaign group, or the classical drivers
ablations/     the planner screen and the robustness tests
campaign/      the script that ran all 96 training runs, with its monitoring tools
paper/         rebuild the paper's tables and check its numbers
results/       the paper's results: per-episode records of every run and the summary tables
ros2/          ROS 2 package, Gazebo worlds and plugins, the trained models, Gazebo data
real_robot/    how to deploy on a real robot, and the logs of the nine trials
tools/         small helpers: drive with the keyboard, check a floor plan, draw routes
docs/          guides (start here), figures, and the stakeholder survey
tests/         automatic checks (pytest)
archive/       earlier experiments and old scripts, kept for transparency, not needed
```

## Names used in the code

The code and the result files use short ids. The paper uses longer names.

| In the code | In the paper |
|---|---|
| `fixed_equal` | SAC-CARS |
| `nav_heavy`, `safe_heavy` | SAC-CARS-nav, SAC-CARS-safe |
| `cwn`, `attention` | SAC-CWN, SAC-Attn |
| `vanilla` | SAC-blind |
| `he2025` (also `risk_field`) | SAC-risk |
| `residual_sf` | Residual |
| `td3_equal`, `ppo_equal` | TD3-CARS, PPO-CARS |
| `planner_sf2` | Tuned SF (social force) |
| `shield` / `shield2` | cone filter / swept-path filter |
| `cult` / `geo` | cultural planner (kappa = 3) / geometric planner (kappa = 0) |
| `tier1` / `tier2` | Tier 1 open floor / Tier 2 walled ward |

More in [docs/glossary.md](docs/glossary.md).

## Limitations

* The benchmark uses one floor plan per tier, the medium crowd of 45 people in the main tests,
  and people who step aside for the robot. A crowd that does not step aside is a hard case for
  every driver (see the robustness tests).
* The safety filter is tested, not proven. It checks commands, not what the motors do.
* The planner settings (kappa = 3, look-ahead 2.5 m) were chosen with the same test episodes
  that are used for evaluation, on policies trained before the main campaign.
* The real-robot trials were single runs on one route, in an apartment set up as a small
  hospital, with a setup that changed between trials. They show that the stack can run on a
  robot. They do not give a success rate.
* The cultural rules (prayer room, separate wards for men and women, family attendants) are
  examples that we wrote. Hospital staff and other stakeholders have not yet checked them.
  They live in the floor-plan files and one price, so a hospital can change them or replace
  them with its own rules without retraining. See [docs/stakeholders/](docs/stakeholders/).

## Data that is not in this repository

Because of their size, these are not included and are available from the authors on request:
the checkpoints and replay buffers of the 96 training runs, the raw Gazebo run folders,
renders and videos (about 5 GB), and the per-run pedestrian logs of the Gazebo study.

## Citation

If you use this benchmark or the navigation stack, please cite the paper (see
[CITATION.cff](CITATION.cff)):

> Md. Abul Basar Roky, Md. Musfiqur Rahman, Md. Asif Sardar, Subrata K. Sarker, Bing Yan and
> Sajal K. Das. *A Hierarchical Price-and-Veto Framework for Culture-Aware Autonomous Navigation
> of Service Robots in Crowded Hospitals: Benchmarking and Experimental Validation.* Preprint, 2026.

## License

The code is released under the [MIT License](LICENSE). The hospital furniture and people models
in `ros2/hospitalnav_deploy/meshes/fuel/` come from the Open Robotics collection on Gazebo Fuel
(see `ATTRIBUTION.md` there). The robot vendor's CAD meshes used by the detailed robot model are
not included (see `ros2/hospitalnav_deploy/meshes/acker/README.md`).

## Contact

Md. Abul Basar Roky, Department of Mechatronics Engineering, Rajshahi University of Engineering
& Technology (m.a.basar.mte@gmail.com).
