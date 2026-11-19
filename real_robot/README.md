# Real robot

This folder explains how to run the HospitalNav-v1 stack on a real car-like robot, and holds
the logs of the nine feasibility trials of the paper.

| File | What it is |
|---|---|
| [`DEPLOYMENT_GUIDE.md`](DEPLOYMENT_GUIDE.md) | step by step: map the building, label the zones, localise, drive autonomously |
| `setup/setup_pi5.sh`, `setup/requirements-pi.txt` | install ROS 2, SLAM, Nav2 and the Python packages on the robot's computer |
| [`TEST_PROTOCOL.md`](TEST_PROTOCOL.md) | how to plan a small, safe test with people |
| `data/real_robot_trials.csv` | one row per trial |
| `data/real_robot_timeseries.csv` | the 5 Hz logs of all trials (pose, commands, filter output, route, battery) |
| `data/DATA_README.md` | what every column means |

The software that runs on the robot is the ROS 2 package in [`ros2/`](../ros2/README.md).

## The robot used in the paper

Our laboratory's in-house-built Ackermann-steered mobile robot (ASMR). We had no hospital
service robot, so this small robot stood in for one.

| Part | Value |
|---|---|
| Size | 0.31 m x 0.22 m, no payload |
| Steering | four wheels, Ackermann, wheelbase 0.137 m, steering +-30 degrees, two drive motors with encoders |
| Sensor | LD19 2-D LiDAR (360 degrees, 12 m) |
| Computer | Raspberry Pi 5, Ubuntu 24.04, ROS 2 Jazzy |
| Motor control | STM32-based motor control board |
| Speed cap in the trials | 0.45 m/s (the benchmark robot drives up to 0.8 m/s) |

## The nine trials (30 October 2026)

* The simulation-trained **residual driver** ran with **unchanged weights**, together with the
  route planner, a LiDAR people tracker and the swept-path filter. Localisation used AMCL
  (Nav2) on a SLAM map.
* The site was a 13.1 m x 7.0 m apartment with hospital roles given to its rooms (nurse
  station, prayer room, emergency room). The route ran 10.53 m from the nurse station to the
  emergency room, through a 0.75 to 0.80 m passage, with 2 to 11 people walking.
* The robot reached the goal in **8 of 9 trials**, 6 of them with no help (one hand push, one
  change of settings during a run, one failure).

Five robot-side additions were made one at a time, each after a failure that the benchmark
does not have:

| What went wrong | What we added |
|---|---|
| walls and door frames were tracked as people, so the robot froze | **wall filter**: drop LiDAR clusters that lie on mapped walls |
| the car-like robot got stuck in dead ends (it cannot turn on the spot) | **reversing escapes**, counter-steered, only with free space behind |
| slow creeping reset the stall timer; furniture was tracked as people | **stall fix**: test stalls on the sent speed; drop clusters that stay within 0.15 m for 1 s |
| the robot reached the narrow passage and turned back | **chassis-sized filter**: body 0.20 m against clutter, wider steering search |
| re-planning after a turn-around found no route | **fixed-route tracking**: plan once, follow with a 1.5 m look-ahead |

**Important.** The reversing escape sends its reverse command (0.40 m/s) straight to the base,
so the swept-path filter does **not** check it. Its only check is its own look at the space
behind the robot. The same holds for the stall recovery in Gazebo.

## What the trials do and do not show

They are single runs on one day and one route, and the setup changed between trials. No zone
map was loaded, and people were not tracked by an outside system. So they show that the stack
can run on a real robot. They give **no** success rate, no prayer-room result, and no contact
or distance measure.

## What is and is not in this repository

* Included: the ROS 2 package (route planner, controller with every driver and the swept-path
  filter, LiDAR people tracker, LD19 LiDAR driver, command bridge with a reversing escape,
  loggers, launch files), the trained models, the deployment guide, and the trial logs.
* Not included: the exact robot-side code of the five additions above as it ran in the trials.
  They are described here and in the paper, and the trial logs record their effect.
