from dataclasses import dataclass
from typing import Any, Dict

import numpy as np


@dataclass
class LedgerState:
    M: np.ndarray
    z: np.ndarray
    predictions: np.ndarray
    outcomes: np.ndarray
    x: np.ndarray
    P: np.ndarray
    baseline_p: np.ndarray


@dataclass
class Anchor:
    invariants: float
    baseline_p: np.ndarray
    tau: float
    epsilon: float
    gamma_max: float
    delta_V: float
    c_V: float
    P: np.ndarray
    id: Any


def compute_invariants(M: np.ndarray, z: np.ndarray) -> float:
    return float(np.linalg.norm(M @ z))


def norm(v: np.ndarray) -> float:
    return float(np.linalg.norm(v))


def project(predictions: np.ndarray) -> np.ndarray:
    # Identity projection placeholder — replace with application-specific projector
    return predictions


def grad_QI(ledger_state: LedgerState) -> np.ndarray:
    # Placeholder gradient approximation — replace with real gradient
    return ledger_state.x


def lyapunov_check(x: np.ndarray, P: np.ndarray, gamma: float) -> bool:
    # Check x^T P x <= gamma
    val = float(x.T @ P @ x)
    return val <= gamma


def seal_closure(ledger_state: LedgerState, anchor_id: Any) -> Dict[str, Any]:
    return {"action": "seal_closure", "anchor_id": anchor_id}


def diagnostics(drift: float, residual: float, stable: bool) -> Dict[str, Any]:
    return {"drift": drift, "residual": residual, "stable": stable}


def issue_corrective(ledger_state: LedgerState, anchor_id: Any, diag: Dict[str, Any]) -> Dict[str, Any]:
    return {"action": "issue_corrective", "anchor_id": anchor_id, "diagnostics": diag}


def _safe_ratio(a: float, b: float) -> float:
    if b == 0:
        return float("inf")
    return a / b


def apply_anchor(anchor: Anchor, ledger_state: LedgerState) -> Dict[str, Any]:
    invariants = compute_invariants(ledger_state.M, ledger_state.z)
    drift = abs(invariants - anchor.invariants)
    residual = norm(ledger_state.predictions - anchor.baseline_p)
    envelope_ok = norm(ledger_state.outcomes - project(ledger_state.predictions)) <= anchor.tau

    gamma = min(
        anchor.gamma_max,
        anchor.delta_V / (anchor.c_V * (1 + norm(grad_QI(ledger_state))))
    )
    stable = lyapunov_check(ledger_state.x, anchor.P, gamma)

    sr1 = _safe_ratio(anchor.tau, residual)
    sr2 = _safe_ratio(anchor.epsilon, drift)
    S = min(sr1, sr2)

    if stable and envelope_ok and S >= 1:
        return seal_closure(ledger_state, anchor.id)
    else:
        return issue_corrective(ledger_state, anchor.id, diagnostics(drift, residual, stable))


if __name__ == "__main__":
    # quick sanity example
    n = 4
    M = np.eye(n)
    z = np.zeros(n)
    preds = np.zeros(n)
    outcomes = np.zeros(n)
    x = np.zeros(n)
    P = np.eye(n)
    baseline = np.zeros(n)

    ledger = LedgerState(M=M, z=z, predictions=preds, outcomes=outcomes, x=x, P=P, baseline_p=baseline)
    anchor = Anchor(invariants=0.0, baseline_p=baseline, tau=1e-6, epsilon=1e-6, gamma_max=1.0, delta_V=1.0, c_V=1.0, P=P, id="a1")

    out = apply_anchor(anchor, ledger)
    print(out)
