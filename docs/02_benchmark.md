# 2. The benchmark (HospitalNav-v1)

HospitalNav-v1 is a [Gymnasium](https://gymnasium.farama.org/) environment. A small car-like
robot must carry out a delivery task on a crowded hospital floor. The code is in `envs/`, the
floors are in `configs/`.

![The two tiers](figures/fig_tiers.png)

## The two floors ("tiers")

Both floors are 40 m x 30 m, stored on a 0.1 m grid. They are representative layouts, not
surveyed plans of a real hospital.

| | Tier 1: open floor | Tier 2: walled ward |
|---|---|---|
| File | `configs/tier1_open_floor.yaml` | `configs/tier2_walled_ward.yaml` |
| Layout | open floor around two crossing corridors, walled male and female wards, beds in the corridors and mattresses on the floor | seven walled rooms off a 4 m corridor, doors 1.7 to 1.8 m wide, a prayer room with two doors |
| Hard part | crowd and corridor beds | for two tasks, the shortest route goes through the prayer room |

## The people

Four kinds of people walk with a social force model (they are pushed toward their goal and
away from walls and each other). The medium crowd, used in all main tests, has 45 people.

| Kind | Number (medium) | Speed (m/s) | Notes |
|---|---|---|---|
| Medical staff | 8 | 1.2 to 1.4 | walk fast and straight |
| Patients | 16 | 0.5 to 0.8 | slow, wander a little |
| Family attendants | 16 | 0.4 to 0.7 | move in groups of 2 to 4, stay near beds |
| Wheelchair users | 5 | 0.6 to 0.9 | wider, turn slowly |

Low and high crowds have 23 and 74 people. People step aside for the robot and never walk into
it, so every contact in the benchmark is caused by the robot. (The robustness tests in guide 6
remove this rule on purpose.)

## The robot

A simulated Ackermann-steered mobile robot (ASMR): four wheels, front-wheel steering, rear-wheel
drive, like a small car. **It cannot turn on the spot.**

* Body: a circle of radius 0.25 m. Wheelbase 0.20 m, so the tightest turn has a radius of 0.35 m.
* Action: `[speed, steering angle]`, speed from -0.3 to 0.8 m/s, steering from -30 to +30 degrees.
* One step is 0.1 s (10 control steps per second). An episode lasts at most 100 s.

## What the robot sees (observation)

A dictionary with 90 numbers:

| Key | Size | Content |
|---|---|---|
| `lidar` | 48 | distances of a 360-degree laser scanner (range 12 m), scaled to 0..1 |
| `robot_state` | 5 | position, heading and speed |
| `pedestrians` | 20 | relative position and velocity of the 5 nearest people within 5 m |
| `goal` | 3 | direction (sin, cos) and distance to the goal, or to the planner's waypoint |
| `context` | 14 | crowd density, task urgency, current zone, time of day |

## The five tasks

| Task id | Urgency | Deadline | Goal on Tier 2 |
|---|---|---|---|
| `STAT_medicine` | 1.0 | 45 s | emergency room |
| `nurse_call` | 0.9 | 60 s | female ward |
| `specimen` | 0.6 | 90 s | general ward 2 |
| `restock` | 0.3 | 180 s | male ward |
| `idle_return` | 0.1 | 300 s | nurse desk |

An episode ends with **success** (within 0.6 m of the goal, no contact), **collision** (the
robot's body touches a person or an obstacle) or **timeout** (100 s).

## The cultural rules

They are examples of rules a hospital may want a robot to respect. We wrote them; stakeholders
have not checked them yet (see `docs/stakeholders/`).

* **Prayer room.** Most sensitive during the five daily prayer times, less sensitive at other
  times. A ward clock runs 48 times faster than real time, so a prayer time can start or end
  during a trip.
* **Separate wards for men and women.** Entering is allowed when a task needs it, but costs a
  little.
* **Family attendants.** The robot should not pass closer than 0.6 m to them.

To change them for your own site, edit the floor-plan YAML: the `rooms` list (each room has a
`type` such as `prayer`, `male_ward`, `female_ward`) and `prayer_windows` (times in hours). The
planner's price for each zone comes from the reward (see guide 3), so no retraining is needed
to change the timetable or the zone map.

## How a test is scored (metrics)

| Metric | Meaning | Better |
|---|---|---|
| SR | success rate: share of episodes that reach the goal | higher |
| Collision, Timeout | share of episodes that end with a contact, or out of time | lower |
| CVR | cultural violation rate: share of time steps inside a prayer room or a gendered ward, or within 0.6 m of a family attendant | lower |
| CVR_STAT | CVR on the urgent STAT task only. Its goal is outside every zone, so all of it could be avoided | lower |
| SVR | social violation rate: share of time steps with any person closer than 0.8 m (centre to centre) | lower |
| SPL | success weighted by path length: 1 = shortest possible path every time | higher |
| Time to goal | mean seconds of the successful episodes | lower |

Some tasks must enter a gendered ward, so CVR cannot reach zero. CVR_STAT can.

## Use the environment in your own code

```python
import sys; sys.path.insert(0, ".")          # run from the repository folder
from envs.hospital_env import HospitalNavEnv, TASK_IDS

env = HospitalNavEnv(floorplan_path="configs/tier2_walled_ward.yaml", use_camera=False)
obs, info = env.reset(seed=1000, options={"task": "STAT_medicine", "density": "medium"})
done = False
while not done:
    action = env.action_space.sample()       # replace with your controller: [speed, steering]
    obs, reward, terminated, truncated, info = env.step(action)
    done = terminated or truncated
print(info["task_complete"], info["collision"], info["steps"])
```

`info` also holds `cultural_violations`, `social_violations`, `min_pedestrian_distance`,
`path_length_actual` and `path_length_optimal`, from which all metrics are computed.

## Design your own floor

* Tier 2 is generated from `tools/tier2_layout.py` by `python tools/gen_tier2_config.py`.
  Copy the layout, change rooms, doors and beds, and generate a new YAML.
* Check any floor with `python tools/validate_floorplan.py <your.yaml>`. It tests that every task
  can be reached and draws the floor.

Next: [3. The navigation stack](03_navigation_stack.md)
