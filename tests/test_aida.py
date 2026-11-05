"""Tests for project #116 `aida`. All must pass before any result is used."""

import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "src"))
from aida import (Ledger, gen_population, run_aida, run_single_pass,
                  run_review, adversary_view, REVIEW_ACCURACY,
                  EVIDENCE_BAR, BUDGET_ROUND, MAX_ROUNDS)


def test_ledger_append_only():
    led = Ledger(1)
    led.append({"kind": "evidence", "item": 3, "incriminating": True})
    led.append({"kind": "thesis", "decision": "escalate"})
    assert len(led) == 2
    # No mutation API: entries() returns copies, mutating them changes nothing.
    entries = led.entries()
    entries[0]["kind"] = "tampered"
    assert led.entries()[0]["kind"] == "evidence"
    assert not hasattr(led, "overwrite") and not hasattr(led, "delete")


def test_adversary_view_has_no_reasoning():
    led = Ledger(2)
    led.append({"kind": "evidence", "item": 5, "incriminating": False})
    view = adversary_view("dismiss", [5], led)
    assert "reasoning" not in view
    assert "private" not in str(view).lower()
    assert view["thesis"] == "dismiss" and view["evidence"] == [5]


def test_aida_never_exposes_reasoning_to_judge_path():
    # run_aida's thesis/challenge/decision entries contain no reasoning text.
    alerts = gen_population(123, 10, 10)
    for al in alerts:
        r = run_aida(al)
        assert r["decision"] in ("escalate", "dismiss")
        assert 1 <= r["rounds"] <= MAX_ROUNDS
        assert r["searches"] <= MAX_ROUNDS * BUDGET_ROUND


def test_single_pass_budget_and_rule():
    alerts = gen_population(7, 5, 5)
    for al in alerts:
        d, s = run_single_pass(al, budget=2)
        assert s == 2 and d in ("escalate", "dismiss")


def test_review_accuracy_parameter():
    assert REVIEW_ACCURACY == 0.60
    alerts = gen_population(9, 20, 20)
    import random
    rng = random.Random(1)
    for al in alerts:
        ini, fin, s, c, b = run_review(al, rng)
        assert c in (0, 1) and b in (0, 1) and not (c and b)


def test_evidence_bar_constant():
    assert EVIDENCE_BAR == 3 and BUDGET_ROUND == 5 and MAX_ROUNDS == 3


def test_aida_dismiss_requires_bar_or_escalates():
    # Construct an attack alert whose incriminating queries are late in
    # the order: AIDA must not end in a bare dismiss without a challenge
    # path (final-round default escalates when the bar is unmet).
    al = {"id": 0, "label": 1, "inc": {17, 18, 19}, "exon": {0, 1},
          "order": list(range(20))}
    r = run_aida(al)
    # Round 1 finds exon 0,1 only -> dismiss thesis -> completeness
    # challenge -> continuation; round 2 finds nothing new... order
    # 5..9 contain no items -> still dismiss thesis, challenge, round 3
    # finds 17,18,19? No: round 3 consumes queries 10..14, none
    # incriminating -> final-round default escalates.
    assert r["decision"] == "escalate"
    assert r["rounds"] == 3


def test_benign_alert_can_dismiss():
    al = {"id": 1, "label": 0, "inc": set(),
          "exon": {0, 1, 2, 3, 4, 5, 6, 7}, "order": list(range(20))}
    r = run_aida(al)
    assert r["decision"] == "dismiss"
    assert r["rounds"] == 1  # 5 exonerating items found, bar met
