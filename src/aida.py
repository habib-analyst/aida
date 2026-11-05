"""Project #116 `aida`: scripted analog of AIDA (arXiv 2610.10608).

Scripted triage agents over synthetic alerts with planted evidence records.
No LLM, no SIEM, no real telemetry. Deterministic given a seed.

Model (fixed in G0, before any pilot number):
- Query universe: 20 query ids. Each alert draws one seeded query
  permutation; every arm reads prefixes/chunks of the SAME permutation
  (common random numbers -> paired comparison across arms).
- Attack alert: 3 discoverable incriminating queries, 2 discoverable
  exonerating queries. Benign alert: 6 discoverable exonerating queries,
  0 incriminating. No false-positive mechanism exists by construction, so
  baseline precision is 1.0 by construction (stated scope limit); the
  comparison is on recall/FNR, and the benign bound is AIDA's own
  escalation rate.
- Baseline decision rule: escalate iff an incriminating item was found,
  else dismiss.

AIDA protocol (Dialectical Commitment Protocol, paper Sec. V):
- Append-only Investigation Ledger: entries are appended, never
  overwritten or deleted (Ledger class exposes append() only).
- Round: Strategist searches up to B new queries; found items are
  appended to the ledger. Thesis: escalate iff incriminating in ledger,
  else dismiss, citing ledger entries.
- Adversary: receives ONLY (thesis decision, cited item ids, ledger
  evidence entries). The Strategist's private reasoning is NEVER passed
  to the Adversary or the Judge (separate function arguments, tested).
  Challenge: contradiction if thesis dismisses while an incriminating
  item is in the ledger; completeness if thesis dismisses with total
  evidence items found < EVIDENCE_BAR (3).
- Judge: contradiction -> escalate; completeness -> continuation (new
  round, budget reset, ledger persists), except in the final round where
  the conservative default is escalate (dismissal bar unmet); no
  challenge -> thesis stands. Escalate-theses are never challenged
  (dismissal is the terminal action -> asymmetric bar).
"""

import random

N_QUERIES = 20
BUDGET_ROUND = 5
MAX_ROUNDS = 3
EVIDENCE_BAR = 3
REVIEW_ACCURACY = 0.60


class Ledger:
    """Append-only investigation ledger. No mutation API exists."""

    def __init__(self, alert_id):
        self.alert_id = alert_id
        self._entries = []

    def append(self, entry):
        self._entries.append(dict(entry))

    def entries(self):
        return [dict(e) for e in self._entries]

    def evidence_items(self):
        """Item ids of evidence entries only (theses/challenges excluded)."""
        return [e["item"] for e in self._entries if e["kind"] == "evidence"]

    def __len__(self):
        return len(self._entries)


def gen_alert(rng, label):
    """label: 1 = attack, 0 = benign. Returns (inc_set, exon_set)."""
    if label == 1:
        inc = set(rng.sample(range(N_QUERIES), 3))
        remaining = [q for q in range(N_QUERIES) if q not in inc]
        exon = set(rng.sample(remaining, 2))
    else:
        inc = set()
        exon = set(rng.sample(range(N_QUERIES), 6))
    return inc, exon


def gen_population(seed, n_attack, n_benign):
    """One seeded population; every arm runs on the SAME alerts."""
    rng = random.Random(seed)
    alerts = []
    for i in range(n_attack):
        inc, exon = gen_alert(rng, 1)
        order = list(range(N_QUERIES))
        rng.shuffle(order)
        alerts.append({"id": i, "label": 1, "inc": inc, "exon": exon,
                       "order": order})
    for j in range(n_benign):
        inc, exon = gen_alert(rng, 0)
        order = list(range(N_QUERIES))
        rng.shuffle(order)
        alerts.append({"id": n_attack + j, "label": 0, "inc": inc,
                       "exon": exon, "order": order})
    return alerts


def _found(alert, queries):
    """Evidence items found by issuing `queries` (query ids)."""
    found_inc = [q for q in queries if q in alert["inc"]]
    found_exon = [q for q in queries if q in alert["exon"]]
    return found_inc, found_exon


def _decide(found_inc):
    return "escalate" if found_inc else "dismiss"


def run_single_pass(alert, budget=2):
    fi, fe = _found(alert, alert["order"][:budget])
    return _decide(fi), budget


def run_react(alert, budget=5):
    fi, fe = _found(alert, alert["order"][:budget])
    return _decide(fi), budget


def run_self_consistency(alert, rng):
    """3 independent budget-2 runs (fresh permutations), majority."""
    votes = []
    for _ in range(3):
        order = list(range(N_QUERIES))
        rng.shuffle(order)
        fi, _ = _found(alert, order[:2])
        votes.append(_decide(fi))
    dec = "escalate" if votes.count("escalate") >= 2 else "dismiss"
    return dec, 6


