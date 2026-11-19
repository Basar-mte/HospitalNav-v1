# Floor plans

| File | What it is |
|---|---|
| `tier1_open_floor.yaml` | Tier 1: open ward floor, 40 m x 30 m |
| `tier2_walled_ward.yaml` | Tier 2: walled ward, 40 m x 30 m (generated from `tools/tier2_layout.py`) |
| `unmapped_obstacles/tier2_walled_ward_L0..L9.yaml` | Tier 2 with 6 extra boxes the planner does not know about (robustness test A1) |

Each file has:

* `map`: size and grid cell size (0.1 m).
* `rooms`: polygons with a `type` (corridor, ward, `male_ward`, `female_ward`, `prayer`,
  emergency, nurse station, ...). The type decides the cultural zone.
* `static_obstacles`: walls, beds, carts and benches as polygons.
* `robot_spawn_points`, `pedestrian_spawn_zones`: where the robot and the people start.
* `tasks`: start room, goal room, urgency and deadline of the five tasks.
* `prayer_windows`: the prayer times in hours on the ward clock.
* `shift_change_windows`: times when staff traffic is higher.

Positions are in metres, deadlines in seconds and times in hours (0 to 24). Check a floor
after editing it with `python tools/validate_floorplan.py <file>`.
