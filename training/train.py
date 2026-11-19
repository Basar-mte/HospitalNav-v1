"""Train one driver of the paper with the paper's recipe. Start here.

Examples
    # SAC-CARS on Tier 2 (walled ward), seed 0, full length (2 million steps, about a day on one CPU core)
    python training/train.py --driver sac_cars --tier 2 --seed 0

    # a short test run (a few minutes) to check that everything works
    python training/train.py --driver sac_cars --tier 2 --seed 0 --steps 5000

    # the residual driver, and SAC-blind without any route planner
    python training/train.py --driver residual --tier 2 --seed 0
    python training/train.py --driver sac_blind --tier 2 --seed 0 --planner none

Drivers (names as in the paper)
    sac_cars        SAC-CARS       SAC, CARS reward with equal weights          (cultural planner)
    sac_cars_nav    SAC-CARS-nav   navigation-heavy CARS weights                (cultural planner)
    sac_cars_safe   SAC-CARS-safe  safety-heavy CARS weights                    (cultural planner)
    sac_cwn         SAC-CWN        weights from a context weight network        (cultural planner)
    sac_attn        SAC-Attn       weights from an attention layer              (cultural planner)
    sac_blind       SAC-blind      culture-blind reward                         (geometric planner)
    sac_risk        SAC-risk       risk-field reward                            (geometric planner)
    residual        Residual       SAC correction on the tuned social force     (cultural planner)
    td3_cars        TD3-CARS       TD3, CARS equal weights                      (cultural planner)
    ppo_cars        PPO-CARS       PPO with library defaults, CARS equal weights (cultural planner)

Planner (default: the one in brackets above)
    cultural   route planner with cultural prices (kappa = 3)
    geometric  route planner with the shortest path (kappa = 0)
    none       no route planner ("mapless"): the driver gets the final goal only

Output
    runs/<group>/<agent id>_s<seed>/<agent id>_seed<seed>_<time>/ with final_model.zip,
    vec_normalize.pkl, checkpoints and training logs. <group> is the campaign group the run
    belongs to (for example tier2, tier2_mapless, tier2_residual), so the campaign scripts
    can find it. Evaluate it with evaluation/evaluate_run.py.

The command that runs is printed first. It is exactly the command the campaign used
(campaign/run_campaign.py), so a run made here is a run of the paper.
"""
from __future__ import annotations

import argparse
import os
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
from training.drivers import (DRIVERS, PLANNERS, default_planner, group_name,  # noqa: E402
                              process_env, train_args)
import campaign.run_campaign as C  # noqa: E402


def main() -> None:
    p = argparse.ArgumentParser(description="Train one HospitalNav-v1 driver with the paper's recipe.",
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--driver", required=True, choices=list(DRIVERS), help="which driver to train")
    p.add_argument("--tier", type=int, default=2, choices=[1, 2], help="1 = open floor, 2 = walled ward")
    p.add_argument("--seed", type=int, default=0)
    p.add_argument("--steps", type=int, default=None,
                   help="training steps (default 2,000,000; 1,000,000 with --pivot)")
    p.add_argument("--planner", choices=list(PLANNERS), default=None,
                   help="cultural, geometric or none (default: the paper's choice for this driver)")
    p.add_argument("--pivot", action="store_true",
                   help="a chassis that can turn on the spot (kinematics ablation)")
    p.add_argument("--runs", default=None, help="output folder (default runs, or $HOSPITALNAV_RUNS)")
    p.add_argument("--resume", action="store_true", help="continue from the newest checkpoint")
    p.add_argument("--dry_run", action="store_true", help="only print the command")
    a = p.parse_args()

    planner = a.planner or default_planner(a.driver)
    steps = a.steps or (1_000_000 if a.pivot else 2_000_000)
    runs = Path(a.runs).resolve() if a.runs else C.RUNS
    group = group_name(a.tier, a.driver, planner, a.pivot)
    agent = DRIVERS[a.driver]["agent"]
    slot = runs / group / f"{agent}_s{a.seed}"

    cmd = [sys.executable, str(ROOT / "training" / "patches.py"), *train_args(a.driver, a.tier, a.seed, steps)]
    existing = sorted(q for q in slot.glob(f"{agent}_seed{a.seed}_*") if q.is_dir()) if slot.exists() else []
    if a.resume and existing and C.ckpt(existing[-1]) is not None:
        cmd += ["--resume_from", str(existing[-1])]
    else:
        cmd += ["--log_dir", os.path.relpath(slot, ROOT)]
    env = process_env(a.driver, planner, pivot=a.pivot)

    shown = {k: v for k, v in env.items() if k.startswith(("PLANNER_", "PILOT_"))}
    print(f"driver {a.driver} (agent id {agent}), Tier {a.tier}, seed {a.seed}, planner {planner}, "
          f"{steps:,} steps -> {slot}")
    print("environment:", " ".join(f"{k}={v}" for k, v in sorted(shown.items())))
    print("command:", " ".join(cmd), flush=True)
    if a.dry_run:
        return
    slot.mkdir(parents=True, exist_ok=True)
    sys.exit(subprocess.call(cmd, cwd=str(ROOT), env=env))


if __name__ == "__main__":
    main()