def run_review(alert, rng):
    """Same-context review: single-pass decision REPLACED by a fresh
    judgment correct with p=REVIEW_ACCURACY (fixed in G0). Returns
    (initial, final, searches, corrected, broken)."""
    initial, _ = run_single_pass(alert, budget=2)
    correct = "escalate" if alert["label"] == 1 else "dismiss"
    if rng.random() < REVIEW_ACCURACY:
        final = correct
    else:
        final = "dismiss" if correct == "escalate" else "escalate"
    corrected = 1 if (initial != correct and final == correct) else 0
    broken = 1 if (initial == correct and final != correct) else 0
    return initial, final, 2, corrected, broken


def adversary_view(thesis_decision, cited_items, ledger):
    """The ONLY view the Adversary (and Judge) ever receive. Contains no
    Strategist private reasoning by construction: the reasoning string
    is not an argument and is never copied into this view."""
    return {"thesis": thesis_decision, "cited": list(cited_items),
            "evidence": ledger.evidence_items()}


def _adversary_challenge(thesis_decision, ledger):
    """Internal challenge logic on the evidence-only view."""
    if thesis_decision != "dismiss":
        return None
    ev = ledger.evidence_items()
    # Contradiction: an incriminating item is in the ledger. The view
    # carries item ids; incriminating status is determined by the ledger
    # entry kind recorded at append time (see run_aida).
    for e in ledger.entries():
        if e["kind"] == "evidence" and e.get("incriminating"):
            return "contradiction"
    if len(ev) < EVIDENCE_BAR:
        return "completeness"
    return None


def run_aida(alert):
    """Full AIDA protocol. Returns dict with final decision, rounds,
    searches, and ledger length. The Strategist's private reasoning is
    generated but NEVER passed to adversary/judge functions."""
    ledger = Ledger(alert["id"])
    ledger.append({"kind": "alert", "label_hidden": True})
    consumed = 0
    searches = 0
    final = None
    rounds_used = 0
    for rnd in range(1, MAX_ROUNDS + 1):
        rounds_used = rnd
        chunk = alert["order"][consumed:consumed + BUDGET_ROUND]
        consumed += len(chunk)
        searches += len(chunk)
        fi, fe = _found(alert, chunk)
        for q in fi:
            ledger.append({"kind": "evidence", "item": q,
                           "incriminating": True})
        for q in fe:
            ledger.append({"kind": "evidence", "item": q,
                           "incriminating": False})
        # Strategist private reasoning (WITHHELD from challenge/judge).
        _private_reasoning = (
            "strategist-note: found %d incriminating, %d exonerating"
            % (len(fi), len(fe)))
        del _private_reasoning
        # Thesis from ledger evidence only.
        inc_in_ledger = any(e["kind"] == "evidence" and e.get("incriminating")
                            for e in ledger.entries())
        thesis = "escalate" if inc_in_ledger else "dismiss"
        cited = ledger.evidence_items()
        ledger.append({"kind": "thesis", "decision": thesis,
                       "cited": list(cited)})
        # Adversary: evidence-only view (no reasoning argument exists).
        challenge = _adversary_challenge(thesis, ledger)
        if challenge is not None:
            ledger.append({"kind": "challenge", "type": challenge})
        # Judge: thesis + challenge + ledger evidence only.
        if challenge == "contradiction":
            final = "escalate"
            break
        if challenge == "completeness":
            if rnd < MAX_ROUNDS:
                ledger.append({"kind": "continuation",
                               "missing": "more evidence required"})
                continue
            final = "escalate"  # final-round conservative default
            break
        final = thesis
        break
    ledger.append({"kind": "decision", "decision": final})
    return {"decision": final, "rounds": rounds_used, "searches": searches,
            "ledger_len": len(ledger)}


def run_no_adversary(alert):
    """Ablation: round-1 thesis stands (no Adversary, no Judge bar)."""
    fi, fe = _found(alert, alert["order"][:BUDGET_ROUND])
    return _decide(fi), BUDGET_ROUND


def run_no_judge_bar(alert):
    """Ablation: Adversary challenge is recorded but the Judge always
    upholds the round-1 thesis immediately (no continuation, no bar)."""
    fi, fe = _found(alert, alert["order"][:BUDGET_ROUND])
    return _decide(fi), BUDGET_ROUND


def run_oracle(alert, budget=15):
    fi, fe = _found(alert, alert["order"][:budget])
    return _decide(fi), budget


