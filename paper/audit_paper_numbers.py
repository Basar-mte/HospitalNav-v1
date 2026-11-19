"""Check the paper's headline numbers against the result files (prints OK or FAIL per number).

    python paper/audit_paper_numbers.py

Reads results/summary/ (the paper's records). Set HOSPITALNAV_RESULTS=runs to check your own runs.
"""
import json, sys
from pathlib import Path
import numpy as np

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))
import os  # noqa: E402
import campaign.run_campaign as C  # noqa: E402  (group definitions: seeds per group)

RES = ROOT / os.environ.get("HOSPITALNAV_RESULTS", "results") / "summary"
T = {g: json.load(open(RES / g / "table.json")) for g in
     ["tier1", "tier2", "tier2_mapless", "tier1_mapless", "tier2_planner_ablation",
      "tier2_pivot", "tier2_ppo", "tier2_td3", "tier2_residual", "tier2_safe"]}
PT2 = json.load(open(RES / "tier2" / "per_task.json"))
PTA = json.load(open(RES / "tier2_planner_ablation" / "per_task.json"))
CL = RES / "tier2" / "classical"
ok = fail = 0


def chk(name, got, want, tol=0.051):
    global ok, fail
    good = abs(got - want) <= tol
    ok += good; fail += (not good)
    print(f"{'OK  ' if good else 'FAIL'} {name}: results={got:.3f} text={want}")


def cj(n):
    return json.load(open(CL / f"{n}.json"))["summary"]


# --- headline claims (text value, results value) in percent/points -------------
chk("mapless t2 fe final SR", 100 * T["tier2_mapless"]["fixed_equal"]["final"]["sr"], 48.2)
chk("mapless t2 fe final std", 100 * T["tier2_mapless"]["fixed_equal"]["final"]["sr_std"], 2.7)
chk("mapless t2 fe shield2 SR", 100 * T["tier2_mapless"]["fixed_equal"]["shield2"]["sr"], 56.5)
chk("mapless t2 fe shield2 tout", 100 * T["tier2_mapless"]["fixed_equal"]["shield2"]["timeout"], 43.5)
chk("t1 mapless fe final", 100 * T["tier1_mapless"]["fixed_equal"]["final"]["sr"], 67.9)
chk("t1 fe final", 100 * T["tier1"]["fixed_equal"]["final"]["sr"], 80.3)
chk("t2 fe final", 100 * T["tier2"]["fixed_equal"]["final"]["sr"], 80.4)
chk("sf2 mapless", 100 * cj("sf2")["sr"], 58.2)
chk("sf2 planner (unbiased tuned)", 100 * cj("planner_sf2_tuned")["sr"], 95.4)
chk("sf2 planner coll", 100 * cj("planner_sf2_tuned")["collision"], 4.6)
chk("sf2 v2", 100 * cj("planner_sf2_tunedb_shield2")["sr"], 97.8)
chk("sf2 v2 tout", 100 * cj("planner_sf2_tunedb_shield2")["timeout"], 2.2)
chk("sf2 v1", 100 * cj("planner_sf2_tuned_shield")["sr"], 93.0)
chk("orca plain", 100 * cj("planner_orca")["sr"], 66.8)
chk("stock sf plain", 100 * cj("planner_sf")["sr"], 6.0)   # text says 'deadlocks ~5-6%'; sf (no planner) 4.6
chk("astar plain", 100 * cj("astar_pp")["sr"], 11.4)
chk("pp plain", 100 * cj("planner_pp")["sr"], 37.0)
chk("residual final", 100 * T["tier2_residual"]["residual_sf"]["final"]["sr"], 94.0)
chk("residual final std", 100 * T["tier2_residual"]["residual_sf"]["final"]["sr_std"], 0.2)
chk("residual shield2", 100 * T["tier2_residual"]["residual_sf"]["shield2"]["sr"], 99.4)
chk("residual shield2 std", 100 * T["tier2_residual"]["residual_sf"]["shield2"]["sr_std"], 0.4)
chk("residual shield2 tout", 100 * T["tier2_residual"]["residual_sf"]["shield2"]["timeout"], 0.6)
chk("td3 final", 100 * T["tier2_td3"]["td3_equal"]["final"]["sr"], 65.0)
chk("td3 std", 100 * T["tier2_td3"]["td3_equal"]["final"]["sr_std"], 11.3)
chk("ppo final", 100 * T["tier2_ppo"]["ppo_equal"]["final"]["sr"], 0.0)
chk("safe_heavy coll", 100 * T["tier2_safe"]["safe_heavy"]["final"]["collision"], 17.2)
chk("pivot shield2", 100 * T["tier2_pivot"]["fixed_equal"]["shield2"]["sr"], 99.3)
chk("2x2 fe-geo STAT", PTA["fixed_equal"]["final"]["STAT_medicine"]["cvr"], 0.081, 0.0015)
chk("2x2 fe-cult STAT", PT2["fixed_equal"]["final"]["STAT_medicine"]["cvr"], 0.001, 0.0015)
chk("2x2 van-cult STAT", PTA["vanilla"]["final"]["STAT_medicine"]["cvr"], 0.003, 0.0015)
chk("2x2 van-geo STAT", PT2["vanilla"]["final"]["STAT_medicine"]["cvr"], 0.080, 0.0015)
chk("cost of culture vanilla", 100 * (T["tier2"]["vanilla"]["final"]["sr"] - T["tier2_planner_ablation"]["vanilla"]["final"]["sr"]), 3.2)

