# Deployment guide: run the stack on a real car-like robot

This guide takes you from a robot with a LiDAR to autonomous start-to-goal runs:
**drive by hand to build a map, label the zones, localise, then let the stack drive.**
It uses the ROS 2 package in `ros2/hospitalnav_deploy/`. Our robot (see `README.md`) is the
example, but any small Ackermann robot with a 2-D LiDAR and ROS 2 works the same way.

---

## 1. How the parts connect

The trained drivers are **hierarchical**: a route planner chooses the route on the map, the
driver handles people and doorways, and the swept-path filter checks every command. The robot
must be wired the way the drivers were trained.

```
/map (SLAM or map_server) ──┐
zone-label image (step 4) ──┼─► route_planner ─► /rl_goal: waypoint 2.5 m ahead (x, y), z = remaining route length
goal (/goal_pose or /nav_goal)┘                 └► /rl_route (the route, for RViz)

/scan + /odom + people_tracker + /rl_goal ─► controller (driver + swept filter) ─► /cmd_shielded
                                                                                    [speed, steering angle]
/cmd_shielded ─► command bridge (gz_cmd_adapter) ─► your base: [speed, yaw rate]
```

| | Planner-guided drivers (all shipped models except `mapless_*`) | Mapless drivers (`mapless_*`) |
|---|---|---|
| route chosen by | `route_planner` | the driver itself |
| `/rl_goal` holds | the waypoint 2.5 m along the route, `z` = remaining route length | the final goal |
| how to send the goal | to `/goal_pose` or `/nav_goal` (the planner reads it) | `goal_publisher` straight to `/rl_goal` |

Mixing these up (a final goal for a planner-guided driver, or a waypoint for a mapless one) is a
train/deploy mismatch and the robot will drive badly.

The controller builds the goal input exactly as in training:

```python
b    = atan2(wy - y, wx - x) - yaw            # bearing to the waypoint
dist = z if z > 0 else hypot(gx - x, gy - y)  # remaining route length
goal = [sin(b), cos(b), min(dist / 25.0, 1.0)]
```

The look-ahead (2.5 m), the line-of-sight pull-back and the cultural prices are trained values.
Do not change them without retraining.

The controller applies the **swept-path filter** to every command (`shield_version: 2`), with the
same geometry as `navstack/swept_filter.py` in the benchmark. It uses the minimum range of each
LiDAR sector, so nothing between two sampled rays is missed.

---

## 2. Check your robot against what the drivers expect

| What the drivers expect | Value |
|---|---|
| Observation | 48 LiDAR rays + 5 robot state + 20 people values + 3 goal values + 14 context values |
| Action | `[speed, steering angle]`, speed -0.3 to 0.8 m/s, steering -30 to +30 degrees |
| Wheelbase in training | 0.20 m (tightest turn radius 0.35 m) |
| Control rate | 10 Hz |

**Your robot must be able to turn at least as tightly as the trained robot** (radius 0.35 m or
less). Then every arc the driver asks for can be driven. Our robot (wheelbase 0.137 m, +-30
degrees) turns down to about 0.24 m, so no retraining was needed.

---

## 3. Translate the commands (the wheelbase rule)

The driver outputs a steering angle `delta`, which **means** an arc of curvature
`tan(delta) / 0.20` (the training wheelbase). Most robot bases take a yaw rate instead. The
bridge `gz_cmd_adapter` converts it with the **training** wheelbase:

```python
SIM_WHEELBASE = 0.20                      # the training wheelbase, NOT your robot's
omega = (v / SIM_WHEELBASE) * tan(delta)  # yaw rate sent to the base
```

The base then picks its own steering angle from `omega / v` with its own wheelbase, so the
robot drives exactly the arc the driver intended. For our robot:
`steering = atan(0.137 * tan(delta) / 0.20)`, so the driver's full 30 degrees become 21.6
degrees on the robot. **Using your robot's real wheelbase in the bridge would make every arc
too tight** (by 0.20 / 0.137 = 1.46 times for our robot).

