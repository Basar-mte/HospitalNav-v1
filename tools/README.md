# Small tools

| File | What it does |
|---|---|
| `play.py` | drive the robot yourself with the arrow keys (`python tools/play.py --density medium`) |
| `validate_floorplan.py` | checks a floor plan: every task reachable, prayer room reachable, spawns free; draws the floor |
| `plot_routes.py` | draws the planner's route for every task, geometric and cultural, in and out of a prayer time |
| `gen_tier2_config.py` | writes `configs/tier2_walled_ward.yaml` from `tier2_layout.py` |
| `tier2_layout.py` | the Tier-2 layout: rooms, doors, beds (the single source of the Tier-2 floor and the Gazebo world) |
