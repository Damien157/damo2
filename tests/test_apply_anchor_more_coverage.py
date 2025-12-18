import os
import sys
import numpy as np
import importlib

# ensure workspace root is on sys.path so apply_anchor can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import apply_anchor
from apply_anchor import LedgerState, Anchor, apply_anchor as apply_anchor_fn


def test_gamma_uses_gamma_max_and_seals():
    n = 3
    M = np.eye(n)
    z = np.zeros(n)
    preds = np.zeros(n)
    outcomes = np.zeros(n)
    x = np.zeros(n)
    P = np.eye(n)
    baseline = np.zeros(n)

    # second term would be delta_V/(c_V*(1+||grad||)) = 10, but gamma_max = 1 forces gamma=1
    ledger = LedgerState(M=M, z=z, predictions=preds, outcomes=outcomes, x=x, P=P, baseline_p=baseline)
    anchor = Anchor(invariants=0.0, baseline_p=baseline, tau=1.0, epsilon=1.0, gamma_max=1.0, delta_V=10.0, c_V=1.0, P=P, id="gmax")

    out = apply_anchor_fn(anchor, ledger)
    assert out["action"] == "seal_closure"


def test_S_exactly_one_boundary_seals():
    n = 4
    M = np.eye(n)
    # set z so invariants == 2.0
    z = np.array([2.0, 0.0, 0.0, 0.0])
    preds = np.array([1.0, 0.0, 0.0, 0.0])
    outcomes = preds.copy()
    x = np.zeros(n)
    P = np.eye(n)
    baseline = np.zeros(n)

    epsilon = 0.25
    # make anchor.invariants such that drift == epsilon
    invariants_val = np.linalg.norm(M @ z)
    anchor_invariants = invariants_val - epsilon

    ledger = LedgerState(M=M, z=z, predictions=preds, outcomes=outcomes, x=x, P=P, baseline_p=baseline)
    anchor = Anchor(invariants=anchor_invariants, baseline_p=baseline, tau=1.0, epsilon=epsilon, gamma_max=1.0, delta_V=1.0, c_V=1.0, P=P, id="S_eq_1")

    out = apply_anchor_fn(anchor, ledger)
    assert out["action"] == "seal_closure"


def test_safe_ratio_infinite_and_seal_when_other_checks_pass():
    n = 2
    M = np.eye(n)
    z = np.zeros(n)
    preds = np.zeros(n)
    outcomes = np.zeros(n)
    x = np.zeros(n)
    P = np.eye(n)
    baseline = np.zeros(n)

    # residual will be zero (preds == baseline), resulting in inf for tau/residual
    # ensure epsilon/drift >= 1 by making drift small
    ledger = LedgerState(M=M, z=z, predictions=preds, outcomes=outcomes, x=x, P=P, baseline_p=baseline)
    anchor = Anchor(invariants=0.0, baseline_p=baseline, tau=1.0, epsilon=1.0, gamma_max=1.0, delta_V=1.0, c_V=1.0, P=P, id="safe_inf")

    out = apply_anchor_fn(anchor, ledger)
    assert out["action"] == "seal_closure"


def test_project_monkeypatched_causes_envelope_failure(monkeypatch):
    # monkeypatch apply_anchor.project to simulate a projector that shifts predictions
    def bad_project(preds):
        return preds + 10.0

    monkeypatch.setattr(apply_anchor, "project", bad_project)

    n = 3
    M = np.eye(n)
    z = np.zeros(n)
    preds = np.zeros(n)
    # outcomes equal preds so normally envelope_ok true, but bad_project will break it
    outcomes = preds.copy()
    x = np.zeros(n)
    P = np.eye(n)
    baseline = np.zeros(n)

    ledger = LedgerState(M=M, z=z, predictions=preds, outcomes=outcomes, x=x, P=P, baseline_p=baseline)
    anchor = Anchor(invariants=0.0, baseline_p=baseline, tau=0.5, epsilon=1.0, gamma_max=1.0, delta_V=1.0, c_V=1.0, P=P, id="proj_bad")

    out = apply_anchor_fn(anchor, ledger)
    assert out["action"] == "issue_corrective"


def test_diagnostics_content_keys():
    n = 3
    M = np.eye(n)
    z = np.ones(n)
    preds = np.ones(n) * 5.0
    outcomes = np.zeros(n)
    x = np.zeros(n)
    P = np.eye(n)
    baseline = np.zeros(n)

    ledger = LedgerState(M=M, z=z, predictions=preds, outcomes=outcomes, x=x, P=P, baseline_p=baseline)
    anchor = Anchor(invariants=0.0, baseline_p=baseline, tau=0.1, epsilon=0.1, gamma_max=1.0, delta_V=1.0, c_V=1.0, P=P, id="diag")

    out = apply_anchor_fn(anchor, ledger)
    if out["action"] == "issue_corrective":
        diag = out.get("diagnostics", {})
        assert "drift" in diag and "residual" in diag and "stable" in diag
        assert isinstance(diag["drift"], float)
        assert isinstance(diag["residual"], float)
        assert isinstance(diag["stable"], bool)
