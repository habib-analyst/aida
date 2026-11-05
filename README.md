# aida — project #116

Scripted analog of AIDA (Adversarial Investigation and Dialectical
Analysis) from arXiv 2610.10608, "From Investigation Failures to
Reliable SOC Agents." The finding: HOW review is organized decides
whether alert triage misses attacks — a thesis committed to an
append-only ledger, challenged from a separate evidence-only context,
and adjudicated by a Judge with a stronger bar before dismissal beats
same-context review and fixed-budget baselines.

## Run

```bash
python3 -m pytest tests/ -q   # 8 tests
python3 run_pilot.py          # seed 116001, n=1000 -> results/pilot.json
python3 run_headtohead.py     # fresh seed 116002, n=4000 -> results/headline.json
```

## Headline (fresh seed 116002, n=4000, paired bootstrap 2000)

- Baselines miss attacks: single-pass FNR 0.727, ReAct-style 0.422,
  self-consistency 0.797, same-context review 0.397 (net correction
  −162: 869 corrected vs 1031 broken).
- Empty-search trap: single-pass dismisses 83.8% of attack alerts whose
  first search returns nothing; AIDA dismisses 0.0% of the same subset.
- AIDA: FNR 0.000, F1 0.994, benign escalation 0.012, mean 9.3 searches
  (vs 15 for an exhaustive-search oracle at FNR 0.011).
- Ablations: removing the Adversary or the Judge bar collapses AIDA to
  the round-1 thesis (FNR 0.422) — both components are load-bearing.

## Scope limits (read before citing)

- Scripted analog only; synthetic planted records only. The paper's
  LLM/SIEM figures (F1 0.958, FNR 40.4% -> 3.1%, 1,247 real alerts) are
  context only, never claimed as reproduced.
- No false-positive mechanism exists by construction (benign alerts
  contain no incriminating item), so baseline precision is 1.0 by
  construction; the comparison is on recall/FNR.
- The ledger is append-only and the challenge is evidence-only: the
  Strategist's private reasoning is never passed to the Adversary or
  the Judge (enforced by function signatures, tested).
- The oracle comparison is reported, not hidden: AIDA does not beat
  exhaustive search on every metric (oracle F1 0.995 vs AIDA 0.994,
  because AIDA's final-round default escalates 1.15% of benign alerts).
  The claim is adaptive, challenge-triggered continuation at a bounded
  benign cost — not a claim about any real SOC deployment.

$0, CPU only, no LLM calls, no SIEM, no real telemetry.
