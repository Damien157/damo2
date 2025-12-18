import os
import sys
import numpy as np

# ensure workspace root is on sys.path so apply_anchor can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apply_anchor import LedgerState, Anchor, apply_anchor


def test_seal_closure_path():
    n = 3
    M = np.eye(n)
    z = np.zeros(n)
    preds = np.zeros(n)
    outcomes = np.zeros(n)
    x = np.zeros(n)
    P = np.eye(n)
    baseline = np.zeros(n)

    ledger = LedgerState(M=M, z=z, predictions=preds, outcomes=outcomes, x=x, P=P, baseline_p=baseline)
    anchor = Anchor(invariants=0.0, baseline_p=baseline, tau=1e-3, epsilon=1e-3, gamma_max=1.0, delta_V=1.0, c_V=1.0, P=P, id="a_seal")

    out = apply_anchor(anchor, ledger)
    assert out["action"] == "seal_closure"
    assert out["anchor_id"] == "a_seal"


def test_issue_corrective_path():
    n = 3
    M = np.eye(n)
    z = np.ones(n)
    preds = np.ones(n) * 10.0
    outcomes = np.zeros(n)
    x = np.zeros(n)
    P = np.eye(n)
    baseline = np.zeros(n)

    ledger = LedgerState(M=M, z=z, predictions=preds, outcomes=outcomes, x=x, P=P, baseline_p=baseline)
    # small tau so residual >> tau leads to S < 1
    anchor = Anchor(invariants=0.0, baseline_p=baseline, tau=0.1, epsilon=1e-6, gamma_max=1.0, delta_V=1.0, c_V=1.0, P=P, id="a_corr")

    out = apply_anchor(anchor, ledger)
    assert out["action"] == "issue_corrective"
    assert out["anchor_id"] == "a_corr"
    assert "diagnostics" in out
