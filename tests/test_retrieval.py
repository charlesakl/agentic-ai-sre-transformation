from unittest.mock import patch
from agents.knowledge import load_documents
from agents.graph import investigate

def test_docs():
    assert len(load_documents()) == 8

def test_offline_retrieval_stage():
    r=investigate("Payment API latency")
    assert any(e["agent"]=="Knowledge Agent" for e in r["trace"])
    assert r["retrieval_mode"]=="Skipped (offline demo)"

def test_live_retrieval_passes_documents():
    docs=[{"doc_id":"RUN-101","source":"RUN-101.md","content":"synthetic","distance":0.1}]
    ai={"summary":"a","likely_cause":"b","confidence":"medium","supporting_evidence":[],
        "alternative_causes":[],"missing_evidence":[],"recommended_checks":[],
        "proposed_action":"review","knowledge_citations":["RUN-101"]}
    with patch("agents.graph.retrieve_knowledge",return_value=docs), patch("agents.graph.reason_about_incident",return_value=ai) as model:
        r=investigate("Payment API latency",use_ai=True)
    assert model.call_args.kwargs["retrieved_knowledge"]==docs
    assert r["retrieved_knowledge"]==docs
