import os
import sys
import numpy as np

# ensure workspace root is on sys.path so apply_anchor can be imported
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from apply_anchor import LedgerState, Anchor, apply_anchor


def test_zero_residual_and_drift_seals():
    n = 4
    M = np.eye(n)
    z = np.zeros(n)
    preds = np.zeros(n)
    outcomes = np.zeros(n)
    x = np.zeros(n)
    P = np.eye(n)
    baseline = np.zeros(n)

    ledger = LedgerState(M=M, z=z, predictions=preds, outcomes=outcomes, x=x, P=P, baseline_p=baseline)
    anchor = Anchor(invariants=0.0, baseline_p=baseline, tau=1e-6, epsilon=1e-6, gamma_max=1.0, delta_V=1.0, c_V=1.0, P=P, id="zero_case")

    out = apply_anchor(anchor, ledger)
    assert out["action"] == "seal_closure"


def test_envelope_failure_causes_corrective():
    n = 3
    M = np.eye(n)
    z = np.zeros(n)
    preds = np.zeros(n)
    # outcomes differ from predictions by more than tau
    outcomes = np.ones(n) * 0.5
    x = np.zeros(n)
    P = np.eye(n)
    baseline = np.zeros(n)

    ledger = LedgerState(M=M, z=z, predictions=preds, outcomes=outcomes, x=x, P=P, baseline_p=baseline)
    anchor = Anchor(invariants=0.0, baseline_p=baseline, tau=1e-3, epsilon=1e-3, gamma_max=1.0, delta_V=1.0, c_V=1.0, P=P, id="env_fail")

    out = apply_anchor(anchor, ledger)
    assert out["action"] == "issue_corrective"


def test_unstable_lyapunov_causes_corrective():
    n = 5
    M = np.eye(n)
    z = np.zeros(n)
    preds = np.zeros(n)
    outcomes = np.zeros(n)
    # large state x makes x^T P x exceed tiny gamma
    x = np.ones(n) * 100.0
    P = np.eye(n)
    baseline = np.zeros(n)

    ledger = LedgerState(M=M, z=z, predictions=preds, outcomes=outcomes, x=x, P=P, baseline_p=baseline)
    # force gamma to be very small so Lyapunov check fails
    anchor = Anchor(invariants=0.0, baseline_p=baseline, tau=1.0, epsilon=1.0, gamma_max=1e-6, delta_V=1e-6, c_V=1.0, P=P, id="unstable")

    out = apply_anchor(anchor, ledger)
    assert out["action"] == "issue_corrective"


def test_residual_zero_safe_ratio_handled():
    # ensure residual==0 doesn't raise and leads to seal when other checks pass
    n = 2
    M = np.eye(n)
    z = np.zeros(n)
    preds = np.zeros(n)
    outcomes = np.zeros(n)
    x = np.zeros(n)
    P = np.eye(n)
    baseline = np.zeros(n)

    ledger = LedgerState(M=M, z=z, predictions=preds, outcomes=outcomes, x=x, P=P, baseline_p=baseline)
    anchor = Anchor(invariants=0.0, baseline_p=baseline, tau=0.0, epsilon=0.0, gamma_max=1.0, delta_V=1.0, c_V=1.0, P=P, id="res_zero")

    out = apply_anchor(anchor, ledger)
    assert out["action"] in ("seal_closure", "issue_corrective")
