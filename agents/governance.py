"""Simulation-only governance: no external changes, credentials or commands."""
from datetime import datetime, timezone
from uuid import uuid4

ALLOWED_ACTIONS = ('observe', 'request_rollback_review', 'request_capacity_review')

def create_change_request(investigation):
    if not investigation.get('incident'):
        return {'status':'NO_CHANGE', 'reason':'No sustained incident; monitor only.', 'action':'observe', 'risk':'low', 'ticket':None}
    scenario = investigation['scenario']
    action = 'request_rollback_review' if scenario == 'Payment API latency' else 'request_capacity_review'
    return {'status':'PENDING_APPROVAL','reason':'Synthetic production-impacting change requires human approval.',
            'action':action,'risk':'high','ticket':'DEMO-CHG-'+uuid4().hex[:8].upper(),
            'created_at':datetime.now(timezone.utc).isoformat(), 'source':'Simulated ServiceNow change request'}

def policy_check(change, approved=False):
    if change['action'] not in ALLOWED_ACTIONS:
        return {'decision':'DENY','reason':'Action not allowlisted'}
    if change['status']=='NO_CHANGE':
        return {'decision':'HOLD','reason':'No remediation needed'}
    if not approved:
        return {'decision':'REQUIRE_APPROVAL','reason':'High-risk changes require explicit human approval'}
    return {'decision':'APPROVED_FOR_SIMULATION','reason':'Human approved a demo-only simulation; no production execution'}

def simulate_remediation(change, policy):
    if policy['decision']!='APPROVED_FOR_SIMULATION':
        return {'executed':False,'status':'BLOCKED','steps':[]}
    return {'executed':False,'status':'SIMULATED_ONLY',
            'steps':['Generate hypothetical Ansible/OpenShift change plan',
                     'Validate hypothetical GitOps review and rollback plan',
                     'Simulate post-change SLO verification'],
            'verification':'Not measured: no real telemetry or production change',
            'rollback':'Hypothetical rollback plan required before any real deployment'}
