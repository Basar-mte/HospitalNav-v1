"""Record what code and libraries a campaign ran with: git HEAD and working-tree status,
sha256 of every behaviour-defining file (environment, rewards, baselines, navigation
stack, training, evaluation, configs, orchestrator), library versions, the full pip
freeze, and a verbatim copy of every hashed file.

    python campaign/provenance.py [runs_dir]      (default runs)

The paper's own record is in results/provenance/. It was written before the code was
reorganised, so its file paths are the old ones (for example experiments/planner/).
"""
from __future__ import annotations
import hashlib, platform, subprocess, sys, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
RUNS = ROOT / (sys.argv[1] if len(sys.argv) > 1 else "runs")
OUT = RUNS / "provenance"
OUT.mkdir(parents=True, exist_ok=True)

GLOBS = ["envs/*.py", "rewards/*.py", "baselines/*.py", "navstack/*.py", "training/*.py",
         "evaluation/*.py", "configs/*.yaml", "campaign/*.py", "ablations/robustness/*.py"]


def sh(cmd):
    try:
        return subprocess.run(cmd, cwd=str(ROOT), capture_output=True, text=True, timeout=120).stdout
    except Exception as e:  # noqa: BLE001
        return f"<{e}>"


files = sorted({p for g in GLOBS for p in ROOT.glob(g) if p.is_file()})
with open(OUT / "sha256.txt", "w", encoding="utf-8") as f:
    for p in files:
        f.write(f"{hashlib.sha256(p.read_bytes()).hexdigest()}  {p.relative_to(ROOT).as_posix()}\n")

(OUT / "git.txt").write_text(
    f"recorded {time.strftime('%Y-%m-%d %H:%M:%S')}\nHEAD {sh(['git', 'rev-parse', 'HEAD']).strip()}\n"
    f"branch {sh(['git', 'rev-parse', '--abbrev-ref', 'HEAD']).strip()}\n\n--- git status --short ---\n"
    + sh(["git", "status", "--short"]) + "\n--- git diff --stat ---\n" + sh(["git", "diff", "--stat"]),
    encoding="utf-8")

import numpy, torch, gymnasium, stable_baselines3  # noqa: E402
(OUT / "versions.txt").write_text(
    f"python {platform.python_version()} ({platform.platform()})\nnumpy {numpy.__version__}\n"
    f"torch {torch.__version__}\ngymnasium {gymnasium.__version__}\nstable_baselines3 {stable_baselines3.__version__}\n"
    f"cpu_count {__import__('os').cpu_count()}\n", encoding="utf-8")
(OUT / "pip_freeze.txt").write_text(sh([sys.executable, "-m", "pip", "freeze"]), encoding="utf-8")

# Verbatim copies of every hashed code file, so the record is self-contained.
import shutil  # noqa: E402
snap = OUT / "snapshot"
snap.mkdir(exist_ok=True)
for p in files:
    rel = p.relative_to(ROOT)
    if rel.suffix == ".py":
        dst = snap / rel
        dst.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(p, dst)
print(f"provenance written to {OUT}: {len(files)} files hashed and copied to snapshot/")
