# Glossary

## Words and abbreviations

| Term | Meaning |
|---|---|
| ASMR | Ackermann-steered mobile robot: a small car-like robot with front-wheel steering. It cannot turn on the spot. |
| Ackermann steering | the steering of a car: the front wheels turn, so the robot drives on arcs |
| Tier 1, Tier 2 | the two benchmark floors: Tier 1 is an open floor, Tier 2 a walled ward |
| Episode | one trip from a start to a goal, at most 100 s |
| Seed | a number that fixes the random choices, so a run or an episode can be repeated |
| SAC, TD3, PPO | three reinforcement learning algorithms (soft actor-critic, twin delayed deep deterministic policy gradient, proximal policy optimisation) |
| CARS | culture-aware reward shaping: the reward with four parts (progress, safety, culture, urgency) |
| CWN | context weight network: a small network that sets the four reward weights from the situation |
| SF | social force: a classical controller that is pulled to the goal and pushed away from people and walls |
| ORCA | optimal reciprocal collision avoidance: a classical controller that avoids each person's predicted path |
| Pure pursuit | a controller that steers toward a point on the path ahead |
| Residual driver | a learned network that adds a correction to the tuned social-force controller |
| Mapless | without the route planner: the driver only knows where the final goal is |
| Route planner | finds the cheapest route on the map; cultural zones cost extra |
| kappa | how much the planner charges for cultural zones: 3 = cultural planner, 0 = geometric (shortest path) |
| lambda | the cultural price of one metre in a zone (0.83 prayer room in prayer time, 0.25 at other times, 0.042 gendered ward) |
| Waypoint | the point on the route, up to 2.5 m ahead, that the driver steers to |
| Swept-path filter | the paper's safety filter: checks the arc the robot will drive and slows down before anything on it |
| Cone filter | the baseline filter: checks a fixed cone in front of the robot |
| Price and veto | cultural rules get a price (they can be traded), contact gets a veto (it cannot) |
| SR | success rate |
| CVR | cultural violation rate: share of steps in a cultural zone or near a family attendant |
| CVR_STAT | CVR on the urgent STAT task, whose goal is outside every zone |
| SVR | social violation rate: share of steps with a person closer than 0.8 m |
| SPL | success weighted by path length |
| STAT | "immediately" in hospital language; the most urgent task |
| Gazebo | a 3D physics simulator for robots, used with ROS 2 |
| ROS 2 | Robot Operating System 2, the software framework that runs on the real robot |

## Names in code and file names

| Code id | Paper name |
|---|---|
| `fixed_equal` | SAC-CARS (equal weights) |
| `nav_heavy` | SAC-CARS-nav |
| `safe_heavy` | SAC-CARS-safe |
| `cwn` | SAC-CWN |
| `attention` | SAC-Attn |
| `vanilla` | SAC-blind |
| `he2025`, `risk_field` | SAC-risk |
| `residual_sf` | Residual |
| `td3_equal` | TD3-CARS |
| `ppo_equal` | PPO-CARS |
| `planner_sf2`, `classical_sf2` | Tuned SF on the route planner |
| `planner_sf` | Stock SF on the route planner |
| `planner_pp` | Pure pursuit on the route planner |
| `planner_orca` | ORCA on the route planner |
| `astar_pp` | A* + pure pursuit (its own path) |
| `sf`, `sf2` | stock and tuned SF without the planner |
| `cult`, `geo` | cultural planner (kappa = 3), geometric planner (kappa = 0) |
| `shield`, `v1` | cone filter |
| `shield2`, `v2` | swept-path filter |
| `final` | the model at the end of training, tested without a filter |
| `mid` | the model at 1 million steps |
| `pivot` | the chassis that turns on the spot (kinematics ablation) |
| `tier2_mapless`, `tier2_planner_ablation`, ... | campaign groups (see guide 4) |
