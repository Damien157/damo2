import pytest


@pytest.fixture
def predictions():
    return {"btts": [0.1, 0.9, 0.5]}


@pytest.fixture
def anchor():
    baseline = sum([0.1, 0.9, 0.5]) / 3
    return {"baseline_btts": baseline, "epsilon": 1e-6}


def test_btts_invariants(predictions, anchor):
    # Norm invariant: probabilities between 0 and 1
    for p in predictions["btts"]:
        assert 0 <= p <= 1, "BTTS probability out of bounds"

    # Drift invariant: deviation from anchor baseline
    drift = abs(sum(predictions["btts"]) / len(predictions["btts"]) - anchor["baseline_btts"])
    assert drift <= anchor["epsilon"], f"BTTS drift {drift} exceeds tolerance"