Run the bridge on the robot and send its output to your base:

```bash
ros2 run hospitalnav_deploy gz_cmd_adapter --ros-args -r /cmd_vel:=<your base's command topic> \
    -p escape_enabled:=false
```

`escape_enabled:=true` adds the reversing escape for a stuck car-like robot. It reverses
**without** the safety filter, after checking only the space behind the robot. Use it only with
a person ready to stop the robot.

Two checks on the base side:

1. **Speed limits.** Some base drivers limit one of their input topics to low "teleoperation"
   speeds. Send to a topic without such a limit, or the driver's behaviour changes silently.
2. **One odometry source.** If your base already publishes `/odom` and the `odom -> base_link`
   transform, do not start a second publisher.

Scaling the speed down (for example to 0.45 m/s, as in our trials) keeps the geometry the
same, because the yaw rate scales with the speed.

---

## 4. Prepare the robot

```bash
bash real_robot/setup/setup_pi5.sh          # ROS 2 Jazzy, SLAM Toolbox, Nav2, Python packages
mkdir -p ~/hn_ws/src && cp -r ros2/hospitalnav_deploy ~/hn_ws/src/
cd ~/hn_ws && colcon build && source install/setup.bash
```

Check that the base and the LiDAR run: `ros2 topic hz /scan` (about 10 Hz) and
`ros2 topic echo /odom`. If your LiDAR has no ROS driver, the package has one for the LD19
(`lidar_node`, settings in `config/robot.yaml`).

Copy onto the robot a model folder from `ros2/models/` (for example `residual_sf_s2/`).
**Keep each `final_model.zip` with its own `vec_normalize.pkl`.** A wrong pair silently ruins
the driving.

---

## 5. Build the map (drive by hand)

```bash
ros2 launch slam_toolbox online_async_launch.py \
    slam_params_file:=$HOME/hn_ws/src/hospitalnav_deploy/config/slam_toolbox_params_jazzy.yaml
```

Drive the robot slowly by hand over the whole route:

* Cover every corridor the robot will use, in both directions.
* Pause at doorways so the scan matcher locks on.
* Come back to the start once, so the loop closes and the drift is corrected.
* Keep moving people away from the robot while mapping.

Save the map (`ros2 run nav2_map_server map_saver_cli -f ~/hn_ws/maps/site`) and look at the
`.pgm` image: **every doorway must be a clean gap**. A doorway that maps shut makes every run
fail there, and it looks like a driver failure when it is a mapping failure.

---

## 6. Label the zones

The planner and the driver's context input need to know where the prayer room and the gendered
wards are. They read a zone image registered to the map.

1. Make an 8-bit grey image with the same size as the map's `.pgm`, where each pixel's value is
   the zone number: 0 walkable, 1 corridor, 2 general ward 1, 3 general ward 2, 4 emergency
   room, 5 prayer room, 6 male ward, 7 female ward (the list `_ZONES` in
   `hospitalnav_deploy/perception.py`). The trained drivers know exactly these 8 zones. An easy
   way: open the `.pgm` in an image editor, paint each zone with its grey value, and save it as
   a PNG without colour conversion.
2. Point `semantic_png` to it in `config/robot.yaml` (both the `controller:` and the
   `route_planner:` section).
3. Set `semantic_res` and `semantic_origin` **exactly** to the resolution and origin in the
   map's `.yaml`, or every zone will be shifted.

Check it: put the robot in a labelled zone and confirm that the controller reports that zone.

---

## 7. Localise

```bash
ros2 launch nav2_bringup localization_launch.py map:=$HOME/hn_ws/maps/site.yaml \
    params_file:=$HOME/hn_ws/src/hospitalnav_deploy/config/nav2_hospitalnav.yaml
```

