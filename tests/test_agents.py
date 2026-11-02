from agents.graph import investigate

def test_payment_workflow():
    result=investigate("Payment API latency")
    assert result["incident"] is True
    assert len(result["trace"])==5
    assert "APPROVAL" in result["decision"]
    assert len(result["evidence"])>=3

def test_false_positive_is_held():
    result=investigate("False-positive alert")
    assert result["incident"] is False
    assert "HOLD" in result["decision"]
