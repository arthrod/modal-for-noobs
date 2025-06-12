"""\
tests/test_complete_dashboard.py

Testing Library Note:
- Framework: pytest
- Fixtures & Mocking: pytest fixtures & monkeypatch for stubbing external dependencies.

Purpose:
This suite verifies the `complete_dashboard` function in the `dashboard.complete` module,
covering normal operation, boundary conditions, and error handling.
"""

import pytest
from dashboard.complete import complete_dashboard  # Adjust import path as needed

@pytest.fixture
def sample_data():
    """Provides a baseline input dictionary for dashboard completion."""
    return {
        "metrics": [1, 2, 3],
        "threshold": 5,
    }

def test_complete_dashboard_happy_path(sample_data):
    """Happy path: returns status 'ok', correct total, and threshold_exceeded False."""
    result = complete_dashboard(sample_data)
    assert isinstance(result, dict)
    assert result["status"] == "ok"
    assert result["total"] == sum(sample_data["metrics"])
    assert result["threshold_exceeded"] is False

def test_complete_dashboard_threshold_exceeded(sample_data):
    """When total exceeds threshold, threshold_exceeded should be True."""
    data = sample_data.copy()
    data["metrics"] = [10, 20]
    data["threshold"] = 5
    result = complete_dashboard(data)
    assert result["threshold_exceeded"] is True

@pytest.mark.parametrize(
    "metrics,threshold,expected_total,expected_flag",
    [
        ([], 0, 0, False),
        ([0, 0, 0], 1, 0, False),
        ([5], 5, 5, True),
    ],
)
def test_complete_dashboard_edge_cases(metrics, threshold, expected_total, expected_flag):
    """Parametrized edge cases for various metric lists and thresholds."""
    data = {"metrics": metrics, "threshold": threshold}
    result = complete_dashboard(data)
    assert result["total"] == expected_total
    assert result["threshold_exceeded"] is expected_flag

def test_complete_dashboard_invalid_input_none():
    """Passing None should raise a TypeError."""
    with pytest.raises(TypeError):
        complete_dashboard(None)

def test_complete_dashboard_missing_keys():
    """Omitting required keys should raise KeyError."""
    with pytest.raises(KeyError):
        complete_dashboard({"metrics": [1, 2]})

def test_complete_dashboard_external_failure(monkeypatch, sample_data):
    """Simulate external dependency failure via monkeypatch."""
    def fake_external_call(data):
        raise RuntimeError("External API error")
    monkeypatch.setattr("dashboard.complete._external_call", fake_external_call)
    with pytest.raises(RuntimeError):
        complete_dashboard(sample_data)