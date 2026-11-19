# The benchmark environment

| File | What it does |
|---|---|
| `hospital_env.py` | `HospitalNavEnv`, the Gymnasium environment: robot model, LiDAR, observation, episode rules, metrics |
| `floorplan.py` | reads a floor-plan YAML from `configs/` and turns it into an occupancy grid and a zone map |
| `pedestrians.py` | the crowd: four kinds of people moved by an anisotropic social force model |

```python
from envs.hospital_env import HospitalNavEnv
env = HospitalNavEnv(floorplan_path="configs/tier2_walled_ward.yaml", use_camera=False)
obs, info = env.reset(seed=1000, options={"task": "STAT_medicine", "density": "medium"})
```

See [docs/02_benchmark.md](../docs/02_benchmark.md) for the full description.
