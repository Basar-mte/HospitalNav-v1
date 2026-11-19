"""Evaluate one trained model with the paper's protocol, with or without a safety filter.

Examples
    # a model shipped in this repository (the best Tier-2 seed of SAC-CARS), 50 episodes
    python evaluation/evaluate_run.py --model ros2/models/fixed_equal_s2 --driver sac_cars --tier 2 --filter swept --episodes 50

    # your own run (the folder written by training/train.py), all three filter settings
    python evaluation/evaluate_run.py --model runs/tier2/fixed_equal_s0 --driver sac_cars --tier 2 --filter all

The protocol
    Episode k uses random seed 1000 + k, task k mod 5 and the medium crowd (45 people), as
    in the paper. Your numbers are therefore comparable with results/ (the paper used 500
    episodes per run; fewer episodes give the same first episodes, but a noisier average).

Filters
    none   the driver's own commands
    cone   with the forward-cone filter (the baseline filter)
    swept  with the swept-path filter (the paper's filter)
    all    the three settings one after the other

Output
    Prints the success rate (SR), collision and timeout shares, the cultural and social
    violation rates (CVR, SVR), SPL and the mean time to goal, and writes
    eval_<filter>.json (one record per episode) into the --out folder (default: the model folder).
    The same files in results/ are called eval_final.json (none), eval_shield.json (cone)
    and eval_shield2.json (swept).
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))


def find_model_dir(path: Path) -> Path:
    """Accept a folder with final_model.zip, or a run slot runs/<group>/<agent>_s<seed>/
    that holds one training run folder <agent>_seed<seed>_<time>/."""
    if list(path.glob("*.zip")):
        return path
    runs = sorted(q for q in path.glob("*_seed*") if q.is_dir() and list(q.glob("final_model.zip")))
    if runs:
        return runs[-1]
    raise SystemExit(f"no trained model (final_model.zip) found in {path}")


def summary(recs: list[dict]) -> dict:
    n = len(recs)
    succ = [r for r in recs if r["success"]]
    mean = lambda k: sum(r[k] for r in recs) / n  # noqa: E731
    return dict(episodes=n, sr=len(succ) / n,
                collision=sum(r["end"] == "collision" for r in recs) / n,
                timeout=sum(r["end"] == "timeout" for r in recs) / n,
                cvr=mean("cvr"), svr=mean("svr"), spl=mean("spl"),
                time_to_goal_s=(sum(r["steps"] for r in succ) * 0.1 / len(succ)) if succ else None)


def main() -> None:
    from training.drivers import DRIVERS, PLANNERS, CONFIGS, default_planner, process_env, apply_in_process
    p = argparse.ArgumentParser(description="Evaluate one HospitalNav-v1 model with the paper's protocol.",
                                formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    p.add_argument("--model", required=True, help="model folder (final_model.zip + vec_normalize.pkl) or run slot")
    p.add_argument("--driver", required=True, choices=list(DRIVERS), help="the driver the model was trained as")
    p.add_argument("--tier", type=int, default=2, choices=[1, 2])
    p.add_argument("--planner", choices=list(PLANNERS), default=None,
                   help="must match training (default: the paper's choice for this driver)")
    p.add_argument("--pivot", action="store_true", help="the model was trained with the pivot chassis")
    p.add_argument("--filter", default="swept", choices=["none", "cone", "swept", "all"])
    p.add_argument("--episodes", type=int, default=500)
    p.add_argument("--out", default=None, help="folder for eval_<filter>.json (default: the model folder)")
    a = p.parse_args()

    planner = a.planner or default_planner(a.driver)
    model_dir = find_model_dir((ROOT / a.model) if not Path(a.model).is_absolute() else Path(a.model))
    config = CONFIGS[a.tier]
    out_dir = Path(a.out) if a.out else model_dir
    out_dir.mkdir(parents=True, exist_ok=True)

    # The patches read these variables when they are imported, so set them first.
    apply_in_process(process_env(a.driver, planner, pivot=a.pivot, evaluation=True))
    import training.patches  # noqa: F401,E402  (applies planner / agent / algorithm patches)
    import evaluation.evaluate as ev  # noqa: E402
    from evaluation.eval_group import filtered_episodes  # noqa: E402

    print(f"model {model_dir}\ndriver {a.driver}, Tier {a.tier}, planner {planner}, {a.episodes} episodes", flush=True)
    filters = ["none", "cone", "swept"] if a.filter == "all" else [a.filter]
    rows = {}
    for f in filters:
        print(f"\n--- filter: {f}", flush=True)
        if f == "none":
            recs = ev.evaluate_model(model_dir=str(model_dir), config_path=config, n_episodes=a.episodes,
                                     density="medium")["records"]
        else:
            recs = filtered_episodes(model_dir, config, v2=(f == "swept"), n_ep=a.episodes)
        rows[f] = summary(recs)
        out = out_dir / f"eval_{f}.json"
        json.dump({"driver": a.driver, "tier": a.tier, "planner": planner, "filter": f, "model": str(model_dir),
                   "summary": rows[f], "records": recs}, open(out, "w"), indent=1)
        print(f"wrote {out}", flush=True)

    print(f"\n{'filter':<7}{'SR %':>7}{'coll %':>8}{'tout %':>8}{'CVR':>7}{'SVR':>7}{'SPL':>6}{'t_goal s':>10}")
    for f, r in rows.items():
        tg = f"{r['time_to_goal_s']:.1f}" if r["time_to_goal_s"] is not None else "n/a"
        print(f"{f:<7}{100*r['sr']:>7.1f}{100*r['collision']:>8.1f}{100*r['timeout']:>8.1f}"
              f"{r['cvr']:>7.3f}{r['svr']:>7.3f}{r['spl']:>6.2f}{tg:>10}")


if __name__ == "__main__":
    main()
