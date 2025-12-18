import os
import sys
import numpy as np

# ensure workspace root is on sys.path so apply_anchor can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import apply_anchor
from apply_anchor import (
    LedgerState,
    Anchor,
    apply_anchor as apply_anchor_fn,
    compute_invariants,
    _safe_ratio,
    norm,
)


def test_compute_invariants_non_identity():
    M = np.array([[2.0, 0.0], [0.0, 3.0]])
    z = np.array([1.0, 2.0])
    expected = np.linalg.norm(M @ z)
    assert compute_invariants(M, z) == expected


def test_safe_ratio_division_by_zero_returns_inf():
    assert _safe_ratio(1.0, 0.0) == float("inf")
    assert _safe_ratio(0.0, 0.0) == float("inf")


def test_norm_matches_numpy():
    v = np.array([3.0, 4.0])
    assert norm(v) == 5.0


def make_basic_ledger(n=3):
    M = np.eye(n)
    z = np.zeros(n)
    preds = np.zeros(n)
    outcomes = np.zeros(n)
    x = np.zeros(n)
    P = np.eye(n)
    baseline = np.zeros(n)
    return LedgerState(M=M, z=z, predictions=preds, outcomes=outcomes, x=x, P=P, baseline_p=baseline)


def test_grad_QI_high_norm_makes_gamma_small_and_triggers_corrective(monkeypatch):
    ledger = make_basic_ledger(4)
    # ensure state x is large so x^T P x exceeds the tiny gamma
    ledger.x = np.ones(4) * 100.0

    # monkeypatch grad_QI to return a large-norm vector
    monkeypatch.setattr(apply_anchor, "grad_QI", lambda ls: np.ones(4) * 1e6)

    # choose anchor such that delta_V/(c_V*(1+norm)) becomes tiny
    anchor = Anchor(invariants=0.0, baseline_p=np.zeros(4), tau=1.0, epsilon=1.0, gamma_max=1.0, delta_V=1.0, c_V=1.0, P=np.eye(4), id="g_small")

    out = apply_anchor_fn(anchor, ledger)
    assert out["action"] == "issue_corrective"


def test_lyapunov_equality_boundary_seals(monkeypatch):
    # Force grad_QI to zero so gamma = min(gamma_max, delta_V/(c_V*(1+0)))
    ledger = make_basic_ledger(3)
    monkeypatch.setattr(apply_anchor, "grad_QI", lambda ls: np.zeros(3))

    # pick x such that x^T P x == gamma
    x = np.array([1.0, 2.0, 0.0])
    P = np.eye(3)
    val = float(x.T @ P @ x)

    # set delta_V/(c_V*(1+0)) == val and gamma_max large so gamma == val
    delta_V = val
    anchor = Anchor(invariants=0.0, baseline_p=np.zeros(3), tau=1.0, epsilon=1.0, gamma_max=10.0, delta_V=delta_V, c_V=1.0, P=P, id="lyap_eq")

    ledger.x = x
    ledger.P = P

    out = apply_anchor_fn(anchor, ledger)
    assert out["action"] == "seal_closure"


def test_project_identity_and_custom_project(monkeypatch):
    ledger = make_basic_ledger(3)

    # default project is identity, so envelope_ok True
    anchor = Anchor(invariants=0.0, baseline_p=np.zeros(3), tau=0.1, epsilon=1.0, gamma_max=1.0, delta_V=1.0, c_V=1.0, P=np.eye(3), id="proj_ok")
    out = apply_anchor_fn(anchor, ledger)
    # depending on other checks, ensure function returns a dict with action
    assert isinstance(out, dict) and "action" in out

    # now monkeypatch project to shift predictions far away causing envelope failure
    monkeypatch.setattr(apply_anchor, "project", lambda p: p + 100.0)
    out2 = apply_anchor_fn(anchor, ledger)
    assert out2["action"] == "issue_corrective"


def test_seal_and_issue_return_types_and_keys():
    ledger = make_basic_ledger(2)
    anchor_seal = Anchor(invariants=0.0, baseline_p=np.zeros(2), tau=1.0, epsilon=1.0, gamma_max=1.0, delta_V=10.0, c_V=1.0, P=np.eye(2), id="s1")
    res = apply_anchor_fn(anchor_seal, ledger)
    assert isinstance(res, dict)
    assert "action" in res and "anchor_id" in res

    anchor_corr = Anchor(invariants=0.0, baseline_p=np.zeros(2), tau=1e-6, epsilon=1e-6, gamma_max=1.0, delta_V=1.0, c_V=1.0, P=np.eye(2), id="c1")
    res2 = apply_anchor_fn(anchor_corr, ledger)
    assert isinstance(res2, dict)
    assert res2.get("action") in ("issue_corrective", "seal_closure")
