"""Head-to-head run for #116 aida (fresh seed 116002, n=4000).
Writes results/headline.json and results/headline_rerun.json (same seed)."""

import json
import os
import random
import sys

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))
from aida import gen_population, evaluate, paired_bootstrap, bootstrap_mean

SEED = 116002


def run():
    alerts = gen_population(SEED, 2000, 2000)
    res = evaluate(alerts, SEED)
    # Paired bootstrap diffs (FNR arm - FNR reference).
    d_aida_react = paired_bootstrap(alerts, "aida", "react")
    d_aida_noadv = paired_bootstrap(alerts, "aida", "no_adversary")
    d_aida_nojudge = paired_bootstrap(alerts, "aida", "no_judge_bar")
    d_aida_oracle = paired_bootstrap(alerts, "aida", "oracle")
    net_ci = bootstrap_mean(res["review"]["net_list"], seed=999)
    # Trap CI: bootstrap over the trap subset's single-pass dismissals.
    trap_n = res["trap"]["n"]
    singles = res["arms"]["single"]["decisions"]
    trap_flags = []
    for i, al in enumerate(alerts):
        first = al["order"][0]
        if al["label"] == 1 and first not in al["inc"] and first not in al["exon"]:
            trap_flags.append(1 if singles[i] == "dismiss" else 0)
    assert len(trap_flags) == trap_n
    trap_ci = bootstrap_mean(trap_flags, seed=999)

    arms = {a: {k: v for k, v in m.items() if k != "decisions"}
            for a, m in res["arms"].items()}
    bars = {
        "D1_all_baselines_fnr_ge_0.30": all(
            res["arms"][a]["fnr"] >= 0.30
            for a in ("single", "react", "selfcons", "review")),
        "D2_trap_dismiss_ge_0.80_and_ci_lo_ge_0.75":
            res["trap"]["single_dismiss_rate"] >= 0.80
            and trap_ci["ci95"][0] >= 0.75,
        "D3_net_correction_negative_and_ci_hi_lt_0":
            res["review"]["net"] < 0 and net_ci["ci95"][1] < 0,
        "M1_aida_minus_react_le_-0.20_and_ci_hi_le_-0.10":
            d_aida_react["mean"] <= -0.20 and d_aida_react["ci95"][1] <= -0.10,
        "M2_aida_minus_noadv_le_-0.15_and_ci_hi_le_-0.05":
            d_aida_noadv["mean"] <= -0.15 and d_aida_noadv["ci95"][1] <= -0.05,
        "M3_aida_minus_nojudge_le_-0.15_and_ci_hi_le_-0.05":
            d_aida_nojudge["mean"] <= -0.15 and d_aida_nojudge["ci95"][1] <= -0.05,
        "M4_searches_le_12_and_fnr_gap_vs_oracle_le_0.02":
            res["arms"]["aida"]["mean_searches"] <= 12
            and d_aida_oracle["mean"] <= 0.02,
        "B1_benign_esc_le_0.10_and_acc_ge_0.90":
            res["arms"]["aida"]["benign_escalation"] <= 0.10
            and res["arms"]["aida"]["benign_accuracy"] >= 0.90,
    }
    out = {
        "meta": {"seed": SEED, "n_attack": 2000, "n_benign": 2000},
        "arms": arms,
        "review": {"corrected": res["review"]["corrected"],
                   "broken": res["review"]["broken"],
                   "net": res["review"]["net"],
                   "net_per_alert": res["review"]["net_per_alert"],
                   "net_ci95": net_ci["ci95"]},
        "trap": dict(res["trap"]),
        "trap_ci95": trap_ci["ci95"],
        "diffs": {"aida_minus_react": d_aida_react,
                  "aida_minus_no_adversary": d_aida_noadv,
                  "aida_minus_no_judge_bar": d_aida_nojudge,
                  "aida_minus_oracle": d_aida_oracle},
        "bars": bars,
    }
    out["all_bars_pass"] = all(bars.values())
    return out


if __name__ == "__main__":
    out = run()
    d = os.path.join(os.path.dirname(__file__), "results")
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "headline.json"), "w") as f:
        json.dump(out, f, indent=2)
    # Determinism rerun on the same seed (must be byte-identical).
    out2 = run()
    with open(os.path.join(d, "headline_rerun.json"), "w") as f:
        json.dump(out2, f, indent=2)
    print(json.dumps(out, indent=2))
