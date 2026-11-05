"""Pilot run for #116 aida (seed 116001, n=1000). Writes results/pilot.json."""

import json
import os
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from aida import gen_population, evaluate, bootstrap_mean

SEED = 116001
alerts = gen_population(SEED, 500, 500)
res = evaluate(alerts, SEED)
net_ci = bootstrap_mean(res["review"]["net_list"], seed=999)

arms = {a: {k: v for k, v in m.items() if k != "decisions"}
        for a, m in res["arms"].items()}
out = {
    "meta": {"seed": SEED, "n_attack": 500, "n_benign": 500},
    "arms": arms,
    "review": {"corrected": res["review"]["corrected"],
               "broken": res["review"]["broken"],
               "net": res["review"]["net"],
               "net_per_alert": res["review"]["net_per_alert"],
               "net_ci95": net_ci["ci95"]},
    "trap": res["trap"],
    "pilot_gate": {
        "P1_react_fnr_ge_0.25": res["arms"]["react"]["fnr"] >= 0.25,
        "P2_trap_dismiss_ge_0.75": res["trap"]["single_dismiss_rate"] >= 0.75,
        "P3_net_correction_negative": res["review"]["net"] < 0,
        "P4_aida_fnr_le_0.05": res["arms"]["aida"]["fnr"] <= 0.05,
    },
}
out["pilot_gate"]["pass"] = all(out["pilot_gate"].values())
os.makedirs(os.path.join(os.path.dirname(__file__), "results"), exist_ok=True)
with open(os.path.join(os.path.dirname(__file__), "results", "pilot.json"),
          "w") as f:
    json.dump(out, f, indent=2)
print(json.dumps(out, indent=2))
