"""The learned drivers of the paper, by their paper names, and the exact settings the
campaign used for each one (trainer, agent id, planner, environment variables).

training/train.py and evaluation/evaluate_run.py both read this table, and
tests/test_drivers.py checks that it reproduces the campaign's own commands
(campaign/run_campaign.py) for every one of the 96 runs.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import campaign.run_campaign as C  # noqa: E402  (recipe, planner defaults, base environment)

SAC = "training/train_sac.py"

# paper name -> agent id (used in code and file names), trainer, extra environment variables
DRIVERS = {
    "sac_cars":      dict(agent="fixed_equal", trainer=SAC, help="SAC, CARS reward with equal weights"),
    "sac_cars_nav":  dict(agent="nav_heavy", trainer=SAC, help="SAC, navigation-heavy CARS weights"),
    "sac_cars_safe": dict(agent="safe_heavy", trainer=SAC, env={"PILOT_AGENT": "safe_heavy"},
                          help="SAC, safety-heavy CARS weights"),
    "sac_cwn":       dict(agent="cwn", trainer=SAC, help="SAC, CARS weights from a context weight network"),
    "sac_attn":      dict(agent="attention", trainer=SAC, help="SAC, CARS weights from an attention layer"),
    "sac_blind":     dict(agent="vanilla", trainer=SAC, help="SAC, culture-blind reward"),
    "sac_risk":      dict(agent="he2025", trainer=SAC, help="SAC, risk-field reward (He et al. 2025)"),
    "residual":      dict(agent="residual_sf", trainer=SAC, env={"PILOT_AGENT": "residual_sf"},
                          help="SAC correction on top of the tuned social force"),
    "td3_cars":      dict(agent="td3_equal", trainer=C.TD3, help="TD3, CARS reward with equal weights"),
    "ppo_cars":      dict(agent="ppo_equal", trainer=C.PPO, help="PPO (library defaults), CARS equal weights"),
}
PLANNERS = {"cultural": "cult", "geometric": "geo", "none": None}
CONFIGS = {1: C.T1, 2: C.T2}


def default_planner(driver: str) -> str:
    """The paper's planner for a driver: culture-blind rewards get the geometric planner."""
    return "geometric" if DRIVERS[driver]["agent"] in C.CULTURE_BLIND else "cultural"


def group_name(tier: int, driver: str, planner: str, pivot: bool = False) -> str:
    """Folder name of the campaign group a run belongs to (e.g. tier2, tier2_mapless)."""
    t = f"tier{tier}"
    special = {"residual": "residual", "sac_cars_safe": "safe", "td3_cars": "td3", "ppo_cars": "ppo"}
    if pivot:
        return f"{t}_pivot"
    if planner == "none":
        return f"{t}_mapless"
    if planner != default_planner(driver):
        return f"{t}_planner_ablation"
    if driver in special:
        return f"{t}_{special[driver]}"
    return t


def process_env(driver: str, planner: str, pivot: bool = False, evaluation: bool = False) -> dict:
    """Environment variables for one training or evaluation process (same rules as
    campaign.run_campaign.env_for)."""
    d = DRIVERS[driver]
    env = {**C.BASE_ENV, **({"PILOT_PIVOT": "1"} if pivot else {})}
    mode = PLANNERS[planner]
    if mode:
        env.update(C.PLANNER_DEFAULTS, PLANNER_MODE=mode)
        if evaluation:
            env["PLANNER_PROGRESS"] = "0"
    if d["trainer"] == C.PPO:
        env["PILOT_ALGO"] = "ppo"
        env["PILOT_NORM_REWARD"] = "1"
    elif d["trainer"] == C.TD3:
        env["PILOT_ALGO"] = "td3"
    env.update(d.get("env", {}))
    return env


def train_args(driver: str, tier: int, seed: int, steps: int) -> list[str]:
    """Arguments after `python training/patches.py` (without --log_dir / --resume_from)."""
    d = DRIVERS[driver]
    recipe = C.PPO_RECIPE if d["trainer"] == C.PPO else C.RECIPE
    return [d["trainer"], "--config", CONFIGS[tier], "--agent", d["agent"], "--seed", str(seed),
            "--timesteps", str(steps), *recipe]


def apply_in_process(env: dict) -> None:
    """Put the variables into this process (call before importing training.patches)."""
    for k in [k for k in os.environ if k.startswith("PLANNER_") or k in ("PILOT_PIVOT", "PILOT_AGENT", "PILOT_ALGO")]:
        os.environ.pop(k)
    os.environ.update(env)
