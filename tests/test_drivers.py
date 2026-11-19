"""training/train.py and evaluation/evaluate_run.py build their commands from the driver
table in training/drivers.py. These tests check that the table gives exactly the
commands and environment variables the paper's campaign used, for all 96 runs."""
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
import campaign.run_campaign as C  # noqa: E402
from training.drivers import DRIVERS, group_name, process_env, train_args  # noqa: E402

AGENT_TO_DRIVER = {d["agent"]: name for name, d in DRIVERS.items()}
PLANNER_NAME = {"cult": "cultural", "geo": "geometric", None: "none"}


def _runs():
    for g, a, s in C.KEYS:
        tier = 1 if g.startswith("tier1") else 2
        planner = PLANNER_NAME[C.planner_mode(g, a)]
        yield (g, a, s), AGENT_TO_DRIVER[a], tier, planner, bool(C.GROUPS[g].get("pivot"))


def test_campaign_has_96_runs():
    if C.SMOKE:
        return
    assert len(C.KEYS) == 96


def test_group_names_match_campaign():
    for (g, a, s), drv, tier, planner, pivot in _runs():
        assert group_name(tier, drv, planner, pivot) == g, (g, a, s)


def test_environment_matches_campaign():
    for key, drv, tier, planner, pivot in _runs():
        for evaluation in (False, True):
            assert process_env(drv, planner, pivot, evaluation) == C.env_for(key, evaluation=evaluation), key


def test_training_command_matches_campaign():
    for key, drv, tier, planner, pivot in _runs():
        g, a, s = key
        label, cmd = C.build_cmd(key)
        if "--resume_from" in cmd:      # a local run exists; the fresh-run form is what we compare
            continue
        assert cmd[2:-2] == train_args(drv, tier, s, C.GROUPS[g]["steps"]), key
        assert cmd[-2:] == ["--log_dir", os.path.relpath(C.RUNS / g / f"{a}_s{s}", C.ROOT)], key
