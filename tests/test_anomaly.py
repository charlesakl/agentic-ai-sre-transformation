from data.anomaly import synthetic_history, detect_p95

def test_p95_detector():
    history = synthetic_history('customer-profile')
    assert len(history) == 90 * 24 * 6
    assert not detect_p95(history, 0)['is_anomaly']
    assert detect_p95(history, 500)['is_anomaly']
    assert history.equals(synthetic_history('customer-profile'))
