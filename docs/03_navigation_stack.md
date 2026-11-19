# 3. The navigation stack

## The idea in one paragraph: price and veto

The robot has four duties: arrive on time, respect cultural places, keep a polite distance
from people, and never touch anyone. They are not alike.

* **Cultural places can be traded.** Two of the five tasks end inside a ward for women or men,
  so a strict ban would make them impossible. So each place gets a **price**: going through it
  costs extra, the robot may pay when a task needs it, and a hospital can read and change the
  price.
* **Touching a person cannot be traded.** So contact gets a **veto**: a filter blocks any command
  that would lead to it.

The floor plan, the zones and the prayer times are known before the trip, but people are only
seen during the trip. So each duty goes to the part of the system that has the information it
needs:

![The navigation stack](figures/fig_stack.png)

```
floor plan + zones + prayer times ──► 1. ROUTE PLANNER (prices) ──► waypoint 2.5 m ahead + route length
                                                                        │
LiDAR + nearby people ──────────────► 2. DRIVER (learned / classical) ◄──┘
                                              │ command [speed, steering]
                                              ▼
LiDAR + nearby people ──────────────► 3. SAFETY FILTER (veto) ──► command sent to the wheels
```

Every part runs 10 times per second.

## 1. Route planner: `navstack/route_planner.py`

* The floor is a grid of 0.1 m cells. Walls and beds are made thicker by the robot's radius, so
  a free cell is a place the robot's centre can be.
* Each cell has a cost per metre:
  `cost = 1 + kappa * lambda + 0.3 (only in a 0.2 m band along walls)`.
  `lambda` is the cultural price of the cell: about **0.83** in the prayer room during a prayer
  time, **0.25** in the prayer room at other times, **0.042** in a gendered ward, and 0
  elsewhere. These come straight from the CARS reward: the penalty per step inside the zone
  divided by the reward for one full-speed step of progress.
* `kappa` sets how much culture counts. **kappa = 3** is the cultural planner, **kappa = 0** the
  geometric (shortest-path) planner. Above about kappa = 1.3 the planner always avoids the
  prayer-room shortcut on Tier 2.
* Dijkstra's algorithm, run once from the goal, gives every cell its cost to the goal and its
  route length. A sweep takes about 0.13 s and is cached per goal and prayer state.
* At each step the planner gives the driver a **waypoint up to 2.5 m ahead** on the route (moved
  closer if a wall blocks the straight line to it) and the **remaining route length**.

`navstack/planner_patch.py` connects the planner to the environment: it replaces the goal in
the observation with the waypoint and, in training, measures progress along the route.

## 2. Drivers

| Driver | Where | Idea |
|---|---|---|
| SAC-CARS and the other learned drivers | `training/`, `rewards/` | a neural network trained with reinforcement learning (SAC, TD3 or PPO) and the CARS reward |
| Stock social force (SF) | `baselines/classical.py` | pulled to the waypoint, pushed away from people and walls |
| Tuned SF | `navstack/sf_prior.py` | SF with a speed rule that suits a car-like robot (never fully stops while turning) |
| ORCA | `baselines/orca.py` | picks a speed that avoids each person's predicted path |
| Pure pursuit, A* + pursuit | `evaluation/eval_classical.py`, `baselines/classical.py` | follow the path, ignore people |
| **Residual** | `navstack/residual.py` | a learned network corrects the tuned SF: `action = clip(SF action + 0.5 * network action)` |

**The CARS reward** (culture-aware reward shaping, `rewards/`) has four parts, each with a
weight: progress toward the goal, safety (distance to people, contact), culture (prayer room,
gendered wards, family attendants) and task urgency (lateness after the deadline). SAC-CARS
uses equal weights. The other learned drivers change the weights or replace the reward (see
the glossary).

## 3. Safety filters

Both filters only lower the speed or change the steering a little. They never speed up.

**Cone filter (baseline), `baselines/cone_filter.py`.** Looks at the nearest laser hit in a
fixed +-30 degree cone in front and caps the speed at `0.727 * (distance - 0.40)`. It brakes for
walls the robot is turning away from, and it does not see a person beside the robot.

**Swept-path filter (the paper's filter), `navstack/swept_filter.py`.**

1. Take the arc the robot would drive with the commanded steering angle.
2. Collect what could block it: every laser hit (band half-width 0.28 m) and each of the 5
   nearest people at their position now, in 0.3 s and in 0.6 s (band half-width 0.65 m).
3. Find the free distance along the arc before the first blocking point.
4. Cap the speed at `0.727 * (free distance - 0.15)`. Full speed needs at least 1.25 m free.
5. If the command had to be slowed, try steering 0.15 and 0.3 rad to each side, and keep the
   fastest (a switch must gain more than 0.05 m/s).

Reverse commands are checked the same way along the backward arc. The filter has no formal
guarantee: it assumes the motors do what they are told and that people do not walk into the
robot. Guide 6 breaks these assumptions on purpose.

## Use the parts in your own code

```python
from navstack.swept_filter import shield_action as swept_filter
from baselines.cone_filter import shield_action as cone_filter

# env is a HospitalNavEnv (see guide 2); action is [speed, steering] from any driver
safe_action = swept_filter(action, {"lidar": env._cast_lidar(),
                                    "pedestrians": env._ped_obs_vec(),
                                    "robot_state": env._robot_state_vec()})
```

```python
from envs.floorplan import load_floorplan
from navstack.route_planner import Planner

planner = Planner(load_floorplan("configs/tier2_walled_ward.yaml"), ratio=3.0)  # ratio = kappa
field = planner.field(goal_xy=(5.0, 7.5), tod_hour=12.5)                        # a prayer time
route = field.route_xy((18.5, 7.5))           # route from a start point, as (x, y) points
waypoint = field.waypoint((18.5, 7.5), lookahead=2.5)
```

Next: [4. Training](04_training.md)
