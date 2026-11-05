# PILOT PREREG — Project #116 `aida` (arXiv 2610.10608)

Written BEFORE any pilot number was observed. The pilot gate must pass ALL
of P1–P4 for the build to proceed to a locked PREREG. If any fails, KILL.

## Pilot protocol (seed 116001, n=1000 alerts, 500 attack / 500 benign)

- Query universe: 20 query ids. Each alert draws a seeded query permutation;
  every arm reads prefixes/chunks of the SAME permutation (common random
  numbers, paired comparison). Attack alerts: 3 discoverable incriminating
  queries + 2 discoverable exonerating queries. Benign alerts: 8 discoverable
  exonerating queries, 0 incriminating. No false-positive mechanism exists
  by construction (benign alerts contain no incriminating item), so baseline
  precision is 1.0 by construction; the comparison is on recall/FNR, and the
  benign bound is measured on AIDA's own escalation rate. This is a stated
  scope limit, not a hidden assumption.
- Arms: single-pass (budget 2), react (budget 5), self-consistency (3 x
  budget 2, majority), same-context review (single-pass decision replaced
  by a fresh judgment correct with p=0.60, fixed in G0), AIDA-full (rounds
  T=3, budget B=5/round, append-only ledger, thesis -> evidence-only
  challenge -> Judge with asymmetric dismissal bar), no-adversary (round-1
  thesis stands), no-judge-bar (challenge recorded but Judge upholds the
  thesis immediately), oracle (budget 15, escalate iff incriminating found).
- AIDA protocol (exact): Strategist searches up to B new queries per round
  and appends every found item to the append-only ledger. Thesis: escalate
  iff an incriminating item is in the ledger, else dismiss. The Adversary
  receives ONLY (thesis decision, cited item ids, ledger evidence entries)
  — never the Strategist's private reasoning (enforced by the function
  signatures and tested). It challenges a dismiss-thesis iff it is a
  contradiction (incriminating item in ledger) or a completeness challenge
  (total evidence items found < 3). The Judge: contradiction -> escalate;
  completeness challenge -> continuation (new round, budget reset, ledger
  persists) unless it is the final round, where the conservative default is
  escalate because the dismissal bar is unmet; no challenge -> thesis
  stands. Escalate-theses are never challenged (dismissal is the terminal,
  dangerous action — the asymmetric bar, per the paper).
- Empty-search trap arm (designed, not accidental): the subset of ATTACK
  alerts whose FIRST query in the permutation is non-discoverable (returns
  no record). Measured: single-pass dismissal rate on that subset.

## Pilot gate thresholds (all must pass)

- P1: react (best-baseline candidate) FNR >= 0.25.
- P2: single-pass dismissal rate on the empty-first-search attack subset
  >= 0.75.
- P3: same-context review net correction (corrections minus breaks, per
  alert, all alerts) < 0.
- P4: AIDA-full FNR <= 0.05.

## Differentiation (stated before any pilot number)

- vs #56 tool-trace-audit: the object here is HOW review is organized
  (thesis + separate-context challenge + adjudication), not trace truth.
- vs #77 detector-truth-gap: investigation organization, not detector
  disagreement.
- vs #85 harness-vcr: review protocol, not model-vs-harness attribution.
- vs #111 blindfold: adjudication structure, not certifier randomness.
- The paper's LLM/SIEM figures (F1 0.958, FNR 40.4% -> 3.1%, 1,247 real
  alerts) are CONTEXT ONLY and are never claimed as reproduced.
- The Judge must never see the Strategist's private reasoning: if the
  Judge arm collapses into same-context review, the pilot KILLs.
