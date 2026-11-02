from data.scenarios import SCENARIOS, telemetry, detect_incident
from maturity import DIMENSIONS, assess

def test_scenarios_have_consistent_telemetry():
    for name in SCENARIOS:
        assert len(telemetry(name)) == 12

def test_false_positive_does_not_trigger():
    assert detect_incident("False-positive alert") is False

def test_payment_incident_triggers():
    assert detect_incident("Payment API latency") is True

def test_maturity_scoring():
    result = assess({k: 3 for k in DIMENSIONS})
    assert result["average"] == 3
    assert result["percent"] == 60