Set the start pose in RViz ("2D Pose Estimate"), drive a little and check that the scan sits
on the walls. Nav2 is used **only for localisation**; the route comes from `route_planner`.
This is a check only: stop it before step 8, which starts the same localisation itself.

---

## 8. Drive autonomously

```bash
ros2 launch hospitalnav_deploy hospitalnav_bringup.launch.py \
    map:=$HOME/hn_ws/maps/site.yaml \
    model_zip:=$HOME/models/residual_sf_s2/final_model.zip \
    vecnorm_pkl:=$HOME/models/residual_sf_s2/vec_normalize.pkl \
    agent:=residual_sf cultural_ratio:=3.0 \
    semantic_png:=$HOME/hn_ws/maps/site_zones.png semantic_res:=0.05
```

This starts localisation, the people tracker, the route planner and the controller. (It also
starts `rrc_bridge`, a bridge for one specific motor board; on other robots it stops at once
and can be ignored. Run `gz_cmd_adapter` from step 3 instead.) Use `cultural_ratio:=0.0` for
`vanilla` and `he2025` models. For a classical driver without a model, use `agent:=classical_sf2`.

Send a goal: click "2D Goal Pose" in RViz, or

```bash
ros2 run hospitalnav_deploy goal_publisher --ros-args -p topic:=/nav_goal -p goal_x:=<x> -p goal_y:=<y>
```

**Before the robot moves**, look at `/rl_route` in RViz. It must pass through doorways, and for a
cultural driver go around the prayer room. A route through a wall means the map or the zone
image is wrong, not the driver.

### Before the first run on the floor

* **Wheels off the ground first.** Check that a forward command drives forward and a positive
  steering command turns the expected way. A sign error is the most common fault.
* **Stop test.** Stop the controller during a command: the robot must stop, not coast.
* **Start slow.** Use a speed cap well below 0.8 m/s.
* **Keep an emergency stop in reach.**

---

## 9. Record and report

`csv_logger` writes time, commands, pose, goal and distance. Keep for every run: the model and
its seed, the start and goal, and the map.

Report each run as **reached** or **not reached** (with the failure mode), or "reached in N of
M runs". **Do not turn a few demonstration runs into a success rate**: they cannot be compared
with the 500-episode benchmark rates.

---

## 10. Common problems

| What you see | Likely cause | Fix |
|---|---|---|
| nothing moves | no bridge between `/cmd_shielded` and the base, or the base listens on another topic | run `gz_cmd_adapter` and remap `/cmd_vel` (step 3) |
| moves, but slow and turns too little | the base limits the topic you send to | send to an unlimited topic (step 3) |
| turns too sharply | the bridge uses the robot's wheelbase | keep `wheelbase` at 0.20 (step 3) |
| wanders, oscillates, ignores the goal | a planner-guided driver gets the goal without `z`, or a mapless driver gets the waypoint | send the goal to `/nav_goal` and run `route_planner` (step 1 table) |
| drives into a wall or a dead end | map and zone image do not line up, or unknown cells are treated as free | check `/rl_route`; fix step 6; keep `unknown_is_free: false` |
| ignores the prayer room | `semantic_png` missing, or wrong resolution or origin | redo step 6 |
| good in one place, bad in another | localisation drift | rebuild the map with a closed loop (step 5) |
| always stuck at one doorway | the doorway mapped as partly closed | look at the `.pgm`; map that area again |
| erratic from the first command | wrong `vec_normalize.pkl` for this model | copy the matching pair again |
| walls tracked as people, robot freezes in corridors | LiDAR clusters on walls are taken for legs | in our trials a wall filter fixed this (see `README.md`) |

---

## 11. What a successful deployment shows

Runs like these show that unchanged benchmark models, on a SLAM map of a new building, can drive
a real Ackermann robot from start to goal without retraining. They do not measure a transfer
rate, and they cannot be compared with the benchmark tables.
