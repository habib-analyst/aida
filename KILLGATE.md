# KILLGATE — Project #116 `aida` — PASS (all gates)

Source: arXiv 2610.10608, "From Investigation Failures to Reliable SOC
Agents: Understanding and Improving LLM-Based Alert Triage"
(Tsegai, Kantchelian, Yao, Gao). Scripted analog; $0, CPU only, no LLM
calls, no SIEM, no real telemetry.

## G0 — Harness: PASS

Runnable harness in src/aida.py: scripted triage agents over synthetic
alerts with planted evidence records (20-query universe, one seeded
permutation per alert shared by all arms); arms single-pass (budget 2),
ReAct-style (budget 5), self-consistency (3 x budget 2, majority),
same-context review (decision replaced by a 0.60-accurate fresh
judgment), AIDA-full (T=3 rounds, B=5/round, append-only Investigation
Ledger, thesis -> evidence-only challenge -> Judge with asymmetric
dismissal bar), no-adversary and no-judge-bar ablations, and an
exhaustive-search oracle (budget 15).

## G1 — Author-code recheck (fresh, by this builder, 2026-10-30 ~10:19 UTC): PASS

- Abstract page (arxiv.org/abs/2610.10608, fetched fresh): title,
  authors (Saimon Amanuel Tsegai, Alex Kantchelian, Danfeng (Daphne)
  Yao, Peng Gao), 7 Oct 2026 submission all match; NO author code
  link — only arXiv's own third-party toggles — and no release
  statement in the abstract.
- Full-text HTML (arxiv.org/html/2610.10608v1, 1350 lines, fetched
  fresh): browser.find validated on this page ("ledger" returns 28
  matches). "github" matches ONLY third-party references (SigmaHQ
  sigma rules, ait-aecid alert-data-set). "zenodo" match ONLY a
  third-party dataset DOI (10.5281/zenodo.5789064, cited in §III).
  ZERO matches: 4open, replication, supplement, anonymous,
  "code is available", "data is available", "available at",
  "we release".
- Conclusion: no author repo, no retrievable author package, no release
  sentence with a public location. G1 PASSES under both the narrow
  reading and the #100 lesson. No package was downloaded or inspected
  (none exists to inspect). If a located author package later appears,
  re-examine under the #100 precedent.

## Pilot gate: PASS

PILOT_PREREG.md written before any pilot number. Seed 116001, n=1000:
P1 react FNR 0.392 (>= 0.25); P2 empty-first-search trap single-pass
dismissal 0.845 (n=373, >= 0.75); P3 same-context review net correction
−80 (CI [−0.123, −0.039] per alert, < 0); P4 AIDA FNR 0.000 (<= 0.05).
Pilot v1 used 8 benign exonerating queries; before PREREG lock this
was reduced to 6 because 15 draws from 20 with 8 successes always
yield >= 3 successes, which made the benign bound vacuous (see
PREREG.md). Pilot v2 (results/pilot.json) re-verified all four gates
with the non-vacuous bound (AIDA benign escalation 0.012). Attack-side
numbers are identical between v1 and v2, as expected (attack
generation untouched). Pilot v1 preserved as results/pilot_v1_exon8.json.

## PREREG: locked before head-to-head, zero amendments

Mtime order: PILOT_PREREG 10:22 < pilot 10:24 < PREREG 10:24:22 <
headline 10:25 UTC. Decision rule "ANY locked bar fails → KILL".
No amendments after locking.

## G2 — Disease: PASS (all 3 bars, fresh seed 116002, n=4000)

- D1: every baseline FNR >= 0.30 — single 0.727, react 0.422,
  self-consistency 0.797, same-context review 0.397. PASS
- D2: empty-first-search trap (n=1533): single-pass dismissal 0.838,
  CI [0.819, 0.856] (bars >= 0.80 / lo >= 0.75). AIDA dismissal on the
  same subset: 0.000. PASS
- D3: same-context review net correction −162 (869 corrected vs 1031
  broken), per-alert CI [−0.064, −0.019] (bar: net < 0, CI upper < 0).
  PASS

## G3 — Mechanism + benign bound: PASS (all 5 bars)

- M1: AIDA − react FNR diff −0.422, CI [−0.445, −0.401]
  (bars <= −0.20 / hi <= −0.10). PASS
- M2: AIDA − no-adversary diff −0.422, CI [−0.445, −0.401]
  (bars <= −0.15 / hi <= −0.05). Without the challenge the round-1
  thesis stands (FNR 0.422). PASS
- M3: AIDA − no-judge-bar diff −0.422, CI [−0.445, −0.401]
  (bars <= −0.15 / hi <= −0.05). Without continuation/default the
  round-1 thesis stands (FNR 0.422). PASS
- M4: AIDA mean searches 9.29 (bar <= 12) vs oracle 15; AIDA − oracle
  FNR diff −0.010, CI [−0.015, −0.007] (bar <= 0.02). Adaptive,
  challenge-triggered continuation, not brute force. PASS
- B1: AIDA benign escalation 0.0115 (bar <= 0.10), benign accuracy
  0.9885 (bar >= 0.90). PASS

## Headline (fresh seed 116002, n=4000, paired bootstrap 2000)

| arm | FNR | F1 | benign esc. | mean searches |
|---|---|---|---|---|
| single-pass | 0.727 | 0.429 | 0.000 | 2.0 |
| ReAct-style | 0.422 | 0.733 | 0.000 | 5.0 |
| self-consistency | 0.797 | 0.338 | 0.000 | 6.0 |
| same-context review | 0.397 | 0.599 | 0.411 | 2.0 |
| AIDA-full | 0.000 | 0.994 | 0.012 | 9.3 |
| no-adversary | 0.422 | 0.733 | 0.000 | 5.0 |
| no-judge-bar | 0.422 | 0.733 | 0.000 | 5.0 |
| oracle (15 queries) | 0.011 | 0.995 | 0.000 | 15.0 |

Honest nuance, reported not hidden: the oracle's F1 (0.995) is a hair
above AIDA's (0.994) because AIDA's final-round conservative default
escalates 23 benign alerts (1.15%) while the oracle escalates none.
AIDA wins on FNR (0.000 vs 0.011) at 9.3 vs 15 searches; it does not
beat exhaustive search on every metric, and no such claim is made.

## Determinism

SHA-256(results/headline.json) =
65d2792a1a2071f8c83ea7cbb9cbea46d17930ffc6f74942180117405e93d1dc.
Rerun on the same seed is byte-identical. Tests: 8 passed.

## Verdict: SHIP

REPO NEEDED: habib-analyst/aida (builder does not push; the GitHub App
token cannot create repos).
