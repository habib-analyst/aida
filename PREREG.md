# PREREG — Project #116 `aida` (arXiv 2610.10608)

Locked AFTER the pilot run and BEFORE any head-to-head run.
Decision rule: **ANY locked bar fails → KILL, no amendments.**
Post-hoc amendments are impermissible (the #97 veto).

## Pilot (seed 116001, n=1000, already observed — bars set below pilot values)

Final pilot (v2, after the pre-lock change below): single FNR 0.730,
react 0.392, self-consistency 0.824, same-context review 0.432;
AIDA FNR 0.000, F1 0.994, benign escalation 0.012, benign accuracy 0.988,
mean searches 9.13; no-adversary 0.392, no-judge-bar 0.392, oracle 0.006
(15 searches); review net correction −80 (per-alert CI [−0.123, −0.039]);
empty-first-search trap: single-pass dismissal 0.845 (n=373),
AIDA dismissal 0.000. Pilot gate P1–P4 all passed (see PILOT_PREREG.md).

## Pilot-informed pre-lock change (made BEFORE locking, disclosed)

The v1 pilot used EIGHT discoverable exonerating queries for benign
alerts. Combinatorics showed that choice made the
benign bound vacuous: 15 draws from 20 with 8 successes always yield
>= 3 successes (at most 12 failures can be drawn), so the final-round
conservative default could never fire on a benign alert and AIDA benign
escalation was 0.000 by construction. Before locking, benign exonerating
queries were reduced 8 -> 6 (attack side untouched: attack generation,
review, trap, and baseline FNRs are identical between v1 and v2, as
verified by the identical attack-side pilot numbers). With 6, the
final-round default fires on ~1.4% of benign alerts (analytic
P(X<=2 in 15 draws) = 0.0139; pilot v2 observed 0.012), so the benign
bound below actually bites. Pilot v1 is preserved as
results/pilot_v1_exon8.json; the locked bars rest on pilot v2
(results/pilot.json). No parameter changes after this lock.

## Head-to-head protocol (fresh seed 116002, n=4000: 2000 attack / 2000 benign)

- Same population for every arm (common query permutations, paired).
- Bootstrap: 2000 resamples, seed 999, paired by alert; CIs are
  percentile 95% CIs. Trap CI: bootstrap over the trap subset.
- Arms and rules exactly as in PILOT_PREREG.md / src/aida.py. Query
  universe 20, per-round budget B=5, max rounds T=3, evidence bar 3,
  review accuracy 0.60 (all fixed in G0).

## G2 — Disease bars

- D1: every baseline FNR >= 0.30 (single, react, self-consistency,
  same-context review). Pilot lowest: react 0.392.
- D2: single-pass dismissal rate on the empty-first-search attack
  subset >= 0.80 AND bootstrap CI lower bound >= 0.75. Pilot: 0.845.
- D3: same-context review net correction < 0 AND bootstrap CI upper
  bound < 0 (corrections minus breaks, per alert, all alerts).
  Pilot: net −80, CI [−0.123, −0.039] per alert.

## G3 — Load-bearing mechanism + benign bound

- M1: AIDA FNR − react FNR (react = best baseline in pilot) <= −0.20
  AND paired-bootstrap CI upper bound <= −0.10. Pilot diff: −0.392.
- M2: AIDA FNR − no-adversary FNR <= −0.15 AND CI upper <= −0.05
  (the challenge is load-bearing: without it the round-1 thesis stands).
  Pilot diff: −0.392.
- M3: AIDA FNR − no-judge-bar FNR <= −0.15 AND CI upper <= −0.05
  (the Judge bar is load-bearing: without continuation/default the
  round-1 thesis stands). Pilot diff: −0.392.
- M4 (efficiency vs the exhaustive oracle): AIDA mean searches <= 12
  AND AIDA FNR − oracle FNR <= 0.02. Pilot: 9.13 searches vs oracle 15;
  diff −0.006. The claim is adaptive, challenge-triggered continuation,
  NOT beating exhaustive search on accuracy alone — the oracle arm is
  reported, not hidden.
- B1 (benign bound): AIDA benign escalation <= 0.10 AND AIDA benign
  accuracy >= 0.90. Pilot: 0.012 / 0.988.

## Differentiation (stated before head-to-head, carried into PAPER.md)

- vs #56 tool-trace-audit: HOW review is organized, not trace truth.
- vs #77 detector-truth-gap: investigation organization, not detector
  disagreement.
- vs #85 harness-vcr: review protocol, not model-vs-harness attribution.
- vs #111 blindfold: adjudication structure, not certifier randomness.

## Scope limits (stated before head-to-head)

- Scripted analog only. The paper's LLM/SIEM figures (F1 0.958,
  FNR 40.4% -> 3.1%, 1,247 real alerts, escalation 18.4%) are CONTEXT
  ONLY and are never claimed as reproduced.
- Synthetic planted records only; the empty-search trap is a designed
  arm (first query non-discoverable), not an accident of the data.
- No false-positive mechanism exists by construction (benign alerts
  contain no incriminating item), so baseline precision is 1.0 by
  construction; the comparison is on recall/FNR, and the benign bound
  is AIDA's own escalation rate.
- The ledger is append-only and the challenge is evidence-only: the
  Strategist's private reasoning is never passed to the Adversary or
  the Judge (enforced by function signatures, tested). If that
  separation had collapsed, the build would have been killed at pilot.
- Claim scope: the investigation structure converts a limited
  per-round budget into near-exhaustive coverage at a bounded benign
  cost in this analog — not a claim about any real SOC deployment.
