from agents.governance import create_change_request, policy_check, simulate_remediation

def test_incident_requires_approval():
    c = create_change_request({'incident':True,'scenario':'Payment API latency'})
    assert policy_check(c)['decision']=='REQUIRE_APPROVAL'
    assert simulate_remediation(c, policy_check(c))['status']=='BLOCKED'
    assert simulate_remediation(c, policy_check(c,approved=True))['status']=='SIMULATED_ONLY'
    assert simulate_remediation(c, policy_check(c,approved=True))['executed'] is False

def test_false_positive_held():
    c=create_change_request({'incident':False,'scenario':'False-positive alert'})
    assert policy_check(c, approved=True)['decision']=='HOLD'
