# The navigation stack (the method of the paper)

| File | Part | What it does |
|---|---|---|
| `route_planner.py` | planner (price) | Dijkstra cost-to-go on the floor grid, with cultural prices `1 + kappa * lambda` |
| `planner_patch.py` | planner | connects the planner to the environment: waypoint 2.5 m ahead and the remaining route length go into the observation |
| `swept_filter.py` | filter (veto) | the swept-path safety filter: caps the speed by the free distance along the commanded arc |
| `sf_prior.py` | driver | the tuned social-force controller for a car-like robot |
| `residual.py` | driver | the residual driver: tuned SF plus 0.5 times a learned correction |

See [docs/03_navigation_stack.md](../docs/03_navigation_stack.md) for how the parts work
together, with code examples. The same planner and filter run on the robot: see
`ros2/hospitalnav_deploy/hospitalnav_deploy/route_planner.py` and `scan_utils.py`.
