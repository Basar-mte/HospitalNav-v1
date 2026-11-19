# The CARS reward (culture-aware reward shaping)

The learned drivers are trained with a reward made of four parts. Each part has a weight.

| File | What it does |
|---|---|
| `components.py` | navigation (progress toward the goal or along the route, arrival bonus), safety (closeness to people, contact) and task (urgency, lateness) parts |
| `cultural.py` | the cultural part: prayer room (stronger in prayer times), gendered wards, family attendants; and the counter of cultural violations |
| `cwn.py` | how the parts are weighted: fixed weights (`FixedWeightSource`, e.g. equal for SAC-CARS) or a context weight network (SAC-CWN) |
| `reinforce_mixin.py` | trains the context weight network |

The culture-blind and risk-field rewards of SAC-blind and SAC-risk are in `baselines/`.