# ranges claimed in text
ag = ["cwn", "fixed_equal", "nav_heavy", "attention", "vanilla", "he2025"]
t2f = [100 * T["tier2"][a]["final"]["sr"] for a in ag]
t1f = [100 * T["tier1"][a]["final"]["sr"] for a in ag]
s2 = [100 * T["tier2"][a]["shield2"]["sr"] for a in ag] + [100 * T["tier1"][a]["shield2"]["sr"] for a in ag]
v1c2 = [100 * T["tier2"][a]["shield"]["collision"] for a in ag]
v1c1 = [100 * T["tier1"][a]["shield"]["collision"] for a in ag]
print(f"INFO tier2 final range {min(t2f):.1f}-{max(t2f):.1f} (text 80-85 for learned incl blind: 79.9-84.5)")
print(f"INFO tier1 final range {min(t1f):.1f}-{max(t1f):.1f} (text 77-84.5)")
print(f"INFO shield2 range both tiers {min(s2):.1f}-{max(s2):.1f} (text 93-96)")
print(f"INFO v1 coll range t2 {min(v1c2):.1f}-{max(v1c2):.1f}  t1 {min(v1c1):.1f}-{max(v1c1):.1f} (text 'leaves 4-6%')")
cars2 = [100 * T["tier2"][a]["final"]["sr"] for a in ["cwn", "fixed_equal", "nav_heavy", "attention"]]
cars1 = [100 * T["tier1"][a]["final"]["sr"] for a in ["cwn", "fixed_equal", "nav_heavy", "attention"]]
print(f"INFO CARS weighting spread t2 {max(cars2)-min(cars2):.1f} pp (text <=1), t1 {max(cars1)-min(cars1):.1f} pp (text <=5)")
tout2 = [100 * T["tier2"][a]["shield2"]["timeout"] for a in ag] + [100 * T["tier1"][a]["shield2"]["timeout"] for a in ag]
print(f"INFO shield2 timeout range {min(tout2):.1f}-{max(tout2):.1f} + residual 0.6 (text 0.6-5%)")

# Contact census under the swept filter, counted from the per-episode records.
# Paper: 0 contacts in 42,500 episodes of planner-guided drivers that navigate (all learned
# planner runs except PPO-CARS, plus the classical planner_* drivers), and 4 contacts in all
# 54,000 clean-world swept-filter episodes (adding mapless runs, PPO-CARS, A* and plain SF).
EXCLUDE = {"planner_sf2_tunedb_shield2.json",   # the same 500 episodes as planner_sf2_shield2.json
           "planner_sf2_tuned_shield2.json"}    # ran with the first, discarded filter margins
all_n = all_c = pg_n = pg_c = 0
contacts = []
for g in T:
    for a in T[g]:
        for s in C.GROUPS[g]["seeds"]:
            recs = json.load(open(RES.parent / g / f"{a}_s{s}" / "eval_shield2.json"))["records"]
            n, c = len(recs), sum(r["end"] == "collision" for r in recs)
            all_n += n; all_c += c
            if c:
                contacts.append(f"{g}/{a}_s{s}:{c}")
            if not g.endswith("_mapless") and a != "ppo_equal":
                pg_n += n; pg_c += c
for f in sorted(RES.glob("tier*/classical/*_shield2.json")):
    if "__" in f.name or f.name in EXCLUDE:
        continue
    recs = json.load(open(f))["records"]
    n, c = len(recs), sum(r["end"] == "collision" for r in recs)
    all_n += n; all_c += c
    if c:
        contacts.append(f"{f.parent.parent.name}/{f.name}:{c}")
    if f.name.startswith("planner_"):
        pg_n += n; pg_c += c
chk("swept filter: episodes, planner-guided navigating drivers", pg_n, 42500, tol=0)
chk("swept filter: contacts, planner-guided navigating drivers", pg_c, 0, tol=0)
chk("swept filter: episodes, all clean-world runs", all_n, 54000, tol=0)
chk("swept filter: contacts, all clean-world runs", all_c, 4, tol=0)
print(f"INFO runs with a contact under the swept filter: {', '.join(contacts) if contacts else 'none'}")

print(f"\n{ok} OK, {fail} FAIL")
