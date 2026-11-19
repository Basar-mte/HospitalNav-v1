# 1. Install

You need **Python 3.10 or newer** (the paper used 3.12) and about 2 GB of disk space for the
Python packages. A GPU is not needed: the networks are small, and the paper trained every run
on one CPU core.

## Steps

```bash
git clone https://github.com/Basar-mte/HospitalNav-v1.git
cd HospitalNav-v1

python -m venv .venv                 # a private Python environment for this project
source .venv/bin/activate            # Linux and macOS
# .venv\Scripts\activate             # Windows

pip install -r requirements.txt
```

`requirements.txt` lists the packages and, in comments, the versions the paper used. To get the
exact environment of the paper, install from `results/provenance/pip_freeze.txt` instead.

## Check the installation

```bash
pytest tests/
```

All tests should pass in under a minute. They check the floor plans, the crowd, the robot
model, the reward, and that the training script builds exactly the commands the paper's
campaign used.

## Look around (optional)

Drive the robot yourself with the arrow keys (needs a screen):

```bash
python tools/play.py --density medium
```

Check a floor plan and draw it with a planned path for every task:

```bash
python tools/validate_floorplan.py configs/tier2_walled_ward.yaml
python tools/plot_routes.py configs/tier2_walled_ward.yaml
```

## Run commands from the repository folder

Every command in these guides is run from the top folder of the repository (the folder that
holds `README.md`). The scripts find the other folders from there.

Next: [2. The benchmark](02_benchmark.md)
