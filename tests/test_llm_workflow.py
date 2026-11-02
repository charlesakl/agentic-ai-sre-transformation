from unittest.mock import patch
from agents.graph import investigate

def test_ai_investigation_uses_mocked_reasoning():
    mock = {"summary":"Latency degraded after deployment", "likely_cause":"Possible connection saturation",
            "confidence":"medium", "supporting_evidence":["Connection utilization 96%"],
            "alternative_causes":["Database slowness"], "missing_evidence":["DB wait times"],
            "recommended_checks":["Inspect connection metrics"], "proposed_action":"Request human review"}
    with patch("agents.graph.retrieve_knowledge",return_value=[]), patch("agents.graph.reason_about_incident", return_value=mock) as fn:
        result=investigate("Payment API latency",use_ai=True)
    assert fn.called
    assert result["analysis_mode"]=="Live OpenAI LLM"
    assert result["hypothesis"]==mock["likely_cause"]
    assert "APPROVAL" in result["decision"]

def test_ai_failure_is_not_misrepresented():
    with patch("agents.graph.retrieve_knowledge",return_value=[]), patch("agents.graph.reason_about_incident",side_effect=RuntimeError("simulated unavailable")):
        result=investigate("Payment API latency",use_ai=True)
    assert result["analysis_mode"]=="Fallback fixture (AI failed)"
    assert "simulated unavailable" in result["ai_error"]

def test_false_positive_never_auto_remediates():
    result=investigate("False-positive alert")
    assert result["decision"].startswith("HOLD")