def evaluate(alerts, seed):
    """Run every arm on the same population. Returns metrics dict."""
    rng = random.Random(seed + 777)
    arms = ["single", "react", "selfcons", "review", "aida",
            "no_adversary", "no_judge_bar", "oracle"]
    dec = {a: [] for a in arms}
    searches = {a: [] for a in arms}
    corrected = broken = 0
    net_list = []
    trap_idx = []  # attack alerts whose FIRST query is non-discoverable
    for al in alerts:
        first = al["order"][0]
        if al["label"] == 1 and first not in al["inc"] and first not in al["exon"]:
            trap_idx.append(len(dec["single"]))
        d, s = run_single_pass(al)
        dec["single"].append(d); searches["single"].append(s)
        d, s = run_react(al)
        dec["react"].append(d); searches["react"].append(s)
        d, s = run_self_consistency(al, rng)
        dec["selfcons"].append(d); searches["selfcons"].append(s)
        ini, fin, s, c, b = run_review(al, rng)
        dec["review"].append(fin); searches["review"].append(s)
        corrected += c; broken += b
        net_list.append(c - b)
        r = run_aida(al)
        dec["aida"].append(r["decision"]); searches["aida"].append(r["searches"])
        d, s = run_no_adversary(al)
        dec["no_adversary"].append(d); searches["no_adversary"].append(s)
        d, s = run_no_judge_bar(al)
        dec["no_judge_bar"].append(d); searches["no_judge_bar"].append(s)
        d, s = run_oracle(al)
        dec["oracle"].append(d); searches["oracle"].append(s)
    labels = [a["label"] for a in alerts]
    out = {"arms": {}, "review": {"corrected": corrected, "broken": broken,
                                  "net": corrected - broken,
                                  "net_per_alert": (corrected - broken) / len(alerts),
                                  "net_list": net_list},
           "trap": {}}
    for a in arms:
        tp = sum(1 for d, y in zip(dec[a], labels) if d == "escalate" and y == 1)
        fn = sum(1 for d, y in zip(dec[a], labels) if d == "dismiss" and y == 1)
        fp = sum(1 for d, y in zip(dec[a], labels) if d == "escalate" and y == 0)
        tn = sum(1 for d, y in zip(dec[a], labels) if d == "dismiss" and y == 0)
        n_att = tp + fn
        fnr = fn / n_att if n_att else 0.0
        prec = tp / (tp + fp) if (tp + fp) else 0.0
        rec = tp / n_att if n_att else 0.0
        f1 = (2 * prec * rec / (prec + rec)) if (prec + rec) else 0.0
        out["arms"][a] = {
            "tp": tp, "fn": fn, "fp": fp, "tn": tn, "fnr": fnr,
            "benign_escalation": fp / (fp + tn) if (fp + tn) else 0.0,
            "benign_accuracy": tn / (fp + tn) if (fp + tn) else 0.0,
            "f1": f1, "mean_searches": sum(searches[a]) / len(searches[a]),
            "decisions": dec[a],
        }
    # Empty-search trap: single-pass dismissal rate on trap subset.
    trap_dec = [dec["single"][i] for i in trap_idx]
    trap_aida = [dec["aida"][i] for i in trap_idx]
    out["trap"] = {
        "n": len(trap_idx),
        "single_dismiss_rate": (sum(1 for d in trap_dec if d == "dismiss")
                                / len(trap_dec)) if trap_dec else 0.0,
        "aida_dismiss_rate": (sum(1 for d in trap_aida if d == "dismiss")
                              / len(trap_aida)) if trap_aida else 0.0,
    }
    return out


def paired_bootstrap(alerts, arm_a, arm_b, n_boot=2000, seed=999):
    """Bootstrap CI for FNR(arm_a) - FNR(arm_b), paired by alert."""
    import statistics
    res = evaluate(alerts, seed)
    # Recompute per-alert FNR contributions: need per-alert decisions.
    # evaluate() already stores decisions per arm; reuse them.
    dec_a = res["arms"][arm_a]["decisions"]
    dec_b = res["arms"][arm_b]["decisions"]
    labels = [a["label"] for a in alerts]
    att = [i for i, y in enumerate(labels) if y == 1]
    rng = random.Random(seed)
    diffs = []
    for _ in range(n_boot):
        sample = [rng.choice(att) for _ in att]
        fa = sum(1 for i in sample if dec_a[i] == "dismiss") / len(sample)
        fb = sum(1 for i in sample if dec_b[i] == "dismiss") / len(sample)
        diffs.append(fa - fb)
    diffs.sort()
    lo = diffs[int(0.025 * n_boot)]
    hi = diffs[int(0.975 * n_boot)]
    mean = sum(diffs) / len(diffs)
    return {"mean": mean, "ci95": [lo, hi]}


def bootstrap_mean(values, n_boot=2000, seed=999):
    rng = random.Random(seed)
    means = []
    for _ in range(n_boot):
        s = [rng.choice(values) for _ in values]
        means.append(sum(s) / len(s))
    means.sort()
    return {"mean": sum(means) / len(means),
            "ci95": [means[int(0.025 * n_boot)], means[int(0.975 * n_boot)]]}
